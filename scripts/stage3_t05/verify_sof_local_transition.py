"""对固定 OOC 网表的两态 PCLK 局部 SOF 锥做穷举转移核验。"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE = "708aafe9a1c6fbd8fbf6606678e81e05fb4284cf"
RTL_HASH = "db4857fe2fc8d86aa831bac619ddfc676d076f0114ba2c07988d944f894adce6"
NET_HASH = "7b8f457c1cd5377367b3032369ba72fc5d00ac465629ecd970d6fb7e479b852a"
NET = "tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/design_1_alinx_ov5640_0_0_synth_1/design_1_alinx_ov5640_0_0_sim_netlist.v"
RTL = "tmp/s3r06/t04_sof_fix_20261020_r01/vendor_src/my_ip/ov5640_ip/src/alinx_ov5640.v"
GOLD = "report/evidence/S3-T05/t05_sof_fix_20261020_r01/patch_verification/expected_patched_alinx_ov5640.v"
RUN = "report/evidence/S3-T05/task11_sof_local_transition_20261025_r01"


def require(ok, message):
    """对未知结构立即报错。"""
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm(text):
    """保留转义标识符身份，移除网表表达式空白。"""
    return re.sub(r"\s+", "", text).lstrip("\\")


def bits(expr):
    """将仅允许的常量、位选和拼接展开成低位优先的信号名。"""
    expr = norm(expr)
    if expr.startswith("{") and expr.endswith("}"):
        return [b for part in reversed(expr[1:-1].split(",")) for b in bits(part)]
    match = re.fullmatch(r"([A-Za-z_][\w$\[\]]*)\[(\d+):(\d+)\]", expr)
    if match:
        name, hi, lo = match.groups()
        require(int(hi) >= int(lo), "不支持升序总线")
        return [f"{name}[{i}]" for i in range(int(lo), int(hi) + 1)]
    require(re.fullmatch(r"1'b[01]|[A-Za-z_][\w$\[\]]*", expr), f"不支持表达式 {expr}")
    return [expr]


def cells(module):
    """提取本任务支持的原语，并拒绝重复引脚、重复实例与残缺语法。"""
    result = {}
    pattern = r"\b(LUT[1-6]|CARRY4|FDRE)\s*(?:#\s*\((.*?)\)\s*)?(\\\S+|[\w$]+)\s*\((.*?)\);"
    for match in re.finditer(pattern, module, re.S):
        kind, params, name, body = match.groups()
        name = norm(name)
        pairs = re.findall(r"\.([\w]+)\s*\(([^()]*)\)", body)
        require(len(pairs) == len(dict(pairs)), f"重复引脚 {name}")
        require(not re.sub(r"\.[\w]+\s*\([^()]*\)|[\s,]", "", body), f"残缺引脚 {name}")
        ports = {p: bits(v) for p, v in pairs}
        expected = ({f"I{i}" for i in range(int(kind[-1]))} | {"O"} if kind.startswith("LUT") else
                    {"C", "CE", "D", "Q", "R"} if kind == "FDRE" else {"CI", "CYINIT", "DI", "S", "CO", "O"})
        require(set(ports) == expected, f"缺失或未知引脚 {name}")
        init = None
        if kind.startswith("LUT"):
            m = re.fullmatch(r"\s*\.INIT\((\d+)'h([0-9A-Fa-f]+)\)\s*", params or "")
            require(m and int(m[1]) == 2 ** int(kind[-1]), f"错误 LUT INIT {name}")
            init = int(m[2], 16)
            require(init < 1 << int(m[1]), f"INIT 溢出 {name}")
        else:
            require(params is None, f"局部原语不支持参数 {name}")
        for p, v in ports.items():
            require(len(v) == (4 if kind == "CARRY4" and p in {"DI", "S", "CO", "O"} else 1), f"引脚宽度错误 {name}.{p}")
        require(name not in result, f"重复实例 {name}")
        result[name] = (kind, init, ports)
    return result


def parse(text):
    """通过真实子模块端口映射展平局部锥；子模块的外部状态仍为边界。"""
    modules = dict(re.findall(r"\bmodule\s+(\w+)\b(.*?)\bendmodule\b", text, re.S))
    topname = next(k for k in modules if k.endswith("_alinx_ov5640"))
    childname = next(k for k in modules if k.endswith("_cmos_8_16bit"))
    top, child = modules[topname], modules[childname]
    instances = re.findall(re.escape(childname) + r"\s+cmos_8_16bit_m0\s*\((.*?)\);", top, re.S)
    require(len(instances) == 1, "子模块实例不唯一")
    pairs = re.findall(r"\.([\w]+|\\\S+)\s*\(([^()]*)\)", instances[0])
    require(len(pairs) == len(dict(pairs)), "子模块重复端口")
    mapping = {}
    for port, expr in pairs:
        port = norm(port)
        width = re.search(r"\b(?:input|output)\s+(?:\[(\d+):(\d+)\])?\s*\\?" + re.escape(port) + r"\s*;", child)
        require(width is not None, f"未知子端口 {port}")
        keys = [port] if width[1] is None else [f"{port}[{i}]" for i in range(int(width[2]), int(width[1]) + 1)]
        vals = bits(expr)
        if len(vals) == 1 and len(keys) > 1:
            decl = re.search(r"\bwire\s+\[(\d+):(\d+)\]\s*" + re.escape(vals[0]) + r"\s*;", top)
            require(decl is not None and int(decl[1]) + 1 == len(keys) and int(decl[2]) == 0, f"层级总线声明错误 {port}")
            vals = [f"{vals[0]}[{i}]" for i in range(len(keys))]
        require(len(keys) == len(vals), f"层级宽度错误 {port}")
        mapping.update(zip(keys, vals))
        if len(keys) == 1:
            mapping[port] = vals[0]
    result = cells(top)
    for name, (kind, init, ports) in cells(child).items():
        result["child/" + name] = (kind, init, {p: [mapping.get(v, "child/" + v) if v not in {"1'b0", "1'b1"} else v for v in vs] for p, vs in ports.items()})
    return result


def cone(allcells):
    """从目标寄存器递归收集组合驱动，遇到未声明边界或未知驱动即失败。"""
    targets = [f"cmos_hblank_low_cnt_reg[{i}]" for i in range(16)] + ["cmos_hblank_d0", "cmos_hblank_d1", "s_axis_tuser"]
    boundary = targets + ["cmos_aresetn", "cmos_hblank", "cmos_href_16bit_d1", "full", "fifo_ready"]
    drivers = {}
    for name, cell in allcells.items():
        kind, _, ports = cell
        for p in (["Q"] if kind == "FDRE" else ["O", "CO"] if kind == "CARRY4" else ["O"]):
            for signal in ports[p]:
                require(signal not in drivers, f"重复驱动 {signal}")
                drivers[signal] = name
    selected, visiting = {}, set()

    def visit(signal):
        if signal in boundary or signal in {"1'b0", "1'b1"}:
            return
        require(signal in drivers, f"无支持的驱动 {signal}")
        name = drivers[signal]
        require(name not in visiting, "组合环")
        if name in selected:
            return
        cell = allcells[name]
        require(cell[0] != "FDRE", f"未声明状态边界 {name}")
        visiting.add(name)
        for p, vs in cell[2].items():
            if p not in {"O", "CO"}:
                for v in vs:
                    visit(v)
        visiting.remove(name)
        selected[name] = cell

    regs = []
    for target in targets:
        require(target in drivers, f"目标缺失 {target}")
        name = drivers[target]
        cell = allcells[name]
        require(cell[0] == "FDRE" and cell[2]["C"] == ["cmos_pclk"], f"目标不是 PCLK FDRE {target}")
        for p in ["CE", "D", "R"]:
            visit(cell[2][p][0])
        regs.append((target, cell))
    visit("wr_en0")
    return boundary, selected, regs


def evaluate(selected, regs, values, mask):
    """以 Python 整数位平面执行 LUT/CARRY4 与同步 FDRE 方程。"""
    values = dict(values, **{"1'b0": 0, "1'b1": mask})
    for kind, init, p in selected.values():
        if kind.startswith("LUT"):
            n = int(kind[-1])
            table = [mask if (init >> i) & 1 else 0 for i in range(1 << n)]
            for i in range(n):
                x = values[p[f"I{i}"][0]]
                table = [(a & (mask ^ x)) | (b & x) for a, b in zip(table[::2], table[1::2])]
            values[p["O"][0]] = table[0]
        else:
            carry = values[p["CI"][0]] | values[p["CYINIT"][0]]
            for i in range(4):
                s, d = values[p["S"][i]], values[p["DI"][i]]
                values[p["O"][i]] = s ^ carry
                carry = (s & carry) | ((mask ^ s) & d)
                values[p["CO"][i]] = carry
    output = {}
    for target, (_, _, p) in regs:
        r, ce, d = (values[p[k][0]] for k in ["R", "CE", "D"])
        output[target] = (mask ^ r) & ((ce & d) | ((mask ^ ce) & values[target]))
    output["wr_en0"] = values["wr_en0"]
    return output


def reference(v, mask, increment):
    """依据 RTL 的条件优先级独立写出转移，不使用网表 LUT 或进位方程。"""
    resetn, h, d0, d1, user, href, full, ready = (v[k] for k in ["cmos_aresetn", "cmos_hblank", "cmos_hblank_d0", "cmos_hblank_d1", "s_axis_tuser", "cmos_href_16bit_d1", "full", "fifo_ready"])
    valid = href & d1 & (mask ^ full)
    threshold = v["cmos_hblank_low_cnt_reg[14]"] | v["cmos_hblank_low_cnt_reg[15]"]
    trigger = h & (mask ^ d0) & threshold
    result = {f"cmos_hblank_low_cnt_reg[{i}]": resetn & (mask ^ h) & increment[i] for i in range(16)}
    result.update(cmos_hblank_d0=resetn & h, cmos_hblank_d1=resetn & d0,
                  s_axis_tuser=resetn & (trigger | ((mask ^ trigger) & user & (mask ^ valid))), wr_en0=valid & ready)
    return result


def plane(index, variables):
    count = 1 << variables
    if index < 3:
        return int.from_bytes(bytes([sum(1 << b for b in range(8) if (b >> index) & 1)]) * (count // 8), "little")
    half = 1 << (index - 3)
    return int.from_bytes((b"\0" * half + b"\xff" * half) * (count // (16 * half)), "little")


def run(text):
    boundary, selected, regs = cone(parse(text))
    n = len(boundary)
    require(n == 24, "边界变量数发生变化")
    total, mask = 1 << n, (1 << (1 << n)) - 1
    v = {name: plane(i, n) for i, name in enumerate(boundary)}
    increment = []
    for bit in range(16):
        table = bytearray(8192)
        for c in range(65536):
            if (min(c + 1, 65535) >> bit) & 1:
                table[c // 8] |= 1 << (c % 8)
        increment.append(int.from_bytes(table * 256, "little"))
    actual, expected = evaluate(selected, regs, v, mask), reference(v, mask, increment)
    mismatches = {k: (actual[k] ^ expected[k]).bit_count() for k in expected}
    require(not any(mismatches.values()), f"转移差异 {mismatches}")
    traces = []
    for start in [0, 16383, 16384, 65534, 65535]:
        state = [start, 0, 0, 0]
        history = []
        for resetn, h, href, full, ready in [(1, 0, 0, 0, 0), (1, 1, 0, 0, 1), (1, 1, 1, 1, 1), (1, 1, 1, 0, 0), (1, 1, 1, 0, 1), (0, 1, 1, 0, 1)]:
            c, d0, d1, user = state
            vv = {f"cmos_hblank_low_cnt_reg[{i}]": (c >> i) & 1 for i in range(16)}
            vv.update(zip(boundary[16:], [d0, d1, user, resetn, h, href, full, ready]))
            out = evaluate(selected, regs, vv, 1)
            ref = reference(vv, 1, [(min(c + 1, 65535) >> i) & 1 for i in range(16)])
            require(out == ref, "边界轨迹不一致")
            nextstate = [sum(out[f"cmos_hblank_low_cnt_reg[{i}]"] << i for i in range(16)), out["cmos_hblank_d0"], out["cmos_hblank_d1"], out["s_axis_tuser"]]
            history.append({"pre": state, "inputs": [resetn, h, href, full, ready], "post": nextstate, "write_enable": out["wr_en0"]})
            state = nextstate
        traces.append({"initial_counter": start, "steps": history})
    return {"variables_lsb_first": boundary, "cases": total, "output_bit_comparisons": total * len(expected), "mismatch_counts": mismatches,
            "parsed_cone": {name: {"type": kind, "init": init, "ports": ports} for name, (kind, init, ports) in selected.items()},
            "registers": {target: p for target, (_, _, p) in regs}, "boundary_traces": traces}


def negatives(text):
    """针对引脚、时钟、宽度和未知驱动验证解析器保护条件。"""
    tests = {
        "missing_lut_pin": text.replace(".I0(cmos_hblank),", "", 1),
        "duplicate_lut_pin": text.replace(".I0(cmos_hblank),", ".I0(cmos_hblank),.I0(cmos_hblank),", 1),
        "unknown_counter_driver": text.replace(".D(\\cmos_hblank_low_cnt_reg[0]_i_3_n_7 )", ".D(unknown_signal)", 1),
        "wrong_fdre_clock": text.replace("FDRE cmos_hblank_d0_reg\n       (.C(cmos_pclk)", "FDRE cmos_hblank_d0_reg\n       (.C(other_clock)", 1),
        "wrong_carry_width": text.replace(".DI({1'b0,1'b0,1'b0,1'b1})", ".DI({1'b0,1'b1})", 1),
    }
    result = {}
    for name, mutant in tests.items():
        require(mutant != text, f"负例未生效 {name}")
        try:
            cone(parse(mutant))
        except ValueError as exc:
            result[name] = str(exc)
        else:
            raise ValueError(f"负例未拒绝 {name}")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    git = lambda *a: subprocess.check_output(["git", "-C", str(root), *a], encoding="utf-8").strip()
    require(git("branch", "--show-current") == "codex/stage3-video", "分支不符")
    require(git("merge-base", "--is-ancestor", BASE, "HEAD") == "", "非基线后代")
    for path, expected in [(NET, NET_HASH), (RTL, RTL_HASH), (GOLD, RTL_HASH)]:
        require(sha(root / path) == expected, f"输入哈希不符 {path}")
    out = args.output_dir or root / RUN
    require(not out.exists() and out.parent.is_dir(), "输出已存在或父目录不存在")
    started = time.perf_counter()
    text = (root / NET).read_text(encoding="utf-8")
    negative = negatives(text)
    result = run(text)
    result.update(verdict="PASS_SOF_LOCAL_TRANSITION", full_task11_sequential_equivalence="NOT_RUN", source_commit=BASE,
                  execution_head=git("rev-parse", "HEAD"), created_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),
                  inputs={p: {"sha256": sha(root / p), "size_bytes": (root / p).stat().st_size} for p in [NET, RTL, GOLD]},
                  negative_parser_cases=negative, elapsed_seconds=round(time.perf_counter() - started, 3), python=sys.version,
                  platform=platform.platform(), peak_memory="NOT_MEASURED", repeat_count=1)
    out.mkdir()
    (out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ["verdict", "cases", "output_bit_comparisons", "elapsed_seconds"]}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, StopIteration, subprocess.SubprocessError) as exc:
        print(f"局部验证失败：{exc}", file=sys.stderr)
        raise SystemExit(2)
