"""只读检查闭合工具结果及原生运行身份字段。"""
import json,re
from pathlib import Path
r=Path(__file__).absolute().parents[4]
p=r/"report/evidence/S2B-T17/s3_source_preflight_20261011_r01"
o=json.loads((p/"root_mcp_calls_closed.json").read_text(encoding="utf-8"))
for c in o["calls"]:
    print("CALL",{k:v for k,v in c.items() if k not in ("result","response","command")})
    print("KEYS",list(c))
    print("RESULT",repr(c.get("result",c.get("response")))[:2500])
for x in sorted((r/"tmp/2B/S2B-T17/s3p1/s2b_inference_candidate.runs").iterdir()):
    if x.is_dir() and x.name!=".jobs":
        s=(x/"runme.log").read_text(encoding="utf-8")
        print(x.name,"HEAD",s[:700],"TAIL",s[-1300:])
profile=json.loads((p/"source_snapshot/board/s2b_inference_platform.json").read_text(encoding="utf-8"))
print("PROFILE_KEYS",list(profile))
print("VERSION",{k:profile[k] for k in profile if "version" in k or "clock" in k or "visibility" in k or "part" in k})
print("NATIVE_READ",re.findall(r"read_verilog[^\n]+",(r/"tmp/2B/S2B-T17/s3p1/s2b_inference_candidate.runs/s2b_inference_infer_0_synth_1/s2b_inference_infer_0.tcl").read_text(encoding="utf-8"))[:2])
