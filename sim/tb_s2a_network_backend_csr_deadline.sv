// S2A-T64：联合检查 backend 与 CSR 在全局 deadline 同沿的完成和错误事件。
`timescale 1ns/1ps
module tb_s2a_network_backend_csr_deadline;
    localparam logic [31:0] TEST_TIMEOUT = 32'd5;
    localparam logic [7:0] REG_CMD = 8'h00;
    localparam logic [7:0] REG_ERROR_CODE = 8'h08;
    localparam logic [7:0] REG_TIMEOUT = 8'h28;

    logic clk = 1'b0;
    logic hard_reset = 1'b1;
    logic csr_valid = 1'b0;
    logic csr_write = 1'b0;
    logic [7:0] csr_addr = 8'd0;
    logic [31:0] csr_wdata = 32'd0;
    logic [31:0] csr_rdata;
    logic csr_ready;
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
    logic mem_ready = 1'b0;
    logic [31:0] mem_rdata = 32'd0;
    logic [2:0] mem_error_code = 3'd0;

    always #5 clk = ~clk;

    initial begin
        #100000;
        $fatal(1, "deadline 联合自检超时");
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
        .busy(busy), .done(done), .error(error), .pl_owns_buffers(buffer_owner_pl),
        .head_output_valid(head_output_valid)
    );

    s2a_network_backend u_backend (
        .clk(clk), .hard_reset(hard_reset), .abort(backend_abort),
        .backend_start(backend_start), .buffer_owner_pl(buffer_owner_pl),
        .input_base_address(32'h0000_0000), .input_length_bytes(32'd519168),
        .weight_package_base_address(32'h0010_0000),
        .weight_package_length_bytes(32'd5903100),
        .mem_valid(mem_valid), .mem_write(mem_write), .mem_addr(mem_addr),
        .mem_wdata(mem_wdata), .mem_rstrb(mem_rstrb), .mem_wstrb(mem_wstrb),
        .mem_ready(mem_ready), .mem_rdata(mem_rdata), .mem_error_code(mem_error_code),
        .backend_memory_error_valid(backend_memory_error_valid),
        .backend_memory_error_code(backend_memory_error_code),
        .operator_result_valid(operator_result_valid),
        .operator_error_code(operator_error_code)
    );

    task automatic write_csr(input logic [7:0] address, input logic [31:0] value);
        begin
            @(negedge clk);
            if (!csr_ready)
                $fatal(1, "CSR write 未 ready：addr=%02h data=%08h",
                       address, value);
            csr_valid = 1'b1;
            csr_write = 1'b1;
            csr_addr = address;
            csr_wdata = value;
            @(posedge clk);
            #1;
            if (!csr_ready)
                $fatal(1, "CSR write handshake 未被接受：addr=%02h data=%08h",
                       address, value);
            @(negedge clk);
            csr_valid = 1'b0;
            csr_write = 1'b0;
            csr_addr = 8'd0;
            csr_wdata = 32'd0;
        end
    endtask

    task automatic reset_design;
        integer reset_wait_index;
        logic reset_cleared;
        begin
            @(negedge clk);
            hard_reset = 1'b1;
            csr_valid = 1'b0;
            csr_write = 1'b0;
            repeat (2) @(posedge clk);
            #1;
            @(negedge clk);
            hard_reset = 1'b0;
            reset_cleared = 1'b0;
            for (reset_wait_index = 0; reset_wait_index < 4; reset_wait_index = reset_wait_index + 1) begin
                @(posedge clk);
                #1;
                if (!backend_abort && !busy && !done && !error && !buffer_owner_pl) begin
                    reset_cleared = 1'b1;
                    break;
                end
            end
            if (!reset_cleared)
                $fatal(1, "CSR/backend reset 未在 4 个时钟内清除 abort/busy/status");
        end
    endtask

    task automatic start_transaction;
        integer elapsed_wait_index;
        logic deadline_preedge_reached;
        begin
            write_csr(REG_TIMEOUT, TEST_TIMEOUT);
            if (u_csr.timeout_cycles != TEST_TIMEOUT)
                $fatal(1, "timeout CSR 未写入：期望=%0d 实际=%0d",
                       TEST_TIMEOUT, u_csr.timeout_cycles);
            write_csr(REG_CMD, 32'd1);
            if (!backend_start || !busy || !buffer_owner_pl || error)
                $fatal(1, "CSR 未接受合法 start：backend_start=%b busy=%b owner=%b error=%b code=%0d timeout=%0d",
                       backend_start, busy, buffer_owner_pl, error,
                       u_csr.error_code, u_csr.timeout_cycles);
            // 此 bench 只隔离 CSR deadline 接口，不推进 descriptor 网络或内存模型。
            force u_backend.state = u_backend.ST_WAIT_CONV;
            force u_backend.selected_result_valid = 1'b0;
            #1;
            if (!busy || error || operator_result_valid || backend_memory_error_valid)
                $fatal(1, "冻结 backend 后未保持无事件 busy：busy=%b error=%b operator_valid=%b memory_error=%b code=%0d",
                       busy, error, operator_result_valid,
                       backend_memory_error_valid, u_csr.error_code);
            deadline_preedge_reached = 1'b0;
            for (elapsed_wait_index = 0;
                 elapsed_wait_index < (TEST_TIMEOUT + 2);
                 elapsed_wait_index = elapsed_wait_index + 1) begin
                @(negedge clk);
                if (u_csr.elapsed_cycles == (TEST_TIMEOUT - 32'd1)) begin
                    deadline_preedge_reached = 1'b1;
                    break;
                end
                if (!busy || done || error)
                    $fatal(1, "busy 在 deadline 前终止：elapsed=%0d busy=%b done=%b error=%b code=%0d start=%b abort=%b",
                           u_csr.elapsed_cycles, busy, done, error,
                           u_csr.error_code, backend_start, backend_abort);
            end
            if (!deadline_preedge_reached)
                $fatal(1, "elapsed 未到 deadline 前一拍：limit=%0d elapsed=%0d busy=%b done=%b error=%b code=%0d start=%b owner=%b abort=%b",
                       TEST_TIMEOUT + 2, u_csr.elapsed_cycles, busy, done, error,
                       u_csr.error_code, backend_start, buffer_owner_pl, backend_abort);
        end
    endtask

    initial begin
        reset_design();

        start_transaction();
        release u_backend.selected_result_valid;
        force u_backend.state = u_backend.ST_DISPATCH;
        force u_backend.layer_cursor = 6'd37;
        force u_backend.output_element_index = 32'd0;
        #1;
        if (!busy || (u_csr.elapsed_cycles != (TEST_TIMEOUT - 32'd1)) ||
            !operator_result_valid || (operator_error_code != 3'd0))
            $fatal(1, "deadline 同沿的全网完成事件未在采样前有效");
        @(posedge clk);
        #1;
        if (!done || error || !head_output_valid || busy || buffer_owner_pl)
            $fatal(1, "CSR 未在 deadline 同沿优先接受全网完成事件");
        release u_backend.state;
        release u_backend.layer_cursor;
        release u_backend.output_element_index;
        release u_backend.selected_result_valid;

        reset_design();
        start_transaction();
        force u_backend.selected_result_valid = 1'b1;
        force u_backend.selected_result_error = 3'd4;
        #1;
        if (!busy || (u_csr.elapsed_cycles != (TEST_TIMEOUT - 32'd1)) ||
            !operator_result_valid || (operator_error_code != 3'd4))
            $fatal(1, "已知错误码 4 未作为 combinational deadline 事件透传");
        @(posedge clk);
        #1;
        if (done || !error || busy || buffer_owner_pl)
            $fatal(1, "CSR 未在 deadline 同沿优先接受后端错误事件");
        csr_valid = 1'b1;
        csr_write = 1'b0;
        csr_addr = REG_ERROR_CODE;
        #1;
        if (csr_rdata[2:0] != 3'd4)
            $fatal(1, "CSR 未保存已知错误码 4");
        csr_valid = 1'b0;
        release u_backend.state;
        release u_backend.selected_result_valid;
        release u_backend.selected_result_error;

        $display("PASS: backend/CSR deadline 同沿完成与错误，错误码 4 透传");
        $finish;
    end
endmodule
