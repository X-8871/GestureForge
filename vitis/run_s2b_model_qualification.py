"""单样本模型资格入口；显式配置与独立资格收据齐备后才允许易失部署。

只允许 sample000、frame0、repeat1；不会执行正式100/1000验收。导入、
--help和--preflight不加载SDK/串口。外部POR与期间独占链必须另行审查，
任何缺失均阻断；system-stop始终不被称为POR。收据的角色字符串不能
创造独立来源，必须由总控固定真实Reviewer原件及SHA。
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import ast
import argparse
import hashlib
import importlib
import json
import os
import re
import struct
import subprocess
import sys
import time
import traceback
import zipfile

ROOT = Path(__file__).absolute().parents[1]
TZ = timezone(timedelta(hours=8))
SCOPE = "visibility1_sample000_single_job"
XSA_SHA = "ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6"
BIT_SHA = "555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7"
BUILD_SHA = "59c42968085d656148de9aec13f4c9e623b7688fc79101038f2b661510c5c0db"
APP_SHA = "a51499895e9387a74db87a3267843b9fbf7fdfa8b6646fcbc5db01485e090bf8"
INIT_SHA = "237dd959f903589c657b743ea1fce175628aaa24020384058fc66339c779e7b1"
GOLDEN_SHA = "090b1422f8e8d4d22124568af9778ba7bd5e7168407c0125e1e729d4a5a46f80"
CONFIG_KEYS = {"schema_version", "source_commit", "run_dir", "build_details", "bindings",
               "owned_hw_server_identity", "uart_identity", "cold_basis", "sdk_files", "pyserial_files",
               "asset_root", "qualification_receipt", "sample_index", "frame", "repeat",
               "core_timeout_cycles", "drain_timeout_cycles", "response_timeout_seconds",
               "g0_basis", "timeout_basis"}
REVIEW_CHECKS = {"hwh_hp0_nonbufferable_adapter0", "new_elf_gp0_device_contract",
                 "controlled_startup_same_xsa", "single_job_arena_cache_retention", "postroute_timing"}
RECEIPT_KEYS = {"schema_version", "kind", "role", "status", "scope", "visibility_parameter",
                "source_commit", "reviewer_task", "manual_trust_root",
                "entry_digest_scheme", "canonical_entry_sha256_v1",
                "source_sha256", "artifacts", "checks", "lifecycle"}
ENTRY_DIGEST_SCHEME = "s2b-model-qualification-entry-canonical-sha256-v1"
ANCHOR_ASSIGNMENT_PREFIX = b"TRUSTED_REVIEW_ANCHOR = "
ANCHOR_CANONICAL_VALUE = b"<NORMALIZED_TRUSTED_REVIEW_ANCHOR_V1>"
MANUAL_REVIEWER_TASK = "/root/ps_build_r02_review"
QUALIFICATION_REVIEWER_TASK = "/root/qualification_single_sample_review"
MANUAL_REVIEW_SOURCE_COMMIT = "37c4b840977e727b6504d83b803da3358f89040e"
MANUAL_REVIEW_SCOPE = "visibility0_cache_probe_only"
MANUAL_REVIEW_PROVENANCE = {
    "path": "C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition/report/evidence/S2B-T19/current_probe_independent_20261015_r01/review_provenance.json",
    "sha256": "c87a2f40a099bdce0fce127af7d3c3282f4b2442e19dbc9da4f299b588321ce5",
}
MANUAL_RUNTIME_COMPATIBILITY = {
    "path": "C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition/report/evidence/S2B-T19/current_probe_independent_20261015_r01/runtime_compatibility_receipt.json",
    "sha256": "e22fd0a1fa0399de48d9694dd07c7b10e06dbb60f55aed7ce8a9057fc3d4c7ea",
}
MANUAL_PLATFORM_MANIFEST = {
    "path": "C:\\Users\\22061\\.codex\\worktrees\\96a3\\FPGA_Competition\\report\\evidence\\S2B-T19\\current_probe_scope_20261015_r01\\platform_delivery_manifest.json",
    "sha256": "5548bb56e6a68e9a02cda4a93b8b5440ded86245a1d351103d6a7144c76676bf",
}
# 迁盘只改变读取位置；Wong批准的原始路径、摘要和收据内引用保持原样。
MANUAL_ROOT_STORAGE = {
    MANUAL_REVIEW_PROVENANCE["path"]: "D:/codex-worktrees/96a3/report/evidence/S2B-T19/current_probe_independent_20261015_r01/review_provenance.json",
    MANUAL_RUNTIME_COMPATIBILITY["path"]: "D:/codex-worktrees/96a3/report/evidence/S2B-T19/current_probe_independent_20261015_r01/runtime_compatibility_receipt.json",
}
MANUAL_TRUST_ROOT_CLAIM = {
    "kind": "s2b-manual-review-trust-root/1.0.0",
    "reviewer_task": MANUAL_REVIEWER_TASK,
    "source_commit": MANUAL_REVIEW_SOURCE_COMMIT,
    "scope": MANUAL_REVIEW_SCOPE,
    "review_provenance": MANUAL_REVIEW_PROVENANCE,
    "runtime_compatibility_receipt": MANUAL_RUNTIME_COMPATIBILITY,
}

# 该Reviewer原件只作为Wong批准的人工信任依据；它不是密码签名，也不证明本资格收据已获审查。
# canonical v1只规范化本行来打破收据SHA与入口SHA的循环；其余入口原字节均参与SHA。
# 两份固定外部原件必须各自匹配SHA、schema、角色、范围与交叉绑定；运行配置不能替换信任根。
# 该根仅覆盖visibility0静态探测且硬件NOT_RUN；G0候选审查与官方POR语义分别由下方固定锚点绑定。
# 首个受控sample000按冻结规程使用有限最大期限；最终部署期限仍须在G4/G5量化。
TRUSTED_REVIEW_ANCHOR = {'path': 'D:\\FPGA_Competition\\w2b\\report\\evidence\\S2B-T19\\qualification_single_sample_review_20261018_r02\\qualification_receipt.json', 'sha256': 'f0b3dbfbb300de550ee11f4b455f263b9d50365cd6d1021e6e06692eb61a2ea9'}
TRUSTED_G0_ANCHOR = {
    'path': 'report/evidence/S2B-T19/g0_board_candidate_scope_20261017_r02/independent_g0_review_outcome.json',
    'sha256': '0540f3ab8d7e27b87a739c520f5228bb3b9186e2733e9fb6bb2d6bec05accc53',
}
TRUSTED_COLD_ANCHOR = {
    'path': 'D:\\FPGA_Competition\\w2b\\report\\evidence\\S2B-T19\\official_reset_basis_20261011_r01\\cold_reset_basis_candidate.json',
    'sha256': '2f13aaa73f526e658008dab879df82a90c37a1109eb5c9295924984272b118c3',
}


class QualificationError(RuntimeError):
    """门禁或运行失败，禁止下一任务及arena复用。"""


def require(condition, message):
    """优化模式下仍执行的门禁。"""
    if not condition:
        raise QualificationError(message)


def helpers():
    """仅导入已有无硬件副作用的项目封装。"""
    directory = str(ROOT / "vitis")
    if directory not in sys.path:
        sys.path.insert(0, directory)
    probe = importlib.import_module("run_s2b_visibility_probe")
    jtag, transport = probe.helpers()
    return probe, jtag, transport


def integer(value, low, high, label):
    """拒绝bool、浮点和越界值。"""
    require(type(value) is int and low <= value <= high, label + "必须为范围内整数")
    return value


def read_trusted_review_anchor(path):
    """读取唯一单行可信锚点赋值；锚点只能是None或精确路径/SHA字面量。"""
    raw = Path(path).read_bytes()
    assignments = list(re.finditer(rb"(?m)^[ \t]*TRUSTED_REVIEW_ANCHOR[ \t]*=", raw))
    require(len(assignments) == 1, "入口必须恰有一个可信Reviewer锚点赋值")
    match = re.search(rb"(?m)^TRUSTED_REVIEW_ANCHOR = ([^\r\n]*)(\r?\n|$)", raw)
    require(match is not None and match.start() == assignments[0].start(),
            "可信Reviewer锚点必须使用单行精确赋值格式")
    try:
        value = ast.literal_eval(match.group(1).decode("utf-8"))
    except (SyntaxError, ValueError, UnicodeDecodeError) as exc:
        raise QualificationError("可信Reviewer锚点必须是安全的Python字面量") from exc
    require(value is None or (type(value) is dict and set(value) == {"path", "sha256"} and
            type(value["path"]) is str and type(value["sha256"]) is str and
            re.fullmatch(r"[0-9a-f]{64}", value["sha256"])),
            "可信Reviewer锚点必须是None或精确路径/SHA绑定")
    return value


def canonical_entry_sha256(path):
    """仅规范化单行Reviewer锚点赋值，其余入口原字节全部参与SHA-256。"""
    raw = Path(path).read_bytes()
    read_trusted_review_anchor(path)
    match = re.search(rb"(?m)^TRUSTED_REVIEW_ANCHOR = ([^\r\n]*)(\r?\n|$)", raw)
    require(match is not None, "缺少可信Reviewer锚点赋值")
    normalized = ANCHOR_ASSIGNMENT_PREFIX + ANCHOR_CANONICAL_VALUE + match.group(2)
    canonical = raw[:match.start()] + normalized + raw[match.end():]
    return hashlib.sha256(canonical).hexdigest()


def require_reviewed_entry_digest(receipt, path):
    """核对版本化入口摘要，保证锚点行外的任一原字节变化均失败。"""
    require(receipt.get("entry_digest_scheme") == ENTRY_DIGEST_SCHEME and
            receipt.get("canonical_entry_sha256_v1") == canonical_entry_sha256(path),
            "资格入口canonical digest漂移或schema不兼容")


def binding(item):
    """绑定精确文件及原字节SHA，不能使用相似路径。"""
    p, j, _ = helpers()
    require(type(item) is dict and set(item) == {"path", "sha256"}, "文件绑定字段错误")
    require(type(item["path"]) is str and type(item["sha256"]) is str and
            re.fullmatch(r"[0-9a-f]{64}", item["sha256"]), "文件绑定类型错误")
    path = j.exact_path(item["path"])
    require(p.digest(path) == item["sha256"], "文件SHA漂移：" + str(path))
    return path


def document(item):
    """所有JSON层次拒重复键及NaN，限制小型审计文档规模。"""
    p, _, _ = helpers()
    path = binding(item)
    require(path.stat().st_size <= 4 * 1024 * 1024, "JSON输入超过4MiB")
    return p.strict_json(path.read_text(encoding="utf-8"))


def fixed_manual_root_document(item, expected):
    """从固定迁移位置读取人工根，保留原引用并核验原字节SHA。"""
    require(type(item) is dict and item == expected, "BLOCKED：人工根路径/SHA不能由配置选择")
    storage = MANUAL_ROOT_STORAGE.get(item["path"])
    require(storage is not None, "BLOCKED：人工根没有固定迁移位置")
    path = Path(storage)
    require(path.is_absolute() and ".." not in path.parts and not any(c in str(path) for c in "*?[]"),
            "BLOCKED：人工根路径必须是精确绝对路径")
    try:
        resolved = path.resolve(strict=True)
        normalized = str(resolved).replace("\\", "/")
        require(normalized == storage, "BLOCKED：人工根路径实际名称/链接解析不符")
        current = Path(path.anchor)
        for name in path.parts[1:]:
            current = current / name
            metadata = current.stat(follow_symlinks=False)
            require(not current.is_symlink() and
                    not (getattr(metadata, "st_file_attributes", 0) & 0x400),
                    "BLOCKED：人工根路径包含链接或重解析点")
        require(path.is_file() and path.stat().st_size <= 4 * 1024 * 1024,
                "BLOCKED：人工根JSON缺失、类型错误或超过4MiB")
        raw = path.read_bytes()
    except OSError as exc:
        raise QualificationError("BLOCKED：无法只读访问固定人工根原件") from exc
    require(hashlib.sha256(raw).hexdigest() == item["sha256"], "BLOCKED：固定人工根SHA漂移")
    p, _, _ = helpers()
    return p.strict_json(raw.decode("utf-8"))


def validate_manual_review_root_documents(provenance, compatibility):
    """核验Wong指定的两份人工信任原件及其平台清单交叉绑定。"""
    require(type(provenance) is dict and type(compatibility) is dict,
            "BLOCKED：人工Reviewer根必须是两个JSON对象")
    require(provenance.get("schema_version") == 1 and type(provenance.get("schema_version")) is int and
            provenance.get("kind") == "s2b-independent-review-provenance/1.0.0" and
            provenance.get("reviewer_task") == MANUAL_REVIEWER_TASK and
            provenance.get("role") == "INDEPENDENT_REVIEWER" and
            provenance.get("source_commit") == MANUAL_REVIEW_SOURCE_COMMIT and
            provenance.get("verdict") == "PASS" and provenance.get("scope") == MANUAL_REVIEW_SCOPE,
            "BLOCKED：固定review provenance schema/角色/身份/范围不符")
    facts = provenance.get("independent_raw_facts")
    require(type(facts) is dict and facts.get("status") == "INDEPENDENT_RAW_FACTS_PASS" and
            facts.get("dynamic_hardware") == "NOT_RUN" and
            provenance.get("hardware_execution") == "NOT_RUN",
            "BLOCKED：人工Reviewer根的动态硬件状态必须明确为NOT_RUN")
    reviewed = provenance.get("frozen_reviewed_inputs")
    platform_key = "report/evidence/S2B-T19/current_probe_scope_20261015_r01/platform_delivery_manifest.json"
    require(type(reviewed) is dict and reviewed.get(platform_key) == MANUAL_PLATFORM_MANIFEST["sha256"],
            "BLOCKED：review provenance未绑定固定平台清单")
    require(compatibility.get("schema_version") == 1 and type(compatibility.get("schema_version")) is int and
            compatibility.get("kind") == "s2b-runtime-platform-compatibility/1.0.0" and
            compatibility.get("role") == "INDEPENDENT_REVIEWER" and
            compatibility.get("status") == "PASS" and compatibility.get("scope") == MANUAL_REVIEW_SCOPE and
            type(compatibility.get("visibility_parameter")) is int and compatibility.get("visibility_parameter") == 0,
            "BLOCKED：固定runtime compatibility schema/角色/范围不符")
    artifacts = compatibility.get("artifacts")
    require(type(artifacts) is dict and artifacts.get("platform_manifest") == MANUAL_PLATFORM_MANIFEST,
            "BLOCKED：runtime compatibility未绑定固定平台清单原件")
    return MANUAL_TRUST_ROOT_CLAIM


def validate_manual_review_trust_root():
    """读取两份源码固定的原件；配置文件不能选择或替换根文件。"""
    provenance = fixed_manual_root_document(MANUAL_REVIEW_PROVENANCE, MANUAL_REVIEW_PROVENANCE)
    compatibility = fixed_manual_root_document(MANUAL_RUNTIME_COMPATIBILITY,
                                               MANUAL_RUNTIME_COMPATIBILITY)
    return validate_manual_review_root_documents(provenance, compatibility)


def validate_qualification_reviewer_claim(receipt):
    """要求资格收据绑定独立资格Reviewer身份及完整人工信任根。"""
    require(type(receipt) is dict and receipt.get("reviewer_task") == QUALIFICATION_REVIEWER_TASK,
            "BLOCKED：资格收据Reviewer task身份不匹配")
    require(receipt.get("manual_trust_root") == MANUAL_TRUST_ROOT_CLAIM,
            "BLOCKED：资格收据缺少或更换固定人工信任根引用")


def validate_config(cfg):
    """先验证窄范围与期限，再读取资产或调用项目检查器。"""
    require(type(cfg) is dict and set(cfg) == CONFIG_KEYS, "qualification config字段错误")
    integer(cfg["schema_version"], 1, 1, "schema_version")
    for key, value in (("sample_index", 0), ("frame", 0), ("repeat", 1)):
        integer(cfg[key], value, value, key)
    for key in ("core_timeout_cycles", "drain_timeout_cycles"):
        integer(cfg[key], 1, 0xFFFFFFFF, key)
    require(cfg["timeout_basis"] is None and
            cfg["core_timeout_cycles"] == 0xFFFFFFFF and
            cfg["drain_timeout_cycles"] == 0xFFFFFFFF,
            "首个受控样本必须使用冻结规程规定的最大有限上限，不接受未审核期限依据")
    integer(cfg["response_timeout_seconds"], 450, 450, "response_timeout_seconds")
    for key, anchor in (("g0_basis", TRUSTED_G0_ANCHOR),):
        item = cfg[key]
        if item is None:
            require(anchor is None, key + "缺少已固定的依据")
            continue
        require(type(item) is dict and set(item) == {"path", "sha256"} and
                type(item["path"]) is str and type(item["sha256"]) is str and
                re.fullmatch(r"[0-9a-f]{64}", item["sha256"]), key + "必须是完整文件绑定")
    require(type(cfg["source_commit"]) is str and re.fullmatch(r"[0-9a-f]{40}", cfg["source_commit"]), "需要完整源码基线")
    uart = cfg["uart_identity"]
    if uart is None:
        require(TRUSTED_REVIEW_ANCHOR is None,
                "UART身份缺失且Reviewer锚点已固定")
        return
    require(type(uart) is dict and set(uart) == {"port", "name", "pnp_device_id", "config_manager_error_code"}
            and uart["port"] == "COM4" and type(uart["config_manager_error_code"]) is int
            and uart["config_manager_error_code"] == 0 and type(uart["name"]) is str
            and uart["name"].endswith("(COM4)") and type(uart["pnp_device_id"]) is str
            and bool(uart["pnp_device_id"]), "COM4身份格式错误")


def hardware_enablement_gaps(cfg):
    """返回未固定或配置不匹配的各项部署信任锚点。"""
    gaps = []
    anchors = (
        ("TRUSTED_REVIEW_ANCHOR", TRUSTED_REVIEW_ANCHOR, cfg.get("qualification_receipt"),
         "当前visibility=1单样本资格范围的独立Reviewer回执路径及SHA，须独立审查当前入口digest、R04 XSA/bit/build/ELF、模型输入与兼容性"),
        ("TRUSTED_G0_ANCHOR", TRUSTED_G0_ANCHOR, cfg.get("g0_basis"),
         "针对XC7Z020-2CLG400I及当前PCB/DDR资料、接口版本、部署范围和正式验收标准的批准依据路径及SHA"),
        ("TRUSTED_COLD_ANCHOR", TRUSTED_COLD_ANCHOR, cfg.get("cold_basis"),
         "操作者签认的外部POR记录及POR后独占保管/无HP探针证据链路径和SHA，时间须为UTC+8"),
    )
    for name, anchor, configured, needed in anchors:
        if anchor is None:
            gaps.append({"anchor": name, "status": "MISSING", "required_evidence": needed})
        elif configured != anchor:
            gaps.append({"anchor": name, "status": "CONFIGURATION_MISMATCH",
                         "required_evidence": "配置必须逐字匹配源码固定的路径与SHA"})
    return gaps


def require_hardware_enablement(cfg):
    """硬件门要求固定人工根、入口锚点和外部依据；缺项即阻断。"""
    source_anchor = read_trusted_review_anchor(Path(__file__))
    require(source_anchor == TRUSTED_REVIEW_ANCHOR,
            "BLOCKED：入口内Reviewer锚点与已加载源码值不一致")
    gaps = hardware_enablement_gaps(cfg)
    require(not gaps, "BLOCKED：缺少部署信任锚点：" +
            json.dumps(gaps, ensure_ascii=False, separators=(",", ":")))
    require(cfg["qualification_receipt"] == TRUSTED_REVIEW_ANCHOR,
            "BLOCKED：配置与总控固定的独立Reviewer原件锚点不一致")
    validate_manual_review_trust_root()
    review = document(cfg["qualification_receipt"])
    validate_qualification_reviewer_claim(review)
    rows = (("正式G0依据", TRUSTED_G0_ANCHOR, cfg["g0_basis"]),
            ("外部POR/冷生命周期依据", TRUSTED_COLD_ANCHOR, cfg["cold_basis"]))
    for label, anchor, configured in rows:
        require(type(anchor) is dict and set(anchor) == {"path", "sha256"},
                "BLOCKED：缺少总控固定的" + label + "锚点；运行配置不可自行授权")
        require(configured == anchor, "BLOCKED：配置与总控固定的" + label + "锚点不一致")


def verify_review(cfg, build, actual_sources):
    """限定收据绑定实际源码、产物及独立检查原件，不能继承visibility0批准。"""
    require_hardware_enablement(cfg)
    p, j, _ = helpers()
    receipt = document(cfg["qualification_receipt"])
    require(type(receipt) is dict and set(receipt) == RECEIPT_KEYS, "缺少typed qualification receipt")
    integer(receipt["schema_version"], 2, 2, "receipt schema")
    integer(receipt["visibility_parameter"], 1, 1, "visibility")
    require(receipt["kind"] == "s2b-single-model-qualification/2.0.0" and
            receipt["role"] == "INDEPENDENT_REVIEWER" and receipt["status"] == "PASS" and
            receipt["scope"] == SCOPE, "独立收据范围/状态不符")
    validate_qualification_reviewer_claim(receipt)
    require(receipt["source_commit"] == cfg["source_commit"] and
            receipt["source_sha256"] == actual_sources, "33文件源码闭包漂移")
    require_reviewed_entry_digest(receipt, Path(__file__))
    artifacts = receipt["artifacts"]
    require(type(artifacts) is dict and set(artifacts) == {"compiled_xsa", "bit", "app_elf", "init_elf", "build_details", "platform_manifest"}, "资格产物字段错误")
    expected = {key: cfg["bindings"][key] for key in ("bit", "app_elf", "init_elf")}
    expected.update(compiled_xsa=cfg["bindings"]["xsa"], build_details=cfg["build_details"],
                    platform_manifest={"path": build["config"]["platform_manifest"], "sha256": build["config"]["platform_manifest_sha256"]})
    require(artifacts == expected, "资格收据与当前vis1完整构建不一致")
    for item in artifacts.values():
        binding(item)
    checks = receipt["checks"]
    require(type(checks) is dict and set(checks) == REVIEW_CHECKS, "资格审计缺项")
    for name, check in checks.items():
        require(type(check) is dict and set(check) == {"status", "evidence"} and check["status"] == "PASS", "资格审计未通过：" + name)
        binding(check["evidence"])
    lifecycle = receipt["lifecycle"]
    require(type(lifecycle) is dict and set(lifecycle) == {"method", "operator_por_confirmation", "custody_chain", "last_probe"}
            and lifecycle["method"] == "EXTERNAL_POR_WITH_EXCLUSIVE_CUSTODY", "BLOCKED：缺外部POR及独占链，SDK复位不能替代")
    # 人工来源必须由真实Reviewer核查；本入口只核对绑定，绝不生成确认或审查PASS。
    operator = document(lifecycle["operator_por_confirmation"])
    require(type(operator) is dict and set(operator) == {"kind", "operator", "time_utc8", "statement", "source"}
            and operator["kind"] == "external-por-operator-confirmation/1.0.0" and operator["operator"] == "Wong"
            and type(operator["statement"]) is str and operator["statement"].strip(), "BLOCKED：没有可追踪的operator POR原件")
    binding(operator["source"])
    por_time = datetime.fromisoformat(operator["time_utc8"])
    require(por_time.utcoffset() == timedelta(hours=8), "POR时间必须显式UTC+8")
    chain = document(lifecycle["custody_chain"])
    require(type(chain) is dict and set(chain) == {"kind", "scope", "run_dir", "operator_confirmation", "last_probe", "exclusive_until_utc8", "events"}
            and chain["kind"] == "s2b-exclusive-board-custody/1.0.0" and chain["scope"] == SCOPE
            and chain["run_dir"] == cfg["run_dir"] and chain["operator_confirmation"] == lifecycle["operator_por_confirmation"]
            and chain["last_probe"] == lifecycle["last_probe"], "BLOCKED：独占链未绑定本次单任务")
    until = datetime.fromisoformat(chain["exclusive_until_utc8"])
    require(until.utcoffset() == timedelta(hours=8) and datetime.now(TZ) < until, "BLOCKED：独占板卡保管期限已过")
    events = chain["events"]
    require(type(events) is list and events, "BLOCKED：POR至本次启动之间没有可审计事件链")
    previous = por_time
    for event in events:
        require(type(event) is dict and set(event) == {"time_utc8", "action", "evidence"} and
                event["action"] in {"EXTERNAL_POR", "CPU_DAP_CACHE_PROBE_NO_HP", "EXCLUSIVE_CUSTODY_NO_HP"}, "BLOCKED：独占链包含未知动作/HP任务")
        stamp = datetime.fromisoformat(event["time_utc8"])
        require(stamp.utcoffset() == timedelta(hours=8) and previous <= stamp <= datetime.now(TZ), "独占链时间错误")
        binding(event["evidence"])
        previous = stamp
    require(events[0]["action"] == "EXTERNAL_POR" and events[0]["evidence"] == lifecycle["operator_por_confirmation"]
            and events[-1]["action"] == "EXCLUSIVE_CUSTODY_NO_HP", "BLOCKED：独占链端点不完整")
    probe_result = document(lifecycle["last_probe"])
    require(probe_result.get("native_exit_code") == 0 and type(probe_result.get("native_exit_code")) is int
            and probe_result.get("status") == "API_OBSERVATIONS_SAVED_ACCEPTANCE_PENDING"
            and probe_result.get("cold_lifecycle_proven") is False and probe_result.get("cleanup_errors") == []
            and probe_result.get("serial_closed") is True, "BLOCKED：前置探针失败或生命周期被改写")
    tx = [e for e in probe_result.get("uart_events", []) if e.get("direction") == "TX"]
    require(len(tx) == 2 and [e.get("sequence") for e in tx] == [1, 2] and
            all(e.get("op") == 4 and e.get("status") == "SENT_TO_SERIAL_DRIVER" for e in tx), "BLOCKED：前置探针不是仅两次无HP缓存动作")
    probe_time = datetime.fromisoformat(probe_result["finished_at_utc8"])
    require(por_time <= probe_time <= previous and any(e["action"] == "CPU_DAP_CACHE_PROBE_NO_HP" and
            e["evidence"] == lifecycle["last_probe"] for e in events), "BLOCKED：探针不在POR保管链内")
    require_idle({int(k): v for k, v in probe_result["final_csr"].items()}, 0)
    return receipt


def verify_static_candidate_bindings(cfg):
    """只读核对R04候选构建、源码闭包及样本000黄金；不访问板卡或SDK。"""
    validate_config(cfg)
    p, j, t = helpers()
    observed = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True).stdout.decode("ascii").strip()
    subprocess.run(["git", "merge-base", "--is-ancestor", cfg["source_commit"], observed], cwd=ROOT, check=True, capture_output=True)
    bindings = cfg["bindings"]
    required = {"init_elf", "app_elf", "xsa", "bit", "csr_source", "interface", "sdk_target", "tool_source", "elf_parser", "delivery_parser", "transport_source", "entry_source", "platform_checker", "sdk_init", "pyserial_init"}
    require(type(bindings) is dict and set(bindings) == required, "运行闭包绑定缺项")
    for key, item in bindings.items():
        if key not in {"sdk_init", "sdk_target", "pyserial_init"}:
            binding(item)
    for key, sha in (("tool_source", p.JTAG_SHA), ("xsa", XSA_SHA), ("bit", BIT_SHA), ("app_elf", APP_SHA), ("init_elf", INIT_SHA)):
        require(bindings[key]["sha256"] == sha, "冻结产物错误：" + key)
    for key, path in (("entry_source", Path(p.__file__)), ("tool_source", Path(j.__file__)),
                      ("transport_source", Path(t.__file__)), ("platform_checker", ROOT / "verification/check_s2b_inference_platform.py"),
                      ("csr_source", ROOT / "src/s2b_control_csr.sv"), ("interface", ROOT / "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"),
                      ("elf_parser", ROOT / "verification/check_s2b_ps_smoke_layout.py"), ("delivery_parser", ROOT / "verification/check_stage_delivery.py")):
        require(j.exact_path(bindings[key]["path"]) == j.exact_path(path), "实际运行来源未绑定：" + key)
    require(cfg["build_details"]["sha256"] == BUILD_SHA, "build_details不匹配R04固定候选")
    binding(cfg["build_details"])
    _, build = t.verify_build(cfg["build_details"]["path"])
    for key, item in (("app_elf", build["elf"]), ("init_elf", build["initializer_elf"]),
                      ("xsa", {"path": build["config"]["xsa"], "sha256": build["xsa_sha256"]})):
        require(bindings[key] == {k: item[k] for k in ("path", "sha256")}, "构建绑定不符：" + key)
    with zipfile.ZipFile(binding(bindings["xsa"])) as archive:
        bits = [name for name in archive.namelist() if name.endswith(".bit")]
        require(len(bits) == 1 and hashlib.sha256(archive.read(bits[0])).hexdigest() == BIT_SHA, "下载bit与编译XSA内bit不同")
    postconfig = j.postconfig_basis(j.bound_bytes(bindings["xsa"]))
    checker = importlib.import_module("check_s2b_inference_platform")
    require(j.exact_path(checker.__file__) == binding(bindings["platform_checker"]), "平台checker来源错误")
    sources = checker.check_static(ROOT)
    weight_path, weights, rows = t.load_assets(cfg["asset_root"], [0])
    row = rows[0]
    golden_path = t.exact_path(row["asset_root"] / "fixtures/sample_000/golden_unique.bin")
    require(golden_path.stat().st_size == 11382150 and p.digest(golden_path) == GOLDEN_SHA,
            "冻结黄金完整流错误")
    return {"build": build, "source_commit": observed, "sources": sources,
            "postconfig_basis": postconfig, "weight_path": weight_path,
            "weights": weights, "row": row, "golden_path": golden_path}


def preflight(cfg):
    """静态输入检查后报告全部缺失信任锚点；不会导入SDK或触碰硬件。"""
    static = verify_static_candidate_bindings(cfg)
    require_hardware_enablement(cfg)
    p, j, t = helpers()
    build = static["build"]
    sources = static["sources"]
    observed = static["source_commit"]
    postconfig = static["postconfig_basis"]
    receipt = verify_review(cfg, build, sources)
    p.verify_sdk_files(cfg)
    p.verify_serial_files(cfg)
    require(j.bound_bytes(cfg["cold_basis"]), "缺官方复位范围依据")
    server = document(cfg["owned_hw_server_identity"])
    require(server.get("status") == "OWNED_SERVER_READY" and type(server.get("native")) is dict, "服务归属未就绪")
    native = server["native"]
    require(type(native.get("ProcessId")) is int and native["ProcessId"] > 0 and
            re.fullmatch(r"[0-9]+", str(native.get("CreationTimeFileTimeUtc", ""))), "服务PID/创建时刻错误")
    executable = j.exact_path(native["ExecutablePath"])
    require(executable.name == "hw_server.exe" and p.digest(executable) == server["native_sha256"], "服务原生程序漂移")
    return {"build": build, "server": server, "weights": static["weights"],
            "weight_path": static["weight_path"],
            "row": static["row"], "receipt": receipt, "source_commit": observed,
            "postconfig_basis": postconfig}


def require_idle(snapshot, epoch):
    """公开CSR完整稳定快照须为同epoch、ownerPS、SAFE及空账本。"""
    require(type(snapshot) is dict and all(type(v) is int for v in snapshot.values()), "CSR必须为实际整数")
    expected = {0: 0x53324250, 4: 0x100, 0x00C: 0x400, 0x010: 0,
                0x050: epoch & 0xFFFFFFFF, 0x054: epoch >> 32, 0x058: 0,
                0x064: 0, 0x068: 0, 0x06C: 0, 0x070: 0, 0x074: 0}
    require(all(snapshot.get(k) == v for k, v in expected.items()), "ACK未回到同epoch稳定IDLE/SAFE/ownerPS/账本0")


class ProgressSerial:
    """串口真实短写进度立即落盘；持久化失败即失败，不伪造发送计数。"""
    def __init__(self, port, stream):
        self.port, self.stream, self.total = port, stream, 0
        self.last_sync = 0.0

    def read(self, count):
        """原样委托已绑定串口。"""
        return self.port.read(count)

    def write(self, raw):
        """仅已返回的真实写字节计数；每块flush，每秒fsync。"""
        count = self.port.write(raw)
        require(type(count) is int and 0 < count <= len(raw), "串口无进展/错误短写返回")
        self.total += count
        now = time.monotonic()
        self.stream.write(json.dumps({"monotonic_seconds": now, "written_bytes": count, "total_written_bytes": self.total}) + "\n")
        self.stream.flush()
        if now - self.last_sync >= 1:
            os.fsync(self.stream.fileno())
            self.last_sync = now
        return count


def make_wire(jtag, port, progress, rx, tx, cfg):
    """把经过类型门限的秒值作为UART观察期限唯一来源。"""
    return jtag.JtagWireSession(ProgressSerial(port, progress), rx, tx,
                                response_timeout=cfg["response_timeout_seconds"])


def single_job(cfg, prepared, controller, wire, folder, record):
    """一次WEIGHTS、一次RUN、一次mode0；任何错误锁存，不重发、不复用arena。"""
    p, j, t = helpers()
    require(type(wire) is j.JtagWireSession and not wire.failed and wire.last_sequence == 0 and wire.epoch == 0, "必须是本次真实且未使用的T16串口会话")
    try:
        controller.gate(both=False)
        require_idle(controller.stable_csr("before_weights"), 0)
        row = prepared["row"]
        reference = t.reference_row(folder, row)
        p.save(folder / "reference.json", reference)
        payload = prepared["weights"]
        request, header = t.make_request(t.OP_WEIGHTS, 1, 0, payload)
        wire.send(request, header, payload, {"path": str(prepared["weight_path"]), "sha256": hashlib.sha256(payload).hexdigest()})
        record["weights_meta"], _, _ = wire.receive(request, 0)
        require_idle(controller.stable_csr("weights_idle_epoch0"), 0)
        payload = struct.pack("<II", cfg["core_timeout_cycles"], cfg["drain_timeout_cycles"]) + row["input_path"].read_bytes()
        width, height = row["golden"]["input"]["geometry_wh"]
        request, header = t.make_request(t.OP_RUN, 2, 0, payload, width=width, height=height, repeat=1)
        record["run_send_started_monotonic"] = time.monotonic()
        wire.send(request, header, payload, {"path": str(row["input_path"]), "sha256": row["input_sha256"]})
        record["run_send_returned_monotonic"] = time.monotonic()
        meta, heads, boxes = wire.receive(request, 0)
        record["run_response_received_monotonic"] = time.monotonic()
        record["run_meta"] = meta
        # 在比较前保存全部真实头与框，黄金不符也不丢失第二个头或框。
        p.save(folder / "observed_boxes.json", {"meta": meta, "detections": boxes})
        for name, raw in heads.items():
            with (folder / ("observed_" + name + ".bin")).open("xb") as output:
                output.write(raw)
        record["capture"] = t.capture_row(folder, row, 0, heads, boxes)
        p.save(folder / "capture.json", record["capture"])
        require(wire.epoch == 1 and wire.last_sequence == 2, "单任务epoch/sequence错误")
        payload = struct.pack("<III", 0, 0, 0)
        request, header = t.make_request(t.OP_DIAG, 3, 0, payload)
        wire.send(request, header, payload, {"kind": "single_job_final_mode0"})
        record["final_diag_meta"], _, _ = wire.receive(request, 0)
        require(record["final_diag_meta"]["phys_status"] == 0x400 and record["final_diag_meta"]["epoch"] == 1 and
                record["final_diag_meta"]["error_code"] == 0 and record["final_diag_meta"]["last_reject"] == 0,
                "最终DIAG不是ACK后真实IDLE")
        controller.gate(both=False)
        record["final_csr"] = controller.stable_csr("single_job_ack_idle_epoch1")
        require_idle(record["final_csr"], 1)
        require(wire.last_sequence == 3 and wire.epoch == 1 and wire.abort_pending is None and not wire.failed, "单任务最终UART状态错误")
        record["qualification"] = "GOLDEN_AND_ACK_IDLE_OBSERVED"
    except BaseException:
        wire.failed = True
        controller.failed = True
        controller.record["status"] = "FAILED"
        controller.fail_stop()
        raise


def cleanup_action(log, name, function, *, record, controller=None, kwargs=None):
    """执行一项清理；异常锁存为FAILED并触发控制器fail-stop。"""
    try:
        log.call(name, function, **(kwargs or {}))
    except BaseException as error:
        record["status"] = "FAILED"
        record["cleanup_errors"].append({"action": name, "error": repr(error)})
        if controller is not None:
            controller.failed = True
            controller.record["status"] = "FAILED"
            try:
                controller.fail_stop()
            except BaseException as stop_error:
                record["cleanup_errors"].append({"action": name + ".fail_stop", "error": repr(stop_error)})
        return error
    return None


def run(config_path, *, offline_only=False):
    """离线预检纯只读；真实运行先留存新Run，再通过可信门禁才导入硬件接口。"""
    p, j, t = helpers()
    path = j.exact_path(config_path)
    require(path.stat().st_size <= 4 * 1024 * 1024, "config过大")
    raw = path.read_bytes()
    cfg = p.strict_json(raw.decode("utf-8"))
    validate_config(cfg)
    if offline_only:
        prepared = preflight(cfg)
        return {"status": "OFFLINE_INPUTS_VERIFIED_HARDWARE_NOT_RUN", "hardware_execution": "NOT_RUN",
                "source_commit": prepared["source_commit"], "cleanup_errors": [],
                "cold_lifecycle_proven": False}
    parent = j.exact_path(ROOT / "report/evidence/S2B-T19", directory=True)
    requested = Path(cfg["run_dir"])
    require(requested.is_absolute() and requested.parent == parent and re.fullmatch(r"[A-Za-z0-9_-]+", requested.name), "RunId必须位于T19且使用精确新名称")
    folder = t.new_directory(requested, parent)
    with (folder / "input_config.json").open("xb") as output:
        output.write(raw)
    record = {"schema_version": 1, "scope": SCOPE, "status": "BLOCKED", "hardware_execution": "NOT_RUN",
              "hardware_attempted": False, "cold_lifecycle_proven": False, "calls": [],
              "cleanup_errors": [], "identity_snapshots": [],
              "entry_sha256": p.digest(j.exact_path(Path(__file__))), "config_sha256": hashlib.sha256(raw).hexdigest(),
              "started_at_utc8": datetime.now(TZ).isoformat(), "pl_elapsed_cycles": None,
              "first_busy_monotonic": None, "terminal_monotonic": None, "peak_process_tree_memory_bytes": None,
              "response_timeout_seconds": cfg["response_timeout_seconds"],
              "limitations": ["单样本资格不代表全T18 G0、109样本、1000连续任务或恢复验收。",
                              "收据来源及人工独占链由真实Reviewer独立核查，角色字符串不能自行证明。",
                              "不伪测公开CSR没有提供的精确PL周期；本实现不并发TCF轮询。",
                              "首个受控样本的CORE/DRAIN使用冻结规程规定的最大有限上限；这不是实测部署上界，最终期限须在G4/G5量化。SDK system-stop不等于POR。",
                              "当前未固定可信Reviewer、G0及POR/冷生命周期锚点，真实硬件执行保持BLOCKED。",
                              "response_timeout_seconds单位为秒，仅限UART响应观察，不替代PL CORE/DRAIN周期上限。"]}
    log = p.Recorder(folder / "entry_calls.jsonl", record)
    sdk = session = channel = port = controller = wire = None
    owner = {}
    started = time.monotonic()
    failure = None
    try:
        prepared = preflight(cfg)
        record["source_commit"] = prepared["source_commit"]
        record["qualified_receipt"] = cfg["qualification_receipt"]
        if not offline_only:
            def identity(label):
                actual = log.call("identity." + label, p._identity_snapshot)
                record["identity_snapshots"].append({"label": label, **actual})
                p.validate_identity(actual, prepared["server"], cfg["uart_identity"])
            identity("before_sdk")
            sdk, serial = log.call("runtime.bound_import", p._runtime, cfg)
            session = log.call("xsdb.start_debug_session", sdk.start_debug_session)
            log.call("runtime.verify_session", p.verify_runtime_sources, cfg, session)
            # TCF connect之后会枚举并操作板上target；在调用前记录交互尝试，连接异常也属于失败。
            record["hardware_attempted"] = True
            record["hardware_execution"] = "BOARD_INTERACTION_ATTEMPTED"
            channel = log.call("session.connect", session.connect, url="TCP:localhost:3121", server="hw_server")
            log.call("runtime.verify_connected", p.verify_runtime_sources, cfg, session)
            identity("after_connect")
            selected = j.validate_targets(log.call("session.initial_targets", session.targets, "--target_properties"))
            for name in j.NAMES[1:3]:
                target = log.call("session.initial_cpu", session.targets, id=selected[name]["target_id"])
                log.call("runtime.verify_target", p.verify_runtime_sources, cfg, session, target)
                require(vars(target).get("_ctx") == selected[name]["target_ctx"] and vars(target).get("_name") == name, "CPU对象身份错误")
                state = log.call("initial_cpu.state", target.state)
                require(type(state) is str and (state == "Running" or state.startswith("Stopped")), "CPU状态未知")
                if state == "Running":
                    log.call("authorized_cpu.stop", target.stop)
                require(log.call("stopped_cpu.state", target.state).startswith("Stopped"), "CPU未停住")
            controller = j.JtagController(session, cfg["bindings"], folder)
            controller.select_and_gate()
            for target in controller.targets.values():
                log.call("runtime.verify_controller_target", p.verify_runtime_sources, cfg, session, target)
            # 第二遍核验包含独占期限，发生任何输入漂移均不得开始部署。
            preflight(cfg)
            identity("before_deploy")
            controller.system_reset_stop(cfg["cold_basis"])
            # 共享探针helper沿用历史字段名implemented_xsa；此入口的静态preflight已验证当前R04 bindings.xsa，且其内含bit并与本次ELF同属一套构建。
            record["verified_inputs"] = {"compat_artifacts": {"implemented_xsa": cfg["bindings"]["xsa"]}}
            p.register_csr_debug_map(cfg, record, log, session, controller, owner)
            port = log.call("serial.construct_closed", serial.Serial, port=None, baudrate=115200, bytesize=8,
                            parity="N", stopbits=1, timeout=0.1, write_timeout=1.0, rtscts=False, dsrdtr=False)
            port.dtr = False
            port.rts = False
            port.port = "COM4"
            log.call("serial.open", port.open)
            record["hardware_execution"] = "VOLATILE_SINGLE_JOB_REQUESTED"
            with (folder / "uart_rx_raw.bin").open("xb") as rx, (folder / "uart_tx_headers.bin").open("xb") as tx, (folder / "uart_tx_progress.jsonl").open("x", encoding="utf-8", newline="\n") as progress:
                wire = make_wire(j, port, progress, rx, tx, cfg)
                controller.deploy()
                log.call("runtime.verify_deployed", p.verify_runtime_sources, cfg, session)
                record["banner"] = wire.banner(prepared["build"]["source_sha256"]["vitis/s2b_inference_app.c"], XSA_SHA)
                require(controller.postconfigured and controller.record["postconfiguration"]["status"] == "PASS", "受控启动未完成")
                single_job(cfg, prepared, controller, wire, folder, record)
                controller.fail_stop()
                require(controller.state("cpu0").startswith("Stopped") and not controller.record["cleanup_errors"], "完成后CPU0未停住")
            identity("after_single_job")
            record["status"] = "SINGLE_JOB_OBSERVATIONS_SAVED_ACCEPTANCE_PENDING"
    except BaseException as error:
        failure = error
        record.update(error=repr(error), traceback=traceback.format_exc())
        if record["hardware_attempted"]:
            record["status"] = "FAILED"
        if wire is not None:
            wire.failed = True
        if controller is not None:
            controller.failed = True
            controller.record["status"] = "FAILED"
            controller.fail_stop()
    finally:
        def cleanup(name, function, **kwargs):
            nonlocal failure
            error = cleanup_action(log, name, function, record=record, controller=controller, kwargs=kwargs)
            failure = failure or error
        if port is not None:
            def close_port():
                port.close()
                require(not port.is_open, "串口关闭失败")
            cleanup("serial.close", close_port)
        if controller is not None:
            cleanup("controller.close", controller.close)
            if controller.failed or controller.record["cleanup_errors"]:
                failure = failure or QualificationError("控制器失败锁存或清理失败")
                record["status"] = "FAILED"
        if session is not None:
            cleanup("owned_map.clear", p.clear_csr_debug_map, config=cfg, record=record, log=log, session=session, owner=owner)
            cleanup("session.disconnect", session.disconnect, **({"chan": channel} if channel is not None else {}))
        if sdk is not None:
            cleanup("xsdb.dispose", sdk.dispose)
        if wire is not None:
            record["uart_events"] = wire.events
            record["uart_failed"] = wire.failed
        record.update(native_exit_code=2 if failure else 0, elapsed_seconds=time.monotonic() - started,
                      finished_at_utc8=datetime.now(TZ).isoformat(), owned_hw_server_released=False)
        log.stream.close()
        record["saved_files"] = {file.name: {"sha256": p.digest(file), "bytes": file.stat().st_size}
                                  for file in folder.iterdir() if file.is_file()}
        p.save(folder / "model_qualification_result.json", record)
    if failure is not None:
        raise QualificationError("单样本资格阻断/失败，证据：" + str(folder)) from failure
    return record


def main(argv=None):
    """help和--offline-bindings不访问硬件；资格运行必须显式提供配置。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--preflight", action="store_true", help="仅离线核验，不导入SDK或串口")
    parser.add_argument("--offline-bindings", action="store_true",
                        help="只读核验R04 XSA/bit、T15 ELF与冻结模型绑定，不运行资格门禁")
    args = parser.parse_args(argv)
    if args.offline_bindings:
        if args.config or args.preflight:
            parser.error("--offline-bindings不能与--config或--preflight组合")
        try:
            vitis_directory = str(Path(__file__).absolute().parent)
            if vitis_directory not in sys.path:
                sys.path.insert(0, vitis_directory)
            offline = importlib.import_module("prepare_s2b_model_qualification_offline")
            report = offline.build_report()
            print(json.dumps({"status": report["status"],
                              "qualification_gate": report["qualification_gate"],
                              "hardware_execution": report["hardware_execution"],
                              "source_head": report["source_head"],
                              "rebuild_config_path": report["same_xsa_elf_rebuild_plan"]["build_config_path"],
                              "input_manifest_path": report["same_xsa_elf_rebuild_plan"]["input_manifest_path"],
                              "managed_launcher_command": report["same_xsa_elf_rebuild_plan"]["managed_launcher"]["command"],
                              "blockers": report["blockers"]}, ensure_ascii=False))
            return 0
        except Exception as error:
            print(json.dumps({"status": "OFFLINE_BINDING_BLOCKED", "error": repr(error)},
                             ensure_ascii=False), file=sys.stderr)
            return 2
    config = args.config or os.environ.get("S2B_MODEL_QUALIFICATION_CONFIG")
    if not config:
        parser.error("必须显式提供--config或S2B_MODEL_QUALIFICATION_CONFIG")
    try:
        result = run(config, offline_only=args.preflight)
        print(json.dumps({"status": result["status"], "hardware_execution": result["hardware_execution"]}, ensure_ascii=False))
        return 0
    except Exception as error:
        print(json.dumps({"status": "BLOCKED_OR_FAILED", "error": repr(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
