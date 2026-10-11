"""只读核对代表性监督器记录和自有失败夹具关闭，冻结独立审查。"""
import hashlib
import json
from pathlib import Path
import psutil

base = Path(__file__).absolute().parent
root = Path.cwd().resolve()
result = json.loads((base / "attempt2/review_result.json").read_text(encoding="utf-8"))
assert result["status"] == "PASS"
entries = {x["path"]: x for x in json.loads((base / "attempt2/review_inputs.json").read_text(encoding="utf-8"))}
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def bind(path, role):
    relative = path.relative_to(root).as_posix()
    entries[relative] = {"path": relative, "sha256": sha(path), "role": role}
def load(path, role="input"):
    bind(path, role)
    return json.loads(path.read_text(encoding="utf-8"))
sup = root / "tmp/2B/S2B-T17/s11_guard_supervisor_20261012_r01"
sup_result = load(sup / "selftest_result.json", "result")
assert len(sup_result["cases"]) == 8 and all(x["supervisor_code"] == 2 for x in sup_result["cases"])
for case in sup_result["cases"]:
    path = sup / ("fixture_" + case["case"]) / "supervisor_receipt.json"
    record = load(path, "result")
    assert sha(path) == case["receipt_sha256"]
    assert record["child_native_exit_code"] == case["native_child_code"]
    assert record["ready"] == case["ready"] and record["supervisor_exit_code"] == 2
# 首轮包装TypeError之后夹具具有25秒自然寿命；只读该次自己的三个PID。
first_readback = []
for role in ("root", "helper", "leaf"):
    path = base / "A_known" / (role + "_ready.json")
    original = load(path)
    try:
        process = psutil.Process(original["pid"])
        current = {"pid": process.pid, "create_time": process.create_time(), "exe": process.exe(), "cwd": process.cwd(), "cmdline": process.cmdline(), "ppid": process.ppid()}
    except psutil.NoSuchProcess:
        first_readback.append({"role": role, "original_pid": original["pid"], "status": "ABSENT", "limitation": "该次身份读取失败前未保存完整出生字段，只证明此时该PID缺失"})
    else:
        first_readback.append({"role": role, "status": "RETAINED_UNKNOWN", "actual": current})
assert all(x["status"] == "ABSENT" for x in first_readback), "自有首轮对象未闭合，不可PASS"
with (base / "first_attempt_fixture_readback.json").open("x", encoding="utf-8") as stream:
    json.dump(first_readback, stream, ensure_ascii=False, indent=2)
first_native = load(base / "review.native.json", "log")
final_native = load(base / "review_attempt2.native.json", "log")
assert first_native["native_exit_code"] == 1 and final_native["native_exit_code"] == 0
for path in base.rglob("*"):
    if path.is_file():
        assert path.suffix.lower() not in {".exe", ".obj", ".bit", ".dcp", ".pyc"}
        bind(path, "source" if path.suffix == ".py" else "log" if path.suffix == ".log" else "diagnostic" if "first" in path.name else "result")
manifest = base / "raw_manifest.jsonl"
with manifest.open("x", encoding="utf-8", newline="\n") as stream:
    for row in sorted(entries.values(), key=lambda x: x["path"]):
        assert set(row) == {"path", "sha256", "role"} and row["role"] in {"source", "input", "result", "log", "diagnostic", "artifact"}
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
receipt = dict(result)
receipt["checks"] = len(result["checks"]) + 2
receipt["supplemental_checks"] = ["监督器八个冻结fixture终态均supervisor2且child原生码逐项不改写", "审查首轮三个自有夹具此时PID真实缺失；未采完整出生身份的限制保留"]
receipt["commands"] = [first_native, final_native, load(base / "attempt2/head.native.json", "log")]
receipt["reviewer_auxiliary_failure"] = {"native_exit_code": 1, "cause": "独立夹具将psutil.Process替换为函数，内部isinstance失效；改为仅候选模块命名空间包装", "evidence": "review.stderr.log", "cleanup": "第一轮fixture25秒自然退出后只读确认三PID缺失；第二轮自有对象六字段核对清理", "production_impact": "无；未修改候选或原件"}
receipt["raw_manifest_sha256"] = sha(manifest)
receipt["raw_manifest_lines"] = len(entries)
receipt["reviewer_stop"] = "STOP_READONLY_S11_TOOL_G2_ONLY"
path = base / "final_review_receipt.json"
with path.open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2); stream.write("\n")
print(json.dumps({"status": "PASS", "STOP": True, "receipt_sha256": sha(path), "raw_manifest_sha256": sha(manifest), "raw_manifest_lines": len(entries)}, ensure_ascii=False))
