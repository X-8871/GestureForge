// INT8 MAC 单元自检：读取 Python 从冻结机器清单生成的规范向量文件。
module tb_s2a_int8_mac_accumulator;
    logic clk = 1'b0;
    always #5 clk = ~clk;

    logic rst;
    logic abort;
    logic start_valid;
    logic start_ready;
    logic [12:0] start_k;
    logic signed [31:0] start_bias;
    logic operand_valid;
    logic operand_ready;
    logic signed [7:0] activation_data;
    logic signed [7:0] weight_data;
    logic result_valid;
    logic result_ready;
    logic signed [31:0] result_data;
    logic [2:0] error_code;
    logic busy;

    integer vector_fd;
    integer scan_result;
    integer vector_class;
    integer case_index;
    integer vector_k;
    integer vector_bias;
    integer expected_error;
    integer expected_result;
    integer pair_activation;
    integer pair_weight;
    integer pair_index;
    integer random_vectors_seen;
    integer directed_vectors_seen;
    integer vectors_seen;
    integer hold_cycles;
    integer hold_index;
    integer held_result;
    integer held_error;
    integer wait_index;
    integer j;
    integer test_count;
    integer signed_activation[0:8190];
    integer signed_weight[0:8190];

    int8_mac_accumulator dut (
        .clk(clk),
        .rst(rst),
        .abort(abort),
        .start_valid(start_valid),
        .start_ready(start_ready),
        .start_k(start_k),
        .start_bias(start_bias),
        .operand_valid(operand_valid),
        .operand_ready(operand_ready),
        .activation_data(activation_data),
        .weight_data(weight_data),
        .result_valid(result_valid),
        .result_ready(result_ready),
        .result_data(result_data),
        .error_code(error_code),
        .busy(busy)
    );

    task automatic fail(input string message);
        begin
            $display("FAIL: %s", message);
            $fatal(1);
        end
    endtask

    task automatic send_start(input integer count, input integer bias_value);
        begin
            @(negedge clk);
            start_k = count[12:0];
            start_bias = bias_value;
            start_valid = 1'b1;
            if (!start_ready) begin
                fail("start_ready must be high for an idle engine");
            end
            @(posedge clk);
            if (!start_ready) begin
                fail("start handshake was not accepted");
            end
            @(negedge clk);
            start_valid = 1'b0;
            if (!busy) begin
                fail("busy must cover the active transaction");
            end
            if (start_ready) begin
                fail("a second start must not be accepted during a transaction");
            end
        end
    endtask

    task automatic send_pair(
        input integer activation_value,
        input integer weight_value,
        input integer insert_bubble
    );
        begin
            if (insert_bubble != 0) begin
                operand_valid = 1'b0;
                @(posedge clk);
                if (!busy) begin
                    fail("input bubble unexpectedly ended the transaction");
                end
                @(negedge clk);
            end
            operand_valid = 1'b1;
            activation_data = activation_value;
            weight_data = weight_value;
            if (!operand_ready) begin
                fail("operand_ready must be high while accepting a pair");
            end
            @(posedge clk);
            if (!operand_ready) begin
                fail("operand pair handshake was not accepted");
            end
            @(negedge clk);
            operand_valid = 1'b0;
        end
    endtask

    task automatic check_response(input integer expected_code, input integer expected_value);
        begin
            wait_index = 0;
            while (!result_valid && wait_index < 4) begin
                @(negedge clk);
                wait_index = wait_index + 1;
            end
            if (!result_valid) begin
                fail("response did not arrive after the final/invalid input");
            end
            if (error_code !== expected_code[2:0]) begin
                $display("expected error=%0d actual=%0d", expected_code, error_code);
                fail("response error code mismatch");
            end
            if (result_data !== expected_value) begin
                $display("expected result=%0d actual=%0d", expected_value, result_data);
                fail("response result mismatch");
            end
            if (!busy || start_ready || operand_ready) begin
                fail("response backpressure must keep busy and block new input/start");
            end

            held_result = result_data;
            held_error = error_code;
            result_ready = 1'b0;
            for (hold_index = 0; hold_index < 2; hold_index = hold_index + 1) begin
                @(posedge clk);
                #1;
                if (!result_valid || result_data !== held_result || error_code !== held_error) begin
                    fail("response data/error/valid changed before result_ready");
                end
                @(negedge clk);
            end

            result_ready = 1'b1;
            @(posedge clk);
            #1;
            if (result_valid || busy) begin
                fail("result handshake must release the engine");
            end
            @(negedge clk);
            result_ready = 1'b0;
            if (!start_ready) begin
                fail("engine did not recover for the next start");
            end
        end
    endtask

    task automatic check_no_stale_response;
        begin
            if (busy || result_valid || !start_ready) begin
                fail("cancelled work left a stale response or busy state");
            end
            for (j = 0; j < 3; j = j + 1) begin
                @(posedge clk);
                #1;
                if (busy || result_valid) begin
                    fail("cancelled work produced a delayed response");
                end
            end
            @(negedge clk);
        end
    endtask

    initial begin
        rst = 1'b1;
        abort = 1'b0;
        start_valid = 1'b0;
        start_k = 13'd0;
        start_bias = 32'sd0;
        operand_valid = 1'b0;
        activation_data = 8'sd0;
        weight_data = 8'sd0;
        result_ready = 1'b0;
        random_vectors_seen = 0;
        directed_vectors_seen = 0;
        vectors_seen = 0;
        test_count = 0;

        repeat (2) @(posedge clk);
        @(negedge clk);
        rst = 1'b0;

        vector_fd = $fopen("vectors.dat", "r");
        if (vector_fd == 0) begin
            fail("cannot open temporary vectors.dat");
        end

        scan_result = $fscanf(vector_fd, "%d %d %d %d %d %d\n",
                              vector_class, case_index, vector_k, vector_bias,
                              expected_error, expected_result);
        while (scan_result == 6) begin
            if (vector_k < 1 || vector_k > 8191) begin
                fail("materialized vector K is outside the interface range");
            end
            if (vector_class == 0) begin
                if (case_index != random_vectors_seen || random_vectors_seen >= 1000) begin
                    fail("random vector ordering/count mismatch");
                end
                random_vectors_seen = random_vectors_seen + 1;
            end else if (vector_class == 1) begin
                if (case_index != directed_vectors_seen || directed_vectors_seen >= 16) begin
                    fail("directed vector ordering/count mismatch");
                end
                directed_vectors_seen = directed_vectors_seen + 1;
            end else begin
                fail("unknown vector class");
            end

            for (pair_index = 0; pair_index < vector_k; pair_index = pair_index + 1) begin
                scan_result = $fscanf(vector_fd, "%d %d\n", pair_activation, pair_weight);
                if (scan_result != 2) begin
                    fail("truncated pair list in vectors.dat");
                end
                signed_activation[pair_index] = pair_activation;
                signed_weight[pair_index] = pair_weight;
            end

            send_start(vector_k, vector_bias);
            for (pair_index = 0; pair_index < vector_k; pair_index = pair_index + 1) begin
                send_pair(signed_activation[pair_index], signed_weight[pair_index],
                          ((pair_index + case_index) % 37) == 0);
            end
            check_response(expected_error, expected_result);
            vectors_seen = vectors_seen + 1;

            scan_result = $fscanf(vector_fd, "%d %d %d %d %d %d\n",
                                  vector_class, case_index, vector_k, vector_bias,
                                  expected_error, expected_result);
        end
        $fclose(vector_fd);
        if (scan_result != -1) begin
            fail("malformed trailing data in vectors.dat");
        end
        if (random_vectors_seen != 1000 || directed_vectors_seen != 16 || vectors_seen != 1016) begin
            $display("random=%0d directed=%0d total=%0d",
                     random_vectors_seen, directed_vectors_seen, vectors_seen);
            fail("expected 1000 random and 16 directed vectors");
        end

        send_start(0, 123);
        check_response(1, 0);

        send_start(2, 55);
        send_pair(-128, 7, 0);
        check_response(1, 0);

        send_start(2, -55);
        send_pair(7, -128, 0);
        check_response(1, 0);

        send_start(4, 91);
        send_pair(2, 3, 0);
        abort = 1'b1;
        @(posedge clk);
        #1;
        if (busy || result_valid) begin
            fail("abort did not cancel an active dot product");
        end
        @(negedge clk);
        abort = 1'b0;
        check_no_stale_response();

        send_start(8191, 0);
        abort = 1'b1;
        @(posedge clk);
        #1;
        if (busy || result_valid) begin
            fail("abort failed at maximum representable K");
        end
        @(negedge clk);
        abort = 1'b0;
        check_no_stale_response();

        send_start(2, 0);
        send_pair(3, 5, 0);
        rst = 1'b1;
        @(posedge clk);
        #1;
        if (busy || result_valid || error_code != 0 || result_data != 0) begin
            fail("synchronous reset did not clear an active operation");
        end
        @(negedge clk);
        rst = 1'b0;
        check_no_stale_response();

        send_start(1, 0);
        send_pair(2, 3, 0);
        if (!result_valid) begin
            fail("expected a pending response before response cancellation");
        end
        abort = 1'b1;
        @(posedge clk);
        #1;
        if (busy || result_valid) begin
            fail("abort did not cancel an unconsumed response");
        end
        @(negedge clk);
        abort = 1'b0;
        check_no_stale_response();

        send_start(2, 100);
        send_pair(-3, 4, 0);
        send_pair(2, 5, 0);
        check_response(0, 98);

        $display("PASS: vectors=%0d random=%0d directed=%0d protocol_checks=8",
                 vectors_seen, random_vectors_seen, directed_vectors_seen);
        $finish;
    end
endmodule
