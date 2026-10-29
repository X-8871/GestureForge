// s4d_preproc_letterbox.sv —— 4-D PL 预处理：640x480 BGR888 → 416x416 INT8 CHW
//
// 口径（冻结，不得自定；逐字节复现 golden）：
//   · 几何：new_w=416, new_h=312, offset_x=0, offset_y=52（Darknet letterbox，端点对齐）
//   · 采样：src_x = x*639/415（等价 x*20/13 在 640→416 下的端点对齐式），src_y = y*479/311
//   · 插值：双线性，权重为 Q24（**由行为级分析得出：Q16 差 13 字节、Q20 差 2 字节、Q24 才 0 字节**）
//   · 量化：v∈[0,255] 的双线性值 v → q = round_away(v*127/255)，饱和 [0,127]
//           pad 归一化 0.5 → 量化后固定 64
//   · 布局：CHW，plane0=R、plane1=G、plane2=B；源为 BGR888 ⇒ src_ch = 2 - plane
//
// 结构：顺序引擎，一个输出字节若干拍；源像素经只读端口读出（1 拍延迟），
//       便于接行缓冲/VDMA/DDR 读通道；本模块自身不实现 DDR 突发。
//
// 时序接口（全部同步于 clk，rstn 低有效）：
//   start 上升沿启动一次转换（busy=0 时有效）；done 置高一拍表示完成。
//
// 诚实边界：本模块只做预处理数据通路；AXI-Lite CSR、BD 接线、时序收敛另见
//   s4d_preproc_csr.sv 与任务3 的 bd_merge_draft.tcl。综合/实现未做。

