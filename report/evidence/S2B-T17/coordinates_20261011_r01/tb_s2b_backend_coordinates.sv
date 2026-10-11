// 基线backend为Git原始S1源码，除模块名外未改；候选为实际S2源。
module tb_s2b_backend_coordinates;
localparam longint unsigned gc[0:37] = '{32,64,64,32,32,32,64,64,128,128,128,64,64,64,128,128,256,256,256,128,128,128,256,256,512,512,512,256,512,30,30,256,128,128,384,256,30,30};
localparam longint unsigned gh[0:37] = '{208,104,104,104,104,104,104,104,104,52,52,52,52,52,52,52,52,26,26,26,26,26,26,26,26,13,13,13,13,13,13,13,13,26,26,26,26,26};
localparam longint unsigned gw[0:37] = '{208,104,104,104,104,104,104,104,104,52,52,52,52,52,52,52,52,26,26,26,26,26,26,26,26,13,13,13,13,13,13,13,13,26,26,26,26,26};
localparam longint unsigned gbase[0:37] = '{16777216,18161664,18853888,19546112,19892224,20238336,20584448,21276672,21968896,23353344,23699456,24045568,24218624,24391680,24564736,24910848,25256960,25949184,26122240,26295296,26381824,26468352,26554880,26727936,26900992,27247104,27333632,27420160,27463424,27549952,27549952,27555072,27598336,27619968,27706496,27966080,28139136,28139136};
localparam longint unsigned gcount[0:37] = '{1384448,692224,692224,346112,346112,346112,692224,692224,1384448,346112,346112,173056,173056,173056,346112,346112,692224,173056,173056,86528,86528,86528,173056,173056,346112,86528,86528,43264,86528,5070,5070,43264,21632,86528,259584,173056,20280,20280};
localparam longint unsigned gop[0:37] = '{0,0,0,2,0,0,2,0,2,1,0,2,0,0,2,0,2,1,0,2,0,0,2,0,2,1,0,0,0,0,4,2,0,3,2,0,0,4};
localparam longint unsigned gsrc0[0:37] = '{0,16777216,18161664,18853888,19546112,19892224,20238336,20584448,18853888,21968896,23353344,23699456,24045568,24218624,24391680,24564736,23699456,25256960,25949184,26122240,26295296,26381824,26468352,26554880,26122240,26900992,27247104,27333632,27420160,27463424,27549952,27420160,27555072,27598336,27619968,27706496,27966080,28139136};
localparam longint unsigned gsrc1[0:37] = '{0,0,0,0,0,0,19892224,0,21276672,0,0,0,0,0,24218624,0,24910848,0,0,0,0,0,26381824,0,26727936,0,0,0,0,0,0,0,0,0,26727936,0,0,0};
localparam longint unsigned gsh0[0:37] = '{0,208,104,104,104,104,104,104,104,104,52,52,52,52,52,52,52,52,26,26,26,26,26,26,26,26,13,13,13,13,13,13,13,13,26,26,26,26};
localparam longint unsigned gsw0[0:37] = '{0,208,104,104,104,104,104,104,104,104,52,52,52,52,52,52,52,52,26,26,26,26,26,26,26,26,13,13,13,13,13,13,13,13,26,26,26,26};
localparam longint unsigned gsh1[0:37] = '{0,0,0,0,0,0,104,0,104,0,0,0,0,0,52,0,52,0,0,0,0,0,26,0,26,0,0,0,0,0,0,0,0,0,26,0,0,0};
localparam longint unsigned gsw1[0:37] = '{0,0,0,0,0,0,104,0,104,0,0,0,0,0,52,0,52,0,0,0,0,0,26,0,26,0,0,0,0,0,0,0,0,0,26,0,0,0};
localparam longint unsigned gstart0[0:37] = '{0,0,0,32,0,0,0,0,0,0,0,64,0,0,0,0,0,0,0,128,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
localparam longint unsigned gstart1[0:37] = '{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
localparam longint unsigned gchannels0[0:37] = '{0,32,64,32,32,32,32,64,64,128,128,64,64,64,64,128,128,256,256,128,128,128,128,256,256,512,512,512,256,512,30,256,256,128,128,384,256,30};
localparam longint unsigned gmul0[0:37] = '{2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,1760973029,2147483648,2147483648,2147483648,2147483648,2147483648,1902693503,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,1959924335,2147483648,2147483648,2147483648};
localparam longint unsigned gmul1[0:37] = '{2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,1771485120,2147483648,1079448152,2147483648,2147483648,2147483648,2147483648,2147483648,1840756065,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,1625315065,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648,2147483648};
logic clk=0, hard_reset=1, abort=0, backend_start=0, buffer_owner_pl=1;
logic [31:0] input_base_address=0, input_length_bytes=519168;
logic [31:0] weight_package_base_address=0, weight_package_length_bytes=5903100;
logic mem_ready=1; logic [31:0] mem_rdata=0; logic [2:0] mem_error_code=0;
longint unsigned cycles=0, boundary_cases=0, trace_requests=0, trace_outputs=0, trace_digest;
integer active_layer=0, gold_index=0, gold_step=0, trace_layers=0;
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
s2b_network_backend new (.clk(clk),.hard_reset(hard_reset),.abort(abort),.backend_start(backend_start),.buffer_owner_pl(buffer_owner_pl),.input_base_address(input_base_address),.input_length_bytes(input_length_bytes),.weight_package_base_address(weight_package_base_address),.weight_package_length_bytes(weight_package_length_bytes),.mem_valid(new_mem_valid),.mem_write(new_mem_write),.mem_addr(new_mem_addr),.mem_wdata(new_mem_wdata),.mem_rstrb(new_mem_rstrb),.mem_wstrb(new_mem_wstrb),.mem_ready(mem_ready),.mem_rdata(mem_rdata),.mem_error_code(mem_error_code),.backend_memory_error_valid(new_backend_memory_error_valid),.backend_memory_error_code(new_backend_memory_error_code),.operator_result_valid(new_operator_result_valid),.operator_error_code(new_operator_error_code));

