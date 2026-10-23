`timescale 1ns/1ps

module s4b_preproc_frame #(
    parameter logic [31:0] OUT_WIDTH = 32'd416,
    parameter logic [31:0] OUT_HEIGHT = 32'd416
) (
    input  logic         clk,
    input  logic         rst_n,
    input  logic         start_valid,
    output logic         start_ready,
    input  logic         abort,
    input  logic [31:0]  source_width,
    input  logic [31:0]  source_height,
    input  logic [31:0]  stride_bytes,
    input  logic [31:0]  logical_bytes,
    input  logic [31:0]  storage_bytes,
    input  logic [31:0]  raw_capacity_bytes,
    input  logic [31:0]  resized_width,
    input  logic [31:0]  resized_height,
    input  logic [31:0]  pad_left,
    input  logic [31:0]  pad_top,
    input  logic [31:0]  raw_base,
    input  logic [31:0]  xgeom_base,
    input  logic [31:0]  ygeom_base,
    input  logic [31:0]  tensor_base,
    input  logic [31:0]  session_id,
    input  logic [31:0]  frame_id,
    output logic         busy,
    output logic         done_valid,
    input  logic         done_ready,
    output logic [31:0]  done_session_id,
    output logic [31:0]  done_frame_id,
    output logic         error_valid,
    input  logic         error_ready,
    output logic [3:0]   error_code,
    output logic [31:0]  error_session_id,
    output logic [31:0]  error_frame_id,
    output logic [31:0]  error_address,
    output logic         fault_isolated,
    output logic         mem_req_valid,
    input  logic         mem_req_ready,
    output logic         mem_req_write,
    output logic [31:0]  mem_req_addr,
    output logic [63:0]  mem_req_wdata,
    output logic [7:0]   mem_req_wstrb,
    input  logic         mem_rsp_valid,
    output logic         mem_rsp_ready,
    input  logic [63:0]  mem_rsp_rdata,
    input  logic         mem_rsp_error
);
    localparam logic [63:0] OUT_WIDTH_U64 = {32'd0, OUT_WIDTH};
    localparam logic [63:0] OUT_HEIGHT_U64 = {32'd0, OUT_HEIGHT};
    localparam logic [63:0] OUT_BYTES_U64 = OUT_WIDTH_U64 * OUT_HEIGHT_U64 * 64'd3;
    localparam logic [63:0] MAX_ADDRESS_END = 64'h0000000100000000;
    localparam logic [62:0] FP64_ONE_MAG = 63'h3ff0000000000000;
    localparam logic [62:0] FP64_MIN_WEIGHT_MAG = 63'h3ca0000000000000;

    localparam logic [3:0] ERR_DESCRIPTOR = 4'd1;
    localparam logic [3:0] ERR_ADDRESS = 4'd2;
    localparam logic [3:0] ERR_OVERLAP = 4'd3;
    localparam logic [3:0] ERR_GEOMETRY = 4'd4;
    localparam logic [3:0] ERR_RAW_READ = 4'd5;
    localparam logic [3:0] ERR_TENSOR_WRITE = 4'd6;
    localparam logic [3:0] ERR_PIXEL = 4'd7;
    localparam logic [3:0] ERR_ABORT = 4'd8;
    localparam logic [3:0] ERR_PROTOCOL = 4'd9;

    typedef enum logic [3:0] {
        ST_IDLE,
        ST_GEOM_REQ,
        ST_GEOM_WAIT,
        ST_NEXT_BYTE,
        ST_RAW_PREP,
        ST_RAW_REQ,
        ST_RAW_WAIT,
        ST_PIXEL_SEND,
        ST_PIXEL_WAIT,
        ST_APPEND_BYTE,
        ST_TENSOR_REQ,
        ST_TENSOR_WAIT,
        ST_DRAIN,
        ST_DONE,
        ST_ERROR,
        ST_STICKY
    } state_t;

    state_t state_q;
    logic [31:0] source_width_q;
    logic [31:0] source_height_q;
    logic [31:0] stride_bytes_q;
    logic [31:0] storage_bytes_q;
    logic [31:0] resized_width_q;
    logic [31:0] resized_height_q;
    logic [31:0] pad_left_q;
    logic [31:0] pad_top_q;
    logic [31:0] raw_base_q;
    logic [31:0] xgeom_base_q;
    logic [31:0] ygeom_base_q;
    logic [31:0] tensor_base_q;
    logic [31:0] session_id_q;
    logic [31:0] frame_id_q;

    logic [31:0] geom_x_i0 [0:OUT_WIDTH-1];
    logic [31:0] geom_x_i1 [0:OUT_WIDTH-1];
    logic [63:0] geom_x_w0 [0:OUT_WIDTH-1];
    logic [63:0] geom_x_w1 [0:OUT_WIDTH-1];
    logic [31:0] geom_y_i0 [0:OUT_HEIGHT-1];
    logic [31:0] geom_y_i1 [0:OUT_HEIGHT-1];
    logic [63:0] geom_y_w0 [0:OUT_HEIGHT-1];
    logic [63:0] geom_y_w1 [0:OUT_HEIGHT-1];

    logic table_axis_q;
    logic [31:0] table_index_q;
    logic [1:0] table_word_q;
    logic [31:0] table_i0_q;
    logic [31:0] table_i1_q;
    logic [63:0] table_w0_q;

    logic [31:0] output_x_q;
    logic [31:0] output_y_q;
    logic [1:0] channel_q;
    logic [31:0] linear_index_q;
    logic [2:0] pack_count_q;
    logic [63:0] pack_word_q;
    logic [63:0] tensor_word_data_q;
    logic [31:0] tensor_word_addr_q;
    logic last_tensor_word_q;
    logic [7:0] append_byte_q;

    logic [31:0] current_x_index_q;
    logic [31:0] current_y_index_q;
    logic [2:0] sample_index_q;
    logic [31:0] raw_word_addr_q;
    logic [2:0] raw_byte_offset_q;
    logic [7:0] p00_q;
    logic [7:0] p01_q;
    logic [7:0] p10_q;
    logic [7:0] p11_q;
    logic [31:0] last_request_addr_q;

    logic mem_pending_q;
    logic response_hold_q;
    logic abort_pending_q;
    logic frame_complete_q;
    logic [3:0] fault_code_q;
    logic [31:0] fault_address_q;
    logic fault_isolated_q;

    logic pixel_in_valid;
    logic pixel_in_ready;
    logic pixel_busy;
    logic pixel_out_valid;
    logic pixel_error_valid;
    logic [7:0] pixel_out_q;
    logic [2:0] pixel_error_code;
    logic [63:0] raw_byte_address_comb;
    logic [31:0] sample_x_comb;
    logic [31:0] sample_y_comb;
    logic [63:0] append_word_comb;
    logic request_fire;
    logic response_fire;
    logic unexpected_response;
    logic [63:0] descriptor_stride_calc;
    logic [63:0] descriptor_logical_calc;
    logic [63:0] descriptor_storage_calc;
    logic [95:0] descriptor_logical_wide;
    logic [95:0] descriptor_storage_wide;
    logic [63:0] raw_region_length;
    logic [63:0] x_region_length;
    logic [63:0] y_region_length;
    logic [63:0] tensor_region_length;
    logic [63:0] raw_region_end;
    logic [63:0] x_region_end;
    logic [63:0] y_region_end;
    logic [63:0] tensor_region_end;
    logic [3:0] descriptor_error_code;
    logic pixel_out_ready;
    logic pixel_error_ready;

    function automatic logic weight_supported(input logic [63:0] value);
        logic [10:0] exponent;
        logic [62:0] magnitude;
        begin
            exponent = value[62:52];
            magnitude = value[62:0];
            if (magnitude == 63'd0) begin
                weight_supported = !value[63];
            end else if (value[63] || exponent == 11'd0 || exponent == 11'h7ff ||
                         magnitude < FP64_MIN_WEIGHT_MAG || magnitude > FP64_ONE_MAG) begin
                weight_supported = 1'b0;
            end else begin
                weight_supported = 1'b1;
            end
        end
    endfunction

    initial begin : parameter_guard
        if (OUT_WIDTH == 0 || OUT_HEIGHT == 0 || OUT_BYTES_U64 == 0 || OUT_BYTES_U64[2:0] != 3'd0)
            $fatal(1, "输出CHW字节数必须为正且可完整打包为64位字");
    end

    always_comb begin : descriptor_validation
        descriptor_stride_calc = {32'd0, source_width} * 64'd3;
        descriptor_logical_wide = {32'd0, descriptor_stride_calc} * {64'd0, source_height};
        descriptor_storage_wide = (descriptor_logical_wide + 96'd7) & 96'hfffffffffffffffffffffff8;
        descriptor_logical_calc = descriptor_logical_wide[63:0];
        descriptor_storage_calc = descriptor_storage_wide[63:0];
        raw_region_length = {32'd0, raw_capacity_bytes};
        x_region_length = OUT_WIDTH_U64 * 64'd24;
        y_region_length = OUT_HEIGHT_U64 * 64'd24;
        tensor_region_length = OUT_BYTES_U64;
        raw_region_end = {32'd0, raw_base} + raw_region_length;
        x_region_end = {32'd0, xgeom_base} + x_region_length;
        y_region_end = {32'd0, ygeom_base} + y_region_length;
        tensor_region_end = {32'd0, tensor_base} + tensor_region_length;
        descriptor_error_code = 4'd0;

        if (source_width == 0 || source_height == 0 || resized_width == 0 || resized_height == 0 ||
            resized_width > OUT_WIDTH || resized_height > OUT_HEIGHT ||
            raw_capacity_bytes < storage_bytes ||
            pad_left != ((OUT_WIDTH - resized_width) >> 1) ||
            pad_top != ((OUT_HEIGHT - resized_height) >> 1)) begin
            descriptor_error_code = ERR_DESCRIPTOR;
        end else if (descriptor_stride_calc > 64'h00000000ffffffff ||
                     descriptor_logical_wide > 96'h0000000000000000ffffffff ||
                     descriptor_storage_wide > 96'h0000000000000000ffffffff ||
                     raw_base[2:0] != 3'd0 || xgeom_base[2:0] != 3'd0 ||
                     ygeom_base[2:0] != 3'd0 || tensor_base[2:0] != 3'd0 ||
                     raw_region_end > MAX_ADDRESS_END || x_region_end > MAX_ADDRESS_END ||
                     y_region_end > MAX_ADDRESS_END || tensor_region_end > MAX_ADDRESS_END) begin
            descriptor_error_code = ERR_ADDRESS;
        end else if (stride_bytes != descriptor_stride_calc[31:0] ||
                     logical_bytes != descriptor_logical_calc[31:0] ||
                     storage_bytes != descriptor_storage_calc[31:0]) begin
            descriptor_error_code = ERR_DESCRIPTOR;
        end else if (({32'd0, raw_base} < x_region_end && {32'd0, xgeom_base} < raw_region_end) ||
                     ({32'd0, raw_base} < y_region_end && {32'd0, ygeom_base} < raw_region_end) ||
                     ({32'd0, raw_base} < tensor_region_end && {32'd0, tensor_base} < raw_region_end) ||
                     ({32'd0, xgeom_base} < y_region_end && {32'd0, ygeom_base} < x_region_end) ||
                     ({32'd0, xgeom_base} < tensor_region_end && {32'd0, tensor_base} < x_region_end) ||
                     ({32'd0, ygeom_base} < tensor_region_end && {32'd0, tensor_base} < y_region_end)) begin
            descriptor_error_code = ERR_OVERLAP;
        end
    end

    always_comb begin : datapath_decode
        start_ready = (state_q == ST_IDLE) && !fault_isolated_q && !done_valid && !error_valid && !mem_pending_q;
        busy = (state_q != ST_IDLE);
        fault_isolated = fault_isolated_q;
        done_session_id = session_id_q;
        done_frame_id = frame_id_q;
        error_session_id = session_id_q;
        error_frame_id = frame_id_q;
        error_code = fault_code_q;
        error_address = fault_address_q;

        mem_req_valid = 1'b0;
        mem_req_write = 1'b0;
        mem_req_addr = 32'd0;
        mem_req_wdata = 64'd0;
        mem_req_wstrb = 8'd0;
        case (state_q)
            ST_GEOM_REQ: begin
                mem_req_valid = 1'b1;
                mem_req_addr = (table_axis_q ? ygeom_base_q : xgeom_base_q) +
                               table_index_q * 32'd24 + {table_word_q, 3'b000};
            end
            ST_RAW_REQ: begin
                mem_req_valid = 1'b1;
                mem_req_addr = raw_word_addr_q;
            end
            ST_TENSOR_REQ: begin
                mem_req_valid = 1'b1;
                mem_req_write = 1'b1;
                mem_req_addr = tensor_word_addr_q;
                mem_req_wdata = tensor_word_data_q;
                mem_req_wstrb = 8'hff;
            end
            default: begin
                mem_req_valid = 1'b0;
            end
        endcase
        mem_rsp_ready = mem_pending_q && !response_hold_q;
        request_fire = mem_req_valid && mem_req_ready;
        response_fire = mem_rsp_valid && mem_rsp_ready;
        unexpected_response = mem_rsp_valid && !mem_pending_q && !request_fire;

        pixel_in_valid = (state_q == ST_PIXEL_SEND) && !abort && !abort_pending_q;
        pixel_out_ready = 1'b1;
        pixel_error_ready = 1'b1;

        sample_x_comb = 32'd0;
        sample_y_comb = 32'd0;
        case (sample_index_q)
            3'd0: begin
                sample_x_comb = geom_x_i0[current_x_index_q];
                sample_y_comb = geom_y_i0[current_y_index_q];
            end
            3'd1: begin
                sample_x_comb = geom_x_i1[current_x_index_q];
                sample_y_comb = geom_y_i0[current_y_index_q];
            end
            3'd2: begin
                sample_x_comb = geom_x_i0[current_x_index_q];
                sample_y_comb = geom_y_i1[current_y_index_q];
            end
            default: begin
                sample_x_comb = geom_x_i1[current_x_index_q];
                sample_y_comb = geom_y_i1[current_y_index_q];
            end
        endcase
        raw_byte_address_comb = {32'd0, raw_base_q} +
                                {32'd0, sample_y_comb} * {32'd0, stride_bytes_q} +
                                ({32'd0, sample_x_comb} * 64'd3) + {62'd0, channel_q};
        append_word_comb = pack_word_q |
                           ({56'd0, append_byte_q} << (pack_count_q * 8));
    end

    s4b_preproc_pixel pixel_core (
        .clk(clk),
        .rst_n(rst_n),
        .in_valid(pixel_in_valid),
        .in_ready(pixel_in_ready),
        .p00(p00_q),
        .p01(p01_q),
        .p10(p10_q),
        .p11(p11_q),
        .wx0(geom_x_w0[current_x_index_q]),
        .wx1(geom_x_w1[current_x_index_q]),
        .wy0(geom_y_w0[current_y_index_q]),
        .wy1(geom_y_w1[current_y_index_q]),
        .busy(pixel_busy),
        .out_valid(pixel_out_valid),
        .out_ready(pixel_out_ready),
        .out_q(pixel_out_q),
        .error_valid(pixel_error_valid),
        .error_ready(pixel_error_ready),
        .error_code(pixel_error_code)
    );

    always_ff @(posedge clk or negedge rst_n) begin : frame_state_machine
        if (!rst_n) begin
            state_q <= ST_IDLE;
            source_width_q <= 32'd0;
            source_height_q <= 32'd0;
            stride_bytes_q <= 32'd0;
            storage_bytes_q <= 32'd0;
            resized_width_q <= 32'd0;
            resized_height_q <= 32'd0;
            pad_left_q <= 32'd0;
            pad_top_q <= 32'd0;
            raw_base_q <= 32'd0;
            xgeom_base_q <= 32'd0;
            ygeom_base_q <= 32'd0;
            tensor_base_q <= 32'd0;
            session_id_q <= 32'd0;
            frame_id_q <= 32'd0;
            table_axis_q <= 1'b0;
            table_index_q <= 32'd0;
            table_word_q <= 2'd0;
            table_i0_q <= 32'd0;
            table_i1_q <= 32'd0;
            table_w0_q <= 64'd0;
            output_x_q <= 32'd0;
            output_y_q <= 32'd0;
            channel_q <= 2'd0;
            linear_index_q <= 32'd0;
            pack_count_q <= 3'd0;
            pack_word_q <= 64'd0;
            tensor_word_data_q <= 64'd0;
            tensor_word_addr_q <= 32'd0;
            last_tensor_word_q <= 1'b0;
            append_byte_q <= 8'd0;
            current_x_index_q <= 32'd0;
            current_y_index_q <= 32'd0;
            sample_index_q <= 3'd0;
            raw_word_addr_q <= 32'd0;
            raw_byte_offset_q <= 3'd0;
            p00_q <= 8'd0;
            p01_q <= 8'd0;
            p10_q <= 8'd0;
            p11_q <= 8'd0;
            last_request_addr_q <= 32'd0;
            mem_pending_q <= 1'b0;
            response_hold_q <= 1'b0;
            abort_pending_q <= 1'b0;
            frame_complete_q <= 1'b0;
            fault_code_q <= 4'd0;
            fault_address_q <= 32'd0;
            fault_isolated_q <= 1'b0;
            done_valid <= 1'b0;
            error_valid <= 1'b0;
        end else begin
            if (request_fire) begin
                mem_pending_q <= 1'b1;
                response_hold_q <= 1'b1;
                last_request_addr_q <= mem_req_addr;
            end
            if (response_hold_q && !request_fire)
                response_hold_q <= 1'b0;
            if (response_fire) begin
                mem_pending_q <= 1'b0;
                response_hold_q <= 1'b0;
            end

            if (abort && state_q != ST_IDLE && state_q != ST_DONE &&
                state_q != ST_ERROR && state_q != ST_STICKY) begin
                abort_pending_q <= 1'b1;
                if (fault_code_q == 4'd0 && fault_address_q == 32'd0)
                    fault_address_q <= mem_pending_q ? last_request_addr_q : tensor_word_addr_q;
                if (state_q == ST_NEXT_BYTE || state_q == ST_RAW_PREP ||
                    state_q == ST_PIXEL_SEND || state_q == ST_PIXEL_WAIT ||
                    state_q == ST_APPEND_BYTE || state_q == ST_DRAIN)
                    state_q <= ST_DRAIN;
            end

            case (state_q)
                ST_IDLE: begin
                    if (start_valid && start_ready) begin
                        session_id_q <= session_id;
                        frame_id_q <= frame_id;
                        done_valid <= 1'b0;
                        error_valid <= 1'b0;
                        fault_code_q <= 4'd0;
                        fault_address_q <= 32'd0;
                        abort_pending_q <= 1'b0;
                        frame_complete_q <= 1'b0;
                        if (descriptor_error_code != 4'd0) begin
                            fault_code_q <= descriptor_error_code;
                            fault_address_q <= (descriptor_error_code == ERR_OVERLAP) ? tensor_base : raw_base;
                            error_valid <= 1'b1;
                            state_q <= ST_ERROR;
                        end else begin
                            source_width_q <= source_width;
                            source_height_q <= source_height;
                            stride_bytes_q <= stride_bytes;
                            storage_bytes_q <= storage_bytes;
                            resized_width_q <= resized_width;
                            resized_height_q <= resized_height;
                            pad_left_q <= pad_left;
                            pad_top_q <= pad_top;
                            raw_base_q <= raw_base;
                            xgeom_base_q <= xgeom_base;
                            ygeom_base_q <= ygeom_base;
                            tensor_base_q <= tensor_base;
                            table_axis_q <= 1'b0;
                            table_index_q <= 32'd0;
                            table_word_q <= 2'd0;
                            tensor_word_addr_q <= tensor_base;
                            pack_count_q <= 3'd0;
                            pack_word_q <= 64'd0;
                            output_x_q <= 32'd0;
                            output_y_q <= 32'd0;
                            channel_q <= 2'd0;
                            linear_index_q <= 32'd0;
                            state_q <= ST_GEOM_REQ;
                        end
                    end
                end

                ST_GEOM_REQ: begin
                    if (request_fire)
                        state_q <= ST_GEOM_WAIT;
                end

                ST_GEOM_WAIT: begin
                    if (response_fire) begin
                        if (mem_rsp_error) begin
                            fault_code_q <= ERR_GEOMETRY;
                            fault_address_q <= last_request_addr_q;
                            state_q <= ST_DRAIN;
                        end else if (abort || abort_pending_q) begin
                            abort_pending_q <= 1'b1;
                            state_q <= ST_DRAIN;
                        end else begin
                            case (table_word_q)
                                2'd0: begin
                                    table_i0_q <= mem_rsp_rdata[31:0];
                                    table_i1_q <= mem_rsp_rdata[63:32];
                                    table_word_q <= 2'd1;
                                    state_q <= ST_GEOM_REQ;
                                end
                                2'd1: begin
                                    table_w0_q <= mem_rsp_rdata;
                                    table_word_q <= 2'd2;
                                    state_q <= ST_GEOM_REQ;
                                end
                                default: begin
                                    if ((!table_axis_q &&
                                         (table_i0_q >= source_width_q || table_i1_q >= source_width_q)) ||
                                        (table_axis_q &&
                                         (table_i0_q >= source_height_q || table_i1_q >= source_height_q)) ||
                                        !weight_supported(table_w0_q) || !weight_supported(mem_rsp_rdata)) begin
                                        fault_code_q <= ERR_GEOMETRY;
                                        fault_address_q <= last_request_addr_q;
                                        state_q <= ST_DRAIN;
                                    end else begin
                                        if (!table_axis_q) begin
                                            geom_x_i0[table_index_q] <= table_i0_q;
                                            geom_x_i1[table_index_q] <= table_i1_q;
                                            geom_x_w0[table_index_q] <= table_w0_q;
                                            geom_x_w1[table_index_q] <= mem_rsp_rdata;
                                        end else begin
                                            geom_y_i0[table_index_q] <= table_i0_q;
                                            geom_y_i1[table_index_q] <= table_i1_q;
                                            geom_y_w0[table_index_q] <= table_w0_q;
                                            geom_y_w1[table_index_q] <= mem_rsp_rdata;
                                        end
                                        table_word_q <= 2'd0;
                                        if (!table_axis_q && table_index_q + 1 >= resized_width_q) begin
                                            table_axis_q <= 1'b1;
                                            table_index_q <= 32'd0;
                                            state_q <= ST_GEOM_REQ;
                                        end else if (table_axis_q && table_index_q + 1 >= resized_height_q) begin
                                            output_x_q <= 32'd0;
                                            output_y_q <= 32'd0;
                                            channel_q <= 2'd0;
                                            linear_index_q <= 32'd0;
                                            pack_count_q <= 3'd0;
                                            pack_word_q <= 64'd0;
                                            state_q <= ST_NEXT_BYTE;
                                        end else begin
                                            table_index_q <= table_index_q + 1'b1;
                                            state_q <= ST_GEOM_REQ;
                                        end
                                    end
                                end
                            endcase
                        end
                    end
                end

                ST_NEXT_BYTE: begin
                    if (abort || abort_pending_q) begin
                        abort_pending_q <= 1'b1;
                        state_q <= ST_DRAIN;
                    end else if (output_x_q < pad_left_q || output_x_q >= pad_left_q + resized_width_q ||
                                 output_y_q < pad_top_q || output_y_q >= pad_top_q + resized_height_q) begin
                        append_byte_q <= 8'd64;
                        state_q <= ST_APPEND_BYTE;
                    end else begin
                        current_x_index_q <= output_x_q - pad_left_q;
                        current_y_index_q <= output_y_q - pad_top_q;
                        sample_index_q <= 3'd0;
                        state_q <= ST_RAW_PREP;
                    end
                end

                ST_RAW_PREP: begin
                    if (abort || abort_pending_q) begin
                        abort_pending_q <= 1'b1;
                        state_q <= ST_DRAIN;
                    end else if (raw_byte_address_comb[63:32] != 32'd0 ||
                                 raw_byte_address_comb < {32'd0, raw_base_q} ||
                                 ((raw_byte_address_comb & 64'hfffffffffffffff8) + 64'd8) >
                                     {32'd0, raw_base_q} + {32'd0, storage_bytes_q}) begin
                        fault_code_q <= ERR_GEOMETRY;
                        fault_address_q <= raw_byte_address_comb[31:0];
                        state_q <= ST_DRAIN;
                    end else begin
                        raw_word_addr_q <= {raw_byte_address_comb[31:3], 3'b000};
                        raw_byte_offset_q <= raw_byte_address_comb[2:0];
                        state_q <= ST_RAW_REQ;
                    end
                end

                ST_RAW_REQ: begin
                    if (request_fire)
                        state_q <= ST_RAW_WAIT;
                end

                ST_RAW_WAIT: begin
                    if (response_fire) begin
                        if (mem_rsp_error) begin
                            fault_code_q <= ERR_RAW_READ;
                            fault_address_q <= last_request_addr_q;
                            state_q <= ST_DRAIN;
                        end else if (abort || abort_pending_q) begin
                            abort_pending_q <= 1'b1;
                            state_q <= ST_DRAIN;
                        end else begin
                            case (sample_index_q)
                                3'd0: p00_q <= mem_rsp_rdata >> (raw_byte_offset_q * 8);
                                3'd1: p01_q <= mem_rsp_rdata >> (raw_byte_offset_q * 8);
                                3'd2: p10_q <= mem_rsp_rdata >> (raw_byte_offset_q * 8);
                                default: p11_q <= mem_rsp_rdata >> (raw_byte_offset_q * 8);
                            endcase
                            if (sample_index_q == 3'd3) begin
                                state_q <= ST_PIXEL_SEND;
                            end else begin
                                sample_index_q <= sample_index_q + 1'b1;
                                state_q <= ST_RAW_PREP;
                            end
                        end
                    end
                end

                ST_PIXEL_SEND: begin
                    if (pixel_in_valid && pixel_in_ready)
                        state_q <= ST_PIXEL_WAIT;
                end

                ST_PIXEL_WAIT: begin
                    if (pixel_error_valid) begin
                        fault_code_q <= ERR_PIXEL;
                        fault_address_q <= tensor_word_addr_q;
                        state_q <= ST_DRAIN;
                    end else if (pixel_out_valid && pixel_out_ready) begin
                        if (abort || abort_pending_q) begin
                            abort_pending_q <= 1'b1;
                            state_q <= ST_DRAIN;
                        end else begin
                            append_byte_q <= pixel_out_q;
                            state_q <= ST_APPEND_BYTE;
                        end
                    end
                end

                ST_APPEND_BYTE: begin
                    if (abort || abort_pending_q) begin
                        abort_pending_q <= 1'b1;
                        state_q <= ST_DRAIN;
                    end else begin
                        linear_index_q <= linear_index_q + 1'b1;
                        if (pack_count_q == 3'd7) begin
                            tensor_word_data_q <= append_word_comb;
                            tensor_word_addr_q <= tensor_base_q + linear_index_q - 32'd7;
                            last_tensor_word_q <= (linear_index_q == OUT_BYTES_U64 - 1);
                            pack_count_q <= 3'd0;
                            pack_word_q <= 64'd0;
                            state_q <= ST_TENSOR_REQ;
                        end else begin
                            pack_word_q <= append_word_comb;
                            pack_count_q <= pack_count_q + 1'b1;
                            if (output_x_q + 1 < OUT_WIDTH) begin
                                output_x_q <= output_x_q + 1'b1;
                            end else begin
                                output_x_q <= 32'd0;
                                if (output_y_q + 1 < OUT_HEIGHT) begin
                                    output_y_q <= output_y_q + 1'b1;
                                end else begin
                                    output_y_q <= 32'd0;
                                    if (channel_q < 2)
                                        channel_q <= channel_q + 1'b1;
                                end
                            end
                            state_q <= ST_NEXT_BYTE;
                        end
                    end
                end

                ST_TENSOR_REQ: begin
                    if (request_fire)
                        state_q <= ST_TENSOR_WAIT;
                end

                ST_TENSOR_WAIT: begin
                    if (response_fire) begin
                        if (mem_rsp_error) begin
                            fault_code_q <= ERR_TENSOR_WRITE;
                            fault_address_q <= last_request_addr_q;
                            state_q <= ST_DRAIN;
                        end else if (abort || abort_pending_q) begin
                            abort_pending_q <= 1'b1;
                            state_q <= ST_DRAIN;
                        end else if (last_tensor_word_q) begin
                            frame_complete_q <= 1'b1;
                            state_q <= ST_DRAIN;
                        end else begin
                            tensor_word_addr_q <= tensor_word_addr_q + 32'd8;
                            if (output_x_q + 1 < OUT_WIDTH) begin
                                output_x_q <= output_x_q + 1'b1;
                            end else begin
                                output_x_q <= 32'd0;
                                if (output_y_q + 1 < OUT_HEIGHT) begin
                                    output_y_q <= output_y_q + 1'b1;
                                end else begin
                                    output_y_q <= 32'd0;
                                    if (channel_q < 2)
                                        channel_q <= channel_q + 1'b1;
                                end
                            end
                            state_q <= ST_NEXT_BYTE;
                        end
                    end
                end

                ST_DRAIN: begin
                    if (!mem_pending_q && !pixel_busy) begin
                        if (fault_code_q != 4'd0 || abort || abort_pending_q) begin
                            if (fault_code_q == 4'd0)
                                fault_code_q <= ERR_ABORT;
                            error_valid <= 1'b1;
                            state_q <= ST_ERROR;
                        end else if (frame_complete_q) begin
                            frame_complete_q <= 1'b0;
                            done_valid <= 1'b1;
                            state_q <= ST_DONE;
                        end else begin
                            fault_code_q <= ERR_PROTOCOL;
                            fault_address_q <= last_request_addr_q;
                            fault_isolated_q <= 1'b1;
                            error_valid <= 1'b1;
                            state_q <= ST_STICKY;
                        end
                    end
                end

                ST_DONE: begin
                    if (done_valid && done_ready) begin
                        done_valid <= 1'b0;
                        state_q <= ST_IDLE;
                    end
                end

                ST_ERROR: begin
                    if (error_valid && error_ready) begin
                        error_valid <= 1'b0;
                        if (fault_code_q == ERR_PROTOCOL || fault_isolated_q) begin
                            fault_isolated_q <= 1'b1;
                            state_q <= ST_STICKY;
                        end else begin
                            fault_code_q <= 4'd0;
                            fault_address_q <= 32'd0;
                            abort_pending_q <= 1'b0;
                            state_q <= ST_IDLE;
                        end
                    end
                end

                ST_STICKY: begin
                    if (error_valid && error_ready)
                        error_valid <= 1'b0;
                end

                default: begin
                    fault_code_q <= ERR_PROTOCOL;
                    fault_address_q <= last_request_addr_q;
                    fault_isolated_q <= 1'b1;
                    error_valid <= 1'b1;
                    state_q <= ST_STICKY;
                end
            endcase

            if (response_fire && state_q != ST_GEOM_WAIT && state_q != ST_RAW_WAIT &&
                state_q != ST_TENSOR_WAIT) begin
                fault_code_q <= ERR_PROTOCOL;
                fault_address_q <= last_request_addr_q;
                fault_isolated_q <= 1'b1;
                error_valid <= 1'b1;
                state_q <= ST_STICKY;
            end else if (unexpected_response) begin
                fault_code_q <= ERR_PROTOCOL;
                fault_address_q <= 32'd0;
                fault_isolated_q <= 1'b1;
                error_valid <= 1'b1;
                state_q <= ST_STICKY;
            end
        end
    end
endmodule
