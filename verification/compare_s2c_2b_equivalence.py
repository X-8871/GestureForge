#!/usr/bin/env python3
"""离线比较候选检测头和冻结2B原始框字节；不访问串口或板卡。"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time
import zlib

ROOT = Path(__file__).resolve().parents[1]
FROZEN = Path("D:/FPGA_Competition/w2b/report/evidence/S2B-T18/formal_stress1000_then109_20261018_r02/frames/corpus_00001000")
MODEL = Path("D:/FPGA_Competition/report/evidence/S2A-T01/tiny416_model_manifest.json")
GCC = Path("D:/FPGA_S2A_MSYS2_20261001/env/mingw64/bin/gcc.exe")
PINS = {
    "head13.bin": "07b59ca389890e8ac2ac704d97364e9717164becbbe90950dc10e9ed28d2cab6",
    "head26.bin": "7524ce5c60a1a0af3b7275dda1481158f808c1d2354141a66c10de2afe7be14e",
    "capture.json": "8f0a236ad2536bbe96d62f22ee46851dc2f9ba5ee0fe1d8a3f305644e594f771",
    "uart_response_raw.bin": "f906cc005a9c540ed0f4e069dbb79af4a63a9de0987f8ade8186adddf0f53d72",
}
MODEL_SHA = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
INPUT_SHA = "da26d3850d23d6f8cb466416799358e77fbeceaa8ee27696ebf7ab365248ab9e"
FIXTURE_PINS = {
    "fixture_manifest": "bc3cd53c7bb34fb14030a40484b3fe1d07ddc6662f4e233125f4ea2e8ed485d0",
    "input": INPUT_SHA,
    "weight_package": "f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39",
    "golden_unique_stream": "090b1422f8e8d4d22124568af9778ba7bd5e7168407c0125e1e729d4a5a46f80",
}


class Detection(ctypes.Structure):
    """保持冻结C99解码核的结构体布局。"""
    _fields_ = [("class_id", ctypes.c_int32), ("source_order", ctypes.c_int32),
                ("score", ctypes.c_double), ("x1", ctypes.c_double), ("y1", ctypes.c_double),
                ("x2", ctypes.c_double), ("y2", ctypes.c_double)]


def sha(path: Path) -> str:
    """原始字节哈希，不做换行转换。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    """不满足身份或格式约束时拒绝给通过结论。"""
    if not condition:
        raise ValueError(message)


def compare_bytes(actual: bytes, expected: bytes) -> dict:
    """保留完整差异位置；样本检测头仅约25KB。"""
    offsets = [index for index in range(max(len(actual), len(expected)))
               if index >= len(actual) or index >= len(expected) or actual[index] != expected[index]]
    return {"actual_bytes": len(actual), "expected_bytes": len(expected),
            "mismatch_count": len(offsets), "mismatch_offsets": offsets, "exact": not offsets}


