#!/usr/bin/env python3
"""S4-T30：D1=A 地址落盘的机械核验（只读，可复跑）。

覆盖任务卡 §6 的全部硬检查：
  A. 8 区域 `base + length_bytes == end_addr_exclusive`（含 hex 与整数一致）；
  B. 全域 **零重叠**（半开区间两两检查）；
  C. **共享图 vs 源图**：区域名集合、`base_addr_hex`、`length_bytes`、`status`、`owner_from_source` ↔ 源 `owner` 全部一致；
  D. 新 region 与 **2B 窗口内冻结对象**（tensor/GF8/feature 包络）**不相交**（字面区间与图中 region 双路核对）；
  E. **禁区精确缩减**：存在 `[0x12C08000,0x20000000)`、不存在 `[0x12000000,0x20000000)`、
     缩减量 == raw_frame + raw_meta == 12,615,680 B，且**其余 8 条禁区相对落地前基线逐条不变**（git 基线比对）；
  F. **状态纪律**：两新 region 为提案态（`PROPOSED_*`，**不是** `FROZEN_STAGE4`）、共享图 `enable_status=0`、
     源图整体 `status=APPROVED` 且有 `approval_history`（事实登记，不据此提升任何关口）；
  G. **契约重绑**：契约 `upstream_bindings.stage4_address_map.sha256` == 当前地址图字节 SHA，
     且 `post_freeze_rebinds` 中存在 `to == 该 SHA` 的留痕。

退出码：0 = 全部通过；1 = 存在失败；2 = 输入/环境错误。
本脚本不写地址图/契约，只写 `--run-dir` 下的证据。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

CN = timezone(timedelta(hours=8))
WORKTREE = Path(__file__).resolve().parents[2]
SRC_MAP = WORKTREE / "docs" / "stage4" / "S4B_stage4_address_map.json"
SHARED_MAP = WORKTREE / "docs" / "stage4" / "S4B_shared_address_map.json"
CONTRACT = WORKTREE / "docs" / "stage4" / "s4b_shared_input_result_contract.json"
DEFAULT_BASELINE_REF = "d29ef5f^"  # 落地提交的父提交（禁区缩减前）

RAW = {"name": "raw_frame", "base": 0x12000000, "end": 0x12C00000, "length": 12582912}
META = {"name": "raw_meta", "base": 0x12C00000, "end": 0x12C08000, "length": 32768}
SHRUNK_GAP = {"base": 0x12C08000, "end": 0x20000000, "length": 222265344}
OLD_GAP_BASE = 0x12000000
FROZEN_2B_OBJECTS = {
    "network_input_tensor": (0x10000000, 0x1007EC00),
    "gf8_weight_package": (0x10100000, 0x106A12FC),
    "feature_envelope": (0x11000000, 0x11ADADB8),
}


def now_cn() -> str:
    """当前 UTC+8 时间戳。"""
    return datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    """字节 SHA-256。"""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """文件 SHA-256。"""
    return sha256_bytes(path.read_bytes())


def overlaps(a0: int, a1: int, b0: int, b1: int) -> bool:
    """半开区间相交判定。"""
    return max(a0, b0) < min(a1, b1)


def load_baseline_gaps(ref: str) -> tuple[list[dict] | None, str | None]:
    """从 git 基线取落地前的 gaps；失败返回 (None, 错误)。"""
    proc = subprocess.run(["git", "-C", str(WORKTREE), "show",
                           f"{ref}:docs/stage4/S4B_stage4_address_map.json"],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        return None, f"git show {ref} 退出 {proc.returncode}: {proc.stderr.strip()[:200]}"
    data = json.loads(proc.stdout)
    return data.get("gaps", []), None


def main() -> int:
    """执行全部机械核验。"""
    parser = argparse.ArgumentParser(description="S4-T30 D1=A 落盘机械核验")
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--baseline-ref", default=DEFAULT_BASELINE_REF, help="落地前基线提交（默认落地提交的父提交）")
    args = parser.parse_args()

    out_dir: Path = args.run_dir
    if out_dir.exists() and any(out_dir.iterdir()):
        print(f"[FAIL] 证据目录非空：{out_dir}")
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)

    src = json.loads(SRC_MAP.read_text(encoding="utf-8"))
    shared = json.loads(SHARED_MAP.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    checks: dict[str, dict[str, object]] = {}
    failures: list[str] = []

    def record(name: str, ok: bool, detail: dict[str, object], note: str = "") -> None:
        checks[name] = {"status": "PASS" if ok else "FAIL", "detail": detail, "note": note}
        if not ok:
            failures.append(name)

    regions = src["regions"]
    by_name = {r["name"]: r for r in regions}

    # A. 8 区域算术
    arith = []
    for r in regions:
        ok = (r["base_addr"] + r["length_bytes"] == r["end_addr_exclusive"]
              and int(r["base_addr_hex"], 16) == r["base_addr"]
              and int(r["end_addr_exclusive_hex"], 16) == r["end_addr_exclusive"])
        arith.append({"name": r["name"], "ok": ok, "base": r["base_addr"], "length": r["length_bytes"],
                      "end": r["end_addr_exclusive"]})
    record("A_region_arithmetic", len(regions) == 8 and all(a["ok"] for a in arith),
           {"region_count": len(regions), "regions": arith})

    # B. 零重叠
    pairs = []
    for i in range(len(regions)):
        for j in range(i + 1, len(regions)):
            a, b = regions[i], regions[j]
            if overlaps(a["base_addr"], a["end_addr_exclusive"], b["base_addr"], b["end_addr_exclusive"]):
                pairs.append([a["name"], b["name"]])
    record("B_zero_overlap", not pairs,
           {"regions_checked": len(regions), "pairs": len(regions) * (len(regions) - 1) // 2, "overlaps": pairs})

    # C. 共享图与源图逐区域一致
    shared_by_name = {r["name"]: r for r in shared.get("regions", [])}
    diffs = []
    if set(shared_by_name) != set(by_name):
        diffs.append({"type": "region_name_set", "source": sorted(by_name), "shared": sorted(shared_by_name)})
    for name, s in by_name.items():
        h = shared_by_name.get(name)
        if h is None:
            continue
        for field, sv, hv in (
            ("base_addr_hex", s["base_addr_hex"], h.get("base_addr_hex")),
            ("length_bytes", s["length_bytes"], h.get("length_bytes")),
            ("status", s["status"], h.get("status")),
            ("owner_from_source", s["owner"], h.get("owner_from_source")),
        ):
            if sv != hv:
                diffs.append({"region": name, "field": field, "source": sv, "shared": hv})
    record("C_shared_vs_source_fidelity", not diffs,
           {"regions_compared": len(by_name), "diffs": diffs},
           "共享图是源图的忠实投影；差集必须为 0")

    # D. 与 2B 冻结对象不相交
    disjoint_detail = []
    ok_d = True
    for new_name in (RAW["name"], META["name"]):
        r = by_name[new_name]
        for obj_name, (o0, o1) in FROZEN_2B_OBJECTS.items():
            hit_literal = overlaps(r["base_addr"], r["end_addr_exclusive"], o0, o1)
            src_obj = by_name.get(obj_name)
            hit_region = bool(src_obj) and overlaps(r["base_addr"], r["end_addr_exclusive"],
                                                   src_obj["base_addr"], src_obj["end_addr_exclusive"])
            ok_d = ok_d and not hit_literal and not hit_region
            disjoint_detail.append({"new_region": new_name, "frozen_object": obj_name,
                                    "frozen_interval": [hex(o0), hex(o1)],
                                    "hit_literal": hit_literal, "hit_map_region": hit_region})
    record("D_disjoint_from_2b_frozen_objects", ok_d, {"detail": disjoint_detail})

    # E. 禁区精确缩减 + 其余禁区逐条不变
    gaps = src["gaps"]
    cur_keys = {(int(g["base_addr_hex"], 16), int(g["end_addr_exclusive_hex"], 16)) for g in gaps}
    has_shrunk = any(int(g["base_addr_hex"], 16) == SHRUNK_GAP["base"]
                     and int(g["end_addr_exclusive_hex"], 16) == SHRUNK_GAP["end"]
                     and g["length_bytes"] == SHRUNK_GAP["length"] for g in gaps)
    has_old = any(int(g["base_addr_hex"], 16) == OLD_GAP_BASE for g in gaps)
    shrink_bytes = (RAW["length"] + META["length"])
    baseline_gaps, baseline_error = load_baseline_gaps(args.baseline_ref)
    unchanged_ok = False
    changed_entries: list[dict[str, object]] = []
    if baseline_gaps is None:
        unchanged_ok = False
    else:
        base_keys = {(int(g["base_addr_hex"], 16), int(g["end_addr_exclusive_hex"], 16)) for g in baseline_gaps}
        removed = base_keys - cur_keys
        added = cur_keys - base_keys
        unchanged_ok = (len(baseline_gaps) == len(gaps) == 9 and removed == {(OLD_GAP_BASE, 0x20000000)}
                        and added == {(SHRUNK_GAP["base"], SHRUNK_GAP["end"])})
        changed_entries = [{"removed": [hex(a), hex(b)] for a, b in sorted(removed)},
                           [{"added": [hex(a), hex(b)]} for a, b in sorted(added)]]
    record("E_forbidden_gap_precise_shrink",
           has_shrunk and not has_old and shrink_bytes == 12615680 and len(gaps) == 9 and unchanged_ok,
           {"gap_count_current": len(gaps), "gap_count_baseline": len(baseline_gaps) if baseline_gaps else None,
            "shrunk_gap_present": has_shrunk, "old_gap_absent": not has_old,
            "shrink_bytes": shrink_bytes, "shrink_bytes_expected": 12615680,
            "shrink_equals_raw_plus_meta": shrink_bytes == RAW["length"] + META["length"],
            "other_gaps_unchanged": unchanged_ok, "baseline_ref": args.baseline_ref,
            "baseline_error": baseline_error, "changed_entries": changed_entries})

    # F. 状态纪律
    statuses = {n: by_name[n]["status"] for n in (RAW["name"], META["name"])}
    proposal_ok = all(s.startswith("PROPOSED_") and s != "FROZEN_STAGE4" for s in statuses.values())
    record("F_status_discipline",
           proposal_ok and shared.get("enable_status") == 0 and src.get("status") == "APPROVED"
           and bool(src.get("approval_history")),
           {"new_region_status": statuses, "proposal_state_not_frozen": proposal_ok,
            "shared_enable_status": shared.get("enable_status"),
            "source_map_status": src.get("status"),
            "approval_history_events": [e.get("event") for e in src.get("approval_history", [])],
            "note": "地图整体 APPROVED 为 Wong 2026-10-27 事实登记；不据此提升任何关口（G0 仍开放）"})

    # G. 契约重绑留痕
    binding = next((b for b in contract.get("upstream_bindings", []) if b.get("id") == "stage4_address_map"), None)
    map_sha = sha256_file(SRC_MAP)
    rebinds = contract.get("post_freeze_rebinds", [])
    rebind_hits = [r for r in rebinds
                   for cb in r.get("changed_bindings", [])
                   if cb.get("id") == "stage4_address_map" and str(cb.get("to", "")).lower() == map_sha]
    record("G_contract_rebind", bool(binding) and str(binding.get("sha256", "")).lower() == map_sha and bool(rebind_hits),
           {"map_sha256": map_sha, "contract_bound_sha256": binding.get("sha256") if binding else None,
            "rebind_entries_for_current_sha": len(rebind_hits),
            "rebind_count": len(rebinds),
            "semantics_changed_flags": [r.get("semantics_changed") for r in rebinds]})

    status = "PASS" if not failures else "FAIL"
    report = {
        "task_id": "S4-CTRL/S4-T30", "checker": "verify_d1a_landing", "checker_version": "r01",
        "status": status, "generated_utc8": now_cn(),
        "command": " ".join([sys.executable, *sys.argv]),
        "worktree": str(WORKTREE), "branch": subprocess.run(
            ["git", "-C", str(WORKTREE), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True).stdout.strip(),
        "hardware_execution": "NOT_RUN",
        "identity": {"source_map": {"path": str(SRC_MAP), "sha256": map_sha},
                     "shared_map": {"path": str(SHARED_MAP), "sha256": sha256_file(SHARED_MAP)},
                     "contract": {"path": str(CONTRACT), "sha256": sha256_file(CONTRACT),
                                  "revision": contract.get("revision"), "status": contract.get("status")},
                     "checker": {"path": str(Path(__file__).resolve()), "sha256": sha256_file(Path(__file__).resolve())}},
        "python_version": sys.version, "platform": platform.platform(),
        "checks": checks, "failures": failures,
        "boundary": "只读机械核验；不代表 G0/G1/G3/G4/G5，不代表板级实测，不改变 ENABLE=0。",
        "not_done": ["板级四项实测（CPU1 停止/无其他 DDR consumer/候选区未被占用/cache 可见性）",
                     "独立复审（由项目总控另派 Reviewer）",
                     "ENABLE=1 与 4-D 构建（须先满足裁决 §3 全部前置）"],
    }
    (out_dir / "mechanical_checks.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, item in checks.items():
        print(f"[{item['status']}] {name}")
    print(f"[{status}] D1=A 落盘机械核验：{len(checks) - len(failures)}/{len(checks)} 通过；失败={failures}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())