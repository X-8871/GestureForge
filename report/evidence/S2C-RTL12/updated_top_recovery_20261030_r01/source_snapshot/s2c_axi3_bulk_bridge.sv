`timescale 1ns/1ps
// S2C 内部bulk事务桥：写数据先完整收齐，物理访问按AXI3边界分段。
module s2c_axi3_bulk_bridge #(
    parameter bit ENABLE_BULK = 1'b0
) (
    input  logic        clk,
    input  logic        cold_reset,
    input  logic        run_enable,
    input  logic        cancel,
    input  logic        clear_safe,
    input  logic [63:0] run_epoch,

    input  logic        bulk_cmd_valid,
    output logic        bulk_cmd_ready,
    input  logic        bulk_cmd_write,
    input  logic [31:0] bulk_cmd_addr,
    input  logic [7:0]  bulk_cmd_bytes,
    input  logic        bulk_wvalid,
    output logic        bulk_wready,
    input  logic [7:0]  bulk_wdata,
    output logic        bulk_rvalid,
    input  logic        bulk_rready,
    output logic [7:0]  bulk_rdata,
    output logic        bulk_done_valid,
    input  logic        bulk_done_ready,
    output logic [2:0]  bulk_done_error,

    output logic [5:0]  m_axi_arid,
    output logic [5:0]  m_axi_awid,
    output logic [5:0]  m_axi_wid,
    output logic [31:0] m_axi_araddr,
    output logic [31:0] m_axi_awaddr,
    output logic [3:0]  m_axi_arlen,
    output logic [3:0]  m_axi_awlen,
    output logic [2:0]  m_axi_arsize,
    output logic [2:0]  m_axi_awsize,
    output logic [1:0]  m_axi_arburst,
    output logic [1:0]  m_axi_awburst,
    output logic [1:0]  m_axi_arlock,
    output logic [1:0]  m_axi_awlock,
    output logic [3:0]  m_axi_arcache,
    output logic [3:0]  m_axi_awcache,
    output logic [2:0]  m_axi_arprot,
    output logic [2:0]  m_axi_awprot,
    output logic [3:0]  m_axi_arqos,
    output logic [3:0]  m_axi_awqos,
    output logic        m_axi_arvalid,
    input  logic        m_axi_arready,
    input  logic [5:0]  m_axi_rid,
    input  logic [63:0] m_axi_rdata,
    input  logic [1:0]  m_axi_rresp,
    input  logic        m_axi_rlast,
    input  logic        m_axi_rvalid,
    output logic        m_axi_rready,
    output logic        m_axi_awvalid,
    input  logic        m_axi_awready,
    output logic        m_axi_wvalid,
    output logic [63:0] m_axi_wdata,
    output logic [7:0]  m_axi_wstrb,
    output logic        m_axi_wlast,
    input  logic        m_axi_wready,
    input  logic [5:0]  m_axi_bid,
    input  logic [1:0]  m_axi_bresp,
    input  logic        m_axi_bvalid,
    output logic        m_axi_bready,

    output logic        ledger_empty,
    output logic [63:0] ledger_epoch,
    output logic        recovery_required,
    output logic        protocol_isolated,
    output logic        first_fault_valid,
    output logic [7:0]  first_fault_code,
    output logic [31:0] first_fault_address,
    output logic        fault_event_valid,
    output logic [7:0]  fault_event_code,
    output logic [31:0] fault_event_address,
    output logic        clear_rejected,
    output logic [9:0]  axi_progress,
    output logic [9:0]  axi_progress_next,
    output logic        ledger_empty_next,
    output logic [1:0]  fault_event_resp,
    output logic        fault_event_write,
    output logic        fault_event_protocol,
    output logic        fault_event_address_valid,
    output logic [31:0] fault_event_physical_address
);
    localparam logic [2:0] NONE = 3'd0;
    localparam logic [2:0] BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] BAD_RANGE = 3'd2;

    typedef enum logic [3:0] {
        ST_IDLE,
        ST_WRITE_COLLECT,
        ST_READ_PREP,
        ST_READ_AR,
        ST_READ_R,
        ST_READ_DELIVER,
        ST_WRITE_PREP,
        ST_WRITE_AXI,
        ST_DONE,
        ST_LOCKED
    } state_t;

    typedef struct packed {
        state_t state;
        logic write_command;
        logic [31:0] logical_address;
        logic [32:0] physical_start;
        logic [32:0] region_begin;
        logic [32:0] region_end;
        logic [7:0] command_bytes;
        logic [7:0] write_count;
        logic [7:0] segment_offset;
        logic [7:0] segment_bytes;
        logic [4:0] segment_beats;
        logic [4:0] read_beat_index;
        logic [4:0] write_beat_index;
        logic [7:0] deliver_index;
        logic [63:0] epoch;
        logic ar_accepted;
        logic aw_accepted;
        logic b_seen;
        logic [1:0] saved_bresp;
        logic cancelled;
        logic recover;
        logic isolated;
        logic first_valid;
        logic [7:0] first_code;
        logic [31:0] first_address;
        logic [2:0] done_error;
    } state_data_t;

    state_data_t q, d;
    logic [7:0] byte_buffer [0:127];
    logic guard_allowed;
    logic [31:0] guard_physical_address;
    logic [32:0] guard_region_begin, guard_region_end;
    logic [2:0] guard_error;
    logic [32:0] command_physical_end;
    logic [32:0] current_segment_physical;
    logic [32:0] current_read_logical;
    logic [32:0] current_write_logical;
    logic command_parameter_error;
    logic command_range_error;
    logic command_accept;
    logic cancel_now;
    logic epoch_mismatch;
    logic r_frame_match;
    logic r_protocol_event;
    logic r_response_error;
    logic b_prior_w_complete;
    logic b_match;
    logic b_protocol_event;
    logic b_response_error;
    logic read_buffer_store;
    logic ar_handshake;
    logic aw_handshake;
    logic w_handshake;
    logic b_handshake;
    logic all_w_complete;
    logic all_aw_complete;
    logic all_b_complete;
    logic final_segment;
    logic [4:0] page_segment_beats;
    logic [7:0] page_segment_bytes;
    integer write_byte_index;

    function automatic logic [4:0] segment_beat_count(
        input logic [32:0] address,
        input logic [7:0] remaining_bytes
    );
        logic [12:0] bytes_to_page_end;
        logic [9:0] page_beats;
        logic [4:0] remaining_beats;
        logic [9:0] remaining_beats_wide;
        begin
            bytes_to_page_end = 13'd4096 - {1'b0, address[11:0]};
            page_beats = bytes_to_page_end[12:3];
            remaining_beats = remaining_bytes[7:3];
            remaining_beats_wide = {5'd0, remaining_beats};
            if (page_beats < remaining_beats_wide)
                segment_beat_count = page_beats[4:0];
            else
                segment_beat_count = remaining_beats;
        end
    endfunction

    s2b_request_guard guard (
        .mem_write(bulk_cmd_write),
        .mem_addr(bulk_cmd_addr),
        .mem_rstrb(bulk_cmd_write ? 4'd0 : 4'd1),
        .mem_wstrb(bulk_cmd_write ? 4'd1 : 4'd0),
        .request_allowed(guard_allowed),
        .physical_addr(guard_physical_address),
        .region_begin_phys(guard_region_begin),
        .region_end_phys_exclusive(guard_region_end),
        .error_code(guard_error)
    );

    always_comb begin
        command_physical_end = {1'b0, guard_physical_address} +
                               {25'd0, bulk_cmd_bytes};
        command_parameter_error = (bulk_cmd_addr[2:0] != 3'b000) ||
                                  (bulk_cmd_bytes < 8'd8) ||
                                  (bulk_cmd_bytes > 8'd128) ||
                                  (bulk_cmd_bytes[2:0] != 3'b000);
        command_range_error = !guard_allowed ||
            (command_physical_end < {1'b0, guard_physical_address}) ||
            ({1'b0, guard_physical_address} < guard_region_begin) ||
            (command_physical_end > guard_region_end) ||
            ({1'b0, guard_physical_address} < 33'h010000000) ||
            (command_physical_end > 33'h012000000);
    end

    always_comb begin
        epoch_mismatch = (q.state != ST_IDLE) && (q.state != ST_LOCKED) &&
                         (run_epoch != q.epoch);
        current_segment_physical = q.physical_start +
                                   {25'd0, q.segment_offset};
        current_read_logical = {1'b0, q.logical_address} +
            {25'd0, q.segment_offset} + {25'd0, q.read_beat_index, 3'b000};
        current_write_logical = {1'b0, q.logical_address} +
                                {25'd0, q.segment_offset};

        r_frame_match = (q.state == ST_READ_R) && q.ar_accepted &&
            (m_axi_rid == 6'd0) &&
            (m_axi_rlast == (q.read_beat_index + 5'd1 == q.segment_beats));
        r_protocol_event = m_axi_rvalid &&
            (!r_frame_match || (m_axi_rresp == 2'b01));
        r_response_error = m_axi_rvalid && r_frame_match && m_axi_rresp[1];

        b_prior_w_complete = (q.state == ST_WRITE_AXI) &&
                             (q.write_beat_index == q.segment_beats);
        b_match = m_axi_bvalid && b_prior_w_complete && !q.b_seen &&
                  (m_axi_bid == 6'd0);
        b_protocol_event = m_axi_bvalid &&
            (!b_match || (m_axi_bresp == 2'b01));
        b_response_error = b_match && m_axi_bresp[1];
        fault_event_valid = 1'b0;
        fault_event_code = 8'd0;
        fault_event_address = 32'd0;
        fault_event_resp = 2'b00;
        fault_event_write = 1'b0;
        fault_event_protocol = 1'b0;
        fault_event_address_valid = 1'b0;
        fault_event_physical_address = 32'd0;
        if (ENABLE_BULK && !q.isolated) begin
            if (r_protocol_event) begin
                fault_event_valid = 1'b1;
                fault_event_code = 8'd11;
                fault_event_protocol = 1'b1;
                fault_event_resp = m_axi_rresp;
                fault_event_address_valid = (q.state == ST_READ_R);
                fault_event_address = current_read_logical[31:0];
                fault_event_physical_address =
                    current_segment_physical[31:0] +
                    {25'd0, q.read_beat_index, 3'b000};
            end else if (b_protocol_event) begin
                fault_event_valid = 1'b1;
                fault_event_code = 8'd11;
                fault_event_protocol = 1'b1;
                fault_event_resp = m_axi_bresp;
                fault_event_write = 1'b1;
                fault_event_address_valid = (q.state == ST_WRITE_AXI);
                fault_event_address = current_write_logical[31:0];
                fault_event_physical_address = current_segment_physical[31:0];
            end else if (epoch_mismatch) begin
                fault_event_valid = 1'b1;
                fault_event_code = 8'd6;
                fault_event_protocol = 1'b1;
                fault_event_address_valid = 1'b1;
                fault_event_address = q.logical_address;
                fault_event_physical_address = q.physical_start[31:0];
            end else if (r_response_error) begin
                fault_event_valid = 1'b1;
                fault_event_code = m_axi_rresp[0] ? 8'd10 : 8'd9;
                fault_event_resp = m_axi_rresp;
                fault_event_address_valid = 1'b1;
                fault_event_address = current_read_logical[31:0];
                fault_event_physical_address =
                    current_segment_physical[31:0] +
                    {25'd0, q.read_beat_index, 3'b000};
            end else if (b_response_error) begin
                fault_event_valid = 1'b1;
                fault_event_code = m_axi_bresp[0] ? 8'd10 : 8'd9;
                fault_event_resp = m_axi_bresp;
                fault_event_write = 1'b1;
                fault_event_address_valid = 1'b1;
                fault_event_address = current_write_logical[31:0];
                fault_event_physical_address = current_segment_physical[31:0];
            end
        end

        cancel_now = cancel || !run_enable || epoch_mismatch ||
                     fault_event_valid;
        read_buffer_store = ENABLE_BULK && (q.state == ST_READ_R) &&
            m_axi_rvalid && r_frame_match && (m_axi_rresp == 2'b00) &&
            !cancel_now && !q.cancelled && !q.isolated;
        bulk_cmd_ready = ENABLE_BULK && (q.state == ST_IDLE) &&
                         run_enable && !cancel && !clear_safe &&
                         !q.recover && !q.isolated &&
                         !fault_event_valid;
        command_accept = bulk_cmd_valid && bulk_cmd_ready;
        bulk_wready = ENABLE_BULK && (q.state == ST_WRITE_COLLECT) &&
                      !cancel_now && !q.cancelled &&
                      (q.write_count < q.command_bytes);
        bulk_rvalid = ENABLE_BULK && (q.state == ST_READ_DELIVER) &&
                      !cancel_now && !q.cancelled && !q.isolated &&
                      (q.deliver_index < q.command_bytes);
        bulk_rdata = byte_buffer[q.deliver_index];
        bulk_done_valid = ENABLE_BULK && (q.state == ST_DONE) &&
                          !cancel_now && !q.cancelled && !q.isolated;
        bulk_done_error = q.done_error;

        m_axi_arid = 6'd0;
        m_axi_awid = 6'd0;
        m_axi_wid = 6'd0;
        m_axi_araddr = current_segment_physical[31:0];
        m_axi_awaddr = current_segment_physical[31:0];
        m_axi_arlen = (q.segment_beats == 5'd0) ? 4'd0 :
                      (q.segment_beats[3:0] - 4'd1);
        m_axi_awlen = (q.segment_beats == 5'd0) ? 4'd0 :
                      (q.segment_beats[3:0] - 4'd1);
        m_axi_arsize = 3'd3;
        m_axi_awsize = 3'd3;
        m_axi_arburst = 2'b01;
        m_axi_awburst = 2'b01;
        m_axi_arlock = 2'b00;
        m_axi_awlock = 2'b00;
        m_axi_arcache = 4'd0;
        m_axi_awcache = 4'd0;
        m_axi_arprot = 3'd0;
        m_axi_awprot = 3'd0;
        m_axi_arqos = 4'd0;
        m_axi_awqos = 4'd0;
        m_axi_arvalid = ENABLE_BULK && (q.state == ST_READ_AR);
        m_axi_rready = ENABLE_BULK;
        m_axi_awvalid = ENABLE_BULK && (q.state == ST_WRITE_AXI) &&
                        !q.aw_accepted;
        m_axi_wvalid = ENABLE_BULK && (q.state == ST_WRITE_AXI) &&
                       (q.write_beat_index < q.segment_beats);
        m_axi_wdata = 64'd0;
        for (integer lane = 0; lane < 8; lane++) begin
            write_byte_index = q.segment_offset +
                               (q.write_beat_index * 8) + lane;
            if ((write_byte_index >= 0) && (write_byte_index < 128))
                m_axi_wdata[8*lane +: 8] =
                    byte_buffer[write_byte_index];
        end
        m_axi_wstrb = m_axi_wvalid ? 8'hff : 8'd0;
        m_axi_wlast = m_axi_wvalid &&
                      (q.write_beat_index + 5'd1 == q.segment_beats);
        m_axi_bready = ENABLE_BULK;

        ledger_empty = (q.state == ST_IDLE) && !q.isolated;
        ledger_epoch = q.epoch;
        recovery_required = q.recover;
        protocol_isolated = q.isolated;
        first_fault_valid = q.first_valid;
        first_fault_code = q.first_code;
        first_fault_address = q.first_address;
        clear_rejected = clear_safe &&
            (run_enable || !ledger_empty || q.isolated || cancel ||
             fault_event_valid);

        ar_handshake = m_axi_arvalid && m_axi_arready;
        aw_handshake = m_axi_awvalid && m_axi_awready;
        w_handshake = m_axi_wvalid && m_axi_wready;
        b_handshake = b_match;
        all_w_complete = (q.write_beat_index == q.segment_beats);
        all_aw_complete = q.aw_accepted || aw_handshake;
        all_b_complete = q.b_seen || b_handshake;
        final_segment = ({1'b0, q.segment_offset} +
                         {25'd0, q.segment_bytes} >=
                         {1'b0, q.command_bytes});
        page_segment_beats = segment_beat_count(
            q.physical_start + {25'd0, q.segment_offset},
            q.command_bytes - q.segment_offset);
        page_segment_bytes = {page_segment_beats, 3'b000};

        axi_progress = {
            q.b_seen,
            (q.state == ST_DONE) || (q.state == ST_READ_DELIVER),
            (q.state == ST_WRITE_AXI) && !q.b_seen,
            (q.state == ST_WRITE_AXI) &&
                (q.write_beat_index != 5'd0),
            (q.state == ST_WRITE_AXI) &&
                (q.write_beat_index < q.segment_beats),
            q.aw_accepted,
            (q.state == ST_WRITE_AXI) && !q.aw_accepted,
            (q.state == ST_READ_R) && q.ar_accepted,
            q.ar_accepted,
            (q.state == ST_READ_AR)
        };
    end

    always_comb begin
        d = q;

        if (clear_safe && !clear_rejected) begin
            d.recover = 1'b0;
            d.first_valid = 1'b0;
            d.first_code = 8'd0;
            d.first_address = 32'd0;
        end

        case (q.state)
            ST_IDLE: begin
                if (command_accept) begin
                    d.write_command = bulk_cmd_write;
                    d.logical_address = bulk_cmd_addr;
                    d.physical_start = {1'b0, guard_physical_address};
                    d.region_begin = guard_region_begin;
                    d.region_end = guard_region_end;
                    d.command_bytes = bulk_cmd_bytes;
                    d.write_count = 8'd0;
                    d.segment_offset = 8'd0;
                    d.segment_bytes = 8'd0;
                    d.segment_beats = 5'd0;
                    d.read_beat_index = 5'd0;
                    d.write_beat_index = 5'd0;
                    d.deliver_index = 8'd0;
                    d.epoch = run_epoch;
                    d.ar_accepted = 1'b0;
                    d.aw_accepted = 1'b0;
                    d.b_seen = 1'b0;
                    d.saved_bresp = 2'b00;
                    d.cancelled = 1'b0;
                    d.done_error = NONE;
                    if (command_parameter_error ||
                        (guard_error == BAD_ARGUMENT)) begin
                        d.done_error = BAD_ARGUMENT;
                        d.state = ST_DONE;
                    end else if (command_range_error ||
                                 (guard_error != NONE)) begin
                        d.done_error = BAD_RANGE;
                        d.state = ST_DONE;
                    end else if (bulk_cmd_write) begin
                        d.state = ST_WRITE_COLLECT;
                    end else begin
                        d.state = ST_READ_PREP;
                    end
                end
            end

            ST_WRITE_COLLECT: begin
                if (cancel_now || q.cancelled) begin
                    d.write_count = 8'd0;
                    d.cancelled = 1'b1;
                    d.recover = 1'b1;
                    d.state = q.isolated ? ST_LOCKED : ST_IDLE;
                end else if (bulk_wvalid && bulk_wready) begin
                    d.write_count = q.write_count + 8'd1;
                    if (q.write_count + 8'd1 == q.command_bytes) begin
                        d.segment_offset = 8'd0;
                        d.segment_beats = page_segment_beats;
                        d.segment_bytes = page_segment_bytes;
                        d.write_beat_index = 5'd0;
                        d.aw_accepted = 1'b0;
                        d.b_seen = 1'b0;
                        d.state = ST_WRITE_PREP;
                    end
                end
            end

            ST_READ_PREP: begin
                if (cancel_now || q.cancelled) begin
                    d.cancelled = 1'b1;
                    d.recover = 1'b1;
                    d.state = q.isolated ? ST_LOCKED : ST_IDLE;
                end else begin
                    d.segment_beats = page_segment_beats;
                    d.segment_bytes = page_segment_bytes;
                    d.read_beat_index = 5'd0;
                    d.ar_accepted = 1'b0;
                    d.state = ST_READ_AR;
                end
            end

            ST_READ_AR: begin
                if (cancel_now || q.cancelled) begin
                    d.cancelled = 1'b1;
                    d.recover = 1'b1;
                end
                if (ar_handshake) begin
                    d.ar_accepted = 1'b1;
                    d.read_beat_index = 5'd0;
                    d.state = ST_READ_R;
                end
            end

            ST_READ_R: begin
                if (cancel_now || q.cancelled) begin
                    d.cancelled = 1'b1;
                    if (cancel || !run_enable || epoch_mismatch)
                        d.recover = 1'b1;
                end
                if (m_axi_rvalid && r_frame_match) begin
                    if (m_axi_rresp[1]) begin
                        d.cancelled = 1'b1;
                        d.recover = 1'b1;
                    end
                    if (q.read_beat_index + 5'd1 == q.segment_beats) begin
                        d.ar_accepted = 1'b0;
                        d.read_beat_index = 5'd0;
                        if (q.isolated || fault_event_protocol ||
                            epoch_mismatch) begin
                            d.state = ST_LOCKED;
                        end else if (cancel_now || q.cancelled ||
                                     (m_axi_rresp != 2'b00)) begin
                            d.cancelled = 1'b1;
                            d.recover = 1'b1;
                            d.state = ST_IDLE;
                        end else if (!final_segment) begin
                            d.segment_offset =
                                q.segment_offset + q.segment_bytes;
                            d.state = ST_READ_PREP;
                        end else begin
                            d.deliver_index = 8'd0;
                            d.state = ST_READ_DELIVER;
                        end
                    end else begin
                        d.read_beat_index = q.read_beat_index + 5'd1;
                    end
                end
            end

            ST_READ_DELIVER: begin
                if (cancel_now || q.cancelled || q.isolated) begin
                    d.cancelled = 1'b1;
                    d.recover = 1'b1;
                    d.state = q.isolated ? ST_LOCKED : ST_IDLE;
                end else if (bulk_rvalid && bulk_rready) begin
                    if (q.deliver_index + 8'd1 == q.command_bytes) begin
                        d.done_error = NONE;
                        d.state = ST_DONE;
                    end else begin
                        d.deliver_index = q.deliver_index + 8'd1;
                    end
                end
            end

            ST_WRITE_PREP: begin
                if (cancel_now || q.cancelled) begin
                    d.cancelled = 1'b1;
                    d.recover = 1'b1;
                    d.state = q.isolated ? ST_LOCKED : ST_IDLE;
                end else begin
                    d.segment_beats = page_segment_beats;
                    d.segment_bytes = page_segment_bytes;
                    d.write_beat_index = 5'd0;
                    d.aw_accepted = 1'b0;
                    d.b_seen = 1'b0;
                    d.saved_bresp = 2'b00;
                    d.state = ST_WRITE_AXI;
                end
            end

            ST_WRITE_AXI: begin
                if (cancel_now || q.cancelled) begin
                    d.cancelled = 1'b1;
                    if (cancel || !run_enable || epoch_mismatch)
                        d.recover = 1'b1;
                end
                if (aw_handshake) d.aw_accepted = 1'b1;
                if (w_handshake)
                    d.write_beat_index = q.write_beat_index + 5'd1;
                if (b_handshake) begin
                    d.b_seen = 1'b1;
                    d.saved_bresp = m_axi_bresp;
                    if (m_axi_bresp[1]) begin
                        d.cancelled = 1'b1;
                        d.recover = 1'b1;
                    end
                end
                if (all_aw_complete && all_w_complete && all_b_complete) begin
                    d.aw_accepted = 1'b0;
                    d.b_seen = 1'b0;
                    d.write_beat_index = 5'd0;
                    if (q.isolated || fault_event_protocol ||
                        epoch_mismatch) begin
                        d.state = ST_LOCKED;
                    end else if (cancel_now || q.cancelled ||
                                 (m_axi_bvalid && b_match &&
                                  (m_axi_bresp != 2'b00)) ||
                                 (q.b_seen && q.saved_bresp != 2'b00)) begin
                        d.cancelled = 1'b1;
                        d.recover = 1'b1;
                        d.state = ST_IDLE;
                    end else if (!final_segment) begin
                        d.segment_offset =
                            q.segment_offset + q.segment_bytes;
                        d.state = ST_WRITE_PREP;
                    end else begin
                        d.done_error = NONE;
                        d.state = ST_DONE;
                    end
                end
            end

            ST_DONE: begin
                if (cancel_now || q.cancelled || q.isolated) begin
                    d.cancelled = 1'b1;
                    d.recover = 1'b1;
                    d.state = q.isolated ? ST_LOCKED : ST_IDLE;
                end else if (bulk_done_valid && bulk_done_ready) begin
                    if (q.done_error != NONE) begin
                        d.recover = 1'b1;
                        if (!q.first_valid) begin
                            d.first_valid = 1'b1;
                            d.first_code = {5'd0, q.done_error};
                            d.first_address = q.logical_address;
                        end
                    end
                    d.state = ST_IDLE;
                end
            end

            ST_LOCKED: begin
                d.state = ST_LOCKED;
            end

            default: begin
                d.state = ST_LOCKED;
                d.isolated = 1'b1;
                d.recover = 1'b1;
            end
        endcase

        if (ENABLE_BULK && cancel &&
            (q.state != ST_IDLE) && !q.isolated)
            d.recover = 1'b1;

        if (fault_event_valid) begin
            d.recover = 1'b1;
            if (fault_event_protocol) d.isolated = 1'b1;
            if (!q.first_valid) begin
                d.first_valid = 1'b1;
                d.first_code = fault_event_code;
                d.first_address = fault_event_address;
            end
            if (fault_event_protocol &&
                (q.state == ST_IDLE || q.state == ST_WRITE_COLLECT ||
                 q.state == ST_READ_PREP || q.state == ST_WRITE_PREP ||
                 q.state == ST_READ_DELIVER || q.state == ST_DONE))
                d.state = ST_LOCKED;
        end

        if (ENABLE_BULK && epoch_mismatch) begin
            d.cancelled = 1'b1;
            d.recover = 1'b1;
            d.isolated = 1'b1;
            if (q.state == ST_WRITE_COLLECT || q.state == ST_READ_PREP ||
                q.state == ST_WRITE_PREP || q.state == ST_READ_DELIVER ||
                q.state == ST_DONE)
                d.state = ST_LOCKED;
        end

        axi_progress_next = {
            d.b_seen,
            (d.state == ST_DONE) || (d.state == ST_READ_DELIVER),
            (d.state == ST_WRITE_AXI) && !d.b_seen,
            (d.state == ST_WRITE_AXI) &&
                (d.write_beat_index != 5'd0),
            (d.state == ST_WRITE_AXI) &&
                (d.write_beat_index < d.segment_beats),
            d.aw_accepted,
            (d.state == ST_WRITE_AXI) && !d.aw_accepted,
            (d.state == ST_READ_R) && d.ar_accepted,
            d.ar_accepted,
            (d.state == ST_READ_AR)
        };
        ledger_empty_next = (d.state == ST_IDLE) && !d.isolated;
    end

    always_ff @(posedge clk) begin
        if (cold_reset) begin
            q <= '0;
            q.state <= ST_IDLE;
        end else begin
            q <= d;
            if (ENABLE_BULK && q.state == ST_WRITE_COLLECT &&
                bulk_wvalid && bulk_wready)
                byte_buffer[q.write_count] <= bulk_wdata;
            if (read_buffer_store) begin
                for (integer lane = 0; lane < 8; lane++) begin
                    byte_buffer[q.segment_offset +
                        (q.read_beat_index * 8) + lane] <=
                        m_axi_rdata[8*lane +: 8];
                end
            end
        end
    end
endmodule
