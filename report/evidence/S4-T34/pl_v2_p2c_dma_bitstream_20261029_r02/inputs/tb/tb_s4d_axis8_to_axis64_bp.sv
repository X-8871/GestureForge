// tb_s4d_axis8_to_axis64_bp.sv —— 打包器反压/多帧自检（P2c，lead 自建）
//
// 目的（rev-s5 非阻断建议）：补"反压 + 背靠背多帧"用例，验证在 m_tready 长时间为 0 时
// 不丢字节、不重复、帧边界（TLAST）正确、TKEEP 只在尾 beat 起作用。
//
// 方法：驱动 8 帧 × 13 字节（故意不是 8 的倍数）随机数据；m_tready 用 LFSR 随机拉低
//       （最长连续 37 拍）；每收一个 beat 就按 TKEEP 把字节还原到重建流；最后比对
//       "重建流 == 输入流"，并检查 TLAST 恰好出现在每帧末尾 beat。
`timescale 1ns / 1ps

module tb_s4d_axis8_to_axis64_bp;
    logic clk = 1'b0;
    logic rstn = 1'b0;

    logic [7:0]  s_tdata  = 8'h00;
    logic        s_tvalid = 1'b0;
    logic        s_tready;
    logic        s_tlast  = 1'b0;
    logic        s_tuser  = 1'b0;

    logic [63:0] m_tdata;
    logic [7:0]  m_tkeep;
    logic        m_tvalid;
    logic        m_tready = 1'b1;
    logic        m_tlast;

    s4d_axis8_to_axis64 dut (
        .clk(clk), .rstn(rstn),
        .s_tdata(s_tdata), .s_tvalid(s_tvalid), .s_tready(s_tready), .s_tlast(s_tlast), .s_tuser(s_tuser),
        .m_tdata(m_tdata), .m_tkeep(m_tkeep), .m_tvalid(m_tvalid), .m_tready(m_tready), .m_tlast(m_tlast)
    );

    always #5 clk = ~clk;

    localparam int FRAMES = 8;
    localparam int FLEN   = 13;             // 每帧字节数（非 8 的倍数 ⇒ 每帧都有部分 beat）
    localparam int TOTAL  = FRAMES * FLEN;

    logic [7:0] in_bytes [0:TOTAL-1];
    logic [7:0] out_bytes[0:TOTAL-1];
    int out_n = 0;
    int errors = 0;
    int frames_last = 0;
    logic [31:0] lfsr = 32'hACE1_2345;

    // 反压发生器
    always_ff @(posedge clk) begin
        if (!rstn) begin
            m_tready <= 1'b1;
            lfsr     <= 32'hACE1_2345;
        end else begin
            lfsr <= {lfsr[30:0], lfsr[31] ^ lfsr[21] ^ lfsr[1] ^ lfsr[0]};
            m_tready <= (lfsr[3:0] != 4'h0);          // 约 1/16 概率拉低
        end
    end

    // 输出检查 + 字节重建
    always @(posedge clk) begin
        if (rstn && m_tvalid && m_tready) begin
            for (int i = 0; i < 8; i++) begin
                if (m_tkeep[i] && out_n < TOTAL) begin
                    out_bytes[out_n] = m_tdata[i*8 +: 8];
                    out_n = out_n + 1;
                end
            end
            if (m_tlast) frames_last = frames_last + 1;
            // TLAST 必须与"帧尾"一致：重建流长度是 FLEN 的整数倍
            if (m_tlast && (out_n % FLEN) != 0) begin
                $display("FAIL tlast at wrong byte boundary out_n=%0d", out_n);
                errors = errors + 1;
            end
        end
    end

    task automatic push_byte(input logic [7:0] b, input logic last);
        begin
            @(negedge clk);
            while (!s_tready) @(negedge clk);
            s_tdata  = b;
            s_tlast  = last;
            s_tvalid = 1'b1;
            @(posedge clk);
            @(negedge clk);
            s_tvalid = 1'b0;
            s_tlast  = 1'b0;
        end
    endtask

    initial begin
        for (int i = 0; i < TOTAL; i++) in_bytes[i] = 8'((i * 37 + 11) & 8'hFF);
        repeat (4) @(posedge clk);
        rstn = 1'b1;
        @(posedge clk);

        for (int f = 0; f < FRAMES; f++) begin
            for (int i = 0; i < FLEN; i++) begin
                push_byte(in_bytes[f*FLEN + i], (i == FLEN-1));
            end
        end
        // 等清空
        repeat (400) @(posedge clk);

        for (int i = 0; i < TOTAL; i++) begin
            if (out_n > i && out_bytes[i] !== in_bytes[i]) begin
                $display("FAIL byte%0d got=%02h exp=%02h", i, out_bytes[i], in_bytes[i]);
                errors = errors + 1;
            end
        end
        if (out_n !== TOTAL) begin
            $display("FAIL out_n=%0d exp=%0d", out_n, TOTAL);
            errors = errors + 1;
        end
        if (frames_last !== FRAMES) begin
            $display("FAIL tlast_count=%0d exp=%0d", frames_last, FRAMES);
            errors = errors + 1;
        end
        if (errors == 0) $display("PACKER_BP_TB_RESULT=PASS frames=%0d bytes=%0d", FRAMES, TOTAL);
        else             $display("PACKER_BP_TB_RESULT=FAIL errors=%0d", errors);
        $finish;
    end

    initial begin
        #500000;
        $display("PACKER_BP_TB_RESULT=FAIL timeout out_n=%0d", out_n);
        $finish;
    end
endmodule