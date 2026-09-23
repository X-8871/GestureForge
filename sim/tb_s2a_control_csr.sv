// S2A-T11：独立 CSR 与控制状态机定向/随机仿真。
module tb_s2a_control_csr;
    logic clk;
    logic hard_reset;
    logic csr_valid;
    logic csr_ready;
    logic csr_write;
    logic [7:0] csr_addr;
    logic [31:0] csr_wdata;
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
    logic pl_owns_buffers;
    logic head_output_valid;

    integer vector_fd;
    integer scan_result;
    integer random_mode;
    integer random_addr;
    integer random_data;
    integer random_expected;
    integer random_count;
    integer csr_transfer_count;
    integer directed_count;
    integer case_count;
    integer code_value;
    integer edge_index;

    s2a_control_csr dut (
        .clk(clk),
        .hard_reset(hard_reset),
        .csr_valid(csr_valid),
        .csr_ready(csr_ready),
        .csr_write(csr_write),
        .csr_addr(csr_addr),
        .csr_wdata(csr_wdata),
        .csr_rdata(csr_rdata),
        .backend_memory_error_valid(backend_memory_error_valid),
        .backend_memory_error_code(backend_memory_error_code),
        .operator_result_valid(operator_result_valid),
        .operator_error_code(operator_error_code),
        .backend_start(backend_start),
        .backend_abort(backend_abort),
        .busy(busy),
        .done(done),
        .error(error),
        .pl_owns_buffers(pl_owns_buffers),
        .head_output_valid(head_output_valid)
    );

    always #5 clk = ~clk;

    task automatic fail(input string message);
        begin
            $display("FAIL: %s", message);
            $fatal(1);
            $finish;
        end
    endtask

    task automatic check(input logic condition, input string message);
        begin
            if (condition !== 1'b1) fail(message);
        end
    endtask

    task automatic check_state(input logic expected_busy,
                               input logic expected_done,
                               input logic expected_error,
                               input logic expected_owner,
                               input logic expected_head,
                               input logic [2:0] expected_code,
                               input string label_text);
        begin
            #1;
            if ((busy !== expected_busy) || (done !== expected_done) ||
                (error !== expected_error) ||
                (pl_owns_buffers !== expected_owner) ||
                (head_output_valid !== expected_head) ||
                (dut.error_code !== expected_code)) begin
                fail($sformatf("%s 状态 busy/done/error/owner/head/code=%b%b%b%b%b/%0d 期望=%b%b%b%b%b/%0d",
                               label_text, busy, done, error, pl_owns_buffers,
                               head_output_valid, dut.error_code, expected_busy,
                               expected_done, expected_error, expected_owner,
                               expected_head, expected_code));
            end
        end
    endtask

    task automatic write_csr(input logic [7:0] address,
                             input logic [31:0] value);
        begin
            @(negedge clk);
            csr_valid = 1'b1;
            csr_write = 1'b1;
            csr_addr = address;
            csr_wdata = value;
            #1;
            check(csr_ready, "非硬复位时 CSR ready 必须为高");
            @(posedge clk);
            if (!(csr_valid && csr_ready)) fail("CSR 写未在 ready 上升沿被接受");
            #1;
            csr_transfer_count = csr_transfer_count + 1;
            @(negedge clk);
            csr_valid = 1'b0;
            csr_write = 1'b0;
            csr_addr = 8'd0;
            csr_wdata = 32'd0;
        end
    endtask

    task automatic csr_read(input logic [7:0] address,
                            input logic [31:0] expected,
                            input string label_text);
        begin
            @(negedge clk);
            csr_valid = 1'b1;
            csr_write = 1'b0;
            csr_addr = address;
            csr_wdata = 32'd0;
            #1;
            check(csr_ready, "读访问非硬复位时 ready 必须为高");
            if (csr_rdata !== expected) begin
                fail($sformatf("%s addr=%h read=%h expected=%h",
                               label_text, address, csr_rdata, expected));
            end
            @(posedge clk);
            if (!(csr_valid && csr_ready)) fail("CSR 读未在 ready 上升沿被接受");
            #1;
            csr_transfer_count = csr_transfer_count + 1;
            @(negedge clk);
            csr_valid = 1'b0;
            csr_addr = 8'd0;
        end
    endtask

    task automatic check_defaults;
        begin
            csr_read(8'h04, 32'd0, "默认 STATUS");
            csr_read(8'h08, 32'd0, "默认 ERROR_CODE");
            csr_read(8'h0C, 32'd0, "默认 FRAME_ID");
            csr_read(8'h10, 32'd0, "默认 INPUT_ADDR");
            csr_read(8'h14, 32'd519168, "默认 INPUT_BYTES");
            csr_read(8'h18, 32'h00100000, "默认 WEIGHT_ADDR");
            csr_read(8'h1C, 32'd5903100, "默认 WEIGHT_BYTES");
            csr_read(8'h20, 32'h01000000, "默认 FEATURE_BASE");
            csr_read(8'h24, 32'd28159416, "默认 FEATURE_LIMIT");
            csr_read(8'h28, 32'd0, "默认 TIMEOUT_CYCLES");
            csr_read(8'h2C, 32'd27549952, "默认 HEAD13_ADDR");
            csr_read(8'h30, 32'd5070, "默认 HEAD13_BYTES");
            csr_read(8'h34, 32'd28139136, "默认 HEAD26_ADDR");
            csr_read(8'h38, 32'd20280, "默认 HEAD26_BYTES");
            directed_count = directed_count + 14;
        end
    endtask

    task automatic start_task(input logic [31:0] timeout_value,
                              input logic [31:0] frame_value);
        begin
            write_csr(8'h0C, frame_value);
            write_csr(8'h28, timeout_value);
            write_csr(8'h00, 32'h00000001);
            check_state(1'b1, 1'b0, 1'b0, 1'b1, 1'b0, 3'd0,
                        "合法 start 接受");
            check(backend_start, "合法 start 必须产生 backend_start");
            check(!backend_abort, "合法 start 不得同时 abort");
            directed_count = directed_count + 1;
        end
    endtask

    task automatic inject_operator(input logic [2:0] code_value_input);
        begin
            @(negedge clk);
            operator_result_valid = 1'b1;
            operator_error_code = code_value_input;
            @(posedge clk);
            #1;
            operator_result_valid = 1'b0;
            operator_error_code = 3'd0;
        end
    endtask

    task automatic inject_memory(input logic [2:0] code_value_input);
        begin
            @(negedge clk);
            backend_memory_error_valid = 1'b1;
            backend_memory_error_code = code_value_input;
            @(posedge clk);
            #1;
            backend_memory_error_valid = 1'b0;
            backend_memory_error_code = 3'd0;
        end
    endtask

    task automatic ack_error;
        begin
            write_csr(8'h3C, 32'h00000002);
            check_state(1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 3'd0,
                        "ACK error 后恢复 idle");
            csr_read(8'h08, 32'd0, "ACK error 清 ERROR_CODE");
            csr_read(8'h04, 32'd0, "ACK error 清 STATUS.error");
            directed_count = directed_count + 1;
        end
    endtask

    task automatic ack_done;
        begin
            write_csr(8'h3C, 32'h00000001);
            #1;
            check(!busy && !done && !error && !pl_owns_buffers &&
                  (dut.error_code == 3'd0), "ACK done 后恢复 idle");
            csr_read(8'h04, 32'd0, "ACK done 清 STATUS.done");
            directed_count = directed_count + 1;
        end
    endtask

    task automatic check_abort_pulse;
        begin
            check(backend_abort, "中止任务必须产生 backend_abort");
            directed_count = directed_count + 1;
        end
    endtask

    task automatic run_random_accesses;
        integer scanned;
        begin
            vector_fd = $fopen("csr_random.dat", "r");
            if (vector_fd == 0) fail("无法打开 runner 生成的 csr_random.dat");
            random_count = 0;
            while (!$feof(vector_fd)) begin
                scanned = $fscanf(vector_fd, "%d %h %h %h\n",
                                  random_mode, random_addr, random_data,
                                  random_expected);
                if (scanned == 4) begin
                    if (random_mode == 0) begin
                        csr_read(random_addr[7:0], random_expected[31:0],
                                 "随机 CSR 读");
                    end else if (random_mode == 1) begin
                        write_csr(random_addr[7:0], random_data[31:0]);
                        csr_read(random_addr[7:0], random_expected[31:0],
                                 "随机 CSR 写后读");
                    end else begin
                        fail("随机向量 mode 非法");
                    end
                    random_count = random_count + 1;
                end
            end
            $fclose(vector_fd);
            if (random_count != 256) fail("随机 CSR 样例数必须为 256");
        end
    endtask

    initial begin
        clk = 1'b0;
        hard_reset = 1'b1;
        csr_valid = 1'b0;
        csr_write = 1'b0;
        csr_addr = 8'd0;
        csr_wdata = 32'd0;
        backend_memory_error_valid = 1'b0;
        backend_memory_error_code = 3'd0;
        operator_result_valid = 1'b0;
        operator_error_code = 3'd0;
        random_count = 0;
        csr_transfer_count = 0;
        directed_count = 0;
        case_count = 0;
        repeat (2) @(posedge clk);
        #1;
        check(!csr_ready, "硬复位期间 csr_ready 必须为低");
        check(!busy && !done && !error && !pl_owns_buffers && !head_output_valid,
              "硬复位清除状态");
        check(backend_abort, "硬复位产生 backend_abort");
        @(negedge clk);
        hard_reset = 1'b0;
        #1;
        check(csr_ready, "硬复位后 csr_ready 必须为高");
        check_defaults();

        // RO 写、未对齐和保留地址按冻结规则忽略。
        write_csr(8'h04, 32'hFFFF_FFFF);
        write_csr(8'h08, 32'hFFFF_FFFF);
        write_csr(8'h20, 32'd1);
        write_csr(8'h24, 32'd2);
        write_csr(8'h2C, 32'd3);
        write_csr(8'h30, 32'd4);
        write_csr(8'h34, 32'd5);
        write_csr(8'h38, 32'd6);
        write_csr(8'h0D, 32'hAAAA_5555);
        write_csr(8'h40, 32'h5555_AAAA);
        csr_read(8'h0D, 32'd0, "未对齐读为零");
        csr_read(8'h40, 32'd0, "保留地址读为零");
        csr_read(8'h04, 32'd0, "RO STATUS 写忽略");
        csr_read(8'h08, 32'd0, "RO ERROR_CODE 写忽略");
        csr_read(8'h20, 32'h01000000, "RO FEATURE_BASE 写忽略");
        directed_count = directed_count + 12;

        // 随机 CSR 序列由 runner 依据固定 seed 生成，并检查读回黄金。
        run_random_accesses();
        if (csr_transfer_count < random_count)
            fail("G0 csr 向量未实际完成足量 ready 握手");
        case_count = case_count + 1;
        // 清回默认值后再验证非法 start，每次只注入一个错误。
        write_csr(8'h0C, 32'd0);
        write_csr(8'h10, 32'd4);
        write_csr(8'h28, 32'd8);
        write_csr(8'h00, 32'd1);
        check_state(1'b0, 1'b0, 1'b1, 1'b0, 1'b0, 3'd2,
                    "INPUT_ADDR 错误为 BAD_RANGE");
        csr_read(8'h04, 32'd4, "error 状态 CSR STATUS 位");
        write_csr(8'h0C, 32'hA5A5_5A5A);
        csr_read(8'h0C, 32'd0, "error sticky 时配置写忽略");
        write_csr(8'h00, 32'd1);
        check_state(1'b0, 1'b0, 1'b1, 1'b0, 1'b0, 3'd2,
                    "error sticky 时 start 忽略");
        ack_error();
        write_csr(8'h10, 32'd0);

        write_csr(8'h18, 32'h00100004);
        write_csr(8'h00, 32'd1);
        check_state(1'b0, 1'b0, 1'b1, 1'b0, 1'b0, 3'd2,
                    "WEIGHT_ADDR 错误为 BAD_RANGE");
        ack_error();
        write_csr(8'h18, 32'h00100000);

        write_csr(8'h14, 32'd519167);
        write_csr(8'h00, 32'd1);
        check_state(1'b0, 1'b0, 1'b1, 1'b0, 1'b0, 3'd3,
                    "INPUT_BYTES 错误为 BAD_LENGTH");
        ack_error();
        write_csr(8'h14, 32'd519168);

        write_csr(8'h1C, 32'd5903099);
        write_csr(8'h00, 32'd1);
        check_state(1'b0, 1'b0, 1'b1, 1'b0, 1'b0, 3'd3,
                    "WEIGHT_BYTES 错误为 BAD_LENGTH");
        ack_error();
        write_csr(8'h1C, 32'd5903100);

        write_csr(8'h28, 32'd0);
        write_csr(8'h00, 32'd1);
        check_state(1'b0, 1'b0, 1'b1, 1'b0, 1'b0, 3'd1,
                    "零 timeout 为 BAD_ARGUMENT");
        ack_error();

        // timeout=1 给出一个完整后续周期；无完成事件时该周期结束后超时。
        start_task(32'd1, 32'd101);
        @(posedge clk);
        #1;
        check_state(1'b0, 1'b0, 1'b1, 1'b0, 1'b0, 3'd5,
                    "timeout=1 在首个后续沿超时");
        check_abort_pulse();
        ack_error();

        // completion_boundary：N=5 时第 5 个后续沿的成功结果优先。
        start_task(32'd5, 32'h1234_5678);
        for (edge_index = 1; edge_index < 5; edge_index = edge_index + 1) begin
            @(posedge clk);
            #1;
            check_state(1'b1, 1'b0, 1'b0, 1'b1, 1'b0, 3'd0,
                        "timeout 边界前保持 busy");
        end
        inject_operator(3'd0);
        check_state(1'b0, 1'b1, 1'b0, 1'b0, 1'b1, 3'd0,
                    "completion_boundary 第五沿成功优先");
        csr_read(8'h04, 32'd2, "done 状态 CSR STATUS 位");
        csr_read(8'h08, 32'd0, "done 时 ERROR_CODE 清零");
        case_count = case_count + 1;
        csr_read(8'h0C, 32'h1234_5678, "完成时回传锁存 frame_id");
        write_csr(8'h0C, 32'h89AB_CDEF);
        csr_read(8'h0C, 32'h1234_5678, "done sticky 时配置写忽略");
        write_csr(8'h00, 32'd1);
        check_state(1'b0, 1'b1, 1'b0, 1'b0, 1'b1, 3'd0,
                    "done sticky 时 start 忽略");
        ack_done();

        // timeout_recovery：timeout=4，在第 4 个后续沿超时，第 5 沿结果无效。
        start_task(32'd4, 32'd202);
        repeat (3) begin
            @(posedge clk);
            #1;
            check(busy, "timeout_recovery 第四沿前必须仍 busy");
        end
        @(posedge clk);
        #1;
        check_state(1'b0, 1'b0, 1'b1, 1'b0, 1'b0, 3'd5,
                    "timeout_recovery 第四后续沿超时");
        check_abort_pulse();
        inject_operator(3'd0);
        check_state(1'b0, 1'b0, 1'b1, 1'b0, 1'b0, 3'd5,
                    "timeout 后晚到结果被忽略");
        ack_error();
        case_count = case_count + 1;

        // 错误优先于同时到达的成功完成，memory 码 1/2/6 原样，7 映射 6。
        for (code_value = 1; code_value <= 2; code_value = code_value + 1) begin
            start_task(32'd20, 32'h2000_0000 + code_value);
            @(negedge clk);
            backend_memory_error_valid = 1'b1;
            backend_memory_error_code = code_value[2:0];
            operator_result_valid = 1'b1;
            operator_error_code = 3'd0;
            @(posedge clk);
            #1;
            backend_memory_error_valid = 1'b0;
            backend_memory_error_code = 3'd0;
            operator_result_valid = 1'b0;
            operator_error_code = 3'd0;
            check_state(1'b0, 1'b0, 1'b1, 1'b0, 1'b0,
                        code_value[2:0], "memory error code 1/2 原样并优先");
            check_abort_pulse();
            ack_error();
        end
        start_task(32'd20, 32'h2000_0006);
        inject_memory(3'd6);
        check_state(1'b0, 1'b0, 1'b1, 1'b0, 1'b0, 3'd6,
                    "G0 memory error code 6 原样");
        ack_error();
        start_task(32'd20, 32'h2000_0007);
        inject_memory(3'd7);
        check_state(1'b0, 1'b0, 1'b1, 1'b0, 1'b0, 3'd6,
                    "G0 memory error code 7 映射 INTERNAL");
        ack_error();
        // 一个 G0 memory_error_recovery 向量包含独立验证的 code 6 和 7。
        case_count = case_count + 1;

        // operator 已知码 1..7 原样保留，包含 G0 accumulator overflow=7。
        for (code_value = 1; code_value <= 7; code_value = code_value + 1) begin
            start_task(32'd20, 32'h3000_0000 + code_value);
            inject_operator(code_value[2:0]);
            check_state(1'b0, 1'b0, 1'b1, 1'b0, 1'b0,
                        code_value[2:0], "operator 已知错误码原样保留");
            check_abort_pulse();
            ack_error();
            if (code_value == 7) case_count = case_count + 1;
        end

        // busy 期间配置与 start 忽略，soft_reset 中止并恢复整组默认寄存器。
        start_task(32'd50, 32'hCAFE_BABE);
        csr_read(8'h04, 32'd9, "busy 与 PL ownership CSR STATUS 位");
        write_csr(8'h0C, 32'hDEAD_BEEF);
        write_csr(8'h00, 32'd1);
        check_state(1'b1, 1'b0, 1'b0, 1'b1, 1'b0, 3'd0,
                    "busy 时 config 和 start 均忽略");
        csr_read(8'h0C, 32'hCAFE_BABE, "busy 时 FRAME_ID 不可改");
        write_csr(8'h00, 32'd3);
        check_state(1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 3'd0,
                    "soft_reset 优先于同时 start 并中止 busy");
        check_abort_pulse();
        check_defaults();

        // soft_reset 在 idle 时同样恢复所有可写配置默认值。
        write_csr(8'h0C, 32'h1111_1111);
        write_csr(8'h10, 32'h0000_0010);
        write_csr(8'h14, 32'd11);
        write_csr(8'h18, 32'h0020_0000);
        write_csr(8'h1C, 32'd12);
        write_csr(8'h28, 32'd13);
        write_csr(8'h00, 32'd2);
        check_defaults();

        // hard reset 取消活动任务并同步恢复默认值。
        start_task(32'd50, 32'h5555_AAAA);
        @(negedge clk);
        hard_reset = 1'b1;
        #1;
        check(!csr_ready, "硬复位期间 ready 为低");
        @(posedge clk);
        #1;
        check_state(1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 3'd0,
                    "硬复位取消活动任务");
        check_abort_pulse();
        @(negedge clk);
        hard_reset = 1'b0;
        check_defaults();

        if (case_count != 5) fail("G0 适用协议向量覆盖计数必须为 5");
        $display("RESULT random_accesses=%0d csr_transfers=%0d directed_checks=%0d protocol_cases=%0d",
                 random_count, csr_transfer_count, directed_count, case_count);
        $display("PASS S2A-T11 standalone CSR/control FSM");
        $finish;
    end
endmodule
