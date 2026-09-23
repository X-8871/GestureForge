// 按 G0 冻结向量检查 YOLO head 的别名、通道和地址映射。
module tb_s2a_yolo_view_query;
    logic [31:0] head_layer_index;
    logic [31:0] head_input_tensor_index;
    logic [31:0] head_output_tensor_index;
    logic [31:0] source_layer_index;
    logic [31:0] source_tensor_index;
    logic source_is_convolution;
    logic [31:0] head_base_address;
    logic [31:0] head_length_bytes;
    logic [31:0] head_channels;
    logic [31:0] head_height;
    logic [31:0] head_width;
    logic [31:0] source_base_address;
    logic [31:0] source_length_bytes;
    logic [31:0] source_channels;
    logic [31:0] source_height;
    logic [31:0] source_width;
    logic [31:0] anchor_count;
    logic [31:0] entries_per_anchor;
    logic [31:0] query_anchor_local;
    logic [31:0] query_entry;
    logic [31:0] query_row;
    logic [31:0] query_col;
    logic [31:0] logical_channel;
    logic [31:0] byte_offset;
    logic [31:0] head_byte_address;
    logic [31:0] source_byte_address;
    logic zero_copy_alias;
    logic [2:0] error_code;

    logic [31:0] fields [0:28];
    integer vector_fd;
    integer scan_result;
    integer total_count;
    integer random_count;
    integer directed_count;
    integer bad_argument_count;
    integer bad_range_count;
    integer boundary_count;
    integer vector_class;
    integer vector_number;
    integer index;
    string vector_path;

    int8_yolo_view_query dut (
        .head_layer_index(head_layer_index),
        .head_input_tensor_index(head_input_tensor_index),
        .head_output_tensor_index(head_output_tensor_index),
        .source_layer_index(source_layer_index),
        .source_tensor_index(source_tensor_index),
        .source_is_convolution(source_is_convolution),
        .head_base_address(head_base_address),
        .head_length_bytes(head_length_bytes),
        .head_channels(head_channels),
        .head_height(head_height),
        .head_width(head_width),
        .source_base_address(source_base_address),
        .source_length_bytes(source_length_bytes),
        .source_channels(source_channels),
        .source_height(source_height),
        .source_width(source_width),
        .anchor_count(anchor_count),
        .entries_per_anchor(entries_per_anchor),
        .query_anchor_local(query_anchor_local),
        .query_entry(query_entry),
        .query_row(query_row),
        .query_col(query_col),
        .logical_channel(logical_channel),
        .byte_offset(byte_offset),
        .head_byte_address(head_byte_address),
        .source_byte_address(source_byte_address),
        .zero_copy_alias(zero_copy_alias),
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
            if (logical_channel !== fields[23] ||
                byte_offset !== fields[24] ||
                head_byte_address !== fields[25] ||
                source_byte_address !== fields[26] ||
                zero_copy_alias !== fields[27][0] ||
                error_code !== fields[28][2:0]) begin
                $display("FAIL: vector=%0d class=%0d", vector_number, vector_class);
                $display("  got channel=%h offset=%h head=%h source=%h alias=%b error=%0d",
                         logical_channel, byte_offset, head_byte_address,
                         source_byte_address, zero_copy_alias, error_code);
                $display("  exp channel=%h offset=%h head=%h source=%h alias=%b error=%0d",
                         fields[23], fields[24], fields[25], fields[26],
                         fields[27][0], fields[28][2:0]);
                $fatal(1);
            end

            total_count = total_count + 1;
            case (vector_class)
                0: random_count = random_count + 1;
                1: directed_count = directed_count + 1;
                2: begin
                    if (error_code != 3'd1) fail("BAD_ARGUMENT 向量错误码不匹配");
                    bad_argument_count = bad_argument_count + 1;
                end
                3: begin
                    if (error_code != 3'd2) fail("BAD_RANGE 向量错误码不匹配");
                    bad_range_count = bad_range_count + 1;
                end
                4: begin
                    if ((error_code != 3'd0) || !zero_copy_alias ||
                        (head_byte_address != 32'hFFFF_FFFF))
                        fail("uint32 最大合法字节边界断言失败");
                    boundary_count = boundary_count + 1;
                end
                default: fail("未知向量类别");
            endcase
        end
    endtask

    initial begin
        total_count = 0;
        random_count = 0;
        directed_count = 0;
        bad_argument_count = 0;
        bad_range_count = 0;
        boundary_count = 0;
        vector_number = 0;

        vector_path = "vectors.dat";
        vector_fd = $fopen(vector_path, "r");
        if (vector_fd == 0) fail("无法打开向量文件");

        while (!$feof(vector_fd)) begin
            scan_result = $fscanf(vector_fd,
                "%h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h",
                fields[0], fields[1], fields[2], fields[3], fields[4],
                fields[5], fields[6], fields[7], fields[8], fields[9],
                fields[10], fields[11], fields[12], fields[13], fields[14],
                fields[15], fields[16], fields[17], fields[18], fields[19],
                fields[20], fields[21], fields[22], fields[23], fields[24],
                fields[25], fields[26], fields[27], fields[28]);
            if (scan_result == -1) begin
                break;
            end
            if (scan_result != 29) begin
                $display("FAIL: vector file row has %0d fields", scan_result);
                $fatal(1);
            end

            vector_class = fields[0];
            head_layer_index = fields[1];
            head_input_tensor_index = fields[2];
            head_output_tensor_index = fields[3];
            source_layer_index = fields[4];
            source_tensor_index = fields[5];
            source_is_convolution = fields[6][0];
            head_base_address = fields[7];
            head_length_bytes = fields[8];
            head_channels = fields[9];
            head_height = fields[10];
            head_width = fields[11];
            source_base_address = fields[12];
            source_length_bytes = fields[13];
            source_channels = fields[14];
            source_height = fields[15];
            source_width = fields[16];
            anchor_count = fields[17];
            entries_per_anchor = fields[18];
            query_anchor_local = fields[19];
            query_entry = fields[20];
            query_row = fields[21];
            query_col = fields[22];
            compare_vector();
            vector_number = vector_number + 1;
        end
        $fclose(vector_fd);

        if ((total_count != 2050) || (random_count != 2000) ||
            (directed_count != 34) || (bad_argument_count != 13) ||
            (bad_range_count != 2) || (boundary_count != 1)) begin
            $display("FAIL: totals=%0d random=%0d directed=%0d bad_argument=%0d bad_range=%0d boundary=%0d",
                     total_count, random_count, directed_count,
                     bad_argument_count, bad_range_count, boundary_count);
            $fatal(1);
        end
        $display("PASS: total=2050 random=2000 directed_cases=32 directed_queries=34 bad_argument=13 bad_range=2 boundary=1");
        $finish;
    end
endmodule
