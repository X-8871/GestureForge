"""S7 轻量证据收集共用函数，写入须先收到总控闭合门禁。"""
from pathlib import Path
import hashlib, json, subprocess, time, sys, os

ROOT=Path(r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition')
WORK=ROOT/'tmp/2B/S2B-T17/s7_collection_20261011_r01'
REPORT=ROOT/'report/evidence/S2B-T17/s7_platform_20261011_r01'
PRE=ROOT/'report/evidence/S2B-T17/s7_source_preflight_20261011_r01'
CACHE=ROOT/'tmp/2B/S2B-T17/s7_root_run_20261011_r01'
PROJECT=ROOT/'tmp/2B/S2B-T17/s7p1'
BASELINE='a5caefba952a08f365d57193696b08c0e1aff2a5'
BEFORE_SHA='63ed047d38f4bb624c2661c6df5b8c0857973b87245a6daff864b44702d27af4'
FREEZE=ROOT/'report/evidence/S2B-T17/route_address_guard_20261011_r04/source_freeze.json'
FREEZE_SHA='a4cc9d6696bc73545c231cf236b5f82d0845423196acacd44c66851904124df7'
sys.stdout.reconfigure(encoding='utf-8')

def require(value,message):
    """条件不符立即停止，保留已形成的失败证据。"""
    if not value:
        raise RuntimeError(message)

def exact(path,kind='file'):
    """验证完整精确路径、目标类型和符号链接。"""
    require(not path.is_symlink() and (path.is_file() if kind=='file' else path.is_dir()),str(path))
    return path

def rel(path):
    """仅转换已核验完整路径的仓库相对标识。"""
    return path.relative_to(ROOT).as_posix()

def sha(path):
    """流式计算原字节哈希。"""
    digest=hashlib.sha256()
    with exact(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):
            digest.update(block)
    return digest.hexdigest()

def binding(path):
    """长度用于单独库存和映射。"""
    return {'path':rel(path),'sha256':sha(path),'bytes':path.stat().st_size}

def read(path):
    """以 UTF-8 读取 JSON 原件。"""
    return json.loads(exact(path).read_text(encoding='utf-8'))

def closed_gate():
    """显式总控信号是正式收集的前置条件，不推断运行已结束。"""
    gate=read(WORK/'closed_inputs.json')
    require(gate.get('root_explicit_signal')=='CLOSED_INPUTS_READY','缺少总控显式闭合信号')
    require(gate.get('source_commit')==BASELINE and gate.get('project_closed') is True,'闭合基线/状态不同')
    required=('source_after','static_source_closed','immutable_session_log','mcp_history')
    require(all(name in gate for name in required),'关闭输入声明缺失')
    for name in required:
        row=gate[name]
        path=exact(ROOT/row['path'])
        require(sha(path)==row['sha256'],'关闭原件漂移：'+name)
        if 'bytes' in row:
            require(path.stat().st_size==row['bytes'],'关闭原件长度不同：'+name)
    return gate

def new_target(path):
    """准备期仅写隔离目录，正式目录必须先具备关闭信号。"""
    require(path.is_relative_to(WORK) or path.is_relative_to(REPORT),'写入越界：'+str(path))
    if path.is_relative_to(REPORT):
        require((WORK/'closed_inputs.json').is_file(),'准备期禁止写正式包')
        require(read(WORK/'closed_inputs.json').get('root_explicit_signal')=='CLOSED_INPUTS_READY','正式写入门禁缺失')
    exact(path.parent,'directory')
    require(not path.exists(),'目标已存在：'+str(path))

def save(path,value):
    """只创建新 UTF-8 文件，不覆盖已有证据。"""
    new_target(path)
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2)
        stream.write('\n')

def rawcopy(source,target):
    """原字节复制并在复制前后核对哈希与长度。"""
    before=binding(source)
    new_target(target)
    with exact(source).open('rb') as src,target.open('xb') as dst:
        for block in iter(lambda:src.read(1048576),b''):
            dst.write(block)
    copied=binding(target)
    require(before==binding(source) and before['sha256']==copied['sha256'] and before['bytes']==copied['bytes'],'复制时原件漂移')
    return {'original_path':rel(source),'saved_path':rel(target),'sha256':copied['sha256'],'bytes':copied['bytes']}

def mkdir_new(path):
    """核验精确父目录和新名称后创建目录。"""
    new_target(path)
    path.mkdir()
    return exact(path,'directory')

def git_blob(path):
    """只读实际综合提交对象，不消费后来修改的 live 文件。"""
    command=['git','show',BASELINE+':'+path]
    result=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=20)
    require(result.returncode==0,'Git对象读取失败：'+path)
    return result.stdout,command,result.returncode

def run_closed(command,prefix,timeout=55):
    """轻量子进程完成后保存真实 returncode 与关闭日志。"""
    started=time.monotonic()
    result=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=timeout,env=dict(os.environ,PYTHONIOENCODING='utf-8'))
    logs=[]
    for suffix,raw in (('stdout.log',result.stdout),('stderr.log',result.stderr)):
        target=WORK/(prefix+'.'+suffix)
        new_target(target)
        with target.open('xb') as stream:
            stream.write(raw)
        logs.append(binding(target))
    record={'command':command,'native_exit_code':result.returncode,'host_shell_exit_code':None,'elapsed_seconds':time.monotonic()-started,'closed_logs':logs,'peak_memory_bytes':None,'process_tree_peak_memory_bytes':None}
    save(WORK/(prefix+'.native.json'),record)
    return record

def copy_closed(prefix):
    """只复制关闭的原始结果和 stdout/stderr。"""
    return [rawcopy(WORK/(prefix+'.'+suffix),REPORT/(prefix+'.'+suffix)) for suffix in ('stdout.log','stderr.log','native.json')]

def mcp_result(record):
    """支持原始 CallToolResult 和显式 input/result 包装。"""
    result=record.get('result',record)
    require(isinstance(result,dict) and isinstance(result.get('content'),list),'MCP结果格式错误')
    return result

def mcp_json(record):
    """要求 MCP 具有唯一的 JSON 文本内容。"""
    blocks=[b['text'] for b in mcp_result(record)['content'] if b.get('type')=='text']
    require(len(blocks)==1,'MCP文本不唯一')
    return json.loads(blocks[0])

def original_check():
    """初始原件全部按首次库存校验，数量由本轮实际库存决定。"""
    rows=read(WORK/'initial_inventory.json')['files']
    for row in rows:
        require(binding(ROOT/row['path'])==row,'初始原件漂移：'+row['path'])
    return rows

def manifest_files(externals=(),exclude=()):
    """正式行仅 path/sha256/标准 role，长度不混入 files。"""
    rows=[]
    for path in sorted(REPORT.rglob('*')):
        if not path.is_file() or path in exclude:
            continue
        role='source' if path.suffix in ('.py','.sv','.v','.tcl','.xdc','.c','.h','.sh','.bat','.js') else 'log' if path.suffix in ('.log','.rpt','.jou','.vds') else 'artifact' if path.suffix in ('.xsa','.bd','.rst') or path.name=='__synthesis_is_complete__' else 'result'
        rows.append({'path':rel(path),'sha256':sha(path),'role':role})
    rows += [{'path':row['path'],'sha256':sha(ROOT/row['path']),'role':row['role']} for row in externals]
    require(len(rows)==len({r['path'] for r in rows}),'清单路径重复')
    return rows
