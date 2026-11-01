"""只读收集官方源码审计依据，不导入SDK、不测试或操作设备。"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).absolute().parents[4]
HERE = Path(__file__).absolute().parent
OUT = ROOT / "report/evidence/S2B-T19/unload_diagnostic_audit_20261013_r01"
SDK = Path(r"D:\Xilinx\2026.1\Vitis\cli")
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert HERE.is_dir() and OUT.is_dir()
assert not (OUT / "audit.json").exists()
sections = []
for relative, ranges in (
    ("xsdb/target.py", [(367, 376), (1776, 1783), (2186, 2198), (2243, 2278), (7368, 7538)]),
    ("xsdb/_utils.py", [(200, 224), (240, 246)]),
    ("tcf/util/sync.py", [(279, 299)]),
    ("tcf/util/task.py", [(136, 158)]),
    ("tcf/protocol.py", [(129, 159)]),
    ("xsdb/_tcf_node_memmap.py", [(59, 79)]),
    ("xsdb/_tcf_children_exec_context.py", [(83, 111), (117, 163)]),
    ("tcf/EventQueue.py", [(47, 65)]),
    ("tcf/services/remote/MemoryMapProxy.py", [(42, 61)]),
    ("tcf/util/cache.py", [(114, 199)])):
    path = SDK / relative
    assert path.is_file()
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    sections.append({"path": str(path), "sha256": sha(path), "ranges": [
        {"start_line": first, "end_line": last, "original_source": "".join(lines[first-1:last])}
        for first, last in ranges]})
assert sections[0]["sha256"] == "a853cb0a0d86e52bc588b045f648e1184708fc2d35ba2bd3b9eb11847288cf71"
hsi = Path(r"D:\Xilinx\2026.1\Vitis\scripts\python_pkg\hsi\__init__.py")
assert hsi.is_file()
summary_path = ROOT / "report/evidence/S2B-T19/cache_probe_execution_20261013_r04/summary.json"
entry_path = ROOT / "report/evidence/S2B-T19/cache_probe_20261013_r04/entry_calls.jsonl"
jtag_path = ROOT / "report/evidence/S2B-T19/cache_probe_20261013_r04/jtag_result.json"
assert all(path.is_file() for path in (summary_path, entry_path, jtag_path))
summary = json.loads(summary_path.read_text(encoding="utf-8"))
rows = [json.loads(line) for line in entry_path.read_text(encoding="utf-8").splitlines()]
baseline = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
assert baseline == summary["source_commit"] == "c8742858fbb23331763358775daa44dafb95db94"
facts = {
    "status": "DIAGNOSTIC_AUDIT_ONLY_ROOT_CAUSE_NOT_PROVEN", "source_commit": baseline,
    "hsi_init": {"path": str(hsi), "sha256": sha(hsi), "observation": "导入本地扩展xv_hsmpytasks，design.close实现不在本条Python源码内；未加载扩展。"},
    "observed_r04": {key: summary[key] for key in ("status", "entry_final_result", "entry_logical_exit_code",
        "sdk_process_native_exit_code", "launcher_exit_code", "primary_error", "last_completed_entry_call",
        "serial_close_returned", "controller_close_returned", "official_unload", "sdk_normal_disconnect_dispose")},
    "last_completed_calls": [{key: row.get(key) for key in ("time_utc8", "api", "status", "elapsed_seconds")} for row in rows[-10:]],
    "source_findings": [
        {"kind": "FACT", "location": "target.py:2188/2254/367", "statement": "loadhw与unloadhw均使用同一子树递归和MemoryMap更新，无load/unload独有线程机制。"},
        {"kind": "FACT", "location": "target.py:1776-1783", "statement": "递归children直接引用缓存字典，并将后代合并回该字典；后续调用可能重复访问后代。正常无祖先环的树仍有限，未证明r04存在环或此处卡住。"},
        {"kind": "FACT", "location": "_utils.py:200-223; sync.py:279-299", "statement": "实际等待使用Runnable/SyncRequest和无超时Condition.wait，无完成谓词；该路径未用Task.get(timeout)。"},
        {"kind": "INFERENCE_NOT_PROVEN_ON_R04", "location": "_utils.py:203-206/218-220; sync.py:286-290", "statement": "invokeLater或invokeAndWait之后才进入sync等待；若done通知先发生，调用者可能错过通知并永久等待。这是静态可成立的调度风险，尚无r04堆栈证据。"},
        {"kind": "INFERENCE_NOT_PROVEN_ON_R04", "location": "EventQueue.py:53-65; _utils.py:200-210", "statement": "Runnable执行异常被事件队列记录时，没有通用桥接将异常转给SyncRequest；某些异常可使等待者没有通知。r04是否存在此异常未知。"},
        {"kind": "FACT", "location": "_tcf_node_memmap.py:66-77; MemoryMapProxy.py:42-60", "statement": "MemoryMap.set异步完成回调才调用sync.done；RPC不完成或dispatcher不处理回调会使上层无超时等待。"},
        {"kind": "FACT", "location": "target.py:7525-7538", "statement": "清理memmap在design.close之前；缺少调用内堆栈，不能断言已到HSI.close。释放服务未唤醒也不能单独证明HSI卡住。"}],
    "minimal_next_diagnostic": {
        "placement": "仅项目public unloadhw单次调用外层；保留现有所有权及来源门禁。",
        "steps": ["在新Run目录独占创建unload_thread_stacks.log，以该文件为faulthandler输出并保持文件打开。",
            "调用前flush一个带UTC+8时间和线程名称的开始marker；调用faulthandler.dump_traceback_later(30,repeat=True,file=stream,exit=False)。",
            "同一调用线程执行现有public unloadhw；不启动第二个SDK/设备调用，不改官方源码，不绕过门禁。",
            "返回或异常时finally取消定时dump，再flush并关闭文件；保存返回/异常marker，不把栈采集超时当成SDK返回。",
            "保留既有外层无进度停止及身份核验。强制停止后明确记录unload/disconnect/dispose是否完成，不伪造最终入口成功。"],
        "stack_interpretation": ["主线程位于_get_all_children→exec_as_runnable：子树缓存/调度等待候选。",
            "主线程位于__update_mem_map→exec_in_dispatch_thread→Condition.wait：MemoryMap回调或错过通知候选。",
            "主线程位于protocol.invokeAndWait：派发线程尚未返回；同时检查TCF Event Dispatcher堆栈。",
            "主线程位于design.close：才支持定位至HSI原生调用入口，Python栈仍不能解释原生内部原因。",
            "dispatcher空闲而主线程等SyncRequest，只能缩小至未收到或错过完成通知；单凭Python栈仍不能区分二者。"],
        "limitation": "faulthandler定时线程只采集堆栈，不是安全取消SDK调用，也不证明清理成功。"},
    "actual_sdk_calls": 0, "actual_hardware_calls": 0, "tests_run": 0,
    "limitations": ["诊断方案未实施；真实卡点及根因未关闭。", "本代理提出诊断，不担任相应修复的独立Reviewer。",
        "其他Developer正在修改四生产/测试文件，本审计不读写其活动差异或给新PA补丁G2。"]}
for name, value in (("source_sections.json", sections), ("audit.json", facts)):
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
snapshot = OUT / "collect_audit.py"
assert not snapshot.exists()
shutil.copyfile(Path(__file__), snapshot)
files = [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "role": "source" if path.suffix == ".py" else "result"}
         for path in sorted(OUT.iterdir()) if path.is_file()]
files.extend({"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "role": "input"}
             for path in (summary_path, entry_path, jtag_path))
manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T19", "run_id": OUT.name,
    "source_commit": baseline, "evidence_dir": OUT.relative_to(ROOT).as_posix(),
    "interfaces": [], "interfaces_not_applicable_reason": "仅官方卸载源码只读诊断与真实失败原件审计，不修改或冻结业务/板卡接口。",
    "tool_versions": {"python": sys.version, "vitis_sdk_source": "2026.1官方源码，只读无模块执行。"},
    "files": files,
    "checks": [{"name": "read_only_source_audit", "status": "PASS", "command": subprocess.list2cmdline([sys.executable, "-X", "utf8", "-B", str(Path(__file__).absolute())]), "exit_code": 0},
               {"name": "r04_unload_root_cause", "status": "BLOCKED", "command": None, "exit_code": None,
                "reason": "缺少调用内全线程堆栈，实际卡点及根因未证明；需在新授权Run采集。"}],
    "limitations": facts["limitations"]}
with (OUT / "delivery_manifest.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(manifest, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps({"status": facts["status"], "manifest_sha256": sha(OUT / "delivery_manifest.json"),
                  "audit_sha256": sha(OUT / "audit.json"), "source_file_count": len(sections)}, ensure_ascii=False))
