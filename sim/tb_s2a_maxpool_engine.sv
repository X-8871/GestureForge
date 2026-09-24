// S2A-T14 maxpool memory datapath 的首轮隔离 smoke test。
module tb_s2a_maxpool_engine;
    logic clk = 1'b0;
    always #5 clk = ~clk;

    logic hard_reset = 1'b1;
    logic abort = 1'b0;
    logic start_valid = 1'b0;
    logic start_ready;
    logic [31:0] layer_index = 32'd9;
    logic [31:0] input_base_address = 32'd21968896;
    logic [31:0] input_length_bytes = 32'd1384448;
    logic [31:0] input_channels = 32'd128;
    logic [31:0] input_height = 32'd104;
    logic [31:0] input_width = 32'd104;
    logic [31:0] output_base_address = 32'd23353344;
    logic [31:0] output_length_bytes = 32'd346112;
    logic [31:0] output_channels = 32'd128;
    logic [31:0] output_height = 32'd52;
    logic [31:0] output_width = 32'd52;
    logic [31:0] kernel_height = 32'd2;
    logic [31:0] kernel_width = 32'd2;
    logic [31:0] stride_y = 32'd2;
    logic [31:0] stride_x = 32'd2;
    logic [31:0] darknet_padding_parameter = 32'd1;
    logic [31:0] output_channel = 32'd0;
    logic [31:0] output_y = 32'd0;
    logic [31:0] output_x = 32'd0;

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
    logic result_valid;
    logic result_ready = 1'b0;
    logic [127:0] result_tap_addresses;
    logic [31:0] result_output_address;
    logic [7:0] result_value;
    logic [2:0] result_error_code;

    logic mem_valid;
    logic mem_ready;
    logic mem_write;
    logic [31:0] mem_addr;
    logic [31:0] mem_wdata;
    logic [3:0] mem_rstrb;
    logic [3:0] mem_wstrb;
    logic [31:0] mem_rdata;
    logic [2:0] mem_error_code;
    logic model_initialized;
    integer read_count = 0;
    integer write_count = 0;
    integer watchdog;

    s2a_maxpool_engine dut (
        .clk(clk), .hard_reset(hard_reset), .abort(abort),
        .start_valid(start_valid), .start_ready(start_ready),
        .layer_index(layer_index),
        .input_base_address(input_base_address),
        .input_length_bytes(input_length_bytes),
        .input_channels(input_channels), .input_height(input_height),
        .input_width(input_width), .output_base_address(output_base_address),
        .output_length_bytes(output_length_bytes),
        .output_channels(output_channels), .output_height(output_height),
        .output_width(output_width), .kernel_height(kernel_height),
        .kernel_width(kernel_width), .stride_y(stride_y), .stride_x(stride_x),
        .darknet_padding_parameter(darknet_padding_parameter),
        .output_channel(output_channel), .output_y(output_y), .output_x(output_x),
        .backend_cancel(backend_cancel), .backend_req_valid(backend_req_valid),
        .backend_req_ready(backend_req_ready), .backend_req_write(backend_req_write),
        .backend_req_addr(backend_req_addr), .backend_req_wdata(backend_req_wdata),
        .backend_req_rstrb(backend_req_rstrb), .backend_req_wstrb(backend_req_wstrb),
        .backend_rsp_valid(backend_rsp_valid), .backend_rsp_rdata(backend_rsp_rdata),
        .backend_rsp_error(backend_rsp_error), .result_valid(result_valid),
        .result_ready(result_ready), .result_tap_addresses(result_tap_addresses),
        .result_output_address(result_output_address), .result_value(result_value),
        .result_error_code(result_error_code)
    );

    s2a_memory_master u_master (
        .clk(clk), .hard_reset(hard_reset), .cancel(backend_cancel),
        .buffer_owner_pl(1'b1), .backend_req_valid(backend_req_valid),
        .backend_req_ready(backend_req_ready), .backend_req_write(backend_req_write),
        .backend_req_addr(backend_req_addr), .backend_req_wdata(backend_req_wdata),
        .backend_req_rstrb(backend_req_rstrb), .backend_req_wstrb(backend_req_wstrb),
        .backend_rsp_valid(backend_rsp_valid), .backend_rsp_rdata(backend_rsp_rdata),
        .backend_rsp_error(backend_rsp_error), .mem_valid(mem_valid),
        .mem_ready(mem_ready), .mem_write(mem_write), .mem_addr(mem_addr),
        .mem_wdata(mem_wdata), .mem_rstrb(mem_rstrb), .mem_wstrb(mem_wstrb),
        .mem_rdata(mem_rdata), .mem_error_code(mem_error_code)
    );

    s2a_memory_model u_memory (
        .clk(clk), .reset(hard_reset), .buffer_owner_pl(1'b1),
        .fault_inject_valid(1'b0), .fault_inject_code(3'd0),
        .mem_valid(mem_valid), .mem_write(mem_write), .mem_addr(mem_addr),
        .mem_wdata(mem_wdata), .mem_rstrb(mem_rstrb), .mem_wstrb(mem_wstrb),
        .mem_ready(mem_ready), .mem_rdata(mem_rdata),
        .mem_error_code(mem_error_code), .model_initialized(model_initialized)
    );

    always @(posedge clk) begin
        if (mem_valid && mem_ready) begin
            if (mem_write) begin
                if (mem_addr !== 32'd23353344 || mem_wstrb !== 4'b0001 ||
                    mem_rstrb !== 4'd0 || mem_wdata[7:0] !== 8'hD3) begin
                    $fatal(1, "FAIL: smoke output byte-lane write mismatch");
                end
                write_count = write_count + 1;
            end else begin
                case (read_count)
                    0: if (mem_addr !== 32'd21968896 || mem_rstrb !== 4'b0001) $fatal(1, "FAIL: tap0");
                    1: if (mem_addr !== 32'd21968896 || mem_rstrb !== 4'b0010) $fatal(1, "FAIL: tap1");
                    2: if (mem_addr !== 32'd21969000 || mem_rstrb !== 4'b0001) $fatal(1, "FAIL: tap2");
                    3: if (mem_addr !== 32'd21969000 || mem_rstrb !== 4'b0010) $fatal(1, "FAIL: tap3");
                    default: $fatal(1, "FAIL: excess smoke read");
                endcase
                read_count = read_count + 1;
            end
        end
    end


    initial begin
        wait (model_initialized);
        repeat (2) @(posedge clk);
        @(negedge clk);
        hard_reset = 1'b0;
        start_valid = 1'b1;
        @(posedge clk);
        @(negedge clk);
        start_valid = 1'b0;
        watchdog = 0;
        while (!result_valid) begin
            @(negedge clk);
            watchdog = watchdog + 1;
            if (watchdog > 300) $fatal(1, "FAIL: smoke result timeout");
        end
        if (result_error_code !== 3'd0 || result_value !== 8'hD3 ||
            result_output_address !== 32'd23353344 ||
            result_tap_addresses !== {32'd21969001, 32'd21969000,
                                      32'd21968897, 32'd21968896} ||
            read_count != 4 || write_count != 1) begin
            $fatal(1, "FAIL: smoke result/transfer mismatch err=%0d value=%02h reads=%0d writes=%0d",
                   result_error_code, result_value, read_count, write_count);
        end
        repeat (2) begin
            @(negedge clk);
            if (!result_valid || result_value !== 8'hD3 || result_error_code !== 3'd0)
                $fatal(1, "FAIL: smoke result did not stay stable");
        end
        result_ready = 1'b1;
        @(posedge clk);
        @(negedge clk);
        if (result_valid) $fatal(1, "FAIL: smoke result handshake failed");
        $display("PASS S2A-T14 maxpool smoke reads=4 writes=1 value=D3");
        $finish;
    end
endmodule

// S2A-T14 官方坐标、T10/T12 故障与事务协议完整验证顶层。
module tb_s2a_maxpool_engine_full;
    logic clk = 1'b0;
    always #5 clk = ~clk;

    logic hard_reset, abort, start_valid, start_ready;
    logic [31:0] layer_index, input_base_address, input_length_bytes;
    logic [31:0] input_channels, input_height, input_width;
    logic [31:0] output_base_address, output_length_bytes;
    logic [31:0] output_channels, output_height, output_width;
    logic [31:0] kernel_height, kernel_width, stride_y, stride_x;
    logic [31:0] darknet_padding_parameter, output_channel, output_y, output_x;
    logic backend_cancel, engine_req_valid, engine_req_ready, engine_req_write;
    logic [31:0] engine_req_addr, engine_req_wdata;
    logic [3:0] engine_req_rstrb, engine_req_wstrb;
    logic engine_rsp_valid;
    logic [31:0] engine_rsp_rdata;
    logic [2:0] engine_rsp_error;
    logic result_valid, result_ready;
    logic [127:0] result_tap_addresses;
    logic [31:0] result_output_address;
    logic [7:0] result_value;
    logic [2:0] result_error_code;

    logic backend_owner_pl, readback_mode;
    logic readback_req_valid, readback_req_ready;
    logic [31:0] readback_req_addr;
    logic [3:0] readback_req_rstrb;
    logic master_req_valid, master_req_ready, master_req_write;
    logic [31:0] master_req_addr, master_req_wdata;
    logic [3:0] master_req_rstrb, master_req_wstrb;
    logic master_rsp_valid;
    logic [31:0] master_rsp_rdata;
    logic [2:0] master_rsp_error;
    logic override_rsp_error_valid;
    logic [2:0] override_rsp_error_code;

    logic fault_inject_valid, fault_on_write_mode;
    logic [2:0] fault_inject_code, model_fault_code;
    integer fault_target_tap;
    logic model_fault_valid, model_reset;
    logic mem_valid, model_ready, mem_write;
    logic [31:0] mem_addr, mem_wdata, model_rdata;
    logic [3:0] mem_rstrb, mem_wstrb;
    logic [2:0] model_error;
    logic model_initialized;

    logic [31:0] expected_tap [0:3];
    logic [31:0] vector_tap [0:3];
    logic [31:0] expected_output_address;
    logic [7:0] expected_output_byte;
    integer expected_tap_index, expected_tap_count;
    integer input_read_transfers, write_transfers, readback_checks;
    integer accepted_backend_requests, backend_responses, memory_handshakes;
    integer memory_stall_cycles, outstanding;
    integer raw_fault_checks, response_override_checks, write_fault_checks;
    integer invalid_checks, read_abort_checks, read_reset_checks;
    integer write_abort_checks, write_reset_checks, recovery_checks, ownership_checks;
    integer official_random, official_directed, official_queries;
    integer official_legal, official_raw_80;
    logic held_memory_request, held_write;
    logic [31:0] held_addr, held_wdata;
    logic [3:0] held_rstrb, held_wstrb;
    integer vector_fd, scan_result, vector_class, vector_layer, vector_case;
    integer vector_channel, vector_y, vector_x;
    integer vector_candidate0, vector_candidate1, vector_candidate2, vector_candidate3;
    integer vector_count, random_counts [0:2], directed_counts [0:2];
    integer official_input_reads, official_writes, official_readbacks;
    integer official_reads_before, official_writes_before, official_readbacks_before;
    integer watchdog, align_count, k;
    logic [2:0] golden_error;
    logic [7:0] golden_value, observed_value, prior_value;

    function automatic logic [7:0] initial_byte(input logic [31:0] address);
        initial_byte = address[7:0] ^ address[15:8] ^ address[23:16] ^
                       address[31:24] ^ 8'hA5;
    endfunction

    function automatic logic [3:0] lane_mask(input logic [31:0] address);
        lane_mask = 4'b0001 << address[1:0];
    endfunction

    function automatic logic [7:0] lane_value(input logic [31:0] word_value,
                                               input logic [1:0] lane);
        lane_value = word_value >> (lane * 8);
    endfunction

    s2a_maxpool_engine dut (
        .clk(clk), .hard_reset(hard_reset), .abort(abort),
        .start_valid(start_valid), .start_ready(start_ready),
        .layer_index(layer_index), .input_base_address(input_base_address),
        .input_length_bytes(input_length_bytes), .input_channels(input_channels),
        .input_height(input_height), .input_width(input_width),
        .output_base_address(output_base_address),
        .output_length_bytes(output_length_bytes), .output_channels(output_channels),
        .output_height(output_height), .output_width(output_width),
        .kernel_height(kernel_height), .kernel_width(kernel_width),
        .stride_y(stride_y), .stride_x(stride_x),
        .darknet_padding_parameter(darknet_padding_parameter),
        .output_channel(output_channel), .output_y(output_y), .output_x(output_x),
        .backend_cancel(backend_cancel), .backend_req_valid(engine_req_valid),
        .backend_req_ready(engine_req_ready), .backend_req_write(engine_req_write),
        .backend_req_addr(engine_req_addr), .backend_req_wdata(engine_req_wdata),
        .backend_req_rstrb(engine_req_rstrb), .backend_req_wstrb(engine_req_wstrb),
        .backend_rsp_valid(engine_rsp_valid), .backend_rsp_rdata(engine_rsp_rdata),
        .backend_rsp_error(engine_rsp_error), .result_valid(result_valid),
        .result_ready(result_ready), .result_tap_addresses(result_tap_addresses),
        .result_output_address(result_output_address), .result_value(result_value),
        .result_error_code(result_error_code)
    );

    always_comb begin
        master_req_valid = readback_mode ? readback_req_valid : engine_req_valid;
        master_req_write = readback_mode ? 1'b0 : engine_req_write;
        master_req_addr = readback_mode ? readback_req_addr : engine_req_addr;
        master_req_wdata = readback_mode ? 32'd0 : engine_req_wdata;
        master_req_rstrb = readback_mode ? readback_req_rstrb : engine_req_rstrb;
        master_req_wstrb = readback_mode ? 4'd0 : engine_req_wstrb;
        engine_req_ready = !readback_mode && master_req_ready;
        readback_req_ready = readback_mode && master_req_ready;
        engine_rsp_valid = !readback_mode && master_rsp_valid;
        engine_rsp_rdata = readback_mode ? 32'd0 : master_rsp_rdata;
        engine_rsp_error = override_rsp_error_valid ? override_rsp_error_code :
                           (readback_mode ? 3'd0 : master_rsp_error);
        model_fault_valid = fault_inject_valid && !readback_mode && !mem_write &&
                            (expected_tap_index == fault_target_tap);
        model_fault_code = fault_inject_code;
        if (fault_on_write_mode && !readback_mode && mem_write) begin
            model_fault_valid = 1'b1;
            model_fault_code = 3'd6;
        end
        model_reset = hard_reset || abort;
    end

    s2a_memory_master u_master (
        .clk(clk), .hard_reset(hard_reset), .cancel(backend_cancel),
        .buffer_owner_pl(backend_owner_pl), .backend_req_valid(master_req_valid),
        .backend_req_ready(master_req_ready), .backend_req_write(master_req_write),
        .backend_req_addr(master_req_addr), .backend_req_wdata(master_req_wdata),
        .backend_req_rstrb(master_req_rstrb), .backend_req_wstrb(master_req_wstrb),
        .backend_rsp_valid(master_rsp_valid), .backend_rsp_rdata(master_rsp_rdata),
        .backend_rsp_error(master_rsp_error), .mem_valid(mem_valid),
        .mem_ready(model_ready), .mem_write(mem_write), .mem_addr(mem_addr),
        .mem_wdata(mem_wdata), .mem_rstrb(mem_rstrb), .mem_wstrb(mem_wstrb),
        .mem_rdata(model_rdata), .mem_error_code(model_error)
    );

    s2a_memory_model u_memory (
        .clk(clk), .reset(model_reset), .buffer_owner_pl(backend_owner_pl),
        .fault_inject_valid(model_fault_valid), .fault_inject_code(model_fault_code),
        .mem_valid(mem_valid), .mem_write(mem_write), .mem_addr(mem_addr),
        .mem_wdata(mem_wdata), .mem_rstrb(mem_rstrb), .mem_wstrb(mem_wstrb),
        .mem_ready(model_ready), .mem_rdata(model_rdata),
        .mem_error_code(model_error), .model_initialized(model_initialized)
    );

    always @(posedge clk) begin
        if (hard_reset || abort || !backend_owner_pl) begin
            outstanding = 0;
            held_memory_request = 1'b0;
        end else begin
            if (master_req_valid && master_req_ready) begin
                if (outstanding != 0) $fatal(1, "FAIL: multiple outstanding backend requests");
                outstanding = 1;
                accepted_backend_requests = accepted_backend_requests + 1;
            end
            if (master_rsp_valid) begin
                if (outstanding != 1) $fatal(1, "FAIL: unmatched backend response");
                outstanding = 0;
                backend_responses = backend_responses + 1;
            end
            if (held_memory_request &&
                (!mem_valid || mem_write !== held_write || mem_addr !== held_addr ||
                 mem_wdata !== held_wdata || mem_rstrb !== held_rstrb ||
                 mem_wstrb !== held_wstrb))
                $fatal(1, "FAIL: memory request changed during backpressure");
            if (mem_valid && !model_ready) begin
                held_memory_request = 1'b1; held_write = mem_write; held_addr = mem_addr;
                held_wdata = mem_wdata; held_rstrb = mem_rstrb; held_wstrb = mem_wstrb;
                memory_stall_cycles = memory_stall_cycles + 1;
            end else if (mem_valid && model_ready) begin
                held_memory_request = 1'b0;
                memory_handshakes = memory_handshakes + 1;
                if (readback_mode) begin
                    if (mem_write || mem_addr !== {expected_output_address[31:2], 2'b00} ||
                        mem_rstrb !== lane_mask(expected_output_address) || mem_wstrb != 0)
                        $fatal(1, "FAIL: readback address/strobe mismatch");
                    readback_checks = readback_checks + 1;
                end else if (mem_write) begin
                    if (mem_addr !== {expected_output_address[31:2], 2'b00} ||
                        mem_rstrb != 0 || mem_wstrb !== lane_mask(expected_output_address) ||
                        lane_value(mem_wdata, expected_output_address[1:0]) !== expected_output_byte)
                        $fatal(1, "FAIL: output write address/lane/value mismatch");
                    write_transfers = write_transfers + 1;
                end else begin
                    if (expected_tap_index >= expected_tap_count ||
                        mem_addr !== {expected_tap[expected_tap_index][31:2], 2'b00} ||
                        mem_rstrb !== lane_mask(expected_tap[expected_tap_index]) || mem_wstrb != 0)
                        $fatal(1, "FAIL: input tap order/lane mismatch at %0d", expected_tap_index);
                    expected_tap_index = expected_tap_index + 1;
                    input_read_transfers = input_read_transfers + 1;
                end
            end
        end
    end

    task automatic set_layer(input integer selected_layer);
        begin
            layer_index = selected_layer;
            kernel_height = 32'd2; kernel_width = 32'd2;
            stride_y = 32'd2; stride_x = 32'd2; darknet_padding_parameter = 32'd1;
            case (selected_layer)
                9: begin
                    input_base_address = 32'd21968896; input_length_bytes = 32'd1384448;
                    input_channels = 32'd128; input_height = 32'd104; input_width = 32'd104;
                    output_base_address = 32'd23353344; output_length_bytes = 32'd346112;
                    output_channels = 32'd128; output_height = 32'd52; output_width = 32'd52;
                end
                17: begin
                    input_base_address = 32'd25256960; input_length_bytes = 32'd692224;
                    input_channels = 32'd256; input_height = 32'd52; input_width = 32'd52;
                    output_base_address = 32'd25949184; output_length_bytes = 32'd173056;
                    output_channels = 32'd256; output_height = 32'd26; output_width = 32'd26;
                end
                25: begin
                    input_base_address = 32'd26900992; input_length_bytes = 32'd346112;
                    input_channels = 32'd512; input_height = 32'd26; input_width = 32'd26;
                    output_base_address = 32'd27247104; output_length_bytes = 32'd86528;
                    output_channels = 32'd512; output_height = 32'd13; output_width = 32'd13;
                end
                default: begin end
            endcase
        end
    endtask

    task automatic set_coordinate(input logic [31:0] channel_value,
                                  input logic [31:0] y_value,
                                  input logic [31:0] x_value);
        integer offset_value;
        begin
            output_channel = channel_value; output_y = y_value; output_x = x_value;
            offset_value = ((channel_value * output_height) + y_value) * output_width + x_value;
            expected_output_address = output_base_address + offset_value;
            offset_value = ((channel_value * input_height) + y_value * 2) * input_width + x_value * 2;
            expected_tap[0] = input_base_address + offset_value;
            expected_tap[1] = expected_tap[0] + 1;
            expected_tap[2] = expected_tap[0] + input_width;
            expected_tap[3] = expected_tap[2] + 1;
            expected_tap_count = 4;
            expected_output_byte = 8'd0;
        end
    endtask

    task automatic calculate_golden(output logic [2:0] err,
                                    output logic [7:0] value_byte);
        integer tap;
        integer signed signed_byte;
        integer signed maximum_byte;
        logic [7:0] raw_byte;
        begin
            err = 3'd0; maximum_byte = -128;
            for (tap = 0; tap < 4; tap = tap + 1) begin
                raw_byte = initial_byte(expected_tap[tap]);
                signed_byte = $signed(raw_byte);
                if (raw_byte == 8'h80) err = 3'd1;
                if (signed_byte > maximum_byte) maximum_byte = signed_byte;
            end
            value_byte = (err == 0) ? maximum_byte[7:0] : 8'd0;
        end
    endtask

    task automatic pulse_start;
        integer wait_count;
        begin
            @(negedge clk); start_valid = 1'b1; #1; wait_count = 0;
            while (!start_ready) begin
                @(negedge clk); #1; wait_count = wait_count + 1;
                if (wait_count > 100) $fatal(1, "FAIL: start_ready timeout");
            end
            @(posedge clk); @(negedge clk); start_valid = 1'b0;
        end
    endtask

    task automatic await_result(input logic [2:0] expected_error,
                                input logic [7:0] expected_byte);
        integer wait_count;
        logic [127:0] held_taps;
        logic [31:0] held_output;
        logic [7:0] held_value;
        logic [2:0] held_error;
        begin
            wait_count = 0;
            while (!result_valid) begin
                @(negedge clk); wait_count = wait_count + 1;
                if (wait_count > 10000) $fatal(1, "FAIL: result timeout");
            end
            if (result_error_code !== expected_error || result_value !== expected_byte ||
                result_output_address !== expected_output_address ||
                result_tap_addresses !== {expected_tap[3], expected_tap[2],
                                          expected_tap[1], expected_tap[0]})
                $fatal(1, "FAIL: result mismatch layer=%0d err=%0d/%0d value=%02h/%02h",
                       layer_index, result_error_code, expected_error, result_value, expected_byte);
            held_taps = result_tap_addresses; held_output = result_output_address;
            held_value = result_value; held_error = result_error_code;
            repeat (3) begin
                @(negedge clk);
                if (!result_valid || result_tap_addresses !== held_taps ||
                    result_output_address !== held_output || result_value !== held_value ||
                    result_error_code !== held_error)
                    $fatal(1, "FAIL: result unstable before result_ready");
            end
            result_ready = 1'b1; @(posedge clk); @(negedge clk); result_ready = 1'b0;
            if (result_valid) $fatal(1, "FAIL: result repeated after handshake");
        end
    endtask

    task automatic readback_byte(input logic [31:0] address,
                                 input logic [7:0] expected_byte,
                                 input logic check_expected,
                                 output logic [7:0] observed_byte);
        integer wait_count;
        logic [31:0] response_word;
        begin
            expected_output_address = address;
            @(negedge clk); readback_mode = 1'b1;
            readback_req_addr = {address[31:2], 2'b00};
            readback_req_rstrb = lane_mask(address); readback_req_valid = 1'b1; #1;
            wait_count = 0;
            while (!readback_req_ready) begin
                @(negedge clk); #1; wait_count = wait_count + 1;
                if (wait_count > 100) $fatal(1, "FAIL: readback request timeout");
            end
            @(posedge clk); @(negedge clk); readback_req_valid = 1'b0;
            wait_count = 0;
            while (!master_rsp_valid) begin
                @(negedge clk); wait_count = wait_count + 1;
                if (wait_count > 200) $fatal(1, "FAIL: readback response timeout");
            end
            response_word = master_rsp_rdata;
            observed_byte = lane_value(response_word, address[1:0]);
            if (master_rsp_error != 0 ||
                (check_expected && observed_byte !== expected_byte))
                $fatal(1, "FAIL: readback mismatch address=%0d got=%02h expected=%02h",
                       address, observed_byte, expected_byte);
            @(negedge clk); readback_mode = 1'b0;
            readback_req_addr = 32'd0; readback_req_rstrb = 4'd0;
        end
    endtask

    task automatic run_one(input logic [2:0] expected_error,
                           input logic [7:0] expected_byte,
                           input logic do_readback);
        integer writes_before;
        integer reads_before;
        begin
            expected_output_byte = expected_byte; expected_tap_index = 0;
            writes_before = write_transfers; reads_before = input_read_transfers;
            pulse_start(); await_result(expected_error, expected_byte);
            if (expected_tap_index != 4) $fatal(1, "FAIL: did not read all four taps");
            if (expected_error == 0) begin
                if (write_transfers != writes_before + 1)
                    $fatal(1, "FAIL: successful result did not write once");
                if (do_readback) begin
                    readback_byte(expected_output_address, expected_byte, 1'b1, observed_value);
                    if (observed_value !== expected_byte) $fatal(1, "FAIL: output readback mismatch");
                end
            end else if (write_transfers != writes_before) begin
                $fatal(1, "FAIL: invalid T10 byte caused output write");
            end
            if (input_read_transfers != reads_before + 4)
                $fatal(1, "FAIL: expected four source reads");
        end
    endtask

    task automatic run_invalid(input logic [2:0] expected_error);
        integer handshakes_before;
        begin
            expected_output_address = 32'd0;
            expected_tap[0] = 32'd0; expected_tap[1] = 32'd0;
            expected_tap[2] = 32'd0; expected_tap[3] = 32'd0;
            expected_tap_count = 0; expected_tap_index = 0; expected_output_byte = 8'd0;
            handshakes_before = memory_handshakes;
            pulse_start(); await_result(expected_error, 8'd0);
            if (memory_handshakes != handshakes_before)
                $fatal(1, "FAIL: invalid request accessed memory");
            invalid_checks = invalid_checks + 1;
        end
    endtask

    task automatic run_read_fault(input logic [2:0] injected_code,
                                  input integer target_tap,
                                  input logic use_override,
                                  input logic [2:0] expected_error);
        integer writes_before;
        begin
            set_layer(9); set_coordinate(32'd0, 32'd0, 32'd0);
            expected_tap_index = 0; expected_tap_count = target_tap + 1;
            expected_output_byte = 8'd0; writes_before = write_transfers;
            fault_target_tap = target_tap;
            if (use_override) begin
                override_rsp_error_valid = 1'b1;
                override_rsp_error_code = injected_code;
            end else begin
                fault_inject_valid = 1'b1; fault_inject_code = injected_code;
            end
            pulse_start(); await_result(expected_error, 8'd0);
            fault_inject_valid = 1'b0; override_rsp_error_valid = 1'b0;
            override_rsp_error_code = 3'd0;
            if (expected_tap_index != target_tap + 1 || write_transfers != writes_before)
                $fatal(1, "FAIL: read error did not stop taps or suppressed write");
            if (use_override) response_override_checks = response_override_checks + 1;
            else raw_fault_checks = raw_fault_checks + 1;
        end
    endtask

    task automatic run_write_fault;
        integer writes_before;
        begin
            set_layer(9); set_coordinate(32'd0, 32'd0, 32'd0);
            calculate_golden(golden_error, golden_value);
            if (golden_error != 0) $fatal(1, "FAIL: write fault vector must be legal");
            readback_byte(expected_output_address, 8'd0, 1'b0, prior_value);
            expected_output_byte = golden_value; expected_tap_index = 0;
            writes_before = write_transfers; fault_on_write_mode = 1'b1;
            pulse_start(); await_result(3'd6, 8'd0); fault_on_write_mode = 1'b0;
            if (expected_tap_index != 4 || write_transfers != writes_before + 1)
                $fatal(1, "FAIL: failed output write was not observed");
            readback_byte(expected_output_address, prior_value, 1'b1, observed_value);
            if (observed_value !== prior_value) $fatal(1, "FAIL: failed write changed output byte");
            write_fault_checks = write_fault_checks + 1;
        end
    endtask

    task automatic wait_stalled_request(input logic expected_write);
        integer wait_count;
        begin
            wait_count = 0;
            while (!(mem_valid && !model_ready && (mem_write == expected_write))) begin
                @(negedge clk); wait_count = wait_count + 1;
                if (wait_count > 10000) $fatal(1, "FAIL: expected stalled request not reached");
            end
            @(posedge clk); @(negedge clk);
            if (!mem_valid || model_ready || !held_memory_request || !u_memory.pending)
                $fatal(1, "FAIL: T10/T12 did not retain stalled request");
        end
    endtask

    task automatic cancel_pending(input logic expected_write,
                                  input logic use_hard_reset);
        integer writes_before;
        integer loops;
        begin
            set_layer(9); set_coordinate(32'd0, 32'd0, 32'd0);
            calculate_golden(golden_error, golden_value);
            if (golden_error != 0) $fatal(1, "FAIL: cancellation source window invalid");
            expected_output_byte = golden_value;
            readback_byte(expected_output_address, 8'd0, 1'b0, prior_value);
            if (expected_write) begin
                loops = 0;
                while (u_memory.stall_index[3] != 3) begin
                    run_one(3'd0, golden_value, 1'b1);
                    loops = loops + 1;
                    if (loops > 8) $fatal(1, "FAIL: cannot align write stall slot");
                end
            end else begin
                while (u_memory.stall_index[2] != 3)
                    readback_byte(expected_output_address, 8'd0, 1'b0, observed_value);
            end
            expected_tap_index = 0; expected_tap_count = 4;
            writes_before = write_transfers;
            pulse_start(); loops = 0;
            if (expected_write) begin
                while (!(mem_valid && mem_write && !model_ready)) begin
                    @(negedge clk); loops = loops + 1;
                    if (loops > 10000) $fatal(1, "FAIL: output pending write not reached");
                end
                wait_stalled_request(1'b1);
            end else begin
                wait_stalled_request(1'b0);
            end
            if (use_hard_reset) hard_reset = 1'b1;
            else abort = 1'b1;
            #1;
            if (mem_valid || master_rsp_valid || engine_rsp_valid)
                $fatal(1, "FAIL: cancel/reset did not withdraw request");
            @(posedge clk); @(negedge clk);
            hard_reset = 1'b0; abort = 1'b0; #1;
            if (result_valid || !start_ready || mem_valid || master_rsp_valid ||
                u_master.pending || u_memory.pending)
                $fatal(1, "FAIL: cancel/reset left stale result or did not recover");
            if (write_transfers != writes_before)
                $fatal(1, "FAIL: canceled transaction reached output write");
            if (expected_write) begin
                readback_byte(expected_output_address, prior_value, 1'b1, observed_value);
                if (observed_value !== prior_value) $fatal(1, "FAIL: canceled write changed memory");
            end
            run_one(3'd0, golden_value, 1'b1); recovery_checks = recovery_checks + 1;
            if (expected_write && use_hard_reset) write_reset_checks = write_reset_checks + 1;
            else if (expected_write) write_abort_checks = write_abort_checks + 1;
            else if (use_hard_reset) read_reset_checks = read_reset_checks + 1;
            else read_abort_checks = read_abort_checks + 1;
        end
    endtask

    task automatic run_owner_gate;
        begin
            set_layer(9); set_coordinate(32'd0, 32'd0, 32'd0);
            backend_owner_pl = 1'b0; pulse_start();
            repeat (4) begin
                @(negedge clk);
                if (mem_valid || master_req_ready || engine_req_ready)
                    $fatal(1, "FAIL: memory owner gate allowed a PL request");
            end
            abort = 1'b1; #1;
            if (mem_valid || master_rsp_valid) $fatal(1, "FAIL: owner wait abort failed");
            @(posedge clk); @(negedge clk);
            abort = 1'b0; backend_owner_pl = 1'b1; ownership_checks = ownership_checks + 1;
            set_layer(9); set_coordinate(32'd0, 32'd0, 32'd0);
            calculate_golden(golden_error, golden_value);
            run_one(golden_error, golden_value, golden_error == 0);
            recovery_checks = recovery_checks + 1;
        end
    endtask

    initial begin : run_official_and_protocol_tests
        integer handshakes_before;
        integer layer_slot;
        hard_reset = 1'b1; abort = 1'b0; start_valid = 1'b0; result_ready = 1'b0;
        backend_owner_pl = 1'b1; readback_mode = 1'b0;
        readback_req_valid = 1'b0; readback_req_addr = 32'd0; readback_req_rstrb = 4'd0;
        fault_inject_valid = 1'b0; fault_inject_code = 3'd0; fault_target_tap = 0;
        fault_on_write_mode = 1'b0; override_rsp_error_valid = 1'b0;
        override_rsp_error_code = 3'd0;
        expected_output_address = 32'd0; expected_output_byte = 8'd0;
        expected_tap_count = 0; expected_tap_index = 0;
        for (k = 0; k < 4; k = k + 1) begin
            expected_tap[k] = 32'd0; vector_tap[k] = 32'd0;
        end
        input_read_transfers = 0; write_transfers = 0; readback_checks = 0;
        accepted_backend_requests = 0; backend_responses = 0; memory_handshakes = 0;
        memory_stall_cycles = 0; outstanding = 0; held_memory_request = 1'b0;
        raw_fault_checks = 0; response_override_checks = 0; write_fault_checks = 0;
        invalid_checks = 0; read_abort_checks = 0; read_reset_checks = 0;
        write_abort_checks = 0; write_reset_checks = 0; recovery_checks = 0;
        ownership_checks = 0; official_random = 0; official_directed = 0;
        official_queries = 0; official_legal = 0; official_raw_80 = 0; vector_count = 0;
        for (layer_slot = 0; layer_slot < 3; layer_slot = layer_slot + 1) begin
            random_counts[layer_slot] = 0; directed_counts[layer_slot] = 0;
        end

        wait (model_initialized);
        repeat (3) @(posedge clk);
        @(negedge clk); hard_reset = 1'b0;

        set_layer(9); set_coordinate(32'd0, 32'd0, 32'd0);
        layer_index = 32'd10; run_invalid(3'd1);
        set_layer(9); set_coordinate(32'd0, 32'd0, 32'd0);
        kernel_width = 32'd3; run_invalid(3'd1);
        set_layer(9); set_coordinate(32'd0, 32'd52, 32'd0); run_invalid(3'd1);
        set_layer(9); set_coordinate(32'd0, 32'd0, 32'd0);
        input_length_bytes = input_length_bytes - 1; run_invalid(3'd3);
        set_layer(9); set_coordinate(32'd0, 32'd0, 32'd0);
        output_length_bytes = output_length_bytes - 1; run_invalid(3'd3);
        set_layer(9); set_coordinate(32'd0, 32'd0, 32'd0);
        input_base_address = input_base_address + 4; run_invalid(3'd2);
        set_layer(9); set_coordinate(32'd0, 32'd0, 32'd0);
        output_base_address = output_base_address + 4; run_invalid(3'd2);

        vector_fd = $fopen("engine_vectors.dat", "r");
        if (vector_fd == 0) $fatal(1, "FAIL: cannot open engine_vectors.dat");
        scan_result = $fscanf(vector_fd,
            "%d %d %d %d %d %d %h %h %h %h %d %d %d %d\n",
            vector_class, vector_layer, vector_case, vector_channel, vector_y, vector_x,
            vector_tap[0], vector_tap[1], vector_tap[2], vector_tap[3],
            vector_candidate0, vector_candidate1, vector_candidate2, vector_candidate3);
        official_reads_before = input_read_transfers;
        official_writes_before = write_transfers;
        official_readbacks_before = readback_checks;
        while (scan_result == 14) begin
            if ((vector_class != 0 && vector_class != 1) ||
                (vector_layer != 9 && vector_layer != 17 && vector_layer != 25))
                $fatal(1, "FAIL: non-model vector in official stream");
            set_layer(vector_layer);
            set_coordinate(vector_channel, vector_y, vector_x);
            for (k = 0; k < 4; k = k + 1)
                if (vector_tap[k] !== expected_tap[k])
                    $fatal(1, "FAIL: T04 tap does not match NCHW model geometry");
            if (vector_candidate0 < -127 || vector_candidate0 > 127 ||
                vector_candidate1 < -127 || vector_candidate1 > 127 ||
                vector_candidate2 < -127 || vector_candidate2 > 127 ||
                vector_candidate3 < -127 || vector_candidate3 > 127)
                $fatal(1, "FAIL: G0 candidate value outside symmetric INT8");
            calculate_golden(golden_error, golden_value);
            expected_output_byte = golden_value;
            run_one(golden_error, golden_value, golden_error == 0);
            if (golden_error == 0) official_legal = official_legal + 1;
            else official_raw_80 = official_raw_80 + 1;
            if (vector_class == 0) begin
                official_random = official_random + 1;
                case (vector_layer)
                    9: random_counts[0] = random_counts[0] + 1;
                    17: random_counts[1] = random_counts[1] + 1;
                    25: random_counts[2] = random_counts[2] + 1;
                endcase
            end else begin
                official_directed = official_directed + 1;
                case (vector_layer)
                    9: directed_counts[0] = directed_counts[0] + 1;
                    17: directed_counts[1] = directed_counts[1] + 1;
                    25: directed_counts[2] = directed_counts[2] + 1;
                endcase
            end
            official_queries = official_queries + 1;
            vector_count = vector_count + 1;
            scan_result = $fscanf(vector_fd,
                "%d %d %d %d %d %d %h %h %h %h %d %d %d %d\n",
                vector_class, vector_layer, vector_case, vector_channel, vector_y, vector_x,
                vector_tap[0], vector_tap[1], vector_tap[2], vector_tap[3],
                vector_candidate0, vector_candidate1, vector_candidate2, vector_candidate3);
        end
        if (scan_result != -1) $fatal(1, "FAIL: malformed engine_vectors.dat");
        $fclose(vector_fd);
        official_input_reads = input_read_transfers - official_reads_before;
        official_writes = write_transfers - official_writes_before;
        official_readbacks = readback_checks - official_readbacks_before;
        if (vector_count != 3048 || official_random != 3000 || official_directed != 48 ||
            official_queries != 3048 || random_counts[0] != 1000 ||
            random_counts[1] != 1000 || random_counts[2] != 1000 ||
            directed_counts[0] != 16 || directed_counts[1] != 16 || directed_counts[2] != 16 ||
            official_input_reads != 12192 || official_writes != official_legal ||
            official_readbacks != official_legal || official_legal + official_raw_80 != 3048)
            $fatal(1, "FAIL: official per-layer query and transfer counts mismatch");

        run_read_fault(3'd6, 0, 1'b0, 3'd6);
        run_read_fault(3'd7, 2, 1'b0, 3'd6);
        run_read_fault(3'd1, 0, 1'b1, 3'd1);
        run_read_fault(3'd2, 0, 1'b1, 3'd2);
        run_read_fault(3'd7, 0, 1'b1, 3'd6);
        run_write_fault();

        cancel_pending(1'b0, 1'b0);
        cancel_pending(1'b0, 1'b1);
        cancel_pending(1'b1, 1'b0);
        cancel_pending(1'b1, 1'b1);
        run_owner_gate();

        if (accepted_backend_requests != backend_responses + 4 ||
            backend_responses != memory_handshakes || outstanding != 0 ||
            raw_fault_checks != 2 || response_override_checks != 3 ||
            write_fault_checks != 1 || invalid_checks != 7 || recovery_checks != 5 ||
            ownership_checks != 1 || read_abort_checks != 1 || read_reset_checks != 1 ||
            write_abort_checks != 1 || write_reset_checks != 1 || memory_stall_cycles < 1000)
            $fatal(1, "FAIL: error/cancel/stall accounting mismatch");
        $display("RESULT random=%0d directed=%0d queries=%0d legal=%0d raw80=%0d official_input_reads=%0d official_writes=%0d official_readbacks=%0d invalid=%0d raw_fault=%0d override=%0d write_fault=%0d read_abort=%0d read_reset=%0d write_abort=%0d write_reset=%0d recovery=%0d owner=%0d accepted=%0d responses=%0d handshakes=%0d stall_cycles=%0d",
                 official_random, official_directed, official_queries, official_legal,
                 official_raw_80, official_input_reads, official_writes, official_readbacks,
                 invalid_checks, raw_fault_checks, response_override_checks, write_fault_checks,
                 read_abort_checks, read_reset_checks, write_abort_checks, write_reset_checks,
                 recovery_checks, ownership_checks, accepted_backend_requests, backend_responses,
                 memory_handshakes, memory_stall_cycles);
        $display("PASS S2A-T14 maxpool official model coordinates and T10/T12 memory protocol");
        $finish;
    end
endmodule
