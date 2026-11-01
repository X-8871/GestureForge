// ============================================================================
// axis_to_video.v —— P3p：AXIS 数据自建 720p60 时序 + tlast 诊断
//                    （替代 BD 里的 v_tc + v_axi4s_vid_out）
//
// 相对 P3m/P3n 的改动（P3p）：
//   1) 新增 `tlast_misalign` 计数：tlast 出现在"非帧末像素"位置时 +1
//      —— 用于判断 VDMA 的帧边界与显示的帧边界是否对齐（fsync 生效后应稳定）
//   2) 欠载语义不变：de=1 且 tvalid=0 ⇒ 输出黑 24'h000000（不残留上一像素）+ uf_pixels++
//
// 时序参数与 COLOR_BAR/P3k 一致（720p60，全正极性）：
//   H: ACTIVE=1280 FP=110 SYNC=40 BP=220 -> TOTAL=1650
//   V: ACTIVE=720  FP=5   SYNC=5  BP=20  -> TOTAL=750
//
// 时钟域：**本模块完全在像素时钟域**（pixel_clk）。
//   VDMA 的 m_axis_mm2s_aclk 也接同一个 pixel_clk（见 BD）⇒ 这里没有跨时钟域；
//   50 MHz(MM 侧) <-> 74.21875(流侧) 的跨域由 VDMA **内部**行缓冲完成（ASYNC 模式）。
// ============================================================================
`timescale 1ns / 1ps

module axis_to_video #(
    parameter H_ACTIVE = 1280,
    parameter H_FP     = 110,
    parameter H_SYNC   = 40,
    parameter H_BP     = 220,
    parameter V_ACTIVE = 720,
    parameter V_FP     = 5,
    parameter V_SYNC   = 5,
    parameter V_BP     = 20
) (
    input  wire        pixel_clk,
    input  wire        rst,            // 高有效，像素域（顶层给 ~locked）

    // ---- AXI4-Stream slave（来自 VDMA M_AXIS_MM2S，**同一像素时钟域**）----
    input  wire [31:0] s_axis_tdata,
    input  wire        s_axis_tvalid,
    input  wire        s_axis_tlast,
    output wire        s_axis_tready,

    // ---- 视频输出（给 rgb2dvi）----
    output wire        hs,
    output wire        vs,
    output wire        de,
    output wire [23:0] rgb,

    // ---- 诊断（像素域，单调递增，便于格雷码跨域）----
    output reg  [31:0] uf_pixels,      // 累计欠载像素数（sticky，不清零）
    output reg  [31:0] tlast_misalign  // tlast 出现在非帧末位置 的次数
);

    localparam H_TOTAL = H_ACTIVE + H_FP + H_SYNC + H_BP;   // 1650
    localparam V_TOTAL = V_ACTIVE + V_FP + V_SYNC + V_BP;   // 750
    localparam H_START = H_FP + H_SYNC + H_BP;              // 370（有效像素起点）
    localparam V_START = V_FP + V_SYNC + V_BP;              // 30 （有效行起点）

    reg [11:0] h_cnt;
    reg [11:0] v_cnt;

    wire hs_comb = (h_cnt >= H_FP) && (h_cnt < H_FP + H_SYNC);
    wire vs_comb = (v_cnt >= V_FP) && (v_cnt < V_FP + V_SYNC);

    wire in_active = (h_cnt >= H_START) && (h_cnt < H_START + H_ACTIVE) &&
                     (v_cnt >= V_START) && (v_cnt < V_START + V_ACTIVE);

    // 帧的最后一个有效像素（tlast 应当出现在这里）
    wire at_last_pixel = in_active &&
                         (h_cnt == H_START + H_ACTIVE - 1) &&
                         (v_cnt == V_START + V_ACTIVE - 1);

    // ---------------- 行/场计数 ----------------
    always @(posedge pixel_clk or posedge rst) begin
        if (rst) begin
            h_cnt <= 12'd0;
            v_cnt <= 12'd0;
        end else begin
            if (h_cnt == H_TOTAL - 1) begin
                h_cnt <= 12'd0;
                if (v_cnt == V_TOTAL - 1)
                    v_cnt <= 12'd0;
                else
                    v_cnt <= v_cnt + 12'd1;
            end else begin
                h_cnt <= h_cnt + 12'd1;
            end
        end
    end

    // ---------------- 像素消费 ----------------
    assign s_axis_tready = in_active;

    reg        de_r, hs_r, vs_r;
    reg [23:0] rgb_r;

    always @(posedge pixel_clk or posedge rst) begin
        if (rst) begin
            de_r      <= 1'b0;
            hs_r      <= 1'b0;
            vs_r      <= 1'b0;
            rgb_r     <= 24'h000000;
            uf_pixels <= 32'd0;
        end else begin
            hs_r <= hs_comb;
            vs_r <= vs_comb;
            de_r <= in_active;
            if (in_active) begin
                if (s_axis_tvalid) begin
                    rgb_r <= s_axis_tdata[23:0];
                end else begin
                    // 欠载：输出黑色（不残留上一像素），并累计
                    rgb_r     <= 24'h000000;
                    uf_pixels <= uf_pixels + 32'd1;
                end
            end
        end
    end

    // ---------------- tlast 诊断：应在帧末像素处出现 ----------------
    always @(posedge pixel_clk or posedge rst) begin
        if (rst)
            tlast_misalign <= 32'd0;
        else if (s_axis_tlast && s_axis_tvalid && !at_last_pixel)
            tlast_misalign <= tlast_misalign + 32'd1;
    end

    assign hs  = hs_r;
    assign vs  = vs_r;
    assign de  = de_r;
    assign rgb = rgb_r;

endmodule