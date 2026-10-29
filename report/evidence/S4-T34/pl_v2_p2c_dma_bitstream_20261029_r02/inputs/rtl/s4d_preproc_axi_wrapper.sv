// s4d_preproc_axi_wrapper.sv —— 4-D 预处理顶层封装（AXI4-Lite 控制 + 源像素读口）
//
// 作用：
//   1) 把 s4d_preproc_csr（AXI4-Lite 从端，基址 0x43C10000）与 s4d_preproc_letterbox（Q24 引擎）接成一体；
//   2) 给 AXI4-Lite 端口加 X_INTERFACE_INFO 属性，使 BD 里的 create_bd_cell -type module -reference
//      能自动推断出 AXI4-Lite 接口，从而直接用 smartconnect 连 PS 的 M_AXI_GP0；
//   3) 把源像素读口（rd_en / rd_addr / rd_data）原样引出，交由数据通路决定接法。
//
// ⚠️ 数据通路是**未决项**，不在本 wrapper 内拍板：
//   引擎当前对每个活跃输出像素发 4 次**单字节**读（TL/TR/BL/BR），共 1,557,504 次/帧。
//   由 task1 TB 实测 3,247,301 cycles/帧推得：@100 MHz 零存储延迟已是 32.5 ms/帧（30.8 fps），
//   叠加 AXI HP 单拍延迟（20–60 ns）后掉到 10–30 fps —— 见 task1/README.md「吞吐边界」。
//   因此 rd_* 不建议直接挂 AXI 主口，应改为「行缓冲 + 突发读」：
//     源 640×480 BGR 每帧仅 921,600 B，突发搬运 ≈1.8 ms @0.5 GB/s，瓶颈即可回到计算侧。
//   该改造**会改变 rd_* 的语义**（从逐字节随机读 → 行填充/流式），故留待架构决策后再接，
//   本 wrapper 只保证控制面（CSR↔引擎）正确闭合，不掩盖数据面缺口。

`timescale 1ns / 1ps

module s4d_preproc_axi_wrapper (
    (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 clk CLK" *)
    (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME clk, ASSOCIATED_BUSIF S_AXI, ASSOCIATED_RESET rstn, FREQ_HZ 100000000, PHASE 0.000" *)
    input  logic        clk,
    (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 rstn RST" *)
    (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME rstn, POLARITY ACTIVE_LOW" *)
    input  logic        rstn,

    // ---------------- AXI4-Lite 从端（PS M_AXI_GP0 → 本模块，基址 0x43C10000） ----------------
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI AWADDR"  *)
    (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME S_AXI, PROTOCOL AXI4LITE, DATA_WIDTH 32, ADDR_WIDTH 6, FREQ_HZ 100000000, ID_WIDTH 0, AWUSER_WIDTH 0, ARUSER_WIDTH 0, WUSER_WIDTH 0, RUSER_WIDTH 0, BUSER_WIDTH 0, READ_WRITE_MODE READ_WRITE, HAS_BURST 0, HAS_LOCK 0, HAS_PROT 0, HAS_CACHE 0, HAS_QOS 0, HAS_REGION 0, SUPPORTS_NARROW_BURST 0, MAX_BURST_LENGTH 1, NUM_READ_OUTSTANDING 1, NUM_WRITE_OUTSTANDING 1" *)
    input  logic [5:0]  s_axi_awaddr,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI AWVALID" *)
    input  logic        s_axi_awvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI AWREADY" *)
    output logic        s_axi_awready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI WDATA"   *)
    input  logic [31:0] s_axi_wdata,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI WSTRB"   *)
    input  logic [3:0]  s_axi_wstrb,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI WVALID"  *)
    input  logic        s_axi_wvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI WREADY"  *)
    output logic        s_axi_wready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI BRESP"   *)
    output logic [1:0]  s_axi_bresp,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI BVALID"  *)
    output logic        s_axi_bvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI BREADY"  *)
    input  logic        s_axi_bready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI ARADDR"  *)
    input  logic [5:0]  s_axi_araddr,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI ARVALID" *)
    input  logic        s_axi_arvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI ARREADY" *)
    output logic        s_axi_arready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI RDATA"   *)
    output logic [31:0] s_axi_rdata,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI RRESP"   *)
    output logic [1:0]  s_axi_rresp,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI RVALID"  *)
    output logic        s_axi_rvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:aximm:1.0 S_AXI RREADY"  *)
    input  logic        s_axi_rready,

    // ---------------- 源像素读口（数据面未决，见文件头） ----------------
    output logic        src_rd_en,
    output logic [23:0] src_rd_addr,
    input  logic [7:0]  src_rd_data,

    // ---------------- 状态指示（可选，便于 ILA/BD 观测） ----------------
    output logic        busy_o,
    output logic        done_o,
    output logic [31:0] done_count_o,
    output logic [31:0] out_byte_count_o
);

    logic        start_pulse;
    logic        busy, done;
    logic [31:0] done_count;
    logic        eng_start;
    logic [31:0] byte_count;

    s4d_preproc_csr u_csr (
        .clk            (clk),
        .rstn           (rstn),
        .s_axi_awaddr   (s_axi_awaddr),
        .s_axi_awvalid  (s_axi_awvalid),
        .s_axi_awready  (s_axi_awready),
        .s_axi_wdata    (s_axi_wdata),
        .s_axi_wstrb    (s_axi_wstrb),
        .s_axi_wvalid   (s_axi_wvalid),
        .s_axi_wready   (s_axi_wready),
        .s_axi_bresp    (s_axi_bresp),
        .s_axi_bvalid   (s_axi_bvalid),
        .s_axi_bready   (s_axi_bready),
        .s_axi_araddr   (s_axi_araddr),
        .s_axi_arvalid  (s_axi_arvalid),
        .s_axi_arready  (s_axi_arready),
        .s_axi_rdata    (s_axi_rdata),
        .s_axi_rresp    (s_axi_rresp),
        .s_axi_rvalid   (s_axi_rvalid),
        .s_axi_rready   (s_axi_rready),
        .start_pulse    (start_pulse),
        .busy           (busy),
        .done           (done),
        .done_count     (done_count)
    );

    // START 只在引擎空闲时放行（CSR 侧 busy 期间已忽略写 1，这里再挡一层）
    assign eng_start = start_pulse & ~busy;

    s4d_preproc_letterbox u_engine (
        .clk        (clk),
        .rstn       (rstn),
        .start      (eng_start),
        .busy       (busy),
        .done       (done),
        .rd_en      (src_rd_en),
        .rd_addr    (src_rd_addr),
        .rd_data    (src_rd_data),
        .m_valid    (),
        .m_data     (),
        .m_last     (),
        .byte_count (byte_count)
    );

    assign busy_o           = busy;
    assign done_o           = done;
    assign done_count_o     = done_count;
    assign out_byte_count_o = byte_count;

endmodule
