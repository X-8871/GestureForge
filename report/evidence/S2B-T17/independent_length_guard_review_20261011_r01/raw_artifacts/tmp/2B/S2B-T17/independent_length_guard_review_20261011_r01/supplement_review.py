#!/usr/bin/env python3
"""补核新r08口径关闭、独立静态反例及S5非卷积原始快照绑定。"""
import collections
import copy
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import psutil

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[3]
G1 = ROOT / "report/evidence/S2B-T17/length_guard_20261011_r08"
M = G1 / "delivery_manifest_r03.json"
EXPECTED = "748cd7d42bf8d3b641aa5d7b606b203ec008b3683c8b5f390185545c423d5bfb"
REPORT = {"status": "RUNNING", "reviewed_manifest_sha256": EXPECTED, "commands": []}

def sha(p):
    """绑定存在的实际文件。"""
    p = Path(p)
    assert p.is_file(), str(p)
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(name, value):
    """新补充原件使用UTF-8且禁止覆盖既有文件。"""
    p = WORK / name
    assert not p.exists(), str(p)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

def capture(name, command, expected):
    """直接捕获Python子进程原生退出及耗时。"""
    path = WORK / (name + ".log")
    assert not path.exists()
    begin = time.monotonic()
    with path.open("wb") as stream:
        result = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    item = {"command": command, "native_exit_code": result.returncode, "expected_native_exit_code": expected,
            "elapsed_seconds": round(time.monotonic() - begin, 3), "log": path.relative_to(ROOT).as_posix(), "sha256": sha(path)}
    REPORT["commands"].append(item)
    assert result.returncode == expected

