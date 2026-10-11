"""补齐归档器的可恢复源码绑定，不改变已审查业务事实。"""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
FORMAL = ROOT / 'report/evidence/S2B-T17/independent_s6_synthesis_review_20261011_r01'
OLD_SHA = '4a68f88164145f0cc1477040f090f3090fb612750e9992474171577788932758'

def sha(path):
    """对精确文件计算原字节哈希。"""
    assert path.is_file(), path
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    """只新增r03及两个源码副本，保持r02原件不变。"""
    old = FORMAL / 'delivery_manifest_r02.json'
    new = FORMAL / 'delivery_manifest_r03.json'
    assert FORMAL.is_dir() and sha(old) == OLD_SHA and not new.exists()
    manifest = json.loads(old.read_text(encoding='utf-8'))
    for source, name in [(ROOT / 'tmp/2B/S2B-T16/postconfig_root_run_20261011_r01/archive_reviewed_evidence.py', 'archive_reviewed_evidence.py'), (Path(__file__).resolve(), 'seal_recoverable_archive.py')]:
        target = FORMAL / name
        assert source.is_file() and target.parent.is_dir() and not target.exists()
        shutil.copyfile(source, target)
        assert source.read_bytes() == target.read_bytes()
        manifest['files'].append({'path': target.relative_to(ROOT).as_posix(), 'sha256': sha(target), 'role': 'source'})
    manifest['files'].append({'path': old.relative_to(ROOT).as_posix(), 'sha256': OLD_SHA, 'role': 'artifact'})
    manifest['limitations'].append('本r03只补齐原生归档命令所用共享归档器及本封装器源码；原r02和独审业务事实保持原字节。')
    new.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'SEALED_RECOVERABLE_ARCHIVE_ONLY', 'bindings': len(manifest['files']), 'manifest_sha256': sha(new)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
