// S2A-T21：tiny416 layer25 maxpool 调度器、T10/T12 协议与整层比对。
`timescale 1ns/1ps
module tb_s2a_maxpool_layer_scheduler;
    localparam logic [31:0] INPUT_BASE = 32'd26900992;
    localparam integer INPUT_BYTES = 346112;
    localparam integer INPUT_CHANNELS = 512;
    localparam integer INPUT_DIMENSION = 26;
    localparam integer OUTPUT_DIMENSION = 13;
    localparam logic [31:0] OUTPUT_BASE = 32'd27247104;
    localparam integer OUTPUT_BYTES = 86528;
    localparam integer PATCH_CAPACITY = 131072;
    localparam logic [31:0] MAX_TIMEOUT = 32'hFFFF_FFFF;

    logic clk = 1'b0;
    logic full_hard_reset = 1'b1;
    logic full_abort = 1'b0;
    logic full_start_valid = 1'b0;
    logic full_start_ready;
    logic [31:0] full_timeout_cycles = MAX_TIMEOUT;
    logic full_completion_ready = 1'b0;
    logic full_busy;
    logic full_done;
    logic full_error;
    logic [2:0] full_error_code;
    logic [16:0] full_completed_elements;
    logic full_cancel;
    logic full_req_valid;
    logic full_req_ready;
    logic full_req_write;
    logic [31:0] full_req_addr;
    logic [31:0] full_req_wdata;
    logic [3:0] full_req_rstrb;
    logic [3:0] full_req_wstrb;
    logic full_rsp_valid;
    logic [31:0] full_rsp_rdata;
    logic [2:0] full_rsp_error;

    logic boundary_hard_reset = 1'b1;
    logic boundary_abort = 1'b0;
    logic boundary_start_valid = 1'b0;
    logic boundary_start_ready;
    logic [31:0] boundary_timeout_cycles = MAX_TIMEOUT;
    logic boundary_completion_ready = 1'b0;
    logic boundary_busy;
    logic boundary_done;
    logic boundary_error;
    logic [2:0] boundary_error_code;
    logic [16:0] boundary_completed_elements;
    logic boundary_cancel;
    logic boundary_req_valid;
    logic boundary_req_ready;
    logic boundary_req_write;
    logic [31:0] boundary_req_addr;
    logic [31:0] boundary_req_wdata;
    logic [3:0] boundary_req_rstrb;
    logic [3:0] boundary_req_wstrb;
    logic boundary_rsp_valid;
    logic [31:0] boundary_rsp_rdata;
    logic [2:0] boundary_rsp_error;

    logic boundary_mode = 1'b1;
    logic master_owner = 1'b1;
    logic master_reset;
    logic master_cancel;
    logic master_req_valid;
    logic master_req_ready;
    logic master_req_write;
    logic [31:0] master_req_addr;
    logic [31:0] master_req_wdata;
    logic [3:0] master_req_rstrb;
    logic [3:0] master_req_wstrb;
    logic master_rsp_valid;
    logic [31:0] master_rsp_rdata;
    logic [2:0] master_rsp_error;
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

    logic [7:0] expected_output_bytes [0:OUTPUT_BYTES-1];
    integer input_sentinel_count = 0;
    integer total_accepted_reads = 0;
    integer total_accepted_writes = 0;
    integer total_error_responses = 0;
    integer total_stall_cycles = 0;
    integer boundary_abort_count = 0;
    integer boundary_reset_count = 0;
    integer boundary_timeout_count = 0;
    integer boundary_zero_timeout_count = 0;
    integer boundary_timeout_n1_count = 0;
    integer boundary_timeout_n2_count = 0;
    integer boundary_error_priority_count = 0;
    integer boundary_raw_error_priority_count = 0;
    integer boundary_done_priority_count = 0;
    integer boundary_completion_hold_count = 0;
    integer full_busy_start_checks = 0;
    integer full_done_hold_count = 0;
    integer full_feature_reads = 0;
    integer full_output_writes = 0;
    integer full_stall_cycles = 0;
    integer full_scoreboard_enable = 0;
    integer trace_file = 0;
    integer selected_lane;
    integer expected_output_index;
    integer expected_tap_index;
    integer expected_channel;
    integer expected_pixel;
    integer expected_y;
    integer expected_x;
    integer expected_tap_y;
    integer expected_tap_x;
    integer sampled_byte;
    integer timeout_count;
    integer hold_count;
    integer input_index;
    integer global_reads_before;
    integer global_writes_before;
    integer boundary_error_cycles = 0;
    integer boundary_success_cycles = 0;
    integer boundary_cycles_current;
    integer calibration_index;
    integer smoke_mode = 0;
    logic [31:0] expected_byte_address;
    logic [3:0] expected_lane;

    always #5 clk = ~clk;

    s2a_maxpool_layer_scheduler u_full_scheduler (
        .clk(clk),
        .hard_reset(full_hard_reset),
        .abort(full_abort),
        .start_valid(full_start_valid),
        .start_ready(full_start_ready),
        .timeout_cycles(full_timeout_cycles),
        .completion_ready(full_completion_ready),
        .busy(full_busy),
        .done(full_done),
        .error(full_error),
        .error_code(full_error_code),
        .completed_elements(full_completed_elements),
        .backend_cancel(full_cancel),
        .backend_req_valid(full_req_valid),
        .backend_req_ready(full_req_ready),
        .backend_req_write(full_req_write),
        .backend_req_addr(full_req_addr),
        .backend_req_wdata(full_req_wdata),
        .backend_req_rstrb(full_req_rstrb),
        .backend_req_wstrb(full_req_wstrb),
        .backend_rsp_valid(full_rsp_valid),
        .backend_rsp_rdata(full_rsp_rdata),
        .backend_rsp_error(full_rsp_error)
    );

    // 单输出边界实例用于精确检查第 N 个上升沿的完成/错误优先级。
    s2a_maxpool_layer_scheduler #(
        .OUTPUT_COUNT_LIMIT(17'd1)
    ) u_boundary_scheduler (
        .clk(clk),
        .hard_reset(boundary_hard_reset),
        .abort(boundary_abort),
        .start_valid(boundary_start_valid),
        .start_ready(boundary_start_ready),
        .timeout_cycles(boundary_timeout_cycles),
        .completion_ready(boundary_completion_ready),
        .busy(boundary_busy),
        .done(boundary_done),
        .error(boundary_error),
        .error_code(boundary_error_code),
        .completed_elements(boundary_completed_elements),
        .backend_cancel(boundary_cancel),
        .backend_req_valid(boundary_req_valid),
        .backend_req_ready(boundary_req_ready),
        .backend_req_write(boundary_req_write),
        .backend_req_addr(boundary_req_addr),
        .backend_req_wdata(boundary_req_wdata),
        .backend_req_rstrb(boundary_req_rstrb),
        .backend_req_wstrb(boundary_req_wstrb),
        .backend_rsp_valid(boundary_rsp_valid),
        .backend_rsp_rdata(boundary_rsp_rdata),
        .backend_rsp_error(boundary_rsp_error)
    );

    always_comb begin
        master_reset = full_hard_reset || boundary_hard_reset;
        master_cancel = boundary_mode ? boundary_cancel : full_cancel;
        master_req_valid = boundary_mode ? boundary_req_valid : full_req_valid;
        master_req_write = boundary_mode ? boundary_req_write : full_req_write;
        master_req_addr = boundary_mode ? boundary_req_addr : full_req_addr;
        master_req_wdata = boundary_mode ? boundary_req_wdata : full_req_wdata;
        master_req_rstrb = boundary_mode ? boundary_req_rstrb : full_req_rstrb;
        master_req_wstrb = boundary_mode ? boundary_req_wstrb : full_req_wstrb;
        full_req_ready = !boundary_mode && master_req_ready;
        boundary_req_ready = boundary_mode && master_req_ready;
        full_rsp_valid = !boundary_mode && master_rsp_valid;
        full_rsp_rdata = boundary_mode ? 32'd0 : master_rsp_rdata;
        full_rsp_error = boundary_mode ? 3'd0 : master_rsp_error;
        boundary_rsp_valid = boundary_mode && master_rsp_valid;
        boundary_rsp_rdata = boundary_mode ? master_rsp_rdata : 32'd0;
        boundary_rsp_error = boundary_mode ? master_rsp_error : 3'd0;
    end

    s2a_memory_master u_memory_master (
        .clk(clk),
        .hard_reset(master_reset),
        .cancel(master_cancel),
        .buffer_owner_pl(master_owner),
        .backend_req_valid(master_req_valid),
        .backend_req_ready(master_req_ready),
        .backend_req_write(master_req_write),
        .backend_req_addr(master_req_addr),
        .backend_req_wdata(master_req_wdata),
        .backend_req_rstrb(master_req_rstrb),
        .backend_req_wstrb(master_req_wstrb),
        .backend_rsp_valid(master_rsp_valid),
        .backend_rsp_rdata(master_rsp_rdata),
        .backend_rsp_error(master_rsp_error),
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
        .PATCH_CAPACITY(PATCH_CAPACITY)
    ) u_memory (
        .clk(clk),
        .reset(master_reset),
        .buffer_owner_pl(master_owner),
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

    function automatic integer selected_byte_lane(input logic [3:0] strobe);
        begin
            case (strobe)
                4'b0001: selected_byte_lane = 0;
                4'b0010: selected_byte_lane = 1;
                4'b0100: selected_byte_lane = 2;
                4'b1000: selected_byte_lane = 3;
                default: selected_byte_lane = -1;
            endcase
        end
    endfunction

    task automatic initialize_fixture;
        logic [7:0] fixture_byte;
        begin
            input_sentinel_count = 0;
            for (input_index = 0; input_index < INPUT_BYTES; input_index = input_index + 1) begin
                fixture_byte = u_memory.initial_byte(INPUT_BASE + input_index);
                if (fixture_byte == 8'h80) begin
                    u_memory.store_byte(INPUT_BASE + input_index, 8'h00);
                    input_sentinel_count = input_sentinel_count + 1;
                end
                if ((input_index != 0) && ((input_index % 32768) == 0)) begin
                    $display("PROGRESS input_fixture=%0d/%0d sentinel_patches=%0d",
                             input_index, INPUT_BYTES, input_sentinel_count);
                end
            end
            if (input_sentinel_count != 1352) begin
                $fatal(1, "T10 layer25 raw -128 数量应为1352，实际=%0d",
                       input_sentinel_count);
            end
            if (u_memory.patch_count != 1352) begin
                $fatal(1, "输入合法域修补 patch 数量错误：%0d", u_memory.patch_count);
            end
            $display("PROGRESS fixture_ready input=%0d sentinels=%0d patches=%0d",
                     INPUT_BYTES, input_sentinel_count, u_memory.patch_count);
        end
    endtask

    task automatic start_boundary;
        begin
            @(negedge clk);
            if (!boundary_start_ready || boundary_busy || boundary_done || boundary_error) begin
                $fatal(1, "boundary scheduler 未处于可启动状态");
            end
            boundary_start_valid = 1'b1;
            @(posedge clk);
            @(negedge clk);
            boundary_start_valid = 1'b0;
        end
    endtask

    task automatic acknowledge_boundary;
        begin
            @(negedge clk);
            boundary_completion_ready = 1'b1;
            @(posedge clk);
            @(negedge clk);
            boundary_completion_ready = 1'b0;
        end
    endtask

    task automatic wait_boundary_error(output integer elapsed);
        begin
            elapsed = 0;
            while (!boundary_error && (elapsed < 100000)) begin
                @(posedge clk);
                #1;
                elapsed = elapsed + 1;
            end
            if (!boundary_error) $fatal(1, "boundary scheduler 等待 error 超时");
        end
    endtask

    task automatic wait_boundary_memory_error(
        output integer elapsed,
        output integer response_code
    );
        integer response_seen;
        begin
            elapsed = 0;
            response_code = 0;
            response_seen = 0;
            while ((response_seen == 0) && (elapsed < 100000)) begin
                @(posedge clk);
                if (boundary_rsp_valid && (boundary_rsp_error != 3'd0)) begin
                    response_seen = 1;
                    response_code = boundary_rsp_error;
                end
                #1;
                elapsed = elapsed + 1;
            end
            if (response_seen == 0)
                $fatal(1, "没有观察到原始 T10/T12 memory error response 握手");
        end
    endtask

    task automatic wait_boundary_done(output integer elapsed);
        begin
            elapsed = 0;
            while (!boundary_done && !boundary_error && (elapsed < 100000)) begin
                @(posedge clk);
                #1;
                elapsed = elapsed + 1;
            end
            if (!boundary_done || boundary_error)
                $fatal(1, "boundary scheduler 等待 done 超时或返回错误 code=%0d",
                       boundary_error_code);
        end
    endtask

    task automatic wait_boundary_read_request;
        begin
            timeout_count = 0;
            while (!(boundary_req_valid && !boundary_req_write) &&
                   (timeout_count < 1000)) begin
                @(negedge clk);
                timeout_count = timeout_count + 1;
            end
            if (!(boundary_req_valid && !boundary_req_write))
                $fatal(1, "没有观察到等待中的 layer25 feature 请求");
        end
    endtask

    task automatic wait_boundary_write_request;
        begin
            timeout_count = 0;
            while (!(boundary_req_valid && boundary_req_write) &&
                   (timeout_count < 20000)) begin
                @(negedge clk);
                timeout_count = timeout_count + 1;
            end
            if (!(boundary_req_valid && boundary_req_write))
                $fatal(1, "没有观察到等待中的 layer25 output 请求");
        end
    endtask

    task automatic wait_pending_memory_read;
        begin
            timeout_count = 0;
            while (!(mem_valid && !mem_ready && !mem_write && u_memory.pending) &&
                   (timeout_count < 1000)) begin
                @(negedge clk);
                timeout_count = timeout_count + 1;
            end
            if (!(mem_valid && !mem_ready && !mem_write) || !u_memory.pending)
                $fatal(1, "没有观察到 T10 pending feature read index=%0d address=%08x",
                       u_memory.stall_index[2], mem_addr);
        end
    endtask

    task automatic wait_pending_memory_write;
        begin
            timeout_count = 0;
            while (!(mem_valid && !mem_ready && mem_write && u_memory.pending) &&
                   (timeout_count < 20000)) begin
                @(negedge clk);
                timeout_count = timeout_count + 1;
            end
            if (!(mem_valid && !mem_ready && mem_write) || !u_memory.pending)
                $fatal(1, "没有观察到 T10 pending output write");
        end
    endtask

    task automatic run_boundary_warmup;
        integer warmup_cycles;
        begin
            boundary_timeout_cycles = MAX_TIMEOUT;
            start_boundary();
            wait_boundary_done(warmup_cycles);
            if (boundary_completed_elements != 17'd1)
                $fatal(1, "单元素 boundary warmup 完成计数错误");
            acknowledge_boundary();
        end
    endtask

    task automatic run_pending_abort_case;
        begin
            global_reads_before = total_accepted_reads;
            global_writes_before = total_accepted_writes;
            boundary_timeout_cycles = MAX_TIMEOUT;
            start_boundary();
            wait_pending_memory_read();
            boundary_abort = 1'b1;
            @(posedge clk);
            @(negedge clk);
            boundary_abort = 1'b0;
            repeat (4) @(posedge clk);
            if (boundary_busy || boundary_done || boundary_error ||
                !boundary_start_ready || total_accepted_reads != global_reads_before ||
                total_accepted_writes != global_writes_before || u_memory.pending ||
                u_memory_master.pending) begin
                $fatal(1, "pending read abort 后状态或 memory 副作用错误");
            end
            boundary_abort_count = boundary_abort_count + 1;
        end
    endtask

    task automatic run_pending_reset_case;
        begin
            global_writes_before = total_accepted_writes;
            boundary_timeout_cycles = MAX_TIMEOUT;
            start_boundary();
            wait_pending_memory_write();
            boundary_hard_reset = 1'b1;
            @(posedge clk);
            @(negedge clk);
            boundary_hard_reset = 1'b0;
            repeat (4) @(posedge clk);
            if (boundary_busy || boundary_done || boundary_error ||
                !boundary_start_ready || total_accepted_writes != global_writes_before ||
                u_memory.pending || u_memory_master.pending) begin
                $fatal(1, "pending output write 硬复位后有副作用或未恢复");
            end
            boundary_reset_count = boundary_reset_count + 1;
        end
    endtask

    task automatic run_pending_timeout_case;
        integer elapsed;
        logic pending_seen;
        begin
            global_reads_before = total_accepted_reads;
            global_writes_before = total_accepted_writes;
            if (u_memory.stall_index[2] != 3)
                $fatal(1, "timeout 用例需从 T10 READ_FEATURE delay=7 槽位开始，index=%0d",
                       u_memory.stall_index[2]);
            boundary_timeout_cycles = 32'd8;
            start_boundary();
            elapsed = 0;
            pending_seen = 1'b0;
            while (!boundary_error && (elapsed < 1000)) begin
                @(posedge clk);
                if (mem_valid && !mem_ready && !mem_write && u_memory.pending)
                    pending_seen = 1'b1;
                #1;
                elapsed = elapsed + 1;
            end
            boundary_cycles_current = elapsed;
            if ((boundary_error_code != 3'd5) || boundary_done || boundary_busy ||
                (boundary_cycles_current != 8) || !pending_seen ||
                (total_accepted_reads != global_reads_before) ||
                (total_accepted_writes != global_writes_before)) begin
                $fatal(1, "G0 第8个后续沿 pending-read timeout/cancel 错误 code=%0d cycles=%0d pending_seen=%0d reads=%0d/%0d",
                       boundary_error_code, boundary_cycles_current, pending_seen,
                       total_accepted_reads, global_reads_before);
            end
            repeat (4) @(posedge clk);
            if (total_accepted_reads != global_reads_before ||
                total_accepted_writes != global_writes_before || u_memory.pending ||
                u_memory_master.pending) begin
                $fatal(1, "timeout cancel 后 memory master 产生延迟副作用");
            end
            for (hold_count = 0; hold_count < 3; hold_count = hold_count + 1) begin
                @(posedge clk);
                #1;
                if (!boundary_error || boundary_error_code != 3'd5 || boundary_start_ready)
                    $fatal(1, "timeout error 未保持到 completion ACK");
            end
            boundary_completion_hold_count = boundary_completion_hold_count + 3;
            acknowledge_boundary();
            if (!boundary_start_ready || boundary_error || boundary_error_code != 3'd0)
                $fatal(1, "timeout ACK 后 scheduler 未恢复 idle");
            boundary_timeout_count = boundary_timeout_count + 1;
        end
    endtask

    task automatic run_zero_timeout_case;
        begin
            global_reads_before = total_accepted_reads;
            global_writes_before = total_accepted_writes;
            boundary_timeout_cycles = 32'd0;
            start_boundary();
            if (!boundary_error || boundary_error_code != 3'd1 || boundary_busy ||
                boundary_done || total_accepted_reads != global_reads_before ||
                total_accepted_writes != global_writes_before)
                $fatal(1, "zero timeout 必须返回 BAD_ARGUMENT 且不发 memory 请求");
            acknowledge_boundary();
            if (!boundary_start_ready || boundary_error)
                $fatal(1, "zero timeout ACK 后无法恢复");
            boundary_zero_timeout_count = boundary_zero_timeout_count + 1;
        end
    endtask

    task automatic run_timeout_one_cycle_case;
        begin
            boundary_timeout_cycles = 32'd1;
            start_boundary();
            if (!boundary_busy || boundary_error || boundary_cancel || boundary_req_valid)
                $fatal(1, "N=1 在首个后续沿前必须保留完整执行周期");
            @(posedge clk);
            #1;
            if (!boundary_error || boundary_error_code != 3'd5 || boundary_busy ||
                !boundary_cancel || boundary_req_valid || boundary_rsp_valid ||
                u_memory.pending || (u_boundary_scheduler.u_element_engine.state != 4'd1))
                $fatal(1, "N=1 第一个后续沿 timeout/cancel 错误 child_state=%0d",
                       u_boundary_scheduler.u_element_engine.state);
            boundary_timeout_n1_count = boundary_timeout_n1_count + 1;
            acknowledge_boundary();
            if (!boundary_start_ready || boundary_error || boundary_error_code != 3'd0)
                $fatal(1, "N=1 timeout ACK 后未恢复 idle");
        end
    endtask

    task automatic run_timeout_two_cycle_case;
        begin
            boundary_timeout_cycles = 32'd2;
            start_boundary();
            if (!boundary_busy || boundary_error || boundary_cancel || boundary_req_valid)
                $fatal(1, "N=2 timeout 在 start 接受后不应提前取消");
            @(posedge clk);
            #1;
            if (!boundary_busy || boundary_error || boundary_cancel ||
                (u_boundary_scheduler.elapsed_cycles != 32'd1) ||
                (u_boundary_scheduler.u_element_engine.state != 4'd1))
                $fatal(1, "N=2 第一个后续沿未保留工作或计数错误");
            @(posedge clk);
            #1;
            if (!boundary_error || boundary_error_code != 3'd5 || boundary_busy ||
                !boundary_cancel || boundary_rsp_valid || u_memory.pending ||
                (u_boundary_scheduler.u_element_engine.state != 4'd2))
                $fatal(1, "N=2 第二个后续沿 timeout/cancel 错误 child_state=%0d",
                       u_boundary_scheduler.u_element_engine.state);
            @(posedge clk);
            #1;
            if (u_memory_master.pending || u_memory.pending || mem_valid)
                $fatal(1, "N=2 deadline 边沿接受的请求未在随后周期取消");
            boundary_timeout_n2_count = boundary_timeout_n2_count + 1;
            acknowledge_boundary();
            if (!boundary_start_ready || boundary_error || boundary_error_code != 3'd0)
                $fatal(1, "N=2 timeout ACK 后未恢复 idle");
        end
    endtask

    task automatic run_error_priority_case;
        integer measured_cycles;
        integer terminal_cycles;
        integer response_code;
        begin
            boundary_error_cycles = 0;
            fault_inject_code = 3'd6;
            fault_inject_valid = 1'b1;
            for (calibration_index = 0; calibration_index < 5;
                 calibration_index = calibration_index + 1) begin
                boundary_timeout_cycles = MAX_TIMEOUT;
                start_boundary();
                wait_boundary_memory_error(measured_cycles, response_code);
                wait_boundary_error(terminal_cycles);
                if (response_code != 6 || boundary_error_code != 3'd6)
                    $fatal(1, "memory fault calibration 未返回 INTERNAL code=%0d",
                           boundary_error_code);
                if (calibration_index == 0) boundary_error_cycles = measured_cycles;
                acknowledge_boundary();
            end
            boundary_timeout_cycles = boundary_error_cycles;
            start_boundary();
            wait_boundary_memory_error(measured_cycles, response_code);
            fault_inject_valid = 1'b0;
            fault_inject_code = 3'd0;
            if ((measured_cycles != boundary_error_cycles) ||
                boundary_error_code != 3'd6 || boundary_done || boundary_busy ||
                !boundary_error || !boundary_cancel || response_code != 6)
                $fatal(1, "原始 T10/T12 error 在 deadline handshake 必须优先 N=%0d got=%0d code=%0d",
                       boundary_error_cycles, measured_cycles, boundary_error_code);
            for (hold_count = 0; hold_count < 3; hold_count = hold_count + 1) begin
                @(posedge clk);
                #1;
                if (!boundary_error || boundary_error_code != 3'd6 || boundary_start_ready)
                    $fatal(1, "memory error 未保持到 completion ACK");
            end
            boundary_completion_hold_count = boundary_completion_hold_count + 3;
            acknowledge_boundary();
            if (!boundary_start_ready || boundary_error || boundary_error_code != 3'd0)
                $fatal(1, "memory error ACK 后无法接受 recovery start");
            boundary_error_priority_count = boundary_error_priority_count + 1;
            boundary_raw_error_priority_count = boundary_raw_error_priority_count + 1;
        end
    endtask

    task automatic run_done_priority_case;
        integer measured_cycles;
        begin
            boundary_success_cycles = 0;
            for (calibration_index = 0; calibration_index < 5;
                 calibration_index = calibration_index + 1) begin
                boundary_timeout_cycles = MAX_TIMEOUT;
                start_boundary();
                wait_boundary_done(measured_cycles);
                if (boundary_completed_elements != 17'd1)
                    $fatal(1, "单元素 boundary instance completed count 错误");
                if (calibration_index == 0) boundary_success_cycles = measured_cycles;
                acknowledge_boundary();
            end
            boundary_timeout_cycles = boundary_success_cycles;
            start_boundary();
            wait_boundary_done(measured_cycles);
            if (measured_cycles != boundary_success_cycles || boundary_error ||
                boundary_error_code != 3'd0 || boundary_completed_elements != 17'd1)
                $fatal(1, "第 N 个沿的 layer done 必须优先 timeout N=%0d got=%0d",
                       boundary_success_cycles, measured_cycles);
            for (hold_count = 0; hold_count < 3; hold_count = hold_count + 1) begin
                @(posedge clk);
                #1;
                if (!boundary_done || boundary_busy || boundary_start_ready ||
                    boundary_completed_elements != 17'd1)
                    $fatal(1, "boundary done 未保持到 completion ACK");
            end
            boundary_completion_hold_count = boundary_completion_hold_count + 3;
            acknowledge_boundary();
            if (!boundary_start_ready || boundary_done || boundary_error)
                $fatal(1, "boundary done ACK 后无法恢复");
            boundary_done_priority_count = boundary_done_priority_count + 1;
        end
    endtask

    task automatic start_full_layer;
        begin
            @(negedge clk);
            if (!full_start_ready || full_busy || full_done || full_error)
                $fatal(1, "full scheduler 未处于 idle");
            full_start_valid = 1'b1;
            @(posedge clk);
            @(negedge clk);
            full_start_valid = 1'b0;
        end
    endtask

    always @(posedge clk) begin
        if (master_reset || !master_owner) begin
            total_accepted_reads = total_accepted_reads;
            total_accepted_writes = total_accepted_writes;
        end else if (mem_valid && mem_ready) begin
            if (mem_error_code == 3'd0) begin
                if (mem_write) total_accepted_writes = total_accepted_writes + 1;
                else total_accepted_reads = total_accepted_reads + 1;
            end else begin
                total_error_responses = total_error_responses + 1;
            end

            if (!boundary_mode && (full_scoreboard_enable != 0) &&
                (mem_error_code != 3'd0)) begin
                $fatal(1, "full layer memory error=%0d addr=%08x",
                       mem_error_code, mem_addr);
            end
            if (!boundary_mode && (full_scoreboard_enable != 0) &&
                (mem_error_code == 3'd0)) begin
                selected_lane = selected_byte_lane(mem_write ? mem_wstrb : mem_rstrb);
                if ((selected_lane < 0) || (mem_addr[1:0] != 2'b00))
                    $fatal(1, "memory byte-lane 非 one-hot 或 word 未对齐 addr=%08x",
                           mem_addr);
                expected_byte_address = mem_addr + selected_lane;
                expected_lane = 4'b0001 << expected_byte_address[1:0];
                if (mem_write) begin
                    if ((mem_rstrb != 4'b0000) || (mem_wstrb != expected_lane) ||
                        (expected_byte_address != OUTPUT_BASE + full_output_writes) ||
                        (full_output_writes >= OUTPUT_BYTES) ||
                        (full_feature_reads != (full_output_writes + 1) * 4)) begin
                        $fatal(1, "output NCHW 地址/lane/时序错误 index=%0d addr=%08x reads=%0d",
                               full_output_writes, expected_byte_address, full_feature_reads);
                    end
                    sampled_byte = (mem_wdata >> (selected_lane * 8)) & 255;
                    if (sampled_byte != expected_output_bytes[full_output_writes])
                        $fatal(1, "output golden mismatch index=%0d got=%02x expected=%02x",
                               full_output_writes, sampled_byte,
                               expected_output_bytes[full_output_writes]);
                    if (trace_file != 0) $fdisplay(trace_file, "%02x", sampled_byte);
                    full_output_writes = full_output_writes + 1;
                    if ((full_output_writes % 1024) == 0)
                        $display("PROGRESS output=%0d/%0d feature_reads=%0d writes=%0d stalls=%0d",
                                 full_output_writes, OUTPUT_BYTES, full_feature_reads,
                                 full_output_writes, full_stall_cycles);
                end else begin
                    if ((mem_wstrb != 4'b0000) || (mem_rstrb != expected_lane) ||
                        (expected_byte_address < INPUT_BASE) ||
                        (expected_byte_address >= INPUT_BASE + INPUT_BYTES))
                        $fatal(1, "maxpool feature 读取 lane/range 错误 addr=%08x",
                               expected_byte_address);
                    expected_output_index = full_feature_reads / 4;
                    expected_tap_index = full_feature_reads % 4;
                    expected_channel = expected_output_index / (OUTPUT_DIMENSION * OUTPUT_DIMENSION);
                    expected_pixel = expected_output_index % (OUTPUT_DIMENSION * OUTPUT_DIMENSION);
                    expected_y = expected_pixel / OUTPUT_DIMENSION;
                    expected_x = expected_pixel % OUTPUT_DIMENSION;
                    expected_tap_y = expected_y * 2 + expected_tap_index / 2;
                    expected_tap_x = expected_x * 2 + expected_tap_index % 2;
                    expected_byte_address = INPUT_BASE + expected_channel *
                        (INPUT_DIMENSION * INPUT_DIMENSION) + expected_tap_y *
                        INPUT_DIMENSION + expected_tap_x;
                    if ((expected_output_index >= OUTPUT_BYTES) ||
                        (expected_channel >= INPUT_CHANNELS) ||
                        (mem_addr + selected_lane != expected_byte_address))
                        $fatal(1, "feature NCHW/tap 地址顺序错误 read=%0d got=%08x expected=%08x",
                               full_feature_reads, mem_addr + selected_lane,
                               expected_byte_address);
                    full_feature_reads = full_feature_reads + 1;
                end
            end
        end

        if (mem_valid && !mem_ready) begin
            total_stall_cycles = total_stall_cycles + 1;
            if (!boundary_mode && (full_scoreboard_enable != 0))
                full_stall_cycles = full_stall_cycles + 1;
        end
    end

    initial begin
        smoke_mode = $test$plusargs("SMOKE");
        total_accepted_reads = 0;
        total_accepted_writes = 0;
        total_error_responses = 0;
        full_feature_reads = 0;
        full_output_writes = 0;
        full_stall_cycles = 0;
        $readmemh("layer25_expected_output.hex", expected_output_bytes);
        repeat (3) @(posedge clk);
        while (!memory_initialized) @(posedge clk);
        @(negedge clk);
        full_hard_reset = 1'b0;
        boundary_hard_reset = 1'b0;
        initialize_fixture();

        run_zero_timeout_case();
        run_timeout_one_cycle_case();
        run_timeout_two_cycle_case();
        run_boundary_warmup();
        run_boundary_warmup();
        run_pending_abort_case();
        run_pending_reset_case();
        run_boundary_warmup();
        run_boundary_warmup();
        run_boundary_warmup();
        run_boundary_warmup();
        run_pending_timeout_case();
        run_error_priority_case();
        run_done_priority_case();

        if ((boundary_zero_timeout_count != 1) || (boundary_timeout_n1_count != 1) ||
            (boundary_timeout_n2_count != 1) || (boundary_abort_count != 1) ||
            (boundary_reset_count != 1) || (boundary_timeout_count != 1) ||
            (boundary_error_priority_count != 1) || (boundary_done_priority_count != 1) ||
            (boundary_raw_error_priority_count != 1) ||
            (boundary_completion_hold_count != 9))
            $fatal(1, "G0 timeout/reset/abort/done/error 覆盖计数错误");

        boundary_mode = 1'b0;
        fault_inject_valid = 1'b0;
        fault_inject_code = 3'd0;
        full_timeout_cycles = MAX_TIMEOUT;
        full_scoreboard_enable = 1;
        trace_file = $fopen("observed_output_hex.txt", "w");
        if (trace_file == 0) $fatal(1, "无法创建 output trace");
        start_full_layer();

        if (smoke_mode != 0) begin
            timeout_count = 0;
            while ((full_completed_elements < 17'd1) && !full_error &&
                   (timeout_count < 200000)) begin
                @(negedge clk);
                timeout_count = timeout_count + 1;
            end
            if ((full_output_writes != 1) || full_error || !full_busy ||
                full_completed_elements != 17'd1 || full_feature_reads != 4)
                $fatal(1, "smoke 未完成首个输出 write=%0d read=%0d error=%0d",
                       full_output_writes, full_feature_reads, full_error);
            @(negedge clk);
            full_abort = 1'b1;
            @(posedge clk);
            @(negedge clk);
            full_abort = 1'b0;
            repeat (4) @(posedge clk);
            $fclose(trace_file);
            trace_file = 0;
            full_scoreboard_enable = 0;
            if (full_busy || full_done || full_error || !full_start_ready ||
                full_output_writes != 1 || full_feature_reads != 4 ||
                u_memory.patch_count != 1353 || u_memory.pending ||
                u_memory_master.pending)
                $fatal(1, "smoke abort/计数/patch/memory 状态错误");
            $display("RESULT mode=SMOKE inputs=%0d input_sentinels=%0d patches=%0d output=%0d feature_reads=%0d writes=%0d stalls=%0d abort=%0d timeout=%0d zero_timeout=%0d timeout_n1=%0d timeout_n2=%0d reset=%0d error_priority=%0d raw_memory_error_priority=%0d done_priority=%0d",
                     INPUT_BYTES, input_sentinel_count, u_memory.patch_count,
                     full_output_writes, full_feature_reads, full_output_writes,
                     full_stall_cycles, boundary_abort_count, boundary_timeout_count,
                     boundary_zero_timeout_count, boundary_timeout_n1_count,
                     boundary_timeout_n2_count, boundary_reset_count,
                     boundary_error_priority_count, boundary_raw_error_priority_count,
                     boundary_done_priority_count);
            $display("PASS S2A-T21 focused smoke");
            $finish;
        end

        for (hold_count = 0; hold_count < 3; hold_count = hold_count + 1) begin
            @(negedge clk);
            if (!full_busy || full_start_ready || full_done || full_error)
                $fatal(1, "full busy/start backpressure 状态错误");
            full_start_valid = 1'b1;
            @(posedge clk);
            @(negedge clk);
            full_start_valid = 1'b0;
            full_busy_start_checks = full_busy_start_checks + 1;
        end

        timeout_count = 0;
        while (!full_done && !full_error && (timeout_count < 2000000000)) begin
            @(posedge clk);
            #1;
            timeout_count = timeout_count + 1;
        end
        if (!full_done || full_error || full_error_code != 3'd0 || full_busy ||
            full_completed_elements != OUTPUT_BYTES || full_feature_reads != OUTPUT_BYTES * 4 ||
            full_output_writes != OUTPUT_BYTES || full_stall_cycles < 100000 ||
            u_memory.patch_count != 1352 + OUTPUT_BYTES ||
            u_memory_master.pending || u_memory.pending)
            $fatal(1, "full layer 状态/请求/patch 计数错误 done=%0d error=%0d code=%0d elements=%0d reads=%0d writes=%0d patches=%0d stalls=%0d",
                   full_done, full_error, full_error_code, full_completed_elements,
                   full_feature_reads, full_output_writes, u_memory.patch_count,
                   full_stall_cycles);
        $fclose(trace_file);
        trace_file = 0;
        full_scoreboard_enable = 0;
        for (hold_count = 0; hold_count < 9; hold_count = hold_count + 1) begin
            @(posedge clk);
            #1;
            if (!full_done || full_busy || full_start_ready ||
                full_completed_elements != OUTPUT_BYTES)
                $fatal(1, "full done 未保持到 completion ACK");
            full_done_hold_count = full_done_hold_count + 1;
        end
        @(negedge clk);
        full_completion_ready = 1'b1;
        @(posedge clk);
        @(negedge clk);
        full_completion_ready = 1'b0;
        if (!full_start_ready || full_done || full_error || full_error_code != 3'd0)
            $fatal(1, "full completion ACK 后未恢复 idle");
        $display("RESULT mode=FULL input_sentinels=%0d output=%0d feature_reads=%0d writes=%0d stalls=%0d patches=%0d busy_start_checks=%0d done_hold=%0d timeout=%0d zero_timeout=%0d timeout_n1=%0d timeout_n2=%0d abort=%0d reset=%0d error_priority=%0d raw_memory_error_priority=%0d done_priority=%0d timeout_priority_cycles=%0d done_priority_cycles=%0d",
                 input_sentinel_count, full_completed_elements, full_feature_reads,
                 full_output_writes, full_stall_cycles, u_memory.patch_count,
                 full_busy_start_checks, full_done_hold_count,
                 boundary_timeout_count, boundary_zero_timeout_count,
                 boundary_timeout_n1_count, boundary_timeout_n2_count,
                 boundary_abort_count, boundary_reset_count,
                 boundary_error_priority_count, boundary_raw_error_priority_count,
                 boundary_done_priority_count, boundary_error_cycles,
                 boundary_success_cycles);
        $display("PASS S2A-T21 complete tiny416 layer25 maxpool scheduler");
        $finish;
    end
endmodule
