// s4d_preproc_v2_wrap.sv —— 4-D 预处理 v2 顶层：AXI4-Lite 控制 + AXI4 突发数据面
//
// 结构：
//   S_AXI(AXI4-Lite) → s4d_preproc_csr(@0x43C10000) ── start/busy/done ──┐
//                                                                        ↓
//   M_AXI_RD(AXI4 读) → s4d_axi4_rd_shim → 突发简单口 → s4d_preproc_engine_v2 → 输出字节流
//
// 与 v1 wrapper 的区别：
//   · v1 的源像素口是"线性地址 + 组合读"，未接 AXI；v2 直接给 **AXI4 读主口（AR/R）**，
//     每行一次 240 beat × 64 bit 突发，可直连 PS 的 S_AXI_HP0（经 smartconnect 做 AXI4→AXI3 转换）。
//   · 输出仍是"有效/数据/最后"的字节流（不改 CHW 语义）；接 DMA/AXIS 属合并阶段的工作。
//
// 边界：
//   · shim 内按 4KB 边界动态拆块（AXI 规定 INCR 不得跨 4KB，HP0 侧经 SmartConnect 转 AXI3）；
//   · 不处理 rresp 错误（仅 err 粘滞读出），已知边界；
//   · 本 wrapper 只做控制面 + 数据面接线，不含行复用优化。