def validate_candidate_run(path: Path, result: dict) -> dict:
    """把结果绑定到持久整帧RunId、源码快照、工具日志与原始摘要。"""
    runs = ROOT / "report/evidence/S2C-RTL11"
    require(path.name == "result.json" and path.parent.parent.resolve() == runs.resolve(), "候选结果必须来自S2C-RTL11独立RunId")
    run_id = path.parent.name
    manifest_path = path.parent / "manifest.json"
    require(manifest_path.is_file(), "候选运行清单缺失")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(manifest.get("task_id") == "S2C-RTL11" and manifest.get("run_id") == run_id == result.get("run_id") and
            manifest.get("status") == result.get("status") == "PASS_IDEAL_BULK_FRAME", "候选RunId/状态不一致")
    binding = manifest.get("result", {})
    require(Path(binding.get("path", "")).resolve() == path.resolve() and binding.get("sha256") == sha(path), "清单未绑定实际结果")
    checker = ROOT.parent / "verification/check_manifest_hash_basis.py"
    require(checker.is_file(), "项目哈希门禁不存在")
    checked = subprocess.run([sys.executable, "-X", "utf8", "-B", str(checker), "--repo", str(ROOT),
                              "--paths", manifest_path.relative_to(ROOT).as_posix(), "--mode", "strict", "--json"],
                             capture_output=True, timeout=60)
    require(checked.returncode == 0, "候选运行清单strict核验失败")
    check_result = json.loads(checked.stdout)
    require(check_result.get("manifests_seen") == 1 and check_result.get("entries_checked", 0) >= 49 and
            check_result.get("mismatched") == 0, "候选清单没有实际覆盖完整源快照")
    snapshot = manifest["source_snapshot"]
    snapshot_path = Path(snapshot["path"])
    require(snapshot_path.is_file() and sha(snapshot_path) == snapshot["sha256"], "源码快照清单SHA不符")
    rows = json.loads(snapshot_path.read_text(encoding="utf-8"))["rows"]
    require(len(rows) == 24, "需要21RTL、TB、平台与runner共24源绑定")
    row_digest = hashlib.sha256(json.dumps(rows, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()
    require(row_digest == snapshot["snapshot_binding_sha256"] == result["source_snapshot_binding_sha256"], "源码快照聚合摘要不符")
    for row in rows:
        source = Path(row["snapshot_path"])
        require(source.is_file() and source.resolve().is_relative_to(path.parent.resolve()) and sha(source) == row["sha256"], "持久源码快照损坏或越界")
    tool = manifest["tool"]
    require(tool.get("version_exit_code") == 0 and "Verilator" in tool.get("version", "") and
            tool["version"] == result.get("tool_version"), "工具版本记录不符")
    for phase in ("compile", "simulation"):
        record = manifest[phase]
        require(record.get("exit_code") == 0 and record.get("timeout") is False and not record.get("resource_held") and
                result.get(phase + "_exit_code") == 0, "工具阶段未正常完成：" + phase)
        for log_name in ("stdout_log", "stderr_log"):
            entry = record[log_name]
            log_path = Path(entry["path"])
            require(log_path.is_file() and log_path.resolve().is_relative_to(path.parent.resolve()) and
                    sha(log_path) == entry["sha256"], "工具原始日志绑定失败：" + phase)
    stdout = Path(manifest["simulation"]["stdout_log"]["path"]).read_text(encoding="utf-8", errors="replace")
    stderr = Path(manifest["simulation"]["stderr_log"]["path"]).read_text(encoding="utf-8", errors="replace")
    require("RTL11_RESULT status=PASS_LAYERWISE_EXACT_GOLDEN_NATIVE_BULK" in stdout and
            not any(marker in stdout + "\n" + stderr for marker in ("Fatal:", "%Error", "FATAL:", "ERROR:")), "仿真终止日志没有无错误PASS")
    summary_path = Path(result["golden_compare"]["result_summary_path"])
    require(summary_path.resolve().is_relative_to(path.parent.resolve()), "原始摘要越出候选RunId")
    command = manifest["simulation"]["command"]
    summary_arguments = [value.split("=", 1)[1] for value in command if value.startswith("+RESULT_FILE=")]
    require(len(summary_arguments) == 1 and Path(summary_arguments[0]).resolve() == summary_path.resolve(), "摘要未绑定实际仿真命令")
    summary = dict(re.findall(r"([A-Za-z0-9_]+)=([^\s]+)", summary_path.read_text(encoding="utf-8")))
    require(summary.get("status") == "PASS_LAYERWISE_EXACT_GOLDEN_NATIVE_BULK" and summary.get("feature_write_bytes") == "11382150" and
            summary.get("mismatches") == "0" and summary.get("cycles") == str(result["cycles"]) and
            summary.get("bulk_seed", "").lower() == "0x11c02026" and
            summary.get("scope") == "sample_0_layer_0_to_37_stored_outputs" and summary.get("head13_bytes") == "5070" and
            summary.get("head26_bytes") == "20280" and summary.get("stored_tensors") == "36" and summary.get("alias_rows") == "2",
            "原始摘要与整帧结果不一致")
    return {"manifest_path": str(manifest_path), "manifest_sha256": sha(manifest_path),
            "snapshot_manifest_sha256": sha(snapshot_path), "source_snapshot_binding_sha256": row_digest,
            "strict_hash_check": check_result, "checker_sha256": sha(checker), "tool_version": tool["version"]}


def main() -> int:
    """以同一冻结C核解码候选头，和2B真实UART保存字节逐项对比。"""
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--head13", type=Path, required=True)
    parser.add_argument("--head26", type=Path, required=True)
    parser.add_argument("--candidate-result", type=Path, required=True)
    parser.add_argument("--baseline-control", action="store_true",
                        help="只运行比较器正控；此模式永远不能标记候选通过")
    args = parser.parse_args()
    require(args.run_id and all(c.isascii() and (c.isalnum() or c in "_-") for c in args.run_id), "RunId非法")
    for path in [FROZEN, MODEL.parent, GCC.parent]:
        require(path.is_dir(), "输入父目录不存在：" + str(path))
    for path in [MODEL, GCC, args.head13, args.head26, args.candidate_result]:
        require(path.is_file() and not path.is_symlink(), "输入不是普通文件：" + str(path))
    require(sha(MODEL) == MODEL_SHA, "冻结模型SHA不符")
    for name, expected in PINS.items():
        require(sha(FROZEN / name) == expected, "冻结2B原件SHA不符：" + name)
    capture = json.loads((FROZEN / "capture.json").read_text(encoding="utf-8"))["samples"][0]
    require(capture["frame_id"] == 0 and capture["sample_id"] == "test_fist_000", "基准样本不符")
    require(capture["input"]["pl_input_sha256"] == INPUT_SHA, "基准输入不符")
    candidate_result = json.loads(args.candidate_result.read_text(encoding="utf-8"))
    require(isinstance(candidate_result, dict), "候选运行结果格式错误")
    candidate_run_binding = None
    if not args.baseline_control:
        require(candidate_result.get("status") == "PASS_IDEAL_BULK_FRAME" and
                candidate_result.get("sample_index") == 0 and candidate_result.get("sample_id") == "test_fist_000", "候选必须是同一样本的整帧PASS")
        require(candidate_result.get("compile_exit_code") == 0 and candidate_result.get("simulation_exit_code") == 0,
                "候选编译/仿真真实退出码不符")
        require(candidate_result.get("feature_write_bytes") == 11_382_150 and candidate_result.get("mismatches") == 0 and
                isinstance(candidate_result.get("cycles"), int) and candidate_result["cycles"] > 0, "整帧覆盖/周期记录不符")
        for name, expected in FIXTURE_PINS.items():
            entry = candidate_result.get("fixture_bindings", {}).get(name, {})
            path = Path(entry.get("path", ""))
            require(entry.get("sha256") == expected and path.is_file() and sha(path) == expected, "候选fixture绑定失败：" + name)
        for name, actual in [("head13", args.head13), ("head26", args.head26)]:
            entry = candidate_result.get("heads", {}).get(name, {})
            require(entry.get("matches_golden") is True and Path(entry.get("path", "")).resolve() == actual.resolve() and
                    entry.get("sha256") == sha(actual), "候选检测头没有绑定到完整仿真结果：" + name)
        golden = candidate_result.get("golden_compare", {})
        summary = Path(golden.get("result_summary_path", ""))
        require(summary.is_file() and sha(summary) == golden.get("summary_sha256"), "候选整帧原始摘要绑定失败")
        candidate_run_binding = validate_candidate_run(args.candidate_result, candidate_result)
    require(args.baseline_control or args.head13.resolve() != (FROZEN / "head13.bin").resolve(), "候选不能直接使用基准头；正控须显式标明")
    evidence = ROOT / "report/evidence/S2C-EQ01" / args.run_id
    work = ROOT / "tmp/S2C/S2C-EQ01" / args.run_id
    require(not evidence.exists() and not work.exists(), "RunId已存在，不能覆盖")
    sources = [Path(__file__).resolve(), ROOT / "verification/s2a_ps_decode_nms_reference.c",
               ROOT / "verification/s2a_ps_decode_nms_reference.h"]
    # 相同C解码数学与PS源码必须维持冻结提交内容；仅磁盘换行可不同。
    frozen_head = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "07c3d3958578b9cc9d3b8eae3758711fe08724c2"], text=True).strip()
    for source in sources[1:] + [ROOT / "vitis/s2b_inference_app.c"]:
        relative = source.relative_to(ROOT).as_posix()
        blob = subprocess.check_output(["git", "-C", str(ROOT), "cat-file", "blob", frozen_head + ":" + relative])
        require(source.read_bytes().replace(b"\r\n", b"\n") == blob.replace(b"\r\n", b"\n"), "冻结解码/PS源码发生变化：" + relative)
    wire = (FROZEN / "uart_response_raw.bin").read_bytes()
    require(len(wire) >= 80 and wire[:8] == b"S2BU\x01\x00\x02\x80", "基准UART响应头不符")
    payload_length, payload_crc, header_crc = struct.unpack_from("<III", wire, 28)
    require(len(wire) == 40 + payload_length, "基准UART长度不符")
    require(zlib.crc32(wire[:36]) == header_crc and zlib.crc32(wire[40:]) == payload_crc, "基准UART CRC不符")
    payload = wire[40:]
    meta = struct.unpack_from("<Q8I", payload)
    raw_count, count = meta[4], meta[5]
    require(meta[2] == 0 and meta[3] == 0 and meta[8] == 0, "基准UART报告错误")
    require(payload_length == 40 + 5070 + 20280 + count * 48, "框数量和负载长度不一致")
    expected_boxes = payload[40 + 5070 + 20280:]
    require(payload[40:40 + 5070] == (FROZEN / "head13.bin").read_bytes(), "UART/head13基准不一致")
    require(payload[40 + 5070:40 + 5070 + 20280] == (FROZEN / "head26.bin").read_bytes(), "UART/head26基准不一致")
    evidence.mkdir(parents=True)
    work.mkdir(parents=True)
    snapshots = evidence / "source_snapshot"
    snapshots.mkdir()
    items = []
    for source in sources:
        target = snapshots / source.name
        target.write_bytes(source.read_bytes())
        items.append({"path": target.relative_to(ROOT).as_posix(), "sha256": sha(target), "role": "source_snapshot"})
    for name, original in [("candidate_result.json", args.candidate_result), ("candidate_head13.bin", args.head13), ("candidate_head26.bin", args.head26)]:
        target = evidence / name
        target.write_bytes(original.read_bytes())
        items.append({"path": target.relative_to(ROOT).as_posix(), "sha256": sha(target), "role": "actual_input_snapshot"})
    report = {"status": "NOT_RUN", "hash_basis": "worktree_disk", "sample_index": 0,
              "candidate_run_binding": candidate_run_binding,
              "baseline_control": args.baseline_control, "candidate_result": {"path": str(args.candidate_result), "sha256": sha(args.candidate_result)},
              "source_commit": subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip(),
              "bindings": [{"path": str(path), "sha256": sha(path), "hash_basis": "worktree_disk"}
                           for path in [MODEL, args.head13, args.head26] + [FROZEN / name for name in PINS]],
              "limitations": ["仅离线样本000；C核在主机运行，不是ARM执行或板级性能证据。",
                              "候选模式强制完整整帧PASS/输入权重/实际head绑定；正控模式只验证比较器。",
                              "比较器不独立认证仿真工具执行真实性；应结合原始运行记录与独立审查。"]}
    dll = work / "frozen_decode.dll"
    log = evidence / "gcc_console.log"
    command = [str(GCC), "-std=c99", "-O2", "-Wall", "-Wextra", "-Werror", "-pedantic", "-shared",
               str(snapshots / sources[1].name), "-o", str(dll), "-lm"]
    started = time.monotonic()
    compiler_env = os.environ.copy()
    compiler_env["PATH"] = str(GCC.parent) + os.pathsep + compiler_env.get("PATH", "")
    version = subprocess.run([str(GCC), "--version"], env=compiler_env, capture_output=True, timeout=15)
    report["compiler_version"] = {"exit_code": version.returncode, "stdout": version.stdout.decode("utf-8", errors="replace")}
    compile_error = None
    with log.open("wb") as stream:
        try:
            result = subprocess.run(command, cwd=work, env=compiler_env, stdout=stream, stderr=subprocess.STDOUT, timeout=60)
            compile_exit = result.returncode
        except (OSError, subprocess.TimeoutExpired) as exc:
            compile_exit = None
            compile_error = str(exc)
    report["compile"] = {"argv": command, "exit_code": compile_exit, "error": compile_error,
                         "path_prefix": str(GCC.parent),
                         "elapsed_seconds": time.monotonic() - started, "log_sha256": sha(log), "log_path": str(log)}
    library = None
    try:
        require(compile_exit == 0 and dll.is_file(), "C参考核编译失败：" + str(compile_error))
        library = ctypes.CDLL(str(dll))
        function = library.s2a_t62_decode_nms
        pointer = ctypes.POINTER(ctypes.c_double)
        function.argtypes = [pointer, ctypes.c_size_t, pointer, ctypes.c_size_t, ctypes.c_uint32,
                             ctypes.c_uint32, ctypes.c_double, ctypes.POINTER(Detection), ctypes.c_size_t,
                             ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t)]
        function.restype = ctypes.c_int
        heads = {head["name"]: head for head in json.loads(MODEL.read_text(encoding="utf-8"))["address_map"]["heads"]}
        arrays, comparisons = [], {}
        for name, path, length in [("head13", args.head13, 5070), ("head26", args.head26, 20280)]:
            data = path.read_bytes()
            require(len(data) == length, name + "长度错误")
            comparisons[name] = compare_bytes(data, (FROZEN / (name + ".bin")).read_bytes())
            values = [(byte if byte < 128 else byte - 256) * heads[name]["int8_scale"] for byte in data]
            arrays.append((ctypes.c_double * length)(*values))
        output = (Detection * 15)()
        actual_count, actual_raw = ctypes.c_size_t(), ctypes.c_size_t()
        width, height = capture["input"]["geometry_wh"]
        decode_exit = function(arrays[0], 5070, arrays[1], 20280, width, height, 0.25,
                               output, 15, ctypes.byref(actual_count), ctypes.byref(actual_raw))
        require(decode_exit == 0, "冻结解码器返回错误")
        actual_boxes = b"".join(struct.pack("<ii5d", row.class_id, row.source_order, row.score, row.x1, row.y1, row.x2, row.y2)
                                for row in output[:actual_count.value])
        comparisons["box_wire_fields"] = compare_bytes(actual_boxes, expected_boxes)
        report.update({"comparisons": comparisons, "decode_exit_code": decode_exit,
                       "raw_candidate_count": actual_raw.value, "expected_raw_candidate_count": raw_count,
                       "box_count": actual_count.value, "expected_box_count": count})
        success = all(row["exact"] for row in comparisons.values()) and actual_raw.value == raw_count and actual_count.value == count
        report["status"] = ("PASS_COMPARATOR_BASELINE_CONTROL_ONLY" if args.baseline_control else "PASS_OFFLINE_BYTE_COMPARISON_ONLY") if success else "FAIL_BYTE_COMPARISON"
    except Exception as exc:
        report.update({"status": "FAIL_COMPARISON_OR_TOOL", "error": str(exc)})
    finally:
        if library is not None and os.name == "nt":
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel.FreeLibrary.argtypes = [ctypes.c_void_p]
            kernel.FreeLibrary.restype = ctypes.c_int
            kernel.FreeLibrary(library._handle)
            library._handle = 0
    result_path = evidence / "result.json"
    result_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    items.append({"path": result_path.relative_to(ROOT).as_posix(), "sha256": sha(result_path), "role": "result"})
    (evidence / "manifest.json").write_text(json.dumps({"hash_basis": "worktree_disk", "items": items,
        "limitations": report["limitations"]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "result": str(result_path)}, ensure_ascii=False))
    return 0 if report["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    sys.exit(main())
