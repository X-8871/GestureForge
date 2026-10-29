`timescale 1ns/1ps
// 2B 全核心集成层：仅连接冻结公共 CSR/memory 接口，不读取核心内部状态。
module s2b_inference_top #(
    // 只有独立审阅且与实际网表、源码和缓存证据绑定的构建可改为 1。
    parameter bit PROFILE_VISIBILITY_PROVEN = 1'b0,
    parameter integer CONV_OUTPUT_LANES = 8,
    parameter bit ENABLE_BULK = 1'b0
) (
    (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 clk CLK",
       X_INTERFACE_PARAMETER = "XIL_INTERFACENAME clk, ASSOCIATED_BUSIF S_AXI:M_AXI, ASSOCIATED_RESET cold_resetn, FREQ_HZ 100000000" *)
    input logic clk,
    (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 cold_resetn RST",
       X_INTERFACE_PARAMETER = "XIL_INTERFACENAME cold_resetn, POLARITY ACTIVE_LOW" *)
    input logic cold_resetn,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI AWADDR" *)
    (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME S_AXI, PROTOCOL AXI4LITE, ADDR_WIDTH 32, DATA_WIDTH 32, READ_WRITE_MODE READ_WRITE, HAS_PROT 1, HAS_WSTRB 1, FREQ_HZ 100000000" *)
    input logic [31:0] s_axi_awaddr,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI AWPROT" *)
    input logic [2:0] s_axi_awprot,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI AWVALID" *)
    input logic s_axi_awvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI AWREADY" *)
    output logic s_axi_awready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI WDATA" *)
    input logic [31:0] s_axi_wdata,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI WSTRB" *)
    input logic [3:0] s_axi_wstrb,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI WVALID" *)
    input logic s_axi_wvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI WREADY" *)
    output logic s_axi_wready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI BRESP" *)
    output logic [1:0] s_axi_bresp,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI BVALID" *)
    output logic s_axi_bvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI BREADY" *)
    input logic s_axi_bready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI ARADDR" *)
    input logic [31:0] s_axi_araddr,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI ARPROT" *)
    input logic [2:0] s_axi_arprot,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI ARVALID" *)
    input logic s_axi_arvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI ARREADY" *)
    output logic s_axi_arready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI RDATA" *)
    output logic [31:0] s_axi_rdata,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI RRESP" *)
    output logic [1:0] s_axi_rresp,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI RVALID" *)
    output logic s_axi_rvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI RREADY" *)
    input logic s_axi_rready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI AWID" *)
    (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME M_AXI, PROTOCOL AXI3, ADDR_WIDTH 32, DATA_WIDTH 64, ID_WIDTH 6, HAS_BURST 1, HAS_LOCK 1, HAS_CACHE 1, HAS_PROT 1, HAS_QOS 1, NUM_READ_OUTSTANDING 1, NUM_WRITE_OUTSTANDING 1, FREQ_HZ 100000000" *)
    output logic [5:0] m_axi_awid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI AWADDR" *)
    output logic [31:0] m_axi_awaddr,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI AWLEN" *)
    output logic [3:0] m_axi_awlen,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI AWSIZE" *)
    output logic [2:0] m_axi_awsize,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI AWBURST" *)
    output logic [1:0] m_axi_awburst,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI AWLOCK" *)
    output logic [1:0] m_axi_awlock,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI AWCACHE" *)
    output logic [3:0] m_axi_awcache,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI AWPROT" *)
    output logic [2:0] m_axi_awprot,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI AWQOS" *)
    output logic [3:0] m_axi_awqos,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI AWVALID" *)
    output logic m_axi_awvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI ARID" *)
    output logic [5:0] m_axi_arid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI ARADDR" *)
    output logic [31:0] m_axi_araddr,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI ARLEN" *)
    output logic [3:0] m_axi_arlen,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI ARSIZE" *)
    output logic [2:0] m_axi_arsize,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI ARBURST" *)
    output logic [1:0] m_axi_arburst,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI ARLOCK" *)
    output logic [1:0] m_axi_arlock,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI ARCACHE" *)
    output logic [3:0] m_axi_arcache,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI ARPROT" *)
    output logic [2:0] m_axi_arprot,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI ARQOS" *)
    output logic [3:0] m_axi_arqos,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI ARVALID" *)
    output logic m_axi_arvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI AWREADY" *)
    input logic m_axi_awready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI ARREADY" *)
    input logic m_axi_arready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI WID" *)
    output logic [5:0] m_axi_wid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI WDATA" *)
    output logic [63:0] m_axi_wdata,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI WSTRB" *)
    output logic [7:0] m_axi_wstrb,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI WLAST" *)
    output logic m_axi_wlast,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI WVALID" *)
    output logic m_axi_wvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI WREADY" *)
    input logic m_axi_wready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI BID" *)
    input logic [5:0] m_axi_bid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI BRESP" *)
    input logic [1:0] m_axi_bresp,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI BVALID" *)
    input logic m_axi_bvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI BREADY" *)
    output logic m_axi_bready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI RID" *)
    input logic [5:0] m_axi_rid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI RDATA" *)
    input logic [63:0] m_axi_rdata,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI RRESP" *)
    input logic [1:0] m_axi_rresp,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI RLAST" *)
    input logic m_axi_rlast,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI RVALID" *)
    input logic m_axi_rvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI RREADY" *)
    output logic m_axi_rready
);
    logic cold_reset;
    logic core_csr_valid, core_csr_ready, core_csr_write;
    logic [7:0] core_csr_addr;
    logic [31:0] core_csr_wdata, core_csr_rdata;
    logic mem_valid, mem_ready, mem_write;
    logic [31:0] mem_addr, mem_wdata, mem_rdata;
    logic [3:0] mem_rstrb, mem_wstrb;
    logic [2:0] mem_error_code;
    logic bulk_cmd_valid;
    logic bulk_cmd_ready;
    logic bulk_cmd_write;
    logic [31:0] bulk_cmd_addr;
    logic [7:0] bulk_cmd_bytes;
    logic bulk_wvalid;
    logic bulk_wready;
    logic [7:0] bulk_wdata;
    logic bulk_rvalid;
    logic bulk_rready;
    logic [7:0] bulk_rdata;
    logic bulk_done_valid;
    logic bulk_done_ready;
    logic [2:0] bulk_done_error;
    logic run_enable, cancel, clear_safe;
    logic [63:0] run_epoch, ledger_epoch;
    logic ledger_empty, ledger_empty_next, req_withdrawn, protocol_isolated;
    logic [9:0] axi_progress_next;
    logic fault_event_valid, fault_event_write, fault_event_protocol, fault_event_address_valid;
    logic [7:0] fault_event_code;
    logic [31:0] fault_event_address, fault_event_physical_address;
    logic [1:0] fault_event_resp;
    logic [5:0] unused_axi_prot;
    logic [9:0] unused_axi_progress;
    logic unused_recovery_required, unused_first_fault_valid, unused_clear_rejected;
    logic [7:0] unused_first_fault_code;
    logic [31:0] unused_first_fault_address;

    // 该输入只允许统一 PS/DDR/PL 冷初始化；运行中不得单独断言以丢弃账本。
    assign cold_reset = !cold_resetn;
    // PROT 和旧诊断保留公开口/实现兼容，当前控制层不消费它们。
    assign unused_axi_prot = {s_axi_awprot, s_axi_arprot};

    s2b_stage2b_core #(
        .CONV_OUTPUT_LANES(CONV_OUTPUT_LANES), .ENABLE_BULK(ENABLE_BULK)
    ) core (
        .bulk_cmd_valid(bulk_cmd_valid),
        .bulk_cmd_ready(bulk_cmd_ready),
        .bulk_cmd_write(bulk_cmd_write),
        .bulk_cmd_addr(bulk_cmd_addr),
        .bulk_cmd_bytes(bulk_cmd_bytes),
        .bulk_wvalid(bulk_wvalid),
        .bulk_wready(bulk_wready),
        .bulk_wdata(bulk_wdata),
        .bulk_rvalid(bulk_rvalid),
        .bulk_rready(bulk_rready),
        .bulk_rdata(bulk_rdata),
        .bulk_done_valid(bulk_done_valid),
        .bulk_done_ready(bulk_done_ready),
        .bulk_done_error(bulk_done_error),
        .clk(clk), .hard_reset(cold_reset),
        .csr_valid(core_csr_valid), .csr_ready(core_csr_ready),
        .csr_write(core_csr_write), .csr_addr(core_csr_addr),
        .csr_wdata(core_csr_wdata), .csr_rdata(core_csr_rdata),
        .mem_valid(mem_valid), .mem_ready(mem_ready), .mem_write(mem_write),
        .mem_addr(mem_addr), .mem_wdata(mem_wdata), .mem_rstrb(mem_rstrb),
        .mem_wstrb(mem_wstrb), .mem_rdata(mem_rdata), .mem_error_code(mem_error_code)
    );

    // AWPROT/ARPROT 仅随 AXI4-Lite 接口保留；地址、WSTRB 和准入语义由控制器校验。
    s2b_control_csr control (
        .clk(clk), .cold_reset(cold_reset),
        .s_axi_awaddr(s_axi_awaddr),
        .s_axi_awvalid(s_axi_awvalid),
        .s_axi_awready(s_axi_awready),
        .s_axi_wdata(s_axi_wdata),
        .s_axi_wstrb(s_axi_wstrb),
        .s_axi_wvalid(s_axi_wvalid),
        .s_axi_wready(s_axi_wready),
        .s_axi_bresp(s_axi_bresp),
        .s_axi_bvalid(s_axi_bvalid),
        .s_axi_bready(s_axi_bready),
        .s_axi_araddr(s_axi_araddr),
        .s_axi_arvalid(s_axi_arvalid),
        .s_axi_arready(s_axi_arready),
        .s_axi_rdata(s_axi_rdata),
        .s_axi_rresp(s_axi_rresp),
        .s_axi_rvalid(s_axi_rvalid),
        .s_axi_rready(s_axi_rready),
        .core_csr_valid(core_csr_valid), .core_csr_ready(core_csr_ready),
        .core_csr_write(core_csr_write), .core_csr_addr(core_csr_addr),
        .core_csr_wdata(core_csr_wdata), .core_csr_rdata(core_csr_rdata),
        .core_mem_valid(mem_valid || (ENABLE_BULK && bulk_cmd_valid)),
        .ledger_empty(ledger_empty), .ledger_epoch(ledger_epoch),
        .axi_progress_next(axi_progress_next),
        .ledger_empty_next(ledger_empty_next), .req_withdrawn(req_withdrawn),
        .protocol_isolated(protocol_isolated), .fault_event_valid(fault_event_valid),
        .fault_event_code(fault_event_code), .fault_event_address(fault_event_address),
        .fault_event_physical_address(fault_event_physical_address),
        .fault_event_resp(fault_event_resp), .fault_event_write(fault_event_write),
        .fault_event_protocol(fault_event_protocol),
        .fault_event_address_valid(fault_event_address_valid),
        .visibility_confirmed(PROFILE_VISIBILITY_PROVEN),
        .run_enable(run_enable), .cancel(cancel), .clear_safe(clear_safe), .run_epoch(run_epoch)
    );

    // 新旧事务物理互斥，合并全部bulk责任后才向原控制层报告SAFE。
    s2c_hp0_bulk_adapter #(.ENABLE_BULK(ENABLE_BULK)) adapter (
        .bulk_cmd_valid(bulk_cmd_valid),
        .bulk_cmd_ready(bulk_cmd_ready),
        .bulk_cmd_write(bulk_cmd_write),
        .bulk_cmd_addr(bulk_cmd_addr),
        .bulk_cmd_bytes(bulk_cmd_bytes),
        .bulk_wvalid(bulk_wvalid),
        .bulk_wready(bulk_wready),
        .bulk_wdata(bulk_wdata),
        .bulk_rvalid(bulk_rvalid),
        .bulk_rready(bulk_rready),
        .bulk_rdata(bulk_rdata),
        .bulk_done_valid(bulk_done_valid),
        .bulk_done_ready(bulk_done_ready),
        .bulk_done_error(bulk_done_error),
        .clk(clk), .cold_reset(cold_reset), .run_enable(run_enable),
        .cancel(cancel), .clear_safe(clear_safe), .run_epoch(run_epoch),
        .mem_valid(mem_valid), .mem_ready(mem_ready), .mem_write(mem_write),
        .mem_addr(mem_addr), .mem_wdata(mem_wdata), .mem_rstrb(mem_rstrb),
        .mem_wstrb(mem_wstrb), .mem_rdata(mem_rdata), .mem_error_code(mem_error_code),
        .m_axi_awid(m_axi_awid),
        .m_axi_awaddr(m_axi_awaddr),
        .m_axi_awlen(m_axi_awlen),
        .m_axi_awsize(m_axi_awsize),
        .m_axi_awburst(m_axi_awburst),
        .m_axi_awlock(m_axi_awlock),
        .m_axi_awcache(m_axi_awcache),
        .m_axi_awprot(m_axi_awprot),
        .m_axi_awqos(m_axi_awqos),
        .m_axi_awvalid(m_axi_awvalid),
        .m_axi_arid(m_axi_arid),
        .m_axi_araddr(m_axi_araddr),
        .m_axi_arlen(m_axi_arlen),
        .m_axi_arsize(m_axi_arsize),
        .m_axi_arburst(m_axi_arburst),
        .m_axi_arlock(m_axi_arlock),
        .m_axi_arcache(m_axi_arcache),
        .m_axi_arprot(m_axi_arprot),
        .m_axi_arqos(m_axi_arqos),
        .m_axi_arvalid(m_axi_arvalid),
        .m_axi_awready(m_axi_awready),
        .m_axi_arready(m_axi_arready),
        .m_axi_wid(m_axi_wid),
        .m_axi_wdata(m_axi_wdata),
        .m_axi_wstrb(m_axi_wstrb),
        .m_axi_wlast(m_axi_wlast),
        .m_axi_wvalid(m_axi_wvalid),
        .m_axi_wready(m_axi_wready),
        .m_axi_bid(m_axi_bid),
        .m_axi_bresp(m_axi_bresp),
        .m_axi_bvalid(m_axi_bvalid),
        .m_axi_bready(m_axi_bready),
        .m_axi_rid(m_axi_rid),
        .m_axi_rdata(m_axi_rdata),
        .m_axi_rresp(m_axi_rresp),
        .m_axi_rlast(m_axi_rlast),
        .m_axi_rvalid(m_axi_rvalid),
        .m_axi_rready(m_axi_rready),
        .ledger_empty(ledger_empty), .ledger_epoch(ledger_epoch),
        .protocol_isolated(protocol_isolated), .req_withdrawn(req_withdrawn),
        .axi_progress(unused_axi_progress), .axi_progress_next(axi_progress_next),
        .ledger_empty_next(ledger_empty_next), .fault_event_valid(fault_event_valid),
        .fault_event_code(fault_event_code), .fault_event_address(fault_event_address),
        .fault_event_physical_address(fault_event_physical_address),
        .fault_event_resp(fault_event_resp), .fault_event_write(fault_event_write),
        .fault_event_protocol(fault_event_protocol),
        .fault_event_address_valid(fault_event_address_valid),
        .recovery_required(unused_recovery_required), .first_fault_valid(unused_first_fault_valid),
        .first_fault_code(unused_first_fault_code), .first_fault_address(unused_first_fault_address),
        .clear_rejected(unused_clear_rejected)
    );
endmodule

