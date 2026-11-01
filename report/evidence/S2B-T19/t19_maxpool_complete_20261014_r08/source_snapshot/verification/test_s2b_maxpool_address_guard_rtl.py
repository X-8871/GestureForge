#!/usr/bin/env python3
"""验证S12冻结POOL常量实例、全域几何守卫及真实引擎每周期等价。"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
import itertools
import json
import os
from pathlib import Path
import platform
import random
import re
import shutil
import stat
import subprocess
import sys
import time
import traceback

import test_s2b_geometry_specialization_rtl as engine
import test_s2b_backend_coordinates_rtl as backend

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "2257a450239ea19ef4e2ddf7b2833d44020f95e3"
SOURCE_BASELINE = "aa6fd7248ef9271bbcc79fefe097c78fec8fb36a"
RUNNER = "verification/test_s2b_maxpool_address_guard_rtl.py"
SEED = 0x581011
U32 = (1 << 32)-1
T18_COMMITTED_PATH_ALLOWLIST = frozenset((
    "verification/test_s2b_model_acceptance_runner.py",
    "vitis/run_s2b_model_acceptance.py",
))
INPUTS = ("input_base_address", "input_channels", "input_height", "input_width",
          "kernel_height", "kernel_width", "stride_y", "stride_x", "darknet_padding_parameter",
          "input_channel", "output_y", "output_x")
RESOURCE_TOOL_NAMES = frozenset(("vivado.exe", "verilator_bin.exe", "cc1plus.exe", "xsim.exe"))
CACHE_DIRECTORY_LABELS = frozenset(("geometry", "fixed_geometry", "engine"))
WORK_CACHE_LIMIT_BYTES = 671088640
EVIDENCE_LIMIT_BYTES = 104857600
RAM_LIMIT_BYTES = 2147483648
EXPECTED_HEAD = "7b9dc9102c0155cc58c3c9a6eb7b279033abfa2d"
T01_INTERFACE_PATH = "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
T01_INTERFACE_VERSION = "S2A-T01/G0"
T01_INTERFACE_SHA256 = "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230"
FIXTURE_NAMES = (
    "tb_s8_geometry.sv",
    "tb_s2b_fixed_pool_geometry.sv",
    "tb_s2b_geometry_specialization.sv",
    "geometry_vectors.dat",
    "fixed_pool_geometry_vectors.dat",
    "pool_vectors.dat",
    "upsample_vectors.dat",
)


def _windows_available_ram_bytes():
    """通过Windows内存状态API读取真实可用物理内存；查询失败时停止。"""
    if os.name != "nt":
        raise OSError("资源预检仅支持本运行器目标Windows系统")

    import ctypes
    from ctypes import wintypes

    class MemoryStatusEx(ctypes.Structure):
        _fields_ = [
            ("dwLength", wintypes.DWORD),
            ("dwMemoryLoad", wintypes.DWORD),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    query = kernel32.GlobalMemoryStatusEx
    query.argtypes = (ctypes.POINTER(MemoryStatusEx),)
    query.restype = wintypes.BOOL
    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(status)
    if not query(ctypes.byref(status)):
        raise ctypes.WinError(ctypes.get_last_error())
    return int(status.ullAvailPhys)


def _windows_running_heavy_tools():
    """通过Windows进程快照枚举进程；快照或枚举异常时停止。"""
    if os.name != "nt":
        raise OSError("资源预检仅支持本运行器目标Windows系统")

    import ctypes
    from ctypes import wintypes

    class ProcessEntry32W(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.c_size_t),
            ("th32ModuleID", wintypes.DWORD),
            ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", wintypes.LONG),
            ("dwFlags", wintypes.DWORD),
            ("szExeFile", wintypes.WCHAR * 260),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create_snapshot = kernel32.CreateToolhelp32Snapshot
    create_snapshot.argtypes = (wintypes.DWORD, wintypes.DWORD)
    create_snapshot.restype = wintypes.HANDLE
    process_first = kernel32.Process32FirstW
    process_first.argtypes = (wintypes.HANDLE, ctypes.POINTER(ProcessEntry32W))
    process_first.restype = wintypes.BOOL
    process_next = kernel32.Process32NextW
    process_next.argtypes = (wintypes.HANDLE, ctypes.POINTER(ProcessEntry32W))
    process_next.restype = wintypes.BOOL
    close_handle = kernel32.CloseHandle
    close_handle.argtypes = (wintypes.HANDLE,)
    close_handle.restype = wintypes.BOOL

    snapshot = create_snapshot(0x00000002, 0)
    invalid_handle = ctypes.c_void_p(-1).value
    if snapshot == invalid_handle:
        raise ctypes.WinError(ctypes.get_last_error())

    matches = []
    try:
        entry = ProcessEntry32W()
        entry.dwSize = ctypes.sizeof(entry)
        ctypes.set_last_error(0)
        if not process_first(snapshot, ctypes.byref(entry)):
            error = ctypes.get_last_error()
            raise ctypes.WinError(error)

        while True:
            name = entry.szExeFile
            if name and name.lower() in RESOURCE_TOOL_NAMES:
                matches.append(dict(pid=int(entry.th32ProcessID), name=name))
            ctypes.set_last_error(0)
            if not process_next(snapshot, ctypes.byref(entry)):
                error = ctypes.get_last_error()
                if error != 18:  # 错误码18表示枚举结束
                    raise ctypes.WinError(error)
                break
    finally:
        close_handle(snapshot)
    return matches


def resource_preflight(work):
    """采集真实可用内存、目标盘空间及重型工具进程；无法确认时不继续。"""
    return dict(
        available_ram_bytes=_windows_available_ram_bytes(),
        disk_free_bytes=shutil.disk_usage(work).free,
        running_tools=_windows_running_heavy_tools(),
    )


def directory_snapshot(directory):
    """统计运行目录内常规文件；遇到链接或特殊对象时拒绝继续。"""
    if not directory.is_dir() or directory.is_symlink():
        raise ValueError("资源目录不是普通目录：" + str(directory))
    total_bytes = 0
    file_count = 0
    for path in directory.rglob("*"):
        info = path.lstat()
        if path.is_symlink() or (getattr(info, "st_file_attributes", 0) & 0x400):
            raise ValueError("资源目录含链接或重解析点：" + str(path))
        if path.is_file():
            total_bytes += info.st_size
            file_count += 1
        elif not path.is_dir():
            raise ValueError("资源目录含非普通文件对象：" + str(path))
    return {"bytes": total_bytes, "files": file_count}


def cleanup_passed_cache(work, evidence, run_id, label, report, simulation_pass):
    """仅删除完整通过的本Run Verilator目标目录，并记录释放量。"""
    if label not in CACHE_DIRECTORY_LABELS:
        raise ValueError("拒绝未列入白名单的缓存标签：" + label)
    run_root = ROOT / "tmp/2B/S2B-T19" / run_id
    expected_work = run_root / "rtl_run"
    if work.resolve(strict=True) != expected_work.resolve(strict=True):
        raise ValueError("缓存清理工作目录与当前Run根不一致")
    if evidence.resolve(strict=True) != (ROOT / "report/evidence/S2B-T19" / run_id).resolve(strict=True):
        raise ValueError("缓存清理证据目录与当前Run根不一致")
    records = report["runs"][-2:]
    if len(records) != 2 or [item["name"] for item in records] != [label + "_compile", label + "_simulation"]:
        raise ValueError("缓存清理前未完成当前模块的compile和simulation配对")
    if any(item.get("exit_code") != 0 or item.get("failure") is not None or
           item.get("process_exit_confirmed") is not True for item in records):
        raise ValueError("缓存清理前compile/simulation退出状态未全部通过")
    if simulation_pass.get("passed") is not True:
        raise ValueError("缓存清理前缺少对应仿真PASS证据")

    cache = work / ("obj_" + label)
    if cache.name != "obj_" + label or cache.parent.resolve(strict=True) != work.resolve(strict=True):
        raise ValueError("缓存路径不在本Run rtl_run根的直接子目录")
    if not cache.is_dir() or cache.is_symlink():
        raise ValueError("通过的Verilator缓存目录缺失或类型异常")
    before_work = directory_snapshot(work)
    before_evidence = directory_snapshot(evidence)
    target_before = directory_snapshot(cache)
    if before_work["bytes"] > WORK_CACHE_LIMIT_BYTES:
        raise ValueError("清理前rtl_run已超过缓存硬上限；保留当前现场")
    if before_evidence["bytes"] > EVIDENCE_LIMIT_BYTES:
        raise ValueError("清理前证据目录已超过证据硬上限；保留当前现场")
    observed_peak = max((int(item.get("peak_work_bytes", 0)) for item in report["runs"]), default=0)
    if max(observed_peak, before_work["bytes"]) > WORK_CACHE_LIMIT_BYTES:
        raise ValueError("本Run观测缓存峰值已超过硬上限；保留当前现场")

    shutil.rmtree(cache)
    if cache.exists():
        raise ValueError("Verilator缓存目录删除后仍存在")
    after_work = directory_snapshot(work)
    after_evidence = directory_snapshot(evidence)
    released_bytes = before_work["bytes"] - after_work["bytes"]
    if released_bytes != target_before["bytes"]:
        raise ValueError("缓存释放量与目标文件字节数不一致")
    if after_work["bytes"] > WORK_CACHE_LIMIT_BYTES or after_evidence["bytes"] > EVIDENCE_LIMIT_BYTES:
        raise ValueError("缓存清理后目录仍超过硬上限")
    budget = report["cache_budget"]
    budget["observed_peak_rtl_run_bytes"] = max(observed_peak, before_work["bytes"])
    budget["removals"].append({
        "label": label,
        "compile_log": records[0]["log"],
        "simulation_log": records[1]["log"],
        "simulation_pass_marker": simulation_pass["marker"],
        "processes_ended": True,
        "deleted_relative_path": cache.relative_to(ROOT).as_posix(),
        "deleted_absolute_path": str(cache.resolve()),
        "deleted_file_count": target_before["files"],
        "deleted_bytes": target_before["bytes"],
        "work_bytes_before": before_work["bytes"],
        "work_bytes_after": after_work["bytes"],
        "bytes_released": released_bytes,
        "released_bytes_verified": True,
        "evidence_bytes_before": before_evidence["bytes"],
        "evidence_bytes_after": after_evidence["bytes"],
        "work_limit_bytes": WORK_CACHE_LIMIT_BYTES,
        "evidence_limit_bytes": EVIDENCE_LIMIT_BYTES,
        "work_within_limit_after": after_work["bytes"] <= WORK_CACHE_LIMIT_BYTES,
        "evidence_within_limit_after": after_evidence["bytes"] <= EVIDENCE_LIMIT_BYTES,
    })


def install_sandbox_path_probe(checker, report):
    """checker逐次核验路径时，仅探测已验证仓库使用的.codex入口。"""
    home = Path.home()
    known_entry = home / ".codex"
    probed_roots = set()

    def wrap_path_check(original_check):
        def checked(root, *args, **kwargs):
            resolved_root = Path(root).resolve()
            original_iterdir = Path.iterdir

            def guarded_iterdir(directory):
                try:
                    yield from original_iterdir(directory)
                except PermissionError:
                    if directory != home or home not in resolved_root.parents:
                        raise
                    if not known_entry.is_dir() or known_entry.is_symlink():
                        raise
                    probed_roots.add(str(resolved_root))
                    yield known_entry

            Path.iterdir = guarded_iterdir
            try:
                return original_check(root, *args, **kwargs)
            finally:
                Path.iterdir = original_iterdir
                report["sandbox_path_probe"] = {
                    "used": bool(probed_roots),
                    "restricted_parent": str(home) if probed_roots else None,
                    "single_verified_entry": str(known_entry) if probed_roots else None,
                    "roots_using_probe": sorted(probed_roots),
                    "remaining_path_components_checked_by_checker": True,
                }
        return checked

    for name in ("check_static", "check_visibility"):
        setattr(checker, name, wrap_path_check(getattr(checker, name)))


def oracle(v):
    """独立NCHW数学定义，使用无限精度整数及公开错误优先生成全部字段。"""
    base, channels, h, w, kh, kw, sy, sx, pad, ch, y, x = v
    zero = (0, 0, 0, 0) + (0,)*36
    if (kh, kw) not in ((2, 2), (3, 3)) or not all((channels, h, w, sy, sx)):
        return (1,)+zero
    if h+pad < kh or w+pad < kw:
        return (1,)+zero
    oh, ow = (h+pad-kh)//sy+1, (w+pad-kw)//sx+1
    if ch >= channels or y >= oh or x >= ow:
        return (1,)+zero
    oy, ox = y*sy-pad//2, x*sx-pad//2
    taps = []; mask = 0; overflow = False
    for tap in range(9):
        if tap >= kh*kw:
            taps.extend((0, 0, 0, 0)); continue
        ky, kx = divmod(tap, kw); ty, tx = oy+ky, ox+kx; addr = 0
        if 0 <= ty < h and 0 <= tx < w:
            mask |= 1 << tap
            row = ch*h+ty
            assert 0 <= row < channels*h < 2**64
            exact = base+row*w+tx
            # 窄表达式只用于交叉核验证明，黄金值始终来自上面的完整地址。
            row_low_sum = ((ch*h) & U32)+ty
            row_high = bool((ch*h) >> 32 or row_low_sum >> 32)
            q = (row_low_sum & U32)*w
            column_sum = (q & U32)+tx
            base_sum = base+(column_sum & U32)
            narrow_bad = bool(row_high or q >> 32 or column_sum >> 32 or base_sum >> 32)
            assert narrow_bad == (exact > U32)
            overflow |= exact > U32
            addr = exact if exact <= U32 else 0
        taps.extend((addr, ch, ty & ((1 << 64)-1), tx & ((1 << 64)-1)))
    return (2,)+zero if overflow else (0, oh, ow, kh*kw, mask, *taps)


def cases():
    """有效小域全坐标、宽输入、明确边界和参数非法样本；种子固定。"""
    rows = []; counts = Counter(); errors = Counter(); padding = 0
    def add(category, v):
        nonlocal padding
        expected = oracle(v); rows.append((v, expected)); counts[category] += 1; errors[expected[0]] += 1
        padding += expected[0] == 0 and expected[4] == 0
    for c, h, w, k, sy, sx, pad in itertools.product((1, 2), range(1, 4), range(1, 4), (2, 3), (1, 2, 3), (1, 2, 3), range(4)):
        oh, ow = max(0, (h+pad-k)//sy+1), max(0, (w+pad-k)//sx+1)
        for ch, y, x in itertools.product(range(c+1), range(oh+1), range(ow+1)):
            for base in (0, U32, U32-c*h*w):
                add("small_all_coordinates_and_outside", (base,c,h,w,k,k,sy,sx,pad,ch,y,x))
    rng = random.Random(SEED)
    for _ in range(20000):
        c,h,w = (rng.choice((1,2,3,13,65536,0x80000000,U32,rng.getrandbits(32))) for _ in range(3))
        k = rng.choice((2,3)); pad = rng.choice((0,1,2,3,100,U32,rng.getrandbits(32)))
        sy,sx = rng.choice((1,2,3,U32)),rng.choice((1,2,3,U32))
        oh,ow = max(0,(h+pad-k)//sy+1),max(0,(w+pad-k)//sx+1)
        y = rng.choice((0,min(U32,max(0,oh-1)),min(U32,oh),rng.getrandbits(32)))
        x = rng.choice((0,min(U32,max(0,ow-1)),min(U32,ow),rng.getrandbits(32)))
        ch = rng.choice((0,max(0,c-1),c,rng.getrandbits(32))) & U32
        add("wide_u32_random", (rng.choice((0,U32,rng.getrandbits(32))),c,h,w,k,k,sy,sx,pad,ch,y,x))
    manual = [
        ("huge_shape_small_window", (0,U32,2,2,2,2,2,2,1,0,0,0),0),
        ("unused_row2_overflow", (0,1,3,0x80000000,2,2,2,2,1,0,0,0),0),
        ("all_padding_high_row", (0,2,3,0x80000000,2,2,1,1,100,1,50,0),0),
        ("last_address_u32", (U32-3,1,2,2,2,2,2,2,1,0,0,0),0),
        ("base_add_carry", (U32-2,1,2,2,2,2,2,2,1,0,0,0),2),
        ("channel_product_high", (0,3,0x80000000,2,2,2,2,2,1,2,0,0),2),
        ("row_sum_carry", (0,2,U32,1,2,2,1,1,1,1,1,0),2),
        ("row_width_high", (0,1,3,U32,2,2,1,1,1,0,1,0),2),
        ("column_add_carry", (0,1,3,U32-1,2,2,1,1,1,0,1,2),2),
        ("c0_high_plane", (0,1,3,0x80000000,2,2,2,2,1,0,0,0),0),
        ("c1_plane_m", (0,2,2,0x80000000,2,2,2,2,1,1,0,0),2),
        ("c2_plane_half_m", (0,3,1,0x80000000,2,2,1,1,1,2,0,0),2),
        ("channel_row_carry", (0,2,3,0x55555555,2,2,1,1,1,1,1,0),2),
        ("row_x_carry", (0,1,2,U32,2,2,1,1,1,0,1,1),2),
        ("signed_padding_u32", (0,1,2,2,3,3,1,1,U32,0,0,0),0),
    ]
    for name, v, error in manual:
        assert oracle(v)[0] == error, name
        add(name,v)
    valid = (0,1,2,2,2,2,2,2,1,0,0,0)
    for index in (1,2,3,6,7):
        v = list(valid); v[index] = 0; add("zero_required_field",tuple(v))
    for kh,kw in ((0,0),(1,1),(2,3),(3,2),(4,4),(U32,U32)):
        v = list(valid); v[4:6] = kh,kw; add("invalid_kernel_pair",tuple(v))
    return rows, dict(vectors=len(rows),categories=dict(counts),errors=dict(errors),all_padding_success=padding,seed=SEED,manual=[dict(name=n,input=v,expected_error=e) for n,v,e in manual])


def geometry_tb():
    """全部公开字段同时对照原RTL与独立黄金，含九组signed坐标。"""
    p = ["module tb_s8_geometry;", "integer count=0; integer scanned; integer f; string vector_path;", "logic [2:0] gold_error; logic [32:0] gold_h,gold_w; logic [3:0] gold_count; logic [8:0] gold_mask;"]
    p += [f"logic [31:0] {n};" for n in INPUTS]
    for variant in ("old","new","gold"):
        if variant != "gold": p += [f"logic [2:0] {variant}_error; logic [32:0] {variant}_h,{variant}_w; logic [3:0] {variant}_count; logic [8:0] {variant}_mask;"]
        p += [f"logic [31:0] {variant}_address[0:8],{variant}_channel[0:8]; logic signed [63:0] {variant}_y[0:8],{variant}_x[0:8];"]
    for variant,module in (("old","int8_maxpool_geometry"),("new","s2b_maxpool_geometry")):
        ports = [f".{n}({n})" for n in INPUTS]+[f".{n}({variant}_{suffix})" for n,suffix in (("output_height","h"),("output_width","w"),("tap_count","count"),("tap_valid_mask","mask"),("error_code","error"),("tap_address","address"),("tap_source_channel","channel"),("tap_source_y","y"),("tap_source_x","x"))]
        p += [f"{module} {variant}_dut("+",".join(ports)+");"]
    fields = list(INPUTS)+["gold_error","gold_h","gold_w","gold_count","gold_mask"]
    fields += [f"gold_{n}[{tap}]" for tap in range(9) for n in ("address","channel","y","x")]
    p += ["initial begin if(!$value$plusargs(\"VECTOR_PATH=%s\",vector_path)) $fatal(1,\"缺少VECTOR_PATH\"); f=$fopen(vector_path,\"r\"); if(!f) $fatal(1,\"缺少向量\"); while(!$feof(f)) begin", 'scanned=$fscanf(f,"'+" ".join("%h" for _ in fields)+'\\n",'+",".join(fields)+");", f"if(scanned=={len(fields)}) begin #1;"]
    for variant in ("old","new"):
        p += [f"if({{{variant}_error,{variant}_h,{variant}_w,{variant}_count,{variant}_mask}} !== {{gold_error,gold_h,gold_w,gold_count,gold_mask}}) $fatal(1,\"几何头字段不等价 {variant} case=%0d\",count);",
              f"for(integer t=0;t<9;t++) if({{{variant}_address[t],{variant}_channel[t],{variant}_y[t],{variant}_x[t]}} !== {{gold_address[t],gold_channel[t],gold_y[t],gold_x[t]}}) $fatal(1,\"几何tap字段不等价 {variant} case=%0d tap=%0d\",count,t);"]
    p += ['count++; end else if(scanned!=-1) $fatal(1,"向量字段不足"); end $fclose(f); $display("PASS S8_GEOMETRY vectors=%0d",count); $finish; end endmodule']
    return "// 原RTL与独立NCHW黄金全字段比较。\n"+"\n".join(p)+"\n"


FIXED_POOL_SHAPES = ((128, 104), (256, 52), (512, 26))


def fixed_shape_vectors():
    """穷举三种冻结形状的每个合法NCHW坐标，并补U32及地址边界。"""
    rows = []
    for shape_index, (channels, height) in enumerate(FIXED_POOL_SHAPES):
        width = height
        for channel, output_y, output_x in itertools.product(
                range(channels), range(height // 2), range(width // 2)):
            rows.append((shape_index, channel, output_y, output_x, 0))
        last_offset = channels * height * width - 1
        rows.append((shape_index, channels - 1, height // 2 - 1, width // 2 - 1, U32 - last_offset))
        rows.append((shape_index, channels - 1, height // 2 - 1, width // 2 - 1, U32 - last_offset + 1))
        rows.extend((shape_index, channel, output_y, output_x, 0) for channel, output_y, output_x in (
            (channels, 0, 0), (U32, 0, 0), (0, U32, 0), (0, 0, U32)))
    data = "".join(" ".join(f"{value:x}" for value in row) + "\n" for row in rows)
    return data, dict(vectors=len(rows), legal_coordinates=sum(c * (h // 2) ** 2 for c, h in FIXED_POOL_SHAPES),
                       shapes=[dict(channels=c, height=h, width=h) for c, h in FIXED_POOL_SHAPES])


def fixed_geometry_tb():
    """穷举固定形状坐标，并逐字段核验专化参数拒绝和输出清零。"""
    p = ["module tb_s2b_fixed_pool_geometry;",
         "logic [31:0] base_address, channel_value, output_y_value, output_x_value;",
         "logic [31:0] vector_shape, input_channel, output_y, output_x;",
         "integer file_handle, scanned, count=0, tap_index;",
         "integer guard_cases=0;",
         "logic [31:0] shape_channels[0:2], shape_height[0:2], shape_width[0:2];",
         "logic [31:0] shape_kernel_height[0:2], shape_kernel_width[0:2];",
         "logic [31:0] shape_stride_y[0:2], shape_stride_x[0:2], shape_padding[0:2];",
         "integer expected_height, expected_width, expected_error;",
         "longint unsigned expected_address, offset_value;",
         "longint signed expected_y, expected_x;",
         "logic [2:0] error_code [0:2]; logic [32:0] output_height [0:2], output_width [0:2];",
         "logic [3:0] tap_count [0:2]; logic [8:0] valid_mask [0:2];",
         "logic [31:0] tap_address [0:2][0:8], tap_channel [0:2][0:8];",
         "logic signed [63:0] tap_source_y [0:2][0:8], tap_source_x [0:2][0:8];",
         "string vector_path;"]
    for index, (channels, height) in enumerate(FIXED_POOL_SHAPES):
        shape = index + 1
        p.append(f"s2b_maxpool_geometry #(.FAST_FIXED_POOL_SHAPE({shape})) u_fixed_{index} ("
                 f".input_base_address(base_address), .input_channels(shape_channels[{index}]), "
                 f".input_height(shape_height[{index}]), .input_width(shape_width[{index}]), "
                 f".kernel_height(shape_kernel_height[{index}]), .kernel_width(shape_kernel_width[{index}]), "
                 f".stride_y(shape_stride_y[{index}]), .stride_x(shape_stride_x[{index}]), "
                 f".darknet_padding_parameter(shape_padding[{index}]), .input_channel(input_channel), "
                 ".output_y(output_y), .output_x(output_x), "
                 f".output_height(output_height[{index}]), .output_width(output_width[{index}]), "
                 f".tap_count(tap_count[{index}]), .tap_valid_mask(valid_mask[{index}]), "
                 f".tap_address(tap_address[{index}]), .tap_source_channel(tap_channel[{index}]), "
                 f".tap_source_y(tap_source_y[{index}]), .tap_source_x(tap_source_x[{index}]), "
                 f".error_code(error_code[{index}]));")
    p.append("""
