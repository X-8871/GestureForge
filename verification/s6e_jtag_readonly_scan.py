"""阶段6只读 JTAG 链/目标扫描的短协调器。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Callable, Sequence


ROOT = Path(r"D:\codex-worktrees\w6")
MAIN_ROOT = Path(r"D:\FPGA_Competition")
SCAN_TCL = Path(r"D:\FPGA_Competition\report\evidence\CTRL-HW-SCAN\hw_scan_20261022_r01\scan2.tcl")
LEASE = Path(r"D:\FPGA_Competition\report\evidence\CTRL-DSH-HANDOFF\dsh_mailbox\DSH-20261027-008-board-lease-stage6.md")
LEASE_MAILBOX = Path(r"D:\FPGA_Competition\report\evidence\CTRL-DSH-HANDOFF\dsh_mailbox")
HW_SERVER = Path(r"D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\hw_server.exe")
XSDB = Path(r"D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\xsdb.exe")
SCAN_SHA256 = "b6987e0a60f4a5a8681f2b3803e60b64b5050a228d9543c3b708cca2e13ba046"
LEASE_SHA256 = "519566fb79202689223e0cd52409b04c072b4cc31ca58270605a104102be88cb"
HW_SERVER_SHA256 = "e1c90dae3564a7d63b48796a8ed9373a4a00e5e70f2312651cff77c48a6399f3"
XSDB_SHA256 = "664dc93eb6cec40a2596162dbdf9bc42d5ab96ffbfc34d7515f8c68072fbac55"
REVIEW_RECEIPT = ROOT / "report" / "evidence" / "S6-E" / "s6e_jtag_readonly_prep_20261027_r06" / "reviewer_receipt.json"
RUN_ID = re.compile(r"s6e_jtag_readonly_[0-9]{8}_r[0-9]{2}\Z")
TASK_ID = "S6E-JTAG-RO::s6_hardware_session_handoff"
SCOPE = "S6E_JTAG_READONLY_DIAGNOSTIC"
PORT = 3121
BUSY_NAMES = {"hw_server.exe", "xsdb.exe", "vivado.exe", "xsim.exe", "vitis.exe"}
LOCAL_TZ = timezone(timedelta(hours=8))
HANDOFF_FIELDS = (
    "任务", "负责人", "工作树/分支", "起始提交", "允许修改范围", "未提交改动归属",
    "让出声明", "心跳(UTC+8)", "证据入口", "恢复命令", "状态/下一接手方",
)
CLAIM_KEYS = ("offer_commit", "offer_blob_oid", "offer_sha256", "offer_source_commit", "hardware_run_id", "scope")
EXPECTED_TEST_COMMAND = (
    r"C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
    "-B", "-m", "unittest", "test_s6e_jtag_readonly_scan", "-v",
)
EXPECTED_TEST_WORKDIR = r"D:\codex-worktrees\w6\verification"


class ScanError(RuntimeError):
    """扫描准备或执行失败。"""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_bytes(root: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, timeout=10, check=False)
    if result.returncode != 0:
        raise ScanError(f"Git 核验失败：{args}; exit={result.returncode}")
    return result.stdout


def _git_text(root: Path, *args: str) -> str:
    return _git_bytes(root, *args).decode("utf-8", errors="strict").strip()


def _safe_repo_file(root: Path, relative_text: str, label: str) -> Path:
    relative = Path(relative_text)
    if relative.is_absolute() or relative.drive or ".." in relative.parts:
        raise ScanError(f"{label}路径越界：{relative_text}")
    try:
        root_real = root.resolve(strict=True)
        path_real = (root / relative).resolve(strict=True)
    except OSError as exc:
        raise ScanError(f"{label}路径不可解析：{relative_text}") from exc
    if not path_real.is_relative_to(root_real) or not path_real.is_file():
        raise ScanError(f"{label}文件缺失或解析到工作树外：{relative_text}")
    return path_real


def _clock_interval(day, clock: str, tzinfo) -> tuple[datetime, datetime] | None:
    """按原始精度生成闭开时间区间；未知分钟个位只接受 x 标记。"""
    pieces = clock.split(":")
    if len(pieces) not in (2, 3):
        return None
    hour_text, minute_text = pieces[:2]
    if not re.fullmatch(r"[0-9]{2}", hour_text):
        return None
    if re.fullmatch(r"[0-5][xX]", minute_text) and len(pieces) == 2:
        hour = int(hour_text)
        minute = int(minute_text[0]) * 10
        try:
            start = datetime(day.year, day.month, day.day, hour, minute, tzinfo=tzinfo)
        except ValueError:
            return None
        return start, start + timedelta(minutes=10)
    if not re.fullmatch(r"[0-5][0-9]", minute_text):
        return None
    second_text = pieces[2] if len(pieces) == 3 else None
    if second_text is not None and not re.fullmatch(r"[0-5][0-9]", second_text):
        return None
    try:
        start = datetime(
            day.year,
            day.month,
            day.day,
            int(hour_text),
            int(minute_text),
            int(second_text or "0"),
            tzinfo=tzinfo,
        )
    except ValueError:
        return None
    return start, start + (timedelta(seconds=1) if second_text is not None else timedelta(minutes=1))


def _mail_time_interval(text: str) -> tuple[datetime, datetime, str] | None:
    """只解析唯一明确的通知元数据时间字段，并保留其原始文本。"""
    clock_pattern = r"[0-9]{2}:(?:[0-5][0-9]|[0-5][xX])(?::[0-5][0-9])?"
    label_pattern = re.compile(r"(?:时间|日期)(?:[ \t]*[（(]UTC\+8[）)])?[ \t]*[：:]")
    date_pattern = r"[0-9]{4}-[0-9]{2}-[0-9]{2}"
    zone_suffix_pattern = r"(?P<zone_suffix>[ \t]*(?:[（(][A-Za-z][A-Za-z0-9+:-]*[）)]|[A-Za-z][A-Za-z0-9+:-]*))?"
    labels = list(label_pattern.finditer(text))
    if len(labels) != 1:
        return None
    label = labels[0]
    line_end = text.find("\n", label.end())
    if line_end < 0:
        line_end = len(text)
    value_end = line_end
    for delimiter in ("；", ";", "｜", "|"):
        delimiter_pos = text.find(delimiter, label.end(), line_end)
        if delimiter_pos >= 0:
            value_end = min(value_end, delimiter_pos)
    raw_value = text[label.end():value_end].strip(" \t\r")
    value = raw_value[:-1].rstrip(" \t\r") if raw_value.endswith(("。", ".")) else raw_value
    if not value:
        return None
    raw_field = text[label.start():value_end].strip(" \t\r")
    if raw_field.endswith(("。", ".")):
        raw_field = raw_field[:-1]
    time_pattern = (
        r"(?P<date>" + date_pattern + r")(?P<date_time_sep>[ T])(?P<start_clock>"
        + clock_pattern
        + r")(?:(?:[ \t]*[–—][ \t]*|[ \t]+-[ \t]*|-[ \t]+)(?P<end_clock>"
        + clock_pattern
        + r"))?(?P<offset>[+-][0-9]{2}:[0-9]{2})?"
        + zone_suffix_pattern
    )
    match = re.fullmatch(time_pattern, value)
    if match is None:
        date_match = re.fullmatch(r"(?P<date>" + date_pattern + r")" + zone_suffix_pattern, value)
        if date_match is None or not _supported_mail_zone_suffix(date_match.group("zone_suffix")):
            return None
        try:
            from datetime import date

            day = date.fromisoformat(date_match.group("date"))
            start = datetime(day.year, day.month, day.day, tzinfo=LOCAL_TZ)
            return start, start + timedelta(days=1), raw_field
        except (ValueError, OverflowError):
            return None
    if not _supported_mail_zone_suffix(match.group("zone_suffix")):
        return None
    if match.group("offset") is not None and match.group("zone_suffix") is not None:
        return None
    try:
        from datetime import date

        day = date.fromisoformat(match.group("date"))
        offset = match.group("offset") or ""
        if offset.startswith("-") and match.group("date_time_sep") != "T":
            return None
        tzinfo = datetime.fromisoformat(f"2000-01-01T00:00{offset}").tzinfo or LOCAL_TZ
        first = _clock_interval(day, match.group("start_clock"), tzinfo)
        if first is None:
            return None
        if match.group("end_clock") is None:
            start, end = first
        else:
            last = _clock_interval(day, match.group("end_clock"), tzinfo)
            if last is None:
                return None
            last_start, end = last
            if last_start <= first[0]:
                return None
            if last_start < first[1]:
                return None
            start = first[0]
        return start.astimezone(LOCAL_TZ), end.astimezone(LOCAL_TZ), raw_field
    except (ValueError, OverflowError):
        return None


def _supported_mail_zone_suffix(suffix: str | None) -> bool:
    """仅接受完整 UTC+8 后缀；其他显式时区不得退回本地时间。"""
    if suffix is None:
        return True
    token = suffix.strip(" \t")
    if len(token) >= 2 and token[0] in "（(" and token[-1] in "）)":
        token = token[1:-1]
    return token == "UTC+8"


def _mail_timestamp(text: str) -> datetime | None:
    """兼容旧调用者，返回时间区间的最早可能时刻。"""
    interval = _mail_time_interval(text)
    return interval[0] if interval is not None else None


def _format_utc8(value: datetime) -> str:
    precision = "seconds" if value.second or value.microsecond else "minutes"
    return value.astimezone(LOCAL_TZ).isoformat(timespec=precision)


def _time_evidence(interval: tuple[datetime, datetime, str]) -> dict:
    start, end, raw_text = interval
    return {
        "time_utc8": _format_utc8(start),
        "time_range_utc8": {"start_inclusive": _format_utc8(start), "end_exclusive": _format_utc8(end)},
        "timestamp_text": raw_text,
    }


def lease_snapshot(lease_path: Path = LEASE, mailbox: Path = LEASE_MAILBOX) -> dict:
    """返回带租约及通知路径、SHA、UTC+8 时间的可审计状态。"""
    snapshot = {
        "valid": False,
        "reason": "租约状态未核验",
        "lease_file": {"path": str(lease_path), "hash_basis": "worktree_disk",
                       "expected_sha256": LEASE_SHA256, "observed_sha256": None, "valid": False},
        "mailbox_path": str(mailbox),
        "events": [],
    }
    if not lease_path.is_file():
        snapshot["reason"] = "DSH-20261027-008 缺失"
        return snapshot
    try:
        lease_bytes = lease_path.read_bytes()
        lease_sha = hashlib.sha256(lease_bytes).hexdigest()
        text = lease_bytes.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        snapshot["reason"] = f"DSH-20261027-008 不可读：{exc}"
        return snapshot
    snapshot["lease_file"]["observed_sha256"] = lease_sha
    if lease_sha != LEASE_SHA256:
        snapshot["reason"] = "DSH-20261027-008 原始 SHA-256 已变化"
        return snapshot
    if "允许 Codex 阶段6 使用板卡" not in text:
        snapshot["reason"] = "固定租约缺少阶段6授权语句"
        return snapshot
    snapshot["lease_file"]["valid"] = True
    if not mailbox.is_dir():
        snapshot["lease_file"]["valid"] = False
        snapshot["reason"] = "DSH mailbox 不可读取，无法核验召回状态"
        return snapshot
    events: list[tuple[datetime, datetime, str, str, str, str]] = []
    unknown_events: list[tuple[tuple[datetime, datetime, str] | None, str, str, bool]] = []
    recall_markers = (
        "板卡归还通知", "板卡归还", "板卡已归还", "暂勿开启新的板级会话", "暂勿开启",
        "不要开启新的板级会话", "租约已收回", "收回本次阶段6租用", "暂停板卡使用", "暂停板级会话",
    )
    relevant_markers = ("阶段6", "S6-E", "S6E-JTAG-RO")
    board_action_markers = ("板卡", "板级", "租约", "租用", "会话", "JTAG", "hw_server", "xsdb")
    board_status_markers = (
        "板卡状态", "板卡使用", "板卡占用", "板级会话", "租约", "租用", "归还", "释放", "召回", "暂停",
    )
    for path in sorted(mailbox.glob("DSH-*.md")):
        if not path.is_file():
            continue
        try:
            event_bytes = path.read_bytes()
            body = event_bytes.decode("utf-8")
        except (OSError, UnicodeError) as exc:
            snapshot["lease_file"]["valid"] = False
            snapshot["reason"] = f"DSH mailbox 记录不可读：{path.name}: {exc}"
            return snapshot
        stamp = _mail_time_interval(body)
        heading = next((line.strip() for line in body.splitlines() if line.strip()), "")
        stage_mentions: set[str] = set()
        for stage_group in re.findall(r"阶段\s*([0-9]+(?:\s*/\s*[0-9]+)*)", body):
            stage_mentions.update(re.findall(r"[0-9]+", stage_group))
        explicit_stage6 = "6" in stage_mentions or any(marker in body for marker in relevant_markers)
        stage5_only = stage_mentions == {"5"} and not explicit_stage6
        is_recall = any(marker in body for marker in recall_markers) or any(
            marker in heading for marker in ("板卡归还", "阶段6租用召回", "阶段6租用收回")
        )
        is_release = (
            "板卡已释放" in heading
            and ("DSH-20261027-009" in body or "租用条款" in body)
            and any(marker in body for marker in ("可以开启", "可开启", "恢复有效", "恢复租用"))
        )
        if is_recall and is_release:
            snapshot["lease_file"]["valid"] = False
            snapshot["reason"] = f"单条记录同时含召回与释放语义，无法核验：{path.name}"
            return snapshot
        if is_release or is_recall:
            if stamp is None:
                snapshot["lease_file"]["valid"] = False
                snapshot["reason"] = f"召回/释放记录缺少可解析 UTC+8 时间：{path.name}"
                return snapshot
            events.append((stamp[0], stamp[1], "RELEASED" if is_release else "RECALLED", str(path),
                           hashlib.sha256(event_bytes).hexdigest(), stamp[2]))
        elif path.resolve() != lease_path.resolve() and any(marker in body for marker in board_action_markers) and (
            explicit_stage6 or stage5_only or any(marker in body for marker in board_status_markers)
        ):
            unknown_events.append((stamp, str(path), hashlib.sha256(event_bytes).hexdigest(), stage5_only))
    events.sort(key=lambda item: (item[0], item[1], item[3]))
    snapshot["events"] = []
    for start, end, kind, path, digest, raw_text in events:
        item = {"event": kind, "path": path, "hash_basis": "worktree_disk", "sha256": digest}
        item.update(_time_evidence((start, end, raw_text)))
        snapshot["events"].append(item)
    for previous, current in zip(events, events[1:]):
        if previous[1] > current[0]:
            snapshot["reason"] = "召回与释放时间区间重叠，无法确认先后"
            return snapshot
    lease_stamp = _mail_time_interval(text)
    latest_known_interval = (events[-1][0], events[-1][1]) if events else (
        (lease_stamp[0], lease_stamp[1]) if lease_stamp is not None else None
    )
    for stamp, path, digest, stage5_only in unknown_events:
        if stamp is None:
            item = {"event": "UNKNOWN_RELEVANT_NOTICE", "path": path, "hash_basis": "worktree_disk",
                    "sha256": digest, "time_utc8": None, "time_range_utc8": None, "timestamp_text": None}
            snapshot["events"].append(item)
            snapshot["reason"] = f"阶段6相关板卡通知缺少可解析 UTC+8 时间，按未知召回阻断：{Path(path).name}"
            return snapshot
        reference_start, reference_end = latest_known_interval or (None, None)
        if reference_start is not None and stamp[1] <= reference_start:
            kind = "OUT_OF_SCOPE_STAGE5_PRE_RELEASE" if stage5_only else "UNKNOWN_RELEVANT_NOTICE_PRE_RELEASE"
            item = {"event": kind, "path": path, "hash_basis": "worktree_disk", "sha256": digest}
            item.update(_time_evidence(stamp))
            snapshot["events"].append(item)
            continue
        if reference_start is None or reference_end is None or stamp[0] < reference_end:
            item = {"event": "UNKNOWN_RELEVANT_NOTICE", "path": path, "hash_basis": "worktree_disk",
                    "sha256": digest}
            item.update(_time_evidence(stamp))
            snapshot["events"].append(item)
            snapshot["reason"] = f"阶段6相关板卡通知时间与有效租约边界重叠或更晚，按未知召回阻断：{Path(path).name}"
            return snapshot
        item = {"event": "UNKNOWN_RELEVANT_NOTICE", "path": path, "hash_basis": "worktree_disk",
                "sha256": digest}
        item.update(_time_evidence(stamp))
        snapshot["events"].append(item)
        snapshot["reason"] = f"存在较新的阶段6相关板卡通知，未能识别其租约语义，按未知召回阻断：{Path(path).name}"
        return snapshot
    if not events:
        snapshot["valid"] = True
        snapshot["reason"] = "固定租约有效，未发现后续召回或未知相关通知"
        return snapshot
    latest = events[-1]
    if latest[2] != "RELEASED":
        snapshot["reason"] = f"租约已被后续通知召回，等待 DSH 明确释放：{Path(latest[3]).name}"
        return snapshot
    snapshot["valid"] = True
    snapshot["reason"] = f"最近一条有效通知为释放：{Path(latest[3]).name}"
    return snapshot


def lease_status(lease_path: Path = LEASE, mailbox: Path = LEASE_MAILBOX) -> tuple[bool, str]:
    """保留简洁调用口；运行证据使用 lease_snapshot 绑定通知来源。"""
    snapshot = lease_snapshot(lease_path, mailbox)
    return snapshot["valid"], snapshot["reason"]


def _row_for_task(state_text: str, expected_status: str, run_id: str) -> tuple[str, dict[str, str]]:
    rows = [line.strip() for line in state_text.splitlines() if TASK_ID in line]
    if len(rows) != 1:
        raise ScanError(f"正式交接状态中任务行必须唯一，实际 {len(rows)} 行")
    row = rows[0]
    missing = [field for field in HANDOFF_FIELDS if field not in row]
    if missing:
        raise ScanError(f"11字段交接行不完整：{missing}")
    status_value = _handoff_field(row, "状态/下一接手方")
    status_token = status_value.split(maxsplit=1)[0].strip("`.,;:") if status_value else ""
    if status_token.upper() != expected_status:
        raise ScanError(f"正式交接状态不是 {expected_status}")
    values: dict[str, str] = {}
    keys = CLAIM_KEYS if expected_status == "CLAIMED" else ("hardware_run_id", "scope")
    for key in keys:
        match = re.search(rf"(?:^|[;|=\s]){re.escape(key)}\s*=\s*`?([^;|\s`]+)", row)
        if match is None:
            raise ScanError(f"交接证据入口缺少 {key}")
        values[key] = match.group(1).strip("`.,")
    if values.get("hardware_run_id") != run_id or values.get("scope") != SCOPE:
        raise ScanError("交接 RunId/scope 与只读扫描不匹配")
    if expected_status == "CLAIMED":
        for key in ("offer_commit", "offer_blob_oid", "offer_source_commit"):
            if not re.fullmatch(r"[0-9a-f]{40}", values[key]):
                raise ScanError(f"{key} 不是完整 Git OID")
        if not re.fullmatch(r"[0-9a-f]{64}", values["offer_sha256"]):
            raise ScanError("offer_sha256 不是完整 SHA-256")
    return row, values


def _handoff_field(row: str, field: str) -> str:
    match = re.search(rf"(?:^|\|\s*){re.escape(field)}\s*[:=：]\s*([^|]*)", row)
    return "" if match is None else match.group(1).strip()


def validate_claim_rows(main_text: str, w6_text: str, run_id: str) -> dict:
    """从正式 main OFFER 与 w6 CLAIMED 行提取并匹配交接字段。"""
    main_row, main_values = _row_for_task(main_text, "OFFERED", run_id)
    w6_row, w6_values = _row_for_task(w6_text, "CLAIMED", run_id)
    if main_values["hardware_run_id"] != w6_values["hardware_run_id"] or main_values["scope"] != w6_values["scope"]:
        raise ScanError("main OFFER 与 w6 CLAIMED 的 RunId/scope 不一致")
    path_branch = _handoff_field(w6_row, "工作树/分支")
    expected_path = re.escape(r"D:\codex-worktrees\w6")
    if re.fullmatch(rf"\s*`?{expected_path}`?\s*/\s*`?stage6-interact-prep`?\s*", path_branch) is None:
        raise ScanError("w6 CLAIM 行未绑定目标工作树与分支")
    return {"main_offer_row": main_row, "w6_claim_row": w6_row, **w6_values}


def verify_formal_claim(run_id: str) -> dict:
    main_state = MAIN_ROOT / ".codex" / "STATE.md"
    w6_state = ROOT / ".codex" / "STATE.md"
    main_current = main_state.read_text(encoding="utf-8")
    w6_current = w6_state.read_text(encoding="utf-8")
    claim = validate_claim_rows(main_current, w6_current, run_id)
    main_head = _git_text(MAIN_ROOT, "rev-parse", "HEAD")
    w6_head = _git_text(ROOT, "rev-parse", "HEAD")
    main_committed = _git_bytes(MAIN_ROOT, "show", f"{main_head}:.codex/STATE.md").decode("utf-8")
    w6_committed = _git_bytes(ROOT, "show", f"{w6_head}:.codex/STATE.md").decode("utf-8")
    if claim["main_offer_row"] not in main_committed or claim["w6_claim_row"] not in w6_committed:
        raise ScanError("正式 OFFER/CLAIM 行尚未提交或已与 HEAD 不同")
    offer_commit = claim["offer_commit"]
    offer_source_commit = claim["offer_source_commit"]
    blob_path = f"{offer_commit}:.codex/STATE.md"
    blob_oid = _git_text(MAIN_ROOT, "rev-parse", blob_path)
    blob = _git_bytes(MAIN_ROOT, "show", blob_path)
    if blob_oid != claim["offer_blob_oid"] or hashlib.sha256(blob).hexdigest() != claim["offer_sha256"]:
        raise ScanError("offer_commit/blob_oid/sha256 绑定不一致")
    if claim["main_offer_row"].encode("utf-8") not in blob:
        raise ScanError("OFFER 行不在 offer_commit 的 main STATE blob 中")
    for source in (offer_commit, offer_source_commit):
        _git_bytes(MAIN_ROOT, "cat-file", "-e", f"{source}^{{commit}}")
    for ancestor_commit, descendant in ((offer_commit, main_head), (offer_source_commit, offer_commit)):
        result = subprocess.run(["git", "-C", str(MAIN_ROOT), "merge-base", "--is-ancestor", ancestor_commit, descendant],
                                capture_output=True, timeout=10, check=False)
        if result.returncode != 0:
            raise ScanError(f"main OFFER/source 提交不在要求的祖先关系中：{ancestor_commit} -> {descendant}")
    return {"status": "FORMAL_CLAIM_VERIFIED", "hardware_run_id": run_id, "scope": SCOPE,
            "offer_commit": offer_commit, "offer_blob_oid": blob_oid, "offer_sha256": hashlib.sha256(blob).hexdigest(),
            "offer_hash_basis": "commit_blob",
            "main_state_head": main_head, "w6_state_head": w6_head}


def validate_review_receipt(receipt: dict, run_id: str, root: Path = ROOT) -> dict:
    """校验审查回执、被审源码字节和提交 blob 三者一致。"""
    if receipt.get("schema_version") != 1 or receipt.get("review_status") != "PASS":
        raise ScanError("独立审查回执缺失或未 PASS")
    if receipt.get("task_id") != "S6E-JTAG-RO" or receipt.get("scope") != SCOPE or receipt.get("run_id") != run_id:
        raise ScanError("Reviewer 回执任务/scope 不匹配")
    if not isinstance(receipt.get("reviewer_id"), str) or not receipt["reviewer_id"].strip():
        raise ScanError("Reviewer 回执缺少独立审查者标识")
    if type(receipt.get("blocking_findings")) is not int or receipt["blocking_findings"] != 0:
        raise ScanError("Reviewer 回执仍有阻断问题")
    tests = receipt.get("tests")
    if not isinstance(tests, dict):
        raise ScanError("Reviewer 回执缺少测试结果")
    if tuple(tests.get("command", ())) != EXPECTED_TEST_COMMAND:
        raise ScanError("Reviewer 测试命令与固定审查命令不一致")
    if tests.get("working_directory") != EXPECTED_TEST_WORKDIR:
        raise ScanError("Reviewer 测试工作目录不一致")
    if type(tests.get("exit_code")) is not int or tests.get("exit_code") != 0:
        raise ScanError("Reviewer 回执未绑定通过的离线测试命令/退出码")
    commit = receipt.get("reviewed_commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ScanError("Reviewer 回执缺少被审提交")
    files = receipt.get("reviewed_files")
    expected = {"verification/s6e_jtag_readonly_scan.py", "verification/test_s6e_jtag_readonly_scan.py"}
    if not isinstance(files, dict) or set(files) != expected:
        raise ScanError("Reviewer 回执未恰好绑定扫描器与测试文件")
    for rel in sorted(expected):
        item = files[rel]
        if not isinstance(item, dict):
            raise ScanError(f"Reviewer 文件哈希记录格式错误：{rel}")
        disk_path = _safe_repo_file(root, rel, "Reviewer 源码")
        if item.get("worktree_disk_hash_basis") != "worktree_disk" or item.get("commit_blob_hash_basis") != "commit_blob":
            raise ScanError(f"Reviewer 源码哈希缺少正确 hash_basis：{rel}")
        if not disk_path.is_file():
            raise ScanError(f"Reviewer 被审文件缺失：{rel}")
        disk_sha = sha256(disk_path)
        if item.get("worktree_disk_sha256") != disk_sha:
            raise ScanError(f"Reviewer 被审磁盘字节与当前文件不一致：{rel}")
        blob_path = f"{commit}:{rel}"
        blob_oid = _git_text(root, "rev-parse", blob_path)
        blob = _git_bytes(root, "show", blob_path)
        blob_sha = hashlib.sha256(blob).hexdigest()
        if item.get("commit_blob_oid") != blob_oid or item.get("commit_blob_sha256") != blob_sha:
            raise ScanError(f"Reviewer 回执的 Git blob 与提交不一致：{rel}")
        if disk_sha != blob_sha:
            raise ScanError(f"Reviewer 工作树源码与提交 blob 字节不一致：{rel}")
    head = _git_text(root, "rev-parse", "HEAD")
    ancestor = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", commit, head],
                              capture_output=True, timeout=10, check=False)
    if ancestor.returncode != 0:
        raise ScanError("被审提交不在当前 w6 HEAD 历史中")
    evidence_path = receipt.get("review_evidence_path")
    evidence_sha = receipt.get("review_evidence_sha256")
    test_log = tests.get("log_path")
    test_sha = tests.get("log_sha256")
    for rel, expected_sha, label in ((evidence_path, evidence_sha, "审查证据"), (test_log, test_sha, "测试日志")):
        if not isinstance(rel, str) or not isinstance(expected_sha, str):
            raise ScanError(f"Reviewer 回执缺少{label}路径/哈希")
        if label == "审查证据" and receipt.get("review_evidence_hash_basis") != "worktree_disk":
            raise ScanError("Reviewer 审查证据 SHA 缺少 worktree_disk 基座")
        if label == "测试日志" and tests.get("log_hash_basis") != "worktree_disk":
            raise ScanError("Reviewer 测试日志 SHA 缺少 worktree_disk 基座")
        path = _safe_repo_file(root, rel, f"Reviewer {label}")
        if not path.is_file() or sha256(path) != expected_sha:
            raise ScanError(f"Reviewer {label}缺失或哈希不符")
    test_log_path = _safe_repo_file(root, test_log, "Reviewer 测试日志")
    test_summary = _parse_test_summary(test_log_path)
    if tests.get("summary") != test_summary or test_summary["tests_run"] < 1 or test_summary["skipped"] != 0:
        raise ScanError("Reviewer 测试日志成功摘要缺失、跳过测试或与回执摘要不一致")
    return {"status": "REVIEW_RECEIPT_VERIFIED", "reviewed_commit": commit,
            "receipt_sha256": hashlib.sha256(json.dumps(receipt, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest(),
            "reviewer_id": receipt["reviewer_id"], "test_exit_code": tests["exit_code"]}


def _parse_test_summary(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ScanError(f"离线测试日志不可读：{path}") from exc
    ran = re.findall(r"^Ran (0|[1-9][0-9]*) tests? in [0-9]+(?:\.[0-9]+)?s$", text, re.MULTILINE)
    passed = re.findall(r"^OK(?: \(skipped=([0-9]+)\))?\s*$", text, re.MULTILINE)
    if len(ran) != 1 or len(passed) != 1 or re.search(r"^(?:FAILED|ERROR:|FAIL:)", text, re.MULTILINE):
        raise ScanError("离线测试日志没有唯一的成功摘要")
    skipped = int(passed[0]) if passed[0] else 0
    return {"tests_run": int(ran[0]), "failures": 0, "errors": 0, "skipped": skipped, "success_marker": "OK"}


def tasklist_names(output: str) -> set[str]:
    names = {row[0].strip().lower() for row in csv.reader(output.splitlines()) if len(row) > 1 and row[1].strip().isdigit()}
    if not names:
        raise ScanError("tasklist 未返回可核验进程列表，停止")
    return names


def port_3121_listeners(output: str) -> list[int]:
    owners = []
    saw_tcp = False
    for line in output.splitlines():
        fields = line.split()
        if fields and fields[0].upper() == "TCP":
            saw_tcp = True
        if len(fields) >= 5 and fields[0].upper() == "TCP" and fields[1].strip("[]").endswith(f":{PORT}"):
            if fields[-2].upper() == "LISTENING":
                if not fields[-1].isdigit():
                    raise ScanError("netstat 3121 监听行缺少 PID，停止")
                owners.append(int(fields[-1]))
    if not saw_tcp and not any("proto" in line.lower() or "协议" in line for line in output.splitlines()):
        raise ScanError("netstat 输出无法识别 TCP 表头/连接行，停止")
    return owners


def _process_snapshot() -> set[str]:
    result = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True, encoding="mbcs", errors="replace", timeout=10)
    if result.returncode:
        raise ScanError(f"tasklist 失败，退出码 {result.returncode}")
    return tasklist_names(result.stdout)


def _listener_snapshot() -> list[int]:
    result = subprocess.run(["netstat", "-ano", "-p", "tcp"], capture_output=True, text=True, encoding="ascii", errors="replace", timeout=10)
    if result.returncode:
        raise ScanError(f"netstat 失败，退出码 {result.returncode}")
    return port_3121_listeners(result.stdout)


def _static_inputs() -> dict:
    for path in (SCAN_TCL, LEASE, HW_SERVER, XSDB):
        if not path.is_file():
            raise ScanError(f"缺少精确路径文件：{path}")
    expected = {SCAN_TCL: SCAN_SHA256, LEASE: LEASE_SHA256, HW_SERVER: HW_SERVER_SHA256, XSDB: XSDB_SHA256}
    actual = {str(path): sha256(path) for path in expected}
    for path, expected_sha in expected.items():
        if actual[str(path)] != expected_sha:
            raise ScanError(f"固定输入 SHA-256 已变化：{path}; observed={actual[str(path)]}")
    lease_text = LEASE.read_text(encoding="utf-8")
    if "允许 Codex 阶段6 使用板卡" not in lease_text:
        raise ScanError("DSH-20261027-008 未包含阶段6板卡租用授权")
    return actual


def _check_idle(process_query: Callable[[], set[str]], port_query: Callable[[], list[int]]) -> None:
    busy = sorted(process_query() & BUSY_NAMES)
    if busy:
        raise ScanError(f"发现相关进程，停止且不触碰：{busy}")
    listeners = port_query()
    if listeners:
        raise ScanError(f"TCP 3121 已有 LISTEN，停止且不触碰：{listeners}")


def _stop_own_process(proc: subprocess.Popen | None) -> str:
    """只通过本次 Popen 句柄停止本次创建的进程。"""
    if proc is None or proc.poll() is not None:
        return "ALREADY_EXITED"
    proc.terminate()
    try:
        proc.wait(timeout=5)
        return "TERMINATED_OWN_PROCESS"
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
        return "KILLED_OWN_PROCESS_AFTER_TIMEOUT"


def _safe_stop(proc: subprocess.Popen | None) -> str:
    try:
        return _stop_own_process(proc)
    except (OSError, subprocess.SubprocessError) as exc:
        return f"STOP_FAILED: {exc}"


def _validate_output(output: str, returncode: int) -> list[str]:
    errors = []
    if returncode != 0:
        errors.append(f"XSDB exit={returncode}")
    connected = re.findall(r"^SCAN2_CONNECTED=1\s*$", output, re.MULTILINE)
    disconnected = re.findall(r"^SCAN2_DISCONNECTED=1\s*$", output, re.MULTILINE)
    count_values = re.findall(r"^SCAN2_TARGET_COUNT=([0-9]+)\s*$", output, re.MULTILINE)
    chain_values = re.findall(r"^SCAN2_JTAG_CHAIN=(.*)$", output, re.MULTILINE)
    target_values = re.findall(r"^SCAN2_TARGET=(.*)$", output, re.MULTILINE)
    if len(connected) != 1 or len(disconnected) != 1:
        errors.append("connect/disconnect 标记必须各出现一次")
    if len(count_values) != 1:
        errors.append(f"目标数量标记必须唯一，实际 {len(count_values)} 个")
    if len(chain_values) != 1 or not chain_values[0].strip():
        errors.append(f"JTAG 链标记必须唯一且非空，实际 {len(chain_values)} 个")
    if count_values:
        count = int(count_values[0])
        if count < 1:
            errors.append("JTAG 目标数为零")
        if len(target_values) != count:
            errors.append(f"目标明细数与目标数量不一致：{len(target_values)} != {count}")
    if any(not item.strip() for item in target_values):
        errors.append("目标明细含空项")
    if any(marker in output for marker in ("SCAN2_CONNECT_FAIL=", "SCAN2_TARGETS_FAIL=", "SCAN2_JTAG_CMD_UNAVAILABLE=")):
        errors.append("scan2.tcl 报告连接/目标/链路错误")
    return errors


def _write_json_atomic(path: Path, value: dict) -> None:
    temporary = path.with_name(path.name + ".partial")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _read_review_receipt(path: Path, run_id: str) -> tuple[dict, dict]:
    if not path.is_file():
        raise ScanError(f"缺少独立 Reviewer PASS 回执：{path}")
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ScanError(f"Reviewer 回执不可读或 JSON 无效：{path}") from exc
    if not isinstance(receipt, dict):
        raise ScanError("Reviewer 回执根节点必须是对象")
    summary = validate_review_receipt(receipt, run_id)
    summary["receipt_file_sha256"] = sha256(path)
    return receipt, summary


def _record_lease_snapshot(record: dict, phase: str, snapshot: dict) -> None:
    evidence = record.setdefault("lease_evidence", {"lease_versions": [], "events": [], "checks": []})
    lease_file = snapshot.get("lease_file", {})
    version = {
        "path": lease_file.get("path"),
        "hash_basis": lease_file.get("hash_basis", "worktree_disk"),
        "expected_sha256": lease_file.get("expected_sha256"),
        "observed_sha256": lease_file.get("observed_sha256"),
        "valid": lease_file.get("valid", False),
    }
    if version not in evidence["lease_versions"]:
        evidence["lease_versions"].append(version)
    for event in snapshot.get("events", []):
        if not any(old.get("path") == event.get("path") and old.get("sha256") == event.get("sha256")
                   for old in evidence["events"]):
            evidence["events"].append(event)
    evidence["mailbox_path"] = snapshot.get("mailbox_path")
    evidence["checks"].append({
        "phase": phase,
        "time_utc8": datetime.now(LOCAL_TZ).isoformat(timespec="seconds"),
        "valid": snapshot.get("valid", False),
        "reason": snapshot.get("reason"),
        "lease_file_path": lease_file.get("path"),
        "lease_file_sha256": lease_file.get("observed_sha256"),
        "events": [{"path": event.get("path"), "sha256": event.get("sha256"), "time_utc8": event.get("time_utc8")}
                   for event in snapshot.get("events", [])],
    })


def _check_live_lease(record: dict, phase: str) -> None:
    snapshot = lease_snapshot()
    _record_lease_snapshot(record, phase, snapshot)
    if not snapshot.get("valid"):
        raise ScanError(f"租用失效/召回（{phase}）：{snapshot.get('reason')}")


def _checked_source_artifact(root: Path, commit: str, relative: str) -> dict:
    disk_path = root / Path(relative)
    if not disk_path.is_file():
        raise ScanError(f"源码证据缺失：{relative}")
    blob_oid = _git_text(root, "rev-parse", f"{commit}:{relative}")
    blob = _git_bytes(root, "show", f"{commit}:{relative}")
    return {"path": relative, "worktree_disk_hash_basis": "worktree_disk", "worktree_disk_sha256": sha256(disk_path),
            "reviewed_commit": commit, "commit_blob_hash_basis": "commit_blob", "commit_blob_oid": blob_oid,
            "commit_blob_sha256": hashlib.sha256(blob).hexdigest()}


def execute(run_id: str, *, confirm_exclusive_window: bool = False,
            process_query: Callable[[], set[str]] = _process_snapshot,
            port_query: Callable[[], list[int]] = _listener_snapshot,
            popen: Callable[..., subprocess.Popen] = subprocess.Popen,
            now: Callable[[], datetime] = lambda: datetime.now(LOCAL_TZ),
            monotonic: Callable[[], float] = time.monotonic,
            sleep: Callable[[float], None] = time.sleep) -> dict:
    """执行受运行期召回监视保护的只读扫描；CLI flag 不构成授权凭据。"""
    if not RUN_ID.fullmatch(run_id):
        raise ScanError("RunId 必须符合 s6e_jtag_readonly_YYYYMMDD_rNN")
    if not confirm_exclusive_window:
        raise ScanError("必须显式确认独占窗口；该确认不替代正式 CLAIM、Reviewer 或租约核验")

    start = monotonic()
    window_start = now()
    claim = verify_formal_claim(run_id)
    receipt, review = _read_review_receipt(REVIEW_RECEIPT, run_id)
    initial_lease = lease_snapshot()
    if not initial_lease.get("valid"):
        raise ScanError(f"当前租用未生效：{initial_lease.get('reason')}")
    inputs = _static_inputs()
    _check_idle(process_query, port_query)
    if monotonic() - start >= 20:
        raise ScanError("前置核验超过 20 秒预算；停止且不启动硬件工具")

    head = _git_text(ROOT, "rev-parse", "HEAD")
    reviewed_commit = review["reviewed_commit"]
    source_files = {
        rel: _checked_source_artifact(ROOT, reviewed_commit, rel)
        for rel in ("verification/s6e_jtag_readonly_scan.py", "verification/test_s6e_jtag_readonly_scan.py")
    }
    for relative, item in receipt["reviewed_files"].items():
        artifact = source_files[relative]
        if (artifact["worktree_disk_sha256"] != item["worktree_disk_sha256"]
                or artifact["commit_blob_oid"] != item["commit_blob_oid"]
                or artifact["commit_blob_sha256"] != item["commit_blob_sha256"]):
            raise ScanError(f"源码在 Reviewer 核验后发生变化：{relative}")
    if sha256(REVIEW_RECEIPT) != review["receipt_file_sha256"]:
        raise ScanError("Reviewer 回执文件在核验后发生变化")
    tests = receipt["tests"]
    test_log_path = ROOT / Path(tests["log_path"])
    review_evidence_path = ROOT / Path(receipt["review_evidence_path"])
    run_dir = ROOT / "report" / "evidence" / "S6-E" / run_id
    if run_dir.exists():
        raise ScanError(f"RunId 目录已存在；拒绝覆盖或复用：{run_dir}")
    run_dir.mkdir(parents=True, exist_ok=False)
    manifest_path = run_dir / "execution_manifest.json"
    record: dict = {
        "schema_version": 1,
        "run_id": run_id,
        "task_id": "S6E-JTAG-RO",
        "scope": SCOPE,
        "status": "RUNNING",
        "start_utc8": window_start.isoformat(timespec="seconds"),
        "source_commit": head,
        "baseline_commit": claim["offer_source_commit"],
        "source_artifacts": source_files,
        "pinned_inputs": {path: {"hash_basis": "worktree_disk", "sha256": digest} for path, digest in inputs.items()},
        "formal_claim": claim,
        "reviewer_receipt": {
            "path": str(REVIEW_RECEIPT.relative_to(ROOT)),
            "hash_basis": "worktree_disk",
            "sha256": review["receipt_file_sha256"],
            "reviewed_commit": review["reviewed_commit"],
            "reviewer_id": review["reviewer_id"],
            "review_evidence": {"path": receipt["review_evidence_path"], "hash_basis": "worktree_disk",
                                "sha256": sha256(review_evidence_path)},
            "test": {"command": tests["command"], "working_directory": tests["working_directory"],
                     "exit_code": tests["exit_code"], "summary": tests["summary"],
                     "log_path": tests["log_path"], "hash_basis": "worktree_disk",
                     "log_sha256": sha256(test_log_path)},
        },
        "board_state_modified": False,
        "hardware_session_started": False,
        "commands": [],
        "lease_evidence": {"lease_versions": [], "events": [], "checks": []},
        "cleanup": {},
        "errors": [],
        "acceptance_claim": "NONE; does not satisfy S6-E gates or G3/G4/G5",
    }
    _record_lease_snapshot(record, "preflight", initial_lease)
    _write_json_atomic(manifest_path, record)
    server = xsdb = None
    server_log = xsdb_log = None
    interrupted = False

    def record_command(argv: list[str], pid: int) -> dict:
        item = {"argv": argv, "pid": pid, "start_utc8": now().isoformat(timespec="seconds"), "exit_code": None}
        record["commands"].append(item)
        _write_json_atomic(manifest_path, record)
        return item

    try:
        # 二次核验紧贴 hw_server 启动，避免用过期快照开窗。
        current_claim = verify_formal_claim(run_id)
        if current_claim != claim:
            raise ScanError("正式 OFFER/CLAIM 在准备后发生变化")
        current_receipt, current_review = _read_review_receipt(REVIEW_RECEIPT, run_id)
        if current_review["receipt_file_sha256"] != review["receipt_file_sha256"]:
            raise ScanError("Reviewer 回执在准备后发生变化")
        for relative, item in current_receipt["reviewed_files"].items():
            if sha256(_safe_repo_file(ROOT, relative, "Reviewer 源码")) != item["worktree_disk_sha256"]:
                raise ScanError(f"源码在启动前发生变化：{relative}")
        current_inputs = _static_inputs()
        if current_inputs != inputs:
            raise ScanError("固定输入哈希在准备后发生变化")
        _check_live_lease(record, "before_hw_server")
        _check_idle(process_query, port_query)
        if monotonic() - start >= 20:
            raise ScanError("前置核验超过 20 秒预算；停止且不启动硬件工具")
        server_log = (run_dir / "hw_server.log").open("xb")
        server_argv = [str(HW_SERVER), "-s", f"tcp::{PORT}"]
        server = popen(server_argv, stdin=subprocess.DEVNULL, stdout=server_log, stderr=subprocess.STDOUT,
                       shell=False, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        record["hardware_session_started"] = True
        server_command = record_command(server_argv, server.pid)
        server_deadline = min(monotonic() + 10, start + 60)
        while monotonic() < server_deadline:
            _check_live_lease(record, "waiting_hw_server")
            owners = port_query()
            if owners:
                if owners != [server.pid]:
                    raise ScanError(f"3121 监听 PID 不属于本次 hw_server：{owners}")
                break
            if server.poll() is not None:
                server_command["exit_code"] = server.returncode
                raise ScanError(f"hw_server 提前退出：{server.returncode}")
            sleep(0.2)
        else:
            raise ScanError("hw_server 未在 10 秒内监听 3121")

        _check_live_lease(record, "before_xsdb")
        listeners = port_query()
        if listeners != [server.pid]:
            raise ScanError(f"启动 XSDB 前 3121 监听者已变化：{listeners}")
        foreign = sorted(process_query() & (BUSY_NAMES - {"hw_server.exe"}))
        if foreign:
            raise ScanError(f"启动 XSDB 前发现外部相关进程，停止且不触碰：{foreign}")
        xsdb_log = (run_dir / "xsdb_scan2.log").open("xb")
        xsdb_argv = [str(XSDB), str(SCAN_TCL)]
        xsdb = popen(xsdb_argv, stdin=subprocess.DEVNULL, stdout=xsdb_log, stderr=subprocess.STDOUT,
                     shell=False, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        xsdb_command = record_command(xsdb_argv, xsdb.pid)
        scan_deadline = min(monotonic() + 30, start + 60)
        while xsdb.poll() is None:
            _check_live_lease(record, "running_xsdb")
            if server.poll() is not None:
                server_command["exit_code"] = server.returncode
                raise ScanError(f"扫描期间 hw_server 提前退出：{server.returncode}")
            listeners = port_query()
            if listeners != [server.pid]:
                raise ScanError(f"扫描期间 3121 监听者变化：{listeners}")
            remaining = scan_deadline - monotonic()
            if remaining <= 0:
                raise ScanError("XSDB 超过 30 秒或总预算；停止并保留本次日志，不重试")
            sleep(min(0.25, remaining))
        xsdb_command["exit_code"] = xsdb.returncode
        xsdb_log.flush()
        output = (run_dir / "xsdb_scan2.log").read_bytes().decode("utf-8", errors="replace")
        record["xsdb_output"] = {"path": "xsdb_scan2.log", "hash_basis": "worktree_disk",
                                  "sha256": sha256(run_dir / "xsdb_scan2.log")}
        record["target_lines"] = [line.split("=", 1)[1].strip() for line in output.splitlines()
                                  if line.startswith("SCAN2_TARGET=")]
        count_match = re.findall(r"^SCAN2_TARGET_COUNT=([0-9]+)\s*$", output, re.MULTILINE)
        chain = re.findall(r"^SCAN2_JTAG_CHAIN=(.*)$", output, re.MULTILINE)
        record["target_count"] = int(count_match[0]) if len(count_match) == 1 else None
        record["jtag_chain"] = chain[0].strip() if len(chain) == 1 else None
        errors = _validate_output(output, int(xsdb.returncode or 0))
        if errors:
            raise ScanError("; ".join(errors))
    except KeyboardInterrupt:
        interrupted = True
        record["errors"].append("收到中断；停止本次启动的进程并保留日志")
    except (OSError, subprocess.SubprocessError, ScanError) as exc:
        record["errors"].append(str(exc))
    finally:
        record["cleanup"]["xsdb"] = _safe_stop(xsdb)
        record["cleanup"]["hw_server"] = _safe_stop(server)
        for item in record["commands"]:
            if xsdb is not None and item["pid"] == xsdb.pid:
                item["exit_code"] = xsdb.poll()
                item["log_path"] = "xsdb_scan2.log"
                log_path = run_dir / "xsdb_scan2.log"
                item["log_hash_basis"] = "worktree_disk"
                item["log_sha256"] = sha256(log_path) if log_path.is_file() else None
            elif server is not None and item["pid"] == server.pid:
                item["exit_code"] = server.poll()
                item["log_path"] = "hw_server.log"
                log_path = run_dir / "hw_server.log"
                item["log_hash_basis"] = "worktree_disk"
                item["log_sha256"] = sha256(log_path) if log_path.is_file() else None
        for stream in (xsdb_log, server_log):
            if stream is not None:
                try:
                    stream.flush()
                    stream.close()
                except OSError as exc:
                    record["errors"].append(f"日志关闭失败：{exc}")

    try:
        record["cleanup"]["remaining_relevant_processes"] = sorted(process_query() & BUSY_NAMES)
        record["cleanup"]["remaining_3121_listeners"] = port_query()
        if record["cleanup"]["remaining_relevant_processes"] or record["cleanup"]["remaining_3121_listeners"]:
            record["errors"].append("收尾有残留；不终止任何非本次进程，保留现场并停止")
        _check_live_lease(record, "after_cleanup")
    except (OSError, ScanError, subprocess.SubprocessError) as exc:
        record["errors"].append(f"收尾状态不可核验或租约已召回：{exc}")
    record["end_utc8"] = now().isoformat(timespec="seconds")
    record["elapsed_seconds"] = round(monotonic() - start, 3)
    record["interrupted"] = interrupted
    if record["elapsed_seconds"] > 80:
        record["errors"].append("运行及有界清理超过 80 秒总上限")
    record["status"] = "INTERRUPTED_STOPPED" if interrupted else ("PASS_READ_ONLY_TOPOLOGY" if not record["errors"] else "FAIL_STOPPED")
    _write_json_atomic(manifest_path, record)
    return record


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="只读 JTAG 拓扑扫描；默认仅显示帮助，不连接硬件")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--execute", action="store_true", help="明确要求执行硬件只读扫描")
    parser.add_argument("--confirm-exclusive-window", action="store_true")
    args = parser.parse_args(argv)
    if not args.execute:
        print("PREPARED_NOT_RUN：未启动硬件工具；请先完成独立复审与正式窗口核验。")
        return 0
    try:
        result = execute(args.run_id, confirm_exclusive_window=args.confirm_exclusive_window)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 130 if result["status"] == "INTERRUPTED_STOPPED" else (0 if result["status"] == "PASS_READ_ONLY_TOPOLOGY" else 1)
    except ScanError as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


