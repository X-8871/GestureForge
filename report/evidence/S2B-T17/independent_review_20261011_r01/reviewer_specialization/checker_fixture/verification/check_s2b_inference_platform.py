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

PROFILE_VERSION = "s2b-inference-platform/0.1.1"
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
    """核对原14源字节和仅有的模块引用、几何参数常量派生关系。"""
    item = profile["source_derivation"]
    require(set(item) == {"policy", "upstream_freeze_commit", "derivation_baseline_commit",
        "newline_policy", "upstream_sources", "derived_sources"}, "派生绑定字段不符")
    require(item["policy"] == "s2b-constant-geometry/1.0.0" and
        item["upstream_freeze_commit"] == "671f9cf494b92ce182b3f1542fefd0cfd4b209f5" and
        item["derivation_baseline_commit"] == "18c0c34f9da885b5f35869c282dc0c2ed50d720e",
        "派生上游或基线不符")
    require(item["newline_policy"] == "派生源按UTF-8/LF创建；仅比较派生关系时将上游CRLF转为LF；冻结上游SHA始终绑定原字节。",
        "换行政策不符")
    require(item["upstream_sources"] == [{"path": path, "sha256": digest}
        for path, digest in FROZEN_CORE_SHA256.items()], "原14源绑定不符")
    for path, digest in FROZEN_CORE_SHA256.items():
        require(sha256(relative_file(root, path)) == digest, f"冻结2A原件字节变化：{path}")
    require(isinstance(item["derived_sources"], list) and len(item["derived_sources"]) == 4,
        "派生源必须恰为4项")
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
    require(sources == expected_sources, "闭包必须精确为10个冻结2A、4个派生及4个原2B模块")
    script = relative_file(root, "vivado/s2b_inference_platform.tcl").read_text(encoding="utf-8")
    require("variable version 0.1.1" in script, "Tcl平台版本不符")
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
         "board/ps_platform_fields.json", "verification/check_s2b_inference_platform.py"]))
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
