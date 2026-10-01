`timescale 1ns/1ps
module tb_s2a_backend_fault_recovery;
    localparam logic [7:0] REG_CMD = 8'h00;
    localparam logic [7:0] REG_STATUS = 8'h04;
    localparam logic [7:0] REG_ERROR_CODE = 8'h08;
    localparam logic [7:0] REG_TIMEOUT = 8'h28;
    localparam logic [7:0] REG_ACK = 8'h3C;

    localparam logic [2:0] NONE = 3'd0;
    localparam logic [2:0] INTERNAL = 3'd6;
    localparam logic [2:0] TIMEOUT_ERROR = 3'd5;
    localparam logic [31:0] INPUT_BASE = 32'h0000_0000;
    localparam logic [31:0] INPUT_BYTES = 32'd519168;
    localparam logic [31:0] WEIGHT_BASE = 32'h0010_0000;
    localparam logic [31:0] WEIGHT_BYTES = 32'd5903100;
    localparam logic [31:0] OUTPUT_CANCEL_TIMEOUT = 32'd100000;
    localparam integer REQUEST_WAIT_LIMIT = 128;
    localparam integer OUTPUT_WRITE_WAIT_LIMIT = 20000;

    logic clk = 1'b0;
    logic hard_reset = 1'b1;
    logic csr_valid = 1'b0;
    logic csr_write = 1'b0;
    logic [7:0] csr_addr = 8'd0;
    logic [31:0] csr_wdata = 32'd0;
    logic csr_ready;
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
    logic buffer_owner_pl;
    logic head_output_valid;
    logic mem_valid;
    logic mem_write;
    logic [31:0] mem_addr;
    logic [31:0] mem_wdata;
    logic [3:0] mem_rstrb;
    logic [3:0] mem_wstrb;
    logic manual_mem_ready = 1'b0;
    logic automatic_read_responses = 1'b0;
    logic mem_ready;
    logic [31:0] mem_rdata;
    logic [2:0] manual_mem_error_code = NONE;
    logic [2:0] mem_error_code;
    logic [31:0] simulation_cycle_count = 32'd0;
    logic [31:0] transaction_start_cycle = 32'd0;
    integer memory_read_handshakes = 0;
    integer memory_write_side_effects = 0;

    always #5 clk = ~clk;

    always_comb begin
        mem_ready = manual_mem_ready;
        mem_rdata = 32'd0;
        mem_error_code = manual_mem_error_code;
        if (automatic_read_responses && mem_valid && !mem_write) begin
            mem_ready = 1'b1;
            mem_error_code = NONE;
        end
    end

    initial begin
        #5000000;
        $fatal(1, "定向 backend/CSR fault-recovery 自检超时");
    end

    always @(posedge clk) begin
        simulation_cycle_count <= simulation_cycle_count + 32'd1;
        if (mem_valid && mem_ready) begin
            if (mem_write) begin
                memory_write_side_effects <= memory_write_side_effects + 1;
            end else begin
                memory_read_handshakes <= memory_read_handshakes + 1;
            end
        end
    end

    s2a_control_csr u_csr (
        .clk(clk), .hard_reset(hard_reset),
        .csr_valid(csr_valid), .csr_ready(csr_ready), .csr_write(csr_write),
        .csr_addr(csr_addr), .csr_wdata(csr_wdata), .csr_rdata(csr_rdata),
        .backend_memory_error_valid(backend_memory_error_valid),
        .backend_memory_error_code(backend_memory_error_code),
        .operator_result_valid(operator_result_valid),
        .operator_error_code(operator_error_code),
        .backend_start(backend_start), .backend_abort(backend_abort),
        .busy(busy), .done(done), .error(error),
        .pl_owns_buffers(buffer_owner_pl), .head_output_valid(head_output_valid)
    );

    s2a_network_backend u_backend (
        .clk(clk), .hard_reset(hard_reset), .abort(backend_abort),
        .backend_start(backend_start), .buffer_owner_pl(buffer_owner_pl),
        .input_base_address(INPUT_BASE), .input_length_bytes(INPUT_BYTES),
        .weight_package_base_address(WEIGHT_BASE),
        .weight_package_length_bytes(WEIGHT_BYTES),
        .mem_valid(mem_valid), .mem_write(mem_write), .mem_addr(mem_addr),
        .mem_wdata(mem_wdata), .mem_rstrb(mem_rstrb), .mem_wstrb(mem_wstrb),
        .mem_ready(mem_ready), .mem_rdata(mem_rdata), .mem_error_code(mem_error_code),
        .backend_memory_error_valid(backend_memory_error_valid),
        .backend_memory_error_code(backend_memory_error_code),
        .operator_result_valid(operator_result_valid),
        .operator_error_code(operator_error_code)
    );

    function automatic logic is_onehot4(input logic [3:0] value);
        begin
            is_onehot4 = (value != 4'b0000) && ((value & (value - 4'b0001)) == 4'b0000);
        end
    endfunction

    function automatic logic selected_byte_in_input_tensor;
        integer lane;
        logic found;
        logic [31:0] selected_address;
        begin
            selected_byte_in_input_tensor = 1'b0;
            found = 1'b0;
            selected_address = 32'd0;
            for (lane = 0; lane < 4; lane = lane + 1) begin
                if (mem_rstrb[lane]) begin
                    selected_address = mem_addr + lane;
                    found = (selected_address >= INPUT_BASE) &&
                            (selected_address < (INPUT_BASE + INPUT_BYTES));
                end
            end
            selected_byte_in_input_tensor = found;
        end
    endfunction

    function automatic logic selected_byte_in_input_or_weight_tensor;
        integer lane;
        logic found;
        logic [31:0] selected_address;
        begin
            selected_byte_in_input_or_weight_tensor = 1'b0;
            found = 1'b0;
            selected_address = 32'd0;
            for (lane = 0; lane < 4; lane = lane + 1) begin
                if (mem_rstrb[lane]) begin
                    selected_address = mem_addr + lane;
                    found = (selected_address < INPUT_BYTES) ||
                            ((selected_address >= WEIGHT_BASE) &&
                             (selected_address < (WEIGHT_BASE + WEIGHT_BYTES)));
                end
            end
            selected_byte_in_input_or_weight_tensor = found;
        end
    endfunction

    function automatic logic selected_byte_in_layer0_output_tensor;
        integer lane;
        logic found;
        logic [31:0] selected_address;
        begin
            selected_byte_in_layer0_output_tensor = 1'b0;
            found = 1'b0;
            selected_address = 32'd0;
            for (lane = 0; lane < 4; lane = lane + 1) begin
                if (mem_wstrb[lane]) begin
                    selected_address = mem_addr + lane;
                    found = (selected_address >= 32'h0100_0000) &&
                            (selected_address < (32'h0100_0000 + 32'h0015_2000));
                end
            end
            selected_byte_in_layer0_output_tensor = found;
        end
    endfunction

    always @(posedge clk) begin
        if (automatic_read_responses && mem_valid && mem_ready && !mem_write) begin
            if (!is_onehot4(mem_rstrb) || (mem_wstrb != 4'b0000) ||
                (mem_addr[1:0] != 2'b00) ||
                !selected_byte_in_input_or_weight_tensor() ||
                (mem_error_code !== NONE) || (mem_rdata !== 32'd0)) begin
                $fatal(1, "synthetic read response 违反对象、byte-lane 或成功返回语义");
            end
        end
    end

    task automatic write_csr(input logic [7:0] address, input logic [31:0] value);
        begin
            @(negedge clk);
            if (!csr_ready) $fatal(1, "CSR 写入未 ready：addr=%02h", address);
            csr_valid = 1'b1;
            csr_write = 1'b1;
            csr_addr = address;
            csr_wdata = value;
            @(posedge clk);
            #1;
            @(negedge clk);
            csr_valid = 1'b0;
            csr_write = 1'b0;
            csr_addr = 8'd0;
            csr_wdata = 32'd0;
        end
    endtask

    task automatic read_csr(input logic [7:0] address, output logic [31:0] value);
        begin
            @(negedge clk);
            csr_valid = 1'b1;
            csr_write = 1'b0;
            csr_addr = address;
            csr_wdata = 32'd0;
            #1;
            value = csr_rdata;
            @(negedge clk);
            csr_valid = 1'b0;
            csr_addr = 8'd0;
        end
    endtask

    task automatic check_status(
        input logic [3:0] expected_status,
        input logic [2:0] expected_error_code,
        input logic expected_head_valid,
        input string phase_name
    );
        logic [31:0] status_value;
        logic [31:0] error_value;
        begin
            read_csr(REG_STATUS, status_value);
            read_csr(REG_ERROR_CODE, error_value);
            if (status_value[3:0] !== expected_status) begin
                $fatal(1, "%s STATUS 不匹配：期望=%b 实际=%b",
                       phase_name, expected_status, status_value[3:0]);
            end
            if (error_value[2:0] !== expected_error_code) begin
                $fatal(1, "%s ERROR_CODE 不匹配：期望=%0d 实际=%0d",
                       phase_name, expected_error_code, error_value[2:0]);
            end
            if (head_output_valid !== expected_head_valid) begin
                $fatal(1, "%s head_output_valid 不匹配：期望=%b 实际=%b",
                       phase_name, expected_head_valid, head_output_valid);
            end
            if ((busy !== expected_status[0]) ||
                (done !== expected_status[1]) ||
                (error !== expected_status[2]) ||
                (buffer_owner_pl !== expected_status[3])) begin
                $fatal(1, "%s CSR/status 输出与状态位不一致", phase_name);
            end
        end
    endtask

    task automatic reset_design;
        begin
            @(negedge clk);
            hard_reset = 1'b1;
            csr_valid = 1'b0;
            csr_write = 1'b0;
            manual_mem_ready = 1'b0;
            automatic_read_responses = 1'b0;
            manual_mem_error_code = NONE;
            repeat (2) @(posedge clk);
            #1;
            if (mem_valid || busy || done || error || buffer_owner_pl || head_output_valid) begin
                $fatal(1, "硬复位期间状态或 memory request 未清除");
            end
            @(negedge clk);
            hard_reset = 1'b0;
            @(posedge clk);
            #1;
            if (backend_abort || mem_valid) $fatal(1, "硬复位释放后 abort/request 未清除");
        end
    endtask

    task automatic start_transaction(input logic [31:0] timeout_value);
        begin
            write_csr(REG_TIMEOUT, timeout_value);
            write_csr(REG_CMD, 32'd1);
            if (!backend_start || !busy || !buffer_owner_pl || done || error) begin
                $fatal(1, "CSR 未接受合法 start：start=%b busy=%b owner=%b",
                       backend_start, busy, buffer_owner_pl);
            end
            transaction_start_cycle = simulation_cycle_count;
        end
    endtask

    task automatic wait_for_read_request;
        integer wait_index;
        logic request_found;
        begin
            request_found = 1'b0;
            for (wait_index = 0; wait_index < REQUEST_WAIT_LIMIT; wait_index = wait_index + 1) begin
                @(negedge clk);
                if (mem_valid) begin
                    request_found = 1'b1;
                    if (mem_write || !is_onehot4(mem_rstrb) || (mem_wstrb != 4'b0000) ||
                        (mem_addr[1:0] != 2'b00) || !selected_byte_in_input_tensor()) begin
                        $fatal(1, "backend 首个 feature 读请求不在输入 tensor 或 byte lane 非法：addr=%08h rstrb=%b",
                               mem_addr, mem_rstrb);
                    end
                    if (mem_ready) $fatal(1, "unaccepted request 观测前意外握手");
                    break;
                end
                if (!busy || !buffer_owner_pl || error || done) begin
                    $fatal(1, "等待合法 read request 时任务提前离开 busy：busy=%b error=%b code=%0d",
                           busy, error, u_csr.error_code);
                end
            end
            if (!request_found) $fatal(1, "backend 未在限定周期内发出真实 read request");
        end
    endtask

    task automatic hold_unaccepted_request;
        logic [31:0] saved_address;
        logic [31:0] saved_wdata;
        logic [3:0] saved_rstrb;
        logic [3:0] saved_wstrb;
        logic saved_write;
        integer stall_index;
        begin
            saved_address = mem_addr;
            saved_wdata = mem_wdata;
            saved_rstrb = mem_rstrb;
            saved_wstrb = mem_wstrb;
            saved_write = mem_write;
            for (stall_index = 0; stall_index < 3; stall_index = stall_index + 1) begin
                @(posedge clk);
                #1;
                if (!mem_valid || mem_ready || (mem_addr !== saved_address) ||
                    (mem_wdata !== saved_wdata) || (mem_rstrb !== saved_rstrb) ||
                    (mem_wstrb !== saved_wstrb) || (mem_write !== saved_write)) begin
                    $fatal(1, "未握手 memory request 字段未保持稳定");
                end
            end
        end
    endtask

    task automatic wait_for_memory_error;
        integer wait_index;
        logic error_found;
        begin
            error_found = 1'b0;
            for (wait_index = 0; wait_index < 8; wait_index = wait_index + 1) begin
                @(negedge clk);
                if (error && !busy) begin
                    error_found = 1'b1;
                    break;
                end
            end
            if (!error_found) $fatal(1, "真实 memory error response 未终止 CSR 任务");
        end
    endtask

    task automatic inject_read_error(input logic [2:0] response_code);
        integer reads_before;
        integer writes_before;
        begin
            automatic_read_responses = 1'b0;
            manual_mem_ready = 1'b0;
            manual_mem_error_code = NONE;
            wait_for_read_request();
            hold_unaccepted_request();
            reads_before = memory_read_handshakes;
            writes_before = memory_write_side_effects;
            @(negedge clk);
            manual_mem_ready = 1'b1;
            manual_mem_error_code = response_code;
            #1;
            if (!mem_valid || mem_write || !backend_memory_error_valid ||
                (backend_memory_error_code !== response_code)) begin
                $fatal(1, "memory response 未经真实 backend handshake 产生错误事件：code=%0d valid=%b",
                       response_code, backend_memory_error_valid);
            end
            @(posedge clk);
            #1;
            manual_mem_ready = 1'b0;
            manual_mem_error_code = NONE;
            if (memory_read_handshakes != (reads_before + 1)) begin
                $fatal(1, "注入错误读未恰好握手一次：before=%0d after=%0d",
                       reads_before, memory_read_handshakes);
            end
            if (memory_write_side_effects != writes_before) begin
                $fatal(1, "失败 read response 产生 output write 副作用");
            end
            wait_for_memory_error();
            if (mem_valid || backend_memory_error_valid) begin
                $fatal(1, "失败 response 后仍有 memory request/error event");
            end
            check_status(4'b0100, INTERNAL, 1'b0, "memory fault");
        end
    endtask

    task automatic acknowledge_error;
        begin
            write_csr(REG_ACK, 32'd2);
            check_status(4'b0000, NONE, 1'b0, "ACK 后");
        end
    endtask

    task automatic check_no_late_effects(input integer reads_before, input integer writes_before);
        integer quiet_index;
        begin
            @(negedge clk);
            automatic_read_responses = 1'b0;
            manual_mem_error_code = NONE;
            manual_mem_ready = 1'b1;
            for (quiet_index = 0; quiet_index < 3; quiet_index = quiet_index + 1) begin
                @(posedge clk);
                #1;
                if (mem_valid || backend_memory_error_valid || mem_write) begin
                    $fatal(1, "取消后出现迟到请求或 memory error event");
                end
                if ((memory_read_handshakes != reads_before) ||
                    (memory_write_side_effects != writes_before)) begin
                    $fatal(1, "取消后出现迟到 read/write memory 副作用");
                end
            end
            @(negedge clk);
            manual_mem_ready = 1'b0;
        end
    endtask

    task automatic wait_for_first_output_write(input string case_name);
        integer wait_index;
        logic request_found;
        begin
            request_found = 1'b0;
            for (wait_index = 0; wait_index < OUTPUT_WRITE_WAIT_LIMIT; wait_index = wait_index + 1) begin
                @(negedge clk);
                if (mem_valid && mem_write) begin
                    request_found = 1'b1;
                    if (mem_ready || !busy || !buffer_owner_pl || done || error ||
                        (u_backend.layer_cursor !== 6'd0) ||
                        !is_onehot4(mem_wstrb) || (mem_rstrb != 4'b0000) ||
                        (mem_addr[1:0] != 2'b00) || !selected_byte_in_layer0_output_tensor()) begin
                        $fatal(1, "layer0 首笔 output write 请求不合法：addr=%08h wstrb=%b ready=%b layer=%0d",
                               mem_addr, mem_wstrb, mem_ready, u_backend.layer_cursor);
                    end
                    $display("S2A_PENDING_OUTPUT_WRITE case=%s layer=0 cycles_from_start=%0d reads=%0d addr=%08h wstrb=%b",
                             case_name, simulation_cycle_count - transaction_start_cycle,
                             memory_read_handshakes, mem_addr, mem_wstrb);
                    break;
                end
                if (!busy || !buffer_owner_pl || error || done) begin
                    $fatal(1, "等待 layer0 output write 时任务提前离开 busy：busy=%b error=%b code=%0d",
                           busy, error, u_csr.error_code);
                end
            end
            if (!request_found) begin
                $fatal(1, "layer0 未在 %0d cycles 内产生首笔 output write", OUTPUT_WRITE_WAIT_LIMIT);
            end
        end
    endtask

    task automatic hold_unaccepted_output_write;
        logic [31:0] saved_address;
        logic [31:0] saved_wdata;
        logic [3:0] saved_wstrb;
        integer stall_index;
        begin
            saved_address = mem_addr;
            saved_wdata = mem_wdata;
            saved_wstrb = mem_wstrb;
            for (stall_index = 0; stall_index < 3; stall_index = stall_index + 1) begin
                @(posedge clk);
                #1;
                if (!mem_valid || !mem_write || mem_ready ||
                    (mem_addr !== saved_address) || (mem_wdata !== saved_wdata) ||
                    (mem_wstrb !== saved_wstrb) || (mem_rstrb !== 4'b0000)) begin
                    $fatal(1, "未握手 layer0 output write 字段未保持稳定");
                end
            end
        end
    endtask

    task automatic prepare_unaccepted_output_write(input string case_name);
        integer reads_before;
        integer writes_before;
        begin
            manual_mem_ready = 1'b0;
            manual_mem_error_code = NONE;
            automatic_read_responses = 1'b1;
            reads_before = memory_read_handshakes;
            writes_before = memory_write_side_effects;
            start_transaction(OUTPUT_CANCEL_TIMEOUT);
            wait_for_first_output_write(case_name);
            hold_unaccepted_output_write();
            if ((memory_read_handshakes <= reads_before) ||
                (memory_write_side_effects != writes_before)) begin
                $fatal(1, "到达首笔未握手 output write 前后读写计数异常");
            end
            if (case_name == "hard_reset") begin
                $display("S2A_RETRY_CASE after=soft_reset request=pending_output_write next=hard_reset start_accepted=1");
            end else if (case_name == "csr_timeout") begin
                $display("S2A_RETRY_CASE after=hard_reset request=pending_output_write next=csr_timeout start_accepted=1");
            end
        end
    endtask

    task automatic cancel_output_write_with_soft_reset;
        integer reads_before;
        integer writes_before;
        begin
            prepare_unaccepted_output_write("soft_reset");
            reads_before = memory_read_handshakes;
            writes_before = memory_write_side_effects;
            write_csr(REG_CMD, 32'd2);
            if (!backend_abort || mem_valid || buffer_owner_pl || busy) begin
                $fatal(1, "soft_reset 未撤销未握手 output write 或释放 ownership");
            end
            check_status(4'b0000, NONE, 1'b0, "soft_reset 后");
            check_no_late_effects(reads_before, writes_before);
            if (memory_write_side_effects != writes_before) begin
                $fatal(1, "soft_reset 后出现迟到 output write 副作用");
            end
            $display("S2A_OUTPUT_WRITE_CANCEL kind=soft_reset layer=0 writes_before=%0d writes_after=%0d",
                     writes_before, memory_write_side_effects);
            $display("S2A_CANCEL_CASE kind=soft_reset request=pending_output_write cancelled=1 writes_before=%0d writes_after=%0d",
                     writes_before, memory_write_side_effects);
        end
    endtask

    task automatic cancel_output_write_with_hard_reset;
        integer reads_before;
        integer writes_before;
        begin
            prepare_unaccepted_output_write("hard_reset");
            reads_before = memory_read_handshakes;
            writes_before = memory_write_side_effects;
            @(negedge clk);
            hard_reset = 1'b1;
            #1;
            if (mem_valid) $fatal(1, "hard_reset 未在 output write 握手前撤销 mem_valid");
            repeat (2) @(posedge clk);
            #1;
            if (busy || done || error || buffer_owner_pl || head_output_valid) begin
                $fatal(1, "hard_reset 未清除 CSR 状态/ownership/head-valid");
            end
            @(negedge clk);
            hard_reset = 1'b0;
            @(posedge clk);
            #1;
            if (backend_abort || mem_valid) $fatal(1, "hard_reset 后未恢复 idle");
            check_status(4'b0000, NONE, 1'b0, "hard_reset 后");
            check_no_late_effects(reads_before, writes_before);
            if (memory_write_side_effects != writes_before) begin
                $fatal(1, "hard_reset 后出现迟到 output write 副作用");
            end
            $display("S2A_OUTPUT_WRITE_CANCEL kind=hard_reset layer=0 writes_before=%0d writes_after=%0d",
                     writes_before, memory_write_side_effects);
            $display("S2A_CANCEL_CASE kind=hard_reset request=pending_output_write cancelled=1 writes_before=%0d writes_after=%0d",
                     writes_before, memory_write_side_effects);
        end
    endtask

    task automatic cancel_output_write_with_timeout;
        integer reads_before;
        integer writes_before;
        integer wait_index;
        logic timeout_found;
        begin
            prepare_unaccepted_output_write("csr_timeout");
            reads_before = memory_read_handshakes;
            writes_before = memory_write_side_effects;
            timeout_found = 1'b0;
            for (wait_index = 0; wait_index < (OUTPUT_CANCEL_TIMEOUT + 8); wait_index = wait_index + 1) begin
                @(negedge clk);
                if (error && !busy) begin
                    timeout_found = 1'b1;
                    break;
                end
                if (!mem_valid || !mem_write || mem_ready || (mem_addr[1:0] != 2'b00)) begin
                    $fatal(1, "CSR timeout 前 layer0 output write 未保持为未握手请求");
                end
            end
            if (!timeout_found) $fatal(1, "未握手 output write 未在配置 timeout 周期撤销");
            if (mem_valid || buffer_owner_pl || done || head_output_valid) begin
                $fatal(1, "timeout 后 output write/ownership/done/head-valid 状态错误");
            end
            check_status(4'b0100, TIMEOUT_ERROR, 1'b0, "output write timeout 后");
            if (memory_read_handshakes != reads_before ||
                memory_write_side_effects != writes_before) begin
                $fatal(1, "timeout 前未握手 output write 不应产生 memory 副作用");
            end
            check_no_late_effects(reads_before, writes_before);
            if (memory_write_side_effects != writes_before) begin
                $fatal(1, "timeout 后出现迟到 output write 副作用");
            end
            $display("S2A_OUTPUT_WRITE_CANCEL kind=csr_timeout layer=0 writes_before=%0d writes_after=%0d",
                     writes_before, memory_write_side_effects);
            $display("S2A_CANCEL_CASE kind=csr_timeout request=pending_output_write cancelled=1 writes_before=%0d writes_after=%0d",
                     writes_before, memory_write_side_effects);
        end
    endtask

    initial begin
        reset_design();
        check_status(4'b0000, NONE, 1'b0, "初始复位后");

        start_transaction(32'd5000);
        inject_read_error(3'd6);
        acknowledge_error();
        $display("S2A_FAULT_CASE code=6 mapped=INTERNAL ack_restart=ready");

        start_transaction(32'd5000);
        inject_read_error(3'd7);
        acknowledge_error();
        $display("S2A_FAULT_CASE code=7 mapped=INTERNAL ack_restart=ready");

        cancel_output_write_with_soft_reset();
        cancel_output_write_with_hard_reset();

        cancel_output_write_with_timeout();
        acknowledge_error();

        automatic_read_responses = 1'b0;
        manual_mem_ready = 1'b0;
        start_transaction(32'd5000);
        wait_for_read_request();
        $display("S2A_RETRY_CASE after=csr_timeout_ack request=pending_read next=soft_reset start_accepted=1");
        begin
            integer reads_before;
            integer writes_before;
            reads_before = memory_read_handshakes;
            writes_before = memory_write_side_effects;
            write_csr(REG_CMD, 32'd2);
            check_status(4'b0000, NONE, 1'b0, "timeout ACK 后重启再 soft_reset");
            check_no_late_effects(reads_before, writes_before);
            $display("S2A_CANCEL_CASE kind=soft_reset request=pending_read cancelled=1 ack_restart=ready");
        end

        if (memory_write_side_effects != 0) begin
            $fatal(1, "定向错误/取消测试不应提交 output writes：%0d", memory_write_side_effects);
        end
        $display("PASS_S2A_BACKEND_FAULT_CANCEL_RECOVERY reads=%0d writes=%0d",
                 memory_read_handshakes, memory_write_side_effects);
        $finish;
    end
endmodule
