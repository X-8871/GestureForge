`timescale 1ns/1ps
module tb_s2c_rtl06_lane32_tile;
    import s2a_network_descriptor_pkg::*;

    localparam integer INPUT_BYTES = 519168;
    localparam integer WEIGHT_BYTES = 864;
    localparam integer OUTPUT_BYTES = 1384448;
    localparam integer FIRST_TILE_OUTPUTS = 32 * 16 * 16;
    localparam integer OUTPUT_GROUP_COUNT = (S2A_OUTPUT_C[0] + 31) / 32;
    localparam logic [31:0] INPUT_FIXTURE_BASE = S2A_INPUT_ADDRESS[0][0];
    localparam logic [31:0] WEIGHT_FIXTURE_BASE = S2A_GF8_PACKAGE_BASE[0] + S2A_GF8_WEIGHT_OFFSET[0];
    localparam logic [31:0] OUTPUT_FIXTURE_BASE = S2A_OUTPUT_ADDRESS[0];

    logic clk = 1'b0;
    logic hard_reset = 1'b1;
    logic start_valid = 1'b0;
    logic start_ready;
    logic busy;
    logic result_valid;
    logic [2:0] result_error_code;
    logic backend_cancel;
    logic backend_req_valid;
    logic backend_req_write;
    logic [31:0] backend_req_addr;
    logic [31:0] backend_req_wdata;
    logic [3:0] backend_req_rstrb;
    logic [3:0] backend_req_wstrb;
    logic backend_rsp_valid = 1'b0;
    logic [31:0] backend_rsp_rdata = 32'd0;
    logic [2:0] backend_rsp_error = 3'd0;
    logic [7:0] input_fixture [0:INPUT_BYTES-1];
    logic [7:0] weight_fixture [0:WEIGHT_BYTES-1];
    logic [7:0] output_golden [0:OUTPUT_BYTES-1];
    integer cycle_count = 0;
    integer feature_read_count = 0;
    integer weight_read_count = 0;
    integer output_write_count = 0;
    wire abort = (output_write_count == FIRST_TILE_OUTPUTS) && !backend_rsp_valid;
    integer feature_bank_write_count = 0;
    integer feature_bank_read_count = 0;
    integer write_byte_lane;
    integer write_offset;
    integer write_channel;
    integer write_row;
    integer write_column;
    integer output_seen_index;
    integer fd;
    integer byte_value;
    integer index;
    logic [FIRST_TILE_OUTPUTS-1:0] output_seen;

    always #5 clk = ~clk;

    s2b_conv_tile_engine #(
        .FROZEN_CONV_DESCRIPTOR(1'b1),
        .FROZEN_OUTPUT_LANES(32)
    ) dut (
        .clk(clk), .hard_reset(hard_reset), .abort(abort), .buffer_owner_pl(1'b1),
        .start_valid(start_valid), .start_ready(start_ready),
        .layer_index(32'd0), .weight_layer_index(32'd0),
        .input_base_address(S2A_INPUT_ADDRESS[0][0]),
        .input_length_bytes(S2A_INPUT_LENGTH_BYTES[0][0]),
        .input_batch_count({16'd0, S2A_INPUT_N[0][0]}),
        .input_channels({16'd0, S2A_INPUT_C[0][0]}),
        .input_height({16'd0, S2A_INPUT_H[0][0]}),
        .input_width({16'd0, S2A_INPUT_W[0][0]}),
        .output_base_address(S2A_OUTPUT_ADDRESS[0]),
        .output_length_bytes(S2A_OUTPUT_LENGTH_BYTES[0]),
        .output_batch_count({16'd0, S2A_OUTPUT_N[0]}),
        .output_channels({16'd0, S2A_OUTPUT_C[0]}),
        .output_height({16'd0, S2A_OUTPUT_H[0]}),
        .output_width({16'd0, S2A_OUTPUT_W[0]}),
        .kernel_height({24'd0, S2A_KERNEL_H[0]}),
        .kernel_width({24'd0, S2A_KERNEL_W[0]}),
        .stride_y({24'd0, S2A_STRIDE_H[0]}),
        .stride_x({24'd0, S2A_STRIDE_W[0]}),
        .pad_left({24'd0, S2A_PADDING_LEFT[0]}),
        .pad_right({24'd0, S2A_PADDING_RIGHT[0]}),
        .pad_top({24'd0, S2A_PADDING_TOP[0]}),
        .pad_bottom({24'd0, S2A_PADDING_BOTTOM[0]}),
        .groups(32'd1), .padding_value_int8(32'sd0),
        .weight_package_base_address(S2A_GF8_PACKAGE_BASE[0]),
        .weight_package_length_bytes(S2A_GF8_PACKAGE_LENGTH[0]),
        .quantized_weight_offset(S2A_GF8_WEIGHT_OFFSET[0]),
        .quantized_weight_bytes(S2A_GF8_WEIGHT_BYTES[0]),
        .output_batch(32'd0),
        .activation_mode((S2A_ACTIVATION[0] == S2A_ACT_LEAKY) ? 2'd1 : 2'd0),
        .backend_cancel(backend_cancel),
        .backend_req_valid(backend_req_valid), .backend_req_ready(1'b1),
        .backend_req_write(backend_req_write), .backend_req_addr(backend_req_addr),
        .backend_req_wdata(backend_req_wdata), .backend_req_rstrb(backend_req_rstrb),
        .backend_req_wstrb(backend_req_wstrb),
        .backend_rsp_valid(backend_rsp_valid), .backend_rsp_rdata(backend_rsp_rdata),
        .backend_rsp_error(backend_rsp_error),
        .busy(busy), .result_valid(result_valid), .result_ready(1'b0),
        .result_error_code(result_error_code)
    );

    function automatic logic [31:0] fixture_word(input logic [31:0] word_address);
        integer byte_index;
        logic [31:0] byte_address;
        logic [31:0] fixture_offset;
        begin
            fixture_word = 32'd0;
            for (byte_index = 0; byte_index < 4; byte_index = byte_index + 1) begin
                byte_address = word_address + byte_index;
                if ((byte_address >= INPUT_FIXTURE_BASE) &&
                    (byte_address < INPUT_FIXTURE_BASE + INPUT_BYTES)) begin
                    fixture_offset = byte_address - INPUT_FIXTURE_BASE;
                    fixture_word[byte_index*8 +: 8] = input_fixture[fixture_offset];
                end else if ((byte_address >= WEIGHT_FIXTURE_BASE) &&
                             (byte_address < WEIGHT_FIXTURE_BASE + WEIGHT_BYTES)) begin
                    fixture_offset = byte_address - WEIGHT_FIXTURE_BASE;
                    fixture_word[byte_index*8 +: 8] = weight_fixture[fixture_offset];
                end
            end
        end
    endfunction

    function automatic integer onehot_lane(input logic [3:0] strobe);
        begin
            case (strobe)
                4'b0001: onehot_lane = 0;
                4'b0010: onehot_lane = 1;
                4'b0100: onehot_lane = 2;
                4'b1000: onehot_lane = 3;
                default: onehot_lane = -1;
            endcase
        end
    endfunction

    always @(negedge clk) begin
        if (!hard_reset && !abort) begin
            if (result_valid) begin
                $fatal(1, "首tile完成前engine提前返回，错误码=%0d", result_error_code);
            end
            if (cycle_count > 200000) begin
                $fatal(1, "首tile仿真超过周期上限");
            end
        end
    end

    always @(posedge clk) begin
        if (hard_reset) begin
            backend_rsp_valid <= 1'b0;
            backend_rsp_rdata <= 32'd0;
            cycle_count <= 0;
            feature_read_count <= 0;
            weight_read_count <= 0;
            output_write_count <= 0;
            feature_bank_write_count <= 0;
            feature_bank_read_count <= 0;
        end else begin
            cycle_count <= cycle_count + 1;
            backend_rsp_valid <= backend_req_valid;
            if (dut.feature_bank_wr_en) begin
                feature_bank_write_count <= feature_bank_write_count + 1;
                if (dut.feature_bank_wr_bad_address) begin
                    $fatal(1, "engine特征补丁bank写地址越界");
                end
            end
            if (dut.feature_bank_rd_en) begin
                feature_bank_read_count <= feature_bank_read_count + 1;
                if ((dut.feature_bank_rd_lane_active !== 16'h0001) ||
                    dut.feature_bank_rd_conflict || dut.feature_bank_rd_bad_address) begin
                    $fatal(1, "engine单lane bank读请求无效");
                end
            end
            if (backend_req_valid && !backend_req_write) begin
                backend_rsp_rdata <= fixture_word(backend_req_addr);
                if ((backend_req_addr >= INPUT_FIXTURE_BASE) &&
                    (backend_req_addr < INPUT_FIXTURE_BASE + INPUT_BYTES)) begin
                    feature_read_count <= feature_read_count + 1;
                end else if ((backend_req_addr >= WEIGHT_FIXTURE_BASE) &&
                             (backend_req_addr < WEIGHT_FIXTURE_BASE + WEIGHT_BYTES)) begin
                    weight_read_count <= weight_read_count + 1;
                end else begin
                    $fatal(1, "冻结首层发生未知读地址 %08x", backend_req_addr);
                end
                if (onehot_lane(backend_req_rstrb) < 0) begin
                    $fatal(1, "读请求strobe不是单字节 one-hot");
                end
            end else if (backend_req_valid && backend_req_write) begin
                write_byte_lane = onehot_lane(backend_req_wstrb);
                if (write_byte_lane < 0) begin
                    $fatal(1, "写请求strobe不是单字节 one-hot");
                end
                write_offset = backend_req_addr + write_byte_lane - OUTPUT_FIXTURE_BASE;
                if ((write_offset < 0) || (write_offset >= OUTPUT_BYTES)) begin
                    $fatal(1, "输出地址超出首层golden范围");
                end
                write_channel = write_offset / (208 * 208);
                write_row = (write_offset % (208 * 208)) / 208;
                write_column = write_offset % 208;
                if ((write_channel >= 32) || (write_row >= 16) || (write_column >= 16)) begin
                    $fatal(1, "首tile写到范围外坐标 c=%0d y=%0d x=%0d",
                        write_channel, write_row, write_column);
                end
                output_seen_index = write_channel * 256 + write_row * 16 + write_column;
                if (output_seen[output_seen_index]) begin
                    $fatal(1, "首tile输出坐标重复写入 c=%0d y=%0d x=%0d",
                        write_channel, write_row, write_column);
                end
                output_seen[output_seen_index] <= 1'b1;
                if (backend_req_wdata[write_byte_lane*8 +: 8] !== output_golden[write_offset]) begin
                    $display("diff offset=%0d c=%0d y=%0d x=%0d expected=%02x actual=%02x",
                        write_offset, write_channel, write_row, write_column,
                        output_golden[write_offset], backend_req_wdata[write_byte_lane*8 +: 8]);
                    $fatal(1, "banked engine与layer0冻结golden不等价");
                end
                output_write_count <= output_write_count + 1;
            end else begin
                backend_rsp_rdata <= 32'd0;
            end
        end
    end

    initial begin
        output_seen = '0;
        if (dut.LANE_COUNT != 32) $fatal(1, "DUT未按32输出lane配置：%0d", dut.LANE_COUNT);
        fd = $fopen("D:\\FPGA_Competition\\report\\evidence\\S2A-T66\\tile01\\fixture\\sample0_input_chw_int8.bin", "rb");
        if (fd == 0) $fatal(1, "输入fixture无法打开");
        for (index = 0; index < INPUT_BYTES; index = index + 1) begin
            byte_value = $fgetc(fd);
            if (byte_value < 0) $fatal(1, "输入fixture截断");
            input_fixture[index] = byte_value[7:0];
        end
        if ($fgetc(fd) >= 0) $fatal(1, "输入fixture长度超预期");
        $fclose(fd);

        fd = $fopen("D:\\FPGA_Competition\\report\\evidence\\S2A-T66\\tile01\\fixture\\sample0_layer0_gf8_weights.bin", "rb");
        if (fd == 0) $fatal(1, "权重fixture无法打开");
        for (index = 0; index < WEIGHT_BYTES; index = index + 1) begin
            byte_value = $fgetc(fd);
            if (byte_value < 0) $fatal(1, "权重fixture截断");
            weight_fixture[index] = byte_value[7:0];
        end
        if ($fgetc(fd) >= 0) $fatal(1, "权重fixture长度超预期");
        $fclose(fd);

        fd = $fopen("D:\\FPGA_Competition\\report\\evidence\\S2A-T66\\tile01\\fixture\\sample0_layer0_expected_nchw_int8.bin", "rb");
        if (fd == 0) $fatal(1, "layer0 golden无法打开");
        for (index = 0; index < OUTPUT_BYTES; index = index + 1) begin
            byte_value = $fgetc(fd);
            if (byte_value < 0) $fatal(1, "layer0 golden截断");
            output_golden[index] = byte_value[7:0];
        end
        if ($fgetc(fd) >= 0) $fatal(1, "layer0 golden长度超预期");
        $fclose(fd);

        repeat (3) @(negedge clk);
        hard_reset = 1'b0;
        @(negedge clk);
        if (!start_ready) $fatal(1, "engine未就绪");
        start_valid = 1'b1;
        @(negedge clk);
        start_valid = 1'b0;

        wait (abort);
        repeat (3) @(posedge clk);
        if (feature_read_count != 3072) begin
            $fatal(1, "首tile输入请求数错误：%0d", feature_read_count);
        end
        if (weight_read_count != WEIGHT_BYTES) begin
            $fatal(1, "首tile权重请求数错误：%0d", weight_read_count);
        end
        if (output_write_count != FIRST_TILE_OUTPUTS) begin
            $fatal(1, "首tile输出数错误：%0d", output_write_count);
        end
        if (feature_bank_write_count != 3267) begin
            $fatal(1, "首tilebank补丁写入数错误：%0d", feature_bank_write_count);
        end
        if (feature_bank_read_count != (6627 * OUTPUT_GROUP_COUNT)) begin
            $fatal(1, "首tilebank有效tap读取数错误：expected=%0d actual=%0d",
                6627 * OUTPUT_GROUP_COUNT, feature_bank_read_count);
        end
        for (index = 0; index < FIRST_TILE_OUTPUTS; index = index + 1) begin
            if (!output_seen[index]) begin
                $fatal(1, "首tile输出缺失 index=%0d c=%0d y=%0d x=%0d",
                    index, index / 256, (index % 256) / 16, index % 16);
            end
        end
        $display("PASS S2C-RTL06 lane32 layer0 tile0 golden match: ext_input=%0d weights=%0d bank_wr=%0d bank_rd=%0d outputs=%0d cycles=%0d",
            feature_read_count, weight_read_count, feature_bank_write_count,
            feature_bank_read_count, output_write_count, cycle_count);
        $finish;
    end
endmodule
