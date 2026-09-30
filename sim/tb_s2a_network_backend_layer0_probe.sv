// S2A-T64：真实启动 descriptor layer0，并探测首个卷积输出写回。
`timescale 1ns/1ps
module tb_s2a_network_backend_layer0_probe;
    import s2a_network_descriptor_pkg::*;

    localparam logic [7:0] REG_CMD = 8'h00;
    localparam logic [7:0] REG_ERROR_CODE = 8'h08;
    localparam logic [7:0] REG_TIMEOUT = 8'h28;
    localparam logic [31:0] TEST_TIMEOUT = 32'd1000000;
    localparam integer PROBE_CYCLE_LIMIT = 20000;

    logic clk = 1'b0;
    logic hard_reset = 1'b0;
    logic csr_valid = 1'b0;
    logic csr_write = 1'b0;
    logic [7:0] csr_addr = 8'd0;
    logic [31:0] csr_wdata = 32'd0;
    logic csr_ready;
    logic [31:0] csr_rdata;
    logic backend_memory_error_valid;
    logic [2:0] backend_memory_error_code;
    logic operator_result_valid;
    logic [2:0] operator_error_code;
    logic backend_start;
    logic backend_abort;
    logic busy;
    logic done;
    logic error;
    logic buffer_owner_pl;
    logic head_output_valid;
    logic mem_valid;
    logic mem_write;
    logic [31:0] mem_addr;
    logic [31:0] mem_wdata;
    logic [3:0] mem_rstrb;
    logic [3:0] mem_wstrb;
    logic mem_ready;
    logic [31:0] mem_rdata;
    logic [2:0] mem_error_code;
    integer probe_cycle;
    integer layer0_read_count;
    integer layer0_output_write_count;
    logic layer0_dispatch_seen;
    logic layer0_conv_start_seen;
    logic layer0_result_seen;
    logic layer0_output_write_seen;
    logic error_snapshot_valid;
    logic [7:0] snapshot_backend_state;
    logic [5:0] snapshot_layer_cursor;
    logic [2:0] snapshot_current_op;
    logic [31:0] snapshot_output_element_index;
    logic snapshot_descriptor_valid;
    logic snapshot_descriptor_fault;
    logic snapshot_selected_start_ready;
    logic snapshot_conv_start_valid;
    logic snapshot_conv_start_ready;
    logic snapshot_operator_result_valid;
    logic [2:0] snapshot_operator_error_code;
    logic snapshot_selected_result_valid;
    logic [2:0] snapshot_selected_result_error;
    logic [7:0] snapshot_conv_engine_state;
    logic snapshot_conv_engine_start_ready;
    logic snapshot_conv_result_valid;
    logic [2:0] snapshot_conv_result_error;
    logic snapshot_response_pending;
    logic [2:0] snapshot_response_target;
    logic [2:0] snapshot_response_error;
    logic snapshot_conv_rsp_valid;
    logic [2:0] snapshot_conv_rsp_error;
    logic snapshot_conv_req_valid;
    logic snapshot_conv_req_write;
    logic [31:0] snapshot_conv_req_addr;
    logic snapshot_mem_valid;
    logic snapshot_mem_write;
    logic [31:0] snapshot_mem_addr;
    logic [31:0] snapshot_mem_wdata;
    logic [3:0] snapshot_mem_rstrb;
    logic [3:0] snapshot_mem_wstrb;
    logic snapshot_mem_ready;
    logic [31:0] snapshot_mem_rdata;
    logic [2:0] snapshot_mem_error_code;
    logic snapshot_backend_memory_error_valid;
    logic [2:0] snapshot_backend_memory_error_code;
    logic [31:0] snapshot_csr_elapsed_cycles;
    logic snapshot_csr_busy;
    logic snapshot_csr_pl_owner;
    logic snapshot_csr_error;
    logic [2:0] snapshot_csr_error_code;

    always #5 clk = ~clk;

    // 确定性存储器：reset/CSR idle 或非 PL 所有权时不就绪，PL busy 时立即接受请求。
    assign mem_ready = !hard_reset && busy && buffer_owner_pl;
    assign mem_rdata = 32'd0;
    assign mem_error_code = 3'd0;

    s2a_control_csr u_csr (
        .clk(clk), .hard_reset(hard_reset),
        .csr_valid(csr_valid), .csr_ready(csr_ready), .csr_write(csr_write),
        .csr_addr(csr_addr), .csr_wdata(csr_wdata), .csr_rdata(csr_rdata),
        .backend_memory_error_valid(backend_memory_error_valid),
        .backend_memory_error_code(backend_memory_error_code),
        .operator_result_valid(operator_result_valid),
        .operator_error_code(operator_error_code),
        .backend_start(backend_start), .backend_abort(backend_abort),
        .busy(busy), .done(done), .error(error),
        .pl_owns_buffers(buffer_owner_pl), .head_output_valid(head_output_valid)
    );

    s2a_network_backend u_backend (
        .clk(clk), .hard_reset(hard_reset), .abort(backend_abort),
        .backend_start(backend_start), .buffer_owner_pl(buffer_owner_pl),
        .input_base_address(32'h0000_0000),
        .input_length_bytes(32'd519168),
        .weight_package_base_address(32'h0010_0000),
        .weight_package_length_bytes(32'd5903100),
        .mem_valid(mem_valid), .mem_write(mem_write), .mem_addr(mem_addr),
        .mem_wdata(mem_wdata), .mem_rstrb(mem_rstrb), .mem_wstrb(mem_wstrb),
        .mem_ready(mem_ready), .mem_rdata(mem_rdata), .mem_error_code(mem_error_code),
        .backend_memory_error_valid(backend_memory_error_valid),
        .backend_memory_error_code(backend_memory_error_code),
        .operator_result_valid(operator_result_valid),
        .operator_error_code(operator_error_code)
    );

    always @(posedge clk) begin
        if (hard_reset) begin
            layer0_read_count <= 0;
            layer0_output_write_count <= 0;
            layer0_dispatch_seen <= 1'b0;
            layer0_conv_start_seen <= 1'b0;
            layer0_result_seen <= 1'b0;
            layer0_output_write_seen <= 1'b0;
        end else begin
            if ((u_backend.state == u_backend.ST_DISPATCH) &&
                (u_backend.layer_cursor == 6'd0) &&
                (u_backend.current_op == S2A_OP_CONV)) begin
                layer0_dispatch_seen <= 1'b1;
            end
            if ((u_backend.conv_start_valid == 1'b1) &&
                (u_backend.conv_start_ready == 1'b1) &&
                (u_backend.layer_cursor == 6'd0)) begin
                layer0_conv_start_seen <= 1'b1;
            end
            if ((u_backend.state == u_backend.ST_WAIT_CONV) &&
                u_backend.conv_result_valid && u_backend.conv_result_ready &&
                (u_backend.layer_cursor == 6'd0) &&
                (u_backend.conv_result_error == 3'd0)) begin
                layer0_result_seen <= 1'b1;
            end
            if (mem_valid && mem_ready) begin
                if (!mem_write && (u_backend.layer_cursor == 6'd0)) begin
                    layer0_read_count <= layer0_read_count + 1;
                end
                if (mem_write && (u_backend.layer_cursor == 6'd0) &&
                    (mem_addr == S2A_OUTPUT_ADDRESS[0])) begin
                    layer0_output_write_count <= layer0_output_write_count + 1;
                    layer0_output_write_seen <= 1'b1;
                end
            end
        end
    end

    // 在 terminal error 被 CSR 采样前的 negedge 冻结现场，避免 abort 推进 FSM。
    always @(negedge clk) begin
        if (hard_reset) begin
            error_snapshot_valid <= 1'b0;
        end else if (!error_snapshot_valid &&
                     ((operator_result_valid && (operator_error_code != 3'd0)) ||
                      (backend_memory_error_valid &&
                       (backend_memory_error_code != 3'd0)) || error)) begin
            error_snapshot_valid <= 1'b1;
            snapshot_backend_state <= u_backend.state;
            snapshot_layer_cursor <= u_backend.layer_cursor;
            snapshot_current_op <= u_backend.current_op;
            snapshot_output_element_index <= u_backend.output_element_index;
            snapshot_descriptor_valid <= u_backend.descriptor_valid;
            snapshot_descriptor_fault <= u_backend.descriptor_fault;
            snapshot_selected_start_ready <= u_backend.selected_start_ready;
            snapshot_conv_start_valid <= u_backend.conv_start_valid;
            snapshot_conv_start_ready <= u_backend.conv_start_ready;
            snapshot_operator_result_valid <= operator_result_valid;
            snapshot_operator_error_code <= operator_error_code;
            snapshot_selected_result_valid <= u_backend.selected_result_valid;
            snapshot_selected_result_error <= u_backend.selected_result_error;
            snapshot_conv_engine_state <= u_backend.u_conv_engine.state;
            snapshot_conv_engine_start_ready <= u_backend.conv_start_ready;
            snapshot_conv_result_valid <= u_backend.conv_result_valid;
            snapshot_conv_result_error <= u_backend.conv_result_error;
            snapshot_response_pending <= u_backend.response_pending;
            snapshot_response_target <= u_backend.response_target_latched;
            snapshot_response_error <= u_backend.response_error_latched;
            snapshot_conv_rsp_valid <= u_backend.conv_rsp_valid;
            snapshot_conv_rsp_error <= u_backend.conv_rsp_error;
            snapshot_conv_req_valid <= u_backend.conv_req_valid;
            snapshot_conv_req_write <= u_backend.conv_req_write;
            snapshot_conv_req_addr <= u_backend.conv_req_addr;
            snapshot_mem_valid <= mem_valid;
            snapshot_mem_write <= mem_write;
            snapshot_mem_addr <= mem_addr;
            snapshot_mem_wdata <= mem_wdata;
            snapshot_mem_rstrb <= mem_rstrb;
            snapshot_mem_wstrb <= mem_wstrb;
            snapshot_mem_ready <= mem_ready;
            snapshot_mem_rdata <= mem_rdata;
            snapshot_mem_error_code <= mem_error_code;
            snapshot_backend_memory_error_valid <= backend_memory_error_valid;
            snapshot_backend_memory_error_code <= backend_memory_error_code;
            snapshot_csr_elapsed_cycles <= u_csr.elapsed_cycles;
            snapshot_csr_busy <= busy;
            snapshot_csr_pl_owner <= buffer_owner_pl;
            snapshot_csr_error <= error;
            snapshot_csr_error_code <= u_csr.error_code;
        end
    end

    task automatic write_csr(input logic [7:0] address,
                             input logic [31:0] value);
        begin
            @(negedge clk);
            if (!csr_ready) begin
                $fatal(1, "probe CSR write 未 ready：addr=%02h data=%08h",
                       address, value);
            end
            csr_valid = 1'b1;
            csr_write = 1'b1;
            csr_addr = address;
            csr_wdata = value;
            @(posedge clk);
            #1;
            @(negedge clk);
            csr_valid = 1'b0;
            csr_write = 1'b0;
            csr_addr = 8'd0;
            csr_wdata = 32'd0;
        end
    endtask

    task automatic report_probe_diagnostics;
        logic layer_index_match;
        logic input_count_nonzero;
        logic input_count_within_limit;
        logic output_shape_ok;
        logic source0_active;
        logic source0_shape_ok;
        logic source0_kind_ok;
        logic source0_ok;
        logic source1_active;
        logic source1_shape_ok;
        logic source1_kind_ok;
        logic source1_ok;
        logic output_ownership_ok;
        logic conv_input_count_ok;
        logic conv_mq_channel_count_ok;
        logic conv_mq_index_ok;
        logic conv_mq_range_ok;
        logic conv_activation_ok;
        logic conv_weight_layer_ok;
        logic descriptor_op_ok;
        logic descriptor_predicates_ok;
        begin
            layer_index_match =
                (S2A_LAYER_INDEX[u_backend.layer_cursor] == u_backend.layer_cursor);
            input_count_nonzero = (u_backend.current_input_count != 2'd0);
            input_count_within_limit =
                (u_backend.current_input_count <= S2A_MAX_INPUTS);
            output_shape_ok = (u_backend.output_n == 16'd1) &&
                              (u_backend.output_c != 16'd0) &&
                              (u_backend.output_h != 16'd0) &&
                              (u_backend.output_w != 16'd0) &&
                              (u_backend.output_length != 32'd0) &&
                              (u_backend.output_element_count != 64'd0);

            source0_active = (u_backend.current_input_count > 2'd0);
            source0_shape_ok = (u_backend.source_n[0] == 16'd1) &&
                               (u_backend.source_c[0] != 16'd0) &&
                               (u_backend.source_h[0] != 16'd0) &&
                               (u_backend.source_w[0] != 16'd0) &&
                               (u_backend.source_length[0] != 32'd0);
            source0_kind_ok =
                (S2A_INPUT_KIND[u_backend.layer_cursor][0] != S2A_INPUT_NETWORK) ||
                (u_backend.layer_cursor == 6'd0);
            source0_ok = !source0_active || (source0_shape_ok && source0_kind_ok);

            source1_active = (u_backend.current_input_count > 2'd1);
            source1_shape_ok = (u_backend.source_n[1] == 16'd1) &&
                               (u_backend.source_c[1] != 16'd0) &&
                               (u_backend.source_h[1] != 16'd0) &&
                               (u_backend.source_w[1] != 16'd0) &&
                               (u_backend.source_length[1] != 32'd0);
            source1_kind_ok =
                (S2A_INPUT_KIND[u_backend.layer_cursor][1] != S2A_INPUT_NETWORK);
            source1_ok = !source1_active || (source1_shape_ok && source1_kind_ok);

            output_ownership_ok = u_backend.is_alias_row ? u_backend.alias_valid :
                ((S2A_OUTPUT_MEMORY_WRITE_REQUIRED[u_backend.layer_cursor] == 1'b1) &&
                 (S2A_OUTPUT_ALLOCATION_KIND[u_backend.layer_cursor] == S2A_OUTPUT_OWNED));
            conv_input_count_ok = (u_backend.current_input_count == 2'd1);
            conv_mq_channel_count_ok =
                (S2A_T23_MQ_CHANNEL_COUNT[u_backend.layer_cursor] == u_backend.output_c);
            conv_mq_index_ok = (u_backend.mq_index < S2A_CONV_CHANNEL_COUNT);
            conv_mq_range_ok =
                (({16'd0, S2A_T23_MQ_BASE[u_backend.layer_cursor]} +
                  {16'd0, S2A_T23_MQ_CHANNEL_COUNT[u_backend.layer_cursor]}) <=
                 S2A_CONV_CHANNEL_COUNT);
            conv_activation_ok =
                (S2A_ACTIVATION[u_backend.layer_cursor] == S2A_ACT_NONE) ||
                (S2A_ACTIVATION[u_backend.layer_cursor] == S2A_ACT_LINEAR) ||
                (S2A_ACTIVATION[u_backend.layer_cursor] == S2A_ACT_LEAKY);
            conv_weight_layer_ok =
                (S2A_WEIGHT_LAYER_INDEX[u_backend.layer_cursor] ==
                 S2A_LAYER_INDEX[u_backend.layer_cursor]);

            descriptor_op_ok = 1'b0;
            if (u_backend.current_op == S2A_OP_CONV) begin
                descriptor_op_ok = conv_input_count_ok && conv_mq_channel_count_ok &&
                                   conv_mq_index_ok && conv_mq_range_ok &&
                                   conv_activation_ok && conv_weight_layer_ok;
            end else if ((u_backend.current_op == S2A_OP_MAXPOOL) ||
                         (u_backend.current_op == S2A_OP_UPSAMPLE)) begin
                descriptor_op_ok = (u_backend.current_input_count == 2'd1);
            end else if (u_backend.current_op == S2A_OP_ROUTE) begin
                descriptor_op_ok = (u_backend.current_input_count == 2'd1) ||
                                   (u_backend.current_input_count == 2'd2);
            end else if (u_backend.is_alias_row) begin
                descriptor_op_ok = 1'b1;
            end
            descriptor_predicates_ok = layer_index_match && input_count_nonzero &&
                                       input_count_within_limit && output_shape_ok &&
                                       source0_ok && source1_ok && output_ownership_ok &&
                                       descriptor_op_ok;

            $display("LAYER0_ERROR_SNAPSHOT valid=%b backend_state=%0d layer=%0d op=%0d output_element_index=%0d descriptor_valid=%b descriptor_fault=%b selected_start_ready=%b conv_start_valid=%b conv_start_ready=%b",
                     error_snapshot_valid, snapshot_backend_state,
                     snapshot_layer_cursor, snapshot_current_op,
                     snapshot_output_element_index, snapshot_descriptor_valid,
                     snapshot_descriptor_fault, snapshot_selected_start_ready,
                     snapshot_conv_start_valid, snapshot_conv_start_ready);
            $display("LAYER0_ERROR_SNAPSHOT operator_valid=%b operator_error=%0d selected_result_valid=%b selected_result_error=%0d conv_state=%0d conv_start_ready=%b conv_result_valid=%b conv_result_error=%0d",
                     snapshot_operator_result_valid, snapshot_operator_error_code,
                     snapshot_selected_result_valid, snapshot_selected_result_error,
                     snapshot_conv_engine_state, snapshot_conv_engine_start_ready,
                     snapshot_conv_result_valid, snapshot_conv_result_error);
            $display("LAYER0_ERROR_SNAPSHOT conv_req_valid=%b conv_req_write=%b conv_req_addr=%08h conv_rsp_valid=%b conv_rsp_error=%0d response_pending=%b response_target=%0d response_error=%0d",
                     snapshot_conv_req_valid, snapshot_conv_req_write,
                     snapshot_conv_req_addr, snapshot_conv_rsp_valid,
                     snapshot_conv_rsp_error, snapshot_response_pending,
                     snapshot_response_target, snapshot_response_error);
            $display("LAYER0_ERROR_SNAPSHOT mem_valid=%b mem_write=%b mem_addr=%08h mem_wdata=%08h mem_rstrb=%b mem_wstrb=%b mem_ready=%b mem_rdata=%08h mem_error=%0d backend_memory_error_valid=%b backend_memory_error=%0d",
                     snapshot_mem_valid, snapshot_mem_write, snapshot_mem_addr,
                     snapshot_mem_wdata, snapshot_mem_rstrb, snapshot_mem_wstrb,
                     snapshot_mem_ready, snapshot_mem_rdata,
                     snapshot_mem_error_code, snapshot_backend_memory_error_valid,
                     snapshot_backend_memory_error_code);
            $display("LAYER0_ERROR_SNAPSHOT csr_elapsed=%0d csr_busy=%b csr_owner=%b csr_error=%b csr_error_code=%0d",
                     snapshot_csr_elapsed_cycles, snapshot_csr_busy,
                     snapshot_csr_pl_owner, snapshot_csr_error,
                     snapshot_csr_error_code);
            $display("LAYER0_PROBE_DIAG csr busy=%b done=%b error=%b code=%0d owner=%b head=%b elapsed=%0d timeout=%0d start=%b abort=%b",
                     busy, done, error, u_csr.error_code, buffer_owner_pl,
                     head_output_valid, u_csr.elapsed_cycles,
                     u_csr.timeout_cycles, backend_start, backend_abort);
            $display("LAYER0_PROBE_DIAG backend state=%0d layer=%0d current_op=%0d descriptor_valid=%b descriptor_fault=%b selected_start_ready=%b conv_start_valid=%b conv_start_ready=%b result_valid=%b result_error=%0d",
                     u_backend.state, u_backend.layer_cursor, u_backend.current_op,
                     u_backend.descriptor_valid, u_backend.descriptor_fault,
                     u_backend.selected_start_ready, u_backend.conv_start_valid,
                     u_backend.conv_start_ready, u_backend.conv_result_valid,
                     u_backend.conv_result_error);
            $display("LAYER0_DESC index cursor=%0d rom=%0d match=%b op=%0d input_count=%0d max_inputs=%0d count_nonzero=%b count_within_limit=%b",
                     u_backend.layer_cursor, S2A_LAYER_INDEX[u_backend.layer_cursor],
                     layer_index_match, u_backend.current_op,
                     u_backend.current_input_count, S2A_MAX_INPUTS,
                     input_count_nonzero, input_count_within_limit);
            $display("LAYER0_DESC src0 kind=%0d rom_base=%08h effective_base=%08h rom_length=%0d effective_length=%0d rom_nchw=%0d,%0d,%0d,%0d effective_nchw=%0d,%0d,%0d,%0d active=%b shape_ok=%b kind_ok=%b source_ok=%b",
                     S2A_INPUT_KIND[u_backend.layer_cursor][0],
                     S2A_INPUT_ADDRESS[u_backend.layer_cursor][0],
                     u_backend.source_base[0],
                     S2A_INPUT_LENGTH_BYTES[u_backend.layer_cursor][0],
                     u_backend.source_length[0],
                     S2A_INPUT_N[u_backend.layer_cursor][0],
                     S2A_INPUT_C[u_backend.layer_cursor][0],
                     S2A_INPUT_H[u_backend.layer_cursor][0],
                     S2A_INPUT_W[u_backend.layer_cursor][0],
                     u_backend.source_n[0], u_backend.source_c[0],
                     u_backend.source_h[0], u_backend.source_w[0],
                     source0_active, source0_shape_ok, source0_kind_ok, source0_ok);
            $display("LAYER0_DESC src1 kind=%0d rom_base=%08h effective_base=%08h rom_length=%0d effective_length=%0d rom_nchw=%0d,%0d,%0d,%0d effective_nchw=%0d,%0d,%0d,%0d active=%b shape_ok=%b kind_ok=%b source_ok=%b",
                     S2A_INPUT_KIND[u_backend.layer_cursor][1],
                     S2A_INPUT_ADDRESS[u_backend.layer_cursor][1],
                     u_backend.source_base[1],
                     S2A_INPUT_LENGTH_BYTES[u_backend.layer_cursor][1],
                     u_backend.source_length[1],
                     S2A_INPUT_N[u_backend.layer_cursor][1],
                     S2A_INPUT_C[u_backend.layer_cursor][1],
                     S2A_INPUT_H[u_backend.layer_cursor][1],
                     S2A_INPUT_W[u_backend.layer_cursor][1],
                     u_backend.source_n[1], u_backend.source_c[1],
                     u_backend.source_h[1], u_backend.source_w[1],
                     source1_active, source1_shape_ok, source1_kind_ok, source1_ok);
            $display("LAYER0_DESC output rom_base=%08h effective_base=%08h rom_length=%0d effective_length=%0d rom_nchw=%0d,%0d,%0d,%0d effective_nchw=%0d,%0d,%0d,%0d allocation=%0d owned_code=%0d write_required=%b elements=%0d shape_ok=%b ownership_ok=%b alias_row=%b alias_valid=%b",
                     S2A_OUTPUT_ADDRESS[u_backend.layer_cursor], u_backend.output_base,
                     S2A_OUTPUT_LENGTH_BYTES[u_backend.layer_cursor],
                     u_backend.output_length,
                     S2A_OUTPUT_N[u_backend.layer_cursor],
                     S2A_OUTPUT_C[u_backend.layer_cursor],
                     S2A_OUTPUT_H[u_backend.layer_cursor],
                     S2A_OUTPUT_W[u_backend.layer_cursor],
                     u_backend.output_n, u_backend.output_c,
                     u_backend.output_h, u_backend.output_w,
                     S2A_OUTPUT_ALLOCATION_KIND[u_backend.layer_cursor],
                     S2A_OUTPUT_OWNED,
                     S2A_OUTPUT_MEMORY_WRITE_REQUIRED[u_backend.layer_cursor],
                     u_backend.output_element_count, output_shape_ok,
                     output_ownership_ok, u_backend.is_alias_row, u_backend.alias_valid);
            $display("LAYER0_DESC conv activation=%0d activation_ok=%b weight_layer=%0d layer_index=%0d weight_layer_ok=%b t23_mq_base=%0d t23_mq_count=%0d output_c=%0d decoded_channel=%0d mq_index=%0d conv_channel_total=%0d input_count_ok=%b mq_channel_count_ok=%b mq_index_ok=%b mq_range_ok=%b",
                     S2A_ACTIVATION[u_backend.layer_cursor], conv_activation_ok,
                     S2A_WEIGHT_LAYER_INDEX[u_backend.layer_cursor],
                     S2A_LAYER_INDEX[u_backend.layer_cursor], conv_weight_layer_ok,
                     S2A_T23_MQ_BASE[u_backend.layer_cursor],
                     S2A_T23_MQ_CHANNEL_COUNT[u_backend.layer_cursor],
                     u_backend.output_c, u_backend.decoded_channel,
                     u_backend.mq_index, S2A_CONV_CHANNEL_COUNT,
                     conv_input_count_ok, conv_mq_channel_count_ok,
                     conv_mq_index_ok, conv_mq_range_ok);
            $display("LAYER0_DESC checks output_shape=%b src0=%b src1=%b output_ownership=%b op_specific=%b reconstructed_valid=%b actual_valid=%b fault=%b",
                     output_shape_ok, source0_ok, source1_ok, output_ownership_ok,
                     descriptor_op_ok, descriptor_predicates_ok,
                     u_backend.descriptor_valid, u_backend.descriptor_fault);
            $display("LAYER0_PROBE_DIAG conv state=%0d validation_ok=%b validation_error=%0d geometry_error=%0d weight_error=%0d result_error_latched=%0d result_addr=%08h result_value=%02h",
                     u_backend.u_conv_engine.state,
                     u_backend.u_conv_engine.validation_ok,
                     u_backend.u_conv_engine.validation_error,
                     u_backend.u_conv_engine.geometry_error_code,
                     u_backend.u_conv_engine.weight_error_code,
                     u_backend.u_conv_engine.result_error_latched,
                     u_backend.conv_result_address, u_backend.conv_result_value);
            $display("LAYER0_PROBE_DIAG memory valid=%b write=%b addr=%08h wdata=%08h rstrb=%b wstrb=%b ready=%b pending=%b reads=%0d output_writes=%0d",
                     mem_valid, mem_write, mem_addr, mem_wdata, mem_rstrb,
                     mem_wstrb, mem_ready, u_backend.response_pending,
                     layer0_read_count, layer0_output_write_count);
            $display("LAYER0_PROBE_DIAG milestones dispatch=%b conv_start=%b result=%b output_write=%b operator_valid=%b operator_error=%0d memory_error_valid=%b memory_error=%0d",
                     layer0_dispatch_seen, layer0_conv_start_seen,
                     layer0_result_seen, layer0_output_write_seen,
                     operator_result_valid, operator_error_code,
                     backend_memory_error_valid, backend_memory_error_code);
        end
    endtask

    initial begin
        @(negedge clk);
        hard_reset = 1'b1;
        repeat (2) @(posedge clk);
        #1;
        @(negedge clk);
        hard_reset = 1'b0;

        write_csr(REG_TIMEOUT, TEST_TIMEOUT);
        if (u_csr.timeout_cycles != TEST_TIMEOUT) begin
            $fatal(1, "probe timeout CSR 未写入：期望=%0d 实际=%0d",
                   TEST_TIMEOUT, u_csr.timeout_cycles);
        end
        write_csr(REG_CMD, 32'd1);
        if (!backend_start || !busy || !buffer_owner_pl || error) begin
            report_probe_diagnostics();
            $fatal(1, "probe CSR 未接受合法 start");
        end

        for (probe_cycle = 0; probe_cycle < PROBE_CYCLE_LIMIT;
             probe_cycle = probe_cycle + 1) begin
            @(posedge clk);
            #1;
            if (error ||
                (layer0_dispatch_seen && layer0_conv_start_seen &&
                 layer0_result_seen && layer0_output_write_seen)) begin
                break;
            end
        end

        if (error) begin
            @(negedge clk);
            #1;
            report_probe_diagnostics();
            $fatal(1, "layer0 probe 收到 CSR/backend 错误");
        end
        if (!(layer0_dispatch_seen && layer0_conv_start_seen &&
              layer0_result_seen && layer0_output_write_seen)) begin
            report_probe_diagnostics();
            $fatal(1, "layer0 probe 有界等待未观察到 dispatch/start/result/output write：cycles=%0d limit=%0d",
                   probe_cycle, PROBE_CYCLE_LIMIT);
        end
        if (!busy || done || error || !buffer_owner_pl || (layer0_read_count == 0)) begin
            report_probe_diagnostics();
            $fatal(1, "layer0 首个输出后 CSR/存储器状态不符合预期");
        end

        $display("PASS: layer0真实CONV dispatch/start/result/write，reads=%0d writes=%0d cycles=%0d",
                 layer0_read_count, layer0_output_write_count, probe_cycle);
        $finish;
    end
endmodule
