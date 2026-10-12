"""独立SOURCE内容及证据封装；保留原采集阻断，绝不调用原seal或批准预算。"""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import stat
import subprocess
import sys

HERE=Path(__file__).parent;ROOT=HERE.parents[3]
WORK=ROOT/'tmp/2B/S2B-T17/s15_launch_prepare_20261012_r02'
ROOTRUN=ROOT/'tmp/2B/S2B-T17/s15_physical_launch_root_20261012_r01'
SOURCE='926c2fd382069e68e6c5ec533b7d3b6a87fbb363'
CONFIG=WORK/'runtime_pins_synth_r1.json'
CONFIG_SHA='1b1468b5df0687fa1a7687956c41d2547980ebf51785a6fb51ecf7dfaaa03885'
ADMISSION_SHA='41b16f8398c6698e6ade3a7acf11a6af45aaa83ed884f5adadf7f3ca12f64ee9'
TOOLS_REVIEW_SHA='76bec7816b01582e5484f18d2d9c7c19881ce9b915532cbd11237b0ac2d45214'
NAMES=('collector.py','compat_pins.py','guard.py','impl_collector.py','launch_monitor.py','materialize_runtime_config.py','native.py','native_capture.py','native_contract.py','native_source_after.py','runtime_consumer.py','source_after_check.py','supervisor.py')
IDENTITY=('pid','create_time','exe','cwd','cmdline','ppid')
PREFIX=['git','-c','core.longpaths=true','-c','maintenance.auto=false']

def require(condition,message):
    """缺失、漂移和矛盾立即拒绝，退出失败保留原件。"""
    if not condition:raise ValueError(message)

def exact(path,directory=False):
    """精确逐组件核真实文件类型，不规范化文件系统路径。"""
    if type(path) is str:require(str(Path(path))==path,'真实路径不得规范化')
    path=Path(path);require(path.is_absolute() and path.is_relative_to(ROOT),'路径越界或非绝对')
    current=Path(path.anchor)
    for name in path.parts[1:]:
        require(current.is_dir() and name in {p.name for p in current.iterdir()},'精确路径不存在：'+str(path))
        current=current/name;info=current.lstat()
        require(not stat.S_ISLNK(info.st_mode) and not getattr(info,'st_file_attributes',0)&1024,'禁止链接路径')
    require(current.is_dir() if directory else current.is_file(),'路径类型不同')
    return current

def relative(name):
    """绑定只接受POSIX仓库相对identifier；真实路径从ROOT按已声明段取得。"""
    require(type(name) is str and '\\' not in name and ':' not in name and not name.startswith('/'),'相对identifier格式不同')
    require(all(part not in ('','.','..') for part in name.split('/')),'相对identifier有空段或跳转')
    return ROOT/Path(name)

def digest(raw):return hashlib.sha256(raw).hexdigest()
def binding(path):
    path=exact(path);raw=path.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(),sha256=digest(raw),bytes=len(raw))

def bound(row):
    """每项必须含真实SHA和字节长度，额外状态字段只读保留。"""
    require(type(row) is dict and all(k in row for k in ('path','sha256','bytes')),'缺完整绑定')
    require(type(row['bytes']) is int and row['bytes']>=0 and re.fullmatch('[0-9a-f]{64}',row['sha256']) is not None,'绑定类型错误')
    path=relative(row['path']);actual=binding(path)
    require(all(actual[k]==row[k] for k in actual),'原件哈希/长度漂移：'+row['path'])
    return path

def read(path):
    """UTF-8 JSON拒绝重复键。"""
    def unique(pairs):
        result={}
        for key,value in pairs:require(key not in result,'JSON重复键');result[key]=value
        return result
    return json.loads(exact(path).read_text(encoding='utf-8'),object_pairs_hook=unique)

def same_binding(a,b):return all(a.get(k)==b.get(k) for k in ('path','sha256','bytes'))

