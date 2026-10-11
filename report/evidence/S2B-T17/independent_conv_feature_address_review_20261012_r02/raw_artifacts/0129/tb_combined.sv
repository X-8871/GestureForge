// 两个完成标记都成立后才结束，任何子回归失败立即报告。
`timescale 1ns/1ps
module tb_combined;
wire feature_done,boundary_done;
tb_s2b_conv_feature_address feature_test(.done(feature_done));
tb_s2b_conv_validation boundary_test(.done(boundary_done));
initial begin wait(feature_done && boundary_done); $display("PASS BOTH_DONE feature=1 boundary=1"); $finish; end
initial begin #2000000; $fatal(1,"两个回归未完整结束"); end
endmodule
