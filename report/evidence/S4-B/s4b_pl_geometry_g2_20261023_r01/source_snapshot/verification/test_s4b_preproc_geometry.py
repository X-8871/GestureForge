"""S4-B 几何元数据生成器的离线单元测试。"""

from __future__ import annotations

import contextlib
import __future__
import ast
import hashlib
import io
import importlib.util
import json
import math
import os
import random
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = REPO_ROOT / "scripts" / "stage4_s4b" / "build_s4b_preproc_geometry.py"
GENERATOR_SPEC = importlib.util.spec_from_file_location(
    "build_s4b_preproc_geometry_under_test",
    GENERATOR_PATH,
)
if GENERATOR_SPEC is None or GENERATOR_SPEC.loader is None:
    raise RuntimeError("无法加载当前测试目标模块")
geometry = importlib.util.module_from_spec(GENERATOR_SPEC)
GENERATOR_SPEC.loader.exec_module(geometry)


def _load_d2_reference_for_tests() -> tuple[dict[str, object], str]:
    """核验 D2 字节后仅为测试提取 resize 对照函数。"""
    geometry_functions, verified_sha = geometry.load_verified_d2_geometry_functions()
    reference_path = REPO_ROOT / "verification" / "s1_t02_d2_numeric_reference.py"
    source_bytes = reference_path.read_bytes()
    source_sha = hashlib.sha256(source_bytes).hexdigest()
    if source_sha != verified_sha or source_sha not in geometry.VERIFIED_REFERENCE_SHA256:
        raise AssertionError("D2 源码在测试提取前改变或不在哈希 allowlist")
    tree = ast.parse(source_bytes.decode("utf-8", errors="strict"), filename=str(reference_path))
    resize_function = next(
        (
            node for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "_resize_bilinear_rgb_values"
        ),
        None,
    )
    if resize_function is None or resize_function.decorator_list:
        raise AssertionError("冻结 D2 源码缺少预期 resize 对照函数")
    module = ast.Module(body=[resize_function], type_ignores=[])
    ast.fix_missing_locations(module)
    code = compile(
        module,
        str(reference_path),
        "exec",
        flags=__future__.annotations.compiler_flag,
        dont_inherit=True,
    )
    namespace = {
        "__builtins__": {
            "ValueError": ValueError,
            "int": int,
            "len": len,
            "list": list,
            "min": min,
            "range": range,
        }
    }
    exec(code, namespace, namespace)
    return (
        {
            **geometry_functions,
            "resize_bilinear_rgb_values": namespace["_resize_bilinear_rgb_values"],
        },
        source_sha,
    )


def _float_from_bits(bits: str) -> float:
    """将固定宽度 binary64 位型字符串解码为 Python float。"""
    import struct

    return struct.unpack(">d", int(bits, 16).to_bytes(8, "big"))[0]


def _apply_metadata_weights(
    pixels: list[list[list[int | float]]], metadata: dict[str, object]
) -> list[list[list[float]]]:
    """测试中按元数据索引和权重重建 D2 的插值结果。"""
    axes = metadata["axes"]
    x_entries = axes["x"]["entries"]
    y_entries = axes["y"]["entries"]
    new_width = len(x_entries)
    new_height = len(y_entries)
    result = []
    for y_entry in y_entries:
        y0 = y_entry["i0"]
        y1 = y_entry["i1"]
        wy0 = _float_from_bits(y_entry["w0bits"])
        wy1 = _float_from_bits(y_entry["w1bits"])
        output_row = []
        for x_entry in x_entries:
            x0 = x_entry["i0"]
            x1 = x_entry["i1"]
            wx0 = _float_from_bits(x_entry["w0bits"])
            wx1 = _float_from_bits(x_entry["w1bits"])
            output_pixel = []
            for channel in range(3):
                top = wx0 * pixels[y0][x0][channel] + wx1 * pixels[y0][x1][channel]
                bottom = wx0 * pixels[y1][x0][channel] + wx1 * pixels[y1][x1][channel]
                output_pixel.append(wy0 * top + wy1 * bottom)
            output_row.append(output_pixel)
        result.append(output_row)
    if len(result) != new_height or any(len(row) != new_width for row in result):
        raise AssertionError("测试插值输出尺寸不符")
    return result


