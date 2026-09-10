`timescale 1ns/1ps

module tb_counter;

    logic clk;
    logic en;
    logic rst;
    logic [2:0] count;

    // 产生周期为 10 ns 的时钟
    always #5 clk = ~clk;

    // 实例化被测试的计数器
    counter #(
        .WIDTH(3),
        .MAX_COUNT(5),
        .WRAP_ON_OVERFLOW(1'b0)
    ) dut (
        .clk(clk),
        .en(en),
        .rst(rst),
        .count(count)
    );

    initial begin
        // 初始化
        clk = 1'b0;
        rst = 1'b1;
        en = 1'b0;

        // 测试复位
        @(posedge clk);
        #1;
        if (count !== 3'd0)
            $error("复位测试失败");

        // 释放复位，但关闭使能
        rst = 1'b0;
        en = 1'b0;

        @(posedge clk);
        #1;
        if (count !== 3'd0)
            $error("使能关闭测试失败");

        // 开启计数，预期为 1
        en = 1'b1;

        @(posedge clk);
        #1;
        if (count !== 3'd1)
            $error("计数 1 测试失败");

        @(posedge clk);
        #1;
        if (count !== 3'd2)
            $error("计数 2 测试失败");

        @(posedge clk);
        #1;
        if (count !== 3'd3)
            $error("计数 3 测试失败");

        @(posedge clk);
        #1;
        if (count !== 3'd4)
            $error("计数 4 测试失败");

        @(posedge clk);
        #1;
        if (count !== 3'd5)
            $error("计数 5 测试失败");

        // 测试溢出回绕
        @(posedge clk);
        #1;
        if (count !== 3'd5)
            $error("溢出回绕测试失败");

        $display("计数器测试完成");
        
        // 连续三个时钟周期检查 count 是否保持为 5
            repeat (3) begin
                @(posedge clk);
                #1;
            
                if (count !== 3'd5)
                    $error("不回绕保持测试失败");
            end

        $finish;
    end

endmodule