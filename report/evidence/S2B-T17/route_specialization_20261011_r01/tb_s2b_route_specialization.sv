module tb_s2b_route_specialization; logic clk=0, hard_reset=1; integer cycles=0,cases=0,query_cases=0,abort_mask=0,reset_mask=0;
integer pending=0,delay_count=0,requests=0,raw=0,response_error=0,error_target=0,stall=0; logic [31:0] rsp_data; logic [2:0] rsp_error;
logic  abort;
logic  start_valid;
logic  old_start_ready, new_start_ready;
logic [31:0] source_count;
logic [31:0] groups;
logic [31:0] group_id;
logic [31:0] output_channel;
logic [31:0] output_y;
logic [31:0] output_x;
logic [31:0] source0_base_address;
logic [31:0] source0_length_bytes;
logic [31:0] source0_channels;
logic [31:0] source0_height;
logic [31:0] source0_width;
logic [31:0] source0_channel_start;
logic [31:0] source0_channel_end;
logic [31:0] source0_multiplier_q31;
logic [31:0] source1_base_address;
logic [31:0] source1_length_bytes;
logic [31:0] source1_channels;
logic [31:0] source1_height;
logic [31:0] source1_width;
logic [31:0] source1_channel_start;
logic [31:0] source1_channel_end;
logic [31:0] source1_multiplier_q31;
logic [31:0] output_base_address;
logic [31:0] output_length_bytes;
logic [31:0] output_channels;
logic [31:0] output_height;
logic [31:0] output_width;
logic  old_backend_cancel, new_backend_cancel;
logic  old_backend_req_valid, new_backend_req_valid;
logic  backend_req_ready;
logic  old_backend_req_write, new_backend_req_write;
logic [31:0] old_backend_req_addr, new_backend_req_addr;
logic [31:0] old_backend_req_wdata, new_backend_req_wdata;
logic [3:0] old_backend_req_rstrb, new_backend_req_rstrb;
logic [3:0] old_backend_req_wstrb, new_backend_req_wstrb;
logic  backend_rsp_valid;
logic [31:0] backend_rsp_rdata;
logic [2:0] backend_rsp_error;
logic  old_result_valid, new_result_valid;
logic  result_ready;
logic [31:0] old_result_source_index, new_result_source_index;
logic [31:0] old_result_source_address, new_result_source_address;
logic [31:0] old_result_output_address, new_result_output_address;
logic [7:0] old_result_value, new_result_value;
logic [2:0] old_result_error_code, new_result_error_code;
s2a_route_engine dut_old (.clk(clk),.hard_reset(hard_reset),.abort(abort),.start_valid(start_valid),.start_ready(old_start_ready),.source_count(source_count),.groups(groups),.group_id(group_id),.output_channel(output_channel),.output_y(output_y),.output_x(output_x),.source0_base_address(source0_base_address),.source0_length_bytes(source0_length_bytes),.source0_channels(source0_channels),.source0_height(source0_height),.source0_width(source0_width),.source0_channel_start(source0_channel_start),.source0_channel_end(source0_channel_end),.source0_multiplier_q31(source0_multiplier_q31),.source1_base_address(source1_base_address),.source1_length_bytes(source1_length_bytes),.source1_channels(source1_channels),.source1_height(source1_height),.source1_width(source1_width),.source1_channel_start(source1_channel_start),.source1_channel_end(source1_channel_end),.source1_multiplier_q31(source1_multiplier_q31),.output_base_address(output_base_address),.output_length_bytes(output_length_bytes),.output_channels(output_channels),.output_height(output_height),.output_width(output_width),.backend_cancel(old_backend_cancel),.backend_req_valid(old_backend_req_valid),.backend_req_ready(backend_req_ready),.backend_req_write(old_backend_req_write),.backend_req_addr(old_backend_req_addr),.backend_req_wdata(old_backend_req_wdata),.backend_req_rstrb(old_backend_req_rstrb),.backend_req_wstrb(old_backend_req_wstrb),.backend_rsp_valid(backend_rsp_valid),.backend_rsp_rdata(backend_rsp_rdata),.backend_rsp_error(backend_rsp_error),.result_valid(old_result_valid),.result_ready(result_ready),.result_source_index(old_result_source_index),.result_source_address(old_result_source_address),.result_output_address(old_result_output_address),.result_value(old_result_value),.result_error_code(old_result_error_code));
s2b_route_engine dut_new (.clk(clk),.hard_reset(hard_reset),.abort(abort),.start_valid(start_valid),.start_ready(new_start_ready),.source_count(source_count),.groups(groups),.group_id(group_id),.output_channel(output_channel),.output_y(output_y),.output_x(output_x),.source0_base_address(source0_base_address),.source0_length_bytes(source0_length_bytes),.source0_channels(source0_channels),.source0_height(source0_height),.source0_width(source0_width),.source0_channel_start(source0_channel_start),.source0_channel_end(source0_channel_end),.source0_multiplier_q31(source0_multiplier_q31),.source1_base_address(source1_base_address),.source1_length_bytes(source1_length_bytes),.source1_channels(source1_channels),.source1_height(source1_height),.source1_width(source1_width),.source1_channel_start(source1_channel_start),.source1_channel_end(source1_channel_end),.source1_multiplier_q31(source1_multiplier_q31),.output_base_address(output_base_address),.output_length_bytes(output_length_bytes),.output_channels(output_channels),.output_height(output_height),.output_width(output_width),.backend_cancel(new_backend_cancel),.backend_req_valid(new_backend_req_valid),.backend_req_ready(backend_req_ready),.backend_req_write(new_backend_req_write),.backend_req_addr(new_backend_req_addr),.backend_req_wdata(new_backend_req_wdata),.backend_req_rstrb(new_backend_req_rstrb),.backend_req_wstrb(new_backend_req_wstrb),.backend_rsp_valid(backend_rsp_valid),.backend_rsp_rdata(backend_rsp_rdata),.backend_rsp_error(backend_rsp_error),.result_valid(new_result_valid),.result_ready(result_ready),.result_source_index(new_result_source_index),.result_source_address(new_result_source_address),.result_output_address(new_result_output_address),.result_value(new_result_value),.result_error_code(new_result_error_code));
task automatic compare; begin if(old_start_ready !== new_start_ready) $fatal(1,"route公开输出差异 start_ready case=%0d cycle=%0d",cases,cycles);
if(old_backend_cancel !== new_backend_cancel) $fatal(1,"route公开输出差异 backend_cancel case=%0d cycle=%0d",cases,cycles);
if(old_backend_req_valid !== new_backend_req_valid) $fatal(1,"route公开输出差异 backend_req_valid case=%0d cycle=%0d",cases,cycles);
if(old_backend_req_write !== new_backend_req_write) $fatal(1,"route公开输出差异 backend_req_write case=%0d cycle=%0d",cases,cycles);
if(old_backend_req_addr !== new_backend_req_addr) $fatal(1,"route公开输出差异 backend_req_addr case=%0d cycle=%0d",cases,cycles);
if(old_backend_req_wdata !== new_backend_req_wdata) $fatal(1,"route公开输出差异 backend_req_wdata case=%0d cycle=%0d",cases,cycles);
if(old_backend_req_rstrb !== new_backend_req_rstrb) $fatal(1,"route公开输出差异 backend_req_rstrb case=%0d cycle=%0d",cases,cycles);
if(old_backend_req_wstrb !== new_backend_req_wstrb) $fatal(1,"route公开输出差异 backend_req_wstrb case=%0d cycle=%0d",cases,cycles);
if(old_result_valid !== new_result_valid) $fatal(1,"route公开输出差异 result_valid case=%0d cycle=%0d",cases,cycles);
if(old_result_source_index !== new_result_source_index) $fatal(1,"route公开输出差异 result_source_index case=%0d cycle=%0d",cases,cycles);
if(old_result_source_address !== new_result_source_address) $fatal(1,"route公开输出差异 result_source_address case=%0d cycle=%0d",cases,cycles);
if(old_result_output_address !== new_result_output_address) $fatal(1,"route公开输出差异 result_output_address case=%0d cycle=%0d",cases,cycles);
if(old_result_value !== new_result_value) $fatal(1,"route公开输出差异 result_value case=%0d cycle=%0d",cases,cycles);
if(old_result_error_code !== new_result_error_code) $fatal(1,"route公开输出差异 result_error_code case=%0d cycle=%0d",cases,cycles); end endtask
task automatic tick; begin clk=0; #2;compare;clk=1;#2;compare;clk=0;#1;cycles++;end endtask
task automatic clear;begin abort=0; start_valid=0; source_count=0; groups=0; group_id=0; output_channel=0; output_y=0; output_x=0; source0_base_address=0; source0_length_bytes=0; source0_channels=0; source0_height=0; source0_width=0; source0_channel_start=0; source0_channel_end=0; source0_multiplier_q31=0; source1_base_address=0; source1_length_bytes=0; source1_channels=0; source1_height=0; source1_width=0; source1_channel_start=0; source1_channel_end=0; source1_multiplier_q31=0; output_base_address=0; output_length_bytes=0; output_channels=0; output_height=0; output_width=0; backend_req_ready=0; backend_rsp_valid=0; backend_rsp_rdata=0; backend_rsp_error=0; result_ready=0; pending=0;requests=0;hard_reset=1;tick;hard_reset=0;tick;end endtask

