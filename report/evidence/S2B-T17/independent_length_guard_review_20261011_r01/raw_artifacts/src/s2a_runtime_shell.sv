// S2A-T12：组合冻结 CSR、单 outstanding master 与 G0 memory bus。
module s2a_runtime_shell (
    input  logic        clk,
    input  logic        hard_reset,

    input  logic        csr_valid,
    output logic        csr_ready,
    input  logic        csr_write,
    input  logic [7:0]  csr_addr,
    input  logic [31:0] csr_wdata,
    output logic [31:0] csr_rdata,

    input  logic        backend_req_valid,
    output logic        backend_req_ready,
    input  logic        backend_req_write,
    input  logic [31:0] backend_req_addr,
    input  logic [31:0] backend_req_wdata,
    input  logic [3:0]  backend_req_rstrb,
    input  logic [3:0]  backend_req_wstrb,
    output logic        backend_rsp_valid,
    output logic [31:0] backend_rsp_rdata,
    output logic [2:0]  backend_rsp_error,

    input  logic        operator_result_valid,
    input  logic [2:0]  operator_error_code,
    output logic        backend_start,
    output logic        backend_abort,
    output logic        busy,
    output logic        done,
    output logic        error,
    output logic        pl_owns_buffers,
    output logic        head_output_valid,

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
    logic backend_memory_error_valid;
    logic [2:0] backend_memory_error_code;
    logic soft_reset_now;
    logic cancel_master;

    always_comb begin
        soft_reset_now = csr_valid && csr_ready && csr_write &&
                         (csr_addr == 8'h00) && csr_wdata[1];
        cancel_master = hard_reset || backend_abort || soft_reset_now;
        backend_memory_error_valid = backend_rsp_valid &&
                                     (backend_rsp_error != 3'd0);
        backend_memory_error_code = backend_rsp_error;
    end

    s2a_control_csr u_control (
        .clk(clk),
        .hard_reset(hard_reset),
        .csr_valid(csr_valid),
        .csr_ready(csr_ready),
        .csr_write(csr_write),
        .csr_addr(csr_addr),
        .csr_wdata(csr_wdata),
        .csr_rdata(csr_rdata),
        .backend_memory_error_valid(backend_memory_error_valid),
        .backend_memory_error_code(backend_memory_error_code),
        .operator_result_valid(operator_result_valid),
        .operator_error_code(operator_error_code),
        .backend_start(backend_start),
        .backend_abort(backend_abort),
        .busy(busy),
        .done(done),
        .error(error),
        .pl_owns_buffers(pl_owns_buffers),
        .head_output_valid(head_output_valid)
    );

    s2a_memory_master u_memory_master (
        .clk(clk),
        .hard_reset(hard_reset),
        .cancel(cancel_master),
        .buffer_owner_pl(pl_owns_buffers),
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
endmodule