def baseline(config_row):
    """绑定实际配置、SOURCE、46/33/14、真实G1/G2及完整恢复依赖。"""
    require(bound(config_row)==CONFIG,'配置不是本次精确原件')
    require(config_row['sha256']==CONFIG_SHA,'配置不是已核本轮实际冻结原字节')
    config=read(CONFIG);require(config.get('SOURCE_COMMIT')==SOURCE,'配置SOURCE不同或缺失')
    freeze_path=exact(Path(config['SOURCE_FREEZE']));require(binding(freeze_path)['sha256']==config['SOURCE_FREEZE_SHA'],'SOURCE冻结哈希不同')
    freeze=read(freeze_path);require(freeze.get('source_commit')==SOURCE and freeze.get('profile')=='s2b-inference-platform/0.1.15','SOURCE/profile不符')
    rows=freeze['source_files'];require(len(rows)==46 and len({r['path'] for r in rows})==46,'实际46SOURCE闭包不同')
    hashes={row['path']:row['sha256'] for row in rows}
    for row in rows:bound(row)
    static=freeze['static_source_sha256'];require(len(static)==33 and all(hashes.get(k)==v for k,v in static.items()),'33static不是SOURCE子集')
    frozen=freeze['frozen14'];require(len(frozen)==14 and all(hashes.get(k)==v for k,v in frozen.items()),'原14冻结不同')
    checker_path=relative('verification/check_s2b_inference_platform.py')
    spec=importlib.util.spec_from_file_location('fallback_static',exact(checker_path));checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    require(checker.check_static(ROOT)==static and checker.FROZEN_CORE_SHA256==frozen,'实际static或原14与已冻结不同')
    dependencies=[config_row,binding(freeze_path),*rows]
    for key,field,status in [('FUNCTIONAL_G1','functional_g1',None),('FUNCTIONAL_G2','functional_g2','PASS_G2_FUNCTIONAL_ONLY'),('TOOLS_G2','tool_g2','PASS_TOOL_G2_ONLY')]:
        path=exact(Path(config[key]));row=binding(path)
        require(row['sha256']==config[key+'_SHA'] and same_binding(row,freeze[field]),'G1/G2配置与SOURCE不同')
        if status is not None:require(read(path).get('status')==status and config[key+'_EXPECTED_STATUS']==status,'G2实际状态不同')
        dependencies.append(row)
    review_path=Path(config['TOOLS_G2']);require(binding(review_path)['sha256']==TOOLS_REVIEW_SHA,'独立工具G2不是本轮冻结原件')
    reviewed=read(review_path)['reviewed_tools'];require(len(reviewed)==13,'完整13工具审查集合不同')
    for name in NAMES:
        matches=[r for r in reviewed if r.get('path')==(WORK/name).relative_to(ROOT).as_posix()]
        require(len(matches)==1,'工具缺失或重复：'+name);bound(matches[0])
    dependencies+=reviewed
    runtime=freeze['tool_runtime_dependencies'];require(len(runtime)==1,'额外r01守卫恢复依赖缺失')
    item=runtime[0]
    expected={'actual':ROOT/'tmp/2B/S2B-T17/s15_launch_prepare_20261012_r01/guard.py',
              'recovery':ROOT/'report/evidence/S2B-T17/s15_launch_tools_20261012_r01/tools/guard.py','reviewed_same_bytes':WORK/'guard.py'}
    for key,path in expected.items():require(bound(item[key])==path,'额外守卫依赖路径不同');dependencies.append(item[key])
    require(len({item[key]['sha256'] for key in expected})==1,'守卫实际/恢复/已审字节不同')
    return config,freeze,reviewed,dependencies

