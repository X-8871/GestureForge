#!/usr/bin/env python
"""S4-B 硬件门禁就绪机检（只读，不接触板卡）。

目的
----
把「板卡已上电」与「可以正式开跑」用机器可读的方式分开。板卡上电、工作树写权交接、
口头同意都不构成授权；授权来自 main OFFER + w4 CLAIM 与八类门禁记录。

判定权归属
----------
八类门禁的**唯一权威**是 `s4b_ps_tensor_adapter.validate_hardware_gates`。本脚本不复制
它的字段语义，只做三件事：
1. 载入并重算 adapter 准备清单（`validate_preparation`）；
2. 把门禁记录目录交给 adapter 校验，原样转述其 `missing`；
3. 额外取证本预检独有的**结构性依赖**（地址图批准状态、owner 决策状态、
   main OFFER / w4 CLAIM 是否在库、串口与 hw_server 当前观测）。

本脚本只读：读 git（只读命令）、读 JSON、读注册表串口枚举、读进程表。
不加载位流、不打开串口、不启动 hw_server/xsdb、不写任何被审文件。

fail-closed
-----------
- 任一依赖未满足或 adapter 判定不允许 → `BLOCKED`，不推断、不补默认；
- 记录「存在」不等于「有效」，有效性一律由 adapter 判定；
- 结论只有 `READY` / `BLOCKED`；`READY` 仍需执行时现场复核独占会话，且不含任何板级结果。

退出码：0 = READY；1 = BLOCKED；2 = 输入/环境错误。
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import ModuleType
from typing import Any

TZ_UTC8 = timezone(timedelta(hours=8))
CHECKER_VERSION = "r02"

OFFER_MARKER = "S4-B-REAL-02B::s4b_hardware_session_handoff"
CLAIM_MARKER = "S4-B-REAL-02B::s4b_hardware_session_claim"
EXPECTED_SCOPE = "S4B_PS_TENSOR_DIAGNOSTIC"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"无法解析 JSON：{path}：{exc}") from exc


def git_text(repo: Path, *args: str) -> tuple[int, str]:
    proc = subprocess.run(["git", "--no-optional-locks", "-C", str(repo), *args],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.returncode, proc.stdout


def load_adapter(path: Path) -> ModuleType:
    """按文件路径载入 adapter 模块，复用其门禁判定而不复制语义。"""
    spec = importlib.util.spec_from_file_location("s4b_ps_tensor_adapter", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"无法构造 adapter 模块规格：{path}")
    module = importlib.util.module_from_spec(spec)
    # dataclass 在 from __future__ import annotations 下需要模块已登记在 sys.modules，
    # 否则解析注释时拿不到模块字典。
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(spec.name, None)
        raise
    return module


def state_record(worktree: Path, ref: str, state_rel: str, marker: str) -> dict[str, Any]:
    """从指定 git 修订的 STATE 中取包含 marker 的行，并绑定 commit 与 blob SHA。"""
    code, commit = git_text(worktree, "rev-parse", ref)
    if code != 0 or not commit.strip():
        return {"present": False, "reason": f"无法解析修订 {ref}"}
    commit = commit.strip()
    code, blob = git_text(worktree, "show", f"{commit}:{state_rel}")
    if code != 0:
        return {"present": False, "reason": f"{commit} 中不存在 {state_rel}"}
    lines = [line for line in blob.splitlines() if marker in line]
    if not lines:
        return {"present": False, "commit": commit,
                "reason": f"{commit}:{state_rel} 中没有 {marker}"}
    return {
        "present": True,
        "commit": commit,
        "state_path": state_rel,
        "blob_sha256": hashlib.sha256(blob.encode("utf-8")).hexdigest(),
        "line_count": len(lines),
        "unique": len(lines) == 1,
        "excerpt": lines[0][:400],
    }


def com_ports() -> list[str]:
    """从注册表读取当前串口枚举（只读）。"""
    try:
        import winreg
    except ImportError:  # 非 Windows
        return []
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM")
    except OSError:
        return []
    ports: list[str] = []
    try:
        index = 0
        while True:
            try:
                _, value, _ = winreg.EnumValue(key, index)
            except OSError:
                break
            ports.append(str(value))
            index += 1
    finally:
        key.Close()
    return sorted(ports)


def hw_server_running() -> bool:
    """只读进程表判定 hw_server 是否在跑。"""
    proc = subprocess.run(["tasklist", "/FI", "IMAGENAME eq hw_server.exe"],
                          capture_output=True, text=True, errors="replace")
    return "hw_server.exe" in proc.stdout


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    worktree = Path(args.worktree).resolve()
    main_repo = Path(args.main_repo).resolve()
    adapter_path = worktree / "scripts/stage4_s4b/s4b_ps_tensor_adapter.py"
    adapter = load_adapter(adapter_path)
    adapter_sha = sha256_file(adapter_path)

    preparation_path = Path(args.preparation).resolve()
    if not preparation_path.is_file():
        raise ValueError(f"adapter 准备清单不存在：{preparation_path}")
    prepared = adapter.validate_preparation(preparation_path)
    identity = prepared.data.get("artifact_identity") or {}
    identity_sha = str(prepared.data.get("artifact_identity_sha256", ""))

    # 门禁记录：只把实际存在的文件按 adapter 要求的 path+sha256 绑定交给它；缺的它会报 record_missing
    gate_dir = Path(args.gate_dir).resolve() if args.gate_dir else None
    gate_files: dict[str, dict[str, str]] = {}
    for role in adapter.REQUIRED_GATE_RECORDS:
        candidate = (gate_dir / f"{role}.json") if gate_dir else None
        if candidate and candidate.is_file():
            gate_files[role] = {"path": str(candidate), "sha256": sha256_file(candidate)}
    gate = adapter.validate_hardware_gates(prepared, args.hardware_run_id, gate_files)

    address_map = load_json(worktree / "docs/stage4/S4B_stage4_address_map.json")
    ownership = load_json(worktree / "docs/stage4/s4b_raw_address_ownership_proposal_20261024_r01.json")
    offer = state_record(main_repo, args.main_ref, ".codex/STATE.md", OFFER_MARKER)
    claim = state_record(worktree, args.claim_ref, ".codex/STATE.md", CLAIM_MARKER)
    ports = com_ports()

    dependencies = {
        "address_map": {
            "status": address_map.get("status"),
            "path": "docs/stage4/S4B_stage4_address_map.json",
            "exists": (worktree / "docs/stage4/S4B_stage4_address_map.json").is_file(),
            "ok": address_map.get("status") == "APPROVED",
            "blocks": ["g0_approval"],
        },
        "shared_address_map": (lambda q: {
            "path": "docs/stage4/S4B_shared_address_map.json",
            "exists": q.is_file(),
            "status": (load_json(q).get("status") if q.is_file() else "FILE_ABSENT"),
            "ok": q.is_file() and str(load_json(q).get("status")) == "APPROVED",
            "blocks": ["g0_approval"],
        })(worktree / "docs/stage4/S4B_shared_address_map.json"),
        "raw_address_ownership": {
            "status": ownership.get("status"),
            "path": "docs/stage4/s4b_raw_address_ownership_proposal_20261024_r01.json",
            "ok": str(ownership.get("status")) in {"APPROVED", "CLOSED", "DECIDED"},
            # 纠错：adapter 的 g0 判定只校验 address_map / shared_address / timebase 三份文件，
            # 不读本提案（见 adapter 内无 raw_address/ownership 引用）。故本提案不 blocks g0。
            # 它真正控制的是 raw_frame/raw_meta 的 FROZEN 迁移与 mailbox/RAW 路径启用。
            "blocks": [],
            "affects": ["raw_frame/raw_meta 迁移至 FROZEN_STAGE4", "mailbox/RAW 路径启用"],
            "open_decisions": [d.get("id") for d in (ownership.get("decision_request") or [])],
            "note": ("仍未裁决（DECISION_REQUESTED）。其选项集为 A/C/B/E，与本轮 Wong 对地址图选的 "
                     "A/B/C 方向方案**不是同一组**：该提案的 B 指『4-D 输入降为 107 帧预冻结子集』。"),
        },
        "main_offer": {**offer, "ok": offer["present"] and offer.get("unique") is True,
                       "blocks": ["hardware_session_handoff"]},
        "w4_claim": {**claim, "ok": claim["present"] and claim.get("unique") is True,
                     "blocks": ["hardware_session_handoff"]},
        "live_session": {
            "hw_server_running": hw_server_running(),
            "com_ports": ports,
            "expect_uart": args.expect_uart,
            "uart_present": args.expect_uart in ports if args.expect_uart else None,
            "ok": False,  # 独占会话必须在执行时由持有者现场证明，预检不得代替
            "blocks": ["exclusive_session"],
            "note": "预检只观测当前状态；exclusive_session 需执行时现场核对，30 分钟有效窗口",
        },
    }

    dep_blockers = {role: [] for role in adapter.REQUIRED_GATE_RECORDS}
    for name, dep in dependencies.items():
        if dep["ok"]:
            continue
        for role in dep["blocks"]:
            dep_blockers[role].append(f"dependency_not_met:{name}")

    adapter_missing = list(gate.missing)
    all_blockers = adapter_missing + sorted({b for rows in dep_blockers.values() for b in rows})
    blocked = bool(all_blockers) or not gate.allowed

    next_actions: list[str] = []
    if not dependencies["address_map"]["ok"]:
        next_actions.append(
            "关闭 G-01：S4B_stage4_address_map.json 由 DRAFT_PENDING_REVIEW 推进到 APPROVED"
            "（需独立复审引用被审 SHA），否则 g0_approval 结构上不可能通过")
    if not dependencies["raw_address_ownership"]["ok"]:
        next_actions.append(
            "Wong 裁决 s4b_raw_address_ownership_proposal（当前 DECISION_REQUESTED）并落盘")
    if not dependencies["main_offer"]["ok"]:
        next_actions.append(
            f"main 发正式 OFFER：{OFFER_MARKER}；scope={EXPECTED_SCOPE}；证据入口 hardware_run_id=<完整RunId>")
    if not dependencies["w4_claim"]["ok"]:
        next_actions.append(
            "OFFER 落库后由 w4 写 CLAIM（六键：offer_commit/offer_blob_oid/offer_sha256/"
            "offer_source_commit/hardware_run_id/scope）")
    for item in adapter_missing:
        role = item.split(":", 1)[0]
        if role == "command_delivery_review":
            next_actions.append(
                f"对当前 adapter 字节 {adapter_sha[:16]}… 重新独立复审并落 command_delivery_review")
        elif role == "operator_authorization":
            next_actions.append(
                "补 operator_authorization（authorized_by 可为 Wong 或阶段4 负责人；须含精确 diagnostic 操作集与有效期）")
        elif role == "cold_basis":
            next_actions.append("补 cold_basis（物理断电重建或等价的冷生命周期独立证明）")
        elif role in {"timing_freeze", "range_reservation", "exclusive_session", "g0_approval"}:
            next_actions.append(f"补 {role}（须绑定本轮 artifact_identity 与硬件 RunId）")

    return {
        "schema_version": "s4b_hw_gate_readiness_v2",
        "checker_version": CHECKER_VERSION,
        "checker_sha256": sha256_file(Path(__file__)),
        "task_id": "S4-B-HW-GATE-READINESS",
        "run_id": args.run_id,
        "generated_utc8": datetime.now(TZ_UTC8).isoformat(timespec="seconds"),
        "scope": "只读门禁就绪机检；不加载位流、不开串口、不启动 hw_server/xsdb",
        "hardware_run_id_candidate": args.hardware_run_id,
        "adapter": {"path": str(adapter_path), "sha256": adapter_sha},
        "preparation": {
            "path": str(preparation_path),
            "sha256": sha256_file(preparation_path),
            "artifact_identity_sha256": identity_sha,
            "elf_sha256": identity.get("elf_sha256"),
            "derived_source_sha256": identity.get("derived_source_sha256"),
        },
        "dependencies": dependencies,
        "authoritative_gate_check": {
            "authority": "s4b_ps_tensor_adapter.validate_hardware_gates",
            "allowed": gate.allowed,
            "missing": adapter_missing,
            "gate_files_supplied": sorted(gate_files),
            "dependency_blockers": {k: v for k, v in dep_blockers.items() if v},
        },
        "blockers": all_blockers,
        "verdict": "BLOCKED" if blocked else "READY",
        "hardware_execution": "NOT_RUN",
        "next_actions": next_actions,
        "boundaries": [
            "READY 只表示记录与依赖齐备，仍不等于门内检查项通过；",
            "板卡上电、工作树写权交接、口头同意均不构成授权；",
            "本预检不含任何板级结果，不得用于声称 G3/G4/G5。",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S4-B 硬件门禁就绪机检（只读）")
    parser.add_argument("--run-id", required=True, help="本次机检 RunId（证据目录名）")
    parser.add_argument("--worktree", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--main-repo", default=r"D:\FPGA_Competition")
    parser.add_argument("--main-ref", default="HEAD", help="读取 OFFER 的 main 修订")
    parser.add_argument("--claim-ref", default="HEAD", help="读取 CLAIM 的 w4 修订")
    parser.add_argument("--preparation", required=True, help="adapter 离线准备清单路径")
    parser.add_argument("--hardware-run-id", required=True, help="拟用于硬件执行的 RunId 候选")
    parser.add_argument("--gate-dir", default=None, help="八类门禁记录目录（缺省视为全缺）")
    parser.add_argument("--expect-uart", default="COM4", help="预期串口（仅用于观测核对）")
    parser.add_argument("--evidence-dir", required=True, help="证据输出目录（必须是新 RunId）")
    args = parser.parse_args(argv)

    out_dir = Path(args.evidence_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        print(f"[ERROR] 证据目录已存在且非空：{out_dir}", file=sys.stderr)
        return 2

    try:
        report = build_report(args)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"[ERROR] 输入或环境错误：{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "gate_readiness.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    files = [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha256_file(p)}
             for p in sorted(out_dir.iterdir()) if p.is_file()]
    exit_code = 0 if report["verdict"] == "READY" else 1
    (out_dir / "manifest.json").write_text(json.dumps({
        "schema_version": 1, "task_id": report["task_id"], "run_id": args.run_id,
        "generated_utc8": report["generated_utc8"], "verdict": report["verdict"],
        "exit_code": exit_code, "files": files, "scope": report["scope"],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[{report['verdict']}] exit={exit_code} 阻断项={len(report['blockers'])}")
    for item in report["blockers"]:
        print(f"  - {item}")
    return exit_code


if __name__ == "__main__":
    # 任何未预期异常都归为输入/环境错误（exit 2），不得伪装成「受阻」（exit 1）。
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as exc:  # noqa: BLE001 - 兜底，避免异常逃逸成非契约退出码
        print(f"[ERROR] 未预期错误：{type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(2)
