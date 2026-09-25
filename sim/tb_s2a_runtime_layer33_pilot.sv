`timescale 1ns/1ps
// S2A-T27：通过冻结 G0 shell 验证 layer33 完整单层运行与取消闭环。
module tb_s2a_runtime_layer33_pilot;
    logic clk = 1'b0;
    always #5 clk = ~clk;

    localparam logic [7:0] REG_CMD = 8'h00;
    localparam logic [7:0] REG_STATUS = 8'h04;
    localparam logic [7:0] REG_ERROR_CODE = 8'h08;
    localparam logic [7:0] REG_TIMEOUT = 8'h28;
    localparam logic [7:0] REG_ACK = 8'h3C;
    localparam logic [31:0] INPUT_BASE = 32'd27598336;
    localparam logic [31:0] OUTPUT_BASE = 32'd27619968;
    localparam integer INPUT_BYTES = 21632;
    localparam integer OUTPUT_BYTES = 86528;
    localparam integer CASE_TIMEOUT = 1;
    localparam integer CASE_HARD_RESET = 2;
    localparam integer CASE_SOFT_RESET = 3;
    localparam integer CASE_SUCCESS = 4;

    logic hard_reset = 1'b0;
    logic csr_valid = 1'b0;
    logic csr_ready;
    logic csr_write = 1'b0;
    logic [7:0] csr_addr = 8'd0;
    logic [31:0] csr_wdata = 32'd0;
    logic [31:0] csr_rdata;
    logic backend_start;
    logic backend_abort;
    logic busy;
    logic done;
    logic error;
    logic pl_owns_buffers;
    logic head_output_valid;
    logic child_busy;
    logic child_done;
    logic child_error;
    logic [2:0] child_error_code;
    logic [16:0] child_completed_elements;

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

    logic fault_inject_valid = 1'b0;
    logic [2:0] fault_inject_code = 3'd0;
    integer active_case = 0;
    integer terminal_event_count = 0;
    integer backend_abort_count = 0;
    logic backend_abort_previous = 1'b0;
    integer all_read_count = 0;
    integer all_write_count = 0;
    integer run_read_count = 0;
    integer run_write_count = 0;
    integer stall_cycle_count = 0;
    integer trace_fd = 0;
    integer lane;
    integer output_byte_address;
    integer output_offset;
    integer output_channel;
    integer output_y;
    integer output_x;
    integer input_offset;
    integer observed_byte;
    integer expected_byte;
    integer watchdog;
    integer writes_before_cancel;
    integer reads_before_cancel;
    integer run_terminal_before;

    function automatic logic [7:0] initial_byte(input logic [31:0] address);
        begin
            initial_byte = address[7:0] ^ address[15:8] ^ address[23:16] ^
                           address[31:24] ^ 8'hA5;
        end
    endfunction

    s2a_runtime_layer33_pilot dut (
        .clk(clk),
        .hard_reset(hard_reset),
        .csr_valid(csr_valid),
        .csr_ready(csr_ready),
        .csr_write(csr_write),
        .csr_addr(csr_addr),
        .csr_wdata(csr_wdata),
        .csr_rdata(csr_rdata),
        .backend_start(backend_start),
        .backend_abort(backend_abort),
        .busy(busy),
        .done(done),
        .error(error),
        .pl_owns_buffers(pl_owns_buffers),
        .head_output_valid(head_output_valid),
        .child_busy(child_busy),
        .child_done(child_done),
        .child_error(child_error),
        .child_error_code(child_error_code),
        .child_completed_elements(child_completed_elements),
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
        .reset(hard_reset || backend_abort || dut.soft_reset_now),
        .buffer_owner_pl(pl_owns_buffers),
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
        if (model_initialized &&
            (dut.child_backend_cancel !== dut.child_abort ||
             dut.u_runtime_shell.cancel_master !== dut.child_abort)) begin
            $fatal(1, "FAIL: scheduler cancel 与 G0 shell cancel 不一致");
        end
        if (dut.operator_result_valid) begin
            terminal_event_count = terminal_event_count + 1;
        end
        if (backend_abort && !backend_abort_previous) begin
            backend_abort_count = backend_abort_count + 1;
        end
        backend_abort_previous = backend_abort;
        if (hard_reset || backend_abort || dut.soft_reset_now) begin
        end else if (mem_valid && !mem_ready) begin
            stall_cycle_count = stall_cycle_count + 1;
        end else if (mem_valid && mem_ready) begin
            if (mem_error_code != 3'd0) begin
                $fatal(1, "FAIL: 意外 memory error code=%0d", mem_error_code);
            end
            if (!mem_write) begin
                all_read_count = all_read_count + 1;
                run_read_count = run_read_count + 1;
            end else begin
                if ((mem_rstrb != 4'd0) || (mem_wstrb == 4'd0) ||
                    ((mem_wstrb & (mem_wstrb - 4'd1)) != 4'd0)) begin
                    $fatal(1, "FAIL: 输出写入 byte lane 非法");
                end
                lane = 0;
                while (!mem_wstrb[lane]) begin
                    lane = lane + 1;
                end
                output_byte_address = mem_addr + lane;
                if ((output_byte_address < OUTPUT_BASE) ||
                    (output_byte_address >= OUTPUT_BASE + OUTPUT_BYTES)) begin
                    $fatal(1, "FAIL: 写入超出 layer33 输出范围 addr=%0d", output_byte_address);
                end
                output_offset = output_byte_address - OUTPUT_BASE;
                if ((active_case == CASE_SUCCESS) &&
                    (output_offset != run_write_count)) begin
                    $fatal(1, "FAIL: 输出写顺序错误 offset=%0d expected=%0d",
                           output_offset, run_write_count);
                end
                output_channel = output_offset / (26 * 26);
                output_y = (output_offset / 26) % 26;
                output_x = output_offset % 26;
                input_offset = (output_channel * 13 + (output_y / 2)) * 13 +
                               (output_x / 2);
                expected_byte = initial_byte(INPUT_BASE + input_offset);
                observed_byte = (mem_wdata >> (lane * 8)) & 8'hFF;
                if ((active_case == CASE_SUCCESS) &&
                    (observed_byte != expected_byte)) begin
                    $fatal(1, "FAIL: 输出 byte 不匹配 offset=%0d actual=%02x expected=%02x",
                           output_offset, observed_byte, expected_byte);
                end
                if ((active_case == CASE_SUCCESS) && (trace_fd != 0)) begin
                    $fdisplay(trace_fd, "%02x", observed_byte);
                end
                all_write_count = all_write_count + 1;
                run_write_count = run_write_count + 1;
                if ((active_case == CASE_SUCCESS) &&
                    ((run_write_count % 8192) == 0)) begin
                    $display("PROGRESS layer33 writes=%0d reads=%0d",
                             run_write_count, run_read_count);
                end
            end
        end
    end

    task automatic write_csr(input logic [7:0] address,
                             input logic [31:0] value);
        begin
            @(negedge clk);
            csr_valid = 1'b1;
            csr_write = 1'b1;
            csr_addr = address;
            csr_wdata = value;
            @(posedge clk);
            if (!csr_ready) $fatal(1, "FAIL: CSR write 未 ready");
            @(negedge clk);
            csr_valid = 1'b0;
            csr_write = 1'b0;
            csr_addr = 8'd0;
            csr_wdata = 32'd0;
        end
    endtask

    task automatic wait_pending_write;
        integer wait_cycles;
        begin
            wait_cycles = 0;
            while (!(mem_valid && mem_write && !mem_ready)) begin
                @(negedge clk);
                wait_cycles = wait_cycles + 1;
                if (wait_cycles > 100000) begin
                    $fatal(1, "FAIL: 未观察到未握手的 layer33 写请求");
                end
            end
        end
    endtask

    task automatic wait_for_terminal;
        integer wait_cycles;
        begin
            wait_cycles = 0;
            while (!done && !error) begin
                @(negedge clk);
                wait_cycles = wait_cycles + 1;
                if (wait_cycles > 2500000) begin
                    $fatal(1, "FAIL: G0 shell-child terminal watchdog 到期");
                end
            end
        end
    endtask

    initial begin
        active_case = 0;
        terminal_event_count = 0;
        backend_abort_count = 0;
        all_read_count = 0;
        all_write_count = 0;
        run_read_count = 0;
        run_write_count = 0;
        stall_cycle_count = 0;
        trace_fd = 0;

        hard_reset = 1'b1;
        repeat (3) @(posedge clk);
        @(negedge clk);
        hard_reset = 1'b0;
        wait (model_initialized);
        repeat (2) @(posedge clk);
        @(negedge clk);
        backend_abort_count = 0;

        // 短 deadline 必须由 G0 全任务计数触发并中止正在运行的 child。
        active_case = CASE_TIMEOUT;
        run_read_count = 0;
        run_write_count = 0;
        terminal_event_count = 0;
        write_csr(REG_TIMEOUT, 32'd24);
        write_csr(REG_CMD, 32'd1);
        wait_for_terminal();
        if (!error || done || busy || pl_owns_buffers || head_output_valid ||
            (csr_rdata != 32'd0)) begin
            $fatal(1, "FAIL: timeout 后 G0 状态/ownership/head 不正确");
        end
        csr_valid = 1'b1;
        csr_write = 1'b0;
        csr_addr = REG_STATUS;
        #1;
        if (csr_rdata[3:0] != 4'b0100) begin
            $fatal(1, "FAIL: G0 STATUS timeout 位字段错误 value=%h", csr_rdata);
        end
        csr_addr = REG_ERROR_CODE;
        #1;
        if (csr_rdata[2:0] != 3'd5) $fatal(1, "FAIL: G0 timeout code 不是 5");
        csr_valid = 1'b0;
        csr_addr = 8'd0;
        if (!backend_abort || !child_busy) begin
            $fatal(1, "FAIL: G0 timeout 未触发 child abort");
        end
        run_terminal_before = terminal_event_count;
        writes_before_cancel = all_write_count;
        repeat (12) @(posedge clk);
        if ((terminal_event_count != run_terminal_before) ||
            (all_write_count != writes_before_cancel) || child_busy ||
            !error || (terminal_event_count != 0) ||
            (run_read_count + run_write_count == 0)) begin
            $fatal(1, "FAIL: timeout 后出现迟到事件/写入，或 timeout 前无 child 活动");
        end
        if (backend_abort_count != 1) begin
            $fatal(1, "FAIL: timeout backend_abort 次数=%0d", backend_abort_count);
        end
        $display("CHECK timeout abort=1 terminal_events=%0d reads=%0d writes=%0d",
                 terminal_event_count, run_read_count, run_write_count);
        write_csr(REG_ACK, 32'd2);

        // 硬复位发生在 memory model 尚未接受的输出写停顿期间。
        active_case = CASE_HARD_RESET;
        run_read_count = 0;
        run_write_count = 0;
        terminal_event_count = 0;
        write_csr(REG_TIMEOUT, 32'd1100000);
        write_csr(REG_CMD, 32'd1);
        wait_pending_write();
        writes_before_cancel = all_write_count;
        reads_before_cancel = all_read_count;
        hard_reset = 1'b1;
        @(posedge clk);
        @(negedge clk);
        hard_reset = 1'b0;
        repeat (12) @(posedge clk);
        if ((all_write_count != writes_before_cancel) ||
            (all_read_count != reads_before_cancel) || busy || done || error ||
            pl_owns_buffers || child_busy || (child_completed_elements != 0) ||
            (terminal_event_count != 0)) begin
            $fatal(1, "FAIL: 硬复位取消 pending write 后状态/副作用错误");
        end
        $display("CHECK hard_reset pending_write=1 late_writes=0");

        // 软复位也必须使用 G0 接受的 CMD[1] 与相同 cancel 组合路径。
        active_case = CASE_SOFT_RESET;
        run_read_count = 0;
        run_write_count = 0;
        terminal_event_count = 0;
        write_csr(REG_TIMEOUT, 32'd1100000);
        write_csr(REG_CMD, 32'd1);
        wait_pending_write();
        writes_before_cancel = all_write_count;
        reads_before_cancel = all_read_count;
        write_csr(REG_CMD, 32'd2);
        repeat (12) @(posedge clk);
        if ((all_write_count != writes_before_cancel) ||
            (all_read_count != reads_before_cancel) || busy || done || error ||
            pl_owns_buffers || child_busy || (child_completed_elements != 0) ||
            (terminal_event_count != 0)) begin
            $fatal(1, "FAIL: 软复位取消 pending write 后状态/副作用错误");
        end
        $display("CHECK soft_reset pending_write=1 late_writes=0");

        if ($test$plusargs("QUICK")) begin
            $display("RESULT mode=QUICK timeout_abort=1 hard_reset_pending_write=1 soft_reset_pending_write=1");
            $display("PASS S2A-T27 G0 shell-child control smoke");
            $finish;
        end

        // 软复位后的合法恢复运行输出完整 86,528 byte trace。
        active_case = CASE_SUCCESS;
        run_read_count = 0;
        run_write_count = 0;
        terminal_event_count = 0;
        backend_abort_count = 0;
        write_csr(REG_TIMEOUT, 32'd1100000);
        trace_fd = $fopen("observed_output_hex.txt", "w");
        if (trace_fd == 0) $fatal(1, "FAIL: 无法创建逐 byte 输出 trace");
        write_csr(REG_CMD, 32'd1);
        wait_for_terminal();
        if (error || !done || busy || pl_owns_buffers || !head_output_valid ||
            child_busy || child_error || (child_completed_elements != 17'd86528) ||
            (run_read_count != OUTPUT_BYTES) || (run_write_count != OUTPUT_BYTES) ||
            (terminal_event_count != 1) || (backend_abort_count != 0) ||
            (stall_cycle_count == 0)) begin
            $fatal(1, "FAIL: 成功层运行状态或计数不符 done=%0d error=%0d reads=%0d writes=%0d events=%0d",
                   done, error, run_read_count, run_write_count, terminal_event_count);
        end
        csr_valid = 1'b1;
        csr_write = 1'b0;
        csr_addr = REG_STATUS;
        #1;
        if (csr_rdata[3:0] != 4'b0010) begin
            $fatal(1, "FAIL: G0 STATUS success 位字段错误 value=%h", csr_rdata);
        end
        csr_valid = 1'b0;
        csr_addr = 8'd0;
        $fclose(trace_fd);
        trace_fd = 0;
        $display("RESULT layer33_bytes=%0d reads=%0d writes=%0d terminal_events=%0d stalls=%0d timeout_abort=1 hard_reset_pending_write=1 soft_reset_pending_write=1 recovery=1",
                 run_write_count, run_read_count, run_write_count,
                 terminal_event_count, stall_cycle_count);
        $display("PASS S2A-T27 G0 shell-child layer33 pilot");
        $finish;
    end
endmodule
