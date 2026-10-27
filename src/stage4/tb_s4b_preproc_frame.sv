// tb_s4b_preproc_frame.sv —— 自检型 testbench（xsim 轻量；失败即 $fatal，禁止进入综合）
//
// 覆盖：BGR→RGB 字节序、INT8 饱和（0x00→-128、0xFF→+127、0x80→0、中间值）、tlast 直通、计数。
// 本增量不含几何/pad（DUT 未实现，TB 也不假装覆盖）。

`timescale 1ns / 1ps

module tb_s4b_preproc_frame;
    logic clk = 0, rstn = 0;
    logic s_valid = 0, s_last = 0, s_ready;
    logic [23:0] s_bgr = 24'h000000;
    logic m_valid, m_ready = 1, m_last;
    logic [23:0] m_rgb_int8;
    logic [31:0] pixel_count;

    localparam int N = 6;
    logic [23:0] vec_bgr [0:N-1];
    logic [23:0] vec_exp [0:N-1];
    logic        vec_last[0:N-1];

    initial begin
        // 输入（BGR 存储顺序），期望输出（{R8,G8,B8}）
        vec_bgr[0] = 24'h102030; vec_exp[0] = {8'hB0, 8'hA0, 8'h90}; // 0x10-128=-112=0x90(B)…
        vec_bgr[1] = 24'h00FF80; vec_exp[1] = {8'h00, 8'h7F, 8'h80}; // R=0x80→0, G=0xFF→127, B=0x00→-128
        vec_bgr[2] = 24'hFFFFFF; vec_exp[2] = 24'h7F7F7F;            // 全饱和上界
        vec_bgr[3] = 24'h000000; vec_exp[3] = 24'h808080;            // 全饱和下界
        vec_bgr[4] = 24'h807F81; vec_exp[4] = 24'h01FF00;            // r=0x81→1, g=0x7F→-1=0xFF, b=0x80→0
        vec_bgr[5] = 24'h010203; vec_exp[5] = 24'h838281;            // r=0x03→-125=0x83, g=0x02→0x82, b=0x01→0x81
        vec_last[0] = 0; vec_last[1] = 0; vec_last[2] = 0;
        vec_last[3] = 0; vec_last[4] = 0; vec_last[5] = 1;
    end

    s4b_preproc_frame dut (
        .clk(clk), .rstn(rstn),
        .s_valid(s_valid), .s_ready(s_ready), .s_bgr(s_bgr), .s_last(s_last),
        .m_valid(m_valid), .m_ready(m_ready), .m_rgb_int8(m_rgb_int8), .m_last(m_last),
        .pixel_count(pixel_count)
    );

    always #5 clk = ~clk;

    int errors = 0;
    int out_idx = 0;

    // 输出检查
    always @(posedge clk) begin
        if (rstn && m_valid && m_ready) begin
            if (m_rgb_int8 !== vec_exp[out_idx]) begin
                errors++;
                $display("[FAIL] out#%0d got=%06h exp=%06h", out_idx, m_rgb_int8, vec_exp[out_idx]);
            end
            if (m_last !== vec_last[out_idx]) begin
                errors++;
                $display("[FAIL] out#%0d tlast got=%0b exp=%0b", out_idx, m_last, vec_last[out_idx]);
            end
            out_idx++;
        end
    end

    // 输入驱动
    initial begin
        int i;
        @(posedge rstn);
        for (i = 0; i < N; i++) begin
            @(negedge clk);
            s_bgr   = vec_bgr[i];
            s_last  = vec_last[i];
            s_valid = 1;
            do @(posedge clk); while (!s_ready);
            @(negedge clk);
            s_valid = 0;
        end
    end

    // 主控
    initial begin
        rstn = 0;
        repeat (4) @(posedge clk);
        rstn = 1;
        fork
            begin : wait_all
                wait (out_idx == N);
                repeat (4) @(posedge clk);
            end
            begin : timeout
                repeat (2000) @(posedge clk);
                $display("[FAIL] 超时：只输出 %0d/%0d", out_idx, N);
                errors++;
            end
        join_any
        disable fork;

        if (out_idx != N) begin
            errors++;
            $display("[FAIL] 输出像素数 got=%0d exp=%0d", out_idx, N);
        end
        if (pixel_count != N) begin
            errors++;
            $display("[FAIL] pixel_count got=%0d exp=%0d", pixel_count, N);
        end
        if (errors == 0) begin
            $display("[PASS] s4b_preproc_frame：%0d 像素全部匹配（BGR→RGB、INT8 饱和、tlast、计数）", out_idx);
            $finish(0);
        end else begin
            $display("[FAIL] 共 %0d 处不匹配", errors);
            $fatal(1);
        end
    end
endmodule
