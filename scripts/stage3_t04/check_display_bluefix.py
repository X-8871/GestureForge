#!/usr/bin/env python3
"""显示蓝字段修正的只读穷举、隔离补丁验证和新运行准备工具。"""

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone, timedelta


WT = Path("D:/codex-worktrees/dbdf")
BASELINE = "d476df8db21614df35bb3ccb11843b1beca88212"
RUN_NAME = "t04_display_bluefix_20261021_r01"
EVID_NAME = "t05_display_bluefix_20261021_r01"
VENDOR = WT / "tmp/stage3_reference/AX7020_2023.1/course_s2_vitis/22_ov5640_single/Vivado/auto_create_project"
RTL = Path("my_ip/ov5640_ip/src/alinx_ov5640.v")
SOF = WT / "board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch"
BLUE = WT / "board/stage3/software/sensor/alinx_ov5640_display_blue_rebuild.patch"
XDC = WT / "board/stage3/hardware/an5642_j11_cmos2.xdc"
TCL = WT / "scripts/stage3_t04/build_t04_camera.tcl"
LAUNCHER = WT / "scripts/stage3_t04/run_t04_camera_display_bluefix_build.sh"
SIGNAL = "s_axis_tdata_display_bluefix"
EXPRESSION = "{s_axis_tdata[14:11],s_axis_tdata[14],s_axis_tdata[10:0]}"
PRISTINE_SHA = "98260b62f996ec700eb766c6c4e57706b2c1ff3a8224a5105a3641b6475b3e4d"
SOF_RTL_SHA = "db4857fe2fc8d86aa831bac619ddfc676d076f0114ba2c07988d944f894adce6"
PINS = {
    SOF: "fd854a622b52c32a43a6770be3f583cce29864a764845c313b623514c91ab2c5",
    TCL: "1f666b4a7ea8ce09c59d6e08471e76028dca53c6d73fe7a9f57006c98c16983c",
    XDC: "2dae928c9458a71ebc9ae741e71f7a274c18afc237676852c53d5e61bbeff5b2",
}


class ResourceBlocked(RuntimeError):
    """物理内存或提交空间不足，使用独立退出码 4。"""


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def plain_path(path, directory=False):
    """拒绝链接及重解析祖先，避免固定路径实际指向其他树。"""
    require(path.is_dir() if directory else path.is_file(), f"目标类型或路径错误: {path}")
    for part in (path, *path.parents):
        info = part.lstat()
        require(not part.is_symlink() and not (getattr(info, "st_file_attributes", 0) & 0x400),
                f"不允许链接或重解析路径: {part}")
    return path


def command(args, cwd=WT):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", timeout=30)
    require(result.returncode == 0, f"命令失败 rc={result.returncode}: {args}\n{result.stdout}{result.stderr}")
    return result.stdout.strip()


def identity():
    plain_path(WT, directory=True)
    require(Path(__file__).resolve() == (WT / "scripts/stage3_t04/check_display_bluefix.py").resolve(),
            "检查器必须来自指定工作树")
    require(Path(command(["git", "rev-parse", "--show-toplevel"])).resolve() == WT.resolve(), "工作树错误")
    require(command(["git", "rev-parse", "HEAD"]) == BASELINE, "HEAD 不等于任务基线")
    lock = Path(command(["git", "rev-parse", "--git-path", "index.lock"]))
    if not lock.is_absolute():
        lock = WT / lock
    require(not os.path.lexists(lock), "存在 index.lock")
    for path, expected in PINS.items():
        require(sha(plain_path(path)) == expected, f"输入身份不符: {path}")
    for path in (BLUE, LAUNCHER, Path(__file__)):
        plain_path(path)
    require(sha(plain_path(VENDOR / RTL)) == PRISTINE_SHA, "厂商原件哈希不符")


def concat_evaluator(expression):
    """按补丁中的通用 Verilog 拼接语法解释位段，而非另抄修复公式。"""
    require(expression.startswith("{") and expression.endswith("}"), "表达式不是拼接")
    fields = []
    for token in expression[1:-1].split(","):
        match = re.fullmatch(r"s_axis_tdata\[(\d+)(?::(\d+))?\]", token.strip())
        require(match is not None, f"不支持的位段: {token}")
        high = int(match[1])
        low = int(match[2]) if match[2] is not None else high
        require(0 <= low <= high < 16, "位段越界")
        fields.append((low, high - low + 1))
    require(sum(width for _, width in fields) == 16, "拼接总宽度错误")

    def evaluate(word):
        value = 0
        for low, width in fields:
            value = (value << width) | ((word >> low) & ((1 << width) - 1))
        return value

    return evaluate


