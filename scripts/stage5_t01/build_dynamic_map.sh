#!/usr/bin/env bash
# S5-T02 隔离构建：把动态映射 C 核心 + 宿主 CLI 用**宿主编译器**构建（不接板卡、不用 Xilinx 工具链）。
# 所有产物落在指定 RunId 隔离目录内（CDX-20261022-014 §6 要求）。
#
# 用法：bash scripts/stage5_t01/build_dynamic_map.sh <隔离目录> [cc]
set -euo pipefail

RUN_DIR="${1:?用法: build_dynamic_map.sh <隔离目录> [cc]}"
CC="${2:-gcc}"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/p1_app"
REPO_ROOT="$(cd "${SRC_DIR}/../../.." && pwd)"
BUILD_DIR="${RUN_DIR}/build"
CFLAGS=(-std=c11 -Wall -Wextra -Werror -O2 -I "${SRC_DIR}")

mkdir -p "${BUILD_DIR}"
LOG="${BUILD_DIR}/build.log"
{
  echo "# S5-T02 隔离构建（宿主）"
  echo "date_utc8=$(date '+%Y-%m-%dT%H:%M:%S+08:00')"
  echo "cc=${CC}"
  echo "cc_version=$("${CC}" --version | head -1)"
  echo "cflags=${CFLAGS[*]}"
  echo "sources=s5_dynamic_map_host.c s5_dynamic_map.c"
} > "${LOG}"

"${CC}" "${CFLAGS[@]}" -o "${BUILD_DIR}/s5_dynamic_map_host" \
  "${SRC_DIR}/s5_dynamic_map_host.c" "${SRC_DIR}/s5_dynamic_map.c" -lm >> "${LOG}" 2>&1
echo "build_exit=0" >> "${LOG}"
BIN="${BUILD_DIR}/s5_dynamic_map_host"
if [ ! -f "${BIN}" ] && [ -f "${BIN}.exe" ]; then BIN="${BIN}.exe"; fi
echo "binary=$(basename "${BIN}")" >> "${LOG}"

python - "$SRC_DIR" "$BUILD_DIR" "$REPO_ROOT" <<'PY' >> "${LOG}" 2>&1 || true
import hashlib, json, pathlib, sys
src, build, repo = (pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]),
                    pathlib.Path(sys.argv[3]))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
manifest = {
    "schema_version": "gestureforge_s5t02_build_v1",
    "cc_version": __import__("subprocess").run(["gcc", "--version"], capture_output=True, text=True).stdout.splitlines()[0],
    "sources": {p.name: {"sha256": sha(p), "bytes": p.stat().st_size}
                for p in sorted(src.glob("s5_dynamic_map*.c")) + sorted(src.glob("s5_dynamic_map*.h"))},
    "binary": {"path": "build/" + (sorted(p.name for p in build.glob("s5_dynamic_map_host*")) or ["?"])[0],
               "sha256": sha(sorted(build.glob("s5_dynamic_map_host*"))[0]),
               "bytes": sorted(build.glob("s5_dynamic_map_host*"))[0].stat().st_size},
    "reference": {"contract_id": "S5A-G0-v2",
                  "path": "verification/s5_display_geometry_reference.py",
                  "sha256": sha(repo / "verification/s5_display_geometry_reference.py")},
    "note": "宿主隔离构建；**不是**板上运行证据。板上项（B1–B10）仍 NOT_RUN。",
}
(build / "build.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
print("build_json=build/build.json")
PY

echo "[build] cc=${CC} out=${BIN}"
echo "build_ok=1"
echo "binary=${BIN}"