// S2A-T08：tiny416 YOLO head 的零拷贝单元素视图查询。
module int8_yolo_view_query (
    input  logic [31:0] head_layer_index,
    input  logic [31:0] head_input_tensor_index,
    input  logic [31:0] head_output_tensor_index,
    input  logic [31:0] source_layer_index,
    input  logic [31:0] source_tensor_index,
    input  logic        source_is_convolution,
    input  logic [31:0] head_base_address,
    input  logic [31:0] head_length_bytes,
    input  logic [31:0] head_channels,
    input  logic [31:0] head_height,
    input  logic [31:0] head_width,
    input  logic [31:0] source_base_address,
    input  logic [31:0] source_length_bytes,
    input  logic [31:0] source_channels,
    input  logic [31:0] source_height,
    input  logic [31:0] source_width,
    input  logic [31:0] anchor_count,
    input  logic [31:0] entries_per_anchor,
    input  logic [31:0] query_anchor_local,
    input  logic [31:0] query_entry,
    input  logic [31:0] query_row,
    input  logic [31:0] query_col,
    output logic [31:0] logical_channel,
    output logic [31:0] byte_offset,
    output logic [31:0] head_byte_address,
    output logic [31:0] source_byte_address,
    output logic        zero_copy_alias,
    output logic [2:0]  error_code
);
    localparam logic [2:0] NONE         = 3'd0;
    localparam logic [2:0] BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] BAD_RANGE    = 3'd2;

    logic [95:0] element_count;
    logic [63:0] channel_count_from_layout;
    logic [63:0] channel_value;
    logic [63:0] offset_value;
    logic [63:0] head_address_value;
    logic [63:0] source_address_value;
    logic [63:0] head_end_exclusive;
    logic [63:0] source_end_exclusive;
    logic [63:0] address_space_limit;

    // 默认清零，所有错误路径都不暴露可用地址。
    always_comb begin
        logical_channel = 32'd0;
        byte_offset = 32'd0;
        head_byte_address = 32'd0;
        source_byte_address = 32'd0;
        zero_copy_alias = 1'b0;
        error_code = NONE;

        element_count = 96'd0;
        channel_count_from_layout = 64'd0;
        channel_value = 64'd0;
        offset_value = 64'd0;
        head_address_value = 64'd0;
        source_address_value = 64'd0;
        head_end_exclusive = 64'd0;
        source_end_exclusive = 64'd0;
        address_space_limit = 64'h0000_0001_0000_0000;

        if ((head_layer_index == 32'd0) ||
            (source_layer_index >= head_layer_index) ||
            (source_layer_index != source_tensor_index) ||
            (({1'b0, source_layer_index} + 33'd1) != {1'b0, head_layer_index}) ||
            !source_is_convolution ||
            (head_input_tensor_index != source_tensor_index) ||
            (head_output_tensor_index != head_input_tensor_index) ||
            (head_base_address != source_base_address) ||
            (head_length_bytes != source_length_bytes) ||
            (head_channels != source_channels) ||
            (head_height != source_height) ||
            (head_width != source_width) ||
            (anchor_count == 32'd0) ||
            (entries_per_anchor == 32'd0) ||
            (head_channels == 32'd0) ||
            (head_height == 32'd0) ||
            (head_width == 32'd0) ||
            (query_anchor_local >= anchor_count) ||
            (query_entry >= entries_per_anchor) ||
            (query_row >= head_height) ||
            (query_col >= head_width)) begin
            error_code = BAD_ARGUMENT;
        end else begin
            element_count = {64'd0, head_channels} *
                            {64'd0, head_height} *
                            {64'd0, head_width};
            channel_count_from_layout = {32'd0, anchor_count} *
                                        {32'd0, entries_per_anchor};
            head_end_exclusive = {32'd0, head_base_address} +
                                 {32'd0, head_length_bytes};
            source_end_exclusive = {32'd0, source_base_address} +
                                   {32'd0, source_length_bytes};

            if ((element_count > 96'h0000_0000_0000_0000_0000_0000_FFFF_FFFF) ||
                (head_length_bytes != element_count[31:0]) ||
                (source_length_bytes != element_count[31:0]) ||
                (channel_count_from_layout != {32'd0, head_channels}) ||
                (head_end_exclusive > address_space_limit) ||
                (source_end_exclusive > address_space_limit)) begin
                error_code = BAD_RANGE;
            end else begin
                channel_value = {32'd0, query_anchor_local} *
                                {32'd0, entries_per_anchor} +
                                {32'd0, query_entry};
                offset_value = (channel_value * {32'd0, head_height} +
                                {32'd0, query_row}) *
                               {32'd0, head_width} +
                               {32'd0, query_col};
                head_address_value = {32'd0, head_base_address} + offset_value;
                source_address_value = {32'd0, source_base_address} + offset_value;

                if ((channel_value >= {32'd0, head_channels}) ||
                    (offset_value >= {32'd0, head_length_bytes}) ||
                    (head_address_value >= address_space_limit) ||
                    (source_address_value >= address_space_limit)) begin
                    error_code = BAD_RANGE;
                end else begin
                    logical_channel = channel_value[31:0];
                    byte_offset = offset_value[31:0];
                    head_byte_address = head_address_value[31:0];
                    source_byte_address = source_address_value[31:0];
                    zero_copy_alias = 1'b1;
                end
            end
        end
    end
endmodule
