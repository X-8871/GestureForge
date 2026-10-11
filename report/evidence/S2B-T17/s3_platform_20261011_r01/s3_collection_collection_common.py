"""S3 已结束运行的精确路径与原字节封存工具。"""
from pathlib import Path
import hashlib,json,subprocess,time,sys,os

ROOT=Path(__file__).absolute().parents[4]
CACHE=Path(__file__).absolute().parent
REPORT=ROOT/"report/evidence/S2B-T17/s3_platform_20261011_r01"
PRE=ROOT/"report/evidence/S2B-T17/s3_source_preflight_20261011_r01"
PROJECT=ROOT/"tmp/2B/S2B-T17/s3p1"
BASELINE="f3a0b0514c90983c41c8729b93f18d627bfc1bb5"
CHECKER_SHA="cf640f8202a673319d45a573584e854aefd71dd08226091b96fdbdfd76983dbf"

def require(condition,message):
    """失败即时保留，不覆盖旧输出或放宽字节门禁。"""
    if not condition: raise RuntimeError(message)

def exact(path,kind="file"):
    """复用已验证路径对象；拒绝链接与错误类型。"""
    require(not path.is_symlink() and (path.is_file() if kind=="file" else path.is_dir()),str(path))
    return path

def sha(path):
    """流式读取原件，不转码或复制大型缓存。"""
    h=hashlib.sha256()
    with exact(path).open("rb") as src:
        for block in iter(lambda:src.read(1048576),b""): h.update(block)
    return h.hexdigest()

def rel(path): return path.relative_to(ROOT).as_posix()
def read(path): return json.loads(exact(path).read_text(encoding="utf-8"))
def binding(path): return {"path":rel(path),"sha256":sha(path),"bytes":path.stat().st_size}

def save(path,value):
    """只创建新 UTF-8 JSON 原件。"""
    exact(path.parent,"directory");require(not path.exists(),"输出已存在："+str(path))
    with path.open("x",encoding="utf-8",newline="\n") as out:
        json.dump(value,out,ensure_ascii=False,indent=2);out.write("\n")

def rawcopy(source,target):
    """副本必须原字节相同；禁止覆盖任何已有目标。"""
    exact(source);exact(target.parent,"directory");require(not target.exists(),"副本已存在："+str(target))
    before=binding(source)
    with source.open("rb") as src,target.open("xb") as out:
        for block in iter(lambda:src.read(1048576),b""): out.write(block)
    after=binding(source);copied=binding(target)
    require(before==after and before["sha256"]==copied["sha256"] and before["bytes"]==copied["bytes"],"rawcopy变动")
    return {"original_path":str(source),"saved_path":rel(target),"sha256":copied["sha256"],"bytes":copied["bytes"]}

def mkdir_new(path):
    """新目录先核对精确父路径与名称。"""
    exact(path.parent,"directory");require(not path.exists(),"目录已存在："+str(path));path.mkdir();return exact(path,"directory")

def original_check():
    """仅核验本次冻结的已有原件，不读取活动 S4 工程源。"""
    items=read(REPORT/"s3_collection_original_inventory.json")["files"]
    for row in items: require(binding(ROOT/row["path"])==row,"已有原件漂移："+row["path"])
    return items

def run_closed(command,prefix,where=REPORT):
    """保存真实原生退出码与已关闭 stdout/stderr；不归一化为宿主码。"""
    started=time.monotonic();proc=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=45,env=dict(os.environ,PYTHONIOENCODING="utf-8"))
    paths=[]
    for suffix,raw in (("stdout.log",proc.stdout),("stderr.log",proc.stderr)):
        p=where/(prefix+"."+suffix);require(not p.exists(),"日志已存在")
        with p.open("xb") as out: out.write(raw)
        paths.append(binding(p))
    record={"command":command,"native_exit_code":proc.returncode,"elapsed_seconds":time.monotonic()-started,"closed_logs":paths,"peak_memory_bytes":None}
    save(where/(prefix+".native.json"),record);return record

def manifest_files():
    """当前 Run 所有原件，外部快照只能作为输入。"""
    rows=[]
    for directory in (REPORT,PRE):
        for p in sorted(directory.rglob("*")):
            if not p.is_file(): continue
            exact(p)
            role="input" if directory==PRE else "source" if p.suffix in (".py",".sv",".v",".tcl",".xdc") else "log" if p.suffix in (".log",".rpt",".jou") else "artifact" if p.suffix in (".xsa",".bd",".rst","") else "result"
            rows.append({**binding(p),"role":role})
    return rows
