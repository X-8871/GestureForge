`timescale 1ns/1ps
// 候选 HP0 AXI3 单 word 桥；只有统一冷初始化可以丢弃物理账本。
module s2b_hp0_word_adapter (
    input logic clk, cold_reset, run_enable, cancel, clear_safe,
    input logic [63:0] run_epoch,
    input logic mem_valid, mem_write,
    input logic [31:0] mem_addr, mem_wdata,
    input logic [3:0] mem_rstrb, mem_wstrb,
    output logic mem_ready,
    output logic [31:0] mem_rdata,
    output logic [2:0] mem_error_code,
    output logic [5:0] m_axi_arid, m_axi_awid, m_axi_wid,
    output logic [31:0] m_axi_araddr, m_axi_awaddr,
    output logic [3:0] m_axi_arlen, m_axi_awlen,
    output logic [2:0] m_axi_arsize, m_axi_awsize,
    output logic [1:0] m_axi_arburst, m_axi_awburst, m_axi_arlock, m_axi_awlock,
    output logic [3:0] m_axi_arcache, m_axi_awcache, m_axi_arqos, m_axi_awqos,
    output logic [2:0] m_axi_arprot, m_axi_awprot,
    output logic m_axi_arvalid, m_axi_awvalid, m_axi_wvalid, m_axi_wlast,
    input logic m_axi_arready, m_axi_awready, m_axi_wready,
    output logic [63:0] m_axi_wdata,
    output logic [7:0] m_axi_wstrb,
    input logic [5:0] m_axi_rid, m_axi_bid,
    input logic [63:0] m_axi_rdata,
    input logic [1:0] m_axi_rresp, m_axi_bresp,
    input logic m_axi_rlast, m_axi_rvalid, m_axi_bvalid,
    output logic m_axi_rready, m_axi_bready,
    output logic ledger_empty,
    output logic [63:0] ledger_epoch,
    output logic recovery_required, protocol_isolated,
    output logic first_fault_valid,
    output logic [7:0] first_fault_code,
    output logic [31:0] first_fault_address,
    output logic fault_event_valid,
    output logic [7:0] fault_event_code,
    output logic [31:0] fault_event_address,
    output logic req_withdrawn, clear_rejected
);
    typedef struct packed {
        logic held, response_pending, bad_response;
        logic write_req;
        logic [31:0] addr, physical_addr, data;
        logic [3:0] rmask, wmask, remaining;
        logic [63:0] epoch;
        logic [31:0] assembled;
        logic [2:0] logical_error;
        logic read_active, arvalid, ar_accepted;
        logic [31:0] araddr;
        logic [2:0] arsize;
        logic [1:0] lane;
        logic write_active, awvalid, wvalid, aw_accepted, w_accepted, b_seen;
        logic [1:0] saved_bresp;
        logic recover, isolated, first_valid;
        logic [7:0] first_code;
        logic [31:0] first_address;
    } ledger_t;
    ledger_t q, d;
    logic guard_allowed;
    logic [31:0] guard_address;
    logic [2:0] guard_error;
    logic payload_equal, live_request, capture_request;
    logic r_match, b_match, r_protocol, b_protocol, logical_protocol;
    logic stop_request, event_is_protocol;
    logic [1:0] next_lane;
    logic [3:0] remaining_after;
    logic [31:0] shifted_read;

    s2b_request_guard guard (
        .mem_write(mem_write), .mem_addr(mem_addr), .mem_rstrb(mem_rstrb),
        .mem_wstrb(mem_wstrb), .request_allowed(guard_allowed),
        .physical_addr(guard_address), .error_code(guard_error)
    );

    function automatic logic [1:0] lowest_lane(input logic [2:0] low_mask);
        // 完整mask非零；低三lane都未选中时，只可能选择lane3。
        lowest_lane = 2'd3;
        if (low_mask[0]) lowest_lane = 2'd0;
        else if (low_mask[1]) lowest_lane = 2'd1;
        else if (low_mask[2]) lowest_lane = 2'd2;
    endfunction

    assign payload_equal = {mem_write, mem_addr, mem_wdata, mem_rstrb, mem_wstrb} ==
                           {q.write_req, q.addr, q.data, q.rmask, q.wmask};
    assign live_request = q.held && mem_valid && payload_equal &&
                          (run_epoch == q.epoch) && run_enable && !cancel;
    assign ledger_empty = !(q.held || q.response_pending || q.read_active || q.arvalid ||
                            q.ar_accepted || q.write_active || q.awvalid || q.wvalid ||
                            q.aw_accepted || q.w_accepted || q.b_seen);
    assign ledger_epoch = q.epoch;
    assign recovery_required = q.recover;
    assign protocol_isolated = q.isolated;
    assign first_fault_valid = q.first_valid;
    assign first_fault_code = q.first_code;
    assign first_fault_address = q.first_address;
    assign req_withdrawn = q.held && !mem_valid;
    assign capture_request = ledger_empty && run_enable && mem_valid && !cancel &&
                             !q.recover && !q.isolated;

    // 匹配依赖此前沿的接受状态；非法响应被消费但不能证明原等待结束。
    assign r_match = q.read_active && q.ar_accepted && (m_axi_rid == 6'd0) && m_axi_rlast;
    assign b_match = q.write_active && q.w_accepted && !q.b_seen && (m_axi_bid == 6'd0);
    assign r_protocol = m_axi_rvalid && (!r_match || (m_axi_rresp == 2'b01));
    assign b_protocol = m_axi_bvalid && (!b_match || (m_axi_bresp == 2'b01));
    assign logical_protocol = q.held && ((mem_valid && !payload_equal) || (run_epoch != q.epoch));
    assign stop_request = cancel || (q.held && (!run_enable || !mem_valid)) ||
                          logical_protocol || fault_event_valid || q.recover || q.isolated;

    // 当前沿事件供外层首错聚合；协议故障优先于普通响应错误，读错优先写错。
    always_comb begin
        fault_event_valid = 1'b0;
        fault_event_code = 8'd0;
        fault_event_address = 32'd0;
        event_is_protocol = 1'b0;
        if (r_protocol || b_protocol) begin
            fault_event_valid = 1'b1;
            fault_event_code = 8'd11;
            fault_event_address = ledger_empty ? 32'd0 : q.addr;
            event_is_protocol = 1'b1;
        end else if (logical_protocol) begin
            fault_event_valid = 1'b1;
            fault_event_code = 8'd6;
            fault_event_address = q.addr;
            event_is_protocol = 1'b1;
        end else if (m_axi_rvalid && r_match && m_axi_rresp[1]) begin
            fault_event_valid = 1'b1;
            fault_event_code = m_axi_rresp[0] ? 8'd10 : 8'd9;
            fault_event_address = q.addr;
        end else if (m_axi_bvalid && b_match && m_axi_bresp[1]) begin
            fault_event_valid = 1'b1;
            fault_event_code = m_axi_bresp[0] ? 8'd10 : 8'd9;
            fault_event_address = q.addr;
        end
    end

    // 错误准入响应只返回 2A 的 1/2；AXI 的 9/10/11 从不截断交给 core。
    assign mem_ready = q.response_pending && live_request && !q.isolated &&
                       !fault_event_valid && !q.recover;
    assign mem_rdata = q.assembled;
    assign mem_error_code = q.logical_error;
    assign m_axi_arid = 6'd0;
    assign m_axi_awid = 6'd0;
    assign m_axi_wid = 6'd0;
    assign m_axi_araddr = q.araddr;
    assign m_axi_awaddr = q.physical_addr;
    assign m_axi_arlen = 4'd0;
    assign m_axi_awlen = 4'd0;
    assign m_axi_arsize = q.arsize;
    assign m_axi_awsize = 3'd2;
    assign m_axi_arburst = 2'b01;
    assign m_axi_awburst = 2'b01;
    assign m_axi_arlock = 2'b00;
    assign m_axi_awlock = 2'b00;
    assign m_axi_arcache = 4'd0;
    assign m_axi_awcache = 4'd0;
    assign m_axi_arprot = 3'd0;
    assign m_axi_awprot = 3'd0;
    assign m_axi_arqos = 4'd0;
    assign m_axi_awqos = 4'd0;
    assign m_axi_arvalid = q.arvalid;
    assign m_axi_awvalid = q.awvalid;
    assign m_axi_wvalid = q.wvalid;
    assign m_axi_wlast = 1'b1;
    assign m_axi_wdata = q.addr[2] ? {q.data, 32'd0} : {32'd0, q.data};
    assign m_axi_wstrb = q.addr[2] ? {q.wmask, 4'd0} : {4'd0, q.wmask};
    assign m_axi_rready = 1'b1;
    assign m_axi_bready = 1'b1;

    always_comb begin
        d = q;
        clear_rejected = clear_safe &&
            (run_enable || !ledger_empty || q.isolated || cancel || fault_event_valid);
        next_lane = lowest_lane(q.remaining[2:0]);
        remaining_after = q.remaining & ~(4'b0001 << q.lane);
        shifted_read = 32'(m_axi_rdata >> (8 * q.araddr[2:0]));

        // 已声明握手始终入账，取消不能屏蔽同沿接受，也不能撤销 VALID。
        if (q.arvalid && m_axi_arready) begin
            d.arvalid = 1'b0;
            d.ar_accepted = 1'b1;
        end
        if (q.awvalid && m_axi_awready) begin
            d.awvalid = 1'b0;
            d.aw_accepted = 1'b1;
        end
        if (q.wvalid && m_axi_wready) begin
            d.wvalid = 1'b0;
            d.w_accepted = 1'b1;
        end
        if (m_axi_rvalid && r_match) begin
            d.read_active = 1'b0;
            d.ar_accepted = 1'b0;
            if (!stop_request) begin
                if (q.arsize == 3'd2) begin
                    d.assembled = shifted_read[31:0];
                    d.remaining = 4'd0;
                    d.response_pending = 1'b1;
                end else begin
                    d.assembled[8*q.lane +: 8] = shifted_read[7:0];
                    d.remaining = remaining_after;
                    if (remaining_after == 4'd0) d.response_pending = 1'b1;
                end
            end
        end
        if (m_axi_bvalid && b_match) begin
            d.b_seen = 1'b1;
            d.saved_bresp = m_axi_bresp;
        end
        // AXI3 允许先 B 后 AW；只在 AW/W/B 三项全部完成时闭合。
        if (q.write_active && d.aw_accepted && d.w_accepted && d.b_seen) begin
            d.write_active = 1'b0;
            d.aw_accepted = 1'b0;
            d.w_accepted = 1'b0;
            d.b_seen = 1'b0;
            if (!stop_request && (d.saved_bresp == 2'b00)) d.response_pending = 1'b1;
        end

        if (mem_ready) begin
            d.held = 1'b0;
            d.response_pending = 1'b0;
            d.bad_response = 1'b0;
            // 准入错误先由 core 实际接受，再关闭此 epoch 的后续准入。
            if (q.bad_response) begin
                d.recover = 1'b1;
                if (!q.first_valid) begin
                    d.first_valid = 1'b1;
                    d.first_code = {5'd0, q.logical_error};
                    d.first_address = q.addr;
                end
            end
        end
        if (stop_request && (cancel || q.held || fault_event_valid)) begin
            d.held = 1'b0;
            d.response_pending = 1'b0;
            d.bad_response = 1'b0;
            d.remaining = 4'd0;
            d.recover = 1'b1;
        end
        if (fault_event_valid) begin
            d.recover = 1'b1;
            if (event_is_protocol) d.isolated = 1'b1;
            if (!q.first_valid) begin
                d.first_valid = 1'b1;
                d.first_code = fault_event_code;
                d.first_address = fault_event_address;
            end
        end
        if (clear_safe && !clear_rejected) begin
            d.recover = 1'b0;
            d.first_valid = 1'b0;
            d.first_code = 8'd0;
            d.first_address = 32'd0;
        end
        if (capture_request && !r_protocol && !b_protocol) begin
            d.held = 1'b1;
            d.write_req = mem_write;
            d.addr = mem_addr;
            // 只捕获guard完成33-bit溢出、窗口和对象核验后的物理地址。
            d.physical_addr = guard_address;
            d.data = mem_wdata;
            d.rmask = mem_rstrb;
            d.wmask = mem_wstrb;
            d.epoch = run_epoch;
            d.assembled = 32'd0;
            d.logical_error = guard_error;
            d.remaining = mem_rstrb;
            if (!guard_allowed) begin
                d.response_pending = 1'b1;
                d.bad_response = 1'b1;
            end
        end
        // 首次声明仅使用已锁存且再次核对的请求，不在捕获沿发 VALID。
        if (q.held && !q.response_pending && !q.read_active && !q.write_active &&
            live_request && !stop_request) begin
            if (q.write_req) begin
                d.write_active = 1'b1;
                d.awvalid = 1'b1;
                d.wvalid = 1'b1;
            end else begin
                d.read_active = 1'b1;
                d.arvalid = 1'b1;
                // guard已证明4B对齐；byte lane替换低两位，无重复平移或截位加法。
                d.araddr = {q.physical_addr[31:2],
                    ((q.rmask == 4'b1111) ? 2'd0 : next_lane)};
                d.arsize = (q.rmask == 4'b1111) ? 3'd2 : 3'd0;
                d.lane = next_lane;
            end
        end
    end

    always_ff @(posedge clk) begin
        if (cold_reset) q <= '0;
        else q <= d;
    end
endmodule
