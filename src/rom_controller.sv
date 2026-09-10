module rom_controller #(
    parameter int ADDR_WIDTH = 2,
    parameter int DATA_WIDTH = 8,
    parameter int DEPTH = 1 << ADDR_WIDTH
)(
    input logic clk,
    input logic rst,
    input logic start,
    input logic [ADDR_WIDTH-1:0] start_addr,
    output logic busy,
    output logic done,
    output logic [DATA_WIDTH-1:0] result_data
);

    logic rd_en;
    logic [ADDR_WIDTH-1:0] rd_addr;
    logic [DATA_WIDTH-1:0] rd_data;
    logic rd_valid;


    
    sync_rom #(
    .ADDR_WIDTH(ADDR_WIDTH),
    .DATA_WIDTH(DATA_WIDTH),
    .DEPTH(DEPTH)
) u_sync_rom (
    .clk(clk),
    .rst(rst),
    .rd_en(rd_en),
    .rd_addr(rd_addr),
    .rd_data(rd_data),
    .rd_valid(rd_valid)
);

    typedef enum logic [1:0] {
    IDLE,
    READ_REQ,
    WAIT_DATA,
    DONE
} state_t;

    state_t state;
    state_t next_state;
    
    logic [ADDR_WIDTH-1:0] addr_reg;
    
    always_ff @(posedge clk) begin
    if (rst) begin
        state       <= IDLE;
        addr_reg    <= '0;
        result_data <= '0;
    end else begin
        state <= next_state;

        if (state == IDLE && start)
            addr_reg <= start_addr;

        if (state == WAIT_DATA && rd_valid)
            result_data <= rd_data;
    end
end
    
    always_comb begin
    next_state = state;

    case (state)
        IDLE: begin
            if (start)
                next_state = READ_REQ;
        end

        READ_REQ: begin
            next_state = WAIT_DATA;
        end

        WAIT_DATA: begin
            if (rd_valid)
                next_state = DONE;
        end

        DONE: begin
            next_state = IDLE;
        end

        default: begin
            next_state = IDLE;
        end
    endcase
end

    assign rd_en = (state == READ_REQ);
    assign rd_addr = addr_reg;
    
    assign busy = (state == READ_REQ) || (state == WAIT_DATA);
    assign done = (state == DONE);

endmodule