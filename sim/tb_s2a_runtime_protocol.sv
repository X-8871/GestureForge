// S2A-T12：端到端验证 CSR、单笔 memory master 与 T10 行为模型。
module tb_s2a_runtime_protocol;
    logic clk;
    logic hard_reset;
    logic csr_valid;
    logic csr_ready;
    logic csr_write;
    logic [7:0] csr_addr;
    logic [31:0] csr_wdata;
    logic [31:0] csr_rdata;
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
    logic operator_result_valid;
    logic [2:0] operator_error_code;
    logic backend_start;
    logic backend_abort;
    logic busy;
    logic done;
    logic error;
    logic pl_owns_buffers;
    logic head_output_valid;
    logic mem_valid;
    logic mem_ready;
    logic mem_write;
    logic [31:0] mem_addr;
    logic [31:0] mem_wdata;
    logic [3:0] mem_rstrb;
    logic [3:0] mem_wstrb;
    logic [31:0] mem_rdata;
    logic [2:0] mem_error_code;
    logic fault_inject_valid;
    logic [2:0] fault_inject_code;
    logic model_initialized;
    logic model_reset;
    integer stall_index [0:3];
    integer stall_schedule [0:4];
    integer transfer_counts [0:3];
    integer error_checks;
    integer cancel_checks;
    integer retry_checks;
    integer vector_fd;
    integer scan_count;
    integer row_index;
    integer class_id;
    integer strobe_value;
    integer expected_stall;
    logic [31:0] vector_addr;
    logic [31:0] vector_data;
    logic [31:0] vector_expected;
    logic [31:0] feature_test_addr [0:3];
    integer parameter_fd;
    integer low_cycles;
    integer guard_cycles;
    logic monitor_active;
    logic [31:0] monitor_addr;
    logic [31:0] monitor_wdata;
    logic [3:0] monitor_rstrb;
    logic [3:0] monitor_wstrb;
    logic monitor_write;
    logic [31:0] random_word;

    s2a_runtime_shell u_shell (
        .clk(clk), .hard_reset(hard_reset),
        .csr_valid(csr_valid), .csr_ready(csr_ready), .csr_write(csr_write),
        .csr_addr(csr_addr), .csr_wdata(csr_wdata), .csr_rdata(csr_rdata),
        .backend_req_valid(backend_req_valid), .backend_req_ready(backend_req_ready),
        .backend_req_write(backend_req_write), .backend_req_addr(backend_req_addr),
        .backend_req_wdata(backend_req_wdata),
        .backend_req_rstrb(backend_req_rstrb), .backend_req_wstrb(backend_req_wstrb),
        .backend_rsp_valid(backend_rsp_valid), .backend_rsp_rdata(backend_rsp_rdata),
        .backend_rsp_error(backend_rsp_error),
        .operator_result_valid(operator_result_valid),
        .operator_error_code(operator_error_code),
        .backend_start(backend_start), .backend_abort(backend_abort),
        .busy(busy), .done(done), .error(error), .pl_owns_buffers(pl_owns_buffers),
        .head_output_valid(head_output_valid),
        .mem_valid(mem_valid), .mem_ready(mem_ready), .mem_write(mem_write),
        .mem_addr(mem_addr), .mem_wdata(mem_wdata), .mem_rstrb(mem_rstrb),
        .mem_wstrb(mem_wstrb), .mem_rdata(mem_rdata),
        .mem_error_code(mem_error_code)
    );

    assign model_reset = hard_reset ||
        (csr_valid && csr_ready && csr_write && (csr_addr == 8'h00) && csr_wdata[1]);

    s2a_memory_model u_memory (
        .clk(clk), .reset(model_reset), .buffer_owner_pl(pl_owns_buffers),
        .fault_inject_valid(fault_inject_valid), .fault_inject_code(fault_inject_code),
        .mem_valid(mem_valid), .mem_write(mem_write), .mem_addr(mem_addr),
        .mem_wdata(mem_wdata), .mem_rstrb(mem_rstrb), .mem_wstrb(mem_wstrb),
        .mem_ready(mem_ready), .mem_rdata(mem_rdata),
        .mem_error_code(mem_error_code), .model_initialized(model_initialized)
    );

    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end

    always @(posedge clk) begin
        if (mem_valid && !mem_ready) begin
            if (monitor_active &&
                ((mem_addr != monitor_addr) || (mem_wdata != monitor_wdata) ||
                 (mem_rstrb != monitor_rstrb) || (mem_wstrb != monitor_wstrb) ||
                 (mem_write != monitor_write))) begin
                $fatal(1, "FAIL: stall 期间 master memory 字段发生变化");
            end
            monitor_addr = mem_addr;
            monitor_wdata = mem_wdata;
            monitor_rstrb = mem_rstrb;
            monitor_wstrb = mem_wstrb;
            monitor_write = mem_write;
            monitor_active = 1'b1;
            if (backend_req_ready) begin
                $fatal(1, "FAIL: outstanding 请求期间错误接受第二笔请求");
            end
        end else begin
            monitor_active = 1'b0;
        end
    end

    function automatic logic [7:0] initial_byte(input logic [31:0] address);
        begin
            initial_byte = address[7:0] ^ address[15:8] ^
                           address[23:16] ^ address[31:24] ^ 8'hA5;
        end
    endfunction

    function automatic logic [31:0] initial_word(input logic [31:0] address);
        integer lane;
        begin
            initial_word = 32'd0;
            for (lane = 0; lane < 4; lane = lane + 1) begin
                initial_word[lane*8 +: 8] = initial_byte(address + lane);
            end
        end
    endfunction

    task automatic csr_write_word(input logic [7:0] address,
                                  input logic [31:0] value);
        begin
            @(negedge clk);
            csr_valid = 1'b1;
            csr_write = 1'b1;
            csr_addr = address;
            csr_wdata = value;
            @(posedge clk);
            if (!csr_ready) begin
                $fatal(1, "FAIL: CSR write 未 ready");
            end
            @(negedge clk);
            csr_valid = 1'b0;
            csr_write = 1'b0;
            csr_addr = 8'd0;
            csr_wdata = 32'd0;
        end
    endtask

    task automatic csr_check(input logic [7:0] address,
                             input logic [31:0] expected_value);
        begin
            @(negedge clk);
            csr_valid = 1'b1;
            csr_write = 1'b0;
            csr_addr = address;
            csr_wdata = 32'd0;
            #1;
            if (csr_rdata !== expected_value) begin
                $fatal(1, "FAIL: CSR 读值地址=%02h 实际=%08h 期望=%08h",
                       address, csr_rdata, expected_value);
            end
            @(posedge clk);
            @(negedge clk);
            csr_valid = 1'b0;
            csr_addr = 8'd0;
        end
    endtask

    task automatic start_job(input integer timeout_value);
        begin
            if (busy || done || error || pl_owns_buffers) begin
                $fatal(1, "FAIL: start 前控制状态不为空闲");
            end
            csr_write_word(8'h28, timeout_value);
            csr_write_word(8'h00, 32'h0000_0001);
            if (!backend_start || !busy || !pl_owns_buffers || head_output_valid) begin
                $fatal(1, "FAIL: 合法 start 未取得 PL ownership");
            end
        end
    endtask

    task automatic finish_success;
        begin
            if (!busy || done || head_output_valid || !pl_owns_buffers) begin
                $fatal(1, "FAIL: operator 成功前状态不符合 busy 语义");
            end
            @(negedge clk);
            operator_result_valid = 1'b1;
            operator_error_code = 3'd0;
            @(posedge clk);
            @(negedge clk);
            operator_result_valid = 1'b0;
            if (busy || !done || error || pl_owns_buffers || !head_output_valid) begin
                $fatal(1, "FAIL: code0 operator completion 未置 done/head_valid");
            end
            csr_check(8'h04, 32'h0000_0002);
        end
    endtask

    task automatic transact(input integer request_class,
                            input logic write_request,
                            input logic [31:0] address,
                            input logic [31:0] write_data,
                            input logic [3:0] read_strobe,
                            input logic [3:0] write_strobe,
                            input logic [31:0] expected_data,
                            input logic [2:0] expected_error,
                            input integer expected_low_cycles);
        integer low_count;
        integer watchdog;
        logic response_seen;
        begin
            if (request_class < 0 || request_class > 3 ||
                expected_low_cycles != stall_schedule[stall_index[request_class]]) begin
                $fatal(1, "FAIL: 测试端 stall schedule 与 memory model 状态不一致");
            end
            backend_req_valid = 1'b1;
            backend_req_write = write_request;
            backend_req_addr = address;
            backend_req_wdata = write_data;
            backend_req_rstrb = read_strobe;
            backend_req_wstrb = write_strobe;
            watchdog = 0;
            while (1) begin
                @(posedge clk);
                watchdog = watchdog + 1;
                if (watchdog > 20) begin
                    $fatal(1, "FAIL: backend request 长时间未被接受");
                end
                if (backend_req_ready) begin
                    break;
                end
            end
            @(negedge clk);
            backend_req_valid = 1'b0;
            low_count = 0;
            watchdog = 0;
            response_seen = 1'b0;
            while (!response_seen) begin
                @(posedge clk);
                watchdog = watchdog + 1;
                if (watchdog > 30) begin
                    $fatal(1, "FAIL: memory master response 超时");
                end
                if (mem_valid) begin
                    if (!mem_ready) begin
                        low_count = low_count + 1;
                    end else begin
                        if (!backend_rsp_valid) begin
                            $fatal(1, "FAIL: mem handshake 未形成 backend response");
                        end
                        if (backend_rsp_error !== expected_error) begin
                            $fatal(1, "FAIL: memory error=%0d expected=%0d",
                                   backend_rsp_error, expected_error);
                        end
                        if ((expected_error == 0) && !write_request &&
                            (backend_rsp_rdata !== expected_data)) begin
                            $fatal(1, "FAIL: read data=%08h expected=%08h",
                                   backend_rsp_rdata, expected_data);
                        end
                        if ((expected_error == 0) && write_request &&
                            (backend_rsp_rdata !== 32'd0)) begin
                            $fatal(1, "FAIL: write response 未将无效读数据清零");
                        end
                        response_seen = 1'b1;
                    end
                end
            end
            if (low_count != expected_low_cycles) begin
                $fatal(1, "FAIL: ready-low cycles=%0d expected=%0d",
                       low_count, expected_low_cycles);
            end
            stall_index[request_class] = (stall_index[request_class] + 1) % 5;
            if (expected_error == 0) begin
                transfer_counts[request_class] = transfer_counts[request_class] + 1;
            end
            @(negedge clk);
        end
    endtask

    task automatic launch_write(input logic [31:0] address,
                                input logic [31:0] value);
        integer watchdog;
        begin
            backend_req_valid = 1'b1;
            backend_req_write = 1'b1;
            backend_req_addr = address;
            backend_req_wdata = value;
            backend_req_rstrb = 4'd0;
            backend_req_wstrb = 4'hF;
            watchdog = 0;
            while (1) begin
                @(posedge clk);
                watchdog = watchdog + 1;
                if (watchdog > 20) begin
                    $fatal(1, "FAIL: pending write backend request 未被接受");
                end
                if (backend_req_ready) begin
                    break;
                end
            end
            @(negedge clk);
            backend_req_valid = 1'b0;
        end
    endtask

    task automatic wait_seven_stall_cycles;
        integer cycles;
        integer watchdog;
        begin
            cycles = 0;
            watchdog = 0;
            while (cycles < 7) begin
                @(posedge clk);
                watchdog = watchdog + 1;
                if (watchdog > 20 || !mem_valid) begin
                    $fatal(1, "FAIL: pending write 未持续有效到七周期 stall");
                end
                if (mem_ready) begin
                    $fatal(1, "FAIL: G0 stall slot 7 提前 ready");
                end
                cycles = cycles + 1;
            end
            @(negedge clk);
            // ready 此时可在下个上升沿前升高；取消 task 必须在该沿前门控请求。
        end
    endtask

    task automatic cancel_with_hard_reset(input logic [31:0] address,
                                          input logic [31:0] value);
        begin
            if (stall_index[3] != 3) begin
                $fatal(1, "FAIL: hard reset cancel 未位于 stall slot 7");
            end
            launch_write(address, value);
            wait_seven_stall_cycles();
            hard_reset = 1'b1;
            #1;
            if (mem_valid || mem_ready || backend_rsp_valid) begin
                $fatal(1, "FAIL: hard reset 未在 ready 边沿前撤销 memory request");
            end
            @(posedge clk);
            @(negedge clk);
            hard_reset = 1'b0;
            if (busy || done || error || pl_owns_buffers || backend_rsp_valid) begin
                $fatal(1, "FAIL: hard reset cancel 状态/响应不正确");
            end
            cancel_checks = cancel_checks + 1;
        end
    endtask

    task automatic cancel_with_soft_reset(input logic [31:0] address,
                                          input logic [31:0] value);
        begin
            if (stall_index[3] != 3) begin
                $fatal(1, "FAIL: soft reset cancel 未位于 stall slot 7");
            end
            launch_write(address, value);
            wait_seven_stall_cycles();
            csr_valid = 1'b1;
            csr_write = 1'b1;
            csr_addr = 8'h00;
            csr_wdata = 32'h0000_0002;
            #1;
            if (!csr_ready || mem_valid || mem_ready || backend_rsp_valid) begin
                $fatal(1, "FAIL: accepted soft_reset 未在 ready 边沿前取消 memory request");
            end
            @(posedge clk);
            @(negedge clk);
            csr_valid = 1'b0;
            csr_write = 1'b0;
            csr_addr = 8'd0;
            csr_wdata = 32'd0;
            if (busy || done || error || pl_owns_buffers || backend_rsp_valid) begin
                $fatal(1, "FAIL: soft_reset cancel 状态/响应不正确");
            end
            cancel_checks = cancel_checks + 1;
        end
    endtask

    task automatic cancel_with_timeout(input logic [31:0] address,
                                       input logic [31:0] value);
        integer cycles;
        integer watchdog;
        begin
            if (stall_index[3] != 3) begin
                $fatal(1, "FAIL: timeout cancel 未位于 stall slot 7");
            end
            launch_write(address, value);
            cycles = 0;
            watchdog = 0;
            while (cycles < 7) begin
                @(posedge clk);
                watchdog = watchdog + 1;
                if (watchdog > 20 || !mem_valid) begin
                    $fatal(1, "FAIL: timeout pending write 未保持七周期");
                end
                if (mem_ready) begin
                    $fatal(1, "FAIL: timeout pending write 在第七个低周期前 ready");
                end
                cycles = cycles + 1;
            end
            @(negedge clk);
            if (busy || !error || done || head_output_valid ||
                pl_owns_buffers || mem_valid || mem_ready || backend_rsp_valid) begin
                $fatal(1, "FAIL: timeout 未取消 pending write 或产生迟到响应");
            end
            csr_check(8'h08, 32'd5);
            cancel_checks = cancel_checks + 1;
        end
    endtask

    task automatic check_cancel_readback(input logic [31:0] address);
        begin
            transact(2, 1'b0, address, 32'd0, 4'hF, 4'd0,
                     initial_word(address), 3'd0,
                     stall_schedule[stall_index[2]]);
        end
    endtask

    task automatic rotate_write_pointer_to_three;
        integer rotate_count;
        begin
            for (rotate_count = 0; rotate_count < 4; rotate_count = rotate_count + 1) begin
                transact(3, 1'b1,
                         feature_test_addr[0] + 32'd128 + rotate_count*4,
                         32'hA500_0000 | rotate_count, 4'd0, 4'hF,
                         32'd0, 3'd0, stall_schedule[stall_index[3]]);
            end
            if (stall_index[3] != 3) begin
                $fatal(1, "FAIL: feature write stall pointer 未回到 slot 7");
            end
        end
    endtask

    initial begin : run_integration
        integer range_index;
        integer response_value;
        integer input_index;
        logic [31:0] expected_data;
        logic [2:0] injected_code;

        hard_reset = 1'b1;
        csr_valid = 1'b0;
        csr_write = 1'b0;
        csr_addr = 8'd0;
        csr_wdata = 32'd0;
        backend_req_valid = 1'b0;
        backend_req_write = 1'b0;
        backend_req_addr = 32'd0;
        backend_req_wdata = 32'd0;
        backend_req_rstrb = 4'd0;
        backend_req_wstrb = 4'd0;
        operator_result_valid = 1'b0;
        operator_error_code = 3'd0;
        fault_inject_valid = 1'b0;
        fault_inject_code = 3'd0;
        monitor_active = 1'b0;
        cancel_checks = 0;
        retry_checks = 0;
        error_checks = 0;
        for (range_index = 0; range_index < 4; range_index = range_index + 1) begin
            stall_index[range_index] = 0;
            transfer_counts[range_index] = 0;
        end
        stall_schedule[0] = 0;
        stall_schedule[1] = 1;
        stall_schedule[2] = 2;
        stall_schedule[3] = 7;
        stall_schedule[4] = 3;
        repeat (3) @(posedge clk);
        @(negedge clk);
        hard_reset = 1'b0;
        wait (model_initialized);
        if (backend_req_ready || mem_valid || busy || pl_owns_buffers) begin
            $fatal(1, "FAIL: idle/PS-owned 时 master ready 或 mem_valid 不为零");
        end

        parameter_fd = $fopen("runtime_params.dat", "r");
        if (parameter_fd == 0) begin
            $fatal(1, "无法打开 manifest 派生的 runtime_params.dat");
        end
        for (range_index = 0; range_index < 4; range_index = range_index + 1) begin
            scan_count = $fscanf(parameter_fd, "%h\n", feature_test_addr[range_index]);
            if (scan_count != 1 || feature_test_addr[range_index][1:0] != 2'b00) begin
                $fatal(1, "FAIL: feature test address 参数非法");
            end
        end
        $fclose(parameter_fd);

        start_job(1000000);
        vector_fd = $fopen("vectors.dat", "r");
        if (vector_fd == 0) begin
            $fatal(1, "无法打开 T12 runtime transfer vectors.dat");
        end
        for (row_index = 0; row_index < 4000; row_index = row_index + 1) begin
            scan_count = $fscanf(vector_fd, "%d %h %h %h %h %d\n",
                                 class_id, vector_addr, vector_data,
                                 strobe_value, vector_expected, expected_stall);
            if (scan_count != 6) begin
                $fatal(1, "FAIL: runtime vector 行格式错误 row=%0d", row_index);
            end
            if ((class_id < 0) || (class_id > 3)) begin
                $fatal(1, "FAIL: runtime vector class 越界");
            end
            transact(class_id, (class_id == 3), vector_addr, vector_data,
                     (class_id == 3) ? 4'd0 : strobe_value[3:0],
                     (class_id == 3) ? strobe_value[3:0] : 4'd0,
                     vector_expected, 3'd0, expected_stall);
        end
        $fclose(vector_fd);
        for (range_index = 0; range_index < 4; range_index = range_index + 1) begin
            if (transfer_counts[range_index] != 1000) begin
                $fatal(1, "FAIL: 类别 transfer 数量错误 class=%0d count=%0d",
                       range_index, transfer_counts[range_index]);
            end
        end
        finish_success();

        csr_write_word(8'h3C, 32'h0000_0001);
        start_job(1000000);
        for (range_index = 0; range_index < 2; range_index = range_index + 1) begin
            injected_code = (range_index == 0) ? 3'd6 : 3'd7;
            fault_inject_valid = 1'b1;
            fault_inject_code = injected_code;
            transact(2, 1'b0, feature_test_addr[0], 32'd0, 4'hF, 4'd0,
                     32'd0, injected_code, stall_schedule[stall_index[2]]);
            fault_inject_valid = 1'b0;
            fault_inject_code = 3'd0;
            if (!error || busy || done || head_output_valid || pl_owns_buffers) begin
                $fatal(1, "FAIL: memory error 未释放任务或未清 head_valid");
            end
            csr_check(8'h08, 32'd6);
            error_checks = error_checks + 1;
            csr_write_word(8'h3C, 32'h0000_0002);
            start_job(1000000);
        end

        transact(2, 1'b0, feature_test_addr[0], 32'd0, 4'd0, 4'd0,
                 32'd0, 3'd1, stall_schedule[stall_index[2]]);
        if (!error) $fatal(1, "FAIL: zero read strobe 未产生 BAD_ARGUMENT");
        csr_check(8'h08, 32'd1);
        error_checks = error_checks + 1;
        csr_write_word(8'h3C, 32'h0000_0002);
        start_job(1000000);

        transact(2, 1'b0, feature_test_addr[0] + 1, 32'd0, 4'h1, 4'd0,
                 32'd0, 3'd2, stall_schedule[stall_index[2]]);
        if (!error) $fatal(1, "FAIL: unaligned read 未产生 BAD_RANGE");
        csr_check(8'h08, 32'd2);
        error_checks = error_checks + 1;
        csr_write_word(8'h3C, 32'h0000_0002);

        start_job(1000000);
        for (range_index = 0; range_index < 3; range_index = range_index + 1) begin
            transact(3, 1'b1, feature_test_addr[0] + range_index*4,
                     32'h7100_0000 | range_index, 4'd0, 4'hF,
                     32'd0, 3'd0, stall_schedule[stall_index[3]]);
        end
        if (stall_index[3] != 3) begin
            $fatal(1, "FAIL: hard-reset cancel 准备未到 slot 7");
        end
        cancel_with_hard_reset(feature_test_addr[1], 32'hDEAD_0001);
        start_job(1000000);
        check_cancel_readback(feature_test_addr[1]);
        finish_success();
        csr_write_word(8'h3C, 32'h0000_0001);
        start_job(1000000);
        transact(3, 1'b1, feature_test_addr[1], 32'h1111_2222, 4'd0, 4'hF,
                 32'd0, 3'd0, stall_schedule[stall_index[3]]);
        retry_checks = retry_checks + 1;
        finish_success();
        csr_write_word(8'h3C, 32'h0000_0001);

        start_job(1000000);
        rotate_write_pointer_to_three();
        cancel_with_soft_reset(feature_test_addr[2], 32'hDEAD_0002);
        start_job(1000000);
        check_cancel_readback(feature_test_addr[2]);
        finish_success();
        csr_write_word(8'h3C, 32'h0000_0001);
        start_job(1000000);
        transact(3, 1'b1, feature_test_addr[2], 32'h3333_4444, 4'd0, 4'hF,
                 32'd0, 3'd0, stall_schedule[stall_index[3]]);
        retry_checks = retry_checks + 1;
        finish_success();
        csr_write_word(8'h3C, 32'h0000_0001);

        start_job(1000000);
        rotate_write_pointer_to_three();
        finish_success();
        csr_write_word(8'h3C, 32'h0000_0001);
        start_job(8);
        cancel_with_timeout(feature_test_addr[3], 32'hDEAD_0003);
        error_checks = error_checks + 1;
        csr_write_word(8'h3C, 32'h0000_0002);
        start_job(1000000);
        check_cancel_readback(feature_test_addr[3]);
        finish_success();
        csr_write_word(8'h3C, 32'h0000_0001);
        start_job(1000000);
        transact(3, 1'b1, feature_test_addr[3], 32'h5555_6666, 4'd0, 4'hF,
                 32'd0, 3'd0, stall_schedule[stall_index[3]]);
        retry_checks = retry_checks + 1;
        finish_success();

        if (error_checks != 5 || cancel_checks != 3 || retry_checks != 3) begin
            $fatal(1, "FAIL: directed integration counter 错误 errors=%0d cancel=%0d retry=%0d",
                   error_checks, cancel_checks, retry_checks);
        end
        $display("RESULT random_transfers=4000 accepted_read_input=%0d accepted_read_weights=%0d accepted_read_feature=%0d accepted_write_feature=%0d error_checks=%0d cancel_checks=%0d retry_checks=%0d",
                 transfer_counts[0], transfer_counts[1], transfer_counts[2],
                 transfer_counts[3], error_checks, cancel_checks, retry_checks);
        $display("PASS S2A-T12 runtime protocol integration");
        $finish;
    end

    initial begin
        #5000000;
        $fatal(1, "FAIL: T12 testbench global watchdog expired");
    end
endmodule
