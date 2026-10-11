"""冻结独立R2软件审查结果与精确归档清单；不改被审源码、G1或Git。"""
from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess

RUN = Path(__file__).absolute().parent
ROOT = RUN.parents[3]
BOOTSTRAP = RUN.parent / "independent_cold_observation_review_20261011_r02"


def sha(path):
    """绑定原始文件字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    """读取本轮UTF8产物。"""
    return json.loads((RUN / name).read_text(encoding="utf-8"))


def write(name, data):
    """以独占创建模式冻结结果。"""
    with (RUN / name).open("x", encoding="utf-8", newline="\n") as out:
        json.dump(data, out, ensure_ascii=False, indent=2)
        out.write("\n")


execution = read("execution_receipt.json")
outcomes = read("test_outcomes.json")
static = read("static_audit.json")
bindings = read("binding_audit.json")
assert execution["native_exit_code"] == 0 and execution["stop_reason"] is None
assert outcomes["tests_run"] == 152 and outcomes["failures"] == outcomes["errors"] == 0
assert not outcomes["remaining_hardware_modules"] and execution["resource"]["peak_working_set_bytes"] < 314572800
assert static["status"] == "PASS" and {name: sha(ROOT / name) for name in execution["source_sha256_before"]} == execution["source_sha256_before"]
assert {row["name"]: row["native_exit_code"] for row in execution["checks"]} == {
    "baseline_diff": 0, "diff_check": 0, "stage_evidence": 0, "stage_inputs": 2}
subtests = Counter(row["id"].split(".")[0] for row in outcomes["outcomes"] if row["kind"] == "subTest")
methods = Counter(row["id"].split(".")[0] for row in outcomes["outcomes"] if row["kind"] == "method")
receipt = {
  "schema_version": 1,
  "role": "INDEPENDENT_REVIEWER",
  "task_id": "S2B-T16-COLD-R2",
  "status": "PASS_SOFTWARE_G2_ONLY",
  "source_commit": execution["source_commit"],
  "observed_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(),
  "source_sha256": execution["source_sha256_before"],
  "g1_manifest": {"path": "report/evidence/S2B-T16/cold_observation_20261011_r02/delivery_manifest.json",
                   "sha256": bindings["manifest_sha256"]},
  "execution_receipt_sha256": sha(RUN / "execution_receipt.json"),
  "static_audit_sha256": sha(RUN / "static_audit.json"),
  "scope": "冻结五源的软件G2；完整metadata/EOS/DDRC、实际调用顺序、失败锁/清理、T19精确pin与既有SDK/native来源门禁、T20兼容回归和G1文件绑定。",
  "findings": [],
  "closed_findings": [{"prior_receipt_sha256": "e5ea9e4b9c86c0207a103ed0ac6d42270acf1e7351bf0a67fbd3f2705d910d77",
      "priority": "P1", "file": "verification/s2b_board_jtag.py", "location": "parse_config_status完整位覆盖require",
      "prior_issue": "EOS-only两态和缺bit3 metadata接受，原R1独立三反例FAIL。",
      "status": "CLOSED", "basis": "保留原失败断言重跑通过；额外对0与0xFFFFFFFF分别逐一删去0..31共64场景全部拒绝。R1生产源按冻结SHA精确恢复，R2只增加完整位覆盖断言。"}],
  "test_results": {"methods_by_group": outcomes["methods_by_group"], "tests_run": outcomes["tests_run"],
      "native_exit_code": execution["native_exit_code"], "failures": outcomes["failures"], "errors": outcomes["errors"],
      "method_result_groups": dict(methods), "subtest_result_groups": dict(subtests),
      "sdk_formatter_count": read("sdk_formatter_captures.json")["count"], "seed": read("sdk_formatter_captures.json")["random_seed"],
      "scope": "明确MOCK；AST只执行官方纯格式化分支，TCF输入由独立代码提供，无硬件SDK导入或连接。"},
  "verified_behaviors": [
      "CONFIG_STATUS十进制32位原字与每段metadata逐值一致；0..31恰好覆盖，无重叠；EOS精确名称唯一位4。",
      "EOS-only、缺bit3/31、所有单bit缺失、错值/重叠/重复/位号错误、替代EOS名、state文字、带符号/超大/非规范整数、非None/stderr拒绝。",
      "官方Target.fpga的原版AST格式化101输入均产出None与完整stdout，独立整除/余数核对原字、EOS和字段值通过。",
      "system-stop→实际EOS0→OCM ready/result2/return0→实际DAP DDRC低3位1→full-bit→实际EOS1→app，仅CPU0继续。",
      "DDRC0及2..7均锁止，不下载bit/app；post-bit失败不下载app；已确认的initialized/configured事实保持，原输出及异常保留。",
      "失败锁与自有CPU0/断点清理、CPU1Stopped、输入绑定和旧生命周期标志false未放宽。",
      "旧Git91bb源码、新源字节漂移及相同字节错误路径均拒绝；T19 SDK闭包、类/alias/code及两个native DLL物理来源门禁与基线原样。",
      "G1全部files的path/sha256/role及原件绑定通过；接口未冻结/实际runtime和cache受阻/BOARD未执行导致inputs原生2按FAIL保留。"
  ],
  "official_sources": static["official_sources"],
  "native_checks": execution["checks"],
  "resource": execution["resource"],
  "elapsed_seconds": execution["elapsed_seconds"],
  "runs": {"complete_suite_runs": 1, "reviewer_bootstrap_failed_runs": 1,
      "bootstrap_receipt": str((BOOTSTRAP / "bootstrap_failure.json").relative_to(ROOT)).replace("\\", "/"),
      "bootstrap_native_exit_code": 1, "bootstrap_git_native_exit_code": 128,
      "bootstrap_meaning": "r02仅Reviewer取历史源码阶段失败，未执行测试。保留原脚本/部分产物，r03修复新增文件处理后通过。"},
  "static_command": {"command": "python -B tmp/2B/S2B-T16/independent_cold_observation_review_20261011_r03/static_audit.py",
      "native_exit_code": 0, "provenance": "exec_command返回原生0；静态结果由static_audit.json冻结。"},
  "limitations": [
      "G3/实际runtime兼容/实际cache仍BLOCKED或NOT_RUN；没有创建实际Session、连接、串口或设备调用，hardware_calls=0。",
      "软件G2不批准全体系冷生命周期、旧AXI/cache/arena终结、visibility1、实际平台时序或板上验收。",
      "R1两个测试源未取得原字节副本，未声称历史测试全文diff可重建；当前五源已冻结并独立运行，R1生产源按已知SHA精确恢复。",
      "S4平台checker只按G1实际快照核验；不把其并行变动算作本任务修改。",
      "测试主子进程峰值工作集已测；短暂纯Python导入子进程峰值和全部工具调用量未独立测量。",
      "所有测试夹具只在本轮scratch；raw清单排除可重建mockSDK/ELF/UNIT兼容夹具，不能把其称为真实兼容批准。",
      "不改项目源码、STATE、Git、SDK或设备；由root归档并统一提交。"
  ],
  "finished_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
  "hardware_calls": 0,
  "stop": "全部测试/校验命令结束；本finalizer完成后Reviewer停止写入。"
}
write("review_receipt.json", receipt)
files = []
for folder in (BOOTSTRAP, RUN):
    assert folder.is_dir() and folder.parent == RUN.parent
    for path in sorted(folder.rglob("*")):
        if not path.is_file() or "scratch" in path.relative_to(folder).parts:
            continue
        assert path.name != "raw_delivery_manifest.json"
        role = "source" if path.suffix == ".py" else "log" if path.suffix in (".log", ".jsonl", ".txt", ".diff") else "result"
        files.append({"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(path), "role": role})
assert all(set(row) == {"path", "sha256", "role"} for row in files)
raw_manifest = {
  "schema_version": 1, "stage": "2B", "task_id": "S2B-T16", "run_id": RUN.name,
  "source_commit": execution["source_commit"], "evidence_dir": str(RUN.relative_to(ROOT)).replace("\\", "/"),
  "files": files,
  "interfaces": [{"name": "PS/PL候选CSR与缓存所有权接口", "version": "s2b-physical-candidate/0.1.1", "frozen": False,
                  "path": static["interface"]["path"], "sha256": static["interface"]["sha256"]}],
  "checks": [{"name": "R2独立软件G2", "status": "PASS", "command": "python -B " + str((RUN / "run_review.py").relative_to(ROOT)).replace("\\", "/"), "exit_code": 0},
             {"name": "Reviewer r02预备历史源码提取", "status": "FAIL", "command": "python -B " + str((BOOTSTRAP / "run_review.py").relative_to(ROOT)).replace("\\", "/"), "exit_code": 1, "reason": "历史失败原件保留，新r03恢复执行。"},
             {"name": "G1 stage inputs", "status": "FAIL", "command": subprocess.list2cmdline(execution["checks"][-1]["command_argv"]), "exit_code": 2},
             {"name": "实际runtime与cache", "status": "BLOCKED", "command": None, "exit_code": None, "reason": "未取得适用实际平台与实板批准事实。"},
             {"name": "BOARD/G3", "status": "NOT_RUN", "command": None, "exit_code": None, "reason": "hardware_calls=0。"}],
  "tool_versions": execution["tool_versions"],
  "limitations": ["raw manifest是root精确归档输入，仅包含本Reviewer r02预备失败及r03实际审查文件；不声称完整tmp目录包装通过。",
      "精确归档集合为files中各路径，再加本raw_delivery_manifest.json自身；全部scratch排除且保留原地。",
      "旧独立R1的46项由root按其原raw_manifest另行归档；本清单不重复纳入它们。",
      "PASS_SOFTWARE_G2_ONLY不等于inputs/G3/实际cache/统一冷生命周期通过。"]
}
write("raw_delivery_manifest.json", raw_manifest)
print(json.dumps({"status": receipt["status"], "review_receipt_sha256": sha(RUN / "review_receipt.json"),
      "raw_delivery_manifest_sha256": sha(RUN / "raw_delivery_manifest.json"),
      "raw_files": len(files), "archive_files_including_manifest": len(files) + 1,
      "total_bytes_including_manifest": sum((ROOT / row["path"]).stat().st_size for row in files) + (RUN / "raw_delivery_manifest.json").stat().st_size}, ensure_ascii=False))
