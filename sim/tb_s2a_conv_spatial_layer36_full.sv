`timescale 1ns/1ps

module tb_s2a_conv_spatial_layer36_full;
    localparam integer INPUT_BYTES = 173056;
    localparam integer K_COUNT = 256;
    localparam integer PIXEL_COUNT = 676;
    localparam integer HEIGHT = 26;
    localparam integer WIDTH = 26;
    localparam integer OUTPUT_CHANNELS = 30;
    localparam integer WEIGHT_BYTES = 7680;
    localparam integer OUTPUT_BYTES = 20280;
    localparam integer EXPECTED_FEATURE_READS = OUTPUT_CHANNELS * HEIGHT * K_COUNT * 7;
    localparam integer EXPECTED_FEATURE_BYTES = OUTPUT_CHANNELS * HEIGHT * K_COUNT * WIDTH;
    localparam integer EXPECTED_WEIGHT_READS = OUTPUT_CHANNELS * HEIGHT * 2 * K_COUNT;
    localparam integer EXPECTED_OUTPUT_WRITES = OUTPUT_CHANNELS * PIXEL_COUNT;
    localparam integer EXPECTED_MEMORY_REQUESTS = EXPECTED_FEATURE_READS +
        EXPECTED_WEIGHT_READS + EXPECTED_OUTPUT_WRITES;
    localparam logic [31:0] FEATURE_BASE = 32'd27966080;
    localparam logic [31:0] WEIGHT_BYTE_BASE = 32'h00100000 + 32'd5895420;
    localparam logic [31:0] OUTPUT_BASE = 32'd28139136;

    logic clk = 1'b0;
    logic rst = 1'b1;
    logic abort = 1'b0;
    logic start_valid = 1'b0;
    logic start_ready;
    logic busy;
    logic mem_valid;
    logic mem_ready = 1'b0;
    logic mem_write;
    logic [31:0] mem_addr;
    logic [31:0] mem_wdata;
    logic [3:0] mem_rstrb;
    logic [3:0] mem_wstrb;
    logic [31:0] mem_rdata = 32'd0;
    logic [2:0] mem_error_code = 3'd0;
    logic raw_valid;
    logic raw_ready = 1'b0;
    logic [4:0] raw_output_channel;
    logic [4:0] raw_y;
    logic [4:0] raw_x;
    logic signed [31:0] raw_accumulator;
    logic result_valid;
    logic result_ready = 1'b0;
    logic [2:0] result_error_code;

    logic [7:0] input_fixture [0:INPUT_BYTES-1];
    logic [7:0] layer36_weights [0:WEIGHT_BYTES-1];
    logic signed [31:0] expected_raw [0:OUTPUT_BYTES-1];
    logic [7:0] expected_golden [0:OUTPUT_BYTES-1];
    logic signed [31:0] expected_bias [0:OUTPUT_CHANNELS-1];
    logic [37:0] expected_mq [0:OUTPUT_CHANNELS-1];
    logic [1:0] expected_activation [0:OUTPUT_CHANNELS-1];
    logic [7:0] output_memory [0:OUTPUT_BYTES-1];
    integer input_seen_count [0:INPUT_BYTES-1];
    logic [OUTPUT_CHANNELS-1:0] input_seen_by_channel [0:INPUT_BYTES-1];
    integer weight_seen_count [0:WEIGHT_BYTES-1];
    logic output_seen [0:OUTPUT_BYTES-1];
    logic raw_seen [0:OUTPUT_BYTES-1];

    logic hold_all = 1'b0;
    logic score_enable = 1'b0;
    integer fault_mode = 0;
    integer fault_code = 0;
    integer fault_seen = 0;
    integer pass_requests = 0;
    integer pass_feature_requests = 0;
    integer pass_weight_requests = 0;
    integer pass_output_writes = 0;
    integer feature_selected_bytes = 0;
    integer weight_selected_bytes = 0;
    integer output_write_count = 0;
    integer raw_compare_count = 0;
    integer parameter_check_count = 0;
    integer stall_cycles = 0;
    integer current_success_runs = 0;
    integer error_codes_seen = 0;
    integer abort_pending_cancel_count = 0;
    integer reset_pending_cancel_count = 0;
    integer output_abort_cancel_count = 0;
    integer output_reset_cancel_count = 0;
    integer output_cancel_write_handshakes = 0;
    integer recovery_runs = 0;
    logic output_cancel_armed = 1'b0;
    integer lfsr = 32'h20260927;
    integer raw_lfsr = 32'h4d595df4;
    integer seq_lane;
    integer idx;
    integer lane;
    integer byte_offset;
    integer expected_index;
    integer feature_k;
    integer feature_row;
    integer feature_x;
    integer timeout_cycles;
    logic previous_mem_stall = 1'b0;
    logic previous_mem_write;
    logic [31:0] previous_mem_addr;
    logic [31:0] previous_mem_wdata;
    logic [3:0] previous_mem_rstrb;
    logic [3:0] previous_mem_wstrb;
    logic previous_raw_stall = 1'b0;
    logic [4:0] previous_raw_output_channel;
    logic [4:0] previous_raw_y;
    logic [4:0] previous_raw_x;
    logic signed [31:0] previous_raw_accumulator;
    logic [31:0] read_byte_address;
    logic active_feature_request;
    logic active_weight_request;
    logic inject_now;

    always #5 clk = ~clk;

    s2a_conv_spatial_layer36_full dut (
        .clk(clk),
        .rst(rst),
        .abort(abort),
        .start_valid(start_valid),
        .start_ready(start_ready),
        .busy(busy),
        .mem_valid(mem_valid),
        .mem_ready(mem_ready),
        .mem_write(mem_write),
        .mem_addr(mem_addr),
        .mem_wdata(mem_wdata),
        .mem_rstrb(mem_rstrb),
        .mem_wstrb(mem_wstrb),
        .mem_rdata(mem_rdata),
        .mem_error_code(mem_error_code),
        .raw_valid(raw_valid),
        .raw_ready(raw_ready),
        .raw_output_channel(raw_output_channel),
        .raw_y(raw_y),
        .raw_x(raw_x),
        .raw_accumulator(raw_accumulator),
        .result_valid(result_valid),
        .result_ready(result_ready),
        .result_error_code(result_error_code)
    );

    task automatic clear_pass_counts;
        begin
            pass_requests = 0;
            pass_feature_requests = 0;
            pass_weight_requests = 0;
            pass_output_writes = 0;
            feature_selected_bytes = 0;
            weight_selected_bytes = 0;
            output_write_count = 0;
            raw_compare_count = 0;
            parameter_check_count = 0;
            fault_seen = 0;
        end
    endtask

    task automatic clear_scoreboards;
        begin
            for (idx = 0; idx < INPUT_BYTES; idx = idx + 1) begin
                input_seen_count[idx] = 0;
                input_seen_by_channel[idx] = '0;
            end
            for (idx = 0; idx < WEIGHT_BYTES; idx = idx + 1) begin
                weight_seen_count[idx] = 0;
            end
            for (idx = 0; idx < OUTPUT_BYTES; idx = idx + 1) begin
                output_seen[idx] = 1'b0;
                raw_seen[idx] = 1'b0;
                output_memory[idx] = 8'd0;
            end
        end
    endtask

    task automatic start_operation;
        begin
            @(negedge clk);
            start_valid = 1'b1;
            do begin
                @(posedge clk);
            end while (!start_ready);
            @(negedge clk);
            start_valid = 1'b0;
        end
    endtask

    task automatic wait_for_result(input integer expected_error);
        begin
            timeout_cycles = 0;
            while (!result_valid && (timeout_cycles < 50000000)) begin
                @(negedge clk);
                timeout_cycles = timeout_cycles + 1;
            end
            if (!result_valid) begin
                $fatal(1, "transaction did not complete within testbench watchdog");
            end
            if (result_error_code !== expected_error[2:0]) begin
                $fatal(1, "result error mismatch got=%0d expected=%0d",
                       result_error_code, expected_error);
            end
            result_ready = 1'b1;
            @(posedge clk);
            @(negedge clk);
            result_ready = 1'b0;
        end
    endtask

    task automatic run_error_case(
        input integer selected_mode,
        input integer selected_code,
        input integer expected_error
    );
        begin
            clear_pass_counts();
            fault_mode = selected_mode;
            fault_code = selected_code;
            start_operation();
            wait_for_result(expected_error);
            if (!fault_seen) begin
                $fatal(1, "directed memory error was not injected");
            end
            repeat (4) begin
                @(negedge clk);
                if (mem_valid || raw_valid) begin
                    $fatal(1, "side effect remained after memory error result");
                end
            end
            fault_mode = 0;
            fault_code = 0;
            error_codes_seen = error_codes_seen | (1 << selected_code);
        end
    endtask

    task automatic cancel_pending_request(input logic use_reset);
        logic [31:0] held_addr;
        logic [31:0] held_wdata;
        logic [3:0] held_rstrb;
        logic [3:0] held_wstrb;
        logic held_write;
        begin
            clear_pass_counts();
            fault_mode = 0;
            hold_all = 1'b1;
            start_operation();
            timeout_cycles = 0;
            while (!mem_valid && (timeout_cycles < 2000)) begin
                @(negedge clk);
                timeout_cycles = timeout_cycles + 1;
            end
            if (!mem_valid || mem_ready) begin
                $fatal(1, "failed to hold a pending memory request");
            end
            held_addr = mem_addr;
            held_wdata = mem_wdata;
            held_rstrb = mem_rstrb;
            held_wstrb = mem_wstrb;
            held_write = mem_write;
            repeat (2) begin
                @(negedge clk);
                if (!mem_valid || mem_ready || mem_addr !== held_addr ||
                    mem_wdata !== held_wdata || mem_rstrb !== held_rstrb ||
                    mem_wstrb !== held_wstrb || mem_write !== held_write) begin
                    $fatal(1, "pending request changed while held");
                end
            end
            if (use_reset) begin
                rst = 1'b1;
                reset_pending_cancel_count = reset_pending_cancel_count + 1;
            end else begin
                abort = 1'b1;
                abort_pending_cancel_count = abort_pending_cancel_count + 1;
            end
            #1;
            if (mem_valid) begin
                $fatal(1, "reset/abort did not cancel pending request");
            end
            @(posedge clk);
            @(negedge clk);
            rst = 1'b0;
            abort = 1'b0;
            hold_all = 1'b0;
            repeat (3) begin
                @(negedge clk);
                if (mem_valid || result_valid) begin
                    $fatal(1, "canceled request caused a delayed side effect");
                end
            end
            if (pass_requests != 0 || pass_output_writes != 0) begin
                $fatal(1, "canceled request was accepted unexpectedly");
            end
        end
    endtask

    task automatic cancel_pending_output_write(input logic use_reset);
        logic [31:0] held_addr;
        logic [31:0] held_wdata;
        logic [3:0] held_rstrb;
        logic [3:0] held_wstrb;
        logic held_write;
        integer accepted_requests_before_cancel;
        begin
            clear_pass_counts();
            fault_mode = 0;
            score_enable = 1'b0;
            hold_all = 1'b0;
            output_cancel_write_handshakes = 0;
            output_cancel_armed = 1'b1;
            start_operation();
            timeout_cycles = 0;
            while (!(mem_valid && mem_write) && (timeout_cycles < 200000)) begin
                @(negedge clk);
                timeout_cycles = timeout_cycles + 1;
            end
            if (!mem_valid || !mem_write) begin
                $fatal(1, "timed out waiting for pending output write");
            end
            hold_all = 1'b1;
            mem_ready = 1'b0;
            #1;
            if (!mem_valid || !mem_write || mem_ready) begin
                $fatal(1, "failed to stall a pending output write");
            end
            held_addr = mem_addr;
            held_wdata = mem_wdata;
            held_rstrb = mem_rstrb;
            held_wstrb = mem_wstrb;
            held_write = mem_write;
            if ((held_addr != OUTPUT_BASE) || (held_wstrb != 4'b0001) ||
                (held_rstrb != 4'b0000) ||
                (held_wdata[7:0] != expected_golden[0]) ||
                (held_wdata[31:8] != 24'd0)) begin
                $fatal(1, "first pending output request fields/data are incorrect");
            end
            repeat (2) begin
                @(negedge clk);
                if (!mem_valid || !mem_write || mem_ready ||
                    mem_addr !== held_addr || mem_wdata !== held_wdata ||
                    mem_rstrb !== held_rstrb || mem_wstrb !== held_wstrb ||
                    mem_write !== held_write) begin
                    $fatal(1, "pending output write changed while stalled");
                end
            end
            accepted_requests_before_cancel = pass_requests;
            if (pass_output_writes != 0 || output_cancel_write_handshakes != 0) begin
                $fatal(1, "output write handshook before cancellation");
            end
            if (use_reset) begin
                rst = 1'b1;
                output_reset_cancel_count = output_reset_cancel_count + 1;
            end else begin
                abort = 1'b1;
                output_abort_cancel_count = output_abort_cancel_count + 1;
            end
            #1;
            if (mem_valid) begin
                $fatal(1, "reset/abort did not cancel pending output write");
            end
            @(posedge clk);
            @(negedge clk);
            rst = 1'b0;
            abort = 1'b0;
            hold_all = 1'b0;
            repeat (3) begin
                @(negedge clk);
                if (mem_valid || result_valid) begin
                    $fatal(1, "canceled output write caused delayed side effect");
                end
            end
            if (pass_requests != accepted_requests_before_cancel ||
                pass_output_writes != 0 || output_cancel_write_handshakes != 0) begin
                $fatal(1, "canceled output write caused a handshake or memory side effect");
            end
            output_cancel_armed = 1'b0;
        end
    endtask

    always @(negedge clk) begin
        lfsr = (lfsr >> 1) ^ ((-(lfsr & 1)) & 32'hD0000001);
        raw_lfsr = (raw_lfsr >> 1) ^ ((-(raw_lfsr & 1)) & 32'hA3000001);
        if (hold_all) begin
            mem_ready = 1'b0;
        end else begin
            mem_ready = (lfsr[1:0] != 2'b00);
        end
        raw_ready = raw_lfsr[1] | raw_lfsr[5];
        mem_rdata = 32'd0;
        mem_error_code = 3'd0;
        inject_now = 1'b0;
        if (mem_valid && mem_ready && !mem_write && (fault_mode == 1) &&
            (pass_requests == 0)) begin
            inject_now = 1'b1;
        end else if (mem_valid && mem_ready && !mem_write && (fault_mode == 2) &&
                     (dut.state == dut.ST_WEIGHT_READ) &&
                     (dut.output_channel == 5'd1) && (dut.row_y == 5'd0) &&
                     !dut.tile_index && (dut.k_index == 8'd0)) begin
            inject_now = 1'b1;
        end else if (mem_valid && mem_ready && mem_write && (fault_mode == 3) &&
                     (dut.output_channel == 5'd0) && (dut.row_y == 5'd25) &&
                     dut.tile_index && (dut.lane_index == 4'd9)) begin
            inject_now = 1'b1;
        end
        if (inject_now) begin
            mem_error_code = fault_code[2:0];
        end
        if (mem_valid && !mem_write) begin
            for (lane = 0; lane < 4; lane = lane + 1) begin
                if (mem_rstrb[lane]) begin
                    read_byte_address = mem_addr + lane;
                    if ((read_byte_address >= FEATURE_BASE) &&
                        (read_byte_address < (FEATURE_BASE + INPUT_BYTES))) begin
                        mem_rdata[lane * 8 +: 8] =
                            input_fixture[read_byte_address - FEATURE_BASE];
                    end else if ((read_byte_address >= WEIGHT_BYTE_BASE) &&
                                 (read_byte_address < (WEIGHT_BYTE_BASE + WEIGHT_BYTES))) begin
                        mem_rdata[lane * 8 +: 8] =
                            layer36_weights[read_byte_address - WEIGHT_BYTE_BASE];
                    end
                end
            end
        end
    end

    always @(posedge clk) begin
        if (rst || abort) begin
            previous_mem_stall <= 1'b0;
            previous_raw_stall <= 1'b0;
        end else begin
            if (output_cancel_armed && mem_valid && mem_ready && mem_write) begin
                output_cancel_write_handshakes = output_cancel_write_handshakes + 1;
            end
            if (previous_mem_stall &&
                (!mem_valid || (mem_write !== previous_mem_write) ||
                 (mem_addr !== previous_mem_addr) || (mem_wdata !== previous_mem_wdata) ||
                 (mem_rstrb !== previous_mem_rstrb) || (mem_wstrb !== previous_mem_wstrb))) begin
                $fatal(1, "memory request fields changed while stalled");
            end
            previous_mem_stall <= mem_valid && !mem_ready;
            if (mem_valid && !mem_ready) begin
                previous_mem_write <= mem_write;
                previous_mem_addr <= mem_addr;
                previous_mem_wdata <= mem_wdata;
                previous_mem_rstrb <= mem_rstrb;
                previous_mem_wstrb <= mem_wstrb;
                stall_cycles <= stall_cycles + 1;
            end

            if (previous_raw_stall &&
                (!raw_valid || (raw_output_channel !== previous_raw_output_channel) ||
                 (raw_y !== previous_raw_y) ||
                 (raw_x !== previous_raw_x) ||
                 (raw_accumulator !== previous_raw_accumulator))) begin
                $fatal(1, "raw accumulator fields changed while stalled");
            end
            previous_raw_stall <= raw_valid && !raw_ready;
            if (raw_valid && !raw_ready) begin
                previous_raw_output_channel <= raw_output_channel;
                previous_raw_y <= raw_y;
                previous_raw_x <= raw_x;
                previous_raw_accumulator <= raw_accumulator;
            end

            if (raw_valid && raw_ready && score_enable) begin
                expected_index = raw_output_channel * PIXEL_COUNT + raw_y * 26 + raw_x;
                if ((raw_output_channel > 29) || (raw_y > 25) || (raw_x > 25) || (expected_index < 0) ||
                    (expected_index >= OUTPUT_BYTES)) begin
                    $fatal(1, "raw stream emitted out-of-range lane oc=%0d y=%0d x=%0d",
                           raw_output_channel, raw_y, raw_x);
                end
                if (expected_index != raw_compare_count) begin
                    $fatal(1, "raw stream order mismatch got_index=%0d expected_index=%0d",
                           expected_index, raw_compare_count);
                end
                if (raw_seen[expected_index]) begin
                    $fatal(1, "raw stream duplicated lane oc=%0d y=%0d x=%0d", raw_output_channel, raw_y, raw_x);
                end
                raw_seen[expected_index] = 1'b1;
                if (raw_accumulator !== expected_raw[expected_index]) begin
                    $fatal(1, "raw mismatch oc=%0d y=%0d x=%0d got=%0d expected=%0d",
                           raw_output_channel, raw_y, raw_x, raw_accumulator, expected_raw[expected_index]);
                end
                raw_compare_count = raw_compare_count + 1;
            end

            if (score_enable && dut.core_start_valid && dut.core_start_ready) begin
                if ((dut.selected_bias !== expected_bias[dut.output_channel]) ||
                    (dut.active_mq !== expected_mq[dut.output_channel]) ||
                    (dut.active_activation !== expected_activation[dut.output_channel]) ||
                    (dut.active_activation !== 2'b00)) begin
                    $fatal(1, "per-channel parameter mismatch oc=%0d bias=%0d mq=%h activation=%b",
                           dut.output_channel, dut.selected_bias, dut.active_mq,
                           dut.active_activation);
                end
                if (dut.tile_lane_mask !== (dut.tile_index ? 16'h03ff : 16'hffff)) begin
                    $fatal(1, "tile valid-lane mask mismatch oc=%0d y=%0d tile=%0d mask=%h",
                           dut.output_channel, dut.row_y, dut.tile_index,
                           dut.tile_lane_mask);
                end
                parameter_check_count = parameter_check_count + 1;
            end

            if (score_enable && dut.core_input_valid && dut.core_input_ready) begin
                for (lane = 0; lane < 16; lane = lane + 1) begin
                    if ((!dut.tile_index || (lane < 10)) &&
                        (dut.feature_lanes[lane * 8 +: 8] !== input_fixture[
                            (dut.k_index * 676) + (dut.row_y * 26) +
                            (dut.tile_index ? 16 : 0) + lane])) begin
                        $fatal(1, "feature lane mismatch y=%0d tile=%0d k=%0d lane=%0d got=%02x expected=%02x",
                               dut.row_y, dut.tile_index, dut.k_index, lane,
                               dut.feature_lanes[lane * 8 +: 8],
                               input_fixture[(dut.k_index * 676) + (dut.row_y * 26) +
                                             (dut.tile_index ? 16 : 0) + lane]);
                    end
                    if (dut.tile_index && (lane >= 10) &&
                        (dut.feature_lanes[lane * 8 +: 8] !== 8'd0)) begin
                        $fatal(1, "feature tail lane is not zero y=%0d k=%0d lane=%0d",
                               dut.row_y, dut.k_index, lane);
                    end
                end
                if ($signed(dut.shared_weight) !==
                    $signed(layer36_weights[dut.output_channel * K_COUNT + dut.k_index])) begin
                    $fatal(1, "weight lane mismatch k=%0d got=%0d expected=%0d",
                           dut.k_index, dut.shared_weight,
                           $signed(layer36_weights[dut.output_channel * K_COUNT + dut.k_index]));
                end
            end

            if (mem_valid && mem_ready) begin
                pass_requests = pass_requests + 1;
                if (mem_write) begin
                    if ((mem_rstrb != 4'b0000) || (mem_wstrb == 4'b0000) ||
                        ((mem_wstrb & (mem_wstrb - 4'd1)) != 4'b0000) ||
                        (mem_addr[1:0] != 2'b00)) begin
                        $fatal(1, "illegal output request address/strobes");
                    end
                    pass_output_writes = pass_output_writes + 1;
                    if ((mem_error_code == 3'd0) && score_enable) begin
                        for (lane = 0; lane < 4; lane = lane + 1) begin
                            if (mem_wstrb[lane]) begin
                                byte_offset = (mem_addr + lane) - OUTPUT_BASE;
                                if ((byte_offset < 0) || (byte_offset >= OUTPUT_BYTES)) begin
                                    $fatal(1, "output write outside 20280-byte tensor");
                                end
                                if (byte_offset != pass_output_writes - 1) begin
                                    $fatal(1, "output address/order mismatch offset=%0d expected=%0d",
                                           byte_offset, pass_output_writes - 1);
                                end
                                if (output_seen[byte_offset]) begin
                                    $fatal(1, "duplicate output write byte=%0d", byte_offset);
                                end
                                output_seen[byte_offset] = 1'b1;
                                if (mem_wdata[lane * 8 +: 8] !== expected_golden[byte_offset]) begin
                                    $fatal(1, "output mismatch byte=%0d got=%02x expected=%02x",
                                           byte_offset, mem_wdata[lane * 8 +: 8],
                                           expected_golden[byte_offset]);
                                end
                                output_memory[byte_offset] = mem_wdata[lane * 8 +: 8];
                                output_write_count = output_write_count + 1;
                                if ((pass_output_writes % PIXEL_COUNT) == 0) begin
                                    $display("PROGRESS output_channel=%0d raw=%0d feature_bytes=%0d weight_bytes=%0d",
                                             (pass_output_writes / PIXEL_COUNT) - 1,
                                             raw_compare_count, feature_selected_bytes,
                                             weight_selected_bytes);
                                end
                            end else if (mem_wdata[lane * 8 +: 8] != 8'd0) begin
                                $fatal(1, "output write has data in an unstroked lane");
                            end
                        end
                    end
                end else begin
                    if ((mem_wstrb != 4'b0000) || (mem_rstrb == 4'b0000) ||
                        (mem_addr[1:0] != 2'b00)) begin
                        $fatal(1, "illegal memory read address/strobes");
                    end
                    active_feature_request = 1'b0;
                    active_weight_request = 1'b0;
                    for (lane = 0; lane < 4; lane = lane + 1) begin
                        if (mem_rstrb[lane]) begin
                            read_byte_address = mem_addr + lane;
                            if ((read_byte_address >= FEATURE_BASE) &&
                                (read_byte_address < (FEATURE_BASE + INPUT_BYTES))) begin
                                active_feature_request = 1'b1;
                            end else if ((read_byte_address >= WEIGHT_BYTE_BASE) &&
                                         (read_byte_address < (WEIGHT_BYTE_BASE + WEIGHT_BYTES))) begin
                                active_weight_request = 1'b1;
                            end else begin
                                $fatal(1, "selected read byte is outside feature/weight fixtures");
                            end
                        end
                    end
                    if (active_feature_request == active_weight_request) begin
                        $fatal(1, "read must select exactly one feature or weight range");
                    end
                    if (active_feature_request) begin
                        pass_feature_requests = pass_feature_requests + 1;
                    end else begin
                        pass_weight_requests = pass_weight_requests + 1;
                    end
                    if ((mem_error_code == 3'd0) && score_enable) begin
                        for (lane = 0; lane < 4; lane = lane + 1) begin
                            if (mem_rstrb[lane]) begin
                                read_byte_address = mem_addr + lane;
                                if (active_feature_request) begin
                                    byte_offset = read_byte_address - FEATURE_BASE;
                                    feature_k = byte_offset / PIXEL_COUNT;
                                    feature_row = (byte_offset % PIXEL_COUNT) / 26;
                                    feature_x = byte_offset % 26;
                                    if ((feature_k != dut.k_index) ||
                                        (feature_row != dut.row_y)) begin
                                        $fatal(1, "feature address K/row mismatch oc=%0d k=%0d y=%0d addr_k=%0d addr_y=%0d",
                                               dut.output_channel, dut.k_index,
                                               dut.row_y, feature_k, feature_row);
                                    end
                                    if ((!dut.tile_index &&
                                         ((feature_x < 16) ||
                                          (dut.row_y[0] &&
                                           (dut.feature_word_index == 3'd4) &&
                                            (feature_x >= 16) && (feature_x <= 17))))) begin
                                        expected_index = 1;
                                    end else if (dut.tile_index &&
                                                 ((!dut.row_y[0] &&
                                                   (feature_x >= 16) && (feature_x <= 25)) ||
                                                  (dut.row_y[0] &&
                                                   (feature_x >= 18) && (feature_x <= 25)))) begin
                                        expected_index = 1;
                                    end else begin
                                        expected_index = 0;
                                    end
                                    if (!expected_index) begin
                                        $fatal(1, "feature read selected invalid spatial byte oc=%0d y=%0d tile=%0d x=%0d",
                                               dut.output_channel, dut.row_y,
                                               dut.tile_index, feature_x);
                                    end
                                    if (input_seen_by_channel[byte_offset][dut.output_channel]) begin
                                        $fatal(1, "duplicate feature byte oc=%0d offset=%0d",
                                               dut.output_channel, byte_offset);
                                    end
                                    input_seen_by_channel[byte_offset][dut.output_channel] = 1'b1;
                                    input_seen_count[byte_offset] = input_seen_count[byte_offset] + 1;
                                    if (mem_rdata[lane * 8 +: 8] !== input_fixture[byte_offset]) begin
                                        $fatal(1, "feature read data mismatch offset=%0d", byte_offset);
                                    end
                                    feature_selected_bytes = feature_selected_bytes + 1;
                                end else begin
                                    byte_offset = read_byte_address - WEIGHT_BYTE_BASE;
                                    if ((mem_rstrb & (mem_rstrb - 4'd1)) != 4'b0000) begin
                                        $fatal(1, "weight read must select exactly one byte");
                                    end
                                    if (byte_offset !=
                                        (dut.output_channel * K_COUNT + dut.k_index)) begin
                                        $fatal(1, "weight address/channel/K mismatch offset=%0d oc=%0d k=%0d",
                                               byte_offset, dut.output_channel,
                                               dut.k_index);
                                    end
                                    weight_seen_count[byte_offset] =
                                        weight_seen_count[byte_offset] + 1;
                                    if (mem_rdata[lane * 8 +: 8] !== layer36_weights[byte_offset]) begin
                                        $fatal(1, "weight read data mismatch offset=%0d", byte_offset);
                                    end
                                    weight_selected_bytes = weight_selected_bytes + 1;
                                end
                            end
                        end
                    end
                end
                if (mem_error_code != 3'd0) begin
                    fault_seen = 1;
                    if ((mem_error_code != 3'd1) && (mem_error_code != 3'd2) &&
                        (mem_error_code != 3'd6)) begin
                        $fatal(1, "test injected unsupported memory error code");
                    end
                end
            end
        end
    end

    initial begin
        $readmemh("input_fixture.hex", input_fixture);
        $readmemh("layer36_weights.hex", layer36_weights);
        $readmemh("expected_raw.hex", expected_raw);
        $readmemh("expected_golden.hex", expected_golden);
        $readmemh("expected_bias.hex", expected_bias);
        $readmemh("expected_mq.hex", expected_mq);
        $readmemh("expected_activation.hex", expected_activation);
        stall_cycles = 0;
        current_success_runs = 0;
        error_codes_seen = 0;
        abort_pending_cancel_count = 0;
        reset_pending_cancel_count = 0;
        output_abort_cancel_count = 0;
        output_reset_cancel_count = 0;
        output_cancel_write_handshakes = 0;
        output_cancel_armed = 1'b0;
        recovery_runs = 0;
        clear_scoreboards();
        clear_pass_counts();
        repeat (4) @(negedge clk);
        rst = 1'b0;

        run_error_case(1, 1, 1);
        run_error_case(2, 2, 2);
        run_error_case(3, 6, 6);
        cancel_pending_request(1'b0);
        cancel_pending_request(1'b1);
        cancel_pending_output_write(1'b0);
        cancel_pending_output_write(1'b1);

        clear_pass_counts();
        clear_scoreboards();
        score_enable = 1'b1;
        fault_mode = 0;
        start_operation();
        wait_for_result(0);
        score_enable = 1'b0;
        current_success_runs = current_success_runs + 1;
        recovery_runs = recovery_runs + 1;

        if (pass_requests != EXPECTED_MEMORY_REQUESTS) begin
            $fatal(1, "request count mismatch got=%0d expected=%0d",
                   pass_requests, EXPECTED_MEMORY_REQUESTS);
        end
        if ((pass_feature_requests != EXPECTED_FEATURE_READS) ||
            (feature_selected_bytes != EXPECTED_FEATURE_BYTES)) begin
            $fatal(1, "feature protocol counts mismatch requests=%0d bytes=%0d",
                   pass_feature_requests, feature_selected_bytes);
        end
        if ((pass_weight_requests != EXPECTED_WEIGHT_READS) ||
            (weight_selected_bytes != EXPECTED_WEIGHT_READS)) begin
            $fatal(1, "weight protocol counts mismatch requests=%0d bytes=%0d",
                   pass_weight_requests, weight_selected_bytes);
        end
        if ((pass_output_writes != EXPECTED_OUTPUT_WRITES) ||
            (output_write_count != EXPECTED_OUTPUT_WRITES) ||
            (raw_compare_count != EXPECTED_OUTPUT_WRITES) ||
            (parameter_check_count != 1560)) begin
            $fatal(1, "output/raw count mismatch writes=%0d outputs=%0d raw=%0d",
                   pass_output_writes, output_write_count, raw_compare_count);
        end
        for (idx = 0; idx < INPUT_BYTES; idx = idx + 1) begin
            if ((input_seen_count[idx] != OUTPUT_CHANNELS) ||
                (input_seen_by_channel[idx] != {OUTPUT_CHANNELS{1'b1}})) begin
                $fatal(1, "feature byte selection count mismatch offset=%0d count=%0d", idx, input_seen_count[idx]);
            end
        end
        for (idx = 0; idx < WEIGHT_BYTES; idx = idx + 1) begin
            if (weight_seen_count[idx] != 52) begin
                $fatal(1, "weight byte selection count mismatch offset=%0d count=%0d",
                       idx, weight_seen_count[idx]);
            end
        end
        for (idx = 0; idx < OUTPUT_BYTES; idx = idx + 1) begin
            if (!output_seen[idx] || !raw_seen[idx]) begin
                $fatal(1, "output/raw lane missing index=%0d", idx);
            end
            if (output_memory[idx] !== expected_golden[idx]) begin
                $fatal(1, "output memory differs from T20 golden index=%0d", idx);
            end
        end
        if ((error_codes_seen & ((1 << 1) | (1 << 2) | (1 << 6))) !=
            ((1 << 1) | (1 << 2) | (1 << 6))) begin
            $fatal(1, "directed memory error cases did not all propagate");
        end
        if ((abort_pending_cancel_count != 1) ||
            (reset_pending_cancel_count != 1) ||
            (output_abort_cancel_count != 1) ||
            (output_reset_cancel_count != 1) ||
            (output_cancel_write_handshakes != 0) || (recovery_runs != 1) ||
            (stall_cycles == 0)) begin
            $fatal(1, "cancel, recovery, or memory stall coverage is incomplete");
        end
        $display("PASS: requests=%0d feature_reads=%0d feature_bytes=%0d weight_reads=%0d weight_bytes=%0d output_writes=%0d raw_compares=%0d parameter_checks=%0d stalls=%0d error_codes=3 channel_boundary_error=1 abort_cancel=%0d reset_cancel=%0d output_abort_cancel=%0d output_reset_cancel=%0d output_cancel_handshakes=%0d recovery=%0d seed=539363623",
                 pass_requests, pass_feature_requests, feature_selected_bytes,
                 pass_weight_requests, weight_selected_bytes, output_write_count,
                 raw_compare_count, parameter_check_count, stall_cycles, abort_pending_cancel_count,
                 reset_pending_cancel_count, output_abort_cancel_count,
                 output_reset_cancel_count, output_cancel_write_handshakes,
                 recovery_runs);
        $display("S2A_T33_SIM_PASS");
        $finish;
    end
endmodule
