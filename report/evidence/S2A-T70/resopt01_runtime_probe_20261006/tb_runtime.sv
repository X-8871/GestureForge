`timescale 1ns/1ps
module tb_runtime;
    logic clk = 1'b0;
    always #5 clk = ~clk;
    initial begin
        $display("RUNTIME_PROBE initial");
        $fflush();
        #1;
        $display("PASS RUNTIME_PROBE");
        $fflush();
        $finish;
    end
endmodule