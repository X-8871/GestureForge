// 原RTL与独立NCHW黄金全字段比较。
module tb_s8_geometry;
integer count=0; integer scanned; integer f;
logic [2:0] gold_error; logic [32:0] gold_h,gold_w; logic [3:0] gold_count; logic [8:0] gold_mask;
logic [31:0] input_base_address;
logic [31:0] input_channels;
logic [31:0] input_height;
logic [31:0] input_width;
logic [31:0] kernel_height;
logic [31:0] kernel_width;
logic [31:0] stride_y;
logic [31:0] stride_x;
logic [31:0] darknet_padding_parameter;
logic [31:0] input_channel;
logic [31:0] output_y;
logic [31:0] output_x;
logic [2:0] old_error; logic [32:0] old_h,old_w; logic [3:0] old_count; logic [8:0] old_mask;
logic [31:0] old_address[0:8],old_channel[0:8]; logic signed [63:0] old_y[0:8],old_x[0:8];
logic [2:0] new_error; logic [32:0] new_h,new_w; logic [3:0] new_count; logic [8:0] new_mask;
logic [31:0] new_address[0:8],new_channel[0:8]; logic signed [63:0] new_y[0:8],new_x[0:8];
logic [31:0] gold_address[0:8],gold_channel[0:8]; logic signed [63:0] gold_y[0:8],gold_x[0:8];
int8_maxpool_geometry old_dut(.input_base_address(input_base_address),.input_channels(input_channels),.input_height(input_height),.input_width(input_width),.kernel_height(kernel_height),.kernel_width(kernel_width),.stride_y(stride_y),.stride_x(stride_x),.darknet_padding_parameter(darknet_padding_parameter),.input_channel(input_channel),.output_y(output_y),.output_x(output_x),.output_height(old_h),.output_width(old_w),.tap_count(old_count),.tap_valid_mask(old_mask),.error_code(old_error),.tap_address(old_address),.tap_source_channel(old_channel),.tap_source_y(old_y),.tap_source_x(old_x));
s2b_maxpool_geometry new_dut(.input_base_address(input_base_address),.input_channels(input_channels),.input_height(input_height),.input_width(input_width),.kernel_height(kernel_height),.kernel_width(kernel_width),.stride_y(stride_y),.stride_x(stride_x),.darknet_padding_parameter(darknet_padding_parameter),.input_channel(input_channel),.output_y(output_y),.output_x(output_x),.output_height(new_h),.output_width(new_w),.tap_count(new_count),.tap_valid_mask(new_mask),.error_code(new_error),.tap_address(new_address),.tap_source_channel(new_channel),.tap_source_y(new_y),.tap_source_x(new_x));
initial begin f=$fopen("geometry_vectors.dat","r"); if(!f) $fatal(1,"缺少向量"); while(!$feof(f)) begin
scanned=$fscanf(f,"%h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h\n",input_base_address,input_channels,input_height,input_width,kernel_height,kernel_width,stride_y,stride_x,darknet_padding_parameter,input_channel,output_y,output_x,gold_error,gold_h,gold_w,gold_count,gold_mask,gold_address[0],gold_channel[0],gold_y[0],gold_x[0],gold_address[1],gold_channel[1],gold_y[1],gold_x[1],gold_address[2],gold_channel[2],gold_y[2],gold_x[2],gold_address[3],gold_channel[3],gold_y[3],gold_x[3],gold_address[4],gold_channel[4],gold_y[4],gold_x[4],gold_address[5],gold_channel[5],gold_y[5],gold_x[5],gold_address[6],gold_channel[6],gold_y[6],gold_x[6],gold_address[7],gold_channel[7],gold_y[7],gold_x[7],gold_address[8],gold_channel[8],gold_y[8],gold_x[8]);
if(scanned==53) begin #1;
if({old_error,old_h,old_w,old_count,old_mask} !== {gold_error,gold_h,gold_w,gold_count,gold_mask}) $fatal(1,"几何头字段不等价 old case=%0d",count);
for(integer t=0;t<9;t++) if({old_address[t],old_channel[t],old_y[t],old_x[t]} !== {gold_address[t],gold_channel[t],gold_y[t],gold_x[t]}) $fatal(1,"几何tap字段不等价 old case=%0d tap=%0d",count,t);
if({new_error,new_h,new_w,new_count,new_mask} !== {gold_error,gold_h,gold_w,gold_count,gold_mask}) $fatal(1,"几何头字段不等价 new case=%0d",count);
for(integer t=0;t<9;t++) if({new_address[t],new_channel[t],new_y[t],new_x[t]} !== {gold_address[t],gold_channel[t],gold_y[t],gold_x[t]}) $fatal(1,"几何tap字段不等价 new case=%0d tap=%0d",count,t);
count++; end else if(scanned!=-1) $fatal(1,"向量字段不足"); end $fclose(f); $display("PASS S8_GEOMETRY vectors=%0d",count); $finish; end endmodule
