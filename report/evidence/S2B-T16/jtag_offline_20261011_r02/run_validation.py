"""只执行离线mock回归并保存原生返回；不导入XSDB或连接硬件。"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
import json
import os
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).absolute().parents[4]
RUN = Path(__file__).absolute().parent


def write(name, value):
    """新建UTF-8原件，不覆盖已有运行。"""
    with (RUN / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write("\n")


sources = ("verification/s2b_board_jtag.py", "verification/test_s2b_board_jtag.py", "verification/check_s2b_ps_smoke_layout.py",
           "verification/check_stage_delivery.py", "src/s2b_control_csr.sv", "src/s2b_hp0_word_adapter.sv",
           "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md")
source_hash = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources}
started = time.monotonic()
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
command = [sys.executable, "-B", "-m", "unittest", "verification.test_s2b_board_jtag", "-v"]
result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=180)
for name, raw in (("unittest_stdout.log", result.stdout), ("unittest_stderr.log", result.stderr)):
    with (RUN / name).open("xb") as stream:
        stream.write(raw)
sdk = Path(r"D:\Xilinx\2026.1\Vitis\cli\xsdb")
basis = {name: {"path": str(sdk / name), "sha256": hashlib.sha256((sdk / name).read_bytes()).hexdigest()}
         for name in ("target.py", "session.py", "_tcf_reset.py", "_tcf_node_memory.py", "_breakpoint.py")}
write("native_sdk_basis.json", {"sdk": basis, "version": "Vitis 2026.1 Python XSDB", "hardware": "NOT_RUN",
      "observed_source_rules": ["target.mrd选中APU node.id后__get_memory_tgt，不选CPU。",
       "target.mwr的--bypass_cache_synq设置MODE_BYPASS_CACHE_SYNC。",
       "system重置保留rst_type=system，processor/cores映射core/cpu；XilinxReset能力校验后调用TCF reset。",
       "system默认resume；必须显式--stop。ps分支要求MicroBlaze PMU，por要求线缆POR引脚能力。",
       "fpga(file=...)保留默认兼容性检查，未用partial/no_revision/skip兼容检查。",
       "SDK没有明确SLVERR错误枚举；通用DAP异常不能当作已证明SLVERR。"],
      "official_non_por_basis_from_root": [{"url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/System-Reset-Effects", "scope": "总控已浏览non-POR系统复位效果，本子任务未独立浏览。"},
        {"url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Internal-Resets", "scope": "总控已浏览SOFT_RST与JTAG/debug非POR来源，本子任务仅核对SDKTCF请求。"}]})
write("validation_result.json", {"status": "PASS_OFFLINE_MOCK" if result.returncode == 0 else "FAIL_OFFLINE_MOCK",
      "hardware_execution": "NOT_RUN", "source_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
      "source_sha256": source_hash, "command": command, "native_exit_code": result.returncode,
      "elapsed_seconds": time.monotonic() - started, "time_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
      "python_version": platform.python_version(), "test_count": result.stderr.decode("utf-8").count(" ... "),
      "peak_memory": "未测", "hardware_api_call_count": 0, "repeated_runs_in_conversation": 3,
      "earlier_runs": [{"native_exit_code": 1, "tests": 33, "errors": 15, "elapsed_seconds": 11.883,
          "failure": "ModuleNotFoundError: No module named 'check_stage_delivery'；既有ELF解析器同目录绝对导入与python -m入口冲突。",
          "full_native_log": "初次未落本目录，完整工具输出在当前会话；本文件仅保存已观测摘要，不冒充完整原件。"},
         {"native_exit_code": 0, "tests": 33, "elapsed_seconds": 34.695, "scope": "修复导入后实际通过；后续ABORT及reset门禁需本轮新测试。"}],
      "limitations": ["mock SDK只证明工具逻辑；实板、冷生命周期、CSR SLVERR、cache/整网均NOT_RUN。", "未创建hw_server或XSDB会话。"]})
raise SystemExit(result.returncode)
