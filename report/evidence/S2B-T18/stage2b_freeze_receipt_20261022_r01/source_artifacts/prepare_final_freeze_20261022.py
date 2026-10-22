"""生成阶段2B最终候选冻结包；只读核验来源并创建新的证据目录。"""
from __future__ import annotations

import hashlib
import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "stage2b_freeze_20261022_r02"
RUN_DIR = ROOT / "report/evidence/S2B-T18" / RUN_ID
PS_RUN = ROOT / "report/evidence/S2B-T18/rebuilt_app_acceptance_20261022_r02"
R12_RUN = ROOT / "report/evidence/S2B-T18/csr_r12_finalize_replay_20261022_r05"
R12_REPLAY = ROOT / "tmp/2B/S2B-T18/csr_r12_finalize_replay_20261022_r05/replay_result.json"
ACK_OBSERVER = ROOT / "report/evidence/S2B-T18/rebuilt_app_ack_observation_20261022_r01/observer_result.json"
MODEL_RUN = ROOT / "report/evidence/S2B-T18/formal_stress1000_then109_20261018_r02"
MODEL_REVIEW = ROOT / "report/evidence/S2B-T18/formal_model_result_review_20261019_r01"
EXPECTED_REBUILT_ELF_SHA256 = "f7a8bc96418590a497577bb45a7cbc0cc75dec416f6af1bf9b33ffd0308fa5a9"
EXPECTED_R04_BIT_SHA256 = "555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7"
EXPECTED_R04_XSA_SHA256 = "ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6"
EXPECTED_CSR_SHA256 = "4beaad995d31835799a20138ed027125fbb4920795d64e471c6174ced12169d1"
EXPECTED_RECOVERY_ZIP_SHA256 = "50b5eb62968795413e03f4474dd98800c8e2c1f0ead04003ae53b47b83ea9436"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    require(path.is_file(), f"缺少必需JSON：{path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON顶层不是对象：{path}")
    return value


def bound(path_value: str, expected_sha256: str | None = None,
          role: str = "input", note: str = "") -> dict:
    path = Path(path_value)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    require(path.is_file(), f"绑定文件不存在：{path}")
    actual = sha256(path)
    if expected_sha256 is not None:
        require(actual == expected_sha256.lower(),
                f"SHA256漂移：{path} expected={expected_sha256} actual={actual}")
    item = {"path": rel(path), "sha256": actual, "role": role}
    if note:
        item["note"] = note
    return item


