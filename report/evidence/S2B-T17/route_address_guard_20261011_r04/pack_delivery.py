#!/usr/bin/env python3
"""只封包本轮实际结果和只读来源；不复制大模型、编译缓存或旧历史。"""
from pathlib import Path
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT/"verification"))
import test_s2b_route_address_guard_rtl as direct
import test_s2b_backend_coordinates_rtl as backend

RUN = "route_address_guard_20261011_r04"
WORK = ROOT/"tmp/2B/S2B-T17"/RUN
EVIDENCE = ROOT/"report/evidence/S2B-T17"/RUN
R1 = ROOT/"report/evidence/S2B-T17/route_address_guard_20261011_r01"
R2 = ROOT/"report/evidence/S2B-T17/route_address_guard_20261011_r02"
PREVIOUS = ROOT/"report/evidence/S2B-T17/length_guard_20261011_r08"
CHANGED = ["src/s2b_route_query.sv", "src/s2b_route_engine.sv", "board/s2b_inference_platform.json",
    "board/s2b_inference_platform.md", "vivado/s2b_inference_platform.tcl", "verification/check_s2b_inference_platform.py",
    backend.RUNNER, direct.geometry.RUNNER, direct.route.RUNNER, direct.RUNNER]


def read(p):
    """UTF8读取原件。"""
    return json.loads(p.read_text(encoding="utf-8"))


def write(p, obj):
    """新文件独占创建，避免覆盖失败或完成产物。"""
    with p.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(obj, ensure_ascii=False, indent=2)+"\n")


def bind(p, role):
    """机器清单仅三个字段，bytes另表。"""
    assert p.is_file() and not p.is_symlink()
    return {"path": p.relative_to(ROOT).as_posix(), "sha256": backend.sha(p), "role": role}


def execute(name, command, expected):
    """直接捕获原生码；包装检查不推断G2或时序通过。"""
    started = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (EVIDENCE/(name+".log")).write_text(result.stdout, encoding="utf-8", newline="\n")
    record = {"name": name, "command": command, "native_exit_code": result.returncode,
        "seconds": round(time.monotonic()-started, 3), "peak_tree_rss_bytes": None,
        "capture_method": "subprocess.run.returncode", "expected_exit_code": expected}
    if result.returncode != expected: raise ValueError(record)
    return record


def checks_for(records):
    """失败的inputs2保持FAIL，未运行必须null，不把预测码写成实测。"""
    return [{"name": r["name"], "status": "PASS" if r["native_exit_code"] == 0 else "FAIL",
        "command": subprocess.list2cmdline(r["command"]), "exit_code": r["native_exit_code"],
        "reason": "原生直接捕获；inputs2因物理候选未冻结以及明确未完成检查，包装不替代G1/G2/G3"} for r in records]


