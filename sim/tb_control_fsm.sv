`timescale 1ns / 1ps

module tb_control_fsm;

    logic clk;
    logic rst;
    logic start;
    logic done;
    logic busy;

    control_fsm #(
        .PROCESS_CYCLES(3)
    ) dut (
        .clk(clk),
        .rst(rst),
        .start(start),
        .done(done),
        .busy(busy)
    );

    always #5 clk = ~clk;

    initial begin
        clk = 1'b0;
        rst = 1'b1;
        start = 1'b0;

        // 保持复位两个时钟周期
        repeat (2) @(posedge clk);
        #1;

        if (busy !== 1'b0 || done !== 1'b0)
            $error("复位测试失败");

        rst = 1'b0;

        // 第一次启动
        @(negedge clk);
        start = 1'b1;

        @(posedge clk);
        #1;

        if (busy !== 1'b1 || done !== 1'b0)
            $error("进入 PROCESS 状态失败");

        start = 1'b0;

        // 在 PROCESS 状态中再次启动，应该被忽略
        @(negedge clk);
        start = 1'b1;

        @(posedge clk);
        #1;

        if (busy !== 1'b1 || done !== 1'b0)
            $error("PROCESS 状态被错误打断");

        start = 1'b0;

        // 继续运行一个周期
        @(posedge clk);
        #1;

        if (busy !== 1'b1 || done !== 1'b0)
            $error("PROCESS 状态持续失败");

        // 处理完成，DONE 只保持一个周期
        @(posedge clk);
        #1;

        if (busy !== 1'b0 || done !== 1'b1)
            $error("DONE 状态或 done 信号错误");

        // DONE 返回 IDLE
        @(posedge clk);
        #1;

        if (busy !== 1'b0 || done !== 1'b0)
            $error("返回 IDLE 状态失败");

        $display("control_fsm 仿真测试完成");
        $finish;
    end

endmodule