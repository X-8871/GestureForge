"""S5-T01 上板硬性前置门禁 v2（fail-closed、只读）。

修订原因（CDX-20261022-014 §0）：v1 用「全部 MD 全文关键词」推断占用，导致**普通操作文档**
（如 `CDX-20261022-014` 运行书正文出现“释放/独占”）被当成最新占用，使此前有效让出失效。

v2 规则：
  1. **登记表驱动**：`scripts/stage5_t01/hardware_handoff_registry.json` 逐条登记 `id/file/sha256/
     order_key/kind/hardware_scope`，状态类仅 `hardware_occupation` / `hardware_release`。
     普通请求、操作文档、回执、报告、决策一律**中性**（不改变硬件状态）。
  2. **绑定核验**：登记项的文件必须存在且 SHA256 一致；带 `evidence_quote` 的登记项，其引用原文必须
     能在该记录中找到 ⇒ 否则视为证据矛盾 → BLOCKED。
  3. **未登记即不可信**：未登记文件若文件名或声明标记（`hw_handoff_kind: ...`）自称硬件交接 →
     BLOCKED（不可识别的硬件交接记录）；否则中性并在报告中列出。
  4. **顺序与范围**：同一 `hardware_scope` 内按 `order_key` 排序，最新状态类记录决定硬件状态；
     让出必须晚于最近占用，且其 scope 必须覆盖本次请求范围。
  5. **现场一致性**：无 `index.lock`；硬件/重型进程枚举成功且为空。任一枚举失败 → BLOCKED。
  6. 授权（`--authorized-by/--authorization-note`）仅在**存在适用本次操作的明确授权原文**时可用：
     必须同时给出 `--authorization-source` 与其 `--authorization-source-sha256`，且 `note` 必须是该
     原文的子串；否则授权被拒（记录原因）。**本操作文档不提供该授权，也不得为绕过误判而填造内容。**

退出码：0=GO；1=BLOCKED；2=环境/输入错误。
用法：
  python -B scripts/stage5_t01/check_hardware_gate.py --out report/evidence/S5-T01/<run_id> \
      --release-id <让出编号> [--authorized-by W --authorization-note ... \
      --authorization-source <path> --authorization-source-sha256 <hex>]
测试用隔离参数：--registry/--mailbox-root/--process-check/--lock-check/--main-state
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import pathlib
import re
import subprocess
import sys

W5 = pathlib.Path(r"D:\codex-worktrees\w5")
MAIN_ROOT = pathlib.Path(r"D:\FPGA_Competition")
DEFAULT_REGISTRY = W5 / "scripts/stage5_t01/hardware_handoff_registry.json"
DEFAULT_MAILBOX_ROOTS = [MAIN_ROOT / "report/evidence/CTRL-DSH-HANDOFF/codex_mailbox",
                         MAIN_ROOT / "report/evidence/CTRL-DSH-HANDOFF/dsh_mailbox"]
DEFAULT_MAIN_STATE = MAIN_ROOT / ".codex/STATE.md"
WORKTREES = {
    "main": MAIN_ROOT,
    "w2b": MAIN_ROOT / "w2b",
    "w4": pathlib.Path(r"D:\codex-worktrees\w4"),
    "w5": W5,
    "dbdf": pathlib.Path(r"D:\codex-worktrees\dbdf"),
    "96a3": pathlib.Path(r"D:\codex-worktrees\96a3"),
}
PROCESS_PATTERNS = ("hw_server", "vivado", "xsdb", "vitis", "xsim", "cs_server")
# 工具包装器（非板卡会话）：如 ROSS 的 `vivado-mcp-server-<ver>.exe --stdio`。
# 2026-10-23 发现：名称含 "vivado" 的 MCP 工具进程会被 PROCESS_PATTERNS 命中而误判为硬件占用，
# 使门禁在"无 hw_server、3121 未监听"时也 BLOCKED。此处**不删除检查**，而是**分类**：
# 工具包装器单列 `tooling_processes`（透明可见、不阻断）；真实硬件进程仍 fail-closed 阻断。
# 该分类需独立复审确认（见 report/evidence/S5-T01/s5t01_gate_fix_20261022_r01/FINDING_mcp_tooling.md）。
TOOLING_PATTERN = re.compile(r"vivado[-_]mcp[-_]server", re.IGNORECASE)
# 仅用于**未登记**文件的“自称硬件交接”识别（不再用于全量状态推断）
HANDOFF_HINT = re.compile(r"(让出|释放|占用|空档|handover|release|exclusive|独占|hw_handoff)", re.IGNORECASE)
DECL_MARKER = re.compile(r"hw_handoff_kind\s*[:=]\s*([a-z_]+)", re.IGNORECASE)
STATE_HW_HINT = re.compile(r"(hw_server|JTAG|COM4|让出|占用|空档|硬件)")


def now_utc8() -> str:
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%dT%H:%M:%S+08:00")


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def git(worktree: pathlib.Path, *args: str) -> str:
    code, out = run(["git", "-C", str(worktree), *args])
    return out.strip()


def load_registry(path: pathlib.Path) -> tuple[dict, list[str]]:
    problems: list[str] = []
    if not path.exists():
        return {}, [f"登记表不存在：{path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:                                   # noqa: BLE001
        return {}, [f"登记表无法解析：{exc}"]
    if not isinstance(data.get("records"), list):
        problems.append("登记表缺少 records 列表")
    return data, problems


def scan_mailboxes(roots: list[pathlib.Path]) -> list[pathlib.Path]:
    """返回全部信箱 MD 的**列表**（不按 basename 去重）。

    第三轮复审发现的既有 fail-open：原先以 basename 为键，两信箱同名文件会互相覆盖，
    被覆盖的一方**永不解析**（真实占用可被同名普通记录遮蔽）。改为列表后两份都参与判定。
    """
    found: list[pathlib.Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.md")):
            found.append(path)
    return found


def normalize_file_entry(name: str) -> tuple[str, str]:
    """把登记表的 `file` 规范化为 (root/basename, basename)。

    BI-1 残余修复：**validate 与 classify 必须共用同一规范化结果**，否则
    `codex_mailbox\\X.md`（反斜杠）或裸名 `X.md` 会让 validate 通过、classify 匹配不到，
    使状态类登记项被静默丢弃（fail-open）。接受 `/` 与 `\\`，返回统一以 `/` 分隔的键。
    """
    s = str(name or "").replace("\\", "/").strip()
    parts = [p for p in s.split("/") if p]
    if not parts:
        return "", ""
    base = parts[-1]
    root = parts[-2] if len(parts) >= 2 else ""
    return (f"{root}/{base}" if root else base), base


def validate_registry(registry: dict, files: list[pathlib.Path]) -> tuple[list[str], list[dict]]:
    """BI-1：登记项 schema 强校验（含 file 身份归一化）。任何不一致 → BLOCKED。"""
    problems: list[str] = []
    records = registry.get("records")
    if not isinstance(records, list):
        return ["登记表缺少 records 列表"], []
    state_kinds = set(registry.get("state_changing_kinds", []))
    neutral_kinds = set(registry.get("neutral_kinds", []))
    allowed = state_kinds | neutral_kinds
    # 实际扫描集合：规范化键（root/basename）→ path（列表输入，同名不同根各自独立）
    actual = {f"{p.parent.name}/{p.name}": p for p in files}
    seen_basenames: dict[str, int] = {}
    for idx, rec in enumerate(records):
        name = rec.get("file")
        if not name:
            problems.append(f"登记项#{idx} 缺 file 字段")
            continue
        key, base = normalize_file_entry(name)
        if not base:
            problems.append(f"登记项#{idx} 的 file 为空或不可解析：{name!r}")
            continue
        if "/" not in key:
            problems.append(f"登记项缺少信箱目录前缀（裸文件名不可作为身份）：{name}（规范化={key}）")
        if key not in actual:
            problems.append(f"登记项指向的信箱文件缺席：{name}（规范化键={key}；不得靠删除/改名登记文件放行）")
            continue
        if base in seen_basenames:
            problems.append(f"同一文件重复登记（按 basename 判定）：{name} 与第 {seen_basenames[base] + 1} 条")
        seen_basenames.setdefault(base, idx)
        kind = rec.get("kind")
        if kind not in allowed:
            problems.append(f"登记项 kind 非法或拼写错误：{name} kind={kind!r}")
            continue
        if not rec.get("sha256"):
            problems.append(f"登记项缺 sha256：{name}（不得跳过绑定）")
        else:
            actual_sha = sha256_file(actual[key])
            if str(rec["sha256"]).lower() != actual_sha.lower():
                problems.append(f"登记项哈希不匹配（证据矛盾）：{name} "
                                f"登记={str(rec['sha256'])[:12]}… 实际={actual_sha[:12]}…")
        if kind in state_kinds and not rec.get("order_key"):
            problems.append(f"状态类登记项缺 order_key：{name}")
        quote = rec.get("evidence_quote")
        if quote:
            text = actual[key].read_text(encoding="utf-8", errors="replace")
            if quote not in text:
                problems.append(f"登记项证据原文不匹配（证据矛盾）：{name} 未找到引用原文 {quote!r}")
    return problems, records


def classify(files: list[pathlib.Path], registry: dict) -> tuple[list[dict], list[dict], list[str]]:
    """返回 (状态类记录, 中性记录, 问题)。"""
    problems: list[str] = []
    by_key: dict[str, dict] = {}
    for rec in registry.get("records", []):
        key, base = normalize_file_entry(rec.get("file", ""))
        if base:
            by_key[key] = rec
    state_records: list[dict] = []
    neutral: list[dict] = []
    scopes = registry.get("state_changing_kinds", ["hardware_occupation", "hardware_release"])

    for path in files:
        name = path.name
        key = f"{path.parent.name}/{name}"
        text = path.read_text(encoding="utf-8", errors="replace")
        rec = by_key.get(key)
        if rec is None:
            hinted_name = bool(HANDOFF_HINT.search(name))
            marker = DECL_MARKER.search(text)
            hinted_body = bool(HANDOFF_HINT.search(text))
            if hinted_name or marker or hinted_body:
                reasons_extra = []
                if hinted_name:
                    reasons_extra.append("文件名含交接语义")
                if marker:
                    reasons_extra.append("声明标记 " + marker.group(0))
                if hinted_body:
                    reasons_extra.append("正文含交接语义")
                problems.append(f"未登记的硬件交接记录（不可识别）：{name}（{'；'.join(reasons_extra)}）")
            else:
                neutral.append({"file": name, "kind": "unregistered_neutral",
                                "note": "未登记且文件名/正文/声明标记均不含交接语义 → 中性"})
            continue
        kind = rec.get("kind")
        actual = sha256_file(path)
        if rec.get("sha256") and rec["sha256"] != actual:
            problems.append(f"登记项哈希不匹配（证据矛盾）：{name} 登记={rec['sha256'][:12]}… 实际={actual[:12]}…")
        quote = rec.get("evidence_quote")
        if quote and quote not in text:
            problems.append(f"登记项证据原文不匹配（证据矛盾）：{name} 未找到引用原文 {quote!r}")
        entry = {"file": name, "key": key, "id": rec.get("id"), "kind": kind, "order_key": rec.get("order_key"),
                 "hardware_scope": rec.get("hardware_scope"), "issuer": rec.get("issuer"),
                 "sha256_actual": actual, "sha256_registered": rec.get("sha256"),
                 "note": rec.get("note")}
        if kind in scopes:
            state_records.append(entry)
        else:
            neutral.append(entry)
    state_records.sort(key=lambda r: r.get("order_key") or "")
    return state_records, neutral, problems


def effective_state(state_records: list[dict], scope: str) -> tuple[str, dict | None, dict | None]:
    latest_occ, latest_rel = None, None
    for rec in state_records:
        rec_scope = rec.get("hardware_scope") or ""
        if scope not in rec_scope and rec_scope:
            continue
        if rec["kind"] == "hardware_occupation":
            latest_occ = rec
        elif rec["kind"] == "hardware_release":
            latest_rel = rec
    if latest_rel and (latest_occ is None or (latest_rel.get("order_key") or "") > (latest_occ.get("order_key") or "")):
        return "RELEASED", latest_rel, latest_occ
    if latest_occ:
        return "OCCUPIED", latest_rel, latest_occ
    return "UNKNOWN", latest_rel, latest_occ


def real_processes() -> tuple[list[dict], str, bool]:
    attempts = [
        ["cmd.exe", "/c", "tasklist", "/FO", "CSV", "/NH"],
        ["tasklist", "/FO", "CSV", "/NH"],
        ["pwsh", "-NoProfile", "-Command",
         "Get-Process | Select-Object ProcessName,Id | ConvertTo-Csv -NoTypeInformation"],
    ]
    raw = ""
    for cmd in attempts:
        code, out = run(cmd)
        raw += f"$ {' '.join(cmd)}\n[exit code: {code}]\n{out}\n"
        if code != 0 or not out.strip():
            continue
        found, tooling = [], []
        for line in out.splitlines():
            parts = [p.strip().strip('"') for p in line.split(",")]
            if len(parts) < 2:
                continue
            name = parts[0].strip('"')
            if any(pattern in name.lower() for pattern in PROCESS_PATTERNS):
                entry = {"name": name, "pid": parts[1].strip('"')}
                if TOOLING_PATTERN.search(name):
                    tooling.append(entry)
                else:
                    found.append(entry)
        return found, tooling, raw, True
    return [], [], raw, False


def main() -> int:
    parser = argparse.ArgumentParser(description="S5-T01 上板硬性前置门禁 v2（只读、fail-closed、登记表驱动）")
    parser.add_argument("--out", required=True)
    parser.add_argument("--release-id", default=None)
    parser.add_argument("--authorized-by", default=None)
    parser.add_argument("--authorization-note", default=None)
    parser.add_argument("--authorization-source", default=None)
    parser.add_argument("--authorization-source-sha256", default=None)
    parser.add_argument("--scope", default="JTAG+COM4")
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--mailbox-root", action="append", default=None)
    parser.add_argument("--process-check", choices=["real", "stub-ok", "stub-fail", "stub-hit", "stub-tooling"],
                        default="real")
    parser.add_argument("--lock-check", choices=["real", "stub-none", "stub-lock"], default="real")
    parser.add_argument("--main-state", default=str(DEFAULT_MAIN_STATE))
    args = parser.parse_args()

    out_dir = pathlib.Path(args.out)
    if not out_dir.is_absolute():
        out_dir = W5 / out_dir
    console = out_dir / "console"

    registry_path = pathlib.Path(args.registry)
    registry, problems = load_registry(registry_path)
    reasons: list[str] = list(problems)

    roots = [pathlib.Path(p) for p in args.mailbox_root] if args.mailbox_root else DEFAULT_MAILBOX_ROOTS
    files = scan_mailboxes(roots)
    if not files:
        reasons.append("未发现任何信箱记录（fail-closed）")
    state_records, neutral, class_problems = classify(files, registry)
    reasons.extend(class_problems)
    schema_problems, _ = validate_registry(registry, files)
    reasons.extend(schema_problems)

    dup_keys = [k for k in {r.get("order_key") for r in state_records if r.get("order_key")}
                if sum(1 for r in state_records if r.get("order_key") == k) > 1]
    if dup_keys:
        reasons.append(f"状态类 order_key 重复（排序歧义）：{sorted(dup_keys)}")

    # BI-1 残余条件③：每条状态类登记项都必须**真正被应用**（否则等于被静默丢弃）
    applied_keys = {r.get("key") for r in state_records}
    state_kinds_all = set(registry.get("state_changing_kinds", []))
    for rec in registry.get("records", []):
        if rec.get("kind") in state_kinds_all:
            rkey, _ = normalize_file_entry(rec.get("file", ""))
            if rkey not in applied_keys:
                reasons.append(f"状态类登记项未被应用（身份/前缀不一致，等同静默丢弃）："
                               f"{rec.get('file')}（规范化={rkey}）")

    state, release, occupation = effective_state(state_records, args.scope)

    # 锁
    worktrees: dict[str, dict] = {}
    locks: list[str] = []
    if args.lock_check == "stub-lock":
        locks = ["stub-w5"]
        worktrees["stub"] = {"exists": True, "index_lock_exists": True, "note": "测试替身"}
    elif args.lock_check == "stub-none":
        worktrees["stub"] = {"exists": True, "index_lock_exists": False, "note": "测试替身"}
    else:
        for name, path in WORKTREES.items():
            if not path.exists():
                worktrees[name] = {"exists": False}
                continue
            lock_path = git(path, "rev-parse", "--git-path", "index.lock")
            lock_abs = pathlib.Path(lock_path) if pathlib.Path(lock_path).is_absolute() else path / lock_path
            worktrees[name] = {"exists": True, "branch": git(path, "rev-parse", "--abbrev-ref", "HEAD"),
                               "head": git(path, "rev-parse", "HEAD"), "index_lock_path": lock_path,
                               "index_lock_exists": lock_abs.exists()}
        locks = [name for name, info in worktrees.items() if info.get("index_lock_exists")]
    if locks:
        reasons.append(f"存在 index.lock：{locks}")

    # 进程
    if args.process_check == "stub-ok":
        procs, tooling, proc_raw, proc_ok = [], [], "[stub-ok] 测试替身：枚举成功且无命中\n", True
    elif args.process_check == "stub-hit":
        procs, tooling, proc_raw, proc_ok = [{"name": "hw_server", "pid": "9999"}], [], "[stub-hit]\n", True
    elif args.process_check == "stub-tooling":
        procs, tooling, proc_raw, proc_ok = [], [
            {"name": "vivado-mcp-server-windows-amd64-2026.9.1.exe", "pid": "10888"}], "[stub-tooling]\n", True
    elif args.process_check == "stub-fail":
        procs, tooling, proc_raw, proc_ok = [], [], "[stub-fail] 测试替身：枚举失败\n", False
    else:
        procs, tooling, proc_raw, proc_ok = real_processes()
    if not proc_ok:
        reasons.append("无法枚举系统进程（fail-closed）：不得据此认为无硬件占用，也不得放行")
    elif procs:
        reasons.append("检测到硬件/重型进程：" + ", ".join(f"{p['name']}({p['pid']})" for p in procs))

    # 授权（严格绑定出处）
    authorization = None
    rejected_authorization = None
    if args.authorized_by or args.authorization_note:
        if not (args.authorized_by and args.authorization_note and args.authorization_source
                and args.authorization_source_sha256):
            rejected_authorization = {"reason": "缺少 authorized-by/note/source/source-sha256 四者之一",
                                      "provided": {"authorized_by": args.authorized_by,
                                                   "source": args.authorization_source}}
        else:
            src = pathlib.Path(args.authorization_source)
            if not src.exists():
                rejected_authorization = {"reason": f"授权原文不存在：{src}"}
            else:
                actual = sha256_file(src)
                if actual.lower() != args.authorization_source_sha256.lower():
                    rejected_authorization = {"reason": "授权原文哈希不匹配",
                                              "expected": args.authorization_source_sha256, "actual": actual}
                else:
                    text = src.read_text(encoding="utf-8", errors="replace")
                    if args.authorization_note not in text:
                        rejected_authorization = {"reason": "授权说明不是原文子串（不得转述或填造）"}
                    else:
                        authorization = {"authorized_by": args.authorized_by, "note": args.authorization_note,
                                         "source": str(src), "source_sha256": actual, "recorded_utc8": now_utc8(),
                                         "basis": "operator_authorization（原文+哈希绑定）"}
    if rejected_authorization:
        reasons.append(f"授权被拒：{rejected_authorization['reason']}")

    release_basis = None
    authorization_ownership_unverifiable = False
    if release is not None and args.release_id == release.get("id"):
        release_basis = "mailbox_release"
    elif authorization is not None:
        release_basis = "operator_authorization"
    if state == "OCCUPIED":
        release_basis = None
        reasons.append(f"{args.scope} 处于占用态：最近状态类记录={occupation['id'] if occupation else '未知'}"
                       "（有效授权也不能覆盖真实占用）")
    elif state == "UNKNOWN":
        if authorization is None:
            reasons.append(f"无法确定 {args.scope} 硬件状态（无登记的状态类记录）且无有效授权")
        else:
            authorization_ownership_unverifiable = True
    if release_basis is None and state != "OCCUPIED":
        if release is None:
            reasons.append(f"登记表未发现适用于 {args.scope} 的让出记录，且无有效授权")
        else:
            reasons.append(f"未提供匹配的 --release-id：登记表检出 {release.get('id')}，实际传入 {args.release_id!r}")

    main_state_path = pathlib.Path(args.main_state)
    state_excerpt = []
    if main_state_path.exists():
        for line in main_state_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if STATE_HW_HINT.search(line):
                state_excerpt.append(line[:400])
    decision = "GO" if not reasons else "BLOCKED"
    report = {
        "schema_version": "gestureforge_s5t01_hardware_gate_v2",
        "task_id": "S5-T01",
        "generated_utc8": now_utc8(),
        "decision": decision,
        "reasons": reasons,
        "release_basis": release_basis,
        "authorization_ownership_unverifiable": authorization_ownership_unverifiable,
        "scope": args.scope,
        "hardware_state": state,
        "effective_release": release,
        "latest_occupation": occupation,
        "registry": {"path": str(registry_path), "sha256": sha256_file(registry_path) if registry_path.exists() else None,
                     "records_total": len(registry.get("records", []))},
        "mailbox_files_scanned": sorted(f"{p.parent.name}/{p.name}" for p in files),
        "state_records": state_records,
        "neutral_records": neutral,
        "unregistered_neutral_files": [r.get("file") for r in neutral
                                       if r.get("kind") == "unregistered_neutral"],
        "provided_release_id": args.release_id,
        "authorization": authorization,
        "rejected_authorization": rejected_authorization,
        "worktrees": worktrees,
        "hardware_processes": procs,
        "tooling_processes": tooling,
        "hardware_process_enumeration_ok": proc_ok,
        "lock_check_mode": args.lock_check,
        "process_check_mode": args.process_check,
        "main_state_hardware_excerpt_informational": state_excerpt,
        "notes": [
            "本门禁只读：不连接板卡、不启动 hw_server、不写寄存器。",
            "普通请求/操作文档/回执/报告中性，不改变硬件状态；只有登记表内 hardware_occupation/release 改变状态。",
            "未登记却自称硬件交接的记录、证据矛盾、锁或进程枚举失败 → BLOCKED（不通过删除校验“修好”）。",
            "门禁 GO 只表示可进入上板流程，不代表 G3/G4/G5 或任何验收通过；也不自动授予硬件使用权。",
        ],
    }

    console.mkdir(parents=True, exist_ok=True)
    (console / "state_records.json").write_text(json.dumps(state_records, ensure_ascii=False, indent=2) + "\n",
                                                encoding="utf-8")
    (console / "neutral_records.json").write_text(json.dumps(neutral, ensure_ascii=False, indent=2) + "\n",
                                                  encoding="utf-8")
    (console / "processes.json").write_text(json.dumps(procs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (console / "process_enumeration.txt").write_text(proc_raw, encoding="utf-8")
    (console / "worktrees.json").write_text(json.dumps(worktrees, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "hardware_gate.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"decision": decision, "hardware_state": state,
                      "effective_release": release.get("id") if release else None,
                      "latest_occupation": occupation.get("id") if occupation else None,
                      "reasons": reasons}, ensure_ascii=False))
    return 0 if decision == "GO" else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())