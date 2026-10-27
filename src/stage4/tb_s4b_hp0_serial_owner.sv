// tb_s4b_hp0_serial_owner.sv —— 串行化 owner 自检 TB（冲突请求 / one-hot / 排空 / 轮转）
`timescale 1ns / 1ps

module tb_s4b_hp0_serial_owner;
    logic clk = 0, rstn = 0;
    logic req0 = 0, req1 = 0, rel0 = 0, rel1 = 0, in_flight0 = 0, in_flight1 = 0;
    logic gnt0, gnt1;
    logic [1:0] ledger_state;
    logic [0:0] owner_id;
    logic busy;

    int errors = 0;

    s4b_hp0_serial_owner dut (
        .clk(clk), .rstn(rstn),
        .req0(req0), .gnt0(gnt0), .rel0(rel0), .in_flight0(in_flight0),
        .req1(req1), .gnt1(gnt1), .rel1(rel1), .in_flight1(in_flight1),
        .ledger_state(ledger_state), .owner_id(owner_id), .busy(busy)
    );

    always #5 clk = ~clk;

    task automatic step(input int n); repeat (n) @(posedge clk); endtask

    // 全局不变量：任一周期不得双授权
    always @(posedge clk) if (rstn && (gnt0 && gnt1)) begin
        errors++; $display("[FAIL] one-hot violated: gnt0&gnt1 at once");
    end

    initial begin
        rstn = 0; step(3); rstn = 1; step(1);

        // 1) 双方同时请求 ⇒ 只授权一个（net 优先），且另一方保持排队
        req0 = 1; req1 = 1; step(2);
        if (!gnt1) begin errors++; $display("[FAIL] 冲突请求应优先 gnt1"); end
        if (gnt0)  begin errors++; $display("[FAIL] 冲突时 gnt0 不应同时有效"); end
        if (owner_id !== 1'b1) begin errors++; $display("[FAIL] owner_id 应为 1"); end

        // 2) net 在途 → 释放并排空 → 自动切到 preproc
        in_flight1 = 1; step(2); rel1 = 1; step(1); rel1 = 0; in_flight1 = 0; req1 = 0; step(6);
        if (!gnt0) begin errors++; $display("[FAIL] net 排空后应授权 preproc"); end
        if (gnt1)  begin errors++; $display("[FAIL] net 不应仍在授权"); end

        // 3) preproc 在途并释放 → 排空 → 若仍排队则回到 IDLE/再授权
        in_flight0 = 0; wait (gnt0); rel0 = 1; step(1); rel0 = 0; req1 = 0; req0 = 0; step(6);
        if (busy) begin errors++; $display("[FAIL] 双方都撤销后应为 IDLE"); end

        // 4) 单方请求 + 释放动作：rel 只能来自 owner（此处应无断言触发）
        req0 = 1; wait (gnt0); step(1);
        if (!gnt0) begin errors++; $display("[FAIL] 单方请求应获授权"); end
        rel0 = 1; step(1); rel0 = 0; req0 = 0; step(2);

        if (errors == 0) begin
            $display("[PASS] s4b_hp0_serial_owner：one-hot/冲突优先/排空切换/IDLE 全部符合");
            $finish(0);
        end else begin
            $display("[FAIL] 共 %0d 处不符", errors);
            $finish(1);
        end
    end
endmodule

