#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核验并恢复 GestureForge 清理归档中的独立工作树。"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Callable, Iterable


CHUNK_SIZE = 1024 * 1024
REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
ARCHIVE_BOUNDARY = Path(r"D:\GestureForge_Archive\2026-11-01")
HEX_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
HEX_OID = re.compile(r"^[0-9a-fA-F]+$")
SCOPE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class RestoreError(Exception):
    """表示归档输入或恢复操作不符合契约。"""


@dataclass(frozen=True)
class PayloadRef:
    """指向一个归档存储对象及其预期内容身份。"""

    label: str
    storage: dict
    byte_count: int
    sha256: str
    expected_oid: str | None = None


@dataclass
class ValidatedScope:
    """完成结构与路径核验后的阶段清单。"""

    manifest_path: Path
    manifest: dict
    files: list[dict]
    directories: list[str]
    links: list[dict]
    excluded: list
    git_repositories: list[dict]
    raw_git_roots: list[str]
    raw_git_note: str | None


def _json_output(payload: dict, stream: BinaryIO | None = None) -> None:
    """以 UTF-8 输出单行 JSON。"""

    text = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if stream is None:
        print(text)
    else:
        stream.write((text + "\n").encode("utf-8"))
        stream.flush()


def _is_reparse(st: os.stat_result) -> bool:
    return bool(getattr(st, "st_file_attributes", 0) & REPARSE_POINT)


def _plain_absolute_path(raw: str, label: str) -> Path:
    """要求命令行绝对路径不含父目录跳转。"""

    path = Path(raw)
    if not path.is_absolute():
        raise RestoreError(f"{label} 必须是绝对路径：{raw!r}")
    if ".." in path.parts:
        raise RestoreError(f"{label} 不得包含 '..' 路径段：{raw!r}")
    return path


def _check_no_reparse(path: Path, *, require_exists: bool) -> None:
    """逐段拒绝符号链接、junction 和其他 reparse point。"""

    absolute = Path(os.path.abspath(str(path)))
    current = Path(absolute.anchor)
    parts = absolute.parts[1:]
    for index, part in enumerate(parts):
        current = current / part
        try:
            st = current.lstat()
        except FileNotFoundError:
            if require_exists:
                raise RestoreError(f"路径不存在：{current}")
            # 缺失路径的后续段也不可能已有 reparse point。
            return
        except OSError as exc:
            raise RestoreError(f"无法核验路径组件 {current}: {exc}") from exc
        if stat.S_ISLNK(st.st_mode) or _is_reparse(st):
            raise RestoreError(f"禁止经过符号链接或 junction：{current}")
        if index < len(parts) - 1 and not stat.S_ISDIR(st.st_mode):
            raise RestoreError(f"路径父组件不是目录：{current}")


def _require_plain_directory(path: Path, label: str) -> None:
    _check_no_reparse(path, require_exists=True)
    try:
        if not path.is_dir():
            raise RestoreError(f"{label} 不是目录：{path}")
    except OSError as exc:
        raise RestoreError(f"无法读取 {label}：{path}: {exc}") from exc


def _safe_relative(raw: object, label: str, *, allow_empty: bool = False) -> PurePosixPath | None:
    """核验归档内相对路径，拒绝绝对路径、跳转和平台分隔符。"""

    if not isinstance(raw, str):
        raise RestoreError(f"{label} 必须是字符串")
    if raw == "" and allow_empty:
        return None
    if not raw or "\x00" in raw or "\\" in raw or ":" in raw:
        raise RestoreError(f"{label} 不是安全的正斜杠相对路径：{raw!r}")
    if raw.startswith("/"):
        raise RestoreError(f"{label} 不得是绝对路径：{raw!r}")
    parts = raw.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise RestoreError(f"{label} 含空段、'.' 或 '..'：{raw!r}")
    return PurePosixPath(*parts)


def _archive_member(archive_root: Path, relative: str, label: str) -> Path:
    """解析归档成员并拒绝路径逃逸及 reparse 组件。"""

    safe = _safe_relative(relative, label)
    assert safe is not None
    candidate = archive_root.joinpath(*safe.parts)
    _check_no_reparse(candidate, require_exists=True)
    try:
        resolved_root = archive_root.resolve(strict=True)
        resolved_candidate = candidate.resolve(strict=True)
        resolved_candidate.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise RestoreError(f"{label} 越出归档目录或无法解析：{candidate}") from exc
    return candidate


