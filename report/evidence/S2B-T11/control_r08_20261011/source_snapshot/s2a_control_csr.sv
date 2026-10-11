// S2A-T11：独立 CSR/控制状态机，不包含 memory master 或算子实现。
module s2a_control_csr (
    input  logic        clk,
    input  logic        hard_reset,

    input  logic        csr_valid,
    output logic        csr_ready,
    input  logic        csr_write,
    input  logic [7:0]  csr_addr,
    input  logic [31:0] csr_wdata,
    output logic [31:0] csr_rdata,

    // 该事件表示后端在已接受的 memory handshake 上返回非零错误码。
    input  logic        backend_memory_error_valid,
    input  logic [2:0]  backend_memory_error_code,
    input  logic        operator_result_valid,
    input  logic [2:0]  operator_error_code,

    output logic        backend_start,
    output logic        backend_abort,
    output logic        busy,
    output logic        done,
    output logic        error,
    output logic        pl_owns_buffers,
    output logic        head_output_valid
);
    localparam logic [7:0] REG_CMD           = 8'h00;
    localparam logic [7:0] REG_STATUS        = 8'h04;
    localparam logic [7:0] REG_ERROR_CODE    = 8'h08;
    localparam logic [7:0] REG_FRAME_ID      = 8'h0C;
    localparam logic [7:0] REG_INPUT_ADDR    = 8'h10;
    localparam logic [7:0] REG_INPUT_BYTES   = 8'h14;
    localparam logic [7:0] REG_WEIGHT_ADDR   = 8'h18;
    localparam logic [7:0] REG_WEIGHT_BYTES  = 8'h1C;
    localparam logic [7:0] REG_FEATURE_BASE  = 8'h20;
    localparam logic [7:0] REG_FEATURE_LIMIT = 8'h24;
    localparam logic [7:0] REG_TIMEOUT       = 8'h28;
    localparam logic [7:0] REG_HEAD13_ADDR   = 8'h2C;
    localparam logic [7:0] REG_HEAD13_BYTES  = 8'h30;
    localparam logic [7:0] REG_HEAD26_ADDR   = 8'h34;
    localparam logic [7:0] REG_HEAD26_BYTES  = 8'h38;
    localparam logic [7:0] REG_ACK           = 8'h3C;

    localparam logic [31:0] DEFAULT_INPUT_ADDR   = 32'h0000_0000;
    localparam logic [31:0] DEFAULT_INPUT_BYTES  = 32'd519168;
    localparam logic [31:0] DEFAULT_WEIGHT_ADDR  = 32'h0010_0000;
    localparam logic [31:0] DEFAULT_WEIGHT_BYTES = 32'd5903100;
    localparam logic [31:0] DEFAULT_FEATURE_BASE = 32'h0100_0000;
    localparam logic [31:0] DEFAULT_FEATURE_LIMIT = 32'd28159416;
    localparam logic [31:0] DEFAULT_HEAD13_ADDR  = 32'd27549952;
    localparam logic [31:0] DEFAULT_HEAD13_BYTES = 32'd5070;
    localparam logic [31:0] DEFAULT_HEAD26_ADDR  = 32'd28139136;
    localparam logic [31:0] DEFAULT_HEAD26_BYTES = 32'd20280;

    localparam logic [2:0] NONE                  = 3'd0;
    localparam logic [2:0] BAD_ARGUMENT          = 3'd1;
    localparam logic [2:0] BAD_RANGE             = 3'd2;
    localparam logic [2:0] BAD_LENGTH            = 3'd3;
    localparam logic [2:0] TIMEOUT_ERROR         = 3'd5;
    localparam logic [2:0] INTERNAL              = 3'd6;

    logic [2:0] error_code;
    logic [31:0] frame_id;
    logic [31:0] active_frame_id;
    logic [31:0] input_addr;
    logic [31:0] input_bytes;
    logic [31:0] weight_addr;
    logic [31:0] weight_bytes;
    logic [31:0] timeout_cycles;
    logic [31:0] elapsed_cycles;
    logic config_idle;
    logic [2:0] mapped_memory_error;

    always_comb begin
        csr_ready = !hard_reset;
        csr_rdata = 32'd0;
        if (csr_valid && !csr_write) begin
            if (csr_addr[1:0] == 2'b00) begin
                case (csr_addr)
                    REG_STATUS: begin
                        csr_rdata = {28'd0, pl_owns_buffers, error, done, busy};
                    end
                    REG_ERROR_CODE: csr_rdata = {29'd0, error_code};
                    REG_FRAME_ID: csr_rdata = frame_id;
                    REG_INPUT_ADDR: csr_rdata = input_addr;
                    REG_INPUT_BYTES: csr_rdata = input_bytes;
                    REG_WEIGHT_ADDR: csr_rdata = weight_addr;
                    REG_WEIGHT_BYTES: csr_rdata = weight_bytes;
                    REG_FEATURE_BASE: csr_rdata = DEFAULT_FEATURE_BASE;
                    REG_FEATURE_LIMIT: csr_rdata = DEFAULT_FEATURE_LIMIT;
                    REG_TIMEOUT: csr_rdata = timeout_cycles;
                    REG_HEAD13_ADDR: csr_rdata = DEFAULT_HEAD13_ADDR;
                    REG_HEAD13_BYTES: csr_rdata = DEFAULT_HEAD13_BYTES;
                    REG_HEAD26_ADDR: csr_rdata = DEFAULT_HEAD26_ADDR;
                    REG_HEAD26_BYTES: csr_rdata = DEFAULT_HEAD26_BYTES;
                    default: csr_rdata = 32'd0;
                endcase
            end
        end
    end

    always_comb begin
        config_idle = !pl_owns_buffers && !busy && !done && !error;
        mapped_memory_error = INTERNAL;
        if ((backend_memory_error_code == 3'd1) ||
            (backend_memory_error_code == 3'd2) ||
            (backend_memory_error_code == 3'd6)) begin
            mapped_memory_error = backend_memory_error_code;
        end
    end

    always_ff @(posedge clk) begin
        backend_start <= 1'b0;
        backend_abort <= 1'b0;

        if (hard_reset) begin
            busy <= 1'b0;
            done <= 1'b0;
            error <= 1'b0;
            error_code <= NONE;
            pl_owns_buffers <= 1'b0;
            head_output_valid <= 1'b0;
            frame_id <= 32'd0;
            active_frame_id <= 32'd0;
            input_addr <= DEFAULT_INPUT_ADDR;
            input_bytes <= DEFAULT_INPUT_BYTES;
            weight_addr <= DEFAULT_WEIGHT_ADDR;
            weight_bytes <= DEFAULT_WEIGHT_BYTES;
            timeout_cycles <= 32'd0;
            elapsed_cycles <= 32'd0;
            backend_abort <= 1'b1;
        end else if (csr_valid && csr_ready && csr_write &&
                     (csr_addr == REG_CMD) && csr_wdata[1]) begin
            // soft_reset 同周期优先于 start，并恢复整个寄存器默认集。
            busy <= 1'b0;
            done <= 1'b0;
            error <= 1'b0;
            error_code <= NONE;
            pl_owns_buffers <= 1'b0;
            head_output_valid <= 1'b0;
            frame_id <= 32'd0;
            active_frame_id <= 32'd0;
            input_addr <= DEFAULT_INPUT_ADDR;
            input_bytes <= DEFAULT_INPUT_BYTES;
            weight_addr <= DEFAULT_WEIGHT_ADDR;
            weight_bytes <= DEFAULT_WEIGHT_BYTES;
            timeout_cycles <= 32'd0;
            elapsed_cycles <= 32'd0;
            backend_abort <= 1'b1;
        end else begin
            if (csr_valid && csr_ready && csr_write) begin
                case (csr_addr)
                    REG_CMD: begin
                        if (csr_wdata[0] && config_idle) begin
                            if ((input_addr != DEFAULT_INPUT_ADDR) ||
                                (weight_addr != DEFAULT_WEIGHT_ADDR)) begin
                                busy <= 1'b0;
                                done <= 1'b0;
                                error <= 1'b1;
                                error_code <= BAD_RANGE;
                                pl_owns_buffers <= 1'b0;
                                head_output_valid <= 1'b0;
                            end else if ((input_bytes != DEFAULT_INPUT_BYTES) ||
                                         (weight_bytes != DEFAULT_WEIGHT_BYTES)) begin
                                busy <= 1'b0;
                                done <= 1'b0;
                                error <= 1'b1;
                                error_code <= BAD_LENGTH;
                                pl_owns_buffers <= 1'b0;
                                head_output_valid <= 1'b0;
                            end else if (timeout_cycles == 32'd0) begin
                                busy <= 1'b0;
                                done <= 1'b0;
                                error <= 1'b1;
                                error_code <= BAD_ARGUMENT;
                                pl_owns_buffers <= 1'b0;
                                head_output_valid <= 1'b0;
                            end else begin
                                busy <= 1'b1;
                                done <= 1'b0;
                                error <= 1'b0;
                                error_code <= NONE;
                                pl_owns_buffers <= 1'b1;
                                head_output_valid <= 1'b0;
                                active_frame_id <= frame_id;
                                elapsed_cycles <= 32'd0;
                                backend_start <= 1'b1;
                            end
                        end
                    end
                    REG_ACK: begin
                        if (csr_wdata[0] && done) begin
                            done <= 1'b0;
                        end
                        if (csr_wdata[1] && error) begin
                            error <= 1'b0;
                            error_code <= NONE;
                        end
                    end
                    default: begin
                        if (config_idle) begin
                            case (csr_addr)
                                REG_FRAME_ID: frame_id <= csr_wdata;
                                REG_INPUT_ADDR: input_addr <= csr_wdata;
                                REG_INPUT_BYTES: input_bytes <= csr_wdata;
                                REG_WEIGHT_ADDR: weight_addr <= csr_wdata;
                                REG_WEIGHT_BYTES: weight_bytes <= csr_wdata;
                                REG_TIMEOUT: timeout_cycles <= csr_wdata;
                                default: begin end
                            endcase
                        end
                    end
                endcase
            end

            if (busy) begin
                if (backend_memory_error_valid &&
                    (backend_memory_error_code != NONE)) begin
                    busy <= 1'b0;
                    done <= 1'b0;
                    error <= 1'b1;
                    error_code <= mapped_memory_error;
                    pl_owns_buffers <= 1'b0;
                    head_output_valid <= 1'b0;
                    backend_abort <= 1'b1;
                end else if (operator_result_valid) begin
                    if (operator_error_code == NONE) begin
                        busy <= 1'b0;
                        done <= 1'b1;
                        error <= 1'b0;
                        error_code <= NONE;
                        pl_owns_buffers <= 1'b0;
                        head_output_valid <= 1'b1;
                        frame_id <= active_frame_id;
                    end else begin
                        busy <= 1'b0;
                        done <= 1'b0;
                        error <= 1'b1;
                        error_code <= operator_error_code;
                        pl_owns_buffers <= 1'b0;
                        head_output_valid <= 1'b0;
                        backend_abort <= 1'b1;
                    end
                end else if ((elapsed_cycles + 32'd1) >= timeout_cycles) begin
                    busy <= 1'b0;
                    done <= 1'b0;
                    error <= 1'b1;
                    error_code <= TIMEOUT_ERROR;
                    pl_owns_buffers <= 1'b0;
                    head_output_valid <= 1'b0;
                    backend_abort <= 1'b1;
                end else begin
                    elapsed_cycles <= elapsed_cycles + 32'd1;
                end
            end
        end
    end
endmodule
