#!/usr/bin/env bash
# 本文件是本次授权清理的命令快照；不得自动重复执行。
set -euo pipefail
export PATH=/usr/bin:/bin:/c/Windows/System32:$PATH
task_plan=${1:?必须提供本次精确清单}
task_mode=${2:-verify-only}
task_expected=${GESTUREFORGE_CACHE_PLAN_SHA256:?必须提供本次已审查计划的SHA}
test "$(sha256sum "$task_plan" | cut -d ' ' -f1)" = "$task_expected"

# 只读解析冻结清单；任何解析异常都会在删除前退出。
task_list=$(node -e 'const fs=require("fs");const p=JSON.parse(fs.readFileSync(process.argv[1],"utf8"));if(p.status!=="PLANNED"||p.files.length!==302||p.directories.length!==5)throw Error("计划身份或数量不符");for(const x of p.files){if(/[\r\n\t]/.test(x.path)||!Number.isSafeInteger(x.size))throw Error("条目非法");process.stdout.write("file\t"+x.size+"\t"+x.path+"\n")}for(const x of p.directories){if(/[\r\n\t]/.test(x.path))throw Error("目录非法");process.stdout.write("directory\t"+x.allocated_bytes+"\t"+x.path+"\n")}' "$task_plan")

# 先核验全部精确目标，禁止把缓存白名单扩大为工具、配置或证据目录。
while IFS=$'\t' read -r task_kind task_size task_path; do
  task_resolved=$(realpath -- "$task_path")
  test ! -L "$task_path"
  if test "$task_kind" = file; then
    test -f "$task_path"
    test "$(stat -c %s -- "$task_path")" = "$task_size"
    task_parent=$(dirname -- "$task_resolved")
    task_name=${task_resolved##*/}
    case "$task_parent" in
      'C:/Espressif/dist') case "$task_name" in *.zip|*.tar.xz|*.tar.gz) ;; *) exit 91 ;; esac ;;
      'C:/Users/22061/anaconda3/pkgs')
        case "$task_name" in *.tar.bz2) task_stem=${task_name%.tar.bz2} ;; *.conda) task_stem=${task_name%.conda} ;; *) exit 92 ;; esac
        test -d "$task_parent/$task_stem"
        test -f "$task_parent/$task_stem/info/index.json"
        ;;
      'C:/Users/22061/AppData/Local/Temp/workbuddy-update-x64') test "$task_name" = 'WorkBuddy-Setup-5.7.7.40774747.exe' ;;
      *) exit 93 ;;
    esac
  else
    test "$task_kind" = directory && test -d "$task_path"
    case "$task_resolved" in
      'C:/Users/22061/.gemini/antigravity-browser-profile/Default/Cache'|'C:/Users/22061/.gemini/antigravity-browser-profile/Default/Code Cache'|'C:/Users/22061/.workbuddy/app/CodeCache'|'C:/Users/22061/AppData/Local/JianyingPro/User Data/CEF/Cache/Cache'|'C:/Users/22061/AppData/Local/JianyingPro/User Data/CEF/Cache/Code Cache') ;;
      *) exit 94 ;;
    esac
  fi
done <<< "$task_list"
printf 'ALL_TARGETS_VERIFIED files=302 directories=5\n'
case "$task_mode" in
  verify-only) printf 'VERIFY_ONLY_NO_DELETE\n'; exit 0 ;;
  execute-once) ;;
  *) exit 95 ;;
esac
df -B1 /c

# 文件命令只在Git Bash内执行；仅删除已逐项核验的307个目标。
task_removed_files=0
task_removed_dirs=0
while IFS=$'\t' read -r task_kind task_size task_path; do
  task_resolved=$(realpath -- "$task_path")
  if test "$task_kind" = file; then
    rm -f -- "$task_resolved"
    task_removed_files=$((task_removed_files + 1))
  else
    rm -rf -- "$task_resolved"
    task_removed_dirs=$((task_removed_dirs + 1))
  fi
  test ! -e "$task_resolved"
done <<< "$task_list"
printf 'REMOVED_FILES=%s REMOVED_DIRS=%s\n' "$task_removed_files" "$task_removed_dirs"
df -B1 /c /d
