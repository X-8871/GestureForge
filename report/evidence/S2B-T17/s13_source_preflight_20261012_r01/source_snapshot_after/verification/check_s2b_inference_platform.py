#!/usr/bin/env python3
"""只读检查平台闭包和可见性启用证据；不运行 Vivado、不修改任何文件。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
from pathlib import Path, PurePosixPath

PROFILE_VERSION = "s2b-inference-platform/0.1.13"
# 冻结上游原字节与允许的派生差异均独立固定，不能由自报哈希授权变更。
FROZEN_CORE_SHA256 = {
    "src/s2a_network_descriptor_pkg.sv": "e83a592d15908474498380bcaedb6db034a2b4e2165af6ea998335351c35f183",
    "src/int8_maxpool_geometry.sv": "320c5414e29f33681f96c3667cb068cbcbf319a97827f3531c87092dac073db5",
    "src/int8_maxpool_window.sv": "0ea5865e939a691ccb7fea4602fd31211c816d13424ac7c77c89713ff5a15653",
    "src/int8_route_query.sv": "6a033547cc6bc40572be5a3253a559f10b21d98a55dc68541bce8b137598bbba",
    "src/int8_upsample_query.sv": "488f90c2b7c7e1c3adfd0b6bc939b4c57082daaa334e8db35b78fb7c8f814fc7",
    "src/s2a_conv_tile_engine.sv": "08fc2789a7eda4047a7496fd93fece44d037dcf1121bab9ac15affecd10025aa",
    "src/s2a_maxpool_engine.sv": "3dbb1fd41fbe773debade2629e8e7565554d14051a906466042906bb925de7b7",
    "src/s2a_route_engine.sv": "4748df19474e6b90e11bb760854311da92ba8d19a5b1d4b12e3d7b2b7968fe44",
    "src/s2a_upsample_engine.sv": "2c08bbc9c1d85e94de448f613617a5d584fe5682d0c4858d550bf377302e195b",
    "src/s2a_network_backend.sv": "93937585df647bf9535248e01416cd8f2337eb6dd0b17adff6fe61194828db55",
    "src/s2a_memory_master.sv": "721d7e09356986d23a6c1f723fe49322057b05aa02ac27e1b5887789b8bacf07",
    "src/s2a_runtime_shell.sv": "c784de2c94456eb4bdbd9ff763454b9784ebcb8d8821d6505d68707cfc37e52e",
    "src/s2a_stage2a_core_ooc.sv": "2700e71c930062a428634deb5b1e3d3e2d3ff711657bb66995ac2c442560169c",
    "src/s2a_control_csr.sv": "97fc62dd1967ea9486db1c6e48134283d62005805a0ca5ef44d6ea70ab2fc9d2",
}
DERIVATION_RULES = {
    "src/s2a_maxpool_engine.sv": ("src/s2b_maxpool_engine.sv", [["module s2a_maxpool_engine (","module s2b_maxpool_engine ("],[".kernel_height(kernel_height)",".kernel_height(32'd2)"],[".kernel_width(kernel_width)",".kernel_width(32'd2)"],[".stride_y(stride_y)",".stride_y(32'd2)"],[".stride_x(stride_x)",".stride_x(32'd2)"],[".darknet_padding_parameter(darknet_padding_parameter)",".darknet_padding_parameter(32'd1)"]]),
    "src/s2a_upsample_engine.sv": ("src/s2b_upsample_engine.sv", [["module s2a_upsample_engine (","module s2b_upsample_engine ("],[".stride(stride)",".stride(32'd2)"]]),
    "src/s2a_network_backend.sv": ("src/s2b_network_backend.sv", [["module s2a_network_backend (","module s2b_network_backend ("],["s2a_maxpool_engine u_maxpool_engine","s2b_maxpool_engine u_maxpool_engine"],["s2a_upsample_engine u_upsample_engine","s2b_upsample_engine u_upsample_engine"]]),
    "src/s2a_stage2a_core_ooc.sv": ("src/s2b_stage2b_core.sv", [["module s2a_stage2a_core_ooc #(","module s2b_stage2b_core #("],["s2a_network_backend u_network_backend","s2b_network_backend u_network_backend"]]),
}
LEGACY_2B_SOURCES = ("src/s2b_request_guard.sv", "src/s2b_hp0_word_adapter.sv",
                     "src/s2b_control_csr.sv", "src/s2b_inference_top.sv")

# 只授权原六个索引更新分支中的坐标寄存器；全部文字独立固定。
COORDINATE_REPLACEMENTS = [
    ["    logic [31:0] output_element_index;",
     "    logic [31:0] output_element_index;\n"
     "    // 冻结38层均为单批次；坐标只沿原索引赋值分支更新。\n"
     "    logic [8:0] output_channel_cursor;\n"
     "    logic [7:0] output_y_cursor;\n"
     "    logic [7:0] output_x_cursor;"],
    ["            decoded_channel = (output_element_index / output_plane_elements) % output_c;\n"
     "            decoded_y = (output_element_index / {48'd0, output_w}) % output_h;\n"
     "            decoded_x = output_element_index % output_w;",
     "            decoded_channel = {23'd0, output_channel_cursor};\n"
     "            decoded_y = {24'd0, output_y_cursor};\n"
     "            decoded_x = {24'd0, output_x_cursor};"],
]
for prefix, indent in (("        if (hard_reset) begin\n", 12),
                       ("        end else if (abort) begin\n", 12),
                       ("                    if (backend_start && buffer_owner_pl) begin\n", 24)):
    gap = " " * indent
    # 复位分支含state赋值；启动分支由layer赋值开始。
    before = prefix + (gap + "state <= ST_IDLE;\n" if indent == 12 else "")
    before += gap + "layer_cursor <= 6'd0;\n" + gap + "output_element_index <= 32'd0;"
    after = before + "\n" + gap + "output_channel_cursor <= 9'd0;\n"
    after += gap + "output_y_cursor <= 8'd0;\n" + gap + "output_x_cursor <= 8'd0;"
    COORDINATE_REPLACEMENTS.append([before, after])
for indent in (32, 28):
    gap = " " * indent
    before = "\n" + gap + "output_element_index <= 32'd0;"
    after = before + "\n" + gap + "output_channel_cursor <= 9'd0;\n"
    after += gap + "output_y_cursor <= 8'd0;\n" + gap + "output_x_cursor <= 8'd0;"
    COORDINATE_REPLACEMENTS.append([before, after])
COORDINATE_REPLACEMENTS.append([
    "                            output_element_index <= output_element_index + 32'd1;",
    "                            output_element_index <= output_element_index + 32'd1;\n"
    "                            // 原末元素条件排除通道溢出，不增加owner或结果门禁。\n"
    "                            if ({8'd0, output_x_cursor} == (output_w - 16'd1)) begin\n"
    "                                output_x_cursor <= 8'd0;\n"
    "                                if ({8'd0, output_y_cursor} == (output_h - 16'd1)) begin\n"
    "                                    output_y_cursor <= 8'd0;\n"
    "                                    output_channel_cursor <= output_channel_cursor + 9'd1;\n"
    "                                end else begin\n"
    "                                    output_y_cursor <= output_y_cursor + 8'd1;\n"
    "                                end\n"
    "                            end else begin\n"
    "                                output_x_cursor <= output_x_cursor + 8'd1;\n"
    "                            end"
])
DERIVATION_RULES["src/s2a_network_backend.sv"][1].extend(COORDINATE_REPLACEMENTS)

# ROUTE仅派生固定ROM的1/2组；通用2A多组分支和原14字节完整保留。
DERIVATION_RULES["src/int8_route_query.sv"] = ("src/s2b_route_query.sv", [
    ["module int8_route_query (", "module s2b_route_query ("],
    ["        end else if (groups > 32'd2) begin\n            if ((source_count != 32'd1) ||\n                ((source0_channels % groups) != 32'd0)) begin\n                bad_argument = 1'b1;\n            end else begin\n                expected_group_start =\n                    {32'd0, group_id} * (source0_channels / groups);\n                expected_group_end = expected_group_start +\n                                     (source0_channels / groups);\n                if ((source0_channel_start != expected_group_start[31:0]) ||\n                    (source0_channel_end != expected_group_end[31:0])) begin\n                    bad_argument = 1'b1;\n                end\n            end\n        end\n", "        end else if (groups > 32'd2) begin\n            // 冻结tiny416的ROUTE只会产生1或2；通用多组语义保留在2A原件。\n            bad_argument = 1'b1;\n        end"]])
DERIVATION_RULES["src/s2a_route_engine.sv"] = ("src/s2b_route_engine.sv", [
    ["module s2a_route_engine (", "module s2b_route_engine ("],
    ["int8_route_query u_query", "s2b_route_query u_query"]])
DERIVATION_RULES["src/s2a_network_backend.sv"][1].append(
    ["s2a_route_engine u_route_engine", "s2b_route_engine u_route_engine"])


# batch非1在原首个校验分支拒绝；只有校验通过的轨迹使用输出元素数。
DERIVATION_RULES["src/s2a_conv_tile_engine.sv"] = ("src/s2b_conv_tile_engine.sv", [["module s2a_conv_tile_engine (","module s2b_conv_tile_engine ("],["input_elements_wide = {96'd0, input_batch_count_latched} *\n                              {96'd0, input_channels_latched} *","input_elements_wide = {96'd0, input_channels_latched} *"],["output_elements_wide = {96'd0, output_batch_count_latched} *\n                               {96'd0, output_channels_latched} *","output_elements_wide = {96'd0, output_channels_latched} *"]])
DERIVATION_RULES["src/s2a_network_backend.sv"][1].append(
    ["s2a_conv_tile_engine u_conv_engine", "s2b_conv_tile_engine u_conv_engine"])

# 前置非零和R<=4608保护窄位宽；溢出独立拒绝，保持原错误分支顺序。
PATCH_GUARD_REPLACEMENTS = [
    [
        "    logic [127:0] full_tile_patch_height_wide;\n    logic [127:0] full_tile_patch_width_wide;\n    logic [127:0] full_tile_patch_bytes_wide;\n    logic [127:0] full_weight_group_bytes_wide;\n",
        "    logic [2:0] full_tile_patch_delta_y;\n    logic [2:0] full_tile_patch_delta_x;\n    logic [18:0] full_tile_patch_height_narrow;\n    logic [18:0] full_tile_patch_width_narrow;\n    logic [31:0] full_tile_patch_plane_narrow;\n    logic [28:0] full_tile_patch_bytes_narrow;\n    logic full_tile_patch_height_bad;\n    logic full_tile_patch_width_bad;\n    logic full_tile_patch_bad;\n"
    ],
    [
        "        full_tile_patch_height_wide = 128'd0;\n        full_tile_patch_width_wide = 128'd0;\n        full_tile_patch_bytes_wide = 128'd0;\n        if ((output_height_latched != 32'd0) && (output_width_latched != 32'd0)) begin\n            full_tile_patch_height_wide =\n                ({96'd0, (output_height_latched < TILE_EDGE ? output_height_latched : TILE_EDGE) - 32'd1} *\n                 {96'd0, stride_y_latched}) + {96'd0, kernel_height_latched};\n            full_tile_patch_width_wide =\n                ({96'd0, (output_width_latched < TILE_EDGE ? output_width_latched : TILE_EDGE) - 32'd1} *\n                 {96'd0, stride_x_latched}) + {96'd0, kernel_width_latched};\n            full_tile_patch_bytes_wide = full_tile_patch_height_wide *\n                                         full_tile_patch_width_wide *\n                                         {96'd0, input_channels_latched};\n        end\n        full_weight_group_bytes_wide =\n            {96'd0, (output_channels_latched < LANE_COUNT ? output_channels_latched : LANE_COUNT)} *\n            reduction_count_wide;\n\n",
        "        // 首分支保证C、KH、KW非零且乘积不超过4608，范围分支才消费此判据。\n        // D为0时stride不参与patch；非零D必须另查stride高位，不能截断后放行。\n        full_tile_patch_delta_y = output_height_latched == 32'd0 ? 3'd0 :\n            (output_height_latched < TILE_EDGE ? output_height_latched[2:0] - 3'd1 : 3'd7);\n        full_tile_patch_delta_x = output_width_latched == 32'd0 ? 3'd0 :\n            (output_width_latched < TILE_EDGE ? output_width_latched[2:0] - 3'd1 : 3'd7);\n        full_tile_patch_height_narrow =\n            ({16'd0, full_tile_patch_delta_y} * {3'd0, stride_y_latched[15:0]}) +\n            {6'd0, kernel_height_latched[12:0]};\n        full_tile_patch_width_narrow =\n            ({16'd0, full_tile_patch_delta_x} * {3'd0, stride_x_latched[15:0]}) +\n            {6'd0, kernel_width_latched[12:0]};\n        full_tile_patch_height_bad =\n            ((full_tile_patch_delta_y != 3'd0) && (stride_y_latched[31:16] != 16'd0)) ||\n            (full_tile_patch_height_narrow[18:16] != 3'd0) ||\n            (full_tile_patch_height_narrow[15:0] > 16'd51200);\n        full_tile_patch_width_bad =\n            ((full_tile_patch_delta_x != 3'd0) && (stride_x_latched[31:16] != 16'd0)) ||\n            (full_tile_patch_width_narrow[18:16] != 3'd0) ||\n            (full_tile_patch_width_narrow[15:0] > 16'd51200);\n        full_tile_patch_plane_narrow =\n            {16'd0, full_tile_patch_height_narrow[15:0]} *\n            {16'd0, full_tile_patch_width_narrow[15:0]};\n        full_tile_patch_bytes_narrow =\n            {13'd0, full_tile_patch_plane_narrow[15:0]} *\n            {16'd0, input_channels_latched[12:0]};\n        full_tile_patch_bad = full_tile_patch_height_bad || full_tile_patch_width_bad ||\n            (full_tile_patch_plane_narrow[31:16] != 16'd0) ||\n            (full_tile_patch_bytes_narrow > 29'd51200);\n\n"
    ],
    [
        "                     (full_tile_patch_bytes_wide > MAX_FEATURE_PATCH_BYTES) ||\n                     (full_weight_group_bytes_wide > MAX_WEIGHT_GROUP_BYTES)) begin",
        "                     full_tile_patch_bad) begin"
    ]
]
DERIVATION_RULES["src/s2a_conv_tile_engine.sv"][1].extend(PATCH_GUARD_REPLACEMENTS)

# 正因子和首分支保护长度化简；精确替换仍禁止时序块、接口及错误优先漂移。
LENGTH_GUARD_REPLACEMENTS = [
    [
        "    logic [127:0] reduction_count_wide;\n",
        "    logic [127:0] reduction_count_wide;\n    logic [63:0] input_element_plane;\n    logic [63:0] output_element_plane;\n    logic [63:0] input_element_product;\n    logic [63:0] output_element_product;\n    logic [25:0] reduction_plane_narrow;\n    logic [25:0] reduction_count_narrow;\n    logic [44:0] expected_weight_bytes_narrow;\n    logic reduction_count_bad;\n"
    ],
    [
        "        input_elements_wide = {96'd0, input_channels_latched} *\n                              {96'd0, input_height_latched} *\n                              {96'd0, input_width_latched};\n        output_elements_wide = {96'd0, output_channels_latched} *\n                               {96'd0, output_height_latched} *\n                               {96'd0, output_width_latched};\n        expected_weight_bytes_wide = {96'd0, output_channels_latched} *\n                                     {96'd0, input_channels_latched} *\n                                     {96'd0, kernel_height_latched} *\n                                     {96'd0, kernel_width_latched};\n        reduction_count_wide = {96'd0, input_channels_latched} *\n                               {96'd0, kernel_height_latched} *\n                               {96'd0, kernel_width_latched};\n",
        "        // 首分支已逐因子拒绝零；长度分支只消费正数乘积。\n        // 前两因子精确64位，高32位非零必超UINT32；否则再精确乘第三因子。\n        input_element_plane = {32'd0, input_channels_latched} * {32'd0, input_height_latched};\n        output_element_plane = {32'd0, output_channels_latched} * {32'd0, output_height_latched};\n        input_element_product = {32'd0, input_element_plane[31:0]} * {32'd0, input_width_latched};\n        output_element_product = {32'd0, output_element_plane[31:0]} * {32'd0, output_width_latched};\n        input_elements_wide = {64'd0, input_element_product};\n        output_elements_wide = {64'd0, output_element_product};\n\n        // 正C/KH/KW的R<=4608蕴含每个因子及C*KH均<=4608；低位截断另有拒绝保护。\n        reduction_plane_narrow = {13'd0, input_channels_latched[12:0]} *\n                                 {13'd0, kernel_height_latched[12:0]};\n        reduction_count_narrow = {13'd0, reduction_plane_narrow[12:0]} *\n                                 {13'd0, kernel_width_latched[12:0]};\n        reduction_count_bad = (input_channels_latched > 32'd4608) ||\n            (kernel_height_latched > 32'd4608) || (kernel_width_latched > 32'd4608) ||\n            (reduction_plane_narrow > 26'd4608) || (reduction_count_narrow > 26'd4608);\n        reduction_count_wide = {102'd0, reduction_count_narrow};\n        // 长度分支已保证R<=4608，故OC32*R13的45位结果精确；不提前消费MQ限制。\n        expected_weight_bytes_narrow = {13'd0, output_channels_latched} *\n                                       {32'd0, reduction_count_narrow[12:0]};\n        expected_weight_bytes_wide = {83'd0, expected_weight_bytes_narrow};\n"
    ],
    [
        "            (reduction_count_wide == 128'd0) ||\n            (reduction_count_wide > 128'd4608) ||\n",
        "            reduction_count_bad ||\n"
    ],
    [
        "        end else if ((input_elements_wide > 128'h0000_0000_0000_0000_FFFF_FFFF) ||\n",
        "        end else if ((input_element_plane[63:32] != 32'd0) ||\n                     (input_element_product[63:32] != 32'd0) ||\n"
    ],
    [
        "                     (output_elements_wide > 128'h0000_0000_0000_0000_FFFF_FFFF) ||\n",
        "                     (output_element_plane[63:32] != 32'd0) ||\n                     (output_element_product[63:32] != 32'd0) ||\n"
    ],
    [
        "                     (expected_weight_bytes_wide > 128'h0000_0000_0000_0000_FFFF_FFFF) ||\n",
        "                     (expected_weight_bytes_narrow[44:32] != 13'd0) ||\n"
    ]
]
DERIVATION_RULES["src/s2a_conv_tile_engine.sv"][1].extend(LENGTH_GUARD_REPLACEMENTS)

# S9仅在原unsigned64模域中重排输出地址乘加；C/Y/X赋值、守卫及全部FF不变。
CONV_OUTPUT_ADDRESS_REPLACEMENTS = [
    ["    logic [31:0] output_channel_current;\n",
     "    logic [31:0] output_channel_current;\n"
     "    logic [63:0] output_geometry_plane;\n"
     "    logic [63:0] output_channel_plane_offset;\n"
     "    logic [63:0] output_row_offset;\n"],
    ["        output_byte_offset_wide =\n"
     "            (({32'd0, output_channel_current} * {32'd0, output_height_latched} +\n"
     "              {32'd0, output_global_y}) * {32'd0, output_width_latched}) +\n"
     "            {32'd0, output_global_x};\n",
     "        // 保留C/Y/X原32位截断；全部乘加在原unsigned64模域内因式分解。\n"
     "        output_geometry_plane = {32'd0, output_height_latched} * {32'd0, output_width_latched};\n"
     "        output_channel_plane_offset = {32'd0, output_channel_current} * output_geometry_plane;\n"
     "        output_row_offset = {32'd0, output_global_y} * {32'd0, output_width_latched};\n"
     "        output_byte_offset_wide = output_channel_plane_offset + output_row_offset +\n"
     "                                  {32'd0, output_global_x};\n"]
]
DERIVATION_RULES["src/s2a_conv_tile_engine.sv"][1].extend(CONV_OUTPUT_ADDRESS_REPLACEMENTS)

# S10仅重排feature地址，行截位只在原signed bounds内消费。
CONV_FEATURE_ADDRESS_REPLACEMENTS = [['    logic [63:0] feature_source_offset;\n', '    logic [63:0] feature_geometry_plane;\n    logic [63:0] feature_channel_plane_offset;\n    logic [63:0] feature_row_offset;\n    logic [63:0] feature_source_offset;\n'], ["        feature_source_offset = 64'd0;\n", "        feature_geometry_plane = 64'd0;\n        feature_channel_plane_offset = 64'd0;\n        feature_row_offset = 64'd0;\n        feature_source_offset = 64'd0;\n"], ["                feature_source_offset =\n                    ((({32'd0, feature_scan_channel} * {32'd0, input_height_latched}) +\n                      feature_input_y[63:0]) * {32'd0, input_width_latched}) +\n                    feature_input_x[63:0];\n", "                // 原signed bounds保证Y高32为零；只在消费分支用精确32乘32行偏移。\n                feature_geometry_plane = {32'd0, input_height_latched} * {32'd0, input_width_latched};\n                feature_channel_plane_offset = {32'd0, feature_scan_channel} * feature_geometry_plane;\n                feature_row_offset = {32'd0, feature_input_y[31:0]} * {32'd0, input_width_latched};\n                feature_source_offset = feature_channel_plane_offset + feature_row_offset +\n                                        feature_input_x[63:0];\n"]]
DERIVATION_RULES["src/s2a_conv_tile_engine.sv"][1].extend(CONV_FEATURE_ADDRESS_REPLACEMENTS)

# S7只删除前置校验蕴含的地址守卫并缩短组合地址；其余严格派生链不变。
ROUTE_QUERY_ADDRESS_REPLACEMENTS = [
    [
        "    logic [63:0] selected_offset;\n    logic [63:0] selected_address_wide;\n",
        "    logic [31:0] selected_offset;\n    logic [31:0] selected_address;\n"
    ],
    [
        "    logic [31:0] selected_length_bytes;\n",
        ""
    ],
    [
        "        selected_offset = 64'd0;\n        selected_address_wide = 64'd0;\n",
        "        selected_offset = 32'd0;\n        selected_address = 32'd0;\n"
    ],
    [
        "        selected_length_bytes = 32'd0;\n",
        ""
    ],
    [
        "            selected_length_bytes = source0_length_bytes;\n",
        ""
    ],
    [
        "            selected_length_bytes = source1_length_bytes;\n",
        ""
    ],
    [
        "        if (selected_value == -8'sd128) begin\n            bad_argument = 1'b1;\n        end\n\n",
        "        if (selected_value == -8'sd128) begin\n            bad_argument = 1'b1;\n        end\n\n        // 前置shape、坐标、长度及对象端点检查保证成功路径地址精确落在32位。\n"
    ],
    [
        "            (({32'd0, selected_source_channel} * {32'd0, source0_height}) +\n             {32'd0, output_y}) * {32'd0, source0_width} +\n            {32'd0, output_x};\n        selected_address_wide = {32'd0, selected_base_address} + selected_offset;\n        if ((selected_offset >= {32'd0, selected_length_bytes}) ||\n            (selected_address_wide > 64'h0000_0000_FFFF_FFFF)) begin\n            bad_range = 1'b1;\n        end\n",
        "            ((selected_source_channel * source0_height) + output_y) *\n            source0_width + output_x;\n        selected_address = selected_base_address + selected_offset;\n"
    ],
    [
        "            source_address = selected_address_wide[31:0];\n",
        "            source_address = selected_address;\n"
    ]
]
DERIVATION_RULES["src/int8_route_query.sv"][1].extend(ROUTE_QUERY_ADDRESS_REPLACEMENTS)
ROUTE_ENGINE_ADDRESS_REPLACEMENTS = [
    [
        "    logic [64:0] output_offset_work;\n",
        "    logic [31:0] output_offset_work;\n"
    ],
    [
        "                               {33'd0, output_width_latched};\n",
        "                               {33'd0, output_width_latched};\n        // VALIDATE前两分支通过时，query坐标和对象范围保证偏移精确落在32位。\n"
    ],
    [
        "            (({33'd0, output_channel_latched} * {33'd0, output_height_latched}) +\n             {33'd0, output_y_latched}) * {33'd0, output_width_latched} +\n            {33'd0, output_x_latched};\n",
        "            ((output_channel_latched * output_height_latched) + output_y_latched) *\n            output_width_latched + output_x_latched;\n"
    ],
    [
        "                    end else if ((output_offset_work >= {33'd0, output_length_latched}) ||\n                                 (output_base_latched + output_offset_work[31:0] < output_base_latched)) begin\n                        result_error_latched <= BAD_RANGE;\n                        state <= RESULT;\n",
        ""
    ]
]
DERIVATION_RULES["src/s2a_route_engine.sv"][1].extend(ROUTE_ENGINE_ADDRESS_REPLACEMENTS)



# S8保留原geometry全域语义，仅将非负地址乘加拆成低位精确值及有效tap高位守卫。
MAXPOOL_GEOMETRY_REPLACEMENTS = [
    [
        "module int8_maxpool_geometry (",
        "module s2b_maxpool_geometry ("
    ],
    [
        "    logic [63:0] row_index_work [0:2];\n    logic [95:0] row_offset_work [0:2];\n    logic [95:0] logical_offset_work;\n    logic [96:0] address_work;",
        "    logic [32:0] row_index_work [0:2];\n    logic row_index_high [0:2];\n    logic [63:0] row_offset_work [0:2];\n    logic [32:0] logical_offset_work;\n    logic [32:0] address_work;\n    logic selected_row_high;\n    logic selected_offset_high;"
    ],
    [
        "        logical_offset_work = 96'd0;\n        address_work = 97'd0;",
        "        logical_offset_work = 33'd0;\n        address_work = 33'd0;\n        selected_row_high = 1'b0;\n        selected_offset_high = 1'b0;"
    ],
    [
        "            row_index_work[row_index] = 64'd0;\n            row_offset_work[row_index] = 96'd0;",
        "            row_index_work[row_index] = 33'd0;\n            row_index_high[row_index] = 1'b0;\n            row_offset_work[row_index] = 64'd0;"
    ],
    [
        "                // 各行独立预计算，避免 tap 的行内地址重复执行宽乘法。",
        "                // 每行低32位和进位分别保留；高位只由实际有效tap消费。\n                // 正width保证行高位非零时完整地址必超UINT32，不能提前拒绝padding行。"
    ],
    [
        "                        row_index_work[row_index] = channel_row_work +\n                            {32'd0, row_y_work[row_index][31:0]};\n                        row_offset_work[row_index] =\n                            {32'd0, row_index_work[row_index]} * {64'd0, input_width};",
        "                        row_index_work[row_index] = {1'b0, channel_row_work[31:0]} +\n                            {1'b0, row_y_work[row_index][31:0]};\n                        row_index_high[row_index] =\n                            (channel_row_work[63:32] != 32'd0) || row_index_work[row_index][32];\n                        row_offset_work[row_index] =\n                            {32'd0, row_index_work[row_index][31:0]} * {32'd0, input_width};"
    ],
    [
        "                            case (kernel_y_work)\n                                0: logical_offset_work = row_offset_work[0] +\n                                    {64'd0, tap_source_x[tap_index][31:0]};\n                                1: logical_offset_work = row_offset_work[1] +\n                                    {64'd0, tap_source_x[tap_index][31:0]};\n                                2: logical_offset_work = row_offset_work[2] +\n                                    {64'd0, tap_source_x[tap_index][31:0]};\n                                default: logical_offset_work = 96'd0;\n                            endcase\n                            address_work = {65'd0, input_base_address} +\n                                {1'b0, logical_offset_work};\n                            if (address_work[96:32] != 65'd0) begin",
        "                            // 行偏移、列和base均非负；每段高位或进位保留完整越界语义。\n                            logical_offset_work = {1'b0, row_offset_work[kernel_y_work][31:0]} +\n                                {1'b0, tap_source_x[tap_index][31:0]};\n                            selected_row_high = row_index_high[kernel_y_work];\n                            selected_offset_high = row_offset_work[kernel_y_work][63:32] != 32'd0;\n                            address_work = {1'b0, input_base_address} +\n                                {1'b0, logical_offset_work[31:0]};\n                            if (selected_row_high || selected_offset_high ||\n                                logical_offset_work[32] || address_work[32]) begin"
    ]
]
# S11按非负分配律独立计算通道平面和行偏移，全部进位仅由有效tap消费。
MAXPOOL_GEOMETRY_REPLACEMENTS.extend([
    [
        "    logic signed [63:0] source_x_work;\n    logic [63:0] channel_row_work;\n    logic signed [63:0] row_y_work [0:2];\n",
        "    logic signed [63:0] source_x_work;\n    logic [63:0] plane_work;\n    logic [63:0] channel_offset_work;\n    logic channel_offset_high;\n    logic signed [63:0] row_y_work [0:2];\n"
    ],
    [
        "    logic signed [63:0] row_y_work [0:2];\n    logic [32:0] row_index_work [0:2];\n    logic row_index_high [0:2];\n    logic [63:0] row_offset_work [0:2];\n",
        "    logic signed [63:0] row_y_work [0:2];\n    logic [63:0] row_offset_work [0:2];\n"
    ],
    [
        "    logic [63:0] row_offset_work [0:2];\n    logic [32:0] logical_offset_work;\n",
        "    logic [63:0] row_offset_work [0:2];\n    logic [32:0] channel_row_sum_work;\n    logic [32:0] logical_offset_work;\n"
    ],
    [
        "        source_x_work = 64'sd0;\n        channel_row_work = 64'd0;\n        logical_offset_work = 33'd0;\n",
        "        source_x_work = 64'sd0;\n        plane_work = 64'd0;\n        channel_offset_work = 64'd0;\n        channel_offset_high = 1'b0;\n        channel_row_sum_work = 33'd0;\n        logical_offset_work = 33'd0;\n"
    ],
    [
        "            row_y_work[row_index] = 64'sd0;\n            row_index_work[row_index] = 33'd0;\n            row_index_high[row_index] = 1'b0;\n            row_offset_work[row_index] = 64'd0;\n",
        "            row_y_work[row_index] = 64'sd0;\n            row_offset_work[row_index] = 64'd0;\n"
    ],
    [
        "                source_x_work = origin_x + $signed({31'd0, output_x_step});\n                // 合法通道和行坐标保证 channel*height+source_y 小于 2^64。\n                channel_row_work = {32'd0, input_channel} * {32'd0, input_height};\n                // 每行低32位和进位分别保留；高位只由实际有效tap消费。\n                // 正width保证行高位非零时完整地址必超UINT32，不能提前拒绝padding行。\n                for (row_index = 0; row_index < 3; row_index = row_index + 1) begin\n",
        "                source_x_work = origin_x + $signed({31'd0, output_x_step});\n                // 通道平面与行偏移分配计算；通道为零时高平面不会产生地址高位。\n                plane_work = {32'd0, input_height} * {32'd0, input_width};\n                channel_offset_work = {32'd0, input_channel} * {32'd0, plane_work[31:0]};\n                channel_offset_high = ((input_channel != 32'd0) && (plane_work[63:32] != 32'd0)) ||\n                    (channel_offset_work[63:32] != 32'd0);\n                // 每行乘积精确保留64位；高位只由实际有效tap消费，padding不提前拒绝。\n                for (row_index = 0; row_index < 3; row_index = row_index + 1) begin\n"
    ],
    [
        "                        (row_y_work[row_index] < $signed({32'd0, input_height}))) begin\n                        row_index_work[row_index] = {1'b0, channel_row_work[31:0]} +\n                            {1'b0, row_y_work[row_index][31:0]};\n                        row_index_high[row_index] =\n                            (channel_row_work[63:32] != 32'd0) || row_index_work[row_index][32];\n                        row_offset_work[row_index] =\n",
        "                        (row_y_work[row_index] < $signed({32'd0, input_height}))) begin\n                        row_offset_work[row_index] =\n"
    ],
    [
        "                        row_offset_work[row_index] =\n                            {32'd0, row_index_work[row_index][31:0]} * {32'd0, input_width};\n                    end\n",
        "                        row_offset_work[row_index] =\n                            {32'd0, row_y_work[row_index][31:0]} * {32'd0, input_width};\n                    end\n"
    ],
    [
        "                            tap_valid_mask[tap_index] = 1'b1;\n                            // 行偏移、列和base均非负；每段高位或进位保留完整越界语义。\n                            logical_offset_work = {1'b0, row_offset_work[kernel_y_work][31:0]} +\n                                {1'b0, tap_source_x[tap_index][31:0]};\n",
        "                            tap_valid_mask[tap_index] = 1'b1;\n                            // 通道加行、再加列、再加base分别保留33位进位，避免三项相加漏进位。\n                            channel_row_sum_work = {1'b0, channel_offset_work[31:0]} +\n                                {1'b0, row_offset_work[kernel_y_work][31:0]};\n                            logical_offset_work = {1'b0, channel_row_sum_work[31:0]} +\n                                {1'b0, tap_source_x[tap_index][31:0]};\n"
    ],
    [
        "                                {1'b0, tap_source_x[tap_index][31:0]};\n                            selected_row_high = row_index_high[kernel_y_work];\n                            selected_offset_high = row_offset_work[kernel_y_work][63:32] != 32'd0;\n",
        "                                {1'b0, tap_source_x[tap_index][31:0]};\n                            selected_row_high = channel_offset_high;\n                            selected_offset_high = row_offset_work[kernel_y_work][63:32] != 32'd0;\n"
    ],
    [
        "                            if (selected_row_high || selected_offset_high ||\n                                logical_offset_work[32] || address_work[32]) begin\n                                tap_range_error = 1'b1;\n",
        "                            if (selected_row_high || selected_offset_high ||\n                                channel_row_sum_work[32] || logical_offset_work[32] || address_work[32]) begin\n                                tap_range_error = 1'b1;\n"
    ]
])
DERIVATION_RULES["src/int8_maxpool_geometry.sv"] = ("src/s2b_maxpool_geometry.sv", MAXPOOL_GEOMETRY_REPLACEMENTS)
DERIVATION_RULES["src/s2a_maxpool_engine.sv"][1].append(["int8_maxpool_geometry u_geometry", "s2b_maxpool_geometry u_geometry"])

# S12只授权组合常量实例、选择及64位偏移；原端口和全部时序逻辑保持。
POOL_FIXED_GEOMETRY_REPLACEMENTS = [['    logic [2:0] query_error_code;\n', '    // 三个冻结POOL层分别使用常量尺寸；未匹配层仍由原首个参数分支拒绝。\n    logic [1:0] geometry_shape_select;\n    integer geometry_tap_index;\n    logic [32:0] fixed_query_output_height [0:2];\n    logic [32:0] fixed_query_output_width [0:2];\n    logic [3:0] fixed_query_tap_count [0:2];\n    logic [8:0] fixed_query_tap_valid_mask [0:2];\n    logic [31:0] fixed_query_tap_address [0:2][0:8];\n    logic [31:0] fixed_query_tap_source_channel [0:2][0:8];\n    logic signed [63:0] fixed_query_tap_source_y [0:2][0:8];\n    logic signed [63:0] fixed_query_tap_source_x [0:2][0:8];\n    logic [2:0] fixed_query_error_code [0:2];\n    logic [2:0] query_error_code;\n'], ["    s2b_maxpool_geometry u_geometry (\n        .input_base_address(input_base_address),\n        .input_channels(input_channels),\n        .input_height(input_height),\n        .input_width(input_width),\n        .kernel_height(32'd2),\n        .kernel_width(32'd2),\n        .stride_y(32'd2),\n        .stride_x(32'd2),\n        .darknet_padding_parameter(32'd1),\n        .input_channel(output_channel),\n        .output_y(output_y),\n        .output_x(output_x),\n        .output_height(query_output_height),\n        .output_width(query_output_width),\n        .tap_count(query_tap_count),\n        .tap_valid_mask(query_tap_valid_mask),\n        .tap_address(query_tap_address),\n        .tap_source_channel(query_tap_source_channel),\n        .tap_source_y(query_tap_source_y),\n        .tap_source_x(query_tap_source_x),\n        .error_code(query_error_code)\n    );", "    s2b_maxpool_geometry u_geometry_l9 (\n        .input_base_address(input_base_address),\n        .input_channels(32'd128),\n        .input_height(32'd104),\n        .input_width(32'd104),\n        .kernel_height(32'd2),\n        .kernel_width(32'd2),\n        .stride_y(32'd2),\n        .stride_x(32'd2),\n        .darknet_padding_parameter(32'd1),\n        .input_channel(output_channel),\n        .output_y(output_y),\n        .output_x(output_x),\n        .output_height(fixed_query_output_height[0]),\n        .output_width(fixed_query_output_width[0]),\n        .tap_count(fixed_query_tap_count[0]),\n        .tap_valid_mask(fixed_query_tap_valid_mask[0]),\n        .tap_address(fixed_query_tap_address[0]),\n        .tap_source_channel(fixed_query_tap_source_channel[0]),\n        .tap_source_y(fixed_query_tap_source_y[0]),\n        .tap_source_x(fixed_query_tap_source_x[0]),\n        .error_code(fixed_query_error_code[0])\n    );\n\n    s2b_maxpool_geometry u_geometry_l17 (\n        .input_base_address(input_base_address),\n        .input_channels(32'd256),\n        .input_height(32'd52),\n        .input_width(32'd52),\n        .kernel_height(32'd2),\n        .kernel_width(32'd2),\n        .stride_y(32'd2),\n        .stride_x(32'd2),\n        .darknet_padding_parameter(32'd1),\n        .input_channel(output_channel),\n        .output_y(output_y),\n        .output_x(output_x),\n        .output_height(fixed_query_output_height[1]),\n        .output_width(fixed_query_output_width[1]),\n        .tap_count(fixed_query_tap_count[1]),\n        .tap_valid_mask(fixed_query_tap_valid_mask[1]),\n        .tap_address(fixed_query_tap_address[1]),\n        .tap_source_channel(fixed_query_tap_source_channel[1]),\n        .tap_source_y(fixed_query_tap_source_y[1]),\n        .tap_source_x(fixed_query_tap_source_x[1]),\n        .error_code(fixed_query_error_code[1])\n    );\n\n    s2b_maxpool_geometry u_geometry_l25 (\n        .input_base_address(input_base_address),\n        .input_channels(32'd512),\n        .input_height(32'd26),\n        .input_width(32'd26),\n        .kernel_height(32'd2),\n        .kernel_width(32'd2),\n        .stride_y(32'd2),\n        .stride_x(32'd2),\n        .darknet_padding_parameter(32'd1),\n        .input_channel(output_channel),\n        .output_y(output_y),\n        .output_x(output_x),\n        .output_height(fixed_query_output_height[2]),\n        .output_width(fixed_query_output_width[2]),\n        .tap_count(fixed_query_tap_count[2]),\n        .tap_valid_mask(fixed_query_tap_valid_mask[2]),\n        .tap_address(fixed_query_tap_address[2]),\n        .tap_source_channel(fixed_query_tap_source_channel[2]),\n        .tap_source_y(fixed_query_tap_source_y[2]),\n        .tap_source_x(fixed_query_tap_source_x[2]),\n        .error_code(fixed_query_error_code[2])\n    );"], ["    always_comb begin\n        query_inputs_valid = 1'b0;", "    always_comb begin\n        geometry_shape_select = 2'd0;\n        case (layer_index)\n            32'd9: geometry_shape_select = 2'd0;\n            32'd17: geometry_shape_select = 2'd1;\n            32'd25: geometry_shape_select = 2'd2;\n            default: geometry_shape_select = 2'd0;\n        endcase\n        query_output_height = fixed_query_output_height[geometry_shape_select];\n        query_output_width = fixed_query_output_width[geometry_shape_select];\n        query_tap_count = fixed_query_tap_count[geometry_shape_select];\n        query_tap_valid_mask = fixed_query_tap_valid_mask[geometry_shape_select];\n        query_error_code = fixed_query_error_code[geometry_shape_select];\n        for (geometry_tap_index = 0; geometry_tap_index < 9; geometry_tap_index = geometry_tap_index + 1) begin\n            query_tap_address[geometry_tap_index] = fixed_query_tap_address[geometry_shape_select][geometry_tap_index];\n            query_tap_source_channel[geometry_tap_index] = fixed_query_tap_source_channel[geometry_shape_select][geometry_tap_index];\n            query_tap_source_y[geometry_tap_index] = fixed_query_tap_source_y[geometry_shape_select][geometry_tap_index];\n            query_tap_source_x[geometry_tap_index] = fixed_query_tap_source_x[geometry_shape_select][geometry_tap_index];\n        end\n        query_inputs_valid = 1'b0;"], ["        output_offset_work =\n            ((({32'd0, output_channel} * {32'd0, output_height}) +\n              {32'd0, output_y}) * {32'd0, output_width}) +\n            {32'd0, output_x};", "        // 原前置字段校验只接受三个冻结形状；坐标仍保留完整U32及64位偏移。\n        output_offset_work = 64'd0;\n        case (layer_index)\n            32'd9: output_offset_work = {32'd0, output_channel} * 64'd2704 +\n                ({32'd0, output_y} * 64'd52) + {32'd0, output_x};\n            32'd17: output_offset_work = {32'd0, output_channel} * 64'd676 +\n                ({32'd0, output_y} * 64'd26) + {32'd0, output_x};\n            32'd25: output_offset_work = {32'd0, output_channel} * 64'd169 +\n                ({32'd0, output_y} * 64'd13) + {32'd0, output_x};\n            default: output_offset_work = 64'd0;\n        endcase"]]
DERIVATION_RULES["src/s2a_maxpool_engine.sv"][1].extend(POOL_FIXED_GEOMETRY_REPLACEMENTS)


# S12固定21完整descriptor；所有原guard保留，私有非匹配域不能视为通用全域。
S12_CONV_FROZEN_FIELDS = ((0, 3, 416, 416, 32, 208, 208, 3, 3, 2, 2, 1, 1, 1, 1), (1, 32, 208, 208, 64, 104, 104, 3, 3, 2, 2, 1, 1, 1, 1), (2, 64, 104, 104, 64, 104, 104, 3, 3, 1, 1, 1, 1, 1, 1), (4, 32, 104, 104, 32, 104, 104, 3, 3, 1, 1, 1, 1, 1, 1), (5, 32, 104, 104, 32, 104, 104, 3, 3, 1, 1, 1, 1, 1, 1), (7, 64, 104, 104, 64, 104, 104, 1, 1, 1, 1, 0, 0, 0, 0), (10, 128, 52, 52, 128, 52, 52, 3, 3, 1, 1, 1, 1, 1, 1), (12, 64, 52, 52, 64, 52, 52, 3, 3, 1, 1, 1, 1, 1, 1), (13, 64, 52, 52, 64, 52, 52, 3, 3, 1, 1, 1, 1, 1, 1), (15, 128, 52, 52, 128, 52, 52, 1, 1, 1, 1, 0, 0, 0, 0), (18, 256, 26, 26, 256, 26, 26, 3, 3, 1, 1, 1, 1, 1, 1), (20, 128, 26, 26, 128, 26, 26, 3, 3, 1, 1, 1, 1, 1, 1), (21, 128, 26, 26, 128, 26, 26, 3, 3, 1, 1, 1, 1, 1, 1), (23, 256, 26, 26, 256, 26, 26, 1, 1, 1, 1, 0, 0, 0, 0), (26, 512, 13, 13, 512, 13, 13, 3, 3, 1, 1, 1, 1, 1, 1), (27, 512, 13, 13, 256, 13, 13, 1, 1, 1, 1, 0, 0, 0, 0), (28, 256, 13, 13, 512, 13, 13, 3, 3, 1, 1, 1, 1, 1, 1), (29, 512, 13, 13, 30, 13, 13, 1, 1, 1, 1, 0, 0, 0, 0), (32, 256, 13, 13, 128, 13, 13, 1, 1, 1, 1, 0, 0, 0, 0), (35, 384, 26, 26, 256, 26, 26, 3, 3, 1, 1, 1, 1, 1, 1), (36, 256, 26, 26, 30, 26, 26, 1, 1, 1, 1, 0, 0, 0, 0))


def _s12_expand_conv_tables(template: str) -> str:
    """由独立固定字段生成精确允许文本，不能由被审源或自报SHA修改常量。"""
    descriptors, tiles, full = [], [], []
    for fields in S12_CONV_FROZEN_FIELDS:
        layer, c, h, w, oc, oh, ow, kh, kw, sy, sx, pl, pr, pt, pb = fields
        key = "".join(f"{value:08X}" for value in fields)
        descriptors.append(f"                480'h{key}: frozen_conv_descriptor_lookup = {{1'b1, 26'd{c*kh}, 26'd{c*kh*kw}, 45'd{oc*c*kh*kw}}};")
        for ey in range(9):
            for ex in range(9):
                ph = (((ey-1)&0xffffffff)*sy+kh)&0xffffffff
                pw = (((ex-1)&0xffffffff)*sx+kw)&0xffffffff
                tiles.append(f"                40'h{layer:08X}{ey:X}{ex:X}: frozen_conv_tile_lookup = {{32'd{ph}, 32'd{pw}, 32'd{(ph*pw*c)&0xffffffff}}};")
        dy = 0 if oh == 0 else min(oh,8)-1
        dx = 0 if ow == 0 else min(ow,8)-1
        fh = (dy*(sy&0xffff)+(kh&0x1fff))&0x7ffff
        fw = (dx*(sx&0xffff)+(kw&0x1fff))&0x7ffff
        plane = (fh&0xffff)*(fw&0xffff)
        count = (plane&0xffff)*(c&0x1fff)
        full.append(f"                32'd{layer}: frozen_full_tile_lookup = {{19'd{fh}, 19'd{fw}, 32'd{plane}, 29'd{count}}};")
    return template.replace("@S12_DESCRIPTOR_CASES@", "\n".join(descriptors)).replace("@S12_TILE_CASES@", "\n".join(tiles)).replace("@S12_FULL_CASES@", "\n".join(full))

DERIVATION_RULES['src/s2a_conv_tile_engine.sv'][1].extend([
    ['// S2A-T66：以 8×8 空间 tile 和 8 个输出通道并行完成一个卷积层。\nmodule s2b_conv_tile_engine (\n    input  logic        clk,\n    input  logic        hard_reset,\n    input  logic        abort,\n', "// S2A-T66：以 8×8 空间 tile 和 8 个输出通道并行完成一个卷积层。\nmodule s2b_conv_tile_engine #(\n    // 仅冻结network实例启用；默认保留原通用参数域和错误判据。\n    parameter bit FROZEN_CONV_DESCRIPTOR = 1'b0\n) (\n    input  logic        clk,\n    input  logic        hard_reset,\n    input  logic        abort,\n"],
    ['    logic [63:0] requant_product;\n    logic [63:0] requant_rounding_add;\n    logic [63:0] requant_rounded_magnitude;\n    logic signed [63:0] requant_signed_value;\n    logic signed [7:0] requantized_value;\n\n    logic [31:0] output_global_y;\n', '    logic [63:0] requant_product;\n    logic [63:0] requant_rounding_add;\n    logic [63:0] requant_rounded_magnitude;\n    logic signed [7:0] requantized_value;\n\n    logic [31:0] output_global_y;\n'],
    ["    integer comb_lane;\n    integer seq_lane;\n\n    always_comb begin\n        // 首分支已逐因子拒绝零；长度分支只消费正数乘积。\n        // 前两因子精确64位，高32位非零必超UINT32；否则再精确乘第三因子。\n        input_element_plane = {32'd0, input_channels_latched} * {32'd0, input_height_latched};\n", _s12_expand_conv_tables("    integer comb_lane;\n    integer seq_lane;\n\n    // 完整480位冻结字段键；私有模式不允许仅layer索引绕过其他参数。\n    function automatic logic [97:0] frozen_conv_descriptor_lookup(input logic [479:0] descriptor_key);\n        begin\n            frozen_conv_descriptor_lookup = 98'd0;\n            case (descriptor_key)\n@S12_DESCRIPTOR_CASES@\n                default: frozen_conv_descriptor_lookup = 98'd0;\n            endcase\n        end\n    endfunction\n\n    // extent为0时保留原减1的U32回绕；其余值使用精确常系数移位加法。\n    function automatic logic [31:0] generic_tile_patch_axis(\n        input logic [31:0] extent, input logic [31:0] stride, input logic [31:0] kernel_size);\n        begin\n            case (extent)\n                32'd0: generic_tile_patch_axis = kernel_size - stride;\n                32'd1: generic_tile_patch_axis = kernel_size;\n                32'd2: generic_tile_patch_axis = stride + kernel_size;\n                32'd3: generic_tile_patch_axis = (stride << 32'd1) + kernel_size;\n                32'd4: generic_tile_patch_axis = (stride << 32'd1) + stride + kernel_size;\n                32'd5: generic_tile_patch_axis = (stride << 32'd2) + kernel_size;\n                32'd6: generic_tile_patch_axis = (stride << 32'd2) + stride + kernel_size;\n                32'd7: generic_tile_patch_axis = (stride << 32'd2) + (stride << 32'd1) + kernel_size;\n                32'd8: generic_tile_patch_axis = (stride << 32'd2) + (stride << 32'd1) + stride + kernel_size;\n                default: generic_tile_patch_axis = 32'd0;\n            endcase\n        end\n    endfunction\n\n    // 三个字段均按原ST_TILE_PREP赋值的U32模域预计算，无额外寄存器或周期。\n    function automatic logic [95:0] frozen_conv_tile_lookup(input logic [39:0] tile_key);\n        begin\n            frozen_conv_tile_lookup = 96'd0;\n            case (tile_key)\n@S12_TILE_CASES@\n                default: frozen_conv_tile_lookup = 96'd0;\n            endcase\n        end\n    endfunction\n\n    // 必须由完整descriptor命中保护；仅替换稳定算术，所有原比较仍保留。\n    function automatic logic [98:0] frozen_full_tile_lookup(input logic [31:0] layer_key);\n        begin\n            frozen_full_tile_lookup = 99'd0;\n            case (layer_key)\n@S12_FULL_CASES@\n                default: frozen_full_tile_lookup = 99'd0;\n            endcase\n        end\n    endfunction\n\n    logic [98:0] frozen_full_tile;\n\n    logic [97:0] frozen_conv_descriptor;\n    logic [95:0] frozen_conv_tile;\n    logic [31:0] tile_prep_extent_y;\n    logic [31:0] tile_prep_extent_x;\n    logic [31:0] tile_prep_patch_height;\n    logic [31:0] tile_prep_patch_width;\n    logic [31:0] tile_prep_patch_bytes;\n\n    always_comb begin\n        frozen_conv_descriptor = 98'd0;\n        frozen_conv_tile = 96'd0;\n        frozen_full_tile = 99'd0;\n        if (FROZEN_CONV_DESCRIPTOR) begin\n            frozen_conv_descriptor = frozen_conv_descriptor_lookup({layer_index_latched, input_channels_latched, input_height_latched, input_width_latched, output_channels_latched, output_height_latched, output_width_latched, kernel_height_latched, kernel_width_latched, stride_y_latched, stride_x_latched, pad_left_latched, pad_right_latched, pad_top_latched, pad_bottom_latched});\n            if (frozen_conv_descriptor[97]) begin\n                frozen_full_tile = frozen_full_tile_lookup(layer_index_latched);\n            end\n        end\n        tile_prep_extent_y = (output_height_latched - tile_start_y >= TILE_EDGE) ?\n                             TILE_EDGE : output_height_latched - tile_start_y;\n        tile_prep_extent_x = (output_width_latched - tile_start_x >= TILE_EDGE) ?\n                             TILE_EDGE : output_width_latched - tile_start_x;\n        tile_prep_patch_height = 32'd0;\n        tile_prep_patch_width = 32'd0;\n        tile_prep_patch_bytes = 32'd0;\n        if (FROZEN_CONV_DESCRIPTOR) begin\n            if (frozen_conv_descriptor[97]) begin\n                frozen_conv_tile = frozen_conv_tile_lookup({layer_index_latched, tile_prep_extent_y[3:0], tile_prep_extent_x[3:0]});\n                tile_prep_patch_height = frozen_conv_tile[95:64];\n                tile_prep_patch_width = frozen_conv_tile[63:32];\n                tile_prep_patch_bytes = frozen_conv_tile[31:0];\n            end\n        end else begin\n            tile_prep_patch_height = generic_tile_patch_axis(tile_prep_extent_y, stride_y_latched, kernel_height_latched);\n            tile_prep_patch_width = generic_tile_patch_axis(tile_prep_extent_x, stride_x_latched, kernel_width_latched);\n            tile_prep_patch_bytes = tile_prep_patch_height * tile_prep_patch_width * input_channels_latched;\n        end\n\n        // 首分支已逐因子拒绝零；长度分支只消费正数乘积。\n        // 前两因子精确64位，高32位非零必超UINT32；否则再精确乘第三因子。\n        input_element_plane = {32'd0, input_channels_latched} * {32'd0, input_height_latched};\n")],
    ["        output_elements_wide = {64'd0, output_element_product};\n\n        // 正C/KH/KW的R<=4608蕴含每个因子及C*KH均<=4608；低位截断另有拒绝保护。\n        reduction_plane_narrow = {13'd0, input_channels_latched[12:0]} *\n                                 {13'd0, kernel_height_latched[12:0]};\n        reduction_count_narrow = {13'd0, reduction_plane_narrow[12:0]} *\n                                 {13'd0, kernel_width_latched[12:0]};\n        reduction_count_bad = (input_channels_latched > 32'd4608) ||\n            (kernel_height_latched > 32'd4608) || (kernel_width_latched > 32'd4608) ||\n            (reduction_plane_narrow > 26'd4608) || (reduction_count_narrow > 26'd4608);\n        reduction_count_wide = {102'd0, reduction_count_narrow};\n        // 长度分支已保证R<=4608，故OC32*R13的45位结果精确；不提前消费MQ限制。\n        expected_weight_bytes_narrow = {13'd0, output_channels_latched} *\n                                       {32'd0, reduction_count_narrow[12:0]};\n        expected_weight_bytes_wide = {83'd0, expected_weight_bytes_narrow};\n        input_end_wide = {96'd0, input_base_latched} + {96'd0, input_length_latched};\n        output_end_wide = {96'd0, output_base_latched} + {96'd0, output_length_latched};\n        weight_package_end_wide = {96'd0, weight_package_base_latched} +\n", "        output_elements_wide = {64'd0, output_element_product};\n\n        // 正C/KH/KW的R<=4608蕴含每个因子及C*KH均<=4608；低位截断另有拒绝保护。\n        if (FROZEN_CONV_DESCRIPTOR) begin\n            reduction_plane_narrow = frozen_conv_descriptor[96:71];\n            reduction_count_narrow = frozen_conv_descriptor[70:45];\n            reduction_count_bad = !frozen_conv_descriptor[97];\n            reduction_count_wide = {102'd0, reduction_count_narrow};\n            expected_weight_bytes_narrow = frozen_conv_descriptor[44:0];\n            expected_weight_bytes_wide = {83'd0, expected_weight_bytes_narrow};\n        end else begin\n            reduction_plane_narrow = {13'd0, input_channels_latched[12:0]} *\n                                     {13'd0, kernel_height_latched[12:0]};\n            reduction_count_narrow = {13'd0, reduction_plane_narrow[12:0]} *\n                                     {13'd0, kernel_width_latched[12:0]};\n            reduction_count_bad = (input_channels_latched > 32'd4608) ||\n                (kernel_height_latched > 32'd4608) || (kernel_width_latched > 32'd4608) ||\n                (reduction_plane_narrow > 26'd4608) || (reduction_count_narrow > 26'd4608);\n            reduction_count_wide = {102'd0, reduction_count_narrow};\n            // 长度分支已保证R<=4608，故OC32*R13的45位结果精确；不提前消费MQ限制。\n            expected_weight_bytes_narrow = {13'd0, output_channels_latched} *\n                                           {32'd0, reduction_count_narrow[12:0]};\n            expected_weight_bytes_wide = {83'd0, expected_weight_bytes_narrow};\n        end\n        input_end_wide = {96'd0, input_base_latched} + {96'd0, input_length_latched};\n        output_end_wide = {96'd0, output_base_latched} + {96'd0, output_length_latched};\n        weight_package_end_wide = {96'd0, weight_package_base_latched} +\n"],
    ["            (output_height_latched < TILE_EDGE ? output_height_latched[2:0] - 3'd1 : 3'd7);\n        full_tile_patch_delta_x = output_width_latched == 32'd0 ? 3'd0 :\n            (output_width_latched < TILE_EDGE ? output_width_latched[2:0] - 3'd1 : 3'd7);\n        full_tile_patch_height_narrow =\n            ({16'd0, full_tile_patch_delta_y} * {3'd0, stride_y_latched[15:0]}) +\n            {6'd0, kernel_height_latched[12:0]};\n        full_tile_patch_width_narrow =\n            ({16'd0, full_tile_patch_delta_x} * {3'd0, stride_x_latched[15:0]}) +\n            {6'd0, kernel_width_latched[12:0]};\n        full_tile_patch_height_bad =\n            ((full_tile_patch_delta_y != 3'd0) && (stride_y_latched[31:16] != 16'd0)) ||\n            (full_tile_patch_height_narrow[18:16] != 3'd0) ||\n", "            (output_height_latched < TILE_EDGE ? output_height_latched[2:0] - 3'd1 : 3'd7);\n        full_tile_patch_delta_x = output_width_latched == 32'd0 ? 3'd0 :\n            (output_width_latched < TILE_EDGE ? output_width_latched[2:0] - 3'd1 : 3'd7);\n        if (FROZEN_CONV_DESCRIPTOR) begin\n            full_tile_patch_height_narrow = frozen_full_tile[98:80];\n            full_tile_patch_width_narrow = frozen_full_tile[79:61];\n        end else begin\n            full_tile_patch_height_narrow =\n                ({16'd0, full_tile_patch_delta_y} * {3'd0, stride_y_latched[15:0]}) +\n                {6'd0, kernel_height_latched[12:0]};\n            full_tile_patch_width_narrow =\n                ({16'd0, full_tile_patch_delta_x} * {3'd0, stride_x_latched[15:0]}) +\n                {6'd0, kernel_width_latched[12:0]};\n        end\n        full_tile_patch_height_bad =\n            ((full_tile_patch_delta_y != 3'd0) && (stride_y_latched[31:16] != 16'd0)) ||\n            (full_tile_patch_height_narrow[18:16] != 3'd0) ||\n"],
    ["            ((full_tile_patch_delta_x != 3'd0) && (stride_x_latched[31:16] != 16'd0)) ||\n            (full_tile_patch_width_narrow[18:16] != 3'd0) ||\n            (full_tile_patch_width_narrow[15:0] > 16'd51200);\n        full_tile_patch_plane_narrow =\n            {16'd0, full_tile_patch_height_narrow[15:0]} *\n            {16'd0, full_tile_patch_width_narrow[15:0]};\n        full_tile_patch_bytes_narrow =\n            {13'd0, full_tile_patch_plane_narrow[15:0]} *\n            {16'd0, input_channels_latched[12:0]};\n        full_tile_patch_bad = full_tile_patch_height_bad || full_tile_patch_width_bad ||\n            (full_tile_patch_plane_narrow[31:16] != 16'd0) ||\n            (full_tile_patch_bytes_narrow > 29'd51200);\n", "            ((full_tile_patch_delta_x != 3'd0) && (stride_x_latched[31:16] != 16'd0)) ||\n            (full_tile_patch_width_narrow[18:16] != 3'd0) ||\n            (full_tile_patch_width_narrow[15:0] > 16'd51200);\n        if (FROZEN_CONV_DESCRIPTOR) begin\n            full_tile_patch_plane_narrow = frozen_full_tile[60:29];\n            full_tile_patch_bytes_narrow = frozen_full_tile[28:0];\n        end else begin\n            full_tile_patch_plane_narrow =\n                {16'd0, full_tile_patch_height_narrow[15:0]} *\n                {16'd0, full_tile_patch_width_narrow[15:0]};\n            full_tile_patch_bytes_narrow =\n                {13'd0, full_tile_patch_plane_narrow[15:0]} *\n                {16'd0, input_channels_latched[12:0]};\n        end\n        full_tile_patch_bad = full_tile_patch_height_bad || full_tile_patch_width_bad ||\n            (full_tile_patch_plane_narrow[31:16] != 16'd0) ||\n            (full_tile_patch_bytes_narrow > 29'd51200);\n"],
    ["            compute_read_reduction_index = 32'd0;\n            compute_read_enable = 1'b1;\n        end else if (state == ST_COMPUTE) begin\n            if ((compute_reduction_index + 32'd1 < reduction_count_latched) &&\n                !compute_bad_argument && !compute_overflow) begin\n                compute_read_point_y = compute_point_scan_y;\n                compute_read_point_x = compute_point_scan_x;\n                compute_read_input_channel = compute_next_input_channel;\n                compute_read_kernel_y = compute_next_kernel_y;\n                compute_read_kernel_x = compute_next_kernel_x;\n                compute_read_reduction_index = compute_next_reduction_index;\n                compute_read_enable = 1'b1;\n            end\n        end\n        if ((compute_kernel_area != 32'd0) && (tile_width != 32'd0)) begin\n", "            compute_read_reduction_index = 32'd0;\n            compute_read_enable = 1'b1;\n        end else if (state == ST_COMPUTE) begin\n            // 下一tap坐标与MAC错误解耦；错误仍禁止实际特征及权重读取。\n            if (compute_reduction_index + 32'd1 < reduction_count_latched) begin\n                compute_read_point_y = compute_point_scan_y;\n                compute_read_point_x = compute_point_scan_x;\n                compute_read_input_channel = compute_next_input_channel;\n                compute_read_kernel_y = compute_next_kernel_y;\n                compute_read_kernel_x = compute_next_kernel_x;\n                compute_read_reduction_index = compute_next_reduction_index;\n                compute_read_enable = !compute_bad_argument && !compute_overflow;\n            end\n        end\n        if ((compute_kernel_area != 32'd0) && (tile_width != 32'd0)) begin\n"],
    ["        requant_product = 64'd0;\n        requant_rounding_add = 64'd0;\n        requant_rounded_magnitude = 64'd0;\n        requant_signed_value = 64'sd0;\n        requantized_value = 8'sd0;\n        if ((requant_lane_index < LANE_COUNT) &&\n            (requant_lane_index < group_lane_count)) begin\n", "        requant_product = 64'd0;\n        requant_rounding_add = 64'd0;\n        requant_rounded_magnitude = 64'd0;\n        requantized_value = 8'sd0;\n        if ((requant_lane_index < LANE_COUNT) &&\n            (requant_lane_index < group_lane_count)) begin\n"],
    ["            end\n            requant_rounded_magnitude =\n                (requant_product + requant_rounding_add) >> requant_q_shift;\n            if (requant_accumulator[31]) begin\n                requant_signed_value =\n                    -$signed({1'b0, requant_rounded_magnitude});\n            end else begin\n                requant_signed_value =\n                    $signed({1'b0, requant_rounded_magnitude});\n            end\n            if (requant_signed_value > 64'sd127) begin\n                requantized_value = 8'sd127;\n            end else if (requant_signed_value < -64'sd127) begin\n                requantized_value = -8'sd127;\n            end else begin\n                requantized_value = requant_signed_value[7:0];\n            end\n        end\n\n", "            end\n            requant_rounded_magnitude =\n                (requant_product + requant_rounding_add) >> requant_q_shift;\n            if (|requant_rounded_magnitude[63:7]) begin\n                requantized_value = requant_accumulator[31] ? -8'sd127 : 8'sd127;\n            end else if (requant_accumulator[31]) begin\n                requantized_value = -$signed(requant_rounded_magnitude[7:0]);\n            end else begin\n                requantized_value = $signed(requant_rounded_magnitude[7:0]);\n            end\n        end\n\n"],
    ["                                   TILE_EDGE : output_height_latched - tile_start_y;\n                    tile_width <= (output_width_latched - tile_start_x >= TILE_EDGE) ?\n                                  TILE_EDGE : output_width_latched - tile_start_x;\n                    patch_height <=\n                        (((output_height_latched - tile_start_y >= TILE_EDGE) ? TILE_EDGE :\n                          output_height_latched - tile_start_y) - 1) * stride_y_latched +\n                        kernel_height_latched;\n                    patch_width <=\n                        (((output_width_latched - tile_start_x >= TILE_EDGE) ? TILE_EDGE :\n                          output_width_latched - tile_start_x) - 1) * stride_x_latched +\n                        kernel_width_latched;\n                    patch_byte_count <=\n                        ((((output_height_latched - tile_start_y >= TILE_EDGE) ? TILE_EDGE :\n                           output_height_latched - tile_start_y) - 1) * stride_y_latched +\n                         kernel_height_latched) *\n                        ((((output_width_latched - tile_start_x >= TILE_EDGE) ? TILE_EDGE :\n                           output_width_latched - tile_start_x) - 1) * stride_x_latched +\n                         kernel_width_latched) * input_channels_latched;\n                    feature_scan_channel <= 32'd0;\n                    feature_scan_y <= 32'd0;\n                    feature_scan_x <= 32'd0;\n", "                                   TILE_EDGE : output_height_latched - tile_start_y;\n                    tile_width <= (output_width_latched - tile_start_x >= TILE_EDGE) ?\n                                  TILE_EDGE : output_width_latched - tile_start_x;\n                    patch_height <= tile_prep_patch_height;\n                    patch_width <= tile_prep_patch_width;\n                    patch_byte_count <= tile_prep_patch_bytes;\n                    feature_scan_channel <= 32'd0;\n                    feature_scan_y <= 32'd0;\n                    feature_scan_x <= 32'd0;\n"],
])
DERIVATION_RULES['src/int8_route_query.sv'][1].extend([
    ['// G0 tiny416 route 单输出元素：group 通道映射、NCHW 地址与 scale 重标定。\nmodule s2b_route_query (\n    input  logic [31:0] source_count,\n    input  logic [31:0] groups,\n    input  logic [31:0] group_id,\n', "// G0 tiny416 route 单输出元素：group 通道映射、NCHW 地址与 scale 重标定。\nmodule s2b_route_query #(\n    // 仅冻结network实例启用；默认保持原任意U32组合查询。\n    parameter bit FROZEN_ROUTE_SHAPES = 1'b0\n) (\n    input  logic [31:0] source_count,\n    input  logic [31:0] groups,\n    input  logic [31:0] group_id,\n"],
    ["    logic [31:0] selected_source_index;\n    logic [31:0] selected_source_channel;\n\n    always_comb begin\n        // 组合默认值保证非法输入无副作用，也避免推断锁存器。\n        output_channels = 32'd0;\n", "    logic [31:0] selected_source_index;\n    logic [31:0] selected_source_channel;\n\n    // 完整96位tuple匹配，避免低位别名；固定值分别为C乘H与C乘H乘W。\n    function automatic logic [128:0] frozen_shape_lookup(input logic [95:0] shape_key);\n        begin\n            frozen_shape_lookup = 129'd0;\n            case (shape_key)\n                96'h000000200000006800000068: frozen_shape_lookup = {1'b1, 64'd3328, 64'd346112};\n                96'h000000400000003400000034: frozen_shape_lookup = {1'b1, 64'd3328, 64'd173056};\n                96'h000000400000006800000068: frozen_shape_lookup = {1'b1, 64'd6656, 64'd692224};\n                96'h000000800000001A0000001A: frozen_shape_lookup = {1'b1, 64'd3328, 64'd86528};\n                96'h000000800000003400000034: frozen_shape_lookup = {1'b1, 64'd6656, 64'd346112};\n                96'h000001000000000D0000000D: frozen_shape_lookup = {1'b1, 64'd3328, 64'd43264};\n                96'h000001000000001A0000001A: frozen_shape_lookup = {1'b1, 64'd6656, 64'd173056};\n                default: frozen_shape_lookup = 129'd0;\n            endcase\n        end\n    endfunction\n\n    logic [128:0] source0_frozen_shape;\n    logic [128:0] source1_frozen_shape;\n\n    always_comb begin\n        // 组合默认值保证非法输入无副作用，也避免推断锁存器。\n        output_channels = 32'd0;\n"],
    ["\n        bad_argument = 1'b0;\n        bad_range = 1'b0;\n        source0_shape_bytes = 64'd0;\n        source1_shape_bytes = 64'd0;\n        source0_plane_elements = 64'd0;\n", "\n        bad_argument = 1'b0;\n        bad_range = 1'b0;\n        source0_frozen_shape = 129'd0;\n        source1_frozen_shape = 129'd0;\n        source0_shape_bytes = 64'd0;\n        source1_shape_bytes = 64'd0;\n        source0_plane_elements = 64'd0;\n"],
    ["            bad_argument = 1'b1;\n        end\n\n        source0_plane_elements = {32'd0, source0_channels} *\n                                 {32'd0, source0_height};\n        if (source0_plane_elements > 64'h0000_0000_FFFF_FFFF) begin\n            bad_range = 1'b1;\n        end else begin\n            source0_shape_bytes = source0_plane_elements *\n                                  {32'd0, source0_width};\n            if (source0_shape_bytes > 64'h0000_0000_FFFF_FFFF) begin\n                bad_range = 1'b1;\n            end\n        end\n        source0_object_end = {32'd0, source0_base_address} +\n", "            bad_argument = 1'b1;\n        end\n\n        if (FROZEN_ROUTE_SHAPES) begin\n            source0_frozen_shape = frozen_shape_lookup({source0_channels, source0_height, source0_width});\n            source0_plane_elements = source0_frozen_shape[127:64];\n            source0_shape_bytes = source0_frozen_shape[63:0];\n            if (!source0_frozen_shape[128]) begin\n                // 私有非冻结tuple拒绝；公开backend可达性由独立G0/G1证明。\n                bad_argument = 1'b1;\n            end\n        end else begin\n            source0_plane_elements = {32'd0, source0_channels} *\n                                     {32'd0, source0_height};\n            if (source0_plane_elements > 64'h0000_0000_FFFF_FFFF) begin\n                bad_range = 1'b1;\n            end else begin\n                source0_shape_bytes = source0_plane_elements *\n                                      {32'd0, source0_width};\n                if (source0_shape_bytes > 64'h0000_0000_FFFF_FFFF) begin\n                    bad_range = 1'b1;\n                end\n            end\n        end\n        source0_object_end = {32'd0, source0_base_address} +\n"],
    ["        end\n\n        if (source_count == 32'd2) begin\n            source1_plane_elements = {32'd0, source1_channels} *\n                                     {32'd0, source1_height};\n            if (source1_plane_elements > 64'h0000_0000_FFFF_FFFF) begin\n                bad_range = 1'b1;\n            end else begin\n                source1_shape_bytes = source1_plane_elements *\n                                      {32'd0, source1_width};\n                if (source1_shape_bytes > 64'h0000_0000_FFFF_FFFF) begin\n                    bad_range = 1'b1;\n                end\n            end\n            source1_object_end = {32'd0, source1_base_address} +\n", "        end\n\n        if (source_count == 32'd2) begin\n            if (FROZEN_ROUTE_SHAPES) begin\n                source1_frozen_shape = frozen_shape_lookup({source1_channels, source1_height, source1_width});\n                source1_plane_elements = source1_frozen_shape[127:64];\n                source1_shape_bytes = source1_frozen_shape[63:0];\n                if (!source1_frozen_shape[128]) begin\n                    // 私有非冻结tuple拒绝；公开backend可达性由独立G0/G1证明。\n                    bad_argument = 1'b1;\n                end\n            end else begin\n                source1_plane_elements = {32'd0, source1_channels} *\n                                         {32'd0, source1_height};\n                if (source1_plane_elements > 64'h0000_0000_FFFF_FFFF) begin\n                    bad_range = 1'b1;\n                end else begin\n                    source1_shape_bytes = source1_plane_elements *\n                                          {32'd0, source1_width};\n                    if (source1_shape_bytes > 64'h0000_0000_FFFF_FFFF) begin\n                        bad_range = 1'b1;\n                    end\n                end\n            end\n            source1_object_end = {32'd0, source1_base_address} +\n"],
])
DERIVATION_RULES['src/s2a_route_engine.sv'][1].extend([
    ['// S2A-T15：tiny416 route 单输出元素 INT8 memory datapath。\nmodule s2b_route_engine (\n    input  logic        clk,\n    input  logic        hard_reset,\n    input  logic        abort,\n', "// S2A-T15：tiny416 route 单输出元素 INT8 memory datapath。\nmodule s2b_route_engine #(\n    // 私有参数仅从冻结network实例透传；默认保留通用U32域。\n    parameter bit FROZEN_ROUTE_SHAPES = 1'b0\n) (\n    input  logic        clk,\n    input  logic        hard_reset,\n    input  logic        abort,\n"],
    ['    logic [31:0] selected_byte_shift;\n    logic [2:0] mapped_response_error;\n\n    s2b_route_query u_query (\n        .source_count(source_count_latched),\n        .groups(groups_latched),\n        .group_id(group_id_latched),\n', '    logic [31:0] selected_byte_shift;\n    logic [2:0] mapped_response_error;\n\n    s2b_route_query #(.FROZEN_ROUTE_SHAPES(FROZEN_ROUTE_SHAPES)) u_query (\n        .source_count(source_count_latched),\n        .groups(groups_latched),\n        .group_id(group_id_latched),\n'],
])
DERIVATION_RULES['src/s2a_network_backend.sv'][1].extend([
    ['        end\n    end\n\n    s2b_conv_tile_engine u_conv_engine (\n        .clk(clk), .hard_reset(hard_reset), .abort(abort),\n        .buffer_owner_pl(buffer_owner_pl),\n        .start_valid(conv_start_valid), .start_ready(conv_start_ready),\n', "        end\n    end\n\n    // 私有稳定descriptor模式只绑定冻结ROM的CONV派发。\n    s2b_conv_tile_engine #(.FROZEN_CONV_DESCRIPTOR(1'b1)) u_conv_engine (\n        .clk(clk), .hard_reset(hard_reset), .abort(abort),\n        .buffer_owner_pl(buffer_owner_pl),\n        .start_valid(conv_start_valid), .start_ready(conv_start_ready),\n"],
    ["        .result_error_code(maxpool_result_error)\n    );\n\n    s2b_route_engine u_route_engine (\n        .clk(clk), .hard_reset(hard_reset), .abort(abort),\n        .start_valid(route_start_valid), .start_ready(route_start_ready),\n        .source_count({30'd0, current_input_count}),\n", "        .result_error_code(maxpool_result_error)\n    );\n\n    // 冻结ROM所有ROUTE source tuple已完整绑定，CSR不提供shape覆盖。\n    s2b_route_engine #(.FROZEN_ROUTE_SHAPES(1'b1)) u_route_engine (\n        .clk(clk), .hard_reset(hard_reset), .abort(abort),\n        .start_valid(route_start_valid), .start_ready(route_start_ready),\n        .source_count({30'd0, current_input_count}),\n"],
])

def sha256(path: Path) -> str:
    """返回实际文件字节的哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_file(path: Path) -> Path:
    """逐级核对精确字面名称，拒绝符号链接与大小写改写。"""
    if not path.is_absolute():
        raise ValueError(f"要求绝对文件路径：{path}")
    current = Path(path.anchor)
    for part in path.parts[1:]:
        if part not in [item.name for item in current.iterdir()]:
            raise ValueError(f"精确路径不存在：{current / part}")
        current = current / part
        info = current.lstat()
        if current.is_symlink() or (getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)):
            raise ValueError(f"拒绝链接路径：{current}")
    if not current.is_file():
        raise ValueError(f"目标不是文件：{current}")
    return current


