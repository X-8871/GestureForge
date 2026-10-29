// s4d_preproc_engine_v2.sv —— 4-D 预处理 v2：行缓冲 + 突发读 + 查表（无除法器）
//
// 【流水版 planB-4拍（2026-10-29 Wong 批准）】S_XCALC 单拍算术链拆 4 拍：
//   S_XADDR（坐标查表 + bank 读 + 流水寄存）→ S_XMUL（行插值 top/bot_q24，2 DSP 并行）
//   → S_XCOL（列插值 v_q48）→ S_XQ（量化 + 输出）。
//   只加流水寄存器与新状态，**定点算术逐字未改、状态机分支语义未改**（can_put 握手照搬）。
//   代价：活跃像素 2 拍 → 4 拍（每像素 +2 拍）；pad 行与载行不变。
//   依据：3 拍版 top10 全在双线性链（16.688 ns，DSP×4+CARRY×18），行/列各一拍后估 ~9 ns。
//
// 相对 v1 的三处结构性改动（定点数学**一字未改**，故输出必须与 v1/golden 逐字节相同）：
//   1) 数据面：v1 每个活跃输出像素发 4 次**单字节随机读**（1,557,504 次/帧，单 outstanding，
//      帧率被 AXI 延迟锁死）。v2 改为**按行突发**：每行 1920 B = 240 beat × 64 bit，
//      一次突发取回整行，落到片上行缓存；滤波器只读 BRAM。
//   2) 行缓存：4 个 bank（top-even / top-odd / bot-even / bot-odd），各 320×24 bit。
//      按像素奇偶分 bank ⇒ 同一拍可并行读到 (sx, sx+1) 的行对 4 个抽头，1 拍拿全。
//   3) 坐标：v1 用 64 位除常量（`(y*479)<<24 / 311`）同拍算完，综合 WNS −8.872 ns @100 MHz。
//      v2 改为**查表**（`s4d_coord_tables.svh`，728 项已与公式逐项 assert 相等）：
//      硬件里不再有除法器，S_ROW 变成 1 拍 ROM 读。比"行首流水"更彻底且无精度风险。
//
// 边界：
//   · 读口是"突发语义"的简单口（req/ack + beat 流）；到 AXI4 AR/R 的适配由 s4d_axi4_rd_shim.sv 提供（含 4KB 拆块）；
//   · 不做行复用优化（sy 不变时复用缓存；变了就整对重载，约 0.65 次/输出行）；
//   · 不重叠"加载下一行"与"计算当前行"（串行，简单可靠；重叠可再省约 20%）。
//
// 尺寸（由 TB 实测 cycles 折算，见 README）：
//   计算 ≈ 2 拍/输出字节；加载 ≈ 880 拍/行 × 约 541 行/平面 × 3 平面。

`timescale 1ns / 1ps

`include "s4d_coord_tables.svh"

