"""用独立重建ELF做单样本及DDR 256B实板验收；仅由根注入真实会话。"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import traceback

if str(Path(__file__).absolute().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).absolute().parent))

from verification import check_s2b_ps_smoke_layout as elf_parser
from verification import s2b_board_acceptance as model
from verification import s2b_board_jtag as jtag
from verification import s2b_board_transport as transport
from verification import s2b_csr_board_acceptance as csr

ROOT = Path(__file__).absolute().parents[1]
TZ = timezone(timedelta(hours=8))
RECOVERY = ROOT / "report/evidence/S2B-T15/recovery_inputs_20261019_r02"
REVIEW = ROOT / "report/evidence/S2B-T15/recovery_input_review_20261019_r01/review_outcome.json"
NEW_APP = ROOT / "tmp/2B/S2B-T15/recovery_inputs_20261019_r02/attempt_03/fresh_build/infer/infer.elf"
EXPECTED_NEW_APP_SHA256 = "f7a8bc96418590a497577bb45a7cbc0cc75dec416f6af1bf9b33ffd0308fa5a9"
EXPECTED_ORIGINAL_APP_SHA256 = "a51499895e9387a74db87a3267843b9fbf7fdfa8b6646fcbc5db01485e090bf8"
EXPECTED_R04_INIT_SHA256 = "237dd959f903589c657b743ea1fce175628aaa24020384058fc66339c779e7b1"
EXPECTED_R04_XSA_SHA256 = "ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6"
EXPECTED_R04_BIT_SHA256 = "555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7"
EXPECTED_BUNDLE_SHA256 = "50b5eb62968795413e03f4474dd98800c8e2c1f0ead04003ae53b47b83ea9436"
EXPECTED_COMPARISON_SHA256 = "c6396a3558f52f9ae64d3a3c9f6c4e134783ec67d60bfd84f7f5b52e845c7108"
EXPECTED_MACHINE_RESULT_SHA256 = "65b3d4c74ed2a920cf5c8886938db2459851792722e7f1b3ac1de1aefdef6433"
EXPECTED_REVIEW_SHA256 = "6c082ec77238fa9f58668824b69073b244af0aa8e74bb6de375eba2b06950850"
EXPECTED_PREPARATION_SHA256 = "b6605206733fd8d9603e1a6e8eafef121342210c8bd4b9f128db8d5686aadfcb"
EXPECTED_BUILD_DETAILS_SHA256 = "59c42968085d656148de9aec13f4c9e623b7688fc79101038f2b661510c5c0db"
EXPECTED_SOURCE_SHA256 = "9ed222a1d132d8cc836c362b4fbe453f833387bc66173dd5eb7d5388447e9a39"
EXPECTED_ORIGINAL_INIT = ROOT / "report/evidence/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04_artifacts/init.elf"
EXPECTED_ORIGINAL_APP = ROOT / "report/evidence/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04_artifacts/infer.elf"
EXPECTED_R04_XSA = ROOT / "report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.xsa"
EXPECTED_R04_BIT = ROOT / "report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit"
EXPECTED_PREPARATION = ROOT / "report/evidence/S2B-T18/formal_online_20261018_r01/preparation_stress_first_csr_r04.json"
EXPECTED_BUILD_DETAILS = ROOT / "report/evidence/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04_artifacts/build_details.json"
EXPECTED_APP_SOURCE = ROOT / "vitis/s2b_inference_app.c"
BOOTROM_CPU_PCS = {"cpu0": 0xFFFFFF28, "cpu1": 0xFFFFFF34}
BOOTROM_UNCONFIGURED_FIELDS = {"END OF STARTUP (EOS) STATUS": 0,
                               "DONE INTERNAL SIGNAL STATUS": 0, "DONE PIN": 0,
                               "GWE STATUS": 0, "GTS_CFG_B STATUS": 0,
                               "CFG STARTUP STATE MACHINE PHASE": 0}


class RebuiltAppAcceptanceError(RuntimeError):
    """重建ELF证据、硬件现场或黄金验收未满足限定scope。"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RebuiltAppAcceptanceError(message)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _read_json(path: Path) -> tuple[dict, bytes]:
    actual = transport.exact_path(path, "file")
    raw = actual.read_bytes()
    _require(len(raw) <= 16 * 1024 * 1024, "固定证据JSON超过16MiB")

    def pairs(items):
        result = {}
        for key, value in items:
            _require(key not in result, "固定证据JSON存在重复字段")
            result[key] = value
        return result

    value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                       parse_constant=lambda _: (_ for _ in ()).throw(
                           RebuiltAppAcceptanceError("固定证据JSON包含非法常数")))
    _require(type(value) is dict, "固定证据JSON根节点必须为对象")
    return value, raw


