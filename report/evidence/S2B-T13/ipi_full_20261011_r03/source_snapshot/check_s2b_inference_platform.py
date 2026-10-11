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


def check_static(root: Path) -> dict:
    """仅确认可恢复输入和公开口约束，不替代 IPI/RTL 审查。"""
    profile = read_json(root / "board/s2b_inference_platform.json")
    require(profile["version"] == "s2b-inference-platform/0.1.0", "平台版本不符")
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
    require(len(sources) == 18 and len(set(sources)) == 18, "闭包应为14个冻结2A模块与4个2B模块")
    script = relative_file(root, "vivado/s2b_inference_platform.tcl").read_text(encoding="utf-8")
    block = re.search(r"variable rtl_sources \{(.*?)\n    \}", script, re.S)
    require(block is not None and block.group(1).split() == sources, "Tcl/JSON源码闭包不一致")
    wrapper = relative_file(root, "src/s2b_inference_top.sv").read_text(encoding="utf-8")
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
    files = sources + profile["build_scripts"] + ["board/s2b_inference_platform.json",
        "board/ps_platform_fields.json", "verification/check_s2b_inference_platform.py"]
    return {path: sha256(relative_file(root, path)) for path in files}


def check_visibility(root: Path, proof_path: Path, review_path: Path, sources: dict, review_sha256: str) -> None:
    """只检查固定审查原件和证据绑定；独立来源与语义必须由总控核查。"""
    proof = read_json(proof_path)
    review = read_json(review_path)
    require(re.fullmatch(r"[0-9a-f]{64}", review_sha256 or "") is not None,
        "需要总控从独立 Reviewer 真来源冻结的审查原件 SHA-256")
    require(sha256(exact_file(review_path)) == review_sha256, "审查原件与固定哈希不符")
    require(proof.get("schema_version") == 1 and proof.get("status") == "PASS", "可见性证明未通过")
    require(proof.get("profile_version") == "s2b-inference-platform/0.1.0", "证明平台版本不符")
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
