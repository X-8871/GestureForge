"""只读识别阶段三/2B现场，必要时停稳阶段三VDMA，再恢复2B易失部署。"""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(r"D:\FPGA_Competition\w2b")
STAGE3_ROOT = Path(r"D:\codex-worktrees\dbdf")
RUN_NAME = "stage3_to_2b_restore_20261022_r01"
OUT = ROOT / "report/evidence/S2B-T18" / RUN_NAME
BASE_CONFIG = ROOT / "report/evidence/S2B-T18/formal_online_20261018_r01/model_config_csr_20261019_r10.json"
RUNTIME_CONFIG = ROOT / "report/evidence/S2B-T18/formal_online_20261018_r01/rebuilt_app_config_20261021_r02.json"
SERVER_IDENTITY = ROOT / "tmp/2B/hw_server_20261022.json"
RUNNER = ROOT / "vitis/run_s2b_model_acceptance.py"
STAGE3_STATE = STAGE3_ROOT / ".codex/STATE.md"
FREEZE_DIR = STAGE3_ROOT / "report/evidence/S3-T05/t05_freeze_20261021_r01"
FREEZE_README = FREEZE_DIR / "README.md"
FREEZE_HASHES = FREEZE_DIR / "hashes.txt"
STAGE3_APP = STAGE3_ROOT / "tmp/s3r06/t04_j11cmos2_elf_v10/elf_build/app/an5642_j11cmos2_v10_read.elf"
STAGE3_XSA = STAGE3_ROOT / "tmp/s3r06/t04_gray_20261021_r01/design_1_wrapper.xsa"
STAGE3_BIT = STAGE3_ROOT / "tmp/s3r06/t04_gray_20261021_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit"
STAGE3_README_SHA256 = "a3b96f95caa8a47158a7923c791e65d1963d5a71e0a7c71dffe4bbd85e67496c"
STAGE3_APP_SHA256 = "1457cda4867649dce8b54b2ebe9c7bafc0a2a1d4d1deba112adc6f6492306073"
STAGE3_XSA_SHA256 = "bb71c3f6e15b6f22fd0709373c3910f3dc4682214fb0cd6a9f69330a13eaaa12"
STAGE3_BIT_SHA256 = "2f72aaa42936225eb7215bd8f138f68e52c27c3ab31ab236c8a3c15f7669af4f"

sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("restore_20261022_runtime", RUNNER)
r = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r
spec.loader.exec_module(r)


def sha(raw: bytes) -> str:
    """计算原始字节SHA-256。"""
    return hashlib.sha256(raw).hexdigest()


def save_json(path: Path, value: object) -> None:
    """以独占创建方式保存UTF-8证据。"""
    raw = (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2, default=repr) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        import os
        os.fsync(stream.fileno())


