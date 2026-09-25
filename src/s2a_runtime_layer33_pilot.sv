// S2A-T27：将 G0 runtime shell 串接到固定 tiny416 layer33 调度器。
module s2a_runtime_layer33_pilot (
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

    output logic        child_busy,
    output logic        child_done,
    output logic        child_error,
    output logic [2:0]  child_error_code,
    output logic [16:0] child_completed_elements,

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

    logic soft_reset_now;
    logic child_abort;
    logic child_backend_cancel;
    logic operator_result_valid;
    logic [2:0] operator_error_code;
    logic start_ready_unused;

    always_comb begin
        soft_reset_now = csr_valid && csr_ready && csr_write &&
                         (csr_addr == 8'h00) && csr_wdata[1];
        child_abort = hard_reset || backend_abort || soft_reset_now;
        operator_result_valid = child_done || child_error;
        operator_error_code = child_error ? child_error_code : 3'd0;
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
        .start_valid(backend_start),
        .start_ready(start_ready_unused),
        .completion_ready(operator_result_valid),
        .busy(child_busy),
        .done(child_done),
        .error(child_error),
        .error_code(child_error_code),
        .completed_elements(child_completed_elements),
        .backend_cancel(child_backend_cancel),
        .backend_req_valid(backend_req_valid),
        .backend_req_ready(backend_req_ready),
        .backend_req_write(backend_req_write),
        .backend_req_addr(backend_req_addr),
        .backend_req_wdata(backend_req_wdata),
        .backend_req_rstrb(backend_req_rstrb),
        .backend_req_wstrb(backend_req_wstrb),
        .backend_rsp_valid(backend_rsp_valid),
        .backend_rsp_rdata(backend_rsp_rdata),
        .backend_rsp_error(backend_rsp_error)
    );

endmodule
