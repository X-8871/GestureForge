"""S4 已关闭原件的精确路径、原字节复制和原生码封存。"""
from pathlib import Path
import hashlib,json,subprocess,time,sys,os

ROOT=Path(__file__).absolute().parents[4]
CACHE=Path(__file__).absolute().parent
REPORT=ROOT/"report/evidence/S2B-T17/s4_platform_20261011_r01"
PRES=[ROOT/"report/evidence/S2B-T17"/f"s4_source_preflight_20261011_r0{i}" for i in (1,2,3)]
PRE=PRES[-1]
PROJECT=ROOT/"tmp/2B/S2B-T17/s4p1"
BASELINE="f96d3e225fd6d92fd33c0407e20c9585c997c870"

def require(condition,message):
    """门禁失败即时停止，不覆盖旧输出。"""
    if not condition:raise RuntimeError(message)

def exact(path,kind="file"):
    """核验精确目标类型，后续复用已核验的对象。"""
    require(not path.is_symlink() and (path.is_file() if kind=="file" else path.is_dir()),str(path))
    return path

def sha(path):
    """流式核验原字节，不转码。"""
    h=hashlib.sha256()
    with exact(path).open("rb") as src:
        for block in iter(lambda:src.read(1048576),b""):h.update(block)
    return h.hexdigest()

def rel(path):return path.relative_to(ROOT).as_posix()
def read(path):return json.loads(exact(path).read_text(encoding="utf-8"))
def binding(path):return {"path":rel(path),"sha256":sha(path),"bytes":path.stat().st_size}

def save(path,value):
    """只创建新 UTF-8 JSON。"""
    exact(path.parent,"directory");require(not path.exists(),"目标已有："+str(path))
    with path.open("x",encoding="utf-8",newline="\n") as out:
        json.dump(value,out,ensure_ascii=False,indent=2);out.write("\n")

def rawcopy(source,target):
    """复制前后核验源、目标哈希和字节数，拒绝覆盖。"""
    exact(source);exact(target.parent,"directory");require(not target.exists(),"副本已有："+str(target))
    before=binding(source)
    with source.open("rb") as src,target.open("xb") as out:
        for block in iter(lambda:src.read(1048576),b""):out.write(block)
    after=binding(source);copied=binding(target)
    require(before==after and before["sha256"]==copied["sha256"] and before["bytes"]==copied["bytes"],"复制时原件漂移")
    return {"original_path":str(source),"saved_path":rel(target),"sha256":copied["sha256"],"bytes":copied["bytes"]}

def mkdir_new(path):
    """创建新目录前核验父目录和新名称。"""
    exact(path.parent,"directory");require(not path.exists(),"目录已有："+str(path));path.mkdir();return exact(path,"directory")

def original_check():
    """只核验 Collector 接手前的全部原件。"""
    rows=read(REPORT/"s4_collection_original_inventory.json")["files"]
    for row in rows:require(binding(ROOT/row["path"])==row,"原件漂移："+row["path"])
    return rows

def git_blob(relative):
    """只消费 f96 的 Git 对象，不消费当前 live 源码。"""
    command=["git","show",BASELINE+":"+relative]
    proc=subprocess.run(command,cwd=ROOT,capture_output=True)
    require(proc.returncode==0,"Git对象不可读："+relative)
    return proc.stdout,command,proc.returncode

def run_closed(command,prefix,where=CACHE):
    """等待轻量命令结束，原生码与 stdout/stderr 独立保存。"""
    started=time.monotonic()
    proc=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=45,env=dict(os.environ,PYTHONIOENCODING="utf-8"))
    logs=[]
    for suffix,raw in (("stdout.log",proc.stdout),("stderr.log",proc.stderr)):
        p=where/(prefix+"."+suffix);require(not p.exists(),"日志已有")
        with p.open("xb") as out:out.write(raw)
        logs.append(binding(p))
    record={"command":command,"native_exit_code":proc.returncode,"elapsed_seconds":time.monotonic()-started,"closed_logs":logs,"peak_memory_bytes":None,"process_tree_peak_memory_bytes":None}
    save(where/(prefix+".native.json"),record);return record

def manifest_files(externals=()):
    """清单 files 严格只有既有 schema 字段，长度另存索引。"""
    rows=[]
    for directory in (REPORT,*PRES):
        for p in sorted(directory.rglob("*")):
            if not p.is_file():continue
            exact(p)
            role="source" if p.suffix in (".py",".sv",".v",".tcl",".xdc",".sh",".bat",".js") else "input" if directory!=REPORT else "log" if p.suffix in (".log",".rpt",".jou") else "artifact" if p.suffix in (".xsa",".bd",".rst") or p.name=="__synthesis_is_complete__" else "result"
            rows.append({"path":rel(p),"sha256":sha(p),"role":role})
    rows += [{"path":rel(p),"sha256":sha(p),"role":"input"} for p in externals]
    require(len(rows)==len({r["path"] for r in rows}),"清单路径重复")
    return rows
