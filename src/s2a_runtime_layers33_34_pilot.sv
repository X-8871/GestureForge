// S2A-T28：将 G0 runtime shell 串接到固定 layer33→34 两层 pilot。
module s2a_runtime_layers33_34_pilot (
    input  logic        clk,
    input  logic        hard_reset,

    input  logic        csr_valid,
    output logic        csr_ready,
    input  logic        csr_write,
    input  logic [7:0]  csr_addr,
    input  logic [31:0] csr_wdata,
    output logic [31:0] csr_rdata,

    output logic        backend_start,
    output logic        backend_abort,
    output logic        busy,
    output logic        done,
    output logic        error,
    output logic        pl_owns_buffers,
    output logic        head_output_valid,

    output logic [1:0]  active_stage,
    output logic [16:0] layer33_completed_elements,
    output logic [18:0] layer34_completed_elements,

    output logic        mem_valid,
    input  logic        mem_ready,
    output logic        mem_write,
    output logic [31:0] mem_addr,
    output logic [31:0] mem_wdata,
    output logic [3:0]  mem_rstrb,
    output logic [3:0]  mem_wstrb,
    input  logic [31:0] mem_rdata,
    input  logic [2:0]  mem_error_code
);
    typedef enum logic [2:0] {
        BACKEND_IDLE,
        START_LAYER33,
        RUN_LAYER33,
        START_LAYER34,
        RUN_LAYER34
    } backend_state_t;

    backend_state_t backend_state;
    logic soft_reset_now;
    logic child_abort;

    logic layer33_start_valid;
    logic layer33_start_ready;
    logic layer33_busy;
    logic layer33_done;
    logic layer33_error;
    logic [2:0] layer33_error_code;
    logic layer33_completion_ready;
    logic layer33_backend_cancel;
    logic layer33_req_valid;
    logic layer33_req_ready;
    logic layer33_req_write;
    logic [31:0] layer33_req_addr;
    logic [31:0] layer33_req_wdata;
    logic [3:0] layer33_req_rstrb;
    logic [3:0] layer33_req_wstrb;
    logic layer33_rsp_valid;
    logic [31:0] layer33_rsp_rdata;
    logic [2:0] layer33_rsp_error;

    logic layer34_start_valid;
    logic layer34_start_ready;
    logic layer34_busy;
    logic layer34_done;
    logic layer34_error;
    logic [2:0] layer34_error_code;
    logic layer34_completion_ready;
    logic layer34_backend_cancel;
    logic layer34_req_valid;
    logic layer34_req_ready;
    logic layer34_req_write;
    logic [31:0] layer34_req_addr;
    logic [31:0] layer34_req_wdata;
    logic [3:0] layer34_req_rstrb;
    logic [3:0] layer34_req_wstrb;
    logic layer34_rsp_valid;
    logic [31:0] layer34_rsp_rdata;
    logic [2:0] layer34_rsp_error;

    logic backend_req_valid;
    logic backend_req_ready;
    logic backend_req_write;
    logic [31:0] backend_req_addr;
    logic [31:0] backend_req_wdata;
    logic [3:0] backend_req_rstrb;
    logic [3:0] backend_req_wstrb;
    logic backend_rsp_valid;
    logic [31:0] backend_rsp_rdata;
    logic [2:0] backend_rsp_error;
    logic operator_result_valid;
    logic [2:0] operator_error_code;

    always_comb begin
        soft_reset_now = csr_valid && csr_ready && csr_write &&
                         (csr_addr == 8'h00) && csr_wdata[1];
        child_abort = hard_reset || backend_abort || soft_reset_now;

        layer33_start_valid = (backend_state == START_LAYER33);
        layer34_start_valid = (backend_state == START_LAYER34);
        layer33_completion_ready = (backend_state == RUN_LAYER33) &&
                                   (layer33_done || layer33_error);
        layer34_completion_ready = (backend_state == RUN_LAYER34) &&
                                   (layer34_done || layer34_error);

        operator_result_valid =
            ((backend_state == RUN_LAYER33) && layer33_error) ||
            ((backend_state == RUN_LAYER34) && (layer34_done || layer34_error));
        operator_error_code = 3'd0;
        if ((backend_state == RUN_LAYER33) && layer33_error) begin
            operator_error_code = layer33_error_code;
        end else if ((backend_state == RUN_LAYER34) && layer34_error) begin
            operator_error_code = layer34_error_code;
        end

        active_stage = 2'd0;
        if ((backend_state == START_LAYER33) ||
            (backend_state == RUN_LAYER33)) begin
            active_stage = 2'd1;
        end else if ((backend_state == START_LAYER34) ||
                     (backend_state == RUN_LAYER34)) begin
            active_stage = 2'd2;
        end

        backend_req_valid = 1'b0;
        backend_req_write = 1'b0;
        backend_req_addr = 32'd0;
        backend_req_wdata = 32'd0;
        backend_req_rstrb = 4'd0;
        backend_req_wstrb = 4'd0;
        layer33_req_ready = 1'b0;
        layer34_req_ready = 1'b0;
        layer33_rsp_valid = 1'b0;
        layer34_rsp_valid = 1'b0;
        layer33_rsp_rdata = 32'd0;
        layer34_rsp_rdata = 32'd0;
        layer33_rsp_error = 3'd0;
        layer34_rsp_error = 3'd0;
        if (backend_state == RUN_LAYER33) begin
            backend_req_valid = layer33_req_valid;
            backend_req_write = layer33_req_write;
            backend_req_addr = layer33_req_addr;
            backend_req_wdata = layer33_req_wdata;
            backend_req_rstrb = layer33_req_rstrb;
            backend_req_wstrb = layer33_req_wstrb;
            layer33_req_ready = backend_req_ready;
            layer33_rsp_valid = backend_rsp_valid;
            layer33_rsp_rdata = backend_rsp_rdata;
            layer33_rsp_error = backend_rsp_error;
        end else if (backend_state == RUN_LAYER34) begin
            backend_req_valid = layer34_req_valid;
            backend_req_write = layer34_req_write;
            backend_req_addr = layer34_req_addr;
            backend_req_wdata = layer34_req_wdata;
            backend_req_rstrb = layer34_req_rstrb;
            backend_req_wstrb = layer34_req_wstrb;
            layer34_req_ready = backend_req_ready;
            layer34_rsp_valid = backend_rsp_valid;
            layer34_rsp_rdata = backend_rsp_rdata;
            layer34_rsp_error = backend_rsp_error;
        end
    end

    s2a_runtime_shell u_runtime_shell (
        .clk(clk),
        .hard_reset(hard_reset),
        .csr_valid(csr_valid),
        .csr_ready(csr_ready),
        .csr_write(csr_write),
        .csr_addr(csr_addr),
        .csr_wdata(csr_wdata),
        .csr_rdata(csr_rdata),
        .backend_req_valid(backend_req_valid),
        .backend_req_ready(backend_req_ready),
        .backend_req_write(backend_req_write),
        .backend_req_addr(backend_req_addr),
        .backend_req_wdata(backend_req_wdata),
        .backend_req_rstrb(backend_req_rstrb),
        .backend_req_wstrb(backend_req_wstrb),
        .backend_rsp_valid(backend_rsp_valid),
        .backend_rsp_rdata(backend_rsp_rdata),
        .backend_rsp_error(backend_rsp_error),
        .operator_result_valid(operator_result_valid),
        .operator_error_code(operator_error_code),
        .backend_start(backend_start),
        .backend_abort(backend_abort),
        .busy(busy),
        .done(done),
        .error(error),
        .pl_owns_buffers(pl_owns_buffers),
        .head_output_valid(head_output_valid),
        .mem_valid(mem_valid),
        .mem_ready(mem_ready),
        .mem_write(mem_write),
        .mem_addr(mem_addr),
        .mem_wdata(mem_wdata),
        .mem_rstrb(mem_rstrb),
        .mem_wstrb(mem_wstrb),
        .mem_rdata(mem_rdata),
        .mem_error_code(mem_error_code)
    );

    s2a_upsample_layer_scheduler u_layer33 (
        .clk(clk),
        .hard_reset(hard_reset),
        .abort(child_abort),
        .start_valid(layer33_start_valid),
        .start_ready(layer33_start_ready),
        .completion_ready(layer33_completion_ready),
        .busy(layer33_busy),
        .done(layer33_done),
        .error(layer33_error),
        .error_code(layer33_error_code),
        .completed_elements(layer33_completed_elements),
        .backend_cancel(layer33_backend_cancel),
        .backend_req_valid(layer33_req_valid),
        .backend_req_ready(layer33_req_ready),
        .backend_req_write(layer33_req_write),
        .backend_req_addr(layer33_req_addr),
        .backend_req_wdata(layer33_req_wdata),
        .backend_req_rstrb(layer33_req_rstrb),
        .backend_req_wstrb(layer33_req_wstrb),
        .backend_rsp_valid(layer33_rsp_valid),
        .backend_rsp_rdata(layer33_rsp_rdata),
        .backend_rsp_error(layer33_rsp_error)
    );

    s2a_route_layer_scheduler u_layer34 (
        .clk(clk),
        .hard_reset(hard_reset),
        .abort(child_abort),
        .start_valid(layer34_start_valid),
        .start_ready(layer34_start_ready),
        .completion_ready(layer34_completion_ready),
        .busy(layer34_busy),
        .done(layer34_done),
        .error(layer34_error),
        .error_code(layer34_error_code),
        .completed_elements(layer34_completed_elements),
        .backend_cancel(layer34_backend_cancel),
        .backend_req_valid(layer34_req_valid),
        .backend_req_ready(layer34_req_ready),
        .backend_req_write(layer34_req_write),
        .backend_req_addr(layer34_req_addr),
        .backend_req_wdata(layer34_req_wdata),
        .backend_req_rstrb(layer34_req_rstrb),
        .backend_req_wstrb(layer34_req_wstrb),
        .backend_rsp_valid(layer34_rsp_valid),
        .backend_rsp_rdata(layer34_rsp_rdata),
        .backend_rsp_error(layer34_rsp_error)
    );

    always_ff @(posedge clk) begin
        if (hard_reset || backend_abort || soft_reset_now) begin
            backend_state <= BACKEND_IDLE;
        end else begin
            case (backend_state)
                BACKEND_IDLE: begin
                    if (backend_start) begin
                        backend_state <= START_LAYER33;
                    end
                end
                START_LAYER33: begin
                    if (layer33_start_ready) begin
                        backend_state <= RUN_LAYER33;
                    end
                end
                RUN_LAYER33: begin
                    if (layer33_error) begin
                        backend_state <= BACKEND_IDLE;
                    end else if (layer33_done) begin
                        backend_state <= START_LAYER34;
                    end
                end
                START_LAYER34: begin
                    if (layer34_start_ready) begin
                        backend_state <= RUN_LAYER34;
                    end
                end
                RUN_LAYER34: begin
                    if (layer34_error) begin
                        backend_state <= BACKEND_IDLE;
                    end else if (layer34_done) begin
                        backend_state <= BACKEND_IDLE;
                    end
                end
                default: begin
                    backend_state <= BACKEND_IDLE;
                end
            endcase
        end
    end
endmodule