task automatic compare;
begin
if(old_mem_valid !== new_mem_valid) $fatal(1,"公开端口差异 mem_valid cycle=%0d layer=%0d index=%0d old=%h new=%h",cycles,old.layer_cursor,old.output_element_index,old_mem_valid,new_mem_valid);
if(old_mem_write !== new_mem_write) $fatal(1,"公开端口差异 mem_write cycle=%0d layer=%0d index=%0d old=%h new=%h",cycles,old.layer_cursor,old.output_element_index,old_mem_write,new_mem_write);
if(old_mem_addr !== new_mem_addr) $fatal(1,"公开端口差异 mem_addr cycle=%0d layer=%0d index=%0d old=%h new=%h",cycles,old.layer_cursor,old.output_element_index,old_mem_addr,new_mem_addr);
if(old_mem_wdata !== new_mem_wdata) $fatal(1,"公开端口差异 mem_wdata cycle=%0d layer=%0d index=%0d old=%h new=%h",cycles,old.layer_cursor,old.output_element_index,old_mem_wdata,new_mem_wdata);
if(old_mem_rstrb !== new_mem_rstrb) $fatal(1,"公开端口差异 mem_rstrb cycle=%0d layer=%0d index=%0d old=%h new=%h",cycles,old.layer_cursor,old.output_element_index,old_mem_rstrb,new_mem_rstrb);
if(old_mem_wstrb !== new_mem_wstrb) $fatal(1,"公开端口差异 mem_wstrb cycle=%0d layer=%0d index=%0d old=%h new=%h",cycles,old.layer_cursor,old.output_element_index,old_mem_wstrb,new_mem_wstrb);
if(old_backend_memory_error_valid !== new_backend_memory_error_valid) $fatal(1,"公开端口差异 backend_memory_error_valid cycle=%0d layer=%0d index=%0d old=%h new=%h",cycles,old.layer_cursor,old.output_element_index,old_backend_memory_error_valid,new_backend_memory_error_valid);
if(old_backend_memory_error_code !== new_backend_memory_error_code) $fatal(1,"公开端口差异 backend_memory_error_code cycle=%0d layer=%0d index=%0d old=%h new=%h",cycles,old.layer_cursor,old.output_element_index,old_backend_memory_error_code,new_backend_memory_error_code);
if(old_operator_result_valid !== new_operator_result_valid) $fatal(1,"公开端口差异 operator_result_valid cycle=%0d layer=%0d index=%0d old=%h new=%h",cycles,old.layer_cursor,old.output_element_index,old_operator_result_valid,new_operator_result_valid);
if(old_operator_error_code !== new_operator_error_code) $fatal(1,"公开端口差异 operator_error_code cycle=%0d layer=%0d index=%0d old=%h new=%h",cycles,old.layer_cursor,old.output_element_index,old_operator_error_code,new_operator_error_code);
  if(old.state !== new.state || old.layer_cursor !== new.layer_cursor || old.output_element_index !== new.output_element_index)
    $fatal(1,"状态或指针逐周期不同 cycle=%0d",cycles);
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
integer value,result_value,tap;
logic writing; logic [31:0] address,wdata; logic [3:0] lane;
begin
  if(gold_index>=gcount[active_layer]) $fatal(1,"完成后额外请求");
  c=gold_index/(gh[active_layer]*gw[active_layer]); y=(gold_index/gw[active_layer])%gh[active_layer]; x=gold_index%gw[active_layer];
  output_address=gbase[active_layer]+gold_index; source_address=0; slot=0; channel=c;
  if(gop[active_layer]==1) begin
    tap=gold_step<4 ? gold_step : 0;
    source_address=gsrc0[active_layer]+(c*gsh0[active_layer]+2*y+tap/2)*gsw0[active_layer]+2*x+tap%2;
    result_value=-127;
    for(integer t=0;t<4;t++) begin
      value=$signed(memory_byte(32'(gsrc0[active_layer]+(c*gsh0[active_layer]+2*y+t/2)*gsw0[active_layer]+2*x+t%2)));
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
    value=$signed(memory_byte(32'(source_address))); magnitude=value<0 ? -value : value;
    product=magnitude*selected_multiplier; result_value=integer'((product+64'd1073741824)/64'd2147483648);
    if(value<0) result_value=-result_value;
    if(result_value>127) result_value=127; if(result_value< -127) result_value=-127;
    writing=gold_step==1;
  end else begin
    source_address=gsrc0[active_layer]+(c*gsh0[active_layer]+y/2)*gsw0[active_layer]+x/2;
    result_value=$signed(memory_byte(32'(source_address))); writing=gold_step==1;
  end
  address=32'(writing ? output_address : source_address) & 32'hfffffffc;
  lane=4'b0001 << (writing ? output_address[1:0] : source_address[1:0]);
  wdata=writing ? (32'(8'(result_value)) << (8*output_address[1:0])) : 0;
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
  if(trace_enabled && old_mem_valid && mem_ready) golden_request;
  clk=1; #1; cycles++; compare; clk=0; #1;
end endtask
task automatic reset_all;
begin
  trace_enabled=0; abort=0; backend_start=0; buffer_owner_pl=1; mem_ready=1; mem_error_code=0;
  input_base_address=0; input_length_bytes=519168; weight_package_base_address=0; weight_package_length_bytes=5903100;
  hard_reset=1; tick; hard_reset=0; #1;
end endtask
task automatic seed(input integer layer,input integer index,input integer state_number);
begin
  old.layer_cursor=6'(layer); new.layer_cursor=6'(layer); old.output_element_index=32'(index); new.output_element_index=32'(index);
  old.state=type(old.state)'(state_number); new.state=type(new.state)'(state_number);
  if(layer<38) begin
    new.output_channel_cursor=9'((index/(gh[layer]*gw[layer]))%gc[layer]);
    new.output_y_cursor=8'((index/gw[layer])%gh[layer]); new.output_x_cursor=8'(index%gw[layer]);
  end else begin new.output_channel_cursor=0; new.output_y_cursor=0; new.output_x_cursor=0; end
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
      if(indices[p]>=gcount[l]) continue;
      for(integer s=0;s<8;s++) for(integer ctrl=0;ctrl<256;ctrl++) for(integer e=0;e<8;e++) begin
        reset_all; seed(l,indices[p],s);
        hard_reset=ctrl[0]; abort=ctrl[1]; backend_start=ctrl[2]; buffer_owner_pl=ctrl[3];
        inj_fault=ctrl[4]; inj_alias=ctrl[5]; inj_ready=ctrl[6]; inj_result=ctrl[7]; inj_error=3'(e);
        tick; boundary_cases++;
      end
    end
    $display("BOUNDARY layer=%0d cases=%0d cycles=%0d",l,boundary_cases,cycles);
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
    if(old.state!=old.ST_IDLE || old.layer_cursor!=l || old.output_element_index!=17)
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
    while(old.layer_cursor==l && cycles-start_cycle<gcount[l]*80+100) begin
      // 两边同一合法服务口，每11周期暂停mem，owner暂停不吞掉pending响应或结果。
      mem_ready=(cycles%11)!=0; buffer_owner_pl=(cycles%29)!=0;
      mem_rdata=memory_word(old_mem_addr); tick;
      if(old_operator_result_valid && old_operator_error_code!=0) $fatal(1,"合法trace错误layer=%0d code=%0d",l,old_operator_error_code);
    end
    trace_enabled=0; expected_requests=gcount[l]*(gop[l]==1 ? 5 : 2);
    if(gold_index!=gcount[l] || trace_requests-previous_requests!=expected_requests || trace_outputs-previous_outputs!=gcount[l])
      $fatal(1,"完整trace计数失败layer=%0d index=%0d requests=%0d",l,gold_index,trace_requests-previous_requests);
    $display("TRACE layer=%0d op=%0d outputs=%0d requests=%0d cycles=%0d digest=%016h",l,gop[l],gold_index,trace_requests-previous_requests,cycles-start_cycle,trace_digest);
    trace_layers++;
  end
end endtask
task automatic actual_errors;
integer start_cycle;
begin
  // 真实非conv引擎响应错误、pending时owner掉低和每个WAIT状态abort。
  for(integer l=0;l<38;l++) begin
    if(gop[l]<1 || gop[l]>3) continue;
    for(integer e=1;e<8;e++) begin
      reset_all; seed(l,0,1); start_cycle=integer'(cycles);
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
initial begin
  reset_all; boundary; invalid_layer; actual_errors; full_traces;
  $display("PASS BACKEND_COORDINATES boundary=%0d layers=%0d outputs=%0d requests=%0d cycles=%0d",boundary_cases,trace_layers,trace_outputs,trace_requests,cycles);
  $finish;
end
endmodule

