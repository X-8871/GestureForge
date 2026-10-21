#!/usr/bin/env python3
"""S4-C 驱动脚本：真实执行对拍/反例/自检/回归并把证据落到 ``report/evidence/S4-C/<run_id>/``。

执行步骤（每步记录真实命令、退出码、耗时与完整控制台日志）：

  s0  manifest 两头常量交叉核对（--check-manifest-heads）
  s1  全量 109 样本 golden 对拍（期望退出码 0、字节/框 mismatch 均为 0）
  s2  种子化子集对拍（--limit 8 --seed 20261021，记录种子与样本 id）
  s3  --actual 正对照：用本样本 golden 两头导出的 pristine heads 对拍（期望 0）
  s4  --actual 反例：驱动侧独立翻转 1 个字节的 heads（期望 1 = FAIL 且定位到字段）
  s5  --self-test-tamper 篡改自检（期望 0 = 全部探针均被检出）
  s6  python -m unittest verification.test_s4_replay_compare -v（期望 0）

反例由本脚本独立构造（不调用被测工具的探针实现），因此 s4 的 FAIL 不是自证。
用法：python -B scripts/stage4_s4c/run_s4c_replay.py [--run-id ...]

限制：纯 CPU 离线；不使用硬件/串口/Vivado/xsim；不修改任何上游只读树。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
VERIFICATION = WORKTREE / "verification"
TOOL = VERIFICATION / "s4_replay_compare.py"
TEST_MODULE = "verification.test_s4_replay_compare"
EVIDENCE_ROOT = WORKTREE / "report" / "evidence" / "S4-C"
TMP_ROOT = WORKTREE / "tmp" / "4" / "S4C"

TAMPER_SAMPLE = "test_fist_000"
SUBSET_LIMIT = 8
SUBSET_SEED = 20261021

if str(VERIFICATION) not in sys.path:
    sys.path.insert(0, str(VERIFICATION))

import s4_replay_compare as s4c  # noqa: E402


def now_utc8() -> str:
    """东八区时间（秒精度 ISO 8601）。"""

    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def default_run_id() -> str:
    """生成不与既有证据冲突的 RunId：``s4c_replay_<YYYYMMDD>_rNN``。"""

    stamp = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d")
    existing = sorted(EVIDENCE_ROOT.glob(f"s4c_replay_{stamp}_r*")) if EVIDENCE_ROOT.is_dir() else []
    used = {item.name.rsplit("_r", 1)[-1] for item in existing}
    index = 1
    while f"{index:02d}" in used:
        index += 1
    return f"s4c_replay_{stamp}_r{index:02d}"


def git_info() -> dict[str, object]:
    """采集当前工作树提交信息（只读）。"""

    def run(args: list[str]) -> str:
        try:
            completed = subprocess.run(
                ["git", *args], cwd=str(WORKTREE), capture_output=True, text=True, encoding="utf-8"
            )
            return completed.stdout.strip() if completed.returncode == 0 else ""
        except OSError:
            return ""

    status = run(["status", "--short"])
    return {
        "head": run(["rev-parse", "HEAD"]),
        "branch": run(["rev-parse", "--abbrev-ref", "HEAD"]),
        "status_short": status.splitlines(),
    }


def sha256_file(path: Path) -> str:
    """调用工具模块的分块哈希。"""

    return s4c.sha256_file(path)


def run_step(
    *,
    name: str,
    purpose: str,
    command: list[str],
    log_path: Path,
    expected_exit: int = 0,
    timeout: int = 3600,
) -> dict[str, object]:
    """执行一条真实命令并把控制台输出写入证据日志。"""

    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            cwd=str(WORKTREE),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        returncode: int | None = completed.returncode
        stdout, stderr = completed.stdout, completed.stderr
        timed_out = False
    except subprocess.TimeoutExpired as exc:  # pragma: no cover - 防御
        returncode = None
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + f"\n[TIMEOUT] 超过 {timeout}s"
        timed_out = True
    seconds = time.perf_counter() - started
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        "\n".join(
            [
                f"$ {' '.join(command)}",
                f"cwd={WORKTREE}",
                f"started_utc8={now_utc8()}",
                f"exit_code={returncode}",
                f"expected_exit={expected_exit}",
                f"elapsed_seconds={seconds:.3f}",
                "",
                "--- stdout ---",
                stdout,
                "--- stderr ---",
                stderr,
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    ok = (not timed_out) and returncode == expected_exit
    marker = "PASS" if ok else "FAIL"
    print(
        f"[{marker}] {name}: exit={returncode}（期望 {expected_exit}）耗时 {seconds:.2f}s -> {log_path.name}",
        flush=True,
    )
    return {
        "step": name,
        "purpose": purpose,
        "command": command,
        "command_line": " ".join(command),
        "cwd": str(WORKTREE),
        "exit_code": returncode,
        "expected_exit": expected_exit,
        "matched_expectation": ok,
        "timed_out": timed_out,
        "elapsed_seconds": seconds,
        "log_file": str(log_path),
        "stdout_tail": "\n".join(stdout.strip().splitlines()[-6:]),
        "stderr_tail": "\n".join(stderr.strip().splitlines()[-6:]),
    }


def load_report(path: Path) -> dict[str, object] | None:
    """读取步骤产出的机器可读报告（不存在则 None）。"""

    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def localized_fields(sample_record: dict) -> list[str]:
    """收集一个样本记录里出现 mismatch 的字段名。"""

    return sorted({str(item.get("field")) for item in sample_record.get("mismatches", [])})


def main(argv: list[str] | None = None) -> int:
    """执行全部步骤并返回退出码（0=全部符合预期，1=存在不符合，2=环境错误）。"""

    parser = argparse.ArgumentParser(description="S4-C 离线回放与对拍驱动")
    parser.add_argument("--run-id", default="", help="证据 RunId（默认自动生成 s4c_replay_<date>_rNN）")
    parser.add_argument("--skip-unittest", action="store_true", help="跳过 unittest 步骤（不推荐）")
    parser.add_argument("--tamper-sample", default=TAMPER_SAMPLE, help="反例使用的样本号")
    parser.add_argument("--timeout", type=int, default=3600, help="单步超时秒数")
    args = parser.parse_args(argv)

    run_id = args.run_id or default_run_id()
    evidence_dir = EVIDENCE_ROOT / run_id
    tmp_dir = TMP_ROOT / run_id
    if evidence_dir.exists() and any(evidence_dir.iterdir()):
        print(f"[FAIL] 证据目录已存在且非空，拒绝覆盖（换 --run-id）：{evidence_dir}")
        return 2

    evidence_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    started_utc8 = now_utc8()
    steps: list[dict[str, object]] = []
    python = sys.executable
    log_dir = evidence_dir / "console"

    print(f"[INFO] RunId={run_id}")
    print(f"[INFO] 证据目录={evidence_dir}")
    print(f"[INFO] 临时目录={tmp_dir}")

    # s0 manifest 两头常量交叉核对
    steps.append(
        run_step(
            name="s0_manifest_head_crosscheck",
            purpose="交叉核对 T01 manifest 的头部 scale/长度/地址与 2A 冻结常量",
            command=[
                python,
                "-B",
                str(TOOL),
                "--check-manifest-heads",
                "--json-out",
                str(evidence_dir / "manifest_head_crosscheck.json"),
            ],
            log_path=log_dir / "s0_manifest_head_crosscheck.txt",
            timeout=args.timeout,
        )
    )

    # s1 全量 109
    steps.append(
        run_step(
            name="s1_golden_full_109",
            purpose="全量 109 样本 golden 对拍（字节校验 + 逐框比较）",
            command=[
                python,
                "-B",
                str(TOOL),
                "--run-id",
                run_id,
                "--json-out",
                str(evidence_dir / "replay_golden_109.json"),
            ],
            log_path=log_dir / "s1_golden_full_109.txt",
            timeout=args.timeout,
        )
    )

    # s2 种子化子集
    steps.append(
        run_step(
            name="s2_subset_seeded",
            purpose=f"种子化子集对拍（--limit {SUBSET_LIMIT} --seed {SUBSET_SEED}）",
            command=[
                python,
                "-B",
                str(TOOL),
                "--run-id",
                run_id,
                "--limit",
                str(SUBSET_LIMIT),
                "--seed",
                str(SUBSET_SEED),
                "--json-out",
                str(evidence_dir / f"replay_subset{SUBSET_LIMIT}_seed{SUBSET_SEED}.json"),
            ],
            log_path=log_dir / "s2_subset_seeded.txt",
            timeout=args.timeout,
        )
    )

    # 构造 --actual 正/反例目录（反例由驱动独立翻转字节，不复用工具探针）
    tamper_meta: dict[str, object] = {}
    pristine_dir = tmp_dir / "actual_pristine"
    tampered_dir = tmp_dir / "actual_tamper1"
    try:
        paths = s4c.resolve_upstream_paths()
        index, reference, catalog = s4c.load_upstream_dataset(paths)
        index_by_id = {str(item["sample_id"]): item for item in index["samples"]}
        t29_by_id = {str(item["sample_id"]): item for item in reference["samples"]}
        sample_id = args.tamper_sample
        if sample_id not in t29_by_id:
            raise s4c.S4CError(f"未知反例样本：{sample_id}")
        exported = s4c.export_golden_heads(
            index_sample=index_by_id[sample_id],
            t29_sample=t29_by_id[sample_id],
            tensors_dir=paths.tensors_dir,
            out_dir=pristine_dir,
        )
        tampered_dir.mkdir(parents=True, exist_ok=True)
        head13_path = pristine_dir / f"{sample_id}.head13.bin"
        head26_path = pristine_dir / f"{sample_id}.head26.bin"
        original = bytearray(head13_path.read_bytes())
        before = original[0]
        original[0] = before ^ 0x01
        (tampered_dir / f"{sample_id}.head13.bin").write_bytes(bytes(original))
        (tampered_dir / f"{sample_id}.head26.bin").write_bytes(head26_path.read_bytes())
        tamper_meta = {
            "constructed_by": "driver（独立于工具 --self-test-tamper 探针实现）",
            "sample_id": sample_id,
            "head": "head13",
            "byte_index": 0,
            "xor_mask": 1,
            "original_byte": before,
            "tampered_byte": original[0],
            "original_head13_sha256": sha256_file(head13_path),
            "tampered_head13_sha256": sha256_file(tampered_dir / f"{sample_id}.head13.bin"),
            "expected_tensor_sha256_t29": t29_by_id[sample_id]["head_tensors"]["head13"]["tensor_sha256"],
            "pristine_heads_dir": str(pristine_dir),
            "tampered_heads_dir": str(tampered_dir),
            "expected_localization": {
                "field": "head13.tensor_sha256",
                "first_diff_offset": 0,
                "diff_byte_count": 1,
                "expected_byte": before,
                "actual_byte": original[0],
            },
            "golden_export": exported,
        }
        print(f"[INFO] 反例已由驱动构造：{tamper_meta['original_head13_sha256']} -> {tamper_meta['tampered_head13_sha256']}")
    except (s4c.S4CError, s4c.UpstreamError, OSError, KeyError) as exc:
        print(f"[FAIL] 反例构造失败：{exc}")
        return 2

    # s3 --actual 正对照
    steps.append(
        run_step(
            name="s3_actual_pristine_control",
            purpose="--actual 正对照：pristine golden heads 必须 PASS",
            command=[
                python,
                "-B",
                str(TOOL),
                "--actual",
                str(pristine_dir),
                "--sample-id",
                str(tamper_meta["sample_id"]),
                "--run-id",
                run_id,
                "--json-out",
                str(evidence_dir / f"replay_actual_pristine_{tamper_meta['sample_id']}.json"),
            ],
            log_path=log_dir / "s3_actual_pristine_control.txt",
            timeout=args.timeout,
        )
    )

    # s4 --actual 反例（期望 FAIL=1）
    steps.append(
        run_step(
            name="s4_actual_tamper_1byte",
            purpose="--actual 反例：1 字节篡改必须 FAIL 并定位到样本/字段（退出码 1）",
            command=[
                python,
                "-B",
                str(TOOL),
                "--actual",
                str(tampered_dir),
                "--sample-id",
                str(tamper_meta["sample_id"]),
                "--run-id",
                run_id,
                "--json-out",
                str(evidence_dir / f"replay_actual_tamper_{tamper_meta['sample_id']}.json"),
            ],
            log_path=log_dir / "s4_actual_tamper_1byte.txt",
            expected_exit=1,
            timeout=args.timeout,
        )
    )

    # s5 篡改自检
    steps.append(
        run_step(
            name="s5_selftest_tamper",
            purpose="--self-test-tamper：全部篡改探针必须被检出（退出码 0）",
            command=[
                python,
                "-B",
                str(TOOL),
                "--self-test-tamper",
                "--tamper-dir",
                str(tmp_dir / "tamper_self_test"),
                "--run-id",
                run_id,
                "--json-out",
                str(evidence_dir / "selftest_tamper.json"),
            ],
            log_path=log_dir / "s5_selftest_tamper.txt",
            timeout=args.timeout,
        )
    )

    # s6 unittest
    if not args.skip_unittest:
        unittest_log = evidence_dir / "unittest_s4_replay_compare.txt"
        steps.append(
            run_step(
                name="s6_unittest",
                purpose="python -m unittest verification.test_s4_replay_compare -v",
                command=[python, "-B", "-m", "unittest", TEST_MODULE, "-v"],
                log_path=unittest_log,
                timeout=args.timeout,
            )
        )

    # 汇总证据
    golden = load_report(evidence_dir / "replay_golden_109.json")
    subset = load_report(evidence_dir / f"replay_subset{SUBSET_LIMIT}_seed{SUBSET_SEED}.json")
    pristine = load_report(evidence_dir / f"replay_actual_pristine_{tamper_meta.get('sample_id')}.json")
    tamper = load_report(evidence_dir / f"replay_actual_tamper_{tamper_meta.get('sample_id')}.json")
    selftest = load_report(evidence_dir / "selftest_tamper.json")
    manifest_heads = load_report(evidence_dir / "manifest_head_crosscheck.json")

    unittest_log_path = evidence_dir / "unittest_s4_replay_compare.txt"
    unittest_summary: dict[str, object] = {"executed": not args.skip_unittest}
    if unittest_log_path.is_file():
        text = unittest_log_path.read_text(encoding="utf-8")
        match = re.search(r"Ran (\d+) tests", text)
        unittest_summary.update(
            {
                "tests_run": int(match.group(1)) if match else None,
                "result": (
                    "OK"
                    if re.search(r"^OK", text, re.M)
                    else ("FAILED" if "FAILED" in text else "UNKNOWN")
                ),
            }
        )

    def summary_of(report: dict | None) -> dict[str, object] | None:
        if not report:
            return None
        summary = report.get("summary", {})
        return {
            "status": report.get("status"),
            "samples_selected": summary.get("samples_selected"),
            "samples_passed": summary.get("samples_passed"),
            "samples_failed": summary.get("samples_failed"),
            "mismatch_total": summary.get("mismatch_total"),
            "byte_mismatch_count": summary.get("byte_mismatch_count"),
            "frame_mismatch_count": summary.get("frame_mismatch_count"),
            "max_score_abs_error": summary.get("max_score_abs_error"),
            "max_xyxy_abs_error": summary.get("max_xyxy_abs_error"),
            "total_detections_expected": summary.get("total_detections_expected"),
            "total_detections_actual": summary.get("total_detections_actual"),
            "failed_sample_ids": summary.get("failed_sample_ids"),
            "selection_rule": report.get("selection", {}).get("rule"),
            "seed": report.get("selection", {}).get("seed"),
            "seed_source": report.get("selection", {}).get("seed_source"),
            "sample_ids": report.get("selection", {}).get("sample_ids"),
            "total_seconds": report.get("timing", {}).get("total_seconds"),
            "tracemalloc_peak_mib": report.get("memory", {}).get("tracemalloc_peak_mib"),
            "peak_rss_mib": report.get("memory", {}).get("peak_rss_mib"),
            "memory_measurement": report.get("memory", {}).get("measurement"),
            "upstream_paths": report.get("upstream_paths"),
            "comparison_spec": report.get("comparison_spec"),
            "upstream_bindings": report.get("upstream_bindings"),
            "limitations": report.get("limitations"),
            "not_executed": report.get("not_executed"),
        }

    tamper_localized: list[str] = []
    tamper_sample_status: dict[str, str] = {}
    tamper_byte_locators: dict[str, object] = {}
    if tamper:
        tamper_sample_status = tamper.get("per_sample_status", {})
        for sample in tamper.get("samples", []):
            tamper_localized.extend(localized_fields(sample))
            for item in sample.get("mismatches", []):
                if item.get("field") == "head13.tensor_sha256" and not tamper_byte_locators:
                    tamper_byte_locators = {
                        "first_diff_offset": item.get("first_diff_offset"),
                        "diff_byte_count": item.get("diff_byte_count"),
                        "expected_byte": item.get("expected_byte"),
                        "actual_byte": item.get("actual_byte"),
                        "max_abs_int8_delta": item.get("max_abs_int8_delta"),
                    }
        tamper_localized = sorted(set(tamper_localized))

    all_steps_ok = all(bool(step["matched_expectation"]) for step in steps)
    golden_pass = bool(golden and golden.get("status") == "PASS")
    golden_zero = bool(
        golden
        and golden.get("summary", {}).get("mismatch_total") == 0
        and golden.get("summary", {}).get("byte_mismatch_count") == 0
        and golden.get("summary", {}).get("frame_mismatch_count") == 0
    )
    tamper_failed_as_expected = bool(
        tamper
        and tamper.get("status") == "FAIL"
        and tamper_sample_status.get(str(tamper_meta.get("sample_id"))) == "FAIL"
        and any(field.startswith("head13.") for field in tamper_localized)
        and tamper_byte_locators.get("first_diff_offset")
        == (tamper_meta.get("expected_localization") or {}).get("first_diff_offset")
        and tamper_byte_locators.get("expected_byte")
        == (tamper_meta.get("expected_localization") or {}).get("expected_byte")
        and tamper_byte_locators.get("actual_byte")
        == (tamper_meta.get("expected_localization") or {}).get("actual_byte")
    )
    selftest_detected = bool(
        selftest and selftest.get("all_tamper_probes_detected") and selftest.get("exit_code") == 0
    )
    overall = (
        "PASS"
        if all_steps_ok and golden_pass and golden_zero and tamper_failed_as_expected and selftest_detected
        else "FAIL"
    )

    deliverables = [
        {"path": str(TOOL), "sha256": sha256_file(TOOL), "bytes": TOOL.stat().st_size},
        {
            "path": str(VERIFICATION / "test_s4_replay_compare.py"),
            "sha256": sha256_file(VERIFICATION / "test_s4_replay_compare.py"),
            "bytes": (VERIFICATION / "test_s4_replay_compare.py").stat().st_size,
        },
        {
            "path": str(Path(__file__).resolve()),
            "sha256": sha256_file(Path(__file__).resolve()),
            "bytes": Path(__file__).resolve().stat().st_size,
        },
    ]

    manifest = {
        "schema_version": "gestureforge_s4c_replay_run_manifest_v1",
        "task_id": "S4-C",
        "run_id": run_id,
        "status": overall,
        "started_utc8": started_utc8,
        "finished_utc8": now_utc8(),
        "git": git_info(),
        "python": sys.version.split()[0],
        "python_executable": python,
        "evidence_dir": str(evidence_dir),
        "tmp_dir": str(tmp_dir),
        "write_scopes_used": [
            "verification/s4_replay_compare.py",
            "verification/test_s4_replay_compare.py",
            "scripts/stage4_s4c/**",
            f"report/evidence/S4-C/{run_id}/**",
            f"tmp/4/S4C/{run_id}/**",
        ],
        "read_only_trees": [
            r"D:\FPGA_Competition（主树，T25 分片/索引、T29 参考、T01 清单、冻结 D9/D6）",
            r"D:\FPGA_Competition\w2b",
            r"D:\codex-worktrees\dbdf",
        ],
        "deliverables": deliverables,
        "commands": steps,
        "tamper_construction": tamper_meta,
        "results": {
            "manifest_head_crosscheck": (
                {
                    "status": manifest_heads.get("status"),
                    "failures": manifest_heads.get("failures"),
                    "manifest_sha256": manifest_heads.get("manifest_sha256"),
                    "heads": manifest_heads.get("heads"),
                }
                if manifest_heads
                else None
            ),
            "golden_109": summary_of(golden),
            "subset_seeded": summary_of(subset),
            "actual_pristine_control": summary_of(pristine),
            "actual_tamper_1byte": {
                "report": summary_of(tamper),
                "exit_code": next(
                    (step["exit_code"] for step in steps if step["step"] == "s4_actual_tamper_1byte"), None
                ),
                "expected_exit": 1,
                "per_sample_status": tamper_sample_status,
                "localized_fields": tamper_localized,
                "byte_locators": tamper_byte_locators,
                "detected_as_expected": tamper_failed_as_expected,
            },
            "selftest_tamper": (
                {
                    "exit_code": selftest.get("exit_code"),
                    "all_tamper_probes_detected": selftest.get("all_tamper_probes_detected"),
                    "probes": [
                        {
                            "probe": item.get("probe"),
                            "detected": item.get("detected"),
                            "mismatch_count": item.get("mismatch_count"),
                            "localized_fields": item.get("localized_fields"),
                            "tamper": item.get("tamper"),
                        }
                        for item in selftest.get("probes", [])
                    ],
                }
                if selftest
                else None
            ),
            "unittest": unittest_summary,
        },
        "acceptance": {
            "s1_full_109_exit_zero": next(
                (step["exit_code"] for step in steps if step["step"] == "s1_golden_full_109"), None
            )
            == 0,
            "s1_mismatch_zero": golden_zero,
            "s2_tamper_run_exit_one": next(
                (step["exit_code"] for step in steps if step["step"] == "s4_actual_tamper_1byte"), None
            )
            == 1,
            "s2_tamper_localized": tamper_failed_as_expected,
            "s2_tamper_expected_field": "head13.tensor_sha256",
            "s2_tamper_localized_fields_observed": tamper_localized,
            "s2_tamper_byte_locators_observed": tamper_byte_locators,
            "s3_unittest_ok": unittest_summary.get("result") == "OK" if not args.skip_unittest else None,
            "selftest_probes_detected": selftest_detected,
            "all_steps_matched_expectation": all_steps_ok,
        },
        "limitations": [
            "纯 CPU 离线对拍：无硬件、无 hw_server/JTAG/COM4、无 Vivado/xsim。",
            "只对拍 2A 冻结的 CPU golden；不产生精度、时序或上板结论。",
            "T25 分片按需流式读取，未复制进本工作树，也不进入 Git。",
            "S4-A 契约为 DRAFT_NOT_FROZEN：仅对齐字段名与口径，不代表阶段4 G0 冻结。",
            "不声称与 Darknet C 后处理逐值相同（2A D9 已声明奇数补边半像素差异）。",
            "阶段4 正式 UART/PL 实测联调未执行（待 S4-B 与实物）。",
        ],
        "not_executed": [
            "板上推理与实物验证（G3 不适用本任务）",
            "阶段4 正式 UART 联调与 PS 侧解码实测",
            "RTL 仿真/综合与 Vivado 流程",
        ],
    }
    s4c.write_json(evidence_dir / "s4c_run_manifest.json", manifest)

    # 人读摘要（不替代机器可读证据）
    golden_summary = manifest["results"]["golden_109"] or {}
    selftest_summary = manifest["results"]["selftest_tamper"] or {}
    subset_summary = manifest["results"]["subset_seeded"] or {}
    tamper_summary = manifest["results"]["actual_tamper_1byte"]
    md_lines = [
        f"# S4-C 离线回放与对拍 RunId `{run_id}`",
        "",
        f"- 任务：S4-C（阶段4 离线准备），状态：**{overall}**",
        f"- 开始/结束：{started_utc8} → {now_utc8()}（UTC+8）",
        f"- 执行环境：Python {sys.version.split()[0]}；纯 CPU 离线；未使用硬件/串口/Vivado/xsim",
        f"- 工作树提交：`{(manifest['git'] or {}).get('head')}`（分支 `{(manifest['git'] or {}).get('branch')}`）",
        "",
        "## 口径",
        f"- 阈值 score ≥ {0.25}（含等号），NMS IoU {0.45}，每图 ≤ {15} 框；"
        "离散字段（框数/class_id/class_name/source_order）必须完全相同。",
        "- score 与 xyxy 各分量绝对误差 ≤ 1e-6，相对容限 0（S2A-T01 规格第 75 行）。",
        "- 两头 INT8 字节 SHA 必须与 T25 索引和 T29 reference 完全一致后再解码。",
        "- 几何取 T29 `input.geometry_wh`（width,height），与 T25/T01 交叉核对。",
        "",
        "## 结果",
        f"- 全量 109 样本：{golden_summary.get('samples_passed')}/109 PASS，"
        f"mismatch={golden_summary.get('mismatch_total')}，"
        f"字节 mismatch 样本={golden_summary.get('byte_mismatch_count')}，"
        f"框 mismatch 样本={golden_summary.get('frame_mismatch_count')}，"
        f"最大 score 误差={golden_summary.get('max_score_abs_error')}，"
        f"最大坐标误差={golden_summary.get('max_xyxy_abs_error')}，"
        f"框数 {golden_summary.get('total_detections_actual')}/{golden_summary.get('total_detections_expected')}。",
        f"- 耗时 {golden_summary.get('total_seconds'):.2f}s，"
        f"tracemalloc 峰值 {golden_summary.get('tracemalloc_peak_mib'):.1f} MiB，"
        f"RSS 峰值 {golden_summary.get('peak_rss_mib'):.1f} MiB。"
        if golden_summary.get("total_seconds") is not None
        else "- 全量结果缺失。",
        f"- 子集（--limit {SUBSET_LIMIT} --seed {SUBSET_SEED}）："
        f"{subset_summary.get('samples_passed')}/{subset_summary.get('samples_selected')} PASS，"
        f"seed={subset_summary.get('seed')}（{subset_summary.get('seed_source')}），"
        f"样本：{subset_summary.get('sample_ids')}。",
        f"- --actual 正对照：{manifest['results']['actual_pristine_control'].get('status') if manifest['results']['actual_pristine_control'] else 'N/A'}"
        if manifest["results"]["actual_pristine_control"]
        else "- --actual 正对照：缺失",
        f"- 反例（驱动侧 1 字节篡改，样本 `{tamper_meta.get('sample_id')}`，"
        f"head13 字节 0 由 {tamper_meta.get('original_byte')} 改为 {tamper_meta.get('tampered_byte')}）："
        f"退出码 {tamper_summary.get('exit_code')}，定位字段 {tamper_summary.get('localized_fields')}。",
        f"- 篡改自检：全部探针检出={selftest_summary.get('all_tamper_probes_detected')}，"
        f"退出码={selftest_summary.get('exit_code')}。",
        f"- unittest：{unittest_summary.get('tests_run')} 个用例，结果 {unittest_summary.get('result')}。",
        "",
        "## 证据文件",
        "- `s4c_run_manifest.json`（机器可读总清单：命令/退出码/哈希/口径/统计）",
        "- `replay_golden_109.json`（全量 109 逐样本逐框明细）",
        f"- `replay_subset{SUBSET_LIMIT}_seed{SUBSET_SEED}.json`（种子化子集）",
        f"- `replay_actual_pristine_{tamper_meta.get('sample_id')}.json`（--actual 正对照）",
        f"- `replay_actual_tamper_{tamper_meta.get('sample_id')}.json`（--actual 反例，退出码 1）",
        "- `selftest_tamper.json`（篡改探针自检证据）",
        "- `manifest_head_crosscheck.json`（T01 manifest 头部常量交叉核对）",
        "- `unittest_s4_replay_compare.txt`（回归输出）",
        "- `console/*.txt`（每步真实 stdout/stderr 与退出码）",
        "",
        "## 限制与未执行项",
        *[f"- {item}" for item in manifest["limitations"]],
        *[f"- 未执行：{item}" for item in manifest["not_executed"]],
        "",
        "> 本摘要不替代机器可读证据，也不代表阶段4 G0/G4/G5 验收或任何实物结论。",
    ]
    (evidence_dir / "S4C_replay_summary.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"[{overall}] S4-C 驱动完成：{evidence_dir}")
    print(f"[INFO] manifest -> {evidence_dir / 's4c_run_manifest.json'}")
    for key, value in manifest["acceptance"].items():
        print(f"[INFO] 验收项 {key} = {value}")
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())