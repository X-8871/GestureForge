// 用冻结向量逐项验证阶段 2A 单窗口最大池化归约原语。
module tb_s2a_maxpool_window;
    logic [3:0] candidate_count;
    logic [71:0] candidate_values;
    logic signed [7:0] max_value;
    logic [2:0] error_code;

    integer vector_fd;
    integer scan_result;
    integer vector_class;
    integer layer_index;
    integer case_index;
    integer vector_count;
    integer expected_bad;
    integer expected_value;
    integer value_0;
    integer value_1;
    integer value_2;
    integer value_3;
    integer value_4;
    integer value_5;
    integer value_6;
    integer value_7;
    integer value_8;
    integer vectors_seen;
    integer random_seen;
    integer directed_seen;
    integer fixture_seen;
    integer invalid_seen;

    int8_maxpool_window dut (
        .candidate_count(candidate_count),
        .candidates(candidate_values),
        .max_value(max_value),
        .error_code(error_code)
    );

    task automatic fail(input string message);
        begin
            $display("FAIL: %s", message);
            $fatal(1);
        end
    endtask

    task automatic assert_invalid(input integer count_value,
                                  input logic [71:0] values,
                                  input string case_name);
        begin
            candidate_count = count_value[3:0];
            candidate_values = values;
            #1;
            if (error_code !== 3'd1 || max_value !== 8'sd0) begin
                $display("invalid case=%s count=%0d error=%0d result=%0d",
                         case_name, count_value, error_code, max_value);
                fail("非法输入必须明确报错并将结果清零");
            end
            invalid_seen = invalid_seen + 1;
        end
    endtask

    initial begin
        candidate_count = 4'd0;
        candidate_values = '0;
        vectors_seen = 0;
        random_seen = 0;
        directed_seen = 0;
        fixture_seen = 0;
        invalid_seen = 0;

        vector_fd = $fopen("vectors.dat", "r");
        if (vector_fd == 0) begin
            fail("无法打开临时规范向量文件");
        end

        scan_result = $fscanf(
            vector_fd,
            "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d\n",
            vector_class, layer_index, case_index, vector_count,
            expected_bad, expected_value, value_0, value_1, value_2,
            value_3, value_4, value_5, value_6, value_7, value_8
        );
        while (scan_result == 15) begin
            candidate_count = vector_count[3:0];
            candidate_values[7:0] = value_0[7:0];
            candidate_values[15:8] = value_1[7:0];
            candidate_values[23:16] = value_2[7:0];
            candidate_values[31:24] = value_3[7:0];
            candidate_values[39:32] = value_4[7:0];
            candidate_values[47:40] = value_5[7:0];
            candidate_values[55:48] = value_6[7:0];
            candidate_values[63:56] = value_7[7:0];
            candidate_values[71:64] = value_8[7:0];
            #1;
            if (error_code !== expected_bad[2:0]) begin
                $display("class=%0d layer=%0d case=%0d expected_error=%0d actual_error=%0d",
                         vector_class, layer_index, case_index, expected_bad, error_code);
                fail("错误标志与冻结向量不匹配");
            end
            if (expected_bad == 0 && max_value !== expected_value[7:0]) begin
                $display("class=%0d layer=%0d case=%0d expected=%0d actual=%0d",
                         vector_class, layer_index, case_index, expected_value, max_value);
                fail("最大值与冻结黄金输出不匹配");
            end
            if (expected_bad != 0 && max_value !== 8'sd0) begin
                fail("错误输入返回了可能误导的非零结果");
            end

            case (vector_class)
                0: random_seen = random_seen + 1;
                1: directed_seen = directed_seen + 1;
                2: fixture_seen = fixture_seen + 1;
                default: fail("向量类别编号非法");
            endcase
            vectors_seen = vectors_seen + 1;

            scan_result = $fscanf(
                vector_fd,
                "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d\n",
                vector_class, layer_index, case_index, vector_count,
                expected_bad, expected_value, value_0, value_1, value_2,
                value_3, value_4, value_5, value_6, value_7, value_8
            );
        end
        if (scan_result != -1) begin
            fail("规范向量文件存在不完整记录");
        end
        $fclose(vector_fd);

        candidate_values = '0;
        assert_invalid(0, candidate_values, "count-zero");
        assert_invalid(5, candidate_values, "count-five");
        assert_invalid(10, candidate_values, "count-ten");
        candidate_values[7:0] = 8'sh80;
        assert_invalid(4, candidate_values, "selected-minus-128");

        candidate_count = 4'd4;
        candidate_values = {{5{8'sh80}}, 8'd4, 8'd3, 8'd2, 8'd1};
        #1;
        if (error_code !== 3'd0 || max_value !== 8'sd4) begin
            fail("未选中的 -128 字节不能使 4-tap 窗口报错");
        end

        if (vectors_seen != 3064 || random_seen != 3000 ||
            directed_seen != 48 || fixture_seen != 16 || invalid_seen != 4) begin
            $display("vectors=%0d random=%0d directed=%0d fixture=%0d invalid=%0d",
                     vectors_seen, random_seen, directed_seen, fixture_seen, invalid_seen);
            fail("仿真向量计数与阶段 2A 任务冻结要求不一致");
        end
        $display("PASS: model_vectors=3048 random=3000 directed=48 fixture=16 invalid=4 mismatches=0");
        $finish;
    end
endmodule
