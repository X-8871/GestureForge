// s4d_axi4_rd_shim.sv —— 把"突发语义简单口"接到 AXI4 读主口（AR/R），**按 4KB 边界动态拆分**
//
// 上游（引擎）接口语义：
//   rd_req 电平请求，保持到 rd_ack；rd_addr 字节地址（须 8 B 对齐）；rd_beats 本次 beat 数；
//   rd_ack 单拍接受；之后主端回 rd_valid/rd_data，上游用 rd_ready 反压。
// 下游（AXI4）：
//   AR：araddr/arlen/arsize/arburst/arvalid/arready
//   R ：rdata/rresp/rlast/rvalid/rready（读通道，无 W 通道；本模块不发写）
//
// 为什么必须拆 4KB（MAJ-2）：
//   AXI 规定 INCR 突发不得跨 4 KB 边界（AXI3/AXI4 同）。本设计一次"载一行"=1920 B，
//   行基址 = sy*1920，并不对齐 4096 ⇒ 实测 1,443 次请求里有 630 次跨 4 KB。
//   该 BD 的 HP0 在 PS 侧是 **AXI3**（SmartConnect 做 AXI4→AXI3 转换），跨 4KB 的突发属违规，
//   行为不被保证。故在 shim 内按边界拆块，上游完全无感（仍是连续 beat 流）。
//
// 拆分规则（每块同时满足三条）：
//   ① 不跨 4 KB：块字节数 ≤ 4096 - (addr & 0xFFF)
//   ② ≤ AXI4 单笔上限 256 beat（=2048 B）
//   ③ 8 B 对齐：addr 本身 8 B 对齐且 4 KB 边界余量必为 8 的倍数 ⇒ 块字节数必为 8 的倍数
//   ⇒ arlen = 块 beat 数 - 1，恒 ≤ 255（8 位字段够用，见 README「arlen 位宽」说明）
//
// 设计取舍：
//   · **接受请求即 ack**（不等 AR 握手），把"请求已收下"和"数据何时到"解耦；
//   · arsize 固定 3（8 B/beat）、arburst 固定 INCR；
//   · 不做 outstanding 排队（同一时刻只有 1 笔未完成突发），与引擎"一次只载一行"的用法匹配；
//   · rresp != OKAY 时置 err_sticky 供上层观测（引擎不消费，属已知边界）。

