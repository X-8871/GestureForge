"""绑定重新连接后新Run配置，仅替换上次启动器的运行及配置字面量。"""
from pathlib import Path
import hashlib
import json

folder = Path(__file__).absolute().parent
source = folder.parent / 'board_run_20261013_r03/run_visibility.ps1'
original = source.read_bytes()
sha = lambda raw: hashlib.sha256(raw).hexdigest()
assert sha(original) == '50fffedf17b831d979b8902893dd28f683f7fff66a1beac85191c38d6fde09ee'
config = folder.parent / 'board_prepare_20261013_r01/visibility_probe_config_r04.json'
assert config.is_file() and sha(config.read_bytes()) == 'ef0ec949aa9996e3e020343e15f374f7f0efcc8386dd78de2e9a3f2071f11430'
changes = [(str(source.parent), str(folder), 1),
           ('visibility_probe_config_r03.json', 'visibility_probe_config_r04.json', 1),
           ('06c669da0e006c093628162c555cc77bf790d02a9cabf8d9b97d9f1c22de42ab', sha(config.read_bytes()), 2)]
raw = original
for old, new, count in changes:
    assert raw.count(old.encode('utf-8')) == count
    raw = raw.replace(old.encode('utf-8'), new.encode('utf-8'))
target = folder / 'run_visibility.ps1'
assert not target.exists()
with target.open('xb') as output:
    output.write(raw)
(folder / 'launcher_derivation.json').write_text(json.dumps({'source': str(source),
    'source_sha256': sha(original), 'derived_sha256': sha(raw), 'literal_changes': changes,
    'hardware_execution': 'NOT_RUN'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'derived': str(target), 'sha256': sha(raw)}))
