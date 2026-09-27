`timescale 1ns/1ps

module tb_s2a_conv_layer35_row9_all_channels;
    localparam integer INPUT_BASE = 27706496;
    localparam integer INPUT_BYTES = 259584;
    localparam integer OUTPUT_BASE = 27966080;
    localparam integer OUTPUT_PIXELS = 676;
    localparam integer INPUT_CHANNELS = 384;
    localparam integer OUTPUT_CHANNELS = 256;
    localparam integer REDUCTION = 3456;
    localparam integer NUM_POINTS = 26;
    localparam integer NUM_OUTPUTS = OUTPUT_CHANNELS * NUM_POINTS;
    localparam integer EXPECTED_PADDING_TAPS = OUTPUT_CHANNELS * INPUT_CHANNELS * 6;
    localparam integer EXPECTED_EDGE_PADDING = OUTPUT_CHANNELS * INPUT_CHANNELS * 3;
    localparam integer EXPECTED_VALID_TAPS = NUM_OUTPUTS * REDUCTION - EXPECTED_PADDING_TAPS;
    localparam integer WEIGHT_ABSOLUTE_BASE = 32'h00100000 + 5010412;
    localparam integer WEIGHT_BYTES = 884736;

    logic clk = 1'b0;
    logic hard_reset = 1'b0;
    logic abort = 1'b0;
    logic buffer_owner_pl = 1'b1;
    logic start_valid = 1'b0;
    logic start_ready;
    logic [31:0] output_channel = 0;
    logic [31:0] output_y = 0;
    logic [31:0] output_x = 0;
    logic signed [31:0] bias_int32 = 0;
    logic [31:0] positive_multiplier = 0;
    logic [31:0] positive_q_shift = 0;
    logic [31:0] negative_multiplier = 0;
    logic [31:0] negative_q_shift = 0;
    logic busy;
    logic result_valid;
    logic result_ready = 1'b1;
    logic [31:0] result_output_address;
    logic [7:0] result_value;
    logic [2:0] result_error_code;
    logic backend_cancel;
    logic backend_req_valid;
    logic backend_req_ready = 1'b0;
    logic backend_req_write;
    logic [31:0] backend_req_addr;
    logic [31:0] backend_req_wdata;
    logic [3:0] backend_req_rstrb;
    logic [3:0] backend_req_wstrb;
    logic backend_rsp_valid = 1'b0;
    logic [31:0] backend_rsp_rdata = 0;
    logic [2:0] backend_rsp_error = 0;

    reg [7:0] feature_memory [0:INPUT_BYTES-1];
    reg [7:0] weight_memory [0:WEIGHT_BYTES-1];
    reg [7:0] output_memory [0:NUM_OUTPUTS-1];
    reg [31:0] expected_raw [0:NUM_OUTPUTS-1];
    reg [7:0] expected_quantized [0:NUM_OUTPUTS-1];
    integer vector_channel [0:NUM_OUTPUTS-1];
    integer vector_y [0:NUM_OUTPUTS-1];
    integer vector_x [0:NUM_OUTPUTS-1];
    integer vector_bias [0:NUM_OUTPUTS-1];
    integer vector_positive_m [0:NUM_OUTPUTS-1];
    integer vector_positive_q [0:NUM_OUTPUTS-1];
    integer vector_negative_m [0:NUM_OUTPUTS-1];
    integer vector_negative_q [0:NUM_OUTPUTS-1];

    integer raw_trace_fd;
    integer output_trace_fd;
    integer fixture_fd;
    integer vectors_fd;
    integer initial_index;
    integer runtime_lane;
    integer byte_value;
    integer raw_word;
    integer request_class_now;
    integer selected_lane;
    integer selected_byte_address;
    integer expected_byte_address;
    integer search_k;
    integer channel_index;
    integer kernel_y;
    integer kernel_x;
    integer input_y;
    integer input_x;
    integer write_byte;
    integer output_address_expected;
    integer active_case_index;
    integer expected_next_k;
    integer active_weight_k;
    integer expect_weight_request;
    integer class_transfer_count [0:2];
    integer class_stall_cycles [0:2];
    integer stall_slot_count [0:2][0:4];
    integer frozen_stall_sequence [0:4];
    integer active_stall_class;
    integer active_stall_slot;
    integer active_stall_expected;
    integer active_stall_low_cycles;
    integer stall_remaining;
    integer stall_class;
    integer forced_stall_class;
    integer forced_error_class;
    integer forced_error_code;
    integer pending_response;
    integer pending_error;
    integer pending_data;
    integer feature_read_count;
    integer weight_read_count;
    integer output_write_count;
    integer output_commit_count;
    integer raw_compare_count;
    integer output_compare_count;
    integer result_compare_count;
    integer padding_tap_count;
    integer tap_visit_count;
    integer row_edge_pad_count [0:1];
    integer feature_lane_mask;
    integer weight_lane_mask;
    integer output_lane_mask;
    integer fault_response_count;
    integer error_code_mask;
    integer abort_cancel_count;
    integer reset_cancel_count;
    integer recovery_count;
    integer saved_output_commits;
    integer watchdog;
    integer stalled_request_cycles;
    integer request_accepted_since_negedge;
    integer was_stalled;
    integer stalled_write;
    integer stalled_address;
    integer stalled_wdata;
    integer stalled_rstrb;
    integer stalled_wstrb;
    integer capture_enable;
    integer current_low_index;
    integer error_result_count;
    integer abort_seen;

    always #5 clk = ~clk;

    s2a_conv_layer35_channel_probe dut (
        .clk(clk), .hard_reset(hard_reset), .abort(abort),
        .buffer_owner_pl(buffer_owner_pl), .start_valid(start_valid),
        .start_ready(start_ready), .output_channel(output_channel),
        .output_y(output_y), .output_x(output_x), .bias_int32(bias_int32),
        .positive_multiplier(positive_multiplier), .positive_q_shift(positive_q_shift),
        .negative_multiplier(negative_multiplier), .negative_q_shift(negative_q_shift),
        .busy(busy), .result_valid(result_valid), .result_ready(result_ready),
        .result_output_address(result_output_address), .result_value(result_value),
        .result_error_code(result_error_code), .backend_cancel(backend_cancel),
        .backend_req_valid(backend_req_valid), .backend_req_ready(backend_req_ready),
        .backend_req_write(backend_req_write), .backend_req_addr(backend_req_addr),
        .backend_req_wdata(backend_req_wdata), .backend_req_rstrb(backend_req_rstrb),
        .backend_req_wstrb(backend_req_wstrb), .backend_rsp_valid(backend_rsp_valid),
        .backend_rsp_rdata(backend_rsp_rdata), .backend_rsp_error(backend_rsp_error)
    );

    function automatic integer classify_request;
        integer lane;
        integer absolute_address;
        begin
            lane = -1;
            for (integer lane_index = 0; lane_index < 4; lane_index = lane_index + 1) begin
                if (!backend_req_write && backend_req_rstrb[lane_index]) lane = lane_index;
                if (backend_req_write && backend_req_wstrb[lane_index]) lane = lane_index;
            end
            absolute_address = backend_req_addr + lane;
            if (backend_req_write) classify_request = 3;
            else if ((absolute_address >= WEIGHT_ABSOLUTE_BASE) &&
                     (absolute_address < WEIGHT_ABSOLUTE_BASE + WEIGHT_BYTES)) classify_request = 2;
            else classify_request = 1;
        end
    endfunction

    task automatic apply_case(input integer case_index);
        begin
            output_channel = vector_channel[case_index];
            output_y = vector_y[case_index];
            output_x = vector_x[case_index];
            bias_int32 = vector_bias[case_index];
            positive_multiplier = vector_positive_m[case_index];
            positive_q_shift = vector_positive_q[case_index];
            negative_multiplier = vector_negative_m[case_index];
            negative_q_shift = vector_negative_q[case_index];
        end
    endtask

    task automatic launch_case(input integer case_index);
        begin
            @(negedge clk);
            apply_case(case_index);
            watchdog = 0;
            while (!start_ready) begin
                @(negedge clk);
                watchdog = watchdog + 1;
                if (watchdog > 100) $fatal(1, "启动接口未恢复空闲");
            end
            start_valid = 1'b1;
            @(posedge clk);
            @(negedge clk);
            start_valid = 1'b0;
        end
    endtask

    task automatic wait_result(input integer expected_error, input integer maximum_cycles);
        begin
            watchdog = 0;
            while (!result_valid) begin
                @(negedge clk);
                watchdog = watchdog + 1;
                if (watchdog > maximum_cycles)
                    $fatal(1, "等待 result 超时，expected_error=%0d", expected_error);
            end
            if (result_error_code !== expected_error[2:0])
                $fatal(1, "result error=%0d expected=%0d", result_error_code, expected_error);
            error_code_mask = error_code_mask | (1 << result_error_code);
            @(posedge clk);
            @(negedge clk);
        end
    endtask

    task automatic wait_held_request(input integer target_class, input integer maximum_cycles);
        begin
            watchdog = 0;
            while (!(backend_req_valid && !backend_req_ready &&
                     (classify_request() == target_class))) begin
                @(negedge clk);
                watchdog = watchdog + 1;
                if (watchdog > maximum_cycles)
                    $fatal(1, "未到达受阻内存请求 class=%0d", target_class);
            end
        end
    endtask

    task automatic cancel_held_request(input integer use_reset);
        begin
            @(negedge clk);
            if (use_reset != 0) hard_reset = 1'b1;
            else abort = 1'b1;
            @(posedge clk);
            @(negedge clk);
            hard_reset = 1'b0;
            abort = 1'b0;
            forced_stall_class = 0;
            backend_req_ready = 1'b0;
            watchdog = 0;
            while (!start_ready) begin
                @(negedge clk);
                watchdog = watchdog + 1;
                if (watchdog > 30) $fatal(1, "取消后启动接口未恢复");
            end
        end
    endtask

    initial begin
        frozen_stall_sequence[0] = 0;
        frozen_stall_sequence[1] = 1;
        frozen_stall_sequence[2] = 2;
        frozen_stall_sequence[3] = 7;
        frozen_stall_sequence[4] = 3;
        capture_enable = 0;
        forced_stall_class = 0;
        forced_error_class = 0;
        forced_error_code = 0;
        pending_response = 0;
        pending_error = 0;
        pending_data = 0;
        expected_next_k = 0;
        active_weight_k = -1;
        expect_weight_request = 0;
        active_case_index = 0;
        result_compare_count = 0;
        raw_compare_count = 0;
        output_compare_count = 0;
        feature_read_count = 0;
        weight_read_count = 0;
        output_write_count = 0;
        output_commit_count = 0;
        padding_tap_count = 0;
        tap_visit_count = 0;
        feature_lane_mask = 0;
        weight_lane_mask = 0;
        output_lane_mask = 0;
        fault_response_count = 0;
        error_code_mask = 0;
        abort_cancel_count = 0;
        reset_cancel_count = 0;
        recovery_count = 0;
        stalled_request_cycles = 0;
        request_accepted_since_negedge = 0;
        was_stalled = 0;
        stall_class = 0;
        active_stall_class = 0;
        active_stall_slot = 0;
        active_stall_expected = 0;
        active_stall_low_cycles = 0;
        stall_remaining = 0;
        error_result_count = 0;
        abort_seen = 0;
        for (initial_index = 0; initial_index < 3; initial_index = initial_index + 1) begin
            class_transfer_count[initial_index] = 0;
            class_stall_cycles[initial_index] = 0;
            for (integer slot_index = 0; slot_index < 5; slot_index = slot_index + 1)
                stall_slot_count[initial_index][slot_index] = 0;
        end
        for (initial_index = 0; initial_index < 2; initial_index = initial_index + 1)
            row_edge_pad_count[initial_index] = 0;
        for (initial_index = 0; initial_index < NUM_OUTPUTS; initial_index = initial_index + 1)
            output_memory[initial_index] = 8'd0;

        fixture_fd = $fopen("feature_input.bin", "rb");
        if (fixture_fd == 0) $fatal(1, "无法打开 feature_input.bin");
        for (initial_index = 0; initial_index < INPUT_BYTES; initial_index = initial_index + 1) begin
            byte_value = $fgetc(fixture_fd);
            if (byte_value < 0) $fatal(1, "feature fixture 截断");
            feature_memory[initial_index] = byte_value[7:0];
        end
        if ($fgetc(fixture_fd) != -1) $fatal(1, "feature fixture 长度过长");
        $fclose(fixture_fd);

        fixture_fd = $fopen("layer35_weights.bin", "rb");
        if (fixture_fd == 0) $fatal(1, "无法打开 layer35_weights.bin");
        for (initial_index = 0; initial_index < WEIGHT_BYTES; initial_index = initial_index + 1) begin
            byte_value = $fgetc(fixture_fd);
            if (byte_value < 0) $fatal(1, "layer35 weights 截断");
            weight_memory[initial_index] = byte_value[7:0];
        end
        if ($fgetc(fixture_fd) != -1) $fatal(1, "layer35 weights 长度过长");
        $fclose(fixture_fd);

        fixture_fd = $fopen("golden.bin", "rb");
        if (fixture_fd == 0) $fatal(1, "无法打开 golden.bin");
        for (initial_index = 0; initial_index < NUM_OUTPUTS; initial_index = initial_index + 1) begin
            byte_value = $fgetc(fixture_fd); if (byte_value < 0) $fatal(1, "raw golden 截断");
            raw_word = byte_value;
            byte_value = $fgetc(fixture_fd); if (byte_value < 0) $fatal(1, "raw golden 截断");
            raw_word = raw_word | (byte_value << 8);
            byte_value = $fgetc(fixture_fd); if (byte_value < 0) $fatal(1, "raw golden 截断");
            raw_word = raw_word | (byte_value << 16);
            byte_value = $fgetc(fixture_fd); if (byte_value < 0) $fatal(1, "raw golden 截断");
            raw_word = raw_word | (byte_value << 24);
            expected_raw[initial_index] = raw_word[31:0];
        end
        for (initial_index = 0; initial_index < NUM_OUTPUTS; initial_index = initial_index + 1) begin
            byte_value = $fgetc(fixture_fd);
            if (byte_value < 0) $fatal(1, "INT8 golden 截断");
            expected_quantized[initial_index] = byte_value[7:0];
        end
        if ($fgetc(fixture_fd) != -1) $fatal(1, "golden 长度过长");
        $fclose(fixture_fd);

        vectors_fd = $fopen("vectors.txt", "r");
        if (vectors_fd == 0) $fatal(1, "无法打开 vectors.txt");
        for (initial_index = 0; initial_index < NUM_OUTPUTS; initial_index = initial_index + 1) begin
            current_low_index = $fscanf(vectors_fd, "%d %d %d %d %d %d %d %d",
                vector_channel[initial_index], vector_y[initial_index], vector_x[initial_index], vector_bias[initial_index],
                vector_positive_m[initial_index], vector_positive_q[initial_index],
                vector_negative_m[initial_index], vector_negative_q[initial_index]);
            if (current_low_index != 8) $fatal(1, "vectors.txt 行格式错误 index=%0d", initial_index);
            if (vector_channel[initial_index] != initial_index / NUM_POINTS)
                $fatal(1, "向量输出通道序号不连续 index=%0d", initial_index);
            if ((vector_y[initial_index] != 9) ||
                (vector_x[initial_index] != (initial_index % NUM_POINTS)))
                $fatal(1, "向量不是按通道递增的 y=9 全行坐标 index=%0d", initial_index);
        end
        $fclose(vectors_fd);

        hard_reset = 1'b1;
        repeat (2) @(posedge clk);
        @(negedge clk);
        hard_reset = 1'b0;
        repeat (2) @(negedge clk);
        if (!start_ready) $fatal(1, "复位后启动接口未就绪");

        forced_error_class = 1;
        forced_error_code = 1;
        launch_case(0);
        wait_result(1, 20000);
        forced_error_class = 0;
        forced_error_code = 0;
        error_result_count = error_result_count + 1;

        forced_error_class = 2;
        forced_error_code = 2;
        launch_case(0);
        wait_result(2, 100000);
        forced_error_class = 0;
        forced_error_code = 0;
        error_result_count = error_result_count + 1;

        forced_error_class = 3;
        forced_error_code = 6;
        saved_output_commits = output_commit_count;
        launch_case(0);
        wait_result(6, 150000);
        forced_error_class = 0;
        forced_error_code = 0;
        if (output_commit_count != saved_output_commits)
            $fatal(1, "输出写 error 产生了存储副作用");
        error_result_count = error_result_count + 1;

        forced_stall_class = 1;
        launch_case(0);
        wait_held_request(1, 100000);
        cancel_held_request(0);
        abort_cancel_count = abort_cancel_count + 1;

        forced_stall_class = 1;
        launch_case(0);
        wait_held_request(1, 100000);
        cancel_held_request(1);
        reset_cancel_count = reset_cancel_count + 1;

        forced_stall_class = 3;
        saved_output_commits = output_commit_count;
        launch_case(0);
        wait_held_request(3, 150000);
        cancel_held_request(0);
        abort_cancel_count = abort_cancel_count + 1;
        if (output_commit_count != saved_output_commits)
            $fatal(1, "被取消的 output write 产生了存储副作用");

        forced_stall_class = 0;
        hard_reset = 1'b1;
        @(posedge clk);
        @(negedge clk);
        hard_reset = 1'b0;
        repeat (2) @(negedge clk);
        if (!start_ready) $fatal(1, "smoke 后复位未恢复启动接口");
        for (initial_index = 0; initial_index < NUM_OUTPUTS; initial_index = initial_index + 1)
            output_memory[initial_index] = 8'd0;

        raw_trace_fd = $fopen("observed_raw.bin", "wb");
        output_trace_fd = $fopen("observed_output.bin", "wb");
        if ((raw_trace_fd == 0) || (output_trace_fd == 0))
            $fatal(1, "无法创建 RTL 观察 trace");
        capture_enable = 1;
        for (initial_index = 0; initial_index < 3; initial_index = initial_index + 1) begin
            class_transfer_count[initial_index] = 0;
            class_stall_cycles[initial_index] = 0;
            for (integer slot_index = 0; slot_index < 5; slot_index = slot_index + 1)
                stall_slot_count[initial_index][slot_index] = 0;
        end
        for (initial_index = 0; initial_index < 2; initial_index = initial_index + 1)
            row_edge_pad_count[initial_index] = 0;
        feature_read_count = 0;
        weight_read_count = 0;
        output_write_count = 0;
        output_commit_count = 0;
        raw_compare_count = 0;
        output_compare_count = 0;
        result_compare_count = 0;
        padding_tap_count = 0;
        tap_visit_count = 0;
        feature_lane_mask = 0;
        weight_lane_mask = 0;
        output_lane_mask = 0;
        stalled_request_cycles = 0;
        stall_remaining = 0;
        active_stall_low_cycles = 0;
        request_accepted_since_negedge = 0;
        was_stalled = 0;

        for (initial_index = 0; initial_index < NUM_OUTPUTS; initial_index = initial_index + 1) begin
            launch_case(initial_index);
            watchdog = 0;
            while (result_compare_count <= initial_index) begin
                @(negedge clk);
                watchdog = watchdog + 1;
                if (watchdog > 100000)
                    $fatal(1, "单输出等待超时 index=%0d", initial_index);
            end
        end
        capture_enable = 0;
        $fclose(raw_trace_fd);
        $fclose(output_trace_fd);

        if ((result_compare_count != NUM_OUTPUTS) || (raw_compare_count != NUM_OUTPUTS) ||
            (output_compare_count != NUM_OUTPUTS) || (output_write_count != NUM_OUTPUTS) ||
            (output_commit_count != NUM_OUTPUTS) || (error_result_count != 3) ||
            (error_code_mask != 8'h46) || (fault_response_count != 3) ||
            (abort_cancel_count < 2) || (reset_cancel_count != 1))
            $fatal(1, "输出数或 error/cancel smoke 覆盖不完整");
        if ((feature_lane_mask != 15) || (weight_lane_mask != 15) || (output_lane_mask != 15))
            $fatal(1, "byte lane 覆盖不完整 feature=%0x weight=%0x output=%0x",
                   feature_lane_mask, weight_lane_mask, output_lane_mask);
        if ((tap_visit_count != (NUM_OUTPUTS * REDUCTION)) ||
            (padding_tap_count != EXPECTED_PADDING_TAPS))
            $fatal(1, "kernel tap/padding 数错误 taps=%0d pad=%0d", tap_visit_count, padding_tap_count);
        if ((row_edge_pad_count[0] != EXPECTED_EDGE_PADDING) ||
            (row_edge_pad_count[1] != EXPECTED_EDGE_PADDING))
            $fatal(1, "y=9 左右边界 padding 覆盖不符: %0d,%0d",
                   row_edge_pad_count[0], row_edge_pad_count[1]);
        if ((feature_read_count != EXPECTED_VALID_TAPS) ||
            (weight_read_count != EXPECTED_VALID_TAPS))
            $fatal(1, "feature/weight transfer 数错误 feature=%0d weight=%0d",
                   feature_read_count, weight_read_count);
        if ((class_transfer_count[0] != feature_read_count) ||
            (class_transfer_count[1] != weight_read_count) ||
            (class_transfer_count[2] != NUM_OUTPUTS))
            $fatal(1, "冻结停顿类别 transfer 数与事务数不一致");

        $display("PASS T45 outputs=%0d raw=%0d feature_reads=%0d weight_reads=%0d output_writes=%0d padding=%0d taps=%0d feature_lanes=%0d weight_lanes=%0d output_lanes=%0d error_mask=%0d fault_responses=%0d abort_cancel=%0d reset_cancel=%0d recovery=%0d request_stalls=%0d feature_transfers=%0d feature_stall_cycles=%0d feature_slot0=%0d feature_slot1=%0d feature_slot2=%0d feature_slot3=%0d feature_slot4=%0d weight_transfers=%0d weight_stall_cycles=%0d weight_slot0=%0d weight_slot1=%0d weight_slot2=%0d weight_slot3=%0d weight_slot4=%0d output_transfers=%0d output_stall_cycles=%0d output_slot0=%0d output_slot1=%0d output_slot2=%0d output_slot3=%0d output_slot4=%0d",
            result_compare_count, raw_compare_count, feature_read_count, weight_read_count,
            output_write_count, padding_tap_count, tap_visit_count,
            feature_lane_mask, weight_lane_mask, output_lane_mask, error_code_mask,
            fault_response_count, abort_cancel_count, reset_cancel_count, recovery_count,
            stalled_request_cycles, class_transfer_count[0], class_stall_cycles[0],
            stall_slot_count[0][0], stall_slot_count[0][1], stall_slot_count[0][2],
            stall_slot_count[0][3], stall_slot_count[0][4],
            class_transfer_count[1], class_stall_cycles[1],
            stall_slot_count[1][0], stall_slot_count[1][1], stall_slot_count[1][2],
            stall_slot_count[1][3], stall_slot_count[1][4],
            class_transfer_count[2], class_stall_cycles[2],
            stall_slot_count[2][0], stall_slot_count[2][1], stall_slot_count[2][2],
            stall_slot_count[2][3], stall_slot_count[2][4]);
        $finish;
    end

    always @(negedge clk) begin
        if (hard_reset || abort || !backend_req_valid) begin
            backend_req_ready = 1'b0;
            stall_remaining = 0;
            active_stall_low_cycles = 0;
            request_accepted_since_negedge = 0;
        end else begin
            request_class_now = classify_request();
            if (forced_stall_class == request_class_now) begin
                backend_req_ready = 1'b0;
                stall_class = request_class_now;
            end else if (!stall_remaining &&
                         ((stall_class != request_class_now) || request_accepted_since_negedge ||
                          (capture_enable && (active_stall_class != request_class_now)))) begin
                request_accepted_since_negedge = 0;
                if (capture_enable && (request_class_now >= 1) && (request_class_now <= 3)) begin
                    stall_class = request_class_now;
                    active_stall_class = request_class_now;
                    active_stall_slot = class_transfer_count[request_class_now - 1] % 5;
                    active_stall_expected = frozen_stall_sequence[active_stall_slot];
                    active_stall_low_cycles = 0;
                    stall_remaining = active_stall_expected;
                    backend_req_ready = (stall_remaining == 0);
                end else begin
                    stall_remaining = 0;
                    backend_req_ready = 1'b1;
                end
            end else if (stall_remaining > 0) begin
                stall_remaining = stall_remaining - 1;
                backend_req_ready = (stall_remaining == 0);
            end else begin
                backend_req_ready = 1'b1;
            end
        end
    end

    always @(posedge clk) begin
        if (hard_reset || backend_cancel) begin
            backend_rsp_valid <= 1'b0;
            backend_rsp_rdata <= 32'd0;
            backend_rsp_error <= 3'd0;
            pending_response = 0;
            pending_data = 0;
            pending_error = 0;
            was_stalled = 0;
        end else begin
            backend_rsp_valid <= 1'b0;
            backend_rsp_error <= 3'd0;
            if (was_stalled && (!backend_req_valid ||
                backend_req_write !== stalled_write || backend_req_addr !== stalled_address ||
                backend_req_wdata !== stalled_wdata || backend_req_rstrb !== stalled_rstrb ||
                backend_req_wstrb !== stalled_wstrb))
                $fatal(1, "backpressure期间请求字段变化");
            was_stalled = backend_req_valid && !backend_req_ready;
            if (backend_req_valid && !backend_req_ready) begin
                stalled_write = backend_req_write;
                stalled_address = backend_req_addr;
                stalled_wdata = backend_req_wdata;
                stalled_rstrb = backend_req_rstrb;
                stalled_wstrb = backend_req_wstrb;
                if (capture_enable) begin
                    request_class_now = classify_request();
                    if ((request_class_now < 1) || (request_class_now > 3) ||
                        (active_stall_class != request_class_now))
                        $fatal(1, "冻结停顿类别在请求等待期间变化");
                    active_stall_low_cycles = active_stall_low_cycles + 1;
                    stalled_request_cycles = stalled_request_cycles + 1;
                    class_stall_cycles[request_class_now - 1] =
                        class_stall_cycles[request_class_now - 1] + 1;
                end
            end
            if (pending_response && backend_req_valid && backend_req_ready)
                $fatal(1, "单 outstanding memory 协议发生重叠请求");
            if (pending_response) begin
                backend_rsp_valid <= 1'b1;
                backend_rsp_rdata <= pending_data[31:0];
                backend_rsp_error <= pending_error[2:0];
                pending_response = 0;
            end

            if (backend_req_valid && backend_req_ready) begin
                if (pending_response) $fatal(1, "memory response 尚未消费时接受新请求");
                if (backend_req_addr[1:0] != 2'b00) $fatal(1, "memory 请求 word 地址未对齐");
                selected_lane = -1;
                for (runtime_lane = 0; runtime_lane < 4; runtime_lane = runtime_lane + 1) begin
                    if (!backend_req_write && backend_req_rstrb[runtime_lane]) selected_lane = runtime_lane;
                    if (backend_req_write && backend_req_wstrb[runtime_lane]) selected_lane = runtime_lane;
                end
                if ((selected_lane < 0) ||
                    (!backend_req_write &&
                     ((backend_req_rstrb != (4'b0001 << selected_lane)) || backend_req_wstrb != 0)) ||
                    (backend_req_write &&
                     ((backend_req_wstrb != (4'b0001 << selected_lane)) || backend_req_rstrb != 0)))
                    $fatal(1, "byte strobe 不是单 lane");
                selected_byte_address = backend_req_addr + selected_lane;
                request_class_now = classify_request();
                if (capture_enable) begin
                    if ((active_stall_class != request_class_now) ||
                        (active_stall_slot != (class_transfer_count[request_class_now - 1] % 5)) ||
                        (active_stall_low_cycles != active_stall_expected))
                        $fatal(1, "冻结停顿握手不匹配 class=%0d low=%0d expected=%0d",
                               request_class_now, active_stall_low_cycles, active_stall_expected);
                    stall_slot_count[request_class_now - 1][active_stall_slot] =
                        stall_slot_count[request_class_now - 1][active_stall_slot] + 1;
                    class_transfer_count[request_class_now - 1] =
                        class_transfer_count[request_class_now - 1] + 1;
                end
                request_accepted_since_negedge = 1;
                pending_error = 0;
                pending_data = 0;
                if (forced_error_class == request_class_now) begin
                    pending_error = forced_error_code;
                    fault_response_count = fault_response_count + 1;
                end else if (request_class_now == 1) begin
                    if ((selected_byte_address < INPUT_BASE) ||
                        (selected_byte_address >= INPUT_BASE + INPUT_BYTES))
                        $fatal(1, "feature 地址超出 layer34 输入 tensor");
                    search_k = expected_next_k;
                    expected_byte_address = -1;
                    while ((search_k < REDUCTION) && (expected_byte_address < 0)) begin
                        channel_index = search_k / 9;
                        kernel_y = (search_k % 9) / 3;
                        kernel_x = search_k % 3;
                        input_y = output_y + kernel_y - 1;
                        input_x = output_x + kernel_x - 1;
                        if ((input_y >= 0) && (input_y < 26) &&
                            (input_x >= 0) && (input_x < 26))
                            expected_byte_address = INPUT_BASE + channel_index * OUTPUT_PIXELS +
                                                    input_y * 26 + input_x;
                        else search_k = search_k + 1;
                    end
                    if ((expected_byte_address < 0) || (search_k >= REDUCTION) ||
                        (selected_byte_address != expected_byte_address) ||
                        (dut.u_engine.reduction_index != search_k))
                        $fatal(1, "feature NCHW 地址或 reduction 次序错误 y=%0d x=%0d k=%0d addr=%0d expected=%0d",
                               output_y, output_x, search_k, selected_byte_address, expected_byte_address);
                    if ((backend_req_rstrb != (4'b0001 << (expected_byte_address & 3))) ||
                        (backend_req_addr != (expected_byte_address & 32'hffff_fffc)))
                        $fatal(1, "feature word/lane 地址不符");
                    active_weight_k = search_k;
                    expect_weight_request = 1;
                    if (pending_error == 0)
                        pending_data = ({24'd0, feature_memory[expected_byte_address - INPUT_BASE]} <<
                                        (selected_lane * 8));
                    feature_read_count = feature_read_count + 1;
                    if (capture_enable) feature_lane_mask = feature_lane_mask | backend_req_rstrb;
                end else if (request_class_now == 2) begin
                    expected_byte_address = WEIGHT_ABSOLUTE_BASE +
                                            output_channel * REDUCTION + active_weight_k;
                    if (!expect_weight_request || (active_weight_k < 0) ||
                        (selected_byte_address != expected_byte_address) ||
                        (dut.u_engine.reduction_index != active_weight_k))
                        $fatal(1, "weight oc*3456+k 地址/次序错误 oc=%0d k=%0d addr=%0d expected=%0d",
                               output_channel, active_weight_k, selected_byte_address, expected_byte_address);
                    if ((backend_req_rstrb != (4'b0001 << (expected_byte_address & 3))) ||
                        (backend_req_addr != (expected_byte_address & 32'hffff_fffc)))
                        $fatal(1, "weight word/lane 地址不符");
                    if (pending_error == 0)
                        pending_data = ({24'd0, weight_memory[output_channel * REDUCTION + active_weight_k]} <<
                                        (selected_lane * 8));
                    weight_read_count = weight_read_count + 1;
                    if (capture_enable) weight_lane_mask = weight_lane_mask | backend_req_rstrb;
                    expected_next_k = active_weight_k + 1;
                    expect_weight_request = 0;
                end else begin
                    output_address_expected = OUTPUT_BASE + output_channel * OUTPUT_PIXELS +
                                              output_y * 26 + output_x;
                    if ((selected_byte_address != output_address_expected) ||
                        (backend_req_addr != (output_address_expected & 32'hffff_fffc)) ||
                        (backend_req_wstrb != (4'b0001 << (output_address_expected & 3))) ||
                        (backend_req_rstrb != 0))
                        $fatal(1, "output NCHW 地址/strobe 错误 oc=%0d y=%0d x=%0d addr=%0d expected=%0d",
                               output_channel, output_y, output_x, selected_byte_address, output_address_expected);
                    write_byte = (backend_req_wdata >> (selected_lane * 8)) & 255;
                    active_case_index = result_compare_count;
                    if ((active_case_index >= NUM_OUTPUTS) ||
                        (write_byte != expected_quantized[active_case_index]))
                        $fatal(1, "output write INT8 与黄金结果不同 index=%0d", active_case_index);
                    output_write_count = output_write_count + 1;
                    if (capture_enable) output_lane_mask = output_lane_mask | backend_req_wstrb;
                    if (pending_error == 0) begin
                        output_memory[active_case_index] = write_byte[7:0];
                        output_commit_count = output_commit_count + 1;
                        if (capture_enable) begin
                            output_compare_count = output_compare_count + 1;
                            $fwrite(output_trace_fd, "%c", write_byte[7:0]);
                        end
                    end
                end
                if (request_class_now == 3) pending_data = 0;
                pending_response = 1;
            end

            if (start_valid && start_ready) begin
                expected_next_k = 0;
                active_weight_k = -1;
                expect_weight_request = 0;
                active_case_index = result_compare_count;
            end

            if (capture_enable && busy && (dut.u_engine.state == 4'd3)) begin
                tap_visit_count = tap_visit_count + 1;
                if (dut.u_engine.geometry_tap_is_padding) begin
                    padding_tap_count = padding_tap_count + 1;
                    if ((output_y == 9) && (output_x == 0)) row_edge_pad_count[0] = row_edge_pad_count[0] + 1;
                    if ((output_y == 9) && (output_x == 25)) row_edge_pad_count[1] = row_edge_pad_count[1] + 1;
                end
            end

            if (capture_enable && dut.u_engine.mac_result_valid &&
                dut.u_engine.mac_result_ready) begin
                if ((raw_compare_count >= NUM_OUTPUTS) ||
                    (dut.u_engine.mac_result_data !== expected_raw[raw_compare_count]))
                    $fatal(1, "raw INT32 不匹配 index=%0d oc=%0d y=%0d x=%0d got=%0d expected=%0d",
                           raw_compare_count, output_channel, output_y, output_x,
                           dut.u_engine.mac_result_data, expected_raw[raw_compare_count]);
                raw_word = dut.u_engine.mac_result_data;
                $fwrite(raw_trace_fd, "%c%c%c%c", raw_word[7:0], raw_word[15:8],
                        raw_word[23:16], raw_word[31:24]);
                raw_compare_count = raw_compare_count + 1;
            end

            if (result_valid && result_ready) begin
                if (result_error_code != 0) begin
                    if (capture_enable) $fatal(1, "主验证意外收到 result error=%0d", result_error_code);
                end else if (capture_enable) begin
                    output_address_expected = OUTPUT_BASE + vector_channel[result_compare_count] * OUTPUT_PIXELS +
                                              vector_y[result_compare_count] * 26 + vector_x[result_compare_count];
                    if ((result_output_address != output_address_expected) ||
                        (result_value !== expected_quantized[result_compare_count]) ||
                        (output_memory[result_compare_count] !== expected_quantized[result_compare_count]))
                        $fatal(1, "INT8 result/NCHW 地址/写入结果不匹配 index=%0d", result_compare_count);
                    result_compare_count = result_compare_count + 1;
                    recovery_count = 1;
                    if ((result_compare_count % NUM_POINTS == 0) || (result_compare_count == NUM_OUTPUTS))
                        $display("PROGRESS T45 outputs=%0d/%0d", result_compare_count, NUM_OUTPUTS);
                end
            end
        end
    end
endmodule
