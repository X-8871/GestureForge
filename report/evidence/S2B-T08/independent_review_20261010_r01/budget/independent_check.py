"""独立使用模型层元数据及显式 patch 坐标枚举复核静态预算。"""
import hashlib
import json
import math
import subprocess
from pathlib import Path

root = Path.cwd()
run = root / 'report/evidence/S2B-T08/request_budget_20261009_r01'
model = json.loads((root / 'report/evidence/S2A-T01/tiny416_model_manifest.json').read_text(encoding='utf-8'))
result = json.loads((run / 'request_budget_result.json').read_text(encoding='utf-8'))
binding = json.loads((run / 'source_binding.json').read_text(encoding='utf-8'))
baseline = '3d424b9cc207e85375ef4f703ee193806c73bd34'
assert result['source_commit'] == binding['source_commit'] == baseline
for item in binding['bindings']:
    actual = (root / item['original_path']).read_bytes()
    snapshot = (root / item['snapshot_path']).read_bytes()
    committed = subprocess.check_output(['git', 'show', baseline + ':' + item['original_path']])
    # 工作树行尾可与 Git blob 不同，逐行内容仍须完全相等。
    assert actual.replace(b'\r\n', b'\n') == committed.replace(b'\r\n', b'\n')
    assert actual == snapshot
    assert hashlib.sha256(actual).hexdigest() == item['sha256'] == item['snapshot_sha256']

totals = dict(reads=0, writes=0, requests=0, feature_reads=0, weight_reads=0,
              compute_reduction_cycles=0, requant_cycles=0, padding_scan_no_request=0)
for layer, reported in zip(model['layers'], result['layers'], strict=True):
    n, outc, outh, outw = layer['output_shape_nchw']
    assert n == 1
    feat = weight = compute = requant = padding = 0
    output = outc * outh * outw
    op = layer['op']
    writes = output if op != 'yolo' else 0
    if op == 'convolutional':
        inc, inh, inw = layer['input_shape_nchw'][1:]
        kh, kw = layer['kernel_hw']
        sy, sx = layer['stride_hw']
        pl, pr, pt, pb = layer['padding_lrtb']
        tiles = 0
        for by in range(0, outh, 8):
            for bx in range(0, outw, 8):
                tiles += 1
                # 枚举实际 tile 的完整 patch 坐标，而非复用被审脚本的轴求和函数。
                ys = range(by * sy - pt, (by + min(8, outh - by) - 1) * sy - pt + kh)
                xs = range(bx * sx - pl, (bx + min(8, outw - bx) - 1) * sx - pl + kw)
                valid = sum(0 <= y < inh and 0 <= x < inw for y in ys for x in xs)
                feat += inc * valid
                padding += inc * (len(ys) * len(xs) - valid)
                weight += outc * inc * kh * kw
        compute = math.ceil(outc / 8) * outh * outw * inc * kh * kw
        requant = output
        assert layer['groups'] == 1
        assert weight == tiles * layer['gf8_parameter_offsets']['quantized_weight_bytes']
    elif op == 'maxpool':
        inc, inh, inw = layer['input_shape_nchw'][1:]
        kh, kw = layer['kernel_hw']
        sy, sx = layer['stride_hw']
        pad = layer['darknet_padding_parameter'] // 2
        feat = outc * sum(0 <= y * sy - pad + ky < inh and 0 <= x * sx - pad + kx < inw
                         for y in range(outh) for x in range(outw) for ky in range(kh) for kx in range(kw))
    elif op in ('route', 'upsample'):
        feat = output
    elif op != 'yolo':
        raise AssertionError(op)
    actual = dict(reads=feat + weight, writes=writes, requests=feat + weight + writes,
                  feature_reads=feat, weight_reads=weight, compute_reduction_cycles=compute,
                  requant_cycles=requant, padding_scan_no_request=padding)
    for key, value in actual.items():
        assert value == reported[key], (layer['layer_index'], key, value, reported[key])
        totals[key] += value
assert totals == result['totals']
nonservice = 2 * totals['requests'] + totals['compute_reduction_cycles'] + totals['requant_cycles'] + totals['padding_scan_no_request']
assert nonservice == 623242289 == result['deadline']['nonservice_cycles_lower_bound']
assert totals['requests'] == 96135961
assert nonservice + 39 * totals['requests'] == 4372544768 > (2**32 - 1)
assert result['deadline']['necessary_average_service_upper_cycles_with_nonservice_lower_bound'] == (2**32 - 1 - nonservice) / totals['requests']
print(json.dumps({'status': 'PASS_INDEPENDENT_METADATA_ENUMERATION_AND_GIT_SOURCE_BINDING', 'layers': 38,
                  'totals': totals, 'nonservice_lower_bound': nonservice,
                  'source_bindings': len(binding['bindings']),
                  'key_sha256': {name: hashlib.sha256((run / name).read_bytes()).hexdigest()
                                 for name in ['delivery_manifest.json', 'request_budget_result.json', 'calculate_budget.py', 'request_budget.md']}}, ensure_ascii=False, indent=2))
