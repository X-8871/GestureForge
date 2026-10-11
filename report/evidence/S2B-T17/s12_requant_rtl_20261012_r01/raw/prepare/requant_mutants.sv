// 仅提取requant组合块的语义变异；不是全核心变异。
module rq_mutant_noround (
    input logic signed [31:0] accumulator,
    input logic [79:0] parameter_word,
    output logic signed [7:0] requantized_value
);
    localparam integer LANE_COUNT = 8;
    logic [31:0] requant_lane_index, group_lane_count;
    logic [79:0] lane_mq_parameter [0:7];
    logic signed [31:0] lane_accumulator [0:7];
    logic [79:0] requant_parameter;
    logic signed [31:0] requant_accumulator;
    logic [31:0] requant_multiplier, requant_q_shift, requant_magnitude;
    logic [63:0] requant_product, requant_rounding_add, requant_rounded_magnitude;
    always_comb begin
        requant_lane_index = 0;
        group_lane_count = 1;
        for (integer lane = 0; lane < 8; lane = lane + 1) begin
            lane_mq_parameter[lane] = 0;
            lane_accumulator[lane] = 0;
        end
        lane_mq_parameter[0] = parameter_word;
        lane_accumulator[0] = accumulator;
        requant_parameter = 80'd0;
        requant_accumulator = 32'sd0;
        requant_multiplier = 32'd0;
        requant_q_shift = 32'd0;
        requant_magnitude = 32'd0;
        requant_product = 64'd0;
        requant_rounding_add = 64'd0;
        requant_rounded_magnitude = 64'd0;
        requantized_value = 8'sd0;
        if ((requant_lane_index < LANE_COUNT) &&
            (requant_lane_index < group_lane_count)) begin
            requant_parameter = lane_mq_parameter[requant_lane_index];
            requant_accumulator = lane_accumulator[requant_lane_index];
            if (requant_accumulator[31]) begin
                requant_multiplier = requant_parameter[39:8];
                requant_q_shift = {24'd0, requant_parameter[7:0]};
                requant_magnitude = ~$unsigned(requant_accumulator) + 32'd1;
            end else begin
                requant_multiplier = requant_parameter[79:48];
                requant_q_shift = {24'd0, requant_parameter[47:40]};
                requant_magnitude = $unsigned(requant_accumulator);
            end
            requant_product = {32'd0, requant_magnitude} *
                              {32'd0, requant_multiplier};
            if (requant_q_shift != 32'd0) begin
                requant_rounding_add = 64'd0;
            end
            requant_rounded_magnitude =
                (requant_product + requant_rounding_add) >> requant_q_shift;
            if (|requant_rounded_magnitude[63:7]) begin
                requantized_value = requant_accumulator[31] ? -8'sd127 : 8'sd127;
            end else if (requant_accumulator[31]) begin
                requantized_value = -$signed(requant_rounded_magnitude[7:0]);
            end else begin
                requantized_value = $signed(requant_rounded_magnitude[7:0]);
            end
        end

    end
endmodule

// 仅提取requant组合块的语义变异；不是全核心变异。
module rq_mutant_minus128sat (
    input logic signed [31:0] accumulator,
    input logic [79:0] parameter_word,
    output logic signed [7:0] requantized_value
);
    localparam integer LANE_COUNT = 8;
    logic [31:0] requant_lane_index, group_lane_count;
    logic [79:0] lane_mq_parameter [0:7];
    logic signed [31:0] lane_accumulator [0:7];
    logic [79:0] requant_parameter;
    logic signed [31:0] requant_accumulator;
    logic [31:0] requant_multiplier, requant_q_shift, requant_magnitude;
    logic [63:0] requant_product, requant_rounding_add, requant_rounded_magnitude;
    always_comb begin
        requant_lane_index = 0;
        group_lane_count = 1;
        for (integer lane = 0; lane < 8; lane = lane + 1) begin
            lane_mq_parameter[lane] = 0;
            lane_accumulator[lane] = 0;
        end
        lane_mq_parameter[0] = parameter_word;
        lane_accumulator[0] = accumulator;
        requant_parameter = 80'd0;
        requant_accumulator = 32'sd0;
        requant_multiplier = 32'd0;
        requant_q_shift = 32'd0;
        requant_magnitude = 32'd0;
        requant_product = 64'd0;
        requant_rounding_add = 64'd0;
        requant_rounded_magnitude = 64'd0;
        requantized_value = 8'sd0;
        if ((requant_lane_index < LANE_COUNT) &&
            (requant_lane_index < group_lane_count)) begin
            requant_parameter = lane_mq_parameter[requant_lane_index];
            requant_accumulator = lane_accumulator[requant_lane_index];
            if (requant_accumulator[31]) begin
                requant_multiplier = requant_parameter[39:8];
                requant_q_shift = {24'd0, requant_parameter[7:0]};
                requant_magnitude = ~$unsigned(requant_accumulator) + 32'd1;
            end else begin
                requant_multiplier = requant_parameter[79:48];
                requant_q_shift = {24'd0, requant_parameter[47:40]};
                requant_magnitude = $unsigned(requant_accumulator);
            end
            requant_product = {32'd0, requant_magnitude} *
                              {32'd0, requant_multiplier};
            if (requant_q_shift != 32'd0) begin
                requant_rounding_add = 64'd1 << (requant_q_shift - 32'd1);
            end
            requant_rounded_magnitude =
                (requant_product + requant_rounding_add) >> requant_q_shift;
            if (|requant_rounded_magnitude[63:7]) begin
                requantized_value = requant_accumulator[31] ? -8'sd128 : 8'sd127;
            end else if (requant_accumulator[31]) begin
                requantized_value = -$signed(requant_rounded_magnitude[7:0]);
            end else begin
                requantized_value = $signed(requant_rounded_magnitude[7:0]);
            end
        end

    end
endmodule

// 仅提取requant组合块的语义变异；不是全核心变异。
module rq_mutant_ignorebit7 (
    input logic signed [31:0] accumulator,
    input logic [79:0] parameter_word,
    output logic signed [7:0] requantized_value
);
    localparam integer LANE_COUNT = 8;
    logic [31:0] requant_lane_index, group_lane_count;
    logic [79:0] lane_mq_parameter [0:7];
    logic signed [31:0] lane_accumulator [0:7];
    logic [79:0] requant_parameter;
    logic signed [31:0] requant_accumulator;
    logic [31:0] requant_multiplier, requant_q_shift, requant_magnitude;
    logic [63:0] requant_product, requant_rounding_add, requant_rounded_magnitude;
    always_comb begin
        requant_lane_index = 0;
        group_lane_count = 1;
        for (integer lane = 0; lane < 8; lane = lane + 1) begin
            lane_mq_parameter[lane] = 0;
            lane_accumulator[lane] = 0;
        end
        lane_mq_parameter[0] = parameter_word;
        lane_accumulator[0] = accumulator;
        requant_parameter = 80'd0;
        requant_accumulator = 32'sd0;
        requant_multiplier = 32'd0;
        requant_q_shift = 32'd0;
        requant_magnitude = 32'd0;
        requant_product = 64'd0;
        requant_rounding_add = 64'd0;
        requant_rounded_magnitude = 64'd0;
        requantized_value = 8'sd0;
        if ((requant_lane_index < LANE_COUNT) &&
            (requant_lane_index < group_lane_count)) begin
            requant_parameter = lane_mq_parameter[requant_lane_index];
            requant_accumulator = lane_accumulator[requant_lane_index];
            if (requant_accumulator[31]) begin
                requant_multiplier = requant_parameter[39:8];
                requant_q_shift = {24'd0, requant_parameter[7:0]};
                requant_magnitude = ~$unsigned(requant_accumulator) + 32'd1;
            end else begin
                requant_multiplier = requant_parameter[79:48];
                requant_q_shift = {24'd0, requant_parameter[47:40]};
                requant_magnitude = $unsigned(requant_accumulator);
            end
            requant_product = {32'd0, requant_magnitude} *
                              {32'd0, requant_multiplier};
            if (requant_q_shift != 32'd0) begin
                requant_rounding_add = 64'd1 << (requant_q_shift - 32'd1);
            end
            requant_rounded_magnitude =
                (requant_product + requant_rounding_add) >> requant_q_shift;
            if (|requant_rounded_magnitude[63:8]) begin
                requantized_value = requant_accumulator[31] ? -8'sd127 : 8'sd127;
            end else if (requant_accumulator[31]) begin
                requantized_value = -$signed(requant_rounded_magnitude[7:0]);
            end else begin
                requantized_value = $signed(requant_rounded_magnitude[7:0]);
            end
        end

    end
endmodule

// 仅提取requant组合块的语义变异；不是全核心变异。
module rq_mutant_product32 (
    input logic signed [31:0] accumulator,
    input logic [79:0] parameter_word,
    output logic signed [7:0] requantized_value
);
    localparam integer LANE_COUNT = 8;
    logic [31:0] requant_lane_index, group_lane_count;
    logic [79:0] lane_mq_parameter [0:7];
    logic signed [31:0] lane_accumulator [0:7];
    logic [79:0] requant_parameter;
    logic signed [31:0] requant_accumulator;
    logic [31:0] requant_multiplier, requant_q_shift, requant_magnitude;
    logic [63:0] requant_product, requant_rounding_add, requant_rounded_magnitude;
    always_comb begin
        requant_lane_index = 0;
        group_lane_count = 1;
        for (integer lane = 0; lane < 8; lane = lane + 1) begin
            lane_mq_parameter[lane] = 0;
            lane_accumulator[lane] = 0;
        end
        lane_mq_parameter[0] = parameter_word;
        lane_accumulator[0] = accumulator;
        requant_parameter = 80'd0;
        requant_accumulator = 32'sd0;
        requant_multiplier = 32'd0;
        requant_q_shift = 32'd0;
        requant_magnitude = 32'd0;
        requant_product = 64'd0;
        requant_rounding_add = 64'd0;
        requant_rounded_magnitude = 64'd0;
        requantized_value = 8'sd0;
        if ((requant_lane_index < LANE_COUNT) &&
            (requant_lane_index < group_lane_count)) begin
            requant_parameter = lane_mq_parameter[requant_lane_index];
            requant_accumulator = lane_accumulator[requant_lane_index];
            if (requant_accumulator[31]) begin
                requant_multiplier = requant_parameter[39:8];
                requant_q_shift = {24'd0, requant_parameter[7:0]};
                requant_magnitude = ~$unsigned(requant_accumulator) + 32'd1;
            end else begin
                requant_multiplier = requant_parameter[79:48];
                requant_q_shift = {24'd0, requant_parameter[47:40]};
                requant_magnitude = $unsigned(requant_accumulator);
            end
            requant_product = {32'd0, requant_magnitude} *
                              {32'd0, requant_multiplier};
            requant_product = {32'd0, requant_product[31:0]};
            if (requant_q_shift != 32'd0) begin
                requant_rounding_add = 64'd1 << (requant_q_shift - 32'd1);
            end
            requant_rounded_magnitude =
                (requant_product + requant_rounding_add) >> requant_q_shift;
            if (|requant_rounded_magnitude[63:7]) begin
                requantized_value = requant_accumulator[31] ? -8'sd127 : 8'sd127;
            end else if (requant_accumulator[31]) begin
                requantized_value = -$signed(requant_rounded_magnitude[7:0]);
            end else begin
                requantized_value = $signed(requant_rounded_magnitude[7:0]);
            end
        end

    end
endmodule

// 仅提取requant组合块的语义变异；不是全核心变异。
module rq_mutant_signwrong (
    input logic signed [31:0] accumulator,
    input logic [79:0] parameter_word,
    output logic signed [7:0] requantized_value
);
    localparam integer LANE_COUNT = 8;
    logic [31:0] requant_lane_index, group_lane_count;
    logic [79:0] lane_mq_parameter [0:7];
    logic signed [31:0] lane_accumulator [0:7];
    logic [79:0] requant_parameter;
    logic signed [31:0] requant_accumulator;
    logic [31:0] requant_multiplier, requant_q_shift, requant_magnitude;
    logic [63:0] requant_product, requant_rounding_add, requant_rounded_magnitude;
    always_comb begin
        requant_lane_index = 0;
        group_lane_count = 1;
        for (integer lane = 0; lane < 8; lane = lane + 1) begin
            lane_mq_parameter[lane] = 0;
            lane_accumulator[lane] = 0;
        end
        lane_mq_parameter[0] = parameter_word;
        lane_accumulator[0] = accumulator;
        requant_parameter = 80'd0;
        requant_accumulator = 32'sd0;
        requant_multiplier = 32'd0;
        requant_q_shift = 32'd0;
        requant_magnitude = 32'd0;
        requant_product = 64'd0;
        requant_rounding_add = 64'd0;
        requant_rounded_magnitude = 64'd0;
        requantized_value = 8'sd0;
        if ((requant_lane_index < LANE_COUNT) &&
            (requant_lane_index < group_lane_count)) begin
            requant_parameter = lane_mq_parameter[requant_lane_index];
            requant_accumulator = lane_accumulator[requant_lane_index];
            if (requant_accumulator[31]) begin
                requant_multiplier = requant_parameter[39:8];
                requant_q_shift = {24'd0, requant_parameter[7:0]};
                requant_magnitude = ~$unsigned(requant_accumulator) + 32'd1;
            end else begin
                requant_multiplier = requant_parameter[79:48];
                requant_q_shift = {24'd0, requant_parameter[47:40]};
                requant_magnitude = $unsigned(requant_accumulator);
            end
            requant_product = {32'd0, requant_magnitude} *
                              {32'd0, requant_multiplier};
            if (requant_q_shift != 32'd0) begin
                requant_rounding_add = 64'd1 << (requant_q_shift - 32'd1);
            end
            requant_rounded_magnitude =
                (requant_product + requant_rounding_add) >> requant_q_shift;
            if (|requant_rounded_magnitude[63:7]) begin
                requantized_value = 1'b0 ? -8'sd127 : 8'sd127;
            end else if (1'b0) begin
                requantized_value = -$signed(requant_rounded_magnitude[7:0]);
            end else begin
                requantized_value = $signed(requant_rounded_magnitude[7:0]);
            end
        end

    end
endmodule

// 仅提取requant组合块的语义变异；不是全核心变异。
module rq_mutant_shiftwrap6 (
    input logic signed [31:0] accumulator,
    input logic [79:0] parameter_word,
    output logic signed [7:0] requantized_value
);
    localparam integer LANE_COUNT = 8;
    logic [31:0] requant_lane_index, group_lane_count;
    logic [79:0] lane_mq_parameter [0:7];
    logic signed [31:0] lane_accumulator [0:7];
    logic [79:0] requant_parameter;
    logic signed [31:0] requant_accumulator;
    logic [31:0] requant_multiplier, requant_q_shift, requant_magnitude;
    logic [63:0] requant_product, requant_rounding_add, requant_rounded_magnitude;
    always_comb begin
        requant_lane_index = 0;
        group_lane_count = 1;
        for (integer lane = 0; lane < 8; lane = lane + 1) begin
            lane_mq_parameter[lane] = 0;
            lane_accumulator[lane] = 0;
        end
        lane_mq_parameter[0] = parameter_word;
        lane_accumulator[0] = accumulator;
        requant_parameter = 80'd0;
        requant_accumulator = 32'sd0;
        requant_multiplier = 32'd0;
        requant_q_shift = 32'd0;
        requant_magnitude = 32'd0;
        requant_product = 64'd0;
        requant_rounding_add = 64'd0;
        requant_rounded_magnitude = 64'd0;
        requantized_value = 8'sd0;
        if ((requant_lane_index < LANE_COUNT) &&
            (requant_lane_index < group_lane_count)) begin
            requant_parameter = lane_mq_parameter[requant_lane_index];
            requant_accumulator = lane_accumulator[requant_lane_index];
            if (requant_accumulator[31]) begin
                requant_multiplier = requant_parameter[39:8];
                requant_q_shift = {26'd0, requant_parameter[5:0]};
                requant_magnitude = ~$unsigned(requant_accumulator) + 32'd1;
            end else begin
                requant_multiplier = requant_parameter[79:48];
                requant_q_shift = {26'd0, requant_parameter[45:40]};
                requant_magnitude = $unsigned(requant_accumulator);
            end
            requant_product = {32'd0, requant_magnitude} *
                              {32'd0, requant_multiplier};
            if (requant_q_shift != 32'd0) begin
                requant_rounding_add = 64'd1 << (requant_q_shift - 32'd1);
            end
            requant_rounded_magnitude =
                (requant_product + requant_rounding_add) >> requant_q_shift;
            if (|requant_rounded_magnitude[63:7]) begin
                requantized_value = requant_accumulator[31] ? -8'sd127 : 8'sd127;
            end else if (requant_accumulator[31]) begin
                requantized_value = -$signed(requant_rounded_magnitude[7:0]);
            end else begin
                requantized_value = $signed(requant_rounded_magnitude[7:0]);
            end
        end

    end
endmodule

// 仅提取requant组合块的语义变异；不是全核心变异。
module rq_mutant_negativeusespositive (
    input logic signed [31:0] accumulator,
    input logic [79:0] parameter_word,
    output logic signed [7:0] requantized_value
);
    localparam integer LANE_COUNT = 8;
    logic [31:0] requant_lane_index, group_lane_count;
    logic [79:0] lane_mq_parameter [0:7];
    logic signed [31:0] lane_accumulator [0:7];
    logic [79:0] requant_parameter;
    logic signed [31:0] requant_accumulator;
    logic [31:0] requant_multiplier, requant_q_shift, requant_magnitude;
    logic [63:0] requant_product, requant_rounding_add, requant_rounded_magnitude;
    always_comb begin
        requant_lane_index = 0;
        group_lane_count = 1;
        for (integer lane = 0; lane < 8; lane = lane + 1) begin
            lane_mq_parameter[lane] = 0;
            lane_accumulator[lane] = 0;
        end
        lane_mq_parameter[0] = parameter_word;
        lane_accumulator[0] = accumulator;
        requant_parameter = 80'd0;
        requant_accumulator = 32'sd0;
        requant_multiplier = 32'd0;
        requant_q_shift = 32'd0;
        requant_magnitude = 32'd0;
        requant_product = 64'd0;
        requant_rounding_add = 64'd0;
        requant_rounded_magnitude = 64'd0;
        requantized_value = 8'sd0;
        if ((requant_lane_index < LANE_COUNT) &&
            (requant_lane_index < group_lane_count)) begin
            requant_parameter = lane_mq_parameter[requant_lane_index];
            requant_accumulator = lane_accumulator[requant_lane_index];
            if (requant_accumulator[31]) begin
                requant_multiplier = requant_parameter[79:48];
                requant_q_shift = {24'd0, requant_parameter[47:40]};
                requant_magnitude = ~$unsigned(requant_accumulator) + 32'd1;
            end else begin
                requant_multiplier = requant_parameter[79:48];
                requant_q_shift = {24'd0, requant_parameter[47:40]};
                requant_magnitude = $unsigned(requant_accumulator);
            end
            requant_product = {32'd0, requant_magnitude} *
                              {32'd0, requant_multiplier};
            if (requant_q_shift != 32'd0) begin
                requant_rounding_add = 64'd1 << (requant_q_shift - 32'd1);
            end
            requant_rounded_magnitude =
                (requant_product + requant_rounding_add) >> requant_q_shift;
            if (|requant_rounded_magnitude[63:7]) begin
                requantized_value = requant_accumulator[31] ? -8'sd127 : 8'sd127;
            end else if (requant_accumulator[31]) begin
                requantized_value = -$signed(requant_rounded_magnitude[7:0]);
            end else begin
                requantized_value = $signed(requant_rounded_magnitude[7:0]);
            end
        end

    end
endmodule
