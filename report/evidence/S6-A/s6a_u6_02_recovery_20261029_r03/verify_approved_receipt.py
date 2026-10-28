from __future__ import annotations

import hashlib
import json
import pathlib
import sys


ROOT = pathlib.Path(r"D:\codex-worktrees\w6")
RUN_ID = "s6a_u6_02_recovery_20261029_r03"
RUN_DIR = ROOT / "report/evidence/S6-A" / RUN_ID
RECEIPT_SOURCE = "report/evidence/S6-A/s6a_u6_02_decision_20261025_r07/decision_receipt.json"
EXPECTED_SEMANTICS = [
    "确认并批准 §10 当前定义：在一个获取区间内，无论目标保持多久、冷却是否结束或窗口是否再次满足，恰好产生一次 ACTION_SUBMITTED。",
    "只有以下任一新获取重新满足稳定窗口，且提交时全局冷却门已结束，才允许产生下一次 ACTION_SUBMITTED：(a) 目标丢失确认后重新获取该目标并再次满足 §9 稳定窗口；(b) 切换到另一合法目标并满足 §9 稳定窗口。提交时须满足 t_now − t_last_submit ≥ T6-K01。",
    "目标持续保持、保持期间稳定窗口再次满足或冷却结束本身都不构成新的获取，也不产生重复提交。",
]


def main() -> int:
    bindings = json.loads((RUN_DIR / "source_bindings.json").read_text(encoding="utf-8"))
    item = next(
        entry for entry in bindings["files"]
        if entry.get("source_path") == RECEIPT_SOURCE
    )
    snapshot = ROOT.joinpath(*pathlib.PurePosixPath(item["path"]).parts)
    raw = snapshot.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    receipt = json.loads(raw.decode("utf-8"))
    checks = {
        "source_binding_hash_matches": digest == item["sha256"],
        "decision_id_matches": receipt.get("decision_id") == "U6-02",
        "approved_status_matches": receipt.get("decision_status") == "APPROVED_20261025",
        "approved_semantics_exact_match": receipt.get("approved_semantics") == EXPECTED_SEMANTICS,
    }
    result = {
        "schema_version": 1,
        "artifact": "u6_02_r07_approved_receipt_exact_verification",
        "task_id": "S6-A",
        "run_id": RUN_ID,
        "receipt_source_path": RECEIPT_SOURCE,
        "snapshot_path": item["path"],
        "receipt_sha256": digest,
        "decision_id": receipt.get("decision_id"),
        "decision_status": receipt.get("decision_status"),
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "hash_basis": "worktree_disk",
        "hash_basis_note": "回执和快照 SHA-256 按工作区磁盘原始字节计算。",
        "scope_limit": "只验证用户批准的 U6-02 r07 回执身份、状态、字节绑定及批准语义原文；不替代独立复核或 G0/G4/G5。",
    }
    output = RUN_DIR / "results/approved_receipt_verification.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": result["status"], "receipt_sha256": digest}, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
