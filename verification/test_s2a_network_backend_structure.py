"""静态检查 T64 descriptor 后端结构，不替代 RTL 编译或功能仿真。"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "s2a_network_backend.sv"
PACKAGE_PATH = ROOT / "src" / "s2a_network_descriptor_pkg.sv"
CONV_ENGINE_PATH = ROOT / "src" / "s2a_conv_engine.sv"
CSR_PATH = ROOT / "src" / "s2a_control_csr.sv"
SUMMARY_PATH = ROOT / "report" / "evidence" / "S2A-T64" / "network_backend_static_summary.json"
DEADLINE_BENCH_PATH = ROOT / "sim" / "tb_s2a_network_backend_csr_deadline.sv"
LAYER0_PROBE_PATH = ROOT / "sim" / "tb_s2a_network_backend_layer0_probe.sv"
SIM_RUN07_PATH = ROOT / "report" / "evidence" / "S2A-T64" / "sim_run07"
SIM_RUN08_PATH = ROOT / "report" / "evidence" / "S2A-T64" / "sim_run08"
SIM_RUN09_PATH = ROOT / "report" / "evidence" / "S2A-T64" / "sim_run09"
SIM_RUN10_PATH = ROOT / "report" / "evidence" / "S2A-T64" / "sim_run10"
SIM_RUN11_PATH = ROOT / "report" / "evidence" / "S2A-T64" / "sim_run11"
SIM_RUN07_BENCH_SHA256 = "3c964f315a5686e4ba7a4f993f92e06664a503c3c1344524a2f9ada6fc4a60c6"
SIM_RUN07_EVIDENCE_SHA256 = {
    "xvlog.log": "3f0d334c15b64a700dede74cb5d50986bc976765b13550617868c5c08b870793",
    "xelab.log": "7a475e0d3aa40f1a363d9f70b10584dbba142bbed20b02ac0f28b5ee3f78ebc3",
    "xsim.log": "84db5ca6e89fb55b9dcb64bd291fa2de34d0c01cec92a4f51d6ceb1797993ab8",
    "run_deadline.cmd": "16478c49ce46e2a6de78fe05dfe1459f0dd88eab0684ab8bf8fb7ccdbcbb2100",
}
SIM_RUN07_PASS_MARKER = "PASS: backend/CSR deadline 同沿完成与错误，错误码 4 透传"
SIM_RUN08_EVIDENCE_SHA256 = {
    "run_layer0_probe.cmd": "181d3af3fd0bb22ab5d7e2e878fab858d6b7f0e90bbde51bc3a4ad2452e7f733",
    "xvlog_console.txt": "d09ffbe0d228ff18bc3644773eb158ddce2f4cecfe5daa825cf39c82316aa7be",
    "xelab_console.txt": "224077731ede4fc7731b90600a6ac2556268af3f07cbcc039aa5a89622010be8",
    "xsim_console.txt": "d29269a3749be2c5b03e20641e25d00a16eb9f2baf431abfb763e4178bc8c393",
    "xsim.log": "fe7758f2deea9435f57855e13976e137e64f4cd2f7b0828816c3efa8386d777a",
    "status.txt": "2c1ba071a0beec5233d5d2e7dcb2dac9bc88118e50ed5be5aa713e12bd00df3d",
}
SIM_RUN09_EVIDENCE_SHA256 = {
    "run_layer0_probe.cmd": "ab46f54c79a385914c3c4f66704f27d1f7be5774fec8a31254750e7365b6b8e5",
    "xvlog_console.txt": "d09ffbe0d228ff18bc3644773eb158ddce2f4cecfe5daa825cf39c82316aa7be",
    "xelab_console.txt": "f92d4b2ba9cef71d7d77b4ea367494df32634d1bfb1435385ca6fd0c96acc8e5",
    "xsim_console.txt": "028705821b8e5f702857a7f4a01b25957a67b31819d3c4395a6bd16154bdfd8d",
    "xsim.log": "a3cb0236c975f1cf4fe1c684fb6e38dd6046b02b9c29a2a5d35a294058b6407e",
    "status.txt": "2c1ba071a0beec5233d5d2e7dcb2dac9bc88118e50ed5be5aa713e12bd00df3d",
}
SIM_RUN10_EVIDENCE_SHA256 = {
    "run_layer0_probe.cmd": "747fd659fcce641a08a0fc34bc6bfc0f1d3c8f3d5eecc2b64c2737005b702bd2",
    "xvlog_console.txt": "d09ffbe0d228ff18bc3644773eb158ddce2f4cecfe5daa825cf39c82316aa7be",
    "xelab_console.txt": "f92d4b2ba9cef71d7d77b4ea367494df32634d1bfb1435385ca6fd0c96acc8e5",
    "xsim_console.txt": "c62affb526bc6af39f63f98b4343a215b13fc7675e74c508622a442b144610e4",
    "xsim.log": "88097be2e007fb5f510ea0dd392e6313b8327314402197df493b0ddafb5cc3d9",
    "status.txt": "2c1ba071a0beec5233d5d2e7dcb2dac9bc88118e50ed5be5aa713e12bd00df3d",
}
SIM_RUN11_BACKEND_SHA256 = "38f0563baccf091024ca93b5a488a869a69f6e61b837695564dade653f465e26"
SIM_RUN11_PROBE_SHA256 = "fc4823532aa5bac37f490153a1a70aa6e5e7e456e32729f1887fc157f1a7b49c"
SIM_RUN11_PASS_MARKER = "PASS: layer0真实CONV dispatch/start/result/write，reads=24 writes=1 cycles=109"
SIM_RUN11_EVIDENCE_SHA256 = {
    "run_layer0_probe.cmd": "eccd6403375fc013aea15aadd8e01d2efba86e6bfd29742541b554798bec319d",
    "status.txt": "d596d218a458868c7af4743d37dc4cc2d91246735b0bb8d2512444fbac86efb8",
    "xvlog_console.txt": "d09ffbe0d228ff18bc3644773eb158ddce2f4cecfe5daa825cf39c82316aa7be",
    "xvlog.log": "e9a50e37da05ee5b4963236375bd6a6efbe641770296791256c30d036bd6b06c",
    "xelab_console.txt": "f92d4b2ba9cef71d7d77b4ea367494df32634d1bfb1435385ca6fd0c96acc8e5",
    "xelab.log": "91f892490f2e301c066de791afca82e839363c305a7aa4bdd98fe5e2bf73a907",
    "xsim_console.txt": "dd335e14e347975f492263dcdd4167f16c2d3214d526ba586d5746bed8cb09da",
    "xsim.log": "aaa4ab1a1198cfec33787c1f7f621d0d651ee4aba5a8d50036dd72662ec21700",
}


def sha256(path: Path) -> str:
    """计算文件的 SHA-256。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    """条件不满足时以中文说明静态契约失败。"""
    if not condition:
        raise AssertionError(message)


