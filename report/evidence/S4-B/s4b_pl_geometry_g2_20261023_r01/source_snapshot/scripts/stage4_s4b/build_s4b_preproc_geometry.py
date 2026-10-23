"""生成仅含 D2 几何索引和 binary64 权重的草案元数据。"""

from __future__ import annotations

import argparse
import ast
import __future__
import hashlib
import json
import math
import ntpath
import os
import platform
import re
import stat
import struct
import sys
import zlib
from pathlib import Path
from typing import Any


REFERENCE_RELATIVE_PATH = Path("verification") / "s1_t02_d2_numeric_reference.py"
VERIFIED_REFERENCE_SHA256 = frozenset(
    {
        "ea48281fa1c1ba14006f6131ff377c7e4523da8c7e4977b0949d454a7c9ded90",
        "6a3453d5bd60ab122c236667fbc9bcb5aa161d14b76bc7115b602743d5cbe54f",
    }
)
STATUS_DRAFT = "DRAFT_GEOMETRY_ONLY_NOT_FOR_HARDWARE"
SCHEMA_VERSION = 1
_REFERENCE_FUNCTIONS = ("letterbox_geometry",)


class ReferenceIntegrityError(ValueError):
    """冻结 D2 源码哈希不在已核验集合中。"""


def _repo_root() -> Path:
    """返回本模块所在工作树的仓库根目录。"""
    return Path(__file__).resolve().parents[2]


def _default_reference_path() -> Path:
    """返回工作树内冻结 D2 数值参考源码路径。"""
    return _repo_root() / REFERENCE_RELATIVE_PATH


def _select_reference_path(
    reference_path: str | os.PathLike[str] | None,
) -> Path:
    """拒绝非绝对或含点路径段的外部参考路径。"""
    if reference_path is None:
        return _default_reference_path()
    raw_path = os.fspath(reference_path)
    if type(raw_path) is not str or not ntpath.isabs(raw_path):
        raise ValueError("D2 参考源码路径必须是绝对路径")
    components = re.split(r"[\\/]", raw_path)
    if any(component in {".", ".."} for component in components):
        raise ValueError("D2 参考源码路径禁止包含 . 或 .. 路径段")
    return Path(raw_path)


def _sha256_bytes(content: bytes) -> str:
    """返回原始字节的 SHA-256 小写十六进制摘要。"""
    return hashlib.sha256(content).hexdigest()


def load_verified_d2_geometry_functions(
    reference_path: str | os.PathLike[str] | None = None,
) -> tuple[dict[str, Any], str]:
    """先核对冻结源 SHA，再仅提取两个纯几何函数定义。"""
    selected_path = _select_reference_path(reference_path)
    source_bytes = selected_path.read_bytes()
    source_sha256 = _sha256_bytes(source_bytes)
    if source_sha256 not in VERIFIED_REFERENCE_SHA256:
        raise ReferenceIntegrityError(
            f"冻结 D2 源码 SHA 不匹配：{source_sha256}；未解析或加载源码"
        )

    source_text = source_bytes.decode("utf-8", errors="strict")
    tree = ast.parse(source_text, filename=str(selected_path), mode="exec")
    has_future_annotations = any(
        isinstance(node, ast.ImportFrom)
        and node.module == "__future__"
        and any(alias.name == "annotations" for alias in node.names)
        for node in tree.body
    )
    if not has_future_annotations:
        raise ReferenceIntegrityError("冻结 D2 源码缺少已核验的延迟注解声明")

    functions: dict[str, ast.FunctionDef] = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in _REFERENCE_FUNCTIONS:
            if node.decorator_list:
                raise ReferenceIntegrityError(f"D2 几何函数含意外装饰器：{node.name}")
            functions[node.name] = node
    if set(functions) != set(_REFERENCE_FUNCTIONS):
        raise ReferenceIntegrityError("冻结 D2 源码缺少预期的纯几何函数")

    isolated_module = ast.Module(
        body=[functions["letterbox_geometry"]],
        type_ignores=[],
    )
    ast.fix_missing_locations(isolated_module)

    safe_builtins = {
        "ValueError": ValueError,
        "float": float,
        "min": min,
    }
    namespace: dict[str, Any] = {"__builtins__": safe_builtins}
    compiled = compile(
        isolated_module,
        str(selected_path),
        "exec",
        flags=__future__.annotations.compiler_flag,
        dont_inherit=True,
    )
    exec(compiled, namespace, namespace)
    return (
        {
            "letterbox_geometry": namespace["letterbox_geometry"],
        },
        source_sha256,
    )


