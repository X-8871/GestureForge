"""冻结独立验证原件与源码版本，明确G2范围。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re
import sys

OUT=Path(__file__).absolute().parent
ROOT=Path(__file__).absolute().parents[4]
sys.path.insert(0,str(ROOT))
from verification.s2b_board_acceptance import save,binding

pre=json.loads((OUT/"precompile_result.json").read_text(encoding="utf-8"))
rtl=json.loads((OUT/"rtl_result.json").read_text(encoding="utf-8"))
assert rtl["status"]=="PASS_INDEPENDENT_G2_S1"
for path,sha in pre["source_bindings"].items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha
warnings=[line for line in (OUT/"compile.log").read_text(encoding="utf-8").splitlines() if line.startswith("%Warning-")]
tb_warnings=[line for line in warnings if "tb_s2b_geometry_specialization.sv:" in line]
assert len(warnings)==33 and not tb_warnings
receipt={"schema_version":1,"task_id":"S2B-T17-S1","role":"INDEPENDENT_REVIEWER","status":"PASS",
    "reviewed_at_utc8":datetime.now(timezone(timedelta(hours=8))).isoformat(),
    "baseline_commit":pre["baseline_commit"],"source_bindings":pre["source_bindings"],
    "scope":"4派生模块仅geometry常量/模块和engine引用重命名，活跃18=10原2A+4派生+4outer；源码/接口/错误优先/差分与来源离线G2。",
    "evidence_bindings":pre["evidence"],
    "independent_artifacts":{name:binding(OUT/name) for name in ("review_driver.py","precompile_result.json","rtl_result.json","compile.log","simulation.log","pool_vectors.dat","upsample_vectors.dat","tb_s2b_geometry_specialization.sv")},
    "findings":[],
    "source_provenance":{"frozen14":"实际原字节SHA全匹配；正文独立与671f9cf494b92ce182b3f1542fefd0cfd4b209f5的git blob比较通过。",
        "derived4":"独立固定允许替换，与4派生源UTF-8/LF原字节逐字符一致；backend/core上游CRLF仅在关系比较转LF，原件原字节保持。",
        "outer":"top仅core实例引用替换，Tcl仅版本/4文件闭包，profile/md披露0.1.1与来源；公共接口、时钟和可见性默认不变。",
        "checker":"独立固定14原件SHA和允许替换，不依赖profile自报SHA授予额外差异；26反例独立通过，旧0.1.0证明拒绝。"},
    "validation":{"precompile_command":"python -B tmp/2B/S2B-T17/independent_review_specialization_20261011_r01/review_driver.py prepare",
        "precompile_exit_code":0,"checker_negatives":26,"rtl_command":"python -B tmp/2B/S2B-T17/independent_review_specialization_20261011_r01/review_driver.py run",
        "rtl_exit_code":0,"runs":rtl["runs"],"simulation_counts":rtl["simulation_counts"],"coverage":pre["coverage"],
        "extra_stimuli":"新增244条多错误组合/合法末边界；req 11周期中7周期背压，rsp等待7..10周期，全部公开输出上/下沿差分及独立signed最大值/nearest地址检查。",
        "diagnostics":{"rtl_warning_count":len(warnings),"tb_warning_count":len(tb_warnings),"policy":"原33继承诊断全部保留；-Wall/-Wno-fatal，不抑制具体警告。"},
        "packaging_evidence":pre["packaging_evidence"],"packaging_inputs":pre["packaging_inputs"]},
    "limitations":["仅已声明采样/异常/等待/abort差分；未枚举全部通道×空间组合。",
        "差分oracle是冻结旧RTL，独立功能oracle限定pool/upsample当前向量；未重跑新闭包109完整整网。",
        "G2不证明完整BD恢复/综合/实现或50MHz STA通过；当前时序阻断未关闭。",
        "未批准visibility1/cache proof或最终bit，不代表G3/G4/G5；未访问硬件/MCP/SDK/Vivado。",
        "只写隔离tmp，不改项目源/共享分支/正式证据、不提交。"]}
save(OUT/"review_receipt.json",receipt)
print(json.dumps({"status":receipt["status"],"receipt":binding(OUT/"review_receipt.json"),"warnings":len(warnings),"tb_warnings":len(tb_warnings)},ensure_ascii=False))