task automatic restore_shape_parameters;
begin
  shape_channels[0]=32'd128; shape_height[0]=32'd104; shape_width[0]=32'd104;
  shape_kernel_height[0]=32'd2; shape_kernel_width[0]=32'd2; shape_stride_y[0]=32'd2; shape_stride_x[0]=32'd2; shape_padding[0]=32'd1;
  shape_channels[1]=32'd256; shape_height[1]=32'd52; shape_width[1]=32'd52;
  shape_kernel_height[1]=32'd2; shape_kernel_width[1]=32'd2; shape_stride_y[1]=32'd2; shape_stride_x[1]=32'd2; shape_padding[1]=32'd1;
  shape_channels[2]=32'd512; shape_height[2]=32'd26; shape_width[2]=32'd26;
  shape_kernel_height[2]=32'd2; shape_kernel_width[2]=32'd2; shape_stride_y[2]=32'd2; shape_stride_x[2]=32'd2; shape_padding[2]=32'd1;
end
endtask
""")
    for index in range(3):
        p.append(f"""
task automatic assert_shape_{index}_rejected(input integer field_id);
begin
  if(error_code[{index}] !== 3'd1) $fatal(1,"FAST_FIXED_POOL_GUARD_REJECT shape={index + 1} field_id=%0d actual_error=%0d",field_id,error_code[{index}]);
  if({{output_height[{index}],output_width[{index}],tap_count[{index}],valid_mask[{index}]}} !== '0) $fatal(1,"固定shape拒绝头字段未清零 shape={index + 1} field_id=%0d",field_id);
  for(integer guard_tap=0;guard_tap<9;guard_tap++) begin
    if({{tap_address[{index}][guard_tap],tap_channel[{index}][guard_tap],tap_source_y[{index}][guard_tap],tap_source_x[{index}][guard_tap]}} !== '0) $fatal(1,"固定shape拒绝tap字段未清零 shape={index + 1} field_id=%0d tap=%0d",field_id,guard_tap);
  end
end
endtask
""")
    p.append("""
task automatic fast_fixed_shape_guard_rejections;
begin
  base_address=0; input_channel=0; output_y=0; output_x=0;
  for(integer mismatch_shape=0;mismatch_shape<3;mismatch_shape++) begin
    for(integer mismatch_field=0;mismatch_field<8;mismatch_field++) begin
      restore_shape_parameters();
      case(mismatch_field)
        0: shape_channels[mismatch_shape]=shape_channels[mismatch_shape]+32'd1;
        1: shape_height[mismatch_shape]=shape_height[mismatch_shape]+32'd1;
        2: shape_width[mismatch_shape]=shape_width[mismatch_shape]+32'd1;
        3: shape_kernel_height[mismatch_shape]=32'd3;
        4: shape_kernel_width[mismatch_shape]=32'd3;
        5: shape_stride_y[mismatch_shape]=32'd1;
        6: shape_stride_x[mismatch_shape]=32'd1;
        7: shape_padding[mismatch_shape]=32'd0;
        default: $fatal(1,"非法固定shape字段编号");
      endcase
      #1;
      case(mismatch_shape)
        0: assert_shape_0_rejected(mismatch_field);
        1: assert_shape_1_rejected(mismatch_field);
        2: assert_shape_2_rejected(mismatch_field);
        default: $fatal(1,"非法固定shape编号");
      endcase
      guard_cases++;
    end
  end
  restore_shape_parameters();
  $display("FAST_FIXED_POOL_GUARD_REJECTIONS cases=%0d shapes=3 fields_per_shape=8",guard_cases);
end
endtask
""")
    p += [
        'initial begin if(!$value$plusargs("VECTOR_PATH=%s",vector_path)) $fatal(1,"缺少专化向量");',
        'restore_shape_parameters();',
        'file_handle=$fopen(vector_path,"r"); if(!file_handle) $fatal(1,"无法读取专化向量");',
        'while(!$feof(file_handle)) begin',
        'scanned=$fscanf(file_handle,"%h %h %h %h %h\\n",vector_shape,channel_value,output_y_value,output_x_value,base_address);',
        'if(scanned==5) begin input_channel=channel_value; output_y=output_y_value; output_x=output_x_value; #1;',
        'case(vector_shape)',
    ]
    for index, (channels, height) in enumerate(FIXED_POOL_SHAPES):
        width = height
        p += [f"{index}: begin expected_height={height // 2}; expected_width={width // 2};",
              "expected_error=0; offset_value=0;",
              f"if(channel_value>={channels} || output_y_value>={height // 2} || output_x_value>={width // 2}) expected_error=1;",
              "else begin offset_value=channel_value*64'd" + str(height * width) +
              "+(output_y_value*64'd2)*64'd" + str(width) +
              "+output_x_value*64'd2; if(base_address+offset_value+64'd" + str(width + 1) +
              ">64'h00000000ffffffff) expected_error=2; end",
              f"if(expected_error==0 && {{error_code[{index}],output_height[{index}],output_width[{index}],tap_count[{index}],valid_mask[{index}]}} !== {{3'd0,33'd{height // 2},33'd{width // 2},4'd4,9'd15}}) $fatal(1,\"专化geometry头字段错误 shape={index} case=%0d\",count);",
              f"if(expected_error!=0 && error_code[{index}] !== expected_error[2:0]) $fatal(1,\"专化geometry错误码错误 shape={index} case=%0d\",count);",
              f"if(expected_error!=0 && {{output_height[{index}],output_width[{index}],tap_count[{index}],valid_mask[{index}]}} !== '0) $fatal(1,\"专化geometry头字段清零错误 shape={index} case=%0d\",count);",
              "for(tap_index=0;tap_index<9;tap_index++) begin",
              f"if(expected_error==0 && tap_index<4) begin expected_y=output_y_value*64'd2+(tap_index/2); expected_x=output_x_value*64'd2+(tap_index%2);",
              f"expected_address=base_address+channel_value*64'd{height * height}+expected_y*64'd{width}+expected_x;",
              f"if(tap_address[{index}][tap_index] !== expected_address[31:0] || tap_channel[{index}][tap_index] !== channel_value || tap_source_y[{index}][tap_index] !== expected_y || tap_source_x[{index}][tap_index] !== expected_x) $fatal(1,\"专化geometry tap错误 shape={index} case=%0d tap=%0d\",count,tap_index);",
              f"end else if ({{tap_address[{index}][tap_index],tap_channel[{index}][tap_index],tap_source_y[{index}][tap_index],tap_source_x[{index}][tap_index]}} !== '0) $fatal(1,\"专化geometry tap清零错误 shape={index} case=%0d tap=%0d\",count,tap_index);",
              "end end"]
    p += ['default: $fatal(1,"非法专化shape=%0d",vector_shape);',
          'endcase count++; end else if(scanned!=-1) $fatal(1,"专化向量字段不足"); end',
          '$fclose(file_handle); fast_fixed_shape_guard_rejections();',
          '$display("PASS FIXED_POOL_GEOMETRY vectors=%0d guards=%0d",count,guard_cases); $finish; end endmodule']
    return "// 三种冻结shape全坐标穷举，地址黄金仅按NCHW定义计算。\n" + "\n".join(p) + "\n"


def engine_tb(declarations, model):
    """复用原真实引擎差分并补充全部状态硬复位和同沿刺激优先。"""
    tb = engine.generate_tb(declarations)
    tasks = []
    for kind,prefix,index,states in (("pool","p",9,7),("upsample","u",33,6)):
        layer,source = model["layers"][index],model["layers"][index-1]
        ic,ih,iw = source["output_shape_nchw"][1:]; oc,oh,ow = layer["output_shape_nchw"][1:]
        values = dict(layer_index=index,input_base_address=source["tensor_address"],input_length_bytes=source["tensor_length_bytes"],input_channels=ic,input_height=ih,input_width=iw,output_base_address=layer["tensor_address"],output_length_bytes=layer["tensor_length_bytes"],output_channels=oc,output_height=oh,output_width=ow,kernel_height=2,kernel_width=2,stride_y=2,stride_x=2,darknet_padding_parameter=1,stride=2,output_channel=0,output_y=0,output_x=0)
        assigns = " ".join(f"{prefix}_{n}_in=32'h{values[n]:x};" for d,w,n in declarations[kind] if d=="input" and n not in engine.PORT_SKIP)
        tasks += [f"integer {prefix}_reset_coverage=0; task automatic {prefix}_resets; integer elapsed; begin for(integer target=0;target<{states};target++) begin {prefix}_clear; {assigns}",
                  f"{prefix}_pending=0; {prefix}_requests=0; {prefix}_raw=0; {prefix}_response_error=0; {prefix}_error_target=0; {prefix}_stall=1;",
                  f"if(target!=0) begin {prefix}_start_valid_in=1; tick; {prefix}_start_valid_in=0; elapsed=0; while(integer'({prefix}_old.state)!=target && elapsed<200) begin {prefix}_service; elapsed++; end if(elapsed>=200) $fatal(1,\"reset状态不可达\"); end",
                  f"reset=1; {prefix}_start_valid_in=1; {prefix}_result_ready_in=1; {prefix}_backend_rsp_valid_in=1; {prefix}_abort_in=1; tick;",
                  f"if({prefix}_start_ready_old || {prefix}_backend_req_valid_old || {prefix}_result_valid_old || !{prefix}_backend_cancel_old || {prefix}_result_value_old!=0 || {prefix}_result_error_code_old!=0 || {prefix}_result_output_address_old!=0) $fatal(1,\"hard_reset优先或输出清零错误\");",
                  f"{prefix}_reset_coverage|=1<<target; {prefix}_clear; {prefix}_pending=0; reset=0; tick; if(!{prefix}_start_ready_old) $fatal(1,\"reset恢复失败\"); end end endtask"]
    marker = "initial begin p_clear; u_clear;"
    assert marker in tb
    tb = tb.replace(marker,"\n".join(tasks)+"\n"+marker)
    tb = tb.replace("p_vectors; u_vectors;", "p_vectors; u_vectors; p_resets; u_resets; if(p_reset_coverage!=127 || u_reset_coverage!=63) $fatal(1,\"reset覆盖不足\"); $display(\"RESET_COVERAGE pool=%0d upsample=%0d\",p_reset_coverage,u_reset_coverage);")
    return tb


def bind_engine_vector_paths(testbench, evidence):
    """将引擎测试的两个向量文件绑定到本次证据目录的实际路径。"""
    for kind in ("pool", "upsample"):
        original = f'$fopen("{kind}_vectors.dat","r");'
        absolute = (evidence / f"{kind}_vectors.dat").resolve().as_posix()
        replacement = f'$fopen("{absolute}","r");'
        if testbench.count(original) != 1:
            raise ValueError("引擎测试向量入口数量不唯一：" + kind)
        testbench = testbench.replace(original, replacement)
    return testbench


def mutants(checker, work, bindings):
    """自报SHA仍不能修改守卫、清零或模块引用，拒绝原件绑定变化。"""
    fixture = work/"mutants"; fixture.mkdir()
    for p in bindings:
        target=fixture/p; target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(ROOT/p,target)
    profile_path=fixture/"board/s2b_inference_platform.json"; original=profile_path.read_bytes(); records=[]
    for name,path,before,after in (
        ("删除高plane守卫", "src/s2b_maxpool_geometry.sv", "(plane_work[63:32] != 32'd0)", "1'b0"),
        ("C0错误拒绝高plane", "src/s2b_maxpool_geometry.sv", "(input_channel != 32'd0)", "1'b1"),
        ("删除通道低plane乘积高位", "src/s2b_maxpool_geometry.sv", "(channel_offset_work[63:32] != 32'd0)", "1'b0"),
        ("删除通道行加法进位", "src/s2b_maxpool_geometry.sv", "(!USE_FIXED_FAST_PATH && channel_row_sum_work[32])", "1'b0"),
        ("提前拒绝全padding高通道", "src/s2b_maxpool_geometry.sv", "if (tap_range_error) begin", "if (tap_range_error || channel_offset_high) begin"),
        ("提前拒绝未消费第三行", "src/s2b_maxpool_geometry.sv", "if (tap_range_error) begin", "if (tap_range_error || row_offset_work[2][63:32] != 0) begin"),
        ("删除宽度乘积高位", "src/s2b_maxpool_geometry.sv", "selected_row_high || selected_offset_high ||", "selected_row_high || 1'b0 ||"),
        ("删除列加法进位", "src/s2b_maxpool_geometry.sv", "logical_offset_work[32] || address_work[32]", "1'b0 || address_work[32]"),
        ("删除base进位", "src/s2b_maxpool_geometry.sv", "logical_offset_work[32] || address_work[32]", "logical_offset_work[32] || 1'b0"),
        ("更改RANGE清零", "src/s2b_maxpool_geometry.sv", "if (tap_range_error) begin", "if (1'b0) begin"),
        ("更改ARG清零", "src/s2b_maxpool_geometry.sv", "if (error_code == BAD_ARGUMENT) begin", "if (1'b0) begin"),
        ("POOL错层选择及自报SHA", "src/s2b_maxpool_engine.sv", "32'd17: geometry_shape_select = 2'd1;", "32'd17: geometry_shape_select = 2'd0;"),
        ("POOL错plane及自报SHA", "src/s2b_maxpool_engine.sv", "64'd2704", "64'd2705"),
        ("POOL漏row及自报SHA", "src/s2b_maxpool_engine.sv", "({32'd0, output_y} * 64'd52)", "64'd0"),
        ("POOL漏X及自报SHA", "src/s2b_maxpool_engine.sv", "({32'd0, output_y} * 64'd52) + {32'd0, output_x}", "({32'd0, output_y} * 64'd52) + 64'd0"),
        ("POOL截通道高位及自报SHA", "src/s2b_maxpool_engine.sv", "{32'd0, output_channel} * 64'd2704", "{32'd0, (output_channel * 32'd2704)}"),
        ("engine引用回退", "src/s2b_maxpool_engine.sv", "s2b_maxpool_geometry #(.FAST_FIXED_POOL_SHAPE(1)) u_geometry_l9", "int8_maxpool_geometry u_geometry_l9"),
    ):
        target=fixture/path; raw=(ROOT/path).read_bytes(); assert raw.count(before.encode())==1
        target.write_bytes(raw.replace(before.encode(),after.encode()))
        profile=json.loads(original); digest=backend.sha(target)
        for row in profile["source_derivation"]["derived_sources"]:
            if row["path"]==path: row["sha256"]=digest
        profile_path.write_text(json.dumps(profile,ensure_ascii=False),encoding="utf-8")
        try: checker.check_static(fixture)
        except ValueError as exc: records.append(dict(name=name,status="REJECTED",reason=str(exc)))
        else: raise ValueError("自报SHA反例未拒绝："+name)
        target.write_bytes(raw); profile_path.write_bytes(original)
    return records


def run_fast_guard_mutant(work, evidence, verilator, common, env, report):
    """编译削弱固定shape通道守卫的语义变异，并要求新增仿真断言拒绝它。"""
    source_path = ROOT / "src/s2b_maxpool_geometry.sv"
    original = source_path.read_bytes()
    before = b"(input_channels != FAST_INPUT_CHANNELS)"
    after = b"1'b0"
    if original.count(before) != 1:
        raise ValueError("固定shape通道守卫变异定位不唯一")
    mutant_dir = evidence / "semantic_mutants"
    mutant_dir.mkdir()
    mutant_path = mutant_dir / "s2b_maxpool_geometry_no_channel_guard.sv"
    mutant_path.write_bytes(original.replace(before, after))
    mutant_sha = backend.sha(mutant_path)
    testbench = evidence / "tb_s2b_fixed_pool_geometry.sv"
    compile_command = common + ["--top-module", "tb_s2b_fixed_pool_geometry",
                                "--Mdir", "obj_fixed_guard_mutant", str(mutant_path), str(testbench)]
    engine.execute("fixed_guard_mutant_compile", compile_command, work, evidence, env, report, 600)
    compile_log = (evidence / "fixed_guard_mutant_compile.log").read_text(encoding="utf-8")
    forbidden = re.findall(r"%Warning-(?:LATCH|UNOPTFLAT|MULTIDRIVEN).*", compile_log)
    if forbidden:
        raise ValueError("固定shape守卫变异编译出现禁止诊断：" + repr(forbidden))

    expected_fatal = "FAST_FIXED_POOL_GUARD_REJECT shape=1 field_id=0 actual_error=0"
    simulation_command = [str(work / "obj_fixed_guard_mutant" / "Vtb_s2b_fixed_pool_geometry.exe"),
                          "+VECTOR_PATH=" + str(evidence / "fixed_pool_geometry_vectors.dat")]
    try:
        engine.execute("fixed_guard_mutant_simulation", simulation_command, work, evidence, env, report, 600)
    except ValueError:
        simulation_record = report["runs"][-1]
        simulation_log = (evidence / "fixed_guard_mutant_simulation.log").read_text(encoding="utf-8")
        if (simulation_record.get("name") != "fixed_guard_mutant_simulation" or
                simulation_record.get("exit_code") in (None, 0) or
                simulation_record.get("failure") is not None or
                simulation_record.get("process_exit_confirmed") is not True or
                expected_fatal not in simulation_log):
            raise ValueError("固定shape守卫变异未被指定字段断言拒绝：" + repr(simulation_record))
    else:
        raise ValueError("固定shape守卫变异通过了参数拒绝仿真")

    report["fast_guard_semantic_mutants"] = [{
        "count": 1,
        "name": "删除固定shape的input_channels专化守卫",
        "source_path": mutant_path.relative_to(ROOT).as_posix(),
        "source_sha256": mutant_sha,
        "original_source_sha256": backend.sha(source_path),
        "replacement": {"before": before.decode("ascii"), "after": after.decode("ascii")},
        "testbench_path": testbench.relative_to(ROOT).as_posix(),
        "testbench_sha256": backend.sha(testbench),
        "compile_exit_code": report["runs"][-2]["exit_code"],
        "simulation_exit_code": report["runs"][-1]["exit_code"],
        "rejected": True,
        "expected_fatal": expected_fatal,
        "compile_log": report["runs"][-2]["log"],
        "compile_log_sha256": report["runs"][-2]["log_sha256"],
        "simulation_log": report["runs"][-1]["log"],
        "simulation_log_sha256": report["runs"][-1]["log_sha256"],
        "process_exit_confirmed": report["runs"][-1]["process_exit_confirmed"],
    }]


def run_delivery_checker(mode, manifest_path):
    """以准确参数执行阶段交付清单检查器并保留原生输出。"""
    checker_path = ROOT / "verification/check_stage_delivery.py"
    command = [sys.executable, str(checker_path), "--mode", mode,
               "--manifest", str(manifest_path.resolve()), "--project-root", str(ROOT)]
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=120, check=False)
    try:
        parsed = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{mode}交付清单核验未返回JSON：{exc}；stderr={completed.stderr!r}") from exc
    return {
        "mode": mode,
        "command": subprocess.list2cmdline(command),
        "exit_code": completed.returncode,
        "status": parsed.get("status"),
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "manifest_sha256": backend.sha(manifest_path),
    }


def delivery_file_entries(evidence, manifest_path, report):
    """绑定仓库源文件及证据目录内除清单自身外的每个常规文件。"""
    entries = []
    seen = set()
    for relative, expected_hash in sorted(report["source_sha256_pre"].items()):
        path = ROOT / relative
        if backend.sha(path) != expected_hash or expected_hash != report["source_sha256_post"].get(relative):
            raise ValueError("清单生成时源码前后SHA不一致：" + relative)
        entries.append({"path": relative, "sha256": expected_hash, "role": "source"})
        seen.add(relative.casefold())

    fixture_hashes = {item["path"]: item["sha256"] for item in report["fixture_bindings"]}
    discovered_fixtures = set()
    for path in sorted(evidence.rglob("*")):
        info = path.lstat()
        if path.is_symlink() or (getattr(info, "st_file_attributes", 0) & 0x400):
            raise ValueError("交付目录出现链接或reparse点：" + str(path))
        if stat.S_ISDIR(info.st_mode):
            continue
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("交付目录出现非常规文件：" + str(path))
        if path.resolve() == manifest_path.resolve():
            continue
        relative = path.relative_to(ROOT).as_posix()
        key = relative.casefold()
        if key in seen:
            raise ValueError("交付清单路径重复：" + relative)
        seen.add(key)
        if relative.startswith((evidence.relative_to(ROOT).as_posix() + "/source_snapshot/",
                                evidence.relative_to(ROOT).as_posix() + "/semantic_mutants/")):
            role = "source"
        elif path.name in FIXTURE_NAMES:
            role = "input"
            expected_fixture_hash = fixture_hashes.get(relative)
            if expected_fixture_hash is None or backend.sha(path) != expected_fixture_hash:
                raise ValueError("七项仿真夹具路径或SHA不匹配：" + relative)
            discovered_fixtures.add(relative)
        elif relative == (evidence.relative_to(ROOT) / "validation.json").as_posix():
            role = "result"
        elif path.suffix == ".log":
            role = "log"
        else:
            role = "artifact"
        entries.append({"path": relative, "sha256": backend.sha(path), "role": role})
    if discovered_fixtures != set(fixture_hashes):
        raise ValueError("七项仿真夹具未全部进入交付清单：" + repr(sorted(set(fixture_hashes) - discovered_fixtures)))
    return sorted(entries, key=lambda item: item["path"])


def build_delivery_manifest(evidence, run_id, report, checker_runs):
    """按schema v1重建清单，接口仅引用已冻结的S2A-T01正式文档。"""
    interface_path = ROOT / T01_INTERFACE_PATH
    interface_sha = backend.sha(interface_path)
    if interface_sha != T01_INTERFACE_SHA256:
        raise ValueError("S2A-T01冻结接口文档SHA与正式冻结值不符")
    runner_command = subprocess.list2cmdline(report["invocation"]["argv"])
    checks = [{
        "name": "source-provenance",
        "status": "PASS",
        "command": "git rev-parse HEAD",
        "exit_code": 0,
        "reason": (f"source_commit={report['source_commit']}表示本次实际HEAD；"
                   f"task_source_baseline_commit={report['task_source_baseline_commit']}用于T19来源闭包；"
                   f"rtl_engine_comparison_baseline_commit={BASELINE}用于引擎参考版本。"),
    }, {
        "name": "t19-complete-offline-regression",
        "status": "PASS",
        "command": runner_command,
        "exit_code": 0,
        "reason": "几何、固定geometry、真实POOL/upsample引擎仿真及固定shape参数守卫验证全部通过。",
    }]
    for item in report["runs"]:
        if item["name"] == "fixed_guard_mutant_simulation":
            continue
        if item["exit_code"] == 0 and item["failure"] is None:
            checks.append({
                "name": item["name"],
                "status": "PASS",
                "command": subprocess.list2cmdline(item["command"]),
                "exit_code": 0,
                "reason": f"子进程已退出；日志SHA-256={item['log_sha256']}。",
            })
    mutant = report["fast_guard_semantic_mutants"][0]
    checks.append({
        "name": "fixed-shape-guard-semantic-mutant-rejected",
        "status": "PASS",
        "command": runner_command,
        "exit_code": 0,
        "reason": (f"runner成功检测并拒绝变异；变异仿真原生退出码={mutant['simulation_exit_code']}，"
                   f"命中日志={mutant['simulation_log']}，SHA-256={mutant['simulation_log_sha256']}。"),
    })
    for item in checker_runs:
        status = "PASS" if item["exit_code"] == 0 and item["status"] == "CHECKS_OK" else "FAIL"
        check = {"name": "check-stage-delivery-" + item["mode"], "status": status,
                 "command": item["command"], "exit_code": item["exit_code"]}
        if status != "PASS":
            check["reason"] = "交付清单核验未返回CHECKS_OK，详见validation.json原始输出。"
        else:
            check["reason"] = ("运行器执行此schema-v1模式返回CHECKS_OK；生成最终manifest后再次执行相同模式，"
                               "并要求最终状态仍为CHECKS_OK；本轮核验的输入manifest SHA-256=" + item["manifest_sha256"])
        checks.append(check)
    manifest = {
        "schema_version": 1,
        "stage": "2B",
        "task_id": "S2B-T19",
        "run_id": run_id,
        "source_commit": report["source_commit"],
        "evidence_dir": (evidence.relative_to(ROOT).as_posix()),
        "interfaces": [{
            "name": "tiny416冻结模型数值及逻辑接口",
            "version": T01_INTERFACE_VERSION,
            "frozen": True,
            "path": T01_INTERFACE_PATH,
            "sha256": interface_sha,
        }],
        "tool_versions": {
            "python": platform.python_version(),
            "verilator": report["tool_versions"]["verilator"],
            "check_stage_delivery": "schema-v1",
            "platform": platform.platform(),
        },
        "files": delivery_file_entries(evidence, evidence / "delivery_manifest.json", report),
        "checks": checks,
        "limitations": [
            "本证据只覆盖离线RTL geometry和POOL/upsample引擎回归，不能作为综合或时序收敛结论。",
            "本次未运行Vivado、STA、完整网络仿真或任何实物板卡测试。",
            "实际源提交、T19来源基线和引擎比较基线的含义与哈希前后核对记录位于validation.json。",
        ],
    }
    return manifest


def main():
    """新运行不覆盖；记录原生退出码、源码快照、资源、夹具和检查器结果。"""
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--toolchain", type=Path, default=Path(r"D:\FPGA_S2A_MSYS2_20261001\env"))
    args = ap.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.run_id):
        ap.error("RunId非法")
    run_work = ROOT / "tmp/2B/S2B-T19" / args.run_id
    work = run_work / "rtl_run"
    evidence = ROOT / "report/evidence/S2B-T19" / args.run_id
    for parent in (run_work.parent, evidence.parent):
        if not parent.is_dir() or parent.is_symlink():
            ap.error("精确父目录不可用")
    if run_work.exists() or evidence.exists():
        ap.error("RunId已存在")
    run_work.mkdir()
    work.mkdir()
    evidence.mkdir()
    start = time.monotonic()
    report = dict(
        task_id="S2B-T19", run_id=args.run_id, status="FAIL", source_commit=SOURCE_BASELINE,
        seed=SEED, runs=[], sta="NOT_RUN", g3="NOT_RUN", independent_review="NOT_RUN",
        invocation={"argv": [sys.executable, *sys.argv]},
        tool_versions={"python": sys.version, "verilator": "NOT_QUERIED"},
        resource_budget=dict(jobs=1, threads=1, rss_limit_bytes=1073741824,
                             available_ram_min_bytes=RAM_LIMIT_BYTES, disk_free_min_bytes=1073741824),
        cache_budget={"work_limit_bytes": WORK_CACHE_LIMIT_BYTES,
                      "evidence_limit_bytes": EVIDENCE_LIMIT_BYTES,
                      "directory_sample_period_seconds": 1.0,
                      "observed_peak_rtl_run_bytes": 0,
                      "observed_peak_evidence_bytes": 0, "removals": []},
        simulation_passes={}, limitations=[
            "通用U32几何以独立无限精度黄金和固定种子向量验证；三种固定shape的合法channel/y/x组合逐一穷举。",
            "三种FAST_FIXED_POOL_SHAPE各自逐字段拒绝八种参数不匹配，并逐项核验BAD_ARGUMENT及全部输出清零。",
            "三种固定shape各含精确U32末地址合法边界与越界相邻用例；POOL/upsample使用完整差分向量。",
            "未运行Vivado、综合、STA、整网或实板；原继承WIDTH/UNUSED诊断保留-Wall/-Wno-fatal，不接受LATCH/UNOPTFLAT/MULTIDRIVEN。",
        ])
    manifest_path = evidence / "delivery_manifest.json"
    final_checker_runs = []
    try:
        actual = subprocess.check_output(
            ["git", "-c", "core.longpaths=true", "-c", "maintenance.auto=false", "rev-parse", "HEAD"],
            cwd=ROOT, text=True).strip()
        report["source_commit"] = actual
        report["task_source_baseline_commit"] = SOURCE_BASELINE
        report["task_source_baseline_meaning"] = "T19源码任务来源闭包基线；用于确认已绑定RTL/runner没有基线后提交变化。"
        report["rtl_engine_comparison_baseline_commit"] = BASELINE
        report["rtl_engine_comparison_baseline_meaning"] = "用于核对POOL引擎固定geometry接入及编译期shape特化差异。"
        if actual != EXPECTED_HEAD:
            raise ValueError("当前HEAD与冻结R08基线不符：" + actual)
        ancestor = subprocess.run(
            ["git", "-c", "core.longpaths=true", "-c", "maintenance.auto=false", "merge-base",
             "--is-ancestor", SOURCE_BASELINE, actual], cwd=ROOT, check=False)
        report["native_preflight_exit_codes"] = {"git_merge_base_is_ancestor": ancestor.returncode}
        if ancestor.returncode != 0:
            raise ValueError("T19源码任务基线不是当前HEAD的祖先")
        checker = backend.load_checker()
        install_sandbox_path_probe(checker, report)
        bindings = checker.check_static(ROOT)
        committed_paths = set(subprocess.check_output(
            ["git", "-c", "core.longpaths=true", "-c", "maintenance.auto=false", "diff",
             "--name-only", SOURCE_BASELINE, actual], cwd=ROOT, text=True).splitlines())
        t19_committed_changes = subprocess.check_output(
            ["git", "-c", "core.longpaths=true", "-c", "maintenance.auto=false", "diff",
             "--name-only", SOURCE_BASELINE, actual, "--", *bindings], cwd=ROOT, text=True).splitlines()
        outside_t19_scope = committed_paths - set(bindings)
        if t19_committed_changes:
            raise ValueError("T19源码绑定路径在任务基线后已有提交变化：" + repr(t19_committed_changes))
        if outside_t19_scope != T18_COMMITTED_PATH_ALLOWLIST:
            raise ValueError("T19基线外提交路径不符合已知T18清单：" + repr(sorted(outside_t19_scope)))
        untracked_bound = subprocess.check_output(
            ["git", "-c", "core.longpaths=true", "-c", "maintenance.auto=false", "ls-files",
             "--others", "--exclude-standard", "--", *bindings], cwd=ROOT, text=True).splitlines()
        if untracked_bound:
            raise ValueError("T19绑定路径包含未跟踪文件：" + repr(untracked_bound))
        report["t19_source_path_allowlist"] = sorted(bindings)
        report["committed_source_changes_since_task_baseline"] = t19_committed_changes
        report["unrelated_t18_paths_outside_t19_allowlist"] = sorted(outside_t19_scope)
        report["source_worktree_status"] = subprocess.check_output(
            ["git", "-c", "core.longpaths=true", "-c", "maintenance.auto=false", "status", "--short",
             "--untracked-files=all", "--", *bindings], cwd=ROOT, text=True).splitlines()
        for relative in (RUNNER, engine.RUNNER, backend.RUNNER, backend.MODEL):
            bindings[relative] = backend.sha(ROOT / relative)
        report["source_sha256_pre"] = dict(bindings)
        report["frozen14_sha256_pre"] = {path: backend.sha(ROOT / path)
                                         for path in checker.FROZEN_CORE_SHA256}
        if backend.sha(ROOT / "src/s2b_maxpool_engine.sv") != bindings["src/s2b_maxpool_engine.sv"]:
            raise ValueError("MaxPool engine源码绑定SHA不一致")
        old = subprocess.check_output(
            ["git", "-c", "core.longpaths=true", "-c", "maintenance.auto=false", "show",
             BASELINE + ":src/s2b_maxpool_engine.sv"], cwd=ROOT).decode("utf-8")
        current = (ROOT / "src/s2b_maxpool_engine.sv").read_text(encoding="utf-8")
        expected = old.replace("int8_maxpool_geometry u_geometry", "s2b_maxpool_geometry u_geometry")
        for before, after in checker.POOL_FIXED_GEOMETRY_REPLACEMENTS:
            if expected.count(before) != 1:
                raise ValueError("POOL固定geometry差异锚点不唯一")
            expected = expected.replace(before, after)
        for before, after in checker.FAST_FIXED_POOL_ENGINE_REPLACEMENTS:
            if expected.count(before) != 1:
                raise ValueError("POOL快路径差异锚点不唯一")
            expected = expected.replace(before, after)
        if current != expected or current.split("    always_ff", 1)[1] != old.split("    always_ff", 1)[1]:
            raise ValueError("POOL引擎与预期固定geometry结构不符")
        report["engine_structure"] = dict(
            only_change="geometry常量实例/选择、三种固定形状编译期参数及64位输出偏移；全部always_ff不变",
            always_ff_sha256=hashlib.sha256(current.split("    always_ff", 1)[1].encode()).hexdigest())
        report["resource_preflight"] = resource_preflight(work)
        if (report["resource_preflight"]["available_ram_bytes"] < RAM_LIMIT_BYTES or
                report["resource_preflight"]["disk_free_bytes"] < 1073741824 or
                report["resource_preflight"]["running_tools"]):
            raise ValueError("资源硬门槛或重型进程预检未通过")
        report["checker_semantic_mutants"] = mutants(checker, work, bindings)
        report["checker_public_negatives"] = engine.checker_negatives(checker, work, bindings)
        rows, report["geometry_coverage"] = cases()
        geometry_data = "\n".join(" ".join(f"{n:x}" for n in (*values, *gold))
                                   for values, gold in rows) + "\n"
        (evidence / "geometry_vectors.dat").write_text(geometry_data, encoding="utf-8", newline="\n")
        fixed_data, report["fixed_geometry_coverage"] = fixed_shape_vectors()
        (evidence / "fixed_pool_geometry_vectors.dat").write_text(fixed_data, encoding="utf-8", newline="\n")
        geometry_testbench = geometry_tb()
        fixed_testbench = fixed_geometry_tb()
        for directory in (work, evidence):
            (directory / "tb_s8_geometry.sv").write_text(geometry_testbench, encoding="utf-8", newline="\n")
            (directory / "tb_s2b_fixed_pool_geometry.sv").write_text(fixed_testbench, encoding="utf-8", newline="\n")
        model = json.loads((ROOT / backend.MODEL).read_text(encoding="utf-8"))
        if backend.sha(ROOT / backend.MODEL) != backend.MODEL_SHA:
            raise ValueError("模型清单SHA与固定值不符")
        declarations = {"pool": engine.ports(ROOT / "src/s2a_maxpool_engine.sv"),
                        "upsample": engine.ports(ROOT / "src/s2a_upsample_engine.sv")}
        report["engine_coverage"] = {}
        for kind in declarations:
            vector_data, counts = engine.vector_data(kind, declarations[kind], model)
            report["engine_coverage"][kind] = counts
            for directory in (work, evidence):
                (directory / (kind + "_vectors.dat")).write_text(
                    vector_data, encoding="utf-8", newline="\n")
        engine_testbench = bind_engine_vector_paths(engine_tb(declarations, model), evidence)
        for directory in (work, evidence):
            (directory / "tb_s2b_geometry_specialization.sv").write_text(
                engine_testbench, encoding="utf-8", newline="\n")
        fixture_consumers = {
            "tb_s8_geometry.sv": "geometry_compile command source argument",
            "tb_s2b_fixed_pool_geometry.sv": "fixed_geometry_compile command source argument and semantic mutant simulation",
            "tb_s2b_geometry_specialization.sv": "engine_compile command source argument",
            "geometry_vectors.dat": "geometry_simulation VECTOR_PATH plusarg",
            "fixed_pool_geometry_vectors.dat": "fixed_geometry_simulation and semantic mutant VECTOR_PATH plusarg",
            "pool_vectors.dat": "engine testbench $fopen absolute evidence path",
            "upsample_vectors.dat": "engine testbench $fopen absolute evidence path",
        }
        report["fixture_bindings"] = []
        for name in FIXTURE_NAMES:
            path = evidence / name
            if not path.is_file() or path.is_symlink():
                raise ValueError("仿真夹具缺失或不是普通文件：" + str(path))
            report["fixture_bindings"].append({
                "path": path.relative_to(ROOT).as_posix(),
                "absolute_path": str(path.resolve()),
                "sha256": backend.sha(path),
                "consumed_by": fixture_consumers[name],
            })
        source = work / "source"
        source.mkdir()
        snapshot = evidence / "source_snapshot"
        snapshot.mkdir()
        for relative in bindings:
            target = snapshot / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        for relative in engine.RTL:
            shutil.copyfile(ROOT / relative, source / Path(relative).name)
        env = os.environ.copy()
        binary_directory = args.toolchain / "mingw64/bin"
        utility_directory = args.toolchain / "usr/bin"
        env["PATH"] = str(utility_directory) + os.pathsep + str(binary_directory) + os.pathsep + env.get("PATH", "")
        env["VERILATOR_ROOT"] = str(args.toolchain / "mingw64/share/verilator")
        env["PYTHONUTF8"] = "1"
        verilator = binary_directory / "verilator_bin.exe"
        for tool in (verilator, binary_directory / "g++.exe", utility_directory / "make.exe"):
            checker.exact_file(tool)
        report["tool_versions"] = {
            "python": sys.version,
            "verilator": subprocess.check_output([str(verilator), "--version"], env=env,
                                                  text=True, timeout=30).strip(),
            "g++": subprocess.check_output([str(binary_directory / "g++.exe"), "--version"], env=env,
                                            text=True, timeout=30).splitlines()[0],
            "make": subprocess.check_output([str(utility_directory / "make.exe"), "--version"], env=env,
                                             text=True, timeout=30).splitlines()[0],
        }
        common = [str(verilator), "--binary", "--timing", "--timescale", "1ns/1ps", "-Wall", "-Wno-fatal",
                  "-j", "1", "--threads", "1", "--output-split", "10000", "--output-split-cfuncs", "100",
                  "-MAKEFLAGS", "PYTHON3='\"" + sys.executable + "\"'", "-CFLAGS",
                  "-D_GLIBCXX_USE_CXX11_ABI=0 -O1"]
        evidence_tests = {name: str((evidence / name).resolve()) for name in FIXTURE_NAMES
                          if name.endswith(".sv")}
        build_cases = (
            ("geometry", "tb_s8_geometry", ["source/int8_maxpool_geometry.sv",
             "source/s2b_maxpool_geometry.sv", evidence_tests["tb_s8_geometry.sv"]]),
            ("fixed_geometry", "tb_s2b_fixed_pool_geometry", ["source/s2b_maxpool_geometry.sv",
             evidence_tests["tb_s2b_fixed_pool_geometry.sv"]]),
            ("engine", "tb_s2b_geometry_specialization", ["source/" + Path(path).name for path in engine.RTL] +
             [evidence_tests["tb_s2b_geometry_specialization.sv"]]),
        )
        for label, top, files in build_cases:
            command = common + ["--top-module", top, "--Mdir", "obj_" + label, *files]
            engine.execute(label + "_compile", command, work, evidence, env, report, 600)
            compile_log = (evidence / (label + "_compile.log")).read_text(encoding="utf-8")
            warnings = re.findall(r"%Warning-(?:LATCH|UNOPTFLAT|MULTIDRIVEN).*", compile_log)
            if warnings:
                raise ValueError(label + "编译出现禁止诊断：" + repr(warnings))
            vector_file = "geometry_vectors.dat" if label == "geometry" else "fixed_pool_geometry_vectors.dat"
            vector_args = ["+VECTOR_PATH=" + str((evidence / vector_file).resolve())] \
                if label in ("geometry", "fixed_geometry") else []
            engine.execute(label + "_simulation",
                           [str(work / ("obj_" + label) / ("V" + top + ".exe")), *vector_args],
                           work, evidence, env, report, 600)
            simulation_log = (evidence / (label + "_simulation.log")).read_text(encoding="utf-8")
            if label == "geometry":
                matches = re.findall(r"PASS S8_GEOMETRY vectors=(\d+)", simulation_log)
                if matches != [str(len(rows))]:
                    raise ValueError("通用几何PASS标记或向量计数不符")
                marker = matches[0]
            elif label == "fixed_geometry":
                matches = re.findall(r"PASS FIXED_POOL_GEOMETRY vectors=(\d+) guards=(\d+)", simulation_log)
                if (matches != [(str(report["fixed_geometry_coverage"]["vectors"]), "24")] or
                        "FAST_FIXED_POOL_GUARD_REJECTIONS cases=24 shapes=3 fields_per_shape=8" not in simulation_log):
                    raise ValueError("固定geometry向量或24个逐字段守卫拒绝计数不符")
                report["fast_guard_parameter_rejections"] = {
                    "shape_count": 3, "fields_per_shape": 8, "case_count": 24,
                    "fields": ["input_channels", "input_height", "input_width", "kernel_height",
                               "kernel_width", "stride_y", "stride_x", "darknet_padding_parameter"],
                    "result": "每例均断言BAD_ARGUMENT且所有输出字段清零",
                    "legal_address_boundary_per_shape": 1,
                    "log": (evidence / "fixed_geometry_simulation.log").relative_to(ROOT).as_posix(),
                    "log_sha256": backend.sha(evidence / "fixed_geometry_simulation.log"),
                }
                marker = matches[0][0] + "/guards=" + matches[0][1]
            else:
                matches = re.findall(
                    r"PASS GEOMETRY_SPECIALIZATION pool=(\d+) upsample=(\d+) cycles=(\d+) pool_abort=(\d+) upsample_abort=(\d+)",
                    simulation_log)
                if len(matches) != 1:
                    raise ValueError("缺少唯一真实引擎PASS标记")
                counts = dict(zip(("pool", "upsample", "cycles", "pool_abort", "upsample_abort"),
                                  map(int, matches[0])))
                if (counts["pool"] != report["engine_coverage"]["pool"]["vectors"] or
                        counts["upsample"] != report["engine_coverage"]["upsample"]["vectors"]):
                    raise ValueError("真实引擎POOL/upsample向量计数不符")
                if counts["pool_abort"] != 127 or counts["upsample_abort"] != 63 or \
                        "RESET_COVERAGE pool=127 upsample=63" not in simulation_log:
                    raise ValueError("真实引擎abort或硬复位覆盖不完整")
                report["engine_simulation_counts"] = counts
                marker = "/".join(matches[0])
            pass_evidence = {"passed": True, "marker": marker}
            report["simulation_passes"][label] = pass_evidence
            cleanup_passed_cache(work, evidence, args.run_id, label, report, pass_evidence)

        run_fast_guard_mutant(work, evidence, verilator, common, env, report)
        report["source_sha256_post"] = {path: backend.sha(ROOT / path) for path in bindings}
        if report["source_sha256_post"] != bindings:
            raise ValueError("验证期间源码变化")
        report["frozen14_sha256_post"] = {path: backend.sha(ROOT / path)
                                          for path in checker.FROZEN_CORE_SHA256}
        if report["frozen14_sha256_pre"] != report["frozen14_sha256_post"]:
            raise ValueError("验证期间冻结2A原件变化")
        report["status"] = "PASS_MAXPOOL_ADDRESS_GUARD_G1"
    except Exception as exc:
        report["status"] = "FAIL"
        report["failure"] = repr(exc)
        report["failure_traceback"] = traceback.format_exc()

    if report["status"] == "PASS_MAXPOOL_ADDRESS_GUARD_G1":
        try:
            report["seconds"] = round(time.monotonic() - start, 3)
            validation_path = evidence / "validation.json"
            validation_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                                       encoding="utf-8", newline="\n")
            manifest = build_delivery_manifest(evidence, args.run_id, report, [])
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                     encoding="utf-8", newline="\n")
            initial_runs = [run_delivery_checker(mode, manifest_path) for mode in ("inputs", "evidence")]
            for result in initial_runs:
                (evidence / ("delivery_checker_" + result["mode"] + ".log")).write_text(
                    result["stdout"] + "\nSTDERR:\n" + result["stderr"] + "\n",
                    encoding="utf-8", newline="\n")
            for result in initial_runs:
                result["log"] = (evidence / ("delivery_checker_" + result["mode"] + ".log")).relative_to(ROOT).as_posix()
                result["log_sha256"] = backend.sha(evidence / ("delivery_checker_" + result["mode"] + ".log"))
            report["delivery_checker_runs"] = initial_runs
            if any(item["exit_code"] != 0 or item["status"] != "CHECKS_OK" for item in initial_runs):
                raise ValueError("初次inputs/evidence阶段清单核验未全部返回CHECKS_OK")
            report["seconds"] = round(time.monotonic() - start, 3)
            validation_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                                       encoding="utf-8", newline="\n")
            manifest = build_delivery_manifest(evidence, args.run_id, report, initial_runs)
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                     encoding="utf-8", newline="\n")
            final_checker_runs = [run_delivery_checker(mode, manifest_path) for mode in ("inputs", "evidence")]
            for result in final_checker_runs:
                if result["exit_code"] != 0 or result["status"] != "CHECKS_OK":
                    raise ValueError("最终manifest的" + result["mode"] + "模式核验未通过：" + result["stdout"])
        except Exception as exc:
            report["status"] = "FAIL"
            report["failure"] = "delivery packaging: " + repr(exc)
            report["failure_traceback"] = traceback.format_exc()
            report["seconds"] = round(time.monotonic() - start, 3)
            (evidence / "validation.json").write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    else:
        report["seconds"] = round(time.monotonic() - start, 3)
        (evidence / "validation.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    summary = {key: report.get(key) for key in (
        "status", "seconds", "geometry_coverage", "fixed_geometry_coverage",
        "fast_guard_parameter_rejections", "fast_guard_semantic_mutants",
        "engine_simulation_counts", "cache_budget", "failure")}
    summary["delivery_checker_final_runs"] = final_checker_runs
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    return 0 if report["status"] == "PASS_MAXPOOL_ADDRESS_GUARD_G1" else 1


if __name__=="__main__":
    raise SystemExit(main())
