#!/usr/bin/env python3
"""只读核验S2C中间版平台闭包；不继承2B通过结论，不启动Vivado。"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

BASELINE = "9c7cc242147b7d4875164a0a99c008f15610fd0b"
CONTRACT_COMMIT = "756f5828fd1d8356f4f51a21b52554aa1f48d6a7"
CONTRACT = "docs/obsidian-project/02-方案设计/s2c_lane32_bulk_interface_20261030.md"
CONTRACT_SHA256 = "6f7c224f5211bd58c96aa477be5cb764c222cabf293d4b0efbe14049ab43439c"
NEW_SOURCES = ["src/s2c_axi3_bulk_bridge.sv", "src/s2c_hp0_bulk_adapter.sv"]
CHANGED_SOURCES = {
    "src/s2b_conv_tile_engine.sv", "src/s2b_network_backend.sv",
    "src/s2b_stage2b_core.sv", "src/s2b_request_guard.sv",
    "src/s2b_inference_top.sv", *NEW_SOURCES,
}


def require(condition: bool, message: str) -> None:
    """任何声明与实际不一致均拒绝。"""
    if not condition:
        raise ValueError(message)


def git(root: Path, *args: str) -> bytes:
    """只读查询Git内容，禁止混用磁盘换行哈希与blob哈希。"""
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=False)
    require(result.returncode == 0, "Git只读查询失败：" + " ".join(args))
    return result.stdout


def blob(root: Path, commit: str, path: str) -> bytes:
    """读取指定提交原始blob。"""
    return git(root, "cat-file", "blob", commit + ":" + path)


def main() -> int:
    """检查候选身份、冻结未改部分、源码顺序与目标频率。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).absolute().parent.parent)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--visibility-proof", type=Path)
    parser.add_argument("--review", type=Path)
    parser.add_argument("--review-sha256")
    args = parser.parse_args()
    try:
        require(not any((args.visibility_proof, args.review, args.review_sha256)),
                "本候选尚未建立新的可见性受理证据；不接受旧2B证明继承")
        root = args.root.absolute()
        require(root.is_dir(), "工作树不存在")
        # 复用既有精确路径和reparse拒绝规则，不调用旧2B派生字节白名单。
        module_path = root / "verification/check_s2b_inference_platform.py"
        spec = importlib.util.spec_from_file_location("s2c_legacy_path_check", module_path)
        require(spec is not None and spec.loader is not None, "无法读取精确路径检查器")
        legacy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(legacy)
        profile_path = legacy.relative_file(root, "board/s2b_inference_platform.json")
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        require(profile["version"] == "s2c-inference-platform/0.1.0", "候选平台版本不符")
        require(profile["status"] == "BUILD_CANDIDATE", "不得把候选标为已验收")
        require(profile["physical_interface"] == "s2c-physical/0.1.0", "候选物理扩展版本不符")
        require(profile["physical_interface_status"] == "OFFLINE_CANDIDATE_NOT_FROZEN",
                "不得继承冻结/G0通过身份")
        require(profile["physical_interface_document"] == CONTRACT, "契约路径不符")
        require(profile["physical_interface_hash_basis"] == "commit_blob" and
                profile["physical_interface_hash_commit"] == CONTRACT_COMMIT and
                profile["physical_interface_sha256"] == CONTRACT_SHA256, "契约哈希基座不符")
        require(hashlib.sha256(blob(root, CONTRACT_COMMIT, CONTRACT)).hexdigest() == CONTRACT_SHA256,
                "提交内契约blob不符")
        require(git(root, "hash-object", "--path=" + CONTRACT, CONTRACT).strip() ==
                git(root, "rev-parse", CONTRACT_COMMIT + ":" + CONTRACT).strip(),
                "当前契约偏离已审查提交")
        require(profile["clock_hz"] == 100_000_000 and profile["visibility_default"] == 0,
                "候选目标频率或默认可见性门控不符")
        require(profile["candidate_generics"] == {"CONV_OUTPUT_LANES": 32, "ENABLE_BULK": 1},
                "候选构建未启用32lane及bulk")
        require(profile["vivado_part"] == "xc7z020clg400-2" and
                profile["requested_part_literal"] == "XC7Z020-2CLG400I", "器件身份不符")
        require(profile["evidence_reuse_policy"] ==
                "NO_PASS_INHERITANCE_FOR_EXISTING_XSA_ELF_OR_T19_EVIDENCE",
                "不得继承旧部署/通过结论")
        require(profile["visibility_binding_only"] is True, "机器绑定不能代替语义审查")
        previous = json.loads(blob(root, BASELINE, "board/s2b_inference_platform.json"))
        for name in ("control", "memory", "physical_ports", "prior_cache_probe", "build_scripts",
                     "ps_profile", "ps_profile_script"):
            require(profile[name] == previous[name], "未授权修改基础平台字段：" + name)
        expected = list(previous["rtl_sources"])
        insert_at = expected.index("src/s2b_hp0_word_adapter.sv") + 1
        expected[insert_at:insert_at] = NEW_SOURCES
        require(profile["rtl_sources"] == expected and len(expected) == 21,
                "源码闭包/顺序不是指定21项")
        script = legacy.relative_file(root, "vivado/s2b_inference_platform.tcl").read_text(encoding="utf-8")
        source_block = re.search(r"variable rtl_sources \{(.*?)\n    \}", script, re.S)
        require(source_block is not None and source_block.group(1).split() == expected,
                "Tcl与JSON源码顺序不一致")
        for token in ("variable version 0.2.0", "CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ 100",
                      "CONFIG.FREQ_HZ 100000000", "CONFIG.CONV_OUTPUT_LANES 32 CONFIG.ENABLE_BULK 1",
                      "verification/check_s2c_inference_platform.py"):
            require(token in script, "构建脚本缺少候选约束：" + token)
        require("make_wrapper -files $bd_file -top -import" in script and
                "set wrapper [get_files */${bd_name}_wrapper.v]" in script,
                "wrapper恢复方式被改变")
        top = legacy.relative_file(root, "src/s2b_inference_top.sv").read_text(encoding="utf-8")
        require(top.count("FREQ_HZ 100000000") == 3 and "FREQ_HZ 50000000" not in top,
                "顶层时钟/总线频率标注不一致")
        for token in ("parameter bit PROFILE_VISIBILITY_PROVEN = 1'b0",
                      "parameter integer CONV_OUTPUT_LANES = 8", "parameter bit ENABLE_BULK = 1'b0",
                      "s2c_hp0_bulk_adapter", ".ledger_empty_next(ledger_empty_next)",
                      ".visibility_confirmed(PROFILE_VISIBILITY_PROVEN)",
                      ".core_mem_valid(mem_valid || (ENABLE_BULK && bulk_cmd_valid))"):
            require(token in top, "顶层兼容/账本约束缺失：" + token)
        rows = []
        for path in expected + ["board/ps_platform_fields.json", "vivado/s2b_ps_platform.tcl"]:
            target = legacy.relative_file(root, path)
            unchanged = path not in CHANGED_SOURCES
            if unchanged:
                require(git(root, "hash-object", "--path=" + path, path).strip() ==
                        git(root, "rev-parse", BASELINE + ":" + path).strip(),
                        "冻结未改模块出现变化：" + path)
            rows.append({"path": path, "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                         "hash_basis": "worktree_disk", "unchanged_from_baseline": unchanged})
        report = {"status": "STATIC_CLOSURE_ONLY", "baseline_commit": BASELINE,
                  "clock_target_hz": profile["clock_hz"], "visibility": 0,
                  "sources_count": len(expected), "sources": rows,
                  "limitations": ["不验证RTL功能/独立审查批准/综合时序/板级结果。",
                                  "候选变化文件另由运行证据和独立代码审查绑定。"]}
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print("S2C_PLATFORM_STATIC:OK visibility=0 rtl_sources=21; 仅静态闭包，不代表功能/时序/实板")
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("S2C_PLATFORM_STATIC:FAIL " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
