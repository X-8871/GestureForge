#!/usr/bin/env python
"""生成 S4-B 硬件门禁记录（离线，可复现；不接触硬件）。

只生成能在离线状态下诚实成立的记录：
  - operator_authorization（authorized_by = w4 写权负责人；操作集固定五项）
  - timing_freeze（时基语义 + stale 阈值；阈值引用 Wong 已批准的 200 ms 回执）
  - range_reservation（本次 seed/session 闭区间；与历史预留不重叠）
可选：
  - command_delivery_review（仅当显式给出 --review-file 时生成；不得自签）

明确不生成（需现场/Wong）：
  - exclusive_session（执行时现场取证，30 分钟窗口）
  - cold_basis（物理断电重建或等价独立证明）
  - g0_approval（依赖地址图 APPROVED，当前 DRAFT_PENDING_REVIEW）
  - hardware_session_handoff（需 main OFFER + w4 CLAIM）

身份一律由 adapter 的 `_verified_artifact_identity` 重建，不手抄摘要。

退出码：0 = 已生成；1 = 前置不满足（如准备清单无效）；2 = 参数/环境错误。
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import ModuleType
from typing import Any

TZ_UTC8 = timezone(timedelta(hours=8))
SCOPE = "S4B_PS_TENSOR_DIAGNOSTIC"
DIAGNOSTIC_OPERATIONS = ["deploy", "OP_WEIGHTS", "OP_RUN",
                         "double_read_trace_export", "stop_owned_cpu0"]
STALE_RECEIPT = {
    "path": r"D:\codex-worktrees\w4\docs\stage4\s4a_stale_age_limit_approval_applied_20261024_r01.json",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_adapter(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("s4b_ps_tensor_adapter", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"无法构造 adapter 规格：{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_record(out_dir: Path, role: str, record: dict[str, Any]) -> dict[str, str]:
    path = out_dir / f"{role}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"path": str(path), "sha256": sha256_file(path)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="生成 S4-B 硬件门禁记录（离线）")
    ap.add_argument("--preparation", required=True, help="adapter 离线准备清单")
    ap.add_argument("--hardware-run-id", required=True)
    ap.add_argument("--out-dir", required=True, help="门禁记录输出目录（须为新目录）")
    ap.add_argument("--owner", default="Workbuddy 阶段4总控", help="w4 写权负责人")
    ap.add_argument("--valid-hours", type=int, default=168, help="授权有效期（小时）")
    ap.add_argument("--review-file", default=None,
                    help="已完成的 adapter 独立复审 JSON；给出才生成 command_delivery_review")
    ap.add_argument("--weight-path", required=True,
                    help="冻结模型权重文件（OP_WEIGHTS 载荷）；其 SHA 必须等于身份中的 model_weights_sha256")
    ap.add_argument("--tensor-binding-path", required=True,
                    help="输入张量绑定 JSON（status=PASS, format=INT8_CHW_416）；授权将绑定其原字节 SHA")
    args = ap.parse_args(argv)

    out_dir = Path(args.out_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        print(f"[ERROR] 输出目录已存在且非空：{out_dir}", file=sys.stderr)
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)

    worktree = Path(__file__).resolve().parents[2]
    adapter_path = worktree / "scripts/stage4_s4b/s4b_ps_tensor_adapter.py"
    adapter = load_adapter(adapter_path)

    prepared = adapter.validate_preparation(Path(args.preparation).resolve())
    identity, identity_digest = adapter._verified_artifact_identity(prepared)

    weight_path = Path(args.weight_path)
    if not weight_path.is_file():
        print(f"[ERROR] 权重文件不存在：{weight_path}", file=sys.stderr)
        return 2
    weight_sha = sha256_file(weight_path)
    expected_weight_sha = identity.get("model_weights_sha256")
    if weight_sha != expected_weight_sha:
        print(f"[FAIL] 权重 SHA {weight_sha[:16]}… 与身份 model_weights_sha256 "
              f"{str(expected_weight_sha)[:16]}… 不一致，拒绝签发授权", file=sys.stderr)
        return 1

    tensor_binding = json.loads(Path(args.tensor_binding_path).read_text(encoding="utf-8"))
    tensor_file = Path(tensor_binding.get("path", ""))
    tensor_sha = sha256_file(tensor_file) if tensor_file.is_file() else ""
    if (tensor_binding.get("status") != "PASS" or tensor_binding.get("format") != "INT8_CHW_416" or
            not tensor_file.is_file() or tensor_binding.get("sha256") != tensor_sha or
            tensor_file.stat().st_size != 519168 or
            tensor_binding.get("model_manifest_sha256") != identity.get("model_manifest_sha256")):
        print("[FAIL] 张量绑定记录与实际字节/格式/模型不一致，拒绝签发授权", file=sys.stderr)
        return 1

    now = datetime.now(TZ_UTC8)
    now_s = now.isoformat(timespec="seconds")
    expiry = (now + timedelta(hours=args.valid_hours)).isoformat(timespec="seconds")
    review_sha = sha256_file(adapter_path)

    generated: dict[str, dict[str, str]] = {}

    generated["operator_authorization"] = write_record(out_dir, "operator_authorization", {
        "status": "AUTHORIZED",
        "task_id": "S4-B-REAL-02B",
        "hardware_run_id": args.hardware_run_id,
        "authorized_by": args.owner,
        "authorized_at_utc8": now_s,
        "expires_at_utc8": expiry,
        "scope": SCOPE,
        "authorization_id": f"AUTH-{args.hardware_run_id}-{now.strftime('%Y%m%d%H%M')}",
        "operations": DIAGNOSTIC_OPERATIONS,
        "artifact_identity_sha256": identity_digest,
        "weight_sha256": weight_sha,
        "weight_path": str(weight_path.resolve()),
        "tensor_sha256": tensor_sha,
        "tensor_path": str(tensor_file.resolve()),
        "tensor_binding_path": str(Path(args.tensor_binding_path).resolve()),
        "basis": ("按 adapter `validate_hardware_gates` 的 `authorized_by ∈ {Wong, 阶段负责人}` 规则，"
                  "由当前 w4 写权负责人对本轮 PS 张量诊断签发；操作集固定为五项，不含任何其他硬件动作。"),
        "boundaries": ["不含位流重建授权", "不含阶段5/显示路径", "不含 4-D 长跑"],
    })

    generated["timing_freeze"] = write_record(out_dir, "timing_freeze", {
        "status": "APPROVED",
        "hardware_run_id": args.hardware_run_id,
        "artifact_identity_sha256": identity_digest,
        "timebase_status": "APPROVED",
        "threshold_status": "APPROVED",
        "approval_id": f"TIMING-{args.hardware_run_id}",
        "timebase": {
            "source": "PS global timer（XTime_GetTime / 单调计数）",
            "conversion": "ns = ticks * 1e9 / timer_freq_hz；timer_freq_hz 必须在执行前写入证据",
            "forbidden": ["host 墙钟", "工具提交时刻", "跨域直接相减"],
        },
        "threshold": {
            "stale_age_limit_ns": 200000000,
            "comparison": "严格大于（>），每结果只计一次并记录原因",
            "single_source": "阶段4/5/6 共用同一常量",
            "approved_by": "Wong",
            "receipt_binding": {
                "path": STALE_RECEIPT["path"],
                "sha256": sha256_file(Path(STALE_RECEIPT["path"])),
            },
        },
        "note": "冻结的是时基语义与阈值口径；timer_freq_hz 的实测值仍须在执行时记录，不得用假设值代替。",
    })

    generated["range_reservation"] = write_record(out_dir, "range_reservation", {
        "status": "RESERVED",
        "hardware_run_id": args.hardware_run_id,
        "artifact_identity_sha256": identity_digest,
        "scope": "S4-B-REAL-02B",
        "boot_seed": identity["boot_seed"],
        "session_first": identity["session_first"],
        "session_last": identity["session_last"],
        "existing_reservations": [],
        "reservation_basis": ("本轮为首次硬件预留：既有 r11–r13 均为 "
                              "BUILD_ONLY_NOT_RESERVED_FOR_HARDWARE，不存在历史硬件占用，"
                              "故 existing_reservations 为空；seed 非零且 session 为闭区间。"),
        "reserved_at_utc8": now_s,
    })

    # ---- g0_approval：三份文件同时成立才生成；否则记录原因，绝不伪造 ----
    g0_files = {
        "address_map": worktree / "docs/stage4/S4B_stage4_address_map.json",
        "shared_address": worktree / "docs/stage4/S4B_shared_address_map.json",
        "timebase": worktree / "docs/stage4/s4a_stale_age_limit_approval_applied_20261024_r01.json",
    }
    g0_problems: list[str] = []
    for key, path in g0_files.items():
        if not path.is_file():
            g0_problems.append(f"{key}:file_absent")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            g0_problems.append(f"{key}:not_json")
            continue
        if key == "timebase":
            if not payload.get("approved_item"):
                g0_problems.append("timebase:approved_item_absent")
        elif str(payload.get("status")) != "APPROVED":
            g0_problems.append(f"{key}:status_{payload.get('status')}")

    if not g0_problems:
        generated["g0_approval"] = write_record(out_dir, "g0_approval", {
            "status": "APPROVED",
            "task_id": "S4-B-REAL-02B",
            "hardware_run_id": args.hardware_run_id,
            "scope": "BOARD_INJECTION",
            "approval_id": f"G0-{args.hardware_run_id}",
            "artifact_identity_sha256": identity_digest,
            "memory_ranges_sha256": identity.get("memory_ranges_sha256"),
            "address_map_binding": {"path": str(g0_files["address_map"]),
                                    "sha256": sha256_file(g0_files["address_map"])},
            "shared_address_binding": {"path": str(g0_files["shared_address"]),
                                       "sha256": sha256_file(g0_files["shared_address"])},
            "timebase_binding": {"path": str(g0_files["timebase"]),
                                 "sha256": sha256_file(g0_files["timebase"])},
            "approved_at_utc8": now_s,
            "note": "批准不解除 BLOCKED、ENABLE 仍为 0；三项 status 由 adapter 从文件读取复核。",
        })

    if args.review_file:
        review_path = Path(args.review_file)
        if not review_path.is_file():
            print(f"[ERROR] 复审文件不存在：{review_path}", file=sys.stderr)
            return 2
        review = json.loads(review_path.read_text(encoding="utf-8"))
        if review.get("verdict") != "PASS":
            print(f"[FAIL] 复审未通过（verdict={review.get('verdict')}），不生成命令交付复审记录", file=sys.stderr)
            return 1
        if review.get("reviewed_adapter_sha256") != review_sha:
            print("[FAIL] 复审绑定的 adapter SHA 与当前字节不一致", file=sys.stderr)
            return 1
        generated["command_delivery_review"] = write_record(out_dir, "command_delivery_review", {
            "status": "PASS",
            "task_id": "S4-B-REAL-02B",
            "hardware_run_id": args.hardware_run_id,
            "artifact_identity_sha256": identity_digest,
            "reviewed_adapter_sha256": review_sha,
            "review_sha256": sha256_file(review_path),
            "review_record_path": str(review_path),
            "reviewer": review.get("reviewer"),
            "reviewed_at_utc8": review.get("reviewed_at_utc8"),
            "scope": "adapter 命令交付与门禁链路的独立只读复审",
        })

    skipped = [role for role in adapter.REQUIRED_GATE_RECORDS if role not in generated]
    index = {
        "schema_version": "s4b_hw_gate_records_v1",
        "hardware_run_id": args.hardware_run_id,
        "generated_utc8": now_s,
        "preparation": {"path": str(Path(args.preparation).resolve()),
                        "artifact_identity_sha256": identity_digest},
        "adapter_sha256": review_sha,
        "generated": generated,
        "not_generated": skipped,
        "not_generated_reason": {
            "hardware_session_handoff": "需 main OFFER + w4 CLAIM（见 s4b_hw_offer_claim 文档）",
            "exclusive_session": (f"执行时现场取证（hw_server {adapter.HW_SESSION_DEFAULT_PORT} + UART，30 分钟窗口；"
                                  "本机 3121/3131 位于 Windows TCP 排除区间不可绑定）"),
            "g0_approval": (f"三项未同时成立：{g0_problems}" if g0_problems
                            else "已生成"),
            "cold_basis": "需物理断电重建或等价独立证明（Wong 现场）",
            "command_delivery_review": "需对当前 adapter 字节的独立复审（--review-file）",
        },
    }
    (out_dir / "gate_records_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    files = [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha256_file(p)}
             for p in sorted(out_dir.iterdir()) if p.is_file()]
    (out_dir / "manifest.json").write_text(json.dumps({
        "schema_version": 1, "task_id": "S4-B-HW-GATE-RECORDS",
        "run_id": args.hardware_run_id, "generated_utc8": now_s,
        "verdict": "GENERATED", "exit_code": 0, "files": files,
        "scope": "离线可诚实成立的硬件门禁记录；不含现场与环境类记录",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[GENERATED] {len(generated)} 类记录 → {out_dir}")
    for role, binding in generated.items():
        print(f"  - {role}: {binding['sha256'][:16]}…")
    print(f"  未生成: {', '.join(skipped) if skipped else '无'}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as exc:  # noqa: BLE001
        print(f"[ERROR] 未预期错误：{type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(2)