def read_sources() -> tuple[str, str]:
    """以 UTF-8 读取后端和描述符包。"""
    return MODULE_PATH.read_text(encoding="utf-8"), PACKAGE_PATH.read_text(encoding="utf-8")


def parse_hex_array(package: str, name: str) -> list[int]:
    """读取 ROM 中一维 38 项十六进制常量数组。"""
    match = re.search(
        rf"\b{name}\s*\[0:37\]\s*=\s*'\{{(.*?)\n\s*\}};",
        package,
        re.DOTALL,
    )
    require(match is not None, f"无法从冻结 ROM 读取数组 {name}")
    tokens = re.findall(r"\b\d+'[hH]([0-9A-Fa-f_]+)", match.group(1))
    require(len(tokens) == 38, f"{name} 应有 38 项，实际 {len(tokens)}")
    return [int(token.replace("_", ""), 16) for token in tokens]


def check_frozen_package_binding(module: str, package: str) -> None:
    require("import s2a_network_descriptor_pkg::*;" in module,
            "后端未导入冻结描述符包")
    require("S2A_LAYER_COUNT = 38" in package,
            "描述符包层数不是冻结的 38 层")
    require("S2A_SERIAL_DISPATCH = 1'b1" in package and
            "S2A_TIMEOUT_SCOPE_GLOBAL = 1'b1" in package and
            "S2A_PS_VISIBLE_CSR_CHANGED = 1'b0" in package,
            "描述符包冻结的调度/timeout/CSR 约束缺失")
    require("S2A_OP[layer_cursor]" in module and
            "S2A_LAYER_INDEX[layer_cursor]" in module,
            "后端未按 ROM 层序读取算子描述符")


def check_shared_engines(module: str) -> None:
    for engine in ("conv", "maxpool", "route", "upsample"):
        matches = re.findall(rf"\bs2a_{engine}_engine\s+u_{engine}_engine\s*\(", module)
        require(len(matches) == 1, f"{engine} engine 实例数应恰为 1，实际 {len(matches)}")
    require("case (current_op)" in module and "case (layer_cursor)" not in module,
            "后端必须通过 descriptor op 类型调度，不能按层号硬编码")
    for op in ("S2A_OP_CONV", "S2A_OP_MAXPOOL", "S2A_OP_ROUTE",
               "S2A_OP_UPSAMPLE", "S2A_OP_YOLO"):
        require(op in module, f"后端没有覆盖 {op}")


def check_rom_operator_and_alias_rows(package: str) -> None:
    ops = parse_hex_array(package, "S2A_OP")
    require(set(ops) == {0, 1, 2, 3, 4}, "38 层 ROM 没有覆盖五种冻结 op 类")
    alias_rows = [index for index, op in enumerate(ops) if op == 4]
    require(alias_rows == [30, 37], f"YOLO alias descriptor 行与冻结 ROM 不符：{alias_rows}")
    fields = {
        name: parse_hex_array(package, name)
        for name in (
            "S2A_OUTPUT_TENSOR_INDEX", "S2A_OUTPUT_ALLOCATION_KIND",
            "S2A_OUTPUT_ALIAS_LAYER_INDEX", "S2A_OUTPUT_MEMORY_WRITE_REQUIRED",
            "S2A_OUTPUT_ADDRESS", "S2A_OUTPUT_LENGTH_BYTES", "S2A_OUTPUT_N",
            "S2A_OUTPUT_C", "S2A_OUTPUT_H", "S2A_OUTPUT_W",
        )
    }
    for row in alias_rows:
        source = fields["S2A_OUTPUT_ALIAS_LAYER_INDEX"][row]
        require(fields["S2A_OUTPUT_MEMORY_WRITE_REQUIRED"][row] == 0 and
                fields["S2A_OUTPUT_ALLOCATION_KIND"][row] == 1 and source < 38,
                f"YOLO 行 {row} 的 alias ownership 标志无效")
        for name in ("S2A_OUTPUT_TENSOR_INDEX", "S2A_OUTPUT_ADDRESS",
                     "S2A_OUTPUT_LENGTH_BYTES", "S2A_OUTPUT_N", "S2A_OUTPUT_C",
                     "S2A_OUTPUT_H", "S2A_OUTPUT_W"):
            require(fields[name][row] == fields[name][source],
                    f"YOLO 行 {row} 与 alias 来源 {source} 的 {name} 不一致")


def check_descriptor_field_binding(module: str) -> None:
    names = (
        "S2A_INPUT_ADDRESS", "S2A_INPUT_LENGTH_BYTES", "S2A_INPUT_N",
        "S2A_INPUT_C", "S2A_INPUT_H", "S2A_INPUT_W", "S2A_OUTPUT_ADDRESS",
        "S2A_OUTPUT_LENGTH_BYTES", "S2A_OUTPUT_N", "S2A_OUTPUT_C",
        "S2A_OUTPUT_H", "S2A_OUTPUT_W", "S2A_KERNEL_H", "S2A_KERNEL_W",
        "S2A_STRIDE_H", "S2A_STRIDE_W", "S2A_PADDING_LEFT",
        "S2A_PADDING_RIGHT", "S2A_PADDING_TOP", "S2A_PADDING_BOTTOM",
        "S2A_GROUP_COUNT", "S2A_PADDING_VALUE_INT8", "S2A_ACTIVATION",
        "S2A_GF8_WEIGHT_OFFSET", "S2A_GF8_WEIGHT_BYTES",
        "S2A_MAXPOOL_DARKNET_PADDING", "S2A_UPSAMPLE_STRIDE",
    )
    for name in names:
        require(name in module, f"后端未读取描述符字段 {name}")
    require("input_base_address" in module and "input_length_bytes" in module and
            "weight_package_base_address" in module and "weight_package_length_bytes" in module,
            "运行时输入/权重配置端口缺失")
    require("(layer_cursor == 6'd0) && (source_slot == 0)" in module,
            "运行时输入基址未限制为第一层的网络输入")
    conv_descriptor_branch = re.search(
        r"if\s*\(\s*current_op\s*==\s*S2A_OP_CONV\s*\)\s*begin"
        r"(?P<body>.*?)\n\s*end\s+else if\s*\(\(current_op == S2A_OP_MAXPOOL\)",
        module,
        re.DOTALL,
    )
    require(conv_descriptor_branch is not None,
            "CONV descriptor 必须先按 op 类型分支，再在分支内验证字段")
    require("if ((current_input_count != 2'd1) ||" in conv_descriptor_branch.group("body") and
            "descriptor_valid = 1'b0;" in conv_descriptor_branch.group("body") and
            not re.search(r"if\s*\(\(current_op\s*==\s*S2A_OP_CONV\)\s*&&",
                          module),
            "CONV 合法字段路径可能继续落入非 alias fallback")


