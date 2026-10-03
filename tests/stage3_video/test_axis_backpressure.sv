`timescale 1ns/1ps
module test_axis_backpressure;
    logic clk = 1'b0;
    logic cmos_vsync = 1'b0;
    logic cmos_href = 1'b0;
    logic [9:0] cmos_d = 10'd0;
    logic m_axis_video_tready = 1'b0;
    wire [15:0] m_axis_video_tdata;
    wire m_axis_video_tvalid;
    wire m_axis_video_tuser;
    wire m_axis_video_tlast;
    wire [1:0] m_axis_video_tkeep;

    logic [17:0] expected_words [0:63];
    integer expected_count = 0;
    integer expected_user_count = 0;
    integer expected_last_count = 0;
    integer index;
    integer pop_count_at_stall;
    logic [17:0] held_word;

    always #5 clk = ~clk;

    alinx_ov5640 #(
        .BUFFER_DEPTH(32),
        .DEBUG_OV5640(0)
    ) dut (
        .cmos_vsync(cmos_vsync),
        .cmos_href(cmos_href),
        .cmos_pclk(clk),
        .cmos_d(cmos_d),
        .m_axis_video_aclk(clk),
        .m_axis_video_aresetn(1'b1),
        .m_axis_video_tdata(m_axis_video_tdata),
        .m_axis_video_tvalid(m_axis_video_tvalid),
        .m_axis_video_tready(m_axis_video_tready),
        .m_axis_video_tuser(m_axis_video_tuser),
        .m_axis_video_tlast(m_axis_video_tlast),
        .m_axis_video_tkeep(m_axis_video_tkeep)
    );

    always @(posedge clk) begin
        if (dut.xpm_fifo_async_inst.wr_en === 1'b1 &&
            dut.xpm_fifo_async_inst.full === 1'b0) begin
            if (expected_count >= 64) $fatal(1, "测试记分板容量不足");
            expected_words[expected_count] <= dut.xpm_fifo_async_inst.din;
            expected_count <= expected_count + 1;
            if (dut.xpm_fifo_async_inst.din[0]) expected_user_count <= expected_user_count + 1;
            if (dut.xpm_fifo_async_inst.din[1]) expected_last_count <= expected_last_count + 1;
        end
    end

    task automatic send_byte(input logic [7:0] value);
        begin
            @(negedge clk);
            cmos_href = 1'b1;
            cmos_d = {value, 2'b00};
            @(posedge clk);
        end
    endtask

    task automatic finish_line;
        begin
            @(negedge clk);
            cmos_href = 1'b0;
            cmos_d = 10'd0;
            repeat (8) @(posedge clk);
        end
    endtask

    initial begin
        force dut.cmos_aresetn = 1'b0;
        force dut.fifo_ready = 1'b0;
        repeat (4) @(posedge clk);
        @(negedge clk);
        force dut.cmos_aresetn = 1'b1;
        force dut.fifo_ready = 1'b1;
        repeat (6) @(posedge clk);

        cmos_vsync = 1'b1;
        repeat (5) @(posedge clk);
        @(negedge clk);
        cmos_vsync = 1'b0;
        repeat (4) @(posedge clk);

        for (index = 0; index < 8; index = index + 1) send_byte(8'h10 + index);
        finish_line();
        for (index = 0; index < 8; index = index + 1) send_byte(8'h30 + index);
        finish_line();
        for (index = 0; index < 8; index = index + 1) send_byte(8'h50 + index);
        finish_line();
        repeat (5) @(posedge clk);
        @(negedge clk);

        if (expected_count < 8) $fatal(1, "未能积累足够的真实 RTL 输出拍：%0d", expected_count);
        if (expected_count >= 32) $fatal(1, "测试输入超过 FIFO 容量：%0d", expected_count);
        if (expected_user_count == 0) $fatal(1, "测试输入未产生 TUSER 标记");
        if (expected_last_count == 0) $fatal(1, "测试输入未产生 TLAST 标记");
        if (dut.xpm_fifo_async_inst.occupancy != expected_count) begin
            $fatal(1, "写入记分板与 FIFO 深度不一致：%0d/%0d",
                   expected_count, dut.xpm_fifo_async_inst.occupancy);
        end
        if (m_axis_video_tready !== 1'b0) $fatal(1, "背压阶段 TREADY 必须为 0");
        if (m_axis_video_tvalid !== 1'b1) begin
            $fatal(1, "非空 FIFO 且接收端未就绪时 TVALID 未保持为 1");
        end
        if (dut.xpm_fifo_async_inst.rd_en !== 1'b0) $fatal(1, "背压阶段 FIFO 不应弹出");

        held_word = {m_axis_video_tdata, m_axis_video_tlast, m_axis_video_tuser};
        pop_count_at_stall = dut.xpm_fifo_async_inst.pop_count;
        repeat (6) begin
            @(posedge clk);
            #1;
            if (m_axis_video_tvalid !== 1'b1) $fatal(1, "背压时 TVALID 撤销");
            if ({m_axis_video_tdata, m_axis_video_tlast, m_axis_video_tuser} !== held_word) begin
                $fatal(1, "背压时 TDATA/TLAST/TUSER 未保持稳定");
            end
            if (dut.xpm_fifo_async_inst.rd_en !== 1'b0) $fatal(1, "背压时出现 FIFO 读使能");
            if (dut.xpm_fifo_async_inst.pop_count != pop_count_at_stall) begin
                $fatal(1, "背压时 FIFO 弹出计数改变");
            end
        end

        for (index = 0; index < expected_count; index = index + 1) begin
            @(negedge clk);
            m_axis_video_tready = 1'b1;
            #1;
            if (m_axis_video_tvalid !== 1'b1) begin
                $fatal(1, "排空第 %0d 拍时 TVALID 未置位", index);
            end
            if ({m_axis_video_tdata, m_axis_video_tlast, m_axis_video_tuser} !== expected_words[index]) begin
                $fatal(1, "排空第 %0d 拍与 FIFO 写入顺序/内容不一致", index);
            end
            if (dut.xpm_fifo_async_inst.rd_en !== 1'b1) begin
                $fatal(1, "握手第 %0d 拍没有产生 FIFO 读使能", index);
            end
            @(posedge clk);
            #1;
            if (dut.xpm_fifo_async_inst.pop_count != index + 1) begin
                $fatal(1, "第 %0d 次握手未恰好弹出一项", index);
            end
        end

        @(negedge clk);
        m_axis_video_tready = 1'b0;
        #1;
        if (dut.xpm_fifo_async_inst.empty !== 1'b1) $fatal(1, "排空后 FIFO 仍非空");
        if (m_axis_video_tvalid !== 1'b0) $fatal(1, "FIFO 空时 TVALID 必须为 0");
        if (dut.xpm_fifo_async_inst.pop_count != expected_count) begin
            $fatal(1, "最终弹出总数与写入数不一致");
        end
        if (m_axis_video_tkeep !== 2'b11) $fatal(1, "TKEEP 常量异常");
        $display("PASS beats=%0d stalled_cycles=6 fifo_pops=%0d tuser=%0d tlast=%0d",
                 expected_count, dut.xpm_fifo_async_inst.pop_count,
                 expected_user_count, expected_last_count);
        $finish;
    end

    initial begin
        #200000;
        $fatal(1, "测试台超时");
    end
endmodule
