"""S6 封存原件的精确路径核验、只增复制与原生退出码记录。"""
from pathlib import Path
import hashlib, json, subprocess, time, sys, os

ROOT = Path(r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition')
WORK = ROOT / 'tmp/2B/S2B-T17/s6_collection_20261011_r01'
REPORT = ROOT / 'report/evidence/S2B-T17/s6_platform_20261011_r01'
PRE = ROOT / 'report/evidence/S2B-T17/s6_source_preflight_20261011_r01'
CACHE = ROOT / 'tmp/2B/S2B-T17/s6_root_run_20261011_r01'
PROJECT = ROOT / 'tmp/2B/S2B-T17/s6p1'
BASELINE = 'b0dbf0dcde758e15046cda36bf2c7424f179b5ae'
sys.stdout.reconfigure(encoding='utf-8')

def require(value, message):
    """异常立即停止并保留已保存原件。"""
    if not value:
        raise RuntimeError(message)

def exact(path, kind='file'):
    """验证完整路径和目标类型，拒绝符号链接。"""
    require(not path.is_symlink() and (path.is_file() if kind == 'file' else path.is_dir()), str(path))
    return path

def sha(path):
    """按原字节流式计算 SHA-256。"""
    digest = hashlib.sha256()
    with exact(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            digest.update(block)
    return digest.hexdigest()

def rel(path):
    """从已核验的完整路径得到仓库相对标识。"""
    return path.relative_to(ROOT).as_posix()

def read(path):
    """以 UTF-8 读取 JSON。"""
    return json.loads(exact(path).read_text(encoding='utf-8'))

def binding(path):
    """长度仅用于库存和诊断映射，不进入正式 files 行。"""
    return {'path': rel(path), 'sha256': sha(path), 'bytes': path.stat().st_size}

def allowed_target(path):
    """写入仅允许当前正式包及隔离收集目录。"""
    require(path.is_relative_to(REPORT) or path.is_relative_to(WORK), '写入越界：' + str(path))
    exact(path.parent, 'directory')
    require(not path.exists(), '目标已存在：' + str(path))

def save(path, value):
    """只创建新 UTF-8 文件，不覆盖失败证据。"""
    allowed_target(path)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')

def rawcopy(source, target):
    """原字节复制，前后核对哈希、长度和授权路径。"""
    before = binding(source)
    allowed_target(target)
    with exact(source).open('rb') as src, target.open('xb') as dst:
        for block in iter(lambda: src.read(1048576), b''):
            dst.write(block)
    after = binding(target)
    require(before == binding(source) and before['sha256'] == after['sha256'] and before['bytes'] == after['bytes'], '复制时原件漂移')
    return {'original_path': rel(source), 'saved_path': rel(target), 'sha256': after['sha256'], 'bytes': after['bytes']}

def mkdir_new(path):
    """核验精确父目录及新名称后创建目录。"""
    allowed_target(path)
    path.mkdir()
    return exact(path, 'directory')

def original_check():
    """逐项检查接手时的 55 份原件。"""
    rows = read(WORK / 'initial_inventory.json')['files']
    require(len(rows) == 55, '初始库存不是55')
    for row in rows:
        require(binding(ROOT / row['path']) == row, '初始原件漂移：' + row['path'])
    return rows

def git_blob(path):
    """只读明确提交的 Git 对象，不消费后来修改的 live 源码。"""
    command = ['git', 'show', BASELINE + ':' + path]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=20)
    require(result.returncode == 0, 'Git对象读取失败：' + path)
    return result.stdout, command, result.returncode

def run_closed(command, prefix, timeout=45):
    """运行轻量检查并保存真正的子进程退出码及关闭日志。"""
    started = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=timeout, env=dict(os.environ, PYTHONIOENCODING='utf-8'))
    logs = []
    for suffix, raw in (('stdout.log', result.stdout), ('stderr.log', result.stderr)):
        target = WORK / (prefix + '.' + suffix)
        allowed_target(target)
        with target.open('xb') as stream:
            stream.write(raw)
        logs.append(binding(target))
    record = {'command': command, 'native_exit_code': result.returncode, 'host_shell_exit_code': None, 'elapsed_seconds': time.monotonic() - started, 'closed_logs': logs, 'peak_memory_bytes': None, 'process_tree_peak_memory_bytes': None}
    save(WORK / (prefix + '.native.json'), record)
    return record

def copy_closed(prefix):
    """只复制已经关闭的 stdout、stderr 和原生结果。"""
    return [rawcopy(WORK / (prefix + '.' + suffix), REPORT / (prefix + '.' + suffix)) for suffix in ('stdout.log', 'stderr.log', 'native.json')]

def manifest_files(externals=(), exclude=()):
    """正式行只使用 path、sha256、标准 role。"""
    paths = [p for p in sorted(REPORT.rglob('*')) if p.is_file() and p not in exclude]
    rows = []
    for path in paths:
        role = 'source' if path.suffix in ('.py','.sv','.v','.tcl','.xdc','.c','.h','.sh','.bat','.js') else 'log' if path.suffix in ('.log','.rpt','.jou','.vds') else 'artifact' if path.suffix in ('.xsa','.bd','.rst') or path.name == '__synthesis_is_complete__' else 'result'
        rows.append({'path': rel(path), 'sha256': sha(path), 'role': role})
    rows += [{'path': row['path'], 'sha256': sha(ROOT / row['path']), 'role': row['role']} for row in externals]
    require(len(rows) == len({r['path'] for r in rows}), '清单路径重复')
    return rows
