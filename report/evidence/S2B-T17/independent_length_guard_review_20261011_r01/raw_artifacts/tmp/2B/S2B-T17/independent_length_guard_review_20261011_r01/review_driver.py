#!/usr/bin/env python3
"""独立审查S6整数边界、冻结绑定及完整模块公开逐周期行为。"""
from __future__ import annotations
import collections
import datetime
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import time
import zlib
import psutil

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[3]
WORK = SCRIPT_DIR / "attempt02"
BASE = "5cb092dcce3631f310e67228738a674a6a82ce41"
HEAD = "d5ad0e0ad13cc12e870d72434c2eb43b74e44330"
G1 = ROOT / "report/evidence/S2B-T17/length_guard_20261011_r07"
MANIFEST = G1 / "delivery_manifest_r02.json"
MANIFEST_SHA = "9a672647c2c4dbb7171e27372ff295a326f1cae835545fb4d947add2d22c2746"
U = (1 << 32) - 1
M64 = (1 << 64) - 1
SEED = 0x1160172B
REPORT = {"schema_version": 1, "status": "RUNNING", "reviewed_source_commit": HEAD,
          "source_baseline_commit": BASE, "reviewed_manifest_sha256": MANIFEST_SHA,
          "started_utc8": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
          "runs": [], "findings": []}

def sha(path):
    """核对实际文件类型并绑定原始字节。"""
    p = Path(path)
    if not p.is_file():
        raise ValueError("精确文件不存在：" + str(p))
    return hashlib.sha256(p.read_bytes()).hexdigest()

def dump(name, obj):
    """仅向本次独立临时目录写入UTF-8证据。"""
    p = WORK / name
    if not p.parent.is_dir():
        raise ValueError("证据父目录不存在")
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

def load(name, path):
    """只读载入生成测试夹具所需模块，不执行其主入口。"""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def rom(text, name):
    """仅解析独立冻结包的层元数据。"""
    m = re.search(r"\b" + name + r"\s+\[0:37\]\s*=\s*'\{(.*?)\};", text, re.S)
    return [int(v, 16) for v in re.findall(r"\d+'h([a-fA-F0-9]+)", m[1])]

def oracle(v, mq, base, ops):
    """直接实现原规格的无限精度乘法和原错误顺序，不消费新窄乘积。"""
    lid = v["layer_index"]
    r = v["input_channels"] * v["kernel_height"] * v["kernel_width"]
    nonzero = ("input_channels", "input_height", "input_width", "output_channels", "output_height", "output_width", "kernel_height", "kernel_width", "stride_y", "stride_x")
    bad_arg = (not v["buffer_owner_pl"] or v["activation_mode"] > 1 or v["input_batch_count"] != 1 or v["output_batch_count"] != 1 or v["output_batch"] != 0 or
               any(v[k] == 0 for k in nonzero) or v["groups"] != 1 or v["padding_value_int8"] != 0 or r == 0 or r > 4608 or
               lid >= 38 or (lid < 38 and ops[lid] != 0) or lid != v["weight_layer_index"])
    if bad_arg:
        return 2 if lid >= 38 or lid != v["weight_layer_index"] else 1
    input_size = v["input_channels"] * v["input_height"] * v["input_width"]
    output_size = v["output_channels"] * v["output_height"] * v["output_width"]
    weights = v["output_channels"] * r
    if (input_size > U or input_size != v["input_length_bytes"] or output_size > U or output_size != v["output_length_bytes"] or weights > U or weights != v["quantized_weight_bytes"]):
        return 3
    ph = (min(v["output_height"], 8) - 1) * v["stride_y"] + v["kernel_height"]
    pw = (min(v["output_width"], 8) - 1) * v["stride_x"] + v["kernel_width"]
    if (any(v[a] + v[b] > 1 << 32 for a, b in (("input_base_address", "input_length_bytes"), ("output_base_address", "output_length_bytes"), ("weight_package_base_address", "weight_package_length_bytes"))) or
        v["weight_package_length_bytes"] == 0 or v["quantized_weight_offset"] + v["quantized_weight_bytes"] > v["weight_package_length_bytes"] or
        mq[lid] != v["output_channels"] or base[lid] + v["output_channels"] > 3164 or ph * pw * v["input_channels"] > 51200):
        return 2
    for size, out, k, s, p0, p1 in (("input_height", "output_height", "kernel_height", "stride_y", "pad_top", "pad_bottom"), ("input_width", "output_width", "kernel_width", "stride_x", "pad_left", "pad_right")):
        n = v[size] + v[p0] + v[p1]
        span = (n - v[k]) & M64
        product = v[out] * v[s]
        if n < v[k] or product <= span or product > ((span + v[s]) & M64):
            return 1
    return 0

