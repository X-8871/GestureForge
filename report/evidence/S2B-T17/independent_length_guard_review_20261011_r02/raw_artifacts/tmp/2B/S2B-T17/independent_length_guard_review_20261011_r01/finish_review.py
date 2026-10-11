#!/usr/bin/env python3
"""冻结本独立审查回执和原始清单，不更改生产源码或Git状态。"""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import time

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[3]

def sha(path):
    """哈希实际存在的文件。"""
    path = Path(path)
    assert path.is_file(), str(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    """UTF-8读取已冻结原件。"""
    return json.loads(Path(path).read_text(encoding="utf-8"))

def write(path, obj):
    """禁止覆盖已保存的审查原件。"""
    path = Path(path)
    assert path.parent.is_dir() and not path.exists()
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

def main():
    """只读最终源和Git差异，所有输出只在允许的本Run。"""
    validation = read(WORK / "attempt02/review_result.json")
    supplement = read(WORK / "supplement_review_result.json")
    assert validation["status"] == "TECHNICAL_PASS_PENDING_EVIDENCE_CLARIFICATION"
    assert supplement["status"] == "PASS_G2_ONLY" and supplement["closed_finding"]["status"] == "CLOSED"
    m = ROOT / "report/evidence/S2B-T17/length_guard_20261011_r08/delivery_manifest_r03.json"
    freeze_path = ROOT / "report/evidence/S2B-T17/length_guard_20261011_r08/source_freeze.json"
    freeze = read(freeze_path)
    assert sha(m) == supplement["reviewed_manifest_sha256"]
    assert all(sha(ROOT / path) == digest for path, digest in freeze["source_sha256"].items())
    current = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    command = ["git", "diff", "--check", "--", *freeze["changed_paths"]]
    log = WORK / "final_diff_check.log"
    assert not log.exists()
    begin = time.monotonic()
    with log.open("wb") as stream:
        result = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    assert result.returncode == 0
    diff_receipt = {"command": command, "native_exit_code": result.returncode, "elapsed_seconds": round(time.monotonic() - begin, 3),
                    "log": log.relative_to(ROOT).as_posix(), "sha256": sha(log)}
    write(WORK / "final_diff_check_native.json", diff_receipt)
    assert not subprocess.check_output(["git", "diff", "--name-only", freeze["source_baseline_commit"], current, "--", *freeze["source_sha256"]], cwd=ROOT, text=True).strip()
    raw_name = "raw_manifest.json"
    receipt_path = WORK / "final_review_receipt.json"
    runs = validation["runs"] + supplement["commands"] + [diff_receipt]
    receipt = {
        "schema_version": 1, "task_id": "S2B-T17-S6-G2", "status": "PASS_G2_ONLY", "reviewer_state": "STOPPED_READ_ONLY_REVIEW_COMPLETE",
        "finished_utc8": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        "reviewed_manifest": m.relative_to(ROOT).as_posix(), "reviewed_manifest_sha256": sha(m),
        "reviewed_source_commit": supplement["reviewed_source_commit"], "source_baseline_commit": freeze["source_baseline_commit"],
        "observed_root_head_at_finish": current, "source_sha256": supplement["source_sha256"],
        "source_freeze_sha256": sha(freeze_path), "source_binding_count": len(freeze["source_sha256"]),
        "g1_manifest_bindings": supplement["g1_bindings"], "independent_math": validation["math"],
        "public_cycle_comparison": validation["actual_coverage"], "vector_generation": validation["vectors"],
        "independent_static_negatives": supplement["independent_static_negatives"],
        "lint": validation["lint"], "lint_warning_audit": supplement["lint_warning_audit"],
        "closed_findings": [supplement["closed_finding"]], "blocking_findings": [],
        "native_commands": runs, "resource_preflight": read(WORK / "attempt02/resource_preflight.json"),
        "layer0_bound_not_rerun": validation["layer0_binding"],
        "nonconv_bound_not_rerun": supplement["nonconv_binding"],
        "reviewer_driver_actual_native_receipts": [read(WORK / "attempt02_driver_native.json"), read(WORK / "supplement_native.json")],
        "initial_reviewer_failure": read(WORK / "initial_host_failure.json"),
        "two_always_ff_suffix_sha256": read(WORK / "attempt02/binding_audit.json")["sequential_suffix_sha256"],
        "profile": read(WORK / "attempt02/binding_audit.json")["profile"],
        "tool_versions": validation["tool_versions"], "raw_manifest": (WORK / raw_name).relative_to(ROOT).as_posix(),
        "limits": [
            "PASS只覆盖S6固定九源及r08修正后的G1证据G2，不代表50MHz综合/STA/postroute/bit/G3/G4/G5。",
            "完整sample000 layer0的1384448非零gold输出、2551955请求响应及27235743周期仅核对原日志/真实快照/独立CPU和T25绑定，Reviewer未复跑layer0或109整网。",
            "S5几何/ROUTE/15非CONV真实引擎只核对未变实际源码与快照、冻结模型计数及trace；CONV控制stub不作为CONV数值通过依据。",
            "旧14源/公开header/两个always_ff及后缀不变；仅合法validation_ok分支锁存精确R并可达后续OUTPUT_SCAN；全宽KH/KW、stride、padding语义不变。",
            "初次Reviewer的CRLF/LF原字节断言错误FAIL已保留，独立数学及原5996黄金在该次先通过；重试采用全5996原字节和3924原S5字节前缀。",
            "G1 r01原生退出未直接捕获/null，host1及源码推导2分开；r04实际native2、r06包装失败和r08首次role失败仍保留。",
            "只在本Run写入；生产九源、STATE、attrs未修改；Git仅只读，未暂存/提交/切分支；ROSS/SDK/串口/板卡动作0。",
            "新重型仅1次单job/thread编译，2次短仿真含1次故意错误预期；RAM门槛2GiB未降低，运行前无重型进程。",
            "峰RSS为0.05秒进程树采样，Python生命周期peak_wset另列，非全系统峰；全部Agent工具调用量未测。"
        ]
    }
    write(receipt_path, receipt)
    selected = {}
    for path in freeze["source_sha256"]:
        selected[ROOT / path] = "input" if path.startswith("report/") else "source"
    for p in (m, freeze_path, ROOT / supplement["closed_finding"]["binding"]):
        selected[p] = "input"
    # 对象编译缓存可重建，仅保留实际被执行的EXE、生成bench、源码及全部日志/回执。
    for p in WORK.rglob("*"):
        if not p.is_file() or p.name == raw_name:
            continue
        relative = p.relative_to(WORK)
        if "obj_dir" in relative.parts and p.name != "Vtb_s2b_conv_validation.exe":
            continue
        if p.name.endswith(".log"):
            role = "log"
        elif p.suffix in (".py", ".sv"):
            role = "source"
        elif p.name == "validation_vectors.txt":
            role = "input"
        elif "failure" in p.name or "review_result" in p.name:
            role = "diagnostic"
        else:
            role = "artifact"
        selected[p] = role
    files = [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p), "role": role} for p, role in sorted(selected.items(), key=lambda item: str(item[0]))]
    file_bytes = {p.relative_to(ROOT).as_posix(): p.stat().st_size for p in selected}
    assert all(set(row) == {"path", "sha256", "role"} for row in files)
    assert all(row["role"] in {"source", "input", "result", "log", "diagnostic", "artifact"} for row in files)
    assert receipt_path.relative_to(ROOT).as_posix() in file_bytes
    assert (WORK / raw_name).relative_to(ROOT).as_posix() not in file_bytes
    raw = {"schema_version": 1, "status": "PASS_G2_ONLY", "reviewed_manifest_sha256": sha(m),
           "reviewed_source_commit": receipt["reviewed_source_commit"], "source_sha256": receipt["source_sha256"],
           "files": files, "file_bytes": file_bytes, "limitations": receipt["limits"]}
    write(WORK / raw_name, raw)
    assert all(sha(ROOT / row["path"]) == row["sha256"] for row in files)
    assert all((ROOT / path).stat().st_size == size for path, size in file_bytes.items())
    print(json.dumps({"status": "PASS_G2_ONLY", "receipt": receipt_path.relative_to(ROOT).as_posix(), "receipt_sha256": sha(receipt_path),
                      "raw_manifest": (WORK / raw_name).relative_to(ROOT).as_posix(), "raw_manifest_sha256": sha(WORK / raw_name),
                      "raw_files": len(files), "raw_file_bytes": sum(file_bytes.values()), "reviewed_source_commit": receipt["reviewed_source_commit"],
                      "reviewed_manifest_sha256": sha(m), "source_baseline_commit": freeze["source_baseline_commit"]}, ensure_ascii=False))

if __name__ == "__main__":
    main()
