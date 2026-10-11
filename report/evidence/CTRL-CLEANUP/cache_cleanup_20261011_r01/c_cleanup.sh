set -e
targets=(
'C:\Users\22061\AppData\Local\npm-cache\_cacache\content-v2'
'C:\Users\22061\AppData\Local\npm-cache\_cacache\index-v5'
'C:\Users\22061\AppData\Local\npm-cache\_cacache\tmp'
'C:\Users\22061\AppData\Local\pip\cache\http'
'C:\Users\22061\AppData\Local\pip\cache\http-v2'
'C:\Users\22061\AppData\Local\pip\cache\wheels'
)
resolved=()
df -B1 /c /d
for input in "${targets[@]}"; do
  test -d "$input" && test ! -L "$input"
  target="$(realpath -- "$input")"
  case "$target" in
    C:/Users/22061/AppData/Local/npm-cache/_cacache/content-v2|C:/Users/22061/AppData/Local/npm-cache/_cacache/index-v5|C:/Users/22061/AppData/Local/npm-cache/_cacache/tmp|C:/Users/22061/AppData/Local/pip/cache/http|C:/Users/22061/AppData/Local/pip/cache/http-v2|C:/Users/22061/AppData/Local/pip/cache/wheels) ;;
    *) exit 91;;
  esac
  resolved+=("$target")
  du -sb -- "$target"
done
for target in "${resolved[@]}"; do
  test -d "$target" && test ! -L "$target"
  test "$(realpath -- "$target")" = "$target"
  rm -rf -- "$target"
  test ! -e "$target"
  printf "REMOVED %s\n" "$target"
done
df -B1 /c /d
