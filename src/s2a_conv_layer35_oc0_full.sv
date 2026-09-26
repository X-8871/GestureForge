// S2A-T34：固定 tiny416 layer35，仅按 NCHW 顺序扫描输出通道 0。
module s2a_conv_layer35_oc0_full (
    input  logic        clk,
    input  logic        hard_reset,
    input  logic        abort,
    input  logic        buffer_owner_pl,
    input  logic        run_valid,
    output logic        run_ready,
    output logic        run_busy,
    output logic        run_done,
    output logic        run_cancelled,
    output logic [2:0]  run_error_code,
    output logic        result_valid,
    input  logic        result_ready,
    output logic [4:0]  result_y,
    output logic [4:0]  result_x,
    output logic [31:0] result_address,
    output logic [7:0]  result_value,
    output logic [2:0]  result_error_code,
    output logic        backend_cancel,
    output logic        backend_req_valid,
    input  logic        backend_req_ready,
    output logic        backend_req_write,
    output logic [31:0] backend_req_addr,
    output logic [31:0] backend_req_wdata,
    output logic [3:0]  backend_req_rstrb,
    output logic [3:0]  backend_req_wstrb,
    input  logic        backend_rsp_valid,
    input  logic [31:0] backend_rsp_rdata,
    input  logic [2:0]  backend_rsp_error
);
    localparam logic [31:0] INPUT_BASE = 32'd27706496;
    localparam logic [31:0] INPUT_LENGTH = 32'd259584;
    localparam logic [31:0] OUTPUT_BASE = 32'd27966080;
    localparam logic [31:0] OUTPUT_LENGTH = 32'd173056;
    localparam logic [31:0] WEIGHT_BASE = 32'h00100000;
    localparam logic [31:0] WEIGHT_PACKAGE_LENGTH = 32'd5903100;
    localparam logic [31:0] WEIGHT_OFFSET = 32'd5010412;
    localparam logic [31:0] WEIGHT_LENGTH = 32'd884736;

    logic run_active;
    logic [4:0] scan_y;
    logic [4:0] scan_x;
    logic engine_start_ready;
    logic engine_busy;
    logic engine_result_valid;
    logic engine_result_ready;
    logic [31:0] engine_result_address;
    logic [7:0] engine_result_value;
    logic [2:0] engine_result_error;

    assign run_ready = !run_busy && !run_active && !hard_reset && !abort;
    assign result_valid = engine_result_valid;
    assign result_y = scan_y;
    assign result_x = scan_x;
    assign result_address = engine_result_address;
    assign result_value = engine_result_value;
    assign result_error_code = engine_result_error;
    assign engine_result_ready = result_ready;

    s2a_conv_engine u_engine (
        .clk(clk),
        .hard_reset(hard_reset),
        .abort(abort),
        .buffer_owner_pl(buffer_owner_pl),
        .start_valid(run_active && engine_start_ready),
        .start_ready(engine_start_ready),
        .layer_index(32'd35),
        .weight_layer_index(32'd35),
        .input_base_address(INPUT_BASE),
        .input_length_bytes(INPUT_LENGTH),
        .input_batch_count(32'd1),
        .input_channels(32'd384),
        .input_height(32'd26),
        .input_width(32'd26),
        .output_base_address(OUTPUT_BASE),
        .output_length_bytes(OUTPUT_LENGTH),
        .output_batch_count(32'd1),
        .output_channels(32'd256),
        .output_height(32'd26),
        .output_width(32'd26),
        .kernel_height(32'd3),
        .kernel_width(32'd3),
        .stride_y(32'd1),
        .stride_x(32'd1),
        .pad_left(32'd1),
        .pad_right(32'd1),
        .pad_top(32'd1),
        .pad_bottom(32'd1),
        .groups(32'd1),
        .padding_value_int8(32'sd0),
        .weight_package_base_address(WEIGHT_BASE),
        .weight_package_length_bytes(WEIGHT_PACKAGE_LENGTH),
        .quantized_weight_offset(WEIGHT_OFFSET),
        .quantized_weight_bytes(WEIGHT_LENGTH),
        .output_batch(32'd0),
        .output_channel(32'd0),
        .output_y({27'd0, scan_y}),
        .output_x({27'd0, scan_x}),
        .bias_int32(-32'sd896),
        .activation_mode(2'd1),
        .positive_multiplier(32'd94787),
        .positive_q_shift(32'd27),
        .negative_multiplier(32'd19412319),
        .negative_q_shift(32'd38),
        .backend_cancel(backend_cancel),
        .backend_req_valid(backend_req_valid),
        .backend_req_ready(backend_req_ready),
        .backend_req_write(backend_req_write),
        .backend_req_addr(backend_req_addr),
        .backend_req_wdata(backend_req_wdata),
        .backend_req_rstrb(backend_req_rstrb),
        .backend_req_wstrb(backend_req_wstrb),
        .backend_rsp_valid(backend_rsp_valid),
        .backend_rsp_rdata(backend_rsp_rdata),
        .backend_rsp_error(backend_rsp_error),
        .busy(engine_busy),
        .result_valid(engine_result_valid),
        .result_ready(engine_result_ready),
        .result_output_address(engine_result_address),
        .result_value(engine_result_value),
        .result_error_code(engine_result_error)
    );

    always_ff @(posedge clk) begin
        if (hard_reset) begin
            run_active <= 1'b0;
            run_busy <= 1'b0;
            run_done <= 1'b0;
            run_cancelled <= 1'b0;
            run_error_code <= 3'd0;
            scan_y <= 5'd0;
            scan_x <= 5'd0;
        end else if (abort) begin
            run_cancelled <= run_active || run_busy;
            run_active <= 1'b0;
            run_busy <= 1'b0;
            run_done <= 1'b0;
            run_error_code <= 3'd0;
            scan_y <= 5'd0;
            scan_x <= 5'd0;
        end else begin
            if (run_valid && run_ready) begin
                run_active <= 1'b1;
                run_busy <= 1'b1;
                run_done <= 1'b0;
                run_cancelled <= 1'b0;
                run_error_code <= 3'd0;
                scan_y <= 5'd0;
                scan_x <= 5'd0;
            end else if (run_active && engine_result_valid && engine_result_ready) begin
                if (engine_result_error != 3'd0) begin
                    run_active <= 1'b0;
                    run_busy <= 1'b0;
                    run_error_code <= engine_result_error;
                end else if ((scan_y == 5'd25) && (scan_x == 5'd25)) begin
                    run_active <= 1'b0;
                    run_busy <= 1'b0;
                    run_done <= 1'b1;
                end else if (scan_x == 5'd25) begin
                    scan_x <= 5'd0;
                    scan_y <= scan_y + 5'd1;
                end else begin
                    scan_x <= scan_x + 5'd1;
                end
            end
        end
    end
endmodule
