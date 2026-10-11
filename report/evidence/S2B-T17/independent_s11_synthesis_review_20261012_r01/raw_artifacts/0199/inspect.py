import json
from pathlib import Path

# 仅输出当前包的字段形状与必要闭合信息。
root = Path.cwd()
e = root / 'report/evidence/S2B-T17/s11_platform_20261012_r01'
for name in ['s11_source_binding.json', 's11_native_mapping.json', 's11_mcp_binding.json', 'resource_monitoring/resource_index.json']:
    j = json.loads((e / name).read_text(encoding='utf-8'))
    print(name, list(j))
    if 'source' in name:
        print(json.dumps({k:v for k,v in j.items() if k not in ['compiled_rtl','frozen14']},ensure_ascii=False))
    elif 'mcp' in name:
        for x in j['paired_calls']:
            print(x['label'], {k:v for k,v in x.items() if k not in ['native_history','client_record']}, {k:v for k,v in x['native_history'].items() if k != 'output'}, x['client_record'])
    elif 'resource' in name:
        print(json.dumps({k:v for k,v in j.items() if k not in ['files','mapping']},ensure_ascii=False))
        print('row', j.get('files',j.get('mapping'))[0])
gate = json.loads((root/'tmp/2B/S2B-T17/s11_root_run_20261012_r01/root_closed_gate.json').read_text(encoding='utf-8'))
print('GATE', json.dumps(gate,ensure_ascii=False))
manifest=json.loads((e/'s11_delivery_manifest_r05.json').read_text(encoding='utf-8'))
print('CHECKS', json.dumps(manifest['checks'],ensure_ascii=False))
