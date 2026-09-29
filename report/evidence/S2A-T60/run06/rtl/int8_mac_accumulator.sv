// 共享对称 INT8 点积累加器，供卷积等算子复用。
// start_valid/start_ready 接受 K 与有符号 INT32 bias；随后每次
// operand_valid/operand_ready 传输一对 activation/weight，严格按序累加 K 项。
// K=0 或任一操作数为 -128 返回 BAD_ARGUMENT(1)；逐项有符号 INT32 越界返回
// ACCUMULATOR_OVERFLOW(7)，不回绕、不饱和。成功返回精确 INT32 累加值。
// result_valid/result_ready 握手前结果和错误码保持稳定；busy 覆盖计算与待取结果。
// abort 与同步高有效 rst 均取消事务且不留下响应；取消后可立即接受新事务。
module int8_mac_accumulator (
    input  logic                    clk,
    input  logic                    rst,
    input  logic                    abort,

    input  logic                    start_valid,
    output logic                    start_ready,
    input  logic        [12:0]      start_k,
    input  logic signed [31:0]      start_bias,

    input  logic                    operand_valid,
    output logic                    operand_ready,
    input  logic signed [7:0]       activation_data,
    input  logic signed [7:0]       weight_data,

    output logic                    result_valid,
    input  logic                    result_ready,
    output logic signed [31:0]      result_data,
    output logic        [2:0]       error_code,
    output logic                    busy
);
    localparam logic [2:0] ERROR_NONE = 3'd0;
    localparam logic [2:0] ERROR_BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] ERROR_ACCUMULATOR_OVERFLOW = 3'd7;

    localparam logic [1:0] ST_IDLE = 2'd0;
    localparam logic [1:0] ST_RUN = 2'd1;
    localparam logic [1:0] ST_RESPONSE = 2'd2;

    logic [1:0] state;
    logic [12:0] remaining_k;
    logic signed [31:0] accumulator;
    logic signed [15:0] product_value;
    logic signed [32:0] checked_sum;

    always_comb begin
        product_value = $signed({{8{activation_data[7]}}, activation_data})
                      * $signed({{8{weight_data[7]}}, weight_data});
        checked_sum = $signed({accumulator[31], accumulator})
                    + $signed({{17{product_value[15]}}, product_value});
    end

    always_comb begin
        start_ready = (state == ST_IDLE) && !rst && !abort;
        operand_ready = (state == ST_RUN) && !rst && !abort;
        result_valid = (state == ST_RESPONSE);
        busy = (state != ST_IDLE);
    end

    always_ff @(posedge clk) begin
        if (rst) begin
            state <= ST_IDLE;
            remaining_k <= 13'd0;
            accumulator <= 32'sd0;
            result_data <= 32'sd0;
            error_code <= ERROR_NONE;
        end else if (abort) begin
            state <= ST_IDLE;
            remaining_k <= 13'd0;
            accumulator <= 32'sd0;
            result_data <= 32'sd0;
            error_code <= ERROR_NONE;
        end else begin
            case (state)
                ST_IDLE: begin
                    if (start_valid && start_ready) begin
                        result_data <= 32'sd0;
                        error_code <= ERROR_NONE;
                        accumulator <= start_bias;
                        if (start_k == 13'd0) begin
                            remaining_k <= 13'd0;
                            error_code <= ERROR_BAD_ARGUMENT;
                            state <= ST_RESPONSE;
                        end else begin
                            remaining_k <= start_k;
                            state <= ST_RUN;
                        end
                    end
                end

                ST_RUN: begin
                    if (operand_valid && operand_ready) begin
                        if ((activation_data == -8'sd128) ||
                            (weight_data == -8'sd128)) begin
                            result_data <= 32'sd0;
                            error_code <= ERROR_BAD_ARGUMENT;
                            remaining_k <= 13'd0;
                            state <= ST_RESPONSE;
                        end else if (checked_sum[32] != checked_sum[31]) begin
                            result_data <= 32'sd0;
                            error_code <= ERROR_ACCUMULATOR_OVERFLOW;
                            remaining_k <= 13'd0;
                            state <= ST_RESPONSE;
                        end else if (remaining_k == 13'd1) begin
                            result_data <= checked_sum[31:0];
                            error_code <= ERROR_NONE;
                            remaining_k <= 13'd0;
                            state <= ST_RESPONSE;
                        end else begin
                            accumulator <= checked_sum[31:0];
                            remaining_k <= remaining_k - 13'd1;
                        end
                    end
                end

                ST_RESPONSE: begin
                    if (result_valid && result_ready) begin
                        state <= ST_IDLE;
                    end
                end

                default: begin
                    state <= ST_IDLE;
                    remaining_k <= 13'd0;
                    accumulator <= 32'sd0;
                    result_data <= 32'sd0;
                    error_code <= ERROR_BAD_ARGUMENT;
                end
            endcase
        end
    end
endmodule
