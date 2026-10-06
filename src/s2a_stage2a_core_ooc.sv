// S2A OOC 顶层：将冻结 CSR/memory master 与 tiny416 网络后端组合。
module s2a_stage2a_core_ooc #(
    // 默认值逐项绑定 S2A-T01 冻结清单 address_map.input.address/length_bytes。
    // 权威文件：report/evidence/S2A-T01/tiny416_model_manifest.json。
    // 该清单 SHA-256：9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a。
    parameter logic [31:0] INPUT_BASE_ADDRESS = 32'h00000000,
    parameter logic [31:0] INPUT_LENGTH_BYTES = 32'd519168,
    // 默认值逐项绑定同一冻结清单 address_map.weight_package.address/length_bytes。
    parameter logic [31:0] WEIGHT_PACKAGE_BASE_ADDRESS = 32'h00100000,
    parameter logic [31:0] WEIGHT_PACKAGE_LENGTH_BYTES = 32'd5903100
) (
    input  logic        clk,
    input  logic        hard_reset,

    input  logic        csr_valid,
    output logic        csr_ready,
    input  logic        csr_write,
    input  logic [7:0]  csr_addr,
    input  logic [31:0] csr_wdata,
    output logic [31:0] csr_rdata,

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

    logic backend_mem_valid;
    logic backend_mem_write;
    logic [31:0] backend_mem_addr;
    logic [31:0] backend_mem_wdata;
    logic [3:0] backend_mem_rstrb;
    logic [3:0] backend_mem_wstrb;

    logic backend_start;
    logic backend_abort;
    logic buffer_owner_pl;
    logic busy;
    logic done;
    logic error;
    logic head_output_valid;
    logic operator_result_valid;
    logic [2:0] operator_error_code;
    // shell 已按同一响应错误码上报 memory error；后端诊断口仅保留内部观察，不外露为顶层引脚。
    logic backend_memory_error_valid;
    logic [2:0] backend_memory_error_code;

    // 直接请求保持有效至外部 memory 返回，runtime shell 锁存单笔请求并产生完成响应。
    // 因此后端的 ready/data/error 接收端使用 shell 的响应通道，而非请求入队 ready。
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
        .pl_owns_buffers(buffer_owner_pl),
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

    // 后端请求经 shell 的单 outstanding master 发往顶层 memory 总线。
    // shell 的 backend_req_ready 仅负责入队；后端事务在 backend_rsp_valid 时完成。
    assign backend_req_valid = backend_mem_valid;
    assign backend_req_write = backend_mem_write;
    assign backend_req_addr = backend_mem_addr;
    assign backend_req_wdata = backend_mem_wdata;
    assign backend_req_rstrb = backend_mem_rstrb;
    assign backend_req_wstrb = backend_mem_wstrb;

    s2a_network_backend u_network_backend (
        .clk(clk),
        .hard_reset(hard_reset),
        .abort(backend_abort),
        .backend_start(backend_start),
        .buffer_owner_pl(buffer_owner_pl),
        .input_base_address(INPUT_BASE_ADDRESS),
        .input_length_bytes(INPUT_LENGTH_BYTES),
        .weight_package_base_address(WEIGHT_PACKAGE_BASE_ADDRESS),
        .weight_package_length_bytes(WEIGHT_PACKAGE_LENGTH_BYTES),
        .mem_valid(backend_mem_valid),
        .mem_write(backend_mem_write),
        .mem_addr(backend_mem_addr),
        .mem_wdata(backend_mem_wdata),
        .mem_rstrb(backend_mem_rstrb),
        .mem_wstrb(backend_mem_wstrb),
        .mem_ready(backend_rsp_valid),
        .mem_rdata(backend_rsp_rdata),
        .mem_error_code(backend_rsp_error),
        .backend_memory_error_valid(backend_memory_error_valid),
        .backend_memory_error_code(backend_memory_error_code),
        .operator_result_valid(operator_result_valid),
        .operator_error_code(operator_error_code)
    );
endmodule