def relative_file(root: Path, value: str) -> Path:
    """只接受仓库内无转义的已声明相对文件。"""
    pure = PurePosixPath(value)
    if not value or "\\" in value or pure.is_absolute() or ".." in pure.parts:
        raise ValueError(f"仓库相对路径非法：{value}")
    return exact_file(root / value)


S13_TILE_ORIGIN_REPLACEMENTS = [
    ["    logic [31:0] tile_start_y;\n    logic [31:0] tile_start_x;\n", "    logic [31:0] tile_start_y;\n    logic [31:0] tile_start_x;\n    // 现有PRE拍登记完整模64坐标原点；SCAN不增加周期或缩减signed域。\n    logic signed [63:0] tile_origin_y;\n    logic signed [63:0] tile_origin_x;\n"],
    ["            feature_input_y =\n                $signed({32'd0, tile_start_y} * {32'd0, stride_y_latched}) +\n                $signed({32'd0, feature_scan_y}) - $signed({32'd0, pad_top_latched});\n            feature_input_x =\n                $signed({32'd0, tile_start_x} * {32'd0, stride_x_latched}) +\n                $signed({32'd0, feature_scan_x}) - $signed({32'd0, pad_left_latched});\n", "            feature_input_y =\n                tile_origin_y + $signed({32'd0, feature_scan_y});\n            feature_input_x =\n                tile_origin_x + $signed({32'd0, feature_scan_x});\n"],
    ["            tile_start_y <= 32'd0;\n            tile_start_x <= 32'd0;\n            tile_height <= 32'd0;\n", "            tile_start_y <= 32'd0;\n            tile_start_x <= 32'd0;\n            tile_origin_y <= 64'sd0;\n            tile_origin_x <= 64'sd0;\n            tile_height <= 32'd0;\n"],
    ["        end else if (abort) begin\n            state <= ST_IDLE;\n", "        end else if (abort) begin\n            state <= ST_IDLE;\n            tile_origin_y <= 64'sd0;\n            tile_origin_x <= 64'sd0;\n"],
    ["                        tile_start_y <= 32'd0;\n                        tile_start_x <= 32'd0;\n", "                        tile_start_y <= 32'd0;\n                        tile_start_x <= 32'd0;\n                        tile_origin_y <= 64'sd0;\n                        tile_origin_x <= 64'sd0;\n"],
    ["                ST_TILE_PREP: begin\n", "                ST_TILE_PREP: begin\n                    // 乘积、减法均按原64位二补码；随后SCAN加法仍在同一模域。\n                    tile_origin_y <=\n                        $signed({32'd0, tile_start_y} * {32'd0, stride_y_latched}) -\n                        $signed({32'd0, pad_top_latched});\n                    tile_origin_x <=\n                        $signed({32'd0, tile_start_x} * {32'd0, stride_x_latched}) -\n                        $signed({32'd0, pad_left_latched});\n"],
]
DERIVATION_RULES["src/s2a_conv_tile_engine.sv"][1].extend(S13_TILE_ORIGIN_REPLACEMENTS)