def verify_frozen_inputs(apis) -> dict:
    """校验阶段三只读状态及冻结README、bit、XSA和v10_read ELF身份。"""
    state = r.exact_path(STAGE3_STATE, "file")
    state_raw = state.read_bytes()
    state_text = state_raw.decode("utf-8")
    task_rows = [line for line in state_text.splitlines() if line.startswith("任务=`S3-T05")]
    r.require(len(task_rows) == 1 and "状态/下一接手方=`DONE" in task_rows[0],
              "阶段三STATE不是只读DONE状态，停止恢复")
    freeze_readme = r.exact_path(FREEZE_README, "file")
    freeze_hashes = r.exact_path(FREEZE_HASHES, "file")
    readme_raw = freeze_readme.read_bytes()
    hashes_text = freeze_hashes.read_text(encoding="utf-8")
    readme_binding = f"{STAGE3_README_SHA256} *report/evidence/S3-T05/t05_freeze_20261021_r01/README.md"
    r.require(sha(readme_raw) == STAGE3_README_SHA256 and readme_binding in hashes_text.splitlines(),
              "阶段三冻结README原字节与hashes.txt绑定不符")
    readme_text = readme_raw.decode("utf-8")
    for required in (STAGE3_BIT_SHA256, STAGE3_XSA_SHA256, STAGE3_APP_SHA256,
                     "an5642_j11cmos2_v10_read.elf"):
        r.require(required in readme_text, "冻结README缺少固定产物身份：" + required)
    assets = {}
    for role, path, expected in (("v10_read_elf", STAGE3_APP, STAGE3_APP_SHA256),
                                 ("gray_xsa", STAGE3_XSA, STAGE3_XSA_SHA256),
                                 ("gray_bit", STAGE3_BIT, STAGE3_BIT_SHA256)):
        actual = r.exact_path(path, "file")
        raw = actual.read_bytes()
        r.require(sha(raw) == expected, role + "实际文件SHA与冻结值不符：" + str(actual))
        assets[role] = {"path": str(actual), "sha256": expected, "bytes": len(raw)}
    stage3_elf = apis.elf_parser.parse_elf(STAGE3_APP.read_bytes())
    return {"state": {"path": str(state), "sha256": sha(state_raw), "status_line": task_rows[0]},
            "freeze_readme": {"path": str(freeze_readme), "sha256": STAGE3_README_SHA256},
            "freeze_hashes": {"path": str(freeze_hashes), "sha256": sha(freeze_hashes.read_bytes())},
            "assets": assets, "stage3_elf": stage3_elf}


def _validate_live_pc(controller, apis, elf: dict, raw: bytes, label: str) -> dict:
    """CPU停止后按CPSR读取PC附近16字节并和指定ELF逐字节核对。"""
    pc = controller.pc()
    cpsr = controller.call(label + ".rrd.cpsr", controller.targets["cpu0"].rrd,
                           "--nvlist", reg="cpsr")["cpsr"]
    aligned = pc & ~3
    observed = struct.pack("<5I", *controller.words(aligned, 5))[pc - aligned:pc - aligned + 16]
    return r._validate_app_pc_instructions(elf, raw, pc, cpsr, observed)


def _verify_vdma_xsa(xsa: Path) -> list[dict]:
    """确认冻结XSA只含预期的两个64 KiB寄存器窗口。"""
    with zipfile.ZipFile(xsa) as archive:
        members = [name for name in archive.namelist() if name.endswith(".hwh")]
        r.require(len(members) == 1, "冻结灰度XSA中的HWH数量不唯一")
        tree = ET.fromstring(archive.read(members[0]))
    expected = ((0x43000000, 0x4300FFFF), (0x43010000, 0x4301FFFF))
    rows = [row.attrib for row in tree.findall(".//MEMRANGE")
            if int(row.get("BASEVALUE", "-1"), 0) in (0x43000000, 0x43010000)]
    r.require(len(rows) == 2 and all(any(int(row["BASEVALUE"], 0) == base and
              int(row["HIGHVALUE"], 0) == high and row.get("MEMTYPE") == "REGISTER"
              for row in rows) for base, high in expected), "冻结灰度XSA的VDMA物理窗口不符")
    return rows


