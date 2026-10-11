// S2A-T66：以 8×8 空间 tile 和 8 个输出通道并行完成一个卷积层。
module s2b_conv_tile_engine (
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
    import s2a_network_descriptor_pkg::*;

    localparam logic [2:0] NONE = 3'd0;
    localparam logic [2:0] BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] BAD_RANGE = 3'd2;
    localparam logic [2:0] BAD_LENGTH = 3'd3;
    localparam logic [2:0] INTERNAL = 3'd6;
    localparam logic [2:0] ACCUMULATOR_OVERFLOW = 3'd7;
    localparam integer TILE_EDGE = 8;
    localparam integer LANE_COUNT = 8;
    localparam integer MAX_FEATURE_PATCH_BYTES = 51200;
    localparam integer MAX_WEIGHT_GROUP_BYTES = 36864;
    localparam integer MAX_WEIGHT_REDUCTION_COUNT = 4608;
    localparam integer OUTPUT_BLOCK_BYTES = 512;

    typedef enum logic [4:0] {
        ST_IDLE,
        ST_VALIDATE,
        ST_TILE_PREP,
        ST_FEATURE_SCAN,
        ST_FEATURE_REQUEST,
        ST_FEATURE_RESPONSE,
        ST_WEIGHT_PREP,
        ST_WEIGHT_SCAN,
        ST_WEIGHT_REQUEST,
        ST_WEIGHT_RESPONSE,
        ST_MQ_PREFETCH,
        ST_COMPUTE_PREP,
        ST_COMPUTE_POINT_PREP,
        ST_COMPUTE,
        ST_COMPUTE_REQUANT,
        ST_OUTPUT_SCAN,
        ST_OUTPUT_REQUEST,
        ST_OUTPUT_RESPONSE,
        ST_ADVANCE,
        ST_RESULT
    } state_t;

    state_t state;

    logic [31:0] layer_index_latched;
    logic [31:0] weight_layer_index_latched;
    logic [31:0] input_base_latched;
    logic [31:0] input_length_latched;
    logic [31:0] input_batch_count_latched;
    logic [31:0] input_channels_latched;
    logic [31:0] input_height_latched;
    logic [31:0] input_width_latched;
    logic [31:0] output_base_latched;
    logic [31:0] output_length_latched;
    logic [31:0] output_batch_count_latched;
    logic [31:0] output_channels_latched;
    logic [31:0] output_height_latched;
    logic [31:0] output_width_latched;
    logic [31:0] kernel_height_latched;
    logic [31:0] kernel_width_latched;
    logic [31:0] stride_y_latched;
    logic [31:0] stride_x_latched;
    logic [31:0] pad_left_latched;
    logic [31:0] pad_right_latched;
    logic [31:0] pad_top_latched;
    logic [31:0] pad_bottom_latched;
    logic [31:0] groups_latched;
    logic signed [31:0] padding_latched;
    logic [31:0] weight_package_base_latched;
    logic [31:0] weight_package_length_latched;
    logic [31:0] quantized_weight_offset_latched;
    logic [31:0] quantized_weight_bytes_latched;
    logic [31:0] output_batch_latched;
    logic [1:0] activation_mode_latched;

    logic signed [7:0] feature_patch [0:MAX_FEATURE_PATCH_BYTES-1];
    logic signed [7:0] output_block [0:OUTPUT_BLOCK_BYTES-1];
    logic signed [31:0] lane_accumulator [0:LANE_COUNT-1];
    logic signed [7:0] feature_read_data;
    logic feature_read_in_bounds;
    logic signed [7:0] weight_read_byte [0:LANE_COUNT-1];

    logic [31:0] reduction_count_latched;
    logic [31:0] output_group_base;
    logic [31:0] tile_start_y;
    logic [31:0] tile_start_x;
    logic [31:0] tile_height;
    logic [31:0] tile_width;
    logic [31:0] patch_height;
    logic [31:0] patch_width;
    logic [31:0] patch_byte_count;
    logic [31:0] tile_point_count;
    logic [31:0] group_lane_count;
    logic [31:0] feature_scan_index;
    logic [31:0] weight_lane_index;
    logic [31:0] weight_reduction_index;
    logic [31:0] compute_point_index;
    logic [31:0] compute_point_scan_y;
    logic [31:0] compute_point_scan_x;
    logic [31:0] compute_reduction_index;
    logic [31:0] output_lane_index;
    logic [31:0] output_point_index;
    logic [31:0] request_address_latched;
    logic [3:0] request_strobe_latched;
    logic request_write_latched;
    logic [31:0] request_wdata_latched;
    logic [31:0] output_address_latched;
    logic [7:0] output_value_latched;
    logic [2:0] result_error_latched;

    logic [127:0] input_elements_wide;
    logic [127:0] output_elements_wide;
    logic [127:0] expected_weight_bytes_wide;
    logic [127:0] reduction_count_wide;
    logic [63:0] input_element_plane;
    logic [63:0] output_element_plane;
    logic [63:0] input_element_product;
    logic [63:0] output_element_product;
    logic [25:0] reduction_plane_narrow;
    logic [25:0] reduction_count_narrow;
    logic [44:0] expected_weight_bytes_narrow;
    logic reduction_count_bad;
    logic [127:0] input_end_wide;
    logic [127:0] output_end_wide;
    logic [127:0] weight_package_end_wide;
    logic [127:0] quantized_weight_end_wide;
    logic [63:0] output_height_numerator;
    logic [63:0] output_width_numerator;
    logic [63:0] output_height_shape_span;
    logic [63:0] output_width_shape_span;
    logic [63:0] output_height_shape_product;
    logic [63:0] output_width_shape_product;
    logic [63:0] output_height_span_plus_stride;
    logic [63:0] output_width_span_plus_stride;
    logic [2:0] full_tile_patch_delta_y;
    logic [2:0] full_tile_patch_delta_x;
    logic [18:0] full_tile_patch_height_narrow;
    logic [18:0] full_tile_patch_width_narrow;
    logic [31:0] full_tile_patch_plane_narrow;
    logic [28:0] full_tile_patch_bytes_narrow;
    logic full_tile_patch_height_bad;
    logic full_tile_patch_width_bad;
    logic full_tile_patch_bad;
    logic validation_ok;
    logic [2:0] validation_error;

    logic [63:0] patch_plane_bytes;
    logic [31:0] feature_scan_channel;
    logic [31:0] feature_scan_y;
    logic [31:0] feature_scan_x;
    logic feature_scan_advance;
    logic signed [63:0] feature_input_y;
    logic signed [63:0] feature_input_x;
    logic feature_scan_in_bounds;
    logic [63:0] feature_geometry_plane;
    logic [63:0] feature_channel_plane_offset;
    logic [63:0] feature_row_offset;
    logic [63:0] feature_source_offset;
    logic [63:0] feature_source_address_wide;

    logic [31:0] current_weight_output_channel;
    logic [63:0] weight_source_address_wide;

    logic [31:0] compute_kernel_area;
    logic [31:0] compute_input_channel;
    logic [31:0] compute_kernel_y;
    logic [31:0] compute_kernel_x;
    logic [31:0] compute_next_input_channel;
    logic [31:0] compute_next_kernel_y;
    logic [31:0] compute_next_kernel_x;
    logic [31:0] compute_next_reduction_index;
    logic [31:0] compute_read_point_y;
    logic [31:0] compute_read_point_x;
    logic [31:0] compute_read_input_channel;
    logic [31:0] compute_read_kernel_y;
    logic [31:0] compute_read_kernel_x;
    logic [31:0] compute_read_reduction_index;
    logic signed [63:0] compute_read_input_y;
    logic signed [63:0] compute_read_input_x;
    logic compute_read_tap_in_bounds;
    logic [63:0] compute_read_feature_index_wide;
    logic [31:0] compute_read_feature_index;
    logic compute_read_enable;
    logic signed [7:0] compute_feature_byte [0:LANE_COUNT-1];
    logic signed [7:0] compute_weight_byte [0:LANE_COUNT-1];
    logic signed [15:0] compute_product [0:LANE_COUNT-1];
    logic signed [32:0] compute_sum [0:LANE_COUNT-1];
    logic compute_bad_argument;
    logic compute_overflow;

    logic [31:0] mq_prefetch_lane;
    logic [31:0] mq_prefetch_index;
    logic [79:0] mq_prefetch_parameter;
    logic signed [31:0] mq_prefetch_bias;
    logic mq_prefetch_invalid;
    logic [79:0] lane_mq_parameter [0:LANE_COUNT-1];
    logic signed [31:0] lane_bias [0:LANE_COUNT-1];
    logic [31:0] requant_lane_index;
    logic [79:0] requant_parameter;
    logic signed [31:0] requant_accumulator;
    logic [31:0] requant_multiplier;
    logic [31:0] requant_q_shift;
    logic [31:0] requant_magnitude;
    logic [63:0] requant_product;
    logic [63:0] requant_rounding_add;
    logic [63:0] requant_rounded_magnitude;
    logic signed [7:0] requantized_value;

    logic [31:0] output_global_y;
    logic [31:0] output_global_x;
    logic [31:0] output_point_scan_y;
    logic [31:0] output_point_scan_x;
    logic [31:0] output_channel_current;
    logic [63:0] output_geometry_plane;
    logic [63:0] output_channel_plane_offset;
    logic [63:0] output_row_offset;
    logic [63:0] output_byte_offset_wide;
    logic [63:0] output_address_wide;
    logic [2:0] mapped_response_error;
    logic [1:0] request_byte_lane;
    integer comb_lane;
    integer seq_lane;

    always_comb begin
        // 首分支已逐因子拒绝零；长度分支只消费正数乘积。
        // 前两因子精确64位，高32位非零必超UINT32；否则再精确乘第三因子。
        input_element_plane = {32'd0, input_channels_latched} * {32'd0, input_height_latched};
        output_element_plane = {32'd0, output_channels_latched} * {32'd0, output_height_latched};
        input_element_product = {32'd0, input_element_plane[31:0]} * {32'd0, input_width_latched};
        output_element_product = {32'd0, output_element_plane[31:0]} * {32'd0, output_width_latched};
        input_elements_wide = {64'd0, input_element_product};
        output_elements_wide = {64'd0, output_element_product};

        // 正C/KH/KW的R<=4608蕴含每个因子及C*KH均<=4608；低位截断另有拒绝保护。
        reduction_plane_narrow = {13'd0, input_channels_latched[12:0]} *
                                 {13'd0, kernel_height_latched[12:0]};
        reduction_count_narrow = {13'd0, reduction_plane_narrow[12:0]} *
                                 {13'd0, kernel_width_latched[12:0]};
        reduction_count_bad = (input_channels_latched > 32'd4608) ||
            (kernel_height_latched > 32'd4608) || (kernel_width_latched > 32'd4608) ||
            (reduction_plane_narrow > 26'd4608) || (reduction_count_narrow > 26'd4608);
        reduction_count_wide = {102'd0, reduction_count_narrow};
        // 长度分支已保证R<=4608，故OC32*R13的45位结果精确；不提前消费MQ限制。
        expected_weight_bytes_narrow = {13'd0, output_channels_latched} *
                                       {32'd0, reduction_count_narrow[12:0]};
        expected_weight_bytes_wide = {83'd0, expected_weight_bytes_narrow};
        input_end_wide = {96'd0, input_base_latched} + {96'd0, input_length_latched};
        output_end_wide = {96'd0, output_base_latched} + {96'd0, output_length_latched};
        weight_package_end_wide = {96'd0, weight_package_base_latched} +
                                  {96'd0, weight_package_length_latched};
        quantized_weight_end_wide = {96'd0, quantized_weight_offset_latched} +
                                    {96'd0, quantized_weight_bytes_latched};
        output_height_numerator = {32'd0, input_height_latched} +
                                  {32'd0, pad_top_latched} + {32'd0, pad_bottom_latched};
        output_width_numerator = {32'd0, input_width_latched} +
                                 {32'd0, pad_left_latched} + {32'd0, pad_right_latched};
        output_height_shape_span = output_height_numerator - {32'd0, kernel_height_latched};
        output_width_shape_span = output_width_numerator - {32'd0, kernel_width_latched};
        output_height_shape_product = {32'd0, output_height_latched} * {32'd0, stride_y_latched};
        output_width_shape_product = {32'd0, output_width_latched} * {32'd0, stride_x_latched};
        output_height_span_plus_stride = output_height_shape_span + {32'd0, stride_y_latched};
        output_width_span_plus_stride = output_width_shape_span + {32'd0, stride_x_latched};

        // 首分支保证C、KH、KW非零且乘积不超过4608，范围分支才消费此判据。
        // D为0时stride不参与patch；非零D必须另查stride高位，不能截断后放行。
        full_tile_patch_delta_y = output_height_latched == 32'd0 ? 3'd0 :
            (output_height_latched < TILE_EDGE ? output_height_latched[2:0] - 3'd1 : 3'd7);
        full_tile_patch_delta_x = output_width_latched == 32'd0 ? 3'd0 :
            (output_width_latched < TILE_EDGE ? output_width_latched[2:0] - 3'd1 : 3'd7);
        full_tile_patch_height_narrow =
            ({16'd0, full_tile_patch_delta_y} * {3'd0, stride_y_latched[15:0]}) +
            {6'd0, kernel_height_latched[12:0]};
        full_tile_patch_width_narrow =
            ({16'd0, full_tile_patch_delta_x} * {3'd0, stride_x_latched[15:0]}) +
            {6'd0, kernel_width_latched[12:0]};
        full_tile_patch_height_bad =
            ((full_tile_patch_delta_y != 3'd0) && (stride_y_latched[31:16] != 16'd0)) ||
            (full_tile_patch_height_narrow[18:16] != 3'd0) ||
            (full_tile_patch_height_narrow[15:0] > 16'd51200);
        full_tile_patch_width_bad =
            ((full_tile_patch_delta_x != 3'd0) && (stride_x_latched[31:16] != 16'd0)) ||
            (full_tile_patch_width_narrow[18:16] != 3'd0) ||
            (full_tile_patch_width_narrow[15:0] > 16'd51200);
        full_tile_patch_plane_narrow =
            {16'd0, full_tile_patch_height_narrow[15:0]} *
            {16'd0, full_tile_patch_width_narrow[15:0]};
        full_tile_patch_bytes_narrow =
            {13'd0, full_tile_patch_plane_narrow[15:0]} *
            {16'd0, input_channels_latched[12:0]};
        full_tile_patch_bad = full_tile_patch_height_bad || full_tile_patch_width_bad ||
            (full_tile_patch_plane_narrow[31:16] != 16'd0) ||
            (full_tile_patch_bytes_narrow > 29'd51200);

        validation_ok = 1'b0;
        validation_error = BAD_ARGUMENT;
        if (!buffer_owner_pl ||
            (activation_mode_latched > 2'd1) ||
            (input_batch_count_latched != 32'd1) ||
            (output_batch_count_latched != 32'd1) ||
            (output_batch_latched != 32'd0) ||
            (input_channels_latched == 32'd0) ||
            (input_height_latched == 32'd0) ||
            (input_width_latched == 32'd0) ||
            (output_channels_latched == 32'd0) ||
            (output_height_latched == 32'd0) ||
            (output_width_latched == 32'd0) ||
            (kernel_height_latched == 32'd0) ||
            (kernel_width_latched == 32'd0) ||
            (stride_y_latched == 32'd0) ||
            (stride_x_latched == 32'd0) ||
            (groups_latched != 32'd1) ||
            (padding_latched != 32'sd0) ||
            reduction_count_bad ||
            (layer_index_latched >= S2A_LAYER_COUNT) ||
            ((layer_index_latched < S2A_LAYER_COUNT) &&
             (S2A_OP[layer_index_latched] != S2A_OP_CONV)) ||
            (layer_index_latched != weight_layer_index_latched)) begin
            if ((layer_index_latched != weight_layer_index_latched) ||
                (layer_index_latched >= S2A_LAYER_COUNT)) begin
                validation_error = BAD_RANGE;
            end else begin
                validation_error = BAD_ARGUMENT;
            end
        end else if ((input_element_plane[63:32] != 32'd0) ||
                     (input_element_product[63:32] != 32'd0) ||
                     (input_length_latched != input_elements_wide[31:0]) ||
                     (output_element_plane[63:32] != 32'd0) ||
                     (output_element_product[63:32] != 32'd0) ||
                     (output_length_latched != output_elements_wide[31:0]) ||
                     (expected_weight_bytes_narrow[44:32] != 13'd0) ||
                     (quantized_weight_bytes_latched != expected_weight_bytes_wide[31:0])) begin
            validation_error = BAD_LENGTH;
        end else if ((input_end_wide > 128'h0000_0000_0000_0001_0000_0000) ||
                     (output_end_wide > 128'h0000_0000_0000_0001_0000_0000) ||
                     (weight_package_end_wide > 128'h0000_0000_0000_0001_0000_0000) ||
                     (weight_package_length_latched == 32'd0) ||
                     (quantized_weight_end_wide > {96'd0, weight_package_length_latched}) ||
                     (S2A_T23_MQ_CHANNEL_COUNT[layer_index_latched] != output_channels_latched) ||
                     ({16'd0, S2A_T23_MQ_BASE[layer_index_latched]} +
                      {96'd0, output_channels_latched} > 128'd3164) ||
                     full_tile_patch_bad) begin
            validation_error = BAD_RANGE;
        end else if ((output_height_numerator < {32'd0, kernel_height_latched}) ||
                     (output_width_numerator < {32'd0, kernel_width_latched}) ||
                     (output_height_shape_product <= output_height_shape_span) ||
                     (output_height_shape_product > output_height_span_plus_stride) ||
                     (output_width_shape_product <= output_width_shape_span) ||
                     (output_width_shape_product > output_width_span_plus_stride)) begin
            validation_error = BAD_ARGUMENT;
        end else begin
            validation_ok = 1'b1;
            validation_error = NONE;
        end

        patch_plane_bytes = {32'd0, patch_height} * {32'd0, patch_width};
        feature_input_y = 64'sd0;
        feature_input_x = 64'sd0;
        feature_scan_in_bounds = 1'b0;
        feature_scan_advance = 1'b0;
        feature_geometry_plane = 64'd0;
        feature_channel_plane_offset = 64'd0;
        feature_row_offset = 64'd0;
        feature_source_offset = 64'd0;
        feature_source_address_wide = 64'd0;
        if ((patch_plane_bytes != 64'd0) && (patch_width != 32'd0)) begin
            feature_input_y =
                $signed({32'd0, tile_start_y} * {32'd0, stride_y_latched}) +
                $signed({32'd0, feature_scan_y}) - $signed({32'd0, pad_top_latched});
            feature_input_x =
                $signed({32'd0, tile_start_x} * {32'd0, stride_x_latched}) +
                $signed({32'd0, feature_scan_x}) - $signed({32'd0, pad_left_latched});
            feature_scan_in_bounds =
                (feature_input_y >= 64'sd0) &&
                (feature_input_y < $signed({32'd0, input_height_latched})) &&
                (feature_input_x >= 64'sd0) &&
                (feature_input_x < $signed({32'd0, input_width_latched}));
            if (feature_scan_in_bounds) begin
                // 原signed bounds保证Y高32为零；只在消费分支用精确32乘32行偏移。
                feature_geometry_plane = {32'd0, input_height_latched} * {32'd0, input_width_latched};
                feature_channel_plane_offset = {32'd0, feature_scan_channel} * feature_geometry_plane;
                feature_row_offset = {32'd0, feature_input_y[31:0]} * {32'd0, input_width_latched};
                feature_source_offset = feature_channel_plane_offset + feature_row_offset +
                                        feature_input_x[63:0];
                feature_source_address_wide = {32'd0, input_base_latched} + feature_source_offset;
            end
        end

        current_weight_output_channel = output_group_base + weight_lane_index;
        weight_source_address_wide = {32'd0, weight_package_base_latched} +
            {32'd0, quantized_weight_offset_latched} +
            ({32'd0, current_weight_output_channel} * {32'd0, reduction_count_latched}) +
            {32'd0, weight_reduction_index};

        compute_kernel_area = kernel_height_latched * kernel_width_latched;
        compute_next_input_channel = compute_input_channel;
        compute_next_kernel_y = compute_kernel_y;
        compute_next_kernel_x = compute_kernel_x;
        compute_next_reduction_index = compute_reduction_index + 32'd1;
        if (compute_kernel_x + 32'd1 >= kernel_width_latched) begin
            compute_next_kernel_x = 32'd0;
            if (compute_kernel_y + 32'd1 >= kernel_height_latched) begin
                compute_next_kernel_y = 32'd0;
                compute_next_input_channel = compute_input_channel + 32'd1;
            end else begin
                compute_next_kernel_y = compute_kernel_y + 32'd1;
            end
        end else begin
            compute_next_kernel_x = compute_kernel_x + 32'd1;
        end
        compute_read_point_y = compute_point_scan_y;
        compute_read_point_x = compute_point_scan_x;
        compute_read_input_channel = compute_input_channel;
        compute_read_kernel_y = compute_kernel_y;
        compute_read_kernel_x = compute_kernel_x;
        compute_read_reduction_index = compute_reduction_index;
        compute_read_input_y = 64'sd0;
        compute_read_input_x = 64'sd0;
        compute_read_tap_in_bounds = 1'b0;
        compute_read_feature_index_wide = 64'd0;
        compute_read_feature_index = 32'd0;
        compute_read_enable = 1'b0;
        compute_bad_argument = 1'b0;
        compute_overflow = 1'b0;
        for (comb_lane = 0; comb_lane < LANE_COUNT; comb_lane = comb_lane + 1) begin
            compute_feature_byte[comb_lane] = 8'sd0;
            compute_weight_byte[comb_lane] = 8'sd0;
            compute_product[comb_lane] = 16'sd0;
            compute_sum[comb_lane] = 33'sd0;
            if (comb_lane < group_lane_count) begin
                compute_feature_byte[comb_lane] = feature_read_in_bounds ? feature_read_data : 8'sd0;
                compute_weight_byte[comb_lane] = weight_read_byte[comb_lane];
                compute_product[comb_lane] =
                    $signed({{8{compute_feature_byte[comb_lane][7]}}, compute_feature_byte[comb_lane]}) *
                    $signed({{8{compute_weight_byte[comb_lane][7]}}, compute_weight_byte[comb_lane]});
                compute_sum[comb_lane] = $signed({lane_accumulator[comb_lane][31], lane_accumulator[comb_lane]}) +
                    $signed({{17{compute_product[comb_lane][15]}}, compute_product[comb_lane]});
                if (feature_read_in_bounds &&
                    ((compute_feature_byte[comb_lane] == -8'sd128) ||
                     (compute_weight_byte[comb_lane] == -8'sd128))) begin
                    compute_bad_argument = 1'b1;
                end
                if (compute_sum[comb_lane][32] != compute_sum[comb_lane][31]) begin
                    compute_overflow = 1'b1;
                end
            end
        end
        if ((state == ST_COMPUTE_PREP) || (state == ST_COMPUTE_POINT_PREP)) begin
            compute_read_point_y = compute_point_scan_y;
            compute_read_point_x = compute_point_scan_x;
            compute_read_input_channel = 32'd0;
            compute_read_kernel_y = 32'd0;
            compute_read_kernel_x = 32'd0;
            compute_read_reduction_index = 32'd0;
            compute_read_enable = 1'b1;
        end else if (state == ST_COMPUTE) begin
            if ((compute_reduction_index + 32'd1 < reduction_count_latched) &&
                !compute_bad_argument && !compute_overflow) begin
                compute_read_point_y = compute_point_scan_y;
                compute_read_point_x = compute_point_scan_x;
                compute_read_input_channel = compute_next_input_channel;
                compute_read_kernel_y = compute_next_kernel_y;
                compute_read_kernel_x = compute_next_kernel_x;
                compute_read_reduction_index = compute_next_reduction_index;
                compute_read_enable = 1'b1;
            end
        end
        if ((compute_kernel_area != 32'd0) && (tile_width != 32'd0)) begin
            compute_read_input_y =
                $signed({32'd0, tile_start_y} * {32'd0, stride_y_latched}) +
                $signed({32'd0, compute_read_point_y} * {32'd0, stride_y_latched}) +
                $signed({32'd0, compute_read_kernel_y}) - $signed({32'd0, pad_top_latched});
            compute_read_input_x =
                $signed({32'd0, tile_start_x} * {32'd0, stride_x_latched}) +
                $signed({32'd0, compute_read_point_x} * {32'd0, stride_x_latched}) +
                $signed({32'd0, compute_read_kernel_x}) - $signed({32'd0, pad_left_latched});
            compute_read_tap_in_bounds =
                (compute_read_input_y >= 64'sd0) &&
                (compute_read_input_y < $signed({32'd0, input_height_latched})) &&
                (compute_read_input_x >= 64'sd0) &&
                (compute_read_input_x < $signed({32'd0, input_width_latched}));
            compute_read_feature_index_wide =
                ({32'd0, compute_read_input_channel} * patch_plane_bytes) +
                ((({32'd0, compute_read_point_y} * {32'd0, stride_y_latched}) +
                  {32'd0, compute_read_kernel_y}) * {32'd0, patch_width}) +
                ({32'd0, compute_read_point_x} * {32'd0, stride_x_latched}) +
                {32'd0, compute_read_kernel_x};
            compute_read_feature_index = compute_read_feature_index_wide[31:0];
        end
        output_global_y = tile_start_y + output_point_scan_y;
        output_global_x = tile_start_x + output_point_scan_x;
        output_channel_current = output_group_base + output_lane_index;
        // 保留C/Y/X原32位截断；全部乘加在原unsigned64模域内因式分解。
        output_geometry_plane = {32'd0, output_height_latched} * {32'd0, output_width_latched};
        output_channel_plane_offset = {32'd0, output_channel_current} * output_geometry_plane;
        output_row_offset = {32'd0, output_global_y} * {32'd0, output_width_latched};
        output_byte_offset_wide = output_channel_plane_offset + output_row_offset +
                                  {32'd0, output_global_x};
        output_address_wide = {32'd0, output_base_latched} + output_byte_offset_wide;

        mq_prefetch_index = 32'd0;
        mq_prefetch_parameter = 80'd0;
        mq_prefetch_bias = 32'sd0;
        mq_prefetch_invalid = 1'b0;
        if ((mq_prefetch_lane < group_lane_count) &&
            (layer_index_latched < S2A_LAYER_COUNT)) begin
            mq_prefetch_index = {16'd0, S2A_T23_MQ_BASE[layer_index_latched]} +
                                output_group_base + mq_prefetch_lane;
            if (mq_prefetch_index < S2A_CONV_CHANNEL_COUNT) begin
                mq_prefetch_parameter = S2A_T23_MQ_ROM[mq_prefetch_index];
                mq_prefetch_bias = $signed(S2A_CONV_BIAS_ACCUMULATOR_INT32[mq_prefetch_index]);
                if ((mq_prefetch_index >=
                     {16'd0, S2A_T23_MQ_BASE[layer_index_latched]} +
                     S2A_T23_MQ_CHANNEL_COUNT[layer_index_latched]) ||
                    (mq_prefetch_parameter[79:48] == 32'd0) ||
                    (mq_prefetch_parameter[39:8] == 32'd0) ||
                    (mq_prefetch_parameter[79:48] > 32'h3FFF_FFFF) ||
                    (mq_prefetch_parameter[39:8] > 32'h3FFF_FFFF) ||
                    (mq_prefetch_parameter[47:40] > 8'd47) ||
                    (mq_prefetch_parameter[7:0] > 8'd47) ||
                    ((activation_mode_latched == 2'd0) &&
                     ((mq_prefetch_parameter[79:48] != mq_prefetch_parameter[39:8]) ||
                      (mq_prefetch_parameter[47:40] != mq_prefetch_parameter[7:0])))) begin
                    mq_prefetch_invalid = 1'b1;
                end
            end else begin
                mq_prefetch_invalid = 1'b1;
            end
        end else if (mq_prefetch_lane < group_lane_count) begin
            mq_prefetch_invalid = 1'b1;
        end

        requant_parameter = 80'd0;
        requant_accumulator = 32'sd0;
        requant_multiplier = 32'd0;
        requant_q_shift = 32'd0;
        requant_magnitude = 32'd0;
        requant_product = 64'd0;
        requant_rounding_add = 64'd0;
        requant_rounded_magnitude = 64'd0;
        requantized_value = 8'sd0;
        if ((requant_lane_index < LANE_COUNT) &&
            (requant_lane_index < group_lane_count)) begin
            requant_parameter = lane_mq_parameter[requant_lane_index];
            requant_accumulator = lane_accumulator[requant_lane_index];
            if (requant_accumulator[31]) begin
                requant_multiplier = requant_parameter[39:8];
                requant_q_shift = {24'd0, requant_parameter[7:0]};
                requant_magnitude = ~$unsigned(requant_accumulator) + 32'd1;
            end else begin
                requant_multiplier = requant_parameter[79:48];
                requant_q_shift = {24'd0, requant_parameter[47:40]};
                requant_magnitude = $unsigned(requant_accumulator);
            end
            requant_product = {32'd0, requant_magnitude} *
                              {32'd0, requant_multiplier};
            if (requant_q_shift != 32'd0) begin
                requant_rounding_add = 64'd1 << (requant_q_shift - 32'd1);
            end
            requant_rounded_magnitude =
                (requant_product + requant_rounding_add) >> requant_q_shift;
            if (|requant_rounded_magnitude[63:7]) begin
                requantized_value = requant_accumulator[31] ? -8'sd127 : 8'sd127;
            end else if (requant_accumulator[31]) begin
                requantized_value = -$signed(requant_rounded_magnitude[7:0]);
            end else begin
                requantized_value = $signed(requant_rounded_magnitude[7:0]);
            end
        end

        mapped_response_error = INTERNAL;
        if (backend_rsp_error == NONE) begin
            mapped_response_error = NONE;
        end else if ((backend_rsp_error == BAD_ARGUMENT) ||
                     (backend_rsp_error == BAD_RANGE) ||
                     (backend_rsp_error == INTERNAL)) begin
            mapped_response_error = backend_rsp_error;
        end

        if ((state == ST_FEATURE_SCAN) &&
            (feature_scan_index < patch_byte_count) && !feature_scan_in_bounds) begin
            feature_scan_advance = 1'b1;
        end else if ((state == ST_FEATURE_RESPONSE) && backend_rsp_valid &&
                     (mapped_response_error == NONE)) begin
            feature_scan_advance = 1'b1;
        end

        request_byte_lane = 2'd0;
        case (request_strobe_latched)
            4'b0001: request_byte_lane = 2'd0;
            4'b0010: request_byte_lane = 2'd1;
            4'b0100: request_byte_lane = 2'd2;
            4'b1000: request_byte_lane = 2'd3;
            default: request_byte_lane = 2'd0;
        endcase

        start_ready = (state == ST_IDLE) && !hard_reset && !abort;
        busy = (state != ST_IDLE);
        result_valid = (state == ST_RESULT);
        result_error_code = result_error_latched;
        backend_cancel = hard_reset || abort;
        backend_req_valid = 1'b0;
        backend_req_write = 1'b0;
        backend_req_addr = request_address_latched;
        backend_req_wdata = request_wdata_latched;
        backend_req_rstrb = 4'd0;
        backend_req_wstrb = 4'd0;
        if (!hard_reset && !abort) begin
            case (state)
                ST_FEATURE_REQUEST, ST_WEIGHT_REQUEST: begin
                    backend_req_valid = 1'b1;
                    backend_req_write = 1'b0;
                    backend_req_rstrb = request_strobe_latched;
                end
                ST_OUTPUT_REQUEST: begin
                    backend_req_valid = 1'b1;
                    backend_req_write = 1'b1;
                    backend_req_wstrb = request_strobe_latched;
                end
                default: begin end
            endcase
        end
    end

    always_ff @(posedge clk) begin
        if (hard_reset) begin
            state <= ST_IDLE;
            layer_index_latched <= 32'd0;
            weight_layer_index_latched <= 32'd0;
            input_base_latched <= 32'd0;
            input_length_latched <= 32'd0;
            input_batch_count_latched <= 32'd0;
            input_channels_latched <= 32'd0;
            input_height_latched <= 32'd0;
            input_width_latched <= 32'd0;
            output_base_latched <= 32'd0;
            output_length_latched <= 32'd0;
            output_batch_count_latched <= 32'd0;
            output_channels_latched <= 32'd0;
            output_height_latched <= 32'd0;
            output_width_latched <= 32'd0;
            kernel_height_latched <= 32'd0;
            kernel_width_latched <= 32'd0;
            stride_y_latched <= 32'd0;
            stride_x_latched <= 32'd0;
            pad_left_latched <= 32'd0;
            pad_right_latched <= 32'd0;
            pad_top_latched <= 32'd0;
            pad_bottom_latched <= 32'd0;
            groups_latched <= 32'd0;
            padding_latched <= 32'sd0;
            weight_package_base_latched <= 32'd0;
            weight_package_length_latched <= 32'd0;
            quantized_weight_offset_latched <= 32'd0;
            quantized_weight_bytes_latched <= 32'd0;
            output_batch_latched <= 32'd0;
            activation_mode_latched <= 2'd0;
            reduction_count_latched <= 32'd0;
            output_group_base <= 32'd0;
            tile_start_y <= 32'd0;
            tile_start_x <= 32'd0;
            tile_height <= 32'd0;
            tile_width <= 32'd0;
            patch_height <= 32'd0;
            patch_width <= 32'd0;
            patch_byte_count <= 32'd0;
            tile_point_count <= 32'd0;
            group_lane_count <= 32'd0;
            feature_scan_index <= 32'd0;
            feature_scan_channel <= 32'd0;
            feature_scan_y <= 32'd0;
            feature_scan_x <= 32'd0;
            feature_read_data <= 8'sd0;
            feature_read_in_bounds <= 1'b0;
            weight_lane_index <= 32'd0;
            weight_reduction_index <= 32'd0;
            compute_point_index <= 32'd0;
            compute_point_scan_y <= 32'd0;
            compute_point_scan_x <= 32'd0;
            compute_reduction_index <= 32'd0;
            compute_input_channel <= 32'd0;
            compute_kernel_y <= 32'd0;
            compute_kernel_x <= 32'd0;
            output_lane_index <= 32'd0;
            output_point_index <= 32'd0;
            output_point_scan_y <= 32'd0;
            output_point_scan_x <= 32'd0;
            mq_prefetch_lane <= 32'd0;
            requant_lane_index <= 32'd0;
            request_address_latched <= 32'd0;
            request_strobe_latched <= 4'd0;
            request_write_latched <= 1'b0;
            request_wdata_latched <= 32'd0;
            output_address_latched <= 32'd0;
            output_value_latched <= 8'd0;
            result_error_latched <= NONE;
            for (seq_lane = 0; seq_lane < LANE_COUNT; seq_lane = seq_lane + 1) begin
                lane_mq_parameter[seq_lane] <= 80'd0;
                lane_bias[seq_lane] <= 32'sd0;
            end
        end else if (abort) begin
            state <= ST_IDLE;
            reduction_count_latched <= 32'd0;
            feature_scan_index <= 32'd0;
            feature_scan_channel <= 32'd0;
            feature_scan_y <= 32'd0;
            feature_scan_x <= 32'd0;
            feature_read_data <= 8'sd0;
            feature_read_in_bounds <= 1'b0;
            weight_lane_index <= 32'd0;
            weight_reduction_index <= 32'd0;
            compute_point_index <= 32'd0;
            compute_point_scan_y <= 32'd0;
            compute_point_scan_x <= 32'd0;
            compute_reduction_index <= 32'd0;
            compute_input_channel <= 32'd0;
            compute_kernel_y <= 32'd0;
            compute_kernel_x <= 32'd0;
            output_lane_index <= 32'd0;
            output_point_index <= 32'd0;
            output_point_scan_y <= 32'd0;
            output_point_scan_x <= 32'd0;
            mq_prefetch_lane <= 32'd0;
            requant_lane_index <= 32'd0;
            request_strobe_latched <= 4'd0;
            request_write_latched <= 1'b0;
            request_wdata_latched <= 32'd0;
            output_address_latched <= 32'd0;
            output_value_latched <= 8'd0;
            result_error_latched <= NONE;
            for (seq_lane = 0; seq_lane < LANE_COUNT; seq_lane = seq_lane + 1) begin
                lane_mq_parameter[seq_lane] <= 80'd0;
                lane_bias[seq_lane] <= 32'sd0;
            end
        end else begin
            if (compute_read_enable) begin
                feature_read_in_bounds <= compute_read_tap_in_bounds;
                if (compute_read_tap_in_bounds) begin
                    feature_read_data <= feature_patch[compute_read_feature_index];
                end else begin
                    feature_read_data <= 8'sd0;
                end
            end
            if (feature_scan_advance) begin
                if (feature_scan_x + 32'd1 >= patch_width) begin
                    feature_scan_x <= 32'd0;
                    if (feature_scan_y + 32'd1 >= patch_height) begin
                        feature_scan_y <= 32'd0;
                        feature_scan_channel <= feature_scan_channel + 32'd1;
                    end else begin
                        feature_scan_y <= feature_scan_y + 32'd1;
                    end
                end else begin
                    feature_scan_x <= feature_scan_x + 32'd1;
                end
            end
            case (state)
                ST_IDLE: begin
                    if (start_valid && start_ready) begin
                        layer_index_latched <= layer_index;
                        weight_layer_index_latched <= weight_layer_index;
                        input_base_latched <= input_base_address;
                        input_length_latched <= input_length_bytes;
                        input_batch_count_latched <= input_batch_count;
                        input_channels_latched <= input_channels;
                        input_height_latched <= input_height;
                        input_width_latched <= input_width;
                        output_base_latched <= output_base_address;
                        output_length_latched <= output_length_bytes;
                        output_batch_count_latched <= output_batch_count;
                        output_channels_latched <= output_channels;
                        output_height_latched <= output_height;
                        output_width_latched <= output_width;
                        kernel_height_latched <= kernel_height;
                        kernel_width_latched <= kernel_width;
                        stride_y_latched <= stride_y;
                        stride_x_latched <= stride_x;
                        pad_left_latched <= pad_left;
                        pad_right_latched <= pad_right;
                        pad_top_latched <= pad_top;
                        pad_bottom_latched <= pad_bottom;
                        groups_latched <= groups;
                        padding_latched <= padding_value_int8;
                        weight_package_base_latched <= weight_package_base_address;
                        weight_package_length_latched <= weight_package_length_bytes;
                        quantized_weight_offset_latched <= quantized_weight_offset;
                        quantized_weight_bytes_latched <= quantized_weight_bytes;
                        output_batch_latched <= output_batch;
                        activation_mode_latched <= activation_mode;
                        reduction_count_latched <= 32'd0;
                        output_group_base <= 32'd0;
                        tile_start_y <= 32'd0;
                        tile_start_x <= 32'd0;
                        feature_scan_index <= 32'd0;
                        feature_scan_channel <= 32'd0;
                        feature_scan_y <= 32'd0;
                        feature_scan_x <= 32'd0;
                        weight_lane_index <= 32'd0;
                        weight_reduction_index <= 32'd0;
                        compute_point_index <= 32'd0;
                        compute_point_scan_y <= 32'd0;
                        compute_point_scan_x <= 32'd0;
                        compute_reduction_index <= 32'd0;
                        compute_input_channel <= 32'd0;
                        compute_kernel_y <= 32'd0;
                        compute_kernel_x <= 32'd0;
                        output_lane_index <= 32'd0;
                        output_point_index <= 32'd0;
                        output_point_scan_y <= 32'd0;
                        output_point_scan_x <= 32'd0;
                        result_error_latched <= NONE;
                        state <= ST_VALIDATE;
                    end
                end
                ST_VALIDATE: begin
                    if (!validation_ok) begin
                        result_error_latched <= validation_error;
                        state <= ST_RESULT;
                    end else begin
                        reduction_count_latched <= reduction_count_wide[31:0];
                        state <= ST_TILE_PREP;
                    end
                end
                ST_TILE_PREP: begin
                    tile_height <= (output_height_latched - tile_start_y >= TILE_EDGE) ?
                                   TILE_EDGE : output_height_latched - tile_start_y;
                    tile_width <= (output_width_latched - tile_start_x >= TILE_EDGE) ?
                                  TILE_EDGE : output_width_latched - tile_start_x;
                    patch_height <=
                        (((output_height_latched - tile_start_y >= TILE_EDGE) ? TILE_EDGE :
                          output_height_latched - tile_start_y) - 1) * stride_y_latched +
                        kernel_height_latched;
                    patch_width <=
                        (((output_width_latched - tile_start_x >= TILE_EDGE) ? TILE_EDGE :
                          output_width_latched - tile_start_x) - 1) * stride_x_latched +
                        kernel_width_latched;
                    patch_byte_count <=
                        ((((output_height_latched - tile_start_y >= TILE_EDGE) ? TILE_EDGE :
                           output_height_latched - tile_start_y) - 1) * stride_y_latched +
                         kernel_height_latched) *
                        ((((output_width_latched - tile_start_x >= TILE_EDGE) ? TILE_EDGE :
                           output_width_latched - tile_start_x) - 1) * stride_x_latched +
                         kernel_width_latched) * input_channels_latched;
                    feature_scan_channel <= 32'd0;
                    feature_scan_y <= 32'd0;
                    feature_scan_x <= 32'd0;
                    compute_point_scan_y <= 32'd0;
                    compute_point_scan_x <= 32'd0;
                    tile_point_count <=
                        ((output_height_latched - tile_start_y >= TILE_EDGE) ? TILE_EDGE :
                         output_height_latched - tile_start_y) *
                        ((output_width_latched - tile_start_x >= TILE_EDGE) ? TILE_EDGE :
                         output_width_latched - tile_start_x);
                    feature_scan_index <= 32'd0;
                    state <= ST_FEATURE_SCAN;
                end
                ST_FEATURE_SCAN: begin
                    if (feature_scan_index >= patch_byte_count) begin
                        output_group_base <= 32'd0;
                        state <= ST_WEIGHT_PREP;
                    end else if (!feature_scan_in_bounds) begin
                        feature_patch[feature_scan_index] <= 8'sd0;
                        feature_scan_index <= feature_scan_index + 32'd1;
                    end else if (feature_source_address_wide > 64'h0000_0000_FFFF_FFFF) begin
                        result_error_latched <= BAD_RANGE;
                        state <= ST_RESULT;
                    end else begin
                        request_address_latched <= {feature_source_address_wide[31:2], 2'b00};
                        request_strobe_latched <= 4'b0001 << feature_source_address_wide[1:0];
                        request_write_latched <= 1'b0;
                        request_wdata_latched <= 32'd0;
                        state <= ST_FEATURE_REQUEST;
                    end
                end
                ST_FEATURE_REQUEST: begin
                    if (backend_req_valid && backend_req_ready) begin
                        state <= ST_FEATURE_RESPONSE;
                    end
                end
                ST_FEATURE_RESPONSE: begin
                    if (backend_rsp_valid) begin
                        if (mapped_response_error != NONE) begin
                            result_error_latched <= mapped_response_error;
                            state <= ST_RESULT;
                        end else begin
                            feature_patch[feature_scan_index] <=
                                $signed(backend_rsp_rdata >> (request_byte_lane * 8));
                            feature_scan_index <= feature_scan_index + 32'd1;
                            state <= ST_FEATURE_SCAN;
                        end
                    end
                end
                ST_WEIGHT_PREP: begin
                    if (output_group_base >= output_channels_latched) begin
                        state <= ST_ADVANCE;
                    end else begin
                        group_lane_count <= (output_channels_latched - output_group_base >= LANE_COUNT) ?
                                            LANE_COUNT : output_channels_latched - output_group_base;
                        compute_point_scan_y <= 32'd0;
                        compute_point_scan_x <= 32'd0;
                        weight_lane_index <= 32'd0;
                        weight_reduction_index <= 32'd0;
                        mq_prefetch_lane <= 32'd0;
                        state <= ST_WEIGHT_SCAN;
                    end
                end
                ST_WEIGHT_SCAN: begin
                    if (weight_lane_index >= group_lane_count) begin
                        mq_prefetch_lane <= 32'd0;
                        state <= ST_MQ_PREFETCH;
                    end else if (weight_reduction_index >= reduction_count_latched) begin
                        weight_lane_index <= weight_lane_index + 32'd1;
                        weight_reduction_index <= 32'd0;
                    end else if (weight_source_address_wide > 64'h0000_0000_FFFF_FFFF) begin
                        result_error_latched <= BAD_RANGE;
                        state <= ST_RESULT;
                    end else begin
                        request_address_latched <= {weight_source_address_wide[31:2], 2'b00};
                        request_strobe_latched <= 4'b0001 << weight_source_address_wide[1:0];
                        request_write_latched <= 1'b0;
                        request_wdata_latched <= 32'd0;
                        state <= ST_WEIGHT_REQUEST;
                    end
                end
                ST_WEIGHT_REQUEST: begin
                    if (backend_req_valid && backend_req_ready) begin
                        state <= ST_WEIGHT_RESPONSE;
                    end
                end
                ST_WEIGHT_RESPONSE: begin
                    if (backend_rsp_valid) begin
                        if (mapped_response_error != NONE) begin
                            result_error_latched <= mapped_response_error;
                            state <= ST_RESULT;
                        end else begin
                            weight_reduction_index <= weight_reduction_index + 32'd1;
                            state <= ST_WEIGHT_SCAN;
                        end
                    end
                end
                ST_MQ_PREFETCH: begin
                    if (mq_prefetch_invalid) begin
                        result_error_latched <= BAD_ARGUMENT;
                        state <= ST_RESULT;
                    end else begin
                        lane_mq_parameter[mq_prefetch_lane] <= mq_prefetch_parameter;
                        lane_bias[mq_prefetch_lane] <= mq_prefetch_bias;
                        if (mq_prefetch_lane + 32'd1 >= group_lane_count) begin
                            state <= ST_COMPUTE_PREP;
                        end else begin
                            mq_prefetch_lane <= mq_prefetch_lane + 32'd1;
                        end
                    end
                end
                ST_COMPUTE_PREP: begin
                    compute_input_channel <= 32'd0;
                    compute_kernel_y <= 32'd0;
                    compute_kernel_x <= 32'd0;
                    for (seq_lane = 0; seq_lane < LANE_COUNT; seq_lane = seq_lane + 1) begin
                        if (seq_lane < group_lane_count) begin
                            lane_accumulator[seq_lane] <= lane_bias[seq_lane];
                        end else begin
                            lane_accumulator[seq_lane] <= 32'sd0;
                        end
                    end
                    compute_point_index <= 32'd0;
                    compute_reduction_index <= 32'd0;
                    state <= ST_COMPUTE;
                end
                ST_COMPUTE_POINT_PREP: begin
                    compute_input_channel <= 32'd0;
                    compute_kernel_y <= 32'd0;
                    compute_kernel_x <= 32'd0;
                    for (seq_lane = 0; seq_lane < LANE_COUNT; seq_lane = seq_lane + 1) begin
                        if (seq_lane < group_lane_count) begin
                            lane_accumulator[seq_lane] <= lane_bias[seq_lane];
                        end else begin
                            lane_accumulator[seq_lane] <= 32'sd0;
                        end
                    end
                    compute_reduction_index <= 32'd0;
                    state <= ST_COMPUTE;
                end
                ST_COMPUTE: begin
                    if (compute_bad_argument) begin
                        result_error_latched <= BAD_ARGUMENT;
                        state <= ST_RESULT;
                    end else if (compute_overflow) begin
                        result_error_latched <= ACCUMULATOR_OVERFLOW;
                        state <= ST_RESULT;
                    end else begin
                        for (seq_lane = 0; seq_lane < LANE_COUNT; seq_lane = seq_lane + 1) begin
                            if (seq_lane < group_lane_count) begin
                                lane_accumulator[seq_lane] <= compute_sum[seq_lane][31:0];
                            end
                        end
                        if (compute_reduction_index + 32'd1 >= reduction_count_latched) begin
                            requant_lane_index <= 32'd0;
                            state <= ST_COMPUTE_REQUANT;
                        end else begin
                            compute_reduction_index <= compute_reduction_index + 32'd1;
                            if (compute_kernel_x + 32'd1 >= kernel_width_latched) begin
                                compute_kernel_x <= 32'd0;
                                if (compute_kernel_y + 32'd1 >= kernel_height_latched) begin
                                    compute_kernel_y <= 32'd0;
                                    compute_input_channel <= compute_input_channel + 32'd1;
                                end else begin
                                    compute_kernel_y <= compute_kernel_y + 32'd1;
                                end
                            end else begin
                                compute_kernel_x <= compute_kernel_x + 32'd1;
                            end
                        end
                    end
                end
                ST_COMPUTE_REQUANT: begin
                    if (requant_lane_index < group_lane_count) begin
                        output_block[(requant_lane_index * (TILE_EDGE * TILE_EDGE)) + compute_point_index] <=
                            requantized_value;
                    end
                    if (requant_lane_index + 32'd1 >= group_lane_count) begin
                        if (compute_point_index + 32'd1 >= tile_point_count) begin
                            output_lane_index <= 32'd0;
                            output_point_index <= 32'd0;
                            output_point_scan_y <= 32'd0;
                            output_point_scan_x <= 32'd0;
                            state <= ST_OUTPUT_SCAN;
                        end else begin
                            compute_point_index <= compute_point_index + 32'd1;
                            if (compute_point_scan_x + 32'd1 >= tile_width) begin
                                compute_point_scan_x <= 32'd0;
                                compute_point_scan_y <= compute_point_scan_y + 32'd1;
                            end else begin
                                compute_point_scan_x <= compute_point_scan_x + 32'd1;
                            end
                            compute_reduction_index <= 32'd0;
                            state <= ST_COMPUTE_POINT_PREP;
                        end
                    end else begin
                        requant_lane_index <= requant_lane_index + 32'd1;
                    end
                end
                ST_OUTPUT_SCAN: begin
                    if (output_lane_index >= group_lane_count) begin
                        state <= ST_ADVANCE;
                    end else if (output_point_index >= tile_point_count) begin
                        output_lane_index <= output_lane_index + 32'd1;
                        output_point_index <= 32'd0;
                        output_point_scan_y <= 32'd0;
                        output_point_scan_x <= 32'd0;
                    end else if ((output_address_wide > 64'h0000_0000_FFFF_FFFF) ||
                                 (output_byte_offset_wide >= output_elements_wide)) begin
                        result_error_latched <= BAD_RANGE;
                        state <= ST_RESULT;
                    end else begin
                        output_address_latched <= output_address_wide[31:0];
                        output_value_latched <= output_block[
                            (output_lane_index * (TILE_EDGE * TILE_EDGE)) + output_point_index
                        ];
                        request_address_latched <= {output_address_wide[31:2], 2'b00};
                        request_strobe_latched <= 4'b0001 << output_address_wide[1:0];
                        request_write_latched <= 1'b1;
                        request_wdata_latched <=
                            {24'd0, output_block[
                                (output_lane_index * (TILE_EDGE * TILE_EDGE)) + output_point_index
                            ]} << (output_address_wide[1:0] * 8);
                        state <= ST_OUTPUT_REQUEST;
                    end
                end
                ST_OUTPUT_REQUEST: begin
                    if (backend_req_valid && backend_req_ready) begin
                        state <= ST_OUTPUT_RESPONSE;
                    end
                end
                ST_OUTPUT_RESPONSE: begin
                    if (backend_rsp_valid) begin
                        if (mapped_response_error != NONE) begin
                            result_error_latched <= mapped_response_error;
                            state <= ST_RESULT;
                        end else begin
                            output_point_index <= output_point_index + 32'd1;
                            if (output_point_scan_x + 32'd1 >= tile_width) begin
                                output_point_scan_x <= 32'd0;
                                output_point_scan_y <= output_point_scan_y + 32'd1;
                            end else begin
                                output_point_scan_x <= output_point_scan_x + 32'd1;
                            end
                            state <= ST_OUTPUT_SCAN;
                        end
                    end
                end
                ST_ADVANCE: begin
                    if (output_group_base + LANE_COUNT < output_channels_latched) begin
                        output_group_base <= output_group_base + LANE_COUNT;
                        state <= ST_WEIGHT_PREP;
                    end else if (tile_start_x + tile_width < output_width_latched) begin
                        output_group_base <= 32'd0;
                        tile_start_x <= tile_start_x + TILE_EDGE;
                        state <= ST_TILE_PREP;
                    end else if (tile_start_y + tile_height < output_height_latched) begin
                        output_group_base <= 32'd0;
                        tile_start_x <= 32'd0;
                        tile_start_y <= tile_start_y + TILE_EDGE;
                        state <= ST_TILE_PREP;
                    end else begin
                        result_error_latched <= NONE;
                        state <= ST_RESULT;
                    end
                end
                ST_RESULT: begin
                    if (result_valid && result_ready) begin
                        result_error_latched <= NONE;
                        state <= ST_IDLE;
                    end
                end
                default: begin
                    result_error_latched <= INTERNAL;
                    state <= ST_RESULT;
                end
            endcase
        end
    end

    genvar weight_bank_index;
    generate
        for (weight_bank_index = 0; weight_bank_index < LANE_COUNT; weight_bank_index = weight_bank_index + 1) begin : gen_weight_lane_bank
            logic signed [7:0] lane_weight_memory [0:MAX_WEIGHT_REDUCTION_COUNT-1];

            always_ff @(posedge clk) begin
                if (hard_reset || abort) begin
                    weight_read_byte[weight_bank_index] <= 8'sd0;
                end else begin
                    if ((state == ST_WEIGHT_RESPONSE) && backend_rsp_valid &&
                        (mapped_response_error == NONE) &&
                        (weight_lane_index == weight_bank_index) &&
                        (weight_reduction_index < MAX_WEIGHT_REDUCTION_COUNT)) begin
                        lane_weight_memory[weight_reduction_index] <=
                            $signed(backend_rsp_rdata[(request_byte_lane * 8) +: 8]);
                    end
                    if (compute_read_enable && (weight_bank_index < group_lane_count)) begin
                        weight_read_byte[weight_bank_index] <=
                            lane_weight_memory[compute_read_reduction_index];
                    end
                end
            end
        end
    endgenerate
endmodule
