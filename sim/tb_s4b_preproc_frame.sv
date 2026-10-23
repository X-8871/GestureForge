`timescale 1ns/1ps

module tb_s4b_preproc_frame;
    localparam integer MEMORY_WORDS = 130000;
    localparam integer SMALL_OUTPUT_BYTES = 48;
    localparam integer LARGE_PREFIX_BYTES = 88;
    // 小图DUT状态机编码：用于在首个RAW请求处安全中止。
    localparam logic [3:0] SMALL_ST_RAW_REQ = 4'd5;
    localparam logic [3:0] SMALL_ST_DRAIN = 4'd12;

    logic clk = 1'b0;
    logic rst_n = 1'b0;
    logic [63:0] memory [0:MEMORY_WORDS-1];
    logic [31:0] descriptor [0:47];
    logic [7:0] expected_small [0:SMALL_OUTPUT_BYTES-1];
    logic [7:0] expected_axis1 [0:SMALL_OUTPUT_BYTES-1];
    logic [7:0] expected_large [0:LARGE_PREFIX_BYTES-1];
    string vector_dir;
    string file_name;

    logic sm_start_valid = 1'b0;
    logic sm_start_ready;
    logic sm_abort = 1'b0;
    logic [31:0] sm_source_width = 32'd0;
    logic [31:0] sm_source_height = 32'd0;
    logic [31:0] sm_stride = 32'd0;
    logic [31:0] sm_logical = 32'd0;
    logic [31:0] sm_storage = 32'd0;
    logic [31:0] sm_raw_capacity = 32'd0;
    logic [31:0] sm_resized_width = 32'd0;
    logic [31:0] sm_resized_height = 32'd0;
    logic [31:0] sm_pad_left = 32'd0;
    logic [31:0] sm_pad_top = 32'd0;
    logic [31:0] sm_raw_base = 32'd0;
    logic [31:0] sm_xgeom_base = 32'd0;
    logic [31:0] sm_ygeom_base = 32'd0;
    logic [31:0] sm_tensor_base = 32'd0;
    logic [31:0] sm_session = 32'd0;
    logic [31:0] sm_frame = 32'd0;
    logic sm_busy;
    logic sm_done_valid;
    logic sm_done_ready = 1'b0;
    logic [31:0] sm_done_session;
    logic [31:0] sm_done_frame;
    logic sm_error_valid;
    logic sm_error_ready = 1'b0;
    logic [3:0] sm_error_code;
    logic [31:0] sm_error_session;
    logic [31:0] sm_error_frame;
    logic [31:0] sm_error_address;
    logic sm_fault_isolated;
    logic sm_req_valid;
    logic sm_req_ready;
    logic sm_req_write;
    logic [31:0] sm_req_addr;
    logic [63:0] sm_req_wdata;
    logic [7:0] sm_req_wstrb;
    logic sm_rsp_valid;
    logic sm_rsp_ready;
    logic [63:0] sm_rsp_rdata;
    logic sm_rsp_error;

    logic lg_start_valid = 1'b0;
    logic lg_start_ready;
    logic lg_abort = 1'b0;
    logic [31:0] lg_source_width = 32'd0;
    logic [31:0] lg_source_height = 32'd0;
    logic [31:0] lg_stride = 32'd0;
    logic [31:0] lg_logical = 32'd0;
    logic [31:0] lg_storage = 32'd0;
    logic [31:0] lg_raw_capacity = 32'd0;
    logic [31:0] lg_resized_width = 32'd0;
    logic [31:0] lg_resized_height = 32'd0;
    logic [31:0] lg_pad_left = 32'd0;
    logic [31:0] lg_pad_top = 32'd0;
    logic [31:0] lg_raw_base = 32'd0;
    logic [31:0] lg_xgeom_base = 32'd0;
    logic [31:0] lg_ygeom_base = 32'd0;
    logic [31:0] lg_tensor_base = 32'd0;
    logic [31:0] lg_session = 32'd0;
    logic [31:0] lg_frame = 32'd0;
    logic lg_busy;
    logic lg_done_valid;
    logic lg_done_ready = 1'b0;
    logic [31:0] lg_done_session;
    logic [31:0] lg_done_frame;
    logic lg_error_valid;
    logic lg_error_ready = 1'b0;
    logic [3:0] lg_error_code;
    logic [31:0] lg_error_session;
    logic [31:0] lg_error_frame;
    logic [31:0] lg_error_address;
    logic lg_fault_isolated;
    logic lg_req_valid;
    logic lg_req_ready;
    logic lg_req_write;
    logic [31:0] lg_req_addr;
    logic [63:0] lg_req_wdata;
    logic [7:0] lg_req_wstrb;
    logic lg_rsp_valid;
    logic lg_rsp_ready;
    logic [63:0] lg_rsp_rdata;
    logic lg_rsp_error;

    logic inject_unsolicited = 1'b0;
    logic inject_next_raw_error = 1'b0;
    logic inject_next_write_error = 1'b0;
    logic raw_error_consumed_q = 1'b0;
    logic write_error_consumed_q = 1'b0;
    logic [31:0] lfsr_q = 32'h20261023;
    logic memory_busy_q = 1'b0;
    logic memory_rsp_valid_q = 1'b0;
    logic memory_owner_large_q = 1'b0;
    logic memory_write_q = 1'b0;
    logic memory_error_q = 1'b0;
    logic [31:0] memory_addr_q = 32'd0;
    logic [63:0] memory_wdata_q = 64'd0;
    logic [7:0] memory_wstrb_q = 8'd0;
    logic [63:0] memory_rdata_q = 64'd0;
    integer memory_delay_q = 0;
    integer small_request_count = 0;
    integer small_geom_read_count = 0;
    integer small_raw_read_count = 0;
    integer small_write_count = 0;
    integer small_write_ack_count = 0;
    integer large_request_count = 0;
    integer large_geom_read_count = 0;
    integer large_raw_read_count = 0;
    integer large_write_count = 0;
    integer large_write_ack_count = 0;
    integer accepted_small_start_count = 0;
    integer cycle_count = 0;
    logic sm_stall_q = 1'b0;
    logic lg_stall_q = 1'b0;
    logic [104:0] sm_stalled_request_q = 105'd0;
    logic [104:0] lg_stalled_request_q = 105'd0;
    logic memory_ready;
    logic memory_rsp_ready_selected;
    logic memory_rsp_fire;
    logic small_request_fire;
    logic large_request_fire;
    integer timeout_count;
    integer index;
    integer saved_requests;
    integer saved_raw_reads;
    integer saved_writes;
    logic [3:0] held_error_code;
    logic [31:0] held_error_address;
    logic [31:0] held_error_session;
    logic [31:0] held_error_frame;
    logic [31:0] held_done_session;
    logic [31:0] held_done_frame;
    logic [31:0] config_base;
    logic [31:0] config_tensor_override;

    always #5 clk = ~clk;
    always @(posedge clk)
        cycle_count <= cycle_count + 1;

    s4b_preproc_frame #(.OUT_WIDTH(32'd4), .OUT_HEIGHT(32'd4)) small_dut (
        .clk(clk), .rst_n(rst_n), .start_valid(sm_start_valid), .start_ready(sm_start_ready),
        .abort(sm_abort), .source_width(sm_source_width), .source_height(sm_source_height),
        .stride_bytes(sm_stride), .logical_bytes(sm_logical), .storage_bytes(sm_storage),
        .raw_capacity_bytes(sm_raw_capacity), .resized_width(sm_resized_width),
        .resized_height(sm_resized_height), .pad_left(sm_pad_left), .pad_top(sm_pad_top),
        .raw_base(sm_raw_base), .xgeom_base(sm_xgeom_base), .ygeom_base(sm_ygeom_base),
        .tensor_base(sm_tensor_base), .session_id(sm_session), .frame_id(sm_frame),
        .busy(sm_busy), .done_valid(sm_done_valid), .done_ready(sm_done_ready),
        .done_session_id(sm_done_session), .done_frame_id(sm_done_frame),
        .error_valid(sm_error_valid), .error_ready(sm_error_ready), .error_code(sm_error_code),
        .error_session_id(sm_error_session), .error_frame_id(sm_error_frame),
        .error_address(sm_error_address), .fault_isolated(sm_fault_isolated),
        .mem_req_valid(sm_req_valid), .mem_req_ready(sm_req_ready), .mem_req_write(sm_req_write),
        .mem_req_addr(sm_req_addr), .mem_req_wdata(sm_req_wdata), .mem_req_wstrb(sm_req_wstrb),
        .mem_rsp_valid(sm_rsp_valid), .mem_rsp_ready(sm_rsp_ready),
        .mem_rsp_rdata(sm_rsp_rdata), .mem_rsp_error(sm_rsp_error)
    );

    s4b_preproc_frame large_dut (
        .clk(clk), .rst_n(rst_n), .start_valid(lg_start_valid), .start_ready(lg_start_ready),
        .abort(lg_abort), .source_width(lg_source_width), .source_height(lg_source_height),
        .stride_bytes(lg_stride), .logical_bytes(lg_logical), .storage_bytes(lg_storage),
        .raw_capacity_bytes(lg_raw_capacity), .resized_width(lg_resized_width),
        .resized_height(lg_resized_height), .pad_left(lg_pad_left), .pad_top(lg_pad_top),
        .raw_base(lg_raw_base), .xgeom_base(lg_xgeom_base), .ygeom_base(lg_ygeom_base),
        .tensor_base(lg_tensor_base), .session_id(lg_session), .frame_id(lg_frame),
        .busy(lg_busy), .done_valid(lg_done_valid), .done_ready(lg_done_ready),
        .done_session_id(lg_done_session), .done_frame_id(lg_done_frame),
        .error_valid(lg_error_valid), .error_ready(lg_error_ready), .error_code(lg_error_code),
        .error_session_id(lg_error_session), .error_frame_id(lg_error_frame),
        .error_address(lg_error_address), .fault_isolated(lg_fault_isolated),
        .mem_req_valid(lg_req_valid), .mem_req_ready(lg_req_ready), .mem_req_write(lg_req_write),
        .mem_req_addr(lg_req_addr), .mem_req_wdata(lg_req_wdata), .mem_req_wstrb(lg_req_wstrb),
        .mem_rsp_valid(lg_rsp_valid), .mem_rsp_ready(lg_rsp_ready),
        .mem_rsp_rdata(lg_rsp_rdata), .mem_rsp_error(lg_rsp_error)
    );

    always_comb begin : memory_interface_mux
        memory_ready = !memory_busy_q && !memory_rsp_valid_q && lfsr_q[0];
        sm_req_ready = memory_ready && !lg_req_valid;
        lg_req_ready = memory_ready && !sm_req_valid;
        sm_rsp_valid = (memory_rsp_valid_q && !memory_owner_large_q) || inject_unsolicited;
        lg_rsp_valid = memory_rsp_valid_q && memory_owner_large_q;
        sm_rsp_rdata = inject_unsolicited ? 64'h0123456789abcdef : memory_rdata_q;
        lg_rsp_rdata = memory_rdata_q;
        sm_rsp_error = memory_error_q && !memory_owner_large_q;
        lg_rsp_error = memory_error_q && memory_owner_large_q;
        memory_rsp_ready_selected = memory_owner_large_q ? lg_rsp_ready : sm_rsp_ready;
        memory_rsp_fire = memory_rsp_valid_q && memory_rsp_ready_selected;
        small_request_fire = sm_req_valid && sm_req_ready;
        large_request_fire = lg_req_valid && lg_req_ready;
    end

    always_ff @(posedge clk) begin : memory_model
        integer word_index;
        integer lane_index;
        if (!rst_n) begin
            lfsr_q <= 32'h20261023;
            memory_busy_q <= 1'b0;
            memory_rsp_valid_q <= 1'b0;
            memory_owner_large_q <= 1'b0;
            memory_write_q <= 1'b0;
            memory_error_q <= 1'b0;
            memory_addr_q <= 32'd0;
            memory_wdata_q <= 64'd0;
            memory_wstrb_q <= 8'd0;
            memory_rdata_q <= 64'd0;
            memory_delay_q <= 0;
            raw_error_consumed_q <= 1'b0;
            write_error_consumed_q <= 1'b0;
            small_request_count <= 0;
            small_geom_read_count <= 0;
            small_raw_read_count <= 0;
            small_write_count <= 0;
            small_write_ack_count <= 0;
            large_request_count <= 0;
            large_geom_read_count <= 0;
            large_raw_read_count <= 0;
            large_write_count <= 0;
            large_write_ack_count <= 0;
        end else begin
            lfsr_q <= {lfsr_q[30:0], lfsr_q[31] ^ lfsr_q[21] ^ lfsr_q[1] ^ lfsr_q[0]};
            if (!inject_next_raw_error)
                raw_error_consumed_q <= 1'b0;
            if (!inject_next_write_error)
                write_error_consumed_q <= 1'b0;
            if ((sm_req_valid && sm_req_ready) || (lg_req_valid && lg_req_ready)) begin
                if (small_request_fire) begin
                    memory_owner_large_q <= 1'b0;
                    memory_addr_q <= sm_req_addr;
                    memory_write_q <= sm_req_write;
                    memory_wdata_q <= sm_req_wdata;
                    memory_wstrb_q <= sm_req_wstrb;
                    small_request_count <= small_request_count + 1;
                    if (sm_req_write) begin
                        small_write_count <= small_write_count + 1;
                        if (sm_req_wstrb != 8'hff || sm_req_addr[2:0] != 3'd0)
                            $fatal(1, "小图tensor写未完整对齐或WSTRB不全");
                    end else if ((sm_req_addr >= 32'h00002000 && sm_req_addr < 32'h00002060) ||
                                 (sm_req_addr >= 32'h00003000 && sm_req_addr < 32'h00003060) ||
                                 (sm_req_addr >= 32'h00009000 && sm_req_addr < 32'h00009060) ||
                                 (sm_req_addr >= 32'h0000a000 && sm_req_addr < 32'h0000a060)) begin
                        small_geom_read_count <= small_geom_read_count + 1;
                    end else begin
                        small_raw_read_count <= small_raw_read_count + 1;
                    end
                end else begin
                    memory_owner_large_q <= 1'b1;
                    memory_addr_q <= lg_req_addr;
                    memory_write_q <= lg_req_write;
                    memory_wdata_q <= lg_req_wdata;
                    memory_wstrb_q <= lg_req_wstrb;
                    large_request_count <= large_request_count + 1;
                    if (lg_req_write) begin
                        large_write_count <= large_write_count + 1;
                        if (lg_req_wstrb != 8'hff || lg_req_addr[2:0] != 3'd0)
                            $fatal(1, "大图tensor写未完整对齐或WSTRB不全");
                    end else if ((lg_req_addr >= 32'h00050000 && lg_req_addr < 32'h00052700) ||
                                 (lg_req_addr >= 32'h00060000 && lg_req_addr < 32'h00062700)) begin
                        large_geom_read_count <= large_geom_read_count + 1;
                    end else begin
                        large_raw_read_count <= large_raw_read_count + 1;
                    end
                end
                memory_busy_q <= 1'b1;
                memory_rsp_valid_q <= 1'b0;
                memory_delay_q <= 1 + (lfsr_q[3:2] % 4);
                memory_error_q <= 1'b0;
                if (small_request_fire && !sm_req_write && inject_next_raw_error && !raw_error_consumed_q &&
                    sm_req_addr >= 32'h00008000 && sm_req_addr < 32'h00008018) begin
                    memory_error_q <= 1'b1;
                    raw_error_consumed_q <= 1'b1;
                end else if (small_request_fire && sm_req_write && inject_next_write_error && !write_error_consumed_q) begin
                    memory_error_q <= 1'b1;
                    write_error_consumed_q <= 1'b1;
                end
                if (small_request_fire && sm_req_write && !(inject_next_write_error && !write_error_consumed_q)) begin
                    word_index = sm_req_addr >> 3;
                    if (word_index >= MEMORY_WORDS)
                        $fatal(1, "小图写地址越出仿真DDR");
                    for (lane_index = 0; lane_index < 8; lane_index = lane_index + 1)
                        if (sm_req_wstrb[lane_index])
                            memory[word_index][lane_index*8 +: 8] <= sm_req_wdata[lane_index*8 +: 8];
                end
                if (large_request_fire && lg_req_write) begin
                    word_index = lg_req_addr >> 3;
                    if (word_index >= MEMORY_WORDS)
                        $fatal(1, "大图写地址越出仿真DDR");
                    for (lane_index = 0; lane_index < 8; lane_index = lane_index + 1)
                        if (lg_req_wstrb[lane_index])
                            memory[word_index][lane_index*8 +: 8] <= lg_req_wdata[lane_index*8 +: 8];
                end
            end else if (memory_busy_q && !memory_rsp_valid_q) begin
                if (memory_delay_q > 0) begin
                    memory_delay_q <= memory_delay_q - 1;
                end else begin
                    memory_rsp_valid_q <= 1'b1;
                    word_index = memory_addr_q >> 3;
                    if (word_index >= MEMORY_WORDS) begin
                        memory_error_q <= 1'b1;
                        memory_rdata_q <= 64'd0;
                    end else if (memory_error_q) begin
                        memory_rdata_q <= 64'd0;
                    end else begin
                        memory_rdata_q <= memory[memory_addr_q >> 3];
                    end
                end
            end
            if (memory_rsp_fire) begin
                memory_rsp_valid_q <= 1'b0;
                memory_busy_q <= 1'b0;
                if (memory_write_q && memory_owner_large_q)
                    large_write_ack_count <= large_write_ack_count + 1;
                if (memory_write_q && !memory_owner_large_q)
                    small_write_ack_count <= small_write_ack_count + 1;
            end
        end
    end

    always_ff @(posedge clk) begin : protocol_monitors
        if (!rst_n) begin
            sm_stall_q <= 1'b0;
            lg_stall_q <= 1'b0;
            sm_stalled_request_q <= 105'd0;
            lg_stalled_request_q <= 105'd0;
            accepted_small_start_count <= 0;
        end else begin
            if (sm_start_valid && sm_start_ready)
                accepted_small_start_count <= accepted_small_start_count + 1;
            if (sm_stall_q && (!sm_req_valid || {sm_req_write, sm_req_addr, sm_req_wdata, sm_req_wstrb} !== sm_stalled_request_q))
                $fatal(1, "小图请求在READY背压期间改变");
            if (lg_stall_q && (!lg_req_valid || {lg_req_write, lg_req_addr, lg_req_wdata, lg_req_wstrb} !== lg_stalled_request_q))
                $fatal(1, "大图请求在READY背压期间改变");
            sm_stall_q <= sm_req_valid && !sm_req_ready;
            lg_stall_q <= lg_req_valid && !lg_req_ready;
            if (sm_req_valid && !sm_req_ready)
                sm_stalled_request_q <= {sm_req_write, sm_req_addr, sm_req_wdata, sm_req_wstrb};
            if (lg_req_valid && !lg_req_ready)
                lg_stalled_request_q <= {lg_req_write, lg_req_addr, lg_req_wdata, lg_req_wstrb};
        end
    end

    task automatic load_small_descriptor(input integer base_index, input logic overlap_tensor);
        begin
            sm_source_width = descriptor[base_index + 0];
            sm_source_height = descriptor[base_index + 1];
            sm_stride = descriptor[base_index + 2];
            sm_logical = descriptor[base_index + 3];
            sm_storage = descriptor[base_index + 4];
            sm_raw_capacity = descriptor[base_index + 5];
            sm_resized_width = descriptor[base_index + 6];
            sm_resized_height = descriptor[base_index + 7];
            sm_pad_left = descriptor[base_index + 8];
            sm_pad_top = descriptor[base_index + 9];
            sm_raw_base = descriptor[base_index + 10];
            sm_xgeom_base = descriptor[base_index + 11];
            sm_ygeom_base = descriptor[base_index + 12];
            sm_tensor_base = overlap_tensor ? descriptor[base_index + 10] : descriptor[base_index + 13];
            sm_session = descriptor[base_index + 14];
            sm_frame = descriptor[base_index + 15];
        end
    endtask

    task automatic start_small(input integer base_index, input logic overlap_tensor);
        begin
            @(negedge clk);
            while (!sm_start_ready)
                @(negedge clk);
            load_small_descriptor(base_index, overlap_tensor);
            sm_start_valid = 1'b1;
            @(posedge clk);
            #1;
            @(negedge clk);
            sm_start_valid = 1'b0;
        end
    endtask

    task automatic wait_small_error(input logic [3:0] wanted_code, input logic sticky);
        integer local_wait;
        begin
            local_wait = 0;
            while (!sm_error_valid && local_wait < 5000) begin
                @(negedge clk);
                local_wait = local_wait + 1;
            end
            if (!sm_error_valid)
                $fatal(1, "小图错误输出超时，期望code=%0d", wanted_code);
            if (sm_error_code !== wanted_code)
                $fatal(1, "小图错误码不符 got=%0d expected=%0d", sm_error_code, wanted_code);
            held_error_code = sm_error_code;
            held_error_address = sm_error_address;
            held_error_session = sm_error_session;
            held_error_frame = sm_error_frame;
            repeat (3) begin
                @(negedge clk);
                if (!sm_error_valid || sm_error_code !== held_error_code ||
                    sm_error_address !== held_error_address || sm_error_session !== held_error_session ||
                    sm_error_frame !== held_error_frame)
                    $fatal(1, "小图错误元数据在READY背压期间改变");
            end
            sm_error_ready = 1'b1;
            @(posedge clk);
            #1;
            @(negedge clk);
            sm_error_ready = 1'b0;
            if (sticky) begin
                if (!sm_fault_isolated || sm_start_ready)
                    $fatal(1, "code9错误握手后未保持sticky隔离");
            end else if (sm_busy || !sm_start_ready) begin
                $fatal(1, "普通错误握手后未回到idle");
            end
        end
    endtask

    task automatic exercise_weight_domain(
        input logic axis_y,
        input logic [63:0] replacement_weight,
        input logic expect_supported,
        input integer expected_geometry_reads
    );
        integer local_wait;
        integer requests_before;
        integer geometry_before;
        integer raw_before;
        integer writes_before;
        integer word_index;
        logic [31:0] table_base;
        logic [63:0] saved_weight;
        begin
            table_base = axis_y ? descriptor[12] : descriptor[11];
            word_index = (table_base >> 3) + 1;
            saved_weight = memory[word_index];
            memory[word_index] = replacement_weight;
            requests_before = small_request_count;
            geometry_before = small_geom_read_count;
            raw_before = small_raw_read_count;
            writes_before = small_write_count;

            start_small(0, 1'b0);
            local_wait = 0;
            if (expect_supported) begin
                while (small_dut.state_q !== SMALL_ST_RAW_REQ && !sm_error_valid && local_wait < 5000) begin
                    @(negedge clk);
                    local_wait = local_wait + 1;
                end
                if (sm_error_valid || small_dut.state_q !== SMALL_ST_RAW_REQ)
                    $fatal(1, "支持域权重被拒绝或表扫描未完成 axis_y=%0d weight=0x%016x state=%0d code=%0d",
                           axis_y, replacement_weight, small_dut.state_q, sm_error_code);
                if (!sm_req_valid || sm_req_write || sm_req_addr !== descriptor[10] || small_dut.mem_pending_q)
                    $fatal(1, "支持域权重扫描后未到达首个RAW请求 axis_y=%0d valid=%0d write=%0d addr=0x%08x pending=%0d",
                           axis_y, sm_req_valid, sm_req_write, sm_req_addr, small_dut.mem_pending_q);
                sm_abort = 1'b1;
                local_wait = 0;
                while (small_dut.state_q !== SMALL_ST_DRAIN && local_wait < 5000) begin
                    @(negedge clk);
                    local_wait = local_wait + 1;
                end
                if (small_dut.state_q !== SMALL_ST_DRAIN || small_dut.mem_pending_q)
                    $fatal(1, "支持域权重样例未在RAW响应后安全排空 state=%0d pending=%0d",
                           small_dut.state_q, small_dut.mem_pending_q);
                sm_abort = 1'b0;
                if (small_request_count - requests_before != 25 ||
                    small_geom_read_count - geometry_before != 24 ||
                    small_raw_read_count - raw_before != 1 || small_write_count != writes_before ||
                    small_dut.pixel_busy || small_dut.pixel_out_valid || small_dut.pixel_error_valid)
                    $fatal(1, "支持域权重样例请求/像素边界异常 axis_y=%0d weight=0x%016x req=%0d geom=%0d raw=%0d writes=%0d pixel=%0d/%0d/%0d",
                           axis_y, replacement_weight, small_request_count - requests_before,
                           small_geom_read_count - geometry_before, small_raw_read_count - raw_before,
                           small_write_count - writes_before, small_dut.pixel_busy,
                           small_dut.pixel_out_valid, small_dut.pixel_error_valid);
                wait_small_error(4'd8, 1'b0);
            end else begin
                while (!sm_error_valid && local_wait < 5000) begin
                    @(negedge clk);
                    local_wait = local_wait + 1;
                end
                if (!sm_error_valid || sm_error_code !== 4'd4)
                    $fatal(1, "不支持域权重未返回ERR_GEOMETRY axis_y=%0d weight=0x%016x valid=%0d code=%0d",
                           axis_y, replacement_weight, sm_error_valid, sm_error_code);
                if (sm_error_address !== table_base + 32'd16 ||
                    sm_error_session !== descriptor[14] || sm_error_frame !== descriptor[15])
                    $fatal(1, "权重域错误元数据不符 axis_y=%0d addr=0x%08x expected=0x%08x session=0x%08x frame=0x%08x",
                           axis_y, sm_error_address, table_base + 32'd16, sm_error_session, sm_error_frame);
                if (small_request_count - requests_before != expected_geometry_reads ||
                    small_geom_read_count - geometry_before != expected_geometry_reads ||
                    small_raw_read_count != raw_before || small_write_count != writes_before ||
                    small_dut.pixel_busy || small_dut.pixel_out_valid || small_dut.pixel_error_valid)
                    $fatal(1, "不支持域权重拒绝前产生RAW/TENSOR或像素活动 axis_y=%0d weight=0x%016x req=%0d geom=%0d raw=%0d writes=%0d pixel=%0d/%0d/%0d",
                           axis_y, replacement_weight, small_request_count - requests_before,
                           small_geom_read_count - geometry_before, small_raw_read_count - raw_before,
                           small_write_count - writes_before, small_dut.pixel_busy,
                           small_dut.pixel_out_valid, small_dut.pixel_error_valid);
                wait_small_error(4'd4, 1'b0);
            end
            memory[word_index] = saved_weight;
        end
    endtask

    task automatic wait_small_done(input integer expected_case, input integer expected_writes);
        integer local_wait;
        integer byte_value;
        logic [31:0] expected_session;
        logic [31:0] expected_frame;
        begin
            local_wait = 0;
            while (!sm_done_valid && !sm_error_valid && local_wait < 50000) begin
                @(negedge clk);
                local_wait = local_wait + 1;
            end
            if (sm_error_valid)
                $fatal(1, "小图作业在done前返回错误 case=%0d state=%0d pending=%0d req=%0d/%0d rsp=%0d/%0d done=%0d error=%0d code=%0d addr=0x%08x fault=%0d pixel_busy=%0d pixel_out=%0d pixel_error=%0d pixel_error_code=%0d linear=%0d xy=(%0d,%0d) channel=%0d writes=%0d",
                       expected_case, small_dut.state_q, small_dut.mem_pending_q, sm_req_valid, sm_req_ready,
                       sm_rsp_valid, sm_rsp_ready, sm_done_valid, sm_error_valid, sm_error_code,
                       sm_error_address, sm_fault_isolated, small_dut.pixel_busy, small_dut.pixel_out_valid,
                       small_dut.pixel_error_valid, small_dut.pixel_error_code, small_dut.linear_index_q,
                       small_dut.output_x_q, small_dut.output_y_q, small_dut.channel_q, small_write_count);
            if (!sm_done_valid)
                $fatal(1, "小图完成输出超时 case=%0d state=%0d pending=%0d req=%0d/%0d rsp=%0d/%0d done=%0d error=%0d code=%0d addr=0x%08x fault=%0d pixel_busy=%0d pixel_out=%0d pixel_error=%0d pixel_error_code=%0d linear=%0d xy=(%0d,%0d) channel=%0d writes=%0d",
                       expected_case, small_dut.state_q, small_dut.mem_pending_q, sm_req_valid, sm_req_ready,
                       sm_rsp_valid, sm_rsp_ready, sm_done_valid, sm_error_valid, sm_error_code,
                       sm_error_address, sm_fault_isolated, small_dut.pixel_busy, small_dut.pixel_out_valid,
                       small_dut.pixel_error_valid, small_dut.pixel_error_code, small_dut.linear_index_q,
                       small_dut.output_x_q, small_dut.output_y_q, small_dut.channel_q, small_write_count);
            expected_session = descriptor[expected_case + 14];
            expected_frame = descriptor[expected_case + 15];
            held_done_session = sm_done_session;
            held_done_frame = sm_done_frame;
            if (sm_done_session !== expected_session || sm_done_frame !== expected_frame)
                $fatal(1, "小图完成session/frame错配");
            repeat (3) begin
                @(negedge clk);
                if (!sm_done_valid || sm_done_session !== held_done_session || sm_done_frame !== held_done_frame)
                    $fatal(1, "小图done元数据在READY背压期间改变");
            end
            if (expected_case == 0) begin
                for (integer output_index = 0; output_index < SMALL_OUTPUT_BYTES; output_index = output_index + 1) begin
                    byte_value = memory[(descriptor[13] + output_index) >> 3][((descriptor[13] + output_index) & 7) * 8 +: 8];
                    if (byte_value !== expected_small[output_index])
                        $fatal(1, "同尺寸CHW数据不符 index=%0d got=%0d expected=%0d", output_index, byte_value, expected_small[output_index]);
                end
            end else begin
                for (integer output_index = 0; output_index < SMALL_OUTPUT_BYTES; output_index = output_index + 1) begin
                    byte_value = memory[(descriptor[29] + output_index) >> 3][((descriptor[29] + output_index) & 7) * 8 +: 8];
                    if (byte_value !== expected_axis1[output_index])
                        $fatal(1, "axis1/letterbox CHW数据不符 index=%0d got=%0d expected=%0d", output_index, byte_value, expected_axis1[output_index]);
                end
            end
            if (small_write_ack_count != expected_writes)
                $fatal(1, "小图完整字写ACK数量不符 got=%0d expected=%0d", small_write_ack_count, expected_writes);
            sm_done_ready = 1'b1;
            @(posedge clk);
            #1;
            @(negedge clk);
            sm_done_ready = 1'b0;
        end
    endtask

    task automatic load_large_descriptor;
        begin
            lg_source_width = descriptor[32 + 0];
            lg_source_height = descriptor[32 + 1];
            lg_stride = descriptor[32 + 2];
            lg_logical = descriptor[32 + 3];
            lg_storage = descriptor[32 + 4];
            lg_raw_capacity = descriptor[32 + 5];
            lg_resized_width = descriptor[32 + 6];
            lg_resized_height = descriptor[32 + 7];
            lg_pad_left = descriptor[32 + 8];
            lg_pad_top = descriptor[32 + 9];
            lg_raw_base = descriptor[32 + 10];
            lg_xgeom_base = descriptor[32 + 11];
            lg_ygeom_base = descriptor[32 + 12];
            lg_tensor_base = descriptor[32 + 13];
            lg_session = descriptor[32 + 14];
            lg_frame = descriptor[32 + 15];
        end
    endtask

    task automatic start_large;
        begin
            @(negedge clk);
            while (!lg_start_ready)
                @(negedge clk);
            load_large_descriptor();
            lg_start_valid = 1'b1;
            @(posedge clk);
            #1;
            @(negedge clk);
            lg_start_valid = 1'b0;
        end
    endtask

    task automatic wait_large_abort;
        integer local_wait;
        integer byte_value;
        begin
            local_wait = 0;
            while (!lg_error_valid && local_wait < 20000) begin
                @(negedge clk);
                local_wait = local_wait + 1;
            end
            if (!lg_error_valid || lg_error_code !== 4'd8)
                $fatal(1, "大图controlled abort错误输出异常 code=%0d", lg_error_code);
            if (lg_error_session !== descriptor[46] || lg_error_frame !== descriptor[47])
                $fatal(1, "大图abort session/frame错配");
            held_error_code = lg_error_code;
            held_error_address = lg_error_address;
            held_error_session = lg_error_session;
            held_error_frame = lg_error_frame;
            repeat (3) begin
                @(negedge clk);
                if (!lg_error_valid || lg_error_code !== held_error_code ||
                    lg_error_address !== held_error_address || lg_error_session !== held_error_session ||
                    lg_error_frame !== held_error_frame)
                    $fatal(1, "大图abort错误元数据在READY背压期间改变");
            end
            for (integer output_index = 0; output_index < LARGE_PREFIX_BYTES; output_index = output_index + 1) begin
                byte_value = memory[(descriptor[45] + output_index) >> 3][((descriptor[45] + output_index) & 7) * 8 +: 8];
                if (byte_value !== expected_large[output_index])
                    $fatal(1, "大图prefix不符 index=%0d got=%0d expected=%0d", output_index, byte_value, expected_large[output_index]);
            end
            if (expected_large[81] !== 8'd100)
                $fatal(1, "独立D2样例未覆盖x81=100");
            if (large_write_ack_count != 11 || large_write_count != 11)
                $fatal(1, "controlled abort前大图写入数不是88B/11字");
            lg_error_ready = 1'b1;
            @(posedge clk);
            #1;
            @(negedge clk);
            lg_error_ready = 1'b0;
            if (lg_busy || !lg_start_ready)
                $fatal(1, "安全abort排空后大图单元未回到idle");
            repeat (8) @(negedge clk);
            if (large_write_count != 11 || large_write_ack_count != 11)
                $fatal(1, "abort后仍产生额外tensor写");
        end
    endtask

    initial begin : test_sequence
        integer local_wait;
        integer count_before;
        integer raw_before;
        integer write_before;
        if (!$value$plusargs("VEC_DIR=%s", vector_dir))
            $fatal(1, "缺少VEC_DIR仿真参数");
        $sformat(file_name, "%0s/memory.hex", vector_dir);
        $readmemh(file_name, memory);
        $sformat(file_name, "%0s/descriptor.hex", vector_dir);
        $readmemh(file_name, descriptor);
        $sformat(file_name, "%0s/expected_small_same.hex", vector_dir);
        $readmemh(file_name, expected_small);
        $sformat(file_name, "%0s/expected_small_axis1.hex", vector_dir);
        $readmemh(file_name, expected_axis1);
        $sformat(file_name, "%0s/expected_large_prefix88.hex", vector_dir);
        $readmemh(file_name, expected_large);

        repeat (4) @(negedge clk);
        rst_n = 1'b1;

        start_small(0, 1'b1);
        wait_small_error(4'd3, 1'b0);
        if (small_request_count != 0)
            $fatal(1, "非法重叠描述符产生了内存请求");

        start_small(0, 1'b0);
        @(negedge clk);
        sm_start_valid = 1'b1;
        sm_session = 32'hdeadbeef;
        repeat (3) begin
            @(posedge clk);
            #1;
            if (sm_start_ready)
                $fatal(1, "busy期间start_ready错误拉高");
        end
        @(negedge clk);
        sm_start_valid = 1'b0;
        wait_small_done(0, 6);
        if (small_geom_read_count != 24 || small_raw_read_count != 192)
            $fatal(1, "same-size活动几何槽/RAW读取数不符 geom=%0d raw=%0d", small_geom_read_count, small_raw_read_count);

        start_small(16, 1'b0);
        wait_small_done(16, 12);
        if (small_geom_read_count != 39 || small_raw_read_count != 240)
            $fatal(1, "axis1活动几何项/RAW读取数不符 geom=%0d raw=%0d", small_geom_read_count, small_raw_read_count);

        count_before = small_request_count;
        raw_before = small_raw_read_count;
        memory[descriptor[27] >> 3] = 64'h0000000000000001;
        start_small(16, 1'b0);
        wait_small_error(4'd4, 1'b0);
        if (small_request_count - count_before != 3 || small_raw_read_count != raw_before)
            $fatal(1, "坏几何索引未在三字检查后、RAW读之前拒绝");
        memory[descriptor[27] >> 3] = 64'd0;

        inject_next_raw_error = 1'b1;
        write_before = small_write_count;
        start_small(16, 1'b0);
        wait_small_error(4'd5, 1'b0);
        inject_next_raw_error = 1'b0;
        if (small_raw_read_count != raw_before + 1 || small_write_count != write_before)
            $fatal(1, "RAW读错误未安全排空或仍有tensor写");

        inject_next_write_error = 1'b1;
        write_before = small_write_count;
        start_small(0, 1'b0);
        wait_small_error(4'd6, 1'b0);
        inject_next_write_error = 1'b0;
        if (small_write_count != write_before + 1)
            $fatal(1, "tensor写错误样例未到达单个写响应");

        // X/Y权重域边界：正零与最小允许权重接受，低于边界的有限值拒绝。
        exercise_weight_domain(1'b0, 64'h0000000000000000, 1'b1, 24);
        exercise_weight_domain(1'b1, 64'h0000000000000000, 1'b1, 24);
        exercise_weight_domain(1'b0, 64'h3ca0000000000000, 1'b1, 24);
        exercise_weight_domain(1'b1, 64'h3ca0000000000000, 1'b1, 24);
        exercise_weight_domain(1'b0, 64'h3c9fffffffffffff, 1'b0, 3);
        exercise_weight_domain(1'b1, 64'h3c9fffffffffffff, 1'b0, 15);
        exercise_weight_domain(1'b0, 64'h39b0000000000000, 1'b0, 3);
        exercise_weight_domain(1'b1, 64'h39b0000000000000, 1'b0, 15);

        start_large();
        local_wait = 0;
        while (large_write_ack_count < 11 && local_wait < 20000) begin
            @(negedge clk);
            local_wait = local_wait + 1;
        end
        if (large_write_ack_count != 11)
            $fatal(1, "大图88字节前缀写ACK超时");
        @(negedge clk);
        lg_abort = 1'b1;
        @(posedge clk);
        #1;
        @(negedge clk);
        lg_abort = 1'b0;
        wait_large_abort();
        if (large_geom_read_count != 2013 || large_raw_read_count != 32)
            $fatal(1, "大图活动表或88B数据读取数不符 geom=%0d raw=%0d", large_geom_read_count, large_raw_read_count);

        inject_unsolicited = 1'b1;
        repeat (2) @(negedge clk);
        inject_unsolicited = 1'b0;
        wait_small_error(4'd9, 1'b1);

        rst_n = 1'b0;
        repeat (3) @(negedge clk);
        if (sm_fault_isolated || sm_busy || lg_busy)
            $fatal(1, "共同cold reset未清空idle单元");
        rst_n = 1'b1;
        repeat (4) @(negedge clk);
        $display("TEST_PASS small_cases=2 descriptor_overlap=1 geometry_fault=1 weight_accept=4 weight_reject=4 raw_error=1 write_error=1 large_prefix_bytes=88 abort=1 unsolicited_response=1 seed=20261023 cycles=%0d", cycle_count);
        $finish;
    end

    initial begin : simulation_watchdog
        #5000000;
        $fatal(1, "整帧PL仿真watchdog超时 phase=%0d cycle=%0d", small_dut.state_q, cycle_count);
    end
endmodule
