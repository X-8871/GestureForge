`timescale 1ns/1ps
module tb_s2b_inference_top_recovery;
    localparam logic [31:0] CORE_TIMEOUT_CYCLES = 32'd10000;
    localparam logic [31:0] DRAIN_TIMEOUT_CYCLES = 32'd32;

    logic clk = 1'b0;
    logic cold_resetn = 1'b0;

    logic [31:0] s_axi_awaddr = 0;
    logic s_axi_awvalid = 0;
    logic s_axi_awready;
    logic [31:0] s_axi_wdata = 0;
    logic [3:0] s_axi_wstrb = 4'hf;
    logic s_axi_wvalid = 0;
    logic s_axi_wready;
    logic [1:0] s_axi_bresp;
    logic s_axi_bvalid;
    logic s_axi_bready = 0;
    logic [31:0] s_axi_araddr = 0;
    logic s_axi_arvalid = 0;
    logic s_axi_arready;
    logic [31:0] s_axi_rdata;
    logic [1:0] s_axi_rresp;
    logic s_axi_rvalid;
    logic s_axi_rready = 0;

    logic m_axi_arready = 0;
    logic [5:0] m_axi_arid;
    logic [31:0] m_axi_araddr;
    logic [3:0] m_axi_arlen;
    logic [2:0] m_axi_arsize;
    logic [1:0] m_axi_arburst;
    logic m_axi_arvalid;
    logic m_axi_awvalid;
    logic m_axi_wvalid;
    logic m_axi_rready;
    logic [5:0] m_axi_rid = 0;
    logic [63:0] m_axi_rdata = 64'h0000000000000000;
    logic [1:0] m_axi_rresp = 0;
    logic m_axi_rlast = 1;
    logic m_axi_rvalid = 0;

    integer cycles = 0;
    integer ar_handshakes = 0;
    integer r_handshakes = 0;
    integer core_start_handshakes = 0;
    integer core_start_cycle = -1;
    integer soft_reset_handshakes = 0;
    integer soft_reset_cycle = -1;
    integer stop_status_observations = 0;
    integer stop_confirmed_cycle = -1;
    integer recovery_seen_cycle = -1;
    integer isolated_seen_cycle = -1;
    logic stop_s2_observed = 1'b0;
    logic [31:0] first_ar_address = 0;

    always #5 clk = ~clk;

    // 被動觀察集成後內層CSR的真實握手，不驅動DUT私有狀態。
    always @(posedge clk) begin
        if (!cold_resetn) begin
            cycles = 0;
        end else begin
            cycles = cycles + 1;
            if (m_axi_arvalid && m_axi_arready) begin
                ar_handshakes = ar_handshakes + 1;
                first_ar_address = m_axi_araddr;
                $display("OBS HP0_AR cycle=%0d address=%08x len=%0d size=%0d", cycles,
                         m_axi_araddr, m_axi_arlen, m_axi_arsize);
            end
            if (m_axi_rvalid && m_axi_rready) begin
                r_handshakes = r_handshakes + 1;
                $display("OBS HP0_R cycle=%0d resp=%0b last=%0b", cycles, m_axi_rresp, m_axi_rlast);
            end
            if (dut.core_csr_valid && dut.core_csr_ready && dut.core_csr_write &&
                dut.core_csr_addr == 8'h00 && dut.core_csr_wdata == 32'd1) begin
                core_start_handshakes = core_start_handshakes + 1;
                core_start_cycle = cycles;
                $display("OBS CORE_START cycle=%0d", cycles);
            end
            if (dut.core_csr_valid && dut.core_csr_ready && dut.core_csr_write &&
                dut.core_csr_addr == 8'h00 && dut.core_csr_wdata == 32'd2) begin
                soft_reset_handshakes = soft_reset_handshakes + 1;
                soft_reset_cycle = cycles;
                $display("OBS SOFT_RESET_S cycle=%0d", cycles);
            end
            if (soft_reset_handshakes != 0 && dut.core_csr_valid && dut.core_csr_ready &&
                !dut.core_csr_write && dut.core_csr_addr == 8'h04 &&
                dut.core_csr_rdata[3:0] == 4'b0000 && !dut.mem_valid) begin
                stop_status_observations = stop_status_observations + 1;
                if ((cycles - soft_reset_cycle) >= 2 && !stop_s2_observed) begin
                    stop_s2_observed = 1'b1;
                    stop_confirmed_cycle = cycles;
                    $display("OBS STOP_S2 cycle=%0d delta=%0d", cycles, cycles-soft_reset_cycle);
                end
            end
        end
    end

    s2b_inference_top #(
        // 仿真中顯式假設已證明可見性，以覆蓋安全歸還路徑；不代表硬件證明。
        .PROFILE_VISIBILITY_PROVEN(1'b1)
    ) dut (
        .clk(clk),
        .cold_resetn(cold_resetn),
        .s_axi_awaddr(s_axi_awaddr),
        .s_axi_awprot(3'b000),
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
        .s_axi_arprot(3'b000),
        .s_axi_arvalid(s_axi_arvalid),
        .s_axi_arready(s_axi_arready),
        .s_axi_rdata(s_axi_rdata),
        .s_axi_rresp(s_axi_rresp),
        .s_axi_rvalid(s_axi_rvalid),
        .s_axi_rready(s_axi_rready),
        .m_axi_awid(), .m_axi_awaddr(), .m_axi_awlen(), .m_axi_awsize(),
        .m_axi_awburst(), .m_axi_awlock(), .m_axi_awcache(), .m_axi_awprot(), .m_axi_awqos(),
        .m_axi_awvalid(m_axi_awvalid),
        .m_axi_arid(m_axi_arid), .m_axi_araddr(m_axi_araddr), .m_axi_arlen(m_axi_arlen),
        .m_axi_arsize(m_axi_arsize), .m_axi_arburst(m_axi_arburst), .m_axi_arlock(),
        .m_axi_arcache(), .m_axi_arprot(), .m_axi_arqos(), .m_axi_arvalid(m_axi_arvalid),
        .m_axi_awready(1'b0), .m_axi_arready(m_axi_arready),
        .m_axi_wid(), .m_axi_wdata(), .m_axi_wstrb(), .m_axi_wlast(), .m_axi_wvalid(m_axi_wvalid),
        .m_axi_wready(1'b0), .m_axi_bid(6'd0), .m_axi_bresp(2'b00), .m_axi_bvalid(1'b0),
        .m_axi_bready(), .m_axi_rid(m_axi_rid), .m_axi_rdata(m_axi_rdata),
        .m_axi_rresp(m_axi_rresp), .m_axi_rlast(m_axi_rlast), .m_axi_rvalid(m_axi_rvalid),
        .m_axi_rready(m_axi_rready)
    );

    task automatic check(input logic condition, input string message);
        if (condition !== 1'b1) $fatal(1, "cycle=%0d %s", cycles, message);
    endtask

    task automatic csr_write(input logic [31:0] address, input logic [31:0] value);
        logic aw_done;
        logic w_done;
        begin
            @(negedge clk);
            s_axi_awaddr = address;
            s_axi_wdata = value;
            s_axi_awvalid = 1'b1;
            s_axi_wvalid = 1'b1;
            aw_done = 1'b0;
            w_done = 1'b0;
            while (!aw_done || !w_done) begin
                @(posedge clk);
                if (!aw_done && s_axi_awready) aw_done = 1'b1;
                if (!w_done && s_axi_wready) w_done = 1'b1;
                @(negedge clk);
                if (aw_done) s_axi_awvalid = 1'b0;
                if (w_done) s_axi_wvalid = 1'b0;
            end
            while (!s_axi_bvalid) @(negedge clk);
            check(s_axi_bresp == 2'b00, "CSR寫入未返回OKAY");
            s_axi_bready = 1'b1;
            @(posedge clk);
            @(negedge clk);
            s_axi_bready = 1'b0;
        end
    endtask

    task automatic csr_read(input logic [31:0] address, output logic [31:0] value);
        begin
            @(negedge clk);
            s_axi_araddr = address;
            s_axi_arvalid = 1'b1;
            do @(posedge clk); while (!s_axi_arready);
            @(negedge clk);
            s_axi_arvalid = 1'b0;
            while (!s_axi_rvalid) @(negedge clk);
            check(s_axi_rresp == 2'b00, "CSR讀取未返回OKAY");
            value = s_axi_rdata;
            s_axi_rready = 1'b1;
            @(posedge clk);
            @(negedge clk);
            s_axi_rready = 1'b0;
        end
    endtask

    task automatic wait_for_terminal(output logic [31:0] status_value);
        integer attempt;
        logic [31:0] sample;
        begin
            status_value = 0;
            sample = 0;
            attempt = 0;
            while (attempt < 80 && sample[2:0] != 3'd5) begin
                csr_read(32'h43c0000c, sample);
                attempt = attempt + 1;
            end
            status_value = sample;
            check(sample[2:0] == 3'd5, "恢復未到ERROR_SAFE終態");
        end
    endtask

    logic [31:0] value;
    logic [31:0] status_value;
    logic [31:0] fault_logical;
    logic [31:0] fault_physical;
    logic [31:0] fault_detail;
    integer wait_cycles;
    integer cycles_since_start;
    logic recovering_seen;
    logic isolated_seen;

    initial begin
        $display("PROFILE_VISIBILITY_PROVEN=1 SIMULATION_ASSUMPTION_ONLY");
        repeat (5) @(posedge clk);
        @(negedge clk);
        cold_resetn = 1'b1;
        repeat (5) @(posedge clk);

        csr_read(32'h43c00000, value);
        check(value == 32'h53324250, "物理CSR簽名錯誤");
        csr_write(32'h43c00014, 32'd42);
        csr_write(32'h43c00018, 32'h00000000);
        csr_write(32'h43c0001c, 32'd519168);
        csr_write(32'h43c00020, 32'h00100000);
        csr_write(32'h43c00024, 32'd5903100);
        csr_write(32'h43c00028, CORE_TIMEOUT_CYCLES);
        csr_write(32'h43c0002c, DRAIN_TIMEOUT_CYCLES);
        csr_write(32'h43c00008, 32'd1);

        wait_cycles = 0;
        while (!m_axi_arvalid && wait_cycles < 2000) begin
            @(negedge clk);
            wait_cycles = wait_cycles + 1;
        end
        check(m_axi_arvalid, "真實network backend未產生第一筆HP0讀請求");
        check(core_start_handshakes == 1, "未觀察到內層CSR接受START");
        check(!m_axi_awvalid && !m_axi_wvalid, "首筆backend請求不是只讀請求");
        check(m_axi_arid == 0 && m_axi_arlen == 0 && m_axi_arburst == 2'b01,
              "第一筆HP0請求不符合單拍AXI3契約");
        check(m_axi_arsize == 0 || m_axi_arsize == 2, "第一筆HP0請求ARSIZE非法");
        check(m_axi_araddr >= 32'h10000000 && m_axi_araddr < 32'h12000000,
              "第一筆backend請求不在DDR arena內");
        first_ar_address = m_axi_araddr;

        repeat (3) begin
            @(posedge clk);
            check(m_axi_arvalid && m_axi_araddr == first_ar_address && !m_axi_arready,
                  "ARREADY停頓期間請求未保持穩定");
        end
        @(negedge clk);
        m_axi_arready = 1'b1;
        @(posedge clk);
        check(m_axi_arvalid && m_axi_araddr == first_ar_address, "AR握手沿請求改變");
        @(negedge clk);
        m_axi_arready = 1'b0;

        repeat (6) @(posedge clk);
        check(!m_axi_arvalid, "一筆未完成時backend又聲明新的AR");
        check(m_axi_rready, "adapter未保持R通道接收能力");

        // 保持已接受的HP0讀無響應，等內核自身超时进入恢复，再等外层排空期限。
        cycles_since_start = cycles - core_start_cycle;
        check(cycles_since_start < CORE_TIMEOUT_CYCLES - 8,
              "首笔backend AR发出前内核已越过timeout观察点");
        repeat (CORE_TIMEOUT_CYCLES - 8 - cycles_since_start) @(posedge clk);

        recovering_seen = 1'b0;
        isolated_seen = 1'b0;
        wait_cycles = 0;
        while (!isolated_seen && wait_cycles < 32) begin
            csr_read(32'h43c0000c, status_value);
            if (status_value[2:0] == 3'd3 && !recovering_seen) begin
                recovering_seen = 1'b1;
                recovery_seen_cycle = cycles;
                $display("OBS RECOVERING cycle=%0d status=%08x", cycles, status_value);
            end
            if (status_value[2:0] == 3'd6) begin
                isolated_seen = 1'b1;
                isolated_seen_cycle = cycles;
                $display("OBS FAULT_ISOLATED cycle=%0d status=%08x", cycles, status_value);
            end
            wait_cycles = wait_cycles + 1;
        end
        check(recovering_seen, "未通过公开PHYS_STATUS观察RECOVERING");
        check(isolated_seen, "超时排空后未到FAULT_ISOLATED");
        check(isolated_seen_cycle > recovery_seen_cycle,
              "FAULT_ISOLATED未发生在RECOVERING之后");
        check(status_value[8] && !status_value[9] && !status_value[10] &&
              !status_value[11] && status_value[12],
              "FAULT_ISOLATED未保持PL所有权、HEAD_INVALID或pending ledger");
        check(ar_handshakes == 1 && r_handshakes == 0,
              "发送晚响应前AXI事务数或ledger状态错误");
        csr_read(32'h43c00010, value);
        check(value == 32'd5, "超时恢复的首错未传播为CORE_TIMEOUT");

        // 返回与此前AR同ID、同拍数且RLAST有效的迟到OKAY，验证只排空旧账本。
        @(negedge clk);
        m_axi_rid = 0;
        m_axi_rresp = 2'b00;
        m_axi_rlast = 1'b1;
        m_axi_rdata = 64'h6b5a4938271605f4;
        m_axi_rvalid = 1'b1;
        @(posedge clk);
        check(m_axi_rready, "匹配迟到R响应未被消费");
        @(negedge clk);
        m_axi_rvalid = 1'b0;
        $display("OBS DELAYED_OKAY_RESPONSE ar=%08x cycle=%0d start_delta=%0d recovery_to_isolated=%0d core_timeout=%0d drain_timeout=%0d",
                 first_ar_address, cycles, cycles-core_start_cycle,
                 isolated_seen_cycle-recovery_seen_cycle,
                 CORE_TIMEOUT_CYCLES, DRAIN_TIMEOUT_CYCLES);

        wait_for_terminal(status_value);
        check(status_value[8] == 1'b0 && status_value[9] == 1'b0 &&
              status_value[10] == 1'b1 && status_value[11] == 1'b1 &&
              status_value[12] == 1'b0 && status_value[13] == 1'b0,
              "ERROR_SAFE所有權、HEAD、SAFE或ledger標誌錯誤");
        check(ar_handshakes == 1 && r_handshakes == 1, "AXI讀事務握手數不為一筆完整事務");
        check(soft_reset_handshakes == 1 && stop_s2_observed &&
              stop_confirmed_cycle >= soft_reset_cycle + 2,
              "未觀察到S及S+2後真實STOP確認");

        csr_read(32'h43c0006c, fault_logical);
        csr_read(32'h43c00070, fault_physical);
        csr_read(32'h43c00074, fault_detail);
        check(fault_logical == 0 && fault_physical == 0,
              "CORE_TIMEOUT首错错误关联了未发生的AXI响应故障地址");
        check(fault_detail[4:0] == 5'b01000,
              "首錯详情未保留排空超时且协议/AXI响应字段错误");
        check(ar_handshakes == 1 && r_handshakes == 1, "首錯後發生額外HP0事務");
        csr_read(32'h43c00010, value);
        check(value == 32'd5, "ERROR_SAFE终态未保持CORE_TIMEOUT首错");

        $display("PASS TOP_RECOVERY ar=%0d r=%0d address=%08x logical=%08x physical=%08x error=%0d detail=%02x START=%0d RECOVERING=%0d ISOLATED=%0d S=%0d STOP=%0d S_delta=%0d",
                 ar_handshakes, r_handshakes, first_ar_address, fault_logical, fault_physical,
                 value, fault_detail[4:0], core_start_cycle, recovery_seen_cycle,
                 isolated_seen_cycle, soft_reset_cycle, stop_confirmed_cycle,
                 stop_confirmed_cycle-soft_reset_cycle);
        $finish;
    end
endmodule
