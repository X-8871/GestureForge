"""借用既有Vitis会话运行隔离CPU BRESP诊断并保存待恢复现场。"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

try:
    from . import s2b_board_acceptance as model
    from . import s2b_board_jtag as jtag
    from . import s2b_board_transport as transport
    from . import s2b_csr_board_acceptance as csr
    from .check_s2b_ps_smoke_layout import parse_elf
except ImportError:
    import s2b_board_acceptance as model
    import s2b_board_jtag as jtag
    import s2b_board_transport as transport
    import s2b_csr_board_acceptance as csr
    from check_s2b_ps_smoke_layout import parse_elf


ROOT = Path(__file__).absolute().parents[1]
RUN_ID = "cpu_bresp_diag_ocm_20261019_r05"
DIAG_DIR = ROOT / "report" / "evidence" / "S2B-T20" / RUN_ID
DIAG_ELF_SHA256 = "a40efe0cab5be792eb2f1edd5b661dd59f7531283cb0a545b6ee34c7c1f88c8d"
DIAG_ASM_SHA256 = "c18c90bcc9c64df426b8aa04904388ad802b922fdeacfec94990661db7f9de09"
APP_ELF_SHA256 = "a51499895e9387a74db87a3267843b9fbf7fdfa8b6646fcbc5db01485e090bf8"
MAILBOX_BASE = 0x0002E000
MAILBOX_BYTES = 0x1000
CPU1_PARK_PC = 0xFFFFFF34
CSR_BASE = 0x43C00000
CSR_STATUS = 0x00C
CSR_EPOCH_LO = 0x050
CSR_EPOCH_HI = 0x054
CSR_RESULT_FRAME = 0x058
CSR_LAST_REJECT = 0x064
CSR_AXI_PROGRESS = 0x068
STATE_IDLE = 0
STATE_RUN = 2
OWNER_PL = 1 << 8
SAFE_REUSE = 1 << 10
TERMINAL = 1 << 11
AXI_PENDING = 1 << 12
FIRST_PENDING = 1 << 13
MAGIC_STARTED = 0x42524453
MAGIC_SLVERR = 0x4252444F
MAGIC_UNKNOWN = 0x4252554E
MAGIC_FAIL = 0x42524641


class CpuBrespExperimentError(RuntimeError):
    """前置条件、真实运行或证据不满足诊断约束。"""


def require(condition: bool, message: str) -> None:
    """拒绝不满足的运行条件。"""
    if not condition:
        raise CpuBrespExperimentError(message)


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "JSON含重复字段")
        result[key] = value
    return result


def _binding_bytes(binding: dict) -> tuple[Path, bytes]:
    """读取严格的路径与SHA绑定。"""
    require(type(binding) is dict and set(binding) == {"path", "sha256"}, "文件绑定字段错误")
    path = Path(binding["path"]).resolve(strict=True)
    require(path.is_file(), "绑定目标不是文件")
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == binding["sha256"], "绑定文件SHA不符")
    return path, raw


def _json_binding(binding: dict) -> tuple[Path, dict]:
    path, raw = _binding_bytes(binding)
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs)
    require(type(value) is dict, "绑定JSON根节点必须是对象")
    return path, value


def _diag_static_layout(diag_binding: dict) -> tuple[dict, Path]:
    """核对冻结诊断ELF身份、PT_LOAD布局和busy store符号。"""
    path, raw = _binding_bytes(diag_binding)
    require(path == DIAG_DIR / "s2b_bresp_diag.elf" and hashlib.sha256(raw).hexdigest() == DIAG_ELF_SHA256,
            "诊断ELF不是独审PASS的R04冻结候选")
    manifest_path = DIAG_DIR / "build_result.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)
    artifact = manifest.get("artifacts", {}).get("s2b_bresp_diag.elf", {})
    source = manifest.get("source", {})
    require(manifest.get("status") == "OFFLINE_BUILD_OK_NOT_HARDWARE_RESULT" and
            artifact.get("sha256") == DIAG_ELF_SHA256 and source.get("sha256") == DIAG_ASM_SHA256,
            "冻结构建清单未绑定R05候选ELF/汇编")
    elf = parse_elf(raw)
    entry = elf["entry"]
    loads = [p for p in elf["programs"] if p["type"] == 1 and p["memory_size"]]
    require(entry == 0xC020 and len(loads) == 2, "诊断ELF入口或PT_LOAD数量变化")
    expected = {(0xC000, 0x5FC, 0x5FC), (0x10000, 0, 0x4000)}
    actual = {(p["physical"], p["file_size"], p["memory_size"]) for p in loads}
    require(actual == expected, "诊断ELF PT_LOAD布局与冻结清单不一致")
    require(all(p["virtual"] == p["physical"] and 0 <= p["physical"] and
                p["physical"] + p["memory_size"] <= 0x30000 for p in loads), "诊断ELF PT_LOAD超出低OCM")
    symbols = [s for s in elf["symbols"] if s["name"] == "diag_busy_start_store" and s["section"] != 0]
    require(len(symbols) == 1 and symbols[0]["value"] == 0xC344, "busy store符号身份变化")
    return ({"path": str(path), "sha256": DIAG_ELF_SHA256, "entry": entry,
            "loads": sorted([{"physical": p["physical"], "file_size": p["file_size"],
                               "memory_size": p["memory_size"]} for p in loads], key=lambda p: p["physical"]),
            "busy_store_pc": symbols[0]["value"], "mailbox": [MAILBOX_BASE, MAILBOX_BASE + MAILBOX_BYTES]}, path)


def _diag_layout(diag_binding: dict, review_binding: dict) -> dict:
    """将独审PASS绑定到实际R05诊断ELF。"""
    layout, _ = _diag_static_layout(diag_binding)
    review_path, review = _json_binding(review_binding)
    source_rows = review.get("source_bindings", [])
    require(review.get("verdict") == "PASS" and any(
            row.get("path", "").endswith(("vitis/s2b_bresp_diag.S", "vitis\\s2b_bresp_diag.S")) and
            row.get("current_sha256") == DIAG_ASM_SHA256 for row in source_rows if type(row) is dict),
            "独审回执未通过或未绑定R05汇编")
    layout["review"] = {"path": str(review_path), "sha256": review_binding["sha256"]}
    return layout


def _verify_app_pc(controller, app_elf: dict, app_raw: bytes) -> dict:
    """用真实CPSR和DAP指令字节核对停驻PC属于绑定app ELF。"""
    cpsr_data = controller.call("cpu0.rrd.cpsr.cpu_bresp", controller.targets["cpu0"].rrd,
                                "--nvlist", reg="cpsr")
    require(type(cpsr_data) is dict and set(cpsr_data) == {"cpsr"} and
            type(cpsr_data["cpsr"]) is int and 0 <= cpsr_data["cpsr"] <= 0xFFFFFFFF,
            "CPU0 CPSR结构化返回字段或范围错误")
    cpsr_value = cpsr_data["cpsr"]
    pc = controller.pc()
    thumb = bool(cpsr_value & (1 << 5))
    require(pc % (2 if thumb else 4) == 0, "CPU0 PC与CPSR执行状态对齐错误")
    read_address = pc & ~3
    count = (pc - read_address + 16 + 3) // 4
    words = controller.words(read_address, count)
    observed = b"".join(word.to_bytes(4, "little") for word in words)
    observed = observed[pc - read_address:pc - read_address + 16]
    exec_loads = [row for row in app_elf["programs"] if row["type"] == 1 and row["flags"] & 1 and
                  row["file_size"] >= 16 and row["virtual"] <= pc and
                  pc + 16 <= row["virtual"] + row["file_size"]]
    sections = [row for row in app_elf["sections"] if row["flags"] & 4 and row["type"] != 8 and
                row["size"] >= 16 and row["address"] <= pc and pc + 16 <= row["address"] + row["size"]]
    matches = []
    for load in exec_loads:
        for section in sections:
            file_offset = section["offset"] + pc - section["address"]
            if (section["offset"] >= load["offset"] and
                    file_offset == load["offset"] + pc - load["virtual"] and
                    file_offset >= load["offset"] and
                    file_offset + 16 <= load["offset"] + load["file_size"]):
                matches.append(file_offset)
    require(len(matches) == 1 and len(observed) == 16 and
            app_raw[matches[0]:matches[0] + 16] == observed,
            "CPU0 PC附近16字节与冻结infer.elf可执行段不一致")
    return {"pc": pc, "cpsr": cpsr_value, "thumb": thumb,
            "instruction_bytes_sha256": hashlib.sha256(observed).hexdigest(),
            "verification": "MATCH_EXECUTABLE_LOAD_AND_SECTION"}


def classify_mailbox(words: list[int], busy_store_pc: int) -> dict:
    """按mailbox原字及ABI规则分类；不能将外部abort或通用错误提升为SLVERR。"""
    require(type(words) is list and len(words) == 64 and
            all(type(word) is int and 0 <= word <= 0xFFFFFFFF for word in words), "mailbox必须是64个32位字")
    magic = words[0]
    if magic != MAGIC_SLVERR:
        return {"classification": "UNKNOWN" if magic == MAGIC_UNKNOWN else "FAIL",
                "mailbox_magic": magic, "reason_code": words[31]}
    # mailbox偏移以字节计；只接受ARM同步外部写abort及唯一目标指令。
    dfsr, fault_pc, opcode, dfar = words[19], words[22], words[23], words[24]
    before_status, before_reject = words[14], words[15]
    before_epoch = words[16] | words[17] << 32
    before_frame = words[18]
    after_status, after_epoch = words[25], words[26] | words[27] << 32
    after_frame, after_reject, after_ledger = words[28], words[29], words[30]
    dfsr_fs = dfsr & 0xF
    valid = (dfsr_fs == 0x8 and not (dfsr & (1 << 10)) and (dfsr & (1 << 11)) != 0 and
             (dfsr & (1 << 12)) != 0 and dfar == CSR_BASE + 8 and fault_pc == busy_store_pc and
             opcode == 0xE5801000 and before_status & 7 == STATE_RUN and before_status & OWNER_PL and
             not (before_status & (SAFE_REUSE | TERMINAL)) and
             after_status & 7 == STATE_RUN and not (after_status & (SAFE_REUSE | TERMINAL)) and
             before_reject == 0 and after_reject == 1 and before_epoch == after_epoch and
             before_frame == after_frame and after_status & OWNER_PL)
    return {"classification": "SLVERR" if valid else "UNKNOWN",
            "mailbox_magic": magic, "fault_status": dfsr, "fault_pc": fault_pc,
            "opcode": opcode, "dfar": dfar, "epoch_before": before_epoch,
            "epoch_after": after_epoch, "frame_before": before_frame,
            "frame_after": after_frame, "last_reject_before": before_reject,
            "last_reject_after": after_reject, "axi_progress_after": after_ledger}


def _validate_r08_result(binding: dict, deployment_bindings: dict) -> dict:
    """核验R08真实seed、ACK、recovery黄金和闭合清单。"""
    result_path, result = _json_binding(binding)
    require(result.get("scope") == "CSR_RECOVERY_ONLY" and
            result.get("hardware_execution") == "BORROWED_SESSION_UART_DAP_REQUESTED", "R08结果不是实际借用会话")
    stages = {row.get("name"): row for row in result.get("stages", []) if type(row) is dict}
    require(stages.get("sample000_seed_frame0", {}).get("status") == "PASS_SAMPLE000_SEED_ONLY" and
            stages.get("sample000_reaccept_frame0", {}).get("status") == "PASS_SAMPLE000_REACCEPT_FRAME0_ONLY" and
            stages.get("wait_final_ack_sample000_recovery", {}).get("status") == "SCENARIO_RESULTS_SAVED_NOT_STAGE_ACCEPTANCE",
            "R08缺少完整sample000 seed/reaccept/ACK recovery阶段")
    outputs = {}
    for item in result.get("t20_outputs", []):
        require(type(item) is dict and set(item) == {"path", "sha256"}, "R08产物绑定字段错误")
        path, raw = _binding_bytes(item)
        outputs[path] = hashlib.sha256(raw).hexdigest()
    seed_dir = Path(stages["sample000_seed_frame0"]["evidence_dir"]).resolve(strict=True)
    recovery_dir = Path(stages["wait_final_ack_sample000_recovery"]["evidence_dir"]).resolve(strict=True)
    seed_path = (seed_dir / "acceptance_result.json").resolve(strict=True)
    recovery_path = (recovery_dir / "csr_result.json").resolve(strict=True)
    golden_path = (recovery_dir / "golden_sample000" / "acceptance_result.json").resolve(strict=True)
    require(all(path in outputs for path in (seed_path, recovery_path, golden_path)),
            "R08闭合清单未绑定seed、recovery或sample000黄金结果")
    seed = json.loads(seed_path.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)
    recovery = json.loads(recovery_path.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)
    golden = json.loads(golden_path.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)
    require(seed.get("status") == "PASS_SAMPLE000_SEED_ONLY" and
            seed.get("hardware_execution") == "BORROWED_SESSION_UART_DAP_REQUESTED" and
            [(r.get("phase"), r.get("frame")) for r in seed.get("frames", [])] ==
            [("weights", 0), ("csr_seed", 0)], "R08 seed receipt结构不符")
    weights_dir = Path(seed["frames"][0]["directory"]).resolve(strict=True)
    seed_frame_dir = Path(seed["frames"][1]["directory"]).resolve(strict=True)
    weights_result_path = (weights_dir / "result.json").resolve(strict=True)
    seed_frame_result_path = (seed_frame_dir / "result.json").resolve(strict=True)
    capture_path = (seed_frame_dir / "capture_check.json").resolve(strict=True)
    require(all(path in outputs for path in (weights_result_path, seed_frame_result_path, capture_path)),
            "R08结果清单未绑定权重LOAD、sample000原UART结果或黄金比较")
    weights_result = json.loads(weights_result_path.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)
    seed_frame_result = json.loads(seed_frame_result_path.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)
    capture = json.loads(capture_path.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)
    require(weights_result.get("status") == "PASS_PROTOCOL_RESPONSE" and
            weights_result.get("meta", {}).get("response_code") == 0 and
            seed_frame_result.get("status") == "PASS_RESPONSE_AND_CAPTURE" and
            seed_frame_result.get("phase") == "csr_seed" and seed_frame_result.get("frame") == 0 and
            seed_frame_result.get("meta", {}).get("response_code") == 0 and
            capture.get("status") == "PASS_OFFLINE_CAPTURE_CHECK",
            "R08同版LOAD/RUN真实收据或sample000完整双头/框黄金比较失败")
    recovered_bindings = recovery.get("admission", {}).get("deployment_bindings")
    require(type(recovered_bindings) is dict and
            all(recovered_bindings.get(name) == deployment_bindings.get(name)
                for name in ("init_elf", "app_elf", "xsa", "bit")) and
            recovery.get("status") == "SCENARIO_RESULTS_SAVED_NOT_STAGE_ACCEPTANCE" and
            any(row.get("name") == "dap_abort_hot_recovery" and row.get("status") == "PASS"
                for row in recovery.get("scenarios", [])), "R08 recovery未绑定当前部署或ACK后恢复未通过")
    ack_calls = [row for row in recovery.get("dap_calls", [])
                 if row.get("api") == "t20.wire.abort.explicit_ack" and row.get("status") == "RETURNED"]
    require(len(ack_calls) == 1, "R08真实ACK调用证据缺失或重复")
    require(golden.get("status") == "PASS_SAMPLE000_AFTER_ABORT_ONLY" and
            golden.get("hardware_execution") == "BORROWED_SESSION_DAP_REQUESTED" and
            any(row.get("phase") == "recovery" and row.get("frame") == 1 and row.get("epoch") == 5
                for row in golden.get("frames", [])), "R08 ACK后sample000黄金结果不完整")
    return {"r08_result": {"path": str(result_path), "sha256": binding["sha256"]},
            "seed_result": {"path": str(seed_path), "sha256": outputs[seed_path]},
            "ack_recovery_result": {"path": str(recovery_path), "sha256": outputs[recovery_path]},
            "golden_result": {"path": str(golden_path), "sha256": outputs[golden_path]},
            "ack_api": ack_calls[0]["api"], "ack_status": ack_calls[0]["status"],
            "golden_epoch": 5, "golden_frame": 1}


def execute_cpu_bresp_experiment(controller, r08_result_binding, diag_elf_binding, review_binding, run_dir, *,
                                 safe_observation_timeout=180.0,
                                 poll_interval=0.05) -> dict:
    """运行一次诊断；失败时停驻并保存待恢复状态，不恢复旧app执行上下文。"""
    require(type(controller) is jtag.JtagController,
            "必须借用真实JTAG控制器")
    run = transport.exact_path(run_dir, "directory")
    require(run.parent == transport.exact_path(ROOT / "report/evidence/S2B-T20", "directory") and
            not any(p.name in ("cpu_bresp_result.json", "cpu_bresp_events.jsonl") for p in run.iterdir()),
            "输出必须是新的S2B-T20独立RunId")
    require(type(safe_observation_timeout) in (int, float) and safe_observation_timeout > 0 and
            type(poll_interval) in (int, float) and poll_interval > 0, "SAFE观察期限参数错误")
    layout = _diag_layout(diag_elf_binding, review_binding)
    require(controller.bindings["app_elf"]["sha256"] == APP_ELF_SHA256,
            "当前控制器未绑定正式R04 infer.elf上下文")
    seed = _validate_r08_result(r08_result_binding, controller.bindings)
    controller.verify_bindings()
    controller.gate(both=True)
    require(controller.state("cpu0").startswith("Stopped") and controller.state("cpu1").startswith("Stopped"),
            "诊断前CPU0/CPU1均须已停止")
    cpu1_pc = controller.pc("cpu1")
    ocm_cfg = controller.words(0xF8000910, 1)[0]
    require(cpu1_pc == CPU1_PARK_PC and ocm_cfg == 0x18, "CPU1停驻PC或OCM_CFG现场不符合R04")
    before = csr.checked_snapshot(controller.stable_csr("cpu_bresp_before"))
    csr.idle(before)
    require(csr.epoch(before) == seed["golden_epoch"] and before[CSR_RESULT_FRAME] == seed["golden_frame"],
            "当前CSR任务身份与R08最后闭合黄金不一致")
    require(before[CSR_AXI_PROGRESS] == 0 and before[0x018] == 0 and before[0x01C] == 519168 and
            before[0x020] == 0x00100000 and before[0x024] == 5903100,
            "启动诊断前未处于安全空闲且AXI账本为零")
    app_raw = jtag.bound_bytes(controller.bindings["app_elf"])
    app_elf = parse_elf(app_raw)
    original_pc = controller.pc()
    app_pc_evidence = _verify_app_pc(controller, app_elf, app_raw)
    original = {"app_elf": controller.bindings["app_elf"], "app_entry": app_elf["entry"],
                "cpu0_pc": original_pc, "pc_evidence": app_pc_evidence,
                "cpu1_pc": cpu1_pc, "ocm_cfg": ocm_cfg}
    record = {"schema_version": 1, "status": "IN_PROGRESS", "hardware_execution": "BORROWED_SESSION_REQUESTED",
              "seed_provenance": seed, "diag_elf": layout, "original_app_context": original,
              "before_csr": before, "events": [], "limitations": [
                  "不执行ACK、reset、重试或清理AXI账本。",
                  "诊断ELF覆盖CPU0执行现场；SDK未提供CPU寄存器/栈/MMU连续上下文快照恢复API。",
                  "仅在真实DONE_SAFE/ERROR_SAFE且pending清零后允许由总控重载原R04 infer.elf并从入口建立新语境。"]}
    event_path = run / "cpu_bresp_events.jsonl"
    result_path = run / "cpu_bresp_result.json"
    with event_path.open("x", encoding="utf-8", newline="\n") as event_file:
        def event(name, value):
            row = {"event": name, "value": value}
            record["events"].append(row)
            event_file.write(json.dumps(row, ensure_ascii=False, default=repr) + "\n")
            event_file.flush()

        try:
            controller.call("cpu0.dow.cpu_bresp_diag", controller.targets["cpu0"].dow,
                            file=layout["path"], auto_stop=True, set_entry=True)
            controller.gate(both=True)
            require(controller.pc() == layout["entry"], "诊断ELF下载后PC与入口不符")
            event("diag_loaded", {"entry": layout["entry"], "elf_sha256": layout["sha256"]})
            controller.call("cpu0.con.cpu_bresp_diag", controller.targets["cpu0"].con, "--block", timeout=30)
            controller.gate(both=True)
            require(controller.state("cpu0").startswith("Stopped"), "诊断ELF未停驻")
            mailbox = controller.words(MAILBOX_BASE, 64)
            classification = classify_mailbox(mailbox, layout["busy_store_pc"])
            record.update(mailbox_words=mailbox, cpu_classification=classification)
            event("mailbox", classification)

            deadline = time.monotonic() + safe_observation_timeout
            final = None
            while time.monotonic() < deadline:
                controller.gate(both=True)
                snapshot = csr.checked_snapshot(controller.stable_csr("cpu_bresp_wait_safe"))
                status = snapshot[CSR_STATUS]
                safe = (status & 7 in (4, 5) and status & SAFE_REUSE and status & TERMINAL and
                        not status & (OWNER_PL | AXI_PENDING | FIRST_PENDING) and snapshot[CSR_AXI_PROGRESS] == 0)
                if safe:
                    require(csr.epoch(snapshot) == csr.epoch(before) + 1 and snapshot[CSR_RESULT_FRAME] == 0,
                            "诊断安全终态不属于本次新epoch/frame0任务")
                    final = snapshot
                    break
                time.sleep(poll_interval)
            if final is None:
                record.update(status="UNKNOWN_SAFE_PENDING", recovery_ready=False,
                              last_observed_csr=snapshot,
                              recovery_instruction="保持CPU0停驻；等待真实SAFE与pending清零，禁止按经过时间恢复或重置。")
            else:
                controller.call("cpu0.dow.restore_app_entry", controller.targets["cpu0"].dow,
                                file=controller.bindings["app_elf"]["path"], auto_stop=True, set_entry=True)
                controller.gate(both=True)
                require(controller.pc() == app_elf["entry"], "原R04 infer.elf重新下载后PC不在入口")
                entry_loads = [p for p in app_elf["programs"] if p["type"] == 1 and p["flags"] & 1 and
                               p["virtual"] <= app_elf["entry"] and
                               app_elf["entry"] + 16 <= p["virtual"] + p["file_size"]]
                require(len(entry_loads) == 1, "原app入口不在唯一可执行文件LOAD中")
                load = entry_loads[0]
                offset = load["offset"] + app_elf["entry"] - load["virtual"]
                expected = app_raw[offset:offset + 16]
                actual = b"".join(word.to_bytes(4, "little") for word in
                                  controller.words(app_elf["entry"], 4))
                require(len(expected) == len(actual) == 16 and actual == expected,
                        "原R04 app入口内存字节与冻结ELF不一致")
                restored_csr = csr.checked_snapshot(controller.stable_csr("cpu_bresp_app_reloaded"))
                require(restored_csr == final, "重载原app入口后CSR/SAFE现场变化")
                record.update(status="SAFE_TERMINAL_APP_RELOADED_AT_ENTRY", recovery_ready=True, final_csr=final,
                              app_reloaded_at_entry=True, app_entry_bytes_sha256=hashlib.sha256(actual).hexdigest(),
                              recovery_instruction="原R04 infer.elf已重载并停在入口；原执行上下文未恢复，须继续由总控运行正式reentry与golden流程。")
            record["cpu_classification"] = classification
            if classification["classification"] != "SLVERR":
                record["status"] = "UNKNOWN_OR_FAIL_SAFE_PENDING" if final is None else "UNKNOWN_OR_FAIL_SAFE_TERMINAL"
            return record
        except BaseException as error:
            controller.fail_stop()
            record.update(status="FAIL_LATCHED", recovery_ready=False, error=repr(error),
                          recovery_instruction="CPU0停驻；不得ACK/reset/retry。待真实SAFE且pending清零后由总控决定重建app语境。")
            raise
        finally:
            result_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, default=repr) + "\n",
                                   encoding="utf-8", newline="\n")
