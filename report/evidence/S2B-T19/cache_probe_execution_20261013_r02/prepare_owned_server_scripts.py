"""从上次已核验服务脚本精确派生新Run，仅替换唯一运行目录。"""
from pathlib import Path
import hashlib
import json
folder=Path(__file__).absolute().parent
source=folder.parent/"board_run_20261013_r01"
expected={"start_owned_server.ps1":"e01bfe0baa44dfd3c5a6c46addba292dd8d80e454bc860d5c9a882fbb793cabc",
          "close_owned_server.ps1":"3adbbc18d8d0a2b2e78d021d11afa0f1af46ad956d7055e0cb16688c65afff55"}
rows=[]
for name,value in expected.items():
    original=source/name;target=folder/name
    assert original.is_file() and folder.is_dir() and not target.exists()
    raw=original.read_bytes();assert hashlib.sha256(raw).hexdigest()==value
    text=raw.decode("utf-8-sig");assert text.count(str(source))==1
    text=text.replace(str(source),str(folder))
    with target.open("x",encoding="utf-8",newline="") as output:output.write(text)
    rows.append({"source":str(original),"source_sha256":value,"derived":str(target),"derived_sha256":hashlib.sha256(target.read_bytes()).hexdigest(),"changes":"仅一个完整运行目录字面量；原有归属、SHA、PID、监听及闭合门禁不变。"})
with (folder/"server_script_bindings.json").open("x",encoding="utf-8",newline="\n") as output:
    json.dump(rows,output,ensure_ascii=False,indent=2);output.write("\n")
print(json.dumps(rows,ensure_ascii=False))
