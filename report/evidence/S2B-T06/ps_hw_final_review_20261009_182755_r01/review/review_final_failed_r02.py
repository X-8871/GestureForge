import hashlib
import json
import pathlib
import re
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta

# 本脚本仅读取冻结证据，检查输出只写入当前隔离目录。
sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path.cwd()
OUT = ROOT / "tmp/2B/S2B-T06/ps_hw_final_review_20261009_r01"
BASE = ROOT / "report/evidence/S2B-T06"
NAMES = ["ps_jtag_retry_20261009_120653_r01", "ps_jtag_retry_20261009_165853_r02", "ps_uart_clock_retest_20261009_172557_r01"]
EXPECTED = ["71dd3cb89de205c75553119293ac49bd6c8666f62c16d5b9563a2df2efacfb9f", "69db1376bad384eb065a90f5cabb6ac3dd6e5c30bbe95ae812663aa23faddc49", "87d078a7aa3dca888d773b3f686c033e2aa1a2c954b9f4ecfd0093f3fffad3c9"]
checks = []
commands = []
bindings = []

def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def load(p):
    def pairs(items):
        d = {}
        for k, v in items:
            if k in d:
                raise ValueError("重复JSON字段：" + k)
            d[k] = v
        return d
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8-sig"), object_pairs_hook=pairs)

def check(name, ok, detail=None):
    checks.append({"name": name, "pass": bool(ok), "detail": detail})

def bound(p, expected):
    p = pathlib.Path(p)
    actual = sha(p) if p.is_file() else None
    bindings.append({"path": str(p), "sha256": actual, "expected": expected})
    check("文件绑定：" + str(p), actual == expected)

def run(argv, stem):
    started = datetime.now(timezone(timedelta(hours=8))).isoformat()
    t = time.perf_counter()
    p = subprocess.run(argv, cwd=ROOT, capture_output=True)
    elapsed = time.perf_counter() - t
    stdout = OUT / (stem + ".stdout.log")
    stderr = OUT / (stem + ".stderr.log")
    stdout.write_bytes(p.stdout)
    stderr.write_bytes(p.stderr)
    commands.append({"argv": argv, "cwd": str(ROOT), "started_at_utc8": started, "elapsed_seconds": elapsed, "exit_code": p.returncode, "stdout": str(stdout), "stdout_sha256": sha(stdout), "stderr": str(stderr), "stderr_sha256": sha(stderr)})
    return p

