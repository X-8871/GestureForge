`timescale 1ns/1ps
module tb_s2c_rtl01_tile16_lookup;
    logic clk = 1'b0;
    logic [95:0] tile_value;
    logic [98:0] full_tile_value;

    always #5 clk = ~clk;

    s2b_conv_tile_engine #(.FROZEN_CONV_DESCRIPTOR(1'b1)) dut_frozen (
        .clk(clk),
        .hard_reset(1'b1)
    );

    s2b_conv_tile_engine dut_generic (
        .clk(clk),
        .hard_reset(1'b1)
    );

    initial begin
        #1;
        if (dut_frozen.TILE_EDGE != 16 || dut_generic.TILE_EDGE != 8) begin
            $fatal(1, "冻结实例与通用实例tile边长错误");
        end

        tile_value = dut_frozen.frozen_conv_tile_lookup_16({32'd0, 5'd16, 5'd16});
        if (tile_value !== {32'd33, 32'd33, 32'd3267}) begin
            $fatal(1, "layer0 stride2+padding完整tile查表错误");
        end

        tile_value = dut_frozen.frozen_conv_tile_lookup_16({32'd35, 5'd16, 5'd16});
        if (tile_value !== {32'd18, 32'd18, 32'd124416}) begin
            $fatal(1, "layer35完整tile查表错误");
        end

        tile_value = dut_frozen.frozen_conv_tile_lookup_16({32'd35, 5'd16, 5'd10});
        if (tile_value !== {32'd18, 32'd12, 32'd82944}) begin
            $fatal(1, "layer35右侧尾tile查表错误");
        end

        tile_value = dut_frozen.frozen_conv_tile_lookup_16({32'd35, 5'd10, 5'd16});
        if (tile_value !== {32'd12, 32'd18, 32'd82944}) begin
            $fatal(1, "layer35底部尾tile查表错误");
        end

        tile_value = dut_frozen.frozen_conv_tile_lookup_16({32'd35, 5'd10, 5'd10});
        if (tile_value !== {32'd12, 32'd12, 32'd55296}) begin
            $fatal(1, "layer35右下角尾tile查表错误");
        end

        full_tile_value = dut_frozen.frozen_full_tile_lookup_16(32'd35);
        if (full_tile_value !== {19'd18, 19'd18, 32'd324, 29'd124416}) begin
            $fatal(1, "layer35完整patch容量查表错误");
        end

        $display("PASS S2C-RTL01 RTL查表：layer0、layer35边缘尾块、generic8/frozen16");
        $finish;
    end
endmodule
