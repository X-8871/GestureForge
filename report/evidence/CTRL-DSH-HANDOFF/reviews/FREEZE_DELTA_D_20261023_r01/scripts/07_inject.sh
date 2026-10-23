#!/bin/bash
# 我自己制造的 PENDING 注入（独立复核 C4 判别力）；写死绝对路径，避免相对路径回落
set -u
ROOT=/d/FPGA_Competition/tmp/review/FREEZE_DELTA_D_20261023_r01
CLONE=$ROOT/clone/w6_transport
export TMP=$ROOT/temp TMPDIR=$ROOT/temp TEMP=$ROOT/temp
mkdir -p "$TMP"
RUN=report/evidence/S6-A/s6a_g0_20261023_r11
PY=python

run_inject () {
  local tag="$1"; local target="$2"
  local INJ=$ROOT/inject_$tag
  rm -rf "$INJ"; mkdir -p "$INJ/.codex" "$INJ/report/evidence/S6-A"
  cp -r "$CLONE/docs" "$CLONE/verification" "$CLONE/src" "$INJ/"
  cp -r "$CLONE/$RUN" "$INJ/$RUN"
  cp "$CLONE/.codex/STATE.md" "$INJ/.codex/STATE.md"
  $PY -B - "$INJ" "$target" <<'PY'
import json, pathlib, sys
root, target = sys.argv[1], sys.argv[2]
p = pathlib.Path(root) / "docs/stage6/s6a_stage6_g0_behavior_v1.json"
d = json.loads(p.read_text(encoding="utf-8"))
if target == "map_status":
    print("inject map_status: was", d["actions"]["map_status"])
    d["actions"]["map_status"] = "PENDING_APPROVAL"
elif target == "approval_ref_missing":
    print("inject remove approval_ref from parameters[5]:", d["parameters"][5]["id"])
    d["parameters"][5].pop("approval_ref", None)
else:
    p0 = d["parameters"][2]
    print("inject param:", p0["id"], "was", p0["approval_status"])
    p0["approval_status"] = "PENDING_APPROVAL"
p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
  cd "$INJ" || return 2
  $PY -B "$INJ/verification/s6_g0_selfcheck.py" \
    --json "$INJ/docs/stage6/s6a_stage6_g0_behavior_v1.json" \
    --doc "$INJ/docs/stage6/S6A_stage6_g0_behavior_spec_v1.md" \
    --cases "$INJ/$RUN/hand_computed_cases.json" \
    --upstream "$INJ/$RUN/upstream_bindings.json" \
    --out "$ROOT/inject_${tag}_selfcheck.json" \
    --project-root "$INJ" --evidence-dir "$INJ/$RUN" \
    --manifest "$INJ/$RUN/delivery_manifest.json" --state .codex/STATE.md > "$ROOT/inject_${tag}_stdout.txt" 2>&1
  local code=$?
  echo "REAL_EXIT_MY_INJECT_$tag=$code"
  $PY -B - "$ROOT/inject_${tag}_selfcheck.json" "$tag" <<'PY'
import json, pathlib, sys
d = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
c4 = next(c for c in d["checks"] if c["id"] == "C4")
print("  overall:", d["status"], "| C4:", c4["status"], "| n_checks_failed:",
      sum(1 for c in d["checks"] if c["status"] != "PASS"))
print("  C4 detail(utf8):", c4["detail"].encode("unicode_escape").decode("ascii"))
PY
  cd "$CLONE" || return 2
}

echo "=== A) 注入 parameters[2]=T6-A03 -> PENDING_APPROVAL ==="
run_inject param2 param
echo "=== B) 注入 actions.map_status -> PENDING_APPROVAL ==="
run_inject mapstatus map_status
echo "=== C) 删除 parameters[5].approval_ref（批准索引缺失） ==="
run_inject noref approval_ref_missing
echo "=== D) 基线（未注入，同一复制流程）对照 ==="
INJ=$ROOT/inject_baseline
rm -rf "$INJ"; mkdir -p "$INJ/.codex" "$INJ/report/evidence/S6-A"
cp -r "$CLONE/docs" "$CLONE/verification" "$CLONE/src" "$INJ/"
cp -r "$CLONE/$RUN" "$INJ/$RUN"
cp "$CLONE/.codex/STATE.md" "$INJ/.codex/STATE.md"
cd "$INJ" || exit 2
$PY -B "$INJ/verification/s6_g0_selfcheck.py" \
  --json "$INJ/docs/stage6/s6a_stage6_g0_behavior_v1.json" \
  --doc "$INJ/docs/stage6/S6A_stage6_g0_behavior_spec_v1.md" \
  --cases "$INJ/$RUN/hand_computed_cases.json" \
  --upstream "$INJ/$RUN/upstream_bindings.json" \
  --out "$ROOT/inject_baseline_selfcheck.json" \
  --project-root "$INJ" --evidence-dir "$INJ/$RUN" \
  --manifest "$INJ/$RUN/delivery_manifest.json" --state .codex/STATE.md > "$ROOT/inject_baseline_stdout.txt" 2>&1
echo "REAL_EXIT_BASELINE_COPY=$?"
$PY -B - "$ROOT/inject_baseline_selfcheck.json" <<'PY'
import json, pathlib, sys
d = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
print("  overall:", d["status"], "| failed:", [c["id"] for c in d["checks"] if c["status"] != "PASS"])
PY
cd "$CLONE" || exit 2
echo "=== S6-B r06 参数快照字段（机器可读） ==="
$PY -B - "$CLONE" <<'PY'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
p = root / "report/evidence/S6-B/s6b_core_20261023_r06/params_snapshot.json"
d = json.loads(p.read_text(encoding="utf-8"))
print("snapshot keys:", sorted(d))
print("all_parameters_pending_approval =", d.get("all_parameters_pending_approval"))
print("thresholds_are_draft_not_approved =", d.get("thresholds_are_draft_not_approved"))
print("note =", d.get("note"))
print("first param:", d.get("parameters", [{}])[0])
PY
echo "=== done ==="