// S2C 候选：带授权区间限制的单请求 AXI3 64-bit 读突发缓存。
// 本模块不接入冻结 adapter；region_begin/end 必须来自外层已批准的对象边界。
// 接入方须在任意DDR写、run_epoch变化或clear_safe时拉高cache_invalidate。
module s2c_axi3_read_cache (
    input  logic        clk,
    input  logic        rst,
    input  logic        cancel,
    input  logic        cache_invalidate,
    input  logic        req_valid,
    output logic        req_ready,
    input  logic [31:0] req_addr,
    input  logic [31:0] region_begin,
    input  logic [31:0] region_end,
    output logic        rsp_valid,
    input  logic        rsp_ready,
    output logic [7:0]  rsp_data,
    output logic        rsp_error,

    output logic [5:0]  m_axi_arid,
    output logic [31:0] m_axi_araddr,
    output logic [3:0]  m_axi_arlen,
    output logic [2:0]  m_axi_arsize,
    output logic [1:0]  m_axi_arburst,
    output logic        m_axi_arvalid,
    input  logic        m_axi_arready,
    input  logic [5:0]  m_axi_rid,
    input  logic [63:0] m_axi_rdata,
    input  logic [1:0]  m_axi_rresp,
    input  logic        m_axi_rlast,
    input  logic        m_axi_rvalid,
    output logic        m_axi_rready,
    output logic        protocol_fault
);
    typedef enum logic [2:0] {ST_IDLE, ST_AR, ST_R, ST_RESP, ST_FAULT} state_t;
    state_t state;

    logic [7:0] cache_bytes [0:127];
    logic [31:0] cache_base;
    logic [7:0] cache_length;
    logic cache_valid;
    logic [31:0] request_address;
    logic [31:0] request_region_begin;
    logic [31:0] request_region_end;
    logic [31:0] burst_base;
    logic [4:0] burst_beats;
    logic [4:0] received_beats;
    logic [31:0] page_limit;
    logic [32:0] page_limit_ext;
    logic [32:0] aligned_end_ext;
    logic [31:0] aligned_address;
    logic [31:0] selected_limit;
    logic [31:0] available_beats;
    logic [31:0] request_cache_offset;
    logic [7:0] response_byte;
    logic response_error;
    logic cancel_pending;
    logic invalidate_pending;
    logic burst_narrow;
    logic burst_protocol_error;

    always_comb begin
        aligned_address = {req_addr[31:3], 3'b000};
        page_limit_ext = {1'b0, req_addr[31:12], 12'h000} + 33'd4096;
        page_limit = page_limit_ext[32] ? 32'hffff_ffff : page_limit_ext[31:0];
        selected_limit = (region_end < page_limit) ? region_end : page_limit;
        aligned_end_ext = {1'b0, aligned_address} + 33'd8;
        available_beats = (selected_limit >= aligned_address) ?
                          ((selected_limit - aligned_address) >> 3) : 32'd0;
        request_cache_offset = request_address - burst_base;

        req_ready = (state == ST_IDLE) && !cancel && !cache_invalidate;
        rsp_valid = (state == ST_RESP) && !cancel && !cancel_pending && !cache_invalidate;
        rsp_data = response_byte;
        rsp_error = response_error;
        m_axi_arid = 6'd0;
        m_axi_araddr = burst_base;
        m_axi_arlen = burst_beats[3:0] - 4'd1;
        m_axi_arsize = burst_narrow ? 3'd0 : 3'd3;
        m_axi_arburst = 2'b01;
        m_axi_arvalid = (state == ST_AR);
        m_axi_rready = 1'b1;
        protocol_fault = (state == ST_FAULT);
        burst_protocol_error = 1'b0;
        if (m_axi_rvalid) begin
            burst_protocol_error = (m_axi_rid != 6'd0) ||
                (m_axi_rlast != (received_beats + 5'd1 == burst_beats));
        end
    end

    always_ff @(posedge clk) begin
        if (rst) begin
            state <= ST_IDLE;
            cache_base <= 32'd0;
            cache_length <= 8'd0;
            cache_valid <= 1'b0;
            request_address <= 32'd0;
            request_region_begin <= 32'd0;
            request_region_end <= 32'd0;
            burst_base <= 32'd0;
            burst_beats <= 5'd1;
            received_beats <= 5'd0;
            burst_narrow <= 1'b0;
            response_byte <= 8'd0;
            response_error <= 1'b0;
            cancel_pending <= 1'b0;
            invalidate_pending <= 1'b0;
        end else begin
            if (cache_invalidate) begin
                cache_valid <= 1'b0;
                if (state != ST_IDLE) invalidate_pending <= 1'b1;
            end

            if (cancel && (state == ST_AR || state == ST_R || state == ST_RESP)) begin
                cancel_pending <= 1'b1;
                if (state == ST_RESP) begin
                    state <= ST_IDLE;
                    cache_valid <= 1'b0;
                    cancel_pending <= 1'b0;
                end
            end
            if (cache_invalidate && state == ST_RESP) begin
                state <= ST_IDLE;
                cache_valid <= 1'b0;
                invalidate_pending <= 1'b0;
            end

            case (state)
                ST_IDLE: begin
                    cancel_pending <= 1'b0;
                    if (req_valid && req_ready) begin
                        invalidate_pending <= 1'b0;
                        request_address <= req_addr;
                        request_region_begin <= region_begin;
                        request_region_end <= region_end;
                        response_error <= 1'b0;
                        if ((region_begin >= region_end) ||
                            (req_addr < region_begin) || (req_addr >= region_end)) begin
                            response_error <= 1'b1;
                            response_byte <= 8'd0;
                            state <= ST_RESP;
                        end else if (!cache_invalidate && cache_valid && (req_addr >= cache_base) &&
                                     (req_addr < cache_base + {24'd0, cache_length})) begin
                            response_byte <= cache_bytes[req_addr - cache_base];
                            state <= ST_RESP;
                        end else begin
                            cache_valid <= 1'b0;
                            if ((aligned_address >= region_begin) &&
                                (aligned_end_ext <= {1'b0, selected_limit})) begin
                                burst_base <= aligned_address;
                                burst_beats <= (available_beats > 16) ? 5'd16 : available_beats[4:0];
                                burst_narrow <= 1'b0;
                            end else begin
                                burst_base <= req_addr;
                                burst_beats <= 5'd1;
                                burst_narrow <= 1'b1;
                            end
                            received_beats <= 5'd0;
                            state <= ST_AR;
                        end
                    end
                end
                ST_AR: begin
                    if (m_axi_arvalid && m_axi_arready) begin
                        state <= ST_R;
                    end
                end
                ST_R: begin
                    if (m_axi_rvalid) begin
                        if (burst_protocol_error) begin
                            cache_valid <= 1'b0;
                            state <= ST_FAULT;
                        end else if (m_axi_rresp != 2'b00) begin
                            cache_valid <= 1'b0;
                            response_error <= 1'b1;
                            if (m_axi_rlast) begin
                                if (cancel || cancel_pending || cache_invalidate || invalidate_pending) begin
                                    state <= ST_IDLE;
                                    cache_valid <= 1'b0;
                                    cancel_pending <= 1'b0;
                                    invalidate_pending <= 1'b0;
                                end else begin
                                    state <= ST_RESP;
                                end
                            end else begin
                                received_beats <= received_beats + 5'd1;
                            end
                        end else begin
                            if (m_axi_arsize == 3'd0) begin
                                cache_base <= request_address;
                                cache_bytes[0] <= m_axi_rdata[8*request_address[2:0] +: 8];
                                cache_length <= 8'd1;
                            end else begin
                                cache_base <= burst_base;
                                for (integer byte_lane = 0; byte_lane < 8; byte_lane++) begin
                                    cache_bytes[received_beats*8 + byte_lane] <=
                                        m_axi_rdata[byte_lane*8 +: 8];
                                end
                                cache_length <= {received_beats, 3'b000} + 8'd8;
                            end
                            if (m_axi_rlast) begin
                                if (!cancel_pending && !cancel && !invalidate_pending && !cache_invalidate) begin
                                    if (m_axi_arsize == 3'd0)
                                        response_byte <= m_axi_rdata[8*request_address[2:0] +: 8];
                                    else if (request_cache_offset[31:3] == received_beats)
                                        response_byte <= m_axi_rdata[8*request_cache_offset[2:0] +: 8];
                                    else
                                        response_byte <= cache_bytes[request_cache_offset[6:0]];
                                    state <= ST_RESP;
                                    cache_valid <= !response_error && !invalidate_pending && !cache_invalidate;
                                    invalidate_pending <= 1'b0;
                                end else begin
                                    state <= ST_IDLE;
                                    cache_valid <= 1'b0;
                                    cancel_pending <= 1'b0;
                                    invalidate_pending <= 1'b0;
                                end
                            end else begin
                                received_beats <= received_beats + 5'd1;
                            end
                        end
                    end
                end
                ST_RESP: begin
                    if (rsp_valid && rsp_ready) state <= ST_IDLE;
                end
                ST_FAULT: begin
                    cache_valid <= 1'b0;
                end
                default: state <= ST_FAULT;
            endcase
        end
    end
endmodule
