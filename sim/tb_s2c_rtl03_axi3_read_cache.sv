`timescale 1ns/1ps
module tb_s2c_rtl03_axi3_read_cache;
    logic clk = 1'b0;
    always #5 clk = ~clk;

    logic rst = 1'b1;
    logic cancel = 1'b0;
    logic cache_invalidate = 1'b0;
    logic req_valid = 1'b0;
    logic req_ready;
    logic [31:0] req_addr = 0;
    logic [31:0] region_begin = 0;
    logic [31:0] region_end = 0;
    logic rsp_valid;
    logic rsp_ready = 1'b0;
    logic [7:0] rsp_data;
    logic rsp_error;
    logic [5:0] m_axi_arid;
    logic [31:0] m_axi_araddr;
    logic [3:0] m_axi_arlen;
    logic [2:0] m_axi_arsize;
    logic [1:0] m_axi_arburst;
    logic m_axi_arvalid;
    logic m_axi_arready = 1'b0;
    logic [5:0] m_axi_rid = 0;
    logic [63:0] m_axi_rdata = 0;
    logic [1:0] m_axi_rresp = 0;
    logic m_axi_rlast = 0;
    logic m_axi_rvalid = 0;
    logic m_axi_rready;
    logic protocol_fault;
    integer checks = 0;

    s2c_axi3_read_cache dut (.*);

    task automatic start_request(input logic [31:0] address,
                                 input logic [31:0] first,
                                 input logic [31:0] last);
        begin
            @(negedge clk);
            req_addr = address;
            region_begin = first;
            region_end = last;
            req_valid = 1'b1;
            do @(posedge clk); while (!req_ready);
            @(negedge clk);
            req_valid = 1'b0;
        end
    endtask

    task automatic accept_ar(input logic [31:0] address,
                             input logic [3:0] length,
                             input logic [2:0] size);
        begin
            wait (m_axi_arvalid);
            #1;
            if (m_axi_arid != 0 || m_axi_araddr !== address ||
                m_axi_arlen !== length || m_axi_arsize !== size ||
                m_axi_arburst != 2'b01) $fatal(1, "AR 元数据或 4KiB/区域切分错误");
            checks = checks + 1;
            @(negedge clk);
            m_axi_arready = 1'b1;
            @(posedge clk);
            @(negedge clk);
            m_axi_arready = 1'b0;
        end
    endtask

    task automatic send_beats(input integer count,
                              input logic [31:0] base,
                              input integer wrong_id_beat,
                              input integer wrong_last_beat);
        logic [63:0] word_data;
        begin
            for (integer beat = 0; beat < count; beat++) begin
                for (integer lane = 0; lane < 8; lane++)
                    word_data[lane*8 +: 8] = (base + beat*8 + lane) & 8'hff;
                @(negedge clk);
                m_axi_rid = (beat == wrong_id_beat) ? 6'd1 : 6'd0;
                m_axi_rdata = word_data;
                m_axi_rresp = 2'b00;
                m_axi_rlast = (beat == count-1);
                if (beat == wrong_last_beat) m_axi_rlast = !m_axi_rlast;
                m_axi_rvalid = 1'b1;
                @(posedge clk);
                @(negedge clk);
                m_axi_rvalid = 1'b0;
            end
        end
    endtask

    task automatic consume_response(input logic [7:0] expected,
                                    input logic expected_error);
        begin
            wait (rsp_valid);
            #1;
            if (rsp_data !== expected || rsp_error !== expected_error)
                $fatal(1, "读响应错误 expected=%h actual=%h err=%b", expected, rsp_data, rsp_error);
            checks = checks + 1;
            @(negedge clk);
            rsp_ready = 1'b1;
            @(posedge clk);
            @(negedge clk);
            rsp_ready = 1'b0;
        end
    endtask

    initial begin
        repeat (3) @(posedge clk);
        @(negedge clk);
        rst = 1'b0;

        // 对齐后的 16 beat 预取与同 cache line 命中。
        start_request(32'h0000_1003, 32'h0000_1000, 32'h0000_1100);
        accept_ar(32'h0000_1000, 4'd15, 3'd3);
        send_beats(16, 32'h0000_1000, -1, -1);
        consume_response(8'h03, 1'b0);
        start_request(32'h0000_1007, 32'h0000_1000, 32'h0000_1100);
        consume_response(8'h07, 1'b0);

        // 写入或epoch/SAFE变化后无效化旧cache，再次读取必须发起新AR。
        @(negedge clk);
        cache_invalidate = 1'b1;
        @(posedge clk);
        @(negedge clk);
        cache_invalidate = 1'b0;
        start_request(32'h0000_1007, 32'h0000_1000, 32'h0000_1100);
        accept_ar(32'h0000_1000, 4'd15, 3'd3);
        send_beats(16, 32'h0000_1000, -1, -1);
        consume_response(8'h07, 1'b0);

        // 即使本请求只有一个 beat，只要完整 8B beat 位于授权区间内，也必须使用 SIZE=3。
        start_request(32'h0000_1103, 32'h0000_1100, 32'h0000_1108);
        accept_ar(32'h0000_1100, 4'd0, 3'd3);
        send_beats(1, 32'h0000_1100, -1, -1);
        consume_response(8'h03, 1'b0);

        // cache_invalidate 与命中请求同拍时不得握手；撤销失效后必须重新发起总线读。
        @(negedge clk);
        req_addr = 32'h0000_1007;
        region_begin = 32'h0000_1000;
        region_end = 32'h0000_1100;
        req_valid = 1'b1;
        cache_invalidate = 1'b1;
        #1;
        if (req_ready) $fatal(1, "失效同拍错误接受请求");
        @(posedge clk);
        @(negedge clk);
        cache_invalidate = 1'b0;
        do @(posedge clk); while (!req_ready);
        @(negedge clk);
        req_valid = 1'b0;
        accept_ar(32'h0000_1000, 4'd15, 3'd3);
        send_beats(16, 32'h0000_1000, -1, -1);
        consume_response(8'h07, 1'b0);

        // 4KiB 边界：突发在页尾结束，不跨页。
        start_request(32'h0000_2ff4, 32'h0000_2000, 32'h0000_4000);
        accept_ar(32'h0000_2ff0, 4'd1, 3'd3);
        send_beats(2, 32'h0000_2ff0, -1, -1);
        consume_response(8'hf4, 1'b0);

        // 对象尾部不足 8B 时退化成单 byte 访问，不能越过授权区间。
        start_request(32'h0000_30fd, 32'h0000_3000, 32'h0000_30fe);
        accept_ar(32'h0000_30fd, 4'd0, 3'd0);
        send_beats(1, 32'h0000_30f8, -1, -1);
        consume_response(8'hfd, 1'b0);

        // 32-bit 地址空间末页的页界计算饱和，且 beat 末端溢出时退化为窄读。
        start_request(32'hffff_fff8, 32'hffff_f000, 32'hffff_ffff);
        accept_ar(32'hffff_fff8, 4'd0, 3'd0);
        send_beats(1, 32'hffff_fff8, -1, -1);
        consume_response(8'hf8, 1'b0);

        // 取消期间必须完整排空已接受的 burst，且不返回陈旧响应。
        start_request(32'h0000_5000, 32'h0000_5000, 32'h0000_5100);
        accept_ar(32'h0000_5000, 4'd15, 3'd3);
        @(negedge clk);
        cancel = 1'b1;
        send_beats(16, 32'h0000_5000, -1, -1);
        @(negedge clk);
        cancel = 1'b0;
        repeat (2) @(posedge clk);
        if (rsp_valid || protocol_fault || !req_ready) $fatal(1, "取消排空后状态未闭合");
        checks = checks + 1;

        // 错误响应末 beat 与 cancel 同拍到达时仍须排空并回到 IDLE。
        start_request(32'h0000_8000, 32'h0000_8000, 32'h0000_8100);
        accept_ar(32'h0000_8000, 4'd15, 3'd3);
        send_beats(15, 32'h0000_8000, -1, 14);
        @(negedge clk);
        cancel = 1'b1;
        m_axi_rid = 6'd0;
        m_axi_rresp = 2'b10;
        m_axi_rlast = 1'b1;
        m_axi_rvalid = 1'b1;
        @(posedge clk);
        @(negedge clk);
        cancel = 1'b0;
        m_axi_rresp = 2'b00;
        m_axi_rlast = 1'b0;
        m_axi_rvalid = 1'b0;
        repeat (2) @(posedge clk);
        if (rsp_valid || protocol_fault || !req_ready) $fatal(1, "错误末 beat/cancel 后状态未闭合");
        checks = checks + 1;

        // 错误响应末 beat 与 cache_invalidate 同拍到达时不得残留失效等待态。
        start_request(32'h0000_9000, 32'h0000_9000, 32'h0000_9100);
        accept_ar(32'h0000_9000, 4'd15, 3'd3);
        send_beats(15, 32'h0000_9000, -1, 14);
        @(negedge clk);
        cache_invalidate = 1'b1;
        m_axi_rid = 6'd0;
        m_axi_rresp = 2'b10;
        m_axi_rlast = 1'b1;
        m_axi_rvalid = 1'b1;
        @(posedge clk);
        @(negedge clk);
        cache_invalidate = 1'b0;
        m_axi_rresp = 2'b00;
        m_axi_rlast = 1'b0;
        m_axi_rvalid = 1'b0;
        repeat (2) @(posedge clk);
        if (rsp_valid || protocol_fault || !req_ready) $fatal(1, "错误末 beat/invalidate 后状态未闭合");
        checks = checks + 1;

        // 错误 ID 必须隔离并置 protocol_fault。
        start_request(32'h0000_6000, 32'h0000_6000, 32'h0000_6100);
        accept_ar(32'h0000_6000, 4'd15, 3'd3);
        send_beats(16, 32'h0000_6000, 0, -1);
        repeat (2) @(posedge clk);
        if (!protocol_fault || rsp_valid) $fatal(1, "错误 RID 未隔离");
        checks = checks + 1;

        @(negedge clk);
        rst = 1'b1;
        repeat (2) @(posedge clk);
        @(negedge clk);
        rst = 1'b0;
        start_request(32'h0000_7000, 32'h0000_7000, 32'h0000_7100);
        accept_ar(32'h0000_7000, 4'd15, 3'd3);
        send_beats(16, 32'h0000_7000, -1, 15);
        repeat (2) @(posedge clk);
        if (!protocol_fault || rsp_valid) $fatal(1, "错误 RLAST 未隔离");
        checks = checks + 1;

        $display("PASS S2C-RTL03 AXI3 burst/cache checks=%0d", checks);
        $finish;
    end
endmodule
