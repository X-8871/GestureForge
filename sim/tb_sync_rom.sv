`timescale 1ns / 1ps

module tb_sync_rom;

    logic clk;
    logic rst;
    logic rd_en;
    logic [1:0] rd_addr;
    logic [7:0] rd_data;
    logic rd_valid;

    sync_rom #(
        .ADDR_WIDTH(2),
        .DATA_WIDTH(8)
    ) dut (
        .clk(clk),
        .rst(rst),
        .rd_en(rd_en),
        .rd_addr(rd_addr),
        .rd_data(rd_data),
        .rd_valid(rd_valid)
    );

    always #5 clk = ~clk;

    initial begin
        clk = 1'b0;
        rst = 1'b1;
        rd_en = 1'b0;
        rd_addr = 2'b00;

        // 复位两个时钟周期
        repeat (2) @(posedge clk);
        #1;

        if (rd_data !== 8'h00 || rd_valid !== 1'b0)
            $error("复位测试失败");

        rst = 1'b0;

        // 读取地址 0
        @(negedge clk);
        rd_en = 1'b1;
        rd_addr = 2'd0;

        @(posedge clk);
        #1;

        if (rd_data !== 8'h11 || rd_valid !== 1'b1)
            $error("地址 0 读取失败");

        // 跳变读取地址 2
        @(negedge clk);
        rd_addr = 2'd2;

        @(posedge clk);
        #1;

        if (rd_data !== 8'h33 || rd_valid !== 1'b1)
            $error("地址 2 读取失败");

        // 读取地址 3
        @(negedge clk);
        rd_addr = 2'd3;

        @(posedge clk);
        #1;

        if (rd_data !== 8'h44 || rd_valid !== 1'b1)
            $error("地址 3 读取失败");

        // 关闭读使能
        @(negedge clk);
        rd_en = 1'b0;

        @(posedge clk);
        #1;

        if (rd_valid !== 1'b0)
            $error("rd_valid 关闭失败");

        $display("同步 ROM 仿真测试完成");
        $finish;
    end

endmodule