// S2A-T66：以 8×8 空间 tile 和 8 个输出通道并行完成一个卷积层。
module s2b_conv_tile_engine #(
    // 仅冻结network实例启用；默认保留原通用参数域和错误判据。
    parameter bit FROZEN_CONV_DESCRIPTOR = 1'b0
) (
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
    // 现有PRE拍登记完整模64坐标原点；SCAN不增加周期或缩减signed域。
    logic signed [63:0] tile_origin_y;
    logic signed [63:0] tile_origin_x;
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
    // 本次START登记完整输入空间平面，SCAN仅保留channel乘法。
    logic [63:0] input_geometry_plane;
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

    // 完整480位冻结字段键；私有模式不允许仅layer索引绕过其他参数。
    function automatic logic [97:0] frozen_conv_descriptor_lookup(input logic [479:0] descriptor_key);
        begin
            frozen_conv_descriptor_lookup = 98'd0;
            case (descriptor_key)
                480'h0000000000000003000001A0000001A000000020000000D0000000D00000000300000003000000020000000200000001000000010000000100000001: frozen_conv_descriptor_lookup = {1'b1, 26'd9, 26'd27, 45'd864};
                480'h0000000100000020000000D0000000D00000004000000068000000680000000300000003000000020000000200000001000000010000000100000001: frozen_conv_descriptor_lookup = {1'b1, 26'd96, 26'd288, 45'd18432};
                480'h000000020000004000000068000000680000004000000068000000680000000300000003000000010000000100000001000000010000000100000001: frozen_conv_descriptor_lookup = {1'b1, 26'd192, 26'd576, 45'd36864};
                480'h000000040000002000000068000000680000002000000068000000680000000300000003000000010000000100000001000000010000000100000001: frozen_conv_descriptor_lookup = {1'b1, 26'd96, 26'd288, 45'd9216};
                480'h000000050000002000000068000000680000002000000068000000680000000300000003000000010000000100000001000000010000000100000001: frozen_conv_descriptor_lookup = {1'b1, 26'd96, 26'd288, 45'd9216};
                480'h000000070000004000000068000000680000004000000068000000680000000100000001000000010000000100000000000000000000000000000000: frozen_conv_descriptor_lookup = {1'b1, 26'd64, 26'd64, 45'd4096};
                480'h0000000A0000008000000034000000340000008000000034000000340000000300000003000000010000000100000001000000010000000100000001: frozen_conv_descriptor_lookup = {1'b1, 26'd384, 26'd1152, 45'd147456};
                480'h0000000C0000004000000034000000340000004000000034000000340000000300000003000000010000000100000001000000010000000100000001: frozen_conv_descriptor_lookup = {1'b1, 26'd192, 26'd576, 45'd36864};
                480'h0000000D0000004000000034000000340000004000000034000000340000000300000003000000010000000100000001000000010000000100000001: frozen_conv_descriptor_lookup = {1'b1, 26'd192, 26'd576, 45'd36864};
                480'h0000000F0000008000000034000000340000008000000034000000340000000100000001000000010000000100000000000000000000000000000000: frozen_conv_descriptor_lookup = {1'b1, 26'd128, 26'd128, 45'd16384};
                480'h00000012000001000000001A0000001A000001000000001A0000001A0000000300000003000000010000000100000001000000010000000100000001: frozen_conv_descriptor_lookup = {1'b1, 26'd768, 26'd2304, 45'd589824};
                480'h00000014000000800000001A0000001A000000800000001A0000001A0000000300000003000000010000000100000001000000010000000100000001: frozen_conv_descriptor_lookup = {1'b1, 26'd384, 26'd1152, 45'd147456};
                480'h00000015000000800000001A0000001A000000800000001A0000001A0000000300000003000000010000000100000001000000010000000100000001: frozen_conv_descriptor_lookup = {1'b1, 26'd384, 26'd1152, 45'd147456};
                480'h00000017000001000000001A0000001A000001000000001A0000001A0000000100000001000000010000000100000000000000000000000000000000: frozen_conv_descriptor_lookup = {1'b1, 26'd256, 26'd256, 45'd65536};
                480'h0000001A000002000000000D0000000D000002000000000D0000000D0000000300000003000000010000000100000001000000010000000100000001: frozen_conv_descriptor_lookup = {1'b1, 26'd1536, 26'd4608, 45'd2359296};
                480'h0000001B000002000000000D0000000D000001000000000D0000000D0000000100000001000000010000000100000000000000000000000000000000: frozen_conv_descriptor_lookup = {1'b1, 26'd512, 26'd512, 45'd131072};
                480'h0000001C000001000000000D0000000D000002000000000D0000000D0000000300000003000000010000000100000001000000010000000100000001: frozen_conv_descriptor_lookup = {1'b1, 26'd768, 26'd2304, 45'd1179648};
                480'h0000001D000002000000000D0000000D0000001E0000000D0000000D0000000100000001000000010000000100000000000000000000000000000000: frozen_conv_descriptor_lookup = {1'b1, 26'd512, 26'd512, 45'd15360};
                480'h00000020000001000000000D0000000D000000800000000D0000000D0000000100000001000000010000000100000000000000000000000000000000: frozen_conv_descriptor_lookup = {1'b1, 26'd256, 26'd256, 45'd32768};
                480'h00000023000001800000001A0000001A000001000000001A0000001A0000000300000003000000010000000100000001000000010000000100000001: frozen_conv_descriptor_lookup = {1'b1, 26'd1152, 26'd3456, 45'd884736};
                480'h00000024000001000000001A0000001A0000001E0000001A0000001A0000000100000001000000010000000100000000000000000000000000000000: frozen_conv_descriptor_lookup = {1'b1, 26'd256, 26'd256, 45'd7680};
                default: frozen_conv_descriptor_lookup = 98'd0;
            endcase
        end
    endfunction

    // extent为0时保留原减1的U32回绕；其余值使用精确常系数移位加法。
    function automatic logic [31:0] generic_tile_patch_axis(
        input logic [31:0] extent, input logic [31:0] stride, input logic [31:0] kernel_size);
        begin
            case (extent)
                32'd0: generic_tile_patch_axis = kernel_size - stride;
                32'd1: generic_tile_patch_axis = kernel_size;
                32'd2: generic_tile_patch_axis = stride + kernel_size;
                32'd3: generic_tile_patch_axis = (stride << 32'd1) + kernel_size;
                32'd4: generic_tile_patch_axis = (stride << 32'd1) + stride + kernel_size;
                32'd5: generic_tile_patch_axis = (stride << 32'd2) + kernel_size;
                32'd6: generic_tile_patch_axis = (stride << 32'd2) + stride + kernel_size;
                32'd7: generic_tile_patch_axis = (stride << 32'd2) + (stride << 32'd1) + kernel_size;
                32'd8: generic_tile_patch_axis = (stride << 32'd2) + (stride << 32'd1) + stride + kernel_size;
                default: generic_tile_patch_axis = 32'd0;
            endcase
        end
    endfunction

    // 三个字段均按原ST_TILE_PREP赋值的U32模域预计算，无额外寄存器或周期。
    function automatic logic [95:0] frozen_conv_tile_lookup(input logic [39:0] tile_key);
        begin
            frozen_conv_tile_lookup = 96'd0;
            case (tile_key)
                40'h0000000000: frozen_conv_tile_lookup = {32'd1, 32'd1, 32'd3};
                40'h0000000001: frozen_conv_tile_lookup = {32'd1, 32'd3, 32'd9};
                40'h0000000002: frozen_conv_tile_lookup = {32'd1, 32'd5, 32'd15};
                40'h0000000003: frozen_conv_tile_lookup = {32'd1, 32'd7, 32'd21};
                40'h0000000004: frozen_conv_tile_lookup = {32'd1, 32'd9, 32'd27};
                40'h0000000005: frozen_conv_tile_lookup = {32'd1, 32'd11, 32'd33};
                40'h0000000006: frozen_conv_tile_lookup = {32'd1, 32'd13, 32'd39};
                40'h0000000007: frozen_conv_tile_lookup = {32'd1, 32'd15, 32'd45};
                40'h0000000008: frozen_conv_tile_lookup = {32'd1, 32'd17, 32'd51};
                40'h0000000010: frozen_conv_tile_lookup = {32'd3, 32'd1, 32'd9};
                40'h0000000011: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd27};
                40'h0000000012: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd45};
                40'h0000000013: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd63};
                40'h0000000014: frozen_conv_tile_lookup = {32'd3, 32'd9, 32'd81};
                40'h0000000015: frozen_conv_tile_lookup = {32'd3, 32'd11, 32'd99};
                40'h0000000016: frozen_conv_tile_lookup = {32'd3, 32'd13, 32'd117};
                40'h0000000017: frozen_conv_tile_lookup = {32'd3, 32'd15, 32'd135};
                40'h0000000018: frozen_conv_tile_lookup = {32'd3, 32'd17, 32'd153};
                40'h0000000020: frozen_conv_tile_lookup = {32'd5, 32'd1, 32'd15};
                40'h0000000021: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd45};
                40'h0000000022: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd75};
                40'h0000000023: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd105};
                40'h0000000024: frozen_conv_tile_lookup = {32'd5, 32'd9, 32'd135};
                40'h0000000025: frozen_conv_tile_lookup = {32'd5, 32'd11, 32'd165};
                40'h0000000026: frozen_conv_tile_lookup = {32'd5, 32'd13, 32'd195};
                40'h0000000027: frozen_conv_tile_lookup = {32'd5, 32'd15, 32'd225};
                40'h0000000028: frozen_conv_tile_lookup = {32'd5, 32'd17, 32'd255};
                40'h0000000030: frozen_conv_tile_lookup = {32'd7, 32'd1, 32'd21};
                40'h0000000031: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd63};
                40'h0000000032: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd105};
                40'h0000000033: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd147};
                40'h0000000034: frozen_conv_tile_lookup = {32'd7, 32'd9, 32'd189};
                40'h0000000035: frozen_conv_tile_lookup = {32'd7, 32'd11, 32'd231};
                40'h0000000036: frozen_conv_tile_lookup = {32'd7, 32'd13, 32'd273};
                40'h0000000037: frozen_conv_tile_lookup = {32'd7, 32'd15, 32'd315};
                40'h0000000038: frozen_conv_tile_lookup = {32'd7, 32'd17, 32'd357};
                40'h0000000040: frozen_conv_tile_lookup = {32'd9, 32'd1, 32'd27};
                40'h0000000041: frozen_conv_tile_lookup = {32'd9, 32'd3, 32'd81};
                40'h0000000042: frozen_conv_tile_lookup = {32'd9, 32'd5, 32'd135};
                40'h0000000043: frozen_conv_tile_lookup = {32'd9, 32'd7, 32'd189};
                40'h0000000044: frozen_conv_tile_lookup = {32'd9, 32'd9, 32'd243};
                40'h0000000045: frozen_conv_tile_lookup = {32'd9, 32'd11, 32'd297};
                40'h0000000046: frozen_conv_tile_lookup = {32'd9, 32'd13, 32'd351};
                40'h0000000047: frozen_conv_tile_lookup = {32'd9, 32'd15, 32'd405};
                40'h0000000048: frozen_conv_tile_lookup = {32'd9, 32'd17, 32'd459};
                40'h0000000050: frozen_conv_tile_lookup = {32'd11, 32'd1, 32'd33};
                40'h0000000051: frozen_conv_tile_lookup = {32'd11, 32'd3, 32'd99};
                40'h0000000052: frozen_conv_tile_lookup = {32'd11, 32'd5, 32'd165};
                40'h0000000053: frozen_conv_tile_lookup = {32'd11, 32'd7, 32'd231};
                40'h0000000054: frozen_conv_tile_lookup = {32'd11, 32'd9, 32'd297};
                40'h0000000055: frozen_conv_tile_lookup = {32'd11, 32'd11, 32'd363};
                40'h0000000056: frozen_conv_tile_lookup = {32'd11, 32'd13, 32'd429};
                40'h0000000057: frozen_conv_tile_lookup = {32'd11, 32'd15, 32'd495};
                40'h0000000058: frozen_conv_tile_lookup = {32'd11, 32'd17, 32'd561};
                40'h0000000060: frozen_conv_tile_lookup = {32'd13, 32'd1, 32'd39};
                40'h0000000061: frozen_conv_tile_lookup = {32'd13, 32'd3, 32'd117};
                40'h0000000062: frozen_conv_tile_lookup = {32'd13, 32'd5, 32'd195};
                40'h0000000063: frozen_conv_tile_lookup = {32'd13, 32'd7, 32'd273};
                40'h0000000064: frozen_conv_tile_lookup = {32'd13, 32'd9, 32'd351};
                40'h0000000065: frozen_conv_tile_lookup = {32'd13, 32'd11, 32'd429};
                40'h0000000066: frozen_conv_tile_lookup = {32'd13, 32'd13, 32'd507};
                40'h0000000067: frozen_conv_tile_lookup = {32'd13, 32'd15, 32'd585};
                40'h0000000068: frozen_conv_tile_lookup = {32'd13, 32'd17, 32'd663};
                40'h0000000070: frozen_conv_tile_lookup = {32'd15, 32'd1, 32'd45};
                40'h0000000071: frozen_conv_tile_lookup = {32'd15, 32'd3, 32'd135};
                40'h0000000072: frozen_conv_tile_lookup = {32'd15, 32'd5, 32'd225};
                40'h0000000073: frozen_conv_tile_lookup = {32'd15, 32'd7, 32'd315};
                40'h0000000074: frozen_conv_tile_lookup = {32'd15, 32'd9, 32'd405};
                40'h0000000075: frozen_conv_tile_lookup = {32'd15, 32'd11, 32'd495};
                40'h0000000076: frozen_conv_tile_lookup = {32'd15, 32'd13, 32'd585};
                40'h0000000077: frozen_conv_tile_lookup = {32'd15, 32'd15, 32'd675};
                40'h0000000078: frozen_conv_tile_lookup = {32'd15, 32'd17, 32'd765};
                40'h0000000080: frozen_conv_tile_lookup = {32'd17, 32'd1, 32'd51};
                40'h0000000081: frozen_conv_tile_lookup = {32'd17, 32'd3, 32'd153};
                40'h0000000082: frozen_conv_tile_lookup = {32'd17, 32'd5, 32'd255};
                40'h0000000083: frozen_conv_tile_lookup = {32'd17, 32'd7, 32'd357};
                40'h0000000084: frozen_conv_tile_lookup = {32'd17, 32'd9, 32'd459};
                40'h0000000085: frozen_conv_tile_lookup = {32'd17, 32'd11, 32'd561};
                40'h0000000086: frozen_conv_tile_lookup = {32'd17, 32'd13, 32'd663};
                40'h0000000087: frozen_conv_tile_lookup = {32'd17, 32'd15, 32'd765};
                40'h0000000088: frozen_conv_tile_lookup = {32'd17, 32'd17, 32'd867};
                40'h0000000100: frozen_conv_tile_lookup = {32'd1, 32'd1, 32'd32};
                40'h0000000101: frozen_conv_tile_lookup = {32'd1, 32'd3, 32'd96};
                40'h0000000102: frozen_conv_tile_lookup = {32'd1, 32'd5, 32'd160};
                40'h0000000103: frozen_conv_tile_lookup = {32'd1, 32'd7, 32'd224};
                40'h0000000104: frozen_conv_tile_lookup = {32'd1, 32'd9, 32'd288};
                40'h0000000105: frozen_conv_tile_lookup = {32'd1, 32'd11, 32'd352};
                40'h0000000106: frozen_conv_tile_lookup = {32'd1, 32'd13, 32'd416};
                40'h0000000107: frozen_conv_tile_lookup = {32'd1, 32'd15, 32'd480};
                40'h0000000108: frozen_conv_tile_lookup = {32'd1, 32'd17, 32'd544};
                40'h0000000110: frozen_conv_tile_lookup = {32'd3, 32'd1, 32'd96};
                40'h0000000111: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd288};
                40'h0000000112: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd480};
                40'h0000000113: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd672};
                40'h0000000114: frozen_conv_tile_lookup = {32'd3, 32'd9, 32'd864};
                40'h0000000115: frozen_conv_tile_lookup = {32'd3, 32'd11, 32'd1056};
                40'h0000000116: frozen_conv_tile_lookup = {32'd3, 32'd13, 32'd1248};
                40'h0000000117: frozen_conv_tile_lookup = {32'd3, 32'd15, 32'd1440};
                40'h0000000118: frozen_conv_tile_lookup = {32'd3, 32'd17, 32'd1632};
                40'h0000000120: frozen_conv_tile_lookup = {32'd5, 32'd1, 32'd160};
                40'h0000000121: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd480};
                40'h0000000122: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd800};
                40'h0000000123: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd1120};
                40'h0000000124: frozen_conv_tile_lookup = {32'd5, 32'd9, 32'd1440};
                40'h0000000125: frozen_conv_tile_lookup = {32'd5, 32'd11, 32'd1760};
                40'h0000000126: frozen_conv_tile_lookup = {32'd5, 32'd13, 32'd2080};
                40'h0000000127: frozen_conv_tile_lookup = {32'd5, 32'd15, 32'd2400};
                40'h0000000128: frozen_conv_tile_lookup = {32'd5, 32'd17, 32'd2720};
                40'h0000000130: frozen_conv_tile_lookup = {32'd7, 32'd1, 32'd224};
                40'h0000000131: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd672};
                40'h0000000132: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd1120};
                40'h0000000133: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd1568};
                40'h0000000134: frozen_conv_tile_lookup = {32'd7, 32'd9, 32'd2016};
                40'h0000000135: frozen_conv_tile_lookup = {32'd7, 32'd11, 32'd2464};
                40'h0000000136: frozen_conv_tile_lookup = {32'd7, 32'd13, 32'd2912};
                40'h0000000137: frozen_conv_tile_lookup = {32'd7, 32'd15, 32'd3360};
                40'h0000000138: frozen_conv_tile_lookup = {32'd7, 32'd17, 32'd3808};
                40'h0000000140: frozen_conv_tile_lookup = {32'd9, 32'd1, 32'd288};
                40'h0000000141: frozen_conv_tile_lookup = {32'd9, 32'd3, 32'd864};
                40'h0000000142: frozen_conv_tile_lookup = {32'd9, 32'd5, 32'd1440};
                40'h0000000143: frozen_conv_tile_lookup = {32'd9, 32'd7, 32'd2016};
                40'h0000000144: frozen_conv_tile_lookup = {32'd9, 32'd9, 32'd2592};
                40'h0000000145: frozen_conv_tile_lookup = {32'd9, 32'd11, 32'd3168};
                40'h0000000146: frozen_conv_tile_lookup = {32'd9, 32'd13, 32'd3744};
                40'h0000000147: frozen_conv_tile_lookup = {32'd9, 32'd15, 32'd4320};
                40'h0000000148: frozen_conv_tile_lookup = {32'd9, 32'd17, 32'd4896};
                40'h0000000150: frozen_conv_tile_lookup = {32'd11, 32'd1, 32'd352};
                40'h0000000151: frozen_conv_tile_lookup = {32'd11, 32'd3, 32'd1056};
                40'h0000000152: frozen_conv_tile_lookup = {32'd11, 32'd5, 32'd1760};
                40'h0000000153: frozen_conv_tile_lookup = {32'd11, 32'd7, 32'd2464};
                40'h0000000154: frozen_conv_tile_lookup = {32'd11, 32'd9, 32'd3168};
                40'h0000000155: frozen_conv_tile_lookup = {32'd11, 32'd11, 32'd3872};
                40'h0000000156: frozen_conv_tile_lookup = {32'd11, 32'd13, 32'd4576};
                40'h0000000157: frozen_conv_tile_lookup = {32'd11, 32'd15, 32'd5280};
                40'h0000000158: frozen_conv_tile_lookup = {32'd11, 32'd17, 32'd5984};
                40'h0000000160: frozen_conv_tile_lookup = {32'd13, 32'd1, 32'd416};
                40'h0000000161: frozen_conv_tile_lookup = {32'd13, 32'd3, 32'd1248};
                40'h0000000162: frozen_conv_tile_lookup = {32'd13, 32'd5, 32'd2080};
                40'h0000000163: frozen_conv_tile_lookup = {32'd13, 32'd7, 32'd2912};
                40'h0000000164: frozen_conv_tile_lookup = {32'd13, 32'd9, 32'd3744};
                40'h0000000165: frozen_conv_tile_lookup = {32'd13, 32'd11, 32'd4576};
                40'h0000000166: frozen_conv_tile_lookup = {32'd13, 32'd13, 32'd5408};
                40'h0000000167: frozen_conv_tile_lookup = {32'd13, 32'd15, 32'd6240};
                40'h0000000168: frozen_conv_tile_lookup = {32'd13, 32'd17, 32'd7072};
                40'h0000000170: frozen_conv_tile_lookup = {32'd15, 32'd1, 32'd480};
                40'h0000000171: frozen_conv_tile_lookup = {32'd15, 32'd3, 32'd1440};
                40'h0000000172: frozen_conv_tile_lookup = {32'd15, 32'd5, 32'd2400};
                40'h0000000173: frozen_conv_tile_lookup = {32'd15, 32'd7, 32'd3360};
                40'h0000000174: frozen_conv_tile_lookup = {32'd15, 32'd9, 32'd4320};
                40'h0000000175: frozen_conv_tile_lookup = {32'd15, 32'd11, 32'd5280};
                40'h0000000176: frozen_conv_tile_lookup = {32'd15, 32'd13, 32'd6240};
                40'h0000000177: frozen_conv_tile_lookup = {32'd15, 32'd15, 32'd7200};
                40'h0000000178: frozen_conv_tile_lookup = {32'd15, 32'd17, 32'd8160};
                40'h0000000180: frozen_conv_tile_lookup = {32'd17, 32'd1, 32'd544};
                40'h0000000181: frozen_conv_tile_lookup = {32'd17, 32'd3, 32'd1632};
                40'h0000000182: frozen_conv_tile_lookup = {32'd17, 32'd5, 32'd2720};
                40'h0000000183: frozen_conv_tile_lookup = {32'd17, 32'd7, 32'd3808};
                40'h0000000184: frozen_conv_tile_lookup = {32'd17, 32'd9, 32'd4896};
                40'h0000000185: frozen_conv_tile_lookup = {32'd17, 32'd11, 32'd5984};
                40'h0000000186: frozen_conv_tile_lookup = {32'd17, 32'd13, 32'd7072};
                40'h0000000187: frozen_conv_tile_lookup = {32'd17, 32'd15, 32'd8160};
                40'h0000000188: frozen_conv_tile_lookup = {32'd17, 32'd17, 32'd9248};
                40'h0000000200: frozen_conv_tile_lookup = {32'd2, 32'd2, 32'd256};
                40'h0000000201: frozen_conv_tile_lookup = {32'd2, 32'd3, 32'd384};
                40'h0000000202: frozen_conv_tile_lookup = {32'd2, 32'd4, 32'd512};
                40'h0000000203: frozen_conv_tile_lookup = {32'd2, 32'd5, 32'd640};
                40'h0000000204: frozen_conv_tile_lookup = {32'd2, 32'd6, 32'd768};
                40'h0000000205: frozen_conv_tile_lookup = {32'd2, 32'd7, 32'd896};
                40'h0000000206: frozen_conv_tile_lookup = {32'd2, 32'd8, 32'd1024};
                40'h0000000207: frozen_conv_tile_lookup = {32'd2, 32'd9, 32'd1152};
                40'h0000000208: frozen_conv_tile_lookup = {32'd2, 32'd10, 32'd1280};
                40'h0000000210: frozen_conv_tile_lookup = {32'd3, 32'd2, 32'd384};
                40'h0000000211: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd576};
                40'h0000000212: frozen_conv_tile_lookup = {32'd3, 32'd4, 32'd768};
                40'h0000000213: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd960};
                40'h0000000214: frozen_conv_tile_lookup = {32'd3, 32'd6, 32'd1152};
                40'h0000000215: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd1344};
                40'h0000000216: frozen_conv_tile_lookup = {32'd3, 32'd8, 32'd1536};
                40'h0000000217: frozen_conv_tile_lookup = {32'd3, 32'd9, 32'd1728};
                40'h0000000218: frozen_conv_tile_lookup = {32'd3, 32'd10, 32'd1920};
                40'h0000000220: frozen_conv_tile_lookup = {32'd4, 32'd2, 32'd512};
                40'h0000000221: frozen_conv_tile_lookup = {32'd4, 32'd3, 32'd768};
                40'h0000000222: frozen_conv_tile_lookup = {32'd4, 32'd4, 32'd1024};
                40'h0000000223: frozen_conv_tile_lookup = {32'd4, 32'd5, 32'd1280};
                40'h0000000224: frozen_conv_tile_lookup = {32'd4, 32'd6, 32'd1536};
                40'h0000000225: frozen_conv_tile_lookup = {32'd4, 32'd7, 32'd1792};
                40'h0000000226: frozen_conv_tile_lookup = {32'd4, 32'd8, 32'd2048};
                40'h0000000227: frozen_conv_tile_lookup = {32'd4, 32'd9, 32'd2304};
                40'h0000000228: frozen_conv_tile_lookup = {32'd4, 32'd10, 32'd2560};
                40'h0000000230: frozen_conv_tile_lookup = {32'd5, 32'd2, 32'd640};
                40'h0000000231: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd960};
                40'h0000000232: frozen_conv_tile_lookup = {32'd5, 32'd4, 32'd1280};
                40'h0000000233: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd1600};
                40'h0000000234: frozen_conv_tile_lookup = {32'd5, 32'd6, 32'd1920};
                40'h0000000235: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd2240};
                40'h0000000236: frozen_conv_tile_lookup = {32'd5, 32'd8, 32'd2560};
                40'h0000000237: frozen_conv_tile_lookup = {32'd5, 32'd9, 32'd2880};
                40'h0000000238: frozen_conv_tile_lookup = {32'd5, 32'd10, 32'd3200};
                40'h0000000240: frozen_conv_tile_lookup = {32'd6, 32'd2, 32'd768};
                40'h0000000241: frozen_conv_tile_lookup = {32'd6, 32'd3, 32'd1152};
                40'h0000000242: frozen_conv_tile_lookup = {32'd6, 32'd4, 32'd1536};
                40'h0000000243: frozen_conv_tile_lookup = {32'd6, 32'd5, 32'd1920};
                40'h0000000244: frozen_conv_tile_lookup = {32'd6, 32'd6, 32'd2304};
                40'h0000000245: frozen_conv_tile_lookup = {32'd6, 32'd7, 32'd2688};
                40'h0000000246: frozen_conv_tile_lookup = {32'd6, 32'd8, 32'd3072};
                40'h0000000247: frozen_conv_tile_lookup = {32'd6, 32'd9, 32'd3456};
                40'h0000000248: frozen_conv_tile_lookup = {32'd6, 32'd10, 32'd3840};
                40'h0000000250: frozen_conv_tile_lookup = {32'd7, 32'd2, 32'd896};
                40'h0000000251: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd1344};
                40'h0000000252: frozen_conv_tile_lookup = {32'd7, 32'd4, 32'd1792};
                40'h0000000253: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd2240};
                40'h0000000254: frozen_conv_tile_lookup = {32'd7, 32'd6, 32'd2688};
                40'h0000000255: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd3136};
                40'h0000000256: frozen_conv_tile_lookup = {32'd7, 32'd8, 32'd3584};
                40'h0000000257: frozen_conv_tile_lookup = {32'd7, 32'd9, 32'd4032};
                40'h0000000258: frozen_conv_tile_lookup = {32'd7, 32'd10, 32'd4480};
                40'h0000000260: frozen_conv_tile_lookup = {32'd8, 32'd2, 32'd1024};
                40'h0000000261: frozen_conv_tile_lookup = {32'd8, 32'd3, 32'd1536};
                40'h0000000262: frozen_conv_tile_lookup = {32'd8, 32'd4, 32'd2048};
                40'h0000000263: frozen_conv_tile_lookup = {32'd8, 32'd5, 32'd2560};
                40'h0000000264: frozen_conv_tile_lookup = {32'd8, 32'd6, 32'd3072};
                40'h0000000265: frozen_conv_tile_lookup = {32'd8, 32'd7, 32'd3584};
                40'h0000000266: frozen_conv_tile_lookup = {32'd8, 32'd8, 32'd4096};
                40'h0000000267: frozen_conv_tile_lookup = {32'd8, 32'd9, 32'd4608};
                40'h0000000268: frozen_conv_tile_lookup = {32'd8, 32'd10, 32'd5120};
                40'h0000000270: frozen_conv_tile_lookup = {32'd9, 32'd2, 32'd1152};
                40'h0000000271: frozen_conv_tile_lookup = {32'd9, 32'd3, 32'd1728};
                40'h0000000272: frozen_conv_tile_lookup = {32'd9, 32'd4, 32'd2304};
                40'h0000000273: frozen_conv_tile_lookup = {32'd9, 32'd5, 32'd2880};
                40'h0000000274: frozen_conv_tile_lookup = {32'd9, 32'd6, 32'd3456};
                40'h0000000275: frozen_conv_tile_lookup = {32'd9, 32'd7, 32'd4032};
                40'h0000000276: frozen_conv_tile_lookup = {32'd9, 32'd8, 32'd4608};
                40'h0000000277: frozen_conv_tile_lookup = {32'd9, 32'd9, 32'd5184};
                40'h0000000278: frozen_conv_tile_lookup = {32'd9, 32'd10, 32'd5760};
                40'h0000000280: frozen_conv_tile_lookup = {32'd10, 32'd2, 32'd1280};
                40'h0000000281: frozen_conv_tile_lookup = {32'd10, 32'd3, 32'd1920};
                40'h0000000282: frozen_conv_tile_lookup = {32'd10, 32'd4, 32'd2560};
                40'h0000000283: frozen_conv_tile_lookup = {32'd10, 32'd5, 32'd3200};
                40'h0000000284: frozen_conv_tile_lookup = {32'd10, 32'd6, 32'd3840};
                40'h0000000285: frozen_conv_tile_lookup = {32'd10, 32'd7, 32'd4480};
                40'h0000000286: frozen_conv_tile_lookup = {32'd10, 32'd8, 32'd5120};
                40'h0000000287: frozen_conv_tile_lookup = {32'd10, 32'd9, 32'd5760};
                40'h0000000288: frozen_conv_tile_lookup = {32'd10, 32'd10, 32'd6400};
                40'h0000000400: frozen_conv_tile_lookup = {32'd2, 32'd2, 32'd128};
                40'h0000000401: frozen_conv_tile_lookup = {32'd2, 32'd3, 32'd192};
                40'h0000000402: frozen_conv_tile_lookup = {32'd2, 32'd4, 32'd256};
                40'h0000000403: frozen_conv_tile_lookup = {32'd2, 32'd5, 32'd320};
                40'h0000000404: frozen_conv_tile_lookup = {32'd2, 32'd6, 32'd384};
                40'h0000000405: frozen_conv_tile_lookup = {32'd2, 32'd7, 32'd448};
                40'h0000000406: frozen_conv_tile_lookup = {32'd2, 32'd8, 32'd512};
                40'h0000000407: frozen_conv_tile_lookup = {32'd2, 32'd9, 32'd576};
                40'h0000000408: frozen_conv_tile_lookup = {32'd2, 32'd10, 32'd640};
                40'h0000000410: frozen_conv_tile_lookup = {32'd3, 32'd2, 32'd192};
                40'h0000000411: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd288};
                40'h0000000412: frozen_conv_tile_lookup = {32'd3, 32'd4, 32'd384};
                40'h0000000413: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd480};
                40'h0000000414: frozen_conv_tile_lookup = {32'd3, 32'd6, 32'd576};
                40'h0000000415: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd672};
                40'h0000000416: frozen_conv_tile_lookup = {32'd3, 32'd8, 32'd768};
                40'h0000000417: frozen_conv_tile_lookup = {32'd3, 32'd9, 32'd864};
                40'h0000000418: frozen_conv_tile_lookup = {32'd3, 32'd10, 32'd960};
                40'h0000000420: frozen_conv_tile_lookup = {32'd4, 32'd2, 32'd256};
                40'h0000000421: frozen_conv_tile_lookup = {32'd4, 32'd3, 32'd384};
                40'h0000000422: frozen_conv_tile_lookup = {32'd4, 32'd4, 32'd512};
                40'h0000000423: frozen_conv_tile_lookup = {32'd4, 32'd5, 32'd640};
                40'h0000000424: frozen_conv_tile_lookup = {32'd4, 32'd6, 32'd768};
                40'h0000000425: frozen_conv_tile_lookup = {32'd4, 32'd7, 32'd896};
                40'h0000000426: frozen_conv_tile_lookup = {32'd4, 32'd8, 32'd1024};
                40'h0000000427: frozen_conv_tile_lookup = {32'd4, 32'd9, 32'd1152};
                40'h0000000428: frozen_conv_tile_lookup = {32'd4, 32'd10, 32'd1280};
                40'h0000000430: frozen_conv_tile_lookup = {32'd5, 32'd2, 32'd320};
                40'h0000000431: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd480};
                40'h0000000432: frozen_conv_tile_lookup = {32'd5, 32'd4, 32'd640};
                40'h0000000433: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd800};
                40'h0000000434: frozen_conv_tile_lookup = {32'd5, 32'd6, 32'd960};
                40'h0000000435: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd1120};
                40'h0000000436: frozen_conv_tile_lookup = {32'd5, 32'd8, 32'd1280};
                40'h0000000437: frozen_conv_tile_lookup = {32'd5, 32'd9, 32'd1440};
                40'h0000000438: frozen_conv_tile_lookup = {32'd5, 32'd10, 32'd1600};
                40'h0000000440: frozen_conv_tile_lookup = {32'd6, 32'd2, 32'd384};
                40'h0000000441: frozen_conv_tile_lookup = {32'd6, 32'd3, 32'd576};
                40'h0000000442: frozen_conv_tile_lookup = {32'd6, 32'd4, 32'd768};
                40'h0000000443: frozen_conv_tile_lookup = {32'd6, 32'd5, 32'd960};
                40'h0000000444: frozen_conv_tile_lookup = {32'd6, 32'd6, 32'd1152};
                40'h0000000445: frozen_conv_tile_lookup = {32'd6, 32'd7, 32'd1344};
                40'h0000000446: frozen_conv_tile_lookup = {32'd6, 32'd8, 32'd1536};
                40'h0000000447: frozen_conv_tile_lookup = {32'd6, 32'd9, 32'd1728};
                40'h0000000448: frozen_conv_tile_lookup = {32'd6, 32'd10, 32'd1920};
                40'h0000000450: frozen_conv_tile_lookup = {32'd7, 32'd2, 32'd448};
                40'h0000000451: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd672};
                40'h0000000452: frozen_conv_tile_lookup = {32'd7, 32'd4, 32'd896};
                40'h0000000453: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd1120};
                40'h0000000454: frozen_conv_tile_lookup = {32'd7, 32'd6, 32'd1344};
                40'h0000000455: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd1568};
                40'h0000000456: frozen_conv_tile_lookup = {32'd7, 32'd8, 32'd1792};
                40'h0000000457: frozen_conv_tile_lookup = {32'd7, 32'd9, 32'd2016};
                40'h0000000458: frozen_conv_tile_lookup = {32'd7, 32'd10, 32'd2240};
                40'h0000000460: frozen_conv_tile_lookup = {32'd8, 32'd2, 32'd512};
                40'h0000000461: frozen_conv_tile_lookup = {32'd8, 32'd3, 32'd768};
                40'h0000000462: frozen_conv_tile_lookup = {32'd8, 32'd4, 32'd1024};
                40'h0000000463: frozen_conv_tile_lookup = {32'd8, 32'd5, 32'd1280};
                40'h0000000464: frozen_conv_tile_lookup = {32'd8, 32'd6, 32'd1536};
                40'h0000000465: frozen_conv_tile_lookup = {32'd8, 32'd7, 32'd1792};
                40'h0000000466: frozen_conv_tile_lookup = {32'd8, 32'd8, 32'd2048};
                40'h0000000467: frozen_conv_tile_lookup = {32'd8, 32'd9, 32'd2304};
                40'h0000000468: frozen_conv_tile_lookup = {32'd8, 32'd10, 32'd2560};
                40'h0000000470: frozen_conv_tile_lookup = {32'd9, 32'd2, 32'd576};
                40'h0000000471: frozen_conv_tile_lookup = {32'd9, 32'd3, 32'd864};
                40'h0000000472: frozen_conv_tile_lookup = {32'd9, 32'd4, 32'd1152};
                40'h0000000473: frozen_conv_tile_lookup = {32'd9, 32'd5, 32'd1440};
                40'h0000000474: frozen_conv_tile_lookup = {32'd9, 32'd6, 32'd1728};
                40'h0000000475: frozen_conv_tile_lookup = {32'd9, 32'd7, 32'd2016};
                40'h0000000476: frozen_conv_tile_lookup = {32'd9, 32'd8, 32'd2304};
                40'h0000000477: frozen_conv_tile_lookup = {32'd9, 32'd9, 32'd2592};
                40'h0000000478: frozen_conv_tile_lookup = {32'd9, 32'd10, 32'd2880};
                40'h0000000480: frozen_conv_tile_lookup = {32'd10, 32'd2, 32'd640};
                40'h0000000481: frozen_conv_tile_lookup = {32'd10, 32'd3, 32'd960};
                40'h0000000482: frozen_conv_tile_lookup = {32'd10, 32'd4, 32'd1280};
                40'h0000000483: frozen_conv_tile_lookup = {32'd10, 32'd5, 32'd1600};
                40'h0000000484: frozen_conv_tile_lookup = {32'd10, 32'd6, 32'd1920};
                40'h0000000485: frozen_conv_tile_lookup = {32'd10, 32'd7, 32'd2240};
                40'h0000000486: frozen_conv_tile_lookup = {32'd10, 32'd8, 32'd2560};
                40'h0000000487: frozen_conv_tile_lookup = {32'd10, 32'd9, 32'd2880};
                40'h0000000488: frozen_conv_tile_lookup = {32'd10, 32'd10, 32'd3200};
                40'h0000000500: frozen_conv_tile_lookup = {32'd2, 32'd2, 32'd128};
                40'h0000000501: frozen_conv_tile_lookup = {32'd2, 32'd3, 32'd192};
                40'h0000000502: frozen_conv_tile_lookup = {32'd2, 32'd4, 32'd256};
                40'h0000000503: frozen_conv_tile_lookup = {32'd2, 32'd5, 32'd320};
                40'h0000000504: frozen_conv_tile_lookup = {32'd2, 32'd6, 32'd384};
                40'h0000000505: frozen_conv_tile_lookup = {32'd2, 32'd7, 32'd448};
                40'h0000000506: frozen_conv_tile_lookup = {32'd2, 32'd8, 32'd512};
                40'h0000000507: frozen_conv_tile_lookup = {32'd2, 32'd9, 32'd576};
                40'h0000000508: frozen_conv_tile_lookup = {32'd2, 32'd10, 32'd640};
                40'h0000000510: frozen_conv_tile_lookup = {32'd3, 32'd2, 32'd192};
                40'h0000000511: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd288};
                40'h0000000512: frozen_conv_tile_lookup = {32'd3, 32'd4, 32'd384};
                40'h0000000513: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd480};
                40'h0000000514: frozen_conv_tile_lookup = {32'd3, 32'd6, 32'd576};
                40'h0000000515: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd672};
                40'h0000000516: frozen_conv_tile_lookup = {32'd3, 32'd8, 32'd768};
                40'h0000000517: frozen_conv_tile_lookup = {32'd3, 32'd9, 32'd864};
                40'h0000000518: frozen_conv_tile_lookup = {32'd3, 32'd10, 32'd960};
                40'h0000000520: frozen_conv_tile_lookup = {32'd4, 32'd2, 32'd256};
                40'h0000000521: frozen_conv_tile_lookup = {32'd4, 32'd3, 32'd384};
                40'h0000000522: frozen_conv_tile_lookup = {32'd4, 32'd4, 32'd512};
                40'h0000000523: frozen_conv_tile_lookup = {32'd4, 32'd5, 32'd640};
                40'h0000000524: frozen_conv_tile_lookup = {32'd4, 32'd6, 32'd768};
                40'h0000000525: frozen_conv_tile_lookup = {32'd4, 32'd7, 32'd896};
                40'h0000000526: frozen_conv_tile_lookup = {32'd4, 32'd8, 32'd1024};
                40'h0000000527: frozen_conv_tile_lookup = {32'd4, 32'd9, 32'd1152};
                40'h0000000528: frozen_conv_tile_lookup = {32'd4, 32'd10, 32'd1280};
                40'h0000000530: frozen_conv_tile_lookup = {32'd5, 32'd2, 32'd320};
                40'h0000000531: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd480};
                40'h0000000532: frozen_conv_tile_lookup = {32'd5, 32'd4, 32'd640};
                40'h0000000533: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd800};
                40'h0000000534: frozen_conv_tile_lookup = {32'd5, 32'd6, 32'd960};
                40'h0000000535: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd1120};
                40'h0000000536: frozen_conv_tile_lookup = {32'd5, 32'd8, 32'd1280};
                40'h0000000537: frozen_conv_tile_lookup = {32'd5, 32'd9, 32'd1440};
                40'h0000000538: frozen_conv_tile_lookup = {32'd5, 32'd10, 32'd1600};
                40'h0000000540: frozen_conv_tile_lookup = {32'd6, 32'd2, 32'd384};
                40'h0000000541: frozen_conv_tile_lookup = {32'd6, 32'd3, 32'd576};
                40'h0000000542: frozen_conv_tile_lookup = {32'd6, 32'd4, 32'd768};
                40'h0000000543: frozen_conv_tile_lookup = {32'd6, 32'd5, 32'd960};
                40'h0000000544: frozen_conv_tile_lookup = {32'd6, 32'd6, 32'd1152};
                40'h0000000545: frozen_conv_tile_lookup = {32'd6, 32'd7, 32'd1344};
                40'h0000000546: frozen_conv_tile_lookup = {32'd6, 32'd8, 32'd1536};
                40'h0000000547: frozen_conv_tile_lookup = {32'd6, 32'd9, 32'd1728};
                40'h0000000548: frozen_conv_tile_lookup = {32'd6, 32'd10, 32'd1920};
                40'h0000000550: frozen_conv_tile_lookup = {32'd7, 32'd2, 32'd448};
                40'h0000000551: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd672};
                40'h0000000552: frozen_conv_tile_lookup = {32'd7, 32'd4, 32'd896};
                40'h0000000553: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd1120};
                40'h0000000554: frozen_conv_tile_lookup = {32'd7, 32'd6, 32'd1344};
                40'h0000000555: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd1568};
                40'h0000000556: frozen_conv_tile_lookup = {32'd7, 32'd8, 32'd1792};
                40'h0000000557: frozen_conv_tile_lookup = {32'd7, 32'd9, 32'd2016};
                40'h0000000558: frozen_conv_tile_lookup = {32'd7, 32'd10, 32'd2240};
                40'h0000000560: frozen_conv_tile_lookup = {32'd8, 32'd2, 32'd512};
                40'h0000000561: frozen_conv_tile_lookup = {32'd8, 32'd3, 32'd768};
                40'h0000000562: frozen_conv_tile_lookup = {32'd8, 32'd4, 32'd1024};
                40'h0000000563: frozen_conv_tile_lookup = {32'd8, 32'd5, 32'd1280};
                40'h0000000564: frozen_conv_tile_lookup = {32'd8, 32'd6, 32'd1536};
                40'h0000000565: frozen_conv_tile_lookup = {32'd8, 32'd7, 32'd1792};
                40'h0000000566: frozen_conv_tile_lookup = {32'd8, 32'd8, 32'd2048};
                40'h0000000567: frozen_conv_tile_lookup = {32'd8, 32'd9, 32'd2304};
                40'h0000000568: frozen_conv_tile_lookup = {32'd8, 32'd10, 32'd2560};
                40'h0000000570: frozen_conv_tile_lookup = {32'd9, 32'd2, 32'd576};
                40'h0000000571: frozen_conv_tile_lookup = {32'd9, 32'd3, 32'd864};
                40'h0000000572: frozen_conv_tile_lookup = {32'd9, 32'd4, 32'd1152};
                40'h0000000573: frozen_conv_tile_lookup = {32'd9, 32'd5, 32'd1440};
                40'h0000000574: frozen_conv_tile_lookup = {32'd9, 32'd6, 32'd1728};
                40'h0000000575: frozen_conv_tile_lookup = {32'd9, 32'd7, 32'd2016};
                40'h0000000576: frozen_conv_tile_lookup = {32'd9, 32'd8, 32'd2304};
                40'h0000000577: frozen_conv_tile_lookup = {32'd9, 32'd9, 32'd2592};
                40'h0000000578: frozen_conv_tile_lookup = {32'd9, 32'd10, 32'd2880};
                40'h0000000580: frozen_conv_tile_lookup = {32'd10, 32'd2, 32'd640};
                40'h0000000581: frozen_conv_tile_lookup = {32'd10, 32'd3, 32'd960};
                40'h0000000582: frozen_conv_tile_lookup = {32'd10, 32'd4, 32'd1280};
                40'h0000000583: frozen_conv_tile_lookup = {32'd10, 32'd5, 32'd1600};
                40'h0000000584: frozen_conv_tile_lookup = {32'd10, 32'd6, 32'd1920};
                40'h0000000585: frozen_conv_tile_lookup = {32'd10, 32'd7, 32'd2240};
                40'h0000000586: frozen_conv_tile_lookup = {32'd10, 32'd8, 32'd2560};
                40'h0000000587: frozen_conv_tile_lookup = {32'd10, 32'd9, 32'd2880};
                40'h0000000588: frozen_conv_tile_lookup = {32'd10, 32'd10, 32'd3200};
                40'h0000000700: frozen_conv_tile_lookup = {32'd0, 32'd0, 32'd0};
                40'h0000000701: frozen_conv_tile_lookup = {32'd0, 32'd1, 32'd0};
                40'h0000000702: frozen_conv_tile_lookup = {32'd0, 32'd2, 32'd0};
                40'h0000000703: frozen_conv_tile_lookup = {32'd0, 32'd3, 32'd0};
                40'h0000000704: frozen_conv_tile_lookup = {32'd0, 32'd4, 32'd0};
                40'h0000000705: frozen_conv_tile_lookup = {32'd0, 32'd5, 32'd0};
                40'h0000000706: frozen_conv_tile_lookup = {32'd0, 32'd6, 32'd0};
                40'h0000000707: frozen_conv_tile_lookup = {32'd0, 32'd7, 32'd0};
                40'h0000000708: frozen_conv_tile_lookup = {32'd0, 32'd8, 32'd0};
                40'h0000000710: frozen_conv_tile_lookup = {32'd1, 32'd0, 32'd0};
                40'h0000000711: frozen_conv_tile_lookup = {32'd1, 32'd1, 32'd64};
                40'h0000000712: frozen_conv_tile_lookup = {32'd1, 32'd2, 32'd128};
                40'h0000000713: frozen_conv_tile_lookup = {32'd1, 32'd3, 32'd192};
                40'h0000000714: frozen_conv_tile_lookup = {32'd1, 32'd4, 32'd256};
                40'h0000000715: frozen_conv_tile_lookup = {32'd1, 32'd5, 32'd320};
                40'h0000000716: frozen_conv_tile_lookup = {32'd1, 32'd6, 32'd384};
                40'h0000000717: frozen_conv_tile_lookup = {32'd1, 32'd7, 32'd448};
                40'h0000000718: frozen_conv_tile_lookup = {32'd1, 32'd8, 32'd512};
                40'h0000000720: frozen_conv_tile_lookup = {32'd2, 32'd0, 32'd0};
                40'h0000000721: frozen_conv_tile_lookup = {32'd2, 32'd1, 32'd128};
                40'h0000000722: frozen_conv_tile_lookup = {32'd2, 32'd2, 32'd256};
                40'h0000000723: frozen_conv_tile_lookup = {32'd2, 32'd3, 32'd384};
                40'h0000000724: frozen_conv_tile_lookup = {32'd2, 32'd4, 32'd512};
                40'h0000000725: frozen_conv_tile_lookup = {32'd2, 32'd5, 32'd640};
                40'h0000000726: frozen_conv_tile_lookup = {32'd2, 32'd6, 32'd768};
                40'h0000000727: frozen_conv_tile_lookup = {32'd2, 32'd7, 32'd896};
                40'h0000000728: frozen_conv_tile_lookup = {32'd2, 32'd8, 32'd1024};
                40'h0000000730: frozen_conv_tile_lookup = {32'd3, 32'd0, 32'd0};
                40'h0000000731: frozen_conv_tile_lookup = {32'd3, 32'd1, 32'd192};
                40'h0000000732: frozen_conv_tile_lookup = {32'd3, 32'd2, 32'd384};
                40'h0000000733: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd576};
                40'h0000000734: frozen_conv_tile_lookup = {32'd3, 32'd4, 32'd768};
                40'h0000000735: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd960};
                40'h0000000736: frozen_conv_tile_lookup = {32'd3, 32'd6, 32'd1152};
                40'h0000000737: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd1344};
                40'h0000000738: frozen_conv_tile_lookup = {32'd3, 32'd8, 32'd1536};
                40'h0000000740: frozen_conv_tile_lookup = {32'd4, 32'd0, 32'd0};
                40'h0000000741: frozen_conv_tile_lookup = {32'd4, 32'd1, 32'd256};
                40'h0000000742: frozen_conv_tile_lookup = {32'd4, 32'd2, 32'd512};
                40'h0000000743: frozen_conv_tile_lookup = {32'd4, 32'd3, 32'd768};
                40'h0000000744: frozen_conv_tile_lookup = {32'd4, 32'd4, 32'd1024};
                40'h0000000745: frozen_conv_tile_lookup = {32'd4, 32'd5, 32'd1280};
                40'h0000000746: frozen_conv_tile_lookup = {32'd4, 32'd6, 32'd1536};
                40'h0000000747: frozen_conv_tile_lookup = {32'd4, 32'd7, 32'd1792};
                40'h0000000748: frozen_conv_tile_lookup = {32'd4, 32'd8, 32'd2048};
                40'h0000000750: frozen_conv_tile_lookup = {32'd5, 32'd0, 32'd0};
                40'h0000000751: frozen_conv_tile_lookup = {32'd5, 32'd1, 32'd320};
                40'h0000000752: frozen_conv_tile_lookup = {32'd5, 32'd2, 32'd640};
                40'h0000000753: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd960};
                40'h0000000754: frozen_conv_tile_lookup = {32'd5, 32'd4, 32'd1280};
                40'h0000000755: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd1600};
                40'h0000000756: frozen_conv_tile_lookup = {32'd5, 32'd6, 32'd1920};
                40'h0000000757: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd2240};
                40'h0000000758: frozen_conv_tile_lookup = {32'd5, 32'd8, 32'd2560};
                40'h0000000760: frozen_conv_tile_lookup = {32'd6, 32'd0, 32'd0};
                40'h0000000761: frozen_conv_tile_lookup = {32'd6, 32'd1, 32'd384};
                40'h0000000762: frozen_conv_tile_lookup = {32'd6, 32'd2, 32'd768};
                40'h0000000763: frozen_conv_tile_lookup = {32'd6, 32'd3, 32'd1152};
                40'h0000000764: frozen_conv_tile_lookup = {32'd6, 32'd4, 32'd1536};
                40'h0000000765: frozen_conv_tile_lookup = {32'd6, 32'd5, 32'd1920};
                40'h0000000766: frozen_conv_tile_lookup = {32'd6, 32'd6, 32'd2304};
                40'h0000000767: frozen_conv_tile_lookup = {32'd6, 32'd7, 32'd2688};
                40'h0000000768: frozen_conv_tile_lookup = {32'd6, 32'd8, 32'd3072};
                40'h0000000770: frozen_conv_tile_lookup = {32'd7, 32'd0, 32'd0};
                40'h0000000771: frozen_conv_tile_lookup = {32'd7, 32'd1, 32'd448};
                40'h0000000772: frozen_conv_tile_lookup = {32'd7, 32'd2, 32'd896};
                40'h0000000773: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd1344};
                40'h0000000774: frozen_conv_tile_lookup = {32'd7, 32'd4, 32'd1792};
                40'h0000000775: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd2240};
                40'h0000000776: frozen_conv_tile_lookup = {32'd7, 32'd6, 32'd2688};
                40'h0000000777: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd3136};
                40'h0000000778: frozen_conv_tile_lookup = {32'd7, 32'd8, 32'd3584};
                40'h0000000780: frozen_conv_tile_lookup = {32'd8, 32'd0, 32'd0};
                40'h0000000781: frozen_conv_tile_lookup = {32'd8, 32'd1, 32'd512};
                40'h0000000782: frozen_conv_tile_lookup = {32'd8, 32'd2, 32'd1024};
                40'h0000000783: frozen_conv_tile_lookup = {32'd8, 32'd3, 32'd1536};
                40'h0000000784: frozen_conv_tile_lookup = {32'd8, 32'd4, 32'd2048};
                40'h0000000785: frozen_conv_tile_lookup = {32'd8, 32'd5, 32'd2560};
                40'h0000000786: frozen_conv_tile_lookup = {32'd8, 32'd6, 32'd3072};
                40'h0000000787: frozen_conv_tile_lookup = {32'd8, 32'd7, 32'd3584};
                40'h0000000788: frozen_conv_tile_lookup = {32'd8, 32'd8, 32'd4096};
                40'h0000000A00: frozen_conv_tile_lookup = {32'd2, 32'd2, 32'd512};
                40'h0000000A01: frozen_conv_tile_lookup = {32'd2, 32'd3, 32'd768};
                40'h0000000A02: frozen_conv_tile_lookup = {32'd2, 32'd4, 32'd1024};
                40'h0000000A03: frozen_conv_tile_lookup = {32'd2, 32'd5, 32'd1280};
                40'h0000000A04: frozen_conv_tile_lookup = {32'd2, 32'd6, 32'd1536};
                40'h0000000A05: frozen_conv_tile_lookup = {32'd2, 32'd7, 32'd1792};
                40'h0000000A06: frozen_conv_tile_lookup = {32'd2, 32'd8, 32'd2048};
                40'h0000000A07: frozen_conv_tile_lookup = {32'd2, 32'd9, 32'd2304};
                40'h0000000A08: frozen_conv_tile_lookup = {32'd2, 32'd10, 32'd2560};
                40'h0000000A10: frozen_conv_tile_lookup = {32'd3, 32'd2, 32'd768};
                40'h0000000A11: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd1152};
                40'h0000000A12: frozen_conv_tile_lookup = {32'd3, 32'd4, 32'd1536};
                40'h0000000A13: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd1920};
                40'h0000000A14: frozen_conv_tile_lookup = {32'd3, 32'd6, 32'd2304};
                40'h0000000A15: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd2688};
                40'h0000000A16: frozen_conv_tile_lookup = {32'd3, 32'd8, 32'd3072};
                40'h0000000A17: frozen_conv_tile_lookup = {32'd3, 32'd9, 32'd3456};
                40'h0000000A18: frozen_conv_tile_lookup = {32'd3, 32'd10, 32'd3840};
                40'h0000000A20: frozen_conv_tile_lookup = {32'd4, 32'd2, 32'd1024};
                40'h0000000A21: frozen_conv_tile_lookup = {32'd4, 32'd3, 32'd1536};
                40'h0000000A22: frozen_conv_tile_lookup = {32'd4, 32'd4, 32'd2048};
                40'h0000000A23: frozen_conv_tile_lookup = {32'd4, 32'd5, 32'd2560};
                40'h0000000A24: frozen_conv_tile_lookup = {32'd4, 32'd6, 32'd3072};
                40'h0000000A25: frozen_conv_tile_lookup = {32'd4, 32'd7, 32'd3584};
                40'h0000000A26: frozen_conv_tile_lookup = {32'd4, 32'd8, 32'd4096};
                40'h0000000A27: frozen_conv_tile_lookup = {32'd4, 32'd9, 32'd4608};
                40'h0000000A28: frozen_conv_tile_lookup = {32'd4, 32'd10, 32'd5120};
                40'h0000000A30: frozen_conv_tile_lookup = {32'd5, 32'd2, 32'd1280};
                40'h0000000A31: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd1920};
                40'h0000000A32: frozen_conv_tile_lookup = {32'd5, 32'd4, 32'd2560};
                40'h0000000A33: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd3200};
                40'h0000000A34: frozen_conv_tile_lookup = {32'd5, 32'd6, 32'd3840};
                40'h0000000A35: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd4480};
                40'h0000000A36: frozen_conv_tile_lookup = {32'd5, 32'd8, 32'd5120};
                40'h0000000A37: frozen_conv_tile_lookup = {32'd5, 32'd9, 32'd5760};
                40'h0000000A38: frozen_conv_tile_lookup = {32'd5, 32'd10, 32'd6400};
                40'h0000000A40: frozen_conv_tile_lookup = {32'd6, 32'd2, 32'd1536};
                40'h0000000A41: frozen_conv_tile_lookup = {32'd6, 32'd3, 32'd2304};
                40'h0000000A42: frozen_conv_tile_lookup = {32'd6, 32'd4, 32'd3072};
                40'h0000000A43: frozen_conv_tile_lookup = {32'd6, 32'd5, 32'd3840};
                40'h0000000A44: frozen_conv_tile_lookup = {32'd6, 32'd6, 32'd4608};
                40'h0000000A45: frozen_conv_tile_lookup = {32'd6, 32'd7, 32'd5376};
                40'h0000000A46: frozen_conv_tile_lookup = {32'd6, 32'd8, 32'd6144};
                40'h0000000A47: frozen_conv_tile_lookup = {32'd6, 32'd9, 32'd6912};
                40'h0000000A48: frozen_conv_tile_lookup = {32'd6, 32'd10, 32'd7680};
                40'h0000000A50: frozen_conv_tile_lookup = {32'd7, 32'd2, 32'd1792};
                40'h0000000A51: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd2688};
                40'h0000000A52: frozen_conv_tile_lookup = {32'd7, 32'd4, 32'd3584};
                40'h0000000A53: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd4480};
                40'h0000000A54: frozen_conv_tile_lookup = {32'd7, 32'd6, 32'd5376};
                40'h0000000A55: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd6272};
                40'h0000000A56: frozen_conv_tile_lookup = {32'd7, 32'd8, 32'd7168};
                40'h0000000A57: frozen_conv_tile_lookup = {32'd7, 32'd9, 32'd8064};
                40'h0000000A58: frozen_conv_tile_lookup = {32'd7, 32'd10, 32'd8960};
                40'h0000000A60: frozen_conv_tile_lookup = {32'd8, 32'd2, 32'd2048};
                40'h0000000A61: frozen_conv_tile_lookup = {32'd8, 32'd3, 32'd3072};
                40'h0000000A62: frozen_conv_tile_lookup = {32'd8, 32'd4, 32'd4096};
                40'h0000000A63: frozen_conv_tile_lookup = {32'd8, 32'd5, 32'd5120};
                40'h0000000A64: frozen_conv_tile_lookup = {32'd8, 32'd6, 32'd6144};
                40'h0000000A65: frozen_conv_tile_lookup = {32'd8, 32'd7, 32'd7168};
                40'h0000000A66: frozen_conv_tile_lookup = {32'd8, 32'd8, 32'd8192};
                40'h0000000A67: frozen_conv_tile_lookup = {32'd8, 32'd9, 32'd9216};
                40'h0000000A68: frozen_conv_tile_lookup = {32'd8, 32'd10, 32'd10240};
                40'h0000000A70: frozen_conv_tile_lookup = {32'd9, 32'd2, 32'd2304};
                40'h0000000A71: frozen_conv_tile_lookup = {32'd9, 32'd3, 32'd3456};
                40'h0000000A72: frozen_conv_tile_lookup = {32'd9, 32'd4, 32'd4608};
                40'h0000000A73: frozen_conv_tile_lookup = {32'd9, 32'd5, 32'd5760};
                40'h0000000A74: frozen_conv_tile_lookup = {32'd9, 32'd6, 32'd6912};
                40'h0000000A75: frozen_conv_tile_lookup = {32'd9, 32'd7, 32'd8064};
                40'h0000000A76: frozen_conv_tile_lookup = {32'd9, 32'd8, 32'd9216};
                40'h0000000A77: frozen_conv_tile_lookup = {32'd9, 32'd9, 32'd10368};
                40'h0000000A78: frozen_conv_tile_lookup = {32'd9, 32'd10, 32'd11520};
                40'h0000000A80: frozen_conv_tile_lookup = {32'd10, 32'd2, 32'd2560};
                40'h0000000A81: frozen_conv_tile_lookup = {32'd10, 32'd3, 32'd3840};
                40'h0000000A82: frozen_conv_tile_lookup = {32'd10, 32'd4, 32'd5120};
                40'h0000000A83: frozen_conv_tile_lookup = {32'd10, 32'd5, 32'd6400};
                40'h0000000A84: frozen_conv_tile_lookup = {32'd10, 32'd6, 32'd7680};
                40'h0000000A85: frozen_conv_tile_lookup = {32'd10, 32'd7, 32'd8960};
                40'h0000000A86: frozen_conv_tile_lookup = {32'd10, 32'd8, 32'd10240};
                40'h0000000A87: frozen_conv_tile_lookup = {32'd10, 32'd9, 32'd11520};
                40'h0000000A88: frozen_conv_tile_lookup = {32'd10, 32'd10, 32'd12800};
                40'h0000000C00: frozen_conv_tile_lookup = {32'd2, 32'd2, 32'd256};
                40'h0000000C01: frozen_conv_tile_lookup = {32'd2, 32'd3, 32'd384};
                40'h0000000C02: frozen_conv_tile_lookup = {32'd2, 32'd4, 32'd512};
                40'h0000000C03: frozen_conv_tile_lookup = {32'd2, 32'd5, 32'd640};
                40'h0000000C04: frozen_conv_tile_lookup = {32'd2, 32'd6, 32'd768};
                40'h0000000C05: frozen_conv_tile_lookup = {32'd2, 32'd7, 32'd896};
                40'h0000000C06: frozen_conv_tile_lookup = {32'd2, 32'd8, 32'd1024};
                40'h0000000C07: frozen_conv_tile_lookup = {32'd2, 32'd9, 32'd1152};
                40'h0000000C08: frozen_conv_tile_lookup = {32'd2, 32'd10, 32'd1280};
                40'h0000000C10: frozen_conv_tile_lookup = {32'd3, 32'd2, 32'd384};
                40'h0000000C11: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd576};
                40'h0000000C12: frozen_conv_tile_lookup = {32'd3, 32'd4, 32'd768};
                40'h0000000C13: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd960};
                40'h0000000C14: frozen_conv_tile_lookup = {32'd3, 32'd6, 32'd1152};
                40'h0000000C15: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd1344};
                40'h0000000C16: frozen_conv_tile_lookup = {32'd3, 32'd8, 32'd1536};
                40'h0000000C17: frozen_conv_tile_lookup = {32'd3, 32'd9, 32'd1728};
                40'h0000000C18: frozen_conv_tile_lookup = {32'd3, 32'd10, 32'd1920};
                40'h0000000C20: frozen_conv_tile_lookup = {32'd4, 32'd2, 32'd512};
                40'h0000000C21: frozen_conv_tile_lookup = {32'd4, 32'd3, 32'd768};
                40'h0000000C22: frozen_conv_tile_lookup = {32'd4, 32'd4, 32'd1024};
                40'h0000000C23: frozen_conv_tile_lookup = {32'd4, 32'd5, 32'd1280};
                40'h0000000C24: frozen_conv_tile_lookup = {32'd4, 32'd6, 32'd1536};
                40'h0000000C25: frozen_conv_tile_lookup = {32'd4, 32'd7, 32'd1792};
                40'h0000000C26: frozen_conv_tile_lookup = {32'd4, 32'd8, 32'd2048};
                40'h0000000C27: frozen_conv_tile_lookup = {32'd4, 32'd9, 32'd2304};
                40'h0000000C28: frozen_conv_tile_lookup = {32'd4, 32'd10, 32'd2560};
                40'h0000000C30: frozen_conv_tile_lookup = {32'd5, 32'd2, 32'd640};
                40'h0000000C31: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd960};
                40'h0000000C32: frozen_conv_tile_lookup = {32'd5, 32'd4, 32'd1280};
                40'h0000000C33: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd1600};
                40'h0000000C34: frozen_conv_tile_lookup = {32'd5, 32'd6, 32'd1920};
                40'h0000000C35: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd2240};
                40'h0000000C36: frozen_conv_tile_lookup = {32'd5, 32'd8, 32'd2560};
                40'h0000000C37: frozen_conv_tile_lookup = {32'd5, 32'd9, 32'd2880};
                40'h0000000C38: frozen_conv_tile_lookup = {32'd5, 32'd10, 32'd3200};
                40'h0000000C40: frozen_conv_tile_lookup = {32'd6, 32'd2, 32'd768};
                40'h0000000C41: frozen_conv_tile_lookup = {32'd6, 32'd3, 32'd1152};
                40'h0000000C42: frozen_conv_tile_lookup = {32'd6, 32'd4, 32'd1536};
                40'h0000000C43: frozen_conv_tile_lookup = {32'd6, 32'd5, 32'd1920};
                40'h0000000C44: frozen_conv_tile_lookup = {32'd6, 32'd6, 32'd2304};
                40'h0000000C45: frozen_conv_tile_lookup = {32'd6, 32'd7, 32'd2688};
                40'h0000000C46: frozen_conv_tile_lookup = {32'd6, 32'd8, 32'd3072};
                40'h0000000C47: frozen_conv_tile_lookup = {32'd6, 32'd9, 32'd3456};
                40'h0000000C48: frozen_conv_tile_lookup = {32'd6, 32'd10, 32'd3840};
                40'h0000000C50: frozen_conv_tile_lookup = {32'd7, 32'd2, 32'd896};
                40'h0000000C51: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd1344};
                40'h0000000C52: frozen_conv_tile_lookup = {32'd7, 32'd4, 32'd1792};
                40'h0000000C53: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd2240};
                40'h0000000C54: frozen_conv_tile_lookup = {32'd7, 32'd6, 32'd2688};
                40'h0000000C55: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd3136};
                40'h0000000C56: frozen_conv_tile_lookup = {32'd7, 32'd8, 32'd3584};
                40'h0000000C57: frozen_conv_tile_lookup = {32'd7, 32'd9, 32'd4032};
                40'h0000000C58: frozen_conv_tile_lookup = {32'd7, 32'd10, 32'd4480};
                40'h0000000C60: frozen_conv_tile_lookup = {32'd8, 32'd2, 32'd1024};
                40'h0000000C61: frozen_conv_tile_lookup = {32'd8, 32'd3, 32'd1536};
                40'h0000000C62: frozen_conv_tile_lookup = {32'd8, 32'd4, 32'd2048};
                40'h0000000C63: frozen_conv_tile_lookup = {32'd8, 32'd5, 32'd2560};
                40'h0000000C64: frozen_conv_tile_lookup = {32'd8, 32'd6, 32'd3072};
                40'h0000000C65: frozen_conv_tile_lookup = {32'd8, 32'd7, 32'd3584};
                40'h0000000C66: frozen_conv_tile_lookup = {32'd8, 32'd8, 32'd4096};
                40'h0000000C67: frozen_conv_tile_lookup = {32'd8, 32'd9, 32'd4608};
                40'h0000000C68: frozen_conv_tile_lookup = {32'd8, 32'd10, 32'd5120};
                40'h0000000C70: frozen_conv_tile_lookup = {32'd9, 32'd2, 32'd1152};
                40'h0000000C71: frozen_conv_tile_lookup = {32'd9, 32'd3, 32'd1728};
                40'h0000000C72: frozen_conv_tile_lookup = {32'd9, 32'd4, 32'd2304};
                40'h0000000C73: frozen_conv_tile_lookup = {32'd9, 32'd5, 32'd2880};
                40'h0000000C74: frozen_conv_tile_lookup = {32'd9, 32'd6, 32'd3456};
                40'h0000000C75: frozen_conv_tile_lookup = {32'd9, 32'd7, 32'd4032};
                40'h0000000C76: frozen_conv_tile_lookup = {32'd9, 32'd8, 32'd4608};
                40'h0000000C77: frozen_conv_tile_lookup = {32'd9, 32'd9, 32'd5184};
                40'h0000000C78: frozen_conv_tile_lookup = {32'd9, 32'd10, 32'd5760};
                40'h0000000C80: frozen_conv_tile_lookup = {32'd10, 32'd2, 32'd1280};
                40'h0000000C81: frozen_conv_tile_lookup = {32'd10, 32'd3, 32'd1920};
                40'h0000000C82: frozen_conv_tile_lookup = {32'd10, 32'd4, 32'd2560};
                40'h0000000C83: frozen_conv_tile_lookup = {32'd10, 32'd5, 32'd3200};
                40'h0000000C84: frozen_conv_tile_lookup = {32'd10, 32'd6, 32'd3840};
                40'h0000000C85: frozen_conv_tile_lookup = {32'd10, 32'd7, 32'd4480};
                40'h0000000C86: frozen_conv_tile_lookup = {32'd10, 32'd8, 32'd5120};
                40'h0000000C87: frozen_conv_tile_lookup = {32'd10, 32'd9, 32'd5760};
                40'h0000000C88: frozen_conv_tile_lookup = {32'd10, 32'd10, 32'd6400};
                40'h0000000D00: frozen_conv_tile_lookup = {32'd2, 32'd2, 32'd256};
                40'h0000000D01: frozen_conv_tile_lookup = {32'd2, 32'd3, 32'd384};
                40'h0000000D02: frozen_conv_tile_lookup = {32'd2, 32'd4, 32'd512};
                40'h0000000D03: frozen_conv_tile_lookup = {32'd2, 32'd5, 32'd640};
                40'h0000000D04: frozen_conv_tile_lookup = {32'd2, 32'd6, 32'd768};
                40'h0000000D05: frozen_conv_tile_lookup = {32'd2, 32'd7, 32'd896};
                40'h0000000D06: frozen_conv_tile_lookup = {32'd2, 32'd8, 32'd1024};
                40'h0000000D07: frozen_conv_tile_lookup = {32'd2, 32'd9, 32'd1152};
                40'h0000000D08: frozen_conv_tile_lookup = {32'd2, 32'd10, 32'd1280};
                40'h0000000D10: frozen_conv_tile_lookup = {32'd3, 32'd2, 32'd384};
                40'h0000000D11: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd576};
                40'h0000000D12: frozen_conv_tile_lookup = {32'd3, 32'd4, 32'd768};
                40'h0000000D13: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd960};
                40'h0000000D14: frozen_conv_tile_lookup = {32'd3, 32'd6, 32'd1152};
                40'h0000000D15: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd1344};
                40'h0000000D16: frozen_conv_tile_lookup = {32'd3, 32'd8, 32'd1536};
                40'h0000000D17: frozen_conv_tile_lookup = {32'd3, 32'd9, 32'd1728};
                40'h0000000D18: frozen_conv_tile_lookup = {32'd3, 32'd10, 32'd1920};
                40'h0000000D20: frozen_conv_tile_lookup = {32'd4, 32'd2, 32'd512};
                40'h0000000D21: frozen_conv_tile_lookup = {32'd4, 32'd3, 32'd768};
                40'h0000000D22: frozen_conv_tile_lookup = {32'd4, 32'd4, 32'd1024};
                40'h0000000D23: frozen_conv_tile_lookup = {32'd4, 32'd5, 32'd1280};
                40'h0000000D24: frozen_conv_tile_lookup = {32'd4, 32'd6, 32'd1536};
                40'h0000000D25: frozen_conv_tile_lookup = {32'd4, 32'd7, 32'd1792};
                40'h0000000D26: frozen_conv_tile_lookup = {32'd4, 32'd8, 32'd2048};
                40'h0000000D27: frozen_conv_tile_lookup = {32'd4, 32'd9, 32'd2304};
                40'h0000000D28: frozen_conv_tile_lookup = {32'd4, 32'd10, 32'd2560};
                40'h0000000D30: frozen_conv_tile_lookup = {32'd5, 32'd2, 32'd640};
                40'h0000000D31: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd960};
                40'h0000000D32: frozen_conv_tile_lookup = {32'd5, 32'd4, 32'd1280};
                40'h0000000D33: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd1600};
                40'h0000000D34: frozen_conv_tile_lookup = {32'd5, 32'd6, 32'd1920};
                40'h0000000D35: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd2240};
                40'h0000000D36: frozen_conv_tile_lookup = {32'd5, 32'd8, 32'd2560};
                40'h0000000D37: frozen_conv_tile_lookup = {32'd5, 32'd9, 32'd2880};
                40'h0000000D38: frozen_conv_tile_lookup = {32'd5, 32'd10, 32'd3200};
                40'h0000000D40: frozen_conv_tile_lookup = {32'd6, 32'd2, 32'd768};
                40'h0000000D41: frozen_conv_tile_lookup = {32'd6, 32'd3, 32'd1152};
                40'h0000000D42: frozen_conv_tile_lookup = {32'd6, 32'd4, 32'd1536};
                40'h0000000D43: frozen_conv_tile_lookup = {32'd6, 32'd5, 32'd1920};
                40'h0000000D44: frozen_conv_tile_lookup = {32'd6, 32'd6, 32'd2304};
                40'h0000000D45: frozen_conv_tile_lookup = {32'd6, 32'd7, 32'd2688};
                40'h0000000D46: frozen_conv_tile_lookup = {32'd6, 32'd8, 32'd3072};
                40'h0000000D47: frozen_conv_tile_lookup = {32'd6, 32'd9, 32'd3456};
                40'h0000000D48: frozen_conv_tile_lookup = {32'd6, 32'd10, 32'd3840};
                40'h0000000D50: frozen_conv_tile_lookup = {32'd7, 32'd2, 32'd896};
                40'h0000000D51: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd1344};
                40'h0000000D52: frozen_conv_tile_lookup = {32'd7, 32'd4, 32'd1792};
                40'h0000000D53: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd2240};
                40'h0000000D54: frozen_conv_tile_lookup = {32'd7, 32'd6, 32'd2688};
                40'h0000000D55: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd3136};
                40'h0000000D56: frozen_conv_tile_lookup = {32'd7, 32'd8, 32'd3584};
                40'h0000000D57: frozen_conv_tile_lookup = {32'd7, 32'd9, 32'd4032};
                40'h0000000D58: frozen_conv_tile_lookup = {32'd7, 32'd10, 32'd4480};
                40'h0000000D60: frozen_conv_tile_lookup = {32'd8, 32'd2, 32'd1024};
                40'h0000000D61: frozen_conv_tile_lookup = {32'd8, 32'd3, 32'd1536};
                40'h0000000D62: frozen_conv_tile_lookup = {32'd8, 32'd4, 32'd2048};
                40'h0000000D63: frozen_conv_tile_lookup = {32'd8, 32'd5, 32'd2560};
                40'h0000000D64: frozen_conv_tile_lookup = {32'd8, 32'd6, 32'd3072};
                40'h0000000D65: frozen_conv_tile_lookup = {32'd8, 32'd7, 32'd3584};
                40'h0000000D66: frozen_conv_tile_lookup = {32'd8, 32'd8, 32'd4096};
                40'h0000000D67: frozen_conv_tile_lookup = {32'd8, 32'd9, 32'd4608};
                40'h0000000D68: frozen_conv_tile_lookup = {32'd8, 32'd10, 32'd5120};
                40'h0000000D70: frozen_conv_tile_lookup = {32'd9, 32'd2, 32'd1152};
                40'h0000000D71: frozen_conv_tile_lookup = {32'd9, 32'd3, 32'd1728};
                40'h0000000D72: frozen_conv_tile_lookup = {32'd9, 32'd4, 32'd2304};
                40'h0000000D73: frozen_conv_tile_lookup = {32'd9, 32'd5, 32'd2880};
                40'h0000000D74: frozen_conv_tile_lookup = {32'd9, 32'd6, 32'd3456};
                40'h0000000D75: frozen_conv_tile_lookup = {32'd9, 32'd7, 32'd4032};
                40'h0000000D76: frozen_conv_tile_lookup = {32'd9, 32'd8, 32'd4608};
                40'h0000000D77: frozen_conv_tile_lookup = {32'd9, 32'd9, 32'd5184};
                40'h0000000D78: frozen_conv_tile_lookup = {32'd9, 32'd10, 32'd5760};
                40'h0000000D80: frozen_conv_tile_lookup = {32'd10, 32'd2, 32'd1280};
                40'h0000000D81: frozen_conv_tile_lookup = {32'd10, 32'd3, 32'd1920};
                40'h0000000D82: frozen_conv_tile_lookup = {32'd10, 32'd4, 32'd2560};
                40'h0000000D83: frozen_conv_tile_lookup = {32'd10, 32'd5, 32'd3200};
                40'h0000000D84: frozen_conv_tile_lookup = {32'd10, 32'd6, 32'd3840};
                40'h0000000D85: frozen_conv_tile_lookup = {32'd10, 32'd7, 32'd4480};
                40'h0000000D86: frozen_conv_tile_lookup = {32'd10, 32'd8, 32'd5120};
                40'h0000000D87: frozen_conv_tile_lookup = {32'd10, 32'd9, 32'd5760};
                40'h0000000D88: frozen_conv_tile_lookup = {32'd10, 32'd10, 32'd6400};
                40'h0000000F00: frozen_conv_tile_lookup = {32'd0, 32'd0, 32'd0};
                40'h0000000F01: frozen_conv_tile_lookup = {32'd0, 32'd1, 32'd0};
                40'h0000000F02: frozen_conv_tile_lookup = {32'd0, 32'd2, 32'd0};
                40'h0000000F03: frozen_conv_tile_lookup = {32'd0, 32'd3, 32'd0};
                40'h0000000F04: frozen_conv_tile_lookup = {32'd0, 32'd4, 32'd0};
                40'h0000000F05: frozen_conv_tile_lookup = {32'd0, 32'd5, 32'd0};
                40'h0000000F06: frozen_conv_tile_lookup = {32'd0, 32'd6, 32'd0};
                40'h0000000F07: frozen_conv_tile_lookup = {32'd0, 32'd7, 32'd0};
                40'h0000000F08: frozen_conv_tile_lookup = {32'd0, 32'd8, 32'd0};
                40'h0000000F10: frozen_conv_tile_lookup = {32'd1, 32'd0, 32'd0};
                40'h0000000F11: frozen_conv_tile_lookup = {32'd1, 32'd1, 32'd128};
                40'h0000000F12: frozen_conv_tile_lookup = {32'd1, 32'd2, 32'd256};
                40'h0000000F13: frozen_conv_tile_lookup = {32'd1, 32'd3, 32'd384};
                40'h0000000F14: frozen_conv_tile_lookup = {32'd1, 32'd4, 32'd512};
                40'h0000000F15: frozen_conv_tile_lookup = {32'd1, 32'd5, 32'd640};
                40'h0000000F16: frozen_conv_tile_lookup = {32'd1, 32'd6, 32'd768};
                40'h0000000F17: frozen_conv_tile_lookup = {32'd1, 32'd7, 32'd896};
                40'h0000000F18: frozen_conv_tile_lookup = {32'd1, 32'd8, 32'd1024};
                40'h0000000F20: frozen_conv_tile_lookup = {32'd2, 32'd0, 32'd0};
                40'h0000000F21: frozen_conv_tile_lookup = {32'd2, 32'd1, 32'd256};
                40'h0000000F22: frozen_conv_tile_lookup = {32'd2, 32'd2, 32'd512};
                40'h0000000F23: frozen_conv_tile_lookup = {32'd2, 32'd3, 32'd768};
                40'h0000000F24: frozen_conv_tile_lookup = {32'd2, 32'd4, 32'd1024};
                40'h0000000F25: frozen_conv_tile_lookup = {32'd2, 32'd5, 32'd1280};
                40'h0000000F26: frozen_conv_tile_lookup = {32'd2, 32'd6, 32'd1536};
                40'h0000000F27: frozen_conv_tile_lookup = {32'd2, 32'd7, 32'd1792};
                40'h0000000F28: frozen_conv_tile_lookup = {32'd2, 32'd8, 32'd2048};
                40'h0000000F30: frozen_conv_tile_lookup = {32'd3, 32'd0, 32'd0};
                40'h0000000F31: frozen_conv_tile_lookup = {32'd3, 32'd1, 32'd384};
                40'h0000000F32: frozen_conv_tile_lookup = {32'd3, 32'd2, 32'd768};
                40'h0000000F33: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd1152};
                40'h0000000F34: frozen_conv_tile_lookup = {32'd3, 32'd4, 32'd1536};
                40'h0000000F35: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd1920};
                40'h0000000F36: frozen_conv_tile_lookup = {32'd3, 32'd6, 32'd2304};
                40'h0000000F37: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd2688};
                40'h0000000F38: frozen_conv_tile_lookup = {32'd3, 32'd8, 32'd3072};
                40'h0000000F40: frozen_conv_tile_lookup = {32'd4, 32'd0, 32'd0};
                40'h0000000F41: frozen_conv_tile_lookup = {32'd4, 32'd1, 32'd512};
                40'h0000000F42: frozen_conv_tile_lookup = {32'd4, 32'd2, 32'd1024};
                40'h0000000F43: frozen_conv_tile_lookup = {32'd4, 32'd3, 32'd1536};
                40'h0000000F44: frozen_conv_tile_lookup = {32'd4, 32'd4, 32'd2048};
                40'h0000000F45: frozen_conv_tile_lookup = {32'd4, 32'd5, 32'd2560};
                40'h0000000F46: frozen_conv_tile_lookup = {32'd4, 32'd6, 32'd3072};
                40'h0000000F47: frozen_conv_tile_lookup = {32'd4, 32'd7, 32'd3584};
                40'h0000000F48: frozen_conv_tile_lookup = {32'd4, 32'd8, 32'd4096};
                40'h0000000F50: frozen_conv_tile_lookup = {32'd5, 32'd0, 32'd0};
                40'h0000000F51: frozen_conv_tile_lookup = {32'd5, 32'd1, 32'd640};
                40'h0000000F52: frozen_conv_tile_lookup = {32'd5, 32'd2, 32'd1280};
                40'h0000000F53: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd1920};
                40'h0000000F54: frozen_conv_tile_lookup = {32'd5, 32'd4, 32'd2560};
                40'h0000000F55: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd3200};
                40'h0000000F56: frozen_conv_tile_lookup = {32'd5, 32'd6, 32'd3840};
                40'h0000000F57: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd4480};
                40'h0000000F58: frozen_conv_tile_lookup = {32'd5, 32'd8, 32'd5120};
                40'h0000000F60: frozen_conv_tile_lookup = {32'd6, 32'd0, 32'd0};
                40'h0000000F61: frozen_conv_tile_lookup = {32'd6, 32'd1, 32'd768};
                40'h0000000F62: frozen_conv_tile_lookup = {32'd6, 32'd2, 32'd1536};
                40'h0000000F63: frozen_conv_tile_lookup = {32'd6, 32'd3, 32'd2304};
                40'h0000000F64: frozen_conv_tile_lookup = {32'd6, 32'd4, 32'd3072};
                40'h0000000F65: frozen_conv_tile_lookup = {32'd6, 32'd5, 32'd3840};
                40'h0000000F66: frozen_conv_tile_lookup = {32'd6, 32'd6, 32'd4608};
                40'h0000000F67: frozen_conv_tile_lookup = {32'd6, 32'd7, 32'd5376};
                40'h0000000F68: frozen_conv_tile_lookup = {32'd6, 32'd8, 32'd6144};
                40'h0000000F70: frozen_conv_tile_lookup = {32'd7, 32'd0, 32'd0};
                40'h0000000F71: frozen_conv_tile_lookup = {32'd7, 32'd1, 32'd896};
                40'h0000000F72: frozen_conv_tile_lookup = {32'd7, 32'd2, 32'd1792};
                40'h0000000F73: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd2688};
                40'h0000000F74: frozen_conv_tile_lookup = {32'd7, 32'd4, 32'd3584};
                40'h0000000F75: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd4480};
                40'h0000000F76: frozen_conv_tile_lookup = {32'd7, 32'd6, 32'd5376};
                40'h0000000F77: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd6272};
                40'h0000000F78: frozen_conv_tile_lookup = {32'd7, 32'd8, 32'd7168};
                40'h0000000F80: frozen_conv_tile_lookup = {32'd8, 32'd0, 32'd0};
                40'h0000000F81: frozen_conv_tile_lookup = {32'd8, 32'd1, 32'd1024};
                40'h0000000F82: frozen_conv_tile_lookup = {32'd8, 32'd2, 32'd2048};
                40'h0000000F83: frozen_conv_tile_lookup = {32'd8, 32'd3, 32'd3072};
                40'h0000000F84: frozen_conv_tile_lookup = {32'd8, 32'd4, 32'd4096};
                40'h0000000F85: frozen_conv_tile_lookup = {32'd8, 32'd5, 32'd5120};
                40'h0000000F86: frozen_conv_tile_lookup = {32'd8, 32'd6, 32'd6144};
                40'h0000000F87: frozen_conv_tile_lookup = {32'd8, 32'd7, 32'd7168};
                40'h0000000F88: frozen_conv_tile_lookup = {32'd8, 32'd8, 32'd8192};
                40'h0000001200: frozen_conv_tile_lookup = {32'd2, 32'd2, 32'd1024};
                40'h0000001201: frozen_conv_tile_lookup = {32'd2, 32'd3, 32'd1536};
                40'h0000001202: frozen_conv_tile_lookup = {32'd2, 32'd4, 32'd2048};
                40'h0000001203: frozen_conv_tile_lookup = {32'd2, 32'd5, 32'd2560};
                40'h0000001204: frozen_conv_tile_lookup = {32'd2, 32'd6, 32'd3072};
                40'h0000001205: frozen_conv_tile_lookup = {32'd2, 32'd7, 32'd3584};
                40'h0000001206: frozen_conv_tile_lookup = {32'd2, 32'd8, 32'd4096};
                40'h0000001207: frozen_conv_tile_lookup = {32'd2, 32'd9, 32'd4608};
                40'h0000001208: frozen_conv_tile_lookup = {32'd2, 32'd10, 32'd5120};
                40'h0000001210: frozen_conv_tile_lookup = {32'd3, 32'd2, 32'd1536};
                40'h0000001211: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd2304};
                40'h0000001212: frozen_conv_tile_lookup = {32'd3, 32'd4, 32'd3072};
                40'h0000001213: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd3840};
                40'h0000001214: frozen_conv_tile_lookup = {32'd3, 32'd6, 32'd4608};
                40'h0000001215: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd5376};
                40'h0000001216: frozen_conv_tile_lookup = {32'd3, 32'd8, 32'd6144};
                40'h0000001217: frozen_conv_tile_lookup = {32'd3, 32'd9, 32'd6912};
                40'h0000001218: frozen_conv_tile_lookup = {32'd3, 32'd10, 32'd7680};
                40'h0000001220: frozen_conv_tile_lookup = {32'd4, 32'd2, 32'd2048};
                40'h0000001221: frozen_conv_tile_lookup = {32'd4, 32'd3, 32'd3072};
                40'h0000001222: frozen_conv_tile_lookup = {32'd4, 32'd4, 32'd4096};
                40'h0000001223: frozen_conv_tile_lookup = {32'd4, 32'd5, 32'd5120};
                40'h0000001224: frozen_conv_tile_lookup = {32'd4, 32'd6, 32'd6144};
                40'h0000001225: frozen_conv_tile_lookup = {32'd4, 32'd7, 32'd7168};
                40'h0000001226: frozen_conv_tile_lookup = {32'd4, 32'd8, 32'd8192};
                40'h0000001227: frozen_conv_tile_lookup = {32'd4, 32'd9, 32'd9216};
                40'h0000001228: frozen_conv_tile_lookup = {32'd4, 32'd10, 32'd10240};
                40'h0000001230: frozen_conv_tile_lookup = {32'd5, 32'd2, 32'd2560};
                40'h0000001231: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd3840};
                40'h0000001232: frozen_conv_tile_lookup = {32'd5, 32'd4, 32'd5120};
                40'h0000001233: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd6400};
                40'h0000001234: frozen_conv_tile_lookup = {32'd5, 32'd6, 32'd7680};
                40'h0000001235: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd8960};
                40'h0000001236: frozen_conv_tile_lookup = {32'd5, 32'd8, 32'd10240};
                40'h0000001237: frozen_conv_tile_lookup = {32'd5, 32'd9, 32'd11520};
                40'h0000001238: frozen_conv_tile_lookup = {32'd5, 32'd10, 32'd12800};
                40'h0000001240: frozen_conv_tile_lookup = {32'd6, 32'd2, 32'd3072};
                40'h0000001241: frozen_conv_tile_lookup = {32'd6, 32'd3, 32'd4608};
                40'h0000001242: frozen_conv_tile_lookup = {32'd6, 32'd4, 32'd6144};
                40'h0000001243: frozen_conv_tile_lookup = {32'd6, 32'd5, 32'd7680};
                40'h0000001244: frozen_conv_tile_lookup = {32'd6, 32'd6, 32'd9216};
                40'h0000001245: frozen_conv_tile_lookup = {32'd6, 32'd7, 32'd10752};
                40'h0000001246: frozen_conv_tile_lookup = {32'd6, 32'd8, 32'd12288};
                40'h0000001247: frozen_conv_tile_lookup = {32'd6, 32'd9, 32'd13824};
                40'h0000001248: frozen_conv_tile_lookup = {32'd6, 32'd10, 32'd15360};
                40'h0000001250: frozen_conv_tile_lookup = {32'd7, 32'd2, 32'd3584};
                40'h0000001251: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd5376};
                40'h0000001252: frozen_conv_tile_lookup = {32'd7, 32'd4, 32'd7168};
                40'h0000001253: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd8960};
                40'h0000001254: frozen_conv_tile_lookup = {32'd7, 32'd6, 32'd10752};
                40'h0000001255: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd12544};
                40'h0000001256: frozen_conv_tile_lookup = {32'd7, 32'd8, 32'd14336};
                40'h0000001257: frozen_conv_tile_lookup = {32'd7, 32'd9, 32'd16128};
                40'h0000001258: frozen_conv_tile_lookup = {32'd7, 32'd10, 32'd17920};
                40'h0000001260: frozen_conv_tile_lookup = {32'd8, 32'd2, 32'd4096};
                40'h0000001261: frozen_conv_tile_lookup = {32'd8, 32'd3, 32'd6144};
                40'h0000001262: frozen_conv_tile_lookup = {32'd8, 32'd4, 32'd8192};
                40'h0000001263: frozen_conv_tile_lookup = {32'd8, 32'd5, 32'd10240};
                40'h0000001264: frozen_conv_tile_lookup = {32'd8, 32'd6, 32'd12288};
                40'h0000001265: frozen_conv_tile_lookup = {32'd8, 32'd7, 32'd14336};
                40'h0000001266: frozen_conv_tile_lookup = {32'd8, 32'd8, 32'd16384};
                40'h0000001267: frozen_conv_tile_lookup = {32'd8, 32'd9, 32'd18432};
                40'h0000001268: frozen_conv_tile_lookup = {32'd8, 32'd10, 32'd20480};
                40'h0000001270: frozen_conv_tile_lookup = {32'd9, 32'd2, 32'd4608};
                40'h0000001271: frozen_conv_tile_lookup = {32'd9, 32'd3, 32'd6912};
                40'h0000001272: frozen_conv_tile_lookup = {32'd9, 32'd4, 32'd9216};
                40'h0000001273: frozen_conv_tile_lookup = {32'd9, 32'd5, 32'd11520};
                40'h0000001274: frozen_conv_tile_lookup = {32'd9, 32'd6, 32'd13824};
                40'h0000001275: frozen_conv_tile_lookup = {32'd9, 32'd7, 32'd16128};
                40'h0000001276: frozen_conv_tile_lookup = {32'd9, 32'd8, 32'd18432};
                40'h0000001277: frozen_conv_tile_lookup = {32'd9, 32'd9, 32'd20736};
                40'h0000001278: frozen_conv_tile_lookup = {32'd9, 32'd10, 32'd23040};
                40'h0000001280: frozen_conv_tile_lookup = {32'd10, 32'd2, 32'd5120};
                40'h0000001281: frozen_conv_tile_lookup = {32'd10, 32'd3, 32'd7680};
                40'h0000001282: frozen_conv_tile_lookup = {32'd10, 32'd4, 32'd10240};
                40'h0000001283: frozen_conv_tile_lookup = {32'd10, 32'd5, 32'd12800};
                40'h0000001284: frozen_conv_tile_lookup = {32'd10, 32'd6, 32'd15360};
                40'h0000001285: frozen_conv_tile_lookup = {32'd10, 32'd7, 32'd17920};
                40'h0000001286: frozen_conv_tile_lookup = {32'd10, 32'd8, 32'd20480};
                40'h0000001287: frozen_conv_tile_lookup = {32'd10, 32'd9, 32'd23040};
                40'h0000001288: frozen_conv_tile_lookup = {32'd10, 32'd10, 32'd25600};
                40'h0000001400: frozen_conv_tile_lookup = {32'd2, 32'd2, 32'd512};
                40'h0000001401: frozen_conv_tile_lookup = {32'd2, 32'd3, 32'd768};
                40'h0000001402: frozen_conv_tile_lookup = {32'd2, 32'd4, 32'd1024};
                40'h0000001403: frozen_conv_tile_lookup = {32'd2, 32'd5, 32'd1280};
                40'h0000001404: frozen_conv_tile_lookup = {32'd2, 32'd6, 32'd1536};
                40'h0000001405: frozen_conv_tile_lookup = {32'd2, 32'd7, 32'd1792};
                40'h0000001406: frozen_conv_tile_lookup = {32'd2, 32'd8, 32'd2048};
                40'h0000001407: frozen_conv_tile_lookup = {32'd2, 32'd9, 32'd2304};
                40'h0000001408: frozen_conv_tile_lookup = {32'd2, 32'd10, 32'd2560};
                40'h0000001410: frozen_conv_tile_lookup = {32'd3, 32'd2, 32'd768};
                40'h0000001411: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd1152};
                40'h0000001412: frozen_conv_tile_lookup = {32'd3, 32'd4, 32'd1536};
                40'h0000001413: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd1920};
                40'h0000001414: frozen_conv_tile_lookup = {32'd3, 32'd6, 32'd2304};
                40'h0000001415: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd2688};
                40'h0000001416: frozen_conv_tile_lookup = {32'd3, 32'd8, 32'd3072};
                40'h0000001417: frozen_conv_tile_lookup = {32'd3, 32'd9, 32'd3456};
                40'h0000001418: frozen_conv_tile_lookup = {32'd3, 32'd10, 32'd3840};
                40'h0000001420: frozen_conv_tile_lookup = {32'd4, 32'd2, 32'd1024};
                40'h0000001421: frozen_conv_tile_lookup = {32'd4, 32'd3, 32'd1536};
                40'h0000001422: frozen_conv_tile_lookup = {32'd4, 32'd4, 32'd2048};
                40'h0000001423: frozen_conv_tile_lookup = {32'd4, 32'd5, 32'd2560};
                40'h0000001424: frozen_conv_tile_lookup = {32'd4, 32'd6, 32'd3072};
                40'h0000001425: frozen_conv_tile_lookup = {32'd4, 32'd7, 32'd3584};
                40'h0000001426: frozen_conv_tile_lookup = {32'd4, 32'd8, 32'd4096};
                40'h0000001427: frozen_conv_tile_lookup = {32'd4, 32'd9, 32'd4608};
                40'h0000001428: frozen_conv_tile_lookup = {32'd4, 32'd10, 32'd5120};
                40'h0000001430: frozen_conv_tile_lookup = {32'd5, 32'd2, 32'd1280};
                40'h0000001431: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd1920};
                40'h0000001432: frozen_conv_tile_lookup = {32'd5, 32'd4, 32'd2560};
                40'h0000001433: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd3200};
                40'h0000001434: frozen_conv_tile_lookup = {32'd5, 32'd6, 32'd3840};
                40'h0000001435: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd4480};
                40'h0000001436: frozen_conv_tile_lookup = {32'd5, 32'd8, 32'd5120};
                40'h0000001437: frozen_conv_tile_lookup = {32'd5, 32'd9, 32'd5760};
                40'h0000001438: frozen_conv_tile_lookup = {32'd5, 32'd10, 32'd6400};
                40'h0000001440: frozen_conv_tile_lookup = {32'd6, 32'd2, 32'd1536};
                40'h0000001441: frozen_conv_tile_lookup = {32'd6, 32'd3, 32'd2304};
                40'h0000001442: frozen_conv_tile_lookup = {32'd6, 32'd4, 32'd3072};
                40'h0000001443: frozen_conv_tile_lookup = {32'd6, 32'd5, 32'd3840};
                40'h0000001444: frozen_conv_tile_lookup = {32'd6, 32'd6, 32'd4608};
                40'h0000001445: frozen_conv_tile_lookup = {32'd6, 32'd7, 32'd5376};
                40'h0000001446: frozen_conv_tile_lookup = {32'd6, 32'd8, 32'd6144};
                40'h0000001447: frozen_conv_tile_lookup = {32'd6, 32'd9, 32'd6912};
                40'h0000001448: frozen_conv_tile_lookup = {32'd6, 32'd10, 32'd7680};
                40'h0000001450: frozen_conv_tile_lookup = {32'd7, 32'd2, 32'd1792};
                40'h0000001451: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd2688};
                40'h0000001452: frozen_conv_tile_lookup = {32'd7, 32'd4, 32'd3584};
                40'h0000001453: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd4480};
                40'h0000001454: frozen_conv_tile_lookup = {32'd7, 32'd6, 32'd5376};
                40'h0000001455: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd6272};
                40'h0000001456: frozen_conv_tile_lookup = {32'd7, 32'd8, 32'd7168};
                40'h0000001457: frozen_conv_tile_lookup = {32'd7, 32'd9, 32'd8064};
                40'h0000001458: frozen_conv_tile_lookup = {32'd7, 32'd10, 32'd8960};
                40'h0000001460: frozen_conv_tile_lookup = {32'd8, 32'd2, 32'd2048};
                40'h0000001461: frozen_conv_tile_lookup = {32'd8, 32'd3, 32'd3072};
                40'h0000001462: frozen_conv_tile_lookup = {32'd8, 32'd4, 32'd4096};
                40'h0000001463: frozen_conv_tile_lookup = {32'd8, 32'd5, 32'd5120};
                40'h0000001464: frozen_conv_tile_lookup = {32'd8, 32'd6, 32'd6144};
                40'h0000001465: frozen_conv_tile_lookup = {32'd8, 32'd7, 32'd7168};
                40'h0000001466: frozen_conv_tile_lookup = {32'd8, 32'd8, 32'd8192};
                40'h0000001467: frozen_conv_tile_lookup = {32'd8, 32'd9, 32'd9216};
                40'h0000001468: frozen_conv_tile_lookup = {32'd8, 32'd10, 32'd10240};
                40'h0000001470: frozen_conv_tile_lookup = {32'd9, 32'd2, 32'd2304};
                40'h0000001471: frozen_conv_tile_lookup = {32'd9, 32'd3, 32'd3456};
                40'h0000001472: frozen_conv_tile_lookup = {32'd9, 32'd4, 32'd4608};
                40'h0000001473: frozen_conv_tile_lookup = {32'd9, 32'd5, 32'd5760};
                40'h0000001474: frozen_conv_tile_lookup = {32'd9, 32'd6, 32'd6912};
                40'h0000001475: frozen_conv_tile_lookup = {32'd9, 32'd7, 32'd8064};
                40'h0000001476: frozen_conv_tile_lookup = {32'd9, 32'd8, 32'd9216};
                40'h0000001477: frozen_conv_tile_lookup = {32'd9, 32'd9, 32'd10368};
                40'h0000001478: frozen_conv_tile_lookup = {32'd9, 32'd10, 32'd11520};
                40'h0000001480: frozen_conv_tile_lookup = {32'd10, 32'd2, 32'd2560};
                40'h0000001481: frozen_conv_tile_lookup = {32'd10, 32'd3, 32'd3840};
                40'h0000001482: frozen_conv_tile_lookup = {32'd10, 32'd4, 32'd5120};
                40'h0000001483: frozen_conv_tile_lookup = {32'd10, 32'd5, 32'd6400};
                40'h0000001484: frozen_conv_tile_lookup = {32'd10, 32'd6, 32'd7680};
                40'h0000001485: frozen_conv_tile_lookup = {32'd10, 32'd7, 32'd8960};
                40'h0000001486: frozen_conv_tile_lookup = {32'd10, 32'd8, 32'd10240};
                40'h0000001487: frozen_conv_tile_lookup = {32'd10, 32'd9, 32'd11520};
                40'h0000001488: frozen_conv_tile_lookup = {32'd10, 32'd10, 32'd12800};
                40'h0000001500: frozen_conv_tile_lookup = {32'd2, 32'd2, 32'd512};
                40'h0000001501: frozen_conv_tile_lookup = {32'd2, 32'd3, 32'd768};
                40'h0000001502: frozen_conv_tile_lookup = {32'd2, 32'd4, 32'd1024};
                40'h0000001503: frozen_conv_tile_lookup = {32'd2, 32'd5, 32'd1280};
                40'h0000001504: frozen_conv_tile_lookup = {32'd2, 32'd6, 32'd1536};
                40'h0000001505: frozen_conv_tile_lookup = {32'd2, 32'd7, 32'd1792};
                40'h0000001506: frozen_conv_tile_lookup = {32'd2, 32'd8, 32'd2048};
                40'h0000001507: frozen_conv_tile_lookup = {32'd2, 32'd9, 32'd2304};
                40'h0000001508: frozen_conv_tile_lookup = {32'd2, 32'd10, 32'd2560};
                40'h0000001510: frozen_conv_tile_lookup = {32'd3, 32'd2, 32'd768};
                40'h0000001511: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd1152};
                40'h0000001512: frozen_conv_tile_lookup = {32'd3, 32'd4, 32'd1536};
                40'h0000001513: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd1920};
                40'h0000001514: frozen_conv_tile_lookup = {32'd3, 32'd6, 32'd2304};
                40'h0000001515: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd2688};
                40'h0000001516: frozen_conv_tile_lookup = {32'd3, 32'd8, 32'd3072};
                40'h0000001517: frozen_conv_tile_lookup = {32'd3, 32'd9, 32'd3456};
                40'h0000001518: frozen_conv_tile_lookup = {32'd3, 32'd10, 32'd3840};
                40'h0000001520: frozen_conv_tile_lookup = {32'd4, 32'd2, 32'd1024};
                40'h0000001521: frozen_conv_tile_lookup = {32'd4, 32'd3, 32'd1536};
                40'h0000001522: frozen_conv_tile_lookup = {32'd4, 32'd4, 32'd2048};
                40'h0000001523: frozen_conv_tile_lookup = {32'd4, 32'd5, 32'd2560};
                40'h0000001524: frozen_conv_tile_lookup = {32'd4, 32'd6, 32'd3072};
                40'h0000001525: frozen_conv_tile_lookup = {32'd4, 32'd7, 32'd3584};
                40'h0000001526: frozen_conv_tile_lookup = {32'd4, 32'd8, 32'd4096};
                40'h0000001527: frozen_conv_tile_lookup = {32'd4, 32'd9, 32'd4608};
                40'h0000001528: frozen_conv_tile_lookup = {32'd4, 32'd10, 32'd5120};
                40'h0000001530: frozen_conv_tile_lookup = {32'd5, 32'd2, 32'd1280};
                40'h0000001531: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd1920};
                40'h0000001532: frozen_conv_tile_lookup = {32'd5, 32'd4, 32'd2560};
                40'h0000001533: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd3200};
                40'h0000001534: frozen_conv_tile_lookup = {32'd5, 32'd6, 32'd3840};
                40'h0000001535: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd4480};
                40'h0000001536: frozen_conv_tile_lookup = {32'd5, 32'd8, 32'd5120};
                40'h0000001537: frozen_conv_tile_lookup = {32'd5, 32'd9, 32'd5760};
                40'h0000001538: frozen_conv_tile_lookup = {32'd5, 32'd10, 32'd6400};
                40'h0000001540: frozen_conv_tile_lookup = {32'd6, 32'd2, 32'd1536};
                40'h0000001541: frozen_conv_tile_lookup = {32'd6, 32'd3, 32'd2304};
                40'h0000001542: frozen_conv_tile_lookup = {32'd6, 32'd4, 32'd3072};
                40'h0000001543: frozen_conv_tile_lookup = {32'd6, 32'd5, 32'd3840};
                40'h0000001544: frozen_conv_tile_lookup = {32'd6, 32'd6, 32'd4608};
                40'h0000001545: frozen_conv_tile_lookup = {32'd6, 32'd7, 32'd5376};
                40'h0000001546: frozen_conv_tile_lookup = {32'd6, 32'd8, 32'd6144};
                40'h0000001547: frozen_conv_tile_lookup = {32'd6, 32'd9, 32'd6912};
                40'h0000001548: frozen_conv_tile_lookup = {32'd6, 32'd10, 32'd7680};
                40'h0000001550: frozen_conv_tile_lookup = {32'd7, 32'd2, 32'd1792};
                40'h0000001551: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd2688};
                40'h0000001552: frozen_conv_tile_lookup = {32'd7, 32'd4, 32'd3584};
                40'h0000001553: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd4480};
                40'h0000001554: frozen_conv_tile_lookup = {32'd7, 32'd6, 32'd5376};
                40'h0000001555: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd6272};
                40'h0000001556: frozen_conv_tile_lookup = {32'd7, 32'd8, 32'd7168};
                40'h0000001557: frozen_conv_tile_lookup = {32'd7, 32'd9, 32'd8064};
                40'h0000001558: frozen_conv_tile_lookup = {32'd7, 32'd10, 32'd8960};
                40'h0000001560: frozen_conv_tile_lookup = {32'd8, 32'd2, 32'd2048};
                40'h0000001561: frozen_conv_tile_lookup = {32'd8, 32'd3, 32'd3072};
                40'h0000001562: frozen_conv_tile_lookup = {32'd8, 32'd4, 32'd4096};
                40'h0000001563: frozen_conv_tile_lookup = {32'd8, 32'd5, 32'd5120};
                40'h0000001564: frozen_conv_tile_lookup = {32'd8, 32'd6, 32'd6144};
                40'h0000001565: frozen_conv_tile_lookup = {32'd8, 32'd7, 32'd7168};
                40'h0000001566: frozen_conv_tile_lookup = {32'd8, 32'd8, 32'd8192};
                40'h0000001567: frozen_conv_tile_lookup = {32'd8, 32'd9, 32'd9216};
                40'h0000001568: frozen_conv_tile_lookup = {32'd8, 32'd10, 32'd10240};
                40'h0000001570: frozen_conv_tile_lookup = {32'd9, 32'd2, 32'd2304};
                40'h0000001571: frozen_conv_tile_lookup = {32'd9, 32'd3, 32'd3456};
                40'h0000001572: frozen_conv_tile_lookup = {32'd9, 32'd4, 32'd4608};
                40'h0000001573: frozen_conv_tile_lookup = {32'd9, 32'd5, 32'd5760};
                40'h0000001574: frozen_conv_tile_lookup = {32'd9, 32'd6, 32'd6912};
                40'h0000001575: frozen_conv_tile_lookup = {32'd9, 32'd7, 32'd8064};
                40'h0000001576: frozen_conv_tile_lookup = {32'd9, 32'd8, 32'd9216};
                40'h0000001577: frozen_conv_tile_lookup = {32'd9, 32'd9, 32'd10368};
                40'h0000001578: frozen_conv_tile_lookup = {32'd9, 32'd10, 32'd11520};
                40'h0000001580: frozen_conv_tile_lookup = {32'd10, 32'd2, 32'd2560};
                40'h0000001581: frozen_conv_tile_lookup = {32'd10, 32'd3, 32'd3840};
                40'h0000001582: frozen_conv_tile_lookup = {32'd10, 32'd4, 32'd5120};
                40'h0000001583: frozen_conv_tile_lookup = {32'd10, 32'd5, 32'd6400};
                40'h0000001584: frozen_conv_tile_lookup = {32'd10, 32'd6, 32'd7680};
                40'h0000001585: frozen_conv_tile_lookup = {32'd10, 32'd7, 32'd8960};
                40'h0000001586: frozen_conv_tile_lookup = {32'd10, 32'd8, 32'd10240};
                40'h0000001587: frozen_conv_tile_lookup = {32'd10, 32'd9, 32'd11520};
                40'h0000001588: frozen_conv_tile_lookup = {32'd10, 32'd10, 32'd12800};
                40'h0000001700: frozen_conv_tile_lookup = {32'd0, 32'd0, 32'd0};
                40'h0000001701: frozen_conv_tile_lookup = {32'd0, 32'd1, 32'd0};
                40'h0000001702: frozen_conv_tile_lookup = {32'd0, 32'd2, 32'd0};
                40'h0000001703: frozen_conv_tile_lookup = {32'd0, 32'd3, 32'd0};
                40'h0000001704: frozen_conv_tile_lookup = {32'd0, 32'd4, 32'd0};
                40'h0000001705: frozen_conv_tile_lookup = {32'd0, 32'd5, 32'd0};
                40'h0000001706: frozen_conv_tile_lookup = {32'd0, 32'd6, 32'd0};
                40'h0000001707: frozen_conv_tile_lookup = {32'd0, 32'd7, 32'd0};
                40'h0000001708: frozen_conv_tile_lookup = {32'd0, 32'd8, 32'd0};
                40'h0000001710: frozen_conv_tile_lookup = {32'd1, 32'd0, 32'd0};
                40'h0000001711: frozen_conv_tile_lookup = {32'd1, 32'd1, 32'd256};
                40'h0000001712: frozen_conv_tile_lookup = {32'd1, 32'd2, 32'd512};
                40'h0000001713: frozen_conv_tile_lookup = {32'd1, 32'd3, 32'd768};
                40'h0000001714: frozen_conv_tile_lookup = {32'd1, 32'd4, 32'd1024};
                40'h0000001715: frozen_conv_tile_lookup = {32'd1, 32'd5, 32'd1280};
                40'h0000001716: frozen_conv_tile_lookup = {32'd1, 32'd6, 32'd1536};
                40'h0000001717: frozen_conv_tile_lookup = {32'd1, 32'd7, 32'd1792};
                40'h0000001718: frozen_conv_tile_lookup = {32'd1, 32'd8, 32'd2048};
                40'h0000001720: frozen_conv_tile_lookup = {32'd2, 32'd0, 32'd0};
                40'h0000001721: frozen_conv_tile_lookup = {32'd2, 32'd1, 32'd512};
                40'h0000001722: frozen_conv_tile_lookup = {32'd2, 32'd2, 32'd1024};
                40'h0000001723: frozen_conv_tile_lookup = {32'd2, 32'd3, 32'd1536};
                40'h0000001724: frozen_conv_tile_lookup = {32'd2, 32'd4, 32'd2048};
                40'h0000001725: frozen_conv_tile_lookup = {32'd2, 32'd5, 32'd2560};
                40'h0000001726: frozen_conv_tile_lookup = {32'd2, 32'd6, 32'd3072};
                40'h0000001727: frozen_conv_tile_lookup = {32'd2, 32'd7, 32'd3584};
                40'h0000001728: frozen_conv_tile_lookup = {32'd2, 32'd8, 32'd4096};
                40'h0000001730: frozen_conv_tile_lookup = {32'd3, 32'd0, 32'd0};
                40'h0000001731: frozen_conv_tile_lookup = {32'd3, 32'd1, 32'd768};
                40'h0000001732: frozen_conv_tile_lookup = {32'd3, 32'd2, 32'd1536};
                40'h0000001733: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd2304};
                40'h0000001734: frozen_conv_tile_lookup = {32'd3, 32'd4, 32'd3072};
                40'h0000001735: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd3840};
                40'h0000001736: frozen_conv_tile_lookup = {32'd3, 32'd6, 32'd4608};
                40'h0000001737: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd5376};
                40'h0000001738: frozen_conv_tile_lookup = {32'd3, 32'd8, 32'd6144};
                40'h0000001740: frozen_conv_tile_lookup = {32'd4, 32'd0, 32'd0};
                40'h0000001741: frozen_conv_tile_lookup = {32'd4, 32'd1, 32'd1024};
                40'h0000001742: frozen_conv_tile_lookup = {32'd4, 32'd2, 32'd2048};
                40'h0000001743: frozen_conv_tile_lookup = {32'd4, 32'd3, 32'd3072};
                40'h0000001744: frozen_conv_tile_lookup = {32'd4, 32'd4, 32'd4096};
                40'h0000001745: frozen_conv_tile_lookup = {32'd4, 32'd5, 32'd5120};
                40'h0000001746: frozen_conv_tile_lookup = {32'd4, 32'd6, 32'd6144};
                40'h0000001747: frozen_conv_tile_lookup = {32'd4, 32'd7, 32'd7168};
                40'h0000001748: frozen_conv_tile_lookup = {32'd4, 32'd8, 32'd8192};
                40'h0000001750: frozen_conv_tile_lookup = {32'd5, 32'd0, 32'd0};
                40'h0000001751: frozen_conv_tile_lookup = {32'd5, 32'd1, 32'd1280};
                40'h0000001752: frozen_conv_tile_lookup = {32'd5, 32'd2, 32'd2560};
                40'h0000001753: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd3840};
                40'h0000001754: frozen_conv_tile_lookup = {32'd5, 32'd4, 32'd5120};
                40'h0000001755: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd6400};
                40'h0000001756: frozen_conv_tile_lookup = {32'd5, 32'd6, 32'd7680};
                40'h0000001757: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd8960};
                40'h0000001758: frozen_conv_tile_lookup = {32'd5, 32'd8, 32'd10240};
                40'h0000001760: frozen_conv_tile_lookup = {32'd6, 32'd0, 32'd0};
                40'h0000001761: frozen_conv_tile_lookup = {32'd6, 32'd1, 32'd1536};
                40'h0000001762: frozen_conv_tile_lookup = {32'd6, 32'd2, 32'd3072};
                40'h0000001763: frozen_conv_tile_lookup = {32'd6, 32'd3, 32'd4608};
                40'h0000001764: frozen_conv_tile_lookup = {32'd6, 32'd4, 32'd6144};
                40'h0000001765: frozen_conv_tile_lookup = {32'd6, 32'd5, 32'd7680};
                40'h0000001766: frozen_conv_tile_lookup = {32'd6, 32'd6, 32'd9216};
                40'h0000001767: frozen_conv_tile_lookup = {32'd6, 32'd7, 32'd10752};
                40'h0000001768: frozen_conv_tile_lookup = {32'd6, 32'd8, 32'd12288};
                40'h0000001770: frozen_conv_tile_lookup = {32'd7, 32'd0, 32'd0};
                40'h0000001771: frozen_conv_tile_lookup = {32'd7, 32'd1, 32'd1792};
                40'h0000001772: frozen_conv_tile_lookup = {32'd7, 32'd2, 32'd3584};
                40'h0000001773: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd5376};
                40'h0000001774: frozen_conv_tile_lookup = {32'd7, 32'd4, 32'd7168};
                40'h0000001775: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd8960};
                40'h0000001776: frozen_conv_tile_lookup = {32'd7, 32'd6, 32'd10752};
                40'h0000001777: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd12544};
                40'h0000001778: frozen_conv_tile_lookup = {32'd7, 32'd8, 32'd14336};
                40'h0000001780: frozen_conv_tile_lookup = {32'd8, 32'd0, 32'd0};
                40'h0000001781: frozen_conv_tile_lookup = {32'd8, 32'd1, 32'd2048};
                40'h0000001782: frozen_conv_tile_lookup = {32'd8, 32'd2, 32'd4096};
                40'h0000001783: frozen_conv_tile_lookup = {32'd8, 32'd3, 32'd6144};
                40'h0000001784: frozen_conv_tile_lookup = {32'd8, 32'd4, 32'd8192};
                40'h0000001785: frozen_conv_tile_lookup = {32'd8, 32'd5, 32'd10240};
                40'h0000001786: frozen_conv_tile_lookup = {32'd8, 32'd6, 32'd12288};
                40'h0000001787: frozen_conv_tile_lookup = {32'd8, 32'd7, 32'd14336};
                40'h0000001788: frozen_conv_tile_lookup = {32'd8, 32'd8, 32'd16384};
                40'h0000001A00: frozen_conv_tile_lookup = {32'd2, 32'd2, 32'd2048};
                40'h0000001A01: frozen_conv_tile_lookup = {32'd2, 32'd3, 32'd3072};
                40'h0000001A02: frozen_conv_tile_lookup = {32'd2, 32'd4, 32'd4096};
                40'h0000001A03: frozen_conv_tile_lookup = {32'd2, 32'd5, 32'd5120};
                40'h0000001A04: frozen_conv_tile_lookup = {32'd2, 32'd6, 32'd6144};
                40'h0000001A05: frozen_conv_tile_lookup = {32'd2, 32'd7, 32'd7168};
                40'h0000001A06: frozen_conv_tile_lookup = {32'd2, 32'd8, 32'd8192};
                40'h0000001A07: frozen_conv_tile_lookup = {32'd2, 32'd9, 32'd9216};
                40'h0000001A08: frozen_conv_tile_lookup = {32'd2, 32'd10, 32'd10240};
                40'h0000001A10: frozen_conv_tile_lookup = {32'd3, 32'd2, 32'd3072};
                40'h0000001A11: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd4608};
                40'h0000001A12: frozen_conv_tile_lookup = {32'd3, 32'd4, 32'd6144};
                40'h0000001A13: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd7680};
                40'h0000001A14: frozen_conv_tile_lookup = {32'd3, 32'd6, 32'd9216};
                40'h0000001A15: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd10752};
                40'h0000001A16: frozen_conv_tile_lookup = {32'd3, 32'd8, 32'd12288};
                40'h0000001A17: frozen_conv_tile_lookup = {32'd3, 32'd9, 32'd13824};
                40'h0000001A18: frozen_conv_tile_lookup = {32'd3, 32'd10, 32'd15360};
                40'h0000001A20: frozen_conv_tile_lookup = {32'd4, 32'd2, 32'd4096};
                40'h0000001A21: frozen_conv_tile_lookup = {32'd4, 32'd3, 32'd6144};
                40'h0000001A22: frozen_conv_tile_lookup = {32'd4, 32'd4, 32'd8192};
                40'h0000001A23: frozen_conv_tile_lookup = {32'd4, 32'd5, 32'd10240};
                40'h0000001A24: frozen_conv_tile_lookup = {32'd4, 32'd6, 32'd12288};
                40'h0000001A25: frozen_conv_tile_lookup = {32'd4, 32'd7, 32'd14336};
                40'h0000001A26: frozen_conv_tile_lookup = {32'd4, 32'd8, 32'd16384};
                40'h0000001A27: frozen_conv_tile_lookup = {32'd4, 32'd9, 32'd18432};
                40'h0000001A28: frozen_conv_tile_lookup = {32'd4, 32'd10, 32'd20480};
                40'h0000001A30: frozen_conv_tile_lookup = {32'd5, 32'd2, 32'd5120};
                40'h0000001A31: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd7680};
                40'h0000001A32: frozen_conv_tile_lookup = {32'd5, 32'd4, 32'd10240};
                40'h0000001A33: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd12800};
                40'h0000001A34: frozen_conv_tile_lookup = {32'd5, 32'd6, 32'd15360};
                40'h0000001A35: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd17920};
                40'h0000001A36: frozen_conv_tile_lookup = {32'd5, 32'd8, 32'd20480};
                40'h0000001A37: frozen_conv_tile_lookup = {32'd5, 32'd9, 32'd23040};
                40'h0000001A38: frozen_conv_tile_lookup = {32'd5, 32'd10, 32'd25600};
                40'h0000001A40: frozen_conv_tile_lookup = {32'd6, 32'd2, 32'd6144};
                40'h0000001A41: frozen_conv_tile_lookup = {32'd6, 32'd3, 32'd9216};
                40'h0000001A42: frozen_conv_tile_lookup = {32'd6, 32'd4, 32'd12288};
                40'h0000001A43: frozen_conv_tile_lookup = {32'd6, 32'd5, 32'd15360};
                40'h0000001A44: frozen_conv_tile_lookup = {32'd6, 32'd6, 32'd18432};
                40'h0000001A45: frozen_conv_tile_lookup = {32'd6, 32'd7, 32'd21504};
                40'h0000001A46: frozen_conv_tile_lookup = {32'd6, 32'd8, 32'd24576};
                40'h0000001A47: frozen_conv_tile_lookup = {32'd6, 32'd9, 32'd27648};
                40'h0000001A48: frozen_conv_tile_lookup = {32'd6, 32'd10, 32'd30720};
                40'h0000001A50: frozen_conv_tile_lookup = {32'd7, 32'd2, 32'd7168};
                40'h0000001A51: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd10752};
                40'h0000001A52: frozen_conv_tile_lookup = {32'd7, 32'd4, 32'd14336};
                40'h0000001A53: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd17920};
                40'h0000001A54: frozen_conv_tile_lookup = {32'd7, 32'd6, 32'd21504};
                40'h0000001A55: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd25088};
                40'h0000001A56: frozen_conv_tile_lookup = {32'd7, 32'd8, 32'd28672};
                40'h0000001A57: frozen_conv_tile_lookup = {32'd7, 32'd9, 32'd32256};
                40'h0000001A58: frozen_conv_tile_lookup = {32'd7, 32'd10, 32'd35840};
                40'h0000001A60: frozen_conv_tile_lookup = {32'd8, 32'd2, 32'd8192};
                40'h0000001A61: frozen_conv_tile_lookup = {32'd8, 32'd3, 32'd12288};
                40'h0000001A62: frozen_conv_tile_lookup = {32'd8, 32'd4, 32'd16384};
                40'h0000001A63: frozen_conv_tile_lookup = {32'd8, 32'd5, 32'd20480};
                40'h0000001A64: frozen_conv_tile_lookup = {32'd8, 32'd6, 32'd24576};
                40'h0000001A65: frozen_conv_tile_lookup = {32'd8, 32'd7, 32'd28672};
                40'h0000001A66: frozen_conv_tile_lookup = {32'd8, 32'd8, 32'd32768};
                40'h0000001A67: frozen_conv_tile_lookup = {32'd8, 32'd9, 32'd36864};
                40'h0000001A68: frozen_conv_tile_lookup = {32'd8, 32'd10, 32'd40960};
                40'h0000001A70: frozen_conv_tile_lookup = {32'd9, 32'd2, 32'd9216};
                40'h0000001A71: frozen_conv_tile_lookup = {32'd9, 32'd3, 32'd13824};
                40'h0000001A72: frozen_conv_tile_lookup = {32'd9, 32'd4, 32'd18432};
                40'h0000001A73: frozen_conv_tile_lookup = {32'd9, 32'd5, 32'd23040};
                40'h0000001A74: frozen_conv_tile_lookup = {32'd9, 32'd6, 32'd27648};
                40'h0000001A75: frozen_conv_tile_lookup = {32'd9, 32'd7, 32'd32256};
                40'h0000001A76: frozen_conv_tile_lookup = {32'd9, 32'd8, 32'd36864};
                40'h0000001A77: frozen_conv_tile_lookup = {32'd9, 32'd9, 32'd41472};
                40'h0000001A78: frozen_conv_tile_lookup = {32'd9, 32'd10, 32'd46080};
                40'h0000001A80: frozen_conv_tile_lookup = {32'd10, 32'd2, 32'd10240};
                40'h0000001A81: frozen_conv_tile_lookup = {32'd10, 32'd3, 32'd15360};
                40'h0000001A82: frozen_conv_tile_lookup = {32'd10, 32'd4, 32'd20480};
                40'h0000001A83: frozen_conv_tile_lookup = {32'd10, 32'd5, 32'd25600};
                40'h0000001A84: frozen_conv_tile_lookup = {32'd10, 32'd6, 32'd30720};
                40'h0000001A85: frozen_conv_tile_lookup = {32'd10, 32'd7, 32'd35840};
                40'h0000001A86: frozen_conv_tile_lookup = {32'd10, 32'd8, 32'd40960};
                40'h0000001A87: frozen_conv_tile_lookup = {32'd10, 32'd9, 32'd46080};
                40'h0000001A88: frozen_conv_tile_lookup = {32'd10, 32'd10, 32'd51200};
                40'h0000001B00: frozen_conv_tile_lookup = {32'd0, 32'd0, 32'd0};
                40'h0000001B01: frozen_conv_tile_lookup = {32'd0, 32'd1, 32'd0};
                40'h0000001B02: frozen_conv_tile_lookup = {32'd0, 32'd2, 32'd0};
                40'h0000001B03: frozen_conv_tile_lookup = {32'd0, 32'd3, 32'd0};
                40'h0000001B04: frozen_conv_tile_lookup = {32'd0, 32'd4, 32'd0};
                40'h0000001B05: frozen_conv_tile_lookup = {32'd0, 32'd5, 32'd0};
                40'h0000001B06: frozen_conv_tile_lookup = {32'd0, 32'd6, 32'd0};
                40'h0000001B07: frozen_conv_tile_lookup = {32'd0, 32'd7, 32'd0};
                40'h0000001B08: frozen_conv_tile_lookup = {32'd0, 32'd8, 32'd0};
                40'h0000001B10: frozen_conv_tile_lookup = {32'd1, 32'd0, 32'd0};
                40'h0000001B11: frozen_conv_tile_lookup = {32'd1, 32'd1, 32'd512};
                40'h0000001B12: frozen_conv_tile_lookup = {32'd1, 32'd2, 32'd1024};
                40'h0000001B13: frozen_conv_tile_lookup = {32'd1, 32'd3, 32'd1536};
                40'h0000001B14: frozen_conv_tile_lookup = {32'd1, 32'd4, 32'd2048};
                40'h0000001B15: frozen_conv_tile_lookup = {32'd1, 32'd5, 32'd2560};
                40'h0000001B16: frozen_conv_tile_lookup = {32'd1, 32'd6, 32'd3072};
                40'h0000001B17: frozen_conv_tile_lookup = {32'd1, 32'd7, 32'd3584};
                40'h0000001B18: frozen_conv_tile_lookup = {32'd1, 32'd8, 32'd4096};
                40'h0000001B20: frozen_conv_tile_lookup = {32'd2, 32'd0, 32'd0};
                40'h0000001B21: frozen_conv_tile_lookup = {32'd2, 32'd1, 32'd1024};
                40'h0000001B22: frozen_conv_tile_lookup = {32'd2, 32'd2, 32'd2048};
                40'h0000001B23: frozen_conv_tile_lookup = {32'd2, 32'd3, 32'd3072};
                40'h0000001B24: frozen_conv_tile_lookup = {32'd2, 32'd4, 32'd4096};
                40'h0000001B25: frozen_conv_tile_lookup = {32'd2, 32'd5, 32'd5120};
                40'h0000001B26: frozen_conv_tile_lookup = {32'd2, 32'd6, 32'd6144};
                40'h0000001B27: frozen_conv_tile_lookup = {32'd2, 32'd7, 32'd7168};
                40'h0000001B28: frozen_conv_tile_lookup = {32'd2, 32'd8, 32'd8192};
                40'h0000001B30: frozen_conv_tile_lookup = {32'd3, 32'd0, 32'd0};
                40'h0000001B31: frozen_conv_tile_lookup = {32'd3, 32'd1, 32'd1536};
                40'h0000001B32: frozen_conv_tile_lookup = {32'd3, 32'd2, 32'd3072};
                40'h0000001B33: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd4608};
                40'h0000001B34: frozen_conv_tile_lookup = {32'd3, 32'd4, 32'd6144};
                40'h0000001B35: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd7680};
                40'h0000001B36: frozen_conv_tile_lookup = {32'd3, 32'd6, 32'd9216};
                40'h0000001B37: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd10752};
                40'h0000001B38: frozen_conv_tile_lookup = {32'd3, 32'd8, 32'd12288};
                40'h0000001B40: frozen_conv_tile_lookup = {32'd4, 32'd0, 32'd0};
                40'h0000001B41: frozen_conv_tile_lookup = {32'd4, 32'd1, 32'd2048};
                40'h0000001B42: frozen_conv_tile_lookup = {32'd4, 32'd2, 32'd4096};
                40'h0000001B43: frozen_conv_tile_lookup = {32'd4, 32'd3, 32'd6144};
                40'h0000001B44: frozen_conv_tile_lookup = {32'd4, 32'd4, 32'd8192};
                40'h0000001B45: frozen_conv_tile_lookup = {32'd4, 32'd5, 32'd10240};
                40'h0000001B46: frozen_conv_tile_lookup = {32'd4, 32'd6, 32'd12288};
                40'h0000001B47: frozen_conv_tile_lookup = {32'd4, 32'd7, 32'd14336};
                40'h0000001B48: frozen_conv_tile_lookup = {32'd4, 32'd8, 32'd16384};
                40'h0000001B50: frozen_conv_tile_lookup = {32'd5, 32'd0, 32'd0};
                40'h0000001B51: frozen_conv_tile_lookup = {32'd5, 32'd1, 32'd2560};
                40'h0000001B52: frozen_conv_tile_lookup = {32'd5, 32'd2, 32'd5120};
                40'h0000001B53: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd7680};
                40'h0000001B54: frozen_conv_tile_lookup = {32'd5, 32'd4, 32'd10240};
                40'h0000001B55: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd12800};
                40'h0000001B56: frozen_conv_tile_lookup = {32'd5, 32'd6, 32'd15360};
                40'h0000001B57: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd17920};
                40'h0000001B58: frozen_conv_tile_lookup = {32'd5, 32'd8, 32'd20480};
                40'h0000001B60: frozen_conv_tile_lookup = {32'd6, 32'd0, 32'd0};
                40'h0000001B61: frozen_conv_tile_lookup = {32'd6, 32'd1, 32'd3072};
                40'h0000001B62: frozen_conv_tile_lookup = {32'd6, 32'd2, 32'd6144};
                40'h0000001B63: frozen_conv_tile_lookup = {32'd6, 32'd3, 32'd9216};
                40'h0000001B64: frozen_conv_tile_lookup = {32'd6, 32'd4, 32'd12288};
                40'h0000001B65: frozen_conv_tile_lookup = {32'd6, 32'd5, 32'd15360};
                40'h0000001B66: frozen_conv_tile_lookup = {32'd6, 32'd6, 32'd18432};
                40'h0000001B67: frozen_conv_tile_lookup = {32'd6, 32'd7, 32'd21504};
                40'h0000001B68: frozen_conv_tile_lookup = {32'd6, 32'd8, 32'd24576};
                40'h0000001B70: frozen_conv_tile_lookup = {32'd7, 32'd0, 32'd0};
                40'h0000001B71: frozen_conv_tile_lookup = {32'd7, 32'd1, 32'd3584};
                40'h0000001B72: frozen_conv_tile_lookup = {32'd7, 32'd2, 32'd7168};
                40'h0000001B73: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd10752};
                40'h0000001B74: frozen_conv_tile_lookup = {32'd7, 32'd4, 32'd14336};
                40'h0000001B75: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd17920};
                40'h0000001B76: frozen_conv_tile_lookup = {32'd7, 32'd6, 32'd21504};
                40'h0000001B77: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd25088};
                40'h0000001B78: frozen_conv_tile_lookup = {32'd7, 32'd8, 32'd28672};
                40'h0000001B80: frozen_conv_tile_lookup = {32'd8, 32'd0, 32'd0};
                40'h0000001B81: frozen_conv_tile_lookup = {32'd8, 32'd1, 32'd4096};
                40'h0000001B82: frozen_conv_tile_lookup = {32'd8, 32'd2, 32'd8192};
                40'h0000001B83: frozen_conv_tile_lookup = {32'd8, 32'd3, 32'd12288};
                40'h0000001B84: frozen_conv_tile_lookup = {32'd8, 32'd4, 32'd16384};
                40'h0000001B85: frozen_conv_tile_lookup = {32'd8, 32'd5, 32'd20480};
                40'h0000001B86: frozen_conv_tile_lookup = {32'd8, 32'd6, 32'd24576};
                40'h0000001B87: frozen_conv_tile_lookup = {32'd8, 32'd7, 32'd28672};
                40'h0000001B88: frozen_conv_tile_lookup = {32'd8, 32'd8, 32'd32768};
                40'h0000001C00: frozen_conv_tile_lookup = {32'd2, 32'd2, 32'd1024};
                40'h0000001C01: frozen_conv_tile_lookup = {32'd2, 32'd3, 32'd1536};
                40'h0000001C02: frozen_conv_tile_lookup = {32'd2, 32'd4, 32'd2048};
                40'h0000001C03: frozen_conv_tile_lookup = {32'd2, 32'd5, 32'd2560};
                40'h0000001C04: frozen_conv_tile_lookup = {32'd2, 32'd6, 32'd3072};
                40'h0000001C05: frozen_conv_tile_lookup = {32'd2, 32'd7, 32'd3584};
                40'h0000001C06: frozen_conv_tile_lookup = {32'd2, 32'd8, 32'd4096};
                40'h0000001C07: frozen_conv_tile_lookup = {32'd2, 32'd9, 32'd4608};
                40'h0000001C08: frozen_conv_tile_lookup = {32'd2, 32'd10, 32'd5120};
                40'h0000001C10: frozen_conv_tile_lookup = {32'd3, 32'd2, 32'd1536};
                40'h0000001C11: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd2304};
                40'h0000001C12: frozen_conv_tile_lookup = {32'd3, 32'd4, 32'd3072};
                40'h0000001C13: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd3840};
                40'h0000001C14: frozen_conv_tile_lookup = {32'd3, 32'd6, 32'd4608};
                40'h0000001C15: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd5376};
                40'h0000001C16: frozen_conv_tile_lookup = {32'd3, 32'd8, 32'd6144};
                40'h0000001C17: frozen_conv_tile_lookup = {32'd3, 32'd9, 32'd6912};
                40'h0000001C18: frozen_conv_tile_lookup = {32'd3, 32'd10, 32'd7680};
                40'h0000001C20: frozen_conv_tile_lookup = {32'd4, 32'd2, 32'd2048};
                40'h0000001C21: frozen_conv_tile_lookup = {32'd4, 32'd3, 32'd3072};
                40'h0000001C22: frozen_conv_tile_lookup = {32'd4, 32'd4, 32'd4096};
                40'h0000001C23: frozen_conv_tile_lookup = {32'd4, 32'd5, 32'd5120};
                40'h0000001C24: frozen_conv_tile_lookup = {32'd4, 32'd6, 32'd6144};
                40'h0000001C25: frozen_conv_tile_lookup = {32'd4, 32'd7, 32'd7168};
                40'h0000001C26: frozen_conv_tile_lookup = {32'd4, 32'd8, 32'd8192};
                40'h0000001C27: frozen_conv_tile_lookup = {32'd4, 32'd9, 32'd9216};
                40'h0000001C28: frozen_conv_tile_lookup = {32'd4, 32'd10, 32'd10240};
                40'h0000001C30: frozen_conv_tile_lookup = {32'd5, 32'd2, 32'd2560};
                40'h0000001C31: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd3840};
                40'h0000001C32: frozen_conv_tile_lookup = {32'd5, 32'd4, 32'd5120};
                40'h0000001C33: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd6400};
                40'h0000001C34: frozen_conv_tile_lookup = {32'd5, 32'd6, 32'd7680};
                40'h0000001C35: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd8960};
                40'h0000001C36: frozen_conv_tile_lookup = {32'd5, 32'd8, 32'd10240};
                40'h0000001C37: frozen_conv_tile_lookup = {32'd5, 32'd9, 32'd11520};
                40'h0000001C38: frozen_conv_tile_lookup = {32'd5, 32'd10, 32'd12800};
                40'h0000001C40: frozen_conv_tile_lookup = {32'd6, 32'd2, 32'd3072};
                40'h0000001C41: frozen_conv_tile_lookup = {32'd6, 32'd3, 32'd4608};
                40'h0000001C42: frozen_conv_tile_lookup = {32'd6, 32'd4, 32'd6144};
                40'h0000001C43: frozen_conv_tile_lookup = {32'd6, 32'd5, 32'd7680};
                40'h0000001C44: frozen_conv_tile_lookup = {32'd6, 32'd6, 32'd9216};
                40'h0000001C45: frozen_conv_tile_lookup = {32'd6, 32'd7, 32'd10752};
                40'h0000001C46: frozen_conv_tile_lookup = {32'd6, 32'd8, 32'd12288};
                40'h0000001C47: frozen_conv_tile_lookup = {32'd6, 32'd9, 32'd13824};
                40'h0000001C48: frozen_conv_tile_lookup = {32'd6, 32'd10, 32'd15360};
                40'h0000001C50: frozen_conv_tile_lookup = {32'd7, 32'd2, 32'd3584};
                40'h0000001C51: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd5376};
                40'h0000001C52: frozen_conv_tile_lookup = {32'd7, 32'd4, 32'd7168};
                40'h0000001C53: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd8960};
                40'h0000001C54: frozen_conv_tile_lookup = {32'd7, 32'd6, 32'd10752};
                40'h0000001C55: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd12544};
                40'h0000001C56: frozen_conv_tile_lookup = {32'd7, 32'd8, 32'd14336};
                40'h0000001C57: frozen_conv_tile_lookup = {32'd7, 32'd9, 32'd16128};
                40'h0000001C58: frozen_conv_tile_lookup = {32'd7, 32'd10, 32'd17920};
                40'h0000001C60: frozen_conv_tile_lookup = {32'd8, 32'd2, 32'd4096};
                40'h0000001C61: frozen_conv_tile_lookup = {32'd8, 32'd3, 32'd6144};
                40'h0000001C62: frozen_conv_tile_lookup = {32'd8, 32'd4, 32'd8192};
                40'h0000001C63: frozen_conv_tile_lookup = {32'd8, 32'd5, 32'd10240};
                40'h0000001C64: frozen_conv_tile_lookup = {32'd8, 32'd6, 32'd12288};
                40'h0000001C65: frozen_conv_tile_lookup = {32'd8, 32'd7, 32'd14336};
                40'h0000001C66: frozen_conv_tile_lookup = {32'd8, 32'd8, 32'd16384};
                40'h0000001C67: frozen_conv_tile_lookup = {32'd8, 32'd9, 32'd18432};
                40'h0000001C68: frozen_conv_tile_lookup = {32'd8, 32'd10, 32'd20480};
                40'h0000001C70: frozen_conv_tile_lookup = {32'd9, 32'd2, 32'd4608};
                40'h0000001C71: frozen_conv_tile_lookup = {32'd9, 32'd3, 32'd6912};
                40'h0000001C72: frozen_conv_tile_lookup = {32'd9, 32'd4, 32'd9216};
                40'h0000001C73: frozen_conv_tile_lookup = {32'd9, 32'd5, 32'd11520};
                40'h0000001C74: frozen_conv_tile_lookup = {32'd9, 32'd6, 32'd13824};
                40'h0000001C75: frozen_conv_tile_lookup = {32'd9, 32'd7, 32'd16128};
                40'h0000001C76: frozen_conv_tile_lookup = {32'd9, 32'd8, 32'd18432};
                40'h0000001C77: frozen_conv_tile_lookup = {32'd9, 32'd9, 32'd20736};
                40'h0000001C78: frozen_conv_tile_lookup = {32'd9, 32'd10, 32'd23040};
                40'h0000001C80: frozen_conv_tile_lookup = {32'd10, 32'd2, 32'd5120};
                40'h0000001C81: frozen_conv_tile_lookup = {32'd10, 32'd3, 32'd7680};
                40'h0000001C82: frozen_conv_tile_lookup = {32'd10, 32'd4, 32'd10240};
                40'h0000001C83: frozen_conv_tile_lookup = {32'd10, 32'd5, 32'd12800};
                40'h0000001C84: frozen_conv_tile_lookup = {32'd10, 32'd6, 32'd15360};
                40'h0000001C85: frozen_conv_tile_lookup = {32'd10, 32'd7, 32'd17920};
                40'h0000001C86: frozen_conv_tile_lookup = {32'd10, 32'd8, 32'd20480};
                40'h0000001C87: frozen_conv_tile_lookup = {32'd10, 32'd9, 32'd23040};
                40'h0000001C88: frozen_conv_tile_lookup = {32'd10, 32'd10, 32'd25600};
                40'h0000001D00: frozen_conv_tile_lookup = {32'd0, 32'd0, 32'd0};
                40'h0000001D01: frozen_conv_tile_lookup = {32'd0, 32'd1, 32'd0};
                40'h0000001D02: frozen_conv_tile_lookup = {32'd0, 32'd2, 32'd0};
                40'h0000001D03: frozen_conv_tile_lookup = {32'd0, 32'd3, 32'd0};
                40'h0000001D04: frozen_conv_tile_lookup = {32'd0, 32'd4, 32'd0};
                40'h0000001D05: frozen_conv_tile_lookup = {32'd0, 32'd5, 32'd0};
                40'h0000001D06: frozen_conv_tile_lookup = {32'd0, 32'd6, 32'd0};
                40'h0000001D07: frozen_conv_tile_lookup = {32'd0, 32'd7, 32'd0};
                40'h0000001D08: frozen_conv_tile_lookup = {32'd0, 32'd8, 32'd0};
                40'h0000001D10: frozen_conv_tile_lookup = {32'd1, 32'd0, 32'd0};
                40'h0000001D11: frozen_conv_tile_lookup = {32'd1, 32'd1, 32'd512};
                40'h0000001D12: frozen_conv_tile_lookup = {32'd1, 32'd2, 32'd1024};
                40'h0000001D13: frozen_conv_tile_lookup = {32'd1, 32'd3, 32'd1536};
                40'h0000001D14: frozen_conv_tile_lookup = {32'd1, 32'd4, 32'd2048};
                40'h0000001D15: frozen_conv_tile_lookup = {32'd1, 32'd5, 32'd2560};
                40'h0000001D16: frozen_conv_tile_lookup = {32'd1, 32'd6, 32'd3072};
                40'h0000001D17: frozen_conv_tile_lookup = {32'd1, 32'd7, 32'd3584};
                40'h0000001D18: frozen_conv_tile_lookup = {32'd1, 32'd8, 32'd4096};
                40'h0000001D20: frozen_conv_tile_lookup = {32'd2, 32'd0, 32'd0};
                40'h0000001D21: frozen_conv_tile_lookup = {32'd2, 32'd1, 32'd1024};
                40'h0000001D22: frozen_conv_tile_lookup = {32'd2, 32'd2, 32'd2048};
                40'h0000001D23: frozen_conv_tile_lookup = {32'd2, 32'd3, 32'd3072};
                40'h0000001D24: frozen_conv_tile_lookup = {32'd2, 32'd4, 32'd4096};
                40'h0000001D25: frozen_conv_tile_lookup = {32'd2, 32'd5, 32'd5120};
                40'h0000001D26: frozen_conv_tile_lookup = {32'd2, 32'd6, 32'd6144};
                40'h0000001D27: frozen_conv_tile_lookup = {32'd2, 32'd7, 32'd7168};
                40'h0000001D28: frozen_conv_tile_lookup = {32'd2, 32'd8, 32'd8192};
                40'h0000001D30: frozen_conv_tile_lookup = {32'd3, 32'd0, 32'd0};
                40'h0000001D31: frozen_conv_tile_lookup = {32'd3, 32'd1, 32'd1536};
                40'h0000001D32: frozen_conv_tile_lookup = {32'd3, 32'd2, 32'd3072};
                40'h0000001D33: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd4608};
                40'h0000001D34: frozen_conv_tile_lookup = {32'd3, 32'd4, 32'd6144};
                40'h0000001D35: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd7680};
                40'h0000001D36: frozen_conv_tile_lookup = {32'd3, 32'd6, 32'd9216};
                40'h0000001D37: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd10752};
                40'h0000001D38: frozen_conv_tile_lookup = {32'd3, 32'd8, 32'd12288};
                40'h0000001D40: frozen_conv_tile_lookup = {32'd4, 32'd0, 32'd0};
                40'h0000001D41: frozen_conv_tile_lookup = {32'd4, 32'd1, 32'd2048};
                40'h0000001D42: frozen_conv_tile_lookup = {32'd4, 32'd2, 32'd4096};
                40'h0000001D43: frozen_conv_tile_lookup = {32'd4, 32'd3, 32'd6144};
                40'h0000001D44: frozen_conv_tile_lookup = {32'd4, 32'd4, 32'd8192};
                40'h0000001D45: frozen_conv_tile_lookup = {32'd4, 32'd5, 32'd10240};
                40'h0000001D46: frozen_conv_tile_lookup = {32'd4, 32'd6, 32'd12288};
                40'h0000001D47: frozen_conv_tile_lookup = {32'd4, 32'd7, 32'd14336};
                40'h0000001D48: frozen_conv_tile_lookup = {32'd4, 32'd8, 32'd16384};
                40'h0000001D50: frozen_conv_tile_lookup = {32'd5, 32'd0, 32'd0};
                40'h0000001D51: frozen_conv_tile_lookup = {32'd5, 32'd1, 32'd2560};
                40'h0000001D52: frozen_conv_tile_lookup = {32'd5, 32'd2, 32'd5120};
                40'h0000001D53: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd7680};
                40'h0000001D54: frozen_conv_tile_lookup = {32'd5, 32'd4, 32'd10240};
                40'h0000001D55: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd12800};
                40'h0000001D56: frozen_conv_tile_lookup = {32'd5, 32'd6, 32'd15360};
                40'h0000001D57: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd17920};
                40'h0000001D58: frozen_conv_tile_lookup = {32'd5, 32'd8, 32'd20480};
                40'h0000001D60: frozen_conv_tile_lookup = {32'd6, 32'd0, 32'd0};
                40'h0000001D61: frozen_conv_tile_lookup = {32'd6, 32'd1, 32'd3072};
                40'h0000001D62: frozen_conv_tile_lookup = {32'd6, 32'd2, 32'd6144};
                40'h0000001D63: frozen_conv_tile_lookup = {32'd6, 32'd3, 32'd9216};
                40'h0000001D64: frozen_conv_tile_lookup = {32'd6, 32'd4, 32'd12288};
                40'h0000001D65: frozen_conv_tile_lookup = {32'd6, 32'd5, 32'd15360};
                40'h0000001D66: frozen_conv_tile_lookup = {32'd6, 32'd6, 32'd18432};
                40'h0000001D67: frozen_conv_tile_lookup = {32'd6, 32'd7, 32'd21504};
                40'h0000001D68: frozen_conv_tile_lookup = {32'd6, 32'd8, 32'd24576};
                40'h0000001D70: frozen_conv_tile_lookup = {32'd7, 32'd0, 32'd0};
                40'h0000001D71: frozen_conv_tile_lookup = {32'd7, 32'd1, 32'd3584};
                40'h0000001D72: frozen_conv_tile_lookup = {32'd7, 32'd2, 32'd7168};
                40'h0000001D73: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd10752};
                40'h0000001D74: frozen_conv_tile_lookup = {32'd7, 32'd4, 32'd14336};
                40'h0000001D75: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd17920};
                40'h0000001D76: frozen_conv_tile_lookup = {32'd7, 32'd6, 32'd21504};
                40'h0000001D77: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd25088};
                40'h0000001D78: frozen_conv_tile_lookup = {32'd7, 32'd8, 32'd28672};
                40'h0000001D80: frozen_conv_tile_lookup = {32'd8, 32'd0, 32'd0};
                40'h0000001D81: frozen_conv_tile_lookup = {32'd8, 32'd1, 32'd4096};
                40'h0000001D82: frozen_conv_tile_lookup = {32'd8, 32'd2, 32'd8192};
                40'h0000001D83: frozen_conv_tile_lookup = {32'd8, 32'd3, 32'd12288};
                40'h0000001D84: frozen_conv_tile_lookup = {32'd8, 32'd4, 32'd16384};
                40'h0000001D85: frozen_conv_tile_lookup = {32'd8, 32'd5, 32'd20480};
                40'h0000001D86: frozen_conv_tile_lookup = {32'd8, 32'd6, 32'd24576};
                40'h0000001D87: frozen_conv_tile_lookup = {32'd8, 32'd7, 32'd28672};
                40'h0000001D88: frozen_conv_tile_lookup = {32'd8, 32'd8, 32'd32768};
                40'h0000002000: frozen_conv_tile_lookup = {32'd0, 32'd0, 32'd0};
                40'h0000002001: frozen_conv_tile_lookup = {32'd0, 32'd1, 32'd0};
                40'h0000002002: frozen_conv_tile_lookup = {32'd0, 32'd2, 32'd0};
                40'h0000002003: frozen_conv_tile_lookup = {32'd0, 32'd3, 32'd0};
                40'h0000002004: frozen_conv_tile_lookup = {32'd0, 32'd4, 32'd0};
                40'h0000002005: frozen_conv_tile_lookup = {32'd0, 32'd5, 32'd0};
                40'h0000002006: frozen_conv_tile_lookup = {32'd0, 32'd6, 32'd0};
                40'h0000002007: frozen_conv_tile_lookup = {32'd0, 32'd7, 32'd0};
                40'h0000002008: frozen_conv_tile_lookup = {32'd0, 32'd8, 32'd0};
                40'h0000002010: frozen_conv_tile_lookup = {32'd1, 32'd0, 32'd0};
                40'h0000002011: frozen_conv_tile_lookup = {32'd1, 32'd1, 32'd256};
                40'h0000002012: frozen_conv_tile_lookup = {32'd1, 32'd2, 32'd512};
                40'h0000002013: frozen_conv_tile_lookup = {32'd1, 32'd3, 32'd768};
                40'h0000002014: frozen_conv_tile_lookup = {32'd1, 32'd4, 32'd1024};
                40'h0000002015: frozen_conv_tile_lookup = {32'd1, 32'd5, 32'd1280};
                40'h0000002016: frozen_conv_tile_lookup = {32'd1, 32'd6, 32'd1536};
                40'h0000002017: frozen_conv_tile_lookup = {32'd1, 32'd7, 32'd1792};
                40'h0000002018: frozen_conv_tile_lookup = {32'd1, 32'd8, 32'd2048};
                40'h0000002020: frozen_conv_tile_lookup = {32'd2, 32'd0, 32'd0};
                40'h0000002021: frozen_conv_tile_lookup = {32'd2, 32'd1, 32'd512};
                40'h0000002022: frozen_conv_tile_lookup = {32'd2, 32'd2, 32'd1024};
                40'h0000002023: frozen_conv_tile_lookup = {32'd2, 32'd3, 32'd1536};
                40'h0000002024: frozen_conv_tile_lookup = {32'd2, 32'd4, 32'd2048};
                40'h0000002025: frozen_conv_tile_lookup = {32'd2, 32'd5, 32'd2560};
                40'h0000002026: frozen_conv_tile_lookup = {32'd2, 32'd6, 32'd3072};
                40'h0000002027: frozen_conv_tile_lookup = {32'd2, 32'd7, 32'd3584};
                40'h0000002028: frozen_conv_tile_lookup = {32'd2, 32'd8, 32'd4096};
                40'h0000002030: frozen_conv_tile_lookup = {32'd3, 32'd0, 32'd0};
                40'h0000002031: frozen_conv_tile_lookup = {32'd3, 32'd1, 32'd768};
                40'h0000002032: frozen_conv_tile_lookup = {32'd3, 32'd2, 32'd1536};
                40'h0000002033: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd2304};
                40'h0000002034: frozen_conv_tile_lookup = {32'd3, 32'd4, 32'd3072};
                40'h0000002035: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd3840};
                40'h0000002036: frozen_conv_tile_lookup = {32'd3, 32'd6, 32'd4608};
                40'h0000002037: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd5376};
                40'h0000002038: frozen_conv_tile_lookup = {32'd3, 32'd8, 32'd6144};
                40'h0000002040: frozen_conv_tile_lookup = {32'd4, 32'd0, 32'd0};
                40'h0000002041: frozen_conv_tile_lookup = {32'd4, 32'd1, 32'd1024};
                40'h0000002042: frozen_conv_tile_lookup = {32'd4, 32'd2, 32'd2048};
                40'h0000002043: frozen_conv_tile_lookup = {32'd4, 32'd3, 32'd3072};
                40'h0000002044: frozen_conv_tile_lookup = {32'd4, 32'd4, 32'd4096};
                40'h0000002045: frozen_conv_tile_lookup = {32'd4, 32'd5, 32'd5120};
                40'h0000002046: frozen_conv_tile_lookup = {32'd4, 32'd6, 32'd6144};
                40'h0000002047: frozen_conv_tile_lookup = {32'd4, 32'd7, 32'd7168};
                40'h0000002048: frozen_conv_tile_lookup = {32'd4, 32'd8, 32'd8192};
                40'h0000002050: frozen_conv_tile_lookup = {32'd5, 32'd0, 32'd0};
                40'h0000002051: frozen_conv_tile_lookup = {32'd5, 32'd1, 32'd1280};
                40'h0000002052: frozen_conv_tile_lookup = {32'd5, 32'd2, 32'd2560};
                40'h0000002053: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd3840};
                40'h0000002054: frozen_conv_tile_lookup = {32'd5, 32'd4, 32'd5120};
                40'h0000002055: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd6400};
                40'h0000002056: frozen_conv_tile_lookup = {32'd5, 32'd6, 32'd7680};
                40'h0000002057: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd8960};
                40'h0000002058: frozen_conv_tile_lookup = {32'd5, 32'd8, 32'd10240};
                40'h0000002060: frozen_conv_tile_lookup = {32'd6, 32'd0, 32'd0};
                40'h0000002061: frozen_conv_tile_lookup = {32'd6, 32'd1, 32'd1536};
                40'h0000002062: frozen_conv_tile_lookup = {32'd6, 32'd2, 32'd3072};
                40'h0000002063: frozen_conv_tile_lookup = {32'd6, 32'd3, 32'd4608};
                40'h0000002064: frozen_conv_tile_lookup = {32'd6, 32'd4, 32'd6144};
                40'h0000002065: frozen_conv_tile_lookup = {32'd6, 32'd5, 32'd7680};
                40'h0000002066: frozen_conv_tile_lookup = {32'd6, 32'd6, 32'd9216};
                40'h0000002067: frozen_conv_tile_lookup = {32'd6, 32'd7, 32'd10752};
                40'h0000002068: frozen_conv_tile_lookup = {32'd6, 32'd8, 32'd12288};
                40'h0000002070: frozen_conv_tile_lookup = {32'd7, 32'd0, 32'd0};
                40'h0000002071: frozen_conv_tile_lookup = {32'd7, 32'd1, 32'd1792};
                40'h0000002072: frozen_conv_tile_lookup = {32'd7, 32'd2, 32'd3584};
                40'h0000002073: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd5376};
                40'h0000002074: frozen_conv_tile_lookup = {32'd7, 32'd4, 32'd7168};
                40'h0000002075: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd8960};
                40'h0000002076: frozen_conv_tile_lookup = {32'd7, 32'd6, 32'd10752};
                40'h0000002077: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd12544};
                40'h0000002078: frozen_conv_tile_lookup = {32'd7, 32'd8, 32'd14336};
                40'h0000002080: frozen_conv_tile_lookup = {32'd8, 32'd0, 32'd0};
                40'h0000002081: frozen_conv_tile_lookup = {32'd8, 32'd1, 32'd2048};
                40'h0000002082: frozen_conv_tile_lookup = {32'd8, 32'd2, 32'd4096};
                40'h0000002083: frozen_conv_tile_lookup = {32'd8, 32'd3, 32'd6144};
                40'h0000002084: frozen_conv_tile_lookup = {32'd8, 32'd4, 32'd8192};
                40'h0000002085: frozen_conv_tile_lookup = {32'd8, 32'd5, 32'd10240};
                40'h0000002086: frozen_conv_tile_lookup = {32'd8, 32'd6, 32'd12288};
                40'h0000002087: frozen_conv_tile_lookup = {32'd8, 32'd7, 32'd14336};
                40'h0000002088: frozen_conv_tile_lookup = {32'd8, 32'd8, 32'd16384};
                40'h0000002300: frozen_conv_tile_lookup = {32'd2, 32'd2, 32'd1536};
                40'h0000002301: frozen_conv_tile_lookup = {32'd2, 32'd3, 32'd2304};
                40'h0000002302: frozen_conv_tile_lookup = {32'd2, 32'd4, 32'd3072};
                40'h0000002303: frozen_conv_tile_lookup = {32'd2, 32'd5, 32'd3840};
                40'h0000002304: frozen_conv_tile_lookup = {32'd2, 32'd6, 32'd4608};
                40'h0000002305: frozen_conv_tile_lookup = {32'd2, 32'd7, 32'd5376};
                40'h0000002306: frozen_conv_tile_lookup = {32'd2, 32'd8, 32'd6144};
                40'h0000002307: frozen_conv_tile_lookup = {32'd2, 32'd9, 32'd6912};
                40'h0000002308: frozen_conv_tile_lookup = {32'd2, 32'd10, 32'd7680};
                40'h0000002310: frozen_conv_tile_lookup = {32'd3, 32'd2, 32'd2304};
                40'h0000002311: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd3456};
                40'h0000002312: frozen_conv_tile_lookup = {32'd3, 32'd4, 32'd4608};
                40'h0000002313: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd5760};
                40'h0000002314: frozen_conv_tile_lookup = {32'd3, 32'd6, 32'd6912};
                40'h0000002315: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd8064};
                40'h0000002316: frozen_conv_tile_lookup = {32'd3, 32'd8, 32'd9216};
                40'h0000002317: frozen_conv_tile_lookup = {32'd3, 32'd9, 32'd10368};
                40'h0000002318: frozen_conv_tile_lookup = {32'd3, 32'd10, 32'd11520};
                40'h0000002320: frozen_conv_tile_lookup = {32'd4, 32'd2, 32'd3072};
                40'h0000002321: frozen_conv_tile_lookup = {32'd4, 32'd3, 32'd4608};
                40'h0000002322: frozen_conv_tile_lookup = {32'd4, 32'd4, 32'd6144};
                40'h0000002323: frozen_conv_tile_lookup = {32'd4, 32'd5, 32'd7680};
                40'h0000002324: frozen_conv_tile_lookup = {32'd4, 32'd6, 32'd9216};
                40'h0000002325: frozen_conv_tile_lookup = {32'd4, 32'd7, 32'd10752};
                40'h0000002326: frozen_conv_tile_lookup = {32'd4, 32'd8, 32'd12288};
                40'h0000002327: frozen_conv_tile_lookup = {32'd4, 32'd9, 32'd13824};
                40'h0000002328: frozen_conv_tile_lookup = {32'd4, 32'd10, 32'd15360};
                40'h0000002330: frozen_conv_tile_lookup = {32'd5, 32'd2, 32'd3840};
                40'h0000002331: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd5760};
                40'h0000002332: frozen_conv_tile_lookup = {32'd5, 32'd4, 32'd7680};
                40'h0000002333: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd9600};
                40'h0000002334: frozen_conv_tile_lookup = {32'd5, 32'd6, 32'd11520};
                40'h0000002335: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd13440};
                40'h0000002336: frozen_conv_tile_lookup = {32'd5, 32'd8, 32'd15360};
                40'h0000002337: frozen_conv_tile_lookup = {32'd5, 32'd9, 32'd17280};
                40'h0000002338: frozen_conv_tile_lookup = {32'd5, 32'd10, 32'd19200};
                40'h0000002340: frozen_conv_tile_lookup = {32'd6, 32'd2, 32'd4608};
                40'h0000002341: frozen_conv_tile_lookup = {32'd6, 32'd3, 32'd6912};
                40'h0000002342: frozen_conv_tile_lookup = {32'd6, 32'd4, 32'd9216};
                40'h0000002343: frozen_conv_tile_lookup = {32'd6, 32'd5, 32'd11520};
                40'h0000002344: frozen_conv_tile_lookup = {32'd6, 32'd6, 32'd13824};
                40'h0000002345: frozen_conv_tile_lookup = {32'd6, 32'd7, 32'd16128};
                40'h0000002346: frozen_conv_tile_lookup = {32'd6, 32'd8, 32'd18432};
                40'h0000002347: frozen_conv_tile_lookup = {32'd6, 32'd9, 32'd20736};
                40'h0000002348: frozen_conv_tile_lookup = {32'd6, 32'd10, 32'd23040};
                40'h0000002350: frozen_conv_tile_lookup = {32'd7, 32'd2, 32'd5376};
                40'h0000002351: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd8064};
                40'h0000002352: frozen_conv_tile_lookup = {32'd7, 32'd4, 32'd10752};
                40'h0000002353: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd13440};
                40'h0000002354: frozen_conv_tile_lookup = {32'd7, 32'd6, 32'd16128};
                40'h0000002355: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd18816};
                40'h0000002356: frozen_conv_tile_lookup = {32'd7, 32'd8, 32'd21504};
                40'h0000002357: frozen_conv_tile_lookup = {32'd7, 32'd9, 32'd24192};
                40'h0000002358: frozen_conv_tile_lookup = {32'd7, 32'd10, 32'd26880};
                40'h0000002360: frozen_conv_tile_lookup = {32'd8, 32'd2, 32'd6144};
                40'h0000002361: frozen_conv_tile_lookup = {32'd8, 32'd3, 32'd9216};
                40'h0000002362: frozen_conv_tile_lookup = {32'd8, 32'd4, 32'd12288};
                40'h0000002363: frozen_conv_tile_lookup = {32'd8, 32'd5, 32'd15360};
                40'h0000002364: frozen_conv_tile_lookup = {32'd8, 32'd6, 32'd18432};
                40'h0000002365: frozen_conv_tile_lookup = {32'd8, 32'd7, 32'd21504};
                40'h0000002366: frozen_conv_tile_lookup = {32'd8, 32'd8, 32'd24576};
                40'h0000002367: frozen_conv_tile_lookup = {32'd8, 32'd9, 32'd27648};
                40'h0000002368: frozen_conv_tile_lookup = {32'd8, 32'd10, 32'd30720};
                40'h0000002370: frozen_conv_tile_lookup = {32'd9, 32'd2, 32'd6912};
                40'h0000002371: frozen_conv_tile_lookup = {32'd9, 32'd3, 32'd10368};
                40'h0000002372: frozen_conv_tile_lookup = {32'd9, 32'd4, 32'd13824};
                40'h0000002373: frozen_conv_tile_lookup = {32'd9, 32'd5, 32'd17280};
                40'h0000002374: frozen_conv_tile_lookup = {32'd9, 32'd6, 32'd20736};
                40'h0000002375: frozen_conv_tile_lookup = {32'd9, 32'd7, 32'd24192};
                40'h0000002376: frozen_conv_tile_lookup = {32'd9, 32'd8, 32'd27648};
                40'h0000002377: frozen_conv_tile_lookup = {32'd9, 32'd9, 32'd31104};
                40'h0000002378: frozen_conv_tile_lookup = {32'd9, 32'd10, 32'd34560};
                40'h0000002380: frozen_conv_tile_lookup = {32'd10, 32'd2, 32'd7680};
                40'h0000002381: frozen_conv_tile_lookup = {32'd10, 32'd3, 32'd11520};
                40'h0000002382: frozen_conv_tile_lookup = {32'd10, 32'd4, 32'd15360};
                40'h0000002383: frozen_conv_tile_lookup = {32'd10, 32'd5, 32'd19200};
                40'h0000002384: frozen_conv_tile_lookup = {32'd10, 32'd6, 32'd23040};
                40'h0000002385: frozen_conv_tile_lookup = {32'd10, 32'd7, 32'd26880};
                40'h0000002386: frozen_conv_tile_lookup = {32'd10, 32'd8, 32'd30720};
                40'h0000002387: frozen_conv_tile_lookup = {32'd10, 32'd9, 32'd34560};
                40'h0000002388: frozen_conv_tile_lookup = {32'd10, 32'd10, 32'd38400};
                40'h0000002400: frozen_conv_tile_lookup = {32'd0, 32'd0, 32'd0};
                40'h0000002401: frozen_conv_tile_lookup = {32'd0, 32'd1, 32'd0};
                40'h0000002402: frozen_conv_tile_lookup = {32'd0, 32'd2, 32'd0};
                40'h0000002403: frozen_conv_tile_lookup = {32'd0, 32'd3, 32'd0};
                40'h0000002404: frozen_conv_tile_lookup = {32'd0, 32'd4, 32'd0};
                40'h0000002405: frozen_conv_tile_lookup = {32'd0, 32'd5, 32'd0};
                40'h0000002406: frozen_conv_tile_lookup = {32'd0, 32'd6, 32'd0};
                40'h0000002407: frozen_conv_tile_lookup = {32'd0, 32'd7, 32'd0};
                40'h0000002408: frozen_conv_tile_lookup = {32'd0, 32'd8, 32'd0};
                40'h0000002410: frozen_conv_tile_lookup = {32'd1, 32'd0, 32'd0};
                40'h0000002411: frozen_conv_tile_lookup = {32'd1, 32'd1, 32'd256};
                40'h0000002412: frozen_conv_tile_lookup = {32'd1, 32'd2, 32'd512};
                40'h0000002413: frozen_conv_tile_lookup = {32'd1, 32'd3, 32'd768};
                40'h0000002414: frozen_conv_tile_lookup = {32'd1, 32'd4, 32'd1024};
                40'h0000002415: frozen_conv_tile_lookup = {32'd1, 32'd5, 32'd1280};
                40'h0000002416: frozen_conv_tile_lookup = {32'd1, 32'd6, 32'd1536};
                40'h0000002417: frozen_conv_tile_lookup = {32'd1, 32'd7, 32'd1792};
                40'h0000002418: frozen_conv_tile_lookup = {32'd1, 32'd8, 32'd2048};
                40'h0000002420: frozen_conv_tile_lookup = {32'd2, 32'd0, 32'd0};
                40'h0000002421: frozen_conv_tile_lookup = {32'd2, 32'd1, 32'd512};
                40'h0000002422: frozen_conv_tile_lookup = {32'd2, 32'd2, 32'd1024};
                40'h0000002423: frozen_conv_tile_lookup = {32'd2, 32'd3, 32'd1536};
                40'h0000002424: frozen_conv_tile_lookup = {32'd2, 32'd4, 32'd2048};
                40'h0000002425: frozen_conv_tile_lookup = {32'd2, 32'd5, 32'd2560};
                40'h0000002426: frozen_conv_tile_lookup = {32'd2, 32'd6, 32'd3072};
                40'h0000002427: frozen_conv_tile_lookup = {32'd2, 32'd7, 32'd3584};
                40'h0000002428: frozen_conv_tile_lookup = {32'd2, 32'd8, 32'd4096};
                40'h0000002430: frozen_conv_tile_lookup = {32'd3, 32'd0, 32'd0};
                40'h0000002431: frozen_conv_tile_lookup = {32'd3, 32'd1, 32'd768};
                40'h0000002432: frozen_conv_tile_lookup = {32'd3, 32'd2, 32'd1536};
                40'h0000002433: frozen_conv_tile_lookup = {32'd3, 32'd3, 32'd2304};
                40'h0000002434: frozen_conv_tile_lookup = {32'd3, 32'd4, 32'd3072};
                40'h0000002435: frozen_conv_tile_lookup = {32'd3, 32'd5, 32'd3840};
                40'h0000002436: frozen_conv_tile_lookup = {32'd3, 32'd6, 32'd4608};
                40'h0000002437: frozen_conv_tile_lookup = {32'd3, 32'd7, 32'd5376};
                40'h0000002438: frozen_conv_tile_lookup = {32'd3, 32'd8, 32'd6144};
                40'h0000002440: frozen_conv_tile_lookup = {32'd4, 32'd0, 32'd0};
                40'h0000002441: frozen_conv_tile_lookup = {32'd4, 32'd1, 32'd1024};
                40'h0000002442: frozen_conv_tile_lookup = {32'd4, 32'd2, 32'd2048};
                40'h0000002443: frozen_conv_tile_lookup = {32'd4, 32'd3, 32'd3072};
                40'h0000002444: frozen_conv_tile_lookup = {32'd4, 32'd4, 32'd4096};
                40'h0000002445: frozen_conv_tile_lookup = {32'd4, 32'd5, 32'd5120};
                40'h0000002446: frozen_conv_tile_lookup = {32'd4, 32'd6, 32'd6144};
                40'h0000002447: frozen_conv_tile_lookup = {32'd4, 32'd7, 32'd7168};
                40'h0000002448: frozen_conv_tile_lookup = {32'd4, 32'd8, 32'd8192};
                40'h0000002450: frozen_conv_tile_lookup = {32'd5, 32'd0, 32'd0};
                40'h0000002451: frozen_conv_tile_lookup = {32'd5, 32'd1, 32'd1280};
                40'h0000002452: frozen_conv_tile_lookup = {32'd5, 32'd2, 32'd2560};
                40'h0000002453: frozen_conv_tile_lookup = {32'd5, 32'd3, 32'd3840};
                40'h0000002454: frozen_conv_tile_lookup = {32'd5, 32'd4, 32'd5120};
                40'h0000002455: frozen_conv_tile_lookup = {32'd5, 32'd5, 32'd6400};
                40'h0000002456: frozen_conv_tile_lookup = {32'd5, 32'd6, 32'd7680};
                40'h0000002457: frozen_conv_tile_lookup = {32'd5, 32'd7, 32'd8960};
                40'h0000002458: frozen_conv_tile_lookup = {32'd5, 32'd8, 32'd10240};
                40'h0000002460: frozen_conv_tile_lookup = {32'd6, 32'd0, 32'd0};
                40'h0000002461: frozen_conv_tile_lookup = {32'd6, 32'd1, 32'd1536};
                40'h0000002462: frozen_conv_tile_lookup = {32'd6, 32'd2, 32'd3072};
                40'h0000002463: frozen_conv_tile_lookup = {32'd6, 32'd3, 32'd4608};
                40'h0000002464: frozen_conv_tile_lookup = {32'd6, 32'd4, 32'd6144};
                40'h0000002465: frozen_conv_tile_lookup = {32'd6, 32'd5, 32'd7680};
                40'h0000002466: frozen_conv_tile_lookup = {32'd6, 32'd6, 32'd9216};
                40'h0000002467: frozen_conv_tile_lookup = {32'd6, 32'd7, 32'd10752};
                40'h0000002468: frozen_conv_tile_lookup = {32'd6, 32'd8, 32'd12288};
                40'h0000002470: frozen_conv_tile_lookup = {32'd7, 32'd0, 32'd0};
                40'h0000002471: frozen_conv_tile_lookup = {32'd7, 32'd1, 32'd1792};
                40'h0000002472: frozen_conv_tile_lookup = {32'd7, 32'd2, 32'd3584};
                40'h0000002473: frozen_conv_tile_lookup = {32'd7, 32'd3, 32'd5376};
                40'h0000002474: frozen_conv_tile_lookup = {32'd7, 32'd4, 32'd7168};
                40'h0000002475: frozen_conv_tile_lookup = {32'd7, 32'd5, 32'd8960};
                40'h0000002476: frozen_conv_tile_lookup = {32'd7, 32'd6, 32'd10752};
                40'h0000002477: frozen_conv_tile_lookup = {32'd7, 32'd7, 32'd12544};
                40'h0000002478: frozen_conv_tile_lookup = {32'd7, 32'd8, 32'd14336};
                40'h0000002480: frozen_conv_tile_lookup = {32'd8, 32'd0, 32'd0};
                40'h0000002481: frozen_conv_tile_lookup = {32'd8, 32'd1, 32'd2048};
                40'h0000002482: frozen_conv_tile_lookup = {32'd8, 32'd2, 32'd4096};
                40'h0000002483: frozen_conv_tile_lookup = {32'd8, 32'd3, 32'd6144};
                40'h0000002484: frozen_conv_tile_lookup = {32'd8, 32'd4, 32'd8192};
                40'h0000002485: frozen_conv_tile_lookup = {32'd8, 32'd5, 32'd10240};
                40'h0000002486: frozen_conv_tile_lookup = {32'd8, 32'd6, 32'd12288};
                40'h0000002487: frozen_conv_tile_lookup = {32'd8, 32'd7, 32'd14336};
                40'h0000002488: frozen_conv_tile_lookup = {32'd8, 32'd8, 32'd16384};
                default: frozen_conv_tile_lookup = 96'd0;
            endcase
        end
    endfunction

    // 必须由完整descriptor命中保护；仅替换稳定算术，所有原比较仍保留。
    function automatic logic [98:0] frozen_full_tile_lookup(input logic [31:0] layer_key);
        begin
            frozen_full_tile_lookup = 99'd0;
            case (layer_key)
                32'd0: frozen_full_tile_lookup = {19'd17, 19'd17, 32'd289, 29'd867};
                32'd1: frozen_full_tile_lookup = {19'd17, 19'd17, 32'd289, 29'd9248};
                32'd2: frozen_full_tile_lookup = {19'd10, 19'd10, 32'd100, 29'd6400};
                32'd4: frozen_full_tile_lookup = {19'd10, 19'd10, 32'd100, 29'd3200};
                32'd5: frozen_full_tile_lookup = {19'd10, 19'd10, 32'd100, 29'd3200};
                32'd7: frozen_full_tile_lookup = {19'd8, 19'd8, 32'd64, 29'd4096};
                32'd10: frozen_full_tile_lookup = {19'd10, 19'd10, 32'd100, 29'd12800};
                32'd12: frozen_full_tile_lookup = {19'd10, 19'd10, 32'd100, 29'd6400};
                32'd13: frozen_full_tile_lookup = {19'd10, 19'd10, 32'd100, 29'd6400};
                32'd15: frozen_full_tile_lookup = {19'd8, 19'd8, 32'd64, 29'd8192};
                32'd18: frozen_full_tile_lookup = {19'd10, 19'd10, 32'd100, 29'd25600};
                32'd20: frozen_full_tile_lookup = {19'd10, 19'd10, 32'd100, 29'd12800};
                32'd21: frozen_full_tile_lookup = {19'd10, 19'd10, 32'd100, 29'd12800};
                32'd23: frozen_full_tile_lookup = {19'd8, 19'd8, 32'd64, 29'd16384};
                32'd26: frozen_full_tile_lookup = {19'd10, 19'd10, 32'd100, 29'd51200};
                32'd27: frozen_full_tile_lookup = {19'd8, 19'd8, 32'd64, 29'd32768};
                32'd28: frozen_full_tile_lookup = {19'd10, 19'd10, 32'd100, 29'd25600};
                32'd29: frozen_full_tile_lookup = {19'd8, 19'd8, 32'd64, 29'd32768};
                32'd32: frozen_full_tile_lookup = {19'd8, 19'd8, 32'd64, 29'd16384};
                32'd35: frozen_full_tile_lookup = {19'd10, 19'd10, 32'd100, 29'd38400};
                32'd36: frozen_full_tile_lookup = {19'd8, 19'd8, 32'd64, 29'd16384};
                default: frozen_full_tile_lookup = 99'd0;
            endcase
        end
    endfunction

    logic [98:0] frozen_full_tile;

    logic [97:0] frozen_conv_descriptor;
    logic [95:0] frozen_conv_tile;
    logic [31:0] tile_prep_extent_y;
    logic [31:0] tile_prep_extent_x;
    logic [31:0] tile_prep_patch_height;
    logic [31:0] tile_prep_patch_width;
    logic [31:0] tile_prep_patch_bytes;

    always_comb begin
        frozen_conv_descriptor = 98'd0;
        frozen_conv_tile = 96'd0;
        frozen_full_tile = 99'd0;
        if (FROZEN_CONV_DESCRIPTOR) begin
            frozen_conv_descriptor = frozen_conv_descriptor_lookup({layer_index_latched, input_channels_latched, input_height_latched, input_width_latched, output_channels_latched, output_height_latched, output_width_latched, kernel_height_latched, kernel_width_latched, stride_y_latched, stride_x_latched, pad_left_latched, pad_right_latched, pad_top_latched, pad_bottom_latched});
            if (frozen_conv_descriptor[97]) begin
                frozen_full_tile = frozen_full_tile_lookup(layer_index_latched);
            end
        end
        tile_prep_extent_y = (output_height_latched - tile_start_y >= TILE_EDGE) ?
                             TILE_EDGE : output_height_latched - tile_start_y;
        tile_prep_extent_x = (output_width_latched - tile_start_x >= TILE_EDGE) ?
                             TILE_EDGE : output_width_latched - tile_start_x;
        tile_prep_patch_height = 32'd0;
        tile_prep_patch_width = 32'd0;
        tile_prep_patch_bytes = 32'd0;
        if (FROZEN_CONV_DESCRIPTOR) begin
            if (frozen_conv_descriptor[97]) begin
                frozen_conv_tile = frozen_conv_tile_lookup({layer_index_latched, tile_prep_extent_y[3:0], tile_prep_extent_x[3:0]});
                tile_prep_patch_height = frozen_conv_tile[95:64];
                tile_prep_patch_width = frozen_conv_tile[63:32];
                tile_prep_patch_bytes = frozen_conv_tile[31:0];
            end
        end else begin
            tile_prep_patch_height = generic_tile_patch_axis(tile_prep_extent_y, stride_y_latched, kernel_height_latched);
            tile_prep_patch_width = generic_tile_patch_axis(tile_prep_extent_x, stride_x_latched, kernel_width_latched);
            tile_prep_patch_bytes = tile_prep_patch_height * tile_prep_patch_width * input_channels_latched;
        end

        // 首分支已逐因子拒绝零；长度分支只消费正数乘积。
        // 前两因子精确64位，高32位非零必超UINT32；否则再精确乘第三因子。
        // 前两因子已在本次START登记完整unsigned64；VALIDATE只保留第三因子乘法。
        input_element_product = {32'd0, input_element_plane[31:0]} * {32'd0, input_width_latched};
        output_element_product = {32'd0, output_element_plane[31:0]} * {32'd0, output_width_latched};
        input_elements_wide = {64'd0, input_element_product};
        output_elements_wide = {64'd0, output_element_product};

        // 正C/KH/KW的R<=4608蕴含每个因子及C*KH均<=4608；低位截断另有拒绝保护。
        if (FROZEN_CONV_DESCRIPTOR) begin
            reduction_plane_narrow = frozen_conv_descriptor[96:71];
            reduction_count_narrow = frozen_conv_descriptor[70:45];
            reduction_count_bad = !frozen_conv_descriptor[97];
            reduction_count_wide = {102'd0, reduction_count_narrow};
            expected_weight_bytes_narrow = frozen_conv_descriptor[44:0];
            expected_weight_bytes_wide = {83'd0, expected_weight_bytes_narrow};
        end else begin
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
        end
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
        if (FROZEN_CONV_DESCRIPTOR) begin
            full_tile_patch_height_narrow = frozen_full_tile[98:80];
            full_tile_patch_width_narrow = frozen_full_tile[79:61];
        end else begin
            full_tile_patch_height_narrow =
                ({16'd0, full_tile_patch_delta_y} * {3'd0, stride_y_latched[15:0]}) +
                {6'd0, kernel_height_latched[12:0]};
            full_tile_patch_width_narrow =
                ({16'd0, full_tile_patch_delta_x} * {3'd0, stride_x_latched[15:0]}) +
                {6'd0, kernel_width_latched[12:0]};
        end
        full_tile_patch_height_bad =
            ((full_tile_patch_delta_y != 3'd0) && (stride_y_latched[31:16] != 16'd0)) ||
            (full_tile_patch_height_narrow[18:16] != 3'd0) ||
            (full_tile_patch_height_narrow[15:0] > 16'd51200);
        full_tile_patch_width_bad =
            ((full_tile_patch_delta_x != 3'd0) && (stride_x_latched[31:16] != 16'd0)) ||
            (full_tile_patch_width_narrow[18:16] != 3'd0) ||
            (full_tile_patch_width_narrow[15:0] > 16'd51200);
        if (FROZEN_CONV_DESCRIPTOR) begin
            full_tile_patch_plane_narrow = frozen_full_tile[60:29];
            full_tile_patch_bytes_narrow = frozen_full_tile[28:0];
        end else begin
            full_tile_patch_plane_narrow =
                {16'd0, full_tile_patch_height_narrow[15:0]} *
                {16'd0, full_tile_patch_width_narrow[15:0]};
            full_tile_patch_bytes_narrow =
                {13'd0, full_tile_patch_plane_narrow[15:0]} *
                {16'd0, input_channels_latched[12:0]};
        end
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
                tile_origin_y + $signed({32'd0, feature_scan_y});
            feature_input_x =
                tile_origin_x + $signed({32'd0, feature_scan_x});
            feature_scan_in_bounds =
                (feature_input_y >= 64'sd0) &&
                (feature_input_y < $signed({32'd0, input_height_latched})) &&
                (feature_input_x >= 64'sd0) &&
                (feature_input_x < $signed({32'd0, input_width_latched}));
            if (feature_scan_in_bounds) begin
                // 原signed bounds保证Y高32为零；只在消费分支用精确32乘32行偏移。
                feature_geometry_plane = input_geometry_plane;
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
            // 下一tap坐标与MAC错误解耦；错误仍禁止实际特征及权重读取。
            if (compute_reduction_index + 32'd1 < reduction_count_latched) begin
                compute_read_point_y = compute_point_scan_y;
                compute_read_point_x = compute_point_scan_x;
                compute_read_input_channel = compute_next_input_channel;
                compute_read_kernel_y = compute_next_kernel_y;
                compute_read_kernel_x = compute_next_kernel_x;
                compute_read_reduction_index = compute_next_reduction_index;
                compute_read_enable = !compute_bad_argument && !compute_overflow;
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
        // 空间平面在本次START登记；通道与行偏移仍保留原unsigned64模域。
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
            input_element_plane <= 64'd0;
            input_geometry_plane <= 64'd0;
            output_element_plane <= 64'd0;
            output_geometry_plane <= 64'd0;
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
            tile_origin_y <= 64'sd0;
            tile_origin_x <= 64'sd0;
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
            input_element_plane <= 64'd0;
            input_geometry_plane <= 64'd0;
            output_element_plane <= 64'd0;
            output_geometry_plane <= 64'd0;
            tile_origin_y <= 64'sd0;
            tile_origin_x <= 64'sd0;
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
                        // 同一握手沿必须消费本拍raw端口，不能读取上一任务的latched参数。
                        input_element_plane <= {32'd0, input_channels} * {32'd0, input_height};
                        input_geometry_plane <= {32'd0, input_height} * {32'd0, input_width};
                        output_element_plane <= {32'd0, output_channels} * {32'd0, output_height};
                        output_geometry_plane <= {32'd0, output_height} * {32'd0, output_width};
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
                        tile_origin_y <= 64'sd0;
                        tile_origin_x <= 64'sd0;
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
                    // 乘积、减法均按原64位二补码；随后SCAN加法仍在同一模域。
                    tile_origin_y <=
                        $signed({32'd0, tile_start_y} * {32'd0, stride_y_latched}) -
                        $signed({32'd0, pad_top_latched});
                    tile_origin_x <=
                        $signed({32'd0, tile_start_x} * {32'd0, stride_x_latched}) -
                        $signed({32'd0, pad_left_latched});
                    tile_height <= (output_height_latched - tile_start_y >= TILE_EDGE) ?
                                   TILE_EDGE : output_height_latched - tile_start_y;
                    tile_width <= (output_width_latched - tile_start_x >= TILE_EDGE) ?
                                  TILE_EDGE : output_width_latched - tile_start_x;
                    patch_height <= tile_prep_patch_height;
                    patch_width <= tile_prep_patch_width;
                    patch_byte_count <= tile_prep_patch_bytes;
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