class S4BPreprocGeometryTests(unittest.TestCase):
    """覆盖冻结 D2 几何、位型权重、路径与摘要边界。"""

    @classmethod
    def setUpClass(cls) -> None:
        """将 CLI 试写限制在调用者指定的 w4 临时 RunId 下。"""
        temp_root = os.environ.get("TEMP")
        if not temp_root or not Path(temp_root).is_absolute() or not Path(temp_root).is_dir():
            raise RuntimeError("测试必须通过 TEMP 指定已存在的 w4 隔离临时目录")
        cls._temporary = tempfile.TemporaryDirectory(
            prefix="test_s4b_geometry_",
            dir=temp_root,
        )
        cls.temp_dir = Path(cls._temporary.name)

    @classmethod
    def tearDownClass(cls) -> None:
        """仅清理本测试自身在隔离临时目录下创建的文件。"""
        cls._temporary.cleanup()

    def test_reference_hash_is_checked_before_ast_extraction(self) -> None:
        """验证仅加载 allowlist 中的冻结 D2 源码。"""
        functions, source_sha = geometry.load_verified_d2_geometry_functions()
        self.assertEqual(source_sha, "6a3453d5bd60ab122c236667fbc9bcb5aa161d14b76bc7115b602743d5cbe54f")
        self.assertEqual(set(functions), {"letterbox_geometry"})
        reference, reference_sha = _load_d2_reference_for_tests()
        self.assertEqual(reference_sha, source_sha)
        self.assertIn("resize_bilinear_rgb_values", reference)

        bad_reference = self.temp_dir / "not_the_frozen_reference.py"
        bad_reference.write_bytes(b"not the frozen D2 source")
        with self.assertRaises(geometry.ReferenceIntegrityError):
            geometry.load_verified_d2_geometry_functions(bad_reference)
        with self.assertRaises(ValueError):
            geometry.load_verified_d2_geometry_functions(
                "verification/s1_t02_d2_numeric_reference.py"
            )

    def test_202_by_329_to_416_geometry_and_endpoints(self) -> None:
        """核对任务指定的 202x329 letterbox 尺寸、偏移与端点。"""
        result = geometry.build_s4b_preproc_geometry(202, 329, 416, 416)
        self.assertEqual(result["status"], geometry.STATUS_DRAFT)
        self.assertEqual(result["source_size"], {"width": 202, "height": 329})
        self.assertEqual(result["destination_size"], {"width": 416, "height": 416})
        self.assertEqual(result["new_size"], {"width": 255, "height": 416})
        self.assertEqual(
            result["padding"],
            {
                "left": 80,
                "top": 0,
                "right": 81,
                "bottom": 0,
                "normalized_value": 0.5,
                "source_uint8_value": 128,
                "offset_semantics": "D2 integer floor: (destination-new_size)//2",
            },
        )
        self.assertFalse(result["resize_semantics"]["same_size"])
        self.assertEqual(len(result["axes"]["x"]["entries"]), 255)
        self.assertEqual(len(result["axes"]["y"]["entries"]), 416)
        last_x = result["axes"]["x"]["entries"][-1]
        last_y = result["axes"]["y"]["entries"][-1]
        self.assertEqual((last_x["i0"], last_x["i1"]), (201, 201))
        self.assertEqual((last_y["i0"], last_y["i1"]), (328, 328))
        self.assertEqual(last_x["fracbits"], "0x0000000000000000")
        self.assertEqual(last_y["fracbits"], "0x0000000000000000")

        reference, _ = _load_d2_reference_for_tests()
        d2_geometry = reference["letterbox_geometry"](202, 329, 416, 416)
        for name in ("new_width", "new_height", "offset_x", "offset_y"):
            self.assertEqual(result["geometry"][name], d2_geometry[name])

    def test_axis_weights_reproduce_d2_observable_resize(self) -> None:
        """用 201/202 相邻像素检查权重重建与 D2 结果及量化码。"""
        result = geometry.build_s4b_preproc_geometry(3, 3, 5, 5)
        pixels = [
            [[201, 0, 255], [202, 20, 100], [203, 40, 0]],
            [[10, 30, 50], [60, 80, 100], [110, 130, 150]],
            [[255, 220, 180], [140, 100, 60], [20, 10, 0]],
        ]
        reference, _ = _load_d2_reference_for_tests()
        d2_geometry = reference["letterbox_geometry"](3, 3, 5, 5)
        d2_pixels = reference["resize_bilinear_rgb_values"](
            pixels,
            d2_geometry["new_width"],
            d2_geometry["new_height"],
        )
        metadata_pixels = _apply_metadata_weights(pixels, result)
        self.assertEqual(metadata_pixels, d2_pixels)
        self.assertEqual(d2_pixels[0][1][0], 201.5)

        normalized = max(0.0, min(1.0, d2_pixels[0][1][0] / 255.0))
        d2_scale = 1.0 / 127.0
        expected_d2_code = math.floor(abs(normalized / d2_scale) + 0.5)
        self.assertEqual(expected_d2_code, 100)

        rng = random.Random(20261023)
        random_pixels = [
            [[rng.randrange(256) for _ in range(3)] for _ in range(3)]
            for _ in range(3)
        ]
        self.assertEqual(
            _apply_metadata_weights(random_pixels, result),
            reference["resize_bilinear_rgb_values"](random_pixels, 5, 5),
        )

    def test_same_size_copy_is_explicit_and_recoverable(self) -> None:
        """同尺寸路径保留 D2 早返回语义并提供仅描述性的单位表。"""
        result = geometry.build_s4b_preproc_geometry(3, 2, 3, 2)
        self.assertTrue(result["resize_semantics"]["same_size"])
        self.assertEqual(result["resize_semantics"]["mode"], "copy_early_return")
        self.assertIsNone(result["axes"]["x"]["scale_bits"])
        self.assertIsNone(result["axes"]["y"]["scale_bits"])
        self.assertEqual(
            [(entry["i0"], entry["i1"], entry["w0bits"], entry["w1bits"])
             for entry in result["axes"]["x"]["entries"]],
            [
                (0, 0, "0x3ff0000000000000", "0x0000000000000000"),
                (1, 1, "0x3ff0000000000000", "0x0000000000000000"),
                (2, 2, "0x3ff0000000000000", "0x0000000000000000"),
            ],
        )
        pixels = [
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            [[10, 11, 12], [13, 14, 15], [16, 17, 18]],
        ]
        reference, _ = _load_d2_reference_for_tests()
        self.assertEqual(reference["resize_bilinear_rgb_values"](pixels, 3, 2), pixels)
        self.assertEqual(_apply_metadata_weights(pixels, result), pixels)

    def test_new_dimension_one_and_last_destination_rule(self) -> None:
        """核对 new dimension 1 与最后行列均强制末索引、分数为零。"""
        result = geometry.build_s4b_preproc_geometry(1, 2, 2, 2)
        self.assertEqual(result["new_size"], {"width": 1, "height": 2})
        self.assertEqual(len(result["axes"]["x"]["entries"]), 1)
        x_entry = result["axes"]["x"]["entries"][0]
        self.assertEqual((x_entry["i0"], x_entry["i1"]), (0, 0))
        self.assertEqual(x_entry["fracbits"], "0x0000000000000000")
        y_last = result["axes"]["y"]["entries"][-1]
        self.assertEqual((y_last["i0"], y_last["i1"]), (1, 1))
        self.assertEqual(y_last["fracbits"], "0x0000000000000000")

    def test_invalid_dimensions_geometry_indices_and_weights_reject(self) -> None:
        """拒绝伪整数、非法几何、越界索引和不合法权重。"""
        for value in (True, False, 1.0, 0, -1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    geometry.build_s4b_preproc_geometry(value, 2, 2, 2)
        with self.assertRaises(ValueError):
            geometry.build_s4b_preproc_geometry(1, 3, 1, 1)
        with self.assertRaises(ValueError):
            geometry._validate_axis_entry(2, 0, 2, 1.0, 0.0)
        with self.assertRaises(ValueError):
            geometry._validate_axis_entry(2, True, 1, 1.0, 0.0)

        for weight in (float("nan"), float("inf"), float("-inf"), -0.25, 1.0001, -0.0):
            with self.subTest(weight=weight):
                with self.assertRaises(ValueError):
                    geometry._validate_weight(weight, "weight")
        with self.assertRaises(ValueError):
            geometry._validate_axis_entry(2, 0, 1, 0.25, 0.25)

    def test_canonical_sha_crc_and_mutation_detection(self) -> None:
        """校验 canonical SHA-256、CRC32 及内容变更检测。"""
        result = geometry.build_s4b_preproc_geometry(202, 329, 416, 416)
        self.assertTrue(geometry.verify_metadata_integrity(result))
        self.assertRegex(result["integrity"]["canonical_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(result["integrity"]["canonical_crc32"], r"^0x[0-9a-f]{8}$")
        changed = json.loads(json.dumps(result))
        changed["geometry"]["offset_x"] += 1
        self.assertFalse(geometry.verify_metadata_integrity(changed))

    def test_cli_writes_exact_absolute_path_once_and_utf8_lf(self) -> None:
        """核对 CLI 绝对路径输出、独占创建和 UTF-8/LF 文件格式。"""
        output_path = str(self.temp_dir / "geometry.json")
        stdout = io.StringIO()
        stderr = io.StringIO()
        args = [
            "--src-width", "3",
            "--src-height", "3",
            "--dst-width", "5",
            "--dst-height", "5",
            "--output", output_path,
        ]
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = geometry.main(args)
        self.assertEqual(exit_code, 0, stderr.getvalue())
        self.assertIn(f"output_path={output_path}\n", stdout.getvalue())
        raw = Path(output_path).read_bytes()
        self.assertTrue(raw.endswith(b"\n"))
        self.assertNotIn(b"\r\n", raw)
        parsed = json.loads(raw.decode("utf-8"))
        self.assertTrue(geometry.verify_metadata_integrity(parsed))

        before = raw
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            second_exit = geometry.main(args)
        self.assertEqual(second_exit, 2)
        self.assertEqual(Path(output_path).read_bytes(), before)

    def test_cli_rejects_relative_and_dot_segment_paths(self) -> None:
        """拒绝相对路径与会被 Path 静默规范化的点路径段。"""
        with self.assertRaises(ValueError):
            geometry._validate_absolute_output_path("relative\\output.json")
        raw = str(self.temp_dir) + r"\.\unexpected.json"
        with self.assertRaises(ValueError):
            geometry._validate_absolute_output_path(raw)


if __name__ == "__main__":
    unittest.main()
