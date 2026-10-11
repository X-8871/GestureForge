#!/usr/bin/env python3
"""S9只读整数准备；仅证明所列整数恒等式，不证明RTL或时序。"""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import random
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[4]
WORK = Path(__file__).resolve().parent
COMMIT = "c9f423cddc74ea45071fdbb6a68e4505316babb1"
SEED = 0x591011
U32 = (1 << 32) - 1
U64 = (1 << 64) - 1
ENGINE = "src/s2b_conv_tile_engine.sv"
FREEZE = "report/evidence/S2B-T17/maxpool_address_guard_20261011_r01/source_freeze.json"
TIMING = "report/evidence/S2B-T17/s8_platform_20261011_r01/timing_worst_synth.rpt"
CONTRACT = "report/evidence/S2A-T22/network_dispatch_contract_validation.json"
MANIFEST = "report/evidence/S2A-T01/tiny416_model_manifest.json"
BINDING = "report/evidence/S2A-T63/descriptor_rom_binding.json"


def sha(path):
    """绑定真实原始字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate(v):
    """精确保留前级32位截断及后级unsigned64模域。"""
    group, lane, h, w, tile_y, point_y, tile_x, point_x, base = v
    c = (group + lane) & U32
    y = (tile_y + point_y) & U32
    x = (tile_x + point_x) & U32
    row = (c * h + y) & U64
    offset = (row * w + x) & U64
    address = (offset + base) & U64
    exact = (c * h + y) * w + x
    plane = h * w
    factored = (c * plane + y * w + x) & U64
    # plane拆为两个32位limb；高limb乘积只保留其低32位。
    channel_low = c * (plane & U32)
    channel_high = (c * (plane >> 32)) & U32
    channel_mod = (channel_low + (channel_high << 32)) & U64
    row_term = y * w
    limb_offset = (channel_mod + row_term + x) & U64
    # 地址高limb也按原64位模域处理，不新增全精度溢出拒绝。
    low_sum = (limb_offset & U32) + base
    high_sum = ((limb_offset >> 32) + (low_sum >> 32)) & U32
    limb_address = (high_sum << 32) | (low_sum & U32)
    assert offset == exact & U64 == factored == limb_offset
    assert address == limb_address
    assert plane < (1 << 64) and channel_low < (1 << 64) and row_term < (1 << 64)
    assert low_sum < (1 << 33)
    return {"channel32": c, "global_y32": y, "global_x32": x,
            "channel_sum33": group + lane, "plane64": plane,
            "exact_unbounded_offset": exact, "old_offset64": offset,
            "old_address64": address, "factored_offset64": factored,
            "limb_address64": limb_address}


def decision(offset, address, elements, lane, lane_count, point, point_count):
    """仅复刻ST_OUTPUT_SCAN分支顺序，不建立任何新状态。"""
    if lane >= lane_count:
        return "ADVANCE"
    if point >= point_count:
        return "NEXT_LANE"
    if address > U32 or offset >= elements:
        return "BAD_RANGE"
    return "REQUEST"


def main():
    """全域随机、边界及模型坐标诊断，记录截断和新守卫的反例。"""
    started = time.monotonic()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert head == COMMIT
    freeze = json.loads((ROOT / FREEZE).read_text(encoding="utf-8"))
    assert sha(ROOT / FREEZE) == "f1a70a6f0b703a1e062c479cbc18177b3800f337e06a9fe25dc7d07363ed8708"
    assert sha(ROOT / ENGINE) == "e8231b045b4b94565cb7b54c1e127878ad1850e88c70298c86af6d74009eebf8"
    paths = set(freeze["frozen14"]) | {ENGINE, FREEZE, TIMING, CONTRACT, MANIFEST, BINDING,
            "src/s2b_network_backend.sv", "verification/s2a_network_descriptor_rom.py"}
    pre = {p: sha(ROOT / p) for p in sorted(paths)}
    for p, expected in freeze["frozen14"].items():
        assert pre[p] == expected
    binding = json.loads((ROOT / BINDING).read_text(encoding="utf-8"))
    binding_relations = []
    for item in binding["source_bindings"]:
        raw = (ROOT / item["path"]).read_bytes()
        lf = raw.replace(b"\r\n", b"\n")
        if hashlib.sha256(raw).hexdigest() == item["sha256"]:
            relation = "RAW_IDENTICAL"
        else:
            assert b"\r" not in lf and raw == lf.replace(b"\n", b"\r\n")
            assert hashlib.sha256(lf).hexdigest() == item["sha256"], item["path"]
            relation = "FROZEN_LF_TO_RAW_CRLF_ONLY"
        binding_relations.append({"path": item["path"], "frozen_sha256": item["sha256"],
                                  "raw_sha256": hashlib.sha256(raw).hexdigest(), "relation": relation})
    contract = json.loads((ROOT / CONTRACT).read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    layers = contract["network_dispatch"]["layers"]
    rng = random.Random(SEED)
    stats = Counter()
    consumption = Counter()
    wrap32 = wrap64 = 0
    examples = {}
    def check(category, v):
        nonlocal wrap32, wrap64
        r = evaluate(v)
        stats[category] += 1
        wrap32 += r["channel_sum33"] > U32
        wrap64 += r["exact_unbounded_offset"] > U64
        # 元素数也含未验证非法域；原比较保留128位域。
        for elements in (0, 1, U32, 1 << 64, (1 << 96) - 1):
            old = decision(r["old_offset64"], r["old_address64"], elements, 0, 8, 0, 64)
            new = decision(r["factored_offset64"], r["limb_address64"], elements, 0, 8, 0, 64)
            assert old == new
            consumption[old] += 1
        # 未消费lane/point不能因地址高位或carry改为错误。
        assert decision(r["old_offset64"], r["old_address64"], 0, 8, 8, 0, 64) == "ADVANCE"
        assert decision(r["old_offset64"], r["old_address64"], 0, 0, 8, 64, 64) == "NEXT_LANE"
        return r
    edge = (0, 1, 2, 7, 8, 13, 65535, 65536, 1 << 31, U32-1, U32)
    for c, h, w in itertools.product(edge, repeat=3):
        for lane, y, x, base in ((0, 0, 0, 0), (7, U32, U32, U32),
                                  (U32, 1, U32, 1), (8, 65536, 65536, U32)):
            check("boundary", (c, lane, h, w, y, 0, x, 0, base))
    for _ in range(200000):
        check("random_u32", tuple(rng.getrandbits(32) for _ in range(9)))
    model_summary = []
    for layer in layers:
        if layer["op"] != "convolutional":
            continue
        index = layer["layer_index"]
        n, channels, h, w = layer["output_tensor"]["shape_nchw"]
        assert [n, channels, h, w] == manifest["layers"][index]["output_shape_nchw"]
        assert n == 1 and channels <= 512 and channels*h*w <= U32
        model_summary.append({"layer_index": index, "nchw": [n, channels, h, w],
                              "plane": h*w, "bytes": channels*h*w})
        for c, y, x in itertools.product((0, channels-1), (0, h-1), (0, w-1)):
            base = U32 - (channels*h*w) + 1
            r = check("model_corner_valid_window_end_u32", (c-c%8, c%8, h, w, y-y%8, y%8, x-x%8, x%8, base))
            assert r["old_address64"] <= U32 and r["old_offset64"] < channels*h*w
        for _ in range(1000):
            c, y, x = rng.randrange(channels), rng.randrange(h), rng.randrange(w)
            check("model_random_coordinate", (c-c%8, c%8, h, w, y-y%8, y%8, x-x%8, x%8, 0))
    cases = {
        "ordinary_manual": (8, 3, 13, 13, 8, 4, 8, 4, 100),
        "channel33_original_wrap": (U32, 1, 1, 1, 0, 0, 0, 0, 0),
        "coordinate33_original_wrap": (0, 0, 1, 1, U32, 1, U32, 1, 0),
        "offset64_original_wrap": (1 << 31, 0, 65536, 131072, 0, 0, 0, 0, 0),
        "address64_original_wrap": (2, 0, 1 << 31, U32, 0, 0, U32, 0, 1),
        "low32_only_alias": (1, 0, 65536, 65536, 0, 0, 0, 0, 0),
        "base33_carry": (0, 0, 1, 2, 0, 0, 1, 0, U32),
    }
    for name, v in cases.items():
        examples[name] = {"input": v, "result": check("manual", v)}
    assert examples["ordinary_manual"]["result"]["old_offset64"] == 2027
    assert examples["channel33_original_wrap"]["result"]["old_offset64"] == 0
    assert examples["offset64_original_wrap"]["result"]["exact_unbounded_offset"] == 1 << 64
    assert examples["offset64_original_wrap"]["result"]["old_offset64"] == 0
    assert examples["address64_original_wrap"]["result"]["old_address64"] == 0
    assert examples["low32_only_alias"]["result"]["old_offset64"] == 1 << 32
    text = (ROOT / TIMING).read_text(encoding="utf-8")
    first = text.split("Slack (VIOLATED)")[1]
    assert "output_group_base_reg[4]" in first and "result_error_latched_reg[0]" in first
    timing = {"slack_ns": -6.749, "data_ns": 26.345, "logic_ns": 18.635,
              "route_ns": 7.710, "levels": 32, "CARRY4": 16, "DSP48E1": 5,
              "mapping": {"state7__1/state7__2": "源码与路径推断为channel*height；未查综合网表引脚，非精确网表映射证明",
                          "state5__0/state5__1/state5__2": "源码与路径推断为(channel*height+y)*width；未查综合网表引脚",
                          "confirmed_net": "output_byte_offset_wide[57]"}}
    post = {p: sha(ROOT / p) for p in sorted(paths)}
    assert pre == post
    result = {"status": "PASS_INTEGER_IDENTITIES_ONLY", "source_commit": head,
              "seed": SEED, "seed_hex": hex(SEED), "source_before": pre, "source_after": post,
              "probe_sha256": sha(Path(__file__)), "source_binding_relations": binding_relations, "samples": dict(stats),
              "decision_samples": dict(consumption), "channel_add_overflow33": wrap32,
              "exact_offset_overflow64": wrap64, "manual_and_counterexamples": examples,
              "model_conv_shapes": model_summary, "actual_timing_first_path": timing,
              "proof": ["C/Y/X各先保留原32位赋值的模2^32结果",
                        "Z/2^64Z中乘法分配律与加法结合律，精确保留原unsigned64回绕",
                        "H*W最大(2^32-1)^2，因此plane64精确；C*plane至96位但仅模64被消费",
                        "plane=Plo+2^32*Phi，C*plane mod64=(C*Plo+2^32*((C*Phi)mod32))mod64",
                        "Y*W精确64；全部求和保留原mod64。地址高limb加carry同样mod32",
                        "本准备不将descriptor固定H/W强加给通用engine端口域"],
              "limitations": ["NOT_RUN_RTL", "NOT_RUN_SYNTHESIS", "NOT_RUN_STA", "NOT_RUN_G2", "NOT_RUN_BOARD"],
              "elapsed_seconds": time.monotonic()-started}
    with (WORK / "result_r02.json").open("x", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps({"status": result["status"], "samples": result["samples"],
                      "elapsed_seconds": result["elapsed_seconds"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
