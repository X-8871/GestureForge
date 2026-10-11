// S2A-T12：单 outstanding 请求锁存与 G0 memory bus 握手。
module s2a_memory_master (
    input  logic        clk,
    input  logic        hard_reset,
    input  logic        cancel,
    input  logic        buffer_owner_pl,

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
    logic pending;
    logic held_write;
    logic [31:0] held_addr;
    logic [31:0] held_wdata;
    logic [3:0] held_rstrb;
    logic [3:0] held_wstrb;

    always_comb begin
        backend_req_ready = !pending && buffer_owner_pl && !hard_reset && !cancel;
        mem_valid = pending && buffer_owner_pl && !hard_reset && !cancel;
        mem_write = held_write;
        mem_addr = held_addr;
        mem_wdata = held_wdata;
        mem_rstrb = held_rstrb;
        mem_wstrb = held_wstrb;
        backend_rsp_valid = mem_valid && mem_ready;
        backend_rsp_rdata = backend_rsp_valid ? mem_rdata : 32'd0;
        backend_rsp_error = backend_rsp_valid ? mem_error_code : 3'd0;
    end

    always_ff @(posedge clk) begin
        if (hard_reset || cancel || !buffer_owner_pl) begin
            pending <= 1'b0;
            held_write <= 1'b0;
            held_addr <= 32'd0;
            held_wdata <= 32'd0;
            held_rstrb <= 4'd0;
            held_wstrb <= 4'd0;
        end else if (pending && mem_valid && mem_ready) begin
            pending <= 1'b0;
        end else if (!pending && backend_req_valid && backend_req_ready) begin
            pending <= 1'b1;
            held_write <= backend_req_write;
            held_addr <= backend_req_addr;
            held_wdata <= backend_req_wdata;
            held_rstrb <= backend_req_rstrb;
            held_wstrb <= backend_req_wstrb;
        end
    end
endmodule
