#!/usr/bin/env python3
"""验证2B几何常量派生来源、平台拒绝行为和新旧引擎逐周期等价。"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
import importlib.util
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

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "3f24c94564d10103aaa00db07356f666b085f687"
MODEL = "report/evidence/S2A-T01/tiny416_model_manifest.json"
MODEL_SHA = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
SEED = 0x2B171011
RUNNER = "verification/test_s2b_geometry_specialization_rtl.py"
PORT_SKIP = {"clk", "hard_reset", "abort", "start_valid", "backend_req_ready",
             "backend_rsp_valid", "backend_rsp_rdata", "backend_rsp_error", "result_ready"}
RTL = ("src/int8_maxpool_geometry.sv", "src/s2b_maxpool_geometry.sv", "src/int8_maxpool_window.sv",
       "src/int8_upsample_query.sv", "src/s2a_maxpool_engine.sv",
       "src/s2a_upsample_engine.sv", "src/s2b_maxpool_engine.sv", "src/s2b_upsample_engine.sv")


def sha(path: Path) -> str:
    """始终绑定文件原始字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_checker():
    """加载只读检查器，不执行其命令行入口。"""
    spec = importlib.util.spec_from_file_location("s1_checker", ROOT / "verification/check_s2b_inference_platform.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ports(path: Path) -> list[tuple[str, str, str]]:
    """仅读取明确的引擎端口声明，输出信号全量参与差分比较。"""
    head = path.read_text(encoding="utf-8").split(");", 1)[0]
    result = re.findall(r"^\s*(input|output)\s+logic\s*(\[[^\]]+\])?\s*(\w+)\s*[,)]?", head, re.M)
    if len(result) < 30:
        raise ValueError(f"端口解析不完整：{path}")
    return result


def vector_data(kind: str, declarations: list, model: dict) -> tuple[str, dict]:
    """按冻结模型空间取样；异常期望来自原公开错误优先，独立地址在TB手算。"""
    rng = random.Random(SEED + (kind == "upsample"))
    names = [name for direction, _width, name in declarations if direction == "input" and name not in PORT_SKIP]
    rows, categories = [], Counter()
    legal_coordinates, covered_channels = {}, {}

    def add(category, values, expected=0, raw=0, error=0, target=0, abort=255, stall=1):
        rows.append(" ".join(f"{int(values[name]) & 0xFFFFFFFF:x}" for name in names) +
                    " " + " ".join(f"{int(v):x}" for v in (expected, raw, error, target, abort, stall)))
        categories[category] += 1

    layer_indices = (9, 17, 25) if kind == "pool" else (33,)
    for index in layer_indices:
        layer = model["layers"][index]
        source = model["layers"][index - 1]
        c, ih, iw = source["output_shape_nchw"][1:]
        oc, oh, ow = layer["output_shape_nchw"][1:]
        values = {"layer_index": index, "input_base_address": source["tensor_address"],
                  "input_length_bytes": source["tensor_length_bytes"], "input_channels": c,
                  "input_height": ih, "input_width": iw, "output_base_address": layer["tensor_address"],
                  "output_length_bytes": layer["tensor_length_bytes"], "output_channels": oc,
                  "output_height": oh, "output_width": ow, "kernel_height": 2, "kernel_width": 2,
                  "stride_y": 2, "stride_x": 2, "darknet_padding_parameter": 1, "stride": 2,
                  "output_channel": 0, "output_y": 0, "output_x": 0}
        points = {(ch, y, x) for ch in (0, oc // 2, oc - 1) for y in range(oh) for x in range(ow)}
        points |= {(ch, y, x) for ch in range(oc) for y in (0, oh // 2, oh - 1) for x in (0, ow // 2, ow - 1)}
        points |= {(rng.randrange(oc), rng.randrange(oh), rng.randrange(ow)) for _ in range(256)}
        legal_coordinates[str(index)] = len(points)
        covered_channels[str(index)] = oc
        for ch, y, x in sorted(points):
            add("legal_spatial_channel_sampling", dict(values, output_channel=ch, output_y=y, output_x=x))
        # 每个参数字段分别破坏；错误优先明确保留参数、长度、地址顺序。
        arguments = ("layer_index", "input_channels", "input_height", "input_width", "output_channels",
                     "output_height", "output_width", "kernel_height", "kernel_width", "stride_y", "stride_x",
                     "darknet_padding_parameter") if kind == "pool" else ("input_channels", "input_height", "input_width", "stride")
        for name in arguments:
            for bad in (0, 1, 3, 0xFFFFFFFF):
                if bad != values[name]:
                    add("parameter_field_rejection", dict(values, **{name: bad}), 1)
        for name in ("input_length_bytes", "output_length_bytes"):
            for bad in (0, values[name] - 1, 0xFFFFFFFF):
                add("length_field_rejection", dict(values, **{name: bad}), 3)
        for name in ("input_base_address", "output_base_address"):
            for bad in (values[name] + 4, 0xFFFFFFFF):
                add("address_field_rejection", dict(values, **{name: bad}), 2)
        add("length_before_address", dict(values, input_length_bytes=0, input_base_address=0xFFFFFFFF), 3)
        add("argument_before_length_address", dict(values, input_height=0, input_length_bytes=0,
            input_base_address=0xFFFFFFFF), 1)
        for name, limit in (("output_channel", oc), ("output_y", oh), ("output_x", ow)):
            for bad in (limit, 0x80000000, 0xFFFFFFFF):
                # 池化geometry坐标先拒绝，后续输出地址溢出仍按原规则优先BAD_RANGE。
                changed = dict(values, **{name: bad})
                offset = ((changed["output_channel"] * oh + changed["output_y"]) * ow + changed["output_x"]) & ((1 << 64) - 1)
                expected = 2 if kind == "pool" and values["output_base_address"] + offset > 0xFFFFFFFF else 1
                add("extreme_coordinate_rejection", changed, expected)
        for code in range(1, 8):
            add("read_response_error", values, code if code in (1, 2, 6) else 6, error=code, target=1)
            add("write_response_error", values, code if code in (1, 2, 6) else 6, error=code,
                target=5 if kind == "pool" else 2)
        add("raw_0x80_policy", values, 1 if kind == "pool" else 0, raw=1)
        for state in range(7 if kind == "pool" else 6):
            add("abort_each_state", values, abort=state)
        add("no_memory_stall", values, stall=0)
    return "\n".join(rows) + "\n", {"vectors": len(rows), "categories": dict(categories),
        "legal_coordinates_per_layer": legal_coordinates, "all_channel_indices_sampled": covered_channels,
        "sampling": "通道0/中间/末尾完整空间；所有通道3×3空间位置；每层256固定种子坐标去重。非完整全通道全空间枚举。",
        "seed": SEED + (kind == "upsample"), "parameter_order": names}


def generate_tb(declarations: dict) -> str:
    """生成两个真实新旧引擎、共享逐笔memory模型和全公开输出比较。"""
    parts = ["module tb_s2b_geometry_specialization;", "logic clk = 0; logic reset = 1;",
             "integer cycles=0; integer pool_cases=0; integer upsample_cases=0;",
             "integer p_abort_coverage=0; integer u_abort_coverage=0;",
             "function automatic logic [7:0] memory_byte(input logic [31:0] address, input integer raw);",
             "logic [7:0] value; begin value = raw != 0 ? 8'h80 : 8'((address ^ (address >> 8) ^ 32'ha5) & 32'hff);",
             "if (raw == 0 && value == 8'h80) value = 8'h81; return value; end endfunction"]
    for kind, prefix in (("pool", "p"), ("upsample", "u")):
        ports_here = declarations[kind]
        for direction, width, name in ports_here:
            if name in ("clk", "hard_reset"):
                continue
            for suffix in (("old", "new") if direction == "output" else ("in",)):
                parts.append(f"logic {width} {prefix}_{name}_{suffix};")
        for variant in ("old", "new"):
            module = f"s2{'a' if variant == 'old' else 'b'}_{'maxpool' if kind == 'pool' else kind}_engine"
            connections = []
            for direction, _width, name in ports_here:
                signal = "clk" if name == "clk" else "reset" if name == "hard_reset" else f"{prefix}_{name}_{variant if direction == 'output' else 'in'}"
                connections.append(f".{name}({signal})")
            parts.append(f"{module} {prefix}_{variant} (" + ",\n".join(connections) + ");")
        params = [name for direction, _width, name in ports_here if direction == "input" and name not in PORT_SKIP]
        assignments = " ".join(f"{prefix}_{name}_in=0;" for direction, _width, name in ports_here if direction == "input" and name not in ("clk", "hard_reset"))
        parts.append(f"task automatic {prefix}_clear; begin {assignments} end endtask")
        # 使用旧引擎状态仅定位abort刺激，等价判据只用全部公开端口。
        parts.append(f"integer {prefix}_pending=0; integer {prefix}_delay=0; integer {prefix}_requests=0; integer {prefix}_raw=0; integer {prefix}_response_error=0; integer {prefix}_error_target=0; integer {prefix}_stall=1; logic [31:0] {prefix}_response_data=0; logic [2:0] {prefix}_pending_error=0;")
        parts.append(f"""
task automatic {prefix}_service;
logic accepting; logic responding; logic [31:0] address;
begin
  {prefix}_backend_req_ready_in = ({prefix}_stall == 0 || (cycles % 5) != 0);
  {prefix}_backend_rsp_valid_in = {prefix}_pending != 0 && {prefix}_delay == 0;
  {prefix}_backend_rsp_rdata_in = {prefix}_response_data;
  {prefix}_backend_rsp_error_in = {prefix}_pending_error;
  #1;
  accepting = {prefix}_backend_req_valid_old && {prefix}_backend_req_ready_in;
  responding = {prefix}_backend_rsp_valid_in;
  address = {prefix}_backend_req_addr_old;
  if ({prefix}_abort_in) begin accepting=0; responding=0; end
  tick;
  if ({prefix}_abort_in) begin {prefix}_pending=0; {prefix}_delay=0; end
  else begin
    if (responding) {prefix}_pending=0;
    else if ({prefix}_pending != 0 && {prefix}_delay > 0) {prefix}_delay={prefix}_delay-1;
    if (accepting) begin
      if ({prefix}_pending != 0) $fatal(1,"重复memory请求");
      {prefix}_requests={prefix}_requests+1;
      {prefix}_pending=1;
      {prefix}_delay={prefix}_stall == 0 ? 0 : cycles % 4;
      {prefix}_pending_error={prefix}_requests == {prefix}_error_target ? 3'({prefix}_response_error) : 3'd0;
      for(integer lane=0;lane<4;lane=lane+1)
        {prefix}_response_data[lane*8+:8]=memory_byte(address+32'(lane),{prefix}_raw);
    end
  end
end endtask
""")
        format_string = " ".join("%h" for _ in range(len(params) + 6)) + "\\n"
        scan_targets = ",".join([f"{prefix}_{name}_in" for name in params] + ["expected_error", f"{prefix}_raw", f"{prefix}_response_error", f"{prefix}_error_target", "abort_state", f"{prefix}_stall"])
        result_state = 6 if kind == "pool" else 5
        if kind == "pool":
            source_formula = f"(({prefix}_output_channel_in * {prefix}_input_height_in + {prefix}_output_y_in*2 + 32'(tap/2))*{prefix}_input_width_in)+{prefix}_output_x_in*2+32'(tap%2)+{prefix}_input_base_address_in"
            functional = f"""
if ({prefix}_result_valid_old && expected_error == 0) begin
  expected_output_address=(({prefix}_output_channel_in*{prefix}_output_height_in+{prefix}_output_y_in)*{prefix}_output_width_in)+{prefix}_output_x_in+{prefix}_output_base_address_in;
  expected_value=-8'sd127;
  for(integer tap=0;tap<4;tap=tap+1) begin
    source_address={source_formula};
    if ({prefix}_result_tap_addresses_old[tap*32+:32] !== source_address) $fatal(1,"池化tap地址错误");
    candidate=$signed(memory_byte(source_address,{prefix}_raw));
    if (candidate>expected_value) expected_value=candidate;
  end
  if ({prefix}_result_output_address_old !== expected_output_address || {prefix}_result_value_old !== expected_value) $fatal(1,"池化独立地址/数值错误");
end
"""
        else:
            functional = f"""
if ({prefix}_result_valid_old && expected_error == 0) begin
  expected_output_address=(({prefix}_output_channel_in*32'd26+{prefix}_output_y_in)*32'd26)+{prefix}_output_x_in+{prefix}_output_base_address_in;
  source_address=(({prefix}_output_channel_in*32'd13+({prefix}_output_y_in>>1))*32'd13)+({prefix}_output_x_in>>1)+{prefix}_input_base_address_in;
  expected_value=$signed(memory_byte(source_address,{prefix}_raw));
  if ({prefix}_result_source_address_old !== source_address || {prefix}_result_output_address_old !== expected_output_address || {prefix}_result_value_old !== expected_value) $fatal(1,"上采样独立地址/数值错误");
end
"""
        candidate_declaration = "logic signed [7:0] candidate;" if kind == "pool" else ""
        parts.append(f"""
task automatic {prefix}_vectors;
integer file_handle; integer scanned; integer expected_error; integer abort_state; integer elapsed; integer injected;
logic [31:0] source_address; logic [31:0] expected_output_address; logic signed [7:0] expected_value; {candidate_declaration}
begin
  file_handle=$fopen("{kind}_vectors.dat","r");
  if(file_handle==0) $fatal(1,"向量文件缺失");
  while(!$feof(file_handle)) begin
    scanned=$fscanf(file_handle,"{format_string}",{scan_targets});
    if(scanned=={len(params)+6}) begin
      {prefix}_pending=0; {prefix}_requests=0; {prefix}_backend_rsp_valid_in=0; {prefix}_backend_rsp_error_in=0;
      {prefix}_start_valid_in=1; {prefix}_result_ready_in=0; {prefix}_abort_in=(abort_state==0); injected=0;
      tick;
      {prefix}_start_valid_in=0;
      if(abort_state==0) begin
        if({prefix}_result_valid_old || {prefix}_backend_req_valid_old || {prefix}_start_ready_old) $fatal(1,"IDLE abort未阻止启动");
        {prefix}_abort_coverage={prefix}_abort_coverage | 1;
        {prefix}_abort_in=0; tick;
      end else begin
        elapsed=0;
        while(!{prefix}_result_valid_old && elapsed<200) begin
          if(abort_state!={result_state} && abort_state==integer'({prefix}_old.state)) begin
            {prefix}_abort_in=1; injected=1;
            {prefix}_abort_coverage={prefix}_abort_coverage | (1<<abort_state);
          end
          {prefix}_service;
          elapsed=elapsed+1;
          if(injected!=0) begin
            if({prefix}_result_valid_old || {prefix}_backend_req_valid_old || !{prefix}_backend_cancel_old) $fatal(1,"活动状态abort未取消");
            {prefix}_abort_in=0; tick;
            break;
          end
        end
        if(injected==0) begin
          if(!{prefix}_result_valid_old) $fatal(1,"结果超时");
          if({prefix}_result_error_code_old !== 3'(expected_error)) $fatal(1,"错误优先/响应错误码不符 case=%0d expected=%0d actual=%0d",{kind}_cases,expected_error,{prefix}_result_error_code_old);
          {functional}
          if(expected_error==0 && {prefix}_requests!={5 if kind == 'pool' else 2}) $fatal(1,"合法请求数不符");
          if(expected_error!=0 && {prefix}_response_error==0 && {prefix}_raw==0 && {prefix}_requests!=0) $fatal(1,"拒绝参数产生请求");
          if(abort_state=={result_state}) begin
            {prefix}_abort_in=1; tick;
            if(!{prefix}_result_valid_old) $fatal(1,"RESULT abort丢失结果");
            {prefix}_abort_coverage={prefix}_abort_coverage | (1<<abort_state);
            {prefix}_abort_in=0;
          end
          repeat(3) {prefix}_service;
          {prefix}_result_ready_in=1; tick;
          {prefix}_result_ready_in=0;
        end
      end
      {prefix}_backend_rsp_valid_in=0; {prefix}_backend_req_ready_in=0; {prefix}_abort_in=0;
      tick;
      if(!{prefix}_start_ready_old) $fatal(1,"未回到IDLE");
      {kind}_cases={kind}_cases+1;
    end else if(scanned!=-1) $fatal(1,"向量字段数量不符");
  end
  $fclose(file_handle);
end endtask
""")
    outputs = {}
    for kind, prefix in (("pool", "p"), ("upsample", "u")):
        names = [name for direction, _width, name in declarations[kind] if direction == "output"]
        outputs[kind] = names
        old = ",".join(f"{prefix}_{name}_old" for name in names)
        new = ",".join(f"{prefix}_{name}_new" for name in names)
        parts.append(f"task automatic {prefix}_compare; begin if({{{old}}} !== {{{new}}}) $fatal(1,\"{kind}公开端口逐周期不等价 cycles=%0d cases=%0d\",cycles,{kind}_cases); end endtask")
    parts.extend(["task automatic tick; begin clk=0; #2; p_compare; u_compare; clk=1; #2; p_compare; u_compare; clk=0; #1; cycles=cycles+1; end endtask",
                  "initial begin p_clear; u_clear; repeat(2) tick; reset=0; tick; p_vectors; u_vectors;",
                  "if(p_abort_coverage!=127 || u_abort_coverage!=63) $fatal(1,\"abort状态覆盖不足\");",
                  '$display("PASS GEOMETRY_SPECIALIZATION pool=%0d upsample=%0d cycles=%0d pool_abort=%0d upsample_abort=%0d",pool_cases,upsample_cases,cycles,p_abort_coverage,u_abort_coverage); $finish; end',
                  "endmodule"])
    return "// 新旧真实引擎逐周期差分；状态仅用于定位abort刺激，所有公开输出均比较。\n" + "\n".join(parts) + "\n"


def execute(name: str, command: list[str], work: Path, evidence: Path, env: dict, report: dict, timeout=300) -> None:
    """单job进程树监测；超过1.5GiB或超时仅终止本次子进程并保留失败日志。"""
    started = time.monotonic()
    log = evidence / (name + ".log")
    peak = 0
    failure = None
    with log.open("x", encoding="utf-8") as stream:
        process = subprocess.Popen(command, cwd=work, env=env, stdout=stream, stderr=subprocess.STDOUT)
        while process.poll() is None:
            try:
                parent = psutil.Process(process.pid)
                members = [parent] + parent.children(recursive=True)
                rss = sum(member.memory_info().rss for member in members if member.is_running())
                peak = max(peak, rss)
            except psutil.Error:
                pass
            if peak > 1610612736 or time.monotonic() - started > timeout:
                failure = "RSS_LIMIT" if peak > 1610612736 else "TIMEOUT"
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                               stdout=stream, stderr=subprocess.STDOUT, timeout=30)
                process.wait(timeout=30)
                break
            time.sleep(0.1)
    record = {"name": name, "command": command, "exit_code": process.returncode,
              "seconds": round(time.monotonic() - started, 3), "peak_tree_rss_bytes": peak,
              "failure": failure, "log": log.relative_to(ROOT).as_posix(), "log_sha256": sha(log)}
    report["runs"].append(record)
    if failure or process.returncode != 0:
        raise ValueError(f"{name}失败：{record}")


def checker_negatives(checker, work: Path, sources: dict) -> list[dict]:
    """隔离副本拒绝自报哈希、额外派生差异和过期profile，原项目保持不动。"""
    fixture = work / "checker_fixture"
    fixture.mkdir()
    for path in sources:
        target = fixture / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / path, target)
    profile_path = fixture / "board/s2b_inference_platform.json"
    original = json.loads(profile_path.read_text(encoding="utf-8"))
    tests = []

    def reject(name, mutate):
        profile = copy.deepcopy(original)
        touched = mutate(profile)
        profile_path.write_text(json.dumps(profile, ensure_ascii=False), encoding="utf-8")
        try:
            checker.check_static(fixture)
        except (ValueError, KeyError, TypeError, OSError) as exc:
            tests.append({"name": name, "result": "REJECTED", "reason": str(exc)})
        else:
            raise ValueError("反例未被拒绝：" + name)
        finally:
            for path in touched if isinstance(touched, list) else []:
                shutil.copyfile(ROOT / path, fixture / path)
            profile_path.write_bytes((ROOT / "board/s2b_inference_platform.json").read_bytes())

    def change_source(profile, path, before, after, update_hash=False):
        target = fixture / path
        raw = target.read_bytes().replace(before.encode(), after.encode())
        target.write_bytes(raw)
        if update_hash:
            for item in profile["source_derivation"]["upstream_sources"] + profile["source_derivation"]["derived_sources"]:
                if item["path"] == path:
                    item["sha256"] = sha(target)
        return [path]

    reject("旧profile版本", lambda p: p.update(version="s2b-inference-platform/0.1.0"))
    reject("闭包重复", lambda p: p["rtl_sources"].__setitem__(1, p["rtl_sources"][0]))
    reject("闭包换序", lambda p: p["rtl_sources"].reverse())
    reject("闭包遗漏", lambda p: p["rtl_sources"].pop())
    reject("闭包额外源", lambda p: p["rtl_sources"].append("src/s2a_maxpool_engine.sv"))
    reject("错误freeze提交", lambda p: p["source_derivation"].update(upstream_freeze_commit="0" * 40))
    reject("错误派生基线", lambda p: p["source_derivation"].update(derivation_baseline_commit="0" * 40))
    reject("错误派生策略", lambda p: p["source_derivation"].update(policy="任意优化"))
    reject("换行政策缺失", lambda p: p["source_derivation"].pop("newline_policy"))
    reject("上游记录遗漏", lambda p: p["source_derivation"]["upstream_sources"].pop())
    reject("上游自报SHA", lambda p: p["source_derivation"]["upstream_sources"][0].update(sha256="0" * 64))
    reject("派生记录遗漏", lambda p: p["source_derivation"]["derived_sources"].pop())
    reject("派生记录换序", lambda p: p["source_derivation"]["derived_sources"].reverse())
    reject("允许替换被篡改", lambda p: p["source_derivation"]["derived_sources"][0]["replacements"].append(["state", "other"]))
    reject("派生哈希错误", lambda p: p["source_derivation"]["derived_sources"][0].update(sha256="0" * 64))
    reject("派生路径越界", lambda p: p["source_derivation"]["derived_sources"][0].update(path="../outside.sv"))
    reject("原冻结源变化及自报SHA", lambda p: change_source(p, "src/s2a_maxpool_engine.sv", "3'd1", "3'd2", True))
    reject("常量化错误及自报SHA", lambda p: change_source(p, "src/s2b_maxpool_engine.sv", ".stride_y(32'd2)", ".stride_y(32'd3)", True))
    reject("额外backend逻辑及自报SHA", lambda p: change_source(p, "src/s2b_network_backend.sv", "decoded_x = 32'd0", "decoded_x = 32'd1", True))
    reject("Tcl闭包变化", lambda p: change_source(p, "vivado/s2b_inference_platform.tcl", "src/s2b_maxpool_engine.sv", "src/s2a_maxpool_engine.sv"))
    reject("Tcl版本变化", lambda p: change_source(p, "vivado/s2b_inference_platform.tcl", "variable version 0.1.10", "variable version 0.1.2"))
    reject("顶层引用旧core", lambda p: change_source(p, "src/s2b_inference_top.sv", "s2b_stage2b_core core (", "s2a_stage2a_core_ooc core ("))
    reject("物理时钟变化", lambda p: p.update(clock_hz=25000000))
    reject("可见性默认启用", lambda p: p.update(visibility_default=1))
    reject("构建脚本遗漏", lambda p: p["build_scripts"].pop())
    # 旧证明即使绑定当前全部源也因profile版本被拒绝。
    proof_path, review_path = fixture / "proof.json", fixture / "review.json"
    proof_path.write_text(json.dumps({"schema_version": 1, "status": "PASS",
        "profile_version": "s2b-inference-platform/0.1.0", "source_sha256": sources}), encoding="utf-8")
    review_path.write_text("{}", encoding="utf-8")
    try:
        checker.check_visibility(fixture, proof_path, review_path, sources, sha(review_path))
    except ValueError as exc:
        if "证明平台版本不符" not in str(exc):
            raise
        tests.append({"name": "旧可见性证明", "result": "REJECTED", "reason": str(exc)})
    else:
        raise ValueError("旧证明未拒绝")
    return tests


def main() -> int:
    """保留每次尝试，G1只说明差分和来源通过，G3明确未运行。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--toolchain", type=Path, default=Path(r"D:\FPGA_S2A_MSYS2_20261001\env"))
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.run_id):
        parser.error("RunId字面格式非法")
    for parent in (ROOT / "tmp/2B/S2B-T17", ROOT / "report/evidence/S2B-T17"):
        if not parent.is_dir() or parent.is_symlink():
            parser.error(f"精确父目录不可用：{parent}")
    work = ROOT / "tmp/2B/S2B-T17/s10_conv_g1_20261011_r01" / args.run_id
    evidence = ROOT / "report/evidence/S2B-T17" / args.run_id
    if work.exists() or evidence.exists():
        parser.error("RunId已存在，禁止覆盖")
    work.mkdir(); evidence.mkdir()
    report = {"schema_version": 1, "task_id": "S2B-T17-S1", "run_id": args.run_id,
        "status": "FAIL", "source_commit": BASELINE, "task_baseline_commit": BASELINE, "runs": [], "g3": "NOT_RUN",
        "limitations": ["仅组合参数连接专化；不证明50MHz闭合、完整整网或实板验收。",
            "差分oracle为冻结旧RTL；另以独立地址与signed最大值/nearest复制手算检查合法结果。",
            "空间采用明确分层采样；未枚举全部通道与空间组合。",
            "Verilator继承的原RTL宽度/未使用诊断保留日志，允许非fatal诊断；无静默waiver。"],
        "resource_budget": {"job": 1, "threads": 1, "rss_limit_bytes": 1610612736}}
    started = time.monotonic()
    try:
        actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        checker = load_checker()
        bindings = checker.check_static(ROOT)
        changes = subprocess.check_output(["git", "diff", "--name-only", BASELINE, actual, "--", *bindings],
                                          cwd=ROOT, text=True).splitlines()
        report["source_commit"] = actual
        report["committed_source_changes_since_task_baseline"] = changes
        if changes:
            raise ValueError("任务源码闭包的提交基线改变")
        if sha(ROOT / MODEL) != MODEL_SHA:
            raise ValueError("模型冻结SHA改变")
        report["source_sha256_pre"] = {**bindings, RUNNER: sha(ROOT / RUNNER)}
        report["frozen14_sha256_pre"] = {path: sha(ROOT / path) for path in checker.FROZEN_CORE_SHA256}
        (evidence / "source_snapshot").mkdir()
        for path in report["source_sha256_pre"]:
            shutil.copyfile(ROOT / path, evidence / "source_snapshot" / Path(path).name)
        report["checker_negatives"] = checker_negatives(checker, work, bindings)
        model = json.loads((ROOT / MODEL).read_text(encoding="utf-8"))
        declarations = {"pool": ports(ROOT / "src/s2a_maxpool_engine.sv"),
                        "upsample": ports(ROOT / "src/s2a_upsample_engine.sv")}
        report["coverage"] = {}
        for kind in declarations:
            payload, counts = vector_data(kind, declarations[kind], model)
            for directory in (work, evidence):
                (directory / (kind + "_vectors.dat")).write_text(payload, encoding="utf-8", newline="\n")
            report["coverage"][kind] = counts
        tb = generate_tb(declarations)
        for directory in (work, evidence):
            (directory / "tb_s2b_geometry_specialization.sv").write_text(tb, encoding="utf-8", newline="\n")
        (work / "source").mkdir()
        for path in RTL:
            shutil.copyfile(ROOT / path, work / "source" / Path(path).name)
        env = os.environ.copy()
        bin_dir, make_dir = args.toolchain / "mingw64/bin", args.toolchain / "usr/bin"
        verilator = bin_dir / "verilator_bin.exe"
        env["PATH"] = str(make_dir) + os.pathsep + str(bin_dir) + os.pathsep + env.get("PATH", "")
        env["VERILATOR_ROOT"] = str(args.toolchain / "mingw64/share/verilator")
        env["PYTHONUTF8"] = "1"
        for tool in (verilator, bin_dir / "g++.exe", make_dir / "make.exe"):
            checker.exact_file(tool)
        available, free = psutil.virtual_memory().available, shutil.disk_usage(work).free
        report["resource_preflight"] = {"available_ram_bytes": available, "disk_free_bytes": free,
            "running_vivado": [{"pid": p.pid, "rss_bytes": p.memory_info().rss}
                for p in psutil.process_iter(["name"]) if p.info["name"] and p.info["name"].lower() == "vivado.exe"],
            "vivado_ownership": "总控确认现有PID23188为idle并close_design；本次独占单job差分编译窗口。"}
        if available < 2147483648 or free < 1073741824:
            raise ValueError("资源不足，未启动编译")
        report["tool_versions"] = {"python": sys.version, "verilator": subprocess.check_output(
            [str(verilator), "--version"], env=env, cwd=work, text=True, timeout=30).strip()}
        command = [str(verilator), "--binary", "--timing", "--timescale", "1ns/1ps", "-Wall", "-Wno-fatal",
            "-j", "1", "--threads", "1", "--output-split", "10000", "--output-split-cfuncs", "100",
            "--top-module", "tb_s2b_geometry_specialization", "--Mdir", "obj_dir",
            "-MAKEFLAGS", "PYTHON3='\"" + sys.executable + "\"'", "-CFLAGS", "-D_GLIBCXX_USE_CXX11_ABI=0 -O0",
            *["source/" + Path(path).name for path in RTL], "tb_s2b_geometry_specialization.sv"]
        execute("compile", command, work, evidence, env, report, 600)
        execute("simulation", [str(work / "obj_dir/Vtb_s2b_geometry_specialization.exe")], work, evidence, env, report, 600)
        matches = re.findall(r"PASS GEOMETRY_SPECIALIZATION pool=(\d+) upsample=(\d+) cycles=(\d+) pool_abort=(\d+) upsample_abort=(\d+)",
            (evidence / "simulation.log").read_text(encoding="utf-8"))
        expected = [report["coverage"]["pool"]["vectors"], report["coverage"]["upsample"]["vectors"]]
        if len(matches) != 1 or list(map(int, matches[0][:2])) != expected or list(map(int, matches[0][3:])) != [127, 63]:
            raise ValueError("实际PASS计数或abort覆盖不完整")
        report["simulation_counts"] = dict(zip(("pool", "upsample", "cycles", "pool_abort", "upsample_abort"), map(int, matches[0])))
        report["source_sha256_post"] = {path: sha(ROOT / path) for path in report["source_sha256_pre"]}
        report["frozen14_sha256_post"] = {path: sha(ROOT / path) for path in checker.FROZEN_CORE_SHA256}
        if report["source_sha256_post"] != report["source_sha256_pre"] or report["frozen14_sha256_post"] != report["frozen14_sha256_pre"]:
            raise ValueError("验证期间源码变化")
        checker.check_static(ROOT)
        report["status"] = "PASS_GEOMETRY_SPECIALIZATION_G1"
    except Exception as exc:
        report["failure"] = repr(exc)
    report["seconds"] = round(time.monotonic() - started, 3)
    report["artifacts"] = [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size}
        for path in evidence.rglob("*") if path.is_file()]
    (evidence / "validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": report["status"], "run_id": args.run_id, "seconds": report["seconds"],
        "counts": report.get("simulation_counts"), "failure": report.get("failure")}, ensure_ascii=False))
    return 0 if report["status"] == "PASS_GEOMETRY_SPECIALIZATION_G1" else 1


if __name__ == "__main__":
    raise SystemExit(main())
