`timescale 1ns/1ps
// S2A-T28：验证 G0 runtime shell 串行调度 layer33 与 layer34。
module tb_s2a_runtime_layers33_34_pilot;
    logic clk = 1'b0;
    always #5 clk = ~clk;

    localparam logic [7:0] REG_CMD = 8'h00;
    localparam logic [7:0] REG_STATUS = 8'h04;
    localparam logic [7:0] REG_ERROR_CODE = 8'h08;
    localparam logic [7:0] REG_TIMEOUT = 8'h28;
    localparam logic [7:0] REG_ACK = 8'h3C;
    localparam logic [31:0] LAYER32_BASE = 32'd27598336;
    localparam logic [31:0] LAYER32_BYTES = 32'd21632;
    localparam logic [31:0] LAYER33_BASE = 32'd27619968;
    localparam logic [31:0] LAYER33_BYTES = 32'd86528;
    localparam logic [31:0] LAYER23_BASE = 32'd26727936;
    localparam logic [31:0] LAYER23_BYTES = 32'd173056;
    localparam logic [31:0] LAYER34_BASE = 32'd27706496;
    localparam logic [31:0] LAYER34_BYTES = 32'd259584;
    localparam logic [31:0] FULL_TASK_TIMEOUT_CYCLES = 32'd8000000;
    localparam integer CASE_TIMEOUT = 1;
    localparam integer CASE_MEMORY_ERROR = 2;
    localparam integer CASE_HARD_RESET = 3;
    localparam integer CASE_SOFT_RESET = 4;
    localparam integer CASE_SUCCESS = 5;
    localparam integer READ_INPUT = 0;
    localparam integer READ_WEIGHTS = 1;
    localparam integer READ_FEATURE = 2;
    localparam integer WRITE_FEATURE = 3;

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
    logic [1:0] active_stage;
    logic [16:0] layer33_completed_elements;
    logic [18:0] layer34_completed_elements;

    logic mem_valid;
    logic mem_ready;
    logic mem_write;
    logic [31:0] mem_addr;
    logic [31:0] mem_wdata;
    logic [3:0] mem_rstrb;
    logic [3:0] mem_wstrb;
    logic [31:0] mem_rdata;
    logic [2:0] mem_error_code;
    logic model_initialized = 1'b0;
    logic model_reset;

    logic fault_inject_valid = 1'b0;
    logic [2:0] fault_inject_code = 3'd0;
    integer active_case = 0;
    integer terminal_event_count = 0;
    integer backend_start_count = 0;
    integer backend_abort_count = 0;
    integer layer33_start_count = 0;
    integer layer34_start_count = 0;
    integer accepted_read_count = 0;
    integer accepted_write_count = 0;
    integer layer32_read_count = 0;
    integer route_source0_read_count = 0;
    integer route_source1_read_count = 0;
    integer layer33_write_count = 0;
    integer layer34_write_count = 0;
    integer stall_cycle_count = 0;
    integer error_response_count = 0;
    integer trace33_fd = 0;
    integer trace34_fd = 0;
    integer comb_lane_index;
    integer lane_index;
    integer byte_address;
    integer byte_offset;
    integer observed_byte;
    integer output_element_index;
    integer output_channel_index;
    integer output_y_index;
    integer output_x_index;
    integer expected_input_offset;
    integer active_class;
    integer comb_request_class;
    integer wait_cycles;
    integer request_stall_expected = 0;
    integer request_stall_observed = 0;
    integer class_index;
    integer watchdog;
    integer global_cycle_count = 0;
    integer full_start_cycle = 0;
    integer full_terminal_cycle = 0;
    integer full_elapsed_cycles = 0;
    integer reads_before_cancel;
    integer writes_before_cancel;
    integer terminals_before_cancel;
    integer terminal_event_count_previous = 0;
    logic backend_abort_previous = 1'b0;
    logic [31:0] accepted_mem_addr;
    logic [31:0] accepted_mem_wdata;
    logic [3:0] accepted_mem_rstrb;
    logic [3:0] accepted_mem_wstrb;
    logic accepted_mem_write;
    logic accepted_fault_valid;
    logic [2:0] accepted_fault_code;

    logic [7:0] layer32_input [0:LAYER32_BYTES-1];
    logic [7:0] layer23_input [0:LAYER23_BYTES-1];
    logic [7:0] expected_layer33 [0:LAYER33_BYTES-1];
    logic [7:0] expected_layer34 [0:LAYER34_BYTES-1];
    logic [7:0] layer33_memory [0:LAYER33_BYTES-1];
    logic [7:0] layer34_memory [0:LAYER34_BYTES-1];
    logic layer33_initialized [0:LAYER33_BYTES-1];
    logic layer34_initialized [0:LAYER34_BYTES-1];

    logic memory_pending = 1'b0;
    integer memory_stall_remaining = 0;
    integer memory_stall_index [0:3];
    integer accepted_by_class [0:3];
    integer stall_cycles_by_class [0:3];
    integer scheduled_stalls_by_class [0:3];
    logic [31:0] held_addr;
    logic [31:0] held_wdata;
    logic [3:0] held_rstrb;
    logic [3:0] held_wstrb;
    logic held_write;
    logic held_fault_valid;
    logic [2:0] held_fault_code;

    s2a_runtime_layers33_34_pilot dut (
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
        .active_stage(active_stage),
        .layer33_completed_elements(layer33_completed_elements),
        .layer34_completed_elements(layer34_completed_elements),
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

    assign model_reset = hard_reset || backend_abort || dut.soft_reset_now;

    function automatic integer scheduled_stall(input integer schedule_index);
        begin
            case (schedule_index % 5)
                0: scheduled_stall = 0;
                1: scheduled_stall = 1;
                2: scheduled_stall = 2;
                3: scheduled_stall = 7;
                default: scheduled_stall = 3;
            endcase
        end
    endfunction

    function automatic integer request_class(
        input logic write_request,
        input logic [31:0] word_address
    );
        begin
            if (write_request &&
                (((word_address >= LAYER33_BASE) &&
                  (word_address < LAYER33_BASE + LAYER33_BYTES)) ||
                 ((word_address >= LAYER34_BASE) &&
                  (word_address < LAYER34_BASE + LAYER34_BYTES)))) begin
                request_class = WRITE_FEATURE;
            end else if (!write_request &&
                         (((word_address >= LAYER32_BASE) &&
                           (word_address < LAYER32_BASE + LAYER32_BYTES)) ||
                          ((word_address >= LAYER33_BASE) &&
                           (word_address < LAYER33_BASE + LAYER33_BYTES)) ||
                          ((word_address >= LAYER23_BASE) &&
                           (word_address < LAYER23_BASE + LAYER23_BYTES)))) begin
                request_class = READ_FEATURE;
            end else begin
                request_class = -1;
            end
        end
    endfunction

    function automatic logic [7:0] read_byte(input logic [31:0] address);
        integer offset;
        begin
            read_byte = 8'd0;
            if ((address >= LAYER32_BASE) &&
                (address < LAYER32_BASE + LAYER32_BYTES)) begin
                offset = address - LAYER32_BASE;
                read_byte = layer32_input[offset];
            end else if ((address >= LAYER33_BASE) &&
                         (address < LAYER33_BASE + LAYER33_BYTES)) begin
                offset = address - LAYER33_BASE;
                read_byte = layer33_memory[offset];
            end else if ((address >= LAYER23_BASE) &&
                         (address < LAYER23_BASE + LAYER23_BYTES)) begin
                offset = address - LAYER23_BASE;
                read_byte = layer23_input[offset];
            end
        end
    endfunction

    always_comb begin
        mem_ready = 1'b0;
        mem_rdata = 32'd0;
        mem_error_code = 3'd0;
        comb_request_class = request_class(mem_write, mem_addr);
        if (model_initialized && !model_reset && pl_owns_buffers && mem_valid) begin
            if (memory_pending) begin
                if (memory_stall_remaining == 0) mem_ready = 1'b1;
            end else if ((comb_request_class >= READ_FEATURE) &&
                         (comb_request_class <= WRITE_FEATURE)) begin
                if (scheduled_stall(memory_stall_index[comb_request_class]) == 0) begin
                    mem_ready = 1'b1;
                end
            end
        end
        if (mem_ready) begin
            if (fault_inject_valid) begin
                mem_error_code = fault_inject_code;
            end
            if (!mem_write && !fault_inject_valid) begin
                for (comb_lane_index = 0; comb_lane_index < 4;
                     comb_lane_index = comb_lane_index + 1) begin
                    if (mem_rstrb[comb_lane_index]) begin
                        mem_rdata[comb_lane_index*8 +: 8] =
                            read_byte(mem_addr + comb_lane_index);
                    end
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

    task automatic wait_for_terminal;
        integer cycles;
        begin
            cycles = 0;
            while (!done && !error) begin
                @(negedge clk);
                cycles = cycles + 1;
                if (cycles > 10000000) $fatal(1, "FAIL: shell terminal watchdog 到期");
            end
        end
    endtask

    task automatic wait_for_pending_write;
        integer cycles;
        begin
            cycles = 0;
            while (!(mem_valid && mem_write && !mem_ready)) begin
                @(negedge clk);
                cycles = cycles + 1;
                if (cycles > 500000) $fatal(1, "FAIL: 未观察到被停顿的输出写请求");
            end
        end
    endtask

    task automatic wait_for_route_stage;
        integer cycles;
        begin
            cycles = 0;
            while ((active_stage != 2'd2) || (layer34_start_count == 0)) begin
                @(negedge clk);
                cycles = cycles + 1;
                if (cycles > 7000000) $fatal(1, "FAIL: layer33 后未启动 layer34");
            end
        end
    endtask

    task automatic accept_current_request;
        begin
            if (!mem_ready) $fatal(1, "FAIL: responder 在 ready-low 时执行了请求");
            if (request_stall_observed != request_stall_expected) begin
                $fatal(1, "FAIL: class=%0d low-ready rising edges=%0d expected=%0d",
                       active_class, request_stall_observed, request_stall_expected);
            end
            if ((mem_addr[1:0] != 2'b00)) begin
                $fatal(1, "FAIL: memory word address 未对齐 %08x", mem_addr);
            end
            if (mem_error_code != 3'd0) begin
                error_response_count = error_response_count + 1;
            end else if (!mem_write) begin
                if ((mem_wstrb != 4'd0) || (mem_rstrb == 4'd0) ||
                    ((mem_rstrb & (mem_rstrb - 4'd1)) != 4'd0)) begin
                    $fatal(1, "FAIL: read strobe 非法 r=%x w=%x", mem_rstrb, mem_wstrb);
                end
                lane_index = 0;
                while (!mem_rstrb[lane_index]) lane_index = lane_index + 1;
                byte_address = mem_addr + lane_index;
                accepted_read_count = accepted_read_count + 1;
                if (active_stage == 2'd1) begin
                    output_element_index = layer32_read_count;
                    output_channel_index = output_element_index / (26 * 26);
                    output_y_index = (output_element_index / 26) % 26;
                    output_x_index = output_element_index % 26;
                    expected_input_offset =
                        (output_channel_index * 13 + (output_y_index / 2)) * 13 +
                        (output_x_index / 2);
                    if ((byte_address < LAYER32_BASE) ||
                        (byte_address >= LAYER32_BASE + LAYER32_BYTES) ||
                        (byte_address != LAYER32_BASE + expected_input_offset)) begin
                        $fatal(1, "FAIL: layer33 source read 地址错误 output_index=%0d addr=%0d expected=%0d",
                               layer32_read_count, byte_address,
                               LAYER32_BASE + expected_input_offset);
                    end
                    layer32_read_count = layer32_read_count + 1;
                end else if (active_stage == 2'd2) begin
                    if (route_source0_read_count < LAYER33_BYTES) begin
                        if ((byte_address != LAYER33_BASE + route_source0_read_count) ||
                            !layer33_initialized[route_source0_read_count]) begin
                            $fatal(1, "FAIL: route source0 顺序/初始化错误 offset=%0d",
                                   route_source0_read_count);
                        end
                        route_source0_read_count = route_source0_read_count + 1;
                    end else begin
                        byte_offset = route_source1_read_count;
                        if ((byte_address != LAYER23_BASE + byte_offset) ||
                            (byte_offset >= LAYER23_BYTES)) begin
                            $fatal(1, "FAIL: route source1 顺序错误 offset=%0d addr=%0d",
                                   byte_offset, byte_address);
                        end
                        route_source1_read_count = route_source1_read_count + 1;
                    end
                end else begin
                    $fatal(1, "FAIL: active stage 外发生 memory read");
                end
            end else begin
                if ((mem_rstrb != 4'd0) || (mem_wstrb == 4'd0) ||
                    ((mem_wstrb & (mem_wstrb - 4'd1)) != 4'd0)) begin
                    $fatal(1, "FAIL: write strobe 非法 r=%x w=%x", mem_rstrb, mem_wstrb);
                end
                lane_index = 0;
                while (!mem_wstrb[lane_index]) lane_index = lane_index + 1;
                byte_address = mem_addr + lane_index;
                observed_byte = (mem_wdata >> (lane_index * 8)) & 8'hFF;
                accepted_write_count = accepted_write_count + 1;
                if (active_stage == 2'd1) begin
                    if ((byte_address != LAYER33_BASE + layer33_write_count) ||
                        (layer33_write_count >= LAYER33_BYTES) ||
                        (observed_byte != expected_layer33[layer33_write_count])) begin
                        $fatal(1, "FAIL: layer33 写入不匹配 offset=%0d actual=%02x expected=%02x",
                               layer33_write_count, observed_byte,
                               expected_layer33[layer33_write_count]);
                    end
                    layer33_memory[layer33_write_count] = observed_byte[7:0];
                    layer33_initialized[layer33_write_count] = 1'b1;
                    if (trace33_fd != 0) $fdisplay(trace33_fd, "%02x", observed_byte);
                    layer33_write_count = layer33_write_count + 1;
                    if ((layer33_write_count % 8192) == 0) begin
                        $display("PROGRESS layer33 writes=%0d reads=%0d",
                                 layer33_write_count, layer32_read_count);
                    end
                end else if (active_stage == 2'd2) begin
                    if ((byte_address != LAYER34_BASE + layer34_write_count) ||
                        (layer34_write_count >= LAYER34_BYTES) ||
                        (observed_byte != expected_layer34[layer34_write_count])) begin
                        $fatal(1, "FAIL: layer34 写入不匹配 offset=%0d actual=%02x expected=%02x",
                               layer34_write_count, observed_byte,
                               expected_layer34[layer34_write_count]);
                    end
                    layer34_memory[layer34_write_count] = observed_byte[7:0];
                    layer34_initialized[layer34_write_count] = 1'b1;
                    if (trace34_fd != 0) $fdisplay(trace34_fd, "%02x", observed_byte);
                    layer34_write_count = layer34_write_count + 1;
                    if ((layer34_write_count % 8192) == 0) begin
                        $display("PROGRESS layer34 writes=%0d reads=%0d source0=%0d source1=%0d",
                                 layer34_write_count, accepted_read_count,
                                 route_source0_read_count, route_source1_read_count);
                    end
                end else begin
                    $fatal(1, "FAIL: active stage 外发生 memory write");
                end
            end

            accepted_by_class[active_class] = accepted_by_class[active_class] + 1;
            scheduled_stalls_by_class[active_class] =
                scheduled_stalls_by_class[active_class] + request_stall_expected;
            memory_stall_index[active_class] = (memory_stall_index[active_class] + 1) % 5;
            memory_pending = 1'b0;
            memory_stall_remaining = 0;
            request_stall_observed = 0;
        end
    endtask

    initial begin : load_fixtures
        integer index;
        for (index = 0; index < 4; index = index + 1) begin
            memory_stall_index[index] = 0;
            accepted_by_class[index] = 0;
            stall_cycles_by_class[index] = 0;
            scheduled_stalls_by_class[index] = 0;
        end
        $readmemh("layer32_seed.hex", layer32_input);
        $readmemh("layer23_seed.hex", layer23_input);
        $readmemh("expected_layer33.hex", expected_layer33);
        $readmemh("expected_layer34.hex", expected_layer34);
        for (index = 0; index < LAYER32_BYTES; index = index + 1) begin
            if ((^layer32_input[index]) === 1'bx) begin
                $fatal(1, "FAIL: layer32 seeded input fixture 有未初始化 byte offset=%0d", index);
            end
        end
        for (index = 0; index < LAYER23_BYTES; index = index + 1) begin
            if ((^layer23_input[index]) === 1'bx) begin
                $fatal(1, "FAIL: layer23 seeded input fixture 有未初始化 byte offset=%0d", index);
            end
        end
        for (index = 0; index < LAYER33_BYTES; index = index + 1) begin
            if ((^expected_layer33[index]) === 1'bx) begin
                $fatal(1, "FAIL: layer33 golden fixture 有未初始化 byte offset=%0d", index);
            end
        end
        for (index = 0; index < LAYER34_BYTES; index = index + 1) begin
            if ((^expected_layer34[index]) === 1'bx) begin
                $fatal(1, "FAIL: layer34 golden fixture 有未初始化 byte offset=%0d", index);
            end
        end
        for (index = 0; index < LAYER33_BYTES; index = index + 1) begin
            layer33_memory[index] = 8'd0;
            layer33_initialized[index] = 1'b0;
        end
        for (index = 0; index < LAYER34_BYTES; index = index + 1) begin
            layer34_memory[index] = 8'd0;
            layer34_initialized[index] = 1'b0;
        end
        model_initialized = 1'b1;
        $display("CHECK direct_index_memory initialized=1 layer32=%0d layer23=%0d",
                 LAYER32_BYTES, LAYER23_BYTES);
    end

    always @(posedge clk) begin : monitor_and_memory
        global_cycle_count = global_cycle_count + 1;
        if (active_case == CASE_SUCCESS && csr_valid && csr_ready && csr_write &&
            (csr_addr == REG_CMD) && csr_wdata[0] && !csr_wdata[1]) begin
            full_start_cycle = global_cycle_count;
        end
        if (dut.operator_result_valid) begin
            terminal_event_count = terminal_event_count + 1;
            if (active_case == CASE_SUCCESS) begin
                full_terminal_cycle = global_cycle_count;
            end
        end
        if (backend_start) backend_start_count = backend_start_count + 1;
        if (dut.layer33_start_valid && dut.layer33_start_ready) begin
            layer33_start_count = layer33_start_count + 1;
        end
        if (dut.layer34_start_valid && dut.layer34_start_ready) begin
            layer34_start_count = layer34_start_count + 1;
        end
        if (backend_abort && !backend_abort_previous) begin
            backend_abort_count = backend_abort_count + 1;
        end
        backend_abort_previous = backend_abort;

        if (model_reset || !pl_owns_buffers || !mem_valid) begin
            memory_pending = 1'b0;
            memory_stall_remaining = 0;
            request_stall_observed = 0;
        end else if (!memory_pending) begin
            active_class = request_class(mem_write, mem_addr);
            if ((active_class < READ_FEATURE) || (active_class > WRITE_FEATURE)) begin
                $fatal(1, "FAIL: memory request 不属于 frozen feature class write=%0d addr=%08x",
                       mem_write, mem_addr);
            end
            accepted_mem_addr = mem_addr;
            accepted_mem_wdata = mem_wdata;
            accepted_mem_rstrb = mem_rstrb;
            accepted_mem_wstrb = mem_wstrb;
            accepted_mem_write = mem_write;
            accepted_fault_valid = fault_inject_valid;
            accepted_fault_code = fault_inject_code;
            request_stall_expected = scheduled_stall(memory_stall_index[active_class]);
            request_stall_observed = 0;
            if (request_stall_expected == 0) begin
                if (!mem_ready) $fatal(1, "FAIL: T10 delay=0 请求首个可接受上升沿 ready 未拉高");
                accept_current_request();
            end else begin
                if (mem_ready) $fatal(1, "FAIL: T10 delay>0 请求首个上升沿错误 ready 拉高");
                memory_pending = 1'b1;
                memory_stall_remaining = request_stall_expected - 1;
                request_stall_observed = request_stall_observed + 1;
                stall_cycle_count = stall_cycle_count + 1;
                stall_cycles_by_class[active_class] = stall_cycles_by_class[active_class] + 1;
            end
        end else begin
            if ((mem_addr != accepted_mem_addr) || (mem_wdata != accepted_mem_wdata) ||
                (mem_rstrb != accepted_mem_rstrb) || (mem_wstrb != accepted_mem_wstrb) ||
                (mem_write != accepted_mem_write) ||
                (fault_inject_valid != accepted_fault_valid) ||
                (fault_inject_code != accepted_fault_code)) begin
                $fatal(1, "FAIL: backpressure 期间 memory request 字段变化");
            end
            if (mem_ready) begin
                if (memory_stall_remaining != 0) begin
                    $fatal(1, "FAIL: responder ready 提前于冻结 stall schedule");
                end
                accept_current_request();
            end else begin
                if (memory_stall_remaining <= 0) begin
                    $fatal(1, "FAIL: responder 在冻结 stall schedule 后仍 ready-low");
                end
                request_stall_observed = request_stall_observed + 1;
                stall_cycle_count = stall_cycle_count + 1;
                stall_cycles_by_class[active_class] = stall_cycles_by_class[active_class] + 1;
                memory_stall_remaining = memory_stall_remaining - 1;
            end
        end

        if ((active_stage == 2'd2) && (terminal_event_count != 0) &&
            (active_case == CASE_SUCCESS) && (layer34_write_count < LAYER34_BYTES)) begin
            $fatal(1, "FAIL: layer34 尚未全部完成时出现终态事件");
        end
        terminal_event_count_previous = terminal_event_count;
    end

    initial begin : run_cases
        active_case = 0;
        terminal_event_count = 0;
        backend_start_count = 0;
        backend_abort_count = 0;
        layer33_start_count = 0;
        layer34_start_count = 0;
        accepted_read_count = 0;
        accepted_write_count = 0;
        layer32_read_count = 0;
        route_source0_read_count = 0;
        route_source1_read_count = 0;
        layer33_write_count = 0;
        layer34_write_count = 0;
        stall_cycle_count = 0;
        error_response_count = 0;
        trace33_fd = 0;
        trace34_fd = 0;

        hard_reset = 1'b1;
        repeat (3) @(posedge clk);
        @(negedge clk);
        hard_reset = 1'b0;
        wait (model_initialized);
        repeat (2) @(posedge clk);
        @(negedge clk);

        active_case = CASE_TIMEOUT;
        write_csr(REG_TIMEOUT, 32'd24);
        write_csr(REG_CMD, 32'd1);
        wait_for_terminal();
        if (!error || done || busy || pl_owns_buffers || head_output_valid ||
            (backend_start_count != 1) || (layer33_start_count != 1) ||
            (layer34_start_count != 0)) begin
            $fatal(1, "FAIL: G0 global timeout / layer33-only abort 状态错误");
        end
        csr_valid = 1'b1;
        csr_write = 1'b0;
        csr_addr = REG_ERROR_CODE;
        #1;
        if (csr_rdata[2:0] != 3'd5) $fatal(1, "FAIL: timeout error code 不是 5");
        csr_valid = 1'b0;
        csr_addr = 8'd0;
        if (!backend_abort || (terminal_event_count != 0)) begin
            $fatal(1, "FAIL: global timeout 未 abort 或产生了算子终态事件");
        end
        reads_before_cancel = accepted_read_count;
        writes_before_cancel = accepted_write_count;
        terminals_before_cancel = terminal_event_count;
        repeat (12) @(posedge clk);
        if ((accepted_read_count != reads_before_cancel) ||
            (accepted_write_count != writes_before_cancel) ||
            (terminal_event_count != terminals_before_cancel) || busy ||
            pl_owns_buffers || (active_stage != 2'd0)) begin
            $fatal(1, "FAIL: timeout 后有迟到 memory side effect 或子层工作");
        end
        $display("CHECK global_timeout abort=1 route_starts=0 late_side_effects=0");
        write_csr(REG_ACK, 32'd2);

        active_case = CASE_MEMORY_ERROR;
        layer32_read_count = 0;
        layer33_write_count = 0;
        route_source0_read_count = 0;
        route_source1_read_count = 0;
        fault_inject_valid = 1'b1;
        fault_inject_code = 3'd2;
        write_csr(REG_TIMEOUT, 32'd1100000);
        write_csr(REG_CMD, 32'd1);
        wait_for_terminal();
        if (!error || done || busy || pl_owns_buffers || head_output_valid ||
            (layer34_start_count != 0) || (error_response_count == 0)) begin
            $fatal(1, "FAIL: memory error 未阻止 layer34 或未映射为 shell error");
        end
        csr_valid = 1'b1;
        csr_write = 1'b0;
        csr_addr = REG_ERROR_CODE;
        #1;
        if (csr_rdata[2:0] != 3'd2) $fatal(1, "FAIL: memory BAD_RANGE code 未转发");
        csr_valid = 1'b0;
        csr_addr = 8'd0;
        if (layer33_start_count != 2 || layer34_start_count != 0) begin
            $fatal(1, "FAIL: memory error 后启动了 downstream layer");
        end
        fault_inject_valid = 1'b0;
        fault_inject_code = 3'd0;
        write_csr(REG_ACK, 32'd2);
        $display("CHECK memory_error route_starts=0 mapped_code=2");

        active_case = CASE_HARD_RESET;
        layer32_read_count = 0;
        layer33_write_count = 0;
        route_source0_read_count = 0;
        route_source1_read_count = 0;
        write_csr(REG_TIMEOUT, 32'd1100000);
        write_csr(REG_CMD, 32'd1);
        wait_for_pending_write();
        writes_before_cancel = accepted_write_count;
        reads_before_cancel = accepted_read_count;
        hard_reset = 1'b1;
        @(posedge clk);
        @(negedge clk);
        hard_reset = 1'b0;
        repeat (12) @(posedge clk);
        if ((accepted_write_count != writes_before_cancel) ||
            (accepted_read_count != reads_before_cancel) || busy || done || error ||
            pl_owns_buffers || (active_stage != 2'd0) || (terminal_event_count != 0)) begin
            $fatal(1, "FAIL: hard reset pending request 后出现迟到 side effect");
        end
        $display("CHECK hard_reset pending_write=1 late_side_effects=0");

        active_case = CASE_SOFT_RESET;
        layer32_read_count = 0;
        layer33_write_count = 0;
        route_source0_read_count = 0;
        route_source1_read_count = 0;
        write_csr(REG_TIMEOUT, 32'd1100000);
        write_csr(REG_CMD, 32'd1);
        wait_for_pending_write();
        writes_before_cancel = accepted_write_count;
        reads_before_cancel = accepted_read_count;
        write_csr(REG_CMD, 32'd2);
        repeat (12) @(posedge clk);
        if ((accepted_write_count != writes_before_cancel) ||
            (accepted_read_count != reads_before_cancel) || busy || done || error ||
            pl_owns_buffers || (active_stage != 2'd0) || (terminal_event_count != 0)) begin
            $fatal(1, "FAIL: soft reset pending request 后出现迟到 side effect");
        end
        $display("CHECK soft_reset pending_write=1 late_side_effects=0");

        if ($test$plusargs("QUICK")) begin
            active_case = CASE_SUCCESS;
            accepted_read_count = 0;
            accepted_write_count = 0;
            layer32_read_count = 0;
            route_source0_read_count = 0;
            route_source1_read_count = 0;
            layer33_write_count = 0;
            layer34_write_count = 0;
            terminal_event_count = 0;
            backend_start_count = 0;
            backend_abort_count = 0;
            layer33_start_count = 0;
            layer34_start_count = 0;
            stall_cycle_count = 0;
            write_csr(REG_TIMEOUT, FULL_TASK_TIMEOUT_CYCLES);
            write_csr(REG_CMD, 32'd1);
            wait_for_route_stage();
            $display("CHECK layer33_boundary terminal_events=%0d layer33_reads=%0d layer33_writes=%0d layer34_start_handshakes=%0d layer34_start_ready=%0d active_stage=%0d",
                     terminal_event_count, layer32_read_count, layer33_write_count,
                     layer34_start_count, dut.layer34_start_ready, active_stage);
            if (terminal_event_count != 0 || (layer33_write_count != LAYER33_BYTES) ||
                (layer32_read_count != LAYER33_BYTES) || (layer34_start_count != 1)) begin
                $fatal(1, "FAIL: QUICK layer33 boundary/start handshake assertion failed");
            end
            reads_before_cancel = accepted_read_count;
            writes_before_cancel = accepted_write_count;
            write_csr(REG_CMD, 32'd2);
            repeat (12) @(posedge clk);
            if ((accepted_read_count != reads_before_cancel) ||
                (accepted_write_count != writes_before_cancel) || busy || done || error ||
                pl_owns_buffers || (active_stage != 2'd0) || (terminal_event_count != 0)) begin
                $fatal(1, "FAIL: QUICK route-boundary soft reset 后出现迟到副作用");
            end
            $display("CHECK quick_boundary_reset terminal_events=0 late_side_effects=0");
            $display("RESULT mode=QUICK timeout_abort=1 memory_error=1 hard_reset=1 soft_reset=1 layer33_boundary=1 route_start=1 terminal_events=0");
            $display("PASS S2A-T28 runtime shell layer33-to-layer34 control and boundary smoke");
            $finish;
        end

        active_case = CASE_SUCCESS;
        accepted_read_count = 0;
        accepted_write_count = 0;
        layer32_read_count = 0;
        route_source0_read_count = 0;
        route_source1_read_count = 0;
        layer33_write_count = 0;
        layer34_write_count = 0;
        terminal_event_count = 0;
        backend_start_count = 0;
        backend_abort_count = 0;
        layer33_start_count = 0;
        layer34_start_count = 0;
        stall_cycle_count = 0;
        for (class_index = 0; class_index < 4; class_index = class_index + 1) begin
            accepted_by_class[class_index] = 0;
            stall_cycles_by_class[class_index] = 0;
            scheduled_stalls_by_class[class_index] = 0;
        end
        trace33_fd = $fopen("observed_layer33_hex.txt", "w");
        trace34_fd = $fopen("observed_layer34_hex.txt", "w");
        if ((trace33_fd == 0) || (trace34_fd == 0)) begin
            $fatal(1, "FAIL: 无法创建 layer output traces");
        end
        write_csr(REG_TIMEOUT, FULL_TASK_TIMEOUT_CYCLES);
        write_csr(REG_CMD, 32'd1);
        wait_for_route_stage();
        $display("CHECK layer33_boundary terminal_events=%0d layer33_reads=%0d layer33_writes=%0d layer34_start_handshakes=%0d layer34_start_ready=%0d active_stage=%0d",
                 terminal_event_count, layer32_read_count, layer33_write_count,
                 layer34_start_count, dut.layer34_start_ready, active_stage);
        if (terminal_event_count != 0 || (layer33_write_count != LAYER33_BYTES) ||
            (layer32_read_count != LAYER33_BYTES) || (layer34_start_count != 1)) begin
            $fatal(1, "FAIL: layer33 到 layer34 交界点状态不正确 terminal=%0d l33_writes=%0d l32_reads=%0d l34_starts=%0d stage=%0d",
                   terminal_event_count, layer33_write_count, layer32_read_count,
                   layer34_start_count, active_stage);
        end
        write_csr(REG_CMD, 32'd1);
        if (!busy || (backend_start_count != 1)) begin
            $fatal(1, "FAIL: busy 状态重复 start 未被忽略");
        end
        wait_for_terminal();
        $fclose(trace33_fd);
        $fclose(trace34_fd);
        trace33_fd = 0;
        trace34_fd = 0;
        if (error || !done || busy || pl_owns_buffers || !head_output_valid ||
            (terminal_event_count != 1) || (backend_start_count != 1) ||
            (layer33_start_count != 1) || (layer34_start_count != 1) ||
            (layer32_read_count != LAYER33_BYTES) ||
            (route_source0_read_count != LAYER33_BYTES) ||
            (route_source1_read_count != LAYER23_BYTES) ||
            (layer33_write_count != LAYER33_BYTES) ||
            (layer34_write_count != LAYER34_BYTES) ||
            (accepted_read_count != LAYER33_BYTES + LAYER33_BYTES + LAYER23_BYTES) ||
            (accepted_write_count != LAYER33_BYTES + LAYER34_BYTES) ||
            (stall_cycle_count <= 0) || (backend_abort_count != 0) ||
            (accepted_by_class[READ_INPUT] != 0) ||
            (accepted_by_class[READ_WEIGHTS] != 0) ||
            (accepted_by_class[READ_FEATURE] != accepted_read_count) ||
            (accepted_by_class[WRITE_FEATURE] != accepted_write_count) ||
            (stall_cycles_by_class[READ_INPUT] != 0) ||
            (stall_cycles_by_class[READ_WEIGHTS] != 0) ||
            (stall_cycles_by_class[READ_FEATURE] != scheduled_stalls_by_class[READ_FEATURE]) ||
            (stall_cycles_by_class[WRITE_FEATURE] != scheduled_stalls_by_class[WRITE_FEATURE])) begin
            $fatal(1, "FAIL: serial full counters busy=%0d done=%0d error=%0d terminal=%0d starts=%0d/%0d/%0d reads=%0d/%0d/%0d writes=%0d/%0d stalls=%0d aborts=%0d",
                   busy, done, error, terminal_event_count, backend_start_count,
                   layer33_start_count, layer34_start_count, accepted_read_count,
                   layer32_read_count, route_source0_read_count + route_source1_read_count,
                   accepted_write_count, layer33_write_count + layer34_write_count,
                   stall_cycle_count, backend_abort_count);
        end
        if (terminal_event_count_previous != terminal_event_count) begin
            $fatal(1, "FAIL: terminal monitor 未收敛");
        end
        full_elapsed_cycles = full_terminal_cycle - full_start_cycle;
        if ((full_start_cycle == 0) || (full_terminal_cycle <= full_start_cycle) ||
            (full_elapsed_cycles >= FULL_TASK_TIMEOUT_CYCLES)) begin
            $fatal(1, "FAIL: 整网pilot未在唯一G0 deadline内完成 start=%0d terminal=%0d",
                   full_start_cycle, full_terminal_cycle);
        end
        $display("RESULT mode=FULL layer33_bytes=%0d layer34_bytes=%0d reads=%0d writes=%0d terminal_events=%0d stalls=%0d source0_reads=%0d source1_reads=%0d timeout_abort=1 memory_error=1 hard_reset=1 soft_reset=1 recovery=1 global_timeout_cycles=%0d elapsed_task_cycles=%0d read_input_transactions=%0d read_weights_transactions=%0d read_feature_transactions=%0d read_feature_stall_cycles=%0d write_feature_transactions=%0d write_feature_stall_cycles=%0d",
                 layer33_write_count, layer34_write_count, accepted_read_count,
                 accepted_write_count, terminal_event_count, stall_cycle_count,
                 route_source0_read_count, route_source1_read_count,
                 FULL_TASK_TIMEOUT_CYCLES, full_elapsed_cycles,
                 accepted_by_class[READ_INPUT], accepted_by_class[READ_WEIGHTS],
                 accepted_by_class[READ_FEATURE], stall_cycles_by_class[READ_FEATURE],
                 accepted_by_class[WRITE_FEATURE], stall_cycles_by_class[WRITE_FEATURE]);
        $display("PASS S2A-T28 runtime shell serial layer33-to-layer34 pilot");
        $finish;
    end
endmodule
