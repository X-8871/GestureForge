#!/usr/bin/env python3
"""把 task-26 的门禁证据与最新离线证据对齐（只读，不做推理）。

背景：STATE 中“T29 控制 2929/5070、10358/20280 字节不一致”与后续提交 e65ea51
（改用 T25 冻结预处理）后的诊断探针结论不同。本脚本只做机器可核验的对齐：
1. 复算每个 head 二进制与对应黄金文件的 SHA 是否逐字节一致；
2. 逐条核对桥接门运行的身份：状态、整型退出码、运行期记录的桥接器 SHA、五项必备检查；
3. 只有“status=PASS + 整型 exit_code=0 + 桥接器 SHA 等于当前字节 + 五项必备检查全 PASS”
   同时成立，才承认“当前代码上有权威门 PASS 运行”；否则 fail-closed 标 BLOCKED。

边界声明：PASS 只表示**证据文件内部自洽且满足判定条件**，不表示门真的在实机上跑过；
伪造一份自洽证据根同样能得到 PASS，因此本脚本输出必须与桥接器原始证据一起使用。

退出码：0 = 当前桥接器字节上存在权威门全 PASS 运行、head 全一致、G0 已闭合；
1 = 未重跑（或跑了但非 PASS）/存在不一致（预期常态）；2 = 输入或环境错误（证据缺失、
损坏、结构非法、重复键、参数非法、写盘失败）。任何异常都不得伪装成 1，失败不得留残目录。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
CN = timezone(timedelta(hours=8))
EV = WORKTREE / "report/evidence/S4-CTRL"
BRIDGE_REL = "scripts/stage4_s4ctrl/replay_forward_bridge.py"

DIVERGENCE_RUN = "s4t26_layer_divergence_20261026_r02"
G0_RUN = "s4t26_g0_inputs_20261026_r13"

REQUIRED_GATE_CHECKS = (
    "raw_head_gate_forward_byte_compare",
    "positive_detection_gate_forward_d9_nms",
    "negative_control_one_int8_input_byte",
    "png_imread_unchanged_pixel_identity",
    "task25_replay_frame_forward",
)

HEAD_PAIRS = (
    ("sample_000", "head13",
     f"{DIVERGENCE_RUN}/sample_000_actual_head13_int8.bin",
     "s4t26_golden_rebind_20261026_r02/golden/test_fist_000_head13.bin"),
    ("sample_000", "head26",
     f"{DIVERGENCE_RUN}/sample_000_actual_head26_int8.bin",
     "s4t26_golden_rebind_20261026_r02/golden/test_fist_000_head26.bin"),
    ("sample_102", "head13",
     f"{DIVERGENCE_RUN}/sample_102_actual_head13_int8.bin",
     "s4t26_golden_rebind_20261026_r02/golden/approved_no_hand_001_head13.bin"),
    ("sample_102", "head26",
     f"{DIVERGENCE_RUN}/sample_102_actual_head26_int8.bin",
     "s4t26_golden_rebind_20261026_r02/golden/approved_no_hand_001_head26.bin"),
)


def sha256_file(path: Path) -> str:
    """按 1 MiB 分块计算 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """拒绝重复键：重复键会让“后值覆盖前值”，可被用来掩盖 BLOCKED。"""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"JSON 含重复键：{key}")
        result[key] = value
    return result


def read_json(path: Path) -> tuple[str, dict[str, object] | None]:
    """读取 JSON 并返回 (状态, 数据)。状态：ok / missing / invalid（含非 dict 与重复键）。"""
    if not path.is_file():
        return "missing", None
    try:
        data = json.loads(path.read_text(encoding="utf-8"),
                          object_pairs_hook=_reject_duplicate_keys)
    except Exception:  # 解析失败、编码错误、递归过深等一律视为非法输入
        return "invalid", None
    if not isinstance(data, dict):
        return "invalid", None
    return "ok", data


def is_strict_zero(value: object) -> bool:
    """严格判定“整型 0”：排除 bool（`False == 0` 为真，会造成绿通道）与浮点/字符串。"""
    return isinstance(value, int) and not isinstance(value, bool) and value == 0


def write_json_atomic(out_dir: Path, name: str, payload: dict[str, object]) -> None:
    """先把内容编码成字节，再建目录并原子落盘；编码失败不会留下 0 字节残文件。"""
    data = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / f".{name}.tmp"
    tmp.write_bytes(data)
    os.replace(tmp, out_dir / name)


