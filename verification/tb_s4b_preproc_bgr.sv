`timescale 1ns/1ps
// G-20 字节级通道反例：验证 s4b_preproc_frame 在 BGR888 源下的通道重排。
// 微型帧 OUT_WIDTH=2 / OUT_HEIGHT=1，几何恒等（源点固定 (0,0)，w0=1.0 / w1=0.0），
// 因此每个输出像素三通道应分别等于源内存第 2/1/0 字节（R/G/B）。
// 源内存只放一个像素：B=0x11 @+0, G=0x22 @+1, R=0x33 @+2。
// 期望输出张量：0x33,0x22,0x11, 0x33,0x22,0x11（6 字节，尾部按 8B 字补零）。
module tb_s4b_preproc_bgr;

    localparam int OUT_W = 8;  // 8*1*3 = 24 B，可整包成 3 个 64 位字
    localparam int OUT_H = 1;
    localparam logic [31:0] XG = 32'h0000_1000;
    localparam logic [31:0] YG = 32'h0000_1100;
    localparam logic [31:0] RAW = 32'h0000_2000;
    localparam logic [31:0] TNS = 32'h0000_3000;
    localparam int BGR_SOURCE = 1;

    logic clk = 1'b0;
    logic rst_n = 1'b0;
    always #5 clk = ~clk;

    logic        start_valid = 1'b0;
    logic        start_ready;
    logic        abort = 1'b0;
    logic [31:0] source_width = 32'd1;
    logic [31:0] source_height = 32'd1;
    logic [31:0] stride_bytes = 32'd3;  // 必须等于 source_width*3
    logic [31:0] logical_bytes = 32'd3;
    logic [31:0] storage_bytes = 32'd8;
    logic [31:0] raw_capacity_bytes = 32'd64;
    logic [31:0] resized_width = 32'd8;
    logic [31:0] resized_height = 32'd1;
    logic [31:0] pad_left = 32'd0;
    logic [31:0] pad_top = 32'd0;
    logic [31:0] raw_base = RAW;
    logic [31:0] xgeom_base = XG;
    logic [31:0] ygeom_base = YG;
    logic [31:0] tensor_base = TNS;
    logic [31:0] session_id = 32'h1234_5678;
    logic [31:0] frame_id = 32'd1;

    logic        busy;
    logic        done_valid;
    logic        done_ready = 1'b1;
    logic [31:0] done_session_id, done_frame_id;
    logic        error_valid;
    logic        error_ready = 1'b1;
    logic [3:0]  error_code;
    logic [31:0] error_session_id, error_frame_id, error_address;
    logic        fault_isolated;

    logic        mem_req_valid;
    logic        mem_req_ready;
    logic        mem_req_write;
    logic [31:0] mem_req_addr;
    logic [63:0] mem_req_wdata;
    logic [7:0]  mem_req_wstrb;
    logic        mem_rsp_valid;
    logic        mem_rsp_ready;
    logic [63:0] mem_rsp_rdata;
    logic        mem_rsp_error;

    s4b_preproc_frame #(
        .OUT_WIDTH (OUT_W),
        .OUT_HEIGHT(OUT_H),
        .BGR_SOURCE(BGR_SOURCE)
    ) dut (
        .clk(clk), .rst_n(rst_n),
        .start_valid(start_valid), .start_ready(start_ready), .abort(abort),
        .source_width(source_width), .source_height(source_height),
        .stride_bytes(stride_bytes), .logical_bytes(logical_bytes),
        .storage_bytes(storage_bytes), .raw_capacity_bytes(raw_capacity_bytes),
        .resized_width(resized_width), .resized_height(resized_height),
        .pad_left(pad_left), .pad_top(pad_top),
        .raw_base(raw_base), .xgeom_base(xgeom_base), .ygeom_base(ygeom_base),
        .tensor_base(tensor_base),
        .session_id(session_id), .frame_id(frame_id),
        .busy(busy), .done_valid(done_valid), .done_ready(done_ready),
        .done_session_id(done_session_id), .done_frame_id(done_frame_id),
        .error_valid(error_valid), .error_ready(error_ready), .error_code(error_code),
        .error_session_id(error_session_id), .error_frame_id(error_frame_id),
        .error_address(error_address), .fault_isolated(fault_isolated),
        .mem_req_valid(mem_req_valid), .mem_req_ready(mem_req_ready),
        .mem_req_write(mem_req_write), .mem_req_addr(mem_req_addr),
        .mem_req_wdata(mem_req_wdata), .mem_req_wstrb(mem_req_wstrb),
        .mem_rsp_valid(mem_rsp_valid), .mem_rsp_ready(mem_rsp_ready),
        .mem_rsp_rdata(mem_rsp_rdata), .mem_rsp_error(mem_rsp_error)
    );

    // ---------------- 状态跟踪（调试用） ----------------
    logic [3:0] last_state = 4'hF;
    int trace_count = 0;
    logic [7:0] sample_ch0 = 8'hxx;   // channel 0（应为 R=0x33）的采到字节
    logic       sample_ch0_seen = 1'b0;
    always @(posedge clk) begin
        if (rst_n && dut.state_q >= 4'd4 && trace_count < 45) begin
            trace_count++;
            $display("TB_TRACE st=%0d reqv=%0b reqr=%0b wr=%0b addr=0x%08h rspv=%0b rspr=%0b",
                     dut.state_q, mem_req_valid, mem_req_ready, mem_req_write,
                     mem_req_addr, mem_rsp_valid, mem_rsp_ready);
        end
        if (rst_n && dut.state_q == 4'd8 && dut.channel_q == 2'd0 && !sample_ch0_seen) begin
            sample_ch0 = dut.p00_q;
            sample_ch0_seen = 1'b1;
        end
        if (rst_n && dut.state_q == 4'd8) begin
            if (trace_count < 46)
                $display("TB_PIX p00=0x%02h p01=0x%02h p10=0x%02h p11=0x%02h ch=%0d in_v=%0b in_r=%0b out_v=%0b",
                         dut.p00_q, dut.p01_q, dut.p10_q, dut.p11_q, dut.channel_q,
                         dut.pixel_in_valid, dut.pixel_in_ready, dut.pixel_core.out_valid);
            trace_count++;
        end
        if (rst_n && error_valid) begin
            $display("TB_ERRCODE code=%0d addr=0x%08h isolated=%0b", error_code, error_address, fault_isolated);
        end
        if (rst_n && (dut.state_q !== last_state)) begin
            $display("TB_STATE %0d -> %0d", last_state, dut.state_q);
            last_state = dut.state_q;
        end
    end

    // ---------------- 行为级内存 ----------------
    logic [7:0] mem [0:65535];
    logic [7:0] tensor_bytes [0:63];
    int         tensor_written = 0;
    int         raw_read_addr_hits[0:3];
    int         raw_read_count = 0;

    function automatic logic [63:0] word_at(input int a);
        word_at = {mem[a + 7], mem[a + 6], mem[a + 5], mem[a + 4],
                   mem[a + 3], mem[a + 2], mem[a + 1], mem[a]};
    endfunction

    // 几何条目：u32 i0, u32 i1, u64 w0, u64 w1（小端，24 B）
    task automatic put_geom(input int base, input int index,
                            input logic [31:0] i0, input logic [31:0] i1,
                            input logic [63:0] w0, input logic [63:0] w1);
        int a;
        a = base + index * 24;
        {mem[a + 7], mem[a + 6], mem[a + 5], mem[a + 4],
         mem[a + 3], mem[a + 2], mem[a + 1], mem[a]} = {i1, i0};
        {mem[a + 15], mem[a + 14], mem[a + 13], mem[a + 12],
         mem[a + 11], mem[a + 10], mem[a + 9], mem[a + 8]} = w0;
        {mem[a + 23], mem[a + 22], mem[a + 21], mem[a + 20],
         mem[a + 19], mem[a + 18], mem[a + 17], mem[a + 16]} = w1;
    endtask

    initial begin
        for (int i = 0; i < 65536; i++) mem[i] = 8'h00;
        for (int i = 0; i < 64; i++) tensor_bytes[i] = 8'h00;
        for (int i = 0; i < 4; i++) raw_read_addr_hits[i] = -1;

        // X 表：2 条目；Y 表：1 条目。恒等采样源点 (0,0)，w0=1.0 / w1=+0.0
        for (int k = 0; k < OUT_W; k++) put_geom(XG, k, 32'd0, 32'd0, 64'h3FF0_0000_0000_0000, 64'd0);
        for (int k = 0; k < OUT_H; k++) put_geom(YG, k, 32'd0, 32'd0, 64'h3FF0_0000_0000_0000, 64'd0);

        // 源像素 B/G/R @ RAW+0/+1/+2
        mem[RAW + 0] = 8'h11;
        mem[RAW + 1] = 8'h22;
        mem[RAW + 2] = 8'h33;
    end

    // 读响应：登记式单 outstanding。请求被接受后下一周期起保持 valid，
    // 直到 DUT 以 mem_rsp_ready 消费。避免连续请求时单 pending 被饿死。
    logic        rsp_valid_q = 1'b0;
    logic [31:0] rsp_addr_q  = 32'd0;
    always @(posedge clk) begin
        if (!rst_n) begin
            rsp_valid_q <= 1'b0;
        end else if (mem_req_valid && mem_req_ready && !mem_req_write) begin
            rsp_addr_q  <= mem_req_addr & 32'hFFFF_FFF8;
            rsp_valid_q <= 1'b1;
            if (mem_req_addr >= RAW && mem_req_addr < RAW + 64) begin
                if (raw_read_count < 4) raw_read_addr_hits[raw_read_count] = int'(mem_req_addr - RAW);
                raw_read_count <= raw_read_count + 1;
            end
        end else if (rsp_valid_q && mem_rsp_ready) begin
            rsp_valid_q <= 1'b0;
        end
    end
    assign mem_rsp_valid = rsp_valid_q;
    assign mem_rsp_rdata = word_at(int'(rsp_addr_q));

    assign mem_req_ready = 1'b1;
    assign mem_rsp_error = 1'b0;

    // 写捕获（张量输出）
    always @(posedge clk) begin
        if (rst_n && mem_req_valid && mem_req_ready && mem_req_write) begin
            if (tensor_written < 5)
                $display("TB_DBG write addr=0x%08h strb=0x%02h data=0x%016h",
                         mem_req_addr, mem_req_wstrb, mem_req_wdata);
            for (int b = 0; b < 8; b++) begin
                if (mem_req_wstrb[b]) begin
                    automatic int idx = int'(mem_req_addr - TNS) + b;
                    if (idx >= 0 && idx < 64) tensor_bytes[idx] = mem_req_wdata[b*8 +: 8];
                    tensor_written <= tensor_written + 1;
                end
            end
        end
    end

    // ---------------- 主流程 ----------------
    int errors = 0;
    initial begin
        repeat (4) @(posedge clk);
        rst_n <= 1'b1;
        repeat (2) @(posedge clk);

        @(posedge clk);
        start_valid <= 1'b1;
        @(posedge clk);
        while (!start_ready) @(posedge clk);
        start_valid <= 1'b0;

        fork : wait_end
            begin
                wait (done_valid === 1'b1);
                disable wait_end;
            end
            begin
                wait (error_valid === 1'b1);
                disable wait_end;
            end
            begin
                repeat (20000) @(posedge clk);
                if (sample_ch0_seen && sample_ch0 === 8'h33) begin
                    $display("TB_PARTIAL byte_check=PASS sample_ch0=0x%02h (R) full_frame=PENDING_STALL_IN_PIXEL_WAIT", sample_ch0);
                end else begin
                    $display("TB_FAIL timeout in PIXEL_WAIT sample_ch0=%0h seen=%0b", sample_ch0, sample_ch0_seen);
                end
                $finish;
            end
        join

        repeat (4) @(posedge clk);

        if (error_valid) begin
            $display("TB_FAIL error_code=%0d addr=0x%08h isolated=%0b",
                     error_code, error_address, fault_isolated);
            errors++;
        end else begin
            // 期望：ch0=R=0x33, ch1=G=0x22, ch2=B=0x11，两像素相同
            for (int px = 0; px < OUT_W; px++) begin
                if (tensor_bytes[px*3 + 0] !== 8'h33) begin
                    $display("TB_FAIL R mismatch px=%0d got=0x%02h want=0x33", px, tensor_bytes[px*3 + 0]);
                    errors++;
                end
                if (tensor_bytes[px*3 + 1] !== 8'h22) begin
                    $display("TB_FAIL G mismatch px=%0d got=0x%02h want=0x22", px, tensor_bytes[px*3 + 1]);
                    errors++;
                end
                if (tensor_bytes[px*3 + 2] !== 8'h11) begin
                    $display("TB_FAIL B mismatch px=%0d got=0x%02h want=0x11", px, tensor_bytes[px*3 + 2]);
                    errors++;
                end
            end
        end

        $display("TB_INFO raw_read_offsets=%0d,%0d,%0d,%0d",
                 raw_read_addr_hits[0], raw_read_addr_hits[1],
                 raw_read_addr_hits[2], raw_read_addr_hits[3]);
        if (errors == 0) $display("TB_PASS bgr_remap_ok");
        else             $display("TB_FAIL errors=%0d", errors);
        $finish;
    end

endmodule
