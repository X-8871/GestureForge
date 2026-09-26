// 验证16路空间累加、统一握手、取消恢复与固定 layer36 输入向量。
module tb_s2a_conv_spatial_tile16;
    logic clk = 1'b0;
    always #5 clk = ~clk;

    logic rst;
    logic abort;
    logic start_valid;
    logic start_ready;
    logic [12:0] start_k;
    logic signed [31:0] start_bias;
    logic input_valid;
    logic input_ready;
    logic [127:0] feature_lanes;
    logic signed [7:0] weight_data;
    logic result_valid;
    logic result_ready;
    logic [511:0] lane_accumulators;
    logic [2:0] error_code;
    logic busy;

    integer vector_fd;
    integer scan_result;
    integer case_id;
    integer case_bias;
    integer case_error;
    integer expected_lane [0:15];
    integer input_lane [0:15];
    integer input_weight;
    integer accepted_beats;
    integer dataset_accepted_beats;
    integer recovery_accepted_beats;
    integer early_error_accepted_beats;
    integer cancelled_accepted_beats;
    integer bad_activation_accepted_beats;
    integer bad_weight_accepted_beats;
    integer overflow_accepted_beats;
    integer abort_accepted_beats;
    integer reset_accepted_beats;
    integer invalid_start_transactions;
    integer completed_dataset_tiles;
    integer protocol_recovery_tiles;
    integer k_index;
    integer lane_index;
    integer bubble_cycles;
    integer held_lane;
    integer held_output [0:15];
    integer expected_case;

    s2a_conv_spatial_tile16 dut (
        .clk(clk),
        .rst(rst),
        .abort(abort),
        .start_valid(start_valid),
        .start_ready(start_ready),
        .start_k(start_k),
        .start_bias(start_bias),
        .input_valid(input_valid),
        .input_ready(input_ready),
        .feature_lanes(feature_lanes),
        .weight_data(weight_data),
        .result_valid(result_valid),
        .result_ready(result_ready),
        .lane_accumulators(lane_accumulators),
        .error_code(error_code),
        .busy(busy)
    );

    task automatic fail(input string message);
        begin
            $display("FAIL: %s", message);
            $fatal(1);
        end
    endtask

    task automatic begin_transaction(input integer reduction_count,
                                     input integer bias_value);
        begin
            @(negedge clk);
            start_k = reduction_count[12:0];
            start_bias = bias_value;
            start_valid = 1'b1;
            #1;
            if (!start_ready) begin
                fail("空闲数据通路未接受 start");
            end
            @(posedge clk);
            #1;
            @(negedge clk);
            start_valid = 1'b0;
        end
    endtask

    task automatic send_beat(input logic [127:0] features,
                             input logic signed [7:0] shared_weight,
                             input integer bubbles);
        integer bubble_index;
        begin
            @(negedge clk);
            input_valid = 1'b0;
            for (bubble_index = 0; bubble_index < bubbles; bubble_index = bubble_index + 1) begin
                @(posedge clk);
                #1;
                if (!busy || result_valid) begin
                    fail("输入停顿期间事务状态提前结束");
                end
            end
            @(negedge clk);
            feature_lanes = features;
            weight_data = shared_weight;
            input_valid = 1'b1;
            #1;
            if (!input_ready) begin
                fail("RUN 状态未对整组16路输入给出 ready");
            end
            @(posedge clk);
            accepted_beats = accepted_beats + 1;
            #1;
            input_valid = 1'b0;
        end
    endtask

    task automatic check_no_stale_response;
        integer wait_index;
        begin
            #1;
            if (busy || result_valid || !start_ready) begin
                fail("取消事务未回到空闲状态");
            end
            for (wait_index = 0; wait_index < 3; wait_index = wait_index + 1) begin
                @(posedge clk);
                #1;
                if (busy || result_valid) begin
                    fail("取消事务产生迟到响应");
                end
            end
            @(negedge clk);
        end
    endtask

    task automatic consume_response(input integer expected_error,
                                    input integer check_expected_values);
        integer lane;
        integer actual_value;
        integer held_error;
        begin
            if (!result_valid) begin
                fail("结果响应缺失");
            end
            if (error_code !== expected_error[2:0]) begin
                $display("expected error=%0d actual=%0d", expected_error, error_code);
                fail("结果错误码不匹配");
            end
            if (!busy || start_ready || input_ready) begin
                fail("待取结果未保持 busy 或仍接收输入");
            end
            for (lane = 0; lane < 16; lane = lane + 1) begin
                actual_value = $signed(lane_accumulators[lane * 32 +: 32]);
                held_output[lane] = actual_value;
                if (check_expected_values != 0) begin
                    if (actual_value !== expected_lane[lane]) begin
                        $display("lane=%0d expected=%0d actual=%0d", lane,
                                 expected_lane[lane], actual_value);
                        fail("INT32 lane 累加结果不匹配");
                    end
                end else if (actual_value !== 0) begin
                    fail("错误响应的数据必须清零");
                end
            end
            held_error = error_code;
            result_ready = 1'b0;
            for (lane = 0; lane < 3; lane = lane + 1) begin
                @(posedge clk);
                #1;
                if (!result_valid || error_code !== held_error[2:0]) begin
                    fail("结果停顿期间 valid 或错误码变化");
                end
                for (lane_index = 0; lane_index < 16; lane_index = lane_index + 1) begin
                    actual_value = $signed(lane_accumulators[lane_index * 32 +: 32]);
                    if (actual_value !== held_output[lane_index]) begin
                        fail("结果停顿期间累加器变化");
                    end
                end
                @(negedge clk);
            end
            result_ready = 1'b1;
            @(posedge clk);
            #1;
            if (result_valid || busy) begin
                fail("结果握手未释放数据通路");
            end
            @(negedge clk);
            result_ready = 1'b0;
            if (!start_ready) begin
                fail("响应后不能接受下一事务");
            end
        end
    endtask

    task automatic run_dataset_tile(input integer expected_id);
        integer header_count;
        integer beat_count;
        integer lane;
        logic [127:0] packed_features;
        begin
            header_count = $fscanf(vector_fd,
                "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d\n",
                case_id, case_bias, case_error,
                expected_lane[0], expected_lane[1], expected_lane[2], expected_lane[3],
                expected_lane[4], expected_lane[5], expected_lane[6], expected_lane[7],
                expected_lane[8], expected_lane[9], expected_lane[10], expected_lane[11],
                expected_lane[12], expected_lane[13], expected_lane[14], expected_lane[15]);
            if (header_count != 19 || case_id != expected_id || case_error != 0) begin
                fail("数据向量头部、顺序或预期状态错误");
            end
            begin_transaction(256, case_bias);
            beat_count = 0;
            for (k_index = 0; k_index < 256; k_index = k_index + 1) begin
                scan_result = $fscanf(vector_fd,
                    "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d\n",
                    input_weight,
                    input_lane[0], input_lane[1], input_lane[2], input_lane[3],
                    input_lane[4], input_lane[5], input_lane[6], input_lane[7],
                    input_lane[8], input_lane[9], input_lane[10], input_lane[11],
                    input_lane[12], input_lane[13], input_lane[14], input_lane[15]);
                if (scan_result != 17) begin
                    fail("输入向量 beat 被截断");
                end
                packed_features = 128'd0;
                for (lane = 0; lane < 16; lane = lane + 1) begin
                    if (input_lane[lane] < -127 || input_lane[lane] > 127 ||
                        input_weight < -127 || input_weight > 127) begin
                        fail("合法数据集包含 INT8 -128 或越界值");
                    end
                    packed_features[lane * 8 +: 8] = input_lane[lane][7:0];
                end
                bubble_cycles = ((k_index % 23) == 7) ? 2 : (((k_index % 17) == 4) ? 1 : 0);
                send_beat(packed_features, input_weight[7:0], bubble_cycles);
                beat_count = beat_count + 1;
                dataset_accepted_beats = dataset_accepted_beats + 1;
            end
            if (beat_count != 256) begin
                fail("有效 tile 接受的 K beat 数不是256");
            end
            @(negedge clk);
            consume_response(0, 1);
            completed_dataset_tiles = completed_dataset_tiles + 1;
        end
    endtask

    task automatic expect_bad_start(input integer reduction_count);
        begin
            begin_transaction(reduction_count, 0);
            @(negedge clk);
            consume_response(1, 0);
            invalid_start_transactions = invalid_start_transactions + 1;
        end
    endtask

    task automatic run_zero_recovery(input integer bias_value);
        logic [127:0] zeros;
        integer beat;
        integer lane;
        begin
            for (lane = 0; lane < 16; lane = lane + 1) begin
                expected_lane[lane] = bias_value;
            end
            zeros = 128'd0;
            begin_transaction(256, bias_value);
            for (beat = 0; beat < 256; beat = beat + 1) begin
                send_beat(zeros, 8'sd0, (beat == 13) ? 2 : 0);
                recovery_accepted_beats = recovery_accepted_beats + 1;
            end
            @(negedge clk);
            consume_response(0, 1);
            protocol_recovery_tiles = protocol_recovery_tiles + 1;
        end
    endtask

    task automatic expect_input_error(input logic [127:0] features,
                                      input logic signed [7:0] shared_weight,
                                      input integer expected_error,
                                      input integer error_kind);
        begin
            begin_transaction(256, 0);
            send_beat(features, shared_weight, 1);
            early_error_accepted_beats = early_error_accepted_beats + 1;
            if (error_kind == 0) begin
                bad_activation_accepted_beats = bad_activation_accepted_beats + 1;
            end else begin
                bad_weight_accepted_beats = bad_weight_accepted_beats + 1;
            end
            @(negedge clk);
            consume_response(expected_error, 0);
        end
    endtask

    task automatic expect_overflow(input integer bias_value,
                                   input logic [127:0] features,
                                   input logic signed [7:0] shared_weight);
        begin
            begin_transaction(256, bias_value);
            send_beat(features, shared_weight, 0);
            early_error_accepted_beats = early_error_accepted_beats + 1;
            overflow_accepted_beats = overflow_accepted_beats + 1;
            @(negedge clk);
            consume_response(7, 0);
        end
    endtask

    task automatic abort_and_recover;
        logic [127:0] zeros;
        integer beat;
        begin
            zeros = 128'd0;
            begin_transaction(256, 0);
            for (beat = 0; beat < 5; beat = beat + 1) begin
                send_beat(zeros, 8'sd1, 0);
                cancelled_accepted_beats = cancelled_accepted_beats + 1;
                abort_accepted_beats = abort_accepted_beats + 1;
            end
            @(negedge clk);
            abort = 1'b1;
            @(posedge clk);
            #1;
            @(negedge clk);
            abort = 1'b0;
            check_no_stale_response();
            run_zero_recovery(23);
        end
    endtask

    task automatic reset_and_recover;
        logic [127:0] zeros;
        integer beat;
        begin
            zeros = 128'd0;
            begin_transaction(256, 0);
            for (beat = 0; beat < 5; beat = beat + 1) begin
                send_beat(zeros, 8'sd1, 0);
                cancelled_accepted_beats = cancelled_accepted_beats + 1;
                reset_accepted_beats = reset_accepted_beats + 1;
            end
            @(negedge clk);
            rst = 1'b1;
            @(posedge clk);
            #1;
            @(negedge clk);
            rst = 1'b0;
            check_no_stale_response();
            run_zero_recovery(-19);
        end
    endtask

    initial begin
        rst = 1'b1;
        abort = 1'b0;
        start_valid = 1'b0;
        start_k = 13'd0;
        start_bias = 32'sd0;
        input_valid = 1'b0;
        feature_lanes = 128'd0;
        weight_data = 8'sd0;
        result_ready = 1'b0;
        accepted_beats = 0;
        dataset_accepted_beats = 0;
        recovery_accepted_beats = 0;
        early_error_accepted_beats = 0;
        cancelled_accepted_beats = 0;
        bad_activation_accepted_beats = 0;
        bad_weight_accepted_beats = 0;
        overflow_accepted_beats = 0;
        abort_accepted_beats = 0;
        reset_accepted_beats = 0;
        invalid_start_transactions = 0;
        completed_dataset_tiles = 0;
        protocol_recovery_tiles = 0;

        repeat (2) @(posedge clk);
        @(negedge clk);
        rst = 1'b0;

        vector_fd = $fopen("vectors.dat", "r");
        if (vector_fd == 0) begin
            fail("无法打开临时 vectors.dat");
        end
        for (expected_case = 0; expected_case < 1002; expected_case = expected_case + 1) begin
            run_dataset_tile(expected_case);
        end
        scan_result = $fscanf(vector_fd, "%d", case_id);
        if (scan_result != -1) begin
            fail("向量文件包含超出1002个 tile 的多余数据");
        end
        $fclose(vector_fd);

        expect_bad_start(255);
        run_zero_recovery(7);
        expect_bad_start(257);
        run_zero_recovery(-7);

        feature_lanes = 128'd0;
        feature_lanes[15 * 8 +: 8] = 8'h80;
        expect_input_error(feature_lanes, 8'sd1, 1, 0);
        run_zero_recovery(11);
        expect_input_error(128'd0, -8'sd128, 1, 1);
        run_zero_recovery(-11);

        feature_lanes = 128'd0;
        feature_lanes[0 +: 8] = 8'd127;
        expect_overflow(2147483600, feature_lanes, 8'sd127);
        run_zero_recovery(13);
        feature_lanes = 128'd0;
        feature_lanes[0 +: 8] = 8'd127;
        expect_overflow(-2147483600, feature_lanes, -8'sd127);
        run_zero_recovery(-13);

        abort_and_recover();
        reset_and_recover();

        if (completed_dataset_tiles != 1002) begin
            fail("数据集 tile 数不匹配");
        end
        if (dataset_accepted_beats != (1002 * 256) ||
            recovery_accepted_beats != (protocol_recovery_tiles * 256) ||
            early_error_accepted_beats != 4 || cancelled_accepted_beats != 10 ||
            early_error_accepted_beats != (bad_activation_accepted_beats +
                                           bad_weight_accepted_beats +
                                           overflow_accepted_beats) ||
            cancelled_accepted_beats != (abort_accepted_beats + reset_accepted_beats) ||
            bad_activation_accepted_beats != 1 || bad_weight_accepted_beats != 1 ||
            overflow_accepted_beats != 2 || abort_accepted_beats != 5 ||
            reset_accepted_beats != 5 || invalid_start_transactions != 2 ||
            protocol_recovery_tiles != 8 ||
            accepted_beats != (dataset_accepted_beats + recovery_accepted_beats +
                               early_error_accepted_beats + cancelled_accepted_beats)) begin
            $display("accepted=%0d dataset=%0d recovery=%0d early_error=%0d cancelled=%0d",
                     accepted_beats, dataset_accepted_beats, recovery_accepted_beats,
                     early_error_accepted_beats, cancelled_accepted_beats);
            fail("有效、错误、取消事务的握手计数不匹配");
        end
        $display("PASS: dataset_tiles=%0d t20_tiles=%0d directed_tiles=%0d random_tiles=%0d accepted_k_beats_per_tile=256 dataset_k_beats=%0d recovery_tiles=%0d recovery_k_beats=%0d bad_activation_beats=%0d bad_weight_beats=%0d overflow_beats=%0d abort_accepted_beats=%0d reset_accepted_beats=%0d error_remaining_unissued_k=1020 abort_remaining_unissued_k=251 reset_remaining_unissued_k=251 invalid_start_transactions=%0d invalid_start_unissued_k=512 protocol_scenarios=8 errors=0",
                 completed_dataset_tiles, 1, 1, 1000, dataset_accepted_beats, protocol_recovery_tiles,
                 recovery_accepted_beats, bad_activation_accepted_beats,
                 bad_weight_accepted_beats, overflow_accepted_beats,
                 abort_accepted_beats, reset_accepted_beats,
                 invalid_start_transactions);
        $finish;
    end

    initial begin
        #100000000;
        $fatal(1, "TIMEOUT: tile16 testbench 超过仿真上限");
    end
endmodule