module s4d_preproc_engine_v2 #(
    parameter integer SRC_W  = 640,
    parameter integer SRC_H  = 480,
    parameter integer DST_W  = 416,   // 输出宽（含左右 pad，本方案 pad=0）
    parameter integer DST_H  = 416,   // 输出高（含上下各 52 行 pad）
    parameter integer NEW_W  = 416,
    parameter integer NEW_H  = 312,
    parameter integer OFF_Y  = 52,
    parameter integer BEATS_PER_ROW = 240    // 1920 B / 8 B
) (
    input  logic        clk,
    input  logic        rstn,

    input  logic        start,
    output logic        busy,
    output logic        done,

    // ---- 突发读口（64 bit beat） ----
    output logic        rd_req,
    output logic [31:0] rd_addr,      // 字节地址（8 B 对齐）
    output logic [9:0]  rd_beats,     // 本次突发 beat 数
    input  logic        rd_ack,       // 主端接受请求（1 拍）
    input  logic        rd_valid,     // 返回 beat
    input  logic [63:0] rd_data,
    output logic        rd_ready,     // 本引擎可接收 beat

    // ---- 输出字节流（CHW 连续；带反压） ----
    output logic        m_valid,
    output logic [7:0]  m_data,
    output logic        m_last,
    input  logic        m_ready,

    output logic [31:0] byte_count
);

    // ---------------------------------------------------------------- 常量
    localparam logic [24:0] ONE24 = 25'd16_777_216;        // 2^24
    localparam logic [7:0]  PAD_Q = 8'd64;                 // quant(0.5/(1/127)) = round(63.5)
    localparam logic [31:0] ROW_BYTES = SRC_W * 3;         // 1920
    localparam logic [9:0]  PX_N      = SRC_W[9:0];        // 640 像素/行

    // ---------------------------------------------------------------- 行缓存
    // 像素字：{R,G,B}，即 [23:16]=R、[15:8]=G、[7:0]=B（源为 BGR888 紧排）
    // 按像素奇偶分 bank：px 偶数 → bank0/bank2，px 奇数 → bank1/bank3
    // 方案 A：显式 ram_style=distributed。4 bank 各仅 1 写口（S_LOAD_STREAM）+ 1 读口
    //（见下方"缓存读口"），满足 LUTRAM 推断条件；不改任何算术与状态机时序。
    (* ram_style = "distributed" *) logic [23:0] bank0 [0:319];   // top row, 偶像素
    (* ram_style = "distributed" *) logic [23:0] bank1 [0:319];   // top row, 奇像素
    (* ram_style = "distributed" *) logic [23:0] bank2 [0:319];   // bot row, 偶像素
    (* ram_style = "distributed" *) logic [23:0] bank3 [0:319];   // bot row, 奇像素

    // ---------------------------------------------------------------- 打包器（beat → 像素字）
    logic [127:0] hold;           // 字节暂存（最多两 beat）
    logic [4:0]   hcnt;           // hold 中有效字节数
    logic [9:0]   wr_px;          // 下一个待写像素号 0..639
    logic         pack_en;

    // 上限 5：接受后 hcnt 最多 13 ≤ 16（hold 为 128 bit），避免移位溢出丢字节
    assign rd_ready = pack_en && (hcnt <= 5'd5);

    // 「同一拍内先弹像素、再追加 beat」
    //   —— 若两者互斥（先前的写法），8 字节要花 4 拍，填充只有 2 B/cycle，
    //      整个加载期被拖成 960 拍/行（实测把整帧推到 >2.5M cycles）。合并后为 640 拍/行（写口下限）。
    logic [127:0] hold_n;
    logic [4:0]   hcnt_n;
    logic [23:0]  px_out;
    logic         px_wr;
    logic         beat_take;

    assign beat_take = rd_valid && rd_ready && pack_en;

    always_comb begin
        hold_n = hold;
        hcnt_n = hcnt;
        px_out = 24'd0;
        px_wr  = 1'b0;
        if (hcnt >= 5'd3) begin
            px_out = hold[23:0];
            px_wr  = 1'b1;
            hold_n = hold >> 24;
            hcnt_n = hcnt - 5'd3;
        end
        if (beat_take) begin
            hold_n = hold_n | ({64'd0, rd_data} << {hcnt_n, 3'b000});
            hcnt_n = hcnt_n + 5'd8;
        end
    end

    // ---------------------------------------------------------------- 坐标查表
    logic [8:0]  y_eff;
    logic [8:0]  ox, oy;
    logic [1:0]  plane;

    always_comb y_eff = (oy >= OFF_Y) ? (oy - OFF_Y) : 9'd0;

    logic [33:0] sy_q, sx_q;
    always_comb sy_q = sy_q_of(y_eff);
    always_comb sx_q = sx_q_of(ox);

    logic [9:0]  sy_int, sy1_int;
    logic [23:0] dy_q;
    logic [9:0]  sx_int, sx1_int;
    logic [23:0] dx_q;

    always_comb begin
        sy_int  = sy_q[33:24];
        dy_q    = sy_q[23:0];
        sy1_int = (sy_int + 10'd1 < SRC_H) ? (sy_int + 10'd1) : (SRC_H - 1);
        sx_int  = sx_q[33:24];
        dx_q    = sx_q[23:0];
        sx1_int = (sx_int + 10'd1 < SRC_W) ? (sx_int + 10'd1) : (SRC_W - 1);
    end

    // 缓存有效行号（初值设为不可达值，强制首次必载）
    logic [9:0] cached_lo, cached_hi;
    // 行复用：sy 步进为 1 时，旧 bot 直接升为 new top，只需再载 1 行（省 23% 加载量）
    logic       sel_flip;      // 0：top 在 bank0/1、bot 在 bank2/3；1：互换
    logic       single_load;   // 1 = 本轮只载一行
    logic       load_phase;    // 0 = 第一行，1 = 第二行（整对重载时用）

    // ---------------------------------------------------------------- 读取地址（1 拍并行）
    // 像素 sx 与 sx+1 必为"一奇一偶"⇒ 一个在偶 bank、一个在奇 bank，各读 1 次即可。
    logic [8:0] a_even, a_odd;
    // 注意：必须用 sx_int[9:1]（10 位整体右移），不能写 sx_int[8:0]>>1
    // —— 后者丢掉 bit9，sx ≥ 512 时地址回绕（表现为"从 x=332 起整段错"）。
    always_comb begin
        if (sx_int[0] == 1'b0) begin
            a_even = sx_int[9:1];      // sx 在偶 bank
            a_odd  = sx1_int[9:1];     // sx+1 在奇 bank
        end else begin
            a_even = sx1_int[9:1];     // sx+1 在偶 bank
            a_odd  = sx_int[9:1];      // sx 在奇 bank
        end
    end

    logic [23:0] d_top_e, d_top_o, d_bot_e, d_bot_o;

    // ---- 流水寄存器（拍1 = S_XADDR 沿打入；拍2 = S_XMUL 消费）----
    // 与 d_* 同一沿打入 ⇒ 与 bank 读数据严格配对（同一像素的奇偶/边界/权重）。
    // 无需复位：rstn=0 期间 st=S_IDLE 不会进 S_XADDR，读前必写（同 d_* 论证）。
    logic        p_swap;    // = sx_int[0]，tap 左右还原方向
    logic        p_edge;    // = (sx_int == sx1_int)，右边界（左右 tap 同址）
    logic [23:0] p_dx_q;    // = dx_q，x 方向权重 Q24
    logic [23:0] p_dy_q;    // = dy_q，y 方向权重 Q24（行级常量，寄存以免 sy 查表进列插值拍路径）
    logic [24:0] p_dy_inv_q; // = ONE24 - dy_q（行级常量，拍1 沿寄存；planA：把 25 位减法移出拍3 关键路径）
    logic [33:0] p_top24;   // 拍2 = S_XMUL 沿打入 = top_q24（行插值结果）；拍3 = S_XCOL 消费
    logic [33:0] p_bot24;   // 拍2 = S_XMUL 沿打入 = bot_q24；拍3 = S_XCOL 消费
    logic [33:0] p_vq24;    // 拍3 = S_XCOL 沿打入 = v_q48[57:24]；拍4 = S_XQ 量化输入

    // ---------------------------------------------------------------- 滤波算术（与 v1 逐字一致）
    logic [7:0]  p_tl, p_tr, p_bl, p_br;
    logic [33:0] top_q24, bot_q24;
    logic [63:0] v_q48;
    logic [39:0] num_q;
    logic [7:0]  q_byte;

    logic [8:0] src_ch;     // 2 - plane（BGR 源 ⇒ plane0=R=ch2）

    always_comb src_ch = 9'd2 - {7'd0, plane};

    // 奇偶分 bank 后必须按 sx 的奇偶把 (左, 右) 还原：
    //   sx 偶 ⇒ 左在偶 bank、右在奇 bank；sx 奇 ⇒ 反之。
    //   （漏了这一步会让奇数 sx 的左右 tap 互换，表现为"差 1 个像素"的 1 LSB 偏移）
    // 流水版：sx_int[0] 在拍1 沿已寄存为 p_swap（与 d_* 同像素配对），此处语义不变。
    logic [23:0] t_l, t_r, b_l, b_r;
    always_comb begin
        if (p_swap) begin
            t_l = d_top_o;  t_r = d_top_e;
            b_l = d_bot_o;  b_r = d_bot_e;
        end else begin
            t_l = d_top_e;  t_r = d_top_o;
            b_l = d_bot_e;  b_r = d_bot_o;
        end
    end

    always_comb begin
        p_tl = t_l[8*src_ch[1:0] +: 8];
        p_tr = p_edge ? p_tl : t_r[8*src_ch[1:0] +: 8];
        p_bl = b_l[8*src_ch[1:0] +: 8];
        p_br = p_edge ? p_bl : b_r[8*src_ch[1:0] +: 8];
    end

    always_comb top_q24 = ((ONE24 - {1'b0, p_dx_q}) * p_tl) + ({1'b0, p_dx_q} * p_tr);
    always_comb bot_q24 = ((ONE24 - {1'b0, p_dx_q}) * p_bl) + ({1'b0, p_dx_q} * p_br);
    // 列插值（拍3）：输入 = 拍2 沿寄存的行插值结果，数值与原单拍链的 top_q24/bot_q24 相同。
    always_comb v_q48  = (p_dy_inv_q * p_top24) + ({1'b0, p_dy_q} * p_bot24);

    // ---- 量化：q = round_away(P*127/255)，P = 像素值 [0,255]（v_q24 = P·2^24）----
    //   原式 (2N + D)/(2D) 中 D = 255·2^24，等价于 q = floor((2·num + 255·2^24) / (510·2^24))
    //   本实现**不含除法器**，只用移位/加法/一次 17×16 乘（可落 1 个 DSP 或纯 LUT）：
    //     h     = (num >> 23) + 255          // 恒等式：floor(W/(510·2^24)) = floor((W>>24)/510)
    //     q     = floor(h/510) = (floor(h/255)) >> 1
    //     floor(h/255) = (h × 65794) >> 24   // 对 h ∈ [0, 65025] 精确（穷举验证见 README §13）
    //   值域：h ≤ 65025 ⇒ q ≤ 127，天然无溢出，无需钳位（v1 的 127 钳位在此不可达）。
    logic [17:0] h_sum;
    logic [35:0] h_mul;
    logic [7:0]  q255;
    always_comb num_q   = ({6'd0, p_vq24} << 7) - {6'd0, p_vq24};   // ×127，移位减法
    always_comb h_sum   = (num_q >> 23) + 18'd255;
    always_comb h_mul   = h_sum * 18'd65794;
    always_comb q255    = h_mul >> 24;                                // = floor(h/255)
    always_comb q_byte  = q255 >> 1;                                  // = floor(h/510)

    // ---------------------------------------------------------------- FSM
    typedef enum logic [3:0] {
        S_IDLE, S_ROW, S_LOAD_REQ, S_LOAD_STREAM, S_XADDR, S_XMUL, S_XCOL, S_XQ, S_ROW_ADV, S_FIN
    } state_t;
    state_t st;

    logic in_pad_row;
    always_comb in_pad_row = (oy < OFF_Y) || (oy >= (OFF_Y + NEW_H));

    // 反压：只有"当前无字节在飞"或"在飞字节已被取走"才能产新字节。
    // 不实现该逻辑则下游一停就必丢字节（AXIS 封装的前提）。
    logic can_put;
    always_comb can_put = (!m_valid) || m_ready;

    // 加载目标行号（本轮要载哪一行）
    logic [9:0] load_row;
    logic [1:0] load_base;      // 0 = top 组，2 = bot 组

    always_ff @(posedge clk or negedge rstn) begin
        if (!rstn) begin
            st         <= S_IDLE;
            busy       <= 1'b0;
            done       <= 1'b0;
            ox         <= 9'd0;
            oy         <= 9'd0;
            plane      <= 2'd0;
            hold       <= 128'd0;
            hcnt       <= 5'd0;
            wr_px      <= 10'd0;
            pack_en    <= 1'b0;
            cached_lo  <= 10'h3FF;
            cached_hi  <= 10'h3FF;
            sel_flip   <= 1'b0;
            single_load<= 1'b0;
            load_phase <= 1'b0;
            rd_req     <= 1'b0;
            rd_addr    <= 32'd0;
            rd_beats   <= 10'd0;
            m_valid    <= 1'b0;
            m_data     <= 8'd0;
            m_last     <= 1'b0;
            byte_count <= 32'd0;
            load_row   <= 10'd0;
            load_base  <= 2'd0;
        end else begin
            // 只有在飞字节被下游取走时才清；否则保持（反压期间数据不得变）
            if (m_valid && m_ready) begin
                m_valid <= 1'b0;
                m_last  <= 1'b0;
            end

            // ---------------- 打包器（仅在加载态工作；弹像素与收 beat 同拍） ----------------
            if (pack_en) begin
                hold <= hold_n;
                hcnt <= hcnt_n;
                if (px_wr) begin
                    // bank 写口已拆到下方独立无复位进程（同一 clk 沿、同一使能）——
                    // Vivado 拒绝对异步复位敏感的写进程做 RAM 推断（8-4767）。
                    wr_px <= wr_px + 10'd1;
                end
            end

            // ---------------- 主状态机 ----------------
            case (st)
                S_IDLE: begin
                    busy <= 1'b0;
                    if (start) begin
                        busy     <= 1'b1;
                        ox       <= 9'd0;
                        oy       <= 9'd0;
                        plane    <= 2'd0;
                        byte_count <= 32'd0;
                        cached_lo <= 10'h3FF;
                        cached_hi <= 10'h3FF;
                        sel_flip  <= 1'b0;
                        st       <= S_ROW;
                    end
                end

                // 行几何：查表（无除法）
                S_ROW: begin
                    ox <= 9'd0;
                    load_phase <= 1'b0;
                    if (in_pad_row) begin
                        st <= S_XADDR;          // pad 行不需要缓存，直接吐常量
                    end else if ((sy_int == cached_lo) && (sy1_int == cached_hi)) begin
                        st <= S_XADDR;          // 缓存命中（同一对行连续复用）
                    end else if (sy_int == cached_hi) begin
                        // 增量复用：旧 bot 即新 top；把它原本所在组腾出来装新 bot
                        single_load <= 1'b1;
                        load_row    <= sy1_int;
                        load_base   <= sel_flip ? 2'd2 : 2'd0;
                        wr_px       <= 10'd0;
                        rd_addr     <= sy1_int * ROW_BYTES;
                        rd_beats    <= BEATS_PER_ROW;
                        rd_req      <= 1'b1;
                        st          <= S_LOAD_REQ;
                    end else begin
                        // 整对重载：强制 sel_flip=0，载 top 进 G0、bot 进 G1
                        single_load <= 1'b0;
                        sel_flip    <= 1'b0;
                        load_row    <= sy_int;
                        load_base   <= 2'd0;
                        wr_px       <= 10'd0;
                        rd_addr     <= sy_int * ROW_BYTES;
                        rd_beats    <= BEATS_PER_ROW;
                        rd_req      <= 1'b1;
                        st          <= S_LOAD_REQ;
                    end
                end

                // 发起一次突发
                S_LOAD_REQ: begin
                    if (rd_ack) begin
                        rd_req  <= 1'b0;
                        pack_en <= 1'b1;
                        hcnt    <= 5'd0;
                        hold    <= 128'd0;
                        st      <= S_LOAD_STREAM;
                    end
                end

                // 收 beat → 打包 → 写 bank，直到写满 640 像素
                S_LOAD_STREAM: begin
                    if (wr_px == PX_N) begin
                        pack_en <= 1'b0;
                        if (single_load) begin
                            // 增量复用：新 top = 旧 bot（已在另一组），新 bot = 刚载的行
                            cached_lo <= cached_hi;
                            cached_hi <= load_row;
                            sel_flip  <= ~sel_flip;
                            st        <= S_XADDR;
                        end else if (load_phase == 1'b0) begin
                            // 整对重载的第一行完成 → 载第二行
                            load_phase <= 1'b1;
                            cached_lo  <= load_row;
                            load_row   <= sy1_int;
                            load_base  <= 2'd2;
                            wr_px      <= 10'd0;
                            hcnt       <= 5'd0;
                            rd_addr    <= sy1_int * ROW_BYTES;
                            rd_beats   <= BEATS_PER_ROW;
                            rd_req     <= 1'b1;
                            st         <= S_LOAD_REQ;
                        end else begin
                            cached_hi <= load_row;
                            st        <= S_XADDR;
                        end
                    end
                end

                // 输出像素：pad 行直接吐常量；活跃行先发读地址（下一拍取数）
                S_XADDR: begin
                    if (in_pad_row) begin
                        // pad 行：1 拍 1 字节（can_put 为假时原地保持）
                        if (can_put) begin
                            m_valid    <= 1'b1;
                            m_data     <= PAD_Q;
                            m_last     <= (plane == 2'd2) && (oy == DST_H - 1) && (ox == DST_W - 1);
                            byte_count <= byte_count + 32'd1;
                            if (ox == DST_W - 1) begin
                                ox <= 9'd0;
                                st <= S_ROW_ADV;
                            end else begin
                                ox <= ox + 9'd1;
                            end
                        end
                    end else begin
                        st <= S_XMUL;
                    end
                end

                // 拍2：行插值（top_q24/bot_q24，2 DSP 并行 + 1 加）在本拍组合完成，沿寄存。
                // 无条件推进：不产输出、无状态分支；反压统一在拍4（S_XQ）处理。
                S_XMUL: begin
                    p_top24 <= top_q24;
                    p_bot24 <= bot_q24;
                    st      <= S_XCOL;
                end

                // 拍3：列插值 v_q48（2 DSP + 加）组合完成，沿寄存 v_q48[57:24]。
                S_XCOL: begin
                    p_vq24 <= v_q48[57:24];
                    st     <= S_XQ;
                end

                // 拍4：量化（原 S_XCALC 输出逻辑逐字搬入；can_put 为假原地保持，数据不丢）
                S_XQ: begin
                    if (can_put) begin
                        m_valid    <= 1'b1;
                        m_data     <= q_byte;
                        m_last     <= (plane == 2'd2) && (oy == DST_H - 1) && (ox == DST_W - 1);
                        byte_count <= byte_count + 32'd1;
                        if (ox == DST_W - 1) begin
                            ox <= 9'd0;
                            st <= S_ROW_ADV;
                        end else begin
                            ox <= ox + 9'd1;
                            st <= S_XADDR;
                        end
                    end
                end

                S_ROW_ADV: begin
                    ox <= 9'd0;
                    if (oy == DST_H - 1) begin
                        st <= S_FIN;
                    end else begin
                        oy <= oy + 9'd1;
                        st <= S_ROW;
                    end
                end

                S_FIN: begin
                    if (plane == 2'd2) begin
                        busy <= 1'b0;
                        done <= 1'b1;
                        st   <= S_IDLE;
                    end else begin
                        plane    <= plane + 2'd1;
                        oy       <= 9'd0;
                        ox       <= 9'd0;
                        cached_lo <= 10'h3FF;   // 换平面重扫，缓存作废
                        cached_hi <= 10'h3FF;
                        sel_flip  <= 1'b0;
                        st       <= S_ROW;
                    end
                end

                default: st <= S_IDLE;
            endcase
        end
    end

    // ---------------------------------------------------------------- 行缓存写口
    // 独立无复位时钟进程：Vivado 要求 RAM 写进程对异步复位不敏感
    //（实测 8-4767：RAM is sensitive to asynchronous reset signal → 退化为寄存器堆）。
    // bank 无需复位：rstn=0 期间 st=S_IDLE、pack_en=0 不会写；cached_lo/hi 复位为 0x3FF
    // 强制首次必整行载入后才读（读前必写，X 不可见）。使能/地址/数据与拆分前完全一致。
    always_ff @(posedge clk) begin
        if (pack_en && px_wr) begin
            // 组别取 load_base：0 = top(bank0/1)，2 = bot(bank2/3)
            case ({load_base[1], wr_px[0]})
                2'd0: bank0[wr_px[9:1]] <= px_out;
                2'd1: bank1[wr_px[9:1]] <= px_out;
                2'd2: bank2[wr_px[9:1]] <= px_out;
                2'd3: bank3[wr_px[9:1]] <= px_out;
            endcase
        end
    end

    // ---------------------------------------------------------------- 缓存读口
    // 方案 A：把 sel_flip 的选择从"读之前"挪到"读之后"——每个 bank 只保留一个
    // 读表达式（if/else 两支各读一次会让综合器视为 2 读口，LUTRAM 推断失败，
    // 退化成 31k FF 寄存器堆）。先各读一份到 r0..r3，再按 sel_flip 决定谁是 top/bot：
    // 同一地址读同一数据、选择次序不变 ⇒ 逐字节等价，cycles 不变。
    logic [23:0] g_top_e, g_top_o, g_bot_e, g_bot_o;
    logic [23:0] r0, r1, r2, r3;   // 每 bank 恰好 1 个读口
    always_comb begin
        r0 = bank0[a_even]; r1 = bank1[a_odd];
        r2 = bank2[a_even]; r3 = bank3[a_odd];
    end
    always_comb begin
        if (sel_flip) begin
            g_top_e = r2; g_top_o = r3;
            g_bot_e = r0; g_bot_o = r1;
        end else begin
            g_top_e = r0; g_top_o = r1;
            g_bot_e = r2; g_bot_o = r3;
        end
    end
    // LUTRAM 读法：地址 S_XADDR 期间稳定，LUTRAM 异步读 + 时钟沿把数据打入 d_*，S_XMUL 消费。
    // 拍1 流水寄存：d_* 与 p_swap/p_edge/p_dx_q/p_dy_q 同一沿、同一像素配对。
    always_ff @(posedge clk) begin
        if (st == S_XADDR && !in_pad_row) begin
            d_top_e <= g_top_e;
            d_top_o <= g_top_o;
            d_bot_e <= g_bot_e;
            d_bot_o <= g_bot_o;
            p_swap  <= sx_int[0];
            p_edge  <= (sx_int == sx1_int);
            p_dx_q  <= dx_q;
            p_dy_q  <= dy_q;
            p_dy_inv_q <= ONE24 - {1'b0, dy_q};
        end
    end

endmodule
