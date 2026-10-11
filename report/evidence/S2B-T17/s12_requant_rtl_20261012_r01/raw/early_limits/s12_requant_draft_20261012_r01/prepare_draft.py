import difflib
import hashlib
import json
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def exactly_once(text, before, after):
    assert text.count(before) == 1, repr(before)
    return text.replace(before, after, 1)


def segment(text, start, end):
    position = text.index(start)
    return text[position:text.index(end, position)]


def replace_preserving_eol(text, before, after):
    # 仅替换目标行；其余原始字节及各行原有换行保持原样。
    lines = text.splitlines(keepends=True)
    expected = before.splitlines()
    indexes = [index for index in range(len(lines) - len(expected) + 1)
               if [line.rstrip('\r\n') for line in lines[index:index + len(expected)]] == expected]
    assert len(indexes) == 1
    index = indexes[0]
    ending = '\r\n' if lines[index].endswith('\r\n') else '\n'
    replacement = ''.join(line + ending for line in after.splitlines())
    return ''.join(lines[:index]) + replacement + ''.join(lines[index + len(expected):])


def main():
    root = Path.cwd()
    directory = Path(__file__).resolve().parent
    production = root / 'src/s2b_conv_tile_engine.sv'
    original_raw = production.read_bytes()
    original_sha = digest(original_raw)
    assert original_sha == '51b76623b29a852ebf66cb818ef947d932c14055e4acbb20bd8fe811bb32d555'
    old = original_raw.decode('utf-8').replace('\r\n', '\n')
    new = exactly_once(old, '    logic signed [63:0] requant_signed_value;\n', '')
    new = exactly_once(new, "        requant_signed_value = 64'sd0;\n", '')
    original_clamp = '''            if (requant_accumulator[31]) begin
                requant_signed_value =
                    -$signed({1'b0, requant_rounded_magnitude});
            end else begin
                requant_signed_value =
                    $signed({1'b0, requant_rounded_magnitude});
            end
            if (requant_signed_value > 64'sd127) begin
                requantized_value = 8'sd127;
            end else if (requant_signed_value < -64'sd127) begin
                requantized_value = -8'sd127;
            end else begin
                requantized_value = requant_signed_value[7:0];
            end
'''
    new_clamp = '''            if (|requant_rounded_magnitude[63:7]) begin
                requantized_value = requant_accumulator[31] ? -8'sd127 : 8'sd127;
            end else if (requant_accumulator[31]) begin
                requantized_value = -$signed(requant_rounded_magnitude[7:0]);
            end else begin
                requantized_value = $signed(requant_rounded_magnitude[7:0]);
            end
'''
    new = exactly_once(new, original_clamp, new_clamp)
    assert 'requant_signed_value' not in new
    # 草稿局部编辑并保留原有混合换行；patch采用UTF-8与LF。
    proposed_text = original_raw.decode('utf-8')
    proposed_text = replace_preserving_eol(proposed_text, '    logic signed [63:0] requant_signed_value;\n', '')
    proposed_text = replace_preserving_eol(proposed_text, "        requant_signed_value = 64'sd0;\n", '')
    proposed_text = replace_preserving_eol(proposed_text, original_clamp, new_clamp)
    assert proposed_text.replace('\r\n', '\n') == new
    proposed_raw = proposed_text.encode('utf-8')
    draft_path = directory / 's2b_conv_tile_engine.sv'
    patch_path = directory / 'draft.patch'
    receipt_path = directory / 'prepare_result.json'
    for path in (draft_path, patch_path, receipt_path):
        assert not path.exists(), str(path)
    patch = ''.join(difflib.unified_diff(old.splitlines(keepends=True), new.splitlines(keepends=True),
                                       fromfile='a/src/s2b_conv_tile_engine.sv',
                                       tofile='b/src/s2b_conv_tile_engine.sv', n=3))
    interface_end = old.index(');\n') + len(');\n')
    interface_same = old[:interface_end] == new[:interface_end]
    sequential_start = '    always_ff @(posedge clk) begin\n'
    sequential_same = old[old.index(sequential_start):] == new[new.index(sequential_start):]
    arithmetic_start = '            requant_parameter = lane_mq_parameter[requant_lane_index];\n'
    arithmetic_end = '            if (requant_accumulator[31]) begin\n                requant_signed_value'
    preserved_arithmetic = segment(old, arithmetic_start, arithmetic_end)
    assert preserved_arithmetic in new
    prefix_same = segment(old, '    always_comb begin\n', "        requant_parameter = 80'd0;\n") == segment(new, '    always_comb begin\n', "        requant_parameter = 80'd0;\n")
    suffix_same = old[old.index('        mapped_response_error = INTERNAL;'):] == new[new.index('        mapped_response_error = INTERNAL;'):]
    assert interface_same and sequential_same and prefix_same and suffix_same
    assert production.read_bytes() == original_raw
    address_patch = root / 'tmp/2B/S2B-T17/s12_conv_address_draft_20261012_r01/draft.patch'
    address_patch_sha = digest(address_patch.read_bytes())
    assert address_patch_sha == 'f9b3149d9c072dea9377469717ab2287b7403fd0adf4b4454262702498441a64'
    draft_path.write_bytes(proposed_raw)
    patch_path.write_bytes(patch.encode('utf-8'))
    result = {
        'status': 'DRAFT_PREPARED_ONLY_G0_MATH_BASIS',
        'baseline_head': '932051cdacdf02f729d6a7554b07118d05e96aa4',
        'production_source_commit': 'a710ec431474841a81912a6055f861e811a151e3',
        'source_path': 'src/s2b_conv_tile_engine.sv',
        'source_raw_sha256': original_sha,
        'proposed_source_raw_sha256': digest(proposed_raw),
        'patch_sha256': digest(patch.encode('utf-8')),
        'prepare_native_exit_code': 0,
        'invariants': {
            'interface_ports_parameters_exact_text_unchanged': interface_same,
            'all_always_ff_and_following_text_exact_unchanged': sequential_same,
            'parameter_selection_magnitude_product_rounding_shift_exact_unchanged': True,
            'upstream_combinational_validation_address_compute_exact_unchanged': prefix_same,
            'response_mapping_handshake_sequential_text_exact_unchanged': suffix_same,
            'production_raw_unchanged': True,
            'draft_untouched_original_eol_preserved': True,
            'signed64_value_declaration_default_and_clamp_only_modified': True},
        'other_frozen_patch': {'path': 'tmp/2B/S2B-T17/s12_conv_address_draft_20261012_r01/draft.patch',
                               'sha256': address_patch_sha, 'read_only': True},
        'prior_prepare_failure': {'native_exit_code': 1, 'reason': '首次草稿脚本错误假设全文件为CRLF；断言在任何输出写入前拒绝，现改为局部保留原始换行', 'production_written': False},
        'integration': ['两个patch均按局部上下文应用到当前生产文本，禁止以任意whole-file草稿覆盖已合并的另一改动',
                        '先核原基线与两patch哈希，按不重叠组合段应用，再对合并后生产SHA重新冻结并审查',
                        'ROOT生产writer统一更新实际适用的派生checker、profile版本、闭包SHA与现有清单；本草稿没有虚构注册',
                        '保持50MHz、-2、visibility0与全部FF/状态机/公开接口'],
        'g1_pending': ['实际RTL编译检查signed8 unary-minus的位宽及符号',
                       '原→拟实际RTL并行对照与全部公开请求/响应/结果周期trace，覆盖随机背压',
                       '绑定原CPU黄金，使用独立手算样例与原始requant RTL参考，不能只比较两个同源算法',
                       'accumulator全域代表边界、-2^31、零、正负半舍入、±126/127/128、合法M/q边界与非对称正负MQ参数',
                       '白盒补充全部unsigned32乘数及q=0/1/47/63/64/65/255；非法MQ仍按原优先返回',
                       'ARG/RANGE/LENGTH与compute非法字节/overflow优先组合、错误不消费输出、全部状态abort/reset与恢复',
                       '重跑两patch合并影响的CONV功能、地址、参数选择及公共周期回归，再独立冻结G2审查',
                       '独立G2后才开展全平台STA；当前没有新增STA结果'],
        'mutants_not_executed': ['删除rounding：A=1,M=1,q=1原应1，错误0',
                                 '负饱和改-128：A=-128,M=1,q=0原应-127',
                                 '检测[63:8]漏bit7：A=128,M=1,q=0原应127，错误-128',
                                 'product截32：A=65536,M=65536,q=0原应127，错误0',
                                 'rounded[63]恢复符号：A=-1,M=1,q=0原应-1，错误+1',
                                 'shift低6位回绕：A=-2^31,M=0xFFFFFFFF,q=64原应0，错误-127',
                                 '负数错误选择正参数：A=-2，正M=1/q0、负M=2/q0原应-4，错误-2'],
        'limits': ['G0数学结论仅适用二值整数；未证明任意X/Z或被强制的不合法64位rounded值',
                   '未运行实际RTL/编译、CPU黄金、公开trace、mutants、STA、实板或G1/G2',
                   '没有生产写入、Git提交、ROSS或进程/硬件操作']}
    receipt_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'source_raw_sha256': original_sha,
                      'proposed_source_raw_sha256': result['proposed_source_raw_sha256'],
                      'patch_sha256': result['patch_sha256'], 'invariants': result['invariants']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
