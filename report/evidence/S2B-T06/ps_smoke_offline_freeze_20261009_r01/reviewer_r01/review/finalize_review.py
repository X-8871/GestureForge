"""绑定独立审查原件、实际SDK与语法核验，生成只读G2收据。"""

import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parent.parent
REVIEW = ROOT / "review"
OUT = REVIEW / "f04"
SHARED = ROOT.parents[3]
RUN = SHARED / "report/evidence/S2B-T06/ps_smoke_20261008_r01"
BUILD = ROOT / "report/evidence/S2B-T06/b01"
sys.stdout.reconfigure(encoding="utf-8")
COMMANDS = []


def digest(path):
    """绑定原始字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    """只读UTF-8 JSON。"""
    return json.loads(path.read_text(encoding="utf-8"))


def new_json(name, value):
    """只在review目录创建新文件。"""
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def command(name, argv):
    """真实静态检查命令，日志拒绝覆盖。"""
    start = time.monotonic()
    proc = subprocess.run(argv, cwd=ROOT, capture_output=True, check=False, env=dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1"))
    log = OUT / (name + ".log")
    with log.open("xb") as stream:
        stream.write(proc.stdout)
        stream.write(proc.stderr)
    COMMANDS.append({"command": argv, "cwd": str(ROOT), "exit_code": proc.returncode, "elapsed_seconds": time.monotonic() - start, "log": str(log), "log_sha256": digest(log)})
    assert proc.returncode == 0, (name, proc.stderr)
    return proc.stdout


def method(path, name):
    """从实际安装源提取函数实现，不导入或实例化调试API。"""
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines()
    nodes = [x for x in ast.walk(ast.parse(source)) if isinstance(x, ast.FunctionDef) and x.name == name]
    assert len(nodes) == 1, name
    n = nodes[0]
    first = n.body[1] if isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant) else n.body[0]
    return {"source_path": str(path), "source_sha256": digest(path), "line": n.lineno, "implementation": "\n".join(lines[first.lineno-1:n.end_lineno])}


def main():
    """全部硬件命令只作文本/AST解析。"""
    text = (ROOT / "vitis/s2b_ps_smoke.md").read_text(encoding="utf-8")
    blocks = [{"index": i, "language": m.group(1), "source": m.group(2)} for i, m in enumerate(re.finditer(r"```(\w+)\n(.*?)\n```", text, re.DOTALL)) if m.group(1) in {"python", "powershell", "bash"}]
    new_json("document_blocks.json", blocks)
    python_blocks = [x for x in blocks if x["language"] == "python"]
    for block in python_blocks:
        ast.parse(block["source"])
    # 原生工具宿主已执行且保留精确命令/原退出，避免无输出的嵌套PowerShell路径。
    ps_capture = read(REVIEW / "f03/native_host_document_syntax.json")
    ps_results = ps_capture["parsed"]["results"]
    assert ps_capture["original_result"]["exit_code"] == 0 and len(ps_results) == 4
    assert all(not x["errors"] for x in ps_results)
    for block in [x for x in blocks if x["language"] == "bash"]:
        filename = OUT / f"document_bash_{block['index']}.bash"
        with filename.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(block["source"] + "\n")
        command("document_bash_parse", [r"C:\Program Files\Git\bin\bash.exe", "-n", str(filename)])
    syntax = {"status": "PASS_SYNTAX_ONLY", "python_blocks": len(python_blocks), "powershell_blocks": len(ps_results), "bash_blocks": sum(x["language"] == "bash" for x in blocks), "document_sha256": digest(ROOT / "vitis/s2b_ps_smoke.md"), "hardware_commands_executed": False, "commands": COMMANDS}
    new_json("document_syntax.json", syntax)
    sdk = {}
    target = Path(r"D:\Xilinx\2026.1\Vitis\cli\xsdb\target.py")
    session = Path(r"D:\Xilinx\2026.1\Vitis\cli\xsdb\session.py")
    bp = Path(r"D:\Xilinx\2026.1\Vitis\cli\xsdb\_breakpoint.py")
    for filename in [target, session, bp]:
        assert filename.is_file()
    for path, names in [(target, ["state", "con", "stop", "bpadd", "rrd", "mrd", "dow", "__get_current_node", "__select_target"]), (session, ["targets", "connect", "disconnect"]), (bp, ["add", "status", "remove"])]:
        for name in names:
            sdk[path.stem + "." + name] = method(path, name)
    for probe_name in ["xsdb_operating_basis_r03.json", "xsdb_help_probe_r02.json"]:
        for entry in read(RUN / probe_name)["methods"]:
            actual = Path(entry["source_path"])
            assert actual.is_file() and digest(actual) == entry["source_sha256"], entry["name"]
    assert "info = 'Stopped'" in sdk["target.state"]["implementation"]
    assert "return self._node" in sdk["target.__get_current_node"]["implementation"]
    assert "'--target_properties'" in sdk["session.targets"]["implementation"] and "return t" in sdk["session.targets"]["implementation"]
    assert "'--block'" in sdk["target.con"]["implementation"] and "timeout = timeout - 1" in sdk["target.con"]["implementation"]
    assert "'addr' in kwargs" in sdk["_breakpoint.add"]["implementation"]
    assert "argvar['set_entry']" in sdk["target.dow"]["implementation"] and "auto_stop" in sdk["target.dow"]["implementation"]
    new_json("sdk_basis.json", {"status": "PASS_INSTALLED_SOURCE_ONLY", "hardware_execution": "NOT_RUN", "debug_session_created": False, "connected": False, "targets_enumerated": False, "methods": sdk})
    post_capture = read(REVIEW / "f03/native_host_postflight.json")
    assert post_capture["original_result"]["exit_code"] == 0
    post_data = post_capture["parsed"]
    assert not post_data["own_remaining"]
    git_head = command("shared_head", ["git", "-C", str(SHARED), "rev-parse", "HEAD"]).decode("ascii").strip()
    git_index = command("shared_index", ["git", "-C", str(SHARED), "diff", "--cached", "--binary"])
    git_status = command("shared_status", ["git", "-C", str(SHARED), "status", "--short"])
    git_status_z = command("shared_status_porcelain_z", ["git", "-C", str(SHARED), "status", "--porcelain=v1", "-z"])
    copy_receipt = read(ROOT / "review_input_copy.json")
    assert git_head == "00f51b664fefdaf0c63e605af2427333579fa5f3" and hashlib.sha256(git_index).hexdigest() == copy_receipt["shared_index_sha256"]
    assert hashlib.sha256(git_status_z).hexdigest() == copy_receipt["shared_status_sha256"]
    assert git_status.decode("utf-8").splitlines() == git_status_z.decode("utf-8").rstrip("\0").split("\0")
    fixed_source_hashes = {
        "vitis/s2b_ps_smoke.c": "d2bb6f0941c2e3765c5a71f889d2e7e1e0428429237f5443510e81cedd16786b",
        "vitis/build_s2b_ps_smoke.py": "addff3a419609ac8203c8838edfd6fd56fb53baccf40efc403fca4eb36b50d76",
        "verification/check_s2b_ps_smoke_layout.py": "6c12023cc9660d392a0f3e393df2ebaf425af8a4cbb51886a35749d0c6fa0f77",
        "vitis/s2b_ps_smoke.md": "c15290c48ccbc03c55418c2efa0ca2df815eacdeffb60e53363eca4fba490db5",
    }
    assert all(digest(ROOT / path) == digest(SHARED / path) == expected for path, expected in fixed_source_hashes.items())
    rebuilt = read(REVIEW / "rebuild_receipt.json")
    assert rebuilt["native_exit_code"] == rebuilt["effective_exit_code"] == 0
    audit = read(REVIEW / "a01/audit_result.json")
    assert audit["status"] == "PASS_INDEPENDENT_OFFLINE_EXPERIMENTS"
    receipt = {
        "schema_version": 1, "task_id": "S2B-T06", "gate": "G2-r01", "decision": "PASS", "reviewer": "/root/s2b_ps_smoke_reviewer", "checked_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "baseline_commit": git_head, "fixed_upstream_commit": "90652b45ef31e763bd3e6f7527e2fd080ece61a8", "source_sha256": {p: digest(ROOT / p) for p in ["vitis/s2b_ps_smoke.c", "vitis/build_s2b_ps_smoke.py", "verification/check_s2b_ps_smoke_layout.py", "vitis/s2b_ps_smoke.md"]},
        "developer_manifest_sha256": digest(RUN / "delivery_manifest.json"), "developer_offline_validation_sha256": digest(RUN / "offline_validation_08.json"), "independent_rebuild": rebuilt, "independent_audit_result": {"path": str(REVIEW / "a01/audit_result.json"), "sha256": digest(REVIEW / "a01/audit_result.json"), "checks": len(audit["checks"]), "commands": len(audit["commands"])},
        "blocking_findings": [], "reviewed_contracts": [
            {"scope": "UART与异常状态", "locations": ["vitis/s2b_ps_smoke.c:59", "vitis/s2b_ps_smoke.c:100", "vitis/s2b_ps_smoke.c:253"], "assessment": "SDT UINTPTR E0001000 lookup、115200/8N1/NONE、IDR禁中断、实际格式/flow/oper模式回读；每字节send与TXACTIVE/FIFO清空均有限轮询。所有格式/发送失败返回非零并发布83；状态2只能在完整PASS/END成功发送后写回。81/82/84/85状态及首错统计已逐分支审查。GetDataFormat的BaudRate来自驱动保存的请求值，实际分频/线路仍需实板核验。"},
            {"scope": "独占DDR与模式参考", "locations": ["vitis/s2b_ps_smoke.c:129", "vitis/s2b_ps_smoke.c:184", "vitis/s2b_ps_smoke.c:204", "verification/check_s2b_ps_smoke_layout.py:351"], "assessment": "真实origin00100000；16MiB应用与1MiB NOBITS/NOLOAD对象[01100000,01200000)分离。独立解析ALLOC/LOAD、entry、6栈、heap、MMU/BSS并比对map；32B L1/L2维护和DSB顺序正确。2×8×262144=4194304，手算0/31/32/末word的8模式及首错/统计口径已对照C。CPU1/DMA/PL静止和物理DDR窗口安全是明确的人工前提。"},
            {"scope": "最小OCM初始化与启动", "locations": ["vitis/build_s2b_ps_smoke.py:22", "vitis/build_s2b_ps_smoke.py:464", "verification/check_s2b_ps_smoke_layout.py:199"], "assessment": "XSA原ps7_init.c/h与官方OCM脚本逐字节同源；全部ALLOC/LOAD和启动6栈/heap/BSS/MMUTable属于OCM且不碰顶部512字节。实际boot机器码/字面池、__cpu_init、_start、__libc_init_array及唯一frame_dummy无pre-main DDR依赖。xtimerinit/TimerInst被GC删除。ready7432/fail7448是无限WFE，main仅原ret0→状态2→DSB→ready；无旧镜像/PCAP/handoff/post_config ELF入口。ps7GetSiliconVersion只读F8007080，真GetSiliconVersion反例拒绝。"},
            {"scope": "CPU1与实际XSDB语义", "locations": ["vitis/s2b_ps_smoke.md:195", "vitis/s2b_ps_smoke.md:212", "vitis/s2b_ps_smoke.md:240"], "assessment": "boot.S及真实机器码仅eFuse单核位80时置CPU1 reset/clockstop22；目标XC7Z020双核需操作员先halt，启动未释放CPU1。实际Target各对象绑定自身_node/_ctx，Session.targets使用下划线--target_properties并返回Target。state返回Stopped或Stopped:(reason)，文档人工检查能使用该语义。断点addr/hw、con block timeout、dow auto_stop/set_entry、mrd/rrd、breakpoint status/remove均逐项核对安装实现；真实命中/状态变化尚未实板执行，遇异常必须停止。"},
            {"scope": "人工操作包", "locations": ["vitis/s2b_ps_smoke.md:117", "vitis/s2b_ps_smoke.md:159", "vitis/s2b_ps_smoke.md:244", "vitis/s2b_ps_smoke.md:269"], "assessment": "冷JTAG/cascade/BootROM结束/独占CPU与writer静止前提、每次全新Run/CreateNew原始UART、server3121归属/PID确认、只移除自己断点、结束server归属确认、失败/超时停止留证及初始化后禁止reset均明确。初始化需要ready PC/ret0/state2/CPU1联合；smoke需要_exit PC/state2与完整BEGIN/BUILD/16模式/PASS4194304/END联合。未把W1C PCFG_DONE事件用作无PL配置证明。固定操作表仍绑定Developer ELF，不把新debug ELF的不同整体SHA当错误或套用到实物步骤。"},
            {"scope": "构建、失败保全与包装", "locations": ["vitis/build_s2b_ps_smoke.py:251", "vitis/build_s2b_ps_smoke.py:319", "vitis/s2b_ps_smoke.md:69"], "assessment": "独立fresh Vitis2026.1构建原builder，无cache、无guard monkeypatch。native0与有效0、三个真实整数SUCCESS0、27API/6命令/ELF/map/layout联合核验。14内存模型/格式反例及3实际二进制语义反例、源码hash/编译头/config反例和真实exit7日志保全通过。原01–07 FAIL与SDK/API/Windows路径/FSBL-U诊断不改写；284文件原SHA全部一致。inputs/evidence CHECKS_OK只证明包装，未代替独立审查或实物验收。"}
        ],
        "task_card_correction": {"original": "两轮cache on/off", "corrected": "两轮重复，均显式启用DCache，每模式WRITE_DSB_FLUSH_DSB_INVALIDATE_DSB_READ", "authority": "总控2026-10-09在子代理消息中确认转写错误", "basis": ["正式阶段计划68–76仅要求记录模式/次数/零不匹配", "固定C196/204–252及说明26一致"]},
        "primary_web_basis": [{"url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Example-JTAG-Boot-Sequence", "verified_version": "UG585 1.15 2026-02-06", "assessment": "官方非安全JTAG/cascade例子在BootROM结束后交出DAP，CPU留在WFE；这是候选依据，非本板实测。"}, {"url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/JTAG-and-Debug-Considerations", "assessment": "官方说明非安全BootROM完成后恢复JTAG。"}, {"url": "https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Registers-Modified-by-the-BootROM-Examples", "assessment": "官方ZC702/7z020及ZC706例表JTAG UNLOCK=757BDF0D，MCTRL包含硅版本；支持推断，不是AX7020已测或单读UNLOCK证明。"}],
        "syntax_only": syntax, "commands": COMMANDS, "postflight": post_data, "shared_head_index_status_unchanged": True,
        "shared_status_representation": {"short_lf_sha256": hashlib.sha256(git_status).hexdigest(), "porcelain_v1_nul_sha256": hashlib.sha256(git_status_z).hexdigest(), "original_copy_receipt_field": "shared_status_sha256", "original_copy_receipt_uses": "git status --porcelain=v1 -z原始stdout", "decoded_entries_equal": True, "entries": git_status.decode("utf-8").splitlines(), "reason": "分隔符分别为LF/NUL；均153字节、5项同一状态。第三次审查收据脚本误把LF与原NUL口径作同SHA，真实ASSERT失败保留；第四次按精确原口径核验并另保留LF原件，没有改原收据。"},
        "review_tooling_diagnostic": {"original_finalize_effective_exit_code": 1, "original_parser_native_exit_code": 0, "original_parser_log": str(REVIEW / "document_powershell_parse.log"), "original_parser_log_sha256": digest(REVIEW / "document_powershell_parse.log"), "original_script": str(REVIEW / "finalize_review_failed_r01.py"), "original_script_sha256": digest(REVIEW / "finalize_review_failed_r01.py"), "second_script": str(REVIEW / "finalize_review_failed_r02.py"), "second_script_sha256": digest(REVIEW / "finalize_review_failed_r02.py"), "second_parser_log": str(REVIEW / "f02/document_powershell_parse.log"), "reason": "审查收据编排的-File和-Command嵌套子进程均返回0但没有JSON输出，未把空输出当通过。两次原脚本/空日志保留；f03采用原生工具宿主调用纯Parser，保存精确命令与真实退出0/4个非空无错误结果。没有改动被审源或Developer证据。"},
        "review_tooling_third_diagnostic": {"effective_exit_code": 1, "original_script": str(REVIEW / "finalize_review_failed_r03.py"), "original_script_sha256": digest(REVIEW / "finalize_review_failed_r03.py"), "original_git_commands_exit_code": 0, "original_logs": {str(REVIEW / "f03" / name): digest(REVIEW / "f03" / name) for name in ["shared_head.log", "shared_index.log", "shared_status.log"]}, "failure": "AssertionError: 审查收据脚本误比较--short LF与原--porcelain=v1 -z NUL的不同原始SHA", "closure": "本次同时运行两个精确命令，原NUL SHA相同且5条解码状态逐项一致；源码/index/HEAD未改动。", "original_stdout_stderr_traceback_file": "NOT_CAPTURED_AS_FILE；保留脚本、实际导致失败的原始git输出及诊断，不补造日志"},
        "hardware_execution": "NOT_RUN", "g3_g4_g5": "NOT_PASSED", "full_process_tree_peak_memory": "NOT_MEASURED", "whole_task_tool_call_count": "NOT_MEASURED",
        "scope_limits": ["独立离线G2 PASS；不授权/执行连接、枚举目标、下载、烧录、初始化或板上UART/DDR。", "板卡XC声明/XA照片、PCB/电平/供电/DDR延时与冷JTAG条件仍须实物前核对。", "不冻结S2B-T05待选择物理恢复接口，不修改2A；不计为整网100样本或1000连续任务。", "本次没有提交或更改共享Git/index；总控后续集成与提交不属于此收据。", "复核证据不依赖保存完整SDK或w01编译缓存；固定Git/XSA、b01绑定原件、review原始实验与复制映射是最小恢复入口。"]
    }
    new_json("semantic_review_receipt.json", receipt)
    evidence = []
    for directory in [REVIEW, BUILD]:
        for path in sorted(directory.rglob("*")):
            if path.is_file() and path.name != "review_evidence_bindings.json":
                evidence.append({"path": str(path), "relative_to_rv1": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "bytes": path.stat().st_size})
    bindings = {"status": "PASS_G2_OFFLINE_REVIEW_BINDINGS", "hardware_execution": "NOT_RUN", "decision": "PASS", "receipt_path": str(OUT / "semantic_review_receipt.json"), "receipt_sha256": digest(OUT / "semantic_review_receipt.json"), "files": evidence, "file_count": len(evidence), "exclude": ["tmp/2B/S2B-T06/w01编译缓存", "完整SDK", ".git对象库副本"], "copy_instruction": "总控按本表逐字节复制到新的正式Reviewer目录，原绝对路径通过copy mapping保存；不要修改原件。"}
    new_json("review_evidence_bindings.json", bindings)
    print(json.dumps({"decision": "PASS", "files": len(evidence), "receipt_sha256": bindings["receipt_sha256"], "bindings_sha256": digest(OUT / "review_evidence_bindings.json"), "syntax": {k: syntax[k] for k in ["python_blocks", "powershell_blocks", "bash_blocks"]}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
