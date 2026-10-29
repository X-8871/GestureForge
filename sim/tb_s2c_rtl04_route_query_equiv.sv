module tb_s2c_rtl04_route_query_equiv;
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
    logic [31:0] old_output_channels;
    logic [31:0] old_output_height;
    logic [31:0] old_output_width;
    logic [31:0] old_source_index;
    logic [31:0] old_source_channel;
    logic [31:0] old_source_address;
    logic signed [7:0] old_output_value;
    logic [2:0] old_error_code;
    logic [31:0] new_output_channels;
    logic [31:0] new_output_height;
    logic [31:0] new_output_width;
    logic [31:0] new_source_index;
    logic [31:0] new_source_channel;
    logic [31:0] new_source_address;
    logic signed [7:0] new_output_value;
    logic [2:0] new_error_code;
    integer seed = 32'h04_29_2026;
    integer sample;

    s2b_route_query #(.FROZEN_ROUTE_SHAPES(1'b1)) old_dut (
        .source_count(source_count), .groups(groups), .group_id(group_id),
        .output_channel(output_channel), .output_y(output_y), .output_x(output_x),
        .source0_base_address(source0_base_address), .source0_length_bytes(source0_length_bytes),
        .source0_channels(source0_channels), .source0_height(source0_height), .source0_width(source0_width),
        .source0_channel_start(source0_channel_start), .source0_channel_end(source0_channel_end),
        .source0_multiplier_q31(source0_multiplier_q31), .source0_value(source0_value),
        .source1_base_address(source1_base_address), .source1_length_bytes(source1_length_bytes),
        .source1_channels(source1_channels), .source1_height(source1_height), .source1_width(source1_width),
        .source1_channel_start(source1_channel_start), .source1_channel_end(source1_channel_end),
        .source1_multiplier_q31(source1_multiplier_q31), .source1_value(source1_value),
        .output_channels(old_output_channels), .output_height(old_output_height), .output_width(old_output_width),
        .source_index(old_source_index), .source_channel(old_source_channel), .source_address(old_source_address),
        .output_value(old_output_value), .error_code(old_error_code)
    );

    s2b_route_query_candidate #(.FROZEN_ROUTE_SHAPES(1'b1)) new_dut (
        .source_count(source_count), .groups(groups), .group_id(group_id),
        .output_channel(output_channel), .output_y(output_y), .output_x(output_x),
        .source0_base_address(source0_base_address), .source0_length_bytes(source0_length_bytes),
        .source0_channels(source0_channels), .source0_height(source0_height), .source0_width(source0_width),
        .source0_channel_start(source0_channel_start), .source0_channel_end(source0_channel_end),
        .source0_multiplier_q31(source0_multiplier_q31), .source0_value(source0_value),
        .source1_base_address(source1_base_address), .source1_length_bytes(source1_length_bytes),
        .source1_channels(source1_channels), .source1_height(source1_height), .source1_width(source1_width),
        .source1_channel_start(source1_channel_start), .source1_channel_end(source1_channel_end),
        .source1_multiplier_q31(source1_multiplier_q31), .source1_value(source1_value),
        .output_channels(new_output_channels), .output_height(new_output_height), .output_width(new_output_width),
        .source_index(new_source_index), .source_channel(new_source_channel), .source_address(new_source_address),
        .output_value(new_output_value), .error_code(new_error_code)
    );

    task automatic compare_outputs;
        begin
            #1;
            if ({old_output_channels, old_output_height, old_output_width, old_source_index,
                 old_source_channel, old_source_address, old_output_value, old_error_code} !==
                {new_output_channels, new_output_height, new_output_width, new_source_index,
                 new_source_channel, new_source_address, new_output_value, new_error_code}) begin
                $fatal(1, "逐位差异 sample=%0d", sample);
            end
        end
    endtask

    initial begin
        source_count = 0;
        groups = 0;
        group_id = 0;
        output_channel = 0;
        output_y = 0;
        output_x = 0;
        source0_base_address = 0;
        source0_length_bytes = 0;
        source0_channels = 0;
        source0_height = 0;
        source0_width = 0;
        source0_channel_start = 0;
        source0_channel_end = 0;
        source0_multiplier_q31 = 0;
        source0_value = 0;
        source1_base_address = 0;
        source1_length_bytes = 0;
        source1_channels = 0;
        source1_height = 0;
        source1_width = 0;
        source1_channel_start = 0;
        source1_channel_end = 0;
        source1_multiplier_q31 = 0;
        source1_value = 0;
        sample = 0;
        compare_outputs();

        for (sample = 1; sample <= 1024; sample = sample + 1) begin
            source_count = $urandom(seed);
            groups = $urandom(seed);
            group_id = $urandom(seed);
            output_channel = $urandom(seed);
            output_y = $urandom(seed);
            output_x = $urandom(seed);
            source0_base_address = $urandom(seed);
            source0_length_bytes = $urandom(seed);
            source0_channels = $urandom(seed);
            source0_height = $urandom(seed);
            source0_width = $urandom(seed);
            source0_channel_start = $urandom(seed);
            source0_channel_end = $urandom(seed);
            source0_multiplier_q31 = $urandom(seed);
            source0_value = $urandom(seed);
            source1_base_address = $urandom(seed);
            source1_length_bytes = $urandom(seed);
            source1_channels = $urandom(seed);
            source1_height = $urandom(seed);
            source1_width = $urandom(seed);
            source1_channel_start = $urandom(seed);
            source1_channel_end = $urandom(seed);
            source1_multiplier_q31 = $urandom(seed);
            source1_value = $urandom(seed);
            compare_outputs();
        end

        $display("RTL04_EQUIV_PASS seed=0x%08x samples=1025", 32'h04_29_2026);
        $finish;
    end
endmodule
