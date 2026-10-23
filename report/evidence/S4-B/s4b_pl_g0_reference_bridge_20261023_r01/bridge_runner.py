from __future__ import annotations

import ast
import ctypes
import hashlib
import json
import math
import pathlib
import subprocess
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone
from typing import Sequence


RUN_DIR = pathlib.Path(__file__).resolve().parent
SOURCE_PATHS = {
    "generator": pathlib.Path(r"D:\FPGA_Competition\verification\s2a_model_delivery.py"),
    "main_d2": pathlib.Path(r"D:\FPGA_Competition\verification\s1_t02_d2_numeric_reference.py"),
    "w4_d2": pathlib.Path(r"D:\codex-worktrees\w4\verification\s1_t02_d2_numeric_reference.py"),
    "rounder": pathlib.Path(r"D:\FPGA_Competition\verification\s1_t02_d2_int8_forward.py"),
}
EXPECTED_SOURCE_SHA256 = {
    "generator": "4831fff0e8ebb189ac9767ae423ad8d5268fc5bee5e333cc2a132112ccfdaab8",
    "main_d2": "ea48281fa1c1ba14006f6131ff377c7e4523da8c7e4977b0949d454a7c9ded90",
    "w4_d2": "6a3453d5bd60ab122c236667fbc9bcb5aa161d14b76bc7115b602743d5cbe54f",
    "rounder": "5dfdbb4a9e57256b362629a2de40b9724df6d28ae225ce6d6622429b9cbad393",
}
EXPECTED_GENERATOR_BYTES = 103291
EXPECTED_MAIN_D2_BYTES = 17935
EXPECTED_W4_D2_BYTES = 18337
MAX_RUNTIME_SECONDS = 60.0
MAX_MEMORY_BYTES = 1024 * 1024 * 1024


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_and_verify_sources() -> tuple[dict[str, bytes], dict[str, dict[str, object]]]:
    source_bytes: dict[str, bytes] = {}
    source_info: dict[str, dict[str, object]] = {}
    for name, path in SOURCE_PATHS.items():
        data = path.read_bytes()
        digest = sha256(data)
        if digest != EXPECTED_SOURCE_SHA256[name]:
            raise RuntimeError(f"源码哈希不符：{name} {path} {digest}")
        source_bytes[name] = data
        source_info[name] = {
            "path": str(path),
            "bytes": len(data),
            "sha256": digest,
        }
    for name, expected_size in (
        ("generator", EXPECTED_GENERATOR_BYTES),
        ("main_d2", EXPECTED_MAIN_D2_BYTES),
        ("w4_d2", EXPECTED_W4_D2_BYTES),
    ):
        if len(source_bytes[name]) != expected_size:
            raise RuntimeError(f"源码字节数不符：{name} {len(source_bytes[name])}")
    main_normalized = source_bytes["main_d2"].replace(b"\r\n", b"\n")
    w4_normalized = source_bytes["w4_d2"].replace(b"\r\n", b"\n")
    source_info["d2_line_ending_comparison"] = {
        "main_normalized_sha256": sha256(main_normalized),
        "w4_normalized_sha256": sha256(w4_normalized),
        "normalized_bytes_equal": main_normalized == w4_normalized,
        "interpretation": "仅在换行规范化后相同；原始源码哈希仍分别保留",
    }
    if main_normalized != w4_normalized:
        raise RuntimeError("主树与 w4 的 D2 源码在换行规范化后仍有差异")
    return source_bytes, source_info


def parse_tree(data: bytes, filename: str) -> tuple[str, ast.Module]:
    source = data.decode("utf-8")
    return source, ast.parse(source, filename=filename)


def select_node(tree: ast.Module, kind: type[ast.AST], name: str) -> ast.AST:
    for node in tree.body:
        if isinstance(node, kind) and getattr(node, "name", None) == name:
            return node
    raise RuntimeError(f"AST 节点缺失：{name}")


def select_assignment(tree: ast.Module, names: set[str]) -> list[ast.AST]:
    selected: list[ast.AST] = []
    found: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        targets = {target.id for target in node.targets if isinstance(target, ast.Name)}
        matched = targets & names
        if matched:
            if matched != (targets & names) or found & matched:
                raise RuntimeError(f"常量赋值不明确：{sorted(matched)}")
            selected.append(node)
            found.update(matched)
    if found != names:
        raise RuntimeError(f"常量缺失：{sorted(names - found)}")
    return selected


