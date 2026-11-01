// 三种冻结shape全坐标穷举，地址黄金仅按NCHW定义计算。
module tb_s2b_fixed_pool_geometry;
logic [31:0] base_address, channel_value, output_y_value, output_x_value;
logic [31:0] vector_shape, input_channel, output_y, output_x;
integer file_handle, scanned, count=0, tap_index;
integer expected_height, expected_width, expected_error;
longint unsigned expected_address, offset_value;
longint signed expected_y, expected_x;
logic [2:0] error_code [0:2]; logic [32:0] output_height [0:2], output_width [0:2];
logic [3:0] tap_count [0:2]; logic [8:0] valid_mask [0:2];
logic [31:0] tap_address [0:2][0:8], tap_channel [0:2][0:8];
logic signed [63:0] tap_source_y [0:2][0:8], tap_source_x [0:2][0:8];
string vector_path;
s2b_maxpool_geometry #(.FAST_FIXED_POOL_SHAPE(1)) u_fixed_0 (.input_base_address(base_address), .input_channels(32'd128), .input_height(32'd104), .input_width(32'd104), .kernel_height(32'd2), .kernel_width(32'd2), .stride_y(32'd2), .stride_x(32'd2), .darknet_padding_parameter(32'd1), .input_channel(input_channel), .output_y(output_y), .output_x(output_x), .output_height(output_height[0]), .output_width(output_width[0]), .tap_count(tap_count[0]), .tap_valid_mask(valid_mask[0]), .tap_address(tap_address[0]), .tap_source_channel(tap_channel[0]), .tap_source_y(tap_source_y[0]), .tap_source_x(tap_source_x[0]), .error_code(error_code[0]));
s2b_maxpool_geometry #(.FAST_FIXED_POOL_SHAPE(2)) u_fixed_1 (.input_base_address(base_address), .input_channels(32'd256), .input_height(32'd52), .input_width(32'd52), .kernel_height(32'd2), .kernel_width(32'd2), .stride_y(32'd2), .stride_x(32'd2), .darknet_padding_parameter(32'd1), .input_channel(input_channel), .output_y(output_y), .output_x(output_x), .output_height(output_height[1]), .output_width(output_width[1]), .tap_count(tap_count[1]), .tap_valid_mask(valid_mask[1]), .tap_address(tap_address[1]), .tap_source_channel(tap_channel[1]), .tap_source_y(tap_source_y[1]), .tap_source_x(tap_source_x[1]), .error_code(error_code[1]));
s2b_maxpool_geometry #(.FAST_FIXED_POOL_SHAPE(3)) u_fixed_2 (.input_base_address(base_address), .input_channels(32'd512), .input_height(32'd26), .input_width(32'd26), .kernel_height(32'd2), .kernel_width(32'd2), .stride_y(32'd2), .stride_x(32'd2), .darknet_padding_parameter(32'd1), .input_channel(input_channel), .output_y(output_y), .output_x(output_x), .output_height(output_height[2]), .output_width(output_width[2]), .tap_count(tap_count[2]), .tap_valid_mask(valid_mask[2]), .tap_address(tap_address[2]), .tap_source_channel(tap_channel[2]), .tap_source_y(tap_source_y[2]), .tap_source_x(tap_source_x[2]), .error_code(error_code[2]));
initial begin if(!$value$plusargs("VECTOR_PATH=%s",vector_path)) $fatal(1,"缺少专化向量");
file_handle=$fopen(vector_path,"r"); if(!file_handle) $fatal(1,"无法读取专化向量");
while(!$feof(file_handle)) begin
scanned=$fscanf(file_handle,"%h %h %h %h %h\n",vector_shape,channel_value,output_y_value,output_x_value,base_address);
if(scanned==5) begin input_channel=channel_value; output_y=output_y_value; output_x=output_x_value; #1;
case(vector_shape)
0: begin expected_height=52; expected_width=52;
expected_error=0; offset_value=0;
if(channel_value>=128 || output_y_value>=52 || output_x_value>=52) expected_error=1;
else begin offset_value=channel_value*64'd10816+(output_y_value*64'd2)*64'd104+output_x_value*64'd2; if(base_address+offset_value+64'd105>64'h00000000ffffffff) expected_error=2; end
if(expected_error==0 && {error_code[0],output_height[0],output_width[0],tap_count[0],valid_mask[0]} !== {3'd0,33'd52,33'd52,4'd4,9'd15}) $fatal(1,"专化geometry头字段错误 shape=0 case=%0d",count);
if(expected_error!=0 && error_code[0] !== expected_error[2:0]) $fatal(1,"专化geometry错误码错误 shape=0 case=%0d",count);
if(expected_error!=0 && {output_height[0],output_width[0],tap_count[0],valid_mask[0]} !== '0) $fatal(1,"专化geometry头字段清零错误 shape=0 case=%0d",count);
for(tap_index=0;tap_index<9;tap_index++) begin
if(expected_error==0 && tap_index<4) begin expected_y=output_y_value*64'd2+(tap_index/2); expected_x=output_x_value*64'd2+(tap_index%2);
expected_address=base_address+channel_value*64'd10816+expected_y*64'd104+expected_x;
if(tap_address[0][tap_index] !== expected_address[31:0] || tap_channel[0][tap_index] !== channel_value || tap_source_y[0][tap_index] !== expected_y || tap_source_x[0][tap_index] !== expected_x) $fatal(1,"专化geometry tap错误 shape=0 case=%0d tap=%0d",count,tap_index);
end else if ({tap_address[0][tap_index],tap_channel[0][tap_index],tap_source_y[0][tap_index],tap_source_x[0][tap_index]} !== '0) $fatal(1,"专化geometry tap清零错误 shape=0 case=%0d tap=%0d",count,tap_index);
end end
1: begin expected_height=26; expected_width=26;
expected_error=0; offset_value=0;
if(channel_value>=256 || output_y_value>=26 || output_x_value>=26) expected_error=1;
else begin offset_value=channel_value*64'd2704+(output_y_value*64'd2)*64'd52+output_x_value*64'd2; if(base_address+offset_value+64'd53>64'h00000000ffffffff) expected_error=2; end
if(expected_error==0 && {error_code[1],output_height[1],output_width[1],tap_count[1],valid_mask[1]} !== {3'd0,33'd26,33'd26,4'd4,9'd15}) $fatal(1,"专化geometry头字段错误 shape=1 case=%0d",count);
if(expected_error!=0 && error_code[1] !== expected_error[2:0]) $fatal(1,"专化geometry错误码错误 shape=1 case=%0d",count);
if(expected_error!=0 && {output_height[1],output_width[1],tap_count[1],valid_mask[1]} !== '0) $fatal(1,"专化geometry头字段清零错误 shape=1 case=%0d",count);
for(tap_index=0;tap_index<9;tap_index++) begin
if(expected_error==0 && tap_index<4) begin expected_y=output_y_value*64'd2+(tap_index/2); expected_x=output_x_value*64'd2+(tap_index%2);
expected_address=base_address+channel_value*64'd2704+expected_y*64'd52+expected_x;
if(tap_address[1][tap_index] !== expected_address[31:0] || tap_channel[1][tap_index] !== channel_value || tap_source_y[1][tap_index] !== expected_y || tap_source_x[1][tap_index] !== expected_x) $fatal(1,"专化geometry tap错误 shape=1 case=%0d tap=%0d",count,tap_index);
end else if ({tap_address[1][tap_index],tap_channel[1][tap_index],tap_source_y[1][tap_index],tap_source_x[1][tap_index]} !== '0) $fatal(1,"专化geometry tap清零错误 shape=1 case=%0d tap=%0d",count,tap_index);
end end
2: begin expected_height=13; expected_width=13;
expected_error=0; offset_value=0;
if(channel_value>=512 || output_y_value>=13 || output_x_value>=13) expected_error=1;
else begin offset_value=channel_value*64'd676+(output_y_value*64'd2)*64'd26+output_x_value*64'd2; if(base_address+offset_value+64'd27>64'h00000000ffffffff) expected_error=2; end
if(expected_error==0 && {error_code[2],output_height[2],output_width[2],tap_count[2],valid_mask[2]} !== {3'd0,33'd13,33'd13,4'd4,9'd15}) $fatal(1,"专化geometry头字段错误 shape=2 case=%0d",count);
if(expected_error!=0 && error_code[2] !== expected_error[2:0]) $fatal(1,"专化geometry错误码错误 shape=2 case=%0d",count);
if(expected_error!=0 && {output_height[2],output_width[2],tap_count[2],valid_mask[2]} !== '0) $fatal(1,"专化geometry头字段清零错误 shape=2 case=%0d",count);
for(tap_index=0;tap_index<9;tap_index++) begin
if(expected_error==0 && tap_index<4) begin expected_y=output_y_value*64'd2+(tap_index/2); expected_x=output_x_value*64'd2+(tap_index%2);
expected_address=base_address+channel_value*64'd676+expected_y*64'd26+expected_x;
if(tap_address[2][tap_index] !== expected_address[31:0] || tap_channel[2][tap_index] !== channel_value || tap_source_y[2][tap_index] !== expected_y || tap_source_x[2][tap_index] !== expected_x) $fatal(1,"专化geometry tap错误 shape=2 case=%0d tap=%0d",count,tap_index);
end else if ({tap_address[2][tap_index],tap_channel[2][tap_index],tap_source_y[2][tap_index],tap_source_x[2][tap_index]} !== '0) $fatal(1,"专化geometry tap清零错误 shape=2 case=%0d tap=%0d",count,tap_index);
end end
default: $fatal(1,"非法专化shape=%0d",vector_shape);
endcase count++; end else if(scanned!=-1) $fatal(1,"专化向量字段不足"); end
$fclose(file_handle); $display("PASS FIXED_POOL_GEOMETRY vectors=%0d",count); $finish; end endmodule