def source_record(row,phase,config,freeze):
    """当前RAW与实际阶段snapshot同时核验，不从声明补造快照。"""
    path=bound(row);pre=Path(config['SOURCE_PRE'])
    require(path==pre/('source_'+phase+'.json'),'SOURCE记录路径与阶段不同')
    value=read(path)
    require(value.get('status')=='PASS_SOURCE_'+phase.upper()+'_ONLY' and value.get('source_commit')==SOURCE and value.get('actual_head_at_check')==SOURCE,'SOURCE实际阶段/commit不同')
    require(value.get('source_freeze')==binding(Path(config['SOURCE_FREEZE']))['path'] and value.get('source_freeze_sha256')==config['SOURCE_FREEZE_SHA'],'阶段SOURCE冻结不同')
    hashes={r['path']:r['sha256'] for r in freeze['source_files']}
    require(value.get('source_sha256')==hashes and value.get('static_source_sha256')==freeze['static_source_sha256'] and value.get('frozen14_sha256')==freeze['frozen14'],'阶段46/33/14绑定不同')
    require(value.get('source_count')==46 and value.get('platform_static_source_count')==33 and value.get('profile_version')==freeze['profile'],'阶段计数/profile不同')
    rows=value['source_files'];require(len(rows)==46 and len({r['path'] for r in rows})==46 and {r['path']:r['sha256'] for r in rows}==hashes,'阶段源码行不同')
    snapshots=[]
    for item in rows:
        actual=binding(relative(item['path']));require(actual['sha256']==item['sha256'] and actual['bytes']==item['bytes'],'阶段RAW漂移')
        target=pre/('source_snapshot' if phase=='before' else 'source_snapshot_after')/Path(item['path'])
        require(relative(item['snapshot'])==target,'阶段快照路径不同')
        snapshot=binding(target);require(snapshot['sha256']==actual['sha256'] and snapshot['bytes']==actual['bytes'],'缺快照或快照字节不同');snapshots.append(snapshot)
        require(item.get('git_native_exit_code')==0 and item.get('git_native_command')==PREFIX+['show',SOURCE+':'+item['path']],'阶段Git证据命令/退出码不同')
    return value,snapshots

def git_relation(raw,row,command):
    """核实际既有Git stdout哈希；不启动Git，不以路径或日志文本补造返回码。"""
    require(command.get('command')==PREFIX+['show',SOURCE+':'+row['path']] and command.get('native_exit_code')==0 and command.get('direct_wait') is True,'Git实际direct wait或命令不同')
    relation=row.get('git_relation')
    if relation=='RAW_IDENTICAL':blob=raw
    elif relation=='GIT_LF_TO_RAW_CRLF':
        blob=raw.replace(b'\r\n',b'\n');require(b'\r\n' not in blob and blob.replace(b'\n',b'\r\n')==raw,'不是精确全文件LF->RAWCRLF')
    else:raise ValueError('未知Git字节关系')
    require(digest(blob)==row.get('git_blob_sha256')==command.get('stdout_sha256'),'实际Git stdout哈希与RAW关系不同')

def admission(row,before_row,before,freeze):
    """ROOT已实际执行的48 Git directwait逐项复核，UNKNOWN原件必须绑定保留。"""
    path=bound(row);require(path==ROOTRUN/'source_admission_r01.json','不是ROOT实际SOURCE admission')
    require(row['sha256']==ADMISSION_SHA,'admission不是已核实际48 Git wait原件')
    value=read(path);require(value.get('status')=='READY_SOURCE_BYTES_AND_COMMIT_ONLY' and value.get('source_commit')==SOURCE,'SOURCE admission错误')
    require(same_binding(value['source_before'],before_row) and value['source_freeze']==binding(WORK/'source_freeze_r01.json'),'admission SOURCE原件不同')
    commands=value['git_commands'];require(len(commands)==48,'缺48实际Git wait')
    for terminal in (commands[0],commands[-1]):
        require(terminal['command']==PREFIX+['rev-parse','HEAD'] and terminal['native_exit_code']==0 and terminal['direct_wait'] is True and terminal['stdout_sha256']==digest((SOURCE+'\n').encode()),'admission HEAD实际证据不同')
    for item in before['source_files']:
        matches=[r for r in commands[1:-1] if r['command']==PREFIX+['show',SOURCE+':'+item['path']]]
        require(len(matches)==1,'Git stdout证据缺失或重复');git_relation(relative(item['path']).read_bytes(),item,matches[0])
    require(value['frozen14']==freeze['frozen14'] and value['source_count']==46 and value['static_count']==33,'admission计数/原14不同')
    require(value['failed_capture_status']=='BLOCKED_UNKNOWN_IDENTITY' and value['failed_capture_unknown_count']==27,'admission丢失实际UNKNOWN失败')
    bound(value['failed_capture'])
    require(value['tool_runtime_dependencies']==freeze['tool_runtime_dependencies'],'admission恢复依赖不同')
    return value

