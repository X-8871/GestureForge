module xpm_fifo_async #(
    parameter FIFO_MEMORY_TYPE = "auto",
    parameter ECC_MODE = "no_ecc",
    parameter RELATED_CLOCKS = 0,
    parameter FIFO_WRITE_DEPTH = 4096,
    parameter WRITE_DATA_WIDTH = 18,
    parameter WR_DATA_COUNT_WIDTH = 12,
    parameter PROG_FULL_THRESH = 10,
    parameter FULL_RESET_VALUE = 0,
    parameter USE_ADV_FEATURES = "0707",
    parameter READ_MODE = "fwft",
    parameter FIFO_READ_LATENCY = 0,
    parameter READ_DATA_WIDTH = 18,
    parameter RD_DATA_COUNT_WIDTH = 12,
    parameter PROG_EMPTY_THRESH = 10,
    parameter DOUT_RESET_VALUE = "0",
    parameter CDC_SYNC_STAGES = 2,
    parameter WAKEUP_TIME = 0
) (
    input wire rst,
    input wire wr_clk,
    input wire wr_en,
    input wire [WRITE_DATA_WIDTH-1:0] din,
    output wire full,
    output reg overflow,
    output wire prog_full,
    output wire [WR_DATA_COUNT_WIDTH-1:0] wr_data_count,
    output wire almost_full,
    output reg wr_ack,
    output wire wr_rst_busy,
    input wire rd_clk,
    input wire rd_en,
    output wire [READ_DATA_WIDTH-1:0] dout,
    output wire empty,
    output reg underflow,
    output wire rd_rst_busy,
    output wire prog_empty,
    output wire [RD_DATA_COUNT_WIDTH-1:0] rd_data_count,
    output wire almost_empty,
    output wire data_valid,
    input wire sleep,
    input wire injectsbiterr,
    input wire injectdbiterr,
    output wire sbiterr,
    output wire dbiterr
);
reg [WRITE_DATA_WIDTH-1:0] storage [0:FIFO_WRITE_DEPTH-1];
integer write_pointer = 0;
integer read_pointer = 0;
integer occupancy = 0;
integer pop_count = 0;
wire accepted_write = wr_en && !full;
wire accepted_read = rd_en && !empty;

assign full = (occupancy >= FIFO_WRITE_DEPTH);
assign empty = (occupancy == 0);
assign dout = empty ? {READ_DATA_WIDTH{1'b0}} : storage[read_pointer];
assign prog_full = (occupancy >= (FIFO_WRITE_DEPTH - PROG_FULL_THRESH));
assign wr_data_count = occupancy;
assign almost_full = full;
assign wr_rst_busy = 1'b0;
assign prog_empty = (occupancy <= PROG_EMPTY_THRESH);
assign rd_data_count = occupancy;
assign almost_empty = empty;
assign data_valid = !empty;
assign rd_rst_busy = 1'b0;
assign sbiterr = 1'b0;
assign dbiterr = 1'b0;

initial begin
    if (READ_DATA_WIDTH != WRITE_DATA_WIDTH) $fatal(1, "测试模型要求 FIFO 读写位宽一致");
    if (READ_MODE != "fwft") $fatal(1, "测试模型只实现 FWFT 读模式");
    if (FIFO_READ_LATENCY != 0) $fatal(1, "测试模型只实现零读延迟 FWFT");
    if (wr_clk !== rd_clk) $fatal(1, "此模型不覆盖异步时钟 CDC");
end

always @(posedge wr_clk or posedge rst) begin
    if (rst) begin
        write_pointer <= 0;
        read_pointer <= 0;
        occupancy <= 0;
        pop_count <= 0;
        wr_ack <= 1'b0;
        overflow <= 1'b0;
        underflow <= 1'b0;
    end else begin
        wr_ack <= accepted_write;
        overflow <= wr_en && full;
        underflow <= rd_en && empty;
        if (accepted_write) begin
            storage[write_pointer] <= din;
            if (write_pointer == FIFO_WRITE_DEPTH - 1) write_pointer <= 0;
            else write_pointer <= write_pointer + 1;
        end
        if (accepted_read) begin
            if (read_pointer == FIFO_WRITE_DEPTH - 1) read_pointer <= 0;
            else read_pointer <= read_pointer + 1;
            pop_count <= pop_count + 1;
        end
        case ({accepted_write, accepted_read})
            2'b10: occupancy <= occupancy + 1;
            2'b01: occupancy <= occupancy - 1;
            default: occupancy <= occupancy;
        endcase
    end
end
endmodule
