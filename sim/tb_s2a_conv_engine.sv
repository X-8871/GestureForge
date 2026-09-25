`timescale 1ns/1ps

module tb_s2a_conv_engine;
    localparam integer MAX_REDUCTION = 8191;
    localparam integer MAX_FEATURE_BYTES = 1500000;
    localparam logic [2:0] NONE = 3'd0;
    localparam logic [2:0] BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] BAD_RANGE = 3'd2;
    localparam logic [2:0] BAD_LENGTH = 3'd3;
    localparam logic [2:0] INTERNAL = 3'd6;
    localparam logic [2:0] ACCUMULATOR_OVERFLOW = 3'd7;

    logic clk;
    logic hard_reset;
    logic abort;
    logic buffer_owner_pl;
    logic start_valid;
    logic start_ready;
    logic [31:0] layer_index;
    logic [31:0] weight_layer_index;
    logic [31:0] input_base_address;
    logic [31:0] input_length_bytes;
    logic [31:0] input_batch_count;
    logic [31:0] input_channels;
    logic [31:0] input_height;
    logic [31:0] input_width;
    logic [31:0] output_base_address;
    logic [31:0] output_length_bytes;
    logic [31:0] output_batch_count;
    logic [31:0] output_channels;
    logic [31:0] output_height;
    logic [31:0] output_width;
    logic [31:0] kernel_height;
    logic [31:0] kernel_width;
    logic [31:0] stride_y;
    logic [31:0] stride_x;
    logic [31:0] pad_left;
    logic [31:0] pad_right;
    logic [31:0] pad_top;
    logic [31:0] pad_bottom;
    logic [31:0] groups;
    logic signed [31:0] padding_value_int8;
    logic [31:0] weight_package_base_address;
    logic [31:0] weight_package_length_bytes;
    logic [31:0] quantized_weight_offset;
    logic [31:0] quantized_weight_bytes;
    logic [31:0] output_batch;
    logic [31:0] output_channel;
    logic [31:0] output_y;
    logic [31:0] output_x;
    logic signed [31:0] bias_int32;
    logic [1:0] activation_mode;
    logic [31:0] positive_multiplier;
    logic [31:0] positive_q_shift;
    logic [31:0] negative_multiplier;
    logic [31:0] negative_q_shift;

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
    logic busy;
    logic result_valid;
    logic result_ready;
    logic [31:0] result_output_address;
    logic [7:0] result_value;
    logic [2:0] result_error_code;

    logic [7:0] feature_memory [0:MAX_FEATURE_BYTES-1];
    integer activation_case [0:MAX_REDUCTION-1];
    integer weight_case [0:MAX_REDUCTION-1];

    integer vector_file;
    integer config_file;
    integer config_fields;
    integer case_count;
    integer protocol_enable;
    integer case_index;
    integer case_kind;
    integer case_channel;
    integer case_y;
    integer case_x;
    integer case_bias;
    integer case_positive_multiplier;
    integer case_positive_q_shift;
    integer case_negative_multiplier;
    integer case_negative_q_shift;
    integer case_expected_accumulator;
    integer case_expected_value;
    integer raw_byte;
    reg [31:0] raw_word;
    integer reduction_count;
    integer reduction_index;
    integer kernel_area;
    integer tap_channel;
    integer tap_kernel_y;
    integer tap_kernel_x;
    integer tap_input_y;
    integer tap_input_x;
    integer tap_offset;
    integer inbound_taps;
    integer case_inbound_reads;
    integer case_weight_reads;
    integer case_write_count;
    integer total_vectors;
    integer total_input_reads;
    integer total_weight_reads;
    integer total_output_writes;
    integer total_padding_taps;
    integer total_feature_lane_mask;
    integer total_weight_lane_mask;
    integer total_output_lane_mask;
    integer case_cycle_count;
    integer feature_read_count;
    integer weight_read_count;
    integer output_write_count;
    integer feature_strobe_mask;
    integer weight_strobe_mask;
    integer output_strobe_mask;
    integer force_error_class;
    integer force_error_code;
    integer force_hold_class;
    integer request_class_now;
    integer stall_remaining;
    integer stall_active;
    integer stalled_previous;
    integer stalled_class;
    integer stall_length;
    integer request_number;
    integer selected_lane;
    integer selected_address;
    integer weight_index;
    integer output_lane;
    integer output_byte;
    integer expected_output_address;
    integer normal_result_value;
    integer normal_result_error;
    integer protocol_cases;
    integer protocol_errors;
    integer i;
    integer j;
    integer k;
    integer config_value;
    integer local_k;
    integer local_channel;
    integer local_kernel_y;
    integer local_kernel_x;
    integer local_y;
    integer local_x;
    integer local_offset;
    integer temp_value;
    reg [31:0] stalled_address;
    reg [31:0] stalled_wdata;
    reg [3:0] stalled_rstrb;
    reg [3:0] stalled_wstrb;
    reg stalled_write;
    reg pending_response;
    reg [31:0] pending_data;
    reg [2:0] pending_error;
    reg output_write_seen;

    always #5 clk = ~clk;

    s2a_conv_engine dut (
        .clk(clk),
        .hard_reset(hard_reset),
        .abort(abort),
        .buffer_owner_pl(buffer_owner_pl),
        .start_valid(start_valid),
        .start_ready(start_ready),
        .layer_index(layer_index),
        .weight_layer_index(weight_layer_index),
        .input_base_address(input_base_address),
        .input_length_bytes(input_length_bytes),
        .input_batch_count(input_batch_count),
        .input_channels(input_channels),
        .input_height(input_height),
        .input_width(input_width),
        .output_base_address(output_base_address),
        .output_length_bytes(output_length_bytes),
        .output_batch_count(output_batch_count),
        .output_channels(output_channels),
        .output_height(output_height),
        .output_width(output_width),
        .kernel_height(kernel_height),
        .kernel_width(kernel_width),
        .stride_y(stride_y),
        .stride_x(stride_x),
        .pad_left(pad_left),
        .pad_right(pad_right),
        .pad_top(pad_top),
        .pad_bottom(pad_bottom),
        .groups(groups),
        .padding_value_int8(padding_value_int8),
        .weight_package_base_address(weight_package_base_address),
        .weight_package_length_bytes(weight_package_length_bytes),
        .quantized_weight_offset(quantized_weight_offset),
        .quantized_weight_bytes(quantized_weight_bytes),
        .output_batch(output_batch),
        .output_channel(output_channel),
        .output_y(output_y),
        .output_x(output_x),
        .bias_int32(bias_int32),
        .activation_mode(activation_mode),
        .positive_multiplier(positive_multiplier),
        .positive_q_shift(positive_q_shift),
        .negative_multiplier(negative_multiplier),
        .negative_q_shift(negative_q_shift),
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
        .backend_rsp_error(backend_rsp_error),
        .busy(busy),
        .result_valid(result_valid),
        .result_ready(result_ready),
        .result_output_address(result_output_address),
        .result_value(result_value),
        .result_error_code(result_error_code)
    );

    function automatic integer read_u8(input integer fd);
        integer value;
        begin
            value = $fgetc(fd);
            if (value < 0) begin
                $fatal(1, "T17 vector file ended early while reading byte");
            end
            read_u8 = value & 255;
        end
    endfunction

    function automatic [31:0] read_u32(input integer fd);
        integer b0;
        integer b1;
        integer b2;
        integer b3;
        begin
            b0 = read_u8(fd);
            b1 = read_u8(fd);
            b2 = read_u8(fd);
            b3 = read_u8(fd);
            read_u32 = {b3[7:0], b2[7:0], b1[7:0], b0[7:0]};
        end
    endfunction

    function automatic integer current_request_class;
        reg [32:0] weight_end;
        begin
            weight_end = {1'b0, weight_package_base_address} +
                         {1'b0, weight_package_length_bytes};
            if (backend_req_write) begin
                current_request_class = 3;
            end else if ({1'b0, backend_req_addr} >= {1'b0, weight_package_base_address} &&
                         {1'b0, backend_req_addr} < weight_end) begin
                current_request_class = 2;
            end else begin
                current_request_class = 1;
            end
        end
    endfunction

    function automatic integer selected_stall_length(input integer request_class_value);
        integer count;
        begin
            case (request_class_value)
                1: count = feature_read_count;
                2: count = weight_read_count;
                default: count = output_write_count;
            endcase
            case (count)
                0: selected_stall_length = 0;
                1: selected_stall_length = 1;
                2: selected_stall_length = 2;
                3: selected_stall_length = 7;
                4: selected_stall_length = 3;
                default: selected_stall_length = 0;
            endcase
        end
    endfunction

    task automatic read_case(input integer fd);
        reg [31:0] word_value;
        integer value;
        begin
            case_index = read_u32(fd);
            case_kind = read_u32(fd);
            case_channel = read_u32(fd);
            case_y = read_u32(fd);
            case_x = read_u32(fd);
            word_value = read_u32(fd);
            case_bias = $signed(word_value);
            case_positive_multiplier = read_u32(fd);
            case_positive_q_shift = read_u32(fd);
            case_negative_multiplier = read_u32(fd);
            case_negative_q_shift = read_u32(fd);
            word_value = read_u32(fd);
            case_expected_accumulator = $signed(word_value);
            value = read_u8(fd);
            case_expected_value = (value >= 128) ? value - 256 : value;
            for (value = 0; value < reduction_count; value = value + 1) begin
                raw_byte = read_u8(fd);
                activation_case[value] = (raw_byte >= 128) ? raw_byte - 256 : raw_byte;
            end
            for (value = 0; value < reduction_count; value = value + 1) begin
                raw_byte = read_u8(fd);
                weight_case[value] = (raw_byte >= 128) ? raw_byte - 256 : raw_byte;
            end
        end
    endtask

    task automatic prepare_case_memory;
        integer local_channel;
        integer local_kernel_y;
        integer local_kernel_x;
        integer local_y;
        integer local_x;
        integer local_offset;
        begin
            inbound_taps = 0;
            for (local_k = 0; local_k < reduction_count; local_k = local_k + 1) begin
                local_channel = local_k / kernel_area;
                local_kernel_y = (local_k % kernel_area) / kernel_width;
                local_kernel_x = local_k % kernel_width;
                local_y = case_y * stride_y + local_kernel_y - pad_top;
                local_x = case_x * stride_x + local_kernel_x - pad_left;
                if ((local_y >= 0) && (local_y < input_height) &&
                    (local_x >= 0) && (local_x < input_width)) begin
                    local_offset = ((local_channel * input_height) + local_y) *
                                   input_width + local_x;
                    if ((local_offset < 0) || (local_offset >= input_length_bytes) ||
                        (local_offset >= MAX_FEATURE_BYTES)) begin
                        $fatal(1, "T17 testbench feature setup offset out of range");
                    end
                    feature_memory[local_offset] = activation_case[local_k] & 8'hff;
                    inbound_taps = inbound_taps + 1;
                end
            end
            case_inbound_reads = 0;
            case_weight_reads = 0;
            case_write_count = 0;
            feature_read_count = 0;
            weight_read_count = 0;
            output_write_count = 0;
            feature_strobe_mask = 0;
            weight_strobe_mask = 0;
            output_strobe_mask = 0;
            output_write_seen = 1'b0;
            output_byte = 0;
            output_channel = case_channel;
            output_y = case_y;
            output_x = case_x;
            bias_int32 = case_bias;
            positive_multiplier = case_positive_multiplier;
            positive_q_shift = case_positive_q_shift;
            negative_multiplier = case_negative_multiplier;
            negative_q_shift = case_negative_q_shift;
            expected_output_address = output_base_address +
                ((case_channel * output_height + case_y) * output_width + case_x);
            if ((expected_output_address < output_base_address) ||
                (expected_output_address >= output_base_address + output_length_bytes)) begin
                $fatal(1, "T17 testbench expected output address out of range");
            end
        end
    endtask

    task automatic start_current_case;
        integer watchdog;
        begin
            result_ready = 1'b0;
            start_valid = 1'b0;
            watchdog = 0;
            while (!start_ready) begin
                @(negedge clk);
                watchdog = watchdog + 1;
                if (watchdog > 100) begin
                    $fatal(1, "T17 start_ready timeout");
                end
            end
            start_valid = 1'b1;
            @(posedge clk);
            @(negedge clk);
            start_valid = 1'b0;
        end
    endtask

    task automatic wait_for_result(input integer expected_error, input integer check_output);
        integer watchdog;
        begin
            watchdog = 0;
            while (!result_valid) begin
                @(negedge clk);
                watchdog = watchdog + 1;
                if (watchdog > 1000000) begin
                    $fatal(1, "T17 result timeout layer=%0d case=%0d expected=%0d state=%0d mac_busy=%0d mac_result_valid=%0d reduction=%0d/%0d backend_rsp=%0d",
                           layer_index, case_index, expected_error, dut.state, dut.mac_busy,
                           dut.mac_result_valid, dut.reduction_index,
                           dut.reduction_count_latched, backend_rsp_valid);
                end
            end
            if (result_error_code !== expected_error[2:0]) begin
                $fatal(1, "T17 wrong result error layer=%0d case=%0d got=%0d expected=%0d",
                       layer_index, case_index, result_error_code, expected_error);
            end
            if (check_output != 0) begin
                if (result_value !== case_expected_value[7:0]) begin
                    $fatal(1, "T17 wrong output layer=%0d case=%0d got=%0d expected=%0d",
                           layer_index, case_index, $signed(result_value), case_expected_value);
                end
                if (result_output_address !== expected_output_address[31:0]) begin
                    $fatal(1, "T17 wrong output address layer=%0d case=%0d", layer_index, case_index);
                end
                if (!output_write_seen || (case_write_count != 1) ||
                    (output_byte != (case_expected_value & 255))) begin
                    $fatal(1, "T17 output byte write mismatch layer=%0d case=%0d count=%0d byte=%0d",
                           layer_index, case_index, case_write_count, output_byte);
                end
                if ((case_inbound_reads != inbound_taps) ||
                    (case_weight_reads != inbound_taps)) begin
                    $fatal(1, "T17 tap memory read count mismatch layer=%0d case=%0d in=%0d wt=%0d expected=%0d",
                           layer_index, case_index, case_inbound_reads, case_weight_reads, inbound_taps);
                end
            end else if ((case_write_count != 0) || output_write_seen) begin
                $fatal(1, "T17 erroneous transaction wrote output layer=%0d case=%0d", layer_index, case_index);
            end
            result_ready = 1'b1;
            @(posedge clk);
            @(negedge clk);
            result_ready = 1'b0;
            if (expected_error != NONE) begin
                protocol_errors = protocol_errors + 1;
            end
        end
    endtask

    task automatic run_success_case(input integer hold_result);
        reg [31:0] saved_address;
        reg [7:0] saved_value;
        reg [2:0] saved_error;
        integer wait_cycle;
        begin
            prepare_case_memory();
            start_current_case();
            wait_cycle = 0;
            while (!result_valid) begin
                @(negedge clk);
                wait_cycle = wait_cycle + 1;
                if ((wait_cycle == 4) && busy && start_ready) begin
                    $fatal(1, "T17 start_ready high while busy");
                end
                if (wait_cycle > 1000000) begin
                    $fatal(1, "T17 success case timeout");
                end
            end
            if (result_error_code != NONE) begin
                $fatal(1, "T17 unexpected error layer=%0d case=%0d error=%0d",
                       layer_index, case_index, result_error_code);
            end
            if (result_value !== case_expected_value[7:0] ||
                result_output_address !== expected_output_address[31:0] ||
                !output_write_seen || (case_write_count != 1) ||
                (output_byte != (case_expected_value & 255)) ||
                (case_inbound_reads != inbound_taps) ||
                (case_weight_reads != inbound_taps)) begin
                $fatal(1, "T17 success output/readback mismatch layer=%0d case=%0d", layer_index, case_index);
            end
            if (hold_result != 0) begin
                saved_address = result_output_address;
                saved_value = result_value;
                saved_error = result_error_code;
                repeat (3) begin
                    @(negedge clk);
                    if (!result_valid || start_ready || !busy ||
                        (result_output_address !== saved_address) ||
                        (result_value !== saved_value) || (result_error_code !== saved_error)) begin
                        $fatal(1, "T17 result/backpressure stability failure");
                    end
                end
            end
            result_ready = 1'b1;
            @(posedge clk);
            @(negedge clk);
            result_ready = 1'b0;
        end
    endtask

    task automatic run_error_case(input integer expected_error);
        begin
            prepare_case_memory();
            start_current_case();
            wait_for_result(expected_error, 0);
            protocol_errors = protocol_errors + 1;
        end
    endtask

    task automatic run_protocol_cases;
        integer fd;
        integer skip_index;
        integer saved_channel;
        integer saved_q;
        integer saved_length;
        integer saved_input_base;
        integer saved_weight_offset;
        integer saved_m;
        integer saved_bias;
        integer held_write_seen;
        integer watchdog;
        integer first_valid_tap;
        integer local_channel;
        integer local_ky;
        integer local_kx;
        integer local_y;
        integer local_x;
        begin
            fd = $fopen("s2a_t17_vectors.bin", "rb");
            if (fd == 0) begin
                $fatal(1, "T17 cannot reopen vector file for protocol cases");
            end
            if ((case_count == 1016) && (protocol_enable != 0)) begin
                for (skip_index = 0; skip_index < 1000; skip_index = skip_index + 1) begin
                    read_case(fd);
                end
            end
            read_case(fd);
            $fclose(fd);

            saved_channel = output_channel;
            saved_length = output_length_bytes;
            saved_q = positive_q_shift;
            prepare_case_memory();
            output_channel = output_channels;
            start_current_case();
            wait_for_result(BAD_ARGUMENT, 0);
            if ((case_inbound_reads != 0) || (case_weight_reads != 0) ||
                (case_write_count != 0)) $fatal(1, "T17 bad channel caused memory side effects");
            output_channel = saved_channel;

            prepare_case_memory();
            output_length_bytes = saved_length - 1;
            start_current_case();
            wait_for_result(BAD_LENGTH, 0);
            if ((case_inbound_reads != 0) || (case_weight_reads != 0) ||
                (case_write_count != 0)) $fatal(1, "T17 bad length caused memory side effects");
            output_length_bytes = saved_length;

            prepare_case_memory();
            saved_m = positive_multiplier;
            positive_multiplier = 32'h4000_0000;
            start_current_case();
            wait_for_result(BAD_ARGUMENT, 0);
            if ((case_inbound_reads != 0) || (case_weight_reads != 0) ||
                (case_write_count != 0)) $fatal(1, "T17 bad multiplier caused memory side effects");
            positive_multiplier = saved_m;
            prepare_case_memory();

            positive_q_shift = 48;
            start_current_case();
            wait_for_result(BAD_ARGUMENT, 0);
            if ((case_inbound_reads != 0) || (case_weight_reads != 0) ||
                (case_write_count != 0)) $fatal(1, "T17 bad Q shift caused memory side effects");
            positive_q_shift = saved_q;

            saved_input_base = input_base_address;
            input_base_address = 32'hffff_fff0;
            prepare_case_memory();
            start_current_case();
            wait_for_result(BAD_RANGE, 0);
            if ((case_inbound_reads != 0) || (case_weight_reads != 0) ||
                (case_write_count != 0)) $fatal(1, "T17 wrapped input range caused memory side effects");
            input_base_address = saved_input_base;

            saved_weight_offset = quantized_weight_offset;
            quantized_weight_offset = weight_package_length_bytes;
            prepare_case_memory();
            start_current_case();
            wait_for_result(BAD_RANGE, 0);
            if ((case_inbound_reads != 0) || (case_weight_reads != 0) ||
                (case_write_count != 0)) $fatal(1, "T17 invalid weight range caused memory side effects");
            quantized_weight_offset = saved_weight_offset;

            prepare_case_memory();
            buffer_owner_pl = 1'b0;
            start_current_case();
            wait_for_result(BAD_ARGUMENT, 0);
            if ((case_inbound_reads != 0) || (case_weight_reads != 0) ||
                (case_write_count != 0)) $fatal(1, "T17 non-owner caused memory side effects");
            buffer_owner_pl = 1'b1;

            force_error_class = 1;
            force_error_code = 6;
            prepare_case_memory();
            start_current_case();
            wait_for_result(INTERNAL, 0);
            if (case_write_count != 0) begin
                $fatal(1, "T17 feature memory error allowed an output write");
            end
            force_error_class = 2;
            force_error_code = 7;
            prepare_case_memory();
            start_current_case();
            wait_for_result(INTERNAL, 0);
            if (case_write_count != 0) begin
                $fatal(1, "T17 weight memory error allowed an output write");
            end
            force_error_class = 3;
            force_error_code = 6;
            prepare_case_memory();
            start_current_case();
            wait_for_result(INTERNAL, 0);
            if (case_write_count != 0 || output_write_seen) begin
                $fatal(1, "T17 output memory error committed a write");
            end
            force_error_class = 0;

            saved_bias = case_bias;
            first_valid_tap = -1;
            for (local_k = 0; local_k < reduction_count; local_k = local_k + 1) begin
                local_channel = local_k / kernel_area;
                local_ky = (local_k % kernel_area) / kernel_width;
                local_kx = local_k % kernel_width;
                local_y = case_y * stride_y + local_ky - pad_top;
                local_x = case_x * stride_x + local_kx - pad_left;
                if ((first_valid_tap < 0) && (local_y >= 0) &&
                    (local_y < input_height) && (local_x >= 0) &&
                    (local_x < input_width)) begin
                    first_valid_tap = local_k;
                end
            end
            if (first_valid_tap < 0) begin
                $fatal(1, "T17 overflow fixture has no valid input tap");
            end
            for (local_k = 0; local_k < reduction_count; local_k = local_k + 1) begin
                activation_case[local_k] = 0;
                weight_case[local_k] = 0;
            end
            activation_case[first_valid_tap] = 1;
            weight_case[first_valid_tap] = 1;
            case_bias = 32'sh7fff_ffff;
            prepare_case_memory();
            start_current_case();
            wait_for_result(ACCUMULATOR_OVERFLOW, 0);
            if (case_write_count != 0) begin
                $fatal(1, "T17 accumulator overflow allowed an output write");
            end
            case_bias = saved_bias;

            force_hold_class = 1;
            prepare_case_memory();
            start_current_case();
            watchdog = 0;
            while (!(backend_req_valid && !backend_req_write && !backend_req_ready)) begin
                @(negedge clk);
                watchdog = watchdog + 1;
                if (watchdog > 100000) $fatal(1, "T17 held feature request timeout");
            end
            abort = 1'b1;
            @(posedge clk);
            @(negedge clk);
            abort = 1'b0;
            force_hold_class = 0;
            repeat (4) @(negedge clk);
            if (busy || result_valid || output_write_seen || (case_write_count != 0)) begin
                $fatal(1, "T17 abort with pending read did not cancel cleanly");
            end

            force_hold_class = 3;
            prepare_case_memory();
            start_current_case();
            watchdog = 0;
            while (!(backend_req_valid && backend_req_write && !backend_req_ready)) begin
                @(negedge clk);
                watchdog = watchdog + 1;
                if (watchdog > 100000) $fatal(1, "T17 held output request timeout");
            end
            hard_reset = 1'b1;
            @(posedge clk);
            @(negedge clk);
            hard_reset = 1'b0;
            force_hold_class = 0;
            repeat (4) @(negedge clk);
            if (busy || result_valid || output_write_seen || (case_write_count != 0)) begin
                $fatal(1, "T17 hard reset with pending write did not cancel cleanly");
            end

            prepare_case_memory();
            run_success_case(1);
            protocol_cases = protocol_cases + 1;
        end
    endtask

    initial begin
        clk = 1'b0;
        hard_reset = 1'b1;
        abort = 1'b0;
        buffer_owner_pl = 1'b1;
        start_valid = 1'b0;
        result_ready = 1'b0;
        backend_req_ready = 1'b0;
        backend_rsp_valid = 1'b0;
        backend_rsp_rdata = 32'd0;
        backend_rsp_error = NONE;
        pending_response = 1'b0;
        pending_data = 32'd0;
        pending_error = NONE;
        output_write_seen = 1'b0;
        force_error_class = 0;
        force_error_code = 0;
        force_hold_class = 0;
        stall_remaining = 0;
        stall_active = 0;
        stalled_previous = 0;
        total_vectors = 0;
        total_input_reads = 0;
        total_weight_reads = 0;
        total_output_writes = 0;
        total_padding_taps = 0;
        total_feature_lane_mask = 0;
        total_weight_lane_mask = 0;
        total_output_lane_mask = 0;
        protocol_cases = 0;
        protocol_errors = 0;
        feature_read_count = 0;
        weight_read_count = 0;
        output_write_count = 0;
        feature_strobe_mask = 0;
        weight_strobe_mask = 0;
        output_strobe_mask = 0;
        layer_index = 0;
        weight_layer_index = 0;
        input_base_address = 0;
        input_length_bytes = 0;
        input_batch_count = 1;
        input_channels = 0;
        input_height = 0;
        input_width = 0;
        output_base_address = 0;
        output_length_bytes = 0;
        output_batch_count = 1;
        output_channels = 0;
        output_height = 0;
        output_width = 0;
        kernel_height = 0;
        kernel_width = 0;
        stride_y = 0;
        stride_x = 0;
        pad_left = 0;
        pad_right = 0;
        pad_top = 0;
        pad_bottom = 0;
        groups = 1;
        padding_value_int8 = 0;
        weight_package_base_address = 0;
        weight_package_length_bytes = 0;
        quantized_weight_offset = 0;
        quantized_weight_bytes = 0;
        output_batch = 0;
        output_channel = 0;
        output_y = 0;
        output_x = 0;
        bias_int32 = 0;
        activation_mode = 0;
        positive_multiplier = 1;
        positive_q_shift = 0;
        negative_multiplier = 1;
        negative_q_shift = 0;
        case_count = 0;
        protocol_enable = 0;

        for (i = 0; i < MAX_FEATURE_BYTES; i = i + 1) begin
            feature_memory[i] = 8'd0;
        end

        config_file = $fopen("s2a_t17_config.txt", "r");
        if (config_file == 0) $fatal(1, "T17 cannot open configuration");
        config_fields = $fscanf(config_file,
            "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d",
            layer_index, weight_layer_index,
            input_base_address, input_length_bytes, input_batch_count,
            input_channels, input_height, input_width,
            output_base_address, output_length_bytes, output_batch_count,
            output_channels, output_height, output_width,
            kernel_height, kernel_width, stride_y, stride_x,
            pad_left, pad_right, pad_top, pad_bottom, groups,
            padding_value_int8, weight_package_base_address,
            weight_package_length_bytes, quantized_weight_offset,
            quantized_weight_bytes, case_count, protocol_enable,
            activation_mode);
        $fclose(config_file);
        if (config_fields != 31) $fatal(1, "T17 configuration field count mismatch: %0d", config_fields);
        reduction_count = input_channels * kernel_height * kernel_width;
        kernel_area = kernel_height * kernel_width;
        if ((reduction_count <= 0) || (reduction_count > MAX_REDUCTION) ||
            (input_length_bytes > MAX_FEATURE_BYTES) || (case_count <= 0)) begin
            $fatal(1, "T17 test configuration exceeds testbench bounds");
        end
        vector_file = $fopen("s2a_t17_vectors.bin", "rb");
        if (vector_file == 0) $fatal(1, "T17 cannot open case vectors");

        repeat (3) @(posedge clk);
        @(negedge clk);
        hard_reset = 1'b0;

        for (i = 0; i < case_count; i = i + 1) begin
            read_case(vector_file);
            run_success_case((i == 0) ? 1 : 0);
            total_vectors = total_vectors + 1;
            total_padding_taps = total_padding_taps + reduction_count - inbound_taps;
            total_input_reads = total_input_reads + case_inbound_reads;
            total_weight_reads = total_weight_reads + case_weight_reads;
            total_output_writes = total_output_writes + case_write_count;
            total_feature_lane_mask = total_feature_lane_mask | feature_strobe_mask;
            total_weight_lane_mask = total_weight_lane_mask | weight_strobe_mask;
            total_output_lane_mask = total_output_lane_mask | output_strobe_mask;
        end
        $fclose(vector_file);
        if (protocol_enable != 0) begin
            run_protocol_cases();
        end

        $display("PASS S2A-T17 layer=%0d vectors=%0d input_reads=%0d weight_reads=%0d output_writes=%0d padding_taps=%0d protocol_cases=%0d protocol_errors=%0d feature_lane_mask=%0x weight_lane_mask=%0x output_lane_mask=%0x",
                 layer_index, total_vectors, total_input_reads, total_weight_reads,
                 total_output_writes, total_padding_taps, protocol_cases, protocol_errors,
                 total_feature_lane_mask, total_weight_lane_mask, total_output_lane_mask);
        $finish;
    end

    always @(negedge clk) begin
        if (hard_reset || abort || backend_cancel) begin
            backend_req_ready = 1'b0;
            stall_active = 0;
            stall_remaining = 0;
        end else if (!backend_req_valid) begin
            backend_req_ready = 1'b0;
            stall_active = 0;
            stall_remaining = 0;
        end else begin
            request_class_now = current_request_class();
            if (force_hold_class == request_class_now) begin
                backend_req_ready = 1'b0;
                stall_active = 1;
                stalled_class = request_class_now;
            end else if (!stall_active || (stalled_class != request_class_now)) begin
                stall_length = selected_stall_length(request_class_now);
                stalled_class = request_class_now;
                if (stall_length > 0) begin
                    stall_active = 1;
                    stall_remaining = stall_length;
                    backend_req_ready = 1'b0;
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
    end

    always @(posedge clk) begin
        if (hard_reset || backend_cancel) begin
            backend_rsp_valid <= 1'b0;
            backend_rsp_rdata <= 32'd0;
            backend_rsp_error <= NONE;
            pending_response <= 1'b0;
            pending_data <= 32'd0;
            pending_error <= NONE;
            stalled_previous <= 1'b0;
        end else begin
            backend_rsp_valid <= 1'b0;
            backend_rsp_error <= NONE;
            if (stalled_previous &&
                (!backend_req_valid || backend_req_write !== stalled_write ||
                 backend_req_addr !== stalled_address ||
                 backend_req_wdata !== stalled_wdata ||
                 backend_req_rstrb !== stalled_rstrb ||
                 backend_req_wstrb !== stalled_wstrb)) begin
                $fatal(1, "T17 backend request changed during a stall");
            end
            stalled_previous <= backend_req_valid && !backend_req_ready;
            if (backend_req_valid && !backend_req_ready) begin
                stalled_write <= backend_req_write;
                stalled_address <= backend_req_addr;
                stalled_wdata <= backend_req_wdata;
                stalled_rstrb <= backend_req_rstrb;
                stalled_wstrb <= backend_req_wstrb;
            end
            if (pending_response) begin
                backend_rsp_valid <= 1'b1;
                backend_rsp_rdata <= pending_data;
                backend_rsp_error <= pending_error;
                pending_response <= 1'b0;
            end
            if (backend_req_valid && backend_req_ready) begin
                if (pending_response) $fatal(1, "T17 backend accepted overlapping request");
                request_class_now = current_request_class();
                selected_lane = -1;
                for (j = 0; j < 4; j = j + 1) begin
                    if (!backend_req_write && backend_req_rstrb[j]) selected_lane = j;
                    if (backend_req_write && backend_req_wstrb[j]) selected_lane = j;
                end
                if ((selected_lane < 0) ||
                    (!backend_req_write && (backend_req_rstrb != (4'b0001 << selected_lane))) ||
                    (backend_req_write && (backend_req_wstrb != (4'b0001 << selected_lane)))) begin
                    $fatal(1, "T17 backend request has invalid byte strobe");
                end
                pending_error = NONE;
                pending_data = 32'd0;
                if (force_error_class == request_class_now) begin
                    pending_error = force_error_code[2:0];
                end else if (backend_req_write) begin
                    output_lane = selected_lane;
                    output_byte = (backend_req_wdata >> (output_lane * 8)) & 255;
                    output_write_seen = 1'b1;
                    case_write_count = case_write_count + 1;
                    output_write_count = output_write_count + 1;
                    output_strobe_mask = output_strobe_mask | backend_req_wstrb;
                    if ((backend_req_wstrb != (4'b0001 << (expected_output_address & 3))) ||
                        (backend_req_addr != (expected_output_address & 32'hffff_fffc))) begin
                        $fatal(1, "T17 output byte lane/address mismatch");
                    end
                end else if (request_class_now == 1) begin
                    selected_address = backend_req_addr + selected_lane - input_base_address;
                    if ((selected_address < 0) || (selected_address >= input_length_bytes)) begin
                        $fatal(1, "T17 feature read escaped input tensor");
                    end
                    pending_data = {24'd0, feature_memory[selected_address]} << (selected_lane * 8);
                    case_inbound_reads = case_inbound_reads + 1;
                    feature_read_count = feature_read_count + 1;
                    feature_strobe_mask = feature_strobe_mask | backend_req_rstrb;
                end else begin
                    selected_address = backend_req_addr + selected_lane -
                                       weight_package_base_address - quantized_weight_offset;
                    if ((selected_address < 0) || (selected_address >= quantized_weight_bytes)) begin
                        $fatal(1, "T17 weight read escaped quantized weight object");
                    end
                    if ((selected_address / reduction_count != case_channel) ||
                        (selected_address < case_channel * reduction_count) ||
                        (selected_address >= (case_channel + 1) * reduction_count)) begin
                        $fatal(1, "T17 weight address is outside selected output-channel segment layer=%0d case=%0d channel=%0d address=%0d K=%0d",
                               layer_index, case_index, case_channel, selected_address,
                               reduction_count);
                    end
                    weight_index = selected_address - case_channel * reduction_count;
                    pending_data = {24'd0, (weight_case[weight_index] & 255)} <<
                                   (selected_lane * 8);
                    case_weight_reads = case_weight_reads + 1;
                    weight_read_count = weight_read_count + 1;
                    weight_strobe_mask = weight_strobe_mask | backend_req_rstrb;
                end
                if (backend_req_write && (force_error_class == request_class_now)) begin
                    output_write_seen = 1'b0;
                end
                pending_response <= 1'b1;
                if (backend_req_write || (request_class_now == 1)) begin
                    total_output_writes = total_output_writes;
                end
            end
        end
    end
endmodule
