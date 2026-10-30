`timescale 1ns/1ps
// S2C候选：旧完成式word接口与原生bulk通道互斥共享HP0，统一汇总安全账本。
module s2c_hp0_bulk_adapter #(
    parameter bit ENABLE_BULK = 1'b0
) (
    input logic clk,
    input logic cold_reset,
    input logic run_enable,
    input logic cancel,
    input logic clear_safe,
    input logic [63:0] run_epoch,
    input logic mem_valid,
    input logic mem_write,
    input logic [31:0] mem_addr,
    input logic [31:0] mem_wdata,
    input logic [3:0] mem_rstrb,
    input logic [3:0] mem_wstrb,
    output logic mem_ready,
    output logic [31:0] mem_rdata,
    output logic [2:0] mem_error_code,
    output logic [5:0] m_axi_arid,
    output logic [5:0] m_axi_awid,
    output logic [5:0] m_axi_wid,
    output logic [31:0] m_axi_araddr,
    output logic [31:0] m_axi_awaddr,
    output logic [3:0] m_axi_arlen,
    output logic [3:0] m_axi_awlen,
    output logic [2:0] m_axi_arsize,
    output logic [2:0] m_axi_awsize,
    output logic [1:0] m_axi_arburst,
    output logic [1:0] m_axi_awburst,
    output logic [1:0] m_axi_arlock,
    output logic [1:0] m_axi_awlock,
    output logic [3:0] m_axi_arcache,
    output logic [3:0] m_axi_awcache,
    output logic [3:0] m_axi_arqos,
    output logic [3:0] m_axi_awqos,
    output logic [2:0] m_axi_arprot,
    output logic [2:0] m_axi_awprot,
    output logic m_axi_arvalid,
    output logic m_axi_awvalid,
    output logic m_axi_wvalid,
    output logic m_axi_wlast,
    input logic m_axi_arready,
    input logic m_axi_awready,
    input logic m_axi_wready,
    output logic [63:0] m_axi_wdata,
    output logic [7:0] m_axi_wstrb,
    input logic [5:0] m_axi_rid,
    input logic [5:0] m_axi_bid,
    input logic [63:0] m_axi_rdata,
    input logic [1:0] m_axi_rresp,
    input logic [1:0] m_axi_bresp,
    input logic m_axi_rlast,
    input logic m_axi_rvalid,
    input logic m_axi_bvalid,
    output logic m_axi_rready,
    output logic m_axi_bready,
    output logic ledger_empty,
    output logic [63:0] ledger_epoch,
    output logic recovery_required,
    output logic protocol_isolated,
    output logic first_fault_valid,
    output logic [7:0] first_fault_code,
    output logic [31:0] first_fault_address,
    output logic fault_event_valid,
    output logic [7:0] fault_event_code,
    output logic [31:0] fault_event_address,
    output logic req_withdrawn,
    output logic clear_rejected,
    output logic [9:0] axi_progress,
    output logic [9:0] axi_progress_next,
    output logic ledger_empty_next,
    output logic [1:0] fault_event_resp,
    output logic fault_event_write,
    output logic fault_event_protocol,
    output logic fault_event_address_valid,
    output logic [31:0] fault_event_physical_address,
    input logic bulk_cmd_valid,
    output logic bulk_cmd_ready,
    input logic bulk_cmd_write,
    input logic [31:0] bulk_cmd_addr,
    input logic [7:0] bulk_cmd_bytes,
    input logic bulk_wvalid,
    output logic bulk_wready,
    input logic [7:0] bulk_wdata,
    output logic bulk_rvalid,
    input logic bulk_rready,
    output logic [7:0] bulk_rdata,
    output logic bulk_done_valid,
    input logic bulk_done_ready,
    output logic [2:0] bulk_done_error
);
    logic legacy_mem_ready;
    logic native_mem_ready;
    logic [31:0] legacy_mem_rdata;
    logic [31:0] native_mem_rdata;
    logic [2:0] legacy_mem_error_code;
    logic [2:0] native_mem_error_code;
    logic [5:0] legacy_m_axi_arid;
    logic [5:0] native_m_axi_arid;
    logic [5:0] legacy_m_axi_awid;
    logic [5:0] native_m_axi_awid;
    logic [5:0] legacy_m_axi_wid;
    logic [5:0] native_m_axi_wid;
    logic [31:0] legacy_m_axi_araddr;
    logic [31:0] native_m_axi_araddr;
    logic [31:0] legacy_m_axi_awaddr;
    logic [31:0] native_m_axi_awaddr;
    logic [3:0] legacy_m_axi_arlen;
    logic [3:0] native_m_axi_arlen;
    logic [3:0] legacy_m_axi_awlen;
    logic [3:0] native_m_axi_awlen;
    logic [2:0] legacy_m_axi_arsize;
    logic [2:0] native_m_axi_arsize;
    logic [2:0] legacy_m_axi_awsize;
    logic [2:0] native_m_axi_awsize;
    logic [1:0] legacy_m_axi_arburst;
    logic [1:0] native_m_axi_arburst;
    logic [1:0] legacy_m_axi_awburst;
    logic [1:0] native_m_axi_awburst;
    logic [1:0] legacy_m_axi_arlock;
    logic [1:0] native_m_axi_arlock;
    logic [1:0] legacy_m_axi_awlock;
    logic [1:0] native_m_axi_awlock;
    logic [3:0] legacy_m_axi_arcache;
    logic [3:0] native_m_axi_arcache;
    logic [3:0] legacy_m_axi_awcache;
    logic [3:0] native_m_axi_awcache;
    logic [3:0] legacy_m_axi_arqos;
    logic [3:0] native_m_axi_arqos;
    logic [3:0] legacy_m_axi_awqos;
    logic [3:0] native_m_axi_awqos;
    logic [2:0] legacy_m_axi_arprot;
    logic [2:0] native_m_axi_arprot;
    logic [2:0] legacy_m_axi_awprot;
    logic [2:0] native_m_axi_awprot;
    logic legacy_m_axi_arvalid;
    logic native_m_axi_arvalid;
    logic legacy_m_axi_awvalid;
    logic native_m_axi_awvalid;
    logic legacy_m_axi_wvalid;
    logic native_m_axi_wvalid;
    logic legacy_m_axi_wlast;
    logic native_m_axi_wlast;
    logic [63:0] legacy_m_axi_wdata;
    logic [63:0] native_m_axi_wdata;
    logic [7:0] legacy_m_axi_wstrb;
    logic [7:0] native_m_axi_wstrb;
    logic legacy_m_axi_rready;
    logic native_m_axi_rready;
    logic legacy_m_axi_bready;
    logic native_m_axi_bready;
    logic legacy_ledger_empty;
    logic native_ledger_empty;
    logic [63:0] legacy_ledger_epoch;
    logic [63:0] native_ledger_epoch;
    logic legacy_recovery_required;
    logic native_recovery_required;
    logic legacy_protocol_isolated;
    logic native_protocol_isolated;
    logic legacy_first_fault_valid;
    logic native_first_fault_valid;
    logic [7:0] legacy_first_fault_code;
    logic [7:0] native_first_fault_code;
    logic [31:0] legacy_first_fault_address;
    logic [31:0] native_first_fault_address;
    logic legacy_fault_event_valid;
    logic native_fault_event_valid;
    logic [7:0] legacy_fault_event_code;
    logic [7:0] native_fault_event_code;
    logic [31:0] legacy_fault_event_address;
    logic [31:0] native_fault_event_address;
    logic legacy_req_withdrawn;
    logic legacy_clear_rejected;
    logic native_clear_rejected;
    logic [9:0] legacy_axi_progress;
    logic [9:0] native_axi_progress;
    logic [9:0] legacy_axi_progress_next;
    logic [9:0] native_axi_progress_next;
    logic legacy_ledger_empty_next;
    logic native_ledger_empty_next;
    logic [1:0] legacy_fault_event_resp;
    logic [1:0] native_fault_event_resp;
    logic legacy_fault_event_write;
    logic native_fault_event_write;
    logic legacy_fault_event_protocol;
    logic native_fault_event_protocol;
    logic legacy_fault_event_address_valid;
    logic native_fault_event_address_valid;
    logic [31:0] legacy_fault_event_physical_address;
    logic [31:0] native_fault_event_physical_address;
    logic native_bulk_cmd_ready;
    logic native_bulk_wready;
    logic native_bulk_rvalid;
    logic [7:0] native_bulk_rdata;
    logic native_bulk_done_valid;
    logic [2:0] native_bulk_done_error;
    logic bulk_owner;
    logic native_grant, native_run_enable, accepted_clear, clear_permitted;
    logic choose_native_fault;
    // 只有两个子账本都没有遗留物理或逻辑职责时，才能报告空。
    assign ledger_empty = legacy_ledger_empty && native_ledger_empty;
    assign ledger_empty_next = legacy_ledger_empty_next && native_ledger_empty_next;
    assign ledger_epoch = bulk_owner ? native_ledger_epoch : legacy_ledger_epoch;
    assign recovery_required = legacy_recovery_required || native_recovery_required;
    assign protocol_isolated = legacy_protocol_isolated || native_protocol_isolated;
    assign axi_progress = legacy_axi_progress | native_axi_progress;
    assign axi_progress_next = legacy_axi_progress_next | native_axi_progress_next;
    assign req_withdrawn = legacy_req_withdrawn;
    // 同沿故障不能再接受新的bulk命令；旧请求有优先权。
    assign native_grant = ENABLE_BULK && !mem_valid && legacy_ledger_empty &&
        !legacy_recovery_required && !legacy_protocol_isolated &&
        !legacy_fault_event_valid && !native_fault_event_valid;
    assign native_run_enable = run_enable && (bulk_owner || native_grant);
    assign bulk_cmd_ready = native_grant && native_bulk_cmd_ready;
    assign bulk_wready = bulk_owner && native_bulk_wready;
    assign bulk_rvalid = bulk_owner && native_bulk_rvalid;
    assign bulk_rdata = native_bulk_rdata;
    assign bulk_done_valid = bulk_owner && native_bulk_done_valid;
    assign bulk_done_error = native_bulk_done_error;
    assign mem_ready = !bulk_owner && legacy_mem_ready;
    assign mem_rdata = legacy_mem_rdata;
    assign mem_error_code = legacy_mem_error_code;
    assign choose_native_fault = native_fault_event_valid &&
        (!legacy_fault_event_valid || (native_fault_event_protocol && !legacy_fault_event_protocol));
    assign fault_event_valid = legacy_fault_event_valid || native_fault_event_valid;
    assign fault_event_code = choose_native_fault ? native_fault_event_code : legacy_fault_event_code;
    assign fault_event_address = choose_native_fault ? native_fault_event_address : legacy_fault_event_address;
    assign fault_event_resp = choose_native_fault ? native_fault_event_resp : legacy_fault_event_resp;
    assign fault_event_write = choose_native_fault ? native_fault_event_write : legacy_fault_event_write;
    assign fault_event_protocol = choose_native_fault ? native_fault_event_protocol : legacy_fault_event_protocol;
    assign fault_event_address_valid = choose_native_fault ? native_fault_event_address_valid : legacy_fault_event_address_valid;
    assign fault_event_physical_address = choose_native_fault ? native_fault_event_physical_address : legacy_fault_event_physical_address;
    assign clear_permitted = !run_enable && ledger_empty && !protocol_isolated &&
        !cancel && !fault_event_valid;
    assign accepted_clear = clear_safe && clear_permitted;
    assign clear_rejected = clear_safe && !clear_permitted;

    // owner只在无遗留事务时切换，未接受的AXI VALID绝不能随owner切换而撤回。
    always_ff @(posedge clk) begin
        if (cold_reset) begin
            bulk_owner <= 1'b0;
            first_fault_valid <= 1'b0;
            first_fault_code <= 8'd0;
            first_fault_address <= 32'd0;
        end else begin
            if (bulk_cmd_valid && bulk_cmd_ready)
                bulk_owner <= 1'b1;
            else if (bulk_owner && native_ledger_empty)
                bulk_owner <= 1'b0;
            if (accepted_clear) begin
                first_fault_valid <= 1'b0;
                first_fault_code <= 8'd0;
                first_fault_address <= 32'd0;
            end else if (!first_fault_valid) begin
                if (legacy_first_fault_valid) begin
                    first_fault_valid <= 1'b1;
                    first_fault_code <= legacy_first_fault_code;
                    first_fault_address <= legacy_first_fault_address;
                end else if (native_first_fault_valid) begin
                    first_fault_valid <= 1'b1;
                    first_fault_code <= native_first_fault_code;
                    first_fault_address <= native_first_fault_address;
                end else if (fault_event_valid) begin
                    first_fault_valid <= 1'b1;
                    first_fault_code <= fault_event_code;
                    first_fault_address <= fault_event_address;
                end
            end
        end
    end

    assign m_axi_arid = bulk_owner ? native_m_axi_arid : legacy_m_axi_arid;
    assign m_axi_awid = bulk_owner ? native_m_axi_awid : legacy_m_axi_awid;
    assign m_axi_wid = bulk_owner ? native_m_axi_wid : legacy_m_axi_wid;
    assign m_axi_araddr = bulk_owner ? native_m_axi_araddr : legacy_m_axi_araddr;
    assign m_axi_awaddr = bulk_owner ? native_m_axi_awaddr : legacy_m_axi_awaddr;
    assign m_axi_arlen = bulk_owner ? native_m_axi_arlen : legacy_m_axi_arlen;
    assign m_axi_awlen = bulk_owner ? native_m_axi_awlen : legacy_m_axi_awlen;
    assign m_axi_arsize = bulk_owner ? native_m_axi_arsize : legacy_m_axi_arsize;
    assign m_axi_awsize = bulk_owner ? native_m_axi_awsize : legacy_m_axi_awsize;
    assign m_axi_arburst = bulk_owner ? native_m_axi_arburst : legacy_m_axi_arburst;
    assign m_axi_awburst = bulk_owner ? native_m_axi_awburst : legacy_m_axi_awburst;
    assign m_axi_arlock = bulk_owner ? native_m_axi_arlock : legacy_m_axi_arlock;
    assign m_axi_awlock = bulk_owner ? native_m_axi_awlock : legacy_m_axi_awlock;
    assign m_axi_arcache = bulk_owner ? native_m_axi_arcache : legacy_m_axi_arcache;
    assign m_axi_awcache = bulk_owner ? native_m_axi_awcache : legacy_m_axi_awcache;
    assign m_axi_arqos = bulk_owner ? native_m_axi_arqos : legacy_m_axi_arqos;
    assign m_axi_awqos = bulk_owner ? native_m_axi_awqos : legacy_m_axi_awqos;
    assign m_axi_arprot = bulk_owner ? native_m_axi_arprot : legacy_m_axi_arprot;
    assign m_axi_awprot = bulk_owner ? native_m_axi_awprot : legacy_m_axi_awprot;
    assign m_axi_arvalid = bulk_owner ? native_m_axi_arvalid : legacy_m_axi_arvalid;
    assign m_axi_awvalid = bulk_owner ? native_m_axi_awvalid : legacy_m_axi_awvalid;
    assign m_axi_wvalid = bulk_owner ? native_m_axi_wvalid : legacy_m_axi_wvalid;
    assign m_axi_wlast = bulk_owner ? native_m_axi_wlast : legacy_m_axi_wlast;
    assign m_axi_wdata = bulk_owner ? native_m_axi_wdata : legacy_m_axi_wdata;
    assign m_axi_wstrb = bulk_owner ? native_m_axi_wstrb : legacy_m_axi_wstrb;
    assign m_axi_rready = bulk_owner ? native_m_axi_rready : legacy_m_axi_rready;
    assign m_axi_bready = bulk_owner ? native_m_axi_bready : legacy_m_axi_bready;
    s2b_hp0_word_adapter legacy_adapter (
        .clk(clk),
        .cold_reset(cold_reset),
        .run_enable((run_enable && !bulk_owner && !native_recovery_required && !native_protocol_isolated)),
        .cancel(cancel),
        .clear_safe(accepted_clear),
        .run_epoch(run_epoch),
        .mem_valid((mem_valid && !bulk_owner)),
        .mem_write(mem_write),
        .mem_addr(mem_addr),
        .mem_wdata(mem_wdata),
        .mem_rstrb(mem_rstrb),
        .mem_wstrb(mem_wstrb),
        .mem_ready(legacy_mem_ready),
        .mem_rdata(legacy_mem_rdata),
        .mem_error_code(legacy_mem_error_code),
        .m_axi_arid(legacy_m_axi_arid),
        .m_axi_awid(legacy_m_axi_awid),
        .m_axi_wid(legacy_m_axi_wid),
        .m_axi_araddr(legacy_m_axi_araddr),
        .m_axi_awaddr(legacy_m_axi_awaddr),
        .m_axi_arlen(legacy_m_axi_arlen),
        .m_axi_awlen(legacy_m_axi_awlen),
        .m_axi_arsize(legacy_m_axi_arsize),
        .m_axi_awsize(legacy_m_axi_awsize),
        .m_axi_arburst(legacy_m_axi_arburst),
        .m_axi_awburst(legacy_m_axi_awburst),
        .m_axi_arlock(legacy_m_axi_arlock),
        .m_axi_awlock(legacy_m_axi_awlock),
        .m_axi_arcache(legacy_m_axi_arcache),
        .m_axi_awcache(legacy_m_axi_awcache),
        .m_axi_arqos(legacy_m_axi_arqos),
        .m_axi_awqos(legacy_m_axi_awqos),
        .m_axi_arprot(legacy_m_axi_arprot),
        .m_axi_awprot(legacy_m_axi_awprot),
        .m_axi_arvalid(legacy_m_axi_arvalid),
        .m_axi_awvalid(legacy_m_axi_awvalid),
        .m_axi_wvalid(legacy_m_axi_wvalid),
        .m_axi_wlast(legacy_m_axi_wlast),
        .m_axi_arready((!bulk_owner && m_axi_arready)),
        .m_axi_awready((!bulk_owner && m_axi_awready)),
        .m_axi_wready((!bulk_owner && m_axi_wready)),
        .m_axi_wdata(legacy_m_axi_wdata),
        .m_axi_wstrb(legacy_m_axi_wstrb),
        .m_axi_rid(m_axi_rid),
        .m_axi_bid(m_axi_bid),
        .m_axi_rdata(m_axi_rdata),
        .m_axi_rresp(m_axi_rresp),
        .m_axi_bresp(m_axi_bresp),
        .m_axi_rlast(m_axi_rlast),
        .m_axi_rvalid((!bulk_owner && m_axi_rvalid)),
        .m_axi_bvalid((!bulk_owner && m_axi_bvalid)),
        .m_axi_rready(legacy_m_axi_rready),
        .m_axi_bready(legacy_m_axi_bready),
        .ledger_empty(legacy_ledger_empty),
        .ledger_epoch(legacy_ledger_epoch),
        .recovery_required(legacy_recovery_required),
        .protocol_isolated(legacy_protocol_isolated),
        .first_fault_valid(legacy_first_fault_valid),
        .first_fault_code(legacy_first_fault_code),
        .first_fault_address(legacy_first_fault_address),
        .fault_event_valid(legacy_fault_event_valid),
        .fault_event_code(legacy_fault_event_code),
        .fault_event_address(legacy_fault_event_address),
        .req_withdrawn(legacy_req_withdrawn),
        .clear_rejected(legacy_clear_rejected),
        .axi_progress(legacy_axi_progress),
        .axi_progress_next(legacy_axi_progress_next),
        .ledger_empty_next(legacy_ledger_empty_next),
        .fault_event_resp(legacy_fault_event_resp),
        .fault_event_write(legacy_fault_event_write),
        .fault_event_protocol(legacy_fault_event_protocol),
        .fault_event_address_valid(legacy_fault_event_address_valid),
        .fault_event_physical_address(legacy_fault_event_physical_address)
    );
    s2c_axi3_bulk_bridge #(.ENABLE_BULK(ENABLE_BULK)) bulk_bridge (
        .clk(clk),
        .cold_reset(cold_reset),
        .run_enable(native_run_enable),
        .cancel(cancel),
        .clear_safe(accepted_clear),
        .run_epoch(run_epoch),
        .m_axi_arid(native_m_axi_arid),
        .m_axi_awid(native_m_axi_awid),
        .m_axi_wid(native_m_axi_wid),
        .m_axi_araddr(native_m_axi_araddr),
        .m_axi_awaddr(native_m_axi_awaddr),
        .m_axi_arlen(native_m_axi_arlen),
        .m_axi_awlen(native_m_axi_awlen),
        .m_axi_arsize(native_m_axi_arsize),
        .m_axi_awsize(native_m_axi_awsize),
        .m_axi_arburst(native_m_axi_arburst),
        .m_axi_awburst(native_m_axi_awburst),
        .m_axi_arlock(native_m_axi_arlock),
        .m_axi_awlock(native_m_axi_awlock),
        .m_axi_arcache(native_m_axi_arcache),
        .m_axi_awcache(native_m_axi_awcache),
        .m_axi_arqos(native_m_axi_arqos),
        .m_axi_awqos(native_m_axi_awqos),
        .m_axi_arprot(native_m_axi_arprot),
        .m_axi_awprot(native_m_axi_awprot),
        .m_axi_arvalid(native_m_axi_arvalid),
        .m_axi_awvalid(native_m_axi_awvalid),
        .m_axi_wvalid(native_m_axi_wvalid),
        .m_axi_wlast(native_m_axi_wlast),
        .m_axi_arready((bulk_owner && m_axi_arready)),
        .m_axi_awready((bulk_owner && m_axi_awready)),
        .m_axi_wready((bulk_owner && m_axi_wready)),
        .m_axi_wdata(native_m_axi_wdata),
        .m_axi_wstrb(native_m_axi_wstrb),
        .m_axi_rid(m_axi_rid),
        .m_axi_bid(m_axi_bid),
        .m_axi_rdata(m_axi_rdata),
        .m_axi_rresp(m_axi_rresp),
        .m_axi_bresp(m_axi_bresp),
        .m_axi_rlast(m_axi_rlast),
        .m_axi_rvalid((bulk_owner && m_axi_rvalid)),
        .m_axi_bvalid((bulk_owner && m_axi_bvalid)),
        .m_axi_rready(native_m_axi_rready),
        .m_axi_bready(native_m_axi_bready),
        .ledger_empty(native_ledger_empty),
        .ledger_epoch(native_ledger_epoch),
        .recovery_required(native_recovery_required),
        .protocol_isolated(native_protocol_isolated),
        .first_fault_valid(native_first_fault_valid),
        .first_fault_code(native_first_fault_code),
        .first_fault_address(native_first_fault_address),
        .fault_event_valid(native_fault_event_valid),
        .fault_event_code(native_fault_event_code),
        .fault_event_address(native_fault_event_address),
        .clear_rejected(native_clear_rejected),
        .axi_progress(native_axi_progress),
        .axi_progress_next(native_axi_progress_next),
        .ledger_empty_next(native_ledger_empty_next),
        .fault_event_resp(native_fault_event_resp),
        .fault_event_write(native_fault_event_write),
        .fault_event_protocol(native_fault_event_protocol),
        .fault_event_address_valid(native_fault_event_address_valid),
        .fault_event_physical_address(native_fault_event_physical_address),
        .bulk_cmd_valid((bulk_cmd_valid && native_grant)),
        .bulk_cmd_ready(native_bulk_cmd_ready),
        .bulk_cmd_write(bulk_cmd_write),
        .bulk_cmd_addr(bulk_cmd_addr),
        .bulk_cmd_bytes(bulk_cmd_bytes),
        .bulk_wvalid((bulk_owner && bulk_wvalid)),
        .bulk_wready(native_bulk_wready),
        .bulk_wdata(bulk_wdata),
        .bulk_rvalid(native_bulk_rvalid),
        .bulk_rready((bulk_owner && bulk_rready)),
        .bulk_rdata(native_bulk_rdata),
        .bulk_done_valid(native_bulk_done_valid),
        .bulk_done_ready((bulk_owner && bulk_done_ready)),
        .bulk_done_error(native_bulk_done_error)
    );
endmodule
