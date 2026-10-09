import argparse
import hashlib
import json
import math
import pathlib
import platform
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta


ROOT = pathlib.Path(__file__).resolve().parents[4]
RUN = pathlib.Path(__file__).resolve().parent
RUN_REL = RUN.relative_to(ROOT).as_posix()
BASELINE = "3f6e327a0ff9adc04ed6c98c1578862b8c2fae64"
MODEL = "report/evidence/S2A-T01/tiny416_model_manifest.json"
SPEC = "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
DESIGN = "docs/obsidian-project/02-方案设计/系统设计.md"
CANDIDATE = "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
PLAN = "docs/obsidian-project/02-方案设计/B方案实施与阶段验收计划.md"
SOURCES = [
    "src/s2a_stage2a_core_ooc.sv", "src/s2a_runtime_shell.sv",
    "src/s2a_control_csr.sv", "src/s2a_memory_master.sv",
    "src/s2a_network_descriptor_pkg.sv", "src/s2a_network_backend.sv",
    "src/s2a_conv_tile_engine.sv", "src/s2a_route_engine.sv",
    "src/s2a_maxpool_engine.sv", "src/s2a_upsample_engine.sv",
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(name, data):
    # 所有输出均为UTF-8，并保留机器可读原始整数。
    (RUN / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def checked_file(relative):
    path = ROOT / relative
    current = ROOT
    for part in pathlib.PurePosixPath(relative).parts:
        if part not in [p.name for p in current.iterdir()]:
            raise ValueError(f"路径分量不存在或字符不精确：{relative}")
        current = current / part
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"不是普通文件：{relative}")
    return path


def compute():
    start = time.perf_counter()
    if subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() != BASELINE:
        raise ValueError("源码基线发生变化，停止尺寸分析")
    model_path = checked_file(MODEL)
    if digest(model_path) != "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a":
        raise ValueError("冻结manifest哈希不匹配")
    m = json.loads(model_path.read_text(encoding="utf-8"))
    translation, arena = 0x10000000, 0x02000000
    feature = m["address_map"]["feature_workspace"]
    layers, convs, intervals = [], [], []
    for item in m["layers"]:
        n = math.prod(item["output_shape_nchw"])
        if n != item["tensor_length_bytes"]:
            raise ValueError(f"shape/长度不一致：layer{item['layer_index']}")
        address, limit = item["tensor_address"], item["tensor_address"] + n
        row = {k: item[k] for k in ["layer_index", "op", "input_tensor_indices", "output_shape_nchw", "tensor_address", "tensor_length_bytes"]}
        row.update(logical_end_exclusive=limit, physical_address=translation + address,
                   physical_end_exclusive=translation + limit,
                   allocated=item["op"] != "yolo")
        if item["op"] == "yolo":
            row["alias_source_layer"] = item["output_tensor_index"]
            prior = m["layers"][item["output_tensor_index"]]
            if (address, n) != (prior["tensor_address"], prior["tensor_length_bytes"]):
                raise ValueError("YOLO不是精确零拷贝别名")
        else:
            if address % feature["alignment_bytes"] or limit > feature["end_address_exclusive"]:
                raise ValueError("特征对齐或范围不一致")
            intervals.append(row)
        if item["op"] == "convolutional":
            offsets = item["gf8_parameter_offsets"]
            oc = item["output_shape_nchw"][1]
            expected = oc * item["input_shape_nchw"][1] * math.prod(item["kernel_hw"]) // item["groups"]
            if expected != offsets["quantized_weight_bytes"]:
                raise ValueError("GF8权重OIHW字节数不一致")
            convs.append({"layer_index": item["layer_index"], "output_channels": oc,
                          "gf8_parameter_offsets": offsets,
                          "quantized_weight_end_offset": offsets["quantized_weight_offset"] + expected,
                          "scale_bytes": oc * 4, "float32_bias_bytes": oc * 4,
                          "shape_weight_bytes": expected})
        layers.append(row)
    gaps = []
    cursor = feature["base_address"]
    for row in sorted(intervals, key=lambda r: r["tensor_address"]):
        address = row["tensor_address"]
        if address < cursor:
            raise ValueError("独立张量重叠")
        if address > cursor:
            gaps.append({"logical_start": cursor, "logical_end_exclusive": address, "bytes": address - cursor})
        cursor = row["logical_end_exclusive"]
    if cursor != feature["end_address_exclusive"]:
        raise ValueError("feature尾地址不一致")
    objects = []
    for key in ["input", "weight_package"]:
        obj = m["address_map"][key]
        limit = obj["address"] + obj["length_bytes"]
        objects.append({"name": key, "logical_address": obj["address"], "length_bytes": obj["length_bytes"],
                        "logical_end_exclusive": limit, "physical_address": translation + obj["address"],
                        "physical_end_exclusive": translation + limit, "pl_access": "read_only"})
    if max(cursor, *(o["logical_end_exclusive"] for o in objects)) > arena:
        raise ValueError("对象超出专属arena")
    heads = []
    for h in m["address_map"]["heads"]:
        end = h["address"] + h["length_bytes"]
        tail = end - ((end - 1) & ~3)
        heads.append({**h, "logical_end_exclusive": end,
                      "physical_address": translation + h["address"], "physical_end_exclusive": translation + end,
                      "last_aligned_word": (end - 1) & ~3, "last_word_legal_mask": (1 << tail) - 1,
                      "cache_start_64": (translation + h["address"]) & ~63,
                      "cache_end_exclusive_64": (translation + end + 63) & ~63})
    projection = {"source_path": MODEL, "source_sha256": digest(model_path),
                  "source_bytes": model_path.stat().st_size, "model": m["model"],
                  "address_map": m["address_map"], "layers_consumed": layers, "gf8_offsets_consumed": convs,
                  "scope": "仅提取实际消费字段；不是重建或替代原冻结manifest"}
    dump("manifest_layout_projection.json", projection)
    feature_bytes = sum(r["tensor_length_bytes"] for r in intervals)
    weight_payload = sum(c["shape_weight_bytes"] for c in convs)
    channel_count = sum(c["output_channels"] for c in convs)
    gf8_bytes = m["address_map"]["weight_package"]["length_bytes"]
    if gf8_bytes != weight_payload + channel_count * 8 + len(convs) * 32 + 28:
        raise ValueError("GF8总字节与包头/记录/scale/bias/weight分解不一致")
    dump("layout_result.json", {
        "status": "PASS_READ_ONLY_LAYOUT_ANALYSIS", "source_commit": BASELINE,
        "created_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "source_manifest": {"path": MODEL, "sha256": digest(model_path)},
        "candidate_not_frozen": True, "translation": translation, "arena_bytes": arena,
        "objects": objects, "layers": layers, "heads": heads, "feature_gaps": gaps,
        "gf8_records": convs, "totals": {
            "layer_count": len(layers), "allocated_feature_count": len(intervals), "yolo_alias_count": len(heads),
            "convolution_count": len(convs), "conv_channel_count": channel_count,
            "feature_effective_bytes": feature_bytes,
            "feature_span_bytes": cursor - feature["base_address"],
            "feature_gap_bytes": sum(g["bytes"] for g in gaps),
            "gf8_package_bytes": gf8_bytes, "gf8_weight_payload_bytes": weight_payload,
            "gf8_header_record_scale_bias_bytes": gf8_bytes - weight_payload,
            "input_gf8_feature_effective_bytes": feature_bytes + sum(o["length_bytes"] for o in objects),
            "translated_used_span_bytes": cursor, "translated_used_span_MiB": cursor / 1048576,
            "arena_unused_tail_bytes": arena - cursor,
            "feature_cache_start": translation + feature["base_address"],
            "feature_cache_end_exclusive": (translation + cursor + 63) & ~63,
            "feature_cache_length": ((cursor + 63) & ~63) - feature["base_address"],
        }, "deadline": {
            "counter_width_bits": 32, "zero_illegal": True, "maximum_cycles": 0xFFFFFFFF,
            "candidate_clock_hz": 50000000, "maximum_seconds": 0xFFFFFFFF / 50000000,
            "core_deployment_cycles": None, "drain_deployment_cycles": None,
            "actual_full_network_requests": None, "actual_hp_latency_cycles": None,
            "reason": "未测完整38层请求/HP往返/计算与背压，不能凭下界确定部署deadline",
        }, "writes_only_lower_bound": {
            "logical_write_requests": feature_bytes, "axi_write_beats": feature_bytes,
            "basis": "conv_tile/route/maxpool/upsample源码均逐输出INT8 one-hot写；YOLO不另分配",
            "ignores": ["所有读取", "控制和计算周期", "握手背压", "PS解码/UART"],
            "serial_service_sensitivity": [{"assumed_cycles_per_write": n, "minimum_cycles": n * feature_bytes,
                "minimum_seconds_at_50MHz": n * feature_bytes / 50000000,
                "exceeds_32bit_deadline_from_writes_alone": n * feature_bytes > 0xFFFFFFFF}
                for n in [1, 10, 100, 500, 1000]],
            "largest_integer_service_cycles_per_write_within_maximum": 0xFFFFFFFF // feature_bytes,
            "not_a_performance_prediction": True,
        }, "source_findings": {
            "timeout_source": "src/s2a_control_csr.sv: timeout_cycles/elapsed_cycles为logic[31:0]，零非法",
            "global_timeout_source": "src/s2a_network_descriptor_pkg.sv: S2A_TIMEOUT_SCOPE_GLOBAL=1，PER_LAYER_TIMEOUT_RESTART=0",
            "byte_packing_source": "src/s2a_conv_tile_engine.sv: 地址向下4byte对齐，strobe按原byte低2bit one-hot",
        }, "elapsed_seconds": time.perf_counter() - start,
        "limitations": ["仅尺寸/地址/源码静态分析，不是RTL测试、吞吐实测或G0冻结", "未访问外部图像/模型参数文件", "峰值内存与本会话全部工具调用未测"],
    })
    snapshots = RUN / "snapshots"
    if snapshots.exists():
        raise ValueError("源码快照目录已存在，不覆盖分析Run")
    snapshots.mkdir()
    bindings = []
    for relative in SOURCES + [SPEC, DESIGN, CANDIDATE, PLAN, "verification/check_stage_delivery.py"]:
        path = checked_file(relative)
        destination = snapshots / path.name
        if destination.exists():
            raise ValueError("快照文件名冲突")
        shutil.copyfile(path, destination)
        bindings.append({"original_path": relative, "snapshot_path": destination.relative_to(ROOT).as_posix(),
                         "sha256": digest(path), "bytes": path.stat().st_size})
    dump("source_snapshot_bindings.json", {"source_commit": BASELINE, "files": bindings,
         "manifest_projection": "完整manifest仍以原文件哈希绑定，投影仅保留消费字段，未复制22MB随机向量"})
    print(json.dumps({"status": "PASS_READ_ONLY_LAYOUT_ANALYSIS", "feature_bytes": feature_bytes,
        "gf8_bytes": gf8_bytes, "feature_span_bytes": cursor - feature["base_address"]}, ensure_ascii=False))


def manifest():
    execution = json.loads((RUN / "analysis_execution.json").read_text(encoding="utf-8"))
    checks = [{"name": "冻结manifest尺寸和地址只读计算", "status": "PASS" if execution["exit_code"] == 0 else "FAIL",
               "command": execution["command"], "exit_code": execution["exit_code"],
               "reason": "仅计算冻结元数据并读取源码，未执行RTL/软件测试或板卡操作"}]
    if (RUN / "packaging_execution.json").exists():
        packaging = json.loads((RUN / "packaging_execution.json").read_text(encoding="utf-8"))
        checks.append({"name": "初次候选证据包装核查", "status": "PASS" if packaging["exit_code"] == 0 else "FAIL",
                       "command": packaging["command"], "exit_code": packaging["exit_code"],
                       "reason": "仅哈希/清单检查，不代表接口语义、G0/G2或实物通过；最终清单另由总控核查"})
    for name, status, reason in [
        ("完整2B物理G0冻结", "BLOCKED", "AXI配置/可见性、集成reset/linker/cache软件、部署deadline及后续验证尚未完成"),
        ("独立候选技术审查", "NOT_RUN", "Developer停止写入后由总控创建独立Reviewer"),
        ("RTL与软件功能验证", "NOT_RUN", "本子任务只设计和计算，不实现或运行测试"),
        ("实板传输与100样本/1000连续任务", "NOT_RUN", "本子任务未操作实物，正式验收数量保留"),
    ]:
        checks.append({"name": name, "status": status, "command": None, "exit_code": None, "reason": reason})
    files = []
    for relative in SOURCES + [SPEC, DESIGN, CANDIDATE, PLAN, MODEL]:
        files.append({"path": relative, "sha256": digest(checked_file(relative)), "role": "input" if relative == MODEL else "source"})
    for path in sorted(RUN.rglob("*")):
        if path.is_file() and path.name != "delivery_manifest.json":
            role = "source" if path.suffix in [".py", ".sv", ".md"] else "log" if path.name.endswith("console.txt") else "result"
            files.append({"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "role": role})
    dump("delivery_manifest.json", {
        "schema_version": 1, "stage": "2B", "task_id": "S2B-T07", "run_id": RUN.name,
        "source_commit": BASELINE, "evidence_dir": RUN_REL,
        "interfaces": [
            {"name": "2A冻结模型/逻辑CSR/单word memory接口", "version": "2026-09-23", "frozen": True, "path": SPEC, "sha256": digest(checked_file(SPEC))},
            {"name": "已批准恢复原则，仅停止/排空/安全归还及未排空隔离", "version": "s2b-axi-recovery-principles/1.0.0", "frozen": True, "path": DESIGN, "sha256": digest(checked_file(DESIGN))},
            {"name": "2B物理接口工程候选，不是正式冻结", "version": "s2b-physical-candidate/0.1.0", "frozen": False, "path": CANDIDATE, "sha256": digest(checked_file(CANDIDATE))},
        ], "files": files, "checks": checks,
        "tool_versions": {"python": platform.python_version(), "git": subprocess.check_output(["git", "--version"], text=True).strip()},
        "limitations": ["只读元数据尺寸/源码分析与候选设计；没有RTL/BD/XSA/软件实现、测试、实物结果", "恢复原则批准不能替代完整物理接口冻结", "完整请求/HP延迟未测，32bit deadline部署值未定", "包装CHECKS_OK不代表G0/G2/G3/G4/G5", "最终候选审查与提交由总控负责，Developer不提交", "原manifest与现存源码哈希绑定，快照不修改原件"],
    })


def execute_analysis():
    command = [sys.executable, "-B", str(pathlib.Path(__file__).resolve()), "--mode", "compute"]
    started = datetime.now(timezone(timedelta(hours=8))).isoformat()
    start = time.perf_counter()
    result = subprocess.run(command, cwd=ROOT, capture_output=True)
    (RUN / "analysis_console.txt").write_bytes(result.stdout + result.stderr)
    dump("analysis_execution.json", {"command": f"python -B {RUN_REL}/layout_analysis.py --mode compute", "argv": command,
         "cwd": str(ROOT), "started_utc8": started, "exit_code": result.returncode,
         "elapsed_seconds": time.perf_counter() - start, "actual_compute_attempt_count": 1,
         "peak_memory": None, "scope": "只读分析，不运行测试"})
    if result.returncode:
        print((result.stdout + result.stderr).decode("utf-8", errors="replace"))
        raise SystemExit(result.returncode)
    manifest()
    command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", "evidence", "--manifest", f"{RUN_REL}/delivery_manifest.json"]
    result = subprocess.run(command, cwd=ROOT, capture_output=True)
    (RUN / "packaging_initial_console.txt").write_bytes(result.stdout + result.stderr)
    dump("packaging_execution.json", {"command": f"python -B verification/check_stage_delivery.py --mode evidence --manifest {RUN_REL}/delivery_manifest.json", "argv": command,
         "exit_code": result.returncode, "scope": "初次清单包装只读核查；随后新增此命令日志并刷新清单"})
    manifest()
    print((RUN / "analysis_console.txt").read_text(encoding="utf-8"))
    print(f"初次包装退出码={result.returncode}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["compute", "run", "manifest"], required=True)
    mode = parser.parse_args().mode
    {"compute": compute, "run": execute_analysis, "manifest": manifest}[mode]()