`timescale 1ns / 1ps

module s4d_preproc_letterbox #(
    parameter integer SRC_W = 640,
    parameter integer SRC_H = 480,
    parameter integer DST_W = 416,
    parameter integer DST_H = 416,
    parameter integer NEW_W = 416,
    parameter integer NEW_H = 312,
    parameter integer OFF_Y = 52
) (
    input  logic        clk,
    input  logic        rstn,

    input  logic        start,
    output logic        busy,
    output logic        done,

    // 源像素只读端口：rd_addr 为线性字节地址（含通道偏移），数据下一拍有效
    output logic        rd_en,
    output logic [23:0] rd_addr,
    input  logic [7:0]  rd_data,

    // 输出字节流（CHW 连续）：m_valid 时 m_data 有效，m_last 为最后一个字节
    output logic        m_valid,
    output logic [7:0]  m_data,
    output logic        m_last,

    // 统计
    output logic [31:0] byte_count
);

    localparam logic [24:0] ONE24 = 25'd16_777_216;   // 2^24
    localparam logic [7:0]  PAD_Q = 8'd64;            // quant(0.5 / (1/127)) = round(63.5) = 64
    localparam logic [63:0] DIV_D = 64'd4_278_190_080;  // 255 * 2^24

    typedef enum logic [3:0] {
        S_IDLE, S_ROW, S_PAD_EMIT, S_COL, S_RD_TL, S_RD_TR, S_RD_BL, S_RD_BR,
        S_CALC, S_EMIT, S_QUANT, S_ROW_ADV, S_FIN
    } state_e;

    state_e st;

    logic [1:0]  plane;       // 0=R,1=G,2=B
    logic [8:0]  oy;          // 0..415
    logic [8:0]  ox;          // 0..415
    logic [8:0]  y_valid;     // oy - OFF_Y（有效区行）
    logic [8:0]  src_ch;      // 2 - plane

    // 行几何（每行算一次）
    logic [17:0] sy_int;      // iy
    logic [23:0] dy_q;
    logic [17:0] sy1_int;

    // 列几何（每列算一次）
    logic [17:0] sx_int;
    logic [23:0] dx_q;
    logic [17:0] sx1_int;

    // 四个源像素与插值中间量
    logic [7:0]  p_tl, p_tr, p_bl, p_br;
    logic [33:0] top_q24, bot_q24;
    logic [63:0] v_q48;
    logic [33:0] v_q24;
    logic [39:0] num_q;
    logic [63:0] quot;
    logic [7:0]  q_byte;

    logic        in_pad_row;

    assign in_pad_row = (oy < OFF_Y) || (oy >= (OFF_Y + NEW_H));

    // ---- 行几何：sy_q = (y*479 << 24) / 311 -----------------------------------
    // 注意：必须由 oy 直接组合计算（若经寄存的 y_valid，会晚一行，导致整幅错位）
    logic [8:0]  y_eff;
    always_comb y_eff = (oy >= OFF_Y) ? (oy - OFF_Y) : 9'd0;
    logic [63:0] sy_num;
    always_comb sy_num = ({46'd0, y_eff} * 64'd479) << 24;
    logic [63:0] sy_q;
    assign sy_q = sy_num / 64'd311;

    // ---- 列几何：sx_q = (x*639 << 24) / 415 -----------------------------------
    logic [63:0] sx_num;
    always_comb sx_num = ({46'd0, ox} * 64'd639) << 24;
    logic [63:0] sx_q;
    assign sx_q = sx_num / 64'd415;

    // ---- 量化：q = round_away(v*127/255) = (2*N + D) / (2D)，N = v_q24*127 -----
    // v_q24 直接由 v_q48 组合截取：若用寄存版会晚一个像素（曾导致 3 字节整体位移）
    logic [33:0] v_q24_c;
    always_comb v_q24_c = v_q48[57:24];
    always_comb begin
        num_q = {6'd0, v_q24_c} * 40'd127;
        quot  = ({24'd0, num_q} * 64'd2 + DIV_D) / (DIV_D * 64'd2);
        q_byte = (quot > 64'd127) ? 8'd127 : quot[7:0];
    end

    // ---- 源地址 ---------------------------------------------------------------
    logic [23:0] addr_tl, addr_tr, addr_bl, addr_br;
    always_comb begin
        addr_tl = ({6'd0, sy_int} * SRC_W + {6'd0, sx_int}) * 3 + {22'd0, src_ch};
        addr_tr = ({6'd0, sy_int} * SRC_W + {6'd0, sx1_int}) * 3 + {22'd0, src_ch};
        addr_bl = ({6'd0, sy1_int} * SRC_W + {6'd0, sx_int}) * 3 + {22'd0, src_ch};
        addr_br = ({6'd0, sy1_int} * SRC_W + {6'd0, sx1_int}) * 3 + {22'd0, src_ch};
    end

    always_ff @(posedge clk or negedge rstn) begin
        if (!rstn) begin
            st         <= S_IDLE;
            busy       <= 1'b0;
            done       <= 1'b0;
            plane      <= 2'd0;
            oy         <= 9'd0;
            ox         <= 9'd0;
            y_valid    <= 9'd0;
            src_ch     <= 9'd2;
            sy_int     <= 18'd0;
            dy_q       <= 24'd0;
            sy1_int    <= 18'd0;
            sx_int     <= 18'd0;
            dx_q       <= 24'd0;
            sx1_int    <= 18'd0;
            rd_en      <= 1'b0;
            rd_addr    <= 24'd0;
            p_tl       <= 8'd0;
            p_tr       <= 8'd0;
            p_bl       <= 8'd0;
            p_br       <= 8'd0;
            top_q24    <= 34'd0;
            bot_q24    <= 34'd0;
            v_q48      <= 64'd0;
            v_q24      <= 34'd0;
            m_valid    <= 1'b0;
            m_data     <= 8'd0;
            m_last     <= 1'b0;
            byte_count <= 32'd0;
        end else begin
            rd_en   <= 1'b0;
            m_valid <= 1'b0;
            m_last  <= 1'b0;
            done    <= 1'b0;

            case (st)
                // ---- 启动 ----------------------------------------------------
                S_IDLE: begin
                    busy <= 1'b0;
                    if (start) begin
                        busy       <= 1'b1;
                        plane      <= 2'd0;
                        oy         <= 9'd0;
                        ox         <= 9'd0;
                        src_ch     <= 9'd2;          // plane0=R ← 源 ch2（BGR 输入）
                        byte_count <= 32'd0;
                        st         <= S_ROW;
                    end
                end

                // ---- 行几何（每行一次） --------------------------------------
                S_ROW: begin
                    sy_int  <= sy_q[41:24];
                    dy_q    <= sy_q[23:0];
                    sy1_int <= ((sy_q[41:24] + 18'd1) < SRC_H) ? (sy_q[41:24] + 18'd1) : SRC_H - 1;
                    ox      <= 9'd0;
                    st      <= in_pad_row ? S_PAD_EMIT : S_COL;
                end

                // ---- pad 行：只吐常量字节 ------------------------------------
                S_PAD_EMIT: begin
                    m_valid    <= 1'b1;
                    m_data     <= PAD_Q;
                    byte_count <= byte_count + 32'd1;
                    if (ox == DST_W - 1) begin
                        ox <= 9'd0;
                        st <= S_ROW_ADV;
                    end else begin
                        ox <= ox + 9'd1;
                        st <= S_PAD_EMIT;
                    end
                end

                // ---- 列几何 --------------------------------------------------
                S_COL: begin
                    sx_int  <= sx_q[41:24];
                    dx_q    <= sx_q[23:0];
                    sx1_int <= ((sx_q[41:24] + 18'd1) < SRC_W) ? (sx_q[41:24] + 18'd1) : SRC_W - 1;
                    st      <= S_RD_TL;
                end

                // ---- 四个源像素（地址本拍发，数据下拍取） --------------------
                S_RD_TL: begin rd_en <= 1'b1; rd_addr <= addr_tl; st <= S_RD_TR;  end
                S_RD_TR: begin p_tl  <= rd_data; rd_en <= 1'b1; rd_addr <= addr_tr; st <= S_RD_BL; end
                S_RD_BL: begin p_tr  <= rd_data; rd_en <= 1'b1; rd_addr <= addr_bl; st <= S_RD_BR; end
                S_RD_BR: begin p_bl  <= rd_data; rd_en <= 1'b1; rd_addr <= addr_br; st <= S_CALC;  end

                // ---- 水平插值（Q24） -----------------------------------------
                S_CALC: begin
                    // p_br 本拍才赋值（非阻塞），下式必须直接用当拍 rd_data，
                    // 否则 bot 行会用到上一个像素的 p_br（曾导致 y>=53 起 30% 字节差 1）
                    p_br    <= rd_data;
                    top_q24 <= ((ONE24 - {1'b0, dx_q}) * p_tl) + ({1'b0, dx_q} * p_tr);
                    bot_q24 <= ((ONE24 - {1'b0, dx_q}) * p_bl) + ({1'b0, dx_q} * rd_data);
                    st      <= S_EMIT;
                end

                // ---- 垂直插值 → Q48 -----------------------------------------
                S_EMIT: begin
                    v_q48 <= ((ONE24 - {1'b0, dy_q}) * top_q24) + ({1'b0, dy_q} * bot_q24);
                    st    <= S_QUANT;
                end

                // ---- 量化输出（v_q24 = v_q48 >> 24，q 由组合逻辑给出） --------
                S_QUANT: begin
                    m_valid    <= 1'b1;
                    m_data     <= q_byte;
                    byte_count <= byte_count + 32'd1;
                    if (ox == DST_W - 1) begin
                        ox <= 9'd0;
                        st <= S_ROW_ADV;
                    end else begin
                        ox <= ox + 9'd1;
                        st <= S_COL;
                    end
                end

                // ---- 行推进 --------------------------------------------------
                S_ROW_ADV: begin
                    ox <= 9'd0;
                    if (oy == DST_H - 1) begin
                        st <= S_FIN;
                    end else begin
                        oy <= oy + 9'd1;
                        st <= S_ROW;
                    end
                end

                // ---- 平面推进 / 结束 -----------------------------------------
                S_FIN: begin
                    if (plane == 2'd2) begin
                        // 仅最后一个平面完成才算整次转换结束
                        m_last <= 1'b1;
                        busy   <= 1'b0;
                        done   <= 1'b1;
                        st     <= S_IDLE;
                    end else begin
                        // 平面推进：不拉 done / m_last，避免调用方误判整次完成
                        plane  <= plane + 2'd1;
                        src_ch <= 9'd2 - (plane + 2'd1);
                        oy     <= 9'd0;
                        ox     <= 9'd0;
                        st     <= S_ROW;
                    end
                end

                default: st <= S_IDLE;
            endcase
        end
    end

endmodule
