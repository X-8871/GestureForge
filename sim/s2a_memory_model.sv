// S2A-T10：G0 单 outstanding byte-lane memory testbench model。
module s2a_memory_model #(
    parameter integer MAX_FEATURE_RANGES = 64,
    parameter integer PATCH_CAPACITY = 32768
) (
    input  logic        clk,
    input  logic        reset,
    input  logic        buffer_owner_pl,
    input  logic        fault_inject_valid,
    input  logic [2:0]  fault_inject_code,
    input  logic        mem_valid,
    input  logic        mem_write,
    input  logic [31:0] mem_addr,
    input  logic [31:0] mem_wdata,
    input  logic [3:0]  mem_rstrb,
    input  logic [3:0]  mem_wstrb,
    output logic        mem_ready,
    output logic [31:0] mem_rdata,
    output logic [2:0]  mem_error_code,
    output logic        model_initialized
);
    localparam logic [2:0] NONE         = 3'd0;
    localparam logic [2:0] BAD_ARGUMENT = 3'd1;
    localparam logic [2:0] BAD_RANGE    = 3'd2;
    localparam logic [2:0] INTERNAL     = 3'd6;

    localparam integer READ_INPUT   = 0;
    localparam integer READ_WEIGHTS = 1;
    localparam integer READ_FEATURE = 2;
    localparam integer WRITE_FEATURE = 3;

    logic [31:0] input_start;
    logic [31:0] input_end;
    logic [31:0] weights_start;
    logic [31:0] weights_end;
    logic [31:0] feature_start [0:MAX_FEATURE_RANGES-1];
    logic [31:0] feature_end [0:MAX_FEATURE_RANGES-1];
    integer feature_range_count;

    integer stall_index [0:3] = '{0, 0, 0, 0};
    logic pending;
    integer pending_class;
    integer stall_remaining;
    logic [31:0] held_addr;
    logic [31:0] held_wdata;
    logic [3:0] held_rstrb;
    logic [3:0] held_wstrb;
    logic held_write;
    logic held_fault_valid;
    logic [2:0] held_fault_code;

    integer patch_count;
    logic [31:0] patch_address [0:PATCH_CAPACITY-1];
    logic [7:0] patch_value [0:PATCH_CAPACITY-1];

    integer request_class;
    integer scheduled_stall;
    integer lane;

    function automatic integer stall_cycles(input integer schedule_index);
        begin
            case (schedule_index % 5)
                0: stall_cycles = 0;
                1: stall_cycles = 1;
                2: stall_cycles = 2;
                3: stall_cycles = 7;
                default: stall_cycles = 3;
            endcase
        end
    endfunction

    function automatic integer object_for_byte(input logic [31:0] byte_address);
        integer range_index;
        begin
            object_for_byte = -1;
            if ((byte_address >= input_start) && (byte_address < input_end)) begin
                object_for_byte = 0;
            end else if ((byte_address >= weights_start) &&
                         (byte_address < weights_end)) begin
                object_for_byte = 1;
            end else begin
                for (range_index = 0; range_index < feature_range_count;
                     range_index = range_index + 1) begin
                    if ((byte_address >= feature_start[range_index]) &&
                        (byte_address < feature_end[range_index])) begin
                        object_for_byte = range_index + 2;
                    end
                end
            end
        end
    endfunction

    function automatic integer patch_index(input logic [31:0] byte_address);
        integer patch_scan;
        begin
            patch_index = -1;
            for (patch_scan = 0; patch_scan < patch_count;
                 patch_scan = patch_scan + 1) begin
                if (patch_address[patch_scan] == byte_address) begin
                    patch_index = patch_scan;
                end
            end
        end
    endfunction

    function automatic logic [7:0] initial_byte(input logic [31:0] byte_address);
        begin
            initial_byte = byte_address[7:0] ^ byte_address[15:8] ^
                           byte_address[23:16] ^ byte_address[31:24] ^ 8'hA5;
        end
    endfunction

    function automatic logic [7:0] read_byte(input logic [31:0] byte_address);
        integer found_patch;
        begin
            read_byte = initial_byte(byte_address);
            found_patch = patch_index(byte_address);
            if (found_patch >= 0) begin
                read_byte = patch_value[found_patch];
            end
        end
    endfunction

    function automatic integer additional_patch_bytes(
        input logic [31:0] word_address,
        input logic [3:0] byte_strobe
    );
        integer byte_lane;
        integer prior_lane;
        integer existing_patch;
        logic repeated_lane;
        begin
            additional_patch_bytes = 0;
            for (byte_lane = 0; byte_lane < 4; byte_lane = byte_lane + 1) begin
                if (byte_strobe[byte_lane]) begin
                    existing_patch = patch_index(word_address + byte_lane);
                    repeated_lane = 1'b0;
                    for (prior_lane = 0; prior_lane < byte_lane;
                         prior_lane = prior_lane + 1) begin
                        if (byte_strobe[prior_lane] &&
                            ((word_address + prior_lane) == (word_address + byte_lane))) begin
                            repeated_lane = 1'b1;
                        end
                    end
                    if ((existing_patch < 0) && !repeated_lane) begin
                        additional_patch_bytes = additional_patch_bytes + 1;
                    end
                end
            end
        end
    endfunction

    function automatic logic [2:0] request_error(
        input logic write_request,
        input logic [31:0] address,
        input logic [3:0] read_strobe,
        input logic [3:0] write_strobe,
        input logic inject_valid,
        input logic [2:0] inject_code
    );
        integer selected_object;
        integer this_object;
        integer byte_lane;
        logic range_bad;
        begin
            request_error = NONE;
            if ((!write_request && ((read_strobe == 4'b0000) ||
                                    (write_strobe != 4'b0000))) ||
                (write_request && ((write_strobe == 4'b0000) ||
                                   (read_strobe != 4'b0000)))) begin
                request_error = BAD_ARGUMENT;
            end else if (address[1:0] != 2'b00) begin
                request_error = BAD_RANGE;
            end else begin
                selected_object = -2;
                range_bad = 1'b0;
                for (byte_lane = 0; byte_lane < 4; byte_lane = byte_lane + 1) begin
                    if ((!write_request && read_strobe[byte_lane]) ||
                        (write_request && write_strobe[byte_lane])) begin
                        this_object = object_for_byte(address + byte_lane);
                        if ((this_object < 0) || (write_request && (this_object < 2))) begin
                            range_bad = 1'b1;
                        end
                        if (selected_object == -2) begin
                            selected_object = this_object;
                        end else if (this_object != selected_object) begin
                            range_bad = 1'b1;
                        end
                    end
                end
                if (range_bad || (selected_object == -2)) begin
                    request_error = BAD_RANGE;
                end else if (write_request &&
                             ((patch_count + additional_patch_bytes(address, write_strobe)) >
                              PATCH_CAPACITY)) begin
                    request_error = INTERNAL;
                end else if (inject_valid) begin
                    if ((inject_code == 3'd6) || (inject_code == 3'd7)) begin
                        request_error = inject_code;
                    end else begin
                        request_error = INTERNAL;
                    end
                end
            end
        end
    endfunction

    task automatic store_byte(input logic [31:0] byte_address,
                              input logic [7:0] byte_value);
        integer found_patch;
        begin
            found_patch = patch_index(byte_address);
            if (found_patch >= 0) begin
                patch_value[found_patch] = byte_value;
            end else if (patch_count < PATCH_CAPACITY) begin
                patch_address[patch_count] = byte_address;
                patch_value[patch_count] = byte_value;
                patch_count = patch_count + 1;
            end
        end
    endtask

    initial begin : load_manifest_ranges
        integer range_file;
        integer scan_count;
        integer range_index;
        logic [31:0] declared_count;
        model_initialized = 1'b0;
        input_start = 32'd0;
        input_end = 32'd0;
        weights_start = 32'd0;
        weights_end = 32'd0;
        feature_range_count = 0;
        patch_count = 0;
        range_file = $fopen("memory_ranges.dat", "r");
        if (range_file == 0) begin
            $fatal(1, "无法打开 manifest 派生的 memory_ranges.dat");
        end
        scan_count = $fscanf(range_file, "%h %h %h %h %h",
                             input_start, input_end, weights_start,
                             weights_end, declared_count);
        if ((scan_count != 5) || (declared_count > MAX_FEATURE_RANGES) ||
            (input_start >= input_end) || (weights_start >= weights_end) ||
            ((input_start < weights_end) && (weights_start < input_end))) begin
            $fatal(1, "memory_ranges.dat 输入/权重描述符非法");
        end
        feature_range_count = declared_count;
        for (range_index = 0; range_index < feature_range_count;
             range_index = range_index + 1) begin
            scan_count = $fscanf(range_file, "%h %h",
                                 feature_start[range_index], feature_end[range_index]);
            if ((scan_count != 2) ||
                (feature_start[range_index] >= feature_end[range_index])) begin
                $fatal(1, "memory_ranges.dat feature tensor 区间非法");
            end
            if ((range_index > 0) &&
                (feature_start[range_index] < feature_end[range_index-1])) begin
                $fatal(1, "memory_ranges.dat feature tensor 区间重叠或无序");
            end
            if (((feature_start[range_index] < input_end) &&
                 (input_start < feature_end[range_index])) ||
                ((feature_start[range_index] < weights_end) &&
                 (weights_start < feature_end[range_index]))) begin
                $fatal(1, "memory_ranges.dat feature tensor 与输入/权重对象重叠");
            end
        end
        $fclose(range_file);
        model_initialized = 1'b1;
    end

    always_comb begin
        request_class = READ_FEATURE;
        if (mem_write) begin
            request_class = WRITE_FEATURE;
        end else if ((mem_addr >= input_start) && (mem_addr < input_end)) begin
            request_class = READ_INPUT;
        end else if ((mem_addr >= weights_start) && (mem_addr < weights_end)) begin
            request_class = READ_WEIGHTS;
        end
        scheduled_stall = stall_cycles(stall_index[request_class]);

        mem_ready = 1'b0;
        mem_rdata = 32'd0;
        mem_error_code = NONE;
        if (model_initialized && !reset && buffer_owner_pl && mem_valid) begin
            if (pending) begin
                if ((stall_remaining == 0) && (request_class == pending_class)) begin
                    mem_ready = 1'b1;
                end
            end else if (scheduled_stall == 0) begin
                mem_ready = 1'b1;
            end
            if (mem_ready) begin
                mem_error_code = request_error(mem_write, mem_addr,
                    mem_rstrb, mem_wstrb, fault_inject_valid, fault_inject_code);
                if ((mem_error_code == NONE) && !mem_write) begin
                    for (lane = 0; lane < 4; lane = lane + 1) begin
                        if (mem_rstrb[lane]) begin
                            mem_rdata[lane*8 +: 8] = read_byte(mem_addr + lane);
                        end
                    end
                end
            end
        end
    end

    always_ff @(posedge clk) begin : memory_state
        integer active_class;
        integer lane_index;
        integer requested_delay;
        if (reset || !buffer_owner_pl) begin
            pending <= 1'b0;
            stall_remaining <= 0;
            pending_class <= READ_INPUT;
        end else if (!mem_valid) begin
            pending <= 1'b0;
            stall_remaining <= 0;
        end else if (pending) begin
            if ((mem_addr != held_addr) || (mem_wdata != held_wdata) ||
                (mem_rstrb != held_rstrb) || (mem_wstrb != held_wstrb) ||
                (mem_write != held_write) ||
                (fault_inject_valid != held_fault_valid) ||
                (fault_inject_code != held_fault_code)) begin
                $fatal(1, "未握手 memory request 字段发生变化");
            end
            if (stall_remaining > 0) begin
                stall_remaining <= stall_remaining - 1;
            end else if (mem_ready) begin
                if ((mem_error_code == NONE) && mem_write) begin
                    for (lane_index = 0; lane_index < 4; lane_index = lane_index + 1) begin
                        if (mem_wstrb[lane_index]) begin
                            store_byte(mem_addr + lane_index,
                                       mem_wdata[lane_index*8 +: 8]);
                        end
                    end
                end
                stall_index[pending_class] <= (stall_index[pending_class] + 1) % 5;
                pending <= 1'b0;
            end
        end else begin
            active_class = request_class;
            requested_delay = scheduled_stall;
            held_addr <= mem_addr;
            held_wdata <= mem_wdata;
            held_rstrb <= mem_rstrb;
            held_wstrb <= mem_wstrb;
            held_write <= mem_write;
            held_fault_valid <= fault_inject_valid;
            held_fault_code <= fault_inject_code;
            if (mem_ready) begin
                if ((mem_error_code == NONE) && mem_write) begin
                    for (lane_index = 0; lane_index < 4; lane_index = lane_index + 1) begin
                        if (mem_wstrb[lane_index]) begin
                            store_byte(mem_addr + lane_index,
                                       mem_wdata[lane_index*8 +: 8]);
                        end
                    end
                end
                stall_index[active_class] <= (stall_index[active_class] + 1) % 5;
            end else begin
                pending_class <= active_class;
                stall_remaining <= requested_delay - 1;
                pending <= 1'b1;
            end
        end
    end
endmodule