def selftest():
    """只读所有输入，仅向标准输出报告，不创建临时文件。"""
    patch = BLUE.read_text(encoding="utf-8")
    target = RTL.as_posix()
    require(patch.count("diff --git ") == 1
            and patch.startswith(f"diff --git a/{target} b/{target}\n--- a/{target}\n+++ b/{target}\n"),
            "补丁只能修改指定厂商 RTL")
    matches = re.findall(r"^\+wire\[15:0\]\s+" + SIGNAL + r"\s*=\s*(\{[^;]+\});$", patch, re.M)
    require(matches == [EXPRESSION], "补丁必须包含唯一指定表达式")
    evaluate = concat_evaluator(matches[0])
    display_levels = set()
    for word in range(65536):
        actual = evaluate(word)
        b = word // 2048
        expected_b = 2 * (b % 16) + (b % 16) // 8
        require(actual // 2048 == expected_b, f"高五位数学参考不符: {word}")
        require(actual % 2048 == word % 2048, f"低十一位改变: {word}")
        require((actual // 32) % 64 == (word // 32) % 64, f"显示 G 改变: {word}")
        require(actual % 32 == word % 32, f"显示 R 改变: {word}")
        require(actual == evaluate(word ^ 32768), "丢失位仍参与重建")
        display_levels.add((actual // 2048) * 8)
    require(sorted(display_levels) == [0, 16, 32, 48, 64, 80, 96, 112, 136, 152, 168, 184, 200, 216, 232, 248],
            "显示蓝量化档不符")
    print(json.dumps({"selftest": "PASS", "words": 65536, "blue_levels": sorted(display_levels),
                      "patch_sha256": sha(BLUE), "meaning": "近似拉伸，不能恢复真实丢位"}, ensure_ascii=False))


def patch_transport(source, target):
    """正式补丁经工具编辑；仅在隔离目录给内容行补 CR，匹配厂商 CRLF。"""
    lines = source.read_bytes().decode("utf-8").splitlines()
    body = False
    result = []
    for line in lines:
        if line.startswith("@@ "):
            body = True
        elif line.startswith("diff --git "):
            body = False
        ending = "\r\n" if body and line.startswith((" ", "+", "-")) else "\n"
        result.append(line + ending)
    with target.open("xb") as stream:
        stream.write("".join(result).encode("utf-8"))
    print(f"PATCH_TRANSPORT source_sha256={sha(source)} applied_sha256={sha(target)}")


def apply_patches(source_root, transport_root):
    rtl = source_root / RTL
    require(sha(rtl) == PRISTINE_SHA, "只能从厂商原件开始")
    original = rtl.read_bytes()
    require(original.count(b"\n") == original.count(b"\r\n"), "原件不是纯 CRLF")
    hashes = {"pristine": sha(rtl)}
    for name, patch in (("sof", SOF), ("display_blue", BLUE)):
        normalized = transport_root / (name + ".patch")
        patch_transport(patch, normalized)
        args = ["git", "apply", "--whitespace=nowarn", "-p1",
                "--directory=" + source_root.relative_to(WT).as_posix()]
        command(args + ["--check", str(normalized)])
        print(f"GIT_APPLY {name} --check rc=0")
        command(args + [str(normalized)])
        print(f"GIT_APPLY {name} apply rc=0")
        hashes[name] = sha(rtl)
        if name == "sof":
            require(hashes[name] == SOF_RTL_SHA, "SOF 后身份错误")
            after_sof = rtl.read_bytes()
    fixed = rtl.read_bytes()
    text = fixed.decode("utf-8")
    declaration = "wire[15:0] " + SIGNAL + "=" + EXPRESSION + ";"
    require(text.count(declaration) == 1 and text.count(SIGNAL) == 2, "表达式或引用不唯一")
    require(text.count(".din              ({" + SIGNAL + ",s_axis_tlast,s_axis_tuser}),") == 1,
            "FIFO 数据或侧带接线错误")
    require("s_axis_tdata_bluefix" not in text, "包含旧低五位修复")
    require(fixed.count(b"\n") == fixed.count(b"\r\n"), "补丁破坏 CRLF")
    added = [line[1:] for line in BLUE.read_text(encoding="utf-8").splitlines()
             if line.startswith("+") and not line.startswith("+++")]
    insertion = ("\r\n".join(added[:3]) + "\r\n").encode("utf-8")
    restored = fixed.replace(insertion, b"", 1).replace(
        (".din              ({" + SIGNAL + ",s_axis_tlast,s_axis_tuser}),").encode(),
        b".din              ({s_axis_tdata,s_axis_tlast,s_axis_tuser}),", 1)
    require(restored == after_sof, "除声明和 FIFO 数据外仍有变更（含侧带、时钟或 ILA）")
    print(json.dumps({"patch_check": "PASS", "rtl_sha256": hashes, "crlf_preserved": True}))
    return hashes


def tree_hashes(root):
    plain_path(root, directory=True)
    result = {}
    for path in sorted(root.rglob("*")):
        require(not path.is_symlink() and not (getattr(path.lstat(), "st_file_attributes", 0) & 0x400),
                f"树中存在链接: {path}")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = sha(path)
    return result


def input_hashes():
    return {str(path): sha(path) for path in (SOF, BLUE, XDC, TCL, LAUNCHER, Path(__file__), Path(sys.executable))}


def run_paths(name):
    require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", name) is not None, "run_name 必须是简单标识符")
    require(name == RUN_NAME, "本任务仅允许指定的新 RunId")
    run_parent = plain_path(WT / "tmp/s3r06", directory=True)
    evid_parent = plain_path(WT / "report/evidence/S3-T05", directory=True)
    return run_parent / name, evid_parent / EVID_NAME


def no_heavy_processes():
    # 只读进程名和 PID；枚举失败或出现重型/硬件服务进程均停止，不打印命令行或环境。
    script = ("$ErrorActionPreference='Stop'; "
              "$p=@(Get-Process -ErrorAction Stop | Where-Object { "
              "$_.ProcessName -match '^(vivado|xsim|xsimk|xelab|xvhdl|xvlog|rdiArgs|loader|vitis|vitis_hls|v\\+\\+|hw_server)$' }); "
              "$p | ForEach-Object { Write-Output ($_.ProcessName + ':' + $_.Id) }; "
              "if ($p.Count -gt 0) { exit 3 }")
    command(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script])
    print("HEAVY_PROCESS_CHECK=PASS")


def memory_check():
    """只读 Windows 实时可用物理内存，不终止任何进程。"""
    class MemoryStatus(ctypes.Structure):
        _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong),
                    ("total_physical", ctypes.c_ulonglong), ("available_physical", ctypes.c_ulonglong),
                    ("total_page", ctypes.c_ulonglong), ("available_page", ctypes.c_ulonglong),
                    ("total_virtual", ctypes.c_ulonglong), ("available_virtual", ctypes.c_ulonglong),
                    ("available_extended", ctypes.c_ulonglong)]

    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    api = ctypes.WinDLL("kernel32", use_last_error=True).GlobalMemoryStatusEx
    api.argtypes = [ctypes.POINTER(MemoryStatus)]
    api.restype = ctypes.c_int
    require(api(ctypes.byref(status)) != 0, "无法读取可用物理内存")
    thresholds = []
    for key, default, available in (("S3_MIN_AVAILABLE_MB", 2048, status.available_physical),
                                    ("S3_MIN_COMMIT_MB", 8192, status.available_page)):
        raw = os.environ.get(key, str(default))
        require(re.fullmatch(r"[1-9][0-9]{0,8}", raw) is not None, f"{key} 必须是明确的正整数 MiB")
        minimum = int(raw) * 1024 ** 2
        thresholds.append(available >= minimum)
        print(f"RESOURCE {key}={raw} AVAILABLE_BYTES={available} MINIMUM_BYTES={minimum}")
    if not all(thresholds):
        raise ResourceBlocked("RESOURCE_BLOCKED: 可用物理内存或提交空间不足；未启动构建，不自动停止其他进程")


def preflight(name):
    run, evid = run_paths(name)
    require(not os.path.lexists(run), "运行目录已存在")
    require(not os.path.lexists(evid), "证据目录已存在")
    no_heavy_processes()
    memory_check()
    print("PREFLIGHT=PASS")


def save_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def prepare(name):
    run, evid = run_paths(name)
    plain_path(run, directory=True)
    plain_path(evid, directory=True)
    plain_path(run / "temp", directory=True)
    require({p.name for p in run.iterdir()} == {"temp"}, "运行目录必须只有空 temp")
    require(not any((run / "temp").iterdir()) and not any(evid.iterdir()), "运行或证据目录非空")
    no_heavy_processes()
    memory_check()
    require(os.environ.get("S3_BUILD_JOBS") == "1", "新 launcher 必须指定 S3_BUILD_JOBS=1")
    sources_before = tree_hashes(VENDOR)
    before = input_hashes()
    shutil.copytree(VENDOR, run / "vendor_src")
    require(tree_hashes(run / "vendor_src") == sources_before, "厂商副本身份不符")
    hashes = apply_patches(run / "vendor_src", run / "temp")
    shutil.copyfile(XDC, run / "vendor_src/src/constraints/an5642.xdc")
    prepared = tree_hashes(run / "vendor_src")
    require(prepared["src/constraints/an5642.xdc"] == PINS[XDC], "J11 CMOS2 约束身份错误")
    expected = dict(sources_before)
    expected[RTL.as_posix()] = hashes["display_blue"]
    expected["src/constraints/an5642.xdc"] = PINS[XDC]
    require(prepared == expected, "厂商副本出现非授权差异")
    require(tree_hashes(VENDOR) == sources_before and input_hashes() == before, "准备期间输入改变")
    save_json(run / "prepare_manifest.json", {
        "baseline": BASELINE, "run_name": name, "evidence": str(evid),
        "inputs_sha256": before, "vendor_files_sha256": sources_before,
        "prepared_files_sha256": prepared, "rtl_sha256": hashes,
        "debug_ov5640": False, "jobs": 1,
        "meaning": "只对显示 B 高五位做近似重建，低十一位不变；不恢复真实丢位",
    })
    print(f"PREPARE=PASS manifest_sha256={sha(run / 'prepare_manifest.json')}")


def finalize(name, exit_code, console_exit_code):
    run, evid = run_paths(name)
    plain_path(run, directory=True)
    plain_path(evid, directory=True)
    manifest = json.loads((run / "prepare_manifest.json").read_text(encoding="utf-8"))
    require(manifest["baseline"] == BASELINE and manifest["run_name"] == name, "准备清单身份错误")
    stable = input_hashes() == manifest["inputs_sha256"]
    stable = stable and tree_hashes(VENDOR) == manifest["vendor_files_sha256"]
    stable = stable and tree_hashes(run / "vendor_src") == manifest["prepared_files_sha256"]
    for path in sorted(run.glob("report_*.rpt")) + [run / "vivado.log", run / "vivado.jou"]:
        if path.is_file():
            target = evid / (path.name + ".txt")
            with target.open("xb") as stream:
                stream.write(path.read_bytes())
    copies = sorted((run / "project").glob("*.gen/sources_1/bd/*/ipshared/*/src/alinx_ov5640.v"))
    expected = manifest["rtl_sha256"]["display_blue"]
    copy_hashes = {str(path): sha(path) for path in copies}
    log = (run / "vivado.log").read_text(encoding="utf-8", errors="replace") if (run / "vivado.log").is_file() else ""
    success = (exit_code == 0 and console_exit_code == 0 and stable
               and bool(copies) and all(h == expected for h in copy_hashes.values())
               and (run / "project/ov5640_single.runs/impl_1/design_1_wrapper.bit").is_file()
               and (run / "design_1_wrapper.xsa").is_file() and "T04: ALL_DONE=1" in log
               and "T04: BUILD_JOBS=1" in log
               and "T04: ILA_DISABLED_DEBUG_OV5640=false" in log)
    report = {
        "status": "BUILD_COMPLETE" if success else "FAILED", "vivado_exit_code": exit_code,
        "console_exit_code": console_exit_code,
        "time_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "inputs_stable": stable, "prepare": manifest, "generated_rtl_sha256": copy_hashes,
        "run_files_sha256": tree_hashes(run), "evidence_files_sha256": tree_hashes(evid),
        "limitations": ["近似重建，不恢复真实丢位", "未上板、未烧录、未做显示效果验收",
                        "源副本哈希相同不单独证明综合网表语义正确", "未做 RTL 仿真或独立 Review"],
    }
    save_json(evid / "build_report.json", report)
    print(f"STATUS={report['status']} REPORT_SHA256={sha(evid / 'build_report.json')}")
    require(success, "构建或输入/产物身份核验未通过；见新证据清单")


def main():
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    for name in ("selftest", "check-patch", "preflight", "check-heavy", "prepare", "finalize"):
        modes.add_argument("--" + name, action="store_true")
    parser.add_argument("--run-name", default=RUN_NAME)
    parser.add_argument("--exit-code", type=int)
    parser.add_argument("--console-exit-code", type=int, default=0)
    args = parser.parse_args()
    identity()
    if args.selftest:
        selftest()
    elif args.check_patch:
        selftest()
        parent = plain_path(WT / "tmp", directory=True)
        with tempfile.TemporaryDirectory(prefix="s3_t05_c1_check_", dir=parent) as temp:
            root = Path(temp)
            source = root / "source"
            (source / RTL.parent).mkdir(parents=True)
            shutil.copyfile(VENDOR / RTL, source / RTL)
            apply_patches(source, root)
    elif args.preflight:
        preflight(args.run_name)
    elif args.check_heavy:
        no_heavy_processes()
        memory_check()
    elif args.prepare:
        selftest()
        prepare(args.run_name)
    else:
        require(args.exit_code is not None, "finalize 必须提供 --exit-code")
        finalize(args.run_name, args.exit_code, args.console_exit_code)


if __name__ == "__main__":
    try:
        main()
    except ResourceBlocked as error:
        print(str(error), file=sys.stderr)
        sys.exit(4)
    except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(2)