def require(condition: bool, message: str) -> None:
    """条件不满足时保留失败原因。"""
    if not condition:
        raise ValueError(message)


def read_json(path: Path) -> dict:
    """重复 JSON 键会隐藏绑定字段，故拒绝。"""
    def unique(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"JSON 重复键：{key}")
            result[key] = value
        return result

    data = json.loads(exact_file(path).read_text(encoding="utf-8"), object_pairs_hook=unique)
    require(isinstance(data, dict), f"要求 JSON 对象：{path}")
    return data


def check_derivation(root: Path, profile: dict) -> None:
    """核对原14源字节、几何常量和同沿坐标寄存器的精确派生关系。"""
    item = profile["source_derivation"]
    require(set(item) == {"policy", "upstream_freeze_commit", "derivation_baseline_commit",
        "newline_policy", "upstream_sources", "derived_sources"}, "派生绑定字段不符")
    require(item["policy"] == "s2b-constant-geometry-coordinates-route-and-conv-validation/1.0.0" and
        item["upstream_freeze_commit"] == "671f9cf494b92ce182b3f1542fefd0cfd4b209f5" and
        item["derivation_baseline_commit"] == "f53e067ba91abc02ed60cf7f9063884d9ddb79f1",
        "派生上游或基线不符")
    require(item["newline_policy"] == "派生源按UTF-8/LF创建；仅比较派生关系时将上游CRLF转为LF；冻结上游SHA始终绑定原字节。",
        "换行政策不符")
    require(item["upstream_sources"] == [{"path": path, "sha256": digest}
        for path, digest in FROZEN_CORE_SHA256.items()], "原14源绑定不符")
    for path, digest in FROZEN_CORE_SHA256.items():
        require(sha256(relative_file(root, path)) == digest, f"冻结2A原件字节变化：{path}")
    require(isinstance(item["derived_sources"], list) and len(item["derived_sources"]) == 8,
        "派生源必须恰为8项")
    for declared, (source, (path, replacements)) in zip(item["derived_sources"], DERIVATION_RULES.items()):
        require(set(declared) == {"source", "path", "sha256", "replacements"} and
            declared["source"] == source and declared["path"] == path and
            declared["replacements"] == replacements, "派生映射或允许差异不符")
        expected = relative_file(root, source).read_bytes().decode("utf-8").replace("\r\n", "\n")
        for before, after in replacements:
            require(expected.count(before) == 1, f"派生替换不是唯一命中：{source}:{before}")
            expected = expected.replace(before, after)
        raw = relative_file(root, path).read_bytes()
        require(raw == expected.encode("utf-8"), f"派生源存在未授权的额外差异：{path}")
        require(declared["sha256"] == hashlib.sha256(raw).hexdigest(), f"派生SHA不符：{path}")


