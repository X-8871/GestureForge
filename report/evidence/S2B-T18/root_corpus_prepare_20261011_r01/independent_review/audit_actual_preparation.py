"""只读审查实际离线准备产物，全部审查记录写入本独占临时目录。"""
from pathlib import Path
import collections
import ctypes
import hashlib
import json
import math
import os
import subprocess
import sys
import time

ROOT = Path(r"C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition")
OUT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True
from verification import s2b_board_acceptance as acceptance
from verification import s2b_board_transport as transport
from verification import s2b_fixed_capture_check as checker

def read(path):
    """验证精确普通文件路径，读入 UTF-8 JSON。"""
    return json.loads(transport.exact_path(path).read_text(encoding="utf-8"))

def file_binding(path):
    """逐块哈希避免大文件驻留内存。"""
    path = transport.exact_path(path)
    sha = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            sha.update(chunk)
            size += len(chunk)
    return {"path": str(path), "sha256": sha.hexdigest(), "bytes": size}

def check(condition, message):
    """发现实际不一致即停止并保留失败记录。"""
    if not condition:
        raise AssertionError(message)

def save(name, value):
    """独占写入审查新文件。"""
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, allow_nan=False, indent=2)
        stream.write("\n")

def peak_memory():
    """读取本审查进程实际峰值工作集。"""
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in ("PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
                "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    kernel = ctypes.WinDLL("kernel32")
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi = ctypes.WinDLL("psapi")
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    check(psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb), "峰值内存读取失败")
    return counters.PeakWorkingSetSize

def hand_compute(reference, frozen):
    """由已留存框的 source_order 定位原始 INT8，独立计算其全部数值字段。"""
    report = []
    anchors = [(10, 14), (23, 27), (37, 58), (81, 82), (135, 169), (344, 319)]
    width, height = reference["input"]["geometry_wh"]
    if width >= height:
        rw, rh = 416, height * 416 // width
    else:
        rw, rh = width * 416 // height, 416
    px, py = (416-rw)//2, (416-rh)//2
    for detection in reference["detections"]:
        order = detection["source_order"]
        if order < 13*13*15:
            name, grid, mask, relative = "head13", 13, [3, 4, 5], order
        else:
            name, grid, mask, relative = "head26", 26, [1, 2, 3], order - 13*13*15
        cell, remainder = divmod(relative, 15)
        local_anchor, class_id = divmod(remainder, 5)
        row, col = divmod(cell, grid)
        raw = transport.exact_path(reference["head_tensors"][name]["path"]).read_bytes()
        offsets = [(local_anchor*10+entry)*grid*grid+cell for entry in range(10)]
        values = [raw[i] if raw[i] < 128 else raw[i]-256 for i in offsets]
        scale = frozen["head_tensors"][name]["int8_scale"]
        logits = [v*scale for v in values]
        sigmoid = lambda value: 1/(1+math.exp(-value))
        cx = (col+sigmoid(logits[0])*1.05-.025)/grid
        cy = (row+sigmoid(logits[1])*1.05-.025)/grid
        aw, ah = anchors[mask[local_anchor]]
        bw, bh = math.exp(logits[2])*aw/416, math.exp(logits[3])*ah/416
        xyxy = [max(0, min(1, v)) for v in (((cx-bw/2)*416-px)/rw, ((cy-bh/2)*416-py)/rh,
                  ((cx+bw/2)*416-px)/rw, ((cy+bh/2)*416-py)/rh)]
        score = sigmoid(logits[4])*sigmoid(logits[5+class_id])
        check(class_id == detection["class_id"] and transport.CLASS_NAMES[class_id] == detection["class_name"], "手算类别不一致")
        errors = [abs(a-b) for a,b in zip(xyxy, detection["xyxy"])]
        check(abs(score-detection["score"]) <= 1e-12 and max(errors) <= 1e-12, "sample000手算框不一致")
        report.append({"source_order": order, "head": name, "row": row, "col": col, "local_anchor": local_anchor,
            "class_id": class_id, "raw_offsets": offsets, "raw_int8": values, "int8_scale": scale,
            "score": score, "xyxy": xyxy, "score_error": abs(score-detection["score"]), "max_xyxy_error": max(errors),
            "scope": "核算已保存非空框的score/xyxy/来源顺序/类别；不声称独立重验全部候选或NMS。"})
    check(bool(report), "sample000必须实际包含框")
    return report

