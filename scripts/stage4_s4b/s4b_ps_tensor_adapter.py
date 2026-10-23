#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S4-B PS 张量诊断 adapter。

CLI 只提供离线 prepare/validate。硬件 API 仅接受外部交接的 XSDB session、UART
stream 与逐字节记录文件；它不创建、连接、关闭或释放任何硬件服务。
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import difflib
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import struct
import subprocess
import sys
import time
import traceback
import uuid
import zipfile
from typing import Any, BinaryIO, Mapping, Sequence


TZ_UTC8 = timezone(timedelta(hours=8))
DEFAULT_BUILD_RUN_ID = "s4b_ps_tensor_20261023_r13"
BUILD_RUN_ID_PATTERN = re.compile(r"s4b_ps_tensor_20261023_r[0-9]{2,3}")
HANDOFF_SOURCE_PATH = ".codex/STATE.md"
HANDOFF_SOURCE_KIND = "committed_project_controller_state_handoff"
HANDOFF_RECORD_KIND = "s4b_hardware_session_handoff"
HANDOFF_OFFER_TASK_MARKER = "S4-B-REAL-02B::s4b_hardware_session_handoff"
HANDOFF_CLAIM_TASK_MARKER = "S4-B-REAL-02B::s4b_hardware_session_claim"
HANDOFF_CLAIM_KIND = "s4b_hardware_session_claim"
HANDOFF_CLAIM_SOURCE_KIND = "committed_stage_claim_receipt"
HANDOFF_TRUSTED_SOURCE_ROOT = Path(r"D:\FPGA_Competition")
HANDOFF_TRUSTED_SOURCE_BRANCH = "main"
HANDOFF_TRUSTED_SENDER = "DSH"
HANDOFF_TRUSTED_RECEIVER_ROOT = Path(r"D:\codex-worktrees\w4")
HANDOFF_TRUSTED_RECEIVER_BRANCH = "stage4-infer-prep"
HANDOFF_FIELDS = (
    "任务", "负责人", "工作树/分支", "起始提交", "允许修改范围", "未提交改动归属",
    "让出声明", "心跳(UTC+8)", "证据入口", "恢复命令", "状态/下一接手方",
)
DIAGNOSTIC_OPERATIONS = frozenset({
    "deploy", "OP_WEIGHTS", "OP_RUN", "double_read_trace_export", "stop_owned_cpu0",
})
FROZEN_2B_COMMIT = "07c3d3958578b9cc9d3b8eae3758711fe08724c2"
FROZEN_TOOL_SHA256 = {
    "verification/s2b_board_jtag.py": "dbd1de2241518e679312746a7386c7e5fb1a5a2e242b88dff052b1ca8907b0c6",
    "verification/s2b_board_transport.py": "7dda231e2888c0ed9d95952dcba4d41c9eaf7423e008e4d179b3f7d2c5f0b334",
    "verification/check_s2b_ps_smoke_layout.py": "6c12023cc9660d392a0f3e393df2ebaf425af8a4cbb51886a35749d0c6fa0f77",
    "verification/check_stage_delivery.py": "788ddcef961cab1a1db917292abbceb41dc6957ca4b8f1c76841158ddc48c112",
}
TOOL_MODULE_NAMES = (
    "s2b_board_jtag",
    "s2b_board_transport",
    "check_s2b_ps_smoke_layout",
    "check_stage_delivery",
)
RECOVERY_INIT_MEMBER = "bundle/workspace/reference/init.elf"
RECOVERY_BUNDLE_MANIFEST = "bundle_manifest.json"
RECOVERY_BUNDLE_MEMBER_COUNT = 85
RECOVERY_BUNDLE_MEMBER_PATHSET_SHA256 = "fd1c9512efa2fcacf6c4bc89c547d4fa82311bd3eaa854b074c9ee019959bce2"
TRACE_HEADER_BYTES = 144
TRACE_RECORD_BYTES = 184
TRACE_CAPACITY = 1000
TRACE_RECORDS_BYTES = TRACE_RECORD_BYTES * TRACE_CAPACITY
TRACE_SNAPSHOT_BYTES = TRACE_HEADER_BYTES + TRACE_RECORDS_BYTES
TRACE_HEADER_STRUCT = struct.Struct("<36I")
DUMP_HEADER = struct.Struct("<8sIIIII")
TRACE_MAGIC = 0x53345054
TRACE_SCHEMA_VERSION = 1
TRACE_RUN_ACTIVE_WORD = 17
TRACE_CSR_STATE_MASK = 0x7
TRACE_CSR_OWNER_PL = 1 << 8
TRACE_CSR_HEAD_VALID = 1 << 9
TRACE_CSR_SAFE_REUSE = 1 << 10
TRACE_CSR_TERMINAL = 1 << 11
TRACE_CSR_AXI_PENDING = 1 << 12
TRACE_CSR_FIRST_PENDING = 1 << 13
TRACE_CSR_DONE_SAFE = 4
TRACE_CSR_ERROR_SAFE = 5
TRACE_RESPONSE_OK = 0
TRACE_UART_SEND_SUCCEEDED = 2
TRACE_ACK_SUCCEEDED = 1
TRACE_INPUT_FORMAT_INT8_CHW_416 = 1
INPUT_BYTES = 519168
WEIGHT_BYTES = 5903100
EXPECTED_MODEL_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
EXPECTED_XSA_SHA256 = "ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6"
EXPECTED_BASE_APP_SHA256 = "9ed222a1d132d8cc836c362b4fbe453f833387bc66173dd5eb7d5388447e9a39"
REQUIRED_GATE_RECORDS = (
    "operator_authorization",
    "hardware_session_handoff",
    "exclusive_session",
    "g0_approval",
    "command_delivery_review",
    "timing_freeze",
    "range_reservation",
    "cold_basis",
)


class AdapterError(RuntimeError):
    """表示离线来源绑定、门禁或诊断流程失败。"""


@dataclass(frozen=True)
class PreparedRun:
    """表示已重新核验的离线准备记录。"""

    path: Path
    data: dict[str, Any]


@dataclass(frozen=True)
class GateCheck:
    """保存正式硬件门禁的只读核验结果。"""

    allowed: bool
    missing: tuple[str, ...]
    records: dict[str, dict[str, Any]]
    bindings: dict[str, dict[str, str]]


def require(condition: bool, message: str) -> None:
    """以显式异常拒绝歧义输入，不依赖 assert 优化设置。"""
    if not condition:
        raise AdapterError(message)


