`timescale 1ns/1ps
module tb_s2c_top_recovery_matrix;
    localparam logic [31:0] CORE_TIMEOUT_CYCLES = 32'd10000;
    localparam logic [31:0] DRAIN_TIMEOUT_CYCLES = 32'd32;
    localparam logic [31:0] CSR_BASE = 32'h43c00000;

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
    logic [31:0] ar_address_record [0:3];
    logic [5:0] ar_id_record [0:3];
    logic [3:0] ar_len_record [0:3];
    logic [2:0] ar_size_record [0:3];
    logic [1:0] ar_burst_record [0:3];

    logic [31:0] status_value;
    logic [31:0] error_value;
    logic [31:0] detail_value;
    logic [31:0] progress_value;
    logic [31:0] epoch_low;
    logic [31:0] epoch_high;
    logic [31:0] ack_low;
    logic [31:0] ack_high;
    logic [1:0] write_response;
    logic [1:0] pre_ack_epoch_low_response;
    logic [1:0] pre_ack_epoch_high_response;
    logic [1:0] pre_ack_response;
    logic [1:0] pre_start_response;
    logic [1:0] post_ack_epoch_low_response;
    logic [1:0] post_ack_epoch_high_response;
    logic [1:0] post_ack_response;
    logic [1:0] post_start_response;
    logic [31:0] status_after_bad_response;
    logic [31:0] status_after_good_response;
    integer wait_cycles;
    integer r_before;
    integer recovery_seen_cycle;
    integer isolated_seen_cycle;
    logic recovering_seen;
    logic isolated_seen;
    logic [63:0] first_epoch;
    logic [63:0] second_epoch;
    logic [63:0] ack_epoch_seen;

    always #5 clk = ~clk;

    always @(posedge clk) begin
        if (!cold_resetn) begin
            cycles = 0;
        end else begin
            cycles = cycles + 1;
            if (m_axi_arvalid && m_axi_arready) begin
                if (ar_handshakes < 4) begin
                    ar_address_record[ar_handshakes] = m_axi_araddr;
                    ar_id_record[ar_handshakes] = m_axi_arid;
                    ar_len_record[ar_handshakes] = m_axi_arlen;
                    ar_size_record[ar_handshakes] = m_axi_arsize;
                    ar_burst_record[ar_handshakes] = m_axi_arburst;
                end
                $display("OBS HP0_AR cycle=%0d index=%0d address=%08x id=%0d len=%0d size=%0d burst=%0b",
                         cycles, ar_handshakes, m_axi_araddr, m_axi_arid, m_axi_arlen,
                         m_axi_arsize, m_axi_arburst);
                ar_handshakes = ar_handshakes + 1;
            end
            if (m_axi_rvalid && m_axi_rready) begin
                $display("OBS HP0_R cycle=%0d index=%0d id=%0d resp=%0b last=%0b",
                         cycles, r_handshakes, m_axi_rid, m_axi_rresp, m_axi_rlast);
                r_handshakes = r_handshakes + 1;
            end
        end
    end

    s2b_inference_top #(
        // 此参数只代表仿真可见性假设，不代表硬件证明。
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

    task automatic csr_write(
        input logic [31:0] address,
        input logic [31:0] value,
        input logic [1:0] expected_response,
        output logic [1:0] observed_response
    );
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
            observed_response = s_axi_bresp;
            $display("OBS CSR_WRITE cycle=%0d address=%08x data=%08x bresp=%0b expected=%0b",
                     cycles, address, value, observed_response, expected_response);
            check(observed_response === expected_response,
                  "公開AXI-Lite寫入BRESP與預期不符");
            s_axi_bready = 1'b1;
            @(posedge clk);
            @(negedge clk);
            s_axi_bready = 1'b0;
        end
    endtask

    task automatic csr_read(
        input logic [31:0] address,
        output logic [31:0] value,
        output logic [1:0] observed_response
    );
        begin
            @(negedge clk);
            s_axi_araddr = address;
            s_axi_arvalid = 1'b1;
            do @(posedge clk); while (!s_axi_arready);
            @(negedge clk);
            s_axi_arvalid = 1'b0;
            while (!s_axi_rvalid) @(negedge clk);
            value = s_axi_rdata;
            observed_response = s_axi_rresp;
            $display("OBS CSR_READ cycle=%0d address=%08x data=%08x rresp=%0b",
                     cycles, address, value, observed_response);
            check(observed_response === 2'b00, "公開AXI-Lite讀取RRESP未返回OKAY");
            s_axi_rready = 1'b1;
            @(posedge clk);
            @(negedge clk);
            s_axi_rready = 1'b0;
        end
    endtask

    task automatic read_status(output logic [31:0] value);
        logic [1:0] response;
        begin
            csr_read(CSR_BASE + 32'h00c, value, response);
            $display("OBS PHYS_STATUS cycle=%0d value=%08x state=%0d owner_pl=%0d head=%0d safe=%0d terminal=%0d ledger_pending=%0d error_pending=%0d",
                     cycles, value, value[2:0], value[8], value[9], value[10],
                     value[11], value[12], value[13]);
        end
    endtask

    task automatic read_error(output logic [31:0] value);
        logic [1:0] response;
        begin
            csr_read(CSR_BASE + 32'h010, value, response);
        end
    endtask

    task automatic read_fault_detail(output logic [31:0] value);
        logic [1:0] response;
        begin
            csr_read(CSR_BASE + 32'h074, value, response);
        end
    endtask

    task automatic read_progress(output logic [31:0] value);
        logic [1:0] response;
        begin
            csr_read(CSR_BASE + 32'h068, value, response);
            $display("OBS AXI_PROGRESS cycle=%0d value=%03x read_active=%0d ar_accepted=%0d",
                     cycles, value[9:0], value[2], value[1]);
        end
    endtask

    task automatic read_epoch(output logic [63:0] value);
        logic [1:0] response;
        begin
            csr_read(CSR_BASE + 32'h050, epoch_low, response);
            csr_read(CSR_BASE + 32'h054, epoch_high, response);
            value = {epoch_high, epoch_low};
            $display("OBS EPOCH cycle=%0d value=%016x", cycles, value);
        end
    endtask

    task automatic read_ack_epoch(output logic [63:0] value);
        logic [1:0] response;
        begin
            csr_read(CSR_BASE + 32'h05c, ack_low, response);
            csr_read(CSR_BASE + 32'h060, ack_high, response);
            value = {ack_high, ack_low};
            $display("OBS ACK_EPOCH cycle=%0d value=%016x", cycles, value);
        end
    endtask

    task automatic wait_for_state(input logic [2:0] wanted_state,
                                  input integer max_reads,
                                  output logic [31:0] last_status);
        integer attempt;
        begin
            last_status = 32'hffffffff;
            attempt = 0;
            while (attempt < max_reads && last_status[2:0] != wanted_state) begin
                read_status(last_status);
                attempt = attempt + 1;
            end
            check(last_status[2:0] == wanted_state,
                  "公開PHYS_STATUS未在限定讀取次數內到達指定狀態");
        end
    endtask

    task automatic wait_for_recovering_isolated(output logic [31:0] isolated_status);
        integer attempt;
        begin
            recovering_seen = 1'b0;
            isolated_seen = 1'b0;
            recovery_seen_cycle = -1;
            isolated_seen_cycle = -1;
            isolated_status = 0;
            attempt = 0;
            while (attempt < 12000 && !isolated_seen) begin
                read_status(status_value);
                if (status_value[2:0] == 3'd3 && !recovering_seen) begin
                    recovering_seen = 1'b1;
                    recovery_seen_cycle = cycles;
                    $display("OBS RECOVERING cycle=%0d status=%08x", cycles, status_value);
                end
                if (status_value[2:0] == 3'd6) begin
                    isolated_seen = 1'b1;
                    isolated_seen_cycle = cycles;
                    isolated_status = status_value;
                    $display("OBS FAULT_ISOLATED cycle=%0d status=%08x recovering_cycle=%0d delta=%0d",
                             cycles, status_value, recovery_seen_cycle,
                             cycles - recovery_seen_cycle);
                end
                attempt = attempt + 1;
            end
            check(recovering_seen && isolated_seen,
                  "未經公開PHYS_STATUS依序觀察RECOVERING與FAULT_ISOLATED");
            check(isolated_seen_cycle > recovery_seen_cycle,
                  "FAULT_ISOLATED沒有晚於RECOVERING");
        end
    endtask

    task automatic accept_next_ar(input integer expected_index);
        integer target_count;
        integer attempt;
        logic [31:0] stable_address;
        begin
            target_count = expected_index + 1;
            attempt = 0;
            while (attempt < 2000 && !m_axi_arvalid) begin
                @(negedge clk);
                attempt = attempt + 1;
            end
            check(m_axi_arvalid, "真實network backend沒有產生預期HP0 AR");
            check(!m_axi_awvalid && !m_axi_wvalid,
                  "預期HP0請求之外觀不是唯讀");
            check(m_axi_arid == 0 && m_axi_arlen == 0 &&
                  m_axi_arburst == 2'b01,
                  "HP0 AR不符合已觀察的單拍AXI3契約");
            check(m_axi_arsize == 0 || m_axi_arsize == 2,
                  "HP0 ARSIZE不是byte或word讀取");
            check(m_axi_araddr >= 32'h10000000 && m_axi_araddr < 32'h12000000,
                  "backend物理讀取位址超出DDR arena");
            stable_address = m_axi_araddr;
            repeat (3) begin
                @(posedge clk);
                check(m_axi_arvalid && m_axi_araddr == stable_address &&
                      !m_axi_arready,
                      "ARREADY停頓期間HP0 AR沒有保持穩定");
            end
            @(negedge clk);
            m_axi_arready = 1'b1;
            @(posedge clk);
            check(m_axi_arvalid && m_axi_araddr == stable_address,
                  "HP0 AR握手沿請求不穩定");
            @(negedge clk);
            m_axi_arready = 1'b0;
            check(ar_handshakes == target_count,
                  "HP0 AR握手計數沒有恰好增加一筆");
            check(ar_address_record[expected_index] == stable_address &&
                  ar_id_record[expected_index] == 0 &&
                  ar_len_record[expected_index] == 0 &&
                  ar_burst_record[expected_index] == 2'b01,
                  "公開HP0 AR觀察記錄與實際接受請求不符");
            $display("OBS ACCEPTED_AR cycle=%0d index=%0d address=%08x id=%0d size=%0d len=%0d burst=%0b",
                     cycles, expected_index, ar_address_record[expected_index],
                     ar_id_record[expected_index], ar_size_record[expected_index],
                     ar_len_record[expected_index], ar_burst_record[expected_index]);
        end
    endtask

    task automatic send_r(input logic [5:0] response_id,
                          input logic response_last,
                          input logic [1:0] response_code);
        begin
            r_before = r_handshakes;
            @(negedge clk);
            m_axi_rid = response_id;
            m_axi_rresp = response_code;
            m_axi_rlast = response_last;
            m_axi_rdata = 64'h6b5a4938271605f4;
            m_axi_rvalid = 1'b1;
            @(posedge clk);
            check(m_axi_rready, "HP0 R通道没有接收能力");
            @(negedge clk);
            m_axi_rvalid = 1'b0;
            check(r_handshakes == r_before + 1,
                  "HP0 R响应没有在真实AXI握手中被消费");
        end
    endtask

    task automatic check_isolated_status(input logic [31:0] observed_status,
                                         input logic ledger_pending);
        begin
            check(observed_status[2:0] == 3'd6 && observed_status[8] &&
                  !observed_status[9] && !observed_status[10] &&
                  !observed_status[11] &&
                  observed_status[12] == ledger_pending &&
                  !observed_status[13],
                  "FAULT_ISOLATED的公開owner/safe/ledger標誌錯誤");
        end
    endtask

    initial begin
        $display("PROFILE_VISIBILITY_PROVEN=1 SIMULATION_ASSUMPTION_ONLY");
        repeat (5) @(posedge clk);
        @(negedge clk);
        cold_resetn = 1'b1;
        repeat (5) @(posedge clk);

        csr_read(CSR_BASE + 32'h000, status_value, write_response);
        check(status_value == 32'h53324250, "公開CSR簽名錯誤");
        csr_write(CSR_BASE + 32'h014, 32'd42, 2'b00, write_response);
        csr_write(CSR_BASE + 32'h018, 32'h00000000, 2'b00, write_response);
        csr_write(CSR_BASE + 32'h01c, 32'd519168, 2'b00, write_response);
        csr_write(CSR_BASE + 32'h020, 32'h00100000, 2'b00, write_response);
        csr_write(CSR_BASE + 32'h024, 32'd5903100, 2'b00, write_response);
        csr_write(CSR_BASE + 32'h028, CORE_TIMEOUT_CYCLES, 2'b00, write_response);
        csr_write(CSR_BASE + 32'h02c, DRAIN_TIMEOUT_CYCLES, 2'b00, write_response);

        // 場景一：先讓真實backend AR進入ledger，內核timeout後回送匹配SLVERR。
        csr_write(CSR_BASE + 32'h008, 32'd1, 2'b00, write_response);
        accept_next_ar(0);
        check(ar_handshakes == 1 && r_handshakes == 0,
              "第一筆AR後ledger或R握手基線錯誤");
        read_progress(progress_value);
        check(progress_value[2] && progress_value[1],
              "第一筆AR後公開AXI_PROGRESS沒有反映接受中的讀事務");
        wait_for_recovering_isolated(status_value);
        check_isolated_status(status_value, 1'b1);
        read_error(error_value);
        check(error_value == 32'd5, "場景一首錯不是CORE_TIMEOUT(5)");
        read_fault_detail(detail_value);
        check(detail_value[4:0] == 5'b01000,
              "遲到SLVERR前FAULT_DETAIL不是單純drain timeout");

        send_r(ar_id_record[0], 1'b1, 2'b10);
        $display("OBS SCENARIO1_LATE_SLVERR cycle=%0d id=%0d resp=2 last=1 ar_address=%08x",
                 cycles, ar_id_record[0], ar_address_record[0]);
        wait_for_state(3'd5, 128, status_value);
        check(status_value[8] == 1'b0 && status_value[9] == 1'b0 &&
              status_value[10] && status_value[11] &&
              !status_value[12] && !status_value[13],
              "匹配遲到SLVERR後ERROR_SAFE旗標/ledger不符");
        check(ar_handshakes == 1 && r_handshakes == 1,
              "場景一遲到SLVERR沒有恰好閉合第一筆AXI讀事務");
        read_error(error_value);
        check(error_value == 32'd5,
              "匹配遲到SLVERR覆蓋了CORE_TIMEOUT首錯");
        read_fault_detail(detail_value);
        check(detail_value[4:0] == 5'b01010,
              "場景一FAULT_DETAIL沒有補記首個遲到SLVERR響應");
        read_epoch(first_epoch);
        check(first_epoch == 64'd1, "場景一epoch不是1");

        csr_write(CSR_BASE + 32'h05c, first_epoch[31:0], 2'b00, write_response);
        csr_write(CSR_BASE + 32'h060, first_epoch[63:32], 2'b00, write_response);
        read_ack_epoch(ack_epoch_seen);
        check(ack_epoch_seen == first_epoch,
              "公開ACK_EPOCH回讀與ERROR_SAFE epoch不匹配");
        csr_write(CSR_BASE + 32'h008, 32'd4, 2'b00, write_response);
        wait_for_state(3'd0, 128, status_value);
        check(!status_value[8] && status_value[10] && !status_value[12],
              "公開CMD ACK後未回到安全IDLE_PS");
        read_error(error_value);
        check(error_value == 0, "CMD ACK後ERROR_CODE沒有清零");
        read_fault_detail(detail_value);
        check(detail_value[4:0] == 0,
              "CMD ACK後FAULT_DETAIL沒有清零");

        csr_write(CSR_BASE + 32'h008, 32'd1, 2'b00, write_response);
        read_epoch(second_epoch);
        check(second_epoch == first_epoch + 64'd1,
              "公開START沒有建立遞增的新64-bit epoch");
        accept_next_ar(1);
        read_status(status_value);
        check(status_value[2:0] == 3'd2 && status_value[8] &&
              !status_value[10] && status_value[12],
              "新epoch的第二筆AR後公開RUN/owner/ledger旗標錯誤");
        read_progress(progress_value);
        check(progress_value[2] && progress_value[1],
              "第二epoch接受AR後公開AXI_PROGRESS沒有讀ledger記錄");
        $display("RESULT scenario=1 name=late_slverr first_error=5 isolated_state=6 final_state=5 final_owner=0 final_safe=1 final_pending=0 detail=0x%02x epoch=0x%016x ack_epoch=0x%016x ack_status=0 restarted_epoch=0x%016x ar_count=%0d r_count=%0d late_rresp=2 late_rlast=1",
                 8'h0A, first_epoch, ack_epoch_seen, second_epoch,
                 ar_handshakes, r_handshakes);

        // 場景二：新epoch第二筆AR尚未完成時，使用公開ABORT並等待排空超時。
        csr_write(CSR_BASE + 32'h008, 32'd2, 2'b00, write_response);
        wait_for_recovering_isolated(status_value);
        check_isolated_status(status_value, 1'b1);
        read_error(error_value);
        check(error_value == 32'd8,
              "公開ABORT首錯沒有保持ERROR_CODE=8");
        read_fault_detail(detail_value);
        check(detail_value[4:0] == 5'b01000,
              "協議錯誤注入前第二場景沒有記錄drain timeout");
        read_progress(progress_value);
        check(progress_value[2] && progress_value[1],
              "ABORT後待處理AR ledger不再由公開AXI_PROGRESS顯示");

        // 同RID但RLAST錯誤會觸發協議隔離，且不能結束原AR記帳。
        send_r(ar_id_record[1], 1'b0, 2'b00);
        read_status(status_after_bad_response);
        check_isolated_status(status_after_bad_response, 1'b1);
        read_error(error_value);
        check(error_value == 32'd8,
              "錯誤RLAST協議事件覆蓋了先前ABORT首錯");
        read_fault_detail(detail_value);
        check(detail_value[4:0] == 5'b11000,
              "錯誤RLAST沒有保留drain timeout並置protocol isolation標記");
        read_progress(progress_value);
        check(progress_value[2] && progress_value[1],
              "錯誤RLAST被錯誤地用來關閉原AR ledger");

        csr_write(CSR_BASE + 32'h05c, second_epoch[31:0], 2'b10,
                  pre_ack_epoch_low_response);
        csr_write(CSR_BASE + 32'h060, second_epoch[63:32], 2'b10,
                  pre_ack_epoch_high_response);
        csr_write(CSR_BASE + 32'h008, 32'd4, 2'b10, pre_ack_response);
        csr_write(CSR_BASE + 32'h008, 32'd1, 2'b10, pre_start_response);
        read_status(status_value);
        check_isolated_status(status_value, 1'b1);

        // 協議隔離已鎖存後，合法晚到R只閉賬，不得發布SAFE或清隔離。
        send_r(ar_id_record[1], 1'b1, 2'b00);
        wait_cycles = 0;
        do begin
            read_status(status_after_good_response);
            wait_cycles = wait_cycles + 1;
        end while (status_after_good_response[12] && wait_cycles < 16);
        check(!status_after_good_response[12],
              "合法匹配晚到R沒有關閉公開pending ledger標記");
        check_isolated_status(status_after_good_response, 1'b0);
        read_progress(progress_value);
        check(progress_value[2:0] == 0,
              "合法匹配晚到R後公開AXI_PROGRESS仍有未結讀ledger");
        read_error(error_value);
        check(error_value == 32'd8,
              "合法晚到R覆蓋了ABORT首錯");
        read_fault_detail(detail_value);
        check(detail_value[4:0] == 5'b11000,
              "合法晚到R錯誤清除了隔離或drain timeout詳情");
        read_ack_epoch(ack_epoch_seen);
        check(ack_epoch_seen == first_epoch,
              "隔離期被拒絕的ACK_EPOCH意外改寫了舊epoch值");

        csr_write(CSR_BASE + 32'h05c, second_epoch[31:0], 2'b10,
                  post_ack_epoch_low_response);
        csr_write(CSR_BASE + 32'h060, second_epoch[63:32], 2'b10,
                  post_ack_epoch_high_response);
        csr_write(CSR_BASE + 32'h008, 32'd4, 2'b10, post_ack_response);
        csr_write(CSR_BASE + 32'h008, 32'd1, 2'b10, post_start_response);
        read_status(status_value);
        check_isolated_status(status_value, 1'b0);
        read_epoch(second_epoch);
        check(second_epoch == 64'd2,
              "隔離期ACK/START拒絕後公開epoch發生變化");
        read_error(error_value);
        check(error_value == 32'd8,
              "隔離期ACK/START拒絕後ABORT首錯發生變化");
        read_fault_detail(detail_value);
        check(detail_value[4:0] == 5'b11000,
              "隔離期ACK/START拒絕後FAULT_DETAIL發生變化");
        check(ar_handshakes == 2 && r_handshakes == 3,
              "矩陣場景AXI實際AR/R握手計數錯誤");

        $display("RESULT scenario=2 name=protocol_isolation first_error=8 state=6 owner=1 safe=0 pending=0 pending_after_bad=1 error_after_bad=8 detail=0x%02x epoch=0x%016x ack_epoch_after_attempt=0x%016x pre_ack_epoch_low_bresp=%0d pre_ack_epoch_high_bresp=%0d pre_ack_bresp=%0d pre_start_bresp=%0d post_ack_epoch_low_bresp=%0d post_ack_epoch_high_bresp=%0d post_ack_bresp=%0d post_start_bresp=%0d bad_rresp=0 bad_rlast=0 ar_count=%0d r_count=%0d",
                 8'h18, second_epoch, ack_epoch_seen,
                 pre_ack_epoch_low_response, pre_ack_epoch_high_response,
                 pre_ack_response, pre_start_response,
                 post_ack_epoch_low_response, post_ack_epoch_high_response,
                 post_ack_response, post_start_response,
                 ar_handshakes, r_handshakes);
        $display("PASS S2C_TOP_RECOVERY_MATRIX scenarios=2 ar=%0d r=%0d core_timeout=%0d drain_timeout=%0d",
                 ar_handshakes, r_handshakes,
                 CORE_TIMEOUT_CYCLES, DRAIN_TIMEOUT_CYCLES);
        $finish;
    end

    initial begin
        #5000000;
        $fatal(1, "整合恢復矩陣超過仿真 watchdog");
    end
endmodule
