// S2A-T21：tiny416 固定 layer25 maxpool 整层调度器。
module s2a_maxpool_layer_scheduler #(
    // 仅由边界仿真的单元素实例覆盖；固定层默认尺寸不由运行时输入修改。
    parameter logic [16:0] OUTPUT_COUNT_LIMIT = 17'd86528
) (
    input  logic        clk,
    input  logic        hard_reset,
    input  logic        abort,
    input  logic        start_valid,
    output logic        start_ready,
    input  logic [31:0] timeout_cycles,
    input  logic        completion_ready,
    output logic        busy,
    output logic        done,
    output logic        error,
    output logic [2:0]  error_code,
    output logic [16:0] completed_elements,

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

    localparam logic [31:0] INPUT_BASE = 32'd26900992;
    localparam logic [31:0] INPUT_LENGTH = 32'd346112;
    localparam logic [31:0] OUTPUT_BASE = 32'd27247104;
    localparam logic [31:0] OUTPUT_LENGTH = 32'd86528;
    localparam logic [31:0] CHANNELS = 32'd512;
    localparam logic [31:0] INPUT_DIMENSION = 32'd26;
    localparam logic [31:0] OUTPUT_DIMENSION = 32'd13;
    typedef enum logic [2:0] {
        IDLE,
        CHILD_START,
        CHILD_WAIT,
        DONE,
        ERROR
    } state_t;

    state_t state;
    logic [31:0] channel_index;
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
    logic [127:0] child_result_tap_addresses;
    logic [31:0] child_result_output_address;
    logic [7:0] child_result_value;
    logic [2:0] child_result_error_code;
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

    assign start_ready = (state == IDLE) && !hard_reset && !abort;
    assign busy = (state == CHILD_START) || (state == CHILD_WAIT);
    assign done = (state == DONE);
    assign error = (state == ERROR);
    // 终态也接收已在边界沿产生的子引擎结果，使 ACK 后子引擎可恢复空闲。
    assign child_result_ready = (state == CHILD_WAIT) || (state == ERROR);

    // 超时决策后才撤销子引擎和未完成的 memory 请求。
    assign child_abort = abort || (state == ERROR);
    assign backend_cancel = hard_reset || abort || (state == ERROR) ||
                            child_backend_cancel;
    assign backend_req_valid = child_req_valid;
    assign backend_req_write = child_req_write;
    assign backend_req_addr = child_req_addr;
    assign backend_req_wdata = child_req_wdata;
    assign backend_req_rstrb = child_req_rstrb;
    assign backend_req_wstrb = child_req_wstrb;
    assign expected_output_address = OUTPUT_BASE +
        ((channel_index * OUTPUT_DIMENSION + output_y_index) * OUTPUT_DIMENSION +
         output_x_index);
    assign child_error_event = child_result_valid && child_result_ready &&
                               (child_result_error_code != NONE);
    assign backend_error_event = backend_rsp_valid &&
                                 (backend_rsp_error != NONE);
    assign child_final_success_event = child_result_valid && child_result_ready &&
        (child_result_error_code == NONE) &&
        (completed_elements == (OUTPUT_COUNT_LIMIT - 17'd1));

    always_comb begin
        timeout_deadline = 1'b0;
        if (busy && (timeout_limit_latched != 32'd0) &&
            (elapsed_cycles == (timeout_limit_latched - 32'd1))) begin
            timeout_deadline = 1'b1;
        end
    end

    s2a_maxpool_engine u_element_engine (
        .clk(clk),
        .hard_reset(hard_reset),
        .abort(child_abort),
        .start_valid(state == CHILD_START),
        .start_ready(child_start_ready),
        .layer_index(32'd25),
        .input_base_address(INPUT_BASE),
        .input_length_bytes(INPUT_LENGTH),
        .input_channels(CHANNELS),
        .input_height(INPUT_DIMENSION),
        .input_width(INPUT_DIMENSION),
        .output_base_address(OUTPUT_BASE),
        .output_length_bytes(OUTPUT_LENGTH),
        .output_channels(CHANNELS),
        .output_height(OUTPUT_DIMENSION),
        .output_width(OUTPUT_DIMENSION),
        .kernel_height(32'd2),
        .kernel_width(32'd2),
        .stride_y(32'd2),
        .stride_x(32'd2),
        .darknet_padding_parameter(32'd1),
        .output_channel(channel_index),
        .output_y(output_y_index),
        .output_x(output_x_index),
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
        .result_valid(child_result_valid),
        .result_ready(child_result_ready),
        .result_tap_addresses(child_result_tap_addresses),
        .result_output_address(child_result_output_address),
        .result_value(child_result_value),
        .result_error_code(child_result_error_code)
    );

    always_ff @(posedge clk) begin
        if (hard_reset || abort) begin
            state <= IDLE;
            channel_index <= 32'd0;
            output_y_index <= 32'd0;
            output_x_index <= 32'd0;
            completed_elements <= 17'd0;
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
                        channel_index <= 32'd0;
                        output_y_index <= 32'd0;
                        output_x_index <= 32'd0;
                        completed_elements <= 17'd0;
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
                            completed_elements <= completed_elements + 17'd1;
                            if (completed_elements == (OUTPUT_COUNT_LIMIT - 17'd1)) begin
                                state <= DONE;
                            end else begin
                                elapsed_cycles <= elapsed_cycles + 32'd1;
                                if (output_x_index + 32'd1 < OUTPUT_DIMENSION) begin
                                    output_x_index <= output_x_index + 32'd1;
                                    state <= CHILD_START;
                                end else if (output_y_index + 32'd1 < OUTPUT_DIMENSION) begin
                                    output_x_index <= 32'd0;
                                    output_y_index <= output_y_index + 32'd1;
                                    state <= CHILD_START;
                                end else begin
                                    output_x_index <= 32'd0;
                                    output_y_index <= 32'd0;
                                    channel_index <= channel_index + 32'd1;
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
