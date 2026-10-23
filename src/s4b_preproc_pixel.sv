`timescale 1ns/1ps

module s4b_preproc_pixel (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        in_valid,
    output logic        in_ready,
    input  logic [7:0]  p00,
    input  logic [7:0]  p01,
    input  logic [7:0]  p10,
    input  logic [7:0]  p11,
    input  logic [63:0] wx0,
    input  logic [63:0] wx1,
    input  logic [63:0] wy0,
    input  logic [63:0] wy1,
    output logic        busy,
    output logic        out_valid,
    input  logic        out_ready,
    output logic [7:0]  out_q,
    output logic        error_valid,
    input  logic        error_ready,
    output logic [2:0]  error_code
);
    localparam logic [63:0] FP64_ONE = 64'h3ff0000000000000;
    localparam logic [63:0] FP64_MIN_GEOMETRY_WEIGHT = 64'h3ca0000000000000;
    localparam logic [63:0] FP64_255 = 64'h406fe00000000000;

    localparam logic [2:0] ERR_NONE = 3'd0;
    localparam logic [2:0] ERR_COEFFICIENT_DOMAIN = 3'd1;
    localparam logic [2:0] ERR_FP64_DOMAIN = 3'd2;

    typedef enum logic [3:0] {
        ST_IDLE,
        ST_ISSUE,
        ST_WAIT_FP64,
        ST_QUANTIZE,
        ST_OUTPUT,
        ST_ERROR
    } state_t;

    state_t state_q;
    logic [7:0] p00_q;
    logic [7:0] p01_q;
    logic [7:0] p10_q;
    logic [7:0] p11_q;
    logic [63:0] wx0_q;
    logic [63:0] wx1_q;
    logic [63:0] wy0_q;
    logic [63:0] wy1_q;
    logic [3:0] operation_q;
    logic [63:0] product00_q;
    logic [63:0] product01_q;
    logic [63:0] row0_q;
    logic [63:0] product10_q;
    logic [63:0] product11_q;
    logic [63:0] row1_q;
    logic [63:0] weighted_row0_q;
    logic [63:0] weighted_row1_q;
    logic [63:0] interpolation_q;
    logic [7:0] search_low_q;
    logic [7:0] search_high_q;
    logic [7:0] search_middle;
    logic [63:0] threshold_value;
    logic [63:0] alu_operand_a;
    logic [63:0] alu_operand_b;
    logic alu_start;
    logic alu_add_op;
    logic alu_busy;
    logic alu_done;
    logic alu_error;
    logic [1:0] alu_error_code;
    logic [63:0] alu_result;

    function automatic logic coefficient_supported(input logic [63:0] value);
        logic [62:0] magnitude;
        logic [10:0] exponent;
        begin
            magnitude = value[62:0];
            exponent = value[62:52];
            if (magnitude == 63'd0) begin
                coefficient_supported = 1'b1;
            end else if (value[63] || (exponent == 11'd0) ||
                         (exponent == 11'h7ff) || (magnitude > FP64_ONE[62:0]) ||
                         (magnitude < FP64_MIN_GEOMETRY_WEIGHT[62:0])) begin
                coefficient_supported = 1'b0;
            end else begin
                coefficient_supported = 1'b1;
            end
        end
    endfunction

    function automatic logic [63:0] canonical_zero(input logic [63:0] value);
        begin
            canonical_zero = (value[62:0] == 63'd0) ? 64'd0 : value;
        end
    endfunction

    function automatic logic [63:0] byte_to_fp64(input logic [7:0] value);
        logic [52:0] significand;
        logic [10:0] exponent;
        integer top_bit;
        integer bit_index;
        logic found;
        begin
            significand = 53'd0;
            top_bit = 0;
            found = 1'b0;
            if (value == 8'd0) begin
                byte_to_fp64 = 64'd0;
            end else begin
                for (bit_index = 7; bit_index >= 0; bit_index = bit_index - 1) begin
                    if (!found && value[bit_index]) begin
                        top_bit = bit_index;
                        found = 1'b1;
                    end
                end
                significand = {45'd0, value};
                significand = significand << (52 - top_bit);
                exponent = 11'd1023 + top_bit;
                byte_to_fp64 = {1'b0, exponent, significand[51:0]};
            end
        end
    endfunction

    function automatic logic [63:0] threshold_at(input logic [6:0] index);
        begin
            case (index)
                7'd0: threshold_at = 64'h3ff0102040810204;
                7'd1: threshold_at = 64'h4008183060c18306;
                7'd2: threshold_at = 64'h4014142850a14285;
                7'd3: threshold_at = 64'h401c1c3870e1c387;
                7'd4: threshold_at = 64'h4022122448912244;
                7'd5: threshold_at = 64'h4026162c58b162c5;
                7'd6: threshold_at = 64'h402a1a3468d1a346;
                7'd7: threshold_at = 64'h402e1e3c78f1e3c7;
                7'd8: threshold_at = 64'h4031112244891224;
                7'd9: threshold_at = 64'h403313264c993264;
                7'd10: threshold_at = 64'h4035152a54a952a5;
                7'd11: threshold_at = 64'h4037172e5cb972e5;
                7'd12: threshold_at = 64'h4039193264c99326;
                7'd13: threshold_at = 64'h403b1b366cd9b366;
                7'd14: threshold_at = 64'h403d1d3a74e9d3a7;
                7'd15: threshold_at = 64'h403f1f3e7cf9f3e7;
                7'd16: threshold_at = 64'h404090a142850a14;
                7'd17: threshold_at = 64'h404191a3468d1a35;
                7'd18: threshold_at = 64'h404292a54a952a54;
                7'd19: threshold_at = 64'h404393a74e9d3a75;
                7'd20: threshold_at = 64'h404494a952a54a95;
                7'd21: threshold_at = 64'h404595ab56ad5ab6;
                7'd22: threshold_at = 64'h404696ad5ab56ad5;
                7'd23: threshold_at = 64'h404797af5ebd7af6;
                7'd24: threshold_at = 64'h404898b162c58b16;
                7'd25: threshold_at = 64'h404999b366cd9b37;
                7'd26: threshold_at = 64'h404a9ab56ad5ab56;
                7'd27: threshold_at = 64'h404b9bb76eddbb77;
                7'd28: threshold_at = 64'h404c9cb972e5cb97;
                7'd29: threshold_at = 64'h404d9dbb76eddbb8;
                7'd30: threshold_at = 64'h404e9ebd7af5ebd7;
                7'd31: threshold_at = 64'h404f9fbf7efdfbf8;
                7'd32: threshold_at = 64'h40505060c183060c;
                7'd33: threshold_at = 64'h4050d0e1c3870e1c;
                7'd34: threshold_at = 64'h40515162c58b162d;
                7'd35: threshold_at = 64'h4051d1e3c78f1e3d;
                7'd36: threshold_at = 64'h40525264c993264c;
                7'd37: threshold_at = 64'h4052d2e5cb972e5c;
                7'd38: threshold_at = 64'h40535366cd9b366d;
                7'd39: threshold_at = 64'h4053d3e7cf9f3e7d;
                7'd40: threshold_at = 64'h40545468d1a3468d;
                7'd41: threshold_at = 64'h4054d4e9d3a74e9d;
                7'd42: threshold_at = 64'h4055556ad5ab56ae;
                7'd43: threshold_at = 64'h4055d5ebd7af5ebe;
                7'd44: threshold_at = 64'h4056566cd9b366cd;
                7'd45: threshold_at = 64'h4056d6eddbb76edd;
                7'd46: threshold_at = 64'h4057576eddbb76ee;
                7'd47: threshold_at = 64'h4057d7efdfbf7efe;
                7'd48: threshold_at = 64'h40585870e1c3870e;
                7'd49: threshold_at = 64'h4058d8f1e3c78f1e;
                7'd50: threshold_at = 64'h40595972e5cb972f;
                7'd51: threshold_at = 64'h4059d9f3e7cf9f3f;
                7'd52: threshold_at = 64'h405a5a74e9d3a74e;
                7'd53: threshold_at = 64'h405adaf5ebd7af5e;
                7'd54: threshold_at = 64'h405b5b76eddbb76f;
                7'd55: threshold_at = 64'h405bdbf7efdfbf7f;
                7'd56: threshold_at = 64'h405c5c78f1e3c78f;
                7'd57: threshold_at = 64'h405cdcf9f3e7cf9f;
                7'd58: threshold_at = 64'h405d5d7af5ebd7b0;
                7'd59: threshold_at = 64'h405dddfbf7efdfc0;
                7'd60: threshold_at = 64'h405e5e7cf9f3e7cf;
                7'd61: threshold_at = 64'h405edefdfbf7efdf;
                7'd62: threshold_at = 64'h405f5f7efdfbf7f0;
                7'd63: threshold_at = 64'h405fe00000000000;
                7'd64: threshold_at = 64'h4060304081020408;
                7'd65: threshold_at = 64'h4060708102040810;
                7'd66: threshold_at = 64'h4060b0c183060c18;
                7'd67: threshold_at = 64'h4060f10204081020;
                7'd68: threshold_at = 64'h40613142850a1429;
                7'd69: threshold_at = 64'h40617183060c1831;
                7'd70: threshold_at = 64'h4061b1c3870e1c39;
                7'd71: threshold_at = 64'h4061f20408102040;
                7'd72: threshold_at = 64'h4062324489122448;
                7'd73: threshold_at = 64'h406272850a142850;
                7'd74: threshold_at = 64'h4062b2c58b162c58;
                7'd75: threshold_at = 64'h4062f3060c183060;
                7'd76: threshold_at = 64'h406333468d1a3469;
                7'd77: threshold_at = 64'h406373870e1c3871;
                7'd78: threshold_at = 64'h4063b3c78f1e3c79;
                7'd79: threshold_at = 64'h4063f40810204081;
                7'd80: threshold_at = 64'h4064344891224489;
                7'd81: threshold_at = 64'h4064748912244891;
                7'd82: threshold_at = 64'h4064b4c993264c99;
                7'd83: threshold_at = 64'h4064f50a142850a1;
                7'd84: threshold_at = 64'h4065354a952a54aa;
                7'd85: threshold_at = 64'h4065758b162c58b2;
                7'd86: threshold_at = 64'h4065b5cb972e5cba;
                7'd87: threshold_at = 64'h4065f60c183060c1;
                7'd88: threshold_at = 64'h4066364c993264c9;
                7'd89: threshold_at = 64'h4066768d1a3468d1;
                7'd90: threshold_at = 64'h4066b6cd9b366cd9;
                7'd91: threshold_at = 64'h4066f70e1c3870e1;
                7'd92: threshold_at = 64'h4067374e9d3a74ea;
                7'd93: threshold_at = 64'h4067778f1e3c78f2;
                7'd94: threshold_at = 64'h4067b7cf9f3e7cfa;
                7'd95: threshold_at = 64'h4067f81020408102;
                7'd96: threshold_at = 64'h40683850a142850a;
                7'd97: threshold_at = 64'h4068789122448912;
                7'd98: threshold_at = 64'h4068b8d1a3468d1a;
                7'd99: threshold_at = 64'h4068f91224489122;
                7'd100: threshold_at = 64'h40693952a54a952b;
                7'd101: threshold_at = 64'h40697993264c9933;
                7'd102: threshold_at = 64'h4069b9d3a74e9d3b;
                7'd103: threshold_at = 64'h4069fa142850a142;
                7'd104: threshold_at = 64'h406a3a54a952a54a;
                7'd105: threshold_at = 64'h406a7a952a54a952;
                7'd106: threshold_at = 64'h406abad5ab56ad5a;
                7'd107: threshold_at = 64'h406afb162c58b162;
                7'd108: threshold_at = 64'h406b3b56ad5ab56b;
                7'd109: threshold_at = 64'h406b7b972e5cb973;
                7'd110: threshold_at = 64'h406bbbd7af5ebd7b;
                7'd111: threshold_at = 64'h406bfc183060c183;
                7'd112: threshold_at = 64'h406c3c58b162c58b;
                7'd113: threshold_at = 64'h406c7c993264c993;
                7'd114: threshold_at = 64'h406cbcd9b366cd9b;
                7'd115: threshold_at = 64'h406cfd1a3468d1a3;
                7'd116: threshold_at = 64'h406d3d5ab56ad5ac;
                7'd117: threshold_at = 64'h406d7d9b366cd9b4;
                7'd118: threshold_at = 64'h406dbddbb76eddbc;
                7'd119: threshold_at = 64'h406dfe1c3870e1c3;
                7'd120: threshold_at = 64'h406e3e5cb972e5cb;
                7'd121: threshold_at = 64'h406e7e9d3a74e9d3;
                7'd122: threshold_at = 64'h406ebeddbb76eddb;
                7'd123: threshold_at = 64'h406eff1e3c78f1e3;
                7'd124: threshold_at = 64'h406f3f5ebd7af5ec;
                7'd125: threshold_at = 64'h406f7f9f3e7cf9f4;
                7'd126: threshold_at = 64'h406fbfdfbf7efdfc;
                default: threshold_at = 64'h7ff0000000000000;
            endcase
        end
    endfunction

    always_comb begin
        in_ready = (state_q == ST_IDLE);
        busy = (state_q != ST_IDLE);
        alu_start = (state_q == ST_ISSUE);
        alu_add_op = (operation_q == 4'd2) ||
                     (operation_q == 4'd5) ||
                     (operation_q == 4'd8);
        alu_operand_a = 64'd0;
        alu_operand_b = 64'd0;
        case (operation_q)
            4'd0: begin alu_operand_a = wx0_q; alu_operand_b = byte_to_fp64(p00_q); end
            4'd1: begin alu_operand_a = wx1_q; alu_operand_b = byte_to_fp64(p01_q); end
            4'd2: begin alu_operand_a = product00_q; alu_operand_b = product01_q; end
            4'd3: begin alu_operand_a = wx0_q; alu_operand_b = byte_to_fp64(p10_q); end
            4'd4: begin alu_operand_a = wx1_q; alu_operand_b = byte_to_fp64(p11_q); end
            4'd5: begin alu_operand_a = product10_q; alu_operand_b = product11_q; end
            4'd6: begin alu_operand_a = wy0_q; alu_operand_b = row0_q; end
            4'd7: begin alu_operand_a = wy1_q; alu_operand_b = row1_q; end
            4'd8: begin alu_operand_a = weighted_row0_q; alu_operand_b = weighted_row1_q; end
            default: begin alu_operand_a = 64'd0; alu_operand_b = 64'd0; end
        endcase
        search_middle = (search_low_q + search_high_q) >> 1;
        threshold_value = threshold_at(search_middle[6:0]);
    end

    s4b_preproc_fp64 fp64_unit (
        .clk(clk),
        .rst_n(rst_n),
        .start(alu_start),
        .add_op(alu_add_op),
        .operand_a(alu_operand_a),
        .operand_b(alu_operand_b),
        .busy(alu_busy),
        .done(alu_done),
        .error(alu_error),
        .error_code(alu_error_code),
        .result(alu_result)
    );

    always_ff @(posedge clk or negedge rst_n) begin : pixel_state_machine
        if (!rst_n) begin
            state_q <= ST_IDLE;
            p00_q <= 8'd0;
            p01_q <= 8'd0;
            p10_q <= 8'd0;
            p11_q <= 8'd0;
            wx0_q <= 64'd0;
            wx1_q <= 64'd0;
            wy0_q <= 64'd0;
            wy1_q <= 64'd0;
            operation_q <= 4'd0;
            product00_q <= 64'd0;
            product01_q <= 64'd0;
            row0_q <= 64'd0;
            product10_q <= 64'd0;
            product11_q <= 64'd0;
            row1_q <= 64'd0;
            weighted_row0_q <= 64'd0;
            weighted_row1_q <= 64'd0;
            interpolation_q <= 64'd0;
            search_low_q <= 8'd0;
            search_high_q <= 8'd127;
            out_valid <= 1'b0;
            out_q <= 8'd0;
            error_valid <= 1'b0;
            error_code <= ERR_NONE;
        end else begin
            case (state_q)
                ST_IDLE: begin
                    if (in_valid && in_ready) begin
                        if (!coefficient_supported(wx0) || !coefficient_supported(wx1) ||
                            !coefficient_supported(wy0) || !coefficient_supported(wy1)) begin
                            error_valid <= 1'b1;
                            error_code <= ERR_COEFFICIENT_DOMAIN;
                            state_q <= ST_ERROR;
                        end else begin
                            p00_q <= p00;
                            p01_q <= p01;
                            p10_q <= p10;
                            p11_q <= p11;
                            wx0_q <= canonical_zero(wx0);
                            wx1_q <= canonical_zero(wx1);
                            wy0_q <= canonical_zero(wy0);
                            wy1_q <= canonical_zero(wy1);
                            operation_q <= 4'd0;
                            out_valid <= 1'b0;
                            error_valid <= 1'b0;
                            error_code <= ERR_NONE;
                            state_q <= ST_ISSUE;
                        end
                    end
                end

                ST_ISSUE: begin
                    state_q <= ST_WAIT_FP64;
                end

                ST_WAIT_FP64: begin
                    if (alu_done) begin
                        if (alu_error) begin
                            error_valid <= 1'b1;
                            error_code <= ERR_FP64_DOMAIN;
                            state_q <= ST_ERROR;
                        end else begin
                            case (operation_q)
                                4'd0: product00_q <= alu_result;
                                4'd1: product01_q <= alu_result;
                                4'd2: row0_q <= alu_result;
                                4'd3: product10_q <= alu_result;
                                4'd4: product11_q <= alu_result;
                                4'd5: row1_q <= alu_result;
                                4'd6: weighted_row0_q <= alu_result;
                                4'd7: weighted_row1_q <= alu_result;
                                4'd8: interpolation_q <= alu_result;
                                default: begin
                                    error_valid <= 1'b1;
                                    error_code <= ERR_FP64_DOMAIN;
                                    state_q <= ST_ERROR;
                                end
                            endcase
                            if (operation_q == 4'd8) begin
                                search_low_q <= 8'd0;
                                search_high_q <= 8'd127;
                                if ((alu_result[62:0] == 63'd0)) begin
                                    out_q <= 8'd0;
                                    out_valid <= 1'b1;
                                    state_q <= ST_OUTPUT;
                                end else if (alu_result[63] || alu_result[62:52] == 11'h7ff) begin
                                    error_valid <= 1'b1;
                                    error_code <= ERR_FP64_DOMAIN;
                                    state_q <= ST_ERROR;
                                end else if (alu_result[62:0] >= FP64_255[62:0]) begin
                                    out_q <= 8'd127;
                                    out_valid <= 1'b1;
                                    state_q <= ST_OUTPUT;
                                end else begin
                                    state_q <= ST_QUANTIZE;
                                end
                            end else if (operation_q < 4'd8) begin
                                operation_q <= operation_q + 1'b1;
                                state_q <= ST_ISSUE;
                            end
                        end
                    end
                end

                ST_QUANTIZE: begin
                    if (search_low_q < search_high_q) begin
                        if (interpolation_q >= threshold_value)
                            search_low_q <= search_middle + 1'b1;
                        else
                            search_high_q <= search_middle;
                    end else begin
                        out_q <= search_low_q;
                        out_valid <= 1'b1;
                        state_q <= ST_OUTPUT;
                    end
                end

                ST_OUTPUT: begin
                    if (out_valid && out_ready) begin
                        out_valid <= 1'b0;
                        state_q <= ST_IDLE;
                    end
                end

                ST_ERROR: begin
                    if (error_valid && error_ready) begin
                        error_valid <= 1'b0;
                        error_code <= ERR_NONE;
                        state_q <= ST_IDLE;
                    end
                end

                default: begin
                    error_valid <= 1'b1;
                    error_code <= ERR_FP64_DOMAIN;
                    state_q <= ST_ERROR;
                end
            endcase
        end
    end
endmodule
