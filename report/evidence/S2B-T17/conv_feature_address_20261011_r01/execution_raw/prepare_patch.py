#!/usr/bin/env python3
"""生成限定生产差异供apply_patch应用，不直接写生产文件。"""
import difflib
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
BASE="3f24c94564d10103aaa00db07356f666b085f687"
changes={}
def replace(text,before,after):
    """要求唯一字符匹配，保持未授权部分原样。"""
    assert text.count(before)==1,before
    return text.replace(before,after)
engine="src/s2b_conv_tile_engine.sv"
old=(ROOT/engine).read_text(encoding="utf-8")
pairs=[
    ["    logic [63:0] feature_source_offset;\n", "    logic [63:0] feature_geometry_plane;\n    logic [63:0] feature_channel_plane_offset;\n    logic [63:0] feature_row_offset;\n    logic [63:0] feature_source_offset;\n"],
    ["        feature_source_offset = 64'd0;\n", "        feature_geometry_plane = 64'd0;\n        feature_channel_plane_offset = 64'd0;\n        feature_row_offset = 64'd0;\n        feature_source_offset = 64'd0;\n"],
    ["                feature_source_offset =\n                    ((({32'd0, feature_scan_channel} * {32'd0, input_height_latched}) +\n                      feature_input_y[63:0]) * {32'd0, input_width_latched}) +\n                    feature_input_x[63:0];\n",
     "                // 原signed bounds保证Y高32为零；只在消费分支用精确32乘32行偏移。\n                feature_geometry_plane = {32'd0, input_height_latched} * {32'd0, input_width_latched};\n                feature_channel_plane_offset = {32'd0, feature_scan_channel} * feature_geometry_plane;\n                feature_row_offset = {32'd0, feature_input_y[31:0]} * {32'd0, input_width_latched};\n                feature_source_offset = feature_channel_plane_offset + feature_row_offset +\n                                        feature_input_x[63:0];\n"]]
new=old
for before,after in pairs:new=replace(new,before,after)
changes[engine]=new
p="verification/check_s2b_inference_platform.py";text=(ROOT/p).read_text(encoding="utf-8")
text=text.replace("s2b-inference-platform/0.1.9","s2b-inference-platform/0.1.10").replace("variable version 0.1.9","variable version 0.1.10")
anchor='DERIVATION_RULES["src/s2a_conv_tile_engine.sv"][1].extend(CONV_OUTPUT_ADDRESS_REPLACEMENTS)\n'
text=replace(text,anchor,anchor+'\n# S10仅重排feature地址，行截位只在原signed bounds内消费。\nCONV_FEATURE_ADDRESS_REPLACEMENTS = '+repr(pairs)+'\nDERIVATION_RULES["src/s2a_conv_tile_engine.sv"][1].extend(CONV_FEATURE_ADDRESS_REPLACEMENTS)\n')
text=replace(text,'"board/ps_platform_fields.json", "verification/check_s2b_inference_platform.py"', '"board/ps_platform_fields.json", "verification/check_s2b_inference_platform.py",\n         "verification/test_s2b_conv_feature_address_rtl.py"')
changes[p]=text
p="board/s2b_inference_platform.json";profile=json.loads((ROOT/p).read_text(encoding="utf-8"))
profile["version"]="s2b-inference-platform/0.1.10"
item=next(i for i in profile["source_derivation"]["derived_sources"] if i["path"]==engine)
item["sha256"]=hashlib.sha256(new.encode()).hexdigest();item["replacements"].extend(pairs)
changes[p]=json.dumps(profile,ensure_ascii=False,indent=2)+"\n"
p="vivado/s2b_inference_platform.tcl";changes[p]=replace((ROOT/p).read_text(encoding="utf-8"),"variable version 0.1.9","variable version 0.1.10")
for p in ("verification/test_s2b_geometry_specialization_rtl.py","verification/test_s2b_backend_coordinates_rtl.py","verification/test_s2b_conv_validation_rtl.py"):
    text=(ROOT/p).read_text(encoding="utf-8").replace("5ea54b441bd885e10eac4794cbad5ad48c510a49",BASE).replace("variable version 0.1.9","variable version 0.1.10")
    if p.endswith("conv_validation_rtl.py"):
        text=text.replace("conv_output_address_(?:boundary|layer0)","conv_(?:output|feature)_address_(?:boundary|layer0)").replace('"S2B-T17-S9"','"S2B-T17-S10"')
    changes[p]=text
p="verification/test_s2b_conv_output_address_rtl.py";text=(ROOT/p).read_text(encoding="utf-8")
text=text.replace("5ea54b441bd885e10eac4794cbad5ad48c510a49",BASE).replace("e8231b045b4b94565cb7b54c1e127878ad1850e88c70298c86af6d74009eebf8","ea3e123327827a2d090a705bb7e364af29cf7e1088bc86c7bd54bf55e36df5fc").replace("s8_conv_tile_engine_original","s9_conv_tile_engine_original").replace("s9_conv_g1_20261011_r01","s10_conv_g1_20261011_r01")
changes[p]=text
p="board/s2b_inference_platform.md";text=(ROOT/p).read_text(encoding="utf-8")
text=replace(text,"版本 `s2b-inference-platform/0.1.9`","版本 `s2b-inference-platform/0.1.10`")
text=replace(text,"本轮S9开发基线为已保存S8实际综合失败证据的提交 `5ea54b441bd885e10eac4794cbad5ad48c510a49`。","本轮S10开发基线为已保存S9实际综合失败证据的提交 `3f24c94564d10103aaa00db07356f666b085f687`。")
text=text.replace("实际编译闭包精确为7+7+4","实际编译闭包精确为6+8+4")
text+='\n## S10：CONV feature地址组合因式分解\n\n原signed64坐标生成及bounds比较保持；在bounds内0≤Y<H≤UINT32严格蕴含Y高32位为零。仅此消费分支将原嵌套offset改为C×(H×W)+Y×W+X，plane使用精确64位，channel和base加法仍原unsigned64回绕，row使用零扩展Y低32×W的精确64结果。新三个组合信号完整默认零；未bounds的offset/address仍零。扫描结束→padding→range→read优先、所有端口/FSM/always_ff/owner/错误语义及逐周期请求保持，输出侧S9坐标截断不变。\n\nS9实际综合WNS−4.527ns/TNS−1840.705ns仍FAIL。S10功能G1、独立G2、真实STA与G3分别判断；本组合结构不声明时序改善或50MHz闭合，不增加流水或33/65位拒绝。100黄金样本、109正式样本及1000次实板指标不变。\n'
changes[p]=text
print("*** Begin Patch")
for p,newtext in changes.items():
    before=(ROOT/p).read_text(encoding="utf-8")
    print("*** Update File: "+str(ROOT/p))
    for line in list(difflib.unified_diff(before.splitlines(),newtext.splitlines(),lineterm=""))[2:]:
        print("@@" if line.startswith("@@") else line)
print("*** End Patch")
