`timescale 1ns / 1ps

module tb_rom_controller;

    logic clk;
    logic rst;
    logic start;
    logic [1:0] start_addr;

    logic busy;
    logic done;
    logic [7:0] result_data;

    rom_controller #(
        .ADDR_WIDTH(2),
        .DATA_WIDTH(8),
        .DEPTH(4)
    ) dut (
        .clk(clk),
        .rst(rst),
        .start(start),
        .start_addr(start_addr),
        .busy(busy),
        .done(done),
        .result_data(result_data)
    );

    always #5 clk = ~clk;

    initial begin
        clk = 1'b0;
        rst = 1'b1;
        start = 1'b0;
        start_addr = 2'd0;

        // 复位两个时钟周期
        repeat (2) @(posedge clk);
        #1;

        if (busy !== 1'b0 || done !== 1'b0)
            $error("复位测试失败");

        rst = 1'b0;

        // 第一次读取地址 2
        @(negedge clk);
        start_addr = 2'd2;
        start = 1'b1;

        @(posedge clk);
        #1;

        if (busy !== 1'b1 || done !== 1'b0)
            $error("READ_REQ 状态测试失败");

        start = 1'b0;

        // 等待 ROM 返回数据
        @(posedge clk);
        #1;

        if (busy !== 1'b1 || done !== 1'b0)
            $error("WAIT_DATA 状态测试失败");

        // 读取完成，地址 2 对应 8'h33
        @(posedge clk);
        #1;

        if (busy !== 1'b0 ||
            done !== 1'b1 ||
            result_data !== 8'h33)
            $error("地址 2 读取结果错误");

        // DONE 返回 IDLE
        @(posedge clk);
        #1;

        if (busy !== 1'b0 || done !== 1'b0)
            $error("返回 IDLE 失败");

        // 第二次读取地址 3
        @(negedge clk);
        start_addr = 2'd3;
        start = 1'b1;

        @(posedge clk);
        #1;

        start = 1'b0;

        @(posedge clk);
        #1;

        @(posedge clk);
        #1;

        if (busy !== 1'b0 ||
            done !== 1'b1 ||
            result_data !== 8'h44)
            $error("地址 3 读取结果错误");

        @(posedge clk);
        #1;

        if (busy !== 1'b0 || done !== 1'b0)
            $error("第二次读取后返回 IDLE 失败");

        $display("rom_controller 集成仿真测试完成");
        $finish;
    end

endmodule