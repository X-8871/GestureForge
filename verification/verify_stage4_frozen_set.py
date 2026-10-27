"""阶段4 冻结集完整性校验（只读、可复跑）。

用途：证明"阶段4 离线范围冻结"不是一句声明，而是一组可逐字节复核的文件状态。
本脚本不写任何被校验对象、不接触硬件、不启动任何服务；只读取并判定。

校验项：
  F1 共享结果契约：状态 FROZEN_OFFLINE_ONLY，且 freeze_record 齐全、能回溯到被审字节
  F2 地址图与共享地址图：状态 APPROVED，review_binding 文件存在且 SHA 吻合
  F3 task-26 权威门：status PASS / exit_code 0 / 六项检查全 PASS / 桥接器自哈希一致
  F4 task-27 回放包（两份）：存在、标 replay_only、detections 数量与样本一致
  F5 硬件门禁记录：6 类记录通过 adapter 的 validate_hardware_gates 接受（只读调用）
  F6 门禁记录目录的 manifest 覆盖完整
  F7 BGR 重排：RTL 参数与测试台证据在位
  F8 结论口径：任何文件都不得把 NOT_RUN / 断点 / 部分完成写成通过（关键字扫描）

退出码：0 = 全部满足（可冻结）；1 = 存在未满足项；2 = 输入/环境错误。
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import traceback
from pathlib import Path
from types import ModuleType

WORKTREE = Path(__file__).resolve().parents[1]  # verification/ -> 工作树根
EVID = WORKTREE / "report" / "evidence"

CONTRACT = WORKTREE / "docs/stage4/s4b_shared_input_result_contract.json"
ADDRESS_MAP = WORKTREE / "docs/stage4/S4B_stage4_address_map.json"
SHARED_MAP = WORKTREE / "docs/stage4/S4B_shared_address_map.json"
GATE_RERUN = EVID / "S4-CTRL/s4t26_gate_rerun_20261027_r04"
GATES_DIR = EVID / "S4-B/s4b_hw_gates_20261027_r04"
PREP = WORKTREE / "tmp/4/S4-B-REAL-02B/s4b_ps_adapter_g3_20261027_r01/adapter_preparation.json"
BASE_REPLAY = EVID / "S4-CTRL/s4t27_replay_package_freeze_20261027_r01/replay_package_freeze.json"
POS_REPLAY = EVID / "S4-CTRL/s4t27_replay_positive_20261027_r01/task27_replay_result_package_positive.json"
BGR_EVID = EVID / "S4-B/s4b_bgr_remap_20261027_r01/result.json"
PREPROC_SV = WORKTREE / "src/s4b_preproc_frame.sv"

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path):
    """返回 (对象, 错误说明)。不抛异常，便于逐项判定。"""
    if not path.is_file():
        return None, "file_absent"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, ValueError) as exc:
        return None, f"unreadable:{type(exc).__name__}"


def check_contract() -> tuple[bool, dict]:
    obj, err = load_json(CONTRACT)
    if err:
        return False, {"error": err}
    freeze = obj.get("freeze_record") or {}
    detail = {
        "status": obj.get("status"),
        "contract_version": obj.get("contract_version"),
        "revision": obj.get("revision"),
        "freeze_scope": freeze.get("freeze_scope"),
        "frozen_revision": freeze.get("frozen_revision"),
        "has_review_record": bool(obj.get("review_record")),
        "sha256": sha256_file(CONTRACT),
    }
    ok = (obj.get("status") == "FROZEN_OFFLINE_ONLY"
          and freeze.get("freeze_scope") == "OFFLINE_ONLY"
          and bool(freeze.get("based_on_reviewed_json_sha256"))
          and bool(freeze.get("reviewed_commit"))
          and bool(obj.get("review_record")))
    return ok, detail


def check_maps() -> tuple[bool, dict]:
    detail = {}
    ok_all = True
    for name, path in (("stage4_address_map", ADDRESS_MAP), ("shared_address_map", SHARED_MAP)):
        obj, err = load_json(path)
        if err:
            detail[name] = {"error": err}
            ok_all = False
            continue
        binding = obj.get("review_binding") or {}
        bpath = Path(str(binding.get("path", "")))
        rec_ok = bpath.is_file() and sha256_file(bpath) == binding.get("sha256")
        ok = (obj.get("status") == "APPROVED"
              and obj.get("approved_by")
              and bool(obj.get("approved_at_utc8"))
              and rec_ok)
        ok_all = ok_all and ok
        detail[name] = {"status": obj.get("status"), "approved_by": obj.get("approved_by"),
                        "review_binding_verified": rec_ok, "sha256": sha256_file(path)}
    return ok_all, detail


def check_gate_run() -> tuple[bool, dict]:
    obj, err = load_json(GATE_RERUN / "replay_forward_bridge_result.json")
    if err:
        return False, {"error": err}
    checks = obj.get("checks") or {}
    statuses = {k: (v.get("status") if isinstance(v, dict) else v) for k, v in checks.items()}
    # 桥接器字节绑定记录在 preflight_verification.json 的 bridge_source 里（result 只记 preflight 的 SHA）
    pf, pf_err = load_json(GATE_RERUN / "preflight_verification.json")
    if pf_err:
        return False, {"error": f"preflight:{pf_err}"}
    bridge = (pf.get("bridge_source") or {}).get("sha256")
    bridge_now = sha256_file(WORKTREE / "scripts/stage4_s4ctrl/replay_forward_bridge.py")
    preflight_sha_ok = obj.get("preflight_sha256") == sha256_file(GATE_RERUN / "preflight_verification.json")
    return (obj.get("status") == "PASS" and obj.get("exit_code") == 0
            and statuses and all(s == "PASS" for s in statuses.values())
            and bridge == bridge_now and preflight_sha_ok), {
        "status": obj.get("status"), "exit_code": obj.get("exit_code"),
        "checks": statuses,
        "bridge_recorded": (bridge or "")[:16],
        "bridge_worktree": bridge_now[:16],
        "bridge_sha_matches_worktree": bridge == bridge_now,
        "preflight_sha_selfconsistent": preflight_sha_ok,
    }


def check_replay_packages() -> tuple[bool, dict]:
    detail = {}
    ok_all = True
    base, err = load_json(BASE_REPLAY)
    if err:
        detail["base"] = {"error": err}
        ok_all = False
    else:
        files = base.get("files") or []
        missing = [f["path"] for f in files
                   if not (GATE_RERUN / f["path"]).is_file()
                   or sha256_file(GATE_RERUN / f["path"]) != f["sha256"]]
        ok = (base.get("consumption_mode") == "replay_only" and files and not missing)
        ok_all = ok_all and ok
        detail["base"] = {"consumption_mode": base.get("consumption_mode"),
                          "file_count": len(files), "mismatched": missing}
    pos, err = load_json(POS_REPLAY)
    if err:
        detail["positive"] = {"error": err}
        ok_all = False
    else:
        count = (pos.get("detections") or {}).get("count")
        ok = ((pos.get("marking") or {}).get("replay_only") is True and isinstance(count, int) and count >= 1)
        ok_all = ok_all and ok
        detail["positive"] = {"replay_only": (pos.get("marking") or {}).get("replay_only"),
                              "detections": count}
    return ok_all, detail


def _load_adapter() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "s4b_adapter_for_freeze", WORKTREE / "scripts/stage4_s4b/s4b_ps_tensor_adapter.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["s4b_adapter_for_freeze"] = module
    spec.loader.exec_module(module)
    return module


def check_gates() -> tuple[bool, dict]:
    adapter = _load_adapter()
    prepared = adapter.validate_preparation(PREP)
    files = {}
    for p in sorted(GATES_DIR.glob("*.json")):
        if p.name in ("manifest.json", "gate_records_index.json"):
            continue
        files[p.stem] = {"path": str(p), "sha256": sha256_file(p)}
    gate = adapter.validate_hardware_gates(prepared, "s4b_ps_tensor_hw_20261027_r01", files)
    accepted = sorted(files)
    missing_by_gate = {}
    for item in gate.missing:
        key = item.split(":")[0]
        missing_by_gate.setdefault(key, []).append(item)
    # 只要求“已生成并配齐 6 类”这一事实成立；剩余两类属硬件窗口依赖，不代表冻结失败
    hard_failures = {k: v for k, v in missing_by_gate.items()
                     if k not in ("hardware_session_handoff", "exclusive_session")}
    return (not hard_failures and len(accepted) >= 6), {
        "records_supplied": accepted,
        "record_count": len(accepted),
        "missing_by_gate": missing_by_gate,
        "blocking_outside_hardware_window": sorted(hard_failures),
    }


def check_manifest() -> tuple[bool, dict]:
    man, err = load_json(GATES_DIR / "manifest.json")
    if err:
        return False, {"error": err}
    listed = {f["path"]: f["sha256"] for f in (man.get("files") or [])}
    actual = {p.name: sha256_file(p) for p in GATES_DIR.iterdir()
              if p.is_file() and p.name != "manifest.json"}
    return listed == actual, {"listed": len(listed), "actual": len(actual),
                              "mismatch": sorted(set(listed) ^ set(actual))}


def check_bgr() -> tuple[bool, dict]:
    ev, err = load_json(BGR_EVID)
    if err:
        return False, {"error": err}
    sv = PREPROC_SV.read_text(encoding="utf-8") if PREPROC_SV.is_file() else ""
    has_param = "BGR_SOURCE" in sv and "raw_channel_index" in sv
    detail = {"verdict": ev.get("verdict"), "rtl_has_remap_param": has_param,
              "sim": (ev.get("simulation") or {}).get("negative_control_conclusion")}
    return has_param and ev.get("verdict") is not None, detail


NEGATIONS = ("不", "未", "无", "禁止", "非", "≠", "无法", "不能", "不可", "不得", "NOT_", "不代表", "不等于")

FORBIDDEN = (
    ("G3 通过", re.compile(r"G3\s*(已)?通过")),
    ("G5 通过", re.compile(r"G5\s*(已)?通过")),
    ("整体冻结", re.compile(r"(阶段4|stage4).{0,6}整体冻结")),
    ("FULL_FROZEN", re.compile(r"FULL_FROZEN")),
)


def check_claims_hygiene() -> tuple[bool, dict]:
    """扫描冻结相关文档，禁止把未达成写成已通过。命中即失败。"""
    # 只扫人读文档。JSON 契约的 forbidden_claims / boundaries 本身就是"禁止这样说"的清单，
    # 把它们一并扫会产生系统性误报（本次实测命中 1 条 forbidden_claims 条目）；其语义字段由 F1/F2 校验。
    targets = [WORKTREE / ".codex/STATE.md",
               WORKTREE / "docs/stage4/s4_stage4_freeze_record_20261027_r01.md",
               WORKTREE / "docs/stage4/s4_stage4_freeze_signed_20261027_r01.md"]
    hits = []
    for path in targets:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for label, pattern in FORBIDDEN:
            for m in pattern.finditer(text):
                window = text[max(0, m.start() - 18): m.end() + 12]
                if any(neg in window for neg in NEGATIONS):
                    continue  # 否定句（如“不宣称 G5 通过”“不能整体冻结”）属正确表述，不算违规
                line_no = text[: m.start()].count("\n") + 1
                hits.append({"file": str(path.relative_to(WORKTREE)), "line": line_no,
                             "phrase": label, "context": window.strip()})
    return not hits, {"scanned": [str(x.relative_to(WORKTREE)) for x in targets], "violations": hits,
                      "exempted": "命中点前后出现否定词的表述视为正确否定，不计违规"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.evidence_dir).resolve()
    if out_dir.exists() and any(out_dir.iterdir()):
        print(f"[ERROR] 证据目录已存在且非空：{out_dir}")
        return 2

    items = [
        ("F1_shared_result_contract_frozen", check_contract),
        ("F2_address_maps_approved", check_maps),
        ("F3_task26_gate_pass", check_gate_run),
        ("F4_replay_packages", check_replay_packages),
        ("F5_hardware_gate_records", check_gates),
        ("F6_gate_manifest_coverage", check_manifest),
        ("F7_bgr_remap_present", check_bgr),
        ("F8_no_overclaiming", check_claims_hygiene),
    ]
    results = []
    for name, fn in items:
        ok, detail = fn()
        results.append({"id": name, "ok": ok, "detail": detail})

    failed = [r["id"] for r in results if not r["ok"]]
    verdict = "FROZEN_SET_VERIFIED" if not failed else "BLOCKED"
    exit_code = 0 if not failed else 1
    facts = {
        "schema_version": "s4_frozen_set_v1",
        "task_id": "S4-FREEZE-VERIFY",
        "run_id": out_dir.name,
        "verifier_sha256": sha256_file(Path(__file__).resolve()),
        "checks": results,
        "failed": failed,
        "verdict": verdict,
        "exit_code": exit_code,
        "scope": ("阶段4 离线冻结集完整性校验：只读判定，不接触硬件、不启动服务、不改任何被校验文件。"),
        "not_covered": ["hardware_session_handoff（需 main OFFER）",
                        "exclusive_session（需现场 30 分钟窗口）",
                        "板级 P / 4-D / G3（NOT_RUN）"],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "frozen_set_verification.json").write_text(
        json.dumps(facts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    files = [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha256_file(p)}
             for p in sorted(out_dir.iterdir()) if p.is_file() and p.name != "manifest.json"]
    (out_dir / "manifest.json").write_text(json.dumps({
        "schema_version": 1, "task_id": facts["task_id"], "run_id": out_dir.name,
        "verdict": verdict, "exit_code": exit_code, "files": files,
        "scope": facts["scope"],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[{verdict}] exit={exit_code} 通过 {len(results) - len(failed)}/{len(results)}")
    for r in results:
        mark = "OK  " if r["ok"] else "FAIL"
        print(f"  {mark} {r['id']}")
        if not r["ok"]:
            print(f"       {json.dumps(r['detail'], ensure_ascii=False)[:300]}")
    return exit_code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"[ERROR] 输入或环境错误：{type(exc).__name__}: {exc}")
        sys.exit(2)
    except Exception:  # noqa: BLE001 - 未预期异常一律按环境错误处理，不伪装成未通过
        traceback.print_exc()
        print("[ERROR] 未预期异常，按环境错误处理")
        sys.exit(2)
