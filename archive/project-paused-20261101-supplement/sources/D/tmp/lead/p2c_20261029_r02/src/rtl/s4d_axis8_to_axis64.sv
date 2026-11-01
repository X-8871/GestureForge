// s4d_axis8_to_axis64.sv —— 8 位（无 TKEEP）AXIS → 64 位（带 TKEEP）AXIS 打包器（P2c 用）
//
// 用途：preproc v2 的 M_AXIS 是 8 bit / 无 TKEEP；AXI DMA 的 S2MM 以 64 bit 流 + 64 bit 内存映射
// 工作最稳妥（避免 8→64 的字节序/填充语义依赖 IP 版本）。本模块把连续 8 个字节按小端打包成 1 个 64 bit beat：
//   第 1 个字节 → m_tdata[7:0]，第 8 个字节 → m_tdata[63:56]，m_tkeep 恒 0xFF。
// 帧尾若不在 8 字节边界（本设计 519,168 B = 64,896×8，恰好整除），用 TKEEP 屏蔽多余字节并置 TLAST。
// s_tuser（preproc 的帧首标记）不参与打包，输入后忽略——保留端口以匹配上游 M_AXIS 的 TUSER_WIDTH=1。
//
// 时序：攒满（或收到 TLAST）后发一个 beat；beat 未被取走时 s_tready=0（简单反压，不做流水重叠）。
// 复位：rstn 低有效；复位期间不接收、不输出。
//
// 自检：src/tb/tb_s4d_axis8_to_axis64.sv（xsim，PACKER_TB_RESULT=PASS）。

`timescale 1ns / 1ps

module s4d_axis8_to_axis64 (
    (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 clk CLK" *)
    (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME clk, ASSOCIATED_BUSIF S_AXIS:M_AXIS, ASSOCIATED_RESET rstn, FREQ_HZ 50000000, PHASE 0.000" *)
    input  logic        clk,
    (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 rstn RST" *)
    (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME rstn, POLARITY ACTIVE_LOW" *)
    input  logic        rstn,

    // ---- 从端：8 bit AXIS（无 TKEEP；TUSER 1 bit 仅接收不参与） ----
    (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 S_AXIS TDATA" *)
    (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME S_AXIS, TDATA_NUM_BYTES 1, HAS_TLAST 1, HAS_TUSER 1, TUSER_WIDTH 1, HAS_TKEEP 0, HAS_TSTRB 0, FREQ_HZ 50000000" *)
    input  logic [7:0]  s_tdata,
    (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 S_AXIS TVALID" *) input  logic        s_tvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 S_AXIS TREADY" *) output logic        s_tready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 S_AXIS TLAST"  *) input  logic        s_tlast,
    (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 S_AXIS TUSER"  *) input  logic        s_tuser,

    // ---- 主端：64 bit AXIS（带 TKEEP） ----
    (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 M_AXIS TDATA" *)
    (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME M_AXIS, TDATA_NUM_BYTES 8, HAS_TLAST 1, HAS_TUSER 0, HAS_TKEEP 1, HAS_TSTRB 0, FREQ_HZ 50000000" *)
    output logic [63:0] m_tdata,
    (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 M_AXIS TKEEP"  *) output logic [7:0]  m_tkeep,
    (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 M_AXIS TVALID" *) output logic        m_tvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 M_AXIS TREADY" *) input  logic        m_tready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 M_AXIS TLAST"  *) output logic        m_tlast
);

    logic [63:0] acc_buf;
    logic [2:0]  fill;
    logic        beat_valid;
    logic [63:0] beat_data;
    logic [7:0]  beat_keep;
    logic        beat_last;

    assign s_tready = ~beat_valid;
    assign m_tdata  = beat_data;
    assign m_tkeep  = beat_keep;
    assign m_tvalid = beat_valid;
    assign m_tlast  = beat_last;

    wire accept = s_tvalid & s_tready;
    wire full   = (fill == 3'd7);
    // 本拍字节按小端并入累加器（acc_buf 在 beat 起点清 0，未填字节天然为 0）
    wire [63:0] cur = {56'd0, s_tdata} << (fill * 8);
    wire [63:0] acc = acc_buf | cur;

    always_ff @(posedge clk) begin
        if (!rstn) begin
            acc_buf    <= 64'd0;
            fill       <= 3'd0;
            beat_valid <= 1'b0;
            beat_data  <= 64'd0;
            beat_keep  <= 8'h00;
            beat_last  <= 1'b0;
        end else begin
            if (beat_valid && m_tready) begin
                beat_valid <= 1'b0;
            end
            if (accept) begin
                if (full || s_tlast) begin
                    beat_data  <= acc;
                    beat_keep  <= full ? 8'hFF : (8'hFF >> (3'd7 - fill));
                    beat_last  <= s_tlast;
                    beat_valid <= 1'b1;
                    acc_buf    <= 64'd0;
                    fill       <= 3'd0;
                end else begin
                    acc_buf[fill*8 +: 8] <= s_tdata;
                    fill                 <= fill + 3'd1;
                end
            end
        end
    end

endmodule