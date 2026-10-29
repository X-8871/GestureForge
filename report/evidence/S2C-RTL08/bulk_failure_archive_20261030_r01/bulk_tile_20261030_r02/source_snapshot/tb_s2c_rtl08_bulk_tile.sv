`timescale 1ns/1ps
module tb_s2c_rtl08_bulk_tile;
    import s2a_network_descriptor_pkg::*;

    localparam integer INPUT_BYTES = 519168;
    localparam integer WEIGHT_BYTES = 864;
    localparam integer OUTPUT_BYTES = 1384448;
    localparam integer FIRST_TILE_OUTPUTS = 32 * 16 * 16;
    localparam integer INPUT_ROW_BYTES = 416;
    localparam logic [31:0] INPUT_FIXTURE_BASE = S2A_INPUT_ADDRESS[0][0];
    localparam logic [31:0] WEIGHT_FIXTURE_BASE = S2A_GF8_PACKAGE_BASE[0] + S2A_GF8_WEIGHT_OFFSET[0];
    localparam logic [31:0] OUTPUT_FIXTURE_BASE = S2A_OUTPUT_ADDRESS[0];

    logic clk = 1'b0;
    logic hard_reset = 1'b1;
    logic start_valid = 1'b0;
    logic start_ready;
    logic busy;
    logic result_valid;
    logic result_ready = 1'b0;
    logic [2:0] result_error_code;
    logic backend_cancel;
    logic backend_req_valid;
    logic backend_req_write;
    logic [31:0] backend_req_addr;
    logic [31:0] backend_req_wdata;
    logic [3:0] backend_req_rstrb;
    logic [3:0] backend_req_wstrb;
    logic backend_rsp_valid = 1'b0;
    logic [31:0] backend_rsp_rdata = 32'd0;
    logic [2:0] backend_rsp_error = 3'd0;

    logic bulk_cmd_valid;
    logic bulk_cmd_ready;
    logic bulk_cmd_write;
    logic [31:0] bulk_cmd_addr;
    logic [7:0] bulk_cmd_bytes;
    logic bulk_wvalid;
    logic bulk_wready;
    logic [7:0] bulk_wdata;
    logic bulk_rvalid;
    logic bulk_rready;
    logic [7:0] bulk_rdata;
    logic bulk_done_valid;
    logic bulk_done_ready;
    logic [2:0] bulk_done_error;

    logic [7:0] input_fixture [0:INPUT_BYTES-1];
    logic [7:0] weight_fixture [0:WEIGHT_BYTES-1];
    logic [7:0] output_golden [0:OUTPUT_BYTES-1];
    logic [FIRST_TILE_OUTPUTS-1:0] output_seen = '0;

    logic [31:0] prng = 32'h32B0_1C08;
    logic model_active = 1'b0;
    logic model_write = 1'b0;
    logic model_reject = 1'b0;
    logic [2:0] model_error = 3'd0;
    logic [31:0] model_address = 32'd0;
    integer model_length = 0;
    integer model_index = 0;
    integer model_done_delay = 0;
    integer test_mode = 0;

    integer cycle_count = 0;
    integer primary_start_cycle = 0;
    integer primary_cycles = 0;
    integer primary_feature_bulk_commands = 0;
    integer primary_weight_bulk_commands = 0;
    integer primary_output_bulk_commands = 0;
    integer primary_feature_bulk_bytes = 0;
    integer primary_weight_bulk_bytes = 0;
    integer primary_output_bulk_bytes = 0;
    integer primary_legacy_requests = 0;
    integer feature_bank_write_count = 0;
    integer feature_bank_read_count = 0;
    integer output_write_count = 0;
    integer output_write_bytes = 0;
    integer legacy_feature_reads = 0;
    integer legacy_weight_reads = 0;
    integer read_byte_address = 0;
    integer write_offset = 0;
    integer write_channel = 0;
    integer write_row = 0;
    integer write_column = 0;
    integer output_seen_index = 0;
    integer command_relative = 0;
    integer command_row_column = 0;
    integer fd = 0;
    integer byte_value = 0;
    integer index = 0;
    integer accepted_commands = 0;
    integer early_error_commands = 0;
    integer early_success_commands = 0;
    logic previous_command_stall = 1'b0;
    logic previous_write_stall = 1'b0;
    logic previous_command_write = 1'b0;
    logic [31:0] previous_command_address = 32'd0;
    logic [7:0] previous_command_bytes = 8'd0;
    logic [7:0] previous_write_data = 8'd0;

    always #5 clk = ~clk;

    s2b_conv_tile_engine #(
        .FROZEN_CONV_DESCRIPTOR(1'b1),
        .FROZEN_OUTPUT_LANES(32),
        .ENABLE_BULK(1'b1)
    ) dut (
        .clk(clk), .hard_reset(hard_reset), .abort(1'b0), .buffer_owner_pl(1'b1),
        .start_valid(start_valid), .start_ready(start_ready),
        .layer_index(32'd0), .weight_layer_index(32'd0),
        .input_base_address(S2A_INPUT_ADDRESS[0][0]),
        .input_length_bytes(S2A_INPUT_LENGTH_BYTES[0][0]),
        .input_batch_count({16'd0, S2A_INPUT_N[0][0]}),
        .input_channels({16'd0, S2A_INPUT_C[0][0]}),
        .input_height({16'd0, S2A_INPUT_H[0][0]}),
        .input_width({16'd0, S2A_INPUT_W[0][0]}),
        .output_base_address(S2A_OUTPUT_ADDRESS[0]),
        .output_length_bytes(S2A_OUTPUT_LENGTH_BYTES[0]),
        .output_batch_count({16'd0, S2A_OUTPUT_N[0]}),
        .output_channels({16'd0, S2A_OUTPUT_C[0]}),
        .output_height({16'd0, S2A_OUTPUT_H[0]}),
        .output_width({16'd0, S2A_OUTPUT_W[0]}),
        .kernel_height({24'd0, S2A_KERNEL_H[0]}),
        .kernel_width({24'd0, S2A_KERNEL_W[0]}),
        .stride_y({24'd0, S2A_STRIDE_H[0]}),
        .stride_x({24'd0, S2A_STRIDE_W[0]}),
        .pad_left({24'd0, S2A_PADDING_LEFT[0]}),
        .pad_right({24'd0, S2A_PADDING_RIGHT[0]}),
        .pad_top({24'd0, S2A_PADDING_TOP[0]}),
        .pad_bottom({24'd0, S2A_PADDING_BOTTOM[0]}),
        .groups(32'd1), .padding_value_int8(32'sd0),
        .weight_package_base_address(S2A_GF8_PACKAGE_BASE[0]),
        .weight_package_length_bytes(S2A_GF8_PACKAGE_LENGTH[0]),
        .quantized_weight_offset(S2A_GF8_WEIGHT_OFFSET[0]),
        .quantized_weight_bytes(S2A_GF8_WEIGHT_BYTES[0]),
        .output_batch(32'd0),
        .activation_mode((S2A_ACTIVATION[0] == S2A_ACT_LEAKY) ? 2'd1 : 2'd0),
        .backend_cancel(backend_cancel),
        .backend_req_valid(backend_req_valid), .backend_req_ready(1'b1),
        .backend_req_write(backend_req_write), .backend_req_addr(backend_req_addr),
        .backend_req_wdata(backend_req_wdata), .backend_req_rstrb(backend_req_rstrb),
        .backend_req_wstrb(backend_req_wstrb),
        .backend_rsp_valid(backend_rsp_valid), .backend_rsp_rdata(backend_rsp_rdata),
        .backend_rsp_error(backend_rsp_error),
        .bulk_cmd_valid(bulk_cmd_valid), .bulk_cmd_ready(bulk_cmd_ready),
        .bulk_cmd_write(bulk_cmd_write), .bulk_cmd_addr(bulk_cmd_addr),
        .bulk_cmd_bytes(bulk_cmd_bytes),
        .bulk_wvalid(bulk_wvalid), .bulk_wready(bulk_wready), .bulk_wdata(bulk_wdata),
        .bulk_rvalid(bulk_rvalid), .bulk_rready(bulk_rready), .bulk_rdata(bulk_rdata),
        .bulk_done_valid(bulk_done_valid), .bulk_done_ready(bulk_done_ready),
        .bulk_done_error(bulk_done_error),
        .busy(busy), .result_valid(result_valid), .result_ready(result_ready),
        .result_error_code(result_error_code)
    );

    function automatic integer onehot_lane(input logic [3:0] strobe);
        begin
            case (strobe)
                4'b0001: onehot_lane = 0;
                4'b0010: onehot_lane = 1;
                4'b0100: onehot_lane = 2;
                4'b1000: onehot_lane = 3;
                default: onehot_lane = -1;
            endcase
        end
    endfunction

    function automatic logic [7:0] model_read_byte(input logic [31:0] byte_address);
        integer offset;
        begin
            model_read_byte = 8'd0;
            if ((byte_address >= INPUT_FIXTURE_BASE) &&
                (byte_address < INPUT_FIXTURE_BASE + INPUT_BYTES)) begin
                offset = byte_address - INPUT_FIXTURE_BASE;
                model_read_byte = input_fixture[offset];
            end else if ((byte_address >= WEIGHT_FIXTURE_BASE) &&
                         (byte_address < WEIGHT_FIXTURE_BASE + WEIGHT_BYTES)) begin
                offset = byte_address - WEIGHT_FIXTURE_BASE;
                model_read_byte = weight_fixture[offset];
            end
        end
    endfunction

    function automatic logic [31:0] fixture_word(input logic [31:0] word_address);
        integer byte_index;
        logic [31:0] byte_address;
        begin
            fixture_word = 32'd0;
            for (byte_index = 0; byte_index < 4; byte_index = byte_index + 1) begin
                byte_address = word_address + byte_index;
                fixture_word[byte_index*8 +: 8] = model_read_byte(byte_address);
            end
        end
    endfunction

    assign bulk_cmd_ready = prng[0] | prng[3];
    assign bulk_wready = prng[2] | prng[7];
    assign bulk_rvalid = model_active && !model_write && !model_reject &&
                         (model_index < model_length) && (prng[4] | prng[9]);
    assign bulk_rdata = model_read_byte(model_address + model_index);
    assign bulk_done_valid = model_active &&
        (model_reject || (model_index >= model_length)) && (model_done_delay == 0);
    assign bulk_done_error = model_error;

    always @(negedge clk) begin
        if (!hard_reset) begin
            if (cycle_count > 200000) begin
                $fatal(1, "RTL08行为测试超过周期看门狗");
            end
            if (result_valid && (test_mode == 0) && (result_error_code != 3'd0)) begin
                $fatal(1, "首tile正常运行返回错误码 %0d", result_error_code);
            end
        end
    end

    always @(posedge clk) begin
        if (hard_reset) begin
            backend_rsp_valid <= 1'b0;
            backend_rsp_rdata <= 32'd0;
            cycle_count <= 0;
            prng <= 32'h32B0_1C08;
            model_active <= 1'b0;
            model_write <= 1'b0;
            model_reject <= 1'b0;
            model_error <= 3'd0;
            model_address <= 32'd0;
            model_length <= 0;
            model_index <= 0;
            model_done_delay <= 0;
            accepted_commands <= 0;
            early_error_commands <= 0;
            early_success_commands <= 0;
            feature_bank_write_count <= 0;
            feature_bank_read_count <= 0;
            output_write_count <= 0;
            output_write_bytes <= 0;
            legacy_feature_reads <= 0;
            legacy_weight_reads <= 0;
            primary_feature_bulk_commands <= 0;
            primary_weight_bulk_commands <= 0;
            primary_output_bulk_commands <= 0;
            primary_feature_bulk_bytes <= 0;
            primary_weight_bulk_bytes <= 0;
            primary_output_bulk_bytes <= 0;
            primary_legacy_requests <= 0;
            previous_command_stall <= 1'b0;
            previous_write_stall <= 1'b0;
            previous_command_write <= 1'b0;
            previous_command_address <= 32'd0;
            previous_command_bytes <= 8'd0;
            previous_write_data <= 8'd0;
        end else begin
            cycle_count <= cycle_count + 1;
            prng <= {prng[30:0], prng[31] ^ prng[21] ^ prng[1] ^ prng[0]};
            backend_rsp_valid <= backend_req_valid;
            if (backend_req_valid && !backend_req_write) begin
                read_byte_address = backend_req_addr + onehot_lane(backend_req_rstrb);
                if (onehot_lane(backend_req_rstrb) < 0) begin
                    $fatal(1, "旧路径读strobe不是单字节one-hot");
                end
                backend_rsp_rdata <= fixture_word(backend_req_addr);
                if ((read_byte_address >= INPUT_FIXTURE_BASE) &&
                    (read_byte_address < INPUT_FIXTURE_BASE + INPUT_BYTES)) begin
                    legacy_feature_reads <= legacy_feature_reads + 1;
                end else if ((read_byte_address >= WEIGHT_FIXTURE_BASE) &&
                             (read_byte_address < WEIGHT_FIXTURE_BASE + WEIGHT_BYTES)) begin
                    legacy_weight_reads <= legacy_weight_reads + 1;
                end else begin
                    $fatal(1, "旧路径读地址超出T66输入与权重对象：%08x", read_byte_address);
                end
                if (test_mode == 0) primary_legacy_requests <= primary_legacy_requests + 1;
            end else if (backend_req_valid && backend_req_write) begin
                $fatal(1, "RTL08意外使用旧逐字节输出写路径");
            end else begin
                backend_rsp_rdata <= 32'd0;
            end

            if (dut.feature_bank_wr_en) begin
                feature_bank_write_count <= feature_bank_write_count + 1;
                if (dut.feature_bank_wr_bad_address) begin
                    $fatal(1, "特征bank写地址越界");
                end
            end
            if (dut.feature_bank_rd_en) begin
                feature_bank_read_count <= feature_bank_read_count + 1;
                if ((dut.feature_bank_rd_lane_active !== 16'h0001) ||
                    dut.feature_bank_rd_conflict || dut.feature_bank_rd_bad_address) begin
                    $fatal(1, "特征bank单lane读异常");
                end
            end

            if (previous_command_stall &&
                (!bulk_cmd_valid || bulk_cmd_write !== previous_command_write ||
                 bulk_cmd_addr !== previous_command_address || bulk_cmd_bytes !== previous_command_bytes)) begin
                $fatal(1, "bulk命令在反压期间未保持有效与负载");
            end
            if (previous_write_stall && (!bulk_wvalid || bulk_wdata !== previous_write_data)) begin
                $fatal(1, "bulk写数据在反压期间未保持有效与负载");
            end
            previous_command_stall <= bulk_cmd_valid && !bulk_cmd_ready;
            previous_write_stall <= bulk_wvalid && !bulk_wready;
            previous_command_write <= bulk_cmd_write;
            previous_command_address <= bulk_cmd_addr;
            previous_command_bytes <= bulk_cmd_bytes;
            previous_write_data <= bulk_wdata;

            if (bulk_cmd_valid && bulk_cmd_ready) begin
                if (model_active) $fatal(1, "前一bulk命令未完成就接受新命令");
                if ((bulk_cmd_addr[2:0] != 3'd0) || (bulk_cmd_bytes < 8) ||
                    (bulk_cmd_bytes > 128) || ((bulk_cmd_bytes % 8) != 0)) begin
                    $fatal(1, "bulk命令对齐或长度非法 addr=%08x bytes=%0d",
                        bulk_cmd_addr, bulk_cmd_bytes);
                end
                accepted_commands <= accepted_commands + 1;
                model_active <= 1'b1;
                model_write <= bulk_cmd_write;
                model_address <= bulk_cmd_addr;
                model_length <= bulk_cmd_bytes;
                model_index <= 0;
                if (test_mode != 0) begin
                    model_reject <= 1'b1;
                    model_error <= (test_mode == 1) ? 3'd2 : 3'd0;
                    model_done_delay <= 2;
                    if (test_mode == 1) early_error_commands <= early_error_commands + 1;
                    else early_success_commands <= early_success_commands + 1;
                end else begin
                    model_reject <= 1'b0;
                    model_error <= 3'd0;
                    model_done_delay <= 0;
                    if (!bulk_cmd_write && (bulk_cmd_addr >= INPUT_FIXTURE_BASE) &&
                        (bulk_cmd_addr < INPUT_FIXTURE_BASE + INPUT_BYTES)) begin
                        command_relative = bulk_cmd_addr - INPUT_FIXTURE_BASE;
                        if ((bulk_cmd_addr + bulk_cmd_bytes > INPUT_FIXTURE_BASE + INPUT_BYTES) ||
                            ((command_relative % INPUT_ROW_BYTES) + bulk_cmd_bytes > INPUT_ROW_BYTES)) begin
                            $fatal(1, "特征bulk命令越过输入对象或行尾");
                        end
                        primary_feature_bulk_commands <= primary_feature_bulk_commands + 1;
                    end else if (!bulk_cmd_write && (bulk_cmd_addr >= WEIGHT_FIXTURE_BASE) &&
                                 (bulk_cmd_addr < WEIGHT_FIXTURE_BASE + WEIGHT_BYTES)) begin
                        if (bulk_cmd_addr + bulk_cmd_bytes > WEIGHT_FIXTURE_BASE + WEIGHT_BYTES)
                            $fatal(1, "权重bulk命令越过权重对象尾部");
                        primary_weight_bulk_commands <= primary_weight_bulk_commands + 1;
                    end else if (bulk_cmd_write && (bulk_cmd_addr >= OUTPUT_FIXTURE_BASE) &&
                                 (bulk_cmd_addr < OUTPUT_FIXTURE_BASE + OUTPUT_BYTES)) begin
                        command_relative = bulk_cmd_addr - OUTPUT_FIXTURE_BASE;
                        command_row_column = (command_relative % (208 * 208)) % 208;
                        if ((bulk_cmd_addr + bulk_cmd_bytes > OUTPUT_FIXTURE_BASE + OUTPUT_BYTES) ||
                            (command_row_column + bulk_cmd_bytes > 16)) begin
                            $fatal(1, "输出bulk命令越过输出对象或首tile行段");
                        end
                        primary_output_bulk_commands <= primary_output_bulk_commands + 1;
                    end else begin
                        $fatal(1, "bulk命令对象类型与地址不匹配 write=%0d addr=%08x",
                            bulk_cmd_write, bulk_cmd_addr);
                    end
                end
            end else if (model_active) begin
                if ((test_mode != 0) &&
                    ((bulk_rvalid && bulk_rready) || (bulk_wvalid && bulk_wready))) begin
                    $fatal(1, "提前完成负例不应传送任何bulk数据");
                end
                if (bulk_rvalid && bulk_rready) begin
                    if ((model_address + model_index >= INPUT_FIXTURE_BASE) &&
                        (model_address + model_index < INPUT_FIXTURE_BASE + INPUT_BYTES)) begin
                        if (test_mode == 0) primary_feature_bulk_bytes <= primary_feature_bulk_bytes + 1;
                    end else if ((model_address + model_index >= WEIGHT_FIXTURE_BASE) &&
                                 (model_address + model_index < WEIGHT_FIXTURE_BASE + WEIGHT_BYTES)) begin
                        if (test_mode == 0) primary_weight_bulk_bytes <= primary_weight_bulk_bytes + 1;
                    end else begin
                        $fatal(1, "bulk读字节地址超出fixture：%08x", model_address + model_index);
                    end
                    if (model_index + 1 == model_length) model_done_delay <= 2;
                    model_index <= model_index + 1;
                end else if (bulk_wvalid && bulk_wready) begin
                    if (!model_write) $fatal(1, "读命令收到写数据");
                    write_offset = model_address + model_index - OUTPUT_FIXTURE_BASE;
                    if ((write_offset < 0) || (write_offset >= OUTPUT_BYTES)) begin
                        $fatal(1, "bulk输出写地址超出golden范围：%08x", model_address + model_index);
                    end
                    write_channel = write_offset / (208 * 208);
                    write_row = (write_offset % (208 * 208)) / 208;
                    write_column = write_offset % 208;
                    if ((write_channel >= 32) || (write_row >= 16) || (write_column >= 16)) begin
                        $fatal(1, "bulk输出写到首tile范围外坐标 c=%0d y=%0d x=%0d",
                            write_channel, write_row, write_column);
                    end
                    output_seen_index = write_channel * 256 + write_row * 16 + write_column;
                    if (output_seen[output_seen_index]) begin
                        $fatal(1, "首tile输出坐标重复写入 c=%0d y=%0d x=%0d",
                            write_channel, write_row, write_column);
                    end
                    output_seen[output_seen_index] <= 1'b1;
                    if (bulk_wdata !== output_golden[write_offset]) begin
                        $display("RTL08首差异诊断 cycle=%0d model_addr=%08x model_index=%0d feature_cmd=%0d weight_cmd=%0d output_cmd=%0d feature_bytes=%0d weight_bytes=%0d legacy=%0d bank_wr=%0d bank_rd=%0d feature_index=%0d dut_state=%0d out_lane=%0d out_point=%0d block_index=%0d block0=%02x acc0=%08x weight0=%02x feature_data=%02x feature_bank_data=%02x feature_valid=%b feature_lane_valid=%h feature_addr=%h feature_mem0=%02x feature_mem_first_valid=%02x weight0_r0=%02x weight0_r4=%02x weight0_r26=%02x weight1_r0=%02x weight31_r26=%02x bulk_remaining=%0d",
                            cycle_count, model_address, model_index,
                            primary_feature_bulk_commands, primary_weight_bulk_commands,
                            primary_output_bulk_commands, primary_feature_bulk_bytes,
                            primary_weight_bulk_bytes, primary_legacy_requests,
                            feature_bank_write_count, feature_bank_read_count, dut.feature_scan_index,
                            dut.state, dut.output_lane_index, dut.output_point_index,
                            dut.bulk_output_block_index, dut.output_block[0],
                            dut.lane_accumulator[0], dut.weight_read_byte[0],
                            dut.feature_read_data, dut.feature_bank_rd_data_flat[7:0],
                            dut.feature_bank_rd_valid, dut.feature_bank_rd_lane_valid,
                            dut.feature_bank_rd_addr_flat[16:0],
                            dut.gen_feature_patch_bank.feature_patch_bank.gen_feature_bank[0].memory[0],
                            dut.gen_feature_patch_bank.feature_patch_bank.gen_feature_bank[2].memory[1],
                            dut.gen_weight_lane_bank[0].lane_weight_memory[0],
                            dut.gen_weight_lane_bank[0].lane_weight_memory[4],
                            dut.gen_weight_lane_bank[0].lane_weight_memory[26],
                            dut.gen_weight_lane_bank[1].lane_weight_memory[0],
                            dut.gen_weight_lane_bank[31].lane_weight_memory[26],
                            dut.bulk_bytes_remaining);
                        $display("差异 offset=%0d c=%0d y=%0d x=%0d 期望=%02x 实际=%02x",
                            write_offset, write_channel, write_row, write_column,
                            output_golden[write_offset], bulk_wdata);
                        $fatal(1, "bulk engine输出与冻结golden不等价");
                    end
                    if (test_mode == 0) begin
                        primary_output_bulk_bytes <= primary_output_bulk_bytes + 1;
                        output_write_count <= output_write_count + 1;
                        output_write_bytes <= output_write_bytes + 1;
                    end
                    if (model_index + 1 == model_length) model_done_delay <= 2;
                    model_index <= model_index + 1;
                end else if ((model_reject || (model_index >= model_length)) &&
                             (model_done_delay > 0)) begin
                    model_done_delay <= model_done_delay - 1;
                end
                if (bulk_done_valid && bulk_done_ready) begin
                    model_active <= 1'b0;
                    model_reject <= 1'b0;
                end
            end
        end
    end

    initial begin
        if (dut.LANE_COUNT != 32) $fatal(1, "DUT没有启用32 lane");
        fd = $fopen("D:\\FPGA_Competition\\report\\evidence\\S2A-T66\\tile01\\fixture\\sample0_input_chw_int8.bin", "rb");
        if (fd == 0) $fatal(1, "T66输入fixture无法打开");
        for (index = 0; index < INPUT_BYTES; index = index + 1) begin
            byte_value = $fgetc(fd);
            if (byte_value < 0) $fatal(1, "T66输入fixture长度不足");
            input_fixture[index] = byte_value[7:0];
        end
        if ($fgetc(fd) >= 0) $fatal(1, "T66输入fixture长度超出预期");
        $fclose(fd);

        fd = $fopen("D:\\FPGA_Competition\\report\\evidence\\S2A-T66\\tile01\\fixture\\sample0_layer0_gf8_weights.bin", "rb");
        if (fd == 0) $fatal(1, "T66权重fixture无法打开");
        for (index = 0; index < WEIGHT_BYTES; index = index + 1) begin
            byte_value = $fgetc(fd);
            if (byte_value < 0) $fatal(1, "T66权重fixture长度不足");
            weight_fixture[index] = byte_value[7:0];
        end
        if ($fgetc(fd) >= 0) $fatal(1, "T66权重fixture长度超出预期");
        $fclose(fd);

        fd = $fopen("D:\\FPGA_Competition\\report\\evidence\\S2A-T66\\tile01\\fixture\\sample0_layer0_expected_nchw_int8.bin", "rb");
        if (fd == 0) $fatal(1, "T66 golden无法打开");
        for (index = 0; index < OUTPUT_BYTES; index = index + 1) begin
            byte_value = $fgetc(fd);
            if (byte_value < 0) $fatal(1, "T66 golden长度不足");
            output_golden[index] = byte_value[7:0];
        end
        if ($fgetc(fd) >= 0) $fatal(1, "T66 golden长度超出预期");
        $fclose(fd);

        repeat (3) @(negedge clk);
        hard_reset = 1'b0;
        @(negedge clk);
        if (!start_ready) $fatal(1, "bulk engine未就绪");
        primary_start_cycle = cycle_count;
        start_valid = 1'b1;
        @(negedge clk);
        start_valid = 1'b0;

        wait (result_valid);
        primary_cycles = cycle_count - primary_start_cycle;
        if (result_error_code != 3'd0) $fatal(1, "首tile返回错误码 %0d", result_error_code);
        if (primary_feature_bulk_commands != 96) $fatal(1, "特征bulk命令应为96，实测%0d", primary_feature_bulk_commands);
        if (primary_weight_bulk_commands != 7) $fatal(1, "权重bulk命令应为7，实测%0d", primary_weight_bulk_commands);
        if (primary_output_bulk_commands != 512) $fatal(1, "输出bulk命令应为512，实测%0d", primary_output_bulk_commands);
        if ((primary_feature_bulk_commands + primary_weight_bulk_commands + primary_output_bulk_commands) != 615)
            $fatal(1, "bulk命令总数不是615");
        if (primary_feature_bulk_bytes != 3072) $fatal(1, "特征bulk有效字节应为3072，实测%0d", primary_feature_bulk_bytes);
        if (primary_weight_bulk_bytes != 856) $fatal(1, "权重bulk有效字节应为856，实测%0d", primary_weight_bulk_bytes);
        if (primary_output_bulk_bytes != 8192) $fatal(1, "输出bulk有效字节应为8192，实测%0d", primary_output_bulk_bytes);
        if (primary_legacy_requests != 8) $fatal(1, "旧路径请求应为8，实测%0d", primary_legacy_requests);
        if (legacy_feature_reads != 0 || legacy_weight_reads != 8)
            $fatal(1, "旧路径输入/权重请求分布错误：feature=%0d weight=%0d", legacy_feature_reads, legacy_weight_reads);
        if (feature_bank_write_count != 3267) $fatal(1, "特征bank写数应为3267，实测%0d", feature_bank_write_count);
        if (feature_bank_read_count != 6627) $fatal(1, "特征bank tap读数应为6627，实测%0d", feature_bank_read_count);
        if (output_write_count != FIRST_TILE_OUTPUTS) $fatal(1, "golden输出覆盖数不为8192");
        for (index = 0; index < FIRST_TILE_OUTPUTS; index = index + 1) begin
            if (!output_seen[index]) $fatal(1, "golden输出缺失 index=%0d", index);
        end
        $display("PASS RTL08首tile：feature_cmd=%0d weight_cmd=%0d output_cmd=%0d legacy_req=%0d bytes=%0d cycles=%0d unique_golden=%0d seed=32'h32B0_1C08",
            primary_feature_bulk_commands, primary_weight_bulk_commands, primary_output_bulk_commands,
            primary_legacy_requests,
            primary_feature_bulk_bytes + primary_weight_bulk_bytes + primary_output_bulk_bytes + primary_legacy_requests,
            primary_cycles, output_write_count);

        result_ready = 1'b1;
        @(negedge clk);
        result_ready = 1'b0;
        @(negedge clk);
        if (!start_ready) $fatal(1, "早错误测试前engine未返回空闲");
        test_mode = 1;
        start_valid = 1'b1;
        @(negedge clk);
        start_valid = 1'b0;
        wait (result_valid);
        if (result_error_code != 3'd2 || early_error_commands != 1)
            $fatal(1, "无payload提前BAD_RANGE未正确结束 code=%0d commands=%0d",
                result_error_code, early_error_commands);

        result_ready = 1'b1;
        @(negedge clk);
        result_ready = 1'b0;
        @(negedge clk);
        if (!start_ready) $fatal(1, "早成功测试前engine未返回空闲");
        test_mode = 2;
        start_valid = 1'b1;
        @(negedge clk);
        start_valid = 1'b0;
        wait (result_valid);
        if (result_error_code != 3'd6 || early_success_commands != 1)
            $fatal(1, "payload未收齐的提前成功未映射为INTERNAL code=%0d commands=%0d",
                result_error_code, early_success_commands);

        $display("PASS RTL08早完成错误/成功语义：error_code=2 success_early_code=6；bulk模型不是AXI桥实测");
        $finish;
    end
endmodule
