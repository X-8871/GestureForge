#!/bin/bash
# 自证记录与 run_id 漂移核对
set -u
cd /d/codex-worktrees/w6 || exit 2
echo "=== behavior json run_id: F4 / F5 / HEAD ==="
for rev in 6b8e5f2a caa9728a c7ae6b49; do
  printf '%s: %s\n' "$rev" "$(git show "$rev:docs/stage6/s6a_stage6_g0_behavior_v1.json" | grep -m1 '"run_id"')"
done
echo "=== r10_selfproof/export_selfproof.json (key lines) ==="
grep -n '"run_id"\|"evidence_dir"\|"verdict"\|"subject"' report/evidence/S6-A/s6a_g0_20261023_r10_selfproof/export_selfproof.json | head -20
echo "=== mismatch count r10_selfproof ==="
grep -o 'SHA-256 不匹配' report/evidence/S6-A/s6a_g0_20261023_r10_selfproof/export_selfproof.json | wc -l
echo "=== mismatch count r11_selfproof ==="
grep -o 'SHA-256 不匹配' report/evidence/S6-A/s6a_g0_20261023_r11_selfproof/export_selfproof.json | wc -l
echo "=== r11_selfproof/transport_clone_selfproof.md ==="
cat report/evidence/S6-A/s6a_g0_20261023_r11_selfproof/transport_clone_selfproof.md
echo "=== r10 delivery_manifest files[0],[1],[7],[9] paths ==="
python -B - <<'PY'
import json, pathlib
p = pathlib.Path("report/evidence/S6-A/s6a_g0_20261023_r10/delivery_manifest.json")
d = json.loads(p.read_text(encoding="utf-8"))
for i in (0, 1, 7, 9):
    f = d["files"][i]
    print(i, f.get("path"), f.get("role"), f.get("sha256"))
print("total files:", len(d["files"]))
PY
echo "=== S6-A r11 manifest hash for spec doc / json ==="
python -B - <<'PY'
import json, pathlib
p = pathlib.Path("report/evidence/S6-A/s6a_g0_20261023_r11/delivery_manifest.json")
d = json.loads(p.read_text(encoding="utf-8"))
for f in d["files"]:
    if f.get("path") in ("docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
                         "docs/stage6/s6a_stage6_g0_behavior_v1.json"):
        print(f["path"], f.get("sha256"))
print("total files:", len(d["files"]))
PY
echo "=== done ==="