def check_static(root: Path) -> dict:
    """仅确认可恢复输入和公开口约束，不替代 IPI/RTL 审查。"""
    profile = read_json(root / "board/s2b_inference_platform.json")
    require(profile["version"] == PROFILE_VERSION, "平台版本不符")
    require(profile.get("physical_interface") == "s2b-physical-candidate/0.1.1", "物理候选版本不符")
    require(profile["requested_part_literal"] == "XC7Z020-2CLG400I", "原始型号被改变")
    require(profile["vivado_part"] == "xc7z020clg400-2", "工具器件不符")
    require(profile["clock_hz"] == 50_000_000 and profile["visibility_default"] == 0, "时钟或默认门控不符")
    require(profile.get("visibility_binding_only") is True, "机器检查不能声明语义或批准来源已验证")
    require(profile.get("prior_cache_probe") == {"visibility_parameter": 0, "physical_state": "IDLE_PS",
        "epoch": 0, "start_count": 0, "load_count": 0, "abi": "S2BU/1", "operation": 4,
        "header_bytes": 40, "payload_bytes": 12, "physical_address": "0x10000000", "length_bytes": 256,
        "word_count": 64, "phase0": "FLUSH_DSB_WAIT_DAP", "phase1": "INVALIDATE_DSB_COMPARE"}, "先验探针入口约束不符")
    require(profile["physical_ports"] == ["DDR", "FIXED_IO"], "物理端口集合不符")
    require(profile["control"] == {"base": "0x43C00000", "length_bytes": 65536,
        "gp_protocol": "AXI3", "gp_data_width": 32, "gp_id_width": 12,
        "slave_protocol": "AXI4LITE", "slave_addr_width": 32}, "控制接口不符")
    require(profile["memory"] == {"protocol": "AXI3", "data_width": 64, "id_width": 6,
        "arena_base": "0x10000000", "arena_end_exclusive": "0x12000000",
        "axcache": "0000", "direct_hp0": True}, "HP/全模型 arena 不符")
    sources = profile["rtl_sources"]
    check_derivation(root, profile)
    expected_sources = [DERIVATION_RULES[path][0] if path in DERIVATION_RULES else path
                        for path in FROZEN_CORE_SHA256] + list(LEGACY_2B_SOURCES)
    require(sources == expected_sources, "闭包必须精确为6个冻结2A、8个派生及4个原2B模块")
    script = relative_file(root, "vivado/s2b_inference_platform.tcl").read_text(encoding="utf-8")
    require("variable version 0.1.12" in script, "Tcl平台版本不符")
    require("list_properties" not in script and len(re.findall(r"\[list_property\s", script)) == 3,
        "Vivado 属性枚举必须使用官方 list_property 命令")
    require("make_wrapper -files $bd_file -top -import" in script and
        "set wrapper [get_files */${bd_name}_wrapper.v]" in script and
        "set wrapper [make_wrapper" not in script,
        "wrapper 必须由导入后的文件对象查询取得，不能假设创建命令返回文件")
    block = re.search(r"variable rtl_sources \{(.*?)\n    \}", script, re.S)
    require(block is not None and block.group(1).split() == sources, "Tcl/JSON源码闭包不一致")
    wrapper = relative_file(root, "src/s2b_inference_top.sv").read_text(encoding="utf-8")
    require("s2b_stage2b_core core (" in wrapper and "s2a_stage2a_core_ooc core (" not in wrapper,
            "公开顶层未实例化受绑定的2B派生核心")
    require("parameter bit PROFILE_VISIBILITY_PROVEN = 1'b0" in wrapper, "RTL默认可见性必须关闭")
    for expected in (".visibility_confirmed(PROFILE_VISIBILITY_PROVEN)",
        ".ledger_empty_next(ledger_empty_next)", ".axi_progress_next(axi_progress_next)",
        "PROTOCOL AXI3, ADDR_WIDTH 32, DATA_WIDTH 64, ID_WIDTH 6",
        "PROTOCOL AXI4LITE, ADDR_WIDTH 32, DATA_WIDTH 32"):
        require(expected in wrapper, f"公开口绑定缺失：{expected}")
    for name in ("s_axi_awaddr", "s_axi_araddr"):
        require(re.search(r"input logic \[31:0\] " + name, wrapper) is not None, f"完整32位地址缺失：{name}")
    adapter = relative_file(root, "src/s2b_hp0_word_adapter.sv").read_text(encoding="utf-8")
    for name in ("m_axi_awcache", "m_axi_arcache"):
        require(re.search(r"assign\s+" + name + r"\s*=\s*4'(?:b0000|d0|h0)\s*;", adapter) is not None,
            f"{name}必须固定非Bufferable 0000")
    require(profile["build_scripts"] == ["vivado/s2b_inference_platform.tcl", "vivado/s2b_ps_platform.tcl"],
            "构建脚本集合不符")
    files = list(dict.fromkeys(sources + list(FROZEN_CORE_SHA256) + profile["build_scripts"] +
        ["board/s2b_inference_platform.json", "board/s2b_inference_platform.md",
         "board/ps_platform_fields.json", "verification/check_s2b_inference_platform.py",
         "verification/test_s2b_conv_feature_address_rtl.py"]))
    return {path: sha256(relative_file(root, path)) for path in files}


