// 由独立 Python manifest 参考生成输入与期望值，逐条检查组合 RTL。
module tb_s2b_request_guard;
    logic mem_write;
    logic [31:0] mem_addr;
    logic [3:0] mem_rstrb, mem_wstrb;
    logic request_allowed;
    logic [31:0] physical_addr;
    logic [2:0] error_code;
    s2b_request_guard dut (.*);
    string vectors_path;
    integer fd, scanned, cases;
    integer expected_allowed, expected_error;
    logic [31:0] expected_physical;
    initial begin
        if (!$value$plusargs("VECTORS=%s", vectors_path)) $fatal(1, "缺少 VECTORS");
        fd = $fopen(vectors_path, "r");
        if (fd == 0) $fatal(1, "不能打开向量");
        cases = 0;
        while (!$feof(fd)) begin
            scanned = $fscanf(fd, "%h %h %h %h %h %h %h\n",
                              mem_write, mem_addr, mem_rstrb, mem_wstrb,
                              expected_allowed, expected_physical, expected_error);
            if (scanned != 7) $fatal(1, "向量格式错误 case=%0d scanned=%0d", cases, scanned);
            #1;
            if ((request_allowed !== 1'(expected_allowed)) ||
                (physical_addr !== expected_physical) ||
                (error_code !== 3'(expected_error)))
                $fatal(1, "case=%0d write=%0d addr=%h r=%h w=%h got=%0d/%h/%0d expected=%0d/%h/%0d",
                       cases, mem_write, mem_addr, mem_rstrb, mem_wstrb,
                       request_allowed, physical_addr, error_code,
                       expected_allowed, expected_physical, expected_error);
            cases++;
        end
        $fclose(fd);
        $display("PASS REQUEST_GUARD cases=%0d", cases);
        $finish;
    end
endmodule
