"""冻结独立G2回执和原字节清单；不自引用清单SHA，不修改被审源。"""

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

RUN = Path(__file__).absolute().parent
ROOT = RUN.parents[3]
BASE = "140e5f6b7c4511b0a0699fab3a91b87de2faf381"
REVIEWED = "7eba2c2962d59633f753cf8b54d61fdf19b89f5f9de419fb920b41894769e6de"
SOURCES = {
    "verification/s2b_board_jtag.py": "06c1f46d9906d39e76f9befddcdb50eaf20cf485ddb5e5d48145ab0553143432",
    "verification/test_s2b_board_jtag.py": "4c8c65ce8ce0314962cae59d58f40e67ac2b531d101e2dfffaba45ce0654d18e",
    "verification/test_s2b_cold_observation.py": "89d5258678d3f30f83d241a7dade6dff2bcc7246b1a359da5a7be79acfe4ff2c",
    "vitis/run_s2b_visibility_probe.py": "d1fc585ff6d0a26c2d13b8bbb7f476357347dbce274489b1cc5906045730fe8d",
    "verification/test_s2b_visibility_probe.py": "5fbdc4f4743325b89b00be570df0e0ce2ac1b084e9c6e64a536c6f70f3dd18fe",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, obj):
    with (RUN / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def load(name):
    return json.loads((RUN / name).read_text(encoding="utf-8"))


for name, digest in SOURCES.items():
    assert sha(ROOT / name) == digest
    assert sha(RUN / "attempt_r02/source_snapshot" / name) == digest
assert sha(ROOT / "report/evidence/S2B-T16/postconfig_20261011_r02/delivery_manifest.json") == REVIEWED
primary = load("independent_r02_native.json")
supplement = load("supplement_native.json")
first = load("independent_r01_native.json")
assert first["native_exit_code"] == 1
assert primary["native_exit_code"] == supplement["native_exit_code"] == 0
cases = load("attempt_r02/independent_cases_summary.json")
tests = load("supplement_test_result.json")
assert cases["status"] == tests["status"] == "PASS"
offsets = set()
for path in (RUN / "supplement_fixtures").rglob("jtag_calls.jsonl"):
    for row in path.read_text(encoding="utf-8").splitlines():
        call = json.loads(row)
        match = re.search(r"独立逐调用异常 ([0-9]+)", call.get("exception_repr", ""))
        if match:
            offsets.add(int(match.group(1)))
assert offsets == set(range(83)), sorted(offsets)
snapshot_dir = RUN / "input_snapshot"
snapshot_dir.mkdir()
xsa = ROOT / "report/evidence/S2B-T13/artifact_recheck_20261011_r01/s2b_inference_no_bit.xsa"
with (snapshot_dir / xsa.name).open("xb") as stream:
    stream.write(xsa.read_bytes())
assert sha(snapshot_dir / xsa.name) == "6cff0c6afd009bf051028c4b793cc99c3c0c700002c2fdb2d247a33d2fc076a7"
save("official_independent_excerpts.json", {
    "status": "CHECKED_PRIMARY_AMD_UG585_1_15", "date_utc8": "2026-10-11", "release_date": "2026-02-06",
    "sources": [
        {"url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Register-SLCR_LOCKSTA-Details?contentId=0quLiBIv~vnI8GvNlY3btw",
         "excerpt": "0: Registers are writeable. 1: Registers are not writeable.", "field": "LOCK_STATUS bit0; reset1; read-only"},
        {"url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Register-SLCR_UNLOCK-Details",
         "excerpt": "A read of this register returns zero.", "key": "0xDF0D", "type": "write-only"},
        {"url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Register-SLCR_LOCK-Details",
         "excerpt": "A read of this register returns zero.", "key": "0x767B", "type": "write-only"},
        {"url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/PS-PL-Voltage-Level-Shifter-Enables",
         "excerpt": "enable the level shifters after the PL is powered up and before the signals are used."},
    ],
    "retrieval_failure_preserved": {"url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Register-SLCR_LOCKSTA-Details",
         "tool_result": "Internal Error; URL not accessible via this tool", "recovered": "使用交付包原queryURL获得完整15行寄存器字段"},
    "scope": "官网仅核对寄存器语义；四动作与32位reset来自已绑定XSA生成C/H/Tcl，而非网站推断。"
})
save("failed_attempt_explanation.json", {
    "collector_r01_native_exit_code": 1,
    "collector_failure": "Reviewer误读consumer_binding.json字段sdk_files；实际为sdk_file_closure。",
    "collector_close_condition": "新attempt_r02使用实际字段，192真实文件逐文件SHA/bytes通过；首次脚本和native/stdout/stderr保留。",
    "changed_second_script": "同时将独立Tcl核对中的假设mww修正为实际生成mwr -force，仅核对字符串而不执行Tcl。",
    "production_issue": False,
    "bootstrap_tool_failures": [
        {"command": ["exec_command", "shell=C:\\Program Files\\Git\\bin\\bash.exe", "pwd -P and three startup reads"],
         "native_exit_code": 1, "diagnostic": "Windows宿主未按shell参数执行Git Bash，pwd未识别。"},
        {"command": ["exec_command", "quoted bash executable without PowerShell call operator"],
         "native_exit_code": 1, "diagnostic": "PowerShell ParserError: Unexpected token noprofile in expression or statement."}
    ],
    "bootstrap_limit": "两个工具初始化错误的原始字节未由工具提供，仅保留解码诊断与工具报告退出码；后续所有原生验证stdout/stderr完整落盘。"
})
head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, check=True).stdout.decode("utf-8").strip()
receipt = {
    "status": "PASS_G2_ONLY", "reviewed_manifest_sha256": REVIEWED, "reviewed_source_commit": BASE,
    "source_sha256": SOURCES, "reviewed_head_at_close": head, "findings": [],
    "finished_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
    "scope": "S2B-T16/T19 EOS1→公开APU postconfig→冷CSR→app的本轮五源软件G2；不批准真实runtime、统一冷生命周期或阶段2B验收。",
    "reviewed_changes": {"files": 5, "insertions": 480, "deletions": 11, "all_diff_read": True},
    "executed": {
        "independent_scenarios": cases["scenarios"], "independent_simulated_api_calls": cases["mock_api_calls"],
        "independent_command": primary["command"], "independent_native_exit_code": primary["native_exit_code"],
        "independent_elapsed_seconds": primary["elapsed_seconds"],
        "supplement_methods": tests["methods"], "supplement_retained_logs": tests["retained_jtag_call_logs"],
        "supplement_simulated_api_calls": tests["simulated_api_calls"],
        "supplement_command": supplement["command"], "supplement_native_exit_code": supplement["native_exit_code"],
        "supplement_elapsed_seconds": supplement["elapsed_seconds"], "postconfig_native_fault_offsets": sorted(offsets),
        "peak_single_process_working_set_bytes": max(primary["peak_single_process_working_set_bytes"], supplement["peak_single_process_working_set_bytes"]),
        "peak_process_tree_bytes": None, "real_sdk_imports": 0, "real_sdk_calls": 0, "real_serial_open": 0,
        "hardware_operations": 0, "evidence_native_exit_code": 0, "inputs_native_exit_code": 2,
        "inputs_status": "FAIL", "bound_files_checked": 65, "sdk_file_count": 192, "sdk_definition_count": 23,
        "sdk_definition_breakdown": {"main": 19, "tcf_reset": 2, "breakpoint": 2},
        "five_sdk_gate_ast_unchanged_from_baseline": True,
        "actual_xsa_three_c_tcl_postconfig_tables": True, "actual_hwh_clock_reset_connections_and_polarity": True,
        "actual_csr_cold_defaults": True, "developer_six_raw_calls_semantically_checked": 673
    },
    "bound_but_not_reexecuted": {
        "full_G1_methods": 103, "full_G1_native_exit_code": 0, "full_G1_elapsed_seconds": 555.234,
        "consumer_methods": 81, "consumer_native_exit_code": 0, "consumer_elapsed_seconds": 46.729,
        "reason": "原件/源SHA/原生日志已经绑定并只读核查；本Reviewer另运行必要轻量新反例与受影响方法，未重复完整9分钟或消费者回归。"
    },
    "coverage_notes": [
        "四write精确为UNLOCK DF0D、LEVEL低4位RMW F且保留高位、RESET完整32位零、LOCK767B；LOCKSTA bit0证明锁状态。",
        "PS_VERSION高nibble选择三实际生成分支，else按生成实现仍选3.0；clock参数/PLL低3位读回且不宣称频率实测。",
        "失败禁止app/继续/重复deploy；解锁部分成功后仅原身份与文件门禁成立且LOCKSTA解锁时重锁，不重解锁/reset/resume。原异常与cleanup异常分别保留。",
        "两份完整CSR ID/ABI/idle/epoch/owner/head/ledger/default稳定后才app；cold_defaults只用于postconfig门禁，常规cache/dapabort snapshot未扩展。",
        "T19固定helper pin、要求并保存postconfig PASS；三postconfig失败场景wire持久失败且无app下载/继续/请求。CPU1从不resume。",
        "G1六代表mock raw逐调用条数、返回、异常、读回与结果一致；不计为真实SDK。"
    ],
    "limitations": [
        "G3硬件、runtime兼容批准、cache/model/1000次验收均不在本审查；cold_lifecycle_proven始终false。",
        "physical0.1.1仍未冻结，inputs原生2/FAIL真实保留，包装0不等于G0/G4/G5。",
        "核状态和身份仅离散观察；FCLK寄存器/HWH不证明板上真实频率。",
        "测试仅重定向并保留临时目录，生产源与测试源未改；部分mock夹具被测试主动改写，改写前构造规则见固定测试源码，不能把重构称为当时快照。",
        "内存峰仅两主Python子进程0.25s采样；整个进程树及审查总墙钟时间、总工具调用数未测。",
        "首个Reviewer collector原生1及初始化工具错误保留；不是生产缺陷或硬件失败。"
    ],
    "raw_evidence_dir": str(RUN), "stop_writing_after_manifest": True
}
save("review_receipt.json", receipt)
paths = sorted(path for path in RUN.rglob("*") if path.is_file())
files = []
sizes = {}
for path in paths:
    relative = path.relative_to(ROOT).as_posix()
    if path.suffix == ".py" or "source_snapshot" in path.parts or path.suffix in (".c", ".h", ".sv", ".tcl"):
        role = "source"
    elif path.suffix == ".log":
        role = "log"
    elif path.suffix in (".xsa", ".hwh") or path.name in ("init_elf", "app_elf", "xsa", "bit", "csr_source", "interface", "sdk_target"):
        role = "input"
    else:
        role = "result"
    files.append({"path": relative, "sha256": sha(path), "role": role})
    sizes[relative] = path.stat().st_size
raw_manifest = {"status": "PASS_G2_ONLY", "reviewed_manifest_sha256": REVIEWED,
                "reviewed_source_commit": BASE, "source_sha256": SOURCES, "files": files,
                "file_bytes": sizes, "total_bytes": sum(sizes.values()), "file_count": len(files),
                "excluded": ["raw_manifest.json itself; no self-reference"],
                "source_scope": "本Run全部原件、失败首试、独立脚本、native/stdout/stderr、SDK/XSA摘录与五源快照；无objcache或真实模型数据。"}
save("raw_manifest.json", raw_manifest)
print(json.dumps({"status": "PASS_G2_ONLY", "receipt_sha256": sha(RUN / "review_receipt.json"),
                  "raw_manifest_sha256": sha(RUN / "raw_manifest.json"), "files": len(files),
                  "bytes": sum(sizes.values()), "reviewed_head_at_close": head}, ensure_ascii=False))