def check_visibility(root: Path, proof_path: Path, review_path: Path, sources: dict, review_sha256: str) -> None:
    """只检查固定审查原件和证据绑定；独立来源与语义必须由总控核查。"""
    proof = read_json(proof_path)
    review = read_json(review_path)
    require(re.fullmatch(r"[0-9a-f]{64}", review_sha256 or "") is not None,
        "需要总控从独立 Reviewer 真来源冻结的审查原件 SHA-256")
    require(sha256(exact_file(review_path)) == review_sha256, "审查原件与固定哈希不符")
    require(proof.get("schema_version") == 1 and proof.get("status") == "PASS", "可见性证明未通过")
    require(proof.get("profile_version") == PROFILE_VERSION, "证明平台版本不符")
    require(proof.get("source_sha256") == sources, "证明源码/构建脚本与当前文件不一致")
    require(review.get("status") == "PASS" and review.get("role") == "INDEPENDENT_REVIEWER",
        "独立审查未通过")
    require(review.get("approved_profile_sha256") == sha256(exact_file(proof_path)), "审查未绑定精确证明内容")
    require(review.get("visibility_parameter") == 1 and review.get("cold_reset_only") is True,
        "审查未批准该参数及统一冷恢复约束")
    expected = {
        "hp_path_audit": ("PASS", ["axi3_nonbufferable_basis", "axcache_0000_full_path",
            "direct_hp0_no_bridge", "no_early_write_response", "full_model_core_present"]),
        "ps_cache_proof": ("PASS", ["dedicated_32mib_arena", "cache_maintenance_actual_bsp",
            "cpu_dap_prior_probe_idle_no_start", "same_runtime_bsp_mmu_macros", "no_use_amp", "single_cacheable_alias",
            "cpu1_other_writers_stopped", "unified_cold_reset_lifecycle"]),
    }
    for key, (status, checks) in expected.items():
        item = proof.get(key, {})
        path = relative_file(root, item["path"])
        require(item.get("sha256") == sha256(path), f"证据哈希不符：{key}")
        artifact = read_json(path)
        require(artifact.get("status") == status and artifact.get("source_sha256") == sources,
            f"证据未通过或源码绑定不符：{key}")
        require(all(artifact.get("checks", {}).get(check) is True for check in checks), f"证据覆盖不完整：{key}")
        if key == "ps_cache_proof":
            probe = artifact.get("prior_probe", {})
            require(probe.get("visibility_parameter") == 0 and probe.get("physical_state") == "IDLE_PS",
                "首次缓存先验探针必须visibility0且全程IDLE_PS")
            for field in ("epoch", "start_count", "load_count"):
                require(type(probe.get(field)) is int and probe[field] == 0,
                    f"首次探针不允许旧任务、START或LOAD：{field}")
            require(probe.get("abi") == "S2BU/1" and probe.get("operation") == 4 and
                probe.get("header_bytes") == 40 and probe.get("payload_bytes") == 12 and
                probe.get("physical_address") == "0x10000000" and probe.get("length_bytes") == 256 and
                probe.get("word_count") == 64 and probe.get("phase0") == "FLUSH_DSB_WAIT_DAP" and
                probe.get("phase1") == "INVALIDATE_DSB_COMPARE" and
                probe.get("dap_read_write_readback") is True, "CPU/DAP先验探针ABI或执行阶段不符")
            bindings = artifact.get("runtime_bindings", {})
            require(proof.get("runtime_bindings") == bindings, "证明与缓存先验运行绑定不一致")
            for name in ("elf", "bsp", "mmu", "macros", "ps_init", "cold_lifecycle", "uart_log", "dap_log"):
                item = bindings.get(name, {})
                require(item.get("sha256") == sha256(relative_file(root, item["path"])),
                    f"实际运行绑定缺失或哈希不符：{name}")
        # 每项结论必须有可恢复原始文件；该检查只验证绑定，语义由独立 Reviewer 判断。
        require(bool(artifact.get("evidence_files")), f"缺少原始证据：{key}")
        for raw in artifact["evidence_files"]:
            require(raw["sha256"] == sha256(relative_file(root, raw["path"])), f"原始证据哈希不符：{raw['path']}")


def main() -> int:
    """以退出码报告静态检查或审批产物绑定结果。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).absolute().parent.parent)
    parser.add_argument("--visibility-proof", type=Path)
    parser.add_argument("--review", type=Path)
    parser.add_argument("--review-sha256")
    args = parser.parse_args()
    try:
        require(args.root.is_absolute(), "仓库根必须为绝对路径")
        sources = check_static(args.root)
        if args.visibility_proof is not None or args.review is not None or args.review_sha256 is not None:
            require(args.visibility_proof is not None and args.review is not None and args.review_sha256 is not None,
                "证明、审查原件与总控固定审查哈希须一起提供")
            check_visibility(args.root, args.visibility_proof, args.review, sources, args.review_sha256)
            print("VISIBILITY_PROFILE:BINDINGS_VERIFIED")
        else:
            print("PLATFORM_STATIC:OK visibility=0 rtl_sources=18; 未证明BD/时序/实板通过")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"PLATFORM_CHECK:FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
