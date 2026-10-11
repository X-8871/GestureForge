// S2A-T13：tiny416 layer33 单元素 INT8 nearest-repeat memory datapath。
module s2b_upsample_engine (
    input  logic        clk,
    input  logic        hard_reset,
    input  logic        abort,

    input  logic        start_valid,
    output logic        start_ready,
    input  logic [31:0] input_base_address,
    input  logic [31:0] input_length_bytes,
    input  logic [31:0] output_base_address,
    input  logic [31:0] output_length_bytes,
    input  logic [31:0] input_channels,
    input  logic [31:0] input_height,
    input  logic [31:0] input_width,
    input  logic [31:0] stride,
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

    localparam logic [31:0] INPUT_BASE = 32'd27598336;
    localparam logic [31:0] INPUT_LENGTH = 32'd21632;
    localparam logic [31:0] OUTPUT_BASE = 32'd27619968;
    localparam logic [31:0] OUTPUT_LENGTH = 32'd86528;
    localparam logic [31:0] CHANNELS = 32'd128;
    localparam logic [31:0] INPUT_DIMENSION = 32'd13;
    localparam logic [31:0] UPSAMPLE_STRIDE = 32'd2;

    typedef enum logic [2:0] {
        IDLE,
        READ_REQUEST,
        READ_RESPONSE,
        WRITE_REQUEST,
        WRITE_RESPONSE,
        RESULT
    } state_t;

    state_t state;
    logic [31:0] source_address_latched;
    logic [31:0] output_address_latched;
    logic [7:0] copied_value_latched;
    logic [2:0] result_error_latched;

    logic [63:0] query_output_height;
    logic [63:0] query_output_width;
    logic [31:0] query_source_channel;
    logic [31:0] query_source_y;
    logic [31:0] query_source_x;
    logic [31:0] query_source_address;
    logic signed [7:0] query_unused_value;
    logic [2:0] query_error_code;
    logic [1351:0] query_unused_plane;
    logic [63:0] output_offset_work;
    logic [64:0] output_address_work;
    logic [31:0] selected_byte_shift;
    logic [2:0] mapped_response_error;

    assign query_unused_plane = '0;

    int8_upsample_query u_query (
        .input_base_address(input_base_address),
        .input_channels(input_channels),
        .input_height(input_height),
        .input_width(input_width),
        .stride(32'd2),
        .input_channel(output_channel),
        .output_y(output_y),
        .output_x(output_x),
        .source_plane(query_unused_plane),
        .output_height(query_output_height),
        .output_width(query_output_width),
        .source_channel(query_source_channel),
        .source_y(query_source_y),
        .source_x(query_source_x),
        .source_address(query_source_address),
        .output_value(query_unused_value),
        .error_code(query_error_code)
    );

    always_comb begin
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
                backend_req_addr = {source_address_latched[31:2], 2'b00};
                backend_req_rstrb = 4'b0001 << source_address_latched[1:0];
            end else if (state == WRITE_REQUEST) begin
                backend_req_valid = 1'b1;
                backend_req_write = 1'b1;
                backend_req_addr = {output_address_latched[31:2], 2'b00};
                backend_req_wdata = {24'd0, copied_value_latched} <<
                                    (output_address_latched[1:0] * 8);
                backend_req_wstrb = 4'b0001 << output_address_latched[1:0];
            end
        end
        result_valid = (state == RESULT);
        result_source_address = source_address_latched;
        result_output_address = output_address_latched;
        result_value = copied_value_latched;
        result_error_code = result_error_latched;

        output_offset_work =
            ((({32'd0, output_channel} * 64'd26) + {32'd0, output_y}) * 64'd26) +
            {32'd0, output_x};
        output_address_work = {33'd0, output_base_address} +
                              {33'd0, output_offset_work};
        selected_byte_shift = {30'd0, source_address_latched[1:0]} * 32'd8;
        mapped_response_error = INTERNAL;
        if ((backend_rsp_error == 3'd1) || (backend_rsp_error == 3'd2) ||
            (backend_rsp_error == 3'd6)) begin
            mapped_response_error = backend_rsp_error;
        end else if (backend_rsp_error == NONE) begin
            mapped_response_error = NONE;
        end
    end

    always_ff @(posedge clk) begin
        if (hard_reset) begin
            state <= IDLE;
            source_address_latched <= 32'd0;
            output_address_latched <= 32'd0;
            copied_value_latched <= 8'd0;
            result_error_latched <= NONE;
        end else if (abort && (state != IDLE) && (state != RESULT)) begin
            source_address_latched <= 32'd0;
            output_address_latched <= 32'd0;
            copied_value_latched <= 8'd0;
            result_error_latched <= NONE;
            state <= IDLE;
        end else begin
            case (state)
                IDLE: begin
                    if (start_valid && start_ready) begin
                        copied_value_latched <= 8'd0;
                        result_error_latched <= NONE;
                        source_address_latched <= 32'd0;
                        output_address_latched <= 32'd0;
                        if ((input_channels != CHANNELS) ||
                            (input_height != INPUT_DIMENSION) ||
                            (input_width != INPUT_DIMENSION) ||
                            (stride != UPSAMPLE_STRIDE) ||
                            (output_channel >= CHANNELS) ||
                            (output_y >= 32'd26) || (output_x >= 32'd26)) begin
                            result_error_latched <= BAD_ARGUMENT;
                            state <= RESULT;
                        end else if ((input_length_bytes != INPUT_LENGTH) ||
                                     (output_length_bytes != OUTPUT_LENGTH)) begin
                            result_error_latched <= BAD_LENGTH;
                            state <= RESULT;
                        end else if ((input_base_address != INPUT_BASE) ||
                                     (output_base_address != OUTPUT_BASE)) begin
                            result_error_latched <= BAD_RANGE;
                            state <= RESULT;
                        end else if ((query_error_code != NONE) ||
                                     (query_source_channel != output_channel) ||
                                     (query_source_address < input_base_address) ||
                                     (({1'b0, query_source_address} -
                                       {1'b0, input_base_address}) >=
                                      {1'b0, input_length_bytes}) ||
                                     (output_address_work[64:32] != 33'd0) ||
                                     (output_offset_work >= {32'd0, output_length_bytes})) begin
                            result_error_latched <=
                                (query_error_code == BAD_RANGE) ? BAD_RANGE : BAD_ARGUMENT;
                            state <= RESULT;
                        end else begin
                            source_address_latched <= query_source_address;
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
                            copied_value_latched <= 8'd0;
                            result_error_latched <= mapped_response_error;
                            state <= RESULT;
                        end else begin
                            copied_value_latched <=
                                (backend_rsp_rdata >> selected_byte_shift);
                            state <= WRITE_REQUEST;
                        end
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
                            copied_value_latched <= 8'd0;
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
                    copied_value_latched <= 8'd0;
                    result_error_latched <= INTERNAL;
                end
            endcase
        end
    end
endmodule
