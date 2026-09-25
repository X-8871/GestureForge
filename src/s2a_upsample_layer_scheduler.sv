// S2A-T18：tiny416 layer33 的逐坐标 nearest-repeat 整层调度器。
module s2a_upsample_layer_scheduler (
    // start_ready 仅在空闲时拉高；busy 覆盖正在执行的逐点事务。
    input  logic        clk,
    input  logic        hard_reset,
    input  logic        abort,

    input  logic        start_valid,
    output logic        start_ready,
    // done/error 与最终计数或错误码保持到 completion_ready 握手。
    input  logic        completion_ready,
    output logic        busy,
    output logic        done,
    output logic        error,
    output logic [2:0]  error_code,
    // 正常运行中只在子元素事务成功后递增；abort/硬复位时清零。
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
    localparam logic [2:0] INTERNAL = 3'd6;
    localparam logic [31:0] INPUT_BASE = 32'd27598336;
    localparam logic [31:0] INPUT_LENGTH = 32'd21632;
    localparam logic [31:0] OUTPUT_BASE = 32'd27619968;
    localparam logic [31:0] OUTPUT_LENGTH = 32'd86528;
    localparam logic [31:0] CHANNELS = 32'd128;
    localparam logic [31:0] INPUT_DIMENSION = 32'd13;
    localparam logic [31:0] OUTPUT_DIMENSION = 32'd26;
    localparam logic [31:0] UPSAMPLE_STRIDE = 32'd2;
    localparam logic [16:0] OUTPUT_COUNT = 17'd86528;

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
    logic child_start_ready;
    logic child_backend_cancel;
    logic child_req_valid;
    logic child_req_write;
    logic [31:0] child_req_addr;
    logic [31:0] child_req_wdata;
    logic [3:0] child_req_rstrb;
    logic [3:0] child_req_wstrb;
    logic child_result_valid;
    logic child_result_ready;
    logic [31:0] child_source_address;
    logic [31:0] child_output_address;
    logic [7:0] child_value;
    logic [2:0] child_error_code;

    assign start_ready = (state == IDLE) && !hard_reset && !abort;
    assign busy = (state == CHILD_START) || (state == CHILD_WAIT);
    assign done = (state == DONE);
    assign error = (state == ERROR);
    assign backend_cancel = hard_reset || abort || child_backend_cancel;
    assign backend_req_valid = child_req_valid;
    assign backend_req_write = child_req_write;
    assign backend_req_addr = child_req_addr;
    assign backend_req_wdata = child_req_wdata;
    assign backend_req_rstrb = child_req_rstrb;
    assign backend_req_wstrb = child_req_wstrb;
    assign child_result_ready = (state == CHILD_WAIT);

    s2a_upsample_engine u_element_engine (
        .clk(clk),
        .hard_reset(hard_reset),
        .abort(abort),
        .start_valid(state == CHILD_START),
        .start_ready(child_start_ready),
        .input_base_address(INPUT_BASE),
        .input_length_bytes(INPUT_LENGTH),
        .output_base_address(OUTPUT_BASE),
        .output_length_bytes(OUTPUT_LENGTH),
        .input_channels(CHANNELS),
        .input_height(INPUT_DIMENSION),
        .input_width(INPUT_DIMENSION),
        .stride(UPSAMPLE_STRIDE),
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
        .result_source_address(child_source_address),
        .result_output_address(child_output_address),
        .result_value(child_value),
        .result_error_code(child_error_code)
    );

    always_ff @(posedge clk) begin
        if (hard_reset || abort) begin
            state <= IDLE;
            channel_index <= 32'd0;
            output_y_index <= 32'd0;
            output_x_index <= 32'd0;
            completed_elements <= 17'd0;
            error_code <= NONE;
        end else begin
            case (state)
                IDLE: begin
                    if (start_valid && start_ready) begin
                        channel_index <= 32'd0;
                        output_y_index <= 32'd0;
                        output_x_index <= 32'd0;
                        completed_elements <= 17'd0;
                        error_code <= NONE;
                        state <= CHILD_START;
                    end
                end
                CHILD_START: begin
                    if (child_start_ready) begin
                        state <= CHILD_WAIT;
                    end
                end
                CHILD_WAIT: begin
                    if (child_result_valid && child_result_ready) begin
                        if (child_error_code != NONE) begin
                            error_code <= child_error_code;
                            state <= ERROR;
                        end else begin
                            completed_elements <= completed_elements + 17'd1;
                            if (completed_elements == (OUTPUT_COUNT - 17'd1)) begin
                                state <= DONE;
                            end else if (output_x_index + 32'd1 < OUTPUT_DIMENSION) begin
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
