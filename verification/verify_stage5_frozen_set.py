#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""阶段5 **离线范围冻结集**校验器（S5-T04）——只读、fail-closed。

角色
====
把「阶段5 离线范围」当前冻结的字节集合（契约/规格、离线实现、离线证据包、以及必要的
宿主侧上游引用）在**任意时刻重算并逐件比对**，用于：
- 冻结后的自证（同一提交单独检出/git archive 导出后仍能逐件复现）；
- 后续轮次的漂移检测（本校验器不看"最新文件"，只看冻结集里登记的哈希）。

退出码（fail-closed，异常绝不伪装通过）
=====================================
- `0`：全部成员逐件一致，打印 `FROZEN_SET_VERIFIED`；
- `1`：存在**内容不一致**（哈希/目录摘要/文件数不符 ⇒ 视为篡改或漂移）；
- `2`：**输入或环境错误**：冻结集缺失/不可解析/结构非法、成员缺失/不可读/不是普通文件、
  路径越界、未知 kind、或任何未预期异常。**这种情况绝不返回 0。**

只读承诺：本脚本不写工作树、不修改任何证据目录；`--selftest` 只在指定的临时目录内造副本。

用法
====
    python -B verification/verify_stage5_frozen_set.py \
        [--root <repo>] [--frozen-set <json>] [--json-out <path>] [--skip-host-references]
    python -B verification/verify_stage5_frozen_set.py --selftest <tmpdir> [--selftest-members 3]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_FROZEN_SET = ("report/evidence/S5-T04/s5_freeze_20261027_r01/frozen_set.json")
KINDS = ("file", "dir_digest")
SCOPES = ("repo", "host")
EXIT_VERIFIED = 0
EXIT_MISMATCH = 1
EXIT_ENV_ERROR = 2


class FrozenSetError(Exception):
    """冻结集本身非法（输入错误 ⇒ exit 2）。"""


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def dir_digest(path: pathlib.Path) -> tuple[str, int]:
    """目录摘要：按相对路径排序，对 `rel\\0sha256\\0bytes\\n` 逐行拼接后取 SHA-256。"""
    lines = []
    count = 0
    for entry in sorted(path.rglob("*")):
        if entry.is_dir():
            continue
        if not entry.is_file():
            raise FrozenSetError(f"目录内存在非普通文件：{entry}")
        relative = entry.relative_to(path).as_posix()
        lines.append(f"{relative}\0{sha256_file(entry)}\0{entry.stat().st_size}\n")
        count += 1
    return hashlib.sha256("".join(lines).encode("utf-8")).hexdigest(), count


