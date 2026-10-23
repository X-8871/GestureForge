#!/bin/bash
# 克隆内独立复核：自检 / 两检查器 / PENDING 注入 / 自证工具 复现
set -u
ROOT=/d/FPGA_Competition/tmp/review/FREEZE_DELTA_D_20261023_r01
CLONE=$ROOT/clone/w6_transport
export TMP=$ROOT/temp TMPDIR=$ROOT/temp TEMP=$ROOT/temp
mkdir -p "$TMP"
cd "$CLONE" || exit 2
PY=python
RUN=report/evidence/S6-A/s6a_g0_20261023_r11
echo "### clone HEAD: $(git rev-parse HEAD)"

echo "=== [1] S6-A 自检（r11 清单，克隆内） ==="
$PY -B verification/s6_g0_selfcheck.py \
  --json docs/stage6/s6a_stage6_g0_behavior_v1.json \
  --doc docs/stage6/S6A_stage6_g0_behavior_spec_v1.md \
  --cases "$RUN/hand_computed_cases.json" \
  --upstream "$RUN/upstream_bindings.json" \
  --out "$ROOT/clone_selfcheck_r11.json" \
  --project-root "$CLONE" --evidence-dir "$CLONE/$RUN" \
  --manifest "$CLONE/$RUN/delivery_manifest.json" --state .codex/STATE.md
echo "REAL_EXIT_SELFCHECK=$?"

echo "=== [2] check_stage_delivery --mode evidence（r11） ==="
$PY -B verification/check_stage_delivery.py --mode evidence \
  --manifest "$CLONE/$RUN/delivery_manifest.json" --project-root "$CLONE"
echo "REAL_EXIT_EVIDENCE=$?"

echo "=== [3] check_stage_delivery --mode inputs（r11） ==="
$PY -B verification/check_stage_delivery.py --mode inputs \
  --manifest "$CLONE/$RUN/inputs_manifest.json" --project-root "$CLONE"
echo "REAL_EXIT_INPUTS=$?"

echo "=== [4] 出库工具 approval_regression.py（克隆内） ==="
$PY -B verification/approval_regression.py --project-root "$CLONE" --run-dir "$RUN" \
  --out "$ROOT/clone_approval_regression.json"
echo "REAL_EXIT_APPROVAL_REGRESSION_TOOL=$?"

echo "=== [5] 我自己制造的 PENDING 注入（独立于出库工具） ==="
INJ=$ROOT/inject_pending
rm -rf "$INJ"; mkdir -p "$INJ/.codex"
for d in docs verification src; do cp -r "$CLONE/$d" "$INJ/$d"; done
mkdir -p "$INJ/report/evidence"
cp -r "$CLONE/$RUN" "$INJ/$RUN"
cp "$CLONE/.codex/STATE.md" "$INJ/.codex/STATE.md"
$PY -B - "$INJ" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1]) / "docs/stage6/s6a_stage6_g0_behavior_v1.json"
d = json.loads(p.read_text(encoding="utf-8"))
print("inject target:", d["parameters"][2]["id"], "was", d["parameters"][2]["approval_status"])
d["parameters"][2]["approval_status"] = "PENDING_APPROVAL"
p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
$PY -B verification/s6_g0_selfcheck.py \
  --json docs/stage6/s6a_stage6_g0_behavior_v1.json \
  --doc docs/stage6/S6A_stage6_g0_behavior_spec_v1.md \
  --cases "$RUN/hand_computed_cases.json" \
  --upstream "$RUN/upstream_bindings.json" \
  --out "$ROOT/inject_pending_selfcheck.json" \
  --project-root "$INJ" --evidence-dir "$INJ/$RUN" \
  --manifest "$INJ/$RUN/delivery_manifest.json" --state .codex/STATE.md
echo "REAL_EXIT_MY_INJECT=$?"
$PY -B - "$ROOT/inject_pending_selfcheck.json" <<'PY'
import json, pathlib, sys
d = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
c4 = next(c for c in d["checks"] if c["id"] == "C4")
print("INJECTED status:", d["status"], "| C4:", c4["status"], "|", c4["detail"])
PY

echo "=== [6] 克隆内跑 export_selfproof（S6-A 剖面，--commit F5） ==="
$PY -B verification/export_selfproof.py --project-root "$CLONE" \
  --commit caa9728af84b0a5b79bed17427eec0091b922923 \
  --out "$ROOT/clone_export_selfproof.json" --markdown "$ROOT/clone_export_selfproof.md"
echo "REAL_EXIT_EXPORT_SELFPROOF=$?"
$PY -B - "$ROOT/clone_export_selfproof.json" <<'PY'
import json, pathlib, sys
d = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
print("verdict:", d["verdict"])
for s in d["subjects"]:
    print(" subject:", s["subject"], "->", s["verdict"], "run_id=", s.get("run_id"),
          "exit_codes=", [c.get("exit_code") for c in s.get("checks", [])])
PY

echo "=== [7] r11 包外：S6-A 证据包与参数批准字段核对 ==="
$PY -B - "$CLONE" <<'PY'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
j = json.loads((root / "docs/stage6/s6a_stage6_g0_behavior_v1.json").read_text(encoding="utf-8"))
rec = j["approval_record"]
print("top status:", j["status"], "| artifact_version:", j["artifact_version"], "| json run_id:", j["run_id"])
print("approval_record.receipt:", rec["receipt"], "| date:", rec["date"], "| words:", rec["user_words"])
bad = [p["id"] for p in j["parameters"] if p.get("approval_ref") != rec["receipt"]]
bad2 = [p["id"] for p in j["parameters"] if p.get("approval_status") != "APPROVED_20261023"]
print("params !=ref:", bad, "| params !=APPROVED:", bad2, "| n:", len(j["parameters"]))
print("receipt exists in clone tree:", (root / rec["receipt"]).is_file())
for pid in ("T6-K01", "T6-C01", "T6-S02"):
    p = next(x for x in j["parameters"] if x["id"] == pid)
    print(f"  sample {pid}: value={p['draft_value']} status={p['approval_status']} ref={p['approval_ref']}")
# S6-B 侧：快照字段
for rel in ("report/evidence/S6-B/s6b_core_20261023_r06/run_report.json",
            "report/evidence/S6-B/s6b_core_20261023_r06/params_snapshot.json"):
    p = root / rel
    if p.is_file():
        t = p.read_text(encoding="utf-8")
        print(f"  {rel}: all_parameters_pending_approval present={('all_parameters_pending_approval' in t)}",
              "pending_true=", '"all_parameters_pending_approval": true' in t,
              "PENDING_APPROVAL_count=", t.count("PENDING_APPROVAL"))
PY
echo "=== done ==="