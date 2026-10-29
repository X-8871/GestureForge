`timescale 1ns/1ps
module tb_s2c_rtl07_bulk_bridge;
    logic clk = 1'b0;
    logic cold_reset = 1'b0;
    logic run_enable = 1'b0;
    logic cancel = 1'b0;
    logic clear_safe = 1'b0;
    logic [63:0] run_epoch = 64'd0;

    logic bulk_cmd_valid = 1'b0;
    logic bulk_cmd_ready;
    logic bulk_cmd_write = 1'b0;
    logic [31:0] bulk_cmd_addr = 32'd0;
    logic [7:0] bulk_cmd_bytes = 8'd0;
    logic bulk_wvalid = 1'b0;
    logic bulk_wready;
    logic [7:0] bulk_wdata = 8'd0;
    logic bulk_rvalid;
    logic bulk_rready = 1'b0;
    logic [7:0] bulk_rdata;
    logic bulk_done_valid;
    logic bulk_done_ready = 1'b0;
    logic [2:0] bulk_done_error;

    logic [5:0] m_axi_arid, m_axi_awid, m_axi_wid;
    logic [31:0] m_axi_araddr, m_axi_awaddr;
    logic [3:0] m_axi_arlen, m_axi_awlen;
    logic [2:0] m_axi_arsize, m_axi_awsize;
    logic [1:0] m_axi_arburst, m_axi_awburst, m_axi_arlock, m_axi_awlock;
    logic [3:0] m_axi_arcache, m_axi_awcache;
    logic [2:0] m_axi_arprot, m_axi_awprot;
    logic [3:0] m_axi_arqos, m_axi_awqos;
    logic m_axi_arvalid;
    logic m_axi_arready = 1'b0;
    logic [5:0] m_axi_rid = 6'd0;
    logic [63:0] m_axi_rdata = 64'd0;
    logic [1:0] m_axi_rresp = 2'b00;
    logic m_axi_rlast = 1'b0;
    logic m_axi_rvalid = 1'b0;
    logic m_axi_rready;
    logic m_axi_awvalid;
    logic m_axi_awready = 1'b0;
    logic m_axi_wvalid;
    logic [63:0] m_axi_wdata;
    logic [7:0] m_axi_wstrb;
    logic m_axi_wlast;
    logic m_axi_wready = 1'b0;
    logic [5:0] m_axi_bid = 6'd0;
    logic [1:0] m_axi_bresp = 2'b00;
    logic m_axi_bvalid = 1'b0;
    logic m_axi_bready;

    logic ledger_empty;
    logic [63:0] ledger_epoch;
    logic recovery_required;
    logic protocol_isolated;
    logic first_fault_valid;
    logic [7:0] first_fault_code;
    logic [31:0] first_fault_address;
    logic fault_event_valid;
    logic [7:0] fault_event_code;
    logic [31:0] fault_event_address;
    logic clear_rejected;
    logic [9:0] axi_progress;
    logic [9:0] axi_progress_next;
    logic ledger_empty_next;
    logic [1:0] fault_event_resp;
    logic fault_event_write;
    logic fault_event_protocol;
    logic fault_event_address_valid;
    logic [31:0] fault_event_physical_address;

    logic guard_mem_write = 1'b0;
    logic [31:0] guard_mem_addr = 32'd0;
    logic [3:0] guard_mem_rstrb = 4'd0;
    logic [3:0] guard_mem_wstrb = 4'd0;
    logic guard_allowed;
    logic [31:0] guard_physical_addr;
    logic [32:0] guard_region_begin, guard_region_end;
    logic [2:0] guard_error;

    logic disabled_ready;
    logic disabled_wready;
    logic disabled_rvalid;
    logic disabled_done_valid;
    logic disabled_arvalid, disabled_awvalid, disabled_wvalid;
    logic disabled_rready, disabled_bready;
    integer cycles = 0;
    integer directed_cases = 0;
    integer axi_ar_count = 0;
    integer axi_aw_count = 0;
    integer axi_w_count = 0;
    integer axi_r_count = 0;
    integer axi_b_count = 0;

    s2c_axi3_bulk_bridge #(.ENABLE_BULK(1'b1)) dut (.*);

    s2c_axi3_bulk_bridge disabled_dut (
        .clk(clk),
        .cold_reset(cold_reset),
        .run_enable(1'b1),
        .cancel(1'b0),
        .clear_safe(1'b0),
        .run_epoch(64'd0),
        .bulk_cmd_valid(1'b1),
        .bulk_cmd_ready(disabled_ready),
        .bulk_cmd_write(1'b0),
        .bulk_cmd_addr(32'd0),
        .bulk_cmd_bytes(8'd8),
        .bulk_wvalid(1'b1),
        .bulk_wready(disabled_wready),
        .bulk_wdata(8'h5a),
        .bulk_rvalid(disabled_rvalid),
        .bulk_rready(1'b1),
        .bulk_done_valid(disabled_done_valid),
        .bulk_done_ready(1'b1),
        .m_axi_arvalid(disabled_arvalid),
        .m_axi_arready(1'b1),
        .m_axi_rid(6'd0),
        .m_axi_rdata(64'd0),
        .m_axi_rresp(2'b00),
        .m_axi_rlast(1'b1),
        .m_axi_rvalid(1'b1),
        .m_axi_rready(disabled_rready),
        .m_axi_awvalid(disabled_awvalid),
        .m_axi_awready(1'b1),
        .m_axi_wvalid(disabled_wvalid),
        .m_axi_wready(1'b1),
        .m_axi_bvalid(1'b1),
        .m_axi_bid(6'd0),
        .m_axi_bresp(2'b00),
        .m_axi_bready(disabled_bready)
    );

    s2b_request_guard guard_dut (
        .mem_write(guard_mem_write),
        .mem_addr(guard_mem_addr),
        .mem_rstrb(guard_mem_rstrb),
        .mem_wstrb(guard_mem_wstrb),
        .request_allowed(guard_allowed),
        .physical_addr(guard_physical_addr),
        .region_begin_phys(guard_region_begin),
        .region_end_phys_exclusive(guard_region_end),
        .error_code(guard_error)
    );

    always #5 clk = ~clk;

    // 只计数物理AXI实际握手，非法命令用这些计数证明没有发起事务。
    always_ff @(posedge clk) begin
        if (cold_reset) begin
            axi_ar_count <= 0;
            axi_aw_count <= 0;
            axi_w_count <= 0;
            axi_r_count <= 0;
            axi_b_count <= 0;
        end else begin
            if (m_axi_arvalid && m_axi_arready) axi_ar_count <= axi_ar_count + 1;
            if (m_axi_awvalid && m_axi_awready) axi_aw_count <= axi_aw_count + 1;
            if (m_axi_wvalid && m_axi_wready) axi_w_count <= axi_w_count + 1;
            if (m_axi_rvalid && m_axi_rready) axi_r_count <= axi_r_count + 1;
            if (m_axi_bvalid && m_axi_bready) axi_b_count <= axi_b_count + 1;
        end
    end

    function automatic logic [7:0] payload_byte(input integer index);
        logic [7:0] value;
        begin
            value = index ^ 8'ha5;
            return value;
        end
    endfunction

    function automatic logic [7:0] memory_byte(input logic [31:0] address);
        logic [7:0] value;
        begin
            value = (address * 32'd37) ^ (address >> 8) ^ 8'h6d;
            return value;
        end
    endfunction

    function automatic logic [63:0] memory_word(input logic [31:0] address);
        logic [63:0] value;
        begin
            for (int lane = 0; lane < 8; lane++)
                value[8*lane +: 8] = memory_byte(address + 32'(lane));
            return value;
        end
    endfunction

    function automatic integer expected_segment_beats(
        input logic [31:0] address,
        input integer remaining_bytes
    );
        integer page_beats;
        integer left_beats;
        begin
            page_beats = (4096 - (address & 32'h00000fff)) / 8;
            left_beats = remaining_bytes / 8;
            if (left_beats > 16) left_beats = 16;
            if (page_beats < left_beats)
                return page_beats;
            return left_beats;
        end
    endfunction

    task automatic must(input logic condition, input string reason);
        begin
            if (condition !== 1'b1)
                $fatal(1, "cycle=%0d case=%0d %s", cycles, directed_cases, reason);
        end
    endtask

    task automatic tick();
        begin
            @(posedge clk);
            #1;
            cycles++;
        end
    endtask

    task automatic reset_case();
        begin
            @(negedge clk);
            cold_reset = 1'b1;
            run_enable = 1'b0;
            cancel = 1'b0;
            clear_safe = 1'b0;
            run_epoch = 64'd0;
            bulk_cmd_valid = 1'b0;
            bulk_cmd_write = 1'b0;
            bulk_cmd_addr = 32'd0;
            bulk_cmd_bytes = 8'd0;
            bulk_wvalid = 1'b0;
            bulk_wdata = 8'd0;
            bulk_rready = 1'b0;
            bulk_done_ready = 1'b0;
            m_axi_arready = 1'b0;
            m_axi_rid = 6'd0;
            m_axi_rdata = 64'd0;
            m_axi_rresp = 2'b00;
            m_axi_rlast = 1'b0;
            m_axi_rvalid = 1'b0;
            m_axi_awready = 1'b0;
            m_axi_wready = 1'b0;
            m_axi_bid = 6'd0;
            m_axi_bresp = 2'b00;
            m_axi_bvalid = 1'b0;
            repeat (2) tick();
            @(negedge clk);
            cold_reset = 1'b0;
            run_enable = 1'b1;
            run_epoch = 64'h0710_2026_0000_0001;
            tick();
            must(ledger_empty && !recovery_required &&
                 !protocol_isolated, "复位后账本应为空");
            must(!disabled_ready && !disabled_wready && !disabled_rvalid &&
                 !disabled_done_valid && !disabled_arvalid &&
                 !disabled_awvalid && !disabled_wvalid &&
                 !disabled_rready && !disabled_bready,
                 "默认关闭实例不得接收命令或参与AXI");
        end
    endtask

    task automatic issue_command(
        input logic write_request,
        input logic [31:0] address,
        input logic [7:0] bytes
    );
        integer timeout;
        begin
            @(negedge clk);
            bulk_cmd_write = write_request;
            bulk_cmd_addr = address;
            bulk_cmd_bytes = bytes;
            bulk_cmd_valid = 1'b1;
            timeout = 0;
            while ((bulk_cmd_ready !== 1'b1) && timeout < 20) begin
                tick();
                timeout++;
            end
            must(bulk_cmd_ready, "命令准入超时");
            @(posedge clk);
            #1;
            bulk_cmd_valid = 1'b0;
            cycles++;
            directed_cases++;
        end
    endtask

    task automatic send_write_payload(input integer bytes);
        begin
            for (int index = 0; index < bytes; index++) begin
                @(negedge clk);
                bulk_wvalid = 1'b1;
                bulk_wdata = payload_byte(index);
                #1;
                must(bulk_wready, "写payload未接收");
                @(posedge clk);
                #1;
                cycles++;
            end
            @(negedge clk);
            bulk_wvalid = 1'b0;
            #1;
            must(!m_axi_awvalid && !m_axi_wvalid,
                 "payload收齐前后不应提前声明物理地址或数据");
        end
    endtask

    task automatic wait_for_ar();
        integer timeout;
        begin
            timeout = 0;
            while ((m_axi_arvalid !== 1'b1) && timeout < 20) begin
                tick();
                timeout++;
            end
            must(m_axi_arvalid, "等待AR超时");
        end
    endtask

    task automatic wait_for_done(input logic [2:0] expected_error);
        integer timeout;
        begin
            timeout = 0;
            while ((bulk_done_valid !== 1'b1) && timeout < 32) begin
                tick();
                timeout++;
            end
            must(bulk_done_valid, "等待bulk done超时");
            must(bulk_done_error == expected_error, "bulk done错误码不符");
            @(negedge clk);
            bulk_done_ready = 1'b1;
            @(posedge clk);
            #1;
            bulk_done_ready = 1'b0;
            cycles++;
            must(ledger_empty, "done握手后账本未关闭");
        end
    endtask

    task automatic run_read(input logic [31:0] address, input integer bytes);
        logic [31:0] physical_start;
        integer offset;
        integer beats;
        integer timeout;
        logic [63:0] saved_ar;
        begin
            physical_start = 32'h1000_0000 + address;
            issue_command(1'b0, address, 8'(bytes));
            offset = 0;
            while (offset < bytes) begin
                wait_for_ar();
                beats = expected_segment_beats(physical_start + offset,
                                               bytes - offset);
                must(m_axi_arid == 0 &&
                     m_axi_araddr == physical_start + offset &&
                     m_axi_arlen == (beats - 1) &&
                     m_axi_arsize == 3 &&
                     m_axi_arburst == 2'b01,
                     "AR属性、长度或4KiB分段不符");
                saved_ar = {m_axi_araddr, m_axi_arlen, m_axi_arsize,
                            m_axi_arburst, m_axi_arlock, m_axi_arcache,
                            m_axi_arprot, m_axi_arqos};
                @(negedge clk);
                m_axi_arready = 1'b0;
                tick();
                must(m_axi_arvalid &&
                     saved_ar == {m_axi_araddr, m_axi_arlen, m_axi_arsize,
                                  m_axi_arburst, m_axi_arlock, m_axi_arcache,
                                  m_axi_arprot, m_axi_arqos},
                     "AR受阻时VALID或负载改变");
                @(negedge clk);
                m_axi_arready = 1'b1;
                tick();
                m_axi_arready = 1'b0;
                for (int beat = 0; beat < beats; beat++) begin
                    @(negedge clk);
                    m_axi_rid = 6'd0;
                    m_axi_rdata = memory_word(physical_start + offset +
                                              (beat * 8));
                    m_axi_rresp = 2'b00;
                    m_axi_rlast = (beat == beats - 1);
                    m_axi_rvalid = 1'b1;
                    tick();
                    m_axi_rvalid = 1'b0;
                end
                offset += beats * 8;
            end

            timeout = 0;
            while ((bulk_rvalid !== 1'b1) && timeout < 20) begin
                tick();
                timeout++;
            end
            must(bulk_rvalid, "读数据交付等待超时");
            @(negedge clk);
            bulk_rready = 1'b0;
            saved_ar = {56'd0, bulk_rdata};
            tick();
            must(bulk_rvalid && bulk_rdata == saved_ar[7:0],
                 "读数据反压时VALID或数据改变");
            for (int index = 0; index < bytes; index++) begin
                @(negedge clk);
                bulk_rready = 1'b1;
                #1;
                must(bulk_rvalid &&
                     bulk_rdata == memory_byte(physical_start + index),
                     "读字节次序或内容不符");
                @(posedge clk);
                #1;
                cycles++;
            end
            bulk_rready = 1'b0;
            wait_for_done(3'd0);
            must(!protocol_isolated && !recovery_required,
                 "成功读不应触发恢复");
        end
    endtask

    task automatic run_write(input logic [31:0] address,
                             input integer bytes);
        logic [31:0] physical_start;
        logic [63:0] expected_data;
        logic [78:0] saved_w;
        logic [59:0] saved_aw;
        integer offset;
        integer beats;
        begin
            physical_start = 32'h1000_0000 + address;
            issue_command(1'b1, address, 8'(bytes));
            must(!m_axi_awvalid && !m_axi_wvalid,
                 "写payload尚未收齐却声明物理事务");
            send_write_payload(bytes);
            offset = 0;
            while (offset < bytes) begin
                tick();
                beats = expected_segment_beats(physical_start + offset,
                                               bytes - offset);
                must(m_axi_awvalid && m_axi_wvalid &&
                     m_axi_awid == 0 &&
                     m_axi_awaddr == physical_start + offset &&
                     m_axi_awlen == (beats - 1) &&
                     m_axi_awsize == 3 &&
                     m_axi_awburst == 2'b01,
                     "AW属性、长度或4KiB分段不符");
                saved_aw = {m_axi_awid, m_axi_awaddr, m_axi_awlen,
                            m_axi_awsize, m_axi_awburst, m_axi_awlock,
                            m_axi_awcache, m_axi_awprot, m_axi_awqos};
                @(negedge clk);
                m_axi_awready = 1'b0;
                m_axi_wready = 1'b0;
                saved_w = {m_axi_wid, m_axi_wdata, m_axi_wstrb,
                           m_axi_wlast};
                tick();
                must(m_axi_awvalid && m_axi_wvalid &&
                     saved_aw == {m_axi_awid, m_axi_awaddr, m_axi_awlen,
                                  m_axi_awsize, m_axi_awburst,
                                  m_axi_awlock, m_axi_awcache,
                                  m_axi_awprot, m_axi_awqos} &&
                     saved_w == {m_axi_wid, m_axi_wdata, m_axi_wstrb,
                                 m_axi_wlast},
                     "AW/W受阻时VALID或负载改变");

                for (int beat = 0; beat < beats; beat++) begin
                    expected_data = 64'd0;
                    for (int lane = 0; lane < 8; lane++)
                        expected_data[8*lane +: 8] =
                            payload_byte(offset + beat*8 + lane);
                    @(negedge clk);
                    m_axi_wready = 1'b0;
                    #1;
                    must(m_axi_wvalid && m_axi_wdata == expected_data &&
                         m_axi_wstrb == 8'hff &&
                         m_axi_wlast == (beat == beats - 1),
                         "W内容、WSTRB或WLAST不符");
                    tick();
                    must(m_axi_wvalid && m_axi_wdata == expected_data,
                         "W负载在反压时不稳定");
                    @(negedge clk);
                    m_axi_wready = 1'b1;
                    tick();
                    m_axi_wready = 1'b0;
                end

                // AXI3允许全部W握手后B先于AW接受；桥必须等AW闭合。
                @(negedge clk);
                m_axi_bid = 6'd0;
                m_axi_bresp = 2'b00;
                m_axi_bvalid = 1'b1;
                #1;
                must(m_axi_bready, "B通道未准备接收响应");
                tick();
                m_axi_bvalid = 1'b0;
                must(!bulk_done_valid, "B早于AW时不能提前完成写段");
                @(negedge clk);
                m_axi_awready = 1'b1;
                tick();
                m_axi_awready = 1'b0;
                must(!m_axi_awvalid, "AW握手后VALID未撤销");
                offset += beats * 8;
            end
            wait_for_done(3'd0);
            must(!protocol_isolated && !recovery_required,
                 "成功写不应触发恢复");
        end
    endtask

    task automatic test_guard_bounds();
        begin
            guard_mem_write = 1'b0;
            guard_mem_addr = 32'h0100_0000;
            guard_mem_rstrb = 4'b0001;
            guard_mem_wstrb = 4'b0000;
            #1;
            must(guard_allowed && guard_physical_addr == 32'h1100_0000 &&
                 guard_region_begin == 33'h011000000 &&
                 guard_region_end == 33'h011152000,
                 "feature对象read bounds不符");
            guard_mem_write = 1'b1;
            guard_mem_addr = 32'h0000_0000;
            guard_mem_rstrb = 4'b0000;
            guard_mem_wstrb = 4'b0001;
            #1;
            must(!guard_allowed && guard_region_begin == 0 &&
                 guard_region_end == 0 && guard_error == 3'd2,
                 "read-only对象不应允许写且无效bounds必须归零");
            guard_mem_write = 1'b1;
            guard_mem_addr = 32'h0100_0000;
            guard_mem_wstrb = 4'b0001;
            #1;
            must(guard_allowed && guard_region_begin == 33'h011000000 &&
                 guard_region_end == 33'h011152000,
                 "feature对象write bounds不符");
            directed_cases += 3;
        end
    endtask

    task automatic test_early_rejection(input logic [31:0] address,
                                        input logic [7:0] bytes,
                                        input logic [2:0] expected_error);
        integer before_ar;
        integer before_aw;
        integer before_w;
        integer before_r;
        integer before_b;
        begin
            before_ar = axi_ar_count;
            before_aw = axi_aw_count;
            before_w = axi_w_count;
            before_r = axi_r_count;
            before_b = axi_b_count;
            must(before_ar == 0 && before_aw == 0 && before_w == 0 &&
                 before_r == 0 && before_b == 0,
                 "非法命令定向用例须从零物理AXI计数开始");
            issue_command(1'b0, address, bytes);
            must(bulk_done_valid && bulk_done_error == expected_error &&
                 !m_axi_arvalid && !m_axi_awvalid && !m_axi_wvalid,
                 "非法命令必须立即拒绝且不发AXI");
            wait_for_done(expected_error);
            must(axi_ar_count == 0 && axi_aw_count == 0 && axi_w_count == 0 &&
                 axi_r_count == 0 && axi_b_count == 0 &&
                 axi_ar_count == before_ar && axi_aw_count == before_aw &&
                 axi_w_count == before_w && axi_r_count == before_r &&
                 axi_b_count == before_b,
                 "非法命令拒绝前后物理AXI AR/AW/W/R/B握手计数必须保持零");
            $display("CHECK RTL07 rejected address=0x%08h bytes=%0d error=%0d AXI_AR/AW/W/R/B=0",
                     address, bytes, expected_error);
        end
    endtask

    task automatic test_read_response_error();
        logic [31:0] physical_start;
        begin
            physical_start = 32'h1100_0000;
            issue_command(1'b0, 32'h0100_0000, 8'd16);
            wait_for_ar();
            @(negedge clk);
            m_axi_arready = 1'b1;
            tick();
            m_axi_arready = 1'b0;
            @(negedge clk);
            m_axi_rid = 6'd0;
            m_axi_rdata = memory_word(physical_start);
            m_axi_rresp = 2'b11;
            m_axi_rlast = 1'b0;
            m_axi_rvalid = 1'b1;
            #1;
            must(fault_event_valid && fault_event_code == 8'd10 &&
                 !fault_event_protocol,
                 "DECERR读响应事件码/协议标志错误");
            tick();
            m_axi_rvalid = 1'b0;
            m_axi_rresp = 2'b00;
            @(negedge clk);
            m_axi_rdata = memory_word(physical_start + 8);
            m_axi_rlast = 1'b1;
            m_axi_rvalid = 1'b1;
            tick();
            m_axi_rvalid = 1'b0;
            must(ledger_empty && recovery_required && first_fault_valid &&
                 first_fault_code == 8'd10 && !bulk_rvalid &&
                 !bulk_done_valid && !protocol_isolated,
                 "读错误应排空、不交付部分数据并记录恢复");
            directed_cases++;
        end
    endtask

    task automatic test_bad_rlast_isolates();
        begin
            issue_command(1'b0, 32'h0100_0000, 8'd8);
            wait_for_ar();
            @(negedge clk);
            m_axi_arready = 1'b1;
            tick();
            m_axi_arready = 1'b0;
            @(negedge clk);
            m_axi_rid = 6'd0;
            m_axi_rdata = 64'h0706_0504_0302_0100;
            m_axi_rlast = 1'b0;
            m_axi_rvalid = 1'b1;
            #1;
            must(fault_event_valid && fault_event_code == 8'd11 &&
                 fault_event_protocol, "错误RLAST必须产生协议隔离");
            tick();
            m_axi_rvalid = 1'b0;
            must(protocol_isolated && !ledger_empty &&
                 !bulk_rvalid && !bulk_done_valid,
                 "错误RLAST不能关闭账本或交付读数据");
            directed_cases++;
        end
    endtask

    task automatic test_early_b_fault();
        begin
            issue_command(1'b1, 32'h0100_0000, 8'd16);
            send_write_payload(16);
            tick();
            must(m_axi_wvalid && m_axi_awvalid, "测试前未进入写AXI阶段");
            @(negedge clk);
            m_axi_bid = 6'd0;
            m_axi_bresp = 2'b00;
            m_axi_bvalid = 1'b1;
            #1;
            must(fault_event_valid && fault_event_code == 8'd11 &&
                 fault_event_protocol,
                 "W尚未全部接受的早期B必须隔离");
            tick();
            m_axi_bvalid = 1'b0;
            must(protocol_isolated && !ledger_empty && !bulk_done_valid,
                 "早期B不能关闭写账本或报告完成");
            directed_cases++;
        end
    endtask

    task automatic test_cancel_before_write_axi();
        begin
            issue_command(1'b1, 32'h0100_0000, 8'd16);
            @(negedge clk);
            bulk_wvalid = 1'b1;
            bulk_wdata = payload_byte(0);
            #1;
            must(bulk_wready, "取消测试写payload未就绪");
            cancel = 1'b1;
            tick();
            bulk_wvalid = 1'b0;
            cancel = 1'b0;
            must(ledger_empty && recovery_required &&
                 !m_axi_awvalid && !m_axi_wvalid && !bulk_done_valid,
                 "物理声明前取消应丢弃本地payload并关闭逻辑账本");
            @(negedge clk);
            run_enable = 1'b0;
            clear_safe = 1'b1;
            #1;
            must(!clear_rejected, "停止且账本空时应允许恢复clear");
            tick();
            clear_safe = 1'b0;
            must(!recovery_required, "安全clear后应清除恢复要求");
            directed_cases++;
        end
    endtask

    task automatic test_cancel_ar_stalled();
        begin
            issue_command(1'b0, 32'h0100_0000, 8'd8);
            wait_for_ar();
            @(negedge clk);
            m_axi_arready = 1'b0;
            cancel = 1'b1;
            #1;
            must(m_axi_arvalid && !bulk_rvalid,
                 "取消不能撤回已声明但受阻的ARVALID");
            tick();
            cancel = 1'b0;
            must(!ledger_empty && m_axi_arvalid && !bulk_done_valid,
                 "AR未接受时取消仍须保留物理账本");
            @(negedge clk);
            m_axi_arready = 1'b1;
            tick();
            m_axi_arready = 1'b0;
            @(negedge clk);
            m_axi_rid = 6'd0;
            m_axi_rdata = memory_word(32'h1100_0000);
            m_axi_rresp = 2'b00;
            m_axi_rlast = 1'b1;
            m_axi_rvalid = 1'b1;
            tick();
            m_axi_rvalid = 1'b0;
            must(ledger_empty && recovery_required && !bulk_rvalid &&
                 !bulk_done_valid,
                 "取消后的AR/R应排空且不交付");
            directed_cases++;
        end
    endtask

    task automatic test_cancel_read_waiting_r();
        begin
            issue_command(1'b0, 32'h0100_0000, 8'd8);
            wait_for_ar();
            @(negedge clk);
            m_axi_arready = 1'b1;
            tick();
            m_axi_arready = 1'b0;
            @(negedge clk);
            cancel = 1'b1;
            tick();
            cancel = 1'b0;
            must(!ledger_empty && !bulk_rvalid && !bulk_done_valid,
                 "AR已接受而R未到时取消不得清空物理账本");
            @(negedge clk);
            m_axi_rid = 6'd0;
            m_axi_rdata = memory_word(32'h1100_0000);
            m_axi_rresp = 2'b00;
            m_axi_rlast = 1'b1;
            m_axi_rvalid = 1'b1;
            tick();
            m_axi_rvalid = 1'b0;
            must(ledger_empty && recovery_required && !bulk_rvalid &&
                 !bulk_done_valid,
                 "取消后的迟到R应排空且丢弃");
            directed_cases++;
        end
    endtask

    task automatic test_cancel_read_delivery();
        begin
            issue_command(1'b0, 32'h0100_0000, 8'd8);
            wait_for_ar();
            @(negedge clk);
            m_axi_arready = 1'b1;
            tick();
            m_axi_arready = 1'b0;
            @(negedge clk);
            m_axi_rid = 6'd0;
            m_axi_rdata = memory_word(32'h1100_0000);
            m_axi_rresp = 2'b00;
            m_axi_rlast = 1'b1;
            m_axi_rvalid = 1'b1;
            tick();
            m_axi_rvalid = 1'b0;
            #1;
            if (!bulk_rvalid || ledger_empty)
                $display("TRACE read-delivery state=%0d bytes=%0d seg_beats=%0d r_index=%0d cancel_now=%0b event=%0b epoch_mismatch=%0b isolated=%0b cancelled=%0b read_ready=%0b",
                         dut.q.state, dut.q.command_bytes, dut.q.segment_beats,
                         dut.q.read_beat_index, dut.cancel_now,
                         fault_event_valid, dut.epoch_mismatch,
                         protocol_isolated, dut.q.cancelled, bulk_rready);
            must(bulk_rvalid && !ledger_empty,
                 "读缓存收齐后应等待core接收字节");
            @(negedge clk);
            bulk_rready = 1'b0;
            cancel = 1'b1;
            #1;
            must(!bulk_rvalid, "取消同沿必须抑制读字节交付");
            tick();
            cancel = 1'b0;
            must(ledger_empty && recovery_required && !bulk_done_valid,
                 "读交付取消应丢弃缓存并关闭逻辑账本");
            directed_cases++;
        end
    endtask

    task automatic test_cancel_done_backpressure();
        begin
            issue_command(1'b0, 32'h0100_0000, 8'd8);
            wait_for_ar();
            @(negedge clk);
            m_axi_arready = 1'b1;
            tick();
            m_axi_arready = 1'b0;
            @(negedge clk);
            m_axi_rid = 6'd0;
            m_axi_rdata = memory_word(32'h1100_0000);
            m_axi_rresp = 2'b00;
            m_axi_rlast = 1'b1;
            m_axi_rvalid = 1'b1;
            tick();
            m_axi_rvalid = 1'b0;
            for (int index = 0; index < 8; index++) begin
                @(negedge clk);
                bulk_rready = 1'b1;
                @(posedge clk);
                #1;
                cycles++;
            end
            bulk_rready = 1'b0;
            must(bulk_done_valid && !bulk_done_ready,
                 "完成valid应在反压期间保持");
            @(negedge clk);
            cancel = 1'b1;
            #1;
            must(!bulk_done_valid, "取消同沿必须抑制完成valid");
            tick();
            cancel = 1'b0;
            must(ledger_empty && recovery_required && !bulk_done_valid,
                 "DONE反压期间取消应丢弃内部完成");
            directed_cases++;
        end
    endtask

    task automatic test_cancel_partial_write_and_delayed_b();
        logic [63:0] expected_data;
        begin
            issue_command(1'b1, 32'h0100_0000, 8'd16);
            send_write_payload(16);
            tick();
            must(m_axi_awvalid && m_axi_wvalid && m_axi_awaddr == 32'h1100_0000,
                 "取消写测试未进入AW/W声明阶段");
            @(negedge clk);
            m_axi_awready = 1'b0;
            m_axi_wready = 1'b1;
            expected_data = 64'd0;
            for (int lane = 0; lane < 8; lane++)
                expected_data[8*lane +: 8] = payload_byte(lane);
            #1;
            must(m_axi_wdata == expected_data && !m_axi_wlast,
                 "首个写beat负载错误");
            tick();
            m_axi_wready = 1'b0;
            must(m_axi_wvalid && m_axi_wlast,
                 "首拍接受后应保留第二个W beat");
            @(negedge clk);
            cancel = 1'b1;
            #1;
            must(m_axi_awvalid && m_axi_wvalid,
                 "取消不得撤回已声明AW/WVALID");
            expected_data = 64'd0;
            for (int lane = 0; lane < 8; lane++)
                expected_data[8*lane +: 8] = payload_byte(8 + lane);
            must(m_axi_wdata == expected_data && m_axi_wlast,
                 "受阻的末拍W数据或WLAST错误");
            tick();
            cancel = 1'b0;
            must(!ledger_empty && !bulk_done_valid,
                 "全部W完成但B/AW未闭合时账本必须保持");
            @(negedge clk);
            m_axi_wready = 1'b1;
            tick();
            m_axi_wready = 1'b0;
            @(negedge clk);
            m_axi_bid = 6'd0;
            m_axi_bresp = 2'b00;
            m_axi_bvalid = 1'b1;
            tick();
            m_axi_bvalid = 1'b0;
            must(!ledger_empty && !bulk_done_valid,
                 "合法早B仍须等待受阻AW");
            @(negedge clk);
            m_axi_awready = 1'b1;
            tick();
            m_axi_awready = 1'b0;
            must(ledger_empty && recovery_required && !bulk_done_valid,
                 "取消写完成AW/W/B闭合后不可向core报告成功");
            directed_cases++;
        end
    endtask

    task automatic test_bad_rid_isolates();
        begin
            issue_command(1'b0, 32'h0100_0000, 8'd8);
            wait_for_ar();
            @(negedge clk);
            m_axi_arready = 1'b1;
            tick();
            m_axi_arready = 1'b0;
            @(negedge clk);
            m_axi_rid = 6'd1;
            m_axi_rdata = memory_word(32'h1100_0000);
            m_axi_rlast = 1'b1;
            m_axi_rvalid = 1'b1;
            #1;
            must(fault_event_valid && fault_event_code == 8'd11 &&
                 fault_event_protocol, "错误RID必须产生协议隔离");
            tick();
            m_axi_rvalid = 1'b0;
            must(protocol_isolated && !ledger_empty &&
                 !bulk_rvalid && !bulk_done_valid,
                 "错误RID不能关闭读账本或交付数据");
            directed_cases++;
        end
    endtask

    task automatic test_bad_bid_isolates();
        begin
            issue_command(1'b1, 32'h0100_0000, 8'd8);
            send_write_payload(8);
            tick();
            @(negedge clk);
            m_axi_awready = 1'b0;
            m_axi_wready = 1'b1;
            tick();
            m_axi_wready = 1'b0;
            @(negedge clk);
            m_axi_bid = 6'd1;
            m_axi_bresp = 2'b00;
            m_axi_bvalid = 1'b1;
            #1;
            must(fault_event_valid && fault_event_code == 8'd11 &&
                 fault_event_protocol, "错误BID必须产生协议隔离");
            tick();
            m_axi_bvalid = 1'b0;
            must(protocol_isolated && !ledger_empty && !bulk_done_valid,
                 "错误BID不能关闭写账本或报告完成");
            directed_cases++;
        end
    endtask

    task automatic test_epoch_change_and_busy_clear();
        begin
            issue_command(1'b0, 32'h0100_0000, 8'd8);
            wait_for_ar();
            @(negedge clk);
            clear_safe = 1'b1;
            #1;
            must(clear_rejected && !ledger_empty,
                 "物理账本忙时必须拒绝clear_safe");
            tick();
            clear_safe = 1'b0;
            @(negedge clk);
            m_axi_arready = 1'b1;
            tick();
            m_axi_arready = 1'b0;
            @(negedge clk);
            run_epoch = run_epoch + 64'd1;
            #1;
            must(fault_event_valid && fault_event_code == 8'd6 &&
                 fault_event_protocol,
                 "epoch失配必须公开为协议隔离事件");
            tick();
            @(negedge clk);
            run_epoch = run_epoch - 64'd1;
            m_axi_rid = 6'd0;
            m_axi_rdata = memory_word(32'h1100_0000);
            m_axi_rlast = 1'b1;
            m_axi_rvalid = 1'b1;
            tick();
            m_axi_rvalid = 1'b0;
            must(protocol_isolated && !ledger_empty && !bulk_rvalid &&
                 !bulk_done_valid && first_fault_valid &&
                 first_fault_code == 8'd6,
                 "epoch失配后必须排空物理R但保持隔离");
            @(negedge clk);
            run_enable = 1'b0;
            clear_safe = 1'b1;
            #1;
            must(clear_rejected, "协议隔离状态不得通过普通clear恢复");
            tick();
            clear_safe = 1'b0;
            must(protocol_isolated && !ledger_empty,
                 "普通clear不得解除协议隔离");
            directed_cases++;
        end
    endtask

    initial begin
        test_guard_bounds();
        reset_case();
        run_read(32'h0100_0000, 8);
        reset_case();
        run_read(32'h0100_0000, 128);
        reset_case();
        run_read(32'h0100_0ff8, 16);
        reset_case();
        run_write(32'h0100_0000, 8);
        reset_case();
        run_write(32'h0100_0000, 128);
        reset_case();
        run_write(32'h0100_0ff8, 16);
        reset_case();
        test_early_rejection(32'h0100_0000, 8'd4, 3'd1);
        reset_case();
        test_early_rejection(32'h0100_0001, 8'd8, 3'd1);
        reset_case();
        test_early_rejection(32'h0100_0000, 8'd12, 3'd1);
        reset_case();
        test_early_rejection(32'h0007_ec00, 8'd8, 3'd2);
        reset_case();
        test_early_rejection(32'h0115_1ff8, 8'd16, 3'd2);
        reset_case();
        test_read_response_error();
        reset_case();
        test_bad_rlast_isolates();
        reset_case();
        test_bad_rid_isolates();
        reset_case();
        test_early_b_fault();
        reset_case();
        test_bad_bid_isolates();
        reset_case();
        test_cancel_ar_stalled();
        reset_case();
        test_cancel_read_waiting_r();
        reset_case();
        test_cancel_read_delivery();
        reset_case();
        test_cancel_done_backpressure();
        reset_case();
        test_cancel_partial_write_and_delayed_b();
        reset_case();
        test_epoch_change_and_busy_clear();
        reset_case();
        test_cancel_before_write_axi();
        $display("PASS RTL07 BULK BRIDGE directed_cases=%0d random_samples=0",
                 directed_cases);
        $finish;
    end
endmodule
