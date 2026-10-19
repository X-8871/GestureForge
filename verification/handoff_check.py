#!/usr/bin/env python3
"""只读核验 Codex↔DSH 交接记录与目标工作树的一致性。

设计边界（对应根 `AGENTS.md`「与 Codex 共享同一工作区」）：
- 只读：仅读取文件系统和 Git 对象；不写仓库任何文件，不执行记录里的恢复命令。
- 只用只读 Git 子命令（`rev-parse` / `status`），一律带 `--no-optional-locks`，
  避免 `git status` 刷新索引而回写工作树。
- `index.lock` 必须先用 `git rev-parse --git-path index.lock` 解析后再判断存在性；
  链接工作树的 gitdir 位于主仓库 `.git/worktrees/<name>/`，不能假定
  `<工作树>/.git/index.lock`。

用法示例：
    python -B verification/handoff_check.py --print-template
    python -B verification/handoff_check.py --worktree D:/FPGA_Competition/w2b \\
        --record handoff.json
    python -B verification/handoff_check.py --record '{"status":"OFFERED"}' --claim \\
        --claimed-path verification/handoff_check.py

退出码：0 全部 PASS/SKIP；1 存在 FAIL；2 输入或环境错误。
检查器结论不代表 G0/G4/G5、测试通过或实物验收。
"""

from __future__ import annotations

import argparse
import csv
import fnmatch
import io
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Sequence

UTC8 = timezone(timedelta(hours=8))
DEFAULT_MAX_HEARTBEAT_MINUTES = 120
HEARTBEAT_FUTURE_TOLERANCE = timedelta(minutes=5)
SCOPE_STATEMENT = (
    "只读核验：不代表 G0/G4/G5、测试通过或实物验收；不执行恢复命令，不写仓库文件。"
)
MAX_EVIDENCE_SAMPLES = 5

HEAVY_PROCESS_NAMES = (
    "vivado",
    "xsim",
    "xelab",
    "xvlog",
    "hw_server",
    "cs_server",
    "xsdb",
)

HANDOFF_STATUS_FLOW = "IDLE→OFFERED→CLAIMED→IN_PROGRESS→DONE"
HANDOFF_STATUSES = ("IDLE", "OFFERED", "CLAIMED", "IN_PROGRESS", "DONE")
TAKEOVER_STATUS = "OFFERED"
# `--claim` 时必须齐备的让出契约字段；heartbeat_utc8 的可解析性由检查项 e 核验。
CLAIM_CONTRACT_FIELDS = ("yield_statement", "next_owner")
# 不参与机器核验、只由人工核对的字段及其说明（模板与测试共用）。
MANUAL_REVIEW_NOTES = {
    "task": "人工核对任务编号，不参与机器核验",
    "owner": "人工核对负责人，不参与机器核验",
    "recovery_command": "人工核对可恢复性，不参与机器核验（检查器绝不执行它）",
}

# 交接行 11 字段（显示顺序即复制顺序）。
TEMPLATE_FIELDS = (
    "任务",
    "负责人",
    "工作树/分支",
    "起始提交",
    "允许修改范围",
    "未提交改动归属",
    "让出声明",
    "心跳(UTC+8)",
    "证据入口",
    "恢复命令",
    "状态/下一接手方",
)

# record 规范键；同一键的多个别名不得同时出现。
RECORD_ALIASES: dict[str, tuple[str, ...]] = {
    "task": ("task", "task_id", "任务"),
    "owner": ("owner", "负责人"),
    "worktree": ("worktree", "worktree_path", "工作树"),
    "branch": ("branch", "分支"),
    "base_commit": ("base_commit", "starting_commit", "head", "head_commit", "起始提交"),
    "allowed_paths": ("allowed_paths", "allowed_scope", "允许修改范围"),
    "dirty_owner": ("dirty_owner", "uncommitted_owner", "未提交改动归属"),
    "yield_statement": ("yield_statement", "yield", "让出声明"),
    "heartbeat_utc8": ("heartbeat_utc8", "heartbeat", "心跳(UTC+8)", "心跳"),
    "evidence_dir": ("evidence_dir", "evidence", "证据入口"),
    "recovery_command": ("recovery_command", "recovery", "恢复命令"),
    "status": ("status", "状态"),
    "next_owner": ("next_owner", "next", "下一接手方"),
}
RECORD_KEYS = tuple(RECORD_ALIASES)
ALIAS_TO_KEY = {
    alias: key for key, aliases in RECORD_ALIASES.items() for alias in aliases
}

# 只读 Git 子命令白名单；run_git 之外的动词一律不出现。
READ_ONLY_GIT_SUBCOMMANDS = ("rev-parse", "status")
GIT_GLOBAL_OPTIONS = ("--no-optional-locks",)

HEARTBEAT_RE = re.compile(
    r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
    r"[T ](?P<hour>\d{2}):(?P<minute>\d{2})(?::(?P<second>\d{2}))?"
    r"(?P<offset>Z|[+-]\d{2}:?\d{2})?\Z"
)
COMMIT_RE = re.compile(r"[0-9a-fA-F]{7,40}\Z")

PLACEHOLDER_TEXTS = {
    "",
    "todo",
    "tbd",
    "pending",
    "placeholder",
    "unknown",
    "none",
    "null",
    "n/a",
    "na",
    "not applicable",
    "unfrozen",
    "待填写",
    "待补",
    "待冻结",
    "待确认",
    "待定",
    "未冻结",
    "未填写",
    "占位",
    "不适用",
}


class UsageError(ValueError):
    """命令行参数错误。"""


class DuplicateKeyError(ValueError):
    """JSON 对象含重复键。"""


class GitUnavailableError(RuntimeError):
    """git 命令无法执行，属于环境错误（退出码 2）。"""


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # noqa: D102 - argparse 钩子
        raise UsageError(message)


def is_placeholder_text(value: Any) -> bool:
    """判断文本是否为占位/未填写内容。"""
    if not isinstance(value, str):
        return True
    trimmed = value.strip()
    folded = trimmed.casefold()
    if folded in PLACEHOLDER_TEXTS:
        return True
    if trimmed.startswith("<") and trimmed.endswith(">"):
        return True
    return bool(re.fullmatch(r"x{2,}|t?xx|-{2,}|\.{3,}", folded))


def record_text(record: dict[str, Any] | None, key: str) -> str | None:
    """取 record 中某个键的非空文本；缺失、非字符串或空串返回 None。"""
    if not record:
        return None
    value = record.get(key)
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value or None


