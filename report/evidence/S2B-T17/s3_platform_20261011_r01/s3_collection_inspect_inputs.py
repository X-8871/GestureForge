"""只读显示本次冻结输入的实际结构，避免沿用旧批次字段。"""
import json
from pathlib import Path
root=Path(__file__).absolute().parents[4]
pre=root/"report/evidence/S2B-T17/s3_source_preflight_20261011_r01"
for name in ("source_before.json","source_after.json","root_mcp_calls_closed.json"):
    obj=json.loads((pre/name).read_text(encoding="utf-8"))
    print(name)
    for k,v in obj.items():
        if isinstance(v,list): print(k,"list",len(v))
        elif isinstance(v,dict): print(k,"dict",list(v))
        else: print(k,repr(v)[:600])
    if name=="source_before.json":
        print("last_sources",obj["source_files"][-15:])
    if name=="root_mcp_calls_closed.json":
        def walk(v):
            if isinstance(v,dict):
                if "command" in v: print("history",{k:v.get(k) for k in ("id","command","code","elapsed","timestamp")})
                if v.get("type")=="text":
                    try: walk(json.loads(v["text"]))
                    except (ValueError,KeyError): pass
                for k,item in v.items():
                    if k!="text": walk(item)
            elif isinstance(v,list):
                for item in v:walk(item)
        walk(obj)
