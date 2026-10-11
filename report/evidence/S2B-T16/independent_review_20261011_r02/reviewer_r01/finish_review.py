"""补齐独立审查收据，不写被审源码，不操作硬件。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

RUN = Path(__file__).absolute().parent
ROOT = RUN.parents[3]
sys.path.insert(0, str(ROOT))
from verification import s2b_board_jtag as j

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

receipt = json.loads((RUN / "review_receipt.json").read_text(encoding="utf-8"))
basis_path = ROOT / "report/evidence/S2B-T16/jtag_offline_20261011_r02/native_sdk_basis.json"
basis = json.loads(basis_path.read_text(encoding="utf-8"))
receipt["sdk_original_checks"] = [{"name": name, "path": binding["path"], "sha256": sha(j.exact_path(binding["path"])),
                                    "matched": sha(j.exact_path(binding["path"])) == binding["sha256"]}
                                   for name, binding in basis["sdk"].items()]
receipt["sdk_inspected_ranges"] = {"target.py": [[120, 140], [211, 218], [2635, 2680], [2857, 2888], [5808, 5862], [5969, 5978]],
                                   "_tcf_reset.py": [[48, 70]], "_breakpoint.py": [[467, 500]]}
receipt["sdk_conclusion"] = "APU对象使用自身node.channel；memory路径保持node.id；bypass_cache_synq映射MODE_BYPASS_CACHE_SYNC；system与processor分别映射system与core；--stop传suspend=True；TCF XilinxReset实际reset请求。仅源码核查，无硬件调用。"
receipt["manifest_path"] = "report/evidence/S2B-T16/jtag_offline_20261011_r02/delivery_manifest.json"
receipt["manifest_sha256"] = sha(ROOT / receipt["manifest_path"])
command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", "inputs", "--manifest", receipt["manifest_path"]]
result = subprocess.run(command, cwd=ROOT, capture_output=True)
(RUN / "g1_inputs_stdout.log").write_bytes(result.stdout)
(RUN / "g1_inputs_stderr.log").write_bytes(result.stderr)
receipt["packaging_checks"] = {"evidence_native_exit_code": 0, "evidence_result": "CHECKS_OK", "inputs_native_exit_code": result.returncode,
                              "scope": "包装核查不代表G2/G3/G4/G5；inputs因候选未冻结受阻。"}
receipt["findings"] = [
    {"id": "R1-F1", "priority": "P1", "file": "verification/s2b_board_jtag.py", "lines": [369, 385],
     "problem": "cache_probe只检CPU1/BOOT_MODE和raw256B，未查epoch0/IDLE/PS拥有/ledger0；RUN epoch7及IDLE epoch7均执行DAP arena写并返回CROSS_MASTER_256_BYTES_MATCHED。",
     "impact": "可在PL拥有arena时写入input，破坏所有权与真实缓存验收；可将已经START后的运行冒充首次缓存探针。",
     "close_condition": "phase0之前、phase间DAP写之前与之后、phase1完成后验证稳定CSR的epoch0、安全IDLE、PS拥有、无head/terminal/pending/ledger；绑定并验证真实UART完整响应及请求身份，拒绝LOAD/START/ACK或漂移。补RUN/nonzero epoch/phase间变化反例。"},
    {"id": "R1-F2", "priority": "P1", "file": "verification/s2b_board_jtag.py", "lines": [427, 464],
     "problem": "dap_abort没有真实WAIT_DAP_ABORT入口证据门禁，wait_final返回只保存不解析；布尔True或epoch999/error0/DONE的UART元数据配上CSR即可返回ACTUAL_ERROR_SAFE_ABORTED_SAVED。",
     "impact": "缺失或身份错误的UART可被记为实际ABORT验收，不能证明同seq/frame的mode2中间与最终响应；违反不得接受伪造bool审批要求。",
     "close_condition": "接收绑定原header/payload字节且已验证CRC/op/sequence/frame/index/epoch的WAIT_DAP_ABORT/code10，再写同epochABORT；final必须来自同请求真实UART响应，验证ERROR_SAFE/code8/无head、无结果，与CSR的epoch/frame/status/error一致。任意bool、错epoch、错seq/frame及无READY必须拒绝。保留终态且不隐式ACK。"},
    {"id": "R1-F3", "priority": "P2", "file": "verification/s2b_board_jtag.py", "lines": [429, 436, 459, 463],
     "problem": "observe只使epoch高word自洽，最终STATUS/ERROR/owner/ledger是单次分散读取；没有双完整快照稳定比较。ERROR被首次读为8后立刻变9仍返回ACTUAL_ERROR_SAFE。",
     "impact": "可用混合时刻寄存器组成不存在或已经改变的安全终态，无法满足stableCSR ERROR_SAFE验收。",
     "close_condition": "最终完整状态/epoch/frame/error/head/owner/ledger快照至少两次一致，并与真实UART一致；读取间变化、ACK/epoch变化、非零ledger/pending均拒绝。保存每次原读回。"}
]
receipt["official_docs_check"] = {"urls": ["https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/System-Reset-Effects", "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Internal-Resets"],
                                  "result": "open成功，但工具返回主要为完整目录，未据此声称独立验证reset效果正文；冷生命周期仍NOT_PROVEN。"}
receipt["limitations"] = ["审查固定JTAG工具及44mock，不审核正在修改的T15候选为冻结版本。", "没有hardware/MCP/串口/hw_server/Vitis启动，G3/G4/G5未执行。", "system-stop原生API源已核对，物理POR与旧AXI结束仍不能由该API证明。", "峰值内存未测，磁盘产物约0.32MB。"]
receipt["source_after"] = {name: sha(ROOT / name) for name in receipt["source_before"]}
receipt["unchanged"] = receipt["source_before"] == receipt["source_after"]
receipt["files"] = [{"path": p.name, "sha256": sha(p)} for p in sorted(RUN.iterdir()) if p.is_file() and p.name != "review_receipt.json"]
(RUN / "review_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"status": receipt["status"], "source_unchanged": receipt["unchanged"], "sdk_all_match": all(r["matched"] for r in receipt["sdk_original_checks"]),
                  "inputs_native_exit_code": result.returncode, "receipt_sha256": sha(RUN / "review_receipt.json")}, ensure_ascii=False))
