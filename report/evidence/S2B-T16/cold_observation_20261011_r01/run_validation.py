"""离线观测回归证据采集，严格限制本次子进程内存；不连接硬件。"""

import ctypes
from ctypes import wintypes
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

ROOT = Path(__file__).absolute().parents[4]
RUN = Path(__file__).absolute().parent
SOURCES = ("verification/s2b_board_jtag.py", "verification/test_s2b_board_jtag.py",
           "verification/test_s2b_cold_observation.py", "verification/s2b_board_transport.py",
           "verification/check_s2b_ps_smoke_layout.py", "verification/check_stage_delivery.py")
INTERFACE = "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
PS7 = "report/evidence/S2B-T15/full_build_20261011_r01/ps7_init.c"
SDK = Path("D:/Xilinx/2026.1/Vitis/cli/xsdb/target.py")


def digest(path):
    """计算实际原字节哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    """新建UTF-8证据，不覆盖既有运行。"""
    with (RUN / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write("\n")


class MemoryCounters(ctypes.Structure):
    """Windows原生进程工作集统计。"""
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
        (name, ctypes.c_size_t) for name in ("PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
        "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]


hashes = {name: digest(ROOT / name) for name in SOURCES + (INTERFACE, PS7)}
sdk_hash = digest(SDK)
sdk_lines = SDK.read_text(encoding="utf-8").splitlines()
with (RUN / "sdk_config_status_excerpt.txt").open("x", encoding="utf-8", newline="\n") as stream:
    stream.write("\n".join(f"{index + 1}: {sdk_lines[index]}" for index in range(4596, 4671)) + "\n")
write("observation_basis.json", {
    "baseline_commit": "6d3fd8567b579a51d4042667d47af7d94f2f5a97",
    "prior_tool_sha256": "91bbf5bc8ac5ef9bee37ce6491627a6ac8f38a53b7bba113d1b83447b2ecddf0",
    "sdk_path": str(SDK), "sdk_sha256": sdk_hash, "sdk_lines": [4597, 4671],
    "sdk_interface": "Target.fpga('--config_status')返回None；stdout原字及metadata字段，无底层TCF替代。",
    "official_sources": [
        {"title": "UG470 v1.17，表5-29，印刷页107 / PDF页索引106",
         "url": "https://docs.amd.com/api/khub/documents/FOs3lXmlcWxBhTIFxVKyGA/content",
         "fact": "EOS位4：0代表启动序列未结束，1代表启动序列结束。"},
        {"title": "UG585 v1.15 Register (ddrc) mode_sts_reg",
         "url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Register-ddrc-mode_sts_reg",
         "fact": "状态地址0xF8006054。"},
        {"title": "UG585 v1.15 Register mode_sts_reg Details",
         "url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Register-mode_sts_reg-Details",
         "fact": "operating_mode[2:0]仅1为normal；0是初始化，2是powerdown，3是self-refresh，4以上是deep powerdown。"}],
    "ps7_init_path": PS7, "ps7_init_sha256": hashes[PS7], "ps7_init_lines": [1518, 1524, 7201, 7214],
    "ps7_init_observation": "现有生成代码注释指定mode1，EMIT_MASKPOLL mask7实际仅等任何掩码位非零；新增DAP校验拒绝2..7。",
    "sequence": ["system-reset-stop", "actual_config_status_EOS0", "OCM_init_ready_result2_return0",
                 "DAP_DDRC_mode1", "full_bit", "actual_config_status_EOS1", "mark_configured", "DDR_app"],
    "lifecycle": "冷生命周期判断继续交由总控和独立Reviewer，工具始终保留cold_lifecycle_proven=false。"})

command = [sys.executable, "-B", "-m", "unittest", "verification.test_s2b_board_jtag",
           "verification.test_s2b_cold_observation", "-v"]
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
started = time.monotonic()
api = ctypes.WinDLL("psapi", use_last_error=True).GetProcessMemoryInfo
api.argtypes = (wintypes.HANDLE, ctypes.POINTER(MemoryCounters), wintypes.DWORD)
api.restype = wintypes.BOOL
peak, samples, memory_errors, stop_reason = 0, 0, 0, None
with (RUN / "unittest_stdout.log").open("xb") as stdout, (RUN / "unittest_stderr.log").open("xb") as stderr:
    child = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stdout, stderr=stderr)
    while child.poll() is None:
        counters = MemoryCounters(); counters.cb = ctypes.sizeof(counters)
        if api(wintypes.HANDLE(int(child._handle)), ctypes.byref(counters), counters.cb):
            samples += 1; peak = max(peak, counters.PeakWorkingSetSize)
        else:
            memory_errors += 1
        if peak >= 300 * 1024 * 1024 or time.monotonic() - started > 180:
            stop_reason = "RSS预算或180秒期限超限"
            child.kill(); break
        time.sleep(0.05)
    native_rc = child.wait()
elapsed = time.monotonic() - started
stderr_text = (RUN / "unittest_stderr.log").read_text(encoding="utf-8")
matched = re.search(r"Ran (\d+) tests", stderr_text)
count = int(matched.group(1)) if matched else None
for name, expected in hashes.items():
    if digest(ROOT / name) != expected:
        raise RuntimeError("验证期间输入漂移：" + name)
if digest(SDK) != sdk_hash:
    raise RuntimeError("验证期间SDK源码漂移")
diff = subprocess.run(["git", "diff", "--check", "--", *SOURCES], cwd=ROOT, capture_output=True)
with (RUN / "diff_check_stdout.log").open("xb") as stream: stream.write(diff.stdout)
with (RUN / "diff_check_stderr.log").open("xb") as stream: stream.write(diff.stderr)
write("validation_result.json", {"status": "PASS" if native_rc == diff.returncode == 0 and count == 66 else "FAIL",
      "command_argv": command, "native_exit_code": native_rc, "tests": count, "elapsed_seconds": elapsed,
      "finished_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
      "source_sha256": hashes, "sdk_sha256": sdk_hash,
      "resource": {"peak_working_set_bytes": peak, "samples": samples, "memory_query_errors": memory_errors,
                   "sampling_interval_seconds": 0.05, "RSS_budget_bytes": 300 * 1024 * 1024,
                   "fresh_import_subprocess_peak": "未单独测量；只有一次短暂纯Python导入子进程。"},
      "stop_reason": stop_reason, "hardware_execution": "NOT_RUN", "hardware_calls": 0,
      "run_count": 2, "first_run": {"native_exit_code": 0, "tests": 66, "elapsed_seconds": 69.611,
              "logs": "初次完整stdout/stderr仅在会话工具输出；本次重复专为永久原始日志与资源采集。"},
      "diff_check_native_exit_code": diff.returncode, "limitations": ["仅离线mock；无G3事实。", "独立审查待总控派发。"]})
files = [{"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path),
          "role": "source" if path.suffix == ".py" else "log" if path.suffix in (".log", ".txt") else "result"}
         for path in sorted(RUN.iterdir()) if path.is_file()]
files += [{"path": name, "sha256": sha, "role": "source" if name in SOURCES else "input"}
          for name, sha in hashes.items()]
write("delivery_manifest.json", {"schema_version": 1, "stage": "2B", "task_id": "S2B-T16", "run_id": RUN.name,
      "source_commit": "6d3fd8567b579a51d4042667d47af7d94f2f5a97", "evidence_dir": RUN.relative_to(ROOT).as_posix(),
      "files": files, "interfaces": [{"name": "PS/PL候选CSR与缓存所有权接口", "version": "s2b-physical-candidate/0.1.1",
      "frozen": False, "path": INTERFACE, "sha256": hashes[INTERFACE]}],
      "tool_versions": {"Python": platform.python_version(), "XSDB-source": "Vitis2026.1只读源码；未导入SDK"},
      "checks": [{"name": "原56mock及新增10独立观测测试", "status": "PASS" if native_rc == 0 and count == 66 else "FAIL",
                   "command": "python -B -m unittest verification.test_s2b_board_jtag verification.test_s2b_cold_observation -v",
                   "exit_code": native_rc},
                  {"name": "本轮差异空白检查", "status": "PASS" if diff.returncode == 0 else "FAIL",
                   "command": "git diff --check -- " + " ".join(SOURCES), "exit_code": diff.returncode},
                  {"name": "实板观测", "status": "NOT_RUN", "command": None, "exit_code": None,
                   "reason": "Developer只允许离线mock，未连接设备。"},
                  {"name": "独立审查", "status": "NOT_RUN", "command": None, "exit_code": None,
                   "reason": "Developer停止写入版待总控固定并独立审查。"}],
      "limitations": ["当前交付仅离线G1，不代表G2/G3/G4/G5。", "候选未冻结和实板NOT_RUN令inputs仍阻断。",
                       "未提交，由总控统一提交；cold_lifecycle_proven始终false。"]})
print(json.dumps({"tests": count, "native_exit_code": native_rc, "elapsed_seconds": elapsed,
                  "peak_working_set_bytes": peak, "source_sha256": hashes,
                  "manifest_sha256": digest(RUN / "delivery_manifest.json")}, ensure_ascii=False))
raise SystemExit(native_rc or diff.returncode or (0 if count == 66 else 1))
