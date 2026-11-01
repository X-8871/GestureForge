"""在显式批准后受控启动一次 visibility=1 全量平台构建。"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import struct
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
RUN_ID = RUN.name
WORK = ROOT / "tmp/2B/S2B-T19" / RUN_ID
OUTPUT = RUN / "artifacts"
PYTHON312 = Path(r"C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe")
VIVADO_BAT = Path(r"D:\Xilinx\2026.1\Vivado\bin\vivado.bat")
IPCFG = Path(r"C:\Users\22061\.codex\plugins\cache\amd-ross-agentic-ai-assistant\amd-ross-agentic-ai-assistant\2026.9.1\skills\vivado-ip-configurator\lib\ipcfg.tcl")
T15 = ROOT / "report/evidence/S2B-T15/csr_fixed_platform_offline_20261016_r03"
T15_MANIFEST_SHA256 = "17b6c017740972565755aa2d75a1b19fb51dce3d5482de8427c465184ce71b79"
T15_FINAL_MANIFEST_SHA256 = "72fbf59b374665db43452d6ccb2ae4845b20f1042f233697a8802842771edfa9"
T15_ELFS = {
    "infer.elf": "a7fbbab2b1aecfe6b46c84118180303362483f4b7742d9e7cfe3fb59ae02ce82",
    "init.elf": "26824eb5ec3a73d3dc606b7f7797591b12ca82cf8fb8dc0e40f3a8756efaaadc",
}
ARTIFACTS = (
    "s2b_inference_no_bit.xsa", "s2b_inference.xsa", "s2b_inference.bit", "bitgen_raw.bit",
    "timing_summary_before_opt.rpt", "actual_timing_setup_before_opt.rpt",
    "actual_timing_hold_before_opt.rpt",
    "timing_summary.rpt", "actual_timing_setup.rpt", "actual_timing_hold.rpt",
    "pulse_width.rpt", "clock_interaction.rpt", "clocks.rpt", "check_timing.rpt",
    "route_status.rpt", "utilization.rpt", "drc.rpt", "methodology.rpt",
    "methodology.json", "constraints.xdc", "routed.dcp", "timing_metrics.tcldict",
)


def sha256(path: Path) -> str:
    """计算文件原始字节的 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise RuntimeError(f"缺少{label}：{path}")


def parse_bit_header(data: bytes) -> dict:
    """读取Xilinx bit文件a至e头字段和e payload。"""
    if len(data) < 16:
        raise ValueError("bit文件短于头部")
    cursor = 0

    def u16() -> int:
        nonlocal cursor
        if cursor + 2 > len(data):
            raise ValueError("u16头字段越界")
        value = struct.unpack_from(">H", data, cursor)[0]
        cursor += 2
        return value

    if u16() != 9:
        raise ValueError("Xilinx magic长度错误")
    magic = data[cursor:cursor + 9]
    cursor += 9
    if len(magic) != 9 or u16() != 1:
        raise ValueError("Xilinx bit字段起始标记错误")
    fields = {}
    ranges = {}
    for expected in "abcd":
        if cursor >= len(data) or chr(data[cursor]) != expected:
            raise ValueError(f"Xilinx bit字段顺序错误：{expected}")
        cursor += 1
        length = u16()
        start = cursor
        end = start + length
        if end > len(data) or length == 0 or data[end - 1] != 0:
            raise ValueError(f"Xilinx bit字段内容错误：{expected}")
        fields[expected] = data[start:end - 1]
        ranges[expected] = (start, end)
        cursor = end
    if cursor >= len(data) or chr(data[cursor]) != "e":
        raise ValueError("Xilinx bit缺少字段e")
    cursor += 1
    if cursor + 4 > len(data):
        raise ValueError("Xilinx bit字段e长度越界")
    payload_length = struct.unpack_from(">I", data, cursor)[0]
    cursor += 4
    if payload_length != len(data) - cursor:
        raise ValueError("Xilinx bit字段e长度不匹配")
    return {"magic": magic, "fields": fields, "field_ranges": ranges,
            "payload": data[cursor:], "payload_offset": cursor}