def write_new(path: Path, content: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(content)
        stream.flush()
        import os
        os.fsync(stream.fileno())


def write_json(path: Path, value: object) -> None:
    data = (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")
    write_new(path, data)


def freeze_inputs(host_review_path: Path) -> tuple[str, dict, dict, dict, dict, dict, list[dict], list[dict], list[dict]]:
    """验证关键运行结果后，构造候选输入、源码与正式接口绑定。"""
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                          text=True, encoding="utf-8", check=True).stdout.strip()
    require(len(head) == 40 and all(char in "0123456789abcdef" for char in head),
            "当前HEAD不是完整Git SHA")

    ps_orchestrator = read_json(PS_RUN / "orchestrator_result.json")
    ps_acceptance = ps_orchestrator.get("acceptance")
    ps_sample = read_json(PS_RUN / "deployment/sample000/acceptance_result.json")
    require(ps_orchestrator.get("run_id") == "rebuilt_app_acceptance_20261022_r02",
            "PS r02 orchestrator RunId不匹配")
    require(ps_orchestrator.get("status") == "FAILED_CLEANUP" and
            ps_orchestrator.get("native_exit_code") == 2 and
            isinstance(ps_orchestrator.get("cleanup_errors"), list) and ps_orchestrator["cleanup_errors"],
            "PS r02失败状态与已保存的FAILED_CLEANUP事实不符")
    require(isinstance(ps_acceptance, dict) and
            ps_acceptance.get("status") == "FAILED_REBUILT_APP_ACCEPTANCE" and
            ps_acceptance.get("exit_code") == 2 and
            "len(sample_result[\"frames\"]) == 1" in ps_acceptance.get("traceback", ""),
            "PS r02内层失败边界不是已知的双帧数量断言")
    require(ps_acceptance.get("source_commit") == ps_orchestrator.get("source_commit") and
            isinstance(ps_orchestrator.get("source_commit"), str) and len(ps_orchestrator["source_commit"]) == 40,
            "PS r02原始源码提交绑定不一致")
    observed_steps = {row.get("name") for row in ps_acceptance.get("steps", [])
                      if isinstance(row, dict) and row.get("status") == "PASS"}
    require({"PRE_RESET_BOOTROM_PL_UNCONFIGURED", "r04_full_volatile_deployment_with_rebuilt_elf",
             "real_uart_banner", "actual_cpu_dap_cache_coherence_256_bytes",
             "actual_bound_weights_op1_sequence3"}
            <= observed_steps, "PS r02缺少一个或多个真实部署、cache、weights、golden、ACK步骤")
    pre_reset_status = ps_acceptance.get("pre_reset_entry", {}).get("status")
    require(pre_reset_status in {"PRE_RESET_SAFE_IDLE", "PRE_RESET_BOOTROM_PL_UNCONFIGURED"},
            "PS r02未保存受控入口预检结论")
    expected_entry_step = ("pre_reset_safe_idle" if pre_reset_status == "PRE_RESET_SAFE_IDLE"
                           else "PRE_RESET_BOOTROM_PL_UNCONFIGURED")
    require(expected_entry_step in observed_steps, "PS r02入口步骤状态与预检证据不一致")
    recovery = ps_acceptance.get("recovery_inputs", {})
    require(recovery.get("new_app_elf", {}).get("sha256") == EXPECTED_REBUILT_ELF_SHA256,
            "PS r02没有绑定冻结重建ELF")
    require(recovery.get("original_r04_bit", {}).get("sha256") == EXPECTED_R04_BIT_SHA256 and
            recovery.get("original_r04_xsa", {}).get("sha256") == EXPECTED_R04_XSA_SHA256,
            "PS r02的R04 bit/XSA绑定不符")
    require(ps_sample.get("status") == "PASS_REBUILT_APP_SAMPLE000_GOLDEN" and
            ps_sample.get("final_epoch") == 1 and ps_sample.get("final_sequence") == 4 and
            [(row.get("phase"), row.get("sequence"), row.get("epoch"))
             for row in ps_sample.get("frames", [])] ==
            [("weights", 3, 0), ("rebuilt_app_sample000", 4, 1)] and
            ps_sample.get("app_elf", {}).get("sha256") == EXPECTED_REBUILT_ELF_SHA256 and
            ps_sample.get("admission", {}).get("source_commit") == ps_orchestrator.get("source_commit"),
            "PS r02黄金样本或weights/模型双帧身份不符")

    ps_sample_path = PS_RUN / "deployment/sample000/acceptance_result.json"
    observer = read_json(ACK_OBSERVER)
    require(observer.get("run_id") == "rebuilt_app_ack_observation_20261022_r01" and
            observer.get("scope") == "POST_R02_READ_ONLY_ACK_IDLE_OBSERVATION" and
            observer.get("status") == "PASS_POST_R02_ACK_IDLE_EPOCH1_LEDGER0" and
            observer.get("exit_code") == 0 and observer.get("cleanup_errors") == [] and
            observer.get("parent_run_unchanged") is True and
            observer.get("new_model_requests") == 0 and observer.get("writes_to_csr") == 0,
            "PS r02之后的只读ACK/IDLE补证未完整PASS")
    observer_bindings = observer.get("bindings")
    require(isinstance(observer_bindings, list), "ACK观察缺少原运行bindings")
    for observed_path in (PS_RUN / "orchestrator_result.json", ps_sample_path):
        matches = [row for row in observer_bindings if isinstance(row, dict) and
                   Path(row.get("path", "")).resolve() == observed_path.resolve()]
        require(len(matches) == 1 and matches[0].get("sha256") == sha256(observed_path),
                f"ACK观察未绑定原r02字节：{observed_path}")

    r12_orchestrator = read_json(R12_RUN / "orchestrator_result.json")
    require(r12_orchestrator.get("run_id") == "csr_r12_finalize_replay_20261022_r05" and
            r12_orchestrator.get("status") == "PASS_CSR_DEADLINE_SCOPE_ONLY" and
            r12_orchestrator.get("native_exit_code") == 0,
            "权威R12 r05隔离封装重放未PASS，拒绝候选")
    r12_replay = read_json(R12_REPLAY)
    r12_manifest_path = R12_RUN / "delivery_manifest.json"
    require(r12_replay.get("clone_run_id") == "csr_r12_finalize_replay_20261022_r05" and
            r12_replay.get("hardware_access") == "NONE" and
            r12_replay.get("original_r12_mutated") is False and
            r12_replay.get("copied_acceptance_scope") == "PASS_CSR_DEADLINE_SCOPE_ONLY" and
            r12_replay.get("manifest_sha256") == sha256(r12_manifest_path),
            "R12 r05真实隔离封装重放回执或manifest绑定不符")
    r12_finalizer = r12_replay.get("finalizer_result")
    require(isinstance(r12_finalizer, dict) and r12_finalizer.get("status") == "CHECKS_OK" and
            r12_finalizer.get("mode") == "evidence" and
            r12_finalizer.get("task_id") == "S2B-T18" and
            r12_finalizer.get("run_id") == "csr_r12_finalize_replay_20261022_r05" and
            r12_finalizer.get("errors") == [], "R12 r05最终封装器身份或CHECKS_OK结果不符")
    r12_csr_checks = r12_finalizer.get("check_statuses")
    require(isinstance(r12_csr_checks, list) and
            any(isinstance(row, dict) and row.get("name") == "CSR恢复固定顺序" and
                row.get("status") == "PASS" for row in r12_csr_checks),
            "R12 r05 finalizer未记录CSR恢复固定顺序PASS")

    model_review = read_json(MODEL_REVIEW / "review_outcome.json")
    model_scope = read_json(MODEL_REVIEW / "scope_analysis.json")
    numeric_scope = model_scope["b_stage2b_numeric_minima"]
    golden_scope = numeric_scope["golden_sample_minimum"]
    stress_scope = numeric_scope["continuous_task_minimum"]
    require(numeric_scope.get("status") == "MET" and golden_scope.get("selected_sample_count") == 108 and
            golden_scope.get("all_selected_head_bytes_and_boxes_matched") is True and
            stress_scope.get("R02_completed") == 1000 and stress_scope.get("all_stress_tasks_ack_closed") is True,
            "模型独审的108+1000计数条件不再满足")
    r08_result = read_json(ROOT / "report/evidence/S2B-T18/formal_csr_recovery_20261019_r08/orchestrator_result.json")
    r08_abort = read_json(ROOT / "report/evidence/S2B-T20/formal_csr_recovery_20261019_r08_csr_abort_recovery/csr_result.json")
    require(model_review.get("review_outcome") == "CHANGES_REQUIRED" and
            model_review.get("data_replay_outcome") == "PASS",
            "模型原独审状态发生漂移；生成器需人工更新后再用")
    require(model_scope.get("parent_review_outcome") == "CHANGES_REQUIRED",
            "108/1000计数补充的模型独审父结论不符")

    review_dir = ROOT / "report/evidence/S2B-T20"
    t15 = ROOT / "report/evidence/S2B-T15"
    t19 = ROOT / "report/evidence/S2B-T19"
    t04 = ROOT / "report/evidence/S2B-T04"
    file_specs = [
        (MODEL_REVIEW / "review_outcome.json", "input", "模型数据重放PASS；整体原独审CHANGES_REQUIRED"),
        (MODEL_REVIEW / "scope_analysis.json", "input", "独审补充：108个闭环黄金与1000次连续任务达到数量门槛"),
        (MODEL_REVIEW / "replay_r02_final_result.json", "input", "独立模型重放摘要"),
        (MODEL_RUN / "delivery_manifest.json", "input", "绑定原模型RunId；不扫描原始9103个条目"),
        (ROOT / "report/evidence/S2B-T18/formal_model_evidence_audit_20261019_r01/audit_report.md",
         "input", "历史源码漂移与原始证据审计摘要"),
        (ROOT / "report/evidence/S2B-T18/formal_csr_recovery_20261019_r08/orchestrator_result.json",
         "input", "R08顶层状态原样保留"),
        (ROOT / "report/evidence/S2B-T18/formal_csr_recovery_20261019_r08/acceptance_result.json",
         "input", "R08原始完整结果，含局部状态与未闭合项"),
        (PS_RUN / "orchestrator_result.json", "input", "PS r02整体FAILED_CLEANUP原始wrapper结果；保留原清理失败"),
        (PS_RUN / "input_config.json", "input", "PS r02实际调用输入与绑定配置"),
        (ps_sample_path, "input", "PS r02真实黄金sample000结果，含seq3 weights与seq4模型双帧"),
        (ACK_OBSERVER, "input", "r02后只读ACK/epoch1/ledger0补证；不发请求、不写CSR"),
        (ROOT / "report/evidence/S2B-T20/formal_csr_recovery_20261019_r08_csr_abort_recovery/csr_result.json",
         "input", "R08 pending ABORT有限子范围"),
        (ROOT / "report/evidence/S2B-T20/formal_csr_recovery_20261019_r08_csr_abort_recovery/golden_sample000/acceptance_result.json",
         "input", "R08恢复后黄金样本子结果"),
        (R12_RUN / "orchestrator_result.json", "input", "R12 r05隔离封装重放的orchestrator结果"),
        (R12_RUN / "acceptance_result.json", "input", "R12 r05隔离封装重放的CSR限定范围结果"),
        (R12_RUN / "delivery_manifest.json", "input", "R12 r05隔离封装重放的封包与源码输入绑定"),
        (R12_REPLAY, "input", "R12 r05真实finalize_evidence隔离重放回执与manifest SHA绑定"),
        (R12_RUN / "deadline_scope/acceptance_result.json", "input", "R12 r05 deadline子范围"),
        (R12_RUN / "before_static_matrix_scene.json", "input", "R12静止拒绝场景原始配置"),
        (R12_RUN / "before_static_matrix_config.json", "input", "R12静止拒绝场景CSR快照配置"),
        (ROOT / "report/evidence/S2B-T20/bresp_composition_review_20261021_r01/analysis.md",
         "input", "条件性BRESP组合论证；SDK UNKNOWN原状态不改写"),
        (ROOT / "report/evidence/S2B-T20/cpu_bresp_gp0_postmortem_independent_review_20261019_r01/review_outcome.json",
         "input", "同地址原生代表事务的独立分类；不是逐笔SDK读数"),
        (ROOT / "report/evidence/S2B-T20/deadline_done_fix_review_20261021_r01/review.md",
         "input", "deadline代码范围G2回执"),
        (ROOT / "report/evidence/S2B-T20/csr_static_bresp_review_20261019_r03/review_outcome.json",
         "input", "静止BRESP实现审查回执及遗留阻断"),
        (t04 / "board_material_mapping_20261022_r01/manifest.json", "input", "板卡材料来源PDF及映射运行清单"),
        (t04 / "board_material_mapping_20261022_r01/status.json", "input", "材料映射处理状态"),
        (t04 / "board_material_mapping_20261022_r01/document.md", "input", "已选原理图页OCR/解析文本"),
        (ROOT / "report/evidence/S2B-T20/rebuilt_app_scope_review_20261021_r01/review_final.md",
         "input", "重建ELF acceptance scope G2回执"),
        (ROOT / "report/evidence/S2B-T20/rebuilt_app_directory_review_20261022_r01/review_outcome.md",
         "input", "真实AcceptanceRunner目录修复G2回执"),
        (ROOT / "report/evidence/S2B-T20/final_host_restore_review_20261022_r01/review_rebuilt_single_session_r01.md",
         "input", "同会话BootROM/安全IDLE入口G2与14项回归回执"),
        (host_review_path, "input", "双帧选择及r02后ACK观察独立G2回执；路径由调用方显式提供"),
        (ROOT / "report/evidence/S2B-T15/recovery_inputs_20261019_r02/comparison.json",
         "input", "重建ELF与恢复包离线比较"),
        (ROOT / "report/evidence/S2B-T15/recovery_inputs_20261019_r02/machine_result.json",
         "input", "恢复包ELF解析/构建机器结果"),
        (ROOT / "report/evidence/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04_artifacts/build_details.json",
         "input", "R04 build/XSA/bit构建身份"),
        (ROOT / "report/evidence/S2B-T19/cache_probe_execution_20261017_r02/visibility_probe_result.json",
         "input", "较早R02平台有限256B DDR前置观察原始结果"),
        (ROOT / "report/evidence/S2B-T20/ddr_prior_probe_review_20261021_r01/review.md",
         "input", "DDR前置探针独审；仅限CPU-DAP 256B与两相"),
        (t19 / "visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.xsa", "artifact", "R04恢复依赖；需随包保留"),
        (t19 / "visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit", "artifact", "R04恢复依赖；需随包保留"),
        (t15 / "recovery_inputs_20261019_r02/recovery_bundle.zip", "artifact", "本地恢复包依赖；不保证随Git提交"),
        (ROOT / "tmp/2B/S2B-T15/recovery_inputs_20261019_r02/attempt_03/fresh_build/infer/infer.elf",
         "artifact", "重建PS ELF本地构建依赖；需归档"),
        (ROOT / "tmp/2B/S2B-T15/recovery_inputs_20261019_r02/attempt_03/fresh_build/init/init.elf",
         "artifact", "R04 init ELF本地重建依赖；需归档"),
        (ROOT / "src/s2b_control_csr.sv", "source", "冻结R04 CSR RTL"),
        (ROOT / "vitis/s2b_inference_app.c", "source", "重建PS应用源码"),
        (ROOT / "verification/s2b_rebuilt_app_acceptance.py", "source", "最终实板runner及BootROM入口逻辑"),
        (ROOT / "verification/test_s2b_rebuilt_app_acceptance.py", "source", "入口与验收离线回归"),
        (ROOT / "vitis/run_s2b_rebuilt_app_acceptance.py", "source", "生产wrapper；原样绑定"),
        (ROOT / "verification/check_stage_delivery.py", "source", "输入/证据manifest只读检查器"),
        (Path(__file__), "source", "最终冻结候选生成器；供恢复与审计"),
        (ROOT / "docs/obsidian-project/02-方案设计/B方案实施与阶段验收计划.md", "input", "正式2B阶段验收要求"),
        (ROOT / "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md", "source", "接口版本s2b-physical/1.0.0"),
        (ROOT / "docs/obsidian-project/02-方案设计/s2b_board_transport.md", "source", "接口版本s2bu/1.1"),
        (ROOT / "docs/obsidian-project/04-提交材料/阶段验收/stage2b_fixed_input_acceptance_20261022.md",
         "input", "固定输入验收候选；文档状态仍为待审，不能独立判G4/G5"),
    ]
    inputs = [bound(str(path), role=role, note=note) for path, role, note in file_specs]

    # 将PS r02本次运行的全部实际输出逐项绑定，不扫描历史模型原始目录。
    ps_outputs = ps_orchestrator.get("raw_logs")
    require(isinstance(ps_outputs, list) and ps_outputs, "PS r02未提供raw_logs输出清单")
    known = {item["path"] for item in inputs}
    for row in ps_outputs:
        require(isinstance(row, dict) and isinstance(row.get("path"), str), "PS r02输出项格式错误")
        item = bound(str(ROOT / row["path"]), row.get("sha256"), "input",
                     "PS r02真实执行原始输出")
        if item["path"] not in known:
            inputs.append(item)
            known.add(item["path"])

    # 从实际源文件绑定关键预期SHA，避免把路径正确误当内容一致。
    for path, expected in (
        (ROOT / "src/s2b_control_csr.sv", EXPECTED_CSR_SHA256),
        (ROOT / "tmp/2B/S2B-T15/recovery_inputs_20261019_r02/attempt_03/fresh_build/infer/infer.elf",
         EXPECTED_REBUILT_ELF_SHA256),
        (t19 / "visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit", EXPECTED_R04_BIT_SHA256),
        (t19 / "visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.xsa", EXPECTED_R04_XSA_SHA256),
        (t15 / "recovery_inputs_20261019_r02/recovery_bundle.zip", EXPECTED_RECOVERY_ZIP_SHA256),
    ):
        bound(str(path), expected)

    interfaces = [
        bound(str(ROOT / "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"),
              role="source", note="正式物理接口正文版本s2b-physical/1.0.0"),
        bound(str(ROOT / "docs/obsidian-project/02-方案设计/s2b_board_transport.md"),
              role="source", note="正式传输接口正文版本s2bu/1.1"),
    ]
    for item, name, version in zip(interfaces, ("physical", "uart"),
                                   ("s2b-physical/1.0.0", "s2bu/1.1")):
        item.pop("role", None)
        item.pop("note", None)
        item.update(name=name, version=version, frozen=True)

    external_dependencies = [
        {"dependency": "official_arm_gcc_13_4_0", "status": "external_toolchain_required",
         "path_from_machine_result": "D:\\Xilinx\\2026.1\\Vitis\\gnu\\aarch32\\nt\\gcc-arm-none-eabi\\bin\\arm-none-eabi-gcc.exe",
         "source_record": "report/evidence/S2B-T15/recovery_inputs_20261019_r02/machine_result.json"},
        {"dependency": "prebuilt_bsp_and_sdk_libraries", "status": "external_recovery_dependency",
         "source_record": "report/evidence/S2B-T15/recovery_inputs_20261019_r02/recovery_bundle.zip",
         "note": "不声称BSP源码全量重建。"},
        {"dependency": "R04_XSA_bit_recovery_zip_init_ELF_model_UART_corpus",
         "status": "preserve_outside_source_only_git_restore",
         "note": "大文件及历史运行源件须随独立恢复归档保留，不可按临时文件删除。"},
    ]
    return head, ps_orchestrator, ps_acceptance, ps_sample, observer, r12_replay, inputs, interfaces, external_dependencies


def main(host_review_path: Path) -> int:
    require(not RUN_DIR.exists(), f"RunId已存在，拒绝覆盖：{RUN_DIR}")
    head, ps_orchestrator, ps_acceptance, ps_sample, observer, r12_replay, inputs, interfaces, external_dependencies = freeze_inputs(host_review_path)
    r12_orchestrator = read_json(R12_RUN / "orchestrator_result.json")
    model_review = read_json(MODEL_REVIEW / "review_outcome.json")
    model_scope = read_json(MODEL_REVIEW / "scope_analysis.json")
    numeric_scope = model_scope["b_stage2b_numeric_minima"]
    golden_scope = numeric_scope["golden_sample_minimum"]
    stress_scope = numeric_scope["continuous_task_minimum"]
    r08_result = read_json(ROOT / "report/evidence/S2B-T18/formal_csr_recovery_20261019_r08/orchestrator_result.json")
    r08_abort = read_json(ROOT / "report/evidence/S2B-T20/formal_csr_recovery_20261019_r08_csr_abort_recovery/csr_result.json")
    material = read_json(ROOT / "report/evidence/S2B-T04/board_material_mapping_20261022_r01/status.json")
    candidate_doc = ROOT / "docs/obsidian-project/04-提交材料/阶段验收/stage2b_fixed_input_acceptance_20261022.md"
    host_review_binding = next(item for item in inputs if item["path"] == rel(host_review_path.resolve()))

    inventory = {
        "schema_version": 1,
        "status": "CANDIDATE_FINAL_FREEZE_INPUTS_BOUND_NOT_G4_G5_ACCEPTANCE",
        "run_id": RUN_ID,
        "created_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "source_commit": head,
        "scope_document": bound(str(candidate_doc), role="input",
                                 note="候选文档原状态保留；最终独审后才可判定阶段结论"),
        "evidence_summary": [
            {"scope": "model_108_golden_and_1000_stress", "overall_independent_review": model_review["review_outcome"],
             "data_replay": model_review["data_replay_outcome"],
             "selected_ack_closed_golden_count": golden_scope["selected_sample_count"],
             "continuous_stress_count": stress_scope["R02_completed"], "source": rel(MODEL_REVIEW / "scope_analysis.json"),
             "limitation": "R02整体独审CHANGES_REQUIRED的最后109项动态ACK缺口仍保留；仅按补充分析计108项闭环及1000连续数量门槛。"},
            {"scope": "R08_pending_abort_and_golden_recovery", "top_level_status": r08_result.get("status"),
             "abort_subscope_status": r08_abort.get("status"),
             "source": "formal_csr_recovery_20261019_r08/orchestrator_result.json",
             "limitation": "R08整流程状态不被局部pending ABORT与恢复子范围替代。"},
            {"scope": "R12_static_matrix_and_deadline", "run_id": r12_orchestrator["run_id"],
             "status": r12_orchestrator["status"], "replay_receipt": rel(R12_REPLAY),
             "replay_sha256": sha256(R12_REPLAY), "evidence": rel(R12_RUN / "delivery_manifest.json"),
             "execution_mode": "ISOLATED_PACKAGE_REPLAY_NOT_A_NEW_BOARD_RUN",
             "limitation": "仅计R12 r05隔离封装重放中声明的限定范围；历史封装恢复r01不作为当前源码绑定。"},
            {"scope": "rebuilt_ps_r02_real_sample_and_cache", "run_id": ps_orchestrator["run_id"],
             "status": ps_orchestrator["status"], "acceptance_status": ps_acceptance["status"],
             "native_exit_code": ps_orchestrator["native_exit_code"],
             "cleanup_errors": ps_orchestrator["cleanup_errors"],
             "acceptance_exit_code": ps_acceptance["exit_code"],
             "failure_boundary": "historical_len(sample_result.frames)==1 assertion after golden result; retained as FAILED",
             "executed_source_commit": ps_orchestrator["source_commit"],
             "current_source_commit": head,
             "sample_status": ps_sample["status"],
             "sample_frames": [{"phase": row["phase"], "sequence": row["sequence"], "epoch": row["epoch"]}
                               for row in ps_sample["frames"]],
             "new_app_elf": ps_acceptance["recovery_inputs"]["new_app_elf"],
             "r04_bit_sha256": EXPECTED_R04_BIT_SHA256, "r04_xsa_sha256": EXPECTED_R04_XSA_SHA256,
             "post_run_ack_observation": {"status": observer["status"], "run_id": observer["run_id"],
                                          "exit_code": observer["exit_code"],
                                          "parent_run_unchanged": observer["parent_run_unchanged"],
                                          "new_model_requests": observer["new_model_requests"],
                                          "writes_to_csr": observer["writes_to_csr"],
                                          "cleanup_errors": observer["cleanup_errors"]},
             "two_frame_review": host_review_binding,
             "limitation": "保留r02整体FAILED_CLEANUP及内层FAILED；只记录部署/cache/weights步骤PASS、黄金sample000结果PASS和后续只读ACK补证。该范围不替代108/1000模型计数，也不声明HP、BSP或全平台重建。"},
            {"scope": "board_material_mapping", "status": material.get("state"),
             "source": "S2B-T04/board_material_mapping_20261022_r01/manifest.json",
             "limitation": "原理图/手册映射不是PCB修订、实装料号或电压实测鉴定。"},
            {"scope": "bresp_composition", "status": "CONDITIONAL_IMPLEMENTATION_INFERENCE",
             "sdk_observed_bresp": "UNKNOWN_RETAINED", "source": "S2B-T20/bresp_composition_review_20261021_r01/analysis.md",
             "limitation": "公共RTL路径与同地址代表事务的组合推论，不写成逐笔SDK直接观测。"},
            {"scope": "independent_code_reviews", "status": "G2_REVIEW_RECORDS_BOUND_VERDICTS_NOT_SYNTHESIZED",
             "sources": ["S2B-T20/rebuilt_app_scope_review_20261021_r01/review_final.md",
                         "S2B-T20/rebuilt_app_directory_review_20261022_r01/review_outcome.md",
                         "S2B-T20/final_host_restore_review_20261022_r01/review_rebuilt_single_session_r01.md",
                         rel(host_review_path.resolve())],
             "limitation": "G2代码审查不等同实板或G4/G5通过。"},
        ],
        "bindings": inputs,
        "external_dependencies": external_dependencies,
        "limitations": [
            "该包为最终冻结候选输入清单；候选文档仍待正式G4/G5判断。",
            "不把任何历史FAILED、CHANGES_REQUIRED、UNKNOWN或BLOCKED记录改写为PASS。",
            "PS r02整体FAILED_CLEANUP、内层FAILED_REBUILT_APP_ACCEPTANCE原样保留；PASS仅指明确记录的部署/cache/weights步骤、黄金sample000结果与后续只读ACK观察。",
            "PS r02执行源码提交与本次生成清单的source_commit分别绑定；本次代码修复由独立双帧G2回执绑定，不追写为旧实板运行代码。",
            "超大原始模型UART/Corpus文件不在本生成器中遍历；由原RunId delivery_manifest及独审回执绑定。",
            "外部工具链、BSP与本地恢复二进制不是源代码Git恢复的一部分，必须随独立恢复归档保全。",
            "接口版本及文档SHA由最终清单固定；候选文档中的技术范围限制继续适用。",
        ],
    }

    input_manifest = {
        "schema_version": 1, "stage": "2B", "task_id": "S2B-T18", "run_id": RUN_ID,
        "source_commit": head, "evidence_dir": rel(RUN_DIR), "interfaces": interfaces,
        "files": [{key: item[key] for key in ("path", "sha256", "role")} for item in inputs],
        "checks": [{"name": "来源文件哈希与组合证据完整性门禁", "status": "PASS",
                    "command": f"python -B tmp/2B/prepare_final_freeze_20261022.py --host-review {rel(host_review_path.resolve())}",
                    "exit_code": 0, "reason": "生成器仅在显式G2回执、PS r02失败原件与黄金结果、后续只读ACK补证及其他冻结输入均绑定后完成；不把PS r02整体失败改写为通过。"}],
        "limitations": ["inputs模式只验证声明输入和正式接口绑定，不表示G4/G5验收。"],
    }

    RUN_DIR.mkdir()
    # 把仅存在于tmp的重建PS ELF复制到新RunId，确保冻结包有稳定恢复副本。
    rebuilt_source = ROOT / "tmp/2B/S2B-T15/recovery_inputs_20261019_r02/attempt_03/fresh_build/infer/infer.elf"
    artifact_dir = RUN_DIR / "artifacts"
    artifact_dir.mkdir()
    rebuilt_copy = artifact_dir / "rebuilt_infer.elf"
    with rebuilt_source.open("rb") as source_stream, rebuilt_copy.open("xb") as target_stream:
        shutil.copyfileobj(source_stream, target_stream, 1024 * 1024)
        target_stream.flush()
        import os
        os.fsync(target_stream.fileno())
    rebuilt_copy_binding = bound(str(rebuilt_copy), EXPECTED_REBUILT_ELF_SHA256,
                                 "artifact", "重建PS ELF持久副本；字节复制非重编译")
    inventory["bindings"].append(rebuilt_copy_binding)
    inventory["recovery_artifacts"] = [
        {"original_tmp_binding": rel(rebuilt_source), "persistent_copy": rebuilt_copy_binding,
         "sha256_equal": True, "copy_method": "byte_copy_no_rebuild"}
    ]
    input_manifest["files"].append({key: rebuilt_copy_binding[key]
                                    for key in ("path", "sha256", "role")})
    inventory_path = RUN_DIR / "final_freeze_inventory.json"
    input_manifest_path = RUN_DIR / "inputs_manifest.json"
    readme_path = RUN_DIR / "README.md"
    write_json(inventory_path, inventory)
    write_json(input_manifest_path, input_manifest)
    readme = (
        "# 阶段2B最终冻结候选\n\n"
        f"RunId：`{RUN_ID}`  \n来源提交：`{head}`  \n"
        "状态：**候选输入已绑定；不代表G4/G5通过。**\n\n"
        "## 文件\n\n"
        "- `final_freeze_inventory.json`：范围、状态、SHA绑定与恢复依赖摘要。\n"
        "- `inputs_manifest.json`：适配 `check_stage_delivery.py --mode inputs`。\n"
        "- `delivery_manifest.json`：适配 `check_stage_delivery.py --mode evidence`；仅枚举本RunId小型产物。\n\n"
        "- `artifacts/rebuilt_infer.elf`：从受SHA绑定的tmp ELF逐字节复制，供离线恢复。\n\n"
        "## 核验命令\n\n"
        "```bash\n"
        f"python -B tmp/2B/prepare_final_freeze_20261022.py --host-review {rel(host_review_path.resolve())}\n"
        f"python -B verification/check_stage_delivery.py --mode inputs --manifest report/evidence/S2B-T18/{RUN_ID}/inputs_manifest.json\n"
        f"python -B verification/check_stage_delivery.py --mode evidence --manifest report/evidence/S2B-T18/{RUN_ID}/delivery_manifest.json\n"
        "```\n\n"
        "清单保留各证据自身的PASS、FAILED、CHANGES_REQUIRED、UNKNOWN或BLOCKED边界。Git只保留代码/元数据；R04 bit/XSA、恢复包、重建ELF/init ELF、官方工具链/BSP以及模型原始数据是工作站/恢复归档依赖，不能删除；源代码仓库的干净检出不能单独重建全部二进制。\n"
    ).encode("utf-8")
    write_new(readme_path, readme)

    evidence_files = [
        bound(str(inventory_path), role="result"),
        bound(str(input_manifest_path), role="result"),
        bound(str(readme_path), role="result"),
    ]
    for item in inputs:
        role = item["role"]
        if role in {"result", "log", "diagnostic", "artifact"}:
            role = "input"
        evidence_files.append({"path": item["path"], "sha256": item["sha256"], "role": role})
    if not any(item["path"] == rebuilt_copy_binding["path"] for item in evidence_files):
        evidence_files.append({"path": rebuilt_copy_binding["path"],
                               "sha256": rebuilt_copy_binding["sha256"], "role": "artifact",
                               "keep_reason": "冻结包内重建PS ELF恢复副本"})
    delivery_manifest = {
        "schema_version": 1, "stage": "2B", "task_id": "S2B-T18", "run_id": RUN_ID,
        "source_commit": head, "evidence_dir": rel(RUN_DIR), "interfaces": interfaces,
        "files": evidence_files,
        "checks": [
            {"name": "候选冻结输入门禁及产物写入", "status": "PASS",
             "command": f"python -B tmp/2B/prepare_final_freeze_20261022.py --host-review {rel(host_review_path.resolve())}", "exit_code": 0,
             "reason": "生成成功表示组合证据、显式G2回执、输入SHA及本RunId产物写入均通过；PS r02失败状态在清单中原样保留。"},
            {"name": "独立最终G4/G5 verdict", "status": "NOT_RUN", "command": None,
             "exit_code": None, "reason": "由根方在冻结候选生成后安排独立审查；清单不自行判阶段通过。"},
        ],
        "limitations": inventory["limitations"],
        "tool_versions": {"python": sys.version.split()[0]},
    }
    write_json(RUN_DIR / "delivery_manifest.json", delivery_manifest)

    print(json.dumps({"status": inventory["status"], "run_id": RUN_ID,
                      "source_commit": head, "input_count": len(inputs),
                      "output_files": 4, "ps_run_status": ps_orchestrator["status"],
                      "ps_sample_status": ps_sample["status"], "ack_observer_status": observer["status"],
                      "r12_run_status": r12_orchestrator["status"],
                      "model_review_outcome": model_review["review_outcome"],
                      "inventory": rel(inventory_path), "manifest": rel(RUN_DIR / "delivery_manifest.json")},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="按指定双帧G2回执绑定阶段2B冻结候选输入")
        parser.add_argument("--host-review", required=True, type=Path,
                            help="根方提供的双帧及ACK观察独立G2回执完整路径")
        arguments = parser.parse_args()
        raise SystemExit(main(arguments.host_review))
    except Exception as error:
        print(f"冻结候选未生成：{error}", file=sys.stderr)
        raise
