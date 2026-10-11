`timescale 1ns/1ps
module tb_s2b_control_csr;
    logic clk=0, cold_reset=0;
    logic [31:0] s_axi_awaddr=0, s_axi_wdata=0, s_axi_araddr=0;
    logic [3:0] s_axi_wstrb=15;
    logic s_axi_awvalid=0, s_axi_wvalid=0, s_axi_bready=0, s_axi_arvalid=0, s_axi_rready=0;
    logic s_axi_awready, s_axi_wready, s_axi_bvalid, s_axi_arready, s_axi_rvalid;
    logic [1:0] s_axi_bresp, s_axi_rresp;
    logic [31:0] s_axi_rdata;
    logic core_csr_valid, core_csr_write, core_csr_ready;
    logic [7:0] core_csr_addr;
    logic [31:0] core_csr_wdata, core_csr_rdata;
    logic core_mem_valid, ledger_empty, req_withdrawn, protocol_isolated;
    logic [63:0] ledger_epoch, run_epoch;
    logic [9:0] axi_progress_next;
    logic ledger_empty_next;
    logic fault_event_valid;
    logic [7:0] fault_event_code;
    logic [31:0] fault_event_address, fault_event_physical_address;
    logic [1:0] fault_event_resp;
    logic fault_event_write, fault_event_protocol, fault_event_address_valid;
    logic visibility_confirmed=1, run_enable, cancel, clear_safe;
    s2b_control_csr dut (.*);

    // mock只给独立公共CSR和公开账本输入；集成模式接真实runtime_shell及word_adapter。
    logic mock_mode=1, ready_enabled=1;
    logic [3:0] mock_status=0;
    logic [31:0] mock_error=0;
    logic mock_empty=1, mock_mem=0, mock_withdrawn=0, mock_isolated=0;
    logic mock_fault=0;
    logic [7:0] mock_fault_code=0;
    logic [1:0] mock_resp=0;
    logic mock_write=0, mock_protocol=0, mock_address_valid=0;
    logic [63:0] mock_ledger_epoch=0;
    logic mock_wrong_epoch=0;
    logic [31:0] runtime_rdata;
    logic runtime_ready;
    logic backend_req_valid=0, backend_req_ready, backend_req_write=0;
    logic [31:0] backend_req_addr=0, backend_req_wdata=32'h12345678;
    logic [3:0] backend_req_rstrb=0, backend_req_wstrb=0;
    logic backend_rsp_valid;
    logic [31:0] backend_rsp_rdata;
    logic [2:0] backend_rsp_error;
    logic [2:0] expected_backend_error=0;
    logic [31:0] expected_backend_data=0;
    logic operator_result_valid=0;
    logic [2:0] operator_error_code=0;
    logic mem_valid, mem_ready, mem_write;
    logic [31:0] mem_addr, mem_wdata, mem_rdata;
    logic [3:0] mem_rstrb, mem_wstrb;
    logic [2:0] mem_error_code;
    logic unused_backend_start, unused_backend_abort, unused_busy, unused_done, unused_error;
    logic unused_pl_owns_buffers, unused_head_output_valid;
    s2a_runtime_shell runtime (
        .clk(clk), .hard_reset(cold_reset), .csr_valid(core_csr_valid && !mock_mode && ready_enabled),
        .csr_ready(runtime_ready), .csr_write(core_csr_write), .csr_addr(core_csr_addr),
        .csr_wdata(core_csr_wdata), .csr_rdata(runtime_rdata),
        .backend_req_valid(backend_req_valid), .backend_req_ready(backend_req_ready),
        .backend_req_write(backend_req_write), .backend_req_addr(backend_req_addr),
        .backend_req_wdata(backend_req_wdata), .backend_req_rstrb(backend_req_rstrb),
        .backend_req_wstrb(backend_req_wstrb), .backend_rsp_valid(backend_rsp_valid),
        .backend_rsp_rdata(backend_rsp_rdata), .backend_rsp_error(backend_rsp_error),
        .operator_result_valid(operator_result_valid), .operator_error_code(operator_error_code),
        .backend_start(unused_backend_start), .backend_abort(unused_backend_abort),
        .busy(unused_busy), .done(unused_done), .error(unused_error),
        .pl_owns_buffers(unused_pl_owns_buffers), .head_output_valid(unused_head_output_valid),
        .mem_valid(mem_valid), .mem_ready(mem_ready), .mem_write(mem_write),
        .mem_addr(mem_addr), .mem_wdata(mem_wdata), .mem_rstrb(mem_rstrb), .mem_wstrb(mem_wstrb),
        .mem_rdata(mem_rdata), .mem_error_code(mem_error_code)
    );
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
    logic adapter_empty, adapter_isolated, adapter_withdrawn, adapter_recovery;
    logic adapter_first_valid, adapter_fault_valid, adapter_clear_rejected;
    logic [63:0] adapter_epoch;
    logic [7:0] adapter_first_code, adapter_fault_code;
    logic [31:0] adapter_first_address, adapter_fault_address, adapter_physical;
    logic [9:0] adapter_progress;
    logic [9:0] adapter_progress_next;
    logic adapter_empty_next;
    logic [1:0] adapter_resp;
    logic adapter_write, adapter_protocol, adapter_address_valid;
    s2b_hp0_word_adapter adapter (
        .clk(clk), .cold_reset(cold_reset), .run_enable(run_enable && !mock_mode),
        .cancel(cancel), .clear_safe(clear_safe), .run_epoch(run_epoch),
        .mem_valid(mem_valid), .mem_write(mem_write), .mem_addr(mem_addr), .mem_wdata(mem_wdata),
        .mem_rstrb(mem_rstrb), .mem_wstrb(mem_wstrb), .mem_ready(mem_ready),
        .mem_rdata(mem_rdata), .mem_error_code(mem_error_code),
        .m_axi_arid(m_axi_arid), .m_axi_awid(m_axi_awid), .m_axi_wid(m_axi_wid),
        .m_axi_araddr(m_axi_araddr), .m_axi_awaddr(m_axi_awaddr),
        .m_axi_arlen(m_axi_arlen), .m_axi_awlen(m_axi_awlen), .m_axi_arsize(m_axi_arsize), .m_axi_awsize(m_axi_awsize),
        .m_axi_arburst(m_axi_arburst), .m_axi_awburst(m_axi_awburst), .m_axi_arlock(m_axi_arlock), .m_axi_awlock(m_axi_awlock),
        .m_axi_arcache(m_axi_arcache), .m_axi_awcache(m_axi_awcache), .m_axi_arqos(m_axi_arqos), .m_axi_awqos(m_axi_awqos),
        .m_axi_arprot(m_axi_arprot), .m_axi_awprot(m_axi_awprot),
        .m_axi_arvalid(m_axi_arvalid), .m_axi_awvalid(m_axi_awvalid), .m_axi_wvalid(m_axi_wvalid), .m_axi_wlast(m_axi_wlast),
        .m_axi_arready(m_axi_arready), .m_axi_awready(m_axi_awready), .m_axi_wready(m_axi_wready),
        .m_axi_wdata(m_axi_wdata), .m_axi_wstrb(m_axi_wstrb),
        .m_axi_rid(m_axi_rid), .m_axi_bid(m_axi_bid), .m_axi_rdata(m_axi_rdata),
        .m_axi_rresp(m_axi_rresp), .m_axi_bresp(m_axi_bresp), .m_axi_rlast(m_axi_rlast),
        .m_axi_rvalid(m_axi_rvalid), .m_axi_bvalid(m_axi_bvalid), .m_axi_rready(m_axi_rready), .m_axi_bready(m_axi_bready),
        .ledger_empty(adapter_empty), .ledger_epoch(adapter_epoch),
        .recovery_required(adapter_recovery), .protocol_isolated(adapter_isolated),
        .first_fault_valid(adapter_first_valid), .first_fault_code(adapter_first_code), .first_fault_address(adapter_first_address),
        .fault_event_valid(adapter_fault_valid), .fault_event_code(adapter_fault_code), .fault_event_address(adapter_fault_address),
        .req_withdrawn(adapter_withdrawn), .clear_rejected(adapter_clear_rejected),
        .axi_progress(adapter_progress), .axi_progress_next(adapter_progress_next),
        .ledger_empty_next(adapter_empty_next), .fault_event_resp(adapter_resp), .fault_event_write(adapter_write),
        .fault_event_protocol(adapter_protocol), .fault_event_address_valid(adapter_address_valid), .fault_event_physical_address(adapter_physical)
    );
    assign core_csr_ready = ready_enabled && (mock_mode || runtime_ready);
    assign core_csr_rdata = mock_mode ? ((core_csr_addr == 4) ? {28'd0,mock_status} :
        (core_csr_addr == 8) ? mock_error : (32'ha0000000 | {24'd0,core_csr_addr})) : runtime_rdata;
    assign core_mem_valid = mock_mode ? mock_mem : mem_valid;
    assign ledger_empty = mock_mode ? mock_empty : adapter_empty;
    assign ledger_epoch = mock_mode ? (mock_wrong_epoch ? mock_ledger_epoch : run_epoch) : adapter_epoch;
    assign axi_progress_next = mock_mode ? 0 : adapter_progress_next;
    assign ledger_empty_next = mock_mode ? mock_empty : adapter_empty_next;
    assign req_withdrawn = mock_mode ? mock_withdrawn : adapter_withdrawn;
    assign protocol_isolated = mock_mode ? mock_isolated : adapter_isolated;
    assign fault_event_valid = mock_mode ? mock_fault : adapter_fault_valid;
    assign fault_event_code = mock_mode ? mock_fault_code : adapter_fault_code;
    assign fault_event_address = mock_mode ? 32'h01000000 : adapter_fault_address;
    assign fault_event_physical_address = mock_mode ? 32'h11000000 : adapter_physical;
    assign fault_event_resp = mock_mode ? mock_resp : adapter_resp;
    assign fault_event_write = mock_mode ? mock_write : adapter_write;
    assign fault_event_protocol = mock_mode ? mock_protocol : adapter_protocol;
    assign fault_event_address_valid = mock_mode ? mock_address_valid : adapter_address_valid;

    int cycles=0, directed=0, random_count=0, integration_count=0;
    int start_count=0, config_count=0, reset_cycle=-1, reset_count=0, ack_count=0, phase=0;
    int status_count=0, error_count=0, debug_count=0;
    int logical_responses=0;
    int phase_coverage[4]='{default:0};
    int runtime_phase_coverage[4]='{default:0};
    logic old_b=0, old_r=0;
    logic [1:0] saved_b;
    logic [33:0] saved_r;
    int unsigned rng=32'h2b111010;
    task automatic must(input logic cond, input string text);
        if (!cond) $fatal(1,"cycle=%0d directed=%0d integration=%0d %s",cycles,directed,integration_count,text);
    endtask
    task automatic tick();
        #1;
        if (!cold_reset) begin
            if (old_b) must(s_axi_bvalid && s_axi_bresp==saved_b,"B背压稳定");
            if (old_r) must(s_axi_rvalid && {s_axi_rresp,s_axi_rdata}==saved_r,"R背压稳定");
            must(!(mem_ready && cancel),"取消同沿禁止逻辑交付");
            must(m_axi_rready && m_axi_bready,"恢复维持响应消费");
            must(adapter_progress[0]==(m_axi_arvalid || adapter_progress[1]) &&
                adapter_progress[3]==(m_axi_awvalid || adapter_progress[4]) &&
                adapter_progress[5]==(m_axi_wvalid || adapter_progress[6]) &&
                adapter_progress[2]==adapter_progress[1],"公开注册账本诊断");
            if(adapter_progress[8]) must(!adapter_empty,"逻辑响应保留到交付或取消");
            must(m_axi_arid==0 && m_axi_awid==0 && m_axi_wid==0 && m_axi_arlen==0 && m_axi_awlen==0 &&
                m_axi_arburst==1 && m_axi_awburst==1 && m_axi_arlock==0 && m_axi_awlock==0 &&
                m_axi_arcache==0 && m_axi_awcache==0 && m_axi_arqos==0 && m_axi_awqos==0 &&
                m_axi_arprot==0 && m_axi_awprot==0 && m_axi_awsize==2 && m_axi_wlast,"固定物理属性");
            if (m_axi_arvalid) must(m_axi_arsize==0 || m_axi_arsize==2,"窄传输size");
            if (m_axi_awvalid) must(m_axi_awaddr==32'h11000000 && m_axi_wdata==64'h12345678 && m_axi_wstrb==15,"集成写payload");
            if (m_axi_arvalid) must(m_axi_araddr>=32'h10000000,"集成读地址");
            if (backend_rsp_valid) begin
                must(backend_rsp_error==expected_backend_error && backend_rsp_rdata==expected_backend_data,"集成逻辑响应");
                logical_responses++;
            end
            if (adapter_clear_rejected) $fatal(1,"控制器发出非法clear_safe");
            if (adapter_first_valid) must(adapter_recovery && adapter_first_code!=0,"适配器首错独立保持");
            if (adapter_address_valid) must(adapter_physical>=32'h10000000 + adapter_fault_address &&
                adapter_physical<32'h10000004 + adapter_fault_address,"实际事件地址关联");
            if (adapter_first_valid && adapter_first_code==9)
                must(adapter_first_address==32'h01000000 || adapter_first_address==0,"集成SLVERR首地址保持");
            if (core_csr_valid && core_csr_ready) begin
                if (!core_csr_write) begin
                    if (phase==0 || phase==3) begin must(core_csr_addr==4,"STATUS固定监视槽"); status_count++; end
                    if (phase==1) begin must(core_csr_addr==8,"ERROR固定监视槽"); error_count++; end
                    if (phase==2) debug_count++;
                end else begin
                    must(phase==2,"写只能用控制槽");
                    if (core_csr_addr==0 && core_csr_wdata==1) begin start_count++; if(mock_mode) mock_status=9; end
                    else if (core_csr_addr==0 && core_csr_wdata==2) begin
                        reset_cycle=cycles; reset_count++; if(mock_mode) begin mock_status=0; mock_error=0; end
                    end else if (core_csr_addr==8'h3c) begin ack_count++; if(mock_mode) mock_status=0; end
                    else config_count++;
                end
            end
        end
        old_b=!cold_reset && s_axi_bvalid && !s_axi_bready;
        old_r=!cold_reset && s_axi_rvalid && !s_axi_rready;
        saved_b=s_axi_bresp; saved_r={s_axi_rresp,s_axi_rdata};
        #4; clk=1; #1; clk=0; #4;
        if(cold_reset) phase=0; else phase=(phase+1)%4;
        cycles++;
    endtask
    task automatic idle_ticks(input int n); repeat(n) tick(); endtask
    task automatic initialize(input bit mock);
        mock_mode=mock; cold_reset=1; ready_enabled=1; visibility_confirmed=1;
        mock_status=0; mock_error=0; mock_empty=1; mock_mem=0; mock_withdrawn=0; mock_isolated=0;
        mock_fault=0; mock_wrong_epoch=0; mock_resp=0; mock_write=0; mock_protocol=0; mock_address_valid=0;
        s_axi_awvalid=0; s_axi_wvalid=0; s_axi_arvalid=0; s_axi_bready=0; s_axi_rready=0;
        backend_req_valid=0; operator_result_valid=0; operator_error_code=0; m_axi_arready=0; m_axi_awready=0; m_axi_wready=0;
        expected_backend_error=0; expected_backend_data=0;
        m_axi_rvalid=0; m_axi_bvalid=0; m_axi_rid=0; m_axi_bid=0; m_axi_rresp=0; m_axi_bresp=0; m_axi_rlast=1;
        tick(); cold_reset=0; reset_cycle=-1;
    endtask
    task automatic write_reg(input logic [31:0] addr, data, input logic [1:0] resp,
        input int skew=0, input logic [3:0] mask=15, input int bstall=0);
        int wait_count;
        s_axi_awaddr=addr; s_axi_wdata=data; s_axi_wstrb=mask;
        if(skew<0) begin
            s_axi_wvalid=1; #1; must(s_axi_wready,"写数据真实准入"); tick(); s_axi_wvalid=0;
            #1; must(!s_axi_wready && s_axi_awready,"W独立单槽"); idle_ticks(-skew);
            s_axi_awvalid=1; #1; must(s_axi_awready,"W先写地址准入"); tick(); s_axi_awvalid=0;
        end else begin
            s_axi_awvalid=1; #1; must(s_axi_awready,"写地址真实准入"); tick(); s_axi_awvalid=0;
            #1; must(!s_axi_awready && s_axi_wready,"AW独立单槽"); idle_ticks(skew);
            s_axi_wvalid=1; #1; must(s_axi_wready,"AW先写数据准入"); tick(); s_axi_wvalid=0;
        end
        wait_count=0;
        while(!s_axi_bvalid && wait_count<100) begin tick(); wait_count++; end
        must(s_axi_bvalid && s_axi_bresp==resp,"写响应或超时");
        must(!s_axi_awready && !s_axi_wready,"B等待期间两写槽保持关闭");
        idle_ticks(bstall); s_axi_bready=1; tick(); s_axi_bready=0;
    endtask
    task automatic read_reg(input logic [31:0] addr, expected, input logic [1:0] resp=0, input int stall=0);
        int wait_count;
        s_axi_araddr=addr; s_axi_arvalid=1;
        #1;
        wait_count=0;
        while(!s_axi_arready && wait_count<100) begin tick(); wait_count++; end
        must(s_axi_arready,"读准入超时"); tick(); s_axi_arvalid=0;
        wait_count=0;
        while(!s_axi_rvalid && wait_count<20) begin tick(); wait_count++; end
        must(s_axi_rvalid && s_axi_rresp==resp && s_axi_rdata==expected,"读值或响应");
        idle_ticks(stall); s_axi_rready=1; tick(); s_axi_rready=0;
    endtask
    task automatic read_state(input int expected);
        s_axi_araddr=32'h43c0000c; s_axi_arvalid=1; tick(); s_axi_arvalid=0;
        must(s_axi_rvalid && s_axi_rdata[2:0]==3'(expected),"物理状态");
        if(expected==5 && reset_cycle>=0) must(cycles-reset_cycle>=3,"S+2之前发布ERROR_SAFE");
        s_axi_rready=1; tick(); s_axi_rready=0;
    endtask
    task automatic configure(input logic [31:0] timeout_value=1000, drain_value=32);
        write_reg(32'h43c00028,timeout_value,0); write_reg(32'h43c0002c,drain_value,0);
    endtask
    task automatic start_run();
        int before_start, before_config, started_cycle;
        before_start=start_count; before_config=config_count;
        write_reg(32'h43c00008,1,0); started_cycle=cycles;
        while(!run_enable && cycles-started_cycle<40) tick();
        must(run_enable && start_count==before_start+1 && config_count==before_config+6,"ARMING六配置及唯一start");
    endtask
    task automatic await_safe();
        // 通过外层公开读采样等待，不窥私有状态。
        int n;
        logic seen;
        n=0; seen=0;
        while(!seen && n<40) begin
            s_axi_araddr=32'h43c0000c; s_axi_arvalid=1; tick(); s_axi_arvalid=0;
            seen=s_axi_rdata[2:0]==5;
            if(seen) must(s_axi_rdata[10] && !s_axi_rdata[8] && !s_axi_rdata[9],"失败安全归还标志");
            if(seen && reset_cycle>=0) must(cycles-reset_cycle>=3,"真实reset后不得早于S+2安全归还");
            s_axi_rready=1; tick(); s_axi_rready=0; n++;
        end
        must(seen,"ERROR_SAFE未到达");
    endtask
    task automatic acknowledge();
        write_reg(32'h43c0005c,run_epoch[31:0],0); write_reg(32'h43c00060,run_epoch[63:32],0);
        write_reg(32'h43c00008,4,0); read_state(0);
    endtask
    task automatic launch_memory(input bit wr, input logic [3:0] mask=15);
        expected_backend_data=wr ? 0 : 32'h76543210;
        backend_req_write=wr; backend_req_addr=wr ? 32'h01000000 : 0;
        backend_req_rstrb=wr ? 4'd0 : mask; backend_req_wstrb=wr ? mask : 4'd0;
        backend_req_valid=1; #1; must(backend_req_ready,"真实runtime准入"); tick(); backend_req_valid=0;
        idle_ticks(3); must(wr ? m_axi_awvalid && m_axi_wvalid : m_axi_arvalid,"真实adapter声明");
    endtask

    initial begin
        // 独立断言：四种相位的START提交沿读取，必须立即取得所有权及ARMING状态。
        for (int p=0;p<4;p++) begin
            initialize(0); configure(); while(phase!=p) tick();
            s_axi_awaddr=32'h43c00008; s_axi_wdata=1; s_axi_wstrb=15;
            s_axi_awvalid=1; s_axi_wvalid=1; tick();
            s_axi_awvalid=0; s_axi_wvalid=0;
            s_axi_araddr=32'h43c0000c; s_axi_arvalid=1; tick(); s_axi_arvalid=0;
            must(s_axi_bvalid && s_axi_bresp==0 && s_axi_rvalid && s_axi_rresp==0 &&
                s_axi_rdata==32'h101 && run_epoch==1,"独立START提交沿快照");
            s_axi_bready=1; tick(); s_axi_bready=0;
            idle_ticks(35); must(run_enable,"独立R背压时ARMING仍有界");
            s_axi_rready=1; tick(); s_axi_rready=0;
            read_reg(32'h43c00050,1); read_reg(32'h43c00054,0);
            directed++;
        end
        // 独立手算：逻辑word0的lane2窄读，错误关联物理地址必须为0x10000002。
        initialize(0); configure(); start_run(); launch_memory(0,4);
        must(m_axi_araddr==32'h10000002 && m_axi_arsize==0,"独立lane2窄读地址");
        m_axi_arready=1; tick(); m_axi_arready=0;
        m_axi_rvalid=1; m_axi_rresp=3; tick(); m_axi_rvalid=0;
        await_safe(); read_reg(32'h43c00010,10); read_reg(32'h43c0006c,0);
        read_reg(32'h43c00070,32'h10000002); read_reg(32'h43c00074,3);
        directed++;
        // 独立连续任务：匹配ACK后epoch递增；高32位不匹配不能解除终态。
        acknowledge(); start_run(); must(run_epoch==2,"独立连续epoch递增");
        operator_result_valid=1; tick(); operator_result_valid=0; idle_ticks(8); read_state(4);
        write_reg(32'h43c0005c,2,0); write_reg(32'h43c00060,1,0);
        write_reg(32'h43c00008,4,2); read_state(4); read_reg(32'h43c00064,4);
        write_reg(32'h43c00060,0,0); write_reg(32'h43c00008,4,0); read_state(0);
        read_reg(32'h43c00050,2); directed++;
        $display("PASS_INDEPENDENT_CONTROL cases=%0d cycles=%0d",directed,cycles);
        $finish;
    end
endmodule