def identity_schema(value):
    """所有已知身份严格六字段；未知生灭仅能在专门UNKNOWN记录中表达。"""
    require(type(value) is dict and all(key in value for key in IDENTITY),'缺完整六字段身份')
    require(type(value['pid']) is int and value['pid']>0 and type(value['ppid']) is int and value['ppid']>=0,'身份PID类型不同')
    require(type(value['create_time']) in (int,float) and math.isfinite(value['create_time']) and value['create_time']>0,'身份birth类型不同')
    for key in ('exe','cwd'):
        require(type(value[key]) is str and bool(value[key]) and Path(value[key]).is_absolute() and str(Path(value[key]))==value[key],'身份exe/cwd不是精确绝对路径')
    require(type(value['cmdline']) is list and bool(value['cmdline']) and all(type(item) is str for item in value['cmdline']),'身份完整cmdline类型不同')

def terminal_schema(row):
    """终态身份、状态和值同时核验，未知与复用不能被布尔值隐藏。"""
    identity_schema(row)
    require('same_identity_exists' in row and 'observed_status' in row,'缺已知身份终态字段')
    status=row['observed_status'];exists=row['same_identity_exists']
    require(type(status) is str and (type(exists) is bool or exists is None),'终态字段类型不同')
    if status=='NO_SUCH_PROCESS':require(exists is False,'退出状态矛盾')
    elif status=='PID_REUSED':require(exists is False and row.get('new_object_untouched') is True,'PID复用状态或不触碰声明矛盾')
    elif status in ('ALIVE','IDENTITY_CHANGED'):
        require('actual' in row,'活或漂移对象缺实际六字段');identity_schema(row['actual'])
        same=all(row[key]==row['actual'][key] for key in IDENTITY)
        require((exists is True and same) if status=='ALIVE' else (exists is None and not same),'活或漂移对象状态矛盾')
    elif status=='UNKNOWN_ACCESS_DENIED':
        require(exists is None and type(row.get('exception')) is str and bool(row['exception']),'权限/读取未知缺异常原件')
    else:raise ValueError('未知已知身份终态状态')

