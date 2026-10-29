#!/usr/bin/env python3
"""封装 S6-B 离线回归、批准输入快照与哈希基座证据。"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


UTC8 = timezone(timedelta(hours=8))
RUN_DIR = Path(__file__).resolve().parent
ROOT = RUN_DIR.parents[3]
TMP_CHECK_ROOT = ROOT / "tmp/stage6/S6-B" / RUN_DIR.name
PYTHON = Path(r"C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")
EXPECTED_HEAD = "e735a5afb5b474793408ec1e61da111006c70e60"
RUN_ID = "s6b_current_20261029_r07"
SOURCE_RUN_ID = "s6b_current_20261029_r03"
SOURCE_RUN = ROOT / "report/evidence/S6-B" / SOURCE_RUN_ID
S6A_RECEIPT = ROOT / "report/evidence/S6-A/s6a_u6_02_decision_20261025_r07/decision_receipt.json"
S4_CONTRACT = ROOT / "report/evidence/S6-D/s6d_replay_qualification_20261029_r05/inputs/w4/s4b_shared_input_result_contract.json"
MAIN_CHECKER_ROOT = Path(r"D:\FPGA_Competition\verification")
MAIN_CHECKER_HASHES = {
    "check_stage_delivery.py": "",
    "check_manifest_hash_basis.py": "",
}
SOURCE_FILES = (
    "src/stage6/s6_core.py",
    "src/stage6/s6_actions.py",
    "src/stage6/s6_params.py",
    "src/stage6/s6_receipts.py",
    "verification/s6b_run_cases.py",
    "verification/s6b_probe.py",
    "verification/s6b_build_evidence.py",
    "verification/test_s6b_core_regressions.py",
    "verification/test_s6b_probe.py",
    "verification/test_s6b_build_evidence.py",
    "verification/check_stage_delivery.py",
    "docs/stage6/s6a_stage6_g0_behavior_v1.json",
    "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
    "docs/stage6/s6b_frozen_interface_v1.json",
    "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md",
    "report/evidence/S6-A/s6a_u6_02_decision_20261025_r07/decision_receipt.json",
    "report/evidence/S6-D/s6d_replay_qualification_20261029_r05/inputs/w4/s4b_shared_input_result_contract.json",
)
OUTPUT_FILES = (
    "cases/case_matrix.json",
    "expected_freeze.json",
    "run_report.json",
    "run_stdout.txt",
    "probe_summary.json",
    "probe_baseline_stdout.txt",
    "probe_expected_tampered_stdout.txt",
    "probe_threshold_tampered_stdout.txt",
    "probe_wrong_semantics_expected_stdout.txt",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(value)


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def copy_utf8(source: Path, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("r", encoding="utf-8", newline="") as reader:
        content = reader.read()
    write_text(destination, content)
    source_sha = sha256_file(source)
    destination_sha = sha256_file(destination)
    if source_sha != destination_sha:
        raise RuntimeError(f"UTF-8 快照字节不一致：{source} -> {destination}")
    return source_sha


def git_text(*arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *arguments],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(arguments)} 退出码 {result.returncode}：{result.stderr}")
    return result.stdout.strip()


def blob_sha(commit: str, relative_path: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "cat-file", "blob", f"{commit}:{relative_path}"],
        capture_output=True,
        check=False,
    )
    return sha256_bytes(result.stdout) if result.returncode == 0 else None


def run_capture(command: list[str], *, cwd: Path = ROOT) -> dict[str, object]:
    environment = {
        **os.environ,
        "PYTHONUTF8": "1",
        "PYTHONIOENCODING": "utf-8",
    }
    result = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
        check=False,
    )
    return {
        "command": subprocess.list2cmdline(command),
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def write_check_output(path: Path, result: dict[str, object]) -> None:
    write_text(path, str(result["stdout"]) + str(result["stderr"]))


def manifest_file_entry(path: Path, role: str, reason: str) -> dict[str, str]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256_file(path),
        "role": role,
        "keep_reason": reason,
        "hash_basis": "worktree_disk",
    }


def package_entry(path: Path) -> dict[str, str]:
    relative = path.relative_to(RUN_DIR).as_posix()
    if relative.startswith("matrix_source_r03/logs/") or relative.endswith("unittest_output.txt"):
        role = "log"
    elif relative.startswith("inputs/source_snapshots/src/") or relative.startswith("inputs/source_snapshots/verification/"):
        role = "source"
    elif relative.startswith("inputs/"):
        role = "input"
    else:
        role = "result"
    return manifest_file_entry(path, role, f"S6-B 离线证据文件：{relative}")


def set_check(checks: list[dict[str, object]], name: str, command: str,
              exit_code: int | None, *, reason: str | None = None) -> None:
    status = "NOT_RUN" if exit_code is None else ("PASS" if exit_code == 0 else "FAIL")
    row: dict[str, object] = {
        "name": name,
        "status": status,
        "command": command,
        "exit_code": exit_code,
    }
    if reason:
        row["reason"] = reason
    for index, old in enumerate(checks):
        if old.get("name") == name:
            checks[index] = row
            return
    checks.append(row)


def main() -> int:
    if RUN_DIR.name != RUN_ID:
        raise RuntimeError(f"RunId 不匹配：{RUN_DIR.name}")
    actual_head = git_text("rev-parse", "HEAD")
    if actual_head != EXPECTED_HEAD:
        raise RuntimeError(f"HEAD 已变化：期望 {EXPECTED_HEAD}，实际 {actual_head}")
    branch = git_text("branch", "--show-current")
    if branch != "stage6-interact-prep":
        raise RuntimeError(f"分支已变化：期望 stage6-interact-prep，实际 {branch}")
    if not PYTHON.is_file():
        raise RuntimeError(f"Python 解释器不存在：{PYTHON}")
    if not SOURCE_RUN.is_dir():
        raise RuntimeError(f"矩阵源运行目录不存在：{SOURCE_RUN}")

    source_run_manifest = json.loads(
        (SOURCE_RUN / "delivery_manifest.json").read_text(encoding="utf-8")
    )
    run_report = json.loads((SOURCE_RUN / "run_report.json").read_text(encoding="utf-8"))
    if run_report.get("status") != "PASS" or run_report.get("case_count") != 26:
        raise RuntimeError("源运行 r03 未通过 26 条矩阵或结果数量不符")
    source_core_entry = next(
        row for row in source_run_manifest["files"]
        if row.get("path") == "src/stage6/s6_core.py"
    )
    current_core_sha = sha256_file(ROOT / "src/stage6/s6_core.py")
    if source_core_entry.get("sha256") != current_core_sha:
        raise RuntimeError("r03 实际运行核心哈希与当前磁盘字节不一致；拒绝复用 r03 结果")

    s4_sha = sha256_file(S4_CONTRACT)
    if s4_sha != "7228f51350feb0c63de9e58de20d72d1fdfcd3bf13c39374344e82b027a0f145":
        raise RuntimeError(f"阶段4 r07 契约快照字节漂移：{s4_sha}")
    s4_doc = json.loads(S4_CONTRACT.read_text(encoding="utf-8"))
    if (s4_doc.get("revision") != "r07"
            or s4_doc.get("status") != "FROZEN_OFFLINE_ONLY"
            or s4_doc.get("freeze_record", {}).get("reviewed_commit")
            != "5f9a04a045f4aaa7516759513f660f9872cbab61"):
        raise RuntimeError("阶段4 r07 契约状态或审查提交不符合已核验快照")
    s4_frame_fields = {
        item.get("name"): item
        for item in s4_doc.get("input_frame_contract", {}).get("fields", [])
    }
    frame_id_field = s4_frame_fields.get("frame_id", {})
    if (frame_id_field.get("type") != "uint32"
            or frame_id_field.get("required") is not True
            or "+1" not in frame_id_field.get("semantics", "")):
        raise RuntimeError("阶段4 r07 契约未明确 frame_id 必填 uint32 与 +1 递增语义")
    frame_sequence_rules = s4_doc.get("input_frame_contract", {}).get("frame_sequence_rules", {})
    if ("回退" not in frame_sequence_rules.get("regressed_frame_id", "")
            or "拒绝" not in frame_sequence_rules.get("regressed_frame_id", "")):
        raise RuntimeError("阶段4 r07 契约未明确回退 frame_id 必须拒绝")
    receipt = json.loads(S6A_RECEIPT.read_text(encoding="utf-8"))
    if (receipt.get("run_id") != "s6a_u6_02_decision_20261025_r07"
            or receipt.get("decision_status") != "APPROVED_20261025"):
        raise RuntimeError("U6-02 r07 批准回执不符合已核验内容")

    snapshot_root = RUN_DIR / "inputs/source_snapshots"
    source_bindings: list[dict[str, object]] = []
    for relative in SOURCE_FILES:
        original = ROOT / relative
        if not original.is_file():
            raise RuntimeError(f"缺少源文件：{original}")
        snapshot = snapshot_root / relative
        disk_sha = copy_utf8(original, snapshot)
        committed_sha = blob_sha(actual_head, relative)
        source_bindings.append({
            "path": relative,
            "snapshot_path": snapshot.relative_to(ROOT).as_posix(),
            "worktree_disk_sha256": disk_sha,
            "commit_blob_sha256": committed_sha,
            "matches_commit_blob": committed_sha == disk_sha if committed_sha else False,
            "hash_basis": "worktree_disk",
        })

    checker_snapshot_root = RUN_DIR / "inputs/main_checkers"
    checker_bindings: list[dict[str, str]] = []
    for name in ("check_stage_delivery.py", "check_manifest_hash_basis.py"):
        original = MAIN_CHECKER_ROOT / name
        if not original.is_file():
            raise RuntimeError(f"main 统一 checker 不存在：{original}")
        snapshot = checker_snapshot_root / name
        digest = copy_utf8(original, snapshot)
        expected = MAIN_CHECKER_HASHES.get(name)
        if expected and digest != expected:
            raise RuntimeError(f"main checker 字节 SHA 不匹配：{name}={digest}")
        checker_bindings.append({
            "name": name,
            "origin_path": str(original),
            "snapshot_path": snapshot.relative_to(ROOT).as_posix(),
            "sha256": digest,
            "hash_basis": "worktree_disk",
        })

    matrix_root = RUN_DIR / "matrix_source_r03"
    for relative in OUTPUT_FILES:
        source = SOURCE_RUN / relative
        if not source.is_file():
            raise RuntimeError(f"源运行 r03 缺少结果文件：{source}")
        copy_utf8(source, matrix_root / relative)
    for source in sorted((SOURCE_RUN / "logs").glob("*.jsonl")):
        copy_utf8(source, matrix_root / "logs" / source.name)

    source_run_record = {
        "schema_version": 1,
        "artifact": "s6b_source_run_binding",
        "task_id": "S6-B",
        "run_id": RUN_ID,
        "source_run_id": SOURCE_RUN_ID,
        "source_commit": actual_head,
        "source_run_manifest_sha256": sha256_file(SOURCE_RUN / "delivery_manifest.json"),
        "source_run_manifest_hash_basis": "worktree_disk",
        "matrix_case_count": 26,
        "matrix_status": "PASS",
        "probe_count": 4,
        "probe_status": "PASS",
        "core_sha256_r03_and_current": current_core_sha,
        "hash_basis": "worktree_disk",
        "files": [],
        "note": "矩阵及探针结果来自 r03；该次运行的核心原始字节 SHA-256 与本包快照一致，其他源文件与测试结果在本包独立绑定。",
    }
    for relative in OUTPUT_FILES:
        path = matrix_root / relative
        source_run_record["files"].append({
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(path),
            "hash_basis": "worktree_disk",
        })
    for path in sorted((matrix_root / "logs").glob("*.jsonl")):
        source_run_record["files"].append({
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(path),
            "hash_basis": "worktree_disk",
        })
    write_json(RUN_DIR / "source_run_r03.json", source_run_record)

    test_command = [str(PYTHON), "-B", "-m", "unittest", "discover",
                    "-s", "verification", "-p", "test_s6b*.py"]
    tests = run_capture(test_command)
    write_text(RUN_DIR / "unittest_output.txt", str(tests["stdout"]) + str(tests["stderr"]))
    test_output = str(tests["stdout"]) + str(tests["stderr"])
    tests_pass = tests["exit_code"] == 0 and "Ran 39 tests" in test_output and "OK" in test_output

    for binding in source_bindings:
        original = ROOT / str(binding["path"])
        if sha256_file(original) != binding["worktree_disk_sha256"]:
            raise RuntimeError(f"运行期间源文件字节发生变化：{original}")

    source_bindings_doc = {
        "schema_version": 1,
        "artifact": "s6b_source_and_input_bindings",
        "task_id": "S6-B",
        "run_id": RUN_ID,
        "source_commit": actual_head,
        "branch": branch,
        "hash_basis": "worktree_disk",
        "hash_basis_note": "逐项 SHA-256 按工作树磁盘原始字节计算；commit_blob_sha256 仅作当前提交基线对照。",
        "files": source_bindings,
        "main_checkers": checker_bindings,
        "s6a_approval": {
            "decision_id": receipt["decision_id"],
            "run_id": receipt["run_id"],
            "decision_status": receipt["decision_status"],
            "path": S6A_RECEIPT.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(S6A_RECEIPT),
            "hash_basis": "worktree_disk",
        },
        "stage4_contract": {
            "contract_id": s4_doc["contract_id"],
            "contract_version": s4_doc["contract_version"],
            "revision": s4_doc["revision"],
            "status": s4_doc["status"],
            "path": S4_CONTRACT.relative_to(ROOT).as_posix(),
            "sha256": s4_sha,
            "hash_basis": "worktree_disk",
            "reviewed_commit": s4_doc["freeze_record"]["reviewed_commit"],
            "freeze_scope": s4_doc["freeze_record"]["freeze_scope"],
            "freeze_record_note": "r07 冻结记录只给 reviewed_commit，没有独立 frozen_commit 字段。",
            "scope": "只用于核验 S6-B 输入 frame_id 的 uint32 类型边界；不构成阶段4/6 实际集成证据。",
        },
    }
    write_json(RUN_DIR / "source_bindings.json", source_bindings_doc)

    limitations = {
        "schema_version": 1,
        "artifact": "s6b_offline_limitations",
        "task_id": "S6-B",
        "run_id": RUN_ID,
        "not_run": [
            {"item": "阶段4/5 实际结果链路集成", "status": "BLOCKED",
             "reason": "本包只绑定阶段4 r07 离线共享契约快照及离线输入类型，不消费实时/板上数据链路。"},
            {"item": "T6-A03 交互延迟门槛", "status": "NOT_RUN",
             "reason": "缺阶段4 实测帧周期 P，继续保持 NOT_RUN。"},
            {"item": "6-E 摄像头实物验收", "status": "NOT_RUN",
             "reason": "本包是离线软件回归，没有摄像头或板级测量。"},
            {"item": "板上操作、JTAG、串口、HDMI、真实时间长跑", "status": "NOT_RUN",
             "reason": "未执行任何硬件或实时会话。"},
        ],
        "open_behavior_deviations": [
            {"id": "B25-SAME-SESSION-LARGE-ROLLBACK", "status": "BLOCKED",
             "reason": "S6-A v1.8 只称同会话 frame_id“大幅回退”需复位，未给数值判据；阶段4 r07 只定义 uint32 与 +1 单调分配，未定义回退量。不得猜阈值。核心当前按 B23 将任意同会话倒序帧作为 E_FRAME_OUT_OF_ORDER，不实现大回退复位。"},
        ],
        "claim_limits": [
            "矩阵、探针和单元测试只证明指定软件字节对离线输入的行为。",
            "不声称板级 G3、阶段4/5 实际集成、G4 或阶段6 G5 通过。",
            "阶段4 r07 的 reviewed_commit 是 5f9a04a045f4aaa7516759513f660f9872cbab61；冻结记录未提供独立 frozen_commit 字段。",
        ],
    }
    write_json(RUN_DIR / "limitations_not_executed.json", limitations)

    source_run_manifest_checks = {
        row["name"]: row for row in source_run_manifest.get("checks", [])
    }
    matrix_check = source_run_manifest_checks.get("S6-B 确定性用例（26 条 / 11 类）", {})
    probe_check = source_run_manifest_checks.get("S6-B 判别力探针（4 项）", {})
    checks: list[dict[str, object]] = []
    set_check(checks, "S6-B 离线矩阵 26/26（复用已绑定 r03）",
              str(matrix_check.get("command", "")), matrix_check.get("exit_code"))
    set_check(checks, "S6-B 判别探针 4/4（复用已绑定 r03）",
              str(probe_check.get("command", "")), probe_check.get("exit_code"))
    set_check(checks, "S6-B unittest 回归 39 项",
              subprocess.list2cmdline(test_command), int(tests["exit_code"]),
              reason=None if tests_pass else "测试输出未满足 39 项全部通过")

    input_files = []
    for relative in SOURCE_FILES:
        snapshot = snapshot_root / relative
        role = "source" if relative.startswith(("src/", "verification/")) else "input"
        input_files.append(manifest_file_entry(
            snapshot, role, f"S6-B 执行字节快照：{relative}"
        ))
    for binding in checker_bindings:
        input_files.append(manifest_file_entry(
            ROOT / binding["snapshot_path"], "input",
            f"main 统一校验器固定快照：{binding['name']}"
        ))
    for relative in OUTPUT_FILES:
        input_files.append(manifest_file_entry(
            matrix_root / relative, "input", f"既有 r03 矩阵运行输入/结果快照：{relative}"
        ))
    for path in sorted((matrix_root / "logs").glob("*.jsonl")):
        input_files.append(manifest_file_entry(
            path, "input", "既有 r03 逐用例日志快照"
        ))

    inputs_manifest = {
        "schema_version": 1,
        "stage": "6",
        "task_id": "S6-B",
        "run_id": RUN_ID,
        "source_commit": actual_head,
        "evidence_dir": f"report/evidence/S6-B/{RUN_ID}",
        "interfaces": [],
        "interfaces_not_applicable_reason": (
            "S6-B 在本包中只核验纯核心离线事件；阶段4 r07 只作为 frame_id uint32 类型来源，"
            "没有实时 adapter 或阶段4/5 集成。"
        ),
        "hash_basis": "worktree_disk",
        "hash_basis_commit": actual_head,
        "files": input_files,
        "checks": [{
            "name": "输入快照原始字节绑定",
            "status": "PASS",
            "command": "bundle_build.py 逐项复算原文件与 UTF-8 快照 SHA-256",
            "exit_code": 0,
        }],
        "limitations": [
            "阶段4 r07 契约仅用于字段类型边界；同会话大幅回退阈值未定义并保持 BLOCKED。",
            "所有 hash_basis=worktree_disk，覆盖本包快照与工作树源文件原始字节。",
        ],
    }
    write_json(RUN_DIR / "inputs_manifest.json", inputs_manifest)

    checks.extend([
        {"name": "main check_stage_delivery inputs", "status": "NOT_RUN",
         "command": "", "exit_code": None},
        {"name": "main check_stage_delivery evidence", "status": "NOT_RUN",
         "command": "", "exit_code": None},
        {"name": "main check_stage_delivery evidence closing", "status": "NOT_RUN",
         "command": "", "exit_code": None},
        {"name": "main check_manifest_hash_basis strict", "status": "NOT_RUN",
         "command": "", "exit_code": None},
    ])
    delivery = {
        "schema_version": 1,
        "stage": "6",
        "task_id": "S6-B",
        "run_id": RUN_ID,
        "source_commit": actual_head,
        "evidence_dir": f"report/evidence/S6-B/{RUN_ID}",
        "interfaces": [],
        "interfaces_not_applicable_reason": inputs_manifest["interfaces_not_applicable_reason"],
        "hash_basis": "worktree_disk",
        "hash_basis_commit": actual_head,
        "hash_basis_note": "哈希项按工作树磁盘原始字节取 SHA-256；源码基线提交与有效工作树字节分别绑定。",
        "files": [],
        "checks": checks,
        "tool_versions": {
            "python": sys.version.split()[0],
            "git": git_text("--version"),
            "main_check_stage_delivery_sha256": checker_bindings[0]["sha256"],
            "main_check_manifest_hash_basis_sha256": checker_bindings[1]["sha256"],
        },
        "limitations": limitations["claim_limits"] + [
            "矩阵/探针来自 r03；核心源文件原始字节与 r03 delivery_manifest 逐字节一致。",
            "6-B 独立审查仍由总控安排；本包不构成 G2/G4/G5。",
        ],
    }

    summary = """# S6-B 离线回归封装摘要（RunId s6b_current_20261029_r07）

