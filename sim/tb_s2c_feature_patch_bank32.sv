`timescale 1ns/1ps
module tb_s2c_feature_patch_bank32;
    localparam integer MAX_BYTES = 124416;
    localparam integer ADDR_WIDTH = 17;
    localparam integer LANES = 16;

    logic clk = 1'b0;
    logic rst;
    logic wr_en;
    logic [ADDR_WIDTH-1:0] wr_addr;
    logic [7:0] wr_data;
    logic rd_en;
    logic [LANES-1:0] rd_lane_active;
    logic [LANES*ADDR_WIDTH-1:0] rd_addr_flat;
    logic rd_valid;
    logic [LANES*8-1:0] rd_data_flat;
    logic [LANES-1:0] rd_lane_valid;
    logic rd_conflict;
    logic rd_bad_address;
    logic wr_bad_address;
    integer addr_i;
    integer lane_i;
    logic [LANES-1:0] expected_mask;

    always #5 clk = ~clk;

    s2c_feature_patch_bank32 dut (
        .clk(clk), .rst(rst),
        .wr_en(wr_en), .wr_addr(wr_addr), .wr_data(wr_data),
        .rd_en(rd_en), .rd_lane_active(rd_lane_active), .rd_addr_flat(rd_addr_flat),
        .rd_valid(rd_valid), .rd_data_flat(rd_data_flat),
        .rd_lane_valid(rd_lane_valid), .rd_conflict(rd_conflict),
        .rd_bad_address(rd_bad_address), .wr_bad_address(wr_bad_address)
    );

    function automatic logic [7:0] value_for(input integer address_value);
        value_for = (address_value * 13 + 7) & 255;
    endfunction

    task automatic check_read_window(
        input integer base_value,
        input integer step_value,
        input integer active_count
    );
        integer expected_address;
        begin
            @(negedge clk);
            rd_addr_flat = '0;
            rd_lane_active = '0;
            expected_mask = '0;
            for (lane_i = 0; lane_i < LANES; lane_i = lane_i + 1) begin
                if (lane_i < active_count) begin
                    expected_address = base_value + lane_i * step_value;
                    rd_addr_flat[lane_i*ADDR_WIDTH +: ADDR_WIDTH] = expected_address;
                    rd_lane_active[lane_i] = 1'b1;
                    expected_mask[lane_i] = 1'b1;
                end else begin
                    rd_addr_flat[lane_i*ADDR_WIDTH +: ADDR_WIDTH] = MAX_BYTES + lane_i;
                end
            end
            rd_en = 1'b1;
            #1;
            if (rd_conflict || rd_bad_address) begin
                $fatal(1, "合法active读窗口被判冲突或越界");
            end
            @(posedge clk);
            #1;
            if (!rd_valid || rd_lane_valid !== expected_mask) begin
                $fatal(1, "同步读响应或active lane valid不匹配");
            end
            for (lane_i = 0; lane_i < active_count; lane_i = lane_i + 1) begin
                expected_address = base_value + lane_i * step_value;
                if (rd_data_flat[lane_i*8 +: 8] !== value_for(expected_address)) begin
                    $display("lane=%0d addr=%0d expected=%0d actual=%0d", lane_i,
                        expected_address, value_for(expected_address), rd_data_flat[lane_i*8 +: 8]);
                    $fatal(1, "banked feature read data mismatch");
                end
            end
            @(negedge clk);
            rd_en = 1'b0;
            @(posedge clk);
            #1;
            if (rd_valid || rd_lane_valid != '0) begin
                $fatal(1, "读请求停止后valid未清除");
            end
        end
    endtask

    initial begin
        rst = 1'b1;
        wr_en = 1'b0;
        wr_addr = '0;
        wr_data = '0;
        rd_en = 1'b0;
        rd_lane_active = '0;
        rd_addr_flat = '0;
        repeat (2) @(posedge clk);
        @(negedge clk);
        rst = 1'b0;

        for (addr_i = 0; addr_i < 256; addr_i = addr_i + 1) begin
            wr_en = 1'b1;
            wr_addr = addr_i;
            wr_data = value_for(addr_i);
            @(posedge clk);
            #1;
        end
        for (addr_i = MAX_BYTES - 5; addr_i < MAX_BYTES; addr_i = addr_i + 1) begin
            wr_en = 1'b1;
            wr_addr = addr_i;
            wr_data = value_for(addr_i);
            @(posedge clk);
            #1;
        end
        @(negedge clk);
        wr_en = 1'b0;

        check_read_window(2, 2, 16);
        check_read_window(30, 2, 16);
        check_read_window(17, 1, 16);
        check_read_window(5, 1, 1);
        check_read_window(MAX_BYTES - 5, 1, 5);

        @(negedge clk);
        rd_addr_flat = '0;
        rd_lane_active = 16'h0001;
        rd_addr_flat[0 +: ADDR_WIDTH] = 5;
        rd_addr_flat[ADDR_WIDTH +: ADDR_WIDTH] = 37;
        for (lane_i = 2; lane_i < LANES; lane_i = lane_i + 1) begin
            rd_addr_flat[lane_i*ADDR_WIDTH +: ADDR_WIDTH] = MAX_BYTES + lane_i;
        end
        rd_en = 1'b1;
        #1;
        if (rd_conflict || rd_bad_address) begin
            $fatal(1, "inactive lane的同bank或padding地址影响了active请求");
        end
        @(posedge clk);
        #1;
        if (!rd_valid || rd_lane_valid !== 16'h0001 || rd_data_flat[7:0] !== value_for(5)) begin
            $fatal(1, "inactive lane被错误地参与读取或置为valid");
        end

        @(negedge clk);
        rd_addr_flat = '0;
        rd_lane_active = 16'h0003;
        rd_addr_flat[0 +: ADDR_WIDTH] = 1;
        rd_addr_flat[ADDR_WIDTH +: ADDR_WIDTH] = 33;
        rd_en = 1'b1;
        #1;
        if (!rd_conflict || rd_bad_address) begin
            $fatal(1, "两个active请求命中同一bank时未正确报告冲突");
        end
        @(posedge clk);
        #1;
        if (rd_valid) begin
            $fatal(1, "冲突读请求错误地产生有效响应");
        end

        @(negedge clk);
        rd_addr_flat = '0;
        rd_lane_active = '0;
        rd_en = 1'b1;
        for (lane_i = 0; lane_i < LANES; lane_i = lane_i + 1) begin
            rd_addr_flat[lane_i*ADDR_WIDTH +: ADDR_WIDTH] = MAX_BYTES + lane_i;
        end
        #1;
        if (rd_conflict || rd_bad_address) begin
            $fatal(1, "空active mask检查了无效lane地址");
        end
        @(posedge clk);
        #1;
        if (rd_valid || rd_lane_valid != '0) begin
            $fatal(1, "空active mask错误地产生读响应");
        end

        @(negedge clk);
        rd_lane_active = 16'h0001;
        rd_addr_flat[0 +: ADDR_WIDTH] = MAX_BYTES;
        rd_en = 1'b1;
        #1;
        if (!rd_bad_address || rd_conflict) begin
            $fatal(1, "active越界读地址未检出");
        end
        @(posedge clk);
        #1;
        if (rd_valid) begin
            $fatal(1, "越界active读请求错误地产生有效响应");
        end

        @(negedge clk);
        rd_en = 1'b0;
        wr_en = 1'b1;
        wr_addr = MAX_BYTES;
        #1;
        if (!wr_bad_address) begin
            $fatal(1, "越界写地址未检出");
        end
        @(posedge clk);
        #1;
        if (rd_valid) begin
            $fatal(1, "越界读请求错误地产生有效响应");
        end

        $display("PASS S2C feature bank32: full, single, tail, padding, conflict and bounds");
        $finish;
    end
endmodule
