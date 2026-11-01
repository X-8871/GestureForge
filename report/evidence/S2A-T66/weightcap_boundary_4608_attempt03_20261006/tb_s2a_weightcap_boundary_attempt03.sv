module tb_s2a_weightcap_boundary;
    timeunit 1ns;
    timeprecision 1ps;
    import s2a_network_descriptor_pkg::*;

    localparam logic [31:0] INPUT_BASE = 32'h00000000;
    localparam logic [31:0] WEIGHT_BASE = 32'h00100000;
    localparam logic [31:0] OUTPUT_BASE = 32'h01000000;
    localparam logic [31:0] MAX_K = 32'd4608;
    localparam logic [63:0] WEIGHT_OBJECT_BASE =
        {32'd0, WEIGHT_BASE} + {32'd0, S2A_GF8_WEIGHT_OFFSET[26]};
    localparam logic [63:0] EXPECTED_FINAL_PACKAGE_BYTE =
        WEIGHT_OBJECT_BASE + {32'd0, S2A_GF8_WEIGHT_BYTES[26]} - 64'd1;

    logic clk = 1'b0;
    logic hard_reset = 1'b1;
    logic abort = 1'b0;
    logic buffer_owner_pl = 1'b1;
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

    logic [31:0] input_length_bytes = 32'd4608;
    logic [31:0] input_channels = 32'd512;
    logic [31:0] input_height = 32'd3;
    logic [31:0] input_width = 32'd3;
    logic [31:0] output_length_bytes = 32'd512;
    logic [31:0] output_channels = 32'd512;
    logic [31:0] output_height = 32'd1;
    logic [31:0] output_width = 32'd1;
    logic [31:0] kernel_height = 32'd3;
    logic [31:0] kernel_width = 32'd3;
    logic [31:0] stride_y = 32'd1;
    logic [31:0] stride_x = 32'd1;
    logic [31:0] weight_package_length_bytes = 32'd5903100;
    logic [31:0] quantized_weight_offset = S2A_GF8_WEIGHT_OFFSET[26];
    logic [31:0] quantized_weight_bytes = S2A_GF8_WEIGHT_BYTES[26];

    logic memory_pending = 1'b0;
    logic [31:0] response_data = 32'h01010101;
    integer request_count = 0;
    integer feature_read_count = 0;
    integer weight_read_count = 0;
    integer output_write_count = 0;
    integer lane7_index4607_request_count = 0;
    integer final_package_byte_request_count = 0;
    integer final_tap_count = 0;
    integer bad_k_request_baseline = 0;
    integer selected_lane;
    logic [63:0] selected_byte_address;
    logic [7:0] final_tap_lane_mask = 8'h00;
    logic group_override_done = 1'b0;
    integer group_override_count = 0;

    function automatic integer strobe_lane(input logic [3:0] strobe);
        begin
            case (strobe)
                4'b0001: strobe_lane = 0;
                4'b0010: strobe_lane = 1;
                4'b0100: strobe_lane = 2;
                4'b1000: strobe_lane = 3;
                default: strobe_lane = -1;
            endcase
        end
    endfunction

    always #5 clk = ~clk;

    always_comb begin
        backend_req_ready = !memory_pending && !hard_reset && !abort;
        backend_rsp_valid = memory_pending;
        backend_rsp_rdata = response_data;
        backend_rsp_error = 3'd0;
    end

    s2a_conv_tile_engine u_dut (
        .clk(clk), .hard_reset(hard_reset), .abort(abort), .buffer_owner_pl(buffer_owner_pl),
        .start_valid(start_valid), .start_ready(start_ready),
        .layer_index(32'd26), .weight_layer_index(32'd26),
        .input_base_address(INPUT_BASE), .input_length_bytes(input_length_bytes),
        .input_batch_count(32'd1), .input_channels(input_channels),
        .input_height(input_height), .input_width(input_width),
        .output_base_address(OUTPUT_BASE), .output_length_bytes(output_length_bytes),
        .output_batch_count(32'd1), .output_channels(output_channels),
        .output_height(output_height), .output_width(output_width),
        .kernel_height(kernel_height), .kernel_width(kernel_width),
        .stride_y(stride_y), .stride_x(stride_x),
        .pad_left(32'd0), .pad_right(32'd0), .pad_top(32'd0), .pad_bottom(32'd0),
        .groups(32'd1), .padding_value_int8(32'sd0),
        .weight_package_base_address(WEIGHT_BASE),
        .weight_package_length_bytes(weight_package_length_bytes),
        .quantized_weight_offset(quantized_weight_offset),
        .quantized_weight_bytes(quantized_weight_bytes),
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

    // 在完整加载冻结 layer26 特征 patch 后、首个 ST_WEIGHT_PREP 上升沿前，
    // 将输出组定位到最后 8 个合法通道，避免遍历前 63 组无关权重。
    always @(negedge clk) begin
        if (!hard_reset && !abort && !group_override_done && (u_dut.state == 5'd6)) begin
            if ((u_dut.output_group_base !== 32'd0) || (feature_read_count != 4608)) begin
                $fatal(1, "输出组注入时机错误: group=%0d feature_reads=%0d",
                       u_dut.output_group_base, feature_read_count);
            end
            u_dut.output_group_base = 32'd504;
            group_override_done = 1'b1;
            group_override_count = group_override_count + 1;
            $display("OUTPUT_GROUP_BASE_DEPOSIT_PASS state=ST_WEIGHT_PREP group=504 feature_reads=%0d",
                     feature_read_count);
        end
    end

    always @(posedge clk) begin
        if (hard_reset || abort) begin
            memory_pending <= 1'b0;
        end else begin
            if (memory_pending) begin
                memory_pending <= 1'b0;
            end
            if (backend_req_valid && backend_req_ready) begin
                request_count <= request_count + 1;
                selected_lane = strobe_lane(backend_req_write ? backend_req_wstrb : backend_req_rstrb);
                if (selected_lane < 0) begin
                    $fatal(1, "非法或非 one-hot memory strobe: write=%0d rstrb=%b wstrb=%b",
                           backend_req_write, backend_req_rstrb, backend_req_wstrb);
                end
                selected_byte_address = {32'd0, backend_req_addr} +
                                        {32'd0, selected_lane[31:0]};
                if (backend_req_write) begin
                    if ((selected_byte_address < {32'd0, OUTPUT_BASE}) ||
                        (selected_byte_address >= {32'd0, OUTPUT_BASE} +
                                                  {32'd0, output_length_bytes}) ||
                        (backend_req_rstrb != 4'b0000)) begin
                        $fatal(1, "输出写地址或 strobe 越界: addr=%08h lane=%0d",
                               backend_req_addr, selected_lane);
                    end
                    output_write_count <= output_write_count + 1;
                end else if (selected_byte_address < {32'd0, INPUT_BASE} +
                                                    {32'd0, input_length_bytes}) begin
                    if (backend_req_wstrb != 4'b0000) begin
                        $fatal(1, "输入读请求同时带写 strobe");
                    end
                    feature_read_count <= feature_read_count + 1;
                end else if ((selected_byte_address >= WEIGHT_OBJECT_BASE) &&
                             (selected_byte_address < WEIGHT_OBJECT_BASE +
                                                      {32'd0, S2A_GF8_WEIGHT_BYTES[26]})) begin
                    if (backend_req_wstrb != 4'b0000) begin
                        $fatal(1, "权重读请求同时带写 strobe");
                    end
                    weight_read_count <= weight_read_count + 1;
                    if (selected_byte_address == EXPECTED_FINAL_PACKAGE_BYTE) begin
                        final_package_byte_request_count <= final_package_byte_request_count + 1;
                    end
                    if ((u_dut.weight_lane_index == 32'd7) &&
                        (u_dut.weight_reduction_index == MAX_K - 1)) begin
                        if (selected_byte_address != EXPECTED_FINAL_PACKAGE_BYTE) begin
                            $fatal(1, "lane7/index4607 未映射至 package 最后字节: observed=%016h expected=%016h",
                                   selected_byte_address, EXPECTED_FINAL_PACKAGE_BYTE);
                        end
                        lane7_index4607_request_count <= lane7_index4607_request_count + 1;
                    end
                end else begin
                    $fatal(1, "memory 请求不属于输入、权重或输出: write=%0d byte_addr=%016h",
                           backend_req_write, selected_byte_address);
                end
                // 测试 responder 对所有读请求合成 0x01010101；地址覆盖由请求地址单独核验。
                response_data <= 32'h01010101;
                memory_pending <= 1'b1;
            end

            if ((u_dut.state == 5'd13) && (u_dut.compute_reduction_index == MAX_K - 1)) begin
                final_tap_count <= final_tap_count + 1;
                if ((u_dut.gen_weight_lane_bank[0].lane_weight_memory[MAX_K-1] !== 8'sd1) ||
                    (u_dut.gen_weight_lane_bank[1].lane_weight_memory[MAX_K-1] !== 8'sd1) ||
                    (u_dut.gen_weight_lane_bank[2].lane_weight_memory[MAX_K-1] !== 8'sd1) ||
                    (u_dut.gen_weight_lane_bank[3].lane_weight_memory[MAX_K-1] !== 8'sd1) ||
                    (u_dut.gen_weight_lane_bank[4].lane_weight_memory[MAX_K-1] !== 8'sd1) ||
                    (u_dut.gen_weight_lane_bank[5].lane_weight_memory[MAX_K-1] !== 8'sd1) ||
                    (u_dut.gen_weight_lane_bank[6].lane_weight_memory[MAX_K-1] !== 8'sd1) ||
                    (u_dut.gen_weight_lane_bank[7].lane_weight_memory[MAX_K-1] !== 8'sd1)) begin
                    $fatal(1, "K=4608 权重末项 index=4607 未成功写入全部 8 个 lane RAM");
                end
                if ((u_dut.compute_weight_byte[0] !== 8'sd1) ||
                    (u_dut.compute_weight_byte[1] !== 8'sd1) ||
                    (u_dut.compute_weight_byte[2] !== 8'sd1) ||
                    (u_dut.compute_weight_byte[3] !== 8'sd1) ||
                    (u_dut.compute_weight_byte[4] !== 8'sd1) ||
                    (u_dut.compute_weight_byte[5] !== 8'sd1) ||
                    (u_dut.compute_weight_byte[6] !== 8'sd1) ||
                    (u_dut.compute_weight_byte[7] !== 8'sd1)) begin
                    $fatal(1, "K=4608 权重末项 index=4607 未被 8 个 lane MAC 读取");
                end
                final_tap_lane_mask <= 8'hff;
            end
        end
    end

    initial begin : run_boundary_cases
        integer wait_cycles;
        repeat (3) @(negedge clk);
        hard_reset = 1'b0;
        wait (start_ready === 1'b1);
        @(negedge clk);
        start_valid = 1'b1;
        @(negedge clk);
        start_valid = 1'b0;

        wait_cycles = 0;
        while (result_valid !== 1'b1) begin
            @(negedge clk);
            wait_cycles = wait_cycles + 1;
            if (wait_cycles > 2000000) begin
                $fatal(1, "K=4608 accepted-run timed out; requests=%0d feature=%0d weight=%0d output=%0d state=%0d group=%0d lane=%0d weight_index=%0d compute_index=%0d",
                       request_count, feature_read_count, weight_read_count, output_write_count,
                       u_dut.state, u_dut.output_group_base, u_dut.weight_lane_index,
                       u_dut.weight_reduction_index, u_dut.compute_reduction_index);
            end
        end
        if (result_error_code !== 3'd0) begin
            $fatal(1, "K=4608 must be accepted, result_error_code=%0d", result_error_code);
        end
        if ((feature_read_count != 4608) || (weight_read_count != 36864) ||
            (output_write_count != 8) || (request_count != 41480)) begin
            $fatal(1, "K=4608 transfer coverage mismatch total=%0d feature=%0d weight=%0d output=%0d",
                   request_count, feature_read_count, weight_read_count, output_write_count);
        end
        if (!group_override_done || (group_override_count != 1) ||
            (lane7_index4607_request_count != 1) ||
            (final_package_byte_request_count != 1) || (final_tap_count != 1) ||
            (final_tap_lane_mask != 8'hff)) begin
            $fatal(1, "K=4608 boundary coverage missing: deposit=%0d/%0d lane7_index4607=%0d final_byte=%0d final_tap=%0d lane_mask=%02h",
                   group_override_done, group_override_count, lane7_index4607_request_count,
                   final_package_byte_request_count, final_tap_count, final_tap_lane_mask);
        end
        $display("K4608_PASS requests=%0d feature_reads=%0d weight_reads=%0d output_writes=%0d lane7_index4607_fetches=%0d final_ram_reads=8 observed_package_last_byte=%016h responder_word=01010101",
                 request_count, feature_read_count, weight_read_count, output_write_count,
                 lane7_index4607_request_count, EXPECTED_FINAL_PACKAGE_BYTE);

        repeat (2) @(negedge clk);
        hard_reset = 1'b1;
        repeat (2) @(negedge clk);
        input_length_bytes = 32'd4609;
        input_channels = 32'd4609;
        input_height = 32'd1;
        input_width = 32'd1;
        kernel_height = 32'd1;
        kernel_width = 32'd1;
        output_length_bytes = 32'd512;
        output_channels = 32'd512;
        output_height = 32'd1;
        output_width = 32'd1;
        quantized_weight_bytes = 32'd2359808;
        quantized_weight_offset = 32'd0;
        weight_package_length_bytes = 32'd2359808;
        hard_reset = 1'b0;
        wait (start_ready === 1'b1);
        @(negedge clk);
        bad_k_request_baseline = request_count;
        start_valid = 1'b1;
        @(negedge clk);
        start_valid = 1'b0;

        wait_cycles = 0;
        while (result_valid !== 1'b1) begin
            @(negedge clk);
            wait_cycles = wait_cycles + 1;
            if (wait_cycles > 20) begin
                $fatal(1, "K=4609 reject-run timed out; new_requests=%0d", request_count - bad_k_request_baseline);
            end
        end
        if ((result_error_code !== 3'd1) || (request_count != bad_k_request_baseline)) begin
            $fatal(1, "K=4609 must BAD_ARGUMENT before any memory access: error=%0d new_requests=%0d",
                   result_error_code, request_count - bad_k_request_baseline);
        end
        $display("K4609_REJECT_PASS result_error_code=%0d prevalidation_memory_requests=%0d input_bytes=%0d quantized_weight_bytes=%0d package_length=%0d",
                 result_error_code, request_count - bad_k_request_baseline,
                 input_length_bytes, quantized_weight_bytes, weight_package_length_bytes);
        $display("PASS: K=4608 max reduction reads lane RAM index4607; K=4609 BAD_ARGUMENT before memory access");
        $finish;
    end
endmodule
