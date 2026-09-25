// S2A-T20：layer36 整层卷积调度器与 T10/T12 memory 协议仿真。
`timescale 1ns/1ps
module tb_s2a_conv_layer_scheduler;
    localparam logic [31:0] INPUT_BASE = 32'd27966080;
    localparam integer INPUT_BYTES = 173056;
    localparam integer INPUT_CHANNELS = 256;
    localparam logic [31:0] WEIGHT_BASE = 32'd1048576;
    localparam logic [31:0] WEIGHT_OFFSET = 32'd5895420;
    localparam integer WEIGHT_BYTES = 7680;
    localparam logic [31:0] OUTPUT_BASE = 32'd28139136;
    localparam integer OUTPUT_BYTES = 20280;
    localparam integer REDUCTION_LENGTH = 256;
    localparam integer PATCH_CAPACITY = 32768;
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
    logic [14:0] full_completed_elements;
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
    logic [14:0] boundary_completed_elements;
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
    logic force_master_hold = 1'b0;
    logic master_owner;
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

    logic [7:0] layer36_weight_bytes [0:WEIGHT_BYTES-1];
    logic [7:0] expected_output_bytes [0:OUTPUT_BYTES-1];
    integer input_sentinel_count = 0;
    integer total_accepted_reads = 0;
    integer total_accepted_writes = 0;
    integer total_error_responses = 0;
    integer total_stall_cycles = 0;
    integer boundary_abort_count = 0;
    integer boundary_timeout_count = 0;
    integer boundary_reset_count = 0;
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
    integer full_weight_reads = 0;
    integer full_output_writes = 0;
    integer full_stall_cycles = 0;
    integer full_scoreboard_enable = 0;
    integer full_feature_weight_pending = 0;
    integer previous_progress = 0;
    integer trace_file = 0;
    integer selected_lane;
    integer expected_output_index;
    integer expected_reduction_index;
    integer expected_channel;
    integer expected_pixel;
    integer sampled_byte;
    integer sim_cycle_count;
    integer timeout_count;
    integer hold_count;
    integer weight_index;
    integer input_index;
    integer weight_seeded_count = 0;
    integer global_reads_before;
    integer global_writes_before;
    integer boundary_error_cycles = 0;
    integer boundary_success_cycles = 0;
    integer boundary_cycles_current;
    integer calibration_index;
    integer smoke_mode = 0;
    logic [31:0] expected_byte_address;
    logic [31:0] expected_word_address;
    logic [3:0] expected_lane;

    always #5 clk = ~clk;

    s2a_conv_layer_scheduler u_full_scheduler (
        .clk(clk),
        .hard_reset(full_hard_reset),
        .abort(full_abort),
        .buffer_owner_pl(1'b1),
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

    // 独立单元素实例仅用于精确检查第 N 个沿的 done/error 优先级。
    s2a_conv_layer_scheduler #(
        .OUTPUT_COUNT_LIMIT(15'd1)
    ) u_boundary_scheduler (
        .clk(clk),
        .hard_reset(boundary_hard_reset),
        .abort(boundary_abort),
        .buffer_owner_pl(1'b1),
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
        master_owner = !force_master_hold;
        master_cancel = 1'b0;
        master_req_valid = 1'b0;
        master_req_write = 1'b0;
        master_req_addr = 32'd0;
        master_req_wdata = 32'd0;
        master_req_rstrb = 4'd0;
        master_req_wstrb = 4'd0;
        full_req_ready = 1'b0;
        boundary_req_ready = 1'b0;
        full_rsp_valid = 1'b0;
        full_rsp_rdata = 32'd0;
        full_rsp_error = 3'd0;
        boundary_rsp_valid = 1'b0;
        boundary_rsp_rdata = 32'd0;
        boundary_rsp_error = 3'd0;
        if (boundary_mode) begin
            master_cancel = boundary_cancel;
            master_req_valid = boundary_req_valid;
            master_req_write = boundary_req_write;
            master_req_addr = boundary_req_addr;
            master_req_wdata = boundary_req_wdata;
            master_req_rstrb = boundary_req_rstrb;
            master_req_wstrb = boundary_req_wstrb;
            boundary_req_ready = master_req_ready;
            boundary_rsp_valid = master_rsp_valid;
            boundary_rsp_rdata = master_rsp_rdata;
            boundary_rsp_error = master_rsp_error;
        end else begin
            master_cancel = full_cancel;
            master_req_valid = full_req_valid;
            master_req_write = full_req_write;
            master_req_addr = full_req_addr;
            master_req_wdata = full_req_wdata;
            master_req_rstrb = full_req_rstrb;
            master_req_wstrb = full_req_wstrb;
            full_req_ready = master_req_ready;
            full_rsp_valid = master_rsp_valid;
            full_rsp_rdata = master_rsp_rdata;
            full_rsp_error = master_rsp_error;
        end
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
            if (!boundary_error) begin
                $fatal(1, "boundary scheduler 等待 error 超时");
            end
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
            if (response_seen == 0) begin
                $fatal(1, "没有观察到原始 T10/T12 memory error response 握手");
            end
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
            if (!boundary_done || boundary_error) begin
                $fatal(1, "boundary scheduler 等待 done 超时或返回错误 code=%0d",
                       boundary_error_code);
            end
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
            if (!(boundary_req_valid && !boundary_req_write)) begin
                $fatal(1, "没有观察到等待中的 layer36 feature 请求");
            end
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
            if (!(boundary_req_valid && boundary_req_write)) begin
                $fatal(1, "没有观察到等待中的 layer36 output 请求");
            end
        end
    endtask

    task automatic wait_pending_memory_read;
        begin
            timeout_count = 0;
            while (!(boundary_mode && mem_valid && !mem_ready && !mem_write &&
                     u_memory.pending) &&
                   (timeout_count < 1000)) begin
                @(negedge clk);
                timeout_count = timeout_count + 1;
            end
            if (!(boundary_mode && mem_valid && !mem_ready && !mem_write) ||
                !u_memory.pending) begin
                $fatal(1, "没有观察到 T10 pending feature read idx=%0d pending=%0d req=%0d master_ready=%0d mem_valid=%0d mem_ready=%0d write=%0d addr=%08x busy=%0d error=%0d state=%0d",
                       u_memory.stall_index[2], u_memory.pending,
                       boundary_req_valid, master_req_ready, mem_valid,
                       mem_ready, mem_write, mem_addr, boundary_busy,
                       boundary_error, u_boundary_scheduler.state);
            end
        end
    endtask

    task automatic wait_pending_memory_write;
        begin
            timeout_count = 0;
            while (!(boundary_mode && mem_valid && !mem_ready && mem_write &&
                     u_memory.pending) &&
                   (timeout_count < 20000)) begin
                @(negedge clk);
                timeout_count = timeout_count + 1;
            end
            if (!(boundary_mode && mem_valid && !mem_ready && mem_write) ||
                !u_memory.pending) begin
                $fatal(1, "没有观察到 T10 中的 pending output write");
            end
        end
    endtask

    task automatic run_boundary_warmup;
        integer warmup_cycles;
        begin
            boundary_timeout_cycles = MAX_TIMEOUT;
            start_boundary();
            wait_boundary_done(warmup_cycles);
            if (boundary_completed_elements != 15'd1) begin
                $fatal(1, "boundary warmup 未完成首个输出");
            end
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
                total_accepted_writes != global_writes_before || u_memory.pending) begin
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
                u_memory.pending) begin
                $fatal(1, "pending write hard reset 后有输出副作用或未恢复");
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
            boundary_timeout_cycles = 32'd8;
            start_boundary();
            elapsed = 0;
            pending_seen = 1'b0;
            while (!boundary_error && (elapsed < 1000)) begin
                @(posedge clk);
                if (boundary_mode && mem_valid && !mem_ready && !mem_write &&
                    u_memory.pending) begin
                    pending_seen = 1'b1;
                end
                #1;
                elapsed = elapsed + 1;
            end
            if (u_memory.stall_index[2] == 0) begin
                $fatal(1, "timeout 用例必须落在 T10 有停顿的 READ_FEATURE 槽位");
            end
            boundary_cycles_current = elapsed;
            if ((boundary_error_code != 3'd5) || boundary_done || boundary_busy ||
                (boundary_cycles_current != 8) || !pending_seen ||
                (total_accepted_reads != global_reads_before) ||
                (total_accepted_writes != global_writes_before)) begin
                $fatal(1, "G0 第8个后续沿 pending-read timeout/cancel 错误 code=%0d cycles=%0d pending_seen=%0d",
                       boundary_error_code, boundary_cycles_current, pending_seen);
            end
            repeat (4) @(posedge clk);
            if (total_accepted_reads != global_reads_before ||
                total_accepted_writes != global_writes_before || u_memory.pending) begin
                $fatal(1, "timeout cancel 后释放 memory master 产生延迟副作用");
            end
            for (hold_count = 0; hold_count < 3; hold_count = hold_count + 1) begin
                @(posedge clk);
                #1;
                if (!boundary_error || (boundary_error_code != 3'd5) ||
                    boundary_start_ready) begin
                    $fatal(1, "timeout error 未保持到 completion ACK");
                end
            end
            boundary_completion_hold_count = boundary_completion_hold_count + 3;
            acknowledge_boundary();
            if (!boundary_start_ready || boundary_error || boundary_error_code != 3'd0) begin
                $fatal(1, "timeout ACK 后 scheduler 未恢复 idle");
            end
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
                boundary_done || (total_accepted_reads != global_reads_before) ||
                (total_accepted_writes != global_writes_before)) begin
                $fatal(1, "zero timeout 必须返回 BAD_ARGUMENT 且不发 memory 请求");
            end
            acknowledge_boundary();
            if (!boundary_start_ready || boundary_error) begin
                $fatal(1, "zero timeout ACK 后无法恢复");
            end
            boundary_zero_timeout_count = boundary_zero_timeout_count + 1;
        end
    endtask

    task automatic run_timeout_one_cycle_case;
        begin
            boundary_timeout_cycles = 32'd1;
            start_boundary();
            if (!boundary_busy || boundary_error || boundary_cancel ||
                boundary_req_valid) begin
                $fatal(1, "N=1 timeout 必须在第一个后续沿前保留完整工作周期");
            end
            @(posedge clk);
            #1;
            if (!boundary_error || (boundary_error_code != 3'd5) ||
                boundary_busy || !boundary_cancel || boundary_req_valid ||
                boundary_rsp_valid || u_memory.pending || u_memory_master.pending ||
                (u_boundary_scheduler.u_element_engine.state != 4'd1)) begin
                $fatal(1, "N=1 第一个后续沿 timeout/cancel 状态错误 code=%0d child_state=%0d",
                       boundary_error_code,
                       u_boundary_scheduler.u_element_engine.state);
            end
            boundary_timeout_n1_count = boundary_timeout_n1_count + 1;
            acknowledge_boundary();
            if (!boundary_start_ready || boundary_error || boundary_error_code != 3'd0) begin
                $fatal(1, "N=1 timeout ACK 后未恢复 idle");
            end
        end
    endtask

    task automatic run_timeout_two_cycle_case;
        begin
            boundary_timeout_cycles = 32'd2;
            start_boundary();
            if (!boundary_busy || boundary_error || boundary_cancel ||
                boundary_req_valid) begin
                $fatal(1, "N=2 timeout 在起始接受后不应提前取消");
            end
            @(posedge clk);
            #1;
            if (!boundary_busy || boundary_error || boundary_cancel ||
                (u_boundary_scheduler.elapsed_cycles != 32'd1) ||
                (u_boundary_scheduler.u_element_engine.state != 4'd1)) begin
                $fatal(1, "N=2 第一个后续沿必须保留工作并计数为1");
            end
            @(posedge clk);
            #1;
            if (!boundary_error || (boundary_error_code != 3'd5) ||
                boundary_busy || !boundary_cancel || boundary_req_valid ||
                boundary_rsp_valid || u_memory.pending || u_memory_master.pending ||
                (u_boundary_scheduler.u_element_engine.state != 4'd2)) begin
                $fatal(1, "N=2 第二个后续沿 timeout/cancel 状态错误 code=%0d child_state=%0d",
                       boundary_error_code,
                       u_boundary_scheduler.u_element_engine.state);
            end
            boundary_timeout_n2_count = boundary_timeout_n2_count + 1;
            acknowledge_boundary();
            if (!boundary_start_ready || boundary_error || boundary_error_code != 3'd0) begin
                $fatal(1, "N=2 timeout ACK 后未恢复 idle");
            end
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
                if ((response_code != 6) || (boundary_error_code != 3'd6)) begin
                    $fatal(1, "memory fault 校准没有返回 INTERNAL：%0d",
                           boundary_error_code);
                end
                if (calibration_index == 0) begin
                    boundary_error_cycles = measured_cycles;
                end
                acknowledge_boundary();
            end
            boundary_timeout_cycles = boundary_error_cycles;
            start_boundary();
            wait_boundary_memory_error(measured_cycles, response_code);
            fault_inject_valid = 1'b0;
            fault_inject_code = 3'd0;
            if ((measured_cycles != boundary_error_cycles) ||
                (boundary_error_code != 3'd6) || boundary_done || boundary_busy ||
                !boundary_error || !boundary_cancel ||
                (response_code != 6)) begin
                $fatal(1, "原始 memory error response 必须在 Nth deadline 握手并优先于 timeout N=%0d got=%0d code=%0d response=%0d",
                       boundary_error_cycles, measured_cycles,
                       boundary_error_code, response_code);
            end
            for (hold_count = 0; hold_count < 3; hold_count = hold_count + 1) begin
                @(posedge clk);
                #1;
                if (!boundary_error || boundary_error_code != 3'd6 ||
                    boundary_start_ready) begin
                    $fatal(1, "memory error 未保持到 completion ACK");
                end
            end
            boundary_completion_hold_count = boundary_completion_hold_count + 3;
            acknowledge_boundary();
            if (!boundary_start_ready || boundary_error || boundary_error_code != 3'd0) begin
                $fatal(1, "memory error ACK 后无法接受 recovery start");
            end
            boundary_error_priority_count = boundary_error_priority_count + 1;
            boundary_raw_error_priority_count =
                boundary_raw_error_priority_count + 1;
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
                if (boundary_completed_elements != 15'd1) begin
                    $fatal(1, "one-element boundary instance completed count 错误");
                end
                if (calibration_index == 0) begin
                    boundary_success_cycles = measured_cycles;
                end
                acknowledge_boundary();
            end
            boundary_timeout_cycles = boundary_success_cycles;
            start_boundary();
            wait_boundary_done(measured_cycles);
            if ((measured_cycles != boundary_success_cycles) ||
                boundary_error || (boundary_error_code != 3'd0) ||
                (boundary_completed_elements != 15'd1)) begin
                $fatal(1, "第 N 个沿的 layer completion 必须优先于 timeout N=%0d got=%0d code=%0d",
                       boundary_success_cycles, measured_cycles, boundary_error_code);
            end
            for (hold_count = 0; hold_count < 3; hold_count = hold_count + 1) begin
                @(posedge clk);
                #1;
                if (!boundary_done || boundary_busy || boundary_start_ready ||
                    boundary_completed_elements != 15'd1) begin
                    $fatal(1, "boundary done 未保持到 completion ACK");
                end
            end
            boundary_completion_hold_count = boundary_completion_hold_count + 3;
            acknowledge_boundary();
            if (!boundary_start_ready || boundary_done || boundary_error) begin
                $fatal(1, "boundary done ACK 后无法恢复");
            end
            boundary_done_priority_count = boundary_done_priority_count + 1;
        end
    endtask

    task automatic start_full_layer;
        begin
            @(negedge clk);
            if (!full_start_ready || full_busy || full_done || full_error) begin
                $fatal(1, "full layer scheduler 未处于 idle");
            end
            full_start_valid = 1'b1;
            @(posedge clk);
            @(negedge clk);
            full_start_valid = 1'b0;
        end
    endtask

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
                if ((input_index != 0) && ((input_index % 16384) == 0)) begin
                    $display("PROGRESS input_fixture=%0d/%0d sentinel_patches=%0d",
                             input_index, INPUT_BYTES, input_sentinel_count);
                end
            end
            if (input_sentinel_count != 675) begin
                $fatal(1, "T10 initial_byte 中 raw -128 数量不匹配：%0d",
                       input_sentinel_count);
            end
            for (weight_index = 0; weight_index < WEIGHT_BYTES; weight_index = weight_index + 1) begin
                u_memory.store_byte(WEIGHT_BASE + WEIGHT_OFFSET + weight_index,
                                    layer36_weight_bytes[weight_index]);
                if ((weight_index != 0) && ((weight_index % 1024) == 0)) begin
                    $display("PROGRESS weight_fixture=%0d/%0d",
                             weight_index, WEIGHT_BYTES);
                end
            end
            weight_seeded_count = WEIGHT_BYTES;
            if (u_memory.patch_count != 675 + WEIGHT_BYTES) begin
                $fatal(1, "输入修正与 layer36 权重 patch 数不符：%0d", u_memory.patch_count);
            end
            $display("PROGRESS fixture_ready input=%0d sentinels=%0d weights=%0d patches=%0d",
                     INPUT_BYTES, input_sentinel_count, weight_seeded_count,
                     u_memory.patch_count);
        end
    endtask

    always @(posedge clk) begin
        if (mem_valid && mem_ready) begin
            if (mem_error_code == 3'd0) begin
                if (mem_write) begin
                    total_accepted_writes = total_accepted_writes + 1;
                end else begin
                    total_accepted_reads = total_accepted_reads + 1;
                end
            end else begin
                total_error_responses = total_error_responses + 1;
                if (full_scoreboard_enable != 0) begin
                    $fatal(1, "full layer 出现 memory error=%0d address=%08x",
                           mem_error_code, mem_addr);
                end
            end

            if (full_scoreboard_enable != 0) begin
                selected_lane = mem_write ? selected_byte_lane(mem_wstrb) :
                                            selected_byte_lane(mem_rstrb);
                if ((selected_lane < 0) || (mem_addr[1:0] != 2'b00)) begin
                    $fatal(1, "byte-lane request 非 one-hot 或 word 未对齐 addr=%08x read=%x write=%x",
                           mem_addr, mem_rstrb, mem_wstrb);
                end
                expected_byte_address = mem_addr + selected_lane;
                expected_lane = 4'b0001 << expected_byte_address[1:0];
                if (mem_write) begin
                    if ((mem_rstrb != 4'b0000) || (mem_wstrb != expected_lane) ||
                        (expected_byte_address != OUTPUT_BASE + full_output_writes) ||
                        (full_output_writes >= OUTPUT_BYTES) ||
                        (full_feature_weight_pending != 0) ||
                        (full_feature_reads != (full_output_writes + 1) * REDUCTION_LENGTH) ||
                        (full_weight_reads != (full_output_writes + 1) * REDUCTION_LENGTH)) begin
                        $fatal(1, "output 写地址/lane/顺序错误 index=%0d addr=%08x feature=%0d weight=%0d",
                               full_output_writes, expected_byte_address,
                               full_feature_reads, full_weight_reads);
                    end
                    sampled_byte = (mem_wdata >> (selected_lane * 8)) & 255;
                    if (sampled_byte != expected_output_bytes[full_output_writes]) begin
                        $fatal(1, "output byte 与 Python golden 不符 index=%0d got=%02x expected=%02x",
                               full_output_writes, sampled_byte,
                               expected_output_bytes[full_output_writes]);
                    end
                    if (trace_file != 0) begin
                        $fdisplay(trace_file, "%02x", sampled_byte);
                    end
                    full_output_writes = full_output_writes + 1;
                    if ((full_output_writes % 128) == 0) begin
                        $display("PROGRESS output=%0d/%0d feature_reads=%0d weight_reads=%0d writes=%0d stalls=%0d",
                                 full_output_writes, OUTPUT_BYTES,
                                 full_feature_reads, full_weight_reads,
                                 full_output_writes, full_stall_cycles);
                    end
                end else if ((expected_byte_address >= INPUT_BASE) &&
                             (expected_byte_address < INPUT_BASE + INPUT_BYTES)) begin
                    if ((mem_wstrb != 4'b0000) || (mem_rstrb != expected_lane) ||
                        (full_feature_weight_pending != 0) ||
                        (full_feature_reads != full_weight_reads)) begin
                        $fatal(1, "feature 读取 lane 或 feature/weight 次序错误");
                    end
                    expected_output_index = full_feature_reads / REDUCTION_LENGTH;
                    expected_reduction_index = full_feature_reads % REDUCTION_LENGTH;
                    expected_channel = expected_output_index / (26 * 26);
                    expected_pixel = expected_output_index % (26 * 26);
                    expected_byte_address = INPUT_BASE +
                        expected_reduction_index * (26 * 26) + expected_pixel;
                    if ((expected_output_index >= OUTPUT_BYTES) ||
                        (mem_addr + selected_lane != expected_byte_address) ||
                        (expected_channel >= 30)) begin
                        $fatal(1, "feature NCHW/reduction 地址错误 read=%0d got=%08x expected=%08x",
                               full_feature_reads, mem_addr + selected_lane,
                               expected_byte_address);
                    end
                    full_feature_reads = full_feature_reads + 1;
                    full_feature_weight_pending = 1;
                end else if ((expected_byte_address >= WEIGHT_BASE + WEIGHT_OFFSET) &&
                             (expected_byte_address < WEIGHT_BASE + WEIGHT_OFFSET + WEIGHT_BYTES)) begin
                    if ((mem_wstrb != 4'b0000) || (mem_rstrb != expected_lane) ||
                        (full_feature_weight_pending != 1) ||
                        (full_weight_reads + 1 != full_feature_reads)) begin
                        $fatal(1, "weight 读取 lane 或 feature/weight 次序错误");
                    end
                    expected_output_index = full_weight_reads / REDUCTION_LENGTH;
                    expected_reduction_index = full_weight_reads % REDUCTION_LENGTH;
                    expected_channel = expected_output_index / (26 * 26);
                    expected_pixel = expected_output_index % (26 * 26);
                    expected_byte_address = WEIGHT_BASE + WEIGHT_OFFSET +
                        expected_channel * REDUCTION_LENGTH + expected_reduction_index;
                    if ((expected_output_index >= OUTPUT_BYTES) ||
                        (mem_addr + selected_lane != expected_byte_address) ||
                        (expected_channel >= 30) || (expected_pixel >= 676)) begin
                        $fatal(1, "GF8 weight channel/K 地址错误 read=%0d got=%08x expected=%08x",
                               full_weight_reads, mem_addr + selected_lane,
                               expected_byte_address);
                    end
                    full_weight_reads = full_weight_reads + 1;
                    full_feature_weight_pending = 0;
                end else begin
                    $fatal(1, "full layer 访问了冻结 feature/weight 范围外地址 %08x",
                           expected_byte_address);
                end
            end
        end

        if (mem_valid && !mem_ready) begin
            total_stall_cycles = total_stall_cycles + 1;
            if (full_scoreboard_enable != 0) begin
                full_stall_cycles = full_stall_cycles + 1;
            end
        end
    end

    initial begin
        smoke_mode = $test$plusargs("SMOKE");
        total_accepted_reads = 0;
        total_accepted_writes = 0;
        total_error_responses = 0;
        total_stall_cycles = 0;
        full_feature_reads = 0;
        full_weight_reads = 0;
        full_output_writes = 0;
        full_feature_weight_pending = 0;
        full_stall_cycles = 0;

        $readmemh("layer36_weights.hex", layer36_weight_bytes);
        $readmemh("layer36_expected_output.hex", expected_output_bytes);
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
        run_pending_timeout_case();
        run_error_priority_case();
        run_done_priority_case();

        if ((boundary_zero_timeout_count != 1) ||
            (boundary_timeout_n1_count != 1) ||
            (boundary_timeout_n2_count != 1) || (boundary_abort_count != 1) ||
            (boundary_reset_count != 1) || (boundary_timeout_count != 1) ||
            (boundary_error_priority_count != 1) || (boundary_done_priority_count != 1) ||
            (boundary_raw_error_priority_count != 1) ||
            (boundary_completion_hold_count != 9)) begin
            $fatal(1, "G0 timeout/reset/abort/done/error 边界覆盖计数错误");
        end

        boundary_mode = 1'b0;
        full_timeout_cycles = MAX_TIMEOUT;
        full_scoreboard_enable = 1;
        trace_file = $fopen("observed_output_hex.txt", "w");
        if (trace_file == 0) begin
            $fatal(1, "无法创建完整 output trace");
        end
        start_full_layer();

        if (smoke_mode != 0) begin
            timeout_count = 0;
            while ((full_completed_elements < 1) && !full_error &&
                   (timeout_count < 200000)) begin
                @(negedge clk);
                timeout_count = timeout_count + 1;
            end
            if ((full_output_writes != 1) || full_error || !full_busy ||
                (full_completed_elements != 15'd1)) begin
                $fatal(1, "smoke 未完成首元素 output=%0d error=%0d code=%0d busy=%0d done=%0d completed=%0d feature=%0d weight=%0d mem_valid=%0d mem_ready=%0d mem_write=%0d mem_addr=%08x master_pending=%0d state=%0d child_error=%0d child_code=%0d",
                       full_output_writes, full_error, full_error_code,
                       full_busy, full_done, full_completed_elements,
                       full_feature_reads, full_weight_reads, mem_valid,
                       mem_ready, mem_write, mem_addr,
                       u_memory_master.pending, u_full_scheduler.state,
                       u_full_scheduler.child_result_valid,
                       u_full_scheduler.child_result_error_code);
            end
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
                (full_output_writes != 1) || (full_feature_reads != REDUCTION_LENGTH) ||
                (full_weight_reads != REDUCTION_LENGTH) ||
                (full_feature_weight_pending != 0) ||
                (u_memory.patch_count != 675 + WEIGHT_BYTES + 1)) begin
                $fatal(1, "smoke abort state/output/read/write/pending/patch 错误 busy=%0d done=%0d error=%0d code=%0d ready=%0d out=%0d feature=%0d weight=%0d pair=%0d master_pending=%0d mem_pending=%0d patches=%0d scheduler_state=%0d",
                       full_busy, full_done, full_error, full_error_code,
                       full_start_ready, full_output_writes,
                       full_feature_reads, full_weight_reads,
                       full_feature_weight_pending, u_memory_master.pending,
                       u_memory.pending, u_memory.patch_count,
                       u_full_scheduler.state);
            end
            $display("RESULT mode=SMOKE inputs=%0d input_sentinels=%0d weights=%0d patches=%0d output=%0d feature_reads=%0d weight_reads=%0d abort=%0d timeout=%0d zero_timeout=%0d timeout_n1=%0d timeout_n2=%0d reset=%0d error_priority=%0d raw_memory_error_priority=%0d done_priority=%0d",
                     INPUT_BYTES, input_sentinel_count, weight_seeded_count,
                     u_memory.patch_count, full_output_writes,
                     full_feature_reads, full_weight_reads,
                     boundary_abort_count, boundary_timeout_count,
                     boundary_zero_timeout_count,
                     boundary_timeout_n1_count, boundary_timeout_n2_count,
                     boundary_reset_count, boundary_error_priority_count,
                     boundary_raw_error_priority_count,
                     boundary_done_priority_count);
            $display("PASS S2A-T20 focused smoke");
            $finish;
        end

        for (hold_count = 0; hold_count < 3; hold_count = hold_count + 1) begin
            @(negedge clk);
            if (!full_busy || full_start_ready || full_done || full_error) begin
                $fatal(1, "full layer busy/start backpressure 状态错误");
            end
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
        if (!full_done || full_error || (full_error_code != 3'd0) ||
            full_busy || (full_completed_elements != OUTPUT_BYTES) ||
            (full_feature_reads != OUTPUT_BYTES * REDUCTION_LENGTH) ||
            (full_weight_reads != OUTPUT_BYTES * REDUCTION_LENGTH) ||
            (full_output_writes != OUTPUT_BYTES) || (full_feature_weight_pending != 0) ||
            (full_stall_cycles < 100000) ||
            (u_memory.patch_count != 675 + WEIGHT_BYTES + OUTPUT_BYTES)) begin
            $fatal(1, "full layer coverage/state/patch count 错误 done=%0d error=%0d code=%0d elements=%0d f=%0d w=%0d out=%0d patches=%0d",
                   full_done, full_error, full_error_code, full_completed_elements,
                   full_feature_reads, full_weight_reads, full_output_writes,
                   u_memory.patch_count);
        end
        $fclose(trace_file);
        trace_file = 0;
        full_scoreboard_enable = 0;
        for (hold_count = 0; hold_count < 3; hold_count = hold_count + 1) begin
            @(posedge clk);
            #1;
            if (!full_done || full_busy || full_start_ready ||
                (full_completed_elements != OUTPUT_BYTES)) begin
                $fatal(1, "full done 未保持到 completion ACK");
            end
            full_done_hold_count = full_done_hold_count + 1;
        end
        @(negedge clk);
        full_completion_ready = 1'b1;
        @(posedge clk);
        @(negedge clk);
        full_completion_ready = 1'b0;
        if (!full_start_ready || full_done || full_error ||
            (full_error_code != 3'd0)) begin
            $fatal(1, "full completion ACK 后未恢复 idle");
        end
        $display("RESULT mode=FULL output=%0d feature_reads=%0d weight_reads=%0d writes=%0d stalls=%0d patches=%0d busy_start_checks=%0d done_hold=%0d timeout=%0d zero_timeout=%0d timeout_n1=%0d timeout_n2=%0d abort=%0d reset=%0d error_priority=%0d raw_memory_error_priority=%0d done_priority=%0d timeout_priority_cycles=%0d done_priority_cycles=%0d",
                 full_completed_elements, full_feature_reads, full_weight_reads,
                 full_output_writes, full_stall_cycles, u_memory.patch_count,
                 full_busy_start_checks, full_done_hold_count,
                 boundary_timeout_count, boundary_zero_timeout_count,
                 boundary_timeout_n1_count, boundary_timeout_n2_count,
                 boundary_abort_count,
                 boundary_reset_count, boundary_error_priority_count,
                 boundary_raw_error_priority_count,
                 boundary_done_priority_count, boundary_error_cycles,
                 boundary_success_cycles);
        $display("PASS S2A-T20 complete tiny416 layer36 convolution scheduler");
        $finish;
    end
endmodule
