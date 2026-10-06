// 阶段 2A：对 NCHW INT8 nearest-repeat 上采样执行单点查询和数值复制。
module int8_upsample_query (
    input  logic [31:0] input_base_address,
    input  logic [31:0] input_channels,
    input  logic [31:0] input_height,
    input  logic [31:0] input_width,
    input  logic [31:0] stride,
    input  logic [31:0] input_channel,
    input  logic [31:0] output_y,
    input  logic [31:0] output_x,
    // 当前查询通道的紧凑行优先平面，byte 0 位于最低 8 位。
    input  logic [1351:0] source_plane,
    output logic [63:0] output_height,
    output logic [63:0] output_width,
    output logic [31:0] source_channel,
    output logic [31:0] source_y,
    output logic [31:0] source_x,
    output logic [31:0] source_address,
    output logic signed [7:0] output_value,
    // 成功为 0；非法参数或坐标为 BAD_ARGUMENT(1)，uint32 地址溢出为 BAD_RANGE(2)。
    output logic [2:0] error_code
);
    localparam logic [2:0] BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] BAD_RANGE = 3'd2;
    localparam logic [31:0] MAX_PLANE_DIMENSION = 32'd13;

    logic [63:0] output_height_work;
    logic [63:0] output_width_work;
    logic [7:0] plane_elements_work;
    logic [7:0] plane_index_work;
    logic [39:0] byte_offset_work;
    logic [40:0] address_work;

    always_comb begin
        output_height_work = 64'd0;
        output_width_work = 64'd0;
        plane_elements_work = 8'd0;
        plane_index_work = 8'd0;
        byte_offset_work = 40'd0;
        address_work = 41'd0;

        output_height = 64'd0;
        output_width = 64'd0;
        source_channel = 32'd0;
        source_y = 32'd0;
        source_x = 32'd0;
        source_address = 32'd0;
        output_value = 8'sd0;
        error_code = 3'd0;

        if ((input_channels == 32'd0) || (input_height == 32'd0) ||
            (input_width == 32'd0) || (stride == 32'd0) ||
            (input_height > MAX_PLANE_DIMENSION) ||
            (input_width > MAX_PLANE_DIMENSION)) begin
            error_code = BAD_ARGUMENT;
        end else begin
            // 步长为 2 时乘法可精确改为移位；其他合法步长保留通用乘法。
            if (stride == 32'd2) begin
                output_height_work = {32'd0, input_height} << 1;
                output_width_work = {32'd0, input_width} << 1;
            end else begin
                output_height_work = {32'd0, input_height} * {32'd0, stride};
                output_width_work = {32'd0, input_width} * {32'd0, stride};
            end
            output_height = output_height_work;
            output_width = output_width_work;

            if ((input_channel >= input_channels) ||
                ({32'd0, output_y} >= output_height_work) ||
                ({32'd0, output_x} >= output_width_work)) begin
                error_code = BAD_ARGUMENT;
            end else begin
                source_channel = input_channel;
                // 步长为 2 时来源坐标就是输出坐标去掉最低位。
                if (stride == 32'd2) begin
                    source_y = {1'b0, output_y[31:1]};
                    source_x = {1'b0, output_x[31:1]};
                end else begin
                    source_y = output_y / stride;
                    source_x = output_x / stride;
                end
                // 边长已限制在 1 到 13，紧凑平面与通道地址可由窄位宽精确表示。
                plane_elements_work =
                    {4'd0, input_height[3:0]} * {4'd0, input_width[3:0]};
                plane_index_work =
                    ({4'd0, source_y[3:0]} * {4'd0, input_width[3:0]}) +
                    {4'd0, source_x[3:0]};
                byte_offset_work =
                    ({8'd0, input_channel} * {32'd0, plane_elements_work}) +
                    {32'd0, plane_index_work};
                address_work = {9'd0, input_base_address} +
                               {1'b0, byte_offset_work};

                if (address_work[40:32] != 9'd0) begin
                    error_code = BAD_RANGE;
                end else begin
                    source_address = address_work[31:0];
                    output_value = $signed(
                        source_plane[{plane_index_work, 3'b000} +: 8]
                    );
                end
            end
        end

        if (error_code != 3'd0) begin
            output_height = 64'd0;
            output_width = 64'd0;
            source_channel = 32'd0;
            source_y = 32'd0;
            source_x = 32'd0;
            source_address = 32'd0;
            output_value = 8'sd0;
        end
    end
endmodule
