`timescale 1ns/1ps
// S2A-T18：以 T10 byte-lane memory model 验证 tiny416 layer33 整层调度。
module tb_s2a_upsample_layer_scheduler;
    logic clk = 1'b0;
    always #5 clk = ~clk;

    localparam logic [31:0] INPUT_BASE = 32'd27598336;
    localparam logic [31:0] OUTPUT_BASE = 32'd27619968;
    localparam integer INPUT_BYTES = 21632;
    localparam integer OUTPUT_BYTES = 86528;

    logic hard_reset;
    logic abort;
    logic start_valid;
    logic start_ready;
    logic completion_ready;
    logic busy;
    logic done;
    logic error;
    logic [2:0] error_code;
    logic [16:0] completed_elements;

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
    logic model_initialized;
    logic fault_inject_valid;
    logic [2:0] fault_inject_code;

    integer run_mode_smoke;
    integer active_case;
    integer run_read_count;
    integer run_write_count;
    integer full_read_count;
    integer full_write_count;
    integer all_read_count;
    integer all_write_count;
    integer read_error_count;
    integer stall_cycle_count;
    integer pending_read_abort_count;
    integer pending_write_reset_count;
    integer busy_start_checks;
    integer completion_hold_checks;
    integer error_hold_checks;
    integer recovery_run_count;
    integer watchdog;
    integer output_fd;
    integer offset;
    integer channel_value;
    integer y_value;
    integer x_value;
    integer expected_byte_address;
    integer expected_lane;
    integer selected_lane;
    integer selected_value;
    logic [7:0] expected_byte;

    function automatic logic [7:0] initial_byte(input logic [31:0] address);
        begin
            initial_byte = address[7:0] ^ address[15:8] ^ address[23:16] ^
                           address[31:24] ^ 8'hA5;
        end
    endfunction

    function automatic logic [3:0] lane_mask(input logic [31:0] address);
        begin
            lane_mask = 4'b0001 << address[1:0];
        end
    endfunction

    s2a_upsample_layer_scheduler dut (
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
        .PATCH_CAPACITY(131072)
    ) u_memory_model (
        .clk(clk),
        .reset(hard_reset || abort),
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
        .model_initialized(model_initialized)
    );

    always @(posedge clk) begin
        if (hard_reset || abort) begin
            // reset/cancel 周期不接受 memory 请求。
        end else if (mem_valid && !mem_ready) begin
            stall_cycle_count = stall_cycle_count + 1;
        end else if (mem_valid && mem_ready) begin
            if (mem_write) begin
                offset = run_write_count;
                if (offset >= OUTPUT_BYTES) begin
                    $fatal(1, "FAIL: 输出写数量超过 layer33 长度");
                end
                channel_value = offset / (26 * 26);
                y_value = (offset % (26 * 26)) / 26;
                x_value = offset % 26;
                expected_byte_address = OUTPUT_BASE + offset;
                expected_lane = expected_byte_address % 4;
                expected_byte = initial_byte(INPUT_BASE +
                    ((channel_value * 13 + (y_value / 2)) * 13) + (x_value / 2));
                selected_value = (mem_wdata >> (expected_lane * 8)) & 255;
                if ((mem_error_code != 3'd0) ||
                    (mem_addr !== {expected_byte_address[31:2], 2'b00}) ||
                    (mem_rstrb != 4'd0) ||
                    (mem_wstrb !== (4'b0001 << expected_lane)) ||
                    (selected_value != expected_byte)) begin
                    $fatal(1, "FAIL: 输出 byte 顺序、lane、地址或值错误 index=%0d addr=%08x lane=%0d got=%02x expected=%02x error=%0d",
                           offset, mem_addr, expected_lane, selected_value,
                           expected_byte, mem_error_code);
                end
                run_write_count = run_write_count + 1;
                all_write_count = all_write_count + 1;
                if (active_case == 4) begin
                    full_write_count = full_write_count + 1;
                    $fwrite(output_fd, "%02x\n", selected_value);
                    if ((full_write_count % 4096) == 0) begin
                        $display("PROGRESS full outputs=%0d reads=%0d stalls=%0d",
                                 full_write_count, full_read_count, stall_cycle_count);
                    end
                end
            end else begin
                if (mem_error_code != 3'd0) begin
                    read_error_count = read_error_count + 1;
                end else begin
                    offset = run_read_count;
                    if (offset >= OUTPUT_BYTES) begin
                        $fatal(1, "FAIL: 特征读取数量超过 layer33 长度");
                    end
                    channel_value = offset / (26 * 26);
                    y_value = (offset % (26 * 26)) / 26;
                    x_value = offset % 26;
                    expected_byte_address = INPUT_BASE +
                        ((channel_value * 13 + (y_value / 2)) * 13) + (x_value / 2);
                    expected_lane = expected_byte_address % 4;
                    selected_lane = (mem_rstrb >> expected_lane) & 1;
                    if ((mem_addr !== {expected_byte_address[31:2], 2'b00}) ||
                        (mem_rstrb !== (4'b0001 << expected_lane)) ||
                        (mem_wstrb != 4'd0) || !selected_lane) begin
                        $fatal(1, "FAIL: 特征读取顺序、lane 或地址错误 index=%0d addr=%08x expected=%08x rstrb=%x",
                               offset, mem_addr, expected_byte_address, mem_rstrb);
                    end
                    run_read_count = run_read_count + 1;
                    all_read_count = all_read_count + 1;
                    if (active_case == 4) begin
                        full_read_count = full_read_count + 1;
                    end
                end
            end
        end
    end

    task automatic start_layer(input integer case_number);
        integer wait_cycles;
        begin
            active_case = case_number;
            run_read_count = 0;
            run_write_count = 0;
            @(negedge clk);
            start_valid = 1'b1;
            wait_cycles = 0;
            while (!start_ready) begin
                @(negedge clk);
                wait_cycles = wait_cycles + 1;
                if (wait_cycles > 20) begin
                    $fatal(1, "FAIL: scheduler start_ready timeout");
                end
            end
            @(posedge clk);
            @(negedge clk);
            start_valid = 1'b0;
        end
    endtask

    task automatic wait_error(input logic [2:0] expected_code);
        integer wait_cycles;
        begin
            wait_cycles = 0;
            while (!error) begin
                @(negedge clk);
                wait_cycles = wait_cycles + 1;
                if (wait_cycles > 1000) begin
                    $fatal(1, "FAIL: scheduler error timeout");
                end
            end
            if (busy || done || (error_code !== expected_code)) begin
                $fatal(1, "FAIL: scheduler error outputs busy=%0d done=%0d code=%0d",
                       busy, done, error_code);
            end
        end
    endtask

    task automatic wait_pending_read;
        integer wait_cycles;
        begin
            wait_cycles = 0;
            while (!(mem_valid && !mem_ready && !mem_write)) begin
                @(negedge clk);
                wait_cycles = wait_cycles + 1;
                if (wait_cycles > 1000) begin
                    $fatal(1, "FAIL: 未到达 pending read stall");
                end
            end
        end
    endtask

    task automatic wait_pending_write;
        integer wait_cycles;
        begin
            wait_cycles = 0;
            while (!(mem_valid && !mem_ready && mem_write)) begin
                @(negedge clk);
                wait_cycles = wait_cycles + 1;
                if (wait_cycles > 1000) begin
                    $fatal(1, "FAIL: 未到达 pending write stall");
                end
            end
        end
    endtask

    task automatic ack_completion;
        begin
            @(negedge clk);
            completion_ready = 1'b1;
            @(posedge clk);
            @(negedge clk);
            completion_ready = 1'b0;
        end
    endtask

    initial begin
        integer writes_before_cancel;
        integer reads_before_cancel;
        integer saved_completed;
        integer cycles;
        integer error_reads_before_hold;
        integer error_writes_before_hold;

        hard_reset = 1'b1;
        abort = 1'b0;
        start_valid = 1'b0;
        completion_ready = 1'b0;
        fault_inject_valid = 1'b0;
        fault_inject_code = 3'd0;
        run_mode_smoke = $test$plusargs("SMOKE");
        active_case = 0;
        run_read_count = 0;
        run_write_count = 0;
        full_read_count = 0;
        full_write_count = 0;
        all_read_count = 0;
        all_write_count = 0;
        read_error_count = 0;
        stall_cycle_count = 0;
        pending_read_abort_count = 0;
        pending_write_reset_count = 0;
        busy_start_checks = 0;
        completion_hold_checks = 0;
        error_hold_checks = 0;
        recovery_run_count = 0;
        output_fd = 0;

        repeat (4) @(posedge clk);
        while (!model_initialized) @(posedge clk);
        @(negedge clk);
        hard_reset = 1'b0;

        // 验证 memory error 传播、错误保持与 ACK 后恢复。
        fault_inject_valid = 1'b1;
        fault_inject_code = 3'd6;
        start_layer(1);
        wait_error(3'd6);
        if ((run_write_count != 0) || (run_read_count != 0)) begin
            $fatal(1, "FAIL: 失败 read 产生了有效输入或 output write");
        end
        error_reads_before_hold = all_read_count;
        error_writes_before_hold = all_write_count;
        fault_inject_valid = 1'b0;
        fault_inject_code = 3'd0;
        repeat (3) begin
            @(posedge clk);
            if (!error || (error_code != 3'd6) || busy || done) begin
                $fatal(1, "FAIL: error completion 未保持稳定");
            end
            if ((all_read_count != error_reads_before_hold) ||
                (all_write_count != error_writes_before_hold)) begin
                $fatal(1, "FAIL: memory error 后仍有新的读写请求");
            end
            error_hold_checks = error_hold_checks + 1;
        end
        ack_completion();
        if (!start_ready || error || (error_code != 3'd0)) begin
            $fatal(1, "FAIL: error ACK 后未恢复到 idle");
        end

        // 在 feature read 尚未握手时 abort，并确认取消后没有延迟写入。
        start_layer(2);
        wait_pending_read();
        writes_before_cancel = all_write_count;
        reads_before_cancel = all_read_count;
        abort = 1'b1;
        @(posedge clk);
        @(negedge clk);
        abort = 1'b0;
        repeat (8) @(posedge clk);
        if ((all_write_count != writes_before_cancel) ||
            (all_read_count != reads_before_cancel) || busy || done || error) begin
            $fatal(1, "FAIL: abort pending read 后有延迟副作用或状态未清除");
        end
        pending_read_abort_count = pending_read_abort_count + 1;

        // 在第二个 output write 尚未握手时硬复位，并确认没有延迟写。
        start_layer(3);
        wait_pending_write();
        writes_before_cancel = all_write_count;
        reads_before_cancel = all_read_count;
        hard_reset = 1'b1;
        @(posedge clk);
        @(negedge clk);
        hard_reset = 1'b0;
        repeat (8) @(posedge clk);
        if ((all_write_count != writes_before_cancel) || busy || done || error ||
            !start_ready) begin
            $fatal(1, "FAIL: hard reset pending write 后有延迟写或状态未清除");
        end
        pending_write_reset_count = pending_write_reset_count + 1;

        if (run_mode_smoke != 0) begin
            // smoke 只检查若干连续坐标及运行中 abort；完整覆盖由 full 模式执行。
            start_layer(5);
            cycles = 0;
            while (completed_elements < 17'd16) begin
                @(negedge clk);
                cycles = cycles + 1;
                if (cycles > 10000) $fatal(1, "FAIL: smoke progress timeout");
            end
            saved_completed = completed_elements;
            writes_before_cancel = all_write_count;
            abort = 1'b1;
            @(posedge clk);
            @(negedge clk);
            abort = 1'b0;
            repeat (8) @(posedge clk);
            if ((saved_completed != 16) || (all_write_count != writes_before_cancel) ||
                busy || done || error) begin
                $fatal(1, "FAIL: smoke 中间 abort 后状态或写副作用错误");
            end
            $display("RESULT mode=SMOKE pending_read_abort=%0d pending_write_reset=%0d error_hold=%0d partial_writes=%0d stalls=%0d",
                     pending_read_abort_count, pending_write_reset_count,
                     error_hold_checks, run_write_count, stall_cycle_count);
            $display("PASS S2A-T18 focused smoke");
            $finish;
        end

        // 正常完整层运行，busy 时的 start 被忽略，done 直到确认才释放。
        output_fd = $fopen("observed_output_hex.txt", "w");
        if (output_fd == 0) $fatal(1, "FAIL: 无法创建全量 output trace");
        start_layer(4);
        if (start_ready || !busy || done || error) begin
            $fatal(1, "FAIL: start 接受后 busy/start_ready 状态错误");
        end
        start_valid = 1'b1;
        repeat (3) begin
            @(posedge clk);
            if (start_ready || !busy) $fatal(1, "FAIL: busy 时接受第二个 start");
            busy_start_checks = busy_start_checks + 1;
        end
        @(negedge clk);
        start_valid = 1'b0;

        watchdog = 0;
        while (!done && !error) begin
            @(negedge clk);
            watchdog = watchdog + 1;
            if (watchdog > 3000000) $fatal(1, "FAIL: full layer no-progress watchdog");
        end
        if (error || !done || busy || (completed_elements != 17'd86528) ||
            (full_read_count != OUTPUT_BYTES) || (full_write_count != OUTPUT_BYTES) ||
            (run_read_count != OUTPUT_BYTES) || (run_write_count != OUTPUT_BYTES)) begin
            $fatal(1, "FAIL: full coverage done=%0d error=%0d code=%0d completed=%0d reads=%0d writes=%0d",
                   done, error, error_code, completed_elements,
                   full_read_count, full_write_count);
        end
        if (stall_cycle_count < 200000) begin
            $fatal(1, "FAIL: T10 scheduled stall coverage is unexpectedly low: %0d",
                   stall_cycle_count);
        end
        repeat (3) begin
            @(posedge clk);
            if (!done || busy || start_ready) $fatal(1, "FAIL: done completion 未保持");
            completion_hold_checks = completion_hold_checks + 1;
        end
        $fclose(output_fd);
        ack_completion();
        recovery_run_count = 1;
        $display("RESULT mode=FULL output_count=%0d reads=%0d writes=%0d stalls=%0d error_responses=%0d pending_read_abort=%0d pending_write_reset=%0d busy_start_checks=%0d completion_hold=%0d error_hold=%0d recovery_runs=%0d cycles=%0d",
                 full_write_count, full_read_count, full_write_count,
                 stall_cycle_count, read_error_count, pending_read_abort_count,
                 pending_write_reset_count, busy_start_checks,
                 completion_hold_checks, error_hold_checks, recovery_run_count,
                 watchdog);
        $display("PASS S2A-T18 full layer33 scheduler");
        $finish;
    end
endmodule
