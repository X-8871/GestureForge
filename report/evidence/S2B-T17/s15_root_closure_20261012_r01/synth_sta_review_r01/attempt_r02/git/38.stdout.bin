#!/usr/bin/env python3
"""用完整整数证明和S6/S7公开口逐周期差分验证ROUTE地址守卫化简。"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
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

import psutil
import test_s2b_backend_coordinates_rtl as backend
import test_s2b_geometry_specialization_rtl as geometry
import test_s2b_route_specialization_rtl as route

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "f53e067ba91abc02ed60cf7f9063884d9ddb79f1"
RUNNER = "verification/test_s2b_route_address_guard_rtl.py"
SEED = 0x5710A7
U32 = (1 << 32) - 1
BASELINE_SHA = {
    "src/s2b_route_query.sv": "b7a36db57f27a6d32ae6616b569fb51a4b81a08e171621d495a7f54af602e89c",
    "src/s2b_route_engine.sv": "c8b774b053179f40bb431290880710b46f51d589c2eeb4608a5914ecb6f60f36",
}


def query_ports():
    """保留signed值端口名，避免通用无符号engine解析器误读signed关键字。"""
    head = (ROOT/"src/s2b_route_query.sv").read_text(encoding="utf-8").split(");", 1)[0]
    declarations = re.findall(r"^\s*(input|output)\s+logic\s*(?:signed\s*)?(\[[^\]]+\])?\s*(\w+)", head, re.M)
    assert len(declarations) == 32 and len({n for d, w, n in declarations}) == 32
    assert sum(d == "output" for d, w, n in declarations) == 8
    return declarations


def query_oracle(v):
    """按独立无限精度整数及S6错误优先返回全部八个公开query输出。"""
    n, g, gid = (v[k] for k in ("source_count", "groups", "group_id"))
    bad = n not in (1, 2) or g not in (1, 2) or gid >= g
    rng = False
    selected = []
    for slot in range(2 if n == 2 else 1):
        p = f"source{slot}_"
        c, h, w, begin, end, mul = (v[p+k] for k in
            ("channels", "height", "width", "channel_start", "channel_end", "multiplier_q31"))
        bad |= c == 0 or h == 0 or w == 0 or begin >= end or end > c or mul == 0 or mul > 2**31
        if slot == 0 and g == 1:
            bad |= begin != 0 or end != c
        if slot == 0 and g == 2:
            bad |= n != 1 or c % 2 != 0 or begin != gid*(c//2) or end != (gid+1)*(c//2)
        if slot == 1:
            bad |= h != v["source0_height"] or w != v["source0_width"] or begin != 0 or end != c or g != 1
        rng |= c*h > U32 or c*h*w > U32
        length, base = v[p+"length_bytes"], v[p+"base_address"]
        rng |= length == 0 or length < c*h*w or base+length > 2**32
        selected.append((end-begin) & U32)
    oc = sum(selected)
    ch, y, x = (v[k] for k in ("output_channel", "output_y", "output_x"))
    bad |= y >= v["source0_height"] or x >= v["source0_width"] or ch >= oc
    rng |= oc > U32
    slot = 0 if ch < selected[0] else 1 if n == 2 else 0
    p = f"source{slot}_"
    # 无选中源时S6默认value为0；该情形已由坐标/参数错误覆盖。
    value = v[p+"value"] if ch < selected[0] or n == 2 else 0
    bad |= value == -128
    if bad or rng:
        return (0, 0, 0, 0, 0, 0, 0, 1 if bad else 2)
    sch = v[p+"channel_start"] + ch - (selected[0] if slot else 0)
    offset = (sch*v["source0_height"]+y)*v["source0_width"]+x
    addr = v[p+"base_address"]+offset
    # 这些断言验证已删守卫被前置检查蕴含，而非用守卫决定oracle错误。
    assert sch < v[p+"channels"]
    assert 0 <= offset < v[p+"channels"]*v[p+"height"]*v[p+"width"] <= v[p+"length_bytes"] <= U32
    assert addr <= U32 and (offset & U32) == offset
    mag = min(127, (abs(value)*v[p+"multiplier_q31"]+2**30)//2**31)
    scaled = (-mag if value < 0 else mag) & 255
    return (oc, v["source0_height"], v["source0_width"], slot, sch, addr, scaled, 0)


def configuration(c=1, h=1, w=1, c1=0, group=1, gid=0, base=0):
    """生成有效任意CHW，第二源仅在c1非零时启用。"""
    n = 2 if c1 else 1
    outc = c+c1 if group == 1 else c//2
    v = dict(source_count=n, groups=group, group_id=gid, output_channel=outc-1,
             output_y=h-1, output_x=w-1, output_base_address=base,
             output_length_bytes=outc*h*w, output_channels=outc, output_height=h, output_width=w)
    for slot, channels in enumerate((c, c1)):
        for key, value in (("base_address", base if slot == 0 else 0), ("length_bytes", channels*h*w),
                           ("channels", channels), ("height", h), ("width", w),
                           ("channel_start", gid*(c//2) if group == 2 and slot == 0 else 0),
                           ("channel_end", (gid+1)*(c//2) if group == 2 and slot == 0 else channels),
                           ("multiplier_q31", 2**31), ("value", 23 if slot == 0 else -31)):
            v[f"source{slot}_{key}"] = value
    return v


def cases():
    """有效域、端点及多重错误显式取样；宽随机不作为有效域覆盖替代。"""
    rows = []; stats = Counter(); rng = random.Random(SEED)
    def add(cat, v):
        expected = query_oracle(v)
        rows.append((v, expected)); stats[cat] += 1
    for c, h, w in itertools.product(range(1, 7), range(1, 5), range(1, 5)):
        for c1, group, gid in ((0, 1, 0), (1, 1, 0), (3, 1, 0), (0, 2, 0), (0, 2, 1)):
            if group == 2 and c % 2: continue
            v = configuration(c, h, w, c1, group, gid)
            for ch, y, x in itertools.product(range(v["output_channels"]), range(h), range(w)):
                add("exhaustive_small_valid", dict(v, output_channel=ch, output_y=y, output_x=x))
    for index in range(10000):
        group = 2 if index % 4 == 0 else 1
        n2 = group == 1 and index % 3 == 0
        if index % 7 == 0:
            h = w = 1; total = U32 if group == 1 else U32-1
        elif index % 7 == 1:
            h, w = rng.choice((1, 2, 3, 13, 257, 65535)), 1
            total = U32 // h
            if group == 2: total &= ~1
        else:
            h, w = rng.randint(1, 65535), rng.randint(1, 257)
            total = rng.randint(2, min(4096, U32//(h*w)))
            if group == 2: total &= ~1
        c1 = rng.randint(1, total-1) if n2 else 0; c = total-c1
        v = configuration(c, h, w, c1, group, index % 2 if group == 2 else 0)
        for slot in range(v["source_count"]):
            p = f"source{slot}_"; shape = v[p+"length_bytes"]
            length = shape + rng.randint(0, min(4096, U32-shape))
            v[p+"length_bytes"] = length
            v[p+"base_address"] = (1 << 32)-length if index % 2 else rng.randint(0, (1 << 32)-length)
            v[p+"multiplier_q31"] = rng.choice((1, 2, 2**30-1, 2**30, 2**31-1, 2**31))
            v[p+"value"] = rng.randint(-127, 127)
        outsize = v["output_length_bytes"]
        v["output_base_address"] = (1 << 32)-outsize if index % 2 else rng.randint(0, (1 << 32)-outsize)
        v["output_channel"] = rng.choice((0, v["output_channels"]-1, rng.randrange(v["output_channels"])))
        v["output_y"] = rng.choice((0, h-1, rng.randrange(h)))
        v["output_x"] = rng.choice((0, w-1, rng.randrange(w)))
        if v["source_count"] == 1:
            for key in list(v):
                if key.startswith("source1_"): v[key] = rng.randint(-128, 127) if key.endswith("value") else rng.getrandbits(32)
        add("wide_valid_with_padding_and_endpoints", v)
        if index < 2000:
            for cat, key, value in (("argument_and_range", "groups", 0),
                                    ("coordinate_and_range", "output_x", w),
                                    ("short_length", "source0_length_bytes", v["source0_channels"]*h*w-1),
                                    ("source_end_overflow", "source0_base_address", U32)):
                mutant = dict(v, **{key: value})
                if "and_range" in cat: mutant["source0_length_bytes"] = 0
                add(cat, mutant)
    manual = [configuration(base=U32), configuration(c=U32), configuration(h=U32), configuration(w=U32),
              configuration(c=2, h=65536, w=32768), configuration(c=65536, h=65536),
              configuration(c=U32, h=U32, w=U32), configuration(c=U32, c1=1)]
    # 手算恶意shape使用公开U32域长度，避免在输入编码时掩盖无效大整数。
    for v in manual:
        for key in list(v):
            if not key.endswith("value"): v[key] &= U32
        add("manual_u32_products_and_end", v)
    assert query_oracle(manual[0]) == (1, 1, 1, 0, 0, U32, 23, 0)
    assert query_oracle(manual[1])[5] == U32-1
    for g in (0, 3, 4, 0x80000000, U32): add("groups_s6_rejection", dict(configuration(), groups=g))
    for raw in range(-128, 128):
        for mul in (0, 1, 2**30, 2**31, 2**31+1, U32):
            add("all_int8_multiplier_boundary", dict(configuration(), source0_value=raw, source0_multiplier_q31=mul))
    qnames = [n for d, w, n in query_ports() if d == "input"]
    for index in range(20000):
        v = configuration()
        for name in qnames: v[name] = rng.randint(-128, 127) if name.endswith("value") else rng.getrandbits(32)
        add("full_u32_invalid_random", v)
    return rows, {"seed": SEED, "vectors": len(rows), "categories": dict(stats),
                  "query_error_histogram": dict(Counter(row[1][-1] for row in rows))}


def math_proof(rows):
    """完整整数蕴含证明，显式记录恶意65位乘积在有效消费域不能回绕。"""
    checked = 0
    for v, q in rows:
        if q[-1]:
            assert q[:7] == (0,)*7
            continue
        c, h, w = q[:3]
        sizes = [v[f"source{s}_channels"]*h*w for s in range(v["source_count"])]
        e = c*h*w
        assert e <= sum(sizes) <= v["source_count"]*U32 < 2**33
        if e <= v["output_length_bytes"] and v["output_base_address"]+v["output_length_bytes"] <= 2**32:
            prefix = v["output_channel"]*h+v["output_y"]
            off = prefix*w+v["output_x"]
            assert 0 <= prefix < c*h <= e <= U32
            assert off < e <= v["output_length_bytes"]
            assert v["output_base_address"]+off <= U32
            checked += 1
    return {"status": "PASS", "integer_samples": len(rows), "engine_valid_guard_samples": checked,
        "query_steps": ["BAD_ARGUMENT=0保证正CHW、合法源/组选区、坐标和倍率；C0/C1选区之和用64位检查。",
            "先用64位精确计算C*H；超过UINT32即BAD_RANGE，否则低32域再乘W，64位精确，无恶意回绕。",
            "前置BAD_RANGE=0给出C*H*W<=length<=UINT32且base+length<=2^32，两个源分别检查。",
            "选区合法及坐标界限给出0<=selected_channel<C、0<=(channel*H+y)<C*H及offset<C*H*W<=length。",
            "base+offset<base+length<=2^32，所以地址<=UINT32，两个32位组合乘法中间值均不超UINT32。",
            "若前置任一错误为真，旧末项守卫仅可能再置BAD_RANGE；错误优先和全零公开输出不改变。source_count=1未消费source1。"],
        "engine_steps": ["query NONE且shape匹配给出E=Cout*H*W<=shape0+shape1<=2*UINT32<2^33，原65位乘法在消费域精确。",
            "首分支通过再给出E<=output_length<=UINT32；第二分支给出base+length<=2^32。",
            "query合法坐标意味着offset<E，前缀和32位运算均精确，base+offset<=UINT32；原第三分支恒假。",
            "query错误或shape不匹配时仍由原第一分支决定错误；输出长度错误优先于输出端点，未改变拒绝域或周期。"],
        "manual": [{"input": {"C": 1, "H": 1, "W": 1, "base": U32, "length": 1}, "end": 2**32, "address": U32, "error": 0},
            {"input": {"C": U32, "H": 1, "W": 1, "base": 0, "length": U32}, "last_offset": U32-1, "error": 0},
            {"input": {"C": 2, "H": 65536, "W": 32768}, "shape": 2**32, "error": 2},
            {"input": {"C": 65536, "H": 65536, "W": 1}, "plane": 2**32, "error": 2},
            {"input": {"C0": U32, "C1": 1, "H": 1, "W": 1}, "output_channels": 2**32, "error": 2}]}


def engine_vectors(model, ports, query_rows):
    """保留S3全部向量并追加S6全域、24响应映射和80原始数据。"""
    data, coverage = route.vectors(model, ports)
    names = coverage["parameter_order"]; extra = []; cats = Counter()
    def add(cat, v, raw=23, error=0, target=0):
        q = query_oracle(dict(v, source0_value=0, source1_value=0)); initial = q[-1]
        if initial == 0:
            e = v["output_channels"]*v["output_height"]*v["output_width"]
            if (q[:3] != (v["output_channels"], v["output_height"], v["output_width"]) or
                0 in (v["output_channels"], v["output_height"], v["output_width"], v["output_length_bytes"]) or e > v["output_length_bytes"]): initial = 3
            elif v["output_base_address"]+v["output_length_bytes"] > 2**32: initial = 2
            else:
                off = (v["output_channel"]*v["output_height"]+v["output_y"])*v["output_width"]+v["output_x"]
                assert e < 2**33 and off < e <= v["output_length_bytes"] and v["output_base_address"]+off <= U32
        slot, addr = q[3], q[5]; outaddr = (v["output_base_address"]+(v["output_channel"]*v["output_height"]+v["output_y"])*v["output_width"]+v["output_x"]) & U32
        value = query_oracle(dict(v, source0_value=raw, source1_value=raw))[6]
        requests = 0 if initial else 1 if raw == -128 or (error and target == 1) else 2
        expected = initial if initial else (error if error in (1, 2, 6) else 6) if error and target in (1, 2) else 1 if raw == -128 else 0
        extras = [raw & 255, error, target, 0, 255, 1, expected, slot, addr, outaddr, value, requests]
        extra.append(" ".join(f"{v[n]:x}" for n in names)+" "+" ".join(f"{x:x}" for x in extras)); cats[cat] += 1
    selected = query_rows[::max(1, len(query_rows)//4000)]
    for v, expected in selected:
        add("s6_public_u32_domain", v, raw=23)
        if expected[-1] == 0:
            add("output_short", dict(v, output_length_bytes=max(0, v["output_length_bytes"]-1)))
            add("output_end_overflow", dict(v, output_base_address=U32))
            add("output_shape_and_end", dict(v, output_channels=U32, output_base_address=U32))
    for slot, target in ((0, 1), (0, 2), (1, 1)):
        v = configuration(c1=1) if slot else configuration()
        for error in range(8): add("response24", v, error=error, target=target)
    for raw in range(-40, 40): add("raw80", configuration(), raw=raw)
    coverage["s3_original_vectors"] = coverage["vectors"]; coverage["vectors"] += len(extra)
    coverage["s7_categories"] = dict(cats)
    return data+"\n".join(extra)+"\n", coverage


def bench(model, ports, qnames):
    """复用原公开口驱动并把旧实例换成S6快照；新增全部八输出oracle读取。"""
    text = route.testbench(model, ports).replace("s2a_route_engine dut_old", "s6_route_engine dut_old").replace("int8_route_query q_qo", "s6_route_query q_qo")
    text = text.replace("qo_error_code!=0||qn_error_code!=1", "qo_error_code!=1||qn_error_code!=1")
    qoutputs = [n for d, w, n in query_ports() if d == "output"]
    declarations = "integer qf,qs; " + " ".join("logic [31:0] expect_"+n+";" for n in qoutputs)
    fmt = " ".join("%h" for _ in qnames+qoutputs)+"\\n"
    run = 'qf=$fopen("query_vectors.dat","r");if(!qf)$fatal(1,"缺query向量");while(!$feof(qf))begin qs=$fscanf(qf,"'+fmt+'",'+",".join(qnames+["expect_"+n for n in qoutputs])+');if(qs=='+str(len(qnames)+len(qoutputs))+')begin query_compare;'
    for n in qoutputs:
        run += f'if($unsigned(qo_{n})!=={32 if n not in ("output_value", "error_code") else 8 if n == "output_value" else 3}\'(expect_{n}))$fatal(1,"独立query oracle {n} case=%0d",query_cases);'
    run += 'end else if(qs!=-1)$fatal(1,"query列数");end $fclose(qf);'
    return text.replace("integer fh,scanned", declarations+"\ninteger fh,scanned").replace("if(abort_mask!=255", run+"\nif(abort_mask!=255")


def structure(checker):
    """直接核对Git原字节，接口、唯一四行时序例外及原14完整性。"""
    records = {}
    branch = "                    end else if ((output_offset_work >= {33'd0, output_length_latched}) ||\n                                 (output_base_latched + output_offset_work[31:0] < output_base_latched)) begin\n                        result_error_latched <= BAD_RANGE;\n                        state <= RESULT;\n"
    for p, expected in BASELINE_SHA.items():
        raw = subprocess.check_output(["git", "show", BASELINE+":"+p], cwd=ROOT)
        assert hashlib.sha256(raw).hexdigest() == expected
        old = raw.decode("utf-8").replace("\r\n", "\n"); new = (ROOT/p).read_text(encoding="utf-8")
        assert old.split(");", 1)[0] == new.split(");", 1)[0]
        if "engine" in p:
            a = old[old.index("    always_ff"):]; b = new[new.index("    always_ff"):]
            assert a.count(branch) == 1 and a.replace(branch, "") == b
            records[p] = {"header_unchanged": True, "always_ff_only_change": "删除原VALIDATE冗余四行分支", "remaining_always_ff_sha256": hashlib.sha256(b.encode()).hexdigest()}
        else: records[p] = {"header_unchanged": True, "always_ff_count": new.count("always_ff")}
    for p, expected in checker.FROZEN_CORE_SHA256.items(): assert backend.sha(ROOT/p) == expected
    return records


def negatives(checker, work, bindings):
    """更新反例声明的自身SHA后，仍须因完整派生关系被拒绝。"""
    records = backend.checker_negatives(checker, work, bindings)
    fixture = work/"checker_fixture"; pp = fixture/"board/s2b_inference_platform.json"
    mutants = [("重加query地址高位守卫", "src/s2b_route_query.sv", "        selected_address = selected_base_address + selected_offset;", "        selected_address = selected_base_address + selected_offset;\n        if (({32'd0, selected_base_address} + {32'd0, selected_offset}) > 64'hFFFF_FFFF) bad_range = 1'b1;"),
               ("query错误缩31位", "src/s2b_route_query.sv", "logic [31:0] selected_offset;", "logic [30:0] selected_offset;"),
               ("engine错误缩31位", "src/s2b_route_engine.sv", "logic [31:0] output_offset_work;", "logic [30:0] output_offset_work;"),
               ("错误优先改变", "src/s2b_route_query.sv", "        if (bad_argument) begin", "        if (bad_argument && !bad_range) begin"),
               ("engine结果门禁改变", "src/s2b_route_engine.sv", "result_valid = (state == RESULT);", "result_valid = (state == RESULT) && !abort;")]
    for label, path, before, after in mutants:
        original = (ROOT/path).read_text(encoding="utf-8"); assert original.count(before) == 1
        target = fixture/path; target.write_text(original.replace(before, after), encoding="utf-8", newline="\n")
        profile = json.loads((ROOT/"board/s2b_inference_platform.json").read_text(encoding="utf-8"))
        for row in profile["source_derivation"]["derived_sources"]:
            if row["path"] == path: row["sha256"] = backend.sha(target)
        pp.write_text(json.dumps(profile, ensure_ascii=False), encoding="utf-8")
        try: checker.check_static(fixture)
        except ValueError as exc:
            assert "派生源存在未授权的额外差异" in str(exc), str(exc)
            records.append({"name": label, "status": "REJECTED", "self_sha_updated": True, "reason": str(exc)})
        else: raise ValueError("反例未拒绝："+label)
        target.write_bytes((ROOT/path).read_bytes()); pp.write_bytes((ROOT/"board/s2b_inference_platform.json").read_bytes())
    return records


def main():
    """先便宜证明、结构和负例，再单job编译及逐周期仿真；失败保留独立Run。"""
    ap = argparse.ArgumentParser(); ap.add_argument("--run-id", required=True)
    ap.add_argument("--toolchain", type=Path, default=Path(r"D:\FPGA_S2A_MSYS2_20261001\env")); args = ap.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.run_id): ap.error("RunId非法")
    work = ROOT/"tmp/2B/S2B-T17"/args.run_id; evidence = ROOT/"report/evidence/S2B-T17"/args.run_id
    for p in (work.parent, evidence.parent):
        if not p.is_dir() or p.is_symlink(): ap.error("精确父目录不可用")
    if work.exists() or evidence.exists(): ap.error("RunId不可覆盖")
    work.mkdir(); evidence.mkdir(); start = time.monotonic()
    report = {"task_id": "S2B-T17-S7", "status": "FAIL", "runs": [], "source_commit": BASELINE,
              "seed": SEED, "sta": "NOT_RUN", "g3": "NOT_RUN", "limits": {"jobs": 1, "threads": 1, "rss_limit_bytes": 1610612736},
              "limitations": ["独立整数蕴含证明覆盖任意U32输入，枚举与有种子向量辅助验证；非穷举2^32全组合。",
                  "所有公开口逐周期比较实际S6及S7；直接引擎无owner口，owner和真实15层由backend集成验证。",
                  "原2A groups>=3差异只属于S3；本轮S6/S7双方均拒绝，未扩展拒绝域。",
                  "未执行STA、bitstream、板卡或新整网G3。"]}
    try:
        checker = backend.load_checker(); bindings = checker.check_static(ROOT)
        for path in (RUNNER, backend.RUNNER, geometry.RUNNER, route.RUNNER): bindings[path] = backend.sha(ROOT/path)
        report["source_sha256_pre"] = dict(bindings); report["structure"] = structure(checker)
        report["checker_negatives"] = negatives(checker, work, checker.check_static(ROOT))
        assert backend.sha(ROOT/backend.MODEL) == backend.MODEL_SHA
        report["model_input"] = {"path": backend.MODEL, "sha256": backend.MODEL_SHA, "snapshot": "复用Git已绑定原件，不复制模型"}
        model = json.loads((ROOT/backend.MODEL).read_text(encoding="utf-8"))
        report["frozen11_route_math"] = route.route_math(model, (ROOT/backend.RTL[0]).read_text(encoding="utf-8"))
        rows, report["query_coverage"] = cases(); report["integer_proof"] = math_proof(rows)
        ports = geometry.ports(ROOT/"src/s2b_route_engine.sv")
        data, report["engine_coverage"] = engine_vectors(model, ports, rows)
        qnames = [n for d, w, n in query_ports() if d == "input"]
        qdata = "\n".join(" ".join(f"{v[n]&U32:x}" for n in qnames)+" "+" ".join(f"{x:x}" for x in expect) for v, expect in rows)+"\n"
        for name, payload in (("route_vectors.dat", data), ("query_vectors.dat", qdata), ("tb_s2b_route_specialization.sv", bench(model, ports, qnames))):
            for directory in (work, evidence): (directory/name).write_text(payload, encoding="utf-8", newline="\n")
        source = work/"source"; source.mkdir(); snapshot = evidence/"source_snapshot"; snapshot.mkdir()
        for p in bindings:
            dest = snapshot/p; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(ROOT/p, dest)
        for path in BASELINE_SHA:
            raw = subprocess.check_output(["git", "show", BASELINE+":"+path], cwd=ROOT)
            (evidence/("s6_"+Path(path).name)).write_bytes(raw)
            renamed = raw.decode("utf-8").replace("s2b_route_engine", "s6_route_engine").replace("s2b_route_query", "s6_route_query")
            (source/("s6_"+Path(path).name)).write_text(renamed, encoding="utf-8", newline="\n")
            shutil.copyfile(ROOT/path, source/Path(path).name)
        report["resource_preflight"] = {"available_ram_bytes": psutil.virtual_memory().available, "disk_free_bytes": shutil.disk_usage(work).free,
            "running_tools": [{"pid": p.pid, "name": p.info["name"]} for p in psutil.process_iter(["name"]) if p.info["name"] and p.info["name"].lower() in ("vivado.exe", "verilator_bin.exe", "cc1plus.exe")], "heavy_slot": "总控授权独占单job；只记录真实进程名，服务名字不算重型"}
        if report["resource_preflight"]["available_ram_bytes"] < 2147483648 or report["resource_preflight"]["disk_free_bytes"] < 1073741824: raise ValueError("资源不足，未编译")
        env = os.environ.copy(); bd = args.toolchain/"mingw64/bin"; md = args.toolchain/"usr/bin"
        env["PATH"] = str(md)+os.pathsep+str(bd)+os.pathsep+env.get("PATH", ""); env["VERILATOR_ROOT"] = str(args.toolchain/"mingw64/share/verilator"); env["PYTHONUTF8"] = "1"
        verilator = bd/"verilator_bin.exe"
        for p in (verilator, bd/"g++.exe", md/"make.exe"): checker.exact_file(p)
        report["tool_versions"] = {"python": sys.version, "verilator": subprocess.check_output([str(verilator), "--version"], env=env, text=True, timeout=30).strip()}
        command = [str(verilator), "--binary", "--timing", "--timescale", "1ns/1ps", "-Wall", "-Wno-fatal", "-j", "1", "--threads", "1", "--output-split", "10000", "--output-split-cfuncs", "100", "--top-module", "tb_s2b_route_specialization", "--Mdir", "obj_dir", "-MAKEFLAGS", "PYTHON3='\""+sys.executable+"\"'", "-CFLAGS", "-D_GLIBCXX_USE_CXX11_ABI=0 -O1", *["source/"+p.name for p in sorted(source.iterdir())], "tb_s2b_route_specialization.sv"]
        backend.execute("compile", command, work, evidence, env, report, 600)
        backend.execute("simulation", [str(work/"obj_dir/Vtb_s2b_route_specialization.exe")], work, evidence, env, report, 600)
        log = (evidence/"simulation.log").read_text(encoding="utf-8")
        matches = re.findall(r"PASS ROUTE_SPECIALIZATION cases=(\d+) queries=(\d+) cycles=(\d+) abort=(\d+) reset=(\d+)", log)
        assert len(matches) == 1
        counts = dict(zip(("cases", "queries", "cycles", "abort", "reset"), map(int, matches[0])))
        assert counts["cases"] == report["engine_coverage"]["vectors"] and counts["queries"] == report["frozen11_route_math"]["outputs"]+50000+len(rows)
        assert counts["abort"] == counts["reset"] == 255
        report["simulation_counts"] = counts
        report["lint_forbidden"] = re.findall(r"%Warning-(?:LATCH|UNOPTFLAT|MULTIDRIVEN).*", (evidence/"compile.log").read_text(encoding="utf-8"))
        assert not report["lint_forbidden"]
        report["source_sha256_post"] = {p: backend.sha(ROOT/p) for p in bindings}
        assert bindings == report["source_sha256_post"]
        report["status"] = "PASS_ROUTE_ADDRESS_GUARD_G1"
    except Exception as exc: report["failure"] = repr(exc)
    report["seconds"] = round(time.monotonic()-start, 3)
    (evidence/"validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: report.get(k) for k in ("status", "seconds", "simulation_counts", "failure")}, ensure_ascii=False), flush=True)
    return 0 if report["status"] == "PASS_ROUTE_ADDRESS_GUARD_G1" else 1


if __name__ == "__main__":
    raise SystemExit(main())
