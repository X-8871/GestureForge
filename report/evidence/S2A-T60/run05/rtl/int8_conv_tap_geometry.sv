// G0 tiny416 卷积单 tap：按 reduction 顺序计算输入坐标和逻辑字节地址。
module int8_conv_tap_geometry (
    input  logic [31:0] input_base_address,
    input  logic [31:0] input_length_bytes,
    input  logic [31:0] input_batch_count,
    input  logic [31:0] input_channels,
    input  logic [31:0] input_height,
    input  logic [31:0] input_width,

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
    input  logic signed [7:0] padding_value_int8,
    input  logic [31:0] groups,

    input  logic [31:0] output_batch,
    input  logic [31:0] output_channel,
    input  logic [31:0] output_y,
    input  logic [31:0] output_x,
    input  logic [31:0] reduction_index,

    output logic [31:0] input_channel,
    output logic [31:0] kernel_y,
    output logic [31:0] kernel_x,
    output logic signed [31:0] input_y,
    output logic signed [31:0] input_x,
    output logic tap_is_padding,
    output logic source_address_valid,
    output logic [31:0] source_address,
    output logic signed [7:0] tap_padding_value,
    output logic [2:0] error_code
);
    localparam logic [2:0] OK = 3'd0;
    localparam logic [2:0] BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] BAD_RANGE = 3'd2;

    logic bad_argument;
    logic bad_range;
    logic [63:0] input_plane_elements;
    logic [63:0] input_shape_bytes;
    logic [63:0] input_object_end;
    logic [63:0] output_height_numerator;
    logic [63:0] output_width_numerator;
    logic [63:0] reduction_plane_elements;
    logic [63:0] reduction_count;
    logic [63:0] safe_kernel_area;
    logic [63:0] selected_input_channel;
    logic [63:0] selected_kernel_y;
    logic [63:0] selected_kernel_x;
    logic signed [63:0] candidate_y;
    logic signed [63:0] candidate_x;
    logic [63:0] source_offset;
    logic [63:0] source_address_wide;
    logic tap_in_bounds;

    always_comb begin
        // 组合默认值使错误请求不输出有效地址或残留坐标。
        input_channel = 32'd0;
        kernel_y = 32'd0;
        kernel_x = 32'd0;
        input_y = 32'sd0;
        input_x = 32'sd0;
        tap_is_padding = 1'b0;
        source_address_valid = 1'b0;
        source_address = 32'd0;
        tap_padding_value = 8'sd0;
        error_code = OK;

        bad_argument = 1'b0;
        bad_range = 1'b0;
        input_plane_elements = 64'd0;
        input_shape_bytes = 64'd0;
        input_object_end = 64'd0;
        output_height_numerator = 64'd0;
        output_width_numerator = 64'd0;
        reduction_plane_elements = 64'd0;
        reduction_count = 64'd0;
        safe_kernel_area = 64'd1;
        selected_input_channel = 64'd0;
        selected_kernel_y = 64'd0;
        selected_kernel_x = 64'd0;
        candidate_y = 64'sd0;
        candidate_x = 64'sd0;
        source_offset = 64'd0;
        source_address_wide = 64'd0;
        tap_in_bounds = 1'b0;

        if ((input_batch_count != 32'd1) ||
            (output_batch_count != 32'd1) || (output_batch != 32'd0) ||
            (input_channels == 32'd0) || (input_height == 32'd0) ||
            (input_width == 32'd0) || (output_channels == 32'd0) ||
            (output_height == 32'd0) || (output_width == 32'd0) ||
            (kernel_height == 32'd0) || (kernel_width == 32'd0) ||
            (stride_y == 32'd0) || (stride_x == 32'd0) ||
            (groups != 32'd1) || (padding_value_int8 != 8'sd0)) begin
            bad_argument = 1'b1;
        end

        if ((output_channel >= output_channels) ||
            (output_y >= output_height) || (output_x >= output_width)) begin
            bad_argument = 1'b1;
        end

        output_height_numerator = {32'd0, input_height} +
                                  {32'd0, pad_top} +
                                  {32'd0, pad_bottom};
        output_width_numerator = {32'd0, input_width} +
                                 {32'd0, pad_left} +
                                 {32'd0, pad_right};
        if ((kernel_height != 32'd0) && (stride_y != 32'd0)) begin
            if (output_height_numerator < {32'd0, kernel_height}) begin
                bad_argument = 1'b1;
            end else if (((output_height_numerator - {32'd0, kernel_height}) /
                          stride_y) + 64'd1 != {32'd0, output_height}) begin
                bad_argument = 1'b1;
            end
        end
        if ((kernel_width != 32'd0) && (stride_x != 32'd0)) begin
            if (output_width_numerator < {32'd0, kernel_width}) begin
                bad_argument = 1'b1;
            end else if (((output_width_numerator - {32'd0, kernel_width}) /
                          stride_x) + 64'd1 != {32'd0, output_width}) begin
                bad_argument = 1'b1;
            end
        end

        input_plane_elements = {32'd0, input_channels} *
                               {32'd0, input_height};
        if (input_plane_elements > 64'h0000_0000_FFFF_FFFF) begin
            bad_range = 1'b1;
        end else begin
            input_shape_bytes = input_plane_elements * {32'd0, input_width};
            if (input_shape_bytes > 64'h0000_0000_FFFF_FFFF) begin
                bad_range = 1'b1;
            end
        end
        input_object_end = {32'd0, input_base_address} +
                           {32'd0, input_length_bytes};
        if ((input_length_bytes == 32'd0) ||
            ({32'd0, input_length_bytes} != input_shape_bytes) ||
            (input_object_end > 64'h0000_0001_0000_0000)) begin
            bad_range = 1'b1;
        end

        reduction_plane_elements = {32'd0, kernel_height} *
                                   {32'd0, kernel_width};
        if ((reduction_plane_elements == 64'd0) ||
            (reduction_plane_elements > 64'h0000_0000_FFFF_FFFF)) begin
            bad_argument = 1'b1;
            safe_kernel_area = 64'd1;
        end else begin
            safe_kernel_area = reduction_plane_elements;
        end
        if (input_channels != 32'd0) begin
            reduction_count = {32'd0, input_channels} * safe_kernel_area;
            if (reduction_count > 64'h0000_0000_FFFF_FFFF) begin
                bad_range = 1'b1;
            end
        end
        if ((reduction_index >= reduction_count) || (safe_kernel_area == 64'd0)) begin
            bad_argument = 1'b1;
        end

        if ((reduction_plane_elements != 64'd0) && (kernel_width != 32'd0)) begin
            selected_input_channel = {32'd0, reduction_index} /
                                     safe_kernel_area;
            selected_kernel_y = ({32'd0, reduction_index} % safe_kernel_area) /
                                kernel_width;
            selected_kernel_x = {32'd0, reduction_index} % kernel_width;
        end
        candidate_y = ($signed({32'd0, output_y}) *
                       $signed({32'd0, stride_y})) +
                      $signed(selected_kernel_y) - $signed({32'd0, pad_top});
        candidate_x = ($signed({32'd0, output_x}) *
                       $signed({32'd0, stride_x})) +
                      $signed(selected_kernel_x) - $signed({32'd0, pad_left});
        if ((candidate_y > 64'sd2147483647) ||
            (candidate_y < -64'sd2147483648) ||
            (candidate_x > 64'sd2147483647) ||
            (candidate_x < -64'sd2147483648)) begin
            bad_range = 1'b1;
        end
        tap_in_bounds =
            (candidate_y >= 64'sd0) &&
            (candidate_y < $signed({32'd0, input_height})) &&
            (candidate_x >= 64'sd0) &&
            (candidate_x < $signed({32'd0, input_width}));

        if (tap_in_bounds) begin
            source_offset =
                ((selected_input_channel * {32'd0, input_height}) +
                 candidate_y[63:0]) * {32'd0, input_width} +
                candidate_x[63:0];
            source_address_wide = {32'd0, input_base_address} + source_offset;
            if ((source_offset >= input_shape_bytes) ||
                (source_offset >= {32'd0, input_length_bytes}) ||
                (source_address_wide > 64'h0000_0000_FFFF_FFFF)) begin
                bad_range = 1'b1;
            end
        end

        if (bad_argument) begin
            error_code = BAD_ARGUMENT;
        end else if (bad_range) begin
            error_code = BAD_RANGE;
        end else begin
            input_channel = selected_input_channel[31:0];
            kernel_y = selected_kernel_y[31:0];
            kernel_x = selected_kernel_x[31:0];
            input_y = candidate_y[31:0];
            input_x = candidate_x[31:0];
            tap_is_padding = !tap_in_bounds;
            source_address_valid = tap_in_bounds;
            if (tap_in_bounds) begin
                source_address = source_address_wide[31:0];
            end
            tap_padding_value = 8'sd0;
        end
    end
endmodule
