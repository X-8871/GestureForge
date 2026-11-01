// 所选真实 tile 的memory加载及输出回归；白盒只设置起始tile/group。
`timescale 1ns/1ps
module tb_s2a_conv_tile_memory;
    import s2a_network_descriptor_pkg::*;
    logic clk=0, hard_reset=0, abort=0, start_valid=0;
    logic start_ready,result_valid,busy,cancel;
    logic [2:0] result_error_code;
    logic req_valid,req_ready=0,req_write,rsp_valid=0;
    logic [31:0] req_addr,req_wdata,rsp_data=0;
    logic [3:0] req_rstrb,req_wstrb;
    integer layer_id=0,fd,ordinal,ty,tx,group_base,th,tw,ph,pw,ci,k,lanes,outputs;
    integer i,l,j,b,idx,oc,y,x,ic,py,px,address,selected_lane,cls,wait_remaining=-1;
    integer counts[0:2],stalls[0:2],seen_count=0,total_outputs=0,case_count=0,required_cases=0;
    integer cycles,expected_reads,actual_features,actual_weights;
    logic [7:0] patch[0:51199],weights[0:36863],golden[0:511];
    logic seen[0:511];
    logic [31:0] hdr[0:12],held_addr,held_wdata;
    logic [3:0] held_rstrb,held_wstrb;
    logic held_write,pending_response=0;
    always #5 clk=~clk;
    s2a_conv_tile_engine dut (
        .clk(clk), .hard_reset(hard_reset), .abort(abort), .buffer_owner_pl(1'b1),
        .start_valid(start_valid), .start_ready(start_ready),
        .layer_index(layer_id), .weight_layer_index(layer_id),
        .input_base_address(S2A_INPUT_ADDRESS[layer_id][0]),
        .input_length_bytes(S2A_INPUT_LENGTH_BYTES[layer_id][0]),
        .input_batch_count({16'd0,S2A_INPUT_N[layer_id][0]}),
        .input_channels({16'd0,S2A_INPUT_C[layer_id][0]}),
        .input_height({16'd0,S2A_INPUT_H[layer_id][0]}),
        .input_width({16'd0,S2A_INPUT_W[layer_id][0]}),
        .output_base_address(S2A_OUTPUT_ADDRESS[layer_id]),
        .output_length_bytes(S2A_OUTPUT_LENGTH_BYTES[layer_id]),
        .output_batch_count({16'd0,S2A_OUTPUT_N[layer_id]}),
        .output_channels({16'd0,S2A_OUTPUT_C[layer_id]}),
        .output_height({16'd0,S2A_OUTPUT_H[layer_id]}),
        .output_width({16'd0,S2A_OUTPUT_W[layer_id]}),
        .kernel_height({24'd0,S2A_KERNEL_H[layer_id]}),
        .kernel_width({24'd0,S2A_KERNEL_W[layer_id]}),
        .stride_y({24'd0,S2A_STRIDE_H[layer_id]}),
        .stride_x({24'd0,S2A_STRIDE_W[layer_id]}),
        .pad_left({24'd0,S2A_PADDING_LEFT[layer_id]}),
        .pad_right({24'd0,S2A_PADDING_RIGHT[layer_id]}),
        .pad_top({24'd0,S2A_PADDING_TOP[layer_id]}),
        .pad_bottom({24'd0,S2A_PADDING_BOTTOM[layer_id]}),
        .groups(32'd1), .padding_value_int8(32'sd0),
        .weight_package_base_address(S2A_GF8_PACKAGE_BASE[layer_id]),
        .weight_package_length_bytes(S2A_GF8_PACKAGE_LENGTH[layer_id]),
        .quantized_weight_offset(S2A_GF8_WEIGHT_OFFSET[layer_id]),
        .quantized_weight_bytes(S2A_GF8_WEIGHT_BYTES[layer_id]),
        // 描述符包为 linear=1/leaky=2；engine 接口为 linear=0/leaky=1。
        .output_batch(32'd0), .activation_mode((S2A_ACTIVATION[layer_id] == S2A_ACT_LEAKY) ? 2'd1 : 2'd0),
        .backend_cancel(cancel), .backend_req_valid(req_valid), .backend_req_ready(req_ready),
        .backend_req_write(req_write), .backend_req_addr(req_addr), .backend_req_wdata(req_wdata),
        .backend_req_rstrb(req_rstrb), .backend_req_wstrb(req_wstrb),
        .backend_rsp_valid(rsp_valid), .backend_rsp_rdata(rsp_data), .backend_rsp_error(3'd0),
        .busy(busy), .result_valid(result_valid), .result_ready(1'b0),
        .result_error_code(result_error_code)
    );

    function automatic integer pattern(input integer n);
        case(n%5)
            0: pattern=0; 1: pattern=1; 2: pattern=2; 3: pattern=7; default: pattern=3;
        endcase
    endfunction

    task automatic read_word(output logic [31:0] value);
        integer n,v;
        begin
            value=0;
            for(n=0;n<4;n=n+1) begin
                v=$fgetc(fd); if(v<0) $fatal(1,"截断fixture");
                value=value|((v&255)<<(n*8));
            end
        end
    endtask

    // 在下降沿准备ready/response，上升沿唯一接受请求。
    always @(negedge clk) begin
        rsp_valid=0;
        if(hard_reset || abort || cancel) begin
            req_ready=0; pending_response=0; wait_remaining=-1;
        end else if(pending_response) begin
            rsp_valid=1; pending_response=0; req_ready=0;
        end else if(req_valid) begin
            if(wait_remaining<0) begin
                cls=req_write ? 2 : ((req_addr>=S2A_INPUT_ADDRESS[layer_id][0] && req_addr<S2A_INPUT_ADDRESS[layer_id][0]+S2A_INPUT_LENGTH_BYTES[layer_id][0]) ? 0 : 1);
                wait_remaining=pattern(counts[cls]);
                held_addr=req_addr; held_wdata=req_wdata; held_rstrb=req_rstrb;
                held_wstrb=req_wstrb; held_write=req_write;
            end else if(req_addr!=held_addr || req_wdata!=held_wdata || req_rstrb!=held_rstrb || req_wstrb!=held_wstrb || req_write!=held_write)
                $fatal(1,"stall请求字段改变");
            req_ready=(wait_remaining==0);
            if(wait_remaining>0) begin wait_remaining=wait_remaining-1; stalls[cls]=stalls[cls]+1; end
        end else begin req_ready=0; wait_remaining=-1; end
    end

    always @(posedge clk) begin
        if(req_valid && req_ready && !hard_reset && !abort) begin
            selected_lane=-1;
            for(j=0;j<4;j=j+1) if((req_write ? req_wstrb : req_rstrb)==(1<<j)) selected_lane=j;
            if(selected_lane<0 || req_addr[1:0]!=0 || (req_write && req_rstrb!=0) || (!req_write && req_wstrb!=0))
                $fatal(1,"非法word/strobe");
            address=req_addr+selected_lane; rsp_data=0;
            if(req_write) begin
                idx=address-S2A_OUTPUT_ADDRESS[layer_id];
                oc=idx/(S2A_OUTPUT_H[layer_id]*S2A_OUTPUT_W[layer_id]);
                y=(idx/S2A_OUTPUT_W[layer_id])%S2A_OUTPUT_H[layer_id]; x=idx%S2A_OUTPUT_W[layer_id];
                if(oc<group_base || oc>=group_base+lanes || y<ty || y>=ty+th || x<tx || x>=tx+tw)
                    $fatal(1,"输出地址不在所选tile/group");
                idx=(oc-group_base)*th*tw+(y-ty)*tw+x-tx;
                if(seen[idx] || ((req_wdata>>(8*selected_lane))&255)!=golden[idx])
                    $fatal(1,"输出不符/重复 layer=%0d case=%0d idx=%0d",layer_id,ordinal,idx);
                if((req_wdata & ~(32'hff<<(8*selected_lane)))!=0) $fatal(1,"未选write lane非零");
                seen[idx]=1; seen_count=seen_count+1;
            end else if(address>=S2A_INPUT_ADDRESS[layer_id][0] && address<S2A_INPUT_ADDRESS[layer_id][0]+S2A_INPUT_LENGTH_BYTES[layer_id][0]) begin
                idx=address-S2A_INPUT_ADDRESS[layer_id][0];
                ic=idx/(S2A_INPUT_H[layer_id][0]*S2A_INPUT_W[layer_id][0]);
                y=(idx/S2A_INPUT_W[layer_id][0])%S2A_INPUT_H[layer_id][0]; x=idx%S2A_INPUT_W[layer_id][0];
                py=y-ty*S2A_STRIDE_H[layer_id]+S2A_PADDING_TOP[layer_id];
                px=x-tx*S2A_STRIDE_W[layer_id]+S2A_PADDING_LEFT[layer_id];
                if(ic>=ci || py<0 || py>=ph || px<0 || px>=pw) $fatal(1,"feature地址超patch");
                rsp_data={24'd0,patch[ic*ph*pw+py*pw+px]}<<(selected_lane*8);
                actual_features=actual_features+1;
            end else begin
                idx=address-S2A_GF8_PACKAGE_BASE[layer_id]-S2A_GF8_WEIGHT_OFFSET[layer_id]-group_base*k;
                if(idx<0 || idx>=lanes*k) $fatal(1,"GF8地址越组");
                rsp_data={24'd0,weights[idx]}<<(selected_lane*8); actual_weights=actual_weights+1;
            end
            counts[cls]=counts[cls]+1; wait_remaining=-1; pending_response=1;
        end
    end

    initial begin
        if(!$value$plusargs("CASES=%d",required_cases) || required_cases<=0) $fatal(1,"必须给定cases");
        fd=$fopen("cases.bin","rb"); if(fd==0) $fatal(1,"fixture缺失");
        hard_reset=1; repeat(2) @(negedge clk); #1; hard_reset=0;
        while(!$feof(fd)) begin
            b=$fgetc(fd); if(b<0) break; hdr[0]=b;
            for(i=1;i<4;i=i+1) begin b=$fgetc(fd); if(b<0) $fatal(1,"截断header"); hdr[0]=hdr[0]|((b&255)<<(8*i)); end
            for(i=1;i<13;i=i+1) read_word(hdr[i]);
            layer_id=hdr[0]; ordinal=hdr[1]; ty=hdr[2];tx=hdr[3];group_base=hdr[4];
            th=hdr[5];tw=hdr[6];ph=hdr[7];pw=hdr[8];ci=hdr[9];k=hdr[10];lanes=hdr[11];outputs=hdr[12];
            if(layer_id>=38 || ci*ph*pw>51200 || lanes*k>36864 || outputs!=lanes*th*tw || outputs>512) $fatal(1,"fixture尺寸非法");
            for(i=0;i<ci*ph*pw;i=i+1) begin b=$fgetc(fd); if(b<0) $fatal(1,"截断patch"); patch[i]=b[7:0]; end
            for(i=0;i<lanes*k;i=i+1) begin b=$fgetc(fd); if(b<0) $fatal(1,"截断weight"); weights[i]=b[7:0]; end
            for(i=0;i<outputs;i=i+1) begin b=$fgetc(fd); if(b<0) $fatal(1,"截断golden"); golden[i]=b[7:0];seen[i]=0; end
            seen_count=0;actual_features=0;actual_weights=0;expected_reads=0;
            for(i=0;i<3;i=i+1) begin counts[i]=0;stalls[i]=0;end
            for(py=0;py<ph;py=py+1) for(px=0;px<pw;px=px+1)
                if(ty*S2A_STRIDE_H[layer_id]+py>=S2A_PADDING_TOP[layer_id] && ty*S2A_STRIDE_H[layer_id]+py-S2A_PADDING_TOP[layer_id]<S2A_INPUT_H[layer_id][0] && tx*S2A_STRIDE_W[layer_id]+px>=S2A_PADDING_LEFT[layer_id] && tx*S2A_STRIDE_W[layer_id]+px-S2A_PADDING_LEFT[layer_id]<S2A_INPUT_W[layer_id][0]) expected_reads=expected_reads+ci;
            @(negedge clk); #1;start_valid=1;
            @(negedge clk); #1;start_valid=0;
            @(negedge clk); #1;
            if(dut.state!=dut.ST_TILE_PREP) $fatal(1,"真实descriptor被拒绝");
            dut.tile_start_y=ty;dut.tile_start_x=tx;
            cycles=0;
            while(dut.state!=dut.ST_WEIGHT_PREP) begin
                @(negedge clk);#1;cycles=cycles+1;
                if(result_valid || cycles>1000000) $fatal(1,"patch加载失败/超时");
            end
            dut.output_group_base=group_base;
            while(dut.state!=dut.ST_ADVANCE) begin
                @(negedge clk);#1;cycles=cycles+1;
                if(result_valid || cycles>2000000) $fatal(1,"tile执行失败/超时 error=%0d",result_error_code);
            end
            if(seen_count!=outputs || actual_features!=expected_reads || actual_weights!=lanes*k)
                $fatal(1,"传输计数不完整 got=%0d/%0d/%0d expected=%0d/%0d/%0d",seen_count,actual_features,actual_weights,outputs,expected_reads,lanes*k);
            for(i=0;i<outputs;i=i+1) if(!seen[i]) $fatal(1,"缺输出");
            abort=1; @(negedge clk);#1;abort=0;#1;
            if(!start_ready) $fatal(1,"取消未恢复");
            case_count=case_count+1;total_outputs=total_outputs+outputs;
            $display("CHECKPOINT TILE_MEMORY layer=%0d case=%0d cycles=%0d feature=%0d weight=%0d output=%0d stalls=%0d/%0d/%0d",layer_id,ordinal,cycles,actual_features,actual_weights,outputs,stalls[0],stalls[1],stalls[2]);
        end
        if(case_count!=required_cases) $fatal(1,"用例数不完整");
        $display("PASS TILE_MEMORY cases=%0d outputs=%0d",case_count,total_outputs);$finish;
    end
endmodule
