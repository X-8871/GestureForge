"""保存S6综合结束后的原生源码核验、静态映射及只读日志快照。"""
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
PREFLIGHT = ROOT / 'report/evidence/S2B-T17/s6_source_preflight_20261011_r01'
LOG = RUN / '.vivado-ai/vivado_17276653_6f07cf83.log'

def digest(path):
    """返回已存在精确文件的原字节哈希。"""
    assert path.is_file(), path
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_new(path, value):
    """只创建新记录，禁止覆盖已有运行证据。"""
    assert path.parent.is_dir() and not path.exists(), path
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    """实际捕获子进程退出码后核对完整冻结集合。"""
    assert ROOT.is_dir() and RUN.is_dir() and PREFLIGHT.is_dir()
    cmd = [sys.executable, '-X', 'utf8', str(RUN / 'source_preflight.py'), 'after']
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True)
    for name, data in [('source_after.stdout.log', result.stdout), ('source_after.stderr.log', result.stderr)]:
        target = RUN / name
        assert not target.exists()
        target.write_bytes(data)
    write_new(RUN / 'source_after.native.json', {'command': cmd, 'cwd': str(ROOT), 'exit_code': result.returncode})
    assert result.returncode == 0, result.stderr.decode('utf-8', errors='replace')
    after = json.loads((PREFLIGHT / 'source_after.json').read_text(encoding='utf-8'))
    spec = importlib.util.spec_from_file_location('s6_closed_checker', ROOT / 'verification/check_s2b_inference_platform.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    mapping = module.check_static(ROOT)
    frozen = {f['path']: f['sha256'] for f in after['source_files']}
    assert len(mapping) == 31 and len(frozen) == 38
    assert all(frozen[name] == value for name, value in mapping.items())
    target = RUN / 'static_actual_closed.json'
    write_new(target, {'status': 'PASS_CLOSED_ACTUAL_STATIC', 'profile': '0.1.6', 'source_commit': after['source_commit'], 'source_count': len(mapping), 'source_sha256': mapping, 'limitations': ['仅静态源码绑定，STA失败，实板未执行']})
    snapshot = RUN / 'root_session_snapshot.log'
    assert LOG.is_file() and not snapshot.exists()
    raw = LOG.read_bytes()
    snapshot.write_bytes(raw)
    assert snapshot.read_bytes() == raw
    write_new(RUN / 'root_session_snapshot_binding.json', {'source_path': LOG.as_posix(), 'snapshot_path': snapshot.as_posix(), 'sha256': digest(snapshot), 'bytes': len(raw), 'project_closed': True, 'scope': 'S6报告与关闭后的日志快照，不允许消费后续追加内容'})
    print(json.dumps({'status': 'PASS_CLOSED_SOURCE_LOG_ONLY', 'source_after_sha256': digest(PREFLIGHT / 'source_after.json'), 'static_sha256': digest(target), 'snapshot_sha256': digest(snapshot), 'snapshot_bytes': len(raw)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