bound(ROOT / ".codex/STATE.md", "743abc18ef2898b355b78052a94d79fe41408507f5b879d7d6486bb02593a642")
state = (ROOT / ".codex/STATE.md").read_text(encoding="utf-8")
check("STATE 54行且保持阶段边界", len(state.splitlines()) == 54 and "G0/G4/G5未通过" in state and "冲突未关闭" in state and "store值丢失" in state)
head = run(["git", "rev-parse", "HEAD"], "head")
check("固定HEAD", head.returncode == 0 and head.stdout.strip().decode() == "117911e63cd7468418f11847ffedc9293dbca075")
results = []
for index, name in enumerate(NAMES):
    folder = BASE / name
    manifestpath = folder / "delivery_manifest.json"
    bound(manifestpath, EXPECTED[index])
    m = load(manifestpath)
    check(name + "清单基线和项数", m["source_commit"] == "117911e63cd7468418f11847ffedc9293dbca075" and len(m["files"]) == [66,52,62][index])
    paths = [x["path"] for x in m["files"]]
    check(name + "无重复文件声明", len(paths) == len(set(paths)))
    for item in m["files"] + m["interfaces"]:
        bound(ROOT / item["path"], item["sha256"])
    check(name + "STATE快照原字节相等", (folder / "source_snapshot/STATE.md").read_bytes() == (ROOT / ".codex/STATE.md").read_bytes())
    for source in ["s2b_ps_smoke.c", "s2b_ps_smoke.md"]:
        if index < 2:
            original = subprocess.run(["git", "show", "HEAD:vitis/" + source], cwd=ROOT, capture_output=True)
            check(name + "旧源码为HEAD原字节：" + source, original.returncode == 0 and original.stdout == (folder / "source_snapshot" / source).read_bytes())
        else:
            check(name + "新源码为当前候选原字节：" + source, (ROOT / "vitis" / source).read_bytes() == (folder / "source_snapshot" / source).read_bytes())
    result = load(folder / "ps_smoke_result.json")
    results.append(result)
    calls = result["calls"]
    check(name + "实际API与host计数", sum("api" in c for c in calls) == result["api_call_count"] and sum("host_query" in c for c in calls) == result["host_query_count"])
    check(name + "命令返回字段保留", all(("command" in c and "exit_code" in c and "stdout" in c and "stderr" in c) if "host_query" in c else ("api" in c and "args" in c and "kwargs" in c and "state" in c and ("return_repr" in c or "error" in c)) for c in calls))
    capture = (folder / "uart_capture_stdout.log").read_text(encoding="utf-8").splitlines()
    opened = [json.loads(l[len("CAPTURE_OPEN "):]) for l in capture if l.startswith("CAPTURE_OPEN ")]
    closed = [json.loads(l[len("CAPTURE_CLOSED "):]) for l in capture if l.startswith("CAPTURE_CLOSED ")]
    check(name + "UART打开关闭唯一", len(opened) == len(closed) == 1)
    check(name + "UART配置", opened[0]["port"] == "COM4" and opened[0]["baud"] == 115200 and opened[0]["format"] == "8N1" and opened[0]["flow_control"] == "None" and opened[0]["dtr"] is False and opened[0]["rts"] is False)
    raw = (folder / "uart_raw.bin").read_bytes()
    check(name + "UART正常stopflag闭合", closed[0]["captured_bytes"] == len(raw) and closed[0]["reason"] == "stop_flag" and closed[0]["exit_code"] == 0 and closed[0]["cleanup_errors"] == [] and closed[0]["failure_message"] is None)
    if index == 0:
        check("A 原失败未改判", result["status"] == "PS_SMOKE_FAILED" and result["downloads"] == [] and result["ps_initialization"] == result["smoke_execution"] == "NOT_RUN" and result["final_states"]["cpu1"] == "Running" and bool(result["cleanup_errors"]) and raw == b"")
    else:
        csha = sha(folder / "source_snapshot/s2b_ps_smoke.c")
        expectedlines = ["BEGIN S2B-T06-1", "BUILD c_sha256=" + csha + " xsa_sha256=a57948c60cfc573b710f562ed7177b0422313d6b77f100856410370273f3eb58", "UART base=0xE0001000 baud=115200 data=8 parity=N stop=1 flow=NONE clock_hz=" + ("0" if index == 1 else "100000000"), "BUFFER begin=0x01100000 end_exclusive=0x01200000 bytes=1048576 words=262144 align=64 cacheline=32", "CONFIG cpu=0 passes=2 patterns=8 words_per_pattern=262144 order=WRITE_DSB_FLUSH_DSB_INVALIDATE_DSB_READ"]
        expectedlines += [f"PATTERN_PASS pass={p} pattern={n} words=262144 mismatches=0" for p in range(2) for n in range(8)]
        expectedlines += ["PASS passes=2 patterns=8 verified_words=4194304 mismatches=0", "END S2B-T06-1"]
        actual = [l for l in re.split(r"[\r\n]+", raw.decode("ascii")) if l]
        check(name + "独立完整23行协议", actual == expectedlines and len(raw) == [1445,1453][index-1])
        check(name + "结果/两核最终观测", result["status"] == ("PS_SMOKE_EXECUTION_SAVED" if index == 1 else "HARDWARE_GATES_SAVED") and result["cleanup_errors"] == [] and all(v.startswith("Stopped:") for v in result["final_states"].values()) and result["final_pc"] == {"cpu0":0x10AD58,"cpu1":0xFFFFFF34} and any(r["name"] == "SMOKE_RESULT" and r["value"] == 2 for r in result["readbacks"]))
        check(name + "新end硬件BP命中", any(b["name"] == "end_after_con" and b["status"]["2"]["HitCount"] == 1 and int(b["status"]["2"]["Address"],16) == 0x10AD58 for b in result["breakpoint_status"]))
    logs = load(folder / "packaging_checks_r01.json")
    for e in logs["events"]:
        mode = e["command"][e["command"].index("--mode") + 1]
        bound(folder / ("packaging_" + mode + "_r01.stdout.log"), e["stdout_sha256"])
        bound(folder / ("packaging_" + mode + "_r01.stderr.log"), e["stderr_sha256"])
        check(name + "历史包装退出码：" + mode, e["exit_code"] == (0 if mode == "evidence" else 2))
    for mode in ["evidence", "inputs"]:
        p = run([sys.executable, "-X", "utf8", "-B", "verification/check_stage_delivery.py", "--mode", mode, "--manifest", str(manifestpath.relative_to(ROOT))], str(index) + "_" + mode)
        check(name + "最终冻结实际包装：" + mode, p.returncode == (0 if mode == "evidence" else 2) and not p.stderr)
        if mode == "evidence":
            check(name + "最终CHECKS_OK", b"CHECKS_OK" in p.stdout)
        else:
            report = json.loads(p.stdout)
            check(name + "inputs仅业务状态阻断", report["warnings"] == [] and bool(report["errors"]) and all(re.fullmatch(r"checks\[\d+\] 依赖检查状态为 (FAIL|BLOCKED|NOT_RUN)，阻断 inputs 核验", error) for error in report["errors"]))

