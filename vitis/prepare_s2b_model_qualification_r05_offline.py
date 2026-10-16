"""准备R04构建对应的r05资格配置和只读阻断报告。"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).absolute().parents[1]
RUN_ID = "single_sample_qualification_20261017_r11"
PREP_DIR = ROOT / "report/evidence/S2B-T19/qualification_r04_single_job_20261017_r11"
CONFIG_PATH = PREP_DIR / "qualification_config.json"
INPUT_MANIFEST_PATH = PREP_DIR / "r05_input_manifest.json"
PREFLIGHT_REPORT_PATH = PREP_DIR / "offline_preflight_report.json"
DELIVERY_PATH = PREP_DIR / "delivery_manifest.json"
FUTURE_RUN_DIR = ROOT / "report/evidence/S2B-T19/single_sample_qualification_20261017_r11"
R04_RUN_DIR = ROOT / "report/evidence/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04"
R04_ARTIFACT_DIR = ROOT / "report/evidence/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04_artifacts"
R04_RUN_DELIVERY = R04_RUN_DIR / "delivery_manifest.json"
R04_ARTIFACT_DELIVERY = R04_ARTIFACT_DIR / "delivery_manifest.json"
R04_INPUT_RECORD = ROOT / "report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/input_record.json"
R04_XSA = ROOT / "report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.xsa"
R04_BIT = ROOT / "report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit"
R04_BUILD = R04_ARTIFACT_DIR / "build_details.json"
R04_APP = R04_ARTIFACT_DIR / "infer.elf"
R04_INIT = R04_ARTIFACT_DIR / "init.elf"
R04_XSA_SHA = "ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6"
R04_BIT_SHA = "555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7"
R04_BUILD_SHA = "59c42968085d656148de9aec13f4c9e623b7688fc79101038f2b661510c5c0db"
R04_APP_SHA = "a51499895e9387a74db87a3267843b9fbf7fdfa8b6646fcbc5db01485e090bf8"
R04_INIT_SHA = "237dd959f903589c657b743ea1fce175628aaa24020384058fc66339c779e7b1"
R04_INPUT_SHA = "01ef860527cfe7cc0979f2267ea1152bd48180a8c2f0a4b4d61d8bc2e70b4164"
R04_BUILD_SOURCE_COMMIT = "03faa2d47a6e49d7475e387cf6b33edda4962c68"
PRIOR_CONFIG = ROOT / "report/evidence/S2B-T19/cache_probe_execution_20261016_r03/input_config.json"
MODEL_PREP = ROOT / "report/evidence/S2B-T18/model_assets_20261016_r02/prep/preparation.json"
ASSET_ROOT = Path(r"D:\FPGA_Competition\report\evidence\S2A-T68\candidate8x8_109_20261006_130252")
MODEL_FILES = {
    "model_manifest": ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json",
    "samples_manifest": ROOT / "report/evidence/S2A-T01/fixed_test_samples.json",
    "golden_source": ROOT / "report/evidence/S2A-T29/cpu_decode_nms_reference.json",
}
FROZEN_MODEL_SHAS = {
    "model_manifest": "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a",
    "samples_manifest": "ccf741c1e996c72b985ce1dcbd399c5184347c922d286a8c0250ef5f6a755eed",
    "golden_source": "24361a13e262d1774ae255195dac3b05df4c16b9c287ff06945f2d630d3a0231",
}


class PreparationError(RuntimeError):
    """准备文件或离线绑定不满足固定来源。"""


def require(condition: bool, message: str) -> None:
    """在所有运行模式下保留准备约束。"""
    if not condition:
        raise PreparationError(message)


def digest_path(path: Path) -> str:
    """只对现有普通文件计算原字节摘要。"""
    require(path.is_absolute() and path.is_file() and not path.is_symlink(),
            f"文件缺失、类型错误或为链接：{path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bound(path: Path) -> dict:
    """创建精确绝对路径和SHA绑定。"""
    return {"path": str(path), "sha256": digest_path(path)}


def json_sha(value: dict) -> str:
    """计算与json_new相同缩进和换行的UTF-8 JSON摘要。"""
    raw = json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    return hashlib.sha256(raw).hexdigest()


def repo_path(path: Path) -> str:
    """将仓库内文件转换为清单使用的POSIX相对路径。"""
    return path.relative_to(ROOT).as_posix()


def strict_json(path: Path) -> dict:
    """读取对象JSON并拒绝重复键。"""
    def unique_pairs(rows):
        value = {}
        for key, item in rows:
            require(key not in value, f"JSON存在重复键：{path}:{key}")
            value[key] = item
        return value

    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs,
                       parse_constant=lambda token: (_ for _ in ()).throw(
                           PreparationError(f"JSON含非有限数：{path}:{token}")))
    require(type(value) is dict, f"JSON顶层必须为对象：{path}")
    return value


def load_modules():
    """加载纯Python离线检查器，不导入XSDB或串口模块。"""
    if str(ROOT / "vitis") not in sys.path:
        sys.path.insert(0, str(ROOT / "vitis"))
    if str(ROOT / "verification") not in sys.path:
        sys.path.insert(0, str(ROOT / "verification"))
    import run_s2b_model_qualification as runner
    import run_s2b_visibility_probe as probe
    import s2b_board_transport as transport
    return runner, probe, transport


def current_source_commit() -> str:
    """读取当前HEAD，要求构建输入确实来自该提交。"""
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
                          capture_output=True, text=True, encoding="ascii").stdout.strip()


def verify_r04_build() -> dict:
    """逐项核对独立审过的R04 build_details、XSA、bit和ELF。"""
    expected = ((R04_BUILD, R04_BUILD_SHA), (R04_APP, R04_APP_SHA),
                (R04_INIT, R04_INIT_SHA), (R04_XSA, R04_XSA_SHA),
                (R04_BIT, R04_BIT_SHA), (R04_INPUT_RECORD, R04_INPUT_SHA))
    rows = {path.name: {"path": str(path), "sha256": digest_path(path)}
            for path, sha in expected}
    for path, sha in expected:
        require(rows[path.name]["sha256"] == sha, f"R04固定产物SHA不符：{path}")
    record = strict_json(R04_INPUT_RECORD)
    require(record.get("status") == "FAIL" and record.get("hardware_execution") == "NOT_RUN",
            "R04原始input_record状态变化，保持原件并停止")
    build = strict_json(R04_BUILD)
    require(build.get("status") == "PASS_OFFLINE_FULL_XSA_BUILD" and
            build.get("hardware_execution") == "NOT_RUN" and
            build.get("hardware_mode") == "FULL_PLATFORM_BOUND",
            "R04 build_details身份或执行范围不符")
    build_source_commit = build.get("config", {}).get("source_commit")
    require(build.get("source_commit") == R04_BUILD_SOURCE_COMMIT and
            build_source_commit == R04_BUILD_SOURCE_COMMIT,
            "R04 build_details源码提交与其冻结构建身份不符")
    subprocess.run(["git", "merge-base", "--is-ancestor", R04_BUILD_SOURCE_COMMIT,
                    current_source_commit()], cwd=ROOT, check=True,
                   capture_output=True)
    require(build.get("xsa_sha256") == R04_XSA_SHA and
            build.get("config", {}).get("xsa_sha256") == R04_XSA_SHA and
            build.get("elf", {}).get("sha256") == R04_APP_SHA and
            build.get("initializer_elf", {}).get("sha256") == R04_INIT_SHA,
            "R04 build_details未绑定固定XSA/ELF")
    require(Path(build["config"]["xsa"]) == R04_XSA and
            Path(build["elf"]["path"]) == R04_APP and
            Path(build["initializer_elf"]["path"]) == R04_INIT,
            "R04 build_details产物路径与固定Run目录不一致")
    require(record.get("artifact_sha256", {}).get("s2b_inference.xsa") == R04_XSA_SHA and
            record.get("artifact_sha256", {}).get("s2b_inference.bit") == R04_BIT_SHA,
            "R04 FAIL记录与XSA/bit身份不一致")
    return {"build_details": rows[R04_BUILD.name], "infer_elf": rows[R04_APP.name],
            "init_elf": rows[R04_INIT.name], "compiled_xsa": rows[R04_XSA.name],
            "bit": rows[R04_BIT.name], "original_input_record": {
                **rows[R04_INPUT_RECORD.name], "status": "FAIL",
                "hardware_execution": "NOT_RUN"},
            "build_source_commit": build_source_commit,
            "current_source_commit": current_source_commit(),
            "build_status_as_recorded": build["status"],
            "hardware_execution": build["hardware_execution"]}


def verify_model_rows(transport) -> dict:
    """验证冻结tiny416权重、109输入和109份独立参考绑定。"""
    prep = strict_json(MODEL_PREP)
    require(prep.get("status") == "NOT_RUN" and prep.get("hardware_execution") == "NOT_RUN" and
            len(prep.get("rows", [])) == 109, "冻结模型准备记录状态或行数错误")
    require(prep.get("weights", {}).get("path") == str(
        ASSET_ROOT / "fixtures/common/weights.gf8"), "冻结权重路径错误")
    weights_path, weights, rows = transport.load_assets(ASSET_ROOT, list(range(109)))
    require(len(rows) == 109 and hashlib.sha256(weights).hexdigest() ==
            prep["weights"]["sha256"] and len(weights) == prep["weights"]["bytes"],
            "冻结权重实际文件与准备记录不一致")
    documents = {}
    for key, path in MODEL_FILES.items():
        require(prep.get(key, {}).get("sha256") == FROZEN_MODEL_SHAS[key],
                f"冻结模型文档摘要声明错误：{key}")
        require(digest_path(path) == FROZEN_MODEL_SHAS[key], f"冻结模型文档内容变化：{key}")
        documents[key] = bound(path)
    model_rows = []
    references = []
    for index, (prep_row, loaded_row) in enumerate(zip(prep["rows"], rows, strict=True)):
        require(prep_row.get("index") == index, f"冻结样本索引不连续：{index}")
        input_path = Path(prep_row["input"]["path"])
        reference_path = Path(prep_row["reference"]["path"])
        require(input_path == loaded_row["input_path"] and
                prep_row["input"]["sha256"] == loaded_row["input_sha256"],
                f"冻结样本输入与transport loader不一致：{index}")
        input_sha = digest_path(input_path)
        reference_sha = digest_path(reference_path)
        require(input_sha == prep_row["input"]["sha256"] and
                reference_sha == prep_row["reference"]["sha256"],
                f"冻结输入或黄金参考SHA不符：{index}")
        row = {"index": index, "sample_id": prep_row["sample_id"],
               "input": {"path": str(input_path), "sha256": input_sha,
                         "bytes": input_path.stat().st_size},
               "reference": {"path": str(reference_path), "sha256": reference_sha}}
        model_rows.append(row)
        references.append(row["reference"])
    return {"asset_root": str(ASSET_ROOT), "weights": bound(weights_path),
            "weights_bytes": len(weights), "frozen_documents": documents,
            "sample_count": len(model_rows), "samples": model_rows,
            "reference_count": len(references),
            "preparation_record": bound(MODEL_PREP)}


def build_candidate_config() -> dict:
    """构造r05待资格配置；所有未建立的信任依据保留为null。"""
    runner, probe, transport = load_modules()
    build_identity = verify_r04_build()
    old = strict_json(PRIOR_CONFIG)
    require(not FUTURE_RUN_DIR.exists(), f"r05资格运行目录已存在，拒绝复用：{FUTURE_RUN_DIR}")
    require(FUTURE_RUN_DIR.parent.is_dir(), f"未来运行父目录不存在：{FUTURE_RUN_DIR.parent}")
    p, j, _ = runner.helpers()
    source_commit = current_source_commit()
    bindings = dict(old["bindings"])
    bindings.update({
        "app_elf": build_identity["infer_elf"],
        "init_elf": build_identity["init_elf"],
        "xsa": build_identity["compiled_xsa"],
        "bit": build_identity["bit"],
    })
    source_paths = {
        "csr_source": ROOT / "src/s2b_control_csr.sv",
        "interface": ROOT / "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md",
        "sdk_target": probe.SDK_INIT.parent / "target.py",
        "tool_source": Path(j.__file__),
        "elf_parser": ROOT / "verification/check_s2b_ps_smoke_layout.py",
        "delivery_parser": ROOT / "verification/check_stage_delivery.py",
        "transport_source": Path(transport.__file__),
        "entry_source": Path(probe.__file__),
        "platform_checker": ROOT / "verification/check_s2b_inference_platform.py",
        "sdk_init": probe.SDK_INIT,
    }
    bindings.update({key: bound(path) for key, path in source_paths.items()})
    require(bindings["tool_source"]["sha256"] == p.JTAG_SHA,
            "qualification入口绑定的JTAG来源与固定SHA不同")
    serial_files = old["pyserial_files"]
    sdk_files = old["sdk_files"]
    config = {
        "schema_version": 1,
        "source_commit": source_commit,
        "run_dir": str(FUTURE_RUN_DIR),
        "build_details": build_identity["build_details"],
        "bindings": bindings,
        "owned_hw_server_identity": None,
        "uart_identity": None,
        "cold_basis": runner.TRUSTED_COLD_ANCHOR,
        "sdk_files": sdk_files,
        "pyserial_files": serial_files,
        "asset_root": str(ASSET_ROOT),
        "qualification_receipt": None,
        "sample_index": 0,
        "frame": 0,
        "repeat": 1,
        "core_timeout_cycles": 0xFFFFFFFF,
        "drain_timeout_cycles": 0xFFFFFFFF,
        "response_timeout_seconds": 450,
        "g0_basis": runner.TRUSTED_G0_ANCHOR,
        "timeout_basis": None,
    }
    runner.validate_config(config)
    return config


def build_offline_report(config: dict, build_identity: dict, model_inputs: dict) -> dict:
    """运行纯静态preflight并明确保存全部缺失锚点，不生成资格通过结论。"""
    runner, _, _ = load_modules()
    gaps = runner.hardware_enablement_gaps(config)
    require(gaps, "锚点意外全部存在；拒绝以此离线准备流程升级资格状态")
    try:
        runner.preflight(config)
    except runner.QualificationError as error:
        message = str(error)
        require("缺少部署信任锚点" in message,
                "只读preflight在锚点报告前被其他问题阻断：" + message)
        preflight_result = {"status": "BLOCKED", "native_exit_code": 2,
                            "diagnostic": message, "hardware_execution": "NOT_RUN"}
    else:
        raise PreparationError("缺失信任锚点未阻断preflight，停止准备")
    return {
        "schema_version": 1,
        "record_type": "S2B_T19_QUALIFICATION_R05_OFFLINE_PREFLIGHT",
        "run_id": RUN_ID,
        "source_commit": config["source_commit"],
        "status": "BLOCKED_MISSING_TRUST_ANCHORS",
        "qualification_gate": "NOT_PASSED",
        "hardware_execution": "NOT_RUN",
        "preflight_result": preflight_result,
        "candidate_build_bindings": build_identity,
        "frozen_model_inputs": {
            "sample_count": model_inputs["sample_count"],
            "reference_count": model_inputs["reference_count"],
            "weights": model_inputs["weights"],
            "frozen_documents": model_inputs["frozen_documents"],
            "preparation_record": model_inputs["preparation_record"],
        },
        "runtime_python_bindings": {
            "source_config": bound(PRIOR_CONFIG),
            "status": "CARRIED_AS_UNVERIFIED_REFERENCE",
            "limitations": "离线静态preflight在缺失信任锚点前不枚举或导入XSDB/pyserial运行时。",
        },
        "missing_anchors": gaps,
        "qualification_config": {"path": str(CONFIG_PATH), "sha256": json_sha(config)},
        "limitations": [
            "本报告仅说明静态候选绑定与实际缺失门禁；不授权任何板卡、串口、XSDB、PS初始化或DDR访问。",
            "R04原始input_record.json仍为FAIL且硬件NOT_RUN，未修改。",
            "不表示单样本、109样本、1000连续任务或G3/G4/G5通过。",
            "Reviewer、G0及外部POR/保管链仍须真实证据及总控固定路径/SHA；首个受控样本按冻结规程使用最大有限CORE/DRAIN上限，最终部署期限测量仍须在G4/G5完成。",
        ],
    }


def file_item(path: Path, role: str, reason: str | None = None) -> dict:
    """创建delivery manifest的单文件绑定。"""
    row = {"path": repo_path(path), "sha256": digest_path(path), "role": role}
    if reason:
        row["keep_reason"] = reason
    return row


def json_new(path: Path, value: dict) -> None:
    """只创建新的UTF-8证据文件，不覆盖已有内容。"""
    require(not path.exists(), f"拒绝覆盖已有输出：{path}")
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def delivery_manifest(directory: Path, run_id: str, files: list[dict], interfaces: list[dict],
                      *, extra_checks: list[dict]) -> dict:
    """组成该目录完整枚举清单；检查状态只描述本封包，不替代G0/G4/G5。"""
    head = current_source_commit()
    return {
        "schema_version": 1,
        "stage": "2B",
        "task_id": "S2B-T15" if directory.parent.name == "S2B-T15" else "S2B-T19",
        "run_id": run_id,
        "source_commit": head,
        "evidence_dir": repo_path(directory),
        "interfaces": interfaces,
        "files": files,
        "checks": extra_checks,
        "limitations": [
            "CHECKS_OK仅表示该目录文件清单及SHA包装核验完成，不表示Vitis构建、静态资格或实物任务通过。",
            "本封包未运行板卡资格；R04原始input_record.json仍为FAIL。",
        ],
        "tool_versions": {"Python": sys.version.split()[0], "Vitis": "2026.1"},
    }


def interface_binding() -> list[dict]:
    """引用当前正式候选接口文档及原始SHA。"""
    path = ROOT / "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
    return [{"name": "阶段2B物理接口候选", "version": "s2b-physical-candidate/0.1.2",
             "frozen": False, "path": repo_path(path), "sha256": digest_path(path)}]


def package_r04_build() -> tuple[dict, dict]:
    """为既有Vitis run与artifact两个目录新建互相绑定的清单。"""
    if R04_RUN_DELIVERY.exists() or R04_ARTIFACT_DELIVERY.exists():
        require(R04_RUN_DELIVERY.is_file() and R04_ARTIFACT_DELIVERY.is_file(),
                "R04目录清单不完整，拒绝重建或覆盖")
        run_manifest = strict_json(R04_RUN_DELIVERY)
        artifact_manifest = strict_json(R04_ARTIFACT_DELIVERY)
        require(run_manifest.get("run_id") == R04_RUN_DIR.name and
                artifact_manifest.get("run_id") == R04_ARTIFACT_DIR.name and
                run_manifest.get("evidence_dir") == repo_path(R04_RUN_DIR) and
                artifact_manifest.get("evidence_dir") == repo_path(R04_ARTIFACT_DIR),
                "现有R04清单的RunId/目录绑定不符")
        return run_manifest, artifact_manifest
    run_files = sorted((path for path in R04_RUN_DIR.rglob("*") if path.is_file()),
                       key=lambda path: path.as_posix())
    artifact_files = sorted((path for path in R04_ARTIFACT_DIR.rglob("*") if path.is_file()),
                            key=lambda path: path.as_posix())
    require(run_files and artifact_files, "R04 run或artifact目录为空")
    external_run_inputs = [R04_RUN_DIR / name for name in
                           ("build.cmd", "config.json", "launcher_record.json",
                            "vitis-server.stdout.log", "vitis.stdout.log")]
    require(all(path.is_file() for path in external_run_inputs), "R04运行器交接文件缺失")
    artifact_entries = []
    for path in artifact_files:
        relative = path.relative_to(R04_ARTIFACT_DIR)
        if relative.parts[0] == "source_snapshot":
            role = "source"
        elif path.suffix == ".log":
            role = "log"
        elif path.suffix in {".elf", ".xsa", ".bit", ".a", ".dcp"}:
            role = "artifact"
        elif path.suffix == ".i" or path.suffix in {".c", ".h", ".S", ".ld"}:
            role = "source"
        else:
            role = "result"
        artifact_entries.append(file_item(path, role,
                                          "保留R04 Vitis实际构建的来源快照、原始产物或诊断文件。"
                                          if role in {"log", "diagnostic", "artifact"} else None))
    artifact_entries.extend(file_item(path, "input", "交叉绑定同一次R04受控launcher输入与运行记录。")
                            for path in external_run_inputs)
    upstream_inputs = (R04_INPUT_RECORD, R04_XSA, R04_BIT,
                       ROOT / "report/evidence/S2B-T19/model_qualification_offline_20261016_r04/r04_xsa_rebuild_input_manifest.json")
    artifact_entries.extend(file_item(path, "input", "绑定本次R04重建使用的固定平台、位流和原FAIL输入记录。")
                            for path in upstream_inputs)
    artifact_check = {"name": "R04构建目录evidence包装核验", "status": "NOT_RUN",
                      "command": "python -B verification/check_stage_delivery.py --mode evidence --manifest " + repo_path(R04_ARTIFACT_DELIVERY),
                      "exit_code": None,
                      "reason": "清单新建时尚未执行包装检查；实际命令结果由后续只读检查器输出。"}
    artifact_manifest = delivery_manifest(
        R04_ARTIFACT_DIR, R04_ARTIFACT_DIR.name, artifact_entries, interface_binding(),
        extra_checks=[artifact_check,
                      {"name": "板卡资格验收", "status": "NOT_RUN", "command": "NOT_RUN",
                       "exit_code": None, "reason": "此目录仅为已有Vitis离线构建产物封包。"}])
    json_new(R04_ARTIFACT_DELIVERY, artifact_manifest)

    run_entries = []
    for path in run_files:
        if path.name in {"vitis.stdout.log", "vitis-server.stdout.log"}:
            role = "log"
        elif "source_snapshot" in path.parts:
            role = "source"
        elif path.name == "launcher_record.json":
            role = "result"
        else:
            role = "input"
        run_entries.append(file_item(path, role,
                                     "保留外层managed Vitis launcher的真实输入、源码快照或原始日志。"
                                     if role == "log" else None))
    run_entries.append(file_item(R04_ARTIFACT_DELIVERY, "input",
                                 "绑定相邻artifact目录及其完整SHA清单。"))
    run_entries.extend(file_item(path, "input", "固定R04含bit XSA、bit及原FAIL记录。")
                       for path in upstream_inputs)
    run_manifest = delivery_manifest(
        R04_RUN_DIR, R04_RUN_DIR.name, run_entries, interface_binding(),
        extra_checks=[{"name": "R04 run目录evidence包装核验", "status": "NOT_RUN",
                       "command": "python -B verification/check_stage_delivery.py --mode evidence --manifest " + repo_path(R04_RUN_DELIVERY),
                       "exit_code": None,
                       "reason": "清单新建时尚未执行包装检查；实际命令结果由后续只读检查器输出。"},
                      {"name": "板卡资格验收", "status": "NOT_RUN", "command": "NOT_RUN",
                       "exit_code": None, "reason": "此目录不含板卡资格执行。"}])
    json_new(R04_RUN_DELIVERY, run_manifest)
    return run_manifest, artifact_manifest


def r05_delivery_manifest(config: dict, input_manifest: dict, report: dict) -> dict:
    """为r05离线配置及阻断报告生成完整delivery文件清单。"""
    local_files = (CONFIG_PATH, INPUT_MANIFEST_PATH, PREFLIGHT_REPORT_PATH)
    entries = [file_item(path, "result") for path in local_files]
    source_paths = (Path(__file__), ROOT / "vitis/run_s2b_model_qualification.py",
                    ROOT / "vitis/prepare_s2b_model_qualification_offline.py",
                    ROOT / "verification/test_s2b_model_qualification_entry.py",
                    ROOT / "verification/s2b_board_transport.py",
                    ROOT / "verification/check_s2b_inference_platform.py")
    entries.extend(file_item(path, "source") for path in source_paths)
    input_paths = (R04_BUILD, R04_APP, R04_INIT, R04_XSA, R04_BIT, R04_INPUT_RECORD,
                   MODEL_PREP, *MODEL_FILES.values(),
                   ROOT / "report/evidence/S2B-T19/model_qualification_offline_20261016_r04/r04_xsa_rebuild_input_manifest.json")
    entries.extend(file_item(path, "input", "绑定r04已审构建、候选XSA/bit、FAIL原记录及冻结tiny416输入来源。")
                   for path in input_paths)
    return delivery_manifest(
        PREP_DIR, PREP_DIR.name, entries, interface_binding(),
        extra_checks=[{"name": "R04静态绑定与离线preflight", "status": "BLOCKED",
                       "command": "prepare_s2b_model_qualification_r05_offline.py --write-evidence",
                       "exit_code": None,
                       "reason": "R04候选文件绑定已检查；当前Reviewer、G0、POR/保管链锚点缺失，资格门保持BLOCKED。CORE/DRAIN首测期限使用最大有限上限，最终部署期限测量仍属G4/G5。"},
                      {"name": "单样本板卡资格", "status": "NOT_RUN", "command": "NOT_RUN",
                       "exit_code": None, "reason": "本Run仅准备离线配置与证据绑定，不执行qualification main或硬件。"},
                      {"name": "109样本与1000连续任务", "status": "NOT_RUN", "command": "NOT_RUN",
                       "exit_code": None, "reason": "本Run没有启动任何上板任务。"}])


def build_outputs() -> dict:
    """构造r05配置、109样本清单及包含缺失锚点的阻断报告。"""
    for path in (PREP_DIR, CONFIG_PATH, INPUT_MANIFEST_PATH, PREFLIGHT_REPORT_PATH,
                 DELIVERY_PATH, FUTURE_RUN_DIR):
        require(not path.exists(), f"r05或R04清单目标已存在，拒绝覆盖：{path}")
    require(PREP_DIR.parent.is_dir(), f"r05父目录不存在：{PREP_DIR.parent}")
    runner, _, transport = load_modules()
    build_identity = verify_r04_build()
    config = build_candidate_config()
    model_inputs = verify_model_rows(transport)
    static_result = None
    try:
        static_result = runner.verify_static_candidate_bindings(config)
    except Exception as error:
        raise PreparationError("R04静态候选绑定不完整：" + repr(error)) from error
    report = build_offline_report(config, build_identity, model_inputs)
    input_manifest = {
        "schema_version": 1,
        "record_type": "S2B_T19_QUALIFICATION_R05_INPUT_BINDING",
        "run_id": RUN_ID,
        "source_commit": config["source_commit"],
        "status": "PREPARED_NOT_RUN",
        "qualification_gate": "NOT_PASSED",
        "hardware_execution": "NOT_RUN",
        "candidate_build_bindings": build_identity,
        "frozen_model_inputs": model_inputs,
        "inherited_runtime_bindings": bound(PRIOR_CONFIG),
        "static_candidate_checks_observed": {
            "build_status_as_recorded": static_result["build"]["status"],
            "source_commit": static_result["source_commit"],
            "model_sample_index": static_result["row"]["sample_index"],
            "golden_file": str(static_result["golden_path"]),
            "golden_sha256": digest_path(static_result["golden_path"]),
        },
        "missing_anchors": report["missing_anchors"],
        "r04_input_record_status": "FAIL",
        "limitations": [
            "此清单绑定r04已审产物和冻结tiny416全部109输入/109参考，不是资格回执。",
            "未运行Vitis、qualification main、XSDB、UART、PS初始化、板卡、109样本或1000任务。",
        ],
    }
    PREP_DIR.mkdir()
    json_new(CONFIG_PATH, config)
    report["qualification_config"] = bound(CONFIG_PATH)
    json_new(INPUT_MANIFEST_PATH, input_manifest)
    json_new(PREFLIGHT_REPORT_PATH, report)
    package_r04_build()
    manifest = r05_delivery_manifest(config, input_manifest, report)
    json_new(DELIVERY_PATH, manifest)
    return {"run_id": RUN_ID, "config": str(CONFIG_PATH),
            "input_manifest": str(INPUT_MANIFEST_PATH),
            "offline_preflight_report": str(PREFLIGHT_REPORT_PATH),
            "delivery_manifest": str(DELIVERY_PATH),
            "qualification_gate": report["qualification_gate"],
            "hardware_execution": report["hardware_execution"],
            "missing_anchor_count": len(report["missing_anchors"])}


def main() -> int:
    """仅写入全新r05离线配置与两目录R04封包清单，不启动资格或硬件。"""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-evidence", action="store_true",
                        help="新建r05离线证据与R04目录封包清单；不覆盖任何现有目标")
    args = parser.parse_args()
    if not args.write_evidence:
        parser.error("需要显式指定--write-evidence")
    try:
        print(json.dumps(build_outputs(), ensure_ascii=False))
        return 0
    except Exception as error:
        print(json.dumps({"status": "PREPARATION_BLOCKED", "error": repr(error)},
                         ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
