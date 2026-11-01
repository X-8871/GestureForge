// s4d_preproc_csr.sv —— 4-D 预处理 AXI4-Lite 控制寄存器（基址 0x43C10000）+ 总线兜底保护
//
// 本版新增（针对"PS 读 PL 永不返回 ⇒ 整机失去响应"的板级事故）：
//   1) **读超时兜底**：AR 被接受后，若 RD_TIMEOUT 拍内无法给出数据（内部依赖未就绪 / 从端被卡），
//      强制返回 RRESP=SLVERR 并记录 rd_to_cnt/last_err/STATUS[3]，**绝不让总线挂着**。
//   2) **写通道有界等待**：任何已提交（AW+W 均已捕获）的写，必在 WR_TIMEOUT 拍内给出 B 响应
//      （正常 OKAY 或超时 SLVERR）；AWREADY 的最坏等待被"B 必在 WR_TIMEOUT 内产生"上界约束。
//   3) **错误响应语义**（原先是静默忽略）：
//      · START 在 BUSY 期间 → SLVERR（last_err=1）
//      · WSTRB != 0xF（本从端不支持窄写） → SLVERR（last_err=4）
//      · 写保留/只读偏移 → SLVERR（last_err=5）
//      · 读超时 → SLVERR（last_err=2）；写超时 → SLVERR（last_err=3）
//   4) **可观测**：STATUS 增加 [3]=RD_TO_SEEN、[4]=WR_TO_SEEN；新增 0x20/0x24/0x28/0x2C 计数与错误码。
//
// 读侧仍保持 fail-safe：**合法偏移**的读永不因数据问题报错（除超时）；**保留偏移**读返回 0 且 OKAY
//   （不把"探测式读"当成错误，避免 PS 驱动误判）。
//
// 注入端口（仅用于 TB 证明超时路径；wrapper 内恒接 0）：
//   inj_rd_stall=1 让读内部"未就绪"，用于触发并验证读超时；inj_wr_stall=1 同理作用于写。

