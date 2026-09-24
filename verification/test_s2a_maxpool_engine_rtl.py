"""在系统临时目录编译并运行 S2A-T14 maxpool datapath smoke test。"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import subprocess
import tempfile
import time
import unittest
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[1]
_BASELINE_HEAD = "0cf68a8f12d8b675737a829ef82e07aec348ff0c"
_MANIFEST = _ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
_MANIFEST_SHA = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
_XILINX_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")
_EVIDENCE = _ROOT / "report/evidence/S2A-T14/maxpool_simulation.json"
_G0_SPEC = _ROOT / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(tool: Path, args: list[str], cwd: Path, log: Path,
         deadline: float) -> tuple[int, str]:
    remain = deadline - time.monotonic()
    if remain <= 0:
        raise TimeoutError("T14 smoke Vivado 总计超过 600 秒")
    cmd = " ".join(f'"{v}"' if (" " in v or "&" in v) else v
                   for v in [str(tool), *args])
    result = subprocess.run(
        f'cmd.exe /d /s /c "{cmd}"', cwd=cwd, shell=False,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=remain, check=False,
    )
    output = result.stdout + "\n" + result.stderr
    log.write_text(output, encoding="utf-8", newline="\n")
    return result.returncode, output


def _write_ranges(work: Path, manifest: dict) -> str:
    address_map = manifest["address_map"]
    image = address_map["input"]
    weights = address_map["weight_package"]
    workspace = address_map["feature_workspace"]
    ranges = sorted({
        (int(layer["tensor_address"]),
         int(layer["tensor_address"]) + int(layer["tensor_length_bytes"]))
        for layer in manifest["layers"] if layer.get("op") != "yolo"
    })
    lines = [
        f"{int(image['address']):08X} {int(image['address']) + int(image['length_bytes']):08X} "
        f"{int(weights['address']):08X} {int(weights['address']) + int(weights['length_bytes']):08X} "
        f"{len(ranges):08X}\n"
    ]
    lines.extend(f"{start:08X} {end:08X}\n" for start, end in ranges)
    payload = "".join(lines).encode("ascii")
    (work / "memory_ranges.dat").write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def _load_runner(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载冻结 oracle runner：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _canonical_sha(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=True).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _initial_byte(address: int) -> int:
    return ((address & 0xFF) ^ ((address >> 8) & 0xFF) ^
            ((address >> 16) & 0xFF) ^ ((address >> 24) & 0xFF) ^ 0xA5)


def _materialize_official_vectors(manifest: dict, work: Path,
                                  source_hashes: dict[str, str]) -> dict:
    """复用 T04 官方 selector 流，并分离 T10 memory golden 与 G0 candidate golden。"""
    t03_runner_path = _ROOT / "verification/test_s2a_maxpool_rtl.py"
    t04_runner_path = _ROOT / "verification/test_s2a_maxpool_geometry_rtl.py"
    t03 = _load_runner(t03_runner_path, "s2a_t14_t03_oracle")
    t04 = _load_runner(t04_runner_path, "s2a_t14_t04_oracle")
    t03_vectors = work / "t03_vectors.dat"
    t04_vectors = work / "t04_vectors.dat"
    t03_result = t03._materialize_vectors(manifest, t03_vectors)
    t04_result = t04._materialize_vectors(manifest, t04_vectors)

    t03_evidence_path = _ROOT / "report/evidence/S2A-T03/maxpool_window_simulation.json"
    t04_evidence_path = _ROOT / "report/evidence/S2A-T04/maxpool_geometry_simulation.json"
    t03_evidence = json.loads(t03_evidence_path.read_text(encoding="utf-8"))
    t04_evidence = json.loads(t04_evidence_path.read_text(encoding="utf-8"))
    if (t03_evidence.get("status") != "PASS" or
            t03_evidence["bindings"].get("manifest_sha256") != _MANIFEST_SHA or
            t03_evidence["bindings"].get("rtl_sha256") != source_hashes["src/int8_maxpool_window.sv"] or
            t03_evidence["bindings"].get("testbench_sha256") != source_hashes["sim/tb_s2a_maxpool_window.sv"] or
            t03_evidence["bindings"].get("test_script_sha256") != source_hashes["verification/test_s2a_maxpool_rtl.py"] or
            t03_evidence["bindings"].get("materialized_vector_sha256") != t03_result["vector_sha256"] or
            t03_evidence["bindings"].get("golden_output_sha256") != t03_result["golden_output_sha256"]):
        raise AssertionError("T03 candidate-value evidence/source/oracle mismatch")
    if (t04_evidence.get("result") != "PASS" or
            t04_evidence["bindings"].get("manifest_sha256") != _MANIFEST_SHA or
            t04_evidence["bindings"].get("rtl_sha256") != source_hashes["src/int8_maxpool_geometry.sv"] or
            t04_evidence["bindings"].get("testbench_sha256") != source_hashes["sim/tb_s2a_maxpool_geometry.sv"] or
            t04_evidence["bindings"].get("runner_sha256") != source_hashes["verification/test_s2a_maxpool_geometry_rtl.py"] or
            t04_evidence["bindings"].get("vector_sha256") != t04_result["vector_sha256"] or
            t04_evidence["bindings"].get("logical_vector_sha256") != t04_result["logical_vector_sha256"] or
            t04_evidence["bindings"].get("golden_output_sha256") != t04_result["golden_output_sha256"]):
        raise AssertionError("T04 official-coordinate evidence/source/oracle mismatch")

    expected_layers = {9: (128, 104, 104, 52, 52),
                       17: (256, 52, 52, 26, 26),
                       25: (512, 26, 26, 13, 13)}
    layer_map = {int(layer["layer_index"]): layer for layer in manifest["layers"]}
    rows: list[str] = []
    stimuli: list[dict] = []
    memory_goldens: list[dict] = []
    counts = {layer: {"random": 0, "directed": 0, "legal_memory_windows": 0,
                      "raw_0x80_rejected": 0} for layer in expected_layers}
    directed_candidates: list[dict] = []
    for layer_index in (9, 17, 25):
        for item in manifest["operator_test_plan"]["directed_case_vectors"]["maxpool"][str(layer_index)]:
            candidates = list(map(int, item["candidate_values_int8"]))
            expected = int(item["expected_output_int8"])
            if len(candidates) != 4 or max(candidates) != expected:
                raise AssertionError("G0 directed candidate-value golden mismatch")
            directed_candidates.append({"layer_index": layer_index,
                                        "case_index": int(item["case_index"]),
                                        "candidate_values_int8": candidates,
                                        "expected_output_int8": expected})

    vector_lines = t04_vectors.read_text(encoding="ascii").splitlines()
    cursor = 0
    while cursor < len(vector_lines):
        fields = vector_lines[cursor].split()
        cursor += 1
        if len(fields) != 24:
            raise AssertionError("T04 vector header width changed")
        vector_class, layer_index, case_index = map(int, fields[:3])
        base = int(fields[3]); channels, height, width = map(int, fields[4:7])
        kernel_h, kernel_w, stride_y, stride_x, padding = map(int, fields[7:12])
        channel, output_y, output_x = map(int, fields[12:15])
        out_h, out_w, tap_count, tap_mask, geom_error = map(int, fields[15:20])
        candidate_values = list(map(int, fields[20:24]))
        if cursor + 9 > len(vector_lines):
            raise AssertionError("T04 vector truncated in tap records")
        tap_rows = [vector_lines[cursor + offset].split() for offset in range(9)]
        cursor += 9
        if vector_class == 2:
            continue
        if vector_class not in (0, 1) or layer_index not in expected_layers:
            raise AssertionError("T04 contains unknown model vector class/layer")
        layer = layer_map[layer_index]
        producer = layer_map[int(layer["input_tensor_indices"][0])]
        exp_c, exp_h, exp_w, exp_oh, exp_ow = expected_layers[layer_index]
        if (base != int(producer["tensor_address"]) or
                (channels, height, width, out_h, out_w) !=
                (exp_c, exp_h, exp_w, exp_oh, exp_ow) or
                (kernel_h, kernel_w, stride_y, stride_x, padding) != (2, 2, 2, 2, 1) or
                tap_count != 4 or tap_mask != 15 or geom_error != 0 or
                candidate_values.__len__() != 4):
            raise AssertionError(f"G0 maxpool descriptor mismatch at layer {layer_index}")
        addresses: list[int] = []
        for tap_index in range(4):
            tap = list(map(int, tap_rows[tap_index]))
            if len(tap) != 6 or tap[0] != 1:
                raise AssertionError("model maxpool tap is not a valid source byte")
            expected_y = output_y * 2 + tap_index // 2
            expected_x = output_x * 2 + tap_index % 2
            expected_address = base + ((channel * height + expected_y) * width + expected_x)
            if ((tap[1], tap[2], tap[3], tap[5]) !=
                    (channel, expected_y, expected_x, expected_address)):
                raise AssertionError("T04 D2 tap order/address differs from the model NCHW map")
            addresses.append(expected_address)
        if vector_class == 1:
            directed_item = next((item for item in manifest["operator_test_plan"]["directed_case_vectors"]["maxpool"][str(layer_index)]
                                  if int(item["case_index"]) == case_index), None)
            if directed_item is None or candidate_values != list(map(int, directed_item["candidate_values_int8"])):
                raise AssertionError("T04 directed candidate vector differs from G0 frozen inputs")

        raw_bytes = [_initial_byte(address) for address in addresses]
        signed_bytes = [value if value < 128 else value - 256 for value in raw_bytes]
        bad_domain = any(value == 0x80 for value in raw_bytes)
        expected_error = 1 if bad_domain else 0
        expected_signed = None if bad_domain else max(signed_bytes)
        expected_byte = None if bad_domain else expected_signed & 0xFF
        output_base = int(layer["tensor_address"])
        output_address = output_base + ((channel * out_h + output_y) * out_w + output_x)
        rows.append("{} {} {} {} {} {} {} {} {} {} {} {} {} {}\n".format(
            vector_class, layer_index, case_index, channel, output_y, output_x,
            *(f"{address:08X}" for address in addresses), *candidate_values))
        stimuli.append({"class": vector_class, "layer": layer_index, "case": case_index,
                        "coordinate_nchw": [0, channel, output_y, output_x],
                        "tap_addresses": addresses,
                        "g0_candidate_values_int8_not_memory_data": candidate_values})
        memory_goldens.append({"class": vector_class, "layer": layer_index,
                               "case": case_index, "tap_addresses": addresses,
                               "t10_initial_bytes_hex": [f"{value:02X}" for value in raw_bytes],
                               "signed_memory_bytes": signed_bytes,
                               "expected_error_code": expected_error,
                               "expected_signed_max": expected_signed,
                               "expected_output_byte_hex": None if expected_byte is None else f"{expected_byte:02X}",
                               "output_address": output_address})
        counts[layer_index]["random" if vector_class == 0 else "directed"] += 1
        counts[layer_index]["raw_0x80_rejected" if bad_domain else "legal_memory_windows"] += 1

    for layer_index in (9, 17, 25):
        if counts[layer_index]["random"] != 1000 or counts[layer_index]["directed"] != 16:
            raise AssertionError(f"official coverage incomplete for layer {layer_index}: {counts[layer_index]}")
    if len(rows) != 3048 or len(directed_candidates) != 48:
        raise AssertionError("official model vector total differs from G0")
    engine_payload = "".join(rows).encode("ascii")
    engine_path = work / "engine_vectors.dat"
    engine_path.write_bytes(engine_payload)
    return {
        "t03_evidence_sha256": _sha(t03_evidence_path),
        "t04_evidence_sha256": _sha(t04_evidence_path),
        "t03_vector_sha256": t03_result["vector_sha256"],
        "t03_candidate_golden_sha256": t03_result["golden_output_sha256"],
        "t04_vector_sha256": t04_result["vector_sha256"],
        "t04_logical_vector_sha256": t04_result["logical_vector_sha256"],
        "t04_coordinate_golden_sha256": t04_result["golden_output_sha256"],
        "engine_vector_sha256": hashlib.sha256(engine_payload).hexdigest(),
        "engine_vector_bytes": len(engine_payload),
        "stimulus_sha256": _canonical_sha(stimuli),
        "memory_golden_sha256": _canonical_sha(memory_goldens),
        "directed_candidate_golden_sha256": _canonical_sha(directed_candidates),
        "directed_candidate_golden_count": len(directed_candidates),
        "counts_by_layer": counts,
        "counts": {"random": 3000, "directed": 48, "queries": 3048,
                   "input_taps": 12192,
                   "legal_memory_windows": sum(v["legal_memory_windows"] for v in counts.values()),
                   "raw_0x80_rejected": sum(v["raw_0x80_rejected"] for v in counts.values())},
        "prng": t04_result["shared_prng"],
        "t03_evidence": t03_evidence,
        "t04_evidence": t04_evidence,
    }


class TestS2AMaxpoolEngineRtl(unittest.TestCase):
    """验证 T14 RTL 的一个模型窗口端到端读取与写回。"""

    def _test_vivado_smoke_reference(self) -> None:
        manifest_raw = _MANIFEST.read_bytes()
        self.assertEqual(hashlib.sha256(manifest_raw).hexdigest(), _MANIFEST_SHA)
        manifest = json.loads(manifest_raw.decode("utf-8"))
        sources = [
            _ROOT / "src/int8_maxpool_geometry.sv",
            _ROOT / "src/int8_maxpool_window.sv",
            _ROOT / "src/s2a_maxpool_engine.sv",
            _ROOT / "src/s2a_memory_master.sv",
            _ROOT / "sim/s2a_memory_model.sv",
            _ROOT / "sim/tb_s2a_maxpool_engine.sv",
        ]
        for path in sources:
            self.assertTrue(path.is_file(), f"缺少源码：{path}")
            raw = path.read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), f"{path.name} 有 BOM")
            self.assertNotIn(b"\r\n", raw, f"{path.name} 必须使用 LF")
            raw.decode("utf-8")
        source_hashes = {str(path.relative_to(_ROOT)).replace("\\", "/"): _sha(path)
                         for path in sources}
        tools = {name: _XILINX_BIN / f"{name}.bat"
                 for name in ("xvlog", "xelab", "xsim")}
        for tool in tools.values():
            self.assertTrue(tool.is_file(), f"找不到 Vivado 工具：{tool}")

        temp_path = Path(tempfile.mkdtemp(prefix="s2a_t14_maxpool_smoke_"))
        ranges_sha = _write_ranges(temp_path, manifest)
        codes: list[dict[str, object]] = []
        simulation_log = ""
        deadline = time.monotonic() + 600.0
        phases = [
            ("xvlog", ["-sv", *(str(path) for path in sources)]),
            ("xelab", ["-top", "tb_s2a_maxpool_engine",
                        "-snapshot", "s2a_t14_maxpool_snapshot"]),
            ("xsim", ["-R", "s2a_t14_maxpool_snapshot"]),
        ]
        for name, arguments in phases:
            code, output = _run(tools[name], arguments, temp_path,
                                temp_path / f"{name}.log", deadline)
            codes.append({"phase": name, "exit_code": code})
            self.assertEqual(code, 0, f"{name} 退出 {code}，日志：{temp_path / (name + '.log')}\n{output[-5000:]}")
            if name == "xsim":
                simulation_log = output
        self.assertIn("PASS S2A-T14 maxpool smoke reads=4 writes=1 value=D3", simulation_log)

        evidence = {
            "schema_version": "gestureforge_s2a_t14_maxpool_simulation_v1",
            "result": "PASS",
            "scope": "首轮 smoke：tiny416 layer9 单窗口的四 tap byte-lane 读取、signed INT8 max 和单 byte 写回",
            "bindings": {
                "manifest_sha256": _MANIFEST_SHA,
                "sources_sha256": source_hashes,
                "memory_ranges_sha256": ranges_sha,
                "baseline_head": _BASELINE_HEAD,
            },
            "counts": {"input_reads": 4, "output_writes": 1, "result_value_hex": "D3"},
            "vivado": {"phases": codes, "log_directory_pattern": "system TEMP/s2a_t14_maxpool_smoke_*"},
            "limitations": ["尚未执行官方随机/定向向量、故障、取消/复位和完整双轮验证。"],
        }
        _EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
        _EVIDENCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8", newline="\n")
        self.assertEqual(_sha(_EVIDENCE), hashlib.sha256(_EVIDENCE.read_bytes()).hexdigest())
        print(f"S2A-T14 smoke phases={[item['exit_code'] for item in codes]} "
              f"evidence_sha256={_sha(_EVIDENCE)} log_dir={temp_path}")


class TestS2AMaxpoolEngineFullRtl(unittest.TestCase):
    """验证三层官方坐标、T10/T12 memory-path 与事务异常语义。"""

    def test_full_official_memory_path(self) -> None:
        manifest_raw = _MANIFEST.read_bytes()
        self.assertEqual(hashlib.sha256(manifest_raw).hexdigest(), _MANIFEST_SHA)
        manifest = json.loads(manifest_raw.decode("utf-8"))
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=_ROOT,
                              capture_output=True, text=True, check=True).stdout.strip()
        ancestor = subprocess.run(["git", "merge-base", "--is-ancestor",
                                   _BASELINE_HEAD, "HEAD"], cwd=_ROOT,
                                  capture_output=True, check=False)
        self.assertEqual(ancestor.returncode, 0,
                         f"T14 baseline {_BASELINE_HEAD} is not in HEAD history {head}")

        relative_sources = [
            "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md",
            "report/evidence/S2A-T01/tiny416_model_manifest.json",
            "report/evidence/S2A-T03/maxpool_window_simulation.json",
            "report/evidence/S2A-T04/maxpool_geometry_simulation.json",
            "report/evidence/S2A-T10/memory_model_simulation.json",
            "report/evidence/S2A-T12/runtime_protocol_simulation.json",
            "src/int8_maxpool_window.sv", "sim/tb_s2a_maxpool_window.sv",
            "verification/test_s2a_maxpool_rtl.py",
            "src/int8_maxpool_geometry.sv", "sim/tb_s2a_maxpool_geometry.sv",
            "verification/test_s2a_maxpool_geometry_rtl.py",
            "src/s2a_memory_master.sv", "sim/s2a_memory_model.sv",
            "src/s2a_maxpool_engine.sv", "sim/tb_s2a_maxpool_engine.sv",
            "verification/test_s2a_maxpool_engine_rtl.py",
        ]
        source_paths = {rel: _ROOT / rel for rel in relative_sources}
        source_hashes: dict[str, str] = {}
        for relative, path in source_paths.items():
            self.assertTrue(path.is_file(), f"missing source/evidence: {path}")
            raw = path.read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), f"UTF-8 BOM: {relative}")
            self.assertNotIn(b"\r\n", raw, f"CRLF source: {relative}")
            raw.decode("utf-8")
            source_hashes[relative] = hashlib.sha256(raw).hexdigest()
        self.assertEqual(source_hashes["report/evidence/S2A-T01/tiny416_model_manifest.json"],
                         _MANIFEST_SHA)

        t10_evidence = json.loads((
            _ROOT / "report/evidence/S2A-T10/memory_model_simulation.json"
        ).read_text(encoding="utf-8"))
        t12_evidence = json.loads((
            _ROOT / "report/evidence/S2A-T12/runtime_protocol_simulation.json"
        ).read_text(encoding="utf-8"))
        g0_sha = source_hashes["docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"]
        self.assertEqual(t10_evidence["bindings"]["g0_spec_sha256"], g0_sha)
        self.assertEqual(t10_evidence["bindings"]["manifest_sha256"], _MANIFEST_SHA)
        self.assertEqual(t10_evidence["bindings"]["model_sha256"],
                         source_hashes["sim/s2a_memory_model.sv"])
        self.assertEqual(t12_evidence["bindings"]["g0_spec_sha256"], g0_sha)
        self.assertEqual(t12_evidence["bindings"]["manifest_sha256"], _MANIFEST_SHA)
        self.assertEqual(t12_evidence["bindings"]["memory_master_sha256"],
                         source_hashes["src/s2a_memory_master.sv"])
        self.assertEqual(t12_evidence["bindings"]["memory_model_sha256"],
                         source_hashes["sim/s2a_memory_model.sv"])

        work = Path(tempfile.mkdtemp(prefix="s2a_t14_maxpool_full_"))
        ranges_sha = _write_ranges(work, manifest)
        self.assertEqual(ranges_sha, t10_evidence["bindings"]["manifest_derived_ranges_sha256"])
        vectors = _materialize_official_vectors(manifest, work, source_hashes)
        self.assertEqual(vectors["prng"]["seed"], 20260922)
        self.assertEqual(vectors["prng"]["state_before_maxpool"], "0x3AFEA916")
        self.assertEqual(vectors["prng"]["state_after_maxpool"], "0xA9D661B5")
        self.assertEqual(vectors["counts"], {
            "random": 3000, "directed": 48, "queries": 3048,
            "input_taps": 12192,
            "legal_memory_windows": vectors["counts"]["legal_memory_windows"],
            "raw_0x80_rejected": vectors["counts"]["raw_0x80_rejected"],
        })

        tools = {name: _XILINX_BIN / f"{name}.bat"
                 for name in ("xvlog", "xelab", "xsim")}
        for tool in tools.values():
            self.assertTrue(tool.is_file(), f"missing Vivado tool: {tool}")
        compile_sources = [
            _ROOT / "src/int8_maxpool_geometry.sv",
            _ROOT / "src/int8_maxpool_window.sv",
            _ROOT / "src/s2a_maxpool_engine.sv",
            _ROOT / "src/s2a_memory_master.sv",
            _ROOT / "sim/s2a_memory_model.sv",
            _ROOT / "sim/tb_s2a_maxpool_engine.sv",
        ]
        phases: list[dict[str, object]] = []
        logs: dict[str, str] = {}
        deadline = time.monotonic() + 600.0
        commands = [
            ("xvlog", ["-sv", *(str(path) for path in compile_sources)]),
            ("xelab_smoke", ["-top", "tb_s2a_maxpool_engine",
                             "-snapshot", "s2a_t14_smoke_snapshot"], "xelab"),
            ("xsim_smoke", ["-R", "s2a_t14_smoke_snapshot"], "xsim"),
            ("xelab_full", ["-top", "tb_s2a_maxpool_engine_full",
                             "-snapshot", "s2a_t14_full_snapshot"], "xelab"),
            ("xsim_full", ["-R", "s2a_t14_full_snapshot"], "xsim"),
        ]
        for entry in commands:
            name, arguments = entry[0], entry[1]
            tool_name = entry[2] if len(entry) == 3 else name
            code, output = _run(tools[tool_name], arguments, work,
                                work / f"{name}.log", deadline)
            phases.append({"phase": name, "exit_code": code})
            logs[name] = output
            self.assertEqual(code, 0,
                             f"{name} exit={code}; log={work / (name + '.log')}\n{output[-5000:]}")
        self.assertIn("PASS S2A-T14 maxpool smoke reads=4 writes=1 value=D3", logs["xsim_smoke"])
        self.assertIn("PASS S2A-T14 maxpool official model coordinates and T10/T12 memory protocol",
                      logs["xsim_full"])
        pattern = (r"RESULT random=(\d+) directed=(\d+) queries=(\d+) legal=(\d+) raw80=(\d+) "
                   r"official_input_reads=(\d+) official_writes=(\d+) official_readbacks=(\d+) "
                   r"invalid=(\d+) raw_fault=(\d+) override=(\d+) write_fault=(\d+) "
                   r"read_abort=(\d+) read_reset=(\d+) write_abort=(\d+) write_reset=(\d+) "
                   r"recovery=(\d+) owner=(\d+) accepted=(\d+) responses=(\d+) "
                   r"handshakes=(\d+) stall_cycles=(\d+)")
        match = re.search(pattern, logs["xsim_full"])
        self.assertIsNotNone(match, "full xsim omitted unique RESULT summary")
        names = ["random", "directed", "queries", "legal", "raw80", "official_input_reads",
                 "official_writes", "official_readbacks", "invalid", "raw_fault", "override",
                 "write_fault", "read_abort", "read_reset", "write_abort", "write_reset",
                 "recovery", "owner", "accepted", "responses", "handshakes", "stall_cycles"]
        summary = dict(zip(names, map(int, match.groups()), strict=True))
        for name, value in {
            "random": 3000, "directed": 48, "queries": 3048,
            "legal": vectors["counts"]["legal_memory_windows"],
            "raw80": vectors["counts"]["raw_0x80_rejected"],
            "official_input_reads": 12192,
            "official_writes": vectors["counts"]["legal_memory_windows"],
            "official_readbacks": vectors["counts"]["legal_memory_windows"],
            "invalid": 7, "raw_fault": 2, "override": 3, "write_fault": 1,
            "read_abort": 1, "read_reset": 1, "write_abort": 1, "write_reset": 1,
            "recovery": 5, "owner": 1,
        }.items():
            self.assertEqual(summary[name], value, f"full xsim {name} count mismatch")
        self.assertEqual(summary["accepted"], summary["responses"] + 4)
        self.assertEqual(summary["responses"], summary["handshakes"])
        self.assertGreater(summary["stall_cycles"], 1000)

        source_hashes_after = {relative: _sha(path) for relative, path in source_paths.items()}
        self.assertEqual(source_hashes_after, source_hashes, "source changed during simulation")
        evidence = {
            "schema_version": "gestureforge_s2a_t14_maxpool_simulation_v1",
            "result": "PASS",
            "scope": "tiny416 maxpool layer9/17/25 单元素四 tap memory datapath；不含整层调度或整网",
            "bindings": {
                "baseline_head_ancestor": _BASELINE_HEAD,
                "g0_spec_sha256": g0_sha,
                "manifest_sha256": _MANIFEST_SHA,
                "source_sha256": source_hashes_after,
                "t03_evidence_sha256": vectors["t03_evidence_sha256"],
                "t03_candidate_vector_sha256": vectors["t03_vector_sha256"],
                "t03_candidate_golden_sha256": vectors["t03_candidate_golden_sha256"],
                "t04_evidence_sha256": vectors["t04_evidence_sha256"],
                "t04_official_vector_sha256": vectors["t04_vector_sha256"],
                "t04_official_logical_vector_sha256": vectors["t04_logical_vector_sha256"],
                "t04_coordinate_golden_sha256": vectors["t04_coordinate_golden_sha256"],
                "t14_engine_vector_sha256": vectors["engine_vector_sha256"],
                "t14_stimulus_sha256": vectors["stimulus_sha256"],
                "t14_memory_golden_sha256": vectors["memory_golden_sha256"],
                "g0_directed_candidate_golden_sha256": vectors["directed_candidate_golden_sha256"],
                "memory_ranges_sha256": ranges_sha,
                "t10_evidence_sha256": _sha(_ROOT / "report/evidence/S2A-T10/memory_model_simulation.json"),
                "t12_evidence_sha256": _sha(_ROOT / "report/evidence/S2A-T12/runtime_protocol_simulation.json"),
            },
            "random_seed_and_stream": vectors["prng"],
            "counts": {"by_layer": vectors["counts_by_layer"],
                       "official_model": vectors["counts"],
                       "protocol_and_error_checks": summary},
            "memory_golden_semantics": {
                "source": "T10 deterministic initial_byte(address), exact byte-lane selected",
                "candidate_golden_is_separate": True,
                "candidate_golden_is_memory_input": False,
                "raw_0x80_policy": "preserve T10 byte; signed INT8 -128 yields T03 BAD_ARGUMENT(1), reads all four taps, performs no output write",
            },
            "vivado": {"tool_directory": str(_XILINX_BIN), "phases": phases,
                       "command_template": "python -B -m unittest verification.test_s2a_maxpool_engine_rtl -v",
                       "log_directory_pattern": "system TEMP/s2a_t14_maxpool_full_*"},
            "limitations": [
                "只完成三个 G0 maxpool 层的单元素 datapath，不含整层调度、整网逐层张量或检测头解码/NMS。",
                "T10 initial_byte 是 synthetic 全字节域；产生 0x80 的窗口按 T03 合同拒绝，未把它解释为合法 G0 activation。",
                "未执行 Vivado 综合、资源估算、时序分析或实物验证。",
            ],
        }
        _EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
        _EVIDENCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8", newline="\n")
        self.assertEqual(_sha(_EVIDENCE), hashlib.sha256(_EVIDENCE.read_bytes()).hexdigest())
        print("S2A-T14 vectors={} legal={} raw80={} vector_sha256={} golden_sha256={} "
              "phases={} evidence_sha256={} log_dir={}".format(
                  summary["queries"], summary["legal"], summary["raw80"],
                  vectors["engine_vector_sha256"], vectors["memory_golden_sha256"],
                  [item["exit_code"] for item in phases], _sha(_EVIDENCE), work))


if __name__ == "__main__":
    unittest.main()