def declared_text(record: dict[str, Any] | None, key: str) -> str | None:
    """取 record 中某个键的已声明文本；占位内容视为未声明。"""
    value = record_text(record, key)
    if value is None or is_placeholder_text(value):
        return None
    return value


def normalize_slashes(path_text: str) -> str:
    """统一路径分隔符：反斜杠一律归一化为 `/`。"""
    return path_text.replace("\\", "/")


def to_absolute(path_value: str, base: Path) -> Path:
    """把用户输入的路径规范化为绝对路径（先统一分隔符）。"""
    if "\x00" in path_value:
        raise UsageError("路径含非法 NUL 字符")
    normalized = normalize_slashes(path_value)
    if path_value.startswith("\\\\?\\") or normalized.startswith("//?/"):
        raise UsageError("不支持 Windows 设备路径（\\\\?\\）")
    candidate = Path(normalized)
    if not candidate.is_absolute():
        candidate = base / candidate
    return Path(os.path.abspath(os.fspath(candidate)))


def default_worktree_root() -> Path:
    """默认检查本脚本所在仓库的工作树根（脚本位于 <worktree>/verification/）。"""
    return Path(__file__).absolute().parent.parent


def norm_key(path: Path | str) -> str:
    """路径比较键：规范化大小写与分隔符。"""
    return os.path.normcase(os.path.normpath(os.fspath(path)))


def run_git(
    args: Sequence[str],
    cwd: Path,
    config: Sequence[str] = (),
) -> tuple[int, str, str]:
    """执行只读 git 命令，返回 (退出码, stdout, stderr)。"""
    if not args or args[0] not in READ_ONLY_GIT_SUBCOMMANDS:
        raise AssertionError(f"run_git 只允许只读子命令：{READ_ONLY_GIT_SUBCOMMANDS}")
    command = ["git", *GIT_GLOBAL_OPTIONS]
    for item in config:
        command.extend(("-c", item))
    command.extend(args)
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        raise GitUnavailableError(f"无法执行 git（{command[0]}）：{exc}") from exc
    return completed.returncode, completed.stdout or "", completed.stderr or ""


def git_command_text(args: Sequence[str], config: Sequence[str] = ()) -> str:
    """用于证据展示的只读命令文本。"""
    parts = ["git", *GIT_GLOBAL_OPTIONS]
    for item in config:
        parts.extend(("-c", item))
    parts.extend(args)
    return " ".join(parts)


def normalize_process_name(image: str) -> str:
    """归一化进程映像名：取基名、去 .exe、小写。"""
    name = os.path.basename(image.strip()).casefold()
    if name.endswith(".exe"):
        name = name[: -len(".exe")]
    return name


def _match_tasklist_rows(text: str) -> list[dict[str, str]]:
    """解析 tasklist /FO CSV /NH 输出。"""
    entries: list[dict[str, str]] = []
    for row in csv.reader(io.StringIO(text)):
        if len(row) < 2:
            continue
        image = row[0].strip()
        if not image:
            continue
        entries.append({"image": image, "pid": row[1].strip()})
    return entries


