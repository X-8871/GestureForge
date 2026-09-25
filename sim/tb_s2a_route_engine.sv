// S2A-T15：两例真实 memory smoke，描述符及独立黄金由 Python 从 G0 生成。
module tb_s2a_route_engine;
    logic  clk;
    logic  hard_reset;
    logic  abort;
    logic  start_valid;
    logic  start_ready;
    logic [31:0] source_count;
    logic [31:0] groups;
    logic [31:0] group_id;
    logic [31:0] output_channel;
    logic [31:0] output_y;
    logic [31:0] output_x;
    logic [31:0] source0_base_address;
    logic [31:0] source0_length_bytes;
    logic [31:0] source0_channels;
    logic [31:0] source0_height;
    logic [31:0] source0_width;
    logic [31:0] source0_channel_start;
    logic [31:0] source0_channel_end;
    logic [31:0] source0_multiplier_q31;
    logic [31:0] source1_base_address;
    logic [31:0] source1_length_bytes;
    logic [31:0] source1_channels;
    logic [31:0] source1_height;
    logic [31:0] source1_width;
    logic [31:0] source1_channel_start;
    logic [31:0] source1_channel_end;
    logic [31:0] source1_multiplier_q31;
    logic [31:0] output_base_address;
    logic [31:0] output_length_bytes;
    logic [31:0] output_channels;
    logic [31:0] output_height;
    logic [31:0] output_width;
    logic  backend_cancel;
    logic  backend_req_valid;
    logic  backend_req_ready;
    logic  backend_req_write;
    logic [31:0] backend_req_addr;
    logic [31:0] backend_req_wdata;
    logic [3:0] backend_req_rstrb;
    logic [3:0] backend_req_wstrb;
    logic  backend_rsp_valid;
    logic [31:0] backend_rsp_rdata;
    logic [2:0] backend_rsp_error;
    logic  result_valid;
    logic  result_ready;
    logic [31:0] result_source_index;
    logic [31:0] result_source_address;
    logic [31:0] result_output_address;
    logic [7:0] result_value;
    logic [2:0] result_error_code;
    initial clk = 0;
    always #5 clk = ~clk;
    logic readback_mode, readback_valid;
    logic master_ready, master_rsp_valid;
    logic [31:0] master_rsp_rdata;
    logic [2:0] master_rsp_error;
    logic mem_valid, mem_ready, mem_write, model_initialized;
    logic [31:0] mem_addr, mem_wdata, mem_rdata;
    logic [3:0] mem_rstrb, mem_wstrb;
    logic [2:0] mem_error_code;
    logic [31:0] expected_source, expected_output, expected_index, expected_value;
    integer fd, count, scan, watchdog, reads, writes, case_index;
    s2a_route_engine dut (
        .clk(clk),
        .hard_reset(hard_reset),
        .abort(abort),
        .start_valid(start_valid),
        .start_ready(start_ready),
        .source_count(source_count),
        .groups(groups),
        .group_id(group_id),
        .output_channel(output_channel),
        .output_y(output_y),
        .output_x(output_x),
        .source0_base_address(source0_base_address),
        .source0_length_bytes(source0_length_bytes),
        .source0_channels(source0_channels),
        .source0_height(source0_height),
        .source0_width(source0_width),
        .source0_channel_start(source0_channel_start),
        .source0_channel_end(source0_channel_end),
        .source0_multiplier_q31(source0_multiplier_q31),
        .source1_base_address(source1_base_address),
        .source1_length_bytes(source1_length_bytes),
        .source1_channels(source1_channels),
        .source1_height(source1_height),
        .source1_width(source1_width),
        .source1_channel_start(source1_channel_start),
        .source1_channel_end(source1_channel_end),
        .source1_multiplier_q31(source1_multiplier_q31),
        .output_base_address(output_base_address),
        .output_length_bytes(output_length_bytes),
        .output_channels(output_channels),
        .output_height(output_height),
        .output_width(output_width),
        .backend_cancel(backend_cancel),
        .backend_req_valid(backend_req_valid),
        .backend_req_ready(backend_req_ready),
        .backend_req_write(backend_req_write),
        .backend_req_addr(backend_req_addr),
        .backend_req_wdata(backend_req_wdata),
        .backend_req_rstrb(backend_req_rstrb),
        .backend_req_wstrb(backend_req_wstrb),
        .backend_rsp_valid(backend_rsp_valid),
        .backend_rsp_rdata(backend_rsp_rdata),
        .backend_rsp_error(backend_rsp_error),
        .result_valid(result_valid),
        .result_ready(result_ready),
        .result_source_index(result_source_index),
        .result_source_address(result_source_address),
        .result_output_address(result_output_address),
        .result_value(result_value),
        .result_error_code(result_error_code)
    );
    assign backend_req_ready = !readback_mode && master_ready;
    assign backend_rsp_valid = !readback_mode && master_rsp_valid;
    assign backend_rsp_rdata = master_rsp_rdata;
    assign backend_rsp_error = master_rsp_error;
    s2a_memory_master u_master (
        .clk(clk), .hard_reset(hard_reset), .cancel(backend_cancel),
        .buffer_owner_pl(1'b1),
        .backend_req_valid(readback_mode ? readback_valid : backend_req_valid),
        .backend_req_ready(master_ready),
        .backend_req_write(readback_mode ? 1'b0 : backend_req_write),
        .backend_req_addr(readback_mode ? {expected_output[31:2],2'b00} : backend_req_addr),
        .backend_req_wdata(readback_mode ? 32'd0 : backend_req_wdata),
        .backend_req_rstrb(readback_mode ? (4'b0001 << expected_output[1:0]) : backend_req_rstrb),
        .backend_req_wstrb(readback_mode ? 4'd0 : backend_req_wstrb),
        .backend_rsp_valid(master_rsp_valid), .backend_rsp_rdata(master_rsp_rdata),
        .backend_rsp_error(master_rsp_error), .mem_valid(mem_valid),
        .mem_ready(mem_ready), .mem_write(mem_write), .mem_addr(mem_addr),
        .mem_wdata(mem_wdata), .mem_rstrb(mem_rstrb), .mem_wstrb(mem_wstrb),
        .mem_rdata(mem_rdata), .mem_error_code(mem_error_code)
    );
    s2a_memory_model u_memory (
        .clk(clk), .reset(hard_reset), .buffer_owner_pl(1'b1),
        .fault_inject_valid(1'b0), .fault_inject_code(3'd0),
        .mem_valid(mem_valid), .mem_write(mem_write), .mem_addr(mem_addr),
        .mem_wdata(mem_wdata), .mem_rstrb(mem_rstrb), .mem_wstrb(mem_wstrb),
        .mem_ready(mem_ready), .mem_rdata(mem_rdata),
        .mem_error_code(mem_error_code), .model_initialized(model_initialized)
    );
    always @(posedge clk) begin
        if (!hard_reset && mem_valid && mem_ready) begin
            if (mem_error_code !== 0) $fatal(1, "FAIL memory error");
            if (mem_write) begin
                if (readback_mode || mem_addr !== {expected_output[31:2],2'b00} ||
                    mem_wstrb !== (4'b0001 << expected_output[1:0]) || mem_rstrb !== 0 ||
                    mem_wdata !== (expected_value << (expected_output[1:0]*8)))
                    $fatal(1, "FAIL output transaction");
                writes = writes + 1;
            end else begin
                if (mem_wstrb !== 0) $fatal(1, "FAIL read strobe");
                if (!readback_mode && (mem_addr !== {expected_source[31:2],2'b00} ||
                    mem_rstrb !== (4'b0001 << expected_source[1:0])))
                    $fatal(1, "FAIL input transaction");
                reads = reads + 1;
            end
        end
    end
    initial begin
        hard_reset=1; abort=0; start_valid=0; result_ready=0;
        readback_mode=0; readback_valid=0; reads=0; writes=0;
        fd=$fopen("route_smoke.dat", "r");
        if (!fd) $fatal(1, "FAIL missing vector file");
        scan=$fscanf(fd, "%d", count);
        if (scan != 1 || count != 2) $fatal(1, "FAIL vector count");
        wait(model_initialized);
        repeat(2) @(posedge clk);
        @(negedge clk); hard_reset=0;
        @(negedge clk);
        for (case_index=0; case_index<count; case_index=case_index+1) begin
            scan=$fscanf(fd, "%h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h",
                source_count, groups, group_id, output_channel, output_y, output_x, source0_base_address, source0_length_bytes, source0_channels, source0_height, source0_width, source0_channel_start, source0_channel_end, source0_multiplier_q31, source1_base_address, source1_length_bytes, source1_channels, source1_height, source1_width, source1_channel_start, source1_channel_end, source1_multiplier_q31, output_base_address, output_length_bytes, output_channels, output_height, output_width, expected_source, expected_output, expected_index, expected_value);
            if (scan != 31) $fatal(1, "FAIL truncated vector");
            if (!start_ready) $fatal(1, "FAIL start not ready");
            reads=0; writes=0; start_valid=1;
            @(posedge clk); @(negedge clk); start_valid=0;
            watchdog=0;
            while (!result_valid) begin
                @(negedge clk); watchdog=watchdog+1;
                if (watchdog>300) $fatal(1, "FAIL result timeout");
            end
            if (result_error_code !== 0 || result_value !== expected_value[7:0] ||
                result_source_address !== expected_source || result_source_index !== expected_index ||
                result_output_address !== expected_output || reads != 1 || writes != 1)
                $fatal(1, "FAIL result case=%0d value=%h expected=%h", case_index, result_value, expected_value);
            repeat(2) begin
                @(negedge clk);
                if (!result_valid || result_value !== expected_value[7:0] || result_error_code !== 0)
                    $fatal(1, "FAIL result backpressure");
            end
            result_ready=1;
            @(posedge clk); @(negedge clk); result_ready=0;
            if (result_valid) $fatal(1, "FAIL completion handshake");
            readback_mode=1; readback_valid=1;
            watchdog=0;
            while (!master_ready) begin
                @(negedge clk); watchdog=watchdog+1;
                if (watchdog>300) $fatal(1, "FAIL readback request timeout");
            end
            @(posedge clk); @(negedge clk); readback_valid=0;
            watchdog=0;
            while (!master_rsp_valid) begin
                @(negedge clk); watchdog=watchdog+1;
                if (watchdog>300) $fatal(1, "FAIL readback response timeout");
            end
            if (master_rsp_error !== 0 ||
                ((master_rsp_rdata >> (expected_output[1:0]*8)) & 32'hFF) !== expected_value) $fatal(1, "FAIL actual memory readback error=%0d data=%h expected=%h reads=%0d writes=%0d", master_rsp_error, master_rsp_rdata, expected_value, reads, writes);
            @(posedge clk); @(negedge clk);
            if (reads != 2 || writes != 1) $fatal(1, "FAIL readback handshake counts");
            readback_mode=0;
        end
        $fclose(fd);
        $display("PASS S2A-T15 route smoke cases=2 input_reads=2 writes=2 readbacks=2");
        $finish;
    end
    initial begin
        #100000; $fatal(1, "FAIL global watchdog");
    end
endmodule

// S2A-T15：T06 每个空间点遍历全部通道，T10 数据与 D2 黄金独立于候选值。
module tb_s2a_route_engine_full;
    logic  clk;
    logic  hard_reset;
    logic  abort;
    logic  start_valid;
    logic  start_ready;
    logic [31:0] source_count;
    logic [31:0] groups;
    logic [31:0] group_id;
    logic [31:0] output_channel;
    logic [31:0] output_y;
    logic [31:0] output_x;
    logic [31:0] source0_base_address;
    logic [31:0] source0_length_bytes;
    logic [31:0] source0_channels;
    logic [31:0] source0_height;
    logic [31:0] source0_width;
    logic [31:0] source0_channel_start;
    logic [31:0] source0_channel_end;
    logic [31:0] source0_multiplier_q31;
    logic [31:0] source1_base_address;
    logic [31:0] source1_length_bytes;
    logic [31:0] source1_channels;
    logic [31:0] source1_height;
    logic [31:0] source1_width;
    logic [31:0] source1_channel_start;
    logic [31:0] source1_channel_end;
    logic [31:0] source1_multiplier_q31;
    logic [31:0] output_base_address;
    logic [31:0] output_length_bytes;
    logic [31:0] output_channels;
    logic [31:0] output_height;
    logic [31:0] output_width;
    logic  backend_cancel;
    logic  backend_req_valid;
    logic  backend_req_ready;
    logic  backend_req_write;
    logic [31:0] backend_req_addr;
    logic [31:0] backend_req_wdata;
    logic [3:0] backend_req_rstrb;
    logic [3:0] backend_req_wstrb;
    logic  backend_rsp_valid;
    logic [31:0] backend_rsp_rdata;
    logic [2:0] backend_rsp_error;
    logic  result_valid;
    logic  result_ready;
    logic [31:0] result_source_index;
    logic [31:0] result_source_address;
    logic [31:0] result_output_address;
    logic [7:0] result_value;
    logic [2:0] result_error_code;
    initial clk = 0;
    always #5 clk = ~clk;
    logic readback_mode, readback_valid;
    logic master_ready, master_rsp_valid;
    logic [31:0] master_rsp_rdata;
    logic [2:0] master_rsp_error;
    logic mem_valid, mem_ready, mem_write, model_initialized;
    logic [31:0] mem_addr, mem_wdata, mem_rdata;
    logic [3:0] mem_rstrb, mem_wstrb;
    logic [2:0] mem_error_code;
    logic [31:0] expected_source, expected_output, expected_index, expected_value;
    integer fd, count, scan, watchdog, reads, writes, case_index;
    integer queries=0, legal=0, raw80=0, total_reads=0, total_writes=0, readbacks=0;
    integer expected_error, vector_class, layer_id, spatial_id;
    logic [31:0] readback_expected;
    integer outstanding=0, accepted=0, responses=0, stall_cycles=0;
    logic held_valid=0;
    logic [72:0] held_fields;
    always @(posedge clk) begin
        if (hard_reset || abort) begin outstanding=0; held_valid=0; end
        else begin
            if ((readback_mode ? readback_valid : backend_req_valid) && master_ready) begin
                if (outstanding != 0) $fatal(1, "FAIL multiple outstanding");
                outstanding=outstanding+1; accepted=accepted+1;
            end
            if (master_rsp_valid) begin
                if (outstanding != 1) $fatal(1, "FAIL response without request");
                outstanding=outstanding-1; responses=responses+1;
            end
            if (held_valid && (!mem_valid ||
                {mem_write,mem_addr,mem_wdata,mem_rstrb,mem_wstrb} !== held_fields))
                $fatal(1, "FAIL stalled fields changed");
            held_valid=mem_valid && !mem_ready;
            held_fields={mem_write,mem_addr,mem_wdata,mem_rstrb,mem_wstrb};
            if (held_valid) stall_cycles=stall_cycles+1;
        end
    end
    s2a_route_engine dut (
        .clk(clk),
        .hard_reset(hard_reset),
        .abort(abort),
        .start_valid(start_valid),
        .start_ready(start_ready),
        .source_count(source_count),
        .groups(groups),
        .group_id(group_id),
        .output_channel(output_channel),
        .output_y(output_y),
        .output_x(output_x),
        .source0_base_address(source0_base_address),
        .source0_length_bytes(source0_length_bytes),
        .source0_channels(source0_channels),
        .source0_height(source0_height),
        .source0_width(source0_width),
        .source0_channel_start(source0_channel_start),
        .source0_channel_end(source0_channel_end),
        .source0_multiplier_q31(source0_multiplier_q31),
        .source1_base_address(source1_base_address),
        .source1_length_bytes(source1_length_bytes),
        .source1_channels(source1_channels),
        .source1_height(source1_height),
        .source1_width(source1_width),
        .source1_channel_start(source1_channel_start),
        .source1_channel_end(source1_channel_end),
        .source1_multiplier_q31(source1_multiplier_q31),
        .output_base_address(output_base_address),
        .output_length_bytes(output_length_bytes),
        .output_channels(output_channels),
        .output_height(output_height),
        .output_width(output_width),
        .backend_cancel(backend_cancel),
        .backend_req_valid(backend_req_valid),
        .backend_req_ready(backend_req_ready),
        .backend_req_write(backend_req_write),
        .backend_req_addr(backend_req_addr),
        .backend_req_wdata(backend_req_wdata),
        .backend_req_rstrb(backend_req_rstrb),
        .backend_req_wstrb(backend_req_wstrb),
        .backend_rsp_valid(backend_rsp_valid),
        .backend_rsp_rdata(backend_rsp_rdata),
        .backend_rsp_error(backend_rsp_error),
        .result_valid(result_valid),
        .result_ready(result_ready),
        .result_source_index(result_source_index),
        .result_source_address(result_source_address),
        .result_output_address(result_output_address),
        .result_value(result_value),
        .result_error_code(result_error_code)
    );
    assign backend_req_ready = !readback_mode && master_ready;
    assign backend_rsp_valid = !readback_mode && master_rsp_valid;
    assign backend_rsp_rdata = master_rsp_rdata;
    assign backend_rsp_error = master_rsp_error;
    s2a_memory_master u_master (
        .clk(clk), .hard_reset(hard_reset), .cancel(backend_cancel),
        .buffer_owner_pl(1'b1),
        .backend_req_valid(readback_mode ? readback_valid : backend_req_valid),
        .backend_req_ready(master_ready),
        .backend_req_write(readback_mode ? 1'b0 : backend_req_write),
        .backend_req_addr(readback_mode ? {expected_output[31:2],2'b00} : backend_req_addr),
        .backend_req_wdata(readback_mode ? 32'd0 : backend_req_wdata),
        .backend_req_rstrb(readback_mode ? (4'b0001 << expected_output[1:0]) : backend_req_rstrb),
        .backend_req_wstrb(readback_mode ? 4'd0 : backend_req_wstrb),
        .backend_rsp_valid(master_rsp_valid), .backend_rsp_rdata(master_rsp_rdata),
        .backend_rsp_error(master_rsp_error), .mem_valid(mem_valid),
        .mem_ready(mem_ready), .mem_write(mem_write), .mem_addr(mem_addr),
        .mem_wdata(mem_wdata), .mem_rstrb(mem_rstrb), .mem_wstrb(mem_wstrb),
        .mem_rdata(mem_rdata), .mem_error_code(mem_error_code)
    );
    s2a_memory_model u_memory (
        .clk(clk), .reset(hard_reset), .buffer_owner_pl(1'b1),
        .fault_inject_valid(1'b0), .fault_inject_code(3'd0),
        .mem_valid(mem_valid), .mem_write(mem_write), .mem_addr(mem_addr),
        .mem_wdata(mem_wdata), .mem_rstrb(mem_rstrb), .mem_wstrb(mem_wstrb),
        .mem_ready(mem_ready), .mem_rdata(mem_rdata),
        .mem_error_code(mem_error_code), .model_initialized(model_initialized)
    );
    always @(posedge clk) begin
        if (!hard_reset && mem_valid && mem_ready) begin
            if (mem_error_code !== 0) $fatal(1, "FAIL memory error");
            if (mem_write) begin
                if (readback_mode || mem_addr !== {expected_output[31:2],2'b00} ||
                    mem_wstrb !== (4'b0001 << expected_output[1:0]) || mem_rstrb !== 0 ||
                    mem_wdata !== (expected_value << (expected_output[1:0]*8)))
                    $fatal(1, "FAIL output transaction");
                writes = writes + 1;
            end else begin
                if (mem_wstrb !== 0) $fatal(1, "FAIL read strobe");
                if (!readback_mode && (mem_addr !== {expected_source[31:2],2'b00} ||
                    mem_rstrb !== (4'b0001 << expected_source[1:0])))
                    $fatal(1, "FAIL input transaction");
                reads = reads + 1;
            end
        end
    end
    initial begin
        hard_reset=1; abort=0; start_valid=0; result_ready=0;
        readback_mode=0; readback_valid=0; reads=0; writes=0;
        fd=$fopen("route_full.dat", "r");
        if (!fd) $fatal(1, "FAIL missing vector file");
        scan=$fscanf(fd, "%d", count);
        if (scan != 1 || count <= 0) $fatal(1, "FAIL vector count");
        wait(model_initialized);
        repeat(2) @(posedge clk);
        @(negedge clk); hard_reset=0;
        @(negedge clk);
        for (case_index=0; case_index<count; case_index=case_index+1) begin
            scan=$fscanf(fd, "%d %d %d", vector_class, layer_id, spatial_id);
            if (scan != 3) $fatal(1, "FAIL spatial metadata");
            scan=$fscanf(fd, "%h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h",
                source_count, groups, group_id, output_channel, output_y, output_x, source0_base_address, source0_length_bytes, source0_channels, source0_height, source0_width, source0_channel_start, source0_channel_end, source0_multiplier_q31, source1_base_address, source1_length_bytes, source1_channels, source1_height, source1_width, source1_channel_start, source1_channel_end, source1_multiplier_q31, output_base_address, output_length_bytes, output_channels, output_height, output_width);
            if (scan != 27) $fatal(1, "FAIL truncated descriptor");
            for (output_channel=0; output_channel<output_channels; output_channel=output_channel+1) begin
                scan=$fscanf(fd, "%h %h %h %h %h %h", expected_source, expected_output,
                             expected_index, expected_value, expected_error, readback_expected);
                if (scan != 6) $fatal(1, "FAIL truncated channel golden");
            if (!start_ready) $fatal(1, "FAIL start not ready");
            reads=0; writes=0; start_valid=1;
            @(posedge clk); @(negedge clk); start_valid=0;
            watchdog=0;
            while (!result_valid) begin
                @(negedge clk); watchdog=watchdog+1;
                if (watchdog>300) $fatal(1, "FAIL result timeout");
            end
            if (result_error_code !== expected_error || result_value !== expected_value[7:0] ||
                result_source_address !== expected_source || result_source_index !== expected_index ||
                result_output_address !== expected_output || reads != 1 || writes != (expected_error==0 ? 1 : 0))
                $fatal(1, "FAIL result case=%0d value=%h expected=%h", case_index, result_value, expected_value);
            repeat(2) begin
                @(negedge clk);
                if (!result_valid || result_value !== expected_value[7:0] || result_error_code !== expected_error)
                    $fatal(1, "FAIL result backpressure");
            end
            result_ready=1;
            @(posedge clk); @(negedge clk); result_ready=0;
            if (result_valid) $fatal(1, "FAIL completion handshake");
            readback_mode=1; readback_valid=1;
            watchdog=0;
            while (!master_ready) begin
                @(negedge clk); watchdog=watchdog+1;
                if (watchdog>300) $fatal(1, "FAIL readback request timeout");
            end
            @(posedge clk); @(negedge clk); readback_valid=0;
            watchdog=0;
            while (!master_rsp_valid) begin
                @(negedge clk); watchdog=watchdog+1;
                if (watchdog>300) $fatal(1, "FAIL readback response timeout");
            end
            if (master_rsp_error !== 0 ||
                ((master_rsp_rdata >> (expected_output[1:0]*8)) & 32'hFF) !== readback_expected) $fatal(1, "FAIL actual memory readback error=%0d data=%h expected=%h reads=%0d writes=%0d", master_rsp_error, master_rsp_rdata, expected_value, reads, writes);
            @(posedge clk); @(negedge clk);
            if (reads != 2 || writes != (expected_error==0 ? 1 : 0)) $fatal(1, "FAIL readback handshake counts");
            readback_mode=0;
            queries=queries+1; readbacks=readbacks+1;
            total_reads=total_reads+reads; total_writes=total_writes+writes;
            if (expected_error==0) legal=legal+1; else raw80=raw80+1;
            end
            // 仅独立空间用例间初始化稀疏补丁表；保留 stall_index，不模拟复位。
            if (mem_valid || u_master.pending || u_memory.pending || outstanding != 0)
                $fatal(1, "FAIL patch reinitialization while active");
            u_memory.patch_count=0;
        end
        $fclose(fd);
        $display("PASS S2A-T15 route full spatial=%0d queries=%0d legal=%0d raw80=%0d reads=%0d writes=%0d readbacks=%0d accepted=%0d responses=%0d stalls=%0d", count,queries,legal,raw80,total_reads,total_writes,readbacks,accepted,responses,stall_cycles);
        $finish;
    end
endmodule

// S2A-T15：真实 T10 总线错误、取消、复位与恢复；整个测试保留已写补丁。
module tb_s2a_route_engine_exceptions;
    logic  clk;
    logic  hard_reset;
    logic  abort;
    logic  start_valid;
    logic  start_ready;
    logic [31:0] source_count;
    logic [31:0] groups;
    logic [31:0] group_id;
    logic [31:0] output_channel;
    logic [31:0] output_y;
    logic [31:0] output_x;
    logic [31:0] source0_base_address;
    logic [31:0] source0_length_bytes;
    logic [31:0] source0_channels;
    logic [31:0] source0_height;
    logic [31:0] source0_width;
    logic [31:0] source0_channel_start;
    logic [31:0] source0_channel_end;
    logic [31:0] source0_multiplier_q31;
    logic [31:0] source1_base_address;
    logic [31:0] source1_length_bytes;
    logic [31:0] source1_channels;
    logic [31:0] source1_height;
    logic [31:0] source1_width;
    logic [31:0] source1_channel_start;
    logic [31:0] source1_channel_end;
    logic [31:0] source1_multiplier_q31;
    logic [31:0] output_base_address;
    logic [31:0] output_length_bytes;
    logic [31:0] output_channels;
    logic [31:0] output_height;
    logic [31:0] output_width;
    logic  backend_cancel;
    logic  backend_req_valid;
    logic  backend_req_ready;
    logic  backend_req_write;
    logic [31:0] backend_req_addr;
    logic [31:0] backend_req_wdata;
    logic [3:0] backend_req_rstrb;
    logic [3:0] backend_req_wstrb;
    logic  backend_rsp_valid;
    logic [31:0] backend_rsp_rdata;
    logic [2:0] backend_rsp_error;
    logic  result_valid;
    logic  result_ready;
    logic [31:0] result_source_index;
    logic [31:0] result_source_address;
    logic [31:0] result_output_address;
    logic [7:0] result_value;
    logic [2:0] result_error_code;
    initial clk = 0;
    always #5 clk = ~clk;
    logic readback_mode, readback_valid;
    logic master_ready, master_rsp_valid;
    logic [31:0] master_rsp_rdata;
    logic [2:0] master_rsp_error;
    logic mem_valid, mem_ready, mem_write, model_initialized;
    logic [31:0] mem_addr, mem_wdata, mem_rdata;
    logic [3:0] mem_rstrb, mem_wstrb;
    logic [2:0] mem_error_code;
    logic [31:0] expected_source, expected_output, expected_index, expected_value;
    integer fd, count, scan, watchdog, reads, writes, case_index;
    integer inject_code=0;
    logic inject_write=0;
    wire injecting = (inject_code != 0) && (mem_write == inject_write) && !readback_mode;
    integer total_cases=0, cancels=0, invalids=0, errors=0, recoveries=0;
    integer committed=0, before_committed, old_patches;
    logic [31:0] old_byte;
    s2a_route_engine dut (
        .clk(clk),
        .hard_reset(hard_reset),
        .abort(abort),
        .start_valid(start_valid),
        .start_ready(start_ready),
        .source_count(source_count),
        .groups(groups),
        .group_id(group_id),
        .output_channel(output_channel),
        .output_y(output_y),
        .output_x(output_x),
        .source0_base_address(source0_base_address),
        .source0_length_bytes(source0_length_bytes),
        .source0_channels(source0_channels),
        .source0_height(source0_height),
        .source0_width(source0_width),
        .source0_channel_start(source0_channel_start),
        .source0_channel_end(source0_channel_end),
        .source0_multiplier_q31(source0_multiplier_q31),
        .source1_base_address(source1_base_address),
        .source1_length_bytes(source1_length_bytes),
        .source1_channels(source1_channels),
        .source1_height(source1_height),
        .source1_width(source1_width),
        .source1_channel_start(source1_channel_start),
        .source1_channel_end(source1_channel_end),
        .source1_multiplier_q31(source1_multiplier_q31),
        .output_base_address(output_base_address),
        .output_length_bytes(output_length_bytes),
        .output_channels(output_channels),
        .output_height(output_height),
        .output_width(output_width),
        .backend_cancel(backend_cancel),
        .backend_req_valid(backend_req_valid),
        .backend_req_ready(backend_req_ready),
        .backend_req_write(backend_req_write),
        .backend_req_addr(backend_req_addr),
        .backend_req_wdata(backend_req_wdata),
        .backend_req_rstrb(backend_req_rstrb),
        .backend_req_wstrb(backend_req_wstrb),
        .backend_rsp_valid(backend_rsp_valid),
        .backend_rsp_rdata(backend_rsp_rdata),
        .backend_rsp_error(backend_rsp_error),
        .result_valid(result_valid),
        .result_ready(result_ready),
        .result_source_index(result_source_index),
        .result_source_address(result_source_address),
        .result_output_address(result_output_address),
        .result_value(result_value),
        .result_error_code(result_error_code)
    );
    assign backend_req_ready = !readback_mode && master_ready;
    assign backend_rsp_valid = !readback_mode && master_rsp_valid;
    assign backend_rsp_rdata = master_rsp_rdata;
    assign backend_rsp_error = master_rsp_error;
    s2a_memory_master u_master (
        .clk(clk), .hard_reset(hard_reset), .cancel(backend_cancel),
        .buffer_owner_pl(1'b1),
        .backend_req_valid(readback_mode ? readback_valid : backend_req_valid),
        .backend_req_ready(master_ready),
        .backend_req_write(readback_mode ? 1'b0 : backend_req_write),
        .backend_req_addr(readback_mode ? {expected_output[31:2],2'b00} : backend_req_addr),
        .backend_req_wdata(readback_mode ? 32'd0 : backend_req_wdata),
        .backend_req_rstrb(readback_mode ? (4'b0001 << expected_output[1:0]) : backend_req_rstrb),
        .backend_req_wstrb(readback_mode ? 4'd0 : backend_req_wstrb),
        .backend_rsp_valid(master_rsp_valid), .backend_rsp_rdata(master_rsp_rdata),
        .backend_rsp_error(master_rsp_error), .mem_valid(mem_valid),
        .mem_ready(mem_ready), .mem_write(mem_write), .mem_addr(mem_addr),
        .mem_wdata(mem_wdata), .mem_rstrb(mem_rstrb), .mem_wstrb(mem_wstrb),
        .mem_rdata(mem_rdata), .mem_error_code(mem_error_code)
    );
    s2a_memory_model u_memory (
        .clk(clk), .reset(hard_reset), .buffer_owner_pl(1'b1),
        .fault_inject_valid(injecting && inject_code >= 6), .fault_inject_code(inject_code[2:0]),
        .mem_valid(mem_valid), .mem_write(mem_write), .mem_addr(injecting && inject_code == 2 ? 32'hFFFF_FFFC : mem_addr),
        .mem_wdata(mem_wdata), .mem_rstrb(injecting && inject_code == 1 ? 4'd0 : mem_rstrb), .mem_wstrb(injecting && inject_code == 1 ? 4'd0 : mem_wstrb),
        .mem_ready(mem_ready), .mem_rdata(mem_rdata),
        .mem_error_code(mem_error_code), .model_initialized(model_initialized)
    );
    always @(posedge clk) begin
        if (!hard_reset && mem_valid && mem_ready) begin
            if (mem_write) begin
                writes=writes+1;
                if (mem_error_code == 0) committed=committed+1;
            end else reads=reads+1;
        end
    end
    task automatic load_base;
        begin
            fd=$fopen("route_smoke.dat", "r");
            scan=$fscanf(fd, "%d", count);
            scan=$fscanf(fd, "%h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h",
                source_count, groups, group_id, output_channel, output_y, output_x, source0_base_address, source0_length_bytes, source0_channels, source0_height, source0_width, source0_channel_start, source0_channel_end, source0_multiplier_q31, source1_base_address, source1_length_bytes, source1_channels, source1_height, source1_width, source1_channel_start, source1_channel_end, source1_multiplier_q31, output_base_address, output_length_bytes, output_channels, output_height, output_width, expected_source, expected_output, expected_index, expected_value);
            if (scan != 31) $fatal(1,"FAIL exception descriptor");
            $fclose(fd);
        end
    endtask
    task automatic launch;
        begin
            if (!start_ready) $fatal(1,"FAIL exception start_ready");
            reads=0; writes=0; start_valid=1;
            @(posedge clk); @(negedge clk); start_valid=0;
        end
    endtask
    task automatic finish_result(input integer error_code, input integer nr, input integer nw);
        logic [106:0] held;
        begin
            watchdog=0;
            while (!result_valid) begin
                @(negedge clk); watchdog=watchdog+1;
                if (watchdog>300) $fatal(1,"FAIL exception timeout");
            end
            if (result_error_code !== error_code || reads != nr || writes != nw)
                $fatal(1,"FAIL exception result code=%0d expected=%0d reads=%0d writes=%0d",result_error_code,error_code,reads,writes);
            held={result_source_index,result_source_address,result_output_address,result_value,result_error_code};
            repeat(3) begin
                @(negedge clk);
                if (!result_valid || start_ready || backend_req_valid ||
                    {result_source_index,result_source_address,result_output_address,result_value,result_error_code} !== held)
                    $fatal(1,"FAIL exception held result");
            end
            result_ready=1;
            @(posedge clk); @(negedge clk); result_ready=0;
            total_cases=total_cases+1;
        end
    endtask
    task automatic read_output(output logic [31:0] value);
        begin
            readback_mode=1; readback_valid=1;
            watchdog=0;
            while (!master_ready) begin
                @(negedge clk); watchdog=watchdog+1;
                if (watchdog>300) $fatal(1,"FAIL exception readback ready");
            end
            @(posedge clk); @(negedge clk); readback_valid=0;
            watchdog=0;
            while (!master_rsp_valid) begin
                @(negedge clk); watchdog=watchdog+1;
                if (watchdog>300) $fatal(1,"FAIL exception readback timeout");
            end
            if (master_rsp_error !== 0) $fatal(1,"FAIL exception readback error");
            value=(master_rsp_rdata >> (expected_output[1:0]*8)) & 32'hFF;
            @(posedge clk); @(negedge clk); readback_mode=0;
        end
    endtask
    task automatic recovery;
        logic [31:0] value;
        begin
            inject_code=0; load_base(); launch(); finish_result(0,1,1);
            if (result_value !== expected_value[7:0]) $fatal(1,"FAIL recovery value");
            read_output(value);
            if (value !== expected_value) $fatal(1,"FAIL recovery memory");
            recoveries=recoveries+1;
        end
    endtask
    task automatic invalid_case(input integer which);
        integer expected_code;
        begin
            load_base(); expected_code=1;
            case(which)
                0: source_count=0;
                1: groups=0;
                2: group_id=groups;
                3: source0_multiplier_q31=0;
                4: output_channel=output_channels;
                5: output_y=output_height;
                6: output_x=output_width;
                7: begin source0_length_bytes=1; expected_code=2; end
                8: begin source0_base_address=32'hFFFF_FFF0; expected_code=2; end
                9: begin output_length_bytes=1; expected_code=3; end
                10: begin output_base_address=32'hFFFF_FFF0; expected_code=2; end
                11: begin output_channels=output_channels+1; expected_code=3; end
                12: source0_channel_start=0;
                13: source0_multiplier_q31=32'h8000_0001;
                14: begin source0_channels=32'h8000_0000; source0_channel_end=32'h8000_0000; source0_channel_start=0; groups=1; group_id=0; expected_code=2; end
            endcase
            before_committed=committed;
            launch(); finish_result(expected_code,0,0);
            if (committed != before_committed) $fatal(1,"FAIL invalid side effect");
            invalids=invalids+1; recovery();
        end
    endtask
    task automatic bus_error(input integer code, input logic write_side);
        logic [31:0] value;
        begin
            load_base(); read_output(old_byte);
            inject_code=code; inject_write=write_side; before_committed=committed;
            launch(); finish_result(code == 7 ? 6 : code,1,write_side ? 1 : 0);
            if (result_value !== 0 || committed != before_committed) $fatal(1,"FAIL error side effect");
            inject_code=0; read_output(value);
            if (value !== old_byte) $fatal(1,"FAIL error memory changed");
            errors=errors+1; recovery();
        end
    endtask
    task automatic cancel_pending(input logic reset_case,input logic write_side);
        logic [31:0] value;
        begin
            load_base(); read_output(old_byte); before_committed=committed; old_patches=u_memory.patch_count;
            // 强制下一目标访问进入确定的 7-cycle stall，再在 pending 时取消。
            u_memory.stall_index[2]=3; u_memory.stall_index[3]=3;
            launch(); watchdog=0;
            while (!(mem_valid && mem_write == write_side && !mem_ready && u_memory.pending)) begin
                @(negedge clk); watchdog=watchdog+1;
                if (watchdog>300) $fatal(1,"FAIL cancel pending timeout");
            end
            if (reset_case) hard_reset=1; else abort=1;
            #1;
            if (mem_valid || backend_req_valid) $fatal(1,"FAIL cancel bus not suppressed");
            @(posedge clk); @(negedge clk); hard_reset=0; abort=0;
            repeat(15) begin
                @(negedge clk);
                if (result_valid || backend_req_valid || mem_valid || master_rsp_valid)
                    $fatal(1,"FAIL late activity after cancel");
            end
            if (!start_ready || committed != before_committed || u_memory.patch_count != old_patches)
                $fatal(1,"FAIL cancellation side effect");
            read_output(value);
            if (value !== old_byte) $fatal(1,"FAIL cancel memory changed");
            cancels=cancels+1; recovery();
        end
    endtask
    task automatic half_away_case(input integer signed_value,input integer rounded_value);
        integer offset;
        logic [31:0] value;
        begin
            load_base();
            offset=0;
            while (u_memory.initial_byte(source0_base_address+offset) !== (signed_value & 255)) offset=offset+1;
            if (offset>=source0_length_bytes) $fatal(1,"FAIL half-away source outside tensor");
            source0_base_address=source0_base_address+offset;
            source_count=1; groups=1; group_id=0; output_channel=0; output_y=0; output_x=0;
            source0_length_bytes=1; source0_channels=1; source0_height=1; source0_width=1;
            source0_channel_start=0; source0_channel_end=1; source0_multiplier_q31=32'h4000_0000;
            output_length_bytes=1; output_channels=1; output_height=1; output_width=1;
            expected_source=source0_base_address; expected_output=output_base_address;
            expected_value=rounded_value & 255;
            launch(); finish_result(0,1,1);
            if (result_value !== expected_value[7:0]) $fatal(1,"FAIL half-away actual input=%0d output=%h",signed_value,result_value);
            read_output(value);
            if (value !== expected_value) $fatal(1,"FAIL half-away actual memory");
        end
    endtask
    initial begin
        hard_reset=1; abort=0; start_valid=0; result_ready=0;
        readback_mode=0; readback_valid=0; reads=0; writes=0;
        wait(model_initialized); repeat(2) @(posedge clk);
        @(negedge clk); hard_reset=0; @(negedge clk);
        recovery();
        for (case_index=0;case_index<15;case_index=case_index+1) invalid_case(case_index);
        bus_error(1,0); bus_error(2,0); bus_error(6,0); bus_error(7,0);
        bus_error(1,1); bus_error(2,1); bus_error(6,1); bus_error(7,1);
        cancel_pending(0,0); cancel_pending(0,1); cancel_pending(1,0); cancel_pending(1,1);
        half_away_case(-127,-64); half_away_case(-3,-2); half_away_case(-1,-1);
        half_away_case(1,1); half_away_case(3,2); half_away_case(127,64);
        $display("PASS S2A-T15 exceptions half_away=6 invalid=%0d bus_errors=%0d cancels=%0d recoveries=%0d result_cases=%0d",invalids,errors,cancels,recoveries,total_cases);
        $finish;
    end
    initial begin #1000000; $fatal(1,"FAIL exceptions global watchdog"); end
endmodule
