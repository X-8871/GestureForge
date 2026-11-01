"""匹配已交出的视频应用，停稳VDMA，再以既有控制器恢复2B易失部署。"""
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import time
import traceback
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(r"D:\FPGA_Competition\w2b")
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("restore_2b_runtime", ROOT / "vitis/run_s2b_model_acceptance.py")
r = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r
spec.loader.exec_module(r)
config = r.strict_json((ROOT / "report/evidence/S2B-T18/formal_online_20261018_r01/model_config_csr_20261019_r10.json").read_bytes())
identity_path = r.exact_path(ROOT / "tmp/2B/hw_server_20261021.json")
config["hw_server"] = r.strict_json(identity_path.read_bytes())
config["source_commit"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                                          text=True, check=True).stdout.strip()
runner_path = r.exact_path(ROOT / "vitis/run_s2b_model_acceptance.py")
config["bindings"]["runner_source"] = {"path": str(runner_path), "sha256": r.digest(runner_path.read_bytes())}
out = ROOT / "report/evidence/S2B-T18/stage3_to_2b_restore_20261021_r02"
assert out.parent.is_dir() and not out.exists()
out.mkdir()
r.save_json_new(out / "input_config.json", config)
(out / "execution_script.py").write_bytes(Path(__file__).read_bytes())
apis = r.load_apis("csr")
runtime = r.ProductionRuntime()
journal = r.Journal(out / "runtime_calls.jsonl")
record = {"status": "IN_PROGRESS", "scope": "RESTORE_ONLY_NOT_ACCEPTANCE", "cleanup_errors": [],
          "stage3_writes": "仅清除两个VDMA通道RUNSTOP并等HALTED；不恢复旧视频上下文"}

class PhysicalController(apis.jtag.JtagController):
    """使用官方AP0物理地址空间，所有写入与部署仍用原控制器。"""
    def words(self, address, count):
        value = self.call("apu.mrd.AP0", self.targets["apu"].mrd, "--value",
                          address=address, size=count, word_size=4, address_space="AP0")
        rows = [value] if count == 1 else value
        r.require(type(rows) is list and len(rows) == count and all(type(v) is int and 0 <= v <= 0xFFFFFFFF for v in rows), "物理读回类型或长度错误")
        self.record.setdefault("readbacks", []).append({"address": address, "words": rows,
            "raw_le_hex": struct.pack("<" + "I" * count, *rows).hex()})
        return rows

xsdb = session = channel = controller = None
video_map_attempted = False
owner = {}
helper, _ = r.load_pinned_csr_map_helper()
hc = {"sdk_files": config["runtime"]["sdk_files"]}
hr = {"verified_inputs": {"compat_artifacts": {"implemented_xsa": config["bindings"]["xsa"]}}, "cleanup_errors": []}
record["csr_debug_map_evidence"] = hr

def clear_video_map():
    """只卸载本会话视频映射，验证SDK空表后才记录成功。"""
    global video_map_attempted
    if not video_map_attempted:
        return
    apu = controller.call("session.select_apu.video_unmap", session.targets, id=vars(controller.targets["apu"])["_id"])
    controller.call("apu.unloadhw.video_vdma_only", apu.unloadhw)
    r.require(not session._designtable and not any(session._memmap_ctxs.values()), "视频硬件映射未完全卸载")
    video_map_attempted = False
    record.setdefault("video_debug_map", {})["cleanup"] = "UNLOADED_AND_SDK_MAP_EMPTY"

