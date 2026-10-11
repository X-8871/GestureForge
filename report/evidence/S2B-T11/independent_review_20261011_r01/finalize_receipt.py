"""冻结独立审阅版本、原始验证证据与发现关闭状态。"""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
FIXED = {
    "src/s2b_control_csr.sv": "f884619e665502decbbb9186b4b79fa3f5d57c7ea0868a52d4af1f553a9a9629",
    "src/s2b_hp0_word_adapter.sv": "344f5553da157434039ec531ccef83cd74dba9c67533a0b88642438e5b5a8f62",
    "sim/tb_s2b_control_csr.sv": "182f4b4afe873d8aba870950c12eb874fcac4c2bc27f70ed18a9620df9c78fe3",
    "sim/tb_s2b_hp0_word_adapter.sv": "4ebf8d9402765b82e9d5501e75dbca92f5bb864297309931a069fe49c4ca7591",
    "verification/test_s2b_control_csr_rtl.py": "d2cdde7334fa87aadedd1932cc9337f5d871c02ea9c295f05d1bd7adb18ba87f",
}

def sha(path):
    """核对文件原始字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
assert head == "09d2115dfe1fe5f1f1499c1b8082348bbdfa2ce3"
for path, expected in FIXED.items():
    assert sha(ROOT / path) == expected, path
reports = [json.loads((BASE / p).read_text(encoding="utf-8")) for p in
    ("result.json", "supplemental_result_r02.json", "adapter_result.json")]
assert all(report["status"].startswith("PASS") for report in reports)
assert all(run["exit_code"] == 0 for report in reports for run in report["runs"])
package_checks = []
for run_id in ("control_r10_20261011", "vivado_lint_20261011_r04"):
    path = ROOT / "report/evidence/S2B-T11" / run_id / "delivery_manifest.json"
    cmd = ["python", "-B", "verification/check_stage_delivery.py", "--mode", "evidence", "--manifest", str(path)]
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True)
    assert result.returncode == 0, result.stdout
    log = BASE / (run_id + "_package_check.log")
    log.write_bytes(result.stdout + result.stderr)
    package_checks.append({"command": cmd, "exit_code": result.returncode, "manifest_sha256": sha(path), "log_sha256": sha(log)})
lint = ROOT / "report/evidence/S2B-T11/vivado_lint_20261011_r04"
corrected = json.loads((lint / "root_result.json").read_text(encoding="utf-8"))
assert "1432.691" in corrected["reason"] and "1442.207" in corrected["reason"]
assert sha(lint / "vivado_native.log") == "7cf37afe1debf39709e630e5db996bc8986144462326978f2336cf6c8825b253"
assert (lint / "control_linter.csv").stat().st_size == (lint / "adapter_linter.csv").stat().st_size == 0
assert (lint / "root_result.json.before_peak_correction.json").is_file()
assert (lint / "delivery_manifest.json.before_peak_correction.json").is_file()
receipt = {
    "review_status": "PASS", "gate": "S2B-T11 G2候选实现", "source_commit": head,
    "interface_version": "s2b-physical-candidate/0.1.1",
    "fixed_sources": [{"path": path, "sha256": value} for path, value in FIXED.items()],
    "spec_sha256": sha(ROOT / "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"),
    "reviewed_scope": ["完整寄存器方向/编码/地址译码与独立AW/W/R/B单槽及背压", "START配置快照/ARMING边界/公共四相位CSR监视/真实STOP S+2", "首观察pending、同沿优先、取消沿不交付、协议风险保持", "完整恢复期限、未闭合隔离及合法晚排空ERROR_SAFE", "epoch单调/耗尽与匹配ACK/晚到故障", "adapter新progress next及地址关联元数据/无组合环", "五待审文件、G1原始日志/快照哈希和最终Vivado lint执行窗口"],
    "independent_control": reports[0], "independent_supplemental": reports[1], "independent_adapter": reports[2],
    "package_checks": package_checks,
    "findings": [{"severity": "非阻断", "status": "CLOSED", "issue": "r04会话峰值原说明仅写controller1432.691MB，遗漏adapter末段1442.207MB", "resolution": "总控校正元数据，保留旧说明原字节，原始RTL与native日志未变，独立包装校验原生0"}],
    "review_failures_preserved": ["initial_path_failure.json：独立driver父目录索引错误，未执行编译，已修正", "supplemental_result.json与supplemental_evidence：独立夹具删去原测试后残留未使用变量，严格Wall拒绝；修正夹具并全新r02重建，未改被审RTL"],
    "limitations": ["只证明候选G2，不冻结物理接口，不代表G3/G4/G5或模型板上验收", "真实runtime_shell/CSR/memory master与adapter已集成，未运行整个network backend/GP0转换器或完整平台", "visibility_confirmed是显式测试输入，实际HP/DDR/cache可见性由后续集成和实物证明", "已审源码无修改、未提交/切分支/使用MCP/操作硬件；所有审查写入仅隔离tmp", "单job/单线程；峰值OS内存和全部工具调用量未测，Verilator自身分配量不可称OS峰值"],
}
(BASE / "review_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": receipt["review_status"], "head": head, "sources": len(FIXED), "receipt_sha256": sha(BASE / "review_receipt.json"), "package_checks": package_checks}, ensure_ascii=False))
