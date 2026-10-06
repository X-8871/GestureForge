// 阶段 2A：计算单个 INT8 最大池化输出窗口的几何和 NCHW 字节地址。
module int8_maxpool_geometry (
    input  logic [31:0] input_base_address,
    input  logic [31:0] input_channels,
    input  logic [31:0] input_height,
    input  logic [31:0] input_width,
    input  logic [31:0] kernel_height,
    input  logic [31:0] kernel_width,
    input  logic [31:0] stride_y,
    input  logic [31:0] stride_x,
    input  logic [31:0] darknet_padding_parameter,
    input  logic [31:0] input_channel,
    input  logic [31:0] output_y,
    input  logic [31:0] output_x,
    output logic [32:0] output_height,
    output logic [32:0] output_width,
    output logic [3:0] tap_count,
    output logic [8:0] tap_valid_mask,
    output logic [31:0] tap_address [0:8],
    output logic [31:0] tap_source_channel [0:8],
    output logic signed [63:0] tap_source_y [0:8],
    output logic signed [63:0] tap_source_x [0:8],
    // 成功为 0；参数/坐标非法为 BAD_ARGUMENT(1)，uint32 地址越界为 BAD_RANGE(2)。
    output logic [2:0] error_code
);
    localparam logic [2:0] BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] BAD_RANGE = 3'd2;

    logic [32:0] extent_y;
    logic [32:0] extent_x;
    logic [32:0] output_height_work;
    logic [32:0] output_width_work;
    logic signed [63:0] origin_y;
    logic signed [63:0] origin_x;
    logic [63:0] output_y_step;
    logic [63:0] output_x_step;
    logic signed [63:0] source_y_work;
    logic signed [63:0] source_x_work;
    logic [95:0] channel_row_work;
    logic [95:0] row_work;
    logic [95:0] logical_offset_work;
    logic [96:0] address_work;
    integer tap_index;
    integer kernel_y_work;
    integer kernel_x_work;
    logic tap_range_error;

    always_comb begin
        extent_y = {1'b0, input_height} + {1'b0, darknet_padding_parameter};
        extent_x = {1'b0, input_width} + {1'b0, darknet_padding_parameter};
        output_height_work = 33'd0;
        output_width_work = 33'd0;
        output_y_step = 64'd0;
        output_x_step = 64'd0;
        source_y_work = 64'sd0;
        source_x_work = 64'sd0;
        channel_row_work = 96'd0;
        row_work = 96'd0;
        logical_offset_work = 96'd0;
        address_work = 97'd0;
        kernel_y_work = 0;
        kernel_x_work = 0;
        tap_range_error = 1'b0;

        output_height = 33'd0;
        output_width = 33'd0;
        tap_count = 4'd0;
        tap_valid_mask = 9'd0;
        error_code = 3'd0;
        origin_y = 64'sd0;
        origin_x = 64'sd0;
        for (tap_index = 0; tap_index < 9; tap_index = tap_index + 1) begin
            tap_address[tap_index] = 32'd0;
            tap_source_channel[tap_index] = 32'd0;
            tap_source_y[tap_index] = 64'sd0;
            tap_source_x[tap_index] = 64'sd0;
        end

        if (!(((kernel_height == 32'd2) && (kernel_width == 32'd2)) ||
              ((kernel_height == 32'd3) && (kernel_width == 32'd3))) ||
            (stride_y == 32'd0) || (stride_x == 32'd0) ||
            (input_channels == 32'd0) || (input_height == 32'd0) ||
            (input_width == 32'd0)) begin
            error_code = BAD_ARGUMENT;
        end else if ((extent_y < {1'b0, kernel_height}) ||
                     (extent_x < {1'b0, kernel_width})) begin
            error_code = BAD_ARGUMENT;
        end else begin
            if (stride_y == 32'd2) begin
                output_height_work =
                    ((extent_y - {1'b0, kernel_height}) >> 1) + 33'd1;
            end else begin
                output_height_work =
                    ((extent_y - {1'b0, kernel_height}) / {1'b0, stride_y}) + 33'd1;
            end
            if (stride_x == 32'd2) begin
                output_width_work =
                    ((extent_x - {1'b0, kernel_width}) >> 1) + 33'd1;
            end else begin
                output_width_work =
                    ((extent_x - {1'b0, kernel_width}) / {1'b0, stride_x}) + 33'd1;
            end
            output_height = output_height_work;
            output_width = output_width_work;

            if ((input_channel >= input_channels) ||
                ({1'b0, output_y} >= output_height_work) ||
                ({1'b0, output_x} >= output_width_work)) begin
                error_code = BAD_ARGUMENT;
            end else begin
                tap_count = (kernel_height == 32'd2) ? 4'd4 : 4'd9;
                origin_y = -$signed({32'd0, darknet_padding_parameter[31:1]});
                origin_x = -$signed({32'd0, darknet_padding_parameter[31:1]});
                if (stride_y == 32'd2) begin
                    output_y_step = {32'd0, output_y} << 1;
                end else begin
                    output_y_step = {32'd0, output_y} * {32'd0, stride_y};
                end
                if (stride_x == 32'd2) begin
                    output_x_step = {32'd0, output_x} << 1;
                end else begin
                    output_x_step = {32'd0, output_x} * {32'd0, stride_x};
                end
                source_y_work = origin_y + $signed(output_y_step);
                source_x_work = origin_x + $signed(output_x_step);

                for (tap_index = 0; tap_index < 9; tap_index = tap_index + 1) begin
                    if (tap_index < tap_count) begin
                        if (kernel_width == 32'd2) begin
                            case (tap_index)
                                0: begin kernel_y_work = 0; kernel_x_work = 0; end
                                1: begin kernel_y_work = 0; kernel_x_work = 1; end
                                2: begin kernel_y_work = 1; kernel_x_work = 0; end
                                3: begin kernel_y_work = 1; kernel_x_work = 1; end
                                default: begin kernel_y_work = 0; kernel_x_work = 0; end
                            endcase
                        end else begin
                            case (tap_index)
                                0: begin kernel_y_work = 0; kernel_x_work = 0; end
                                1: begin kernel_y_work = 0; kernel_x_work = 1; end
                                2: begin kernel_y_work = 0; kernel_x_work = 2; end
                                3: begin kernel_y_work = 1; kernel_x_work = 0; end
                                4: begin kernel_y_work = 1; kernel_x_work = 1; end
                                5: begin kernel_y_work = 1; kernel_x_work = 2; end
                                6: begin kernel_y_work = 2; kernel_x_work = 0; end
                                7: begin kernel_y_work = 2; kernel_x_work = 1; end
                                8: begin kernel_y_work = 2; kernel_x_work = 2; end
                                default: begin kernel_y_work = 0; kernel_x_work = 0; end
                            endcase
                        end
                        tap_source_channel[tap_index] = input_channel;
                        tap_source_y[tap_index] = source_y_work + kernel_y_work;
                        tap_source_x[tap_index] = source_x_work + kernel_x_work;

                        if ((tap_source_y[tap_index] >= 64'sd0) &&
                            (tap_source_y[tap_index] < $signed({32'd0, input_height})) &&
                            (tap_source_x[tap_index] >= 64'sd0) &&
                            (tap_source_x[tap_index] < $signed({32'd0, input_width}))) begin
                            tap_valid_mask[tap_index] = 1'b1;
                            channel_row_work =
                                {64'd0, input_channel} * {64'd0, input_height};
                            row_work = channel_row_work +
                                {64'd0, tap_source_y[tap_index][31:0]};
                            logical_offset_work = row_work * {64'd0, input_width} +
                                {64'd0, tap_source_x[tap_index][31:0]};
                            address_work = {65'd0, input_base_address} +
                                {1'b0, logical_offset_work};
                            if (address_work[96:32] != 65'd0) begin
                                tap_range_error = 1'b1;
                            end else begin
                                tap_address[tap_index] = address_work[31:0];
                            end
                        end
                    end
                end

                if (tap_range_error) begin
                    error_code = BAD_RANGE;
                    output_height = 33'd0;
                    output_width = 33'd0;
                    tap_count = 4'd0;
                    tap_valid_mask = 9'd0;
                    for (tap_index = 0; tap_index < 9; tap_index = tap_index + 1) begin
                        tap_address[tap_index] = 32'd0;
                        tap_source_channel[tap_index] = 32'd0;
                        tap_source_y[tap_index] = 64'sd0;
                        tap_source_x[tap_index] = 64'sd0;
                    end
                end
            end
        end

        if (error_code == BAD_ARGUMENT) begin
            output_height = 33'd0;
            output_width = 33'd0;
            tap_count = 4'd0;
            tap_valid_mask = 9'd0;
            for (tap_index = 0; tap_index < 9; tap_index = tap_index + 1) begin
                tap_address[tap_index] = 32'd0;
                tap_source_channel[tap_index] = 32'd0;
                tap_source_y[tap_index] = 64'sd0;
                tap_source_x[tap_index] = 64'sd0;
            end
        end
    end
endmodule
