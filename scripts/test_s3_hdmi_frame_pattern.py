#!/usr/bin/env python3
"""在隔离主机环境中回归 HDMI 测试帧生成逻辑。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any


TASK_ID = "S3-HDMI-FRAME-TEST-01"
BASELINE_HEAD = "4492f1157b8635a8eb8e7f783d334def2fa55424"
BASELINE_BRANCH = "codex/stage3-video"
SOURCE_CACHE_HEAD = "fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327"
PATCH_SHA256 = "f03aad77aeef0c36defa5f832eb93bd92f8c038bc40c6c9260c28835cb843dc1"
PATCH_REL = Path("board/stage3/software/hdmi_test/hdmi_display_bringup.patch")
SOURCE_CACHE_REL = Path("tmp/stage3_reference/AX7020_2023.1")
SOURCE_PREFIX = PurePosixPath(
    "course_s2_vitis/14_vdma_hdmi_out/Vitis/auto_create_vitis/src/vdma_hdmi"
)
SOURCE_FILES = (
    SOURCE_PREFIX / "main.c",
    SOURCE_PREFIX / "dynclk/dynclk.c",
    SOURCE_PREFIX / "dynclk/dynclk.h",
    SOURCE_PREFIX / "display_ctrl/display_ctrl.c",
)
RUN_ROOT_REL = Path("tmp/s3_hdmi_frame_test_01")
REPORT_REL = Path("report/stage3_hdmi_frame_pattern_host_test_20261007.json")
RUN_NAME_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z", re.ASCII)
PIXEL_COUNT = 1920 * 1080
FRAME_BYTES = PIXEL_COUNT * 3
SOURCE_BYTES = 800 * 600 * 3
CANARY_BYTES = 64
SOURCE_SEED = 0xC0DEC0DE
LOCAL_TZ = timezone(timedelta(hours=8), name="Asia/Shanghai")


class TestFailure(RuntimeError):
    """表示回归前置条件或断言失败。"""


def now_local() -> str:
    return datetime.now(LOCAL_TZ).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def path_for_json(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def normalized_path(path_text: str) -> str:
    return str(Path(path_text).resolve()).casefold().replace("\\", "/")


def extract_c_function(source: str, function_name: str) -> str:
    """按 C 注释、字符串和字符常量边界提取一个完整函数定义。"""
    matches = list(
        re.finditer(rf"\b[A-Za-z_][A-Za-z0-9_\s\*]*\b{re.escape(function_name)}\s*\(", source)
    )
    if len(matches) != 1:
        raise TestFailure(
            f"函数 {function_name} 定义匹配数应为 1，实际为 {len(matches)}"
        )

    start = matches[0].start()
    open_brace = source.find("{", matches[0].end())
    if open_brace < 0:
        raise TestFailure(f"函数 {function_name} 缺少函数体")

    depth = 0
    state = "normal"
    index = open_brace
    while index < len(source):
        char = source[index]
        next_char = source[index + 1] if index + 1 < len(source) else ""

        if state == "normal":
            if char == "/" and next_char == "/":
                state = "line_comment"
                index += 2
                continue
            if char == "/" and next_char == "*":
                state = "block_comment"
                index += 2
                continue
            if char == '"':
                state = "string"
            elif char == "'":
                state = "character"
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return source[start : index + 1]
        elif state == "line_comment":
            if char == "\n":
                state = "normal"
        elif state == "block_comment":
            if char == "*" and next_char == "/":
                state = "normal"
                index += 2
                continue
        elif state in ("string", "character"):
            if char == "\\":
                index += 2
                continue
            if (state == "string" and char == '"') or (
                state == "character" and char == "'"
            ):
                state = "normal"
        index += 1

    raise TestFailure(f"函数 {function_name} 的花括号没有闭合")


def blank_comments_and_literals(source: str) -> str:
    """屏蔽注释和字面量，保留偏移以便安全检查调用顺序。"""
    chars = list(source)
    state = "normal"
    index = 0
    while index < len(source):
        char = source[index]
        next_char = source[index + 1] if index + 1 < len(source) else ""
        if state == "normal":
            if char == "/" and next_char == "/":
                chars[index] = chars[index + 1] = " "
                state = "line_comment"
                index += 2
                continue
            if char == "/" and next_char == "*":
                chars[index] = chars[index + 1] = " "
                state = "block_comment"
                index += 2
                continue
            if char == '"' or char == "'":
                chars[index] = " "
                state = "string" if char == '"' else "character"
        elif state == "line_comment":
            if char == "\n":
                state = "normal"
            else:
                chars[index] = " "
        elif state == "block_comment":
            chars[index] = " "
            if char == "*" and next_char == "/":
                chars[index + 1] = " "
                state = "normal"
                index += 2
                continue
        elif state in ("string", "character"):
            if char != "\n":
                chars[index] = " "
            if char == "\\":
                if index + 1 < len(source) and source[index + 1] != "\n":
                    chars[index + 1] = " "
                index += 2
                continue
            if (state == "string" and char == '"') or (
                state == "character" and char == "'"
            ):
                state = "normal"
        index += 1
    return "".join(chars)


def source_vector_fingerprints() -> tuple[str, str]:
    """生成固定种子的测试源图像，并返回 SHA-256 与 FNV-1a。"""
    state = SOURCE_SEED
    digest = hashlib.sha256()
    fnv = 14695981039346656037
    prime = 1099511628211
    for _ in range(SOURCE_BYTES):
        state ^= (state << 13) & 0xFFFFFFFF
        state ^= state >> 17
        state ^= (state << 5) & 0xFFFFFFFF
        value = state & 0xFF
        digest.update(bytes((value,)))
        fnv = ((fnv ^ value) * prime) & 0xFFFFFFFFFFFFFFFF
    return digest.hexdigest(), f"{fnv:016x}"


class CommandRunner:
    """执行并归档子进程命令及其完整标准输出。"""

    def __init__(self, run_dir: Path, logs_dir: Path, repo_root: Path):
        self.run_dir = run_dir
        self.logs_dir = logs_dir
        self.repo_root = repo_root
        self.records: list[dict[str, Any]] = []

    def run(
        self,
        label: str,
        argv: list[str],
        cwd: Path,
        *,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        command_number = len(self.records) + 1
        safe_label = re.sub(r"[^A-Za-z0-9_.-]+", "_", label).strip("_")
        log_rel = Path("logs") / f"{command_number:02d}_{safe_label}.log"
        result = subprocess.run(
            argv,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        log_text = (
            f"LABEL={label}\n"
            f"ARGV={json.dumps(argv, ensure_ascii=False)}\n"
            f"CWD={cwd}\n"
            f"EXIT_CODE={result.returncode}\n"
            "--- STDOUT ---\n"
            f"{result.stdout}"
            "\n--- STDERR ---\n"
            f"{result.stderr}"
        )
        (self.run_dir / log_rel).write_text(log_text, encoding="utf-8")
        record = {
            "label": label,
            "argv": argv,
            "cwd": path_for_json(cwd, self.repo_root),
            "exit_code": result.returncode,
            "log": log_rel.as_posix(),
        }
        self.records.append(record)
        if check and result.returncode != 0:
            raise TestFailure(
                f"命令失败（退出码 {result.returncode}）：{label}；详见 {log_rel.as_posix()}"
            )
        return result


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TestFailure(message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="隔离运行 S3 HDMI 测试帧主机回归，不调用 Vivado/Vitis 或板卡。"
    )
    parser.add_argument("--run-name", required=True, help="新的 ASCII 安全运行目录名")
    parser.add_argument(
        "--expected-head",
        default=BASELINE_HEAD,
        help="完整 40 位 Git SHA；默认使用脚本固定基线，不自动接受当前 HEAD",
    )
    args = parser.parse_args()
    if not RUN_NAME_PATTERN.fullmatch(args.run_name) or args.run_name in (".", ".."):
        parser.error("run-name 仅可由 ASCII 字母、数字、点、下划线和连字符组成")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", args.expected_head, re.ASCII):
        parser.error("expected-head 必须是完整的 40 位十六进制 Git SHA")
    args.expected_head = args.expected_head.lower()
    return args


def create_harness(function_source: str) -> str:
    """将实际补丁函数嵌入独立主机检查程序。"""
    wrapper = r'''#include <inttypes.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef uint8_t u8;
typedef uint32_t u32;

#define DEMO_PATTERN_0 0
#define DEMO_PATTERN_1 1
#define DEMO_PATTERN_2 2
#define DEMO_PATTERN_3 3
#define BYTES_PIXEL 3U
#define DEMO_MAX_FRAME (1920U * 1080U * BYTES_PIXEL)

static u8 gImage_pic_800_600[800U * 600U * BYTES_PIXEL];
static unsigned int g_flush_calls;
static unsigned int g_flush_address;
static unsigned int g_flush_length;

int xil_printf(const char *format, ...)
{
    (void)format;
    return 0;
}

void Xil_DCacheFlushRange(unsigned int address, unsigned int length)
{
    ++g_flush_calls;
    g_flush_address = address;
    g_flush_length = length;
}

'''
    tail = r'''

int main(void)
{
    const size_t source_bytes = sizeof(gImage_pic_800_600);
    const size_t allocation_bytes = (size_t)DEMO_MAX_FRAME + 2U * 64U;
    const uint32_t expected_seed = UINT32_C(0xC0DEC0DE);
    uint32_t state = expected_seed;
    uint64_t source_fnv = UINT64_C(14695981039346656037);
    uint8_t *allocation = (uint8_t *)malloc(allocation_bytes);
    uint8_t *frame;
    uint64_t pixels_checked = 0;
    uint64_t bytes_checked = 0;
    uint64_t mismatches = 0;
    uint64_t first_mismatch = UINT64_MAX;
    unsigned int prefix_ok = 1;
    unsigned int suffix_ok = 1;
    unsigned int flush_start_matches;
    unsigned int flush_length_matches;
    unsigned int pass;

    if (allocation == NULL) {
        fprintf(stderr, "ERROR=malloc_failed\n");
        return 2;
    }
    memset(allocation, 0xCD, allocation_bytes);
    memset(allocation, 0xA5, 64U);
    memset(allocation + 64U + DEMO_MAX_FRAME, 0x5A, 64U);
    frame = allocation + 64U;

    for (size_t index = 0; index < source_bytes; ++index) {
        uint8_t value;
        state ^= state << 13;
        state ^= state >> 17;
        state ^= state << 5;
        value = (uint8_t)(state & UINT32_C(0xFF));
        gImage_pic_800_600[index] = value;
        source_fnv = (source_fnv ^ value) * UINT64_C(1099511628211);
    }

    DemoPrintTest(frame, 1920U, 1080U, 1920U * BYTES_PIXEL, DEMO_PATTERN_0);

    for (size_t index = 0; index < 64U; ++index) {
        if (allocation[index] != 0xA5U) {
            prefix_ok = 0;
        }
        if (allocation[64U + DEMO_MAX_FRAME + index] != 0x5AU) {
            suffix_ok = 0;
        }
    }

    for (uint32_t y = 0; y < 1080U; ++y) {
        const uint32_t source_y = (uint32_t)(((uint64_t)y * 600U) / 1080U);
        for (uint32_t x = 0; x < 1920U; ++x) {
            const uint32_t source_x = (uint32_t)(((uint64_t)x * 800U) / 1920U);
            const size_t source_offset =
                ((size_t)source_y * 800U + source_x) * BYTES_PIXEL;
            const size_t output_offset =
                (size_t)y * (1920U * BYTES_PIXEL) + (size_t)x * BYTES_PIXEL;
            ++pixels_checked;
            for (size_t channel = 0; channel < BYTES_PIXEL; ++channel) {
                if (frame[output_offset + channel] !=
                    gImage_pic_800_600[source_offset + channel]) {
                    if (first_mismatch == UINT64_MAX) {
                        first_mismatch = (uint64_t)y * 1920U + x;
                    }
                    ++mismatches;
                }
                ++bytes_checked;
            }
        }
    }

    flush_start_matches =
        g_flush_address == (unsigned int)(uintptr_t)frame ? 1U : 0U;
    flush_length_matches = g_flush_length == DEMO_MAX_FRAME ? 1U : 0U;
    pass = pixels_checked == UINT64_C(2073600) &&
           bytes_checked == UINT64_C(6220800) && mismatches == 0 &&
           prefix_ok && suffix_ok && g_flush_calls == 1U &&
           flush_start_matches && flush_length_matches;

    printf("SOURCE_FNV64=%016" PRIx64 "\n", source_fnv);
    printf("PIXELS_CHECKED=%" PRIu64 "\n", pixels_checked);
    printf("BYTES_CHECKED=%" PRIu64 "\n", bytes_checked);
    printf("PIXEL_MISMATCHES=%" PRIu64 "\n", mismatches);
    if (first_mismatch != UINT64_MAX) {
        printf("FIRST_MISMATCH_PIXEL=%" PRIu64 "\n", first_mismatch);
    }
    printf("CANARY_PREFIX=%s\n", prefix_ok ? "PASS" : "FAIL");
    printf("CANARY_SUFFIX=%s\n", suffix_ok ? "PASS" : "FAIL");
    printf("DCACHE_FLUSH_CALLS=%u\n", g_flush_calls);
    printf("DCACHE_FLUSH_START_MATCH_LOW32=%u\n", flush_start_matches);
    printf("DCACHE_FLUSH_LENGTH=%u\n", g_flush_length);
    printf("DCACHE_FLUSH_LENGTH_MATCH=%u\n", flush_length_matches);
    printf("RESULT=%s\n", pass ? "PASS" : "FAIL");
    free(allocation);
    return pass ? 0 : 1;
}
'''
    return wrapper + function_source + tail


def check_main_flow(main_source: str, function_source: str) -> dict[str, Any]:
    clean_main = blank_comments_and_literals(extract_c_function(main_source, "main"))
    names = ("DisplayInitialize", "DisplaySetMode", "DemoPrintTest", "DisplayStart")
    offsets: dict[str, int] = {}
    for name in names:
        occurrences = list(re.finditer(rf"\b{re.escape(name)}\s*\(", clean_main))
        require(len(occurrences) == 1, f"main 中 {name} 调用次数不是 1")
        offsets[name] = occurrences[0].start()
    require(
        [offsets[name] for name in names] == sorted(offsets.values()),
        "main 调用顺序不是初始化→设模→绘制→启动",
    )
    require(
        re.search(
            r"\bDisplaySetMode\s*\(\s*&\s*dispCtrl\s*,\s*&\s*VMODE_1920x1080\s*\)",
            clean_main,
        )
        is not None,
        "main 未将显示模式设为 VMODE_1920x1080",
    )

    clean_pattern = blank_comments_and_literals(function_source)
    case_start = clean_pattern.find("case DEMO_PATTERN_0:")
    case_end = clean_pattern.find("case DEMO_PATTERN_1:", case_start + 1)
    require(case_start >= 0 and case_end > case_start, "找不到 pattern 0 分支边界")
    pattern_zero = clean_pattern[case_start:case_end]
    require(
        re.search(r"for\s*\(\s*ycoi\s*=\s*0\s*;\s*ycoi\s*<\s*height\s*;", pattern_zero)
        is not None,
        "pattern 0 未按目标高度遍历",
    )
    require(
        re.search(r"for\s*\(\s*xcoi\s*=\s*0\s*;\s*xcoi\s*<\s*\(\s*width\s*\*\s*BYTES_PIXEL\s*\)", pattern_zero)
        is not None,
        "pattern 0 未按目标宽度遍历",
    )
    writes = pattern_zero.find("frame[")
    flush = pattern_zero.find("Xil_DCacheFlushRange(")
    require(writes >= 0 and flush > writes, "pattern 0 的 DCache flush 不在绘制之后")
    require(
        len(re.findall(r"\bXil_DCacheFlushRange\s*\(", pattern_zero)) == 1,
        "pattern 0 中 DCache flush 静态调用次数不是 1",
    )
    return {
        "main_call_order": list(names),
        "main_call_offsets_bytes": offsets,
        "display_mode_symbol": "VMODE_1920x1080",
        "pattern_zero_flush_after_draw": True,
        "pattern_zero_static_flush_calls": 1,
    }


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    run_root = repo_root / RUN_ROOT_REL
    run_dir = run_root / args.run_name
    if run_dir.exists() or run_dir.is_symlink():
        raise SystemExit(f"拒绝覆盖已有运行目录：{run_dir}")
    if REPORT_REL.is_absolute() or ".." in REPORT_REL.parts:
        raise SystemExit("内部错误：报告路径越界")
    report_path = repo_root / REPORT_REL
    if not report_path.resolve().is_relative_to(repo_root.resolve()):
        raise SystemExit("拒绝写入仓库外的报告路径")
    previous_report_bytes: bytes | None = None
    previous_report_info: dict[str, Any] | None = None
    if report_path.exists() or report_path.is_symlink():
        if report_path.is_symlink() or not report_path.is_file():
            raise SystemExit(f"拒绝覆盖非普通文件报告：{report_path}")
        previous_report_bytes = report_path.read_bytes()
        try:
            previous_report_document = json.loads(previous_report_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise SystemExit(f"拒绝覆盖无法解析的既有报告：{report_path}") from error
        if previous_report_document.get("task_id") != TASK_ID:
            raise SystemExit(f"拒绝覆盖其他任务的报告：{report_path}")
        previous_report_info = {
            "sha256": hashlib.sha256(previous_report_bytes).hexdigest(),
            "status": previous_report_document.get("status", "UNKNOWN"),
        }
    run_root_resolved = run_root.resolve()
    if not run_root_resolved.is_relative_to(repo_root.resolve()):
        raise SystemExit("拒绝写入仓库外的运行目录")
    run_root.mkdir(parents=True, exist_ok=True)
    try:
        run_dir.mkdir(exist_ok=False)
    except FileExistsError as error:
        raise SystemExit(f"拒绝覆盖已有运行目录：{run_dir}") from error
    previous_report_archive: dict[str, Any] | None = None
    if previous_report_bytes is not None and previous_report_info is not None:
        archive_path = run_dir / "previous_report.json"
        archive_path.write_bytes(previous_report_bytes)
        previous_report_archive = {
            **previous_report_info,
            "path": path_for_json(archive_path, repo_root),
            "archive_sha256": sha256_file(archive_path),
        }

    logs_dir = run_dir / "logs"
    logs_dir.mkdir()
    runner = CommandRunner(run_dir, logs_dir, repo_root)
    source_cache = repo_root / SOURCE_CACHE_REL
    summary: dict[str, Any] = {
        "task_id": TASK_ID,
        "schema_version": 1,
        "started_at_utc_plus_8": now_local(),
        "run_name": args.run_name,
        "selected_expected_head": args.expected_head,
        "run_directory": path_for_json(run_dir, repo_root),
        "previous_report_archive": previous_report_archive,
        "invocation": {
            "shell": "Git Bash",
            "argv": [
                sys.executable,
                str(Path(__file__).resolve()),
                "--run-name",
                args.run_name,
                "--expected-head",
                args.expected_head,
            ],
            "cwd": path_for_json(repo_root, repo_root),
        },
        "status": "RUNNING",
        "commands": runner.records,
        "checks": {},
        "errors": [],
    }

    try:
        require(
            normalized_path(str(Path.cwd())) == normalized_path(str(repo_root)),
            "脚本工作目录未落在项目仓库根目录",
        )
        require(source_cache.is_dir(), f"官方源缓存目录不存在：{source_cache}")

        git_exe = shutil.which("git.exe") or shutil.which("git")
        gcc_exe = shutil.which("gcc.exe") or shutil.which("gcc")
        bash_exe = Path(r"C:\Program Files\Git\bin\bash.exe")
        require(git_exe is not None, "PATH 中找不到 Git")
        require(gcc_exe is not None, "PATH 中找不到 MinGW GCC")
        require(bash_exe.is_file(), f"找不到 Git Bash：{bash_exe}")
        python_exe = Path(sys.executable).resolve()
        git_path = Path(git_exe).resolve()
        gcc_path = Path(gcc_exe).resolve()

        tool_versions: dict[str, str] = {
            "python": platform.python_version(),
            "python_implementation": platform.python_implementation(),
        }
        for name, executable in (
            ("python_version", python_exe),
            ("git_version", git_path),
            ("gcc_version", gcc_path),
            ("gcc_target", gcc_path),
            ("bash_version", bash_exe),
        ):
            arguments = {
                "python_version": ["--version"],
                "git_version": ["--version"],
                "gcc_version": ["--version"],
                "gcc_target": ["-dumpmachine"],
                "bash_version": ["--version"],
            }[name]
            version_result = runner.run(
                name.replace("_", " "), [str(executable), *arguments], repo_root
            )
            first_line = (version_result.stdout or version_result.stderr).splitlines()
            tool_versions[name] = first_line[0] if first_line else ""
        tools = {
            "python": {"path": str(python_exe), "sha256": sha256_file(python_exe)},
            "git": {"path": str(git_path), "sha256": sha256_file(git_path)},
            "mingw_gcc": {"path": str(gcc_path), "sha256": sha256_file(gcc_path)},
            "git_bash": {"path": str(bash_exe), "sha256": sha256_file(bash_exe)},
        }
        summary["tool_versions"] = tool_versions
        summary["tools"] = tools

        head_result = runner.run(
            "project HEAD", [str(git_path), "rev-parse", "HEAD"], repo_root
        )
        branch_result = runner.run(
            "project branch", [str(git_path), "branch", "--show-current"], repo_root
        )
        project_head = head_result.stdout.strip()
        project_branch = branch_result.stdout.strip()
        summary["project_baseline"] = {
            "expected_head": args.expected_head,
            "actual_head": project_head,
            "expected_branch": BASELINE_BRANCH,
            "actual_branch": project_branch,
        }
        require(project_head == args.expected_head, "项目 HEAD 与显式选择的完整基线不一致，拒绝继续")
        require(project_branch == BASELINE_BRANCH, "项目分支与任务基线不一致，拒绝继续")

        source_git_root_result = runner.run(
            "official source git root",
            [str(git_path), "rev-parse", "--show-toplevel"],
            source_cache,
        )
        actual_source_root = source_git_root_result.stdout.strip()
        require(
            normalized_path(actual_source_root) == normalized_path(str(source_cache)),
            "官方源缓存 Git 根目录与指定目录不一致",
        )
        source_head_result = runner.run(
            "official source HEAD",
            [str(git_path), "rev-parse", "HEAD"],
            source_cache,
        )
        source_head = source_head_result.stdout.strip()
        full_status = runner.run(
            "official source full status",
            [str(git_path), "status", "--porcelain=v1", "--untracked-files=all"],
            source_cache,
        ).stdout
        target_rel = SOURCE_PREFIX.as_posix()
        target_status = runner.run(
            "official source target status",
            [
                str(git_path),
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
                "--",
                target_rel,
            ],
            source_cache,
        ).stdout
        summary["official_source"] = {
            "expected_head": SOURCE_CACHE_HEAD,
            "actual_head": source_head,
            "git_root": actual_source_root,
            "full_worktree_clean": not full_status.strip(),
            "target_subtree_clean": not target_status.strip(),
            "target_subtree": target_rel,
        }
        require(source_head == SOURCE_CACHE_HEAD, "官方源缓存提交与锁定版本不一致")
        require(not full_status.strip(), "官方源缓存工作区不干净，拒绝复制")
        require(not target_status.strip(), "官方源目标子树不干净，拒绝复制")

        patch_path = repo_root / PATCH_REL
        require(patch_path.is_file(), f"候选补丁不存在：{patch_path}")
        patch_hash = sha256_file(patch_path)
        patch_text = patch_path.read_text(encoding="utf-8")
        patch_paths = re.findall(r"^diff --git a/(.+?) b/(.+?)$", patch_text, re.MULTILINE)
        require(bool(patch_paths), "候选补丁没有可解析的 diff 文件路径")
        patch_targets: set[str] = set()
        for old_path, new_path in patch_paths:
            old_parts = PurePosixPath(old_path)
            new_parts = PurePosixPath(new_path)
            require(
                old_path == new_path
                and not old_parts.is_absolute()
                and not new_parts.is_absolute()
                and ".." not in old_parts.parts
                and ".." not in new_parts.parts
                and "\\" not in old_path
                and "\\" not in new_path,
                "候选补丁含路径穿越或不一致路径",
            )
            patch_targets.add(new_path)
        expected_targets = {path.as_posix() for path in SOURCE_FILES}
        require(patch_targets == expected_targets, "候选补丁修改文件集合与任务卡不一致")
        require(patch_hash == PATCH_SHA256, "候选补丁 SHA-256 与锁定值不一致")

        patch_copy = run_dir / "input" / patch_path.name
        patch_copy.parent.mkdir(parents=True)
        shutil.copyfile(patch_path, patch_copy)
        require(sha256_file(patch_copy) == PATCH_SHA256, "补丁副本 SHA-256 不匹配")

        patch_tree = run_dir / "patch_tree"
        patch_tree.mkdir()
        source_hashes: dict[str, str] = {}
        for relative in SOURCE_FILES:
            source_path = source_cache.joinpath(*relative.parts)
            destination = patch_tree.joinpath(*relative.parts)
            require(source_path.is_file(), f"官方源缺少必要源码：{relative.as_posix()}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_path, destination)
            source_hashes[relative.as_posix()] = sha256_file(source_path)
            require(
                sha256_file(destination) == source_hashes[relative.as_posix()],
                f"隔离源码副本哈希不匹配：{relative.as_posix()}",
            )
        summary["source_copy"] = {
            "files": source_hashes,
            "copied_file_count": len(source_hashes),
            "candidate_patch_sha256": patch_hash,
            "applied_patch_copy": path_for_json(patch_copy, repo_root),
        }

        patch_directory = (
            run_dir.relative_to(repo_root).as_posix() + "/patch_tree"
        )
        runner.run(
            "isolated patch check",
            [
                str(git_path),
                "apply",
                "--check",
                "-p1",
                f"--directory={patch_directory}",
                str(patch_copy),
            ],
            repo_root,
        )
        runner.run(
            "apply isolated patch copy",
            [
                str(git_path),
                "apply",
                "-p1",
                f"--directory={patch_directory}",
                str(patch_copy),
            ],
            repo_root,
        )

        main_relative = next(path for path in SOURCE_FILES if path.name == "main.c")
        main_path = patch_tree.joinpath(*main_relative.parts)
        main_source = main_path.read_text(encoding="utf-8")
        demo_function = extract_c_function(main_source, "DemoPrintTest")
        flow_checks = check_main_flow(main_source, demo_function)
        source_hash256, source_fnv64 = source_vector_fingerprints()
        harness_path = run_dir / "harness" / "demo_print_test_harness.c"
        harness_path.parent.mkdir(parents=True)
        harness_path.write_text(create_harness(demo_function), encoding="utf-8")

        gcc_arguments = [
            str(gcc_path),
            "-std=c11",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-Wno-pointer-to-int-cast",
            str(harness_path),
            "-o",
            str(run_dir / "demo_print_test_host.exe"),
        ]
        runner.run("compile extracted DemoPrintTest", gcc_arguments, run_dir)
        executable = run_dir / "demo_print_test_host.exe"
        execution = runner.run("run host frame regression", [str(executable)], run_dir)
        results = dict(
            re.findall(r"^([A-Z0-9_]+)=(.*)$", execution.stdout, re.MULTILINE)
        )
        expected_results = {
            "SOURCE_FNV64": source_fnv64,
            "PIXELS_CHECKED": str(PIXEL_COUNT),
            "BYTES_CHECKED": str(FRAME_BYTES),
            "PIXEL_MISMATCHES": "0",
            "CANARY_PREFIX": "PASS",
            "CANARY_SUFFIX": "PASS",
            "DCACHE_FLUSH_CALLS": "1",
            "DCACHE_FLUSH_START_MATCH_LOW32": "1",
            "DCACHE_FLUSH_LENGTH": str(FRAME_BYTES),
            "DCACHE_FLUSH_LENGTH_MATCH": "1",
            "RESULT": "PASS",
        }
        for key, expected in expected_results.items():
            require(results.get(key) == expected, f"主机 harness 结果 {key} 不符合预期")

        summary["checks"] = {
            "nearest_neighbor_pixelwise": "PASS",
            "frame_prefix_canary": "PASS",
            "frame_suffix_canary": "PASS",
            "dcache_flush_once": "PASS",
            "dcache_flush_length_demo_max_frame": "PASS",
            "main_display_call_order": "PASS",
            "source_cache_unchanged": "PENDING_FINAL_CHECK",
        }
        summary["main_flow"] = flow_checks
        summary["test_vector"] = {
            "source_width": 800,
            "source_height": 600,
            "source_pixel_format": "RGB888 byte array consumed by candidate function",
            "target_width": 1920,
            "target_height": 1080,
            "target_pixel_format": "three bytes per pixel",
            "coordinate_rule": "source_x=floor(x*800/1920), source_y=floor(y*600/1080)",
            "generator": "xorshift32 low byte, seed 0xC0DEC0DE",
            "source_bytes": SOURCE_BYTES,
            "source_sha256": source_hash256,
            "source_fnv1a64": source_fnv64,
            "pixels_compared": PIXEL_COUNT,
            "bytes_compared": FRAME_BYTES,
            "canary_each_side_bytes": CANARY_BYTES,
        }
        summary["host_results"] = results
        summary["test_boundaries"] = [
            "只编译并运行从补丁后 main.c 提取的 DemoPrintTest；未构建完整 main、BSP 或 Vitis 应用。",
            "MinGW x86_64 主机 stub 将 DCache 起始地址按候选代码的 unsigned int 转换后比较低 32 位；不代表 ARM 地址映射。",
            "不等同于 Vitis/BSP link、bitstream、HDMI 电气/显示器或板上验证。",
            "不调用 Vivado/Vitis，不接触板卡/JTAG，不干预 Batch109，不修改官方源缓存。",
        ]
        summary["status"] = "PASS"
    except Exception as error:
        summary["status"] = "FAILED"
        summary["errors"].append(f"{type(error).__name__}: {error}")

    try:
        source_head_after = runner.run(
            "official source HEAD final",
            [str(shutil.which("git.exe") or shutil.which("git")), "rev-parse", "HEAD"],
            source_cache,
            check=False,
        )
        source_status_after = runner.run(
            "official source status final",
            [
                str(shutil.which("git.exe") or shutil.which("git")),
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
            ],
            source_cache,
            check=False,
        )
        source_unchanged = (
            source_head_after.returncode == 0
            and source_head_after.stdout.strip() == SOURCE_CACHE_HEAD
            and source_status_after.returncode == 0
            and not source_status_after.stdout.strip()
        )
        summary.setdefault("checks", {})["source_cache_unchanged"] = (
            "PASS" if source_unchanged else "FAIL"
        )
        summary.setdefault("official_source", {})["final_worktree_clean"] = (
            not source_status_after.stdout.strip()
            if source_status_after.returncode == 0
            else False
        )
        if not source_unchanged:
            summary["status"] = "FAILED"
            summary["errors"].append("官方源缓存最终状态与锁定提交/干净工作区不符")
    except Exception as error:
        summary["status"] = "FAILED"
        summary["errors"].append(f"官方源最终核验失败：{type(error).__name__}: {error}")

    summary["commands"] = runner.records
    summary["ended_at_utc_plus_8"] = now_local()
    summary["script_sha256"] = sha256_file(Path(__file__).resolve())
    evidence_files: dict[str, str] = {}
    for path in sorted(run_dir.rglob("*")):
        if path.is_file() and path.name != "summary.json":
            evidence_files[path.relative_to(run_dir).as_posix()] = sha256_file(path)
    summary["evidence_file_sha256"] = evidence_files
    run_summary_path = run_dir / "summary.json"
    write_json(run_summary_path, summary)
    report = {
        "task_id": TASK_ID,
        "schema_version": 1,
        "generated_at_utc_plus_8": summary["ended_at_utc_plus_8"],
        "status": summary["status"],
        "run_name": args.run_name,
        "selected_expected_head": args.expected_head,
        "baseline": summary.get("project_baseline"),
        "official_source": summary.get("official_source"),
        "patch_sha256": PATCH_SHA256,
        "tools": summary.get("tools", {}),
        "tool_versions": summary.get("tool_versions", {}),
        "commands": runner.records,
        "checks": summary.get("checks", {}),
        "main_flow": summary.get("main_flow"),
        "test_vector": summary.get("test_vector"),
        "host_results": summary.get("host_results"),
        "test_boundaries": summary.get("test_boundaries", []),
        "errors": summary["errors"],
        "evidence": {
            "run_directory": path_for_json(run_dir, repo_root),
            "run_summary": path_for_json(run_summary_path, repo_root),
            "run_summary_sha256": sha256_file(run_summary_path),
            "files_sha256": evidence_files,
        },
        "script_sha256": summary["script_sha256"],
        "previous_report_archive": previous_report_archive,
    }
    write_json(report_path, report)
    print(json.dumps({"status": summary["status"], "run": str(run_dir), "report": str(report_path)}, ensure_ascii=False))
    if summary["errors"]:
        for error in summary["errors"]:
            print(error, file=sys.stderr)
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
