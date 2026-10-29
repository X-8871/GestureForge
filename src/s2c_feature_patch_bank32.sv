// 固定32路交织特征补丁缓存，提供16个无冲突同步读端口。
module s2c_feature_patch_bank32 (
    input  logic                                      clk,
    input  logic                                      rst,
    input  logic                                      wr_en,
    input  logic [16:0]                              wr_addr,
    input  logic [7:0]                               wr_data,
    input  logic                                      rd_en,
    input  logic [15:0]                              rd_lane_active,
    input  logic [16*17-1:0]                          rd_addr_flat,
    output logic                                      rd_valid,
    output logic [16*8-1:0]                           rd_data_flat,
    output logic [15:0]                              rd_lane_valid,
    output logic                                      rd_conflict,
    output logic                                      rd_bad_address,
    output logic                                      wr_bad_address
);
    localparam integer MAX_BYTES = 124416;
    localparam integer ADDR_WIDTH = 17;
    localparam integer BANK_COUNT = 32;
    localparam integer READ_LANES = 16;
    localparam integer BANK_BITS = 5;
    localparam integer BANK_DEPTH = MAX_BYTES / BANK_COUNT;
    localparam integer BANK_ADDR_WIDTH = ADDR_WIDTH - BANK_BITS;
    localparam integer LANE_BITS = 4;

    logic [BANK_COUNT-1:0] bank_read_hit;
    logic [LANE_BITS-1:0] bank_read_lane [0:BANK_COUNT-1];
    logic [BANK_ADDR_WIDTH-1:0] bank_read_offset [0:BANK_COUNT-1];
    logic [7:0] bank_read_data [0:BANK_COUNT-1];
    logic [LANE_BITS-1:0] bank_result_lane [0:BANK_COUNT-1];
    logic bank_result_valid [0:BANK_COUNT-1];
    logic rd_request_valid;
    integer lane_i;
    integer bank_i;
    integer lane_j;
    integer seq_lane;

    always_comb begin
        rd_conflict = 1'b0;
        rd_bad_address = 1'b0;
        for (lane_i = 0; lane_i < READ_LANES; lane_i = lane_i + 1) begin
            if (rd_lane_active[lane_i] &&
                (rd_addr_flat[lane_i*ADDR_WIDTH +: ADDR_WIDTH] >= MAX_BYTES)) begin
                rd_bad_address = 1'b1;
            end
            for (lane_j = lane_i + 1; lane_j < READ_LANES; lane_j = lane_j + 1) begin
                if (rd_lane_active[lane_i] && rd_lane_active[lane_j] &&
                    (rd_addr_flat[lane_i*ADDR_WIDTH +: BANK_BITS] ==
                     rd_addr_flat[lane_j*ADDR_WIDTH +: BANK_BITS])) begin
                    rd_conflict = 1'b1;
                end
            end
        end

        for (bank_i = 0; bank_i < BANK_COUNT; bank_i = bank_i + 1) begin
            bank_read_hit[bank_i] = 1'b0;
            bank_read_lane[bank_i] = '0;
            bank_read_offset[bank_i] = '0;
            for (lane_i = 0; lane_i < READ_LANES; lane_i = lane_i + 1) begin
                if (rd_lane_active[lane_i] &&
                    (rd_addr_flat[lane_i*ADDR_WIDTH +: BANK_BITS] == bank_i[BANK_BITS-1:0])) begin
                    bank_read_hit[bank_i] = 1'b1;
                    bank_read_lane[bank_i] = lane_i[LANE_BITS-1:0];
                    bank_read_offset[bank_i] = rd_addr_flat[
                        lane_i*ADDR_WIDTH + BANK_BITS +: BANK_ADDR_WIDTH
                    ];
                end
            end
        end
        rd_request_valid = rd_en && (|rd_lane_active) && !rd_conflict && !rd_bad_address;
    end

    always_ff @(posedge clk) begin
        if (rst) begin
            rd_valid <= 1'b0;
        end else begin
            rd_valid <= rd_request_valid;
        end
    end

    always_comb begin
        rd_data_flat = '0;
        rd_lane_valid = '0;
        for (seq_lane = 0; seq_lane < BANK_COUNT; seq_lane = seq_lane + 1) begin
            if (bank_result_valid[seq_lane]) begin
                rd_data_flat[bank_result_lane[seq_lane]*8 +: 8] = bank_read_data[seq_lane];
                rd_lane_valid[bank_result_lane[seq_lane]] = 1'b1;
            end
        end
    end

    genvar bank_g;
    generate
        for (bank_g = 0; bank_g < BANK_COUNT; bank_g = bank_g + 1) begin : gen_feature_bank
            logic [7:0] memory [0:BANK_DEPTH-1];

            always_ff @(posedge clk) begin
                if (rst) begin
                    bank_read_data[bank_g] <= 8'd0;
                    bank_result_lane[bank_g] <= '0;
                    bank_result_valid[bank_g] <= 1'b0;
                end else begin
                    bank_result_valid[bank_g] <= rd_request_valid && bank_read_hit[bank_g];
                    if (wr_en && (wr_addr < MAX_BYTES) && (wr_addr[BANK_BITS-1:0] == bank_g)) begin
                        memory[wr_addr[ADDR_WIDTH-1:BANK_BITS]] <= wr_data;
                    end
                    if (rd_request_valid && bank_read_hit[bank_g]) begin
                        bank_read_data[bank_g] <= memory[bank_read_offset[bank_g]];
                        bank_result_lane[bank_g] <= bank_read_lane[bank_g];
                    end
                end
            end
        end
    endgenerate

    always_comb begin
        wr_bad_address = wr_en && (wr_addr >= MAX_BYTES);
    end
endmodule
