"""固定新Run配置及已审入口，只替换上次启动器的精确字面量。"""
from pathlib import Path
import hashlib
import json

folder = Path(__file__).absolute().parent
source = folder.parent / 'board_run_20261013_r02/run_visibility.ps1'
original = source.read_bytes()
config = folder.parent / 'board_prepare_20261013_r01/visibility_probe_config_r03.json'
entry = folder.parents[3] / 'vitis/run_s2b_visibility_probe.py'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert config.is_file() and entry.is_file()
assert sha(config) == '06c669da0e006c093628162c555cc77bf790d02a9cabf8d9b97d9f1c22de42ab'
assert sha(entry) == '2015542ac9766110657112030040dd30d0f333223f8d60b5d31348bd65bd9638'
changes = [(str(source.parent), str(folder), 1),
           ('visibility_probe_config_r02.json', 'visibility_probe_config_r03.json', 1),
           ('fb9004b81360093c5b36e7b79ae7528bfdf3705e79d217e961587c6c78bbe637', sha(config), 2),
           ('01e7668a5af91a3f110ae92bcdeecdcf4cb56f12d4dd8f2cc3c45ee6d7ed71ab', sha(entry), 1)]
raw = original
for old, new, count in changes:
    assert raw.count(old.encode('utf-8')) == count, old
    raw = raw.replace(old.encode('utf-8'), new.encode('utf-8'))
target = folder / 'run_visibility.ps1'
assert not target.exists()
with target.open('xb') as output:
    output.write(raw)
(folder / 'launcher_derivation.json').write_text(json.dumps({'source': str(source),
    'source_sha256': hashlib.sha256(original).hexdigest(), 'derived_sha256': sha(target),
    'literal_changes': changes, 'hardware_execution': 'NOT_RUN'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'derived': str(target), 'sha256': sha(target)}))