def capture_schema(value):
    """原native_capture完整结构先核验，允许完整真实BLOCKED而拒绝任何缺失。"""
    required={'command','wrapper_command','cwd','launcher_identity','direct_child_identity','native_exit_code','direct_child_wait_returned',
              'wrapper_exit_code','capture_status','capture_target_kind','consumed_gate','consumed_gate_after','collection_summary','source_output',
              'elapsed_seconds','sampled_owned_tree_peak_bytes','sample_interval_seconds','unknown_samples','unknown_count','absolute_tree_peak_bytes',
              'confirmed_capture_exits','known_descendant_identity_terminal_observations','known_descendants_same_identity_absent_at_observation',
              'launcher_terminal','entire_os_tree_terminal','budget_stop','python','psutil','tool_bindings_before','tool_bindings_after','stdout','stderr','mode','prefix','closed_logs'}
    require(type(value) is dict and required<=set(value),'SOURCE捕获缺完整metadata')
    for key in ('command','wrapper_command'):
        require(type(value[key]) is list and bool(value[key]) and all(type(item) is str for item in value[key]),'实际argv类型不同')
    require(type(value['cwd']) is str and type(value['prefix']) is str and type(value['mode']) is str,'捕获标识类型不同')
    require(value['capture_target_kind']=='COLLECTOR','捕获target不是COLLECTOR')
    require(type(value['native_exit_code']) is int and type(value['wrapper_exit_code']) is int,'原生/wrapper码必须严格int')
    require(type(value['direct_child_wait_returned']) is bool,'direct wait类型不同')
    require(value['budget_stop'] is None or (type(value['budget_stop']) is str and bool(value['budget_stop'].strip())),'budget_stop缺值或类型不同')
    require(value['capture_status'] in ('CLOSED_NATIVE_SUCCESS','BLOCKED_UNKNOWN_IDENTITY','BLOCKED_BUDGET_OR_BINDING'),'捕获终态状态不同')
    identity_schema(value['launcher_identity']);identity_schema(value['direct_child_identity'])
    require(all(value[key] is None for key in ('consumed_gate','consumed_gate_after','collection_summary')),'SOURCE捕获混入collect对象')
    for key in ('stdout','stderr','source_output'):
        require(type(value[key]) is dict,'捕获绑定类型不同');bound(value[key])
    require(type(value['closed_logs']) is list and len(value['closed_logs'])==2,'闭合流列表不同')
    for key in ('tool_bindings_before','tool_bindings_after'):
        require(type(value[key]) is list and len(value[key])==13,'完整13工具闭包列表不同')
        for row in value[key]:bound(row)
    for key in ('elapsed_seconds','sample_interval_seconds'):
        require(type(value[key]) in (int,float) and math.isfinite(value[key]) and value[key]>=0,'采样时间类型不同')
    require(value['sample_interval_seconds']>0 and type(value['sampled_owned_tree_peak_bytes']) is int and value['sampled_owned_tree_peak_bytes']>=0,'采样峰或节拍类型不同')
    require(value['absolute_tree_peak_bytes'] is None,'离散采集不能补造绝对峰')
    require(type(value['python']) is str and bool(value['python']) and type(value['psutil']) is str and bool(value['psutil']),'工具版本缺失或类型不同')
    require(value['launcher_terminal']=='RUNNING_WHEN_RECORD_WRITTEN' and value['entire_os_tree_terminal']=='NOT_PROVEN_BY_DISCRETE_ENUMERATION','包装或整树终态声明不同')
    unknown=value['unknown_samples']
    require(type(unknown) is list and type(value['unknown_count']) is int and value['unknown_count']==len(unknown),'UNKNOWN原件或计数类型不同')
    for row in unknown:
        require(type(row) is dict and all(key in row for key in ('phase','pid','create_time','exception_type','exception')),'UNKNOWN记录缺实际字段')
        require(all(type(row[key]) is str and bool(row[key]) for key in ('phase','exception_type','exception')),'UNKNOWN异常字段类型不同')
        require(row['pid'] is None or (type(row['pid']) is int and row['pid']>0),'UNKNOWN PID类型不同')
        require(row['create_time'] is None or (type(row['create_time']) in (int,float) and math.isfinite(row['create_time']) and row['create_time']>0),'UNKNOWN birth类型不同')
        if row.get('fresh_readback') is not None:terminal_schema(row['fresh_readback'])
    terminal=value['known_descendant_identity_terminal_observations']
    require(type(terminal) is list and bool(terminal) and type(value['known_descendants_same_identity_absent_at_observation']) is bool,'已知终态列表或absence类型不同')
    for row in terminal:terminal_schema(row)
    require(value['known_descendants_same_identity_absent_at_observation']==all(row['same_identity_exists'] is False for row in terminal),'已知终态汇总与原件矛盾')
    child=value['direct_child_identity'];require(any(all(row[key]==child[key] for key in IDENTITY) for row in terminal),'缺直接子六字段终态')
    require(type(value['confirmed_capture_exits']) is list,'确认退出原件列表类型不同')
    for row in value['confirmed_capture_exits']:
        terminal_schema(row);require(row['same_identity_exists'] is False,'确认退出对象仍活或未知')

