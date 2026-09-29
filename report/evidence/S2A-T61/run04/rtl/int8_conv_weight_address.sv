// S2A-T09：查询 GFINT8W1 卷积 INT8 权重字节的局部偏移和逻辑地址。
module int8_conv_weight_address (
    input  logic [31:0] layer_index,
    input  logic [31:0] weight_layer_index,
    input  logic [31:0] groups,
    input  logic [31:0] output_channels,
    input  logic [31:0] input_channels,
    input  logic [31:0] kernel_height,
    input  logic [31:0] kernel_width,
    input  logic [31:0] quantized_weight_offset,
    input  logic [31:0] quantized_weight_bytes,
    input  logic [31:0] weight_package_base_address,
    input  logic [31:0] weight_package_length_bytes,
    input  logic [31:0] query_output_channel,
    input  logic [31:0] query_input_channel,
    input  logic [31:0] query_kernel_y,
    input  logic [31:0] query_kernel_x,
    output logic [31:0] reduction_index,
    output logic [31:0] layer_weight_byte_offset,
    output logic [31:0] package_byte_offset,
    output logic [31:0] weight_byte_address,
    output logic [2:0]  error_code
);
    localparam logic [2:0] NONE         = 3'd0;
    localparam logic [2:0] BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] BAD_RANGE    = 3'd2;

    logic [95:0] reduction_count;
    logic [127:0] expected_weight_bytes;
    logic [63:0] reduction_value;
    logic [63:0] layer_offset_value;
    logic [63:0] package_offset_value;
    logic [63:0] address_value;
    logic [63:0] package_end_exclusive;
    logic [63:0] quantized_end_exclusive;
    logic [63:0] address_space_limit;

    // 默认清零；错误查询不暴露偏移或地址。
    always_comb begin
        reduction_index = 32'd0;
        layer_weight_byte_offset = 32'd0;
        package_byte_offset = 32'd0;
        weight_byte_address = 32'd0;
        error_code = NONE;

        reduction_count = 96'd0;
        expected_weight_bytes = 128'd0;
        reduction_value = 64'd0;
        layer_offset_value = 64'd0;
        package_offset_value = 64'd0;
        address_value = 64'd0;
        package_end_exclusive = 64'd0;
        quantized_end_exclusive = 64'd0;
        address_space_limit = 64'h0000_0001_0000_0000;

        if ((layer_index != weight_layer_index) ||
            (groups != 32'd1) ||
            (output_channels == 32'd0) ||
            (input_channels == 32'd0) ||
            (kernel_height == 32'd0) ||
            (kernel_width == 32'd0) ||
            (query_output_channel >= output_channels) ||
            (query_input_channel >= input_channels) ||
            (query_kernel_y >= kernel_height) ||
            (query_kernel_x >= kernel_width)) begin
            error_code = BAD_ARGUMENT;
        end else begin
            reduction_count = {64'd0, input_channels} *
                              {64'd0, kernel_height} *
                              {64'd0, kernel_width};
            expected_weight_bytes = {96'd0, output_channels} *
                                    {96'd0, input_channels} *
                                    {96'd0, kernel_height} *
                                    {96'd0, kernel_width};
            package_end_exclusive = {32'd0, weight_package_base_address} +
                                    {32'd0, weight_package_length_bytes};
            quantized_end_exclusive = {32'd0, quantized_weight_offset} +
                                      {32'd0, quantized_weight_bytes};

            if ((weight_package_length_bytes == 32'd0) ||
                (expected_weight_bytes > 128'h0000_0000_0000_0000_0000_0000_FFFF_FFFF) ||
                (quantized_weight_bytes != expected_weight_bytes[31:0]) ||
                (quantized_end_exclusive > {32'd0, weight_package_length_bytes}) ||
                (package_end_exclusive > address_space_limit)) begin
                error_code = BAD_RANGE;
            end else begin
                reduction_value = {32'd0, query_input_channel} *
                                  {32'd0, kernel_height} *
                                  {32'd0, kernel_width} +
                                  {32'd0, query_kernel_y} *
                                  {32'd0, kernel_width} +
                                  {32'd0, query_kernel_x};
                layer_offset_value = {32'd0, query_output_channel} *
                                     reduction_count + reduction_value;
                package_offset_value = {32'd0, quantized_weight_offset} +
                                       layer_offset_value;
                address_value = {32'd0, weight_package_base_address} +
                                package_offset_value;

                if ((reduction_value >= reduction_count) ||
                    (layer_offset_value >= {32'd0, quantized_weight_bytes}) ||
                    (package_offset_value >= {32'd0, weight_package_length_bytes}) ||
                    (address_value >= address_space_limit)) begin
                    error_code = BAD_RANGE;
                end else begin
                    reduction_index = reduction_value[31:0];
                    layer_weight_byte_offset = layer_offset_value[31:0];
                    package_byte_offset = package_offset_value[31:0];
                    weight_byte_address = address_value[31:0];
                end
            end
        end
    end
endmodule
