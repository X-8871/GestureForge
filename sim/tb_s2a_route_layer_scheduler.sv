// S2A-T19：以 T10/T12 真实 byte-lane 协议检查 layer34 整层 route 调度。
`timescale 1ns/1ps
module tb_s2a_route_layer_scheduler;
    localparam logic [31:0] SOURCE0_BASE = 32'd27619968;
    localparam logic [31:0] SOURCE0_BYTES = 32'd86528;
    localparam logic [31:0] SOURCE1_BASE = 32'd26727936;
    localparam logic [31:0] SOURCE1_BYTES = 32'd173056;
    localparam logic [31:0] OUTPUT_BASE = 32'd27706496;
    localparam integer OUTPUT_BYTES = 259584;
    localparam integer INPUT_BYTES = 259584;
    localparam logic [31:0] RANDOM_SEED = 32'h2A20_2609;

    logic clk = 1'b0;
    logic hard_reset = 1'b1;
    logic abort = 1'b0;
    logic start_valid = 1'b0;
    logic start_ready;
    logic completion_ready = 1'b0;
    logic busy;
    logic done;
    logic error;
    logic [2:0] error_code;
    logic [18:0] completed_elements;

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

    logic mem_valid;
    logic mem_ready;
    logic mem_write;
    logic [31:0] mem_addr;
    logic [31:0] mem_wdata;
    logic [3:0] mem_rstrb;
    logic [3:0] mem_wstrb;
    logic [31:0] mem_rdata;
    logic [2:0] mem_error_code;
    logic memory_initialized;
    logic fault_inject_valid = 1'b0;
    logic [2:0] fault_inject_code = 3'd0;

    integer trace_file = 0;
    integer scoreboard_enable = 0;
    integer scoreboard_failed = 0;
    integer full_read_count = 0;
    integer full_write_count = 0;
    integer full_stall_count = 0;
    integer full_busy_start_checks = 0;
    integer completion_hold_count = 0;
    integer previous_progress = 0;
    integer accepted_reads_total = 0;
    integer accepted_writes_total = 0;
    integer error_responses_total = 0;
    integer observed_stall_cycles_total = 0;
    integer sampled_byte;
    integer byte_lane;
    integer timeout_count;
    integer hold_count;
    integer smoke_mode = 0;
    integer recovery_runs = 0;
    integer pending_read_abort_count = 0;
    integer pending_write_reset_count = 0;
    integer error_hold_count = 0;
    logic [31:0] random_state;
    logic [31:0] expected_address;

    always #5 clk = ~clk;

    s2a_route_layer_scheduler u_scheduler (
        .clk(clk),
        .hard_reset(hard_reset),
        .abort(abort),
        .start_valid(start_valid),
        .start_ready(start_ready),
        .completion_ready(completion_ready),
        .busy(busy),
        .done(done),
        .error(error),
        .error_code(error_code),
        .completed_elements(completed_elements),
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

    s2a_memory_master u_memory_master (
        .clk(clk),
        .hard_reset(hard_reset),
        .cancel(backend_cancel),
        .buffer_owner_pl(1'b1),
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
        .mem_valid(mem_valid),
        .mem_ready(mem_ready),
        .mem_write(mem_write),
        .mem_addr(mem_addr),
        .mem_wdata(mem_wdata),
        .mem_rstrb(mem_rstrb),
        .mem_wstrb(mem_wstrb),
        .mem_rdata(mem_rdata),
        .mem_error_code(mem_error_code)
    );

    s2a_memory_model #(
        .MAX_FEATURE_RANGES(64),
        .PATCH_CAPACITY(519168)
    ) u_memory (
        .clk(clk),
        .reset(hard_reset),
        .buffer_owner_pl(1'b1),
        .fault_inject_valid(fault_inject_valid),
        .fault_inject_code(fault_inject_code),
        .mem_valid(mem_valid),
        .mem_write(mem_write),
        .mem_addr(mem_addr),
        .mem_wdata(mem_wdata),
        .mem_rstrb(mem_rstrb),
        .mem_wstrb(mem_wstrb),
        .mem_ready(mem_ready),
        .mem_rdata(mem_rdata),
        .mem_error_code(mem_error_code),
        .model_initialized(memory_initialized)
    );

    function automatic logic [31:0] xorshift32(input logic [31:0] seed);
        logic [31:0] value;
        begin
            value = seed ^ (seed << 13);
            value = value ^ (value >> 17);
            value = value ^ (value << 5);
            xorshift32 = value;
        end
    endfunction

    function automatic logic [31:0] expected_source_byte_address(
        input integer output_index
    );
        integer source0_end;
        begin
            source0_end = 128 * 26 * 26;
            if (output_index < source0_end) begin
                expected_source_byte_address = SOURCE0_BASE + output_index;
            end else begin
                expected_source_byte_address = SOURCE1_BASE +
                                               (output_index - source0_end);
            end
        end
    endfunction

    task automatic initialize_full_inputs;
        integer index;
        integer signed value;
        begin
            random_state = RANDOM_SEED;
            for (index = 0; index < SOURCE0_BYTES; index = index + 1) begin
                random_state = xorshift32(random_state);
                value = (random_state % 32'd255) - 127;
                u_memory.store_byte(SOURCE0_BASE + index, value[7:0]);
                if ((index != 0) && ((index % 8192) == 0)) begin
                    $display("PROGRESS input_seed source0=%0d/%0d",
                             index, SOURCE0_BYTES);
                end
            end
            for (index = 0; index < SOURCE1_BYTES; index = index + 1) begin
                random_state = xorshift32(random_state);
                value = (random_state % 32'd255) - 127;
                u_memory.store_byte(SOURCE1_BASE + index, value[7:0]);
                if ((index != 0) && ((index % 8192) == 0)) begin
                    $display("PROGRESS input_seed source1=%0d/%0d",
                             index, SOURCE1_BYTES);
                end
            end
            if (u_memory.patch_count != INPUT_BYTES) begin
                $fatal(1, "输入预置唯一 byte 数量错误：%0d", u_memory.patch_count);
            end
            $display("PROGRESS input_seed complete=%0d", INPUT_BYTES);
        end
    endtask

    task automatic start_layer;
        begin
            @(negedge clk);
            if (!start_ready || busy || done || error) begin
                $fatal(1, "scheduler 未处于可启动状态");
            end
            start_valid = 1'b1;
            @(posedge clk);
            @(negedge clk);
            start_valid = 1'b0;
        end
    endtask

    task automatic wait_for_pending_read;
        begin
            timeout_count = 0;
            while (!(mem_valid && !mem_ready && !mem_write) && timeout_count < 1000) begin
                @(negedge clk);
                timeout_count = timeout_count + 1;
            end
            if (timeout_count == 1000) begin
                $fatal(1, "未观察到等待中的 feature read");
            end
        end
    endtask

    task automatic wait_for_pending_write;
        begin
            timeout_count = 0;
            while (!(mem_valid && !mem_ready && mem_write) && timeout_count < 1000) begin
                @(negedge clk);
                timeout_count = timeout_count + 1;
            end
            if (timeout_count == 1000) begin
                $fatal(1, "未观察到等待中的 feature write");
            end
        end
    endtask

    task automatic run_abort_and_reset_cases;
        integer writes_at_abort;
        integer writes_at_reset;
        begin
            start_layer();
            while (completed_elements < 19'd2) @(negedge clk);
            wait_for_pending_read();
            writes_at_abort = accepted_writes_total;
            abort = 1'b1;
            @(posedge clk);
            @(negedge clk);
            abort = 1'b0;
            repeat (4) @(posedge clk);
            if (busy || done || error || !start_ready ||
                accepted_writes_total != writes_at_abort) begin
                $fatal(1, "pending read abort 后状态或写副作用错误");
            end
            pending_read_abort_count = pending_read_abort_count + 1;

            start_layer();
            wait_for_pending_write();
            writes_at_reset = accepted_writes_total;
            hard_reset = 1'b1;
            repeat (2) @(posedge clk);
            @(negedge clk);
            hard_reset = 1'b0;
            repeat (4) @(posedge clk);
            if (busy || done || error || !start_ready ||
                accepted_writes_total != writes_at_reset) begin
                $fatal(1, "pending write hard reset 后状态或写副作用错误");
            end
            pending_write_reset_count = pending_write_reset_count + 1;
        end
    endtask

    task automatic run_error_hold_case;
        begin
            fault_inject_code = 3'd6;
            fault_inject_valid = 1'b1;
            start_layer();
            timeout_count = 0;
            while (!error && timeout_count < 1000) begin
                @(negedge clk);
                timeout_count = timeout_count + 1;
            end
            if (!error || error_code != 3'd6 || done || busy ||
                completed_elements != 19'd0) begin
                $fatal(1, "backend error 未传播到 scheduler");
            end
            fault_inject_valid = 1'b0;
            fault_inject_code = 3'd0;
            for (hold_count = 0; hold_count < 3; hold_count = hold_count + 1) begin
                @(posedge clk);
                #1;
                if (!error || error_code != 3'd6 || start_ready) begin
                    $fatal(1, "scheduler error 未保持到 completion_ready");
                end
                error_hold_count = error_hold_count + 1;
            end
            @(negedge clk);
            completion_ready = 1'b1;
            @(posedge clk);
            @(negedge clk);
            completion_ready = 1'b0;
            if (!start_ready || error || error_code != 3'd0) begin
                $fatal(1, "错误 completion 握手后未恢复空闲");
            end
        end
    endtask

    always @(posedge clk) begin
        if (mem_valid && mem_ready) begin
            if (mem_error_code == 3'd0) begin
                if (mem_write) begin
                    accepted_writes_total = accepted_writes_total + 1;
                end else begin
                    accepted_reads_total = accepted_reads_total + 1;
                end
            end else begin
                error_responses_total = error_responses_total + 1;
            end
            if (mem_write && scoreboard_enable != 0 && mem_error_code == 3'd0) begin
                byte_lane = -1;
                for (integer lane_index = 0; lane_index < 4; lane_index = lane_index + 1) begin
                    if (mem_wstrb[lane_index]) begin
                        if (byte_lane != -1) begin
                            scoreboard_failed = 1;
                        end
                        byte_lane = lane_index;
                    end
                end
                if ((byte_lane < 0) ||
                    (mem_addr[1:0] != 2'b00) ||
                    (mem_wstrb != (4'b0001 << ((OUTPUT_BASE + full_write_count) & 3))) ||
                    ((mem_addr + byte_lane) != (OUTPUT_BASE + full_write_count))) begin
                    scoreboard_failed = 1;
                    $fatal(1, "输出地址/lane 次序错误 index=%0d addr=%08x strobe=%x",
                           full_write_count, mem_addr, mem_wstrb);
                end
                sampled_byte = (mem_wdata >> (byte_lane * 8)) & 255;
                if (scoreboard_enable == 2) begin
                    if ((full_write_count >= 2) ||
                        (sampled_byte != ((full_write_count == 0) ? 21 : 219))) begin
                        $fatal(1, "smoke 输出值错误 index=%0d value=%0d",
                               full_write_count, sampled_byte);
                    end
                end
                if (trace_file != 0) begin
                    $fdisplay(trace_file, "%02x", sampled_byte);
                end
                full_write_count = full_write_count + 1;
            end else if (!mem_write && scoreboard_enable == 1 && mem_error_code == 3'd0) begin
                byte_lane = -1;
                for (integer lane_index = 0; lane_index < 4; lane_index = lane_index + 1) begin
                    if (mem_rstrb[lane_index]) begin
                        if (byte_lane != -1) begin
                            scoreboard_failed = 1;
                        end
                        byte_lane = lane_index;
                    end
                end
                expected_address = expected_source_byte_address(full_read_count);
                if ((byte_lane < 0) ||
                    (mem_addr[1:0] != 2'b00) ||
                    (mem_rstrb != (4'b0001 << (expected_address & 3))) ||
                    ((mem_addr + byte_lane) != expected_address)) begin
                    scoreboard_failed = 1;
                    $fatal(1, "输入 source/channel/lane 次序错误 index=%0d expected=%08x addr=%08x strobe=%x",
                           full_read_count, expected_address, mem_addr, mem_rstrb);
                end
                full_read_count = full_read_count + 1;
            end
        end
        if (scoreboard_enable != 0 && mem_valid && !mem_ready) begin
            observed_stall_cycles_total = observed_stall_cycles_total + 1;
            if (scoreboard_enable == 1) begin
                full_stall_count = full_stall_count + 1;
            end
        end
        if (scoreboard_enable != 0 && busy && completed_elements >= 19'd8192 &&
            (completed_elements % 19'd8192) == 0 &&
            completed_elements != previous_progress) begin
            previous_progress = completed_elements;
            $display("PROGRESS output_elements=%0d/%0d reads=%0d writes=%0d",
                     completed_elements, OUTPUT_BYTES, full_read_count, full_write_count);
        end
    end

    initial begin
        smoke_mode = $test$plusargs("SMOKE");
        repeat (3) @(posedge clk);
        while (!memory_initialized) @(posedge clk);
        @(negedge clk);
        hard_reset = 1'b0;

        if (smoke_mode != 0) begin
            u_memory.store_byte(SOURCE0_BASE, 8'h17);
            u_memory.store_byte(SOURCE0_BASE + 1, 8'hD7);
            scoreboard_enable = 2;
        end else begin
            initialize_full_inputs();
        end

        run_abort_and_reset_cases();
        run_error_hold_case();

        if (smoke_mode != 0) begin
            if ((full_write_count != 2) || (scoreboard_failed != 0) ||
                (error_responses_total != 1)) begin
                $fatal(1, "smoke output/error scoreboard 失败");
            end
            scoreboard_enable = 0;
            $display("RESULT mode=SMOKE pending_read_abort=%0d pending_write_reset=%0d error_hold=%0d partial_writes=%0d stalls=%0d error_responses=%0d",
                     pending_read_abort_count, pending_write_reset_count,
                     error_hold_count, full_write_count, observed_stall_cycles_total,
                     error_responses_total);
            $display("PASS S2A-T19 focused smoke");
            $finish;
        end

        full_read_count = 0;
        full_write_count = 0;
        full_stall_count = 0;
        previous_progress = 0;
        scoreboard_failed = 0;
        trace_file = $fopen("observed_output_hex.txt", "w");
        if (trace_file == 0) begin
            $fatal(1, "无法创建 output trace");
        end
        scoreboard_enable = 1;
        recovery_runs = recovery_runs + 1;
        start_layer();
        repeat (3) begin
            @(negedge clk);
            if (!busy || start_ready) begin
                $fatal(1, "busy 时错误接受了 start backpressure 请求");
            end
            start_valid = 1'b1;
            @(posedge clk);
            @(negedge clk);
            start_valid = 1'b0;
            full_busy_start_checks = full_busy_start_checks + 1;
        end
        timeout_count = 0;
        while (!done && !error && timeout_count < 5000000) begin
            @(negedge clk);
            timeout_count = timeout_count + 1;
        end
        if (!done || error || error_code != 3'd0 ||
            completed_elements != OUTPUT_BYTES ||
            full_read_count != OUTPUT_BYTES || full_write_count != OUTPUT_BYTES ||
            scoreboard_failed != 0) begin
            $fatal(1, "full layer 计数/完成状态错误 done=%0d error=%0d code=%0d elements=%0d reads=%0d writes=%0d",
                   done, error, error_code, completed_elements,
                   full_read_count, full_write_count);
        end
        $fclose(trace_file);
        trace_file = 0;
        scoreboard_enable = 0;
        for (hold_count = 0; hold_count < 3; hold_count = hold_count + 1) begin
            @(posedge clk);
            #1;
            if (!done || busy || start_ready || completed_elements != OUTPUT_BYTES) begin
                $fatal(1, "done 未保持到 completion_ready");
            end
            completion_hold_count = completion_hold_count + 1;
        end
        @(negedge clk);
        completion_ready = 1'b1;
        @(posedge clk);
        @(negedge clk);
        completion_ready = 1'b0;
        if (!start_ready || done || error) begin
            $fatal(1, "done completion 握手后 scheduler 未恢复");
        end
        if ((u_memory.patch_count != INPUT_BYTES + OUTPUT_BYTES) ||
            (pending_read_abort_count != 1) || (pending_write_reset_count != 1) ||
            (error_hold_count != 3) || (full_busy_start_checks != 3) ||
            (completion_hold_count != 3) || (error_responses_total != 1) ||
            (recovery_runs != 1) || (full_stall_count < 100000)) begin
            $fatal(1, "full protocol counters/patch count 不符合验收");
        end
        $display("RESULT mode=FULL output_count=%0d reads=%0d writes=%0d stalls=%0d pending_read_abort=%0d pending_write_reset=%0d error_hold=%0d busy_start_checks=%0d completion_hold=%0d recovery_runs=%0d input_patches=%0d output_patches=%0d error_responses=%0d",
                 full_write_count, full_read_count, full_write_count,
                 full_stall_count, pending_read_abort_count,
                 pending_write_reset_count, error_hold_count,
                 full_busy_start_checks, completion_hold_count, recovery_runs,
                 INPUT_BYTES, OUTPUT_BYTES, error_responses_total);
        $display("PASS S2A-T19 complete layer34 route scheduler");
        $finish;
    end
endmodule
