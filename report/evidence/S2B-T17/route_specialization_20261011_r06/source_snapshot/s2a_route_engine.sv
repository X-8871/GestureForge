// S2A-T15：tiny416 route 单输出元素 INT8 memory datapath。
module s2a_route_engine (
    input  logic        clk,
    input  logic        hard_reset,
    input  logic        abort,

    input  logic        start_valid,
    output logic        start_ready,
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

    input  logic [31:0] source1_base_address,
    input  logic [31:0] source1_length_bytes,
    input  logic [31:0] source1_channels,
    input  logic [31:0] source1_height,
    input  logic [31:0] source1_width,
    input  logic [31:0] source1_channel_start,
    input  logic [31:0] source1_channel_end,
    input  logic [31:0] source1_multiplier_q31,

    input  logic [31:0] output_base_address,
    input  logic [31:0] output_length_bytes,
    input  logic [31:0] output_channels,
    input  logic [31:0] output_height,
    input  logic [31:0] output_width,

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
    output logic [31:0] result_source_index,
    output logic [31:0] result_source_address,
    output logic [31:0] result_output_address,
    output logic [7:0]  result_value,
    output logic [2:0]  result_error_code
);
    localparam logic [2:0] NONE = 3'd0;
    localparam logic [2:0] BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] BAD_RANGE = 3'd2;
    localparam logic [2:0] BAD_LENGTH = 3'd3;
    localparam logic [2:0] INTERNAL = 3'd6;

    typedef enum logic [3:0] {
        IDLE,
        VALIDATE,
        READ_REQUEST,
        READ_RESPONSE,
        CHECK_VALUE,
        WRITE_REQUEST,
        WRITE_RESPONSE,
        RESULT
    } state_t;

    state_t state;

    logic [31:0] source_count_latched;
    logic [31:0] groups_latched;
    logic [31:0] group_id_latched;
    logic [31:0] output_channel_latched;
    logic [31:0] output_y_latched;
    logic [31:0] output_x_latched;

    logic [31:0] source0_base_latched;
    logic [31:0] source0_length_latched;
    logic [31:0] source0_channels_latched;
    logic [31:0] source0_height_latched;
    logic [31:0] source0_width_latched;
    logic [31:0] source0_start_latched;
    logic [31:0] source0_end_latched;
    logic [31:0] source0_multiplier_latched;
    logic signed [7:0] source0_value_latched;

    logic [31:0] source1_base_latched;
    logic [31:0] source1_length_latched;
    logic [31:0] source1_channels_latched;
    logic [31:0] source1_height_latched;
    logic [31:0] source1_width_latched;
    logic [31:0] source1_start_latched;
    logic [31:0] source1_end_latched;
    logic [31:0] source1_multiplier_latched;
    logic signed [7:0] source1_value_latched;

    logic [31:0] output_base_latched;
    logic [31:0] output_length_latched;
    logic [31:0] output_channels_latched;
    logic [31:0] output_height_latched;
    logic [31:0] output_width_latched;

    logic [31:0] source_index_latched;
    logic [31:0] source_address_latched;
    logic [31:0] output_address_latched;
    logic [7:0] result_value_latched;
    logic [2:0] result_error_latched;

    logic [31:0] query_output_channels;
    logic [31:0] query_output_height;
    logic [31:0] query_output_width;
    logic [31:0] query_source_index;
    logic [31:0] query_source_channel;
    logic [31:0] query_source_address;
    logic signed [7:0] query_output_value;
    logic [2:0] query_error_code;

    logic [64:0] output_elements_work;
    logic [64:0] output_offset_work;
    logic [64:0] output_end_work;
    logic [31:0] selected_word_address;
    logic [3:0] selected_read_lane;
    logic [31:0] selected_byte_shift;
    logic [2:0] mapped_response_error;

    int8_route_query u_query (
        .source_count(source_count_latched),
        .groups(groups_latched),
        .group_id(group_id_latched),
        .output_channel(output_channel_latched),
        .output_y(output_y_latched),
        .output_x(output_x_latched),
        .source0_base_address(source0_base_latched),
        .source0_length_bytes(source0_length_latched),
        .source0_channels(source0_channels_latched),
        .source0_height(source0_height_latched),
        .source0_width(source0_width_latched),
        .source0_channel_start(source0_start_latched),
        .source0_channel_end(source0_end_latched),
        .source0_multiplier_q31(source0_multiplier_latched),
        .source0_value(source0_value_latched),
        .source1_base_address(source1_base_latched),
        .source1_length_bytes(source1_length_latched),
        .source1_channels(source1_channels_latched),
        .source1_height(source1_height_latched),
        .source1_width(source1_width_latched),
        .source1_channel_start(source1_start_latched),
        .source1_channel_end(source1_end_latched),
        .source1_multiplier_q31(source1_multiplier_latched),
        .source1_value(source1_value_latched),
        .output_channels(query_output_channels),
        .output_height(query_output_height),
        .output_width(query_output_width),
        .source_index(query_source_index),
        .source_channel(query_source_channel),
        .source_address(query_source_address),
        .output_value(query_output_value),
        .error_code(query_error_code)
    );

    always_comb begin
        output_elements_work = {33'd0, output_channels_latched} *
                               {33'd0, output_height_latched} *
                               {33'd0, output_width_latched};
        output_offset_work =
            (({33'd0, output_channel_latched} * {33'd0, output_height_latched}) +
             {33'd0, output_y_latched}) * {33'd0, output_width_latched} +
            {33'd0, output_x_latched};
        output_end_work = {33'd0, output_base_latched} +
                          {33'd0, output_length_latched};

        selected_word_address = {source_address_latched[31:2], 2'b00};
        selected_read_lane = 4'b0001 << source_address_latched[1:0];
        selected_byte_shift = {30'd0, source_address_latched[1:0]} * 32'd8;

        mapped_response_error = INTERNAL;
        if ((backend_rsp_error == BAD_ARGUMENT) ||
            (backend_rsp_error == BAD_RANGE) ||
            (backend_rsp_error == INTERNAL)) begin
            mapped_response_error = backend_rsp_error;
        end else if (backend_rsp_error == NONE) begin
            mapped_response_error = NONE;
        end

        start_ready = (state == IDLE) && !hard_reset && !abort;
        backend_cancel = hard_reset || abort;
        backend_req_valid = 1'b0;
        backend_req_write = 1'b0;
        backend_req_addr = 32'd0;
        backend_req_wdata = 32'd0;
        backend_req_rstrb = 4'd0;
        backend_req_wstrb = 4'd0;
        if (!hard_reset && !abort) begin
            if (state == READ_REQUEST) begin
                backend_req_valid = 1'b1;
                backend_req_addr = selected_word_address;
                backend_req_rstrb = selected_read_lane;
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
        result_source_index = source_index_latched;
        result_source_address = source_address_latched;
        result_output_address = output_address_latched;
        result_value = result_value_latched;
        result_error_code = result_error_latched;
    end

    always_ff @(posedge clk) begin
        if (hard_reset) begin
            state <= IDLE;
            source_count_latched <= 32'd0;
            groups_latched <= 32'd0;
            group_id_latched <= 32'd0;
            output_channel_latched <= 32'd0;
            output_y_latched <= 32'd0;
            output_x_latched <= 32'd0;
            source0_base_latched <= 32'd0;
            source0_length_latched <= 32'd0;
            source0_channels_latched <= 32'd0;
            source0_height_latched <= 32'd0;
            source0_width_latched <= 32'd0;
            source0_start_latched <= 32'd0;
            source0_end_latched <= 32'd0;
            source0_multiplier_latched <= 32'd0;
            source0_value_latched <= 8'sd0;
            source1_base_latched <= 32'd0;
            source1_length_latched <= 32'd0;
            source1_channels_latched <= 32'd0;
            source1_height_latched <= 32'd0;
            source1_width_latched <= 32'd0;
            source1_start_latched <= 32'd0;
            source1_end_latched <= 32'd0;
            source1_multiplier_latched <= 32'd0;
            source1_value_latched <= 8'sd0;
            output_base_latched <= 32'd0;
            output_length_latched <= 32'd0;
            output_channels_latched <= 32'd0;
            output_height_latched <= 32'd0;
            output_width_latched <= 32'd0;
            source_index_latched <= 32'd0;
            source_address_latched <= 32'd0;
            output_address_latched <= 32'd0;
            result_value_latched <= 8'd0;
            result_error_latched <= NONE;
        end else if (abort && (state != IDLE) && (state != RESULT)) begin
            state <= IDLE;
            source_index_latched <= 32'd0;
            source_address_latched <= 32'd0;
            output_address_latched <= 32'd0;
            result_value_latched <= 8'd0;
            result_error_latched <= NONE;
            source0_value_latched <= 8'sd0;
            source1_value_latched <= 8'sd0;
        end else begin
            case (state)
                IDLE: begin
                    if (start_valid && start_ready) begin
                        source_count_latched <= source_count;
                        groups_latched <= groups;
                        group_id_latched <= group_id;
                        output_channel_latched <= output_channel;
                        output_y_latched <= output_y;
                        output_x_latched <= output_x;
                        source0_base_latched <= source0_base_address;
                        source0_length_latched <= source0_length_bytes;
                        source0_channels_latched <= source0_channels;
                        source0_height_latched <= source0_height;
                        source0_width_latched <= source0_width;
                        source0_start_latched <= source0_channel_start;
                        source0_end_latched <= source0_channel_end;
                        source0_multiplier_latched <= source0_multiplier_q31;
                        source0_value_latched <= 8'sd0;
                        source1_base_latched <= source1_base_address;
                        source1_length_latched <= source1_length_bytes;
                        source1_channels_latched <= source1_channels;
                        source1_height_latched <= source1_height;
                        source1_width_latched <= source1_width;
                        source1_start_latched <= source1_channel_start;
                        source1_end_latched <= source1_channel_end;
                        source1_multiplier_latched <= source1_multiplier_q31;
                        source1_value_latched <= 8'sd0;
                        output_base_latched <= output_base_address;
                        output_length_latched <= output_length_bytes;
                        output_channels_latched <= output_channels;
                        output_height_latched <= output_height;
                        output_width_latched <= output_width;
                        source_index_latched <= 32'd0;
                        source_address_latched <= 32'd0;
                        output_address_latched <= 32'd0;
                        result_value_latched <= 8'd0;
                        result_error_latched <= NONE;
                        state <= VALIDATE;
                    end
                end
                VALIDATE: begin
                    if ((query_error_code != NONE) ||
                        (query_output_channels != output_channels_latched) ||
                        (query_output_height != output_height_latched) ||
                        (query_output_width != output_width_latched) ||
                        (output_channels_latched == 32'd0) ||
                        (output_height_latched == 32'd0) ||
                        (output_width_latched == 32'd0) ||
                        (output_length_latched == 32'd0) ||
                        (output_elements_work > {33'd0, output_length_latched})) begin
                        result_error_latched <=
                            (query_error_code == BAD_RANGE) ? BAD_RANGE :
                            ((query_error_code == BAD_ARGUMENT) ? BAD_ARGUMENT : BAD_LENGTH);
                        state <= RESULT;
                    end else if (output_end_work > 65'h0000_0001_0000_0000) begin
                        result_error_latched <= BAD_RANGE;
                        state <= RESULT;
                    end else if ((output_offset_work >= {33'd0, output_length_latched}) ||
                                 (output_base_latched + output_offset_work[31:0] < output_base_latched)) begin
                        result_error_latched <= BAD_RANGE;
                        state <= RESULT;
                    end else begin
                        source_index_latched <= query_source_index;
                        source_address_latched <= query_source_address;
                        output_address_latched <=
                            output_base_latched + output_offset_work[31:0];
                        state <= READ_REQUEST;
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
                            result_value_latched <= 8'd0;
                            result_error_latched <= mapped_response_error;
                            state <= RESULT;
                        end else if (source_index_latched == 32'd0) begin
                            source0_value_latched <=
                                $signed(backend_rsp_rdata >> selected_byte_shift);
                            state <= CHECK_VALUE;
                        end else if (source_index_latched == 32'd1) begin
                            source1_value_latched <=
                                $signed(backend_rsp_rdata >> selected_byte_shift);
                            state <= CHECK_VALUE;
                        end else begin
                            result_value_latched <= 8'd0;
                            result_error_latched <= INTERNAL;
                            state <= RESULT;
                        end
                    end
                end
                CHECK_VALUE: begin
                    if (query_error_code != NONE) begin
                        result_value_latched <= 8'd0;
                        result_error_latched <= query_error_code;
                        state <= RESULT;
                    end else begin
                        result_value_latched <= query_output_value;
                        result_error_latched <= NONE;
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
                    state <= IDLE;
                    result_value_latched <= 8'd0;
                    result_error_latched <= INTERNAL;
                end
            endcase
        end
    end
endmodule
