// ============================================================================
// tb_tuser_shaper.v —— tuser_shaper 的行为级 testbench（xsim）
//
// 激励：模拟 OV5640 -> RGB565->RGB888 converter 的输出流
//   - aclk = 100 MHz，每拍都可 tready
//   - 每帧 4 行（简化），每行 8 个 beat，行尾 tlast=1，帧间空隙 5 个 idle 拍
//   - sof_pulse：每帧开始前 1 拍（模拟 PCLK 域 vsync 下降沿同步过来的脉冲），
//     刻意让它落在 **tvalid=0 的帧间隙里**（这正是线上真实情形）
//
// 断言：
//   A1 每帧**恰好 1 次** tuser，且该拍 tvalid=1（AXIS 采样合法性）
//   A2 整形后 tuser 落在"帧首拍 tvalid"那一拍（即该帧第一个 tvalid 拍）
//   A3 a0_tuser2tlast == 每行 beat 数（8）
//   A4 a1_tlast2tuser == 0（帧间无多余 beat）
//   A5 b0_frame_beats == 每帧总 beat 数（4 行 × 8 = 32）
//   A6 b1_pending_stuck == 0
// ============================================================================
`timescale 1ns / 1ps

module tb_tuser_shaper;

    localparam integer LINES_PER_FRAME = 4;
    localparam integer BEATS_PER_LINE  = 8;
    localparam integer FRAMES          = 3;

    reg         aclk = 1'b0;
    reg         aresetn = 1'b0;
    reg         sof_pulse = 1'b0;
    reg         tvalid = 1'b0;
    reg         tready = 1'b1;
    reg         tlast  = 1'b0;
    wire        tuser;
    wire [31:0] a0, a1, b0, b1, c0;

    integer frame_cnt   = 0;
    integer tuser_cnt   = 0;
    integer tuser_xfer  = 0;
    integer errs = 0;

    // ---- DUT ----
    tuser_shaper #(.TUSER_MODE(1)) dut (
        .aclk            (aclk),
        .aresetn         (aresetn),
        .sof_pulse       (sof_pulse),
        .tvalid          (tvalid),
        .tready          (tready),
        .tlast           (tlast),
        .tuser           (tuser),
        .a0_tuser2tlast  (a0),
        .a1_tlast2tuser  (a1),
        .b0_frame_beats  (b0),
        .b1_pending_stuck(b1),
        .c0_misalign_cnt(c0)
    );


    // ---- 100 MHz 时钟 ----
    always #5 aclk = ~aclk;


    // ---- 激励（全部在 negedge 驱动与采样，避免与 DUT 同沿竞争）----
    integer i, j, k;
    initial begin
        $dumpfile("tb_tuser_shaper.vcd");
        $dumpvars(0, tb_tuser_shaper);
        repeat (5) @(negedge aclk);
        aresetn = 1'b1;
        repeat (2) @(negedge aclk);

        for (k = 0; k < FRAMES; k = k + 1) begin
            // 帧间隙：tvalid=0；SOF 脉冲出现在这里（模拟 vsync 下降沿早于首行数据）
            repeat (2) @(negedge aclk);
            sof_pulse = 1'b1;
            @(negedge aclk);
            sof_pulse = 1'b0;
            repeat (2) @(negedge aclk);

            frame_cnt = frame_cnt + 1;

            for (i = 0; i < LINES_PER_FRAME; i = i + 1) begin
                for (j = 0; j < BEATS_PER_LINE; j = j + 1) begin
                    tvalid = 1'b1;
                    tlast  = (j == BEATS_PER_LINE - 1);
                    #1;                      // 组合稳定后采样（此时是 beat 传输前的半周期）
                    if ((i == 0) && (j == 0)) begin
                        // ★ 同拍断言：帧首拍（tvalid&tready 有效的同一拍）tuser 必须为 1
                        if (!tuser) begin
                            $display("[%0t] ASSERT FAIL: 帧首拍没有 tuser（晚/早 1 拍）", $time);
                            errs = errs + 1;
                        end
                    end else begin
                        if (tuser) begin
                            $display("[%0t] ASSERT FAIL: tuser 出现在非帧首拍 (line=%0d beat=%0d)", $time, i, j);
                            errs = errs + 1;
                        end
                    end
                    if (tuser && tvalid && tready) tuser_xfer <= tuser_xfer + 1;
                    @(negedge aclk);
                    tvalid = 1'b0; tlast = 1'b0;
                    #1;
                    // ★ 下一拍断言：tuser 必须已回 0（不得比首拍晚 1 拍）
                    if (tuser) begin
                        $display("[%0t] ASSERT FAIL: tuser 在下一拍仍为高（晚 1 拍/多拍）", $time);
                        errs = errs + 1;
                    end
                    @(negedge aclk);
                end
            end
            repeat (3) @(negedge aclk);
        end

        repeat (10) @(negedge aclk);
        $display("-------------------------------------------------------------");
        $display("frame_cnt            = %0d (期望 %0d)", frame_cnt, FRAMES);
        $display("tuser_xfer(有效拍)    = %0d (期望 %0d)", tuser_xfer, FRAMES);
        $display("a0 tuser->首tlast     = %0d (期望 %0d)", a0, BEATS_PER_LINE);
        $display("a1 末tlast->tuser     = %0d (期望 0)", a1);
        $display("b0 每帧总 beat        = %0d (期望 %0d)", b0, LINES_PER_FRAME * BEATS_PER_LINE);
        $display("b1 pending 卡住       = %0d (期望 0)", b1);
        $display("c0 错拍(tuser&!tvalid) = %0d (期望 0)", c0);
        if (tuser_xfer != FRAMES)                  begin $display("ASSERT FAIL: tuser 有效拍数不符"); errs = errs + 1; end
        if (a0 != BEATS_PER_LINE)                  begin $display("ASSERT FAIL: a0 != 每行 beat 数"); errs = errs + 1; end
        if (a1 != 0)                               begin $display("ASSERT FAIL: a1 != 0"); errs = errs + 1; end
        if (b0 != LINES_PER_FRAME * BEATS_PER_LINE) begin $display("ASSERT FAIL: b0 != 每帧 beat 数"); errs = errs + 1; end
        if (b1 != 0)                               begin $display("ASSERT FAIL: b1 != 0"); errs = errs + 1; end
        if (c0 != 0)                               begin $display("ASSERT FAIL: c0 != 0（存在错拍）"); errs = errs + 1; end
        $display("-------------------------------------------------------------");
        if (errs == 0) $display("TB_RESULT: PASS");
        else           $display("TB_RESULT: FAIL (%0d errors)", errs);
        $finish;
    end

    // 超时保护
    initial begin
        #2000000;
        $display("TB_RESULT: TIMEOUT");
        $finish;
    end

endmodule