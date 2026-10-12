// G0 tiny416 route 单输出元素：group 通道映射、NCHW 地址与 scale 重标定。
module s2b_route_query #(
    // 仅冻结network实例启用；默认保持原任意U32组合查询。
    parameter bit FROZEN_ROUTE_SHAPES = 1'b0
) (
    input  logic [31:0] source_count,
    input  logic [31:0] groups,
    input  logic [31:0] group_id,
    input  logic [31:0] output_channel,
    input  logic [31:0] output_y,
    input  logic [31:0] output_x,

    input  logic [31:0] source0_base_address,
    input  logic [31:0] source0_length_bytes,
    input  logic [31:0] source0_channels,
    input  logic [31:0] source0_height,
    input  logic [31:0] source0_width,
    input  logic [31:0] source0_channel_start,
    input  logic [31:0] source0_channel_end,
    input  logic [31:0] source0_multiplier_q31,
    input  logic signed [7:0] source0_value,

    input  logic [31:0] source1_base_address,
    input  logic [31:0] source1_length_bytes,
    input  logic [31:0] source1_channels,
    input  logic [31:0] source1_height,
    input  logic [31:0] source1_width,
    input  logic [31:0] source1_channel_start,
    input  logic [31:0] source1_channel_end,
    input  logic [31:0] source1_multiplier_q31,
    input  logic signed [7:0] source1_value,

    output logic [31:0] output_channels,
    output logic [31:0] output_height,
    output logic [31:0] output_width,
    output logic [31:0] source_index,
    output logic [31:0] source_channel,
    output logic [31:0] source_address,
    output logic signed [7:0] output_value,
    output logic [2:0] error_code
);
    localparam logic [2:0] OK = 3'd0;
    localparam logic [2:0] BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] BAD_RANGE = 3'd2;

    logic bad_argument;
    logic bad_range;
    logic [63:0] source0_shape_bytes;
    logic [63:0] source1_shape_bytes;
    logic [63:0] source0_plane_elements;
    logic [63:0] source1_plane_elements;
    logic [63:0] source0_object_end;
    logic [63:0] source1_object_end;
    logic [63:0] output_channels_wide;
    logic [63:0] expected_group_start;
    logic [63:0] expected_group_end;
    logic [31:0] selected_offset;
    logic [31:0] selected_address;
    logic [31:0] source0_selected_count;
    logic [31:0] source1_selected_count;
    logic [31:0] selected_multiplier;
    logic [31:0] selected_base_address;
    logic signed [7:0] selected_value;
    // 成功路径已排除 -128 并限制倍率，绝对值为 7 位，乘积可精确落在 39 位。
    logic [6:0] selected_magnitude;
    logic [38:0] scaled_product;
    logic [39:0] rounded_product;
    logic [8:0] rounded_magnitude;
    logic signed [8:0] scaled_signed;
    logic [31:0] selected_source_index;
    logic [31:0] selected_source_channel;

    // 完整tuple匹配得到H乘W空间平面；旧C乘H字段不能用作通道跨度。
    function automatic logic [31:0] frozen_spatial_plane_lookup(input logic [95:0] shape_key);
        begin
            frozen_spatial_plane_lookup = 32'd0;
            case (shape_key)
                96'h000000200000006800000068: frozen_spatial_plane_lookup = 32'd10816;
                96'h000000400000003400000034: frozen_spatial_plane_lookup = 32'd2704;
                96'h000000400000006800000068: frozen_spatial_plane_lookup = 32'd10816;
                96'h000000800000001A0000001A: frozen_spatial_plane_lookup = 32'd676;
                96'h000000800000003400000034: frozen_spatial_plane_lookup = 32'd2704;
                96'h000001000000000D0000000D: frozen_spatial_plane_lookup = 32'd169;
                96'h000001000000001A0000001A: frozen_spatial_plane_lookup = 32'd676;
                default: frozen_spatial_plane_lookup = 32'd0;
            endcase
        end
    endfunction
    logic [31:0] source0_spatial_plane;

    // 完整96位tuple匹配，避免低位别名；固定值分别为C乘H与C乘H乘W。
    function automatic logic [128:0] frozen_shape_lookup(input logic [95:0] shape_key);
        begin
            frozen_shape_lookup = 129'd0;
            case (shape_key)
                96'h000000200000006800000068: frozen_shape_lookup = {1'b1, 64'd3328, 64'd346112};
                96'h000000400000003400000034: frozen_shape_lookup = {1'b1, 64'd3328, 64'd173056};
                96'h000000400000006800000068: frozen_shape_lookup = {1'b1, 64'd6656, 64'd692224};
                96'h000000800000001A0000001A: frozen_shape_lookup = {1'b1, 64'd3328, 64'd86528};
                96'h000000800000003400000034: frozen_shape_lookup = {1'b1, 64'd6656, 64'd346112};
                96'h000001000000000D0000000D: frozen_shape_lookup = {1'b1, 64'd3328, 64'd43264};
                96'h000001000000001A0000001A: frozen_shape_lookup = {1'b1, 64'd6656, 64'd173056};
                default: frozen_shape_lookup = 129'd0;
            endcase
        end
    endfunction

    logic [128:0] source0_frozen_shape;
    logic [128:0] source1_frozen_shape;

    always_comb begin
        // 组合默认值保证非法输入无副作用，也避免推断锁存器。
        output_channels = 32'd0;
        output_height = 32'd0;
        output_width = 32'd0;
        source_index = 32'd0;
        source_channel = 32'd0;
        source_address = 32'd0;
        output_value = 8'sd0;
        error_code = OK;

        bad_argument = 1'b0;
        bad_range = 1'b0;
        source0_frozen_shape = 129'd0;
        source0_spatial_plane = 32'd0;
        source1_frozen_shape = 129'd0;
        source0_shape_bytes = 64'd0;
        source1_shape_bytes = 64'd0;
        source0_plane_elements = 64'd0;
        source1_plane_elements = 64'd0;
        source0_object_end = 64'd0;
        source1_object_end = 64'd0;
        output_channels_wide = 64'd0;
        expected_group_start = 64'd0;
        expected_group_end = 64'd0;
        selected_offset = 32'd0;
        selected_address = 32'd0;
        source0_selected_count = 32'd0;
        source1_selected_count = 32'd0;
        selected_multiplier = 32'd0;
        selected_base_address = 32'd0;
        selected_value = 8'sd0;
        selected_magnitude = 7'd0;
        scaled_product = 39'd0;
        rounded_product = 40'd0;
        rounded_magnitude = 9'd0;
        scaled_signed = 9'sd0;
        selected_source_index = 32'd0;
        selected_source_channel = 32'd0;

        if (!((source_count == 32'd1) || (source_count == 32'd2)) ||
            (groups == 32'd0) || (group_id >= groups) ||
            (source0_channels == 32'd0) || (source0_height == 32'd0) ||
            (source0_width == 32'd0) ||
            (source0_channel_start >= source0_channel_end) ||
            (source0_channel_end > source0_channels) ||
            (source0_multiplier_q31 == 32'd0) ||
            (source0_multiplier_q31 > 32'h8000_0000)) begin
            bad_argument = 1'b1;
        end

        if (source_count == 32'd2) begin
            if ((source1_channels == 32'd0) ||
                (source1_height == 32'd0) || (source1_width == 32'd0) ||
                (source1_height != source0_height) ||
                (source1_width != source0_width) ||
                (source1_channel_start >= source1_channel_end) ||
                (source1_channel_end > source1_channels) ||
                (source1_multiplier_q31 == 32'd0) ||
                (source1_multiplier_q31 > 32'h8000_0000)) begin
                bad_argument = 1'b1;
            end
        end

        if ((groups == 32'd1) &&
            ((source0_channel_start != 32'd0) ||
             (source0_channel_end != source0_channels))) begin
            bad_argument = 1'b1;
        end else if (groups == 32'd2) begin
            if ((source_count != 32'd1) || source0_channels[0]) begin
                bad_argument = 1'b1;
            end else begin
                expected_group_start = (group_id == 32'd1) ?
                    {32'd0, source0_channels[31:1]} : 64'd0;
                expected_group_end = expected_group_start +
                                     {33'd0, source0_channels[31:1]};
                if ((source0_channel_start != expected_group_start[31:0]) ||
                    (source0_channel_end != expected_group_end[31:0])) begin
                    bad_argument = 1'b1;
                end
            end
        end else if (groups > 32'd2) begin
            // 冻结tiny416的ROUTE只会产生1或2；通用多组语义保留在2A原件。
            bad_argument = 1'b1;
        end
        if ((source_count == 32'd2) &&
            ((source1_channel_start != 32'd0) ||
             (source1_channel_end != source1_channels) ||
             (groups != 32'd1))) begin
            bad_argument = 1'b1;
        end

        source0_selected_count = source0_channel_end - source0_channel_start;
        if (source_count == 32'd2) begin
            source1_selected_count = source1_channel_end - source1_channel_start;
        end
        output_channels_wide = {32'd0, source0_selected_count} +
                               {32'd0, source1_selected_count};
        if (output_channels_wide > 64'h0000_0000_FFFF_FFFF) begin
            bad_range = 1'b1;
        end
        if ((output_y >= source0_height) || (output_x >= source0_width) ||
            ({32'd0, output_channel} >= output_channels_wide)) begin
            bad_argument = 1'b1;
        end

        if (FROZEN_ROUTE_SHAPES) begin
            source0_frozen_shape = frozen_shape_lookup({source0_channels, source0_height, source0_width});
            source0_spatial_plane = frozen_spatial_plane_lookup({source0_channels, source0_height, source0_width});
            source0_plane_elements = source0_frozen_shape[127:64];
            source0_shape_bytes = source0_frozen_shape[63:0];
            if (!source0_frozen_shape[128]) begin
                // 私有非冻结tuple拒绝；公开backend可达性由独立G0/G1证明。
                bad_argument = 1'b1;
            end
        end else begin
            source0_plane_elements = {32'd0, source0_channels} *
                                     {32'd0, source0_height};
            if (source0_plane_elements > 64'h0000_0000_FFFF_FFFF) begin
                bad_range = 1'b1;
            end else begin
                source0_shape_bytes = source0_plane_elements *
                                      {32'd0, source0_width};
                if (source0_shape_bytes > 64'h0000_0000_FFFF_FFFF) begin
                    bad_range = 1'b1;
                end
            end
        end
        source0_object_end = {32'd0, source0_base_address} +
                             {32'd0, source0_length_bytes};
        if ((source0_length_bytes == 32'd0) ||
            ({32'd0, source0_length_bytes} < source0_shape_bytes) ||
            (source0_object_end > 64'h0000_0001_0000_0000)) begin
            bad_range = 1'b1;
        end

        if (source_count == 32'd2) begin
            if (FROZEN_ROUTE_SHAPES) begin
                source1_frozen_shape = frozen_shape_lookup({source1_channels, source1_height, source1_width});
                source1_plane_elements = source1_frozen_shape[127:64];
                source1_shape_bytes = source1_frozen_shape[63:0];
                if (!source1_frozen_shape[128]) begin
                    // 私有非冻结tuple拒绝；公开backend可达性由独立G0/G1证明。
                    bad_argument = 1'b1;
                end
            end else begin
                source1_plane_elements = {32'd0, source1_channels} *
                                         {32'd0, source1_height};
                if (source1_plane_elements > 64'h0000_0000_FFFF_FFFF) begin
                    bad_range = 1'b1;
                end else begin
                    source1_shape_bytes = source1_plane_elements *
                                          {32'd0, source1_width};
                    if (source1_shape_bytes > 64'h0000_0000_FFFF_FFFF) begin
                        bad_range = 1'b1;
                    end
                end
            end
            source1_object_end = {32'd0, source1_base_address} +
                                 {32'd0, source1_length_bytes};
            if ((source1_length_bytes == 32'd0) ||
                ({32'd0, source1_length_bytes} < source1_shape_bytes) ||
                (source1_object_end > 64'h0000_0001_0000_0000)) begin
                bad_range = 1'b1;
            end
        end

        if (output_channel < source0_selected_count) begin
            selected_source_index = 32'd0;
            selected_source_channel = source0_channel_start + output_channel;
            selected_value = source0_value;
            selected_multiplier = source0_multiplier_q31;
            selected_base_address = source0_base_address;
        end else if (source_count == 32'd2) begin
            selected_source_index = 32'd1;
            selected_source_channel = source1_channel_start +
                                     (output_channel - source0_selected_count);
            selected_value = source1_value;
            selected_multiplier = source1_multiplier_q31;
            selected_base_address = source1_base_address;
        end

        if (selected_value == -8'sd128) begin
            bad_argument = 1'b1;
        end

        // 前置shape、坐标、长度及对象端点检查保证成功路径地址精确落在32位。
        if (FROZEN_ROUTE_SHAPES) begin
            // 成功路径的完整tuple已验证；分配律在原32位模域内，不增加周期。
            selected_offset = selected_source_channel * source0_spatial_plane +
                              output_y * source0_width + output_x;
        end else begin
            selected_offset =
                ((selected_source_channel * source0_height) + output_y) *
                source0_width + output_x;
        end
        selected_address = selected_base_address + selected_offset;

        if (bad_argument) begin
            error_code = BAD_ARGUMENT;
        end else if (bad_range) begin
            error_code = BAD_RANGE;
        end else begin
            if (selected_value < 8'sd0) begin
                selected_magnitude = $unsigned(-selected_value);
            end else begin
                selected_magnitude = $unsigned(selected_value);
            end
            scaled_product = {32'd0, selected_magnitude} *
                             {7'd0, selected_multiplier};
            rounded_product = {1'b0, scaled_product} + 40'd1_073_741_824;
            rounded_magnitude = rounded_product[39:31];
            if (selected_value < 8'sd0) begin
                scaled_signed = -$signed(rounded_magnitude);
            end else begin
                scaled_signed = $signed(rounded_magnitude);
            end
            if (scaled_signed > 9'sd127) begin
                scaled_signed = 9'sd127;
            end else if (scaled_signed < -9'sd127) begin
                scaled_signed = -9'sd127;
            end

            output_channels = output_channels_wide[31:0];
            output_height = source0_height;
            output_width = source0_width;
            source_index = selected_source_index;
            source_channel = selected_source_channel;
            source_address = selected_address;
            output_value = scaled_signed[7:0];
        end
    end
endmodule