def compile_nodes(nodes: list[ast.AST], filename: str, namespace: dict[str, object]) -> None:
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    exec(compile(module, filename, "exec"), namespace)


def ast_record(label: str, source_path: pathlib.Path, nodes: list[ast.AST]) -> dict[str, object]:
    entries = []
    for node in nodes:
        dumped = ast.dump(node, annotate_fields=True, include_attributes=False)
        entries.append(
            {
                "name": getattr(node, "name", None),
                "node_type": type(node).__name__,
                "source_lines": [getattr(node, "lineno", None), getattr(node, "end_lineno", None)],
                "ast_sha256": sha256(dumped.encode("utf-8")),
                "ast": dumped,
            }
        )
    return {"label": label, "source_path": str(source_path), "nodes": entries}


def build_extracted_callables(
    source_bytes: dict[str, bytes], source_info: dict[str, dict[str, object]]
) -> tuple[dict[str, object], dict[str, object]]:
    import numpy as np

    generator_source, generator_tree = parse_tree(source_bytes["generator"], str(SOURCE_PATHS["generator"]))
    d2_source, d2_tree = parse_tree(source_bytes["w4_d2"], str(SOURCE_PATHS["w4_d2"]))
    rounder_source, rounder_tree = parse_tree(source_bytes["rounder"], str(SOURCE_PATHS["rounder"]))
    del generator_source, d2_source, rounder_source

    d2_nodes = [
        select_node(d2_tree, ast.FunctionDef, name)
        for name in (
            "_finite",
            "round_away_from_zero",
            "saturate_int8",
            "quantize_symmetric",
            "letterbox_geometry",
            "_resize_bilinear_rgb_values",
            "letterbox_rgb_normalized",
            "normalized_hwc_to_chw",
            "quantize_input_chw",
            "preprocess_rgb_uint8_to_chw_int8",
        )
    ]
    d2_constants = select_assignment(d2_tree, {"INT8_MIN", "INT8_MAX", "INPUT_SCALE"})
    d2_namespace: dict[str, object] = {"math": math, "Sequence": Sequence}
    compile_nodes(d2_constants + d2_nodes, str(SOURCE_PATHS["w4_d2"]), d2_namespace)

    rounder_nodes = [
        select_node(rounder_tree, ast.FunctionDef, name)
        for name in ("round_away_array", "saturate_array")
    ]
    rounder_constants = select_assignment(rounder_tree, {"INT8_MIN", "INT8_MAX", "INPUT_SCALE"})
    rounder_namespace: dict[str, object] = {"np": np}
    compile_nodes(rounder_constants + rounder_nodes, str(SOURCE_PATHS["rounder"]), rounder_namespace)

    delivery_error = select_node(generator_tree, ast.ClassDef, "DeliveryError")
    generator_function = select_node(generator_tree, ast.FunctionDef, "preprocess_rgb_chw_int8")
    generator_namespace: dict[str, object] = {
        "np": np,
        "letterbox_geometry": d2_namespace["letterbox_geometry"],
        "INPUT_SCALE": rounder_namespace["INPUT_SCALE"],
        "INT8_MIN": rounder_namespace["INT8_MIN"],
        "INT8_MAX": rounder_namespace["INT8_MAX"],
    }
    compile_nodes([delivery_error, generator_function], str(SOURCE_PATHS["generator"]), generator_namespace)
    generator_namespace["round_away_array"] = rounder_namespace["round_away_array"]
    generator_namespace["saturate_array"] = rounder_namespace["saturate_array"]

    selected_records = [
        ast_record("d2_callable", SOURCE_PATHS["w4_d2"], d2_constants + d2_nodes),
        ast_record("quantizer_helpers", SOURCE_PATHS["rounder"], rounder_constants + rounder_nodes),
        ast_record("numpy_generator", SOURCE_PATHS["generator"], [delivery_error, generator_function]),
    ]
    extraction_manifest = {
        "source_files": source_info,
        "extracted_nodes": selected_records,
        "top_level_module_execution": False,
        "algorithm_rewritten": False,
        "execution_limits": {
            "only_listed_ast_nodes_compiled": True,
            "no_model_or_image_files_opened": True,
            "no_network_access": True,
            "max_runtime_seconds": MAX_RUNTIME_SECONDS,
            "max_memory_bytes": MAX_MEMORY_BYTES,
        },
        "runtime": {
            "python": sys.version,
            "numpy": np.__version__,
        },
    }
    (RUN_DIR / "extraction_manifest.json").write_text(
        json.dumps(extraction_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return generator_namespace, d2_namespace


def peak_memory_bytes() -> dict[str, int | str] | None:
    if sys.platform != "win32":
        return None
    from ctypes import wintypes

    class ProcessMemoryCountersEx(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
            ("PrivateUsage", ctypes.c_size_t),
        ]

    counters = ProcessMemoryCountersEx()
    counters.cb = ctypes.sizeof(counters)
    psapi = ctypes.WinDLL("Psapi.dll")
    kernel32 = ctypes.WinDLL("Kernel32.dll")
    get_process = kernel32.GetCurrentProcess
    get_process.restype = wintypes.HANDLE
    query = psapi.GetProcessMemoryInfo
    query.argtypes = [wintypes.HANDLE, ctypes.POINTER(ProcessMemoryCountersEx), wintypes.DWORD]
    query.restype = wintypes.BOOL
    if not query(get_process(), ctypes.byref(counters), counters.cb):
        return {"error": "GetProcessMemoryInfo 失败"}
    return {
        "peak_working_set_bytes": int(counters.PeakWorkingSetSize),
        "private_usage_bytes": int(counters.PrivateUsage),
    }


def make_pattern(np, height: int, width: int) -> object:
    rgb = np.empty((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            rgb[y, x, 0] = (11 + 13 * y + 3 * x) % 256
            rgb[y, x, 1] = (67 + 7 * y + 17 * x) % 256
            rgb[y, x, 2] = (239 - 5 * y - 11 * x) % 256
    return rgb


def run_case(
    np,
    name: str,
    rgb,
    dst_width: int,
    dst_height: int,
    generation: str,
    generator_namespace: dict[str, object],
    d2_namespace: dict[str, object],
) -> tuple[dict[str, object], object, object]:
    if rgb.dtype != np.uint8 or rgb.ndim != 3 or rgb.shape[2] != 3:
        raise RuntimeError(f"合成输入格式错误：{name}")
    src_height, src_width = rgb.shape[:2]
    geometry = d2_namespace["letterbox_geometry"](src_width, src_height, dst_width, dst_height)
    input_digest = sha256(np.ascontiguousarray(rgb).tobytes())
    started = time.perf_counter()
    generator_output = generator_namespace["preprocess_rgb_chw_int8"](
        rgb, dst_width=dst_width, dst_height=dst_height
    )
    reference_input = rgb.tolist()
    reference_nested = d2_namespace["preprocess_rgb_uint8_to_chw_int8"](
        reference_input, dst_width, dst_height
    )
    reference_output = np.asarray(reference_nested, dtype=np.int8)
    del reference_nested, reference_input
    elapsed = time.perf_counter() - started
    if generator_output.shape != reference_output.shape:
        raise RuntimeError(
            f"輸出形狀不同：{name} generator={generator_output.shape} d2={reference_output.shape}"
        )
    different = generator_output != reference_output
    difference_count = int(np.count_nonzero(different))
    difference_positions = np.argwhere(different)[:32]
    examples = [
        {
            "chw_index": [int(v) for v in position],
            "generator_value": int(generator_output[tuple(position)]),
            "d2_value": int(reference_output[tuple(position)]),
        }
        for position in difference_positions
    ]
    case_result: dict[str, object] = {
        "name": name,
        "synthetic_generation": generation,
        "input_shape_hwc": [int(src_height), int(src_width), 3],
        "input_sha256": input_digest,
        "output_shape_chw": [int(v) for v in generator_output.shape],
        "geometry": geometry,
        "generator_output_sha256": sha256(np.ascontiguousarray(generator_output).tobytes()),
        "d2_output_sha256": sha256(np.ascontiguousarray(reference_output).tobytes()),
        "elementwise_equal": difference_count == 0,
        "difference_count": difference_count,
        "difference_examples": examples,
        "elapsed_seconds": elapsed,
    }
    return case_result, generator_output, reference_output


def worker_main() -> int:
    started = time.perf_counter()
    result: dict[str, object] = {
        "scope": "合成 uint8 RGB 小样本与指定 202x329→416 半边界桥接；不覆盖 109 样本、PL 或 4D 验收",
        "status": "ERROR",
        "cases": [],
        "limits": {"max_runtime_seconds": MAX_RUNTIME_SECONDS, "max_memory_bytes": MAX_MEMORY_BYTES},
    }
    try:
        import numpy as np

        source_bytes, source_info = read_and_verify_sources()
        generator_namespace, d2_namespace = build_extracted_callables(source_bytes, source_info)
        cases: list[dict[str, object]] = []

        vectors = [
            ("black_with_padding", np.zeros((1, 1, 3), dtype=np.uint8), 5, 4, "全黑 1x1 合成帧"),
            ("white_with_padding", np.full((1, 1, 3), 255, dtype=np.uint8), 5, 4, "全白 1x1 合成帧"),
            ("channel_distinction", make_pattern(np, 2, 3), 7, 7, "按坐标构造 RGB 通道区别"),
            ("odd_padding_non_square", make_pattern(np, 2, 4), 5, 7, "按坐标构造非方形且奇数补边"),
            ("source_width_one", make_pattern(np, 5, 1), 4, 7, "按坐标构造源宽为 1"),
            ("source_height_one", make_pattern(np, 1, 5), 7, 4, "按坐标构造源高为 1"),
            ("destination_width_one", make_pattern(np, 5, 2), 1, 7, "按坐标构造目标宽为 1"),
            ("destination_height_one", make_pattern(np, 2, 5), 7, 1, "按坐标构造目标高为 1"),
            ("same_geometry", make_pattern(np, 3, 4), 4, 3, "按坐标构造同尺寸输入"),
        ]
        rng = np.random.default_rng(20261023)
        for index in range(24):
            height = int(rng.integers(1, 11))
            width = int(rng.integers(1, 11))
            rgb = rng.integers(0, 256, size=(height, width, 3), dtype=np.uint8)
            vectors.append(
                (
                    f"seeded_random_{index:02d}",
                    rgb,
                    13,
                    11,
                    "NumPy default_rng seed=20261023, 独立生成 uint8 RGB",
                )
            )

        for name, rgb, dst_width, dst_height, generation in vectors:
            case_result, generator_output, reference_output = run_case(
                np,
                name,
                rgb,
                dst_width,
                dst_height,
                generation,
                generator_namespace,
                d2_namespace,
            )
            cases.append(case_result)
            del generator_output, reference_output, rgb
            if time.perf_counter() - started > MAX_RUNTIME_SECONDS:
                raise TimeoutError("合成桥接超过 60 秒，按限制停止")
            memory = peak_memory_bytes()
            if memory and int(memory.get("peak_working_set_bytes", 0)) > MAX_MEMORY_BYTES:
                raise MemoryError("峰值工作集超过 1 GiB，按限制停止")

        boundary = np.zeros((329, 202, 3), dtype=np.uint8)
        boundary[0, 0, :] = 201
        boundary[0, 1, :] = 202
        boundary_result, boundary_generator, boundary_d2 = run_case(
            np,
            "half_boundary_202x329_to_416",
            boundary,
            416,
            416,
            "全零合成帧；首行相邻 RGB 值 201、202；固定边界向量",
            generator_namespace,
            d2_namespace,
        )
        cases.append(boundary_result)
        boundary_values_generator = [int(boundary_generator[channel, 0, 81]) for channel in range(3)]
        boundary_values_d2 = [int(boundary_d2[channel, 0, 81]) for channel in range(3)]
        special_boundary = {
            "source_geometry_wh": [202, 329],
            "target_geometry_wh": [416, 416],
            "expected_letterbox_geometry": {
                "new_width": 255,
                "new_height": 416,
                "offset_x": 80,
                "offset_y": 0,
            },
            "target_chw_positions": [[channel, 0, 81] for channel in range(3)],
            "generator_values": boundary_values_generator,
            "d2_values": boundary_values_d2,
            "both_equal_100": boundary_values_generator == [100, 100, 100]
            and boundary_values_d2 == [100, 100, 100],
        }
        del boundary_generator, boundary_d2, boundary

        memory = peak_memory_bytes()
        elapsed = time.perf_counter() - started
        mismatches = sum(1 for case in cases if not case["elementwise_equal"])
        status = "PASS_SYNTHETIC_BRIDGE" if mismatches == 0 and special_boundary["both_equal_100"] else "REFERENCE_DIFFERENCE"
        result.update(
            {
                "status": status,
                "case_count": len(cases),
                "fixed_random_seed": 20261023,
                "random_case_count": 24,
                "cases": cases,
                "half_boundary": special_boundary,
                "mismatch_case_count": mismatches,
                "elapsed_seconds": elapsed,
                "peak_memory": memory,
                "memory_below_1gib": memory is None
                or int(memory.get("peak_working_set_bytes", 0)) < MAX_MEMORY_BYTES,
                "algorithm_analysis": [
                    "两路坐标均以 binary64 计算 (src-1)/(dst-1) 与整数坐标乘该系数；端点及尺寸为 1 时均选最后源点。",
                    "两路水平项均为 (1-dx)*左值 + dx*右值，垂直项均为 (1-dy)*top + dy*bottom；乘法交换因子次序不改变 binary64 乘积，乘加未合并。",
                    "两路均在 0..255 域完成插值，再除 255、裁剪、HWC→CHW、除以同一 INPUT_SCALE、半数远离零并饱和到 [-127,127]。",
                    "本实验的逐值比较是当前 Python/NumPy runtime 与合成向量的证据，不是跨平台形式化证明，也不重跑 frozen_test_samples109。",
                ],
                "limitations": [
                    "不读取模型、人像、既有 390 MB golden 或样本清单；不导入原模块，生成器顶层代码未执行。",
                    "只编译 extraction_manifest.json 列出的 AST 常量、纯函数与异常类；源代码未改写。",
                    "不证明所有可能输入、所有 Python/NumPy 版本、PL 实现或 4D 通过。",
                ],
                "completed_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
            }
        )
        if elapsed > MAX_RUNTIME_SECONDS:
            result["status"] = "ERROR_RUNTIME_LIMIT"
        if memory and int(memory.get("peak_working_set_bytes", 0)) > MAX_MEMORY_BYTES:
            result["status"] = "ERROR_MEMORY_LIMIT"
    except Exception as exc:
        result.update(
            {
                "status": "ERROR",
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "elapsed_seconds": time.perf_counter() - started,
                "completed_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
            }
        )
        traceback.print_exc(file=sys.stderr)
    result_path = RUN_DIR / "result.json"
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "case_count": result.get("case_count"),
                "mismatch_case_count": result.get("mismatch_case_count"),
                "half_boundary": result.get("half_boundary"),
                "elapsed_seconds": result.get("elapsed_seconds"),
                "result_path": str(result_path),
            },
            ensure_ascii=False,
        )
    )
    if result["status"] == "PASS_SYNTHETIC_BRIDGE":
        return 0
    if result["status"] == "REFERENCE_DIFFERENCE":
        return 1
    return 2


def launch_and_capture() -> int:
    command = [sys.executable, "-B", str(pathlib.Path(__file__).resolve()), "--worker"]
    completed = subprocess.run(command, capture_output=True, check=False)
    (RUN_DIR / "command_stdout.txt").write_bytes(completed.stdout)
    (RUN_DIR / "command_stderr.txt").write_bytes(completed.stderr)
    (RUN_DIR / "native_exit_code.txt").write_text(f"{completed.returncode}\n", encoding="utf-8")
    sys.stdout.buffer.write(completed.stdout)
    sys.stderr.buffer.write(completed.stderr)
    sys.stdout.flush()
    sys.stderr.flush()
    return completed.returncode


if __name__ == "__main__":
    if sys.argv[1:] == ["--worker"]:
        raise SystemExit(worker_main())
    raise SystemExit(launch_and_capture())
