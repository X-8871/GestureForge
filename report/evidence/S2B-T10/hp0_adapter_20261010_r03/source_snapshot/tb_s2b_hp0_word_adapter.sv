`timescale 1ns/1ps
module tb_s2b_hp0_word_adapter;
    logic clk=0, cold_reset=0, run_enable=0, cancel=0, clear_safe=0;
    logic [63:0] run_epoch=0;
    logic mem_valid=0, mem_write=0;
    logic [31:0] mem_addr=0, mem_wdata=0, mem_rdata;
    logic [3:0] mem_rstrb=0, mem_wstrb=0;
    logic mem_ready;
    logic [2:0] mem_error_code;
    logic [5:0] m_axi_arid, m_axi_awid, m_axi_wid, m_axi_rid=0, m_axi_bid=0;
    logic [31:0] m_axi_araddr, m_axi_awaddr;
    logic [3:0] m_axi_arlen, m_axi_awlen;
    logic [2:0] m_axi_arsize, m_axi_awsize;
    logic [1:0] m_axi_arburst, m_axi_awburst, m_axi_arlock, m_axi_awlock;
    logic [3:0] m_axi_arcache, m_axi_awcache, m_axi_arqos, m_axi_awqos;
    logic [2:0] m_axi_arprot, m_axi_awprot;
    logic m_axi_arvalid, m_axi_awvalid, m_axi_wvalid, m_axi_wlast;
    logic m_axi_arready=0, m_axi_awready=0, m_axi_wready=0;
    logic [63:0] m_axi_wdata, m_axi_rdata=0;
    logic [7:0] m_axi_wstrb;
    logic [1:0] m_axi_rresp=0, m_axi_bresp=0;
    logic m_axi_rlast=1, m_axi_rvalid=0, m_axi_bvalid=0, m_axi_rready, m_axi_bready;
    logic ledger_empty, recovery_required, protocol_isolated, first_fault_valid;
    logic [63:0] ledger_epoch;
    logic [7:0] first_fault_code, fault_event_code;
    logic [31:0] first_fault_address, fault_event_address;
    logic fault_event_valid, req_withdrawn, clear_rejected;
    s2b_hp0_word_adapter dut (.*);
    int cycles=0, logical_count=0, ar_count=0, aw_count=0, w_count=0, r_count=0, b_count=0;
    int vector_count=0, directed_count=0;
    logic old_ar_stall=0, old_aw_stall=0, old_w_stall=0;
    logic [59:0] old_ar_payload, old_aw_payload;
    logic [78:0] old_w_payload;
    int unsigned rng=32'h2b101010;

    function automatic int jitter();
        // 固定种子的轻量总线背压；不依赖仿真器的全局随机状态。
        rng = rng ^ (rng << 13);
        rng = rng ^ (rng >> 17);
        rng = rng ^ (rng << 5);
        return int'(rng % 4);
    endfunction
    function automatic logic [7:0] memory_byte(input logic [31:0] address);
        return 8'((address * 32'd37) ^ (address >> 8) ^ 32'ha5);
    endfunction
    function automatic logic [63:0] memory_bus(input logic [31:0] address);
        logic [63:0] result;
        for (int i=0; i<8; i++) result[8*i +: 8] = memory_byte((address & 32'hfffffff8) + 32'(i));
        return result;
    endfunction
    task automatic must(input logic condition, input string reason);
        if (!condition) $fatal(1, "cycle=%0d vector=%0d directed=%0d %s", cycles, vector_count, directed_count, reason);
    endtask
    task automatic step();
        logic [59:0] ar_payload, aw_payload;
        logic [78:0] w_payload;
        #1;
        ar_payload = {m_axi_arid,m_axi_araddr,m_axi_arlen,m_axi_arsize,m_axi_arburst,
                      m_axi_arlock,m_axi_arcache,m_axi_arprot,m_axi_arqos};
        aw_payload = {m_axi_awid,m_axi_awaddr,m_axi_awlen,m_axi_awsize,m_axi_awburst,
                      m_axi_awlock,m_axi_awcache,m_axi_awprot,m_axi_awqos};
        w_payload = {m_axi_wid,m_axi_wdata,m_axi_wstrb,m_axi_wlast};
        if (!cold_reset) begin
            if (old_ar_stall) must(m_axi_arvalid && ar_payload==old_ar_payload, "AR VALID/全部payload在stall中变化");
            if (old_aw_stall) must(m_axi_awvalid && aw_payload==old_aw_payload, "AW VALID/全部payload在stall中变化");
            if (old_w_stall) must(m_axi_wvalid && w_payload==old_w_payload, "W VALID/全部payload在stall中变化");
            must(m_axi_arid==0 && m_axi_awid==0 && m_axi_wid==0 && m_axi_arlen==0 && m_axi_awlen==0 &&
                 m_axi_arburst==1 && m_axi_awburst==1 && m_axi_arlock==0 && m_axi_awlock==0 &&
                 m_axi_arcache==0 && m_axi_awcache==0 && m_axi_arprot==0 && m_axi_awprot==0 &&
                 m_axi_arqos==0 && m_axi_awqos==0 && m_axi_awsize==2 && m_axi_wlast &&
                 m_axi_rready && m_axi_bready, "固定AXI3属性或恢复READY错误");
            if (mem_ready) begin
                must(run_enable && !cancel && !protocol_isolated && !fault_event_valid, "取消/隔离/同沿故障仍交付");
                logical_count++;
            end
            if (m_axi_arvalid && m_axi_arready) ar_count++;
            if (m_axi_awvalid && m_axi_awready) aw_count++;
            if (m_axi_wvalid && m_axi_wready) w_count++;
            if (m_axi_rvalid) r_count++;
            if (m_axi_bvalid) b_count++;
        end
        old_ar_stall = !cold_reset && m_axi_arvalid && !m_axi_arready;
        old_aw_stall = !cold_reset && m_axi_awvalid && !m_axi_awready;
        old_w_stall = !cold_reset && m_axi_wvalid && !m_axi_wready;
        old_ar_payload=ar_payload; old_aw_payload=aw_payload; old_w_payload=w_payload;
        #4; clk=1; #1; clk=0; #4;
        cycles++;
    endtask
    task automatic initialize();
        cold_reset=1; run_enable=0; cancel=0; clear_safe=0; mem_valid=0;
        m_axi_arready=0; m_axi_awready=0; m_axi_wready=0;
        m_axi_rvalid=0; m_axi_bvalid=0; m_axi_rid=0; m_axi_bid=0;
        m_axi_rresp=0; m_axi_bresp=0; m_axi_rlast=1;
        step(); cold_reset=0; run_enable=1; run_epoch=64'h1234567810000042;
        must(ledger_empty && !recovery_required && !protocol_isolated, "冷初始化状态");
    endtask
    task automatic start_request(input bit write_req, input logic [31:0] address,
                                 input logic [3:0] mask);
        mem_valid=1; mem_write=write_req; mem_addr=address; mem_wdata=32'hd4c3b2a1;
        mem_rstrb=write_req ? 4'd0 : mask; mem_wstrb=write_req ? mask : 4'd0;
        step();
        must(!m_axi_arvalid && !m_axi_awvalid && !m_axi_wvalid && !mem_ready, "锁存沿提前声明/交付");
        must(ledger_epoch==run_epoch && !ledger_empty, "请求epoch未捕获");
    endtask
    task automatic declare_request();
        step();
        must(mem_write ? (m_axi_awvalid && m_axi_wvalid && !m_axi_arvalid) :
                         (m_axi_arvalid && !m_axi_awvalid && !m_axi_wvalid), "首次通道声明错误");
    endtask
    task automatic accept_ar();
        m_axi_arready=1; step(); m_axi_arready=0;
        must(!m_axi_arvalid && !ledger_empty, "AR接受后等待丢失");
    endtask
    task automatic return_r(input logic [1:0] response, input logic [5:0] id, input bit last);
        m_axi_rresp=response; m_axi_rid=id; m_axi_rlast=last;
        m_axi_rdata=memory_bus(m_axi_araddr); m_axi_rvalid=1; step(); m_axi_rvalid=0;
        m_axi_rid=0; m_axi_rlast=1; m_axi_rresp=0;
    endtask
    task automatic return_b(input logic [1:0] response, input logic [5:0] id);
        m_axi_bresp=response; m_axi_bid=id; m_axi_bvalid=1; step(); m_axi_bvalid=0;
        m_axi_bid=0; m_axi_bresp=0;
    endtask
    task automatic finish_logical(input logic [31:0] expected_data, input logic [2:0] expected_error);
        int before_count;
        before_count=logical_count;
        must(mem_ready && mem_rdata==expected_data && mem_error_code==expected_error, "逻辑响应与独立字节参考不符");
        step(); mem_valid=0; step();
        must(logical_count==before_count+1 && ledger_empty && !mem_ready, "逻辑交付次数/空账本错误");
    endtask
    task automatic clear_diagnostic(input bit should_accept);
        run_enable=0; clear_safe=1; #1;
        must(clear_rejected==!should_accept, "clear门禁判断错误");
        step(); clear_safe=0;
        if (should_accept) must(!recovery_required && !first_fault_valid && !protocol_isolated, "safe clear未清诊断");
    endtask
    task automatic drain_write();
        m_axi_awready=1; m_axi_wready=1; step(); m_axi_awready=0; m_axi_wready=0;
        return_b(0,0);
        must(ledger_empty && !mem_ready, "取消写合法排空没有闭合");
    endtask
    task automatic check_fault(input logic [7:0] code, input bit isolated);
        must(recovery_required && first_fault_valid && first_fault_code==code &&
             first_fault_address==mem_addr && protocol_isolated==isolated && !mem_ready, "首错/隔离诊断错误");
    endtask

    task automatic vector_case(input bit wr, input logic [31:0] address, data,
        input logic [3:0] rmask, wmask, input bit allowed,
        input logic [2:0] error_code, input logic [31:0] expected_data);
        int expected_beats, before_ar, before_aw, before_w;
        logic [31:0] expected_address;
        logic [63:0] expected_wdata;
        logic [7:0] expected_wmask;
        initialize();
        mem_valid=1; mem_write=wr; mem_addr=address; mem_wdata=data;
        mem_rstrb=rmask; mem_wstrb=wmask;
        before_ar=ar_count; before_aw=aw_count; before_w=w_count;
        step();
        must(!m_axi_arvalid && !m_axi_awvalid && !m_axi_wvalid, "捕获沿发AXI");
        if (!allowed) begin
            must(!recovery_required && !first_fault_valid && !fault_event_valid, "非法请求交付前提前恢复");
            finish_logical(0,error_code);
            must(recovery_required && first_fault_code=={5'd0,error_code}, "非法请求交付沿不锁住epoch");
            mem_valid=1; step(); step(); mem_valid=0;
            must(ar_count==before_ar && aw_count==before_aw && w_count==before_w && !mem_ready,
                 "非法请求/同epoch后继发出AXI");
            clear_diagnostic(1);
        end else if (!wr) begin
            expected_beats=0;
            for (int lane=0; lane<4; lane++) begin
                if ((rmask==15 && lane==0) || (rmask!=15 && rmask[lane])) begin
                    expected_beats++;
                    step();
                    expected_address=address+32'h10000000+((rmask==15) ? 32'd0 : 32'(lane));
                    must(m_axi_arvalid && m_axi_araddr==expected_address && m_axi_arsize==((rmask==15)?2:0),
                         "读访问字节集合/次序错误");
                    repeat(jitter()) step(); accept_ar(); repeat(jitter()) step(); return_r(0,0,1);
                    if (rmask!=15 && (int'(rmask) >> (lane+1))!=0) must(!mem_ready, "部分子读提前交付");
                end
            end
            finish_logical(expected_data,0);
            must(ar_count-before_ar==expected_beats && aw_count==before_aw && w_count==before_w &&
                 !recovery_required && !protocol_isolated, "正常读物理次数/门禁错误");
        end else begin
            declare_request();
            expected_wdata={32'd0,data} << ((address%8)*8);
            expected_wmask={4'd0,wmask} << (address%8);
            must(m_axi_awaddr==address+32'h10000000 && m_axi_wdata==expected_wdata && m_axi_wstrb==expected_wmask,
                 "窄写数据/byte lane错误");
            // 三种序列均独立背压；第三种覆盖 AXI3 合法先B后AW。
            case (vector_count%3)
                0: begin
                    repeat(jitter()) step(); m_axi_awready=1; step(); m_axi_awready=0;
                    repeat(jitter()) step(); m_axi_wready=1; step(); m_axi_wready=0; return_b(0,0);
                end
                1: begin
                    m_axi_wready=1; step(); m_axi_wready=0; repeat(jitter()) step();
                    m_axi_awready=1; step(); m_axi_awready=0; return_b(0,0);
                end
                2: begin
                    m_axi_wready=1; step(); m_axi_wready=0; return_b(0,0);
                    must(m_axi_awvalid && !ledger_empty && !mem_ready && !recovery_required, "早B丢失AW责任");
                    repeat(jitter()) step(); m_axi_awready=1; step(); m_axi_awready=0;
                end
            endcase
            finish_logical(0,0);
            must(aw_count-before_aw==1 && w_count-before_w==1 && ar_count==before_ar && !recovery_required,
                 "正常写物理次数/门禁错误");
        end
    endtask

    task automatic directed();
        int before_count, before_ar;
        // 声明前取消、撤销及关闭 RUN，不产生任何新 VALID。
        for (int why=0; why<3; why++) begin
            directed_count++; initialize(); start_request(0,32'h01000004,15);
            if (why==0) cancel=1;
            if (why==1) mem_valid=0;
            if (why==2) run_enable=0;
            #1; if (why==1) must(req_withdrawn, "撤销脉冲缺失");
            step(); must(ledger_empty && recovery_required && !first_fault_valid && !m_axi_arvalid, "声明前取消行为");
            cancel=0; mem_valid=0; clear_diagnostic(1);
        end
        // 各 AW/W 接受组合的取消，含取消沿握手。
        for (int combo=0; combo<4; combo++) begin
            directed_count++; initialize(); start_request(1,32'h01000004,9); declare_request();
            cancel=1; m_axi_awready=1'(combo&1); m_axi_wready=1'((combo>>1)&1); step();
            cancel=0; mem_valid=0; m_axi_awready=0; m_axi_wready=0;
            must(!ledger_empty && recovery_required && !first_fault_valid, "取消沿写握手未入账");
            drain_write(); clear_diagnostic(1);
        end
        // AR 声明与已接受两种取消，必须继续等合法 R。
        for (int accepted=0; accepted<2; accepted++) begin
            directed_count++; initialize(); start_request(0,32'h01000000,15); declare_request();
            if (accepted!=0) accept_ar();
            cancel=1; m_axi_arready=1; step(); cancel=0; m_axi_arready=0; mem_valid=0;
            must(!ledger_empty && recovery_required, "取消读提前丢账");
            return_r(0,0,1); must(ledger_empty && !mem_ready, "取消读不合法排空"); clear_diagnostic(1);
        end
        // R/B响应同沿取消，以及独立RESP槽尚未交付时取消。
        for (int wr=0; wr<2; wr++) begin
            for (int at_slot=0; at_slot<2; at_slot++) begin
                directed_count++; initialize(); start_request(1'(wr),32'h01000000,15); declare_request();
                if (wr!=0) begin m_axi_awready=1; m_axi_wready=1; step(); m_axi_awready=0; m_axi_wready=0; end
                else accept_ar();
                if (at_slot==0) cancel=1;
                if (wr!=0) return_b(0,0); else return_r(0,0,1);
                if (at_slot!=0) begin must(mem_ready && !ledger_empty, "RESP槽没有保留逻辑责任"); cancel=1; end
                before_count=logical_count; step(); cancel=0; mem_valid=0;
                must(ledger_empty && logical_count==before_count && recovery_required, "取消响应仍交付");
                clear_diagnostic(1);
            end
        end
        // byte子读之间的撤销，不启动未声明的剩余byte。
        directed_count++; initialize(); start_request(0,32'h01a474cc,3); declare_request(); accept_ar();
        return_r(0,0,1); before_ar=ar_count; mem_valid=0; step(); repeat(3) step();
        must(ledger_empty && recovery_required && !first_fault_valid && ar_count==before_ar && !m_axi_arvalid,
             "撤销后发起剩余byte"); clear_diagnostic(1);
        // 所有公开请求payload字段逐bit变化都隔离，已声明字段保持。
        for (int field=0; field<5; field++) begin
            directed_count++; initialize(); start_request(1,32'h01000000,5); declare_request();
            case(field)
                0: mem_write=0;
                1: mem_addr^=4;
                2: mem_wdata^=32'h80000000;
                3: mem_rstrb=1;
                4: mem_wstrb=1;
            endcase
            #1; must(fault_event_valid && fault_event_code==6 && fault_event_address==32'h01000000,
                     "payload变化无当前沿事件"); step();
            must(protocol_isolated && recovery_required && first_fault_code==6 && first_fault_address==32'h01000000,
                 "payload变化隔离诊断"); mem_valid=0; drain_write(); clear_diagnostic(0);
        end
        // held epoch违规变更不替换旧账本epoch。
        directed_count++; initialize(); start_request(0,32'h01000000,15); declare_request();
        run_epoch++; step(); must(ledger_epoch==64'h1234567810000042 && protocol_isolated && first_fault_code==6,
                                 "epoch变化替换旧归属"); mem_valid=0; accept_ar(); return_r(0,0,1); clear_diagnostic(0);
        // 正常响应错误、EXOKAY、非法 ID/LAST、早响应及随后合法响应。
        for (int kind=0; kind<7; kind++) begin
            directed_count++; initialize(); start_request(0,32'h01000000,15); declare_request();
            if (kind!=6) accept_ar();
            case(kind)
                0: return_r(2,0,1);
                1: return_r(3,0,1);
                2: return_r(1,0,1);
                3: return_r(0,1,1);
                4: return_r(0,0,0);
                5: begin m_axi_rresp=2; m_axi_bvalid=1; m_axi_bresp=3; return_r(2,0,1); m_axi_bvalid=0; end
                6: return_r(0,0,1);
            endcase
            check_fault((kind==0)?8'd9:(kind==1)?8'd10:8'd11,kind>=2);
            mem_valid=0;
            if (kind==3 || kind==4 || kind==6) begin
                must(!ledger_empty, "非法R清除未证明账本");
                if (kind==6) accept_ar();
                return_r(0,0,1);
            end
            must(ledger_empty, "匹配R未闭账"); clear_diagnostic(kind<2);
        end
        for (int kind=0; kind<7; kind++) begin
            directed_count++; initialize(); start_request(1,32'h01000004,15); declare_request();
            // AW持续stall，检查早到B错误仍必须完成AW。
            if (kind!=4) begin m_axi_wready=1; step(); m_axi_wready=0; end
            case(kind)
                0: return_b(2,0);
                1: return_b(3,0);
                2: return_b(1,0);
                3: return_b(0,1);
                4: return_b(0,0);
                5: begin return_b(0,0); return_b(0,0); end
                6: begin return_b(2,0); return_b(0,1); end
            endcase
            check_fault((kind==0 || kind==6)?8'd9:(kind==1)?8'd10:8'd11,kind>=2);
            must(m_axi_awvalid && !ledger_empty, "早B清掉AW"); mem_valid=0;
            m_axi_awready=1; m_axi_wready=1; step(); m_axi_awready=0; m_axi_wready=0;
            if (kind==3 || kind==4) return_b(0,0);
            must(ledger_empty && !mem_ready, "早错B后物理闭账"); clear_diagnostic(kind<2);
        end
        // R重复发生在RESP槽，协议事件禁止原本即将交付的成功。
        directed_count++; initialize(); start_request(0,32'h01000000,15); declare_request(); accept_ar(); return_r(0,0,1);
        before_count=logical_count; return_r(0,0,1); must(logical_count==before_count && protocol_isolated && ledger_empty,
                                                      "重复R未拦截RESP槽"); clear_diagnostic(0);
        // late协议事件不得覆盖首错，但当前沿事件仍必须输出11。
        directed_count++; initialize(); start_request(0,32'h01000000,15); declare_request(); accept_ar(); return_r(2,0,1);
        m_axi_bvalid=1; #1; must(fault_event_valid && fault_event_code==11, "晚协议没有当前事件");
        step(); m_axi_bvalid=0; must(first_fault_code==9 && protocol_isolated, "晚协议覆盖首错/漏隔离");
        mem_valid=0; clear_diagnostic(0);
        // 永久stall有限观察窗口：只证明仍pending且VALID保持，不声称timeout控制器。
        for (int wr=0; wr<2; wr++) begin
            directed_count++; initialize(); start_request(1'(wr),32'h01000004,15); declare_request(); cancel=1; step();
            cancel=0; mem_valid=0; repeat(256) step();
            must(!ledger_empty && recovery_required && !first_fault_valid && !mem_ready &&
                 ((wr!=0) ? (m_axi_awvalid && m_axi_wvalid) : m_axi_arvalid), "永久stall账本/VALID丢失");
            clear_diagnostic(0);
        end
        // idle关闭RUN无取消诊断；idle cancel则锁住直到安全clear。
        directed_count++; initialize(); run_enable=0; step(); must(!recovery_required, "idle RUN关闭制造故障");
        run_enable=1; clear_safe=1; #1; must(clear_rejected, "RUN中clear被接受"); step(); clear_safe=0;
        cancel=1; step(); cancel=0; must(recovery_required && ledger_empty && !first_fault_valid, "idle cancel门禁");
        clear_diagnostic(1);
        // clear和无请求响应竞争时，应隔离而不清诊断。
        directed_count++; initialize(); run_enable=0; clear_safe=1; m_axi_rvalid=1; #1;
        must(clear_rejected && fault_event_code==11, "clear与异常响应竞争被接受"); step();
        clear_safe=0; m_axi_rvalid=0; must(protocol_isolated && first_fault_code==11, "clear掩盖响应隔离");
    endtask

    initial begin
        string vector_path;
        int descriptor, scanned;
        logic wr, allowed;
        logic [2:0] error_code;
        logic [31:0] address, data, expected_data;
        logic [3:0] rmask, wmask;
        must($value$plusargs("VECTORS=%s",vector_path), "缺少向量路径");
        descriptor=$fopen(vector_path,"r"); must(descriptor!=0, "向量打开失败");
        while (!$feof(descriptor)) begin
            scanned=$fscanf(descriptor,"%h %h %h %h %h %h %h %h\n",wr,address,data,rmask,wmask,allowed,error_code,expected_data);
            if (scanned==8) begin
                vector_count++;
                vector_case(1'(wr),address,data,rmask,wmask,1'(allowed),3'(error_code),expected_data);
            end else must(scanned==-1, "向量格式错误");
        end
        $fclose(descriptor);
        directed();
        $display("PASS HP0_WORD_ADAPTER vectors=%0d directed=%0d cycles=%0d logical=%0d AR=%0d AW=%0d W=%0d R=%0d B=%0d",
                 vector_count,directed_count,cycles,logical_count,ar_count,aw_count,w_count,r_count,b_count);
        $finish;
    end
endmodule
