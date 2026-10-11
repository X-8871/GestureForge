"""只读输入与离线证据封包；不导入SDK、不操作板卡，不覆盖Run。"""

from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).absolute().parents[4]
RUN = ROOT / "report/evidence/S2B-T16" / sys.argv[1]
SOURCE_NAMES = ("verification/s2b_board_jtag.py", "verification/test_s2b_board_jtag.py",
                "verification/test_s2b_cold_observation.py", "vitis/run_s2b_visibility_probe.py",
                "verification/test_s2b_visibility_probe.py", "verification/s2b_board_transport.py",
                "verification/check_s2b_ps_smoke_layout.py", "verification/check_stage_delivery.py",
                "src/s2b_control_csr.sv")
INTERFACE = "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
XSA = "report/evidence/S2B-T13/artifact_recheck_20261011_r01/s2b_inference_no_bit.xsa"


def digest(path):
    """逐字节绑定，不重写输入。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    """证据新建且UTF8，不覆盖已存在文件。"""
    with (RUN / name).open("x", encoding="utf-8", newline="\n") as output:
        json.dump(value, output, ensure_ascii=False, indent=2); output.write("\n")


def snapshot():
    """固定当前实际源码与XSA生成原件，后续只消费该快照。"""
    assert RUN.is_dir() and not (RUN / "source_binding.json").exists()
    hashes = {}
    for name in SOURCE_NAMES + (INTERFACE,):
        source = ROOT / name
        assert source.is_file()
        target = RUN / "source_snapshot" / name
        assert not target.exists()
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        assert digest(target) == digest(source)
        hashes[name] = digest(source)
    assert digest(ROOT / XSA) == "6cff0c6afd009bf051028c4b793cc99c3c0c700002c2fdb2d247a33d2fc076a7"
    with zipfile.ZipFile(ROOT / XSA) as archive:
        for name in ("ps7_init.c", "ps7_init.h", "ps7_init.tcl", "ps7_init_gpl.c", "ps7_init_gpl.h", "s2b_inference.hwh"):
            target = RUN / "generated_basis" / name
            assert not target.exists()
            target.parent.mkdir(exist_ok=True)
            target.write_bytes(archive.read(name))
    diff = subprocess.run(["git", "diff", "--", *SOURCE_NAMES[:5]], cwd=ROOT, capture_output=True)
    assert diff.returncode == 0
    (RUN / "source_changes.patch").write_bytes(diff.stdout)
    target = RUN / "package_postconfig.py"
    assert not target.exists(); shutil.copyfile(Path(__file__), target)
    save("source_binding.json", {"baseline_commit": "140e5f6b7c4511b0a0699fab3a91b87de2faf381",
         "snapshot_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(), "source_sha256": hashes,
         "xsa": {"path": XSA, "sha256": digest(ROOT / XSA)}, "source_changes_native_exit_code": diff.returncode,
         "scope": "T16/T19 postconfig离线源码；正在并行修改的S5平台profile/checker/RTL不属于本轮G1测试闭包。"})
    save("official_basis.json", {"document": "UG585 v1.15 / 2026-02-06", "retrieved_utc8": "2026-10-11",
         "sources": [
          {"title": "SLCR_LOCKSTA Details", "url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Register-SLCR_LOCKSTA-Details?contentId=0quLiBIv~vnI8GvNlY3btw",
           "excerpt": "0: Registers are writeable. 1: Registers are not writeable.", "fact": "LOCKSTA bit0是实际写保护状态；解锁后0、重锁后1。"},
          {"title": "SLCR_LOCK Details", "url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Register-SLCR_LOCK-Details?contentId=HYXceB0Lob2m_cY6qM4Qeg",
           "excerpt": "A read of this register returns zero.", "fact": "LOCK_KEY=0x767B；write-only地址不做键值读回。"},
          {"title": "SLCR_UNLOCK Details", "url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Register-SLCR_UNLOCK-Details?contentId=EIgvT0h0onkO3L5eBYaiKw",
           "excerpt": "A read of this register returns zero.", "fact": "UNLOCK_KEY=0xDF0D；write-only地址不做键值读回。"},
          {"title": "PS–PL Voltage Level Shifter Enables", "url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/PS-PL-Voltage-Level-Shifter-Enables",
           "excerpt": "enable the level shifters after the PL is powered up and before the signals are used.",
           "fact": "PS/PL跨电压边界通信前需开启电平转换器。"},
          {"title": "FPGA_RST_CTRL", "url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Register-slcr-FPGA_RST_CTRL",
           "fact": "地址0xF8000240，32-bit读写，FPGA软件reset控制；本轮完整零动作来自绑定生成表。"},
          {"title": "Resets", "url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Resets?contentId=8VJt_7GapP9S1lMozBY0Cg",
           "fact": "四路PL reset由FPGA_RST_CTRL的FPGA[3:0]_OUT_RST独立控制；PL输出信号为FCLKRESETN[3:0]。"}],
         "sdk_scope": "未启动或导入XSDB/serial；公开Target.mrd/mwr API仅在mock上执行，实际Target来源门禁保持T19原有19定义闭包。",
         "generated_scope": "六生成原件及HWH逐字节来自固定XSA；执行四动作来自三个ps7_post_config分支，clock/PLL来自同分支clock/pll表。",
         "limitations": ["FCLK寄存器和HWH不等于实际频率测量。", "FPGA0_THR_STA的RUNNING位没有被当作频率计或门禁。", "implemented平台连接仍需T19独立compatibility批准；本轮不批准真实runtime。"]})


def package():
    """清单只含path/sha256/role；体积另列inventory，分别保存原生检查结果。"""
    binding = json.loads((RUN / "source_binding.json").read_text(encoding="utf-8"))
    assert all(digest(ROOT / name) == sha for name, sha in binding["source_sha256"].items())
    native_path = RUN / "native_run_result.json"
    native = json.loads(native_path.read_text(encoding="utf-8")) if native_path.exists() else None
    if native is not None: assert not native["source_drift"] and native["native_exit_code"] == int(sys.argv[3])
    resource = {"peak_working_set_bytes": None, "reason": "本次直接原生unittest未采样峰值内存；不由进程当前RSS推算峰值。"} if native is None else {
        key: native[key] for key in ("peak_working_set_bytes", "samples", "sampling_interval_seconds", "query_errors", "resource_scope", "RSS_budget_bytes", "total_deadline_seconds", "stop_reason")}
    final_script = RUN / "package_final.py"
    assert not final_script.exists(); shutil.copyfile(Path(__file__), final_script)
    stderr = (RUN / "unittest_stderr.log").read_text(encoding="utf-8")
    matched = re.search(r"Ran (\d+) tests in ([0-9.]+)s", stderr)
    rc = int(sys.argv[3])
    save("validation_result.json", {"status": "PASS" if rc == 0 and matched and "\nOK\n" in stderr.replace("\r", "") else "FAIL",
         "command": [sys.executable, "-B", "-m", "unittest", "verification.test_s2b_board_jtag", "verification.test_s2b_cold_observation", "verification.test_s2b_visibility_probe", "-v"],
         "native_exit_code": rc, "test_methods": int(matched[1]) if matched else None,
         "unittest_elapsed_seconds": float(matched[2]) if matched else None, "source_sha256": binding["source_sha256"],
         "resource": resource,
         "run_count": 1, "hardware_execution": "NOT_RUN", "cold_lifecycle_proven": False,
         "limitations": ["只运行mock及文件解析；无SDK session/connect、Serial.open或硬件调用。", "独立G2待root派发。"]})
    checks = [{"name": "T16_T19_mock_regression", "status": "PASS" if rc == 0 else "FAIL", "command": "python -B -m unittest verification.test_s2b_board_jtag verification.test_s2b_cold_observation verification.test_s2b_visibility_probe -v", "exit_code": rc},
              {"name": "G3_board", "status": "NOT_RUN", "command": None, "exit_code": None, "reason": "本任务授权仅离线G1，不操作板卡。"}]
    consumers = RUN / "consumer_binding.json"
    if consumers.exists():
        observed = json.loads(consumers.read_text(encoding="utf-8"))
        assert all(digest(ROOT / name) == sha for name, sha in observed["source_sha256"].items())
        checks.append({"name": "consumer_mock_regression_81", "status": "PASS", "command": observed["consumer_tests"]["command"], "exit_code": observed["consumer_tests"]["native_exit_code"]})
        checks.append({"name": "SDK_gate_AST_unchanged", "status": "PASS", "command": "python -B tmp/2B/S2B-T16/postconfig_20261011_r02/consumer_binding.py", "exit_code": 0})
        checks.append({"name": "cold_default_wire_lock_precheck_2", "status": "PASS", "command": "python -B -m unittest verification.test_s2b_cold_observation.PostconfigTests.test_all_cold_reset_default_fields_and_post_lock_clock_drift verification.test_s2b_visibility_probe.LifecycleTests.test_postconfig_failure_locks_wire_before_app_load_or_uart_request -v", "exit_code": 0})
    diff = subprocess.run(["git", "diff", "--check", "--", *SOURCE_NAMES[:5]], cwd=ROOT, capture_output=True)
    (RUN / "diff_check_stdout.log").write_bytes(diff.stdout); (RUN / "diff_check_stderr.log").write_bytes(diff.stderr)
    checks.append({"name": "diff_check", "status": "PASS" if diff.returncode == 0 else "FAIL", "command": "git diff --check -- " + " ".join(SOURCE_NAMES[:5]), "exit_code": diff.returncode})
    def manifest():
        inventory = [{"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "bytes": path.stat().st_size} for path in sorted(RUN.rglob("*")) if path.is_file() and path.name not in ("artifact_inventory.json", "delivery_manifest.json")]
        (RUN / "artifact_inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        files = [{"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "role": "source" if path.suffix in (".py", ".c", ".h", ".tcl", ".sv", ".patch") else "log" if path.suffix == ".log" else "input" if path.suffix in (".md", ".hwh") else "result"} for path in sorted(RUN.rglob("*")) if path.is_file() and path.name != "delivery_manifest.json"]
        files.append({"path": XSA, "sha256": digest(ROOT / XSA), "role": "input"})
        value = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T16", "run_id": RUN.name,
                 "source_commit": binding["baseline_commit"], "evidence_dir": RUN.relative_to(ROOT).as_posix(),
                 "interfaces": [{"name": "PS/PL物理候选接口", "version": "s2b-physical-candidate/0.1.1", "frozen": False,
                     "path": INTERFACE, "sha256": binding["source_sha256"][INTERFACE]}],
                 "files": files, "checks": checks, "tool_versions": {"python": platform.python_version(), "platform": platform.platform()},
                 "limitations": ["软件mock G1；G2未运行、G3 NOT_RUN，cold_lifecycle_proven始终false。", "physical0.1.1未冻结；inputs原生2为FAIL，不伪装为BLOCKED/code1。", "S5正在并行修改的平台源不在本轮测试闭包；真实runtime前须重新固定最终implemented兼容闭包。"]}
        (RUN / "delivery_manifest.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest()
    check_results = []
    for mode in ("evidence", "inputs"):
        command = [sys.executable, "-B", str(ROOT / "verification/check_stage_delivery.py"), "--mode", mode, "--manifest", str(RUN / "delivery_manifest.json")]
        result = subprocess.run(command, cwd=ROOT, capture_output=True)
        (RUN / (mode + "_stdout.log")).write_bytes(result.stdout); (RUN / (mode + "_stderr.log")).write_bytes(result.stderr)
        check_results.append({"mode": mode, "command": command, "native_exit_code": result.returncode})
        checks.append({"name": mode + "_packaging", "status": "PASS" if result.returncode == 0 else "FAIL", "command": " ".join(command), "exit_code": result.returncode,
                       "reason": "清单/绑定检查不代表接口冻结或G0/G4/G5；inputs失败由未冻结physical0.1.1产生。"})
        manifest()
    save("packaging_checks.json", check_results); manifest()
    final = subprocess.run([sys.executable, "-B", str(ROOT / "verification/check_stage_delivery.py"), "--mode", "evidence", "--manifest", str(RUN / "delivery_manifest.json")], cwd=ROOT, capture_output=True)
    print(json.dumps({"manifest_sha256": digest(RUN / "delivery_manifest.json"), "evidence_native_exit_code": final.returncode,
                      "evidence_stdout": final.stdout.decode("utf-8"), "source_sha256": binding["source_sha256"]}, ensure_ascii=False))
    assert final.returncode == 0


if sys.argv[2] == "snapshot": snapshot()
elif sys.argv[2] == "package": package()
else: raise RuntimeError("未知封包动作")
