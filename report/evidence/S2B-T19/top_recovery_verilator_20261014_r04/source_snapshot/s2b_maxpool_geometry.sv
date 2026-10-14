// 阶段 2A：计算单个 INT8 最大池化输出窗口的几何和 NCHW 字节地址。
module s2b_maxpool_geometry #(
    // 0 保留通用几何；1/2/3 分别专化冻结的 L9/L17/L25 池化形状。
    parameter integer FAST_FIXED_POOL_SHAPE = 0
) (
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
    localparam bit USE_FIXED_FAST_PATH =
        (FAST_FIXED_POOL_SHAPE == 1) ||
        (FAST_FIXED_POOL_SHAPE == 2) ||
        (FAST_FIXED_POOL_SHAPE == 3);
    localparam integer FAST_INPUT_CHANNELS = (FAST_FIXED_POOL_SHAPE == 1) ? 128 :
        (FAST_FIXED_POOL_SHAPE == 2) ? 256 :
        (FAST_FIXED_POOL_SHAPE == 3) ? 512 : 1;
    localparam integer FAST_INPUT_DIM = (FAST_FIXED_POOL_SHAPE == 1) ? 104 :
        (FAST_FIXED_POOL_SHAPE == 2) ? 52 :
        (FAST_FIXED_POOL_SHAPE == 3) ? 26 : 1;
    localparam integer FAST_OUTPUT_COORD_WIDTH = (FAST_FIXED_POOL_SHAPE == 1) ? 6 :
        (FAST_FIXED_POOL_SHAPE == 2) ? 5 :
        (FAST_FIXED_POOL_SHAPE == 3) ? 4 : 1;
    localparam integer FAST_CHANNEL_WIDTH = (FAST_FIXED_POOL_SHAPE == 1) ? 7 :
        (FAST_FIXED_POOL_SHAPE == 2) ? 8 :
        (FAST_FIXED_POOL_SHAPE == 3) ? 9 : 1;
    localparam integer FAST_OFFSET_WIDTH = (FAST_FIXED_POOL_SHAPE == 1) ? 21 :
        (FAST_FIXED_POOL_SHAPE == 2) ? 20 :
        (FAST_FIXED_POOL_SHAPE == 3) ? 19 : 1;
    localparam logic [FAST_OFFSET_WIDTH-1:0] FAST_PLANE_ELEMENTS =
        FAST_OFFSET_WIDTH'(FAST_INPUT_DIM * FAST_INPUT_DIM);
    localparam logic [FAST_OFFSET_WIDTH-1:0] FAST_ROW_WIDTH =
        FAST_OFFSET_WIDTH'(FAST_INPUT_DIM);

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
    logic [63:0] plane_work;
    logic [63:0] channel_offset_work;
    logic channel_offset_high;
    logic signed [63:0] row_y_work [0:2];
    logic [63:0] row_offset_work [0:2];
    logic [FAST_OFFSET_WIDTH-1:0] fast_channel_offset_work;
    logic [FAST_OFFSET_WIDTH-1:0] fast_row_offset_work [0:1];
    logic [FAST_OFFSET_WIDTH-1:0] fast_column_offset_work;
    logic [FAST_OFFSET_WIDTH-1:0] fast_logical_offset_work;
    logic [FAST_OUTPUT_COORD_WIDTH:0] fast_row_coordinate_work;
    logic [FAST_OUTPUT_COORD_WIDTH:0] fast_column_coordinate_work;
    logic [32:0] channel_row_sum_work;
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
        plane_work = 64'd0;
        channel_offset_work = 64'd0;
        fast_channel_offset_work = '0;
        fast_column_offset_work = '0;
        fast_logical_offset_work = '0;
        fast_row_coordinate_work = '0;
        fast_column_coordinate_work = '0;
        fast_row_offset_work[0] = '0;
        fast_row_offset_work[1] = '0;
        channel_offset_high = 1'b0;
        channel_row_sum_work = 33'd0;
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
        end else if (USE_FIXED_FAST_PATH &&
                     ((input_channels != FAST_INPUT_CHANNELS) ||
                      (input_height != FAST_INPUT_DIM) ||
                      (input_width != FAST_INPUT_DIM) ||
                      (kernel_height != 32'd2) || (kernel_width != 32'd2) ||
                      (stride_y != 32'd2) || (stride_x != 32'd2) ||
                      (darknet_padding_parameter != 32'd1))) begin
            // 专化参数只接受与冻结形状完全相符的端口常量。
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
                if (USE_FIXED_FAST_PATH) begin
                    // 完整U32坐标比较已通过，之后才取固定形状所需的窄低位。
                    fast_channel_offset_work =
                        {{(FAST_OFFSET_WIDTH-FAST_CHANNEL_WIDTH){1'b0}},
                         input_channel[FAST_CHANNEL_WIDTH-1:0]} * FAST_PLANE_ELEMENTS;
                    fast_row_coordinate_work =
                        ({1'b0, output_y[FAST_OUTPUT_COORD_WIDTH-1:0]} << 1);
                    fast_row_offset_work[0] =
                        FAST_OFFSET_WIDTH'(fast_row_coordinate_work) * FAST_ROW_WIDTH;
                    fast_row_offset_work[1] = fast_row_offset_work[0] + FAST_ROW_WIDTH;
                end else begin
                    // 通用形状保留完整宽度的通道平面与逐行地址运算。
                    plane_work = {32'd0, input_height} * {32'd0, input_width};
                    channel_offset_work = {32'd0, input_channel} * {32'd0, plane_work[31:0]};
                    channel_offset_high = ((input_channel != 32'd0) && (plane_work[63:32] != 32'd0)) ||
                        (channel_offset_work[63:32] != 32'd0);
                    // 高位只由实际有效tap消费，padding不提前拒绝。
                    for (row_index = 0; row_index < 3; row_index = row_index + 1) begin
                        row_y_work[row_index] = source_y_work + row_index;
                        if ((row_y_work[row_index] >= 64'sd0) &&
                            (row_y_work[row_index] < $signed({32'd0, input_height}))) begin
                            row_offset_work[row_index] =
                                {32'd0, row_y_work[row_index][31:0]} * {32'd0, input_width};
                        end
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
                            tap_valid_mask[tap_index] = 1'b1;
                            if (USE_FIXED_FAST_PATH) begin
                                fast_column_coordinate_work =
                                    ({1'b0, output_x[FAST_OUTPUT_COORD_WIDTH-1:0]} << 1);
                                if (kernel_x_work != 0) begin
                                    fast_column_coordinate_work = fast_column_coordinate_work + 1'b1;
                                end
                                fast_column_offset_work =
                                    FAST_OFFSET_WIDTH'(fast_column_coordinate_work);
                                fast_logical_offset_work = fast_channel_offset_work +
                                    fast_row_offset_work[kernel_y_work] + fast_column_offset_work;
                                logical_offset_work =
                                    {{(33-FAST_OFFSET_WIDTH){1'b0}}, fast_logical_offset_work};
                                selected_row_high = 1'b0;
                                selected_offset_high = 1'b0;
                            end else begin
                                // 通道、行、列各段保留进位，地址base使用33位相加。
                                channel_row_sum_work = {1'b0, channel_offset_work[31:0]} +
                                    {1'b0, row_offset_work[kernel_y_work][31:0]};
                                logical_offset_work = {1'b0, channel_row_sum_work[31:0]} +
                                    {1'b0, tap_source_x[tap_index][31:0]};
                                selected_row_high = channel_offset_high;
                                selected_offset_high = row_offset_work[kernel_y_work][63:32] != 32'd0;
                            end
                            address_work = {1'b0, input_base_address} +
                                {1'b0, logical_offset_work[31:0]};
                            if (selected_row_high || selected_offset_high ||
                                (!USE_FIXED_FAST_PATH && channel_row_sum_work[32]) ||
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
