// 仅受控组合域：完整旧新模块、时钟恒0、无posedge；不属于公开事务覆盖。
`timescale 1ns/1ps
module tb_s2b_conv_feature_address;
logic clk=0;logic[1:0]v_state;logic v_rsp_valid;logic[2:0]v_rsp_error;
logic [31:0] v_feature_scan_channel;
logic [31:0] v_input_height_latched;
logic [31:0] v_input_width_latched;
logic [31:0] v_tile_start_y;
logic [31:0] v_stride_y_latched;
logic [31:0] v_feature_scan_y;
logic [31:0] v_pad_top_latched;
logic [31:0] v_tile_start_x;
logic [31:0] v_stride_x_latched;
logic [31:0] v_feature_scan_x;
logic [31:0] v_pad_left_latched;
logic [31:0] v_input_base_latched;
logic [31:0] v_patch_height;
logic [31:0] v_patch_width;
logic [31:0] v_feature_scan_index;
logic [31:0] v_patch_byte_count;
logic [63:0] gold_plane;
logic [63:0] gold_y;
logic [63:0] gold_x;
logic [0:0] gold_bounds;
logic [63:0] gold_offset;
logic [63:0] gold_address;
logic [0:0] gold_range;
logic [1:0] gold_action;
logic [0:0] gold_advance;
logic [31:0] gold_aligned;
logic [3:0] gold_strobe;
logic [63:0] gold_row;
s2b_conv_tile_engine_original u_old (.clk(clk),.hard_reset('0),.abort('0),.buffer_owner_pl('0),.start_valid('0),.start_ready(),.layer_index('0),.weight_layer_index('0),.input_base_address('0),.input_length_bytes('0),.input_batch_count('0),.input_channels('0),.input_height('0),.input_width('0),.output_base_address('0),.output_length_bytes('0),.output_batch_count('0),.output_channels('0),.output_height('0),.output_width('0),.kernel_height('0),.kernel_width('0),.stride_y('0),.stride_x('0),.pad_left('0),.pad_right('0),.pad_top('0),.pad_bottom('0),.groups('0),.padding_value_int8('0),.weight_package_base_address('0),.weight_package_length_bytes('0),.quantized_weight_offset('0),.quantized_weight_bytes('0),.output_batch('0),.activation_mode('0),.backend_cancel(),.backend_req_valid(),.backend_req_ready('0),.backend_req_write(),.backend_req_addr(),.backend_req_wdata(),.backend_req_rstrb(),.backend_req_wstrb(),.backend_rsp_valid(v_rsp_valid),.backend_rsp_rdata('0),.backend_rsp_error(v_rsp_error),.busy(),.result_valid(),.result_ready('0),.result_error_code());
s2b_conv_tile_engine u_dut (.clk(clk),.hard_reset('0),.abort('0),.buffer_owner_pl('0),.start_valid('0),.start_ready(),.layer_index('0),.weight_layer_index('0),.input_base_address('0),.input_length_bytes('0),.input_batch_count('0),.input_channels('0),.input_height('0),.input_width('0),.output_base_address('0),.output_length_bytes('0),.output_batch_count('0),.output_channels('0),.output_height('0),.output_width('0),.kernel_height('0),.kernel_width('0),.stride_y('0),.stride_x('0),.pad_left('0),.pad_right('0),.pad_top('0),.pad_bottom('0),.groups('0),.padding_value_int8('0),.weight_package_base_address('0),.weight_package_length_bytes('0),.quantized_weight_offset('0),.quantized_weight_bytes('0),.output_batch('0),.activation_mode('0),.backend_cancel(),.backend_req_valid(),.backend_req_ready('0),.backend_req_write(),.backend_req_addr(),.backend_req_wdata(),.backend_req_rstrb(),.backend_req_wstrb(),.backend_rsp_valid(v_rsp_valid),.backend_rsp_rdata('0),.backend_rsp_error(v_rsp_error),.busy(),.result_valid(),.result_ready('0),.result_error_code());
function automatic logic[1:0]action(input logic[31:0]index,count,input logic bounds,bad);
begin if(index>=count)action=0;else if(!bounds)action=1;else if(bad)action=2;else action=3;end
endfunction
integer fd,scanned,count=0;integer branch_count[0:3]='{default:0};string vector_path;
initial begin
if(!$value$plusargs("VECTOR_PATH=%s",vector_path))$fatal(1,"精确向量路径缺失");
fd=$fopen(vector_path,"r");if(fd==0)$fatal(1,"向量缺失");
while(!$feof(fd))begin
scanned=$fscanf(fd,"%h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h\n",v_feature_scan_channel,v_input_height_latched,v_input_width_latched,v_tile_start_y,v_stride_y_latched,v_feature_scan_y,v_pad_top_latched,v_tile_start_x,v_stride_x_latched,v_feature_scan_x,v_pad_left_latched,v_input_base_latched,v_patch_height,v_patch_width,v_feature_scan_index,v_patch_byte_count,v_state,v_rsp_valid,v_rsp_error,gold_plane,gold_y,gold_x,gold_bounds,gold_offset,gold_address,gold_range,gold_action,gold_advance,gold_aligned,gold_strobe,gold_row);
if(scanned==31)begin
u_old.feature_scan_channel=v_feature_scan_channel;
u_old.input_height_latched=v_input_height_latched;
u_old.input_width_latched=v_input_width_latched;
u_old.tile_start_y=v_tile_start_y;
u_old.stride_y_latched=v_stride_y_latched;
u_old.feature_scan_y=v_feature_scan_y;
u_old.pad_top_latched=v_pad_top_latched;
u_old.tile_start_x=v_tile_start_x;
u_old.stride_x_latched=v_stride_x_latched;
u_old.feature_scan_x=v_feature_scan_x;
u_old.pad_left_latched=v_pad_left_latched;
u_old.input_base_latched=v_input_base_latched;
u_old.patch_height=v_patch_height;
u_old.patch_width=v_patch_width;
u_old.feature_scan_index=v_feature_scan_index;
u_old.patch_byte_count=v_patch_byte_count;
u_dut.feature_scan_channel=v_feature_scan_channel;
u_dut.input_height_latched=v_input_height_latched;
u_dut.input_width_latched=v_input_width_latched;
u_dut.tile_start_y=v_tile_start_y;
u_dut.stride_y_latched=v_stride_y_latched;
u_dut.feature_scan_y=v_feature_scan_y;
u_dut.pad_top_latched=v_pad_top_latched;
u_dut.tile_start_x=v_tile_start_x;
u_dut.stride_x_latched=v_stride_x_latched;
u_dut.feature_scan_x=v_feature_scan_x;
u_dut.pad_left_latched=v_pad_left_latched;
u_dut.input_base_latched=v_input_base_latched;
u_dut.patch_height=v_patch_height;
u_dut.patch_width=v_patch_width;
u_dut.feature_scan_index=v_feature_scan_index;
u_dut.patch_byte_count=v_patch_byte_count;
case(v_state) 0:u_old.state=u_old.ST_IDLE;1:u_old.state=u_old.ST_FEATURE_SCAN;2:u_old.state=u_old.ST_FEATURE_RESPONSE;default:u_old.state=u_old.ST_WEIGHT_SCAN;endcase
case(v_state) 0:u_dut.state=u_dut.ST_IDLE;1:u_dut.state=u_dut.ST_FEATURE_SCAN;2:u_dut.state=u_dut.ST_FEATURE_RESPONSE;default:u_dut.state=u_dut.ST_WEIGHT_SCAN;endcase
#1;
if(u_old.patch_plane_bytes!==gold_plane)$fatal(1,"组合字段u_old.patch_plane_bytes case=%0d",count);
if(u_old.feature_input_y!==gold_y)$fatal(1,"组合字段u_old.feature_input_y case=%0d",count);
if(u_old.feature_input_x!==gold_x)$fatal(1,"组合字段u_old.feature_input_x case=%0d",count);
if(u_old.feature_scan_in_bounds!==gold_bounds)$fatal(1,"组合字段u_old.feature_scan_in_bounds case=%0d",count);
if(u_old.feature_source_offset!==gold_offset)$fatal(1,"组合字段u_old.feature_source_offset case=%0d",count);
if(u_old.feature_source_address_wide!==gold_address)$fatal(1,"组合字段u_old.feature_source_address_wide case=%0d",count);
if(u_old.feature_scan_advance!==gold_advance)$fatal(1,"组合字段u_old.feature_scan_advance case=%0d",count);
if((u_old.feature_source_address_wide>64'hFFFFFFFF)!==gold_range)$fatal(1,"原范围判据 case=%0d",count);
if(action(u_old.feature_scan_index,u_old.patch_byte_count,u_old.feature_scan_in_bounds,(u_old.feature_source_address_wide>64'hFFFFFFFF))!==gold_action)$fatal(1,"消费顺序 case=%0d",count);
if(gold_action==3 && v_state==1)begin if({u_old.feature_source_address_wide[31:2],2'b00}!==gold_aligned || (4'b0001<<u_old.feature_source_address_wide[1:0])!==gold_strobe)$fatal(1,"请求对齐/strobe case=%0d",count);end
if(u_dut.patch_plane_bytes!==gold_plane)$fatal(1,"组合字段u_dut.patch_plane_bytes case=%0d",count);
if(u_dut.feature_input_y!==gold_y)$fatal(1,"组合字段u_dut.feature_input_y case=%0d",count);
if(u_dut.feature_input_x!==gold_x)$fatal(1,"组合字段u_dut.feature_input_x case=%0d",count);
if(u_dut.feature_scan_in_bounds!==gold_bounds)$fatal(1,"组合字段u_dut.feature_scan_in_bounds case=%0d",count);
if(u_dut.feature_source_offset!==gold_offset)$fatal(1,"组合字段u_dut.feature_source_offset case=%0d",count);
if(u_dut.feature_source_address_wide!==gold_address)$fatal(1,"组合字段u_dut.feature_source_address_wide case=%0d",count);
if(u_dut.feature_scan_advance!==gold_advance)$fatal(1,"组合字段u_dut.feature_scan_advance case=%0d",count);
if((u_dut.feature_source_address_wide>64'hFFFFFFFF)!==gold_range)$fatal(1,"原范围判据 case=%0d",count);
if(action(u_dut.feature_scan_index,u_dut.patch_byte_count,u_dut.feature_scan_in_bounds,(u_dut.feature_source_address_wide>64'hFFFFFFFF))!==gold_action)$fatal(1,"消费顺序 case=%0d",count);
if(gold_action==3 && v_state==1)begin if({u_dut.feature_source_address_wide[31:2],2'b00}!==gold_aligned || (4'b0001<<u_dut.feature_source_address_wide[1:0])!==gold_strobe)$fatal(1,"请求对齐/strobe case=%0d",count);end
if(u_dut.feature_row_offset!==gold_row)$fatal(1,"消费行精确64/未bounds默认0 case=%0d",count);
branch_count[gold_action]++;count++;
end else if(scanned!=-1)$fatal(1,"向量字段不足");
end
$fclose(fd);$display("PASS S10_CONV_FEATURE_ADDRESS vectors=%0d end=%0d padding=%0d range=%0d request=%0d",count,branch_count[0],branch_count[1],branch_count[2],branch_count[3]);$finish;
end
endmodule
