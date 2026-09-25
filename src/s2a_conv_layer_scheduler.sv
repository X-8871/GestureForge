// S2A-T20：固定 tiny416 layer36 卷积输出坐标调度器。
module s2a_conv_layer_scheduler #(
    // 正式固定 layer36 实例保留 20280 默认值；仅测试边界实例用编译期参数设为 1。
    // 此参数不是运行时层尺寸或 descriptor 接口。
    parameter logic [14:0] OUTPUT_COUNT_LIMIT = 15'd20280
) (
    input  logic        clk,
    input  logic        hard_reset,
    input  logic        abort,
    input  logic        buffer_owner_pl,
    input  logic        start_valid,
    output logic        start_ready,
    input  logic [31:0] timeout_cycles,
    input  logic        completion_ready,
    output logic        busy,
    output logic        done,
    output logic        error,
    output logic [2:0]  error_code,
    output logic [14:0] completed_elements,

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
    input  logic [2:0]  backend_rsp_error
);
    localparam logic [2:0] NONE = 3'd0;
    localparam logic [2:0] BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] INTERNAL = 3'd6;
    localparam logic [2:0] TIMEOUT = 3'd5;

    localparam logic [31:0] INPUT_BASE = 32'd27966080;
    localparam logic [31:0] INPUT_LENGTH = 32'd173056;
    localparam logic [31:0] INPUT_CHANNELS = 32'd256;
    localparam logic [31:0] HEIGHT = 32'd26;
    localparam logic [31:0] WIDTH = 32'd26;
    localparam logic [31:0] OUTPUT_BASE = 32'd28139136;
    localparam logic [31:0] OUTPUT_LENGTH = 32'd20280;
    localparam logic [31:0] OUTPUT_CHANNELS = 32'd30;
    localparam logic [31:0] KERNEL_SIZE = 32'd256;
    localparam logic [31:0] WEIGHT_PACKAGE_BASE = 32'd1048576;
    localparam logic [31:0] WEIGHT_PACKAGE_LENGTH = 32'd5903100;
    localparam logic [31:0] WEIGHT_OFFSET = 32'd5895420;
    localparam logic [31:0] WEIGHT_BYTES = 32'd7680;

    typedef enum logic [2:0] {
        IDLE,
        CHILD_START,
        CHILD_WAIT,
        DONE,
        ERROR
    } state_t;

    state_t state;
    logic [31:0] output_channel_index;
    logic [31:0] output_y_index;
    logic [31:0] output_x_index;
    logic [31:0] timeout_limit_latched;
    logic [31:0] elapsed_cycles;
    logic timeout_deadline;
    logic backend_error_event;

    logic child_start_ready;
    logic child_abort;
    logic child_backend_cancel;
    logic child_req_valid;
    logic child_req_write;
    logic [31:0] child_req_addr;
    logic [31:0] child_req_wdata;
    logic [3:0] child_req_rstrb;
    logic [3:0] child_req_wstrb;
    logic child_result_valid;
    logic child_result_ready;
    logic [31:0] child_result_output_address;
    logic [7:0] child_result_value;
    logic [2:0] child_result_error_code;
    logic signed [31:0] channel_bias;
    logic [31:0] channel_multiplier;
    logic [31:0] expected_output_address;
    logic child_error_event;
    logic child_final_success_event;

    function automatic logic [2:0] map_backend_error(input logic [2:0] code);
        begin
            case (code)
                3'd1, 3'd2, 3'd6: map_backend_error = code;
                default: map_backend_error = INTERNAL;
            endcase
        end
    endfunction

    function automatic logic signed [31:0] bias_for_channel(
        input logic [31:0] channel
    );
        begin
            case (channel)
                32'd0: bias_for_channel = -32'sd40;
                32'd1: bias_for_channel = 32'sd164;
                32'd2: bias_for_channel = 32'sd630;
                32'd3: bias_for_channel = 32'sd1326;
                32'd4: bias_for_channel = -32'sd1291;
                32'd5: bias_for_channel = -32'sd112;
                32'd6: bias_for_channel = -32'sd230;
                32'd7: bias_for_channel = -32'sd96;
                32'd8: bias_for_channel = -32'sd142;
                32'd9: bias_for_channel = -32'sd140;
                32'd10: bias_for_channel = -32'sd63;
                32'd11: bias_for_channel = 32'sd204;
                32'd12: bias_for_channel = -32'sd19;
                32'd13: bias_for_channel = -32'sd3;
                32'd14: bias_for_channel = -32'sd999;
                32'd15: bias_for_channel = -32'sd199;
                32'd16: bias_for_channel = -32'sd144;
                32'd17: bias_for_channel = -32'sd122;
                32'd18: bias_for_channel = -32'sd135;
                32'd19: bias_for_channel = -32'sd124;
                32'd20: bias_for_channel = -32'sd22;
                32'd21: bias_for_channel = 32'sd19;
                32'd22: bias_for_channel = -32'sd981;
                32'd23: bias_for_channel = 32'sd186;
                32'd24: bias_for_channel = -32'sd1047;
                32'd25: bias_for_channel = -32'sd176;
                32'd26: bias_for_channel = -32'sd89;
                32'd27: bias_for_channel = -32'sd165;
                32'd28: bias_for_channel = -32'sd118;
                32'd29: bias_for_channel = -32'sd137;
                default: bias_for_channel = 32'sd0;
            endcase
        end
    endfunction

    function automatic logic [31:0] multiplier_for_channel(
        input logic [31:0] channel
    );
        begin
            case (channel)
                32'd0: multiplier_for_channel = 32'd4521539;
                32'd1: multiplier_for_channel = 32'd1236893;
                32'd2: multiplier_for_channel = 32'd185501;
                32'd3: multiplier_for_channel = 32'd36126967;
                32'd4: multiplier_for_channel = 32'd703195;
                32'd5: multiplier_for_channel = 32'd1727583;
                32'd6: multiplier_for_channel = 32'd10899483;
                32'd7: multiplier_for_channel = 32'd2919885;
                32'd8: multiplier_for_channel = 32'd911915;
                32'd9: multiplier_for_channel = 32'd14363353;
                32'd10: multiplier_for_channel = 32'd11000719;
                32'd11: multiplier_for_channel = 32'd11372807;
                32'd12: multiplier_for_channel = 32'd9310791;
                32'd13: multiplier_for_channel = 32'd1280979;
                32'd14: multiplier_for_channel = 32'd931085;
                32'd15: multiplier_for_channel = 32'd3299743;
                32'd16: multiplier_for_channel = 32'd6110579;
                32'd17: multiplier_for_channel = 32'd1489969;
                32'd18: multiplier_for_channel = 32'd319819;
                32'd19: multiplier_for_channel = 32'd15080773;
                32'd20: multiplier_for_channel = 32'd4217309;
                32'd21: multiplier_for_channel = 32'd491685;
                32'd22: multiplier_for_channel = 32'd4250589;
                32'd23: multiplier_for_channel = 32'd17733479;
                32'd24: multiplier_for_channel = 32'd255023;
                32'd25: multiplier_for_channel = 32'd116125;
                32'd26: multiplier_for_channel = 32'd9767409;
                32'd27: multiplier_for_channel = 32'd4476747;
                32'd28: multiplier_for_channel = 32'd4341945;
                32'd29: multiplier_for_channel = 32'd4566843;
                default: multiplier_for_channel = 32'd0;
            endcase
        end
    endfunction

    function automatic logic [31:0] q_shift_for_channel(
        input logic [31:0] channel
    );
        begin
            case (channel)
                32'd0: q_shift_for_channel = 32'd33;
                32'd1: q_shift_for_channel = 32'd31;
                32'd2: q_shift_for_channel = 32'd29;
                32'd3: q_shift_for_channel = 32'd37;
                32'd4: q_shift_for_channel = 32'd29;
                32'd5: q_shift_for_channel = 32'd30;
                32'd6: q_shift_for_channel = 32'd33;
                32'd7: q_shift_for_channel = 32'd31;
                32'd8: q_shift_for_channel = 32'd29;
                32'd9: q_shift_for_channel = 32'd33;
                32'd10: q_shift_for_channel = 32'd34;
                32'd11: q_shift_for_channel = 32'd34;
                32'd12: q_shift_for_channel = 32'd35;
                32'd13: q_shift_for_channel = 32'd32;
                32'd14: q_shift_for_channel = 32'd29;
                32'd15: q_shift_for_channel = 32'd31;
                32'd16: q_shift_for_channel = 32'd32;
                32'd17: q_shift_for_channel = 32'd30;
                32'd18: q_shift_for_channel = 32'd28;
                32'd19: q_shift_for_channel = 32'd33;
                32'd20: q_shift_for_channel = 32'd33;
                32'd21: q_shift_for_channel = 32'd30;
                32'd22: q_shift_for_channel = 32'd34;
                32'd23: q_shift_for_channel = 32'd36;
                32'd24: q_shift_for_channel = 32'd27;
                32'd25: q_shift_for_channel = 32'd27;
                32'd26: q_shift_for_channel = 32'd33;
                32'd27: q_shift_for_channel = 32'd32;
                32'd28: q_shift_for_channel = 32'd32;
                32'd29: q_shift_for_channel = 32'd32;
                default: q_shift_for_channel = 32'd0;
            endcase
        end
    endfunction

    assign start_ready = (state == IDLE) && !hard_reset && !abort;
    assign busy = (state == CHILD_START) || (state == CHILD_WAIT);
    assign done = (state == DONE);
    assign error = (state == ERROR);
    assign child_result_ready = (state == CHILD_WAIT);
    // timeout/error 状态在决定沿之后才撤销子引擎及未完成 memory 请求。
    assign child_abort = abort || (state == ERROR);
    assign backend_cancel = hard_reset || abort || (state == ERROR) ||
                            child_backend_cancel;
    assign backend_req_valid = child_req_valid;
    assign backend_req_write = child_req_write;
    assign backend_req_addr = child_req_addr;
    assign backend_req_wdata = child_req_wdata;
    assign backend_req_rstrb = child_req_rstrb;
    assign backend_req_wstrb = child_req_wstrb;
    assign channel_bias = bias_for_channel(output_channel_index);
    assign channel_multiplier = multiplier_for_channel(output_channel_index);
    assign expected_output_address = OUTPUT_BASE +
        ((output_channel_index * HEIGHT + output_y_index) * WIDTH + output_x_index);
    assign child_error_event = child_result_valid && child_result_ready &&
                               (child_result_error_code != NONE);
    assign backend_error_event = backend_rsp_valid &&
                                 (backend_rsp_error != NONE);
    assign child_final_success_event = child_result_valid && child_result_ready &&
        (child_result_error_code == NONE) &&
        (completed_elements == (OUTPUT_COUNT_LIMIT - 15'd1));

    always_comb begin
        timeout_deadline = 1'b0;
        if (busy && (timeout_limit_latched != 32'd0) &&
            (elapsed_cycles == (timeout_limit_latched - 32'd1))) begin
            timeout_deadline = 1'b1;
        end
    end

    s2a_conv_engine u_element_engine (
        .clk(clk),
        .hard_reset(hard_reset),
        .abort(child_abort),
        .buffer_owner_pl(buffer_owner_pl),
        .start_valid(state == CHILD_START),
        .start_ready(child_start_ready),
        .layer_index(32'd36),
        .weight_layer_index(32'd36),
        .input_base_address(INPUT_BASE),
        .input_length_bytes(INPUT_LENGTH),
        .input_batch_count(32'd1),
        .input_channels(INPUT_CHANNELS),
        .input_height(HEIGHT),
        .input_width(WIDTH),
        .output_base_address(OUTPUT_BASE),
        .output_length_bytes(OUTPUT_LENGTH),
        .output_batch_count(32'd1),
        .output_channels(OUTPUT_CHANNELS),
        .output_height(HEIGHT),
        .output_width(WIDTH),
        .kernel_height(32'd1),
        .kernel_width(32'd1),
        .stride_y(32'd1),
        .stride_x(32'd1),
        .pad_left(32'd0),
        .pad_right(32'd0),
        .pad_top(32'd0),
        .pad_bottom(32'd0),
        .groups(32'd1),
        .padding_value_int8(32'sd0),
        .weight_package_base_address(WEIGHT_PACKAGE_BASE),
        .weight_package_length_bytes(WEIGHT_PACKAGE_LENGTH),
        .quantized_weight_offset(WEIGHT_OFFSET),
        .quantized_weight_bytes(WEIGHT_BYTES),
        .output_batch(32'd0),
        .output_channel(output_channel_index),
        .output_y(output_y_index),
        .output_x(output_x_index),
        .bias_int32(channel_bias),
        .activation_mode(2'd0),
        .positive_multiplier(channel_multiplier),
        .positive_q_shift(q_shift_for_channel(output_channel_index)),
        .negative_multiplier(channel_multiplier),
        .negative_q_shift(q_shift_for_channel(output_channel_index)),
        .backend_cancel(child_backend_cancel),
        .backend_req_valid(child_req_valid),
        .backend_req_ready(backend_req_ready),
        .backend_req_write(child_req_write),
        .backend_req_addr(child_req_addr),
        .backend_req_wdata(child_req_wdata),
        .backend_req_rstrb(child_req_rstrb),
        .backend_req_wstrb(child_req_wstrb),
        .backend_rsp_valid(backend_rsp_valid),
        .backend_rsp_rdata(backend_rsp_rdata),
        .backend_rsp_error(backend_rsp_error),
        .busy(),
        .result_valid(child_result_valid),
        .result_ready(child_result_ready),
        .result_output_address(child_result_output_address),
        .result_value(child_result_value),
        .result_error_code(child_result_error_code)
    );

    always_ff @(posedge clk) begin
        if (hard_reset || abort) begin
            state <= IDLE;
            output_channel_index <= 32'd0;
            output_y_index <= 32'd0;
            output_x_index <= 32'd0;
            completed_elements <= 15'd0;
            timeout_limit_latched <= 32'd0;
            elapsed_cycles <= 32'd0;
            error_code <= NONE;
        end else if (timeout_deadline && child_error_event) begin
            state <= ERROR;
            error_code <= child_result_error_code;
        end else if (timeout_deadline && backend_error_event) begin
            state <= ERROR;
            error_code <= map_backend_error(backend_rsp_error);
        end else if (timeout_deadline && !child_final_success_event) begin
            state <= ERROR;
            error_code <= TIMEOUT;
        end else begin
            case (state)
                IDLE: begin
                    if (start_valid && start_ready) begin
                        output_channel_index <= 32'd0;
                        output_y_index <= 32'd0;
                        output_x_index <= 32'd0;
                        completed_elements <= 15'd0;
                        elapsed_cycles <= 32'd0;
                        timeout_limit_latched <= timeout_cycles;
                        error_code <= NONE;
                        if (timeout_cycles == 32'd0) begin
                            error_code <= BAD_ARGUMENT;
                            state <= ERROR;
                        end else begin
                            state <= CHILD_START;
                        end
                    end
                end
                CHILD_START: begin
                    elapsed_cycles <= elapsed_cycles + 32'd1;
                    if (child_start_ready) begin
                        state <= CHILD_WAIT;
                    end
                end
                CHILD_WAIT: begin
                    if (child_result_valid && child_result_ready) begin
                        if (child_result_error_code != NONE) begin
                            error_code <= child_result_error_code;
                            state <= ERROR;
                        end else if (child_result_output_address != expected_output_address) begin
                            error_code <= INTERNAL;
                            state <= ERROR;
                        end else begin
                            completed_elements <= completed_elements + 15'd1;
                            if (completed_elements == (OUTPUT_COUNT_LIMIT - 15'd1)) begin
                                state <= DONE;
                            end else begin
                                elapsed_cycles <= elapsed_cycles + 32'd1;
                                if (output_x_index + 32'd1 < WIDTH) begin
                                    output_x_index <= output_x_index + 32'd1;
                                    state <= CHILD_START;
                                end else if (output_y_index + 32'd1 < HEIGHT) begin
                                    output_x_index <= 32'd0;
                                    output_y_index <= output_y_index + 32'd1;
                                    state <= CHILD_START;
                                end else begin
                                    output_x_index <= 32'd0;
                                    output_y_index <= 32'd0;
                                    output_channel_index <= output_channel_index + 32'd1;
                                    state <= CHILD_START;
                                end
                            end
                        end
                    end else begin
                        elapsed_cycles <= elapsed_cycles + 32'd1;
                    end
                end
                DONE: begin
                    if (completion_ready) begin
                        state <= IDLE;
                        error_code <= NONE;
                    end
                end
                ERROR: begin
                    if (completion_ready) begin
                        state <= IDLE;
                        error_code <= NONE;
                    end
                end
                default: begin
                    state <= ERROR;
                    error_code <= INTERNAL;
                end
            endcase
        end
    end
endmodule
