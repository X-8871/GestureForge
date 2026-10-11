"""运行R1修复后的真实字节流mock回归，保存完整原件及机器清单；不操作硬件。"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time

ROOT = Path(__file__).absolute().parents[4]
RUN = Path(__file__).absolute().parent


def digest(path):
    """对实际文件原字节计算SHA256。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    """证据只新建，不覆盖历史运行。"""
    with (RUN / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write("\n")


sources = ("verification/s2b_board_jtag.py", "verification/test_s2b_board_jtag.py", "verification/s2b_board_transport.py",
           "verification/check_s2b_ps_smoke_layout.py", "verification/check_stage_delivery.py", "src/s2b_control_csr.sv",
           "src/s2b_hp0_word_adapter.sv", "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md")
source_hash = {name: digest(ROOT / name) for name in sources}
started = time.monotonic()
command = [sys.executable, "-B", "-m", "unittest", "verification.test_s2b_board_jtag", "-v"]
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=180)
elapsed = time.monotonic() - started
for name, raw in (("unittest_stdout.log", result.stdout), ("unittest_stderr.log", result.stderr)):
    with (RUN / name).open("xb") as stream:
        stream.write(raw)
count = int(re.search(r"Ran (\d+) tests", result.stderr.decode("utf-8")).group(1))
commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
for name, expected in source_hash.items():
    if digest(ROOT / name) != expected:
        raise RuntimeError("回归期间源文件漂移：" + name)
review = ROOT / "tmp/2B/S2B-T16/independent_review_20261011_r01"
prior = {str(path.relative_to(ROOT).as_posix()): digest(path) for path in sorted(review.iterdir()) if path.is_file()}
write("validation_result.json", {"status": "PASS_OFFLINE_MOCK" if result.returncode == 0 else "FAIL_OFFLINE_MOCK",
      "native_exit_code": result.returncode, "command": command, "test_count": count, "elapsed_seconds": elapsed,
      "source_commit": commit, "source_sha256": source_hash, "python_version": platform.python_version(),
      "time_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(), "hardware_execution": "NOT_RUN",
      "hardware_api_call_count": 0, "peak_memory": "未测；仅单进程轻量unittest，未调用Vivado/XSDB",
      "current_fix_mock_runs": 3,
      "earlier_fix_runs": [{"tests": 56, "native_exit_code": 1, "errors": 53, "elapsed_seconds": 19.829,
          "reason": "新增测试辅助函数时误缩进FakeSession.targets；已恢复类方法。",
          "full_native_log": "完整工具输出仅在会话中，本项为真实摘要，不声称已保存原件。"},
          {"tests": 56, "native_exit_code": 0, "elapsed_seconds": 57.066,
           "log_path": "tmp/2B/S2B-T16/developer_fix_20261011_r02/unittest.log"}],
      "prior_review_failure_originals_sha256": prior,
      "closed_boundaries": ["cache RUN/epoch7及IDLE/epoch7在phase/DAP写前拒绝。",
          "每phase和DAP写前后核对两份完整CSR一致的冷epoch0/IDLE/ownerPS/head0/ledger0。",
          "ABORT必须实际消费T15 code10 WAIT原帧；caller bool/dict/callback不构成UART证据。",
          "UART header/payload CRC及op/seq/frame/epoch/error/status经T15原解析器严格绑定。",
          "ABORT final由真实UART与两份完整一致CSR确认ERROR_SAFE/code8；8→9变化拒绝，无隐式ACK。"],
      "limitations": ["仅mock通过；部署、cache实板、真实SLVERR及整网均NOT_RUN。", "独立复审尚未执行。",
          "T15与物理候选的冻结状态由root独立决定；本工具不声明整体成功。"]})
interface = "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
files = [{"path": p.relative_to(ROOT).as_posix(), "sha256": digest(p),
          "role": "source" if p.suffix == ".py" else ("log" if p.suffix == ".log" else "result")}
         for p in sorted(RUN.iterdir()) if p.is_file()]
files += [{"path": name, "sha256": value, "role": "source" if name.startswith("verification/") else "input"}
          for name, value in source_hash.items()]
write("delivery_manifest.json", {"schema_version": 1, "stage": "2B", "task_id": "S2B-T16", "run_id": RUN.name,
      "source_commit": commit, "evidence_dir": RUN.relative_to(ROOT).as_posix(), "files": files,
      "interfaces": [{"name": "PS/PL候选CSR与缓存所有权接口", "version": "s2b-physical-candidate/0.1.1",
                      "frozen": False, "path": interface, "sha256": source_hash[interface]}],
      "tool_versions": {"Python": platform.python_version(), "XSDB-source": "Vitis 2026.1 Python SDK只读依据"},
      "checks": [{"name": f"R1修复离线mock回归{count}项", "status": "PASS" if result.returncode == 0 else "FAIL",
                  "command": "python -B -m unittest verification.test_s2b_board_jtag -v", "exit_code": result.returncode},
                 {"name": "实板验证", "status": "NOT_RUN", "command": None, "exit_code": None,
                  "reason": "仅root固定G2后允许操作硬件。"},
                 {"name": "独立复审", "status": "NOT_RUN", "command": None, "exit_code": None,
                  "reason": "Developer交付停止写入版，等待root独立Reviewer。"}],
      "limitations": ["G1离线工具交付不代表G2/G3/G4/G5；未提交，由总控统一提交。",
                      "旧r01/r02失败及独立R1失败原件保留；候选未冻结，inputs检查预期仍阻断。"]})
print(json.dumps({"native_exit_code": result.returncode, "tests": count, "elapsed_seconds": elapsed,
                  "source_sha256": source_hash, "manifest_sha256": digest(RUN / "delivery_manifest.json")}, ensure_ascii=False))
raise SystemExit(result.returncode)
