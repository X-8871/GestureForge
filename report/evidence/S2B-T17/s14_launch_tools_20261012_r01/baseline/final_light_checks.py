"""最后仅跑纯fixture及CLI help/待冻结拒绝；逐条保留原生身份和字节流。"""
import json
from pathlib import Path
import sys
import native_capture

W=Path(__file__).absolute().parent
commands=[("collector_fixture_r02",[str(W/"collector_fixtures.py")],0)]
for name in ("collector.py","impl_collector.py","native.py","source_after_check.py","native_source_after.py","runtime_consumer.py","launch_monitor.py","materialize_runtime_config.py","supervisor.py","guard.py"):
    commands.append(("help_"+Path(name).stem,[str(W/name),"--help"],0))
commands.append(("pending_prepare_refusal",[str(W/"collector.py"),"prepare"],1))
rows=[]
for label,arguments,expected in commands:
    sys.argv=[str(W/"native_capture.py"),label,sys.executable,"-X","utf8","-B",*arguments]
    code=native_capture.main(); row=json.loads((W/(label+".native.json")).read_text(encoding="utf-8"))
    rows.append(dict(label=label,actual_native_exit_code=code,expected_native_exit_code=expected,record=row))
    assert code==expected,(label,code,expected)
with (W/"final_light_checks_result.json").open("x",encoding="utf-8",newline="\n") as stream:
    json.dump(dict(status="PASS_G1_ONLY",checks=rows,actual_SOURCE_COMMIT=None,actual_source_before="NOT_RUN",actual_Vivado="NOT_RUN",actual_hardware="NOT_RUN"),stream,ensure_ascii=False,indent=2); stream.write("\n")
