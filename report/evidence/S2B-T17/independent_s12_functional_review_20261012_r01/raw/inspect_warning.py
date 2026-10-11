import json
from pathlib import Path
p=Path('report/evidence/S2B-T17/s12_conv_cones_20261012_r03')
v=json.loads((p/'validation.json').read_text(encoding='utf-8'))
for exe,diagnostics in v['controlled_multidriven_diagnostics'].items():
 for d in diagnostics:
  if 'u_private' in d['raw'] and "'state'" in d['raw']:print(exe,d)
print('TB',[(i+1,l) for i,l in enumerate((p/'tb_s12_conv_cones.sv').read_text(encoding='utf-8').splitlines()) if '$cast(u_private.state' in l])
