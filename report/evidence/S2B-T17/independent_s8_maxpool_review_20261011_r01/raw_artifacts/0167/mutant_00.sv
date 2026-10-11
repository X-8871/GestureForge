// 阶段 2A：计算单个 INT8 最大池化输出窗口的几何和 NCHW 字节地址。
module s2b_maxpool_geometry (
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
    logic [32:0] output_y_step;
    logic [32:0] output_x_step;
    logic signed [63:0] source_y_work;
    logic signed [63:0] source_x_work;
    logic [63:0] channel_row_work;
    logic signed [63:0] row_y_work [0:2];
    logic [32:0] row_index_work [0:2];
    logic row_index_high [0:2];
    logic [63:0] row_offset_work [0:2];
    logic [32:0] logical_offset_work;
    logic [32:0] address_work;
    logic selected_row_high;
    logic selected_offset_high;
    integer tap_index;
    integer row_index;
    integer kernel_y_work;
    integer kernel_x_work;
    logic tap_range_error;

    always_comb begin
        extent_y = {1'b0, input_height} + {1'b0, darknet_padding_parameter};
        extent_x = {1'b0, input_width} + {1'b0, darknet_padding_parameter};
        output_height_work = 33'd0;
        output_width_work = 33'd0;
        output_y_step = 33'd0;
        output_x_step = 33'd0;
        source_y_work = 64'sd0;
        source_x_work = 64'sd0;
        channel_row_work = 64'd0;
        logical_offset_work = 33'd0;
        address_work = 33'd0;
        selected_row_high = 1'b0;
        selected_offset_high = 1'b0;
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
        for (row_index = 0; row_index < 3; row_index = row_index + 1) begin
            row_y_work[row_index] = 64'sd0;
            row_index_work[row_index] = 33'd0;
            row_index_high[row_index] = 1'b0;
            row_offset_work[row_index] = 64'd0;
        end
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
                // 坐标合法时，坐标乘步长不大于 extent-kernel，33 位足够。
                if (stride_y == 32'd2) begin
                    output_y_step = {1'b0, output_y} << 1;
                end else begin
                    output_y_step = {1'b0, output_y} * {1'b0, stride_y};
                end
                if (stride_x == 32'd2) begin
                    output_x_step = {1'b0, output_x} << 1;
                end else begin
                    output_x_step = {1'b0, output_x} * {1'b0, stride_x};
                end
                source_y_work = origin_y + $signed({31'd0, output_y_step});
                source_x_work = origin_x + $signed({31'd0, output_x_step});
                // 合法通道和行坐标保证 channel*height+source_y 小于 2^64。
                channel_row_work = {32'd0, input_channel} * {32'd0, input_height};
                // 每行低32位和进位分别保留；高位只由实际有效tap消费。
                // 正width保证行高位非零时完整地址必超UINT32，不能提前拒绝padding行。
                for (row_index = 0; row_index < 3; row_index = row_index + 1) begin
                    row_y_work[row_index] = source_y_work + row_index;
                    if ((row_y_work[row_index] >= 64'sd0) &&
                        (row_y_work[row_index] < $signed({32'd0, input_height}))) begin
                        row_index_work[row_index] = {1'b0, channel_row_work[31:0]} +
                            {1'b0, row_y_work[row_index][31:0]};
                        row_index_high[row_index] =
                            (channel_row_work[63:32] != 32'd0) || row_index_work[row_index][32];
                        row_offset_work[row_index] =
                            {32'd0, row_index_work[row_index][31:0]} * {32'd0, input_width};
                    end
                end

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
                            tap_valid_mask[tap_index] = 1'b0;
                            // 行偏移、列和base均非负；每段高位或进位保留完整越界语义。
                            logical_offset_work = {1'b0, row_offset_work[kernel_y_work][31:0]} +
                                {1'b0, tap_source_x[tap_index][31:0]};
                            selected_row_high = row_index_high[kernel_y_work];
                            selected_offset_high = row_offset_work[kernel_y_work][63:32] != 32'd0;
                            address_work = {1'b0, input_base_address} +
                                {1'b0, logical_offset_work[31:0]};
                            if (selected_row_high || selected_offset_high ||
                                logical_offset_work[32] || address_work[32]) begin
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
