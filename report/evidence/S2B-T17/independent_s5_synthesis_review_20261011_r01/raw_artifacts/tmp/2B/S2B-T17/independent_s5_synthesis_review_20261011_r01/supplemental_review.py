"""补核精确methodology计数、S4例外保留及实际生成参数。"""
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

out = Path(__file__).resolve().parent
root = out.parents[3]
base = root / 'report/evidence/S2B-T17/s5_platform_20261011_r01'
if len(sys.argv) == 1:
    command = [sys.executable, '-B', '-X', 'utf8', str(Path(__file__).resolve()), '--check']
    started = time.monotonic()
    proc = subprocess.run(command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    logs = []
    for suffix, raw in [('stdout.log', proc.stdout), ('stderr.log', proc.stderr)]:
        target = out / ('supplemental.' + suffix)
        assert not target.exists()
        target.write_bytes(raw)
        logs.append({'path': target.relative_to(root).as_posix(), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
    result = {'command': command, 'native_exit_code': proc.returncode, 'elapsed_seconds': time.monotonic() - started,
              'closed_logs': logs, 'process_tree_peak_memory_bytes': None}
    target = out / 'supplemental.native.json'
    assert not target.exists()
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(proc.stdout.decode('utf-8'))
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(proc.returncode)

methodology = (base / 'methodology_synth.rpt').read_text(encoding='utf-8')
assert re.findall(r'^\s*Checks found:\s*(\d+)\s*$', methodology, re.M) == ['747']
assert re.findall(r'^\|\s*TIMING-16\s*\|\s*(\w+)\s*\|\s*Large setup violation\s*\|\s*(\d+)\s*\|', methodology, re.M) == [('Warning', '747')]
current = json.loads((base / 's5_collection_constraints_binding.json').read_text(encoding='utf-8'))
prior = json.loads((root / 'report/evidence/S2B-T17/s4_platform_20261011_r01/s4_collection_constraints_binding.json').read_text(encoding='utf-8'))
assert current['exported_reset_cdc_false_paths'] == prior['exported_reset_cdc_false_paths']
generated = (base / 'generated_inputs/s2b_inference_infer_0.sv').read_text(encoding='utf-8')
assert re.findall(r'\.PROFILE_VISIBILITY_PROVEN\(([^)]+)\)', generated) == ["1'D0"]
assert 'PROFILE_VISIBILITY_PROVEN=0' in generated and 'FREQ_HZ 50000000' in generated
result = {'status': 'PASS_EVIDENCE_INTEGRITY_ONLY', 'reviewed_source_commit': '5cb092dcce3631f310e67228738a674a6a82ce41',
          'reviewed_manifest_sha256': 'efc201ca9b69139aa95813403a5c0b8af0b22e89eb72a1bd29b439dc9f647945',
          'checks': {'methodology_checks': 747, 'TIMING-16_severity': 'Warning', 'S4_reset_CDC_false_paths_unchanged': True,
                     'generated_visibility_literal': "1'D0", 'generated_clock_hz': 50000000},
          'limitations': ['仅对失败综合证据补核；未实现、未下载，不批准板上验收。']}
target = out / 'supplemental_result.json'
assert not target.exists()
target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
