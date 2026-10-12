// 阶段 2A：对一个 INT8 最大池化窗口做有符号最大值归约。
module int8_maxpool_window (
    // 仅接受 4 个真实 2x2 模型 tap 或 9 个通用 3x3 tap。
    input  logic [3:0]  candidate_count,
    // tap 0 放在最低字节；其余 tap 按 kernel_y、kernel_x 顺序递增。
    input  logic [71:0] candidates,
    output logic signed [7:0] max_value,
    // 成功为 0；非法 tap 数量或已选 tap 为 -128 时返回 BAD_ARGUMENT(1)。
    output logic [2:0]  error_code
);
    localparam logic [2:0] BAD_ARGUMENT = 3'd1;
    integer tap_index;
    logic signed [7:0] candidate_value;
    logic signed [7:0] current_maximum;

    always_comb begin
        max_value = 8'sd0;
        error_code = 3'd0;
        current_maximum = 8'sh80;
        candidate_value = 8'sd0;

        case (candidate_count)
            4'd4, 4'd9: begin
                for (tap_index = 0; tap_index < 9; tap_index = tap_index + 1) begin
                    if (tap_index < candidate_count) begin
                        candidate_value = $signed(candidates[tap_index * 8 +: 8]);
                        if (candidate_value == 8'sh80) begin
                            error_code = BAD_ARGUMENT;
                        end
                        if (candidate_value > current_maximum) begin
                            current_maximum = candidate_value;
                        end
                    end
                end
                if (error_code == 3'd0) begin
                    max_value = current_maximum;
                end
            end
            default: begin
                error_code = BAD_ARGUMENT;
            end
        endcase
    end
endmodule
