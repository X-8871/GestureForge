"""S5封存原件的路径核验、只增不改复制与原生退出码记录。"""
from pathlib import Path
import hashlib, json, subprocess, time, sys, os

ROOT = Path(__file__).resolve().parents[4]
WORK = Path(__file__).resolve().parent
REPORT = ROOT / 'report/evidence/S2B-T17/s5_platform_20261011_r01'
PRE = ROOT / 'report/evidence/S2B-T17/s5_source_preflight_20261011_r01'
CACHE = ROOT / 'tmp/2B/S2B-T17/s5_root_run_20261011_r01'
PROJECT = ROOT / 'tmp/2B/S2B-T17/s5p1'
BASELINE = '5cb092dcce3631f310e67228738a674a6a82ce41'
sys.stdout.reconfigure(encoding='utf-8')

def require(value, message):
    """异常立即停止，已保存原件保留。"""
    if not value:
        raise RuntimeError(message)

def exact(path, kind='file'):
    """验证完整路径和目标类型，拒绝符号链接。"""
    require(not path.is_symlink() and (path.is_file() if kind == 'file' else path.is_dir()), str(path))
    return path

def sha(path):
    """流式计算原字节哈希。"""
    digest = hashlib.sha256()
    with exact(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            digest.update(block)
    return digest.hexdigest()

def rel(path):
    return path.relative_to(ROOT).as_posix()

def read(path):
    return json.loads(exact(path).read_text(encoding='utf-8'))

def binding(path):
    return {'path': rel(path), 'sha256': sha(path), 'bytes': path.stat().st_size}

def save(path, value):
    """仅创建新UTF-8文件，不覆盖任何旧原件。"""
    exact(path.parent, 'directory')
    require(not path.exists(), '目标已存在：' + str(path))
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')

def rawcopy(source, target):
    """复制前后核对哈希及长度，拒绝覆盖。"""
    first = binding(source)
    exact(target.parent, 'directory')
    require(not target.exists(), '副本已存在：' + str(target))
    with source.open('rb') as src, target.open('xb') as dst:
        for block in iter(lambda: src.read(1048576), b''):
            dst.write(block)
    copied = binding(target)
    require(first == binding(source) and first['sha256'] == copied['sha256'] and first['bytes'] == copied['bytes'], '复制时原件漂移')
    return {'original_path': rel(source), 'saved_path': rel(target), 'sha256': copied['sha256'], 'bytes': copied['bytes']}

def mkdir_new(path):
    """核验父目录及新名称后创建隔离目录。"""
    exact(path.parent, 'directory')
    require(not path.exists(), '目录已存在：' + str(path))
    path.mkdir()
    return exact(path, 'directory')

def original_check():
    """核对接手前56原件，既有文件不得改变。"""
    rows = read(WORK / 'initial_inventory.json')['files']
    require(len(rows) == 56, '初始库存不同')
    for row in rows:
        require(binding(ROOT / row['path']) == {k: row[k] for k in ('path', 'sha256', 'bytes')}, '初始原件漂移：' + row['path'])
    return rows

def git_blob(path):
    """只读明确提交的Git对象，不消费live源码。"""
    command = ['git', 'show', BASELINE + ':' + path]
    result = subprocess.run(command, cwd=ROOT, capture_output=True)
    require(result.returncode == 0, 'Git对象读取失败：' + path)
    return result.stdout, command, result.returncode

def run_closed(command, prefix):
    """轻量检查结束后保存原生退出码与关闭的日志。"""
    started = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=45, env=dict(os.environ, PYTHONIOENCODING='utf-8'))
    logs = []
    for suffix, raw in (('stdout.log', result.stdout), ('stderr.log', result.stderr)):
        target = WORK / (prefix + '.' + suffix)
        require(not target.exists(), '日志已存在')
        with target.open('xb') as stream:
            stream.write(raw)
        logs.append(binding(target))
    record = {'command': command, 'native_exit_code': result.returncode, 'elapsed_seconds': time.monotonic() - started, 'closed_logs': logs, 'peak_memory_bytes': None, 'process_tree_peak_memory_bytes': None}
    save(WORK / (prefix + '.native.json'), record)
    return record

def copy_closed(prefix):
    return [rawcopy(WORK / (prefix + '.' + suffix), REPORT / (prefix + '.' + suffix)) for suffix in ('stdout.log', 'stderr.log', 'native.json')]

def manifest_files(externals=(), exclude=()):
    """正式files只含path、sha256、role，长度另表保存。"""
    paths = [p for p in sorted(REPORT.rglob('*')) if p.is_file() and p not in exclude]
    rows = []
    for path in paths:
        role = 'source' if path.suffix in ('.py', '.sv', '.v', '.tcl', '.xdc', '.c', '.h', '.sh', '.bat', '.js') else 'log' if path.suffix in ('.log', '.rpt', '.jou', '.vds') else 'artifact' if path.suffix in ('.xsa', '.bd', '.rst') or path.name == '__synthesis_is_complete__' else 'result'
        rows.append({'path': rel(path), 'sha256': sha(path), 'role': role})
    rows += [{'path': row['path'], 'sha256': sha(ROOT / row['path']), 'role': row['role']} for row in externals]
    require(len(rows) == len({r['path'] for r in rows}), '清单路径重复')
    return rows