def _runtime_config() -> dict:
    """沿用R10原R04部署绑定，仅换用官方SDK完整运行配置与当前服务身份。"""
    config = r.strict_json(r.exact_path(BASE_CONFIG, "file").read_bytes())
    runtime_template = r.strict_json(r.exact_path(RUNTIME_CONFIG, "file").read_bytes())
    config["runtime"] = runtime_template["runtime"]
    config["hw_server"] = r.strict_json(r.exact_path(SERVER_IDENTITY, "file").read_bytes())
    config["source_commit"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
    runner = r.exact_path(RUNNER, "file")
    config["bindings"]["runner_source"] = {"path": str(runner), "sha256": sha(runner.read_bytes())}
    config["run_id"] = RUN_NAME
    return config


class PhysicalController(r.load_apis("csr").jtag.JtagController):
    """用官方AP0接口读取和控制VDMA窗口，其余部署仍由原控制器负责。"""
    def words(self, address, count, address_space=None):
        kwargs = {"address": address, "size": count, "word_size": 4}
        if address_space is not None:
            kwargs["address_space"] = address_space
        value = self.call("apu.mrd" + ("." + address_space if address_space else ""),
                          self.targets["apu"].mrd, "--value", **kwargs)
        rows = [value] if count == 1 else value
        r.require(type(rows) is list and len(rows) == count and
                  all(type(item) is int and 0 <= item <= 0xFFFFFFFF for item in rows),
                  "物理读回长度或类型错误")
        self.record.setdefault("readbacks", []).append({"address": address, "words": rows,
            "raw_le_hex": struct.pack("<" + "I" * count, *rows).hex()})
        return rows


def _new_session(runtime, config, directory, label):
    """在指定隔离目录建立全新XSDB session/controller。"""
    apis = r.load_apis("csr")
    journal = r.Journal(directory / "runtime_calls.jsonl")
    xsdb = session = channel = controller = None
    try:
        xsdb, serial = runtime.modules(config)
        session, channel = runtime.session(xsdb, serial, config, journal, lambda value: None)
        controller = PhysicalController(session, config["bindings"], directory)
        return apis, journal, xsdb, session, channel, controller
    except BaseException:
        if session is not None:
            try:
                session.disconnect(**({"chan": channel} if channel is not None else {}))
            except BaseException:
                pass
        if xsdb is not None:
            try:
                xsdb.dispose()
            except BaseException:
                pass
        journal.close()
        raise


def _close_session(journal, xsdb, session, channel, controller, cleanup_errors, label):
    """关闭本脚本新建的controller/session及日志，收集每项异常。"""
    for name, action in (("controller", lambda: controller.close() if controller else None),
                         ("session", lambda: session.disconnect(**({"chan": channel} if channel is not None else {})) if session else None),
                         ("xsdb", lambda: xsdb.dispose() if xsdb else None)):
        try:
            action()
        except BaseException as error:
            cleanup_errors.append({"session": label, "step": name, "error": repr(error)})
    try:
        journal.close()
    except BaseException as error:
        cleanup_errors.append({"session": label, "step": "journal", "error": repr(error)})


def _stop_vdma_and_reset(controller, session, xsa, cold_basis, record):
    """只清两个冻结VDMA通道RUNSTOP，等待HALTED，卸载映射，再观察EOS0复位。"""
    expected_ranges = [[0x43000000, 0x4300FFFF], [0x43010000, 0x4301FFFF]]
    apu = controller.call("session.select_apu.video_map", session.targets,
                          id=vars(controller.targets["apu"])["_id"])
    r.require(not session._designtable and not session._memmap_ctxs,
              "新stage3检查session已有硬件映射")
    record["stage3_mapping_attempted"] = True
    controller.call("apu.loadhw.gray_vdma_only", apu.loadhw, hw=str(xsa), mem_ranges=expected_ranges)
    mapped = session._memmap_ctxs.get(session._curchan, {}).get(vars(apu)["_ctx"], {})
    actual = sorted((row.get("base"), row.get("high"), row.get("type"), row.get("flags"))
                    for row in mapped.values())
    r.require(actual == [(base, high, "REGISTER", 3) for base, high in expected_ranges],
              "SDK实际VDMA映射范围/权限不符")
    record["stage3_vdma_map"] = {"xsa": str(xsa), "ranges": mapped}
    record["vdma"] = []
    try:
        for label, address in (("MM2S", 0x43000000), ("S2MM", 0x43010030)):
            controller.gate(both=True)
            before = controller.words(address, 2, "AP0")
            r.require(before[0] & 4 == 0, "VDMA RESET位为1，禁止停止与system reset")
            row = {"channel": label, "control_address": address, "before": before, "poll": []}
            record["vdma"].append(row)
            controller.call("apu.mwr.vdma_stop." + label, controller.targets["apu"].mwr,
                            "--bypass_cache_synq", address=address, size=1, word_size=4,
                            words=[before[0] & ~1])
            deadline = time.monotonic() + 5
            while True:
                current = controller.words(address, 2, "AP0")
                row["poll"].append(current)
                if current[0] & 1 == 0 and current[1] & 1:
                    row["status"] = "HALTED_RUNSTOP0"
                    break
                r.require(time.monotonic() < deadline, "VDMA停止超时，禁止system reset")
                time.sleep(0.05)
    finally:
        if record.get("stage3_mapping_attempted"):
            try:
                video_apu = controller.call("session.select_apu.gray_vdma_unmap", session.targets,
                    id=vars(controller.targets["apu"])["_id"])
                controller.call("apu.unloadhw.gray_vdma_only", video_apu.unloadhw)
                r.require(not session._designtable and not any(session._memmap_ctxs.values()),
                          "冻结VDMA映射卸载后SDK表非空")
                record["stage3_mapping_attempted"] = False
                record["stage3_vdma_map_cleanup"] = "UNLOADED_AND_SDK_MAP_EMPTY"
            except BaseException as error:
                record["stage3_vdma_map_cleanup_error"] = repr(error)
                raise
    record["stage3_quiescence"] = "BOTH_VDMA_HALTED_AND_MAPPING_UNLOADED"
    controller.system_reset_stop(cold_basis)
    record["stage3_system_reset"] = controller.record.get("system_reset")
    record["stage3_eos0"] = [row for row in controller.record.get("configuration_observations", [])
                              if row.get("phase") == "after_system_reset" and row.get("eos") == 0]
    r.require(record["stage3_eos0"], "stage3至EOS0复位观察缺失")


def main() -> int:
    """创建新证据目录，识别现场并在全新部署session恢复2B至安全IDLE。"""
    r.require(ROOT.is_dir() and OUT.parent.is_dir() and not OUT.exists(),
              "新RunId证据路径不存在或已存在，拒绝覆盖")
    OUT.mkdir()
    preflight_dir = OUT / "preflight"
    deployment_dir = OUT / "deployment"
    preflight_dir.mkdir()
    deployment_dir.mkdir()
    script_copy = OUT / "execution_script.py"
    save_json(OUT / "script_binding.json", {"path": str(Path(__file__).resolve()),
        "sha256": sha(Path(__file__).read_bytes()), "source_commit": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
            encoding="utf-8", check=True).stdout.strip()})
    script_copy.write_bytes(Path(__file__).read_bytes())
    apis = r.load_apis("csr")
    frozen = verify_frozen_inputs(apis)
    stage3_app_raw = STAGE3_APP.read_bytes()
    original_app_path = r.exact_path(ROOT / "report/evidence/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04_artifacts/infer.elf", "file")
    original_app_raw = original_app_path.read_bytes()
    config = _runtime_config()
    # 部署仍绑定已验证R04 init/XSA/bit/original infer；只替换当前SDK、服务和runner身份。
    r.require(r.exact_path(config["bindings"]["app_elf"]["path"], "file") == original_app_path and
              sha(original_app_raw) == config["bindings"]["app_elf"]["sha256"],
              "R10冻结原R04 infer ELF绑定或SHA漂移")
    frozen["2b_original_infer"] = {"path": str(original_app_path), "sha256": sha(original_app_raw)}
    config_raw = (json.dumps(config, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")
    with (OUT / "input_config.json").open("xb") as stream:
        stream.write(config_raw)
        stream.flush()
        import os
        os.fsync(stream.fileno())
    save_json(OUT / "frozen_inputs.json", {key: value for key, value in frozen.items() if key != "stage3_elf"})
    record = {"schema_version": 1, "run_id": RUN_NAME, "scope": "RESTORE_2B_ONLY_NOT_ACCEPTANCE",
              "status": "IN_PROGRESS", "source_commit": config["source_commit"],
              "input_config_sha256": sha(config_raw), "frozen_inputs": str(OUT / "frozen_inputs.json"),
              "cleanup_errors": [], "current_scene": None,
              "limitations": ["不执行UART模型请求、不做G3/G4/G5验收。", "不改传感器/I2C寄存器。",
                              "本次system reset不是POR，不能据此声称旧AXI生命周期终止。", "峰值内存未测。"]}
    runtime = r.ProductionRuntime()
    xsdb = session = channel = controller = journal = None
    helper = owner = None
    map_record = {"verified_inputs": {"compat_artifacts": {"implemented_xsa": config["bindings"]["xsa"]}},
                  "cleanup_errors": []}
    try:
        record["runtime_identity"] = runtime.identity(config)
        pre_apis, journal, xsdb, session, channel, controller = _new_session(
            runtime, config, preflight_dir, "preflight")
        # 先记录现场核状态和PC；已结束的stage3恢复任务允许停下活动核，再用实读指令唯一分类。
        target_rows = controller.call("session.targets.properties", session.targets, "--target_properties")
        selected = pre_apis.jtag.validate_targets(target_rows)
        controller.refresh_targets(selected)
        controller.record["targets"] = selected
        states_before = {name: controller.state(name) for name in ("cpu0", "cpu1")}
        pcs_before = {name: controller.pc(name) for name in ("cpu0", "cpu1")}
        record["preflight_cpu"] = {"states_before": states_before, "pc_before": pcs_before,
            "stop_authorization": {
                "cpu0": "当前2B恢复任务独占硬件；用户已授权恢复已结束的stage3应用，root明确授权本任务XSDB stop CPU0。",
                "cpu1": "当前2B恢复任务独占硬件；用户已授权恢复已结束的stage3应用，root明确授权本任务XSDB stop CPU1。"}}
        stage3_elf = frozen["stage3_elf"]
        original_elf = pre_apis.elf_parser.parse_elf(original_app_raw)
        any_core_running = any(value == "Running" for value in states_before.values())
        if any_core_running:
            for name in ("cpu1", "cpu0"):
                if states_before[name] == "Running":
                    controller.call(name + ".stop.ended_stage3_restore", controller.targets[name].stop)
            controller.gate(both=True)
        else:
            controller.gate(both=True)
        states_after = {name: controller.state(name) for name in ("cpu0", "cpu1")}
        pcs_after = {name: controller.pc(name) for name in ("cpu0", "cpu1")}
        r.require(states_after["cpu0"].startswith("Stopped"), "CPU0未停止，禁止AP0代码读回")
        record["preflight_cpu"].update(states_after=states_after, pc_after=pcs_after)
        stage3_match = None
        original_match = None
        try:
            stage3_match = _validate_live_pc(controller, pre_apis, stage3_elf, stage3_app_raw, "stage3.v10_read")
        except BaseException as error:
            record["preflight_cpu"]["stage3_pc_match_error"] = repr(error)
        try:
            original_match = _validate_live_pc(controller, pre_apis, original_elf, original_app_raw, "2b.original_infer")
        except BaseException as error:
            record["preflight_cpu"]["2b_pc_match_error"] = repr(error)
        r.require((stage3_match is None) != (original_match is None),
                  "PC处指令未能唯一匹配冻结stage3 v10_read或原R04 infer ELF")
        if stage3_match is not None:
            record["current_scene"] = "STAGE3_V10_READ"
            record["stage3_pc_match"] = stage3_match
            for name in ("cpu1",):
                if not states_after[name].startswith("Stopped"):
                    controller.call(name + ".stop.stage3_transition", controller.targets[name].stop)
            controller.gate(both=True)
            xsa = r.exact_path(STAGE3_XSA, "file")
            record["stage3_vdma_hwh_ranges"] = _verify_vdma_xsa(xsa)
            _stop_vdma_and_reset(controller, session, xsa, config["cold_basis"], record)
            save_json(OUT / "stage3_quiescence.json", {key: value for key, value in record.items()
                if key.startswith("stage3_") or key in ("current_scene", "preflight_cpu", "vdma")})
        else:
            record["current_scene"] = "2B_ORIGINAL_R04_INFER"
            record["2b_pc_match"] = original_match
            r.require(all(value.startswith("Stopped") for value in states_after.values()),
                      "2B scene has a running core; safe IDLE-only preflight refuses to stop it")
            controller.gate(both=True)
            snapshot = controller.stable_csr("pre_restore_2b_safe_idle")
            pre_apis.csr_flow.csr.idle(snapshot)
            record["pre_restore_2b"] = {"csr": snapshot, "status": "SAFE_IDLE_LEDGER0"}
        _close_session(journal, xsdb, session, channel, controller, record["cleanup_errors"], "preflight")
        journal = xsdb = session = channel = controller = None
        r.require(not record["cleanup_errors"],
                  "preflight controller/session/XSDB/journal关闭失败，停止后续复位与部署")

        # helper使用全新session与空SDK映射表，避免复用旧memmap上下文外壳。
        dep_apis, journal, xsdb, session, channel, controller = _new_session(
            runtime, config, deployment_dir, "deployment")
        controller.select_and_gate()
        if record["current_scene"] == "STAGE3_V10_READ":
            controller.record["stage3_preflight_reset"] = record.get("stage3_system_reset")
        controller.system_reset_stop(config["cold_basis"])
        record["deployment_reset"] = controller.record.get("system_reset")
        helper, _ = r.load_pinned_csr_map_helper()
        helper_config = {"sdk_files": config["runtime"]["sdk_files"]}
        owner = {}
        helper.register_csr_debug_map(helper_config, map_record, journal, session, controller, owner)
        controller.deploy()
        controller.call("cpu0.stop.restored_app", controller.targets["cpu0"].stop)
        controller.gate()
        restored = controller.stable_csr("restored_2b_safe_idle")
        dep_apis.csr_flow.csr.idle(restored)
        record["restored_csr"] = restored
        record["restored_pc"] = controller.pc()
        record["deployment"] = controller.record
        record["csr_debug_map"] = map_record
        record["status"] = "RESTORED_2B_IDLE_APP_STOPPED_NOT_ACCEPTANCE"
    except BaseException as error:
        record.update(status="FAILED_RESTORE", error=repr(error), traceback=traceback.format_exc())
        if controller is not None and controller.cpu0_touched and not controller.failed:
            try:
                controller.fail_stop()
            except BaseException as stop_error:
                record["fail_stop_error"] = repr(stop_error)
    finally:
        if helper is not None and session is not None and owner and owner.get("attempted"):
            try:
                helper.clear_csr_debug_map({"sdk_files": config["runtime"]["sdk_files"]},
                    map_record, journal, session, owner)
            except BaseException as error:
                record["cleanup_errors"].append({"step": "csr_map", "error": repr(error)})
        if journal is not None:
            _close_session(journal, xsdb, session, channel, controller,
                           record["cleanup_errors"], "deployment")
        record["cleanup_errors"].extend({"step": "csr_map_helper", "error": item}
                                        for item in map_record.get("cleanup_errors", []))
        record["finished_at_utc8"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
        save_json(OUT / "restore_result.json", record)
    print(json.dumps({key: record.get(key) for key in
        ("status", "current_scene", "error", "restored_pc", "restored_csr", "cleanup_errors")},
        ensure_ascii=False))
    return 0 if record["status"] == "RESTORED_2B_IDLE_APP_STOPPED_NOT_ACCEPTANCE" and not record["cleanup_errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