def head_rows(root: Path) -> list[dict[str, object]]:
    """逐对核对 head 二进制与黄金文件。"""
    rows: list[dict[str, object]] = []
    for sample, head, actual_rel, golden_rel in HEAD_PAIRS:
        actual, golden = root / actual_rel, root / golden_rel
        row: dict[str, object] = {
            "sample": sample, "head": head,
            "actual_path": actual_rel, "golden_path": golden_rel,
        }
        if actual.is_file() and golden.is_file():
            a, g = sha256_file(actual), sha256_file(golden)
            row.update({"actual_sha256": a, "golden_sha256": g,
                        "bytes": actual.stat().st_size,
                        "byte_identical": a == g})
        else:
            row.update({"actual_sha256": None, "golden_sha256": None,
                        "byte_identical": False,
                        "detail": "探针输出或黄金文件缺失"})
        rows.append(row)
    return rows


def collect_runs(root: Path, bridge_sha_now: str) -> tuple[list[dict[str, object]], str | None, list[str]]:
    """收集全部桥接门运行。返回 (runs, bridge_last_commit, invalid_files)。

    preflight 缺失只意味着“桥接器身份未知”（不算输入错误）；但**存在却解析失败**属输入错误，
    由 invalid_files 上报，调用方据此返回 2，避免把“读不了”误当“没跑过”。
    """
    proc = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(WORKTREE), "log",
         "--format=%H %cI", "-1", "--", BRIDGE_REL],
        capture_output=True)
    head_info = proc.stdout.decode("utf-8", "replace").strip().split(" ")
    bridge_committed = head_info[1] if len(head_info) > 1 else None

    runs: list[dict[str, object]] = []
    invalid: list[str] = []
    paths = sorted(
        [*root.glob("s4t26_forward_bridge_*/replay_forward_bridge_result.json"),
         *root.glob("s4t26_golden_rebind_*/replay_forward_bridge_result.json")],
        key=lambda p: p.parent.name)
    for path in paths:
        status, data = read_json(path)
        if status != "ok" or data is None:
            invalid.append(str(path))
            continue
        pre_status, pre_data = read_json(path.parent / "preflight_verification.json")
        if pre_status == "invalid":
            invalid.append(str(path.parent / "preflight_verification.json"))
            continue
        bridge_source = (pre_data or {}).get("bridge_source")
        recorded_sha = bridge_source.get("sha256") if isinstance(bridge_source, dict) else None
        checks = data.get("checks")
        check_status: dict[str, object] = {}
        if isinstance(checks, dict):
            for name, item in checks.items():
                if isinstance(item, dict):
                    check_status[str(name)] = item.get("status")
        missing_checks = [n for n in REQUIRED_GATE_CHECKS if check_status.get(n) != "PASS"]
        runs.append({
            "run_id": path.parent.name,
            "generated_utc8": str(data.get("generated_utc8", "")),
            "status": data.get("status"),
            "exit_code": data.get("exit_code"),
            "checker_version": data.get("checker_version"),
            "bridge_sha256_recorded": recorded_sha,
            "bridge_matches_current": bool(recorded_sha) and recorded_sha == bridge_sha_now,
            "checks_not_pass_or_missing": missing_checks,
            "generated_after_bridge_commit": (
                bool(bridge_committed) and str(data.get("generated_utc8", "")) > bridge_committed
            ),
        })
    runs.sort(key=lambda r: str(r.get("generated_utc8")))
    return runs, bridge_committed, invalid


def qualifies_as_gate_pass(run: dict[str, object]) -> bool:
    """判定一次运行是否算“当前字节上的权威门 PASS”。

    必须同时满足：status 恰为 "PASS"、exit_code 为**整型** 0（排除 False/"0"/0.0）、
    运行期记录的桥接器 SHA 等于当前字节、五项必备检查全 PASS。
    """
    return (
        run.get("status") == "PASS"
        and is_strict_zero(run.get("exit_code"))
        and run.get("bridge_matches_current") is True
        and not run.get("checks_not_pass_or_missing")
    )