def _bound(path: Path, expected_sha256: str) -> dict:
    actual = transport.exact_path(path, "file")
    raw = actual.read_bytes()
    _require(_sha(raw) == expected_sha256, "固定文件SHA不匹配：" + str(actual))
    return {"path": str(actual), "sha256": expected_sha256, "bytes": len(raw)}


def verify_recovery_inputs() -> dict:
    """逐字核验独审回执、重建对比、构建结果和新ELF；不改变任何输入。"""
    comparison_path = RECOVERY / "comparison.json"
    machine_path = RECOVERY / "machine_result.json"
    comparison, comparison_raw = _read_json(comparison_path)
    machine, machine_raw = _read_json(machine_path)
    review, review_raw = _read_json(REVIEW)
    _require(_sha(comparison_raw) == EXPECTED_COMPARISON_SHA256 and
             _sha(machine_raw) == EXPECTED_MACHINE_RESULT_SHA256 and
             _sha(review_raw) == EXPECTED_REVIEW_SHA256, "恢复材料或独审回执与已审版本漂移")
    _require(review.get("status") == "PASS_OFFLINE_PS_RECOVERY_SCOPE_ONLY" and
             review.get("role") == "INDEPENDENT_REVIEWER", "恢复输入包没有限定scope的独审PASS")
    bound_rows = review.get("bindings")
    _require(type(bound_rows) is list, "独审回执bindings缺失")
    for item in bound_rows:
        _require(type(item) is dict and set(item) == {"path", "sha256"}, "独审绑定格式错误")
        path = transport.exact_path(ROOT / item["path"], "file")
        _require(_sha(path.read_bytes()) == item["sha256"], "独审回执输入绑定漂移：" + str(path))
    _require(machine.get("status") == "BUILD_OK" and machine.get("bundle_sha256") == EXPECTED_BUNDLE_SHA256 and
             machine.get("infer_elf_sha256") == EXPECTED_NEW_APP_SHA256,
             "恢复包机器构建结果不符")
    rebuilt = comparison.get("infer", {}).get("rebuilt", {})
    original = comparison.get("infer", {}).get("original", {})
    _require(rebuilt.get("sha256") == EXPECTED_NEW_APP_SHA256 and rebuilt.get("entry") == 0x100000 and
             comparison.get("infer", {}).get("entry_equal") is True and
             comparison.get("infer", {}).get("pt_load_layout_equal") is True and
             comparison.get("infer", {}).get("all_pt_load_payload_equal_after_only_build_id_descriptor_mask") is True,
             "独审ELF比较未证明入口/PT_LOAD/限定build-id差异")
    _require(original.get("sha256") == EXPECTED_ORIGINAL_APP_SHA256, "R04原ELF身份与比较记录不符")
    app_binding = _bound(NEW_APP, EXPECTED_NEW_APP_SHA256)
    old_app_binding = _bound(EXPECTED_ORIGINAL_APP, EXPECTED_ORIGINAL_APP_SHA256)
    _require(elf_parser.parse_elf(Path(app_binding["path"]).read_bytes())["entry"] == 0x100000,
             "实际重建ELF入口不是0x100000")
    _bound(EXPECTED_ORIGINAL_INIT, EXPECTED_R04_INIT_SHA256)
    _bound(EXPECTED_R04_XSA, EXPECTED_R04_XSA_SHA256)
    _bound(EXPECTED_R04_BIT, EXPECTED_R04_BIT_SHA256)
    bundle_binding = _bound(RECOVERY / "recovery_bundle.zip", EXPECTED_BUNDLE_SHA256)
    prep, prep_raw = _read_json(EXPECTED_PREPARATION)
    _require(_sha(prep_raw) == EXPECTED_PREPARATION_SHA256, "R04正式准备计划SHA漂移")
    model.validate_plan(prep)
    _require(prep["rows"][0]["input"]["sha256"] == "da26d3850d23d6f8cb466416799358e77fbeceaa8ee27696ebf7ab365248ab9e",
             "sample000输入不是已冻结黄金输入")
    _bound(EXPECTED_BUILD_DETAILS, EXPECTED_BUILD_DETAILS_SHA256)
    source_binding = _bound(EXPECTED_APP_SOURCE, EXPECTED_SOURCE_SHA256)
    return {"scope": "OFFLINE_INPUTS_VERIFIED_ONLY_NOT_G0_OR_BOARD_ACCEPTANCE",
            "review": {"path": str(REVIEW), "sha256": EXPECTED_REVIEW_SHA256},
            "comparison": {"path": str(comparison_path), "sha256": EXPECTED_COMPARISON_SHA256},
            "machine_result": {"path": str(machine_path), "sha256": EXPECTED_MACHINE_RESULT_SHA256},
            "new_app_elf": app_binding, "original_r04_app_elf": old_app_binding,
            "original_r04_init_elf": _bound(EXPECTED_ORIGINAL_INIT, EXPECTED_R04_INIT_SHA256),
            "original_r04_xsa": _bound(EXPECTED_R04_XSA, EXPECTED_R04_XSA_SHA256),
            "original_r04_bit": _bound(EXPECTED_R04_BIT, EXPECTED_R04_BIT_SHA256),
            "recovery_bundle": bundle_binding,
            "application_source": source_binding,
            "preparation": {"path": str(EXPECTED_PREPARATION), "sha256": EXPECTED_PREPARATION_SHA256},
            "build_details": {"path": str(EXPECTED_BUILD_DETAILS), "sha256": EXPECTED_BUILD_DETAILS_SHA256},
            "review_limitations": review.get("limitations", [])}


