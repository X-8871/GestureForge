// S2A-T64：按冻结 descriptor ROM 串行复用四类算子引擎。
module s2a_network_backend (
    input  logic        clk,
    input  logic        hard_reset,
    input  logic        abort,
    input  logic        backend_start,
    input  logic        buffer_owner_pl,
    input  logic [31:0] input_base_address,
    input  logic [31:0] input_length_bytes,
    input  logic [31:0] weight_package_base_address,
    input  logic [31:0] weight_package_length_bytes,

    output logic        mem_valid,
    output logic        mem_write,
    output logic [31:0] mem_addr,
    output logic [31:0] mem_wdata,
    output logic [3:0]  mem_rstrb,
    output logic [3:0]  mem_wstrb,
    input  logic        mem_ready,
    input  logic [31:0] mem_rdata,
    input  logic [2:0]  mem_error_code,

    output logic        backend_memory_error_valid,
    output logic [2:0]  backend_memory_error_code,
    output logic        operator_result_valid,
    output logic [2:0]  operator_error_code
);
    import s2a_network_descriptor_pkg::*;

    localparam logic [2:0] NONE = 3'd0;
    localparam logic [2:0] BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] BAD_RANGE = 3'd2;
    localparam logic [2:0] BAD_LENGTH = 3'd3;
    localparam logic [2:0] INTERNAL = 3'd6;

    typedef enum logic [2:0] {
        ST_IDLE,
        ST_DISPATCH,
        ST_WAIT_CONV,
        ST_WAIT_MAXPOOL,
        ST_WAIT_ROUTE,
        ST_WAIT_UPSAMPLE
    } state_t;

    state_t state;
    logic [5:0] layer_cursor;
    logic [31:0] output_element_index;
    logic response_pending;
    logic [31:0] response_data_latched;
    logic [2:0] response_error_latched;
    logic [2:0] response_target_latched;

    logic [2:0] current_op;
    logic [1:0] current_input_count;
    logic [31:0] source_base [0:1];
    logic [31:0] source_length [0:1];
    logic [15:0] source_n [0:1];
    logic [15:0] source_c [0:1];
    logic [15:0] source_h [0:1];
    logic [15:0] source_w [0:1];
    logic [15:0] source_route_start [0:1];
    logic [15:0] source_route_end [0:1];
    logic [31:0] output_base;
    logic [31:0] output_length;
    logic [15:0] output_n;
    logic [15:0] output_c;
    logic [15:0] output_h;
    logic [15:0] output_w;
    logic [63:0] output_plane_elements;
    logic [63:0] output_batch_elements;
    logic [63:0] output_element_count;
    logic [31:0] decoded_batch;
    logic [31:0] decoded_channel;
    logic [31:0] decoded_y;
    logic [31:0] decoded_x;
    logic [31:0] mq_index;
    logic descriptor_valid;
    logic alias_valid;
    logic descriptor_fault;
    logic is_alias_row;
    logic [5:0] alias_layer_index;
    logic [63:0] alias_output_plane_elements;
    logic [63:0] alias_output_element_count;

    logic conv_start_valid, conv_start_ready;
    logic maxpool_start_valid, maxpool_start_ready;
    logic route_start_valid, route_start_ready;
    logic upsample_start_valid, upsample_start_ready;
    logic conv_cancel, maxpool_cancel, route_cancel, upsample_cancel;
    logic conv_req_valid, conv_req_ready, conv_req_write;
    logic [31:0] conv_req_addr, conv_req_wdata;
    logic [3:0] conv_req_rstrb, conv_req_wstrb;
    logic maxpool_req_valid, maxpool_req_ready, maxpool_req_write;
    logic [31:0] maxpool_req_addr, maxpool_req_wdata;
    logic [3:0] maxpool_req_rstrb, maxpool_req_wstrb;
    logic route_req_valid, route_req_ready, route_req_write;
    logic [31:0] route_req_addr, route_req_wdata;
    logic [3:0] route_req_rstrb, route_req_wstrb;
    logic upsample_req_valid, upsample_req_ready, upsample_req_write;
    logic [31:0] upsample_req_addr, upsample_req_wdata;
    logic [3:0] upsample_req_rstrb, upsample_req_wstrb;
    logic conv_rsp_valid, maxpool_rsp_valid, route_rsp_valid, upsample_rsp_valid;
    logic [31:0] conv_rsp_data, maxpool_rsp_data, route_rsp_data, upsample_rsp_data;
    logic [2:0] conv_rsp_error, maxpool_rsp_error, route_rsp_error, upsample_rsp_error;
    logic conv_result_valid, conv_result_ready;
    logic [31:0] conv_result_address;
    logic [7:0] conv_result_value;
    logic [2:0] conv_result_error;
    logic maxpool_result_valid, maxpool_result_ready;
    logic [127:0] maxpool_tap_addresses;
    logic [31:0] maxpool_result_address;
    logic [7:0] maxpool_result_value;
    logic [2:0] maxpool_result_error;
    logic route_result_valid, route_result_ready;
    logic [31:0] route_result_source_index;
    logic [31:0] route_result_source_address;
    logic [31:0] route_result_address;
    logic [7:0] route_result_value;
    logic [2:0] route_result_error;
    logic upsample_result_valid, upsample_result_ready;
    logic [31:0] upsample_result_source_address;
    logic [31:0] upsample_result_address;
    logic [7:0] upsample_result_value;
    logic [2:0] upsample_result_error;

    logic selected_req_valid;
    logic selected_req_write;
    logic [31:0] selected_req_addr;
    logic [31:0] selected_req_wdata;
    logic [3:0] selected_req_rstrb;
    logic [3:0] selected_req_wstrb;
    logic selected_result_valid;
    logic [2:0] selected_result_error;
    logic memory_handshake;
    logic selected_start_ready;

    function automatic logic [2:0] normalize_engine_error(input logic [2:0] code);
        begin
            case (code)
                3'd0: normalize_engine_error = NONE;
                3'd1, 3'd2, 3'd3, 3'd4, 3'd5, 3'd6, 3'd7:
                    normalize_engine_error = code;
                default: normalize_engine_error = INTERNAL;
            endcase
        end
    endfunction

    // 冻结包 activation 枚举映射到卷积引擎的方向性 M/Q 选择编码。
    function automatic logic [1:0] map_conv_activation(input logic [1:0] descriptor_activation);
        begin
            case (descriptor_activation)
                S2A_ACT_NONE, S2A_ACT_LINEAR: map_conv_activation = 2'd0;
                S2A_ACT_LEAKY: map_conv_activation = 2'd1;
                default: map_conv_activation = 2'd3;
            endcase
        end
    endfunction

    always_comb begin
        current_op = S2A_OP[layer_cursor];
        current_input_count = S2A_INPUT_COUNT[layer_cursor];
        output_base = S2A_OUTPUT_ADDRESS[layer_cursor];
        output_length = S2A_OUTPUT_LENGTH_BYTES[layer_cursor];
        output_n = S2A_OUTPUT_N[layer_cursor];
        output_c = S2A_OUTPUT_C[layer_cursor];
        output_h = S2A_OUTPUT_H[layer_cursor];
        output_w = S2A_OUTPUT_W[layer_cursor];
        output_plane_elements = {48'd0, output_h} * {48'd0, output_w};
        output_batch_elements = {48'd0, output_c} * output_plane_elements;
        output_element_count = {48'd0, output_n} * output_batch_elements;
        decoded_batch = 32'd0;
        decoded_channel = 32'd0;
        decoded_y = 32'd0;
        decoded_x = 32'd0;
        if ((output_plane_elements != 64'd0) &&
            (output_batch_elements != 64'd0) && (output_w != 16'd0)) begin
            decoded_batch = output_element_index / output_batch_elements;
            decoded_channel = (output_element_index / output_plane_elements) % output_c;
            decoded_y = (output_element_index / {48'd0, output_w}) % output_h;
            decoded_x = output_element_index % output_w;
        end

        for (integer source_slot = 0; source_slot < 2; source_slot = source_slot + 1) begin
            source_base[source_slot] = 32'd0;
            source_length[source_slot] = 32'd0;
            source_n[source_slot] = 16'd0;
            source_c[source_slot] = 16'd0;
            source_h[source_slot] = 16'd0;
            source_w[source_slot] = 16'd0;
            source_route_start[source_slot] = 16'd0;
            source_route_end[source_slot] = 16'd0;
            if (source_slot < current_input_count) begin
                if ((layer_cursor == 6'd0) && (source_slot == 0) &&
                    (S2A_INPUT_KIND[layer_cursor][source_slot] == S2A_INPUT_NETWORK)) begin
                    source_base[source_slot] = input_base_address;
                    source_length[source_slot] = input_length_bytes;
                end else begin
                    source_base[source_slot] = S2A_INPUT_ADDRESS[layer_cursor][source_slot];
                    source_length[source_slot] = S2A_INPUT_LENGTH_BYTES[layer_cursor][source_slot];
                end
                source_n[source_slot] = S2A_INPUT_N[layer_cursor][source_slot];
                source_c[source_slot] = S2A_INPUT_C[layer_cursor][source_slot];
                source_h[source_slot] = S2A_INPUT_H[layer_cursor][source_slot];
                source_w[source_slot] = S2A_INPUT_W[layer_cursor][source_slot];
                source_route_start[source_slot] = S2A_ROUTE_CHANNEL_START[layer_cursor][source_slot];
                source_route_end[source_slot] = S2A_ROUTE_CHANNEL_END[layer_cursor][source_slot];
            end
        end

        mq_index = {16'd0, S2A_T23_MQ_BASE[layer_cursor]} + decoded_channel;
        alias_layer_index = S2A_OUTPUT_ALIAS_LAYER_INDEX[layer_cursor];
        is_alias_row = (current_op == S2A_OP_YOLO);
        alias_valid = 1'b0;
        if (is_alias_row &&
            (S2A_OUTPUT_MEMORY_WRITE_REQUIRED[layer_cursor] == 1'b0) &&
            (S2A_OUTPUT_ALLOCATION_KIND[layer_cursor] == S2A_OUTPUT_HEAD_ALIAS) &&
            (alias_layer_index < S2A_LAYER_COUNT)) begin
            alias_output_plane_elements =
                {48'd0, S2A_OUTPUT_H[alias_layer_index]} *
                {48'd0, S2A_OUTPUT_W[alias_layer_index]};
            alias_output_element_count =
                {48'd0, S2A_OUTPUT_N[alias_layer_index]} *
                {48'd0, S2A_OUTPUT_C[alias_layer_index]} *
                alias_output_plane_elements;
            alias_valid =
                (S2A_OUTPUT_TENSOR_INDEX[alias_layer_index] ==
                 S2A_OUTPUT_TENSOR_INDEX[layer_cursor]) &&
                (S2A_OUTPUT_ADDRESS[alias_layer_index] == output_base) &&
                (S2A_OUTPUT_LENGTH_BYTES[alias_layer_index] == output_length) &&
                (S2A_OUTPUT_N[alias_layer_index] == output_n) &&
                (S2A_OUTPUT_C[alias_layer_index] == output_c) &&
                (S2A_OUTPUT_H[alias_layer_index] == output_h) &&
                (S2A_OUTPUT_W[alias_layer_index] == output_w) &&
                (alias_output_element_count == output_element_count);
        end else begin
            alias_output_plane_elements = 64'd0;
            alias_output_element_count = 64'd0;
        end

        descriptor_valid = 1'b1;
        if ((S2A_LAYER_INDEX[layer_cursor] != layer_cursor) ||
            (current_input_count == 2'd0) || (current_input_count > S2A_MAX_INPUTS) ||
            (output_n != 16'd1) || (output_c == 16'd0) ||
            (output_h == 16'd0) || (output_w == 16'd0) ||
            (output_length == 32'd0) || (output_element_count == 64'd0)) begin
            descriptor_valid = 1'b0;
        end
        for (integer validate_slot = 0; validate_slot < 2; validate_slot = validate_slot + 1) begin
            if (validate_slot < current_input_count) begin
                if ((source_n[validate_slot] != 16'd1) ||
                    (source_c[validate_slot] == 16'd0) ||
                    (source_h[validate_slot] == 16'd0) ||
                    (source_w[validate_slot] == 16'd0) ||
                    (source_length[validate_slot] == 32'd0)) begin
                    descriptor_valid = 1'b0;
                end
                if ((S2A_INPUT_KIND[layer_cursor][validate_slot] == S2A_INPUT_NETWORK) &&
                    !((layer_cursor == 6'd0) && (validate_slot == 0))) begin
                    descriptor_valid = 1'b0;
                end
            end
        end
        if (is_alias_row) begin
            if (!alias_valid) descriptor_valid = 1'b0;
        end else if ((S2A_OUTPUT_MEMORY_WRITE_REQUIRED[layer_cursor] != 1'b1) ||
                     (S2A_OUTPUT_ALLOCATION_KIND[layer_cursor] != S2A_OUTPUT_OWNED)) begin
            descriptor_valid = 1'b0;
        end
        if (current_op == S2A_OP_CONV) begin
            if ((current_input_count != 2'd1) ||
                (S2A_T23_MQ_CHANNEL_COUNT[layer_cursor] != output_c) ||
                (mq_index >= S2A_CONV_CHANNEL_COUNT) ||
                (({16'd0, S2A_T23_MQ_BASE[layer_cursor]} +
                  {16'd0, S2A_T23_MQ_CHANNEL_COUNT[layer_cursor]}) >
                 S2A_CONV_CHANNEL_COUNT) ||
                (map_conv_activation(S2A_ACTIVATION[layer_cursor]) == 2'd3) ||
                (S2A_WEIGHT_LAYER_INDEX[layer_cursor] != S2A_LAYER_INDEX[layer_cursor])) begin
                descriptor_valid = 1'b0;
            end
        end else if ((current_op == S2A_OP_MAXPOOL) ||
                     (current_op == S2A_OP_UPSAMPLE)) begin
            if (current_input_count != 2'd1) descriptor_valid = 1'b0;
        end else if (current_op == S2A_OP_ROUTE) begin
            if ((current_input_count != 2'd1) && (current_input_count != 2'd2))
                descriptor_valid = 1'b0;
        end else if (!is_alias_row) begin
            descriptor_valid = 1'b0;
        end

        descriptor_fault = !descriptor_valid;

        conv_start_valid = (state == ST_DISPATCH) && buffer_owner_pl &&
                           descriptor_valid && (current_op == S2A_OP_CONV);
        maxpool_start_valid = (state == ST_DISPATCH) && buffer_owner_pl &&
                              descriptor_valid && (current_op == S2A_OP_MAXPOOL);
        route_start_valid = (state == ST_DISPATCH) && buffer_owner_pl &&
                            descriptor_valid && (current_op == S2A_OP_ROUTE);
        upsample_start_valid = (state == ST_DISPATCH) && buffer_owner_pl &&
                               descriptor_valid && (current_op == S2A_OP_UPSAMPLE);
        selected_start_ready = 1'b0;
        case (current_op)
            S2A_OP_CONV: selected_start_ready = conv_start_ready;
            S2A_OP_MAXPOOL: selected_start_ready = maxpool_start_ready;
            S2A_OP_ROUTE: selected_start_ready = route_start_ready;
            S2A_OP_UPSAMPLE: selected_start_ready = upsample_start_ready;
            default: selected_start_ready = 1'b0;
        endcase

        selected_req_valid = 1'b0;
        selected_req_write = 1'b0;
        selected_req_addr = 32'd0;
        selected_req_wdata = 32'd0;
        selected_req_rstrb = 4'd0;
        selected_req_wstrb = 4'd0;
        case (state)
            ST_WAIT_CONV: begin
                selected_req_valid = conv_req_valid;
                selected_req_write = conv_req_write;
                selected_req_addr = conv_req_addr;
                selected_req_wdata = conv_req_wdata;
                selected_req_rstrb = conv_req_rstrb;
                selected_req_wstrb = conv_req_wstrb;
            end
            ST_WAIT_MAXPOOL: begin
                selected_req_valid = maxpool_req_valid;
                selected_req_write = maxpool_req_write;
                selected_req_addr = maxpool_req_addr;
                selected_req_wdata = maxpool_req_wdata;
                selected_req_rstrb = maxpool_req_rstrb;
                selected_req_wstrb = maxpool_req_wstrb;
            end
            ST_WAIT_ROUTE: begin
                selected_req_valid = route_req_valid;
                selected_req_write = route_req_write;
                selected_req_addr = route_req_addr;
                selected_req_wdata = route_req_wdata;
                selected_req_rstrb = route_req_rstrb;
                selected_req_wstrb = route_req_wstrb;
            end
            ST_WAIT_UPSAMPLE: begin
                selected_req_valid = upsample_req_valid;
                selected_req_write = upsample_req_write;
                selected_req_addr = upsample_req_addr;
                selected_req_wdata = upsample_req_wdata;
                selected_req_rstrb = upsample_req_rstrb;
                selected_req_wstrb = upsample_req_wstrb;
            end
            default: begin end
        endcase

        mem_valid = selected_req_valid && buffer_owner_pl && !hard_reset &&
                    !abort && !response_pending;
        mem_write = mem_valid && selected_req_write;
        mem_addr = selected_req_addr;
        mem_wdata = selected_req_wdata;
        mem_rstrb = mem_valid ? selected_req_rstrb : 4'd0;
        mem_wstrb = mem_valid ? selected_req_wstrb : 4'd0;
        conv_req_ready = (state == ST_WAIT_CONV) && mem_valid && mem_ready;
        maxpool_req_ready = (state == ST_WAIT_MAXPOOL) && mem_valid && mem_ready;
        route_req_ready = (state == ST_WAIT_ROUTE) && mem_valid && mem_ready;
        upsample_req_ready = (state == ST_WAIT_UPSAMPLE) && mem_valid && mem_ready;
        memory_handshake = mem_valid && mem_ready;
        backend_memory_error_valid = memory_handshake && (mem_error_code != NONE);
        backend_memory_error_code = mem_error_code;

        conv_rsp_valid = response_pending && (response_target_latched == S2A_OP_CONV) &&
                         !hard_reset && !abort;
        maxpool_rsp_valid = response_pending && (response_target_latched == S2A_OP_MAXPOOL) &&
                            !hard_reset && !abort;
        route_rsp_valid = response_pending && (response_target_latched == S2A_OP_ROUTE) &&
                          !hard_reset && !abort;
        upsample_rsp_valid = response_pending && (response_target_latched == S2A_OP_UPSAMPLE) &&
                             !hard_reset && !abort;
        conv_rsp_data = response_data_latched;
        maxpool_rsp_data = response_data_latched;
        route_rsp_data = response_data_latched;
        upsample_rsp_data = response_data_latched;
        conv_rsp_error = response_error_latched;
        maxpool_rsp_error = response_error_latched;
        route_rsp_error = response_error_latched;
        upsample_rsp_error = response_error_latched;

        selected_result_valid = 1'b0;
        selected_result_error = INTERNAL;
        conv_result_ready = !hard_reset && (state == ST_WAIT_CONV) && conv_result_valid;
        maxpool_result_ready = !hard_reset && (state == ST_WAIT_MAXPOOL) && maxpool_result_valid;
        route_result_ready = !hard_reset && (state == ST_WAIT_ROUTE) && route_result_valid;
        upsample_result_ready = !hard_reset && (state == ST_WAIT_UPSAMPLE) && upsample_result_valid;
        case (state)
            ST_WAIT_CONV: begin
                selected_result_valid = conv_result_valid && conv_result_ready;
                selected_result_error = conv_result_error;
            end
            ST_WAIT_MAXPOOL: begin
                selected_result_valid = maxpool_result_valid && maxpool_result_ready;
                selected_result_error = maxpool_result_error;
            end
            ST_WAIT_ROUTE: begin
                selected_result_valid = route_result_valid && route_result_ready;
                selected_result_error = route_result_error;
            end
            ST_WAIT_UPSAMPLE: begin
                selected_result_valid = upsample_result_valid && upsample_result_ready;
                selected_result_error = upsample_result_error;
            end
            default: begin end
        endcase
    end

    always_comb begin
        operator_result_valid = 1'b0;
        operator_error_code = NONE;
        if (!hard_reset && !abort && buffer_owner_pl) begin
            case (state)
                ST_DISPATCH: begin
                    if ((layer_cursor >= S2A_LAYER_COUNT) || descriptor_fault ||
                        (!is_alias_row && !selected_start_ready) ||
                        (is_alias_row && !alias_valid)) begin
                        operator_result_valid = 1'b1;
                        operator_error_code = INTERNAL;
                    end else if (is_alias_row &&
                                 ((layer_cursor + 6'd1) >= S2A_LAYER_COUNT)) begin
                        operator_result_valid = 1'b1;
                        operator_error_code = NONE;
                    end
                end
                ST_WAIT_CONV, ST_WAIT_MAXPOOL, ST_WAIT_ROUTE, ST_WAIT_UPSAMPLE: begin
                    if (selected_result_valid &&
                        (normalize_engine_error(selected_result_error) != NONE)) begin
                        operator_result_valid = 1'b1;
                        operator_error_code = normalize_engine_error(selected_result_error);
                    end else if (selected_result_valid &&
                                 (({32'd0, output_element_index} + 64'd1) >=
                                  output_element_count) &&
                                 ((layer_cursor + 6'd1) >= S2A_LAYER_COUNT)) begin
                        operator_result_valid = 1'b1;
                        operator_error_code = NONE;
                    end
                end
                ST_IDLE: begin end
                default: begin
                    operator_result_valid = 1'b1;
                    operator_error_code = INTERNAL;
                end
            endcase
        end
    end

    s2a_conv_engine u_conv_engine (
        .clk(clk), .hard_reset(hard_reset), .abort(abort),
        .buffer_owner_pl(buffer_owner_pl),
        .start_valid(conv_start_valid), .start_ready(conv_start_ready),
        .layer_index({26'd0, S2A_LAYER_INDEX[layer_cursor]}),
        .weight_layer_index({26'd0, S2A_WEIGHT_LAYER_INDEX[layer_cursor]}),
        .input_base_address(source_base[0]), .input_length_bytes(source_length[0]),
        .input_batch_count({16'd0, source_n[0]}),
        .input_channels({16'd0, source_c[0]}), .input_height({16'd0, source_h[0]}),
        .input_width({16'd0, source_w[0]}),
        .output_base_address(output_base), .output_length_bytes(output_length),
        .output_batch_count({16'd0, output_n}), .output_channels({16'd0, output_c}),
        .output_height({16'd0, output_h}), .output_width({16'd0, output_w}),
        .kernel_height({24'd0, S2A_KERNEL_H[layer_cursor]}),
        .kernel_width({24'd0, S2A_KERNEL_W[layer_cursor]}),
        .stride_y({24'd0, S2A_STRIDE_H[layer_cursor]}),
        .stride_x({24'd0, S2A_STRIDE_W[layer_cursor]}),
        .pad_left({24'd0, S2A_PADDING_LEFT[layer_cursor]}),
        .pad_right({24'd0, S2A_PADDING_RIGHT[layer_cursor]}),
        .pad_top({24'd0, S2A_PADDING_TOP[layer_cursor]}),
        .pad_bottom({24'd0, S2A_PADDING_BOTTOM[layer_cursor]}),
        .groups({16'd0, S2A_GROUP_COUNT[layer_cursor]}),
        .padding_value_int8($signed({{24{S2A_PADDING_VALUE_INT8[layer_cursor][7]}},
                                     S2A_PADDING_VALUE_INT8[layer_cursor]})),
        .weight_package_base_address(weight_package_base_address),
        .weight_package_length_bytes(weight_package_length_bytes),
        .quantized_weight_offset(S2A_GF8_WEIGHT_OFFSET[layer_cursor]),
        .quantized_weight_bytes(S2A_GF8_WEIGHT_BYTES[layer_cursor]),
        .output_batch(decoded_batch), .output_channel(decoded_channel),
        .output_y(decoded_y), .output_x(decoded_x),
        .bias_int32($signed(S2A_CONV_BIAS_ACCUMULATOR_INT32[mq_index])),
        .activation_mode(map_conv_activation(S2A_ACTIVATION[layer_cursor])),
        .positive_multiplier(S2A_T23_MQ_ROM[mq_index][79:48]),
        .positive_q_shift({24'd0, S2A_T23_MQ_ROM[mq_index][47:40]}),
        .negative_multiplier(S2A_T23_MQ_ROM[mq_index][39:8]),
        .negative_q_shift({24'd0, S2A_T23_MQ_ROM[mq_index][7:0]}),
        .backend_cancel(conv_cancel), .backend_req_valid(conv_req_valid),
        .backend_req_ready(conv_req_ready), .backend_req_write(conv_req_write),
        .backend_req_addr(conv_req_addr), .backend_req_wdata(conv_req_wdata),
        .backend_req_rstrb(conv_req_rstrb), .backend_req_wstrb(conv_req_wstrb),
        .backend_rsp_valid(conv_rsp_valid), .backend_rsp_rdata(conv_rsp_data),
        .backend_rsp_error(conv_rsp_error), .busy(),
        .result_valid(conv_result_valid), .result_ready(conv_result_ready),
        .result_output_address(conv_result_address), .result_value(conv_result_value),
        .result_error_code(conv_result_error)
    );

    s2a_maxpool_engine u_maxpool_engine (
        .clk(clk), .hard_reset(hard_reset), .abort(abort),
        .start_valid(maxpool_start_valid), .start_ready(maxpool_start_ready),
        .layer_index({26'd0, S2A_LAYER_INDEX[layer_cursor]}),
        .input_base_address(source_base[0]), .input_length_bytes(source_length[0]),
        .input_channels({16'd0, source_c[0]}), .input_height({16'd0, source_h[0]}),
        .input_width({16'd0, source_w[0]}), .output_base_address(output_base),
        .output_length_bytes(output_length), .output_channels({16'd0, output_c}),
        .output_height({16'd0, output_h}), .output_width({16'd0, output_w}),
        .kernel_height({24'd0, S2A_KERNEL_H[layer_cursor]}),
        .kernel_width({24'd0, S2A_KERNEL_W[layer_cursor]}),
        .stride_y({24'd0, S2A_STRIDE_H[layer_cursor]}),
        .stride_x({24'd0, S2A_STRIDE_W[layer_cursor]}),
        .darknet_padding_parameter({24'd0, S2A_MAXPOOL_DARKNET_PADDING[layer_cursor]}),
        .output_channel(decoded_channel), .output_y(decoded_y), .output_x(decoded_x),
        .backend_cancel(maxpool_cancel), .backend_req_valid(maxpool_req_valid),
        .backend_req_ready(maxpool_req_ready), .backend_req_write(maxpool_req_write),
        .backend_req_addr(maxpool_req_addr), .backend_req_wdata(maxpool_req_wdata),
        .backend_req_rstrb(maxpool_req_rstrb), .backend_req_wstrb(maxpool_req_wstrb),
        .backend_rsp_valid(maxpool_rsp_valid), .backend_rsp_rdata(maxpool_rsp_data),
        .backend_rsp_error(maxpool_rsp_error), .result_valid(maxpool_result_valid),
        .result_ready(maxpool_result_ready), .result_tap_addresses(maxpool_tap_addresses),
        .result_output_address(maxpool_result_address), .result_value(maxpool_result_value),
        .result_error_code(maxpool_result_error)
    );

    s2a_route_engine u_route_engine (
        .clk(clk), .hard_reset(hard_reset), .abort(abort),
        .start_valid(route_start_valid), .start_ready(route_start_ready),
        .source_count({30'd0, current_input_count}),
        .groups({16'd0, S2A_GROUP_COUNT[layer_cursor]}),
        .group_id({16'd0, S2A_ROUTE_GROUP_ID[layer_cursor]}),
        .output_channel(decoded_channel), .output_y(decoded_y), .output_x(decoded_x),
        .source0_base_address(source_base[0]), .source0_length_bytes(source_length[0]),
        .source0_channels({16'd0, source_c[0]}), .source0_height({16'd0, source_h[0]}),
        .source0_width({16'd0, source_w[0]}),
        .source0_channel_start({16'd0, source_route_start[0]}),
        .source0_channel_end({16'd0, source_route_end[0]}),
        .source0_multiplier_q31(S2A_ROUTE_SOURCE_MULTIPLIER_Q31[layer_cursor][0]),
        .source1_base_address(source_base[1]), .source1_length_bytes(source_length[1]),
        .source1_channels({16'd0, source_c[1]}), .source1_height({16'd0, source_h[1]}),
        .source1_width({16'd0, source_w[1]}),
        .source1_channel_start({16'd0, source_route_start[1]}),
        .source1_channel_end({16'd0, source_route_end[1]}),
        .source1_multiplier_q31(S2A_ROUTE_SOURCE_MULTIPLIER_Q31[layer_cursor][1]),
        .output_base_address(output_base), .output_length_bytes(output_length),
        .output_channels({16'd0, output_c}), .output_height({16'd0, output_h}),
        .output_width({16'd0, output_w}),
        .backend_cancel(route_cancel), .backend_req_valid(route_req_valid),
        .backend_req_ready(route_req_ready), .backend_req_write(route_req_write),
        .backend_req_addr(route_req_addr), .backend_req_wdata(route_req_wdata),
        .backend_req_rstrb(route_req_rstrb), .backend_req_wstrb(route_req_wstrb),
        .backend_rsp_valid(route_rsp_valid), .backend_rsp_rdata(route_rsp_data),
        .backend_rsp_error(route_rsp_error), .result_valid(route_result_valid),
        .result_ready(route_result_ready), .result_source_index(route_result_source_index),
        .result_source_address(route_result_source_address),
        .result_output_address(route_result_address), .result_value(route_result_value),
        .result_error_code(route_result_error)
    );

    s2a_upsample_engine u_upsample_engine (
        .clk(clk), .hard_reset(hard_reset), .abort(abort),
        .start_valid(upsample_start_valid), .start_ready(upsample_start_ready),
        .input_base_address(source_base[0]), .input_length_bytes(source_length[0]),
        .output_base_address(output_base), .output_length_bytes(output_length),
        .input_channels({16'd0, source_c[0]}), .input_height({16'd0, source_h[0]}),
        .input_width({16'd0, source_w[0]}),
        .stride({16'd0, S2A_UPSAMPLE_STRIDE[layer_cursor]}),
        .output_channel(decoded_channel), .output_y(decoded_y), .output_x(decoded_x),
        .backend_cancel(upsample_cancel), .backend_req_valid(upsample_req_valid),
        .backend_req_ready(upsample_req_ready), .backend_req_write(upsample_req_write),
        .backend_req_addr(upsample_req_addr), .backend_req_wdata(upsample_req_wdata),
        .backend_req_rstrb(upsample_req_rstrb), .backend_req_wstrb(upsample_req_wstrb),
        .backend_rsp_valid(upsample_rsp_valid), .backend_rsp_rdata(upsample_rsp_data),
        .backend_rsp_error(upsample_rsp_error), .result_valid(upsample_result_valid),
        .result_ready(upsample_result_ready),
        .result_source_address(upsample_result_source_address),
        .result_output_address(upsample_result_address), .result_value(upsample_result_value),
        .result_error_code(upsample_result_error)
    );

    always_ff @(posedge clk) begin
        if (hard_reset) begin
            state <= ST_IDLE;
            layer_cursor <= 6'd0;
            output_element_index <= 32'd0;
            response_pending <= 1'b0;
            response_data_latched <= 32'd0;
            response_error_latched <= NONE;
            response_target_latched <= S2A_OP_CONV;
        end else if (abort) begin
            state <= ST_IDLE;
            layer_cursor <= 6'd0;
            output_element_index <= 32'd0;
            response_pending <= 1'b0;
            response_data_latched <= 32'd0;
            response_error_latched <= NONE;
            response_target_latched <= S2A_OP_CONV;
        end else begin
            if (response_pending) response_pending <= 1'b0;
            if (memory_handshake) begin
                response_pending <= 1'b1;
                response_data_latched <= mem_rdata;
                response_error_latched <= mem_error_code;
                response_target_latched <= current_op;
            end

            case (state)
                ST_IDLE: begin
                    if (backend_start && buffer_owner_pl) begin
                        layer_cursor <= 6'd0;
                        output_element_index <= 32'd0;
                        state <= ST_DISPATCH;
                    end
                end
                ST_DISPATCH: begin
                    if (buffer_owner_pl) begin
                        if ((layer_cursor >= S2A_LAYER_COUNT) || descriptor_fault) begin
                            state <= ST_IDLE;
                        end else if (is_alias_row) begin
                            if (!alias_valid) begin
                                state <= ST_IDLE;
                            end else if ((layer_cursor + 6'd1) >= S2A_LAYER_COUNT) begin
                                state <= ST_IDLE;
                            end else begin
                                layer_cursor <= layer_cursor + 6'd1;
                                output_element_index <= 32'd0;
                            end
                        end else if (!selected_start_ready) begin
                            state <= ST_IDLE;
                        end else begin
                            case (current_op)
                                S2A_OP_CONV: state <= ST_WAIT_CONV;
                                S2A_OP_MAXPOOL: state <= ST_WAIT_MAXPOOL;
                                S2A_OP_ROUTE: state <= ST_WAIT_ROUTE;
                                S2A_OP_UPSAMPLE: state <= ST_WAIT_UPSAMPLE;
                                default: begin
                                    state <= ST_IDLE;
                                end
                            endcase
                        end
                    end
                end
                ST_WAIT_CONV, ST_WAIT_MAXPOOL, ST_WAIT_ROUTE, ST_WAIT_UPSAMPLE: begin
                    if (selected_result_valid) begin
                        if (normalize_engine_error(selected_result_error) != NONE) begin
                            state <= ST_IDLE;
                        end else if (({32'd0, output_element_index} + 64'd1) <
                                     output_element_count) begin
                            output_element_index <= output_element_index + 32'd1;
                            state <= ST_DISPATCH;
                        end else if ((layer_cursor + 6'd1) >= S2A_LAYER_COUNT) begin
                            state <= ST_IDLE;
                        end else begin
                            layer_cursor <= layer_cursor + 6'd1;
                            output_element_index <= 32'd0;
                            state <= ST_DISPATCH;
                        end
                    end
                end
                default: begin
                    state <= ST_IDLE;
                end
            endcase
        end
    end
endmodule
