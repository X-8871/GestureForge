// ============================================================================
// top_p3q.v —— 阶段5（HDMI 显示链）/ S5-T01 / **P3q（P2d 计算体 + P3n/P3p 显示链）**
//
// P3p = P3n（数据面 100 MHz）+ **VDMA frame-sync（fsync）+ tlast 诊断 + 每帧欠载计数**
//
//   目的：修掉"帧不同步"这个独立于欠载的第二根因 ——
//     P3m/P3n 里 axis_to_video 按自建 60 Hz 自由跑、VDMA 按 52 fps 出帧，
//     两者帧率不等 ⇒ 显示的一帧会横跨 VDMA 的两个帧边界 ⇒ 水平撕裂/滚动。
//   fsync 方案：把显示侧的 vsync 送给 VDMA 的 mm2s_fsync，
//     VDMA 每收到一个 fsync 脉冲才推进一帧 ⇒ 供帧节奏由显示决定，从架构上消除撕裂。
//
//   结构（骨架仍是 P3k 已验证的那套）：
//     sys_clk(U18,50MHz) -> MMCME2_ADV -> pixel_clk 74.21875 / pixel_clk_5x 371.09375 + locked
//     BD(最小): PS7(FCLK0=50 控制面 / FCLK1=100 数据面) + axi_vdma(MM2S-only, 非SG, fsync=1)
//               + axi_protocol_converter + axi_gpio(双通道: 本帧欠载 / 累计欠载)
//     axis_to_video: 自建 720p60 + 欠载计黑 + tlast 诊断
//     rgb2dvi -> TMDS(N18/V20/T20/N20)
//
//   时钟域：
//     - 控制面 50 MHz / 数据面(VDMA MM, HP2, 协议转换器) 100 MHz / 流侧 pixel_clk 74.21875 (ASYNC)
//     - 跨域只出现在诊断计数：像素域 -> 50 MHz 域，用格雷码 + 3 级同步（见下）
//     - **vsync 从像素域送到 BD 的 mm2s_fsync**：单比特，VDMA 内部按 m_axis_mm2s_aclk 采样，
//       属于慢变信号（高电平持续 5 行 ≈ 111 µs），无亚稳态风险
//
//   边界：不上板、不烧 QSPI、不 git。
// ============================================================================
`timescale 1ns / 1ps

module top_p3q (
    // ---------------- PS DDR / FIXED_IO（透传 BD wrapper，芯片边界必需）----------------
    inout  [14:0] DDR_0_addr,
    inout  [2:0]  DDR_0_ba,
    inout         DDR_0_cas_n,
    inout         DDR_0_ck_n,
    inout         DDR_0_ck_p,
    inout         DDR_0_cke,
    inout         DDR_0_cs_n,
    inout  [3:0]  DDR_0_dm,
    inout  [31:0] DDR_0_dq,
    inout  [3:0]  DDR_0_dqs_n,
    inout  [3:0]  DDR_0_dqs_p,
    inout         DDR_0_odt,
    inout         DDR_0_ras_n,
    inout         DDR_0_reset_n,
    inout         DDR_0_we_n,
    inout         FIXED_IO_0_ddr_vrn,
    inout         FIXED_IO_0_ddr_vrp,
    inout  [53:0] FIXED_IO_0_mio,
    inout         FIXED_IO_0_ps_clk,
    inout         FIXED_IO_0_ps_porb,
    inout         FIXED_IO_0_ps_srstb,
    // ---------------- 板载 50 MHz ----------------
    input  wire       sys_clk,        // U18
    // ---------------- HDMI / TMDS ----------------
    output wire       TMDS_clk_p,
    output wire       TMDS_clk_n,
    output wire [2:0] TMDS_data_p,
    output wire [2:0] TMDS_data_n,
    output wire       hdmi_oen
);

    // ---------------- 时钟：50 MHz -> 74.21875 / 371.09375 + LOCKED ----------------
    wire clk_pixel_raw, clk_5x_raw, clk_fb, locked;
    wire pixel_clk, pixel_clk_5x;

    MMCME2_ADV #(
        .BANDWIDTH           ("OPTIMIZED"),
        .CLKOUT4_CASCADE     ("FALSE"),
        .COMPENSATION        ("ZHOLD"),
        .STARTUP_WAIT        ("FALSE"),
        .DIVCLK_DIVIDE       (4),
        .CLKFBOUT_MULT_F     (59.375),
        .CLKFBOUT_PHASE      (0.000),
        .CLKFBOUT_USE_FINE_PS("FALSE"),
        .CLKOUT0_DIVIDE_F    (10.000),
        .CLKOUT0_PHASE       (0.000),
        .CLKOUT0_DUTY_CYCLE  (0.500),
        .CLKOUT1_DIVIDE      (2),
        .CLKOUT1_PHASE       (0.000),
        .CLKOUT1_DUTY_CYCLE  (0.500),
        .CLKIN1_PERIOD       (20.000),
        .REF_JITTER1         (0.010)
    ) u_mmcm (
        .CLKOUT0(clk_pixel_raw), .CLKOUT0B(), .CLKOUT1(clk_5x_raw), .CLKOUT1B(),
        .CLKOUT2(), .CLKOUT2B(), .CLKOUT3(), .CLKOUT3B(), .CLKOUT4(), .CLKOUT5(), .CLKOUT6(),
        .CLKFBOUT(clk_fb), .CLKFBOUTB(), .CLKFBIN(clk_fb),
        .CLKIN1(sys_clk), .CLKIN2(1'b0), .CLKINSEL(1'b1),
        .DADDR(7'b0), .DCLK(1'b0), .DEN(1'b0), .DI(16'b0), .DO(), .DRDY(), .DWE(1'b0),
        .LOCKED(locked),
        .PSCLK(1'b0), .PSDONE(), .PSEN(1'b0), .PSINCDEC(1'b0),
        .PWRDWN(1'b0), .RST(1'b0)
    );

    BUFG u_bufg_pixel (.I(clk_pixel_raw), .O(pixel_clk));
    BUFG u_bufg_5x    (.I(clk_5x_raw),    .O(pixel_clk_5x));

    // ---------------- BD ----------------
    wire [31:0] m_axis_tdata;
    wire        m_axis_tvalid;
    wire        m_axis_tlast;
    wire        m_axis_tready;
    wire [31:0] uf_frame_in;      // 送 GPIO ch1（本帧欠载像素数，50 MHz 域）
    wire [31:0] uf_total_in;      // 送 GPIO ch2（累计欠载像素数，50 MHz 域）
    wire        clk_50;           // BD 导出的 FCLK0

    wire        hs, vs, de;
    wire [23:0] rgb;
    wire [31:0] uf_pixels;        // 像素域累计欠载
    wire [31:0] tlast_misalign;   // 像素域 tlast 异常计数

    s4d_p3q_wrapper u_bd (
        .DDR_0_addr     (DDR_0_addr),
        .DDR_0_ba       (DDR_0_ba),
        .DDR_0_cas_n    (DDR_0_cas_n),
        .DDR_0_ck_n     (DDR_0_ck_n),
        .DDR_0_ck_p     (DDR_0_ck_p),
        .DDR_0_cke      (DDR_0_cke),
        .DDR_0_cs_n     (DDR_0_cs_n),
        .DDR_0_dm       (DDR_0_dm),
        .DDR_0_dq       (DDR_0_dq),
        .DDR_0_dqs_n    (DDR_0_dqs_n),
        .DDR_0_dqs_p    (DDR_0_dqs_p),
        .DDR_0_odt      (DDR_0_odt),
        .DDR_0_ras_n    (DDR_0_ras_n),
        .DDR_0_reset_n  (DDR_0_reset_n),
        .DDR_0_we_n     (DDR_0_we_n),
        .FIXED_IO_0_ddr_vrn  (FIXED_IO_0_ddr_vrn),
        .FIXED_IO_0_ddr_vrp  (FIXED_IO_0_ddr_vrp),
        .FIXED_IO_0_mio      (FIXED_IO_0_mio),
        .FIXED_IO_0_ps_clk   (FIXED_IO_0_ps_clk),
        .FIXED_IO_0_ps_porb  (FIXED_IO_0_ps_porb),
        .FIXED_IO_0_ps_srstb (FIXED_IO_0_ps_srstb),
        .pixel_clk      (pixel_clk),
        .clk_50         (clk_50),
        .m_axis_tdata   (m_axis_tdata),
        .m_axis_tvalid  (m_axis_tvalid),
        .m_axis_tlast   (m_axis_tlast),
        .m_axis_tready  (m_axis_tready),
        .mm2s_fsync     (vs),          // ★ 显示侧场同步 -> VDMA frame sync
        .uf_frame       (uf_frame_in),
        .uf_total       (uf_total_in)
    );

    // ---------------- 自建视频时序 + AXIS 取数 ----------------
    axis_to_video u_atv (
        .pixel_clk      (pixel_clk),
        .rst            (~locked),
        .s_axis_tdata   (m_axis_tdata),
        .s_axis_tvalid  (m_axis_tvalid),
        .s_axis_tlast   (m_axis_tlast),
        .s_axis_tready  (m_axis_tready),
        .hs             (hs),
        .vs             (vs),
        .de             (de),
        .rgb            (rgb),
        .uf_pixels      (uf_pixels),
        .tlast_misalign (tlast_misalign)
    );

    // ============================================================================
    // 诊断计数：像素域 -> 50 MHz 域（格雷码 + 3 级同步），并在 50 MHz 域算"本帧欠载"
    // ============================================================================
    // 1) 两组单调递增计数器 -> 格雷码
    wire [31:0] uf_gray      = (uf_pixels      >> 1) ^ uf_pixels;
    wire [31:0] mis_gray     = (tlast_misalign >> 1) ^ tlast_misalign;

    (* ASYNC_REG = "TRUE" *) reg [31:0] uf_g_s1, uf_g_s2, uf_g_s3;
    (* ASYNC_REG = "TRUE" *) reg [31:0] mis_g_s1, mis_g_s2, mis_g_s3;

    always @(posedge clk_50) begin
        uf_g_s1  <= uf_gray;
        uf_g_s2  <= uf_g_s1;
        uf_g_s3  <= uf_g_s2;
        mis_g_s1 <= mis_gray;
        mis_g_s2 <= mis_g_s1;
        mis_g_s3 <= mis_g_s2;
    end

    // 2) 格雷 -> 二进制
    integer i;
    reg [31:0] uf_bin, mis_bin;
    always @* begin
        uf_bin[31] = uf_g_s3[31];
        for (i = 30; i >= 0; i = i - 1) uf_bin[i] = uf_bin[i+1] ^ uf_g_s3[i];
    end
    always @* begin
        mis_bin[31] = mis_g_s3[31];
        for (i = 30; i >= 0; i = i - 1) mis_bin[i] = mis_bin[i+1] ^ mis_g_s3[i];
    end

    // 3) vsync 同步到 50 MHz 域，取上升沿作为"帧边界"
    (* ASYNC_REG = "TRUE" *) reg vs_meta, vs_sync, vs_sync_d;
    always @(posedge clk_50) begin
        vs_meta   <= vs;
        vs_sync   <= vs_meta;
        vs_sync_d <= vs_sync;
    end
    wire vs_rise = vs_sync & ~vs_sync_d;

    // 4) 本帧欠载 = 当前累计 - 本帧起点累计（全部在 50 MHz 域做减法，安全）
    reg [31:0] uf_frame_start;
    always @(posedge clk_50) begin
        if (vs_rise)
            uf_frame_start <= uf_bin;
    end
    assign uf_frame_in = uf_bin - uf_frame_start;
    assign uf_total_in = uf_bin;

    // tlast_misalign 目前只做内部诊断（不接 GPIO，两个 GPIO 通道已给"本帧/累计欠载"）；
    // 需要时可换到 GPIO ch2 或用 ILA 观测。
    wire [31:0] unused_mis = mis_bin;

    // ---------------- rgb2dvi ----------------
    wire unused_oen;

    rgb2dvi_wrap u_rgb2dvi (
        .TMDS_Clk_p  (TMDS_clk_p),
        .TMDS_Clk_n  (TMDS_clk_n),
        .TMDS_Data_p (TMDS_data_p),
        .TMDS_Data_n (TMDS_data_n),
        .oen         (unused_oen),
        .aRst_n      (locked),
        .vid_pData   (rgb),
        .vid_pVDE    (de),
        .vid_pHSync  (hs),
        .vid_pVSync  (vs),
        .PixelClk    (pixel_clk),
        .SerialClk   (pixel_clk_5x)
    );

    // ---------------- 其他 ----------------
    assign hdmi_oen = 1'b1;

endmodule