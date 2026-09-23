// 按 G0 directed 权重值与 T09 随机向量检查 GFINT8W1 字节地址。
module tb_s2a_conv_weight_address;
    logic [31:0] layer_index;
    logic [31:0] weight_layer_index;
    logic [31:0] groups;
    logic [31:0] output_channels;
    logic [31:0] input_channels;
    logic [31:0] kernel_height;
    logic [31:0] kernel_width;
    logic [31:0] quantized_weight_offset;
    logic [31:0] quantized_weight_bytes;
    logic [31:0] weight_package_base_address;
    logic [31:0] weight_package_length_bytes;
    logic [31:0] query_output_channel;
    logic [31:0] query_input_channel;
    logic [31:0] query_kernel_y;
    logic [31:0] query_kernel_x;
    logic [31:0] reduction_index;
    logic [31:0] layer_weight_byte_offset;
    logic [31:0] package_byte_offset;
    logic [31:0] weight_byte_address;
    logic [2:0] error_code;

    logic [31:0] fields [0:22];
    integer vector_fd;
    integer scan_result;
    integer total_count;
    integer random_count;
    integer directed_count;
    integer layer_boundary_count;
    integer uint32_boundary_count;
    integer bad_argument_count;
    integer bad_range_count;
    integer directed_value_count;
    integer vector_class;
    integer vector_number;
    string vector_path;

    int8_conv_weight_address dut (
        .layer_index(layer_index),
        .weight_layer_index(weight_layer_index),
        .groups(groups),
        .output_channels(output_channels),
        .input_channels(input_channels),
        .kernel_height(kernel_height),
        .kernel_width(kernel_width),
        .quantized_weight_offset(quantized_weight_offset),
        .quantized_weight_bytes(quantized_weight_bytes),
        .weight_package_base_address(weight_package_base_address),
        .weight_package_length_bytes(weight_package_length_bytes),
        .query_output_channel(query_output_channel),
        .query_input_channel(query_input_channel),
        .query_kernel_y(query_kernel_y),
        .query_kernel_x(query_kernel_x),
        .reduction_index(reduction_index),
        .layer_weight_byte_offset(layer_weight_byte_offset),
        .package_byte_offset(package_byte_offset),
        .weight_byte_address(weight_byte_address),
        .error_code(error_code)
    );

    task automatic fail(input string message);
        begin
            $display("FAIL: %s", message);
            $fatal(1);
        end
    endtask

    task automatic compare_vector;
        begin
            #1;
            if (reduction_index !== fields[16] ||
                layer_weight_byte_offset !== fields[17] ||
                package_byte_offset !== fields[18] ||
                weight_byte_address !== fields[19] ||
                error_code !== fields[22][2:0]) begin
                $display("FAIL: vector=%0d class=%0d", vector_number, vector_class);
                $display("  got reduction=%h layer_offset=%h package_offset=%h address=%h error=%0d",
                         reduction_index, layer_weight_byte_offset, package_byte_offset,
                         weight_byte_address, error_code);
                $display("  exp reduction=%h layer_offset=%h package_offset=%h address=%h error=%0d",
                         fields[16], fields[17], fields[18], fields[19], fields[22][2:0]);
                $fatal(1);
            end

            total_count = total_count + 1;
            case (vector_class)
                0: begin
                    random_count = random_count + 1;
                    if (fields[20] != 32'd0) fail("随机查询不应伪造黄金权重值");
                end
                1: begin
                    directed_count = directed_count + 1;
                    if ((fields[20] != 32'd1) || (fields[21] == 32'd128))
                        fail("G0 directed 权重黄金值缺失或超出对称 INT8 域");
                    directed_value_count = directed_value_count + 1;
                end
                2: begin
                    layer_boundary_count = layer_boundary_count + 1;
                    if (fields[20] != 32'd0) fail("边界地址不应伪造权重字节值");
                end
                3: begin
                    uint32_boundary_count = uint32_boundary_count + 1;
                    if ((error_code != 3'd0) ||
                        (weight_byte_address != 32'hFFFF_FFFF))
                        fail("uint32 最大权重字节地址边界断言失败");
                end
                4: begin
                    if ((error_code != 3'd1) ||
                        (reduction_index != 32'd0) ||
                        (layer_weight_byte_offset != 32'd0) ||
                        (package_byte_offset != 32'd0) ||
                        (weight_byte_address != 32'd0))
                        fail("BAD_ARGUMENT 必须清零所有偏移和地址");
                    bad_argument_count = bad_argument_count + 1;
                end
                5: begin
                    if ((error_code != 3'd2) ||
                        (reduction_index != 32'd0) ||
                        (layer_weight_byte_offset != 32'd0) ||
                        (package_byte_offset != 32'd0) ||
                        (weight_byte_address != 32'd0))
                        fail("BAD_RANGE 必须清零所有偏移和地址");
                    bad_range_count = bad_range_count + 1;
                end
                default: fail("未知向量类别");
            endcase
        end
    endtask

    initial begin
        total_count = 0;
        random_count = 0;
        directed_count = 0;
        layer_boundary_count = 0;
        uint32_boundary_count = 0;
        bad_argument_count = 0;
        bad_range_count = 0;
        directed_value_count = 0;
        vector_number = 0;
        vector_path = "vectors.dat";
        vector_fd = $fopen(vector_path, "r");
        if (vector_fd == 0) fail("无法打开临时向量文件");

        while (!$feof(vector_fd)) begin
            scan_result = $fscanf(vector_fd,
                "%h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h",
                fields[0], fields[1], fields[2], fields[3], fields[4],
                fields[5], fields[6], fields[7], fields[8], fields[9],
                fields[10], fields[11], fields[12], fields[13], fields[14],
                fields[15], fields[16], fields[17], fields[18], fields[19],
                fields[20], fields[21], fields[22]);
            if (scan_result == -1) break;
            if (scan_result != 23) begin
                $display("FAIL: vector row has %0d fields", scan_result);
                $fatal(1);
            end

            vector_class = fields[0];
            layer_index = fields[1];
            weight_layer_index = fields[2];
            groups = fields[3];
            output_channels = fields[4];
            input_channels = fields[5];
            kernel_height = fields[6];
            kernel_width = fields[7];
            quantized_weight_offset = fields[8];
            quantized_weight_bytes = fields[9];
            weight_package_base_address = fields[10];
            weight_package_length_bytes = fields[11];
            query_output_channel = fields[12];
            query_input_channel = fields[13];
            query_kernel_y = fields[14];
            query_kernel_x = fields[15];
            compare_vector();
            vector_number = vector_number + 1;
        end
        $fclose(vector_fd);

        if ((total_count != 352790) || (random_count != 21000) ||
            (directed_count != 331696) || (directed_value_count != 331696) ||
            (layer_boundary_count != 84) || (uint32_boundary_count != 1) ||
            (bad_argument_count != 6) || (bad_range_count != 3)) begin
            $display("FAIL: total=%0d random=%0d directed=%0d directed_values=%0d edges=%0d uint32_boundary=%0d bad_argument=%0d bad_range=%0d",
                     total_count, random_count, directed_count,
                     directed_value_count, layer_boundary_count,
                     uint32_boundary_count, bad_argument_count, bad_range_count);
            $fatal(1);
        end
        $display("PASS: total=352790 random=21000 directed=331696 directed_values=331696 layer_edges=84 uint32_boundary=1 bad_argument=6 bad_range=3");
        $finish;
    end
endmodule
