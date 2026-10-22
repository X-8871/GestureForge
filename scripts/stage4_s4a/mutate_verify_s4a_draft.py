#!/usr/bin/env python3
"""S4-A r06 自检器的变异自证（隔离沙箱，只写 tmp 与证据目录）。

在沙箱副本（保持相同相对布局）上对 md/json 做定点变异，逐个运行自检脚本，期望：
  - 阳性对照（未变异）必须 exit 0；
  - 每一条变异必须被检出（exit 1）。

覆盖本轮新增的机器检查：钉扎 SHA、g0_round_freeze 冻结项/未冻结项、文档事实锚点、
候选边界锚点、上游钉扎条目齐备性。默认跳过 109 分片逐片 SHA（`--with-shard-sha` 可开启），
因为该检查已由主自检覆盖且会显著拉长变异轮次；变异目标不涉及分片内容。

本脚本只写 tmp/4/S4-A/<run_id>/mutation_sandbox 与 --evidence-dir；不修改工作树被审文件。
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
SANDBOX = WORKTREE / "tmp" / "4" / "S4-A" / "s4a_g0_20261022_r01" / "mutation_sandbox"
RELATIVE_FILES = (
    "docs/stage4/S4A_stage4_g0_tracking_and_timing_draft.md",
    "docs/stage4/s4a_stage4_g0_fields.json",
    "verification/s1_t02_d2_numeric_reference.py",
    "verification/s1_t02_d9_yolo_decode.py",
    "verification/s1_t02_d6_detection_metrics.py",
    "scripts/stage4_s4a/verify_s4a_draft.py",
)
CN_TIMES = timedelta(hours=8)


def now_utc8() -> str:
    """返回 UTC+8 的 ISO 8601 当前时刻。"""
    return datetime.now(timezone.utc).astimezone(timezone(CN_TIMES)).isoformat(timespec="seconds")


def build_sandbox() -> Path:
    """把被审文件与自检脚本复制到隔离沙箱，保持相对布局。"""
    if SANDBOX.exists():
        shutil.rmtree(SANDBOX)
    for rel in RELATIVE_FILES:
        target = SANDBOX / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(WORKTREE / rel, target)
    return SANDBOX


def run_checker(with_shard_sha: bool) -> int:
    """在沙箱里运行自检脚本，返回真实退出码。"""
    command = [sys.executable, "-B", str(SANDBOX / "scripts" / "stage4_s4a" / "verify_s4a_draft.py")]
    if not with_shard_sha:
        command.append("--no-shard-sha")
    result = subprocess.run(
        command,
        cwd=str(SANDBOX),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode


def mutate_doc(mutator) -> None:
    """对沙箱内人读文档施加变异。"""
    path = SANDBOX / "docs/stage4/S4A_stage4_g0_tracking_and_timing_draft.md"
    path.write_text(mutator(path.read_text(encoding="utf-8")), encoding="utf-8")


def mutate_json(mutator) -> None:
    """对沙箱内契约 JSON 施加变异。"""
    path = SANDBOX / "docs/stage4/s4a_stage4_g0_fields.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    mutator(doc)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def flip_binding_sha(binding_id: str):
    """返回把某条钉扎的期望 SHA 末位翻转的变异函数（制造 MISMATCH）。"""
    def _mutator(doc: dict) -> None:
        binding = next(item for item in doc["upstream_bindings"] if item["id"] == binding_id)
        sha = binding["sha256"]
        binding["sha256"] = sha[:-1] + ("0" if sha[-1] != "0" else "1")
    return _mutator


def drop_binding(binding_id: str):
    """返回删除某条钉扎条目的变异函数。"""
    def _mutator(doc: dict) -> None:
        doc["upstream_bindings"] = [item for item in doc["upstream_bindings"] if item["id"] != binding_id]
    return _mutator


def drop_frozen_item(item_id: str):
    """返回删除某个冻结项的变异函数。"""
    def _mutator(doc: dict) -> None:
        doc["g0_round_freeze"]["frozen_items"] = [
            item for item in doc["g0_round_freeze"]["frozen_items"] if item["id"] != item_id
        ]
    return _mutator


def approve_stale():
    """返回把 stale_age_limit 写成已批准（APPROVED）的变异函数。"""
    def _mutator(doc: dict) -> None:
        for item in doc["g0_round_freeze"]["not_frozen_items"]:
            if item["id"] == "stale_age_limit":
                item["status"] = "APPROVED"
    return _mutator


def main() -> int:
    """执行全部变异并输出结果表。"""
    parser = argparse.ArgumentParser(description="S4-A r06 自检器变异自证")
    parser.add_argument("--evidence-dir", default="", help="可选的证据输出目录（本工作树内）")
    parser.add_argument("--with-shard-sha", action="store_true", help="变异轮次也逐片校验 109 分片 SHA（慢）")
    args = parser.parse_args()

    cases: list[tuple[str, str, object]] = [
        ("M0 阳性对照（未变异）", "none", None),
        ("M1 翻转一条钉扎期望 SHA（s1_t02_d9_decoder）", "json", flip_binding_sha("s1_t02_d9_decoder")),
        ("M2 删除冻结项 candidate_limit_boundary", "json", drop_frozen_item("candidate_limit_boundary")),
        ("M3a 把 stale_age_limit 状态写成 APPROVED", "json", approve_stale()),
        ("M3b 文档把 DRAFT_PENDING_APPROVAL 写成已批准", "doc", lambda t: t.replace("DRAFT_PENDING_APPROVAL", "已批准")),
        ("M4 文档删除候选边界 12676 锚点", "doc", lambda t: t.replace("追加 12676", "追加 27676")),
        ("M5 文档删除 2B 冻结回执 SHA", "doc", lambda t: t.replace(
            "2687e87a9664d6415d17738a6f6ff10b8fe3e372696399eb710fa2d06d2778e1", "0" * 64)),
        ("M6 删除上游钉扎条目 stage2b_freeze_receipt", "json", drop_binding("stage2b_freeze_receipt")),
        ("M7 文档删除注入不伪造采集时间锚点", "doc", lambda t: t.replace("注入不得伪造", "注入可以伪造")),
    ]

    rows: list[dict[str, object]] = []
    unexpected = 0
    for label, kind, mutator in cases:
        build_sandbox()
        if kind == "doc":
            mutate_doc(mutator)
        elif kind == "json":
            mutate_json(mutator)
        code = run_checker(args.with_shard_sha)
        expected = 0 if label.startswith("M0") else 1
        ok = code == expected
        if not ok:
            unexpected += 1
        rows.append({"case": label, "exit_code": code, "expected": expected, "verdict": "OK" if ok else "UNEXPECTED"})
        print(f"{'OK ' if ok else 'BAD'} {label}: exit={code} expected={expected}")

    result = {
        "task_id": "S4-A",
        "purpose": "自检器 r06 变异自证：改动钉扎 SHA / 删除冻结项 / 把 stale_age_limit 写成已批准 必须 FAIL",
        "generated_at_utc8": now_utc8(),
        "sandbox": str(SANDBOX),
        "shard_sha_in_mutation_runs": bool(args.with_shard_sha),
        "positive_control_expected_exit": 0,
        "cases": rows,
        "unexpected": unexpected,
        "status": "PASS" if unexpected == 0 else "FAIL",
        "exit_code": 0 if unexpected == 0 else 1,
    }

    if args.evidence_dir:
        out_dir = Path(args.evidence_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "mutation_selfcheck_result.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"[INFO] 变异自证结果已写入 {out_dir / 'mutation_selfcheck_result.json'}")

    print(f"[{'PASS' if unexpected == 0 else 'FAIL'}] 变异自证：{len(cases)} 例，{unexpected} 例与期望不符")
    return 0 if unexpected == 0 else 1


if __name__ == "__main__":
    sys.exit(main())