def main():
    """按实际集合派生闭包并只封装本轮已执行检查。"""
    assert Path.cwd().resolve() == ROOT and WORK.is_dir() and EVIDENCE.is_dir()
    if (EVIDENCE/"source_freeze.json").exists(): raise ValueError("封包Run不可重跑")
    r1, r2 = read(R1/"validation.json"), read(R2/"validation.json")
    assert r1["status"] == "PASS_ROUTE_ADDRESS_GUARD_G1" and r2["status"] == "PASS_BACKEND_COORDINATES_G1"
    assert read(R1/"native_capture.json")["native_exit_code"] == read(R2/"native_capture.json")["native_exit_code"] == 0
    checker = backend.load_checker(); static = checker.check_static(ROOT)
    prior = read(PREVIOUS/"source_freeze.json")
    paths = list(dict.fromkeys([*static, *prior["extra_bindings_beyond_static"], direct.RUNNER]))
    sources = {p: backend.sha(ROOT/p) for p in paths}
    document_correction = {}
    for result in (r1, r2):
        assert result["source_sha256_pre"] == result["source_sha256_post"]
        for p, value in result["source_sha256_pre"].items():
            if sources[p] != value:
                assert p == "board/s2b_inference_platform.md"
                document_correction[p] = {"simulation_source_sha256": value, "final_sha256": sources[p],
                    "reason": "总控指出全局版本替换误改S5/S6历史，仿真结束后仅纠正文档，全部RTL/工具实现字节未变"}
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert head == direct.BASELINE
    unchanged_conv = "src/s2b_conv_tile_engine.sv"
    assert sources[unchanged_conv] == prior["source_sha256"][unchanged_conv]
    git_class = {}; frozen14 = {}
    s6_review = read(ROOT/"report/evidence/S2B-T17/independent_s6_synthesis_review_20261011_r01/raw_artifacts/tmp/2B/S2B-T17/independent_s6_synthesis_review_20261011_r01/r03/receipt.json")
    eol_sources = {r["path"] for r in s6_review["details"]["sources"]["results"] if r["relation"] == "GIT_LF_TO_RAW_CRLF"}
    assert len(eol_sources) == 6
    for p in paths:
        result = subprocess.run(["git", "show", head+":"+p], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        current = (ROOT/p).read_bytes()
        if result.returncode != 0:
            assert p == direct.RUNNER
            label = "NEW_SOURCE"
        elif result.stdout == current: label = "GIT_RAW_IDENTICAL"
        elif p in eol_sources and result.stdout.replace(b"\n", b"\r\n") == current: label = "GIT_LF_TO_RAW_CRLF"
        else:
            assert p in CHANGED
            label = "AUTHORIZED_MODIFICATION"
        git_class[p] = label
        if p in checker.FROZEN_CORE_SHA256:
            expected = checker.FROZEN_CORE_SHA256[p]
            git_raw = result.stdout.replace(b"\n", b"\r\n") if p in eol_sources else result.stdout
            assert result.returncode == 0 and hashlib.sha256(git_raw).hexdigest() == sources[p] == expected
            assert backend.sha(R1/"source_snapshot"/p) == expected
            frozen14[p] = expected
    diff = subprocess.check_output(["git", "diff", "--binary", head, "--", *CHANGED[:-1]], cwd=ROOT)
    new = (ROOT/direct.RUNNER).read_text(encoding="utf-8")
    diff += "".join(difflib.unified_diff([], new.splitlines(True), fromfile="/dev/null", tofile="b/"+direct.RUNNER)).encode("utf-8")
    (EVIDENCE/"source_diff.patch").write_bytes(diff)
    snapshot = {p.relative_to(R1/"source_snapshot").as_posix(): backend.sha(p) for p in (R1/"source_snapshot").rglob("*") if p.is_file()}
    assert all(sources[p] == value or p in document_correction for p, value in snapshot.items())
    encoding = {p: {"utf8": True, "replacement_character_count": (ROOT/p).read_text(encoding="utf-8").count("\ufffd")} for p in sources}
    assert all(v["replacement_character_count"] == 0 for v in encoding.values())
    records = [execute("static_checker", [sys.executable, "-B", "verification/check_s2b_inference_platform.py"], 0),
               execute("diff_check", ["git", "diff", "--check", "--", *CHANGED], 0)]
    old_backend = ROOT/"report/evidence/S2B-T17/patch_guard_20261011_r06"
    warning_pattern = r"%Warning-(?:LATCH|UNOPTFLAT|MULTIDRIVEN).*"
    old_warnings = re.findall(warning_pattern, (old_backend/"compile.log").read_text(encoding="utf-8"))
    new_warnings = re.findall(warning_pattern, (R2/"compile.log").read_text(encoding="utf-8"))
    assert old_warnings == new_warnings and len(new_warnings) == 16
    assert backend.sha(old_backend/"tb_s2b_backend_coordinates.sv") == backend.sha(R2/"tb_s2b_backend_coordinates.sv")
    assert read(old_backend/"validation.json")["trace_summaries"] == r2["trace_summaries"]
    write(EVIDENCE/"source_integrity.json", {"baseline": head, "classifications": git_class,
        "classification_counts": {k: sum(v == k for v in git_class.values()) for k in sorted(set(git_class.values()))},
        "raw_snapshot_count": len(snapshot), "raw_snapshot_sha256": snapshot, "snapshot_eol_transformation_count": 0,
        "additional_sources_bound_without_copy": [p for p in sources if p not in snapshot], "encoding": encoding,
        "original14_git_raw_and_snapshot_verified": True, "unchanged_conv_sha256": sources[unchanged_conv],
        "post_simulation_document_only_correction": document_correction,
        "structure": r1["structure"], "lint_forbidden_direct": r1["lint_forbidden"],
        "lint_forbidden_backend": new_warnings, "lint_inherited_baseline": {"log": bind(old_backend/"compile.log", "input"),
            "testbench": bind(old_backend/"tb_s2b_backend_coordinates.sv", "input"), "warnings": old_warnings,
            "new_warning_count": 0, "cause": "原测试台force/release和relational边界状态注入；backend源和TB字节未变，16条位置/文本逐条相同"}})
    freeze = {"schema_version": 1, "task_id": "S2B-T17-S7", "run_id": RUN, "freeze_state": "STOPPED_PENDING_INDEPENDENT_REVIEW",
        "source_baseline_commit": head, "source_commit_at_freeze": head, "s6_source_freeze": bind(PREVIOUS/"source_freeze.json", "input"),
        "profile_version": checker.PROFILE_VERSION, "physical_interface": "s2b-physical-candidate/0.1.1", "clock_hz": 50000000,
        "visibility_default": 0, "active_rtl_count": len(read(ROOT/"board/s2b_inference_platform.json")["rtl_sources"]),
        "static_binding_count": len(static), "source_binding_count": len(sources), "extra_bindings_beyond_static": [p for p in sources if p not in static],
        "source_sha256": sources, "frozen14_sha256": frozen14, "frozen14_unchanged": True,
        "changed_paths": CHANGED, "source_diff_sha256": backend.sha(EVIDENCE/"source_diff.patch"),
        "g1": "PASS_G1_ONLY", "g2": "NOT_RUN", "sta": "NOT_RUN", "g3": "NOT_RUN", "git_commit": "NOT_PERFORMED_ROOT_OWNS_COMMIT"}
    write(EVIDENCE/"source_freeze.json", freeze)
    checks = checks_for(records)
    for name, result, directory in (("direct_s6_s7", r1, R1), ("backend_nonconv", r2, R2)):
        for record in result["runs"]:
            assert record["exit_code"] == 0
            checks.append({"name": name+"_"+record["name"], "status": "PASS", "command": subprocess.list2cmdline(record["command"]), "exit_code": record["exit_code"]})
        native = read(directory/"native_capture.json")
        checks.append({"name": name+"_runner", "status": "PASS", "command": subprocess.list2cmdline(native["command"]), "exit_code": native["native_exit_code"]})
    checks += [{"name": name, "status": "NOT_RUN", "command": None, "exit_code": None, "reason": reason} for name, reason in
        (("S7_G2", "源码停止写入，等待总控独立Reviewer"), ("S7_STA_bit_BOARD", "总控后续执行实际STA；本轮未使用Vivado/设备"),
         ("new_CONV_layer0", "CONV源字节未改，复用S6冻结实际完整layer0数值原件，未新执行"),
         ("new_109_network_G3", "非CONV实际trace及38层控制stub不属于卷积数值整网或实板G3"))]
    write(EVIDENCE/"g1_summary.json", {"status": "PASS_G1_ONLY", "checks": checks,
        "query": r1["query_coverage"], "engine": r1["engine_coverage"], "direct_counts": r1["simulation_counts"],
        "integer_proof": r1["integer_proof"], "negative_count": len(r1["checker_negatives"]),
        "backend_counts": r2["simulation_counts"], "public_entries": r2["public_entries"], "trace_summaries": r2["trace_summaries"],
        "native_runs": r1["runs"]+r2["runs"], "new_simulation_repetitions": 2, "new_compilation_repetitions": 2,
        "agent_tool_calls": None, "global_system_peak_memory": None, "package_process_peak_memory": None})
    shutil.copyfile(Path(__file__), EVIDENCE/"pack_delivery.py")
    refs = [PREVIOUS/"delivery_manifest_r03.json", PREVIOUS/"source_freeze.json", PREVIOUS/"corrected_closure_receipt.json",
        ROOT/"report/evidence/S2B-T17/independent_length_guard_review_20261011_r01/delivery_manifest.json",
        ROOT/"report/evidence/S2B-T17/independent_s6_synthesis_review_20261011_r01/delivery_manifest_r03.json",
        ROOT/"report/evidence/S2B-T17/independent_s6_synthesis_review_20261011_r01/raw_artifacts/tmp/2B/S2B-T17/independent_s6_synthesis_review_20261011_r01/r03/receipt.json",
        ROOT/"report/evidence/S2B-T17/s6_platform_20261011_r01/s6_collection_delivery_manifest_r02.json",
        ROOT/"report/evidence/S2B-T17/s6_platform_20261011_r01/timing_worst_synth.rpt",
        ROOT/"report/evidence/S2B-T17/s6_platform_20261011_r01/timing_summary_synth.rpt",
        ROOT/"report/evidence/S2B-T17/s6_platform_20261011_r01/utilization_flat_synth.rpt",
        ROOT/"report/evidence/S2B-T17/length_guard_20261011_r05/validation.json",
        ROOT/"report/evidence/S2B-T17/length_guard_20261011_r05/simulation.log",
        ROOT/"report/evidence/S2B-T17/length_guard_20261011_r05/cpu_layer0_expected.bin",
        old_backend/"compile.log", old_backend/"tb_s2b_backend_coordinates.sv", old_backend/"validation.json",
        ROOT/"tmp/2B/S2B-T17/route_address_guard_20261011_r03/pack_delivery.py",
        ROOT/"report/evidence/S2B-T17/route_address_guard_20261011_r03/pack_native_capture.json",
        ROOT/"report/evidence/S2B-T17/route_address_guard_20261011_r03/pack_native_stdout.log",
        ROOT/"report/evidence/S2B-T17/route_address_guard_20261011_r03/source_integrity.json",
        ROOT/"report/evidence/S2B-T17/route_address_guard_20261011_r03/static_checker.log",
        ROOT/"report/evidence/S2B-T17/route_address_guard_20261011_r03/diff_check.log",
        ROOT/"report/evidence/S2B-T17/route_address_guard_20261011_r03/preparation_diagnostics.json",
        ROOT/"report/evidence/S2B-T17/route_address_guard_20261011_r03/system_preflight.json"]
    # 原CPU文件名称由既有Run枚举确认；不存在就失败，绝不猜替代。
    inputs = {p: bind(p, "input") for p in refs}
    shutil.copyfile(ROOT/"tmp/2B/S2B-T17/route_address_guard_20261011_r03/pack_delivery.py", EVIDENCE/"failed_pack_delivery_r03.py")
    shutil.copyfile(ROOT/"tmp/2B/S2B-T17/route_address_guard_20261011_r03/run_package.py", EVIDENCE/"failed_run_package_r03.py")
    for directory in (R1, R2):
        for p in directory.rglob("*"):
            if p.is_file(): inputs[p] = bind(p, "input")
    for interface in read(PREVIOUS/"delivery_manifest_r03.json")["interfaces"]:
        p = ROOT/interface["path"]; inputs[p] = bind(p, "input")
    for p in sources:
        path = ROOT/p; inputs[path] = bind(path, "input" if p == backend.MODEL else "source")
    failed = read(ROOT/"report/evidence/S2B-T17/route_address_guard_20261011_r03/pack_native_capture.json")
    checks.append({"name": "historical_r03_package_failure", "status": "FAIL", "command": subprocess.list2cmdline(failed["command"]),
        "exit_code": failed["native_exit_code"], "reason": "r03错误要求继承TB告警绝对为0；native1真实捕获。r04核对16条S5告警全文同一，无新增且无抑制，业务仿真均0"})
    def manifest(name, check_list):
        rows = dict(inputs)
        for p in EVIDENCE.rglob("*"):
            if p.is_file(): rows[p] = bind(p, "log" if p.suffix == ".log" else "diagnostic" if p.name == "source_diff.patch" else "artifact")
        obj = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T17", "run_id": RUN, "source_commit": head,
            "evidence_dir": EVIDENCE.relative_to(ROOT).as_posix(), "interfaces": read(PREVIOUS/"delivery_manifest_r03.json")["interfaces"],
            "files": sorted(rows.values(), key=lambda r: r["path"]), "checks": check_list,
            "tool_versions": r1["tool_versions"], "limitations": ["PASS_G1_ONLY；独立G2/50MHz STA/bit/BOARD/G3均NOT_RUN。",
                "39绑定为实际31static加8extra；新增专用S6/S7 runner，原14和CONV字节完整。",
                "engine时序块唯一差异为总控明确授权删除恒假四行分支，其余字节/状态/周期保持，真实逐周期差分通过。",
                "真实15非CONV trace与公共38层CONV控制stub各自按覆盖判断，不声明新卷积整网数值。",
                "S6实际完整layer0只绑定原件复用；无需重复本轮未受影响卷积数值。",
                "files仅path/sha256/role，bytes另表；原生码直接捕获，未知峰/全Agent调用量为null。",
                "不复制22MB模型、大输入/weights、整套历史、obj_dir/EXE/SDK；上游原件只绑定。",
                "cheap一次反例原因文本断言失败保留隔离tmp；未启动编译，非设计失败；r03诊断原件作input绑定。",
                "r03封包native1因把16条继承TB MULTIDRIVEN当新增；原失败保留，r04仅修口径，逐条旧日志与TB和15层trace完全相同。"]}
        write(EVIDENCE/name, obj)
        return obj
    write(EVIDENCE/"file_sizes.json", {"sources": [{"path": p, "bytes": (ROOT/p).stat().st_size} for p in sources],
        "referenced_inputs": [{"path": row["path"], "bytes": p.stat().st_size} for p, row in inputs.items()],
        "new_model_copy_bytes": 0, "snapshot_bytes": sum(p.stat().st_size for p in (R1/"source_snapshot").rglob("*") if p.is_file()),
        "compiled_cache_in_formal": False})
    manifest("delivery_manifest_r01.json", checks)
    packaging = [execute("packaging_evidence_r01", [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", "evidence", "--manifest", (EVIDENCE/"delivery_manifest_r01.json").relative_to(ROOT).as_posix()], 0),
        execute("packaging_inputs_r01", [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", "inputs", "--manifest", (EVIDENCE/"delivery_manifest_r01.json").relative_to(ROOT).as_posix()], 2)]
    write(EVIDENCE/"packaging_receipt.json", {"records": packaging, "g1": "PASS_G1_ONLY", "evidence_is_only_binding_check": True})
    manifest("delivery_manifest_r02.json", checks+checks_for(packaging))
    print(json.dumps({"status": "STOP_PASS_G1_ONLY", "source_binding_count": len(sources), "static_binding_count": len(static),
        "source_freeze_sha256": backend.sha(EVIDENCE/"source_freeze.json"), "manifest": bind(EVIDENCE/"delivery_manifest_r02.json", "artifact")}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
