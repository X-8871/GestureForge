// 用冻结坐标逐 tap 验证 maxpool 几何、掩码和 NCHW 字节地址。
module tb_s2a_maxpool_geometry;
    logic [31:0] input_base_address;
    logic [31:0] input_channels;
    logic [31:0] input_height;
    logic [31:0] input_width;
    logic [31:0] kernel_height;
    logic [31:0] kernel_width;
    logic [31:0] stride_y;
    logic [31:0] stride_x;
    logic [31:0] darknet_padding_parameter;
    logic [31:0] input_channel;
    logic [31:0] output_y;
    logic [31:0] output_x;
    logic [32:0] output_height;
    logic [32:0] output_width;
    logic [3:0] tap_count;
    logic [8:0] tap_valid_mask;
    logic [31:0] tap_address [0:8];
    logic [31:0] tap_source_channel [0:8];
    logic signed [63:0] tap_source_y [0:8];
    logic signed [63:0] tap_source_x [0:8];
    logic [2:0] error_code;

    integer vector_fd;
    integer scan_result;
    integer vector_class;
    integer layer_index;
    integer case_index;
    integer record_count;
    integer random_count;
    integer directed_count;
    integer fixture_count;
    integer model_tap_count;
    integer fixture_tap_count;
    integer expected_bad_argument_count;
    integer expected_bad_range_count;
    integer boundary_success_count;
    integer input_base_value;
    integer input_channels_value;
    integer input_height_value;
    integer input_width_value;
    integer kernel_height_value;
    integer kernel_width_value;
    integer stride_y_value;
    integer stride_x_value;
    integer padding_value;
    integer input_channel_value;
    integer output_y_value;
    integer output_x_value;
    integer expected_output_height;
    integer expected_output_width;
    integer expected_tap_count;
    integer expected_mask;
    integer expected_error;
    integer random_value_0;
    integer random_value_1;
    integer random_value_2;
    integer random_value_3;
    integer expected_valid;
    integer expected_channel;
    integer expected_address;
    integer tap_index;
    longint signed expected_y;
    longint signed expected_x;
    longint signed expected_offset;
    longint unsigned actual_offset;

    int8_maxpool_geometry dut (
        .input_base_address(input_base_address),
        .input_channels(input_channels),
        .input_height(input_height),
        .input_width(input_width),
        .kernel_height(kernel_height),
        .kernel_width(kernel_width),
        .stride_y(stride_y),
        .stride_x(stride_x),
        .darknet_padding_parameter(darknet_padding_parameter),
        .input_channel(input_channel),
        .output_y(output_y),
        .output_x(output_x),
        .output_height(output_height),
        .output_width(output_width),
        .tap_count(tap_count),
        .tap_valid_mask(tap_valid_mask),
        .tap_address(tap_address),
        .tap_source_channel(tap_source_channel),
        .tap_source_y(tap_source_y),
        .tap_source_x(tap_source_x),
        .error_code(error_code)
    );

    task automatic fail(input string message);
        begin
            $display("FAIL: %s", message);
            $fatal(1);
        end
    endtask

    task automatic set_default_valid;
        begin
            input_base_address = 32'd0;
            input_channels = 32'd2;
            input_height = 32'd4;
            input_width = 32'd4;
            kernel_height = 32'd2;
            kernel_width = 32'd2;
            stride_y = 32'd1;
            stride_x = 32'd1;
            darknet_padding_parameter = 32'd0;
            input_channel = 32'd0;
            output_y = 32'd0;
            output_x = 32'd0;
        end
    endtask

    task automatic assert_error(input integer expected_code,
                                input string case_name);
        integer check_index;
        begin
            #1;
            if (error_code !== expected_code[2:0]) begin
                $display("case=%s expected_error=%0d actual_error=%0d",
                         case_name, expected_code, error_code);
                fail("错误码与非法刺激不匹配");
            end
            if ((output_height !== 33'd0) || (output_width !== 33'd0) ||
                (tap_count !== 4'd0) || (tap_valid_mask !== 9'd0)) begin
                fail("非法请求必须清零几何结果");
            end
            for (check_index = 0; check_index < 9; check_index = check_index + 1) begin
                if ((tap_address[check_index] !== 32'd0) ||
                    (tap_source_channel[check_index] !== 32'd0) ||
                    (tap_source_y[check_index] !== 64'sd0) ||
                    (tap_source_x[check_index] !== 64'sd0)) begin
                    fail("非法请求必须清零 tap 输出");
                end
            end
            if (expected_code == 1) begin
                expected_bad_argument_count = expected_bad_argument_count + 1;
            end else if (expected_code == 2) begin
                expected_bad_range_count = expected_bad_range_count + 1;
            end
        end
    endtask

    initial begin
        input_base_address = 32'd0;
        input_channels = 32'd0;
        input_height = 32'd0;
        input_width = 32'd0;
        kernel_height = 32'd0;
        kernel_width = 32'd0;
        stride_y = 32'd0;
        stride_x = 32'd0;
        darknet_padding_parameter = 32'd0;
        input_channel = 32'd0;
        output_y = 32'd0;
        output_x = 32'd0;
        record_count = 0;
        random_count = 0;
        directed_count = 0;
        fixture_count = 0;
        model_tap_count = 0;
        fixture_tap_count = 0;
        expected_bad_argument_count = 0;
        expected_bad_range_count = 0;
        boundary_success_count = 0;

        vector_fd = $fopen("vectors.dat", "r");
        if (vector_fd == 0) begin
            fail("无法打开临时几何向量文件");
        end

        scan_result = $fscanf(
            vector_fd,
            "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d\n",
            vector_class, layer_index, case_index, input_base_value,
            input_channels_value, input_height_value, input_width_value,
            kernel_height_value, kernel_width_value, stride_y_value,
            stride_x_value, padding_value, input_channel_value,
            output_y_value, output_x_value, expected_output_height,
            expected_output_width, expected_tap_count, expected_mask,
            expected_error, random_value_0, random_value_1,
            random_value_2, random_value_3
        );
        while (scan_result == 24) begin
            input_base_address = input_base_value[31:0];
            input_channels = input_channels_value[31:0];
            input_height = input_height_value[31:0];
            input_width = input_width_value[31:0];
            kernel_height = kernel_height_value[31:0];
            kernel_width = kernel_width_value[31:0];
            stride_y = stride_y_value[31:0];
            stride_x = stride_x_value[31:0];
            darknet_padding_parameter = padding_value[31:0];
            input_channel = input_channel_value[31:0];
            output_y = output_y_value[31:0];
            output_x = output_x_value[31:0];
            #1;

            if (error_code !== expected_error[2:0]) begin
                $display("class=%0d layer=%0d case=%0d expected_error=%0d actual_error=%0d",
                         vector_class, layer_index, case_index,
                         expected_error, error_code);
                fail("向量错误码不匹配");
            end
            if ((output_height !== {1'b0, expected_output_height[31:0]}) ||
                (output_width !== {1'b0, expected_output_width[31:0]})) begin
                $display("class=%0d layer=%0d case=%0d expected_hw=%0dx%0d actual_hw=%0dx%0d",
                         vector_class, layer_index, case_index,
                         expected_output_height, expected_output_width,
                         output_height, output_width);
                fail("输出尺寸与 G0 规格不匹配");
            end
            if ((tap_count !== expected_tap_count[3:0]) ||
                (tap_valid_mask !== expected_mask[8:0])) begin
                $display("class=%0d layer=%0d case=%0d expected_count=%0d actual_count=%0d expected_mask=%h actual_mask=%h",
                         vector_class, layer_index, case_index,
                         expected_tap_count, tap_count,
                         expected_mask[8:0], tap_valid_mask);
                fail("tap 数量或有效掩码与黄金向量不匹配");
            end
            if ((random_value_0 < -127) || (random_value_0 > 127) ||
                (random_value_1 < -127) || (random_value_1 > 127) ||
                (random_value_2 < -127) || (random_value_2 > 127) ||
                (random_value_3 < -127) || (random_value_3 > 127)) begin
                fail("向量记录中的 PRNG INT8 抽样越界");
            end

            for (tap_index = 0; tap_index < 9; tap_index = tap_index + 1) begin
                scan_result = $fscanf(vector_fd, "%d %d %d %d %d %d\n",
                                      expected_valid, expected_channel,
                                      expected_y, expected_x, expected_offset,
                                      expected_address);
                if (scan_result != 6) begin
                    fail("向量文件包含不完整的 tap 期望值");
                end
                if (tap_valid_mask[tap_index] !== expected_valid[0]) begin
                    $display("class=%0d layer=%0d case=%0d tap=%0d expected_valid=%0d actual_valid=%0d",
                             vector_class, layer_index, case_index, tap_index,
                             expected_valid, tap_valid_mask[tap_index]);
                    fail("逐 tap 有效标志与参考坐标不匹配");
                end
                if ((tap_source_channel[tap_index] !== expected_channel[31:0]) ||
                    (tap_source_y[tap_index] !== expected_y) ||
                    (tap_source_x[tap_index] !== expected_x)) begin
                    $display("class=%0d layer=%0d case=%0d tap=%0d expected_cyx=%0d,%0d,%0d actual_cyx=%0d,%0d,%0d",
                             vector_class, layer_index, case_index, tap_index,
                             expected_channel, expected_y, expected_x,
                             tap_source_channel[tap_index],
                             tap_source_y[tap_index], tap_source_x[tap_index]);
                    fail("逐 tap 坐标与独立参考不匹配");
                end
                if (tap_address[tap_index] !== expected_address[31:0]) begin
                    $display("class=%0d layer=%0d case=%0d tap=%0d expected_address=%0d actual_address=%0d",
                             vector_class, layer_index, case_index, tap_index,
                             expected_address, tap_address[tap_index]);
                    fail("逐 tap 地址与冻结模型映射不匹配");
                end
                if (expected_valid != 0) begin
                    actual_offset = tap_address[tap_index] - input_base_address;
                    if (actual_offset !== expected_offset[63:0]) begin
                        $display("class=%0d layer=%0d case=%0d tap=%0d expected_offset=%0d actual_offset=%0d",
                                 vector_class, layer_index, case_index, tap_index,
                                 expected_offset, actual_offset);
                        fail("逐 tap NCHW 相对字节偏移不匹配");
                    end
                end else if (expected_address != 0) begin
                    fail("越界 tap 必须没有可访问地址");
                end
            end

            case (vector_class)
                0: begin
                    random_count = random_count + 1;
                    model_tap_count = model_tap_count + expected_tap_count;
                end
                1: begin
                    directed_count = directed_count + 1;
                    model_tap_count = model_tap_count + expected_tap_count;
                end
                2: begin
                    fixture_count = fixture_count + 1;
                    fixture_tap_count = fixture_tap_count + expected_tap_count;
                end
                default: fail("向量类别编号非法");
            endcase
            record_count = record_count + 1;

            scan_result = $fscanf(
                vector_fd,
                "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d\n",
                vector_class, layer_index, case_index, input_base_value,
                input_channels_value, input_height_value, input_width_value,
                kernel_height_value, kernel_width_value, stride_y_value,
                stride_x_value, padding_value, input_channel_value,
                output_y_value, output_x_value, expected_output_height,
                expected_output_width, expected_tap_count, expected_mask,
                expected_error, random_value_0, random_value_1,
                random_value_2, random_value_3
            );
        end
        if (scan_result != -1) begin
            fail("向量文件存在不完整记录头");
        end
        $fclose(vector_fd);

        set_default_valid();
        kernel_height = 32'd1;
        assert_error(1, "kernel-one");
        set_default_valid();
        kernel_height = 32'd4;
        kernel_width = 32'd4;
        assert_error(1, "kernel-four");
        set_default_valid();
        stride_y = 32'd0;
        assert_error(1, "stride-y-zero");
        set_default_valid();
        stride_x = 32'd0;
        assert_error(1, "stride-x-zero");
        set_default_valid();
        input_channels = 32'd0;
        assert_error(1, "channels-zero");
        set_default_valid();
        input_height = 32'd0;
        assert_error(1, "height-zero");
        set_default_valid();
        input_width = 32'd0;
        assert_error(1, "width-zero");
        set_default_valid();
        input_height = 32'd1;
        assert_error(1, "kernel-larger-than-padded-input");
        set_default_valid();
        input_channel = 32'd2;
        assert_error(1, "channel-out-of-range");
        set_default_valid();
        output_y = 32'd3;
        assert_error(1, "output-y-out-of-range");
        set_default_valid();
        output_x = 32'd3;
        assert_error(1, "output-x-out-of-range");

        set_default_valid();
        input_channels = 32'd1;
        input_height = 32'd2;
        input_width = 32'd2;
        input_base_address = 32'hffff_fffa;
        #1;
        if ((error_code !== 3'd0) || (tap_address[0] !== 32'hffff_fffa) ||
            (tap_address[1] !== 32'hffff_fffb) ||
            (tap_address[2] !== 32'hffff_fffc) ||
            (tap_address[3] !== 32'hffff_fffd)) begin
            fail("最大合法 uint32 地址边界应正常工作");
        end
        boundary_success_count = boundary_success_count + 1;

        set_default_valid();
        input_channels = 32'd1;
        input_height = 32'd2;
        input_width = 32'd2;
        input_base_address = 32'hffff_ffff;
        assert_error(2, "address-overflow-at-maximum-base");
        set_default_valid();
        input_channels = 32'd1;
        input_height = 32'd2;
        input_width = 32'd2;
        input_base_address = 32'hffff_fffd;
        assert_error(2, "address-overflow-in-window");

        if ((record_count != 3064) || (random_count != 3000) ||
            (directed_count != 48) || (fixture_count != 16) ||
            (model_tap_count != 12192) || (fixture_tap_count != 144) ||
            (expected_bad_argument_count != 11) ||
            (expected_bad_range_count != 2) || (boundary_success_count != 1)) begin
            $display("records=%0d random=%0d directed=%0d fixture=%0d model_taps=%0d fixture_taps=%0d bad_argument=%0d bad_range=%0d boundary=%0d",
                     record_count, random_count, directed_count, fixture_count,
                     model_tap_count, fixture_tap_count,
                     expected_bad_argument_count, expected_bad_range_count,
                     boundary_success_count);
            fail("测试类别或非法断言数量与任务规格不匹配");
        end

        $display("PASS: records=3064 model_random=3000 model_directed=48 fixture_windows=16 model_taps=12192 fixture_taps=144 bad_argument=11 bad_range=2 boundary=1");
        $finish;
    end
endmodule