def validate_pre_reset_snapshot(snapshot: dict) -> dict:
    """只准从完整安全IDLE/PS owner/无pending账本现场进入既有复位部署。"""
    csr.idle(snapshot)
    return {"epoch_before_system_reset": csr.epoch(snapshot), "status": snapshot[0x00C],
            "owner": "PS", "ledger": {"pending": snapshot[0x068], "issued": snapshot[0x06C],
                                        "completed": snapshot[0x070], "fault_detail": snapshot[0x074]},
            "snapshot": snapshot}


def validate_deployment_directory(controller_run: str | Path, run_id: str) -> Path:
    """controller日志必须位于唯一RunId目录内的deployment子目录。"""
    _require(type(run_id) is str and re.fullmatch(r"rebuilt_app_acceptance_[A-Za-z0-9_-]+", run_id) is not None,
             "需要新的独立T18 RunId")
    actual = transport.exact_path(controller_run, "directory")
    _require(actual.name == "deployment" and actual.parent.name == run_id,
             "controller.run必须是<T18 RunId>/deployment")
    return actual


def _save_new(path: Path, value: object) -> bytes:
    raw = (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2, default=repr) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        import os
        os.fsync(stream.fileno())
    return raw


def _evidence_bindings(run_dir: Path) -> list[dict]:
    return [{"path": path.relative_to(ROOT).as_posix(), "sha256": _sha(path.read_bytes()), "role": "result"}
            for path in sorted(run_dir.rglob("*")) if path.is_file() and path.name != "delivery_manifest.json"]


def _save_confirmed_tx_payload(wire, sequence: int, payload: bytes, path: Path) -> dict:
    """将已由串口write成功的真实TX payload原字节另存并核对写入摘要。"""
    request, header, sent_payload = wire.sent_requests[sequence]
    _require(sent_payload == payload and header == request.pack(), "真实已发送TX与绑定payload原字节不同")
    event = next((row for row in reversed(wire.events)
                  if row.get("direction") == "TX" and row.get("sequence") == sequence), None)
    _require(type(event) is dict and event.get("status") == "SENT_TO_SERIAL_DRIVER" and
             event.get("sent_bytes") == len(header) + len(payload) and
             event.get("sent_sha256") == _sha(header + payload),
             "真实serial.write长度或组合原字节摘要不符")
    with path.open("xb") as stream:
        stream.write(sent_payload)
        stream.flush()
        import os
        os.fsync(stream.fileno())
    return {"path": str(path), "bytes": len(sent_payload), "sha256": _sha(sent_payload),
            "request_header_hex": header.hex(), "serial_write": event}