B, W = results[1:]
check("B 独立cold成功", B["ps_initialization"] == "HARDWARE_GATES_SAVED" and len(B["downloads"]) == 2 and any(r["name"] == "INIT_RESULT" and r["value"] == 2 for r in B["readbacks"]) and any(r["name"] == "INIT_RETURN_CODE" and r["value"] == 0 for r in B["readbacks"]))
check("B ready1/fail0", any(b["name"] == "ready_after_con" and b["status"]["2"]["HitCount"] == 1 for b in B["breakpoint_status"]) and any(b["name"] == "fail_after_con" and b["status"]["2"]["HitCount"] == 0 for b in B["breakpoint_status"]))
check("Warm仅复用初始化", W["ps_initialization"] == "REUSED_PRIOR_SUCCESS" and W["prior_initialization_provenance"]["executed_init_this_run"] is False and W["prior_initialization_provenance"]["result_sha256"] == sha(BASE/NAMES[1]/"ps_smoke_result.json") and W["initial_stop_requested"] == [])
api = [c for c in W["calls"] if "api" in c]
dow = [c for c in api if ".dow." in c["api"]]
con = [c for c in api if ".con." in c["api"]]
check("Warm仅一次默认dow/con且无强写复位", len(dow) == len(con) == 1 and dow[0]["kwargs"] == {"file": W["downloads"][0]["path"], "auto_stop": True, "set_entry": True} and con[0]["kwargs"] == {"timeout": 120} and con[0]["args"] == ["'--block'"] and not any(".mwr" in c["api"] or ".reset" in c["api"] for c in api))
check("Warm 57 API/8host且全部完成", W["api_call_count"] == 57 and W["host_query_count"] == 8 and all(c["state"] == "DONE" for c in api))
warm = BASE/NAMES[2]
accept = load(warm/"uart_acceptance.json")
check("Root新版独立UART接收PASS", accept["status"] == "PASS_UART_DDR_RETEST")
closure = load(warm/"hw_server_close.stdout.json")
check("服务闭合不声称核持续监测", closure["status"] == "OWNED_SERVER_CLOSED" and closure["native_exited"] is True and closure["launcher_exited"] is True and closure["remaining_listeners"] == [] and closure["cpu_resume_execution"] == "NOT_RUN")
history = load(warm/"root_execution_history.json")
check("历史store限制透明", "PARTIAL_STORE_UNAVAILABLE" in json.dumps(history) and "functions.store" in json.dumps(history) and (warm/"root_execution_history_initial_partial.json").is_file())
bound(warm/"root_execution_history.json", "e19c858c71971e92a94443c0486d05c5ade882a15b180e9abf7d7a6972e33717")
for f,h in [("old_and_warm_review_receipt.json","e3a3480a7fbe2417e9302aa886db70d0bfc4a1dd0790fc6e3cc842de94162930"),("code_review_receipt.json","e42e9d34d7437a15bed226cef7d259ddc75f5c4cc2eb1b1f76d84f7dbcc8208f"),("runner_review_receipt.json","6f34f5d707d66d077ae7e6b759f788ea5c59a6058a0802343adce3039be983ea"),("d08_package_review_receipt.json","2fb6ee5ca75e592c8cf935b57792b76847fbae42b2747d8251e1d46c3b3d0651")]:
    bound(warm/f,h)
    check("审查原件PASS："+f, "PASS" in (warm/f).read_text(encoding="utf-8"))
receipt = {"status":"PASS" if all(c["pass"] for c in checks) else "CHANGES_REQUIRED", "scope":"R13只读最终包装及固定UART/1MiB DDR实测核验；不代表完整阶段2B G0/G4/G5", "source_sha256":sha(__file__), "checks":checks, "bindings":bindings, "commands":commands, "hardware_access":"NOT_RUN", "reviewer_previous_failure":{"path":"reviewer_assumption_failure_r01.json","sha256":sha(OUT/"reviewer_assumption_failure_r01.json"),"reason":"第一轮脚本误用B的status/初始化枚举和API日志标签，误把con的位置参数block写成kwargs；按冻结原记录修正。没有修改被审证据。"}, "limitations":["未实物连接，核状态仅原会话内观测；沿用已独立审查的实际C/ELF及runner", "旧clock报告缺陷保留，新100M仅BSP配置值；非仪器测量", "初次root history部分store不可取原件和最终来源说明保留，未伪称恢复原始store", "全DDR扫描、双向UART回环、长期稳定性及带宽为此次固定smoke范围外扩展项"]}
(OUT/"final_review_receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"status":receipt["status"],"checks":len(checks),"failed":[c for c in checks if not c["pass"]],"receipt_sha256":sha(OUT/"final_review_receipt.json")},ensure_ascii=False,indent=2))
sys.exit(0 if receipt["status"] == "PASS" else 1)
