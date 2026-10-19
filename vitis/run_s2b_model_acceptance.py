#!/usr/bin/env python3
"""S2B-T18 visibility1 部署编排入口；仅显式配置可触发板卡访问。"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import argparse
import ast
import hashlib
import importlib
import importlib.machinery
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import traceback


ROOT = Path(__file__).absolute().parents[1]
EVIDENCE_PARENT = ROOT / "report/evidence/S2B-T18"
TZ = timezone(timedelta(hours=8))
JTAG_SOURCE_SHA256 = "dbd1de2241518e679312746a7386c7e5fb1a5a2e242b88dff052b1ca8907b0c6"
COLD_RECEIPT_CONTROLLER_SHA256 = "248779cf4281f4f57cf805a46f3546e22e2549663f60d6578c5500b1891ff3ee"
CSR_MAP_HELPER_SOURCE_SHA256 = "e2cf60f08a0de90b40eb38599c2b3ed5eb809c7d35b6b16a8de6efd4fe94ec1a"
CSR_FLOW_SOURCE_SHA256 = "632b137e27c73fe6e648a49ab77a98bda31f4e5c36d0c3b241dd561e0fab11a9"
CSR_BOARD_SOURCE_SHA256 = "2384c4c001f82b8c877c0b861f97c356483ec4d5b627b7d8b6ef286b6fdb368b"
CSR_BUSY_SOURCE_SHA256 = "e51dcf4360fe3f14805cc2e873449bc9b4367a92d40c2b06965f1e6cd68b2a20"
# 正式G0与统一冷生命周期回执固定到本轮独立审查原件；不代表109/1000或阶段验收已通过。
G0_BASIS_PATH: Path | None = ROOT / "report/evidence/S2B-T18/formal_g0_refresh_20261019_r01/g0_receipt_csr_r04.json"
G0_BASIS_SHA256: str | None = "45369c180f6b5de585dea35c4d5ac6b0655b80f5be0c5a100960d737b929bd79"
COLD_BASIS_PATH: Path | None = ROOT / "report/evidence/S2B-T18/formal_review_20261018_r01/cold_lifecycle_receipt.json"
COLD_BASIS_SHA256: str | None = "62dd8423a9f29446845f1c30236e599104f366a1bafed8ddc7287a85b100c9e2"
CONTROLLER_BINDING_KEYS = {
    "init_elf", "app_elf", "xsa", "bit", "csr_source", "interface", "sdk_target",
    "tool_source", "elf_parser", "delivery_parser", "transport_source",
    "acceptance_source", "runner_source", "uart_interface",
}
CONFIG_KEYS = {
    "schema_version", "source_commit", "run_id", "preparation", "build_details", "bindings",
    "visibility_proof", "visibility_review", "final_platform_manifest", "final_review",
    "g0_basis", "cold_basis", "runtime", "serial", "hw_server", "core_timeout", "drain_timeout",
    "response_timeout_seconds",
}
CSR_CONFIG_KEYS = CONFIG_KEYS | {"csr_reentry"}
G0_RECEIPT_KEYS = {
    "schema_version", "status", "role", "scope", "source_commit", "interface_versions", "bindings",
    "deadline_profile",
}
G0_BINDING_NAMES = (
    "interface", "uart_interface", "preparation", "build_details", "xsa", "bit", "app_elf", "init_elf",
    "visibility_proof", "visibility_review", "final_platform_manifest", "final_review",
)
COLD_RECEIPT_KEYS = {
    "schema_version", "status", "role", "scope", "controller_source_sha256", "reset_method",
    "evidence_kind", "hard_reset_proven", "cold_lifecycle_proven", "evidence",
}


class RunnerError(RuntimeError):
    """输入、设备身份、部署或证据清理失败。"""


def require(condition: bool, message: str) -> None:
    """不受 Python 优化选项影响的门禁。"""
    if not condition:
        raise RunnerError(message)


def strict_json(raw: bytes) -> object:
    """拒绝重复字段、非标准常量和无效 UTF-8 JSON。"""
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "JSON 含重复字段：" + key)
            result[key] = value
        return result

    def constant(value):
        raise RunnerError("JSON 含非标准常量：" + value)

    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, UnicodeError, RecursionError) as error:
        raise RunnerError("JSON 原字节无效") from error


def exact_path(raw: str | Path, kind: str = "file") -> Path:
    """逐级核对绝对路径名称、目标类型和重解析点。"""
    path = Path(raw)
    require(path.is_absolute() and not any(part in {".", ".."} for part in path.parts), "需要精确绝对路径")
    if path.is_relative_to(ROOT):
        current = ROOT
        parts = path.relative_to(ROOT).parts
    else:
        current = Path(path.anchor)
        parts = path.parts[1:]
    for part in parts:
        entries = [entry for entry in current.iterdir() if entry.name.casefold() == part.casefold()]
        require(len(entries) == 1 and entries[0].name == part, "路径名称不存在或大小写冲突：" + str(path))
        current = entries[0]
        attributes = getattr(current.stat(follow_symlinks=False), "st_file_attributes", 0)
        require(not current.is_symlink() and not (attributes & 0x400), "拒绝链接或重解析点：" + str(current))
    require(current.is_file() if kind == "file" else current.is_dir(), "目标类型不符：" + str(path))
    return current


def digest(raw: bytes) -> str:
    """计算原字节 SHA-256。"""
    return hashlib.sha256(raw).hexdigest()


def verify_binding(item: object, label: str, *, max_bytes: int | None = None,
                   within_root: bool = True) -> tuple[Path, bytes]:
    """在消费前核对唯一精确文件及完整原字节摘要。"""
    require(type(item) is dict and set(item) == {"path", "sha256"}, label + " 绑定格式错误")
    require(type(item["path"]) is str and type(item["sha256"]) is str and
            re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is not None, label + " 绑定摘要格式错误")
    path = exact_path(item["path"])
    if within_root:
        require(path.is_relative_to(ROOT), label + " 必须位于仓库内")
    if max_bytes is not None:
        require(path.stat().st_size <= max_bytes, label + " 超出大小限制")
    raw = path.read_bytes()
    require(digest(raw) == item["sha256"], label + " SHA-256 不匹配：" + str(path))
    return path, raw


def _verify_csr_flow_sources() -> None:
    """显式CSR scope在设备运行时导入前固定三份编排/执行源码。"""
    pins = {
        ROOT / "verification/s2b_csr_acceptance_flow.py": CSR_FLOW_SOURCE_SHA256,
        ROOT / "verification/s2b_csr_board_acceptance.py": CSR_BOARD_SOURCE_SHA256,
        ROOT / "verification/s2b_csr_busy_observer.py": CSR_BUSY_SOURCE_SHA256,
    }
    for path, expected in pins.items():
        actual = digest(exact_path(path).read_bytes())
        require(re.fullmatch(r"[0-9a-f]{64}", expected) is not None and actual == expected,
                "CSR固定执行源码SHA不匹配：" + str(path))


def load_apis(scope: str = "model"):
    """延迟加载仓库 API；模块导入不连接板卡或串口。"""
    root_text = str(ROOT)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    verification_text = str(ROOT / "verification")
    if verification_text not in sys.path:
        sys.path.insert(0, verification_text)
    from verification import check_s2b_inference_platform as platform
    from verification import check_s2b_ps_smoke_layout as elf_parser
    from verification import check_stage_delivery as delivery
    from verification import s2b_board_acceptance as acceptance
    from verification import s2b_board_jtag as jtag
    from verification import s2b_board_transport as transport
    values = {"acceptance": acceptance, "delivery": delivery, "jtag": jtag,
              "elf_parser": elf_parser, "platform": platform, "transport": transport}
    if scope == "csr":
        from verification import s2b_csr_acceptance_flow as csr_flow
        values["csr_flow"] = csr_flow
    return type("Apis", (), values)


def _same_binding(left: dict, right: dict) -> bool:
    return type(left) is dict and type(right) is dict and left == right


def _verify_pinned_basis(item: object, label: str, pinned_path: Path | None,
                         pinned_sha256: str | None) -> tuple[Path, bytes]:
    """只接受由代码固定路径和摘要的独立回执，不接受配置自报批准。"""
    path, raw = verify_binding(item, label, max_bytes=8 * 1024 * 1024)
    require(pinned_path is not None and pinned_sha256 is not None,
            label + "尚无独立审查固定的正式回执SHA，禁止部署")
    require(re.fullmatch(r"[0-9a-f]{64}", pinned_sha256) is not None,
            label + "正式回执SHA pin 格式错误")
    require(path == exact_path(pinned_path), label + "路径与独立审查固定路径不符")
    require(digest(raw) == pinned_sha256, label + "原字节与独立审查固定SHA不符")
    return path, raw


def _validate_interface_freeze_sources(bindings: object) -> dict[str, str]:
    """在运行时初始化前检查物理接口和UART文档状态及首行版本。"""
    require(type(bindings) is dict and {"interface", "uart_interface"} <= set(bindings),
            "缺少PS/PL或物理UART接口绑定")
    expected = {
        "interface": ROOT / "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md",
        "uart_interface": ROOT / "docs/obsidian-project/02-方案设计/s2b_board_transport.md",
    }
    versions = {}
    for name, expected_path in expected.items():
        path, raw = verify_binding(bindings[name], name, max_bytes=4 * 1024 * 1024)
        require(path == exact_path(expected_path), name + "必须绑定正式接口文档")
        try:
            text = raw.decode("utf-8")
        except UnicodeError as error:
            raise RunnerError(name + "不是有效UTF-8") from error
        if name == "interface":
            require("CANDIDATE_NOT_FROZEN" not in text and "G0_FROZEN" in text,
                    "PS/PL物理接口仍未冻结，当前文档不是G0_FROZEN")
        else:
            require("尚未完成完整平台冻结" not in text and "G0_FROZEN" in text,
                    "物理UART接口尚未声明G0_FROZEN")
        first_line = text.splitlines()[0] if text.splitlines() else ""
        prefix = "s2b-physical/" if name == "interface" else "s2bu/"
        version_pattern = re.escape(prefix) + r"[A-Za-z0-9][A-Za-z0-9._/-]*"
        # 正式标题用反引号版本字段，旧式首行用“版本：”字段；两种格式均须唯一且匹配接口前缀。
        title_versions = re.findall(r"`(" + version_pattern + r")`", first_line)
        labeled_versions = re.findall(r"版本\s*[：:]?\s*`?(" + version_pattern + r")`?", first_line)
        matches = title_versions + labeled_versions
        require(len(matches) == 1, name + "首行必须含唯一且前缀正确的明确版本")
        versions[name] = matches[0]
    return versions


def validate_controller_source_pin(binding: object) -> None:
    """维持 T16 已审 JTAG controller 的源码SHA边界。"""
    require(type(binding) is dict and type(binding.get("sha256")) is str and
            binding["sha256"] == JTAG_SOURCE_SHA256,
            "T16 JTAG controller 不是已审源码版本")


def load_pinned_csr_map_helper():
    """仅加载原字节SHA固定的T19 CSR映射helper。"""
    path = exact_path(ROOT / "vitis/run_s2b_visibility_probe.py")
    require(digest(path.read_bytes()) == CSR_MAP_HELPER_SOURCE_SHA256,
            "CSR map helper 源码SHA不匹配")
    module_dir = str(path.parent)
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location("_s2b_t18_pinned_csr_map_helper", path)
    require(spec is not None and spec.loader is not None, "无法创建固定CSR map helper导入规格")
    helper = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = helper
    spec.loader.exec_module(helper)
    require(exact_path(helper.__file__) == path and
            digest(path.read_bytes()) == CSR_MAP_HELPER_SOURCE_SHA256,
            "已导入CSR map helper路径或原字节SHA漂移")
    return helper, {"path": str(path), "sha256": CSR_MAP_HELPER_SOURCE_SHA256}


def _g0_config_binding(config: dict, name: str) -> object:
    """从现行 T18 config 读取需要被 G0 receipt 锁定的精确输入。"""
    if name in {"interface", "uart_interface", "xsa", "bit", "app_elf", "init_elf"}:
        bindings = config.get("bindings")
        require(type(bindings) is dict and name in bindings, "G0 config 缺少 controller 绑定：" + name)
        return bindings[name]
    require(name in config, "G0 config 缺少输入绑定：" + name)
    return config[name]


def _validate_g0_build_outputs(config: dict) -> None:
    """检查 build_details 的源码祖先关系，以及真实 XSA/ELF 产物绑定。"""
    build_path, build_raw = verify_binding(config.get("build_details"), "build_details", max_bytes=4 * 1024 * 1024)
    build = strict_json(build_raw)
    require(type(build) is dict and build.get("status") == "PASS_OFFLINE_FULL_XSA_BUILD" and
            build.get("hardware_mode") == "FULL_PLATFORM_BOUND", "G0 build_details 不是完整平台成功构建")
    build_config = build.get("config")
    require(type(build_config) is dict and type(config.get("bindings")) is dict,
            "G0 build_details config schema 错误")
    for build_item, config_name in ((build_config, "xsa"), (build, "elf"), (build, "initializer_elf")):
        require(type(build_item) is dict, "G0 build_details 缺少产物绑定：" + config_name)
    xsa = config["bindings"]["xsa"]
    app_elf = config["bindings"]["app_elf"]
    init_elf = config["bindings"]["init_elf"]
    require(type(xsa) is dict and type(app_elf) is dict and type(init_elf) is dict,
            "G0 config 产物绑定格式错误")
    build_commit = build.get("source_commit")
    current_commit = config.get("source_commit")
    require(type(build_commit) is str and re.fullmatch(r"[0-9a-f]{40}", build_commit) is not None and
            type(current_commit) is str and re.fullmatch(r"[0-9a-f]{40}", current_commit) is not None,
            "G0 build_details/config source_commit 必须是完整 commit SHA")
    try:
        subprocess.run(["git", "merge-base", "--is-ancestor", build_commit, current_commit],
                       cwd=ROOT, capture_output=True, check=True)
    except subprocess.CalledProcessError as error:
        raise RunnerError("G0 build_details source_commit 不是当前源码基线的祖先") from error
    except OSError as error:
        raise RunnerError("无法核验 G0 build_details source_commit 祖先关系") from error
    require(build_config.get("xsa") == xsa.get("path") and
            build_config.get("xsa_sha256") == xsa.get("sha256") and
            build.get("xsa_sha256") == xsa.get("sha256"),
            "G0 build_details 与当前编译 XSA 不一致")
    for label, actual, expected in (("app_elf", build.get("elf"), app_elf),
                                    ("init_elf", build.get("initializer_elf"), init_elf)):
        require(actual.get("path") == expected.get("path") and actual.get("sha256") == expected.get("sha256"),
                "G0 build_details 与当前产物不一致：" + label)
    del build_path


def _validate_g0_receipt(receipt: object, config: dict, versions: dict[str, str]) -> None:
    """严格校验 G0 receipt schema 并绑定当前文档、构建和验收输入字节。"""
    require(type(receipt) is dict and set(receipt) == G0_RECEIPT_KEYS, "G0 receipt schema 字段不匹配")
    require(type(receipt["schema_version"]) is int and receipt["schema_version"] == 1 and
            receipt["status"] == "PASS" and receipt["role"] == "INDEPENDENT_REVIEWER" and
            receipt["scope"] == "S2B_T18_G0_APPROVAL", "G0 receipt 审批身份或范围错误")
    source_commit = config.get("source_commit")
    receipt_commit = receipt["source_commit"]
    require(type(source_commit) is str and re.fullmatch(r"[0-9a-f]{40}", source_commit) is not None and
            type(receipt_commit) is str and re.fullmatch(r"[0-9a-f]{40}", receipt_commit) is not None,
            "G0 receipt/config source_commit 必须是完整 commit SHA")
    try:
        subprocess.run(["git", "merge-base", "--is-ancestor", receipt_commit, source_commit],
                       cwd=ROOT, capture_output=True, check=True)
    except subprocess.CalledProcessError as error:
        raise RunnerError("G0 receipt source_commit 不是当前源码基线的祖先") from error
    except OSError as error:
        raise RunnerError("无法核验 G0 receipt source_commit 祖先关系") from error
    require(type(receipt["interface_versions"]) is dict and
            set(receipt["interface_versions"]) == {"interface", "uart_interface"} and
            receipt["interface_versions"] == versions, "G0 receipt 接口文档版本与当前原文不符")
    profile = receipt["deadline_profile"]
    require(type(profile) is dict and set(profile) ==
            {"core_timeout", "drain_timeout", "response_timeout_seconds"}, "G0 deadline_profile字段错误")
    _validate_deadline_profile(config)
    require(profile == {name: config[name] for name in profile},
            "G0 deadline_profile与当前config值不一致")
    expected = {}
    for name in G0_BINDING_NAMES:
        item = _g0_config_binding(config, name)
        path, raw = verify_binding(item, "G0 当前输入 " + name, max_bytes=64 * 1024 * 1024)
        binding = {"path": str(path), "sha256": digest(raw)}
        if name in versions:
            binding["version"] = versions[name]
        expected[name] = binding
    require(type(receipt["bindings"]) is dict and set(receipt["bindings"]) == set(G0_BINDING_NAMES) and
            receipt["bindings"] == expected, "G0 receipt path/version/SHA 与当前实际输入不符")
    _validate_g0_build_outputs(config)


def _validate_deadline_profile(config: dict) -> None:
    """核验CSR deadline计数周期和UART接收秒数的独立单位契约。"""
    require(type(config.get("core_timeout")) is int and 1 <= config["core_timeout"] <= 0xFFFFFFFF,
            "core_timeout必须是非零uint32周期数")
    require(type(config.get("drain_timeout")) is int and 1 <= config["drain_timeout"] <= 0xFFFFFFFF,
            "drain_timeout必须是非零uint32周期数")
    response = config.get("response_timeout_seconds")
    require(type(response) in (int, float) and 0 < response <= 450 and
            (type(response) is int or math.isfinite(response)),
            "UART response_timeout_seconds必须是有限正数且不超过450秒")


def _validate_cold_receipt(receipt: object) -> None:
    """仅接受精确绑定已审 JTAG 源的真实物理 POR 生命周期回执。"""
    require(type(receipt) is dict and set(receipt) == COLD_RECEIPT_KEYS, "冷生命周期 receipt schema 字段不匹配")
    require(type(receipt["schema_version"]) is int and receipt["schema_version"] == 1 and
            receipt["status"] == "PASS" and receipt["role"] == "INDEPENDENT_REVIEWER" and
            receipt["scope"] == "S2B_T18_UNIFIED_COLD_LIFECYCLE", "冷生命周期 receipt 审批身份或范围错误")
    require(receipt["controller_source_sha256"] == COLD_RECEIPT_CONTROLLER_SHA256,
            "冷生命周期 receipt controller SHA 与其审查时的 T16 源不符")
    require(receipt["reset_method"] == "PHYSICAL_POR" and
            receipt["evidence_kind"] == "PHYSICAL_HARD_RESET_POR" and
            receipt["hard_reset_proven"] is True and receipt["cold_lifecycle_proven"] is True,
            "冷生命周期 receipt 未证明真实硬复位/POR 生命周期")
    verify_binding(receipt["evidence"], "冷生命周期真实硬复位/POR证据", max_bytes=64 * 1024 * 1024)


def _validate_source_preflight(config: dict) -> str:
    """在API导入前绑定当前HEAD及已审JTAG controller的路径和实际字节。"""
    source_commit = config.get("source_commit")
    require(type(source_commit) is str and re.fullmatch(r"[0-9a-f]{40}", source_commit) is not None,
            "source_commit 必须是完整 commit SHA")
    try:
        observed = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                                  text=True, encoding="ascii", check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError) as error:
        raise RunnerError("API加载前无法读取当前HEAD") from error
    require(observed == source_commit, "config 源码 commit 与当前 HEAD 不一致")
    bindings = config.get("bindings")
    require(type(bindings) is dict and "tool_source" in bindings, "缺少 T16 JTAG controller 源绑定")
    path, _ = verify_binding(bindings["tool_source"], "controller tool_source", max_bytes=64 * 1024 * 1024)
    require(path == exact_path(ROOT / "verification/s2b_board_jtag.py"),
            "controller tool_source 必须绑定正式 JTAG 源文件路径")
    validate_controller_source_pin(bindings["tool_source"])
    return observed


def validate_preflight_basis(config: object) -> dict:
    """在SDK导入或任何设备动作前验证G0和统一冷生命周期的可信固定回执。"""
    require(type(config) is dict, "T18 config 顶层必须是对象")
    versions = _validate_interface_freeze_sources(config.get("bindings"))
    g0_path, g0_raw = _verify_pinned_basis(
        config.get("g0_basis"), "S2B-T18 G0冻结回执", G0_BASIS_PATH, G0_BASIS_SHA256)
    cold_path, cold_raw = _verify_pinned_basis(
        config.get("cold_basis"), "统一冷生命周期批准依据", COLD_BASIS_PATH, COLD_BASIS_SHA256)
    _validate_g0_receipt(strict_json(g0_raw), config, versions)
    _validate_cold_receipt(strict_json(cold_raw))
    source_commit = _validate_source_preflight(config)
    return {"g0_path": g0_path, "g0_sha256": digest(g0_raw),
            "cold_path": cold_path, "cold_sha256": digest(cold_raw), "source_commit": source_commit}


def _validate_reentry_identity(snapshot: object, prior_config: dict) -> None:
    """确保前序运行的JTAG进程与串口身份由同一份config声明并被观测。"""
    require(type(snapshot) is dict and type(snapshot.get("validated")) is dict,
            "前序模型运行缺少已验证硬件身份快照")
    validated = snapshot["validated"]
    server, uart, listeners = validated.get("server"), validated.get("uart"), validated.get("listeners")
    expected_server = prior_config["hw_server"]
    expected_uart = prior_config["serial"]["identity"]
    require(type(server) is dict and server.get("ProcessId") == expected_server["process_id"] and
            server.get("ExecutablePath") == expected_server["executable_path"] and
            server.get("CreationTimeFileTimeUtc") == expected_server["creation_time_filetime_utc"],
            "前序模型hw_server身份与其config不匹配")
    require(type(listeners) is list and listeners and all(
            row.get("LocalPort") == 3121 and row.get("OwningProcess") == expected_server["process_id"]
            for row in listeners), "前序模型hw_server listener归属不匹配")
    require(type(uart) is dict and uart.get("Name") == expected_uart["name"] and
            uart.get("PNPDeviceID") == expected_uart["pnp_device_id"] and
            uart.get("ConfigManagerErrorCode") == expected_uart["config_manager_error_code"] == 0,
            "前序模型COM/PNP身份与其config不匹配")


def _validate_bound_jtag_log(result_binding: object, calls_binding: object, label: str) -> tuple[dict, list]:
    """核对JTAG结果与逐行调用日志的原始记录一致。"""
    _, result_raw = verify_binding(result_binding, label + " jtag_result", max_bytes=2 * 1024 * 1024)
    _, calls_raw = verify_binding(calls_binding, label + " jtag_calls", max_bytes=2 * 1024 * 1024)
    result = strict_json(result_raw)
    require(type(result) is dict and type(result.get("calls")) is list,
            label + " jtag_result缺少调用列表")
    try:
        calls = [strict_json(line) for line in calls_raw.splitlines() if line]
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RunnerError(label + " jtag_calls格式错误") from error
    require(calls == result["calls"], label + " jtag_calls与jtag_result.calls不一致")
    return result, calls


def _target_rows_from_call(call: dict, label: str) -> dict:
    require(type(call) is dict and call.get("api") == "session.targets.properties" and
            call.get("status") == "RETURNED" and type(call.get("return_repr")) is str,
            label + "缺少目标链枚举调用")
    try:
        rows = ast.literal_eval(call["return_repr"])
    except (SyntaxError, ValueError) as error:
        raise RunnerError(label + "目标链枚举结果无法安全解析") from error
    require(type(rows) is dict and rows, label + "目标链枚举结果为空")
    by_name = {row.get("name"): row for row in rows.values() if type(row) is dict}
    require(len(by_name) == len(rows), label + "目标链枚举名称重复或格式错误")
    return by_name


def _same_jtag_target_identity(previous: dict, observed: dict) -> None:
    """将两次运行的JTAG上下文绑定到同一物理目标链。"""
    fields = ("target_id", "target_ctx", "level", "name", "parent_ctx", "parent", "jtag_device_id",
              "jtag_device_ctx", "jtag_device_index", "jtag_device_name", "jtag_cable_id",
              "jtag_cable_ctx", "jtag_cable_name", "jtag_cable_manufacturer", "jtag_cable_product",
              "jtag_cable_serial")
    integer_fields = {"target_id", "level", "jtag_device_id", "jtag_device_index", "jtag_cable_id"}
    def valid_rows(rows: object) -> bool:
        return (type(rows) is dict and bool(rows) and all(
            type(name) is str and type(row) is dict and row.get("name") == name and
            set(fields) <= set(row) and all(
                type(row[field]) is (int if field in integer_fields else str) for field in fields)
            for name, row in rows.items()))
    require(type(previous) is dict and type(observed) is dict and set(previous) == set(observed) and
            valid_rows(previous) and valid_rows(observed) and
            all(all(previous[name][field] == observed[name][field] for field in fields)
                for name in previous), "前序模型与当前运行的JTAG目标链身份缺失或不一致")


def _validate_app_pc_instructions(elf: dict, raw: bytes, pc: int, cpsr: int,
                                  observed_bytes: object) -> dict:
    """按CPSR.T核验PC后16字节位于绑定ELF可执行段且与ELF逐字节一致。"""
    require(type(cpsr) is int and 0 <= cpsr <= 0xFFFFFFFF, "CPU0 CPSR不是有效32位值")
    thumb = bool(cpsr & (1 << 5))
    require(type(pc) is int and 0 <= pc <= 0xFFFFFFFF and pc % (2 if thumb else 4) == 0,
            "CPU0 PC与CPSR指示的ARM/Thumb指令对齐不符")
    require(type(observed_bytes) is bytes and len(observed_bytes) == 16,
            "CPU0 PC附近内存读回不是16字节指令")
    width = 16
    loads = [row for row in elf.get("programs", []) if row.get("type") == 1 and
             row.get("flags", 0) & 1 and row.get("file_size", 0) >= width and
             row.get("virtual") <= pc and pc + width <= row.get("virtual", 0) + row.get("file_size", 0)]
    sections = [row for row in elf.get("sections", []) if row.get("flags", 0) & 4 and
                row.get("type") != 8 and row.get("size", 0) >= width and
                row.get("address") <= pc and pc + width <= row.get("address", 0) + row.get("size", 0)]
    matches = []
    for load in loads:
        for section in sections:
            file_offset = section["offset"] + pc - section["address"]
            if (section["offset"] >= load["offset"] and
                    file_offset == load["offset"] + pc - load["virtual"] and
                    file_offset >= load["offset"] and
                    file_offset + width <= load["offset"] + load["file_size"]):
                matches.append((load, section, file_offset))
    require(len(matches) == 1, "CPU0 PC不在唯一的绑定应用ELF可执行LOAD/section中")
    load, section, file_offset = matches[0]
    expected = raw[file_offset:file_offset + width]
    observed = observed_bytes
    require(len(expected) == width and expected == observed,
            "CPU0 PC处实读16字节指令与绑定应用ELF不一致")
    return {"pc": pc, "cpsr": cpsr, "thumb_state": thumb, "section": section["name"],
            "segment_virtual": load["virtual"],
            "instruction_bytes": width, "instruction_bytes_sha256": digest(observed),
            "elf_file_offset": file_offset, "verification": "MATCH_EXECUTABLE_LOAD_AND_SECTION"}


def _validate_model_jtag_observations(jtag_result: dict, calls: list, prior_config: dict) -> dict:
    """证明前序模型在同一绑定ELF上完成app下载并观察到CPU0运行。"""
    require(jtag_result.get("status") == "API_OBSERVATIONS_SAVED_ACCEPTANCE_PENDING" and
            jtag_result.get("cleanup_errors") == [], "前序模型JTAG观察未正常保存")
    bindings = jtag_result.get("bindings")
    require(type(bindings) is dict, "前序模型JTAG结果缺少部署绑定")
    for name in ("app_elf", "bit", "xsa"):
        old, current = bindings.get(name), prior_config["bindings"].get(name)
        require(type(old) is dict and type(current) is dict and
                old.get("path") == current.get("path") and old.get("sha256") == current.get("sha256"),
                "前序模型JTAG结果部署绑定不一致：" + name)
    app_downloads = [(index, call) for index, call in enumerate(calls) if call.get("api") == "cpu0.dow.app"]
    app_continues = [(index, call) for index, call in enumerate(calls) if call.get("api") == "cpu0.con.app"]
    require(len(app_downloads) == len(app_continues) == 1 and
            app_downloads[0][1].get("status") == "RETURNED" and
            app_downloads[0][1].get("kwargs") == {"file": prior_config["bindings"]["app_elf"]["path"],
                                                    "auto_stop": True, "set_entry": True} and
            app_continues[0][1].get("status") == "RETURNED" and
            app_downloads[0][0] < app_continues[0][0],
            "前序模型JTAG调用未按绑定ELF完成app下载与continue")
    cpu0_states_after_continue = [call for index, call in enumerate(calls)
                                  if index > app_continues[0][0] and call.get("api") == "cpu0.state" and
                                  call.get("status") == "RETURNED"]
    cpu1_states = [call for call in calls if call.get("api") == "cpu1.state" and
                   call.get("status") == "RETURNED"]
    require(cpu0_states_after_continue and cpu0_states_after_continue[-1].get("return_repr") == "'Running'" and
            cpu1_states and cpu1_states[-1].get("return_repr") == "'Stopped: (Suspended)'",
            "前序模型最后观测未证明CPU0运行且CPU1停止")
    require(type(jtag_result.get("targets")) is dict, "前序模型JTAG结果缺少已选目标链")
    return jtag_result["targets"]


def _validate_prior_csr_failure(result: dict, jtag_result: dict, calls: list,
                                orchestrator_calls_binding: object, run_id: str,
                                current_config: dict, model_targets: dict) -> dict:
    """核验前次CSR入口失败只读观察到既有app仍运行且未改变板卡状态。"""
    required_run_id = "formal_csr_recovery_20261019_r02"
    require(run_id == required_run_id and result.get("run_id") == run_id and
            result.get("scope") == "csr" and result.get("status") == "FAILED" and
            result.get("native_exit_code") == 2 and "CPU0未停止" in result.get("traceback", ""),
            "绑定的前次CSR结果不是R02只读入口失败")
    require(jtag_result.get("status") == "FAILED" and "CPU0未停止" in jtag_result.get("error", "") and
            jtag_result.get("cleanup_errors") == [], "前次CSR JTAG结果未记录CPU0未停止")
    for name in ("app_elf", "bit", "xsa"):
        old, current = jtag_result.get("bindings", {}).get(name), current_config["bindings"].get(name)
        require(type(old) is dict and type(current) is dict and
                old.get("path") == current.get("path") and old.get("sha256") == current.get("sha256"),
                "前次CSR失败运行的部署绑定不一致：" + name)
    snapshots = result.get("identity_snapshots")
    require(type(snapshots) is list and snapshots, "前次CSR失败结果缺少硬件身份快照")
    for snapshot in snapshots:
        _validate_reentry_identity(snapshot, current_config)
    failed_events = []
    _, raw = verify_binding(orchestrator_calls_binding, "前次CSR orchestrator_calls", max_bytes=2 * 1024 * 1024)
    try:
        orchestrator_calls = [strict_json(line) for line in raw.splitlines() if line]
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RunnerError("前次CSR orchestrator_calls格式错误") from error
    failed_events = [row for row in orchestrator_calls if row.get("step") == "board_flow" and
                     row.get("status") == "FAILED"]
    require(len(failed_events) == 1 and failed_events[0].get("uart_tx_count") == 0 and
            "CPU0未停止" in failed_events[0].get("exception", ""),
            "前次CSR入口失败没有可核验的CPU0未停止与UART TX=0记录")
    forbidden = ("cpu0.stop", "apu.rst", "fpga.config", "cpu0.dow", "cpu0.con", "apu.mwr", "cpu0.mwr")
    require(not any(type(call.get("api")) is str and call["api"].startswith(forbidden) for call in calls),
            "前次CSR失败调用日志包含可能改变板卡状态的操作")
    states = [(index, call.get("api"), call.get("return_repr")) for index, call in enumerate(calls)
              if call.get("api") in ("cpu0.state", "cpu1.state") and call.get("status") == "RETURNED"]
    require(len(states) >= 2 and states[-2][1:] == ("cpu1.state", "'Stopped: (Suspended)'",) and
            states[-1][1:] == ("cpu0.state", "'Running'"),
            "前次CSR失败运行末态未核验CPU1停止与CPU0运行")
    failure_target_call = next((call for call in calls if call.get("api") == "session.targets.properties"), None)
    failure_targets = _target_rows_from_call(failure_target_call, "前次CSR失败")
    _same_jtag_target_identity(model_targets, failure_targets)
    return {"run_id": run_id, "uart_tx_count": 0,
            "observed_cpu0": "Running", "observed_cpu1": "Stopped: (Suspended)",
            "target_identity": failure_targets}


def validate_csr_reentry(config: object, *, scope: str) -> dict | None:
    """在SDK导入或设备动作前验证CSR重入所引用的前序模型PASS。"""
    require(scope in ("model", "csr"), "scope只能是model或csr")
    require(type(config) is dict, "T18 config顶层必须是对象")
    if scope == "model":
        require("csr_reentry" not in config, "model scope禁止携带CSR重入授权")
        return None
    binding = config.get("csr_reentry")
    required = {"model_result", "model_input_config", "model_jtag_result", "model_jtag_calls",
                "prior_csr_result", "prior_csr_jtag_result", "prior_csr_jtag_calls",
                "prior_csr_orchestrator_calls"}
    require(type(binding) is dict and set(binding) == required,
            "csr scope必须精确绑定前序模型与R02失败证据")
    current_run_id = config.get("run_id")
    require(type(current_run_id) is str and re.fullmatch(r"[A-Za-z0-9_-]+", current_run_id) is not None,
            "CSR config缺少有效run_id")
    result_path, result_raw = verify_binding(binding["model_result"], "前序模型orchestrator_result",
                                             max_bytes=2 * 1024 * 1024)
    require(result_path.name == "orchestrator_result.json" and
            re.fullmatch(r"[A-Za-z0-9_-]+", result_path.parent.name) is not None,
            "前序模型orchestrator_result路径错误")
    run_id = result_path.parent.name
    require(current_run_id != run_id, "CSR本次run_id不能复用前序模型RunId")
    deployment = result_path.parent.parent / (run_id + "_deployment")
    expected_paths = {"model_input_config": deployment / "input_config.json",
                      "model_jtag_result": deployment / "jtag_result.json",
                      "model_jtag_calls": deployment / "jtag_calls.jsonl"}
    for name, expected in expected_paths.items():
        path, _ = verify_binding(binding[name], "前序模型 " + name, max_bytes=2 * 1024 * 1024)
        require(path == exact_path(expected), "前序模型证据未与result按相邻run/deployment目录配对：" + name)
    failure_run_id = "formal_csr_recovery_20261019_r02"
    failure_result_path = exact_path(EVIDENCE_PARENT / failure_run_id / "orchestrator_result.json")
    failure_deployment = EVIDENCE_PARENT / (failure_run_id + "_deployment")
    failure_paths = {"prior_csr_result": failure_result_path,
                     "prior_csr_jtag_result": failure_deployment / "jtag_result.json",
                     "prior_csr_jtag_calls": failure_deployment / "jtag_calls.jsonl",
                     "prior_csr_orchestrator_calls": failure_deployment / "orchestrator_calls.jsonl"}
    prior_failure_files = {}
    for name, expected in failure_paths.items():
        path, _ = verify_binding(binding[name], "前次CSR失败 " + name, max_bytes=2 * 1024 * 1024)
        require(path == exact_path(expected), "前次CSR失败证据路径不等于固定R02目录：" + name)
        prior_failure_files[name] = path
    _, config_raw = verify_binding(binding["model_input_config"], "前序模型input_config",
                                   max_bytes=1024 * 1024)
    prior_config = strict_json(config_raw)
    result = strict_json(result_raw)
    require(type(result) is dict and result.get("scope") == "model" and
            result.get("status") == "PASS_MODEL_CORPUS_AND_STRESS_ONLY" and
            result.get("native_exit_code") == 0 and type(result.get("run_id")) is str and
            result["run_id"] == run_id and type(prior_config) is dict and prior_config.get("run_id") == run_id and
            result.get("cleanup_errors") == [], "前序模型结果不是完整PASS或清理失败")
    acceptance = result.get("acceptance")
    require(type(acceptance) is dict and acceptance.get("status") == "PASS_MODEL_CORPUS_AND_STRESS_ONLY" and
            acceptance.get("completed_stress") == 1000 and acceptance.get("completed_corpus") == 109,
            "前序模型结果未完成1000次压力与109项语料")
    require(type(prior_config) is dict and type(prior_config.get("bindings")) is dict and
            type(config.get("bindings")) is dict, "前序或当前config缺少部署产物绑定")
    for name in ("app_elf", "bit", "xsa"):
        old, current = prior_config["bindings"].get(name), config["bindings"].get(name)
        require(type(old) is dict and type(current) is dict and old.get("path") == current.get("path") and
                old.get("sha256") == current.get("sha256"),
                "CSR重入前序模型与当前部署产物不一致：" + name)
    require(prior_config.get("hw_server") == config.get("hw_server") and
            prior_config.get("serial", {}).get("identity") == config.get("serial", {}).get("identity"),
            "前序模型与当前CSR config的hw_server/COM身份不一致")
    snapshots = result.get("identity_snapshots")
    required_labels = {"before_runtime", "after_connect", "before_serial", "after_serial_open"}
    require(type(snapshots) is list and required_labels <=
            {row.get("label") for row in snapshots if type(row) is dict},
            "前序模型运行缺少部署前后硬件身份快照")
    for snapshot in snapshots:
        _validate_reentry_identity(snapshot, prior_config)
    model_jtag_result, model_jtag_calls = _validate_bound_jtag_log(
        binding["model_jtag_result"], binding["model_jtag_calls"], "前序模型")
    model_targets = _validate_model_jtag_observations(model_jtag_result, model_jtag_calls, prior_config)
    failure_result = strict_json(prior_failure_files["prior_csr_result"].read_bytes())
    failure_jtag_result, failure_jtag_calls = _validate_bound_jtag_log(
        binding["prior_csr_jtag_result"], binding["prior_csr_jtag_calls"], "前次CSR失败")
    failure_run_id = _validate_prior_csr_failure(
            failure_result, failure_jtag_result, failure_jtag_calls,
        binding["prior_csr_orchestrator_calls"], "formal_csr_recovery_20261019_r02",
        config, model_targets)
    try:
        model_finished = datetime.fromisoformat(result["finished_at_utc8"])
        failure_started = datetime.fromisoformat(failure_result["started_at_utc8"])
    except (KeyError, TypeError, ValueError) as error:
        raise RunnerError("模型PASS或前次CSR失败缺少有效时间戳") from error
    require(model_finished <= failure_started, "前次CSR失败时间早于所绑定模型PASS")
    failure_run_id.update({"result": dict(binding["prior_csr_result"]),
                           "jtag_result": dict(binding["prior_csr_jtag_result"]),
                           "jtag_calls": dict(binding["prior_csr_jtag_calls"]),
                           "orchestrator_calls": dict(binding["prior_csr_orchestrator_calls"])})
    return {"model_run_id": result["run_id"], "model_result": dict(binding["model_result"]),
            "model_input_config": dict(binding["model_input_config"]),
            "model_jtag_result": dict(binding["model_jtag_result"]),
            "model_jtag_calls": dict(binding["model_jtag_calls"]),
            "model_target_identity": model_targets,
            "prior_csr_failure": failure_run_id,
            "artifact_bindings": {name: dict(prior_config["bindings"][name])
                                  for name in ("app_elf", "bit", "xsa")}}


def _validate_runtime_config(config: dict, apis) -> None:
    runtime = config["runtime"]
    required = {"sdk_init", "sdk_target", "sdk_files", "pyserial_init", "pyserial_files", "pyserial_version"}
    require(type(runtime) is dict and set(runtime) == required, "runtime 字段不完整或含未知字段")
    sdk_init, _ = verify_binding(runtime["sdk_init"], "SDK 入口", max_bytes=8 * 1024 * 1024, within_root=False)
    sdk_target, _ = verify_binding(runtime["sdk_target"], "SDK Target 源", max_bytes=8 * 1024 * 1024,
                                   within_root=False)
    require(sdk_init.name == "__init__.py" and sdk_init.parent.name == "xsdb" and
            sdk_target == sdk_init.parent / "target.py", "SDK 路径或包布局不匹配")
    require(_same_binding(runtime["sdk_target"], config["bindings"]["sdk_target"]),
            "controller 与实际 SDK Target 源绑定不同")
    sdk_files = runtime["sdk_files"]
    require(type(sdk_files) is dict and {"xsdb", "xsdb.target", "xsdb.xsdb_debug_session",
            "xsdb.session", "xsdb._tcf_reset", "xv_pycommontasks", "xv_hsmpytasks"} <= set(sdk_files)
            and len(sdk_files) <= 512,
            "SDK 模块源码闭包格式错误")
    require(_same_binding(sdk_files["xsdb"], runtime["sdk_init"]) and
            _same_binding(sdk_files["xsdb.target"], runtime["sdk_target"]), "SDK 源码闭包入口绑定不一致")
    cli_root = sdk_init.parent.parent
    product_root = cli_root.parent
    sdk_roots = (cli_root, cli_root / "python-packages/site-packages", cli_root / "python-packages/win64",
                 product_root / "scripts/python_pkg", product_root / "lib/win64.o")
    for name, item in sdk_files.items():
        require(type(name) is str and name and not name.startswith("."), "SDK 模块名无效")
        path, _ = verify_binding(item, "SDK 模块 " + name, max_bytes=32 * 1024 * 1024, within_root=False)
        require(any(path.is_relative_to(root) for root in sdk_roots), "SDK 模块路径逃逸出声明的安装目录")

    serial_init, _ = verify_binding(runtime["pyserial_init"], "pyserial 入口", max_bytes=8 * 1024 * 1024,
                                    within_root=False)
    require(serial_init.name == "__init__.py" and serial_init.parent.name == "serial" and
            runtime["pyserial_version"] == "3.5", "pyserial 入口或版本不符合已审运行时")
    serial_files = runtime["pyserial_files"]
    require(type(serial_files) is list and 0 < len(serial_files) <= 100, "pyserial 文件闭包无效")
    listed = []
    for item in serial_files:
        path, _ = verify_binding(item, "pyserial 模块", max_bytes=8 * 1024 * 1024, within_root=False)
        require(path.suffix == ".py" and path.is_relative_to(serial_init.parent), "pyserial 模块路径不在包内")
        listed.append(path)
    actual = {exact_path(path) for path in serial_init.parent.rglob("*.py")}
    require(len(listed) == len(set(listed)) and set(listed) == actual and serial_init in listed,
            "pyserial 纯 Python 文件闭包缺项、重复或多项")


def validate_v1_inputs(config: dict, apis, *, scope: str = "model") -> dict:
    """全部核验模型、构建、证明与最终独审后才允许建立 SDK 会话。"""
    require(scope in ("model", "csr"), "scope只能是model或csr")
    expected_keys = CONFIG_KEYS if scope == "model" else CSR_CONFIG_KEYS
    require(type(config) is dict and set(config) == expected_keys, "config 字段集合不匹配")
    require(type(config["schema_version"]) is int and config["schema_version"] == 1, "config schema_version 错误")
    approved_basis = validate_preflight_basis(config)
    csr_reentry = validate_csr_reentry(config, scope=scope)
    require(type(config["source_commit"]) is str and re.fullmatch(r"[0-9a-f]{40}", config["source_commit"]),
            "source_commit 必须是完整 commit SHA")
    observed = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, encoding="ascii", check=True).stdout.strip()
    require(observed == config["source_commit"], "config 源码 commit 与当前 HEAD 不一致")
    run_id = config["run_id"]
    require(type(run_id) is str and re.fullmatch(r"[A-Za-z0-9_-]+", run_id) is not None,
            "run_id 只能包含 ASCII 字母、数字、下划线和连字符")
    parent = exact_path(EVIDENCE_PARENT, "directory")
    run_dir, deploy_dir = parent / run_id, parent / (run_id + "_deployment")
    for target in (run_dir, deploy_dir):
        require(not any(row.name.casefold() == target.name.casefold() for row in parent.iterdir()),
                "拒绝覆盖已存在或仅大小写不同的运行目录：" + str(target))

    bindings = config["bindings"]
    require(type(bindings) is dict and set(bindings) == CONTROLLER_BINDING_KEYS,
            "T16 controller 绑定字段不完整或含未知字段")
    binding_paths = {}
    for name, item in bindings.items():
        binding_paths[name], _ = verify_binding(item, "controller " + name, max_bytes=64 * 1024 * 1024,
                                                 within_root=(name != "sdk_target"))
    expected_paths = {
        "tool_source": ROOT / "verification/s2b_board_jtag.py",
        "elf_parser": ROOT / "verification/check_s2b_ps_smoke_layout.py",
        "delivery_parser": ROOT / "verification/check_stage_delivery.py",
        "transport_source": ROOT / "verification/s2b_board_transport.py",
        "acceptance_source": ROOT / "verification/s2b_board_acceptance.py",
        "runner_source": Path(__file__).absolute(),
        "csr_source": ROOT / "src/s2b_control_csr.sv",
        "interface": ROOT / "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md",
        "uart_interface": ROOT / "docs/obsidian-project/02-方案设计/s2b_board_transport.md",
    }
    for name, expected in expected_paths.items():
        require(binding_paths[name] == exact_path(expected), "源码/接口绑定路径错误：" + name)
    validate_controller_source_pin(bindings["tool_source"])
    require(bindings["runner_source"]["sha256"] == digest(Path(__file__).read_bytes()), "runner 源码绑定漂移")
    _validate_runtime_config(config, apis)
    runtime = config["runtime"]
    require(binding_paths["sdk_target"] == exact_path(runtime["sdk_target"]["path"]), "controller SDK Target 路径漂移")

    build_path, build_raw = verify_binding(config["build_details"], "build_details", max_bytes=4 * 1024 * 1024)
    build_path, build = apis.transport.verify_build(str(build_path))
    require(digest(build_raw) == config["build_details"]["sha256"], "build_details SHA-256 漂移")
    for key, expected in (("app_elf", build["elf"]), ("init_elf", build["initializer_elf"]),
                          ("xsa", {"path": build["config"]["xsa"], "sha256": build["xsa_sha256"]})):
        require(_same_binding(bindings[key], {field: expected[field] for field in ("path", "sha256")}),
                "controller 与实际 build_details 产物不一致：" + key)
    xsa_raw = verify_binding(bindings["xsa"], "编译 XSA", max_bytes=64 * 1024 * 1024)[1]
    init_raw = verify_binding(bindings["init_elf"], "PS 初始化 ELF", max_bytes=64 * 1024 * 1024)[1]
    app_raw = verify_binding(bindings["app_elf"], "应用 ELF", max_bytes=64 * 1024 * 1024)[1]
    apis.jtag.postconfig_basis(xsa_raw)
    apis.jtag.init_layout(init_raw)
    app = apis.elf_parser.parse_elf(app_raw)
    require(0x100000 <= app["entry"] < 0x1100000, "应用 ELF 入口超出已批准 DDR 区域")
    loads = [program for program in app["programs"] if program["type"] == 1 and program["memory_size"]]
    require(loads, "应用 ELF 缺少 LOAD 段")
    for program in loads:
        in_app = 0x100000 <= program["physical"] and program["physical"] + program["memory_size"] <= 0x1100000
        arena_noload = program["physical"] == 0x10000000 and program["memory_size"] == 0x2000000 and program["file_size"] == 0
        require(program["virtual"] == program["physical"] and (in_app or arena_noload),
                "应用 ELF LOAD 超出已批准 DDR/arena 区域")
    preparation_path, preparation_raw = verify_binding(config["preparation"], "T18 preparation", max_bytes=4 * 1024 * 1024)
    preparation = strict_json(preparation_raw)
    require(type(preparation) is dict, "T18 preparation 顶层必须是对象")
    apis.acceptance.validate_plan(preparation)

    proof_path, proof_raw = verify_binding(config["visibility_proof"], "visibility1 proof", max_bytes=4 * 1024 * 1024)
    review_path, review_raw = verify_binding(config["visibility_review"], "visibility1 review", max_bytes=4 * 1024 * 1024)
    sources = apis.platform.check_static(ROOT)
    apis.platform.check_visibility(ROOT, proof_path, review_path, sources, config["visibility_review"]["sha256"])
    proof = apis.platform.read_json(proof_path)
    proof_elf = proof["runtime_bindings"]["elf"]
    proof_elf_path = apis.platform.relative_file(ROOT, proof_elf["path"])
    app_path = exact_path(bindings["app_elf"]["path"])
    require(proof_elf_path.samefile(app_path) and digest(proof_elf_path.read_bytes()) == proof_elf["sha256"] ==
            bindings["app_elf"]["sha256"], "visibility1 proof 未绑定同一应用 ELF")

    manifest_path, manifest_raw = verify_binding(config["final_platform_manifest"], "最终平台 manifest", max_bytes=8 * 1024 * 1024)
    manifest_result = apis.delivery.check_manifest("evidence", str(manifest_path), str(ROOT))
    require(manifest_result.get("status") == "CHECKS_OK", "最终平台 manifest 机器核验失败")
    manifest = strict_json(manifest_raw)
    require(type(manifest) is dict and type(manifest.get("files")) is list and type(manifest.get("checks")) is list,
            "最终平台 manifest schema 不完整")
    require(any(str(ROOT / item["path"]) == bindings["bit"]["path"] and item["sha256"] == bindings["bit"]["sha256"]
                for item in manifest["files"] if type(item) is dict and "path" in item and "sha256" in item),
            "最终平台 manifest 未绑定部署 bit")
    require(all(item.get("status") in ("PASS", "NOT_APPLICABLE") for item in manifest["checks"]),
            "最终平台 manifest 含失败或未执行检查")
    final_review_path, final_review_raw = verify_binding(config["final_review"], "最终平台独审回执", max_bytes=4 * 1024 * 1024)
    final_review = strict_json(final_review_raw)
    validate_final_review_receipt(final_review, digest(manifest_raw), digest(proof_raw))

    del review_raw, final_review_path
    _validate_serial_config(config["serial"])
    _validate_server_config(config["hw_server"])
    _validate_deadline_profile(config)
    return {"run_dir": run_dir, "deploy_dir": deploy_dir, "build": build,
            "preparation": preparation, "preparation_path": preparation_path,
            "proof_path": proof_path, "review_path": review_path, "manifest_path": manifest_path,
            "final_review_path": exact_path(config["final_review"]["path"]),
            "cold_basis": config["cold_basis"], "approved_basis": approved_basis,
            "csr_reentry": csr_reentry,
            "source_commit": observed}


def _validate_serial_config(value: object) -> None:
    required = {"identity", "baudrate", "bytesize", "parity", "stopbits", "timeout", "write_timeout",
                "rtscts", "dsrdtr", "dtr", "rts"}
    require(type(value) is dict and set(value) == required, "串口配置字段集合错误")
    identity = value["identity"]
    require(type(identity) is dict and set(identity) == {"port", "name", "pnp_device_id", "config_manager_error_code"},
            "串口设备身份字段错误")
    require(type(identity["port"]) is str and re.fullmatch(r"COM[1-9][0-9]*", identity["port"]) is not None and
            type(identity["name"]) is str and identity["name"].endswith("(" + identity["port"] + ")") and
            type(identity["pnp_device_id"]) is str and identity["pnp_device_id"] and
            type(identity["config_manager_error_code"]) is int and identity["config_manager_error_code"] == 0,
            "串口身份必须由 config 声明有效 COM/PNP")
    require(type(value["baudrate"]) is int and value["baudrate"] == 115200 and
            type(value["bytesize"]) is int and value["bytesize"] == 8 and value["parity"] == "N" and
            type(value["stopbits"]) is int and value["stopbits"] == 1 and
            type(value["timeout"]) in (int, float) and value["timeout"] == 0.1 and
            type(value["write_timeout"]) in (int, float) and value["write_timeout"] == 1.0 and
            value["rtscts"] is False and value["dsrdtr"] is False and value["dtr"] is False and value["rts"] is False,
            "串口参数不符合冻结 UART transport")


def _validate_server_config(value: object) -> None:
    required = {"process_id", "executable_path", "creation_time_filetime_utc"}
    require(type(value) is dict and set(value) == required and type(value["process_id"]) is int and
            value["process_id"] > 0 and type(value["executable_path"]) is str and
            Path(value["executable_path"]).is_absolute() and type(value["creation_time_filetime_utc"]) is str and
            value["creation_time_filetime_utc"], "hw_server 身份字段错误")


def validate_final_review_receipt(receipt: object, manifest_sha256: str, proof_sha256: str) -> None:
    """确保最终独审回执只批准同一份 visibility1 清单。"""
    require(type(receipt) is dict and receipt.get("status") == "PASS" and
            receipt.get("role") == "INDEPENDENT_REVIEWER" and
            receipt.get("approved_manifest_sha256") == manifest_sha256 and
            receipt.get("approved_profile_sha256") == proof_sha256 and
            type(receipt.get("visibility_parameter")) is int and receipt["visibility_parameter"] == 1 and
            receipt.get("same_runtime_bsp_mmu_macros") is True and
            receipt.get("only_visibility_parameter_changed") is True,
            "最终 PL 独立回执没有精确批准 visibility1 平台")


def _collect_bindings(value: object, found: dict[str, dict]) -> None:
    """递归收集机器计划中所有精确 path/SHA 文件绑定。"""
    if type(value) is dict:
        if set(value) == {"path", "sha256"} and type(value.get("path")) is str:
            found[value["path"]] = value
        for child in value.values():
            _collect_bindings(child, found)
    elif type(value) is list:
        for child in value:
            _collect_bindings(child, found)


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def save_json_new(path: Path, value: object) -> None:
    """以 UTF-8/LF 独占写入并同步到磁盘。"""
    raw = (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


class Journal:
    """每个运行步骤立即追加到本次部署日志。"""
    def __init__(self, path: Path):
        self.path = path
        self.stream = path.open("x", encoding="utf-8", newline="\n")

    def event(self, name: str, status: str, **details) -> None:
        row = {"time_utc8": datetime.now(TZ).isoformat(), "step": name, "status": status, **details}
        self.stream.write(json.dumps(row, ensure_ascii=False, default=repr) + "\n")
        self.stream.flush()
        os.fsync(self.stream.fileno())

    def call(self, name: str, function, *args, **kwargs):
        started = time.monotonic()
        try:
            result = function(*args, **kwargs)
            self.event(name, "RETURNED", elapsed_seconds=time.monotonic() - started,
                       return_type=type(result).__name__, return_repr=repr(result)[:2000])
            return result
        except BaseException as error:
            self.event(name, "RAISED", elapsed_seconds=time.monotonic() - started,
                       exception=repr(error), traceback=traceback.format_exc())
            raise

    def close(self) -> None:
        if not self.stream.closed:
            self.stream.flush()
            os.fsync(self.stream.fileno())
            self.stream.close()


def execute_board_flow(controller, wire, config: dict, checked: dict, apis,
                       journal: Journal | None = None, *, scope: str = "model", csr_map=None):
    """先完成 T16 冷部署，再通过 T18 完整准入后进入 UART 验收。"""
    require(scope in ("model", "csr"), "scope只能是model或csr")
    try:
        reentry = checked.get("csr_reentry") if scope == "csr" else None
        if reentry is not None:
            def stop_prior_model_app():
                rows = controller.call("session.targets.properties.csr_reentry",
                                       controller.session.targets, "--target_properties")
                current_targets = apis.jtag.validate_targets(rows)
                _same_jtag_target_identity(reentry["model_target_identity"], current_targets)
                _same_jtag_target_identity(reentry["prior_csr_failure"]["target_identity"], current_targets)
                controller.refresh_targets(current_targets)
                controller.gate(both=False)
                before_cpu0 = controller.state("cpu0")
                before_cpu1 = controller.state("cpu1")
                require(before_cpu1.startswith("Stopped"), "CSR重入前CPU1未停止")
                require(before_cpu0 == "Running" or before_cpu0.startswith("Stopped"),
                        "CSR重入当前CPU0状态既非运行也非停机")
                app_path, app_raw = verify_binding(reentry["artifact_bindings"]["app_elf"],
                                                   "CSR重入绑定应用ELF", max_bytes=64 * 1024 * 1024)
                app_elf = apis.elf_parser.parse_elf(app_raw)
                cpsr_data = controller.call("cpu0.rrd.cpsr.csr_reentry", controller.targets["cpu0"].rrd,
                                            "--nvlist", reg="cpsr")
                require(type(cpsr_data) is dict and set(cpsr_data) == {"cpsr"} and
                        type(cpsr_data["cpsr"]) is int and 0 <= cpsr_data["cpsr"] <= 0xFFFFFFFF,
                        "CPU0 CPSR结构化返回类型、字段或32位范围错误")
                cpsr = cpsr_data["cpsr"]
                thumb = bool(cpsr & (1 << 5))
                pc = controller.pc("cpu0")
                require(pc % (2 if thumb else 4) == 0,
                        "CPU0 PC与CPSR指示的ARM/Thumb指令对齐不符")
                read_address = pc & ~3
                word_count = (pc - read_address + 16 + 3) // 4
                observed_words = controller.words(read_address, word_count)
                require(type(observed_words) is list and len(observed_words) == word_count and
                        all(type(word) is int and 0 <= word <= 0xFFFFFFFF for word in observed_words),
                        "CPU0 PC附近DAP读回不是预期的32位指令字数量")
                aligned_bytes = b"".join(word.to_bytes(4, "little") for word in observed_words)
                pc_offset = pc - read_address
                instruction_bytes = aligned_bytes[pc_offset:pc_offset + 16]
                pc_evidence = _validate_app_pc_instructions(app_elf, app_raw, pc, cpsr, instruction_bytes)
                pc_evidence.update(readback_address=read_address, readback_word_count=word_count,
                                   readback_alignment_offset=pc_offset)
                event = {"model_run_id": reentry["model_run_id"],
                         "model_result": reentry["model_result"],
                         "model_input_config": reentry["model_input_config"],
                         "model_jtag_result": reentry["model_jtag_result"],
                         "model_jtag_calls": reentry["model_jtag_calls"],
                         "prior_csr_failure": reentry["prior_csr_failure"],
                         "artifact_bindings": reentry["artifact_bindings"],
                         "current_target_identity": current_targets,
                         "current_app_pc": pc_evidence,
                         "continuity_limit": "历史R02之后无法从本机日志全面证明未发生外部硬件控制；本次仅以当前完整目标链、CPU状态、JTAG启动模式及PC/指令与绑定ELF一致作现场核验。",
                         "before_cpu0": before_cpu0, "before_cpu1": before_cpu1,
                         "stop_status": "NOT_REQUESTED"}
                stop_call_index = None
                if before_cpu0 == "Running":
                    controller.call("cpu0.stop.csr_reentry", controller.targets["cpu0"].stop)
                    stop_call_index = len(controller.record["calls"]) - 1
                    event["stop_status"] = "RETURNED"
                else:
                    event["stop_status"] = "ALREADY_STOPPED"
                after_cpu0 = controller.state("cpu0")
                after_cpu1 = controller.state("cpu1")
                require(after_cpu0.startswith("Stopped") and after_cpu1.startswith("Stopped"),
                        "CSR重入stop后CPU0/CPU1未全部停止")
                event.update(after_cpu0=after_cpu0, after_cpu1=after_cpu1,
                             stop_call_index=stop_call_index)
                controller.record["csr_reentry"] = event
                return event
            reentry_evidence = controller.guarded(stop_prior_model_app)
            if journal:
                journal.event("csr_reentry.stop_running_model_app", "PASS", **reentry_evidence)
        controller.select_and_gate()
        controller.system_reset_stop(checked["cold_basis"])
        if csr_map is not None:
            helper, helper_config, helper_record, session, owner = csr_map
            helper.register_csr_debug_map(helper_config, helper_record, journal,
                                          session, controller, owner)
            if journal:
                journal.event("csr_debug_map.registered", "PASS",
                              helper_sha256=CSR_MAP_HELPER_SOURCE_SHA256,
                              debug_memory_map=helper_record.get("debug_memory_map"))
        controller.deploy()
        require(controller.configured and controller.postconfigured and controller.app_running and not controller.failed,
                "T16 EOS/postconfig/app 状态未全部通过")
        if journal:
            journal.event("deployment_ready", "PASS", postconfigured=controller.postconfigured,
                          app_running=controller.app_running, configured=controller.configured)
        source_sha = checked["build"]["source_sha256"]["vitis/s2b_inference_app.c"]
        xsa_sha = checked["build"]["xsa_sha256"]
        banner = wire.banner(source_sha, xsa_sha)
        require(type(banner) is dict and set(banner) == {"bytes", "sha256", "text"} and
                type(banner["bytes"]) is int and banner["bytes"] > 0 and
                type(banner["sha256"]) is str and re.fullmatch(r"[0-9a-f]{64}", banner["sha256"]) and
                type(banner["text"]) is str, "真实启动banner返回字段错误")
        if journal:
            journal.event("uart.banner", "PASS", **banner)
        rx_file = getattr(wire, "rx_file", None)
        prefix_binding = None
        if rx_file is not None and getattr(rx_file, "name", None):
            rx_path = exact_path(rx_file.name)
            rx_file.flush()
            with rx_path.open("rb") as stream:
                prefix = stream.read(banner["bytes"])
            require(len(prefix) == banner["bytes"] and digest(prefix) == banner["sha256"],
                    "真实UART原始RX启动前缀与banner返回摘要不一致")
            prefix_binding = {"path": str(rx_path), "offset": 0,
                              "bytes": len(prefix), "sha256": digest(prefix)}
        wire_type = getattr(getattr(apis, "jtag", None), "JtagWireSession", None)
        require(wire_type is None or type(wire) is not wire_type or prefix_binding is not None,
                "正式UART wire未提供可绑定的真实RX banner前缀")
        args = (controller, wire, config["build_details"]["path"], checked["proof_path"],
                checked["review_path"], config["visibility_review"]["sha256"],
                checked["manifest_path"], checked["final_review_path"], config["final_review"]["sha256"])
        admission = apis.acceptance.admit(*args)
        if journal:
            journal.event("s2b_t18_admit", "PASS", uart_tx_count=len(getattr(wire, "sent_requests", {})))
        if scope == "model":
            result = apis.acceptance.execute(
                controller, wire, checked["preparation_path"], checked["run_dir"],
                build_details=config["build_details"]["path"], visibility_proof=checked["proof_path"],
                review=checked["review_path"], review_sha256=config["visibility_review"]["sha256"],
                final_platform_manifest=checked["manifest_path"], final_review=checked["final_review_path"],
                final_review_sha256=config["final_review"]["sha256"], core_timeout=config["core_timeout"],
                drain_timeout=config["drain_timeout"])
        elif scope == "csr":
            result = apis.csr_flow.execute(controller, wire, config, checked, apis,
                                           admission, journal)
            if result.get("status") != "PASS_CSR_RECOVERY_SCOPE_ONLY":
                error = RunnerError("CSR固定流程失败；原始阶段异常见acceptance结果")
                error.csr_flow_result = result
                raise error
        else:
            raise RunnerError("scope 只能是model或csr")
        result["startup_banner"] = {"returned": banner, "rx_prefix": prefix_binding}
        return result
    except BaseException as error:
        if wire is not None:
            wire.failed = True
        if controller is not None and not controller.failed:
            controller.failed = True
            try:
                controller.fail_stop()
                if journal:
                    journal.event("controller.fail_stop", "RETURNED")
            except BaseException as stop_error:
                if journal:
                    journal.event("controller.fail_stop", "RAISED", exception=repr(stop_error))
        if journal:
            journal.event("board_flow", "FAILED", exception=repr(error), traceback=traceback.format_exc(),
                          uart_tx_count=len(getattr(wire, "sent_requests", {})) if wire is not None else 0)
        if isinstance(error, RunnerError):
            raise
        raise RunnerError("部署或模型验收阶段异常；已锁存失败状态") from error


def _normalize_rows(value) -> list:
    if value is None:
        return []
    return value if type(value) is list else [value]


def collect_system_identity() -> dict:
    """只读采集 hw_server 监听与串口 PNP 身份。"""
    command = r"""$ErrorActionPreference='Stop'; [Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false)
