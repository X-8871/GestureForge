#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按冻结R04输入制作离线恢复包并在解包目录执行一次真实重建。"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / "report/evidence/S2B-T15/recovery_inputs_20261019_r02"
TMP = ROOT / "tmp/2B/S2B-T15/recovery_inputs_20261019_r02/attempt_01"
OLD = ROOT / "tmp/2B/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04"
ART = ROOT / "report/evidence/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04_artifacts"
COMPILER = Path(r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-gcc.exe")
BASE = Path("bundle/workspace")

def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def log_command(name, command, cwd):
    log = EVIDENCE / (name + ".log")
    if log.exists():
        raise FileExistsError(log)
    p = subprocess.run(command, cwd=str(cwd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log.write_bytes(("$ " + command + "\r\n").encode("utf-8") + p.stdout)
    return p.returncode, log

def main():
    if EVIDENCE.exists() and any(p.name not in {Path(__file__).name, "preparation_failure_01.log"} for p in EVIDENCE.iterdir()):
        raise FileExistsError("R02 evidence目录非空，拒绝覆盖")
    TMP.mkdir(parents=True, exist_ok=False)
    stage = TMP / "staging"
    stage.mkdir()
    ws = stage / BASE
    paths = []
    # 用GCC -M（含-isystem）记录完整头文件解析；R02将收录整个仅512KB的BSP include目录。
    deps = {}
    for app in ("infer", "init"):
        db_name = "app_compile_commands.json" if app == "infer" else "init_compile_commands.json"
        db = json.loads((ART / db_name).read_text(encoding="utf-8-sig"))
        deps[app] = []
        for i, item in enumerate(db):
            cmd = item["command"]
            cmd = cmd.replace(" -MMD -MP", "")
            cmd = re.sub(r"\s-o\s+CMakeFiles\\[^ ]+\s-c\s", " -M ", cmd, count=1)
            cmd = cmd.replace(" -save-temps=obj", "")
            if cmd == item["command"]:
                raise RuntimeError("无法将捕获编译命令转换为GCC -M: " + app)
            rc, log = log_command(f"dependency_{app}_{i:02d}", cmd, Path(item["directory"]))
            if rc:
                raise RuntimeError(f"GCC -M失败 {app}/{i} rc={rc}, log={log}")
            txt = log.read_text(encoding="utf-8", errors="replace")
            # 保存GCC -M完整输出；BSP include目录完整收录，工具链sysroot由安装提供。
            deps[app].extend(re.findall(r"(?m)^\s*([A-Za-z]:/[^\s\\]+(?:/[^\s\\]+)*)", txt))

    def copy(src, rel):
        src = Path(src)
        dst = ws / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        paths.append(dst)

    # 冻结应用源、头、链接脚本和原始编译数据库。
    for name in ("s2b_inference_app.c", "s2a_ps_decode_nms_reference.c", "s2a_ps_decode_nms_reference.h"):
        copy(ART / "source_snapshot" / name, "infer/src/" + name)
    copy(ART / "s2b_inference_platform.h", "infer/src/s2b_inference_platform.h")
    copy(ART / "lscript.ld", "infer/src/lscript.ld")
    for name in ("ps7_init.c", "ps7_init.h", "s2b_ps_init.c"):
        copy(ART / name, "init/src/" + name)
    copy(ART / "init_lscript.ld", "init/src/lscript.ld")
    copy(ART / "app_compile_commands.json", "commands/app_compile_commands.json")
    copy(ART / "init_compile_commands.json", "commands/init_compile_commands.json")
    copy(ART / "infer.elf", "reference/infer.elf")
    copy(ART / "init.elf", "reference/init.elf")
    bsp = OLD / "ps7/export/ps7/sw/cpu0"
    copy(bsp / "Xilinx.spec", "ps7/export/ps7/sw/cpu0/Xilinx.spec")
    for f in (bsp / "include").rglob("*"):
        if f.is_file():
            copy(f, "ps7/export/ps7/sw/cpu0/include/" + f.relative_to(bsp / "include").as_posix())
    libs = {
        "libxilstandalone.a": ROOT / "report/evidence/S2B-T18/formal_review_20261018_r01/runtime/libxilstandalone.a",
        "libxil.a": bsp / "lib/libxil.a",
        "libxiltimer.a": bsp / "lib/libxiltimer.a",
    }
    for name, src in libs.items():
        copy(src, "ps7/export/ps7/sw/cpu0/lib/" + name)
    # 原始Ninja链接命令是R04生成命令的引用；固定命令文本并保留SHA。
    link_commands = {}
    ninja = Path(r"D:\Xilinx\2026.1\Vitis\bin\ninja.exe")
    for app in ("infer", "init"):
        p = subprocess.run([str(ninja), "-C", str(OLD / app / "build"), "-t", "commands", app + ".elf"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if p.returncode:
            raise RuntimeError("ninja -t commands失败: " + app)
        line = next((x for x in p.stdout.splitlines() if re.search(r"-o\s+" + app + r"\.elf\s", x)), None)
        if not line:
            raise RuntimeError("未找到原始ELF链接命令: " + app)
        link_commands[app] = line
    (ws / "commands").mkdir(parents=True, exist_ok=True)
    (ws / "commands/link_commands.json").write_text(json.dumps(link_commands, indent=2), encoding="utf-8")
    paths.append(ws / "commands/link_commands.json")
    (EVIDENCE / "dependency_inventory.json").write_text(json.dumps({"method":"GCC -M; BSP include directory bundled in full", "gcc_dependency_logs":[p.name for p in EVIDENCE.glob("dependency_*.log")], "include_bytes":sum(x.stat().st_size for x in (bsp/"include").rglob("*") if x.is_file()), "include_files":sum(1 for x in (bsp/"include").rglob("*") if x.is_file()), "resolved_bsp_headers":[x for x in deps["infer"]+deps["init"] if "cpu0" in x and "include" in x]}, indent=2), encoding="utf-8")
    manifest = {"schema":1,"source_commit":"03faa2d47a6e49d7475e387cf6b33edda4962c68","xsa_sha256":"ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6","note":"仅PS infer/init离线编译链接输入；工具链为外部依赖；不含完整BSP生成器/SDK/PL重建输入。", "files":[]}
    for f in sorted(paths):
        manifest["files"].append({"path":f.relative_to(stage).as_posix(),"bytes":f.stat().st_size,"sha256":sha(f)})
    mf = ws / "manifest.json"
    mf.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    zpath = EVIDENCE / "recovery_bundle.zip"
    with zipfile.ZipFile(zpath, "x", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(ws.rglob("*")):
            if f.is_file(): z.write(f, f.relative_to(stage).as_posix())
    shutil.copyfile(mf, EVIDENCE / "bundle_manifest.json")
    extract = TMP / "bundle_extract"
    extract.mkdir()
    with zipfile.ZipFile(zpath) as z: z.extractall(extract)
    # 检查ZIP解包文件绑定后再编译。
    m = json.loads((extract / "bundle/workspace/manifest.json").read_text(encoding="utf-8"))
    for item in m["files"]:
        f = extract / item["path"]
        if f.stat().st_size != item["bytes"] or sha(f) != item["sha256"]:
            raise RuntimeError("包内输入哈希不符: " + item["path"])
    fresh = TMP / "fresh_build"
    for app in ("infer", "init"):
        (fresh / app / "CMakeFiles" / (app + ".elf.dir")).mkdir(parents=True)
        db = json.loads((extract / "bundle/workspace/commands" / ("app_compile_commands.json" if app=="infer" else "init_compile_commands.json")).read_text(encoding="utf-8"))
        for i, item in enumerate(db):
            cmd = item["command"].replace(str(OLD).replace("\\","/"), str(extract / "bundle/workspace").replace("\\","/"))
            cmd = cmd.replace(str(OLD), str(extract / "bundle/workspace"))
            cmd = re.sub(r"\s-o\s+CMakeFiles\\[^ ]+\s-c\s", lambda m: " -o " + item["output"].replace("/", "\\") + " -c ", cmd, count=1)
            rc, log = log_command(f"build_{app}_{i:02d}", cmd, fresh / app)
            if rc: raise RuntimeError(f"编译失败 {app}/{i} rc={rc}, log={log}")
        # 使用捕获的原始链接参数序列，不调用生成器；路径实参替换到解包副本。
        link = link_commands[app]
        # ninja捕获的命令行有cmd wrapper和后处理；提取gcc实际命令主体。
        mlink = re.search(r"(?:&&\s*)?" + re.escape(str(COMPILER)) + r"\s+(.*?)(?:\s+&&\s+C:\\WINDOWS|$)", link, re.I)
        if not mlink:
            raise RuntimeError("不能识别捕获链接命令主体: " + app)
        lcmd = str(COMPILER) + " " + mlink.group(1)
        lcmd = lcmd.replace(str(OLD).replace("\\","/"), str(extract / "bundle/workspace").replace("\\","/"))
        lcmd = lcmd.replace(str(OLD), str(extract / "bundle/workspace"))
        rc, log = log_command(f"link_{app}", lcmd, fresh / app)
        if rc: raise RuntimeError(f"链接失败 {app} rc={rc}, log={log}")
    print(json.dumps({"status":"BUILD_OK","bundle_sha256":sha(zpath),"infer_sha256":sha(fresh/"infer/infer.elf"),"init_sha256":sha(fresh/"init/init.elf"),"fresh_build":str(fresh)},indent=2))

if __name__ == "__main__":
    main()
