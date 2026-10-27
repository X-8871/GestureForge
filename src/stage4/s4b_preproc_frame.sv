// s4b_preproc_frame.sv —— 4-D PL 预处理首增量（BGR888 → RGB 字节序转换 + INT8 饱和打包）
//
// 本增量范围（诚实限定）：
//   · 输入 BGR888（tdata = {B,G,R}），输出 INT8 打包 RGB（tdata = {R8,G8,B8}）；
//   · 每分量 v → int8(v-128)，饱和到 [-128,127]；
//   · 单拍流式，1 周期延迟；tlast 直通；满/空握手由 s_ready/m_ready 决定；
//   · **未包含**几何 resize / pad 零填充 / 输出坐标计数 —— 这些属下一增量（ADR §8.4 寄存器已冻结），
//     本增量**不假装支持**，避免把未验证逻辑带进综合。
//
// 说明：本增量只做数据通路，AXI4-Lite（0x43C00200..0x27C）与 AXI4/HP0 接线需动 BD（新从机需互连、
//       HP0 为单 owner 需仲裁），属结构性改动，由项目总控批准后再动；本文件不包含 AXI 接口。

`timescale 1ns / 1ps

module s4b_preproc_frame (
    input  logic        clk,
    input  logic        rstn,

    // 输入：BGR888
    input  logic        s_valid,
    output logic        s_ready,
    input  logic [23:0] s_bgr,
    input  logic        s_last,

    // 输出：INT8 打包 RGB
    output logic        m_valid,
    input  logic        m_ready,
    output logic [23:0] m_rgb_int8,
    output logic        m_last,

    // 统计
    output logic [31:0] pixel_count
);

    logic        v_q;
    logic [23:0] d_q;
    logic        l_q;

    function automatic logic [7:0] to_int8(input logic [7:0] v);
        logic signed [8:0] t;
        t = $signed({1'b0, v}) - 9'sd128;   // -128..127
        if (t > 9'sd127)       to_int8 = 8'h7F;
        else if (t < -9'sd128) to_int8 = 8'h80;
        else                   to_int8 = t[7:0];
    endfunction

    logic [7:0] r8, g8, b8;
    assign r8 = to_int8(d_q[7:0]);     // 输入低字节 = R
    assign g8 = to_int8(d_q[15:8]);    // 中字节   = G
    assign b8 = to_int8(d_q[23:16]);   // 高字节   = B

    assign s_ready = !v_q || m_ready;

    always_ff @(posedge clk or negedge rstn) begin
        if (!rstn) begin
            v_q         <= 1'b0;
            d_q         <= 24'h000000;
            l_q         <= 1'b0;
            pixel_count <= 32'd0;
        end else if (s_ready) begin
            v_q <= s_valid;
            if (s_valid) begin
                d_q         <= s_bgr;
                l_q         <= s_last;
                pixel_count <= pixel_count + 32'd1;
            end
        end
    end

    assign m_valid    = v_q;
    assign m_rgb_int8 = {r8, g8, b8};
    assign m_last     = l_q;

endmodule