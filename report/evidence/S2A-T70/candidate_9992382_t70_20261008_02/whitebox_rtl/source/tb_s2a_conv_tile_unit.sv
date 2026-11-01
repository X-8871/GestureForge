// 新 tile 的白盒单点算术回归；不验证内存或整层遍历。
`timescale 1ns/1ps
module tb_s2a_conv_tile_unit;
    import s2a_network_descriptor_pkg::*;
    logic clk = 0;
    logic hard_reset = 0, abort = 0, start_valid = 0;
    logic start_ready, result_valid, busy;
    logic [2:0] result_error_code;
    integer layer_id = 0;
    integer fd, ordinal, kind, channel, y, x, k, lanes;
    integer i, l, ic, ky, kx, idx, group_base, ty, tx, th, tw, ph, pw, point;
    integer expected_acc [0:7];
    integer expected_byte [0:7];
    integer query_count = 0, lane_checks = 0;
    integer cycles;
    logic [31:0] hdr [0:7];
    logic [31:0] word_work;
    integer byte_work;
    logic [7:0] activations [0:8191];
    logic [7:0] weights [0:36863];
    always #5 clk = ~clk;

    s2a_conv_tile_engine dut (
        .clk(clk), .hard_reset(hard_reset), .abort(abort), .buffer_owner_pl(1'b1),
        .start_valid(start_valid), .start_ready(start_ready),
        .layer_index(layer_id), .weight_layer_index(layer_id),
        .input_base_address(S2A_INPUT_ADDRESS[layer_id][0]),
        .input_length_bytes(S2A_INPUT_LENGTH_BYTES[layer_id][0]),
        .input_batch_count({16'd0,S2A_INPUT_N[layer_id][0]}),
        .input_channels({16'd0,S2A_INPUT_C[layer_id][0]}),
        .input_height({16'd0,S2A_INPUT_H[layer_id][0]}),
        .input_width({16'd0,S2A_INPUT_W[layer_id][0]}),
        .output_base_address(S2A_OUTPUT_ADDRESS[layer_id]),
        .output_length_bytes(S2A_OUTPUT_LENGTH_BYTES[layer_id]),
        .output_batch_count({16'd0,S2A_OUTPUT_N[layer_id]}),
        .output_channels({16'd0,S2A_OUTPUT_C[layer_id]}),
        .output_height({16'd0,S2A_OUTPUT_H[layer_id]}),
        .output_width({16'd0,S2A_OUTPUT_W[layer_id]}),
        .kernel_height({24'd0,S2A_KERNEL_H[layer_id]}),
        .kernel_width({24'd0,S2A_KERNEL_W[layer_id]}),
        .stride_y({24'd0,S2A_STRIDE_H[layer_id]}),
        .stride_x({24'd0,S2A_STRIDE_W[layer_id]}),
        .pad_left({24'd0,S2A_PADDING_LEFT[layer_id]}),
        .pad_right({24'd0,S2A_PADDING_RIGHT[layer_id]}),
        .pad_top({24'd0,S2A_PADDING_TOP[layer_id]}),
        .pad_bottom({24'd0,S2A_PADDING_BOTTOM[layer_id]}),
        .groups(32'd1), .padding_value_int8(32'sd0),
        .weight_package_base_address(S2A_GF8_PACKAGE_BASE[layer_id]),
        .weight_package_length_bytes(S2A_GF8_PACKAGE_LENGTH[layer_id]),
        .quantized_weight_offset(S2A_GF8_WEIGHT_OFFSET[layer_id]),
        .quantized_weight_bytes(S2A_GF8_WEIGHT_BYTES[layer_id]),
        // 描述符包为 linear=1/leaky=2；engine 接口为 linear=0/leaky=1。
        .output_batch(32'd0), .activation_mode((S2A_ACTIVATION[layer_id] == S2A_ACT_LEAKY) ? 2'd1 : 2'd0),
        .backend_cancel(), .backend_req_valid(), .backend_req_ready(1'b0),
        .backend_req_write(), .backend_req_addr(), .backend_req_wdata(),
        .backend_req_rstrb(), .backend_req_wstrb(),
        .backend_rsp_valid(1'b0), .backend_rsp_rdata(32'd0), .backend_rsp_error(3'd0),
        .busy(busy), .result_valid(result_valid), .result_ready(1'b0),
        .result_error_code(result_error_code)
    );

    task automatic read_u32(output logic [31:0] value);
        integer b, j;
        begin
            value = 0;
            for (j = 0; j < 4; j = j + 1) begin
                b = $fgetc(fd);
                if (b < 0) $fatal(1, "截断 header 或 oracle");
                value = value | ((b & 255) << (8*j));
            end
        end
    endtask

    initial begin
        fd = $fopen("queries.bin", "rb");
        if (fd == 0) $fatal(1, "queries.bin 缺失");
        hard_reset = 1;
        repeat (2) @(negedge clk);
        hard_reset = 0;
        while (!$feof(fd)) begin
            // 首字节用于区分正常 EOF 与记录截断。
            byte_work = $fgetc(fd);
            if (byte_work < 0) break;
            hdr[0] = byte_work;
            for (i = 1; i < 4; i = i + 1) begin
                byte_work = $fgetc(fd);
                if (byte_work < 0) $fatal(1,"截断 layer header");
                hdr[0] = hdr[0] | ((byte_work & 255) << (8*i));
            end
            for (i = 1; i < 8; i = i + 1) read_u32(hdr[i]);
            layer_id = hdr[0]; ordinal = hdr[1]; kind = hdr[2]; channel = hdr[3];
            y = hdr[4]; x = hdr[5]; k = hdr[6]; lanes = hdr[7];
            if ((layer_id >= 38) || (k <= 0) || (k > 8191) || (lanes < 1) || (lanes > 8))
                $fatal(1,"非法查询记录");
            for (i = 0; i < k; i = i + 1) begin
                byte_work = $fgetc(fd);
                if (byte_work < 0) $fatal(1,"截断 activation");
                activations[i] = byte_work[7:0];
            end
            if (lanes*k > 36864) $fatal(1,"weight_group 容量超限");
            for (i = 0; i < lanes*k; i = i + 1) begin
                byte_work = $fgetc(fd);
                if (byte_work < 0) $fatal(1,"截断 weight");
                weights[i] = byte_work[7:0];
            end
            for (l = 0; l < lanes; l = l + 1) begin
                read_u32(word_work);
                expected_acc[l] = $signed(word_work);
                byte_work = $fgetc(fd);
                if (byte_work < 0) $fatal(1,"截断输出 oracle");
                expected_byte[l] = byte_work;
            end
            group_base = (channel/8)*8; ty = (y/8)*8; tx = (x/8)*8;
            th = ((S2A_OUTPUT_H[layer_id]-ty) < 8) ? S2A_OUTPUT_H[layer_id]-ty : 8;
            tw = ((S2A_OUTPUT_W[layer_id]-tx) < 8) ? S2A_OUTPUT_W[layer_id]-tx : 8;
            ph = (th-1)*S2A_STRIDE_H[layer_id] + S2A_KERNEL_H[layer_id];
            pw = (tw-1)*S2A_STRIDE_W[layer_id] + S2A_KERNEL_W[layer_id];
            point = (y-ty)*tw + x-tx;
            if (lanes != ((S2A_OUTPUT_C[layer_id]-group_base < 8) ? S2A_OUTPUT_C[layer_id]-group_base : 8))
                $fatal(1,"尾组 lane 数错误");
            if (k != S2A_INPUT_C[layer_id][0]*S2A_KERNEL_H[layer_id]*S2A_KERNEL_W[layer_id])
                $fatal(1,"实际模型 K 不一致");
            @(negedge clk); start_valid = 1;
            @(negedge clk); start_valid = 0;
            // 生产验证状态必须通过，随后仅白盒选择计算起点。
            @(negedge clk);
            if (dut.state != dut.ST_TILE_PREP) $fatal(1,"真实 descriptor 未通过验证 state=%0d layer=%0d error=%0d validation=%0d", dut.state, layer_id, result_error_code, dut.validation_error);
            dut.tile_start_y = ty; dut.tile_start_x = tx;
            dut.tile_height = th; dut.tile_width = tw;
            dut.patch_height = ph; dut.patch_width = pw;
            dut.patch_byte_count = ph*pw*S2A_INPUT_C[layer_id][0];
            dut.tile_point_count = th*tw; dut.output_group_base = group_base;
            dut.group_lane_count = lanes;
            // 只预装所选点实际使用的 reduction；不声称其他 patch 元素被测试。
            for (i = 0; i < k; i = i + 1) begin
                ic = i/(S2A_KERNEL_H[layer_id]*S2A_KERNEL_W[layer_id]);
                ky = (i%(S2A_KERNEL_H[layer_id]*S2A_KERNEL_W[layer_id]))/S2A_KERNEL_W[layer_id];
                kx = i%S2A_KERNEL_W[layer_id];
                idx = ic*ph*pw + ((y-ty)*S2A_STRIDE_H[layer_id]+ky)*pw + (x-tx)*S2A_STRIDE_W[layer_id]+kx;
                if (idx >= 51200) $fatal(1,"patch 索引超限");
                dut.feature_patch[idx] = $signed(activations[i]);
            end
            for (l = 0; l < lanes; l = l + 1) begin
                for (i = 0; i < k; i = i + 1) begin
                    case (l)
                        0: dut.gen_weight_lane_bank[0].lane_weight_memory[i] = $signed(weights[l*k+i]);
                        1: dut.gen_weight_lane_bank[1].lane_weight_memory[i] = $signed(weights[l*k+i]);
                        2: dut.gen_weight_lane_bank[2].lane_weight_memory[i] = $signed(weights[l*k+i]);
                        3: dut.gen_weight_lane_bank[3].lane_weight_memory[i] = $signed(weights[l*k+i]);
                        4: dut.gen_weight_lane_bank[4].lane_weight_memory[i] = $signed(weights[l*k+i]);
                        5: dut.gen_weight_lane_bank[5].lane_weight_memory[i] = $signed(weights[l*k+i]);
                        6: dut.gen_weight_lane_bank[6].lane_weight_memory[i] = $signed(weights[l*k+i]);
                        7: dut.gen_weight_lane_bank[7].lane_weight_memory[i] = $signed(weights[l*k+i]);
                    endcase
                end
            end
            dut.state = dut.ST_COMPUTE_PREP;
            @(negedge clk);
            dut.compute_point_index = point;
            cycles = 0;
            while (dut.state != dut.ST_COMPUTE_REQUANT) begin
                if (result_valid || cycles > k+4) $fatal(1,"计算异常 layer=%0d ordinal=%0d error=%0d",layer_id,ordinal,result_error_code);
                @(negedge clk); cycles = cycles + 1;
            end
            for (l = 0; l < lanes; l = l + 1) begin
                if ($signed(dut.lane_accumulator[l]) != expected_acc[l])
                    $fatal(1,"累加不符 layer=%0d ordinal=%0d lane=%0d",layer_id,ordinal,l);
            end
            @(negedge clk);
            for (l = 0; l < lanes; l = l + 1) begin
                if ((dut.output_block[l*64+point] & 255) != expected_byte[l])
                    $fatal(1,"INT8 不符 layer=%0d ordinal=%0d lane=%0d",layer_id,ordinal,l);
                lane_checks = lane_checks + 1;
            end
            abort = 1;
            @(negedge clk); abort = 0;
            // 撤销 abort 后允许 always_comb 更新 start_ready 再观察。
            #1;
            if (!start_ready) $fatal(1,"白盒 query 取消后未恢复 idle");
            query_count = query_count + 1;
            if (query_count % 1016 == 0) $display("CHECKPOINT TILE_WHITEBOX layer=%0d queries=%0d",layer_id,query_count);
        end
        $fclose(fd);
        if (query_count != 21336) $fatal(1,"查询总数不完整");
        $display("PASS TILE_WHITEBOX queries=%0d lane_checks=%0d",query_count,lane_checks);
        $finish;
    end
endmodule