def g0_closed(g0: dict[str, object]) -> bool:
    """G0 闭合判定：status 必须为 PASS 且退出码必须是整型 0（两者不一致时按未闭合）。"""
    return g0.get("status") == "PASS" and is_strict_zero(g0.get("exit_code"))


def main() -> int:
    """执行对齐并写证据。"""
    parser = argparse.ArgumentParser(description="task-26 门禁证据对齐")
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--evidence-root", default=str(EV),
                        help="被对齐证据的根目录；默认 report/evidence/S4-CTRL（负控用临时根）")
    args = parser.parse_args()

    root = Path(args.evidence_root)
    if not root.is_dir():
        print(f"[ERROR] 证据根目录不存在：{root}")
        return 2

    out_dir = Path(args.evidence_dir)
    if not out_dir.is_absolute():
        out_dir = WORKTREE / out_dir
    if out_dir.exists():
        if not out_dir.is_dir():
            print(f"[ERROR] 证据目录路径已存在且不是目录：{out_dir}")
            return 2
        if any(out_dir.iterdir()):
            print(f"[ERROR] 证据目录非空，拒绝复用 RunId：{out_dir}")
            return 2

    bridge_path = WORKTREE / BRIDGE_REL
    if not bridge_path.is_file():
        print(f"[ERROR] 桥接器缺失，无法核对字节身份：{bridge_path}")
        return 2

    statuses = {}
    data = {}
    for key, path in (
        ("divergence_report", root / f"{DIVERGENCE_RUN}/layer_divergence_report.json"),
        ("authoritative_run", root / "s4t26_golden_rebind_20261026_r02/replay_forward_bridge_result.json"),
        ("g0_r13_preflight", root / f"{G0_RUN}/preflight_verification.json"),
    ):
        statuses[key], data[key] = read_json(path)
    broken = [k for k, s in statuses.items() if s != "ok"]
    if broken:
        detail = "、".join(f"{k}={statuses[k]}" for k in broken)
        print(f"[ERROR] 关键证据不可用（{detail}）；按输入错误处理")
        return 2

    divergence, authoritative, g0_r13 = data["divergence_report"], data["authoritative_run"], data["g0_r13_preflight"]
    bridge_now = sha256_file(bridge_path)
    sources = divergence.get("sources")
    bridge_in_divergence = None
    if isinstance(sources, dict):
        bridge_block = sources.get("bridge")
        if isinstance(bridge_block, dict):
            bridge_in_divergence = bridge_block.get("sha256")
    bridge_in_authoritative = None
    checks = g0_r13.get("checks")
    if isinstance(checks, list):
        for item in checks:
            if isinstance(item, dict) and item.get("name") == "bridge_runner_moving_head_contract":
                detail = item.get("detail")
                if isinstance(detail, dict):
                    bridge_in_authoritative = detail.get("bridge_source_sha256")

    rows = head_rows(root)
    heads_all_identical = all(r["byte_identical"] for r in rows)
    runs, bridge_committed, invalid_runs = collect_runs(root, bridge_now)
    if invalid_runs:
        print("[ERROR] 门运行结果或 preflight 存在但无法解析："
              + "、".join(invalid_runs) + "（按输入错误处理，不得当作“没跑过”）")
        return 2
    qualified_runs = [r for r in runs if qualifies_as_gate_pass(r)]

    problems: list[str] = []
    if not heads_all_identical:
        problems.append("诊断探针 head 与黄金文件不是全部逐字节一致")
    if not qualified_runs:
        problems.append(
            "当前桥接器字节上没有任何权威门 PASS 运行：需 status=PASS、整型 exit_code=0、"
            "运行期 bridge_source.sha256 等于当前字节，且五项必备检查全 PASS；"
            "仅“跑过”或时间更晚不算通过"
        )
    failing_on_current = [
        r["run_id"] for r in runs
        if r.get("bridge_matches_current") and not qualifies_as_gate_pass(r)
    ]
    if failing_on_current:
        problems.append(
            "当前桥接器字节上存在非 PASS 运行：" + "、".join(failing_on_current)
            + "（这些运行的真实状态必须保留，不得以旧 PASS 覆盖）"
        )
    if not g0_closed(g0_r13):
        problems.append(
            f"G0 r13 仍为 {g0_r13.get('status')}/exit {g0_r13.get('exit_code')}，"
            "activation producer provenance 未闭合"
        )

    exit_code = 0 if not problems else 1
    facts: dict[str, object] = {
        "schema_version": "s4t26_gate_reconcile_v3",
        "task_id": "S4-T26-GATE-RECONCILE",
        "run_id": out_dir.name,
        "checker": "scripts/stage4_s4ctrl/reconcile_t26_gate_evidence.py",
        "checker_sha256": sha256_file(Path(__file__).resolve()),
        "generated_utc8": datetime.now(CN).isoformat(timespec="seconds"),
        "evidence_root": str(root),
        "bridge_sha256_now": bridge_now,
        "bridge_sha256_in_divergence_probe": bridge_in_divergence,
        "bridge_sha256_in_authoritative_run": bridge_in_authoritative,
        "bridge_sha256_authoritative_source": "s4t26_g0_inputs_20261026_r13 检查项 bridge_runner_moving_head_contract.detail.bridge_source_sha256",
        "bridge_last_commit_time": bridge_committed,
        "required_gate_checks": list(REQUIRED_GATE_CHECKS),
        "head_comparisons": rows,
        "heads_all_byte_identical": heads_all_identical,
        "divergence_probe": {
            "run_id": DIVERGENCE_RUN,
            "status": divergence.get("status"),
            "exit_code": divergence.get("exit_code"),
            "first_byte_mismatch_layer": divergence.get("first_byte_mismatch_layer"),
            "evidence_kind": "diagnostic_trace_not_authoritative_gate",
        },
        "authoritative_run_cited": {
            "run_id": "s4t26_golden_rebind_20261026_r02",
            "status": authoritative.get("status"),
            "exit_code": authoritative.get("exit_code"),
        },
        "authoritative_bridge_runs": runs,
        "qualified_gate_pass_runs": [r["run_id"] for r in qualified_runs],
        "rerun_after_bridge_fix": bool(qualified_runs),
        "historical_notes": [
            "s4t26_golden_rebind_20261026_r02 的 BLOCKED（桥接器 6780446f…）产生于 T25 预处理修复之前，"
            "其失败归因已被 e65ea51 与诊断探针推翻；该结论对当前代码不再适用，但同样不能当作 PASS。",
            "PASS 只表示证据文件内部自洽且满足判定条件，不表示门在实机执行过；伪造自洽证据根也能得到 PASS。",
        ],
        "g0_r13": {"status": g0_r13.get("status"),
                   "exit_code": g0_r13.get("exit_code"),
                   "blocking_reasons": g0_r13.get("blocking_reasons")},
        "unclosed": problems,
        "verdict": "PASS" if not problems else "BLOCKED",
        "exit_code": exit_code,
        "interpretation_boundary": [
            "诊断探针只观察 forward_one 局部变量，不改变网络数学，但它不是权威门运行。",
            "head 字节一致不等于 D9/NMS 已在权威流程中通过；后者需要桥接器运行并留证。",
            "只有 status=PASS、整型 exit_code=0、运行期桥接器 SHA 等于当前字节、五项必备检查全 PASS，"
            "才计为“当前代码上的门 PASS”。",
            "本脚本不做推理、不生成黄金、不改算法、不访问硬件。",
            "不构成 G0/G1/G3/G4/G5 或实物验收结论；ENABLE=0 不变。",
        ],
    }
    write_json_atomic(out_dir, "reconcile.json", facts)
    files = [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha256_file(p)}
             for p in sorted(out_dir.iterdir())
             if p.is_file() and p.name != "manifest.json"]
    write_json_atomic(out_dir, "manifest.json", {
        "schema_version": 1, "task_id": "S4-T26-GATE-RECONCILE", "run_id": out_dir.name,
        "generated_utc8": facts["generated_utc8"], "verdict": facts["verdict"],
        "exit_code": exit_code, "files": files,
        "scope": "只读对齐；不含推理、黄金生成或硬件操作",
    })

    print(f"[{facts['verdict']}] exit={exit_code} 未闭合项={len(problems)}")
    for line in problems:
        print(f"  - {line}")
    return exit_code


if __name__ == "__main__":
    # 任何未预期异常（含递归过深、编码失败）都归为输入/环境错误（exit 2），不得伪装成 1。
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - 顶层兜底，必须区分于“未闭合”
        print(f"[ERROR] 输入或环境错误：{type(exc).__name__}: {exc}")
        sys.exit(2)