def main():
    """所有操作均轻量，只修改本Run中的隔离静态夹具。"""
    started = time.monotonic()
    assert sha(M) == EXPECTED
    manifest = json.loads(M.read_text(encoding="utf-8"))
    for row in manifest["files"]:
        assert sha(ROOT / row["path"]) == row["sha256"], row["path"]
    freeze = json.loads((G1 / "source_freeze.json").read_text(encoding="utf-8"))
    assert sha(G1 / "source_freeze.json") == "37ed95bb84166a406589ebcba4a23c262e6d390dd1551c446988bcd222ea832b"
    old_freeze = json.loads((ROOT / "report/evidence/S2B-T17/length_guard_20261011_r07/source_freeze.json").read_text(encoding="utf-8"))
    assert freeze["source_sha256"] == old_freeze["source_sha256"]
    assert all(sha(ROOT / p) == digest for p, digest in freeze["source_sha256"].items())
    REPORT["reviewed_source_commit"] = manifest["source_commit"]
    REPORT["source_sha256"] = {p: freeze["source_sha256"][p] for p in freeze["changed_paths"]}
    REPORT["g1_bindings"] = len(manifest["files"])
    REPORT["source_freeze_sha256"] = sha(G1 / "source_freeze.json")
    current = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert not subprocess.check_output(["git", "diff", "--name-only", freeze["source_baseline_commit"], current, "--", *freeze["source_sha256"]], cwd=ROOT, text=True).strip()
    REPORT["observed_root_head"] = current
    correction = json.loads((G1 / "r01_native_exit_correction.json").read_text(encoding="utf-8"))
    r01 = correction["r01"]
    assert r01["native_exit_code"] is None and r01["native_exit_capture_status"] == "NOT_CAPTURED"
    assert r01["business_status"] == "FAIL_RESOURCE_PREFLIGHT" and r01["host_exit_code"] == 1 and r01["expected_or_inferred_native_exit_code"] == 2
    assert r01["compile_or_simulation_runs"] == [] and not r01["replayed"]
    for row in (r01["validation_binding"], r01["inference_source"]["snapshot"]):
        assert sha(ROOT / row["path"]) == row["sha256"]
    original = json.loads((ROOT / r01["validation_binding"]["path"]).read_text(encoding="utf-8"))
    source_text = (ROOT / r01["inference_source"]["snapshot"]["path"]).read_text(encoding="utf-8")
    assert original["status"] == "FAIL" and original["runs"] == [] and original["error"] == r01["observed_error"]
    assert r01["inference_source"]["return_expression"] in source_text
    for name, actual_run, exit_code in (("boundary_native", "length_guard_20261011_r03", 0), ("layer0_native", "length_guard_20261011_r04", 2)):
        row = correction["separate_captures"][name]
        assert sha(ROOT / row["path"]) == row["sha256"]
        actual = json.loads((ROOT / row["path"]).read_text(encoding="utf-8"))
        assert actual_run in actual["command"] and actual["native_exit_code"] == exit_code
    assert not any(row["name"] == "historical_ram_preflight_r01" for row in manifest["checks"])
    capture_row = next(row for row in manifest["checks"] if row["name"] == "historical_r01_native_exit_capture")
    assert capture_row["status"] == "NOT_RUN" and capture_row["exit_code"] is None
    REPORT["closed_finding"] = {"priority": "P2", "status": "CLOSED", "binding": (G1 / "r01_native_exit_correction.json").relative_to(ROOT).as_posix(),
                                "sha256": sha(G1 / "r01_native_exit_correction.json"), "basis": "r01失败事实、宿主1、未捕获native/null与源码推导2分别记录；r03/r04原生capture准确归属；旧r07原件保留。"}

    checker_path = ROOT / "verification/check_s2b_inference_platform.py"
    spec = importlib.util.spec_from_file_location("independent_static_checker", checker_path)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    actual_static = checker.check_static(ROOT)
    assert len(actual_static) == 31
    fixture = WORK / "independent_checker_fixture"
    assert not fixture.exists()
    fixture.mkdir()
    for path in actual_static:
        target = fixture / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / path, target)
    profile = json.loads((ROOT / "board/s2b_inference_platform.json").read_text(encoding="utf-8"))
    mutation_cases = (
        ("zero_factor_removed", "(input_height_latched == 32'd0)", "(input_height_latched == 32'd0 && 1'b0)"),
        ("input_plane_high_removed", "(input_element_plane[63:32] != 32'd0)", "(input_element_plane[63:32] != 32'd0 && 1'b0)"),
        ("output_plane_high_removed", "(output_element_plane[63:32] != 32'd0)", "(output_element_plane[63:32] != 32'd0 && 1'b0)"),
        ("reduction_factor_truncated", "(input_channels_latched > 32'd4608)", "(input_channels_latched[12:0] > 13'd4608)"),
        ("reduction_plane_threshold_changed", "(reduction_plane_narrow > 26'd4608)", "(reduction_plane_narrow > 26'd8192)"),
        ("weight_high_bits_removed", "(expected_weight_bytes_narrow[44:32] != 13'd0)", "(expected_weight_bytes_narrow[44:32] != 13'd0 && 1'b0)"),
        ("state_gate_removed", "if (!validation_ok) begin", "if (!validation_ok && 1'b0) begin"),
        ("generic_kernel_frozen", "(kernel_height_latched == 32'd0)", "(kernel_height_latched != 32'd3)"),
        ("extra_owner_condition", "if (result_valid && result_ready) begin", "if (result_valid && result_ready && buffer_owner_pl) begin"))
    target = "src/s2b_conv_tile_engine.sv"
    original_raw = (ROOT / target).read_bytes()
    records = []
    for name, before, after in mutation_cases:
        p = fixture / target
        assert original_raw.count(before.encode("utf-8")) == 1
        p.write_bytes(original_raw.replace(before.encode("utf-8"), after.encode("utf-8")))
        changed_profile = copy.deepcopy(profile)
        for row in changed_profile["source_derivation"]["derived_sources"]:
            if row["path"] == target:
                row["sha256"] = sha(p)
        profile_path = fixture / "board/s2b_inference_platform.json"
        profile_path.write_text(json.dumps(changed_profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        preserved = WORK / "checker_mutations" / name
        preserved.mkdir(parents=True)
        shutil.copyfile(p, preserved / "s2b_conv_tile_engine.sv")
        shutil.copyfile(profile_path, preserved / "s2b_inference_platform.json")
        try:
            checker.check_static(fixture)
        except ValueError as exc:
            records.append({"case": name, "status": "REJECTED", "message": str(exc), "mutated_source_sha256": sha(p), "self_reported_sha_updated": True})
        else:
            raise AssertionError("静态篡改反例被放行：" + name)
        p.write_bytes(original_raw)
        profile_path.write_bytes((ROOT / "board/s2b_inference_platform.json").read_bytes())
    assert checker.check_static(fixture) == actual_static
    REPORT["independent_static_negatives"] = records

    cross_path = ROOT / "report/evidence/S2B-T17/length_guard_20261011_r07/cross_version_regression.json"
    cross = json.loads(cross_path.read_text(encoding="utf-8"))
    model = json.loads((ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json").read_text(encoding="utf-8"))
    statuses = {"patch_guard_20261011_r04": "PASS_GEOMETRY_SPECIALIZATION_G1", "patch_guard_20261011_r05": "PASS_ROUTE_SPECIALIZATION_DIRECT_G1", "patch_guard_20261011_r06": "PASS_BACKEND_COORDINATES_G1"}
    audited = []
    for row in cross["integration"][1:]:
        run_id = row["run"]
        directory = ROOT / "report/evidence/S2B-T17" / run_id
        validation = json.loads((directory / "validation.json").read_text(encoding="utf-8"))
        assert validation["status"] == statuses[run_id]
        for command in validation["runs"]:
            assert command["exit_code"] == 0 and sha(ROOT / command["log"]) == command["log_sha256"]
        assert sha(directory / "simulation.log") == row["simulation_sha256"]
        command = next(r["command"] for r in validation["runs"] if r["name"] == "compile")
        assert command == row["compile_command"] and not any("s2b_conv_tile_engine.sv" in t for t in command)
        consumed = []
        for token in command:
            if not token.startswith("source/"):
                continue
            basename = Path(token).name
            snapshot = ROOT / "tmp/2B/S2B-T17" / run_id / token
            current_path = ROOT / "src" / basename
            if basename == "s2_network_backend.sv":
                assert snapshot.is_file()
                consumed.append({"path": str(snapshot.relative_to(ROOT)), "sha256": sha(snapshot), "role": "original_S2_control_baseline"})
                continue
            assert sha(snapshot) == sha(current_path) == validation["source_sha256_pre"]["src/" + basename]
            consumed.append({"path": str(snapshot.relative_to(ROOT)), "sha256": sha(snapshot), "role": "unchanged_real_nonconv_source"})
        simlog = (directory / "simulation.log").read_text(encoding="utf-8")
        actual_trace = [line for line in simlog.splitlines() if line.startswith("TRACE ")]
        assert actual_trace == row["trace_lines"]
        if run_id.endswith("r06"):
            assert len(actual_trace) == 15 and "convolution_stub.sv" in command
            parsed = [re.fullmatch(r"TRACE layer=(\d+) op=(\d+) outputs=(\d+) requests=(\d+) cycles=(\d+) digest=([0-9a-f]+)", line) for line in actual_trace]
            assert all(parsed)
            for match in parsed:
                layer, op, count, requests = map(int, match.groups()[:4])
                mr = model["layers"][layer]
                expected_count = 1
                for factor in mr["output_shape_nchw"]:
                    expected_count *= factor
                assert count == expected_count and mr["op"] in ("route", "maxpool", "upsample")
                assert requests == count * (5 if mr["op"] == "maxpool" else 2)
            assert sum(int(m[3]) for m in parsed) == row["coverage"]["nonconv_outputs"] == 5234944
            assert sum(int(m[4]) for m in parsed) == row["coverage"]["nonconv_requests"] == 12286976
        audited.append({"run_id": run_id, "status": validation["status"], "consumed_snapshot_sources": consumed,
                        "simulation_sha256": sha(directory / "simulation.log"), "coverage": row["coverage"], "trace_lines": actual_trace,
                        "scope": "绑定S5真实非CONV快照和原生结果；本轮未重跑，CONV控制stub不证明数值。"})
    REPORT["nonconv_binding"] = audited
    lintlog = (WORK / "attempt02/lint.log").read_text(encoding="utf-8")
    numeric = re.findall(r"%Warning-(WIDTHEXPAND|WIDTHTRUNC): source\\(s2[ab]_conv_tile_engine.sv):\d+:\d+: (.*)", lintlog)
    old_messages = {message for kind, path, message in numeric if path == "s2a_conv_tile_engine.sv"}
    new_messages = {message for kind, path, message in numeric if path == "s2b_conv_tile_engine.sv"}
    assert new_messages <= old_messages
    REPORT["lint_warning_audit"] = {"status": "PASS", "new_numeric_warning_messages": sorted(new_messages - old_messages),
                                    "note": "候选数值宽度警告均在旧2A存在；新增三个128位名字的高位UNUSEDSIGNAL源于兼容原时序块，非未赋值或锁存。"}
    for mode, expected in (("evidence", 0), ("inputs", 2)):
        capture("r08_" + mode, [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", mode, "--manifest", str(M)], expected)
    assert all(sha(ROOT / p) == digest for p, digest in freeze["source_sha256"].items())
    REPORT["status"] = "PASS_G2_ONLY"
    REPORT["elapsed_seconds"] = round(time.monotonic() - started, 3)
    REPORT["peak_self_working_set_bytes"] = getattr(psutil.Process().memory_info(), "peak_wset", None)
    REPORT["limitations"] = ["数学和RTL保持审查范围；源码哈希绑定r08；无综合/STA/板卡动作。", "S5几何/ROUTE/nonconv与完整非零layer0只绑定未复跑；109整网及1000次实物未执行。", "原生子进程捕获2不覆盖r01未捕获/null；本Reviewer初次EOL断言FAIL另保留。"]
    write("supplement_review_result.json", REPORT)
    print(json.dumps({"status": REPORT["status"], "g1_bindings": REPORT["g1_bindings"], "static_negatives": len(records), "nonconv_runs": len(audited), "elapsed_seconds": REPORT["elapsed_seconds"]}, ensure_ascii=False))

if __name__ == "__main__":
    main()
