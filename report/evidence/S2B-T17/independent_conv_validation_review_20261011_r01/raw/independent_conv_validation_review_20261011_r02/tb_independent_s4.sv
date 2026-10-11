`timescale 1ns/1ps
module tb_independent_s4;
logic clk=0;
logic  hard_reset=0;
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
logic  new_start_ready;
logic  new_backend_cancel;
logic  new_backend_req_valid;
logic  new_backend_req_write;
logic [31:0] new_backend_req_addr;
logic [31:0] new_backend_req_wdata;
logic [3:0] new_backend_req_rstrb;
logic [3:0] new_backend_req_wstrb;
logic  new_busy;
logic  new_result_valid;
logic [2:0] new_result_error_code;
s2a_conv_tile_engine old(.clk(clk),.hard_reset(hard_reset),.abort(abort),.buffer_owner_pl(buffer_owner_pl),.start_valid(start_valid),.start_ready(start_ready),.layer_index(layer_index),.weight_layer_index(weight_layer_index),.input_base_address(input_base_address),.input_length_bytes(input_length_bytes),.input_batch_count(input_batch_count),.input_channels(input_channels),.input_height(input_height),.input_width(input_width),.output_base_address(output_base_address),.output_length_bytes(output_length_bytes),.output_batch_count(output_batch_count),.output_channels(output_channels),.output_height(output_height),.output_width(output_width),.kernel_height(kernel_height),.kernel_width(kernel_width),.stride_y(stride_y),.stride_x(stride_x),.pad_left(pad_left),.pad_right(pad_right),.pad_top(pad_top),.pad_bottom(pad_bottom),.groups(groups),.padding_value_int8(padding_value_int8),.weight_package_base_address(weight_package_base_address),.weight_package_length_bytes(weight_package_length_bytes),.quantized_weight_offset(quantized_weight_offset),.quantized_weight_bytes(quantized_weight_bytes),.output_batch(output_batch),.activation_mode(activation_mode),.backend_cancel(backend_cancel),.backend_req_valid(backend_req_valid),.backend_req_ready(backend_req_ready),.backend_req_write(backend_req_write),.backend_req_addr(backend_req_addr),.backend_req_wdata(backend_req_wdata),.backend_req_rstrb(backend_req_rstrb),.backend_req_wstrb(backend_req_wstrb),.backend_rsp_valid(backend_rsp_valid),.backend_rsp_rdata(backend_rsp_rdata),.backend_rsp_error(backend_rsp_error),.busy(busy),.result_valid(result_valid),.result_ready(result_ready),.result_error_code(result_error_code));
s2b_conv_tile_engine candidate(.clk(clk),.hard_reset(hard_reset),.abort(abort),.buffer_owner_pl(buffer_owner_pl),.start_valid(start_valid),.start_ready(new_start_ready),.layer_index(layer_index),.weight_layer_index(weight_layer_index),.input_base_address(input_base_address),.input_length_bytes(input_length_bytes),.input_batch_count(input_batch_count),.input_channels(input_channels),.input_height(input_height),.input_width(input_width),.output_base_address(output_base_address),.output_length_bytes(output_length_bytes),.output_batch_count(output_batch_count),.output_channels(output_channels),.output_height(output_height),.output_width(output_width),.kernel_height(kernel_height),.kernel_width(kernel_width),.stride_y(stride_y),.stride_x(stride_x),.pad_left(pad_left),.pad_right(pad_right),.pad_top(pad_top),.pad_bottom(pad_bottom),.groups(groups),.padding_value_int8(padding_value_int8),.weight_package_base_address(weight_package_base_address),.weight_package_length_bytes(weight_package_length_bytes),.quantized_weight_offset(quantized_weight_offset),.quantized_weight_bytes(quantized_weight_bytes),.output_batch(output_batch),.activation_mode(activation_mode),.backend_cancel(new_backend_cancel),.backend_req_valid(new_backend_req_valid),.backend_req_ready(backend_req_ready),.backend_req_write(new_backend_req_write),.backend_req_addr(new_backend_req_addr),.backend_req_wdata(new_backend_req_wdata),.backend_req_rstrb(new_backend_req_rstrb),.backend_req_wstrb(new_backend_req_wstrb),.backend_rsp_valid(backend_rsp_valid),.backend_rsp_rdata(backend_rsp_rdata),.backend_rsp_error(backend_rsp_error),.busy(new_busy),.result_valid(new_result_valid),.result_ready(result_ready),.result_error_code(new_result_error_code));
integer ticks=0,checked=0,hand_count=0,pending=0,delay_left=0,requests=0,writes=0;
integer inject_class=-1,inject_error=0,inject_raw=0,abort_mask=0,reset_mask=0,error_cases=0;
logic [31:0] response_word=0;
logic [2:0] response_error=0;
logic [511:0] seen=0;
localparam logic [7:0] golden[0:511]='{8'hff,8'hff,8'hff,8'hfe,8'hfe,8'hfe,8'hfe,8'hfd,8'hfd,8'hfd,8'hfd,8'hfc,8'hfc,8'hfc,8'hfc,8'hff,8'h21,8'h1d,8'h1a,8'h16,8'h13,8'h0f,8'h0b,8'h08,8'h04,8'h00,8'h00,8'hff,8'hff,8'hff,8'hfe,8'h21,8'h0a,8'h08,8'h07,8'h06,8'h04,8'h03,8'h01,8'h00,8'h00,8'h00,8'h00,8'hff,8'hff,8'hff,8'hff,8'h0a,8'h14,8'h11,8'h0e,8'h0c,8'h09,8'h07,8'h04,8'h01,8'h00,8'h00,8'hff,8'hff,8'hff,8'hff,8'hfe,8'h14,8'h0e,8'h0b,8'h09,8'h07,8'h04,8'h02,8'h00,8'h00,8'h00,8'hff,8'hff,8'hff,8'hff,8'hfe,8'hfe,8'h0e,8'h06,8'h05,8'h05,8'h04,8'h04,8'h04,8'h03,8'h03,8'h02,8'h02,8'h01,8'h01,8'h00,8'h00,8'h00,8'h06,8'h07,8'h06,8'h05,8'h05,8'h04,8'h04,8'h03,8'h03,8'h02,8'h02,8'h01,8'h01,8'h00,8'h00,8'h00,8'h07,8'h0b,8'h0a,8'h09,8'h09,8'h08,8'h07,8'h07,8'h06,8'h06,8'h05,8'h04,8'h04,8'h03,8'h02,8'h02,8'h0b,8'h07,8'h06,8'h05,8'h04,8'h02,8'h01,8'h00,8'h00,8'h00,8'h00,8'h00,8'hff,8'hff,8'hff,8'hff,8'h07,8'h05,8'h04,8'h04,8'h04,8'h04,8'h04,8'h03,8'h03,8'h03,8'h03,8'h03,8'h02,8'h02,8'h02,8'h02,8'h05,8'h07,8'h07,8'h07,8'h07,8'h07,8'h07,8'h07,8'h07,8'h07,8'h07,8'h07,8'h07,8'h07,8'h08,8'h08,8'h07,8'h00,8'h00,8'h00,8'h00,8'h00,8'h00,8'h00,8'h00,8'h01,8'h01,8'h01,8'h02,8'h02,8'h03,8'h03,8'h00,8'hff,8'hff,8'hff,8'h00,8'h00,8'h00,8'h00,8'h00,8'h01,8'h01,8'h02,8'h03,8'h04,8'h05,8'h06,8'hff,8'h00,8'h01,8'h01,8'h02,8'h03,8'h04,8'h05,8'h06,8'h07,8'h08,8'h09,8'h09,8'h0a,8'h0b,8'h0c,8'h00,8'hfd,8'hfd,8'hfd,8'hfd,8'hfd,8'hfd,8'hfd,8'hfd,8'hfd,8'hfd,8'hfe,8'hfe,8'hfe,8'hfe,8'hfe,8'hfd,8'hfe,8'hfe,8'hfe,8'hff,8'hff,8'hff,8'hff,8'h00,8'h00,8'h03,8'h06,8'h09,8'h0c,8'h0f,8'h12,8'hfe,8'hff,8'hff,8'hff,8'h00,8'h00,8'h00,8'h01,8'h02,8'h04,8'h05,8'h07,8'h08,8'h0a,8'h0b,8'h0d,8'hff,8'h00,8'h00,8'h01,8'h02,8'h03,8'h04,8'h04,8'h05,8'h06,8'h07,8'h08,8'h09,8'h0a,8'h0a,8'h0b,8'h00,8'hfe,8'hfe,8'hfe,8'hff,8'hff,8'h00,8'h00,8'h02,8'h06,8'h09,8'h0d,8'h10,8'h13,8'h17,8'h1a,8'hfe,8'hfe,8'hfe,8'hff,8'hff,8'hff,8'hff,8'h00,8'h01,8'h04,8'h07,8'h0a,8'h0d,8'h10,8'h12,8'h15,8'hfe,8'h06,8'h06,8'h06,8'h06,8'h06,8'h06,8'h05,8'h05,8'h05,8'h05,8'h05,8'h05,8'h05,8'h05,8'h05,8'h06,8'h15,8'h11,8'h0e,8'h0b,8'h07,8'h04,8'h01,8'h00,8'hff,8'hff,8'hff,8'hfe,8'hfe,8'hfe,8'hfd,8'h15,8'h0f,8'h0d,8'h0c,8'h0a,8'h09,8'h07,8'h06,8'h04,8'h03,8'h01,8'h00,8'h00,8'h00,8'h00,8'hff,8'h0f,8'h14,8'h11,8'h0f,8'h0d,8'h0a,8'h08,8'h06,8'h03,8'h01,8'h00,8'h00,8'hff,8'hff,8'hff,8'hff,8'h14,8'h18,8'h15,8'h12,8'h0f,8'h0b,8'h08,8'h05,8'h02,8'h00,8'h00,8'hff,8'hff,8'hff,8'hfe,8'hfe,8'h18,8'h0d,8'h0b,8'h0a,8'h08,8'h07,8'h06,8'h04,8'h03,8'h01,8'h00,8'h00,8'h00,8'h00,8'hff,8'hff,8'h0d,8'h05,8'h04,8'h04,8'h04,8'h03,8'h03,8'h03,8'h02,8'h02,8'h01,8'h01,8'h01,8'h00,8'h00,8'h00,8'h05,8'h07,8'h06,8'h05,8'h05,8'h04,8'h03,8'h02,8'h01,8'h00,8'h00,8'h00,8'h00,8'h00,8'h00,8'hff,8'h07,8'h09,8'h08,8'h08,8'h08,8'h08,8'h08,8'h07,8'h07,8'h07,8'h07,8'h06,8'h06,8'h06,8'h06,8'h05,8'h09,8'h01,8'h01,8'h01,8'h01,8'h01,8'h01,8'h01,8'h01,8'h01,8'h01,8'h00,8'h00,8'h00,8'h00,8'h00,8'h01,8'h00,8'h00,8'h00,8'h00,8'h00,8'h00,8'h01,8'h01,8'h01,8'h01,8'h01,8'h01,8'h01,8'h01,8'h01,8'h00,8'h05,8'h05,8'h05,8'h06,8'h06,8'h06,8'h06,8'h06,8'h07,8'h07,8'h07,8'h07,8'h08,8'h08,8'h08,8'h05};
always #5 clk=~clk;
always @(negedge clk) begin
 if(start_ready !== new_start_ready || backend_cancel !== new_backend_cancel || backend_req_valid !== new_backend_req_valid || backend_req_write !== new_backend_req_write || backend_req_addr !== new_backend_req_addr || backend_req_wdata !== new_backend_req_wdata || backend_req_rstrb !== new_backend_req_rstrb || backend_req_wstrb !== new_backend_req_wstrb || busy !== new_busy || result_valid !== new_result_valid || result_error_code !== new_result_error_code) $fatal(1,"独立原新公开口比较失败tick=%0d",ticks);
 checked++;
end
task automatic tick;begin @(posedge clk);#1;ticks++;@(negedge clk);#1;end endtask
task automatic defaults;begin buffer_owner_pl=32'h1; layer_index=32'h0; weight_layer_index=32'h0; input_base_address=32'h1003; input_length_bytes=32'h10; input_batch_count=32'h1; input_channels=32'h1; input_height=32'h4; input_width=32'h4; output_base_address=32'h3001; output_length_bytes=32'h200; output_batch_count=32'h1; output_channels=32'h20; output_height=32'h4; output_width=32'h4; kernel_height=32'h1; kernel_width=32'h1; stride_y=32'h1; stride_x=32'h1; pad_left=32'h0; pad_right=32'h0; pad_top=32'h0; pad_bottom=32'h0; groups=32'h1; padding_value_int8=32'h0; weight_package_base_address=32'h2001; weight_package_length_bytes=32'h80; quantized_weight_offset=32'h4; quantized_weight_bytes=32'h20; output_batch=32'h0; activation_mode=32'h1; end endtask
task automatic reset_all;begin
 hard_reset=1;abort=0;start_valid=0;result_ready=0;backend_req_ready=0;backend_rsp_valid=0;backend_rsp_error=0;
 pending=0;delay_left=0;requests=0;writes=0;seen=0;inject_class=-1;inject_error=0;inject_raw=0;tick;hard_reset=0;tick;
end endtask
task automatic launch;begin start_valid=1;tick;start_valid=0;end endtask
task automatic validate_case(input integer expected);begin
 launch;tick;
 if(expected!=0)begin
  if(!result_valid || result_error_code!=expected || backend_req_valid)$fatal(1,"手算校验失败n=%0d want=%0d got=%0d",hand_count,expected,result_error_code);
  repeat(3)begin tick;if(!result_valid || result_error_code!=expected)$fatal(1,"错误结果不保持");end
  result_ready=1;tick;result_ready=0;
 end else begin if(result_valid)$fatal(1,"手算合法拒绝n=%0d error=%0d",hand_count,result_error_code);abort=1;tick;abort=0;end
 hand_count++;
end endtask
task automatic service;
logic accepted,responded;logic[31:0] req_addr,req_data;logic[3:0] rsel,wsel;logic wr;
integer address,index,category,bytevalue;
begin
 backend_req_ready=(ticks%7)!=1 && (ticks%7)!=2;
 backend_rsp_valid=pending!=0 && delay_left==0;
 backend_rsp_rdata=response_word;backend_rsp_error=response_error;
 #1;accepted=backend_req_valid && backend_req_ready;responded=backend_rsp_valid;
 req_addr=backend_req_addr;req_data=backend_req_wdata;rsel=backend_req_rstrb;wsel=backend_req_wstrb;wr=backend_req_write;
 tick;
 if(responded)pending=0;else if(pending!=0 && delay_left>0)delay_left--;
 if(accepted)begin
  if(pending!=0)$fatal(1,"独立服务多pending");
  requests++;pending=1;delay_left=ticks%4;response_word=0;response_error=0;
  if(wr)begin
   if(rsel!=0 || $countones(wsel)!=1)$fatal(1,"写strobe错误");
   category=2;
   for(integer lane=0;lane<4;lane++)if(wsel[lane])begin
    address=int'(req_addr)+lane;index=address-32'h3001;
    if(index<0 || index>=512)$fatal(1,"输出地址范围错误");
    if(seen[index])$fatal(1,"输出地址重复");
    if(req_data[lane*8+:8]!==golden[index])$fatal(1,"独立D2数学输出错idx=%0d expected=%0d got=%0d",index,golden[index],req_data[lane*8+:8]);
    seen[index]=1;writes++;
   end
  end else begin
   if(wsel!=0 || $countones(rsel)!=1)$fatal(1,"读strobe错误");
   category=-1;
   for(integer lane=0;lane<4;lane++)if(rsel[lane])begin
    address=int'(req_addr)+lane;
    if(address>=32'h1003 && address<32'h1013)begin category=0;index=address-32'h1003;bytevalue=(index*17)%255-127;end
    else if(address>=32'h2005 && address<32'h2025)begin category=1;index=address-32'h2005;bytevalue=(index*13)%255-127;end
    else $fatal(1,"独立读地址错误addr=%x",address);
    response_word[lane*8+:8]=inject_raw!=0 ? 8'h80 : 8'(bytevalue);
   end
  end
  if(category==inject_class)response_error=3'(inject_error);
 end
end endtask
task automatic run_result(input integer expected);
integer watchdog;
begin
 launch;tick;
 // 已通过VALIDATE后改变公开描述符与owner，内部锁存必须保持。
 input_batch_count=32'hffffffff;output_batch_count=0;input_base_address=0;output_base_address=0;buffer_owner_pl=0;
 watchdog=0;
 while(!result_valid && watchdog<20000)begin service;watchdog++;end
 if(!result_valid || result_error_code!=expected)$fatal(1,"独立结果错误want=%0d got=%0d",expected,result_error_code);
 if(expected==0 && (writes!=512 || seen!={512{1'b1}} || pending!=0))$fatal(1,"输出覆盖不全writes=%0d",writes);
 repeat(5)begin service;if(!result_valid || result_error_code!=expected)$fatal(1,"背压结果未保持");end
 result_ready=1;service;result_ready=0;
 if(busy || result_valid || !start_ready)$fatal(1,"结果ACK不回IDLE");
end endtask
initial begin
 reset_all; defaults;  validate_case(0);
reset_all; defaults; input_batch_count=32'h0; validate_case(1);
reset_all; defaults; input_length_bytes=32'h0; input_batch_count=32'h0; validate_case(1);
reset_all; defaults; weight_layer_index=32'h1; input_batch_count=32'h0; validate_case(2);
reset_all; defaults; input_batch_count=32'h2; validate_case(1);
reset_all; defaults; input_length_bytes=32'h0; input_batch_count=32'h2; validate_case(1);
reset_all; defaults; weight_layer_index=32'h1; input_batch_count=32'h2; validate_case(2);
reset_all; defaults; input_batch_count=32'hffffffff; validate_case(1);
reset_all; defaults; input_length_bytes=32'h0; input_batch_count=32'hffffffff; validate_case(1);
reset_all; defaults; weight_layer_index=32'h1; input_batch_count=32'hffffffff; validate_case(2);
reset_all; defaults; output_batch_count=32'h0; validate_case(1);
reset_all; defaults; input_length_bytes=32'h0; output_batch_count=32'h0; validate_case(1);
reset_all; defaults; weight_layer_index=32'h1; output_batch_count=32'h0; validate_case(2);
reset_all; defaults; output_batch_count=32'h2; validate_case(1);
reset_all; defaults; input_length_bytes=32'h0; output_batch_count=32'h2; validate_case(1);
reset_all; defaults; weight_layer_index=32'h1; output_batch_count=32'h2; validate_case(2);
reset_all; defaults; output_batch_count=32'hffffffff; validate_case(1);
reset_all; defaults; input_length_bytes=32'h0; output_batch_count=32'hffffffff; validate_case(1);
reset_all; defaults; weight_layer_index=32'h1; output_batch_count=32'hffffffff; validate_case(2);
reset_all; defaults; input_base_address=32'hffffffef; validate_case(0);
reset_all; defaults; input_base_address=32'hfffffff0; validate_case(0);
reset_all; defaults; input_base_address=32'hfffffff1; validate_case(2);
reset_all; defaults; output_base_address=32'hfffffdff; validate_case(0);
reset_all; defaults; output_base_address=32'hfffffe00; validate_case(0);
reset_all; defaults; output_base_address=32'hfffffe01; validate_case(2);
reset_all; defaults; weight_package_base_address=32'hffffff7f; validate_case(0);
reset_all; defaults; weight_package_base_address=32'hffffff80; validate_case(0);
reset_all; defaults; weight_package_base_address=32'hffffff81; validate_case(2);
reset_all; defaults; input_length_bytes=32'h0; input_height=32'h10000; input_width=32'h10000; validate_case(3);
reset_all; defaults; output_length_bytes=32'h0; output_height=32'h10000; output_width=32'h10000; validate_case(3);
reset_all; defaults; input_length_bytes=32'h1; input_height=32'hffffffff; input_width=32'hffffffff; validate_case(3);
reset_all; defaults; output_length_bytes=32'h20; output_height=32'hffffffff; output_width=32'hffffffff; validate_case(3);
reset_all; defaults; input_length_bytes=32'h0; input_batch_count=32'h0; input_height=32'hffffffff; input_width=32'hffffffff; validate_case(1);
reset_all; defaults; buffer_owner_pl=32'h0; validate_case(1);
reset_all; defaults; output_batch=32'h1; validate_case(1);
reset_all; defaults; output_length_bytes=32'h1f0; output_channels=32'h1f; quantized_weight_bytes=32'h1f; validate_case(2);
 reset_all;defaults;run_result(0);
 $display("PASS_SYNTHETIC bytes=512 requests=%0d nonzero_data=1 descriptor_poison=1 owner_drop=1",requests);
 for(integer cls=0;cls<3;cls++)for(integer code=1;code<8;code++)begin
  reset_all;defaults;inject_class=cls;inject_error=code;run_result(code==1?1:code==2?2:6);error_cases++;
 end
 reset_all;defaults;inject_raw=1;run_result(1);
 for(integer action=0;action<2;action++)for(integer state_id=0;state_id<20;state_id++)begin
  integer watchdog;
  reset_all;defaults;if(state_id!=0)launch;watchdog=0;
  while(int'(old.state)!=state_id && watchdog<20000)begin service;watchdog++;end
  if(watchdog==20000)$fatal(1,"独立状态不可达%0d",state_id);
  // 只读定位实际可达状态；取消时故意同沿给READY/RSP。
  backend_req_ready=1;backend_rsp_valid=1;backend_rsp_error=3'd7;
  if(action==0)begin abort=1;abort_mask|=1<<state_id;end else begin hard_reset=1;reset_mask|=1<<state_id;end
  tick;abort=0;hard_reset=0;backend_rsp_valid=0;pending=0;tick;
  if(busy || result_valid || !start_ready)$fatal(1,"独立取消/复位未回IDLE");
 end
 $display("PASS_INDEPENDENT_S4 hand=%0d cycles=%0d compare_cycles=%0d response_errors=%0d raw80=1 abort_mask=%x reset_mask=%x",hand_count,ticks,checked,error_cases,abort_mask,reset_mask);
 $finish;
end
endmodule
