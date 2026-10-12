"""一次性归档新S13工具、必要失败原流和恢复映射；最终验证写scratch避免循环封存。"""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import sys
import compat_pins as p
import native_capture

W=p.exact(p.WORK,True); D=p.exact(p.ARCHIVE,True); ROOT=p.ROOT


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,row):
    assert not path.exists()
    with path.open("x",encoding="utf-8",newline="\n") as stream: json.dump(row,stream,ensure_ascii=False,indent=2); stream.write("\n")


def main():
    assert not (W/"runtime_pins.json").exists() and p.SOURCE_COMMIT is None
    assert all(not value.exists() for value in (p.SOURCE_FREEZE,p.SOURCE_PRE,p.PROJECT,p.SYNTH_REPORT,p.PNR_REPORT,p.SYNTH_CACHE,p.PNR_CACHE))
    for name in ("tools","raw","baseline","diffs"):
        target=D/name; assert not target.exists(); target.mkdir()
    mappings=[]
    def copy(original,target):
        original=p.exact(original); raw=original.read_bytes(); target.parent.mkdir(parents=True,exist_ok=True)
        assert not target.exists()
        with target.open("xb") as stream: stream.write(raw)
        assert original.read_bytes()==raw and target.read_bytes()==raw
        mappings.append(dict(original_absolute_path=str(original),archived_repo_path=target.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
    for original in sorted(W.rglob("*")):
        if original.is_file():
            relative=original.relative_to(W)
            if relative.parts[0]=="scratch" or original.name.startswith("seal_tools_r01."): continue
            target=D/"tools"/original.name if len(relative.parts)==1 and original.suffix==".py" else D/"raw"/relative
            copy(original,target)
    guard_baseline=ROOT/"tmp/2B/S2B-T17/s12_resource_guard_20261012_r02"
    collector_baseline=ROOT/"tmp/2B/S2B-T17/s12_launch_prepare_20261012_r01"
    assert sha(guard_baseline/"guard.py")=="a2f5c581b79a40116bf59c240a7b8c0fe35bac4db7b26a79ce5ba14c451a18ac"
    assert sha(guard_baseline/"supervisor.py")=="193416f869463c38065e257545720032438ab12c7bbe30beec6bc8c53d8f9ca0"
    assert sha(collector_baseline/"collector.py")=="61916205c4993ae856e6ba9afbb198f2cfee1f36b76aff27743e916880beeaad"
    for name in ("guard.py","supervisor.py","collector.py","impl_collector.py","native.py","source_after_check.py","native_source_after.py","compat_pins.py"):
        original=(guard_baseline if name in ("guard.py","supervisor.py") else collector_baseline)/name
        copy(original,D/"baseline"/name)
        diff="".join(difflib.unified_diff(original.read_text(encoding="utf-8").splitlines(True),(W/name).read_text(encoding="utf-8").splitlines(True),fromfile=str(original),tofile=str(W/name)))
        with (D/"diffs"/(name+".patch")).open("x",encoding="utf-8",newline="\n") as stream: stream.write(diff)
    historical=ROOT/"tmp/2B/S2B-T17/s12_physical_launch_root_20261012_r01"
    for relative in ("root_consumption.jsonl","root_consumption_r02.jsonl","wait.tool.json","runtime_consumer.mjs","supervision/guard/guard_receipt.json","supervision_r02/guard/guard_receipt.json","supervision_r03/guard/guard_receipt.json","supervision_r04/guard/guard_receipt.json"):
        copy(historical/relative,D/"baseline"/"s12_monitor"/relative)
    def functions(path):
        tree=ast.parse(path.read_text(encoding="utf-8")); result={}
        for node in tree.body:
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)): result[node.name]=ast.dump(node,include_attributes=False)
            if isinstance(node,ast.ClassDef):
                for child in node.body:
                    if isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef)): result[node.name+"."+child.name]=ast.dump(child,include_attributes=False)
        return result
    before=functions(D/"baseline"/"guard.py"); after=functions(W/"guard.py")
    unchanged=[name for name in before if before[name]==after.get(name)]
    preserved=["base_identity","identity","same_identity","Guard.readback_member","Guard.verified_chain","Guard.historical_member","Guard.stop_tree","Guard.stop_one","Guard.validate","Guard.limits","Guard.run"]
    assert all(name in unchanged for name in preserved)
    write(D/"ast_comparison.json",dict(unchanged_guard_functions=unchanged,required_preserved_functions=preserved,changed_guard_functions=[name for name in before if before[name]!=after.get(name)],added_guard_functions=sorted(set(after)-set(before)),no_threshold_changes=True,max_scans=3,continuous_same_set_scans_required=2,guard_target_seconds=1,supervisor_target_seconds=5,consumer_target_seconds=5,existing_consumer_hard_freshness_seconds=10))
    captures=[]; known=[]
    for path in sorted(W.glob("*.native.json")):
        row=json.loads(path.read_text(encoding="utf-8"))
        captures.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),native_exit_code=row["native_exit_code"],unknown_observations=row["unknown_count"],sampled_owned_tree_peak_bytes=row["sampled_owned_tree_peak_bytes"],elapsed_seconds=row["elapsed_seconds"],budget_stop=row["budget_stop"]))
        for identity in [row.get("launcher_identity"),row.get("direct_child_identity")]:
            if identity:
                known.append(native_capture.read_identity(identity))
    assert all(row["budget_stop"] is None for row in captures)
    write(D/"known_identity_readback.json",dict(observations=known,scope="仅本轮实际记录的launcher及direct child；此刻离散读回，不代表全部树闭合",whole_tree_terminal="NOT_PROVEN",current_sealer_identity=native_capture.identity(native_capture.psutil.Process())))
    write(D/"raw_mapping.json",dict(binding_rows=mappings,file_count=len(mappings),total_bytes=sum(row["bytes"] for row in mappings),copy_raw_equal=True,excluded_live_sealer_outputs="seal_tools_r01.*",excluded_future_validation_streams="scratch/；最后验证/本封存包装的关闭流不可能循环绑定自身，保留原件供ROOT另行封存。"))
    tools=[dict(path=(D/"tools"/path.name).relative_to(ROOT).as_posix(),sha256=sha(path),bytes=path.stat().st_size) for path in sorted(W.glob("*.py"))]
    write(D/"author_receipt.json",dict(status="PASS_G1_TOOLS_ONLY_PREPARATION_PENDING",SOURCE_COMMIT=None,source_freeze="PENDING_CODE_G2_AND_ROOT_COMMIT",source_count="ACTUAL_FREEZE_SET_AFTER_G2_NOT_READ",tool_archive_baseline_commit="467463757158aed80d6f75afadff6a8458614a29",actual_source_before="NOT_RUN",actual_synthesis="NOT_RUN",actual_pnr="NOT_RUN",actual_resource_admission="BLOCKED_PENDING_ACTUAL_ADMISSION",actual_independent_tools_review="NOT_RUN",actual_hardware="NOT_RUN",tools=tools,native_captures=captures,unknown_observation_count=sum(row["unknown_observations"] for row in captures),unknown_count_scope="各wrapper的观测事件合计；嵌套wrapper可重复同一对象，非独立UNKNOWN对象数。",maximum_sampled_wrapper_tree_bytes=max(row["sampled_owned_tree_peak_bytes"] for row in captures),absolute_tree_peak_bytes=None,complete_tree_terminal="NOT_PROVEN",guard_mock_methods=22,new_monitor_mock_methods=10,collector_mock_methods=7,actual_resource_threshold_canary=1,actual_native_consumer_canary=1,independent_native_consumption_during_driver_wait_rows=3,ROSS_calls=0,hardware_calls=0,Vivado_launches=0,production_or_STATE_or_Git_writes=False,limitations=["S12真实STA FAIL−2.402ns/91不由本轮工具准备关闭；S13新的源码及实际STA仍待运行。","monitor r03 actual直接流证明consumer独立运行与终态BLOCKED；其结果包装KeyError原件保留，由只读close_fixture_r03 native0补充，不补root canary未记录OS码。","r01 guard fixture父身份结果字段错误、r01 monitor错误mock、r02 cwd外conhost failclosed、r03包装KeyError全部原件保留。","新工具只G1，待独立G2；5秒是目标，所有actual gap/deadline miss保留，10秒硬门槛不放宽。","历史Developer PID/create_time未记录的范围不能恢复；本轮六字段只覆盖真实记录范围。","封存自身及随后最终检查流保留scratch，不声明无限循环自封存完成。","不读改生产源/STATE/HEAD；source_commit只为机器清单的S12工具出处，绝非S13生产SOURCE。"] ))
    write(D/"runtime_config_schema.json",dict(required_fields=list(p._CONFIG_FIELDS),path_fields=sorted(p._CONFIG_PATHS),fixed_nonconfigurable=dict(guard_sha=p.GUARD_SHA,supervisor_sha=p.SUP_SHA,tree_rss_bytes=6*1024**3,available_ram_stop_bytes=512*1024**2,c_disk_free_bytes=8*1024**3,guard_target_seconds=1,supervisor_target_seconds=5,consumer_target_seconds=5,hard_freshness_seconds=10),selector="S13_RUNTIME_CONFIG=精确绝对runtime_pins_synth_rNN.json或runtime_pins_pnr_rNN.json；每份新建，禁止覆盖工具源。",materializer="materialize_runtime_config.py --input ROOT审核真实JSON --output 精确新JSON；只是数据绑定，后续source-before仍需CLI==SOURCE==actualHEAD。",monitor_launch="launch_monitor.py --config ROOT真实monitor配置 --output-dir 与consumer同父目录精确新目录；READY_NATIVE_BACKGROUND_RUNNING后方可派发MCP重型命令。",closed_gate_requires="runtime_config实际path/sha256/bytes；一次products/synth；client running移交只保留None，不补0；关流绑定完整native JSONL。"))
    files=[]
    for path in sorted(D.rglob("*")):
        if path.is_file(): files.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),role="source" if path.suffix==".py" else "artifact",keep_reason="本轮工具/fixture/失败及原生身份流精确恢复；不批准heavy或硬件。"))
    checks=[]
    for label in ("guard_fixture_r01","guard_fixture_r02","monitor_fixture_r01","monitor_fixture_r02","monitor_fixture_r03","close_fixture_r03","collector_fixture_r01","collector_fixture_r02","final_light_r01","tool_mapping_r01"):
        row=json.loads((W/(label+".native.json")).read_text(encoding="utf-8"))
        checks.append(dict(name=label,status="PASS" if row["native_exit_code"]==0 else "FAIL",command=row["command"],exit_code=row["native_exit_code"],reason="实际原生结果；失败保留且补充记录不改首失败。"))
    for name,reason in (("S13_SOURCE_READY","新代码G2/ROOT提交/actualHEAD/实际集合冻结与G1/G2未提供；工具SOURCE仍None。"),("ACTUAL_RESOURCE_ADMISSION","未做本轮实际重型准入；现有门槛保持，不能由轻量fixture继承。"),("S13_TOOLS_G2","等待ROOT派发独立Reviewer；本交付只G1。")):
        checks.append(dict(name=name,status="BLOCKED",command=[],exit_code=None,reason=reason))
    for name in ("SOURCE_BEFORE_AFTER","SYNTH_PNR_STA_BIT_FULLXSA_VITIS","HARDWARE_G3_G4_G5"):
        checks.append(dict(name=name,status="NOT_RUN",command=[],exit_code=None,reason="本轮仅离线工具准备；实际运行未执行，不继承S12结果。"))
    manifest=dict(schema_version=1,stage="2B",task_id="S2B-T17",run_id=D.name,source_commit="467463757158aed80d6f75afadff6a8458614a29",evidence_dir=D.relative_to(ROOT).as_posix(),interfaces=[],interfaces_not_applicable_reason="独立原生进程监护及离线collector工具准备，不修改RTL/总线/模型接口；生产SOURCE与功能G2仍待冻结。",tool_versions=dict(python=sys.version,psutil=native_capture.psutil.__version__,Vivado="NOT_RUN_OFFLINE_TOOLS_ONLY"),files=files,checks=checks,limitations=["source_commit仅归档S12工具来源；S13实际SOURCE_COMMIT=None，未读取当前HEAD或变动生产源。","检查器仅包装核验，工具G2及实际资源准入/STA/硬件未通过。","最后验证流在scratch保留；封存自身stdout/stderr/native关闭流不循环绑定自身，需ROOT后续另归档。"])
    write(D/"delivery_manifest.json",manifest)
    print(json.dumps(dict(manifest_sha256=sha(D/"delivery_manifest.json"),receipt_sha256=sha(D/"author_receipt.json"),mapping_sha256=sha(D/"raw_mapping.json"),formal_file_count=len(files)+1,formal_bytes=sum(path.stat().st_size for path in D.rglob("*") if path.is_file()),unknown_observation_count=sum(row["unknown_observations"] for row in captures),max_sampled_wrapper_tree_bytes=max(row["sampled_owned_tree_peak_bytes"] for row in captures),SOURCE_COMMIT=None,STOP="PENDING_FINAL_WRAPPER_AND_CHECKER_READBACK"),ensure_ascii=False))


if __name__=="__main__": main()