def sha256_bytes(raw: bytes) -> str:
    """计算原始字节的 SHA-256。"""
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    """分块计算文件原始字节 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_identity_sha256(identity: Mapping[str, Any]) -> str:
    """以稳定UTF-8 JSON编码计算整组硬件产物身份摘要。"""
    require(type(identity) is dict and identity, "artifact identity必须是非空JSON对象")
    encoded = json.dumps(identity, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    return sha256_bytes(encoded)


def exact_path(raw: str | os.PathLike[str], *, directory: bool = False) -> Path:
    """逐分量检查精确路径并拒绝符号链接、junction 和大小写别名。"""
    original = os.fspath(raw)
    require(type(original) is str and original != "", "路径必须是非空字符串")
    require(not any(char in original for char in "*?[]"), f"路径不能含通配符：{original}")
    require(not original.startswith(("\\\\?\\", "\\\\.\\", "\\??\\")),
            f"拒绝Windows设备或NT别名路径：{original}")
    if os.name == "nt":
        require(re.match(r"^[A-Za-z]:[\\/]", original) is not None,
                f"需要盘符绝对路径：{original}")
        tail = original[3:]
        components = re.split(r"[\\/]", tail)
        require(all(component != "" for component in components),
                f"路径包含重复或末尾分隔符：{original}")
        require(all(component not in {".", ".."} for component in components),
                f"路径包含别名分量：{original}")
        require(all(not component.endswith((".", " ")) for component in components),
                f"路径包含Windows尾点或尾空格别名：{original}")
        require(all(":" not in component for component in components),
                f"路径包含盘符以外的冒号别名：{original}")
    else:
        require(not re.search(r"/{2,}", original), f"路径包含重复分隔符：{original}")
        components = original.split("/")
        require(all(component not in {".", ".."} for component in components),
                f"路径包含别名分量：{original}")
    path = Path(original)
    require(path.is_absolute(), f"需要绝对路径：{original}")
    current = Path(path.anchor)
    for part in path.parts[1:]:
        try:
            entries = [item for item in current.iterdir() if item.name == part]
        except OSError as error:
            raise AdapterError(f"无法枚举精确路径父目录 {current}: {error}") from error
        require(len(entries) == 1, f"路径不存在或大小写不精确：{current / part}")
        current = entries[0]
        metadata = current.stat(follow_symlinks=False)
        windows_attributes = getattr(metadata, "st_file_attributes", 0)
        require(not current.is_symlink() and not (windows_attributes & 0x400),
                f"拒绝符号链接或重解析点：{current}")
    require(current.is_dir() if directory else current.is_file(),
            f"目标类型错误：{current}")
    return current


def safe_relative_path(value: str) -> PurePosixPath:
    """解析清单中的 POSIX 相对路径并拒绝路径别名。"""
    require(type(value) is str and value != "", "相对路径必须为非空字符串")
    require("\\" not in value and not value.startswith("/"), f"清单路径必须为 POSIX 相对路径：{value!r}")
    path = PurePosixPath(value)
    require(not path.is_absolute() and value == path.as_posix(), f"拒绝清单路径别名：{value!r}")
    require(all(part not in {"", ".", ".."} for part in path.parts), f"拒绝清单路径别名：{value!r}")
    return path


def _relative_target(root: Path, relative: str, *, directory: bool = False) -> Path:
    """将受限 POSIX 相对路径精确落到已核验根目录下。"""
    parts = safe_relative_path(relative).parts
    candidate = root.joinpath(*parts)
    actual = exact_path(candidate, directory=directory)
    require(actual.parent == candidate.parent, f"路径解析改变了父目录：{relative}")
    return actual


def _json_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """解析器发现重复键时立即拒绝。"""
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, f"JSON含重复键：{key}")
        result[key] = value
    return result


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    """严格按 UTF-8 读取 JSON 并拒绝重复键或非对象顶层。"""
    actual = exact_path(path)
    raw = actual.read_bytes()
    try:
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=_json_no_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AdapterError(f"JSON读取失败：{actual}: {error}") from error
    require(type(data) is dict, f"JSON顶层必须为对象：{actual}")
    return data, raw


def _write_json_new(path: Path, value: Mapping[str, Any]) -> None:
    """以 UTF-8/LF 新建机器记录并立即刷盘，禁止覆盖。"""
    require(not path.exists(), f"拒绝覆盖已存在文件：{path}")
    encoded = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())


def _write_bytes_new(path: Path, raw: bytes) -> None:
    """以独占新建方式保存原始证据并立即刷盘。"""
    require(type(raw) is bytes, "原始证据必须是bytes")
    require(not path.exists(), f"拒绝覆盖已存在文件：{path}")
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def _validate_run_id(value: str) -> str:
    """限制 RunId 字符集并拒绝大小写折叠冲突。"""
    require(type(value) is str and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,95}", value) is not None,
            f"RunId格式错误：{value!r}")
    return value


def _manifest_entries(manifest: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """索引交付清单文件行并拒绝路径重复。"""
    rows = manifest.get("files")
    require(type(rows) is list, "交付清单缺少files数组")
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        require(type(row) is dict and type(row.get("path")) is str, "交付清单文件行格式错误")
        safe_relative_path(row["path"])
        require(row["path"] not in result, f"交付清单重复路径：{row['path']}")
        require(re.fullmatch(r"[0-9a-f]{64}", str(row.get("sha256", ""))) is not None,
                f"交付清单SHA格式错误：{row['path']}")
        result[row["path"]] = row
    return result


def _bound_manifest_file(root: Path, entries: Mapping[str, Mapping[str, Any]], relative: str,
                         allowed_roles: Sequence[str], *, required: bool = True) -> dict[str, Any] | None:
    """以精确路径、角色和实测哈希绑定一个交付清单文件。"""
    safe_relative_path(relative)
    row = entries.get(relative)
    if row is None:
        if required:
            raise AdapterError(f"交付清单缺少必需文件：{relative}")
        return None
    require(row.get("role") in set(allowed_roles),
            f"交付清单文件角色错误：{relative} role={row.get('role')!r}")
    path = _relative_target(root, relative)
    actual_sha = sha256_file(path)
    require(actual_sha == row["sha256"], f"交付清单文件SHA不匹配：{relative}")
    return {"path": str(path), "relative_path": relative, "sha256": actual_sha,
            "bytes": path.stat().st_size, "role": row["role"]}


def _inventory_rows(inventory: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """核对外部输入清单的前后构建快照完全一致。"""
    current = inventory.get("external_inputs")
    before = inventory.get("external_inputs_before_build")
    after = inventory.get("external_inputs_after_build")
    require(type(current) is list and type(before) is list and type(after) is list,
            "外部输入清单缺少构建前后快照")

    def index(rows: list[Any], label: str) -> dict[str, dict[str, Any]]:
        output: dict[str, dict[str, Any]] = {}
        for row in rows:
            require(type(row) is dict and type(row.get("label")) is str, f"{label}行格式错误")
            require(row["label"] not in output, f"{label}标签重复：{row['label']}")
            output[row["label"]] = row
        return output

    current_by = index(current, "external_inputs")
    before_by = index(before, "external_inputs_before_build")
    after_by = index(after, "external_inputs_after_build")
    require(set(current_by) == set(before_by) == set(after_by), "外部输入清单的标签集合变化")
    for label, row in current_by.items():
        identity = (row.get("path"), row.get("bytes"), row.get("sha256"), row.get("expected_sha256"), row.get("status"))
        require(identity == tuple(before_by[label].get(key) for key in ("path", "bytes", "sha256", "expected_sha256", "status")),
                f"外部输入构建前快照不同：{label}")
        require(identity == tuple(after_by[label].get(key) for key in ("path", "bytes", "sha256", "expected_sha256", "status")),
                f"外部输入构建后快照不同：{label}")
        digest = row.get("sha256")
        expected = row.get("expected_sha256")
        require(row.get("exists") is True and row.get("status") == "PASS" and
                type(row.get("bytes")) is int and
                type(digest) is str and re.fullmatch(r"[0-9a-f]{64}", digest) is not None and
                (expected is None or expected == digest),
                f"外部输入未通过构建清单或缺少实测SHA：{label}")
    return current_by


def _inventory_binding(row: Mapping[str, Any], label: str) -> dict[str, Any]:
    """按清单中完整原路径复算单个外部输入。"""
    require(row.get("label") == label and type(row.get("path")) is str, f"外部输入标签或路径错误：{label}")
    path = exact_path(row["path"])
    require(path.stat().st_size == row["bytes"], f"外部输入长度变化：{label}")
    digest = sha256_file(path)
    expected = row.get("expected_sha256")
    require(digest == row["sha256"] and
            (expected is None or digest == expected), f"外部输入SHA变化：{label}")
    return {"path": str(path), "sha256": digest, "bytes": path.stat().st_size, "role": "external_input", "label": label}


def _git_output(args: Sequence[str], *, cwd: Path | None = None) -> bytes:
    """以参数数组调用只读Git命令，不经过命令解释器。"""
    try:
        result = subprocess.run(["git", *args], cwd=cwd, check=False, capture_output=True)
    except OSError as error:
        raise AdapterError(f"Git只读查询无法启动：{error}") from error
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise AdapterError(f"Git只读查询失败 exit={result.returncode}: {detail}")
    return result.stdout


def _resolve_historical_source_commit(root: Path, source_commit: Any) -> tuple[str, str]:
    """核对编译清单记录的历史基线可解析，并单独记录prepare时HEAD。"""
    require(type(source_commit) is str and re.fullmatch(r"[0-9a-f]{40}", source_commit) is not None,
            "构建清单历史源码基线格式错误")
    resolved = _git_output(["-C", str(root), "rev-parse", "--verify",
                            source_commit + "^{commit}"]).decode("ascii").strip()
    require(resolved == source_commit, "构建清单历史源码提交在当前仓库不可解析")
    current_head = _git_output(["-C", str(root), "rev-parse", "HEAD"]).decode("ascii").strip()
    return source_commit, current_head


def _expected_derived_patch(base_bytes: bytes, derived_bytes: bytes) -> bytes:
    """重建builder保存的唯一app派生diff以核对输入与输出原文。"""
    base_text = base_bytes.decode("utf-8").replace("\r\n", "\n")
    derived_text = derived_bytes.decode("utf-8").replace("\r\n", "\n")
    diff = difflib.unified_diff(
        base_text.splitlines(keepends=True), derived_text.splitlines(keepends=True),
        fromfile="frozen-2b-app.c", tofile="derived-s4b-ps-tensor-app.c",
    )
    return "".join(diff).encode("utf-8")


def _derive_from_current_builder(root: Path, base_source: bytes) -> tuple[bytes, str]:
    """用已绑定的本树builder重新生成派生app原字节。"""
    builder_path = exact_path(root / "scripts" / "stage4_s4b" / "build_s4b_ps_tensor.py")
    module_name = "_s4b_ps_tensor_adapter_bound_builder"
    require(module_name not in sys.modules, "派生源码重建builder模块名已被占用")
    spec = importlib.util.spec_from_file_location(module_name, builder_path)
    require(spec is not None and spec.loader is not None, "无法加载已绑定的S4-B builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
        derived, digest = module.derive_source(base_source)
    finally:
        sys.modules.pop(module_name, None)
    return derived, digest


def _frozen_tool_blobs(repo: Path) -> dict[str, bytes]:
    """从固定提交取回完整工具闭包并在任何import前逐项核验。"""
    repo = exact_path(repo, directory=True)
    root_text = _git_output(["-C", str(repo), "rev-parse", "--show-toplevel"]).decode("utf-8").strip()
    root = exact_path(root_text, directory=True)
    require(root == repo, f"冻结工具仓库根路径变化：{root} != {repo}")
    commit_text = _git_output(["-C", str(root), "rev-parse", "--verify", FROZEN_2B_COMMIT + "^{commit}"]).decode("ascii").strip()
    require(commit_text == FROZEN_2B_COMMIT, "冻结2B工具提交对象身份不符")
    blobs: dict[str, bytes] = {}
    for relative, expected in FROZEN_TOOL_SHA256.items():
        safe_relative_path(relative)
        raw = _git_output(["-C", str(root), "cat-file", "blob", f"{FROZEN_2B_COMMIT}:{relative}"])
        actual = sha256_bytes(raw)
        require(actual == expected, f"冻结工具Git blob SHA错误：{relative}")
        blobs[relative] = raw
    return blobs


def _frozen_2b_git_root_from_manifest(path: Path | str) -> Path:
    """从固定2B冻结delivery manifest精确反推出Git根并验证repo身份。"""
    manifest_path = exact_path(path)
    require(manifest_path.name == "delivery_manifest.json" and
            manifest_path.parents[0].name == "stage2b_freeze_20261022_r02" and
            manifest_path.parents[1].name == "S2B-T18",
            "冻结2B delivery manifest路径层级不符合实际证据位置")
    root = exact_path(manifest_path.parents[4], directory=True)
    git_root = _git_output(["-C", str(root), "rev-parse", "--show-toplevel"]).decode("utf-8").strip()
    require(exact_path(git_root, directory=True) == root,
            f"冻结2B manifest推导路径不是仓库Git根：{root}")
    return root


def _verify_bundle_members(zip_path: Path, bundle_manifest_path: Path,
                           extracted_root: Path,
                           expected_overlays: Mapping[str, bytes],
                           derived_source_sha256: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """逐项核验恢复清单、ZIP原成员和builder解包后的实际输入。"""
    manifest, manifest_raw = read_json(bundle_manifest_path)
    require(manifest.get("source_commit") == "03faa2d47a6e49d7475e387cf6b33edda4962c68",
            "恢复包成员清单来源提交不符")
    require(manifest.get("xsa_sha256") == EXPECTED_XSA_SHA256, "恢复包成员清单XSA身份不符")
    members = manifest.get("files")
    require(type(members) is list and members, "恢复包成员清单files为空或格式错误")
    member_names: set[str] = set()
    expected_overlay_names = set(expected_overlays)
    allowed_overlay_names = {
        "bundle/workspace/infer/src/s2b_inference_app.c",
        "bundle/workspace/infer/src/s4b_ps_trace.c",
        "bundle/workspace/infer/src/s4b_ps_trace.h",
        "bundle/workspace/infer/src/s4b_ps_build_config.h",
    }
    require(expected_overlay_names == allowed_overlay_names,
            "builder overlay集合与冻结S4-B派生契约不同")
    bindings: list[dict[str, Any]] = []
    try:
        archive = zipfile.ZipFile(zip_path, "r")
    except (OSError, zipfile.BadZipFile) as error:
        raise AdapterError(f"恢复ZIP无法读取：{error}") from error
    with archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        require(len(names) == len(set(names)), "恢复ZIP含重复成员名称")
        folded_names = [name.casefold() for name in names]
        require(len(folded_names) == len(set(folded_names)), "恢复ZIP含大小写折叠别名成员")
        require(all(not item.is_dir() for item in infos), "恢复ZIP含未授权目录项")
        info_by_name = {item.filename: item for item in infos}
        require(RECOVERY_INIT_MEMBER in info_by_name, "恢复ZIP缺少绑定的init ELF成员")
        internal_manifest_name = "bundle/workspace/manifest.json"
        internal_manifest_info = info_by_name.get(internal_manifest_name)
        require(internal_manifest_info is not None, "恢复ZIP缺少唯一内部bundle manifest")
        internal_manifest_raw = archive.read(internal_manifest_info)
        require(internal_manifest_raw == manifest_raw,
                "恢复ZIP内部manifest原字节与经交付清单绑定的sidecar不同")
        for row in members:
            require(type(row) is dict and type(row.get("path")) is str and type(row.get("bytes")) is int,
                    "恢复包成员行格式错误")
            name = row["path"]
            safe_relative_path(name)
            require(name not in member_names, f"恢复包成员清单重复路径：{name}")
            member_names.add(name)
            expected = row.get("sha256")
            require(type(expected) is str and re.fullmatch(r"[0-9a-f]{64}", expected) is not None,
                    f"恢复包成员SHA格式错误：{name}")
            info = info_by_name.get(name)
            require(info is not None and info.file_size == row["bytes"], f"ZIP成员缺失或长度不符：{name}")
            mode = info.external_attr >> 16
            require(not mode or (mode & 0o170000) in (0, 0o100000), f"恢复ZIP成员不是普通文件：{name}")
            raw = archive.read(info)
            require(len(raw) == row["bytes"] and sha256_bytes(raw) == expected,
                    f"恢复ZIP成员原字节不符：{name}")
            extracted = _relative_target(extracted_root, name)
            if name == "bundle/workspace/infer/src/s2b_inference_platform.h":
                platform_text = raw.decode("utf-8")
                pattern = re.compile(r'(?m)(#define S2B_C_SOURCE_SHA256 ")[0-9a-f]{64}("\s*)')
                platform_bytes, replacements = pattern.subn(
                    lambda match: match.group(1) + derived_source_sha256 + match.group(2), platform_text)
                require(replacements == 1, "冻结platform header中的SOURCE锚点必须唯一")
                expected_extracted = platform_bytes.encode("utf-8")
            else:
                expected_extracted = expected_overlays.get(name, raw)
            actual_extracted = extracted.read_bytes()
            require(actual_extracted == expected_extracted,
                    f"builder解包或overlay后的实际输入不符：{name}")
            bindings.append({"path": str(extracted), "relative_path": name,
                             "sha256": sha256_bytes(expected_extracted),
                             "bytes": len(expected_extracted),
                             "role": "compiled_extracted_overlay" if name in expected_overlay_names or
                             name == "bundle/workspace/infer/src/s2b_inference_platform.h" else
                             "verified_recovery_bundle_member"})
        _verify_bundle_member_pathset(member_names)
        expected_archive_names = member_names | {internal_manifest_name}
        require(set(names) == expected_archive_names,
                f"恢复ZIP实际文件集合不精确：extra={sorted(set(names)-expected_archive_names)} "
                f"missing={sorted(expected_archive_names-set(names))}")
        require(len(names) == RECOVERY_BUNDLE_MEMBER_COUNT + 1,
                "恢复ZIP实际文件数必须是85个payload加唯一内部manifest")
        missing_overlays = expected_overlay_names - member_names
        for name in sorted(missing_overlays):
            safe_relative_path(name)
            extracted = _relative_target(extracted_root, name)
            expected_raw = expected_overlays[name]
            actual_raw = extracted.read_bytes()
            require(actual_raw == expected_raw, f"builder新增编译overlay字节不符：{name}")
            bindings.append({"path": str(extracted), "relative_path": name,
                             "sha256": sha256_bytes(expected_raw), "bytes": len(expected_raw),
                             "role": "compiled_extracted_overlay"})
        actual_files: set[str] = set()
        for candidate in extracted_root.rglob("*"):
            if candidate.is_dir():
                exact_path(candidate, directory=True)
            elif candidate.is_file():
                actual = exact_path(candidate)
                actual_files.add(actual.relative_to(extracted_root).as_posix())
            else:
                raise AdapterError(f"bundle_extract含非普通文件或目录：{candidate}")
        expected_files = member_names | expected_overlay_names
        require(actual_files == expected_files,
                f"bundle_extract有未绑定或缺失的额外文件：extra={sorted(actual_files-expected_files)} missing={sorted(expected_files-actual_files)}")
    init = next((row for row in bindings if row["relative_path"] == RECOVERY_INIT_MEMBER), None)
    require(init is not None, "恢复包清单没有绑定init ELF")
    return {"sha256": sha256_bytes(manifest_raw), "source_commit": manifest["source_commit"],
            "xsa_sha256": manifest["xsa_sha256"], "init_elf": init}, bindings


def _verify_bundle_member_pathset(names: set[str]) -> None:
    """仅接受冻结恢复ZIP的精确成员路径集合，拒绝未审源码、头文件或库。"""
    require(type(names) is set and all(type(name) is str for name in names),
            "恢复ZIP成员路径集合格式错误")
    actual_hash = sha256_bytes("\n".join(sorted(names)).encode("utf-8"))
    require(len(names) == RECOVERY_BUNDLE_MEMBER_COUNT and
            actual_hash == RECOVERY_BUNDLE_MEMBER_PATHSET_SHA256,
            f"恢复ZIP成员集合含未知或缺失源码/库：count={len(names)} pathset_sha256={actual_hash}")


def _decode_banner_text(value: Any) -> bytes:
    """把来源JSON中明确保存的反斜线r/n尾标记转为真实CRLF。"""
    require(type(value) is str and value.endswith(r"\r\n"),
            "派生READY banner没有精确的C转义CRLF尾标记")
    text = value[:-4] + "\r\n"
    require(text.isascii() and text.endswith("\r\n"), "READY banner必须是ASCII且以CRLF结尾")
    return text.encode("ascii")


def build_expected_ready_banner(derived: Mapping[str, Any], xsa_sha256: str,
                                model_sha256: str) -> bytes:
    """逐项核对完整S4-B READY身份并生成实际ASCII/CRLF期望字节。"""
    source = derived.get("derived_s4b_ps_app_sha256")
    require(type(source) is str and re.fullmatch(r"[0-9a-f]{64}", source) is not None,
            "派生app源码SHA格式错误")
    require(type(xsa_sha256) is str and re.fullmatch(r"[0-9a-f]{64}", xsa_sha256) is not None,
            "XSA SHA格式错误")
    require(type(model_sha256) is str and re.fullmatch(r"[0-9a-f]{64}", model_sha256) is not None,
            "模型SHA格式错误")
    expected = (f"S2B-INFERENCE/1 READY SOURCE={source} XSA={xsa_sha256} MODEL={model_sha256} "
                "DIAG=s4b-ps-tensor/1 TRACE_ABI=1\r\n").encode("ascii")
    recorded = _decode_banner_text(derived.get("embedded_ready_banner"))
    require(recorded == expected, "来源记录的READY banner与app/XSA/model/DIAG/TRACE身份不一致")
    return expected


def _validate_trace_header(raw: bytes, expected_source_sha256: str,
                           expected_boot_seed: int, expected_session_first: int | None = None,
                           expected_session_last: int | None = None) -> tuple[int, ...]:
    """核对完整日志头CRC、身份、布局、run_active及session配置。"""
    require(type(raw) is bytes and len(raw) == TRACE_HEADER_BYTES, "trace header必须恰好144字节")
    require(type(expected_source_sha256) is str and re.fullmatch(r"[0-9a-f]{64}", expected_source_sha256) is not None,
            "期望派生源码SHA必须是小写64位")
    require(type(expected_boot_seed) is int and 0 < expected_boot_seed <= 0xFFFFFFFFFFFFFFFF,
            "期望boot seed必须是非零u64")
    words = TRACE_HEADER_STRUCT.unpack(raw)
    require(words[0] == TRACE_MAGIC and words[1] == TRACE_SCHEMA_VERSION and words[2] == TRACE_HEADER_BYTES,
            "trace header magic/schema/size不匹配")
    require(words[3] == TRACE_RECORD_BYTES and words[4] == TRACE_CAPACITY and words[5] <= TRACE_CAPACITY,
            "trace记录布局或计数不匹配")
    require(words[TRACE_RUN_ACTIVE_WORD] == 0, "trace日志仍有活动RUN，不允许快照")
    require(words[25] == 1 and words[26] == 1, "trace诊断种类或PS时基类型不匹配")
    require(words[35] == (zlib_crc32(raw[:140])), "trace header CRC错误")
    actual_seed = (words[7] << 32) | words[6]
    require(actual_seed == expected_boot_seed, "trace boot seed与本轮run_config不匹配")
    actual_source = "".join(f"{word:08x}" for word in words[27:35])
    require(actual_source == expected_source_sha256, "trace派生源码SHA与本轮清单不匹配")
    if expected_session_first is not None:
        require(words[8] == expected_session_first, "trace session_first与预留范围不匹配")
    if expected_session_last is not None:
        require(words[9] == expected_session_last, "trace session_last与预留范围不匹配")
    return words


def zlib_crc32(raw: bytes) -> int:
    """返回无符号IEEE CRC-32，与冻结trace decoder一致。"""
    import zlib
    return zlib.crc32(raw) & 0xFFFFFFFF


def pack_double_snapshot(first_header: bytes, first_records: bytes,
                         second_header: bytes, second_records: bytes, *,
                         expected_source_sha256: str, expected_boot_seed: int,
                         expected_session_first: int | None = None,
                         expected_session_last: int | None = None) -> bytes:
    """仅将两次逐字节稳定的完整双区读回封装为冻结dump格式。"""
    for label, value, expected in (
        ("first header", first_header, TRACE_HEADER_BYTES),
        ("first records", first_records, TRACE_RECORDS_BYTES),
        ("second header", second_header, TRACE_HEADER_BYTES),
        ("second records", second_records, TRACE_RECORDS_BYTES),
    ):
        require(type(value) is bytes and len(value) == expected,
                f"{label}长度错误：期望{expected}，实际{len(value) if isinstance(value, bytes) else '非bytes'}")
    require(first_header == second_header and first_records == second_records,
            "两次完整trace区域读取不一致，拒绝打包")
    _validate_trace_header(first_header, expected_source_sha256, expected_boot_seed,
                           expected_session_first, expected_session_last)
    snapshot = first_header + first_records
    prefix = DUMP_HEADER.pack(b"S4BPSDMP", 1, TRACE_HEADER_BYTES, TRACE_RECORD_BYTES,
                              TRACE_CAPACITY, TRACE_SNAPSHOT_BYTES)
    return prefix + snapshot + snapshot


def _validate_empty_trace_header(raw: bytes, identity: Mapping[str, Any]) -> tuple[int, ...]:
    """确认本次部署后的trace已初始化且尚无旧RUN/记录。"""
    words = _validate_trace_header(raw, identity["derived_source_sha256"],
                                   identity["boot_seed"], identity["session_first"],
                                   identity["session_last"])
    require(words[5] == 0 and words[10] == identity["session_first"] and
            words[11] == 0 and words[12] == 0 and words[13] == 0 and
            words[17] == 0 and words[18] == 0 and words[19] == 0 and
            words[20] == 0 and words[21] == 0 and words[22] == 0 and
            words[23] == 0 and words[24] == 0,
            "新部署trace不是空初态；拒绝把旧记录归入本次UART运行")
    return words


def _validate_completed_run_header(raw: bytes, identity: Mapping[str, Any], *,
                                   uart_sequence: int, frame_id: int,
                                   repeat: int) -> tuple[int, ...]:
    """核对本次唯一RUN的完整header身份与成功完成状态。"""
    words = _validate_trace_header(raw, identity["derived_source_sha256"],
                                   identity["boot_seed"], identity["session_first"],
                                   identity["session_last"])
    require(words[5] == repeat and words[11] == 0 and words[12] == 0 and words[13] == 0 and
            words[18] == 1 and words[19] == identity["session_first"] and
            words[20] == uart_sequence and words[21] == frame_id and
            words[22] == repeat and words[23] == repeat and
            words[24] == identity["session_first"],
            "trace header不是本次完整成功RUN：record/session/sequence/frame/repeat/status不匹配")
    return words


def _wait_for_safe_idle(controller: Any, identity: Mapping[str, Any], *,
                        uart_sequence: int, frame_id: int, repeat: int,
                        expected_epoch: int,
                        header_address: int, timeout_seconds: float = 5.0,
                        poll_interval_seconds: float = 0.05) -> tuple[dict[int, int], bytes]:
    """在有限时限内等待ACK后的稳定IDLE_PS与end_run成功记录。"""
    require(type(timeout_seconds) in (int, float) and timeout_seconds > 0 and
            type(poll_interval_seconds) in (int, float) and poll_interval_seconds > 0,
            "IDLE/trace完成观察时限无效")
    deadline = time.monotonic() + float(timeout_seconds)
    previous: tuple[tuple[tuple[int, int], ...], bytes] | None = None
    last_reason = "尚未观察到稳定IDLE_PS"
    while time.monotonic() < deadline:
        try:
            csr = controller.stable_csr("after_RUN_ACK_wait_for_IDLE")
            header_first = words_le(controller.words(header_address, TRACE_HEADER_BYTES // 4))
            header_second = words_le(controller.words(header_address, TRACE_HEADER_BYTES // 4))
            if header_first != header_second:
                last_reason = "trace header仍在变化"
                previous = None
            else:
                words = _validate_completed_run_header(
                    header_first, identity, uart_sequence=uart_sequence,
                    frame_id=frame_id, repeat=repeat)
                status = csr.get(0x00C)
                current_epoch = ((csr.get(0x054, 0) & 0xFFFFFFFF) << 32) | (csr.get(0x050, 0) & 0xFFFFFFFF)
                acknowledged_epoch = ((csr.get(0x060, 0) & 0xFFFFFFFF) << 32) | (csr.get(0x05C, 0) & 0xFFFFFFFF)
                unsafe = TRACE_CSR_OWNER_PL | TRACE_CSR_AXI_PENDING | TRACE_CSR_FIRST_PENDING
                require(type(status) is int, "CSR状态寄存器缺失")
                require((status & TRACE_CSR_STATE_MASK) == 0 and
                        status & TRACE_CSR_SAFE_REUSE and not status & TRACE_CSR_TERMINAL and
                        not status & unsafe and csr.get(0x010) == 0 and
                        current_epoch == acknowledged_epoch == expected_epoch and
                        csr.get(0x058) == frame_id,
                        "RUN ACK后尚未回到IDLE_PS/terminal0，或owner/pending/epoch/frame不安全")
                snapshot = (tuple(sorted((int(address), int(value)) for address, value in csr.items())),
                            header_first)
                if snapshot == previous:
                    return csr, header_first
                previous = snapshot
                last_reason = "等待连续两次相同的安全CSR/header"
        except AdapterError as error:
            last_reason = str(error)
            previous = None
        time.sleep(min(float(poll_interval_seconds), max(0.0, deadline - time.monotonic())))
    raise AdapterError(f"有限IDLE/trace完成观察期限到期：{last_reason}；不ACK/reset/释放/重试")


def _validate_trace_uart_join(header_raw: bytes, records_raw: bytes,
                              receipts: Sequence[Mapping[str, Any]], *,
                              identity: Mapping[str, Any], uart_sequence: int,
                              frame_id: int, repeat: int, input_crc32: int) -> dict[str, Any]:
    """按session/frame/result_seq/repeat/sequence逐项连接完整trace与UART原始回执。"""
    words = _validate_completed_run_header(header_raw, identity,
                                           uart_sequence=uart_sequence,
                                           frame_id=frame_id, repeat=repeat)
    require(type(records_raw) is bytes and len(records_raw) == TRACE_RECORDS_BYTES,
            "trace records必须是完整46000-word快照")
    require(type(receipts) in (list, tuple) and len(receipts) == repeat,
            "当前RUN的UART回执数不等于repeat；拒绝空/部分/多余记录")
    record_struct = struct.Struct("<46I")
    matched: list[dict[str, int]] = []
    for index, receipt in enumerate(receipts):
        require(type(receipt) is dict and type(receipt.get("meta")) is dict,
                f"UART回执{index}缺少冻结transport解析字段")
        meta = receipt["meta"]
        record_raw = records_raw[index * TRACE_RECORD_BYTES:(index + 1) * TRACE_RECORD_BYTES]
        record = record_struct.unpack(record_raw)
        require(record[0] == 0x53345243 and record[1] == 1 and record[2] == TRACE_RECORD_BYTES and
                record[3] == index and record[45] == zlib_crc32(record_raw[:180]),
                f"trace记录{index} magic/schema/index/CRC无效")
        expected_frame = frame_id + index
        expected_fields = {
            4: identity["session_first"], 5: expected_frame, 6: index + 1,
            7: index, 8: uart_sequence, 9: input_crc32, 10: INPUT_BYTES,
            11: TRACE_INPUT_FORMAT_INT8_CHW_416, 33: expected_frame,
            34: meta.get("phys_status"), 35: meta.get("error_code"),
            36: meta.get("last_reject"), 39: meta.get("box_count"),
            40: meta.get("raw_candidate_count"), 41: meta.get("response_code"),
        }
        for word_index, expected in expected_fields.items():
            require(type(expected) is int and record[word_index] == expected,
                    f"trace记录{index} word{word_index}与同键UART回执不匹配")
        require(receipt.get("index") == index and receipt.get("frame") == expected_frame and
                receipt.get("sequence") == uart_sequence and receipt.get("epoch") == meta.get("epoch") and
                meta.get("index") == index and meta.get("total") == repeat and
                meta.get("response_code") == TRACE_RESPONSE_OK and
                meta.get("error_code") == 0 and meta.get("last_reject") == 0 and
                receipt.get("input_crc32") == input_crc32 and
                receipt.get("input_bytes") == INPUT_BYTES and
                receipt.get("input_format") == "INT8_CHW_416",
                f"trace记录{index}缺少精确session/frame/result_seq/repeat/UART序号/epoch/输入schema关联")
        record_epoch = (record[32] << 32) | record[31]
        require(record_epoch == meta.get("epoch") and
                record[38] == 0 and record[42] == TRACE_UART_SEND_SUCCEEDED and
                record[43] == TRACE_ACK_SUCCEEDED and record[12] == 0 and
                record[13] == 0 and record[14] == 3,
                f"trace记录{index}的epoch/decode/UART/ACK/采集schema与回执不符")
        matched.append({"record_index": index, "session_id": record[4],
                        "frame_id": record[5], "result_seq": record[6],
                        "repeat_index": record[7], "uart_sequence": record[8],
                        "epoch": record_epoch, "terminal_status": record[34],
                        "input_crc32": record[9]})
    for offset in range(repeat * TRACE_RECORD_BYTES, TRACE_RECORDS_BYTES):
        require(records_raw[offset] == 0, "trace未使用记录槽含非零旧/额外数据")
    return {"status": "PASS_EXACT_TRACE_UART_JOIN", "record_count": repeat,
            "input_crc32": input_crc32, "matches": matched}


def prepare_adapter(project_root: Path, source_run_id: str, run_id: str) -> Path:
    """离线绑定所选实际编译产物并创建新的adapter准备证据目录。"""
    root = exact_path(project_root, directory=True)
    source_run_id = _validate_run_id(source_run_id)
    run_id = _validate_run_id(run_id)
    evidence_dir = _relative_target(root, f"report/evidence/S4-B/{source_run_id}", directory=True)
    build_manifest_path = _relative_target(evidence_dir, "delivery_manifest.json")
    prep_parent = exact_path(root / "tmp" / "4", directory=True)
    task_dir = prep_parent / "S4-B-REAL-02B"
    if not task_dir.exists():
        task_dir.mkdir()
    else:
        exact_path(task_dir, directory=True)
    collisions = [entry.name for entry in task_dir.iterdir() if entry.name.casefold() == run_id.casefold()]
    require(not collisions, f"拒绝覆盖或大小写折叠RunId：{run_id}")
    output_dir = task_dir / run_id
    output_dir.mkdir()
    exact_path(output_dir, directory=True)

    try:
        record = _collect_preparation(root, source_run_id, evidence_dir, build_manifest_path, output_dir, run_id)
        _write_json_new(output_dir / "adapter_preparation.json", record)
        return output_dir / "adapter_preparation.json"
    except BaseException as error:
        failure = {
            "schema_version": 1,
            "status": "FAIL_OFFLINE_PREPARATION",
            "task_id": "S4-B-REAL-02B",
            "run_id": run_id,
            "source_build_run_id": source_run_id,
            "error_type": type(error).__name__,
            "error": str(error),
            "traceback": traceback.format_exc(),
            "hardware_execution": "NOT_RUN",
        }
        _write_json_new(output_dir / "adapter_prepare_error.json", failure)
        raise


def _collect_preparation(root: Path, source_run_id: str, evidence_dir: Path,
                         build_manifest_path: Path, output_dir: Path, run_id: str, *,
                         write_verified_init: bool = True) -> dict[str, Any]:
    """核对选定构建身份、派生app和实际编译输入。"""
    require(type(source_run_id) is str and BUILD_RUN_ID_PATTERN.fullmatch(source_run_id) is not None,
            "S4-B构建RunId格式错误")
    manifest, manifest_raw = read_json(build_manifest_path)
    require(manifest.get("schema_version") == 1 and manifest.get("stage") == "stage4" and
            manifest.get("task_id") == "S4-B" and manifest.get("run_id") == source_run_id,
            "选定S4-B构建清单身份不符")
    expected_evidence = f"report/evidence/S4-B/{source_run_id}"
    require(manifest.get("evidence_dir") == expected_evidence, "构建清单evidence_dir不是选定的精确RunId")
    source_commit, current_head = _resolve_historical_source_commit(root, manifest.get("source_commit"))
    entries = _manifest_entries(manifest)
    bindings: dict[str, dict[str, Any]] = {}

    def add_manifest(relative: str, roles: Sequence[str], required: bool = True) -> dict[str, Any] | None:
        result = _bound_manifest_file(root, entries, relative, roles, required=required)
        if result is not None:
            bindings[result["path"]] = result
        return result

    delivery_binding = {
        "path": str(build_manifest_path), "sha256": sha256_bytes(manifest_raw),
        "bytes": len(manifest_raw), "role": "selected_build_manifest",
    }
    bindings[str(build_manifest_path)] = delivery_binding
    elf_rel = f"report/evidence/S4-B/{source_run_id}/s4b_ps_tensor_diagnostic.elf"
    map_rel = f"report/evidence/S4-B/{source_run_id}/s4b_ps_tensor_diagnostic.map"
    elf = add_manifest(elf_rel, ("artifact",))
    map_file = add_manifest(map_rel, ("artifact",))
    require(elf is not None and map_file is not None, "选定构建的ELF/map绑定缺失")

    selected_result_names = (
        "derived_source_sha256.json", "derived_source.patch", "run_config.json", "memory_ranges.json", "external_inputs_inventory.json",
        "machine_result.json", "commands.json",
    )
    selected: dict[str, dict[str, Any]] = {}
    for filename in selected_result_names:
        relative = f"report/evidence/S4-B/{source_run_id}/{filename}"
        selected[filename] = add_manifest(relative, ("result", "input", "log", "artifact"))  # type: ignore[assignment]
        require(selected[filename] is not None, f"构建清单缺少选择输入：{filename}")

    derived_path = Path(selected["derived_source_sha256.json"]["path"])
    derived, derived_raw = read_json(derived_path)
    source_sha = derived.get("derived_s4b_ps_app_sha256")
    require(type(source_sha) is str and re.fullmatch(r"[0-9a-f]{64}", source_sha) is not None,
            "派生app源码SHA格式错误")
    require(derived.get("frozen_2b_app_sha256") == EXPECTED_BASE_APP_SHA256,
            "派生身份没有记录builder所需的冻结app原始SHA")
    run_config_path = Path(selected["run_config.json"]["path"])
    run_config, _ = read_json(run_config_path)
    require(run_config.get("run_id") == source_run_id and
            run_config.get("hardware_reservation_status") == "BUILD_ONLY_NOT_RESERVED_FOR_HARDWARE",
            "运行配置身份或硬件预留状态不符")
    boot_seed = int(run_config["boot_seed"], 0)
    session_first = int(run_config["session_first"], 0)
    session_last = int(run_config["session_last"], 0)
    require(0 < boot_seed <= 0xFFFFFFFFFFFFFFFF and
            1 <= session_first <= session_last <= 0xFFFFFFFE, "seed/session范围无效")
    memory_path = Path(selected["memory_ranges.json"]["path"])
    memory, _ = read_json(memory_path)
    header_range = memory.get("trace_header", {})
    record_range = memory.get("trace_records", {})
    require(header_range == {"start": 7464512, "end_exclusive": 7464656, "size_bytes": TRACE_HEADER_BYTES} and
            record_range == {"start": 7280512, "end_exclusive": 7464512, "size_bytes": TRACE_RECORDS_BYTES,
                             "record_capacity": TRACE_CAPACITY, "record_bytes": TRACE_RECORD_BYTES},
            "trace地址/布局与核验值不符")

    # 只核验实际编译所需源文件；构建时保存的runbook行可能已被后续修订。
    compiled_source_relatives = (
        "scripts/stage4_s4b/build_s4b_ps_tensor.py",
        "vitis/stage4/ps/s4b_ps_trace.c",
        "vitis/stage4/ps/s4b_ps_trace.h",
    )
    compiled_sources: dict[str, dict[str, Any]] = {}
    for relative in compiled_source_relatives:
        row = add_manifest(relative, ("source",))
        require(row is not None, f"实际编译源码绑定缺失：{relative}")
        compiled_sources[relative] = row
    require(derived.get("trace_source_sha256") == compiled_sources["vitis/stage4/ps/s4b_ps_trace.c"]["sha256"] and
            derived.get("trace_header_sha256") == compiled_sources["vitis/stage4/ps/s4b_ps_trace.h"]["sha256"],
            "derived_source身份中的trace C/H SHA与实际编译源码清单不同")

    temp_build = exact_path(root / "tmp" / "4" / "S4-B-REAL-01" / source_run_id, directory=True)
    derived_app_path = exact_path(temp_build / "derived_app_source.c")
    require(sha256_file(derived_app_path) == source_sha,
            "builder临时目录中的实际派生C源SHA与派生身份不同")
    bindings[str(derived_app_path)] = {"path": str(derived_app_path), "sha256": source_sha,
                                       "bytes": derived_app_path.stat().st_size, "role": "compiled_app_source"}

    inventory_path = Path(selected["external_inputs_inventory.json"]["path"])
    inventory, inventory_raw = read_json(inventory_path)
    external_rows = _inventory_rows(inventory)
    required_external = {
        "2B恢复输入ZIP": "recovery_zip",
        "2B冻结交付清单": "frozen_2b_manifest",
        "冻结XSA引用": "xsa",
        "冻结模型manifest": "model_manifest",
    }
    external: dict[str, dict[str, Any]] = {}
    for label, name in required_external.items():
        external[name] = _inventory_binding(external_rows[label], label)
        bindings[external[name]["path"]] = external[name]

    frozen_manifest_path = Path(external["frozen_2b_manifest"]["path"])
    frozen_manifest, frozen_manifest_raw = read_json(frozen_manifest_path)
    frozen_files = _manifest_entries(frozen_manifest)
    w2b_root = _frozen_2b_git_root_from_manifest(frozen_manifest_path)
    frozen_commit = _git_output(["-C", str(w2b_root), "rev-parse", "--verify", FROZEN_2B_COMMIT + "^{commit}"]).decode("ascii").strip()
    require(frozen_commit == FROZEN_2B_COMMIT, "2B冻结工具commit不可解析")
    bindings[str(frozen_manifest_path)] = {"path": str(frozen_manifest_path),
                                           "sha256": external["frozen_2b_manifest"]["sha256"],
                                           "bytes": external["frozen_2b_manifest"]["bytes"],
                                           "role": "frozen_2b_manifest"}

    frozen_manifest_sha = external["frozen_2b_manifest"]["sha256"]
    require(sha256_bytes(frozen_manifest_raw) == frozen_manifest_sha, "2B冻结清单实际SHA不匹配")
    frozen_required = {
        "report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit": ("bit", "input"),
        "src/s2b_control_csr.sv": ("csr_source", "source"),
        "docs/obsidian-project/02-方案设计/s2b_board_transport.md": ("interface", "source"),
        "report/evidence/S2B-T15/recovery_inputs_20261019_r02/recovery_bundle.zip": ("recovery_zip", "input"),
    }
    selected_2b: dict[str, dict[str, Any]] = {}
    for relative, (key, expected_role) in frozen_required.items():
        row = _bound_manifest_file(w2b_root, frozen_files, relative, (expected_role,))
        require(row is not None, f"2B冻结manifest缺少{key}：{relative}")
        selected_2b[key] = row
        bindings[row["path"]] = row
    require(selected_2b["recovery_zip"]["path"] == external["recovery_zip"]["path"] and
            selected_2b["recovery_zip"]["sha256"] == external["recovery_zip"]["sha256"],
            "S4-B外部inventory路径/SHA与2B冻结artifact manifest不同")

    with zipfile.ZipFile(external["recovery_zip"]["path"], "r") as recovery_archive:
        base_app_raw = recovery_archive.read("bundle/workspace/infer/src/s2b_inference_app.c")
    require(sha256_bytes(base_app_raw) == EXPECTED_BASE_APP_SHA256,
            "恢复ZIP中的app原始字节SHA与冻结builder输入不符")
    derived_app_raw = derived_app_path.read_bytes()
    require(sha256_bytes(derived_app_raw) == source_sha,
            "builder目录中的派生app源码SHA与来源身份不同")
    regenerated_app, regenerated_sha = _derive_from_current_builder(root, base_app_raw)
    require(derived_app_raw == regenerated_app and source_sha == regenerated_sha,
            "实际编译app源码不是当前绑定builder从冻结app派生出的精确字节")
    expected_patch = _expected_derived_patch(base_app_raw, derived_app_raw)
    actual_patch = Path(selected["derived_source.patch"]["path"]).read_bytes()
    require(actual_patch == expected_patch,
            "derived_source.patch不是冻结ZIP原始app到实际compiled app的精确diff")

    recovery_dir = exact_path(Path(external["recovery_zip"]["path"]).parent, directory=True)
    recovery_delivery_path = exact_path(recovery_dir / "delivery_manifest.json")
    require(selected_2b["recovery_zip"]["sha256"] == external["recovery_zip"]["sha256"],
            "2B冻结manifest与S4-B外部清单的恢复ZIP SHA不同")
    recovery_delivery, recovery_delivery_raw = read_json(recovery_delivery_path)
    require(recovery_delivery.get("schema_version") == 1 and recovery_delivery.get("stage") == "2B" and
            recovery_delivery.get("task_id") == "S2B-T15" and
            recovery_delivery.get("run_id") == "recovery_inputs_20261019_r02" and
            recovery_delivery.get("source_commit") == "e1b048f3a867f5608c2e12c385800fed055da1da",
            "恢复输入delivery manifest历史身份不符")
    recovery_entries = _manifest_entries(recovery_delivery)
    bundle_manifest_row = recovery_entries.get(f"report/evidence/S2B-T15/recovery_inputs_20261019_r02/{RECOVERY_BUNDLE_MANIFEST}")
    require(bundle_manifest_row is not None and bundle_manifest_row.get("role") == "result",
            "恢复交付清单未绑定ZIP成员manifest")
    recovery_zip_row = recovery_entries.get("report/evidence/S2B-T15/recovery_inputs_20261019_r02/recovery_bundle.zip")
    require(recovery_zip_row is not None and recovery_zip_row.get("role") == "artifact" and
            recovery_zip_row.get("sha256") == external["recovery_zip"]["sha256"],
            "恢复交付清单、2B冻结manifest与实测ZIP身份不一致")
    bundle_manifest_path = exact_path(recovery_dir / RECOVERY_BUNDLE_MANIFEST)
    require(sha256_file(bundle_manifest_path) == bundle_manifest_row["sha256"], "恢复ZIP成员manifest SHA不匹配")
    bindings[str(recovery_delivery_path)] = {"path": str(recovery_delivery_path),
                                              "sha256": sha256_bytes(recovery_delivery_raw),
                                              "bytes": len(recovery_delivery_raw),
                                              "role": "cross_checked_recovery_delivery_manifest"}
    bindings[str(bundle_manifest_path)] = {"path": str(bundle_manifest_path),
                                            "sha256": bundle_manifest_row["sha256"],
                                            "bytes": bundle_manifest_path.stat().st_size,
                                            "role": "recovery_bundle_manifest"}

    extracted_root = exact_path(temp_build / "bundle_extract", directory=True)
    expected_overlays = {
        "bundle/workspace/infer/src/s2b_inference_app.c": derived_app_path.read_bytes(),
        "bundle/workspace/infer/src/s4b_ps_trace.c": Path(compiled_sources["vitis/stage4/ps/s4b_ps_trace.c"]["path"]).read_bytes(),
        "bundle/workspace/infer/src/s4b_ps_trace.h": Path(compiled_sources["vitis/stage4/ps/s4b_ps_trace.h"]["path"]).read_bytes(),
        "bundle/workspace/infer/src/s4b_ps_build_config.h": (
            "#ifndef S4B_PS_BUILD_CONFIG_H\n"
            "#define S4B_PS_BUILD_CONFIG_H\n"
            "#include <stdint.h>\n"
            f"#define S4B_PS_BOOT_SEED UINT64_C(0x{boot_seed:016x})\n"
            f"#define S4B_PS_SESSION_FIRST 0x{session_first:08x}U\n"
            f"#define S4B_PS_SESSION_LAST 0x{session_last:08x}U\n"
            "#endif\n"
        ).encode("utf-8"),
    }
    bundle_info, bundle_member_bindings = _verify_bundle_members(
        Path(external["recovery_zip"]["path"]), bundle_manifest_path, extracted_root,
        expected_overlays, source_sha)
    for binding in bundle_member_bindings:
        bindings[binding["path"]] = binding
    init_source = Path(bundle_info["init_elf"]["path"])
    verified_payload = output_dir / "verified_payload"
    if write_verified_init:
        verified_payload.mkdir()
    else:
        exact_path(verified_payload, directory=True)
    init_copy = verified_payload / "init.elf"
    init_raw = init_source.read_bytes()
    if write_verified_init:
        _write_bytes_new(init_copy, init_raw)
    else:
        actual_init_copy = exact_path(init_copy)
        require(actual_init_copy.read_bytes() == init_raw,
                "prepare中的init.elf副本与冻结恢复ZIP实际成员字节不同")
    init_binding = {"path": str(exact_path(init_copy)), "sha256": sha256_bytes(init_raw),
                    "bytes": len(init_raw), "role": "verified_recovery_init_elf"}
    bindings[init_binding["path"]] = init_binding

    bit = selected_2b["bit"]
    require(external["xsa"]["sha256"] == EXPECTED_XSA_SHA256, "XSA SHA与冻结派生banner身份不符")
    require(external["model_manifest"]["sha256"] == EXPECTED_MODEL_SHA256, "模型manifest SHA与冻结身份不符")
    model_path = Path(external["model_manifest"]["path"])
    model, _ = read_json(model_path)
    gf8 = model.get("bindings", {}).get("gf8_package", {})
    require(type(gf8.get("path")) is str and re.fullmatch(r"[0-9a-f]{64}", str(gf8.get("sha256", ""))) is not None,
            "冻结模型manifest缺少权重包路径或SHA")
    require(gf8.get("sha256") == "f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39",
            "冻结模型权重包SHA与冻结模型身份不符")
    expected_banner = build_expected_ready_banner(derived, external["xsa"]["sha256"], external["model_manifest"]["sha256"])

    # 在prepare阶段只校验源码blob，不import项目工具模块。
    tool_blobs = _frozen_tool_blobs(w2b_root)
    tool_bindings = {name: {"git_path": name, "commit": FROZEN_2B_COMMIT,
                            "sha256": sha256_bytes(raw), "bytes": len(raw)}
                     for name, raw in tool_blobs.items()}

    decoder_path = exact_path(root / "scripts" / "stage4_s4b" / "decode_s4b_ps_trace.py")
    decoder_sha = sha256_file(decoder_path)
    decoder_text = decoder_path.read_text(encoding="utf-8")
    decoder_args = ("--expected-source-sha256", "--expected-boot-seed", "--output")
    require(all(argument in decoder_text for argument in decoder_args),
            "当前trace decoder没有稳定的SOURCE/seed/output CLI参数")
    decoder_manifest_row = entries.get("scripts/stage4_s4b/decode_s4b_ps_trace.py")
    bindings[str(decoder_path)] = {"path": str(decoder_path), "sha256": decoder_sha,
                                   "bytes": decoder_path.stat().st_size, "role": "current_trace_decoder_cli"}

    artifact_identity = {
        "build_run_id": source_run_id,
        "source_commit": source_commit,
        "derived_source_sha256": source_sha,
        "elf_sha256": elf["sha256"],
        "map_sha256": map_file["sha256"],
        "xsa_sha256": external["xsa"]["sha256"],
        "model_manifest_sha256": external["model_manifest"]["sha256"],
        "model_weights_sha256": gf8["sha256"],
        "bit_sha256": bit["sha256"],
        "init_elf_sha256": init_binding["sha256"],
        "memory_ranges_sha256": selected["memory_ranges.json"]["sha256"],
        "trace_abi": 1,
        "trace_log_abi": derived.get("trace_log_abi"),
        "boot_seed": boot_seed,
        "session_first": session_first,
        "session_last": session_last,
        "reservation_status": run_config["hardware_reservation_status"],
    }
    require(artifact_identity["trace_log_abi"] == "s4b-ps-tensor/1", "trace日志ABI身份不符")
    prep_sha_bindings = sorted(bindings.values(), key=lambda row: row["path"].casefold())
    require(len({row["path"].casefold() for row in prep_sha_bindings}) == len(prep_sha_bindings),
            "实际输入路径发生大小写别名")
    return {
        "schema_version": 1,
        "status": "OFFLINE_PREPARATION_VALID",
        "task_id": "S4-B-REAL-02B",
        "run_id": run_id,
        "source_build_run_id": source_run_id,
        "project_root": str(root),
        "output_run_dir": str(output_dir),
        "source_evidence": {
            "delivery_manifest": delivery_binding,
            "source_commit_recorded": source_commit,
            "current_head_at_prepare": current_head,
            "external_inputs_inventory": selected["external_inputs_inventory.json"],
            "external_inputs_inventory_raw_sha256": sha256_bytes(inventory_raw),
            "compiled_app_source": bindings[str(derived_app_path)],
            "recovery_delivery_manifest": {
                "path": str(recovery_delivery_path),
                "sha256": sha256_bytes(recovery_delivery_raw),
                "outer_anchor": "2B冻结manifest绑定ZIP原始SHA；该历史sidecar仅交叉核对ZIP和bundle manifest",
            },
            "bundle_manifest": {"path": str(bundle_manifest_path), "sha256": bundle_info["sha256"]},
            "frozen_2b_manifest": {"path": str(frozen_manifest_path), "sha256": frozen_manifest_sha},
            "frozen_2b_commit": FROZEN_2B_COMMIT,
            "frozen_tool_sources": tool_bindings,
            "decoder_cli": {"path": str(decoder_path), "sha256": decoder_sha,
                            "historical_manifest_sha256": decoder_manifest_row.get("sha256")
                            if type(decoder_manifest_row) is dict else None,
                            "matches_historical_manifest": type(decoder_manifest_row) is dict and
                            decoder_manifest_row.get("sha256") == decoder_sha,
                            "interface_arguments": list(decoder_args)},
        },
        "artifact_identity": artifact_identity,
        "artifact_identity_sha256": artifact_identity_sha256(artifact_identity),
        "ready_banner": {"text": expected_banner.decode("ascii"), "hex": expected_banner.hex(),
                         "sha256": sha256_bytes(expected_banner)},
        "memory_ranges": memory,
        "model_weights_input": {"path_from_model_manifest": gf8["path"], "sha256": gf8["sha256"],
                                 "expected_bytes": WEIGHT_BYTES, "header_magic_hex": "4746494e54385731"},
        "bindings": prep_sha_bindings,
        "hardware_gate": {
            "status": "BLOCKED_BEFORE_HARDWARE",
            "missing_conditions": list(REQUIRED_GATE_RECORDS),
            "reason": f"{source_run_id}仅标记BUILD_ONLY_NOT_RESERVED_FOR_HARDWARE；本轮无S4-B实物授权、真实OFFERED→CLAIMED排他会话与地址/时基G0批准。",
            "execution_this_task": "NOT_RUN",
            "system_stop_is_cold_lifecycle_proof": False,
        },
        "limitations": [
            "离线来源绑定不代表READY、PS、PL、UART、JTAG、DDR或实物会话已验证。",
            f"此准备没有预留{source_run_id}的boot_seed/session，不能直接用于硬件执行。",
            "共享地址图、时基及4-D硬件授权条件仍需正式记录和独立审查。",
            "PS张量诊断不覆盖RGB resize、letterbox、量化预处理或完整阶段4摄像头G5。",
        ],
        "hardware_execution": "NOT_RUN",
    }


def validate_preparation(path: Path) -> PreparedRun:
    """从准备记录绑定的构建RunId重新构建身份，不把自报行当来源证明。"""
    actual_path = exact_path(path)
    data, _ = read_json(actual_path)
    require(data.get("schema_version") == 1 and data.get("status") == "OFFLINE_PREPARATION_VALID" and
            data.get("task_id") == "S4-B-REAL-02B", "离线准备记录状态或schema不符")
    run_id = _validate_run_id(data.get("run_id"))
    root = exact_path(Path(__file__).absolute().parents[2], directory=True)
    require(data.get("project_root") == str(root), "准备记录project_root不是当前adapter所在w4仓库")
    output_dir = exact_path(data.get("output_run_dir", ""), directory=True)
    require(actual_path.parent == output_dir and output_dir.name == run_id,
            "准备记录路径与精确RunId目录不一致")
    require(output_dir.parent == exact_path(root / "tmp" / "4" / "S4-B-REAL-02B", directory=True),
            "准备记录不在指定隔离目录")
    source_run_id = data.get("source_build_run_id")
    require(type(source_run_id) is str and BUILD_RUN_ID_PATTERN.fullmatch(source_run_id) is not None,
            "准备记录未选择格式正确的S4-B构建RunId")
    evidence_dir = exact_path(root / "report" / "evidence" / "S4-B" / source_run_id,
                              directory=True)
    build_manifest_path = exact_path(evidence_dir / "delivery_manifest.json")
    authoritative = _collect_preparation(root, source_run_id, evidence_dir,
                                         build_manifest_path, output_dir, run_id,
                                         write_verified_init=False)
    require(set(data) == set(authoritative), "准备记录含缺失或未审字段")
    for key in set(authoritative) - {"source_evidence"}:
        require(data.get(key) == authoritative[key],
                f"准备记录字段与选定构建权威重建结果不同：{key}")
    recorded_evidence = data.get("source_evidence")
    expected_evidence = authoritative.get("source_evidence")
    require(type(recorded_evidence) is dict and type(expected_evidence) is dict,
            "准备记录source_evidence格式错误")
    recorded_head = recorded_evidence.get("current_head_at_prepare")
    require(type(recorded_head) is str and re.fullmatch(r"[0-9a-f]{40}", recorded_head) is not None,
            "准备记录current_head_at_prepare格式错误")
    resolved_head = _git_output(["-C", str(root), "rev-parse", "--verify",
                                 recorded_head + "^{commit}"]).decode("ascii").strip()
    require(resolved_head == recorded_head, "准备记录current_head_at_prepare不是可解析历史提交")
    recorded_without_dynamic = dict(recorded_evidence)
    expected_without_dynamic = dict(expected_evidence)
    recorded_without_dynamic.pop("current_head_at_prepare", None)
    expected_without_dynamic.pop("current_head_at_prepare", None)
    require(recorded_without_dynamic == expected_without_dynamic,
            "准备记录source_evidence与选定构建输入链重建结果不同")
    encoded_banner = bytes.fromhex(data["ready_banner"]["hex"])
    require(sha256_bytes(encoded_banner) == data["ready_banner"]["sha256"] and
            encoded_banner == data["ready_banner"]["text"].encode("ascii") and
            encoded_banner.endswith(b"\r\n"),
            "准备READY banner的ASCII、SHA或实际CRLF不一致")
    return PreparedRun(actual_path, data)


def _binding_row(data: Mapping[str, Any], role: str, filename: str) -> dict[str, Any]:
    """从已记录的SHA绑定中唯一定位具有指定角色和文件名的内容。"""
    rows = data.get("bindings")
    matches = [row for row in rows if type(row) is dict and row.get("role") == role and
               Path(row.get("path", "")).name == filename] if type(rows) is list else []
    require(len(matches) == 1, f"身份重建要求唯一{role}/{filename}绑定，实际{len(matches)}项")
    return matches[0]


def _read_bound_json(row: Mapping[str, Any]) -> dict[str, Any]:
    """读取并二次核对一条已绑定JSON的实际字节摘要。"""
    path = exact_path(row["path"])
    raw = path.read_bytes()
    require(sha256_bytes(raw) == row.get("sha256") and len(raw) == row.get("bytes"),
            f"身份来源JSON在重建时发生变化：{path}")
    data, _ = read_json(path)
    return data


def _reconstruct_artifact_identity(data: Mapping[str, Any]) -> dict[str, Any]:
    """从仓库内选定manifest、ZIP和实际编译输入链重建规范身份。"""
    require(data.get("task_id") == "S4-B-REAL-02B", "身份重建任务ID不符")
    source_run_id = data.get("source_build_run_id")
    require(type(source_run_id) is str and BUILD_RUN_ID_PATTERN.fullmatch(source_run_id) is not None,
            "身份重建来源不是有效S4-B构建RunId")
    root = exact_path(Path(__file__).absolute().parents[2], directory=True)
    require(data.get("project_root") == str(root), "身份重建project_root不是当前仓库")
    output_dir = exact_path(data.get("output_run_dir", ""), directory=True)
    run_id = _validate_run_id(data.get("run_id"))
    require(output_dir.name == run_id and output_dir.parent ==
            exact_path(root / "tmp" / "4" / "S4-B-REAL-02B", directory=True),
            "身份重建输出Run目录不在指定隔离路径")
    evidence_dir = exact_path(root / "report" / "evidence" / "S4-B" / source_run_id,
                              directory=True)
    rebuilt = _collect_preparation(root, source_run_id, evidence_dir,
                                   exact_path(evidence_dir / "delivery_manifest.json"),
                                   output_dir, run_id, write_verified_init=False)
    return rebuilt["artifact_identity"]


def _binding_row_by_path(data: Mapping[str, Any], path: str, role: str) -> dict[str, Any]:
    """以逐字符路径和角色定位外部输入，拒绝同SHA不同路径替代。"""
    matches = [row for row in data.get("bindings", []) if type(row) is dict and
               row.get("role") == role and row.get("path") == path]
    require(len(matches) == 1, f"身份重建缺少唯一{role}路径绑定：{path}")
    return matches[0]


def _verified_artifact_identity(prepared: PreparedRun) -> tuple[dict[str, Any], str]:
    """重建身份并验证规范JSON摘要，拒绝仅由调用方自报的身份对象。"""
    identity = _reconstruct_artifact_identity(prepared.data)
    require(prepared.data.get("artifact_identity") == identity,
            "准备清单artifact_identity与绑定产物重建结果不同")
    digest = artifact_identity_sha256(identity)
    require(prepared.data.get("artifact_identity_sha256") == digest,
            "准备清单artifact_identity_sha256不是规范重建身份摘要")
    return identity, digest


def _parse_time(value: Any) -> datetime | None:
    """解析带时区的ISO时间并统一到UTC+8。"""
    if type(value) is not str:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(hours=8):
        return None
    return parsed.astimezone(TZ_UTC8)


def _load_gate_record(value: Any, role: str) -> tuple[dict[str, Any], dict[str, str]]:
    """要求门禁记录是完整SHA绑定的真实文件，而非调用方状态字符串。"""
    require(type(value) is dict and set(value) == {"path", "sha256"}, f"{role}必须是path+sha256绑定")
    path = exact_path(value["path"])
    actual_sha = sha256_file(path)
    require(type(value["sha256"]) is str and actual_sha == value["sha256"], f"{role}记录SHA不符")
    data, raw = read_json(path)
    return data, {"path": str(path), "sha256": sha256_bytes(raw)}


def _git_state_snapshot(root: Path) -> dict[str, Any]:
    """读取真实HEAD身份及工作树中的当前STATE，发现未提交撤销。"""
    snapshot = _git_record_snapshot(root, HANDOFF_SOURCE_PATH)
    working_path = exact_path(root / HANDOFF_SOURCE_PATH)
    working_raw = working_path.read_bytes()
    try:
        snapshot["state_text"] = snapshot["state_raw"].decode("utf-8")
        snapshot["working_state_text"] = working_raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise AdapterError("权威STATE不是UTF-8") from error
    snapshot["working_state_raw"] = working_raw
    return snapshot


def _git_record_snapshot(root: Path, relative_path: str) -> dict[str, Any]:
    """从指定worktree的HEAD读取单个受信记录的真实Git身份与字节。"""
    root = exact_path(root, directory=True)
    actual_root_text = _git_output(["-C", str(root), "rev-parse", "--show-toplevel"]).decode("utf-8").strip()
    actual_root = exact_path(actual_root_text, directory=True)
    require(actual_root.resolve() == root.resolve(), "Git根目录与指定权威worktree不一致")
    relative = safe_relative_path(relative_path)
    git_path = relative.as_posix()
    branch = _git_output(["-C", str(root), "branch", "--show-current"]).decode("utf-8").strip()
    head = _git_output(["-C", str(root), "rev-parse", "HEAD"]).decode("ascii").strip()
    require(branch and re.fullmatch(r"[0-9a-f]{40}", head) is not None,
            "权威worktree branch或HEAD格式无效")
    blob_oid = _git_output(["-C", str(root), "rev-parse", "--verify", f"HEAD:{git_path}"]
                           ).decode("ascii").strip()
    state_raw = _git_output(["-C", str(root), "show", f"HEAD:{git_path}"])
    require(blob_oid and state_raw, "权威HEAD缺少非空记录blob")
    return {
        "worktree": str(root), "branch": branch, "commit": head,
        "path": git_path, "blob_oid": blob_oid,
        "sha256": sha256_bytes(state_raw), "state_raw": state_raw,
    }


def _git_record_snapshot_at_commit(root: Path, relative_path: str, commit: Any) -> dict[str, Any]:
    """从受信当前分支历史中的指定commit读取不可变记录blob。"""
    root = exact_path(root, directory=True)
    relative = safe_relative_path(relative_path)
    git_path = relative.as_posix()
    branch = _git_output(["-C", str(root), "branch", "--show-current"]).decode("utf-8").strip()
    head = _git_output(["-C", str(root), "rev-parse", "HEAD"]).decode("ascii").strip()
    require(branch and re.fullmatch(r"[0-9a-f]{40}", head) is not None and
            type(commit) is str and re.fullmatch(r"[0-9a-f]{40}", commit) is not None,
            "指定记录的branch或commit格式无效")
    resolved = _git_output(["-C", str(root), "rev-parse", "--verify", commit + "^{commit}"]
                           ).decode("ascii").strip()
    require(resolved == commit, "指定记录commit不是当前受信仓库中的真实commit")
    ancestry = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", commit, head],
                              check=False, capture_output=True)
    require(ancestry.returncode == 0, "指定记录commit不在受信当前分支历史中")
    blob_oid = _git_output(["-C", str(root), "rev-parse", "--verify",
                            f"{commit}:{git_path}"]).decode("ascii").strip()
    record_raw = _git_output(["-C", str(root), "show", f"{commit}:{git_path}"])
    require(blob_oid and record_raw, "指定commit缺少非空记录blob")
    return {
        "worktree": str(root), "branch": branch, "commit": commit,
        "path": git_path, "blob_oid": blob_oid,
        "sha256": sha256_bytes(record_raw), "state_raw": record_raw,
    }


def _parse_state_handoff_rows(state_raw: bytes) -> tuple[str, list[dict[str, str]]]:
    """从提交版STATE只解析完整且字段顺序固定的11字段行。"""
    try:
        text = state_raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise AdapterError("权威STATE不是UTF-8") from error
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        row_start = line.find("任务=")
        if row_start < 0:
            continue
        fields = [part.strip() for part in line[row_start:].strip().strip("|").split("|")]
        if len(fields) != len(HANDOFF_FIELDS):
            continue
        row: dict[str, str] = {}
        valid = True
        for field_text, expected_field in zip(fields, HANDOFF_FIELDS):
            key, separator, raw_value = field_text.partition("=")
            value = raw_value.strip()
            if (not separator or key.strip() != expected_field or
                    not value.startswith("`") or not value.endswith("`")):
                valid = False
                break
            row[expected_field] = value[1:-1]
        if valid and tuple(row) == HANDOFF_FIELDS and all(type(value) is str for value in row.values()):
            rows.append(row)
    return text, rows


def _unique_handoff_task_row(rows: list[dict[str, str]], task_marker: str,
                             role: str) -> dict[str, str]:
    """在核对scope等字段前，要求任务标记只出现一次。"""
    candidates = [row for row in rows if row.get("任务") == task_marker]
    require(len(candidates) == 1, f"{role}任务标记必须恰有一条11字段记录")
    return candidates[0]


def _parse_handoff_evidence(value: Any, role: str) -> dict[str, str]:
    """解析分号分隔的唯一key=value证据项，拒绝重复键和歧义文本。"""
    require(type(value) is str and value, f"{role}证据入口必须是非空key=value串")
    parsed: dict[str, str] = {}
    for raw_item in value.split(";"):
        item = raw_item.strip()
        key, separator, field_value = item.partition("=")
        key, field_value = key.strip(), field_value.strip()
        require(separator and item.count("=") == 1 and
                re.fullmatch(r"[a-z][a-z0-9_]*", key) is not None and field_value,
                f"{role}证据入口包含格式不完整或歧义的key=value项")
        require(key not in parsed, f"{role}证据入口包含重复键：{key}")
        parsed[key] = field_value
    return parsed


def _verify_handoff_reference_values(handoff: Mapping[str, Any], offer: Mapping[str, str],
                                     claim: Mapping[str, str], hardware_run_id: str,
                                     source_context: Mapping[str, Any],
                                     offer_start_commit: str) -> None:
    """逐键精确核对硬件RunId及claim引用，不接受前缀相似值。"""
    require(handoff.get("hardware_run_id") == hardware_run_id,
            "handoff顶层hardware_run_id与本次RunId不精确匹配")
    offer_evidence = _parse_handoff_evidence(offer.get("证据入口"), "main OFFER")
    require(set(offer_evidence) == {"hardware_run_id"} and
            offer_evidence.get("hardware_run_id") == hardware_run_id,
            "main OFFER证据入口hardware_run_id与本次RunId不精确匹配")
    claim_evidence = _parse_handoff_evidence(claim.get("证据入口"), "w4 CLAIM")
    expected_claim_evidence = {
        "offer_commit": str(source_context["commit"]),
        "offer_blob_oid": str(source_context["blob_oid"]),
        "offer_sha256": str(source_context["sha256"]),
        "offer_source_commit": offer_start_commit,
        "hardware_run_id": hardware_run_id,
        "scope": "S4B_PS_TENSOR_DIAGNOSTIC",
    }
    require(set(claim_evidence) == set(expected_claim_evidence) and
            all(claim_evidence.get(key) == expected for key, expected in expected_claim_evidence.items()),
            "w4 CLAIM证据入口的RunId、scope或OFFER引用未逐键精确匹配")


def _state_stage_owner(state_text: str) -> str:
    """从提交版阶段STATE读出当前独占写权负责人。"""
    owners = re.findall(r"(?m)^\*\*写权：(.+?)受.+?独占[，。]", state_text)
    require(len(owners) == 1 and owners[0].strip(), "提交版阶段STATE缺少唯一写权负责人")
    return owners[0].strip()


def _require_ancestor_commit(root: Path, candidate: Any, head: str) -> str:
    """要求记录中的起始提交是当前权威分支上真实可达的commit。"""
    require(type(candidate) is str and re.fullmatch(r"[0-9a-f]{40}", candidate) is not None,
            "交接起始提交不是完整Git commit SHA")
    resolved = _git_output(["-C", str(root), "rev-parse", "--verify",
                            candidate + "^{commit}"]).decode("ascii").strip()
    require(resolved == candidate, "交接起始提交不是Git中的真实commit")
    result = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", candidate, head],
                            check=False, capture_output=True)
    require(result.returncode == 0, "交接起始提交不在权威分支HEAD历史中")
    return resolved


def _hardware_authority_snapshot() -> dict[str, Any]:
    """只从代码内允许的main总控STATE读取当前硬件交接权威来源。"""
    source_context = _git_state_snapshot(HANDOFF_TRUSTED_SOURCE_ROOT)
    require(source_context["branch"] == HANDOFF_TRUSTED_SOURCE_BRANCH,
            "硬件交接来源不是allowlist中的main总控分支")
    return source_context


def _verified_hardware_handoff(prepared: PreparedRun, handoff: Mapping[str, Any],
                               hardware_run_id: str, stage_context: Mapping[str, Any]) -> dict[str, str]:
    """核对main真实OFFERED、w4真实CLAIMED和allowlist板卡释放记录。"""
    current_source_context = _hardware_authority_snapshot()
    project_root = exact_path(prepared.data["project_root"], directory=True)
    require(project_root == exact_path(HANDOFF_TRUSTED_RECEIVER_ROOT, directory=True) and
            stage_context.get("worktree") == str(project_root) and
            stage_context.get("branch") == HANDOFF_TRUSTED_RECEIVER_BRANCH,
            "CLAIMED接收记录不是allowlist指定的w4工作树/分支")
    stage_owner = _state_stage_owner(str(stage_context["state_text"]))
    working_stage_text = str(stage_context.get("working_state_text", ""))
    require(_state_stage_owner(working_stage_text) == stage_owner,
            "w4工作树STATE负责人和当前提交负责人不一致")
    authority_input = handoff.get("authority_source")
    require(type(authority_input) is dict,
            "handoff缺少由main当前历史可达的原OFFER blob指针")
    source_context = _git_record_snapshot_at_commit(
        HANDOFF_TRUSTED_SOURCE_ROOT, HANDOFF_SOURCE_PATH, authority_input.get("commit"))
    require(source_context["branch"] == HANDOFF_TRUSTED_SOURCE_BRANCH and
            current_source_context["branch"] == HANDOFF_TRUSTED_SOURCE_BRANCH,
            "硬件交接来源不是allowlist中的main总控分支")
    expected_source = {key: source_context[key] for key in (
        "worktree", "branch", "commit", "path", "blob_oid", "sha256")}
    expected_source["kind"] = HANDOFF_SOURCE_KIND
    require(authority_input == expected_source,
            "handoff来源未绑定allowlist总控worktree/branch/offer commit/STATE blob")
    _, offer_rows = _parse_state_handoff_rows(source_context["state_raw"])
    _, current_main_rows = _parse_state_handoff_rows(current_source_context["state_raw"])
    _, working_main_rows = _parse_state_handoff_rows(current_source_context["working_state_raw"])
    offer = _unique_handoff_task_row(offer_rows, HANDOFF_OFFER_TASK_MARKER, "main OFFER")
    current_offer = _unique_handoff_task_row(
        current_main_rows, HANDOFF_OFFER_TASK_MARKER, "main当前HEAD OFFER")
    working_offer = _unique_handoff_task_row(
        working_main_rows, HANDOFF_OFFER_TASK_MARKER, "main工作树 OFFER")
    require(offer == current_offer == working_offer,
            "main当前HEAD/工作树不再包含原offer提交中的唯一未撤销硬件OFFER记录")
    require(offer["允许修改范围"] == "S4B_PS_TENSOR_DIAGNOSTIC",
            "main唯一硬件行的scope不匹配")
    expected_source_tree = f"{source_context['worktree']} / {source_context['branch']}"
    require(offer["工作树/分支"] == expected_source_tree,
            "硬件交接发出方工作树/分支与实际main checkout不一致")
    require(offer["负责人"] == HANDOFF_TRUSTED_SENDER,
            "硬件交接发出方不是allowlist指定的项目总控")
    offer_start_commit = _require_ancestor_commit(HANDOFF_TRUSTED_SOURCE_ROOT,
                                                   offer["起始提交"], source_context["commit"])
    require(offer["让出声明"] == "OFFERED" and
            offer["状态/下一接手方"] == f"OFFERED {stage_owner}" and
            _recent_time(offer["心跳(UTC+8)"], maximum_age_seconds=3600),
            "总控硬件行不是近期OFFERED或未明确指定当前w4负责人")
    require(handoff.get("task_id") == "S4-B-REAL-02B" and
            offer["允许修改范围"] == handoff.get("scope") == "S4B_PS_TENSOR_DIAGNOSTIC" and
            bool(offer["恢复命令"]),
            "权威OFFER任务、精确诊断scope或恢复入口不匹配")

    claim_input = handoff.get("claim_source")
    require(type(claim_input) is dict,
            "handoff缺少由w4当前分支历史可达的真实CLAIM blob指针")
    claim_context = _git_record_snapshot_at_commit(project_root, HANDOFF_SOURCE_PATH,
                                                   claim_input.get("commit"))
    expected_claim_source = {key: claim_context[key] for key in (
        "worktree", "branch", "commit", "path", "blob_oid", "sha256")}
    expected_claim_source["kind"] = HANDOFF_CLAIM_SOURCE_KIND
    require(claim_input == expected_claim_source and
            claim_context["branch"] == stage_context["branch"],
            "CLAIMED来源未绑定当前w4分支历史中的CLAIM blob")
    _, claim_rows = _parse_state_handoff_rows(claim_context["state_raw"])
    _, current_claim_rows = _parse_state_handoff_rows(stage_context["state_raw"])
    _, working_claim_rows = _parse_state_handoff_rows(stage_context["working_state_raw"])
    claim = _unique_handoff_task_row(claim_rows, HANDOFF_CLAIM_TASK_MARKER, "w4 CLAIM")
    current_claim = _unique_handoff_task_row(
        current_claim_rows, HANDOFF_CLAIM_TASK_MARKER, "w4当前HEAD CLAIM")
    working_claim = _unique_handoff_task_row(
        working_claim_rows, HANDOFF_CLAIM_TASK_MARKER, "w4工作树 CLAIM")
    require(claim == current_claim == working_claim,
            "w4当前HEAD/工作树不再包含原claim提交中的唯一真实CLAIMED回执")
    require(claim["允许修改范围"] == "S4B_PS_TENSOR_DIAGNOSTIC",
            "w4唯一硬件CLAIM行的scope不匹配")
    expected_stage_tree = f"{stage_context['worktree']} / {stage_context['branch']}"
    _verify_handoff_reference_values(
        handoff, offer, claim, hardware_run_id, source_context, offer_start_commit)
    require(claim["负责人"] == stage_owner and claim["工作树/分支"] == expected_stage_tree and
            claim["让出声明"] == "CLAIMED" and
            claim["状态/下一接手方"] == f"CLAIMED {stage_owner}" and
            _recent_time(claim["心跳(UTC+8)"], maximum_age_seconds=3600),
            "w4真实CLAIMED回执未精确引用main OFFER提交/blob/SHA、RunId与相同scope")
    claim_start_commit = _require_ancestor_commit(project_root, claim["起始提交"], claim_context["commit"])
    require(claim["恢复命令"], "w4 CLAIMED回执缺少恢复命令")
    require(handoff.get("claim_record_kind") == HANDOFF_CLAIM_KIND and
            handoff.get("claim_fields") == claim,
            "调用方CLAIMED回执没有逐字段匹配当前w4提交版STATE")
    require(handoff.get("record_kind") == HANDOFF_RECORD_KIND and
            handoff.get("handoff_fields") == offer and
            handoff.get("source_commit") == offer_start_commit and
            handoff.get("claim_commit") == claim_start_commit and
            handoff.get("sender") == offer["负责人"] and
            handoff.get("sender_worktree_branch") == offer["工作树/分支"] and
            handoff.get("uncommitted_changes_owner") == offer["未提交改动归属"] and
            handoff.get("receiver") == stage_owner and
            handoff.get("receiver_worktree_branch") == stage_context["branch"],
            "handoff字段未逐项匹配可信来源记录或当前接收方")
    return offer


def _exact_diagnostic_operations(value: Any) -> bool:
    """仅接受完整且无重复项的S4-B诊断操作集合。"""
    return (type(value) is list and len(value) == len(DIAGNOSTIC_OPERATIONS) and
            all(type(item) is str for item in value) and set(value) == DIAGNOSTIC_OPERATIONS)


def validate_hardware_gates(prepared: PreparedRun, hardware_run_id: str,
                            gate_files: Mapping[str, Any] | None) -> GateCheck:
    """只读核验真实授权、交接、独占、G0、review、时间、范围和冷依据记录。"""
    hardware_run_id = _validate_run_id(hardware_run_id)
    supplied = dict(gate_files or {})
    missing: list[str] = []
    records: dict[str, dict[str, Any]] = {}
    record_bindings: dict[str, dict[str, str]] = {}
    for role in REQUIRED_GATE_RECORDS:
        if role not in supplied:
            missing.append(f"{role}:record_missing")
            continue
        try:
            record, binding = _load_gate_record(supplied[role], role)
            records[role], record_bindings[role] = record, binding
        except (AdapterError, OSError, ValueError) as error:
            missing.append(f"{role}:{error}")

    identity = prepared.data["artifact_identity"]
    if records:
        identity, identity_digest = _verified_artifact_identity(prepared)
        auth = records.get("operator_authorization", {})
        auth_time = _parse_time(auth.get("authorized_at_utc8"))
        expiry = _parse_time(auth.get("expires_at_utc8"))
        now = datetime.now(TZ_UTC8)
        project_root = exact_path(prepared.data["project_root"], directory=True)
        stage_context: dict[str, Any] | None = None
        try:
            stage_context = _git_state_snapshot(project_root)
            branch = str(stage_context["branch"])
            stage_receiver = _state_stage_owner(str(stage_context["state_text"]))
        except (AdapterError, OSError, ValueError) as error:
            branch, stage_receiver = "", None
            missing.append(f"receiver_worktree:{error}")
        if (auth.get("status") != "AUTHORIZED" or auth.get("task_id") != "S4-B-REAL-02B" or
                auth.get("hardware_run_id") != hardware_run_id or
                auth.get("authorized_by") not in {"Wong", stage_receiver} or
                auth.get("scope") != "S4B_PS_TENSOR_DIAGNOSTIC" or not auth.get("authorization_id") or
                auth_time is None or expiry is None or not auth_time <= now < expiry):
            missing.append("operator_authorization:scope_or_time_invalid")
        if not _exact_diagnostic_operations(auth.get("operations")):
            missing.append("operator_authorization:operations_not_exact_diagnostic_set")
        if auth.get("artifact_identity_sha256") != identity_digest:
            missing.append("operator_authorization:artifact_identity_sha256_mismatch")

        handoff = records.get("hardware_session_handoff", {})
        try:
            require(stage_context is not None, "无法从当前阶段HEAD核实接收者身份")
            _verified_hardware_handoff(prepared, handoff, hardware_run_id, stage_context)
        except (AdapterError, OSError, ValueError) as error:
            missing.append(f"hardware_session_handoff:authoritative_record_invalid:{error}")
        if handoff.get("artifact_identity_sha256") != identity_digest:
            missing.append("hardware_session_handoff:artifact_identity_sha256_mismatch")
        sdk_target = handoff.get("sdk_target_binding")
        if not _valid_bound_file(sdk_target):
            missing.append("hardware_session_handoff:sdk_target_binding_invalid")

        exclusive = records.get("exclusive_session", {})
        if (exclusive.get("status") != "PASS" or exclusive.get("exclusive") is not True or
                exclusive.get("hardware_run_id") != hardware_run_id or
                exclusive.get("artifact_identity_sha256") != identity_digest or
                type(exclusive.get("hw_server_pid")) is not int or exclusive.get("hw_server_pid") <= 0 or
                exclusive.get("xsdb_peer") not in ({"Host": "localhost", "Port": "3121"},
                                                     {"Host": "127.0.0.1", "Port": "3121"}) or
                not isinstance(exclusive.get("uart_port"), str) or not exclusive.get("uart_port") or
                not _recent_time(exclusive.get("verified_at_utc8"), maximum_age_seconds=1800)):
            missing.append("exclusive_session:peer_or_live_exclusivity_not_proven")

        g0 = records.get("g0_approval", {})
        if (g0.get("status") != "APPROVED" or g0.get("task_id") != "S4-B-REAL-02B" or
                g0.get("hardware_run_id") != hardware_run_id or g0.get("scope") != "BOARD_INJECTION" or
                g0.get("address_map_status") != "APPROVED" or
                g0.get("address_map_sha256") != identity.get("map_sha256") or
                g0.get("memory_ranges_sha256") != identity.get("memory_ranges_sha256") or
                g0.get("artifact_identity_sha256") != identity_digest or
                g0.get("shared_address_status") != "APPROVED" or
                not re.fullmatch(r"[0-9a-f]{64}", str(g0.get("shared_address_map_sha256", ""))) or
                g0.get("timebase_status") != "APPROVED" or not g0.get("approval_id")):
            missing.append("g0_approval:address_map_shared_address_or_timebase_not_approved")

        review = records.get("command_delivery_review", {})
        if (review.get("status") != "PASS" or review.get("task_id") != "S4-B-REAL-02B" or
                review.get("hardware_run_id") != hardware_run_id or
                not re.fullmatch(r"[0-9a-f]{64}", str(review.get("review_sha256", ""))) or
                review.get("artifact_identity_sha256") != identity_digest or
                review.get("reviewed_adapter_sha256") != sha256_file(Path(__file__))):
            missing.append("command_delivery_review:independent_review_not_bound_to_adapter")

        timing = records.get("timing_freeze", {})
        if (timing.get("status") != "APPROVED" or timing.get("hardware_run_id") != hardware_run_id or
                timing.get("artifact_identity_sha256") != identity_digest or
                timing.get("timebase_status") != "APPROVED" or timing.get("threshold_status") != "APPROVED" or
                not timing.get("approval_id")):
            missing.append("timing_freeze:timebase_or_threshold_not_approved")

        reservation = records.get("range_reservation", {})
        if not _reservation_matches(reservation, hardware_run_id, identity, identity_digest):
            missing.append("range_reservation:seed_or_session_not_reserved_disjointly")

        cold = records.get("cold_basis", {})
        if (cold.get("status") != "PASS" or cold.get("hardware_run_id") != hardware_run_id or
                cold.get("artifact_identity_sha256") != identity_digest or
                cold.get("old_axi_lifecycle_cleared") is not True or
                not _valid_bound_file(cold.get("evidence_binding")) or
                cold.get("basis_kind") not in {"physical_power_cycle", "independently_proven_cold_lifecycle"}):
            missing.append("cold_basis:old_AXI_lifecycle_not_independently_proven")

    all_bindings = {**record_bindings}
    return GateCheck(not missing, tuple(missing), records, all_bindings)


def _recent_time(value: Any, maximum_age_seconds: int) -> bool:
    """判断带时区的核验时刻是否仍在短期有效窗口内。"""
    parsed = _parse_time(value)
    return parsed is not None and 0 <= (datetime.now(TZ_UTC8) - parsed).total_seconds() <= maximum_age_seconds


def _valid_bound_file(value: Any) -> bool:
    """核验嵌套文件绑定只含绝对路径和当前原字节SHA。"""
    try:
        require(type(value) is dict and set(value) == {"path", "sha256"}, "必须是path+sha256")
        path = exact_path(value["path"])
        return sha256_file(path) == value["sha256"] and re.fullmatch(r"[0-9a-f]{64}", value["sha256"]) is not None
    except (AdapterError, OSError, TypeError):
        return False


def _reservation_matches(reservation: Mapping[str, Any], hardware_run_id: str,
                         identity: Mapping[str, Any], identity_digest: str) -> bool:
    """确认本次非零seed与session闭区间专属且不与旧预留重叠。"""
    if (reservation.get("status") != "RESERVED" or reservation.get("hardware_run_id") != hardware_run_id or
            reservation.get("artifact_identity_sha256") != identity_digest or
            reservation.get("boot_seed") != identity.get("boot_seed") or
            reservation.get("session_first") != identity.get("session_first") or
            reservation.get("session_last") != identity.get("session_last") or
            reservation.get("scope") != "S4-B-REAL-02B"):
        return False
    older = reservation.get("existing_reservations")
    if type(older) is not list:
        return False
    seed = identity["boot_seed"]
    low, high = identity["session_first"], identity["session_last"]
    for row in older:
        if type(row) is not dict:
            return False
        if row.get("boot_seed") == seed:
            return False
        if row.get("hardware_run_id") == hardware_run_id:
            return False
        if type(row.get("session_first")) is not int or type(row.get("session_last")) is not int:
            return False
        if low <= row["session_last"] and row["session_first"] <= high:
            return False
    return True


def _read_ready_banner(wire: Any, expected: bytes, timeout_seconds: float = 20.0) -> bytes:
    """逐字节读取完整启动横幅；原始接收字节由冻结WireSession即时落盘。"""
    require(type(expected) is bytes and expected.endswith(b"\r\n") and expected.isascii(),
            "READY期望值必须是完整ASCII/CRLF原字节")
    require(type(timeout_seconds) in (int, float) and timeout_seconds > 0,
            "READY观察期限无效")
    received = bytearray()
    deadline = time.monotonic() + float(timeout_seconds)
    while not received.endswith(b"\r\n"):
        require(len(received) < 320, "READY banner超过320字节")
        received.extend(wire.read_exact(1, deadline))
    raw = bytes(received)
    require(raw == expected, "实际READY banner与SOURCE/XSA/MODEL/DIAG/TRACE_ABI/CRLF绑定不符")
    return raw


def _stage_verified_tool_modules(prepared: PreparedRun, evidence_dir: Path,
                                 repo: Path) -> dict[str, Any]:
    """导入前核验冻结Git闭包，随后从唯一隔离目录导入并复核__file__。"""
    collisions = [name for name in TOOL_MODULE_NAMES if name in sys.modules]
    require(not collisions, f"拒绝使用预加载的同名工具模块：{collisions}")
    blobs = _frozen_tool_blobs(repo)
    prep_tool_bindings = prepared.data["source_evidence"]["frozen_tool_sources"]
    for relative, raw in blobs.items():
        expected = prep_tool_bindings.get(relative, {}).get("sha256")
        require(expected == sha256_bytes(raw), f"冻结工具与prepare阶段blob不同：{relative}")

    package_name = "s4b_frozen_" + uuid.uuid4().hex
    package_parent = evidence_dir / "verified_tools"
    if not package_parent.exists():
        package_parent.mkdir()
    exact_path(package_parent, directory=True)
    package_root = package_parent / package_name
    package_root.mkdir()
    exact_path(package_root, directory=True)
    verification_dir = package_root / "verification"
    verification_dir.mkdir()
    exact_path(verification_dir, directory=True)
    _write_bytes_new(package_root / "__init__.py", b"\n")
    _write_bytes_new(verification_dir / "__init__.py", b"\n")
    staged: dict[str, Path] = {}
    for relative, raw in blobs.items():
        name = safe_relative_path(relative).name
        target = verification_dir / name
        _write_bytes_new(target, raw)
        require(sha256_file(target) == FROZEN_TOOL_SHA256[relative],
                f"冻结工具隔离副本SHA不匹配：{relative}")
        staged[relative] = exact_path(target)

    sys_path_before = list(sys.path)
    modules_before = set(sys.modules)
    try:
        sys.path[:0] = [str(verification_dir), str(package_parent)]
        delivery_module = importlib.import_module("check_stage_delivery")
        require(exact_path(delivery_module.__file__) == staged["verification/check_stage_delivery.py"],
                "导入后的check_stage_delivery.__file__不在核验隔离目录")
        jtag_module = importlib.import_module(f"{package_name}.verification.s2b_board_jtag")
        transport_module = importlib.import_module(f"{package_name}.verification.s2b_board_transport")
        elf_module = importlib.import_module(f"{package_name}.verification.check_s2b_ps_smoke_layout")
        expected_modules = (
            (jtag_module, "verification/s2b_board_jtag.py"),
            (transport_module, "verification/s2b_board_transport.py"),
            (elf_module, "verification/check_s2b_ps_smoke_layout.py"),
        )
        for module, relative in expected_modules:
            require(exact_path(module.__file__) == staged[relative],
                    f"导入后的{relative}.__file__不在核验隔离目录")
        stdlib_roots = (exact_path(Path(sys.prefix) / "Lib", directory=True),
                        exact_path(Path(sys.prefix) / "DLLs", directory=True))
        for name in set(sys.modules) - modules_before:
            module = sys.modules.get(name)
            module_path = getattr(module, "__file__", None)
            if module_path is None:
                continue
            loaded_path = exact_path(module_path)
            allowed_local = loaded_path == package_root or package_root in loaded_path.parents
            allowed_stdlib = any(loaded_path == root or root in loaded_path.parents
                                 for root in stdlib_roots)
            require(allowed_local or allowed_stdlib,
                    f"冻结工具闭包导入了未绑定的外部模块：{name} ({loaded_path})")
        require(getattr(jtag_module, "JtagController", None) is not None and
                getattr(jtag_module, "JtagWireSession", None) is not None,
                "冻结JtagController/JtagWireSession API缺失")
        return {
            "package_name": package_name,
            "package_root": str(exact_path(package_root, directory=True)),
            "verification_dir": str(exact_path(verification_dir, directory=True)),
            "jtag_module": jtag_module,
            "transport_module": transport_module,
            "delivery_module": delivery_module,
            "elf_module": elf_module,
            "paths": {key: str(value) for key, value in staged.items()},
            "sha256": {key: FROZEN_TOOL_SHA256[key] for key in staged},
        }
    except BaseException:
        for name in tuple(sys.modules):
            if (name == package_name or name.startswith(package_name + ".") or
                    name == "check_stage_delivery") and name not in modules_before:
                sys.modules.pop(name, None)
        raise
    finally:
        sys.path[:] = sys_path_before


def _binding(path: str | Path, digest: str | None = None) -> dict[str, str]:
    """为JtagController生成其严格要求的path/sha256二元绑定。"""
    actual = exact_path(path)
    value = sha256_file(actual)
    require(digest is None or value == digest, f"JTAG部署绑定SHA变化：{actual}")
    return {"path": str(actual), "sha256": value}


def _hardware_bindings(prepared: PreparedRun, gate: GateCheck,
                       tool_modules: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    """构建冻结控制器所需的全部文件绑定。"""
    by_role: dict[str, dict[str, Any]] = {}
    for row in prepared.data["bindings"]:
        by_role.setdefault(row["role"], {})[row.get("relative_path", row["path"])] = row
    identity = prepared.data["artifact_identity"]
    root = Path(prepared.data["project_root"])
    build_id = prepared.data["source_build_run_id"]
    evidence = root / "report" / "evidence" / "S4-B" / build_id
    inventory = Path(prepared.data["source_evidence"]["external_inputs_inventory"]["path"])
    inventory_data, _ = read_json(inventory)
    external = {row["label"]: row for row in inventory_data["external_inputs"]}
    frozen_manifest_path = Path(prepared.data["source_evidence"]["frozen_2b_manifest"]["path"])
    frozen_manifest, _ = read_json(frozen_manifest_path)
    frozen_entries = _manifest_entries(frozen_manifest)
    w2b_root = exact_path(frozen_manifest_path.parents[4], directory=True)
    recovery_zip = Path(external["2B恢复输入ZIP"]["path"])
    xsa = Path(external["冻结XSA引用"]["path"])
    model = Path(external["冻结模型manifest"]["path"])
    bit_relative = "report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit"
    csr_relative = "src/s2b_control_csr.sv"
    interface_relative = "docs/obsidian-project/02-方案设计/s2b_board_transport.md"
    init = next(row for row in prepared.data["bindings"] if row["role"] == "verified_recovery_init_elf")
    tool_paths = tool_modules["paths"]
    tool_shas = tool_modules["sha256"]
    handoff = gate.records["hardware_session_handoff"]
    cold = gate.records["cold_basis"]
    sdk_binding = handoff["sdk_target_binding"]
    cold_binding = cold["evidence_binding"]

    def freeze(relative: str) -> dict[str, str]:
        row = frozen_entries[relative]
        actual = _relative_target(w2b_root, relative)
        require(sha256_file(actual) == row["sha256"], f"2B冻结文件在执行前发生变化：{relative}")
        return {"path": str(actual), "sha256": row["sha256"]}

    return {
        "init_elf": _binding(init["path"], identity["init_elf_sha256"]),
        "app_elf": _binding(evidence / "s4b_ps_tensor_diagnostic.elf", identity["elf_sha256"]),
        "xsa": _binding(xsa, identity["xsa_sha256"]),
        "bit": freeze(bit_relative),
        "model": _binding(model, identity["model_manifest_sha256"]),
        "SOURCE": _binding(evidence / "derived_source_sha256.json"),
        "TRACE_ABI": _binding(root / "vitis" / "stage4" / "ps" / "s4b_ps_trace.h"),
        "boot_seed": _binding(evidence / "run_config.json"),
        "session_range": _binding(evidence / "run_config.json"),
        "csr_source": freeze(csr_relative),
        "interface": freeze(interface_relative),
        "sdk_target": _binding(sdk_binding["path"], sdk_binding["sha256"]),
        "cold_basis": _binding(cold_binding["path"], cold_binding["sha256"]),
        "tool_source": _binding(tool_paths["verification/s2b_board_jtag.py"], tool_shas["verification/s2b_board_jtag.py"]),
        "elf_parser": _binding(tool_paths["verification/check_s2b_ps_smoke_layout.py"], tool_shas["verification/check_s2b_ps_smoke_layout.py"]),
        "delivery_parser": _binding(tool_paths["verification/check_stage_delivery.py"], tool_shas["verification/check_stage_delivery.py"]),
        "transport_source": _binding(tool_paths["verification/s2b_board_transport.py"], tool_shas["verification/s2b_board_transport.py"]),
        "recovery_zip": _binding(recovery_zip, external["2B恢复输入ZIP"]["sha256"]),
    }


def _write_event(log: BinaryIO, event: str, *, status: str = "RECORDED", **fields: Any) -> None:
    """向追加式事件证据写入一行并立即刷盘。"""
    row = {"time_utc8": datetime.now(TZ_UTC8).isoformat(), "event": event, "status": status, **fields}
    encoded = (json.dumps(row, ensure_ascii=False, default=str, sort_keys=True) + "\n").encode("utf-8")
    log.write(encoded)
    log.flush()
    os.fsync(log.fileno())


def _read_bound_run_inputs(weight_path: Path, tensor_path: Path,
                           tensor_binding_path: Path,
                           prepared: PreparedRun) -> tuple[bytes, bytes, dict[str, Any]]:
    """核验模型权重与INT8 CHW输入的实际长度、路径和SHA。"""
    weight = exact_path(weight_path).read_bytes()
    weight_sha = prepared.data["model_weights_input"]["sha256"]
    require(len(weight) == WEIGHT_BYTES and sha256_bytes(weight) == weight_sha,
            "OP_WEIGHTS文件长度或冻结模型SHA不匹配")
    require(weight[:8] == b"GFINT8W1", "OP_WEIGHTS文件magic不是冻结GF8格式")
    tensor_actual = exact_path(tensor_path)
    tensor = tensor_actual.read_bytes()
    require(len(tensor) == INPUT_BYTES, "OP_RUN输入必须恰好519168字节INT8_CHW_416")
    tensor_record, _ = read_json(tensor_binding_path)
    tensor_sha = sha256_bytes(tensor)
    require(tensor_record.get("status") == "PASS" and tensor_record.get("format") == "INT8_CHW_416" and
            tensor_record.get("path") == str(tensor_actual) and tensor_record.get("bytes") == INPUT_BYTES and
            tensor_record.get("sha256") == tensor_sha and
            tensor_record.get("model_manifest_sha256") == prepared.data["artifact_identity"]["model_manifest_sha256"],
            "输入张量绑定记录与实际路径/长度/SHA/model不一致")
    return weight, tensor, {"path": str(tensor_actual), "sha256": tensor_sha,
                            "bytes": len(tensor), "source_id": tensor_record.get("source_id"),
                            "format": "INT8_CHW_416"}


def execute_prepared(preparation: PreparedRun | Path, *, hardware_run_id: str,
                     gate_files: Mapping[str, Any] | None,
                     xsdb_session: Any, uart_stream: Any,
                     weight_path: Path, tensor_path: Path, tensor_binding_path: Path,
                     rx_record_path: Path, tx_header_record_path: Path,
                     frame_id: int, width: int, height: int, repeat: int,
                      core_timeout: int, drain_timeout: int,
                      completion_timeout_seconds: float = 5.0) -> dict[str, Any]:
    """以外部交接的session/stream执行受门禁保护的PS张量诊断。

    缺少任一真实门禁时在碰触session、stream、SDK或UART前返回BLOCKED；此函数不
    打开串口、不创建/关闭XSDB连接，不ACK、不reset、不重试，也不释放外部会话。
    """
    prepared = validate_preparation(preparation.path if isinstance(preparation, PreparedRun) else preparation)
    hardware_run_id = _validate_run_id(hardware_run_id)
    gates = validate_hardware_gates(prepared, hardware_run_id, gate_files)
    if not gates.allowed:
        return {
            "schema_version": 1,
            "status": "BLOCKED_BEFORE_HARDWARE",
            "hardware_run_id": hardware_run_id,
            "sdk_calls": 0,
            "uart_calls": 0,
            "missing_conditions": list(gates.missing),
            "hardware_execution": "NOT_RUN",
        }

    identity = prepared.data["artifact_identity"]
    auth = gates.records["operator_authorization"]
    evidence_dir = Path(prepared.data["project_root"]) / "tmp" / "4" / "S4-B-REAL-02B" / hardware_run_id
    parent = exact_path(evidence_dir.parent, directory=True)
    require(parent.name == "S4-B-REAL-02B", "硬件Run目录不在独占证据路径")
    require(hardware_run_id != prepared.data["run_id"], "硬件RunId不得覆盖离线prepare RunId")
    collision = [entry.name for entry in parent.iterdir() if entry.name.casefold() == hardware_run_id.casefold()]
    require(not collision, f"拒绝覆盖已存在硬件RunId：{hardware_run_id}")
    evidence_dir.mkdir()
    exact_path(evidence_dir, directory=True)
    events_path = evidence_dir / "adapter_hardware_events.jsonl"
    result_path = evidence_dir / "adapter_hardware_result.json"
    rx_path = Path(os.fspath(rx_record_path))
    tx_path = Path(os.fspath(tx_header_record_path))

    event_log: BinaryIO | None = None
    rx_file: BinaryIO | None = None
    tx_file: BinaryIO | None = None
    controller: Any = None
    wire: Any = None
    operation_count = {"sdk": 0, "uart": 0}
    result: dict[str, Any] = {
        "schema_version": 1,
        "status": "IN_PROGRESS",
        "task_id": "S4-B-REAL-02B",
        "hardware_run_id": hardware_run_id,
        "hardware_execution": "IN_PROGRESS",
        "artifact_identity": identity,
        "tensor_identity": None,
        "weight_sha256": None,
        "gate_record_sha256": gates.bindings,
        "operator_authorization_id": auth.get("authorization_id"),
        "safety_policy": {
            "session_created_or_closed": False,
            "serial_port_opened_or_closed": False,
            "ack_used": False,
            "retry_used": False,
            "automatic_release": False,
        },
    }
    try:
        event_log = events_path.open("xb")
        _write_event(event_log, "hardware_preflight", status="STARTED", gates="ALL_REQUIRED_RECORDS_VALID")
        require(auth.get("weight_sha256") == identity["model_weights_sha256"],
                "操作授权没有绑定冻结权重SHA")
        require(type(frame_id) is int and 0 <= frame_id <= 0xFFFFFFFF and
                type(width) is int and 1 <= width <= 65535 and
                type(height) is int and 1 <= height <= 65535 and
                type(repeat) is int and 1 <= repeat <= 1000 and frame_id + repeat - 1 <= 0xFFFFFFFF,
                "RUN frame/几何/repeat参数范围错误")
        require(type(core_timeout) is int and 0 < core_timeout <= 0xFFFFFFFF and
                type(drain_timeout) is int and 0 < drain_timeout <= 0xFFFFFFFF,
                "RUN core/drain timeout必须是非零u32")
        require(type(completion_timeout_seconds) in (int, float) and
                0 < completion_timeout_seconds <= 10,
                "RUN ACK/IDLE观察期限必须在(0,10]秒内")
        weight, tensor, tensor_identity = _read_bound_run_inputs(
            weight_path, tensor_path, tensor_binding_path, prepared)
        require(auth.get("tensor_sha256") == tensor_identity["sha256"],
                "操作授权没有绑定本次张量原字节SHA")
        result.update(tensor_identity=tensor_identity, weight_sha256=sha256_bytes(weight))
        require(rx_path.is_absolute() and tx_path.is_absolute() and
                not any(part in {".", ".."} for part in rx_path.parts + tx_path.parts),
                "UART原始记录路径必须是无别名绝对路径")
        require(os.fspath(rx_record_path) == str(evidence_dir / "uart_rx.raw.bin") and
                os.fspath(tx_header_record_path) == str(evidence_dir / "uart_tx_headers.raw.bin"),
                "UART记录文件路径必须与新RunId目录中的逐字符指定名称一致")
        require(rx_path.parent == evidence_dir and tx_path.parent == evidence_dir and
                rx_path.name == "uart_rx.raw.bin" and tx_path.name == "uart_tx_headers.raw.bin",
                "UART原始记录必须使用新Run目录中的固定文件名")
        rx_file = rx_path.open("xb")
        tx_file = tx_path.open("xb")
        _write_event(event_log, "hardware_preflight", status="PASS",
                     tensor_sha256=tensor_identity["sha256"], weight_sha256=sha256_bytes(weight))
        repo = _frozen_2b_git_root_from_manifest(
            prepared.data["source_evidence"]["frozen_2b_manifest"]["path"])
        tool_modules = _stage_verified_tool_modules(prepared, evidence_dir, repo)
        bindings = _hardware_bindings(prepared, gates, tool_modules)
        jtag_module = tool_modules["jtag_module"]
        require(callable(getattr(uart_stream, "read", None)) and callable(getattr(uart_stream, "write", None)),
                "必须显式传入已交接的双向UART stream")
        wire = jtag_module.JtagWireSession(uart_stream, rx_file, tx_file)
        require(type(wire) is jtag_module.JtagWireSession, "UART对象必须包装为冻结闭包的精确JtagWireSession类型")
        controller = jtag_module.JtagController(xsdb_session, bindings, evidence_dir=evidence_dir)
        _write_event(event_log, "verified_tool_import", status="PASS", modules=tool_modules["paths"])

        controller.select_and_gate()
        operation_count["sdk"] += len(controller.record.get("calls", []))
        _write_event(event_log, "initial_target_gate", status="PASS", targets=controller.record.get("targets"))
        controller.system_reset_stop(cold_basis=bindings["cold_basis"])
        operation_count["sdk"] = len(controller.record.get("calls", []))
        _write_event(event_log, "authorized_system_stop", status="PASS",
                     cold_lifecycle_proven=controller.record.get("cold_lifecycle_proven", False))
        controller.deploy()
        operation_count["sdk"] = len(controller.record.get("calls", []))
        require(controller.app_running and controller.state("cpu0") == "Running" and
                controller.state("cpu1").startswith("Stopped"), "完整部署后CPU状态不符合要求")
        operation_count["sdk"] = len(controller.record.get("calls", []))
        _write_event(event_log, "full_frozen_deploy", status="PASS", deployment=controller.record.get("deployment"))

        expected_banner = bytes.fromhex(prepared.data["ready_banner"]["hex"])
        banner_holder: dict[str, bytes] = {}
        def read_banner() -> dict[str, Any]:
            banner_holder["raw"] = _read_ready_banner(wire, expected_banner)
            return {"length": len(banner_holder["raw"]), "sha256": sha256_bytes(banner_holder["raw"]),
                    "text": banner_holder["raw"].decode("ascii")}
        require(wire.last_sequence == 0 and wire.epoch == 0 and not wire.sent_requests and
                wire.abort_pending is None and not wire.failed, "UART必须是本次新应用的未消费会话")
        controller.call("wire.ready_banner.complete_identity", read_banner)
        operation_count["sdk"] = len(controller.record.get("calls", []))
        operation_count["uart"] += 1
        _write_event(event_log, "ready_banner", status="PASS", raw_hex=banner_holder["raw"].hex(),
                     raw_sha256=sha256_bytes(banner_holder["raw"]))

        transport = tool_modules["transport_module"]
        weight_request, weight_header = transport.make_request(
            transport.OP_WEIGHTS, wire.last_sequence + 1, 0, weight)
        def send_weights() -> None:
            wire.send(weight_request, weight_header, weight,
                      {"kind": "frozen_model_weights", "sha256": sha256_bytes(weight),
                       "model_manifest_sha256": identity["model_manifest_sha256"]})
        controller.call("wire.OP_WEIGHTS.send", send_weights)
        operation_count["sdk"] = len(controller.record.get("calls", []))
        operation_count["uart"] += 1
        previous_epoch = wire.epoch
        weight_chunk_start = len(wire.rx_chunks)
        parsed_weight: dict[str, Any] = {}
        def receive_weights() -> dict[str, Any]:
            parsed_weight["value"] = wire.receive(weight_request, 0)
            return {"meta": parsed_weight["value"][0],
                    "head_lengths": {name: len(raw) for name, raw in parsed_weight["value"][1].items()},
                    "detection_count": len(parsed_weight["value"][2])}
        controller.call("wire.OP_WEIGHTS.receive_actual", receive_weights)
        operation_count["sdk"] = len(controller.record.get("calls", []))
        operation_count["uart"] += 1
        raw_weight_response = b"".join(wire.rx_chunks[weight_chunk_start:])
        require(len(raw_weight_response) >= transport.HEADER.size, "OP_WEIGHTS响应原始字节截断")
        _write_bytes_new(evidence_dir / "weights_response.raw.bin", raw_weight_response)
        weight_meta, weight_heads, weight_detections = transport.decode_response(
            raw_weight_response[:transport.HEADER.size], raw_weight_response[transport.HEADER.size:],
            weight_request, 0, previous_epoch)
        require(parsed_weight.get("value") == (weight_meta, weight_heads, weight_detections) and
                not weight_heads and not weight_detections,
                "冻结UART OP_WEIGHTS解析与响应原始字节再次解码不一致")
        _write_event(event_log, "OP_WEIGHTS", status="PASS", sequence=weight_request.sequence,
                     raw_response_sha256=sha256_bytes(raw_weight_response), meta=weight_meta)

        ranges = prepared.data["memory_ranges"]
        header_range = ranges["trace_header"]
        record_range = ranges["trace_records"]
        require(header_range["size_bytes"] == TRACE_HEADER_BYTES and
                record_range["size_bytes"] == TRACE_RECORDS_BYTES and
                record_range["end_exclusive"] == header_range["start"],
                "准备内存映射与双区完整快照约束不符")
        initial_header_1 = words_le(controller.words(header_range["start"], TRACE_HEADER_BYTES // 4))
        initial_header_2 = words_le(controller.words(header_range["start"], TRACE_HEADER_BYTES // 4))
        require(initial_header_1 == initial_header_2,
                "OP_RUN前trace header仍变化；不猜测旧日志是否属于本次RUN")
        _validate_empty_trace_header(initial_header_1, identity)
        _write_bytes_new(evidence_dir / "trace_header_before_run.bin", initial_header_1)

        core_drain = struct.pack("<II", core_timeout, drain_timeout)
        run_payload = core_drain + tensor
        require(len(run_payload) == INPUT_BYTES + 8, "OP_RUN负载长度必须是timeout双u32+519168B张量")
        run_request, run_header = transport.make_request(
            transport.OP_RUN, wire.last_sequence + 1, frame_id, run_payload,
            width=width, height=height, repeat=repeat)
        def send_run() -> None:
            wire.send(run_request, run_header, run_payload,
                      {"kind": "s4b_ps_tensor_run", "tensor_sha256": tensor_identity["sha256"],
                       "format": "INT8_CHW_416", "model_manifest_sha256": identity["model_manifest_sha256"],
                       "timeout_u32": [core_timeout, drain_timeout]})
        controller.call("wire.OP_RUN.send", send_run)
        operation_count["sdk"] = len(controller.record.get("calls", []))
        operation_count["uart"] += 1
        run_rows: list[dict[str, Any]] = []
        for index in range(repeat):
            chunk_start = len(wire.rx_chunks)
            prior_epoch = wire.epoch
            parsed_holder: dict[str, Any] = {}
            def receive_one() -> dict[str, Any]:
                parsed_holder["parsed"] = wire.receive(run_request, index)
                meta = parsed_holder["parsed"][0]
                return {"meta": meta, "head_lengths": {name: len(raw) for name, raw in parsed_holder["parsed"][1].items()},
                        "detection_count": len(parsed_holder["parsed"][2])}
            controller.call(f"wire.OP_RUN.receive_actual.{index}", receive_one)
            operation_count["sdk"] = len(controller.record.get("calls", []))
            operation_count["uart"] += 1
            raw_response = b"".join(wire.rx_chunks[chunk_start:])
            require(len(raw_response) >= transport.HEADER.size, "OP_RUN响应原始字节截断")
            verified = transport.decode_response(
                raw_response[:transport.HEADER.size], raw_response[transport.HEADER.size:],
                run_request, index, prior_epoch)
            parsed = parsed_holder["parsed"]
            require(parsed == verified, "冻结decode_response与UART实际原字节解析结果不同")
            _write_bytes_new(evidence_dir / f"run_response_{index:04d}.raw.bin", raw_response)
            for head_name, head_raw in parsed[1].items():
                _write_bytes_new(evidence_dir / f"{head_name}_{index:04d}.raw.bin", head_raw)
            row = {"index": index, "frame": frame_id + index, "sequence": run_request.sequence,
                   "epoch": verified[0]["epoch"], "response_code": verified[0]["response_code"],
                   "meta": verified[0], "input_crc32": zlib_crc32(tensor),
                   "input_bytes": len(tensor), "input_format": "INT8_CHW_416",
                   "raw_response_sha256": sha256_bytes(raw_response),
                   "heads": {name: {"bytes": len(raw), "sha256": sha256_bytes(raw)} for name, raw in parsed[1].items()},
                   "detection_count": len(parsed[2])}
            run_rows.append(row)
            _write_event(event_log, "OP_RUN_response", status="PASS", **row)

        require(wire.abort_pending is None and not wire.failed and len(run_rows) == repeat,
                "UART会话进入abort或failed状态，停止后续操作")
        last = run_rows[-1]
        _write_json_new(evidence_dir / "uart_run_receipts.json", {
            "schema_version": 1, "hardware_run_id": hardware_run_id,
            "transport_sequence": run_request.sequence, "frame_id": frame_id,
            "repeat": repeat, "input_crc32": zlib_crc32(tensor),
            "input_bytes": len(tensor), "input_format": "INT8_CHW_416",
            "raw_response_files": [f"run_response_{index:04d}.raw.bin" for index in range(repeat)],
            "receipts": run_rows,
        })
        csr_before, completion_header = _wait_for_safe_idle(
            controller, identity, uart_sequence=run_request.sequence,
            frame_id=frame_id, repeat=repeat, expected_epoch=last["epoch"],
            header_address=header_range["start"], timeout_seconds=completion_timeout_seconds,
            poll_interval_seconds=0.05)
        _write_bytes_new(evidence_dir / "trace_header_after_RUN_complete.bin", completion_header)
        _write_event(event_log, "run_ack_returned_to_stable_idle", status="PASS",
                     csr_snapshot=csr_before, trace_header_sha256=sha256_bytes(completion_header),
                     observation_timeout_seconds=completion_timeout_seconds)
        before_header_1 = words_le(controller.words(header_range["start"], TRACE_HEADER_BYTES // 4))
        before_header_2 = words_le(controller.words(header_range["start"], TRACE_HEADER_BYTES // 4))
        require(before_header_1 == before_header_2 == completion_header,
                "安全IDLE观察后到CPU0 stop前trace header变化")
        _validate_trace_header(before_header_1, identity["derived_source_sha256"], identity["boot_seed"],
                               identity["session_first"], identity["session_last"])
        require(controller.state("cpu1").startswith("Stopped") and controller.state("cpu0") == "Running",
                "安全点CPU状态不符，不停止任何核")
        controller.gate(both=False)
        csr_immediately_before_stop = controller.stable_csr("immediately_before_cpu0_stop")
        require(csr_immediately_before_stop == csr_before,
                "安全IDLE后到CPU0 stop前完整CSR发生变化；不停止CPU0")
        controller.call("cpu0.stop.after_safe_point", controller.targets["cpu0"].stop)
        operation_count["sdk"] = len(controller.record.get("calls", []))
        controller.gate()
        require(controller.state("cpu0").startswith("Stopped") and controller.state("cpu1").startswith("Stopped"),
                "本次CPU0 stop后没有确认CPU0/CPU1均停止")
        csr_after_stop = controller.stable_csr("after_owned_cpu0_stop")
        require(csr_after_stop == csr_before, "停止本次CPU0前后CSR状态变化，拒绝trace导出")
        _write_event(event_log, "stop_owned_cpu0", status="PASS", csr_snapshot=csr_after_stop,
                     immediately_before_stop=csr_immediately_before_stop)

        snapshots: list[tuple[bytes, bytes]] = []
        for pass_index in (1, 2):
            header_raw = words_le(controller.words(header_range["start"], TRACE_HEADER_BYTES // 4))
            _write_bytes_new(evidence_dir / f"trace_header_read_{pass_index}.bin", header_raw)
            record_raw = words_le(controller.words(record_range["start"], TRACE_RECORDS_BYTES // 4))
            _write_bytes_new(evidence_dir / f"trace_records_read_{pass_index}.bin", record_raw)
            snapshots.append((header_raw, record_raw))
            _write_event(event_log, "trace_region_read", status="RECORDED", pass_index=pass_index,
                         header_sha256=sha256_bytes(header_raw), records_sha256=sha256_bytes(record_raw),
                         header_bytes=len(header_raw), record_bytes=len(record_raw))
        csr_after_reads = controller.stable_csr("after_full_double_read")
        require(csr_after_reads == csr_after_stop, "双读期间CSR发生变化，拒绝打包")
        trace_uart_join = _validate_trace_uart_join(
            snapshots[0][0], snapshots[0][1], run_rows,
            identity=identity, uart_sequence=run_request.sequence,
            frame_id=frame_id, repeat=repeat, input_crc32=zlib_crc32(tensor))
        _write_json_new(evidence_dir / "trace_uart_join.json", trace_uart_join)
        dump = pack_double_snapshot(snapshots[0][0], snapshots[0][1], snapshots[1][0], snapshots[1][1],
                                    expected_source_sha256=identity["derived_source_sha256"],
                                    expected_boot_seed=identity["boot_seed"],
                                    expected_session_first=identity["session_first"],
                                    expected_session_last=identity["session_last"])
        dump_path = evidence_dir / "trace_double_read.bin"
        _write_bytes_new(dump_path, dump)
        decoder_path = Path(prepared.data["source_evidence"]["decoder_cli"]["path"])
        require(sha256_file(exact_path(decoder_path)) == prepared.data["source_evidence"]["decoder_cli"]["sha256"],
                "双读后当前decoder CLI相对prepare发生变化")
        decoder_output = evidence_dir / "trace_decoded.json"
        decoder_command = [sys.executable, "-B", str(decoder_path), str(dump_path),
                           "--expected-source-sha256", identity["derived_source_sha256"],
                           "--expected-boot-seed", hex(identity["boot_seed"]),
                           "--output", str(decoder_output)]
        decode_process = subprocess.run(decoder_command, check=False, capture_output=True,
                                        text=True, encoding="utf-8", errors="replace")
        _write_bytes_new(evidence_dir / "decoder.stdout.txt", decode_process.stdout.encode("utf-8"))
        _write_bytes_new(evidence_dir / "decoder.stderr.txt", decode_process.stderr.encode("utf-8"))
        _write_event(event_log, "decode_double_read_snapshot", status="PASS" if decode_process.returncode == 0 else "FAIL",
                     command=decoder_command, exit_code=decode_process.returncode)
        require(decode_process.returncode == 0, f"冻结trace decoder失败 exit={decode_process.returncode}")
        decoded, _ = read_json(decoder_output)
        require(decoded.get("status") == "PASS_DECODED_DOUBLE_READ_SNAPSHOT" and
                decoded.get("header", {}).get("derived_source_sha256") == identity["derived_source_sha256"] and
                decoded.get("header", {}).get("boot_seed") == identity["boot_seed"],
                "trace decoder结果状态或SOURCE/seed身份不符")
        result.update(status="ACTUAL_PS_TENSOR_DIAGNOSTIC_CAPTURED", hardware_execution="EXECUTED_WITH_EXPLICIT_GATES",
                      ready_banner_sha256=prepared.data["ready_banner"]["sha256"],
                      uart_receipts=run_rows, trace_dump={"path": str(dump_path), "sha256": sha256_bytes(dump),
                                                          "bytes": len(dump), "decoder_status": decoded["status"],
                                                          "record_count": decoded["record_count"]},
                       trace_uart_join=trace_uart_join,
                      run_active_zero=True, cpu0_stopped_after_safe_point=True,
                      cpu1_stopped=True, sdk_call_count=len(controller.record.get("calls", [])),
                      uart_read_write_operations=operation_count["uart"],
                      complete_stage4_or_RGB_preprocess="NOT_CLAIMED",
                      limitation="PS INT8 CHW张量诊断不证明RGB预处理、raw/PL新架构或阶段4 G5。")
        _write_event(event_log, "adapter_complete", status="PASS", trace_dump_sha256=sha256_bytes(dump))
        return result
    except BaseException as error:
        if wire is not None:
            try:
                wire.failed = True
            except BaseException:
                pass
        result.update(status="FAILED", hardware_execution="FAILED_OR_INCOMPLETE",
                      error_type=type(error).__name__, error=str(error), traceback=traceback.format_exc(),
                      sdk_call_count=len(controller.record.get("calls", [])) if controller is not None else 0,
                      uart_read_write_operations=operation_count["uart"],
                      fail_state="NOT_ASSUMED_SAFE", automatic_recovery="NONE")
        if event_log is not None:
            try:
                _write_event(event_log, "adapter_failure", status="FAILED", error_type=type(error).__name__, error=str(error))
            except BaseException:
                pass
        raise
    finally:
        if wire is not None and wire.receipt_attempts:
            try:
                _write_json_new(evidence_dir / "uart_receipt_attempts.json", wire.receipt_attempts)
            except BaseException:
                pass
        if controller is not None:
            try:
                if not controller.log.closed:
                    if controller.owned_bps:
                        controller.log.flush()
                        controller.log.close()
                    else:
                        controller.close()
            except BaseException:
                try:
                    if not controller.log.closed:
                        controller.log.flush()
                        controller.log.close()
                except BaseException:
                    pass
        if rx_file is not None:
            try:
                rx_file.flush()
                os.fsync(rx_file.fileno())
                rx_file.close()
            except BaseException:
                pass
        if tx_file is not None:
            try:
                tx_file.flush()
                os.fsync(tx_file.fileno())
                tx_file.close()
            except BaseException:
                pass
        if event_log is not None:
            try:
                event_log.flush()
                os.fsync(event_log.fileno())
                event_log.close()
            except BaseException:
                pass
        if not result_path.exists():
            try:
                _write_json_new(result_path, result)
            except BaseException:
                pass


def words_le(words: Sequence[int]) -> bytes:
    """将SDK返回的u32列表编码为原始小端字节。"""
    require(type(words) in (list, tuple) and all(type(word) is int and 0 <= word <= 0xFFFFFFFF for word in words),
            "SDK内存读回必须是u32序列")
    return struct.pack("<" + "I" * len(words), *words)


def main(argv: Sequence[str] | None = None) -> int:
    """执行只读离线准备或重新验证；不提供硬件命令行入口。"""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare", help="离线绑定所选编译产物与冻结2B工具来源")
    prepare.add_argument("--project-root", type=Path, default=Path(__file__).absolute().parents[2])
    prepare.add_argument("--source-run-id", default=DEFAULT_BUILD_RUN_ID)
    prepare.add_argument("--run-id", required=True)
    validate = commands.add_parser("validate", help="重算离线prepare清单中的文件SHA")
    validate.add_argument("preparation", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            output = prepare_adapter(args.project_root, args.source_run_id, args.run_id)
            record = validate_preparation(output)
            print(json.dumps({"status": record.data["status"], "preparation": str(output),
                              "hardware_execution": "NOT_RUN"}, ensure_ascii=False))
            return 0
        record = validate_preparation(args.preparation)
        print(json.dumps({"status": record.data["status"], "preparation": str(record.path),
                          "hardware_execution": "NOT_RUN"}, ensure_ascii=False))
        return 0
    except (AdapterError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(json.dumps({"status": "FAIL", "error_type": type(error).__name__, "error": str(error)},
                         ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
