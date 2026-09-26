// layer36 通道0、row0 的 G0 字节 strobe feeder pilot。
// 本模块只验证 feature/weight 读地址、停顿与 INT8 tile16 的连接，不写输出 buffer。
module s2a_conv_spatial_row0_pilot (
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

    output logic          tile_result_valid,
    input  logic          tile_result_ready,
    output logic          tile_result_index,
    output logic [15:0]   tile_valid_mask,
    output logic [511:0]  tile_raw_accumulators,
    output logic          tile_result_last,

    output logic          error_valid,
    input  logic          error_ready,
    output logic [2:0]    error_code
);
    localparam logic [31:0] FEATURE_BASE = 32'd27966080;
    localparam logic [31:0] WEIGHT_BYTE_BASE = 32'h00100000 + 32'd5895420;
    localparam logic [2:0] ERROR_NONE = 3'd0;
    localparam logic [2:0] ERROR_BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] ERROR_BAD_RANGE = 3'd2;
    localparam logic [2:0] ERROR_INTERNAL = 3'd6;

    localparam logic [3:0] ST_IDLE = 4'd0;
    localparam logic [3:0] ST_TILE_START = 4'd1;
    localparam logic [3:0] ST_WEIGHT_READ = 4'd2;
    localparam logic [3:0] ST_FEATURE_READ = 4'd3;
    localparam logic [3:0] ST_FEED_TILE = 4'd4;
    localparam logic [3:0] ST_WAIT_TILE = 4'd5;
    localparam logic [3:0] ST_EMIT_TILE_A = 4'd6;
    localparam logic [3:0] ST_EMIT_TILE_B = 4'd7;
    localparam logic [3:0] ST_ERROR = 4'd8;

    logic [3:0] state;
    logic        tile_index;
    logic [8:0]  k_index;
    logic [1:0]  feature_word_index;
    logic [127:0] feature_lanes;
    logic signed [7:0] shared_weight;
    logic [31:0] weight_byte_address;
    logic [31:0] feature_byte_address;
    logic [3:0]  core_state_unused;
    logic        core_start_valid;
    logic        core_start_ready;
    logic        core_input_valid;
    logic        core_input_ready;
    logic        core_result_valid;
    logic        core_result_ready;
    logic        core_abort;
    logic [511:0] core_accumulators;
    logic [2:0]   core_error_code;
    logic         core_busy;
    logic [31:0]  raw_result [0:25];
    integer comb_lane;
    integer seq_lane;
    integer feature_lane_index;

    always_comb begin
        weight_byte_address = WEIGHT_BYTE_BASE + {23'd0, k_index};
        feature_byte_address = FEATURE_BASE +
            ({23'd0, k_index} * 32'd676) +
            (tile_index ? 32'd16 : 32'd0) +
            ({30'd0, feature_word_index} * 32'd4);

        mem_valid = ((state == ST_WEIGHT_READ) || (state == ST_FEATURE_READ)) &&
                    !rst && !abort;
        mem_write = 1'b0;
        mem_addr = 32'd0;
        mem_wdata = 32'd0;
        mem_rstrb = 4'b0000;
        mem_wstrb = 4'b0000;
        if (state == ST_WEIGHT_READ) begin
            mem_addr = {weight_byte_address[31:2], 2'b00};
            mem_rstrb = 4'b0001 << weight_byte_address[1:0];
        end else if (state == ST_FEATURE_READ) begin
            mem_addr = {feature_byte_address[31:2], 2'b00};
            if (tile_index && (feature_word_index == 2'd2)) begin
                mem_rstrb = 4'b0011;
            end else begin
                mem_rstrb = 4'b1111;
            end
        end

        start_ready = (state == ST_IDLE) && !rst && !abort;
        busy = (state != ST_IDLE);
        tile_result_valid = ((state == ST_EMIT_TILE_A) ||
                             (state == ST_EMIT_TILE_B)) && !rst && !abort;
        tile_result_index = (state == ST_EMIT_TILE_B);
        tile_valid_mask = 16'd0;
        tile_raw_accumulators = 512'd0;
        tile_result_last = (state == ST_EMIT_TILE_B);
        if (state == ST_EMIT_TILE_A) begin
            tile_valid_mask = 16'hffff;
            for (comb_lane = 0; comb_lane < 16; comb_lane = comb_lane + 1) begin
                tile_raw_accumulators[comb_lane * 32 +: 32] = raw_result[comb_lane];
            end
        end else if (state == ST_EMIT_TILE_B) begin
            tile_valid_mask = 16'h03ff;
            for (comb_lane = 0; comb_lane < 10; comb_lane = comb_lane + 1) begin
                tile_raw_accumulators[comb_lane * 32 +: 32] = raw_result[16 + comb_lane];
            end
        end
        error_valid = (state == ST_ERROR) && !rst && !abort;
        core_start_valid = (state == ST_TILE_START) && !rst && !abort;
        core_input_valid = (state == ST_FEED_TILE) && !rst && !abort;
        core_result_ready = (state == ST_WAIT_TILE) && !rst && !abort;
        core_abort = rst || abort || (state == ST_ERROR);
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
            tile_index <= 1'b0;
            k_index <= 9'd0;
            feature_word_index <= 2'd0;
            feature_lanes <= 128'd0;
            shared_weight <= 8'sd0;
            error_code <= ERROR_NONE;
            for (seq_lane = 0; seq_lane < 26; seq_lane = seq_lane + 1) begin
                raw_result[seq_lane] <= 32'd0;
            end
        end else if (abort) begin
            state <= ST_IDLE;
            tile_index <= 1'b0;
            k_index <= 9'd0;
            feature_word_index <= 2'd0;
            feature_lanes <= 128'd0;
            shared_weight <= 8'sd0;
            error_code <= ERROR_NONE;
            for (seq_lane = 0; seq_lane < 26; seq_lane = seq_lane + 1) begin
                raw_result[seq_lane] <= 32'd0;
            end
        end else begin
            case (state)
                ST_IDLE: begin
                    if (start_valid && start_ready) begin
                        tile_index <= 1'b0;
                        k_index <= 9'd0;
                        feature_word_index <= 2'd0;
                        feature_lanes <= 128'd0;
                        shared_weight <= 8'sd0;
                        error_code <= ERROR_NONE;
                        for (seq_lane = 0; seq_lane < 26; seq_lane = seq_lane + 1) begin
                            raw_result[seq_lane] <= 32'd0;
                        end
                        state <= ST_TILE_START;
                    end
                end

                ST_TILE_START: begin
                    if (core_start_valid && core_start_ready) begin
                        k_index <= 9'd0;
                        state <= ST_WEIGHT_READ;
                    end
                end

                ST_WEIGHT_READ: begin
                    if (mem_valid && mem_ready) begin
                        if (mem_error_code != ERROR_NONE) begin
                            error_code <= (mem_error_code == ERROR_BAD_ARGUMENT ||
                                           mem_error_code == ERROR_BAD_RANGE ||
                                           mem_error_code == ERROR_INTERNAL) ?
                                          mem_error_code : ERROR_INTERNAL;
                            for (seq_lane = 0; seq_lane < 26; seq_lane = seq_lane + 1) begin
                                raw_result[seq_lane] <= 32'd0;
                            end
                            state <= ST_ERROR;
                        end else begin
                            shared_weight <= $signed(
                                mem_rdata[weight_byte_address[1:0] * 8 +: 8]
                            );
                            feature_lanes <= 128'd0;
                            feature_word_index <= 2'd0;
                            state <= ST_FEATURE_READ;
                        end
                    end
                end

                ST_FEATURE_READ: begin
                    if (mem_valid && mem_ready) begin
                        if (mem_error_code != ERROR_NONE) begin
                            error_code <= (mem_error_code == ERROR_BAD_ARGUMENT ||
                                           mem_error_code == ERROR_BAD_RANGE ||
                                           mem_error_code == ERROR_INTERNAL) ?
                                          mem_error_code : ERROR_INTERNAL;
                            for (seq_lane = 0; seq_lane < 26; seq_lane = seq_lane + 1) begin
                                raw_result[seq_lane] <= 32'd0;
                            end
                            state <= ST_ERROR;
                        end else begin
                            for (seq_lane = 0; seq_lane < 4; seq_lane = seq_lane + 1) begin
                                if (mem_rstrb[seq_lane]) begin
                                    feature_lane_index =
                                        (feature_word_index * 4) + seq_lane;
                                    feature_lanes[feature_lane_index * 8 +: 8] <=
                                        mem_rdata[seq_lane * 8 +: 8];
                                end
                            end
                            if ((!tile_index && (feature_word_index == 2'd3)) ||
                                (tile_index && (feature_word_index == 2'd2))) begin
                                state <= ST_FEED_TILE;
                            end else begin
                                feature_word_index <= feature_word_index + 2'd1;
                            end
                        end
                    end
                end

                ST_FEED_TILE: begin
                    if (core_input_valid && core_input_ready) begin
                        if (k_index == 9'd255) begin
                            state <= ST_WAIT_TILE;
                        end else begin
                            k_index <= k_index + 9'd1;
                            state <= ST_WEIGHT_READ;
                        end
                    end
                end

                ST_WAIT_TILE: begin
                    if (core_result_valid && core_result_ready) begin
                        if (core_error_code != ERROR_NONE) begin
                            error_code <= (core_error_code == ERROR_BAD_ARGUMENT ||
                                           core_error_code == ERROR_BAD_RANGE ||
                                           core_error_code == ERROR_INTERNAL ||
                                           core_error_code == 3'd7) ?
                                          core_error_code : ERROR_INTERNAL;
                            for (seq_lane = 0; seq_lane < 26; seq_lane = seq_lane + 1) begin
                                raw_result[seq_lane] <= 32'd0;
                            end
                            state <= ST_ERROR;
                        end else if (!tile_index) begin
                            for (seq_lane = 0; seq_lane < 16; seq_lane = seq_lane + 1) begin
                                raw_result[seq_lane] <=
                                    core_accumulators[seq_lane * 32 +: 32];
                            end
                            tile_index <= 1'b1;
                            k_index <= 9'd0;
                            state <= ST_TILE_START;
                        end else begin
                            for (seq_lane = 0; seq_lane < 10; seq_lane = seq_lane + 1) begin
                                raw_result[16 + seq_lane] <=
                                    core_accumulators[seq_lane * 32 +: 32];
                            end
                            state <= ST_EMIT_TILE_A;
                        end
                    end
                end

                ST_EMIT_TILE_A: begin
                    if (tile_result_valid && tile_result_ready) begin
                        state <= ST_EMIT_TILE_B;
                    end
                end

                ST_EMIT_TILE_B: begin
                    if (tile_result_valid && tile_result_ready) begin
                        state <= ST_IDLE;
                    end
                end

                ST_ERROR: begin
                    if (error_valid && error_ready) begin
                        error_code <= ERROR_NONE;
                        state <= ST_IDLE;
                    end
                end

                default: begin
                    state <= ST_IDLE;
                    tile_index <= 1'b0;
                    k_index <= 9'd0;
                    feature_word_index <= 2'd0;
                    feature_lanes <= 128'd0;
                    shared_weight <= 8'sd0;
                    error_code <= ERROR_INTERNAL;
                    for (seq_lane = 0; seq_lane < 26; seq_lane = seq_lane + 1) begin
                        raw_result[seq_lane] <= 32'd0;
                    end
                end
            endcase
        end
    end
endmodule