def _read_json(path: Path, label: str) -> dict:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RestoreError(f"无法读取 {label}：{path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RestoreError(f"{label} 顶层必须是 JSON 对象：{path}")
    return value


def _nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise RestoreError(f"{label} 必须是非负整数")
    return value


def _sha256(value: object, label: str) -> str:
    if not isinstance(value, str) or not HEX_SHA256.fullmatch(value):
        raise RestoreError(f"{label} 必须是 64 位十六进制 SHA-256")
    return value.lower()


def _oid(value: object, label: str) -> str:
    if not isinstance(value, str) or not HEX_OID.fullmatch(value):
        raise RestoreError(f"{label} 必须是十六进制 Git object id")
    if len(value) not in (40, 64):
        raise RestoreError(f"{label} 的长度不是 SHA-1/SHA-256 object id：{value!r}")
    return value.lower()


def _validate_storage(value: object, label: str) -> dict:
    if not isinstance(value, dict):
        raise RestoreError(f"{label}.storage 必须是对象")
    kind = value.get("kind")
    if kind == "git_blob":
        return {"kind": kind, "oid": _oid(value.get("oid"), f"{label}.storage.oid")}
    if kind == "gzip":
        path = value.get("path")
        _safe_relative(path, f"{label}.storage.path")
        return {"kind": kind, "path": path}
    raise RestoreError(f"{label}.storage.kind 仅支持 git_blob 或 gzip")


def _validate_payload(value: object, label: str, *, require_oid: bool) -> PayloadRef:
    if not isinstance(value, dict):
        raise RestoreError(f"{label} 必须是对象")
    byte_count = _nonnegative_int(value.get("bytes"), f"{label}.bytes")
    digest = _sha256(value.get("sha256"), f"{label}.sha256")
    storage = _validate_storage(value.get("storage"), label)
    expected_oid = _oid(value.get("oid"), f"{label}.oid") if require_oid else None
    return PayloadRef(label, storage, byte_count, digest, expected_oid)


def _git_metadata_path(raw: object, label: str) -> str:
    safe = _safe_relative(raw, label, allow_empty=True)
    return "" if safe is None else safe.as_posix()


def _load_scope(archive_root: Path, scope_id: str) -> tuple[dict, ValidatedScope]:
    if not SCOPE_ID.fullmatch(scope_id):
        raise RestoreError(f"非法 scope id：{scope_id!r}")
    archive_root = archive_root.absolute()
    _require_plain_directory(archive_root, "archive")
    root_archive_path = archive_root / "archive.json"
    _check_no_reparse(root_archive_path, require_exists=True)
    archive_doc = _read_json(root_archive_path, "root archive.json")

    manifest_path = archive_root / "scopes" / scope_id / "manifest.json"
    _check_no_reparse(manifest_path, require_exists=True)
    manifest_doc = _read_json(manifest_path, "scope manifest")
    if manifest_doc.get("schema") != "gestureforge.cleanup_scope.v2":
        raise RestoreError("scope manifest schema 必须是 gestureforge.cleanup_scope.v2")
    if manifest_doc.get("id") != scope_id:
        raise RestoreError("scope manifest.id 与 --scope 不一致")
    if not isinstance(manifest_doc.get("original_root"), str):
        raise RestoreError("scope manifest 缺少字符串 original_root")

    raw_files = manifest_doc.get("files")
    raw_dirs = manifest_doc.get("directories")
    raw_links = manifest_doc.get("links")
    raw_excluded = manifest_doc.get("excluded")
    raw_git = manifest_doc.get("git_repositories")
    raw_git_roots = manifest_doc.get("raw_git_roots", [])
    if not isinstance(raw_files, list) or not isinstance(raw_dirs, list):
        raise RestoreError("scope manifest.files 和 directories 必须是数组")
    if not isinstance(raw_links, list) or not isinstance(raw_excluded, list):
        raise RestoreError("scope manifest.links 和 excluded 必须是数组")
    if not isinstance(raw_git, list):
        raise RestoreError("scope manifest.git_repositories 必须是数组")
    if not isinstance(raw_git_roots, list):
        raise RestoreError("scope manifest.raw_git_roots 必须是数组")

    files: list[dict] = []
    seen_paths: dict[str, tuple[str, str]] = {}
    for index, raw in enumerate(raw_files):
        label = f"files[{index}]"
        if not isinstance(raw, dict):
            raise RestoreError(f"{label} 必须是对象")
        safe = _safe_relative(raw.get("path"), f"{label}.path")
        assert safe is not None
        path = safe.as_posix()
        key = path.casefold()
        if key in seen_paths:
            raise RestoreError(f"Windows 路径大小写冲突：{seen_paths[key]!r} 与 {path!r}")
        seen_paths[key] = (path, "file")
        _nonnegative_int(raw.get("bytes"), f"{label}.bytes")
        _sha256(raw.get("sha256"), f"{label}.sha256")
        mtime_ns = raw.get("mtime_ns")
        if isinstance(mtime_ns, bool) or not isinstance(mtime_ns, int):
            raise RestoreError(f"{label}.mtime_ns 必须是整数")
        mode = raw.get("mode")
        if isinstance(mode, bool) or not isinstance(mode, (int, str)):
            raise RestoreError(f"{label}.mode 必须是整数或数字字符串")
        if isinstance(mode, int) and mode < 0:
            raise RestoreError(f"{label}.mode 不得为负数")
        _validate_storage(raw.get("storage"), label)
        files.append(raw)

    directories: list[str] = []
    for index, raw in enumerate(raw_dirs):
        safe = _safe_relative(raw, f"directories[{index}]", allow_empty=True)
        path = "" if safe is None else safe.as_posix()
        if path:
            key = path.casefold()
            if key in seen_paths:
                raise RestoreError(f"文件与目录路径冲突：{seen_paths[key]!r} 与 {path!r}")
            seen_paths[key] = (path, "directory")
        directories.append(path)

    links: list[dict] = []
    for index, raw in enumerate(raw_links):
        label = f"links[{index}]"
        if not isinstance(raw, dict):
            raise RestoreError(f"{label} 必须是对象")
        safe = _safe_relative(raw.get("path"), f"{label}.path")
        assert safe is not None
        path = safe.as_posix()
        key = path.casefold()
        if key in seen_paths:
            raise RestoreError(f"链接与文件/目录路径冲突：{seen_paths[key]!r} 与 {path!r}")
        seen_paths[key] = (path, "link")
        if not isinstance(raw.get("target"), str):
            raise RestoreError(f"{label}.target 必须是字符串")
        if raw.get("kind") not in ("junction", "symlink"):
            raise RestoreError(f"{label}.kind 仅支持 junction 或 symlink")
        if not isinstance(raw.get("is_directory"), bool):
            raise RestoreError(f"{label}.is_directory 必须是布尔值")
        links.append(raw)

    for path_text, _path_kind in seen_paths.values():
        parts = path_text.split("/")
        for end in range(1, len(parts)):
            parent_key = "/".join(parts[:end]).casefold()
            parent = seen_paths.get(parent_key)
            if parent is not None and parent[1] != "directory":
                raise RestoreError(
                    f"非目录路径 {parent[0]!r} 不能包含子路径 {path_text!r}"
                )

    git_repositories: list[dict] = []
    git_paths: set[str] = set()
    top_count = 0
    for index, raw in enumerate(raw_git):
        label = f"git_repositories[{index}]"
        if not isinstance(raw, dict):
            raise RestoreError(f"{label} 必须是对象")
        repo_path = _git_metadata_path(raw.get("path"), f"{label}.path")
        repo_key = repo_path.casefold()
        if repo_key in git_paths:
            raise RestoreError(f"重复 Git repository path：{repo_path!r}")
        git_paths.add(repo_key)
        if repo_path == "":
            top_count += 1
        branch = raw.get("branch")
        if branch is not None and not isinstance(branch, str):
            raise RestoreError(f"{label}.branch 必须是字符串或 null")
        refs = raw.get("refs", {})
        if not isinstance(refs, dict):
            raise RestoreError(f"{label}.refs 必须是对象")
        for ref_name, ref_oid in refs.items():
            if not isinstance(ref_name, str):
                raise RestoreError(f"{label}.refs 的键必须是字符串")
            _oid(ref_oid, f"{label}.refs[{ref_name!r}]")
        raw_head = raw.get("head")
        if raw_head is None:
            if repo_path == "" or refs:
                raise RestoreError(f"{label}.head 为空时仅允许无引用的嵌套空仓库")
            head = None
        else:
            head = _oid(raw_head, f"{label}.head")
        bundle = raw.get("bundle")
        if bundle is not None:
            if not isinstance(bundle, str):
                raise RestoreError(f"{label}.bundle 必须是字符串或 null")
            _safe_bundle_relative(bundle, f"{label}.bundle")
        index_record = raw.get("index")
        if index_record is not None:
            if not isinstance(index_record, dict):
                raise RestoreError(f"{label}.index 必须是对象或 null")
            _safe_relative(index_record.get("path"), f"{label}.index.path")
            _sha256(index_record.get("sha256"), f"{label}.index.sha256")
        staged_objects = raw.get("staged_objects", [])
        if not isinstance(staged_objects, list):
            raise RestoreError(f"{label}.staged_objects 必须是数组")
        for object_index, obj in enumerate(staged_objects):
            _validate_payload(obj, f"{label}.staged_objects[{object_index}]", require_oid=True)
        git_repositories.append(raw)
    if top_count > 1:
        raise RestoreError("git_repositories 中只能有一个 path='' 的顶层仓库")

    normalized_raw_roots: list[str] = []
    raw_root_keys: set[str] = set()
    for index, raw in enumerate(raw_git_roots):
        safe = _safe_relative(raw, f"raw_git_roots[{index}]")
        assert safe is not None
        path = safe.as_posix()
        key = path.casefold()
        if key in raw_root_keys:
            raise RestoreError(f"重复 raw_git_roots 路径：{path!r}")
        if key in git_paths:
            raise RestoreError(f"路径不能同时作为真实Git仓库和 raw_git_root：{path!r}")
        if seen_paths.get(key, (None, None))[1] != "directory":
            raise RestoreError(f"raw_git_roots 必须指向清单内目录：{path!r}")
        raw_root_keys.add(key)
        normalized_raw_roots.append(path)
    raw_git_note = manifest_doc.get("raw_git_note")
    if normalized_raw_roots:
        if not isinstance(raw_git_note, str) or not raw_git_note.strip():
            raise RestoreError("存在 raw_git_roots 时必须提供非空 raw_git_note")
    elif raw_git_note is not None and not isinstance(raw_git_note, str):
        raise RestoreError("raw_git_note 必须是字符串或 null")

    return archive_doc, ValidatedScope(
        manifest_path=manifest_path,
        manifest=manifest_doc,
        files=files,
        directories=directories,
        links=links,
        excluded=raw_excluded,
        git_repositories=git_repositories,
        raw_git_roots=normalized_raw_roots,
        raw_git_note=raw_git_note,
    )


def _safe_bundle_relative(raw: str, label: str) -> str:
    """核验允许包含 '..'、但最终必须留在固定档案根目录的 bundle 路径。"""

    if not raw or "\x00" in raw or "\\" in raw or ":" in raw or raw.startswith("/"):
        raise RestoreError(f"{label} 必须是正斜杠相对路径：{raw!r}")
    if Path(raw).is_absolute():
        raise RestoreError(f"{label} 不得是绝对路径：{raw!r}")
    if any(part in ("", ".") for part in raw.split("/")):
        raise RestoreError(f"{label} 含空路径段或 '.'：{raw!r}")
    return raw


def _resolve_bundle(archive_root: Path, repo_record: dict, archive_doc: dict) -> Path | None:
    raw = repo_record.get("bundle")
    if raw is None:
        raw = archive_doc.get("base_git_bundle")
    if raw is None:
        return None
    if isinstance(raw, dict):
        raw = raw.get("path")
    if not isinstance(raw, str):
        raise RestoreError("base_git_bundle/bundle 必须是相对路径字符串或 null")
    _safe_bundle_relative(raw, "base_git_bundle")
    bundle = archive_root / Path(*raw.split("/"))
    try:
        boundary = ARCHIVE_BOUNDARY.resolve(strict=False)
        resolved = bundle.resolve(strict=True)
        resolved.relative_to(boundary)
    except (OSError, ValueError) as exc:
        raise RestoreError(
            f"Git bundle 必须存在且解析后留在 {ARCHIVE_BOUNDARY} 内：{bundle}"
        ) from exc
    _check_no_reparse(bundle, require_exists=True)
    if not bundle.is_file():
        raise RestoreError(f"Git bundle 不是普通文件：{bundle}")
    return bundle


def _git(repo: Path, *args: str, input_bytes: bytes | None = None) -> subprocess.CompletedProcess:
    command = ["git", "-C", str(repo), *args]
    try:
        result = subprocess.run(
            command,
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise RestoreError(f"无法运行 Git：{exc}") from exc
    return result


def _require_git_repo(repo: Path) -> str:
    _require_plain_directory(repo, "repo")
    top = _git(repo, "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        raise RestoreError(f"--repo 不是 Git 工作树：{top.stderr.decode('utf-8', 'replace').strip()}")
    object_format = _git(repo, "rev-parse", "--show-object-format")
    if object_format.returncode != 0:
        raise RestoreError("无法读取 Git object format")
    fmt = object_format.stdout.decode("ascii", "strict").strip()
    if fmt not in ("sha1", "sha256"):
        raise RestoreError(f"不支持的 Git object format：{fmt!r}")
    return fmt


def _storage_key(storage: dict) -> tuple[str, str]:
    if storage["kind"] == "git_blob":
        return ("git_blob", storage["oid"].lower())
    return ("gzip", storage["path"])


def _file_payload_refs(scope: ValidatedScope) -> list[PayloadRef]:
    refs: list[PayloadRef] = []
    for raw in scope.files:
        refs.append(
            PayloadRef(
                label=f"file:{raw['path']}",
                storage=_validate_storage(raw["storage"], f"file:{raw['path']}"),
                byte_count=raw["bytes"],
                sha256=raw["sha256"].lower(),
            )
        )
    return refs


class CatFileBatch:
    """通过单个常驻 `git cat-file --batch` 进程读取多个 blob。"""

    def __init__(self, repo: Path):
        try:
            self.process = subprocess.Popen(
                ["git", "-C", str(repo), "cat-file", "--batch"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0,
            )
        except OSError as exc:
            raise RestoreError(f"无法启动 Git cat-file --batch：{exc}") from exc

    @staticmethod
    def _read_exact(stream: BinaryIO, length: int) -> bytes:
        chunks = bytearray()
        while len(chunks) < length:
            block = stream.read(min(CHUNK_SIZE, length - len(chunks)))
            if not block:
                raise RestoreError("git cat-file --batch 在 blob 内容中途结束")
            chunks.extend(block)
        return bytes(chunks)

    def stream(self, oid: str, consume: Callable[[bytes], None]) -> tuple[int, str]:
        assert self.process.stdin is not None and self.process.stdout is not None
        try:
            self.process.stdin.write(oid.encode("ascii") + b"\n")
            self.process.stdin.flush()
            header = self.process.stdout.readline(256)
        except (OSError, BrokenPipeError) as exc:
            raise RestoreError(f"Git cat-file 通信失败：{exc}") from exc
        parts = header.rstrip(b"\n").split(b" ")
        if len(parts) == 2 and parts[1] == b"missing":
            raise RestoreError(f"Git blob 缺失：{oid}")
        if len(parts) != 3:
            raise RestoreError(f"git cat-file 返回无效头：{header[:200]!r}")
        returned_oid, object_type, raw_size = parts
        if returned_oid.decode("ascii", "replace").lower() != oid.lower():
            raise RestoreError(f"git cat-file 返回了意外 object id：{returned_oid!r}")
        if object_type != b"blob":
            raise RestoreError(f"归档文件引用的 Git 对象不是 blob：{oid} ({object_type!r})")
        try:
            size = int(raw_size)
        except ValueError as exc:
            raise RestoreError(f"Git blob 大小无效：{raw_size!r}") from exc
        remaining = size
        digest = hashlib.sha256()
        while remaining:
            block = self._read_exact(self.process.stdout, min(CHUNK_SIZE, remaining))
            consume(block)
            digest.update(block)
            remaining -= len(block)
        delimiter = self.process.stdout.read(1)
        if delimiter != b"\n":
            raise RestoreError(f"git cat-file blob 后缺少分隔换行：{oid}")
        return size, digest.hexdigest()

    def close(self) -> None:
        process = self.process
        if process.stdin is not None:
            try:
                process.stdin.close()
            except OSError:
                pass
        if process.stdout is not None:
            try:
                process.stdout.close()
            except OSError:
                pass
        stderr = b""
        if process.stderr is not None:
            try:
                stderr = process.stderr.read()
                process.stderr.close()
            except OSError:
                pass
        try:
            code = process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            raise RestoreError("git cat-file --batch 未能正常退出")
        if code != 0:
            detail = stderr.decode("utf-8", "replace").strip()
            raise RestoreError(f"git cat-file --batch 退出码 {code}: {detail}")

    def __enter__(self) -> "CatFileBatch":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def _stream_storage(
    storage: dict,
    archive_root: Path,
    cat_file: CatFileBatch | None,
    consume: Callable[[bytes], None],
    *,
    expected_gzip_bytes: int | None = None,
    git_hash_algo: str | None = None,
) -> tuple[int, str, str | None]:
    """分块读取 Git blob 或 gzip 对象，并计算内容与可选 Git blob 身份。"""

    sha = hashlib.sha256()
    git_hash = hashlib.new(git_hash_algo) if git_hash_algo else None
    total = 0

    def feed(block: bytes) -> None:
        nonlocal total
        consume(block)
        sha.update(block)
        if git_hash is not None:
            git_hash.update(block)
        total += len(block)

    if storage["kind"] == "git_blob":
        if cat_file is None:
            raise RestoreError("归档引用 Git blob，但没有可用的 cat-file 会话")
        oid = storage["oid"]
        def collect(block: bytes) -> None:
            feed(block)

        size, digest = cat_file.stream(oid, collect)
        return size, digest, oid

    relative = storage["path"]
    source = _archive_member(archive_root, relative, "gzip storage")
    if git_hash is not None:
        if expected_gzip_bytes is None:
            raise RestoreError("gzip staged object 缺少预期字节数")
        git_hash.update(f"blob {expected_gzip_bytes}\0".encode("ascii"))
    try:
        with gzip.open(source, "rb") as handle:
            while True:
                block = handle.read(CHUNK_SIZE)
                if not block:
                    break
                feed(block)
    except (OSError, EOFError, gzip.BadGzipFile) as exc:
        raise RestoreError(f"gzip 存储对象无法解压：{source}: {exc}") from exc
    git_oid = git_hash.hexdigest() if git_hash is not None else None
    return total, sha.hexdigest(), git_oid


def _payload_storage_groups(refs: Iterable[PayloadRef]) -> dict[tuple[str, str], list[PayloadRef]]:
    groups: dict[tuple[str, str], list[PayloadRef]] = {}
    for ref in refs:
        groups.setdefault(_storage_key(ref.storage), []).append(ref)
    return groups


def _verify_refs(
    refs: list[PayloadRef], archive_root: Path, repo: Path, object_format: str
) -> tuple[int, int, int]:
    groups = _payload_storage_groups(refs)
    git_groups = [key for key in groups if key[0] == "git_blob"]
    checked_refs = 0
    with CatFileBatch(repo) if git_groups else _NullContext(None) as cat_file:
        for key, group in groups.items():
            representative = group[0]
            expected_oid_ref = next((ref for ref in group if ref.expected_oid is not None), None)
            compute_oid = expected_oid_ref is not None
            actual_bytes, actual_sha, actual_oid = _stream_storage(
                representative.storage,
                archive_root,
                cat_file,
                lambda _block: None,
                expected_gzip_bytes=(representative.byte_count if compute_oid else None),
                git_hash_algo=(
                    object_format
                    if compute_oid and representative.storage["kind"] == "gzip"
                    else None
                ),
            )
            for ref in group:
                if actual_bytes != ref.byte_count:
                    raise RestoreError(
                        f"payload 字节数不符：{ref.label}，预期 {ref.byte_count}，实际 {actual_bytes}"
                    )
                if actual_sha != ref.sha256.lower():
                    raise RestoreError(f"payload SHA-256 不符：{ref.label}")
                if ref.expected_oid is not None:
                    if actual_oid != ref.expected_oid:
                        raise RestoreError(f"staged object Git oid 不符：{ref.label}")
                checked_refs += 1
    return len(groups), checked_refs, len(git_groups)


class _NullContext:
    """为不含 Git blob 的归档提供统一上下文接口。"""

    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self.value

    def __exit__(self, exc_type, exc, traceback):
        return None


def _all_payload_refs(scope: ValidatedScope) -> list[PayloadRef]:
    refs = _file_payload_refs(scope)
    for repo_index, repo_record in enumerate(scope.git_repositories):
        for object_index, obj in enumerate(repo_record.get("staged_objects", [])):
            refs.append(
                _validate_payload(
                    obj,
                    f"git_repositories[{repo_index}].staged_objects[{object_index}]",
                    require_oid=True,
                )
            )
    return refs


def _verify_indexes(scope: ValidatedScope, archive_root: Path) -> int:
    count = 0
    for repo_record in scope.git_repositories:
        index_record = repo_record.get("index")
        if index_record is None:
            continue
        path = _archive_member(archive_root, index_record["path"], "git index")
        digest = hashlib.sha256()
        total = 0
        try:
            with path.open("rb") as handle:
                while block := handle.read(CHUNK_SIZE):
                    digest.update(block)
                    total += len(block)
        except OSError as exc:
            raise RestoreError(f"无法读取归档 Git index：{path}: {exc}") from exc
        if digest.hexdigest() != index_record["sha256"].lower():
            raise RestoreError(f"归档 Git index SHA-256 不符：{path}")
        count += 1
    return count


def _git_root_record(scope: ValidatedScope) -> dict | None:
    for repo_record in scope.git_repositories:
        if repo_record.get("path") == "":
            return repo_record
    return None


def _git_head_available(repo: Path, head: str) -> bool:
    result = _git(repo, "cat-file", "-e", f"{head}^{{commit}}")
    return result.returncode == 0


def _import_bundle_if_needed(
    repo: Path, head: str, repo_record: dict, archive_doc: dict, archive_root: Path
) -> str | None:
    if _git_head_available(repo, head):
        return None
    bundle = _resolve_bundle(archive_root, repo_record, archive_doc)
    if bundle is None:
        raise RestoreError(f"--repo 中找不到归档 HEAD，且没有 base_git_bundle：{head}")
    result = _git(repo, "bundle", "unbundle", str(bundle))
    if result.returncode != 0 or not _git_head_available(repo, head):
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise RestoreError(f"Git bundle 导入后仍无法找到 HEAD {head}: {detail}")
    return str(bundle)


def _ensure_target_parent(target: Path) -> None:
    _check_no_reparse(target.parent, require_exists=True)
    if not target.parent.is_dir():
        raise RestoreError(f"target 父目录不是目录：{target.parent}")
    if target.exists() or target.is_symlink():
        raise RestoreError(f"target 必须不存在，拒绝覆盖：{target}")


def _target_member(target: Path, relative: str, label: str) -> Path:
    safe = _safe_relative(relative, label)
    assert safe is not None
    destination = target.joinpath(*safe.parts)
    _check_no_reparse(destination.parent, require_exists=False)
    return destination


def _make_directory_chain(
    target: Path, relative: str, created_directories: set[str] | None = None
) -> Path:
    if not relative:
        return target
    safe = _safe_relative(relative, "directory path")
    assert safe is not None
    current = target
    for part in safe.parts:
        current = current / part
        try:
            st = current.lstat()
        except FileNotFoundError:
            current.mkdir()
            if created_directories is not None:
                created_directories.add(current.relative_to(target).as_posix().casefold())
            continue
        if stat.S_ISLNK(st.st_mode) or _is_reparse(st):
            raise RestoreError(f"target 父路径包含符号链接或 junction：{current}")
        if not stat.S_ISDIR(st.st_mode):
            raise RestoreError(f"target 路径组件已是非目录：{current}")
    return current


def _parse_mode(value: int | str) -> int:
    if isinstance(value, int):
        return stat.S_IMODE(value)
    if re.fullmatch(r"[0-7]{3,7}", value):
        return int(value, 8) & 0o777
    try:
        return stat.S_IMODE(int(value, 0))
    except ValueError as exc:
        raise RestoreError(f"无法解析文件 mode：{value!r}") from exc


def _restore_file(
    raw: dict,
    target: Path,
    archive_root: Path,
    cat_file: CatFileBatch | None,
    created_directories: set[str],
    *,
    allow_replace: bool = False,
) -> int:
    relative = raw["path"]
    destination = _target_member(target, relative, "file path")
    parent_rel = "/".join(PurePosixPath(relative).parts[:-1])
    _make_directory_chain(target, parent_rel, created_directories)
    _check_no_reparse(destination.parent, require_exists=True)
    existing = False
    try:
        existing_stat = destination.lstat()
    except FileNotFoundError:
        existing_stat = None
    if existing_stat is not None:
        if stat.S_ISLNK(existing_stat.st_mode) or _is_reparse(existing_stat):
            raise RestoreError(f"target 文件是链接或 reparse point：{destination}")
        if not allow_replace or not stat.S_ISREG(existing_stat.st_mode):
            raise RestoreError(f"target 文件已存在，拒绝覆盖：{destination}")
        existing = True
    digest = hashlib.sha256()
    total = 0
    try:
        temporary = destination.with_name(destination.name + ".restore-tmp") if existing else destination
        if temporary != destination and temporary.exists():
            raise RestoreError(f"恢复临时文件已存在：{temporary}")
        with temporary.open("xb") as output:
            def consume(block: bytes) -> None:
                nonlocal total
                output.write(block)
                digest.update(block)
                total += len(block)

            storage = _validate_storage(raw["storage"], f"file:{relative}")
            actual_bytes, actual_sha, _ = _stream_storage(
                storage,
                archive_root,
                cat_file,
                consume,
            )
            output.flush()
            os.fsync(output.fileno())
        if existing:
            os.replace(temporary, destination)
    except OSError as exc:
        raise RestoreError(f"写入恢复文件失败：{destination}: {exc}") from exc
    if total != raw["bytes"] or actual_bytes != raw["bytes"]:
        raise RestoreError(
            f"恢复文件字节数不符：{relative}，预期 {raw['bytes']}，写入 {total}，存储 {actual_bytes}"
        )
    actual_sha256 = digest.hexdigest()
    if actual_sha256 != raw["sha256"].lower() or actual_sha != raw["sha256"].lower():
        raise RestoreError(f"恢复文件 SHA-256 不符：{relative}")
    try:
        os.chmod(destination, _parse_mode(raw["mode"]))
        os.utime(destination, ns=(raw["mtime_ns"], raw["mtime_ns"]))
    except (OSError, ValueError) as exc:
        raise RestoreError(f"恢复文件元数据失败：{destination}: {exc}") from exc
    return total


def _prepare_worktree(
    repo: Path,
    root_record: dict,
    target: Path,
    archive_doc: dict,
    archive_root: Path,
    *,
    checkout_head: bool,
) -> tuple[str | None, str]:
    head = _oid(root_record.get("head"), "顶层 Git head")
    imported_bundle = _import_bundle_if_needed(repo, head, root_record, archive_doc, archive_root)
    lock = _git(repo, "rev-parse", "--git-path", "index.lock")
    if lock.returncode == 0:
        lock_path = Path(lock.stdout.decode("utf-8", "replace").strip())
        if not lock_path.is_absolute():
            lock_path = repo / lock_path
        if lock_path.exists():
            raise RestoreError(f"repo 存在 index.lock，拒绝创建 worktree：{lock_path}")
    arguments = [
        "-c",
        "core.hooksPath=NUL",
        "worktree",
        "add",
        "--detach",
    ]
    if not checkout_head:
        arguments.append("--no-checkout")
    arguments.extend((str(target), head))
    result = _git(repo, *arguments)
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise RestoreError(f"git worktree add 失败：{detail}")
    git_dir = _git(target, "rev-parse", "--git-dir")
    if git_dir.returncode != 0:
        raise RestoreError("新 worktree 创建后无法解析 git-dir")
    return imported_bundle, git_dir.stdout.decode("utf-8", "replace").strip()


def _deleted_worktree_paths(repo_record: dict, archive_root: Path) -> list[str]:
    """从原始 NUL 状态记录提取暂存或未暂存删除项。"""

    record = repo_record.get("status")
    if not isinstance(record, dict):
        raise RestoreError("partial Git 恢复缺少 status -z 控制记录")
    source = _archive_member(archive_root, record.get("path"), "git status")
    expected = _sha256(record.get("sha256"), "git status.sha256")
    try:
        raw = source.read_bytes()
    except OSError as exc:
        raise RestoreError(f"无法读取归档 Git status：{source}: {exc}") from exc
    if hashlib.sha256(raw).hexdigest() != expected:
        raise RestoreError(f"归档 Git status SHA-256 不符：{source}")

    paths: list[str] = []
    records = raw.split(b"\0")
    for entry in records:
        if not entry:
            continue
        if len(entry) < 4 or entry[2:3] != b" ":
            raise RestoreError("归档 Git status -z 格式异常")
        status = entry[:2]
        if b"D" not in status:
            continue
        try:
            path = entry[3:].decode("utf-8", "strict")
        except UnicodeDecodeError as exc:
            raise RestoreError("删除路径不是 UTF-8，拒绝猜测并删除") from exc
        safe = _safe_relative(path, "deleted Git path")
        assert safe is not None
        paths.append(safe.as_posix())
    return sorted(set(paths), key=str.casefold)


def _remove_restored_deletions(target: Path, deleted_paths: list[str]) -> int:
    """重放原工作区的 Git 删除状态，不沿链接遍历。"""

    removed = 0
    for relative in deleted_paths:
        destination = _target_member(target, relative, "deleted Git path")
        if not destination.exists() and not destination.is_symlink():
            continue
        _check_no_reparse(destination.parent, require_exists=True)
        try:
            info = destination.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or _is_reparse(info) or not stat.S_ISREG(info.st_mode):
            raise RestoreError(f"Git 删除目标不是普通文件，拒绝处理：{destination}")
        destination.unlink()
        removed += 1
    return removed


def _import_staged_objects(repo: Path, target: Path, repo_record: dict, object_format: str, archive_root: Path) -> int:
    objects = repo_record.get("staged_objects", [])
    if not objects:
        return 0
    with tempfile.TemporaryDirectory(prefix=".cleanup-archive-stage-", dir=target) as staging_name:
        staging = Path(staging_name)
        temp_paths: list[Path] = []
        expected_oids: list[str] = []
        has_git_blobs = any(
            item.get("storage", {}).get("kind") == "git_blob" for item in objects
        )
        with CatFileBatch(repo) if has_git_blobs else _NullContext(None) as cat_file:
            for index, raw in enumerate(objects):
                ref = _validate_payload(raw, f"staged_objects[{index}]", require_oid=True)
                oid = ref.expected_oid
                assert oid is not None
                path = staging / f"{index:08d}.blob"
                sha = hashlib.sha256()
                git_hash = hashlib.new(object_format)
                git_hash.update(f"blob {ref.byte_count}\0".encode("ascii"))
                total = 0
                try:
                    with path.open("xb") as output:
                        def consume(block: bytes) -> None:
                            nonlocal total
                            output.write(block)
                            sha.update(block)
                            git_hash.update(block)
                            total += len(block)

                        actual_bytes, actual_sha, _ = _stream_storage(
                            ref.storage,
                            archive_root,
                            cat_file,
                            consume,
                        )
                        output.flush()
                        os.fsync(output.fileno())
                except OSError as exc:
                    raise RestoreError(f"暂存 staged object 失败：{path}: {exc}") from exc
                if total != ref.byte_count or actual_bytes != ref.byte_count:
                    raise RestoreError(f"staged object 字节数不符：{ref.label}")
                if sha.hexdigest() != ref.sha256.lower() or actual_sha != ref.sha256.lower():
                    raise RestoreError(f"staged object SHA-256 不符：{ref.label}")
                if git_hash.hexdigest() != oid:
                    raise RestoreError(f"staged object Git oid 不符：{ref.label}")
                temp_paths.append(path)
                expected_oids.append(oid)
        if not temp_paths:
            return 0
        input_paths = b"".join(os.fsencode(path) + b"\n" for path in temp_paths)
        result = _git(repo, "hash-object", "-w", "--stdin-paths", input_bytes=input_paths)
        if result.returncode != 0:
            detail = result.stderr.decode("utf-8", "replace").strip()
            raise RestoreError(f"写入 staged Git objects 失败：{detail}")
        actual_oids = result.stdout.decode("ascii", "replace").splitlines()
        if len(actual_oids) != len(expected_oids):
            raise RestoreError("git hash-object 返回的 staged object 数量不符")
        for actual, expected in zip(actual_oids, expected_oids):
            if actual.lower() != expected:
                raise RestoreError(f"staged object 写入后 oid 不符：预期 {expected}，实际 {actual}")
        return len(set(expected_oids))


def _restore_index(target: Path, repo_record: dict, archive_root: Path) -> bool:
    index_record = repo_record.get("index")
    if index_record is None:
        return False
    source = _archive_member(archive_root, index_record["path"], "git index")
    try:
        raw = source.read_bytes()
    except OSError as exc:
        raise RestoreError(f"无法读取归档 Git index：{source}: {exc}") from exc
    if hashlib.sha256(raw).hexdigest() != index_record["sha256"].lower():
        raise RestoreError(f"归档 Git index SHA-256 不符：{source}")
    result = _git(target, "rev-parse", "--git-path", "index")
    if result.returncode != 0:
        raise RestoreError("无法取得新 worktree 的实际 Git index 路径")
    index_path = Path(result.stdout.decode("utf-8", "replace").strip())
    if not index_path.is_absolute():
        index_path = target / index_path
    lock_path = index_path.with_name(index_path.name + ".lock")
    _check_no_reparse(index_path.parent, require_exists=True)
    if lock_path.exists():
        raise RestoreError(f"新 worktree 存在 index.lock：{lock_path}")
    temporary = index_path.with_name(index_path.name + ".restore-tmp")
    if temporary.exists():
        raise RestoreError(f"Git index 临时路径已存在：{temporary}")
    try:
        with temporary.open("xb") as output:
            output.write(raw)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, index_path)
    except OSError as exc:
        raise RestoreError(f"写入新 worktree Git index 失败：{index_path}: {exc}") from exc
    return True


def _git_metadata_roots(scope: ValidatedScope) -> tuple[list[str], list[str]]:
    """按清单声明的真实 Git 根和原样 Git 根生成精确的元数据路径。"""

    actual = []
    for record in scope.git_repositories:
        root = record.get("path", "")
        actual.append(f"{root}/.git" if root else ".git")
    raw = [f"{root}/.git" for root in scope.raw_git_roots]
    return actual, raw


def _metadata_root_for(relative: str, roots: list[str]) -> str | None:
    """仅匹配真实元数据根自身及其后代，不把普通伪 .git 当元数据。"""

    for root in roots:
        relative_key = relative.casefold()
        root_key = root.casefold()
        if relative_key == root_key or relative_key.startswith(root_key + "/"):
            return root
    return None


def _raw_git_metadata_paths(scope: ValidatedScope) -> list[str]:
    """返回归档中确实存在、但默认不重建的 raw Git 元数据根。"""

    candidates = [f"{root}/.git" for root in scope.raw_git_roots]
    recorded = [item["path"] for item in scope.files]
    recorded.extend(scope.directories)
    recorded.extend(item["path"] for item in scope.links)
    return [
        root
        for root in candidates
        if any(
            path.casefold() == root.casefold()
            or path.casefold().startswith(root.casefold() + "/")
            for path in recorded
        )
    ]


def _read_payload_prefix(
    raw: dict, archive_root: Path, repo: Path, *, limit: int = 4096
) -> bytes:
    """只收集文件前缀，同时消费并验证整个存储流。"""

    prefix = bytearray()

    def collect(block: bytes) -> None:
        remaining = limit - len(prefix)
        if remaining > 0:
            prefix.extend(block[:remaining])

    storage = _validate_storage(raw["storage"], f"file:{raw['path']}")
    with CatFileBatch(repo) if storage["kind"] == "git_blob" else _NullContext(None) as cat:
        length, digest, _ = _stream_storage(storage, archive_root, cat, collect)
    if length != raw["bytes"] or digest != raw["sha256"].lower():
        raise RestoreError(f"伪 .git 内容与清单身份不符：{raw['path']}")
    return bytes(prefix)


def _reject_gitdir_pointers(
    scope: ValidatedScope, archive_root: Path, repo: Path
) -> None:
    """在写入目标前拒绝会把嵌套 Git 指向外部目录的伪 .git 指针。"""

    actual_roots, raw_roots = _git_metadata_roots(scope)
    recognized = actual_roots + raw_roots
    for raw in scope.files:
        relative = raw["path"]
        if _metadata_root_for(relative, recognized) is not None:
            continue
        parts = PurePosixPath(relative).parts
        is_gitdir_file = parts[-1].casefold() == ".git"
        is_pointer_record = len(parts) >= 2 and parts[-2].casefold() == ".git" and parts[-1].casefold() in {
            "gitdir",
            "commondir",
        }
        if not (is_gitdir_file or is_pointer_record):
            continue
        prefix = _read_payload_prefix(raw, archive_root, repo)
        first_line = prefix.splitlines()[0].strip() if prefix.splitlines() else b""
        if is_gitdir_file:
            normalized = first_line.lstrip(b"\xef\xbb\xbf \t").lower()
            if normalized.startswith(b"gitdir:"):
                raise RestoreError(
                    f"伪 .git 文件含 gitdir 外部指针，拒绝恢复以免关联其他仓库：{relative}"
                )
        elif prefix.strip():
            raise RestoreError(
                f"伪 .git/{parts[-1]} 文件含仓库路径指针，拒绝恢复：{relative}"
            )


def _verify_mode(archive_root: Path, scope: ValidatedScope, repo: Path, object_format: str) -> dict:
    refs = _all_payload_refs(scope)
    storage_count, checked_refs, git_storage_count = _verify_refs(refs, archive_root, repo, object_format)
    index_count = _verify_indexes(scope, archive_root)
    return {
        "status": "PAYLOADS_VERIFIED",
        "scope_id": scope.manifest["id"],
        "files_metadata_verified": len(scope.files),
        "unique_storages_verified": storage_count,
        "payload_references_verified": checked_refs,
        "git_blob_storages_verified": git_storage_count,
        "indexes_verified": index_count,
        "directories_recorded": len(scope.directories),
        "links_not_restored": len(scope.links),
        "excluded_records": len(scope.excluded),
        "nested_git_metadata_saved": sum(1 for item in scope.git_repositories if item.get("path", "") != ""),
        "semantic_acceptance": False,
        "note": "仅核验归档 payload 与元数据绑定，不代表工程语义、测试或验收通过。",
    }


def _restore_mode(
    archive_doc: dict,
    archive_root: Path,
    scope: ValidatedScope,
    repo: Path,
    object_format: str,
    target: Path,
    with_git: bool,
) -> dict:
    target = _plain_absolute_path(str(target), "target")
    _verify_indexes(scope, archive_root)
    _ensure_target_parent(target)
    root_record = _git_root_record(scope) if with_git else None
    if with_git and root_record is None:
        raise RestoreError("--with-git 要求 manifest 存在 path='' 的顶层 Git 记录")
    _reject_gitdir_pointers(scope, archive_root, repo)
    deleted_paths = []
    partial_git_tree = bool(with_git and not scope.manifest.get("complete_tree", True))
    if partial_git_tree:
        deleted_paths = _deleted_worktree_paths(root_record, archive_root)

    imported_bundle = None
    git_dir = None
    if with_git:
        imported_bundle, git_dir = _prepare_worktree(
            repo,
            root_record,
            target,
            archive_doc,
            archive_root,
            checkout_head=partial_git_tree,
        )
        if not target.is_dir():
            raise RestoreError("git worktree add 未创建 target 目录")
        _check_no_reparse(target, require_exists=True)
    else:
        target.mkdir()
        _check_no_reparse(target, require_exists=True)

    skipped_git_paths = 0
    skipped_raw_git_paths = 0
    files_restored = 0
    bytes_restored = 0
    created_directories: set[str] = set()
    actual_metadata_roots, raw_metadata_roots = _git_metadata_roots(scope)
    metadata_roots = actual_metadata_roots + raw_metadata_roots
    git_files = [
        item
        for item in scope.files
        if item["storage"]["kind"] == "git_blob"
        and _metadata_root_for(item["path"], metadata_roots) is None
    ]
    with CatFileBatch(repo) if git_files else _NullContext(None) as cat_file:
        for raw in scope.directories:
            metadata_root = _metadata_root_for(raw, metadata_roots)
            if metadata_root is not None:
                if metadata_root in raw_metadata_roots:
                    skipped_raw_git_paths += 1
                else:
                    skipped_git_paths += 1
                continue
            _make_directory_chain(target, raw, created_directories)
        for raw in scope.files:
            metadata_root = _metadata_root_for(raw["path"], metadata_roots)
            if metadata_root is not None:
                if metadata_root in raw_metadata_roots:
                    skipped_raw_git_paths += 1
                else:
                    skipped_git_paths += 1
                continue
            bytes_restored += _restore_file(
                raw,
                target,
                archive_root,
                cat_file,
                created_directories,
                allow_replace=partial_git_tree,
            )
            files_restored += 1

    deletions_restored = _remove_restored_deletions(target, deleted_paths)
    staged_imported = 0
    index_restored = False
    if with_git:
        staged_imported = _import_staged_objects(repo, target, root_record, object_format, archive_root)
        index_restored = _restore_index(target, root_record, archive_root)

    nested_records = sum(1 for item in scope.git_repositories if item.get("path", "") != "")
    raw_metadata_not_restored = _raw_git_metadata_paths(scope)
    return {
        "status": "RESTORE_COMPLETE",
        "scope_id": scope.manifest["id"],
        "target": str(target),
        "files_restored": files_restored,
        "bytes_restored": bytes_restored,
        "directories_created": len(created_directories),
        "git_metadata_paths_skipped": skipped_git_paths,
        "raw_git_metadata_paths_skipped": skipped_raw_git_paths,
        "raw_git_metadata_not_restored": raw_metadata_not_restored,
        "raw_git_note": scope.raw_git_note,
        "pseudo_git_entries_restored": [
            path
            for path in [item["path"] for item in scope.files] + scope.directories
            if any(part.casefold() == ".git" for part in PurePosixPath(path).parts)
            and _metadata_root_for(path, metadata_roots) is None
        ],
        "links_not_restored": [
            {"path": link["path"], "target": link["target"], "kind": link["kind"], "is_directory": link["is_directory"]}
            for link in scope.links
        ],
        "nested_git_metadata_saved": nested_records,
        "nested_git_metadata_restored": 0,
        "nested_git_note": "嵌套仓库源码已恢复；未自动重建 Git 元数据。若清单提供 nested bundle，可另行导入；本结果不代表嵌套 clone 完整恢复。",
        "git_worktree_created": bool(with_git),
        "git_dir": git_dir,
        "original_branch_recorded": root_record.get("branch") if with_git else None,
        "restored_branch": None,
        "staged_objects_imported": staged_imported,
        "index_restored": index_restored,
        "deleted_paths_restored": deletions_restored,
        "base_git_bundle_imported": imported_bundle,
        "semantic_acceptance": False,
        "note": "文件内容与清单身份在恢复时逐项核验；未执行构建、硬件操作或语义验收。",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="核验或恢复 GestureForge 清理归档；不会覆盖已有 target。"
    )
    parser.add_argument("--archive", required=True, help="含 archive.json 与 scopes/ 的归档根绝对路径")
    parser.add_argument("--scope", required=True, help="scope id")
    parser.add_argument("--repo", required=True, help="持有归档 Git blob 对象的 Git 工作树绝对路径")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--verify", action="store_true", help="只读核验所有唯一 payload 与索引")
    mode.add_argument("--restore", action="store_true", help="恢复文件到一个全新 target 目录")
    parser.add_argument("--target", help="--restore 的新目录绝对路径")
    parser.add_argument("--with-git", action="store_true", help="创建 detached worktree 并恢复 Git index 和暂存对象")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        archive_root = _plain_absolute_path(args.archive, "archive")
        repo = _plain_absolute_path(args.repo, "repo")
        if args.restore and not args.target:
            raise RestoreError("--restore 必须同时提供 --target")
        if not args.restore and (args.target is not None or args.with_git):
            raise RestoreError("--target 和 --with-git 只能与 --restore 一起使用")
        target = _plain_absolute_path(args.target, "target") if args.target else None
        archive_doc, scope = _load_scope(archive_root, args.scope)
        object_format = _require_git_repo(repo)
        if args.verify:
            _json_output(_verify_mode(archive_root, scope, repo, object_format))
            return 0
        assert target is not None
        _json_output(
            _restore_mode(
                archive_doc,
                archive_root,
                scope,
                repo,
                object_format,
                target,
                args.with_git,
            )
        )
        return 0
    except RestoreError as exc:
        payload = {"status": "ERROR", "error": str(exc)}
        if args.restore and args.target:
            payload["target"] = args.target
            payload["target_may_be_partial"] = Path(args.target).exists()
        _json_output(payload, stream=sys.stderr.buffer)
        return 2
    except OSError as exc:
        payload = {"status": "ERROR", "error": f"文件系统错误：{exc}"}
        if args.restore and args.target:
            payload["target"] = args.target
            payload["target_may_be_partial"] = Path(args.target).exists()
        _json_output(payload, stream=sys.stderr.buffer)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
