"""只读核对总控最终lint包装，保存独立审查的真实范围和原件索引。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
load = lambda path: json.loads(path.read_text(encoding="utf-8"))
lint = ROOT / "report/evidence/S2B-T10/vivado_lint_20261010_r03"
report = load(HERE / "final_d3/result.json")
assert report["status"] == "PASS_FINAL_INDEPENDENT_RTL_REBUILD"
manifest = load(lint / "delivery_manifest.json")
for item in manifest["files"]:
    assert sha(ROOT / item["path"]) == item["sha256"], item["path"]
assert (lint / "linter.csv").read_bytes() == b""
for name in ("s2b_request_guard.sv", "s2b_hp0_word_adapter.sv"):
    assert sha(lint / "source_snapshot" / name) == sha(ROOT / "src" / name)
calls = load(lint / "execute_calls.json")
native = (lint / "vivado_native.log").read_text(encoding="utf-8")
execution = json.loads(calls[1]["result"]["content"][0]["text"])
assert execution["exit_code"] == 0 and execution["elapsed_seconds"] == 5.456
assert "Total of 0 linter message(s) generated" in native
assert "0 Warnings, 0 Critical Warnings and 0 Errors encountered" in native
assert "peak = 1331.348" in native
history = json.loads(load(lint / "mcp_history.json")["content"][0]["text"])
assert history["history"][1]["code"] == 0
assert json.loads(load(lint / "session_stop.json")["content"][0]["text"])["status"] == "success"
command = [sys.executable,"-B",str(ROOT / "verification/check_stage_delivery.py"),"--mode","evidence","--manifest",str(lint / "delivery_manifest.json")]
started = time.monotonic()
checked = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=60)
(HERE / "lint_final_check.log").write_bytes(checked.stdout+checked.stderr)
assert checked.returncode == 0, checked.stdout.decode("utf-8", errors="replace")
receipt = {
    "decision": "PASS", "source_commit": report["source_commit"], "interface": "s2b-physical-candidate/0.1.1 CANDIDATE_NOT_FROZEN",
    "sources": report["sources"], "inputs": report["inputs"],
    "scope": ["HP0原生AXI3单word候选RTL、公开端口测试台和runner", "guard唯一lane无符号兼容修复及独立70736条回归", "取消/故障同沿账本、持久VALID、合法早B、非法response与EXOKAY隔离、首错优先、guard错误RESP时序", "D1/D2/D3差异、r01-r09原始证据绑定、最终Vivado lint原件"],
    "findings": [], "redundancy_review": "物理地址统一消费guard核验值；无双重平移或独立业务白名单。逐通道声明/accepted/等待与逻辑RESP字段均有恢复用途，未发现需删除的冗余实现。",
    "coverage": report["coverage"], "simulation_counts": report["simulation_counts"],
    "independent_runs": {"T10": report["runs"], "guard": report["guard_regression"]["runs"], "extra": report["extra"], "elapsed_seconds": report["elapsed_seconds"]},
    "packaging": report["packaging"],
    "lint": {"source_manifest_sha256": sha(lint / "delivery_manifest.json"),"csv_bytes":0,"native_exit_code":0,"seconds":5.456,"tool_report_peak_MB":1331.348,"final_evidence_check": {"command":command,"native_exit_code":checked.returncode,"seconds":round(time.monotonic()-started,3)}},
    "closed_lint_items": ["r01 ASSIGN-1截宽地址加法：guard实际physical_addr捕获与对齐lane替换", "r01 ASSIGN-6 unused guard地址：实际消费核验后的物理addr", "r01 guard ASSIGN-2符号混用：33bit显式无符号lane拼接，独立70736回归", "r01/r02 ASSIGN-5 helper赋值：完整组合next_lane选择，r03无诊断、无waiver"],
    "historical_failures": ["D1 r01运行前FAIL；r02编译native1；r03/r04编译0仿真1；r05-r09各版本结果按snapshot区分", "独立D2额外TB实际compile0/sim0及11场景PASS，但D3编辑发生在运行中，SHA保护driver1/FAIL；原件未覆盖，不作为稳定D3通过", "lint r03首次包装checks[1] PASS却command/exit_code空；实测CHECKS_FAILED原文已反馈总控，最终包装修复后独立原生0，不改lint源码或诊断"],
    "artifacts": [{"path": str(path.relative_to(ROOT)),"sha256":sha(path)} for path in sorted((HERE / "final_d3").rglob("*")) if path.is_file() and not any(part.endswith("_cache") for part in path.parts)],
    "limitations": report["limitations"] + ["PASS仅为本候选leaf的独立G2审查；不构成完整2B、物理接口冻结、G3/G4/G5、SAFE_TO_REUSE或实板通过。", "审查未修改项目源码、STATE、被审原件或Git；由总控核对被审内容一致后统一提交。"]
}
(HERE / "review_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(receipt["decision"], sha(HERE / "review_receipt.json"))