$servers=@(Get-CimInstance Win32_Process -Filter "Name='hw_server.exe'" | Select-Object ProcessId,ExecutablePath,@{Name='CreationTimeFileTimeUtc';Expression={[string]$_.CreationDate.ToFileTimeUtc()}})
$listeners=@(Get-NetTCPConnection -LocalPort 3121 -State Listen -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,OwningProcess)
$ports=@(Get-CimInstance Win32_PnPEntity -Filter "PNPClass='Ports'" | Select-Object Name,PNPDeviceID,ConfigManagerErrorCode)
[pscustomobject]@{servers=$servers;listeners=$listeners;ports=$ports}|ConvertTo-Json -Depth 5"""
    result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", command], capture_output=True, timeout=30)
    require(result.returncode == 0, "系统设备身份采集失败：" + repr(result.stderr))
    data = strict_json(result.stdout.decode("utf-8-sig").encode("utf-8"))
    require(type(data) is dict, "系统身份 JSON 顶层错误")
    snapshot = {name: _normalize_rows(data.get(name)) for name in ("servers", "listeners", "ports")}
    require(set(data) == set(snapshot), "系统身份包含未知或缺失字段")
    return {"command": command, "native_exit_code": result.returncode, "stdout_sha256": digest(result.stdout),
            "stderr_sha256": digest(result.stderr), "snapshot": snapshot}


def validate_system_identity(actual: dict, config: dict) -> dict:
    """核对动态进程、TCP 监听和 config 声明的 COM/PNP 身份。"""
    data = actual["snapshot"]
    servers, listeners, ports = data["servers"], data["listeners"], data["ports"]
    expected_server, expected_uart = config["hw_server"], config["serial"]["identity"]
    require(type(servers) is list and len(servers) == 1, "必须唯一明确的 hw_server 进程")
    server = servers[0]
    expected = {"ProcessId": expected_server["process_id"], "ExecutablePath": expected_server["executable_path"],
                "CreationTimeFileTimeUtc": expected_server["creation_time_filetime_utc"]}
    require(all(server.get(key) == value for key, value in expected.items()), "hw_server 进程身份与 config 不匹配")
    require(type(listeners) is list and listeners and all(row.get("LocalPort") == 3121 and
            row.get("OwningProcess") == expected_server["process_id"] for row in listeners),
            "TCP 3121 listener 不唯一归属 config 声明进程")
    matches = [row for row in ports if row.get("Name") == expected_uart["name"] and
               row.get("PNPDeviceID") == expected_uart["pnp_device_id"]]
    port_matches = [row for row in ports if str(row.get("Name", "")).endswith("(" + expected_uart["port"] + ")")]
    require(len(matches) == len(port_matches) == 1 and
            matches[0].get("ConfigManagerErrorCode") == expected_uart["config_manager_error_code"] == 0,
            "config 声明的串口 COM/PNP 身份缺失、异常或有歧义")
    return {"server": server, "listeners": listeners, "uart": matches[0]}


def _verify_native_images(config: dict) -> None:
    """核对官方共享 Python alias 与两个分别加载的原生映像。"""
    require(os.name == "nt", "官方 Vitis 原生模块核验要求 Windows")
    names = ("xv_pycommontasks", "xv_hsmpytasks")
    require(all(name in sys.modules for name in names), "实际 XSDB 未加载完整官方原生模块")
    module = sys.modules[names[0]]
    require(module is sys.modules[names[1]] and module.__name__ == "vivado", "官方原生 Python alias 不匹配")
    spec = getattr(module, "__spec__", None)
    loader = getattr(spec, "loader", None)
    require(spec is not None and spec.name == "xv_hsmpytasks" and
            type(loader) is importlib.machinery.ExtensionFileLoader and loader.name == "xv_hsmpytasks",
            "官方原生 Python module spec/loader 不匹配")
    sdk_init = exact_path(config["runtime"]["sdk_init"]["path"], "file")
    native_root = sdk_init.parent.parent.parent / "lib/win64.o"
    final_module = exact_path(native_root / "xv_hsmpytasks.pyd")
    require(exact_path(module.__file__) == final_module and exact_path(spec.origin) == final_module and
            exact_path(loader.path) == final_module, "原生 Python alias 元数据来源不匹配")
    ctypes = importlib.import_module("ctypes")
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetModuleHandleW.argtypes = [ctypes.c_wchar_p]
    kernel.GetModuleHandleW.restype = ctypes.c_void_p
    kernel.GetModuleFileNameW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_ulong]
    kernel.GetModuleFileNameW.restype = ctypes.c_ulong
    handles = []
    for name in names:
        expected = exact_path(native_root / (name + ".pyd"))
        binding_path, raw = verify_binding(config["runtime"]["sdk_files"][name],
                                            "原生 SDK 模块 " + name, within_root=False)
        require(binding_path == expected, "原生 SDK 模块路径不匹配：" + name)
        handle = kernel.GetModuleHandleW(name + ".pyd")
        require(bool(handle), "原生 SDK 映像未加载：" + name)
        buffer = ctypes.create_unicode_buffer(32768)
        length = kernel.GetModuleFileNameW(handle, buffer, len(buffer))
        require(0 < length < len(buffer) and exact_path(buffer.value) == expected,
                "进程内已加载原生 SDK 映像路径不匹配：" + name)
        require(digest(raw) == config["runtime"]["sdk_files"][name]["sha256"],
                "原生 SDK 模块 SHA 不匹配：" + name)
        handles.append(handle)
    require(len(set(handles)) == len(names), "两个原生 SDK 映像意外共用同一加载句柄")


def _verify_loaded_runtime(xsdb, serial, config: dict, expected_session=None) -> None:
    """核对实际导入的 XSDB/pyserial 文件与预先验证的原字节闭包。"""
    runtime = config["runtime"]
    require(exact_path(xsdb.__file__) == exact_path(runtime["sdk_init"]["path"]), "实际 XSDB 入口来源漂移")
    require(exact_path(serial.__file__) == exact_path(runtime["pyserial_init"]["path"]), "实际 pyserial 入口来源漂移")
    require(serial.__version__ == runtime["pyserial_version"], "实际 pyserial 版本不匹配")
    sdk_map = runtime["sdk_files"]
    cli_root = exact_path(runtime["sdk_init"]["path"]).parent.parent
    product_root = cli_root.parent
    sdk_roots = (cli_root, cli_root / "python-packages/site-packages", cli_root / "python-packages/win64",
                 product_root / "scripts/python_pkg", product_root / "lib/win64.o")
    for name, module in list(sys.modules.items()):
        module_path = getattr(module, "__file__", None)
        if not module_path:
            continue
        actual = Path(module_path).absolute()
        controlled = name.startswith(("xsdb.", "tcf.")) or any(actual.is_relative_to(root) for root in sdk_roots)
        if not controlled:
            continue
        if name in ("xv_pycommontasks", "xv_hsmpytasks"):
            continue
        require(name in sdk_map, "实际 SDK 模块未列入源码闭包：" + name)
        binding = sdk_map[name]
        bound_path, raw = verify_binding(binding, "实际 SDK 模块 " + name, within_root=False)
        require(exact_path(actual) == bound_path and digest(raw) == binding["sha256"],
                "实际 SDK 模块路径/SHA 不匹配：" + name)
    _verify_native_images(config)
    require(getattr(xsdb, "debug_session", None) is expected_session, "XSDB session 所有权与本入口状态不符")
    dispatch = sys.modules.get("xsdb.xsdb_debug_session")
    if dispatch is not None:
        require(getattr(dispatch, "debug_session_int_obj", None) is expected_session,
                "XSDB dispatch session 所有权与本入口状态不符")


class ProductionRuntime:
    """只在 config 完整预检通过后导入设备运行时。"""
    def identity(self, config: dict) -> dict:
        snapshot = collect_system_identity()
        return {"capture": snapshot, "validated": validate_system_identity(snapshot, config)}

    def modules(self, config: dict):
        init_path = exact_path(config["runtime"]["sdk_init"]["path"])
        package_root = str(init_path.parent.parent)
        if package_root not in sys.path:
            sys.path.insert(0, package_root)
        xsdb = importlib.import_module("xsdb")
        serial_root = str(exact_path(config["runtime"]["pyserial_init"]["path"]).parent.parent)
        if serial_root not in sys.path:
            sys.path.insert(0, serial_root)
        serial = importlib.import_module("serial")
        _verify_loaded_runtime(xsdb, serial, config)
        return xsdb, serial

    def session(self, xsdb, serial_module, config: dict, journal: Journal, on_session):
        session = journal.call("xsdb.start_debug_session", xsdb.start_debug_session)
        on_session(session)
        dispatch = sys.modules.get("xsdb.xsdb_debug_session")
        require(dispatch is not None and getattr(xsdb, "debug_session", None) is session and
                getattr(dispatch, "debug_session_int_obj", None) is session,
                "XSDB 返回 session 非本入口新建对象")
        _verify_loaded_runtime(xsdb, serial_module, config, expected_session=session)
        channel = journal.call("session.connect", session.connect, url="TCP:localhost:3121", server="hw_server")
        require(type(session).__name__ == "Session" and getattr(session, "_curchan", None) is channel,
                "XSDB session/channel 所有权不匹配")
        _verify_loaded_runtime(xsdb, serial_module, config, expected_session=session)
        return session, channel

    def serial(self, serial_module, config: dict, journal: Journal, on_port):
        settings = config["serial"]
        port = journal.call("serial.construct_closed", serial_module.Serial, port=None,
                            baudrate=settings["baudrate"], bytesize=settings["bytesize"],
                            parity=settings["parity"], stopbits=settings["stopbits"], timeout=settings["timeout"],
                            write_timeout=settings["write_timeout"], rtscts=settings["rtscts"], dsrdtr=settings["dsrdtr"])
        on_port(port)
        port.dtr, port.rts = settings["dtr"], settings["rts"]
        port.port = settings["identity"]["port"]
        journal.call("serial.open", port.open)
        require(port.is_open and port.port == settings["identity"]["port"], "实际串口未按 config 打开")
        return port


def _bound_file(path: Path) -> dict:
    actual = exact_path(path)
    return {"path": str(actual), "sha256": digest(actual.read_bytes())}


def _manifest_file(role: str, path: Path) -> dict:
    return {"path": _relative(exact_path(path)), "sha256": _bound_file(path)["sha256"], "role": role}


def finalize_evidence(config: dict, checked: dict, apis, config_raw: bytes, record: dict,
                      journal: Journal, controller, wire, runtime_objects: dict) -> dict:
    """封装部署、串口与 T18 产物，随后运行当前 Run 的清单核验。"""
    run_dir = checked["run_dir"]
    if not run_dir.exists():
        run_dir.mkdir()
        save_json_new(run_dir / "acceptance_result.json", {
            "schema_version": 1, "status": "BLOCKED_BEFORE_TX", "hardware_execution": "NOT_RUN",
            "error": record.get("error", "部署或准入未完成"),
        })
        apis.acceptance.evidence_manifest(run_dir, "BLOCKED", "部署、postconfig 或完整准入未通过；未发送 UART 请求。")
    require(run_dir.is_dir(), "T18 evidence Run 目录未创建")
    orchestrator_dir = run_dir / "orchestrator"
    if not orchestrator_dir.exists():
        orchestrator_dir.mkdir()
    with (orchestrator_dir / "input_config.json").open("xb") as stream:
        stream.write(config_raw)
        stream.flush()
        os.fsync(stream.fileno())
    if not (run_dir / "orchestrator_result.json").exists():
        save_json_new(run_dir / "orchestrator_result.json", record)

    manifest_path = run_dir / "delivery_manifest.json"
    require(manifest_path.is_file(), "T18 delivery_manifest.json 缺失")
    manifest = strict_json(manifest_path.read_bytes())
    require(type(manifest) is dict and type(manifest.get("files")) is list, "T18 清单文件字段错误")
    files_by_path = {}
    for path in sorted(run_dir.rglob("*")):
        if path.is_file() and path != manifest_path:
            files_by_path[_relative(path)] = _manifest_file("result", path)
    for name, item in config["bindings"].items():
        if name == "sdk_target":
            continue
        path, _ = verify_binding(item, "controller " + name)
        files_by_path[_relative(path)] = _manifest_file("source", path)
    for path in (Path(apis.acceptance.__file__), Path(apis.jtag.__file__), Path(__file__),
                 Path(apis.transport.__file__), Path(apis.platform.__file__), Path(apis.delivery.__file__)):
        actual = exact_path(path)
        files_by_path[_relative(actual)] = _manifest_file("source", actual)
    if record.get("scope") == "csr":
        for path in (Path(apis.csr_flow.__file__),
                     exact_path(ROOT / "verification/s2b_csr_board_acceptance.py"),
                     exact_path(ROOT / "verification/s2b_csr_busy_observer.py")):
            files_by_path[_relative(path)] = _manifest_file("source", path)
    external_inputs = {}
    for key in ("preparation", "build_details", "visibility_proof", "visibility_review",
                "final_platform_manifest", "final_review", "g0_basis", "cold_basis"):
        path, _ = verify_binding(config[key], key)
        external_inputs[str(path)] = config[key]
    _collect_bindings(checked["preparation"], external_inputs)
    for path in sorted(checked["deploy_dir"].rglob("*")):
        if path.is_file():
            external_inputs[str(exact_path(path))] = _bound_file(path)
    for item in record.get("acceptance", {}).get("t20_outputs", []):
        path, _ = verify_binding(item, "T20 CSR输出", within_root=False)
        external_inputs[str(path)] = item
    for binding in external_inputs.values():
        path, _ = verify_binding(binding, "T18 输入/运行日志", within_root=False)
        if not path.is_relative_to(ROOT):
            record.setdefault("inputs_outside_repository", []).append(binding)
            continue
        relative = _relative(path)
        existing = files_by_path.get(relative)
        if existing:
            require(existing["sha256"] == binding["sha256"], "T18 文件重复绑定 SHA 不同：" + relative)
        else:
            files_by_path[relative] = _manifest_file("input", path)
    manifest["files"] = [files_by_path[key] for key in sorted(files_by_path)]
    raw = (json.dumps(manifest, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")
    with manifest_path.open("wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    result = apis.delivery.check_manifest("evidence", str(manifest_path), str(ROOT))
    record["delivery_manifest_check"] = result
    if result.get("status") != "CHECKS_OK":
        record.update(status="FAILED", native_exit_code=2,
                      evidence_packaging_error="首次 delivery manifest 核验失败")
    record["deployment_log"] = _bound_file(checked["deploy_dir"] / "orchestrator_calls.jsonl")
    if controller is not None and (checked["deploy_dir"] / "jtag_result.json").is_file():
        record["jtag_result"] = _bound_file(checked["deploy_dir"] / "jtag_result.json")
    if wire is not None:
        record["uart_raw"] = {"rx": _bound_file(Path(wire.rx_file.name)), "tx": _bound_file(Path(wire.tx_file.name))}
    cleanup_names = {row.get("step") for row in record.get("cleanup_steps", []) if row.get("status") == "PASS"}
    record["owned_resources"] = {"serial_open": bool(runtime_objects.get("port") and runtime_objects["port"].is_open),
                                  "session_connected": bool(runtime_objects.get("session") and
                                                             "session.disconnect" not in cleanup_names),
                                  "hw_server": "borrowed; runner does not start, stop, or terminate it"}
    with (run_dir / "orchestrator_result.json").open("wb") as stream:
        stream.write((json.dumps(record, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8"))
        stream.flush()
        os.fsync(stream.fileno())
    summary_relative = _relative(run_dir / "orchestrator_result.json")
    summary_rows = [item for item in manifest["files"] if item.get("path") == summary_relative]
    require(len(summary_rows) == 1, "最终清单未唯一声明 orchestrator_result.json")
    summary_rows[0]["sha256"] = _bound_file(run_dir / "orchestrator_result.json")["sha256"]
    with manifest_path.open("wb") as stream:
        stream.write((json.dumps(manifest, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8"))
        stream.flush()
        os.fsync(stream.fileno())
    result = apis.delivery.check_manifest("evidence", str(manifest_path), str(ROOT))
    return result


def run(config_path: str | Path, *, runtime=None, scope: str = "model") -> dict:
    """显式 config 是唯一可启动硬件入口；调用者不得用环境变量替代。"""
    require(scope in ("model", "csr"), "scope 只能是model或csr")
    config_file = exact_path(config_path)
    require(config_file.is_relative_to(ROOT), "显式 config 必须位于仓库内的隔离证据目录")
    require(config_file.stat().st_size <= 1024 * 1024, "config 超过 1 MiB")
    config_raw = config_file.read_bytes()
    config = strict_json(config_raw)
    validate_preflight_basis(config)
    csr_reentry = validate_csr_reentry(config, scope=scope)
    if scope == "csr":
        _verify_csr_flow_sources()
    csr_map_helper, csr_map_source = load_pinned_csr_map_helper()
    apis = load_apis(scope)
    checked = validate_v1_inputs(config, apis, scope=scope)
    checked["csr_reentry"] = csr_reentry
    runtime = runtime or ProductionRuntime()
    checked["deploy_dir"].mkdir()
    deploy_dir = exact_path(checked["deploy_dir"], "directory")
    journal = Journal(deploy_dir / "orchestrator_calls.jsonl")
    with (deploy_dir / "input_config.json").open("xb") as stream:
        stream.write(config_raw)
        stream.flush()
        os.fsync(stream.fileno())
    record = {"schema_version": 1, "status": "IN_PROGRESS", "scope": scope,
              "hardware_execution": "REQUESTED_BY_EXPLICIT_CONFIG",
              "source_commit": checked["source_commit"], "run_id": config["run_id"],
              "started_at_utc8": datetime.now(TZ).isoformat(), "identity_snapshots": [],
              "cleanup_steps": [], "cleanup_errors": [], "limitations": [
                  "本入口不执行 Vitis build；build_details 与全部部署产物须预先绑定。",
                  "只核验 visibility1 文件与独审回执绑定；独立 Reviewer 身份由总控确认。",
                  ("本入口只完成 T18 109 样本及 1000 次连续请求，不替代 T16 复位、CSR 负向或阶段验收。"
                   if scope == "model" else "本scope只执行固定CSR恢复顺序，不代表109样本或1000次压力完成。"),
                  "硬件进程峰值内存未测。"]}
    csr_map_config = {"sdk_files": config["runtime"]["sdk_files"]}
    csr_map_record = {"verified_inputs": {"compat_artifacts": {
        "implemented_xsa": config["bindings"]["xsa"]}}, "cleanup_errors": []}
    csr_map_owner = {}
    record["csr_debug_map_helper"] = csr_map_source
    objects = {"xsdb": None, "serial": None, "session": None, "channel": None,
               "controller": None, "port": None, "wire": None, "rx": None, "tx": None,
               "csr_map": None}
    failure = None
    started = time.monotonic()
    try:
        for label in ("before_runtime",):
            identity = journal.call("identity." + label, runtime.identity, config)
            record["identity_snapshots"].append({"label": label, **identity})
        objects["xsdb"], objects["serial"] = journal.call("runtime.import_bound_modules", runtime.modules, config)
        objects["session"], objects["channel"] = runtime.session(
            objects["xsdb"], objects["serial"], config, journal,
            lambda session: objects.__setitem__("session", session))
        identity = journal.call("identity.after_connect", runtime.identity, config)
        record["identity_snapshots"].append({"label": "after_connect", **identity})
        objects["controller"] = apis.jtag.JtagController(objects["session"], config["bindings"], deploy_dir)
        objects["csr_map"] = (csr_map_helper, csr_map_config, csr_map_record,
                               objects["session"], csr_map_owner)
        uart_identity = journal.call("identity.before_serial", runtime.identity, config)
        record["identity_snapshots"].append({"label": "before_serial", **uart_identity})
        objects["port"] = runtime.serial(objects["serial"], config, journal,
                                          lambda port: objects.__setitem__("port", port))
        identity = journal.call("identity.after_serial_open", runtime.identity, config)
        record["identity_snapshots"].append({"label": "after_serial_open", **identity})
        objects["rx"] = (deploy_dir / "uart_rx_raw.bin").open("xb")
        objects["tx"] = (deploy_dir / "uart_tx_raw.bin").open("xb")
        objects["wire"] = apis.jtag.JtagWireSession(objects["port"], objects["rx"], objects["tx"],
                                                     response_timeout=config["response_timeout_seconds"])
        result = execute_board_flow(objects["controller"], objects["wire"], config, checked, apis,
                                    journal, scope=scope, csr_map=objects["csr_map"])
        record["acceptance"] = result
        record["status"] = result.get("status", "PASS_MODEL_CORPUS_AND_STRESS_ONLY" if scope == "model"
                                      else "PASS_CSR_RECOVERY_SCOPE_ONLY")
    except BaseException as error:
        failure = error
        record.update(status="FAILED", error=repr(error), traceback=traceback.format_exc())
        partial_acceptance = getattr(error, "csr_flow_result", None)
        if type(partial_acceptance) is dict:
            record["acceptance"] = partial_acceptance
        if objects["wire"] is not None:
            objects["wire"].failed = True
        if objects["controller"] is not None and not objects["controller"].failed:
            objects["controller"].failed = True
            try:
                objects["controller"].fail_stop()
                record["cleanup_steps"].append({"step": "failure_fail_stop", "status": "RETURNED"})
            except BaseException as stop_error:
                record["cleanup_errors"].append({"step": "failure_fail_stop", "error": repr(stop_error)})
    finally:
        port = objects["port"]
        if port is not None:
            try:
                if port.is_open:
                    journal.call("cleanup.serial.close", port.close)
                require(not port.is_open, "serial.close 返回后设备仍打开")
                record["cleanup_steps"].append({"step": "serial.close", "status": "PASS"})
            except BaseException as error:
                record["cleanup_errors"].append({"step": "serial.close", "error": repr(error)})
                failure = failure or error
                record["status"] = "FAILED"
        for name in ("rx", "tx"):
            stream = objects[name]
            if stream is not None:
                try:
                    stream.flush()
                    os.fsync(stream.fileno())
                    stream.close()
                    require(stream.closed, name + " stream 仍打开")
                    record["cleanup_steps"].append({"step": name + ".close", "status": "PASS"})
                except BaseException as error:
                    record["cleanup_errors"].append({"step": name + ".close", "error": repr(error)})
                    failure = failure or error
                    record["status"] = "FAILED"
        controller = objects["controller"]
        if controller is not None and record["cleanup_errors"] and not controller.failed:
            controller.failed = True
            try:
                journal.call("cleanup.failure_fail_stop", controller.fail_stop)
                record["cleanup_steps"].append({"step": "failure_fail_stop", "status": "PASS"})
            except BaseException as error:
                record["cleanup_errors"].append({"step": "failure_fail_stop", "error": repr(error)})
                failure = failure or error
        if controller is not None:
            try:
                journal.call("cleanup.controller.close", controller.close)
                require(controller.log.closed, "JtagController.close 返回后日志仍打开")
                if controller.failed or controller.record.get("cleanup_errors"):
                    raise RunnerError("JTAG controller 或自有断点清理失败")
                record["cleanup_steps"].append({"step": "controller.close", "status": "PASS"})
            except BaseException as error:
                record["cleanup_errors"].append({"step": "controller.close", "error": repr(error)})
                failure = failure or error
                record["status"] = "FAILED"
                if not controller.log.closed:
                    snapshot_path = checked["deploy_dir"] / "jtag_close_failure_snapshot.json"
                    try:
                        save_json_new(snapshot_path, controller.record)
                        controller.log.close()
                    except BaseException as snapshot_error:
                        record["cleanup_errors"].append({"step": "controller.partial_log.close",
                                                          "error": repr(snapshot_error)})
        csr_map = objects["csr_map"]
        if csr_map is not None:
            helper, helper_config, helper_record, map_session, owner = csr_map
            if owner.get("attempted"):
                try:
                    journal.call("cleanup.csr_debug_map.clear", helper.clear_csr_debug_map,
                                 helper_config, helper_record, journal, map_session, owner)
                    record["cleanup_steps"].append({"step": "csr_debug_map.clear", "status": "PASS"})
                except BaseException as error:
                    record["cleanup_errors"].append({"step": "csr_debug_map.clear", "error": repr(error)})
                    failure = failure or error
                    record["status"] = "FAILED"
            else:
                record["cleanup_steps"].append({"step": "csr_debug_map.clear", "status": "NOT_NEEDED"})
            if type(helper_record.get("debug_memory_map")) is dict:
                record["debug_memory_map"] = helper_record["debug_memory_map"]
            for error in helper_record.get("cleanup_errors", []):
                record["cleanup_errors"].append({"step": "csr_debug_map.internal_cleanup",
                                                  **error})
                failure = failure or RunnerError("CSR debug map 内部清理失败")
                record["status"] = "FAILED"
        session = objects["session"]
        if session is not None:
            try:
                kwargs = {"chan": objects["channel"]} if objects["channel"] is not None else {}
                journal.call("cleanup.session.disconnect", session.disconnect, **kwargs)
                record["cleanup_steps"].append({"step": "session.disconnect", "status": "PASS"})
            except BaseException as error:
                record["cleanup_errors"].append({"step": "session.disconnect", "error": repr(error)})
                failure = failure or error
                record["status"] = "FAILED"
        xsdb = objects["xsdb"]
        if xsdb is not None:
            try:
                journal.call("cleanup.xsdb.dispose", xsdb.dispose)
                record["cleanup_steps"].append({"step": "xsdb.dispose", "status": "PASS"})
            except BaseException as error:
                record["cleanup_errors"].append({"step": "xsdb.dispose", "error": repr(error)})
                failure = failure or error
                record["status"] = "FAILED"
        try:
            identity = journal.call("identity.after_cleanup", runtime.identity, config)
            record["identity_snapshots"].append({"label": "after_cleanup", **identity})
        except BaseException as error:
            record["cleanup_errors"].append({"step": "identity.after_cleanup", "error": repr(error)})
            failure = failure or error
            record["status"] = "FAILED"
        record.update(finished_at_utc8=datetime.now(TZ).isoformat(), elapsed_seconds=time.monotonic() - started,
                      native_exit_code=2 if failure else 0)
        try:
            journal.close()
        except BaseException as error:
            record["cleanup_errors"].append({"step": "journal.close", "error": repr(error)})
            failure = failure or error
            record["status"] = "FAILED"

    try:
        manifest_result = finalize_evidence(config, checked, apis, config_raw, record, journal,
                                            objects["controller"], objects["wire"], objects)
        record["delivery_manifest_check"] = manifest_result
        if manifest_result.get("status") != "CHECKS_OK":
            record["status"] = "FAILED"
            failure = failure or RunnerError("最终 T18 delivery manifest 核验失败")
        if record["cleanup_errors"]:
            record["status"] = "FAILED"
            failure = failure or RunnerError("一个或多个自有资源清理失败")
        if record["status"] == "IN_PROGRESS":
            record["status"] = "PASS_MODEL_CORPUS_AND_STRESS_ONLY" if scope == "model" else "PASS_CSR_RECOVERY_SCOPE_ONLY"
    except BaseException as error:
        failure = failure or error
        record.update(status="FAILED", evidence_packaging_error=repr(error),
                      evidence_packaging_traceback=traceback.format_exc())
    if failure is not None:
        raise RunnerError("S2B-T18 部署/验收失败；原始记录保留于 " + str(checked["deploy_dir"])) from failure
    return record


def main(argv=None) -> int:
    """只接受显式 --config；无配置、导入和 --help 不加载硬件模块。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True,
                        help="由总控生成并逐文件绑定的 S2B-T18 visibility1 部署配置")
    parser.add_argument("--scope", choices=("model", "csr"), default="model",
                        help="固定验收scope；默认model，csr只执行CSR恢复序列")
    args = parser.parse_args(argv)
    record = run(args.config, scope=args.scope)
    print(json.dumps({"status": record["status"], "native_exit_code": record["native_exit_code"],
                      "run_id": record["run_id"], "delivery_manifest_check": record.get("delivery_manifest_check")},
                     ensure_ascii=False))
    return record["native_exit_code"]


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RunnerError, OSError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2)