def _create_sample_runner(wire, run_dir: Path, admission: dict):
    """将未创建的样本目录交给验收器，由其唯一负责创建。"""
    return model.AcceptanceRunner(wire, run_dir / "sample000", admission, capture_wire_receipts=True)


def _register_preflight_csr_map(controller, csr_map, journal) -> None:
    """仅在需要检查2B CSR或BootROM复位后部署时注册本session映射。"""
    _require(csr_map is not None, "缺少本次controller session的CSR debug map")
    helper, helper_config, helper_record, map_session, owner = csr_map
    _require(map_session is controller.session and not owner.get("attempted"),
             "CSR debug map必须是本会话新的自有注册")
    helper.register_csr_debug_map(helper_config, helper_record, journal, map_session, controller, owner)


def _preflight_entry(controller, csr_map, journal) -> dict:
    """同一XSDB会话内停核并区分BootROM/EOS0与2B安全IDLE入口。"""
    controller.verify_bindings()
    rows = controller.call("session.targets.properties.entry_preflight", controller.session.targets,
                           "--target_properties")
    selected = jtag.validate_targets(rows)
    controller.refresh_targets(selected)
    controller.record["targets"] = selected
    states_before = {label: controller.state(label) for label in ("cpu0", "cpu1")}
    pcs_before = {label: controller.pc(label) for label in ("cpu0", "cpu1")}
    evidence = {"cpu_states_before": states_before, "pc_before": pcs_before}
    controller.record["entry_preflight"] = evidence
    for label in ("cpu1", "cpu0"):
        if states_before[label] == "Running":
            if label == "cpu0":
                controller.cpu0_touched = True
            controller.call(label + ".stop.entry_preflight", controller.targets[label].stop)
    states_after = {label: controller.state(label) for label in ("cpu0", "cpu1")}
    pcs_after = {label: controller.pc(label) for label in ("cpu0", "cpu1")}
    evidence.update(cpu_states_after_stop=states_after, pc_after_stop=pcs_after)
    _require(all(state.startswith("Stopped") for state in states_after.values()),
             "入口预检受控停核后仍有运行CPU")
    controller.gate(both=True)
    boot_mode = controller.words(0xF800025C, 1)[0]
    _require(boot_mode == 0, "入口预检BOOT_MODE不是JTAG=0")
    evidence["boot_mode"] = boot_mode
    if pcs_after == BOOTROM_CPU_PCS:
        controller.observe_config_status("pre_reset_bootrom", 0)
        observation = controller.record["configuration_observations"][-1]
        fields = {row["name"]: row["value"] for row in observation["fields"]}
        _require(observation.get("status") == "PASS" and observation.get("eos") == 0 and
                 all(fields.get(name) == value for name, value in BOOTROM_UNCONFIGURED_FIELDS.items()),
                 "BootROM入口CONFIG_STATUS未证明EOS0/PL未配置")
        evidence.update(status="PRE_RESET_BOOTROM_PL_UNCONFIGURED",
                        configuration_status=observation, csr_read="NOT_READ_CSR_ABSENT")
        return {"kind": "bootrom", "csr_map_registered": False, "evidence": evidence}

    _register_preflight_csr_map(controller, csr_map, journal)
    snapshot = controller.stable_csr("rebuilt_app.before_system_reset")
    pre_reset = validate_pre_reset_snapshot(snapshot)
    evidence.update(status="PRE_RESET_SAFE_IDLE", csr=pre_reset)
    return {"kind": "2b_safe_idle", "csr_map_registered": True, "evidence": evidence}


