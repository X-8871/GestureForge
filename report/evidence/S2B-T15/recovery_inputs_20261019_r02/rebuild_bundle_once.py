#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证R02恢复包并从全新解包目录执行一次编译和链接。"""
import hashlib, json, re, shutil, subprocess, zipfile
from pathlib import Path, PureWindowsPath

ROOT = Path(__file__).resolve().parents[4]
E = ROOT / "report/evidence/S2B-T15/recovery_inputs_20261019_r02"
T = ROOT / "tmp/2B/S2B-T15/recovery_inputs_20261019_r02/attempt_03"
ZIP = E / "recovery_bundle.zip"
COMPILER = r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-gcc.exe"

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def run(name, cmd, cwd):
    log=E/(name+".log")
    if log.exists(): raise FileExistsError(log)
    p=subprocess.run(cmd,cwd=str(cwd),shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log.write_bytes(("$ "+cmd+"\r\n").encode("utf-8")+p.stdout)
    return p.returncode,log

def main():
    if T.exists(): raise FileExistsError("attempt_03已存在，拒绝覆盖")
    if not ZIP.is_file(): raise FileNotFoundError(ZIP)
    if (E/"machine_result.json").exists() or (E/"command_results.json").exists():
        raise FileExistsError("R02已有结果，拒绝重跑")
    T.mkdir(parents=True)
    extracted=T/"bundle_extract"
    extracted.mkdir()
    with zipfile.ZipFile(ZIP) as z: z.extractall(extracted)
    ws=extracted/"bundle/workspace"
    manifest=json.loads((ws/"manifest.json").read_text(encoding="utf-8"))
    for x in manifest["files"]:
        f=extracted/x["path"]
        if f.stat().st_size!=x["bytes"] or sha(f)!=x["sha256"]: raise RuntimeError("输入绑定失败: "+x["path"])
    fresh=T/"fresh_build"
    command_results=[]
    for app,db_name in (("infer","app_compile_commands.json"),("init","init_compile_commands.json")):
        build=fresh/app
        (build/"CMakeFiles"/(app+".elf.dir")).mkdir(parents=True)
        db=json.loads((ws/"commands"/db_name).read_text(encoding="utf-8"))
        for i,item in enumerate(db):
            cmd=item["command"]
            cmd=cmd.replace("D:/FPGA_Competition/w2b/tmp/2B/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04",str(ws).replace("\\","/"))
            cmd=cmd.replace(r"D:\FPGA_Competition\w2b\tmp\2B\S2B-T15\qualification_r04_xsa_rebuild_20261016_r04",str(ws))
            rc,log=run(f"rebuild_{app}_compile_{i:02d}",cmd,build)
            command_results.append({"kind":"compile","target":app,"index":i,"exit_code":rc,"command":cmd,"log_sha256":sha(log)})
            if rc: raise RuntimeError(f"{app}编译{ i }失败 rc={rc} log={log}")
        raw=json.loads((ws/"commands/link_commands.json").read_text(encoding="utf-8"))[app]
        m=re.search(re.escape(COMPILER)+r"\s+(.*?)(?:\s+&&\s+C:\\WINDOWS|$)",raw,re.I)
        if not m: raise RuntimeError("原始链接命令主体提取失败: "+app)
        cmd=COMPILER+" "+m.group(1)
        cmd=cmd.replace("D:/FPGA_Competition/w2b/tmp/2B/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04",str(ws).replace("\\","/"))
        cmd=cmd.replace(r"D:\FPGA_Competition\w2b\tmp\2B\S2B-T15\qualification_r04_xsa_rebuild_20261016_r04",str(ws))
        rc,log=run(f"rebuild_{app}_link",cmd,build)
        command_results.append({"kind":"link","target":app,"exit_code":rc,"command":cmd,"log_sha256":sha(log)})
        if rc: raise RuntimeError(f"{app}链接失败 rc={rc} log={log}")
    result={"status":"BUILD_OK","bundle_sha256":sha(ZIP),"infer_elf_sha256":sha(fresh/"infer/infer.elf"),"init_elf_sha256":sha(fresh/"init/init.elf"),"build_dir":str(fresh),"compiler":COMPILER,"toolchain_external_dependency":True,"build_invocations":6}
    result_path=E/"machine_result.json"
    if result_path.exists(): raise FileExistsError(result_path)
    result_path.write_text(json.dumps(result,indent=2),encoding="utf-8")
    cp=E/"command_results.json"
    if cp.exists(): raise FileExistsError(cp)
    cp.write_text(json.dumps(command_results,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__": main()