def capture(row,phase,source_row,tools):
    """只确认实际collector child0与输出；未知包装终态原样保留，禁止升级PASS。"""
    path=bound(row);require(path.parent==WORK and re.fullmatch('s15_runtime_[A-Za-z0-9_]+\\.native\\.json',path.name),'SOURCE捕获路径不同')
    value=read(path);capture_schema(value);prefix=value['prefix'];require(path.name==prefix+'.native.json' and value.get('mode')=='source','捕获阶段标识不同')
    command=[sys.executable,'-X','utf8','-B',str(WORK/'collector.py'),'source','--commit',SOURCE,'--phase',phase]
    wrappers=[[sys.executable,'-X','utf8','-B',str(WORK/'native.py'),'--prefix',prefix,'--',*command[5:]],
              [sys.executable,'-X','utf8','-B',str(WORK/'native_capture.py'),prefix,*command]]
    require(value.get('command')==command and value.get('wrapper_command') in wrappers and value.get('cwd')==str(ROOT),'SOURCE完整命令或cwd不同')
    require(type(value.get('native_exit_code')) is int and value['native_exit_code']==0 and value.get('direct_child_wait_returned') is True,'不是实际collector child0/directwait')
    launcher=value['launcher_identity'];child=value['direct_child_identity']
    for identity,argv in ((launcher,value['wrapper_command']),(child,command)):
        require(all(key in identity for key in IDENTITY) and identity['cmdline']==argv and identity['exe']==sys.executable and identity['cwd']==str(ROOT),'SOURCE六字段身份不同')
        require(type(identity['pid']) is int and identity['pid']>0 and type(identity['ppid']) is int and identity['ppid']>=0 and type(identity['create_time']) in (float,int) and math.isfinite(identity['create_time']) and identity['create_time']>0,'SOURCE PID/birth错误')
    require(child['ppid']==launcher['pid'] and child['create_time']>=launcher['create_time'],'SOURCE父PID/birth错误')
    require(value.get('tool_bindings_before')==tools and value.get('tool_bindings_after')==tools,'SOURCE冻结工具前后不同')
    logs=[binding(WORK/(prefix+'.'+suffix)) for suffix in ('stdout.bin','stderr.bin')]
    require(value.get('stdout')==logs[0] and value.get('stderr')==logs[1] and value.get('closed_logs')==logs,'SOURCE实际日志字节不同')
    require(value.get('source_output')==source_row,'SOURCE实际输出字节不同')
    printed=json.loads(bound(logs[0]).read_bytes().decode('utf-8'))
    require(printed.get('status')=='PASS_SOURCE_'+phase.upper()+'_ONLY' and printed.get('source_record')==source_row and printed.get('source_count')==46 and printed.get('static_count')==33,'collector stdout不确认实际阶段结果')
    unknown=value.get('unknown_samples');require(type(unknown) is list and type(value.get('unknown_count')) is int and value['unknown_count']==len(unknown),'UNKNOWN原件缺失或计数矛盾')
    if value.get('budget_stop') is not None:
        require(value.get('wrapper_exit_code')==1 and value.get('capture_status')=='BLOCKED_BUDGET_OR_BINDING','预算失败被升级')
    elif unknown or value.get('known_descendants_same_identity_absent_at_observation') is not True:
        require(value.get('wrapper_exit_code')==2 and value.get('capture_status')=='BLOCKED_UNKNOWN_IDENTITY','未知包装被升级PASS')
    else:require(value.get('wrapper_exit_code')==0 and value.get('capture_status')=='CLOSED_NATIVE_SUCCESS','捕获状态与实际终态不同')
    if value['capture_status']=='CLOSED_NATIVE_SUCCESS':
        terminal=value.get('known_descendant_identity_terminal_observations')
        require(type(terminal) is list and bool(terminal) and all(item.get('same_identity_exists') is False for item in terminal),'closed包装终态矛盾')
        require(any(all(item.get(k)==child[k] for k in IDENTITY) for item in terminal),'closed包装缺直接子终态')
    return dict(original=row,original_status=value['capture_status'],original_wrapper_exit_code=value['wrapper_exit_code'],original_wrapper_command=value['wrapper_command'],unknown_count=len(unknown),budget_stop=value.get('budget_stop'),source_child_content_only=True),logs

