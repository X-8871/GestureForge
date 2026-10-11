// 基线backend为Git原始S2源码，除模块名外未改；候选为实际S3源。
module tb_s2b_backend_coordinates;
localparam longint unsigned gc[0:37] = '{64'd32,64'd64,64'd64,64'd32,64'd32,64'd32,64'd64,64'd64,64'd128,64'd128,64'd128,64'd64,64'd64,64'd64,64'd128,64'd128,64'd256,64'd256,64'd256,64'd128,64'd128,64'd128,64'd256,64'd256,64'd512,64'd512,64'd512,64'd256,64'd512,64'd30,64'd30,64'd256,64'd128,64'd128,64'd384,64'd256,64'd30,64'd30};
localparam longint unsigned gh[0:37] = '{64'd208,64'd104,64'd104,64'd104,64'd104,64'd104,64'd104,64'd104,64'd104,64'd52,64'd52,64'd52,64'd52,64'd52,64'd52,64'd52,64'd52,64'd26,64'd26,64'd26,64'd26,64'd26,64'd26,64'd26,64'd26,64'd13,64'd13,64'd13,64'd13,64'd13,64'd13,64'd13,64'd13,64'd26,64'd26,64'd26,64'd26,64'd26};
localparam longint unsigned gw[0:37] = '{64'd208,64'd104,64'd104,64'd104,64'd104,64'd104,64'd104,64'd104,64'd104,64'd52,64'd52,64'd52,64'd52,64'd52,64'd52,64'd52,64'd52,64'd26,64'd26,64'd26,64'd26,64'd26,64'd26,64'd26,64'd26,64'd13,64'd13,64'd13,64'd13,64'd13,64'd13,64'd13,64'd13,64'd26,64'd26,64'd26,64'd26,64'd26};
localparam longint unsigned gbase[0:37] = '{64'd16777216,64'd18161664,64'd18853888,64'd19546112,64'd19892224,64'd20238336,64'd20584448,64'd21276672,64'd21968896,64'd23353344,64'd23699456,64'd24045568,64'd24218624,64'd24391680,64'd24564736,64'd24910848,64'd25256960,64'd25949184,64'd26122240,64'd26295296,64'd26381824,64'd26468352,64'd26554880,64'd26727936,64'd26900992,64'd27247104,64'd27333632,64'd27420160,64'd27463424,64'd27549952,64'd27549952,64'd27555072,64'd27598336,64'd27619968,64'd27706496,64'd27966080,64'd28139136,64'd28139136};
localparam longint unsigned gcount[0:37] = '{64'd1384448,64'd692224,64'd692224,64'd346112,64'd346112,64'd346112,64'd692224,64'd692224,64'd1384448,64'd346112,64'd346112,64'd173056,64'd173056,64'd173056,64'd346112,64'd346112,64'd692224,64'd173056,64'd173056,64'd86528,64'd86528,64'd86528,64'd173056,64'd173056,64'd346112,64'd86528,64'd86528,64'd43264,64'd86528,64'd5070,64'd5070,64'd43264,64'd21632,64'd86528,64'd259584,64'd173056,64'd20280,64'd20280};
localparam longint unsigned gop[0:37] = '{64'd0,64'd0,64'd0,64'd2,64'd0,64'd0,64'd2,64'd0,64'd2,64'd1,64'd0,64'd2,64'd0,64'd0,64'd2,64'd0,64'd2,64'd1,64'd0,64'd2,64'd0,64'd0,64'd2,64'd0,64'd2,64'd1,64'd0,64'd0,64'd0,64'd0,64'd4,64'd2,64'd0,64'd3,64'd2,64'd0,64'd0,64'd4};
localparam longint unsigned gsrc0[0:37] = '{64'd0,64'd16777216,64'd18161664,64'd18853888,64'd19546112,64'd19892224,64'd20238336,64'd20584448,64'd18853888,64'd21968896,64'd23353344,64'd23699456,64'd24045568,64'd24218624,64'd24391680,64'd24564736,64'd23699456,64'd25256960,64'd25949184,64'd26122240,64'd26295296,64'd26381824,64'd26468352,64'd26554880,64'd26122240,64'd26900992,64'd27247104,64'd27333632,64'd27420160,64'd27463424,64'd27549952,64'd27420160,64'd27555072,64'd27598336,64'd27619968,64'd27706496,64'd27966080,64'd28139136};
localparam longint unsigned gsrc1[0:37] = '{64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd19892224,64'd0,64'd21276672,64'd0,64'd0,64'd0,64'd0,64'd0,64'd24218624,64'd0,64'd24910848,64'd0,64'd0,64'd0,64'd0,64'd0,64'd26381824,64'd0,64'd26727936,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd26727936,64'd0,64'd0,64'd0};
localparam longint unsigned gsh0[0:37] = '{64'd0,64'd208,64'd104,64'd104,64'd104,64'd104,64'd104,64'd104,64'd104,64'd104,64'd52,64'd52,64'd52,64'd52,64'd52,64'd52,64'd52,64'd52,64'd26,64'd26,64'd26,64'd26,64'd26,64'd26,64'd26,64'd26,64'd13,64'd13,64'd13,64'd13,64'd13,64'd13,64'd13,64'd13,64'd26,64'd26,64'd26,64'd26};
localparam longint unsigned gsw0[0:37] = '{64'd0,64'd208,64'd104,64'd104,64'd104,64'd104,64'd104,64'd104,64'd104,64'd104,64'd52,64'd52,64'd52,64'd52,64'd52,64'd52,64'd52,64'd52,64'd26,64'd26,64'd26,64'd26,64'd26,64'd26,64'd26,64'd26,64'd13,64'd13,64'd13,64'd13,64'd13,64'd13,64'd13,64'd13,64'd26,64'd26,64'd26,64'd26};
localparam longint unsigned gsh1[0:37] = '{64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd104,64'd0,64'd104,64'd0,64'd0,64'd0,64'd0,64'd0,64'd52,64'd0,64'd52,64'd0,64'd0,64'd0,64'd0,64'd0,64'd26,64'd0,64'd26,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd26,64'd0,64'd0,64'd0};
localparam longint unsigned gsw1[0:37] = '{64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd104,64'd0,64'd104,64'd0,64'd0,64'd0,64'd0,64'd0,64'd52,64'd0,64'd52,64'd0,64'd0,64'd0,64'd0,64'd0,64'd26,64'd0,64'd26,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd26,64'd0,64'd0,64'd0};
localparam longint unsigned gstart0[0:37] = '{64'd0,64'd0,64'd0,64'd32,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd64,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd128,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0};
localparam longint unsigned gstart1[0:37] = '{64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0,64'd0};
localparam longint unsigned gchannels0[0:37] = '{64'd0,64'd32,64'd64,64'd32,64'd32,64'd32,64'd32,64'd64,64'd64,64'd128,64'd128,64'd64,64'd64,64'd64,64'd64,64'd128,64'd128,64'd256,64'd256,64'd128,64'd128,64'd128,64'd128,64'd256,64'd256,64'd512,64'd512,64'd512,64'd256,64'd512,64'd30,64'd256,64'd256,64'd128,64'd128,64'd384,64'd256,64'd30};
localparam longint unsigned gmul0[0:37] = '{64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd1760973029,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd1902693503,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd1959924335,64'd2147483648,64'd2147483648,64'd2147483648};
localparam longint unsigned gmul1[0:37] = '{64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd1771485120,64'd2147483648,64'd1079448152,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd1840756065,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd1625315065,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648,64'd2147483648};
logic clk=0, hard_reset=1, abort=0, backend_start=0, buffer_owner_pl=1;
logic [31:0] input_base_address=0, input_length_bytes=519168;
logic [31:0] weight_package_base_address=0, weight_package_length_bytes=5903100;
logic mem_ready=1; logic [31:0] mem_rdata=0; logic [2:0] mem_error_code=0;
longint unsigned cycles=0, boundary_cases=0, trace_requests=0, trace_outputs=0, trace_digest, owner_drop_results=0;
integer active_layer=0, gold_step=0, trace_layers=0; longint unsigned gold_index=0;
longint unsigned public_route_mask=0; integer public_start_trials=0; logic public_tracking=0;
logic trace_enabled=0; logic inj_result=0, inj_ready=1, inj_fault=0, inj_alias=1; logic [2:0] inj_error=0;
logic  old_mem_valid, new_mem_valid;
logic  old_mem_write, new_mem_write;
logic [31:0] old_mem_addr, new_mem_addr;
logic [31:0] old_mem_wdata, new_mem_wdata;
logic [3:0] old_mem_rstrb, new_mem_rstrb;
logic [3:0] old_mem_wstrb, new_mem_wstrb;
logic  old_backend_memory_error_valid, new_backend_memory_error_valid;
logic [2:0] old_backend_memory_error_code, new_backend_memory_error_code;
logic  old_operator_result_valid, new_operator_result_valid;
logic [2:0] old_operator_error_code, new_operator_error_code;
s2b_network_backend_original old (.clk(clk),.hard_reset(hard_reset),.abort(abort),.backend_start(backend_start),.buffer_owner_pl(buffer_owner_pl),.input_base_address(input_base_address),.input_length_bytes(input_length_bytes),.weight_package_base_address(weight_package_base_address),.weight_package_length_bytes(weight_package_length_bytes),.mem_valid(old_mem_valid),.mem_write(old_mem_write),.mem_addr(old_mem_addr),.mem_wdata(old_mem_wdata),.mem_rstrb(old_mem_rstrb),.mem_wstrb(old_mem_wstrb),.mem_ready(mem_ready),.mem_rdata(mem_rdata),.mem_error_code(mem_error_code),.backend_memory_error_valid(old_backend_memory_error_valid),.backend_memory_error_code(old_backend_memory_error_code),.operator_result_valid(old_operator_result_valid),.operator_error_code(old_operator_error_code));
s2b_network_backend dut_new (.clk(clk),.hard_reset(hard_reset),.abort(abort),.backend_start(backend_start),.buffer_owner_pl(buffer_owner_pl),.input_base_address(input_base_address),.input_length_bytes(input_length_bytes),.weight_package_base_address(weight_package_base_address),.weight_package_length_bytes(weight_package_length_bytes),.mem_valid(new_mem_valid),.mem_write(new_mem_write),.mem_addr(new_mem_addr),.mem_wdata(new_mem_wdata),.mem_rstrb(new_mem_rstrb),.mem_wstrb(new_mem_wstrb),.mem_ready(mem_ready),.mem_rdata(mem_rdata),.mem_error_code(mem_error_code),.backend_memory_error_valid(new_backend_memory_error_valid),.backend_memory_error_code(new_backend_memory_error_code),.operator_result_valid(new_operator_result_valid),.operator_error_code(new_operator_error_code));