`timescale 1ns / 1ps

module s4d_preproc_csr #(
    parameter integer RD_TIMEOUT = 64,   // 拍（@100MHz = 640 ns）
    parameter integer WR_TIMEOUT = 64
) (
    input  logic        clk,
    input  logic        rstn,

    // AXI4-Lite 从端
    input  logic [5:0]  s_axi_awaddr,
    input  logic        s_axi_awvalid,
    output logic        s_axi_awready,
    input  logic [31:0] s_axi_wdata,
    input  logic [3:0]  s_axi_wstrb,
    input  logic        s_axi_wvalid,
    output logic        s_axi_wready,
    output logic [1:0]  s_axi_bresp,
    output logic        s_axi_bvalid,
    input  logic        s_axi_bready,
    input  logic [5:0]  s_axi_araddr,
    input  logic        s_axi_arvalid,
    output logic        s_axi_arready,
    output logic [31:0] s_axi_rdata,
    output logic [1:0]  s_axi_rresp,
    output logic        s_axi_rvalid,
    input  logic        s_axi_rready,

    // 与预处理引擎的握手
    output logic        start_pulse,
    input  logic        busy,
    input  logic        done,
    output logic [31:0] done_count,

    // 测试注入（真实集成恒 0）
    input  logic        inj_rd_stall,
    input  logic        inj_wr_stall
);

    localparam logic [31:0] ID_VALUE = 32'h5334_4450;
    localparam logic [31:0] BYTES    = 32'd519168;
    localparam logic [1:0]  OKAY = 2'b00, SLVERR = 2'b10;

    // 错误码
    localparam logic [2:0] E_NONE = 3'd0, E_ILLEGAL = 3'd1, E_RD_TO = 3'd2,
                           E_WR_TO = 3'd3, E_STROBE = 3'd4, E_ADDR = 3'd5;

    logic        done_sticky, error_sticky;
    logic [31:0] done_cnt_q;

    // 写通道捕获与超时
    logic        aw_hit, w_hit;
    logic [31:0] awaddr_q, wdata_q;
    logic [3:0]  wstrb_q;
    logic [7:0]  wr_wait;
    logic        wr_stalled;

    // 读通道超时
    logic        rd_pending;
    logic [7:0]  rd_wait;

    // 错误记录（只由下方"记账"单块驱动，避免多 procedural driver）
    logic [31:0] rd_to_cnt_q, wr_to_cnt_q;
    logic [2:0]  last_err_q;
    logic        rd_to_seen, wr_to_seen;
    // 事件脉冲（由读/写通道各自产生，记账块消费）
    logic        ev_rd_to, ev_wr_to, ev_wr_err, ev_irq_clr;
    logic [2:0]  wr_code;

    assign s_axi_awready = !aw_hit && !s_axi_bvalid;
    assign s_axi_wready  = !w_hit  && !s_axi_bvalid;
    assign s_axi_arready = !s_axi_rvalid && !rd_pending;

    // 地址是否可写（写语义受限）
    function automatic logic wr_addr_ok(input logic [5:0] a);
        wr_addr_ok = (a == 6'h04) || (a == 6'h1C);
    endfunction

    // 读数据译码（组合，供正常路径与超时后的后续事务共用）
    function automatic logic [31:0] rd_decode(input logic [5:0] a);
        case (a)
            6'h00: rd_decode = ID_VALUE;
            6'h04: rd_decode = 32'd0;                                  // CTRL 读回 0（START 自清）
            6'h08: rd_decode = {27'd0, wr_to_seen, rd_to_seen, error_sticky, done_sticky, busy};
            6'h0C: rd_decode = BYTES;
            6'h10: rd_decode = {16'd312, 16'd416};
            6'h14: rd_decode = {16'd52,  16'd0};
            6'h18: rd_decode = done_cnt_q;
            6'h20: rd_decode = rd_to_cnt_q;
            6'h24: rd_decode = wr_to_cnt_q;
            6'h28: rd_decode = {29'd0, last_err_q};
            6'h2C: rd_decode = {29'd0, wr_to_seen, rd_to_seen, 1'b0};
            default: rd_decode = 32'd0;                                // 保留偏移：0 + OKAY
        endcase
    endfunction

    // ======================= 写通道 =======================
    always_ff @(posedge clk or negedge rstn) begin
        if (!rstn) begin
            aw_hit       <= 1'b0;
            w_hit        <= 1'b0;
            awaddr_q     <= 32'd0;
            wdata_q      <= 32'd0;
            wstrb_q      <= 4'd0;
            s_axi_bvalid <= 1'b0;
            s_axi_bresp  <= OKAY;
            start_pulse  <= 1'b0;
            done_sticky  <= 1'b0;
            done_cnt_q   <= 32'd0;
            done_count   <= 32'd0;
            wr_wait      <= 8'd0;
            wr_stalled   <= 1'b0;
            ev_wr_to     <= 1'b0;
            ev_wr_err    <= 1'b0;
            ev_irq_clr   <= 1'b0;
            wr_code      <= E_NONE;
        end else begin
            start_pulse <= 1'b0;
            ev_wr_to    <= 1'b0;
            ev_wr_err   <= 1'b0;
            ev_irq_clr  <= 1'b0;

            if (s_axi_awvalid && s_axi_awready) begin
                aw_hit   <= 1'b1;
                awaddr_q <= s_axi_awaddr;
            end
            if (s_axi_wvalid && s_axi_wready) begin
                w_hit   <= 1'b1;
                wdata_q <= s_axi_wdata;
                wstrb_q <= s_axi_wstrb;
            end

            // ---- 写完成（或超时兜底）----
            if (aw_hit && w_hit && !s_axi_bvalid) begin
                if (inj_wr_stall && !wr_stalled) begin
                    // 内部"未就绪"：进入有界等待
                    wr_stalled <= 1'b1;
                    wr_wait    <= 8'd0;
                end else if (wr_stalled) begin
                    if (wr_wait + 8'd1 >= WR_TIMEOUT[7:0]) begin
                        // 超时：给 B=SLVERR，绝不无限挂
                        s_axi_bvalid <= 1'b1;
                        s_axi_bresp  <= SLVERR;
                        aw_hit       <= 1'b0;
                        w_hit        <= 1'b0;
                        wr_stalled   <= 1'b0;
                        wr_wait      <= 8'd0;
                        ev_wr_to     <= 1'b1;
                    end else begin
                        wr_wait <= wr_wait + 8'd1;
                    end
                end else begin
                    // 正常完成 + 语义检查
                    aw_hit       <= 1'b0;
                    w_hit        <= 1'b0;
                    s_axi_bvalid <= 1'b1;
                    if (wstrb_q != 4'hF) begin
                        s_axi_bresp <= SLVERR; ev_wr_err <= 1'b1; wr_code <= E_STROBE;
                    end else if (!wr_addr_ok(awaddr_q[5:0])) begin
                        s_axi_bresp <= SLVERR; ev_wr_err <= 1'b1; wr_code <= E_ADDR;
                    end else if (awaddr_q[5:0] == 6'h04 && wdata_q[0] && busy) begin
                        // START 在 BUSY 期间：明确报错，不再静默吞掉
                        s_axi_bresp <= SLVERR; ev_wr_err <= 1'b1; wr_code <= E_ILLEGAL;
                    end else begin
                        s_axi_bresp <= OKAY;
                        // CTRL.START
                        if (awaddr_q[5:0] == 6'h04 && wdata_q[0]) begin
                            start_pulse <= 1'b1;
                            done_sticky <= 1'b0;
                        end
                        // IRQ_CLR：清 sticky 与错误记录
                        if (awaddr_q[5:0] == 6'h1C && wdata_q[0]) begin
                            ev_irq_clr  <= 1'b1;
                            done_sticky <= 1'b0;     // 注意：done_sticky 由本通道驱动，不能只在记账块清
                        end
                    end
                end
            end

            if (s_axi_bvalid && s_axi_bready) s_axi_bvalid <= 1'b0;

            if (done) begin
                done_sticky <= 1'b1;
                if (done_cnt_q != 32'hFFFF_FFFF) done_cnt_q <= done_cnt_q + 32'd1;
            end
            done_count <= done_cnt_q;
        end
    end

    // ======================= 读通道（含超时兜底） =======================
    always_ff @(posedge clk or negedge rstn) begin
        if (!rstn) begin
            s_axi_rvalid <= 1'b0;
            s_axi_rdata  <= 32'd0;
            s_axi_rresp  <= OKAY;
            rd_pending   <= 1'b0;
            rd_wait      <= 8'd0;
            ev_rd_to     <= 1'b0;
        end else begin
            ev_rd_to <= 1'b0;          // 单拍脉冲（否则会永久占住记账分支）
            if (s_axi_arvalid && s_axi_arready) begin
                rd_wait <= 8'd0;
                if (inj_rd_stall) begin
                    // 内部依赖未就绪：挂起等待，由超时兜底
                    rd_pending <= 1'b1;
                    s_axi_rresp <= SLVERR;      // 若最终超时，用它返回
                end else begin
                    rd_pending   <= 1'b0;
                    s_axi_rvalid <= 1'b1;
                    s_axi_rresp  <= OKAY;
                    s_axi_rdata  <= rd_decode(s_axi_araddr[5:0]);
                end
            end else if (rd_pending) begin
                if (rd_wait + 8'd1 >= RD_TIMEOUT[7:0]) begin
                    // 超时：强制 R=SLVERR，数据无意义（给 0）
                    s_axi_rvalid <= 1'b1;
                    s_axi_rresp  <= SLVERR;
                    s_axi_rdata  <= 32'd0;
                    rd_pending   <= 1'b0;
                    rd_wait      <= 8'd0;
                    ev_rd_to     <= 1'b1;
                end else begin
                    rd_wait <= rd_wait + 8'd1;
                end
            end

            if (s_axi_rvalid && s_axi_rready) s_axi_rvalid <= 1'b0;
        end
    end

    // ======================= 错误记账（唯一驱动源） =======================
    always_ff @(posedge clk or negedge rstn) begin
        if (!rstn) begin
            rd_to_cnt_q  <= 32'd0;
            wr_to_cnt_q  <= 32'd0;
            last_err_q   <= E_NONE;
            rd_to_seen   <= 1'b0;
            wr_to_seen   <= 1'b0;
            error_sticky <= 1'b0;
        end else if (ev_irq_clr) begin
            // 清标志与错误码；计数器保留（诊断需累计值）
            rd_to_seen   <= 1'b0;
            wr_to_seen   <= 1'b0;
            last_err_q   <= E_NONE;
            error_sticky <= 1'b0;
        end else if (ev_rd_to) begin
            last_err_q   <= E_RD_TO;
            rd_to_seen   <= 1'b1;
            error_sticky <= 1'b1;
            if (rd_to_cnt_q != 32'hFFFF_FFFF) rd_to_cnt_q <= rd_to_cnt_q + 32'd1;
        end else if (ev_wr_to) begin
            last_err_q   <= E_WR_TO;
            wr_to_seen   <= 1'b1;
            error_sticky <= 1'b1;
            if (wr_to_cnt_q != 32'hFFFF_FFFF) wr_to_cnt_q <= wr_to_cnt_q + 32'd1;
        end else if (ev_wr_err) begin
            last_err_q   <= wr_code;
            error_sticky <= 1'b1;
        end
    end

endmodule
