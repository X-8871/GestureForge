// 验证 row0 两块 feeder 的地址、byte strobe、停顿、错误与恢复。
module tb_s2a_conv_spatial_row0_pilot;
    localparam integer FEATURE_BYTES = 173056;
    localparam integer K_COUNT = 256;
    localparam integer TOTAL_REQUESTS = 2304;
    localparam logic [31:0] FEATURE_BASE = 32'd27966080;
    localparam logic [31:0] WEIGHT_BASE = 32'h00100000 + 32'd5895420;

    logic clk = 1'b0;
    always #5 clk = ~clk;

    logic rst;
    logic abort;
    logic start_valid;
    logic start_ready;
    logic busy;
    logic mem_valid;
    logic mem_ready;
    logic mem_write;
    logic [31:0] mem_addr;
    logic [31:0] mem_wdata;
    logic [3:0] mem_rstrb;
    logic [3:0] mem_wstrb;
    logic [31:0] mem_rdata;
    logic [2:0] mem_error_code;
    logic tile_result_valid;
    logic tile_result_ready;
    logic tile_result_index;
    logic [15:0] tile_valid_mask;
    logic [511:0] tile_raw_accumulators;
    logic tile_result_last;
    logic error_valid;
    logic error_ready;
    logic [2:0] error_code;

    logic [7:0] input_memory [0:FEATURE_BYTES-1];
    logic [7:0] weight_memory [0:255];
    logic [31:0] expected_raw [0:25];

    logic expect_bus;
    logic [2:0] injected_error_code;
    integer injected_request_index;
    integer transaction_request_count;
    integer transaction_feature_reads;
    integer transaction_weight_reads;
    integer transaction_feature_bytes;
    integer transaction_weight_bytes;
    integer transaction_core_beats;
    integer primary_feature_reads;
    integer primary_weight_reads;
    integer primary_feature_bytes;
    integer primary_weight_bytes;
    integer primary_core_beats;
    integer total_stall_cycles;
    integer completed_normal_runs;
    integer memory_error_scenarios;
    integer cancelled_abort_scenarios;
    integer cancelled_reset_scenarios;
    integer recovery_runs;
    integer selected_lane_count;
    integer monitor_lane;
    integer read_offset;
    logic capture_primary;
    logic model_address_bad;
    logic hold_stalled_request;
    logic [31:0] held_addr;
    logic [31:0] held_wdata;
    logic [3:0] held_rstrb;
    logic [3:0] held_wstrb;
    logic held_write;
    logic [3:0] stall_remaining;
    logic stall_active;
    logic force_long_stall;
    logic [31:0] stall_prng_state;
    logic [31:0] next_prng_value;
    integer delay_value;
    integer request_count_before_cancel;
    integer cycle_index;
    integer lane_index;
    integer output_index;
    logic [511:0] held_tile_data;
    logic [15:0] held_tile_mask;
    logic held_tile_index;
    logic held_tile_last;
    logic [2:0] held_error_code;

    s2a_conv_spatial_row0_pilot dut (
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
        .tile_result_valid(tile_result_valid),
        .tile_result_ready(tile_result_ready),
        .tile_result_index(tile_result_index),
        .tile_valid_mask(tile_valid_mask),
        .tile_raw_accumulators(tile_raw_accumulators),
        .tile_result_last(tile_result_last),
        .error_valid(error_valid),
        .error_ready(error_ready),
        .error_code(error_code)
    );

    function automatic logic [31:0] xorshift32(input logic [31:0] value);
        logic [31:0] work_value;
        begin
            work_value = value ^ (value << 13);
            work_value = work_value ^ (work_value >> 17);
            work_value = work_value ^ (work_value << 5);
            xorshift32 = work_value;
        end
    endfunction

    task automatic fail(input string message);
        begin
            $display("FAIL: %s", message);
            $fatal(1);
        end
    endtask

    task automatic check_expected_request(input integer request_index);
        integer expected_tile;
        integer requests_per_k;
        integer k_value;
        integer position_in_k;
        integer word_index;
        logic [31:0] expected_byte_address;
        logic [31:0] expected_word_address;
        logic [3:0] expected_strobe;
        begin
            if (request_index < 0 || request_index >= TOTAL_REQUESTS) begin
                fail("G0 feeder 发出了超出 row0 计划的 memory 请求");
            end
            if (request_index < (5 * K_COUNT)) begin
                expected_tile = 0;
                requests_per_k = 5;
                k_value = request_index / 5;
                position_in_k = request_index % 5;
            end else begin
                expected_tile = 1;
                requests_per_k = 4;
                k_value = (request_index - (5 * K_COUNT)) / 4;
                position_in_k = (request_index - (5 * K_COUNT)) % 4;
            end
            if (expected_tile == 0 && requests_per_k != 5) begin
                fail("tile A memory request 分组错误");
            end
            if (position_in_k == 0) begin
                expected_byte_address = WEIGHT_BASE + k_value;
                expected_word_address = {expected_byte_address[31:2], 2'b00};
                expected_strobe = 4'b0001 << expected_byte_address[1:0];
            end else begin
                word_index = position_in_k - 1;
                expected_byte_address = FEATURE_BASE + (k_value * 676) +
                    ((expected_tile == 0) ? 0 : 16) + (word_index * 4);
                expected_word_address = {expected_byte_address[31:2], 2'b00};
                expected_strobe = ((expected_tile == 1) && (word_index == 2)) ?
                    4'b0011 : 4'b1111;
            end
            if (mem_addr !== expected_word_address || mem_rstrb !== expected_strobe) begin
                $display("request=%0d expected_addr=%0d actual_addr=%0d expected_rstrb=%b actual_rstrb=%b",
                         request_index, expected_word_address, mem_addr,
                         expected_strobe, mem_rstrb);
                fail("G0 memory address 或 byte strobe 不匹配 row0 tile/K 顺序");
            end
            if (mem_addr[1:0] != 2'b00 || mem_write !== 1'b0 ||
                mem_wstrb !== 4'b0000 || mem_wdata !== 32'd0) begin
                fail("feeder 请求未对齐、写方向或写 strobe 非零");
            end
        end
    endtask

    always_comb begin
        mem_rdata = 32'd0;
        mem_error_code = 3'd0;
        model_address_bad = 1'b0;
        selected_lane_count = 0;
        read_offset = 0;
        if (mem_valid && mem_ready) begin
            if ((injected_error_code != 3'd0) &&
                (transaction_request_count == injected_request_index)) begin
                mem_error_code = injected_error_code;
            end else begin
                for (monitor_lane = 0; monitor_lane < 4; monitor_lane = monitor_lane + 1) begin
                    if (mem_rstrb[monitor_lane]) begin
                        selected_lane_count = selected_lane_count + 1;
                        if ((mem_addr + monitor_lane) >= FEATURE_BASE &&
                            (mem_addr + monitor_lane) < (FEATURE_BASE + FEATURE_BYTES)) begin
                            read_offset = (mem_addr + monitor_lane) - FEATURE_BASE;
                            mem_rdata[monitor_lane * 8 +: 8] = input_memory[read_offset];
                        end else if ((mem_addr + monitor_lane) >= WEIGHT_BASE &&
                                     (mem_addr + monitor_lane) < (WEIGHT_BASE + 256)) begin
                            read_offset = (mem_addr + monitor_lane) - WEIGHT_BASE;
                            mem_rdata[monitor_lane * 8 +: 8] = weight_memory[read_offset];
                        end else begin
                            model_address_bad = 1'b1;
                            mem_error_code = 3'd2;
                        end
                    end
                end
            end
        end
    end

    always @(negedge clk) begin
        if (rst || abort || !mem_valid) begin
            stall_active <= 1'b0;
            stall_remaining <= 4'd0;
            mem_ready <= 1'b0;
        end else if (!stall_active) begin
            stall_active <= 1'b1;
            if (force_long_stall) begin
                stall_remaining <= 4'd7;
                mem_ready <= 1'b0;
            end else begin
                next_prng_value = xorshift32(stall_prng_state);
                stall_prng_state <= next_prng_value;
                delay_value = next_prng_value[2:0];
                stall_remaining <= delay_value[3:0];
                mem_ready <= (delay_value == 0);
            end
        end else if (stall_remaining == 4'd0) begin
            mem_ready <= 1'b1;
        end else if (stall_remaining == 4'd1) begin
            stall_remaining <= 4'd0;
            mem_ready <= 1'b1;
        end else begin
            stall_remaining <= stall_remaining - 4'd1;
            mem_ready <= 1'b0;
        end
    end

    always @(posedge clk) begin
        if (rst || abort) begin
            hold_stalled_request <= 1'b0;
            stall_active <= 1'b0;
            mem_ready <= 1'b0;
        end else begin
            if (mem_write !== 1'b0 || mem_wstrb !== 4'b0000 || mem_wdata !== 32'd0) begin
                fail("本 pilot 不得产生 memory 写请求");
            end
            if (mem_valid) begin
                if (mem_addr[1:0] != 2'b00 || mem_rstrb == 4'b0000) begin
                    fail("memory read 地址未对齐或 read strobe 为空");
                end
                if (!mem_ready) begin
                    total_stall_cycles <= total_stall_cycles + 1;
                    if (hold_stalled_request) begin
                        if (mem_addr !== held_addr || mem_write !== held_write ||
                            mem_wdata !== held_wdata || mem_rstrb !== held_rstrb ||
                            mem_wstrb !== held_wstrb) begin
                            fail("mem_valid 未握手期间请求字段变化");
                        end
                    end else begin
                        hold_stalled_request <= 1'b1;
                        held_addr <= mem_addr;
                        held_write <= mem_write;
                        held_wdata <= mem_wdata;
                        held_rstrb <= mem_rstrb;
                        held_wstrb <= mem_wstrb;
                    end
                end else begin
                    if (hold_stalled_request &&
                        (mem_addr !== held_addr || mem_write !== held_write ||
                         mem_wdata !== held_wdata || mem_rstrb !== held_rstrb ||
                         mem_wstrb !== held_wstrb)) begin
                        fail("最终握手周期请求字段与 stall 中字段不一致");
                    end
                    hold_stalled_request <= 1'b0;
                    stall_active <= 1'b0;
                    mem_ready <= 1'b0;
                    if (!expect_bus) begin
                        fail("未授权事务期间 feeder 发出了 memory 请求");
                    end
                    check_expected_request(transaction_request_count);
                    if (model_address_bad) begin
                        fail("memory model 收到落在冻结对象范围外的被选中字节");
                    end
                    if (injected_error_code != 3'd0 &&
                        transaction_request_count == injected_request_index) begin
                        if (mem_error_code !== injected_error_code) begin
                            fail("注入 memory error code 与 G0 同周期响应不符");
                        end
                    end else if (mem_error_code != 3'd0) begin
                        fail("非注入请求出现 memory model 错误");
                    end

                    if (transaction_request_count < 5 * K_COUNT) begin
                        if ((transaction_request_count % 5) == 0) begin
                            transaction_weight_reads <= transaction_weight_reads + 1;
                            if (mem_error_code == 3'd0) begin
                                transaction_weight_bytes <= transaction_weight_bytes + selected_lane_count;
                            end
                        end else begin
                            transaction_feature_reads <= transaction_feature_reads + 1;
                            if (mem_error_code == 3'd0) begin
                                transaction_feature_bytes <= transaction_feature_bytes + selected_lane_count;
                            end
                        end
                    end else begin
                        if (((transaction_request_count - 5 * K_COUNT) % 4) == 0) begin
                            transaction_weight_reads <= transaction_weight_reads + 1;
                            if (mem_error_code == 3'd0) begin
                                transaction_weight_bytes <= transaction_weight_bytes + selected_lane_count;
                            end
                        end else begin
                            transaction_feature_reads <= transaction_feature_reads + 1;
                            if (mem_error_code == 3'd0) begin
                                transaction_feature_bytes <= transaction_feature_bytes + selected_lane_count;
                            end
                        end
                    end
                    if (capture_primary) begin
                        if (transaction_request_count < 5 * K_COUNT) begin
                            if ((transaction_request_count % 5) == 0) begin
                                primary_weight_reads <= primary_weight_reads + 1;
                                if (mem_error_code == 3'd0) begin
                                    primary_weight_bytes <= primary_weight_bytes + selected_lane_count;
                                end
                            end else begin
                                primary_feature_reads <= primary_feature_reads + 1;
                                if (mem_error_code == 3'd0) begin
                                    primary_feature_bytes <= primary_feature_bytes + selected_lane_count;
                                end
                            end
                        end else begin
                            if (((transaction_request_count - 5 * K_COUNT) % 4) == 0) begin
                                primary_weight_reads <= primary_weight_reads + 1;
                                if (mem_error_code == 3'd0) begin
                                    primary_weight_bytes <= primary_weight_bytes + selected_lane_count;
                                end
                            end else begin
                                primary_feature_reads <= primary_feature_reads + 1;
                                if (mem_error_code == 3'd0) begin
                                    primary_feature_bytes <= primary_feature_bytes + selected_lane_count;
                                end
                            end
                        end
                    end
                    transaction_request_count <= transaction_request_count + 1;
                end
            end else begin
                hold_stalled_request <= 1'b0;
                mem_ready <= 1'b0;
            end

            if (dut.core_input_valid && dut.core_input_ready) begin
                transaction_core_beats <= transaction_core_beats + 1;
                if (capture_primary) begin
                    primary_core_beats <= primary_core_beats + 1;
                end
            end
        end
    end

    task automatic initialize_transaction(input logic [2:0] fault_code_value,
                                           input integer fault_request_value);
        begin
            expect_bus = 1'b1;
            injected_error_code = fault_code_value;
            injected_request_index = fault_request_value;
            transaction_request_count = 0;
            transaction_feature_reads = 0;
            transaction_weight_reads = 0;
            transaction_feature_bytes = 0;
            transaction_weight_bytes = 0;
            transaction_core_beats = 0;
        end
    endtask

    task automatic start_transaction(input logic [2:0] fault_code_value,
                                     input integer fault_request_value);
        begin
            initialize_transaction(fault_code_value, fault_request_value);
            @(negedge clk);
            #1;
            if (!start_ready) begin
                fail("空闲 feeder 未接受 start");
            end
            start_valid = 1'b1;
            @(posedge clk);
            #1;
            if (!busy) begin
                fail("接受 start 后 busy 未置位");
            end
            @(negedge clk);
            #1;
            start_valid = 1'b0;
        end
    endtask

    task automatic wait_for_tile_result;
        integer wait_cycles;
        begin
            wait_cycles = 0;
            while (!tile_result_valid && !error_valid && wait_cycles < 20000) begin
                @(posedge clk);
                #1;
                wait_cycles = wait_cycles + 1;
            end
            if (!tile_result_valid || error_valid) begin
                fail("等待成功 tile response 超时或收到错误");
            end
        end
    endtask

    task automatic verify_tile_response(input integer tile_number);
        integer lane;
        integer valid_lanes;
        integer expected_x;
        logic [15:0] expected_mask;
        begin
            expected_mask = (tile_number == 0) ? 16'hffff : 16'h03ff;
            valid_lanes = (tile_number == 0) ? 16 : 10;
            expected_x = (tile_number == 0) ? 0 : 16;
            if (!tile_result_valid || error_valid || tile_result_index !== (tile_number != 0) ||
                tile_valid_mask !== expected_mask || tile_result_last !== (tile_number != 0)) begin
                fail("tile result valid/index/mask/last 不符合 G0 valid-lane 约定");
            end
            held_tile_data = tile_raw_accumulators;
            held_tile_mask = tile_valid_mask;
            held_tile_index = tile_result_index;
            held_tile_last = tile_result_last;
            for (lane = 0; lane < valid_lanes; lane = lane + 1) begin
                if ($signed(tile_raw_accumulators[lane * 32 +: 32]) !==
                    $signed(expected_raw[expected_x + lane])) begin
                    $display("tile=%0d lane=%0d expected_raw=%0d actual_raw=%0d",
                             tile_number, lane, $signed(expected_raw[expected_x + lane]),
                             $signed(tile_raw_accumulators[lane * 32 +: 32]));
                    fail("CPU raw INT32 oracle 与 feeder/tile 输出不匹配");
                end
            end
            for (lane = valid_lanes; lane < 16; lane = lane + 1) begin
                if (tile_raw_accumulators[lane * 32 +: 32] !== 32'd0) begin
                    fail("tile B 无效 lane 必须屏蔽为零");
                end
            end
            tile_result_ready = 1'b0;
            repeat (3) begin
                @(posedge clk);
                #1;
                if (!tile_result_valid || tile_valid_mask !== held_tile_mask ||
                    tile_result_index !== held_tile_index || tile_result_last !== held_tile_last ||
                    tile_raw_accumulators !== held_tile_data) begin
                    fail("tile response 停顿期间输出字段变化");
                end
            end
        end
    endtask

    task automatic consume_success;
        begin
            wait_for_tile_result();
            if (transaction_request_count != TOTAL_REQUESTS ||
                transaction_feature_reads != 1792 || transaction_weight_reads != 512 ||
                transaction_feature_bytes != 6656 || transaction_weight_bytes != 512 ||
                transaction_core_beats != 512) begin
                $display("requests=%0d feature_reads=%0d weight_reads=%0d feature_bytes=%0d weight_bytes=%0d core_beats=%0d",
                         transaction_request_count, transaction_feature_reads,
                         transaction_weight_reads, transaction_feature_bytes,
                         transaction_weight_bytes, transaction_core_beats);
                fail("成功 row0 transaction 的完整地址/数据/核心握手计数不符");
            end
            verify_tile_response(0);
            @(negedge clk);
            #1;
            tile_result_ready = 1'b1;
            @(posedge clk);
            #1;
            @(negedge clk);
            #1;
            tile_result_ready = 1'b0;
            if (!tile_result_valid) begin
                fail("tile A 握手后 tile B response 缺失");
            end
            verify_tile_response(1);
            @(negedge clk);
            #1;
            tile_result_ready = 1'b1;
            @(posedge clk);
            #1;
            tile_result_ready = 1'b0;
            if (tile_result_valid || error_valid || busy || !start_ready) begin
                fail("tile B 最后握手后 feeder 未返回空闲");
            end
            expect_bus = 1'b0;
            injected_error_code = 3'd0;
            completed_normal_runs = completed_normal_runs + 1;
        end
    endtask

    task automatic run_success(input logic primary_run);
        begin
            if (primary_run) begin
                primary_feature_reads = 0;
                primary_weight_reads = 0;
                primary_feature_bytes = 0;
                primary_weight_bytes = 0;
                primary_core_beats = 0;
            end
            start_transaction(3'd0, -1);
            if (primary_run) begin
                capture_primary = 1'b1;
            end
            consume_success();
            capture_primary = 1'b0;
            if (primary_run &&
                (primary_feature_reads != 1792 || primary_weight_reads != 512 ||
                 primary_feature_bytes != 6656 || primary_weight_bytes != 512 ||
                 primary_core_beats != 512)) begin
                fail("primary normal run 的捕获计数不匹配");
            end
        end
    endtask

    task automatic consume_error(input logic [2:0] expected_error);
        integer wait_cycles;
        begin
            wait_cycles = 0;
            while (!error_valid && wait_cycles < 20000) begin
                @(posedge clk);
                #1;
                wait_cycles = wait_cycles + 1;
            end
            if (!error_valid || tile_result_valid || error_code !== expected_error ||
                mem_valid || !busy) begin
                $display("expected_error=%0d actual_error=%0d requests=%0d",
                         expected_error, error_code, transaction_request_count);
                fail("memory error code 未精确返回，或出现无效 tile 输出");
            end
            if (transaction_request_count != injected_request_index + 1) begin
                fail("memory 错误握手后 feeder 仍继续发起请求");
            end
            held_error_code = error_code;
            error_ready = 1'b0;
            repeat (3) begin
                @(posedge clk);
                #1;
                if (!error_valid || error_code !== held_error_code || tile_result_valid || mem_valid) begin
                    fail("错误响应停顿期间状态/错误码/请求变化");
                end
            end
            @(negedge clk);
            #1;
            error_ready = 1'b1;
            @(posedge clk);
            #1;
            error_ready = 1'b0;
            expect_bus = 1'b0;
            injected_error_code = 3'd0;
            if (error_valid || tile_result_valid || busy || !start_ready) begin
                fail("错误 ACK 后 feeder 未返回空闲");
            end
            repeat (3) begin
                @(posedge clk);
                #1;
                if (error_valid || tile_result_valid || mem_valid || busy) begin
                    fail("memory error ACK 后产生迟到响应");
                end
            end
            memory_error_scenarios = memory_error_scenarios + 1;
        end
    endtask

    task automatic run_memory_error(input logic [2:0] injected_code,
                                    input integer request_index);
        begin
            start_transaction(injected_code, request_index);
            consume_error(injected_code);
        end
    endtask

    task automatic wait_for_stalled_request;
        integer wait_cycles;
        begin
            wait_cycles = 0;
            while (!(mem_valid && !mem_ready) && wait_cycles < 100) begin
                @(posedge clk);
                #1;
                wait_cycles = wait_cycles + 1;
            end
            if (!(mem_valid && !mem_ready)) begin
                fail("未能进入可取消的 pending memory request");
            end
            repeat (2) begin
                @(posedge clk);
                #1;
                if (!mem_valid || mem_ready) begin
                    fail("强制 stall request 在取消前错误地握手");
                end
            end
        end
    endtask

    task automatic cancel_pending_read(input logic use_reset);
        begin
            force_long_stall = 1'b1;
            start_transaction(3'd0, -1);
            wait_for_stalled_request();
            request_count_before_cancel = transaction_request_count;
            if (request_count_before_cancel != 0) begin
                fail("pending 首读取消前不应已有 memory handshake");
            end
            @(negedge clk);
            #1;
            if (use_reset) begin
                rst = 1'b1;
            end else begin
                abort = 1'b1;
            end
            #1;
            if (mem_valid || mem_ready) begin
                $display("CANCEL_SAMPLE t=%0t use_reset=%0b mem_valid=%b mem_ready=%b rst=%b abort=%b dut_state=%0d stall_remaining=%0d stall_active=%b held_request=%b mem_addr=%0d mem_rstrb=%b",
                         $time, use_reset, mem_valid, mem_ready, rst, abort,
                         dut.state, stall_remaining, stall_active,
                         hold_stalled_request, mem_addr, mem_rstrb);
                fail("reset/abort 后未握手 memory request 未撤销");
            end
            @(posedge clk);
            #1;
            @(negedge clk);
            #1;
            rst = 1'b0;
            abort = 1'b0;
            force_long_stall = 1'b0;
            expect_bus = 1'b0;
            injected_error_code = 3'd0;
            #1;
            if (busy || mem_valid || tile_result_valid || error_valid || !start_ready) begin
                $display("CANCEL_IDLE_SAMPLE t=%0t use_reset=%0b busy=%b mem_valid=%b tile_valid=%b error_valid=%b start_ready=%b rst=%b abort=%b dut_state=%0d mem_addr=%0d mem_rstrb=%b",
                         $time, use_reset, busy, mem_valid, tile_result_valid,
                         error_valid, start_ready, rst, abort, dut.state,
                         mem_addr, mem_rstrb);
                fail("reset/abort 后 feeder 未立即恢复空闲");
            end
            repeat (4) begin
                @(posedge clk);
                #1;
                if (busy || mem_valid || tile_result_valid || error_valid) begin
                    fail("reset/abort 后出现迟到 memory/result/error response");
                end
            end
            if (use_reset) begin
                cancelled_reset_scenarios = cancelled_reset_scenarios + 1;
            end else begin
                cancelled_abort_scenarios = cancelled_abort_scenarios + 1;
            end
        end
    endtask

    initial begin
        $readmemh("input_fixture.hex", input_memory);
        $readmemh("channel0_weights.hex", weight_memory);
        $readmemh("expected_raw.hex", expected_raw);

        rst = 1'b1;
        abort = 1'b0;
        start_valid = 1'b0;
        mem_ready = 1'b0;
        tile_result_ready = 1'b0;
        error_ready = 1'b0;
        expect_bus = 1'b0;
        injected_error_code = 3'd0;
        injected_request_index = -1;
        transaction_request_count = 0;
        transaction_feature_reads = 0;
        transaction_weight_reads = 0;
        transaction_feature_bytes = 0;
        transaction_weight_bytes = 0;
        transaction_core_beats = 0;
        primary_feature_reads = 0;
        primary_weight_reads = 0;
        primary_feature_bytes = 0;
        primary_weight_bytes = 0;
        primary_core_beats = 0;
        total_stall_cycles = 0;
        completed_normal_runs = 0;
        memory_error_scenarios = 0;
        cancelled_abort_scenarios = 0;
        cancelled_reset_scenarios = 0;
        recovery_runs = 0;
        hold_stalled_request = 1'b0;
        stall_remaining = 4'd0;
        stall_active = 1'b0;
        force_long_stall = 1'b0;
        stall_prng_state = 32'h20260927;
        capture_primary = 1'b0;

        repeat (3) @(posedge clk);
        @(negedge clk);
        #1 rst = 1'b0;

        if ($test$plusargs("cancel_only")) begin
            cancel_pending_read(1'b0);
            $display("CANCEL_DIAG_COMPLETE abort_scenarios=%0d errors=%0d",
                     cancelled_abort_scenarios, 0);
            $finish;
        end else begin
        run_success(1'b1);
        if (primary_feature_reads != 1792 || primary_weight_reads != 512 ||
            primary_feature_bytes != 6656 || primary_weight_bytes != 512 ||
            primary_core_beats != 512) begin
            fail("primary G0 memory/read count 不匹配");
        end

        run_memory_error(3'd1, 0);
        run_success(1'b0);
        recovery_runs = recovery_runs + 1;
        run_memory_error(3'd2, 1);
        run_success(1'b0);
        recovery_runs = recovery_runs + 1;
        run_memory_error(3'd6, 1295);
        run_success(1'b0);
        recovery_runs = recovery_runs + 1;

        cancel_pending_read(1'b0);
        run_success(1'b0);
        recovery_runs = recovery_runs + 1;
        cancel_pending_read(1'b1);
        run_success(1'b0);
        recovery_runs = recovery_runs + 1;

        if (completed_normal_runs != 6 || memory_error_scenarios != 3 ||
            cancelled_abort_scenarios != 1 || cancelled_reset_scenarios != 1 ||
            recovery_runs != 5 || total_stall_cycles == 0) begin
            fail("成功运行、错误注入、取消或恢复覆盖计数不匹配");
        end
        $display("PASS: baseline_reads=2304 baseline_feature_reads=%0d baseline_weight_reads=%0d baseline_feature_bytes=%0d baseline_weight_bytes=%0d baseline_core_beats=%0d baseline_valid_values=26 tile_a_mask=65535 tile_b_mask=1023 normal_runs=%0d memory_error_codes=3 abort_pending_cancel=1 reset_pending_cancel=1 recovery_runs=%0d stall_cycles=%0d stall_seed=539363623 writes=0 errors=0",
                 primary_feature_reads, primary_weight_reads, primary_feature_bytes,
                 primary_weight_bytes, primary_core_beats, completed_normal_runs,
                 recovery_runs, total_stall_cycles);
        $finish;
        end
    end

    initial begin
        #100000000;
        $fatal(1, "TIMEOUT: row0 feeder testbench 超过仿真上限");
    end
endmodule