def load_frozen_set(path: pathlib.Path) -> dict:
    if not path.is_file():
        raise FrozenSetError(f"冻结集不存在：{path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise FrozenSetError(f"冻结集不可解析：{error}") from error
    if not isinstance(data, dict):
        raise FrozenSetError("冻结集顶层必须是对象")
    members = data.get("members")
    if not isinstance(members, list) or not members:
        raise FrozenSetError("冻结集必须包含非空 members 数组")
    return data


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FrozenSetError(message)


def verify(root: pathlib.Path, frozen_set_path: pathlib.Path,
           skip_host: bool = False) -> dict:
    """逐件复算；返回结果字典（含 status/exit_code/逐项明细）。"""
    data = load_frozen_set(frozen_set_path)
    items: list[dict] = []
    mismatches: list[str] = []
    errors: list[str] = []
    skipped: list[str] = []

    for index, member in enumerate(data["members"]):
        label = f"members[{index}]"
        try:
            _require(isinstance(member, dict), f"{label} 必须是对象")
            member_id = member.get("id")
            _require(isinstance(member_id, str) and member_id, f"{label}.id 必须是非空字符串")
            kind = member.get("kind")
            _require(kind in KINDS, f"{label}.kind 必须是 {KINDS}")
            scope = member.get("scope", "repo")
            _require(scope in SCOPES, f"{label}.scope 必须是 {SCOPES}")
            raw_path = member.get("path")
            _require(isinstance(raw_path, str) and raw_path, f"{label}.path 必须是非空字符串")
        except FrozenSetError as error:
            errors.append(str(error))
            items.append({"id": member.get("id", f"#{index}"), "status": "ENV_ERROR",
                          "detail": str(error)})
            continue

        if scope == "host" and skip_host:
            skipped.append(member_id)
            items.append({"id": member_id, "status": "SKIPPED_HOST_REFERENCE",
                          "detail": raw_path})
            continue

        try:
            candidate = pathlib.Path(raw_path)
            resolved = candidate if (scope == "host" and candidate.is_absolute()) else (root / candidate)
            resolved = pathlib.Path(resolved)
            if not resolved.exists():
                raise FrozenSetError(f"{member_id}: 成员缺失：{resolved}")
            if not resolved.is_file() and not resolved.is_dir():
                raise FrozenSetError(f"{member_id}: 成员不是普通文件/目录：{resolved}")

            if kind == "file":
                if not resolved.is_file():
                    raise FrozenSetError(f"{member_id}: 登记为 file 但实际不是普通文件：{resolved}")
                expected = member.get("sha256")
                _require(isinstance(expected, str) and len(expected) == 64,
                         f"{member_id}: sha256 必须是 64 位十六进制")
                actual = sha256_file(resolved)
                if actual == expected:
                    items.append({"id": member_id, "status": "MATCH", "sha256": actual,
                                  "scope": scope, "path": str(resolved)})
                else:
                    mismatches.append(member_id)
                    items.append({"id": member_id, "status": "MISMATCH", "expected": expected,
                                  "actual": actual, "scope": scope, "path": str(resolved)})
            else:
                if not resolved.is_dir():
                    raise FrozenSetError(f"{member_id}: 登记为 dir_digest 但实际不是目录：{resolved}")
                expected_digest = member.get("digest_sha256")
                _require(isinstance(expected_digest, str) and len(expected_digest) == 64,
                         f"{member_id}: digest_sha256 必须是 64 位十六进制")
                actual_digest, actual_count = dir_digest(resolved)
                expected_count = member.get("file_count")
                count_ok = (expected_count is None) or (int(expected_count) == actual_count)
                if actual_digest == expected_digest and count_ok:
                    items.append({"id": member_id, "status": "MATCH", "digest_sha256": actual_digest,
                                  "file_count": actual_count, "scope": scope, "path": str(resolved)})
                else:
                    mismatches.append(member_id)
                    items.append({"id": member_id, "status": "MISMATCH",
                                  "expected": expected_digest, "actual": actual_digest,
                                  "expected_file_count": expected_count,
                                  "actual_file_count": actual_count,
                                  "scope": scope, "path": str(resolved)})
        except FrozenSetError as error:
            errors.append(str(error))
            items.append({"id": member_id, "status": "ENV_ERROR", "detail": str(error)})
        except (OSError, ValueError) as error:                      # 读不到/权限/其它环境问题
            errors.append(f"{member_id}: {error}")
            items.append({"id": member_id, "status": "ENV_ERROR", "detail": str(error)})

    if errors:
        status, exit_code = "FROZEN_SET_ENV_ERROR", EXIT_ENV_ERROR
    elif mismatches:
        status, exit_code = "FROZEN_SET_MISMATCH", EXIT_MISMATCH
    else:
        status, exit_code = "FROZEN_SET_VERIFIED", EXIT_VERIFIED

    return {
        "status": status,
        "exit_code": exit_code,
        "root": str(root),
        "frozen_set": str(frozen_set_path),
        "frozen_set_id": data.get("frozen_set_id"),
        "baseline_commit": data.get("baseline_commit"),
        "totals": {"members": len(data["members"]), "matched": sum(1 for i in items if i["status"] == "MATCH"),
                   "mismatched": len(mismatches), "env_errors": len(errors), "skipped_host": len(skipped)},
        "mismatches": mismatches,
        "errors": errors,
        "skipped_host_references": skipped,
        "items": items,
    }


def run_selftest(workdir: pathlib.Path, member_limit: int,
                 source: pathlib.Path | None = None) -> dict:
    """注入自测：真实进程级调用本校验器，要求 clean=0 / 篡改=1 / 缺件=2。"""
    workdir = pathlib.Path(workdir)
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True)

    source = pathlib.Path(source) if source else (REPO_ROOT / DEFAULT_FROZEN_SET)
    data = load_frozen_set(source)
    file_members = [m for m in data["members"]
                    if m.get("kind") == "file" and m.get("scope", "repo") == "repo"]
    if len(file_members) < member_limit:
        raise FrozenSetError(f"冻结集内 repo 文件成员不足 {member_limit} 个，无法做注入自测")
    chosen = file_members[:member_limit]
    reduced = {"frozen_set_id": data.get("frozen_set_id", "") + "__selftest_subset",
               "baseline_commit": data.get("baseline_commit"),
               "note": "注入自测用的缩减冻结集（只含前若干 repo 文件成员）",
               "members": []}
    for member in chosen:
        target = workdir / member["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / member["path"], target)
        reduced["members"].append({"id": member["id"], "kind": "file", "scope": "repo",
                                   "path": member["path"], "sha256": member["sha256"]})
    frozen_path = workdir / "frozen_set.json"
    frozen_path.write_text(json.dumps(reduced, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def invoke() -> dict:
        completed = subprocess.run([sys.executable, "-B", str(pathlib.Path(__file__).resolve()),
                                    "--root", str(workdir), "--frozen-set", str(frozen_path),
                                    "--skip-host-references"],
                                   capture_output=True, text=True, encoding="utf-8", errors="replace")
        return {"exit_code": completed.returncode, "stdout_tail": completed.stdout.strip().splitlines()[-1:]}

    steps = {"clean": invoke()}

    tampered = workdir / chosen[0]["path"]
    blob = bytearray(tampered.read_bytes())
    blob[0] = blob[0] ^ 0xFF if blob else 0x00
    if not blob:
        blob = bytearray(b"\x00")
    tampered.write_bytes(bytes(blob))
    steps["tampered_one_byte"] = invoke()

    missing = workdir / chosen[1]["path"]
    missing.unlink()
    steps["deleted_one_member"] = invoke()

    expectations = {"clean": EXIT_VERIFIED, "tampered_one_byte": EXIT_MISMATCH,
                    "deleted_one_member": EXIT_ENV_ERROR}
    checks = [{"step": name, "expected_exit": expectations[name],
               "observed_exit": steps[name]["exit_code"],
               "pass": steps[name]["exit_code"] == expectations[name]}
              for name in ("clean", "tampered_one_byte", "deleted_one_member")]
    return {"workdir": str(workdir), "member_limit": member_limit,
            "steps": steps, "checks": checks,
            "verdict": "SELFTEST_PASS" if all(c["pass"] for c in checks) else "SELFTEST_FAIL",
            "exit_code": EXIT_VERIFIED if all(c["pass"] for c in checks) else EXIT_MISMATCH}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(REPO_ROOT))
    parser.add_argument("--frozen-set", default="")
    parser.add_argument("--json-out", default="")
    parser.add_argument("--skip-host-references", action="store_true")
    parser.add_argument("--selftest", default="")
    parser.add_argument("--selftest-members", type=int, default=3)
    args = parser.parse_args(argv)

    root = pathlib.Path(args.root)
    if not root.is_dir():
        print(f"[ENV_ERROR] --root 不是目录：{root}", file=sys.stderr)
        return EXIT_ENV_ERROR

    if args.selftest:
        source = pathlib.Path(args.frozen_set) if args.frozen_set else root / DEFAULT_FROZEN_SET
        try:
            result = run_selftest(pathlib.Path(args.selftest), args.selftest_members, source)
        except FrozenSetError as error:
            print(f"[ENV_ERROR] 注入自测无法进行：{error}", file=sys.stderr)
            return EXIT_ENV_ERROR
        payload = json.dumps(result, ensure_ascii=False, indent=2)
        if args.json_out:
            pathlib.Path(args.json_out).write_text(payload + "\n", encoding="utf-8")
        print(payload)
        return int(result["exit_code"])

    frozen_path = pathlib.Path(args.frozen_set) if args.frozen_set else root / DEFAULT_FROZEN_SET
    try:
        result = verify(root, frozen_path, skip_host=args.skip_host_references)
    except FrozenSetError as error:
        print(f"[ENV_ERROR] {error}", file=sys.stderr)
        return EXIT_ENV_ERROR
    except Exception as error:                                    # 兜底：绝不伪装通过
        print(f"[ENV_ERROR] 未预期异常：{type(error).__name__}: {error}", file=sys.stderr)
        return EXIT_ENV_ERROR

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_out:
        pathlib.Path(args.json_out).write_text(payload + "\n", encoding="utf-8")
    for item in result["items"]:
        detail = item.get("sha256") or item.get("digest_sha256") or item.get("detail") or ""
        print(f"{item['status']:<28} {item['id']:<46} {detail}")
    print(json.dumps({k: result[k] for k in
                      ("status", "exit_code", "totals", "mismatches", "errors")},
                     ensure_ascii=False))
    if result["exit_code"] == EXIT_VERIFIED:
        print("FROZEN_SET_VERIFIED")
    elif result["exit_code"] == EXIT_MISMATCH:
        print("FROZEN_SET_MISMATCH")
    else:
        print("FROZEN_SET_ENV_ERROR")
    return int(result["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())