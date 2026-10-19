#!/usr/bin/env bash
# 阶段3 T03 板测下载（Git Bash + Vivado xsdb）。只做易失性 JTAG 下载：PL bitstream + PS 初始化 + ELF。
# 用法: bash run_jtag_download_t03.sh <run_dir> <elf_path> [bit_path] [log_subdir]
set -u

RUN_DIR="${1:?需要 run_dir}"
ELF="${2:?需要 ELF 路径}"
BIT_ARG="${3:-}"
LOG_SUBDIR="${4:-jtag_download}"

WT="D:/codex-worktrees/dbdf"
if [ -n "$BIT_ARG" ]; then
  BIT="$BIT_ARG"
else
  BIT="$(ls -1 "$RUN_DIR"/project/*.runs/impl_1/design_1_wrapper.bit 2>/dev/null | head -1)"
fi
XSA="$RUN_DIR/design_1_wrapper.xsa"
PS7="$RUN_DIR/ps7_init.tcl"
LOG_DIR="$RUN_DIR/$LOG_SUBDIR"

echo "RUN_DIR=$RUN_DIR"
echo "BIT=$BIT"
echo "XSA=$XSA"
echo "ELF=$ELF"

[ -f "$BIT" ] || { echo "FAIL=bit_missing"; exit 3; }
[ -f "$XSA" ] || { echo "FAIL=xsa_missing"; exit 3; }
[ -f "$ELF" ] || { echo "FAIL=elf_missing"; exit 3; }
mkdir -p "$LOG_DIR" || { echo "FAIL=mkdir"; exit 3; }

# 从 XSA 解出 ps7_init.tcl（XSA 为 zip）
python - "$XSA" "$PS7" <<'PY' || { echo "FAIL=ps7_init_extract"; exit 3; }
import sys, zipfile
xsa, out = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(xsa) as z:
    names = [n for n in z.namelist() if n.endswith("ps7_init.tcl")]
    if not names:
        print("NO_PS7_INIT_IN_XSA"); sys.exit(2)
    data = z.read(names[0])
open(out, "wb").write(data)
print(f"PS7_INIT_EXTRACTED={out} bytes={len(data)} from={names[0]}")
PY

sha256sum "$BIT" "$XSA" "$ELF" "$PS7" | tee "$LOG_DIR/input_hashes.txt"

bash "$WT/scripts/stage3_t03b/run_xsdb.sh" \
  "D:\\codex-worktrees\\dbdf\\scripts\\stage3_t03b\\jtag_download_t03.tcl" \
  "$(cygpath -w "$BIT")" "$(cygpath -w "$XSA")" "$(cygpath -w "$ELF")" "$(cygpath -w "$PS7")" \
  2>&1 | tee "$LOG_DIR/download.log"
rc=${PIPESTATUS[0]}
echo "DOWNLOAD_EXIT=$rc"
exit "$rc"