#!/usr/bin/env python3
"""从候选 Git 对象恢复与历史 OOC 字节一致的隔离 RTL，并只读复核绑定。"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path, PurePosixPath


RUN_ID = "xc7z020_2_ooc_20261008_r01"
COMMIT = "999238284157bed77cdb3a37e3e6eea52daeefc4"
TREE = "b77b0ae5e1f49d2b7ab1c217f09edaedcbf5ea67"
TILE_SHA256 = "76ca735b14802e26f0a4b016989e13b43cf8bd904587ccea37651c757d089300"
ROOT = Path(r"D:\FPGA_Competition")
EVIDENCE_REL = PurePosixPath("report/evidence/S2A-T68") / RUN_ID
CACHE_REL = PurePosixPath("tmp/stage2a/S2A-T68") / RUN_ID
OLD_REL = PurePosixPath(
    "report/evidence/S2A-T68/g4_synthesis_20261005/"
    "candidate8x8_core_ooc_run01_20261006"
)
INTERFACE_REL = PurePosixPath(
    "docs/obsidian-project/04-提交材料/阶段验收/"
    "S2A-T01_模型交付规格与G0接口冻结.md"
)
INTERFACE_SHA256 = "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230"
APPROVAL_REL = PurePosixPath(
    "report/evidence/S2A-T68/stage2a_g4_g5_acceptance_20261005.md"
)


def now_local() -> str:
    """返回南京时区的可复核时间。"""
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exact_path(relative: str | PurePosixPath, kind: str) -> Path:
    """在已确认根目录内核对逐级精确名称和目标类型。"""
    parts = PurePosixPath(relative).parts
    if not parts or any(part in {".", ".."} for part in parts):
        raise ValueError(f"无效相对路径：{relative}")
    path = ROOT
    for part in parts:
        if part not in {item.name for item in path.iterdir()}:
            raise FileNotFoundError(f"精确名称不存在：{path / part}")
        path = path / part
        if path.is_symlink():
            raise ValueError(f"不接受符号链接：{path}")
    if kind == "file" and not path.is_file():
        raise ValueError(f"目标不是文件：{path}")
    if kind == "directory" and not path.is_dir():
        raise ValueError(f"目标不是目录：{path}")
    return path


def git(*arguments: str) -> bytes:
    """通过 Git 对象读取冻结内容，避免消费共享工作区源码。"""
    result = subprocess.run(
        ["git", "-C", str(ROOT), *arguments],
        check=True, capture_output=True,
    )
    return result.stdout


def write_new_json(path: Path, data: dict) -> None:
    """只创建新证据，已存在的运行文件不得覆盖。"""
    if path.name in {item.name for item in path.parent.iterdir()}:
        raise FileExistsError(f"拒绝覆盖既有运行文件：{path}")
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def load_old() -> tuple[dict, Path]:
    """核对历史清单与候选提交/树，保留其原始字节哈希。"""
    if not ROOT.is_dir() or ROOT.name != "FPGA_Competition":
        raise ValueError(f"已确认根目录不可用：{ROOT}")
    path = exact_path(OLD_REL / "source_manifest.json", "file")
    old = json.loads(path.read_text(encoding="utf-8"))
    if old["candidate_commit"] != COMMIT or old["candidate_tree"] != TREE:
        raise ValueError("历史 OOC 清单提交/树与任务候选不一致")
    if git("rev-parse", f"{COMMIT}^{{tree}}").decode("ascii").strip() != TREE:
        raise ValueError("Git 实际候选树与绑定不一致")
    if len(old["rtl_sources"]) != 14:
        raise ValueError("历史 OOC 闭包不是 14 个 RTL")
    interface = exact_path(INTERFACE_REL, "file")
    if sha256(interface.read_bytes()) != INTERFACE_SHA256:
        raise ValueError("T01 正式冻结文档哈希已变化")
    return old, path


def recover_bytes(item: dict) -> tuple[bytes, dict]:
    """仅在历史 SHA 和字节数证实后显式还原 CRLF。"""
    relative = item["relative_path"]
    if not relative.startswith("src/") or ".." in PurePosixPath(relative).parts:
        raise ValueError(f"闭包源路径越界：{relative}")
    blob = git("rev-parse", f"{COMMIT}:{relative}").decode("ascii").strip()
    if blob != item["git_blob"]:
        raise ValueError(f"候选 Git blob 与历史闭包不一致：{relative}")
    raw = git("cat-file", "blob", blob)
    raw.decode("utf-8")
    candidates = [("identity", raw)]
    restored_offsets: list[int] = []
    if b"\r" not in raw:
        candidates.append(("LF_to_CRLF_verified_against_historical_OOC", raw.replace(b"\n", b"\r\n")))
        if relative == "src/s2a_stage2a_core_ooc.sv":
            # 历史顶层仅第 59/137 行使用 CRLF；9316 种双 CR 组合仅此项匹配历史 SHA。
            restored_offsets = [2220, 5430]
            if all(offset < len(raw) and raw[offset] == 10 for offset in restored_offsets):
                first, second = restored_offsets
                mixed = raw[:first] + b"\r" + raw[first:second] + b"\r" + raw[second:]
                candidates.append(("two_mixed_CRLF_verified_against_historical_OOC", mixed))
    matching = [(name, data) for name, data in candidates
                if sha256(data) == item["sha256"] and len(data) == item["bytes"]]
    if not matching:
        raise ValueError(f"Git 字节及显式 CRLF 还原均不能匹配历史 OOC：{relative}")
    transform, exported = matching[0]
    if relative == "src/s2a_conv_tile_engine.sv" and sha256(exported) != TILE_SHA256:
        raise ValueError("tile 源码未匹配冻结 SHA")
    record = {
        "relative_path": relative, "git_blob": blob,
        "git_object_sha256": sha256(raw), "git_object_bytes": len(raw),
        "historical_ooc_sha256": item["sha256"], "historical_ooc_bytes": item["bytes"],
        "export_transform": transform,
        "exported_sha256": sha256(exported), "exported_bytes": len(exported),
        "git_lf_count": raw.count(b"\n"), "git_crlf_count": raw.count(b"\r\n"),
        "exported_lf_count": exported.count(b"\n"),
        "exported_crlf_count": exported.count(b"\r\n"),
        "explicit_restored_lf_offsets": restored_offsets if transform.startswith("two_mixed") else [],
    }
    return exported, record


def prepare() -> dict:
    """创建一次性隔离源快照、运行计划和来源绑定。"""
    old, old_path = load_old()
    evidence = exact_path(EVIDENCE_REL, "directory")
    cache = exact_path(CACHE_REL, "directory")
    output_names = ["source_manifest.json", "source_binding_result.json", "run_plan.json"]
    existing = {item.name for item in evidence.iterdir()}
    if any(name in existing for name in output_names) or (cache / "sources").exists():
        raise FileExistsError("本 RunId 已准备过，拒绝覆盖源码或证据")
    recovered = [recover_bytes(item) for item in old["rtl_sources"]]
    sources = cache / "sources"
    sources.mkdir()
    (sources / "src").mkdir()
    records = []
    for data, record in recovered:
        target = sources.joinpath(*PurePosixPath(record["relative_path"]).parts)
        with target.open("xb") as stream:
            stream.write(data)
        if sha256(target.read_bytes()) != record["historical_ooc_sha256"]:
            raise ValueError(f"写入后字节哈希不一致：{target}")
        record["exported_path"] = str(target)
        record["exported_repo_relative_path"] = target.relative_to(ROOT).as_posix()
        records.append(record)
    approval = exact_path(APPROVAL_REL, "file")
    manifest = {
        "schema": "s2a-xc2-ooc-source-manifest-v1", "run_id": RUN_ID,
        "created_at_local": now_local(), "repo_root": str(ROOT),
        "candidate_commit": COMMIT, "candidate_tree": TREE,
        "top": "s2a_stage2a_core_ooc", "rtl_source_count": len(records),
        "historical_source_manifest": {
            "path": OLD_REL.joinpath("source_manifest.json").as_posix(),
            "sha256": sha256(old_path.read_bytes()),
        },
        "source_origin": "git cat-file blob；不读取共享 src 工作区文件",
        "all_exported_bytes_equal_historical_ooc": True,
        "interface_binding": {
            "name": "T01 阶段2A CSR、单 word memory、timeout 与握手协议",
            "version": "G0_FROZEN_2026-09-23", "frozen": True,
            "path": INTERFACE_REL.as_posix(), "sha256": INTERFACE_SHA256,
        },
        "approval_binding": {
            "path": APPROVAL_REL.as_posix(), "sha256": sha256(approval.read_bytes()),
            "scope": "既有 T01 冻结、8×8/8-lane 批准与 Stage2A G4/G5；本补验须另经独立审查",
        },
        "rtl_sources": records,
    }
    write_new_json(evidence / "source_manifest.json", manifest)
    manifest_sha = sha256((evidence / "source_manifest.json").read_bytes())
    script = exact_path(EVIDENCE_REL / "run_synthesis.tcl", "file")
    binding = {
        "schema": "s2a-xc2-ooc-source-binding-result-v1", "run_id": RUN_ID,
        "status": "PASS_14_GIT_BLOBS_TO_HISTORICAL_OOC_BYTES",
        "created_at_local": now_local(), "candidate_commit": COMMIT, "candidate_tree": TREE,
        "source_manifest_sha256": manifest_sha, "rtl_source_count": len(records),
        "same_source_closure_as_historical_ooc": True,
        "identity_exports": sum(row["export_transform"] == "identity" for row in records),
        "explicit_full_lf_to_crlf_exports": sum(row["export_transform"].startswith("LF_to_CRLF") for row in records),
        "explicit_mixed_crlf_exports": sum(row["export_transform"].startswith("two_mixed") for row in records),
        "top_wrapper_mixed_crlf_diagnosis": {
            "git_bytes": 5431, "historical_ooc_bytes": 5433,
            "checked_two_cr_combinations": 9316, "unique_matching_combinations": 1,
            "restored_lf_offsets": [2220, 5430], "restored_line_numbers": [59, 137],
            "initial_preparation_failed_before_source_or_manifest_creation": True,
        },
        "shared_src_read": False, "verification_commands": [
            "git rev-parse <candidate>:<relative_path>", "git cat-file blob <git_blob>",
            "SHA-256 和字节数逐项精确匹配历史 source_manifest.json",
        ],
        "limitations": ["仅证明同源及历史字节精确恢复，不证明综合或功能通过。"],
    }
    write_new_json(evidence / "source_binding_result.json", binding)
    plan = {
        "schema": "s2a-xc2-ooc-run-plan-v1", "run_id": RUN_ID,
        "created_at_local": now_local(), "stage": "2A", "task_id": "S2A-T68",
        "candidate_commit": COMMIT, "candidate_tree": TREE,
        "evidence_dir": str(evidence), "cache_dir": str(cache),
        "source_manifest_sha256": manifest_sha,
        "run_synthesis_tcl_sha256": sha256(script.read_bytes()),
        "prepare_sources_py_sha256": sha256(Path(__file__).read_bytes()),
        "top": "s2a_stage2a_core_ooc", "user_confirmed_device": "XC7Z020-2CLG400I",
        "part_selection": "主控 get_parts 实际解析后设置 ::s2a_target_part；本脚本不猜测器件名称",
        "python_executable": sys.executable,
        "synthesis_command": "synth_design -top s2a_stage2a_core_ooc -part $resolved_part -mode out_of_context -flatten_hierarchy none",
        "launch_command": "set ::s2a_target_part {<target_resolution.json 的实际 resolved_part>}; source {<本目录 run_synthesis.tcl>}",
        "vivado_max_threads": 2, "clock_constraints": [], "xdc_files": [],
        "expected_duration_seconds": {"minimum": 140, "planning_upper": 900},
        "duration_basis": "历史同源 OOC 实际 140 秒；MCP 与本机负载可能改变耗时。",
        "operating_conditions_command": "set_operating_conditions -grade industrial",
        "operating_conditions_scope": "功耗与环境分析设置，不冻结温度数值，不证明工业温度时序。",
        "reports": ["utilization.rpt", "utilization_hierarchical.rpt", "timing_summary.rpt", "clocks.rpt", "worst_paths.rpt", "operating_conditions.rpt"],
        "latch_checks": ["PRIMITIVE_SUBGROUP=LATCH/latch", "可用时 IS_LATCH", "REF_NAME=LDCE", "REF_NAME=LDPE"],
        "latch_property_basis": [
            "https://docs.amd.com/r/en-US/ug953-vivado-7series-libraries/LDCE",
            "https://docs.amd.com/r/en-US/ug953-vivado-7series-libraries/LDPE",
        ],
        "stop_conditions": ["源码/器件绑定不符", "OOM 或综合错误", "报告生成失败", "锁存器非零", "主控观察到约定 10 分钟无进度超时"],
        "no_progress_watchdog": "由主控观察 MCP/进程；脚本不能中断或关闭其他 Vivado 会话。",
        "checkpoint_keep_reason": "保留本次所选器件综合后网表，供资源、锁存器与未约束路径独立复核。",
        "limitations": ["无 XDC/冻结时钟，不产生 timing closure 或频率达标结论。", "不运行实现、板上测试或 109 样本整网回归。"],
    }
    write_new_json(evidence / "run_plan.json", plan)
    return binding


def verify(part: str | None) -> dict:
    """只读校验隔离快照及本次待运行参数。"""
    old, old_path = load_old()
    manifest_path = exact_path(EVIDENCE_REL / "source_manifest.json", "file")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["candidate_commit"] != COMMIT or manifest["candidate_tree"] != TREE:
        raise ValueError("隔离清单候选绑定不一致")
    if manifest["historical_source_manifest"]["sha256"] != sha256(old_path.read_bytes()):
        raise ValueError("历史输入清单在准备后变化")
    if len(manifest["rtl_sources"]) != len(old["rtl_sources"]):
        raise ValueError("隔离源码数量与历史清单不一致")
    for actual, expected in zip(manifest["rtl_sources"], old["rtl_sources"], strict=True):
        recovered, verified = recover_bytes(expected)
        for field in ("relative_path", "git_blob", "git_object_sha256", "export_transform", "exported_sha256"):
            if actual[field] != verified[field]:
                raise ValueError(f"源绑定字段变化：{actual['relative_path']} / {field}")
        path = exact_path(actual["exported_repo_relative_path"], "file")
        if str(path) != actual["exported_path"] or path.read_bytes() != recovered:
            raise ValueError(f"实际隔离源码与冻结字节不一致：{path}")
    plan = json.loads(exact_path(EVIDENCE_REL / "run_plan.json", "file").read_text(encoding="utf-8"))
    if plan["source_manifest_sha256"] != sha256(manifest_path.read_bytes()):
        raise ValueError("运行计划源清单哈希不一致")
    for name, field in (("run_synthesis.tcl", "run_synthesis_tcl_sha256"), ("prepare_sources.py", "prepare_sources_py_sha256")):
        if sha256(exact_path(EVIDENCE_REL / name, "file").read_bytes()) != plan[field]:
            raise ValueError(f"运行脚本准备后变化：{name}")
    if part is not None:
        resolution = json.loads(exact_path(EVIDENCE_REL / "target_resolution.json", "file").read_text(encoding="utf-8"))
        if resolution.get("resolved_part") != part:
            raise ValueError("运行 Part 与主控实际器件解析记录不一致")
    return {"status": "PASS_READ_ONLY_14_SOURCE_BINDINGS", "rtl_source_count": 14,
            "part": part, "source_manifest_sha256": sha256(manifest_path.read_bytes())}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--part")
    arguments = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        result = verify(arguments.part) if arguments.verify_only else prepare()
    except Exception as error:
        print(json.dumps({"status": "FAIL_SOURCE_PREPARATION_OR_BINDING", "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
