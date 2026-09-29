// S2A-T17：按 NCHW/reduction 顺序计算一个 INT8 卷积输出元素。
module s2a_conv_engine (
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
    input  logic [31:0] output_channel,
    input  logic [31:0] output_y,
    input  logic [31:0] output_x,
    input  logic signed [31:0] bias_int32,
    input  logic [1:0] activation_mode,
    input  logic [31:0] positive_multiplier,
    input  logic [31:0] positive_q_shift,
    input  logic [31:0] negative_multiplier,
    input  logic [31:0] negative_q_shift,

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
    output logic [31:0] result_output_address,
    output logic [7:0]  result_value,
    output logic [2:0]  result_error_code
);
    localparam logic [2:0] NONE = 3'd0;
    localparam logic [2:0] BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] BAD_RANGE = 3'd2;
    localparam logic [2:0] BAD_LENGTH = 3'd3;
    localparam logic [2:0] INTERNAL = 3'd6;
    localparam logic [2:0] ACCUMULATOR_OVERFLOW = 3'd7;

    typedef enum logic [3:0] {
        ST_IDLE,
        ST_VALIDATE,
        ST_MAC_START,
        ST_SELECT_TAP,
        ST_FEATURE_REQUEST,
        ST_FEATURE_RESPONSE,
        ST_WEIGHT_REQUEST,
        ST_WEIGHT_RESPONSE,
        ST_MAC_OPERAND,
        ST_MAC_RESULT,
        ST_OUTPUT_REQUEST,
        ST_OUTPUT_RESPONSE,
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
    logic [31:0] output_channel_latched;
    logic [31:0] output_y_latched;
    logic [31:0] output_x_latched;
    logic signed [31:0] bias_latched;
    logic [1:0] activation_mode_latched;
    logic [31:0] positive_multiplier_latched;
    logic [31:0] positive_q_shift_latched;
    logic [31:0] negative_multiplier_latched;
    logic [31:0] negative_q_shift_latched;

    logic [31:0] reduction_index;
    logic [31:0] reduction_count_latched;
    logic [31:0] output_address_latched;
    logic signed [7:0] feature_byte_latched;
    logic signed [7:0] weight_byte_latched;
    logic [7:0] result_value_latched;
    logic [2:0] result_error_latched;

    logic [31:0] geometry_input_channel;
    logic [31:0] geometry_kernel_y;
    logic [31:0] geometry_kernel_x;
    logic signed [31:0] geometry_input_y;
    logic signed [31:0] geometry_input_x;
    logic geometry_tap_is_padding;
    logic geometry_source_address_valid;
    logic [31:0] geometry_source_address;
    logic signed [7:0] geometry_padding_value;
    logic [2:0] geometry_error_code;

    logic [31:0] weight_reduction_index;
    logic [31:0] weight_layer_byte_offset;
    logic [31:0] weight_package_byte_offset;
    logic [31:0] weight_byte_address;
    logic [2:0] weight_error_code;

    logic [127:0] input_elements_work;
    logic [127:0] output_elements_work;
    logic [127:0] expected_weight_bytes_work;
    logic [127:0] reduction_count_work;
    logic [127:0] output_offset_work;
    logic [127:0] input_end_work;
    logic [127:0] output_end_work;
    logic [127:0] weight_package_end_work;
    logic [127:0] output_address_work;
    logic validation_ok;
    logic [2:0] validation_error;

    logic [31:0] selected_feature_word_address;
    logic [3:0] selected_feature_lane;
    logic [31:0] selected_feature_shift;
    logic [31:0] selected_weight_word_address;
    logic [3:0] selected_weight_lane;
    logic [31:0] selected_weight_shift;
    logic [31:0] selected_output_word_address;
    logic [31:0] selected_output_shift;
    logic [3:0] selected_output_strobe;
    logic [2:0] mapped_response_error;

    logic mac_start_valid;
    logic mac_start_ready;
    logic [12:0] mac_start_k;
    logic signed [31:0] mac_start_bias;
    logic mac_operand_valid;
    logic mac_operand_ready;
    logic signed [7:0] mac_activation_data;
    logic signed [7:0] mac_weight_data;
    logic mac_result_valid;
    logic mac_result_ready;
    logic signed [31:0] mac_result_data;
    logic [2:0] mac_error_code;
    logic mac_busy;
    logic mac_cancel;

    logic [31:0] selected_multiplier;
    logic [31:0] selected_q_shift;
    logic [31:0] accumulator_magnitude;
    logic [63:0] requant_product;
    logic [63:0] requant_rounding_add;
    logic [63:0] requant_rounded_magnitude;
    logic signed [63:0] requant_signed_value;
    logic signed [7:0] requantized_value;

    int8_conv_tap_geometry u_geometry (
        .input_base_address(input_base_latched),
        .input_length_bytes(input_length_latched),
        .input_batch_count(input_batch_count_latched),
        .input_channels(input_channels_latched),
        .input_height(input_height_latched),
        .input_width(input_width_latched),
        .output_batch_count(output_batch_count_latched),
        .output_channels(output_channels_latched),
        .output_height(output_height_latched),
        .output_width(output_width_latched),
        .kernel_height(kernel_height_latched),
        .kernel_width(kernel_width_latched),
        .stride_y(stride_y_latched),
        .stride_x(stride_x_latched),
        .pad_left(pad_left_latched),
        .pad_right(pad_right_latched),
        .pad_top(pad_top_latched),
        .pad_bottom(pad_bottom_latched),
        .padding_value_int8(padding_latched[7:0]),
        .groups(groups_latched),
        .output_batch(output_batch_latched),
        .output_channel(output_channel_latched),
        .output_y(output_y_latched),
        .output_x(output_x_latched),
        .reduction_index(reduction_index),
        .input_channel(geometry_input_channel),
        .kernel_y(geometry_kernel_y),
        .kernel_x(geometry_kernel_x),
        .input_y(geometry_input_y),
        .input_x(geometry_input_x),
        .tap_is_padding(geometry_tap_is_padding),
        .source_address_valid(geometry_source_address_valid),
        .source_address(geometry_source_address),
        .tap_padding_value(geometry_padding_value),
        .error_code(geometry_error_code)
    );

    int8_conv_weight_address u_weight_address (
        .layer_index(layer_index_latched),
        .weight_layer_index(weight_layer_index_latched),
        .groups(groups_latched),
        .output_channels(output_channels_latched),
        .input_channels(input_channels_latched),
        .kernel_height(kernel_height_latched),
        .kernel_width(kernel_width_latched),
        .quantized_weight_offset(quantized_weight_offset_latched),
        .quantized_weight_bytes(quantized_weight_bytes_latched),
        .weight_package_base_address(weight_package_base_latched),
        .weight_package_length_bytes(weight_package_length_latched),
        .query_output_channel(output_channel_latched),
        .query_input_channel(geometry_input_channel),
        .query_kernel_y(geometry_kernel_y),
        .query_kernel_x(geometry_kernel_x),
        .reduction_index(weight_reduction_index),
        .layer_weight_byte_offset(weight_layer_byte_offset),
        .package_byte_offset(weight_package_byte_offset),
        .weight_byte_address(weight_byte_address),
        .error_code(weight_error_code)
    );

    int8_mac_accumulator u_mac (
        .clk(clk),
        .rst(hard_reset),
        .abort(mac_cancel),
        .start_valid(mac_start_valid),
        .start_ready(mac_start_ready),
        .start_k(mac_start_k),
        .start_bias(mac_start_bias),
        .operand_valid(mac_operand_valid),
        .operand_ready(mac_operand_ready),
        .activation_data(mac_activation_data),
        .weight_data(mac_weight_data),
        .result_valid(mac_result_valid),
        .result_ready(mac_result_ready),
        .result_data(mac_result_data),
        .error_code(mac_error_code),
        .busy(mac_busy)
    );

    always_comb begin
        input_elements_work = {96'd0, input_batch_count_latched} *
                              {96'd0, input_channels_latched} *
                              {96'd0, input_height_latched} *
                              {96'd0, input_width_latched};
        output_elements_work = {96'd0, output_batch_count_latched} *
                               {96'd0, output_channels_latched} *
                               {96'd0, output_height_latched} *
                               {96'd0, output_width_latched};
        expected_weight_bytes_work = {96'd0, output_channels_latched} *
                                     {96'd0, input_channels_latched} *
                                     {96'd0, kernel_height_latched} *
                                     {96'd0, kernel_width_latched};
        reduction_count_work = {96'd0, input_channels_latched} *
                               {96'd0, kernel_height_latched} *
                               {96'd0, kernel_width_latched};
        output_offset_work =
            ((({96'd0, output_batch_latched} * {96'd0, output_channels_latched}) +
               {96'd0, output_channel_latched}) * {96'd0, output_height_latched} +
              {96'd0, output_y_latched}) * {96'd0, output_width_latched} +
              {96'd0, output_x_latched};
        input_end_work = {96'd0, input_base_latched} + {96'd0, input_length_latched};
        output_end_work = {96'd0, output_base_latched} + {96'd0, output_length_latched};
        weight_package_end_work = {96'd0, weight_package_base_latched} +
                                  {96'd0, weight_package_length_latched};
        output_address_work = {96'd0, output_base_latched} + output_offset_work;

        validation_ok = 1'b0;
        validation_error = BAD_ARGUMENT;
        if (!buffer_owner_pl ||
            (activation_mode_latched > 2'd1) ||
            (positive_multiplier_latched == 32'd0) ||
            (negative_multiplier_latched == 32'd0) ||
            (positive_multiplier_latched > 32'h3FFF_FFFF) ||
            (negative_multiplier_latched > 32'h3FFF_FFFF) ||
            (positive_q_shift_latched > 32'd47) ||
            (negative_q_shift_latched > 32'd47) ||
            ((activation_mode_latched == 2'd0) &&
             ((positive_multiplier_latched != negative_multiplier_latched) ||
              (positive_q_shift_latched != negative_q_shift_latched))) ||
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
            (output_channel_latched >= output_channels_latched) ||
            (output_y_latched >= output_height_latched) ||
            (output_x_latched >= output_width_latched) ||
            (reduction_count_work == 128'd0) ||
            (reduction_count_work > 128'd8191)) begin
            validation_error = BAD_ARGUMENT;
        end else if ((input_length_latched != input_elements_work[31:0]) ||
                     (input_elements_work > 128'h0000_0000_0000_0000_FFFF_FFFF) ||
                     (output_length_latched != output_elements_work[31:0]) ||
                     (output_elements_work > 128'h0000_0000_0000_0000_FFFF_FFFF) ||
                     (quantized_weight_bytes_latched != expected_weight_bytes_work[31:0]) ||
                     (expected_weight_bytes_work > 128'h0000_0000_0000_0000_FFFF_FFFF)) begin
            validation_error = BAD_LENGTH;
        end else if ((input_end_work > 128'h0000_0000_0000_0001_0000_0000) ||
                     (output_end_work > 128'h0000_0000_0000_0001_0000_0000) ||
                     (weight_package_end_work > 128'h0000_0000_0000_0001_0000_0000) ||
                     (weight_package_length_latched == 32'd0) ||
                     (output_offset_work >= output_elements_work) ||
                     (output_address_work > 128'h0000_0000_0000_0000_FFFF_FFFF) ||
                     (layer_index_latched != weight_layer_index_latched)) begin
            validation_error = BAD_RANGE;
        end else if ((geometry_error_code != NONE) ||
                     (weight_error_code != NONE)) begin
            if ((geometry_error_code == BAD_RANGE) ||
                (weight_error_code == BAD_RANGE) ||
                (layer_index_latched != weight_layer_index_latched)) begin
                validation_error = BAD_RANGE;
            end else begin
                validation_error = BAD_ARGUMENT;
            end
        end else begin
            validation_ok = 1'b1;
            validation_error = NONE;
        end

        selected_feature_word_address = {geometry_source_address[31:2], 2'b00};
        selected_feature_lane = 4'b0001 << geometry_source_address[1:0];
        selected_feature_shift = {30'd0, geometry_source_address[1:0]} * 32'd8;
        selected_weight_word_address = {weight_byte_address[31:2], 2'b00};
        selected_weight_lane = 4'b0001 << weight_byte_address[1:0];
        selected_weight_shift = {30'd0, weight_byte_address[1:0]} * 32'd8;
        selected_output_word_address = {output_address_latched[31:2], 2'b00};
        selected_output_shift = {30'd0, output_address_latched[1:0]} * 32'd8;
        selected_output_strobe = 4'b0001 << output_address_latched[1:0];

        mapped_response_error = INTERNAL;
        if (backend_rsp_error == NONE) begin
            mapped_response_error = NONE;
        end else if ((backend_rsp_error == BAD_ARGUMENT) ||
                     (backend_rsp_error == BAD_RANGE) ||
                     (backend_rsp_error == INTERNAL)) begin
            mapped_response_error = backend_rsp_error;
        end

        mac_cancel = abort ||
                     ((state == ST_SELECT_TAP) &&
                      ((geometry_error_code != NONE) || (weight_error_code != NONE))) ||
                     ((state == ST_FEATURE_RESPONSE) && backend_rsp_valid &&
                      (mapped_response_error != NONE)) ||
                     ((state == ST_WEIGHT_RESPONSE) && backend_rsp_valid &&
                      (mapped_response_error != NONE));

        selected_multiplier = mac_result_data[31] ?
                              negative_multiplier_latched : positive_multiplier_latched;
        selected_q_shift = mac_result_data[31] ?
                           negative_q_shift_latched : positive_q_shift_latched;
        accumulator_magnitude = mac_result_data[31] ?
                                (~$unsigned(mac_result_data) + 32'd1) :
                                $unsigned(mac_result_data);
        requant_product = {32'd0, accumulator_magnitude} *
                          {32'd0, selected_multiplier};
        requant_rounding_add = 64'd0;
        if (selected_q_shift != 32'd0) begin
            requant_rounding_add = 64'd1 << (selected_q_shift - 32'd1);
        end
        requant_rounded_magnitude = (requant_product + requant_rounding_add) >>
                                    selected_q_shift;
        if (mac_result_data[31]) begin
            requant_signed_value = -$signed({1'b0, requant_rounded_magnitude});
        end else begin
            requant_signed_value = $signed({1'b0, requant_rounded_magnitude});
        end
        if (requant_signed_value > 64'sd127) begin
            requantized_value = 8'sd127;
        end else if (requant_signed_value < -64'sd127) begin
            requantized_value = -8'sd127;
        end else begin
            requantized_value = requant_signed_value[7:0];
        end

        start_ready = (state == ST_IDLE) && !hard_reset && !abort;
        busy = (state != ST_IDLE);
        result_valid = (state == ST_RESULT);
        result_output_address = output_address_latched;
        result_value = result_value_latched;
        result_error_code = result_error_latched;
        backend_cancel = hard_reset || abort;
        backend_req_valid = 1'b0;
        backend_req_write = 1'b0;
        backend_req_addr = 32'd0;
        backend_req_wdata = 32'd0;
        backend_req_rstrb = 4'd0;
        backend_req_wstrb = 4'd0;
        mac_start_valid = 1'b0;
        mac_start_k = reduction_count_latched[12:0];
        mac_start_bias = bias_latched;
        mac_operand_valid = 1'b0;
        mac_activation_data = feature_byte_latched;
        mac_weight_data = weight_byte_latched;
        mac_result_ready = 1'b0;

        if (!hard_reset && !abort) begin
            case (state)
                ST_MAC_START: mac_start_valid = 1'b1;
                ST_FEATURE_REQUEST: begin
                    backend_req_valid = 1'b1;
                    backend_req_addr = selected_feature_word_address;
                    backend_req_rstrb = selected_feature_lane;
                end
                ST_WEIGHT_REQUEST: begin
                    backend_req_valid = 1'b1;
                    backend_req_addr = selected_weight_word_address;
                    backend_req_rstrb = selected_weight_lane;
                end
                ST_MAC_OPERAND: mac_operand_valid = 1'b1;
                ST_MAC_RESULT: mac_result_ready = 1'b1;
                ST_OUTPUT_REQUEST: begin
                    backend_req_valid = 1'b1;
                    backend_req_write = 1'b1;
                    backend_req_addr = selected_output_word_address;
                    backend_req_wdata = {24'd0, result_value_latched} << selected_output_shift;
                    backend_req_wstrb = selected_output_strobe;
                end
                default: begin
                end
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
            output_channel_latched <= 32'd0;
            output_y_latched <= 32'd0;
            output_x_latched <= 32'd0;
            bias_latched <= 32'sd0;
            activation_mode_latched <= 2'd0;
            positive_multiplier_latched <= 32'd0;
            positive_q_shift_latched <= 32'd0;
            negative_multiplier_latched <= 32'd0;
            negative_q_shift_latched <= 32'd0;
            reduction_index <= 32'd0;
            reduction_count_latched <= 32'd0;
            output_address_latched <= 32'd0;
            feature_byte_latched <= 8'sd0;
            weight_byte_latched <= 8'sd0;
            result_value_latched <= 8'd0;
            result_error_latched <= NONE;
        end else if (abort) begin
            state <= ST_IDLE;
            reduction_index <= 32'd0;
            reduction_count_latched <= 32'd0;
            output_address_latched <= 32'd0;
            feature_byte_latched <= 8'sd0;
            weight_byte_latched <= 8'sd0;
            result_value_latched <= 8'd0;
            result_error_latched <= NONE;
        end else begin
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
                        output_channel_latched <= output_channel;
                        output_y_latched <= output_y;
                        output_x_latched <= output_x;
                        bias_latched <= bias_int32;
                        activation_mode_latched <= activation_mode;
                        positive_multiplier_latched <= positive_multiplier;
                        positive_q_shift_latched <= positive_q_shift;
                        negative_multiplier_latched <= negative_multiplier;
                        negative_q_shift_latched <= negative_q_shift;
                        reduction_index <= 32'd0;
                        reduction_count_latched <= 32'd0;
                        output_address_latched <= 32'd0;
                        feature_byte_latched <= 8'sd0;
                        weight_byte_latched <= 8'sd0;
                        result_value_latched <= 8'd0;
                        result_error_latched <= NONE;
                        state <= ST_VALIDATE;
                    end
                end
                ST_VALIDATE: begin
                    if (!validation_ok) begin
                        result_error_latched <= validation_error;
                        result_value_latched <= 8'd0;
                        output_address_latched <= 32'd0;
                        state <= ST_RESULT;
                    end else begin
                        reduction_count_latched <= reduction_count_work[31:0];
                        output_address_latched <= output_address_work[31:0];
                        state <= ST_MAC_START;
                    end
                end
                ST_MAC_START: begin
                    if (mac_start_valid && mac_start_ready) begin
                        reduction_index <= 32'd0;
                        state <= ST_SELECT_TAP;
                    end
                end
                ST_SELECT_TAP: begin
                    if (mac_result_valid) begin
                        state <= ST_MAC_RESULT;
                    end else if (geometry_error_code != NONE) begin
                        result_value_latched <= 8'd0;
                        result_error_latched <= geometry_error_code;
                        state <= ST_RESULT;
                    end else if (weight_error_code != NONE) begin
                        result_value_latched <= 8'd0;
                        result_error_latched <= weight_error_code;
                        state <= ST_RESULT;
                    end else if (geometry_tap_is_padding) begin
                        feature_byte_latched <= 8'sd0;
                        weight_byte_latched <= 8'sd0;
                        state <= ST_MAC_OPERAND;
                    end else if (!geometry_source_address_valid) begin
                        result_value_latched <= 8'd0;
                        result_error_latched <= INTERNAL;
                        state <= ST_RESULT;
                    end else begin
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
                            result_value_latched <= 8'd0;
                            result_error_latched <= mapped_response_error;
                            state <= ST_RESULT;
                        end else begin
                            feature_byte_latched <= $signed(
                                backend_rsp_rdata >> selected_feature_shift
                            );
                            state <= ST_WEIGHT_REQUEST;
                        end
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
                            result_value_latched <= 8'd0;
                            result_error_latched <= mapped_response_error;
                            state <= ST_RESULT;
                        end else begin
                            weight_byte_latched <= $signed(
                                backend_rsp_rdata >> selected_weight_shift
                            );
                            state <= ST_MAC_OPERAND;
                        end
                    end
                end
                ST_MAC_OPERAND: begin
                    if (mac_result_valid) begin
                        state <= ST_MAC_RESULT;
                    end else if (mac_operand_valid && mac_operand_ready) begin
                        if (reduction_index + 32'd1 == reduction_count_latched) begin
                            state <= ST_MAC_RESULT;
                        end else begin
                            reduction_index <= reduction_index + 32'd1;
                            state <= ST_SELECT_TAP;
                        end
                    end
                end
                ST_MAC_RESULT: begin
                    if (mac_result_valid && mac_result_ready) begin
                        if (mac_error_code != NONE) begin
                            result_value_latched <= 8'd0;
                            result_error_latched <= mac_error_code;
                            state <= ST_RESULT;
                        end else begin
                            result_value_latched <= requantized_value[7:0];
                            result_error_latched <= NONE;
                            state <= ST_OUTPUT_REQUEST;
                        end
                    end
                end
                ST_OUTPUT_REQUEST: begin
                    if (backend_req_valid && backend_req_ready) begin
                        state <= ST_OUTPUT_RESPONSE;
                    end
                end
                ST_OUTPUT_RESPONSE: begin
                    if (backend_rsp_valid) begin
                        result_error_latched <= mapped_response_error;
                        if (mapped_response_error != NONE) begin
                            result_value_latched <= 8'd0;
                        end
                        state <= ST_RESULT;
                    end
                end
                ST_RESULT: begin
                    if (result_valid && result_ready) begin
                        state <= ST_IDLE;
                        result_error_latched <= NONE;
                    end
                end
                default: begin
                    state <= ST_IDLE;
                    reduction_index <= 32'd0;
                    reduction_count_latched <= 32'd0;
                    result_value_latched <= 8'd0;
                    result_error_latched <= INTERNAL;
                end
            endcase
        end
    end
endmodule
