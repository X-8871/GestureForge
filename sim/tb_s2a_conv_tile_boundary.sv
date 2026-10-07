// 真实检测头黑盒遍历与独立异常测试；mode3 在首个输出点的归约索引 4（输入通道 4）白盒注入 INT32_MAX + 1*1，不代表真实 GF8 权重溢出。
`timescale 1ns/1ps
module tb_s2a_conv_tile_boundary;
    import s2a_network_descriptor_pkg::*;
    logic clk=0, hard_reset=1, abort=0, start_valid=0;
    logic start_ready, result_valid, busy, cancel;
    logic req_valid, req_ready, req_write, rsp_valid=0;
    logic [31:0] req_addr, req_data, rsp_data=0;
    logic [3:0] rstrb, wstrb;
    logic [2:0] rsp_error=0, result_error;
    integer layer_id=29, mode=0, cycles=0, reads=0, feature_reads=0, weight_reads=0, writes=0;
    integer class_count[0:2], class_stalls[0:2], wait_count=0, selected_lane, byte_address, index_work, transfer_class;
    integer fd, loaded, i, expected_error, requests_before;
    logic [7:0] weights[0:15359], expected[0:20279], features[0:173055];
    logic seen[0:20279];
    logic waiting=0;
    logic [31:0] held_addr, held_data;
    logic held_write;
    logic [3:0] held_rs, held_ws;
    string weight_file, golden_file, feature_file;
    integer expected_feature, expected_weight, expected_output;
    logic injected=0;
    always #5 clk=~clk;

    function automatic integer stalls(input integer n);
        case(n%5) 0:stalls=0; 1:stalls=1; 2:stalls=2; 3:stalls=7; default:stalls=3; endcase
    endfunction
    function automatic integer total_stalls(input integer n);
        integer j;
        begin total_stalls=(n/5)*13; for(j=0;j<n%5;j=j+1) total_stalls=total_stalls+stalls(j); end
    endfunction
    always_comb begin
        transfer_class=req_write ? 2 : ((req_addr >= S2A_GF8_PACKAGE_BASE[layer_id] && req_addr < S2A_GF8_PACKAGE_BASE[layer_id]+S2A_GF8_PACKAGE_LENGTH[layer_id]) ? 1 : 0);
        req_ready=req_valid && !hard_reset && !rsp_valid && ((waiting && wait_count==0) || (!waiting && stalls(class_count[transfer_class])==0));
    end

    s2a_conv_tile_engine dut(
        .clk(clk),.hard_reset(hard_reset),.abort(abort),.buffer_owner_pl(1'b1),
        .start_valid(start_valid),.start_ready(start_ready),.layer_index(layer_id),.weight_layer_index(layer_id),
        .input_base_address(mode==15 ? 32'hfffffff0 : S2A_INPUT_ADDRESS[layer_id][0]),
        .input_length_bytes(mode==14 ? S2A_INPUT_LENGTH_BYTES[layer_id][0]-1 : S2A_INPUT_LENGTH_BYTES[layer_id][0]),
        .input_batch_count({16'd0,S2A_INPUT_N[layer_id][0]}),.input_channels({16'd0,S2A_INPUT_C[layer_id][0]}),
        .input_height({16'd0,S2A_INPUT_H[layer_id][0]}),.input_width({16'd0,S2A_INPUT_W[layer_id][0]}),
        .output_base_address(S2A_OUTPUT_ADDRESS[layer_id]),
        .output_length_bytes(mode==13 ? S2A_OUTPUT_LENGTH_BYTES[layer_id]+S2A_OUTPUT_C[layer_id]*S2A_OUTPUT_W[layer_id] : S2A_OUTPUT_LENGTH_BYTES[layer_id]),
        .output_batch_count({16'd0,S2A_OUTPUT_N[layer_id]}),.output_channels({16'd0,S2A_OUTPUT_C[layer_id]}),
        .output_height(mode==13 ? {16'd0,S2A_OUTPUT_H[layer_id]}+1 : {16'd0,S2A_OUTPUT_H[layer_id]}),
        .output_width({16'd0,S2A_OUTPUT_W[layer_id]}),.kernel_height({24'd0,S2A_KERNEL_H[layer_id]}),
        .kernel_width({24'd0,S2A_KERNEL_W[layer_id]}),.stride_y({24'd0,S2A_STRIDE_H[layer_id]}),.stride_x({24'd0,S2A_STRIDE_W[layer_id]}),
        .pad_left({24'd0,S2A_PADDING_LEFT[layer_id]}),.pad_right({24'd0,S2A_PADDING_RIGHT[layer_id]}),
        .pad_top({24'd0,S2A_PADDING_TOP[layer_id]}),.pad_bottom({24'd0,S2A_PADDING_BOTTOM[layer_id]}),
        .groups(mode==12 ? 32'd2 : 32'd1),.padding_value_int8(32'sd0),
        .weight_package_base_address(S2A_GF8_PACKAGE_BASE[layer_id]),.weight_package_length_bytes(S2A_GF8_PACKAGE_LENGTH[layer_id]),
        .quantized_weight_offset(S2A_GF8_WEIGHT_OFFSET[layer_id]),.quantized_weight_bytes(S2A_GF8_WEIGHT_BYTES[layer_id]),
        .output_batch(32'd0),.activation_mode(mode==11 ? 2'd2 : 2'd0),
        .backend_cancel(cancel),.backend_req_valid(req_valid),.backend_req_ready(req_ready),.backend_req_write(req_write),
        .backend_req_addr(req_addr),.backend_req_wdata(req_data),.backend_req_rstrb(rstrb),.backend_req_wstrb(wstrb),
        .backend_rsp_valid(rsp_valid),.backend_rsp_rdata(rsp_data),.backend_rsp_error(rsp_error),
        .busy(busy),.result_valid(result_valid),.result_ready(1'b0),.result_error_code(result_error)
    );

    // 请求只在 ready 上升沿执行；停顿期间全部请求字段必须保持不变。
    always @(posedge clk) begin
        if (!hard_reset) begin
            cycles=cycles+1;
            if(cycles>10000000) $fatal(1,"周期 watchdog");
            rsp_valid<=0;
            if(waiting && (!req_valid || req_addr!=held_addr || req_data!=held_data || req_write!=held_write || rstrb!=held_rs || wstrb!=held_ws))
                $fatal(1,"停顿请求不稳定");
            if(req_valid && !req_ready && !rsp_valid) begin
                class_stalls[transfer_class]=class_stalls[transfer_class]+1;
                if(!waiting) begin
                    waiting=1; wait_count=stalls(class_count[transfer_class])-1;
                    held_addr=req_addr; held_data=req_data; held_write=req_write; held_rs=rstrb; held_ws=wstrb;
                end else wait_count=wait_count-1;
            end
            if(req_valid && req_ready) begin
                waiting=0;
                class_count[transfer_class]=class_count[transfer_class]+1;
                if(req_addr[1:0]!=0) $fatal(1,"地址未word对齐");
                case(req_write ? wstrb : rstrb)
                    1:selected_lane=0; 2:selected_lane=1; 4:selected_lane=2; 8:selected_lane=3;
                    default:$fatal(1,"非one-hot strobe");
                endcase
                byte_address=req_addr+selected_lane;
                rsp_data<=0; rsp_error<=0; rsp_valid<=1;
                if(req_write) begin
                    if(rstrb!=0 || byte_address<S2A_OUTPUT_ADDRESS[layer_id] || byte_address>=S2A_OUTPUT_ADDRESS[layer_id]+S2A_OUTPUT_LENGTH_BYTES[layer_id])
                        $fatal(1,"输出请求越界");
                    index_work=byte_address-S2A_OUTPUT_ADDRESS[layer_id];
                    if((mode!=0 && mode!=4) || seen[index_work] || ((req_data>>(8*selected_lane))&255)!=expected[index_work])
                        $fatal(1,"输出重复/异常/数值不符 index=%0d",index_work);
                    seen[index_work]=1; writes=writes+1;
                end else begin
                    if(wstrb!=0 || req_data!=0) $fatal(1,"读请求携带写字段");
                    reads=reads+1;
                    if(transfer_class==1) begin
                        index_work=byte_address-S2A_GF8_PACKAGE_BASE[layer_id]-S2A_GF8_WEIGHT_OFFSET[layer_id];
                        if(index_work<0 || index_work>=S2A_GF8_WEIGHT_BYTES[layer_id]) $fatal(1,"权重越界");
                        rsp_data<={24'd0,(mode==2 ? 8'h80 : weights[index_work])}<<(8*selected_lane);
                        weight_reads=weight_reads+1;
                    end else begin
                        if(byte_address<S2A_INPUT_ADDRESS[layer_id][0] || byte_address>=S2A_INPUT_ADDRESS[layer_id][0]+S2A_INPUT_LENGTH_BYTES[layer_id][0]) $fatal(1,"特征越界");
                        index_work=byte_address-S2A_INPUT_ADDRESS[layer_id][0];
                        rsp_data<={24'd0,(mode==1 ? 8'h80 : features[index_work])}<<(8*selected_lane);
                        feature_reads=feature_reads+1;
                    end
                end
            end
        end
    end

    // 不改变生产遍历状态；mode3 在首个输出点的归约索引 4（输入通道 4）白盒注入 INT32_MAX + 1*1，不代表真实 GF8 权重溢出。
    always @(negedge clk) begin
        if(mode==3 && !injected && dut.state==dut.ST_COMPUTE && dut.compute_reduction_index==4) begin
            if(!dut.feature_read_in_bounds) $fatal(1,"overflow注入tap不在输入边界内");
            dut.lane_accumulator[0]=32'sh7fffffff;
            dut.feature_read_data=8'sd1;
            dut.gen_weight_lane_bank[0].lane_weight_memory[4]=8'sd1;
            dut.weight_read_byte[0]=8'sd1;
            injected=1;
        end
    end

    initial begin
        if(!$value$plusargs("LAYER=%d",layer_id) || !$value$plusargs("MODE=%d",mode)) $fatal(1,"参数缺失");
        if(layer_id!=29 && layer_id!=36) $fatal(1,"不是真实head层");
        if(!$value$plusargs("WEIGHT=%s",weight_file) || !$value$plusargs("GOLDEN=%s",golden_file) || !$value$plusargs("FEATURE=%s",feature_file)) $fatal(1,"夹具参数缺失");
        fd=$fopen(weight_file,"rb"); if(!fd) $fatal(1,"权重文件缺失");
        loaded=$fread(weights,fd); $fclose(fd); if(loaded!=S2A_GF8_WEIGHT_BYTES[layer_id]) $fatal(1,"权重长度错误");
        fd=$fopen(golden_file,"rb"); if(!fd) $fatal(1,"黄金文件缺失");
        loaded=$fread(expected,fd); $fclose(fd); if(loaded!=S2A_OUTPUT_LENGTH_BYTES[layer_id]) $fatal(1,"黄金长度错误");
        fd=$fopen(feature_file,"rb"); if(!fd) $fatal(1,"特征文件缺失");
        loaded=$fread(features,fd); $fclose(fd); if(loaded!=S2A_INPUT_LENGTH_BYTES[layer_id][0]) $fatal(1,"特征长度错误");
        for(i=0;i<20280;i=i+1) seen[i]=0;
        for(i=0;i<3;i=i+1) begin class_count[i]=0; class_stalls[i]=0; end
        repeat(2) @(negedge clk); hard_reset=0;
        @(negedge clk); if(!start_ready) $fatal(1,"start未ready"); start_valid=1;
        @(negedge clk); start_valid=0;
        while(!result_valid) @(negedge clk);
        expected_error=0;
        if(mode==1 || mode==2 || mode==11 || mode==12 || mode==13) expected_error=1;
        if(mode==3) expected_error=7;
        if(mode==14) expected_error=3;
        if(mode==15) expected_error=2;
        if(result_error!=expected_error) $fatal(1,"错误码 mode=%0d actual=%0d expected=%0d",mode,result_error,expected_error);
        if(mode>=11 && reads+writes!=0) $fatal(1,"非法descriptor有memory副作用");
        if(mode==3 && !injected) $fatal(1,"overflow未注入");
        if(mode==0 || mode==4) begin
            expected_feature=S2A_INPUT_LENGTH_BYTES[layer_id][0];
            expected_weight=((S2A_OUTPUT_H[layer_id]+7)/8)*((S2A_OUTPUT_W[layer_id]+7)/8)*S2A_GF8_WEIGHT_BYTES[layer_id];
            expected_output=S2A_OUTPUT_LENGTH_BYTES[layer_id];
            if(feature_reads!=expected_feature || weight_reads!=expected_weight || writes!=expected_output) $fatal(1,"cache复用计数错误");
            for(i=0;i<expected_output;i=i+1) if(!seen[i]) $fatal(1,"输出缺失");
        end else if(writes!=0) $fatal(1,"异常时已有输出");
        for(i=0;i<3;i=i+1) if(class_stalls[i]!=total_stalls(class_count[i])) $fatal(1,"stall计数错误");
        requests_before=reads+writes;
        repeat(5) @(negedge clk);
        if(!result_valid || result_error!=expected_error || reads+writes!=requests_before) $fatal(1,"result背压期间发生副作用");
        $display("PASS TILE_BOUNDARY layer=%0d mode=%0d feature=%0d weight=%0d writes=%0d error=%0d cycles=%0d",layer_id,mode,feature_reads,weight_reads,writes,result_error,cycles);
        $finish;
    end
endmodule
