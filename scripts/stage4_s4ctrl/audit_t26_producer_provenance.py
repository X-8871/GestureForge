#!/usr/bin/env python3
"""task-26 阻断项只读身份审计（S4-T26-PRODUCER-AUDIT）。

不生成黄金、不改算法、不访问硬件。只回答三件事：
1. activation report 记录的 producer（darknet.exe 与 hook 源）字节能否在现有副本中复现；
2. 固定路径上的构建产物是否在报告生成之后被改写（后写覆盖 → 原始 producer 不可复现）；
3. 黄金链的每个绑定文件在“工作区原始字节”和“Git 归一化字节”两种口径下的 SHA 是否与
   各记录声明一致；两种口径不一致即为绑定歧义，必须显式登记。

判定原则（fail-closed）：只有全部 producer 字节可复现、全部绑定无歧义、且被审报告与冻结 SHA
一致时才返回 0；任一不成立返回 1 并逐条列出未闭合原因；输入或环境错误（含报告被改写、
证据目录非法、文件缺失）返回 2。绑定审计为强制项，**不提供跳过开关**，避免靠开关变绿。
脚本绝不把“看起来一致”当成一致，也绝不改写被审文件或被审记录。

退出码：0 = 全部可复现且绑定无歧义；1 = 存在未闭合阻断（预期常态）；2 = 输入/环境错误。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
CN = timezone(timedelta(hours=8))
SCHEMA = "s4t26_producer_audit_v1"

# 默认审计对象：activation report 与其记录的 fixed-path producer。
DEFAULT_ACTIVATION_REPORT = (
    WORKTREE / "report/evidence/S1-T02/20260922_s1_t02_d2_tiny416_activation_calibration_r1.json"
)
# 被审报告的冻结 SHA-256：防止用“重写过的报告”自证关闭（B1 不得由被审方自行改写）。
DEFAULT_EXPECTED_REPORT_SHA256 = (
    "6d73283c698a94dd30cf00634de59fb76a8e889916eb4d00e50b76c245687216"
)
# 候选副本枚举根（只读遍历，不进入 report/ 之外的写入）。
DEFAULT_SEARCH_ROOTS = (Path("D:/FPGA_Data"),)
DEFAULT_EXE_NAME = "darknet.exe"
DEFAULT_HOOK_NAME = "network_kernels.cu"

# 黄金链绑定：路径 → 记录中声明值（来源见各记录，脚本不解释、只比对）。
DEFAULT_BINDINGS = (
    {
        "id": "s2a_t29_cpu_decode_nms_reference",
        "path": "report/evidence/S2A-T29/cpu_decode_nms_reference.json",
        "expected_sha256": "24361a13e262d1774ae255195dac3b05df4c16b9c287ff06945f2d630d3a0231",
        "expected_source": "docs/stage4/s4a_stage4_g0_fields.json upstream_bindings[s2a_t29_cpu_decode_nms_reference]",
    },
    {
        "id": "t29_reference_as_cited_by_rebind_manifest",
        "path": "report/evidence/S2A-T29/cpu_decode_nms_reference.json",
        "expected_sha256": "26392c8d7f5ca8643a26c149411c66d6f2343a544f8c4f03d32584dc4e071d33",
        "expected_source": "report/evidence/S4-CTRL/s4t26_golden_rebind_20261026_r02/golden_materialization_manifest.json frozen_sources.t29_reference",
    },
    {
        "id": "s2a_t25_cpu_layer_golden_index",
        "path": "report/evidence/S2A-T25/cpu_layer_golden_index.json",
        "expected_sha256": "2d76f9e284130c96374de6ea3525e0c92778b0f701c8894cd4d127234c8d3c72",
        "expected_source": "report/evidence/S4-CTRL/s4t26_golden_rebind_20261026_r02/golden_materialization_manifest.json frozen_sources.t25_index",
    },
)


def sha256_bytes(data: bytes) -> str:
    """对给定字节计算 SHA-256。"""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """按 1 MiB 分块计算文件 SHA-256（不对字节做任何归一化）。"""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """拒绝重复键：重复键会以后值覆盖前值，可被用来掩盖真实值。"""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"JSON 含重复键：{key}")
        result[key] = value
    return result


def write_json_atomic(out_dir: Path, name: str, payload: dict[str, object]) -> None:
    """先把内容编码成字节，再建目录并原子落盘；编码失败不会留下 0 字节残文件。"""
    data = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / f".{name}.tmp"
    tmp.write_bytes(data)
    os.replace(tmp, out_dir / name)


def sha256_file_normalized(path: Path) -> str:
    """把 CRLF 归一化为 LF 后再算 SHA-256（对齐 Git 的 eol 归一化口径）。"""
    return sha256_bytes(path.read_bytes().replace(b"\r\n", b"\n"))


def git(args: list[str]) -> subprocess.CompletedProcess:
    """只读 Git 调用；一律带 --no-optional-locks。"""
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(WORKTREE), *args],
        capture_output=True,
    )


def git_blob_sha256(rel_path: str) -> dict[str, object]:
    """取 HEAD 中该路径的 blob 字节并计算 SHA-256（不存在则如实返回）。"""
    proc = git(["show", f"HEAD:{rel_path}"])
    if proc.returncode != 0:
        return {"path": rel_path, "available": False,
                "detail": proc.stderr.decode("utf-8", "replace").strip()[:300]}
    return {"path": rel_path, "available": True, "bytes": len(proc.stdout),
            "sha256": sha256_bytes(proc.stdout)}


def file_mtime(path: Path) -> datetime:
    """取文件修改时间（统一换算为 UTC+8 的带时区时间，秒级）。"""
    return datetime.fromtimestamp(path.stat().st_mtime, tz=CN).replace(microsecond=0)


def parse_time(text: str) -> datetime | None:
    """解析 ISO8601 时间；失败返回 None。"""
    try:
        return datetime.fromisoformat(text)
    except (TypeError, ValueError):
        return None


def enumerate_candidates(roots: tuple[Path, ...], name: str, max_depth: int) -> list[Path]:
    """在各根目录下按文件名枚举候选副本（只读遍历，深度受限）。"""
    found: list[Path] = []
    lowered = name.lower()
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            try:
                rel_depth = len(path.relative_to(root).parts)
            except ValueError:
                continue
            if rel_depth > max_depth:
                continue
            if path.is_file() and path.name.lower() == lowered:
                found.append(path)
    return sorted(found)


def audit_producer(report: dict[str, object], roots: tuple[Path, ...], max_depth: int) -> dict[str, object]:
    """审计 activation report 声明的两个 producer 字节可复现性。"""
    inputs = report.get("inputs", {}) if isinstance(report.get("inputs"), dict) else {}
    generated_at = parse_time(str(report.get("generated_at_utc8", "")))

    results: dict[str, object] = {}
    for key, recorded_path_key, recorded_sha_key, filename in (
        ("darknet_executable", "darknet_executable", "darknet_executable_sha256", DEFAULT_EXE_NAME),
        ("activation_hook_source", "activation_hook_source", "activation_hook_source_sha256", DEFAULT_HOOK_NAME),
    ):
        recorded_path = inputs.get(recorded_path_key)
        recorded_sha = inputs.get(recorded_sha_key)
        entry: dict[str, object] = {
            "recorded_path": recorded_path,
            "recorded_sha256": recorded_sha,
        }
        if not isinstance(recorded_path, str) or not isinstance(recorded_sha, str):
            entry.update({"status": "INPUT_MISSING", "fixed_path_exists": False,
                          "reproduced": False,
                          "detail": "activation report 未记录该 producer 的路径或 SHA"})
            results[key] = entry
            continue

        fixed = Path(recorded_path)
        entry["fixed_path_exists"] = fixed.is_file()
        if fixed.is_file():
            actual = sha256_file(fixed)
            mtime = file_mtime(fixed)
            entry.update({
                "fixed_path_actual_sha256": actual,
                "fixed_path_bytes": fixed.stat().st_size,
                "fixed_path_mtime_utc8": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                "fixed_path_matches_recorded": actual == recorded_sha.lower(),
            })
            if generated_at is not None:
                delta = (mtime - generated_at).total_seconds()
                entry["fixed_path_written_after_report"] = delta > 0
                entry["fixed_path_mtime_minus_report_seconds"] = round(delta, 1)
        else:
            entry["fixed_path_actual_sha256"] = None
            entry["fixed_path_matches_recorded"] = False
            entry["fixed_path_written_after_report"] = None
            entry["fixed_path_mtime_minus_report_seconds"] = None

        candidates = []
        reproduced_by: list[str] = []
        for cand in enumerate_candidates(roots, filename, max_depth):
            cand_sha = sha256_file(cand)
            matched = cand_sha == recorded_sha.lower()
            candidates.append({
                "path": str(cand),
                "bytes": cand.stat().st_size,
                "sha256": cand_sha,
                "matches_recorded": matched,
                "mtime_utc8": file_mtime(cand).strftime("%Y-%m-%d %H:%M:%S"),
            })
            if matched:
                reproduced_by.append(str(cand))
            if len(candidates) >= 40:  # 只记录到 40 个，防爆量
                break
        entry["candidate_count"] = len(candidates)
        entry["candidates"] = candidates
        entry["reproduced_by"] = reproduced_by
        entry["reproduced"] = bool(reproduced_by) or bool(entry.get("fixed_path_matches_recorded"))
        entry["status"] = "REPRODUCED" if entry["reproduced"] else "UNRECOVERABLE"
        if not entry["reproduced"]:
            entry["detail"] = (
                "记录的 SHA 在固定路径与全部候选副本中均无字节匹配；"
                "原始 producer 字节未保留，无法用现有文件重建该身份"
            )
        results[key] = entry
    return results


def audit_tool(report: dict[str, object]) -> dict[str, object]:
    """核对报告记录的生产工具 SHA 是否与当前工具文件一致。"""
    tool = report.get("tool", {}) if isinstance(report.get("tool"), dict) else {}
    path_text = tool.get("path")
    recorded = tool.get("sha256")
    if not isinstance(path_text, str) or not isinstance(recorded, str):
        return {"status": "INPUT_MISSING", "detail": "报告未记录 tool.path/tool.sha256"}
    path = Path(path_text)
    if not path.is_file():
        return {"status": "TOOL_MISSING", "recorded_path": path_text, "recorded_sha256": recorded}
    actual = sha256_file(path)
    normalized = sha256_file_normalized(path)
    return {
        "recorded_path": path_text,
        "recorded_sha256": recorded,
        "actual_sha256": actual,
        "actual_sha256_crlf_normalized": normalized,
        "match": actual == recorded.lower(),
        "status": "MATCH" if actual == recorded.lower() else "MISMATCH",
        "byte_basis": (
            "raw" if actual == recorded.lower()
            else ("crlf_normalized" if normalized == recorded.lower() else "none")
        ),
        "interpretation": (
            "生产工具的 SHA 与记录一致 ⇒ 报告内的 producer SHA 是运行期由 sha256_file 计算的"
            "实测值，而不是事后手填；因此 producer 不一致只能由文件被后写解释，不能归因于抄录错误"
        ),
    }


def audit_bindings(bindings: tuple[dict[str, str], ...]) -> list[dict[str, object]]:
    """核对绑定文件在两种字节口径下的 SHA 与记录声明。"""
    rows: list[dict[str, object]] = []
    for item in bindings:
        rel = item["path"]
        expected = item["expected_sha256"].lower()
        path = WORKTREE / rel
        row: dict[str, object] = {
            "id": item["id"],
            "path": rel,
            "expected_sha256": expected,
            "expected_source": item.get("expected_source"),
        }
        if path.is_file():
            raw = path.read_bytes()
            raw_sha = sha256_bytes(raw)
            norm_sha = sha256_bytes(raw.replace(b"\r\n", b"\n"))
            row.update({
                "exists": True,
                "raw_bytes": len(raw),
                "raw_sha256": raw_sha,
                "normalized_bytes": len(raw.replace(b"\r\n", b"\n")),
                "normalized_sha256": norm_sha,
                "crlf_count": raw.count(b"\r\n"),
                "raw_matches_expected": raw_sha == expected,
                "normalized_matches_expected": norm_sha == expected,
            })
        else:
            row.update({"exists": False, "raw_sha256": None,
                        "normalized_sha256": None,
                        "raw_matches_expected": False,
                        "normalized_matches_expected": False})
        row["git_blob_at_head"] = git_blob_sha256(rel)
        blob = row["git_blob_at_head"]
        row["git_blob_matches_expected"] = bool(
            isinstance(blob, dict) and blob.get("available") and blob.get("sha256") == expected
        )
        row["byte_basis_ambiguous"] = bool(
            row.get("raw_sha256") and row.get("normalized_sha256")
            and row["raw_sha256"] != row["normalized_sha256"]
        )
        if row["raw_matches_expected"]:
            row["status"] = "MATCH_RAW_BASIS"
        elif row["normalized_matches_expected"]:
            row["status"] = "MATCH_NORMALIZED_BASIS"
        else:
            row["status"] = "NO_MATCH"
        rows.append(row)
    return rows


def main() -> int:
    """执行审计并按 fail-closed 规则给出退出码。"""
    parser = argparse.ArgumentParser(description="task-26 阻断项只读身份审计")
    parser.add_argument("--evidence-dir", required=True,
                        help="新 RunId 证据目录（相对工作树或绝对路径）；必须不存在或为空")
    parser.add_argument("--activation-report", default=str(DEFAULT_ACTIVATION_REPORT))
    parser.add_argument("--search-root", action="append", default=[],
                        help="候选副本枚举根，可重复；默认 D:/FPGA_Data")
    parser.add_argument("--max-depth", type=int, default=8)
    parser.add_argument("--expect-report-sha256", default=DEFAULT_EXPECTED_REPORT_SHA256,
                        help="被审 activation report 的冻结 SHA-256；不一致即视为输入错误（exit 2）")
    parser.add_argument("--allow-repin", action="store_true",
                        help="显式允许用与内置冻结常量不同的 --expect-report-sha256（换钉需具名承认）")
    args = parser.parse_args()

    report_path = Path(args.activation_report)
    if not report_path.is_file():
        print(f"[ERROR] activation report 不存在：{report_path}")
        return 2
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"),
                            object_pairs_hook=reject_duplicate_keys)
    except Exception:  # 解析/编码/递归过深一律视为输入错误
        print(f"[ERROR] activation report 解析失败或结构非法：{report_path}")
        return 2
    if not isinstance(report, dict):
        print("[ERROR] activation report 顶层结构不是对象，按输入错误处理")
        return 2

    # 先钉死被审对象：报告字节必须等于冻结值，避免“重写报告自证关闭”。
    expected_report_sha = (args.expect_report_sha256 or "").strip().lower()
    if not expected_report_sha:
        print("[ERROR] 必须提供 --expect-report-sha256，禁止审计未钉死的报告")
        return 2
    if expected_report_sha != DEFAULT_EXPECTED_REPORT_SHA256 and not args.allow_repin:
        print("[ERROR] --expect-report-sha256 与内置冻结常量不同；换钉须显式加 --allow-repin")
        return 2
    report_raw_sha = sha256_file(report_path)
    if report_raw_sha != expected_report_sha:
        print(f"[ERROR] 被审报告与冻结值不一致：expected={expected_report_sha} actual={report_raw_sha}")
        return 2

    out_dir = Path(args.evidence_dir)
    if not out_dir.is_absolute():
        out_dir = WORKTREE / out_dir
    if out_dir.exists():
        if not out_dir.is_dir():
            print(f"[ERROR] 证据目录路径已存在且不是目录：{out_dir}")
            return 2
        if any(out_dir.iterdir()):
            print(f"[ERROR] 证据目录非空，拒绝复用 RunId：{out_dir}")
            return 2

    roots = tuple(Path(p) for p in (args.search_root or [str(r) for r in DEFAULT_SEARCH_ROOTS]))
    producers = audit_producer(report, roots, args.max_depth)
    tool = audit_tool(report)
    # 绑定审计为强制项，不提供跳过开关：绑定口径歧义属未闭合阻断，不能靠开关变绿。
    bindings = audit_bindings(DEFAULT_BINDINGS)

    problems: list[str] = []
    for key, entry in producers.items():
        if not entry.get("reproduced"):
            problems.append(
                f"{key}: 记录的 SHA 不可复现（recorded={entry.get('recorded_sha256')}，"
                f"fixed_path_actual={entry.get('fixed_path_actual_sha256')}，候选副本 "
                f"{entry.get('candidate_count')} 个均无匹配）"
            )
        if entry.get("fixed_path_written_after_report"):
            problems.append(
                f"{key}: 固定路径 mtime({entry.get('fixed_path_mtime_utc8')}) 晚于报告生成时间 "
                f"{entry.get('fixed_path_mtime_minus_report_seconds')} 秒 ⇒ 该路径在报告后被改写"
            )
    if tool.get("status") != "MATCH":
        problems.append(f"producer tool: 状态 {tool.get('status')}，与记录不一致")
    # 报告时间必须落在 [工具 mtime, 现在] 之间，防止用未来时间戳绕过后写判定。
    report_time = parse_time(str(report.get("generated_at_utc8", "")))
    tool_path_text = (report.get("tool", {}) or {}).get("path")
    if report_time is None:
        problems.append("activation report: generated_at_utc8 无法解析，不能作为时间旁证")
    else:
        if report_time.tzinfo is None:
            report_time = report_time.replace(tzinfo=CN)
        if report_time > datetime.now(CN):
            problems.append(
                f"activation report: generated_at_utc8({report.get('generated_at_utc8')}) 晚于当前时间"
                " ⇒ 报告可能被改写"
            )
        if isinstance(tool_path_text, str) and Path(tool_path_text).is_file():
            tool_mtime = file_mtime(Path(tool_path_text))
            if report_time < tool_mtime:
                problems.append(
                    f"activation report: generated_at_utc8 早于生产工具 mtime({tool_mtime:%Y-%m-%d %H:%M:%S})"
                    " ⇒ 时间线不自洽"
                )
    for row in bindings:
        if row["status"] == "NO_MATCH":
            problems.append(f"binding[{row['id']}]: 两种字节口径均不等于声明值 {row['expected_sha256']}")
        elif row["byte_basis_ambiguous"]:
            problems.append(
                f"binding[{row['id']}]: 原始字节与归一化字节 SHA 不同"
                f"（raw={row['raw_sha256']} normalized={row['normalized_sha256']}），"
                f"声明值命中 {row['status']} ⇒ 绑定字节口径必须显式声明，否则跨记录比对会误判"
            )

    facts: dict[str, object] = {
        "schema_version": SCHEMA,
        "task_id": "S4-T26-PRODUCER-AUDIT",
        "run_id": out_dir.name,
        "checker": "scripts/stage4_s4ctrl/audit_t26_producer_provenance.py",
        "checker_sha256": sha256_file(Path(__file__).resolve()),
        "generated_utc8": datetime.now(CN).isoformat(timespec="seconds"),
        "worktree": str(WORKTREE),
        "activation_report": {
            "path": str(report_path),
            "raw_sha256": report_raw_sha,
            "normalized_sha256": sha256_file_normalized(report_path),
            "expected_sha256": expected_report_sha,
            "pinned_matches": report_raw_sha == expected_report_sha,
            "generated_at_utc8": report.get("generated_at_utc8"),
            "status_field": report.get("status"),
            "darknet_source_commit": (report.get("inputs", {}) or {}).get("darknet_source_commit"),
        },
        "producers": producers,
        "producer_tool": tool,
        "binding_audit": "MANDATORY（无跳过开关）",
        "bindings": bindings,
        "search_roots": [str(r) for r in roots],
        "search_max_depth": args.max_depth,
        "unclosed": problems,
        "verdict": "PASS" if not problems else "BLOCKED",
        "interpretation_boundary": [
            "本审计只核对字节身份，不判断浮点/量化算法正确性，不生成黄金，不改算法。",
            "SHA 不可复现 ≠ 记录造假：报告 SHA 由 sha256_file 在运行期计算；本审计只陈述可从现有文件验证的部分。",
            "mtime 先后是覆盖时点的旁证，不是文件内容来源的证明。",
            "不构成 G0/G1/G3/G4/G5 或实物验收结论；ENABLE=0 与 task-26 BLOCKED 不变。",
        ],
    }

    exit_code = 0 if not problems else 1
    facts["exit_code"] = exit_code
    # 先编码、再建目录、原子落盘：编码失败不会留下 0 字节结论文件。
    write_json_atomic(out_dir, "audit.json", facts)

    files = []
    for path in sorted(out_dir.iterdir()):
        if path.is_file() and path.name != "manifest.json":
            files.append({"path": path.name, "bytes": path.stat().st_size,
                          "sha256": sha256_file(path)})
    manifest = {
        "schema_version": 1,
        "task_id": "S4-T26-PRODUCER-AUDIT",
        "run_id": out_dir.name,
        "generated_utc8": facts["generated_utc8"],
        "verdict": facts["verdict"],
        "exit_code": exit_code,
        "files": files,
        "scope": "只读身份审计；不含算法改动、黄金生成或硬件操作",
    }
    write_json_atomic(out_dir, "manifest.json", manifest)

    print(f"[{facts['verdict']}] exit={exit_code} 未闭合项={len(problems)}")
    for line in problems:
        print(f"  - {line}")
    return exit_code


if __name__ == "__main__":
    # 任何未预期异常（含递归过深、编码失败）都归为输入/环境错误（exit 2），不得伪装成 1。
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - 顶层兜底，必须区分于“未闭合”
        print(f"[ERROR] 输入或环境错误：{type(exc).__name__}: {exc}")
        sys.exit(2)
