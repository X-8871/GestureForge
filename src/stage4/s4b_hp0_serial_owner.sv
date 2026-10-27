// s4b_hp0_serial_owner.sv —— HP0 单 master 串行化 owner（不新增 AXI master、不加互连）
//
// 协议（按 lead 裁 (a)）：
//   · 两个请求方：REQ_PREPROC(0) 与 REQ_NET(1)，各自 req/gnt/rel（grant 握手 + 释放）；
//   · 任一时刻**只有一个**请求方持有 HP0 通道（one-hot grant），持有期间另一方 req 保持即可排队；
//   · owner ledger 三态 + 故障隔离：
//       IDLE      —— 无在途请求，可授权；
//       GRANTED   —— 单一 owner 在途（busy 由外部 master 的 last 或 rel 决定）；
//       DRAINING  —— 收到释放但外部仍在途，等待排空；
//     FAULT 隔离另由上层（现有 adapter 账本）处理，本模块只保证"单 owner"不变量。
//   · 断言：gnt 必须 one-hot（至多一个）、GRANTED 期间不允许切换 owner、rel 只能由当前 owner 发。
//
// 说明：本模块只做**授权/串行化**，不含 AXI 信号；把 granted 请求方的 AXI 通道复用为同一 64 位 master
//       由上层 wrapper 选择（mux），本增量不包含该 mux 的 BD 接线。

`timescale 1ns / 1ps

module s4b_hp0_serial_owner (
    input  logic clk,
    input  logic rstn,

    // 请求方 0（预处理）
    input  logic req0,
    output logic gnt0,
    input  logic rel0,
    input  logic in_flight0,   // 外部 master 仍在途（由该请求方的 last 驱动）

    // 请求方 1（网络）
    input  logic req1,
    output logic gnt1,
    input  logic rel1,
    input  logic in_flight1,

    // 状态观测
    output logic [1:0] ledger_state,   // 0=IDLE, 1=GRANTED, 2=DRAINING
    output logic [0:0] owner_id,
    output logic       busy
);

    typedef enum logic [1:0] {ST_IDLE = 2'd0, ST_GRANTED = 2'd1, ST_DRAINING = 2'd2} state_t;
    state_t st, st_n;

    logic [0:0] owner_q, owner_n;
    logic       gnt0_q, gnt1_q;

    // 授权组合逻辑：IDLE 时按固定优先级（net 优先，保证推理不被预处理饿死；可在后续版本改轮转）
    always_comb begin
        st_n    = st;
        owner_n = owner_q;
        case (st)
        ST_IDLE: begin
            if (req1) begin
                st_n = ST_GRANTED; owner_n = 1'b1;
            end else if (req0) begin
                st_n = ST_GRANTED; owner_n = 1'b0;
            end
        end
        ST_GRANTED: begin
            if (owner_q ? (rel1 || !in_flight1) : (rel0 || !in_flight0)) begin
                st_n = ST_DRAINING;
            end
        end
        ST_DRAINING: begin
            // 等待外部排空：in_flight 低即视为排空（上层账本另判）
            if (!(owner_q ? in_flight1 : in_flight0)) begin
                st_n = ST_IDLE;
            end
        end
        default: st_n = ST_IDLE;
        endcase
    end

    always_ff @(posedge clk or negedge rstn) begin
        if (!rstn) begin
            st      <= ST_IDLE;
            owner_q <= 1'b0;
        end else begin
            st      <= st_n;
            owner_q <= owner_n;
        end
    end

    assign gnt0 = (st == ST_GRANTED) && (owner_q == 1'b0);
    assign gnt1 = (st == ST_GRANTED) && (owner_q == 1'b1);
    assign gnt0_q = gnt0;
    assign gnt1_q = gnt1;
    assign ledger_state = st;
    assign owner_id = owner_q;
    assign busy = (st != ST_IDLE);

    // synthesis translate_off
    always_ff @(posedge clk) begin
        if (rstn) begin
            if (gnt0 && gnt1) $error("[ASSERT] two owners granted simultaneously (one-hot violated)");
            if ((st == ST_GRANTED) && (st_n == ST_GRANTED) && (owner_n != owner_q))
                $error("[ASSERT] owner switched while GRANTED");
            if (rel0 && (owner_q != 1'b0)) $error("[ASSERT] rel0 from non-owner");
            if (rel1 && (owner_q != 1'b1)) $error("[ASSERT] rel1 from non-owner");
        end
    end
    // synthesis translate_on

endmodule