def _require_positive_int(name: str, value: object) -> int:
    """拒绝布尔伪整数、非整数和非正尺寸。"""
    if type(value) is not int:
        raise ValueError(f"{name} 必须是严格的 Python 整数")
    if value <= 0:
        raise ValueError(f"{name} 必须大于零")
    return value


def _float64_bits(value: float) -> str:
    """将 binary64 数值编码为固定宽度的显式位型字符串。"""
    return f"0x{struct.unpack('>Q', struct.pack('>d', value))[0]:016x}"


def _validate_weight(value: object, name: str) -> float:
    """拒绝非 binary64、非有限、负数或大于一的权重。"""
    if type(value) is not float:
        raise ValueError(f"{name} 必须是 binary64 Python float")
    if not math.isfinite(value):
        raise ValueError(f"{name} 必须是有限数")
    if value < 0.0 or value > 1.0:
        raise ValueError(f"{name} 必须位于 [0, 1]")
    if value == 0.0 and _float64_bits(value) != "0x0000000000000000":
        raise ValueError(f"{name} 的零必须使用正零位型")
    return value


def _validate_axis_entry(
    source_length: int,
    i0: object,
    i1: object,
    w0: object,
    w1: object,
) -> tuple[int, int, float, float]:
    """检查单个轴表项的索引和权重域。"""
    if type(source_length) is not int or source_length <= 0:
        raise ValueError("source_length 必须是正整数")
    if type(i0) is not int or type(i1) is not int:
        raise ValueError("几何索引必须是严格整数")
    if not (0 <= i0 < source_length and 0 <= i1 < source_length):
        raise ValueError("几何索引越出源轴范围")
    checked_w0 = _validate_weight(w0, "w0")
    checked_w1 = _validate_weight(w1, "w1")
    if checked_w0 + checked_w1 != 1.0:
        raise ValueError("双线性权重必须按 binary64 精确和为 1")
    return i0, i1, checked_w0, checked_w1


def _axis_table(
    source_length: int,
    new_length: int,
    *,
    same_size_copy: bool,
) -> dict[str, Any]:
    """按 D2 运算顺序生成一个轴的索引和权重位型表。"""
    _require_positive_int("source_length", source_length)
    _require_positive_int("new_length", new_length)

    if same_size_copy:
        if source_length != new_length:
            raise ValueError("same-size 复制轴的源长与目标长必须相同")
        scale: float | None = None
        scale_bits: str | None = None
        entries = []
        for position in range(new_length):
            i0, i1, w0, w1 = _validate_axis_entry(
                source_length, position, position, 1.0, 0.0
            )
            entries.append(
                {
                    "destination_index": position,
                    "i0": i0,
                    "i1": i1,
                    "fracbits": _float64_bits(0.0),
                    "w0bits": _float64_bits(w0),
                    "w1bits": _float64_bits(w1),
                }
            )
        return {
            "source_length": source_length,
            "new_length": new_length,
            "scale_f64_hex": None,
            "scale_bits": scale_bits,
            "scale_semantics": "D2 same-size early return; axis coefficients are identity metadata",
            "entries": entries,
        }

    if new_length == 1:
        scale = 0.0
    else:
        try:
            scale = (source_length - 1) / (new_length - 1)
        except (OverflowError, ZeroDivisionError) as exc:
            raise ValueError("D2 几何缩放系数无法表示为有限 binary64") from exc
    if not math.isfinite(scale) or scale < 0.0:
        raise ValueError("D2 几何缩放系数必须有限且非负")

    entries = []
    for position in range(new_length):
        if new_length == 1 or position == new_length - 1:
            i0 = source_length - 1
            i1 = i0
            frac = 0.0
        else:
            sample_position = position * scale
            if not math.isfinite(sample_position) or sample_position < 0.0:
                raise ValueError("D2 源坐标必须有限且非负")
            i0 = int(sample_position)
            frac = sample_position - i0
            i1 = min(i0 + 1, source_length - 1)
        if not math.isfinite(frac) or frac < 0.0 or frac > 1.0:
            raise ValueError("D2 分数坐标必须位于 [0, 1]")
        w0 = 1.0 - frac
        w1 = frac
        i0, i1, w0, w1 = _validate_axis_entry(source_length, i0, i1, w0, w1)
        entries.append(
            {
                "destination_index": position,
                "i0": i0,
                "i1": i1,
                "fracbits": _float64_bits(frac),
                "w0bits": _float64_bits(w0),
                "w1bits": _float64_bits(w1),
            }
        )
    return {
        "source_length": source_length,
        "new_length": new_length,
        "scale_f64_hex": scale.hex(),
        "scale_bits": _float64_bits(scale),
        "scale_semantics": "binary64 divide, destination_index*scale, int truncation, subtract, then 1-frac",
        "entries": entries,
    }


