// 卷积计算未改；此stub仅隔离backend控制验证，不声明卷积数值回归。
module s2a_conv_tile_engine (
    input  logic        clk,
    input  logic        hard_reset,
    input  logic        abort,
    input  logic        buffer_owner_pl,

    input  logic        start_valid,
    output logic        start_ready,
    input  logic [31:0] layer_index,
    input  logic [31:0] weight_layer_index,
    input  logic [31:0] input_base_address,
    input  logic [31:0] input_length_bytes,
    input  logic [31:0] input_batch_count,
    input  logic [31:0] input_channels,
    input  logic [31:0] input_height,
    input  logic [31:0] input_width,
    input  logic [31:0] output_base_address,
    input  logic [31:0] output_length_bytes,
    input  logic [31:0] output_batch_count,
    input  logic [31:0] output_channels,
    input  logic [31:0] output_height,
    input  logic [31:0] output_width,
    input  logic [31:0] kernel_height,
    input  logic [31:0] kernel_width,
    input  logic [31:0] stride_y,
    input  logic [31:0] stride_x,
    input  logic [31:0] pad_left,
    input  logic [31:0] pad_right,
    input  logic [31:0] pad_top,
    input  logic [31:0] pad_bottom,
    input  logic [31:0] groups,
    input  logic signed [31:0] padding_value_int8,
    input  logic [31:0] weight_package_base_address,
    input  logic [31:0] weight_package_length_bytes,
    input  logic [31:0] quantized_weight_offset,
    input  logic [31:0] quantized_weight_bytes,
    input  logic [31:0] output_batch,
    input  logic [1:0]  activation_mode,

    output logic        backend_cancel,
    output logic        backend_req_valid,
    input  logic        backend_req_ready,
    output logic        backend_req_write,
    output logic [31:0] backend_req_addr,
    output logic [31:0] backend_req_wdata,
    output logic [3:0]  backend_req_rstrb,
    output logic [3:0]  backend_req_wstrb,
    input  logic        backend_rsp_valid,
    input  logic [31:0] backend_rsp_rdata,
    input  logic [2:0]  backend_rsp_error,

    output logic        busy,
    output logic        result_valid,
    input  logic        result_ready,
    output logic [2:0]  result_error_code
);
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
// 卷积计算未改；此stub仅隔离backend控制验证，不声明卷积数值回归。
module s2b_conv_tile_engine #(parameter bit FROZEN_CONV_DESCRIPTOR=1'b0) (
    input  logic        clk,
    input  logic        hard_reset,
    input  logic        abort,
    input  logic        buffer_owner_pl,

    input  logic        start_valid,
    output logic        start_ready,
    input  logic [31:0] layer_index,
    input  logic [31:0] weight_layer_index,
    input  logic [31:0] input_base_address,
    input  logic [31:0] input_length_bytes,
    input  logic [31:0] input_batch_count,
    input  logic [31:0] input_channels,
    input  logic [31:0] input_height,
    input  logic [31:0] input_width,
    input  logic [31:0] output_base_address,
    input  logic [31:0] output_length_bytes,
    input  logic [31:0] output_batch_count,
    input  logic [31:0] output_channels,
    input  logic [31:0] output_height,
    input  logic [31:0] output_width,
    input  logic [31:0] kernel_height,
    input  logic [31:0] kernel_width,
    input  logic [31:0] stride_y,
    input  logic [31:0] stride_x,
    input  logic [31:0] pad_left,
    input  logic [31:0] pad_right,
    input  logic [31:0] pad_top,
    input  logic [31:0] pad_bottom,
    input  logic [31:0] groups,
    input  logic signed [31:0] padding_value_int8,
    input  logic [31:0] weight_package_base_address,
    input  logic [31:0] weight_package_length_bytes,
    input  logic [31:0] quantized_weight_offset,
    input  logic [31:0] quantized_weight_bytes,
    input  logic [31:0] output_batch,
    input  logic [1:0]  activation_mode,

    output logic        backend_cancel,
    output logic        backend_req_valid,
    input  logic        backend_req_ready,
    output logic        backend_req_write,
    output logic [31:0] backend_req_addr,
    output logic [31:0] backend_req_wdata,
    output logic [3:0]  backend_req_rstrb,
    output logic [3:0]  backend_req_wstrb,
    input  logic        backend_rsp_valid,
    input  logic [31:0] backend_rsp_rdata,
    input  logic [2:0]  backend_rsp_error,

    output logic        busy,
    output logic        result_valid,
    input  logic        result_ready,
    output logic [2:0]  result_error_code
);
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
