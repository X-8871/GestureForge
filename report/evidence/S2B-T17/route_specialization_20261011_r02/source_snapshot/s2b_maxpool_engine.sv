// S2A-T14 tiny416 三个 maxpool 层的单元素 INT8 memory datapath。
module s2b_maxpool_engine (
    input  logic        clk,
    input  logic        hard_reset,
    input  logic        abort,

    input  logic        start_valid,
    output logic        start_ready,
    input  logic [31:0] layer_index,
    input  logic [31:0] input_base_address,
    input  logic [31:0] input_length_bytes,
    input  logic [31:0] input_channels,
    input  logic [31:0] input_height,
    input  logic [31:0] input_width,
    input  logic [31:0] output_base_address,
    input  logic [31:0] output_length_bytes,
    input  logic [31:0] output_channels,
    input  logic [31:0] output_height,
    input  logic [31:0] output_width,
    input  logic [31:0] kernel_height,
    input  logic [31:0] kernel_width,
    input  logic [31:0] stride_y,
    input  logic [31:0] stride_x,
    input  logic [31:0] darknet_padding_parameter,
    input  logic [31:0] output_channel,
    input  logic [31:0] output_y,
    input  logic [31:0] output_x,

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

    output logic        result_valid,
    input  logic        result_ready,
    output logic [127:0] result_tap_addresses,
    output logic [31:0] result_output_address,
    output logic [7:0]  result_value,
    output logic [2:0]  result_error_code
);
    localparam logic [2:0] NONE = 3'd0;
    localparam logic [2:0] BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] BAD_RANGE = 3'd2;
    localparam logic [2:0] BAD_LENGTH = 3'd3;
    localparam logic [2:0] INTERNAL = 3'd6;

    localparam logic [31:0] L9_INPUT_BASE = 32'd21968896;
    localparam logic [31:0] L9_INPUT_LENGTH = 32'd1384448;
    localparam logic [31:0] L9_OUTPUT_BASE = 32'd23353344;
    localparam logic [31:0] L9_OUTPUT_LENGTH = 32'd346112;
    localparam logic [31:0] L17_INPUT_BASE = 32'd25256960;
    localparam logic [31:0] L17_INPUT_LENGTH = 32'd692224;
    localparam logic [31:0] L17_OUTPUT_BASE = 32'd25949184;
    localparam logic [31:0] L17_OUTPUT_LENGTH = 32'd173056;
    localparam logic [31:0] L25_INPUT_BASE = 32'd26900992;
    localparam logic [31:0] L25_INPUT_LENGTH = 32'd346112;
    localparam logic [31:0] L25_OUTPUT_BASE = 32'd27247104;
    localparam logic [31:0] L25_OUTPUT_LENGTH = 32'd86528;

    typedef enum logic [3:0] {
        IDLE,
        READ_REQUEST,
        READ_RESPONSE,
        REDUCE_WINDOW,
        WRITE_REQUEST,
        WRITE_RESPONSE,
        RESULT
    } state_t;

    state_t state;
    logic [31:0] tap_address_latched [0:3];
    logic [31:0] output_address_latched;
    logic [71:0] candidate_values_latched;
    logic [2:0] read_tap_index;
    logic [7:0] result_value_latched;
    logic [2:0] result_error_latched;

    logic [32:0] query_output_height;
    logic [32:0] query_output_width;
    logic [3:0] query_tap_count;
    logic [8:0] query_tap_valid_mask;
    logic [31:0] query_tap_address [0:8];
    logic [31:0] query_tap_source_channel [0:8];
    logic signed [63:0] query_tap_source_y [0:8];
    logic signed [63:0] query_tap_source_x [0:8];
    logic [2:0] query_error_code;
    logic query_inputs_valid;
    logic query_outputs_valid;
    logic [63:0] output_offset_work;
    logic [64:0] output_address_work;
    logic [31:0] selected_byte_shift;
    logic [31:0] selected_input_word_address;
    logic [3:0] selected_input_lane;
    logic [2:0] mapped_response_error;
    logic signed [7:0] window_max_value;
    logic [2:0] window_error_code;
    integer tap_index;

    int8_maxpool_geometry u_geometry (
        .input_base_address(input_base_address),
        .input_channels(input_channels),
        .input_height(input_height),
        .input_width(input_width),
        .kernel_height(32'd2),
        .kernel_width(32'd2),
        .stride_y(32'd2),
        .stride_x(32'd2),
        .darknet_padding_parameter(32'd1),
        .input_channel(output_channel),
        .output_y(output_y),
        .output_x(output_x),
        .output_height(query_output_height),
        .output_width(query_output_width),
        .tap_count(query_tap_count),
        .tap_valid_mask(query_tap_valid_mask),
        .tap_address(query_tap_address),
        .tap_source_channel(query_tap_source_channel),
        .tap_source_y(query_tap_source_y),
        .tap_source_x(query_tap_source_x),
        .error_code(query_error_code)
    );

    int8_maxpool_window u_window (
        .candidate_count(4'd4),
        .candidates(candidate_values_latched),
        .max_value(window_max_value),
        .error_code(window_error_code)
    );

    always_comb begin
        query_inputs_valid = 1'b0;
        case (layer_index)
            32'd9: begin
                query_inputs_valid =
                    (input_channels == 32'd128) &&
                    (input_height == 32'd104) && (input_width == 32'd104) &&
                    (output_channels == 32'd128) &&
                    (output_height == 32'd52) && (output_width == 32'd52) &&
                    (kernel_height == 32'd2) && (kernel_width == 32'd2) &&
                    (stride_y == 32'd2) && (stride_x == 32'd2) &&
                    (darknet_padding_parameter == 32'd1);
            end
            32'd17: begin
                query_inputs_valid =
                    (input_channels == 32'd256) &&
                    (input_height == 32'd52) && (input_width == 32'd52) &&
                    (output_channels == 32'd256) &&
                    (output_height == 32'd26) && (output_width == 32'd26) &&
                    (kernel_height == 32'd2) && (kernel_width == 32'd2) &&
                    (stride_y == 32'd2) && (stride_x == 32'd2) &&
                    (darknet_padding_parameter == 32'd1);
            end
            32'd25: begin
                query_inputs_valid =
                    (input_channels == 32'd512) &&
                    (input_height == 32'd26) && (input_width == 32'd26) &&
                    (output_channels == 32'd512) &&
                    (output_height == 32'd13) && (output_width == 32'd13) &&
                    (kernel_height == 32'd2) && (kernel_width == 32'd2) &&
                    (stride_y == 32'd2) && (stride_x == 32'd2) &&
                    (darknet_padding_parameter == 32'd1);
            end
            default: query_inputs_valid = 1'b0;
        endcase

        query_outputs_valid =
            (query_error_code == NONE) && (query_tap_count == 4'd4) &&
            (query_tap_valid_mask[3:0] == 4'b1111) &&
            (query_output_height == {1'b0, output_height}) &&
            (query_output_width == {1'b0, output_width});

        start_ready = (state == IDLE) && !hard_reset && !abort;
        backend_cancel = hard_reset || abort;
        backend_req_valid = 1'b0;
        backend_req_write = 1'b0;
        backend_req_addr = 32'd0;
        backend_req_wdata = 32'd0;
        backend_req_rstrb = 4'd0;
        backend_req_wstrb = 4'd0;

        selected_input_word_address = 32'd0;
        selected_input_lane = 4'd0;
        selected_byte_shift = 32'd0;
        if (read_tap_index < 3'd4) begin
            selected_input_word_address =
                {tap_address_latched[read_tap_index][31:2], 2'b00};
            selected_input_lane = 4'b0001 << tap_address_latched[read_tap_index][1:0];
            selected_byte_shift =
                {30'd0, tap_address_latched[read_tap_index][1:0]} * 32'd8;
        end

        if (!hard_reset && !abort) begin
            if (state == READ_REQUEST) begin
                backend_req_valid = 1'b1;
                backend_req_addr = selected_input_word_address;
                backend_req_rstrb = selected_input_lane;
            end else if (state == WRITE_REQUEST) begin
                backend_req_valid = 1'b1;
                backend_req_write = 1'b1;
                backend_req_addr = {output_address_latched[31:2], 2'b00};
                backend_req_wdata = {24'd0, result_value_latched} <<
                                    (output_address_latched[1:0] * 8);
                backend_req_wstrb = 4'b0001 << output_address_latched[1:0];
            end
        end

        result_valid = (state == RESULT);
        result_tap_addresses = {
            tap_address_latched[3], tap_address_latched[2],
            tap_address_latched[1], tap_address_latched[0]
        };
        result_output_address = output_address_latched;
        result_value = result_value_latched;
        result_error_code = result_error_latched;

        output_offset_work =
            ((({32'd0, output_channel} * {32'd0, output_height}) +
              {32'd0, output_y}) * {32'd0, output_width}) +
            {32'd0, output_x};
        output_address_work = {33'd0, output_base_address} +
                              {1'b0, output_offset_work};

        mapped_response_error = INTERNAL;
        if ((backend_rsp_error == BAD_ARGUMENT) ||
            (backend_rsp_error == BAD_RANGE) ||
            (backend_rsp_error == INTERNAL)) begin
            mapped_response_error = backend_rsp_error;
        end else if (backend_rsp_error == NONE) begin
            mapped_response_error = NONE;
        end
    end

    always_ff @(posedge clk) begin
        if (hard_reset) begin
            state <= IDLE;
            tap_address_latched[0] <= 32'd0;
            tap_address_latched[1] <= 32'd0;
            tap_address_latched[2] <= 32'd0;
            tap_address_latched[3] <= 32'd0;
            output_address_latched <= 32'd0;
            candidate_values_latched <= 72'd0;
            read_tap_index <= 3'd0;
            result_value_latched <= 8'd0;
            result_error_latched <= NONE;
        end else if (abort && (state != IDLE) && (state != RESULT)) begin
            state <= IDLE;
            tap_address_latched[0] <= 32'd0;
            tap_address_latched[1] <= 32'd0;
            tap_address_latched[2] <= 32'd0;
            tap_address_latched[3] <= 32'd0;
            output_address_latched <= 32'd0;
            candidate_values_latched <= 72'd0;
            read_tap_index <= 3'd0;
            result_value_latched <= 8'd0;
            result_error_latched <= NONE;
        end else begin
            case (state)
                IDLE: begin
                    if (start_valid && start_ready) begin
                        tap_address_latched[0] <= 32'd0;
                        tap_address_latched[1] <= 32'd0;
                        tap_address_latched[2] <= 32'd0;
                        tap_address_latched[3] <= 32'd0;
                        output_address_latched <= 32'd0;
                        candidate_values_latched <= 72'd0;
                        read_tap_index <= 3'd0;
                        result_value_latched <= 8'd0;
                        result_error_latched <= NONE;
                        if (!query_inputs_valid) begin
                            result_error_latched <= BAD_ARGUMENT;
                            state <= RESULT;
                        end else if ((input_length_bytes !=
                                      (input_channels * input_height * input_width)) ||
                                     (output_length_bytes !=
                                      (output_channels * output_height * output_width))) begin
                            result_error_latched <= BAD_LENGTH;
                            state <= RESULT;
                        end else if ((layer_index == 32'd9 &&
                                      ((input_base_address != L9_INPUT_BASE) ||
                                       (output_base_address != L9_OUTPUT_BASE) ||
                                       (input_length_bytes != L9_INPUT_LENGTH) ||
                                       (output_length_bytes != L9_OUTPUT_LENGTH)) ) ||
                                     (layer_index == 32'd17 &&
                                      ((input_base_address != L17_INPUT_BASE) ||
                                       (output_base_address != L17_OUTPUT_BASE) ||
                                       (input_length_bytes != L17_INPUT_LENGTH) ||
                                       (output_length_bytes != L17_OUTPUT_LENGTH)) ) ||
                                     (layer_index == 32'd25 &&
                                      ((input_base_address != L25_INPUT_BASE) ||
                                       (output_base_address != L25_OUTPUT_BASE) ||
                                       (input_length_bytes != L25_INPUT_LENGTH) ||
                                       (output_length_bytes != L25_OUTPUT_LENGTH)) )) begin
                            if ((input_length_bytes !=
                                 (input_channels * input_height * input_width)) ||
                                (output_length_bytes !=
                                 (output_channels * output_height * output_width))) begin
                                result_error_latched <= BAD_LENGTH;
                            end else begin
                                result_error_latched <= BAD_RANGE;
                            end
                            state <= RESULT;
                        end else if ((query_error_code != NONE) || !query_outputs_valid ||
                                     (output_channel >= output_channels) ||
                                     (output_y >= output_height) ||
                                     (output_x >= output_width) ||
                                     (output_offset_work >= {32'd0, output_length_bytes}) ||
                                     (output_address_work[64:32] != 33'd0)) begin
                            result_error_latched <=
                                (query_error_code == BAD_RANGE ||
                                 output_address_work[64:32] != 33'd0) ?
                                BAD_RANGE : BAD_ARGUMENT;
                            state <= RESULT;
                        end else begin
                            for (tap_index = 0; tap_index < 4; tap_index = tap_index + 1) begin
                                tap_address_latched[tap_index] <= query_tap_address[tap_index];
                            end
                            output_address_latched <= output_address_work[31:0];
                            state <= READ_REQUEST;
                        end
                    end
                end
                READ_REQUEST: begin
                    if (backend_req_valid && backend_req_ready) begin
                        state <= READ_RESPONSE;
                    end
                end
                READ_RESPONSE: begin
                    if (backend_rsp_valid) begin
                        if (mapped_response_error != NONE) begin
                            candidate_values_latched <= 72'd0;
                            result_value_latched <= 8'd0;
                            result_error_latched <= mapped_response_error;
                            state <= RESULT;
                        end else begin
                            candidate_values_latched[read_tap_index * 8 +: 8] <=
                                backend_rsp_rdata >> selected_byte_shift;
                            if (read_tap_index == 3'd3) begin
                                state <= REDUCE_WINDOW;
                            end else begin
                                read_tap_index <= read_tap_index + 3'd1;
                                state <= READ_REQUEST;
                            end
                        end
                    end
                end
                REDUCE_WINDOW: begin
                    if (window_error_code != NONE) begin
                        result_value_latched <= 8'd0;
                        result_error_latched <= window_error_code;
                        state <= RESULT;
                    end else begin
                        result_value_latched <= window_max_value;
                        state <= WRITE_REQUEST;
                    end
                end
                WRITE_REQUEST: begin
                    if (backend_req_valid && backend_req_ready) begin
                        state <= WRITE_RESPONSE;
                    end
                end
                WRITE_RESPONSE: begin
                    if (backend_rsp_valid) begin
                        result_error_latched <= mapped_response_error;
                        if (mapped_response_error != NONE) begin
                            result_value_latched <= 8'd0;
                        end
                        state <= RESULT;
                    end
                end
                RESULT: begin
                    if (result_valid && result_ready) begin
                        state <= IDLE;
                        result_error_latched <= NONE;
                    end
                end
                default: begin
                    state <= RESULT;
                    result_value_latched <= 8'd0;
                    result_error_latched <= INTERNAL;
                end
            endcase
        end
    end
endmodule
