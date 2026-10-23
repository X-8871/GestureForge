`timescale 1ns/1ps

module s4b_preproc_fp64 (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        start,
    input  logic        add_op,
    input  logic [63:0] operand_a,
    input  logic [63:0] operand_b,
    output logic        busy,
    output logic        done,
    output logic        error,
    output logic [1:0]  error_code,
    output logic [63:0] result
);
    localparam logic [1:0] ERR_NONE = 2'd0;
    localparam logic [1:0] ERR_INPUT_DOMAIN = 2'd1;
    localparam logic [1:0] ERR_RESULT_DOMAIN = 2'd2;

    typedef enum logic [2:0] {
        ST_IDLE,
        ST_MUL_ITER,
        ST_MUL_ROUND,
        ST_ADD_ALIGN,
        ST_ADD_SUM,
        ST_ADD_ROUND
    } state_t;

    state_t state_q;
    logic [63:0] a_q;
    logic [63:0] b_q;
    logic [10:0] mul_exp_a_q;
    logic [10:0] mul_exp_b_q;
    logic [52:0] mul_multiplier_q;
    logic [105:0] mul_multiplicand_q;
    logic [105:0] mul_accumulator_q;
    logic [105:0] mul_product_q;
    logic [5:0] mul_iteration_q;

    logic [55:0] add_large_q;
    logic [55:0] add_small_q;
    logic [10:0] add_exponent_q;
    logic [56:0] add_sum_q;

    logic [105:0] mul_next_product;

    function automatic logic operand_supported(input logic [63:0] value);
        logic [10:0] exponent;
        logic [51:0] fraction;
        begin
            exponent = value[62:52];
            fraction = value[51:0];
            operand_supported = (value[63] == 1'b0)
                && (exponent != 11'h7ff)
                && ((exponent != 11'd0) || (fraction == 52'd0));
        end
    endfunction

    function automatic logic is_zero(input logic [63:0] value);
        begin
            is_zero = (value[62:0] == 63'd0);
        end
    endfunction

    function automatic logic [55:0] shift_right_jam56(
        input logic [55:0] value,
        input logic [11:0] amount
    );
        logic [55:0] shifted;
        logic sticky;
        integer bit_index;
        begin
            shifted = 56'd0;
            sticky = 1'b0;
            if (amount == 12'd0) begin
                shifted = value;
            end else if (amount >= 12'd56) begin
                shifted[0] = |value;
            end else begin
                shifted = value >> amount;
                for (bit_index = 0; bit_index < 56; bit_index = bit_index + 1) begin
                    if (bit_index < amount)
                        sticky = sticky | value[bit_index];
                end
                shifted[0] = shifted[0] | sticky;
            end
            shift_right_jam56 = shifted;
        end
    endfunction

    function automatic [64:0] pack_product(
        input logic [105:0] product,
        input logic [10:0] exponent_a,
        input logic [10:0] exponent_b
    );
        logic [52:0] significand;
        logic guard_bit;
        logic sticky_bit;
        logic round_up;
        logic [53:0] rounded_significand;
        integer signed exponent_result;
        logic [63:0] packed_value;
        logic invalid_result;
        begin
            if (product[105]) begin
                significand = product[105:53];
                guard_bit = product[52];
                sticky_bit = |product[51:0];
                exponent_result = exponent_a + exponent_b - 1023 + 1;
            end else begin
                significand = product[104:52];
                guard_bit = product[51];
                sticky_bit = |product[50:0];
                exponent_result = exponent_a + exponent_b - 1023;
            end

            round_up = guard_bit & (sticky_bit | significand[0]);
            rounded_significand = {1'b0, significand} + {{53{1'b0}}, round_up};
            if (rounded_significand[53]) begin
                significand = 53'h10000000000000;
                exponent_result = exponent_result + 1;
            end else begin
                significand = rounded_significand[52:0];
            end

            invalid_result = (exponent_result <= 0) || (exponent_result >= 2047);
            packed_value = 64'd0;
            if (!invalid_result)
                packed_value = {1'b0, exponent_result[10:0], significand[51:0]};
            pack_product = {invalid_result, packed_value};
        end
    endfunction

    function automatic [64:0] pack_sum(
        input logic [56:0] unnormalized_sum,
        input logic [10:0] base_exponent
    );
        logic [55:0] normalized;
        logic [52:0] significand;
        logic [53:0] rounded_significand;
        logic guard_bit;
        logic round_bit;
        logic sticky_bit;
        logic round_up;
        integer signed exponent_result;
        logic invalid_result;
        logic [63:0] packed_value;
        begin
            if (unnormalized_sum[56]) begin
                normalized = {unnormalized_sum[56:2],
                              (unnormalized_sum[1] | unnormalized_sum[0])};
                exponent_result = base_exponent + 1;
            end else begin
                normalized = unnormalized_sum[55:0];
                exponent_result = base_exponent;
            end

            significand = normalized[55:3];
            guard_bit = normalized[2];
            round_bit = normalized[1];
            sticky_bit = normalized[0];
            round_up = guard_bit & (round_bit | sticky_bit | significand[0]);
            rounded_significand = {1'b0, significand} + {{53{1'b0}}, round_up};
            if (rounded_significand[53]) begin
                significand = 53'h10000000000000;
                exponent_result = exponent_result + 1;
            end else begin
                significand = rounded_significand[52:0];
            end

            invalid_result = (exponent_result <= 0) || (exponent_result >= 2047);
            packed_value = 64'd0;
            if (!invalid_result)
                packed_value = {1'b0, exponent_result[10:0], significand[51:0]};
            pack_sum = {invalid_result, packed_value};
        end
    endfunction

    always_comb begin
        mul_next_product = mul_accumulator_q;
        if (mul_multiplier_q[0])
            mul_next_product = mul_accumulator_q + mul_multiplicand_q;
    end

    assign busy = (state_q != ST_IDLE);

    always_ff @(posedge clk or negedge rst_n) begin : fp64_state_machine
        logic [10:0] exponent_a;
        logic [10:0] exponent_b;
        logic [52:0] significand_a;
        logic [52:0] significand_b;
        logic [11:0] exponent_difference;
        logic [64:0] packed_result;
        begin
            if (!rst_n) begin
                state_q <= ST_IDLE;
                a_q <= 64'd0;
                b_q <= 64'd0;
                mul_exp_a_q <= 11'd0;
                mul_exp_b_q <= 11'd0;
                mul_multiplier_q <= 53'd0;
                mul_multiplicand_q <= 106'd0;
                mul_accumulator_q <= 106'd0;
                mul_product_q <= 106'd0;
                mul_iteration_q <= 6'd0;
                add_large_q <= 56'd0;
                add_small_q <= 56'd0;
                add_exponent_q <= 11'd0;
                add_sum_q <= 57'd0;
                done <= 1'b0;
                error <= 1'b0;
                error_code <= ERR_NONE;
                result <= 64'd0;
            end else begin
                done <= 1'b0;
                error <= 1'b0;
                error_code <= ERR_NONE;

                case (state_q)
                    ST_IDLE: begin
                        if (start) begin
                            a_q <= operand_a;
                            b_q <= operand_b;
                            if (!operand_supported(operand_a) || !operand_supported(operand_b)) begin
                                done <= 1'b1;
                                error <= 1'b1;
                                error_code <= ERR_INPUT_DOMAIN;
                                state_q <= ST_IDLE;
                            end else if (add_op && is_zero(operand_a)) begin
                                result <= operand_b[62:0] == 63'd0 ? 64'd0 : operand_b;
                                done <= 1'b1;
                                state_q <= ST_IDLE;
                            end else if (add_op && is_zero(operand_b)) begin
                                result <= operand_a[62:0] == 63'd0 ? 64'd0 : operand_a;
                                done <= 1'b1;
                                state_q <= ST_IDLE;
                            end else if (!add_op &&
                                         (is_zero(operand_a) || is_zero(operand_b))) begin
                                result <= 64'd0;
                                done <= 1'b1;
                                state_q <= ST_IDLE;
                            end else if (add_op) begin
                                state_q <= ST_ADD_ALIGN;
                            end else begin
                                exponent_a = operand_a[62:52];
                                exponent_b = operand_b[62:52];
                                significand_a = {1'b1, operand_a[51:0]};
                                significand_b = {1'b1, operand_b[51:0]};
                                mul_exp_a_q <= exponent_a;
                                mul_exp_b_q <= exponent_b;
                                mul_multiplier_q <= significand_b;
                                mul_multiplicand_q <= {53'd0, significand_a};
                                mul_accumulator_q <= 106'd0;
                                mul_iteration_q <= 6'd0;
                                state_q <= ST_MUL_ITER;
                            end
                        end
                    end

                    ST_MUL_ITER: begin
                        mul_accumulator_q <= mul_next_product;
                        mul_multiplicand_q <= mul_multiplicand_q << 1;
                        mul_multiplier_q <= mul_multiplier_q >> 1;
                        if (mul_iteration_q == 6'd52) begin
                            mul_product_q <= mul_next_product;
                            state_q <= ST_MUL_ROUND;
                        end else begin
                            mul_iteration_q <= mul_iteration_q + 1'b1;
                        end
                    end

                    ST_MUL_ROUND: begin
                        packed_result = pack_product(mul_product_q, mul_exp_a_q, mul_exp_b_q);
                        if (packed_result[64]) begin
                            done <= 1'b1;
                            error <= 1'b1;
                            error_code <= ERR_RESULT_DOMAIN;
                        end else begin
                            result <= packed_result[63:0];
                            done <= 1'b1;
                        end
                        state_q <= ST_IDLE;
                    end

                    ST_ADD_ALIGN: begin
                        exponent_a = a_q[62:52];
                        exponent_b = b_q[62:52];
                        significand_a = {1'b1, a_q[51:0]};
                        significand_b = {1'b1, b_q[51:0]};
                        if (exponent_a >= exponent_b) begin
                            exponent_difference = exponent_a - exponent_b;
                            add_large_q <= {significand_a, 3'b000};
                            add_small_q <= shift_right_jam56({significand_b, 3'b000},
                                                             exponent_difference);
                            add_exponent_q <= exponent_a;
                        end else begin
                            exponent_difference = exponent_b - exponent_a;
                            add_large_q <= {significand_b, 3'b000};
                            add_small_q <= shift_right_jam56({significand_a, 3'b000},
                                                             exponent_difference);
                            add_exponent_q <= exponent_b;
                        end
                        state_q <= ST_ADD_SUM;
                    end

                    ST_ADD_SUM: begin
                        add_sum_q <= {1'b0, add_large_q} + {1'b0, add_small_q};
                        state_q <= ST_ADD_ROUND;
                    end

                    ST_ADD_ROUND: begin
                        packed_result = pack_sum(add_sum_q, add_exponent_q);
                        if (packed_result[64]) begin
                            done <= 1'b1;
                            error <= 1'b1;
                            error_code <= ERR_RESULT_DOMAIN;
                        end else begin
                            result <= packed_result[63:0];
                            done <= 1'b1;
                        end
                        state_q <= ST_IDLE;
                    end

                    default: begin
                        state_q <= ST_IDLE;
                        done <= 1'b1;
                        error <= 1'b1;
                        error_code <= ERR_RESULT_DOMAIN;
                    end
                endcase
            end
        end
    end
endmodule