def budget(rows,claimed):
    """仅保留实际guard/consumer阻断；本入口永远不给预算PASS。"""
    require(type(rows) is list and bool(rows),'缺实际预算原件')
    statuses=[];guard_count=0;raw=[]
    for row in rows:
        path=bound(row);require(path.is_relative_to(ROOTRUN),'预算原件不属于本ROOT运行')
        value=read(path);status=value.get('status');require(type(status) is str,'预算原件状态未知')
        if path.name=='guard_receipt.json':
            guard_count+=1
            require(value.get('source_commit')==SOURCE and value.get('guard_sha256')==binding(WORK/'guard.py')['sha256'],'guard实际SOURCE/工具不同')
            require(value.get('limits')==dict(tree_rss_bytes=6442450944,available_ram_bytes=536870912,c_disk_free_bytes=8589934592) and value.get('sample_interval_seconds')==1,'实际guard预算或节拍不同')
            for item in value.get('files',[]):
                require(item['path'] in ('samples.jsonl','events.jsonl'),'未知guard原流标识')
                record=binding(path.parent/item['path']);require(record['sha256']==item['sha256'],'guard原流丢失或漂移');raw.append(record)
        statuses.append(dict(original=row,status=status,reason=value.get('reason')))
    require(guard_count>0,'缺实际guard预算收据')
    blocked=any('BLOCKED' in row['status'] or row['status'].startswith(('FAIL','STOP_PARTIAL')) for row in statuses)
    actual='BLOCKED' if blocked else 'NOT_PROVEN'
    require(claimed==actual,'预算声明不能改原件或伪称PASS')
    return dict(status=actual,originals=statuses,raw_files=raw,absolute_tree_peak_bytes=None,continuous_budget_pass=False)

def verify(request):
    """SOURCE前后必须都存在；此结果不是原seal、STA或独立审查结果。"""
    require(request.get('source_commit')==SOURCE,'缺本轮SOURCE commit')
    config,freeze,tools,inputs=baseline(request['config'])
    before,snap_before=source_record(request['source_before'],'before',config,freeze)
    after,snap_after=source_record(request['source_after'],'after',config,freeze)
    original_admission=admission(request['source_admission'],request['source_before'],before,freeze)
    require(request['capture_before']==original_admission['failed_capture'],'丢失或替换UNKNOWN27原件')
    captures=[]
    for phase in ('before','after'):
        status,logs=capture(request['capture_'+phase],phase,request['source_'+phase],tools);captures.append(status);inputs+=[request['capture_'+phase],*logs,request['source_'+phase]]
    for item in after['source_files']:
        original=next(row for row in before['source_files'] if row['path']==item['path'])
        require(item['git_blob_sha256']==original['git_blob_sha256'] and item['git_relation']==original['git_relation'],'前后Git字节关系不同')
    inputs += snap_before+snap_after+[request['source_admission'],*request['budget_records']]
    preserved_budget=budget(request['budget_records'],request['budget_status'])
    inputs+=preserved_budget['raw_files']
    extras=request.get('additional_evidence',[]);require(type(extras) is list,'额外证据必须显式列表')
    for row in extras:bound(row)
    inputs+=extras
    unique={}
    for row in inputs:
        bound(row);key=row['path']
        require(key not in unique or same_binding(unique[key],row),'同路径不同字节绑定');unique[key]={key:row[key] for key in ('path','sha256','bytes')}
    return dict(status='SOURCE_CONTENT_CLOSED_ONLY_PRESERVED_RUNTIME_BLOCKS',source_commit=SOURCE,source_count=46,static_count=33,frozen14=freeze['frozen14'],
                captures=captures,budget=preserved_budget,inputs=list(unique.values()),original_seal='NOT_CALLED_NOT_PASSED',mcp9_sta_validation='NOT_IN_SCOPE',sta='NOT_APPROVED_BY_THIS_ENTRY',independent_review='NOT_GRANTED_BY_THIS_ENTRY',hardware='NOT_RUN',stage_g5='NOT_APPROVED')

