"""阶段6只读 JTAG 扫描门禁的全离线回归。"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import s6e_jtag_readonly_scan as scan


RUN_ID = "s6e_jtag_readonly_20261028_r01"
FAKE_COMMIT = "a" * 40
FAKE_BLOB_OID = "b" * 40
FAKE_SHA = "c" * 64
VALID_OUTPUT = (
    "SCAN2_CONNECTED=1\n"
    "SCAN2_TARGET_COUNT=2\n"
    "SCAN2_TARGET=xc7z020\n"
    "SCAN2_TARGET=arm_dap\n"
    "SCAN2_JTAG_CHAIN=xc7z020\n"
    "SCAN2_DISCONNECTED=1\n"
)


def _handoff_row(
    status: str,
    run_id: str = RUN_ID,
    path: str = r"D:\codex-worktrees\w6",
    offer_commit: str = FAKE_COMMIT,
    offer_blob_oid: str = FAKE_BLOB_OID,
    offer_sha256: str = FAKE_SHA,
    offer_source_commit: str = FAKE_COMMIT,
) -> str:
    """构造项目 11 字段交接行样本。"""
    values = {
        "任务": scan.TASK_ID,
        "负责人": "Codex 项目总控",
        "工作树/分支": f"`{path}` / `stage6-interact-prep`",
        "起始提交": FAKE_COMMIT,
        "允许修改范围": "S6E_JTAG_READONLY_DIAGNOSTIC",
        "未提交改动归属": "由 Codex 总控记录",
        "让出声明": "本任务边界内正式交接",
        "心跳(UTC+8)": "2026-10-28 00:00",
        "证据入口": (
            f"hardware_run_id={run_id}; scope={scan.SCOPE}; "
            f"offer_commit={offer_commit}; offer_blob_oid={offer_blob_oid}; "
            f"offer_sha256={offer_sha256}; offer_source_commit={offer_source_commit}"
        ),
        "恢复命令": "按阶段 STATE 恢复",
        "状态/下一接手方": f"{status} / Codex",
    }
    return " | ".join(f"{name}={value}" for name, value in values.items())


def _review_fixture(root: Path, run_id: str = RUN_ID) -> dict:
    """建立可哈希的临时审查材料；Git 身份由测试桩提供。"""
    verify_dir = root / "verification"
    verify_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    for rel, data in (
        ("verification/s6e_jtag_readonly_scan.py", b"reviewed scanner\n"),
        ("verification/test_s6e_jtag_readonly_scan.py", b"reviewed tests\n"),
    ):
        path = root / Path(rel)
        path.write_bytes(data)
        files[rel] = {
            "worktree_disk_hash_basis": "worktree_disk",
            "worktree_disk_sha256": hashlib.sha256(data).hexdigest(),
            "commit_blob_hash_basis": "commit_blob",
            "commit_blob_oid": FAKE_BLOB_OID,
            "commit_blob_sha256": hashlib.sha256(data).hexdigest(),
        }
    evidence = root / "review-evidence.md"
    evidence.write_text("independent review PASS evidence\n", encoding="utf-8")
    test_log = root / "offline-tests.log"
    test_log.write_text("Ran 24 tests in 0.076s\n\nOK\n", encoding="utf-8")
    return {
        "schema_version": 1,
        "task_id": "S6E-JTAG-RO",
        "scope": scan.SCOPE,
        "run_id": run_id,
        "review_status": "PASS",
        "reviewer_id": "independent-reviewer",
        "blocking_findings": 0,
        "reviewed_commit": FAKE_COMMIT,
        "reviewed_files": files,
        "tests": {
            "command": list(scan.EXPECTED_TEST_COMMAND),
            "working_directory": scan.EXPECTED_TEST_WORKDIR,
            "exit_code": 0,
            "log_path": "offline-tests.log",
            "log_hash_basis": "worktree_disk",
            "log_sha256": hashlib.sha256(test_log.read_bytes()).hexdigest(),
            "summary": {"tests_run": 24, "failures": 0, "errors": 0, "skipped": 0, "success_marker": "OK"},
        },
        "review_evidence_path": "review-evidence.md",
        "review_evidence_hash_basis": "worktree_disk",
        "review_evidence_sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
    }


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, timeout=15, check=False)
    if result.returncode != 0:
        raise AssertionError(f"temporary git command failed: {args}: {result.stderr.decode(errors='replace')}")
    return result.stdout.decode("utf-8", errors="strict").strip()


def _commit_state(root: Path, contents: str, message: str) -> str:
    state = root / ".codex" / "STATE.md"
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(contents, encoding="utf-8")
    _git(root, "add", "--", ".codex/STATE.md")
    _git(root, "commit", "-m", message)
    return _git(root, "rev-parse", "HEAD")


def _temporary_formal_repos(root: Path, bad_claim_field: str | None = None, divergent_offer: bool = False,
                            claim_uncommitted: bool = False):
    main = root / "main"
    w6 = root / "w6"
    main.mkdir(parents=True)
    w6.mkdir(parents=True)
    for repo in (main, w6):
        _git(repo, "init", "--initial-branch=main")
        _git(repo, "config", "user.name", "Offline Test")
        _git(repo, "config", "user.email", "offline-test@example.invalid")
    source_commit = _commit_state(main, "main baseline\n", "source baseline")
    offer_row = _handoff_row("OFFERED")
    offer_text = f"## 当前交接\n{offer_row}\n"
    if divergent_offer:
        _git(main, "checkout", "-b", "offer-side")
        offer_commit = _commit_state(main, offer_text, "offer side commit")
        _git(main, "checkout", "main")
        _commit_state(main, offer_text, "main copied offer row")
    else:
        offer_commit = _commit_state(main, offer_text, "main offer")
    blob_oid = _git(main, "rev-parse", f"{offer_commit}:.codex/STATE.md")
    blob = subprocess.run(["git", "-C", str(main), "show", f"{offer_commit}:.codex/STATE.md"],
                          capture_output=True, timeout=10, check=True).stdout
    offer_sha = hashlib.sha256(blob).hexdigest()
    claim_row = _handoff_row("CLAIMED", offer_commit=offer_commit, offer_blob_oid=blob_oid,
                             offer_sha256=offer_sha, offer_source_commit=source_commit)
    if bad_claim_field == "offer_blob_oid":
        claim_row = claim_row.replace(f"offer_blob_oid={blob_oid}", f"offer_blob_oid={'0' * 40}")
    elif bad_claim_field == "offer_sha256":
        claim_row = claim_row.replace(f"offer_sha256={offer_sha}", f"offer_sha256={'0' * 64}")
    if claim_uncommitted:
        _commit_state(w6, "## 当前交接\nw6 baseline without claim\n", "w6 baseline")
        (w6 / ".codex" / "STATE.md").write_text(f"## 当前交接\n{claim_row}\n", encoding="utf-8")
    else:
        _commit_state(w6, f"## 当前交接\n{claim_row}\n", "w6 claim")
    return main, w6, {"source_commit": source_commit, "offer_commit": offer_commit,
                      "offer_blob_oid": blob_oid, "offer_sha256": offer_sha}


class FakeProc:
    """仅供离线单元测试使用的子进程桩。"""

    def __init__(self, pid: int, role: str, active_ports: set[int], stdout=None) -> None:
        self.pid = pid
        self.role = role
        self.active_ports = active_ports
        self.returncode = 0 if role == "xsdb-complete" else None
        self.terminate_calls = 0
        self.kill_calls = 0
        if role.startswith("xsdb") and stdout is not None and role == "xsdb-complete":
            stdout.write(VALID_OUTPUT.encode("utf-8"))

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        if self.returncode is None:
            self.returncode = -15
            self.active_ports.discard(self.pid)
        return self.returncode

    def terminate(self):
        self.terminate_calls += 1
        if "cleanup-fail" in self.role:
            raise OSError("mock terminate failure")
        self.returncode = -15
        self.active_ports.discard(self.pid)

    def kill(self):
        self.kill_calls += 1
        self.returncode = -9
        self.active_ports.discard(self.pid)


class ScanGuardTests(unittest.TestCase):
    def _snapshot_for_notice(self, root: Path, notice_text: str, release_time: str):
        mailbox = root / "mailbox"
        mailbox.mkdir()
        lease = root / "DSH-20261027-008-board-lease-stage6.md"
        lease.write_text("允许 Codex 阶段6 使用板卡\n", encoding="utf-8")
        notice = mailbox / "DSH-20261024-004-stage6-board-note.md"
        notice.write_text(notice_text, encoding="utf-8")
        release = mailbox / "DSH-20261027-010-board-released.md"
        release.write_text(
            "# DSH-20261027-010 板卡已释放\n"
            f"时间：{release_time}（UTC+8）\n"
            "关联 DSH-20261027-009 和租用条款；阶段6恢复有效，可以开启。\n",
            encoding="utf-8",
        )
        pinned_sha = hashlib.sha256(lease.read_bytes()).hexdigest()
        with patch.object(scan, "LEASE_SHA256", pinned_sha):
            snapshot = scan.lease_snapshot(lease, mailbox)
        return snapshot, notice

    def test_cli_without_execute_is_plan_only(self) -> None:
        output = io.StringIO()
        with patch.object(scan, "execute") as execute, contextlib.redirect_stdout(output):
            self.assertEqual(scan.main(["--run-id", RUN_ID]), 0)
        execute.assert_not_called()
        self.assertIn("PREPARED_NOT_RUN", output.getvalue())

    def test_cli_rejects_legacy_boolean_authority_flags(self) -> None:
        stderr = io.StringIO()
        with patch.object(scan, "execute") as execute, contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as exc:
                scan.main([
                    "--run-id", RUN_ID, "--execute", "--confirm-exclusive-window",
                    "--confirm-lease-active", "--confirm-no-dsh-recall",
                    "--confirm-handoff-claimed", "--confirm-command-review-pass",
                ])
        self.assertEqual(exc.exception.code, 2)
        execute.assert_not_called()

    def test_formal_claim_is_required_even_when_exclusive_flag_is_set(self) -> None:
        popen = MagicMock()
        with patch.object(scan, "verify_formal_claim", side_effect=scan.ScanError("no formal claim")):
            with self.assertRaisesRegex(scan.ScanError, "no formal claim"):
                scan.execute(RUN_ID, confirm_exclusive_window=True, popen=popen)
        popen.assert_not_called()

    def test_missing_reviewer_receipt_blocks_before_process_probe(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            missing = root / "reviewer_receipt.json"
            process_query = MagicMock()
            popen = MagicMock()
            with patch.object(scan, "verify_formal_claim", return_value={"offer_source_commit": FAKE_COMMIT}), \
                 patch.object(scan, "REVIEW_RECEIPT", missing):
                with self.assertRaisesRegex(scan.ScanError, "缺少独立 Reviewer"):
                    scan.execute(RUN_ID, confirm_exclusive_window=True, process_query=process_query, popen=popen)
            process_query.assert_not_called()
            popen.assert_not_called()

    def test_tasklist_parses_process_names(self) -> None:
        self.assertEqual(scan.tasklist_names('"hw_server.exe","100","Console","1","1 K"'), {"hw_server.exe"})

    def test_empty_tasklist_fails_closed(self) -> None:
        with self.assertRaises(scan.ScanError):
            scan.tasklist_names("")

    def test_netstat_only_reports_3121_listening_pid(self) -> None:
        output = (
            "Proto Local Address Foreign Address State PID\n"
            "TCP 0.0.0.0:3121 0.0.0.0:0 LISTENING 100\n"
            "TCP 127.0.0.1:3121 127.0.0.1:3 TIME_WAIT 0\n"
        )
        self.assertEqual(scan.port_3121_listeners(output), [100])

    def test_valid_scan_output_requires_target_details(self) -> None:
        self.assertEqual(scan._validate_output(VALID_OUTPUT, 0), [])

    def test_duplicate_target_count_is_rejected(self) -> None:
        output = VALID_OUTPUT.replace("SCAN2_TARGET_COUNT=2\n", "SCAN2_TARGET_COUNT=2\nSCAN2_TARGET_COUNT=2\n")
        self.assertTrue(any("数量标记必须唯一" in error for error in scan._validate_output(output, 0)))

    def test_duplicate_chain_is_rejected(self) -> None:
        output = VALID_OUTPUT.replace("SCAN2_JTAG_CHAIN=xc7z020\n", "SCAN2_JTAG_CHAIN=xc7z020\nSCAN2_JTAG_CHAIN=xc7z020\n")
        self.assertTrue(any("JTAG 链标记必须唯一" in error for error in scan._validate_output(output, 0)))

    def test_target_count_must_match_details(self) -> None:
        output = VALID_OUTPUT.replace("SCAN2_TARGET=arm_dap\n", "")
        self.assertTrue(any("目标明细数与目标数量不一致" in error for error in scan._validate_output(output, 0)))

    def test_zero_targets_are_not_a_pass(self) -> None:
        output = VALID_OUTPUT.replace("SCAN2_TARGET_COUNT=2", "SCAN2_TARGET_COUNT=0").replace(
            "SCAN2_TARGET=xc7z020\nSCAN2_TARGET=arm_dap\n", ""
        )
        self.assertTrue(scan._validate_output(output, 0))

    def test_handoff_rows_must_be_formal_and_bound_to_same_run(self) -> None:
        main_row = _handoff_row("OFFERED")
        claim_row = _handoff_row("CLAIMED")
        validated = scan.validate_claim_rows(main_row, claim_row, RUN_ID)
        self.assertEqual(validated["hardware_run_id"], RUN_ID)
        self.assertEqual(validated["scope"], scan.SCOPE)
        with self.assertRaises(scan.ScanError):
            scan.validate_claim_rows(main_row.replace("OFFERED", "OFFERED_FORGED"), claim_row, RUN_ID)
        with self.assertRaises(scan.ScanError):
            scan.validate_claim_rows(main_row, claim_row.replace("CLAIMED", "CLAIMED_FORGED"), RUN_ID)
        with self.assertRaises(scan.ScanError):
            scan.validate_claim_rows(main_row.replace("OFFERED", "IN_PROGRESS"), claim_row, RUN_ID)
        with self.assertRaises(scan.ScanError):
            scan.validate_claim_rows(main_row, _handoff_row("CLAIMED", "s6e_jtag_readonly_20261028_r02"), RUN_ID)
        with self.assertRaisesRegex(scan.ScanError, "工作树与分支"):
            scan.validate_claim_rows(main_row, _handoff_row("CLAIMED", path=r"D:\codex-worktrees\other"), RUN_ID)
        with self.assertRaisesRegex(scan.ScanError, "工作树与分支"):
            scan.validate_claim_rows(main_row, _handoff_row("CLAIMED", path=r"D:\codex-worktrees\w6-shadow"), RUN_ID)
        with self.assertRaisesRegex(scan.ScanError, "工作树与分支"):
            shadow_branch = claim_row.replace("stage6-interact-prep", "stage6-interact-prep-shadow")
            scan.validate_claim_rows(main_row, shadow_branch, RUN_ID)

    def test_missing_handoff_fields_are_rejected(self) -> None:
        with self.assertRaises(scan.ScanError):
            scan.validate_claim_rows("任务=" + scan.TASK_ID, _handoff_row("CLAIMED"), RUN_ID)

    def test_real_temporary_git_repositories_verify_offer_claim_blobs_and_ancestry(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            main, w6, expected = _temporary_formal_repos(Path(temp))
            with patch.object(scan, "MAIN_ROOT", main), patch.object(scan, "ROOT", w6):
                result = scan.verify_formal_claim(RUN_ID)
            self.assertEqual(result["status"], "FORMAL_CLAIM_VERIFIED")
            self.assertEqual(result["offer_commit"], expected["offer_commit"])
            self.assertEqual(result["offer_blob_oid"], expected["offer_blob_oid"])
            self.assertEqual(result["offer_sha256"], expected["offer_sha256"])

    def test_real_temporary_git_rejects_forged_offer_blob_oid_and_sha(self) -> None:
        for field in ("offer_blob_oid", "offer_sha256"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temp:
                main, w6, _ = _temporary_formal_repos(Path(temp), bad_claim_field=field)
                with patch.object(scan, "MAIN_ROOT", main), patch.object(scan, "ROOT", w6):
                    with self.assertRaisesRegex(scan.ScanError, "offer_commit/blob_oid/sha256"):
                        scan.verify_formal_claim(RUN_ID)

    def test_real_temporary_git_rejects_uncommitted_claim_status_spoof(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            main, w6, _ = _temporary_formal_repos(Path(temp))
            state = w6 / ".codex" / "STATE.md"
            state.write_text(state.read_text(encoding="utf-8").replace("CLAIMED / Codex", "CLAIMED_FORGED / Codex"),
                             encoding="utf-8")
            with patch.object(scan, "MAIN_ROOT", main), patch.object(scan, "ROOT", w6):
                with self.assertRaisesRegex(scan.ScanError, "正式交接状态不是 CLAIMED"):
                    scan.verify_formal_claim(RUN_ID)

    def test_real_temporary_git_rejects_valid_claimed_row_only_in_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            main, w6, _ = _temporary_formal_repos(Path(temp), claim_uncommitted=True)
            state = w6 / ".codex" / "STATE.md"
            current = state.read_text(encoding="utf-8")
            self.assertIn("CLAIMED / Codex", current)
            self.assertNotIn("CLAIMED", _git(w6, "show", "HEAD:.codex/STATE.md"))
            with patch.object(scan, "MAIN_ROOT", main), patch.object(scan, "ROOT", w6):
                with self.assertRaisesRegex(scan.ScanError, "正式 OFFER/CLAIM 行尚未提交"):
                    scan.verify_formal_claim(RUN_ID)

    def test_real_temporary_git_rejects_offer_not_ancestor_of_main_head(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            main, w6, _ = _temporary_formal_repos(Path(temp), divergent_offer=True)
            with patch.object(scan, "MAIN_ROOT", main), patch.object(scan, "ROOT", w6):
                with self.assertRaisesRegex(scan.ScanError, "祖先关系"):
                    scan.verify_formal_claim(RUN_ID)

    def test_dsh_008_content_modification_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            lease = root / "DSH-20261027-008.md"
            mailbox = root / "mailbox"
            mailbox.mkdir()
            lease.write_text("允许 Codex 阶段6 使用板卡\n内容被修改\n", encoding="utf-8")
            valid, reason = scan.lease_status(lease, mailbox)
            self.assertFalse(valid)
            self.assertIn("SHA-256 已变化", reason)

    def test_unknown_minute_suffix_preserves_conservative_interval(self) -> None:
        raw = "时间：2026-10-24 00:5x（UTC+8）"
        interval = scan._mail_time_interval(raw)
        self.assertIsNotNone(interval)
        assert interval is not None
        start, end, source_text = interval
        self.assertEqual(start.isoformat(timespec="minutes"), "2026-10-24T00:50+08:00")
        self.assertEqual(end.isoformat(timespec="minutes"), "2026-10-24T01:00+08:00")
        self.assertEqual(source_text, raw)

    def test_explicit_invalid_or_ambiguous_ranges_are_not_reduced_to_start_time(self) -> None:
        invalid = (
            "时间：2026-10-27 22:50–23:60（UTC+8）",
            "时间：2026-10-27 22:50–23:15:60（UTC+8）",
            "时间：2026-10-27 22:50–（UTC+8）",
            "时间：2026-10-27 23:50–00:10（UTC+8）",
        )
        for raw in invalid:
            with self.subTest(raw=raw):
                self.assertIsNone(scan._mail_time_interval(raw))

    def test_range_symbol_on_a_later_body_line_does_not_extend_timestamp(self) -> None:
        raw = "时间：2026-10-27 22:50（UTC+8）\n备注：适用范围—只限阶段6。\n"
        interval = scan._mail_time_interval(raw)
        self.assertIsNotNone(interval)
        assert interval is not None
        start, end, source_text = interval
        self.assertEqual(start.isoformat(timespec="minutes"), "2026-10-27T22:50+08:00")
        self.assertEqual(end.isoformat(timespec="minutes"), "2026-10-27T22:51+08:00")
        self.assertEqual(source_text, "时间：2026-10-27 22:50（UTC+8）")

    def test_valid_explicit_range_is_used_as_a_whole_by_lease_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            raw = (
                "# DSH-20261024-004 阶段3板级窗口\n"
                "时间：2026-10-27 22:40–22:50（UTC+8）\n"
                "阶段3/6板级窗口信息。\n"
            )
            snapshot, notice = self._snapshot_for_notice(Path(temp), raw, "2026-10-27 23:00")
            self.assertTrue(snapshot["valid"], snapshot["reason"])
            event = next(item for item in snapshot["events"] if item["path"] == str(notice))
            self.assertEqual(event["event"], "UNKNOWN_RELEVANT_NOTICE_PRE_RELEASE")
            self.assertEqual(
                event["time_range_utc8"],
                {"start_inclusive": "2026-10-27T22:40+08:00", "end_exclusive": "2026-10-27T22:51+08:00"},
            )

    def test_lease_snapshot_blocks_invalid_explicit_ranges_instead_of_accepting_start(self) -> None:
        invalid = (
            "2026-10-27 22:50–23:60",
            "2026-10-27 22:50–23:15:60",
            "2026-10-27 23:50–00:10",
        )
        for timestamp in invalid:
            with self.subTest(timestamp=timestamp), tempfile.TemporaryDirectory() as temp:
                raw = (
                    "# DSH-20261024-004 阶段3板级窗口\n"
                    f"时间：{timestamp}（UTC+8）\n"
                    "阶段3/6板级窗口信息。\n"
                )
                snapshot, notice = self._snapshot_for_notice(Path(temp), raw, "2026-10-27 23:00")
                self.assertFalse(snapshot["valid"])
                event = next(item for item in snapshot["events"] if item["path"] == str(notice))
                self.assertEqual(event["event"], "UNKNOWN_RELEVANT_NOTICE")
                self.assertIsNone(event["time_utc8"])
                self.assertIn("缺少可解析 UTC+8 时间", snapshot["reason"])

    def test_date_only_notice_uses_full_day_interval_without_inventing_time(self) -> None:
        raw = "日期：2026-10-24（UTC+8）"
        interval = scan._mail_time_interval(raw)
        self.assertIsNotNone(interval)
        assert interval is not None
        start, end, source_text = interval
        self.assertEqual(start.isoformat(timespec="minutes"), "2026-10-24T00:00+08:00")
        self.assertEqual(end.isoformat(timespec="minutes"), "2026-10-25T00:00+08:00")
        self.assertEqual(source_text, raw)
        self.assertIsNotNone(scan._mail_time_interval("日期：2026-10-24 UTC+8"))

    def test_date_only_unsupported_timezone_suffixes_fail_closed(self) -> None:
        for raw in (
            "日期：2026-10-24（UTC+9）",
            "日期：2026-10-24 PST",
            "日期：2026-10-24 UTC-8",
            "日期：2026-10-24+08:00",
        ):
            with self.subTest(raw=raw):
                self.assertIsNone(scan._mail_time_interval(raw))

    def test_full_time_timezone_suffixes_must_be_complete_and_supported(self) -> None:
        expected = {
            "时间：2026-10-27 22:50 UTC+8": "2026-10-27T22:50+08:00",
            "时间：2026-10-27 22:50+08:00": "2026-10-27T22:50+08:00",
            "时间：2026-10-27T14:50-08:00": "2026-10-28T06:50+08:00",
        }
        for raw, start in expected.items():
            with self.subTest(raw=raw):
                interval = scan._mail_time_interval(raw)
                self.assertIsNotNone(interval)
                assert interval is not None
                self.assertEqual(interval[0].isoformat(timespec="minutes"), start)
                self.assertEqual(interval[2], raw)
        for raw in (
            "时间：2026-10-27 22:50 UTC+9",
            "时间：2026-10-27 22:50 PST",
            "时间：2026-10-27 22:50 UTC-8",
            "时间：2026-10-27 22:50+08:00 PST",
            "时间：2026-10-27 22:50+08:00 UTC+8",
            "时间：2026-10-27T22:50-08:00 PST",
        ):
            with self.subTest(raw=raw):
                self.assertIsNone(scan._mail_time_interval(raw))

    def test_mail_time_interval_rejects_repeated_or_incompatible_metadata_fields(self) -> None:
        ambiguous = (
            "时间：2026-10-27 22:50（UTC+8）\n时间：2026-10-27 23:10（UTC+8）",
            "日期：2026-10-27（UTC+8）\n日期：2026-10-28（UTC+8）",
            "时间：2026-10-27 22:30（UTC+8）\n时间：2026-10-27T15:30-08:00",
            "时间：2026-10-27 22:30（UTC+8）\n日期：2026-10-28T00:00+08:00",
        )
        for raw in ambiguous:
            with self.subTest(raw=raw):
                self.assertIsNone(scan._mail_time_interval(raw))

    def test_mail_time_interval_accepts_one_authoritative_metadata_field_with_other_header_fields(self) -> None:
        raw = "- 编号：DSH-20261024-004；时间：2026-10-24 00:50（UTC+8）。"
        interval = scan._mail_time_interval(raw)
        self.assertIsNotNone(interval)
        assert interval is not None
        self.assertEqual(interval[0].isoformat(timespec="minutes"), "2026-10-24T00:50+08:00")
        self.assertEqual(interval[2], "时间：2026-10-24 00:50（UTC+8）")

    def test_actual_stage5_metadata_pipe_range_is_a_complete_authoritative_field(self) -> None:
        raw = "- 记录方：DSH（阶段5 总控）｜时间（UTC+8）：2026-10-27 12:26–12:40｜性质：授权登记（decision）"
        interval = scan._mail_time_interval(raw)
        self.assertIsNotNone(interval)
        assert interval is not None
        self.assertEqual(interval[0].isoformat(timespec="minutes"), "2026-10-27T12:26+08:00")
        self.assertEqual(interval[1].isoformat(timespec="minutes"), "2026-10-27T12:41+08:00")
        self.assertEqual(interval[2], "时间（UTC+8）：2026-10-27 12:26–12:40")

    def test_actual_stage5_metadata_unknown_zone_does_not_fall_back_to_utc8(self) -> None:
        raw = "- 记录方：DSH（阶段5 总控）｜时间（UTC-8）：2026-10-27 12:26–12:40｜性质：授权登记（decision）"
        self.assertIsNone(scan._mail_time_interval(raw))

    def test_lease_snapshot_rejects_old_timestamp_followed_by_newer_recall_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            raw = (
                "# DSH-20261024-004 板卡归还通知\n"
                "- 时间：2026-10-27 22:50（UTC+8）\n"
                "- 召回时间：2026-10-27T15:10-08:00\n"
                "请勿继续开启新的阶段6板级会话。\n"
            )
            snapshot, _ = self._snapshot_for_notice(Path(temp), raw, "2026-10-27 23:00")
            self.assertFalse(snapshot["valid"])
            self.assertIn("召回/释放记录缺少可解析 UTC+8 时间", snapshot["reason"])

    def test_lease_snapshot_rejects_duplicate_dates_and_cross_zone_time_fields(self) -> None:
        notices = (
            "日期：2026-10-27（UTC+8）\n日期：2026-10-28（UTC+8）",
            "时间：2026-10-27 22:30（UTC+8）\n时间：2026-10-27T15:30-08:00",
        )
        for fields in notices:
            with self.subTest(fields=fields), tempfile.TemporaryDirectory() as temp:
                raw = (
                    "# DSH-20261024-004 阶段3板级窗口\n"
                    f"{fields}\n"
                    "阶段3/6板级窗口信息。\n"
                )
                snapshot, notice = self._snapshot_for_notice(Path(temp), raw, "2026-10-27 23:00")
                self.assertFalse(snapshot["valid"])
                event = next(item for item in snapshot["events"] if item["path"] == str(notice))
                self.assertEqual(event["event"], "UNKNOWN_RELEVANT_NOTICE")
                self.assertIsNone(event["time_utc8"])
                self.assertIsNone(event["timestamp_text"])
                self.assertIn("缺少可解析 UTC+8 时间", snapshot["reason"])

    def test_lease_snapshot_accepts_one_authoritative_inline_time_field(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            raw = (
                "# DSH-20261024-004 阶段3板级窗口\n"
                "- 编号：DSH-20261024-004；时间：2026-10-24 00:50（UTC+8）。\n"
                "阶段3/6板级窗口信息。\n"
            )
            snapshot, notice = self._snapshot_for_notice(Path(temp), raw, "2026-10-27 23:00")
            self.assertTrue(snapshot["valid"], snapshot["reason"])
            event = next(item for item in snapshot["events"] if item["path"] == str(notice))
            self.assertEqual(event["event"], "UNKNOWN_RELEVANT_NOTICE_PRE_RELEASE")
            self.assertEqual(event["timestamp_text"], "时间：2026-10-24 00:50（UTC+8）")

    def test_lease_snapshot_accepts_actual_stage5_pipe_range_before_release(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            raw = (
                "# DSH-20261027-001：阶段5 硬件窗口与实物授权（Wong 授予）\n"
                "- 记录方：DSH（阶段5 总控）｜时间（UTC+8）：2026-10-27 12:26–12:40｜性质：授权登记（decision）\n"
                "阶段5板级项目，JTAG 仍需会话交接。\n"
            )
            snapshot, notice = self._snapshot_for_notice(Path(temp), raw, "2026-10-27 23:00")
            self.assertTrue(snapshot["valid"], snapshot["reason"])
            event = next(item for item in snapshot["events"] if item["path"] == str(notice))
            self.assertEqual(event["event"], "OUT_OF_SCOPE_STAGE5_PRE_RELEASE")
            self.assertEqual(event["timestamp_text"], "时间（UTC+8）：2026-10-27 12:26–12:40")

    def test_lease_snapshot_blocks_actual_stage5_metadata_with_unsupported_zone(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            raw = (
                "# DSH-20261027-001：阶段5 硬件窗口与实物授权（Wong 授予）\n"
                "- 记录方：DSH（阶段5 总控）｜时间（UTC-8）：2026-10-27 12:26–12:40｜性质：授权登记（decision）\n"
                "阶段5板级项目，JTAG 仍需会话交接。\n"
            )
            snapshot, notice = self._snapshot_for_notice(Path(temp), raw, "2026-10-27 23:00")
            self.assertFalse(snapshot["valid"])
            event = next(item for item in snapshot["events"] if item["path"] == str(notice))
            self.assertEqual(event["event"], "UNKNOWN_RELEVANT_NOTICE")
            self.assertIsNone(event["time_utc8"])
            self.assertIsNone(event["timestamp_text"])
            self.assertIn("缺少可解析 UTC+8 时间", snapshot["reason"])

    def test_lease_snapshot_rejects_unsupported_timezone_suffixes(self) -> None:
        timestamp_lines = (
            "时间：2026-10-27 22:50 UTC-8",
            "时间：2026-10-27 22:50 PST",
            "日期：2026-10-27（UTC+9）",
        )
        for timestamp_line in timestamp_lines:
            with self.subTest(timestamp_line=timestamp_line), tempfile.TemporaryDirectory() as temp:
                raw = (
                    "# DSH-20261024-004 阶段3板级窗口\n"
                    f"{timestamp_line}\n"
                    "阶段3/6板级窗口信息。\n"
                )
                snapshot, notice = self._snapshot_for_notice(Path(temp), raw, "2026-10-28 00:00")
                self.assertFalse(snapshot["valid"])
                event = next(item for item in snapshot["events"] if item["path"] == str(notice))
                self.assertEqual(event["event"], "UNKNOWN_RELEVANT_NOTICE")
                self.assertIsNone(event["time_utc8"])
                self.assertIn("缺少可解析 UTC+8 时间", snapshot["reason"])

    def test_lease_snapshot_accepts_explicit_utc8_and_iso_offset_controls(self) -> None:
        cases = (
            ("时间：2026-10-27 22:50 UTC+8", "2026-10-27 23:00", "2026-10-27T22:50+08:00"),
            ("时间：2026-10-27T14:50-08:00", "2026-10-28 07:00", "2026-10-28T06:50+08:00"),
        )
        for timestamp_line, release_time, expected_start in cases:
            with self.subTest(timestamp_line=timestamp_line), tempfile.TemporaryDirectory() as temp:
                raw = (
                    "# DSH-20261024-004 阶段3板级窗口\n"
                    f"{timestamp_line}\n"
                    "阶段3/6板级窗口信息。\n"
                )
                snapshot, notice = self._snapshot_for_notice(Path(temp), raw, release_time)
                self.assertTrue(snapshot["valid"], snapshot["reason"])
                event = next(item for item in snapshot["events"] if item["path"] == str(notice))
                self.assertEqual(event["event"], "UNKNOWN_RELEVANT_NOTICE_PRE_RELEASE")
                self.assertEqual(event["time_utc8"], expected_start)
        with tempfile.TemporaryDirectory() as temp:
            raw = (
                "# DSH-20261024-001 日期型通报\n"
                "日期：2026-10-27 UTC+8\n"
                "阶段6板卡状态随通知提供。\n"
            )
            snapshot, notice = self._snapshot_for_notice(Path(temp), raw, "2026-10-28 00:00")
            self.assertTrue(snapshot["valid"], snapshot["reason"])
            event = next(item for item in snapshot["events"] if item["path"] == str(notice))
            self.assertEqual(event["time_range_utc8"], {
                "start_inclusive": "2026-10-27T00:00+08:00",
                "end_exclusive": "2026-10-28T00:00+08:00",
            })

    def test_october_24_partial_time_is_superseded_by_october_27_release_with_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            raw = (
                "# DSH-20261024-004 阶段3板级窗口\n"
                "时间：2026-10-24 00:5x（UTC+8）\n"
                "阶段3将开始单次板级窗口，结束后另行留证；阶段5/6接口后续对接。\n"
            )
            snapshot, notice = self._snapshot_for_notice(Path(temp), raw, "2026-10-27 23:00")
            self.assertTrue(snapshot["valid"], snapshot["reason"])
            event = next(item for item in snapshot["events"] if item["path"] == str(notice))
            self.assertEqual(event["event"], "UNKNOWN_RELEVANT_NOTICE_PRE_RELEASE")
            self.assertEqual(event["sha256"], hashlib.sha256(notice.read_bytes()).hexdigest())
            self.assertEqual(event["hash_basis"], "worktree_disk")
            self.assertEqual(event["timestamp_text"], "时间：2026-10-24 00:5x（UTC+8）")
            self.assertEqual(
                event["time_range_utc8"],
                {"start_inclusive": "2026-10-24T00:50+08:00", "end_exclusive": "2026-10-24T01:00+08:00"},
            )

    def test_date_only_october_24_notice_is_superseded_without_guessing_clock_time(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            raw = (
                "# DSH-20261024-001 阶段三方向调整\n"
                "编号：DSH-20261024-001；日期：2026-10-24（UTC+8）。\n"
                "阶段6按阶段三彩色实测调整输入方向，板卡状态随记录提供。\n"
            )
            snapshot, notice = self._snapshot_for_notice(Path(temp), raw, "2026-10-27 23:00")
            self.assertTrue(snapshot["valid"], snapshot["reason"])
            event = next(item for item in snapshot["events"] if item["path"] == str(notice))
            self.assertEqual(event["event"], "UNKNOWN_RELEVANT_NOTICE_PRE_RELEASE")
            self.assertEqual(event["sha256"], hashlib.sha256(notice.read_bytes()).hexdigest())
            self.assertEqual(event["timestamp_text"], "日期：2026-10-24（UTC+8）")
            self.assertEqual(
                event["time_range_utc8"],
                {"start_inclusive": "2026-10-24T00:00+08:00", "end_exclusive": "2026-10-25T00:00+08:00"},
            )

    def test_same_day_overlapping_partial_notice_and_release_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            snapshot, _ = self._snapshot_for_notice(
                Path(temp),
                "# DSH-20261024-004 阶段3板级窗口\n时间：2026-10-27 22:5x（UTC+8）\n"
                "阶段3/6板级窗口信息。\n",
                "2026-10-27 22:55",
            )
            self.assertFalse(snapshot["valid"])
            self.assertEqual(snapshot["events"][-1]["event"], "UNKNOWN_RELEVANT_NOTICE")
            self.assertIn("重叠或更晚", snapshot["reason"])

    def test_partial_notice_ending_at_release_boundary_is_provably_earlier(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            snapshot, _ = self._snapshot_for_notice(
                Path(temp),
                "# DSH-20261024-004 阶段3板级窗口\n时间：2026-10-27 22:5x（UTC+8）\n"
                "阶段3/6板级窗口信息。\n",
                "2026-10-27 23:00",
            )
            self.assertTrue(snapshot["valid"], snapshot["reason"])

    def test_cross_day_partial_notice_touching_release_boundary_is_provably_earlier(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            snapshot, _ = self._snapshot_for_notice(
                Path(temp),
                "# DSH-20261024-004 阶段3板级窗口\n时间：2026-10-26 23:5x（UTC+8）\n"
                "阶段3/6板级窗口信息。\n",
                "2026-10-27 00:00",
            )
            self.assertTrue(snapshot["valid"], snapshot["reason"])

    def test_future_or_undated_unknown_notice_blocks_after_release(self) -> None:
        notice_texts = (
            "# 后续阶段6板卡状态\n时间：2026-10-28 00:0x（UTC+8）\n阶段6板卡状态待核实。\n",
            "# 后续阶段6板卡状态\n阶段6板卡状态待核实。\n",
        )
        for notice_text in notice_texts:
            with self.subTest(notice_text=notice_text), tempfile.TemporaryDirectory() as temp:
                snapshot, _ = self._snapshot_for_notice(Path(temp), notice_text, "2026-10-27 23:00")
                self.assertFalse(snapshot["valid"])
                self.assertEqual(snapshot["events"][-1]["event"], "UNKNOWN_RELEVANT_NOTICE")

    def test_dsh_recall_blocks_then_explicit_release_reopens_then_new_recall_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            mailbox = root / "mailbox"
            mailbox.mkdir()
            lease = root / "DSH-20261027-008.md"
            lease.write_text("允许 Codex 阶段6 使用板卡\n", encoding="utf-8")
            pinned_sha = hashlib.sha256(lease.read_bytes()).hexdigest()
            recall = mailbox / "DSH-20261027-009-board-return-notice.md"
            recall.write_text(
                "# DSH-20261027-009 板卡归还通知\n- 时间：2026-10-27 22:30（UTC+8）\n"
                "暂勿开启新的板级会话，直到 DSH-20261027-010 板卡已释放。\n",
                encoding="utf-8",
            )
            release = mailbox / "DSH-20261027-010-board-released.md"
            with patch.object(scan, "LEASE_SHA256", pinned_sha):
                blocked, _ = scan.lease_status(lease, mailbox)
                self.assertFalse(blocked)
                release.write_text(
                    "# DSH-20261027-010 板卡已释放\n- 时间：2026-10-27 23:00（UTC+8）\n"
                    "关联 DSH-20261027-009；阶段6可按 DSH-20261027-008 使用；租用恢复有效。\n",
                    encoding="utf-8",
                )
                allowed, _ = scan.lease_status(lease, mailbox)
                self.assertTrue(allowed)
                later_recall = mailbox / "DSH-20261028-001-board-return-notice.md"
                later_recall.write_text(
                    "# DSH-20261028-001 板卡归还通知\n- 时间：2026-10-28 00:10（UTC+8）\n"
                    "暂勿开启新的板级会话。\n",
                    encoding="utf-8",
                )
                blocked_again, _ = scan.lease_status(lease, mailbox)
                self.assertFalse(blocked_again)

    def test_body_recall_then_later_release_and_unknown_later_notice(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            mailbox = root / "mailbox"
            mailbox.mkdir()
            lease = root / "DSH-20261027-008.md"
            lease.write_text("允许 Codex 阶段6 使用板卡\n时间：2026-10-27 22:10（UTC+8）\n", encoding="utf-8")
            pinned_sha = hashlib.sha256(lease.read_bytes()).hexdigest()
            body_recall = mailbox / "DSH-20261027-009-clarification.md"
            body_recall.write_text(
                "# 一般通知\n时间：2026-10-27 22:30（UTC+8）\n"
                "Codex 阶段6请暂勿开启新的板级会话，等待明确释放。\n",
                encoding="utf-8",
            )
            release = mailbox / "DSH-20261027-010-board-released.md"
            with patch.object(scan, "LEASE_SHA256", pinned_sha):
                self.assertFalse(scan.lease_snapshot(lease, mailbox)["valid"])
                release.write_text(
                    "# DSH-20261027-010 板卡已释放\n时间：2026-10-27 23:00（UTC+8）\n"
                    "关联 DSH-20261027-009；阶段6可按 DSH-20261027-008 使用，可以开启。\n",
                    encoding="utf-8",
                )
                released = scan.lease_snapshot(lease, mailbox)
                self.assertTrue(released["valid"])
                self.assertEqual([event["event"] for event in released["events"]], ["RECALLED", "RELEASED"])
                unknown = mailbox / "DSH-20261028-001-stage6-board-note.md"
                unknown.write_text(
                    "# 后续记录\n时间：2026-10-28T00:10:00+08:00\n"
                    "Codex 阶段6板卡使用状态需要重新确认。\n",
                    encoding="utf-8",
                )
                blocked = scan.lease_snapshot(lease, mailbox)
                self.assertFalse(blocked["valid"])
                self.assertEqual(blocked["events"][-1]["event"], "UNKNOWN_RELEVANT_NOTICE")

    def test_test_summary_accepts_unittest_zero_test_success(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "zero-tests.log"
            path.write_text("Ran 0 tests in 0.000s\n\nOK\n", encoding="utf-8")
            self.assertEqual(
                scan._parse_test_summary(path),
                {"tests_run": 0, "failures": 0, "errors": 0, "skipped": 0, "success_marker": "OK"},
            )

    def test_generic_unlabeled_board_return_blocks_after_stage6_release(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            mailbox = root / "mailbox"
            mailbox.mkdir()
            lease = root / "DSH-20261027-008.md"
            lease.write_text("允许 Codex 阶段6 使用板卡\n", encoding="utf-8")
            pinned_sha = hashlib.sha256(lease.read_bytes()).hexdigest()
            release = mailbox / "DSH-20261027-010-board-released.md"
            release.write_text(
                "# DSH-20261027-010 板卡已释放\n时间：2026-10-27 23:00（UTC+8）\n"
                "关联 DSH-20261027-008；阶段6可按租用条款使用，可以开启。\n",
                encoding="utf-8",
            )
            generic_recall = mailbox / "DSH-20261028-001-board-status.md"
            generic_recall.write_text(
                "# 通用板卡通知\n时间：2026-10-28 00:10（UTC+8）\n"
                "板卡已归还，请暂勿开启新的板级会话。\n",
                encoding="utf-8",
            )
            with patch.object(scan, "LEASE_SHA256", pinned_sha):
                snapshot = scan.lease_snapshot(lease, mailbox)
            self.assertFalse(snapshot["valid"])
            self.assertEqual(snapshot["events"][-1]["event"], "RECALLED")
            self.assertIn("DSH-20261028-001-board-status.md", snapshot["reason"])

    def test_confirmed_stage5_only_notice_before_stage6_release_is_recorded_as_out_of_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            mailbox = root / "mailbox"
            mailbox.mkdir()
            lease = root / "DSH-20261027-008.md"
            lease.write_text("允许 Codex 阶段6 使用板卡\n", encoding="utf-8")
            pinned_sha = hashlib.sha256(lease.read_bytes()).hexdigest()
            stage5 = mailbox / "DSH-20261027-001-stage5-hardware-window.md"
            stage5.write_text(
                "# 阶段5硬件窗口与实物授权\n- 时间（UTC+8）：2026-10-27 12:26–12:40\n"
                "收件方 Codex 项目总控；范围仅 S5-T02 阶段5板级项目。\n",
                encoding="utf-8",
            )
            release = mailbox / "DSH-20261027-010-board-released.md"
            release.write_text(
                "# DSH-20261027-010 板卡已释放\n- 时间：2026-10-27 23:00（UTC+8）\n"
                "关联 DSH-20261027-008；阶段6可按租用条款使用，可以开启。\n",
                encoding="utf-8",
            )
            self.assertEqual(scan._mail_timestamp(stage5.read_text(encoding="utf-8")).hour, 12)
            with patch.object(scan, "LEASE_SHA256", pinned_sha):
                snapshot = scan.lease_snapshot(lease, mailbox)
            self.assertTrue(snapshot["valid"])
            self.assertTrue(any(event["event"] == "OUT_OF_SCOPE_STAGE5_PRE_RELEASE" for event in snapshot["events"]))

    def test_lease_snapshot_binds_real_notice_paths_hashes_and_times_into_manifest_data(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            mailbox = root / "mailbox"
            mailbox.mkdir()
            lease = root / "DSH-20261027-008-board-lease-stage6.md"
            lease.write_text("允许 Codex 阶段6 使用板卡\n", encoding="utf-8")
            recall = mailbox / "DSH-20261027-009-board-return-notice.md"
            recall.write_text(
                "# DSH-20261027-009 板卡归还通知\n- 时间：2026-10-27 22:30（UTC+8）\n"
                "暂勿开启新的板级会话。\n", encoding="utf-8")
            release = mailbox / "DSH-20261027-010-board-released.md"
            release.write_text(
                "# DSH-20261027-010 板卡已释放\n- 时间：2026-10-27 23:00（UTC+8）\n"
                "关联 DSH-20261027-009；阶段6恢复有效。\n", encoding="utf-8")
            pinned = hashlib.sha256(lease.read_bytes()).hexdigest()
            with patch.object(scan, "LEASE_SHA256", pinned):
                snapshot = scan.lease_snapshot(lease, mailbox)
            self.assertTrue(snapshot["valid"])
            record = {}
            scan._record_lease_snapshot(record, "preflight", snapshot)
            evidence = record["lease_evidence"]
            self.assertEqual(evidence["lease_versions"][0]["path"], str(lease))
            self.assertEqual(evidence["lease_versions"][0]["expected_sha256"], pinned)
            self.assertEqual(evidence["lease_versions"][0]["observed_sha256"], pinned)
            by_path = {event["path"]: event for event in evidence["events"]}
            for path, stamp in ((recall, "2026-10-27T22:30+08:00"), (release, "2026-10-27T23:00+08:00")):
                event = by_path[str(path)]
                self.assertEqual(event["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
                self.assertEqual(event["time_utc8"], stamp)
                self.assertEqual(event["hash_basis"], "worktree_disk")

    def test_static_tool_hashes_are_pinned(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = [root / name for name in ("scan.tcl", "lease.md", "hw_server.exe", "xsdb.exe")]
            for path in paths:
                path.write_bytes(path.name.encode("utf-8"))
            with patch.object(scan, "SCAN_TCL", paths[0]), patch.object(scan, "LEASE", paths[1]), \
                 patch.object(scan, "HW_SERVER", paths[2]), patch.object(scan, "XSDB", paths[3]):
                with self.assertRaisesRegex(scan.ScanError, "固定输入 SHA-256 已变化"):
                    scan._static_inputs()

    def test_review_receipt_binds_code_test_evidence_and_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            receipt = _review_fixture(root)
            def git_blob(_root, *args):
                rel = args[-1].split(":", 1)[1]
                return (root / Path(rel)).read_bytes()
            with patch.object(scan, "_git_text", side_effect=lambda _root, *args: (
                    "d" * 40 if args[0] == "rev-parse" and args[1] == "HEAD" else FAKE_BLOB_OID)), \
                 patch.object(scan, "_git_bytes", side_effect=git_blob), \
                 patch.object(scan.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)):
                result = scan.validate_review_receipt(receipt, RUN_ID, root)
                self.assertEqual(result["status"], "REVIEW_RECEIPT_VERIFIED")

    def test_review_receipt_rejects_zero_tests_and_accepts_positive_count(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            receipt = _review_fixture(root)
            test_log = root / "offline-tests.log"
            receipt_path = root / "reviewer_receipt.json"

            def receipt_with_test_log(contents: str) -> dict:
                test_log.write_text(contents, encoding="utf-8")
                receipt["tests"]["summary"] = scan._parse_test_summary(test_log)
                receipt["tests"]["log_sha256"] = hashlib.sha256(test_log.read_bytes()).hexdigest()
                receipt_path.write_text(json.dumps(receipt, ensure_ascii=False), encoding="utf-8")
                return json.loads(receipt_path.read_text(encoding="utf-8"))

            def git_blob(_root, *args):
                rel = args[-1].split(":", 1)[1]
                return (root / Path(rel)).read_bytes()

            with patch.object(scan, "_git_text", side_effect=lambda _root, *args: (
                    "d" * 40 if args[0] == "rev-parse" and args[1] == "HEAD" else FAKE_BLOB_OID)), \
                 patch.object(scan, "_git_bytes", side_effect=git_blob), \
                 patch.object(scan.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)):
                zero_tests = receipt_with_test_log("Ran 0 tests in 0.000s\n\nOK\n")
                with self.assertRaisesRegex(scan.ScanError, "成功摘要缺失"):
                    scan.validate_review_receipt(zero_tests, RUN_ID, root)
                one_test = receipt_with_test_log("Ran 1 test in 0.001s\n\nOK\n")
                result = scan.validate_review_receipt(one_test, RUN_ID, root)
                self.assertEqual(result["status"], "REVIEW_RECEIPT_VERIFIED")

    def test_outdated_source_sha_in_review_receipt_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            receipt = _review_fixture(root)
            (root / "verification" / "s6e_jtag_readonly_scan.py").write_text("changed after review\n", encoding="utf-8")
            with patch.object(scan, "_git_text", return_value=FAKE_BLOB_OID), \
                 patch.object(scan, "_git_bytes", return_value=b"reviewed blob"), \
                 patch.object(scan.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)):
                with self.assertRaisesRegex(scan.ScanError, "磁盘字节与当前文件不一致"):
                    scan.validate_review_receipt(receipt, RUN_ID, root)

    def test_review_receipt_rejects_different_commit_blob_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            receipt = _review_fixture(root)
            rel = "verification/s6e_jtag_readonly_scan.py"
            stale_blob = b"different committed bytes\n"
            receipt["reviewed_files"][rel]["commit_blob_sha256"] = hashlib.sha256(stale_blob).hexdigest()
            def git_blob(_root, *args):
                return stale_blob if args[-1].endswith(rel) else (root / Path(args[-1].split(":", 1)[1])).read_bytes()
            with patch.object(scan, "_git_text", side_effect=lambda _root, *args: (
                    "d" * 40 if args[0] == "rev-parse" and args[1] == "HEAD" else FAKE_BLOB_OID)), \
                 patch.object(scan, "_git_bytes", side_effect=git_blob), \
                 patch.object(scan.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)):
                with self.assertRaisesRegex(scan.ScanError, "工作树源码与提交 blob 字节不一致"):
                    scan.validate_review_receipt(receipt, RUN_ID, root)

    def test_review_receipt_requires_fixed_command_and_clean_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            receipt = _review_fixture(root)
            receipt["tests"]["command"] = ["python", "-B", "-m", "unittest"]
            with self.assertRaisesRegex(scan.ScanError, "固定审查命令"):
                scan.validate_review_receipt(receipt, RUN_ID, root)
            receipt = _review_fixture(root)
            receipt["tests"]["summary"]["tests_run"] = 23
            with patch.object(scan, "_git_text", side_effect=lambda _root, *args: (
                    "d" * 40 if args[0] == "rev-parse" and args[1] == "HEAD" else FAKE_BLOB_OID)), \
                 patch.object(scan, "_git_bytes", side_effect=lambda _root, *args: (
                    root / Path(args[-1].split(":", 1)[1])).read_bytes()), \
                 patch.object(scan.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)):
                with self.assertRaisesRegex(scan.ScanError, "成功摘要缺失"):
                    scan.validate_review_receipt(receipt, RUN_ID, root)

    def test_review_receipt_for_other_run_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            receipt = _review_fixture(root, "s6e_jtag_readonly_20261028_r02")
            with self.assertRaisesRegex(scan.ScanError, "任务/scope"):
                scan.validate_review_receipt(receipt, RUN_ID, root)

    def test_stop_uses_only_owned_process_handle(self) -> None:
        proc = MagicMock()
        proc.poll.return_value = None
        proc.wait.return_value = 0
        self.assertEqual(scan._stop_own_process(proc), "TERMINATED_OWN_PROCESS")
        proc.terminate.assert_called_once_with()
        proc.kill.assert_not_called()

    def test_stop_kills_only_owned_handle_after_bounded_timeout(self) -> None:
        proc = MagicMock()
        proc.poll.return_value = None
        proc.wait.side_effect = [subprocess.TimeoutExpired("owned", 5), 0]
        self.assertEqual(scan._stop_own_process(proc), "KILLED_OWN_PROCESS_AFTER_TIMEOUT")
        proc.kill.assert_called_once_with()

    def _run_mocked_execute(self, root: Path, lease_results: list[bool] | None = None, failure: str | None = None):
        (root / "report" / "evidence" / "S6-E").mkdir(parents=True, exist_ok=True)
        receipt_path = root / "reviewer_receipt.json"
        receipt_path.write_text("{}", encoding="utf-8")
        evidence = root / "review.md"
        evidence.write_text("reviewed\n", encoding="utf-8")
        test_log = root / "tests.log"
        test_log.write_text("Ran 24 tests in 0.076s\n\nOK\n", encoding="utf-8")
        (root / "verification").mkdir(parents=True, exist_ok=True)
        source_bytes = b"mocked source\n"
        source_blob_sha = hashlib.sha256(source_bytes).hexdigest()
        source_files = {}
        for rel in ("verification/s6e_jtag_readonly_scan.py", "verification/test_s6e_jtag_readonly_scan.py"):
            (root / Path(rel)).write_bytes(source_bytes)
            source_files[rel] = {
                "worktree_disk_hash_basis": "worktree_disk",
                "worktree_disk_sha256": hashlib.sha256(source_bytes).hexdigest(),
                "commit_blob_hash_basis": "commit_blob",
                "commit_blob_oid": FAKE_BLOB_OID,
                "commit_blob_sha256": source_blob_sha,
            }
        receipt = {
            "reviewed_files": source_files,
            "tests": {"command": list(scan.EXPECTED_TEST_COMMAND), "working_directory": scan.EXPECTED_TEST_WORKDIR,
                      "exit_code": 0, "summary": {"tests_run": 24, "failures": 0, "errors": 0,
                                                    "skipped": 0, "success_marker": "OK"},
                      "log_path": "tests.log", "log_hash_basis": "worktree_disk",
                      "log_sha256": hashlib.sha256(test_log.read_bytes()).hexdigest()},
            "review_evidence_path": "review.md",
            "review_evidence_hash_basis": "worktree_disk",
            "review_evidence_sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
        }
        review = {"reviewed_commit": FAKE_COMMIT, "reviewer_id": "independent-reviewer",
                  "receipt_file_sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest()}
        active_ports: set[int] = set()
        processes: list[FakeProc] = []
        next_pid = iter((4101, 4102))

        def fake_popen(argv, **kwargs):
            is_server = argv[0] == str(scan.HW_SERVER)
            if failure == "server-popen" and is_server:
                raise OSError("mock hw_server Popen failure")
            if failure == "xsdb-popen" and not is_server:
                raise OSError("mock xsdb Popen failure")
            role = "server-cleanup-fail" if is_server and failure == "cleanup-fail" else (
                "server" if is_server else (
                    "xsdb-timeout" if failure == "xsdb-timeout" else
                    ("xsdb-wait" if lease_results is not None else "xsdb-complete")
                )
            )
            proc = FakeProc(next(next_pid), role, active_ports, kwargs.get("stdout"))
            if is_server:
                active_ports.add(proc.pid)
            processes.append(proc)
            return proc

        def lease_snapshot():
            if lease_results is None:
                value = True
            else:
                value = lease_results.pop(0) if lease_results else False
            events = [
                {"event": "RECALLED", "path": r"D:\mailbox\DSH-009.md", "hash_basis": "worktree_disk",
                 "sha256": "1" * 64, "time_utc8": "2026-10-27T22:30+08:00"},
                {"event": "RELEASED", "path": r"D:\mailbox\DSH-010.md", "hash_basis": "worktree_disk",
                 "sha256": "2" * 64, "time_utc8": "2026-10-27T23:00+08:00"},
            ]
            if not value and lease_results is not None:
                events.append({"event": "RECALLED", "path": r"D:\mailbox\DSH-011.md", "hash_basis": "worktree_disk",
                               "sha256": "3" * 64, "time_utc8": "2026-10-28T00:10+08:00"})
            return {
                "valid": value,
                "reason": "test lease valid" if value else "test recall",
                "lease_file": {"path": r"D:\mailbox\DSH-008.md", "hash_basis": "worktree_disk",
                               "expected_sha256": "0" * 64, "observed_sha256": "0" * 64, "valid": value},
                "mailbox_path": r"D:\mailbox",
                "events": events,
            }

        patches = contextlib.ExitStack()
        patches.enter_context(patch.object(scan, "ROOT", root))
        patches.enter_context(patch.object(scan, "REVIEW_RECEIPT", receipt_path))
        patches.enter_context(patch.object(scan, "verify_formal_claim", return_value={
            "offer_source_commit": FAKE_COMMIT, "status": "FORMAL_CLAIM_VERIFIED", "hardware_run_id": RUN_ID,
            "scope": scan.SCOPE,
        }))
        patches.enter_context(patch.object(scan, "_read_review_receipt", return_value=(receipt, review)))
        patches.enter_context(patch.object(scan, "lease_snapshot", side_effect=lease_snapshot))
        patches.enter_context(patch.object(scan, "_static_inputs", return_value={"pinned-input": FAKE_SHA}))
        patches.enter_context(patch.object(scan, "_checked_source_artifact", side_effect=lambda _root, commit, rel: {
            "path": rel, "worktree_disk_hash_basis": "worktree_disk",
            "worktree_disk_sha256": hashlib.sha256(b"mocked source\n").hexdigest(),
            "reviewed_commit": commit, "commit_blob_hash_basis": "commit_blob",
            "commit_blob_oid": FAKE_BLOB_OID, "commit_blob_sha256": source_blob_sha,
        }))
        patches.enter_context(patch.object(scan, "_git_text", return_value="d" * 40))
        return patches, fake_popen, active_ports, processes, lease_snapshot

    def test_mock_only_success_manifest_binds_inputs_and_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            patches, fake_popen, active_ports, processes, _ = self._run_mocked_execute(root)
            with patches:
                result = scan.execute(RUN_ID, confirm_exclusive_window=True, process_query=lambda: set(),
                                      port_query=lambda: sorted(active_ports), popen=fake_popen, sleep=lambda _seconds: None)
            self.assertEqual(result["status"], "PASS_READ_ONLY_TOPOLOGY")
            self.assertEqual(result["acceptance_claim"], "NONE; does not satisfy S6-E gates or G3/G4/G5")
            self.assertEqual(result["reviewer_receipt"]["test"]["exit_code"], 0)
            self.assertEqual(len(result["commands"]), 2)
            self.assertTrue(all(type(command["exit_code"]) is int for command in result["commands"]))
            manifest = root / "report" / "evidence" / "S6-E" / RUN_ID / "execution_manifest.json"
            parsed = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(parsed["run_id"], RUN_ID)
            self.assertIn("baseline_commit", parsed)
            self.assertEqual(parsed["source_artifacts"]["verification/s6e_jtag_readonly_scan.py"]["worktree_disk_hash_basis"],
                             "worktree_disk")
            lease_events = {event["path"]: event for event in parsed["lease_evidence"]["events"]}
            self.assertEqual(lease_events[r"D:\mailbox\DSH-009.md"]["sha256"], "1" * 64)
            self.assertEqual(lease_events[r"D:\mailbox\DSH-010.md"]["time_utc8"], "2026-10-27T23:00+08:00")
            self.assertEqual(len(processes), 2)
            self.assertEqual(processes[0].terminate_calls, 1)

    def test_recall_during_scan_stops_only_our_processes_and_preserves_logs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            lease_sequence = [True, True, True, True, False, False]
            patches, fake_popen, active_ports, processes, _ = self._run_mocked_execute(root, lease_sequence)
            with patches:
                result = scan.execute(RUN_ID, confirm_exclusive_window=True, process_query=lambda: set(),
                                      port_query=lambda: sorted(active_ports), popen=fake_popen, sleep=lambda _seconds: None)
            self.assertEqual(result["status"], "FAIL_STOPPED")
            self.assertTrue(any("running_xsdb" in error for error in result["errors"]))
            self.assertEqual(len(processes), 2)
            self.assertEqual([proc.terminate_calls for proc in processes], [1, 1])
            run_dir = root / "report" / "evidence" / "S6-E" / RUN_ID
            self.assertTrue((run_dir / "hw_server.log").is_file())
            self.assertTrue((run_dir / "xsdb_scan2.log").is_file())
            manifest = json.loads((run_dir / "execution_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "FAIL_STOPPED")
            self.assertTrue(all(type(command["exit_code"]) is int for command in manifest["commands"]))
            lease_events = {event["path"]: event for event in manifest["lease_evidence"]["events"]}
            self.assertEqual(lease_events[r"D:\mailbox\DSH-011.md"]["sha256"], "3" * 64)
            self.assertEqual(lease_events[r"D:\mailbox\DSH-011.md"]["time_utc8"], "2026-10-28T00:10+08:00")

    def test_popen_failures_are_saved_in_unique_run_manifest(self) -> None:
        for failure in ("server-popen", "xsdb-popen"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                patches, fake_popen, active_ports, _processes, _ = self._run_mocked_execute(root, failure=failure)
                with patches:
                    result = scan.execute(RUN_ID, confirm_exclusive_window=True, process_query=lambda: set(),
                                          port_query=lambda: sorted(active_ports), popen=fake_popen, sleep=lambda _seconds: None)
                self.assertEqual(result["status"], "FAIL_STOPPED")
                self.assertTrue(result["errors"])
                manifest = root / "report" / "evidence" / "S6-E" / RUN_ID / "execution_manifest.json"
                self.assertTrue(manifest.is_file())
                parsed = json.loads(manifest.read_text(encoding="utf-8"))
                self.assertEqual(parsed["status"], "FAIL_STOPPED")
                self.assertTrue((manifest.parent / "hw_server.log").is_file())
                if failure == "xsdb-popen":
                    self.assertEqual(parsed["commands"][0]["exit_code"], -15)
                    self.assertTrue((manifest.parent / "xsdb_scan2.log").is_file())

    def test_xsdb_timeout_is_bounded_and_preserves_command_logs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            patches, fake_popen, active_ports, processes, _ = self._run_mocked_execute(root, failure="xsdb-timeout")
            clock = [0.0]
            def sleep(seconds):
                clock[0] += seconds
            with patches:
                result = scan.execute(RUN_ID, confirm_exclusive_window=True, process_query=lambda: set(),
                                      port_query=lambda: sorted(active_ports), popen=fake_popen,
                                      monotonic=lambda: clock[0], sleep=sleep)
            self.assertEqual(result["status"], "FAIL_STOPPED")
            self.assertTrue(any("XSDB 超过 30 秒" in error for error in result["errors"]))
            self.assertLessEqual(result["elapsed_seconds"], 80)
            self.assertTrue(all(type(command["exit_code"]) is int for command in result["commands"]))
            run_dir = root / "report" / "evidence" / "S6-E" / RUN_ID
            self.assertTrue((run_dir / "hw_server.log").is_file())
            self.assertTrue((run_dir / "xsdb_scan2.log").is_file())
            self.assertEqual([proc.terminate_calls for proc in processes], [1, 1])

    def test_cleanup_failure_is_recorded_and_does_not_force_kill_foreign_handles(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            patches, fake_popen, active_ports, processes, _ = self._run_mocked_execute(root, failure="cleanup-fail")
            with patches:
                result = scan.execute(RUN_ID, confirm_exclusive_window=True, process_query=lambda: set(),
                                      port_query=lambda: sorted(active_ports), popen=fake_popen, sleep=lambda _seconds: None)
            self.assertEqual(result["status"], "FAIL_STOPPED")
            self.assertTrue(result["cleanup"]["hw_server"].startswith("STOP_FAILED"))
            self.assertEqual(result["cleanup"]["remaining_3121_listeners"], [4101])
            self.assertEqual(processes[0].kill_calls, 0)
            manifest = root / "report" / "evidence" / "S6-E" / RUN_ID / "execution_manifest.json"
            parsed = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertTrue(parsed["cleanup"]["hw_server"].startswith("STOP_FAILED"))
            self.assertTrue((manifest.parent / "hw_server.log").is_file())


if __name__ == "__main__":
    unittest.main()

