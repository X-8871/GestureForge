#!/usr/bin/env python
"""从既有门禁证据生成"含检测框"的回放结果包（replay_only，离线）。

背景：task-27 现有包的主结果是 task-25 回放帧（NO_HAND、零框），阳性检测段只是附带信息。
本脚本改用门内的正样本 `test_fist_000` 作为主结果，产出带真实检测框的回放包。

只读既有证据，不重新推理、不改冻结值、不接触硬件。所有引用逐文件绑定 SHA。

用法：
    python -B scripts/stage4_s4ctrl/build_replay_package_positive.py \
        --source-run report/evidence/S4-CTRL/s4t26_gate_rerun_20261027_r04 \
        --run-id s4t27_replay_positive_20261027_r01

退出码：0 = 生成且框数>0；1 = 前置不满足（样本/框缺失或门未 PASS）；2 = 参数/环境错误。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

TZ_UTC8 = timezone(timedelta(hours=8))
SAMPLE_ID = "test_fist_000"
REPLAY_SESSION_ID = 0x5342504F  # "SBPO"：replay-only 合成会话标识，非 PS 分配


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="生成含检测框的回放结果包（只读既有证据）")
    ap.add_argument("--source-run", required=True, help="含 replay_forward_bridge_result.json 的门禁 RunId 目录")
    ap.add_argument("--run-id", required=True, help="本包 RunId（输出目录名）")
    ap.add_argument("--evidence-root", default="report/evidence/S4-CTRL")
    args = ap.parse_args(argv)

    src = Path(args.source_run)
    result_path = src / "replay_forward_bridge_result.json"
    if not result_path.is_file():
        print(f"[ERROR] 缺少门禁结果：{result_path}", file=sys.stderr)
        return 2
    gate = json.loads(result_path.read_text(encoding="utf-8"))
    if gate.get("status") != "PASS":
        print(f"[FAIL] 源门未 PASS（status={gate.get('status')}），拒绝出包", file=sys.stderr)
        return 1

    pos = gate.get("positive_detection_gate") or {}
    if pos.get("sample_id") != SAMPLE_ID:
        print(f"[FAIL] 正样本段不是 {SAMPLE_ID}", file=sys.stderr)
        return 1
    d9 = pos.get("d9_nms") or {}
    preds = d9.get("predictions") or []
    if not preds:
        print("[FAIL] 正样本段没有任何检测框，无法产出带框包", file=sys.stderr)
        return 1
    if not pos.get("positive_detection_match"):
        print("[FAIL] 阳性检测门未匹配（positive_detection_match 非真）", file=sys.stderr)
        return 1

    out_dir = Path(args.evidence_root) / args.run_id
    if out_dir.exists() and any(out_dir.iterdir()):
        print(f"[ERROR] 输出目录已存在且非空：{out_dir}", file=sys.stderr)
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)

    worktree = Path(__file__).resolve().parents[2]
    contract_path = worktree / "docs/stage4/s4b_shared_input_result_contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    now = datetime.now(TZ_UTC8).isoformat(timespec="seconds")

    boxes = [{
        "class_id": p.get("class_id"),
        "class_name": p.get("class_name"),
        "score": p.get("score"),
        "xyxy": p.get("xyxy"),
        "source_order": p.get("source_order"),
    } for p in preds]

    package = {
        "task_id": "S4-T27-REPLAY-POSITIVE",
        "frame_id": 1,
        "result_seq": 1,
        "contract_result_key": {"session_id": REPLAY_SESSION_ID, "frame_id": 1, "result_seq": 1},
        "replay_frame": {
            "sample_id": SAMPLE_ID,
            "sample_index": pos.get("sample_index"),
            "status": "PASS",
            "source_kind": "frozen_gate_positive_sample",
            "image_sha256": pos.get("input_sha256"),
            "input_shape_bgr": pos.get("input_shape_bgr"),
            "input_chw_sha256": pos.get("input_chw_sha256"),
            "decoded_rgb_sha256": (pos.get("preprocessing_representations") or {}).get("decoded_rgb_sha256"),
            "actual_head_sha256": pos.get("actual_head_sha256"),
            "preprocessing_representations": pos.get("preprocessing_representations"),
            "offline_host_elapsed_ms": pos.get("offline_host_elapsed_ms"),
        },
        "detections": {
            "count": len(boxes),
            "boxes": boxes,
            "raw_candidate_count_before_stable_nms": d9.get("raw_candidate_count_before_stable_nms"),
            "expected_raw_candidate_count": d9.get("expected_raw_candidate_count"),
            "nms_output_count": d9.get("nms_output_count"),
            "expected_nms_output_count": d9.get("expected_nms_output_count"),
            "t29_reference_predictions": d9.get("t29_reference_predictions"),
            "exact_t29_detection_match": d9.get("exact_t29_detection_match"),
        },
        "cross_gate_context": {
            "note": "同一门禁运行内的负样本（approved_no_hand_001）仅作 raw-head 逐字节门，不参与本包主结果。",
            "raw_head_gate_sample": (gate.get("raw_head_gate") or {}).get("sample_id"),
            "raw_head_gate_status": (gate.get("raw_head_gate") or {}).get("raw_head_match"),
        },
        "source_bindings": {
            "source_run": src.name,
            "gate_result_path": str(result_path),
            "gate_result_sha256": sha256_file(result_path),
            "bridge_source_sha256": (gate.get("bridge_source") or {}).get("sha256"),
        },
        "contract_binding": {
            "contract_id": contract.get("contract_id"),
            "contract_version": contract.get("contract_version"),
            "revision": contract.get("revision"),
            "status": contract.get("status"),
            "json_sha256": sha256_file(contract_path),
        },
        "marking": {
            "replay_only": True,
            "evidence_kind": "offline_replay",
            "buffer_scope": "offline_host",
            "statement": "离线主机回放；不代表 PL、实物或实时检测输出",
            "session_id_provenance": "0x5342504F 为 replay-only 合成标识，不是 PS 分配的 u32 会话",
        },
        "limitations": [
            "ENABLE=0；RAW 系统 G0 OPEN；P/4-D/G3/G5 NOT_RUN；",
            "本包主结果为冻结正样本 test_fist_000 的离线回放，不是真实摄像头采集；",
            "框坐标为解码后归一化原图 xyxy，仅用于离线回放口径。",
        ],
    }
    (out_dir / "task27_replay_result_package_positive.json").write_text(
        json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    index = {
        "schema_version": "s4t27_replay_positive_freeze_v1",
        "task_id": "S4-T27-REPLAY-POSITIVE",
        "run_id": args.run_id,
        "generated_utc8": now,
        "consumption_mode": "replay_only",
        "package_path": str(out_dir / "task27_replay_result_package_positive.json"),
        "package_sha256": sha256_file(out_dir / "task27_replay_result_package_positive.json"),
        "detection_count": len(boxes),
        "contract_binding": package["contract_binding"],
        "source_run": src.name,
        "gate_result_sha256": package["source_bindings"]["gate_result_sha256"],
        "integrity_rule": "消费方须先复算 package_sha256 与 gate_result_sha256，任一不符即拒绝消费。",
        "forbidden_claims": ["板上行为", "UART 实收", "真实采集质量", "P/4-D/G3/G4/G5 通过", "当实时结果"],
    }
    (out_dir / "freeze_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    files = [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha256_file(p)}
             for p in sorted(out_dir.iterdir()) if p.is_file() and p.name != "manifest.json"]
    (out_dir / "manifest.json").write_text(json.dumps({
        "schema_version": 1, "task_id": package["task_id"], "run_id": args.run_id,
        "generated_utc8": now, "verdict": "FROZEN_REPLAY_ONLY_WITH_DETECTIONS",
        "exit_code": 0, "files": files,
        "scope": "含检测框的离线回放结果包（正样本 test_fist_000）",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[OK] 包已生成：{len(boxes)} 个检测框 → {out_dir}")
    for b in boxes:
        print(f"  - {b['class_name']} score={b['score']:.6f} xyxy={b['xyxy']}")
    print(f"  package_sha256={index['package_sha256'][:16]}…")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as exc:  # noqa: BLE001
        print(f"[ERROR] 未预期错误：{type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(2)
