"""R2原生捕获完整契约；仅描述真实身份和文件绑定，不授予SOURCE或G2批准。"""
import hashlib
import math
from pathlib import Path
import re
import sys

TOOL_NAMES=('collector.py','compat_pins.py','guard.py','impl_collector.py','launch_monitor.py',
            'materialize_runtime_config.py','native.py','native_capture.py','native_contract.py',
            'native_source_after.py','runtime_consumer.py','source_after_check.py','supervisor.py')
IDENTITY_KEYS=('pid','create_time','exe','cwd','cmdline','ppid')

def require(value,message):
    if not value:raise ValueError(message)

def capture_tools(work,root):
    """闭包名称固定、实际原字节绑定；不以glob扩大或缩小闭包。"""
    result=[]
    for name in sorted(TOOL_NAMES):
        path=work/name
        require(path.is_file() and not path.is_symlink() and not path.is_junction(),'工具闭包缺失或链接：'+name)
        raw=path.read_bytes()
        result.append(dict(path=path.relative_to(root).as_posix(),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
    return result

def identity_schema(row):
    require(type(row) is dict and all(key in row for key in IDENTITY_KEYS),'缺完整六字段身份')
    require(type(row['pid']) is int and row['pid']>0 and type(row['ppid']) is int and row['ppid']>=0,'身份PID类型或值错误')
    require(type(row['create_time']) in (int,float) and math.isfinite(row['create_time']) and row['create_time']>0,'身份birth类型或值错误')
    require(all(type(row[key]) is str and bool(row[key]) and str(Path(row[key]))==row[key] and Path(row[key]).is_absolute() for key in ('exe','cwd')),'身份exe/cwd不是精确绝对路径')
    require(type(row['cmdline']) is list and bool(row['cmdline']) and all(type(s) is str for s in row['cmdline']),'身份cmdline类型错误')

def collector_arguments(arguments):
    """严格完整argv白名单；无重复选项、额外参数或静默默认phase/gate。"""
    require(type(arguments) is list and bool(arguments) and all(type(s) is str for s in arguments),'命令argv类型不同')
    mode=arguments[0];require(mode in ('prepare','source','collect','seal'),'未知collector模式')
    rest=arguments[1:];require(len(rest)%2==0,'命令参数未成对')
    options={}
    for index in range(0,len(rest),2):
        key,value=rest[index:index+2]
        require(key not in options,'命令重复参数：'+key);options[key]=value
    allowed={'prepare':{'--receipt'},'source':{'--commit','--phase'},'collect':{'--commit','--gate'},'seal':{'--commit','--gate'}}[mode]
    require(set(options)<=allowed,'命令包含额外参数')
    if mode=='prepare':
        require(re.fullmatch(r'prepared_receipt(?:_r\d+)?\.json',options.get('--receipt','prepared_receipt.json')) is not None,'准备receipt标识不同')
    else:
        require(set(options)==allowed and re.fullmatch(r'[0-9a-f]{40}',options['--commit']) is not None,'命令缺commit/phase/gate或commit错误')
        if mode=='source':require(options['--phase'] in ('before','after'),'命令phase不同')
        else:require(Path(options['--gate']).is_absolute() and str(Path(options['--gate']))==options['--gate'],'命令gate不是精确绝对路径')
    return dict(mode=mode,options=options)

def validate_capture(record,command,wrapper_command,cwd,tool_bindings,prefix,logs,runtime_config,native_python):
    """缺字段、未知、预算失败与矛盾值拒绝；child非零真实失败仍可归档。"""
    require(type(record) is dict,'原生记录不是object')
    required={'command','wrapper_command','cwd','launcher_identity','direct_child_identity','native_exit_code',
              'wrapper_exit_code','capture_status','direct_child_wait_returned','unknown_samples','unknown_count',
              'budget_stop','tool_bindings_before','tool_bindings_after','stdout','stderr','closed_logs',
              'known_descendant_identity_terminal_observations','known_descendants_same_identity_absent_at_observation',
              'runtime_config','native_python'}
    require(required<=set(record),'原生记录缺身份/工具/状态metadata')
    require(record['command']==command and record['wrapper_command']==wrapper_command,'完整wrapper/child argv不同')
    require(record['cwd']==cwd,'包装实际cwd不同')
    launcher=record['launcher_identity'];child=record['direct_child_identity']
    identity_schema(launcher);identity_schema(child)
    require(launcher['cmdline']==wrapper_command and child['cmdline']==command,'身份命令与实际argv不同')
    require(launcher['exe']==sys.executable and child['exe']==sys.executable and launcher['cwd']==cwd and child['cwd']==cwd,'wrapper/child exe或cwd不同')
    require(child['ppid']==launcher['pid'] and child['create_time']>=launcher['create_time'],'child父PID/birth不同')
    require(record['tool_bindings_before']==tool_bindings and record['tool_bindings_after']==tool_bindings,'完整冻结工具集合或前后哈希不同')
    require(record['runtime_config']==runtime_config and record['native_python']==native_python,'运行配置或Vitis解释器绑定不同')
    require(type(record['unknown_count']) is int and record['unknown_count']==0 and record['unknown_samples']==[],'原生身份存在UNKNOWN，禁止用child0放行')
    require(record['budget_stop'] is None,'原生包装预算停止，禁止用child0放行')
    require(record['direct_child_wait_returned'] is True and type(record['native_exit_code']) is int,'原生直接wait未闭合')
    require(type(record['wrapper_exit_code']) is int and record['wrapper_exit_code']==record['native_exit_code'],'wrapper/child状态矛盾')
    require(record['capture_status']==('CLOSED_NATIVE_SUCCESS' if record['native_exit_code']==0 else 'CLOSED_NATIVE_CHILD_FAILURE'),'原生状态与退出码不同')
    require(record['closed_logs']==logs and record['stdout']==logs[0] and record['stderr']==logs[1],'日志路径/字节/字段不同')
    terminal=record['known_descendant_identity_terminal_observations']
    require(type(terminal) is list and bool(terminal),'缺已知身份终态')
    require(record['known_descendants_same_identity_absent_at_observation'] is True,'已知后代仍活或未知')
    found=False
    for row in terminal:
        identity_schema(row)
        require(row.get('same_identity_exists') is False and row.get('observed_status') in ('NO_SUCH_PROCESS','PID_REUSED'),'已知身份终态未知或仍活')
        if row['observed_status']=='PID_REUSED':require(row.get('new_object_untouched') is True,'复用对象未明确保留')
        if all(row[k]==child[k] for k in IDENTITY_KEYS):found=True
    require(found,'直接子终态未绑定六字段')
    require(record.get('prefix')==prefix,'原生prefix不同')