`timescale 1ns / 1ps

module s4d_axi4_rd_shim (
    input  logic        clk,
    input  logic        rstn,

    // ---- 上游：突发语义简单口 ----
    input  logic        rd_req,
    input  logic [31:0] rd_addr,
    input  logic [9:0]  rd_beats,
    output logic        rd_ack,
    output logic        rd_valid,
    output logic [63:0] rd_data,
    input  logic        rd_ready,

    // ---- 下游：AXI4 读主口 ----
    output logic [31:0] m_axi_araddr,
    output logic [7:0]  m_axi_arlen,
    output logic [2:0]  m_axi_arsize,
    output logic [1:0]  m_axi_arburst,
    output logic        m_axi_arvalid,
    input  logic        m_axi_arready,
    input  logic [63:0] m_axi_rdata,
    input  logic [1:0]  m_axi_rresp,
    input  logic        m_axi_rlast,
    input  logic        m_axi_rvalid,
    output logic        m_axi_rready,

    // ---- 状态 ----
    output logic        busy,
    output logic        err_sticky,
    // ---- 观测：本次请求被拆成多少块（= 实际 AR 笔数），供 TB/上层对账 ----
    output logic [15:0] chunk_cnt
);

    localparam logic [12:0] PAGE_BYTES = 13'd4096;
    localparam logic [9:0]  MAX_BEATS  = 10'd256;      // AXI4 INCR 单笔上限

    typedef enum logic [1:0] {S_IDLE, S_AR, S_R} state_t;
    state_t st;

    logic [31:0] nxt_addr;      // 下一块的起始字节地址（8 B 对齐）
    logic [9:0]  remain_b;      // 尚未发出的 beat 数
    logic [9:0]  chunk_new;     // 新请求首块 beat 数
    logic [9:0]  chunk_nxt;     // 后续块 beat 数
    logic [15:0] chunk_c;       // 本次请求已发起的块数

    // 单块 beat 数：min(剩余, 到 4KB 边界可容纳 beat, 256)
    function automatic logic [9:0] chunk_of (input logic [31:0] a, input logic [9:0] b);
        logic [12:0] to_page;   // 到 4 KB 边界剩余字节（8 的倍数，1..4096）
        logic [9:0]  page_b;    // 该地址起 4 KB 内可容纳的 beat 数（1..512）
        logic [9:0]  c;
        begin
            to_page = PAGE_BYTES - {1'b0, a[11:0]};
            page_b  = to_page[12:3];
            c       = (b < page_b) ? b : page_b;
            chunk_of = (c > MAX_BEATS) ? MAX_BEATS : c;
        end
    endfunction

    always_comb chunk_new = chunk_of(rd_addr,  rd_beats);
    always_comb chunk_nxt = chunk_of(nxt_addr, remain_b);

    always_ff @(posedge clk or negedge rstn) begin
        if (!rstn) begin
            st              <= S_IDLE;
            rd_ack          <= 1'b0;
            nxt_addr        <= 32'd0;
            remain_b        <= 10'd0;
            chunk_c         <= 16'd0;
            m_axi_araddr    <= 32'd0;
            m_axi_arlen     <= 8'd0;
            m_axi_arsize    <= 3'd3;      // 8 B/beat
            m_axi_arburst   <= 2'b01;     // INCR
            m_axi_arvalid   <= 1'b0;
            err_sticky      <= 1'b0;
            busy            <= 1'b0;
            chunk_cnt       <= 16'd0;
        end else begin
            rd_ack <= 1'b0;

            case (st)
                S_IDLE: begin
                    busy <= 1'b0;
                    if (rd_req) begin
                        // 收下请求：立即 ack；只发起**首块**，其余块在 rlast 时续发
                        rd_ack        <= 1'b1;
                        m_axi_araddr  <= rd_addr;
                        m_axi_arlen   <= chunk_new[7:0] - 8'd1;
                        m_axi_arvalid <= 1'b1;
                        remain_b      <= rd_beats - chunk_new;
                        nxt_addr      <= rd_addr + {19'd0, chunk_new, 3'b000};
                        chunk_c       <= 16'd1;
                        busy          <= 1'b1;
                        st            <= S_AR;
                    end
                end

                S_AR: begin
                    if (m_axi_arready) begin
                        m_axi_arvalid <= 1'b0;
                        st            <= S_R;
                    end
                end

                S_R: begin
                    if (m_axi_rvalid && rd_ready && m_axi_rlast) begin
                        if (remain_b == 10'd0) begin
                            busy      <= 1'b0;
                            chunk_cnt <= chunk_c;
                            st        <= S_IDLE;
                        end else begin
                            // 续发下一块（地址已按上一块长度前移，天然不跨 4 KB）
                            m_axi_araddr  <= nxt_addr;
                            m_axi_arlen   <= chunk_nxt[7:0] - 8'd1;
                            m_axi_arvalid <= 1'b1;
                            remain_b      <= remain_b - chunk_nxt;
                            nxt_addr      <= nxt_addr + {19'd0, chunk_nxt, 3'b000};
                            chunk_c       <= chunk_c + 16'd1;
                            st            <= S_AR;
                        end
                    end
                end

                default: st <= S_IDLE;
            endcase

            // 错误粘滞（rresp != OKAY 记为 2'b10=SLVERR / 3=DECERR，此处只置标志）
            if (m_axi_rvalid && rd_ready && (m_axi_rresp != 2'b00)) err_sticky <= 1'b1;
        end
    end

    // 读数据直通（组合），rready 由上游反压决定
    assign rd_valid      = m_axi_rvalid;
    assign rd_data       = m_axi_rdata;
    assign m_axi_rready  = rd_ready && (st == S_R);

endmodule