task automatic service;
logic accept_request,responding;
begin
 backend_req_ready = stall == 2 ? 0 : stall == 0 || cycles%5!=0;
 backend_rsp_valid = pending && delay_count==0;
 backend_rsp_rdata=rsp_data;backend_rsp_error=rsp_error;
 #1;accept_request=old_backend_req_valid&&backend_req_ready;responding=backend_rsp_valid;
 tick;
 if(responding) pending=0;
 else if(pending&&delay_count>0) delay_count--;
 if(accept_request) begin
  if(pending) $fatal(1,"重复请求");
  requests++; pending=1;delay_count=stall==0 ? 0 : cycles%4;
  rsp_data={4{8'(raw)}};
  rsp_error=requests==error_target ? 3'(response_error) : 0;
 end
end endtask

logic signed [7:0] source0_value=0,source1_value=0;
logic [31:0] qo_output_channels,qn_output_channels;
logic [31:0] qo_output_height,qn_output_height;
logic [31:0] qo_output_width,qn_output_width;
logic [31:0] qo_source_index,qn_source_index;
logic [31:0] qo_source_channel,qn_source_channel;
logic [31:0] qo_source_address,qn_source_address;
logic [7:0] qo_output_value,qn_output_value;
logic [2:0] qo_error_code,qn_error_code;
int8_route_query q_qo (.source_count(source_count),.groups(groups),.group_id(group_id),.output_channel(output_channel),.output_y(output_y),.output_x(output_x),.source0_base_address(source0_base_address),.source0_length_bytes(source0_length_bytes),.source0_channels(source0_channels),.source0_height(source0_height),.source0_width(source0_width),.source0_channel_start(source0_channel_start),.source0_channel_end(source0_channel_end),.source0_multiplier_q31(source0_multiplier_q31),.source0_value(source0_value),.source1_base_address(source1_base_address),.source1_length_bytes(source1_length_bytes),.source1_channels(source1_channels),.source1_height(source1_height),.source1_width(source1_width),.source1_channel_start(source1_channel_start),.source1_channel_end(source1_channel_end),.source1_multiplier_q31(source1_multiplier_q31),.source1_value(source1_value),.output_channels(qo_output_channels),.output_height(qo_output_height),.output_width(qo_output_width),.source_index(qo_source_index),.source_channel(qo_source_channel),.source_address(qo_source_address),.output_value(qo_output_value),.error_code(qo_error_code));
s2b_route_query q_qn (.source_count(source_count),.groups(groups),.group_id(group_id),.output_channel(output_channel),.output_y(output_y),.output_x(output_x),.source0_base_address(source0_base_address),.source0_length_bytes(source0_length_bytes),.source0_channels(source0_channels),.source0_height(source0_height),.source0_width(source0_width),.source0_channel_start(source0_channel_start),.source0_channel_end(source0_channel_end),.source0_multiplier_q31(source0_multiplier_q31),.source0_value(source0_value),.source1_base_address(source1_base_address),.source1_length_bytes(source1_length_bytes),.source1_channels(source1_channels),.source1_height(source1_height),.source1_width(source1_width),.source1_channel_start(source1_channel_start),.source1_channel_end(source1_channel_end),.source1_multiplier_q31(source1_multiplier_q31),.source1_value(source1_value),.output_channels(qn_output_channels),.output_height(qn_output_height),.output_width(qn_output_width),.source_index(qn_source_index),.source_channel(qn_source_channel),.source_address(qn_source_address),.output_value(qn_output_value),.error_code(qn_error_code));
task automatic query_compare;begin #1;if(qo_output_channels!==qn_output_channels)$fatal(1,"query差异 output_channels"); if(qo_output_height!==qn_output_height)$fatal(1,"query差异 output_height"); if(qo_output_width!==qn_output_width)$fatal(1,"query差异 output_width"); if(qo_source_index!==qn_source_index)$fatal(1,"query差异 source_index"); if(qo_source_channel!==qn_source_channel)$fatal(1,"query差异 source_channel"); if(qo_source_address!==qn_source_address)$fatal(1,"query差异 source_address"); if(qo_output_value!==qn_output_value)$fatal(1,"query差异 output_value"); if(qo_error_code!==qn_error_code)$fatal(1,"query差异 error_code");query_cases++;end endtask
integer fh,scanned,control,target_state,expected_error,expected_slot,expected_addr,expected_outaddr,expected_value,expected_requests,elapsed,injected;
initial begin clear;fh=$fopen("route_vectors.dat","r");if(!fh)$fatal(1,"缺向量");while(!$feof(fh)) begin
clear;scanned=$fscanf(fh,"%h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h\n",source_count,groups,group_id,output_channel,output_y,output_x,source0_base_address,source0_length_bytes,source0_channels,source0_height,source0_width,source0_channel_start,source0_channel_end,source0_multiplier_q31,source1_base_address,source1_length_bytes,source1_channels,source1_height,source1_width,source1_channel_start,source1_channel_end,source1_multiplier_q31,output_base_address,output_length_bytes,output_channels,output_height,output_width,raw,response_error,error_target,control,target_state,stall,expected_error,expected_slot,expected_addr,expected_outaddr,expected_value,expected_requests);

if(scanned==39) begin
 start_valid=1;result_ready=0;injected=0;
 if(control && target_state==0) begin
  if(control==1) begin abort=1;abort_mask|=1;end
  else begin hard_reset=1;reset_mask|=1;end
 end
 tick;start_valid=0;
 if(control && target_state==0) begin
  abort=0;hard_reset=0;tick;
 end else begin
  elapsed=0;
  while(!old_result_valid&&elapsed<300) begin
   if((control==1||control==2)&&integer'(dut_old.state)==target_state) begin
    if(control==1) begin abort=1;abort_mask|=1<<target_state;end
    else begin hard_reset=1;reset_mask|=1<<target_state;end
    tick;injected=1;break;
   end
   service;elapsed++;
   if(control==3&&elapsed==200) begin
    if(old_result_valid||requests!=0) $fatal(1,"无限请求背压提前完成");
    abort=1;tick;injected=1;break;
   end
  end
  if(injected) begin
   if(old_result_valid||old_backend_req_valid) $fatal(1,"活动状态取消失败");
   pending=0;abort=0;hard_reset=0;tick;
  end else begin
   if(!old_result_valid||old_result_error_code!==3'(expected_error)||requests!=expected_requests)
    $fatal(1,"结果/请求oracle不同 case=%0d code=%0d expected=%0d requests=%0d expectedrequests=%0d",cases,old_result_error_code,expected_error,requests,expected_requests);
   if(!expected_error && (old_result_source_index!==32'(expected_slot)||old_result_source_address!==32'(expected_addr)||old_result_output_address!==32'(expected_outaddr)||old_result_value!==8'(expected_value)))
    $fatal(1,"独立数学结果不同");
   if(control&&target_state==7) begin
    if(control==1) begin abort=1;abort_mask|=128;tick;if(!old_result_valid)$fatal(1,"RESULT abort未保持");abort=0;end
    else begin hard_reset=1;reset_mask|=128;tick;if(old_result_valid)$fatal(1,"RESULT reset未清空");hard_reset=0;end
   end
   repeat(3) service;
   result_ready=1;tick;result_ready=0;
  end
 end
 cases++;
end else if(scanned!=-1) $fatal(1,"向量列数错误");
end
$fclose(fh);clear;
source_count=32'd1; groups=32'd2; group_id=32'd1; output_channel=32'd0; output_y=32'd0; output_x=32'd0; output_base_address=32'd19546112; output_length_bytes=32'd346112; output_channels=32'd32; output_height=32'd104; output_width=32'd104; source0_base_address=32'd18853888; source0_length_bytes=32'd692224; source0_channels=32'd64; source0_height=32'd104; source0_width=32'd104; source0_channel_start=32'd32; source0_channel_end=32'd64; source0_multiplier_q31=32'd2147483648; source1_base_address=32'd0; source1_length_bytes=32'd0; source1_channels=32'd0; source1_height=32'd0; source1_width=32'd0; source1_channel_start=32'd0; source1_channel_end=32'd0; source1_multiplier_q31=32'd0;source0_value=23;source1_value=-31;
for(integer c=0;c<32;c++) for(integer y=0;y<104;y++) for(integer x=0;x<104;x++) begin output_channel=32'(c);output_y=32'(y);output_x=32'(x);query_compare;end
source_count=32'd2; groups=32'd1; group_id=32'd0; output_channel=32'd0; output_y=32'd0; output_x=32'd0; output_base_address=32'd20584448; output_length_bytes=32'd692224; output_channels=32'd64; output_height=32'd104; output_width=32'd104; source0_base_address=32'd20238336; source0_length_bytes=32'd346112; source0_channels=32'd32; source0_height=32'd104; source0_width=32'd104; source0_channel_start=32'd0; source0_channel_end=32'd32; source0_multiplier_q31=32'd2147483648; source1_base_address=32'd19892224; source1_length_bytes=32'd346112; source1_channels=32'd32; source1_height=32'd104; source1_width=32'd104; source1_channel_start=32'd0; source1_channel_end=32'd32; source1_multiplier_q31=32'd1771485120;source0_value=23;source1_value=-31;
for(integer c=0;c<64;c++) for(integer y=0;y<104;y++) for(integer x=0;x<104;x++) begin output_channel=32'(c);output_y=32'(y);output_x=32'(x);query_compare;end
source_count=32'd2; groups=32'd1; group_id=32'd0; output_channel=32'd0; output_y=32'd0; output_x=32'd0; output_base_address=32'd21968896; output_length_bytes=32'd1384448; output_channels=32'd128; output_height=32'd104; output_width=32'd104; source0_base_address=32'd18853888; source0_length_bytes=32'd692224; source0_channels=32'd64; source0_height=32'd104; source0_width=32'd104; source0_channel_start=32'd0; source0_channel_end=32'd64; source0_multiplier_q31=32'd2147483648; source1_base_address=32'd21276672; source1_length_bytes=32'd692224; source1_channels=32'd64; source1_height=32'd104; source1_width=32'd104; source1_channel_start=32'd0; source1_channel_end=32'd64; source1_multiplier_q31=32'd1079448152;source0_value=23;source1_value=-31;
for(integer c=0;c<128;c++) for(integer y=0;y<104;y++) for(integer x=0;x<104;x++) begin output_channel=32'(c);output_y=32'(y);output_x=32'(x);query_compare;end
source_count=32'd1; groups=32'd2; group_id=32'd1; output_channel=32'd0; output_y=32'd0; output_x=32'd0; output_base_address=32'd24045568; output_length_bytes=32'd173056; output_channels=32'd64; output_height=32'd52; output_width=32'd52; source0_base_address=32'd23699456; source0_length_bytes=32'd346112; source0_channels=32'd128; source0_height=32'd52; source0_width=32'd52; source0_channel_start=32'd64; source0_channel_end=32'd128; source0_multiplier_q31=32'd2147483648; source1_base_address=32'd0; source1_length_bytes=32'd0; source1_channels=32'd0; source1_height=32'd0; source1_width=32'd0; source1_channel_start=32'd0; source1_channel_end=32'd0; source1_multiplier_q31=32'd0;source0_value=23;source1_value=-31;
for(integer c=0;c<64;c++) for(integer y=0;y<52;y++) for(integer x=0;x<52;x++) begin output_channel=32'(c);output_y=32'(y);output_x=32'(x);query_compare;end
source_count=32'd2; groups=32'd1; group_id=32'd0; output_channel=32'd0; output_y=32'd0; output_x=32'd0; output_base_address=32'd24564736; output_length_bytes=32'd346112; output_channels=32'd128; output_height=32'd52; output_width=32'd52; source0_base_address=32'd24391680; source0_length_bytes=32'd173056; source0_channels=32'd64; source0_height=32'd52; source0_width=32'd52; source0_channel_start=32'd0; source0_channel_end=32'd64; source0_multiplier_q31=32'd2147483648; source1_base_address=32'd24218624; source1_length_bytes=32'd173056; source1_channels=32'd64; source1_height=32'd52; source1_width=32'd52; source1_channel_start=32'd0; source1_channel_end=32'd64; source1_multiplier_q31=32'd1840756065;source0_value=23;source1_value=-31;
for(integer c=0;c<128;c++) for(integer y=0;y<52;y++) for(integer x=0;x<52;x++) begin output_channel=32'(c);output_y=32'(y);output_x=32'(x);query_compare;end
source_count=32'd2; groups=32'd1; group_id=32'd0; output_channel=32'd0; output_y=32'd0; output_x=32'd0; output_base_address=32'd25256960; output_length_bytes=32'd692224; output_channels=32'd256; output_height=32'd52; output_width=32'd52; source0_base_address=32'd23699456; source0_length_bytes=32'd346112; source0_channels=32'd128; source0_height=32'd52; source0_width=32'd52; source0_channel_start=32'd0; source0_channel_end=32'd128; source0_multiplier_q31=32'd1760973029; source1_base_address=32'd24910848; source1_length_bytes=32'd346112; source1_channels=32'd128; source1_height=32'd52; source1_width=32'd52; source1_channel_start=32'd0; source1_channel_end=32'd128; source1_multiplier_q31=32'd2147483648;source0_value=23;source1_value=-31;
for(integer c=0;c<256;c++) for(integer y=0;y<52;y++) for(integer x=0;x<52;x++) begin output_channel=32'(c);output_y=32'(y);output_x=32'(x);query_compare;end
source_count=32'd1; groups=32'd2; group_id=32'd1; output_channel=32'd0; output_y=32'd0; output_x=32'd0; output_base_address=32'd26295296; output_length_bytes=32'd86528; output_channels=32'd128; output_height=32'd26; output_width=32'd26; source0_base_address=32'd26122240; source0_length_bytes=32'd173056; source0_channels=32'd256; source0_height=32'd26; source0_width=32'd26; source0_channel_start=32'd128; source0_channel_end=32'd256; source0_multiplier_q31=32'd2147483648; source1_base_address=32'd0; source1_length_bytes=32'd0; source1_channels=32'd0; source1_height=32'd0; source1_width=32'd0; source1_channel_start=32'd0; source1_channel_end=32'd0; source1_multiplier_q31=32'd0;source0_value=23;source1_value=-31;
for(integer c=0;c<128;c++) for(integer y=0;y<26;y++) for(integer x=0;x<26;x++) begin output_channel=32'(c);output_y=32'(y);output_x=32'(x);query_compare;end
source_count=32'd2; groups=32'd1; group_id=32'd0; output_channel=32'd0; output_y=32'd0; output_x=32'd0; output_base_address=32'd26554880; output_length_bytes=32'd173056; output_channels=32'd256; output_height=32'd26; output_width=32'd26; source0_base_address=32'd26468352; source0_length_bytes=32'd86528; source0_channels=32'd128; source0_height=32'd26; source0_width=32'd26; source0_channel_start=32'd0; source0_channel_end=32'd128; source0_multiplier_q31=32'd1902693503; source1_base_address=32'd26381824; source1_length_bytes=32'd86528; source1_channels=32'd128; source1_height=32'd26; source1_width=32'd26; source1_channel_start=32'd0; source1_channel_end=32'd128; source1_multiplier_q31=32'd2147483648;source0_value=23;source1_value=-31;
for(integer c=0;c<256;c++) for(integer y=0;y<26;y++) for(integer x=0;x<26;x++) begin output_channel=32'(c);output_y=32'(y);output_x=32'(x);query_compare;end
source_count=32'd2; groups=32'd1; group_id=32'd0; output_channel=32'd0; output_y=32'd0; output_x=32'd0; output_base_address=32'd26900992; output_length_bytes=32'd346112; output_channels=32'd512; output_height=32'd26; output_width=32'd26; source0_base_address=32'd26122240; source0_length_bytes=32'd173056; source0_channels=32'd256; source0_height=32'd26; source0_width=32'd26; source0_channel_start=32'd0; source0_channel_end=32'd256; source0_multiplier_q31=32'd2147483648; source1_base_address=32'd26727936; source1_length_bytes=32'd173056; source1_channels=32'd256; source1_height=32'd26; source1_width=32'd26; source1_channel_start=32'd0; source1_channel_end=32'd256; source1_multiplier_q31=32'd1625315065;source0_value=23;source1_value=-31;
for(integer c=0;c<512;c++) for(integer y=0;y<26;y++) for(integer x=0;x<26;x++) begin output_channel=32'(c);output_y=32'(y);output_x=32'(x);query_compare;end
source_count=32'd1; groups=32'd1; group_id=32'd0; output_channel=32'd0; output_y=32'd0; output_x=32'd0; output_base_address=32'd27555072; output_length_bytes=32'd43264; output_channels=32'd256; output_height=32'd13; output_width=32'd13; source0_base_address=32'd27420160; source0_length_bytes=32'd43264; source0_channels=32'd256; source0_height=32'd13; source0_width=32'd13; source0_channel_start=32'd0; source0_channel_end=32'd256; source0_multiplier_q31=32'd2147483648; source1_base_address=32'd0; source1_length_bytes=32'd0; source1_channels=32'd0; source1_height=32'd0; source1_width=32'd0; source1_channel_start=32'd0; source1_channel_end=32'd0; source1_multiplier_q31=32'd0;source0_value=23;source1_value=-31;
for(integer c=0;c<256;c++) for(integer y=0;y<13;y++) for(integer x=0;x<13;x++) begin output_channel=32'(c);output_y=32'(y);output_x=32'(x);query_compare;end
source_count=32'd2; groups=32'd1; group_id=32'd0; output_channel=32'd0; output_y=32'd0; output_x=32'd0; output_base_address=32'd27706496; output_length_bytes=32'd259584; output_channels=32'd384; output_height=32'd26; output_width=32'd26; source0_base_address=32'd27619968; source0_length_bytes=32'd86528; source0_channels=32'd128; source0_height=32'd26; source0_width=32'd26; source0_channel_start=32'd0; source0_channel_end=32'd128; source0_multiplier_q31=32'd1959924335; source1_base_address=32'd26727936; source1_length_bytes=32'd173056; source1_channels=32'd256; source1_height=32'd26; source1_width=32'd26; source1_channel_start=32'd0; source1_channel_end=32'd256; source1_multiplier_q31=32'd2147483648;source0_value=23;source1_value=-31;
for(integer c=0;c<384;c++) for(integer y=0;y<26;y++) for(integer x=0;x<26;x++) begin output_channel=32'(c);output_y=32'(y);output_x=32'(x);query_compare;end
begin integer seed=722939921;integer r; for(integer n=0;n<50000;n++) begin
source_count=32'($unsigned($random(seed))%4);
groups=32'($unsigned($random(seed))%3);
group_id=$unsigned($random(seed));
output_channel=$unsigned($random(seed));
output_y=$unsigned($random(seed));
output_x=$unsigned($random(seed));
source0_base_address=$unsigned($random(seed));
source0_length_bytes=$unsigned($random(seed));
source0_channels=$unsigned($random(seed));
source0_height=$unsigned($random(seed));
source0_width=$unsigned($random(seed));
source0_channel_start=$unsigned($random(seed));
source0_channel_end=$unsigned($random(seed));
source0_multiplier_q31=$unsigned($random(seed));
source0_value=$unsigned($random(seed));
source1_base_address=$unsigned($random(seed));
source1_length_bytes=$unsigned($random(seed));
source1_channels=$unsigned($random(seed));
source1_height=$unsigned($random(seed));
source1_width=$unsigned($random(seed));
source1_channel_start=$unsigned($random(seed));
source1_channel_end=$unsigned($random(seed));
source1_multiplier_q31=$unsigned($random(seed));
source1_value=$unsigned($random(seed));
query_compare;end end
source_count=1;groups=3;group_id=1;source0_channels=6;source0_height=1;source0_width=1;source0_channel_start=2;source0_channel_end=4;source0_length_bytes=6;source0_base_address=0;source0_multiplier_q31=32'h80000000;output_channel=0;output_y=0;output_x=0;source0_value=23;#1;if(qo_error_code!=0||qn_error_code!=1)$fatal(1,"通用group3边界未明确");
if(abort_mask!=255||reset_mask!=255)$fatal(1,"取消状态覆盖缺失");
$display("PASS ROUTE_SPECIALIZATION cases=%0d queries=%0d cycles=%0d abort=%0d reset=%0d",cases,query_cases,cycles,abort_mask,reset_mask);$finish;end
endmodule

