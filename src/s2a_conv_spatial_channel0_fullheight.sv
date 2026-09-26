// layer36 通道0的完整26行空间卷积 pilot。
// 单 outstanding G0 字节存储器读取输入和权重，复用 T30 tile16 执行 MAC，随后量化并写出676字节。
module s2a_conv_spatial_channel0_fullheight (
    input  logic          clk,
    input  logic          rst,
    input  logic          abort,

    input  logic          start_valid,
    output logic          start_ready,
    output logic          busy,

    output logic          mem_valid,
    input  logic          mem_ready,
    output logic          mem_write,
    output logic [31:0]   mem_addr,
    output logic [31:0]   mem_wdata,
    output logic [3:0]    mem_rstrb,
    output logic [3:0]    mem_wstrb,
    input  logic [31:0]   mem_rdata,
    input  logic [2:0]    mem_error_code,

    output logic          raw_valid,
    input  logic          raw_ready,
    output logic [4:0]    raw_y,
    output logic [4:0]    raw_x,
    output logic signed [31:0] raw_accumulator,

    output logic          result_valid,
    input  logic          result_ready,
    output logic [2:0]    result_error_code
);
    localparam logic [31:0] FEATURE_BASE = 32'd27966080;
    localparam logic [31:0] WEIGHT_BYTE_BASE = 32'h00100000 + 32'd5895420;
    localparam logic [31:0] OUTPUT_BASE = 32'd28139136;
    localparam logic [2:0] ERROR_NONE = 3'd0;
    localparam logic [2:0] ERROR_BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] ERROR_BAD_RANGE = 3'd2;
    localparam logic [2:0] ERROR_INTERNAL = 3'd6;
    localparam logic [2:0] ERROR_ACCUMULATOR_OVERFLOW = 3'd7;

    localparam logic [3:0] ST_IDLE = 4'd0;
    localparam logic [3:0] ST_TILE_START = 4'd1;
    localparam logic [3:0] ST_WEIGHT_READ = 4'd2;
    localparam logic [3:0] ST_FEATURE_READ = 4'd3;
    localparam logic [3:0] ST_FEED_TILE = 4'd4;
    localparam logic [3:0] ST_WAIT_TILE = 4'd5;
    localparam logic [3:0] ST_EMIT_RAW = 4'd6;
    localparam logic [3:0] ST_OUTPUT_WRITE = 4'd7;
    localparam logic [3:0] ST_RESULT = 4'd8;

    logic [3:0] state;
    logic [4:0] row_y;
    logic       tile_index;
    logic [7:0] k_index;
    logic [2:0] feature_word_index;
    logic [3:0] lane_index;
    logic [127:0] feature_lanes;
    logic signed [7:0] shared_weight;
    logic [7:0] overlap_cache_low [0:255];
    logic [7:0] overlap_cache_high [0:255];
    logic [511:0] raw_tile;
    logic [7:0] quantized_tile [0:15];
    logic [31:0] selected_feature_byte_address;
    logic [31:0] selected_feature_word_address;
    logic [31:0] row_feature_base;
    logic [31:0] tile_feature_base;
    logic [31:0] output_byte_address;
    logic [31:0] weight_byte_address;
    logic [2:0] last_feature_word_index;
    logic [3:0] selected_output_strobe;
    logic [31:0] selected_output_shift;
    logic [2:0] mapped_memory_error;
    logic [2:0] mapped_core_error;

    logic core_start_valid;
    logic core_start_ready;
    logic core_input_valid;
    logic core_input_ready;
    logic core_result_valid;
    logic core_result_ready;
    logic core_abort;
    logic [511:0] core_accumulators;
    logic [2:0] core_error_code;
    logic core_busy;

    integer seq_lane;
    integer seq_k;
    integer feature_lane_index;

    function automatic logic signed [7:0] requantize_linear(
        input logic signed [31:0] accumulator
    );
        logic [31:0] magnitude;
        logic [63:0] product;
        logic [63:0] rounded_magnitude;
        logic signed [63:0] signed_value;
        begin
            if (accumulator[31]) begin
                magnitude = ~$unsigned(accumulator) + 32'd1;
            end else begin
                magnitude = $unsigned(accumulator);
            end
            product = {32'd0, magnitude} * 64'd4521539;
            rounded_magnitude = (product + (64'd1 << 32)) >> 33;
            if (accumulator[31]) begin
                signed_value = -$signed({1'b0, rounded_magnitude});
            end else begin
                signed_value = $signed({1'b0, rounded_magnitude});
            end
            if (signed_value > 64'sd127) begin
                requantize_linear = 8'sd127;
            end else if (signed_value < -64'sd127) begin
                requantize_linear = -8'sd127;
            end else begin
                requantize_linear = signed_value[7:0];
            end
        end
    endfunction

    always_comb begin
        row_feature_base = FEATURE_BASE +
            ({27'd0, k_index} * 32'd676) + ({27'd0, row_y} * 32'd26);
        tile_feature_base = row_feature_base + (tile_index ? 32'd16 : 32'd0);
        selected_feature_byte_address = tile_feature_base +
            ({29'd0, feature_word_index} * 32'd4);
        if (!tile_index && row_y[0]) begin
            selected_feature_byte_address = row_feature_base - 32'd2 +
                ({29'd0, feature_word_index} * 32'd4);
        end else if (tile_index && row_y[0]) begin
            selected_feature_byte_address = row_feature_base + 32'd18 +
                ({29'd0, feature_word_index} * 32'd4);
        end
        selected_feature_word_address = {selected_feature_byte_address[31:2], 2'b00};
        weight_byte_address = WEIGHT_BYTE_BASE + {24'd0, k_index};
        output_byte_address = OUTPUT_BASE + ({27'd0, row_y} * 32'd26) +
            (tile_index ? 32'd16 : 32'd0) + {28'd0, lane_index};
        selected_output_strobe = 4'b0001 << output_byte_address[1:0];
        selected_output_shift = {30'd0, output_byte_address[1:0]} * 32'd8;
        last_feature_word_index = 3'd0;
        if (!tile_index) begin
            last_feature_word_index = row_y[0] ? 3'd4 : 3'd3;
        end else begin
            last_feature_word_index = row_y[0] ? 3'd1 : 3'd2;
        end

        mapped_memory_error = ERROR_INTERNAL;
        if ((mem_error_code == ERROR_BAD_ARGUMENT) ||
            (mem_error_code == ERROR_BAD_RANGE) ||
            (mem_error_code == ERROR_INTERNAL)) begin
            mapped_memory_error = mem_error_code;
        end else if (mem_error_code == ERROR_NONE) begin
            mapped_memory_error = ERROR_NONE;
        end
        mapped_core_error = ERROR_INTERNAL;
        if ((core_error_code == ERROR_BAD_ARGUMENT) ||
            (core_error_code == ERROR_BAD_RANGE) ||
            (core_error_code == ERROR_INTERNAL) ||
            (core_error_code == ERROR_ACCUMULATOR_OVERFLOW)) begin
            mapped_core_error = core_error_code;
        end else if (core_error_code == ERROR_NONE) begin
            mapped_core_error = ERROR_NONE;
        end

        mem_valid = ((state == ST_WEIGHT_READ) ||
                     (state == ST_FEATURE_READ) ||
                     (state == ST_OUTPUT_WRITE)) && !rst && !abort;
        mem_write = (state == ST_OUTPUT_WRITE);
        mem_addr = 32'd0;
        mem_wdata = 32'd0;
        mem_rstrb = 4'b0000;
        mem_wstrb = 4'b0000;
        if (state == ST_WEIGHT_READ) begin
            mem_addr = {weight_byte_address[31:2], 2'b00};
            mem_rstrb = 4'b0001 << weight_byte_address[1:0];
        end else if (state == ST_FEATURE_READ) begin
            mem_addr = selected_feature_word_address;
            if (!tile_index && row_y[0] && (feature_word_index == 3'd0)) begin
                mem_rstrb = 4'b1100;
            end else if (tile_index && !row_y[0] &&
                         (feature_word_index == 3'd2)) begin
                mem_rstrb = 4'b0011;
            end else begin
                mem_rstrb = 4'b1111;
            end
        end else if (state == ST_OUTPUT_WRITE) begin
            mem_addr = {output_byte_address[31:2], 2'b00};
            mem_wdata = {24'd0, quantized_tile[lane_index]} << selected_output_shift;
            mem_wstrb = selected_output_strobe;
        end

        start_ready = (state == ST_IDLE) && !rst && !abort;
        busy = (state != ST_IDLE);
        raw_valid = (state == ST_EMIT_RAW) && !rst && !abort;
        raw_y = row_y;
        raw_x = (tile_index ? 5'd16 : 5'd0) + {1'b0, lane_index};
        raw_accumulator = $signed(raw_tile[lane_index * 32 +: 32]);
        result_valid = (state == ST_RESULT) && !rst && !abort;
        core_start_valid = (state == ST_TILE_START) && !rst && !abort;
        core_input_valid = (state == ST_FEED_TILE) && !rst && !abort;
        core_result_ready = (state == ST_WAIT_TILE) && !rst && !abort;
        core_abort = rst || abort || result_valid;
    end

    s2a_conv_spatial_tile16 u_tile16 (
        .clk(clk),
        .rst(rst),
        .abort(core_abort),
        .start_valid(core_start_valid),
        .start_ready(core_start_ready),
        .start_k(13'd256),
        .start_bias(-32'sd40),
        .input_valid(core_input_valid),
        .input_ready(core_input_ready),
        .feature_lanes(feature_lanes),
        .weight_data(shared_weight),
        .result_valid(core_result_valid),
        .result_ready(core_result_ready),
        .lane_accumulators(core_accumulators),
        .error_code(core_error_code),
        .busy(core_busy)
    );

    always_ff @(posedge clk) begin
        if (rst) begin
            state <= ST_IDLE;
            row_y <= 5'd0;
            tile_index <= 1'b0;
            k_index <= 8'd0;
            feature_word_index <= 3'd0;
            lane_index <= 4'd0;
            feature_lanes <= 128'd0;
            shared_weight <= 8'sd0;
            raw_tile <= 512'd0;
            result_error_code <= ERROR_NONE;
            for (seq_lane = 0; seq_lane < 16; seq_lane = seq_lane + 1) begin
                quantized_tile[seq_lane] <= 8'd0;
            end
            for (seq_k = 0; seq_k < 256; seq_k = seq_k + 1) begin
                overlap_cache_low[seq_k] <= 8'd0;
                overlap_cache_high[seq_k] <= 8'd0;
            end
        end else if (abort) begin
            state <= ST_IDLE;
            row_y <= 5'd0;
            tile_index <= 1'b0;
            k_index <= 8'd0;
            feature_word_index <= 3'd0;
            lane_index <= 4'd0;
            feature_lanes <= 128'd0;
            shared_weight <= 8'sd0;
            raw_tile <= 512'd0;
            result_error_code <= ERROR_NONE;
            for (seq_lane = 0; seq_lane < 16; seq_lane = seq_lane + 1) begin
                quantized_tile[seq_lane] <= 8'd0;
            end
            for (seq_k = 0; seq_k < 256; seq_k = seq_k + 1) begin
                overlap_cache_low[seq_k] <= 8'd0;
                overlap_cache_high[seq_k] <= 8'd0;
            end
        end else begin
            case (state)
                ST_IDLE: begin
                    if (start_valid && start_ready) begin
                        row_y <= 5'd0;
                        tile_index <= 1'b0;
                        k_index <= 8'd0;
                        feature_word_index <= 3'd0;
                        lane_index <= 4'd0;
                        result_error_code <= ERROR_NONE;
                        state <= ST_TILE_START;
                    end
                end

                ST_TILE_START: begin
                    if (core_start_valid && core_start_ready) begin
                        k_index <= 8'd0;
                        state <= ST_WEIGHT_READ;
                    end
                end

                ST_WEIGHT_READ: begin
                    if (mem_valid && mem_ready) begin
                        if (mem_error_code != ERROR_NONE) begin
                            result_error_code <= mapped_memory_error;
                            state <= ST_RESULT;
                        end else begin
                            shared_weight <= $signed(
                                mem_rdata[weight_byte_address[1:0] * 8 +: 8]
                            );
                            feature_lanes <= 128'd0;
                            if (tile_index && row_y[0]) begin
                                feature_lanes[7:0] <= overlap_cache_low[k_index];
                                feature_lanes[15:8] <= overlap_cache_high[k_index];
                            end
                            feature_word_index <= 3'd0;
                            state <= ST_FEATURE_READ;
                        end
                    end
                end

                ST_FEATURE_READ: begin
                    if (mem_valid && mem_ready) begin
                        if (mem_error_code != ERROR_NONE) begin
                            result_error_code <= mapped_memory_error;
                            state <= ST_RESULT;
                        end else begin
                            for (seq_lane = 0; seq_lane < 4; seq_lane = seq_lane + 1) begin
                                if (mem_rstrb[seq_lane]) begin
                                    if (((selected_feature_word_address + seq_lane) >=
                                         tile_feature_base) &&
                                        ((selected_feature_word_address + seq_lane) <
                                         (tile_feature_base + 32'd16))) begin
                                        feature_lane_index =
                                            selected_feature_word_address + seq_lane -
                                            tile_feature_base;
                                        feature_lanes[feature_lane_index * 8 +: 8] <=
                                            mem_rdata[seq_lane * 8 +: 8];
                                    end else if (!tile_index && row_y[0] &&
                                                 (feature_word_index == 3'd4) &&
                                                 ((selected_feature_word_address + seq_lane) ==
                                                  (tile_feature_base + 32'd16))) begin
                                        overlap_cache_low[k_index] <=
                                            mem_rdata[seq_lane * 8 +: 8];
                                    end else if (!tile_index && row_y[0] &&
                                                 (feature_word_index == 3'd4) &&
                                                 ((selected_feature_word_address + seq_lane) ==
                                                  (tile_feature_base + 32'd17))) begin
                                        overlap_cache_high[k_index] <=
                                            mem_rdata[seq_lane * 8 +: 8];
                                    end
                                end
                            end
                            if (feature_word_index == last_feature_word_index) begin
                                state <= ST_FEED_TILE;
                            end else begin
                                feature_word_index <= feature_word_index + 3'd1;
                            end
                        end
                    end
                end

                ST_FEED_TILE: begin
                    if (core_input_valid && core_input_ready) begin
                        if (k_index == 8'd255) begin
                            state <= ST_WAIT_TILE;
                        end else begin
                            k_index <= k_index + 8'd1;
                            state <= ST_WEIGHT_READ;
                        end
                    end
                end

                ST_WAIT_TILE: begin
                    if (core_result_valid && core_result_ready) begin
                        if (core_error_code != ERROR_NONE) begin
                            result_error_code <= mapped_core_error;
                            state <= ST_RESULT;
                        end else begin
                            raw_tile <= core_accumulators;
                            lane_index <= 4'd0;
                            state <= ST_EMIT_RAW;
                        end
                    end
                end

                ST_EMIT_RAW: begin
                    if (raw_valid && raw_ready) begin
                        quantized_tile[lane_index] <= requantize_linear(
                            $signed(raw_tile[lane_index * 32 +: 32])
                        );
                        if ((!tile_index && (lane_index == 4'd15)) ||
                            (tile_index && (lane_index == 4'd9))) begin
                            lane_index <= 4'd0;
                            state <= ST_OUTPUT_WRITE;
                        end else begin
                            lane_index <= lane_index + 4'd1;
                        end
                    end
                end

                ST_OUTPUT_WRITE: begin
                    if (mem_valid && mem_ready) begin
                        if (mem_error_code != ERROR_NONE) begin
                            result_error_code <= mapped_memory_error;
                            state <= ST_RESULT;
                        end else if ((!tile_index && (lane_index == 4'd15)) ||
                                     (tile_index && (lane_index == 4'd9))) begin
                            lane_index <= 4'd0;
                            if (!tile_index) begin
                                tile_index <= 1'b1;
                                k_index <= 8'd0;
                                state <= ST_TILE_START;
                            end else if (row_y == 5'd25) begin
                                result_error_code <= ERROR_NONE;
                                state <= ST_RESULT;
                            end else begin
                                row_y <= row_y + 5'd1;
                                tile_index <= 1'b0;
                                k_index <= 8'd0;
                                state <= ST_TILE_START;
                            end
                        end else begin
                            lane_index <= lane_index + 4'd1;
                        end
                    end
                end

                ST_RESULT: begin
                    if (result_valid && result_ready) begin
                        result_error_code <= ERROR_NONE;
                        state <= ST_IDLE;
                    end
                end

                default: begin
                    result_error_code <= ERROR_INTERNAL;
                    state <= ST_RESULT;
                end
            endcase
        end
    end
endmodule
