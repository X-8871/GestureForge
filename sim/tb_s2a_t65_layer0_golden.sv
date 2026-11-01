// S2A-T65：使用 sample0 的真实输入和 GF8 layer0 权重，核对首个输出字节。
`timescale 1ns/1ps
module tb_s2a_t65_layer0_golden;
    import s2a_network_descriptor_pkg::*;

    localparam logic [7:0] REG_CMD = 8'h00;
    localparam logic [7:0] REG_TIMEOUT = 8'h28;
    localparam logic [31:0] TEST_TIMEOUT = 32'd1000000;
    localparam integer PROBE_CYCLE_LIMIT = 3000;
    localparam integer INPUT_BYTE_COUNT = 519168;
    localparam integer LAYER0_WEIGHT_BYTE_COUNT = S2A_GF8_WEIGHT_BYTES[0];
    localparam logic [31:0] INPUT_BASE_ADDRESS = 32'h00000000;
    localparam logic [31:0] WEIGHT_BASE_ADDRESS = 32'h00100000;
    localparam logic [7:0] EXPECTED_T25_FIRST_BYTE = 8'hff;

    localparam logic [2:0] NONE = 3'd0;
    localparam logic [2:0] BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] BAD_RANGE = 3'd2;

    logic clk = 1'b0;
    logic hard_reset = 1'b0;
    logic csr_valid = 1'b0;
    logic csr_write = 1'b0;
    logic [7:0] csr_addr = 8'd0;
    logic [31:0] csr_wdata = 32'd0;
    logic csr_ready;
    logic [31:0] csr_rdata;
    logic backend_memory_error_valid;
    logic [2:0] backend_memory_error_code;
    logic operator_result_valid;
    logic [2:0] operator_error_code;
    logic backend_start;
    logic backend_abort;
    logic busy;
    logic done;
    logic error;
    logic buffer_owner_pl;
    logic head_output_valid;
    logic mem_valid;
    logic mem_write;
    logic [31:0] mem_addr;
    logic [31:0] mem_wdata;
    logic [3:0] mem_rstrb;
    logic [3:0] mem_wstrb;
    logic mem_ready;
    logic [31:0] mem_rdata;
    logic [2:0] mem_error_code;

    logic [7:0] input_bytes [0:INPUT_BYTE_COUNT-1];
    logic [7:0] weight_bytes [0:LAYER0_WEIGHT_BYTE_COUNT-1];
    logic [7:0] expected_first_byte [0:0];
    string input_fixture_path;
    string weight_fixture_path;
    string golden_fixture_path;
    logic [26:0] expected_valid_tap;
    logic [31:0] expected_input_address [0:26];
    logic [31:0] expected_weight_address [0:26];
    logic [26:0] input_tap_seen = 27'd0;
    logic [26:0] weight_tap_seen = 27'd0;

    integer input_read_byte_count = 0;
    integer weight_read_byte_count = 0;
    integer first_point_write_count = 0;
    integer probe_cycle;
    logic layer0_dispatch_seen = 1'b0;
    logic layer0_conv_start_seen = 1'b0;
    logic layer0_result_seen = 1'b0;
    logic layer0_first_point_write_seen = 1'b0;

    integer file_id;
    integer file_byte_count;
    integer init_index;
    integer init_channel;
    integer init_kernel_y;
    integer init_kernel_x;
    integer init_input_y;
    integer init_input_x;
    integer init_reduction_index;
    integer memory_lane;
    integer scoreboard_lane;
    integer tap_index;
    integer matched_tap;
    logic tap_match_found;
    logic [31:0] memory_lane_address;
    logic [31:0] scoreboard_lane_address;
    logic [31:0] layer0_weight_start_address;

    // 常量由冻结 sample0 输入和 GF8 layer0 切片逐 tap 得出，Python 核验 SHA 与字节映射。
    function automatic logic [7:0] expected_sample0_input_tap_byte(input integer reduction_index);
        begin
            case (reduction_index)
                4, 5, 7, 8, 13, 14, 16, 17, 22, 23, 25, 26:
                    expected_sample0_input_tap_byte = 8'h40;
                default: expected_sample0_input_tap_byte = 8'hxx;
            endcase
        end
    endfunction

    function automatic logic [7:0] expected_sample0_weight_tap_byte(input integer reduction_index);
        begin
            case (reduction_index)
                4: expected_sample0_weight_tap_byte = 8'h1d;
                5: expected_sample0_weight_tap_byte = 8'hf7;
                7: expected_sample0_weight_tap_byte = 8'hf7;
                8: expected_sample0_weight_tap_byte = 8'h08;
                13: expected_sample0_weight_tap_byte = 8'h42;
                14: expected_sample0_weight_tap_byte = 8'hf1;
                16: expected_sample0_weight_tap_byte = 8'hf9;
                17: expected_sample0_weight_tap_byte = 8'hf7;
                22: expected_sample0_weight_tap_byte = 8'h7f;
                23: expected_sample0_weight_tap_byte = 8'h14;
                25: expected_sample0_weight_tap_byte = 8'h0c;
                26: expected_sample0_weight_tap_byte = 8'hf9;
                default: expected_sample0_weight_tap_byte = 8'hxx;
            endcase
        end
    endfunction

    always #5 clk = ~clk;

    // memory 只映射冻结 sample0 输入与 layer0 GF8 权重切片；未知地址返回 BAD_RANGE。
    always_comb begin
        mem_ready = !hard_reset && busy && buffer_owner_pl;
        mem_rdata = 32'd0;
        mem_error_code = NONE;
        memory_lane_address = 32'd0;

        if (mem_valid && mem_ready) begin
            if (mem_addr[1:0] != 2'b00) begin
                mem_error_code = BAD_RANGE;
            end else if (mem_write) begin
                if ((mem_rstrb != 4'b0000) || (mem_wstrb == 4'b0000)) begin
                    mem_error_code = BAD_ARGUMENT;
                end else begin
                    for (memory_lane = 0; memory_lane < 4; memory_lane = memory_lane + 1) begin
                        if (mem_wstrb[memory_lane]) begin
                            memory_lane_address = mem_addr + memory_lane;
                            if (memory_lane_address != S2A_OUTPUT_ADDRESS[0]) begin
                                mem_error_code = BAD_RANGE;
                            end
                        end
                    end
                end
            end else if ((mem_rstrb == 4'b0000) || (mem_wstrb != 4'b0000)) begin
                mem_error_code = BAD_ARGUMENT;
            end else begin
                for (memory_lane = 0; memory_lane < 4; memory_lane = memory_lane + 1) begin
                    if (mem_rstrb[memory_lane]) begin
                        memory_lane_address = mem_addr + memory_lane;
                        if ((memory_lane_address >= INPUT_BASE_ADDRESS) &&
                            (memory_lane_address < INPUT_BASE_ADDRESS + INPUT_BYTE_COUNT)) begin
                            mem_rdata[(memory_lane * 8) +: 8] =
                                input_bytes[memory_lane_address - INPUT_BASE_ADDRESS];
                        end else if ((memory_lane_address >= layer0_weight_start_address) &&
                                     (memory_lane_address < layer0_weight_start_address + LAYER0_WEIGHT_BYTE_COUNT)) begin
                            mem_rdata[(memory_lane * 8) +: 8] =
                                weight_bytes[memory_lane_address - layer0_weight_start_address];
                        end else begin
                            mem_error_code = BAD_RANGE;
                        end
                    end
                end
            end
        end
    end

    s2a_control_csr u_csr (
        .clk(clk), .hard_reset(hard_reset),
        .csr_valid(csr_valid), .csr_ready(csr_ready), .csr_write(csr_write),
        .csr_addr(csr_addr), .csr_wdata(csr_wdata), .csr_rdata(csr_rdata),
        .backend_memory_error_valid(backend_memory_error_valid),
        .backend_memory_error_code(backend_memory_error_code),
        .operator_result_valid(operator_result_valid),
        .operator_error_code(operator_error_code),
        .backend_start(backend_start), .backend_abort(backend_abort),
        .busy(busy), .done(done), .error(error),
        .pl_owns_buffers(buffer_owner_pl), .head_output_valid(head_output_valid)
    );

    s2a_network_backend u_backend (
        .clk(clk), .hard_reset(hard_reset), .abort(backend_abort),
        .backend_start(backend_start), .buffer_owner_pl(buffer_owner_pl),
        .input_base_address(INPUT_BASE_ADDRESS),
        .input_length_bytes(INPUT_BYTE_COUNT),
        .weight_package_base_address(WEIGHT_BASE_ADDRESS),
        .weight_package_length_bytes(32'd5903100),
        .mem_valid(mem_valid), .mem_write(mem_write), .mem_addr(mem_addr),
        .mem_wdata(mem_wdata), .mem_rstrb(mem_rstrb), .mem_wstrb(mem_wstrb),
        .mem_ready(mem_ready), .mem_rdata(mem_rdata), .mem_error_code(mem_error_code),
        .backend_memory_error_valid(backend_memory_error_valid),
        .backend_memory_error_code(backend_memory_error_code),
        .operator_result_valid(operator_result_valid),
        .operator_error_code(operator_error_code)
    );

    task automatic write_csr(input logic [7:0] address,
                             input logic [31:0] value);
        begin
            @(negedge clk);
            if (!csr_ready) begin
                $fatal(1, "T65 CSR 写入未 ready：addr=%02h data=%08h", address, value);
            end
            csr_valid = 1'b1;
            csr_write = 1'b1;
            csr_addr = address;
            csr_wdata = value;
            @(posedge clk);
            #1;
            @(negedge clk);
            csr_valid = 1'b0;
            csr_write = 1'b0;
            csr_addr = 8'd0;
            csr_wdata = 32'd0;
        end
    endtask

    // 每个 memory 握手的选中字节都必须命中当前输出点的真实 input 或 weight tap。
    always @(posedge clk) begin
        if (hard_reset) begin
            input_read_byte_count <= 0;
            weight_read_byte_count <= 0;
            first_point_write_count <= 0;
            input_tap_seen <= 27'd0;
            weight_tap_seen <= 27'd0;
            layer0_dispatch_seen <= 1'b0;
            layer0_conv_start_seen <= 1'b0;
            layer0_result_seen <= 1'b0;
            layer0_first_point_write_seen <= 1'b0;
        end else begin
            if ((u_backend.state == u_backend.ST_DISPATCH) &&
                (u_backend.layer_cursor == 6'd0) &&
                (u_backend.current_op == S2A_OP_CONV)) begin
                layer0_dispatch_seen <= 1'b1;
            end
            if (u_backend.conv_start_valid && u_backend.conv_start_ready &&
                (u_backend.layer_cursor == 6'd0)) begin
                layer0_conv_start_seen <= 1'b1;
            end
            if ((u_backend.state == u_backend.ST_WAIT_CONV) &&
                u_backend.conv_result_valid && u_backend.conv_result_ready &&
                (u_backend.layer_cursor == 6'd0) &&
                (u_backend.conv_result_error == NONE)) begin
                layer0_result_seen <= 1'b1;
            end

            if (mem_valid && mem_ready) begin
                if (mem_error_code != NONE) begin
                    $fatal(1, "T65 memory model 报错：code=%0d addr=%08h", mem_error_code, mem_addr);
                end
                if (mem_write) begin
                    if ((mem_rstrb != 4'b0000) || ($countones(mem_wstrb) != 1)) begin
                        $fatal(1, "T65 输出写入 strobes 错误：rstrb=%b wstrb=%b", mem_rstrb, mem_wstrb);
                    end
                    for (scoreboard_lane = 0; scoreboard_lane < 4; scoreboard_lane = scoreboard_lane + 1) begin
                        if (mem_wstrb[scoreboard_lane]) begin
                            scoreboard_lane_address = mem_addr + scoreboard_lane;
                            if (scoreboard_lane_address != S2A_OUTPUT_ADDRESS[0]) begin
                                $fatal(1, "T65 写入超出 layer0 首个输出字节：addr=%08h", scoreboard_lane_address);
                            end
                            if (mem_wdata[(scoreboard_lane * 8) +: 8] !== expected_first_byte[0]) begin
                                $fatal(1, "T65 sample0 layer0 首字节 mismatch：RTL=%02h T25=%02h",
                                       mem_wdata[(scoreboard_lane * 8) +: 8], expected_first_byte[0]);
                            end
                            first_point_write_count <= first_point_write_count + 1;
                            layer0_first_point_write_seen <= 1'b1;
                            $display("T65_FIRST_POINT_WRITE address=%08h value=%02h signed=%0d",
                                     scoreboard_lane_address,
                                     mem_wdata[(scoreboard_lane * 8) +: 8],
                                     $signed(mem_wdata[(scoreboard_lane * 8) +: 8]));
                        end
                    end
                end else begin
                    if ((mem_rstrb == 4'b0000) || (mem_wstrb != 4'b0000) ||
                        ($countones(mem_rstrb) != 1)) begin
                        $fatal(1, "T65 CONV 读请求 strobes 错误：rstrb=%b wstrb=%b", mem_rstrb, mem_wstrb);
                    end
                    for (scoreboard_lane = 0; scoreboard_lane < 4; scoreboard_lane = scoreboard_lane + 1) begin
                        if (mem_rstrb[scoreboard_lane]) begin
                            scoreboard_lane_address = mem_addr + scoreboard_lane;
                            tap_match_found = 1'b0;
                            matched_tap = -1;
                            if ((scoreboard_lane_address >= INPUT_BASE_ADDRESS) &&
                                (scoreboard_lane_address < INPUT_BASE_ADDRESS + INPUT_BYTE_COUNT)) begin
                                if (mem_rdata[(scoreboard_lane * 8) +: 8] !==
                                    input_bytes[scoreboard_lane_address - INPUT_BASE_ADDRESS]) begin
                                    $fatal(1, "T65 输入读数据不匹配：addr=%08h data=%02h expected=%02h",
                                           scoreboard_lane_address,
                                           mem_rdata[(scoreboard_lane * 8) +: 8],
                                           input_bytes[scoreboard_lane_address - INPUT_BASE_ADDRESS]);
                                end
                                for (tap_index = 0; tap_index < 27; tap_index = tap_index + 1) begin
                                    if (expected_valid_tap[tap_index] &&
                                        (expected_input_address[tap_index] == scoreboard_lane_address)) begin
                                        matched_tap = tap_index;
                                        tap_match_found = 1'b1;
                                    end
                                end
                                if (!tap_match_found || input_tap_seen[matched_tap]) begin
                                    $fatal(1, "T65 输入读地址不属于首点唯一有效 tap：addr=%08h tap=%0d",
                                           scoreboard_lane_address, matched_tap);
                                end
                                input_tap_seen[matched_tap] <= 1'b1;
                                input_read_byte_count <= input_read_byte_count + 1;
                            end else if ((scoreboard_lane_address >= layer0_weight_start_address) &&
                                         (scoreboard_lane_address < layer0_weight_start_address + LAYER0_WEIGHT_BYTE_COUNT)) begin
                                if (mem_rdata[(scoreboard_lane * 8) +: 8] !==
                                    weight_bytes[scoreboard_lane_address - layer0_weight_start_address]) begin
                                    $fatal(1, "T65 GF8 权重读数据不匹配：addr=%08h data=%02h expected=%02h",
                                           scoreboard_lane_address,
                                           mem_rdata[(scoreboard_lane * 8) +: 8],
                                           weight_bytes[scoreboard_lane_address - layer0_weight_start_address]);
                                end
                                for (tap_index = 0; tap_index < 27; tap_index = tap_index + 1) begin
                                    if (expected_valid_tap[tap_index] &&
                                        (expected_weight_address[tap_index] == scoreboard_lane_address)) begin
                                        matched_tap = tap_index;
                                        tap_match_found = 1'b1;
                                    end
                                end
                                if (!tap_match_found || weight_tap_seen[matched_tap]) begin
                                    $fatal(1, "T65 权重读地址不属于首点唯一有效 tap：addr=%08h tap=%0d",
                                           scoreboard_lane_address, matched_tap);
                                end
                                weight_tap_seen[matched_tap] <= 1'b1;
                                weight_read_byte_count <= weight_read_byte_count + 1;
                            end else begin
                                $fatal(1, "T65 非输入/权重地址读请求：%08h", scoreboard_lane_address);
                            end
                        end
                    end
                end
            end
        end
    end

    initial begin
        layer0_weight_start_address = WEIGHT_BASE_ADDRESS + S2A_GF8_WEIGHT_OFFSET[0];
        expected_valid_tap = 27'd0;
        for (init_index = 0; init_index < INPUT_BYTE_COUNT; init_index = init_index + 1) begin
            input_bytes[init_index] = 8'hxx;
        end
        for (init_index = 0; init_index < LAYER0_WEIGHT_BYTE_COUNT; init_index = init_index + 1) begin
            weight_bytes[init_index] = 8'hxx;
        end
        expected_first_byte[0] = 8'hxx;

        if (!$value$plusargs("T65_INPUT_PATH=%s", input_fixture_path)) begin
            $fatal(1, "缺少 T65_INPUT_PATH 仿真参数");
        end
        if (!$value$plusargs("T65_WEIGHT_PATH=%s", weight_fixture_path)) begin
            $fatal(1, "缺少 T65_WEIGHT_PATH 仿真参数");
        end
        if (!$value$plusargs("T65_GOLDEN_PATH=%s", golden_fixture_path)) begin
            $fatal(1, "缺少 T65_GOLDEN_PATH 仿真参数");
        end

        file_id = $fopen(input_fixture_path, "rb");
        if (file_id == 0) begin
            $fatal(1, "无法打开 T01 sample0 输入夹具：%s", input_fixture_path);
        end
        file_byte_count = $fread(input_bytes, file_id);
        $fclose(file_id);
        if (file_byte_count != INPUT_BYTE_COUNT) begin
            $fatal(1, "sample0 输入夹具长度错误：expected=%0d actual=%0d", INPUT_BYTE_COUNT, file_byte_count);
        end

        file_id = $fopen(weight_fixture_path, "rb");
        if (file_id == 0) begin
            $fatal(1, "无法打开 G0 layer0 GF8 权重夹具：%s", weight_fixture_path);
        end
        file_byte_count = $fread(weight_bytes, file_id);
        $fclose(file_id);
        if (file_byte_count != LAYER0_WEIGHT_BYTE_COUNT) begin
            $fatal(1, "layer0 GF8 权重夹具长度错误：expected=%0d actual=%0d",
                   LAYER0_WEIGHT_BYTE_COUNT, file_byte_count);
        end

        file_id = $fopen(golden_fixture_path, "rb");
        if (file_id == 0) begin
            $fatal(1, "无法打开 T25 sample0 layer0 黄金夹具：%s", golden_fixture_path);
        end
        file_byte_count = $fread(expected_first_byte, file_id);
        $fclose(file_id);
        if (file_byte_count != 1) begin
            $fatal(1, "T25 首输出夹具必须恰为 1 byte，actual=%0d", file_byte_count);
        end

        for (init_index = 0; init_index < INPUT_BYTE_COUNT; init_index = init_index + 1) begin
            if ((^input_bytes[init_index]) === 1'bx) begin
                $fatal(1, "sample0 输入夹具含未加载字节：index=%0d", init_index);
            end
        end
        for (init_index = 0; init_index < LAYER0_WEIGHT_BYTE_COUNT; init_index = init_index + 1) begin
            if ((^weight_bytes[init_index]) === 1'bx) begin
                $fatal(1, "layer0 权重夹具含未加载字节：index=%0d", init_index);
            end
        end
        if ((^expected_first_byte[0]) === 1'bx) begin
            $fatal(1, "T25 首输出黄金字节未加载");
        end
        if (expected_first_byte[0] !== EXPECTED_T25_FIRST_BYTE) begin
            $fatal(1, "T25 首输出夹具必须为冻结字节 ff：actual=%02h", expected_first_byte[0]);
        end

        for (init_index = 0; init_index < 27; init_index = init_index + 1) begin
            init_channel = init_index / 9;
            init_kernel_y = (init_index % 9) / 3;
            init_kernel_x = init_index % 3;
            init_input_y = init_kernel_y - 1;
            init_input_x = init_kernel_x - 1;
            expected_input_address[init_index] = 32'd0;
            expected_weight_address[init_index] = 32'd0;
            if ((init_input_y >= 0) && (init_input_y < 416) &&
                (init_input_x >= 0) && (init_input_x < 416)) begin
                init_reduction_index = init_channel * 9 + init_kernel_y * 3 + init_kernel_x;
                expected_input_address[init_index] = INPUT_BASE_ADDRESS +
                    init_channel * 416 * 416 + init_input_y * 416 + init_input_x;
                expected_weight_address[init_index] = WEIGHT_BASE_ADDRESS +
                    S2A_GF8_WEIGHT_OFFSET[0] + init_reduction_index;
                expected_valid_tap[init_index] = 1'b1;
            end
        end
        if ($countones(expected_valid_tap) != 12) begin
            $fatal(1, "layer0 sample0 output [0,0,0,0] 的有效输入 tap 应为 12 项：mask=%h",
                   expected_valid_tap);
        end
        for (init_index = 0; init_index < 27; init_index = init_index + 1) begin
            if (expected_valid_tap[init_index]) begin
                if (input_bytes[expected_input_address[init_index] - INPUT_BASE_ADDRESS] !==
                    expected_sample0_input_tap_byte(init_index)) begin
                    $fatal(1, "T65 固定 sample0 输入 tap 与夹具不符：reduction=%0d address=%08h expected=%02h actual=%02h",
                           init_index, expected_input_address[init_index],
                           expected_sample0_input_tap_byte(init_index),
                           input_bytes[expected_input_address[init_index] - INPUT_BASE_ADDRESS]);
                end
                if (weight_bytes[expected_weight_address[init_index] - layer0_weight_start_address] !==
                    expected_sample0_weight_tap_byte(init_index)) begin
                    $fatal(1, "T65 固定 layer0 权重 tap 与夹具不符：reduction=%0d address=%08h expected=%02h actual=%02h",
                           init_index, expected_weight_address[init_index],
                           expected_sample0_weight_tap_byte(init_index),
                           weight_bytes[expected_weight_address[init_index] - layer0_weight_start_address]);
                end
            end
        end

        $display("T65_FIXTURE input_bytes=%0d weight_bytes=%0d golden_byte=%02h layer0_weight_offset=%08h output_address=%08h",
                 INPUT_BYTE_COUNT, LAYER0_WEIGHT_BYTE_COUNT,
                 expected_first_byte[0], S2A_GF8_WEIGHT_OFFSET[0], S2A_OUTPUT_ADDRESS[0]);
        $display("T65_SCOPE sample0 layer0 首个输出字节 NCHW=[0,0,0,0]；其余输出不在本 bench 范围内");

        @(negedge clk);
        hard_reset = 1'b1;
        repeat (2) @(posedge clk);
        #1;
        @(negedge clk);
        hard_reset = 1'b0;

        write_csr(REG_TIMEOUT, TEST_TIMEOUT);
        if (u_csr.timeout_cycles != TEST_TIMEOUT) begin
            $fatal(1, "T65 timeout CSR 未写入：expected=%0d actual=%0d",
                   TEST_TIMEOUT, u_csr.timeout_cycles);
        end
        write_csr(REG_CMD, 32'd1);
        if (!backend_start || !busy || !buffer_owner_pl || error) begin
            $fatal(1, "T65 CSR 未接受合法 start：start=%b busy=%b owner=%b error=%b",
                   backend_start, busy, buffer_owner_pl, error);
        end

        for (probe_cycle = 0; probe_cycle < PROBE_CYCLE_LIMIT;
             probe_cycle = probe_cycle + 1) begin
            @(posedge clk);
            #1;
            if (error ||
                (layer0_dispatch_seen && layer0_conv_start_seen && layer0_result_seen &&
                 layer0_first_point_write_seen)) begin
                break;
            end
        end

        if (error) begin
            $fatal(1, "T65 CSR/backend 报错：code=%0d elapsed=%0d",
                   u_csr.error_code, u_csr.elapsed_cycles);
        end
        if (!(layer0_dispatch_seen && layer0_conv_start_seen && layer0_result_seen &&
              layer0_first_point_write_seen)) begin
            $fatal(1, "T65 有界等待未完成首点 dispatch/start/result/write：cycles=%0d limit=%0d",
                   probe_cycle, PROBE_CYCLE_LIMIT);
        end
        if ((input_tap_seen !== expected_valid_tap) ||
            (weight_tap_seen !== expected_valid_tap)) begin
            $fatal(1, "T65 memory 实读 tap 覆盖不全：input=%h weight=%h expected=%h",
                   input_tap_seen, weight_tap_seen, expected_valid_tap);
        end
        if ((input_read_byte_count != 12) || (weight_read_byte_count != 12) ||
            (first_point_write_count != 1)) begin
            $fatal(1, "T65 首点实际传输计数错误：input=%0d weight=%0d output=%0d",
                   input_read_byte_count, weight_read_byte_count, first_point_write_count);
        end
        if (!busy || done || error || !buffer_owner_pl || head_output_valid) begin
            $fatal(1, "T65 首点完成后的整网运行状态超出单点测试范围");
        end

        $display("PASS: sample0 layer0 首个输出字节 memory-read/write matched T25，input_reads=12 weight_reads=12 output_writes=1 cycles=%0d",
                 probe_cycle);
        $finish;
    end
endmodule