task automatic compare;
begin
if(old_mem_valid !== new_mem_valid) $fatal(1,"公开端口差异 mem_valid cycle=%0d layer=%0d index=%0d old=%h dut_new=%h",cycles,old.layer_cursor,old.output_element_index,old_mem_valid,new_mem_valid);
if(old_mem_write !== new_mem_write) $fatal(1,"公开端口差异 mem_write cycle=%0d layer=%0d index=%0d old=%h dut_new=%h",cycles,old.layer_cursor,old.output_element_index,old_mem_write,new_mem_write);
if(old_mem_addr !== new_mem_addr) $fatal(1,"公开端口差异 mem_addr cycle=%0d layer=%0d index=%0d old=%h dut_new=%h",cycles,old.layer_cursor,old.output_element_index,old_mem_addr,new_mem_addr);
if(old_mem_wdata !== new_mem_wdata) $fatal(1,"公开端口差异 mem_wdata cycle=%0d layer=%0d index=%0d old=%h dut_new=%h",cycles,old.layer_cursor,old.output_element_index,old_mem_wdata,new_mem_wdata);
if(old_mem_rstrb !== new_mem_rstrb) $fatal(1,"公开端口差异 mem_rstrb cycle=%0d layer=%0d index=%0d old=%h dut_new=%h",cycles,old.layer_cursor,old.output_element_index,old_mem_rstrb,new_mem_rstrb);
if(old_mem_wstrb !== new_mem_wstrb) $fatal(1,"公开端口差异 mem_wstrb cycle=%0d layer=%0d index=%0d old=%h dut_new=%h",cycles,old.layer_cursor,old.output_element_index,old_mem_wstrb,new_mem_wstrb);
if(old_backend_memory_error_valid !== new_backend_memory_error_valid) $fatal(1,"公开端口差异 backend_memory_error_valid cycle=%0d layer=%0d index=%0d old=%h dut_new=%h",cycles,old.layer_cursor,old.output_element_index,old_backend_memory_error_valid,new_backend_memory_error_valid);
if(old_backend_memory_error_code !== new_backend_memory_error_code) $fatal(1,"公开端口差异 backend_memory_error_code cycle=%0d layer=%0d index=%0d old=%h dut_new=%h",cycles,old.layer_cursor,old.output_element_index,old_backend_memory_error_code,new_backend_memory_error_code);
if(old_operator_result_valid !== new_operator_result_valid) $fatal(1,"公开端口差异 operator_result_valid cycle=%0d layer=%0d index=%0d old=%h dut_new=%h",cycles,old.layer_cursor,old.output_element_index,old_operator_result_valid,new_operator_result_valid);
if(old_operator_error_code !== new_operator_error_code) $fatal(1,"公开端口差异 operator_error_code cycle=%0d layer=%0d index=%0d old=%h dut_new=%h",cycles,old.layer_cursor,old.output_element_index,old_operator_error_code,new_operator_error_code);
  if(old.state !== dut_new.state || old.layer_cursor !== dut_new.layer_cursor || old.output_element_index !== dut_new.output_element_index)
    $fatal(1,"状态或指针逐周期不同 cycle=%0d",cycles);
  if(old.route_start_valid && !(old.u_route_engine.groups == 1 || old.u_route_engine.groups == 2))
    $fatal(1,"原冻结ROM产生非法ROUTE组数");
  if(dut_new.route_start_valid && !(dut_new.u_route_engine.groups == 1 || dut_new.u_route_engine.groups == 2))
    $fatal(1,"派生backend产生非法ROUTE组数");
  if(old.layer_cursor<38 && old.decoded_channel !== dut_new.decoded_channel)
    $fatal(1,"通道不等价 cycle=%0d layer=%0d index=%0d old=%0d dut_new=%0d",cycles,old.layer_cursor,old.output_element_index,old.decoded_channel,dut_new.decoded_channel);
  if(old.layer_cursor<38 && (old.decoded_y !== dut_new.decoded_y || old.decoded_x !== dut_new.decoded_x))
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
  old.layer_cursor=6'(layer); dut_new.layer_cursor=6'(layer); old.output_element_index=32'(index); dut_new.output_element_index=32'(index);
  old.state=type(old.state)'(state_number); dut_new.state=type(dut_new.state)'(state_number);
  if(layer<38) begin
    dut_new.output_channel_cursor=9'((index/(gh[layer]*gw[layer]))%gc[layer]);
    dut_new.output_y_cursor=8'((index/gw[layer])%gh[layer]); dut_new.output_x_cursor=8'(index%gw[layer]);
  end else begin dut_new.output_channel_cursor=0; dut_new.output_y_cursor=0; dut_new.output_x_cursor=0; end
  #1; compare;
end endtask
task automatic boundary;
integer indices[0:7];
begin
  force old.selected_result_valid=inj_result; force dut_new.selected_result_valid=inj_result;
  force old.selected_result_error=inj_error; force dut_new.selected_result_error=inj_error;
  force old.selected_start_ready=inj_ready; force dut_new.selected_start_ready=inj_ready;
  force old.descriptor_fault=inj_fault; force dut_new.descriptor_fault=inj_fault;
  force old.alias_valid=inj_alias; force dut_new.alias_valid=inj_alias;
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
  release old.selected_result_valid; release dut_new.selected_result_valid;
  release old.selected_result_error; release dut_new.selected_result_error;
  release old.selected_start_ready; release dut_new.selected_start_ready;
  release old.descriptor_fault; release dut_new.descriptor_fault;
  release old.alias_valid; release dut_new.alias_valid;
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
    if(old.state!=old.ST_IDLE || dut_new.output_channel_cursor!=0 || dut_new.output_y_cursor!=0 || dut_new.output_x_cursor!=0)
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