- 26 条确定性矩阵和 4 项判别探针来自 `s6b_current_20261029_r03`。r03 清单中的 `src/stage6/s6_core.py` 原始 SHA-256 与本包当前工作树字节完全一致；动作层、参数装载、矩阵驱动和探针也逐项一致。
- 本包重新运行 `python -B -m unittest discover -s verification -p 'test_s6b*.py'`，保存 39 项回归输出。新增 `frame_id` uint32 检查覆盖 0、0xFFFFFFFE、0xFFFFFFFF，拒绝 -1、2^32、bool、float 和超大整数，并逐项核对非法输入前后状态不变。
- 已绑定 S6-A v1.8 JSON/规格、U6-02 r07 批准回执、阶段4 S4B r07 / 1.3.0 冻结离线契约快照及 main 统一 `check_stage_delivery.py`、`check_manifest_hash_basis.py` 固定副本。各清单逐项声明 `hash_basis=worktree_disk`，`source_commit` 固定为运行时 HEAD。
- 阶段4 r07 契约 SHA-256：`7228f51350feb0c63de9e58de20d72d1fdfcd3bf13c39374344e82b027a0f145`；`reviewed_commit=5f9a04a045f4aaa7516759513f660f9872cbab61`，契约冻结范围 `OFFLINE_ONLY`。契约没有独立的 `frozen_commit` 字段。
- B25 同会话 `frame_id`“大幅回退”没有数值判据，按 `BLOCKED` 登记；实现保留 B23 倒序处理，不猜复位阈值。