started = time.perf_counter()
result = {"schema_version": 1, "role": "INDEPENDENT_REVIEWER", "status": "CHANGES_REQUIRED", "hardware_execution": "NOT_RUN",
    "review_scope": "实际109样本离线准备完整性；不批准runtime兼容性、最终PL或G3/G4/G5。"}
try:
    prep_path = ROOT / "report/evidence/S2B-T18/root_corpus_prepare_20261011_r01/preparation.json"
    result["preparation"] = file_binding(prep_path)
    check(result["preparation"]["sha256"] == "3d87b85e2e46becde90be7a071eb094d6dfb6b559d0301ece6333460a3a502cb", "准备原件不符")
    plan = read(prep_path)
    check(plan["status"] == "NOT_RUN" and plan["hardware_execution"] == "NOT_RUN", "实际准备被错误标记板上执行")
    acceptance.validate_plan(plan)
    result["production_validate_plan"] = "PASS_ACTUAL_NO_MOCK"
    samples = read(plan["samples_manifest"]["path"])["samples"]
    golden = read(plan["golden_source"]["path"])["samples"]
    model = read(plan["model_manifest"]["path"])
    weight = file_binding(plan["weights"]["path"])
    check(weight["bytes"] == 5903100 and weight["sha256"] == plan["weights"]["sha256"] == model["bindings"]["gf8_package"]["sha256"], "GF8绑定不一致")
    with transport.exact_path(weight["path"]).open("rb") as stream:
        check(stream.read(8) == b"GFINT8W1", "GF8魔数错误")
    result["weights"] = weight
    classes = collections.Counter(tag[6:] for sample in samples[:100] for tag in sample["coverage_tags"] if tag.startswith("class:"))
    check(classes == collections.Counter({name:20 for name in transport.CLASS_NAMES}), "五类各20实际覆盖不一致")
    check(len({s["sample_id"] for s in samples}) == 109 and len(samples) == len(golden) == 109, "109身份不完整或重复")
    result["class_coverage_first100"] = dict(classes)
    result["extra_samples"] = [{"index": index, "sample_id": samples[index]["sample_id"], "coverage_tags": samples[index]["coverage_tags"]} for index in range(100,109)]
    result["rows"] = []
    for index, row in enumerate(plan["rows"]):
        sample, gold = samples[index], golden[index]
        input_binding = file_binding(row["input"]["path"])
        check(input_binding["bytes"] == row["input"]["bytes"] == 519168 and input_binding["sha256"] == sample["pl_input_sha256"] == gold["input"]["pl_input_sha256"], f"input {index} 不一致")
        check(row["sample_id"] == sample["sample_id"] == gold["sample_id"] and row["index"] == index and sample["frame_id"] == gold["frame_id"] == index, f"身份 {index} 不一致")
        ref_binding = file_binding(row["reference"]["path"])
        check(ref_binding["sha256"] == row["reference"]["sha256"], f"reference {index} 不一致")
        ref = read(row["reference"]["path"])["samples"][0]
        for key in ("frame_id", "sample_id", "input", "detections", "nms_output_box_count"):
            check(ref[key] == gold[key], f"reference {index}/{key} 不一致")
        raw_path = transport.exact_path(transport.exact_path(input_binding["path"]).parent / "golden_unique.bin")
        head_results = {}
        with raw_path.open("rb") as stream:
            for name, length in {"head13":5070,"head26":20280}.items():
                descriptor = gold["head_tensors"][name]
                binding = file_binding(ref["head_tensors"][name]["path"])
                check(binding["bytes"] == descriptor["byte_length"] == length and binding["sha256"] == descriptor["tensor_sha256"] == ref["head_tensors"][name]["tensor_sha256"], f"head {index}/{name}不一致")
                stream.seek(descriptor["byte_offset"])
                raw = stream.read(length)
                check(len(raw) == length and hashlib.sha256(raw).hexdigest() == binding["sha256"] and raw == Path(binding["path"]).read_bytes() and 128 not in raw, f"raw slice {index}/{name}不一致")
                head_results[name] = {**binding, "raw_golden_path":str(raw_path), "byte_offset":descriptor["byte_offset"], "slice_sha256":hashlib.sha256(raw).hexdigest()}
        result["rows"].append({"index":index,"sample_id":sample["sample_id"],"input":input_binding,"reference":ref_binding,"head_tensors":head_results,"all_detection_fields_match_frozen_cpu_d9":True,"nms_output_box_count":ref["nms_output_box_count"]})
        if index == 0:
            result["sample000_independent_hand_computation"] = hand_compute(ref, gold)
    result["source_bindings"] = {}
    snapshot = OUT / "source_snapshot"
    snapshot.mkdir()
    for rel in ["verification/s2b_board_acceptance.py", "verification/s2b_board_transport.py", "verification/s2b_fixed_capture_check.py", "verification/check_s2b_inference_platform.py", *checker.SOURCE_LF_HASHES]:
        binding = file_binding(ROOT / rel)
        payload = transport.exact_path(binding["path"]).read_bytes()
        if rel in checker.SOURCE_LF_HASHES:
            check(hashlib.sha256(payload.replace(b"\r\n", b"\n")).hexdigest() == checker.SOURCE_LF_HASHES[rel], "冻结解码依据源码漂移")
        target = snapshot / Path(rel).name
        with target.open("xb") as stream:
            stream.write(payload)
        result["source_bindings"][rel] = {**binding, "snapshot":file_binding(target)}
    check(result["source_bindings"]["verification/s2b_board_acceptance.py"]["sha256"] == "5beefa0b60993ccd8f2c2a68718d36fdca391dc1048e0a1ab2bfca1b4eba1867", "审查生产源码漂移")
    process_path = ROOT / "tmp/2B/S2B-T18/root_corpus_prepare_20261011_r01/prepare_process.json"
    result["root_prepare_native_process"] = {"binding":file_binding(process_path),"record":read(process_path)}
    check(result["root_prepare_native_process"]["record"]["exit_code"] == 0, "实际prepare退出码非0")
    result["root_prepare_logs"] = [file_binding(process_path.parent/name) for name in ["prepare.stdout.log", "prepare.stderr.log"]]
    result["git_head"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
    result["status"] = "PASS_OFFLINE_PREPARATION_INTEGRITY"
except BaseException as error:
    result["error"] = repr(error)
finally:
    result["actual_seconds"] = time.perf_counter()-started
    result["peak_working_set_bytes"] = peak_memory()
    if result["peak_working_set_bytes"] >= 300*1024*1024:
        result["status"] = "CHANGES_REQUIRED"
        result["error"] = "审查实际峰值工作集超出300MiB预算"
    result["limitations"] = ["硬件NOT_RUN；未接串口、未调用SDK/Vivado/硬件。", "raw golden仅核验218实际头切片，不重算全模型或重哈希大gold shards。", "sample000手算核验保存框字段；全109框字段来源按冻结CPU D9原字节记录核对，不重新执行全部NMS。", "本审查不批准runtimecompatibility、visibility、最终PL、STA或实板验收。"]
    save("raw_audit_result.json", result)
    print(json.dumps({key:result[key] for key in ("status", "hardware_execution", "actual_seconds", "peak_working_set_bytes")}, ensure_ascii=False))
sys.exit(0 if result["status"] == "PASS_OFFLINE_PREPARATION_INTEGRITY" else 1)
