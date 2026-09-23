// 按 manifest 派生向量验证 G0 memory testbench model。
module tb_s2a_memory_model;
    logic clk;
    logic reset;
    logic buffer_owner_pl;
    logic fault_inject_valid;
    logic [2:0] fault_inject_code;
    logic mem_valid;
    logic mem_write;
    logic [31:0] mem_addr;
    logic [31:0] mem_wdata;
    logic [3:0] mem_rstrb;
    logic [3:0] mem_wstrb;
    logic mem_ready;
    logic [31:0] mem_rdata;
    logic [2:0] mem_error_code;
    logic model_initialized;

    logic [31:0] fields [0:13];
    integer vector_fd;
    integer scan_result;
    integer vector_index;
    integer mode;
    integer category;
    integer expected_class;
    integer expected_error;
    integer expected_stall;
    integer abort_cycles;
    integer cycle_index;
    integer total_accepted;
    integer random_accepted;
    integer directed_accepted;
    integer invalid_accepted;
    integer fault_accepted;
    integer cancelled_count;
    integer bad_argument_count;
    integer bad_range_count;
    integer accepted_by_class [0:3];
    integer random_by_class [0:3];
    integer category_counts [0:3];
    logic [31:0] observed_rdata;
    logic [2:0] observed_error;
    string vector_path;

    s2a_memory_model dut (
        .clk(clk),
        .reset(reset),
        .buffer_owner_pl(buffer_owner_pl),
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

    always #5 clk = ~clk;

    task automatic fail(input string message);
        begin
            $display("FAIL: %s", message);
            $fatal(1);
        end
    endtask

    task automatic check_stalled_cycle(input integer expected_class_value);
        begin
            #1;
            if (dut.request_class !== expected_class_value) begin
                $display("FAIL: vector=%0d request class got=%0d exp=%0d",
                         vector_index, dut.request_class, expected_class_value);
                $fatal(1);
            end
            if ((mem_ready !== 1'b0) || (mem_error_code !== 3'd0) ||
                (mem_rdata !== 32'd0)) begin
                $display("FAIL: vector=%0d expected stalled quiet outputs ready=%b error=%0d rdata=%h",
                         vector_index, mem_ready, mem_error_code, mem_rdata);
                $fatal(1);
            end
        end
    endtask

    task automatic run_transfer;
        integer low_cycle;
        begin
            @(negedge clk);
            reset = 1'b0;
            buffer_owner_pl = 1'b1;
            mem_valid = 1'b1;
            mem_write = fields[3][0];
            mem_addr = fields[4];
            mem_wdata = fields[5];
            mem_rstrb = fields[6][3:0];
            mem_wstrb = fields[7][3:0];
            fault_inject_valid = fields[8][0];
            fault_inject_code = fields[9][2:0];
            expected_error = fields[10];
            expected_stall = fields[12];
            for (low_cycle = 0; low_cycle <= expected_stall;
                 low_cycle = low_cycle + 1) begin
                #1;
                if (dut.request_class !== expected_class) begin
                    $display("FAIL: vector=%0d class got=%0d exp=%0d",
                             vector_index, dut.request_class, expected_class);
                    $fatal(1);
                end
                if (low_cycle < expected_stall) begin
                    if ((mem_ready !== 1'b0) || (mem_error_code !== 3'd0) ||
                        (mem_rdata !== 32'd0)) begin
                        $display("FAIL: vector=%0d stall=%0d/%0d ready=%b error=%0d rdata=%h",
                                 vector_index, low_cycle, expected_stall,
                                 mem_ready, mem_error_code, mem_rdata);
                        $fatal(1);
                    end
                    @(posedge clk);
                    @(negedge clk);
                end else begin
                    if (mem_ready !== 1'b1) begin
                        $display("FAIL: vector=%0d expected ready-high after %0d low cycles",
                                 vector_index, expected_stall);
                        $fatal(1);
                    end
                    observed_error = mem_error_code;
                    observed_rdata = mem_rdata;
                    @(posedge clk);
                    if ((observed_error !== fields[10][2:0]) ||
                        (observed_rdata !== fields[11])) begin
                        $display("FAIL: vector=%0d class=%0d error got=%0d exp=%0d data got=%h exp=%h",
                                 vector_index, expected_class, observed_error,
                                 fields[10][2:0], observed_rdata, fields[11]);
                        $fatal(1);
                    end
                    total_accepted = total_accepted + 1;
                    accepted_by_class[expected_class] = accepted_by_class[expected_class] + 1;
                    if (category == 0) begin
                        random_accepted = random_accepted + 1;
                        random_by_class[expected_class] = random_by_class[expected_class] + 1;
                    end else if (category == 1) begin
                        directed_accepted = directed_accepted + 1;
                    end else if (category == 2) begin
                        invalid_accepted = invalid_accepted + 1;
                    end else if (category == 3) begin
                        fault_accepted = fault_accepted + 1;
                    end
                    if (observed_error == 3'd1) bad_argument_count = bad_argument_count + 1;
                    if (observed_error == 3'd2) bad_range_count = bad_range_count + 1;
                    @(negedge clk);
                    mem_valid = 1'b0;
                    fault_inject_valid = 1'b0;
                    #1;
                    if ((mem_ready !== 1'b0) || (mem_error_code !== 3'd0) ||
                        (mem_rdata !== 32'd0)) begin
                        fail("valid 撤销后 ready/error/read data 未回到空闲值");
                    end
                end
            end
        end
    endtask

    task automatic run_cancel;
        integer low_cycle;
        begin
            @(negedge clk);
            reset = 1'b0;
            buffer_owner_pl = 1'b1;
            mem_valid = 1'b1;
            mem_write = 1'b1;
            mem_addr = fields[4];
            mem_wdata = fields[5];
            mem_rstrb = 4'b0000;
            mem_wstrb = fields[7][3:0];
            fault_inject_valid = 1'b0;
            fault_inject_code = 3'd0;
            expected_stall = fields[12];
            abort_cycles = fields[13];
            for (low_cycle = 0; low_cycle < abort_cycles;
                 low_cycle = low_cycle + 1) begin
                check_stalled_cycle(3);
                @(posedge clk);
                @(negedge clk);
            end
            if (fields[0] == 2) begin
                reset = 1'b1;
                mem_valid = 1'b0;
                #1;
                if ((mem_ready !== 1'b0) || (mem_error_code !== 3'd0))
                    fail("reset 期间 memory model ready/error 必须清零");
                @(posedge clk);
                @(negedge clk);
                reset = 1'b0;
            end else begin
                mem_valid = 1'b0;
                #1;
                if ((mem_ready !== 1'b0) || (mem_error_code !== 3'd0))
                    fail("撤销 valid 后 pending 请求不得握手");
                @(posedge clk);
            end
            cancelled_count = cancelled_count + 1;
        end
    endtask

    initial begin
        clk = 1'b0;
        reset = 1'b1;
        buffer_owner_pl = 1'b0;
        fault_inject_valid = 1'b0;
        fault_inject_code = 3'd0;
        mem_valid = 1'b0;
        mem_write = 1'b0;
        mem_addr = 32'd0;
        mem_wdata = 32'd0;
        mem_rstrb = 4'd0;
        mem_wstrb = 4'd0;
        total_accepted = 0;
        random_accepted = 0;
        directed_accepted = 0;
        invalid_accepted = 0;
        fault_accepted = 0;
        cancelled_count = 0;
        bad_argument_count = 0;
        bad_range_count = 0;
        vector_index = 0;
        for (cycle_index = 0; cycle_index < 4; cycle_index = cycle_index + 1) begin
            accepted_by_class[cycle_index] = 0;
            random_by_class[cycle_index] = 0;
        end
        for (cycle_index = 0; cycle_index < 4; cycle_index = cycle_index + 1)
            category_counts[cycle_index] = 0;

        wait(model_initialized === 1'b1);
        @(negedge clk);
        reset = 1'b0;
        buffer_owner_pl = 1'b0;
        mem_valid = 1'b1;
        #1;
        if ((mem_ready !== 1'b0) || (mem_error_code !== 3'd0))
            fail("无 PL buffer owner 时 ready/error 必须为零");
        @(posedge clk);
        @(negedge clk);
        reset = 1'b1;
        buffer_owner_pl = 1'b1;
        #1;
        if ((mem_ready !== 1'b0) || (mem_error_code !== 3'd0))
            fail("reset 时 ready/error 必须为零");
        @(posedge clk);
        @(negedge clk);
        reset = 1'b0;
        buffer_owner_pl = 1'b0;
        mem_valid = 1'b0;

        vector_path = "vectors.dat";
        vector_fd = $fopen(vector_path, "r");
        if (vector_fd == 0) fail("无法打开 TEMP 内向量文件");
        while (!$feof(vector_fd)) begin
            scan_result = $fscanf(vector_fd,
                "%h %h %h %h %h %h %h %h %h %h %h %h %h %h",
                fields[0], fields[1], fields[2], fields[3], fields[4],
                fields[5], fields[6], fields[7], fields[8], fields[9],
                fields[10], fields[11], fields[12], fields[13]);
            if (scan_result == -1) break;
            if (scan_result != 14) begin
                $display("FAIL: vector=%0d field count=%0d", vector_index, scan_result);
                $fatal(1);
            end
            mode = fields[0];
            category = fields[1];
            expected_class = fields[2];
            if (expected_class < 0 || expected_class > 3)
                fail("未知 memory request class");
            if (mode == 0) begin
                run_transfer();
                category_counts[category] = category_counts[category] + 1;
            end else if ((mode == 1) || (mode == 2)) begin
                run_cancel();
            end else begin
                fail("未知 memory vector mode");
            end
            vector_index = vector_index + 1;
        end
        $fclose(vector_fd);

        for (cycle_index = 0; cycle_index < 4; cycle_index = cycle_index + 1) begin
            if (random_by_class[cycle_index] < 1000) begin
                $display("FAIL: class=%0d random transactions=%0d",
                         cycle_index, random_by_class[cycle_index]);
                $fatal(1);
            end
        end
        if ((cancelled_count != 2) || (bad_argument_count == 0) ||
            (bad_range_count == 0) || (fault_accepted < 4)) begin
            $display("FAIL: cancelled=%0d BAD_ARGUMENT=%0d BAD_RANGE=%0d fault=%0d",
                     cancelled_count, bad_argument_count, bad_range_count, fault_accepted);
            $fatal(1);
        end

        @(negedge clk);
        buffer_owner_pl = 1'b0;
        mem_valid = 1'b0;
        #1;
        if ((mem_ready !== 1'b0) || (mem_error_code !== 3'd0))
            fail("测试结束后空闲 ready/error 必须清零");
        $display("PASS: accepted=%0d read_input=%0d read_weights=%0d read_feature=%0d write_feature=%0d random=%0d directed=%0d invalid=%0d fault=%0d cancelled=%0d BAD_ARGUMENT=%0d BAD_RANGE=%0d",
                 total_accepted, accepted_by_class[0], accepted_by_class[1],
                 accepted_by_class[2], accepted_by_class[3], random_accepted,
                 directed_accepted, invalid_accepted, fault_accepted,
                 cancelled_count, bad_argument_count, bad_range_count);
        $finish;
    end
endmodule
