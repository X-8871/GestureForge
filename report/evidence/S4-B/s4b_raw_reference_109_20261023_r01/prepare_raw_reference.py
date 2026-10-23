"""生成冻结109帧的RAW与独立D2参考，仅写本次唯一运行目录。"""
from __future__ import annotations

import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
import time

import cv2
import numpy as np

RUN = Path(__file__).resolve().parent
PROJECT = Path(r"D:\codex-worktrees\w4")
MAIN = Path(r"D:\FPGA_Competition")
DATA = Path(r"D:\FPGA_Data\HaGRIDv2")
FIXED = MAIN / "report/evidence/S2A-T01/fixed_test_samples.json"
REFERENCE = PROJECT / "verification/s1_t02_d2_numeric_reference.py"
FIXED_SHA = "ccf741c1e996c72b985ce1dcbd399c5184347c922d286a8c0250ef5f6a755eed"
D2_SHA = "6a3453d5bd60ab122c236667fbc9bcb5aa161d14b76bc7115b602743d5cbe54f"


def sha(blob: bytes) -> str:
    """计算实际字节摘要。"""
    return hashlib.sha256(blob).hexdigest()


def save_new(path: Path, blob: bytes) -> None:
    """以独占新建方式保存原始字节，永不覆盖。"""
    with path.open("xb") as handle:
        handle.write(blob)


def save_json_new(path: Path, value: object) -> None:
    """保存UTF-8/LF记录。"""
    save_new(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


class MemoryStatus(ctypes.Structure):
    """Windows全局可用物理内存状态。"""
    _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong),
                ("total_phys", ctypes.c_ulonglong), ("avail_phys", ctypes.c_ulonglong),
                ("total_page", ctypes.c_ulonglong), ("avail_page", ctypes.c_ulonglong),
                ("total_virtual", ctypes.c_ulonglong), ("avail_virtual", ctypes.c_ulonglong),
                ("avail_extended", ctypes.c_ulonglong)]


def available_memory() -> int:
    """低于预算时停止，不终止任何其他进程。"""
    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise RuntimeError("无法读取内存预算")
    return int(status.avail_phys)


def synthetic(sample_id: str, seed: int) -> np.ndarray:
    """按冻结构造规则生成四种合成RGB字节；最后仍核对冻结摘要。"""
    count = 416 * 416 * 3
    if sample_id == "synthetic_black":
        raw = bytes(count)
    elif sample_id == "synthetic_white":
        raw = bytes([255]) * count
    elif sample_id == "synthetic_checkerboard":
        raw = bytearray(count)
        for y in range(416):
            for x in range(416):
                value = 255 if (x + y) & 1 else 0
                off = (y * 416 + x) * 3
                raw[off:off + 3] = bytes([value]) * 3
    elif sample_id == "synthetic_xorshift32":
        state = seed & 0xffffffff
        if not state:
            raise ValueError("合成样本种子不得为零")
        raw = bytearray(count)
        for i in range(count):
            state ^= (state << 13) & 0xffffffff
            state ^= state >> 17
            state ^= (state << 5) & 0xffffffff
            raw[i] = state & 0xff
    else:
        raise ValueError("未知合成样本")
    return np.frombuffer(raw, dtype=np.uint8).reshape(416, 416, 3)


