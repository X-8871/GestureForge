// S2A-T66候选黑盒回归：完整比较 sample0 layer0 的 1,384,448 个输出字节。
`timescale 1ns/1ps
module tb_s2a_t66_candidate_blackbox;
    import s2a_network_descriptor_pkg::*;

    localparam integer INPUT_BYTES = 519168;
    localparam integer WEIGHT_BYTES = 864;
    localparam integer OUTPUT_BYTES = 1384448;
    localparam integer CYCLE_LIMIT = 75000000;
    localparam integer FEATURE_CLASS = 0;
    localparam integer WEIGHT_CLASS = 1;
    localparam integer OUTPUT_CLASS = 2;
    localparam integer TRANSFER_CLASS_COUNT = 3;
    localparam logic [31:0] INPUT_BASE = 32'h00000000;
    localparam logic [31:0] WEIGHT_BASE = 32'h00100000;
    localparam logic [31:0] OUTPUT_BASE = 32'h01000000;
    localparam logic [2:0] NONE = 3'd0;
    localparam logic [2:0] BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] BAD_RANGE = 3'd2;

    logic clk = 1'b0;
    logic hard_reset = 1'b0;
    logic abort = 1'b0;
    logic buffer_owner_pl = 1'b0;
    logic start_valid = 1'b0;
    logic start_ready;
    logic backend_cancel;
    logic backend_req_valid;
    logic backend_req_ready;
    logic backend_req_write;
    logic [31:0] backend_req_addr;
    logic [31:0] backend_req_wdata;
    logic [3:0] backend_req_rstrb;
    logic [3:0] backend_req_wstrb;
    logic backend_rsp_valid;
    logic [31:0] backend_rsp_rdata;
    logic [2:0] backend_rsp_error;
    logic busy;
    logic result_valid;
    logic result_ready = 1'b0;
    logic [2:0] result_error_code;

    logic [7:0] input_bytes [0:INPUT_BYTES-1];
    logic [7:0] weight_bytes [0:WEIGHT_BYTES-1];
    logic [7:0] expected_bytes [0:OUTPUT_BYTES-1];
    logic output_seen [0:OUTPUT_BYTES-1];
    logic weight_seen [0:WEIGHT_BYTES-1];
    logic first_tile_point0_golden_seen = 1'b0;
    logic first_tile_point1_golden_seen = 1'b0;

    logic memory_pending = 1'b0;
    logic [31:0] response_data = 32'd0;
    logic [2:0] response_error = NONE;
    integer response_delay_remaining = 0;
    integer request_count = 0;
    integer response_count = 0;
    integer class_request_count [0:TRANSFER_CLASS_COUNT-1];
    integer class_response_count [0:TRANSFER_CLASS_COUNT-1];
    integer class_request_stall_count [0:TRANSFER_CLASS_COUNT-1];
    integer class_response_stall_count [0:TRANSFER_CLASS_COUNT-1];
    integer output_write_count = 0;
    integer input_read_count = 0;
    integer weight_read_count = 0;
    integer stall_cycle_count = 0;
    integer response_stall_cycle_count = 0;
    integer held_request = 0;
    integer stall_remaining = 0;
    logic held_write;
    logic [31:0] held_address;
    logic [31:0] held_wdata;
    logic [3:0] held_rstrb;
    logic [3:0] held_wstrb;
    integer file_id;
    integer file_read_count;
    integer load_index;
    integer lane;
    integer address_index;
    integer cycle_count = 0;
    integer next_cycle_progress = 100000;
    integer result_count = 0;
    integer next_progress = 200000;
    integer missing_count;
    integer weight_byte_index;
    integer request_transfer_class_comb;
    integer pending_transfer_class = -1;
    integer transfer_class_work;
    integer active_request_stall_observed = 0;
    integer active_response_stall_observed = 0;
    integer reset_index;
    integer selected_read_lane_work;
    integer feature_lane_request_count [0:3];
    integer weight_lane_request_count [0:3];
    string fixture_input_path = "";
    string fixture_weight_path = "";
    string fixture_expected_path = "";
    logic [31:0] read_word_work;
    logic [2:0] read_error_work;
    logic [31:0] selected_byte_address_work;
    logic [7:0] observed_byte_work;

    function automatic integer request_stall_cycles(input integer index);
        begin
            case (index % 5)
                0: request_stall_cycles = 0;
                1: request_stall_cycles = 1;
                2: request_stall_cycles = 2;
                3: request_stall_cycles = 7;
                default: request_stall_cycles = 3;
            endcase
        end
    endfunction

    function automatic integer response_stall_cycles(input integer index);
        begin
            case (index % 5)
                0: response_stall_cycles = 0;
                1: response_stall_cycles = 1;
                2: response_stall_cycles = 2;
                3: response_stall_cycles = 7;
                default: response_stall_cycles = 3;
            endcase
        end
    endfunction

    function automatic integer classify_transfer(
        input logic is_write,
        input logic [31:0] word_address
    );
        begin
            if (is_write) begin
                if ((word_address >= OUTPUT_BASE) &&
                    (word_address < OUTPUT_BASE + OUTPUT_BYTES)) begin
                    classify_transfer = OUTPUT_CLASS;
                end else begin
                    classify_transfer = -1;
                end
            end else if (word_address < INPUT_BASE + INPUT_BYTES) begin
                classify_transfer = FEATURE_CLASS;
            end else if ((word_address >= WEIGHT_BASE + S2A_GF8_WEIGHT_OFFSET[0]) &&
                         (word_address < WEIGHT_BASE + S2A_GF8_WEIGHT_OFFSET[0] + WEIGHT_BYTES)) begin
                classify_transfer = WEIGHT_CLASS;
            end else begin
                classify_transfer = -1;
            end
        end
    endfunction

    function automatic integer strobe_lane_index(input logic [3:0] strobe);
        begin
            case (strobe)
                4'b0001: strobe_lane_index = 0;
                4'b0010: strobe_lane_index = 1;
                4'b0100: strobe_lane_index = 2;
                4'b1000: strobe_lane_index = 3;
                default: strobe_lane_index = -1;
            endcase
        end
    endfunction

    function automatic integer expected_stall_total(input integer transfer_count);
        integer remainder;
        integer partial_stalls;
        begin
            remainder = transfer_count % 5;
            partial_stalls = 0;
            expected_stall_total = (transfer_count / 5) * 13;
            case (remainder)
                2: partial_stalls = 1;
                3: partial_stalls = 3;
                4: partial_stalls = 10;
                default: partial_stalls = 0;
            endcase
            expected_stall_total = expected_stall_total + partial_stalls;
        end
    endfunction

    always #5 clk = ~clk;

    always_comb begin
        request_transfer_class_comb = classify_transfer(backend_req_write, backend_req_addr);
        if (hard_reset || abort || memory_pending) begin
            backend_req_ready = 1'b0;
        end else if (held_request != 0) begin
            backend_req_ready = (stall_remaining == 0);
        end else if (!backend_req_valid) begin
            backend_req_ready = 1'b0;
        end else if (request_transfer_class_comb < 0) begin
            backend_req_ready = 1'b1;
        end else begin
            backend_req_ready =
                (request_stall_cycles(class_request_count[request_transfer_class_comb]) == 0);
        end
        backend_rsp_valid = memory_pending && (response_delay_remaining == 0);
        backend_rsp_rdata = response_data;
        backend_rsp_error = response_error;
    end

    // DUT 只连接公开端口；本测试不读取、驱动或强制任何层级内部信号。
    s2a_conv_tile_engine u_dut (
        .clk(clk), .hard_reset(hard_reset), .abort(abort), .buffer_owner_pl(buffer_owner_pl),
        .start_valid(start_valid), .start_ready(start_ready),
        .layer_index(32'd0), .weight_layer_index(32'd0),
        .input_base_address(INPUT_BASE), .input_length_bytes(INPUT_BYTES),
        .input_batch_count(32'd1), .input_channels(32'd3),
        .input_height(32'd416), .input_width(32'd416),
        .output_base_address(OUTPUT_BASE), .output_length_bytes(OUTPUT_BYTES),
        .output_batch_count(32'd1), .output_channels(32'd32),
        .output_height(32'd208), .output_width(32'd208),
        .kernel_height(32'd3), .kernel_width(32'd3),
        .stride_y(32'd2), .stride_x(32'd2),
        .pad_left(32'd1), .pad_right(32'd1), .pad_top(32'd1), .pad_bottom(32'd1),
        .groups(32'd1), .padding_value_int8(32'sd0),
        .weight_package_base_address(WEIGHT_BASE), .weight_package_length_bytes(32'd5903100),
        .quantized_weight_offset(S2A_GF8_WEIGHT_OFFSET[0]),
        .quantized_weight_bytes(S2A_GF8_WEIGHT_BYTES[0]),
        .output_batch(32'd0), .activation_mode(2'd1),
        .backend_cancel(backend_cancel), .backend_req_valid(backend_req_valid),
        .backend_req_ready(backend_req_ready), .backend_req_write(backend_req_write),
        .backend_req_addr(backend_req_addr), .backend_req_wdata(backend_req_wdata),
        .backend_req_rstrb(backend_req_rstrb), .backend_req_wstrb(backend_req_wstrb),
        .backend_rsp_valid(backend_rsp_valid), .backend_rsp_rdata(backend_rsp_rdata),
        .backend_rsp_error(backend_rsp_error), .busy(busy),
        .result_valid(result_valid), .result_ready(result_ready),
        .result_error_code(result_error_code)
    );

    // 该模型只映射指定的输入、权重和输出对象，并按小端字节 lane 解释请求。
    always_ff @(posedge clk) begin
        transfer_class_work = classify_transfer(backend_req_write, backend_req_addr);
        if (hard_reset || abort) begin
            memory_pending <= 1'b0;
            response_data <= 32'd0;
            response_error <= NONE;
            response_delay_remaining <= 0;
            request_count <= 0;
            response_count <= 0;
            for (reset_index = 0; reset_index < TRANSFER_CLASS_COUNT; reset_index = reset_index + 1) begin
                class_request_count[reset_index] <= 0;
                class_response_count[reset_index] <= 0;
                class_request_stall_count[reset_index] <= 0;
                class_response_stall_count[reset_index] <= 0;
            end
            for (reset_index = 0; reset_index < 4; reset_index = reset_index + 1) begin
                feature_lane_request_count[reset_index] <= 0;
                weight_lane_request_count[reset_index] <= 0;
            end
            for (reset_index = 0; reset_index < WEIGHT_BYTES; reset_index = reset_index + 1)
                weight_seen[reset_index] <= 1'b0;
            pending_transfer_class <= -1;
            active_request_stall_observed <= 0;
            active_response_stall_observed <= 0;
            output_write_count <= 0;
            first_tile_point0_golden_seen <= 1'b0;
            first_tile_point1_golden_seen <= 1'b0;
            input_read_count <= 0;
            weight_read_count <= 0;
            stall_cycle_count <= 0;
            response_stall_cycle_count <= 0;
            held_request <= 0;
            stall_remaining <= 0;
            cycle_count <= 0;
            next_cycle_progress <= 100000;
            result_count <= 0;
            next_progress <= 200000;
        end else begin
            cycle_count <= cycle_count + 1;
            if (cycle_count + 1 >= next_cycle_progress) begin
                $display("T66_CYCLE_PROGRESS cycles=%0d requests=%0d writes=%0d", cycle_count + 1,
                         request_count, output_write_count);
                next_cycle_progress <= next_cycle_progress + 100000;
            end
            if (held_request != 0) begin
                if (!backend_req_valid ||
                    (backend_req_write !== held_write) ||
                    (backend_req_addr !== held_address) ||
                    (backend_req_wdata !== held_wdata) ||
                    (backend_req_rstrb !== held_rstrb) ||
                    (backend_req_wstrb !== held_wstrb)) begin
                    $fatal(1, "T66 backpressure 期间 request 字段变化：cycle=%0d", cycle_count);
                end
            end

            if (backend_req_valid && !backend_req_ready) begin
                if (transfer_class_work < 0)
                    $fatal(1, "T66 backpressure 请求不属于已映射对象：addr=%08h write=%b",
                           backend_req_addr, backend_req_write);
                stall_cycle_count <= stall_cycle_count + 1;
                class_request_stall_count[transfer_class_work] <=
                    class_request_stall_count[transfer_class_work] + 1;
                active_request_stall_observed <= active_request_stall_observed + 1;
                if (held_request == 0) begin
                    held_request <= 1;
                    held_write <= backend_req_write;
                    held_address <= backend_req_addr;
                    held_wdata <= backend_req_wdata;
                    held_rstrb <= backend_req_rstrb;
                    held_wstrb <= backend_req_wstrb;
                    stall_remaining <=
                        request_stall_cycles(class_request_count[transfer_class_work]) - 1;
                end else if (stall_remaining > 0) begin
                    stall_remaining <= stall_remaining - 1;
                end
            end

            if (backend_req_valid && backend_req_ready) begin
                if (transfer_class_work < 0)
                    $fatal(1, "T66 请求不属于已映射对象：addr=%08h write=%b",
                           backend_req_addr, backend_req_write);
                if (memory_pending) begin
                    $fatal(1, "T66 memory model 发现第二个 outstanding 请求");
                end
                if ((backend_req_addr[1:0] != 2'b00) ||
                    (backend_req_rstrb == 4'b0000 && backend_req_wstrb == 4'b0000)) begin
                    $fatal(1, "T66 请求未对齐或 byte strobe 为空：addr=%08h rstrb=%b wstrb=%b",
                           backend_req_addr, backend_req_rstrb, backend_req_wstrb);
                end
                if (held_request != 0 &&
                    ((backend_req_write !== held_write) ||
                     (backend_req_addr !== held_address) ||
                     (backend_req_wdata !== held_wdata) ||
                     (backend_req_rstrb !== held_rstrb) ||
                     (backend_req_wstrb !== held_wstrb))) begin
                    $fatal(1, "T66 接受时 request 字段与 stalled request 不一致");
                end
                held_request <= 0;
                stall_remaining <= 0;
                if (active_request_stall_observed !=
                    request_stall_cycles(class_request_count[transfer_class_work])) begin
                    $fatal(1, "T66 request stall 序列错误：class=%0d index=%0d expected=%0d actual=%0d",
                           transfer_class_work, class_request_count[transfer_class_work],
                           request_stall_cycles(class_request_count[transfer_class_work]),
                           active_request_stall_observed);
                end
                active_request_stall_observed <= 0;
                request_count <= request_count + 1;
                class_request_count[transfer_class_work] <=
                    class_request_count[transfer_class_work] + 1;
                memory_pending <= 1'b1;
                pending_transfer_class <= transfer_class_work;
                response_delay_remaining <=
                    response_stall_cycles(class_response_count[transfer_class_work]);
                response_data <= 32'd0;
                response_error <= NONE;

                if (backend_req_write) begin
                    if ((backend_req_rstrb != 4'b0000) ||
                        (backend_req_wstrb == 4'b0000) ||
                        ($countones(backend_req_wstrb) != 1)) begin
                        $fatal(1, "T66 写请求方向或 strobe 错误：r=%b w=%b",
                               backend_req_rstrb, backend_req_wstrb);
                    end
                    for (lane = 0; lane < 4; lane = lane + 1) begin
                        if (backend_req_wstrb[lane]) begin
                            selected_byte_address_work = backend_req_addr + lane;
                            if ((selected_byte_address_work < OUTPUT_BASE) ||
                                (selected_byte_address_work >= OUTPUT_BASE + OUTPUT_BYTES)) begin
                                $fatal(1, "T66 写请求越界：address=%08h", selected_byte_address_work);
                            end
                            address_index = selected_byte_address_work - OUTPUT_BASE;
                            if (output_seen[address_index]) begin
                                $fatal(1, "T66 重复写输出字节：index=%0d address=%08h",
                                       address_index, selected_byte_address_work);
                            end
                            observed_byte_work = backend_req_wdata[(lane * 8) +: 8];
                            if (observed_byte_work !== expected_bytes[address_index]) begin
                                $fatal(1, "T66 输出 mismatch：index=%0d NCHW-channel-plane-byte=%0d address=%08h actual=%02h expected=%02h",
                                       address_index, address_index, selected_byte_address_work,
                                       observed_byte_work, expected_bytes[address_index]);
                            end
                            if (selected_byte_address_work == OUTPUT_BASE)
                                first_tile_point0_golden_seen <= 1'b1;
                            if (selected_byte_address_work == (OUTPUT_BASE + 32'd1))
                                first_tile_point1_golden_seen <= 1'b1;
                            output_seen[address_index] <= 1'b1;
                            output_write_count <= output_write_count + 1;
                            if (output_write_count + 1 >= next_progress) begin
                                $display("T66_PROGRESS writes=%0d/%0d cycles=%0d requests=%0d",
                                         output_write_count + 1, OUTPUT_BYTES, cycle_count, request_count + 1);
                                next_progress <= next_progress + 200000;
                            end
                        end
                    end
                end else begin
                    if ((backend_req_wstrb != 4'b0000) ||
                        (backend_req_rstrb == 4'b0000) ||
                        ($countones(backend_req_rstrb) != 1)) begin
                        $fatal(1, "T66 读请求方向或 strobe 错误：r=%b w=%b",
                               backend_req_rstrb, backend_req_wstrb);
                    end
                    selected_read_lane_work = strobe_lane_index(backend_req_rstrb);
                    if (selected_read_lane_work < 0) begin
                        $fatal(1, "T66 读请求 strobe 不是 one-hot：class=%0d strobe=%b",
                               transfer_class_work, backend_req_rstrb);
                    end
                    if (transfer_class_work == FEATURE_CLASS)
                        feature_lane_request_count[selected_read_lane_work] <=
                            feature_lane_request_count[selected_read_lane_work] + 1;
                    else if (transfer_class_work == WEIGHT_CLASS)
                        weight_lane_request_count[selected_read_lane_work] <=
                            weight_lane_request_count[selected_read_lane_work] + 1;
                    read_word_work = 32'd0;
                    read_error_work = NONE;
                    for (lane = 0; lane < 4; lane = lane + 1) begin
                        if (backend_req_rstrb[lane]) begin
                            selected_byte_address_work = backend_req_addr + lane;
                            if (selected_byte_address_work < INPUT_BASE + INPUT_BYTES) begin
                                read_word_work[(lane * 8) +: 8] =
                                    input_bytes[selected_byte_address_work - INPUT_BASE];
                                input_read_count <= input_read_count + 1;
                            end else if ((selected_byte_address_work >=
                                          WEIGHT_BASE + S2A_GF8_WEIGHT_OFFSET[0]) &&
                                         (selected_byte_address_work <
                                          WEIGHT_BASE + S2A_GF8_WEIGHT_OFFSET[0] + WEIGHT_BYTES)) begin
                                weight_byte_index = selected_byte_address_work -
                                    WEIGHT_BASE - S2A_GF8_WEIGHT_OFFSET[0];
                                weight_seen[weight_byte_index] <= 1'b1;
                                read_word_work[(lane * 8) +: 8] = weight_bytes[weight_byte_index];
                                weight_read_count <= weight_read_count + 1;
                            end else begin
                                read_error_work = BAD_RANGE;
                                $fatal(1, "T66 读请求越界：address=%08h", selected_byte_address_work);
                            end
                        end
                    end
                    response_data <= read_word_work;
                    response_error <= read_error_work;
                end
            end else if (held_request != 0 && !backend_req_ready && stall_remaining > 0) begin
                stall_remaining <= stall_remaining - 1;
            end

            if (memory_pending && backend_rsp_valid) begin
                if (pending_transfer_class < 0)
                    $fatal(1, "T66 响应缺少有效的 transfer class");
                if (active_response_stall_observed !=
                    response_stall_cycles(class_response_count[pending_transfer_class])) begin
                    $fatal(1, "T66 response stall 序列错误：class=%0d index=%0d expected=%0d actual=%0d",
                           pending_transfer_class, class_response_count[pending_transfer_class],
                           response_stall_cycles(class_response_count[pending_transfer_class]),
                           active_response_stall_observed);
                end
                memory_pending <= 1'b0;
                response_count <= response_count + 1;
                class_response_count[pending_transfer_class] <=
                    class_response_count[pending_transfer_class] + 1;
                pending_transfer_class <= -1;
                active_response_stall_observed <= 0;
            end else if (memory_pending && response_delay_remaining > 0) begin
                response_delay_remaining <= response_delay_remaining - 1;
                response_stall_cycle_count <= response_stall_cycle_count + 1;
                class_response_stall_count[pending_transfer_class] <=
                    class_response_stall_count[pending_transfer_class] + 1;
                active_response_stall_observed <= active_response_stall_observed + 1;
            end

            if (result_valid && result_ready) begin
                result_count <= result_count + 1;
            end
        end
    end

    initial begin
        if (!$value$plusargs("T66_INPUT_PATH=%s", fixture_input_path) ||
            !$value$plusargs("T66_WEIGHT_PATH=%s", fixture_weight_path) ||
            !$value$plusargs("T66_GOLDEN_PATH=%s", fixture_expected_path)) begin
            $fatal(1, "T66 必须通过 plusargs 指定输入、权重和全层黄金文件路径");
        end
        for (load_index = 0; load_index < INPUT_BYTES; load_index = load_index + 1) begin
            input_bytes[load_index] = 8'hxx;
        end
        for (load_index = 0; load_index < WEIGHT_BYTES; load_index = load_index + 1) begin
            weight_bytes[load_index] = 8'hxx;
        end
        for (load_index = 0; load_index < OUTPUT_BYTES; load_index = load_index + 1) begin
            expected_bytes[load_index] = 8'hxx;
            output_seen[load_index] = 1'b0;
        end

        file_id = $fopen(fixture_input_path, "rb");
        if (file_id == 0) $fatal(1, "无法打开 sample0 输入夹具：%s", fixture_input_path);
        file_read_count = $fread(input_bytes, file_id);
        $fclose(file_id);
        if (file_read_count != INPUT_BYTES)
            $fatal(1, "sample0 输入夹具长度错误：expected=%0d actual=%0d", INPUT_BYTES, file_read_count);

        file_id = $fopen(fixture_weight_path, "rb");
        if (file_id == 0) $fatal(1, "无法打开 layer0 权重夹具：%s", fixture_weight_path);
        file_read_count = $fread(weight_bytes, file_id);
        $fclose(file_id);
        if (file_read_count != WEIGHT_BYTES)
            $fatal(1, "layer0 权重夹具长度错误：expected=%0d actual=%0d", WEIGHT_BYTES, file_read_count);

        file_id = $fopen(fixture_expected_path, "rb");
        if (file_id == 0) $fatal(1, "无法打开 T25 layer0 黄金夹具：%s", fixture_expected_path);
        file_read_count = $fread(expected_bytes, file_id);
        $fclose(file_id);
        if (file_read_count != OUTPUT_BYTES)
            $fatal(1, "T25 layer0 黄金夹具长度错误：expected=%0d actual=%0d", OUTPUT_BYTES, file_read_count);
        for (load_index = 0; load_index < INPUT_BYTES; load_index = load_index + 1) begin
            if ((^input_bytes[load_index]) === 1'bx)
                $fatal(1, "sample0 输入夹具有未加载字节：index=%0d", load_index);
        end
        for (load_index = 0; load_index < WEIGHT_BYTES; load_index = load_index + 1) begin
            if ((^weight_bytes[load_index]) === 1'bx)
                $fatal(1, "layer0 权重夹具有未加载字节：index=%0d", load_index);
        end
        for (load_index = 0; load_index < OUTPUT_BYTES; load_index = load_index + 1) begin
            if ((^expected_bytes[load_index]) === 1'bx)
                $fatal(1, "T25 黄金夹具有未加载字节：index=%0d", load_index);
        end
        $display("T66_FIXTURES input=%0d weight=%0d expected=%0d shape=[1,32,208,208] layout=NCHW",
                 INPUT_BYTES, WEIGHT_BYTES, OUTPUT_BYTES);
        $display("T66_MEMORY byte-strobes=one-hot aligned=32-bit outstanding=1 stall-pattern=[0,1,2,7,3]");
        $display("T66_PLAN cycle_limit=%0d lanes=8 waveforms=disabled mq_bias=normal_descriptor_prefetch",
                 CYCLE_LIMIT);

        @(negedge clk);
        hard_reset = 1'b1;
        repeat (2) @(posedge clk);
        #1;
        @(negedge clk);
        hard_reset = 1'b0;
        buffer_owner_pl = 1'b1;
        #1;
        if (start_ready !== 1'b1)
            $fatal(1, "T66 layer start 未 ready：start_ready=%b", start_ready);
        start_valid = 1'b1;
        @(posedge clk);
        if ((start_valid !== 1'b1) || (start_ready !== 1'b1))
            $fatal(1, "T66 layer start 握手未发生：start_valid=%b start_ready=%b", start_valid, start_ready);
        #1;
        @(negedge clk);
        start_valid = 1'b0;

        for (load_index = 0; load_index < CYCLE_LIMIT; load_index = load_index + 1) begin
            @(posedge clk);
            #1;
            if (result_valid) begin
                if (result_error_code != NONE)
                    $fatal(1, "T66 layer engine 返回错误：code=%0d cycles=%0d", result_error_code, cycle_count);
                break;
            end
        end
        if (!result_valid)
            $fatal(1, "T66 全层仿真 watchdog 超时：limit=%0d cycles=%0d writes=%0d requests=%0d",
                   CYCLE_LIMIT, cycle_count, output_write_count, request_count);
        @(negedge clk);
        result_ready = 1'b1;
        @(posedge clk);
        #1;
        if (memory_pending || held_request != 0)
            $fatal(1, "T66 result 时仍有未完成 memory request/response");
        if ((output_write_count != OUTPUT_BYTES) || (result_count != 1) || busy || result_valid ||
            (request_count != response_count))
            $fatal(1, "T66 传输计数不完整：writes=%0d result=%0d req=%0d rsp=%0d",
                   output_write_count, result_count, request_count, response_count);
        missing_count = 0;
        for (load_index = 0; load_index < OUTPUT_BYTES; load_index = load_index + 1) begin
            if (!output_seen[load_index]) begin
                missing_count = missing_count + 1;
                if (missing_count <= 8)
                    $display("T66_MISSING_OUTPUT index=%0d expected=%02h", load_index, expected_bytes[load_index]);
            end
        end
        if (missing_count != 0)
            $fatal(1, "T66 有未写输出字节：count=%0d", missing_count);
        if (!first_tile_point0_golden_seen || !first_tile_point1_golden_seen)
            $fatal(1, "T66 首个 tile 前两个空间点未完成全层 golden 比对：golden0=%b golden1=%b",
                   first_tile_point0_golden_seen, first_tile_point1_golden_seen);
        if ((input_read_count == 0) || (weight_read_count == 0) ||
            (stall_cycle_count == 0) || (response_stall_cycle_count == 0))
            $fatal(1, "T66 memory/stall 覆盖不足：input=%0d weight=%0d request_stalls=%0d response_stalls=%0d",
                   input_read_count, weight_read_count, stall_cycle_count, response_stall_cycle_count);
        if ((class_request_count[FEATURE_CLASS] != input_read_count) ||
            (class_request_count[WEIGHT_CLASS] != weight_read_count) ||
            (class_request_count[OUTPUT_CLASS] != output_write_count) ||
            (class_response_count[FEATURE_CLASS] != class_request_count[FEATURE_CLASS]) ||
            (class_response_count[WEIGHT_CLASS] != class_request_count[WEIGHT_CLASS]) ||
            (class_response_count[OUTPUT_CLASS] != class_request_count[OUTPUT_CLASS]))
            $fatal(1, "T66 transfer class 计数不一致：feature=%0d/%0d weight=%0d/%0d output=%0d/%0d",
                   class_request_count[FEATURE_CLASS], input_read_count,
                   class_request_count[WEIGHT_CLASS], weight_read_count,
                   class_request_count[OUTPUT_CLASS], output_write_count);
        for (load_index = 0; load_index < WEIGHT_BYTES; load_index = load_index + 1) begin
            if (!weight_seen[load_index])
                $fatal(1, "T66 layer0 权重地址未覆盖：index=%0d", load_index);
        end
        for (load_index = 0; load_index < 4; load_index = load_index + 1) begin
            if ((feature_lane_request_count[load_index] == 0) ||
                (weight_lane_request_count[load_index] == 0))
                $fatal(1, "T66 feature/weight read lane 覆盖不完整：lane=%0d feature=%0d weight=%0d",
                       load_index, feature_lane_request_count[load_index],
                       weight_lane_request_count[load_index]);
            $display("T66_READ_LANE_PASS lane=%0d feature_requests=%0d weight_requests=%0d",
                     load_index, feature_lane_request_count[load_index],
                     weight_lane_request_count[load_index]);
        end
        for (load_index = 0; load_index < TRANSFER_CLASS_COUNT; load_index = load_index + 1) begin
            if ((class_request_stall_count[load_index] !=
                 expected_stall_total(class_request_count[load_index])) ||
                (class_response_stall_count[load_index] !=
                 expected_stall_total(class_response_count[load_index])))
                $fatal(1, "T66 transfer class stall 总数不符：class=%0d request=%0d/%0d response=%0d/%0d",
                       load_index, class_request_stall_count[load_index],
                       expected_stall_total(class_request_count[load_index]),
                       class_response_stall_count[load_index],
                       expected_stall_total(class_response_count[load_index]));
            $display("T66_CLASS_STALL class=%0d requests=%0d request_stalls=%0d responses=%0d response_stalls=%0d pattern=[0,1,2,7,3]",
                     load_index, class_request_count[load_index], class_request_stall_count[load_index],
                     class_response_count[load_index], class_response_stall_count[load_index]);
        end
        if ((result_error_code != NONE) || (backend_cancel !== 1'b0))
            $fatal(1, "T66 结束状态错误：error=%0d cancel=%b", result_error_code, backend_cancel);
        $display("PASS: T66 candidate blackbox sample0 layer0 full tensor matched T25; bytes=%0d mismatches=0 input_reads=%0d weight_reads=%0d output_writes=%0d requests=%0d responses=%0d request_stalls=%0d response_stalls=%0d cycles=%0d",
                 OUTPUT_BYTES, input_read_count, weight_read_count, output_write_count,
                 request_count, response_count, stall_cycle_count, response_stall_cycle_count, cycle_count);
        $finish;
    end
endmodule
