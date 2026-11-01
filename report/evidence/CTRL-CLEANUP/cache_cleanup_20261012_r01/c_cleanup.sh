#!/usr/bin/env bash
# 本文件是本次授权清理快照，默认只核验，不得自动重复执行。
set -euo pipefail
export PATH=/usr/bin:/bin:/c/Windows/System32:$PATH
task_plan=${1:?必须指定冻结清单}
task_mode=${2:-verify-only}
task_expected=${GESTUREFORGE_CACHE_PLAN_SHA256:?必须指定已审查清单SHA}
test "$(sha256sum -- "$task_plan" | cut -d ' ' -f1)" = "$task_expected"
task_here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# 机器清单仅作为数据解析，先验证独立白名单、类型、唯一性和摘要格式。
task_paths_text=$(node -e '
const fs=require("fs"),p=JSON.parse(fs.readFileSync(process.argv[1],"utf8"));
const hp=["C:\\SWSetup\\sp160053\\Application","C:\\SWSetup\\sp160053\\Driver","C:\\SWSetup\\sp160053\\uwp"];
const suffixes=["@genieworkbuddy-desktop-updater\\installer.exe","bilibili-updater\\installer.exe","bilibili-updater\\pending\\bilibili-setup-v1.17.5.exe","douyin-downloader-desktop-updater\\installer.exe","dsh-desktop-updater\\installer.exe","mchosehub-updater\\installer.exe","mineradio-updater\\installer.exe","mojie-updater\\installer.exe","tiktok-downloader-updater\\installer.exe"];
const updates=new Set(suffixes.map(x=>"C:\\Users\\22061\\AppData\\Local\\"+x)),seen=new Set();
if(p.status!=="PLANNED"||p.run_id!=="cache_cleanup_20261012_r01"||p.files.length!==1470||p.delete_directories.length)throw Error("计划身份或数量不符");
for(const x of p.files){
 if(x.type!=="file"||/[\r\n\t]/.test(x.path)||!Number.isSafeInteger(x.bytes)||!/^[a-f0-9]{64}$/.test(x.sha256)||seen.has(x.path.toLowerCase()))throw Error("条目非法");
 const inHP=hp.some(r=>x.path.startsWith(r+"\\"));
 if(!inHP&&!updates.has(x.path))throw Error("目标越界");
 if(inHP&&(/\\\.\.?\\/.test(x.path)||/\.(log|etl|evtx|dmp|dump|onnx|pt|pth|safetensors|weights|gguf|mdl|ckpt)$/i.test(x.path)||/\\logs?\\/i.test(x.path)))throw Error("保留内容不能删除");
 seen.add(x.path.toLowerCase());process.stdout.write(x.path+"\n");
}' "$task_plan")
mapfile -t task_paths <<< "$task_paths_text"
test "${#task_paths[@]}" = 1470
# 单进程批量核验摘要，避免为每个文件反复启动工具。
task_checks=$(node -e 'const fs=require("fs"),p=JSON.parse(fs.readFileSync(process.argv[1],"utf8"));for(const x of p.files)process.stdout.write(x.sha256+" *"+x.path+"\n");' "$task_plan")
sha256sum -c --status <<< "$task_checks"
# Windows重解析点、安装进程与服务只能通过原生接口可靠核验；此步骤只读。
MSYS_NO_PATHCONV=1 /c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -File "$(cygpath -w "$task_here/preflight_guard.ps1")" -Plan "$(cygpath -w "$task_plan")"
printf 'ALL_TARGETS_VERIFIED files=1470 directories_to_delete=0\n'
case "$task_mode" in
 verify-only) printf 'VERIFY_ONLY_NO_DELETE\n';exit 0 ;;
 execute-once) ;;
 *) exit 95 ;;
esac
printf 'SPACE_BEFORE\n'
df -B1 /c
# 仅按冻结白名单批量删除普通文件；不递归、不删除目录或通配符匹配内容。
for ((task_i=0;task_i<${#task_paths[@]};task_i+=32)); do
 rm -f -- "${task_paths[@]:task_i:32}"
done
node -e 'const fs=require("fs"),p=JSON.parse(fs.readFileSync(process.argv[1],"utf8"));for(const x of p.files){try{fs.lstatSync(x.path);throw Error("目标仍存在："+x.path);}catch(e){if(e.code!=="ENOENT")throw e;}}console.log("ALL_1470_TARGET_FILES_ABSENT");' "$task_plan"
printf 'SPACE_AFTER\n'
df -B1 /c

