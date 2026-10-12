`timescale 1ns/1ps
module tb_s2b_conv_validation;
logic clk=0; logic  hard_reset=0;
logic  abort=0;
logic  buffer_owner_pl=0;
logic  start_valid=0;
logic  start_ready=0;
logic [31:0] layer_index=0;
logic [31:0] weight_layer_index=0;
logic [31:0] input_base_address=0;
logic [31:0] input_length_bytes=0;
logic [31:0] input_batch_count=0;
logic [31:0] input_channels=0;
logic [31:0] input_height=0;
logic [31:0] input_width=0;
logic [31:0] output_base_address=0;
logic [31:0] output_length_bytes=0;
logic [31:0] output_batch_count=0;
logic [31:0] output_channels=0;
logic [31:0] output_height=0;
logic [31:0] output_width=0;
logic [31:0] kernel_height=0;
logic [31:0] kernel_width=0;
logic [31:0] stride_y=0;
logic [31:0] stride_x=0;
logic [31:0] pad_left=0;
logic [31:0] pad_right=0;
logic [31:0] pad_top=0;
logic [31:0] pad_bottom=0;
logic [31:0] groups=0;
logic signed [31:0] padding_value_int8=0;
logic [31:0] weight_package_base_address=0;
logic [31:0] weight_package_length_bytes=0;
logic [31:0] quantized_weight_offset=0;
logic [31:0] quantized_weight_bytes=0;
logic [31:0] output_batch=0;
logic [1:0] activation_mode=0;
logic  backend_cancel=0;
logic  backend_req_valid=0;
logic  backend_req_ready=0;
logic  backend_req_write=0;
logic [31:0] backend_req_addr=0;
logic [31:0] backend_req_wdata=0;
logic [3:0] backend_req_rstrb=0;
logic [3:0] backend_req_wstrb=0;
logic  backend_rsp_valid=0;
logic [31:0] backend_rsp_rdata=0;
logic [2:0] backend_rsp_error=0;
logic  busy=0;
logic  result_valid=0;
logic  result_ready=0;
logic [2:0] result_error_code=0;
s2a_conv_tile_engine u_dut (.clk(clk),.hard_reset(hard_reset),.abort(abort),.buffer_owner_pl(buffer_owner_pl),.start_valid(start_valid),.start_ready(start_ready),.layer_index(layer_index),.weight_layer_index(weight_layer_index),.input_base_address(input_base_address),.input_length_bytes(input_length_bytes),.input_batch_count(input_batch_count),.input_channels(input_channels),.input_height(input_height),.input_width(input_width),.output_base_address(output_base_address),.output_length_bytes(output_length_bytes),.output_batch_count(output_batch_count),.output_channels(output_channels),.output_height(output_height),.output_width(output_width),.kernel_height(kernel_height),.kernel_width(kernel_width),.stride_y(stride_y),.stride_x(stride_x),.pad_left(pad_left),.pad_right(pad_right),.pad_top(pad_top),.pad_bottom(pad_bottom),.groups(groups),.padding_value_int8(padding_value_int8),.weight_package_base_address(weight_package_base_address),.weight_package_length_bytes(weight_package_length_bytes),.quantized_weight_offset(quantized_weight_offset),.quantized_weight_bytes(quantized_weight_bytes),.output_batch(output_batch),.activation_mode(activation_mode),.backend_cancel(backend_cancel),.backend_req_valid(backend_req_valid),.backend_req_ready(backend_req_ready),.backend_req_write(backend_req_write),.backend_req_addr(backend_req_addr),.backend_req_wdata(backend_req_wdata),.backend_req_rstrb(backend_req_rstrb),.backend_req_wstrb(backend_req_wstrb),.backend_rsp_valid(backend_rsp_valid),.backend_rsp_rdata(backend_rsp_rdata),.backend_rsp_error(backend_rsp_error),.busy(busy),.result_valid(result_valid),.result_ready(result_ready),.result_error_code(result_error_code));
logic  candidate_start_ready;
logic  candidate_backend_cancel;
logic  candidate_backend_req_valid;
logic  candidate_backend_req_write;
logic [31:0] candidate_backend_req_addr;
logic [31:0] candidate_backend_req_wdata;
logic [3:0] candidate_backend_req_rstrb;
logic [3:0] candidate_backend_req_wstrb;
logic  candidate_busy;
logic  candidate_result_valid;
logic [2:0] candidate_result_error_code;
s2b_conv_tile_engine u_candidate (.clk(clk),.hard_reset(hard_reset),.abort(abort),.buffer_owner_pl(buffer_owner_pl),.start_valid(start_valid),.start_ready(candidate_start_ready),.layer_index(layer_index),.weight_layer_index(weight_layer_index),.input_base_address(input_base_address),.input_length_bytes(input_length_bytes),.input_batch_count(input_batch_count),.input_channels(input_channels),.input_height(input_height),.input_width(input_width),.output_base_address(output_base_address),.output_length_bytes(output_length_bytes),.output_batch_count(output_batch_count),.output_channels(output_channels),.output_height(output_height),.output_width(output_width),.kernel_height(kernel_height),.kernel_width(kernel_width),.stride_y(stride_y),.stride_x(stride_x),.pad_left(pad_left),.pad_right(pad_right),.pad_top(pad_top),.pad_bottom(pad_bottom),.groups(groups),.padding_value_int8(padding_value_int8),.weight_package_base_address(weight_package_base_address),.weight_package_length_bytes(weight_package_length_bytes),.quantized_weight_offset(quantized_weight_offset),.quantized_weight_bytes(quantized_weight_bytes),.output_batch(output_batch),.activation_mode(activation_mode),.backend_cancel(candidate_backend_cancel),.backend_req_valid(candidate_backend_req_valid),.backend_req_ready(backend_req_ready),.backend_req_write(candidate_backend_req_write),.backend_req_addr(candidate_backend_req_addr),.backend_req_wdata(candidate_backend_req_wdata),.backend_req_rstrb(candidate_backend_req_rstrb),.backend_req_wstrb(candidate_backend_req_wstrb),.backend_rsp_valid(backend_rsp_valid),.backend_rsp_rdata(backend_rsp_rdata),.backend_rsp_error(backend_rsp_error),.busy(candidate_busy),.result_valid(candidate_result_valid),.result_ready(result_ready),.result_error_code(candidate_result_error_code));
integer compare_cycles=0; always @(negedge clk) begin if ((start_ready !== candidate_start_ready) || (backend_cancel !== candidate_backend_cancel) || (backend_req_valid !== candidate_backend_req_valid) || (backend_req_write !== candidate_backend_req_write) || (backend_req_addr !== candidate_backend_req_addr) || (backend_req_wdata !== candidate_backend_req_wdata) || (backend_req_rstrb !== candidate_backend_req_rstrb) || (backend_req_wstrb !== candidate_backend_req_wstrb) || (busy !== candidate_busy) || (result_valid !== candidate_result_valid) || (result_error_code !== candidate_result_error_code)) $fatal(1,"CONV公开输出逐周期不同 cycle=%0d",compare_cycles); compare_cycles++; end

integer cycles=0,cases=0,pending=0,delay_count=0,requests=0,error_code=0,error_request=0,raw_invalid=0;
integer abort_mask=0,reset_mask=0,fd,scanned,expected_error,timeout_count;
always #5 clk=~clk;
task automatic tick; begin @(posedge clk); #1; cycles++; @(negedge clk); #1; end endtask
task automatic reset_dut; begin hard_reset=1; abort=0; start_valid=0; result_ready=0; backend_rsp_valid=0; backend_req_ready=0; pending=0; tick; hard_reset=0; tick; end endtask
task automatic defaults; begin layer_index=32'h0; weight_layer_index=32'h0; input_base_address=32'h0; input_length_bytes=32'h30; input_batch_count=32'h1; input_channels=32'h3; input_height=32'h4; input_width=32'h4; output_base_address=32'h1000000; output_length_bytes=32'h80; output_batch_count=32'h1; output_channels=32'h20; output_height=32'h2; output_width=32'h2; kernel_height=32'h3; kernel_width=32'h3; stride_y=32'h1; stride_x=32'h1; pad_left=32'h0; pad_right=32'h0; pad_top=32'h0; pad_bottom=32'h0; groups=32'h1; padding_value_int8=32'h0; weight_package_base_address=32'h100000; weight_package_length_bytes=32'h5a12fc; quantized_weight_offset=32'h13c; quantized_weight_bytes=32'h360; output_batch=32'h0; activation_mode=32'h1; buffer_owner_pl=1; end endtask
task automatic start_dut; begin start_valid=1; tick; start_valid=0; end endtask
task automatic service;
logic accepted,responded;
begin
 backend_req_ready=(cycles%5)!=0; backend_rsp_valid=pending!=0 && delay_count==0;
 backend_rsp_rdata=raw_invalid!=0?32'h80808080:0; backend_rsp_error=(requests==error_request)?3'(error_code):0;
 #1; accepted=backend_req_valid && backend_req_ready; responded=backend_rsp_valid;
 tick;
 if(responded)pending=0; else if(pending!=0 && delay_count>0)delay_count--;
 if(accepted)begin if(pending!=0)$fatal(1,"重复请求"); requests++;pending=1;delay_count=cycles%4;end
end endtask
initial begin
 reset_dut;
 fd=$fopen("validation_vectors.txt","r"); if(fd==0)$fatal(1,"向量文件缺失");
 while(!$feof(fd))begin
  scanned=$fscanf(fd,"%h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h\n",layer_index,weight_layer_index,input_base_address,input_length_bytes,input_batch_count,input_channels,input_height,input_width,output_base_address,output_length_bytes,output_batch_count,output_channels,output_height,output_width,kernel_height,kernel_width,stride_y,stride_x,pad_left,pad_right,pad_top,pad_bottom,groups,padding_value_int8,weight_package_base_address,weight_package_length_bytes,quantized_weight_offset,quantized_weight_bytes,output_batch,activation_mode,buffer_owner_pl,expected_error);
  if(scanned!=32)begin if(!$feof(fd))$fatal(1,"向量读取失败");break;end
  start_dut; tick;
  if(expected_error==0)begin if(result_valid)$fatal(1,"合法层校验被拒绝 case=%0d",cases); abort=1;tick;abort=0;end
  else begin if(!result_valid || result_error_code!=expected_error)$fatal(1,"独立校验黄金不同 case=%0d want=%0d got=%0d",cases,expected_error,result_error_code); result_ready=1;tick;result_ready=0;end
  cases++;reset_dut;
 end
 $fclose(fd);
 for(integer action=0;action<2;action++)begin
  for(integer state_id=0;state_id<20;state_id++)begin
   reset_dut;defaults;requests=0;error_code=0;error_request=0;if(state_id!=0)start_dut;timeout_count=0;
   while(int'(u_dut.state)!=state_id && timeout_count<20000)begin service;timeout_count++;end
   if(timeout_count==20000)$fatal(1,"状态不可达state=%0d",state_id);
   if(action==0)begin abort=1;abort_mask|=1<<state_id;end else begin hard_reset=1;reset_mask|=1<<state_id;end
   service; abort=0;hard_reset=0;pending=0;backend_rsp_valid=0;tick;
   if(busy || result_valid || !start_ready)$fatal(1,"复位abort未回IDLE");
  end
 end
 for(integer code=0;code<8;code++)begin
  for(integer request_target=1;request_target<=3;request_target++)begin
   reset_dut;defaults;requests=0;error_code=code;error_request=(request_target==1?1:request_target==2?49:265);start_dut;
   timeout_count=0;while(!result_valid && timeout_count<20000)begin
    // owner低不取消已接受合法任务；输入batch改变不能改变锁存状态。
    if(timeout_count>2)begin buffer_owner_pl=0;input_batch_count=32'hffffffff;output_batch_count=0;end
    service;timeout_count++;
   end
   if(!result_valid)$fatal(1,"响应错误或成功超时code=%0d target=%0d",code,request_target);
   expected_error=(code==0?0:code==1?1:code==2?2:6);
   if(result_error_code!=expected_error)$fatal(1,"响应映射不同code=%0d target=%0d got=%0d",code,request_target,result_error_code);
   repeat(7)service;result_ready=1;service;result_ready=0;
  end
 end
 reset_dut;defaults;requests=0;error_code=0;error_request=0;raw_invalid=1;start_dut;timeout_count=0;
 while(!result_valid && timeout_count<20000)begin service;timeout_count++;end
 if(!result_valid || result_error_code!=1)$fatal(1,"raw80拒绝语义不同");

 raw_invalid=0;result_ready=1;service;result_ready=0;
 for(integer job=0;job<2;job++)begin
  defaults;requests=0;error_code=0;error_request=0;pending=0;backend_rsp_valid=0;
  input_channels=1;input_height=(job==0?9:19);input_width=input_height;
  input_length_bytes=input_height*input_width;output_channels=32;output_height=(job==0?9:11);output_width=output_height;
  output_length_bytes=32*output_height*output_width;kernel_height=1;kernel_width=1;
  stride_y=(job==0?1:2);stride_x=stride_y;pad_top=job;pad_bottom=job;pad_left=job;pad_right=job;
  quantized_weight_bytes=32;start_dut;timeout_count=0;
  while(!result_valid && timeout_count<100000)begin service;timeout_count++;end
  if(!result_valid || result_error_code!=0)$fatal(1,"公开多tile/newSTART轨迹失败job=%0d state=%0d result=%0d code=%0d",job,u_dut.state,result_valid,result_error_code);
  $display("S13_PUBLIC_TRACE job=%0d requests=%0d cycles=%0d preps=%0d",job,requests,timeout_count,origin_preps);
  result_ready=1;service;result_ready=0;
 end
 if(origin_preps<8 || origin_x_tiles<2 || origin_y_tiles<2 || origin_clears<40)$fatal(1,"顺序origin覆盖不足");
 if(tap_samples==0)$fatal(1,"顺序tap覆盖缺失");
 $display("PASS S13_TAP_REGRESSION samples=%0d",tap_samples);
 $display("PASS S13_ORIGIN_INVARIANTS preps=%0d x_tiles=%0d y_tiles=%0d clears=%0d",origin_preps,origin_x_tiles,origin_y_tiles,origin_clears);
 $display("PASS CONV_VALIDATION vectors=%0d cycles=%0d abort_mask=%x reset_mask=%x response_cases=24 raw80=1",cases,cycles,abort_mask,reset_mask);
 $finish;
end

integer origin_preps=0,origin_x_tiles=0,origin_y_tiles=0,origin_clears=0;
logic [63:0] expected_origin_y,expected_origin_x;
logic check_origin_prep,check_origin_clear;
always @(posedge clk) begin
 check_origin_clear=hard_reset || abort || (u_candidate.state==u_candidate.ST_IDLE && start_valid && start_ready);
 check_origin_prep=!hard_reset && !abort && u_candidate.state==u_candidate.ST_TILE_PREP;
 expected_origin_y=64'(u_candidate.tile_start_y)*64'(u_candidate.stride_y_latched)-64'(u_candidate.pad_top_latched);
 expected_origin_x=64'(u_candidate.tile_start_x)*64'(u_candidate.stride_x_latched)-64'(u_candidate.pad_left_latched);
 #1;
 if(check_origin_clear)begin
  if(u_candidate.tile_origin_y!==64'd0 || u_candidate.tile_origin_x!==64'd0)$fatal(1,"origin复位/abort/START清零失败");
  origin_clears++;
 end else if(check_origin_prep)begin
  if(u_candidate.tile_origin_y!==expected_origin_y || u_candidate.tile_origin_x!==expected_origin_x)$fatal(1,"PRE原点登记失败");
  origin_preps++;if(u_candidate.tile_start_x!=0)origin_x_tiles++;if(u_candidate.tile_start_y!=0)origin_y_tiles++;
 end
end
always @(negedge clk)begin
 if(!hard_reset && !abort && (u_candidate.state==u_candidate.ST_FEATURE_SCAN || u_candidate.state==u_candidate.ST_FEATURE_REQUEST || u_candidate.state==u_candidate.ST_FEATURE_RESPONSE))begin
  if(u_candidate.tile_origin_y!==(64'(u_candidate.tile_start_y)*64'(u_candidate.stride_y_latched)-64'(u_candidate.pad_top_latched)) || u_candidate.tile_origin_x!==(64'(u_candidate.tile_start_x)*64'(u_candidate.stride_x_latched)-64'(u_candidate.pad_left_latched)))$fatal(1,"特征消费拍origin不变量失败");
 end
end

integer tap_samples=0;
always @(negedge clk)begin
 if(!hard_reset && !abort && u_dut.compute_read_enable)begin
  if(!u_candidate.compute_read_enable || u_dut.compute_read_tap_in_bounds!==u_candidate.compute_read_tap_in_bounds || u_dut.compute_read_feature_index_wide!==u_candidate.compute_read_feature_index_wide)$fatal(1,"真实顺序tap坐标/索引差分失败");
  tap_samples++;
 end
end

endmodule
