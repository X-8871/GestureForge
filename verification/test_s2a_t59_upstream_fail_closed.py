#!/usr/bin/env python3
"""对 S2A-T59 六项冻结上游逐项验证 verify-only 的失败关闭行为。"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
RUN_ROOT = ROOT / "report/evidence/S2A-T59/run07"
PREPARE_REPORT = RUN_ROOT / "prepare_summary.json"
MANIFEST_PATH = RUN_ROOT / "fixture/fixture_manifest.json"
PROJECT_PREFLIGHT = RUN_ROOT / "project_preflight_binding.json"
AUDIT_PATH = RUN_ROOT / "upstream_fail_closed_audit.json"
RUNNER_PATH = ROOT / "verification/test_s2a_conv_layer35_row23_all_channels_rtl.py"
EXPECTED_DEPENDENCIES = {
    "T16_conv_requant_proof": (
        Path(r"D:\FPGA_Competition\report\evidence\S2A-T16\conv_requant_proof.json"),
        "edd2e766278849136c806b755b275c6ad089964ff784ebe687032733f2ccbb24",
    ),
    "T17_conv_engine_evidence": (
        Path(r"D:\FPGA_Competition\report\evidence\S2A-T17\conv_engine_simulation.json"),
        "4cd1d0f0e5edf7b34907179dea47a9a9c0994eb1d8bd89adfa341067cac17ab2",
    ),
    "T20_layer_scheduler_evidence": (
        Path(r"D:\FPGA_Competition\report\evidence\S2A-T20\conv_layer_scheduler_simulation.json"),
        "d6bc16966a2d3c7707d98aafa6b435ae158cd28faa53baa8f795e13e86a17887",
    ),
    "T16_requant_proof_source": (
        Path(r"D:\FPGA_Competition\verification\s2a_conv_requant_proof.py"),
        "3bfb6d711160c21ae38147a181a042dcc5fee872d0688ae688f31e5909ebe8c9",
    ),
    "D2_forward_reference_source": (
        Path(r"D:\FPGA_Competition\verification\s1_t02_d2_int8_forward.py"),
        "5dfdbb4a9e57256b362629a2de40b9724df6d28ae225ce6d6622429b9cbad393",
    ),
    "oracle_source": (
        ROOT / "verification/test_s2a_conv_layer35_row18_all_channels_rtl.py",
        "4ec6a743d6a80c380505be2a8601879c311a7f42e07323027098c07a8dadd4f3",
    ),
}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON 根节点不是对象：{path}")
    return value


def _write_json(path: Path, value: dict[str, Any], *, exclusive: bool = False) -> None:
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    mode = "xb" if exclusive else "wb"
    with path.open(mode) as stream:
        stream.write(payload)


def _artifact(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
    }


def _record_path(record: dict[str, Any], path: Path) -> None:
    record["path"] = str(path.resolve())
    record["bytes"] = path.stat().st_size
    record["sha256"] = _sha256_file(path)


def _rebind_isolated_run(temp_run: Path, dependency_key: str,
                         dependency_path: Path) -> None:
    fixture_root = temp_run / "fixture"
    summary_path = temp_run / "prepare_summary.json"
    manifest_path = fixture_root / "fixture_manifest.json"
    preflight_path = temp_run / "project_preflight_binding.json"
    summary = _read_json(summary_path)
    manifest = _read_json(manifest_path)
    preflight = _read_json(preflight_path)

    summary["fixture"]["root"] = str(fixture_root.resolve())
    manifest["fixture_root"] = str(fixture_root.resolve())
    preflight["run_directory"] = str(temp_run.resolve())
    for name, record in summary["fixture"]["files"].items():
        _record_path(record, fixture_root / name)
    for name, record in manifest["files"].items():
        _record_path(record, fixture_root / name)

    for record in (
        summary["bindings"][dependency_key],
        manifest["preparation_inputs"][dependency_key],
        preflight["preparation_inputs"][dependency_key],
    ):
        record["path"] = str(dependency_path.resolve())
        record["sha256"] = EXPECTED_DEPENDENCIES[dependency_key][1]

    _write_json(preflight_path, preflight)
    preflight_record = _artifact(preflight_path)
    summary["project_preflight"].update(preflight_record)
    summary["bindings"]["project_preflight_binding"] = preflight_record
    manifest["project_preflight_binding"] = preflight_record
    _write_json(manifest_path, manifest)
    summary["fixture"]["manifest"] = _artifact(manifest_path)
    _write_json(summary_path, summary)


def _wrapper_source(dependency_key: str, dependency_path: Path,
                    expected_sha256: str, temp_run: Path) -> str:
    runner_literal = repr(str(RUNNER_PATH.resolve()))
    dependency_literal = repr(str(dependency_path.resolve()))
    run_literal = repr(str(temp_run.resolve()))
    preflight_literal = repr(str((temp_run / "project_preflight_binding.json").resolve()))
    fixture_literal = repr(str((temp_run / "fixture").resolve()))
    summary_literal = repr(str((temp_run / "prepare_summary.json").resolve()))
    return "\n".join((
        "import importlib.util, pathlib, sys",
        "sys.dont_write_bytecode = True",
        f"runner_path = pathlib.Path({runner_literal})",
        "spec = importlib.util.spec_from_file_location('t59_r7_verify_probe', runner_path)",
        "module = importlib.util.module_from_spec(spec)",
        "sys.modules[spec.name] = module",
        "spec.loader.exec_module(module)",
        f"module.UPSTREAM_BINDINGS[{dependency_key!r}] = (pathlib.Path({dependency_literal}), {expected_sha256!r})",
        f"module.RUN_ROOT = pathlib.Path({run_literal})",
        f"module.PROJECT_PREFLIGHT = pathlib.Path({preflight_literal})",
        f"module.FIXTURE_ROOT = pathlib.Path({fixture_literal})",
        f"module.PREPARE_REPORT = pathlib.Path({summary_literal})",
        "sys.argv = [str(runner_path), '--verify-only']",
        "raise SystemExit(module.main())",
        "",
    ))


def _run_case(dependency_key: str) -> dict[str, Any]:
    original_path, expected_sha256 = EXPECTED_DEPENDENCIES[dependency_key]
    if not original_path.is_file() or _sha256_file(original_path) != expected_sha256:
        raise RuntimeError(f"冻结依赖缺失或原始 SHA 不符：{original_path}")

    case: dict[str, Any] = {
        "dependency_key": dependency_key,
        "dependency_path": str(original_path.resolve()),
        "expected_sha256": expected_sha256,
        "expected_rejection": "exit_code=1 and structured EXPECTED_UPSTREAM_SHA_MISMATCH matches dependency key/path/SHA",
        "temp_cleanup_policy": "TemporaryDirectory 在 verify-only 子进程结束后清理",
    }
    with tempfile.TemporaryDirectory(prefix="T59-R7-upstream-") as temp_name:
        temp_root = Path(temp_name)
        temp_run = temp_root / "isolated_run07"
        shutil.copytree(RUN_ROOT, temp_run)
        temp_dependency = temp_root / "tampered_dependency.bin"
        shutil.copyfile(original_path, temp_dependency)
        with temp_dependency.open("ab") as stream:
            stream.write(b"T59-R7-ISOLATED-MUTATION")
        _rebind_isolated_run(temp_run, dependency_key, temp_dependency)
        wrapper_path = temp_root / "invoke_verify_only.py"
        wrapper_path.write_text(
            _wrapper_source(dependency_key, temp_dependency, expected_sha256, temp_run),
            encoding="utf-8",
            newline="\n",
        )
        child_env = os.environ.copy()
        child_env["PYTHONUTF8"] = "1"
        child_env["PYTHONIOENCODING"] = "utf-8:backslashreplace"
        result = subprocess.run(
            [sys.executable, "-X", "utf8", "-B", str(wrapper_path)],
            cwd=ROOT,
            env=child_env,
            capture_output=True,
            check=False,
            timeout=120,
        )
        stderr_text = result.stderr.decode("utf-8", errors="replace")
        stdout_text = result.stdout.decode("utf-8", errors="replace")
        transcript = (stderr_text + "\n" + stdout_text).strip()
        marker_lines = [line for line in transcript.splitlines()
                        if line.startswith("T59_FAILURE_JSON=")]
        failure_record = None
        if len(marker_lines) == 1:
            try:
                failure_record = json.loads(marker_lines[0].split("=", 1)[1])
            except json.JSONDecodeError:
                failure_record = None
        expected_temp_path = str(temp_dependency.resolve())
        mutated_sha256 = _sha256_file(temp_dependency)
        error_excerpt = next(
            (line.strip() for line in transcript.splitlines()
             if line.startswith("T59_FAILURE_JSON=")),
            transcript.splitlines()[0][:1200] if transcript else "",
        )
        intended_rejection = (
            result.returncode == 1 and
            isinstance(failure_record, dict) and
            failure_record.get("code") == "EXPECTED_UPSTREAM_SHA_MISMATCH" and
            failure_record.get("dependency_key") == dependency_key and
            failure_record.get("dependency_path") == expected_temp_path and
            failure_record.get("expected_sha256") == expected_sha256 and
            failure_record.get("actual_sha256") == mutated_sha256 and
            mutated_sha256 != expected_sha256
        )
        case.update({
            "temp_root_path": str(temp_root.resolve()),
            "temp_dependency_path": expected_temp_path,
            "mutated_sha256": mutated_sha256,
            "actual_exit_code": result.returncode,
            "failure_record": failure_record,
            "actual_stderr_utf8_excerpt": stderr_text[:2400],
            "actual_stdout_utf8_excerpt": stdout_text[:1200],
            "actual_error_excerpt": error_excerpt[:1200],
            "result": "PASS" if intended_rejection else "FAIL",
        })
    case["temp_path_cleaned"] = not Path(case["temp_root_path"]).exists()
    if not case["temp_path_cleaned"]:
        case["result"] = "FAIL"
    return case


def _finalize_run07(cases: list[dict[str, Any]]) -> dict[str, Any]:
    summary = _read_json(PREPARE_REPORT)
    manifest = _read_json(MANIFEST_PATH)
    source_hashes = summary.get("bindings", {}).get("T59_source_hashes", {})
    audit_payload = {
        "schema": "GestureForge-S2A-T59-upstream-fail-closed-v2",
        "task_id": "S2A-T59",
        "run_id": "run07",
        "status": "PASS" if all(case.get("result") == "PASS" for case in cases) else "FAIL",
        "verify_mode": "--verify-only",
        "audit_script_sha256": source_hashes.get(
            "verification/test_s2a_t59_upstream_fail_closed.py"),
        "mutation_policy": "仅在各自临时副本末尾追加固定字节；以 UTF-8 结构化错误码、依赖键、路径、期望/实测 SHA 与退出码判定；不修改正式冻结依赖或 run07 fixture。",
        "cases": cases,
    }
    if AUDIT_PATH.exists():
        raise RuntimeError(f"拒绝覆盖既有 run07 审计：{AUDIT_PATH}")
    _write_json(AUDIT_PATH, audit_payload, exclusive=True)
    record = _artifact(AUDIT_PATH)
    manifest["fail_closed_audit"] = record
    _write_json(MANIFEST_PATH, manifest)
    summary["fail_closed_audit"] = record
    summary["bindings"]["fail_closed_audit"] = record
    summary["fixture"]["manifest"] = _artifact(MANIFEST_PATH)
    _write_json(PREPARE_REPORT, summary)
    return record


def main() -> int:
    if not RUN_ROOT.is_dir() or not PREPARE_REPORT.is_file() or not MANIFEST_PATH.is_file():
        print("FAIL T59 R7: 缺少 prepare-only 生成的 run07 证据", file=sys.stderr)
        return 1
    if AUDIT_PATH.exists():
        print("FAIL T59 R7: 审计文件已存在，拒绝覆盖", file=sys.stderr)
        return 1
    summary = _read_json(PREPARE_REPORT)
    expected_source_sha = summary.get("bindings", {}).get(
        "T59_source_hashes", {}).get("verification/test_s2a_t59_upstream_fail_closed.py")
    if expected_source_sha != _sha256_file(Path(__file__).resolve()):
        print("FAIL T59 R7: 审计脚本 SHA 与准备摘要不匹配", file=sys.stderr)
        return 1
    if set(EXPECTED_DEPENDENCIES) != set(summary.get("bindings", {})) & set(EXPECTED_DEPENDENCIES):
        print("FAIL T59 R7: prepare_summary 缺少六项上游绑定", file=sys.stderr)
        return 1

    cases = [_run_case(key) for key in EXPECTED_DEPENDENCIES]
    record = _finalize_run07(cases)
    print(json.dumps({
        "result": "PASS" if all(case["result"] == "PASS" for case in cases) else "FAIL",
        "case_count": len(cases),
        "cases": [{
            "dependency_key": case["dependency_key"],
            "actual_exit_code": case["actual_exit_code"],
            "result": case["result"],
            "temp_path_cleaned": case["temp_path_cleaned"],
        } for case in cases],
        "audit_record": record,
    }, ensure_ascii=False, indent=2))
    return 0 if all(case["result"] == "PASS" for case in cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
