// ============================================================================
// tuser_shaper.v —— AXI-Stream SOF(tuser) 整形器（build11l）
//
// 作用：把"每帧单拍"的 SOF 事件，对齐到**帧首拍 tvalid 那一拍**输出 tuser。
//       AXI-Stream 规范：tuser 只在 tvalid 有效时才被 VDMA 采样。
//
// 域约定：全部逻辑在 aclk（= FCLK1 100 MHz，与 conv_tvalid/conv_tready 同域）。
//         sof_pulse 必须已由上游（PCLK 域 -> aclk 两级同步）产生为 aclk 域单拍脉冲。
//
// TUSER_MODE：
//   1 = 对齐模式（默认）：tuser = sof_pending & tvalid，与该拍 tready 无关，只高 1 拍
//   0 = 直连模式（= build11i/11j 行为，保底可切回）
//
// 探针（全部为寄存器输出，跨到 GPIO 前不需要再打拍）：
//   a0_tuser2tlast  : tuser 那一拍 -> 该帧首个 tlast 的 beat 数（期望 ≈1280）
//   a1_tlast2tuser  : 末 tlast -> 下一 tuser 之间的 beat 数（期望 =0）
//   b0_frame_beats  : 每帧总 beat 数（tuser -> 下一 tuser，期望 =921600）
//   b1_pending_stuck: sof_pending 未被消费（卡住）的帧计数（期望 =0）
// ============================================================================
module tuser_shaper #(
    parameter integer TUSER_MODE = 1
) (
    input  wire        aclk,
    input  wire        aresetn,
    input  wire        sof_pulse,     // aclk 域：每帧单拍
    input  wire        tvalid,        // converter -> VDMA 的 tvalid
    input  wire        tready,        // converter -> VDMA 的 tready
    input  wire        tlast,         // converter -> VDMA 的 tlast
    output wire        tuser,         // 整形后的 tuser（接 VDMA s_axis_s2mm_tuser）
    output reg  [31:0] a0_tuser2tlast,
    output reg  [31:0] a1_tlast2tuser,
    output reg  [31:0] b0_frame_beats,
    output reg  [31:0] b1_pending_stuck,
    output reg  [31:0] c0_misalign_cnt   // tuser=1 但 tvalid=0 的拍数（应恒 0 = 同拍已对齐）
);

    wire hs_beat = tvalid & tready;

    // ---- pending：收到 SOF 后置位，在首个 tvalid 拍被消费 ----
    reg sof_pending;
    always @(posedge aclk) begin
        if (!aresetn) begin
            sof_pending <= 1'b0;
        end else if (sof_pulse) begin
            sof_pending <= 1'b1;
        end else if (sof_pending && tvalid && tready) begin   // 与 tuser 同拍清除
            sof_pending <= 1'b0;
        end
    end

    // ---- tuser 输出 ----
    // 候选A(build11p2): SOF 必须真正被接收 —— 首拍 tready=0 时不清 pending
    assign tuser = (TUSER_MODE != 0) ? (sof_pending & tvalid & tready) : sof_pulse;
    // 有效 tuser 事件：对齐模式下就是"tuser 与有效 beat 同拍"，直连模式为脉冲本身
    wire tuser_ev = (TUSER_MODE != 0) ? (tuser & hs_beat) : sof_pulse;

    // ---- 探针状态机 ----
    reg [31:0] fb_cnt;        // 本帧已过 beat 数
    reg [31:0] a0_cnt;        // tuser 起算的 beat 数
    reg [31:0] gap_cnt;       // 末 tlast 之后的 beat 数
    reg        fb_active;
    reg        first_tlast_seen;
    reg        gap_active;

    always @(posedge aclk) begin
        if (!aresetn) begin
            fb_cnt <= 32'd0; a0_cnt <= 32'd0; gap_cnt <= 32'd0;
            fb_active <= 1'b0; first_tlast_seen <= 1'b0; gap_active <= 1'b0;
            a0_tuser2tlast <= 32'd0; a1_tlast2tuser <= 32'd0;
            b0_frame_beats <= 32'd0; b1_pending_stuck <= 32'd0; c0_misalign_cnt <= 32'd0;
        end else begin
            // 错拍计数：tuser 拉高但该拍没有 tvalid（AXIS 不合法）=> 必须恒 0
            if (tuser && (!tvalid || !tready)) c0_misalign_cnt <= c0_misalign_cnt + 32'd1;   // tuser 必须与 tvalid&tready 同拍

            // pending 卡住计数：SOF 到来时上一帧的 pending 还没被消费
            if (sof_pulse && sof_pending) b1_pending_stuck <= b1_pending_stuck + 32'd1;

            // 帧边界
            if (tuser_ev) begin
                if (fb_active)         b0_frame_beats <= fb_cnt;        // 上一帧总 beat
                if (!first_tlast_seen) a0_tuser2tlast <= 32'd0;         // 上一帧无 tlast（异常）
                if (gap_active) begin  a1_tlast2tuser <= gap_cnt; gap_active <= 1'b0; end
                fb_cnt <= 32'd1; a0_cnt <= 32'd1;
                fb_active <= 1'b1; first_tlast_seen <= 1'b0;
            end else if (hs_beat && fb_active) begin
                fb_cnt <= fb_cnt + 32'd1;
                if (!first_tlast_seen) a0_cnt <= a0_cnt + 32'd1;
            end

            // tuser -> 首个 tlast
            if (hs_beat && tlast && fb_active && !first_tlast_seen) begin
                // 该 tlast 拍本身也算 1 个 beat（a0_cnt 尚未含本拍）=> +1
                a0_tuser2tlast   <= a0_cnt + 32'd1;
                first_tlast_seen <= 1'b1;
            end

            // 末 tlast 后的空档
            if (hs_beat && tlast) begin
                gap_cnt <= 32'd0; gap_active <= 1'b1;
            end else if (hs_beat && gap_active) begin
                gap_cnt <= gap_cnt + 32'd1;
            end
        end
    end
endmodule