def check_nchw_decode(module: str) -> None:
    for signal in ("decoded_batch", "decoded_channel", "decoded_y", "decoded_x"):
        require(signal in module, f"缺少 NCHW 坐标 {signal}")
    require("output_element_index / output_batch_elements" in module and
            "output_element_index / output_plane_elements" in module and
            "output_element_index / {48'd0, output_w}" in module and
            "output_element_index % output_w" in module,
            "线性输出索引未按 NCHW 解码")
    require("(output_n != 16'd1)" in module and "(source_n[validate_slot] != 16'd1)" in module,
            "未将非 N=1 descriptor 作为内部描述符错误拒绝")


def check_t23_flattened_rom(module: str) -> None:
    require("S2A_T23_MQ_BASE[layer_cursor]" in module and
            "S2A_T23_MQ_ROM[mq_index]" in module and
            "S2A_CONV_BIAS_ACCUMULATOR_INT32[mq_index]" in module,
            "卷积 M/Q 或 bias 未使用 T23 平坦基址索引")
    for field_slice in ("[79:48]", "[47:40]", "[39:8]", "[7:0]"):
        require(f"S2A_T23_MQ_ROM[mq_index]{field_slice}" in module,
                f"T23 ROM 解包缺少字段切片 {field_slice}")
    require(".positive_q_shift({24'd0," in module and
            ".negative_q_shift({24'd0," in module,
            "8-bit Q 未零扩展到引擎的 32-bit 端口")
    require("S2A_T23_MQ_CHANNEL_COUNT[layer_cursor]" in module and
            "S2A_CONV_CHANNEL_COUNT" in module,
            "卷积平坦 M/Q ROM 范围没有静态边界检查")


def check_activation_adapter(module: str, package: str, engine: str) -> None:
    require("S2A_ACT_LEAKY = 2'd2" in package,
            "冻结 descriptor leaky activation 编码不是预期的 2")
    require("S2A_ACT_NONE, S2A_ACT_LINEAR: map_conv_activation = 2'd0;" in module and
            "S2A_ACT_LEAKY: map_conv_activation = 2'd1;" in module and
            ".activation_mode(map_conv_activation(S2A_ACTIVATION[layer_cursor]))" in module,
            "descriptor activation 未按卷积引擎接口映射")
    require("(activation_mode_latched > 2'd1)" in engine and
            "(activation_mode_latched == 2'd0)" in engine and
            "mac_result_data[31] ?" in engine and
            "negative_multiplier_latched : positive_multiplier_latched" in engine,
            "卷积引擎接受范围/正负 M/Q 语义未被适配器静态核对")


def check_route_sources(module: str) -> None:
    require("S2A_ROUTE_SOURCE_MULTIPLIER_Q31[layer_cursor][0]" in module and
            "S2A_ROUTE_SOURCE_MULTIPLIER_Q31[layer_cursor][1]" in module,
            "route 未绑定两个 descriptor Q31 系数")
    for name in ("S2A_INPUT_COUNT", "S2A_ROUTE_CHANNEL_START",
                 "S2A_ROUTE_CHANNEL_END", "S2A_INPUT_N", "S2A_INPUT_C",
                 "S2A_INPUT_H", "S2A_INPUT_W"):
        require(name in module, f"route source 描述符缺少 {name}")
    require("(current_input_count != 2'd1) && (current_input_count != 2'd2)" in module,
            "route source 数未限制为 1 或 2")


def check_memory_handshake_and_response_stage(module: str) -> None:
    require("mem_valid = selected_req_valid && buffer_owner_pl && !hard_reset &&" in module and
            "!abort && !response_pending;" in module,
            "memory request 未同时受 owner/reset/abort/outstanding 状态门控")
    require("memory_handshake = mem_valid && mem_ready;" in module and
            "conv_req_ready = (state == ST_WAIT_CONV) && mem_valid && mem_ready;" in module,
            "请求 ready 与 G0 valid/ready handshake 不一致")
    require("response_data_latched <= mem_rdata;" in module and
            "response_error_latched <= mem_error_code;" in module and
            "response_target_latched <= current_op;" in module,
            "同周期响应数据/错误/目标未在请求握手时暂存")
    require("response_pending <= 1'b1;" in module and
            "response_pending && (response_target_latched == S2A_OP_CONV)" in module and
            "response_pending && (response_target_latched == S2A_OP_ROUTE)" in module,
            "暂存响应未在后续周期仅送达对应引擎")
    require("backend_memory_error_valid = memory_handshake && (mem_error_code != NONE);" in module,
            "CSR memory error event 未限定为非零已接受响应")


def check_combinational_deadline_event(module: str, csr: str) -> None:
    require("operator_result_valid = 1'b0;" in module and
            "operator_error_code = NONE;" in module and
            not re.search(r"\boperator_result_valid\s*<=", module) and
            not re.search(r"\boperator_error_code\s*<=", module),
            "operator event 必须是组合事件，不能寄存后再交给 CSR")
    normalize_match = re.search(
        r"function\s+automatic\s+logic\s*\[2:0\]\s*normalize_engine_error"
        r"\s*\(input\s+logic\s*\[2:0\]\s*code\s*\);(.*?)endfunction",
        module,
        re.DOTALL,
    )
    require(normalize_match is not None, "缺少完整的引擎错误码归一化函数")
    normalize = normalize_match.group(1)
    require(re.search(r"3'd0\s*:\s*normalize_engine_error\s*=\s*NONE\s*;", normalize),
            "合法成功码 0 必须映射为 NONE")
    passthrough = re.search(
        r"3'd1\s*,\s*3'd2\s*,\s*3'd3\s*,\s*3'd4\s*,\s*3'd5\s*,\s*3'd6\s*,\s*3'd7"
        r"\s*:\s*normalize_engine_error\s*=\s*code\s*;",
        normalize,
    )
    require(passthrough is not None, "已知引擎错误码 1..7 必须逐值透明透传")
    require("default: normalize_engine_error = INTERNAL;" in normalize,
            "未知或含 X/Z 的错误码必须由 default 映射为 INTERNAL")
    require("if (selected_result_valid &&" in module and
            "(normalize_engine_error(selected_result_error) != NONE)" in module and
            "operator_error_code = normalize_engine_error(selected_result_error);" in module,
            "引擎成功码 0 不得触发 operator error，非零归一化错误仍需上报")
    event_index = csr.index("else if (operator_result_valid)")
    timeout_index = csr.index("else if ((elapsed_cycles + 32'd1) >= timeout_cycles)")
    require(event_index < timeout_index,
            "CSR 的 terminal result 优先级不高于同沿 timeout")
    check_sim_run10_evidence()
    check_sim_run11_evidence()


