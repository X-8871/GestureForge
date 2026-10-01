// S2A-T68：单样本完整网络逐层 INT8 golden memory harness。
`timescale 1ns/1ps
module tb_s2a_network_backend_golden;
    import s2a_network_descriptor_pkg::*;

    localparam logic [2:0] NONE = 3'd0;
    localparam logic [2:0] BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] BAD_RANGE = 3'd2;
    localparam logic [2:0] INTERNAL = 3'd6;

    localparam integer INPUT_BYTE_COUNT = 519168;
    localparam integer WEIGHT_BYTE_COUNT = 5903100;
    localparam integer FEATURE_BASE_ADDRESS = 32'h01000000;
    localparam integer FEATURE_WORKSPACE_BYTES = 11382200;
    localparam integer GOLDEN_BYTE_COUNT = 11382150;
    localparam integer TRANSFER_CLASS_COUNT = 4;
    localparam integer INPUT_READ_CLASS = 0;
    localparam integer WEIGHT_READ_CLASS = 1;
    localparam integer FEATURE_READ_CLASS = 2;
    localparam integer FEATURE_WRITE_CLASS = 3;
    localparam longint unsigned DEFAULT_MAX_CYCLES = 64'd4294967295;
    localparam longint unsigned PROGRESS_INTERVAL_CYCLES = 64'd30000000;

    logic clk = 1'b0;
    logic hard_reset = 1'b1;
    logic abort = 1'b0;
    logic backend_start = 1'b0;
    logic buffer_owner_pl = 1'b0;
    logic [31:0] input_base_address = 32'h00000000;
    logic [31:0] input_length_bytes = INPUT_BYTE_COUNT;
    logic [31:0] weight_package_base_address = 32'h00100000;
    logic [31:0] weight_package_length_bytes = WEIGHT_BYTE_COUNT;
    logic mem_valid;
    logic mem_write;
    logic [31:0] mem_addr;
    logic [31:0] mem_wdata;
    logic [3:0] mem_rstrb;
    logic [3:0] mem_wstrb;
    logic mem_ready;
    logic [31:0] mem_rdata;
    logic [2:0] mem_error_code;
    logic backend_memory_error_valid;
    logic [2:0] backend_memory_error_code;
    logic operator_result_valid;
    logic [2:0] operator_error_code;

    byte unsigned input_bytes [0:INPUT_BYTE_COUNT-1];
    byte unsigned weight_bytes [0:WEIGHT_BYTE_COUNT-1];
    byte unsigned feature_bytes [0:FEATURE_WORKSPACE_BYTES-1];
    byte unsigned feature_byte_valid [0:FEATURE_WORKSPACE_BYTES-1];
    byte unsigned expected_bytes [0:GOLDEN_BYTE_COUNT-1];
    byte unsigned golden_byte_seen [0:GOLDEN_BYTE_COUNT-1];

    string fixture_dir;
    string input_fixture_path;
    string weight_fixture_path;
    string golden_fixture_path;
    string result_file_path;
    string progress_file_path;
    integer sample_index = -1;
    longint unsigned max_cycles = DEFAULT_MAX_CYCLES;
    longint unsigned cycle_count = 0;
    longint unsigned next_progress_cycle = PROGRESS_INTERVAL_CYCLES;
    integer golden_offset [0:S2A_LAYER_COUNT-1];
    integer layer_write_count [0:S2A_LAYER_COUNT-1];
    integer class_transfer_index [0:TRANSFER_CLASS_COUNT-1];
    integer class_wait_count = 0;
    integer class_accepted_count [0:TRANSFER_CLASS_COUNT-1];
    integer class_selected_byte_count [0:TRANSFER_CLASS_COUNT-1];
    integer golden_cursor = 0;
    integer loaded_byte_count;
    integer file_id;
    integer extra_byte;
    integer init_index;
    integer comb_lane;
    integer verify_layer;
    integer verify_offset;
    integer seq_lane;
    integer comb_owner;
    integer comb_tensor_owner;
    integer comb_transfer_class;
    integer comb_feature_index;
    integer comb_byte_index;
    integer seq_owner;
    integer seq_lane_owner;
    integer seq_tensor_owner;
    integer seq_transfer_class;
    integer seq_golden_index;
    integer verify_golden_index;
    integer seq_feature_index;
    integer input_bytes_this_transfer;
    integer weight_bytes_this_transfer;
    integer feature_bytes_this_transfer;
    integer active_byte_count;
    integer delay_count;
    logic stalled_previous = 1'b0;
    logic [31:0] stalled_address = 32'd0;
    logic [31:0] stalled_data = 32'd0;
    logic stalled_write = 1'b0;
    logic [3:0] stalled_rstrb = 4'd0;
    logic [3:0] stalled_wstrb = 4'd0;
    logic [31:0] comb_lane_address;
    logic [31:0] seq_lane_address;
    logic [31:0] cross_boundary_test_address;
    logic [3:0] cross_boundary_test_strobe;
    integer total_feature_write_bytes = 0;
    integer total_memory_read_bytes = 0;
    integer total_input_read_bytes = 0;
    integer total_weight_read_bytes = 0;
    integer total_feature_read_bytes = 0;
    integer total_memory_write_transactions = 0;
    integer total_memory_read_transactions = 0;
    logic [31:0] total_mismatches = 32'd0;

    always #5 clk = ~clk;

    function automatic integer memory_tensor_owner(input logic [31:0] address);
        integer layer_index;
        begin
            memory_tensor_owner = -1;
            if ((address >= input_base_address) &&
                (address < input_base_address + input_length_bytes)) begin
                memory_tensor_owner = 0;
            end else if ((address >= weight_package_base_address) &&
                         (address < weight_package_base_address + weight_package_length_bytes)) begin
                memory_tensor_owner = 1;
            end else begin
                for (layer_index = 0; layer_index < S2A_LAYER_COUNT; layer_index = layer_index + 1) begin
                    if (S2A_OUTPUT_MEMORY_WRITE_REQUIRED[layer_index] &&
                        (address >= S2A_OUTPUT_ADDRESS[layer_index]) &&
                        (address < S2A_OUTPUT_ADDRESS[layer_index] + S2A_OUTPUT_LENGTH_BYTES[layer_index])) begin
                        memory_tensor_owner = layer_index + 2;
                    end
                end
            end
        end
    endfunction

    function automatic logic [2:0] validate_read_request(input logic [31:0] request_address,
                                                         input logic [3:0] read_strobe);
        integer lane;
        integer first_owner;
        integer lane_owner;
        logic [31:0] byte_address;
        begin
            validate_read_request = NONE;
            if (request_address[1:0] != 2'b00) begin
                validate_read_request = BAD_RANGE;
            end else if (read_strobe == 4'b0000) begin
                validate_read_request = BAD_ARGUMENT;
            end else begin
                first_owner = -1;
                for (lane = 0; lane < 4; lane = lane + 1) begin
                    if (read_strobe[lane]) begin
                        byte_address = request_address + lane;
                        lane_owner = memory_tensor_owner(byte_address);
                        if (lane_owner < 0) begin
                            validate_read_request = BAD_RANGE;
                        end else if (first_owner < 0) begin
                            first_owner = lane_owner;
                        end else if (lane_owner != first_owner) begin
                            validate_read_request = BAD_RANGE;
                        end
                    end
                end
            end
        end
    endfunction

    function automatic logic is_onehot4(input logic [3:0] value);
        begin
            case (value)
                4'b0001, 4'b0010, 4'b0100, 4'b1000: is_onehot4 = 1'b1;
                default: is_onehot4 = 1'b0;
            endcase
        end
    endfunction

    function automatic integer classify_transfer(input logic write_request,
                                                   input logic [31:0] address,
                                                   input logic [3:0] read_strobe);
        integer lane;
        integer selected_lane;
        integer lane_owner;
        integer found_lane;
        logic [31:0] selected_address;
        begin
            if (write_request) begin
                classify_transfer = FEATURE_WRITE_CLASS;
            end else begin
                selected_lane = 0;
                found_lane = 0;
                for (lane = 0; lane < 4; lane = lane + 1) begin
                    if (read_strobe[lane] && !found_lane) begin
                        selected_lane = lane;
                        found_lane = 1;
                    end
                end
                selected_address = address + selected_lane;
                lane_owner = memory_tensor_owner(selected_address);
                if (lane_owner == 0) begin
                    classify_transfer = INPUT_READ_CLASS;
                end else if (lane_owner == 1) begin
                    classify_transfer = WEIGHT_READ_CLASS;
                end else begin
                    classify_transfer = FEATURE_READ_CLASS;
                end
            end
        end
    endfunction

    task automatic emit_progress(input string phase_name);
        integer progress_marker_file_id;
        begin
            progress_marker_file_id = $fopen(progress_file_path, "a");
            if (progress_marker_file_id == 0) begin
                $fatal(1, "T68 无法追加 progress marker：%s", progress_file_path);
            end
            $fdisplay(progress_marker_file_id,
                      "S2A_PROGRESS sample=%0d layer=%0d cycle=%0d output=%0d conv_tile_y=%0d conv_tile_x=%0d conv_group=%0d conv_point=%0d conv_reduction=%0d conv_feature_scan=%0d conv_weight_reduction=%0d conv_output_lane=%0d conv_output_point=%0d pool_tap=%0d feature_write_bytes=%0d read_transactions=%0d write_transactions=%0d phase=%s",
                      sample_index, u_backend.layer_cursor, cycle_count, u_backend.output_element_index,
                      u_backend.u_conv_engine.tile_start_y, u_backend.u_conv_engine.tile_start_x,
                      u_backend.u_conv_engine.output_group_base, u_backend.u_conv_engine.compute_point_index,
                      u_backend.u_conv_engine.compute_reduction_index, u_backend.u_conv_engine.feature_scan_index,
                      u_backend.u_conv_engine.weight_reduction_index, u_backend.u_conv_engine.output_lane_index,
                      u_backend.u_conv_engine.output_point_index, u_backend.u_maxpool_engine.read_tap_index,
                      total_feature_write_bytes, total_memory_read_transactions,
                      total_memory_write_transactions, phase_name);
            $fflush(progress_marker_file_id);
            $fclose(progress_marker_file_id);
            $display("S2A_PROGRESS sample=%0d layer=%0d cycle=%0d output=%0d conv_tile_y=%0d conv_tile_x=%0d conv_group=%0d conv_point=%0d conv_reduction=%0d conv_feature_scan=%0d conv_weight_reduction=%0d conv_output_lane=%0d conv_output_point=%0d pool_tap=%0d feature_write_bytes=%0d read_transactions=%0d write_transactions=%0d phase=%s",
                     sample_index, u_backend.layer_cursor, cycle_count, u_backend.output_element_index,
                     u_backend.u_conv_engine.tile_start_y, u_backend.u_conv_engine.tile_start_x,
                     u_backend.u_conv_engine.output_group_base, u_backend.u_conv_engine.compute_point_index,
                     u_backend.u_conv_engine.compute_reduction_index, u_backend.u_conv_engine.feature_scan_index,
                     u_backend.u_conv_engine.weight_reduction_index, u_backend.u_conv_engine.output_lane_index,
                     u_backend.u_conv_engine.output_point_index, u_backend.u_maxpool_engine.read_tap_index,
                     total_feature_write_bytes, total_memory_read_transactions,
                     total_memory_write_transactions, phase_name);
            $fflush();
        end
    endtask

    function automatic integer fixed_stall_delay(input integer transfer_index);
        begin
            case (transfer_index % 5)
                0: fixed_stall_delay = 0;
                1: fixed_stall_delay = 1;
                2: fixed_stall_delay = 2;
                3: fixed_stall_delay = 7;
                default: fixed_stall_delay = 3;
            endcase
        end
    endfunction

    function automatic integer owned_output_layer(input logic [31:0] address);
        integer layer_index;
        begin
            owned_output_layer = -1;
            for (layer_index = 0; layer_index < S2A_LAYER_COUNT; layer_index = layer_index + 1) begin
                if (S2A_OUTPUT_MEMORY_WRITE_REQUIRED[layer_index] &&
                    (address >= S2A_OUTPUT_ADDRESS[layer_index]) &&
                    (address < S2A_OUTPUT_ADDRESS[layer_index] + S2A_OUTPUT_LENGTH_BYTES[layer_index])) begin
                    owned_output_layer = layer_index;
                end
            end
        end
    endfunction

    always_comb begin
        mem_ready = !hard_reset && buffer_owner_pl;
        mem_rdata = 32'd0;
        mem_error_code = NONE;
        comb_transfer_class = FEATURE_READ_CLASS;
        delay_count = 0;
        comb_owner = -1;
        comb_tensor_owner = -1;
        comb_feature_index = 0;
        comb_byte_index = -1;
        comb_lane_address = 32'd0;
        if (mem_valid) begin
            comb_transfer_class = classify_transfer(mem_write, mem_addr, mem_rstrb);
            delay_count = fixed_stall_delay(class_transfer_index[comb_transfer_class]);
            if (class_wait_count < delay_count) begin
                mem_ready = 1'b0;
            end
        end

        if (mem_valid) begin
            if (mem_addr[1:0] != 2'b00) begin
                mem_error_code = BAD_RANGE;
            end else if (mem_write) begin
                if ((mem_rstrb != 4'b0000) || (mem_wstrb == 4'b0000)) begin
                    mem_error_code = BAD_ARGUMENT;
                end else begin
                    for (comb_lane = 0; comb_lane < 4; comb_lane = comb_lane + 1) begin
                        if (mem_wstrb[comb_lane]) begin
                            comb_lane_address = mem_addr + comb_lane;
                            comb_byte_index = owned_output_layer(comb_lane_address);
                            if (comb_byte_index < 0) begin
                                mem_error_code = BAD_RANGE;
                            end
                        end
                    end
                end
            end else if (mem_wstrb != 4'b0000) begin
                mem_error_code = BAD_ARGUMENT;
            end else begin
                mem_error_code = validate_read_request(mem_addr, mem_rstrb);
                if (mem_error_code == NONE) begin
                    for (comb_lane = 0; comb_lane < 4; comb_lane = comb_lane + 1) begin
                        if (mem_rstrb[comb_lane]) begin
                            comb_lane_address = mem_addr + comb_lane;
                            comb_tensor_owner = memory_tensor_owner(comb_lane_address);
                            if (comb_tensor_owner == 0) begin
                                mem_rdata[(comb_lane * 8) +: 8] = input_bytes[comb_lane_address - input_base_address];
                            end else if (comb_tensor_owner == 1) begin
                                mem_rdata[(comb_lane * 8) +: 8] = weight_bytes[comb_lane_address - weight_package_base_address];
                            end else begin
                                comb_owner = comb_tensor_owner - 2;
                                comb_feature_index = comb_lane_address - FEATURE_BASE_ADDRESS;
                                if (!feature_byte_valid[comb_feature_index]) begin
                                    mem_error_code = INTERNAL;
                                end else begin
                                    mem_rdata[(comb_lane * 8) +: 8] = feature_bytes[comb_feature_index];
                                end
                            end
                        end
                    end
                end
            end
        end
    end

    s2a_network_backend u_backend (
        .clk(clk),
        .hard_reset(hard_reset),
        .abort(abort),
        .backend_start(backend_start),
        .buffer_owner_pl(buffer_owner_pl),
        .input_base_address(input_base_address),
        .input_length_bytes(input_length_bytes),
        .weight_package_base_address(weight_package_base_address),
        .weight_package_length_bytes(weight_package_length_bytes),
        .mem_valid(mem_valid),
        .mem_write(mem_write),
        .mem_addr(mem_addr),
        .mem_wdata(mem_wdata),
        .mem_rstrb(mem_rstrb),
        .mem_wstrb(mem_wstrb),
        .mem_ready(mem_ready),
        .mem_rdata(mem_rdata),
        .mem_error_code(mem_error_code),
        .backend_memory_error_valid(backend_memory_error_valid),
        .backend_memory_error_code(backend_memory_error_code),
        .operator_result_valid(operator_result_valid),
        .operator_error_code(operator_error_code)
    );

    initial begin : run_golden
        fixture_dir = "";
        result_file_path = "";
        progress_file_path = "";
        if (!$value$plusargs("SAMPLE_INDEX=%d", sample_index)) begin
            $fatal(1, "T68 缺少 +SAMPLE_INDEX=0..108");
        end
        if ((sample_index < 0) || (sample_index > 108)) begin
            $fatal(1, "T68 sample index 超出 0..108：%0d", sample_index);
        end
        if (!$value$plusargs("FIXTURE_DIR=%s", fixture_dir)) begin
            $fatal(1, "T68 缺少 +FIXTURE_DIR");
        end
        if (!$value$plusargs("RESULT_FILE=%s", result_file_path)) begin
            $fatal(1, "T68 缺少 +RESULT_FILE");
        end
        if (!$value$plusargs("PROGRESS_FILE=%s", progress_file_path)) begin
            $fatal(1, "T68 缺少 +PROGRESS_FILE");
        end
        if (!$value$plusargs("MAX_CYCLES=%d", max_cycles)) begin
            max_cycles = DEFAULT_MAX_CYCLES;
        end
        if (max_cycles == 0) begin
            $fatal(1, "T68 MAX_CYCLES 必须大于 0");
        end

        input_fixture_path = $sformatf("%s\\input_chw_int8.bin", fixture_dir);
        weight_fixture_path = $sformatf("%s\\..\\common\\weights.gf8", fixture_dir);
        golden_fixture_path = $sformatf("%s\\golden_unique.bin", fixture_dir);

        for (init_index = 0; init_index < S2A_LAYER_COUNT; init_index = init_index + 1) begin
            golden_offset[init_index] = golden_cursor;
            layer_write_count[init_index] = 0;
            class_transfer_index[init_index % TRANSFER_CLASS_COUNT] = 0;
            if (S2A_OUTPUT_MEMORY_WRITE_REQUIRED[init_index]) begin
                golden_cursor = golden_cursor + S2A_OUTPUT_LENGTH_BYTES[init_index];
            end
        end
        for (init_index = 0; init_index < TRANSFER_CLASS_COUNT; init_index = init_index + 1) begin
            class_transfer_index[init_index] = 0;
            class_accepted_count[init_index] = 0;
            class_selected_byte_count[init_index] = 0;
        end
        if (golden_cursor != GOLDEN_BYTE_COUNT) begin
            $fatal(1, "T68 descriptor unique byte count 错误：%0d", golden_cursor);
        end
        cross_boundary_test_address =
            (S2A_OUTPUT_ADDRESS[29] + S2A_OUTPUT_LENGTH_BYTES[29] - 1) & 32'hffff_fffc;
        cross_boundary_test_strobe = 4'b0101;
        if ((memory_tensor_owner(cross_boundary_test_address) != 31) ||
            (memory_tensor_owner(cross_boundary_test_address + 2) >= 0) ||
            (validate_read_request(cross_boundary_test_address, cross_boundary_test_strobe) != BAD_RANGE)) begin
            $fatal(1, "T68 跨 tensor 尾部负向检查未拒绝非法 read lane：addr=%08h strobe=%b",
                   cross_boundary_test_address, cross_boundary_test_strobe);
        end
        for (init_index = 0; init_index < FEATURE_WORKSPACE_BYTES; init_index = init_index + 1) begin
            feature_bytes[init_index] = 8'd0;
            feature_byte_valid[init_index] = 8'd0;
        end
        for (init_index = 0; init_index < GOLDEN_BYTE_COUNT; init_index = init_index + 1) begin
            expected_bytes[init_index] = 8'd0;
            golden_byte_seen[init_index] = 8'd0;
        end

        input_fixture_path = $sformatf("%s\\input_chw_int8.bin", fixture_dir);
        file_id = $fopen(input_fixture_path, "rb");
        if (file_id == 0) $fatal(1, "T68 无法打开 input fixture：%s", input_fixture_path);
        loaded_byte_count = $fread(input_bytes, file_id);
        extra_byte = $fgetc(file_id);
        $fclose(file_id);
        if ((loaded_byte_count != INPUT_BYTE_COUNT) || (extra_byte != -1)) begin
            $fatal(1, "T68 input fixture 长度错误：read=%0d extra=%0d", loaded_byte_count, extra_byte);
        end

        file_id = $fopen(weight_fixture_path, "rb");
        if (file_id == 0) $fatal(1, "T68 无法打开 weight fixture：%s", weight_fixture_path);
        loaded_byte_count = $fread(weight_bytes, file_id);
        extra_byte = $fgetc(file_id);
        $fclose(file_id);
        if ((loaded_byte_count != WEIGHT_BYTE_COUNT) || (extra_byte != -1)) begin
            $fatal(1, "T68 weight fixture 长度错误：read=%0d extra=%0d", loaded_byte_count, extra_byte);
        end

        file_id = $fopen(golden_fixture_path, "rb");
        if (file_id == 0) $fatal(1, "T68 无法打开 golden fixture：%s", golden_fixture_path);
        loaded_byte_count = $fread(expected_bytes, file_id);
        extra_byte = $fgetc(file_id);
        $fclose(file_id);
        if ((loaded_byte_count != GOLDEN_BYTE_COUNT) || (extra_byte != -1)) begin
            $fatal(1, "T68 golden fixture 长度错误：read=%0d extra=%0d", loaded_byte_count, extra_byte);
        end

        repeat (4) @(negedge clk);
        hard_reset = 1'b0;
        buffer_owner_pl = 1'b1;
        backend_start = 1'b1;
        emit_progress("start");
        @(negedge clk);
        backend_start = 1'b0;

        while (!operator_result_valid) begin
            @(negedge clk);
            if (cycle_count >= max_cycles) begin
                $fatal(1, "T68 全网运行达到 cycle timeout：sample=%0d cycles=%0d", sample_index, cycle_count);
            end
        end
        #1;
        if (operator_error_code != NONE) begin
            $fatal(1, "T68 backend 返回 operator_error_code=%0d", operator_error_code);
        end
        if (backend_memory_error_valid || (backend_memory_error_code != NONE)) begin
            $fatal(1, "T68 backend 报告 memory error：valid=%0d code=%0d", backend_memory_error_valid, backend_memory_error_code);
        end

        for (verify_layer = 0; verify_layer < S2A_LAYER_COUNT; verify_layer = verify_layer + 1) begin
            if (S2A_OUTPUT_MEMORY_WRITE_REQUIRED[verify_layer]) begin
                if (layer_write_count[verify_layer] != S2A_OUTPUT_LENGTH_BYTES[verify_layer]) begin
                    $fatal(1, "T68 layer%0d 写入字节不完整：%0d/%0d", verify_layer,
                           layer_write_count[verify_layer], S2A_OUTPUT_LENGTH_BYTES[verify_layer]);
                end
                for (verify_offset = 0; verify_offset < S2A_OUTPUT_LENGTH_BYTES[verify_layer]; verify_offset = verify_offset + 1) begin
                    verify_golden_index = golden_offset[verify_layer] + verify_offset;
                    if (golden_byte_seen[verify_golden_index] != 8'd1) begin
                        $fatal(1, "T68 layer%0d golden byte 未恰好写入一次：offset=%0d seen=%0d",
                               verify_layer, verify_offset, golden_byte_seen[verify_golden_index]);
                    end
                end
            end
        end
        if (total_feature_write_bytes != GOLDEN_BYTE_COUNT) begin
            $fatal(1, "T68 总 feature write 字节数不匹配：%0d/%0d", total_feature_write_bytes, GOLDEN_BYTE_COUNT);
        end
        if (total_mismatches != 0) begin
            $fatal(1, "T68 tensor mismatch 非零：%0d", total_mismatches);
        end

        emit_progress("complete");

        file_id = $fopen(result_file_path, "w");
        if (file_id == 0) $fatal(1, "T68 无法创建 result summary：%s", result_file_path);
        $fdisplay(file_id, "status=PASS_LAYERWISE_EXACT_GOLDEN");
        $fdisplay(file_id, "scope=sample_%0d_layer_0_to_37_stored_outputs", sample_index);
        $fdisplay(file_id, "stored_tensors=36 alias_rows=2");
        $fdisplay(file_id, "input_read_bytes=%0d weight_read_bytes=%0d feature_read_bytes=%0d",
                  total_input_read_bytes, total_weight_read_bytes, total_feature_read_bytes);
        $fdisplay(file_id, "feature_write_bytes=%0d mismatches=%0d cycles=%0d",
                  total_feature_write_bytes, total_mismatches, cycle_count);
        $fdisplay(file_id, "stall_pattern_per_class=0,1,2,7,3");
        $fclose(file_id);
        $display("T68_RESULT status=PASS_LAYERWISE_EXACT_GOLDEN sample=%0d layers=38 stored=36 aliases=2 bytes=%0d mismatches=%0d cycles=%0d",
                 sample_index, total_feature_write_bytes, total_mismatches, cycle_count);
        $display("T68_MEMORY input_read_bytes=%0d weight_read_bytes=%0d feature_read_bytes=%0d read_transactions=%0d write_transactions=%0d",
                 total_input_read_bytes, total_weight_read_bytes, total_feature_read_bytes,
                 total_memory_read_transactions, total_memory_write_transactions);
        $display("T68_STALL accepted_by_class input=%0d weight=%0d feature_read=%0d feature_write=%0d pattern=0,1,2,7,3",
                 class_accepted_count[INPUT_READ_CLASS], class_accepted_count[WEIGHT_READ_CLASS],
                 class_accepted_count[FEATURE_READ_CLASS], class_accepted_count[FEATURE_WRITE_CLASS]);
        $finish;
    end

    always @(posedge clk) begin
        if (hard_reset) begin
            cycle_count <= 0;
            next_progress_cycle <= PROGRESS_INTERVAL_CYCLES;
            class_wait_count <= 0;
            stalled_previous <= 1'b0;
            stalled_address <= 32'd0;
            stalled_data <= 32'd0;
            stalled_write <= 1'b0;
            stalled_rstrb <= 4'd0;
            stalled_wstrb <= 4'd0;
        end else begin
            cycle_count <= cycle_count + 1;
            if (cycle_count >= next_progress_cycle) begin
                emit_progress("running");
                next_progress_cycle <= next_progress_cycle + PROGRESS_INTERVAL_CYCLES;
            end
            if (mem_valid && !mem_write && !is_onehot4(mem_rstrb)) begin
                $fatal(1, "T68 后端读请求必须每次只选一个 byte lane：addr=%08h rstrb=%b",
                       mem_addr, mem_rstrb);
            end
            if (mem_valid && !mem_write && (mem_error_code != NONE)) begin
                $fatal(1, "T68 后端读请求的选中字节越过 tensor/object 边界或非法：addr=%08h rstrb=%b code=%0d",
                       mem_addr, mem_rstrb, mem_error_code);
            end
            if (stalled_previous &&
                (!mem_valid || (mem_addr != stalled_address) || (mem_write != stalled_write) ||
                 (mem_wdata != stalled_data) || (mem_rstrb != stalled_rstrb) || (mem_wstrb != stalled_wstrb))) begin
                $fatal(1, "T68 request signals changed while stalled");
            end
            stalled_previous <= mem_valid && !mem_ready;
            if (mem_valid && !mem_ready) begin
                class_wait_count <= class_wait_count + 1;
                stalled_address <= mem_addr;
                stalled_data <= mem_wdata;
                stalled_write <= mem_write;
                stalled_rstrb <= mem_rstrb;
                stalled_wstrb <= mem_wstrb;
            end else if (!mem_valid || (mem_valid && mem_ready)) begin
                class_wait_count <= 0;
            end

            if (backend_memory_error_valid || (backend_memory_error_code != NONE)) begin
                $fatal(1, "T68 backend memory error：valid=%0d code=%0d",
                       backend_memory_error_valid, backend_memory_error_code);
            end
            if (mem_valid && mem_ready) begin
                if (mem_error_code != NONE) begin
                    $fatal(1, "T68 memory model error：code=%0d addr=%08h write=%0d",
                           mem_error_code, mem_addr, mem_write);
                end
                seq_transfer_class = classify_transfer(mem_write, mem_addr, mem_rstrb);
                class_transfer_index[seq_transfer_class] <= class_transfer_index[seq_transfer_class] + 1;
                class_accepted_count[seq_transfer_class] <= class_accepted_count[seq_transfer_class] + 1;
                active_byte_count = 0;
                if (mem_write) begin
                    total_memory_write_transactions <= total_memory_write_transactions + 1;
                    seq_owner = -1;
                    for (seq_lane = 0; seq_lane < 4; seq_lane = seq_lane + 1) begin
                        if (mem_wstrb[seq_lane]) begin
                            seq_lane_address = mem_addr + seq_lane;
                            seq_lane_owner = owned_output_layer(seq_lane_address);
                            if (seq_lane_owner < 0) begin
                                $fatal(1, "T68 feature write 落在非 owned output 地址：%08h", seq_lane_address);
                            end
                            if ((seq_owner >= 0) && (seq_owner != seq_lane_owner)) begin
                                $fatal(1, "T68 单个 word write 跨越两个 tensor：addr=%08h", seq_lane_address);
                            end
                            seq_owner = seq_lane_owner;
                            seq_feature_index = seq_lane_address - FEATURE_BASE_ADDRESS;
                            seq_golden_index = golden_offset[seq_owner] +
                                               (seq_lane_address - S2A_OUTPUT_ADDRESS[seq_owner]);
                            if (golden_byte_seen[seq_golden_index] != 8'd0) begin
                                $fatal(1, "T68 feature byte 被重复写入：layer=%0d offset=%0d",
                                       seq_owner, seq_lane_address - S2A_OUTPUT_ADDRESS[seq_owner]);
                            end
                            if (mem_wdata[(seq_lane * 8) +: 8] != expected_bytes[seq_golden_index]) begin
                                total_mismatches = total_mismatches + 1;
                                $fatal(1, "T68 golden mismatch：layer=%0d offset=%0d addr=%08h got=%02h expected=%02h",
                                       seq_owner, seq_lane_address - S2A_OUTPUT_ADDRESS[seq_owner], seq_lane_address,
                                       mem_wdata[(seq_lane * 8) +: 8], expected_bytes[seq_golden_index]);
                            end
                            feature_bytes[seq_feature_index] <= mem_wdata[(seq_lane * 8) +: 8];
                            feature_byte_valid[seq_feature_index] <= 8'd1;
                            golden_byte_seen[seq_golden_index] <= 8'd1;
                            active_byte_count = active_byte_count + 1;
                        end
                    end
                    if (seq_owner >= 0) begin
                        layer_write_count[seq_owner] <= layer_write_count[seq_owner] + active_byte_count;
                    end
                    total_feature_write_bytes <= total_feature_write_bytes + active_byte_count;
                    class_selected_byte_count[seq_transfer_class] <=
                        class_selected_byte_count[seq_transfer_class] + active_byte_count;
                end else begin
                    total_memory_read_transactions <= total_memory_read_transactions + 1;
                    input_bytes_this_transfer = 0;
                    weight_bytes_this_transfer = 0;
                    feature_bytes_this_transfer = 0;
                    for (seq_lane = 0; seq_lane < 4; seq_lane = seq_lane + 1) begin
                        if (mem_rstrb[seq_lane]) begin
                            seq_lane_address = mem_addr + seq_lane;
                            seq_tensor_owner = memory_tensor_owner(seq_lane_address);
                            if (seq_tensor_owner == 0) begin
                                input_bytes_this_transfer = input_bytes_this_transfer + 1;
                            end else if (seq_tensor_owner == 1) begin
                                weight_bytes_this_transfer = weight_bytes_this_transfer + 1;
                            end else if (seq_tensor_owner >= 2) begin
                                feature_bytes_this_transfer = feature_bytes_this_transfer + 1;
                                seq_feature_index = seq_lane_address - FEATURE_BASE_ADDRESS;
                                if (!feature_byte_valid[seq_feature_index]) begin
                                    $fatal(1, "T68 feature read 未初始化：%08h", seq_lane_address);
                                end
                            end else begin
                                $fatal(1, "T68 接受了没有合法 tensor owner 的 read lane：%08h", seq_lane_address);
                            end
                            active_byte_count = active_byte_count + 1;
                        end
                    end
                    total_input_read_bytes <= total_input_read_bytes + input_bytes_this_transfer;
                    total_weight_read_bytes <= total_weight_read_bytes + weight_bytes_this_transfer;
                    total_feature_read_bytes <= total_feature_read_bytes + feature_bytes_this_transfer;
                    total_memory_read_bytes <= total_memory_read_bytes + active_byte_count;
                    class_selected_byte_count[seq_transfer_class] <=
                        class_selected_byte_count[seq_transfer_class] + active_byte_count;
                end
            end
        end
    end
endmodule
