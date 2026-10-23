#!/usr/bin/env python3
"""帧周期 P 证据校验器（阶段4 → 阶段6 T6-A03）。

结构性禁止填造：`NOT_RUN` 不得携带任何数值/统计量；`MEASURED` 必须有真实硬件执行、
实时彩色来源、部署与计时器绑定、≥1000 合格帧、自洽统计量与八类硬件门禁。

脚本同时对**内存内构造的合成记录**做负向对照（不落盘、不当证据），只有在负向对照
全部被拒时才判 PASS。

退出码：0 = 记录合规且负向对照全部被拒；1 = 记录被拒或负向对照漏检；2 = 输入/环境错误。
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import platform
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
TEMPLATE = WORKTREE / "docs" / "stage4" / "s4b_frame_period_p_evidence_template.json"
CN = timezone(timedelta(hours=8))

STATUSES = ("NOT_RUN", "INSUFFICIENT_SAMPLE", "MEASURED", "FAILED")
GATES = (
    "operator_authorization", "hardware_session_handoff", "exclusive_session", "g0_approval",
    "command_delivery_review", "timing_freeze", "range_reservation", "cold_basis",
)
DEPLOY_FIELDS = (
    "uncompensated_sof_bit_sha256", "xsa_identity", "runtime_elf", "runtime_elf_sha256",
    "verified_on_site_utc8",
)
POSITIVE_STATS = ("p_mean_ns", "p_median_ns", "p_p95_ns", "p_min_ns", "p_max_ns")


def sha256_of(path: Path) -> str:
    """按 1 MiB 分块计算 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(record: dict) -> list[str]:
    """校验一条帧周期 P 证据记录；返回错误列表（空即合规）。"""
    errors: list[str] = []
    status = record.get("status")
    if status not in STATUSES:
        errors.append(f"非法 status：{status}（合法 {STATUSES}）")
        return errors
    value = record.get("value")
    hardware = record.get("hardware_execution")
    source = record.get("source") or {}
    session = record.get("session") or {}
    stats = record.get("statistics") or {}

    if status in ("NOT_RUN", "FAILED"):
        if value is not None:
            errors.append(f"status={status} 时 value 必须为 null（禁止填造）")
        if hardware != "NOT_RUN":
            errors.append(f"status={status} 时 hardware_execution 必须为 NOT_RUN")
        if any(v is not None for v in stats.values()):
            errors.append(f"status={status} 不得携带统计量")
        if source.get("range_label") is not None:
            errors.append(f"status={status} 不得声明来源标签")
        if session.get("n_valid") is not None:
            errors.append(f"status={status} 不得声明样本量")
        return errors

    # 以下为已执行样本
    if hardware != "EXECUTED":
        errors.append("非 NOT_RUN/FAILED 必须 hardware_execution=EXECUTED")
    if source.get("range_label") != "camera_live_colour":
        errors.append("P 的数值来源必须是 camera_live_colour；回放/合成/注入不得作为 T6-A03 数值来源")

    deploy = record.get("deployment_bindings") or {}
    for field in DEPLOY_FIELDS:
        if not deploy.get(field):
            errors.append(f"缺部署绑定 {field}")
    capture = record.get("capture_bindings") or {}
    freq = capture.get("timer_freq_hz")
    if not isinstance(freq, (int, float)) or freq <= 0:
        errors.append("timer_freq_hz 必须为正数（未标定即停止）")
    if not capture.get("clock_domain"):
        errors.append("缺 clock_domain")

    n_valid = session.get("n_valid")
    n_intervals = session.get("n_intervals")
    if not isinstance(n_valid, int) or n_valid <= 0:
        errors.append("n_valid 必须为正整数")
    if isinstance(n_valid, int) and isinstance(n_intervals, int) and n_intervals != n_valid - 1:
        errors.append("n_intervals 必须等于 n_valid − 1")

    if status == "INSUFFICIENT_SAMPLE":
        if isinstance(n_valid, int) and n_valid >= 1000:
            errors.append("status=INSUFFICIENT_SAMPLE 要求 n_valid < 1000")
        if value is not None:
            errors.append("样本不足时不得给出 value")
    if status == "MEASURED":
        if not isinstance(n_valid, int) or n_valid < 1000:
            errors.append(f"status=MEASURED 要求 n_valid ≥ 1000，实际 {n_valid}")
        if value is None:
            errors.append("status=MEASURED 必须给出 value")
        for name in POSITIVE_STATS:
            if not isinstance(stats.get(name), (int, float)) or stats.get(name) <= 0:
                errors.append(f"统计量 {name} 必须为正数且已实测")
        std = stats.get("p_std_ns")
        if not isinstance(std, (int, float)) or std < 0:
            errors.append("统计量 p_std_ns 必须为非负数且已实测")
        try:
            pmin, pmax = stats["p_min_ns"], stats["p_max_ns"]
            pmed, p95, pmean = stats["p_median_ns"], stats["p_p95_ns"], stats["p_mean_ns"]
            if not pmin <= pmed <= pmax:
                errors.append("p_median_ns 必须落在 [p_min_ns, p_max_ns] 内")
            if not pmed <= p95 <= pmax:
                errors.append("p_p95_ns 必须落在 [p_median_ns, p_max_ns] 内")
            if not pmin <= pmean <= pmax:
                errors.append("p_mean_ns 必须落在 [p_min_ns, p_max_ns] 内")
            if value != pmed:
                errors.append("顶层 value 必须等于 p_median_ns（value_selection 口径）")
        except KeyError:
            pass

    for entry in ("per_frame_evidence", "source_frame_hashes"):
        block = record.get(entry) or {}
        if not block.get("path") or not block.get("sha256"):
            errors.append(f"{entry} 必须给出 path 与 sha256")
    per_frame = record.get("per_frame_evidence") or {}
    if not per_frame.get("fields"):
        errors.append("per_frame_evidence.fields 不得为空")

    gates = record.get("hardware_gates") or {}
    for gate in GATES:
        if gates.get(gate) is not True:
            errors.append(f"硬件门禁 {gate} 必须为 true（CDX-20261023-018 §4 八类门禁）")
    for field in ("offer_commit", "claim_commit"):
        if not gates.get(field):
            errors.append(f"硬件门禁 {field} 不得为空（OFFER/CLAIM 必须为真实 Git 记录）")
    if len(deploy.get("runtime_elf_sha256", "")) != 64:
        errors.append("runtime_elf_sha256 必须是 64 位十六进制")
    return errors