`timescale 1ns / 1ps

module s4d_preproc_v2_wrap #(
    parameter logic [31:0] SRC_BASE = 32'h0000_0000   // 源图基址（P2c BD 覆盖为 0x12000000）
) (

    (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 clk CLK" *)
    (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME clk, ASSOCIATED_BUSIF S_AXI:M_AXI_RD:M_AXIS, ASSOCIATED_RESET rstn, FREQ_HZ 50000000, PHASE 0.000" *)
    input  logic        clk,
    (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 rstn RST" *)
    (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME rstn, POLARITY ACTIVE_LOW" *)
    input  logic        rstn,

    // ---------------- AXI4-Lite 从端（控制，基址 0x43C10000） ----------------
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI AWADDR" *)
    (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME S_AXI, PROTOCOL AXI4LITE, DATA_WIDTH 32, ADDR_WIDTH 6, FREQ_HZ 50000000, ID_WIDTH 0, AWUSER_WIDTH 0, ARUSER_WIDTH 0, WUSER_WIDTH 0, RUSER_WIDTH 0, BUSER_WIDTH 0, READ_WRITE_MODE READ_WRITE, HAS_BURST 0, HAS_LOCK 0, HAS_PROT 0, HAS_CACHE 0, HAS_QOS 0, HAS_REGION 0, SUPPORTS_NARROW_BURST 0, MAX_BURST_LENGTH 1, NUM_READ_OUTSTANDING 1, NUM_WRITE_OUTSTANDING 1" *)
    input  logic [5:0]  s_axi_awaddr,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI AWVALID" *) input  logic        s_axi_awvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI AWREADY" *) output logic        s_axi_awready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI WDATA"   *) input  logic [31:0] s_axi_wdata,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI WSTRB"   *) input  logic [3:0]  s_axi_wstrb,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI WVALID"  *) input  logic        s_axi_wvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI WREADY"  *) output logic        s_axi_wready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI BRESP"   *) output logic [1:0]  s_axi_bresp,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI BVALID"  *) output logic        s_axi_bvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI BREADY"  *) input  logic        s_axi_bready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI ARADDR"  *) input  logic [5:0]  s_axi_araddr,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI ARVALID" *) input  logic        s_axi_arvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI ARREADY" *) output logic        s_axi_arready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI RDATA"   *) output logic [31:0] s_axi_rdata,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI RRESP"   *) output logic [1:0]  s_axi_rresp,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI RVALID"  *) output logic        s_axi_rvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI RREADY"  *) input  logic        s_axi_rready,

    // ---------------- AXI4 读主口（数据面，64 bit / INCR） ----------------
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI_RD ARADDR" *)
    (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME M_AXI_RD, PROTOCOL AXI4, READ_WRITE_MODE READ_ONLY, DATA_WIDTH 64, ADDR_WIDTH 32, FREQ_HZ 50000000, ID_WIDTH 0, AWUSER_WIDTH 0, ARUSER_WIDTH 0, WUSER_WIDTH 0, RUSER_WIDTH 0, BUSER_WIDTH 0, HAS_BURST 1, HAS_LOCK 0, HAS_PROT 0, HAS_CACHE 0, HAS_QOS 0, HAS_REGION 0, SUPPORTS_NARROW_BURST 0, MAX_BURST_LENGTH 256, NUM_READ_OUTSTANDING 1, NUM_WRITE_OUTSTANDING 0" *)
    output logic [31:0] m_axi_rd_araddr,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI_RD ARLEN"    *) output logic [7:0]  m_axi_rd_arlen,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI_RD ARSIZE"   *) output logic [2:0]  m_axi_rd_arsize,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI_RD ARBURST"  *) output logic [1:0]  m_axi_rd_arburst,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI_RD ARVALID"  *) output logic        m_axi_rd_arvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI_RD ARREADY"  *) input  logic        m_axi_rd_arready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI_RD RDATA"    *) input  logic [63:0] m_axi_rd_rdata,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI_RD RRESP"    *) input  logic [1:0]  m_axi_rd_rresp,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI_RD RLAST"    *) input  logic        m_axi_rd_rlast,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI_RD RVALID"   *) input  logic        m_axi_rd_rvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 M_AXI_RD RREADY"   *) output logic        m_axi_rd_rready,

    // ---------------- 输出：AXI4-Stream（INT8 CHW，tuser=帧首，tlast=帧尾） ----------------
    (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 M_AXIS TDATA"  *) output logic [7:0] m_axis_tdata,
    (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 M_AXIS TVALID" *) output logic       m_axis_tvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 M_AXIS TREADY" *) input  logic       m_axis_tready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 M_AXIS TLAST"  *) output logic       m_axis_tlast,
    (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 M_AXIS TUSER"  *)
    (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME M_AXIS, TDATA_NUM_BYTES 1, TUSER_WIDTH 1, HAS_TLAST 1, HAS_TUSER 1, HAS_TREADY 1, FREQ_HZ 50000000" *)
    output logic        m_axis_tuser,

    // ---------------- 状态 ----------------
    output logic        busy_o,
    output logic        done_o,
    output logic [31:0] done_count_o,
    output logic [31:0] byte_count_o,
    output logic        rd_err_o
);

    logic        start_pulse;
    logic        busy, done;
    logic [31:0] done_count;
    logic        eng_start;

    // 引擎 ↔ AXIS 封装
    logic        e_valid, e_last, e_ready;
    logic [7:0]  e_data;
    logic [31:0] e_bytes;
    logic [31:0] axis_pushed, axis_popped;

    // 引擎 ↔ shim 的突发简单口
    logic        b_req, b_ack, b_valid, b_ready;
    logic [31:0] b_addr;
    logic [9:0]  b_beats;
    logic [63:0] b_data;

    s4d_preproc_csr u_csr (
        .clk(clk), .rstn(rstn),
        .s_axi_awaddr(s_axi_awaddr), .s_axi_awvalid(s_axi_awvalid), .s_axi_awready(s_axi_awready),
        .s_axi_wdata(s_axi_wdata), .s_axi_wstrb(s_axi_wstrb),
        .s_axi_wvalid(s_axi_wvalid), .s_axi_wready(s_axi_wready),
        .s_axi_bresp(s_axi_bresp), .s_axi_bvalid(s_axi_bvalid), .s_axi_bready(s_axi_bready),
        .s_axi_araddr(s_axi_araddr), .s_axi_arvalid(s_axi_arvalid), .s_axi_arready(s_axi_arready),
        .s_axi_rdata(s_axi_rdata), .s_axi_rresp(s_axi_rresp),
        .s_axi_rvalid(s_axi_rvalid), .s_axi_rready(s_axi_rready),
        .start_pulse(start_pulse), .busy(busy), .done(done), .done_count(done_count),
        // 超时注入仅用于 TB 证明保护路径；真实集成恒接 0
        .inj_rd_stall(1'b0), .inj_wr_stall(1'b0)
    );

    assign eng_start = start_pulse & ~busy;

    s4d_preproc_engine_v2 #(.SRC_BASE(SRC_BASE)) u_eng (
        .clk(clk), .rstn(rstn),
        .start(eng_start), .busy(busy), .done(done),
        .rd_req(b_req), .rd_addr(b_addr), .rd_beats(b_beats),
        .rd_ack(b_ack), .rd_valid(b_valid), .rd_data(b_data), .rd_ready(b_ready),
        .m_valid(e_valid), .m_data(e_data), .m_last(e_last), .m_ready(e_ready),
        .byte_count(e_bytes)
    );

    s4d_preproc_out_axis #(.DEPTH(8)) u_axis (
        .clk(clk), .rstn(rstn),
        .s_valid(e_valid), .s_data(e_data), .s_last(e_last), .s_ready(e_ready),
        .m_axis_tdata(m_axis_tdata), .m_axis_tvalid(m_axis_tvalid),
        .m_axis_tready(m_axis_tready), .m_axis_tlast(m_axis_tlast),
        .m_axis_tuser(m_axis_tuser),
        .pushed_cnt(axis_pushed), .popped_cnt(axis_popped)
    );

    assign byte_count_o = e_bytes;

    s4d_axi4_rd_shim u_shim (
        .clk(clk), .rstn(rstn),
        .rd_req(b_req), .rd_addr(b_addr), .rd_beats(b_beats), .rd_ack(b_ack),
        .rd_valid(b_valid), .rd_data(b_data), .rd_ready(b_ready),
        .m_axi_araddr(m_axi_rd_araddr), .m_axi_arlen(m_axi_rd_arlen),
        .m_axi_arsize(m_axi_rd_arsize), .m_axi_arburst(m_axi_rd_arburst),
        .m_axi_arvalid(m_axi_rd_arvalid), .m_axi_arready(m_axi_rd_arready),
        .m_axi_rdata(m_axi_rd_rdata), .m_axi_rresp(m_axi_rd_rresp), .m_axi_rlast(m_axi_rd_rlast),
        .m_axi_rvalid(m_axi_rd_rvalid), .m_axi_rready(m_axi_rd_rready),
        .busy(), .err_sticky(rd_err_o), .chunk_cnt()   // 拆块计数本层不观测（TB 直连 shim）
    );

    assign busy_o       = busy;
    assign done_o       = done;
    assign done_count_o = done_count;

endmodule