def check_sim_run10_evidence() -> None:
    """核对复现实证：engine 成功码 0 被旧归一化错误映射为 INTERNAL。"""
    evidence: dict[str, str] = {}
    for name, expected_hash in SIM_RUN10_EVIDENCE_SHA256.items():
        path = SIM_RUN10_PATH / name
        require(path.is_file(), f"sim_run10 缺少证据文件 {name}")
        actual_hash = sha256(path)
        require(actual_hash == expected_hash,
                f"sim_run10 证据 {name} SHA 与固定运行不符")
        evidence[name] = path.read_text(encoding="utf-8", errors="replace")

    for name in ("xvlog_console.txt", "xelab_console.txt"):
        require(not re.search(r"(?im)^\s*(?:ERROR|FATAL):", evidence[name]),
                f"sim_run10 {name} 含 ERROR/FATAL")
    require("analyzing module tb_s2a_network_backend_layer0_probe" in
            evidence["xvlog_console.txt"].lower() and
            "Built simulation snapshot s2a_t64_layer0_snapshot" in
            evidence["xelab_console.txt"],
            "sim_run10 未成功编译并展开 layer0 probe")
    require("XSIM_LOG_FAIL" in evidence["status.txt"],
            "sim_run10 runner 未记录 xsim 日志失败")
    for name in ("xsim_console.txt", "xsim.log"):
        log = evidence[name]
        require("LAYER0_ERROR_SNAPSHOT operator_valid=1 operator_error=6 "
                "selected_result_valid=1 selected_result_error=0" in log and
                "conv_result_valid=1 conv_result_error=0" in log and
                "csr_elapsed=109 csr_busy=1 csr_owner=1 csr_error=0 csr_error_code=0" in log,
                f"sim_run10 {name} 未证明 CSR 报错前成功码 0 被映射为 INTERNAL=6")


def check_sim_run11_evidence() -> None:
    """核对成功码映射修复后的真实 backend 首个 layer0 输出仿真。"""
    require(sha256(MODULE_PATH) == SIM_RUN11_BACKEND_SHA256,
            "sim_run11 PASS 未绑定当前 backend RTL SHA")
    require(sha256(LAYER0_PROBE_PATH) == SIM_RUN11_PROBE_SHA256,
            "sim_run11 PASS 未绑定当前 layer0 probe SHA")

    evidence: dict[str, str] = {}
    for name, expected_hash in SIM_RUN11_EVIDENCE_SHA256.items():
        path = SIM_RUN11_PATH / name
        require(path.is_file(), f"sim_run11 缺少证据文件 {name}")
        actual_hash = sha256(path)
        require(actual_hash == expected_hash,
                f"sim_run11 证据 {name} SHA 与固定运行不符")
        evidence[name] = path.read_text(encoding="utf-8", errors="replace")

    for name in ("xvlog_console.txt", "xvlog.log", "xelab_console.txt", "xelab.log"):
        require(not re.search(r"(?im)^\s*(?:ERROR|FATAL):", evidence[name]),
                f"sim_run11 {name} 含 ERROR/FATAL")
    require("analyzing module tb_s2a_network_backend_layer0_probe" in
            evidence["xvlog_console.txt"].lower() and
            "Built simulation snapshot s2a_t64_layer0_snapshot" in
            evidence["xelab_console.txt"],
            "sim_run11 xvlog/xelab 未成功编译并展开 layer0 probe")
    require(evidence["status.txt"].strip() == "PASS",
            "sim_run11 runner 状态不是 PASS")
    for name in ("xsim_console.txt", "xsim.log"):
        log = evidence[name]
        require(SIM_RUN11_PASS_MARKER in log and
                "$finish called at time : 1166 ns" in log and
                not re.search(r"(?im)^\s*(?:ERROR|FATAL):", log),
                f"sim_run11 {name} 缺少 layer0 PASS/结束标记或含 ERROR/FATAL")


def check_deadline_bench_source() -> None:
    require(DEADLINE_BENCH_PATH.is_file(), "缺少 backend+CSR deadline 联合自检 bench")
    bench = DEADLINE_BENCH_PATH.read_text(encoding="utf-8")
    for token in (
        "s2a_control_csr u_csr", "s2a_network_backend u_backend",
        "u_csr.timeout_cycles != TEST_TIMEOUT",
        "!backend_start || !busy || !buffer_owner_pl || error",
        "deadline_preedge_reached",
        "elapsed_wait_index < (TEST_TIMEOUT + 2)",
        "busy 在 deadline 前终止",
        "elapsed 未到 deadline 前一拍",
        "reset_wait_index < 4",
        "CSR write 未 ready",
        "force u_backend.state = u_backend.ST_DISPATCH",
        "force u_backend.layer_cursor = 6'd37",
        "force u_backend.state = u_backend.ST_WAIT_CONV",
        "force u_backend.selected_result_valid = 1'b0;",
        "force u_backend.selected_result_valid = 1'b1;",
        "force u_backend.selected_result_error = 3'd4",
        "deadline 同沿的全网完成事件未在采样前有效",
        "deadline 同沿的全网完成事件未在采样前有效",
        "CSR 未在 deadline 同沿优先接受全网完成事件",
        "CSR 未在 deadline 同沿优先接受后端错误事件",
        "CSR 未保存已知错误码 4",
    ):
        require(token in bench, f"deadline bench 缺少检查点：{token}")
    require("localparam logic [2:0] ST_DISPATCH" not in bench and
            "localparam logic [2:0] ST_WAIT_CONV" not in bench,
            "deadline bench 不应以 logic 常量代替 backend 的 enum 成员")
    require(not re.search(r"\bwhile\s*\(", bench),
            "deadline bench 等待条件必须有界，禁止无限 while")
    accepted_start_index = bench.index("if (!backend_start || !busy || !buffer_owner_pl || error)")
    freeze_backend_index = bench.index("force u_backend.state = u_backend.ST_WAIT_CONV;")
    elapsed_wait_index = bench.index("elapsed_wait_index < (TEST_TIMEOUT + 2)")
    require(accepted_start_index < freeze_backend_index < elapsed_wait_index and
            "operator_result_valid || backend_memory_error_valid" in bench,
            "bench 未在确认 CSR 接受 start 后、计时等待前冻结无结果 backend")
    require("!busy || (u_csr.elapsed_cycles != (TEST_TIMEOUT - 32'd1))" in bench,
            "deadline 注入前没有断言 busy 保持到 timeout 前一拍")
    require("此 bench 只隔离 CSR deadline 接口" in bench,
            "bench 未明确说明冻结 backend 的隔离范围")
    check_sim_run07_evidence()
    check_layer0_probe_source()