def mathematics():
    """穷举全部合法R三因子，再检查宽随机、高位和零掩盖反例。"""
    rng = random.Random(SEED)
    edges = (0, 1, 2, 3, 7, 8, 13, 4607, 4608, 4609, 8191, 8192, 8193, 65535, 65536, 65537, 0x7fffffff, 0x80000000, U - 1, U)
    counts = collections.Counter()
    def verify(a, b, c):
        exact = a * b * c
        p = (a & 8191) * (b & 8191)
        q = (p & 8191) * (c & 8191)
        reject = a == 0 or b == 0 or c == 0 or max(a, b, c) > 4608 or p > 4608 or q > 4608
        assert reject == (exact == 0 or exact > 4608), (a, b, c, exact, p, q)
        if not reject:
            assert q == exact
            counts["valid_r"] += 1
        if a and b and c:
            plane = a * b
            product = (plane & U) * c
            assert plane < 1 << 64 and product < 1 << 64
            bad_length = plane > U or product > U
            assert bad_length == (exact > U)
            if not bad_length:
                assert product == exact
            counts["positive_length"] += 1
        else:
            counts["zero_masked"] += 1
        counts["triples"] += 1
    for a in range(1, 4609):
        for b in range(1, 4608 // a + 1):
            for c in range(1, 4608 // (a * b) + 1):
                verify(a, b, c)
    counts["exhaustive_all_valid_r_triples"] = counts["triples"]
    for triple in itertools.product(edges, repeat=3):
        verify(*triple)
    for _ in range(100000):
        verify(*(rng.getrandbits(32) for _ in range(3)))
    for _ in range(50000):
        verify(*(rng.randrange(0, 8194) for _ in range(3)))
    weight_count = 0
    for r in range(1, 4609):
        for oc in sorted(set(edges + (U // r, min(U, U // r + 1)))):
            p = oc * r
            assert p < 1 << 45
            assert (p >> 32 != 0) == (p > U)
            assert (p & U) == p % (1 << 32)
            weight_count += 1
    result = {"status": "PASS", "seed": SEED, **dict(counts), "weight_pairs": weight_count,
              "coverage": "全部正整数C*KH*KW<=4608三因子穷举；U32宽随机100000；0..8193随机50000；20值笛卡尔；每个合法R的OC端点及U32阈值两侧。",
              "proof": ["零因子由第一分支拒绝，层越界/weight层失配在该分支仍覆盖BAD_RANGE。",
                        "正a,b,c且abc<=U32：ab<=U32，故plane高位检查充分；合法plane32*c32精确64。",
                        "R<=4608蕴含三个正因子和CKH均<=4608；factor32门禁及plane26门禁先保证低13位截取等价。",
                        "非法R不进入长度分支，合法R13*OC32精确45；无需提前MQ容量限制。"]}
    dump("independent_math.json", result)
    return result

def native(name, cmd, cwd, expected=0, timeout=300):
    """保留真实原生命令、返回、采样峰和失败日志，不用宿主返回替代。"""
    log = WORK / (name + ".log")
    start = time.monotonic()
    peak = 0
    reason = None
    env = os.environ.copy()
    env.update({k: "1" for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")})
    toolroot = Path("D:/FPGA_S2A_MSYS2_20261001/env")
    env["PATH"] = str(toolroot / "usr/bin") + os.pathsep + str(toolroot / "mingw64/bin") + os.pathsep + env.get("PATH", "")
    env["VERILATOR_ROOT"] = str(toolroot / "mingw64/share/verilator")
    env["PYTHONUTF8"] = "1"
    with log.open("wb") as stream:
        proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=stream, stderr=subprocess.STDOUT)
        while proc.poll() is None:
            try:
                tree = [psutil.Process(proc.pid)] + psutil.Process(proc.pid).children(recursive=True)
                rss = sum(p.memory_info().rss for p in tree if p.is_running())
                peak = max(peak, rss)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            if peak > 1610612736 or time.monotonic() - start > timeout:
                reason = "进程树RSS超1.5GiB或命令超时"
                for p in reversed(tree):
                    if p.is_running():
                        p.kill()
                break
            time.sleep(0.05)
        code = proc.wait()
    item = {"name": name, "command": cmd, "cwd": str(cwd), "native_exit_code": code, "expected_native_exit_code": expected,
            "elapsed_seconds": round(time.monotonic() - start, 3), "peak_tree_rss_bytes": peak, "sampling_period_seconds": 0.05,
            "log": log.relative_to(ROOT).as_posix(), "log_sha256": sha(log), "failure": reason}
    REPORT["runs"].append(item)
    dump(name + "_native.json", item)
    dump("review_progress.json", REPORT)
    if reason or code != expected:
        raise ValueError("原生命令未达到预期：" + name + "=" + str(code))
    return log.read_text(encoding="utf-8", errors="replace")

def bindings():
    """重新核对全G1清单、实际38源和编译快照及原14源。"""
    assert sha(MANIFEST) == MANIFEST_SHA
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checked = []
    for row in manifest["files"]:
        assert sha(ROOT / row["path"]) == row["sha256"], row["path"]
        checked.append({**row, "bytes": (ROOT / row["path"]).stat().st_size})
    freeze = json.loads((G1 / "source_freeze.json").read_text(encoding="utf-8"))
    assert sha(G1 / "source_freeze.json") == "57a0f293e800802b00367ec4b2d8a131310a803825598f773ea19da4ff5be6b4"
    for path, digest in freeze["source_sha256"].items():
        assert sha(ROOT / path) == digest == sha(G1 / "source_snapshot" / path)
    assert len(freeze["source_sha256"]) == 38 and len(freeze["frozen14_sha256"]) == 14
    for path, digest in freeze["frozen14_sha256"].items():
        assert sha(ROOT / path) == digest
        blob = subprocess.check_output(["git", "show", BASE + ":" + path], cwd=ROOT)
        assert hashlib.sha256(blob).hexdigest() == hashlib.sha256((ROOT / path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    for row in json.loads((G1 / "compiled_mapping.json").read_text(encoding="utf-8")):
        assert sha(ROOT / row["path"]) == row["sha256"] == sha(ROOT / row["copy"])
    old = subprocess.check_output(["git", "show", BASE + ":src/s2b_conv_tile_engine.sv"], cwd=ROOT).decode("utf-8")
    cur = (ROOT / "src/s2b_conv_tile_engine.sv").read_text(encoding="utf-8")
    suffix = "    always_ff @(posedge clk) begin"
    assert cur.count("always_ff") == old.count("always_ff") == 2
    assert cur[cur.index(suffix):] == old[old.index(suffix):]
    assert cur.split(");", 1)[0] == old.split(");", 1)[0]
    assert cur.count("reduction_count_wide") == 3 and cur.count("output_elements_wide") == 4
    assert "if (!validation_ok) begin" in cur and "reduction_count_latched <= reduction_count_wide[31:0];" in cur
    profile = json.loads((ROOT / "board/s2b_inference_platform.json").read_text(encoding="utf-8"))
    assert profile["version"] == "s2b-inference-platform/0.1.6" and profile["physical_interface"] == "s2b-physical-candidate/0.1.1"
    assert profile["clock_hz"] == 50000000 and profile["visibility_default"] == 0 and len(profile["rtl_sources"]) == 18
    s5_freeze = json.loads((ROOT / freeze["s5_source_freeze"]["path"]).read_text(encoding="utf-8"))
    nonconv = [p for p in freeze["source_sha256"] if p.startswith("src/") and p != "src/s2b_conv_tile_engine.sv"]
    assert all(freeze["source_sha256"][p] == s5_freeze["source_sha256"][p] for p in nonconv)
    result = {"status": "PASS", "manifest_bindings": len(checked), "source_sha256": freeze["source_sha256"], "frozen14": 14,
              "sequential_suffix_sha256": hashlib.sha256(cur[cur.index(suffix):].encode("utf-8")).hexdigest(), "static_plus_extra": [31, 7],
              "profile": {k: profile[k] for k in ("version", "physical_interface", "clock_hz", "visibility_default")},
              "nonconv_actual_sources_identical_to_s5": nonconv, "binding_details": checked}
    dump("binding_audit.json", result)
    REPORT["source_sha256"] = {p: freeze["source_sha256"][p] for p in freeze["changed_paths"]}
    return freeze

def vectors_and_tb():
    """沿用公开协议测试骨架，原5996黄金逐条独立重算，另附独立刺激。"""
    sys.path.insert(0, str(ROOT / "verification"))
    scaffold = load("reviewed_conv_scaffold", ROOT / "verification/test_s2b_conv_validation_rtl.py")
    package = (ROOT / "src/s2a_network_descriptor_pkg.sv").read_text(encoding="utf-8")
    mq, base, ops = (rom(package, n) for n in ("S2A_T23_MQ_CHANNEL_COUNT", "S2A_T23_MQ_BASE", "S2A_OP"))
    model = json.loads((ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json").read_text(encoding="utf-8"))
    names, original, small, stats = scaffold.vectors(model)
    original_lines = original.splitlines()
    assert len(original_lines) == 5996
    for line in original_lines:
        values = [int(v, 16) for v in line.split()]
        v = dict(zip(names + ["buffer_owner_pl"], values[:-1]))
        assert oracle(v, mq, base, ops) == values[-1], v
    s5 = (ROOT / "report/evidence/S2B-T17/patch_guard_20261011_r02/validation_vectors.txt").read_bytes()
    original_raw = (ROOT / "report/evidence/S2B-T17/length_guard_20261011_r03/validation_vectors.txt").read_bytes()
    assert original_raw.replace(b"\r\n", b"\n") == original.encode("utf-8")
    assert b"".join(original_raw.splitlines(keepends=True)[:3924]) == s5
    extras = []
    categories = collections.Counter()
    rng = random.Random(SEED)
    def add(cat, v):
        v = dict(v)
        v["activation_mode"] &= 3
        exp = oracle(v, mq, base, ops)
        extras.append(" ".join(f"{v[n] & U:x}" for n in names + ["buffer_owner_pl"]) + f" {exp:x}")
        categories[cat] += 1
    seed_case = dict(small)
    seed_case.update(input_channels=1, input_height=1, input_width=1, output_height=1, output_width=1, kernel_height=1, kernel_width=1, stride_y=1, stride_x=1)
    def lengths(v):
        v["input_length_bytes"] = v["input_channels"] * v["input_height"] * v["input_width"] & U
        v["output_length_bytes"] = v["output_channels"] * v["output_height"] * v["output_width"] & U
        v["quantized_weight_bytes"] = v["output_channels"] * v["input_channels"] * v["kernel_height"] * v["kernel_width"] & U
        return v
    for fields in (("input_channels", "kernel_height", "kernel_width"), ("input_channels", "input_height", "input_width"), ("output_channels", "output_height", "output_width")):
        for t in ((0, U, U), (0, 65536, 65536), (1, 65536, 65536), (4608, 1, 1), (4609, 1, 1), (4096, 2, 1), (U, U, U), (65536, 65536, 65536), (8192, 1, 1)):
            for perm in sorted(set(itertools.permutations(t))):
                v = dict(seed_case)
                v.update(zip(fields, perm))
                lengths(v)
                for layer_pair in ((0, 0), (0, 1), (38, 38), (U, U)):
                    v.update(layer_index=layer_pair[0], weight_layer_index=layer_pair[1])
                    add("zero_high_overflow_layer_priority", v)
    for c in range(1, 4609):
        for oc in (U // c, min(U, U // c + 1)):
            v = dict(seed_case)
            v.update(input_channels=c, output_channels=oc, weight_package_length_bytes=U, quantized_weight_offset=0)
            add("every_r_weight_u32_sides", lengths(v))
    for _ in range(6000):
        v = dict(seed_case)
        axis = rng.randrange(3)
        if axis == 0:
            v.update(input_channels=rng.randrange(1, 4609), input_height=rng.getrandbits(32), input_width=rng.getrandbits(32))
        elif axis == 1:
            v.update(output_channels=rng.getrandbits(32), output_height=rng.getrandbits(32), output_width=rng.getrandbits(32))
        else:
            v.update(input_channels=rng.getrandbits(32), kernel_height=rng.getrandbits(32), kernel_width=rng.getrandbits(32))
        lengths(v)
        if rng.randrange(4) == 0:
            v[rng.choice(("input_length_bytes", "output_length_bytes", "quantized_weight_bytes"))] ^= 1
        if rng.randrange(5) == 0:
            v[rng.choice(("input_base_address", "output_base_address", "weight_package_base_address"))] = U
        if rng.randrange(11) == 0:
            v["weight_layer_index"] = 1
        add("independent_mixed_width_random", v)
    for field, length in (("input_base_address", "input_length_bytes"), ("output_base_address", "output_length_bytes"), ("weight_package_base_address", "weight_package_length_bytes")):
        for delta in (-1, 0, 1):
            v = dict(small)
            v[field] = (1 << 32) - v[length] + delta
            add("address_2pow32_legal_boundary", v)
    vector_raw = original_raw + ("\r\n".join(extras) + "\r\n").encode("utf-8")
    (WORK / "validation_vectors.txt").write_bytes(vector_raw)
    (WORK / "tb_s2b_conv_validation.sv").write_text(scaffold.boundary_tb(names, small), encoding="utf-8", newline="\n")
    source = WORK / "source"
    source.mkdir()
    for p in scaffold.RTL:
        shutil.copyfile(ROOT / p, source / Path(p).name)
    result = {"status": "PASS", "original_vectors_recomputed_independently": len(original_lines), "s5_prefix_vectors": 3924, "s4_prefix_vectors": 2871,
              "extra_vectors": len(extras), "total_vectors": len(original_lines) + len(extras), "extra_categories": dict(categories), "seed": SEED,
              "scaffold_scope": "只复用公开端口时钟/握手驱动；每条原有黄金独立重算；新刺激不调用Developer oracle。"}
    dump("independent_vectors.json", result)
    return result

def resource_gate():
    """检查当前真实资源及运行进程，仍保持2GiB准入门槛。"""
    names = {"vivado.exe", "verilator_bin.exe", "cc1plus.exe", "vtb_s2b_conv_layer0.exe", "vtb_s2b_conv_validation.exe"}
    processes = []
    for p in psutil.process_iter(["name", "cmdline"]):
        if p.info["name"] and p.info["name"].lower() in names:
            processes.append({"pid": p.pid, "name": p.info["name"], "command": p.info["cmdline"], "rss": p.memory_info().rss})
    gate = {"available_ram_bytes": psutil.virtual_memory().available, "minimum_ram_bytes": 2147483648,
            "free_disk_bytes": shutil.disk_usage(WORK).free, "running_heavy_processes": processes, "heavy_slot": "root授权本Reviewer独占，单job/thread"}
    dump("resource_preflight.json", gate)
    if gate["available_ram_bytes"] < gate["minimum_ram_bytes"] or processes:
        raise ValueError("资源门禁拒绝，未启动编译")

def layer0_binding():
    """只读验证真实非零layer0及T25独立切片，不重复整层仿真。"""
    validation = json.loads((ROOT / "report/evidence/S2B-T17/length_guard_20261011_r05/validation.json").read_text(encoding="utf-8"))
    assert validation["status"] == "PASS" and validation["actual_coverage"]["bytes"] == 1384448
    assert validation["actual_coverage"]["requests"] == validation["actual_coverage"]["responses"] == 2551955
    assert validation["actual_coverage"]["cycles"] == 27235743
    for run in validation["runs"]:
        assert run["exit_code"] == 0 and sha(ROOT / run["log"]) == run["log_sha256"]
    for row in validation["fixture_bindings"]:
        assert sha(row["path"]) == row["sha256"] and Path(row["path"]).stat().st_size == row["bytes"]
    cpu = validation["independent_cpu_layer0"]
    for row in cpu["bindings"]:
        assert sha(row["path"]) == row["sha256"]
    restored = zlib.decompress(Path(cpu["bindings"][0]["path"]).read_bytes())
    fixture = Path(validation["fixture_bindings"][2]["path"]).read_bytes()
    cpu_file = ROOT / "report/evidence/S2B-T17/length_guard_20261011_r05/cpu_layer0_expected.bin"
    assert restored[:len(fixture)] == fixture == cpu_file.read_bytes()
    assert sha(cpu_file) == "220499b6b8122c3264bef4d581967d51eedccc9e28813df3e0ff8f8716bc2ed8"
    counts = collections.Counter(int.from_bytes(bytes([v]), "big", signed=True) for v in fixture)
    assert counts[0] < len(fixture) and len(counts) > 1
    sim = (ROOT / "report/evidence/S2B-T17/length_guard_20261011_r05/simulation.log").read_text(encoding="utf-8")
    assert sim.count("PASS: T66 candidate blackbox sample0 layer0 full tensor matched T25; bytes=1384448 mismatches=0") == 1
    result = {"status": "PASS_BOUND_NOT_RERUN", "actual_coverage": validation["actual_coverage"], "golden_sha256": sha(cpu_file),
              "golden_nonzero_bytes": len(fixture) - counts[0], "golden_unique_values": len(counts),
              "cpu_result_status": cpu["status"], "t25_restored_bytes": len(restored), "reviewer_scope": "绑定原生完整layer0/G1公开逐周期日志、实际编译快照、独立CPU与T25非零gold；未复跑layer0/109。"}
    dump("layer0_binding_audit.json", result)
    return result

def main():
    """按依赖串行审查；失败和负测试均保持原件。"""
    begin = time.monotonic()
    try:
        freeze = bindings()
        REPORT["math"] = mathematics()
        REPORT["vectors"] = vectors_and_tb()
        REPORT["layer0_binding"] = layer0_binding()
        resource_gate()
        verilator = Path("D:/FPGA_S2A_MSYS2_20261001/env/mingw64/bin/verilator_bin.exe")
        assert verilator.is_file()
        REPORT["tool_versions"] = {"python": sys.version, "verilator": subprocess.check_output([str(verilator), "--version"], text=True).strip()}
        files = ["source/s2a_network_descriptor_pkg.sv", "source/s2a_conv_tile_engine.sv", "source/s2b_conv_tile_engine.sv", "tb_s2b_conv_validation.sv"]
        lint = native("lint", [str(verilator), "--lint-only", "--timing", "--timescale", "1ns/1ps", "-Wall", "-Wno-fatal", "--top-module", "tb_s2b_conv_validation", *files], WORK)
        assert not re.search(r"%Warning-(LATCH|UNOPTFLAT|MULTIDRIVEN)|%Error", lint)
        REPORT["lint"] = {"status": "PASS", "latch": 0, "unoptflat": 0, "multidriven": 0, "scope": "Verilator真实新RTL结构检查；非Vivado综合或STA。", "warnings": dict(collections.Counter(re.findall(r"%Warning-([A-Z0-9_]+)", lint)))}
        command = [str(verilator), "--binary", "--timing", "--timescale", "1ns/1ps", "-Wall", "-Wno-fatal", "-j", "1", "--threads", "1", "--output-split", "10000", "--output-split-cfuncs", "100", "--top-module", "tb_s2b_conv_validation", "--Mdir", "obj_dir", "-MAKEFLAGS", "PYTHON3='\"" + sys.executable + "\"'", "-CFLAGS", "-D_GLIBCXX_USE_CXX11_ABI=0 -O1", *files]
        native("compile", command, WORK, timeout=900)
        exe = WORK / "obj_dir/Vtb_s2b_conv_validation.exe"
        # 先在独立新子目录执行故意错误预期，原5996+新刺激原件不改写。
        negative = WORK / "negative_wrong_expected"
        negative.mkdir()
        first = (WORK / "validation_vectors.txt").read_text(encoding="utf-8").splitlines()[0].split()
        first[-1] = "1"
        (negative / "validation_vectors.txt").write_text(" ".join(first) + "\n", encoding="utf-8", newline="\n")
        rejected = native("negative_wrong_expected", [str(exe)], negative, expected=1)
        assert "独立校验黄金不同" in rejected and "want=1 got=0" in rejected
        output = native("simulation", [str(exe)], WORK)
        match = re.search(r"PASS CONV_VALIDATION vectors=(\d+) cycles=(\d+) abort_mask=([0-9a-f]+) reset_mask=([0-9a-f]+) response_cases=24 raw80=1", output)
        assert match and int(match[1]) == REPORT["vectors"]["total_vectors"] and int(match[3], 16) == int(match[4], 16) == 0xfffff
        REPORT["actual_coverage"] = {"vectors": int(match[1]), "cycles": int(match[2]), "abort_mask": match[3], "reset_mask": match[4], "response_cases": 24, "raw80": 1}
        # 独立只读核验最终清单，保留inputs候选未冻结原生2。
        native("g1_evidence", [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", "evidence", "--manifest", str(MANIFEST)], ROOT)
        native("g1_inputs", [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", "inputs", "--manifest", str(MANIFEST)], ROOT, expected=2)
        native("static_checker", [sys.executable, "-B", "verification/check_s2b_inference_platform.py"], ROOT)
        assert all(sha(ROOT / p) == digest for p, digest in freeze["source_sha256"].items())
        REPORT["status"] = "TECHNICAL_PASS_PENDING_EVIDENCE_CLARIFICATION"
        REPORT["findings"].append({"priority": "P2", "file": "report/evidence/S2B-T17/length_guard_20261011_r07/delivery_manifest_r02.json", "issue": "historical_ram_preflight_r01把代码推导2表述为真实脚本返回2；尚无直接原生capture。", "closing_condition": "另建不可变澄清清单：r01直接原生exit=null、宿主1、由当时源码推导expected2分开表述，保留原件。"})
    except Exception as exc:
        REPORT["status"] = "REVIEW_VALIDATION_FAILED"
        REPORT["error"] = repr(exc)
        raise
    finally:
        REPORT["elapsed_seconds"] = round(time.monotonic() - begin, 3)
        REPORT["runner_peak_self_working_set_bytes"] = getattr(psutil.Process().memory_info(), "peak_wset", None)
        REPORT["limitations"] = ["只读九源；只写本Run；Git未暂存/提交/切分支；ROSS/SDK/串口/板卡调用0。", "新验证是独立数学、结构和公开逐周期；完整layer0仅绑定未复跑；109整网/1000次/STA/G3未执行。", "G1 r01历史真实原生退出尚未捕获；后次r04 native2不覆盖r01。", "峰RSS为0.05秒进程树采样，非全系统峰；宿主线程及工具调用总体未测。"]
        dump("review_result.json", REPORT)
        print(json.dumps({"status": REPORT["status"], "error": REPORT.get("error"), "elapsed_seconds": REPORT["elapsed_seconds"], "runs": len(REPORT["runs"])}, ensure_ascii=False))

if __name__ == "__main__":
    main()