def _canonical_bytes(metadata: dict[str, Any]) -> bytes:
    """序列化不含 integrity 字段的 canonical JSON。"""
    payload = {key: value for key, value in metadata.items() if key != "integrity"}
    serialized = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return serialized.encode("utf-8")


def verify_metadata_integrity(metadata: dict[str, Any]) -> bool:
    """重新核验元数据 canonical SHA-256 和 CRC32。"""
    if type(metadata) is not dict:
        return False
    integrity = metadata.get("integrity")
    if type(integrity) is not dict:
        return False
    try:
        canonical = _canonical_bytes(metadata)
    except (TypeError, ValueError):
        return False
    expected_sha256 = hashlib.sha256(canonical).hexdigest()
    expected_crc32 = f"0x{zlib.crc32(canonical) & 0xffffffff:08x}"
    return (
        integrity.get("canonical_sha256") == expected_sha256
        and integrity.get("canonical_crc32") == expected_crc32
    )


def _attach_integrity(metadata: dict[str, Any]) -> dict[str, Any]:
    """添加 canonical JSON 的 SHA-256 和 CRC32。"""
    canonical = _canonical_bytes(metadata)
    metadata["integrity"] = {
        "canonicalization": "UTF-8 JSON, sorted keys, compact separators, excluding integrity",
        "canonical_sha256": hashlib.sha256(canonical).hexdigest(),
        "canonical_crc32": f"0x{zlib.crc32(canonical) & 0xffffffff:08x}",
    }
    return metadata


def build_s4b_preproc_geometry(
    src_width: int,
    src_height: int,
    dst_width: int,
    dst_height: int,
    *,
    reference_path: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    """生成 D2 几何元数据，不接收、不读取或处理像素。"""
    src_width = _require_positive_int("src_width", src_width)
    src_height = _require_positive_int("src_height", src_height)
    dst_width = _require_positive_int("dst_width", dst_width)
    dst_height = _require_positive_int("dst_height", dst_height)

    reference, reference_sha256 = load_verified_d2_geometry_functions(reference_path)
    try:
        geometry = reference["letterbox_geometry"](
            src_width, src_height, dst_width, dst_height
        )
    except (OverflowError, ZeroDivisionError) as exc:
        raise ValueError("D2 letterbox 几何无法表示") from exc

    new_width = _require_positive_int("new_width", geometry["new_width"])
    new_height = _require_positive_int("new_height", geometry["new_height"])
    if new_width > dst_width or new_height > dst_height:
        raise ValueError("D2 letterbox 新尺寸越出目标尺寸")
    offset_x = geometry["offset_x"]
    offset_y = geometry["offset_y"]
    if type(offset_x) is not int or type(offset_y) is not int:
        raise ValueError("D2 padding 偏移必须是严格整数")
    right = dst_width - offset_x - new_width
    bottom = dst_height - offset_y - new_height
    if min(offset_x, offset_y, right, bottom) < 0:
        raise ValueError("D2 letterbox padding 几何无效")

    same_size_copy = new_width == src_width and new_height == src_height
    x_axis = _axis_table(src_width, new_width, same_size_copy=same_size_copy)
    y_axis = _axis_table(src_height, new_height, same_size_copy=same_size_copy)
    generator_path = Path(__file__).resolve(strict=True)
    generator_sha256 = _sha256_bytes(generator_path.read_bytes())

    metadata: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_DRAFT,
        "scope": "geometry_and_weights_metadata_only_no_pixel_processing",
        "source_size": {"width": src_width, "height": src_height},
        "destination_size": {"width": dst_width, "height": dst_height},
        "new_size": {"width": new_width, "height": new_height},
        "padding": {
            "left": offset_x,
            "top": offset_y,
            "right": right,
            "bottom": bottom,
            "normalized_value": 0.5,
            "source_uint8_value": 128,
            "offset_semantics": "D2 integer floor: (destination-new_size)//2",
        },
        "resize_semantics": {
            "same_size": same_size_copy,
            "mode": "copy_early_return" if same_size_copy else "endpoint_aligned_bilinear",
            "same_size_rule": (
                "D2 returns a copy before scale calculation; identity axis entries are descriptive only"
            ),
            "endpoint_rule": (
                "new dimension 1 or final destination row/column selects the final source index with frac=0"
            ),
        },
        "geometry": {
            "src_width": src_width,
            "src_height": src_height,
            "dst_width": dst_width,
            "dst_height": dst_height,
            "new_width": new_width,
            "new_height": new_height,
            "offset_x": offset_x,
            "offset_y": offset_y,
            "padding_normalized": 0.5,
            "padding_uint8": 128,
        },
        "axes": {"x": x_axis, "y": y_axis},
        "provenance": {
            "reference_sha256": reference_sha256,
            "generator_sha256": generator_sha256,
            "python_version": platform.python_version(),
        },
    }
    _attach_integrity(metadata)
    return metadata


