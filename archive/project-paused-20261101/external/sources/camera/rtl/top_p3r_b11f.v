// ============================================================================
// top_p3r_b11f.v —— build11f（时钟/复位电平观测）：/ 阶段5（HDMI 显示链）/ S5-T01 / **P3r（P3q 冻结集成体 + AN5642 相机采集→DDR raw）**
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

module top_p3r_b11f (
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
    output wire       hdmi_oen,
    // ---------------- AN5642 相机（J11 / CMOS2，阶段3 冻结引脚）----------------
    input  wire [9:0] cmos1_d,
    input  wire       cmos1_href,
    input  wire       cmos1_vsync,
    input  wire       cmos1_pclk,
    inout  wire       cmos1_i2c_sda_io,   // SCCB：PS7 I2C0 via EMIO
    inout  wire       cmos1_i2c_scl_io,
    output wire       cmos_rstn
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

    // ============================================================================
    // build7：SCCB 测试通道（PS7 EMIO I2C0 正常模式 与 手动 bit-bang 二选一）
    //   0x43C80000 +0x00 ctrl(3b): bit0=mode(1=手动) bit1=scl_drive_low bit2=sda_drive_low
    //   0x43C80000 +0x08 level(2b): bit0=SCL 实际电平 bit1=SDA 实际电平（IOBUF 回读）
    //   正常模式(mode=0)：完全直通 PS7 的 SCL/SDA O/T —— 不改变既有 I2C0 行为
    //   手动模式(mode=1)：open-drain 方式——拉低=驱动0(T=0,I=0)，释放=高阻(T=1)，靠上拉
    // ============================================================================
    wire        ps_scl_i, ps_scl_o, ps_scl_t;
    wire        ps_sda_i, ps_sda_o, ps_sda_t;
    wire [2:0]  sccb_ctrl;
    wire [7:0]  sccb_level;   // build8：加宽，含 PS7 侧驱动观测
    wire        scl_pad_i, sda_pad_i;

    wire sccb_mode   = sccb_ctrl[0];
    wire scl_drive_l = sccb_ctrl[1];
    wire sda_drive_l = sccb_ctrl[2];

    wire scl_o_mux = sccb_mode ? 1'b0 : ps_scl_o;
    wire scl_t_mux = sccb_mode ? ~scl_drive_l : ps_scl_t;
    wire sda_o_mux = sccb_mode ? 1'b0 : ps_sda_o;
    wire sda_t_mux = sccb_mode ? ~sda_drive_l : ps_sda_t;

    IOBUF u_iobuf_scl (.I(scl_o_mux), .IO(cmos1_i2c_scl_io), .O(scl_pad_i), .T(scl_t_mux));
    IOBUF u_iobuf_sda (.I(sda_o_mux), .IO(cmos1_i2c_sda_io), .O(sda_pad_i), .T(sda_t_mux));

    // build8 状态位（只读，0x43C80008）：
    //   [0]=SCL 引脚电平  [1]=SDA 引脚电平
    //   [2]=PS7 的 SCL_O  [3]=PS7 的 SCL_T  [4]=PS7 的 SDA_O  [5]=PS7 的 SDA_T
    //   [6]=回传给 PS7 的 SCL_I  [7]=回传给 PS7 的 SDA_I
    assign sccb_level = {ps_sda_i, ps_scl_i, ps_sda_t, ps_sda_o, ps_scl_t, ps_scl_o, sda_pad_i, scl_pad_i};

    // ============================================================================
    // build9：相机输入侧计数器（cam_pclk 域采集 → clk_100 域格雷码同步读出）
    //   0x43C90000 +0x00 = PCLK 上升沿计数   （cam_pclk 域自由运行，无 PCLK 时恒 0）
    //   0x43C90000 +0x08 = HREF 高电平期间的 PCLK 计数
    //   0x43CA0000 +0x00 = VSYNC 边沿计数界 {[31:16]=下降沿数, [15:0]=上升沿数}
    //   跨域：cam_pclk 域二进制计数器 -> 格雷码 -> clk_100 两级同步 -> 还原二进制
    //   （格雷码每次只变 1 位，多 bit CDC 安全）
    // ============================================================================
    reg  [31:0] pclk_cnt, href_cnt;
    reg  [15:0] vsync_r_cnt, vsync_f_cnt;
    reg         vsync_d;

    always @(posedge cmos1_pclk) begin
        pclk_cnt <= pclk_cnt + 32'd1;
        if (cmos1_href) href_cnt <= href_cnt + 32'd1;
        vsync_d  <= cmos1_vsync;
        if ( cmos1_vsync & ~vsync_d) vsync_r_cnt <= vsync_r_cnt + 16'd1;
        if (~cmos1_vsync &  vsync_d) vsync_f_cnt <= vsync_f_cnt + 16'd1;
    end

    function [31:0] b2g32; input [31:0] x; begin b2g32 = x ^ (x >> 1); end endfunction
    function [31:0] g2b32; input [31:0] x; integer i;
        begin g2b32[31] = x[31]; for (i = 30; i >= 0; i = i - 1) g2b32[i] = g2b32[i+1] ^ x[i]; end
    endfunction
    function [15:0] b2g16; input [15:0] x; begin b2g16 = x ^ (x >> 1); end endfunction
    function [15:0] g2b16; input [15:0] x; integer i;
        begin g2b16[15] = x[15]; for (i = 14; i >= 0; i = i - 1) g2b16[i] = g2b16[i+1] ^ x[i]; end
    endfunction

    wire [31:0] pclk_g  = b2g32(pclk_cnt);
    wire [31:0] href_g  = b2g32(href_cnt);
    wire [15:0] vr_g    = b2g16(vsync_r_cnt);
    wire [15:0] vf_g    = b2g16(vsync_f_cnt);

    reg  [31:0] pclk_g1, pclk_g2, href_g1, href_g2;
    reg  [15:0] vr_g1, vr_g2, vf_g1, vf_g2;
    always @(posedge clk_100) begin
        pclk_g1 <= pclk_g;  pclk_g2 <= pclk_g1;
        href_g1 <= href_g;  href_g2 <= href_g1;
        vr_g1   <= vr_g;    vr_g2   <= vr_g1;
        vf_g1   <= vf_g;    vf_g2   <= vf_g1;
    end

    wire [31:0] cam_pclk_cnt  = g2b32(pclk_g2);
    wire [31:0] cam_href_cnt  = g2b32(href_g2);
    wire [31:0] cam_vsync_cnt = {g2b16(vf_g2), g2b16(vr_g2)};

    // ============================================================================
    // build10b：S2MM 链路观测（clk_100 = s_axis_s2mm_aclk 域）
    //   * 修复：converter 的 tuser 原先只接 cam_sof 计数器，VDMA 的 tuser 悬空
    //           现在 BD 里三端同网（converter tuser + VDMA tuser + cam_sof），本层只观测
    //   * tdata 仍走 AXIS 接口（不拆！否则 axi_vdma 的派生流宽会变成 32）
    //   * 计数器：tlast / tuser / (tvalid&&tready) / (tvalid&&!tready)
    //   * 另观测 alinx_ov5640 的 m_axis_video_aresetn 电平（IP 内部其实未使用该端口，
    //     仅用于确认 rst_100 已释放）
    // ============================================================================
    wire conv_tvalid, conv_tlast, conv_tuser, conv_tready;
    wire cam_aresetn_ip;
    wire [31:0] cam_aresetn_ip32 = {31'd0, cam_aresetn_ip};

    // ============================================================================
    // build11b：**IP 输出侧**计数器（converter 之前），判断"IP 不出数"还是"链路丢数"
    //   0x43CE0000 +0x00 = IP m_axis_video_tvalid 拍数
    //   0x43CE0000 +0x08 = IP m_axis_video_tlast 拍数
    //   0x43CF0000 +0x00 = IP m_axis_video_tuser 拍数
    //   0x43CF0000 +0x08 = IP m_axis_video_tready 高电平拍数（VDMA 是否在收）
    //   注意：厂商 IP 的 tvalid = ~empty & tready，因此 tready=0 时 tvalid 也不会拉高，
    //         必须同时看 tready 计数才能区分"IP 无数据"与"下游不收"
    // ============================================================================
    wire ip_tvalid, ip_tlast, ip_tuser, ip_tready;
    wire [31:0] ip_tvalid_cnt, ip_tlast_cnt, ip_tuser_cnt, ip_tready_cnt;
    reg [31:0] ip_tvalid_r, ip_tlast_r, ip_tuser_r, ip_tready_r;
    always @(posedge clk_100) begin
        if (ip_tvalid) ip_tvalid_r <= ip_tvalid_r + 32'd1;
        if (ip_tlast)  ip_tlast_r  <= ip_tlast_r  + 32'd1;
        if (ip_tuser)  ip_tuser_r  <= ip_tuser_r  + 32'd1;
        if (ip_tready) ip_tready_r <= ip_tready_r + 32'd1;
    end
    wire [31:0] itv_g = b2g32(ip_tvalid_r), itl_g = b2g32(ip_tlast_r);
    wire [31:0] itu_g = b2g32(ip_tuser_r), itr_g = b2g32(ip_tready_r);
    reg  [31:0] itv_g1, itv_g2, itl_g1, itl_g2, itu_g1, itu_g2, itr_g1, itr_g2;
    always @(posedge clk_50) begin
        itv_g1 <= itv_g; itv_g2 <= itv_g1;
        itl_g1 <= itl_g; itl_g2 <= itl_g1;
        itu_g1 <= itu_g; itu_g2 <= itu_g1;
        itr_g1 <= itr_g; itr_g2 <= itr_g1;
    end
    assign ip_tvalid_cnt = g2b32(itv_g2);
    assign ip_tlast_cnt  = g2b32(itl_g2);
    assign ip_tuser_cnt  = g2b32(itu_g2);
    assign ip_tready_cnt = g2b32(itr_g2);

    // ============================================================================
    // build11f：时钟/复位电平观测（只读，不接引脚）
    //   0x43D40000 +0x00 = 复位电平 [0]=rst_100/peripheral_aresetn [1]=rst_all/peripheral_aresetn
    //   0x43D40000 +0x08 = FCLK0(50MHz) 上升沿计数
    //   0x43D50000 +0x00 = FCLK1(100MHz) 上升沿计数
    //   计数器各在本域自由运行（不做 CDC，仅判"是否在动"）
    // ============================================================================
    wire        rst100_pa, rstall_pa;
    wire [31:0] obs_rst_levels, obs_fclk0_cnt, obs_fclk1_cnt;
    reg  [31:0] f0_cnt, f1_cnt;
    always @(posedge clk_50)  f0_cnt <= f0_cnt + 32'd1;
    always @(posedge clk_100) f1_cnt <= f1_cnt + 32'd1;
    assign obs_rst_levels = {30'd0, rstall_pa, rst100_pa};
    assign obs_fclk0_cnt  = f0_cnt;
    assign obs_fclk1_cnt  = f1_cnt;
    wire [31:0] s2mm_tlast_cnt, s2mm_tuser_cnt, s2mm_beat_cnt, s2mm_stall_cnt;

    assign cam_sof = conv_tuser;

    reg [31:0] s2mm_tlast_r, s2mm_tuser_r, s2mm_beat_r, s2mm_stall_r;
    always @(posedge clk_100) begin
        if (conv_tvalid &&  conv_tready) s2mm_beat_r  <= s2mm_beat_r  + 32'd1;
        if (conv_tvalid &&  conv_tlast)  s2mm_tlast_r <= s2mm_tlast_r + 32'd1;
        if (conv_tuser)                  s2mm_tuser_r <= s2mm_tuser_r + 32'd1;
        if (conv_tvalid && !conv_tready) s2mm_stall_r <= s2mm_stall_r + 32'd1;
    end

    wire [31:0] tl_g = b2g32(s2mm_tlast_r), tu_g = b2g32(s2mm_tuser_r);
    wire [31:0] bt_g = b2g32(s2mm_beat_r),  st_g = b2g32(s2mm_stall_r);
    reg  [31:0] tl_g1, tl_g2, tu_g1, tu_g2, bt_g1, bt_g2, st_g1, st_g2;
    always @(posedge clk_50) begin
        tl_g1 <= tl_g;  tl_g2 <= tl_g1;
        tu_g1 <= tu_g;  tu_g2 <= tu_g1;
        bt_g1 <= bt_g;  bt_g2 <= bt_g1;
        st_g1 <= st_g;  st_g2 <= st_g1;
    end
    assign s2mm_tlast_cnt = g2b32(tl_g2);
    assign s2mm_tuser_cnt = g2b32(tu_g2);
    assign s2mm_beat_cnt  = g2b32(bt_g2);
    assign s2mm_stall_cnt = g2b32(st_g2);

    // ---------------- P3r 相机采集状态 ----------------
    wire        clk_100;        // BD 导出的 FCLK1（100 MHz，采集/显示数据面）
    wire        cam_sof;        // alinx_ov5640 的 tuser（帧首，单拍脉冲）
    wire [4:0]  cam_frmptr;     // 采集 VDMA S2MM 当前帧指针
    reg  [31:0] cam_sof_cnt;    // 采集帧计数（clk_100 域）
    wire [31:0] cam_frmptr32 = {27'd0, cam_frmptr};

    always @(posedge clk_100) begin
        if (cam_sof)
            cam_sof_cnt <= cam_sof_cnt + 32'd1;
    end

    wire        hs, vs, de;
    wire [23:0] rgb;
    wire [31:0] uf_pixels;        // 像素域累计欠载
    wire [31:0] tlast_misalign;   // 像素域 tlast 异常计数

    s4d_p3r_wrapper u_bd (
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
        .uf_total       (uf_total_in),
        // ---- P3r 相机采集 ----
        .cmos1_d          (cmos1_d),
        .cmos1_href       (cmos1_href),
        .cmos1_vsync      (cmos1_vsync),
        .cmos1_pclk       (cmos1_pclk),
        // build7：I2C 走标量信号 + 测试通道（IOBUF/mux 在本层实现）
        .ps_i2c_scl_i     (ps_scl_i),
        .ps_i2c_scl_o     (ps_scl_o),
        .ps_i2c_scl_t     (ps_scl_t),
        .ps_i2c_sda_i     (ps_sda_i),
        .ps_i2c_sda_o     (ps_sda_o),
        .ps_i2c_sda_t     (ps_sda_t),
        .sccb_ctrl        (sccb_ctrl),
        .sccb_level       (sccb_level),
        .cam_pclk_cnt     (cam_pclk_cnt),
        .cam_href_cnt     (cam_href_cnt),
        .cam_vsync_cnt    (cam_vsync_cnt),
        .conv_tvalid      (conv_tvalid),
        .conv_tlast       (conv_tlast),
        .conv_tuser       (conv_tuser),
        .conv_tready      (conv_tready),
        .cam_aresetn_ip   (cam_aresetn_ip),
        .cam_aresetn_ip32 (cam_aresetn_ip32),
        .ip_tvalid        (ip_tvalid),
        .ip_tlast         (ip_tlast),
        .ip_tuser         (ip_tuser),
        .ip_tready        (ip_tready),
        .ip_tvalid_cnt    (ip_tvalid_cnt),
        .ip_tlast_cnt     (ip_tlast_cnt),
        .ip_tuser_cnt     (ip_tuser_cnt),
        .ip_tready_cnt    (ip_tready_cnt),
        .rst100_pa        (rst100_pa),
        .rstall_pa        (rstall_pa),
        .obs_rst_levels   (obs_rst_levels),
        .obs_fclk0_cnt    (obs_fclk0_cnt),
        .obs_fclk1_cnt    (obs_fclk1_cnt),
        .s2mm_tlast_cnt   (s2mm_tlast_cnt),
        .s2mm_tuser_cnt   (s2mm_tuser_cnt),
        .s2mm_beat_cnt    (s2mm_beat_cnt),
        .s2mm_stall_cnt   (s2mm_stall_cnt),
        .cmos_rstn        (cmos_rstn),
        .clk_100          (clk_100),
        .cam_frmptr       (cam_frmptr),
        .cam_sof_cnt      (cam_sof_cnt),
        .cam_frmptr32     (cam_frmptr32)
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