def check_layer0_probe_source() -> None:
    require(LAYER0_PROBE_PATH.is_file(), "缺少真实 backend layer0 probe bench")
    probe = LAYER0_PROBE_PATH.read_text(encoding="utf-8")
    for token in (
        "import s2a_network_descriptor_pkg::*;",
        "s2a_control_csr u_csr", "s2a_network_backend u_backend",
        "assign mem_ready = !hard_reset && busy && buffer_owner_pl;",
        "assign mem_rdata = 32'd0;",
        "assign mem_error_code = 3'd0;",
        "localparam logic [31:0] TEST_TIMEOUT = 32'd1000000",
        "localparam integer PROBE_CYCLE_LIMIT = 20000",
        ".input_base_address(32'h0000_0000)",
        ".input_length_bytes(32'd519168)",
        ".weight_package_base_address(32'h0010_0000)",
        ".weight_package_length_bytes(32'd5903100)",
        "write_csr(REG_CMD, 32'd1)",
        "if (!backend_start || !busy || !buffer_owner_pl || error)",
        "u_backend.state == u_backend.ST_DISPATCH",
        "u_backend.conv_start_valid == 1'b1",
        "u_backend.conv_result_valid && u_backend.conv_result_ready",
        "if (mem_valid && mem_ready)",
        "mem_addr == S2A_OUTPUT_ADDRESS[0]",
        "layer0_dispatch_seen", "layer0_conv_start_seen",
        "layer0_result_seen", "layer0_output_write_seen",
        "for (probe_cycle = 0; probe_cycle < PROBE_CYCLE_LIMIT;",
        "descriptor_valid=%b descriptor_fault=%b",
        "selected_start_ready=%b conv_start_valid=%b conv_start_ready=%b",
        "validation_ok=%b validation_error=%0d geometry_error=%0d weight_error=%0d",
        "result_error_latched=%0d result_addr=%08h result_value=%02h",
        "LAYER0_DESC index cursor=%0d rom=%0d match=%b op=%0d input_count=%0d",
        "S2A_INPUT_KIND[u_backend.layer_cursor][0]",
        "S2A_INPUT_ADDRESS[u_backend.layer_cursor][0]",
        "S2A_INPUT_LENGTH_BYTES[u_backend.layer_cursor][0]",
        "S2A_INPUT_N[u_backend.layer_cursor][0]",
        "S2A_INPUT_C[u_backend.layer_cursor][0]",
        "S2A_INPUT_H[u_backend.layer_cursor][0]",
        "S2A_INPUT_W[u_backend.layer_cursor][0]",
        "S2A_INPUT_KIND[u_backend.layer_cursor][1]",
        "S2A_OUTPUT_ADDRESS", "S2A_OUTPUT_LENGTH_BYTES",
        "S2A_OUTPUT_N", "S2A_OUTPUT_C", "S2A_OUTPUT_H", "S2A_OUTPUT_W",
        "S2A_OUTPUT_ALLOCATION_KIND", "S2A_OUTPUT_MEMORY_WRITE_REQUIRED",
        "S2A_ACTIVATION", "S2A_WEIGHT_LAYER_INDEX", "S2A_T23_MQ_BASE",
        "S2A_T23_MQ_CHANNEL_COUNT", "decoded_channel", "mq_index",
        "S2A_CONV_CHANNEL_COUNT", "source0_shape_ok", "source0_kind_ok",
        "source1_shape_ok", "source1_kind_ok", "output_shape_ok",
        "output_ownership_ok", "conv_input_count_ok",
        "conv_mq_channel_count_ok", "conv_mq_index_ok", "conv_mq_range_ok",
        "conv_activation_ok", "conv_weight_layer_ok", "descriptor_op_ok",
        "descriptor_predicates_ok",
        "always @(negedge clk)", "!error_snapshot_valid",
        "operator_result_valid && (operator_error_code != 3'd0)",
        "snapshot_output_element_index <= u_backend.output_element_index;",
        "snapshot_operator_result_valid <= operator_result_valid;",
        "snapshot_operator_error_code <= operator_error_code;",
        "snapshot_selected_result_valid <= u_backend.selected_result_valid;",
        "snapshot_selected_result_error <= u_backend.selected_result_error;",
        "snapshot_conv_engine_state <= u_backend.u_conv_engine.state;",
        "snapshot_conv_engine_start_ready <= u_backend.conv_start_ready;",
        "snapshot_conv_result_valid <= u_backend.conv_result_valid;",
        "snapshot_conv_result_error <= u_backend.conv_result_error;",
        "snapshot_response_pending <= u_backend.response_pending;",
        "snapshot_conv_rsp_valid <= u_backend.conv_rsp_valid;",
        "snapshot_mem_valid <= mem_valid;", "snapshot_mem_ready <= mem_ready;",
        "snapshot_csr_elapsed_cycles <= u_csr.elapsed_cycles;",
        "LAYER0_ERROR_SNAPSHOT valid=%b backend_state=%0d layer=%0d op=%0d output_element_index=%0d",
        "LAYER0_ERROR_SNAPSHOT operator_valid=%b operator_error=%0d selected_result_valid=%b selected_result_error=%0d",
        "LAYER0_ERROR_SNAPSHOT conv_req_valid=%b conv_req_write=%b conv_req_addr=%08h conv_rsp_valid=%b",
        "LAYER0_ERROR_SNAPSHOT mem_valid=%b mem_write=%b mem_addr=%08h",
        "LAYER0_ERROR_SNAPSHOT csr_elapsed=%0d",
        "u_csr.elapsed_cycles", "u_csr.timeout_cycles",
        "PASS: layer0真实CONV dispatch/start/result/write",
    ):
        require(token in probe, f"layer0 probe 缺少检查点：{token}")
    require(not re.search(r"\b(?:force|release)\b", probe),
            "layer0 probe 不得强制驱动 backend 或 engine 状态")
    require(not re.search(r"\bwhile\s*\(", probe),
            "layer0 probe 等待必须有界，禁止无限 while")
    require("if (error ||" in probe and
            "!(layer0_dispatch_seen && layer0_conv_start_seen &&" in probe,
            "layer0 probe 未在有界窗口内监测错误与全部成功里程碑")
    error_branch = probe.index("if (error) begin", probe.index("for (probe_cycle"))
    snapshot_wait = probe.index("@(negedge clk);", error_branch)
    diagnostic_report = probe.index("report_probe_diagnostics();", error_branch)
    require(snapshot_wait < diagnostic_report,
            "layer0 probe 在 negedge 错误快照前已打印失败现场")
    check_sim_run08_evidence()
    check_sim_run09_evidence()


