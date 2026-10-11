// 完整原模块及完整合并候选的白盒二态组合核验；不是公开FSM输入可达性测试。
module tb_s12_requant;
    logic signed [31:0] accumulator;
    logic [79:0] parameter_word;
    logic signed [7:0] expected_file, expected_oracle;
    wire signed [7:0] mutant_value [0:6];
    integer mutant_hits [0:6];
    integer fd, fields, case_id, vectors, mismatch_count;
    rq_original_engine original_engine (
        .clk('0),
        .hard_reset('0),
        .abort('0),
        .buffer_owner_pl('0),
        .start_valid('0),
        .start_ready(),
        .layer_index('0),
        .weight_layer_index('0),
        .input_base_address('0),
        .input_length_bytes('0),
        .input_batch_count('0),
        .input_channels('0),
        .input_height('0),
        .input_width('0),
        .output_base_address('0),
        .output_length_bytes('0),
        .output_batch_count('0),
        .output_channels('0),
        .output_height('0),
        .output_width('0),
        .kernel_height('0),
        .kernel_width('0),
        .stride_y('0),
        .stride_x('0),
        .pad_left('0),
        .pad_right('0),
        .pad_top('0),
        .pad_bottom('0),
        .groups('0),
        .padding_value_int8('0),
        .weight_package_base_address('0),
        .weight_package_length_bytes('0),
        .quantized_weight_offset('0),
        .quantized_weight_bytes('0),
        .output_batch('0),
        .activation_mode('0),
        .backend_cancel(),
        .backend_req_valid(),
        .backend_req_ready('0),
        .backend_req_write(),
        .backend_req_addr(),
        .backend_req_wdata(),
        .backend_req_rstrb(),
        .backend_req_wstrb(),
        .backend_rsp_valid('0),
        .backend_rsp_rdata('0),
        .backend_rsp_error('0),
        .busy(),
        .result_valid(),
        .result_ready('0),
        .result_error_code()
    );
    rq_candidate_engine #(.FROZEN_CONV_DESCRIPTOR(1'b0)) candidate_engine (
        .clk('0),
        .hard_reset('0),
        .abort('0),
        .buffer_owner_pl('0),
        .start_valid('0),
        .start_ready(),
        .layer_index('0),
        .weight_layer_index('0),
        .input_base_address('0),
        .input_length_bytes('0),
        .input_batch_count('0),
        .input_channels('0),
        .input_height('0),
        .input_width('0),
        .output_base_address('0),
        .output_length_bytes('0),
        .output_batch_count('0),
        .output_channels('0),
        .output_height('0),
        .output_width('0),
        .kernel_height('0),
        .kernel_width('0),
        .stride_y('0),
        .stride_x('0),
        .pad_left('0),
        .pad_right('0),
        .pad_top('0),
        .pad_bottom('0),
        .groups('0),
        .padding_value_int8('0),
        .weight_package_base_address('0),
        .weight_package_length_bytes('0),
        .quantized_weight_offset('0),
        .quantized_weight_bytes('0),
        .output_batch('0),
        .activation_mode('0),
        .backend_cancel(),
        .backend_req_valid(),
        .backend_req_ready('0),
        .backend_req_write(),
        .backend_req_addr(),
        .backend_req_wdata(),
        .backend_req_rstrb(),
        .backend_req_wstrb(),
        .backend_rsp_valid('0),
        .backend_rsp_rdata('0),
        .backend_rsp_error('0),
        .busy(),
        .result_valid(),
        .result_ready('0),
        .result_error_code()
    );
    rq_mutant_noround mutant_0 (.accumulator(accumulator), .parameter_word(parameter_word), .requantized_value(mutant_value[0]));
    rq_mutant_minus128sat mutant_1 (.accumulator(accumulator), .parameter_word(parameter_word), .requantized_value(mutant_value[1]));
    rq_mutant_ignorebit7 mutant_2 (.accumulator(accumulator), .parameter_word(parameter_word), .requantized_value(mutant_value[2]));
    rq_mutant_product32 mutant_3 (.accumulator(accumulator), .parameter_word(parameter_word), .requantized_value(mutant_value[3]));
    rq_mutant_signwrong mutant_4 (.accumulator(accumulator), .parameter_word(parameter_word), .requantized_value(mutant_value[4]));
    rq_mutant_shiftwrap6 mutant_5 (.accumulator(accumulator), .parameter_word(parameter_word), .requantized_value(mutant_value[5]));
    rq_mutant_negativeusespositive mutant_6 (.accumulator(accumulator), .parameter_word(parameter_word), .requantized_value(mutant_value[6]));
    function automatic logic signed [7:0] division_oracle(
        input logic signed [31:0] value,
        input logic [79:0] mq
    );
        logic [31:0] multiplier;
        logic [7:0] shift;
        logic [63:0] magnitude;
        logic [255:0] numerator, denominator, quotient, remainder;
        begin
            multiplier = value[31] ? mq[39:8] : mq[79:48];
            shift = value[31] ? mq[7:0] : mq[47:40];
            magnitude = value[31] ? -$signed({{32{value[31]}}, value}) : {32'd0, value};
            numerator = magnitude * {32'd0, multiplier};
            denominator = 256'd1 << shift;
            quotient = numerator / denominator;
            remainder = numerator % denominator;
            if ((remainder << 1) >= denominator) quotient = quotient + 256'd1;
            if (quotient > 256'd127) division_oracle = value[31] ? -8'sd127 : 8'sd127;
            else division_oracle = value[31] ? -$signed(quotient[7:0]) : $signed(quotient[7:0]);
        end
    endfunction

    initial begin
        vectors = 0;
        mismatch_count = 0;
        for (integer index = 0; index < 7; index = index + 1) mutant_hits[index] = 0;
        // clk固定为0；直接装载内部寄存器，不通过公开接口绕过或更改参数校验。
        original_engine.requant_lane_index = 0;
        candidate_engine.requant_lane_index = 0;
        original_engine.group_lane_count = 1;
        candidate_engine.group_lane_count = 1;
        fd = $fopen("vectors.txt", "r");
        if (!fd) $fatal(1, "VECTORS_OPEN_FAILED");
        while (!$feof(fd)) begin
            fields = $fscanf(fd, "%h %h %h %d\n", accumulator, parameter_word, expected_file, case_id);
            if (fields == 4) begin
                original_engine.lane_accumulator[0] = accumulator;
                candidate_engine.lane_accumulator[0] = accumulator;
                original_engine.lane_mq_parameter[0] = parameter_word;
                candidate_engine.lane_mq_parameter[0] = parameter_word;
                #1;
                expected_oracle = division_oracle(accumulator, parameter_word);
                if ((expected_oracle !== expected_file) ||
                    (original_engine.requantized_value !== expected_oracle) ||
                    (candidate_engine.requantized_value !== expected_oracle)) begin
                    mismatch_count = mismatch_count + 1;
                    if (mismatch_count <= 12)
                        $display("REQUANT_MISMATCH case=%0d acc=%h mq=%h old=%h new=%h oracle=%h file=%h", case_id,
                                 accumulator, parameter_word, original_engine.requantized_value,
                                 candidate_engine.requantized_value, expected_oracle, expected_file);
                end
                for (integer index = 0; index < 7; index = index + 1) begin
                    if (mutant_value[index] !== expected_oracle) begin
                        mutant_hits[index] = mutant_hits[index] + 1;
                        if (mutant_hits[index] == 1)
                            $display("MUTANT_SEMANTIC_WITNESS id=%0d case=%0d acc=%h mq=%h actual=%h oracle=%h", index,
                                     case_id, accumulator, parameter_word, mutant_value[index], expected_oracle);
                    end
                end
                vectors = vectors + 1;
            end else if (fields != -1) $fatal(1, "MALFORMED_VECTOR fields=%0d", fields);
        end
        $fclose(fd);
        if (mismatch_count != 0) $fatal(1, "FULL_RTL_ORACLE_MISMATCH count=%0d", mismatch_count);
        for (integer index = 0; index < 7; index = index + 1) begin
            if (mutant_hits[index] == 0) $fatal(1, "MUTANT_SURVIVED id=%0d", index);
            $display("MUTANT_SEMANTIC_KILLED id=%0d count=%0d", index, mutant_hits[index]);
        end
        $display("S12_REQUANT_FULL_RTL_PASS vectors=%0d mutants=7 mismatches=0", vectors);
        $finish;
    end
endmodule
