#!/usr/bin/env python3
"""从冻结 CPU checkpoint 安全恢复缺失的 T25 shard 目录。"""

from __future__ import annotations

import argparse
import ctypes
import errno
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import types
import zlib
from pathlib import Path
from typing import Any, Callable


BASELINE_COMMIT = "62414cecaf08ddbb82fe3da59eef16ee5e1ecd89"
INDEX_RELATIVE_PATH = "report/evidence/S2A-T25/cpu_layer_golden_index.json"
T25_DIRECTORY_RELATIVE_PATH = "report/evidence/S2A-T25"
TENSOR_DIRECTORY_NAME = "tensors"
GENERATOR_RELATIVE_PATH = "verification/s2a_cpu_layer_goldens.py"
EXPECTED_SAMPLE_COUNT = 109
EXPECTED_LAYER_COUNT = 38
EXPECTED_RAW_BYTES = 11_382_150


class RestoreError(RuntimeError):
    """表示 T25 shard 恢复前置条件、摘要或发布步骤失败。"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RestoreError(message)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _has_reparse_point(path: Path) -> bool:
    """识别符号链接及 Windows junction 等重解析点。"""
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    if stat.S_ISLNK(info.st_mode):
        return True
    attributes = getattr(info, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse_flag)


def _lexists(path: Path) -> bool:
    return os.path.lexists(os.fspath(path))


def _require_plain_directory(path: Path, field: str) -> None:
    _require(_lexists(path), f"{field} 不存在: {path}")
    _require(not _has_reparse_point(path), f"{field} 是符号链接或重解析点: {path}")
    _require(path.is_dir(), f"{field} 不是目录: {path}")


def _require_plain_file(path: Path, field: str) -> None:
    _require(_lexists(path), f"{field} 不存在: {path}")
    _require(not _has_reparse_point(path), f"{field} 是符号链接或重解析点: {path}")
    _require(path.is_file(), f"{field} 不是普通文件: {path}")


def _run_git(root: Path, *arguments: str) -> bytes:
    """以固定仓库根目录执行只读 Git 查询。"""
    try:
        result = subprocess.run(
            ["git", "-C", os.fspath(root), *arguments],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as exc:
        raise RestoreError(f"无法运行 Git: {exc}") from exc
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RestoreError(f"Git 查询失败（{arguments[0]}，退出码 {result.returncode}）: {detail}")
    return result.stdout


def _check_repository_root(root: Path, baseline_commit: str) -> Path:
    """确认给定目录是仓库根目录，且当前提交基于指定冻结基线。"""
    try:
        canonical = root.resolve(strict=True)
    except OSError as exc:
        raise RestoreError(f"仓库根目录无法解析: {root}") from exc
    _require_plain_directory(canonical, "仓库根目录")
    top_text = _run_git(canonical, "rev-parse", "--show-toplevel").decode("utf-8").strip()
    try:
        top = Path(top_text).resolve(strict=True)
    except OSError as exc:
        raise RestoreError("Git 返回的仓库根目录无法解析") from exc
    _require(top == canonical, "--repo-root 必须精确指向 Git 仓库根目录")
    _run_git(canonical, "cat-file", "-e", f"{baseline_commit}^{{commit}}")
    _run_git(canonical, "merge-base", "--is-ancestor", baseline_commit, "HEAD")
    return canonical


def _read_frozen_index(root: Path, baseline_commit: str) -> tuple[dict[str, Any], bytes, str]:
    """只接受基线提交所跟踪且工作树字节完全一致的完整索引。"""
    repo_path = Path(INDEX_RELATIVE_PATH)
    t25_dir = root / T25_DIRECTORY_RELATIVE_PATH
    _require_plain_directory(root / "report", "report 目录")
    _require_plain_directory(root / "report" / "evidence", "evidence 目录")
    _require_plain_directory(t25_dir, "T25 目录")
    index_path = root / repo_path
    _require_plain_file(index_path, "T25 checkpoint 索引")

    tracked = _run_git(root, "ls-files", "--error-unmatch", "--", INDEX_RELATIVE_PATH)
    _require(tracked.decode("utf-8").strip() == INDEX_RELATIVE_PATH, "T25 checkpoint 索引没有按预期路径纳入 Git")
    baseline_blob = _run_git(root, "rev-parse", f"{baseline_commit}:{INDEX_RELATIVE_PATH}").decode("ascii").strip()
    head_blob = _run_git(root, "rev-parse", f"HEAD:{INDEX_RELATIVE_PATH}").decode("ascii").strip()
    _require(baseline_blob == head_blob, "HEAD 中的 T25 checkpoint 索引与冻结基线不一致")
    baseline_bytes = _run_git(root, "show", f"{baseline_commit}:{INDEX_RELATIVE_PATH}")
    try:
        working_bytes = index_path.read_bytes()
    except OSError as exc:
        raise RestoreError(f"读取 T25 checkpoint 索引失败: {exc}") from exc
    _require(working_bytes == baseline_bytes, "工作树 T25 checkpoint 索引与冻结 Git 基线不一致")
    try:
        index = json.loads(working_bytes.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise RestoreError("冻结 T25 checkpoint 索引不是有效 UTF-8 JSON") from exc
    _require(isinstance(index, dict), "冻结 T25 checkpoint 索引根节点必须为 object")
    return index, working_bytes, _sha256(working_bytes)


def _check_frozen_index_shape(index: dict[str, Any]) -> list[dict[str, Any]]:
    """核对完成状态、样本顺序、逐层范围及 shard 摘要字段。"""
    _require(index.get("schema_version") == "gestureforge_s2a_cpu_layer_golden_index_v2", "T25 索引 schema 不匹配")
    _require(index.get("task_id") == "S2A-T25" and index.get("model_id") == "tiny416", "T25 索引身份不匹配")
    _require(index.get("status") == "COMPLETE", "T25 checkpoint 尚未 COMPLETE")
    _require(index.get("stage_acceptance") == {"G4": "NOT_MET", "G5": "NOT_MET"}, "T25 索引不得宣称 G4/G5 已通过")
    catalog = index.get("fixed_sample_catalog")
    _require(isinstance(catalog, dict), "T25 固定样本目录字段缺失")
    _require(catalog.get("path") == "report/evidence/S2A-T01/fixed_test_samples.json", "T25 固定样本清单路径不匹配")
    _require(catalog.get("total_samples") == EXPECTED_SAMPLE_COUNT, "T25 固定样本总数不为 109")
    _require(catalog.get("completed_samples") == EXPECTED_SAMPLE_COUNT, "T25 checkpoint 不是 109/109")
    _require(catalog.get("remaining_samples") == 0, "T25 checkpoint 尚有未完成样本")
    network = index.get("network")
    _require(isinstance(network, dict), "T25 网络摘要缺失")
    _require(network.get("layer_count") == EXPECTED_LAYER_COUNT, "T25 网络层数不为 38")
    _require(network.get("unique_output_raw_bytes_per_sample") == EXPECTED_RAW_BYTES, "T25 每样本原始输出字节数不匹配")
    records = index.get("samples")
    _require(isinstance(records, list) and len(records) == EXPECTED_SAMPLE_COUNT, "T25 样本记录数不为 109")

    for sample_index, record in enumerate(records):
        _require(isinstance(record, dict), f"T25 样本 {sample_index} 记录不是 object")
        _require(record.get("sample_index") == sample_index, f"T25 样本顺序在 {sample_index} 处不连续")
        _require(isinstance(record.get("sample_id"), str) and record["sample_id"], f"T25 样本 {sample_index} 缺少 sample_id")
        sample_network = record.get("network")
        _require(isinstance(sample_network, dict), f"T25 样本 {sample_index} 网络摘要缺失")
        _require(sample_network.get("layer_count") == EXPECTED_LAYER_COUNT, f"T25 样本 {sample_index} 层数不为 38")
        _require(sample_network.get("unique_output_raw_bytes") == EXPECTED_RAW_BYTES, f"T25 样本 {sample_index} 原始输出字节数不匹配")
        shard = sample_network.get("compressed_shard")
        _require(isinstance(shard, dict), f"T25 样本 {sample_index} shard 摘要缺失")
        expected_rel = f"{T25_DIRECTORY_RELATIVE_PATH}/tensors/sample_{sample_index:03d}.zlib"
        _require(shard.get("path") == expected_rel, f"T25 样本 {sample_index} shard 路径不匹配")
        _require(shard.get("codec") == "zlib" and shard.get("compression_level") == 9, f"T25 样本 {sample_index} zlib 设置不匹配")
        compressed_bytes = shard.get("compressed_bytes")
        _require(isinstance(compressed_bytes, int) and not isinstance(compressed_bytes, bool) and compressed_bytes > 0, f"T25 样本 {sample_index} 压缩长度无效")
        compressed_sha = shard.get("sha256")
        _require(_is_sha256(compressed_sha), f"T25 样本 {sample_index} 压缩 SHA 格式无效")
        _require(shard.get("decompressed_bytes") == EXPECTED_RAW_BYTES, f"T25 样本 {sample_index} 解压长度不匹配")
        raw_sha = shard.get("decompressed_sha256")
        _require(_is_sha256(raw_sha), f"T25 样本 {sample_index} 解压 SHA 格式无效")
        _require(sample_network.get("raw_stream_sha256") == raw_sha, f"T25 样本 {sample_index} 原始流摘要交叉引用不匹配")
    return records


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and value == value.lower() and all(char in "0123456789abcdef" for char in value)


def _validate_compressed_payload(payload: bytes, shard_record: dict[str, Any]) -> None:
    """逐项校验压缩字节及受长度上限约束的解压摘要。"""
    _require(isinstance(payload, bytes), "生成器没有返回 bytes 类型 shard")
    expected_compressed_bytes = shard_record.get("compressed_bytes")
    _require(len(payload) == expected_compressed_bytes, "生成 shard 的压缩字节数不匹配冻结索引")
    _require(_sha256(payload) == shard_record.get("sha256"), "生成 shard 的压缩 SHA-256 不匹配冻结索引")
    expected_raw_bytes = shard_record.get("decompressed_bytes")
    decompressor = zlib.decompressobj()
    try:
        raw = decompressor.decompress(payload, expected_raw_bytes + 1)
        _require(len(raw) <= expected_raw_bytes, "生成 shard 解压后超过冻结长度")
        _require(not decompressor.unconsumed_tail, "生成 shard 解压数据超过冻结长度")
        tail = decompressor.flush()
    except zlib.error as exc:
        raise RestoreError("生成 shard 不是有效 zlib 数据") from exc
    raw += tail
    _require(decompressor.eof, "生成 shard zlib 流未完整结束")
    _require(not decompressor.unused_data and not decompressor.unconsumed_tail, "生成 shard 含尾随或未消费压缩数据")
    _require(len(raw) == expected_raw_bytes, "生成 shard 解压长度不匹配冻结索引")
    _require(_sha256(raw) == shard_record.get("decompressed_sha256"), "生成 shard 解压 SHA-256 不匹配冻结索引")


def _load_generator(root: Path, index: dict[str, Any], baseline_commit: str) -> Any:
    """先绑定 Git 冻结字节，再从内存执行 T25 生成器。"""
    source = root / GENERATOR_RELATIVE_PATH
    _require_plain_file(source, "冻结 T25 生成器")
    tracked = _run_git(root, "ls-files", "--error-unmatch", "--", GENERATOR_RELATIVE_PATH)
    _require(tracked.decode("utf-8").strip() == GENERATOR_RELATIVE_PATH, "T25 生成器没有按预期路径纳入 Git")
    baseline_blob = _run_git(root, "rev-parse", f"{baseline_commit}:{GENERATOR_RELATIVE_PATH}").decode("ascii").strip()
    head_blob = _run_git(root, "rev-parse", f"HEAD:{GENERATOR_RELATIVE_PATH}").decode("ascii").strip()
    _require(baseline_blob == head_blob, "HEAD 中的 T25 生成器与冻结基线不一致")
    baseline_bytes = _run_git(root, "show", f"{baseline_commit}:{GENERATOR_RELATIVE_PATH}")
    try:
        working_bytes = source.read_bytes()
    except OSError as exc:
        raise RestoreError(f"读取 T25 生成器失败: {exc}") from exc
    _require(working_bytes == baseline_bytes, "工作树 T25 生成器与冻结 Git 基线不一致")

    bindings = index.get("tooling_bindings")
    _require(isinstance(bindings, list), "T25 索引缺少 tooling_bindings")
    exporter_bindings = [
        binding
        for binding in bindings
        if isinstance(binding, dict) and binding.get("role") == "t25_exporter"
    ]
    _require(len(exporter_bindings) == 1, "T25 索引必须包含且只包含一个 t25_exporter binding")
    exporter_binding = exporter_bindings[0]
    _require(exporter_binding.get("path") == GENERATOR_RELATIVE_PATH, "T25 t25_exporter 路径不匹配")
    _require(_is_sha256(exporter_binding.get("sha256")), "T25 t25_exporter SHA-256 无效")
    _require(_sha256(baseline_bytes) == exporter_binding["sha256"], "Git 冻结的 T25 生成器与索引 SHA-256 不匹配")

    module_name = "_s2a_cpu_layer_goldens_restore"
    module = types.ModuleType(module_name)
    module.__file__ = os.fspath(source)
    module.__package__ = ""
    module.__spec__ = importlib.util.spec_from_loader(module_name, loader=None, origin=os.fspath(source))
    try:
        sys.modules[module_name] = module
        code = compile(baseline_bytes, os.fspath(source), "exec", dont_inherit=True)
        exec(code, module.__dict__)
    except BaseException:
        sys.modules.pop(module_name, None)
        raise
    return module


def _validate_index_bindings(index: dict[str, Any], generator: Any, context: dict[str, Any]) -> None:
    """将 checkpoint 来源、工具及运行时绑定到当前冻结生成上下文。"""
    try:
        generator.validate_t25_index_status(index)
        _require(index.get("source_bindings") == context["source_bindings"], "T25 checkpoint source bindings 与冻结输入不符")
        _require(index.get("tooling_bindings") == generator._t25_tooling_bindings(context), "T25 checkpoint tooling bindings 与冻结生成器不符")
        _require(index.get("runtime") == context["runtime"], "T25 checkpoint runtime 与当前生成环境不符")
        checks = generator.verify_synthetic_replay(context)
        _require(len(checks) == 4, "T25 冻结 synthetic RGB replay 覆盖数不为 4")
        _require(index["fixed_sample_catalog"].get("synthetic_rgb_preprocess_replays") == checks, "T25 checkpoint synthetic replay 绑定不匹配")
        context["_synthetic_replay_checks"] = checks
    except (KeyError, TypeError, ValueError, AssertionError) as exc:
        if isinstance(exc, RestoreError):
            raise
        raise RestoreError(f"T25 checkpoint 与冻结生成上下文不匹配: {exc}") from exc


def _write_new_file(path: Path, payload: bytes) -> None:
    """独占创建暂存文件并同步内容，禁止覆盖任何已有路径。"""
    _require(not _lexists(path), f"暂存 shard 目标已存在，拒绝覆盖: {path.name}")
    try:
        with path.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        raise RestoreError(f"写入暂存 shard 失败 {path.name}: {exc}") from exc


def _verify_staged_directory(stage: Path, records: list[dict[str, Any]]) -> None:
    """确认暂存目录只含 109 个普通文件且每个文件摘要仍匹配。"""
    _require_plain_directory(stage, "暂存目录")
    expected_names = {f"sample_{index:03d}.zlib" for index in range(EXPECTED_SAMPLE_COUNT)}
    entries = list(stage.iterdir())
    _require({entry.name for entry in entries} == expected_names, "暂存目录含缺失 shard 或未绑定文件")
    for sample_index, record in enumerate(records):
        path = stage / f"sample_{sample_index:03d}.zlib"
        _require_plain_file(path, f"暂存 shard {sample_index}")
        try:
            payload = path.read_bytes()
        except OSError as exc:
            raise RestoreError(f"重读暂存 shard 失败 {sample_index}: {exc}") from exc
        _validate_compressed_payload(payload, record["network"]["compressed_shard"])


def _fsync_directory(path: Path) -> None:
    """在支持的系统上同步暂存目录项。"""
    if os.name == "nt":
        return
    descriptor = None
    try:
        descriptor = os.open(path, os.O_RDONLY)
        os.fsync(descriptor)
    except OSError as exc:
        raise RestoreError(f"同步暂存目录失败: {exc}") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _rename_directory_noreplace(source: Path, destination: Path) -> None:
    """以原子且不覆盖已有目标的方式发布目录；不支持时直接失败。"""
    if os.name == "nt":
        try:
            os.rename(source, destination)
        except OSError as exc:
            raise RestoreError(f"发布目标冲突或原子改名失败，未覆盖目标: {exc}") from exc
        return
    if os.name == "posix":
        libc = ctypes.CDLL(None, use_errno=True)
        renameat2 = getattr(libc, "renameat2", None)
        _require(renameat2 is not None, "当前 POSIX 系统没有 renameat2；为避免覆盖目标，拒绝发布")
        renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        renameat2.restype = ctypes.c_int
        result = renameat2(-100, os.fsencode(source), -100, os.fsencode(destination), 1)
        if result != 0:
            error_number = ctypes.get_errno()
            if error_number in (errno.EEXIST, errno.ENOTEMPTY, errno.EISDIR):
                raise RestoreError("tensors 目标在发布前出现，拒绝覆盖")
            raise RestoreError(f"renameat2 原子发布失败，errno={error_number}")
        return
    raise RestoreError(f"不支持安全的目录原子发布平台: {os.name}")


def _publish_directory(stage: Path, destination: Path) -> None:
    """校验目标缺失后执行原子 no-replace 目录改名。"""
    _require(not _lexists(destination), f"tensors 目标已存在，拒绝覆盖: {destination}")
    _require(not _has_reparse_point(stage), "暂存目录不能是符号链接或重解析点")
    _rename_directory_noreplace(stage, destination)


def _check_destination(root: Path) -> tuple[Path, Path]:
    """验证 T25 目录路径，并确认 tensors 目标完全缺失。"""
    t25_dir = root / T25_DIRECTORY_RELATIVE_PATH
    _require_plain_directory(t25_dir, "T25 目录")
    target = t25_dir / TENSOR_DIRECTORY_NAME
    _require(not _lexists(target), f"tensors 目标已存在（包括符号链接），拒绝运行: {target}")
    return t25_dir, target


def restore_shards(
    repo_root: Path,
    *,
    max_sample_seconds: float = 600.0,
    max_total_seconds: float = 7200.0,
    baseline_commit: str = BASELINE_COMMIT,
    sample_runner: Callable[..., dict[str, Any]] | None = None,
    generator_loader: Callable[[Path, dict[str, Any], str], Any] = _load_generator,
) -> dict[str, Any]:
    """在隔离目录完整重算并校验 109 个 shard 后，原子发布缺失 tensors 目录。"""
    _require(max_sample_seconds > 0 and max_total_seconds > 0, "单样本和全程超时必须为正")
    root = _check_repository_root(repo_root, baseline_commit)
    t25_dir, destination = _check_destination(root)
    index, index_bytes, index_sha = _read_frozen_index(root, baseline_commit)
    records = _check_frozen_index_shape(index)
    generator = generator_loader(root, index, baseline_commit)
    try:
        context = generator.load_context(root)
    except BaseException as exc:
        raise RestoreError(f"冻结输入或 T25 生成上下文加载失败: {exc}") from exc
    _validate_index_bindings(index, generator, context)
    runner = sample_runner or generator.run_sample_pilot

    try:
        stage_name = tempfile.mkdtemp(prefix=".t25-shards-restore-", dir=t25_dir)
    except OSError as exc:
        raise RestoreError(f"无法创建隔离暂存目录: {exc}") from exc
    stage = Path(stage_name)
    try:
        try:
            _require(stage.resolve(strict=True).parent == t25_dir.resolve(strict=True), "暂存目录未位于 T25 同一文件系统父目录")
            started = time.monotonic()
            for sample_index, record in enumerate(records):
                remaining = max_total_seconds - (time.monotonic() - started)
                _require(remaining > 0, "T25 shard 恢复超过全程超时，未发布输出")
                sample_budget = min(max_sample_seconds, remaining)
                try:
                    pilot = runner(context, sample_index, sample_budget, synthetic_checks=context.get("_synthetic_replay_checks"))
                except BaseException as exc:
                    raise RestoreError(f"T25 样本 {sample_index} 重新生成失败，未发布输出: {exc}") from exc
                _require(isinstance(pilot, dict) and pilot.get("sample_index") == sample_index, f"T25 样本 {sample_index} 生成器返回项错误")
                expected_record = record["network"]["compressed_shard"]
                compressed = pilot.get("compressed_stream")
                _validate_compressed_payload(compressed, expected_record)
                _write_new_file(stage / f"sample_{sample_index:03d}.zlib", compressed)
            _verify_staged_directory(stage, records)

            current_index, current_bytes, current_sha = _read_frozen_index(root, baseline_commit)
            _require(current_bytes == index_bytes and current_sha == index_sha, "生成期间冻结索引发生变化，拒绝发布")
            _require(current_index == index, "生成期间冻结索引内容发生变化，拒绝发布")
            _check_destination(root)
            _fsync_directory(stage)
            _fsync_directory(t25_dir)
            _publish_directory(stage, destination)
            _fsync_directory(t25_dir)
        except RestoreError:
            raise
        except BaseException as exc:
            raise RestoreError(f"T25 shard 恢复失败，未发布输出: {exc}") from exc
    finally:
        if _lexists(stage):
            try:
                _require(not _has_reparse_point(stage), "暂存目录变成符号链接/重解析点，拒绝清理")
                _require(stage.parent.resolve(strict=True) == t25_dir.resolve(strict=True), "暂存目录父路径变化，拒绝清理")
                shutil.rmtree(stage)
            except OSError as exc:
                raise RestoreError(f"清理隔离暂存目录失败: {exc}") from exc

    return {
        "status": "PUBLISHED",
        "sample_count": EXPECTED_SAMPLE_COUNT,
        "layer_count_per_sample": EXPECTED_LAYER_COUNT,
        "index_sha256": index_sha,
        "published_directory": f"{T25_DIRECTORY_RELATIVE_PATH}/{TENSOR_DIRECTORY_NAME}",
    }


def main(argv: list[str] | None = None) -> int:
    """运行安全 T25 shard 恢复命令行入口。"""
    parser = argparse.ArgumentParser(description="按冻结 T25 index 恢复缺失的 109 个 CPU golden shard")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--max-sample-seconds", type=float, default=600.0)
    parser.add_argument("--max-total-seconds", type=float, default=7200.0)
    args = parser.parse_args(argv)
    try:
        result = restore_shards(
            args.repo_root,
            max_sample_seconds=args.max_sample_seconds,
            max_total_seconds=args.max_total_seconds,
        )
    except (RestoreError, OSError, ValueError, OverflowError, ImportError, AssertionError) as exc:
        print(f"T25 shard restore error: {exc}", file=sys.stderr)
        return 2
    print(
        "S2A-T25 shards restored: "
        f"{result['sample_count']}/{result['sample_count']} samples, "
        f"{result['layer_count_per_sample']} layers/sample, "
        f"index_sha256={result['index_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
