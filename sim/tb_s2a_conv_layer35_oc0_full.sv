`timescale 1ns/1ps

module tb_s2a_conv_layer35_oc0_full;
    localparam integer INPUT_BASE = 27706496;
    localparam integer INPUT_BYTES = 259584;
    localparam integer OUTPUT_BASE = 27966080;
    localparam integer OUTPUT_BYTES = 173056;
    localparam integer OUTPUT_PIXELS = 676;
    localparam integer OUTPUT_WIDTH = 26;
    localparam integer CHANNEL_BYTES = 676;
    localparam integer REDUCTION = 3456;
    localparam integer WEIGHT_BASE = 1048576;
    localparam integer WEIGHT_OFFSET = 5010412;
    localparam integer WEIGHT_ABSOLUTE_BASE = WEIGHT_BASE + WEIGHT_OFFSET;
    localparam integer WEIGHT_OC0_BYTES = REDUCTION;
    localparam integer TOTAL_TAPS = OUTPUT_PIXELS * REDUCTION;
    localparam integer VALID_TAPS = 384 * 5776;
    localparam integer PAD_TAPS = TOTAL_TAPS - VALID_TAPS;

    logic clk;
    logic hard_reset;
    logic abort;
    logic buffer_owner_pl;
    logic run_valid;
    logic run_ready;
    logic run_busy;
    logic run_done;
    logic run_cancelled;
    logic [2:0] run_error_code;
    logic result_valid;
    logic result_ready;
    logic [4:0] result_y;
    logic [4:0] result_x;
    logic [31:0] result_address;
    logic [7:0] result_value;
    logic [2:0] result_error_code;
    logic backend_cancel;
    logic backend_req_valid;
    logic backend_req_ready;
    logic backend_req_write;
    logic [31:0] backend_req_addr;
    logic [31:0] backend_req_wdata;
    logic [3:0] backend_req_rstrb;
    logic [3:0] backend_req_wstrb;
    logic backend_rsp_valid;
    logic [31:0] backend_rsp_rdata;
    logic [2:0] backend_rsp_error;

    reg [7:0] feature_memory [0:INPUT_BYTES-1];
    reg [7:0] weight_oc0 [0:WEIGHT_OC0_BYTES-1];
    reg [7:0] output_memory [0:OUTPUT_PIXELS-1];
    reg signed [31:0] expected_raw [0:OUTPUT_PIXELS-1];
    reg [7:0] expected_quantized [0:OUTPUT_PIXELS-1];

    integer raw_trace_fd;
    integer output_trace_fd;
    integer fixture_fd;
    integer i;
    integer byte_value;
    integer raw_word;
    integer expected_next_k;
    integer active_weight_k;
    integer expect_weight_request;
    integer search_k;
    integer channel_index;
    integer kernel_y;
    integer kernel_x;
    integer input_y;
    integer input_x;
    integer expected_byte_address;
    integer selected_lane;
    integer selected_byte_address;
    integer request_class_now;
    integer forced_class;
    integer forced_error_code;
    integer pending_response;
    reg [31:0] pending_data;
    reg [2:0] pending_error;
    integer accepted_transactions;
    integer feature_read_count;
    integer weight_read_count;
    integer output_write_request_count;
    integer output_write_commit_count;
    integer feature_lane_mask;
    integer weight_lane_mask;
    integer output_lane_mask;
    integer raw_compare_count;
    integer output_write_compare_count;
    integer result_compare_count;
    integer error_result_count;
    integer error_code_mask;
    integer padding_tap_count;
    integer tap_visit_count;
    integer corner_pad_count [0:3];
    integer stalled_request_cycles;
    integer class_transfer_count [0:2];
    integer class_stall_cycles [0:2];
    integer stall_slot_count [0:2][0:4];
    integer result_stall_cycles;
    integer forced_error_responses;
    integer abort_cancel_count;
    integer reset_cancel_count;
    integer output_index;
    integer expected_y;
    integer expected_x;
    integer write_byte;
    integer stall_class;
    integer stall_remaining;
    integer stall_active;
    integer stall_length;
    integer active_stall_class;
    integer active_stall_sequence_index;
    integer active_stall_expected;
    integer active_stall_low_cycles;
    integer request_accepted_since_negedge;
    integer expected_slot_count;
    integer expected_class_stall_cycles;
    integer forced_stall_class;
    integer result_forced_stalls_remaining;
    integer result_stall_index;
    integer watchdog;
    integer saved_commits;
    integer saved_transactions;
    integer saved_result_count;
    reg was_stalled;
    reg stalled_write;
    reg [31:0] stalled_address;
    reg [31:0] stalled_wdata;
    reg [3:0] stalled_rstrb;
    reg [3:0] stalled_wstrb;
    reg was_result_stalled;
    reg [31:0] stalled_result_address;
    reg [7:0] stalled_result_value;
    reg [2:0] stalled_result_error;
    reg [4:0] stalled_result_y;
    reg [4:0] stalled_result_x;
    reg capture_enable;

    function automatic integer frozen_stall_length(input integer slot);
        begin
            case (slot)
                0: frozen_stall_length = 0;
                1: frozen_stall_length = 1;
                2: frozen_stall_length = 2;
                3: frozen_stall_length = 7;
                4: frozen_stall_length = 3;
                default: frozen_stall_length = -1;
            endcase
        end
    endfunction

    always #5 clk = ~clk;

    s2a_conv_layer35_oc0_full dut (
        .clk(clk),
        .hard_reset(hard_reset),
        .abort(abort),
        .buffer_owner_pl(buffer_owner_pl),
        .run_valid(run_valid),
        .run_ready(run_ready),
        .run_busy(run_busy),
        .run_done(run_done),
        .run_cancelled(run_cancelled),
        .run_error_code(run_error_code),
        .result_valid(result_valid),
        .result_ready(result_ready),
        .result_y(result_y),
        .result_x(result_x),
        .result_address(result_address),
        .result_value(result_value),
        .result_error_code(result_error_code),
        .backend_cancel(backend_cancel),
        .backend_req_valid(backend_req_valid),
        .backend_req_ready(backend_req_ready),
        .backend_req_write(backend_req_write),
        .backend_req_addr(backend_req_addr),
        .backend_req_wdata(backend_req_wdata),
        .backend_req_rstrb(backend_req_rstrb),
        .backend_req_wstrb(backend_req_wstrb),
        .backend_rsp_valid(backend_rsp_valid),
        .backend_rsp_rdata(backend_rsp_rdata),
        .backend_rsp_error(backend_rsp_error)
    );

    function automatic integer classify_request;
        integer lane;
        integer byte_addr;
        begin
            lane = -1;
            for (integer n = 0; n < 4; n = n + 1) begin
                if (backend_req_write && backend_req_wstrb[n]) lane = n;
                if (!backend_req_write && backend_req_rstrb[n]) lane = n;
            end
            byte_addr = backend_req_addr + lane;
            if (backend_req_write) classify_request = 3;
            else if ((byte_addr >= WEIGHT_ABSOLUTE_BASE) &&
                     (byte_addr < WEIGHT_ABSOLUTE_BASE + WEIGHT_OC0_BYTES))
                classify_request = 2;
            else classify_request = 1;
        end
    endfunction

    task automatic pulse_run;
        begin
            @(negedge clk);
            if (!run_ready) $fatal(1, "T34 run interface was not ready");
            run_valid = 1'b1;
            @(posedge clk);
            @(negedge clk);
            run_valid = 1'b0;
        end
    endtask

    task automatic wait_terminal(input integer maximum_cycles);
        begin
            watchdog = 0;
            while (run_busy || (!run_done && (run_error_code == 3'd0) &&
                                !run_cancelled)) begin
                @(negedge clk);
                watchdog = watchdog + 1;
                if (watchdog > maximum_cycles)
                    $fatal(1, "T34 run watchdog expired after %0d cycles", maximum_cycles);
            end
        end
    endtask

    task automatic run_memory_error(input integer target_class,
                                    input integer error_code_value);
        begin
            forced_class = target_class;
            forced_error_code = error_code_value;
            saved_commits = output_write_commit_count;
            pulse_run();
            wait_terminal(100000);
            if (run_error_code !== error_code_value[2:0])
                $fatal(1, "T34 memory error mapping mismatch class=%0d expected=%0d got=%0d",
                       target_class, error_code_value, run_error_code);
            if (output_write_commit_count != saved_commits)
                $fatal(1, "T34 memory error caused output side effect class=%0d", target_class);
            forced_class = 0;
            forced_error_code = 0;
        end
    endtask

    task automatic wait_stalled_request(input integer target_class);
        begin
            watchdog = 0;
            while (!(backend_req_valid && !backend_req_ready &&
                     (classify_request() == target_class))) begin
                @(negedge clk);
                watchdog = watchdog + 1;
                if (watchdog > 100000)
                    $fatal(1, "T34 failed to reach held request class=%0d", target_class);
            end
        end
    endtask

    task automatic abort_held_request;
        begin
            @(negedge clk);
            abort = 1'b1;
            @(posedge clk);
            @(negedge clk);
            abort = 1'b0;
            forced_stall_class = 0;
            repeat (3) @(negedge clk);
            if (run_busy || result_valid || pending_response || !run_cancelled)
                $fatal(1, "T34 abort failed to cancel held transaction");
            if (output_write_commit_count != saved_commits)
                $fatal(1, "T34 cancelled request caused an output side effect");
            abort_cancel_count = abort_cancel_count + 1;
        end
    endtask

    task automatic reset_counters_for_grid;
        begin
            accepted_transactions = 0;
            feature_read_count = 0;
            weight_read_count = 0;
            output_write_request_count = 0;
            output_write_commit_count = 0;
            feature_lane_mask = 0;
            weight_lane_mask = 0;
            output_lane_mask = 0;
            raw_compare_count = 0;
            output_write_compare_count = 0;
            result_compare_count = 0;
            error_result_count = 0;
            padding_tap_count = 0;
            tap_visit_count = 0;
            stalled_request_cycles = 0;
            result_stall_cycles = 0;
            active_stall_class = 0;
            active_stall_sequence_index = 0;
            active_stall_expected = 0;
            active_stall_low_cycles = 0;
            request_accepted_since_negedge = 0;
            result_forced_stalls_remaining = 0;
            result_stall_index = -1;
            for (integer c = 0; c < 3; c = c + 1) begin
                class_transfer_count[c] = 0;
                class_stall_cycles[c] = 0;
                for (integer s = 0; s < 5; s = s + 1)
                    stall_slot_count[c][s] = 0;
            end
            for (integer c = 0; c < 4; c = c + 1) corner_pad_count[c] = 0;
            expected_next_k = 0;
            active_weight_k = -1;
            expect_weight_request = 0;
        end
    endtask

    initial begin
        clk = 1'b0;
        hard_reset = 1'b1;
        abort = 1'b0;
        buffer_owner_pl = 1'b1;
        run_valid = 1'b0;
        result_ready = 1'b1;
        backend_req_ready = 1'b0;
        backend_rsp_valid = 1'b0;
        backend_rsp_rdata = 32'd0;
        backend_rsp_error = 3'd0;
        pending_response = 0;
        pending_data = 32'd0;
        pending_error = 3'd0;
        forced_class = 0;
        forced_error_code = 0;
        forced_stall_class = 0;
        capture_enable = 1'b0;
        was_stalled = 1'b0;
        was_result_stalled = 1'b0;
        stall_active = 0;
        stall_remaining = 0;
        stall_class = 0;
        stall_length = 0;
        active_stall_class = 0;
        active_stall_sequence_index = 0;
        active_stall_expected = 0;
        active_stall_low_cycles = 0;
        request_accepted_since_negedge = 0;
        accepted_transactions = 0;
        feature_read_count = 0;
        weight_read_count = 0;
        output_write_request_count = 0;
        output_write_commit_count = 0;
        feature_lane_mask = 0;
        weight_lane_mask = 0;
        output_lane_mask = 0;
        raw_compare_count = 0;
        output_write_compare_count = 0;
        result_compare_count = 0;
        error_result_count = 0;
        error_code_mask = 0;
        padding_tap_count = 0;
        tap_visit_count = 0;
        stalled_request_cycles = 0;
        result_stall_cycles = 0;
        forced_error_responses = 0;
        abort_cancel_count = 0;
        reset_cancel_count = 0;
        result_forced_stalls_remaining = 0;
        result_stall_index = -1;
        for (integer c = 0; c < 3; c = c + 1) begin
            class_transfer_count[c] = 0;
            class_stall_cycles[c] = 0;
            for (integer s = 0; s < 5; s = s + 1)
                stall_slot_count[c][s] = 0;
        end
        expected_next_k = 0;
        active_weight_k = -1;
        expect_weight_request = 0;
        raw_trace_fd = 0;
        output_trace_fd = 0;
        for (i = 0; i < OUTPUT_PIXELS; i = i + 1) output_memory[i] = 8'd0;

        fixture_fd = $fopen("feature_input.bin", "rb");
        if (fixture_fd == 0) $fatal(1, "T34 cannot open feature_input.bin");
        for (i = 0; i < INPUT_BYTES; i = i + 1) begin
            byte_value = $fgetc(fixture_fd);
            if (byte_value < 0) $fatal(1, "T34 truncated feature input fixture");
            feature_memory[i] = byte_value[7:0];
        end
        if ($fgetc(fixture_fd) >= 0) $fatal(1, "T34 feature fixture has extra bytes");
        $fclose(fixture_fd);

        fixture_fd = $fopen("weight_oc0.bin", "rb");
        if (fixture_fd == 0) $fatal(1, "T34 cannot open weight_oc0.bin");
        for (i = 0; i < WEIGHT_OC0_BYTES; i = i + 1) begin
            byte_value = $fgetc(fixture_fd);
            if (byte_value < 0) $fatal(1, "T34 truncated weight fixture");
            weight_oc0[i] = byte_value[7:0];
        end
        if ($fgetc(fixture_fd) >= 0) $fatal(1, "T34 weight fixture has extra bytes");
        $fclose(fixture_fd);

        fixture_fd = $fopen("golden.bin", "rb");
        if (fixture_fd == 0) $fatal(1, "T34 cannot open golden.bin");
        for (i = 0; i < OUTPUT_PIXELS; i = i + 1) begin
            byte_value = $fgetc(fixture_fd);
            if (byte_value < 0) $fatal(1, "T34 truncated raw golden");
            raw_word = byte_value;
            byte_value = $fgetc(fixture_fd);
            if (byte_value < 0) $fatal(1, "T34 truncated raw golden");
            raw_word = raw_word | (byte_value << 8);
            byte_value = $fgetc(fixture_fd);
            if (byte_value < 0) $fatal(1, "T34 truncated raw golden");
            raw_word = raw_word | (byte_value << 16);
            byte_value = $fgetc(fixture_fd);
            if (byte_value < 0) $fatal(1, "T34 truncated raw golden");
            raw_word = raw_word | (byte_value << 24);
            expected_raw[i] = raw_word;
        end
        for (i = 0; i < OUTPUT_PIXELS; i = i + 1) begin
            byte_value = $fgetc(fixture_fd);
            if (byte_value < 0) $fatal(1, "T34 truncated quantized golden");
            expected_quantized[i] = byte_value[7:0];
        end
        if ($fgetc(fixture_fd) >= 0) $fatal(1, "T34 golden fixture has extra bytes");
        $fclose(fixture_fd);

        repeat (4) @(posedge clk);
        @(negedge clk);
        hard_reset = 1'b0;

        run_memory_error(1, 1);
        run_memory_error(2, 2);
        run_memory_error(3, 6);
        if (forced_error_responses != 3 || error_result_count != 3 ||
            error_code_mask != ((1 << 1) | (1 << 2) | (1 << 6)))
            $fatal(1, "T34 memory error coverage was incomplete");

        saved_commits = output_write_commit_count;
        forced_stall_class = 1;
        pulse_run();
        wait_stalled_request(1);
        abort_held_request();

        saved_commits = output_write_commit_count;
        forced_stall_class = 2;
        pulse_run();
        wait_stalled_request(2);
        @(negedge clk);
        hard_reset = 1'b1;
        @(posedge clk);
        @(negedge clk);
        hard_reset = 1'b0;
        forced_stall_class = 0;
        repeat (3) @(negedge clk);
        if (run_busy || result_valid || pending_response || output_write_commit_count != saved_commits)
            $fatal(1, "T34 hard reset did not cancel held read cleanly");
        reset_cancel_count = reset_cancel_count + 1;

        saved_commits = output_write_commit_count;
        forced_stall_class = 3;
        pulse_run();
        wait_stalled_request(3);
        abort_held_request();
        if (output_write_commit_count != 0)
            $fatal(1, "T34 pending output write cancellation had a side effect");

        reset_counters_for_grid();
        for (i = 0; i < OUTPUT_PIXELS; i = i + 1) output_memory[i] = 8'd0;
        raw_trace_fd = $fopen("observed_raw.bin", "wb");
        output_trace_fd = $fopen("observed_output.bin", "wb");
        if ((raw_trace_fd == 0) || (output_trace_fd == 0))
            $fatal(1, "T34 cannot create observed trace files");
        capture_enable = 1'b1;
        pulse_run();
        wait_terminal(30000000);
        capture_enable = 1'b0;
        $fclose(raw_trace_fd);
        $fclose(output_trace_fd);

        if (!run_done || run_error_code != 3'd0 || result_compare_count != OUTPUT_PIXELS ||
            raw_compare_count != OUTPUT_PIXELS || output_write_compare_count != OUTPUT_PIXELS ||
            feature_read_count != VALID_TAPS || weight_read_count != VALID_TAPS ||
            class_transfer_count[0] != VALID_TAPS || class_transfer_count[1] != VALID_TAPS ||
            class_transfer_count[2] != OUTPUT_PIXELS ||
            output_write_request_count != OUTPUT_PIXELS ||
            output_write_commit_count != OUTPUT_PIXELS || tap_visit_count != TOTAL_TAPS ||
            padding_tap_count != PAD_TAPS || feature_lane_mask != 15 ||
            weight_lane_mask != 15 || output_lane_mask != 15 ||
            result_stall_cycles == 0 || forced_error_responses != 3 ||
            error_code_mask != ((1 << 1) | (1 << 2) | (1 << 6)) ||
            abort_cancel_count != 2 || reset_cancel_count != 1)
            $fatal(1, "T34 full-grid count or protocol coverage mismatch");
        expected_class_stall_cycles = 0;
        for (integer c = 0; c < 3; c = c + 1) begin
            expected_class_stall_cycles = 0;
            for (integer s = 0; s < 5; s = s + 1) begin
                expected_slot_count = class_transfer_count[c] / 5;
                if (s < (class_transfer_count[c] % 5))
                    expected_slot_count = expected_slot_count + 1;
                if ((expected_slot_count == 0) ||
                    (stall_slot_count[c][s] != expected_slot_count))
                    $fatal(1, "T34 frozen stall order coverage mismatch class=%0d slot=%0d got=%0d expected=%0d",
                           c + 1, s, stall_slot_count[c][s], expected_slot_count);
                expected_class_stall_cycles = expected_class_stall_cycles +
                    expected_slot_count * frozen_stall_length(s);
            end
            if (class_stall_cycles[c] != expected_class_stall_cycles)
                $fatal(1, "T34 frozen stall cycle count mismatch class=%0d got=%0d expected=%0d",
                       c + 1, class_stall_cycles[c], expected_class_stall_cycles);
        end
        if (stalled_request_cycles !=
            (class_stall_cycles[0] + class_stall_cycles[1] + class_stall_cycles[2]))
            $fatal(1, "T34 total frozen request stall cycles mismatch");
        for (i = 0; i < OUTPUT_PIXELS; i = i + 1) begin
            if (output_memory[i] !== expected_quantized[i])
                $fatal(1, "T34 final output memory mismatch index=%0d", i);
        end
        for (i = 0; i < 4; i = i + 1) begin
            if (corner_pad_count[i] != (384 * 5))
                $fatal(1, "T34 corner padding coverage mismatch corner=%0d count=%0d",
                       i, corner_pad_count[i]);
        end

        $display("PASS T34 pixels=%0d raw=%0d feature_reads=%0d weight_reads=%0d output_writes=%0d padding=%0d taps=%0d feature_lanes=%0x weight_lanes=%0x output_lanes=%0x corners=%0d,%0d,%0d,%0d error_mask=%0x fault_responses=%0d request_stalls=%0d feature_transfers=%0d feature_stall_cycles=%0d feature_slot0=%0d feature_slot1=%0d feature_slot2=%0d feature_slot3=%0d feature_slot4=%0d weight_transfers=%0d weight_stall_cycles=%0d weight_slot0=%0d weight_slot1=%0d weight_slot2=%0d weight_slot3=%0d weight_slot4=%0d output_transfers=%0d output_stall_cycles=%0d output_slot0=%0d output_slot1=%0d output_slot2=%0d output_slot3=%0d output_slot4=%0d result_stalls=%0d abort_cancels=%0d reset_cancels=%0d",
                 result_compare_count, raw_compare_count, feature_read_count, weight_read_count,
                 output_write_commit_count, padding_tap_count, tap_visit_count,
                 feature_lane_mask, weight_lane_mask, output_lane_mask,
                 corner_pad_count[0], corner_pad_count[1], corner_pad_count[2], corner_pad_count[3],
                 error_code_mask, forced_error_responses, stalled_request_cycles,
                 class_transfer_count[0], class_stall_cycles[0],
                 stall_slot_count[0][0], stall_slot_count[0][1], stall_slot_count[0][2],
                 stall_slot_count[0][3], stall_slot_count[0][4],
                 class_transfer_count[1], class_stall_cycles[1],
                 stall_slot_count[1][0], stall_slot_count[1][1], stall_slot_count[1][2],
                 stall_slot_count[1][3], stall_slot_count[1][4],
                 class_transfer_count[2], class_stall_cycles[2],
                 stall_slot_count[2][0], stall_slot_count[2][1], stall_slot_count[2][2],
                 stall_slot_count[2][3], stall_slot_count[2][4], result_stall_cycles,
                 abort_cancel_count, reset_cancel_count);
        $finish;
    end

    always @(negedge clk) begin
        if (hard_reset || abort || !backend_req_valid) begin
            backend_req_ready = 1'b0;
            stall_active = 0;
            stall_remaining = 0;
            active_stall_low_cycles = 0;
            request_accepted_since_negedge = 0;
        end else begin
            request_class_now = classify_request();
            if (forced_stall_class == request_class_now) begin
                backend_req_ready = 1'b0;
                stall_active = 1;
                stall_class = request_class_now;
            end else if (!stall_active || (stall_class != request_class_now) ||
                         request_accepted_since_negedge) begin
                request_accepted_since_negedge = 0;
                if (capture_enable && (request_class_now >= 1) && (request_class_now <= 3)) begin
                    stall_class = request_class_now;
                    active_stall_class = request_class_now;
                    active_stall_sequence_index = class_transfer_count[request_class_now - 1] % 5;
                    active_stall_expected = frozen_stall_length(active_stall_sequence_index);
                    active_stall_low_cycles = 0;
                    stall_length = active_stall_expected;
                    if (stall_length < 0)
                        $fatal(1, "T34 frozen stall sequence index invalid");
                    if (stall_length > 0) begin
                        stall_active = 1;
                        stall_remaining = stall_length;
                        backend_req_ready = 1'b0;
                    end else begin
                        stall_active = 0;
                        stall_remaining = 0;
                        backend_req_ready = 1'b1;
                    end
                end else begin
                    stall_active = 0;
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

        if (capture_enable && result_valid) begin
            if (result_forced_stalls_remaining > 0) begin
                result_ready = 1'b0;
                result_forced_stalls_remaining = result_forced_stalls_remaining - 1;
                result_stall_cycles = result_stall_cycles + 1;
            end else if ((result_compare_count % 19) == 0 &&
                         result_stall_index != result_compare_count) begin
                result_forced_stalls_remaining = 2;
                result_stall_index = result_compare_count;
                result_ready = 1'b0;
                result_stall_cycles = result_stall_cycles + 1;
            end else begin
                result_ready = 1'b1;
            end
        end else begin
            result_ready = 1'b1;
        end
    end

    always @(posedge clk) begin
        if (hard_reset || backend_cancel) begin
            backend_rsp_valid <= 1'b0;
            backend_rsp_rdata <= 32'd0;
            backend_rsp_error <= 3'd0;
            pending_response <= 0;
            pending_data <= 32'd0;
            pending_error <= 3'd0;
            was_stalled <= 1'b0;
            was_result_stalled <= 1'b0;
        end else begin
            backend_rsp_valid <= 1'b0;
            backend_rsp_error <= 3'd0;

            if (was_stalled && (!backend_req_valid || backend_req_write !== stalled_write ||
                backend_req_addr !== stalled_address || backend_req_wdata !== stalled_wdata ||
                backend_req_rstrb !== stalled_rstrb || backend_req_wstrb !== stalled_wstrb))
                $fatal(1, "T34 request changed before single-outstanding handshake");
            was_stalled <= backend_req_valid && !backend_req_ready;
            if (backend_req_valid && !backend_req_ready) begin
                stalled_write <= backend_req_write;
                stalled_address <= backend_req_addr;
                stalled_wdata <= backend_req_wdata;
                stalled_rstrb <= backend_req_rstrb;
                stalled_wstrb <= backend_req_wstrb;
                if (capture_enable) begin
                    request_class_now = classify_request();
                    if ((request_class_now < 1) || (request_class_now > 3) ||
                        (active_stall_class != request_class_now))
                        $fatal(1, "T34 frozen stall class changed while request held");
                    active_stall_low_cycles = active_stall_low_cycles + 1;
                    stalled_request_cycles = stalled_request_cycles + 1;
                    class_stall_cycles[request_class_now - 1] =
                        class_stall_cycles[request_class_now - 1] + 1;
                end
            end
            if (pending_response && backend_req_valid && backend_req_ready)
                $fatal(1, "T34 accepted an overlapping memory request");

            if (pending_response) begin
                backend_rsp_valid <= 1'b1;
                backend_rsp_rdata <= pending_data;
                backend_rsp_error <= pending_error;
                pending_response <= 0;
            end

            if (backend_req_valid && backend_req_ready) begin
                if (pending_response) $fatal(1, "T34 backend has multiple outstanding responses");
                if (backend_req_addr[1:0] != 2'b00)
                    $fatal(1, "T34 unaligned memory word address");
                selected_lane = -1;
                for (i = 0; i < 4; i = i + 1) begin
                    if (!backend_req_write && backend_req_rstrb[i]) selected_lane = i;
                    if (backend_req_write && backend_req_wstrb[i]) selected_lane = i;
                end
                if ((selected_lane < 0) ||
                    (!backend_req_write &&
                     ((backend_req_rstrb != (4'b0001 << selected_lane)) || backend_req_wstrb != 0)) ||
                    (backend_req_write &&
                     ((backend_req_wstrb != (4'b0001 << selected_lane)) || backend_req_rstrb != 0)))
                    $fatal(1, "T34 invalid byte strobe");

                selected_byte_address = backend_req_addr + selected_lane;
                request_class_now = classify_request();
                if (capture_enable) begin
                    if ((request_class_now < 1) || (request_class_now > 3) ||
                        (active_stall_class != request_class_now) ||
                        (active_stall_sequence_index !=
                         (class_transfer_count[request_class_now - 1] % 5)) ||
                        (active_stall_low_cycles != active_stall_expected))
                        $fatal(1, "T34 frozen stall handshake mismatch class=%0d low=%0d expected=%0d",
                               request_class_now, active_stall_low_cycles,
                               active_stall_expected);
                    stall_slot_count[request_class_now - 1][active_stall_sequence_index] =
                        stall_slot_count[request_class_now - 1][active_stall_sequence_index] + 1;
                    class_transfer_count[request_class_now - 1] =
                        class_transfer_count[request_class_now - 1] + 1;
                end
                request_accepted_since_negedge = 1;
                pending_error = 3'd0;
                pending_data = 32'd0;
                if (forced_class == request_class_now) begin
                    pending_error = forced_error_code[2:0];
                    forced_error_responses = forced_error_responses + 1;
                end else if (request_class_now == 1) begin
                    if ((selected_byte_address < INPUT_BASE) ||
                        (selected_byte_address >= INPUT_BASE + INPUT_BYTES))
                        $fatal(1, "T34 feature byte escaped layer34 tensor");
                    search_k = expected_next_k;
                    expected_byte_address = -1;
                    while ((search_k < REDUCTION) && (expected_byte_address < 0)) begin
                        channel_index = search_k / 9;
                        kernel_y = (search_k % 9) / 3;
                        kernel_x = search_k % 3;
                        input_y = result_y + kernel_y - 1;
                        input_x = result_x + kernel_x - 1;
                        if ((input_y >= 0) && (input_y < 26) &&
                            (input_x >= 0) && (input_x < 26))
                            expected_byte_address = INPUT_BASE + channel_index * CHANNEL_BYTES +
                                                    input_y * 26 + input_x;
                        else search_k = search_k + 1;
                    end
                    if ((expected_byte_address < 0) || (search_k >= REDUCTION) ||
                        (selected_byte_address != expected_byte_address) ||
                        (dut.u_engine.reduction_index != search_k))
                        $fatal(1, "T34 feature address/order mismatch y=%0d x=%0d k=%0d addr=%0d expected=%0d",
                               result_y, result_x, search_k, selected_byte_address,
                               expected_byte_address);
                    if (backend_req_rstrb != (4'b0001 << (expected_byte_address & 3)) ||
                        backend_req_addr != (expected_byte_address & 32'hffff_fffc))
                        $fatal(1, "T34 feature byte lane/address mismatch");
                    active_weight_k = search_k;
                    expect_weight_request = 1;
                    if (pending_error == 0) begin
                        pending_data = {24'd0, feature_memory[expected_byte_address - INPUT_BASE]} <<
                                       (selected_lane * 8);
                    end
                    feature_read_count = feature_read_count + 1;
                    if (capture_enable) feature_lane_mask = feature_lane_mask | backend_req_rstrb;
                end else if (request_class_now == 2) begin
                    if (!expect_weight_request || (active_weight_k < 0) ||
                        (selected_byte_address != WEIGHT_ABSOLUTE_BASE + active_weight_k) ||
                        (dut.u_engine.reduction_index != active_weight_k))
                        $fatal(1, "T34 weight address/order mismatch y=%0d x=%0d k=%0d addr=%0d",
                               result_y, result_x, active_weight_k, selected_byte_address);
                    if (backend_req_rstrb != (4'b0001 << (selected_byte_address & 3)) ||
                        backend_req_addr != (selected_byte_address & 32'hffff_fffc))
                        $fatal(1, "T34 weight byte lane/address mismatch");
                    if (pending_error == 0) begin
                        pending_data = {24'd0, weight_oc0[active_weight_k]} << (selected_lane * 8);
                    end
                    weight_read_count = weight_read_count + 1;
                    if (capture_enable) weight_lane_mask = weight_lane_mask | backend_req_rstrb;
                    expected_next_k = active_weight_k + 1;
                    expect_weight_request = 0;
                end else begin
                    output_index = result_y * OUTPUT_WIDTH + result_x;
                    if ((output_index < 0) || (output_index >= OUTPUT_PIXELS) ||
                        (selected_byte_address != OUTPUT_BASE + output_index) ||
                        (backend_req_addr != ((OUTPUT_BASE + output_index) & 32'hffff_fffc)) ||
                        (backend_req_wstrb != (4'b0001 << ((OUTPUT_BASE + output_index) & 3))) ||
                        (backend_req_rstrb != 0))
                        $fatal(1, "T34 output address/strobe/order mismatch y=%0d x=%0d addr=%0d",
                               result_y, result_x, selected_byte_address);
                    write_byte = (backend_req_wdata >> (selected_lane * 8)) & 255;
                    if (write_byte != expected_quantized[output_index])
                        $fatal(1, "T34 output quantized value mismatch index=%0d", output_index);
                    output_write_request_count = output_write_request_count + 1;
                    if (capture_enable) output_lane_mask = output_lane_mask | backend_req_wstrb;
                    if (pending_error == 0) begin
                        output_memory[output_index] = write_byte[7:0];
                        output_write_commit_count = output_write_commit_count + 1;
                        if (capture_enable) begin
                            output_write_compare_count = output_write_compare_count + 1;
                            $fwrite(output_trace_fd, "%c", write_byte[7:0]);
                        end
                    end
                end
                if (request_class_now == 3) pending_data = 32'd0;
                pending_response = 1;
                accepted_transactions = accepted_transactions + 1;
            end

            if (run_valid && run_ready) begin
                expected_next_k = 0;
                active_weight_k = -1;
                expect_weight_request = 0;
            end

            if (capture_enable && run_busy && (dut.u_engine.state == 4'd3)) begin
                tap_visit_count = tap_visit_count + 1;
                if (dut.u_engine.geometry_tap_is_padding) begin
                    padding_tap_count = padding_tap_count + 1;
                    if ((result_y == 0) && (result_x == 0)) corner_pad_count[0] = corner_pad_count[0] + 1;
                    if ((result_y == 0) && (result_x == 25)) corner_pad_count[1] = corner_pad_count[1] + 1;
                    if ((result_y == 25) && (result_x == 0)) corner_pad_count[2] = corner_pad_count[2] + 1;
                    if ((result_y == 25) && (result_x == 25)) corner_pad_count[3] = corner_pad_count[3] + 1;
                end
            end

            if (capture_enable && dut.u_engine.mac_result_valid &&
                dut.u_engine.mac_result_ready) begin
                output_index = raw_compare_count;
                if (output_index >= OUTPUT_PIXELS)
                    $fatal(1, "T34 received excess raw accumulators");
                expected_y = output_index / OUTPUT_WIDTH;
                expected_x = output_index % OUTPUT_WIDTH;
                if ((result_y != expected_y) || (result_x != expected_x) ||
                    (dut.u_engine.mac_result_data !== expected_raw[output_index]))
                    $fatal(1, "T34 raw INT32 mismatch index=%0d y=%0d x=%0d got=%0d expected=%0d",
                           output_index, result_y, result_x,
                           dut.u_engine.mac_result_data, expected_raw[output_index]);
                raw_word = dut.u_engine.mac_result_data;
                $fwrite(raw_trace_fd, "%c%c%c%c", raw_word[7:0], raw_word[15:8],
                        raw_word[23:16], raw_word[31:24]);
                raw_compare_count = raw_compare_count + 1;
            end

            if (was_result_stalled && (!result_valid ||
                result_address !== stalled_result_address || result_value !== stalled_result_value ||
                result_error_code !== stalled_result_error || result_y !== stalled_result_y ||
                result_x !== stalled_result_x))
                $fatal(1, "T34 result interface changed under backpressure");
            was_result_stalled <= result_valid && !result_ready;
            if (result_valid && !result_ready) begin
                stalled_result_address <= result_address;
                stalled_result_value <= result_value;
                stalled_result_error <= result_error_code;
                stalled_result_y <= result_y;
                stalled_result_x <= result_x;
            end

            if (result_valid && result_ready) begin
                if (result_error_code != 3'd0) begin
                    error_result_count = error_result_count + 1;
                    error_code_mask = error_code_mask | (1 << result_error_code);
                end else if (capture_enable) begin
                    output_index = result_compare_count;
                    expected_y = output_index / OUTPUT_WIDTH;
                    expected_x = output_index % OUTPUT_WIDTH;
                    if ((output_index >= OUTPUT_PIXELS) || (result_y != expected_y) ||
                        (result_x != expected_x) ||
                        (result_address != OUTPUT_BASE + output_index) ||
                        (result_value !== expected_quantized[output_index]) ||
                        (output_memory[output_index] !== expected_quantized[output_index]))
                        $fatal(1, "T34 result/address/order mismatch index=%0d", output_index);
                    result_compare_count = result_compare_count + 1;
                    expected_next_k = 0;
                    active_weight_k = -1;
                    expect_weight_request = 0;
                    if ((result_compare_count % OUTPUT_WIDTH) == 0)
                        $display("PROGRESS T34 row=%0d/%0d outputs=%0d/%0d",
                                 result_compare_count / OUTPUT_WIDTH - 1,
                                 OUTPUT_WIDTH - 1, result_compare_count, OUTPUT_PIXELS);
                end
            end
        end
    end
endmodule
