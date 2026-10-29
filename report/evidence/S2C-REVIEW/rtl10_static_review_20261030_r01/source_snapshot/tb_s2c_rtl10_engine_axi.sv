`timescale 1ns/1ps
module tb_s2c_rtl10_engine_axi;
    import s2a_network_descriptor_pkg::*;

    localparam integer INPUT_BYTES = 519168;
    localparam integer WEIGHT_BYTES = 864;
    localparam integer OUTPUT_BYTES = 1384448;
    localparam integer FIRST_TILE_BYTES = 32 * 16 * 16;
    localparam integer INPUT_ROW_BYTES = 416;
    localparam logic [31:0] INPUT_FIXTURE_BASE = S2A_INPUT_ADDRESS[0][0];
    localparam logic [31:0] WEIGHT_FIXTURE_BASE =
        S2A_GF8_PACKAGE_BASE[0] + S2A_GF8_WEIGHT_OFFSET[0];
    localparam logic [31:0] OUTPUT_FIXTURE_BASE = S2A_OUTPUT_ADDRESS[0];
    localparam logic [31:0] DDR_PHYSICAL_OFFSET = 32'h1000_0000;

    logic clk = 1'b0;
    logic hard_reset = 1'b1;
    logic engine_abort = 1'b0;
    logic start_valid = 1'b0;
    logic start_ready;
    logic busy;
    logic result_valid;
    logic result_ready = 1'b0;
    logic [2:0] result_error_code;
    logic backend_cancel;
    logic backend_req_valid;
    logic backend_req_ready;
    logic backend_req_write;
    logic [31:0] backend_req_addr;
    logic [31:0] backend_req_wdata;
    logic [3:0] backend_req_rstrb;
    logic [3:0] backend_req_wstrb;
    logic backend_rsp_valid = 1'b0;
    logic [31:0] backend_rsp_rdata = 32'd0;
    logic [2:0] backend_rsp_error = 3'd0;

    logic bulk_cmd_valid;
    logic bulk_cmd_ready;
    logic bulk_cmd_write;
    logic [31:0] bulk_cmd_addr;
    logic [7:0] bulk_cmd_bytes;
    logic bulk_wvalid;
    logic bulk_wready;
    logic [7:0] bulk_wdata;
    logic bulk_rvalid;
    logic bulk_rready;
    logic [7:0] bulk_rdata;
    logic bulk_done_valid;
    logic bulk_done_ready;
    logic [2:0] bulk_done_error;

    logic cold_reset;
    logic run_enable = 1'b1;
    logic cancel;
    logic clear_safe = 1'b0;
    logic [63:0] run_epoch = 64'h0000_0000_0000_0001;
    logic mem_valid;
    logic mem_write;
    logic [31:0] mem_addr;
    logic [31:0] mem_wdata;
    logic [3:0] mem_rstrb;
    logic [3:0] mem_wstrb;
    logic mem_ready;
    logic [31:0] mem_rdata;
    logic [2:0] mem_error_code;

    logic [5:0] m_axi_arid, m_axi_awid, m_axi_wid;
    logic [31:0] m_axi_araddr, m_axi_awaddr;
    logic [3:0] m_axi_arlen, m_axi_awlen;
    logic [2:0] m_axi_arsize, m_axi_awsize;
    logic [1:0] m_axi_arburst, m_axi_awburst, m_axi_arlock, m_axi_awlock;
    logic [3:0] m_axi_arcache, m_axi_awcache, m_axi_arqos, m_axi_awqos;
    logic [2:0] m_axi_arprot, m_axi_awprot;
    logic m_axi_arvalid, m_axi_arready;
    logic [5:0] m_axi_rid;
    logic [63:0] m_axi_rdata;
    logic [1:0] m_axi_rresp;
    logic m_axi_rlast, m_axi_rvalid, m_axi_rready;
    logic m_axi_awvalid, m_axi_awready;
    logic m_axi_wvalid, m_axi_wlast, m_axi_wready;
    logic [63:0] m_axi_wdata;
    logic [7:0] m_axi_wstrb;
    logic [5:0] m_axi_bid;
    logic [1:0] m_axi_bresp;
    logic m_axi_bvalid, m_axi_bready;

    logic ledger_empty;
    logic [63:0] ledger_epoch;
    logic recovery_required;
    logic protocol_isolated;
    logic first_fault_valid;
    logic [7:0] first_fault_code;
    logic [31:0] first_fault_address;
    logic fault_event_valid;
    logic [7:0] fault_event_code;
    logic [31:0] fault_event_address;
    logic req_withdrawn;
    logic clear_rejected;
    logic [9:0] axi_progress;
    logic [9:0] axi_progress_next;
    logic ledger_empty_next;
    logic [1:0] fault_event_resp;
    logic fault_event_write;
    logic fault_event_protocol;
    logic fault_event_address_valid;
    logic [31:0] fault_event_physical_address;

    logic [7:0] input_fixture [0:INPUT_BYTES-1];
    logic [7:0] weight_fixture [0:WEIGHT_BYTES-1];
    logic [7:0] output_golden [0:OUTPUT_BYTES-1];
    logic [FIRST_TILE_BYTES-1:0] output_seen = '0;
    logic fixtures_loaded = 1'b0;

    logic [31:0] prng = 32'h32B0_1C08;
    logic rd_active = 1'b0;
    logic rd_valid_reg = 1'b0;
    logic [31:0] rd_address = 32'd0;
    logic [3:0] rd_len = 4'd0;
    logic [2:0] rd_size = 3'd0;
    integer rd_index = 0;
    integer rd_delay = 0;
    logic [63:0] rd_data_reg = 64'd0;
    logic rd_last_reg = 1'b0;

    logic aw_seen = 1'b0;
    logic write_checked = 1'b0;
    logic bvalid_reg = 1'b0;
    logic [31:0] aw_address = 32'd0;
    logic [3:0] aw_len = 4'd0;
    logic [2:0] aw_size = 3'd0;
    integer write_beat_count = 0;
    integer b_delay = 0;
    logic [63:0] saved_wdata [0:15];
    logic [7:0] saved_wstrb [0:15];
    logic saved_wlast [0:15];
    logic [5:0] saved_wid [0:15];

    integer cycle_count = 0;
    integer start_cycle = 0;
    integer ar_count = 0;
    integer aw_count = 0;
    integer axi_w_count = 0;
    integer r_count = 0;
    integer b_count = 0;
    integer ar_size3_count = 0;
    integer ar_size0_count = 0;
    integer bulk_command_count = 0;
    integer feature_command_count = 0;
    integer weight_command_count = 0;
    integer output_command_count = 0;
    integer feature_command_bytes = 0;
    integer weight_command_bytes = 0;
    integer output_command_bytes = 0;
    integer legacy_request_count = 0;
    integer legacy_weight_read_count = 0;
    integer output_bulk_done_count = 0;
    integer output_byte_count = 0;
    integer w_before_aw_count = 0;
    integer aw_stall_count = 0;
    integer w_stall_count = 0;
    integer ar_stall_count = 0;
    integer r_delay_count = 0;
    integer b_delay_count = 0;
    logic current_bulk_write = 1'b0;

    integer fd = 0;
    integer index = 0;
    integer byte_value = 0;
    integer legacy_byte_address = 0;

    assign cold_reset = hard_reset;
    assign cancel = engine_abort;
    assign mem_valid = backend_req_valid;
    assign mem_write = backend_req_write;
    assign mem_addr = backend_req_addr;
    assign mem_wdata = backend_req_wdata;
    assign mem_rstrb = backend_req_rstrb;
    assign mem_wstrb = backend_req_wstrb;
    assign backend_req_ready = mem_ready;

    assign m_axi_arready = !rd_active && (prng[0] || prng[5]);
    assign m_axi_awready = !aw_seen && (prng[1] || prng[6]) &&
                           !((aw_count == 0) && (write_beat_count < 2));
    assign m_axi_wready = !write_checked && !bvalid_reg &&
                          (write_beat_count < 16) && (prng[2] || prng[7]);
    assign m_axi_rvalid = rd_valid_reg;
    assign m_axi_rdata = rd_data_reg;
    assign m_axi_rlast = rd_last_reg;
    assign m_axi_rid = 6'd0;
    assign m_axi_rresp = 2'b00;
    assign m_axi_bvalid = bvalid_reg;
    assign m_axi_bid = 6'd0;
    assign m_axi_bresp = 2'b00;

    always #5 clk = ~clk;

    s2b_conv_tile_engine #(
        .FROZEN_CONV_DESCRIPTOR(1'b1),
        .FROZEN_OUTPUT_LANES(32),
        .ENABLE_BULK(1'b1)
    ) dut (
        .clk(clk), .hard_reset(hard_reset), .abort(engine_abort),
        .buffer_owner_pl(1'b1), .start_valid(start_valid),
        .start_ready(start_ready),
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
        .backend_req_valid(backend_req_valid), .backend_req_ready(backend_req_ready),
        .backend_req_write(backend_req_write), .backend_req_addr(backend_req_addr),
        .backend_req_wdata(backend_req_wdata), .backend_req_rstrb(backend_req_rstrb),
        .backend_req_wstrb(backend_req_wstrb), .backend_rsp_valid(backend_rsp_valid),
        .backend_rsp_rdata(backend_rsp_rdata), .backend_rsp_error(backend_rsp_error),
        .bulk_cmd_valid(bulk_cmd_valid), .bulk_cmd_ready(bulk_cmd_ready),
        .bulk_cmd_write(bulk_cmd_write), .bulk_cmd_addr(bulk_cmd_addr),
        .bulk_cmd_bytes(bulk_cmd_bytes),
        .bulk_wvalid(bulk_wvalid), .bulk_wready(bulk_wready), .bulk_wdata(bulk_wdata),
        .bulk_rvalid(bulk_rvalid), .bulk_rready(bulk_rready), .bulk_rdata(bulk_rdata),
        .bulk_done_valid(bulk_done_valid), .bulk_done_ready(bulk_done_ready),
        .bulk_done_error(bulk_done_error), .busy(busy), .result_valid(result_valid),
        .result_ready(result_ready), .result_error_code(result_error_code)
    );

    s2c_hp0_bulk_adapter #(.ENABLE_BULK(1'b1)) adapter (.*);

    function automatic logic [7:0] model_read_byte(input logic [31:0] physical_address);
        logic [31:0] logical_address;
        integer offset;
        begin
            model_read_byte = 8'd0;
            if (physical_address >= DDR_PHYSICAL_OFFSET) begin
                logical_address = physical_address - DDR_PHYSICAL_OFFSET;
                if ((logical_address >= INPUT_FIXTURE_BASE) &&
                    (logical_address < INPUT_FIXTURE_BASE + INPUT_BYTES)) begin
                    offset = logical_address - INPUT_FIXTURE_BASE;
                    model_read_byte = input_fixture[offset];
                end else if ((logical_address >= WEIGHT_FIXTURE_BASE) &&
                             (logical_address < WEIGHT_FIXTURE_BASE + WEIGHT_BYTES)) begin
                    offset = logical_address - WEIGHT_FIXTURE_BASE;
                    model_read_byte = weight_fixture[offset];
                end
            end
        end
    endfunction

    function automatic logic [63:0] memory_word(input logic [31:0] physical_word_address);
        logic [63:0] value;
        begin
            value = 64'd0;
            for (int lane = 0; lane < 8; lane++)
                value[8*lane +: 8] = model_read_byte(physical_word_address + 32'(lane));
            return value;
        end
    endfunction

    function automatic integer onehot_lane(input logic [3:0] strobe);
        begin
            case (strobe)
                4'b0001: return 0;
                4'b0010: return 1;
                4'b0100: return 2;
                4'b1000: return 3;
                default: return -1;
            endcase
        end
    endfunction

    task automatic check_write_burst();
        integer beats;
        integer logical_address;
        integer output_offset;
        integer output_channel;
        integer output_row;
        integer output_column;
        integer seen_index;
        begin
            beats = aw_len + 1;
            if (aw_size != 3 || beats != 2 || aw_address[2:0] != 3'd0)
                $fatal(1, "首tile物理写突发属性错误 addr=%08x len=%0d size=%0d",
                       aw_address, aw_len, aw_size);
            if ((aw_address[11:0] + (beats * 8)) > 4096)
                $fatal(1, "物理写突发跨越4KiB页界");
            for (int beat = 0; beat < beats; beat++) begin
                if (saved_wid[beat] != 0 || saved_wstrb[beat] != 8'hff ||
                    saved_wlast[beat] !== (beat == beats - 1))
                    $fatal(1, "物理W属性错误 beat=%0d wid=%0d strb=%02x last=%b",
                           beat, saved_wid[beat], saved_wstrb[beat], saved_wlast[beat]);
                for (int lane = 0; lane < 8; lane++) begin
                    logical_address = aw_address + (beat * 8) + lane - DDR_PHYSICAL_OFFSET;
                    if ((logical_address < OUTPUT_FIXTURE_BASE) ||
                        (logical_address >= OUTPUT_FIXTURE_BASE + OUTPUT_BYTES))
                        $fatal(1, "物理W地址落在golden对象外 addr=%08x", logical_address);
                    output_offset = logical_address - OUTPUT_FIXTURE_BASE;
                    output_channel = output_offset / (208 * 208);
                    output_row = (output_offset % (208 * 208)) / 208;
                    output_column = output_offset % 208;
                    if ((output_channel >= 32) || (output_row >= 16) ||
                        (output_column >= 16))
                        $fatal(1, "物理W地址超出首tile坐标 c=%0d y=%0d x=%0d",
                               output_channel, output_row, output_column);
                    seen_index = output_channel * 256 + output_row * 16 + output_column;
                    if (output_seen[seen_index])
                        $fatal(1, "物理W地址重复覆盖golden index=%0d", seen_index);
                    if (saved_wdata[beat][8*lane +: 8] !== output_golden[output_offset])
                        $fatal(1, "物理W/golden不符 addr=%08x expect=%02x got=%02x",
                               logical_address, output_golden[output_offset],
                               saved_wdata[beat][8*lane +: 8]);
                    output_seen[seen_index] = 1'b1;
                    output_byte_count = output_byte_count + 1;
                end
            end
        end
    endtask

    always @(negedge clk) begin
        if (!hard_reset && cycle_count > 200000)
            $fatal(1, "RTL10首tile AXI仿真超过周期看门狗");
    end

    always @(posedge clk) begin
        if (hard_reset) begin
            backend_rsp_valid <= 1'b0;
            backend_rsp_rdata <= 32'd0;
            backend_rsp_error <= 3'd0;
            prng <= 32'h32B0_1C08;
            rd_active <= 1'b0;
            rd_valid_reg <= 1'b0;
            rd_address <= 32'd0;
            rd_len <= 4'd0;
            rd_size <= 3'd0;
            rd_index <= 0;
            rd_delay <= 0;
            rd_data_reg <= 64'd0;
            rd_last_reg <= 1'b0;
            aw_seen <= 1'b0;
            write_checked <= 1'b0;
            bvalid_reg <= 1'b0;
            aw_address <= 32'd0;
            aw_len <= 4'd0;
            aw_size <= 3'd0;
            write_beat_count <= 0;
            b_delay <= 0;
            cycle_count <= 0;
            ar_count <= 0;
            aw_count <= 0;
            axi_w_count <= 0;
            r_count <= 0;
            b_count <= 0;
            ar_size3_count <= 0;
            ar_size0_count <= 0;
            bulk_command_count <= 0;
            feature_command_count <= 0;
            weight_command_count <= 0;
            output_command_count <= 0;
            feature_command_bytes <= 0;
            weight_command_bytes <= 0;
            output_command_bytes <= 0;
            legacy_request_count <= 0;
            legacy_weight_read_count <= 0;
            output_bulk_done_count <= 0;
            output_byte_count <= 0;
            w_before_aw_count <= 0;
            aw_stall_count <= 0;
            w_stall_count <= 0;
            ar_stall_count <= 0;
            r_delay_count <= 0;
            b_delay_count <= 0;
            current_bulk_write <= 1'b0;
        end else begin
            cycle_count <= cycle_count + 1;
            prng <= {prng[30:0], prng[31] ^ prng[21] ^ prng[1] ^ prng[0]};
            backend_rsp_valid <= mem_ready;
            if (mem_ready) begin
                backend_rsp_rdata <= mem_rdata;
                backend_rsp_error <= mem_error_code;
            end

            if (backend_rsp_valid && backend_rsp_error != 3'd0)
                $fatal(1, "旧路径响应错误 code=%0d", backend_rsp_error);
            if (bulk_done_valid && bulk_done_ready && bulk_done_error != 3'd0)
                $fatal(1, "bulk完成错误 code=%0d", bulk_done_error);
            if (mem_valid && mem_ready) begin
                if (mem_write)
                    $fatal(1, "首tile测试出现旧路径写请求");
                legacy_byte_address = mem_addr + onehot_lane(mem_rstrb);
                if (onehot_lane(mem_rstrb) < 0)
                    $fatal(1, "旧路径请求读strobe不是单字节one-hot");
                legacy_request_count <= legacy_request_count + 1;
                if ((legacy_byte_address >= WEIGHT_FIXTURE_BASE) &&
                    (legacy_byte_address < WEIGHT_FIXTURE_BASE + WEIGHT_BYTES))
                    legacy_weight_read_count <= legacy_weight_read_count + 1;
                else if ((legacy_byte_address >= INPUT_FIXTURE_BASE) &&
                         (legacy_byte_address < INPUT_FIXTURE_BASE + INPUT_BYTES)) begin
                    // 旧路径输入读在T66首tile预期为零，但保留范围检查以便诊断。
                end else
                    $fatal(1, "旧路径逻辑读地址超出T66 fixture addr=%08x", mem_addr);
            end

            if (bulk_cmd_valid && bulk_cmd_ready) begin
                bulk_command_count <= bulk_command_count + 1;
                current_bulk_write <= bulk_cmd_write;
                if ((bulk_cmd_addr[2:0] != 0) || (bulk_cmd_bytes < 8) ||
                    (bulk_cmd_bytes > 128) || ((bulk_cmd_bytes % 8) != 0))
                    $fatal(1, "engine发出非法bulk命令 addr=%08x bytes=%0d",
                           bulk_cmd_addr, bulk_cmd_bytes);
                if (!bulk_cmd_write && (bulk_cmd_addr >= INPUT_FIXTURE_BASE) &&
                    (bulk_cmd_addr < INPUT_FIXTURE_BASE + INPUT_BYTES)) begin
                    if (((bulk_cmd_addr - INPUT_FIXTURE_BASE) % INPUT_ROW_BYTES) +
                        bulk_cmd_bytes > INPUT_ROW_BYTES)
                        $fatal(1, "特征bulk命令越过输入行尾");
                    feature_command_count <= feature_command_count + 1;
                    feature_command_bytes <= feature_command_bytes + bulk_cmd_bytes;
                end else if (!bulk_cmd_write &&
                             (bulk_cmd_addr >= WEIGHT_FIXTURE_BASE) &&
                             (bulk_cmd_addr < WEIGHT_FIXTURE_BASE + WEIGHT_BYTES)) begin
                    if (bulk_cmd_addr + bulk_cmd_bytes > WEIGHT_FIXTURE_BASE + WEIGHT_BYTES)
                        $fatal(1, "权重bulk命令越过对象尾部");
                    weight_command_count <= weight_command_count + 1;
                    weight_command_bytes <= weight_command_bytes + bulk_cmd_bytes;
                end else if (bulk_cmd_write &&
                             (bulk_cmd_addr >= OUTPUT_FIXTURE_BASE) &&
                             (bulk_cmd_addr < OUTPUT_FIXTURE_BASE + OUTPUT_BYTES)) begin
                    output_command_count <= output_command_count + 1;
                    output_command_bytes <= output_command_bytes + bulk_cmd_bytes;
                end else
                    $fatal(1, "bulk命令与输入/权重/输出对象不匹配 write=%0d addr=%08x",
                           bulk_cmd_write, bulk_cmd_addr);
            end
            if (bulk_done_valid && bulk_done_ready && current_bulk_write) begin
                output_bulk_done_count <= output_bulk_done_count + 1;
                if ((output_bulk_done_count == 511) &&
                    (output_byte_count == FIRST_TILE_BYTES))
                    engine_abort <= 1'b1;
            end

            if (m_axi_arvalid && !m_axi_arready) ar_stall_count <= ar_stall_count + 1;
            if (m_axi_awvalid && !m_axi_awready) aw_stall_count <= aw_stall_count + 1;
            if (m_axi_wvalid && !m_axi_wready) w_stall_count <= w_stall_count + 1;
            if (rd_active && !rd_valid_reg) r_delay_count <= r_delay_count + 1;
            if (write_checked && !bvalid_reg) b_delay_count <= b_delay_count + 1;

            if (m_axi_arvalid && m_axi_arready) begin
                if (!fixtures_loaded)
                    $fatal(1, "fixture尚未加载就接受了物理读地址");
                if (rd_active || m_axi_arid != 0 || m_axi_arburst != 2'b01 ||
                    m_axi_arlen > 15 ||
                    !((m_axi_arsize == 3'd3) ||
                      ((m_axi_arsize == 3'd0) && (m_axi_arlen == 0))))
                    $fatal(1, "物理AR属性/单outstanding约束错误");
                if (m_axi_arsize == 3'd3) begin
                    if (m_axi_araddr[2:0] != 0 ||
                        (m_axi_araddr[11:0] + ((m_axi_arlen + 1) * 8)) > 4096)
                        $fatal(1, "SIZE3读突发未对齐或越过4KiB");
                    ar_size3_count <= ar_size3_count + 1;
                end else begin
                    if (m_axi_arlen != 0)
                        $fatal(1, "旧SIZE0读事务必须为单拍");
                    ar_size0_count <= ar_size0_count + 1;
                end
                ar_count <= ar_count + 1;
                rd_active <= 1'b1;
                rd_address <= m_axi_araddr;
                rd_len <= m_axi_arlen;
                rd_size <= m_axi_arsize;
                rd_index <= 0;
                rd_delay <= 1 + int'(prng[4:3]);
            end

            if (rd_valid_reg && m_axi_rready) begin
                r_count <= r_count + 1;
                if (rd_index == rd_len) begin
                    rd_active <= 1'b0;
                    rd_valid_reg <= 1'b0;
                end else begin
                    rd_index <= rd_index + 1;
                    rd_valid_reg <= 1'b0;
                    rd_delay <= 1 + int'(prng[6:5]);
                end
            end else if (rd_active && !rd_valid_reg) begin
                if (rd_delay > 0)
                    rd_delay <= rd_delay - 1;
                else if (prng[8] || prng[11]) begin
                    rd_valid_reg <= 1'b1;
                    rd_data_reg <= memory_word((rd_address +
                        (rd_index * (1 << rd_size))) & 32'hffff_fff8);
                    rd_last_reg <= (rd_index == rd_len);
                end
            end

            if (m_axi_awvalid && m_axi_awready) begin
                if (aw_seen || m_axi_awid != 0 || m_axi_awburst != 2'b01 ||
                    m_axi_awsize != 3'd3 || m_axi_awaddr[2:0] != 0 ||
                    m_axi_awlen != 4'd1 ||
                    (m_axi_awaddr[11:0] + ((m_axi_awlen + 1) * 8)) > 4096)
                    $fatal(1, "首tile物理AW属性/长度/单outstanding约束错误");
                aw_seen <= 1'b1;
                aw_address <= m_axi_awaddr;
                aw_len <= m_axi_awlen;
                aw_size <= m_axi_awsize;
                aw_count <= aw_count + 1;
            end
            if (m_axi_wvalid && m_axi_wready) begin
                if (write_beat_count >= 16 || m_axi_wid != 0)
                    $fatal(1, "物理W beat越界或WID错误");
                if (!aw_seen && !(m_axi_awvalid && m_axi_awready))
                    w_before_aw_count <= w_before_aw_count + 1;
                saved_wdata[write_beat_count] <= m_axi_wdata;
                saved_wstrb[write_beat_count] <= m_axi_wstrb;
                saved_wlast[write_beat_count] <= m_axi_wlast;
                saved_wid[write_beat_count] <= m_axi_wid;
                write_beat_count <= write_beat_count + 1;
                axi_w_count <= axi_w_count + 1;
            end

            if (aw_seen && !write_checked &&
                (write_beat_count == (aw_len + 1))) begin
                check_write_burst();
                write_checked <= 1'b1;
                b_delay <= 1 + int'(prng[10:9]);
            end
            if (write_checked && !bvalid_reg) begin
                if (b_delay > 0)
                    b_delay <= b_delay - 1;
                else if (prng[12] || prng[14])
                    bvalid_reg <= 1'b1;
            end
            if (bvalid_reg && m_axi_bready) begin
                b_count <= b_count + 1;
                bvalid_reg <= 1'b0;
                aw_seen <= 1'b0;
                write_checked <= 1'b0;
                write_beat_count <= 0;
            end
        end
    end

    initial begin
        if (dut.LANE_COUNT != 32) $fatal(1, "DUT没有启用32 lane");
        fd = $fopen("D:\\FPGA_Competition\\report\\evidence\\S2A-T66\\tile01\\fixture\\sample0_input_chw_int8.bin", "rb");
        if (fd == 0) $fatal(1, "T66输入fixture无法打开");
        for (index = 0; index < INPUT_BYTES; index = index + 1) begin
            byte_value = $fgetc(fd);
            if (byte_value < 0) $fatal(1, "T66输入fixture长度不足");
            input_fixture[index] = byte_value[7:0];
        end
        if ($fgetc(fd) >= 0) $fatal(1, "T66输入fixture长度超出预期");
        $fclose(fd);

        fd = $fopen("D:\\FPGA_Competition\\report\\evidence\\S2A-T66\\tile01\\fixture\\sample0_layer0_gf8_weights.bin", "rb");
        if (fd == 0) $fatal(1, "T66权重fixture无法打开");
        for (index = 0; index < WEIGHT_BYTES; index = index + 1) begin
            byte_value = $fgetc(fd);
            if (byte_value < 0) $fatal(1, "T66权重fixture长度不足");
            weight_fixture[index] = byte_value[7:0];
        end
        if ($fgetc(fd) >= 0) $fatal(1, "T66权重fixture长度超出预期");
        $fclose(fd);

        fd = $fopen("D:\\FPGA_Competition\\report\\evidence\\S2A-T66\\tile01\\fixture\\sample0_layer0_expected_nchw_int8.bin", "rb");
        if (fd == 0) $fatal(1, "T66 golden无法打开");
        for (index = 0; index < OUTPUT_BYTES; index = index + 1) begin
            byte_value = $fgetc(fd);
            if (byte_value < 0) $fatal(1, "T66 golden长度不足");
            output_golden[index] = byte_value[7:0];
        end
        if ($fgetc(fd) >= 0) $fatal(1, "T66 golden长度超出预期");
        $fclose(fd);
        fixtures_loaded = 1'b1;

        repeat (3) @(negedge clk);
        hard_reset = 1'b0;
        @(negedge clk);
        if (!start_ready) $fatal(1, "32 lane engine未就绪");
        start_cycle = cycle_count;
        start_valid = 1'b1;
        @(negedge clk);
        start_valid = 1'b0;

        wait (output_bulk_done_count == 512);
        @(negedge clk);
        if (!ledger_empty || protocol_isolated || recovery_required || first_fault_valid)
            $fatal(1, "首tile最后bulk完成后全局AXI账本未安全归空");
        if (output_byte_count != FIRST_TILE_BYTES)
            $fatal(1, "物理W只覆盖%0d个首tile golden字节", output_byte_count);
        for (index = 0; index < FIRST_TILE_BYTES; index = index + 1)
            if (!output_seen[index]) $fatal(1, "物理W缺少首tile golden字节 index=%0d", index);

        if (bulk_command_count != 615 || feature_command_count != 96 ||
            weight_command_count != 7 || output_command_count != 512 ||
            feature_command_bytes != 3072 || weight_command_bytes != 856 ||
            output_command_bytes != 8192 || legacy_request_count != 8 ||
            legacy_weight_read_count != 8)
            $fatal(1, "engine命令计数不符 bulk=%0d feature=%0d weight=%0d output=%0d legacy=%0d",
                   bulk_command_count, feature_command_count, weight_command_count,
                   output_command_count, legacy_request_count);
        if (ar_count != 111 || ar_size3_count != 103 || ar_size0_count != 8 ||
            aw_count != 512 || axi_w_count != 1024 || r_count != 499 ||
            b_count != 512 || (r_count + axi_w_count) != 1523)
            $fatal(1, "物理AXI计数不符 AR=%0d(size3=%0d,size0=%0d) AW=%0d W=%0d R=%0d B=%0d",
                   ar_count, ar_size3_count, ar_size0_count, aw_count,
                   axi_w_count, r_count, b_count);
        if (w_before_aw_count == 0 || aw_stall_count == 0 || w_stall_count == 0 ||
            ar_stall_count == 0 || r_delay_count == 0 || b_delay_count == 0)
            $fatal(1, "固定随机背压/AXI3 W先于AW覆盖不足");
        if (bulk_cmd_valid || backend_req_valid || m_axi_arvalid || m_axi_awvalid ||
            m_axi_wvalid || m_axi_rvalid || m_axi_bvalid)
            $fatal(1, "停止首tile时仍有活动物理事务或内部请求");

        $display("PASS RTL10 ENGINE_AXI first_tile cycles=%0d bulk_cmd=%0d legacy=%0d AR=%0d AW=%0d W=%0d R=%0d B=%0d AXI_data_beats=%0d output_golden_bytes=%0d seed=32'h32B0_1C08",
                 cycle_count - start_cycle, bulk_command_count, legacy_request_count,
                 ar_count, aw_count, axi_w_count, r_count, b_count,
                 r_count + axi_w_count, output_byte_count);
        $finish;
    end
endmodule
