set -e
input='D:\FPGA_Competition\report\evidence\S2A-T68\candidate8x8_109_20261006_130252\runs'
root="$(realpath -- "$input")"
test "$root" = "D:/FPGA_Competition/report/evidence/S2A-T68/candidate8x8_109_20261006_130252/runs"
resolved=()
removed_bytes=0
df -B1 /c /d
for i in {0..108}; do
  sample="$(printf "sample_%03d" "$i")"
  if (( i <= 24 )); then run=candidate8x8_109_20261006_130252; else run=candidate8x8_109_resume_20261007_023531; fi
  build="$root/$sample/$run/build"
  test -d "$build" && test ! -L "$build"
  test "$(realpath -- "$build")" = "$build"
  for name in Vtb_s2a_network_backend_golden__pch.h.fast.gch Vtb_s2a_network_backend_golden__pch.h.slow.gch; do
    file="$build/$name"
    test -f "$file" && test ! -L "$file"
    test "$(realpath -- "$file")" = "$file"
    size="$(stat -c %s -- "$file")"
    removed_bytes=$((removed_bytes+size))
    resolved+=("$file")
  done
done
test "${#resolved[@]}" = 218
test "$removed_bytes" = 31633309006
for file in "${resolved[@]}"; do
  test -f "$file" && test ! -L "$file"
  test "$(realpath -- "$file")" = "$file"
  rm -f -- "$file"
  test ! -e "$file"
done
printf "REMOVED_FILES=%s LOGICAL_BYTES=%s\n" "${#resolved[@]}" "$removed_bytes"
df -B1 /c /d
