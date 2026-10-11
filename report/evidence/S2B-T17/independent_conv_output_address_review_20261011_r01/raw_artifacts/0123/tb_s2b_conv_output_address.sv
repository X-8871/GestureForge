// 完整旧/新CONV模块组合锥对比；公开运行由独立START回归负责。
`timescale 1ns/1ps
module tb_s2b_conv_output_address;
logic clk=0;
logic [31:0] v_output_group_base;
logic [31:0] v_output_lane_index;
logic [31:0] v_output_height_latched;
logic [31:0] v_output_width_latched;
logic [31:0] v_tile_start_y;
logic [31:0] v_output_point_scan_y;
logic [31:0] v_tile_start_x;
logic [31:0] v_output_point_scan_x;
logic [31:0] v_output_base_latched;
logic [31:0] v_output_channels_latched;
logic [31:0] v_group_lane_count;
logic [31:0] v_output_point_index;
logic [31:0] v_tile_point_count;
logic [31:0] gold_c;
logic [31:0] gold_y;
logic [31:0] gold_x;
logic [63:0] gold_offset;
logic [63:0] gold_address;
logic [0:0] gold_bad;
logic [1:0] gold_action;
logic [63:0] gold_elements;
s2b_conv_tile_engine_original u_old (.clk(clk),.hard_reset('0),.abort('0),.buffer_owner_pl('0),.start_valid('0),.start_ready(),.layer_index('0),.weight_layer_index('0),.input_base_address('0),.input_length_bytes('0),.input_batch_count('0),.input_channels('0),.input_height('0),.input_width('0),.output_base_address('0),.output_length_bytes('0),.output_batch_count('0),.output_channels('0),.output_height('0),.output_width('0),.kernel_height('0),.kernel_width('0),.stride_y('0),.stride_x('0),.pad_left('0),.pad_right('0),.pad_top('0),.pad_bottom('0),.groups('0),.padding_value_int8('0),.weight_package_base_address('0),.weight_package_length_bytes('0),.quantized_weight_offset('0),.quantized_weight_bytes('0),.output_batch('0),.activation_mode('0),.backend_cancel(),.backend_req_valid(),.backend_req_ready('0),.backend_req_write(),.backend_req_addr(),.backend_req_wdata(),.backend_req_rstrb(),.backend_req_wstrb(),.backend_rsp_valid('0),.backend_rsp_rdata('0),.backend_rsp_error('0),.busy(),.result_valid(),.result_ready('0),.result_error_code());
s2b_conv_tile_engine u_dut (.clk(clk),.hard_reset('0),.abort('0),.buffer_owner_pl('0),.start_valid('0),.start_ready(),.layer_index('0),.weight_layer_index('0),.input_base_address('0),.input_length_bytes('0),.input_batch_count('0),.input_channels('0),.input_height('0),.input_width('0),.output_base_address('0),.output_length_bytes('0),.output_batch_count('0),.output_channels('0),.output_height('0),.output_width('0),.kernel_height('0),.kernel_width('0),.stride_y('0),.stride_x('0),.pad_left('0),.pad_right('0),.pad_top('0),.pad_bottom('0),.groups('0),.padding_value_int8('0),.weight_package_base_address('0),.weight_package_length_bytes('0),.quantized_weight_offset('0),.quantized_weight_bytes('0),.output_batch('0),.activation_mode('0),.backend_cancel(),.backend_req_valid(),.backend_req_ready('0),.backend_req_write(),.backend_req_addr(),.backend_req_wdata(),.backend_req_rstrb(),.backend_req_wstrb(),.backend_rsp_valid('0),.backend_rsp_rdata('0),.backend_rsp_error('0),.busy(),.result_valid(),.result_ready('0),.result_error_code());
function automatic logic [1:0] action(input logic[31:0] lane,lanes,point,points,input logic bad);
begin if(lane>=lanes) action=0;else if(point>=points)action=1;else if(bad)action=2;else action=3;end
endfunction
integer fd,scanned,count=0;integer branch_count[0:3]='{default:0};string vector_path;
initial begin
 if(!$value$plusargs("VECTOR_PATH=%s",vector_path))$fatal(1,"精确向量路径缺失");
 fd=$fopen(vector_path,"r");if(fd==0)$fatal(1,"向量缺失");
 while(!$feof(fd))begin
  scanned=$fscanf(fd,"%h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h\n",v_output_group_base,v_output_lane_index,v_output_height_latched,v_output_width_latched,v_tile_start_y,v_output_point_scan_y,v_tile_start_x,v_output_point_scan_x,v_output_base_latched,v_output_channels_latched,v_group_lane_count,v_output_point_index,v_tile_point_count,gold_c,gold_y,gold_x,gold_offset,gold_address,gold_bad,gold_action,gold_elements);
  if(scanned==21)begin
   u_old.output_group_base=v_output_group_base;
u_old.output_lane_index=v_output_lane_index;
u_old.output_height_latched=v_output_height_latched;
u_old.output_width_latched=v_output_width_latched;
u_old.tile_start_y=v_tile_start_y;
u_old.output_point_scan_y=v_output_point_scan_y;
u_old.tile_start_x=v_tile_start_x;
u_old.output_point_scan_x=v_output_point_scan_x;
u_old.output_base_latched=v_output_base_latched;
u_old.output_channels_latched=v_output_channels_latched;
u_old.group_lane_count=v_group_lane_count;
u_old.output_point_index=v_output_point_index;
u_old.tile_point_count=v_tile_point_count;
u_dut.output_group_base=v_output_group_base;
u_dut.output_lane_index=v_output_lane_index;
u_dut.output_height_latched=v_output_height_latched;
u_dut.output_width_latched=v_output_width_latched;
u_dut.tile_start_y=v_tile_start_y;
u_dut.output_point_scan_y=v_output_point_scan_y;
u_dut.tile_start_x=v_tile_start_x;
u_dut.output_point_scan_x=v_output_point_scan_x;
u_dut.output_base_latched=v_output_base_latched;
u_dut.output_channels_latched=v_output_channels_latched;
u_dut.group_lane_count=v_group_lane_count;
u_dut.output_point_index=v_output_point_index;
u_dut.tile_point_count=v_tile_point_count;
   #1;
   if(u_old.output_channel_current !== gold_c) $fatal(1,"组合字段u_old.output_channel_current case=%0d",count);
if(u_old.output_global_y !== gold_y) $fatal(1,"组合字段u_old.output_global_y case=%0d",count);
if(u_old.output_global_x !== gold_x) $fatal(1,"组合字段u_old.output_global_x case=%0d",count);
if(u_old.output_byte_offset_wide !== gold_offset) $fatal(1,"组合字段u_old.output_byte_offset_wide case=%0d",count);
if(u_old.output_address_wide !== gold_address) $fatal(1,"组合字段u_old.output_address_wide case=%0d",count);
if(u_old.output_elements_wide !== {64'd0,gold_elements}) $fatal(1,"组合长度域 case=%0d",count);
if(((u_old.output_address_wide>64'hFFFFFFFF)||(u_old.output_byte_offset_wide>=u_old.output_elements_wide)) !== gold_bad) $fatal(1,"原范围判据 case=%0d",count);
if(action(u_old.output_lane_index,u_old.group_lane_count,u_old.output_point_index,u_old.tile_point_count,((u_old.output_address_wide>64'hFFFFFFFF)||(u_old.output_byte_offset_wide>=u_old.output_elements_wide))) !== gold_action) $fatal(1,"未消费分支次序 case=%0d",count);
if(u_dut.output_channel_current !== gold_c) $fatal(1,"组合字段u_dut.output_channel_current case=%0d",count);
if(u_dut.output_global_y !== gold_y) $fatal(1,"组合字段u_dut.output_global_y case=%0d",count);
if(u_dut.output_global_x !== gold_x) $fatal(1,"组合字段u_dut.output_global_x case=%0d",count);
if(u_dut.output_byte_offset_wide !== gold_offset) $fatal(1,"组合字段u_dut.output_byte_offset_wide case=%0d",count);
if(u_dut.output_address_wide !== gold_address) $fatal(1,"组合字段u_dut.output_address_wide case=%0d",count);
if(u_dut.output_elements_wide !== {64'd0,gold_elements}) $fatal(1,"组合长度域 case=%0d",count);
if(((u_dut.output_address_wide>64'hFFFFFFFF)||(u_dut.output_byte_offset_wide>=u_dut.output_elements_wide)) !== gold_bad) $fatal(1,"原范围判据 case=%0d",count);
if(action(u_dut.output_lane_index,u_dut.group_lane_count,u_dut.output_point_index,u_dut.tile_point_count,((u_dut.output_address_wide>64'hFFFFFFFF)||(u_dut.output_byte_offset_wide>=u_dut.output_elements_wide))) !== gold_action) $fatal(1,"未消费分支次序 case=%0d",count);
   branch_count[gold_action]++;count++;
  end else if(scanned!=-1)$fatal(1,"向量字段不足");
 end
 $fclose(fd);$display("PASS S9_CONV_OUTPUT_ADDRESS vectors=%0d advance=%0d next_lane=%0d range=%0d request=%0d",count,branch_count[0],branch_count[1],branch_count[2],branch_count[3]);$finish;
end
endmodule