def execute(controller, wire, *, run_id: str, source_sha256: str, cold_basis: dict,
            cache_cpu_seed: int = 0xC0DEC0DE, cache_dap_seed: int = 0xDADA1234,
            journal=None, csr_map=None) -> dict:
    """执行受限实板范围；controller/wire/session由根生产factory创建并持有。"""
    evidence = {"schema_version": 1, "scope": "REBUILT_APP_SINGLE_SAMPLE_AND_R04_DDR256B_PROBE",
                "status": "IN_PROGRESS", "hardware_execution": "BORROWED_REAL_CONTROLLER_AND_UART",
                "run_id": run_id, "new_app_identity": "REBUILT_ELF_NOT_OLD_G0_APP",
                "exit_code": 2, "steps": [], "limitations": [
                    "不重复109样本或1000连续任务。", "本次只测试DDR 256B双主机缓存一致性，不声明HP带宽/HP事务。",
                    "新ELF只接受R04限定PS恢复离线比较，不能继承旧app ELF的G0收据。",
                    "不扩大DDR器件、PCB/DDR布线或温度等级结论。"]}
    run_dir = None
    acceptance_runner = None
    try:
        _require(type(run_id) is str and re.fullmatch(r"[A-Za-z0-9_-]+", run_id) is not None,
                 "run_id格式错误")
        _require(type(source_sha256) is str and re.fullmatch(r"[0-9a-f]{64}", source_sha256) is not None,
                 "应用源码SHA格式错误")
        _require(type(controller) is jtag.JtagController and type(wire) is jtag.JtagWireSession,
                 "必须注入生产JtagController及JtagWireSession对象")
        controller.verify_bindings()
        run_dir = validate_deployment_directory(controller.run, run_id)
        evidence_root = transport.exact_path(ROOT / "report/evidence", "directory")
        run_root = transport.exact_path(run_dir.parent, "directory")
        t18_root = transport.exact_path(ROOT / "report/evidence/S2B-T18", "directory")
        _require(run_root.parent == t18_root and run_root != evidence_root and
                 evidence_root in run_root.parents,
                 "运行证据目录必须是report/evidence/S2B-T18/<RunId>")
        _require(not (run_dir / "rebuilt_app_acceptance_result.json").exists(),
                 "该deployment目录已有验收结果，拒绝覆盖")
        recovery = verify_recovery_inputs()
        _require(source_sha256 == EXPECTED_SOURCE_SHA256 and
                 recovery["application_source"]["sha256"] == source_sha256,
                 "调用方源码SHA不是实际绑定的R04应用源码")
        build, build_raw = model.read_bound({"path": str(EXPECTED_BUILD_DETAILS),
                                             "sha256": EXPECTED_BUILD_DETAILS_SHA256})
        build_details = json.loads(build_raw.decode("utf-8"))
        configured_source = build_details.get("source_sha256", {}).get("vitis/s2b_inference_app.c")
        _require(configured_source == source_sha256, "源码SHA与绑定R04 build_details不符")
        _require(controller.bindings["app_elf"] == {"path": recovery["new_app_elf"]["path"],
                                                       "sha256": EXPECTED_NEW_APP_SHA256},
                 "controller未精确绑定独立重建ELF")
        for key, path, digest in (("init_elf", EXPECTED_ORIGINAL_INIT, EXPECTED_R04_INIT_SHA256),
                                  ("xsa", EXPECTED_R04_XSA, EXPECTED_R04_XSA_SHA256),
                                  ("bit", EXPECTED_R04_BIT, EXPECTED_R04_BIT_SHA256)):
            _require(controller.bindings[key] == {"path": str(transport.exact_path(path)), "sha256": digest},
                     "部署输入不再是既有R04冻结项：" + key)
        _require(not controller.initialized and not controller.configured and not controller.app_running and
                 not controller.failed and not controller.log.closed,
                 "需要全新调用方controller对象；拒绝重复deploy或继承旧app状态")
        _require(type(wire) is jtag.JtagWireSession and not wire.failed and wire.abort_pending is None and
                 wire.epoch == 0 and wire.last_sequence == 0 and not wire.sent_requests,
                 "需要新建且未发送请求的真实UART会话")
        _require(cache_cpu_seed != cache_dap_seed and
                 all(type(item) is int and 0 <= item <= 0xFFFFFFFF for item in
                     (cache_cpu_seed, cache_dap_seed)), "cache probe种子必须不同且为32位无符号整数")
        evidence["recovery_inputs"] = recovery
        evidence["controller_bindings"] = controller.bindings
        evidence["runtime_sources"] = {str(Path(__file__)): _sha(Path(__file__).read_bytes()),
            str(Path(model.__file__)): _sha(Path(model.__file__).read_bytes()),
            str(Path(jtag.__file__)): _sha(Path(jtag.__file__).read_bytes()),
            str(Path(transport.__file__)): _sha(Path(transport.__file__).read_bytes()),
            str(Path(elf_parser.__file__)): _sha(Path(elf_parser.__file__).read_bytes())}
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, encoding="utf-8")
        _require(head.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}", head.stdout.strip()) is not None,
                 "无法绑定当前源码提交")
        evidence["source_commit"] = head.stdout.strip()

        entry = _preflight_entry(controller, csr_map, journal)
        evidence["pre_reset_entry"] = entry["evidence"]
        if entry["kind"] == "2b_safe_idle":
            evidence["pre_reset_safety"] = entry["evidence"]["csr"]
            step_name = "pre_reset_safe_idle"
        else:
            step_name = entry["evidence"]["status"]
        evidence["steps"].append({"name": step_name, "status": "PASS"})
        controller.system_reset_stop(cold_basis)
        if not entry["csr_map_registered"]:
            _register_preflight_csr_map(controller, csr_map, journal)
        controller.deploy()
        _require(controller.configured and controller.postconfigured and controller.app_running and
                 not controller.failed, "R04全bit/postconfig/重建app部署未完整成功")
        evidence["steps"].append({"name": "r04_full_volatile_deployment_with_rebuilt_elf", "status": "PASS",
                                  "configuration_observations": controller.record.get("configuration_observations"),
                                  "initialization": controller.record.get("initialization"),
                                  "ddrc_observation": controller.record.get("ddrc_observation"),
                                  "postconfiguration": controller.record.get("postconfiguration")})

        banner = wire.banner(source_sha256, EXPECTED_R04_XSA_SHA256)
        evidence["banner"] = banner
        evidence["steps"].append({"name": "real_uart_banner", "status": "PASS", "binding": banner})

        cache = controller.cache_probe(wire, cache_cpu_seed, cache_dap_seed)
        evidence["cache_probe"] = cache
        evidence["steps"].append({"name": "actual_cpu_dap_cache_coherence_256_bytes", "status": "PASS",
                                  "result": cache})
        prep, prep_raw = _read_json(EXPECTED_PREPARATION)
        _require(_sha(prep_raw) == EXPECTED_PREPARATION_SHA256, "运行前R04样本准备文件SHA漂移")
        model.validate_plan(prep)
        weight_path, weight_payload = model.read_bound(prep["weights"])
        _require(wire.epoch == 0 and wire.last_sequence == 2 and wire.abort_pending is None,
                 "真实cache probe之后须保持冷epoch0/seq2才能加载权重")
        weight_request, weight_header = transport.make_request(
            transport.OP_WEIGHTS, wire.last_sequence + 1, 0, weight_payload)
        admission = {"scope": evidence["scope"], "status": "INDEPENDENT_REBUILT_APP_SCOPE",
                     "new_app_elf": recovery["new_app_elf"], "old_g0_receipt": "NOT_REUSED",
                     "offline_recovery_review": recovery["review"], "source_commit": evidence["source_commit"]}
        acceptance_runner = _create_sample_runner(wire, run_dir, admission)
        sample_dir = acceptance_runner.run
        acceptance_runner.record["hardware_execution"] = "BORROWED_REAL_JTAG_UART_SESSION"
        acceptance_runner.record["app_elf"] = recovery["new_app_elf"]
        _require(weight_request.sequence == 3 and weight_request.op == transport.OP_WEIGHTS and
                 weight_request.frame == 0,
                 "weights请求不是cache后的真实seq3权重")
        acceptance_runner.send(weight_request, weight_header, weight_payload, prep["weights"])
        weight_meta = acceptance_runner.receive(weight_request, 0, phase="weights")
        _require(weight_meta["epoch"] == 0 and wire.epoch == 0 and wire.last_sequence == 3,
                 "seq3真实weights响应没有保持冷epoch0")
        evidence["weights"] = {"path": str(weight_path), "bytes": len(weight_payload),
                               "sha256": _sha(weight_payload), "request_sequence": weight_request.sequence,
                               "response": weight_meta, "result": "PASS_REAL_OP_WEIGHTS"}
        evidence["weights"]["actual_tx"] = _save_confirmed_tx_payload(
            wire, 3, weight_payload, run_dir / "weights_tx_payload_raw.bin")
        evidence["steps"].append({"name": "actual_bound_weights_op1_sequence3", "status": "PASS"})
        acceptance_runner.run_input(prep["rows"][0], wire.last_sequence + 1, 0, 1,
                                    0xFFFFFFFF, 0xFFFFFFFF, "rebuilt_app_sample000")
        sample_result = acceptance_runner.finish("PASS_REBUILT_APP_SAMPLE000_GOLDEN")
        _require(sample_result["status"] == "PASS_REBUILT_APP_SAMPLE000_GOLDEN" and
                 len(sample_result["frames"]) == 1 and sample_result["frames"][0]["epoch"] == 1 and
                 wire.epoch == 1 and wire.last_sequence == 4,
                 "重建app sample000协议/黄金或动态epoch结果不符")
        _, _, sample_payload = wire.sent_requests[4]
        evidence["sample000"] = {"status": sample_result["status"],
                                 "result_path": str(sample_dir / "acceptance_result.json"),
                                 "result_sha256": _sha((sample_dir / "acceptance_result.json").read_bytes()),
                                 "frame": sample_result["frames"][0], "uart_epoch": wire.epoch,
                                 "uart_sequence": wire.last_sequence,
                                 "golden_check": "PASS_HEADS_AND_ALL_BOXES"}
        evidence["sample000"]["actual_tx"] = _save_confirmed_tx_payload(
            wire, 4, sample_payload, sample_dir / "sample000_tx_payload_raw.bin")
        evidence["steps"].append({"name": "sample000_goldens_and_uart_completion", "status": "PASS"})

        controller.gate(both=False)
        if not controller.state("cpu0").startswith("Stopped"):
            controller.call("rebuilt_app.cpu0.stop_after_sample", controller.targets["cpu0"].stop)
        controller.gate(both=True)
        final_snapshot = controller.stable_csr("rebuilt_app.after_sample_ack")
        csr.idle(final_snapshot)
        _require(csr.epoch(final_snapshot) == wire.epoch == 1 and final_snapshot[0x068] == 0 and
                 final_snapshot[0x06C] == 0 and final_snapshot[0x070] == 0 and final_snapshot[0x074] == 0,
                 "sample000结束后不是epoch1/安全IDLE/ledger0")
        evidence["final_snapshot"] = final_snapshot
        evidence["steps"].append({"name": "cpu_stopped_after_dynamic_ack_idle_epoch1", "status": "PASS"})
        evidence.update(status="PASS_REBUILT_APP_SINGLE_SAMPLE_AND_DDR256B_PROBE", exit_code=0)
    except BaseException as error:
        evidence.update(status="FAILED_REBUILT_APP_ACCEPTANCE", exit_code=2,
                        error=repr(error), traceback=traceback.format_exc())
        if acceptance_runner is not None and not acceptance_runner.log.closed:
            try:
                acceptance_runner.finish("FAILED_REBUILT_APP_ACCEPTANCE", error)
            except BaseException as save_error:
                evidence["acceptance_result_save_error"] = repr(save_error)
        if controller is not None and hasattr(controller, "failed") and not controller.failed:
            controller.failed = True
            try:
                controller.fail_stop()
            except BaseException as stop_error:
                evidence["bounded_fail_stop_error"] = repr(stop_error)
    if run_dir is not None:
        evidence["outputs"] = _evidence_bindings(run_dir)
        evidence["tool_versions"] = {"python": sys.version.split()[0]}
        evidence["limitations"].append("result仅覆盖本次真实执行状态；不声明109/1000、HP或正式G0/G4/G5通过。")
        _save_new(run_dir / "rebuilt_app_acceptance_result.json", evidence)
    return evidence