def synthetic_measured() -> dict:
    """内存内构造一条合规的 MEASURED 记录，仅供负向对照使用（不落盘、非证据）。"""
    return {
        "schema_version": "gestureforge_s4_frame_period_p_evidence_v1",
        "run_id": "SELF_TEST_ONLY_NOT_EVIDENCE",
        "status": "MEASURED",
        "hardware_execution": "EXECUTED",
        "value": 33_333_333,
        "source": {"range_label": "camera_live_colour"},
        "deployment_bindings": {
            "uncompensated_sof_bit_sha256": "7cb330685260ced38636d3e90a92160979b0f88770d380269e9864722ce48710",
            "xsa_identity": "self-test",
            "runtime_elf": "an5642_j11cmos2_v10_read.elf",
            "runtime_elf_sha256": "1457cda4867649dce8b54b2ebe9c7bafc0a2a1d4d1deba112adc6f6492306073",
            "verified_on_site_utc8": "2026-10-24T00:00:00+08:00",
        },
        "capture_bindings": {"timer_freq_hz": 100000000, "clock_domain": "PS 100MHz global timer"},
        "session": {"n_valid": 1000, "n_intervals": 999},
        "statistics": {
            "p_mean_ns": 33_333_000, "p_median_ns": 33_333_333, "p_p95_ns": 33_400_000,
            "p_min_ns": 33_000_000, "p_max_ns": 33_600_000, "p_std_ns": 50_000, "jitter_ratio": 0.0015,
        },
        "per_frame_evidence": {"path": "self-test.jsonl", "sha256": "0" * 64, "fields": ["frame_id", "capture_time_ns"]},
        "source_frame_hashes": {"path": "self-test-hashes.txt", "sha256": "0" * 64, "bound_frame_count": 100},
        "hardware_gates": {
            **{gate: True for gate in GATES}, "offer_commit": "0" * 40, "claim_commit": "0" * 40,
        },
    }


