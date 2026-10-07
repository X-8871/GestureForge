// 用 G0 nearest-repeat 查询验证坐标、NCHW 地址及 INT8 数值复制。
module tb_s2a_upsample_query;
    logic [31:0] input_base_address;
    logic [31:0] input_channels;
    logic [31:0] input_height;
    logic [31:0] input_width;
    logic [31:0] stride;
    logic [31:0] input_channel;
    logic [31:0] output_y;
    logic [31:0] output_x;
    logic [1351:0] source_plane;
    logic [63:0] output_height;
    logic [63:0] output_width;
    logic [31:0] source_channel;
    logic [31:0] source_y;
    logic [31:0] source_x;
    logic [31:0] source_address;
    logic signed [7:0] output_value;
    logic [2:0] error_code;

    integer vector_fd;
    integer scan_result;
    integer vector_class;
    integer case_index;
    integer query_index;
    integer record_count;
    integer model_query_count;
    integer random_count;
    integer directed_query_count;
    integer directed_case_count;
    integer fixture_query_count;
    integer bad_argument_count;
    integer bad_range_count;
    integer boundary_success_count;
    integer input_base_value;
    integer input_channels_value;
    integer input_height_value;
    integer input_width_value;
    integer stride_value;
    integer input_channel_value;
    integer output_y_value;
    integer output_x_value;
    integer expected_output_height;
    integer expected_output_width;
    integer expected_source_channel;
    integer expected_source_y;
    integer expected_source_x;
    longint unsigned expected_offset;
    integer expected_address;
    integer expected_output_value;
    integer expected_error;
    integer previous_directed_case;
    longint unsigned actual_offset;
    logic [1351:0] source_plane_value;

    int8_upsample_query dut (
        .input_base_address(input_base_address),
        .input_channels(input_channels),
        .input_height(input_height),
        .input_width(input_width),
        .stride(stride),
        .input_channel(input_channel),
        .output_y(output_y),
        .output_x(output_x),
        .source_plane(source_plane),
        .output_height(output_height),
        .output_width(output_width),
        .source_channel(source_channel),
        .source_y(source_y),
        .source_x(source_x),
        .source_address(source_address),
        .output_value(output_value),
        .error_code(error_code)
    );

    task automatic fail(input string message);
        begin
            $display("FAIL: %s", message);
            $fatal(1);
        end
    endtask

    task automatic set_default_small;
        begin
            input_base_address = 32'd0;
            input_channels = 32'd1;
            input_height = 32'd2;
            input_width = 32'd2;
            stride = 32'd2;
            input_channel = 32'd0;
            output_y = 32'd0;
            output_x = 32'd0;
            source_plane = '0;
            source_plane[7:0] = 8'd1;
            source_plane[15:8] = 8'd2;
            source_plane[23:16] = 8'd3;
            source_plane[31:24] = 8'd4;
        end
    endtask

    task automatic assert_error(input integer expected_code,
                                input string case_name);
        begin
            #1;
            if (error_code !== expected_code[2:0]) begin
                $display("case=%s expected_error=%0d actual_error=%0d",
                         case_name, expected_code, error_code);
                fail("错误码与非法刺激不匹配");
            end
            if ((output_height !== 64'd0) || (output_width !== 64'd0) ||
                (source_channel !== 32'd0) || (source_y !== 32'd0) ||
                (source_x !== 32'd0) || (source_address !== 32'd0) ||
                (output_value !== 8'sd0)) begin
                fail("非法请求必须清零所有结果");
            end
            if (expected_code == 1) begin
                bad_argument_count = bad_argument_count + 1;
            end else if (expected_code == 2) begin
                bad_range_count = bad_range_count + 1;
            end
        end
    endtask

    initial begin
        input_base_address = 32'd0;
        input_channels = 32'd0;
        input_height = 32'd0;
        input_width = 32'd0;
        stride = 32'd0;
        input_channel = 32'd0;
        output_y = 32'd0;
        output_x = 32'd0;
        source_plane = '0;
        record_count = 0;
        model_query_count = 0;
        random_count = 0;
        directed_query_count = 0;
        directed_case_count = 0;
        fixture_query_count = 0;
        bad_argument_count = 0;
        bad_range_count = 0;
        boundary_success_count = 0;
        previous_directed_case = -1;

        vector_fd = $fopen("vectors.dat", "r");
        if (vector_fd == 0) begin
            fail("无法打开临时上采样查询向量文件");
        end

        scan_result = $fscanf(
            vector_fd,
            "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %h\n",
            vector_class, case_index, query_index, input_base_value,
            input_channels_value, input_height_value, input_width_value,
            stride_value, input_channel_value, output_y_value, output_x_value,
            expected_output_height, expected_output_width,
            expected_source_channel, expected_source_y, expected_source_x,
            expected_offset, expected_address, expected_output_value,
            expected_error, source_plane_value
        );
        while (scan_result == 21) begin
            input_base_address = input_base_value[31:0];
            input_channels = input_channels_value[31:0];
            input_height = input_height_value[31:0];
            input_width = input_width_value[31:0];
            stride = stride_value[31:0];
            input_channel = input_channel_value[31:0];
            output_y = output_y_value[31:0];
            output_x = output_x_value[31:0];
            source_plane = source_plane_value;
            #1;

            if (error_code !== expected_error[2:0]) begin
                $display("class=%0d case=%0d query=%0d expected_error=%0d actual_error=%0d",
                         vector_class, case_index, query_index,
                         expected_error, error_code);
                fail("查询错误码与向量不匹配");
            end
            if ((output_height !== {32'd0, expected_output_height[31:0]}) ||
                (output_width !== {32'd0, expected_output_width[31:0]})) begin
                $display("class=%0d case=%0d query=%0d expected_hw=%0dx%0d actual_hw=%0dx%0d",
                         vector_class, case_index, query_index,
                         expected_output_height, expected_output_width,
                         output_height, output_width);
                fail("nearest-repeat 输出尺寸不匹配");
            end
            if ((source_channel !== expected_source_channel[31:0]) ||
                (source_y !== expected_source_y[31:0]) ||
                (source_x !== expected_source_x[31:0])) begin
                $display("class=%0d case=%0d query=%0d expected_source=%0d,%0d,%0d actual_source=%0d,%0d,%0d",
                         vector_class, case_index, query_index,
                         expected_source_channel, expected_source_y, expected_source_x,
                         source_channel, source_y, source_x);
                fail("映射源坐标与期望不匹配");
            end
            if ((source_address !== expected_address[31:0]) ||
                (output_value !== expected_output_value[7:0])) begin
                $display("class=%0d case=%0d query=%0d expected_address=%0d actual_address=%0d expected_value=%0d actual_value=%0d",
                         vector_class, case_index, query_index,
                         expected_address, source_address,
                         expected_output_value, output_value);
                fail("逻辑地址或复制值不匹配");
            end
            actual_offset = source_address - input_base_address;
            if (actual_offset !== expected_offset[63:0]) begin
                $display("class=%0d case=%0d query=%0d expected_offset=%0d actual_offset=%0d",
                         vector_class, case_index, query_index,
                         expected_offset, actual_offset);
                fail("NCHW 相对 byte offset 不匹配");
            end

            case (vector_class)
                0: begin
                    random_count = random_count + 1;
                    model_query_count = model_query_count + 1;
                end
                1: begin
                    directed_query_count = directed_query_count + 1;
                    model_query_count = model_query_count + 1;
                    if (case_index != previous_directed_case) begin
                        directed_case_count = directed_case_count + 1;
                        previous_directed_case = case_index;
                    end
                end
                2: fixture_query_count = fixture_query_count + 1;
                default: fail("向量类别编号非法");
            endcase
            record_count = record_count + 1;

            scan_result = $fscanf(
                vector_fd,
                "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %h\n",
                vector_class, case_index, query_index, input_base_value,
                input_channels_value, input_height_value, input_width_value,
                stride_value, input_channel_value, output_y_value, output_x_value,
                expected_output_height, expected_output_width,
                expected_source_channel, expected_source_y, expected_source_x,
                expected_offset, expected_address, expected_output_value,
                expected_error, source_plane_value
            );
        end
        if (scan_result != -1) begin
            fail("向量文件包含不完整查询记录");
        end
        $fclose(vector_fd);

        set_default_small();
        input_channels = 32'd0;
        assert_error(1, "channels-zero");
        set_default_small();
        input_height = 32'd0;
        assert_error(1, "height-zero");
        set_default_small();
        input_width = 32'd0;
        assert_error(1, "width-zero");
        set_default_small();
        stride = 32'd0;
        assert_error(1, "stride-zero");
        set_default_small();
        input_height = 32'd14;
        assert_error(1, "height-over-plane-limit");
        set_default_small();
        input_width = 32'd14;
        assert_error(1, "width-over-plane-limit");
        set_default_small();
        input_channel = 32'd1;
        assert_error(1, "channel-out-of-range");
        set_default_small();
        output_y = 32'd4;
        assert_error(1, "output-y-out-of-range");
        set_default_small();
        output_x = 32'd4;
        assert_error(1, "output-x-out-of-range");

        set_default_small();
        input_base_address = 32'hffff_fffc;
        output_y = 32'd2;
        output_x = 32'd2;
        #1;
        if ((error_code !== 3'd0) || (output_height !== 64'd4) ||
            (output_width !== 64'd4) || (source_y !== 32'd1) ||
            (source_x !== 32'd1) || (source_address !== 32'hffff_ffff) ||
            (output_value !== 8'sd4)) begin
            fail("最大合法 uint32 地址边界应正常复制输入值");
        end
        boundary_success_count = boundary_success_count + 1;

        set_default_small();
        input_base_address = 32'hffff_fffd;
        output_y = 32'd2;
        output_x = 32'd2;
        assert_error(2, "address-overflow-near-maximum");
        set_default_small();
        input_base_address = 32'hffff_ffff;
        output_y = 32'd2;
        output_x = 32'd2;
        assert_error(2, "address-overflow-at-maximum");

        if ((record_count != 1034) || (random_count != 1000) ||
            (directed_query_count != 18) || (directed_case_count != 16) ||
            (fixture_query_count != 16) || (model_query_count != 1018) ||
            (bad_argument_count != 9) || (bad_range_count != 2) ||
            (boundary_success_count != 1)) begin
            $display("records=%0d random=%0d directed_cases=%0d directed_queries=%0d fixture=%0d model=%0d bad_argument=%0d bad_range=%0d boundary=%0d",
                     record_count, random_count, directed_case_count,
                     directed_query_count, fixture_query_count, model_query_count,
                     bad_argument_count, bad_range_count, boundary_success_count);
            fail("测试计数与冻结用例数量不符");
        end

        $display("PASS: queries=1034 model_random=1000 model_directed_cases=16 model_directed_queries=18 fixture_queries=16 bad_argument=9 bad_range=2 boundary=1");
        $finish;
    end
endmodule