def _validate_absolute_output_path(raw_path: str) -> str:
    """核对 Windows 绝对输出路径、完整父目录及不存在的目标名。"""
    if type(raw_path) is not str or not raw_path or raw_path.strip() != raw_path:
        raise ValueError("输出路径必须是无首尾空格的非空绝对路径")
    if "\x00" in raw_path or raw_path.startswith(("\\\\?\\", "\\\\.\\")):
        raise ValueError("输出路径含不支持的 NUL 或设备命名空间")
    components = re.split(r"[\\/]", raw_path)
    if any(component in {".", ".."} for component in components):
        raise ValueError("输出路径禁止包含 . 或 .. 路径段")
    if raw_path.endswith(("\\", "/")) or not ntpath.isabs(raw_path):
        raise ValueError("输出路径必须是指向新文件名的 Windows 绝对路径")
    parent_path = ntpath.dirname(raw_path)
    file_name = ntpath.basename(raw_path)
    if not parent_path or not file_name or file_name in {".", ".."}:
        raise ValueError("输出路径必须包含完整父目录与待建文件名")
    try:
        parent_stat = os.stat(parent_path)
    except OSError as exc:
        raise FileNotFoundError(f"输出父目录不存在或不可访问：{parent_path}") from exc
    if not stat.S_ISDIR(parent_stat.st_mode):
        raise NotADirectoryError(f"输出父路径不是目录：{parent_path}")
    if os.path.lexists(raw_path):
        raise FileExistsError(f"拒绝覆盖已有输出目标：{raw_path}")
    return raw_path


def write_s4b_preproc_geometry(
    metadata: dict[str, Any],
    output_path: str,
) -> str:
    """以独占创建方式写入 UTF-8/LF JSON，并返回未改写的绝对路径。"""
    raw_path = _validate_absolute_output_path(output_path)
    if not verify_metadata_integrity(metadata):
        raise ValueError("几何元数据 canonical SHA/CRC 校验失败")
    document = json.dumps(
        metadata,
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
        allow_nan=False,
    ).encode("utf-8") + b"\n"
    descriptor = os.open(
        raw_path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0),
        0o666,
    )
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(document)
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise
    return raw_path


def _build_parser() -> argparse.ArgumentParser:
    """构造只接受几何尺寸和绝对输出路径的命令行参数。"""
    parser = argparse.ArgumentParser(
        description="生成 D2 letterbox 几何元数据草案；不读取或处理像素。"
    )
    parser.add_argument("--src-width", required=True, type=int)
    parser.add_argument("--src-height", required=True, type=int)
    parser.add_argument("--dst-width", required=True, type=int)
    parser.add_argument("--dst-height", required=True, type=int)
    parser.add_argument("--output", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """执行 CLI；成功输出原样绝对路径，失败返回 2。"""
    args = _build_parser().parse_args(argv)
    try:
        output_path = _validate_absolute_output_path(args.output)
        metadata = build_s4b_preproc_geometry(
            args.src_width,
            args.src_height,
            args.dst_width,
            args.dst_height,
        )
        write_s4b_preproc_geometry(metadata, output_path)
    except (OSError, ValueError, TypeError) as exc:
        print(f"error={type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    print(f"status={metadata['status']}")
    print(f"output_path={output_path}")
    print(f"canonical_sha256={metadata['integrity']['canonical_sha256']}")
    print(f"canonical_crc32={metadata['integrity']['canonical_crc32']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