def save(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')

def package(request_path,output):
    """只创建ROOT明确指定的新目录；核完所有输入后逐字节封包，失败不删除。"""
    request_path=exact(request_path);request=read(request_path);result=verify(request)
    require(output.is_absolute() and str(Path(str(output)))==str(output),'输出必须精确绝对路径')
    parent=exact(output.parent,True)
    require(parent==HERE or parent==ROOT/'report/evidence/S2B-T17','输出父目录未经本任务授权')
    require(not output.exists() and re.fullmatch('s15_source_closure_[A-Za-z0-9_]+',output.name) is not None,'输出存在或名称不同')
    output.mkdir();mapping=[]
    for row in result['inputs']+[binding(request_path),binding(Path(__file__))]:
        source=bound(row);target=output/'raw'/Path(row['path']);target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as stream:stream.write(source.read_bytes())
        require(binding(target)['sha256']==row['sha256'] and binding(source)=={k:row[k] for k in ('path','sha256','bytes')},'封包前后漂移')
        mapping.append(dict(original=row,saved=binding(target)))
    result['raw_mapping']=mapping;save(output/'source_closure_receipt.json',result)
    checks=[dict(name='SOURCE前后内容独立闭合',status='PASS',command=subprocess.list2cmdline([sys.executable,'-X','utf8','-B',str(Path(__file__)),'--request',str(request_path),'--output-dir',str(output)]),exit_code=0,reason='仅实际RAW/snapshot/Git既有directwait哈希及collector child0输出核验。')]
    for status in result['captures']:
        checks.append(dict(name=status['original']['path'],status='FAIL' if status['original_status'].startswith('BLOCKED') else 'PASS',command=subprocess.list2cmdline(status['original_wrapper_command']),exit_code=status['original_wrapper_exit_code'],reason='原生包装原状态保留：'+status['original_status']))
    checks += [dict(name='连续运行预算证明',status='NOT_RUN',command=None,exit_code=None,reason=result['budget']['status']+'原件保留；没有连续预算PASS。'),dict(name='STA/G2/G3/G5',status='NOT_RUN',command=None,exit_code=None,reason='本入口不授予原seal或设计/硬件/阶段批准。')]
    files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=binding(p)['sha256'],role='source' if p.suffix in ('.py','.sv','.v','.tcl','.xdc') else 'log' if p.suffix in ('.bin','.log','.jsonl') else 'result') for p in sorted(output.rglob('*')) if p.is_file()]
    manifest=dict(schema_version=1,stage='2B',task_id='S2B-T17',run_id=output.name,source_commit=SOURCE,evidence_dir=output.relative_to(ROOT).as_posix(),interfaces=[],interfaces_not_applicable_reason='只独立封SOURCE及既有证据，不改硬件业务接口。',tool_versions=dict(python=sys.version),files=files,checks=checks,
                  limitations=['原seal未调用也未通过；UNKNOWN27/26与guard BLOCKED原件保留。','mcp9_sta_validation=NOT_IN_SCOPE；九MCP/五job/STA不属于本工具批准范围。additional_evidence可空，仅按显式原字节封存，不生成或验证其设计语义。','实际Git由ROOT之前执行，本入口复核其直接wait/hash及字节关系，不执行Git。'])
    save(output/'delivery_manifest.json',manifest)
    return dict(status=result['status'],receipt=binding(output/'source_closure_receipt.json'),manifest=binding(output/'delivery_manifest.json'))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--request',required=True);parser.add_argument('--output-dir',required=True);args=parser.parse_args()
    require(str(Path(args.request))==args.request and str(Path(args.output_dir))==args.output_dir,'CLI真实路径不得规范化')
    print(json.dumps(package(Path(args.request),Path(args.output_dir)),ensure_ascii=False))
if __name__=='__main__':main()
