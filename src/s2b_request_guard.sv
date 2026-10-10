// 候选物理请求准入：冻结逻辑对象级白名单，不包含 AXI 声明或所有权状态。
module s2b_request_guard (
    input  logic        mem_write,
    input  logic [31:0] mem_addr,
    input  logic [3:0]  mem_rstrb,
    input  logic [3:0]  mem_wstrb,
    output logic        request_allowed,
    output logic [31:0] physical_addr,
    output logic [2:0]  error_code
);
    localparam logic [2:0] BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] BAD_RANGE = 3'd2;
    // 来自 S2A-T01 冻结 manifest；对象 0/1 只读，36 个独立 feature 可读写。
    localparam logic [31:0] OBJECT_BEGIN [0:37] = '{
        32'h00000000, 32'h00100000,
        32'h01000000, 32'h01152000, 32'h011FB000, 32'h012A4000,
        32'h012F8800, 32'h0134D000, 32'h013A1800, 32'h0144A800,
        32'h014F3800, 32'h01645800, 32'h0169A000, 32'h016EE800,
        32'h01718C00, 32'h01743000, 32'h0176D400, 32'h017C1C00,
        32'h01816400, 32'h018BF400, 32'h018E9800, 32'h01913C00,
        32'h01928E00, 32'h0193E000, 32'h01953200, 32'h0197D600,
        32'h019A7A00, 32'h019FC200, 32'h01A11400, 32'h01A26600,
        32'h01A30F00, 32'h01A46100, 32'h01A47500, 32'h01A51E00,
        32'h01A57280, 32'h01A6C480, 32'h01AABA80, 32'h01AD5E80
    };
    localparam logic [31:0] OBJECT_END [0:37] = '{
        32'h0007EC00, 32'h006A12FC,
        32'h01152000, 32'h011FB000, 32'h012A4000, 32'h012F8800,
        32'h0134D000, 32'h013A1800, 32'h0144A800, 32'h014F3800,
        32'h01645800, 32'h0169A000, 32'h016EE800, 32'h01718C00,
        32'h01743000, 32'h0176D400, 32'h017C1C00, 32'h01816400,
        32'h018BF400, 32'h018E9800, 32'h01913C00, 32'h01928E00,
        32'h0193E000, 32'h01953200, 32'h0197D600, 32'h019A7A00,
        32'h019FC200, 32'h01A11400, 32'h01A26600, 32'h01A30F00,
        32'h01A46100, 32'h01A474CE, 32'h01A51E00, 32'h01A57280,
        32'h01A6C480, 32'h01AABA80, 32'h01AD5E80, 32'h01ADADB8
    };
    logic [3:0] selected;
    logic [32:0] translated;
    logic [32:0] lane_addr;
    logic object_matches;
    logic range_allowed;

    always_comb begin
        selected = mem_write ? mem_wstrb : mem_rstrb;
        translated = {1'b0, mem_addr} + 33'h010000000;
        lane_addr = 33'd0;
        object_matches = 1'b0;
        range_allowed = 1'b0;
        request_allowed = 1'b0;
        physical_addr = 32'd0;
        error_code = BAD_RANGE;
        // 每个选中字节都要落入同一对象；未选 lane 不要求对象覆盖。
        for (int object_index = 0; object_index < 38; object_index++) begin
            object_matches = !mem_write || (object_index >= 2);
            for (int lane = 0; lane < 4; lane++) begin
                lane_addr = {1'b0, mem_addr} + {31'd0, lane[1:0]};
                if (selected[lane] &&
                    ((lane_addr < {1'b0, OBJECT_BEGIN[object_index]}) ||
                     (lane_addr >= {1'b0, OBJECT_END[object_index]})))
                    object_matches = 1'b0;
            end
            range_allowed = range_allowed || object_matches;
        end
        if ((mem_addr[1:0] != 2'b00) || (selected == 4'b0000) ||
            (mem_write ? (mem_rstrb != 4'b0000) : (mem_wstrb != 4'b0000))) begin
            error_code = BAD_ARGUMENT;
        end else if (range_allowed && !translated[32] &&
                     (translated >= 33'h010000000) &&
                     (translated < 33'h012000000)) begin
            request_allowed = 1'b1;
            physical_addr = translated[31:0];
            error_code = 3'd0;
        end
    end
endmodule
