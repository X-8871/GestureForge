// 使用 G0 冻结随机/定向向量逐通道验证 route 单元素查询。
module tb_s2a_route_query;
    logic [31:0] source_count;
    logic [31:0] groups;
    logic [31:0] group_id;
    logic [31:0] output_channel;
    logic [31:0] output_y;
    logic [31:0] output_x;

    logic [31:0] source0_base_address;
    logic [31:0] source0_length_bytes;
    logic [31:0] source0_channels;
    logic [31:0] source0_height;
    logic [31:0] source0_width;
    logic [31:0] source0_channel_start;
    logic [31:0] source0_channel_end;
    logic [31:0] source0_multiplier_q31;
    logic signed [7:0] source0_value;

    logic [31:0] source1_base_address;
    logic [31:0] source1_length_bytes;
    logic [31:0] source1_channels;
    logic [31:0] source1_height;
    logic [31:0] source1_width;
    logic [31:0] source1_channel_start;
    logic [31:0] source1_channel_end;
    logic [31:0] source1_multiplier_q31;
    logic signed [7:0] source1_value;

    logic [31:0] output_channels;
    logic [31:0] output_height;
    logic [31:0] output_width;
    logic [31:0] source_index;
    logic [31:0] source_channel;
    logic [31:0] source_address;
    logic signed [7:0] output_value;
    logic [2:0] error_code;

    logic [2047:0] source0_values_packed;
    logic [2047:0] source1_values_packed;
    logic [4095:0] expected_output_values_packed;

    integer vector_fd;
    integer expected_fd;
    integer scan_result;
    integer expected_scan_result;
    integer vector_class;
    integer layer_index_value;
    integer case_index_value;
    integer output_y_value;
    integer output_x_value;
    integer source_count_value;
    integer groups_value;
    integer group_id_value;
    integer output_channels_value;
    integer height_value;
    integer width_value;
    integer source0_base_value;
    integer source0_length_value;
    integer source0_channels_value;
    integer source0_start_value;
    integer source0_end_value;
    integer source1_base_value;
    integer source1_length_value;
    integer source1_channels_value;
    integer source1_start_value;
    integer source1_end_value;
    logic [31:0] source0_multiplier_value;
    logic [31:0] source1_multiplier_value;

    integer output_index;
    integer expected_source_index;
    integer expected_source_channel;
    integer source_local_index;
    integer record_count;
    integer random_spatial_count;
    integer random_query_count;
    integer directed_case_count;
    integer directed_query_count;
    integer fixture_value_count;
    integer bad_argument_count;
    integer bad_range_count;
    integer boundary_success_count;
    longint unsigned expected_offset;
    longint unsigned expected_address_wide;

    int8_route_query dut (
        .source_count(source_count),
        .groups(groups),
        .group_id(group_id),
        .output_channel(output_channel),
        .output_y(output_y),
        .output_x(output_x),
        .source0_base_address(source0_base_address),
        .source0_length_bytes(source0_length_bytes),
        .source0_channels(source0_channels),
        .source0_height(source0_height),
        .source0_width(source0_width),
        .source0_channel_start(source0_channel_start),
        .source0_channel_end(source0_channel_end),
        .source0_multiplier_q31(source0_multiplier_q31),
        .source0_value(source0_value),
        .source1_base_address(source1_base_address),
        .source1_length_bytes(source1_length_bytes),
        .source1_channels(source1_channels),
        .source1_height(source1_height),
        .source1_width(source1_width),
        .source1_channel_start(source1_channel_start),
        .source1_channel_end(source1_channel_end),
        .source1_multiplier_q31(source1_multiplier_q31),
        .source1_value(source1_value),
        .output_channels(output_channels),
        .output_height(output_height),
        .output_width(output_width),
        .source_index(source_index),
        .source_channel(source_channel),
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

    task automatic set_default_valid;
        begin
            source_count = 32'd1;
            groups = 32'd1;
            group_id = 32'd0;
            output_channel = 32'd0;
            output_y = 32'd0;
            output_x = 32'd0;
            source0_base_address = 32'h0000_1000;
            source0_length_bytes = 32'd4;
            source0_channels = 32'd4;
            source0_height = 32'd1;
            source0_width = 32'd1;
            source0_channel_start = 32'd0;
            source0_channel_end = 32'd4;
            source0_multiplier_q31 = 32'h8000_0000;
            source0_value = 8'sd5;
            source1_base_address = 32'd0;
            source1_length_bytes = 32'd0;
            source1_channels = 32'd0;
            source1_height = 32'd0;
            source1_width = 32'd0;
            source1_channel_start = 32'd0;
            source1_channel_end = 32'd0;
            source1_multiplier_q31 = 32'd0;
            source1_value = 8'sd0;
        end
    endtask

    task automatic set_second_source;
        begin
            source_count = 32'd2;
            source1_base_address = 32'h0000_2000;
            source1_length_bytes = 32'd2;
            source1_channels = 32'd2;
            source1_height = 32'd1;
            source1_width = 32'd1;
            source1_channel_start = 32'd0;
            source1_channel_end = 32'd2;
            source1_multiplier_q31 = 32'h8000_0000;
            source1_value = 8'sd7;
        end
    endtask

    task automatic assert_error(input integer expected_code,
                                input string case_name);
        begin
            #1;
            if (error_code !== expected_code[2:0]) begin
                $display("case=%s expected_error=%0d actual_error=%0d",
                         case_name, expected_code, error_code);
                fail("route 错误码与非法刺激不匹配");
            end
            if ((output_channels !== 32'd0) || (output_height !== 32'd0) ||
                (output_width !== 32'd0) || (source_index !== 32'd0) ||
                (source_channel !== 32'd0) || (source_address !== 32'd0) ||
                (output_value !== 8'sd0)) begin
                fail("非法 route 查询必须清零所有结果");
            end
            if (expected_code == 1) begin
                bad_argument_count = bad_argument_count + 1;
            end else if (expected_code == 2) begin
                bad_range_count = bad_range_count + 1;
            end
        end
    endtask

    task automatic assert_valid_boundary;
        begin
            #1;
            if ((error_code !== 3'd0) || (output_channels !== 32'd1) ||
                (output_height !== 32'd1) || (output_width !== 32'd4) ||
                (source_index !== 32'd0) || (source_channel !== 32'd0) ||
                (source_address !== 32'hffff_ffff) ||
                (output_value !== 8'sd127)) begin
                fail("uint32 最大地址字节成功边界不匹配");
            end
            boundary_success_count = boundary_success_count + 1;
        end
    endtask

    initial begin
        source_count = 32'd0;
        groups = 32'd0;
        group_id = 32'd0;
        output_channel = 32'd0;
        output_y = 32'd0;
        output_x = 32'd0;
        source0_base_address = 32'd0;
        source0_length_bytes = 32'd0;
        source0_channels = 32'd0;
        source0_height = 32'd0;
        source0_width = 32'd0;
        source0_channel_start = 32'd0;
        source0_channel_end = 32'd0;
        source0_multiplier_q31 = 32'd0;
        source0_value = 8'sd0;
        source1_base_address = 32'd0;
        source1_length_bytes = 32'd0;
        source1_channels = 32'd0;
        source1_height = 32'd0;
        source1_width = 32'd0;
        source1_channel_start = 32'd0;
        source1_channel_end = 32'd0;
        source1_multiplier_q31 = 32'd0;
        source1_value = 8'sd0;
        record_count = 0;
        random_spatial_count = 0;
        random_query_count = 0;
        directed_case_count = 0;
        directed_query_count = 0;
        fixture_value_count = 0;
        bad_argument_count = 0;
        bad_range_count = 0;
        boundary_success_count = 0;

        vector_fd = $fopen("vectors.dat", "r");
        expected_fd = $fopen("expected.dat", "r");
        if ((vector_fd == 0) || (expected_fd == 0)) begin
            fail("无法打开临时 route 向量或黄金文件");
        end

        scan_result = $fscanf(
            vector_fd,
            "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %h %d %d %d %d %d %h %h %h\n",
            vector_class, layer_index_value, case_index_value,
            output_y_value, output_x_value, source_count_value,
            groups_value, group_id_value, output_channels_value,
            height_value, width_value,
            source0_base_value, source0_length_value, source0_channels_value,
            source0_start_value, source0_end_value, source0_multiplier_value,
            source1_base_value, source1_length_value, source1_channels_value,
            source1_start_value, source1_end_value, source1_multiplier_value,
            source0_values_packed, source1_values_packed
        );
        while (scan_result == 25) begin
            expected_scan_result = $fscanf(expected_fd, "%h\n",
                                            expected_output_values_packed);
            if (expected_scan_result != 1) begin
                fail("route 黄金文件记录数量少于刺激文件");
            end

            source_count = source_count_value[31:0];
            groups = groups_value[31:0];
            group_id = group_id_value[31:0];
            output_y = output_y_value[31:0];
            output_x = output_x_value[31:0];
            source0_base_address = source0_base_value[31:0];
            source0_length_bytes = source0_length_value[31:0];
            source0_channels = source0_channels_value[31:0];
            source0_height = height_value[31:0];
            source0_width = width_value[31:0];
            source0_channel_start = source0_start_value[31:0];
            source0_channel_end = source0_end_value[31:0];
            source0_multiplier_q31 = source0_multiplier_value;
            source1_base_address = source1_base_value[31:0];
            source1_length_bytes = source1_length_value[31:0];
            source1_channels = source1_channels_value[31:0];
            source1_height = height_value[31:0];
            source1_width = width_value[31:0];
            source1_channel_start = source1_start_value[31:0];
            source1_channel_end = source1_end_value[31:0];
            source1_multiplier_q31 = source1_multiplier_value;

            for (output_index = 0; output_index < output_channels_value;
                 output_index = output_index + 1) begin
                output_channel = output_index[31:0];
                if (output_index < (source0_end_value - source0_start_value)) begin
                    expected_source_index = 0;
                    expected_source_channel = source0_start_value + output_index;
                    source_local_index = output_index;
                    source0_value = $signed(
                        source0_values_packed[(source_local_index * 8) +: 8]
                    );
                    source1_value = 8'sd0;
                    expected_offset =
                        (((expected_source_channel * height_value) + output_y_value) *
                         width_value) + output_x_value;
                    expected_address_wide = source0_base_value + expected_offset;
                    if ((expected_offset >= source0_length_value) ||
                        (expected_address_wide > 64'h0000_0000_ffff_ffff)) begin
                        fail("测试平台 route source0 黄金地址越过对象边界");
                    end
                end else begin
                    expected_source_index = 1;
                    expected_source_channel = source1_start_value +
                        (output_index - (source0_end_value - source0_start_value));
                    source_local_index = output_index -
                        (source0_end_value - source0_start_value);
                    source0_value = 8'sd0;
                    source1_value = $signed(
                        source1_values_packed[(source_local_index * 8) +: 8]
                    );
                    expected_offset =
                        (((expected_source_channel * height_value) + output_y_value) *
                         width_value) + output_x_value;
                    expected_address_wide = source1_base_value + expected_offset;
                    if ((expected_offset >= source1_length_value) ||
                        (expected_address_wide > 64'h0000_0000_ffff_ffff)) begin
                        fail("测试平台 route source1 黄金地址越过对象边界");
                    end
                end
                #1;
                if ((error_code !== 3'd0) ||
                    (output_channels !== output_channels_value[31:0]) ||
                    (output_height !== height_value[31:0]) ||
                    (output_width !== width_value[31:0])) begin
                    $display("class=%0d layer=%0d case=%0d output_channel=%0d err=%0d out_channels=%0d",
                             vector_class, layer_index_value, case_index_value,
                             output_index, error_code, output_channels);
                    fail("route 几何或参数校验不匹配");
                end
                if ((source_index !== expected_source_index[31:0]) ||
                    (source_channel !== expected_source_channel[31:0]) ||
                    (source_address !== expected_address_wide[31:0]) ||
                    (output_value !== expected_output_values_packed[(output_index * 8) +: 8])) begin
                    $display("class=%0d layer=%0d case=%0d output_channel=%0d expected_source=%0d:%0d actual_source=%0d:%0d expected_addr=%0d actual_addr=%0d expected_value=%0d actual_value=%0d",
                             vector_class, layer_index_value, case_index_value,
                             output_index, expected_source_index,
                             expected_source_channel, source_index, source_channel,
                             expected_address_wide, source_address,
                             $signed(expected_output_values_packed[(output_index * 8) +: 8]),
                             output_value);
                    fail("route 来源顺序、NCHW 地址或 INT8 输出逐值不匹配");
                end
                if (vector_class == 0) begin
                    random_query_count = random_query_count + 1;
                end else if (vector_class == 1) begin
                    directed_query_count = directed_query_count + 1;
                end else if (vector_class == 2) begin
                    fixture_value_count = fixture_value_count + 1;
                end else begin
                    fail("route 向量类型编号非法");
                end
            end
            if (vector_class == 0) begin
                random_spatial_count = random_spatial_count + 1;
            end else if (vector_class == 1) begin
                directed_case_count = directed_case_count + 1;
            end
            record_count = record_count + 1;

            scan_result = $fscanf(
                vector_fd,
                "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %h %d %d %d %d %d %h %h %h\n",
                vector_class, layer_index_value, case_index_value,
                output_y_value, output_x_value, source_count_value,
                groups_value, group_id_value, output_channels_value,
                height_value, width_value,
                source0_base_value, source0_length_value, source0_channels_value,
                source0_start_value, source0_end_value, source0_multiplier_value,
                source1_base_value, source1_length_value, source1_channels_value,
                source1_start_value, source1_end_value, source1_multiplier_value,
                source0_values_packed, source1_values_packed
            );
        end
        if (scan_result != -1) begin
            fail("route 刺激文件包含不完整记录");
        end
        expected_scan_result = $fscanf(expected_fd, "%h\n",
                                       expected_output_values_packed);
        if (expected_scan_result != -1) begin
            fail("route 黄金文件记录多于刺激文件");
        end
        $fclose(vector_fd);
        $fclose(expected_fd);

        set_default_valid();
        source_count = 32'd0;
        assert_error(1, "source-count-zero");
        set_default_valid();
        source_count = 32'd3;
        assert_error(1, "source-count-three");
        set_default_valid();
        groups = 32'd0;
        assert_error(1, "groups-zero");
        set_default_valid();
        groups = 32'd2;
        group_id = 32'd2;
        assert_error(1, "group-id-out-of-range");
        set_default_valid();
        set_second_source();
        groups = 32'd2;
        assert_error(1, "two-sources-with-group-slice");
        set_default_valid();
        groups = 32'd2;
        source0_length_bytes = 32'd3;
        source0_channels = 32'd3;
        source0_channel_end = 32'd3;
        assert_error(1, "channels-not-divisible-by-groups");
        set_default_valid();
        groups = 32'd2;
        group_id = 32'd1;
        source0_channel_start = 32'd0;
        source0_channel_end = 32'd2;
        assert_error(1, "wrong-group-channel-range");
        set_default_valid();
        source0_channels = 32'd0;
        assert_error(1, "source0-channels-zero");
        set_default_valid();
        source0_height = 32'd0;
        assert_error(1, "source0-height-zero");
        set_default_valid();
        source0_width = 32'd0;
        assert_error(1, "source0-width-zero");
        set_default_valid();
        source0_channel_end = 32'd0;
        assert_error(1, "empty-source0-channel-range");
        set_default_valid();
        source0_channel_end = 32'd5;
        assert_error(1, "source0-channel-range-too-large");
        set_default_valid();
        output_channel = 32'd4;
        assert_error(1, "output-channel-out-of-range");
        set_default_valid();
        output_y = 32'd1;
        assert_error(1, "output-y-out-of-range");
        set_default_valid();
        output_x = 32'd1;
        assert_error(1, "output-x-out-of-range");
        set_default_valid();
        set_second_source();
        source1_height = 32'd2;
        assert_error(1, "source-height-mismatch");
        set_default_valid();
        set_second_source();
        source1_channel_end = 32'd1;
        assert_error(1, "source1-range-must-cover-channels");
        set_default_valid();
        source0_multiplier_q31 = 32'd0;
        assert_error(1, "source0-multiplier-zero");
        set_default_valid();
        source0_multiplier_q31 = 32'h8000_0001;
        assert_error(1, "source0-multiplier-over-q31-one");
        set_default_valid();
        set_second_source();
        source1_multiplier_q31 = 32'd0;
        assert_error(1, "source1-multiplier-zero");
        set_default_valid();
        source0_value = -8'sd128;
        assert_error(1, "source0-symmetric-int8-rejects-minus-128");
        set_default_valid();
        set_second_source();
        output_channel = 32'd4;
        source1_value = -8'sd128;
        assert_error(1, "source1-symmetric-int8-rejects-minus-128");
        set_default_valid();
        set_second_source();
        source1_channels = 32'd0;
        assert_error(1, "source1-channels-zero");

        set_default_valid();
        source0_length_bytes = 32'd3;
        assert_error(2, "source0-object-shorter-than-shape");
        set_default_valid();
        source0_base_address = 32'hffff_fffd;
        assert_error(2, "source0-object-crosses-uint32-address-space");
        set_default_valid();
        set_second_source();
        source1_base_address = 32'hffff_fffd;
        assert_error(2, "source1-object-crosses-uint32-address-space");
        set_default_valid();
        source0_channels = 32'hffff_ffff;
        source0_length_bytes = 32'hffff_ffff;
        source0_channel_end = 32'hffff_ffff;
        source0_height = 32'd2;
        assert_error(2, "source-shape-exceeds-uint32-object-length");

        set_default_valid();
        source0_base_address = 32'hffff_fffc;
        source0_length_bytes = 32'd4;
        source0_channels = 32'd1;
        source0_height = 32'd1;
        source0_width = 32'd4;
        source0_channel_end = 32'd1;
        output_x = 32'd3;
        source0_value = 8'sd127;
        assert_valid_boundary();

        if ((record_count != 11177) || (random_spatial_count != 11000) ||
            (directed_case_count != 176) ||
            (fixture_value_count != 12) || (bad_argument_count != 23) ||
            (bad_range_count != 4) || (boundary_success_count != 1)) begin
            $display("records=%0d random_cases=%0d directed_cases=%0d fixture_values=%0d bad_argument=%0d bad_range=%0d boundary=%0d",
                     record_count, random_spatial_count, directed_case_count,
                     fixture_value_count, bad_argument_count, bad_range_count,
                     boundary_success_count);
            fail("route 固定验证数量不匹配");
        end
        $display("PASS: route_queries=%0d random_cases=%0d directed_cases=%0d fixture_values=%0d bad_argument=%0d bad_range=%0d boundary=%0d",
                 random_query_count + directed_query_count + fixture_value_count,
                 random_spatial_count, directed_case_count, fixture_value_count,
                 bad_argument_count, bad_range_count, boundary_success_count);
        $finish;
    end
endmodule
