"""只读核验R04候选平台、现有PS ELF与冻结tiny416资产的离线绑定。

该入口不调用SDK、串口、JTAG或硬件，也不生成硬件资格收据。输出仅供独立
Reviewer审查候选文件之间的关系；任何硬件任务仍由正式资格入口的全部门禁决定。
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).absolute().parents[1]
R04_SOURCE_COMMIT = "6f5c6dc871d92fe32e5d37a58ff693442b793903"
R04_INPUT_RECORD_SHA256 = "01ef860527cfe7cc0979f2267ea1152bd48180a8c2f0a4b4d61d8bc2e70b4164"
R04_SOURCE_PATHS = (
    "board/ps_platform_fields.json",
    "board/s2b_inference_platform.json",
    "board/s2b_inference_platform.md",
    "src/int8_maxpool_window.sv",
    "src/int8_upsample_query.sv",
    "src/s2a_control_csr.sv",
    "src/s2a_memory_master.sv",
    "src/s2a_network_descriptor_pkg.sv",
    "src/s2a_runtime_shell.sv",
    "src/s2b_control_csr.sv",
    "src/s2b_conv_tile_engine.sv",
    "src/s2b_hp0_word_adapter.sv",
    "src/s2b_inference_top.sv",
    "src/s2b_maxpool_engine.sv",
    "src/s2b_maxpool_geometry.sv",
    "src/s2b_network_backend.sv",
    "src/s2b_request_guard.sv",
    "src/s2b_route_engine.sv",
    "src/s2b_route_query.sv",
    "src/s2b_stage2b_core.sv",
    "src/s2b_upsample_engine.sv",
    "verification/check_s2b_inference_platform.py",
    "verification/s15_job_guard.py",
    "verification/s2b_process_supervisor.py",
    "vivado/s2b_inference_platform.tcl",
    "vivado/s2b_ps_platform.tcl",
)
R04 = ROOT / "report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04"
T15 = ROOT / "report/evidence/S2B-T15/csr_fixed_platform_offline_20261016_r03"
MODEL_PREP = ROOT / "report/evidence/S2B-T18/model_assets_20261016_r02/prep/preparation.json"
ASSET_ROOT = Path(r"D:\FPGA_Competition\report\evidence\S2A-T68\candidate8x8_109_20261006_130252")
OUTPUT = ROOT / "report/evidence/S2B-T19/model_qualification_offline_20261016_r04/offline_binding_report.json"
OUTPUT_DIR = OUTPUT.parent
REBUILD_RUN_ID = "qualification_r04_xsa_rebuild_20261016_r04"
REBUILD_MANIFEST = OUTPUT_DIR / "r04_xsa_rebuild_input_manifest.json"
REBUILD_RUN_DIR = ROOT / "report/evidence/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04"
REBUILD_CONFIG = REBUILD_RUN_DIR / "config.json"
REBUILD_WORKSPACE = ROOT / "tmp/2B/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04"
REBUILD_ARTIFACT_DIR = ROOT / "report/evidence/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04_artifacts"
VITIS_BAT = Path(r"D:\Xilinx\2026.1\Vitis\bin\vitis.bat")
MANAGED_PYTHON = Path(r"C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe")
R04_BIT_SHA = "555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7"
R04_XSA_SHA = "ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6"
R04_FINAL_MANIFEST_SHA = "72fbf59b374665db43452d6ccb2ae4845b20f1042f233697a8802842771edfa9"
T15_DELIVERY_SHA = "17b6c017740972565755aa2d75a1b19fb51dce3d5482de8427c465184ce71b79"
T15_FINAL_DELIVERY_SHA = "72fbf59b374665db43452d6ccb2ae4845b20f1042f233697a8802842771edfa9"
T15_BUILD_SHA = "e96bb5042a9824b20231060e60a475effd0dd8c0c8d2db599b1112844aa3f104"
T15_XSA_SHA = "0607120b1733ee17582ab0c508c366fca7b1f49d32afffe87a070a346df04252"
T15_APP_SHA = "a7fbbab2b1aecfe6b46c84118180303362483f4b7742d9e7cfe3fb59ae02ce82"
T15_INIT_SHA = "26824eb5ec3a73d3dc606b7f7797591b12ca82cf8fb8dc0e40f3a8756efaaadc"


class OfflineBindingError(RuntimeError):
    """静态输入不满足预期的原字节或来源绑定。"""


def require(condition: bool, message: str) -> None:
    """不依赖assert，确保优化运行时仍执行约束。"""
    if not condition:
        raise OfflineBindingError(message)


def sha256(path: Path) -> str:
    """对普通文件原字节计算SHA-256。"""
    require(path.is_absolute() and path.exists() and path.is_file(), f"文件缺失或类型错误：{path}")
    require(not path.is_symlink(), f"拒绝符号链接：{path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strict_json(path: Path) -> dict:
    """拒绝重复键、非有限数和非对象JSON。"""
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, f"JSON重复键：{path}:{key}")
            result[key] = value
        return result

    def reject_constant(value):
        raise OfflineBindingError(f"JSON包含非有限数：{path}:{value}")

    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
                       parse_constant=reject_constant)
    require(type(value) is dict, f"JSON顶层必须为对象：{path}")
    return value


def verify_bound(path: Path, expected: str, label: str) -> dict:
    """核对精确文件身份和原字节摘要。"""
    observed = sha256(path)
    require(observed == expected, f"{label} SHA不符：{path}")
    return {"path": str(path), "sha256": observed, "bytes": path.stat().st_size}


def verify_r04_record_hash(path: Path) -> str:
    """将原始R04输入记录绑定到独立给定的固定摘要。"""
    observed = sha256(path)
    require(observed == R04_INPUT_RECORD_SHA256,
            f"R04 input_record.json SHA不符：{observed}")
    return observed


def verify_source_closure(source_hashes: dict) -> list[dict]:
    """以固定路径闭包从R04 Git tree读取源文件并核对记录、工作树摘要。"""
    require(type(source_hashes) is dict and set(source_hashes) == set(R04_SOURCE_PATHS),
            "R04源码闭包路径集合与固定清单不一致")
    tree = subprocess.run(["git", "ls-tree", "-r", "-z", "--full-tree",
                           R04_SOURCE_COMMIT], cwd=ROOT, check=True,
                          capture_output=True).stdout
    tree_blobs = {}
    for entry in tree.split(b"\0"):
        if not entry:
            continue
        metadata, relative_raw = entry.split(b"\t", 1)
        mode, object_type, object_id = metadata.decode("ascii").split()
        relative = relative_raw.decode("utf-8")
        if relative in R04_SOURCE_PATHS:
            require(object_type == "blob" and mode in ("100644", "100755"),
                    f"R04 Git tree源码不是普通blob：{relative}")
            tree_blobs[relative] = object_id
    require(set(tree_blobs) == set(R04_SOURCE_PATHS),
            "R04指定commit tree缺少固定源码闭包成员")

    checked = []
    for relative in R04_SOURCE_PATHS:
        git_blob = subprocess.run(["git", "cat-file", "blob", tree_blobs[relative]],
                                  cwd=ROOT, check=True, capture_output=True).stdout
        blob_sha = hashlib.sha256(git_blob).hexdigest()
        crlf_checkout_sha = hashlib.sha256(
            git_blob.replace(b"\n", b"\r\n") if b"\r" not in git_blob else git_blob
        ).hexdigest()
        path = ROOT / relative
        require(path.resolve(strict=True) == path,
                f"源码路径含链接或非规范成分：{path}")
        worktree_sha = sha256(path)
        require(worktree_sha in (blob_sha, crlf_checkout_sha),
                f"当前工作树源码与R04指定commit tree不一致：{relative}")
        require(source_hashes[relative] == worktree_sha,
                f"R04记录源码摘要与指定commit tree工作树表示不一致：{relative}")
        checked.append({"path": str(path), "sha256": worktree_sha,
                        "git_blob": tree_blobs[relative],
                        "git_blob_sha256": blob_sha,
                        "git_checkout_line_ending": "CRLF" if worktree_sha == crlf_checkout_sha and worktree_sha != blob_sha else "LF_OR_NO_LF"})
    return checked


def verify_r04() -> dict:
    """验证R04原记录、当前源码闭包、XSA和独立bit的静态绑定。"""
    record_path = R04 / "input_record.json"
    record_sha = verify_r04_record_hash(record_path)
    record = strict_json(record_path)
    require(record.get("status") == "FAIL" and record.get("hardware_execution") == "NOT_RUN",
            "R04输入记录状态变化；保持原记录并停止")
    require(record.get("current_source_commit") == R04_SOURCE_COMMIT,
            "R04记录未绑定预期源码HEAD")
    observed_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                   check=True, capture_output=True, text=True).stdout.strip()
    subprocess.run(["git", "merge-base", "--is-ancestor", R04_SOURCE_COMMIT, observed_head],
                   cwd=ROOT, check=True, capture_output=True)

    source_hashes = record.get("source_sha256")
    checked_sources = verify_source_closure(source_hashes)

    artifacts = record.get("artifact_sha256")
    require(type(artifacts) is dict, "R04缺少产物SHA表")
    artifact_dir = R04 / "artifacts"
    xsa = artifact_dir / "s2b_inference.xsa"
    bit = artifact_dir / "s2b_inference.bit"
    require(artifacts.get(xsa.name) == R04_XSA_SHA and
            artifacts.get(bit.name) == R04_BIT_SHA,
            "R04 XSA/bit未与固定产物记录一致")
    xsa_binding = verify_bound(xsa, R04_XSA_SHA, "R04含bit XSA")
    bit_binding = verify_bound(bit, R04_BIT_SHA, "R04 standalone bit")
    with zipfile.ZipFile(xsa) as archive:
        bit_members = [name for name in archive.namelist() if name.lower().endswith(".bit")]
        require(len(bit_members) == 1, "R04 XSA必须含且仅含一个bit")
        embedded = archive.read(bit_members[0])
    embedded_sha = hashlib.sha256(embedded).hexdigest()
    require(embedded_sha == R04_BIT_SHA and embedded == bit.read_bytes(),
            "R04 XSA内嵌bit与独立bit不一致")
    reconciliation = record.get("bit_header_reconciliation", {})
    require(reconciliation.get("status") == "PASS_HEADER_AND_PAYLOAD_RECONCILED" and
            reconciliation.get("raw_sha256") == R04_BIT_SHA and
            reconciliation.get("canonical_sha256") == R04_BIT_SHA and
            reconciliation.get("e_payload_byte_equal") is True,
            "R04既有bit头部/载荷对账不通过")
    require(record.get("stdout_has_profile_bindings") is False,
            "R04原FAIL原因已变化；本工具不重写原记录")

    return {
        "run_id": "visibility1_csr_fixed_20261016_r04",
        "original_input_record": {"path": str(record_path), "sha256": record_sha,
                                   "status": record["status"],
                                   "stdout_has_profile_bindings": False},
        "source_commit": R04_SOURCE_COMMIT,
        "current_repository_head": observed_head,
        "current_source_closure_matches_r04": True,
        "source_closure_count": len(checked_sources),
        "source_closure_sha256": checked_sources,
        "compiled_xsa": xsa_binding,
        "standalone_bit": bit_binding,
        "embedded_bit": {"member": bit_members[0], "sha256": embedded_sha,
                          "byte_equal_to_standalone": True},
        "bit_header_reconciliation": "PASS_HEADER_AND_PAYLOAD_RECONCILED",
    }


def rebuild_plan(r04: dict, t15: dict, model: dict) -> dict:
    """预检新RunId配置；不导入Vitis SDK、不创建workspace或输出目录。"""
    if str(ROOT / "vitis") not in sys.path:
        sys.path.insert(0, str(ROOT / "vitis"))
    import build_s2b_inference

    xsa = Path(r04["compiled_xsa"]["path"])
    platform = build_s2b_inference.xsa_contract(xsa, "FULL_PLATFORM_BOUND")
    with zipfile.ZipFile(xsa) as archive:
        hwh_names = [name for name in archive.namelist() if name.endswith(".hwh")]
        require(len(hwh_names) == 1, "R04 XSA HWH数量不为1")
        hwh = ET.fromstring(archive.read(hwh_names[0]))
    ps = [module for module in hwh.iter("MODULE")
          if module.attrib.get("MODTYPE") == "processing_system7"]
    require(len(ps) == 1, "R04 XSA PS7实例数量不为1")
    params = {item.attrib.get("NAME"): item.attrib.get("VALUE")
              for item in ps[0].findall("PARAMETERS/PARAMETER")}
    ddr_part = params.get("PCW_UIPARAM_DDR_PARTNO")
    require(ddr_part == "MT41K256M16TW-107",
            "R04 HWH DDR完整料号与当前手册候选不符")

    current_head = r04["current_repository_head"]
    source_rows = {}
    for relative in (
        "vitis/s2b_inference_app.c", "vitis/build_s2b_inference.py",
        "vitis/build_s2b_ps_smoke.py", "verification/s2a_ps_decode_nms_reference.c",
        "verification/s2a_ps_decode_nms_reference.h", "verification/s2b_board_transport.py",
        "verification/check_s2b_ps_smoke_layout.py", "verification/check_s2b_inference_mmu.py",
        "verification/s2b_managed_vitis.py",
    ):
        path = ROOT / relative
        source_rows[relative] = {"path": str(path), "sha256": sha256(path)}

    input_manifest = {
        "schema_version": 1,
        "record_type": "S2B_T15_REBUILD_INPUT_BINDING",
        "status": "PREPARED_NOT_RUN",
        "hardware_execution": "NOT_RUN",
        "run_id": REBUILD_RUN_ID,
        "current_source_commit": current_head,
        "xsa_source_commit": R04_SOURCE_COMMIT,
        "xsa": r04["compiled_xsa"],
        "bit": r04["standalone_bit"],
        "r04_original_record": r04["original_input_record"],
        "r04_original_record_status": "FAIL",
        "full_platform_static_metadata": platform,
        "ps_ddr_part_from_hwh": ddr_part,
        "reused_elf_inputs": {
            "prior_app_elf": t15["app_elf"],
            "prior_init_elf": t15["init_elf"],
            "prior_build_details": t15["build_details"],
            "prior_elf_build_xsa": t15["elf_build_xsa"],
            "prior_elf_matches_r04_xsa": False,
        },
        "frozen_model_inputs": model,
        "build_source_inputs": source_rows,
        "run_outputs": {"workspace": str(REBUILD_WORKSPACE),
                        "artifact_dir": str(REBUILD_ARTIFACT_DIR),
                        "managed_run_dir": str(REBUILD_RUN_DIR),
                        "managed_config": str(REBUILD_CONFIG)},
        "limitations": [
            "此输入清单仅绑定R04 XSA及构建源；重建未执行。",
            "须在同一R04含bit XSA上重新构建BSP、infer.elf和init.elf，再独立审查新build_details。",
            "原R04 input_record FAIL保持不变；本清单不升级R04原构建状态。",
            "静态XSA参数核验不证明实际板卡、DDR稳定性、PS初始化行为或G3。",
        ],
    }
    manifest_raw = json.dumps(input_manifest, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    manifest_sha = hashlib.sha256(manifest_raw).hexdigest()
    config = {
        "schema_version": 1,
        "source_commit": current_head,
        "xsa": str(xsa),
        "xsa_sha256": r04["compiled_xsa"]["sha256"],
        "xsa_source_commit": R04_SOURCE_COMMIT,
        "hardware_mode": "FULL_PLATFORM_BOUND",
        "platform_manifest": str(REBUILD_MANIFEST),
        "platform_manifest_sha256": manifest_sha,
        "workspace": str(REBUILD_WORKSPACE),
        "artifact_dir": str(REBUILD_ARTIFACT_DIR),
    }
    config_raw = json.dumps(config, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    config_sha = hashlib.sha256(config_raw).hexdigest()
    for candidate in (REBUILD_WORKSPACE, REBUILD_ARTIFACT_DIR):
        require(candidate.parent.is_dir(), f"Run输出父目录不存在：{candidate.parent}")
    existing_run = REBUILD_RUN_DIR.exists()
    existing_manifest = REBUILD_MANIFEST.exists()
    existing_config = REBUILD_CONFIG.exists()
    require(existing_run == existing_manifest == existing_config,
            "既有Run、输入清单和配置必须同时存在或同时缺失")
    if existing_run:
        require(REBUILD_RUN_DIR.is_dir() and not REBUILD_RUN_DIR.is_symlink(),
                f"既有Run目录类型错误：{REBUILD_RUN_DIR}")
        require(REBUILD_CONFIG.is_file() and not REBUILD_CONFIG.is_symlink() and
                REBUILD_MANIFEST.is_file() and not REBUILD_MANIFEST.is_symlink(),
                "既有Run配置或输入清单不是普通文件")
        observed_config = strict_json(REBUILD_CONFIG)
        observed_manifest = strict_json(REBUILD_MANIFEST)
        prepared_commit = observed_manifest.get("current_source_commit")
        require(type(prepared_commit) is str and re.fullmatch(r"[0-9a-f]{40}", prepared_commit),
                "既有Run输入清单缺少准备时的完整源码提交")
        subprocess.run(["git", "merge-base", "--is-ancestor", prepared_commit, current_head],
                       cwd=ROOT, check=True, capture_output=True)
        expected_manifest = dict(input_manifest)
        expected_manifest["current_source_commit"] = prepared_commit
        require(observed_manifest == expected_manifest,
                "既有Run输入清单的RunId、依赖绑定或来源不匹配")
        expected_config = dict(config)
        expected_config["source_commit"] = prepared_commit
        expected_config["platform_manifest_sha256"] = sha256(REBUILD_MANIFEST)
        require(observed_config == expected_config and
                observed_config.get("platform_manifest_sha256") == sha256(REBUILD_MANIFEST),
                "既有Run配置的来源提交、RunId路径或输入绑定不匹配")
        config = observed_config
        input_manifest = observed_manifest
        config_sha = sha256(REBUILD_CONFIG)
        manifest_sha = sha256(REBUILD_MANIFEST)
    else:
        require(not REBUILD_WORKSPACE.exists() and not REBUILD_ARTIFACT_DIR.exists(),
                "Run配置缺失但构建输出目录已存在，拒绝将其归入本次计划")
        require(REBUILD_RUN_DIR.parent.is_dir(),
                f"新Run输出父目录不存在：{REBUILD_RUN_DIR.parent}")
    return {
        "status": "REBUILD_CONFIG_PREPARED_NOT_RUN",
        "build_config_path": str(REBUILD_CONFIG),
        "build_config": config,
        "build_config_sha256": config_sha,
        "input_manifest_path": str(REBUILD_MANIFEST),
        "input_manifest": input_manifest,
        "input_manifest_sha256": manifest_sha,
        "xsa_contract_check": platform,
        "ddr_part_from_hwh": ddr_part,
        "vitis_build_started": False,
        "hardware_access": "NOT_RUN",
        "managed_launcher": {
            "script": str(ROOT / "verification/s2b_managed_vitis.py"),
            "command": [str(MANAGED_PYTHON), str(ROOT / "verification/s2b_managed_vitis.py"),
                        "--run-dir", str(REBUILD_RUN_DIR), "--vitis-bat", str(VITIS_BAT),
                        "--timeout-seconds", "600"],
            "python_executable": str(MANAGED_PYTHON),
            "vitis_bat": verify_bound(VITIS_BAT, sha256(VITIS_BAT), "Vitis launcher"),
        },
    }


def verify_t15_elfs() -> dict:
    """验证复用ELF的T15清单来源，并明确其构建XSA不是R04 XSA。"""
    delivery = T15 / "delivery_manifest.json"
    final_delivery = T15 / "final_delivery_manifest.json"
    build_path = T15 / "artifacts/build_details.json"
    app_path = T15 / "artifacts/infer.elf"
    init_path = T15 / "artifacts/init.elf"
    verify_bound(delivery, T15_DELIVERY_SHA, "T15 delivery manifest")
    verify_bound(final_delivery, T15_FINAL_DELIVERY_SHA, "T15 final delivery manifest")
    verify_bound(build_path, T15_BUILD_SHA, "T15 build_details")
    verify_bound(app_path, T15_APP_SHA, "T15 infer.elf")
    verify_bound(init_path, T15_INIT_SHA, "T15 init.elf")
    build = strict_json(build_path)
    require(build.get("status") == "PASS_OFFLINE_FULL_XSA_BUILD" and
            build.get("hardware_mode") == "FULL_PLATFORM_BOUND",
            "T15 build_details不符合预期")
    require(build.get("xsa_sha256") == T15_XSA_SHA and
            build.get("config", {}).get("xsa_sha256") == T15_XSA_SHA,
            "T15 ELF构建XSA摘要不符")
    require(build.get("elf", {}).get("sha256") == T15_APP_SHA and
            build.get("initializer_elf", {}).get("sha256") == T15_INIT_SHA,
            "T15 build_details未绑定当前ELF")
    return {
        "app_elf": {"path": str(app_path), "sha256": T15_APP_SHA},
        "init_elf": {"path": str(init_path), "sha256": T15_INIT_SHA},
        "build_details": {"path": str(build_path), "sha256": T15_BUILD_SHA,
                          "source_commit": build.get("source_commit")},
        "elf_build_xsa": {"path": build["config"]["xsa"], "sha256": T15_XSA_SHA},
        "r04_xsa_sha256": R04_XSA_SHA,
        "same_xsa_as_r04": False,
        "compatibility_status": "REVIEW_REQUIRED",
    }


def verify_model_assets() -> dict:
    """用冻结模型索引及transport loader逐行核验109个输入与权重。"""
    if str(ROOT / "verification") not in sys.path:
        sys.path.insert(0, str(ROOT / "verification"))
    import s2b_board_transport as transport

    prep = strict_json(MODEL_PREP)
    require(prep.get("status") == "NOT_RUN" and prep.get("hardware_execution") == "NOT_RUN" and
            len(prep.get("rows", [])) == 109,
            "模型资产准备记录状态或109行数量不符")
    require(prep.get("weights", {}).get("path") == str(ASSET_ROOT / "fixtures/common/weights.gf8"),
            "准备记录权重路径与固定资产根不符")
    weights_path, weights, rows = transport.load_assets(ASSET_ROOT, list(range(109)))
    require(len(rows) == 109, "冻结资产加载结果数量错误")
    weight_sha = transport.digest(weights)
    require(weight_sha == prep["weights"]["sha256"] and len(weights) == prep["weights"]["bytes"],
            "准备记录与冻结权重文件不一致")
    frozen_documents = (
        ("model_manifest", ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json",
         transport.MODEL_SHA),
        ("samples_manifest", ROOT / "report/evidence/S2A-T01/fixed_test_samples.json",
         transport.SAMPLES_SHA),
        ("golden_source", ROOT / "report/evidence/S2A-T29/cpu_decode_nms_reference.json",
         transport.CPU_D9_SHA),
    )
    checked_documents = {}
    for name, path, expected in frozen_documents:
        configured = prep.get(name, {})
        require(configured.get("sha256") == expected,
                f"模型准备记录中的{name}摘要不是冻结值")
        checked_documents[name] = verify_bound(path, expected, name)

    checked_references = []
    for index, row in enumerate(prep["rows"]):
        require(row.get("index") == index, f"准备记录样本序号不连续：{index}")
        ref = row.get("reference", {})
        ref_path = Path(ref.get("path", ""))
        require(ref_path.is_absolute() and ref_path.parent == MODEL_PREP.parent,
                f"黄金引用路径越界或不精确：{ref_path}")
        checked_references.append(verify_bound(ref_path, ref.get("sha256", ""), "样本黄金引用"))
    row0 = rows[0]
    require(row0["input_sha256"] == prep["rows"][0]["input"]["sha256"],
            "样本000输入绑定不一致")
    return {
        "asset_root": str(ASSET_ROOT),
        "weights": {"path": str(weights_path), "sha256": weight_sha, "bytes": len(weights)},
        **checked_documents,
        "sample_count_bound": len(rows),
        "sample000_input": {"path": str(row0["input_path"]), "sha256": row0["input_sha256"]},
        "sample000_golden_reference": checked_references[0],
        "reference_count_bound": len(checked_references),
        "source_preparation_record": {"path": str(MODEL_PREP), "sha256": sha256(MODEL_PREP)},
    }


def build_report() -> dict:
    """汇总离线绑定结果和不能被离线检查关闭的门禁。"""
    r04 = verify_r04()
    t15 = verify_t15_elfs()
    model = verify_model_assets()
    plan = rebuild_plan(r04, t15, model)
    return {
        "schema_version": 1,
        "record_type": "S2B_MODEL_QUALIFICATION_OFFLINE_BINDING_AUDIT",
        "status": "OFFLINE_BINDINGS_VERIFIED_REVIEW_REQUIRED",
        "hardware_execution": "NOT_RUN",
        "generated_by": "vitis/prepare_s2b_model_qualification_offline.py",
        "source_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                       check=True, capture_output=True, text=True).stdout.strip(),
        "r04_candidate": r04,
        "reused_t15_ps_software": t15,
        "frozen_tiny416_assets": model,
        "same_xsa_elf_rebuild_plan": plan,
        "qualification_gate": "NOT_PASSED",
        "qualification_entry_source": {
            "path": str(ROOT / "vitis/run_s2b_model_qualification.py"),
            "sha256": sha256(ROOT / "vitis/run_s2b_model_qualification.py"),
        },
        "offline_checker_source": {
            "path": str(Path(__file__).absolute()),
            "sha256": sha256(Path(__file__).absolute()),
        },
        "blockers": [
            "R04原input_record.json仍为FAIL；此记录保持原样。",
            "T15 infer.elf/init.elf绑定的构建XSA与R04含bit XSA不同；须由独立Reviewer明确核验该组合兼容性。",
            "已准备使用R04 XSA重新构建BSP、infer.elf和init.elf的全新Run配置；实际受控Vitis重建仍未运行。",
            "R04独立审查为有限范围的控制器转录，不构成新模型资格Reviewer原件。",
            "正式入口的Reviewer、G0、外部冷生命周期/POR及CORE/DRAIN期限测量锚点仍未固定；运行门禁继续fail-closed。",
            "板卡G0对应、PS初始化、DDR/HP0访问及模型运行均未在此离线检查中验证。",
        ],
        "not_authorized_by_this_record": [
            "不产生可供run_s2b_model_qualification.py硬件运行消费的资格收据。",
            "不授权JTAG、PS初始化、DDR/HP0、UART、volatile部署或永久烧录。",
            "不代表单样本、109样本、1000连续任务、异常恢复或G3/G4/G5通过。",
        ],
    }


def write_json_new(path: Path, value: dict) -> None:
    """仅新建UTF-8/LF证据文件，拒绝覆盖。"""
    require(path.is_absolute(), "证据文件必须使用绝对路径")
    require(not path.exists(), f"拒绝覆盖已有证据：{path}")
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main(argv: list[str] | None = None) -> int:
    """命令行只读检查；--write-evidence仅新建固定RunId证据。"""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-evidence", action="store_true",
                        help="将通过的离线绑定审计写入固定的新证据路径；拒绝覆盖")
    args = parser.parse_args(argv)
    try:
        report = build_report()
        if args.write_evidence:
            require(not OUTPUT.exists() and not REBUILD_MANIFEST.exists() and
                    not REBUILD_RUN_DIR.exists() and not REBUILD_CONFIG.exists(),
                    "目标Run证据或配置已有文件，拒绝覆盖")
            require(not REBUILD_WORKSPACE.exists() and not REBUILD_ARTIFACT_DIR.exists(),
                    "构建输出目标已有文件，拒绝覆盖")
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            plan = report["same_xsa_elf_rebuild_plan"]
            REBUILD_RUN_DIR.mkdir()
            write_json_new(REBUILD_MANIFEST, plan["input_manifest"])
            write_json_new(REBUILD_CONFIG, plan["build_config"])
            write_json_new(OUTPUT, report)
            report["evidence_path"] = str(OUTPUT)
        print(json.dumps({"status": report["status"],
                          "hardware_execution": report["hardware_execution"],
                          "blocker_count": len(report["blockers"]),
                          **({"evidence_path": report["evidence_path"]} if "evidence_path" in report else {})},
                         ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "OFFLINE_BINDING_BLOCKED", "error": repr(exc)},
                         ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
