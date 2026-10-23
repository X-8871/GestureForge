`timescale 1ns/1ps

module tb_s4b_preproc_pixel;
    logic clk = 1'b0;
    logic rst_n = 1'b0;
    logic in_valid = 1'b0;
    logic in_ready;
    logic [7:0] p00 = 8'd0;
    logic [7:0] p01 = 8'd0;
    logic [7:0] p10 = 8'd0;
    logic [7:0] p11 = 8'd0;
    logic [63:0] wx0 = 64'd0;
    logic [63:0] wx1 = 64'd0;
    logic [63:0] wy0 = 64'd0;
    logic [63:0] wy1 = 64'd0;
    logic busy;
    logic out_valid;
    logic out_ready = 1'b0;
    logic [7:0] out_q;
    logic error_valid;
    logic error_ready = 1'b0;
    logic [2:0] error_code;
    logic alu_start = 1'b0;
    logic alu_add_op = 1'b0;
    logic [63:0] alu_operand_a = 64'd0;
    logic [63:0] alu_operand_b = 64'd0;
    logic alu_busy;
    logic alu_done;
    logic alu_error;
    logic [1:0] alu_error_code;
    logic [63:0] alu_result;

    logic [7:0] expected_mem [0:9];
    logic [7:0] p00_mem [0:9];
    logic [7:0] p01_mem [0:9];
    logic [7:0] p10_mem [0:9];
    logic [7:0] p11_mem [0:9];
    logic [63:0] wx0_mem [0:9];
    logic [63:0] wx1_mem [0:9];
    logic [63:0] wy0_mem [0:9];
    logic [63:0] wy1_mem [0:9];
    integer cycle_count = 0;
    integer transaction_start_cycle = 0;
    integer first_valid_cycle = 0;
    integer output_handshake_cycle = 0;
    integer alu_start_cycle = 0;
    integer alu_done_cycle = 0;
    integer fd;
    integer scan_count;
    integer index;
    integer waited;
    integer stable_count;
    integer fp64_fd;
    integer fp64_scan_count;
    integer fp64_vector_count;
    integer fp64_vector_index;
    integer fp64_expected_error;
    integer fp64_expected_code;
    integer fp64_pass_count;
    logic fp64_is_add;
    logic [63:0] fp64_a;
    logic [63:0] fp64_b;
    logic [63:0] fp64_expected_result;

    always #5 clk = ~clk;
    always @(posedge clk) cycle_count <= cycle_count + 1;

    s4b_preproc_pixel dut (
        .clk(clk),
        .rst_n(rst_n),
        .in_valid(in_valid),
        .in_ready(in_ready),
        .p00(p00),
        .p01(p01),
        .p10(p10),
        .p11(p11),
        .wx0(wx0),
        .wx1(wx1),
        .wy0(wy0),
        .wy1(wy1),
        .busy(busy),
        .out_valid(out_valid),
        .out_ready(out_ready),
        .out_q(out_q),
        .error_valid(error_valid),
        .error_ready(error_ready),
        .error_code(error_code)
    );

    s4b_preproc_fp64 alu_dut (
        .clk(clk),
        .rst_n(rst_n),
        .start(alu_start),
        .add_op(alu_add_op),
        .operand_a(alu_operand_a),
        .operand_b(alu_operand_b),
        .busy(alu_busy),
        .done(alu_done),
        .error(alu_error),
        .error_code(alu_error_code),
        .result(alu_result)
    );

    task automatic send_input(
        input logic [7:0] a00,
        input logic [7:0] a01,
        input logic [7:0] a10,
        input logic [7:0] a11,
        input logic [63:0] ax0,
        input logic [63:0] ax1,
        input logic [63:0] ay0,
        input logic [63:0] ay1
    );
        begin
            @(negedge clk);
            while (!in_ready)
                @(negedge clk);
            p00 = a00;
            p01 = a01;
            p10 = a10;
            p11 = a11;
            wx0 = ax0;
            wx1 = ax1;
            wy0 = ay0;
            wy1 = ay1;
            in_valid = 1'b1;
            @(posedge clk);
            #1;
            transaction_start_cycle = cycle_count;
            in_valid = 1'b0;
        end
    endtask

    task automatic inject_busy_input;
        begin
            @(negedge clk);
            if (!busy || in_ready)
                $fatal(1, "忙期间握手门禁错误");
            p00 = 8'd99;
            p01 = 8'd99;
            p10 = 8'd99;
            p11 = 8'd99;
            wx0 = 64'h3ff0000000000000;
            wx1 = 64'd0;
            wy0 = 64'h3ff0000000000000;
            wy1 = 64'd0;
            in_valid = 1'b1;
            @(posedge clk);
            #1;
            @(negedge clk);
            in_valid = 1'b0;
        end
    endtask

    task automatic wait_output(input logic [7:0] expected_value, input integer vector_index);
        logic [7:0] held_value;
        begin
            out_ready = 1'b0;
            waited = 0;
            while (!out_valid && waited < 1000) begin
                @(negedge clk);
                waited = waited + 1;
            end
            if (!out_valid)
                $fatal(1, "输出超时，vector=%0d", vector_index);
            first_valid_cycle = cycle_count;
            if (error_valid)
                $fatal(1, "输出同时出现错误，vector=%0d", vector_index);
            if (out_q !== expected_value)
                $fatal(1, "量化不一致，vector=%0d got=%0d expected=%0d", vector_index, out_q, expected_value);
            held_value = out_q;
            stable_count = 0;
            repeat (3) begin
                @(negedge clk);
                if (!out_valid || out_q !== held_value || in_ready)
                    $fatal(1, "输出背压期间状态未保持，vector=%0d", vector_index);
                stable_count = stable_count + 1;
            end
            out_ready = 1'b1;
            @(posedge clk);
            #1;
            output_handshake_cycle = cycle_count;
            out_ready = 1'b0;
            if (out_valid || !in_ready)
                $fatal(1, "输出握手后未回到空闲，vector=%0d", vector_index);
            $display("VECTOR_PASS index=%0d q=%0d cycles_to_valid=%0d cycles_to_handshake=%0d forced_backpressure_cycles=3",
                     vector_index, held_value, first_valid_cycle - transaction_start_cycle,
                     output_handshake_cycle - transaction_start_cycle);
        end
    endtask

    task automatic expect_coefficient_error(input logic [63:0] bad_weight, input integer case_index);
        begin
            send_input(8'd1, 8'd2, 8'd3, 8'd4,
                       bad_weight, 64'd0, 64'h3ff0000000000000, 64'd0);
            waited = 0;
            while (!error_valid && waited < 10) begin
                @(negedge clk);
                waited = waited + 1;
            end
            if (!error_valid || error_code != 3'd1 || out_valid || in_ready)
                $fatal(1, "非法系数错误状态错误，case=%0d", case_index);
            repeat (3) begin
                @(negedge clk);
                if (!error_valid || error_code != 3'd1 || in_ready)
                    $fatal(1, "错误背压期间状态未保持，case=%0d", case_index);
            end
            error_ready = 1'b1;
            @(posedge clk);
            #1;
            error_ready = 1'b0;
            if (error_valid || !in_ready)
                $fatal(1, "错误握手后未回到空闲，case=%0d", case_index);
            $display("COEFFICIENT_ERROR_PASS case=%0d", case_index);
        end
    endtask

    task automatic check_alu_case(
        input logic is_add,
        input logic [63:0] a,
        input logic [63:0] b,
        input logic [63:0] expected_value,
        input integer expected_error,
        input integer expected_code,
        input integer case_index
    );
        begin
            @(negedge clk);
            while (alu_busy)
                @(negedge clk);
            alu_add_op = is_add;
            alu_operand_a = a;
            alu_operand_b = b;
            alu_start = 1'b1;
            @(posedge clk);
            #1;
            alu_start_cycle = cycle_count;
            alu_start = 1'b0;
            waited = 0;
            while (!alu_done && waited < 100) begin
                @(negedge clk);
                waited = waited + 1;
            end
            alu_done_cycle = cycle_count;
            if (alu_done !== 1'b1)
                $fatal(1, "FP64算术未完成，case=%0d", case_index);
            if (alu_error !== (expected_error != 0) || alu_error_code !== expected_code[1:0])
                $fatal(1, "FP64错误状态不一致，case=%0d error=%0d/%0d code=%0d/%0d",
                       case_index, alu_error, expected_error, alu_error_code, expected_code);
            if (alu_result !== expected_value)
                $fatal(1, "FP64位型不一致，case=%0d got=%h expected=%h", case_index, alu_result, expected_value);
            fp64_pass_count = fp64_pass_count + 1;
            $display("FP64_VECTOR_PASS index=%0d add=%0d result=%h error=%0d code=%0d cycles_start_accept_to_done_assert=%0d",
                     case_index, is_add, alu_result, alu_error, alu_error_code,
                     alu_done_cycle - alu_start_cycle);
        end
    endtask

    initial begin
        #1000000;
        $fatal(1, "TB全局watchdog超时");
    end

    initial begin
        #30;
        rst_n = 1'b1;
        fd = $fopen("preproc_vectors.hex", "r");
        if (fd == 0)
            $fatal(1, "无法打开preproc_vectors.hex");
        for (index = 0; index < 10; index = index + 1) begin
            scan_count = $fscanf(fd, "%h %h %h %h %h %h %h %h %h\n",
                                 expected_mem[index], p00_mem[index], p01_mem[index],
                                 p10_mem[index], p11_mem[index], wx0_mem[index],
                                 wx1_mem[index], wy0_mem[index], wy1_mem[index]);
            if (scan_count != 9)
                $fatal(1, "测试向量字段不足，index=%0d count=%0d", index, scan_count);
        end
        $fclose(fd);

        send_input(p00_mem[0], p01_mem[0], p10_mem[0], p11_mem[0],
                   wx0_mem[0], wx1_mem[0], wy0_mem[0], wy1_mem[0]);
        repeat (5) @(posedge clk);
        @(negedge clk);
        rst_n = 1'b0;
        repeat (2) @(posedge clk);
        #1;
        if (busy || out_valid || error_valid || !in_ready)
            $fatal(1, "忙态复位未清空事务");
        @(negedge clk);
        rst_n = 1'b1;
        send_input(p00_mem[0], p01_mem[0], p10_mem[0], p11_mem[0],
                   wx0_mem[0], wx1_mem[0], wy0_mem[0], wy1_mem[0]);
        inject_busy_input();
        wait_output(expected_mem[0], 0);

        for (index = 1; index < 10; index = index + 1) begin
            send_input(p00_mem[index], p01_mem[index], p10_mem[index], p11_mem[index],
                       wx0_mem[index], wx1_mem[index], wy0_mem[index], wy1_mem[index]);
            wait_output(expected_mem[index], index);
        end

        expect_coefficient_error(64'hbfe0000000000000, 0);
        expect_coefficient_error(64'h3c90000000000000, 1);
        expect_coefficient_error(64'h0000000000000001, 2);
        expect_coefficient_error(64'h4000000000000000, 3);
        expect_coefficient_error(64'h7ff0000000000000, 4);
        expect_coefficient_error(64'h7ff8000000000001, 5);

        fp64_fd = $fopen("fp64_vectors.hex", "r");
        if (fp64_fd == 0)
            $fatal(1, "无法打开fp64_vectors.hex");
        fp64_scan_count = $fscanf(fp64_fd, "%d\n", fp64_vector_count);
        if (fp64_scan_count != 1 || fp64_vector_count < 1)
            $fatal(1, "FP64测试向量数量头错误 count=%0d", fp64_vector_count);
        fp64_pass_count = 0;
        for (fp64_vector_index = 0; fp64_vector_index < fp64_vector_count; fp64_vector_index = fp64_vector_index + 1) begin
            fp64_scan_count = $fscanf(fp64_fd, "%h %h %h %h %h %h\n",
                                      fp64_is_add, fp64_a, fp64_b, fp64_expected_result,
                                      fp64_expected_error, fp64_expected_code);
            if (fp64_scan_count != 6)
                $fatal(1, "FP64测试向量字段不足，index=%0d count=%0d",
                       fp64_vector_index, fp64_scan_count);
            check_alu_case(fp64_is_add, fp64_a, fp64_b, fp64_expected_result,
                           fp64_expected_error, fp64_expected_code, fp64_vector_index);
        end
        $fclose(fp64_fd);
        if (fp64_pass_count != fp64_vector_count)
            $fatal(1, "FP64测试向量总数不符 got=%0d expected=%0d",
                   fp64_pass_count, fp64_vector_count);

        $display("TEST_PASS vectors=10 coefficient_errors=6 fp64_cases=%0d busy_reset=PASS backpressure=PASS",
                 fp64_pass_count);
        $finish;
    end
endmodule
