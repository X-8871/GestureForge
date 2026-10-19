"""交接检查器的隔离单元测试。

全部用例只在 `tempfile` 临时目录内建沙盒仓库（`git init`），不读写主工作树；
仅 `--print-template` 与 CLI 入口用例读取仓库内的 `verification/handoff_check.py`。

时间无关约定（防止验收命令随真实墙钟由绿转红）：
- 进程内用例一律通过 `now=NOW` 注入固定时刻，心跳按 `NOW ± 偏移` 生成；
- 必须走真实 CLI 的用例用真实墙钟生成心跳（`live_record()` / `heartbeat_text(live_now())`），
  过期心跳则由真实墙钟减去足够大的偏移得到；
- 断言不得依赖“运行时恰好过期/未过期”，只依赖注入或动态推导的事实。
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from verification import handoff_check as checker


def use_utf8_streams() -> None:
    """让自测输出统一为 UTF-8，不受 Windows 控制台代码页影响。"""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (ValueError, OSError):  # 已关闭或不可重配置的流
                pass


use_utf8_streams()


REPO_ROOT = Path(__file__).absolute().parent.parent
CHECKER_PATH = REPO_ROOT / "verification" / "handoff_check.py"
UTC8 = timezone(timedelta(hours=8))
# 进程内用例注入的“当前时间”，与真实墙钟完全解耦。
NOW = datetime(2026, 10, 19, 20, 0, 0, tzinfo=UTC8)
HEARTBEAT_MINUTES_DEFAULT = 120


def heartbeat_text(moment: datetime) -> str:
    """把时刻转成交接行心跳文本（UTC+8，分钟精度）。"""
    return moment.astimezone(UTC8).strftime("%Y-%m-%d %H:%M")


def live_now() -> datetime:
    """真实墙钟（UTC+8）；仅供必须走真实 CLI 的用例生成动态心跳。"""
    return datetime.now(UTC8)
FORBIDDEN_GIT_VERBS = {
    "add",
    "commit",
    "checkout",
    "stash",
    "reset",
    "clean",
    "push",
    "fetch",
    "pull",
    "merge",
    "rebase",
    "rm",
    "mv",
    "init",
    "switch",
    "restore",
    "gc",
}


def no_processes() -> tuple[list[dict[str, str]], None]:
    """注入探针：无重型进程。"""
    return [], None


def vivado_running() -> tuple[list[dict[str, str]], None]:
    """注入探针：存在 vivado 进程。"""
    return [{"image": "vivado.exe", "pid": "4321"}], None


def probe_unavailable() -> tuple[None, str]:
    """注入探针：当前平台无法枚举进程。"""
    return None, "测试注入：当前平台无法枚举进程"


class HandoffCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="handoff-check-test-")
        self.sandbox = Path(self.temporary.name)
        subprocess.run(["git", "init", "--quiet"], cwd=self.sandbox, check=True)
        subprocess.run(
            ["git", "config", "user.name", "Handoff Check Test"],
            cwd=self.sandbox,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "handoff-check@example.invalid"],
            cwd=self.sandbox,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "--quiet", "--allow-empty", "-m", "fixture"],
            cwd=self.sandbox,
            check=True,
        )
        self.root = Path(self.git(["rev-parse", "--show-toplevel"]))
        self.commit = self.git(["rev-parse", "HEAD"])
        self.branch = self.git(["rev-parse", "--abbrev-ref", "HEAD"])

    def tearDown(self) -> None:
        self.temporary.cleanup()

    # ---------- 基础设施 ----------

    def git(self, args: list[str], cwd: Path | None = None) -> str:
        """测试夹具用的 git 命令（只作用于临时沙盒）。"""
        completed = subprocess.run(
            ["git", *args],
            cwd=cwd or self.sandbox,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        return completed.stdout.strip()

    def write_text(self, relative: str, text: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def write_json(self, relative: str, data: object) -> Path:
        return self.write_text(
            relative,
            json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        )

    def make_record(self, **overrides: object) -> dict:
        record: dict = {
            "task": "HL-T01",
            "owner": "DSH",
            "worktree": str(self.root),
            "branch": self.branch,
            "base_commit": self.commit,
            "allowed_paths": [
                "verification/handoff_check.py",
                "verification/test_handoff_check.py",
            ],
            "dirty_owner": "无未提交改动",
            "yield_statement": "本轮已让出写权限，无并发写入方",
            # 心跳相对注入时刻 NOW 生成，绝不用固定日历字面量。
            "heartbeat_utc8": heartbeat_text(NOW - timedelta(minutes=30)),
            "evidence_dir": None,
            "recovery_command": "python -B -m unittest verification.test_handoff_check -v",
            "status": "OFFERED",
            "next_owner": "Codex",
        }
        record.update(overrides)
        return record

    def live_record(self, **overrides: object) -> dict:
        """心跳取自真实墙钟的记录，供走真实 CLI 的用例使用（任意时间均新鲜）。"""
        overrides.setdefault("heartbeat_utc8", heartbeat_text(live_now()))
        return self.make_record(**overrides)

    def run_check(
        self,
        record: dict | None = None,
        claimed_paths: tuple[str, ...] = (),
        max_minutes: int = HEARTBEAT_MINUTES_DEFAULT,
        claim: bool = False,
        worktree: str | None = None,
        probe=no_processes,
    ) -> dict:
        return checker.check_handoff(
            worktree_arg=worktree if worktree is not None else str(self.root),
            record=record,
            claimed_paths=claimed_paths,
            max_heartbeat_minutes=max_minutes,
            claim=claim,
            now=NOW,
            process_probe=probe,
        )

    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-B", str(CHECKER_PATH), *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    @staticmethod
    def statuses(result: dict) -> dict[str, str]:
        return {check["id"]: check["status"] for check in result["checks"]}

    @staticmethod
    def check_of(result: dict, ident: str) -> dict:
        return next(check for check in result["checks"] if check["id"] == ident)

    def assertCheck(self, result: dict, ident: str, expected: str) -> dict:  # noqa: N802
        check = self.check_of(result, ident)
        self.assertEqual(expected, check["status"], check)
        return check

    # ---------- 模板 ----------

    def test_模板含11字段与状态机取值(self) -> None:
        text = checker.render_template()
        self.assertEqual(11, len(checker.TEMPLATE_FIELDS))
        header = " | ".join(checker.TEMPLATE_FIELDS)
        self.assertIn(header, text)
        for label in checker.TEMPLATE_FIELDS:
            self.assertIn(label, header)
        self.assertIn("IDLE→OFFERED→CLAIMED→IN_PROGRESS→DONE", text)
        self.assertIn("只有该状态允许新接手方接管", text)
        self.assertIn("心跳超时 且 无重型进程 且 无 index.lock", text)
        for key in checker.RECORD_KEYS:
            self.assertIn(key, text)
        self.assertIn("退出码：0 全部 PASS/SKIP；1 存在 FAIL；2 输入或环境错误。", text)
        self.assertIn("不写仓库文件", text)

    def test_打印模板CLI退出码为0且与函数输出一致(self) -> None:
        completed = self.run_cli("--print-template")
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("", completed.stderr)
        self.assertEqual(checker.render_template(), completed.stdout)

    # ---------- PASS 路径 ----------

    def test_全PASS路径(self) -> None:
        self.write_text("verification/handoff_check.py", "# 本测试沙盒内的占位实现\n")
        self.write_text(
            "report/evidence/HL-T01/run01/manifest.json",
            json.dumps({"task_id": "HL-T01"}, ensure_ascii=False),
        )
        record = self.make_record(
            evidence_dir="report/evidence/HL-T01/run01",
            dirty_owner="临时沙盒内的 README 属 DSH",
        )
        result = self.run_check(record=record, claimed_paths=("verification/handoff_check.py",))
        self.assertEqual(
            {
                "a": "PASS",
                "b": "PASS",
                "c": "PASS",
                "d": "PASS",
                "e": "PASS",
                "f": "PASS",
                "g": "PASS",
                "h": "PASS",
                "i": "SKIP",
            },
            self.statuses(result),
        )
        self.assertEqual("HANDOFF_OK", result["status"])
        self.assertEqual(0, checker.exit_code_for(result))

    def test_未提供record时记录类检查项SKIP(self) -> None:
        result = self.run_check(record=None)
        expected = {ident: "SKIP" for ident in "efghi"}
        actual = self.statuses(result)
        for ident, status in expected.items():
            self.assertEqual(status, actual[ident], self.check_of(result, ident))
        self.assertIn("--claim", self.check_of(result, "i")["reason"])
        self.assertEqual("HANDOFF_OK", result["status"])
        self.assertEqual(0, checker.exit_code_for(result))
        self.assertIsNone(result["lost_contact"]["lost_contact"])

    def test_工作树参数指向子目录时改用工作树根(self) -> None:
        (self.root / "sub").mkdir()
        result = self.run_check(record=None, worktree=str(self.root / "sub"))
        self.assertCheck(result, "a", "PASS")
        self.assertEqual(os.fspath(self.root), result["worktree_root"])
        self.assertTrue(any("已改用工作树根" in item for item in result["warnings"]))

    def test_脏树已声明归属则PASS(self) -> None:
        self.write_text("untracked.txt", "未提交内容\n")
        result = self.run_check(record=self.make_record())
        check = self.assertCheck(result, "c", "PASS")
        self.assertIn("未提交改动 1 项", check["evidence"])
        self.assertIn("声明归属=无未提交改动", check["evidence"])

    # ---------- FAIL 路径 ----------

    def test_FAIL_起始提交不符(self) -> None:
        result = self.run_check(record=self.make_record(base_commit="0" * 40))
        check = self.assertCheck(result, "a", "FAIL")
        self.assertIn("实际 HEAD", check["reason"])
        self.assertEqual(1, checker.exit_code_for(result))

    def test_FAIL_分支不符(self) -> None:
        result = self.run_check(record=self.make_record(branch="codex/other-branch"))
        self.assertCheck(result, "a", "FAIL")

    def test_FAIL_工作树路径声明不符(self) -> None:
        result = self.run_check(record=self.make_record(worktree=str(self.root / "elsewhere")))
        self.assertCheck(result, "a", "FAIL")

    def test_FAIL_缩写提交仍按前缀核验(self) -> None:
        result = self.run_check(record=self.make_record(base_commit=self.commit[:8]))
        self.assertCheck(result, "a", "PASS")
        wrong_short = self.commit[:6] + ("0" if self.commit[6] != "0" else "1")
        result = self.run_check(record=self.make_record(base_commit=wrong_short))
        self.assertCheck(result, "a", "FAIL")

    def test_FAIL_主仓库根index锁(self) -> None:
        lock = self.root / ".git" / "index.lock"
        lock.write_text("", encoding="utf-8")
        result = self.run_check(record=self.make_record())
        check = self.assertCheck(result, "b", "FAIL")
        self.assertIn("index.lock 存在", check["reason"])
        self.assertIn("rev-parse --git-path index.lock", check["evidence"])

    def test_FAIL_链接工作树的index锁路径由git解析(self) -> None:
        linked = self.sandbox / "linked"
        completed = subprocess.run(
            ["git", "worktree", "add", "--detach", "--quiet", str(linked)],
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if completed.returncode != 0:
            self.skipTest(f"当前环境不支持 git worktree add：{completed.stderr.strip()}")
        linked_root = Path(self.git(["rev-parse", "--show-toplevel"], cwd=linked))
        self.assertTrue((linked_root / ".git").is_file(), "链接工作树的 .git 应为文件")
        resolved = Path(
            self.git(["rev-parse", "--git-path", "index.lock"], cwd=linked_root)
        )
        if not resolved.is_absolute():
            resolved = linked_root / resolved
        self.assertNotEqual(
            os.path.normcase(os.fspath(linked_root / ".git" / "index.lock")),
            os.path.normcase(os.fspath(resolved)),
            "链接工作树的锁路径必须与 <工作树>/.git/index.lock 不同",
        )
        clean = self.run_check(
            record=self.make_record(worktree=str(linked_root)), worktree=str(linked_root)
        )
        self.assertCheck(clean, "b", "PASS")
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text("", encoding="utf-8")
        try:
            locked = self.run_check(
                record=self.make_record(worktree=str(linked_root)), worktree=str(linked_root)
            )
        finally:
            resolved.unlink()
        check = self.assertCheck(locked, "b", "FAIL")
        self.assertIn(
            os.fspath(resolved).replace("\\", "/").casefold(),
            check["evidence"].casefold(),
        )

    def test_FAIL_脏树未声明归属(self) -> None:
        self.write_text("untracked.txt", "未提交内容\n")
        record = self.make_record()
        del record["dirty_owner"]
        result = self.run_check(record=record)
        check = self.assertCheck(result, "c", "FAIL")
        self.assertIn("未提交改动归属", check["reason"])
        self.assertEqual(1, checker.exit_code_for(result))

    def test_FAIL_心跳超时(self) -> None:
        stale = heartbeat_text(NOW - timedelta(minutes=300))
        result = self.run_check(record=self.make_record(heartbeat_utc8=stale))
        check = self.assertCheck(result, "e", "FAIL")
        self.assertIn("心跳超过 120 分钟阈值", check["reason"])
        self.assertEqual(1, checker.exit_code_for(result))

    def test_心跳阈值可调(self) -> None:
        # 恰好 300 分钟前：阈值 300 视为未过期，阈值 1 视为过期，均与真实墙钟无关。
        record = self.make_record(heartbeat_utc8=heartbeat_text(NOW - timedelta(minutes=300)))
        self.assertCheck(self.run_check(record=record, max_minutes=300), "e", "PASS")
        self.assertCheck(self.run_check(record=record, max_minutes=1), "e", "FAIL")

    def test_FAIL_心跳格式非法与未来时间(self) -> None:
        self.assertCheck(
            self.run_check(record=self.make_record(heartbeat_utc8="昨天")), "e", "FAIL"
        )
        future = heartbeat_text(NOW + timedelta(minutes=30))
        self.assertCheck(
            self.run_check(record=self.make_record(heartbeat_utc8=future)), "e", "FAIL"
        )
        self.assertCheck(
            self.run_check(record=self.make_record(heartbeat_utc8="")), "e", "FAIL"
        )

    def test_心跳支持带时区后缀(self) -> None:
        # 与注入时刻相差 10 分钟，但带 Z 后缀（UTC），用于核验时区归一化。
        utc_text = (
            (NOW - timedelta(minutes=10))
            .astimezone(timezone.utc)
            .strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        self.assertCheck(
            self.run_check(record=self.make_record(heartbeat_utc8=utc_text)), "e", "PASS"
        )

    def test_FAIL_非法状态与接管条件(self) -> None:
        result = self.run_check(record=self.make_record(status="RUNNING"))
        check = self.assertCheck(result, "f", "FAIL")
        self.assertIn("非法状态", check["reason"])
        self.assertCheck(self.run_check(record=self.make_record(status="CLAIMED"), claim=True), "f", "FAIL")
        self.assertCheck(self.run_check(record=self.make_record(status="IDLE"), claim=True), "f", "FAIL")
        self.assertCheck(self.run_check(record=self.make_record(status="OFFERED"), claim=True), "f", "PASS")
        self.assertCheck(self.run_check(record=self.make_record(), claim=True), "f", "PASS")
        self.assertCheck(self.run_check(record=None, claim=True), "f", "FAIL")
        self.assertCheck(self.run_check(record=self.make_record(status="DONE")), "f", "PASS")

    def test_claim强制让出契约(self) -> None:
        """OBS-2 反例：--claim 时 yield_statement/next_owner 缺失或占位必须 FAIL。"""
        complete = self.run_check(
            record=self.make_record(),
            claimed_paths=("verification/handoff_check.py",),
            claim=True,
        )
        self.assertCheck(complete, "i", "PASS")
        self.assertCheck(complete, "f", "PASS")
        self.assertEqual("HANDOFF_OK", complete["status"], complete["checks"])
        self.assertEqual(0, checker.exit_code_for(complete))

        # 反例 1：next_owner 占位（<> 包裹）
        placeholder = self.make_record(next_owner="<下一接手方>")
        check = self.assertCheck(self.run_check(record=placeholder, claim=True), "i", "FAIL")
        self.assertIn("next_owner", check["reason"])
        self.assertIn("占位", check["reason"])
        self.assertEqual(
            1, checker.exit_code_for(self.run_check(record=placeholder, claim=True))
        )

        # 反例 2：yield_statement 缺失
        missing = self.make_record()
        del missing["yield_statement"]
        check = self.assertCheck(self.run_check(record=missing, claim=True), "i", "FAIL")
        self.assertIn("yield_statement", check["reason"])
        self.assertIn("缺失", check["reason"])

        # 反例 3：两项均不成立，需同时指明
        both = self.make_record(yield_statement="<待填写>", next_owner="")
        check = self.assertCheck(self.run_check(record=both, claim=True), "i", "FAIL")
        self.assertIn("yield_statement", check["reason"])
        self.assertIn("next_owner", check["reason"])

        # 非 --claim 时该检查不适用
        self.assertCheck(
            self.run_check(record=self.make_record(next_owner="")), "i", "SKIP"
        )
        # --claim 但无 record：无法核验契约
        self.assertCheck(self.run_check(record=None, claim=True), "i", "FAIL")
        # 回归：非 OFFERED 状态仍拒绝 claim（f 项）
        taken = self.make_record(status="CLAIMED")
        self.assertCheck(self.run_check(record=taken, claim=True), "f", "FAIL")

    def test_模板写明字段核验语义与匹配规则(self) -> None:
        text = checker.render_template()
        for field, note in checker.MANUAL_REVIEW_NOTES.items():
            self.assertIn("不参与机器核验", note)
            self.assertIn(f"- {field}：{note}；", text)
        for field in checker.CLAIM_CONTRACT_FIELDS:
            self.assertIn(f"- {field}：--claim 时必须非空且非占位（检查项 i）；", text)
        self.assertEqual(("yield_statement", "next_owner"), checker.CLAIM_CONTRACT_FIELDS)
        self.assertIn("精确路径严格相等，不做前缀匹配", text)
        self.assertIn("dir/ 表示子树", text)
        self.assertIn("只匹配单个路径段，不跨 /", text)
        self.assertIn("** 作为独立路径段匹配零个或多个段", text)
        self.assertIn("反斜杠与 ./ 统一归一化为 / 相对路径", text)
        self.assertIn("i 接管让出契约（仅 --claim 时生效）", text)

    def test_FAIL_越界路径与同前缀陷阱(self) -> None:
        record = self.make_record()
        self.assertCheck(
            self.run_check(record=record, claimed_paths=("verification/handoff_check.py",)),
            "h",
            "PASS",
        )
        check = self.assertCheck(
            self.run_check(record=record, claimed_paths=("verification/handoff_check.py.bak",)),
            "h",
            "FAIL",
        )
        self.assertIn("不在允许修改范围内", check["reason"])
        self.assertCheck(
            self.run_check(record=record, claimed_paths=("src/other.c",)), "h", "FAIL"
        )
        outside = self.run_check(
            record=record, claimed_paths=(str(self.sandbox.parent / "handoff-outside.py"),)
        )
        check = self.assertCheck(outside, "h", "FAIL")
        self.assertIn("越出工作树", check["reason"])

    def test_允许范围支持目录与glob(self) -> None:
        record = self.make_record(allowed_paths=["verification/", "tmp/**"])
        self.assertCheck(
            self.run_check(record=record, claimed_paths=("verification/a/b.py",)), "h", "PASS"
        )
        self.assertCheck(
            self.run_check(record=record, claimed_paths=("tmp/HL-T01/run01/log.txt",)),
            "h",
            "PASS",
        )
        self.assertCheck(
            self.run_check(record=record, claimed_paths=("docs/x.md",)), "h", "FAIL"
        )

    def test_范围匹配单元表(self) -> None:
        """分隔符感知匹配的核心判据（不依赖 git 沙盒）。"""
        cases = (
            ("dir/a.py", "dir/*.py", False, True),
            ("dir/sub/a.py", "dir/*.py", False, False),
            ("dir/a.py", "dir/**", False, True),
            ("dir/sub/a.py", "dir/**", False, True),
            ("dir", "dir/**", False, True),
            ("dir/sub/a.py", "dir/", True, True),
            ("dir", "dir/", True, True),
            ("dirx/a.py", "dir/", True, False),
            ("dir/a.py.bak", "dir/a.py", False, False),
            ("dir/a.py", "dir/a.py", False, True),
            ("a.py", "**/*.py", False, True),
            ("dir/sub/a.py", "**/*.py", False, True),
            ("dir/sub/deep.py", "dir/*/deep.py", False, True),
            ("dir/sub/x/deep.py", "dir/*/deep.py", False, False),
            # 直接传入带结尾 / 的条目等价于 subtree=True
            ("dir/a.py", "dir/", False, True),
        )
        for claimed, entry, subtree, expected in cases:
            with self.subTest(claimed=claimed, entry=entry, subtree=subtree):
                self.assertEqual(expected, checker.matches_scope(claimed, entry, subtree))

    def test_范围匹配_分隔符感知四类边界(self) -> None:
        """OBS-1 反例：`*` 不得跨段；`dir/` 子树；`**` 跨层；同前缀陷阱仍 FAIL。"""
        # 反例 1：verification/*.py 不得放行 verification/sub/deep.py（旧实现假通过）
        obs1 = self.make_record(allowed_paths=["verification/*.py"])
        self.assertCheck(
            self.run_check(record=obs1, claimed_paths=("verification/handoff_check.py",)),
            "h",
            "PASS",
        )
        check = self.assertCheck(
            self.run_check(record=obs1, claimed_paths=("verification/sub/deep.py",)),
            "h",
            "FAIL",
        )
        self.assertIn("不在允许修改范围内", check["reason"])
        # 反例 2：同一 record 下 dir/*.py 与 dir/ 子树、dir/** 跨层并存
        record = self.make_record(allowed_paths=["dir/*.py", "tree/", "deep/**"])
        self.assertCheck(
            self.run_check(record=record, claimed_paths=("dir/a.py",)), "h", "PASS"
        )
        self.assertCheck(
            self.run_check(record=record, claimed_paths=("dir/sub/a.py",)), "h", "FAIL"
        )
        self.assertCheck(
            self.run_check(record=record, claimed_paths=("tree/x/y/z.py",)), "h", "PASS"
        )
        self.assertCheck(
            self.run_check(record=record, claimed_paths=("deep/a/b/c.py",)), "h", "PASS"
        )
        # 反例 3：精确文件路径严格相等，不因前缀放行
        trap = self.make_record(allowed_paths=["dir/a.py"])
        self.assertCheck(
            self.run_check(record=trap, claimed_paths=("dir/a.py",)), "h", "PASS"
        )
        self.assertCheck(
            self.run_check(record=trap, claimed_paths=("dir/a.py.bak",)), "h", "FAIL"
        )
        self.assertCheck(
            self.run_check(record=trap, claimed_paths=("dir/a.py/inner",)), "h", "FAIL"
        )
        # 反例 4：子树以 / 结尾才算，dir/ 不得放行 dirx/
        subtree = self.make_record(allowed_paths=["dir/"])
        self.assertCheck(
            self.run_check(record=subtree, claimed_paths=("dir/sub/a.py",)), "h", "PASS"
        )
        self.assertCheck(
            self.run_check(record=subtree, claimed_paths=("dirx/a.py",)), "h", "FAIL"
        )

    def test_反斜杠与相对路径统一归一化(self) -> None:
        self.write_text("verification/handoff_check.py", "# 占位\n")
        self.write_text("verification/sub/deep.py", "# 占位\n")
        record = self.make_record(
            allowed_paths=["./verification/handoff_check.py", "verification\\sub\\"]
        )
        check = self.assertCheck(
            self.run_check(record=record, claimed_paths=(".\\verification\\handoff_check.py",)),
            "h",
            "PASS",
        )
        self.assertIn("verification/handoff_check.py", check["evidence"])
        self.assertIn("verification/sub/", check["evidence"], "子树条目应显示为 dir/ 形式")
        self.assertCheck(
            self.run_check(record=record, claimed_paths=("verification/sub/deep.py",)),
            "h",
            "PASS",
        )
        self.assertCheck(
            self.run_check(record=record, claimed_paths=("verification/sub/deep/more.py",)),
            "h",
            "PASS",
        )

    def test_目录条目未写结尾斜杠时给出提示(self) -> None:
        (self.root / "verification").mkdir()
        record = self.make_record(allowed_paths=["verification"])
        check = self.assertCheck(
            self.run_check(record=record, claimed_paths=("verification/a.py",)), "h", "FAIL"
        )
        self.assertIn("未以 / 结尾", check["reason"])
        self.assertIn("verification/", check["reason"])

    def test_FAIL_允许修改范围为空或占位(self) -> None:
        check = self.assertCheck(self.run_check(record=self.make_record(allowed_paths=[])), "h", "FAIL")
        self.assertIn("为空", check["reason"])
        self.assertCheck(
            self.run_check(record=self.make_record(allowed_paths=["待填写"])), "h", "FAIL"
        )
        record = self.make_record()
        del record["allowed_paths"]
        self.assertCheck(self.run_check(record=record), "h", "FAIL")

    def test_FAIL_证据目录缺失或没有manifest(self) -> None:
        self.assertCheck(
            self.run_check(record=self.make_record(evidence_dir="report/evidence/HL-T01/none")),
            "g",
            "FAIL",
        )
        (self.root / "report/evidence/HL-T01/run02").mkdir(parents=True)
        self.assertCheck(
            self.run_check(record=self.make_record(evidence_dir="report/evidence/HL-T01/run02")),
            "g",
            "FAIL",
        )
        self.write_text("report/evidence/HL-T01/run02/manifest.json", "{}")
        self.assertCheck(
            self.run_check(record=self.make_record(evidence_dir="report/evidence/HL-T01/run02")),
            "g",
            "PASS",
        )
        self.assertCheck(self.run_check(record=self.make_record()), "g", "SKIP")
        outside_evidence = self.run_check(
            record=self.make_record(evidence_dir=str(self.sandbox.parent / "outside-evidence"))
        )
        self.assertIn("越出工作树", self.assertCheck(outside_evidence, "g", "FAIL")["reason"])

    def test_FAIL_工作树不存在或不是git仓库(self) -> None:
        missing = self.run_check(record=None, worktree=str(self.sandbox / "no-such-dir"))
        self.assertCheck(missing, "a", "FAIL")
        self.assertCheck(missing, "b", "SKIP")
        plain = self.sandbox / "plain"
        plain.mkdir()
        # 沙盒内子目录仍在同一工作树内，不能用来构造“非仓库”场景。
        holder = tempfile.TemporaryDirectory(prefix="handoff-check-plain-")
        self.addCleanup(holder.cleanup)
        outside = Path(holder.name)
        probe = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=outside,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if probe.returncode == 0:
            self.skipTest("临时目录外层存在 git 仓库，无法构造非仓库目录")
        not_repo = self.run_check(record=None, worktree=str(outside))
        self.assertCheck(not_repo, "a", "FAIL")
        self.assertEqual(1, checker.exit_code_for(not_repo))

    def test_进程占用FAIL与不可枚举SKIP(self) -> None:
        occupied = self.run_check(record=self.make_record(), probe=vivado_running)
        check = self.assertCheck(occupied, "d", "FAIL")
        self.assertIn("vivado.exe", check["evidence"])
        self.assertEqual(1, checker.exit_code_for(occupied))
        skipped = self.run_check(record=self.make_record(), probe=probe_unavailable)
        self.assertCheck(skipped, "d", "SKIP")
        self.assertEqual(0, checker.exit_code_for(skipped))
        self.assertTrue(any("进程占用未能核验" in item for item in skipped["warnings"]))
        clean = self.run_check(record=self.make_record(), probe=no_processes)
        self.assertCheck(clean, "d", "PASS")

    def test_失联判定需三者同时成立(self) -> None:
        stale = self.make_record(heartbeat_utc8=heartbeat_text(NOW - timedelta(minutes=600)))
        lost = self.run_check(record=stale, probe=no_processes)
        self.assertTrue(lost["lost_contact"]["lost_contact"])
        with_process = self.run_check(record=stale, probe=vivado_running)
        self.assertFalse(with_process["lost_contact"]["lost_contact"])
        (self.root / ".git" / "index.lock").write_text("", encoding="utf-8")
        try:
            with_lock = self.run_check(record=stale, probe=no_processes)
        finally:
            (self.root / ".git" / "index.lock").unlink()
        self.assertFalse(with_lock["lost_contact"]["lost_contact"])
        unknown_probe = self.run_check(record=stale, probe=probe_unavailable)
        self.assertFalse(unknown_probe["lost_contact"]["lost_contact"])

    # ---------- 输入错误（退出码 2） ----------

    def test_输入错误退出码2(self) -> None:
        missing = self.run_cli("--record", str(self.sandbox / "absent.json"))
        self.assertEqual(2, missing.returncode)
        self.assertIn("record", missing.stderr)
        self.assertEqual("", missing.stdout)

        record_path = self.write_json("record.json", self.make_record())
        unknown = self.run_cli("--worktree", str(self.root), "--record", '{"status":"OFFERED","typo":1}')
        self.assertEqual(2, unknown.returncode)
        self.assertIn("未知字段", unknown.stderr)

        broken = self.run_cli("--worktree", str(self.root), "--record", "{不是 JSON}")
        self.assertEqual(2, broken.returncode)

        threshold = self.run_cli(
            "--worktree", str(self.root), "--record", str(record_path), "--max-heartbeat-minutes", "0"
        )
        self.assertEqual(2, threshold.returncode)
        self.assertIn("--max-heartbeat-minutes", threshold.stderr)

        machine = self.run_cli(
            "--json", "--record", str(self.sandbox / "absent.json")
        )
        self.assertEqual(2, machine.returncode)
        payload = json.loads(machine.stdout)
        self.assertEqual("HANDOFF_INPUT_ERROR", payload["status"])
        self.assertIn("只读核验", payload["scope_statement"])

    def test_内联JSON与中文别名(self) -> None:
        record, errors = checker.load_record(
            json.dumps(
                {
                    "任务": "HL-T01",
                    "负责人": "DSH",
                    "允许修改范围": ["verification/handoff_check.py"],
                    "心跳(UTC+8)": heartbeat_text(NOW),
                    "状态": "OFFERED",
                    "下一接手方": "Codex",
                },
                ensure_ascii=False,
            )
        )
        self.assertEqual([], errors)
        assert record is not None
        self.assertEqual("HL-T01", record["task"])
        self.assertEqual(["verification/handoff_check.py"], record["allowed_paths"])
        self.assertEqual("OFFERED", record["status"])

        conflict_record, conflict_errors = checker.load_record(
            '{"status":"OFFERED","状态":"CLAIMED"}'
        )
        self.assertIsNone(conflict_record)
        self.assertTrue(any("重复声明" in item for item in conflict_errors))

        object_errors = checker.load_record("[]")[1]
        self.assertTrue(any("顶层必须是 JSON 对象" in item for item in object_errors))

    # ---------- 只读保证 ----------

    def test_只读_无文件副作用且只调用只读git命令(self) -> None:
        self.write_text("verification/handoff_check.py", "# 占位\n")
        self.write_text("untracked.txt", "未提交内容\n")
        record = self.make_record(evidence_dir=None)
        before = {
            path.relative_to(self.root).as_posix(): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }
        git_calls: list[list[str]] = []
        real_run = subprocess.run

        def tracked_run(command, *args, **kwargs):
            if isinstance(command, (list, tuple)) and command and command[0] == "git":
                git_calls.append([str(item) for item in command])
            return real_run(command, *args, **kwargs)

        with patch.object(checker.subprocess, "run", side_effect=tracked_run):
            result = self.run_check(record=record)
        after = {
            path.relative_to(self.root).as_posix(): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }
        self.assertEqual("HANDOFF_OK", result["status"], result["checks"])
        self.assertEqual(before, after, "检查器不得写入或删除工作树内的文件")

        self.assertTrue(git_calls, "检查器应通过只读 git 命令取证")
        for command in git_calls:
            self.assertIn("--no-optional-locks", command, command)
            self.assertTrue({"rev-parse", "status"} & set(command), command)
            self.assertFalse(
                FORBIDDEN_GIT_VERBS & set(command),
                f"出现写操作动词：{command}",
            )

    def test_JSON输出为单行且可解析(self) -> None:
        # 走真实 CLI + 真实墙钟：心跳必须由当前时间生成，否则超过 120 分钟阈值后
        # e 会同 d 一起 FAIL，本用例将随墙钟永久变红（BLOCKING-1）。
        record_path = self.write_json("record.json", self.live_record())
        completed = self.run_cli(
            "--json",
            "--worktree",
            str(self.root),
            "--record",
            str(record_path),
            "--claimed-path",
            "verification/handoff_check.py",
        )
        self.assertEqual(1, len(completed.stdout.strip().splitlines()))
        payload = json.loads(completed.stdout)
        self.assertEqual(
            ["a", "b", "c", "d", "e", "f", "g", "h", "i"],
            [check["id"] for check in payload["checks"]],
        )
        statuses = {check["id"]: check["status"] for check in payload["checks"]}
        # 新鲜心跳在任何墙钟时间都必须 PASS。
        self.assertEqual("PASS", statuses["e"], payload["checks"])
        # CLI 使用真实进程探针：本机若正跑 Vivado/xsim/hw_server，只有 d 允许为 FAIL。
        failing = [check["id"] for check in payload["checks"] if check["status"] == "FAIL"]
        self.assertIn(failing, ([], ["d"]), payload["checks"])
        self.assertEqual(1 if failing else 0, completed.returncode)
        self.assertEqual(
            "HANDOFF_FAILED" if failing else "HANDOFF_OK", payload["status"]
        )
        self.assertIn("只读核验", payload["scope_statement"])

    # ---------- 时间无关守护 ----------

    def test_时间无关_新鲜心跳必须PASS(self) -> None:
        """真实墙钟 + 动态心跳：e 必须 PASS，与是否跑着重型进程无关。"""
        record_path = self.write_json("record_fresh.json", self.live_record())
        completed = self.run_cli(
            "--json", "--worktree", str(self.root), "--record", str(record_path)
        )
        payload = json.loads(completed.stdout)
        statuses = {check["id"]: check["status"] for check in payload["checks"]}
        self.assertEqual("PASS", statuses["e"], payload["checks"])

    def test_时间无关_过期心跳必须FAIL(self) -> None:
        """守护用例：过期心跳在任何墙钟下都必须 FAIL，防止修复削弱 e 检查。"""
        # 注入时刻下确定性核验
        stale_injected = self.make_record(
            heartbeat_utc8=heartbeat_text(NOW - timedelta(minutes=300))
        )
        check = self.assertCheck(self.run_check(record=stale_injected), "e", "FAIL")
        self.assertIn("心跳超过 120 分钟阈值", check["reason"])

        # 真实墙钟下走 CLI：心跳取 4 小时前，任意时间运行都必然过期
        stale_live = self.make_record(
            heartbeat_utc8=heartbeat_text(live_now() - timedelta(minutes=240))
        )
        record_path = self.write_json("record_stale.json", stale_live)
        completed = self.run_cli(
            "--json", "--worktree", str(self.root), "--record", str(record_path)
        )
        payload = json.loads(completed.stdout)
        statuses = {check["id"]: check["status"] for check in payload["checks"]}
        self.assertEqual("FAIL", statuses["e"], payload["checks"])
        failing = [check["id"] for check in payload["checks"] if check["status"] == "FAIL"]
        self.assertIn("e", failing, payload["checks"])
        self.assertEqual(1, completed.returncode, payload["checks"])

    def test_时间无关_用例不依赖固定日历字面量(self) -> None:
        """审计守护：测试源码不得再出现固定日历心跳（BLOCKING-1 同类缺陷）。

        注入式固定时刻 `NOW` 不属此类：它只作为 `now=` 参数使用，与真实墙钟无关。
        正则模式本身不含可自匹配的完整片段，避免守护用例自匹配。
        """
        source = Path(__file__).read_text(encoding="utf-8")
        patterns = (
            re.compile(r'heartbeat_utc8"\s*:\s*"\d{4}-\d{2}-\d{2}'),
            re.compile(r'heartbeat_utc8="\d{4}-\d{2}-\d{2}'),
            re.compile(r'心跳\(UTC\+8\)"\s*:\s*"\d{4}-\d{2}-\d{2}'),
        )
        for pattern in patterns:
            self.assertIsNone(
                pattern.search(source), f"发现固定日历心跳：{pattern.pattern}"
            )


if __name__ == "__main__":
    unittest.main()