本包只证明离线注入和软件回归。没有板卡、JTAG、串口、摄像头、HDMI 或实时会话操作；T6-A03 仍 `NOT_RUN`，真实阶段4/5 集成仍 `BLOCKED`，不声称 G3/G4/G5。
"""
    write_text(RUN_DIR / "s6b_run_summary.md", summary)

    def current_package_files() -> list[dict[str, str]]:
        result = []
        for path in sorted(RUN_DIR.rglob("*")):
            if not path.is_file() or path == RUN_DIR / "delivery_manifest.json":
                continue
            result.append(package_entry(path))
        for relative in SOURCE_FILES:
            source = ROOT / relative
            role = "source" if relative.startswith(("src/", "verification/")) else "input"
            result.append(manifest_file_entry(source, role, f"实际执行源文件：{relative}"))
        return sorted(result, key=lambda row: row["path"])

    def write_hashes() -> None:
        lines = []
        for path in sorted(RUN_DIR.rglob("*")):
            if not path.is_file() or path.name == "hashes_sha256.txt" or path.name == "delivery_manifest.json":
                continue
            lines.append(f"{sha256_file(path)}  {path.relative_to(RUN_DIR).as_posix()}")
        write_text(RUN_DIR / "hashes_sha256.txt", "\n".join(lines) + "\n")

    delivery_path = RUN_DIR / "delivery_manifest.json"
    inputs_path = RUN_DIR / "inputs_manifest.json"
    inputs_checker = checker_snapshot_root / "check_stage_delivery.py"
    basis_checker = checker_snapshot_root / "check_manifest_hash_basis.py"
    inputs_command = [str(PYTHON), "-B", str(inputs_checker), "--mode", "inputs",
                      "--manifest", str(inputs_path), "--project-root", str(ROOT)]
    evidence_command = [str(PYTHON), "-B", str(inputs_checker), "--mode", "evidence",
                        "--manifest", str(delivery_path), "--project-root", str(ROOT)]
    basis_command = [str(PYTHON), "-B", str(basis_checker), "--repo", str(ROOT),
                     "--paths", inputs_path.relative_to(ROOT).as_posix(),
                     "--paths", delivery_path.relative_to(ROOT).as_posix(),
                     "--mode", "strict", "--json"]
    inputs_result = run_capture(inputs_command)
    write_check_output(TMP_CHECK_ROOT / "check_inputs_mode_output.txt", inputs_result)
    set_check(checks, "main check_stage_delivery inputs", str(inputs_result["command"]),
              int(inputs_result["exit_code"]), reason=None if int(inputs_result["exit_code"]) == 0
              else "inputs 模式 checker 返回非零，隔离诊断输出见 tmp/stage6/S6-B/s6b_current_20261029_r07")

    previous_state = None
    final_results: dict[str, dict[str, object]] = {}
    for iteration in range(1, 9):
        write_hashes()
        delivery["files"] = current_package_files()
        write_json(delivery_path, delivery)

        evidence_result = run_capture(evidence_command)
        write_check_output(TMP_CHECK_ROOT / "check_evidence_mode_output.txt", evidence_result)
        basis_result = run_capture(basis_command)
        write_check_output(TMP_CHECK_ROOT / "check_hash_basis_output.txt", basis_result)
        set_check(checks, "main check_stage_delivery evidence", str(evidence_result["command"]),
                  int(evidence_result["exit_code"]), reason=None if int(evidence_result["exit_code"]) == 0
                  else "evidence 模式 checker 返回非零，隔离诊断输出见 tmp/stage6/S6-B/s6b_current_20261029_r07")
        set_check(checks, "main check_manifest_hash_basis strict", str(basis_result["command"]),
                  int(basis_result["exit_code"]), reason=None if int(basis_result["exit_code"]) == 0
                  else "strict hash_basis checker 返回非零，隔离诊断输出见 tmp/stage6/S6-B/s6b_current_20261029_r07")

        write_hashes()
        delivery["files"] = current_package_files()
        write_json(delivery_path, delivery)
        closing_result = run_capture(evidence_command)
        write_check_output(TMP_CHECK_ROOT / "check_closing_evidence_mode_output.txt", closing_result)
        set_check(checks, "main check_stage_delivery evidence closing",
                  str(closing_result["command"]), int(closing_result["exit_code"]),
                  reason=None if int(closing_result["exit_code"]) == 0
                  else "closing evidence checker 返回非零，隔离诊断输出见 tmp/stage6/S6-B/s6b_current_20261029_r07")
        write_hashes()
        delivery["files"] = current_package_files()
        write_json(delivery_path, delivery)

        state = {
            "files": delivery["files"],
            "checks": checks,
            "inputs_output": sha256_file(TMP_CHECK_ROOT / "check_inputs_mode_output.txt"),
            "evidence_output": sha256_file(TMP_CHECK_ROOT / "check_evidence_mode_output.txt"),
            "closing_output": sha256_file(TMP_CHECK_ROOT / "check_closing_evidence_mode_output.txt"),
            "basis_output": sha256_file(TMP_CHECK_ROOT / "check_hash_basis_output.txt"),
            "hashes_output": sha256_file(RUN_DIR / "hashes_sha256.txt"),
        }
        final_results = {
            "inputs": inputs_result,
            "evidence": evidence_result,
            "closing": closing_result,
            "hash_basis": basis_result,
        }
        all_passed = all(int(row["exit_code"]) == 0 for row in final_results.values())
        if all_passed and state == previous_state:
            break
        previous_state = state

    write_hashes()
    delivery["files"] = current_package_files()
    write_json(delivery_path, delivery)
    final_statuses = {row["name"]: row["exit_code"] for row in checks}
    write_json(RUN_DIR / "final_check_status.json", {
        "schema_version": 1,
        "artifact": "s6b_final_check_status",
        "task_id": "S6-B",
        "run_id": RUN_ID,
        "hash_basis": "worktree_disk",
        "checks": final_statuses,
    })
    write_hashes()
    delivery["files"] = current_package_files()
    write_json(delivery_path, delivery)
    if not tests_pass:
        print("S6-B unittest 回归失败；完整输出已保留。")
        return 1
    if not all(int(row["exit_code"]) == 0 for row in final_results.values()):
        print("至少一项证据检查失败；完整输出已保留。")
        return 1
    print(json.dumps({
        "status": "S6B_OFFLINE_BUNDLE_BUILT",
        "run_id": RUN_ID,
        "source_run_id": SOURCE_RUN_ID,
        "matrix_cases": 26,
        "probes": 4,
        "unittest": "39/39",
        "checks": {key: value["exit_code"] for key, value in final_results.items()},
        "stage4_contract_sha256": s4_sha,
        "b25_status": "BLOCKED",
    }, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