def _match_ps_rows(text: str, with_pid: bool) -> list[dict[str, str]]:
    """解析 `ps -A -o comm=` 或 `pgrep -l` 输出。"""
    entries: list[dict[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if with_pid:
            pid, _, image = stripped.partition(" ")
            entries.append({"image": image.strip(), "pid": pid.strip()})
        else:
            entries.append({"image": stripped, "pid": ""})
    return entries


def detect_heavy_processes() -> tuple[list[dict[str, str]] | None, str | None]:
    """枚举重型进程占用，返回 (命中列表, 不可用原因)。

    命中列表为 [] 表示枚举成功且无占用；返回 (None, 原因) 表示当前平台无法枚举，
    调用方应记 SKIP 并写明原因。本函数只读，不结束任何进程。
    """
    wanted = set(HEAVY_PROCESS_NAMES)
    if os.name == "nt":
        try:
            completed = subprocess.run(
                ["tasklist", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
        except OSError as exc:
            return None, f"无法执行 tasklist 枚举进程：{exc}"
        if completed.returncode != 0:
            return None, f"tasklist 枚举失败（退出码 {completed.returncode}）"
        entries = _match_tasklist_rows(completed.stdout or "")
    else:
        attempts: list[tuple[bool, str]] = []
        entries = []
        for command, with_pid in ((["ps", "-A", "-o", "comm="], False), (["pgrep", "-l"], True)):
            try:
                completed = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    check=False,
                )
            except OSError:
                attempts.append((False, command[0]))
                continue
            if completed.returncode != 0:
                attempts.append((False, command[0]))
                continue
            entries = _match_ps_rows(completed.stdout or "", with_pid)
            break
        else:
            tried = "、".join(name for _, name in attempts) or "ps/pgrep"
            return None, f"当前平台无可用的进程枚举命令（已尝试 {tried}）"
    matched = [
        entry
        for entry in entries
        if normalize_process_name(entry["image"]) in wanted
    ]
    return matched, None


def resolve_index_lock_path(worktree_root: Path) -> tuple[Path | None, str, str | None]:
    """用 `git rev-parse --git-path index.lock` 解析锁文件真实路径。

    返回 (锁路径或 None, 证据文本, 错误说明或 None)。链接工作树的 gitdir 不在
    工作树根下，因此必须先解析再判断存在性。
    """
    command_text = git_command_text(("rev-parse", "--git-path", "index.lock"))
    try:
        code, out, err = run_git(("rev-parse", "--git-path", "index.lock"), worktree_root)
    except GitUnavailableError as exc:
        return None, f"{command_text}（cwd={worktree_root}）", str(exc)
    evidence = f"{command_text}（cwd={worktree_root}）"
    if code != 0:
        detail = err.strip() or f"退出码 {code}"
        return None, evidence, f"解析 index.lock 失败：{detail}"
    raw = out.strip()
    evidence = f"{evidence} → {raw or '<空输出>'}"
    if not raw:
        return None, evidence, "git rev-parse --git-path index.lock 输出为空"
    lock_path = Path(raw)
    if not lock_path.is_absolute():
        # --git-path 的输出相对命令工作目录，故必须以 worktree_root 为基准。
        lock_path = worktree_root / raw
    return Path(os.path.abspath(os.fspath(lock_path))), evidence, None


def parse_heartbeat(text: str) -> tuple[datetime | None, str | None]:
    """解析 UTC+8 心跳时间；无时区后缀按 UTC+8 解释。"""
    match = HEARTBEAT_RE.fullmatch(text.strip())
    if match is None:
        return None, "心跳必须是 YYYY-MM-DD HH:MM[:SS] 或 YYYY-MM-DDTHH:MM[:SS][±HH:MM|Z]"
    offset = match.group("offset")
    normalized = text.strip().replace(" ", "T")
    if offset == "Z":
        normalized = normalized[:-1] + "+00:00"
    elif offset is not None and ":" not in offset:
        normalized = normalized[: -len(offset)] + offset[:3] + ":" + offset[3:]
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        return None, f"心跳时间无法解析：{exc}"
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC8)
    return parsed.astimezone(UTC8), None


def path_scope_key(path_text: str, root: Path | None) -> tuple[str | None, str | None]:
    """把路径规范化为工作树相对的 POSIX 路径；越界或非法时返回错误说明。"""
    value = path_text.strip()
    if not value:
        return None, "空路径"
    normalized = normalize_slashes(value)
    if "\x00" in value or value.startswith("\\\\?\\") or normalized.startswith("//?/"):
        return None, "含不支持的路径字符"
    if root is not None:
        candidate = to_absolute(value, root)
        try:
            common = os.path.commonpath((os.fspath(root), os.fspath(candidate)))
        except ValueError:
            return None, "与工作树不在同一路径树"
        if os.path.normcase(common) != os.path.normcase(os.fspath(root)):
            return None, "越出工作树"
        relative = os.path.relpath(os.fspath(candidate), os.fspath(root))
        return PurePosixPath(*Path(relative).parts).as_posix(), None
    parts = [part for part in normalized.split("/") if part not in ("", ".")]
    if any(part == ".." for part in parts):
        return None, "含 .. 路径分量"
    return "/".join(parts), None


def normalize_scope_entry(text: str, root: Path | None) -> tuple[str | None, bool, str | None]:
    """归一化允许范围条目，返回 (相对路径, 是否子树, 错误说明)。

    `dir/` 记为子树；反斜杠、`./` 与大小写统一归一化后再比较。
    """
    value = text.strip()
    if not value:
        return None, False, "空路径"
    subtree = normalize_slashes(value).endswith("/")
    key, failure = path_scope_key(value, root)
    if failure is not None:
        return None, False, failure
    return key, subtree, None


def _match_segments(claimed_parts: Sequence[str], pattern_parts: Sequence[str]) -> bool:
    """按路径段递归匹配；`**` 作为独立段可匹配零个或多个段，`*` 只作用于单段。"""
    if not pattern_parts:
        return not claimed_parts
    head = pattern_parts[0]
    if head == "**":
        if _match_segments(claimed_parts, pattern_parts[1:]):
            return True
        return bool(claimed_parts) and _match_segments(claimed_parts[1:], pattern_parts)
    if not claimed_parts:
        return False
    if not fnmatch.fnmatchcase(claimed_parts[0], head):
        return False
    return _match_segments(claimed_parts[1:], pattern_parts[1:])


def matches_scope(claimed: str, entry: str, subtree: bool = False) -> bool:
    """分隔符感知的范围匹配。

    - 精确路径严格相等，不做前缀匹配（`dir/a.py` 不允许 `dir/a.py.bak`）；
    - `dir/`（subtree=True）表示子树，覆盖 `dir` 及其全部子孙；
    - `*`、`?`、`[]` 只匹配单个路径段，不跨 `/`；
    - `**` 作为独立路径段匹配零个或多个段。
    """
    claimed_key = claimed.casefold()
    entry_key = entry.casefold()
    if entry_key.endswith("/"):
        # 直接传入 `dir/` 形式时同样按子树处理，避免调用方误用后静默不匹配。
        entry_key = entry_key[:-1]
        subtree = True
    if not claimed_key or not entry_key:
        return False
    if any(character in entry_key for character in "*?["):
        return _match_segments(claimed_key.split("/"), entry_key.split("/"))
    if subtree:
        return claimed_key == entry_key or claimed_key.startswith(entry_key + "/")
    return claimed_key == entry_key


def subtree_hint(claimed_key: str, entries: Sequence[tuple[str, bool]], root: Path | None) -> str | None:
    """越界时给出可操作提示：条目实为目录但未写结尾 `/`。"""
    if root is None:
        return None
    for entry, subtree in entries:
        if subtree or any(character in entry for character in "*?["):
            continue
        if claimed_key.startswith(entry + "/") and (root / entry).is_dir():
            return (
                f"条目 {entry} 是已存在目录但未以 / 结尾，按精确路径匹配（不做前缀匹配）；"
                f"若要覆盖子树请写作 {entry}/"
            )
    return None


def add_check(
    checks: list[dict[str, Any]],
    ident: str,
    name: str,
    status: str,
    evidence: str,
    reason: str | None = None,
) -> None:
    """登记一个检查项。"""
    item: dict[str, Any] = {
        "id": ident,
        "name": name,
        "status": status,
        "evidence": evidence,
    }
    if reason:
        item["reason"] = reason
    checks.append(item)


def load_record(value: str) -> tuple[dict[str, Any] | None, list[str]]:
    """读取 record（文件路径或内联 JSON）并规范化为标准键。

返回 (record 或 None, 错误列表)；错误列表为空表示读取成功。
"""
    errors: list[str] = []
    text = value
    looks_like_inline = value.lstrip().startswith(("{", "["))
    if not looks_like_inline:
        candidate = to_absolute(value, Path.cwd())
        if not os.path.exists(candidate):
            errors.append(f"record 既不是存在的文件也不是内联 JSON：{value}")
            return None, errors
        if not os.path.isfile(candidate):
            errors.append(f"record 路径不是普通文件：{candidate}")
            return None, errors
        try:
            text = candidate.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"record 文件读取失败：{exc}")
            return None, errors

    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, item in pairs:
            if key in result:
                raise DuplicateKeyError(f"record JSON 含重复键：{key}")
            result[key] = item
        return result

    def reject_constant(constant: str) -> None:
        raise ValueError(f"record JSON 含非法常量：{constant}")

    try:
        data = json.loads(text, object_pairs_hook=pairs_hook, parse_constant=reject_constant)
    except (json.JSONDecodeError, DuplicateKeyError, ValueError, RecursionError) as exc:
        errors.append(f"record JSON 解析失败：{exc}")
        return None, errors
    if not isinstance(data, dict):
        errors.append("record 顶层必须是 JSON 对象")
        return None, errors
    unknown = sorted(key for key in data if key not in ALIAS_TO_KEY)
    if unknown:
        errors.append(
            "record 含未知字段："
            + "、".join(unknown)
            + "；规范键为 "
            + "、".join(RECORD_KEYS)
        )
        return None, errors
    seen: dict[str, str] = {}
    for alias in data:
        canonical = ALIAS_TO_KEY[alias]
        if canonical in seen:
            errors.append(f"record 字段重复声明：{seen[canonical]} 与 {alias}")
            continue
        seen[canonical] = alias
    if errors:
        return None, errors
    return {ALIAS_TO_KEY[alias]: item for alias, item in data.items()}, []


def _check_worktree_and_head(
    checks: list[dict[str, Any]],
    warnings: list[str],
    requested: Path,
    record: dict[str, Any] | None,
) -> tuple[Path | None, str | None, str | None]:
    """检查 a：工作树存在、分支与 HEAD 与 record 声明一致。"""
    name = "工作树存在与分支/HEAD 一致性"
    if not os.path.isdir(requested):
        add_check(checks, "a", name, "FAIL", f"工作树路径={requested}", "工作树不存在或不是目录")
        return None, None, None
    code, out, err = run_git(("rev-parse", "--show-toplevel"), requested)
    if code != 0:
        detail = err.strip() or f"退出码 {code}"
        add_check(
            checks,
            "a",
            name,
            "FAIL",
            f"命令：{git_command_text(('rev-parse', '--show-toplevel'))}（cwd={requested}）；{detail}",
            "不是可核验的 git 工作树",
        )
        return None, None, None
    worktree_root = Path(os.path.abspath(out.strip()))
    if norm_key(worktree_root) != norm_key(requested):
        warnings.append(f"--worktree 指向 git 工作树内的其他路径，已改用工作树根：{worktree_root}")

    branch_code, branch_out, branch_err = run_git(
        ("rev-parse", "--abbrev-ref", "HEAD"), worktree_root
    )
    head_code, head_out, head_err = run_git(("rev-parse", "HEAD"), worktree_root)
    if branch_code != 0 or head_code != 0:
        detail = (branch_err.strip() or head_err.strip()) or "无法读取分支或 HEAD"
        add_check(checks, "a", name, "FAIL", f"工作树根={worktree_root}；{detail}", "分支/HEAD 读取失败")
        return worktree_root, None, None
    branch = branch_out.strip()
    head = head_out.strip()
    if branch == "HEAD":
        warnings.append("当前处于 detached HEAD，交接行请写明具体提交而不是分支名")

    problems: list[str] = []
    declared_worktree = record_text(record, "worktree")
    if declared_worktree:
        declared_path = to_absolute(declared_worktree, Path.cwd())
        if norm_key(declared_path) != norm_key(worktree_root):
            problems.append(f"record 声明工作树 {declared_path}，实际 {worktree_root}")
    declared_branch = record_text(record, "branch")
    if declared_branch:
        if declared_branch != branch:
            problems.append(f"record 声明分支 {declared_branch}，实际 {branch}")
    declared_commit = record_text(record, "base_commit")
    if declared_commit:
        if not COMMIT_RE.fullmatch(declared_commit):
            problems.append(f"record 起始提交不是 7–40 位十六进制 commit：{declared_commit}")
        elif not head.casefold().startswith(declared_commit.casefold()):
            problems.append(f"record 声明起始提交 {declared_commit}，实际 HEAD {head}")

    declared_bits = []
    if declared_worktree:
        declared_bits.append(f"声明工作树={declared_worktree}")
    if declared_branch:
        declared_bits.append(f"声明分支={declared_branch}")
    if declared_commit:
        declared_bits.append(f"声明起始提交={declared_commit}")
    if record is None:
        declared_bits.append("未提供 record（跳过声明比对）")
    evidence = f"工作树根={worktree_root}；实际分支={branch}；实际HEAD={head}"
    if declared_bits:
        evidence = f"{evidence}；{'；'.join(declared_bits)}"
    if problems:
        add_check(checks, "a", name, "FAIL", evidence, "；".join(problems))
    else:
        add_check(checks, "a", name, "PASS", evidence)
    return worktree_root, branch, head


def _check_index_lock(
    checks: list[dict[str, Any]],
    worktree_root: Path | None,
) -> bool | None:
    """检查 b：用 git rev-parse --git-path 解析 index.lock 后判断存在性。"""
    name = "index.lock 解析与占用"
    if worktree_root is None:
        add_check(checks, "b", name, "SKIP", "工作树未解析，无法定位 index.lock", "依赖检查 a")
        return None
    lock_path, evidence, failure = resolve_index_lock_path(worktree_root)
    if failure is not None:
        add_check(checks, "b", name, "FAIL", evidence, failure)
        return None
    present = os.path.lexists(os.fspath(lock_path))
    evidence = f"{evidence}；存在={present}"
    if present:
        add_check(
            checks,
            "b",
            name,
            "FAIL",
            evidence,
            f"index.lock 存在（{lock_path}）；可能存在未完成的 git 写操作，不得接管或提交",
        )
        return True
    add_check(checks, "b", name, "PASS", evidence)
    return False


def _check_dirty(
    checks: list[dict[str, Any]],
    warnings: list[str],
    worktree_root: Path | None,
    record: dict[str, Any] | None,
) -> None:
    """检查 c：未提交改动计数；有改动时必须声明归属。"""
    name = "未提交改动计数与归属声明"
    if worktree_root is None:
        add_check(checks, "c", name, "SKIP", "工作树未解析，无法读取 git status", "依赖检查 a")
        return
    command_text = git_command_text(("status", "--short"), ("core.quotepath=false",))
    try:
        code, out, err = run_git(
            ("status", "--short"), worktree_root, config=("core.quotepath=false",)
        )
    except GitUnavailableError as exc:
        add_check(checks, "c", name, "FAIL", command_text, str(exc))
        return
    if code != 0:
        detail = err.strip() or f"退出码 {code}"
        add_check(checks, "c", name, "FAIL", f"{command_text}（cwd={worktree_root}）；{detail}", "git status 失败，无法确认未提交改动计数")
        return
    lines = [line for line in out.splitlines() if line.strip()]
    count = len(lines)
    samples = "；".join(lines[:MAX_EVIDENCE_SAMPLES])
    if count > MAX_EVIDENCE_SAMPLES:
        samples = f"{samples}；…（共 {count} 项）"
    declared_owner = declared_text(record, "dirty_owner")
    evidence = f"{command_text}（cwd={worktree_root}）→ 未提交改动 {count} 项"
    if samples:
        evidence = f"{evidence}；样例：{samples}"
    if declared_owner:
        evidence = f"{evidence}；声明归属={declared_owner}"
    if count > 0 and not declared_owner:
        add_check(
            checks,
            "c",
            name,
            "FAIL",
            evidence,
            "存在未提交改动但 record 未声明「未提交改动归属」",
        )
        return
    if count == 0 and declared_owner:
        warnings.append(f"record 声明了未提交改动归属（{declared_owner}），但当前工作树是干净的")
    add_check(checks, "c", name, "PASS", evidence)


def _check_processes(
    checks: list[dict[str, Any]],
    warnings: list[str],
    process_probe: Callable[[], tuple[list[dict[str, str]] | None, str | None]],
) -> bool | None:
    """检查 d：重型进程占用；平台无法枚举时 SKIP 并写明原因。"""
    name = "重型进程占用"
    matched, unavailable = process_probe()
    wanted = "、".join(HEAVY_PROCESS_NAMES)
    if unavailable is not None:
        warnings.append(f"进程占用未能核验：{unavailable}")
        add_check(
            checks,
            "d",
            name,
            "SKIP",
            f"待匹配进程名={wanted}；{unavailable}",
            "当前平台无法枚举进程，不能据此判断资源互斥状态",
        )
        return None
    if matched:
        detail = "；".join(
            f"{entry['image']}(pid={entry['pid'] or '未知'})" for entry in matched
        )
        add_check(
            checks,
            "d",
            name,
            "FAIL",
            f"待匹配进程名={wanted}；命中：{detail}",
            "存在重型进程占用；16 GB 本机同一时刻只允许一个重型综合/实现/整网仿真，"
            "需先核对归属，不代表交接记录本身冲突",
        )
        return True
    add_check(checks, "d", name, "PASS", f"待匹配进程名={wanted}；未发现占用")
    return False


def _check_heartbeat(
    checks: list[dict[str, Any]],
    record: dict[str, Any] | None,
    max_heartbeat_minutes: int,
    now: datetime,
) -> bool | None:
    """检查 e：心跳时效（UTC+8）。返回是否已超时。"""
    name = "交接心跳时效"
    if record is None:
        add_check(checks, "e", name, "SKIP", "未提供 record", "无心跳可核验")
        return None
    raw = record.get("heartbeat_utc8")
    command_text = f"阈值={max_heartbeat_minutes} 分钟；当前时间(UTC+8)={now:%Y-%m-%d %H:%M:%S}"
    if raw is None:
        add_check(checks, "e", name, "FAIL", command_text, "record 缺少 heartbeat_utc8")
        return None
    if not isinstance(raw, str) or not raw.strip():
        add_check(checks, "e", name, "FAIL", command_text, "heartbeat_utc8 必须是非空字符串")
        return None
    heartbeat, failure = parse_heartbeat(raw)
    if heartbeat is None:
        add_check(checks, "e", name, "FAIL", f"heartbeat_utc8={raw}；{command_text}", failure)
        return None
    age = now - heartbeat
    evidence = (
        f"heartbeat_utc8={raw}（归一化 {heartbeat:%Y-%m-%d %H:%M:%S} UTC+8）；"
        f"{command_text}；距今={age.total_seconds() / 60:.1f} 分钟"
    )
    if age > timedelta(minutes=max_heartbeat_minutes):
        add_check(
            checks,
            "e",
            name,
            "FAIL",
            evidence,
            f"心跳超过 {max_heartbeat_minutes} 分钟阈值",
        )
        return True
    if age < -HEARTBEAT_FUTURE_TOLERANCE:
        add_check(
            checks,
            "e",
            name,
            "FAIL",
            evidence,
            f"心跳时间晚于当前时间超过 {HEARTBEAT_FUTURE_TOLERANCE.total_seconds() / 60:.0f} 分钟",
        )
        return None
    add_check(checks, "e", name, "PASS", evidence)
    return False


def _check_status(
    checks: list[dict[str, Any]],
    record: dict[str, Any] | None,
    claim: bool,
) -> None:
    """检查 f：状态机合法性与接管前置条件。"""
    name = "交接状态机与接管条件"
    flow_text = f"状态机：{HANDOFF_STATUS_FLOW}；只有 {TAKEOVER_STATUS} 允许接管"
    if record is None:
        if claim:
            add_check(checks, "f", name, "FAIL", flow_text, "--claim 需要 record 声明 status")
            return
        add_check(checks, "f", name, "SKIP", flow_text, "未提供 record")
        return
    raw = record.get("status")
    if raw is None:
        add_check(checks, "f", name, "FAIL", flow_text, "record 缺少 status")
        return
    if not isinstance(raw, str) or not raw.strip():
        add_check(checks, "f", name, "FAIL", flow_text, "status 必须是非空字符串")
        return
    status_value = raw.strip()
    evidence = f"status={status_value}；{flow_text}"
    if status_value not in HANDOFF_STATUSES:
        add_check(
            checks,
            "f",
            name,
            "FAIL",
            evidence,
            f"非法状态；合法取值为 {'/'.join(HANDOFF_STATUSES)}",
        )
        return
    if claim and status_value != TAKEOVER_STATUS:
        add_check(
            checks,
            "f",
            name,
            "FAIL",
            evidence,
            f"--claim 只允许接管 {TAKEOVER_STATUS} 状态；当前 {status_value} 说明已被占用或本轮已结束",
        )
        return
    if claim:
        evidence = f"{evidence}；--claim 接管条件满足"
    add_check(checks, "f", name, "PASS", evidence)


def _check_evidence_dir(
    checks: list[dict[str, Any]],
    worktree_root: Path | None,
    record: dict[str, Any] | None,
) -> None:
    """检查 g：证据入口存在且含 manifest.json。"""
    name = "证据入口"
    if record is None:
        add_check(checks, "g", name, "SKIP", "未提供 record", "无证据入口可核验")
        return
    raw = record.get("evidence_dir")
    if raw is None:
        add_check(checks, "g", name, "SKIP", "record 未声明 evidence_dir", "本轮无证据入口")
        return
    if not isinstance(raw, str) or not raw.strip():
        add_check(checks, "g", name, "FAIL", f"evidence_dir={raw!r}", "evidence_dir 必须是非空字符串或 null")
        return
    text = raw.strip()
    base = worktree_root if worktree_root is not None else Path.cwd()
    target = to_absolute(text, base)
    evidence = f"evidence_dir={text}；解析路径={target}"
    if worktree_root is not None:
        try:
            common = os.path.commonpath((os.fspath(worktree_root), os.fspath(target)))
        except ValueError:
            common = None
        if common is None or os.path.normcase(common) != os.path.normcase(os.fspath(worktree_root)):
            add_check(checks, "g", name, "FAIL", evidence, "证据入口越出工作树")
            return
    if not os.path.isdir(target):
        add_check(checks, "g", name, "FAIL", evidence, "证据目录不存在或不是目录")
        return
    manifest = target / "manifest.json"
    if not os.path.isfile(manifest):
        add_check(checks, "g", name, "FAIL", f"{evidence}；缺失 {manifest}", "证据目录缺少 manifest.json")
        return
    try:
        size = os.path.getsize(manifest)
    except OSError as exc:
        add_check(checks, "g", name, "FAIL", f"{evidence}；{manifest} 读取失败：{exc}", "manifest.json 不可读")
        return
    add_check(checks, "g", name, "PASS", f"{evidence}；manifest.json={size} 字节")


def _check_allowed_scope(
    checks: list[dict[str, Any]],
    worktree_root: Path | None,
    record: dict[str, Any] | None,
    claimed_paths: Iterable[str],
    claim: bool,
    warnings: list[str],
) -> None:
    """检查 h：允许修改范围非空，且 --claimed-path 不越界。"""
    name = "允许修改范围与越界核验"
    if record is None:
        add_check(checks, "h", name, "SKIP", "未提供 record", "无允许修改范围可核验")
        return
    raw_scope = record.get("allowed_paths")
    if raw_scope is None:
        add_check(checks, "h", name, "FAIL", "record 缺少 allowed_paths", "允许修改范围不能为空")
        return
    if not isinstance(raw_scope, list):
        add_check(checks, "h", name, "FAIL", f"allowed_paths={raw_scope!r}", "allowed_paths 必须是数组")
        return
    scope_entries: list[tuple[str, bool]] = []
    scope_problems: list[str] = []
    for index, item in enumerate(raw_scope):
        if not isinstance(item, str) or not item.strip():
            scope_problems.append(f"allowed_paths[{index}] 必须是非空字符串")
            continue
        if is_placeholder_text(item):
            scope_problems.append(f"allowed_paths[{index}] 是占位内容：{item.strip()}")
            continue
        key, subtree, failure = normalize_scope_entry(item, worktree_root)
        if failure is not None:
            scope_problems.append(f"allowed_paths[{index}]={item.strip()}：{failure}")
            continue
        scope_entries.append((key, subtree))
    display = "、".join(
        f"{entry}/" if subtree else entry for entry, subtree in scope_entries
    )
    evidence = "允许修改范围=" + (display if scope_entries else "<空>")
    if scope_problems:
        add_check(checks, "h", name, "FAIL", evidence, "；".join(scope_problems))
        return
    if not scope_entries:
        add_check(checks, "h", name, "FAIL", evidence, "允许修改范围为空")
        return

    claimed = [item for item in claimed_paths if isinstance(item, str) and item.strip()]
    if not claimed:
        if claim:
            warnings.append("--claim 未同时给出 --claimed-path，本次未做越界核验")
        add_check(checks, "h", name, "PASS", f"{evidence}；未提供 --claimed-path，跳过越界核验")
        return

    claimed_keys: list[str] = []
    violations: list[str] = []
    for item in claimed:
        key, failure = path_scope_key(item, worktree_root)
        if failure is not None:
            violations.append(f"{item.strip()}：{failure}")
            continue
        claimed_keys.append(key)
        if not any(matches_scope(key, entry, subtree) for entry, subtree in scope_entries):
            hint = subtree_hint(key, scope_entries, worktree_root)
            detail = f"{key}：不在允许修改范围内"
            violations.append(f"{detail}（{hint}）" if hint else detail)
    evidence = f"{evidence}；声明要改动的路径=" + "、".join(claimed_keys or ["<无有效路径>"])
    if violations:
        add_check(checks, "h", name, "FAIL", evidence, "；".join(violations))
        return
    add_check(checks, "h", name, "PASS", evidence)


def _check_claim_contract(
    checks: list[dict[str, Any]],
    record: dict[str, Any] | None,
    claim: bool,
) -> None:
    """检查 i：--claim 时的接管让出契约。

    只有 `--claim` 时生效：`yield_statement` 与 `next_owner` 必须非空且非占位
    （`<>` 包裹视为占位）；`heartbeat_utc8` 的可解析性由检查项 e 核验。
    """
    name = "接管让出契约"
    rule = (
        "规则：--claim 时 yield_statement 与 next_owner 必须非空且非占位；"
        "heartbeat_utc8 的可解析性由检查项 e 核验"
    )
    if not claim:
        add_check(checks, "i", name, "SKIP", rule, "未使用 --claim，无需让出契约")
        return
    if record is None:
        add_check(checks, "i", name, "FAIL", rule, "缺少 record，无法核验让出契约字段")
        return
    problems: list[str] = []
    seen: list[str] = []
    for field in CLAIM_CONTRACT_FIELDS:
        raw = record.get(field)
        if not isinstance(raw, str) or not raw.strip():
            problems.append(f"{field}（缺失）")
        elif is_placeholder_text(raw):
            problems.append(f"{field}（占位：{raw.strip()}）")
        else:
            seen.append(f"{field}={raw.strip()}")
    evidence = "；".join([*seen, rule])
    if problems:
        add_check(checks, "i", name, "FAIL", evidence, "让出契约不成立：" + "、".join(problems))
        return
    add_check(checks, "i", name, "PASS", evidence)


def check_handoff(
    worktree_arg: str | None = None,
    record: dict[str, Any] | None = None,
    claimed_paths: Iterable[str] = (),
    max_heartbeat_minutes: int = DEFAULT_MAX_HEARTBEAT_MINUTES,
    claim: bool = False,
    now: datetime | None = None,
    process_probe: Callable[
        [], tuple[list[dict[str, str]] | None, str | None]
    ] = detect_heavy_processes,
) -> dict[str, Any]:
    """执行全部只读检查，返回机器可读结果。"""
    if isinstance(claimed_paths, str):
        raise UsageError("claimed_paths 必须是路径序列，不能是单个字符串")
    if now is None:
        now = datetime.now(UTC8)
    requested = (
        to_absolute(worktree_arg, Path.cwd()) if worktree_arg else default_worktree_root()
    )
    checks: list[dict[str, Any]] = []
    warnings: list[str] = []
    worktree_root, branch, head = _check_worktree_and_head(checks, warnings, requested, record)
    lock_present = _check_index_lock(checks, worktree_root)
    _check_dirty(checks, warnings, worktree_root, record)
    heavy_present = _check_processes(checks, warnings, process_probe)
    heartbeat_expired = _check_heartbeat(checks, record, max_heartbeat_minutes, now)
    _check_status(checks, record, claim)
    _check_evidence_dir(checks, worktree_root, record)
    _check_allowed_scope(
        checks, worktree_root, record, claimed_paths, claim, warnings
    )
    _check_claim_contract(checks, record, claim)

    counts = {"PASS": 0, "FAIL": 0, "SKIP": 0}
    for check in checks:
        counts[check["status"]] = counts.get(check["status"], 0) + 1
    failed = counts["FAIL"] > 0
    lost_contact: bool | None = None
    if record is not None:
        lost_contact = bool(
            heartbeat_expired is True
            and heavy_present is False
            and lock_present is False
        )
    result: dict[str, Any] = {
        "status": "HANDOFF_FAILED" if failed else "HANDOFF_OK",
        "worktree_arg": os.fspath(requested),
        "worktree_root": os.fspath(worktree_root) if worktree_root else None,
        "branch": branch,
        "head": head,
        "record_provided": record is not None,
        "checks": checks,
        "counts": counts,
        "lost_contact": {
            "lost_contact": lost_contact,
            "heartbeat_expired": heartbeat_expired,
            "heavy_processes": heavy_present,
            "index_lock_present": lock_present,
            "note": "只有「心跳超时+无重型进程+无 index.lock」同时成立才可判失联；"
            "否则只能报告，不能自行接管。",
        },
        "warnings": warnings,
        "scope_statement": SCOPE_STATEMENT,
    }
    return result


def exit_code_for(result: dict[str, Any]) -> int:
    """按检查结论给出退出码：0 无 FAIL；1 存在 FAIL。"""
    return 0 if result["counts"]["FAIL"] == 0 else 1


def render_template() -> str:
    """渲染交接行模板与状态机说明（--print-template 输出）。"""
    separator = " | "
    lines = [
        "交接行模板（11 字段，按顺序复制后用真实值替换 <> 占位）：",
        separator.join(TEMPLATE_FIELDS),
        "",
        "占位示例（勿直接当真实记录使用）：",
        separator.join(
            (
                "<任务编号，如 HL-T01>",
                "<负责人，如 DSH/Codex>",
                "<工作树绝对路径>/<分支名>",
                "<起始提交，7–40 位十六进制>",
                "<仓库相对路径，多个用、分隔>",
                "<未提交改动归属；无改动写“无未提交改动”>",
                "<让出声明/未让出声明>",
                "<YYYY-MM-DD HH:MM>",
                "<report/evidence/<task_id>/<run_id> 或 无>",
                "<恢复命令>",
                "<状态> | <下一接手方>",
            )
        ),
        "",
        f"状态机：{HANDOFF_STATUS_FLOW}",
        "- IDLE：任务未发布，无让出方，不可接管。",
        f"- {TAKEOVER_STATUS}：已让出待认领；只有该状态允许新接手方接管（--claim 时校验）。",
        "- CLAIMED / IN_PROGRESS：已有写入方，同一文件不得并发写，不得并发提交。",
        "- DONE：本轮结束；重开需要新任务卡，不能沿用旧交接行。",
        "失联判定：心跳超时 且 无重型进程 且 无 index.lock 三者同时成立才可判失联；"
        "缺一只能报告，不能自行接管。",
        "",
        "JSON 记录键（--record 支持文件路径或内联 JSON，可用中文别名）：",
        "、".join(RECORD_KEYS),
        "允许的别名："
        + "；".join(f"{key}={'/'.join(aliases)}" for key, aliases in RECORD_ALIASES.items()),
        "",
        "字段核验语义（提供 --record 时生效；带“人工核对”的字段不参与机器核验）：",
        *[f"- {key}：{note}；" for key, note in MANUAL_REVIEW_NOTES.items()],
        "- worktree：与 git rev-parse --show-toplevel 精确比对（检查项 a）；",
        "- branch：与 git rev-parse --abbrev-ref HEAD 比对（检查项 a）；",
        "- base_commit：7–40 位十六进制，按前缀与 HEAD 比对（检查项 a）；",
        "- allowed_paths：必须非空，按下方匹配规则与 --claimed-path 比对（检查项 h）；",
        "- dirty_owner：工作树非干净时必须声明归属（检查项 c）；",
        *[f"- {field}：--claim 时必须非空且非占位（检查项 i）；" for field in CLAIM_CONTRACT_FIELDS],
        "- heartbeat_utc8：UTC+8 时间，超过阈值判 FAIL（检查项 e）；",
        "- evidence_dir：目录须存在且含 manifest.json（检查项 g）；",
        "- status：必须是 IDLE/OFFERED/CLAIMED/IN_PROGRESS/DONE，--claim 仅接受 OFFERED（检查项 f）。",
        "",
        "允许修改范围匹配规则（分隔符感知，检查项 h）：",
        "- 精确路径严格相等，不做前缀匹配：dir/a.py 不允许 dir/a.py.bak；",
        "- dir/ 表示子树：覆盖 dir 及其全部子孙；",
        "- * ? [] 只匹配单个路径段，不跨 /：dir/*.py 命中 dir/a.py，不命中 dir/sub/a.py；",
        "- ** 作为独立路径段匹配零个或多个段：dir/** 跨层命中 dir/a.py 与 dir/sub/a.py；",
        "- 反斜杠与 ./ 统一归一化为 / 相对路径；越出工作树的条目直接 FAIL。",
        "",
        "检查项：a 工作树与分支/HEAD 一致性；b index.lock 解析与占用；c 未提交改动归属；"
        "d 重型进程占用；e 心跳时效；f 状态机与接管条件；g 证据入口；h 允许修改范围与越界核验；"
        "i 接管让出契约（仅 --claim 时生效）。",
        "退出码：0 全部 PASS/SKIP；1 存在 FAIL；2 输入或环境错误。",
        "只读声明：本检查器只读文件与 Git 对象，只用 rev-parse/status 且带 --no-optional-locks，"
        "不执行恢复命令，不写仓库文件。",
    ]
    return "\n".join(lines) + "\n"


def render_text(result: dict[str, Any]) -> str:
    """渲染中文文本输出。"""
    lines = [
        f"交接只读核验：{result['worktree_arg']}",
        f"工作树根：{result['worktree_root'] or '<未解析>'}",
        f"分支：{result['branch'] or '<未知>'}",
        f"HEAD：{result['head'] or '<未知>'}",
        f"record：{'已提供' if result['record_provided'] else '未提供'}",
    ]
    for check in result["checks"]:
        lines.append(f"[{check['status']}] {check['id']}. {check['name']}")
        lines.append(f"    证据：{check['evidence']}")
        if check.get("reason"):
            lines.append(f"    说明：{check['reason']}")
    counts = result["counts"]
    lines.append(
        f"结论：{result['status']}（PASS {counts['PASS']}、FAIL {counts['FAIL']}、SKIP {counts['SKIP']}）"
    )
    lines.append(f"退出码：{exit_code_for(result)}")
    lost = result["lost_contact"]
    if lost["lost_contact"] is not None:
        lines.append(
            "失联判定："
            + ("可按失联处理" if lost["lost_contact"] else "不能判失联（见上方检查项）")
            + f"；心跳超时={lost['heartbeat_expired']}、重型进程={lost['heavy_processes']}、"
            f"index.lock={lost['index_lock_present']}"
        )
    for warning in result["warnings"]:
        lines.append(f"提示：{warning}")
    lines.append(f"范围声明：{result['scope_statement']}")
    return "\n".join(lines) + "\n"


def build_parser() -> JsonArgumentParser:
    parser = JsonArgumentParser(
        prog="handoff_check.py",
        allow_abbrev=False,
        description="只读核验 Codex↔DSH 交接记录与目标工作树的一致性",
    )
    parser.add_argument(
        "--worktree",
        help="目标工作树路径；默认本脚本所在仓库的工作树根",
    )
    parser.add_argument(
        "--record",
        help="交接记录：JSON 文件路径或内联 JSON 字符串",
    )
    parser.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    parser.add_argument(
        "--print-template",
        action="store_true",
        help="打印 11 字段交接行模板与状态机取值后退出",
    )
    parser.add_argument(
        "--claim",
        action="store_true",
        help="按接管语义校验（仅 OFFERED 允许接管）",
    )
    parser.add_argument(
        "--claimed-path",
        action="append",
        default=[],
        metavar="PATH",
        help="拟改动的仓库相对路径，可重复；与允许修改范围比对",
    )
    parser.add_argument(
        "--max-heartbeat-minutes",
        type=int,
        default=DEFAULT_MAX_HEARTBEAT_MINUTES,
        help=f"心跳超时阈值（分钟），默认 {DEFAULT_MAX_HEARTBEAT_MINUTES}",
    )
    return parser


def _error_result(message: str) -> dict[str, Any]:
    """构造输入/环境错误结果（退出码 2）。"""
    return {
        "status": "HANDOFF_INPUT_ERROR",
        "worktree_arg": None,
        "worktree_root": None,
        "branch": None,
        "head": None,
        "record_provided": False,
        "checks": [],
        "counts": {"PASS": 0, "FAIL": 0, "SKIP": 0},
        "lost_contact": {
            "lost_contact": None,
            "heartbeat_expired": None,
            "heavy_processes": None,
            "index_lock_present": None,
            "note": "输入或环境错误，未执行检查。",
        },
        "errors": [message],
        "warnings": [],
        "scope_statement": SCOPE_STATEMENT,
    }


def main(argv: list[str] | None = None) -> int:
    """命令行入口，返回进程退出码。"""
    arguments_list = list(sys.argv[1:] if argv is None else argv)
    json_requested = "--json" in arguments_list
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    try:
        arguments = build_parser().parse_args(arguments_list)
    except UsageError as exc:
        message = f"命令行参数错误：{exc}"
        if json_requested:
            print(json.dumps(_error_result(message), ensure_ascii=False, separators=(",", ":")))
        else:
            print(message, file=sys.stderr)
        return 2
    if arguments.print_template:
        sys.stdout.write(render_template())
        return 0
    if arguments.max_heartbeat_minutes <= 0:
        message = "命令行参数错误：--max-heartbeat-minutes 必须是正整数"
        if json_requested:
            print(json.dumps(_error_result(message), ensure_ascii=False, separators=(",", ":")))
        else:
            print(message, file=sys.stderr)
        return 2
    record: dict[str, Any] | None = None
    if arguments.record is not None:
        record, record_errors = load_record(arguments.record)
        if record_errors:
            message = "record 读取失败：" + "；".join(record_errors)
            if json_requested:
                print(json.dumps(_error_result(message), ensure_ascii=False, separators=(",", ":")))
            else:
                print(message, file=sys.stderr)
            return 2
    try:
        result = check_handoff(
            worktree_arg=arguments.worktree,
            record=record,
            claimed_paths=arguments.claimed_path,
            max_heartbeat_minutes=arguments.max_heartbeat_minutes,
            claim=arguments.claim,
        )
    except (UsageError, GitUnavailableError) as exc:
        message = f"输入或环境错误：{exc}"
        if json_requested:
            print(json.dumps(_error_result(message), ensure_ascii=False, separators=(",", ":")))
        else:
            print(message, file=sys.stderr)
        return 2
    except Exception as exc:  # 兜底：核验未完成不得伪装成检查结论
        message = f"检查器未能完成核验：{type(exc).__name__}: {exc}"
        if json_requested:
            print(json.dumps(_error_result(message), ensure_ascii=False, separators=(",", ":")))
        else:
            print(message, file=sys.stderr)
        return 2
    if json_requested:
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    else:
        sys.stdout.write(render_text(result))
    return exit_code_for(result)


if __name__ == "__main__":
    raise SystemExit(main())