def reconcile_xsa_bit() -> dict:
    """以XSA内部bit为canonical并证明仅日期/时间头字段可变化。"""
    xsa = OUTPUT / "s2b_inference.xsa"
    raw_path = OUTPUT / "bitgen_raw.bit"
    canonical_path = OUTPUT / "s2b_inference.bit"
    if not xsa.is_file() or not raw_path.is_file():
        raise ValueError("缺少XSA或bitgen raw bit")
    if canonical_path.exists():
        raise ValueError("canonical bit目标已存在，拒绝覆盖")
    with zipfile.ZipFile(xsa) as archive:
        entries = [name for name in archive.namelist() if name.lower().endswith(".bit")]
        if len(entries) != 1 or Path(entries[0]).name != "s2b_inference.bit":
            raise ValueError(f"XSA必须含唯一s2b_inference.bit：{entries}")
        canonical = archive.read(entries[0])
    raw = raw_path.read_bytes()
    raw_info = parse_bit_header(raw)
    canonical_info = parse_bit_header(canonical)
    if raw_info["magic"] != canonical_info["magic"]:
        raise ValueError("raw与XSA bit magic不等")
    if raw_info["fields"]["a"] != canonical_info["fields"]["a"]:
        raise ValueError("raw与XSA bit设计字段a不等")
    if raw_info["fields"]["b"] != canonical_info["fields"]["b"]:
        raise ValueError("raw与XSA bit器件字段b不等")
    if raw_info["payload"] != canonical_info["payload"]:
        raise ValueError("raw与XSA bit字段e payload不相等")
    differing = [index for index, pair in enumerate(zip(raw, canonical)) if pair[0] != pair[1]]
    if len(raw) != len(canonical):
        raise ValueError("raw与XSA bit文件长度不等")
    date_time = (raw_info["field_ranges"]["c"], raw_info["field_ranges"]["d"])
    if any(not any(start <= offset < end for start, end in date_time) for offset in differing):
        raise ValueError(f"raw与XSA bit头差异超出日期/时间字段c/d：{differing}")
    canonical_path.write_bytes(canonical)
    return {
        "status": "PASS_HEADER_AND_PAYLOAD_RECONCILED",
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "canonical_sha256": hashlib.sha256(canonical).hexdigest(),
        "xsa_entry": entries[0],
        "design_field_a_equal": True,
        "part_field_b_equal": True,
        "date_field_c_raw": raw_info["fields"]["c"].decode("ascii"),
        "date_field_c_xsa": canonical_info["fields"]["c"].decode("ascii"),
        "time_field_d_raw": raw_info["fields"]["d"].decode("ascii"),
        "time_field_d_xsa": canonical_info["fields"]["d"].decode("ascii"),
        "differing_file_offsets": differing,
        "e_payload_length": len(canonical_info["payload"]),
        "e_payload_sha256": hashlib.sha256(canonical_info["payload"]).hexdigest(),
        "e_payload_byte_equal": True,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proof", type=Path, required=True, help="visibility=1 证明 JSON")
    parser.add_argument("--review", type=Path, required=True, help="独立审查原件 JSON")
    parser.add_argument("--review-sha256", required=True, help="总控固定的审查原件 SHA-256")
    parser.add_argument("--budget-approval", required=True, help="总控批准本次额外综合预算的回执标识")
    parser.add_argument("--execute", action="store_true", help="显式执行一次重型构建；省略时仅做准入检查")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if sys.executable.lower() != str(PYTHON312).lower():
        raise RuntimeError(f"必须由固定 Python312 启动：{PYTHON312}")
    if not args.proof.is_absolute() or not args.review.is_absolute():
        raise RuntimeError("proof与review必须以已核验的绝对路径原样传入")
    if not re.fullmatch(r"[0-9a-f]{64}", args.review_sha256):
        raise RuntimeError("独立审查 SHA-256 必须为64位小写十六进制")
    if not args.budget_approval.strip():
        raise RuntimeError("缺少总控对额外综合预算的批准回执标识")
    if args.execute is not True:
        print("PREFLIGHT_ONLY:NOT_RUN；未传 --execute，不启动重型构建。")
        return 0

    require_file(args.proof, "可见性证明")
    require_file(args.review, "独立审查原件")
    require_file(VIVADO_BAT, "Vivado 2026.1 启动器")
    require_file(IPCFG, "已审 IP 配置 helper")
    require_file(T15 / "delivery_manifest.json", "T15 原始交付清单")
    if sha256(T15 / "delivery_manifest.json") != T15_MANIFEST_SHA256:
        raise RuntimeError("T15 原始清单哈希变化，停止执行")
    require_file(T15 / "final_delivery_manifest.json", "T15 补充交付清单")
    if sha256(T15 / "final_delivery_manifest.json") != T15_FINAL_MANIFEST_SHA256:
        raise RuntimeError("T15 补充交付清单哈希变化，停止执行")
    elf_hashes = {}
    for name, expected in T15_ELFS.items():
        path = T15 / "artifacts" / name
        require_file(path, f"T15 {name}")
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"T15 {name} 哈希变化，停止执行")
        elf_hashes[name] = actual

    checker = ROOT / "verification/check_s2b_inference_platform.py"
    checker_result = subprocess.run(
        [str(PYTHON312), str(checker), "--root", str(ROOT),
         "--visibility-proof", str(args.proof), "--review", str(args.review),
         "--review-sha256", args.review_sha256],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False,
    )
    if checker_result.returncode != 0 or checker_result.stdout.strip() != "VISIBILITY_PROFILE:BINDINGS_VERIFIED":
        raise RuntimeError(f"可见性准入检查失败：{checker_result.stdout}{checker_result.stderr}")

    import psutil
    sys.path.insert(0, str(ROOT / "verification"))
    from s2b_process_supervisor import GIB, supervise_process

    active = []
    for process in psutil.process_iter(("pid", "name", "cmdline")):
        try:
            name = (process.info.get("name") or "").lower()
            command = " ".join(process.info.get("cmdline") or []).lower()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
        if not name.startswith("vivado-mcp-server-") and (
            "vivado" in name or ("vivado" in command and ("-mode tcl" in command or "vivado.bat" in command))
        ):
            active.append({"pid": process.info.get("pid"), "name": name})
    if active:
        raise RuntimeError(f"检测到其他 Vivado 进程；单重型门禁拒绝启动：{active}")
    if WORK.exists():
        raise RuntimeError(f"本 RunId 临时目录已存在，拒绝覆盖：{WORK}")
    if OUTPUT.exists():
        raise RuntimeError(f"本 RunId 构建输出目录已存在，拒绝覆盖：{OUTPUT}")
    for name in ARTIFACTS:
        if (RUN / name).exists():
            raise RuntimeError(f"检测到目标目录已有同名构建产物，拒绝覆盖：{RUN / name}")

    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
                            encoding="ascii", capture_output=True, check=True).stdout.strip()
    if len(commit) != 40:
        raise RuntimeError("当前 Git HEAD 无法固定")
    source_bindings = {}
    profile = json.loads((ROOT / "board/s2b_inference_platform.json").read_text(encoding="utf-8"))
    for relative in profile["rtl_sources"] + profile["build_scripts"] + [
        "board/s2b_inference_platform.json", "board/s2b_inference_platform.md",
        "board/ps_platform_fields.json", "verification/check_s2b_inference_platform.py",
        "verification/s2b_process_supervisor.py", "verification/s15_job_guard.py",
    ]:
        path = ROOT / relative
        require_file(path, f"來源檔 {relative}")
        source_bindings[relative] = sha256(path)

    WORK.mkdir(parents=True, exist_ok=False)
    output_stream_path = RUN / "vivado.stdout.log"
    native_log_path = WORK / "vivado.native.log"
    build_tcl = RUN / "build_visibility1.tcl"
    if not build_tcl.is_file():
        raise RuntimeError(f"缺少構建 Tcl：{build_tcl}")
    build_cmd = WORK / "build_visibility1.cmd"
    cmd_values = [VIVADO_BAT, build_tcl, ROOT, WORK / "project", OUTPUT, IPCFG,
                  native_log_path, args.proof, args.review]
    if any(re.search(r'["%\r\n]', str(value)) for value in cmd_values):
        raise RuntimeError("Windows批处理参数含有引号、百分号或换行，拒绝启动")
    command_line = (
        f'@echo off\r\ncall "{VIVADO_BAT}" -mode tcl -notrace -source "{build_tcl}" '
        f'-tclargs "{ROOT}" "{WORK / "project"}" "{OUTPUT}" "{IPCFG}" '
        f'"{native_log_path}" "{args.proof}" "{args.review}" {args.review_sha256}\r\n'
        'exit /b %ERRORLEVEL%\r\n'
    )
    with build_cmd.open("x", encoding="ascii", newline="") as stream:
        stream.write(command_line)
    native_log_path.write_bytes(b"")
    command = [str(Path(os.environ["SystemRoot"]) / "System32/cmd.exe"), "/d", "/c", str(build_cmd)]
    input_record = {
        "status": "RUNNING", "hardware_execution": "NOT_RUN",
        "current_source_commit": commit, "source_sha256": source_bindings,
        "visibility_parameter": 1, "part": "xc7z020clg400-2", "clock_mhz": 50,
        "ddr_manual_reference": "MT41K256M16TW-107",
        "t15_manifest_sha256": T15_MANIFEST_SHA256,
        "t15_final_manifest_sha256": T15_FINAL_MANIFEST_SHA256,
        "t15_elf_sha256": elf_hashes,
        "visibility_proof": str(args.proof), "review": str(args.review),
        "review_sha256": args.review_sha256, "budget_approval_ref": args.budget_approval,
        "budget": {"single_heavy_job": True, "start_floor_bytes": int(4.5 * GIB),
                   "stop_floor_bytes": 2 * GIB, "timeout_seconds": 1800,
                   "sample_interval_seconds": 0.25, "max_sample_gap_seconds": 1.0},
        "command": command, "build_cmd": str(build_cmd), "working_directory": str(WORK),
        "vivado_bat_sha256": sha256(VIVADO_BAT), "ipcfg_sha256": sha256(IPCFG),
        "build_tcl_sha256": sha256(build_tcl), "build_cmd_sha256": sha256(build_cmd),
        "proof_sha256": sha256(args.proof),
        "review_file_sha256": sha256(args.review),
        "note": "visibility=1 新BD与实现XSA仅用于兼容桥及PL位流；沿用T15原ELF，不重建PS/BSP。",
    }
    with (RUN / "input_record.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(input_record, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    with output_stream_path.open("xb") as output_stream:
        job = supervise_process(
            name="s2b_inference_visibility1_full_synthesis_implementation",
            command=command,
            cwd=str(WORK), environment=dict(os.environ), output_stream=output_stream,
            timeout_seconds=1800, sample_interval_seconds=0.25,
            max_sample_gap_seconds=1.0, start_floor_bytes=int(4.5 * GIB),
            stop_floor_bytes=2 * GIB,
        )
    input_record["job"] = job
    input_record["source_bindings_unchanged"] = all(
        sha256(ROOT / relative) == expected for relative, expected in source_bindings.items()
    )
    input_record["proof_review_unchanged"] = (
        sha256(args.proof) == input_record["proof_sha256"]
        and sha256(args.review) == input_record["review_file_sha256"]
    )
    native_text = native_log_path.read_text(encoding="utf-8", errors="replace")
    stdout_text = output_stream_path.read_text(encoding="utf-8", errors="replace")
    input_record["native_log_sha256"] = sha256(native_log_path)
    input_record["stdout_log_sha256"] = sha256(output_stream_path)
    input_record["stdout_has_profile_bindings"] = "VISIBILITY_PROFILE:BINDINGS_VERIFIED" in stdout_text
    input_record["stdout_has_platform_proof"] = "VISIBILITY1_PLATFORM_PROOF_ACCEPTED" in stdout_text
    input_record["stdout_has_synth_complete"] = "CHECKPOINT SYNTH_COMPLETE" in stdout_text
    input_record["stdout_has_route_artifacts"] = "CHECKPOINT ROUTED_ARTIFACTS_WRITTEN" in stdout_text
    input_record["stdout_has_final_sentinel"] = "PASS_VISIBILITY1_FULL_SYNTH_IMPL_TIMING_REVIEW_PENDING" in stdout_text
    input_record["stdout_has_failure"] = "VISIBILITY1_BUILD_FAILED:" in stdout_text
    try:
        input_record["bit_header_reconciliation"] = reconcile_xsa_bit()
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        input_record["bit_header_reconciliation"] = {"status": "FAIL", "error": repr(error)}
    input_record["artifact_sha256"] = {}
    input_record["artifact_sizes"] = {}
    missing = []
    for name in ARTIFACTS:
        path = OUTPUT / name
        if not path.is_file() or path.stat().st_size == 0:
            missing.append(name)
        else:
            input_record["artifact_sha256"][name] = sha256(path)
            input_record["artifact_sizes"][name] = path.stat().st_size
    input_record["missing_or_empty_artifacts"] = missing
    metrics_path = OUTPUT / "timing_metrics.tcldict"
    metrics_text = metrics_path.read_text(encoding="utf-8", errors="replace") if metrics_path.is_file() else ""
    metric_values = {}
    for metric in ("setup_slack", "hold_slack"):
        match = re.search(rf"(?:^|\s){metric}\s+\{{?(-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\}}?(?=\s|$)", metrics_text)
        if match:
            metric_values[metric] = float(match.group(1))
    input_record["timing_slack_values"] = metric_values
    initial_metric_values = {}
    for metric in ("initial_setup_slack", "initial_hold_slack"):
        match = re.search(rf"(?:^|\s){metric}\s+\{{?(-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\}}?(?=\s|$)", metrics_text)
        if match:
            initial_metric_values[metric] = float(match.group(1))
    input_record["initial_timing_slack_values"] = initial_metric_values
    phys_opt_match = re.search(r"(?:^|\s)post_route_phys_opt_ran\s+(true|false)(?=\s|$)", metrics_text)
    input_record["post_route_phys_opt_ran"] = phys_opt_match.group(1) == "true" if phys_opt_match else None
    initial_sta_recorded = set(initial_metric_values) == {"initial_setup_slack", "initial_hold_slack"}
    initial_sta_requires_opt = initial_sta_recorded and any(value < 0 for value in initial_metric_values.values())
    input_record["post_route_opt_condition_satisfied"] = (
        initial_sta_recorded and input_record["post_route_phys_opt_ran"] is not None
        and input_record["post_route_phys_opt_ran"] == initial_sta_requires_opt
    )
    input_record["timing_slacks_nonnegative"] = (
        set(metric_values) == {"setup_slack", "hold_slack"}
        and all(value >= 0 for value in metric_values.values())
    )
    xsa = OUTPUT / "s2b_inference.xsa"
    input_record["xsa_contains_bit"] = False
    input_record["xsa_bit_matches_standalone"] = False
    if xsa.is_file() and xsa.stat().st_size > 0:
        try:
            with zipfile.ZipFile(xsa) as archive:
                input_record["xsa_contents"] = archive.namelist()
                bit_entries = [name for name in archive.namelist() if name.lower().endswith(".bit")]
                input_record["xsa_contains_bit"] = len(bit_entries) == 1
                standalone_bit = OUTPUT / "s2b_inference.bit"
                input_record["xsa_bit_sha256"] = hashlib.sha256(archive.read(bit_entries[0])).hexdigest() if len(bit_entries) == 1 else None
                input_record["standalone_bit_sha256"] = sha256(standalone_bit) if standalone_bit.is_file() else None
                input_record["xsa_bit_matches_standalone"] = (
                    len(bit_entries) == 1 and standalone_bit.is_file()
                    and input_record["xsa_bit_sha256"] == input_record["standalone_bit_sha256"]
                )
        except zipfile.BadZipFile:
            input_record["xsa_contents"] = []
    input_record["status"] = "PASS_ARTIFACTS_PENDING_INDEPENDENT_REVIEW" if (
        job.get("status") == "PASS" and job.get("exit_code") == 0
        and job.get("cleanup_confirmed") is True
        and input_record["source_bindings_unchanged"] and input_record["proof_review_unchanged"]
        and input_record["stdout_has_profile_bindings"]
        and input_record["stdout_has_platform_proof"] and input_record["stdout_has_synth_complete"]
        and input_record["stdout_has_route_artifacts"] and input_record["stdout_has_final_sentinel"]
        and not input_record["stdout_has_failure"] and not missing
        and input_record["post_route_opt_condition_satisfied"]
        and input_record["timing_slacks_nonnegative"] and input_record["xsa_contains_bit"]
        and input_record["xsa_bit_matches_standalone"]
        and input_record["bit_header_reconciliation"].get("status") == "PASS_HEADER_AND_PAYLOAD_RECONCILED"
    ) else "FAIL"
    with (RUN / "input_record.json").open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(input_record, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return 0 if input_record["status"] == "PASS_ARTIFACTS_PENDING_INDEPENDENT_REVIEW" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"VISIBILITY1_BUILD_REFUSED: {error}", file=sys.stderr)
        raise SystemExit(2)
