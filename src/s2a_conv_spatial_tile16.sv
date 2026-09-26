// layer36 单输出通道、连续16像素的空间 INT8 点积试验数据通路。
// 每个输入握手接收16个相邻 NCHW 像素和一份广播权重，K 顺序固定为0到255。
// 该模块只验证 MAC 数据通路，不包含片上缓冲、外存寻址、重定标或系统调度。
module s2a_conv_spatial_tile16 (
    input  logic                 clk,
    input  logic                 rst,
    input  logic                 abort,

    input  logic                 start_valid,
    output logic                 start_ready,
    input  logic        [12:0]   start_k,
    input  logic signed [31:0]   start_bias,

    input  logic                 input_valid,
    output logic                 input_ready,
    input  logic        [127:0]  feature_lanes,
    input  logic signed [7:0]   weight_data,

    output logic                 result_valid,
    input  logic                 result_ready,
    output logic        [511:0]  lane_accumulators,
    output logic        [2:0]   error_code,
    output logic                 busy
);
    localparam logic [2:0] ERROR_NONE = 3'd0;
    localparam logic [2:0] ERROR_BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] ERROR_ACCUMULATOR_OVERFLOW = 3'd7;

    localparam logic [1:0] ST_IDLE = 2'd0;
    localparam logic [1:0] ST_RUN = 2'd1;
    localparam logic [1:0] ST_RESPONSE = 2'd2;

    logic [1:0] state;
    logic [8:0] remaining_k;
    logic signed [31:0] accumulator_lane [0:15];
    logic signed [15:0] product_lane [0:15];
    logic signed [32:0] checked_sum_lane [0:15];
    logic invalid_operand;
    logic overflow_any;
    integer comb_lane;
    integer seq_lane;

    always_comb begin
        invalid_operand = (weight_data == -8'sd128);
        overflow_any = 1'b0;
        for (comb_lane = 0; comb_lane < 16; comb_lane = comb_lane + 1) begin
            product_lane[comb_lane] =
                $signed({{8{feature_lanes[comb_lane * 8 + 7]}},
                          feature_lanes[comb_lane * 8 +: 8]})
              * $signed({{8{weight_data[7]}}, weight_data});
            checked_sum_lane[comb_lane] =
                $signed({accumulator_lane[comb_lane][31], accumulator_lane[comb_lane]})
              + $signed({{17{product_lane[comb_lane][15]}}, product_lane[comb_lane]});
            if (feature_lanes[comb_lane * 8 +: 8] == 8'h80) begin
                invalid_operand = 1'b1;
            end
            if (checked_sum_lane[comb_lane][32] != checked_sum_lane[comb_lane][31]) begin
                overflow_any = 1'b1;
            end
        end
    end

    always_comb begin
        start_ready = (state == ST_IDLE) && !rst && !abort;
        input_ready = (state == ST_RUN) && !rst && !abort;
        result_valid = (state == ST_RESPONSE) && !rst && !abort;
        busy = (state != ST_IDLE);
    end

    always_ff @(posedge clk) begin
        if (rst) begin
            state <= ST_IDLE;
            remaining_k <= 9'd0;
            lane_accumulators <= 512'd0;
            error_code <= ERROR_NONE;
            for (seq_lane = 0; seq_lane < 16; seq_lane = seq_lane + 1) begin
                accumulator_lane[seq_lane] <= 32'sd0;
            end
        end else if (abort) begin
            state <= ST_IDLE;
            remaining_k <= 9'd0;
            lane_accumulators <= 512'd0;
            error_code <= ERROR_NONE;
            for (seq_lane = 0; seq_lane < 16; seq_lane = seq_lane + 1) begin
                accumulator_lane[seq_lane] <= 32'sd0;
            end
        end else begin
            case (state)
                ST_IDLE: begin
                    if (start_valid && start_ready) begin
                        lane_accumulators <= 512'd0;
                        error_code <= ERROR_NONE;
                        for (seq_lane = 0; seq_lane < 16; seq_lane = seq_lane + 1) begin
                            accumulator_lane[seq_lane] <= start_bias;
                        end
                        if (start_k != 13'd256) begin
                            remaining_k <= 9'd0;
                            error_code <= ERROR_BAD_ARGUMENT;
                            state <= ST_RESPONSE;
                        end else begin
                            remaining_k <= 9'd256;
                            state <= ST_RUN;
                        end
                    end
                end

                ST_RUN: begin
                    if (input_valid && input_ready) begin
                        if (invalid_operand) begin
                            lane_accumulators <= 512'd0;
                            error_code <= ERROR_BAD_ARGUMENT;
                            remaining_k <= 9'd0;
                            state <= ST_RESPONSE;
                        end else if (overflow_any) begin
                            lane_accumulators <= 512'd0;
                            error_code <= ERROR_ACCUMULATOR_OVERFLOW;
                            remaining_k <= 9'd0;
                            state <= ST_RESPONSE;
                        end else begin
                            for (seq_lane = 0; seq_lane < 16; seq_lane = seq_lane + 1) begin
                                accumulator_lane[seq_lane] <= checked_sum_lane[seq_lane][31:0];
                            end
                            if (remaining_k == 9'd1) begin
                                for (seq_lane = 0; seq_lane < 16; seq_lane = seq_lane + 1) begin
                                    lane_accumulators[seq_lane * 32 +: 32] <=
                                        checked_sum_lane[seq_lane][31:0];
                                end
                                error_code <= ERROR_NONE;
                                remaining_k <= 9'd0;
                                state <= ST_RESPONSE;
                            end else begin
                                remaining_k <= remaining_k - 9'd1;
                            end
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
                    remaining_k <= 9'd0;
                    lane_accumulators <= 512'd0;
                    error_code <= ERROR_BAD_ARGUMENT;
                    for (seq_lane = 0; seq_lane < 16; seq_lane = seq_lane + 1) begin
                        accumulator_lane[seq_lane] <= 32'sd0;
                    end
                end
            endcase
        end
    end
endmodule
