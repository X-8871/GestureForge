#!/usr/bin/env python3
"""只读复算本次限定CPU/DAP 256字节探针；不导入SDK，不连接设备。"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import pathlib
import struct
import subprocess
import sys
import zipfile

BASELINE = "d49f9b8d5bd5ec3f8d791a3f425aa7691c79f37c"
EXECUTION = "report/evidence/S2B-T19/cache_probe_execution_20261015_r01"
PACKAGE = "report/evidence/S2B-T19/cache_probe_acceptance_20261015_r01"
AUX_NAMES = ("visibility_probe_config.json", "readonly_preflight.json", "probe_launcher_execution.json",
             "vitis_probe_stdout.log", "hw_server_identity.json", "hw_server_stdout.log",
             "hw_server_stderr.log", "launcher_identity.json")
HEADER = struct.Struct("<4sHH8I")
import zlib

def require(ok, message):
    """每一项必须由现存原字节与记录共同支持。"""
    if not ok:
        raise ValueError(message)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def file_sha(path):
    with path.open("rb") as stream:
        h = hashlib.file_digest(stream, "sha256")
    return h.hexdigest()

def frame(header, payload, op, seq):
    """独立按固定协议布局校验，不复用主机协议实现。"""
    require(len(header) == 40, "头长度错误")
    magic, version, actual_op, actual_seq, image, width, height, repeat, length, crc, hcrc = HEADER.unpack(header)
    require((magic, version, actual_op, actual_seq, image, width, height, repeat) ==
            (b"S2BU", 1, op, seq, 0, 0, 0, 1), "协议身份/序号/请求种类错误")
    require(length == len(payload) and zlib.crc32(payload) == crc, "负载长度/CRC错误")
    require(zlib.crc32(header[:36]) == hcrc, "头CRC错误")

def audit(root, auxiliary):
    """在内存中核查运行、平台、收据、帧、读回与清理，返回确定性摘要。"""
    folder = root / EXECUTION
    result = read_json(folder / "visibility_probe_result.json")
    jtag = read_json(folder / "jtag_result.json")
    config_raw = (folder / "input_config.json").read_bytes()
    config = json.loads(config_raw)
    build = read_json(folder / "bound_build_details.json.raw")
    receipt = read_json(folder / "bound_compat_review.json.raw")
    platform = read_json(folder / "bound_platform_manifest.json.raw")
    entry = [json.loads(line) for line in (folder / "entry_calls.jsonl").read_text(encoding="utf-8").splitlines()]
    calls = [json.loads(line) for line in (folder / "jtag_calls.jsonl").read_text(encoding="utf-8").splitlines()]
    require(result["source_commit"] == config["source_commit"] == BASELINE, "运行源码提交错误")
    require(result["status"] == jtag["status"] == "API_OBSERVATIONS_SAVED_ACCEPTANCE_PENDING", "原始状态不是待验收")
    require(result["native_exit_code"] == 0 and result["cleanup_errors"] == jtag["cleanup_errors"] == [], "原始运行/清理失败")
    require(result["cold_lifecycle_proven"] is False and jtag["cold_lifecycle_proven"] is False, "不得提升冷生命周期证明")
    require(len(entry) == 52 and len(calls) == 376 and sorted(entry, key=lambda x: (x["time_utc8"], x["api"])) == sorted(result["calls"], key=lambda x: (x["time_utc8"], x["api"])) and calls == jtag["calls"], "调用记录不完整/不一致")
    require(all(row["status"] == "RETURNED" for row in entry + calls), "存在RAISED/非返回调用")
    require(result["config_sha256"] == sha(config_raw), "配置哈希错误")
    require(config_raw == (auxiliary / "visibility_probe_config.json").read_bytes(), "启动配置原字节不一致")

    bindings = {}
    def bind(path, expected):
        """仅绑定仓库现存文件；临时源由归档副本独立绑定。"""
        p = pathlib.Path(path)
        if not p.is_absolute():
            p = root / p
        try:
            relative = p.relative_to(root).as_posix()
        except ValueError:
            allowed = [config["bindings"][key] for key in ("sdk_init", "sdk_target")]
            require(any(str(p) == item["path"] and expected == item["sha256"] for item in allowed), "未授权的外部工具源")
            relative = PACKAGE + "/sdk_source_snapshot/" + p.name
            if auxiliary.name == "launcher_raw":
                p = root / relative
        require(p.is_file() and file_sha(p) == expected, "输入哈希错误：" + relative)
        require(relative not in bindings or bindings[relative] == expected, "输入哈希冲突")
        bindings[relative] = expected
        return p
    for item in platform["files"]:
        bind(item["path"], item["sha256"])
    for key, record in result["raw_json_inputs"].items():
        saved = pathlib.Path(record["saved_path"])
        require(file_sha(saved) == record["sha256"] == record["binding"]["sha256"], "运行保存的JSON哈希错误")
        if key != "owned_server":
            require(bind(record["binding"]["path"], record["sha256"]).read_bytes() == saved.read_bytes(), "JSON来源与运行副本不一致")
    for key, item in config["bindings"].items():
        if key != "pyserial_init":
            bind(item["path"], item["sha256"])
    for mapping in (build["source_sha256"], result["verified_inputs"]["source_sha256"], receipt["source_sha256"]):
        for path, expected in mapping.items():
            bind(path, expected)
    for item in receipt["artifacts"].values():
        bind(item["path"], item["sha256"])
    bind(config["cold_basis"]["path"], config["cold_basis"]["sha256"])
    provenance_path = root / "report/evidence/S2B-T19/current_probe_independent_20261015_r01/review_provenance.json"
    provenance = read_json(provenance_path)
    require(provenance["verdict"] == "PASS" and provenance["role"] == "INDEPENDENT_REVIEWER" and
            provenance["scope"] == "visibility0_cache_probe_only", "入场独审来源不符")
    for path, expected in provenance["frozen_reviewed_inputs"].items():
        bind(path, expected)
    bind(provenance["independent_raw_review_source"]["path"], provenance["independent_raw_review_source"]["sha256"])
    bind(provenance_path, file_sha(provenance_path))
    require(receipt["role"] == "INDEPENDENT_REVIEWER" and receipt["status"] == "PASS" and
            receipt["visibility_parameter"] == 0 and receipt["scope"] == "visibility0_cache_probe_only" and
            all(receipt["checks"].values()), "入场限定收据不符")
    require(file_sha(folder / "bound_compat_review.json.raw") ==
            "e22fd0a1fa0399de48d9694dd07c7b10e06dbb60f55aed7ce8a9057fc3d4c7ea", "独审固定哈希错误")
    for name, info in result["saved_files"].items():
        p = folder / name
        require(p.stat().st_size == info["bytes"] and file_sha(p) == info["sha256"], "原始产物绑定错误")
    require(result["source_sha256"] == config["bindings"]["entry_source"]["sha256"], "入口源码绑定错误")

    artifacts = receipt["artifacts"]
    require(artifacts == result["verified_inputs"]["compat_artifacts"], "平台产物绑定不一致")
    with zipfile.ZipFile(artifacts["implemented_xsa"]["path"]) as archive:
        bits = [n for n in archive.namelist() if n.endswith(".bit")]
        require(len(bits) == 1 and sha(archive.read(bits[0])) == artifacts["bit"]["sha256"], "实际部署XSA/bit不一致")
    with zipfile.ZipFile(artifacts["compiled_xsa"]["path"]) as archive:
        for name, expected in jtag["postconfig_basis"]["member_sha256"].items():
            require(sha(archive.read(name)) == expected, "PS初始化生成依据不一致")
    require(build["xsa_sha256"] == artifacts["compiled_xsa"]["sha256"], "ELF编译XSA绑定错误")
    require(jtag["bindings"] == config["bindings"], "JTAG源码绑定不一致")
    by_api = {}
    for row in calls:
        by_api.setdefault(row["api"], []).append(row)
    entry_api = {row["api"]: row for row in entry}
    for api, key in (("cpu0.dow.init", "init_elf"), ("cpu0.dow.app", "app_elf"), ("fpga.full.compatibility_default", "bit")):
        require(len(by_api[api]) == 1 and by_api[api][0]["kwargs"]["file"] == artifacts[key]["path"], "实际下载路径不符")
    require(by_api["apu.rst.system.stop"][0]["args"] == ["--stop"] and
            by_api["apu.rst.system.stop"][0]["kwargs"] == {"type": "system"}, "复位调用不符")

    seeds = (722665479, 722665480)
    require((config["cpu_seed"], config["dap_seed"]) == seeds, "种子错误")
    # 独立按CPU源码约定生成全部64个小端字；首、次字同时提供常量锚点。
    words = [[seed ^ ((2654435769 * index) % (2 ** 32)) for index in range(64)] for seed in seeds]
    require(words[0][:2] == [722665479, 3039066558] and words[1][:2] == [722665480, 3039066545], "模式常量错误")
    expected = [struct.pack("<64I", *w) for w in words]
    probe = result["cache_probe"]
    require(probe == jtag["cache_probe"] and probe["address"] == 0x10000000 and
            (probe["cpu_seed"], probe["dap_seed"]) == seeds, "两份探针记录/地址/种子不一致")
    rx = (folder / "uart_rx_raw.bin").read_bytes()
    tx = (folder / "uart_tx_headers.bin").read_bytes()
    banner = result["banner"]["text"].encode("utf-8")
    require(rx.startswith(banner) and len(banner) == result["banner"]["bytes"] and sha(banner) == result["banner"]["sha256"], "READY原始字节错误")
    require(build["source_sha256"]["vitis/s2b_inference_app.c"].encode() in banner and
            artifacts["compiled_xsa"]["sha256"].encode() in banner, "READY的应用/XSA身份错误")
    offset = len(banner)
    event_rows = result["uart_events"]
    require(len(event_rows) == 4 and len(tx) == 80, "UART请求数量不符")
    phase_summary = []
    for phase in range(2):
        rec = probe["phase%d_receipt" % phase]
        payload = struct.pack("<III", phase, *seeds)
        htx = tx[phase * 40:(phase + 1) * 40]
        hrx = rx[offset:offset + 40]
        prx = rx[offset + 40:offset + 336]
        frame(htx, payload, 4, phase + 1)
        frame(hrx, prx, 0x8004, phase + 1)
        require((htx.hex(), payload.hex(), hrx.hex(), prx.hex()) ==
                (rec["request_header_hex"], rec["request_payload_hex"], rec["header_hex"], rec["payload_hex"]), "原始UART与receipt不一致")
        meta = struct.unpack("<Q8I", prx[:40])
        require(meta == (0, 0x400, 0, 0, 0, 0, 0, 1, 0), "响应不是epoch0/IDLE/成功")
        require(prx[40:] == expected[phase] == bytes.fromhex(probe["phase%d_raw_hex" % phase]), "CPU侧256字节全量比较失败")
        sent = by_api["wire.OP4.send"][phase]
        received = ast.literal_eval(by_api["wire.OP4.receive_actual"][phase]["return_repr"])
        require(ast.literal_eval(sent["args"][1]) == htx and ast.literal_eval(sent["args"][2]) == payload, "实际发送调用原字节不符")
        require(received["header_hex"] == hrx.hex() and received["payload_hex"] == prx.hex() and
                received["meta"]["probe_bytes"] == expected[phase], "实际接收调用原字节不符")
        txe, rxe = event_rows[phase * 2:phase * 2 + 2]
        require(txe["direction"] == "TX" and txe["op"] == 4 and txe["sequence"] == phase + 1 and
                txe["payload_sha256"] == sha(payload) and txe["header_sha256"] == sha(htx) and
                txe["sent_sha256"] == sha(htx + payload) and txe["sent_bytes"] == 52, "TX事件绑定错误")
        require(rxe["direction"] == "RX" and rxe["header"]["op"] == 0x8004 and
                rxe["header_sha256"] == sha(hrx) and rxe["payload_sha256"] == sha(prx), "RX事件绑定错误")
        phase_summary.append({"phase": phase, "sequence": phase + 1, "bytes_compared": 256,
                              "seed": seeds[phase], "data_sha256": sha(expected[phase]), "metadata": list(meta)})
        offset += 336
    require(offset == len(rx) == 907, "RX存在未解析/缺失字节")
    require(len(by_api["wire.OP4.send"]) == len(by_api["wire.OP4.receive_actual"]) == 2, "存在额外协议请求")

    read_calls = by_api["apu.mrd"]
    readbacks = jtag["readbacks"]
    require(len(read_calls) == len(readbacks), "DAP调用与读回数量不符")
    for row, back in zip(read_calls, readbacks):
        values = ast.literal_eval(row["return_repr"])
        values = [values] if row["kwargs"]["size"] == 1 else values
        require(row["kwargs"]["address"] == back["address"] and values == back["words"] and
                row["kwargs"]["size"] == len(values) and row["kwargs"]["word_size"] == 4 and
                struct.pack("<%dI" % len(values), *values).hex() == back["raw_le_hex"], "DAP全字节回读与调用不一致")
    dap_reads = [row for row in readbacks if row["address"] == 0x10000000]
    require(len(dap_reads) == 2 and [row["words"] for row in dap_reads] == words, "DAP双方256字节比较失败")
    write = by_api["apu.mwr.cache_probe.bypass"]
    require(len(write) == 1 and write[0]["args"] == ["--bypass_cache_synq"] and
            write[0]["kwargs"] == {"address": 0x10000000, "size": 64, "word_size": 4, "words": words[1]}, "DAP绕缓存写原字节错误")

    expected_csr = {"0": 1395802704, "4": 256, "12": 1024, "16": 0, "20": 0, "24": 0,
                    "28": 519168, "32": 1048576, "36": 5903100, "40": 0, "44": 0,
                    "48": 268435456, "52": 33554432, "56": 16777216, "60": 28159416,
                    "64": 27549952, "68": 5070, "72": 28139136, "76": 20280,
                    **{str(n): 0 for n in range(80, 120, 4)}}
    windows = [back for back in readbacks if back["address"] == 0x43C0000C and len(back["words"]) == 27]
    require(len(windows) == 16 and all(back["words"] == [expected_csr[str(n)] for n in range(12,120,4)] for back in windows), "CSR实际27字窗口非稳定默认值")
    stable = jtag["stable_csr"]
    require(len(stable) == 8 and all(s["first"] == s["second"] == expected_csr for s in stable), "CSR摘要/双读不一致")
    require(result["final_csr"] == jtag["postconfiguration"]["cold_csr"] == expected_csr, "最终CSR不符")
    boot = [back for back in readbacks if back["address"] == 0xF800025C]
    require(boot and all(back["words"] == [0] for back in boot), "实际BOOT_MODE非JTAG=0")
    for core in (0, 1):
        name = "ARM Cortex-A9 MPCore #%d" % core
        require(ast.literal_eval(entry_api["stopped."+name+".state"]["return_repr"]).startswith("Stopped"), "入场CPU未停止")
    require(all(ast.literal_eval(row["return_repr"]).startswith("Stopped") for row in by_api["cpu1.state"]), "CPU1离散状态非停止")
    require(ast.literal_eval(entry_api["completed_probe_cpu0.state_after"]["return_repr"]).startswith("Stopped"), "结束CPU0未停止")
    init = jtag["initialization"]
    symbols = jtag["init_symbols"]
    require(init["result"] == 2 and init["return_code"] == 0 and init["ready_address"] == symbols["s2b_ps_init_ready"], "PS初始化未成功")
    for key, value in (("s2b_ps_init_result", 2), ("s2b_ps_init_return", 0)):
        require(any(b["address"] == symbols[key] and b["words"] == [value] for b in readbacks), "初始化实际回读缺失")
    require(any(ast.literal_eval(row["return_repr"])["pc"] == symbols["s2b_ps_init_ready"] for row in by_api["cpu0.rrd.pc"]), "初始化ready PC缺失")
    post = jtag["postconfiguration"]
    require(post["status"] == "PASS" and post["cleanup"] == [] and post["steps"][0]["locksta"] == 0 and
            post["steps"][-1]["locksta"] == 1, "postconfig锁定/清理错误")
    for step in post["steps"][1:-1]:
        calculated = (step["before"] & (~step["mask"] & 0xffffffff)) | (step["value"] & step["mask"])
        require(calculated == step["expected"] == step["after"] and step["status"] == "PASS", "postconfig掩码回读错误")
    for observe in post["clock_observations"]:
        require(observe["clock_word"] & observe["clock_mask"] == observe["clock_expected"] and
                all(observe["pll_word"] & mask == mask for mask in observe["pll_masks"]), "时钟寄存器观测错误")
    for observe in jtag["configuration_observations"]:
        require((observe["status_word"] >> 4) & 1 == observe["expected_eos"] == observe["eos"], "配置EOS实际值错误")
    require(result["debug_memory_map"]["range"] == [0x43C00000, 0x43C0FFFF] and
            result["debug_memory_map"]["cleanup"] == "OWNED_HW_MAP_CLEARED", "自有CSR映射范围/清理错误")
    for api in ("serial.close", "controller.close", "apu.unloadhw.owned_map", "owned_csr_debug_map.clear", "session.disconnect", "xsdb.dispose"):
        require(api in entry_api and entry_api[api]["status"] == "RETURNED", "清理调用缺失：" + api)
    require(result["serial_closed"] is True and result["uart_failed"] is False and result["owned_hw_server_released"] is False, "串口/外部服务器状态不符")
    for snapshot in result["identity_snapshots"]:
        decoded = json.loads(bytes.fromhex(snapshot["stdout_hex"]))
        require(decoded == snapshot["snapshot"] and snapshot["native_exit_code"] == 0 and snapshot["stderr_hex"] == "", "身份快照原始字节错误")
        require(decoded["servers"][0]["ProcessId"] == 27580 and decoded["listeners"][0]["OwningProcess"] == 27580, "服务器身份漂移")

    launcher = read_json(auxiliary / "probe_launcher_execution.json")
    preflight = read_json(auxiliary / "readonly_preflight.json")
    require(launcher["native_exit_code"] == launcher["wrapper_exit_code"] == 0 and launcher["owned_launcher_pid"] == 27640 and
            abs(launcher["elapsed_seconds"] - 107.672) < 0.000001 and launcher["stop_reason"] is None, "外层执行收据错误")
    require(launcher["config_sha256"] == preflight["config_sha256"] == sha(config_raw) and
            preflight["source_commit"] == BASELINE and preflight["sdk_imported"] is False and
            preflight["hardware_actions"] is False, "只读入场收据错误")
    for name, observed in result["runtime_sdk_sources"].items():
        require(name in config["sdk_files"] and observed["sha256"] == config["sdk_files"][name]["sha256"] and
                observed["path"] == config["sdk_files"][name]["path"], "运行时SDK来源哈希不符")
    require(result["runtime_modules"]["vitis_environment_version"] == "Vitis v2026.1 (64-bit)", "实际工具版本不符")
    auxiliary_hashes = {name: file_sha(auxiliary / name) for name in AUX_NAMES}
    require(auxiliary_hashes["hw_server_identity.json"] == config["owned_hw_server_identity"]["sha256"] ==
            file_sha(folder / "bound_owned_server.json.raw"), "服务器身份归档不一致")
    return {"schema_version": 1, "status": "LIMITED_CPU_DAP_256B_PROBE_PASS",
            "source_commit": BASELINE, "cold_lifecycle_proven": False,
            "execution_run": EXECUTION, "address": "0x10000000", "phases": phase_summary,
            "entry_calls_returned": 52, "jtag_calls_returned": 376, "dap_readback_count": len(readbacks),
            "stable_csr_pairs": len(stable), "actual_csr_27word_windows": len(windows),
            "cpu1_stopped_discrete_observations": len(by_api["cpu1.state"]),
            "ps_init_result": 2, "ps_init_return_code": 0, "ps_init_ready_pc": symbols["s2b_ps_init_ready"],
            "final_csr": expected_csr, "cleanup_errors": [], "serial_closed": True,
            "owned_map_cleanup": "OWNED_HW_MAP_CLEARED", "owned_hw_server_released": False,
            "launcher_native_exit_code": 0, "launcher_wrapper_exit_code": 0,
            "launcher_elapsed_seconds": launcher["elapsed_seconds"], "entry_elapsed_seconds": result["elapsed_seconds"],
            "peak_process_tree_memory_bytes": None, "hardware_repetition_count": 1,
            "external_confirmation": {"source": "用户经总控转述", "text": "已重新上电，JTAG模式，继续", "instrument_measurement": False},
            "limitations": ["仅覆盖CPU0/DAP交叉可见性起始256字节；不经PL/HP0，不证明32 MiB arena。",
                            "仅两个OP4；未发送LOAD或START，不替代整网G0、100样本、1000连续任务或异常恢复。",
                            "外部重新上电确认不等于仪器测量；system-stop不证明物理POR或旧AXI生命周期结束。",
                            "CPU1和CPU0状态为离散观测；时钟值是寄存器观测，未实测频率；峰值内存未测。",
                            "自有hw_server PID27580由总控管理，本验收不操作或关闭；本包独立G2审查待后续执行。"],
            "external_tool_dependency": {"vitis_environment_version": result["runtime_modules"]["vitis_environment_version"],
                    "pyserial_version": result["runtime_modules"]["pyserial_version"],
                    "configured_sdk_files": len(config["sdk_files"]),
                    "runtime_sdk_modules": len(result["runtime_sdk_sources"]),
                    "configured_pyserial_files": len(config["pyserial_files"]),
                    "restoration": "安装同一Vitis2026.1和pyserial，逐项匹配input_config.json中的路径/哈希；本包仅快照SDK __init__.py和target.py，未封存全部外部SDK或原生库。"},
            "auxiliary_sha256": auxiliary_hashes, "input_bindings": dict(sorted(bindings.items()))}

def main():
    """--verify仅只读复算及校验清单；允许真实后代提交且所有绑定文件保持相同哈希。"""
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--verify", action="store_true")
    mode.add_argument("--audit", action="store_true")
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path(__file__).resolve().parents[4])
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    subprocess.run(["git", "merge-base", "--is-ancestor", BASELINE, "HEAD"], cwd=root, check=True, capture_output=True)
    package = root / PACKAGE
    actual = audit(root, package / "launcher_raw")
    require(actual == read_json(package / "summary.json"), "摘要与独立复算不一致")
    if args.audit:
        print(json.dumps({"status": "AUDIT_OK", "scope": actual["status"], "cold_lifecycle_proven": False}, ensure_ascii=False))
        return 0
    manifest = read_json(package / "delivery_manifest.json")
    require(manifest["source_commit"] == BASELINE, "清单基线错误")
    for item in manifest["files"]:
        p = root / item["path"]
        require(p.is_file() and file_sha(p) == item["sha256"], "清单绑定漂移：" + item["path"])
    print(json.dumps({"status": "VERIFY_OK", "scope": actual["status"], "entry_calls": 52,
                      "jtag_calls": 376, "phases": 2, "bytes_per_phase": 256,
                      "bound_files": len(manifest["files"]), "cold_lifecycle_proven": False}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"status": "VERIFY_FAILED", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)

