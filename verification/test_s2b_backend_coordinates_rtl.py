#!/usr/bin/env python3
"""核对冻结来源、完整坐标数学空间和真实backend逐周期控制及非conv请求。"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

import psutil

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "6d3fd8567b579a51d4042667d47af7d94f2f5a97"
SOURCE_BASELINE = "71983d70cbfcacbbf90dfa032568f8c68a5c0162"
OLD_BACKEND_SHA = "7c6defe3438aa1b2afcedcfc1714d9993c773373dcdd814450d96a2b38778a27"
MODEL = "report/evidence/S2A-T01/tiny416_model_manifest.json"
MODEL_SHA = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
RUNNER = "verification/test_s2b_backend_coordinates_rtl.py"
RTL = ("src/s2a_network_descriptor_pkg.sv", "src/int8_maxpool_geometry.sv",
       "src/int8_maxpool_window.sv", "src/int8_route_query.sv", "src/int8_upsample_query.sv",
       "src/s2b_maxpool_engine.sv", "src/s2a_route_engine.sv", "src/s2b_upsample_engine.sv",
       "src/s2b_network_backend.sv", "src/s2b_route_query.sv", "src/s2b_route_engine.sv")
OPS = {"convolutional": 0, "maxpool": 1, "route": 2, "upsample": 3, "yolo": 4}


def sha(path: Path) -> str:
    """绑定原始文件字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_checker():
    """加载实际平台检查器，不执行其命令行入口。"""
    spec = importlib.util.spec_from_file_location("coordinate_checker", ROOT / "verification/check_s2b_inference_platform.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def math_proof(model: dict, package: str) -> dict:
    """独立按原含通道取模公式枚举38层全部index；不调用RTL候选carry。"""
    layers = model["layers"]
    if len(layers) != 38:
        raise ValueError("冻结层数变化")
    for key, field in (("S2A_OUTPUT_N", 0), ("S2A_OUTPUT_C", 1), ("S2A_OUTPUT_H", 2),
                       ("S2A_OUTPUT_W", 3), ("S2A_OP", None)):
        match = re.search(r"\b" + key + r"\s+\[0:37\]\s*=\s*'\{(.*?)\};", package, re.S)
        values = [int(x, 16) for x in re.findall(r"\d+'h([0-9A-Fa-f]+)", match[1])] if match else []
        expected = [OPS[row["op"]] if field is None else row["output_shape_nchw"][field] for row in layers]
        if values != expected:
            raise ValueError("ROM与manifest不同：" + key)
    rows = []
    for number, row in enumerate(layers):
        n, c, h, w = row["output_shape_nchw"]
        if n != 1 or not (1 <= c <= 512 and 1 <= h <= 208 and 1 <= w <= 208):
            raise ValueError("坐标寄存器宽度前提失效")
        index = 0
        # 使用独立三重循环，比较原公式并检查索引完整性及通道取模恒等。
        for channel in range(c):
            for y in range(h):
                for x in range(w):
                    decoded = ((index // (h * w)) % c, (index // w) % h, index % w)
                    if decoded != (channel, y, x) or index // (h * w) != channel:
                        raise ValueError(f"数学关系失败layer={number} index={index}")
                    index += 1
        if index != n * c * h * w or index >= 2**32:
            raise ValueError("count或wrap前提失败")
        rows.append({"layer": number, "op": row["op"], "shape": [n, c, h, w],
                     "indices": index, "last_coordinate": [c-1, h-1, w-1], "status": "PASS"})
    return {"status": "PASS", "all_38_layers": rows, "indices": sum(r["indices"] for r in rows),
            "channel_modulo_identity": True, "index_wrap_excluded": True,
            "method": "独立C/Y/X三重枚举对比原含%C整数decode，不调用RTL或候选carry。"}


def literal_array(values: list) -> str:
    """生成冻结测试常量，不从候选内部信号计算黄金地址。"""
    return "'{" + ",".join("64'd"+str(int(x)) for x in values) + "}"


def golden_constants(model: dict) -> str:
    """从冻结manifest建立独立地址、route切片和Q31倍率。"""
    rows = model["layers"]
    arrays = {name: [] for name in ("gc", "gh", "gw", "gbase", "gcount", "gop", "gsrc0", "gsrc1",
              "gsh0", "gsw0", "gsh1", "gsw1", "gstart0", "gstart1", "gchannels0", "gmul0", "gmul1")}
    for row in rows:
        _, c, h, w = row["output_shape_nchw"]
        refs = row.get("input_tensor_indices", [])
        inputs = [rows[index] for index in refs if isinstance(index, int) and index >= 0]
        arrays["gc"].append(c); arrays["gh"].append(h); arrays["gw"].append(w)
        arrays["gbase"].append(row["tensor_address"]); arrays["gcount"].append(c*h*w)
        arrays["gop"].append(OPS[row["op"]])
        for slot in (0, 1):
            source = inputs[slot] if slot < len(inputs) else None
            shape = source["output_shape_nchw"] if source else [0, 0, 0, 0]
            arrays[f"gsrc{slot}"].append(source["tensor_address"] if source else 0)
            arrays[f"gsh{slot}"].append(shape[2]); arrays[f"gsw{slot}"].append(shape[3])
            ranges = row.get("route_source_channel_ranges", [])
            start, end = ranges[slot] if slot < len(ranges) else (0, shape[1])
            arrays[f"gstart{slot}"].append(start)
            if slot == 0:
                arrays["gchannels0"].append(end-start)
            scales = row.get("input_scales", [])
            multiplier = int(math.floor(scales[slot]/row["output_scale"]*2**31+0.5)) if row["op"] == "route" and slot < len(scales) else 2**31
            arrays[f"gmul{slot}"].append(multiplier)
    # 倍率按冻结模型scale重新量化；Golden不读取candidate query。
    return "\n".join(f"localparam longint unsigned {name}[0:37] = {literal_array(values)};" for name, values in arrays.items())


def convolution_stub() -> str:
    """仅为backend控制隔离提供原卷积端口，非conv实际引擎保持真实源码。"""
    source = (ROOT / "src/s2a_conv_tile_engine.sv").read_text(encoding="utf-8")
    header = source[source.index("module s2a_conv_tile_engine ("):source.index(");")+2]
    stub = "// 卷积计算未改；此stub仅隔离backend控制验证，不声明卷积数值回归。\n" + header + """
logic pending;
assign start_ready = !pending;
assign backend_cancel = abort;
assign backend_req_valid = 0;
assign backend_req_write = 0;
assign backend_req_addr = 0;
assign backend_req_wdata = 0;
assign backend_req_rstrb = 0;
assign backend_req_wstrb = 0;
assign busy = pending;
assign result_valid = pending;
assign result_error_code = 0;
always_ff @(posedge clk) begin
  if(hard_reset || abort) pending<=0;
  else if(result_valid && result_ready) pending<=0;
  else if(start_valid && start_ready) pending<=1;
end
endmodule
"""

    return stub + stub.replace("module s2a_conv_tile_engine (", "module s2b_conv_tile_engine (")


def generate_tb(model: dict) -> str:
    """真实新旧backend与三个nonconv引擎；每个请求独立核对且全输出逐周期比较。"""
    parts = ["// 基线backend为Git原始S2源码，除模块名外未改；候选为实际S3源。",
             "module tb_s2b_backend_coordinates;", golden_constants(model),
             "logic clk=0, hard_reset=1, abort=0, backend_start=0, buffer_owner_pl=1;",
             "logic [31:0] input_base_address=0, input_length_bytes=519168;",
             "logic [31:0] weight_package_base_address=0, weight_package_length_bytes=5903100;",
             "logic mem_ready=1; logic [31:0] mem_rdata=0; logic [2:0] mem_error_code=0;",
             "longint unsigned cycles=0, boundary_cases=0, trace_requests=0, trace_outputs=0, trace_digest, owner_drop_results=0;",
             "integer active_layer=0, gold_step=0, trace_layers=0; longint unsigned gold_index=0;",
             "longint unsigned public_route_mask=0; integer public_start_trials=0; logic public_tracking=0;",
             "logic trace_enabled=0; logic inj_result=0, inj_ready=1, inj_fault=0, inj_alias=1; logic [2:0] inj_error=0;"]
    declarations = re.findall(r"^\s*(input|output)\s+logic\s*(\[[^\]]+\])?\s*(\w+)\s*[,)]?",
        (ROOT / "src/s2b_network_backend.sv").read_text(encoding="utf-8").split(");", 1)[0], re.M)
    outputs = [name for direction, _width, name in declarations if direction == "output"]
    for direction, width, name in declarations:
        if direction == "output":
            parts.append(f"logic {width} old_{name}, new_{name};")
    for variant, module in (("old", "s2b_network_backend_original"), ("new", "s2b_network_backend")):
        connections = [f".{name}({variant+'_'+name if direction=='output' else name})" for direction, _width, name in declarations]
        parts.append(f"{module} {variant} (" + ",".join(connections) + ");")
    comparisons = "\n".join(f'if(old_{name} !== new_{name}) $fatal(1,"公开端口差异 {name} cycle=%0d layer=%0d index=%0d old=%h new=%h",cycles,old.layer_cursor,old.output_element_index,old_{name},new_{name});' for name in outputs)
    parts.append("""
task automatic compare;
begin
COMPARISONS
  if(old.state !== new.state || old.layer_cursor !== new.layer_cursor || old.output_element_index !== new.output_element_index)
    $fatal(1,"状态或指针逐周期不同 cycle=%0d",cycles);
  if(old.route_start_valid && !(old.u_route_engine.groups == 1 || old.u_route_engine.groups == 2))
    $fatal(1,"原冻结ROM产生非法ROUTE组数");
  if(dut_new.route_start_valid && !(dut_new.u_route_engine.groups == 1 || dut_new.u_route_engine.groups == 2))
    $fatal(1,"派生backend产生非法ROUTE组数");
  if(old.layer_cursor<38 && old.decoded_channel !== new.decoded_channel)
    $fatal(1,"通道不等价 cycle=%0d layer=%0d index=%0d old=%0d new=%0d",cycles,old.layer_cursor,old.output_element_index,old.decoded_channel,new.decoded_channel);
  if(old.layer_cursor<38 && (old.decoded_y !== new.decoded_y || old.decoded_x !== new.decoded_x))
    $fatal(1,"空间坐标不等价 cycle=%0d layer=%0d index=%0d",cycles,old.layer_cursor,old.output_element_index);
end endtask
function automatic logic [7:0] memory_byte(input logic [31:0] address);
logic [7:0] value;
begin value=8'(address ^ (address>>8) ^ 32'ha5); if(value==8'h80) value=8'h81; return value; end
endfunction
function automatic logic [31:0] memory_word(input logic [31:0] address);
begin return {memory_byte(address+3),memory_byte(address+2),memory_byte(address+1),memory_byte(address)}; end
endfunction
task automatic golden_request;
longint unsigned c,y,x,source_address,output_address,channel,slot,selected_multiplier,magnitude,product;
integer value,result_value; longint unsigned tap;
logic writing; logic [31:0] address,wdata; logic [3:0] lane;
begin
  if(gold_index>=gcount[active_layer]) $fatal(1,"完成后额外请求");
  c=gold_index/(gh[active_layer]*gw[active_layer]); y=(gold_index/gw[active_layer])%gh[active_layer]; x=gold_index%gw[active_layer];
  output_address=gbase[active_layer]+gold_index; source_address=0; slot=0; channel=c;
  if(gop[active_layer]==1) begin
    tap=gold_step<4 ? 64'(gold_step) : 64'd0;
    source_address=gsrc0[active_layer]+(c*gsh0[active_layer]+2*y+tap/2)*gsw0[active_layer]+2*x+tap%2;
    result_value=-127;
    for(integer t=0;t<4;t++) begin
      value=integer'($signed(memory_byte(32'(gsrc0[active_layer]+(c*gsh0[active_layer]+2*y+64'(t)/2)*gsw0[active_layer]+2*x+64'(t)%2))));
      if(value>result_value) result_value=value;
    end
    writing=gold_step==4;
  end else if(gop[active_layer]==2) begin
    if(c>=gchannels0[active_layer]) begin slot=1; channel=c-gchannels0[active_layer]; end
    if(slot==0) begin
      source_address=gsrc0[active_layer]+((channel+gstart0[active_layer])*gsh0[active_layer]+y)*gsw0[active_layer]+x;
      selected_multiplier=gmul0[active_layer];
    end else begin
      source_address=gsrc1[active_layer]+((channel+gstart1[active_layer])*gsh1[active_layer]+y)*gsw1[active_layer]+x;
      selected_multiplier=gmul1[active_layer];
    end
    value=integer'($signed(memory_byte(32'(source_address)))); magnitude=64'(integer'(value<0 ? -value : value));
    product=magnitude*selected_multiplier; result_value=integer'((product+64'd1073741824)/64'd2147483648);
    if(value<0) result_value=-result_value;
    if(result_value>127) result_value=127; if(result_value< -127) result_value=-127;
    writing=gold_step==1;
  end else begin
    source_address=gsrc0[active_layer]+(c*gsh0[active_layer]+y/2)*gsw0[active_layer]+x/2;
    result_value=integer'($signed(memory_byte(32'(source_address)))); writing=gold_step==1;
  end
  address=32'(writing ? output_address : source_address) & 32'hfffffffc;
  lane=4'b0001 << (writing ? output_address[1:0] : source_address[1:0]);
  wdata=writing ? ({24'd0,8'(result_value)} << (8*output_address[1:0])) : 0;
  if(old_mem_write !== writing || old_mem_addr !== address || old_mem_wdata !== wdata ||
     old_mem_rstrb !== (writing ? 4'd0 : lane) || old_mem_wstrb !== (writing ? lane : 4'd0))
    $fatal(1,"独立请求golden失败 layer=%0d output=%0d step=%0d addr=%h/%h data=%h/%h",active_layer,gold_index,gold_step,old_mem_addr,address,old_mem_wdata,wdata);
  trace_digest=(trace_digest ^ {old_mem_addr,old_mem_wdata})*64'h100000001b3;
  trace_digest=(trace_digest ^ {55'd0,old_mem_write,old_mem_rstrb,old_mem_wstrb})*64'h100000001b3;
  trace_requests++;
  if(writing) begin gold_index++; gold_step=0; trace_outputs++; end else gold_step++;
end endtask
task automatic tick;
begin
  #1; compare;
  if(public_tracking && old.route_start_valid) public_route_mask |= 64'd1 << old.layer_cursor;
  if(trace_enabled && !buffer_owner_pl && old.selected_result_valid && old.selected_result_error==0) owner_drop_results++;
  if(trace_enabled && old_mem_valid && mem_ready) golden_request;
  clk=1; #1; cycles++; compare; clk=0; #1;
end endtask
task automatic reset_all;
begin
  trace_enabled=0; abort=0; backend_start=0; buffer_owner_pl=1; mem_ready=1; mem_error_code=0;
  input_base_address=0; input_length_bytes=519168; weight_package_base_address=0; weight_package_length_bytes=5903100;
  hard_reset=1; tick; hard_reset=0; #1;
end endtask
task automatic seed(input integer layer,input longint unsigned index,input logic [2:0] state_number);
begin
  old.layer_cursor=6'(layer); new.layer_cursor=6'(layer); old.output_element_index=32'(index); new.output_element_index=32'(index);
  old.state=type(old.state)'(state_number); new.state=type(new.state)'(state_number);
  if(layer<38) begin
    old.output_channel_cursor=9'((index/(gh[layer]*gw[layer]))%gc[layer]);
    old.output_y_cursor=8'((index/gw[layer])%gh[layer]); old.output_x_cursor=8'(index%gw[layer]);
    new.output_channel_cursor=9'((index/(gh[layer]*gw[layer]))%gc[layer]);
    new.output_y_cursor=8'((index/gw[layer])%gh[layer]); new.output_x_cursor=8'(index%gw[layer]);
  end else begin old.output_channel_cursor=0; old.output_y_cursor=0; old.output_x_cursor=0;
    new.output_channel_cursor=0; new.output_y_cursor=0; new.output_x_cursor=0; end
  #1; compare;
end endtask
task automatic boundary;
integer indices[0:7];
begin
  force old.selected_result_valid=inj_result; force new.selected_result_valid=inj_result;
  force old.selected_result_error=inj_error; force new.selected_result_error=inj_error;
  force old.selected_start_ready=inj_ready; force new.selected_start_ready=inj_ready;
  force old.descriptor_fault=inj_fault; force new.descriptor_fault=inj_fault;
  force old.alias_valid=inj_alias; force new.alias_valid=inj_alias;
  for(integer l=0;l<38;l++) begin
    indices[0]=0; indices[1]=1; indices[2]=integer'(gw[l]-1); indices[3]=integer'(gw[l]);
    indices[4]=integer'(gh[l]*gw[l]-1); indices[5]=integer'(gh[l]*gw[l]);
    indices[6]=integer'(gcount[l]-2); indices[7]=integer'(gcount[l]-1);
    for(integer p=0;p<8;p++) begin
      if(64'(indices[p])>=gcount[l]) continue;
      for(integer s=0;s<8;s++) for(integer ctrl=0;ctrl<256;ctrl++) for(integer e=0;e<8;e++) begin
        reset_all; seed(l,64'(indices[p]),3'(s));
        hard_reset=ctrl[0]; abort=ctrl[1]; backend_start=ctrl[2]; buffer_owner_pl=ctrl[3];
        inj_fault=ctrl[4]; inj_alias=ctrl[5]; inj_ready=ctrl[6]; inj_result=ctrl[7]; inj_error=3'(e);
        tick; boundary_cases++;
      end
    end
    $display("BOUNDARY layer=%0d cases=%0d cycles=%0d",l,boundary_cases,cycles);
    $fflush();
  end
  release old.selected_result_valid; release new.selected_result_valid;
  release old.selected_result_error; release new.selected_result_error;
  release old.selected_start_ready; release new.selected_start_ready;
  release old.descriptor_fault; release new.descriptor_fault;
  release old.alias_valid; release new.alias_valid;
end endtask
task automatic invalid_layer;
begin
  for(integer l=38;l<=63;l+=25) begin
    reset_all; seed(l,17,1); tick;
    if(old.state!=old.ST_IDLE || integer'(old.layer_cursor)!=l || old.output_element_index!=17)
      $fatal(1,"非法layer控制不同");
  end
end endtask
task automatic full_traces;
longint unsigned previous_requests,previous_outputs,start_cycle,expected_requests;
begin
  for(integer l=0;l<38;l++) begin
    if(gop[l]<1 || gop[l]>3) continue;
    reset_all; seed(l,0,1); active_layer=l; gold_index=0; gold_step=0; trace_enabled=1;
    previous_requests=trace_requests; previous_outputs=trace_outputs; start_cycle=cycles; trace_digest=64'hcbf29ce484222325;
    while(integer'(old.layer_cursor)==l && cycles-start_cycle<gcount[l]*80+100) begin
      // 两边同一合法服务口，每11周期暂停mem，owner暂停不吞掉pending响应或结果。
      mem_ready=(cycles%11)!=0; buffer_owner_pl=(cycles%29)!=0;
      mem_rdata=memory_word(old_mem_addr); tick;
      if(old_operator_result_valid && old_operator_error_code!=0) $fatal(1,"合法trace错误layer=%0d code=%0d",l,old_operator_error_code);
    end
    trace_enabled=0; expected_requests=gcount[l]*(gop[l]==1 ? 5 : 2);
    if(gold_index!=gcount[l] || trace_requests-previous_requests!=expected_requests || trace_outputs-previous_outputs!=gcount[l])
      $fatal(1,"完整trace计数失败layer=%0d index=%0d requests=%0d",l,gold_index,trace_requests-previous_requests);
    $display("TRACE layer=%0d op=%0d outputs=%0d requests=%0d cycles=%0d digest=%016h",l,gop[l],gold_index,trace_requests-previous_requests,cycles-start_cycle,trace_digest);
    $fflush();
    trace_layers++;
  end
end endtask
task automatic actual_errors;
longint unsigned start_cycle;
begin
  // 真实非conv引擎响应错误、pending时owner掉低和每个WAIT状态abort。
  for(integer l=0;l<38;l++) begin
    if(gop[l]<1 || gop[l]>3) continue;
    for(integer e=1;e<8;e++) begin
      reset_all; seed(l,0,1); start_cycle=cycles;
      while(!old_mem_valid && cycles-start_cycle<100) tick;
      if(!old_mem_valid) $fatal(1,"错误刺激前无请求");
      mem_rdata=memory_word(old_mem_addr); mem_error_code=3'(e); tick;
      mem_error_code=0; buffer_owner_pl=0; tick; buffer_owner_pl=1;
      while(old.state!=old.ST_IDLE && cycles-start_cycle<200) tick;
      if(old.state!=old.ST_IDLE || old.output_element_index!=0) $fatal(1,"响应错误没有保持索引");
    end
    reset_all; seed(l,0,1); tick; abort=1; tick;
    if(old.state!=old.ST_IDLE || new.output_channel_cursor!=0 || new.output_y_cursor!=0 || new.output_x_cursor!=0)
      $fatal(1,"真实WAIT abort没有复位");
  end
end endtask
task automatic public_entries;
longint unsigned begin_cycle;
begin
  // 公共START真实走38层；只隔离卷积数值，不注入任何backend内部状态。
  reset_all; public_tracking=1; backend_start=1; tick; backend_start=0; begin_cycle=cycles;
  while(old.state!=old.ST_IDLE && cycles-begin_cycle<150000000) begin
    mem_ready=(cycles%11)!=0; buffer_owner_pl=(cycles%29)!=0;
    mem_rdata=memory_word(old_mem_addr); tick;
    if(old_operator_result_valid && old_operator_error_code!=0) $fatal(1,"公共完整路径错误");
  end
  public_tracking=0;
  if(old.state!=old.ST_IDLE || public_route_mask!=64'h0000000481494948)
    $fatal(1,"公共START未遍历冻结11个ROUTE layer mask=%h",public_route_mask);
  // 非法长度/base、启动时owner为低、重复START及abort/reset只改变控制输入。
  for(integer mode=0;mode<12;mode++) begin
    reset_all; public_tracking=1;
    case(mode)
      0: input_length_bytes=0;
      1: input_base_address=32'hffffffff;
      2: weight_package_length_bytes=0;
      3: weight_package_base_address=32'hffffffff;
      4: buffer_owner_pl=0;
      5: input_length_bytes=32'hffffffff;
      6: weight_package_length_bytes=32'hffffffff;
      default: begin end
    endcase
    backend_start=1; tick;
    for(integer n=0;n<256;n++) begin
      if(mode!=7) backend_start=0;
      if(mode==8 && n==13) abort=1;
      if(mode==9 && n==13) hard_reset=1;
      if(mode==10) buffer_owner_pl=n%3!=0;
      if(mode==11) mem_error_code=3'(n%8);
      mem_rdata=memory_word(old_mem_addr); tick;
    end
    public_start_trials++;
    public_tracking=0;
  end
  $display("PUBLIC_ENTRY trials=%0d route_mask=%h",public_start_trials,public_route_mask);
end endtask
initial begin
  reset_all; boundary; invalid_layer; actual_errors; full_traces; public_entries;
  if(owner_drop_results==0) $fatal(1,"真实owner掉低成功结果沿未覆盖");
  $display("PASS BACKEND_COORDINATES boundary=%0d layers=%0d outputs=%0d requests=%0d cycles=%0d owner_drop_results=%0d",boundary_cases,trace_layers,trace_outputs,trace_requests,cycles,owner_drop_results);
  $finish;
end
endmodule
""".replace("COMPARISONS", comparisons))
    # new是SystemVerilog关键字，信号前缀保留，实例名使用明确合法标识符。
    return re.sub(r"\bnew\b", "dut_new", "\n".join(parts) + "\n")


def execute(name: str, command: list[str], work: Path, evidence: Path, env: dict, report: dict, timeout: int):
    """只监视本次子进程树；RSS/时间/目录预算超限则终止并保存失败原件。"""
    log = evidence / (name + ".log")
    peak = 0; failure = None; started = time.monotonic(); progress = started
    with log.open("x", encoding="utf-8") as stream:
        process = subprocess.Popen(command, cwd=work, env=env, stdout=stream, stderr=subprocess.STDOUT)
        while process.poll() is None:
            try:
                parent = psutil.Process(process.pid)
                peak = max(peak, sum(p.memory_info().rss for p in [parent]+parent.children(recursive=True) if p.is_running()))
            except psutil.Error:
                pass
            if time.monotonic()-progress>30:
                progress=time.monotonic()
                print(json.dumps({"running": name, "seconds": round(progress-started), "peak_rss_bytes": peak}), flush=True)
            # 目录每5秒采样，避免遍历影响实际simulation；均不删除文件。
            sizes = None
            if int(time.monotonic()-started)%5==0:
                sizes = [sum(p.stat().st_size for p in directory.rglob("*") if p.is_file()) for directory in (work,evidence)]
            if peak>1610612736 or time.monotonic()-started>timeout or (sizes and (sizes[0]>314572800 or sizes[1]>104857600)):
                failure="RSS_LIMIT" if peak>1610612736 else "DISK_LIMIT" if sizes and (sizes[0]>314572800 or sizes[1]>104857600) else "TIMEOUT"
                subprocess.run(["taskkill","/PID",str(process.pid),"/T","/F"],stdout=stream,stderr=subprocess.STDOUT,timeout=30)
                process.wait(timeout=30); break
            time.sleep(0.1)
    record={"name":name,"command":command,"exit_code":process.returncode,"seconds":round(time.monotonic()-started,3),
            "peak_tree_rss_bytes":peak,"failure":failure,"log":log.relative_to(ROOT).as_posix(),"log_sha256":sha(log)}
    report["runs"].append(record)
    if failure or process.returncode!=0:
        raise ValueError(f"{name}失败：{record}")


def checker_negatives(checker, work: Path, bindings: dict) -> list:
    """隔离反例拒绝旧版本、自报SHA和未经授权的更新沿修改。"""
    fixture=work/"checker_fixture"; fixture.mkdir()
    for relative in bindings:
        path=fixture/relative; path.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(ROOT/relative,path)
    profile_path=fixture/"board/s2b_inference_platform.json"
    original=json.loads(profile_path.read_text(encoding="utf-8")); records=[]
    def reject(name,mutator):
        profile=copy.deepcopy(original); changed=mutator(profile)
        profile_path.write_text(json.dumps(profile,ensure_ascii=False),encoding="utf-8")
        try: checker.check_static(fixture)
        except (ValueError,KeyError,TypeError,OSError) as exc: records.append({"name":name,"status":"REJECTED","reason":str(exc)})
        else: raise ValueError("反例未拒绝："+name)
        finally:
            for relative in changed if isinstance(changed,list) else []: shutil.copyfile(ROOT/relative,fixture/relative)
            profile_path.write_bytes((ROOT/"board/s2b_inference_platform.json").read_bytes())
    def change(profile,path,before,after):
        target=fixture/path; raw=target.read_bytes(); expected=before.encode("utf-8")
        if raw.count(expected)!=1: raise ValueError("反例字符匹配非唯一")
        target.write_bytes(raw.replace(expected,after.encode("utf-8")))
        for item in profile["source_derivation"]["derived_sources"]+profile["source_derivation"]["upstream_sources"]:
            if item["path"]==path: item["sha256"]=sha(target)
        return [path]
    for version in ("0.1.0","0.1.1"):
        reject("旧profile"+version,lambda p,v=version:p.update(version="s2b-inference-platform/"+v))
    reject("旧派生policy",lambda p:p["source_derivation"].update(policy="s2b-constant-geometry-and-coordinates/1.0.0"))
    reject("旧派生基线",lambda p:p["source_derivation"].update(derivation_baseline_commit="18c0c34f9da885b5f35869c282dc0c2ed50d720e"))
    for name,before,after in (("通道宽度自报SHA","logic [8:0] output_channel_cursor","logic [7:0] output_channel_cursor"),
        ("carry自报SHA","output_channel_cursor + 9'd1","output_channel_cursor + 9'd2"),
        ("保持分支额外复位","default: begin\n                    state <= ST_IDLE;","default: begin\n                    output_x_cursor <= 0;\n                    state <= ST_IDLE;"),
        ("WAIT额外owner门禁","if (selected_result_valid) begin","if (selected_result_valid && buffer_owner_pl) begin")):
        reject(name,lambda p,b=before,a=after:change(p,"src/s2b_network_backend.sv",b,a))
    reject("允许替换自报",lambda p:p["source_derivation"]["derived_sources"][2]["replacements"].append(["state","bad"]))
    reject("冻结源自报SHA",lambda p:change(p,"src/s2a_network_backend.sv","module s2a_network_backend (","module bad_backend ("))
    reject("闭包遗漏",lambda p:p["rtl_sources"].pop())
    reject("闭包重复",lambda p:p["rtl_sources"].append(p["rtl_sources"][0]))
    reject("时钟降低",lambda p:p.update(clock_hz=25000000))
    reject("physical版本改变",lambda p:p.update(physical_interface="s2b-physical-candidate/0.1.2"))
    reject("旧Tcl版本",lambda p:change(p,"vivado/s2b_inference_platform.tcl","variable version 0.1.5","variable version 0.1.1"))
    reject("ROUTE引用原engine",lambda p:change(p,"src/s2b_network_backend.sv","s2b_route_engine u_route_engine","s2a_route_engine u_route_engine"))
    reject("ROUTE恢复动态除法自报SHA",lambda p:change(p,"src/s2b_route_query.sv","groups > 32'd2","groups > (source0_channels / groups)"))
    reject("ROUTE组2校验漂移自报SHA",lambda p:change(p,"src/s2b_route_query.sv","source0_channels[0]","source0_channels[1]"))
    reject("ROUTE额外结果门禁",lambda p:change(p,"src/s2b_route_engine.sv","if (result_valid && result_ready)","if (result_valid && result_ready && !abort)"))
    reject("CONV引用原engine",lambda p:change(p,"src/s2b_network_backend.sv","s2b_conv_tile_engine u_conv_engine","s2a_conv_tile_engine u_conv_engine"))
    reject("CONV校验新增batch语义自报SHA",lambda p:change(p,"src/s2b_conv_tile_engine.sv","(input_batch_count_latched != 32'd1)","(input_batch_count_latched != 32'd2)"))
    reject("CONV恢复batch乘积自报SHA",lambda p:change(p,"src/s2b_conv_tile_engine.sv","input_elements_wide = {96'd0, input_channels_latched} *","input_elements_wide = {96'd0, input_batch_count_latched} * {96'd0, input_channels_latched} *"))
    reject("CONV额外周期自报SHA",lambda p:change(p,"src/s2b_conv_tile_engine.sv","state <= ST_VALIDATE;","state <= ST_IDLE;"))
    return records


def main() -> int:
    """每次尝试独立落点，G1仅表示声明覆盖通过，实板/STA明确未运行。"""
    parser=argparse.ArgumentParser(); parser.add_argument("--run-id",required=True)
    parser.add_argument("--toolchain",type=Path,default=Path(r"D:\FPGA_S2A_MSYS2_20261001\env"))
    parser.add_argument("--prepare-only",action="store_true")
    args=parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+",args.run_id): parser.error("RunId非法")
    work=ROOT/"tmp/2B/S2B-T17"/args.run_id; evidence=ROOT/"report/evidence/S2B-T17"/args.run_id
    for parent in (work.parent,evidence.parent):
        if not parent.is_dir() or parent.is_symlink(): parser.error("精确父目录不可用")
    if work.exists() or evidence.exists(): parser.error("RunId已存在，不覆盖")
    work.mkdir(); evidence.mkdir(); started=time.monotonic()
    report={"schema_version":1,"task_id":"S2B-T17-S3","run_id":args.run_id,"task_baseline_commit":BASELINE,
            "status":"FAIL","runs":[],"g3":"NOT_RUN","sta":"NOT_RUN",
            "limitations":["卷积计算使用与原端口一致的共享stub，仅验证backend控制；未声称CONV数值或整网功能回归。",
                "非conv每层独立复位并注入合法DISPATCH层入口，真实pool/route/up与两个真实backend全周期执行；不执行前置卷积。",
                "完整非conv trace采用独立manifest黄金逐请求核对和流式digest，不保存巨量逐笔文本；可从固定来源重放。",
                "boundary使用relational寄存器初态及双方相同控制注入，验证实际FF分支；完整trace不注入内部控制。",
                "Verilator继承诊断保留-Wall/-Wno-fatal日志，不抑制原WIDTH/UNUSED警告；50MHz需独立新综合/STA。"],
            "resource_budget":{"jobs":1,"threads":1,"rss_limit_bytes":1610612736,"cache_limit_bytes":314572800,"evidence_limit_bytes":104857600}}
    try:
        checker=load_checker(); bindings=checker.check_static(ROOT)
        actual=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
        committed_changes=subprocess.check_output(["git","diff","--name-only",SOURCE_BASELINE,actual,"--",*bindings],cwd=ROOT,text=True).splitlines()
        if committed_changes: raise ValueError("任务源码闭包的提交来源改变")
        report["committed_source_changes_since_task_baseline"]=committed_changes
        report["source_commit"]=actual; report["source_sha256_pre"]={**bindings,RUNNER:sha(ROOT/RUNNER)}
        report["frozen14_sha256_pre"]={p:sha(ROOT/p) for p in checker.FROZEN_CORE_SHA256}
        old=subprocess.check_output(["git","show",BASELINE+":src/s2b_network_backend.sv"],cwd=ROOT)
        if hashlib.sha256(old).hexdigest()!=OLD_BACKEND_SHA: raise ValueError("S2 raw来源不符")
        (evidence/"s2_network_backend.sv").write_bytes(old)
        report["original_backend"]={"commit":BASELINE,"git_path":"src/s2b_network_backend.sv","raw_sha256":OLD_BACKEND_SHA,
                                    "compile_transformation":"仅将唯一module名称替换为s2b_network_backend_original"}
        if sha(ROOT/MODEL)!=MODEL_SHA: raise ValueError("模型SHA变化")
        model=json.loads((ROOT/MODEL).read_text(encoding="utf-8"))
        report["math_proof"]=math_proof(model,(ROOT/RTL[0]).read_text(encoding="utf-8"))
        report["checker_negatives"]=checker_negatives(checker,work,bindings)
        source=work/"source"; source.mkdir()
        for relative in RTL: shutil.copyfile(ROOT/relative,source/Path(relative).name)
        compiled_old=old.decode("utf-8").replace("module s2b_network_backend (","module s2b_network_backend_original (")
        (source/"s2_network_backend.sv").write_text(compiled_old,encoding="utf-8",newline="\n")
        for name,payload in (("convolution_stub.sv",convolution_stub()),("tb_s2b_backend_coordinates.sv",generate_tb(model))):
            for directory in (work,evidence): (directory/name).write_text(payload,encoding="utf-8",newline="\n")
        nonconv=[row for row in model["layers"] if row["op"] in ("maxpool","route","upsample")]
        counts=[math.prod(row["output_shape_nchw"]) for row in nonconv]
        report["coverage_expected"]={"nonconv_layers":len(nonconv),"nonconv_outputs":sum(counts),
            "nonconv_requests":sum(count*(5 if row["op"]=="maxpool" else 2) for row,count in zip(nonconv,counts)),
            "boundary_cases":38*8*8*256*8,"all_error_codes":list(range(8)),"all_states":list(range(8))}
        env=os.environ.copy(); bin_dir=args.toolchain/"mingw64/bin"; make_dir=args.toolchain/"usr/bin"
        verilator=bin_dir/"verilator_bin.exe"
        env["PATH"]=str(make_dir)+os.pathsep+str(bin_dir)+os.pathsep+env.get("PATH","")
        env["VERILATOR_ROOT"]=str(args.toolchain/"mingw64/share/verilator"); env["PYTHONUTF8"]="1"
        for path in (verilator,bin_dir/"g++.exe",make_dir/"make.exe"): checker.exact_file(path)
        report["resource_preflight"]={"available_ram_bytes":psutil.virtual_memory().available,"disk_free_bytes":shutil.disk_usage(work).free,
            "running_vivado":[{"pid":p.pid,"rss":p.memory_info().rss} for p in psutil.process_iter(["name"]) if p.info["name"] and p.info["name"].lower()=="vivado.exe"],
            "heavy_slot":"总控已明确S2退出且保留唯一heavy槽；job1/thread1。"}
        if report["resource_preflight"]["available_ram_bytes"]<2147483648 or report["resource_preflight"]["disk_free_bytes"]<1073741824:
            raise ValueError("资源不足，未编译")
        report["tool_versions"]={"python":sys.version,"verilator":subprocess.check_output([str(verilator),"--version"],env=env,cwd=work,text=True,timeout=30).strip()}
        command=[str(verilator),"--binary","--timing","--timescale","1ns/1ps","-Wall","-Wno-fatal","-j","1","--threads","1",
            "--output-split","10000","--output-split-cfuncs","100","--top-module","tb_s2b_backend_coordinates","--Mdir","obj_dir",
            "-MAKEFLAGS","PYTHON3='\""+sys.executable+"\"'","-CFLAGS","-D_GLIBCXX_USE_CXX11_ABI=0 -O1",
            *["source/"+Path(path).name for path in RTL],"source/s2_network_backend.sv","convolution_stub.sv","tb_s2b_backend_coordinates.sv"]
        report["prepared_compile_command"]=command
        if args.prepare_only:
            report["status"]="PREPARED_NOT_COMPILED"
        else:
            execute("compile",command,work,evidence,env,report,600)
            execute("simulation",[str(work/"obj_dir/Vtb_s2b_backend_coordinates.exe")],work,evidence,env,report,1200)
            text=(evidence/"simulation.log").read_text(encoding="utf-8")
            final=re.findall(r"PASS BACKEND_COORDINATES boundary=(\d+) layers=(\d+) outputs=(\d+) requests=(\d+) cycles=(\d+) owner_drop_results=(\d+)",text)
            if len(final)!=1: raise ValueError("缺少唯一RTL PASS")
            actual_counts=dict(zip(("boundary_cases","nonconv_layers","nonconv_outputs","nonconv_requests","cycles","owner_drop_results"),map(int,final[0])))
            for key,expected in report["coverage_expected"].items():
                if key in actual_counts and actual_counts[key]!=expected: raise ValueError("实际覆盖计数不同："+key)
            report["simulation_counts"]=actual_counts
            report["trace_summaries"]=re.findall(r"TRACE layer=(\d+) op=(\d+) outputs=(\d+) requests=(\d+) cycles=(\d+) digest=([0-9a-fA-F]+)",text)
            if len(report["trace_summaries"])!=len(nonconv): raise ValueError("trace层数不完整")
            public=re.findall(r"PUBLIC_ENTRY trials=(\d+) route_mask=([0-9a-fA-F]+)",text)
            if len(public)!=1 or int(public[0][0])!=12 or int(public[0][1],16)!=sum(1<<i for i in (3,6,8,11,14,16,19,22,24,31,34)):
                raise ValueError("真实公共START可达路径覆盖不足")
            report["public_entries"]={"trials":12,"route_layer_mask":public[0][1],
                "method":"一次合法公共START完整38层及12类公共非法/owner/重复START/abort/reset输入；无内部状态注入，卷积只使用共享控制stub。"}
            report["status"]="PASS_BACKEND_COORDINATES_G1"
        report["source_sha256_post"]={p:sha(ROOT/p) for p in report["source_sha256_pre"]}
        report["frozen14_sha256_post"]={p:sha(ROOT/p) for p in checker.FROZEN_CORE_SHA256}
        if report["source_sha256_pre"]!=report["source_sha256_post"] or report["frozen14_sha256_pre"]!=report["frozen14_sha256_post"]:
            raise ValueError("验证期间来源变化")
    except Exception as exc:
        report["failure"]=repr(exc); report["status"]="FAIL"
    report["seconds"]=round(time.monotonic()-started,3)
    report["artifacts"]=[{"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"bytes":p.stat().st_size} for p in evidence.rglob("*") if p.is_file()]
    (evidence/"validation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"status":report["status"],"run_id":args.run_id,"seconds":report["seconds"],
                      "counts":report.get("simulation_counts"),"failure":report.get("failure")},ensure_ascii=False),flush=True)
    return 0 if report["status"] in ("PASS_BACKEND_COORDINATES_G1","PREPARED_NOT_COMPILED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
