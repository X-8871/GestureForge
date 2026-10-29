// s4d_preproc_out_axis.sv —— 把 INT8 CHW 输出字节流封成 AXI4-Stream
//
// 作用：引擎输出是"valid/data/last + ready"的字节流；接 VDMA/DMA 需要 AXIS。
//   本模块加 8 深 FIFO（吸收短时阻塞，避免引擎频繁停顿）+ **tuser=帧首标记**（便于 VDMA 做 frame sync）。
//
// 语义：
//   · 每帧 = 519,168 字节，**第一个字节 tuser=1**（其余 0），**最后一个字节 tlast=1**；
//   · 满/空反压：s_ready=!full，m_tvalid=!empty；**不丢字节**（FIFO 满时压住上游，
//     引擎侧已实现 m_ready 停顿语义）；
//   · tuser 由帧边界自动生成：复位后首字节置 1；每次压入 tlast 字节后，下一个字节重新置 1。
//
// 边界：不做位宽转换（保持 8 bit，匹配 INT8 CHW）；不做跨帧粘连检查（由上层 VDMA 管）。

`timescale 1ns / 1ps

module s4d_preproc_out_axis #(
    parameter integer DEPTH = 8
) (
    input  logic        clk,
    input  logic        rstn,

    // ---- 上游：引擎字节流 ----
    input  logic        s_valid,
    input  logic [7:0]  s_data,
    input  logic        s_last,
    output logic        s_ready,

    // ---- 下游：AXI4-Stream 主口 ----
    (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 M_AXIS_TDATA"  *) output logic [7:0]  m_axis_tdata,
    (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 M_AXIS_TVALID" *) output logic        m_axis_tvalid,
    (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 M_AXIS_TREADY" *) input  logic        m_axis_tready,
    (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 M_AXIS_TLAST"  *) output logic        m_axis_tlast,
    (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 M_AXIS_TUSER"  *)
    (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME M_AXIS, TDATA_NUM_BYTES 1, TDEST_WIDTH 0, TID_WIDTH 0, TUSER_WIDTH 1, HAS_TLAST 1, HAS_TKEEP 0, HAS_TSTRB 0, HAS_TREADY 1, HAS_TUSER 1, FREQ_HZ 100000000, PHASE 0.000" *)
    output logic        m_axis_tuser,

    output logic [31:0] pushed_cnt,
    output logic [31:0] popped_cnt
);

    logic [7:0] fifo_data [0:DEPTH-1];
    logic       fifo_last [0:DEPTH-1];
    logic       fifo_user [0:DEPTH-1];
    logic [$clog2(DEPTH):0] cnt;
    logic [$clog2(DEPTH)-1:0] wr_ptr, rd_ptr;
    logic        fs_pending;

    logic full, empty, push, pop;

    assign full  = (cnt == DEPTH[$clog2(DEPTH):0]);
    assign empty = (cnt == 0);
    assign s_ready = !full;
    assign m_axis_tvalid = !empty;
    assign m_axis_tdata  = fifo_data[rd_ptr];
    assign m_axis_tlast  = fifo_last[rd_ptr];
    assign m_axis_tuser  = fifo_user[rd_ptr];

    assign push = s_valid && s_ready;
    assign pop  = m_axis_tvalid && m_axis_tready;

    always_ff @(posedge clk or negedge rstn) begin
        if (!rstn) begin
            cnt           <= '0;
            wr_ptr        <= '0;
            rd_ptr        <= '0;
            fs_pending    <= 1'b1;      // 复位后第一个字节即帧首
            pushed_cnt    <= 32'd0;
            popped_cnt    <= 32'd0;
        end else begin
            if (push) begin
                fifo_data[wr_ptr] <= s_data;
                fifo_last[wr_ptr] <= s_last;
                fifo_user[wr_ptr] <= fs_pending;
                wr_ptr            <= wr_ptr + 1'b1;
                fs_pending        <= s_last;      // 本条是帧尾 → 下一条是帧首
                pushed_cnt        <= pushed_cnt + 32'd1;
            end
            if (pop) begin
                rd_ptr     <= rd_ptr + 1'b1;
                popped_cnt <= popped_cnt + 32'd1;
            end
            case ({push, pop})
                2'b10: cnt <= cnt + 1'b1;
                2'b01: cnt <= cnt - 1'b1;
                default: cnt <= cnt;
            endcase
        end
    end

endmodule
