#!/usr/bin/env python3
"""固化并只读核验 R08 manifest 引用的临时输入字节。"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

R08_REL = "report/evidence/S6-D/s6d_replay_no_hand_20261027_r08"
R10_REL = "report/evidence/S6-D/s6d_replay_no_hand_20261027_r10"
R10_RUN_ID = "s6d_replay_no_hand_20261027_r10"
R08_RUN_ID = "s6d_replay_no_hand_20261027_r08"
RECOVERY_REL = f"{R10_REL}/recovery_manifest.json"
SUMMARY_REL = f"{R10_REL}/summary.md"
SCRIPT_REL = f"{R10_REL}/recover_r08_tmp_inputs.py"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON 顶层必须是对象：{path}")
    return value


def safe_rel_path(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"路径必须是非空 POSIX 相对路径：{value!r}")
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if posix.is_absolute() or windows.is_absolute() or ".." in posix.parts:
        raise ValueError(f"拒绝绝对路径或父目录遍历：{value!r}")
    if any(part in {"", "."} for part in posix.parts):
        raise ValueError(f"拒绝非规范路径：{value!r}")
    return posix


def project_path(root: Path, relative: str) -> Path:
    parts = safe_rel_path(relative).parts
    base = root.resolve()
    candidate = base.joinpath(*parts)
    resolved = candidate.resolve(strict=False)
    if not resolved.is_relative_to(base):
        raise ValueError(f"路径解析越出项目根：{relative}")
    return resolved


def require_file(root: Path, relative: str, expected_sha: str | None = None) -> dict[str, Any]:
    path = project_path(root, relative)
    if not path.is_file() or path.is_symlink():
        raise FileNotFoundError(f"需要普通文件且不能是符号链接：{relative}")
    actual_sha = sha256_file(path)
    if expected_sha is not None and actual_sha != expected_sha:
        raise ValueError(f"文件 SHA-256 漂移：{relative}，期望 {expected_sha}，实际 {actual_sha}")
    return {"path": relative, "sha256": actual_sha, "bytes": path.stat().st_size}


def git_output(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失败：{result.stderr.strip()}")
    return result.stdout.strip()


def run_tool(command: list[str], cwd: Path) -> dict[str, Any]:
    result = subprocess.run(
        command, cwd=str(cwd), capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False,
    )
    return {
        "command": subprocess.list2cmdline(command),
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def now_utc8() -> str:
    zone = timezone(timedelta(hours=8))
    return datetime.now(zone).isoformat(timespec="seconds")


def corrected_keep_reason(path: str) -> str:
    name = PurePosixPath(path).name
    if path == "tmp/6/s6d_r05_attempt_evidence/prior_attempt_record.json":
        return "R05 启动尝试记录：执行器副本占用了目标证据目录，预检拒绝既有 RunId；外层退出 1、子进程退出 2，核心未调用。"
    if path == "tmp/6/s6d_r05_attempt_evidence/runner_output.txt":
        return "R05 预检子进程原始 stdout：记录 RunId 已存在并拒绝覆盖。"
    if path == "tmp/6/s6d_r05_attempt_evidence/runner_exit_code.txt":
        return "R05 预检子进程实际退出码 2；不是阶段6核心执行结果。"
    if path == "tmp/6/s6d_r05_attempt_evidence/positive_replay_audit_output.txt":
        return "R05 初版阳性审计 stderr：当时把 CRLF 工作树字节 SHA 与 Git raw blob SHA 直接比较而误报；后续 R08 采用双哈希口径复核通过，此日志仅保留失败历史。"
    if path == "tmp/6/s6d_r05_attempt_evidence/positive_replay_audit_exit_code.txt":
        return "R05 初版阳性审计实际退出码 2；原因见同轮 stderr，不能作为上游文件损坏结论。"
    if path == "tmp/6/s6d_r06_attempt_evidence/attempt_record.json":
        return "R06 上游审计失败记录：旧检查器把当前 W5 磁盘测试文件与 pinned commit blob 要求相等；固定提交 blob 实际与 S5 清单一致，R06 在创建证据目录前退出，核心未调用。"
    if path == "tmp/6/s6d_r08_runtime/preflight_runtime.py":
        return "R08 实际预检器字节；用于复核 R08 上游绑定命令、冻结源文件哈希和 fail-closed 逻辑。"
    if path == "tmp/6/s6d_r08_runtime/runner_runtime.py":
        return "R08 实际运行包装器字节；用于复核执行命令、子进程退出码收集和清单生成。"
    if path == "tmp/6/s6d_r08_runtime/positive_replay_audit.py":
        return "R08 实际只读阳性回放绑定审计器字节；用于复核 W4/W5 哈希和阳性帧时间资格判定。"
    if "/s6d_replay_no_hand_20261027_r07/" in path:
        if name == "preflight_result.json":
            return "R07 预检结果：上游绑定与定向单测通过；NO_HAND stale=null 使输入 BLOCKED，核心 NOT_RUN。"
        if name == "inputs_manifest.json":
            return "R07 输入清单原件：该轮最终 inputs checker 曾因 PASS 检查缺 command 字段而失败；原件保留供追溯。"
        if name == "delivery_manifest.json":
            return "R07 交付清单原件：该轮最终 checker 曾因 FAIL 缺 reason、PASS 缺 command 字段而失败；原件保留供追溯。"
        if name == "check_inputs_mode_output.txt":
            return "R07 inputs checker 原始输出：记录 checks[2] 为 PASS 时 command 为空的结构错误。"
        if name == "check_evidence_mode_output.txt":
            return "R07 evidence checker 原始输出：记录 inputs FAIL 缺 reason 及前序 PASS 缺 command 的结构错误。"
        if name == "runner_exit_code.txt":
            return "R07 预检子进程实际退出码 2（因 stale=null fail-closed）；外层清单封装失败另见 checker 输出。"
        if name == "runner_output.txt":
            return "R07 预检子进程 stdout：记录上游审计、单测及初始清单检查结果；不等同于外层最终 checker 结果。"
        return "R07 前序执行及清单失败追溯文件；具体失败原因见 recovery_manifest.json 对应记录。"
    if path.startswith(f"{R08_REL}/"):
        return "R08 正式证据原件；其状态和哈希由 R08 原始清单绑定，本 R10 仅提供恢复副本和映射。"
    return f"R08 清单所引用的原始输入：{name}；保持原 SHA，并由 R10 recovery_manifest.json 映射。"


def collect_r08_sources(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, dict[str, Any]]]:
    r08_dir = project_path(root, R08_REL)
    inputs_rel = f"{R08_REL}/inputs_manifest.json"
    delivery_rel = f"{R08_REL}/delivery_manifest.json"
    result_rel = f"{R08_REL}/preflight_result.json"
    inputs = read_json(project_path(root, inputs_rel))
    delivery = read_json(project_path(root, delivery_rel))
    result = read_json(project_path(root, result_rel))
    if (inputs.get("run_id") != R08_RUN_ID or delivery.get("run_id") != R08_RUN_ID
            or result.get("run_id") != R08_RUN_ID):
        raise ValueError("R08 运行身份字段不一致")
    if result.get("status") != "BLOCKED" or result.get("core_execution", {}).get("status") != "NOT_RUN":
        raise ValueError("R08 原始 BLOCKED/NOT_RUN 结论已变化；拒绝打包")
    runner = result.get("runner_process", {})
    if runner.get("exit_code") != 2:
        raise ValueError("R08 预检子进程实际退出码不再是已记录的 2")
    sidecar_rel = f"{R08_REL}/runner_exit_code.txt"
    sidecar = project_path(root, sidecar_rel).read_text(encoding="utf-8").strip()
    if sidecar != "2":
        raise ValueError(f"R08 runner_exit_code sidecar 与结果不一致：{sidecar!r}")

    records: dict[str, dict[str, Any]] = {}
    for manifest_name, document in (("inputs_manifest.json", inputs), ("delivery_manifest.json", delivery)):
        for record in document.get("files", []):
            path = record.get("path")
            if not isinstance(path, str):
                raise ValueError(f"{manifest_name} 含无效文件路径")
            safe_rel_path(path)
            if path.startswith("tmp/") and not path.startswith("tmp/6/"):
                raise ValueError(f"R08 临时引用不属于限定 tmp/6 子树：{path}")
            actual = require_file(root, path, record.get("sha256"))
            if path not in records:
                records[path] = {
                    "original_path": path,
                    "sha256": actual["sha256"],
                    "bytes": actual["bytes"],
                    "manifest_records": [],
                }
            elif records[path]["sha256"] != actual["sha256"]:
                raise ValueError(f"相同路径在 R08 两清单中的 SHA 不一致：{path}")
            records[path]["manifest_records"].append({
                "manifest": manifest_name,
                "role": record.get("role"),
                "sha256": record.get("sha256"),
                "keep_reason": record.get("keep_reason"),
            })
    temp_records = {p: r for p, r in records.items() if p.startswith("tmp/")}
    if not temp_records:
        raise ValueError("R08 清单中没有待固化的 tmp 引用")

    r08_formal_files = []
    for record in delivery.get("files", []):
        path = record["path"]
        if path.startswith(f"{R08_REL}/"):
            actual = require_file(root, path, record.get("sha256"))
            r08_formal_files.append({
                **actual,
                "role": record.get("role"),
                "keep_reason": "R08 正式运行证据原件；未复制或改写。",
            })
    for relative in (inputs_rel, delivery_rel, result_rel, sidecar_rel):
        actual = require_file(root, relative)
        if not any(item["path"] == relative for item in r08_formal_files):
            r08_formal_files.append({
                **actual,
                "role": "input",
                "keep_reason": "R08 原始结果/清单/退出码 sidecar；用于确认恢复包对应的确切运行。",
            })
    return inputs, delivery, result, records


def verify_local_package(root: Path, r10_dir: Path) -> dict[str, Any]:
    recovery = read_json(r10_dir / "recovery_manifest.json")
    r08_inputs_rel = recovery["r08_original"]["inputs_manifest_path"]
    r08_delivery_rel = recovery["r08_original"]["delivery_manifest_path"]
    r08_result_rel = recovery["r08_original"]["preflight_result_path"]
    r08_inputs = read_json(project_path(root, r08_inputs_rel))
    r08_delivery = read_json(project_path(root, r08_delivery_rel))
    r08_result = read_json(project_path(root, r08_result_rel))
    for rel, expected in recovery["r08_original"]["file_hashes"].items():
        require_file(root, rel, expected)
    if (r08_result.get("status") != "BLOCKED"
            or r08_result.get("core_execution", {}).get("status") != "NOT_RUN"
            or r08_result.get("runner_process", {}).get("exit_code") != 2):
        raise ValueError("干净副本中的 R08 原始 BLOCKED/NOT_RUN/退出码状态不匹配")

    current_temp: dict[str, str] = {}
    for document in (r08_inputs, r08_delivery):
        for item in document.get("files", []):
            path = item.get("path", "")
            if path.startswith("tmp/"):
                current_temp[path] = item.get("sha256")
    saved_temp = {item["original_path"]: item["sha256"]
                  for item in recovery.get("recovered_tmp_files", [])}
    if current_temp != saved_temp:
        raise ValueError("R08 两清单的 tmp 路径/SHA 集合与恢复映射不一致")

    verified = []
    for item in recovery["recovered_tmp_files"]:
        original = item["original_path"]
        stored = item["stored_path"]
        if not original.startswith("tmp/6/"):
            raise ValueError(f"恢复映射越出 tmp/6 子树：{original}")
        safe_rel_path(original)
        safe_rel_path(stored)
        if not stored.startswith(f"{R10_REL}/recovery_inputs/"):
            raise ValueError(f"保存路径不在正式 R10 recovery_inputs 内：{stored}")
        actual = require_file(root, stored, item["sha256"])
        if actual["bytes"] != item["bytes"]:
            raise ValueError(f"保存副本 bytes 不一致：{stored}")
        verified.append({"original_path": original, "stored_path": stored,
                         "sha256": actual["sha256"], "bytes": actual["bytes"],
                         "status": "PASS"})

    for manifest_name in ("inputs_manifest.json", "delivery_manifest.json"):
        path = r10_dir / manifest_name
        if path.is_file():
            manifest = read_json(path)
            for item in manifest.get("files", []):
                rel = item.get("path", "")
                if rel.startswith("tmp/"):
                    raise ValueError(f"R10 清单仍直接依赖 tmp 路径：{rel}")
                safe_rel_path(rel)

    return {"status": "PASS_LOCAL_RECOVERY_MAP_AND_BYTES",
            "r08_run_id": R08_RUN_ID,
            "r08_original_status": "BLOCKED",
            "r08_core_execution": "NOT_RUN",
            "r08_runner_child_exit_code": 2,
            "tmp_reference_count": len(verified),
            "verified_files": verified,
            "scope": "仅校验 R10 本地保存字节与映射；不恢复 tmp，不重跑 R08 checker。"}


def build(root: Path, r10_dir: Path) -> dict[str, Any]:
    root = root.resolve()
    if not r10_dir.is_dir() or r10_dir.is_symlink():
        raise ValueError("R10 精确目标必须是已核验的普通目录")
    if r10_dir.resolve() != project_path(root, R10_REL):
        raise ValueError("R10 目录与固定相对路径不一致")
    allowed_existing = {"recover_r08_tmp_inputs.py"}
    extras = {item.name for item in r10_dir.iterdir()} - allowed_existing
    if extras:
        raise FileExistsError(f"R10 已有其他内容，拒绝覆盖：{sorted(extras)}")

    r08_inputs, r08_delivery, r08_result, records = collect_r08_sources(root)
    temp_records = [records[path] for path in sorted(records) if path.startswith("tmp/")]
    recovered = []
    for record in temp_records:
        original = record["original_path"]
        relative_under_tmp = safe_rel_path(original).parts[1:]
        stored = f"{R10_REL}/recovery_inputs/" + "/".join(relative_under_tmp)
        destination = project_path(root, stored)
        if destination.exists():
            raise FileExistsError(f"恢复目标已存在，拒绝覆盖：{stored}")
        source = project_path(root, original)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as output:
            output.write(source.read_bytes())
        copied = require_file(root, stored, record["sha256"])
        if copied["bytes"] != record["bytes"]:
            raise ValueError(f"复制后 bytes 不一致：{stored}")
        recovered.append({
            **record,
            "stored_path": stored,
            "keep_reason": corrected_keep_reason(original),
        })

    r08_relations = {}
    for manifest_name, document in (("inputs_manifest.json", r08_inputs),
                                    ("delivery_manifest.json", r08_delivery)):
        for item in document.get("files", []):
            path = item.get("path", "")
            if path.startswith("tmp/"):
                continue
            try:
                safe_rel_path(path)
                actual = require_file(root, path, item.get("sha256"))
            except (ValueError, FileNotFoundError):
                continue
            record = r08_relations.setdefault(path, {
                "path": path,
                "sha256": actual["sha256"],
                "bytes": actual["bytes"],
                "manifest_records": [],
            })
            record["manifest_records"].append({
                "manifest": manifest_name,
                "role": item.get("role"),
                "keep_reason": item.get("keep_reason"),
            })

    inputs_rel = f"{R08_REL}/inputs_manifest.json"
    delivery_rel = f"{R08_REL}/delivery_manifest.json"
    result_rel = f"{R08_REL}/preflight_result.json"
    sidecar_rel = f"{R08_REL}/runner_exit_code.txt"
    reference_hashes = {
        inputs_rel: sha256_file(project_path(root, inputs_rel)),
        delivery_rel: sha256_file(project_path(root, delivery_rel)),
        result_rel: sha256_file(project_path(root, result_rel)),
        sidecar_rel: sha256_file(project_path(root, sidecar_rel)),
    }
    r08_formal_files = []
    for record in r08_delivery.get("files", []):
        path = record.get("path", "")
        if path.startswith(f"{R08_REL}/"):
            actual = require_file(root, path, record.get("sha256"))
            r08_formal_files.append({**actual, "role": record.get("role"),
                                     "keep_reason": "R08 正式证据原件；保留原路径与哈希。"})
    for path in (inputs_rel, delivery_rel, result_rel, sidecar_rel):
        if not any(item["path"] == path for item in r08_formal_files):
            actual = require_file(root, path)
            r08_formal_files.append({**actual, "role": "input",
                                     "keep_reason": "R08 原始结果/清单/退出码 sidecar；恢复包来源。"})

    branch = git_output(root, "branch", "--show-current")
    head = git_output(root, "rev-parse", "HEAD")
    core_binding = next((item for item in r08_result.get("stage6_source_bindings", [])
                         if item.get("path") == "src/stage6/s6_core.py"), None)
    if core_binding is None:
        raise ValueError("R08 缺少 stage6 core 源码绑定")
    r08_checks = [{"name": item.get("name"), "status": item.get("status"),
                   "exit_code": item.get("exit_code"), "reason": item.get("reason")}
                  for item in r08_delivery.get("checks", [])]
    script_abs = Path(__file__).resolve()
    build_command = subprocess.list2cmdline([
        sys.executable, "-B", "-X", "utf8", str(script_abs), "--build",
        "--project-root", str(root), "--r10-rel", R10_REL,
    ])
    recovery = {
        "schema_version": 1,
        "artifact_kind": "S6-D evidence recovery supplement",
        "run_id": R10_RUN_ID,
        "generated_utc8": now_utc8(),
        "recovery_scope": "只固化 R08 清单所引用的临时输入字节和恢复映射；不是新的回放运行或独立审查。",
        "builder_command": build_command,
        "r08_original": {
            "run_id": R08_RUN_ID,
            "run_dir": R08_REL,
            "inputs_manifest_path": inputs_rel,
            "delivery_manifest_path": delivery_rel,
            "preflight_result_path": result_rel,
            "runner_exit_code_sidecar_path": sidecar_rel,
            "file_hashes": reference_hashes,
            "source_commit": r08_result.get("stage6_source_commit"),
            "current_w6_branch": branch,
            "current_w6_head": head,
            "status": r08_result.get("status"),
            "core_execution": r08_result.get("core_execution"),
            "runner_process_command": r08_result.get("runner_process", {}).get("command"),
            "runner_process_exit_code": r08_result.get("runner_process", {}).get("exit_code"),
            "runner_exit_code_sidecar_text": project_path(root, sidecar_rel).read_text(encoding="utf-8").strip(),
            "blocked_check_exit_code_field": None,
            "core_sha256": core_binding.get("disk_sha256"),
            "core_disk_matches_head_blob": core_binding.get("disk_matches_head_blob"),
            "checks": r08_checks,
        },
        "source_manifests": {
            "inputs_manifest_sha256": reference_hashes[inputs_rel],
            "delivery_manifest_sha256": reference_hashes[delivery_rel],
            "preflight_result_sha256": reference_hashes[result_rel],
        },
        "recovered_tmp_files": recovered,
        "r08_formal_files": r08_formal_files,
        "r08_non_tmp_input_references": list(r08_relations.values()),
        "history_keep_reason_policy": {
            "r05": "目录冲突导致预检拒绝；初版阳性审计的 CRLF/raw blob 比较错误单独标注。",
            "r06": "W5 工作树与固定旧提交 blob 不同；固定 blob 哈希匹配，审计在创建运行目录前终止。",
            "r07": "最终 inputs/evidence checker 对包装器字段报错；分别记录原始 manifests 与 checker 输出。",
            "r08": "输入资格 BLOCKED（stale=null）；子进程 exit=2，check manifest 中 BLOCKED exit_code 保持 null；核心 NOT_RUN。",
        },
        "manual_restore_procedure": [
            "在副本中验证 R10：运行 recover_r08_tmp_inputs.py --verify-local；此模式仅读取 R08 正式证据和 R10 保存字节。",
            "如需重跑原 R08 checker，按 recovered_tmp_files 将 stored_path 逐项复制到 original_path；仅当目标不存在时复制，目标已存在且 SHA 不同则停止，不覆盖。",
            "所有映射还原后，才可使用 R08 原 delivery_manifest 记录的 checker 命令；本 R10 没有执行该恢复或重跑。",
        ],
        "privacy_review": {
            "credential_markers_found": False,
            "note": "9 个源文件未发现凭据标记；其中 R05 命令记录包含本机 Python 安装路径，原字节为 SHA 一致性要求保留，仅用于本机审计，不上传。",
        },
        "limitations": [
            "R10 本地自检只校验映射、R08 正式清单哈希和保存副本字节；不验证 W4/W5 新鲜度，也不调用阶段6核心。",
            "R08 原始 inputs/evidence checker 仍引用 tmp/6；干净副本必须按上述映射先恢复目标文件，R10 自检本身不声称 R08 checker 无需恢复即可重跑。",
            "阶段6输入仍 BLOCKED；T6-A03/P、硬件 G3、6-E 实物验收及 G4/G5 未执行。",
        ],
    }
    recovery_path = r10_dir / "recovery_manifest.json"
    write_json(recovery_path, recovery)

    summary = [
        "# S6-D R08 临时依赖恢复补充包",
        "",
        "- 类型：证据路径恢复补充；不是新回放执行，也不是独立技术审查。",
        f"- 来源运行：`{R08_RUN_ID}`；原始清单 SHA 已在 `recovery_manifest.json` 绑定。",
        f"- R08 原结论：**{r08_result.get('status')}**；阶段6核心：**{r08_result.get('core_execution', {}).get('status')}**。",
        f"- R08 预检子进程实际退出码：`{r08_result.get('runner_process', {}).get('exit_code')}`；sidecar 原文 `{recovery['r08_original']['runner_exit_code_sidecar_text']}`。BLOCKED 检查字段仍为 `exit_code=null`。",
        f"- tmp 引用：{len(recovered)} 个；按 R08 两清单声明 SHA 复制到 `recovery_inputs/`，源/目标 SHA 和 bytes 一致。",
        "- R05、R06、R07 历史失败按轮次及文件逐项重述，见 `recovery_manifest.json` 和 R10 `inputs_manifest.json`；R08 原清单不改写。",
        "- R10 本地自检只读验证 R08 清单哈希、映射与 R10 保存字节；原 R08 checker 仍需按映射恢复 tmp 路径后重跑。",
        "- 恢复提示：只在目标缺失时按映射复制；目标已存在且哈希不同则停止，不覆盖。未执行 restore，也未重跑原 R08 checker。",
        "- 阳性与 NO_HAND 输入资格结论保持 BLOCKED；没有调用核心、没有板上或 G3/G4/G5 结论。",
        "",
    ]
    summary_path = r10_dir / "summary.md"
    summary_path.write_text("\n".join(summary), encoding="utf-8")

    command = subprocess.list2cmdline([
        sys.executable, "-B", "-X", "utf8", str(script_abs), "--verify-local",
        "--project-root", str(root), "--r10-rel", R10_REL,
    ])
    script_rel = SCRIPT_REL
    local_files: dict[str, dict[str, Any]] = {}

    def add_file(path: str, role: str, reason: str, expected_sha: str | None = None) -> None:
        actual = require_file(root, path, expected_sha)
        previous = local_files.get(path)
        candidate = {
            "path": actual["path"],
            "sha256": actual["sha256"],
            "role": role,
            "keep_reason": reason,
        }
        if previous is not None:
            if previous["sha256"] != candidate["sha256"]:
                raise ValueError(f"R10 同一路径重复记录 SHA 不一致：{path}")
            if role == "source":
                previous["role"] = "source"
            previous["keep_reason"] = reason if "R07" in path or path.startswith("tmp/") else previous["keep_reason"]
        else:
            local_files[path] = candidate

    add_file(script_rel, "source", "R10 证据恢复包构建和只读本地映射验证脚本。")
    add_file(RECOVERY_REL, "result", "R08 原始 SHA 到 R10 持久副本的可恢复映射及限制。")
    add_file(SUMMARY_REL, "result", "R10 恢复补充包范围和人工恢复步骤摘要。")
    for item in recovered:
        add_file(item["stored_path"], "input", item["keep_reason"], item["sha256"])
    for path, record in sorted(r08_relations.items()):
        add_file(path, "input", corrected_keep_reason(path), record["sha256"])
    for item in r08_formal_files:
        add_file(item["path"], "input", item["keep_reason"], item["sha256"])

    recovery_ref = {
        "path": RECOVERY_REL,
        "sha256": sha256_file(recovery_path),
        "role": "result",
        "keep_reason": "恢复映射和 R08 原状态绑定。",
    }
    input_files = list(local_files.values())
    inputs_doc = {
        "schema_version": 1,
        "stage": "6",
        "task_id": "S6-D",
        "run_id": R10_RUN_ID,
        "source_commit": git_output(root, "rev-parse", "HEAD"),
        "evidence_dir": R10_REL,
        "interfaces": [],
        "interfaces_not_applicable_reason": "本项仅恢复 R08 tmp 输入字节的持久引用，不构成阶段4/5接口或阶段6集成验证。",
        "files": input_files,
        "checks": [{
            "name": "R08 tmp 引用到 R10 持久副本映射自检",
            "status": "PASS",
            "command": command,
            "exit_code": 0,
        }],
        "limitations": [
            "仅检查 R10 保存副本与映射；未恢复 tmp、未重跑 R08 原 checker、未调用阶段6核心。",
            "R08 输入资格仍 BLOCKED；R10 清单结构检查通过不提升该结论。",
        ],
    }
    inputs_path = r10_dir / "inputs_manifest.json"
    write_json(inputs_path, inputs_doc)

    verifier_command = [sys.executable, "-B", "-X", "utf8", str(script_abs),
                        "--verify-local", "--project-root", str(root), "--r10-rel", R10_REL]
    verify_run = run_tool(verifier_command, root)
    (r10_dir / "recovery_verify_output.txt").write_text(
        verify_run["stdout"] + verify_run["stderr"], encoding="utf-8")
    if verify_run["exit_code"] != 0:
        raise RuntimeError(f"R10 恢复包本地自检失败：{verify_run['stderr']}")

    checker = root / "verification/check_stage_delivery.py"
    inputs_command = [sys.executable, "-B", "-X", "utf8", str(checker), "--mode", "inputs",
                      "--manifest", str(inputs_path), "--project-root", str(root)]
    inputs_run = run_tool(inputs_command, root)
    (r10_dir / "check_inputs_mode_output.txt").write_text(
        inputs_run["stdout"] + inputs_run["stderr"], encoding="utf-8")

    delivery_files = list(local_files.values())
    for path, reason in (
        (f"{R10_REL}/inputs_manifest.json", "R10 inputs mode 使用的原始输入清单。"),
        (f"{R10_REL}/recovery_verify_output.txt", "R10 本地只读恢复映射与文件 SHA 自检真实 stdout/stderr。"),
        (f"{R10_REL}/check_inputs_mode_output.txt", "R10 inputs checker 真实 stdout/stderr。"),
    ):
        actual = require_file(root, path)
        delivery_files.append({
            "path": actual["path"],
            "sha256": actual["sha256"],
            "role": "log",
            "keep_reason": reason,
        })
    r08_process = r08_result["runner_process"]
    delivery_doc = {
        "schema_version": 1,
        "stage": "6",
        "task_id": "S6-D",
        "run_id": R10_RUN_ID,
        "source_commit": git_output(root, "rev-parse", "HEAD"),
        "evidence_dir": R10_REL,
        "interfaces": [],
        "interfaces_not_applicable_reason": inputs_doc["interfaces_not_applicable_reason"],
        "files": delivery_files,
        "checks": [
            {
                "name": "R08 原始回放输入资格",
                "status": "BLOCKED",
                "command": r08_process.get("command"),
                "exit_code": None,
                "reason": "该行原样反映 R08 BLOCKED：stale=null，core NOT_RUN；真实子进程退出码 2 记录在 R08 result 与 sidecar。",
            },
            {
                "name": "R08 tmp 引用持久副本与映射自检",
                "status": "PASS",
                "command": command,
                "exit_code": verify_run["exit_code"],
            },
            {
                "name": "R10 inputs mode",
                "status": "PASS" if inputs_run["exit_code"] == 0 else "FAIL",
                "command": inputs_run["command"],
                "exit_code": inputs_run["exit_code"],
                **({} if inputs_run["exit_code"] == 0
                   else {"reason": "R10 inputs 模式失败，见 check_inputs_mode_output.txt"}),
            },
            {
                "name": "R10 evidence mode",
                "status": "NOT_RUN",
                "command": subprocess.list2cmdline([
                    sys.executable, "-B", "-X", "utf8", str(checker), "--mode", "evidence",
                    "--manifest", str(r10_dir / "delivery_manifest.json"),
                    "--project-root", str(root),
                ]),
                "exit_code": None,
                "reason": "在最终清单写定前尚未执行；随后记录实际 evidence checker 结果。",
            },
        ],
        "limitations": inputs_doc["limitations"],
        "tool_versions": {
            "python": sys.version.split()[0],
            "git": git_output(root, "--version"),
        },
    }
    delivery_path = r10_dir / "delivery_manifest.json"
    write_json(delivery_path, delivery_doc)
    evidence_command = [sys.executable, "-B", "-X", "utf8", str(checker), "--mode", "evidence",
                        "--manifest", str(delivery_path), "--project-root", str(root)]
    evidence_run = run_tool(evidence_command, root)
    evidence_check = next(item for item in delivery_doc["checks"]
                          if item.get("name") == "R10 evidence mode")
    evidence_check.update({
        "status": "PASS" if evidence_run["exit_code"] == 0 else "FAIL",
        "command": evidence_run["command"],
        "exit_code": evidence_run["exit_code"],
    })
    if evidence_run["exit_code"] != 0:
        evidence_check["reason"] = "R10 evidence 模式失败；真实 stdout/stderr 由本次构建进程输出返回。"
    else:
        evidence_check.pop("reason", None)
    write_json(delivery_path, delivery_doc)
    final_evidence_run = run_tool(evidence_command, root)
    if final_evidence_run["exit_code"] != 0:
        evidence_check.update({
            "status": "FAIL",
            "command": final_evidence_run["command"],
            "exit_code": final_evidence_run["exit_code"],
            "reason": "R10 最终 delivery_manifest 自检失败；真实 stdout/stderr 由本次构建进程输出返回。",
        })
        write_json(delivery_path, delivery_doc)

    summary_output = {
        "run_id": R10_RUN_ID,
        "artifact_kind": "evidence_recovery_only",
        "r08_status_preserved": r08_result["status"],
        "r08_core_execution": r08_result["core_execution"]["status"],
        "r08_child_exit_code": r08_process["exit_code"],
        "recovered_tmp_file_count": len(recovered),
        "verify_exit_code": verify_run["exit_code"],
        "inputs_check_exit_code": inputs_run["exit_code"],
        "evidence_check_exit_code": evidence_run["exit_code"],
        "final_evidence_check_exit_code": final_evidence_run["exit_code"],
    }
    print(json.dumps(summary_output, ensure_ascii=False))
    print(evidence_run["stdout"] + evidence_run["stderr"], end="")
    print(final_evidence_run["stdout"] + final_evidence_run["stderr"], end="")
    if (inputs_run["exit_code"] != 0 or evidence_run["exit_code"] != 0
            or final_evidence_run["exit_code"] != 0):
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(description="阶段6 R08 临时输入的持久化补充工具")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build", action="store_true", help="创建新的 R10 持久恢复补充包")
    mode.add_argument("--verify-local", action="store_true", help="只读核验 R10 映射及保存字节")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--r10-rel", default=R10_REL)
    args = parser.parse_args(argv)
    root = Path(args.project_root).resolve()
    if args.r10_rel != R10_REL:
        parser.error(f"R10 路径必须精确为 {R10_REL}")
    r10_dir = project_path(root, args.r10_rel)
    try:
        if args.build:
            return build(root, r10_dir)
        result = verify_local_package(root, r10_dir)
    except Exception as exc:  # noqa: BLE001
        print(f"R10 恢复包操作失败：{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
