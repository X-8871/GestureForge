// 按 G0 向量逐 tap 验证卷积 NCHW 输入几何、padding 与逻辑地址。
module tb_s2a_conv_tap_geometry;
    logic [31:0] input_base_address;
    logic [31:0] input_length_bytes;
    logic [31:0] input_batch_count;
    logic [31:0] input_channels;
    logic [31:0] input_height;
    logic [31:0] input_width;
    logic [31:0] output_batch_count;
    logic [31:0] output_channels;
    logic [31:0] output_height;
    logic [31:0] output_width;
    logic [31:0] kernel_height;
    logic [31:0] kernel_width;
    logic [31:0] stride_y;
    logic [31:0] stride_x;
    logic [31:0] pad_left;
    logic [31:0] pad_right;
    logic [31:0] pad_top;
    logic [31:0] pad_bottom;
    logic signed [7:0] padding_value_int8;
    logic [31:0] groups;
    logic [31:0] output_batch;
    logic [31:0] output_channel;
    logic [31:0] output_y;
    logic [31:0] output_x;
    logic [31:0] reduction_index;

    logic [31:0] observed_input_channel;
    logic [31:0] observed_kernel_y;
    logic [31:0] observed_kernel_x;
    logic signed [31:0] observed_input_y;
    logic signed [31:0] observed_input_x;
    logic observed_tap_is_padding;
    logic observed_source_address_valid;
    logic [31:0] observed_source_address;
    logic signed [7:0] observed_padding_value;
    logic [2:0] error_code;

    logic [31:0] vector_base_address;
    integer vector_fd;
    integer scan_result;
    integer vector_class;
    integer layer_index_value;
    integer case_index_value;
    integer output_batch_value;
    integer output_channel_value;
    integer output_y_value;
    integer output_x_value;
    integer input_length_value;
    integer input_batch_count_value;
    integer input_channels_value;
    integer input_height_value;
    integer input_width_value;
    integer output_batch_count_value;
    integer output_channels_value;
    integer output_height_value;
    integer output_width_value;
    integer kernel_height_value;
    integer kernel_width_value;
    integer stride_y_value;
    integer stride_x_value;
    integer pad_left_value;
    integer pad_right_value;
    integer pad_top_value;
    integer pad_bottom_value;
    integer padding_value_value;
    integer groups_value;
    integer reduction_count_value;

    integer tap_index;
    integer expected_input_channel;
    integer expected_kernel_y;
    integer expected_kernel_x;
    integer expected_input_y;
    integer expected_input_x;
    integer expected_is_padding;
    integer record_count;
    integer random_point_count;
    integer random_tap_count;
    integer directed_case_count;
    integer directed_tap_count;
    integer fixture_point_count;
    integer fixture_tap_count;
    integer bad_argument_count;
    integer bad_range_count;
    integer boundary_success_count;
    integer padding_success_count;
    longint unsigned expected_offset;
    longint unsigned expected_address;

    int8_conv_tap_geometry dut (
        .input_base_address(input_base_address),
        .input_length_bytes(input_length_bytes),
        .input_batch_count(input_batch_count),
        .input_channels(input_channels),
        .input_height(input_height),
        .input_width(input_width),
        .output_batch_count(output_batch_count),
        .output_channels(output_channels),
        .output_height(output_height),
        .output_width(output_width),
        .kernel_height(kernel_height),
        .kernel_width(kernel_width),
        .stride_y(stride_y),
        .stride_x(stride_x),
        .pad_left(pad_left),
        .pad_right(pad_right),
        .pad_top(pad_top),
        .pad_bottom(pad_bottom),
        .padding_value_int8(padding_value_int8),
        .groups(groups),
        .output_batch(output_batch),
        .output_channel(output_channel),
        .output_y(output_y),
        .output_x(output_x),
        .reduction_index(reduction_index),
        .input_channel(observed_input_channel),
        .kernel_y(observed_kernel_y),
        .kernel_x(observed_kernel_x),
        .input_y(observed_input_y),
        .input_x(observed_input_x),
        .tap_is_padding(observed_tap_is_padding),
        .source_address_valid(observed_source_address_valid),
        .source_address(observed_source_address),
        .tap_padding_value(observed_padding_value),
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
            input_base_address = 32'h0000_1000;
            input_length_bytes = 32'd9;
            input_batch_count = 32'd1;
            input_channels = 32'd1;
            input_height = 32'd3;
            input_width = 32'd3;
            output_batch_count = 32'd1;
            output_channels = 32'd1;
            output_height = 32'd3;
            output_width = 32'd3;
            kernel_height = 32'd3;
            kernel_width = 32'd3;
            stride_y = 32'd1;
            stride_x = 32'd1;
            pad_left = 32'd1;
            pad_right = 32'd1;
            pad_top = 32'd1;
            pad_bottom = 32'd1;
            padding_value_int8 = 8'sd0;
            groups = 32'd1;
            output_batch = 32'd0;
            output_channel = 32'd0;
            output_y = 32'd0;
            output_x = 32'd0;
            reduction_index = 32'd0;
        end
    endtask

    task automatic assert_error(input integer expected_code,
                                input string case_name);
        begin
            #1;
            if (error_code !== expected_code[2:0]) begin
                $display("case=%s expected_error=%0d actual_error=%0d",
                         case_name, expected_code, error_code);
                fail("卷积 tap 错误码与非法刺激不匹配");
            end
            if ((observed_input_channel !== 32'd0) ||
                (observed_kernel_y !== 32'd0) || (observed_kernel_x !== 32'd0) ||
                (observed_input_y !== 32'sd0) || (observed_input_x !== 32'sd0) ||
                (observed_tap_is_padding !== 1'b0) ||
                (observed_source_address_valid !== 1'b0) ||
                (observed_source_address !== 32'd0) ||
                (observed_padding_value !== 8'sd0)) begin
                fail("非法卷积 tap 请求必须清零几何结果并撤销地址有效");
            end
            if (expected_code == 1) begin
                bad_argument_count = bad_argument_count + 1;
            end else if (expected_code == 2) begin
                bad_range_count = bad_range_count + 1;
            end
        end
    endtask

    task automatic assert_padding_success;
        begin
            #1;
            if ((error_code !== 3'd0) || (observed_input_channel !== 32'd0) ||
                (observed_kernel_y !== 32'd0) || (observed_kernel_x !== 32'd0) ||
                (observed_input_y !== -32'sd1) || (observed_input_x !== -32'sd1) ||
                (observed_tap_is_padding !== 1'b1) ||
                (observed_source_address_valid !== 1'b0) ||
                (observed_source_address !== 32'd0) ||
                (observed_padding_value !== 8'sd0)) begin
                fail("合法越界 tap 必须报告 zero padding 且不输出地址");
            end
            padding_success_count = padding_success_count + 1;
        end
    endtask

    task automatic assert_uint32_last_address;
        begin
            #1;
            if ((error_code !== 3'd0) ||
                (observed_tap_is_padding !== 1'b0) ||
                (observed_source_address_valid !== 1'b1) ||
                (observed_source_address !== 32'hffff_ffff) ||
                (observed_input_channel !== 32'd0) ||
                (observed_kernel_y !== 32'd0) ||
                (observed_kernel_x !== 32'd0) ||
                (observed_input_y !== 32'sd0) ||
                (observed_input_x !== 32'sd0)) begin
                fail("uint32 最大地址字节成功边界不匹配");
            end
            boundary_success_count = boundary_success_count + 1;
        end
    endtask

    initial begin
        input_base_address = 32'd0;
        input_length_bytes = 32'd0;
        input_batch_count = 32'd0;
        input_channels = 32'd0;
        input_height = 32'd0;
        input_width = 32'd0;
        output_batch_count = 32'd0;
        output_channels = 32'd0;
        output_height = 32'd0;
        output_width = 32'd0;
        kernel_height = 32'd0;
        kernel_width = 32'd0;
        stride_y = 32'd0;
        stride_x = 32'd0;
        pad_left = 32'd0;
        pad_right = 32'd0;
        pad_top = 32'd0;
        pad_bottom = 32'd0;
        padding_value_int8 = 8'sd0;
        groups = 32'd0;
        output_batch = 32'd0;
        output_channel = 32'd0;
        output_y = 32'd0;
        output_x = 32'd0;
        reduction_index = 32'd0;
        record_count = 0;
        random_point_count = 0;
        random_tap_count = 0;
        directed_case_count = 0;
        directed_tap_count = 0;
        fixture_point_count = 0;
        fixture_tap_count = 0;
        bad_argument_count = 0;
        bad_range_count = 0;
        boundary_success_count = 0;
        padding_success_count = 0;

        vector_fd = $fopen("vectors.dat", "r");
        if (vector_fd == 0) begin
            fail("无法打开临时卷积 tap 向量文件");
        end
        scan_result = $fscanf(
            vector_fd,
            "%d %d %d %d %d %d %d %h %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d\n",
            vector_class, layer_index_value, case_index_value,
            output_batch_value, output_channel_value, output_y_value,
            output_x_value, vector_base_address, input_length_value,
            input_batch_count_value, input_channels_value, input_height_value,
            input_width_value, output_batch_count_value, output_channels_value,
            output_height_value, output_width_value, kernel_height_value,
            kernel_width_value, stride_y_value, stride_x_value, pad_left_value,
            pad_right_value, pad_top_value, pad_bottom_value,
            padding_value_value, groups_value, reduction_count_value
        );
        while (scan_result == 28) begin
            input_base_address = vector_base_address;
            input_length_bytes = input_length_value[31:0];
            input_batch_count = input_batch_count_value[31:0];
            input_channels = input_channels_value[31:0];
            input_height = input_height_value[31:0];
            input_width = input_width_value[31:0];
            output_batch_count = output_batch_count_value[31:0];
            output_channels = output_channels_value[31:0];
            output_height = output_height_value[31:0];
            output_width = output_width_value[31:0];
            kernel_height = kernel_height_value[31:0];
            kernel_width = kernel_width_value[31:0];
            stride_y = stride_y_value[31:0];
            stride_x = stride_x_value[31:0];
            pad_left = pad_left_value[31:0];
            pad_right = pad_right_value[31:0];
            pad_top = pad_top_value[31:0];
            pad_bottom = pad_bottom_value[31:0];
            padding_value_int8 = padding_value_value[7:0];
            groups = groups_value[31:0];
            output_batch = output_batch_value[31:0];
            output_channel = output_channel_value[31:0];
            output_y = output_y_value[31:0];
            output_x = output_x_value[31:0];

            for (tap_index = 0; tap_index < reduction_count_value;
                 tap_index = tap_index + 1) begin
                reduction_index = tap_index[31:0];
                expected_input_channel = tap_index /
                    (kernel_height_value * kernel_width_value);
                expected_kernel_y =
                    (tap_index / kernel_width_value) % kernel_height_value;
                expected_kernel_x = tap_index % kernel_width_value;
                expected_input_y = output_y_value * stride_y_value +
                                   expected_kernel_y - pad_top_value;
                expected_input_x = output_x_value * stride_x_value +
                                   expected_kernel_x - pad_left_value;
                expected_is_padding =
                    (expected_input_y < 0) ||
                    (expected_input_y >= input_height_value) ||
                    (expected_input_x < 0) ||
                    (expected_input_x >= input_width_value);

                expected_offset = 64'd0;
                expected_address = 64'd0;
                if (expected_is_padding == 0) begin
                    expected_offset =
                        (((expected_input_channel * input_height_value) +
                          expected_input_y) * input_width_value) + expected_input_x;
                    expected_address = vector_base_address + expected_offset;
                    if ((expected_offset >= input_length_value) ||
                        (expected_address > 64'h0000_0000_ffff_ffff)) begin
                        fail("testbench 独立卷积 tap 地址越过输入对象边界");
                    end
                end

                #1;
                if (error_code !== 3'd0) begin
                    $display("class=%0d layer=%0d case=%0d k=%0d error=%0d",
                             vector_class, layer_index_value, case_index_value,
                             tap_index, error_code);
                    fail("合法卷积 tap 查询返回错误");
                end
                if ((observed_input_channel !== expected_input_channel[31:0]) ||
                    (observed_kernel_y !== expected_kernel_y[31:0]) ||
                    (observed_kernel_x !== expected_kernel_x[31:0]) ||
                    (observed_input_y !== expected_input_y[31:0]) ||
                    (observed_input_x !== expected_input_x[31:0]) ||
                    (observed_tap_is_padding !== (expected_is_padding != 0)) ||
                    (observed_source_address_valid !== (expected_is_padding == 0)) ||
                    (observed_source_address !== expected_address[31:0]) ||
                    (observed_padding_value !== 8'sd0)) begin
                    $display("class=%0d layer=%0d case=%0d k=%0d expected=(ic%0d ky%0d kx%0d y%0d x%0d pad%0d addr%0d) actual=(ic%0d ky%0d kx%0d y%0d x%0d pad%0d valid%0d addr%0d)",
                             vector_class, layer_index_value, case_index_value,
                             tap_index, expected_input_channel, expected_kernel_y,
                             expected_kernel_x, expected_input_y, expected_input_x,
                             expected_is_padding, expected_address,
                             observed_input_channel, observed_kernel_y,
                             observed_kernel_x, observed_input_y, observed_input_x,
                             observed_tap_is_padding, observed_source_address_valid,
                             observed_source_address);
                    fail("卷积 tap 坐标、padding 标志或逻辑地址逐项不匹配");
                end

                if (vector_class == 0) begin
                    random_tap_count = random_tap_count + 1;
                end else if (vector_class == 1) begin
                    directed_tap_count = directed_tap_count + 1;
                end else if (vector_class == 2) begin
                    fixture_tap_count = fixture_tap_count + 1;
                end else begin
                    fail("卷积 tap 向量类别编号非法");
                end
            end
            if (vector_class == 0) begin
                random_point_count = random_point_count + 1;
            end else if (vector_class == 1) begin
                directed_case_count = directed_case_count + 1;
            end else if (vector_class == 2) begin
                fixture_point_count = fixture_point_count + 1;
            end
            record_count = record_count + 1;
            scan_result = $fscanf(
                vector_fd,
                "%d %d %d %d %d %d %d %h %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d\n",
                vector_class, layer_index_value, case_index_value,
                output_batch_value, output_channel_value, output_y_value,
                output_x_value, vector_base_address, input_length_value,
                input_batch_count_value, input_channels_value, input_height_value,
                input_width_value, output_batch_count_value, output_channels_value,
                output_height_value, output_width_value, kernel_height_value,
                kernel_width_value, stride_y_value, stride_x_value, pad_left_value,
                pad_right_value, pad_top_value, pad_bottom_value,
                padding_value_value, groups_value, reduction_count_value
            );
        end
        if (scan_result != -1) begin
            fail("卷积 tap 刺激文件包含不完整向量");
        end
        $fclose(vector_fd);

        set_default_valid();
        groups = 32'd2;
        assert_error(1, "groups-not-supported-by-frozen-layers");
        set_default_valid();
        input_batch_count = 32'd0;
        assert_error(1, "input-batch-count-invalid");
        set_default_valid();
        output_batch_count = 32'd2;
        assert_error(1, "output-batch-count-invalid");
        set_default_valid();
        output_batch = 32'd1;
        assert_error(1, "output-batch-index-invalid");
        set_default_valid();
        input_channels = 32'd0;
        assert_error(1, "input-channels-zero");
        set_default_valid();
        input_height = 32'd0;
        assert_error(1, "input-height-zero");
        set_default_valid();
        input_width = 32'd0;
        assert_error(1, "input-width-zero");
        set_default_valid();
        output_channels = 32'd0;
        assert_error(1, "output-channels-zero");
        set_default_valid();
        output_height = 32'd0;
        assert_error(1, "output-height-zero");
        set_default_valid();
        output_width = 32'd0;
        assert_error(1, "output-width-zero");
        set_default_valid();
        kernel_height = 32'd0;
        assert_error(1, "kernel-height-zero");
        set_default_valid();
        kernel_width = 32'd0;
        assert_error(1, "kernel-width-zero");
        set_default_valid();
        stride_y = 32'd0;
        assert_error(1, "stride-y-zero");
        set_default_valid();
        stride_x = 32'd0;
        assert_error(1, "stride-x-zero");
        set_default_valid();
        padding_value_int8 = 8'sd1;
        assert_error(1, "padding-value-must-match-g0-zero");
        set_default_valid();
        output_channel = 32'd1;
        assert_error(1, "output-channel-out-of-range");
        set_default_valid();
        output_y = 32'd3;
        assert_error(1, "output-y-out-of-range");
        set_default_valid();
        output_x = 32'd3;
        assert_error(1, "output-x-out-of-range");
        set_default_valid();
        reduction_index = 32'd9;
        assert_error(1, "reduction-index-out-of-range");
        set_default_valid();
        output_height = 32'd2;
        assert_error(1, "output-height-descriptor-mismatch");
        set_default_valid();
        output_width = 32'd2;
        assert_error(1, "output-width-descriptor-mismatch");
        set_default_valid();
        pad_top = 32'd2;
        assert_error(1, "padding-shape-descriptor-mismatch");
        set_default_valid();
        input_height = 32'hffff_ffff;
        pad_top = 32'hffff_ffff;
        pad_bottom = 32'hffff_ffff;
        output_height = 32'hffff_ffff;
        assert_error(1, "output-shape-overflow-descriptor");

        set_default_valid();
        input_length_bytes = 32'd8;
        assert_error(2, "input-object-length-does-not-match-shape");
        set_default_valid();
        input_base_address = 32'hffff_ffff;
        assert_error(2, "input-object-crosses-uint32-boundary");
        set_default_valid();
        input_channels = 32'hffff_ffff;
        input_height = 32'd2;
        input_width = 32'd1;
        input_length_bytes = 32'hffff_ffff;
        output_height = 32'd2;
        output_width = 32'd1;
        kernel_height = 32'd1;
        kernel_width = 32'd1;
        stride_y = 32'd1;
        stride_x = 32'd1;
        pad_left = 32'd0;
        pad_right = 32'd0;
        pad_top = 32'd0;
        pad_bottom = 32'd0;
        reduction_index = 32'd0;
        assert_error(2, "input-shape-size-exceeds-uint32-range");

        set_default_valid();
        assert_padding_success();
        set_default_valid();
        input_base_address = 32'hffff_ffff;
        input_length_bytes = 32'd1;
        input_height = 32'd1;
        input_width = 32'd1;
        output_height = 32'd1;
        output_width = 32'd1;
        kernel_height = 32'd1;
        kernel_width = 32'd1;
        stride_y = 32'd1;
        stride_x = 32'd1;
        pad_left = 32'd0;
        pad_right = 32'd0;
        pad_top = 32'd0;
        pad_bottom = 32'd0;
        assert_uint32_last_address();

        if ((record_count != 21345) || (random_point_count != 21000) ||
            (random_tap_count != 20731000) || (directed_case_count != 336) ||
            (directed_tap_count != 331696) || (fixture_point_count != 9) ||
            (fixture_tap_count != 81) || (bad_argument_count != 23) ||
            (bad_range_count != 3) || (boundary_success_count != 1) ||
            (padding_success_count != 1)) begin
            $display("records=%0d random_points=%0d random_taps=%0d directed_cases=%0d directed_taps=%0d fixture_points=%0d fixture_taps=%0d bad_argument=%0d bad_range=%0d boundary=%0d pad_success=%0d",
                     record_count, random_point_count, random_tap_count,
                     directed_case_count, directed_tap_count, fixture_point_count,
                     fixture_tap_count, bad_argument_count, bad_range_count,
                     boundary_success_count, padding_success_count);
            fail("卷积 tap 固定验证数量不匹配");
        end
        $display("PASS: random_taps=%0d directed_taps=%0d fixture_taps=%0d random_points=%0d directed_cases=%0d fixture_points=%0d bad_argument=%0d bad_range=%0d boundary=%0d pad_success=%0d",
                 random_tap_count, directed_tap_count, fixture_tap_count,
                 random_point_count, directed_case_count, fixture_point_count,
                 bad_argument_count, bad_range_count, boundary_success_count,
                 padding_success_count);
        $finish;
    end
endmodule