def main() -> int:
    """校验目标记录并执行负向对照。"""
    parser = argparse.ArgumentParser(description="帧周期 P 证据校验器")
    parser.add_argument("--record", default=str(TEMPLATE))
    parser.add_argument("--evidence-dir", default="")
    args = parser.parse_args()

    path = Path(args.record)
    if not path.is_file():
        print(f"[FAIL] 记录不存在：{path}")
        return 2
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[FAIL] 记录无法解析：{exc}")
        return 2

    failures: list[str] = []
    passes: list[str] = []

    base_errors = validate(record)
    if base_errors:
        failures.extend([f"目标记录被拒：{err}" for err in base_errors])
    else:
        passes.append(f"目标记录合规（status={record.get('status')}）：{path.name}")

    controls: dict[str, bool] = {}
    base = synthetic_measured()
    if validate(base):
        failures.append("负向对照基线（内存合成 MEASURED）本身不合规，对照无效")

    mutated = copy.deepcopy(base)
    mutated["status"] = "NOT_RUN"
    mutated["hardware_execution"] = "NOT_RUN"
    controls["not_run_with_value"] = bool(validate(mutated))

    mutated = copy.deepcopy(base)
    mutated["source"]["range_label"] = "camera_capture_replay_colour"
    controls["replay_as_value_source"] = bool(validate(mutated))

    mutated = copy.deepcopy(base)
    mutated["session"] = {"n_valid": 100, "n_intervals": 99}
    controls["insufficient_sample_marked_measured"] = bool(validate(mutated))

    mutated = copy.deepcopy(base)
    mutated["statistics"]["p_median_ns"] = 99_999_999_999
    controls["median_outside_range"] = bool(validate(mutated))

    mutated = copy.deepcopy(base)
    mutated["hardware_gates"]["g0_approval"] = False
    controls["gate_missing"] = bool(validate(mutated))

    mutated = copy.deepcopy(base)
    mutated["capture_bindings"]["timer_freq_hz"] = 0
    controls["uncalibrated_timer"] = bool(validate(mutated))

    if not all(controls.values()):
        failures.append(f"负向对照未全部被拒：{controls}")
    else:
        passes.append("负向对照 6/6 均被拒（禁止填造/回放冒充/样本不足/统计矛盾/门禁缺失/计时器未标定）")

    status = "PASS" if not failures else "FAIL"
    report = {
        "task_id": "S4-CTRL/S4-T21",
        "checker": "validate_frame_period_p_evidence",
        "checker_version": "r01",
        "status": status,
        "generated_at_utc8": datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds"),
        "command": " ".join([sys.executable, *sys.argv]),
        "exit_code": 0 if status == "PASS" else 1,
        "python_version": sys.version,
        "platform": platform.platform(),
        "record_path": str(path),
        "record_status": record.get("status"),
        "record_sha256": sha256_of(path),
        "checker_sha256": sha256_of(Path(__file__).resolve()),
        "passes": passes,
        "failures": failures,
        "negative_controls": controls,
        "hardware_execution": "NOT_RUN",
        "boundary": "只读校验；不代表 G3/G4/G5，也不产生 P 的数值。",
    }
    if args.evidence_dir:
        out = Path(args.evidence_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "frame_period_p_validation_result.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    for line in passes:
        print(f"[PASS] {line}")
    for line in failures:
        print(f"[FAIL] {line}")
    print(f"[{status}] 帧周期 P 证据校验：{len(passes)} 项通过、{len(failures)} 项失败")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())