def check_sim_run07_evidence() -> None:
    """核对隔离 deadline 联合仿真的固定证据和当前 bench 版本。"""
    status_path = SIM_RUN07_PATH / "status.txt"
    require(status_path.is_file() and
            status_path.read_text(encoding="utf-8").strip() == "PASS",
            "sim_run07 runner 状态不是 PASS")
    require(sha256(DEADLINE_BENCH_PATH) == SIM_RUN07_BENCH_SHA256,
            "sim_run07 PASS 未绑定当前 deadline bench SHA")

    evidence: dict[str, str] = {}
    for name, expected_hash in SIM_RUN07_EVIDENCE_SHA256.items():
        path = SIM_RUN07_PATH / name
        require(path.is_file(), f"sim_run07 缺少证据文件 {name}")
        actual_hash = sha256(path)
        require(actual_hash == expected_hash,
                f"sim_run07 证据 {name} SHA 与已复跑结果不符")
        evidence[name] = path.read_text(encoding="utf-8", errors="replace")

    for name in ("xvlog.log", "xelab.log", "xsim.log"):
        require(not re.search(r"(?im)^\s*(?:ERROR|FATAL):", evidence[name]),
                f"sim_run07 {name} 含 ERROR/FATAL")
    require("Vivado Simulator v2026.1" in evidence["xelab.log"] and
            "xsim v2026.1" in evidence["xsim.log"],
            "sim_run07 工具版本不是 Vivado Simulator 2026.1")
    require(SIM_RUN07_PASS_MARKER in evidence["xsim.log"] and
            "$finish called at time : 227 ns" in evidence["xsim.log"],
            "sim_run07 缺少 deadline 同沿 PASS 标记或 227ns 结束证据")


def check_sim_run08_evidence() -> None:
    """核对 layer0 probe 的既有失败证据及文件哈希。"""
    evidence: dict[str, str] = {}
    for name, expected_hash in SIM_RUN08_EVIDENCE_SHA256.items():
        path = SIM_RUN08_PATH / name
        require(path.is_file(), f"sim_run08 缺少证据文件 {name}")
        actual_hash = sha256(path)
        require(actual_hash == expected_hash,
                f"sim_run08 证据 {name} SHA 与记录不符")
        evidence[name] = path.read_text(encoding="utf-8", errors="replace")

    for name in ("xvlog_console.txt", "xelab_console.txt"):
        require(not re.search(r"(?im)^\s*(?:ERROR|FATAL):", evidence[name]),
                f"sim_run08 {name} 含 ERROR/FATAL")
    require("analyzing module tb_s2a_network_backend_layer0_probe" in
            evidence["xvlog_console.txt"].lower(),
            "sim_run08 xvlog 未分析 layer0 probe 顶层")
    require("Built simulation snapshot s2a_t64_layer0_snapshot" in
            evidence["xelab_console.txt"],
            "sim_run08 xelab 未生成 probe 仿真 snapshot")
    require("XSIM_LOG_FAIL" in evidence["status.txt"],
            "sim_run08 runner 状态未记录 xsim 日志失败")
    for name in ("xsim_console.txt", "xsim.log"):
        require("descriptor_fault=1" in evidence[name] and
                "Time: 86 ns" in evidence[name] and
                "reads=0 output_writes=0" in evidence[name],
                f"sim_run08 {name} 未包含 86ns descriptor fault/无 memory handshake 证据")
        require("error=1 code=6" in evidence[name],
                f"sim_run08 {name} 未包含 CSR INTERNAL=6 结果")


def check_sim_run09_evidence() -> None:
    """核对真实 layer0 首次输出后 INTERNAL 失败的固定证据哈希。"""
    evidence: dict[str, str] = {}
    for name, expected_hash in SIM_RUN09_EVIDENCE_SHA256.items():
        path = SIM_RUN09_PATH / name
        require(path.is_file(), f"sim_run09 缺少证据文件 {name}")
        actual_hash = sha256(path)
        require(actual_hash == expected_hash,
                f"sim_run09 证据 {name} SHA 与记录不符")
        evidence[name] = path.read_text(encoding="utf-8", errors="replace")

    for name in ("xvlog_console.txt", "xelab_console.txt"):
        require(not re.search(r"(?im)^\s*(?:ERROR|FATAL):", evidence[name]),
                f"sim_run09 {name} 含 ERROR/FATAL")
    require("analyzing module tb_s2a_network_backend_layer0_probe" in
            evidence["xvlog_console.txt"].lower() and
            "Built simulation snapshot s2a_t64_layer0_snapshot" in
            evidence["xelab_console.txt"],
            "sim_run09 xvlog/xelab 未成功编译并展开 layer0 probe")
    require("XSIM_LOG_FAIL" in evidence["status.txt"],
            "sim_run09 runner 状态未记录 xsim 失败")
    for name in ("xsim_console.txt", "xsim.log"):
        require("error=1 code=6" in evidence[name] and
                "elapsed=109 timeout=1000000" in evidence[name] and
                "dispatch=1 conv_start=1 result=1 output_write=1" in evidence[name] and
                "reads=24 output_writes=1" in evidence[name],
                f"sim_run09 {name} 未包含 elapsed=109 INTERNAL=6 与 layer0 成功里程碑")


def check_alias_skip_and_completion(module: str) -> None:
    for name in ("S2A_OUTPUT_MEMORY_WRITE_REQUIRED", "S2A_OUTPUT_ALLOCATION_KIND",
                 "S2A_OUTPUT_HEAD_ALIAS", "S2A_OUTPUT_ALIAS_LAYER_INDEX",
                 "S2A_OUTPUT_TENSOR_INDEX"):
        require(name in module, f"YOLO alias 检查缺少 {name}")
    require("if (is_alias_row) begin" in module and "else if (is_alias_row) begin" in module,
            "仅 YOLO alias 行没有走跳过写回路径")
    require("operator_result_valid = 1'b1;" in module and
            "operator_error_code = NONE;" in module and
            "(layer_cursor + 6'd1) >= S2A_LAYER_COUNT" in module,
            "全网完成事件没有以 38 层 ROM 边界为条件")
    require("normalize_engine_error(selected_result_error)" in module and
            "default: normalize_engine_error = INTERNAL;" in module,
            "引擎错误没有统一终止并将未知码映射为 INTERNAL")


def check_no_local_timeout_or_layer_special_case(module: str) -> None:
    require(not re.search(r"\b(timeout|elapsed_cycles|layer_timeout)\b", module, re.IGNORECASE),
            "后端新增了本地 timeout 或逐层 timeout 状态")
    require("case (layer_cursor)" not in module and
            not re.search(r"layer_cursor\s*==\s*6'd(?:[1-9]|[12][0-9]|3[0-7])", module),
            "后端包含逐层硬编码分支")
    require("if (response_pending) response_pending <= 1'b0;" in module,
            "单 outstanding 响应未在交付周期清除")


