// 用 G0 layer33 向量与 T10/T12 memory contract 验证单元素复制事务。
module tb_s2a_upsample_engine;
    logic clk = 1'b0;
    always #5 clk = ~clk;

    logic hard_reset;
    logic abort;
    logic start_valid;
    logic start_ready;
    logic [31:0] input_base_address;
    logic [31:0] input_length_bytes;
    logic [31:0] output_base_address;
    logic [31:0] output_length_bytes;
    logic [31:0] input_channels;
    logic [31:0] input_height;
    logic [31:0] input_width;
    logic [31:0] stride;
    logic [31:0] output_channel;
    logic [31:0] output_y;
    logic [31:0] output_x;

    logic backend_cancel;
    logic engine_req_valid;
    logic engine_req_ready;
    logic engine_req_write;
    logic [31:0] engine_req_addr;
    logic [31:0] engine_req_wdata;
    logic [3:0] engine_req_rstrb;
    logic [3:0] engine_req_wstrb;
    logic engine_rsp_valid;
    logic [31:0] engine_rsp_rdata;
    logic [2:0] engine_rsp_error;
    logic result_valid;
    logic result_ready;
    logic [31:0] result_source_address;
    logic [31:0] result_output_address;
    logic [7:0] result_value;
    logic [2:0] result_error_code;

    logic backend_owner_pl;
    logic fault_inject_valid;
    logic [2:0] fault_inject_code;
    logic fault_on_write_mode;
    logic model_fault_valid;
    logic [2:0] model_fault_code;
    logic model_reset;
    logic model_ready;
    logic [31:0] model_rdata;
    logic [2:0] model_error;
    logic model_initialized;
    logic mem_valid;
    logic mem_write;
    logic [31:0] mem_addr;
    logic [31:0] mem_wdata;
    logic [3:0] mem_rstrb;
    logic [3:0] mem_wstrb;

    logic readback_mode;
    logic readback_req_valid;
    logic readback_req_ready;
    logic [31:0] readback_req_addr;
    logic [3:0] readback_req_rstrb;
    logic [31:0] master_req_addr;
    logic [31:0] master_req_wdata;
    logic [3:0] master_req_rstrb;
    logic [3:0] master_req_wstrb;
    logic master_req_valid;
    logic master_req_ready;
    logic master_req_write;
    logic master_rsp_valid;
    logic [31:0] master_rsp_rdata;
    logic [2:0] master_rsp_error;
    logic override_rsp_error_valid;
    logic [2:0] override_rsp_error_code;

    logic [31:0] expected_source_address;
    logic [31:0] expected_output_address;
    logic [7:0] expected_copy_value;
    logic [7:0] readback_expected_value;
    integer feature_read_transfers;
    integer write_feature_transfers;
    integer readback_checks;
    integer success_results;
    integer error_results;
    integer invalid_checks;
    integer raw_fault_checks;
    integer write_fault_checks;
    integer response_override_checks;
    integer abort_cancel_checks;
    integer reset_cancel_checks;
    integer ownership_checks;
    integer random_queries;
    integer directed_cases;
    integer directed_queries;
    integer vector_count;
    integer transaction_count;
    integer outstanding;
    integer accepted_backend_requests;
    integer backend_responses;
    integer memory_handshakes;
    integer memory_stall_cycles;
    integer previous_stall;
    logic held_memory_request;
    logic held_mem_write;
    logic [31:0] held_mem_addr;
    logic [31:0] held_mem_wdata;
    logic [3:0] held_mem_rstrb;
    logic [3:0] held_mem_wstrb;
    integer vector_fd;
    integer scan_result;
    integer vector_class;
    integer vector_case;
    integer vector_query;
    integer vector_channel;
    integer vector_y;
    integer vector_x;
    integer vector_source_y;
    integer vector_source_x;
    integer vector_expected_value;
    logic [31:0] vector_source_address;
    integer expected_source_offset;
    integer expected_output_offset;
    integer result_before;
    integer watchdog;
    integer case_loop;
    integer raw_error_case;
    logic [7:0] byte_value;

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

    function automatic logic [7:0] lane_value(input logic [31:0] word_value,
                                               input logic [1:0] lane);
        begin
            lane_value = word_value >> (lane * 8);
        end
    endfunction

    s2a_upsample_engine dut (
        .clk(clk),
        .hard_reset(hard_reset),
        .abort(abort),
        .start_valid(start_valid),
        .start_ready(start_ready),
        .input_base_address(input_base_address),
        .input_length_bytes(input_length_bytes),
        .output_base_address(output_base_address),
        .output_length_bytes(output_length_bytes),
        .input_channels(input_channels),
        .input_height(input_height),
        .input_width(input_width),
        .stride(stride),
        .output_channel(output_channel),
        .output_y(output_y),
        .output_x(output_x),
        .backend_cancel(backend_cancel),
        .backend_req_valid(engine_req_valid),
        .backend_req_ready(engine_req_ready),
        .backend_req_write(engine_req_write),
        .backend_req_addr(engine_req_addr),
        .backend_req_wdata(engine_req_wdata),
        .backend_req_rstrb(engine_req_rstrb),
        .backend_req_wstrb(engine_req_wstrb),
        .backend_rsp_valid(engine_rsp_valid),
        .backend_rsp_rdata(engine_rsp_rdata),
        .backend_rsp_error(engine_rsp_error),
        .result_valid(result_valid),
        .result_ready(result_ready),
        .result_source_address(result_source_address),
        .result_output_address(result_output_address),
        .result_value(result_value),
        .result_error_code(result_error_code)
    );

    always_comb begin
        master_req_valid = readback_mode ? readback_req_valid : engine_req_valid;
        master_req_write = readback_mode ? 1'b0 : engine_req_write;
        master_req_addr = readback_mode ? readback_req_addr : engine_req_addr;
        master_req_wdata = readback_mode ? 32'd0 : engine_req_wdata;
        master_req_rstrb = readback_mode ? readback_req_rstrb : engine_req_rstrb;
        master_req_wstrb = readback_mode ? 4'd0 : engine_req_wstrb;
        engine_req_ready = !readback_mode && master_req_ready;
        readback_req_ready = readback_mode && master_req_ready;
        engine_rsp_valid = !readback_mode && master_rsp_valid;
        engine_rsp_rdata = readback_mode ? 32'd0 : master_rsp_rdata;
        engine_rsp_error = override_rsp_error_valid ? override_rsp_error_code :
                           (readback_mode ? 3'd0 : master_rsp_error);
        model_fault_valid = fault_inject_valid ||
                            (fault_on_write_mode && mem_valid && mem_write);
        model_fault_code = (fault_on_write_mode && mem_valid && mem_write) ?
                           3'd6 : fault_inject_code;
        model_reset = hard_reset || abort;
    end

    s2a_memory_master u_memory_master (
        .clk(clk),
        .hard_reset(hard_reset),
        .cancel(backend_cancel),
        .buffer_owner_pl(backend_owner_pl),
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
        .mem_ready(model_ready),
        .mem_write(mem_write),
        .mem_addr(mem_addr),
        .mem_wdata(mem_wdata),
        .mem_rstrb(mem_rstrb),
        .mem_wstrb(mem_wstrb),
        .mem_rdata(model_rdata),
        .mem_error_code(model_error)
    );

    s2a_memory_model u_memory_model (
        .clk(clk),
        .reset(model_reset),
        .buffer_owner_pl(backend_owner_pl),
        .fault_inject_valid(model_fault_valid),
        .fault_inject_code(model_fault_code),
        .mem_valid(mem_valid),
        .mem_write(mem_write),
        .mem_addr(mem_addr),
        .mem_wdata(mem_wdata),
        .mem_rstrb(mem_rstrb),
        .mem_wstrb(mem_wstrb),
        .mem_ready(model_ready),
        .mem_rdata(model_rdata),
        .mem_error_code(model_error),
        .model_initialized(model_initialized)
    );

    always @(posedge clk) begin
        if (hard_reset || abort || !backend_owner_pl) begin
            outstanding = 0;
            held_memory_request = 1'b0;
        end else begin
            if (master_req_valid && master_req_ready) begin
                if (outstanding != 0) begin
                    $fatal(1, "FAIL: memory master 接受第二个 outstanding 请求");
                end
                outstanding = 1;
                accepted_backend_requests = accepted_backend_requests + 1;
            end
            if (master_rsp_valid) begin
                if (outstanding != 1) begin
                    $fatal(1, "FAIL: memory response 无对应的已接受请求");
                end
                outstanding = 0;
                backend_responses = backend_responses + 1;
            end

            if (held_memory_request) begin
                if (!mem_valid) begin
                    $fatal(1, "FAIL: 未握手 memory request 被提前撤销");
                end
                if ((mem_write !== held_mem_write) || (mem_addr !== held_mem_addr) ||
                    (mem_wdata !== held_mem_wdata) || (mem_rstrb !== held_mem_rstrb) ||
                    (mem_wstrb !== held_mem_wstrb)) begin
                    $fatal(1, "FAIL: memory stall 期间请求字段变化");
                end
            end

            if (mem_valid && !model_ready) begin
                held_memory_request = 1'b1;
                held_mem_write = mem_write;
                held_mem_addr = mem_addr;
                held_mem_wdata = mem_wdata;
                held_mem_rstrb = mem_rstrb;
                held_mem_wstrb = mem_wstrb;
                memory_stall_cycles = memory_stall_cycles + 1;
            end else if (mem_valid && model_ready) begin
                held_memory_request = 1'b0;
                memory_handshakes = memory_handshakes + 1;
                if (readback_mode) begin
                    if (mem_write || (mem_addr !== {expected_output_address[31:2], 2'b00}) ||
                        (mem_rstrb !== lane_mask(expected_output_address)) ||
                        (mem_wstrb !== 4'd0)) begin
                        $fatal(1, "FAIL: readback 地址或 byte lane 错误");
                    end
                end else if (mem_write) begin
                    if ((mem_addr !== {expected_output_address[31:2], 2'b00}) ||
                        (mem_rstrb !== 4'd0) ||
                        (mem_wstrb !== lane_mask(expected_output_address)) ||
                        (lane_value(mem_wdata, expected_output_address[1:0]) !==
                         expected_copy_value)) begin
                        $fatal(1, "FAIL: upsample output write 地址、strobe 或字节值错误");
                    end
                    write_feature_transfers = write_feature_transfers + 1;
                end else if ((mem_addr !== {expected_source_address[31:2], 2'b00}) ||
                             (mem_rstrb !== lane_mask(expected_source_address)) ||
                             (mem_wstrb !== 4'd0)) begin
                    $fatal(1, "FAIL: upsample source read 地址或 byte lane 错误");
                end

                if (!mem_write) begin
                    feature_read_transfers = feature_read_transfers + 1;
                end
            end else if (held_memory_request && !backend_cancel && backend_owner_pl) begin
                $fatal(1, "FAIL: held memory request 消失但未握手或取消");
            end
        end
    end

    task automatic set_defaults;
        begin
            input_base_address = 32'd27598336;
            input_length_bytes = 32'd21632;
            output_base_address = 32'd27619968;
            output_length_bytes = 32'd86528;
            input_channels = 32'd128;
            input_height = 32'd13;
            input_width = 32'd13;
            stride = 32'd2;
            output_channel = 32'd0;
            output_y = 32'd0;
            output_x = 32'd0;
        end
    endtask

    task automatic set_context(input logic [31:0] channel_value,
                               input logic [31:0] y_value,
                               input logic [31:0] x_value);
        integer source_offset;
        integer output_offset;
        begin
            output_channel = channel_value;
            output_y = y_value;
            output_x = x_value;
            source_offset = ((channel_value * 13) + (y_value / 2)) * 13 +
                            (x_value / 2);
            output_offset = ((channel_value * 26) + y_value) * 26 + x_value;
            expected_source_address = 32'd27598336 + source_offset;
            expected_output_address = 32'd27619968 + output_offset;
            expected_copy_value = initial_byte(expected_source_address);
        end
    endtask

    task automatic pulse_start;
        integer wait_count;
        begin
            @(negedge clk);
            start_valid = 1'b1;
            wait_count = 0;
            while (!start_ready) begin
                @(negedge clk);
                wait_count = wait_count + 1;
                if (wait_count > 20) begin
                    $fatal(1, "FAIL: upsample engine start_ready timeout");
                end
            end
            @(posedge clk);
            @(negedge clk);
            start_valid = 1'b0;
        end
    endtask

    task automatic wait_result(input logic [2:0] expected_error,
                               input logic [31:0] expected_source,
                               input logic [31:0] expected_output,
                               input logic [7:0] expected_value);
        integer wait_count;
        logic [31:0] stable_source;
        logic [31:0] stable_output;
        logic [7:0] stable_value;
        logic [2:0] stable_error;
        begin
            wait_count = 0;
            while (!result_valid) begin
                @(negedge clk);
                wait_count = wait_count + 1;
                if (wait_count > 200) begin
                    $fatal(1, "FAIL: upsample result 超时");
                end
            end
            if ((result_error_code !== expected_error) ||
                (result_source_address !== expected_source) ||
                (result_output_address !== expected_output) ||
                (result_value !== expected_value)) begin
                $fatal(1, "FAIL: result mismatch err=%0d src=%0d out=%0d value=%02h",
                       result_error_code, result_source_address,
                       result_output_address, result_value);
            end
            stable_source = result_source_address;
            stable_output = result_output_address;
            stable_value = result_value;
            stable_error = result_error_code;
            repeat (3) begin
                @(negedge clk);
                if (!result_valid || (result_source_address !== stable_source) ||
                    (result_output_address !== stable_output) ||
                    (result_value !== stable_value) ||
                    (result_error_code !== stable_error)) begin
                    $fatal(1, "FAIL: result fields 在 result_ready 前未保持稳定");
                end
            end
            result_ready = 1'b1;
            @(posedge clk);
            @(negedge clk);
            result_ready = 1'b0;
            if (result_valid) begin
                $fatal(1, "FAIL: result handshake 后重复报告 result");
            end
            if (expected_error == 0) begin
                success_results = success_results + 1;
            end else begin
                error_results = error_results + 1;
            end
        end
    endtask

    task automatic readback_byte(input logic [31:0] address,
                                 input logic [7:0] expected_value,
                                 input logic check_expected,
                                 output logic [7:0] observed_value);
        integer wait_count;
        logic [31:0] response_data;
        begin
            readback_expected_value = expected_value;
            @(negedge clk);
            readback_mode = 1'b1;
            readback_req_addr = {address[31:2], 2'b00};
            readback_req_rstrb = lane_mask(address);
            readback_req_valid = 1'b1;
            #1;
            wait_count = 0;
            while (!readback_req_ready) begin
                @(negedge clk);
                #1;
                wait_count = wait_count + 1;
                if (wait_count > 20) begin
                    $fatal(1, "FAIL: readback backend request timeout");
                end
            end
            @(posedge clk);
            @(negedge clk);
            readback_req_valid = 1'b0;
            wait_count = 0;
            while (!master_rsp_valid) begin
                @(negedge clk);
                wait_count = wait_count + 1;
                if (wait_count > 40) begin
                    $fatal(1, "FAIL: readback memory response timeout");
                end
            end
            response_data = master_rsp_rdata;
            if ((master_rsp_error != 3'd0) ||
                (check_expected &&
                (lane_value(response_data, address[1:0]) !== readback_expected_value))) begin
                $fatal(1, "FAIL: output readback mismatch address=%0d data=%08h expected=%02h error=%0d",
                       address, response_data, readback_expected_value, master_rsp_error);
            end
            observed_value = lane_value(response_data, address[1:0]);
            @(negedge clk);
            readback_mode = 1'b0;
            readback_req_addr = 32'd0;
            readback_req_rstrb = 4'd0;
            readback_checks = readback_checks + 1;
        end
    endtask

    task automatic run_success(input logic [31:0] channel_value,
                               input logic [31:0] y_value,
                               input logic [31:0] x_value);
        logic [7:0] readback_value;
        begin
            set_context(channel_value, y_value, x_value);
            pulse_start();
            wait_result(3'd0, expected_source_address, expected_output_address,
                        expected_copy_value);
            readback_byte(expected_output_address, expected_copy_value, 1'b1,
                          readback_value);
            if (readback_value !== expected_copy_value) begin
                $fatal(1, "FAIL: output tensor byte 与输入源字节不一致");
            end
            transaction_count = transaction_count + 1;
        end
    endtask

    task automatic run_invalid(input logic [2:0] expected_error);
        integer before_transfers;
        begin
            expected_source_address = 32'd0;
            expected_output_address = 32'd0;
            expected_copy_value = 8'd0;
            before_transfers = memory_handshakes;
            pulse_start();
            wait_result(expected_error, 32'd0, 32'd0, 8'd0);
            if (memory_handshakes != before_transfers) begin
                $fatal(1, "FAIL: invalid arguments/range caused memory side effect");
            end
            invalid_checks = invalid_checks + 1;
            set_defaults();
        end
    endtask

    task automatic run_memory_fault(input logic [2:0] injected_code);
        logic [7:0] prior_value;
        integer writes_before;
        begin
            set_context(32'd127, 32'd25, 32'd25);
            readback_byte(expected_output_address, 8'd0, 1'b0, prior_value);
            fault_inject_valid = 1'b1;
            fault_inject_code = injected_code;
            writes_before = write_feature_transfers;
            pulse_start();
            wait_result(3'd6, expected_source_address, expected_output_address, 8'd0);
            fault_inject_valid = 1'b0;
            fault_inject_code = 3'd0;
            if (write_feature_transfers != writes_before) begin
                $fatal(1, "FAIL: read error 后仍发出 output write");
            end
            readback_byte(expected_output_address, 8'd0, 1'b0, byte_value);
            if (byte_value !== prior_value) begin
                $fatal(1, "FAIL: read error 后 output byte 被修改");
            end
            raw_fault_checks = raw_fault_checks + 1;
        end
    endtask

    task automatic run_response_override(input logic [2:0] injected_code,
                                         input logic [2:0] expected_error);
        logic [7:0] prior_value;
        integer writes_before;
        begin
            set_context(32'd126, 32'd24, 32'd24);
            readback_byte(expected_output_address, 8'd0, 1'b0, prior_value);
            override_rsp_error_valid = 1'b1;
            override_rsp_error_code = injected_code;
            writes_before = write_feature_transfers;
            pulse_start();
            wait_result(expected_error, expected_source_address,
                        expected_output_address, 8'd0);
            override_rsp_error_valid = 1'b0;
            override_rsp_error_code = 3'd0;
            if (write_feature_transfers != writes_before) begin
                $fatal(1, "FAIL: backend read error 后仍发出 output write");
            end
            readback_byte(expected_output_address, 8'd0, 1'b0, byte_value);
            if (byte_value !== prior_value) begin
                $fatal(1, "FAIL: backend read error 后 output byte 被修改");
            end
            response_override_checks = response_override_checks + 1;
        end
    endtask

    task automatic run_memory_write_fault;
        logic [7:0] prior_value;
        integer writes_before;
        begin
            set_context(32'd125, 32'd23, 32'd23);
            readback_byte(expected_output_address, 8'd0, 1'b0, prior_value);
            writes_before = write_feature_transfers;
            fault_on_write_mode = 1'b1;
            pulse_start();
            wait_result(3'd6, expected_source_address, expected_output_address, 8'd0);
            fault_on_write_mode = 1'b0;
            if (write_feature_transfers != writes_before + 1) begin
                $fatal(1, "FAIL: injected write error 未恰好接受一笔 write request");
            end
            readback_byte(expected_output_address, 8'd0, 1'b0, byte_value);
            if (byte_value !== prior_value) begin
                $fatal(1, "FAIL: memory write error 后 output byte 被修改");
            end
            write_fault_checks = write_fault_checks + 1;
        end
    endtask

    task automatic wait_first_stalled_request(input logic expected_write);
        integer wait_count;
        begin
            wait_count = 0;
            while (!(mem_valid && !model_ready)) begin
                @(negedge clk);
                wait_count = wait_count + 1;
                if (wait_count > 80) begin
                    $fatal(1, "FAIL: 未遇到预期的 pending stall request");
                end
            end
            if (mem_write !== expected_write) begin
                $fatal(1, "FAIL: pending request 方向错误");
            end
            @(posedge clk);
            @(negedge clk);
            if (!mem_valid || model_ready || !held_memory_request ||
                !u_memory_model.pending || (u_memory_model.stall_remaining != 6) ||
                (u_memory_model.stall_index[expected_write ? 3 : 2] != 3)) begin
                $fatal(1, "FAIL: T10 未锁存 pending stall request write=%0d valid=%0d ready=%0d held=%0d state=%0d master_pending=%0d model_pending=%0d remaining=%0d read_slot=%0d write_slot=%0d",
                       expected_write, mem_valid, model_ready, held_memory_request,
                       dut.state, u_memory_master.pending, u_memory_model.pending,
                       u_memory_model.stall_remaining, u_memory_model.stall_index[2],
                       u_memory_model.stall_index[3]);
            end
        end
    endtask

    task automatic cancel_pending(input logic expected_write,
                                 input logic use_hard_reset);
        integer before_writes;
        integer align_count;
        logic [7:0] prior_value;
        begin
            set_context(32'd127, 32'd25, 32'd24);
            readback_byte(expected_output_address, 8'd0, 1'b0, prior_value);
            if (expected_write) begin
                align_count = 0;
                while (u_memory_model.stall_index[3] != 3) begin
                    run_success(32'd125, 32'd22, align_count[4:0]);
                    align_count = align_count + 1;
                    if (align_count > 5) begin
                        $fatal(1, "FAIL: 无法把 T10 write_feature stall 游标对齐到 slot 7");
                    end
                end
            end else begin
                while (u_memory_model.stall_index[2] != 3) begin
                    readback_byte(expected_output_address, 8'd0, 1'b0, byte_value);
                end
            end
            if (expected_write) begin
                if (u_memory_model.stall_index[3] != 3) begin
                    $fatal(1, "FAIL: pending write case 未对齐 T10 stall slot 7");
                end
            end else if (u_memory_model.stall_index[2] != 3) begin
                $fatal(1, "FAIL: pending read case 未对齐 T10 stall slot 7");
            end
            before_writes = write_feature_transfers;
            pulse_start();
            if (expected_write) begin
                watchdog = 0;
                while (!mem_valid || !mem_write) begin
                    @(negedge clk);
                    watchdog = watchdog + 1;
                    if (watchdog > 80) begin
                        $fatal(1, "FAIL: upsample 未到达 output pending write");
                    end
                end
            end
            wait_first_stalled_request(expected_write);
            if (use_hard_reset) begin
                hard_reset = 1'b1;
            end else begin
                abort = 1'b1;
            end
            #1;
            if (mem_valid || master_rsp_valid || engine_rsp_valid) begin
                $fatal(1, "FAIL: reset/abort 未在 ready 握手前撤銷请求和响应");
            end
            @(posedge clk);
            @(negedge clk);
            hard_reset = 1'b0;
            abort = 1'b0;
            #1;
            if (result_valid || !start_ready || master_rsp_valid || mem_valid) begin
                $fatal(1, "FAIL: reset/abort 后出现结果/迟到响应或未回到 idle hard=%0d abort=%0d result=%0d start_ready=%0d rsp=%0d mem_valid=%0d state=%0d master_pending=%0d model_pending=%0d",
                       hard_reset, abort, result_valid, start_ready,
                       master_rsp_valid, mem_valid, dut.state,
                       u_memory_master.pending, u_memory_model.pending);
            end
            if (write_feature_transfers != before_writes) begin
                $fatal(1, "FAIL: cancelled pending transaction 产生写副作用");
            end
            readback_byte(expected_output_address, 8'd0, 1'b0, byte_value);
            if (byte_value !== prior_value) begin
                $fatal(1, "FAIL: cancelled pending write 修改了 output byte");
            end
            if (use_hard_reset) begin
                reset_cancel_checks = reset_cancel_checks + 1;
            end else begin
                abort_cancel_checks = abort_cancel_checks + 1;
            end
        end
    endtask

    task automatic run_owner_gate;
        begin
            backend_owner_pl = 1'b0;
            set_context(32'd4, 32'd2, 32'd2);
            pulse_start();
            repeat (4) begin
                @(negedge clk);
                if (mem_valid || master_req_ready || engine_req_ready) begin
                    $fatal(1, "FAIL: PS ownership 时 memory request 未被 master 阻止");
                end
            end
            abort = 1'b1;
            #1;
            if (mem_valid || master_rsp_valid) begin
                $fatal(1, "FAIL: ownership wait abort 未撤销请求");
            end
            @(posedge clk);
            @(negedge clk);
            abort = 1'b0;
            backend_owner_pl = 1'b1;
            ownership_checks = ownership_checks + 1;
        end
    endtask

    initial begin : run_tests
        logic [7:0] readback_value;
        integer before_transfers;
        integer query_index;

        hard_reset = 1'b1;
        abort = 1'b0;
        start_valid = 1'b0;
        result_ready = 1'b0;
        backend_owner_pl = 1'b1;
        fault_inject_valid = 1'b0;
        fault_inject_code = 3'd0;
        fault_on_write_mode = 1'b0;
        readback_mode = 1'b0;
        readback_req_valid = 1'b0;
        readback_req_addr = 32'd0;
        readback_req_rstrb = 4'd0;
        override_rsp_error_valid = 1'b0;
        override_rsp_error_code = 3'd0;
        feature_read_transfers = 0;
        write_feature_transfers = 0;
        readback_checks = 0;
        success_results = 0;
        error_results = 0;
        invalid_checks = 0;
        raw_fault_checks = 0;
        response_override_checks = 0;
        write_fault_checks = 0;
        abort_cancel_checks = 0;
        reset_cancel_checks = 0;
        ownership_checks = 0;
        random_queries = 0;
        directed_cases = 0;
        directed_queries = 0;
        vector_count = 0;
        transaction_count = 0;
        outstanding = 0;
        accepted_backend_requests = 0;
        backend_responses = 0;
        memory_handshakes = 0;
        memory_stall_cycles = 0;
        held_memory_request = 1'b0;
        expected_source_address = 32'd0;
        expected_output_address = 32'd0;
        expected_copy_value = 8'd0;
        readback_expected_value = 8'd0;
        set_defaults();

        wait (model_initialized);
        repeat (3) @(posedge clk);
        @(negedge clk);
        hard_reset = 1'b0;

        input_channels = 32'd0;
        run_invalid(3'd1);
        input_height = 32'd12;
        run_invalid(3'd1);
        stride = 32'd1;
        run_invalid(3'd1);
        output_channel = 32'd128;
        run_invalid(3'd1);
        output_y = 32'd26;
        run_invalid(3'd1);
        output_x = 32'd26;
        run_invalid(3'd1);
        input_base_address = 32'd27598340;
        run_invalid(3'd2);
        output_base_address = 32'd27619972;
        run_invalid(3'd2);
        input_length_bytes = 32'd21631;
        run_invalid(3'd3);
        output_length_bytes = 32'd86527;
        run_invalid(3'd3);

        vector_fd = $fopen("engine_vectors.dat", "r");
        if (vector_fd == 0) begin
            $fatal(1, "FAIL: 无法打开 G0 layer33 engine_vectors.dat");
        end
        scan_result = $fscanf(vector_fd, "%d %d %d %d %d %d %h %d %d %d\n",
            vector_class, vector_case, vector_query, vector_channel,
            vector_y, vector_x, vector_source_address, vector_expected_value,
            vector_source_y, vector_source_x);
        while (scan_result == 10) begin
            if ((vector_class != 0) && (vector_class != 1)) begin
                $fatal(1, "FAIL: engine vector 类别不是模型随机/定向向量");
            end
            expected_source_offset =
                ((vector_channel * 13) + vector_source_y) * 13 + vector_source_x;
            expected_output_offset =
                ((vector_channel * 26) + vector_y) * 26 + vector_x;
            if ((vector_source_y != (vector_y / 2)) ||
                (vector_source_x != (vector_x / 2)) ||
                (vector_source_address !== (32'd27598336 + expected_source_offset))) begin
                $fatal(1, "FAIL: official query vector 的 layer32 source mapping 不一致");
            end
            if (vector_class == 0) begin
                random_queries = random_queries + 1;
                if (vector_case != random_queries - 1) begin
                    $fatal(1, "FAIL: official random case 顺序变化");
                end
            end else if (vector_case + 1 > directed_cases) begin
                directed_cases = vector_case + 1;
            end
            set_context(vector_channel, vector_y, vector_x);
            if (expected_source_address !== vector_source_address) begin
                $fatal(1, "FAIL: task address mapping 与 G0 vector 不匹配");
            end
            pulse_start();
            wait_result(3'd0, expected_source_address, expected_output_address,
                        expected_copy_value);
            readback_byte(expected_output_address, expected_copy_value, 1'b1,
                          readback_value);
            if (readback_value !== expected_copy_value) begin
                $fatal(1, "FAIL: copied output byte 与 T10 input byte 不匹配");
            end
            if (vector_class == 1) begin
                directed_queries = directed_queries + 1;
                if (vector_expected_value < -127 || vector_expected_value > 127) begin
                    $fatal(1, "FAIL: G0 directed source_value 超出 INT8 对称范围");
                end
            end
            vector_count = vector_count + 1;
            transaction_count = transaction_count + 1;
            scan_result = $fscanf(vector_fd,
                "%d %d %d %d %d %d %h %d %d %d\n",
                vector_class, vector_case, vector_query, vector_channel,
                vector_y, vector_x, vector_source_address, vector_expected_value,
                vector_source_y, vector_source_x);
        end
        if (scan_result != -1) begin
            $fatal(1, "FAIL: engine_vectors.dat 有不完整记录");
        end
        $fclose(vector_fd);
        if ((vector_count != 1018) || (random_queries != 1000) ||
            (directed_cases != 16) || (directed_queries != 18)) begin
            $fatal(1, "FAIL: G0 upsample coordinates count mismatch");
        end

        cancel_pending(1'b0, 1'b0);
        cancel_pending(1'b0, 1'b1);
        run_success(32'd127, 32'd25, 32'd24);
        for (case_loop = 0; case_loop < 4; case_loop = case_loop + 1) begin
            run_success(32'd127, 32'd24, case_loop[4:0]);
        end
        cancel_pending(1'b1, 1'b0);
        cancel_pending(1'b1, 1'b1);
        run_success(32'd127, 32'd25, 32'd24);

        run_owner_gate();
        run_success(32'd4, 32'd2, 32'd2);

        run_memory_fault(3'd6);
        run_memory_fault(3'd7);
        run_response_override(3'd1, 3'd1);
        run_response_override(3'd2, 3'd2);
        run_memory_write_fault();

        if (outstanding != 0 || accepted_backend_requests != backend_responses +
            abort_cancel_checks + reset_cancel_checks) begin
            $fatal(1, "FAIL: backend accepted/response/cancel accounting mismatch");
        end
        if ((transaction_count != 1025) || (readback_checks != 1047) ||
            (invalid_checks != 10) || (raw_fault_checks != 2) ||
            (response_override_checks != 2) || (write_fault_checks != 1) ||
            (abort_cancel_checks != 2) || (reset_cancel_checks != 2) ||
            (ownership_checks != 1) || (success_results != transaction_count) ||
            (error_results != 15)) begin
            $display("counts tx=%0d readback=%0d invalid=%0d raw=%0d override=%0d writefault=%0d abort=%0d reset=%0d owner=%0d success=%0d error=%0d accepted=%0d responses=%0d handshakes=%0d stalls=%0d",
                transaction_count, readback_checks, invalid_checks,
                raw_fault_checks, response_override_checks, write_fault_checks,
                abort_cancel_checks, reset_cancel_checks, ownership_checks, success_results,
                error_results, accepted_backend_requests, backend_responses,
                memory_handshakes, memory_stall_cycles);
            $fatal(1, "FAIL: test coverage totals mismatch");
        end

        $display("RESULT model_random=%0d directed_cases=%0d directed_queries=%0d memory_path_queries=%0d success=%0d errors=%0d readback=%0d invalid=%0d raw_fault=%0d response_override=%0d write_fault=%0d abort_cancel=%0d reset_cancel=%0d ownership=%0d accepted=%0d responses=%0d memory_handshakes=%0d stall_cycles=%0d",
            random_queries, directed_cases, directed_queries, vector_count,
            success_results, error_results, readback_checks, invalid_checks,
            raw_fault_checks, response_override_checks, write_fault_checks,
            abort_cancel_checks, reset_cancel_checks, ownership_checks, accepted_backend_requests,
            backend_responses, memory_handshakes, memory_stall_cycles);
        $display("PASS S2A-T13 upsample memory datapath");
        $finish;
    end
endmodule