def main() -> int:
    """逐帧绑定原图、RAW与冻结D2；失败保留部分结果并非零退出。"""
    started = time.perf_counter()
    rows = []
    result = {"schema_version": 1, "status": "RUNNING", "hardware_execution": "NOT_RUN",
              "model_inference": "NOT_RUN", "pixel_oracle": "direct frozen D2 Python callable",
              "runtime": {"python": sys.version, "numpy": np.__version__, "opencv": cv2.__version__},
              "limits": {"wallclock_seconds": 900, "min_available_phys_bytes": 3 * 1024**3,
                         "min_free_disk_bytes": 4 * 1024**3}, "samples": rows}
    try:
        if RUN.parent != PROJECT / "tmp/4/S4B-PL-RAW-REFERENCE":
            raise ValueError("运行目录不在已授权w4路径")
        for path in (PROJECT, MAIN, DATA):
            if not path.is_dir():
                raise ValueError(f"精确目录不存在：{path}")
        if sha(FIXED.read_bytes()) != FIXED_SHA or sha(REFERENCE.read_bytes()) != D2_SHA:
            raise ValueError("冻结输入清单或D2源码摘要不匹配")
        fixed = json.loads(FIXED.read_text(encoding="utf-8"))
        if fixed["sample_count"] != 109 or len(fixed["samples"]) != 109:
            raise ValueError("冻结样本数不是109")
        manifest = Path(fixed["official_test_manifest"]["path"])
        if not manifest.is_file() or manifest.parent != DATA:
            raise ValueError("公开数据集清单路径绑定错误")
        if sha(manifest.read_bytes()) != fixed["official_test_manifest"]["sha256"]:
            raise ValueError("公开数据集清单摘要不匹配")
        spec = importlib.util.spec_from_file_location("s4b_verified_d2_raw_oracle", REFERENCE)
        if spec is None or spec.loader is None:
            raise RuntimeError("无法载入已验证D2")
        oracle = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(oracle)
        result["source_bindings"] = {"fixed_samples_sha256": FIXED_SHA, "d2_sha256": D2_SHA,
                                     "runner_sha256": sha(Path(__file__).read_bytes()),
                                     "python_executable_sha256": sha(Path(sys.executable).read_bytes()),
                                     "dataset_manifest_sha256": fixed["official_test_manifest"]["sha256"]}
        raw_dir, ref_dir = RUN / "raw", RUN / "reference"
        raw_dir.mkdir()
        ref_dir.mkdir()
        ids = set()
        for index, sample in enumerate(fixed["samples"]):
            if time.perf_counter() - started > 900:
                raise RuntimeError("超过900秒预算")
            if available_memory() < 3 * 1024**3 or shutil.disk_usage(RUN).free < 4 * 1024**3:
                raise RuntimeError("可用物理内存或磁盘低于停止门槛")
            sid = sample["sample_id"]
            if not re.fullmatch(r"[A-Za-z0-9_-]+", sid) or sid in ids:
                raise ValueError("样本ID非法或重复")
            ids.add(sid)
            if sample["source"] == "synthetic_rgb416":
                rgb = synthetic(sid, fixed["seed"])
                image_binding = {"synthetic_seed": fixed["seed"]}
            else:
                rel = sample["relative_image"]
                if Path(rel).is_absolute() or ".." in Path(rel).parts:
                    raise ValueError("源图相对路径越界")
                source = DATA / rel
                if not source.is_file():
                    raise ValueError(f"精确源图路径不存在：{source}")
                encoded = source.read_bytes()
                if sha(encoded) != sample["image_sha256"]:
                    raise ValueError(f"冻结源图摘要不符：{sid}")
                bgr = cv2.imdecode(np.frombuffer(encoded, dtype=np.uint8), cv2.IMREAD_COLOR)
                if bgr is None:
                    raise ValueError(f"OpenCV解码失败：{sid}")
                rgb = bgr[:, :, ::-1].copy()
                del bgr, encoded
                image_binding = {"path": str(source), "sha256": sample["image_sha256"]}
            if tuple(rgb.shape) != (sample["height"], sample["width"], 3) or rgb.dtype != np.uint8:
                raise ValueError(f"RGB几何或类型不符：{sid}")
            raw = rgb.tobytes(order="C")
            raw_sha = sha(raw)
            if "rgb_sha256" in sample and raw_sha != sample["rgb_sha256"]:
                raise ValueError(f"合成RGB摘要不符：{sid}")
            raw_path = raw_dir / (sid + ".rgb")
            save_new(raw_path, raw)
            # 直接调用冻结标量D2，不用向量化生成器充当独立黄金。
            chw = oracle.preprocess_rgb_uint8_to_chw_int8(rgb.tolist(), 416, 416)
            tensor = np.asarray(chw, dtype=np.int8).tobytes(order="C")
            del chw, rgb
            tensor_path = ref_dir / (sid + ".int8")
            save_new(tensor_path, tensor)
            tensor_sha = sha(tensor)
            row = {"frame_id": sample["frame_id"], "sample_id": sid, "source": image_binding,
                   "width": sample["width"], "height": sample["height"],
                   "stride": sample["width"] * 3, "raw_path": str(raw_path),
                   "raw_bytes": len(raw), "raw_sha256": raw_sha,
                   "reference_path": str(tensor_path), "reference_bytes": len(tensor),
                   "reference_sha256": tensor_sha, "frozen_tensor_sha256": sample["pl_input_sha256"],
                   "status": "PASS" if tensor_sha == sample["pl_input_sha256"] and len(tensor) == 519168 else "FAIL"}
            rows.append(row)
            with (RUN / "progress.jsonl").open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                handle.flush()
            print(f"{index + 1}/109 {sid} {row['status']}", flush=True)
            del raw, tensor
            if row["status"] != "PASS":
                raise ValueError(f"D2重生成与冻结输入张量不符：{sid}")
        result["status"] = "PASS_109_RAW_AND_DIRECT_D2_REFERENCE_ONLY"
        result["raw_total_bytes"] = sum(row["raw_bytes"] for row in rows)
        result["reference_total_bytes"] = sum(row["reference_bytes"] for row in rows)
        result["limitations"] = ["仅本次RGB解码和独立CPU D2参考；不是PL、模型、板卡或4D通过。",
                                 "未生成最终DDR邮箱ABI或批准写入地址；真实摄像头未验证。",
                                 "RAW/参考保留本地tmp，不进入源码Git；失败运行不得覆盖或删除。"]
        return_code = 0
    except Exception as exc:
        result["status"] = "FAIL_PRESERVED_PARTIAL_RESULTS"
        result["error"] = f"{type(exc).__name__}: {exc}"
        print(result["error"], file=sys.stderr, flush=True)
        return_code = 1
    result["elapsed_seconds"] = time.perf_counter() - started
    result["exit_code"] = return_code
    save_json_new(RUN / "result.json", result)
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