def main() -> int:
    module, package = read_sources()
    engine = CONV_ENGINE_PATH.read_text(encoding="utf-8")
    csr = CSR_PATH.read_text(encoding="utf-8")
    checks = (
        ("frozen_package_binding", lambda: check_frozen_package_binding(module, package)),
        ("shared_engines", lambda: check_shared_engines(module)),
        ("rom_operator_and_alias_rows", lambda: check_rom_operator_and_alias_rows(package)),
        ("descriptor_field_binding", lambda: check_descriptor_field_binding(module)),
        ("nchw_decode", lambda: check_nchw_decode(module)),
        ("t23_flattened_rom", lambda: check_t23_flattened_rom(module)),
        ("activation_adapter", lambda: check_activation_adapter(module, package, engine)),
        ("route_sources", lambda: check_route_sources(module)),
        ("memory_handshake_and_response_stage",
         lambda: check_memory_handshake_and_response_stage(module)),
        ("combinational_deadline_event",
         lambda: check_combinational_deadline_event(module, csr)),
        ("deadline_bench_source", check_deadline_bench_source),
        ("alias_skip_and_completion", lambda: check_alias_skip_and_completion(module)),
        ("no_local_timeout_or_layer_special_case",
         lambda: check_no_local_timeout_or_layer_special_case(module)),
    )
    passed: list[str] = []
    failures: list[dict[str, str]] = []
    for name, check in checks:
        try:
            check()
            passed.append(name)
        except AssertionError as exc:
            failures.append({"check": name, "reason": str(exc)})

    summary = {
        "task": "S2A-T64",
        "status": "STATIC_STRUCTURE_PASS" if not failures else "STATIC_STRUCTURE_FAIL",
        "simulation_status": "SIM_RUN11_LAYER0_FIRST_OUTPUT_PASS_FULL_NETWORK_UNVERIFIED",
        "scope": "静态结构检查通过。sim_run10 首错快照确认成功码 0 被旧映射误报为 operator INTERNAL=6；修复后 sim_run11 的真实 backend layer0 首个 CONV 输出通过 dispatch/start/result/write，读取 24 次并写回 1 次。该结果仅覆盖首个 layer0 输出元素；其余 layer0 元素、38 层整网及 109 输入一致性仍未验证。",
        "success_code_mapping_diagnostic": {
            "run": "report/evidence/S2A-T64/sim_run10",
            "launch_method": "Vivado MCP run_tcl；D 盘隔离运行目录",
            "xvlog": "PASS",
            "xelab": "PASS",
            "xsim": "FAIL",
            "runner_status": "XSIM_LOG_FAIL",
            "observed_failure": "sim_run10 首错快照于 CSR 置错/abort 前记录 backend ST_WAIT_CONV、descriptor_valid=1、selected_result_valid=1/selected_result_error=0、conv_result_valid=1/conv_result_error=0，但 operator_result_valid=1/operator_error_code=6；同一快照 CSR error=0/error_code=0，确认 normalize_engine_error(0) 错误落入 default INTERNAL。",
            "milestones": {
                "layer0_dispatch": 1,
                "layer0_conv_start": 1,
                "layer0_result_handshake": 1,
                "layer0_output_write_handshake": 1,
                "memory_reads": 24,
                "output_writes": 1,
            },
            "attempted_backend_sha256": "3b69e25584ec86515819804a005bfe4a32aa08fa5e11b053c3841d3b6ad27537",
            "attempted_probe_sha256": "fc4823532aa5bac37f490153a1a70aa6e5e7e456e32729f1887fc157f1a7b49c",
            "current_backend_sha256": sha256(MODULE_PATH),
            "current_probe_sha256": sha256(LAYER0_PROBE_PATH),
            "first_error_snapshot": {
                "backend_state": "ST_WAIT_CONV",
                "layer": 0,
                "descriptor_valid": 1,
                "operator_result_valid": 1,
                "operator_error_code": 6,
                "selected_result_valid": 1,
                "selected_result_error_code": 0,
                "conv_result_valid": 1,
                "conv_result_error_code": 0,
                "csr_error_before_event": 0,
                "csr_error_code_before_event": 0,
            },
            "snapshot_status": "sim_run10 首错快照确认映射根因；修复后的真实 layer0 probe 结果记录在 sim_run11。",
            "evidence_sha256": {
                name: sha256(SIM_RUN10_PATH / name)
                for name in SIM_RUN10_EVIDENCE_SHA256
            },
        },
        "last_dynamic_attempt": {
            "run": "report/evidence/S2A-T64/sim_run11",
            "launch_method": "Vivado MCP run_tcl；D 盘隔离运行目录",
            "tool_version": "Vivado Simulator 2026.1",
            "xvlog": "PASS",
            "xelab": "PASS",
            "xsim": "PASS",
            "runner_status": "PASS",
            "pass_marker": SIM_RUN11_PASS_MARKER,
            "finish": "$finish called at time : 1166 ns",
            "validation_scope": "真实 backend 接受合法 CSR start，layer0 CONV 完成 dispatch/start/result，并成功握手首个输出写回；memory reads=24、writes=1、elapsed cycles=109。",
            "backend_sha256": SIM_RUN11_BACKEND_SHA256,
            "probe_sha256": SIM_RUN11_PROBE_SHA256,
            "evidence_sha256": {
                name: sha256(SIM_RUN11_PATH / name)
                for name in SIM_RUN11_EVIDENCE_SHA256
            },
        },
        "prior_layer0_attempt": {
            "run": "report/evidence/S2A-T64/sim_run09",
            "runner_status": "XSIM_LOG_FAIL",
            "observed_failure": "elapsed=109 报 INTERNAL=6；当时未在 abort 前采集到足以区分原因的字段。",
            "attempted_backend_sha256": "3b69e25584ec86515819804a005bfe4a32aa08fa5e11b053c3841d3b6ad27537",
            "attempted_probe_sha256": "bc986a1f3b525992fea1f2391e6b6b50d9338d440676fab2fe16b47690796520",
            "evidence_sha256": {
                name: sha256(SIM_RUN09_PATH / name)
                for name in SIM_RUN09_EVIDENCE_SHA256
            },
        },
        "success_code_mapping_fix": {
            "function": "normalize_engine_error",
            "mapping": {"0": "NONE", "1..7": "透传", "未知或含 X/Z": "INTERNAL"},
            "operator_event_contract": "selected_result_valid 且归一化错误码非 NONE 时才生成 operator error；成功码 0 不触发错误事件。",
            "dynamic_post_fix_status": "SIM_RUN11_LAYER0_FIRST_OUTPUT_PASS",
            "dynamic_pre_fix_run": "report/evidence/S2A-T64/sim_run10",
            "dynamic_post_fix_run": "report/evidence/S2A-T64/sim_run11",
            "dynamic_post_fix_backend_sha256": SIM_RUN11_BACKEND_SHA256,
            "dynamic_post_fix_probe_sha256": SIM_RUN11_PROBE_SHA256,
        },
        "descriptor_fault_attempt": {
            "run": "report/evidence/S2A-T64/sim_run08",
            "launch_method": "Vivado MCP run_tcl；D 盘隔离运行目录",
            "xvlog": "PASS",
            "xelab": "PASS",
            "xsim": "FAIL at 86 ns",
            "runner_status": "XSIM_LOG_FAIL",
            "observed_failure": "CSR error=1/code=6，descriptor_valid=0/descriptor_fault=1，memory reads=0/output_writes=0。CONV bad-fields 条件为假时跌入非 alias fallback；该分支现已修复。",
            "attempted_backend_sha256": "4d5c1291a45696f73ca331a127cb02f092e7c77e870ae1f4ae9c7fe0feaceea9",
            "attempted_probe_sha256": "568815316a297e22b64dbb1c8f24e924ed4161905c8f8ff87a053d8d6987c7df",
            "evidence_sha256": {
                name: sha256(SIM_RUN08_PATH / name)
                for name in SIM_RUN08_EVIDENCE_SHA256
            },
        },
        "deadline_interface_attempt": {
            "run": "report/evidence/S2A-T64/sim_run07",
            "launch_method": "Vivado MCP check_connection（healthy）+ run_tcl；D 盘隔离运行目录",
            "tool_version": "Vivado 2026.1",
            "xvlog": "PASS",
            "xelab": "PASS",
            "xsim": "PASS",
            "runner_status": "PASS",
            "pass_marker": SIM_RUN07_PASS_MARKER,
            "finish": "$finish called at 227 ns",
            "validation_scope": "仅 backend/CSR deadline 同沿完成和错误接口；backend 在合法 start 被 CSR 接受后被冻结，随后注入 alias 最终成功或错误码 4。",
            "bench_sha256": sha256(DEADLINE_BENCH_PATH),
            "evidence_sha256": {
                name: sha256(SIM_RUN07_PATH / name)
                for name in SIM_RUN07_EVIDENCE_SHA256
            },
        },
        "unisolated_backend_attempt": {
            "run": "report/evidence/S2A-T64/sim_run06",
            "launch_method": "Vivado MCP run_tcl in an isolated D-drive run directory",
            "xvlog": "PASS",
            "xelab": "PASS",
            "xsim": "FAIL",
            "observed_failure": "At 90ns, before the deadline, CSR busy fell with elapsed_cycles=1, done=0, error=1, error_code=6, backend_start=0, and backend_abort=1.",
            "attempted_bench_sha256": "512ff5f5fe5c6a8f75a7c9fc829fc5beb092ff597fce9607084f63b60d5b6058",
            "current_bench_sha256": sha256(DEADLINE_BENCH_PATH),
            "interpretation": "该运行使用修复前 backend，失败来自 CONV descriptor 分支缺陷；后续 sim_run08/09 分别记录修复前后状态，sim_run07 deadline PASS 与真实启动无关。",
        },
        "prior_dynamic_attempt": {
            "run": "report/evidence/S2A-T64/sim_run05",
            "xvlog": "PASS",
            "xelab": "PASS",
            "xsim": "FAIL at the prior bench 100us watchdog before deadline assertions",
            "attempted_bench_sha256": "09c1f6f6faa1c38409edb21fd827e7d9abeae898ad4c0c25e45956e3875946ff",
        },
        "layer0_probe": {
            "bench": "sim/tb_s2a_network_backend_layer0_probe.sv",
            "status": "SIM_RUN11_PASS_LAYER0_FIRST_OUTPUT_ONLY",
            "attempted_bench_sha256": "bc986a1f3b525992fea1f2391e6b6b50d9338d440676fab2fe16b47690796520",
            "bench_sha256": sha256(LAYER0_PROBE_PATH),
            "timeout_cycles": 1000000,
            "probe_cycle_limit": 20000,
            "memory_model": "mem_ready=0 during reset/CSR idle/non-PL ownership; mem_ready=1 only while CSR busy and PL owns buffers; mem_rdata=0; mem_error_code=0",
            "current_probe_diagnostics": "打印 layer/op/input_count、两路 source 的 kind/base/length/NCHW、output allocation/write ownership、activation/weight layer/T23 base-count/decoded channel/mq index/channel total，以及 header/source/output/op-specific 每项 descriptor_valid 子谓词。",
            "error_snapshot": "negedge 捕获首个非零 operator/memory error 的 state/layer/op/output index、start/selected/result/conv状态、request/response、memory总线及CSR elapsed；error后negedge+1ns打印快照。",
            "snapshot_source_status": "sim_run10 捕获 CSR 置错前成功码0/operator码6错配；sim_run11 绑定修复版 RTL/probe 并通过首个 layer0 输出。",
            "success_criteria": [
                "真实 CSR start 被接受且 backend 经过 layer0 CONV dispatch/start",
                "首个 layer0 conv result 成功握手",
                "layer0 输出地址对应的 memory write 成功握手",
            ],
            "scope": "仅首个 layer0 输出元素；不验证其余层、整网输出或 109 输入一致性。",
        },
        "checks_passed": passed,
        "checks_failed": failures,
        "sha256": {
            "test_script": sha256(Path(__file__).resolve()),
            "backend_module": sha256(MODULE_PATH),
            "descriptor_package": sha256(PACKAGE_PATH),
            "conv_engine_contract": sha256(CONV_ENGINE_PATH),
            "deadline_bench": sha256(DEADLINE_BENCH_PATH),
            "layer0_probe_bench": sha256(LAYER0_PROBE_PATH),
            "csr_deadline_contract": sha256(CSR_PATH),
        },
        "limitations": [
            "sim_run07 仅通过 deadline 接口联合验证；bench 冻结 backend 后注入 terminal event，不证明真实 backend 的 38 层整网执行或 memory 协议周期行为。",
            "sim_run08 的 CONV descriptor_fault 已通过分支结构修复；sim_run10 定位成功码0错误映射，sim_run11 证明修复版真实 backend 首个 layer0 输出通过。",
            "动态覆盖只到首个 layer0 输出元素；其余层、38 层整网运行和 109 输入一致性仍未验证。",
        ],
    }
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
    print(json.dumps({"status": summary["status"], "passed": len(passed),
                      "failed": len(failures), "summary": str(SUMMARY_PATH)},
                     ensure_ascii=False))
    if failures:
        for failure in failures:
            print(f"FAIL {failure['check']}: {failure['reason']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