try:
    record["identity"] = runtime.identity(config)
    xsdb, serial = runtime.modules(config)
    session, channel = runtime.session(xsdb, serial, config, journal, lambda value: None)
    controller = PhysicalController(session, config["bindings"], out)
    controller.select_and_gate()
    handoff = r.exact_path(r"D:\codex-worktrees\dbdf\report\evidence\S3-CTRL\S3-T05\S3CTRL-20261021-003-handoff-to-dsh-stage3.md")
    r.require("OFFERED" in handoff.read_text(encoding="utf-8"), "阶段3交出依据不符")
    record["stage3_handoff"] = {"path": str(handoff), "sha256": r.digest(handoff.read_bytes())}
    phase_state = r.exact_path(r"D:\codex-worktrees\dbdf\.codex\STATE.md")
    last_line = phase_state.read_text(encoding="utf-8").strip().splitlines()[-1]
    r.require("状态/下一接手方=`OFFERED / DSH 阶段三总控`" in last_line, "阶段3已被接管或交接状态不符，禁止覆盖")
    record["stage3_state"] = {"path": str(phase_state), "sha256": r.digest(phase_state.read_bytes()), "last_line": last_line}
    app = r.exact_path(r"D:\codex-worktrees\dbdf\tmp\s3r06\t04_j11cmos2_elf_v8\elf_build\app\an5642_j11cmos2_v8_off.elf")
    raw = app.read_bytes()
    r.require(r.digest(raw) == "85e989196dc34f5f1cc7b87607b2905f54405ec95a5486cf14916edd7eec145e", "视频应用哈希不符")
    pc = controller.pc()
    cpsr = controller.call("cpu0.rrd.cpsr", controller.targets["cpu0"].rrd, "--nvlist", reg="cpsr")["cpsr"]
    aligned = pc & ~3
    observed = struct.pack("<5I", *controller.words(aligned, 5))[pc - aligned:pc - aligned + 16]
    record["stage3_app_match"] = r._validate_app_pc_instructions(apis.elf_parser.parse_elf(raw), raw, pc, cpsr, observed)
    video_xsa = r.exact_path(r"D:\codex-worktrees\dbdf\tmp\s3r06\t04_display_bluefix_20261021_r01\design_1_wrapper.xsa")
    r.require(r.digest(video_xsa.read_bytes()) == "b9a565729148be989cb37e10eaf46f0da7c5df0fec2db856a278afba9daddf17", "视频XSA哈希不符")
    with zipfile.ZipFile(video_xsa) as archive:
        members = [name for name in archive.namelist() if name.endswith(".hwh")]
        r.require(len(members) == 1, "视频HWH不唯一")
        tree = ET.fromstring(archive.read(members[0]))
    ranges = [[0x43000000, 0x4300FFFF], [0x43010000, 0x4301FFFF]]
    regions = [row.attrib for row in tree.findall(".//MEMRANGE")
               if int(row.get("BASEVALUE", "-1"), 0) in (0x43000000, 0x43010000)]
    r.require(len(regions) == 2 and all(any(int(row["BASEVALUE"], 0) == base and
              int(row["HIGHVALUE"], 0) == end and row.get("MEMTYPE") == "REGISTER"
              for row in regions) for base, end in ranges), "视频VDMA窗口不符")
    apu = controller.call("session.select_apu.video_map", session.targets, id=vars(controller.targets["apu"])["_id"])
    r.require(not session._designtable and not session._memmap_ctxs, "自有会话已有映射")
    video_map_attempted = True
    controller.call("apu.loadhw.video_vdma_only", apu.loadhw, hw=str(video_xsa), mem_ranges=ranges)
    mapped = session._memmap_ctxs.get(session._curchan, {}).get(vars(apu)["_ctx"], {})
    actual = sorted((row.get("base"), row.get("high"), row.get("type"), row.get("flags")) for row in mapped.values())
    r.require(actual == [(base, end, "REGISTER", 3) for base, end in ranges], "实际视频映射范围或权限不符")
    record["video_debug_map"] = {"xsa": {"path": str(video_xsa), "sha256": r.digest(video_xsa.read_bytes())},
                                 "hwh_regions": regions, "sdk_regions": mapped, "cleanup": "NOT_RUN"}
    record["vdma"] = []
    for label, address in (("MM2S", 0x43000000), ("S2MM", 0x43010030)):
        controller.gate()
        before = controller.words(address, 2)
        r.require(before[0] & 4 == 0, "VDMA RESET位仍为1，禁止回写或后续复位")
        row = {"channel": label, "control_address": address, "before": before, "poll": []}
        record["vdma"].append(row)
        controller.call("apu.mwr.vdma_stop." + label, controller.targets["apu"].mwr, "--bypass_cache_synq",
                        address=address, size=1, word_size=4, words=[before[0] & ~1])
        deadline = time.monotonic() + 5
        while True:
            current = controller.words(address, 2)
            row["poll"].append(current)
            if current[0] & 1 == 0 and current[1] & 1:
                row["status"] = "HALTED_RUNSTOP0"
                break
            r.require(time.monotonic() < deadline, "VDMA停止超时，禁止复位或覆盖")
            time.sleep(0.05)
    r.save_json_new(out / "stage3_quiescence.json", record)
    clear_video_map()
    controller.system_reset_stop(config["cold_basis"])
    helper.register_csr_debug_map(hc, hr, journal, session, controller, owner)
    controller.deploy()
    controller.call("cpu0.stop.restored_app", controller.targets["cpu0"].stop)
    controller.gate()
    record["restored_csr"] = controller.stable_csr("restored_2b")
    apis.csr_flow.csr.checked_snapshot(record["restored_csr"])
    apis.csr_flow.csr.idle(record["restored_csr"])
    record["restored_pc"] = controller.pc()
    record["status"] = "RESTORED_2B_IDLE_APP_STOPPED_NOT_ACCEPTANCE"
except BaseException as error:
    record.update(status="FAILED_RESTORE", error=repr(error), traceback=traceback.format_exc())
    if controller is not None and controller.cpu0_touched:
        controller.fail_stop()
finally:
    for label, action in (("video_map", clear_video_map),
                          ("controller", lambda: controller.close() if controller else None),
                          ("map", lambda: helper.clear_csr_debug_map(hc, hr, journal, session, owner) if session and owner.get("attempted") else None),
                          ("session", lambda: session.disconnect(**({"chan": channel} if channel is not None else {})) if session else None),
                          ("xsdb", lambda: xsdb.dispose() if xsdb else None)):
        try:
            action()
        except BaseException as error:
            record["cleanup_errors"].append({"step": label, "error": repr(error)})
    journal.close()
    record["cleanup_errors"].extend({"step": "map_helper", "error": error} for error in hr["cleanup_errors"])
    r.save_json_new(out / "restore_result.json", record)
print(json.dumps({key: record.get(key) for key in ("status", "error", "restored_pc", "restored_csr", "cleanup_errors")}, ensure_ascii=False))
raise SystemExit(0 if record["status"].startswith("RESTORED_") and not record["cleanup_errors"] else 2)
