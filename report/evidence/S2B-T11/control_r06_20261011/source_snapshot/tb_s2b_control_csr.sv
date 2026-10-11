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
        .clk(clk), .hard_reset(cold_reset), .csr_valid(core_csr_valid && !mock_mode),
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
            if (s_axi_awvalid) must(s_axi_awready,"写地址实际准入");
            if (s_axi_wvalid) must(s_axi_wready,"写数据实际准入");
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
        backend_req_valid=0; operator_result_valid=0; m_axi_arready=0; m_axi_awready=0; m_axi_wready=0;
        expected_backend_error=0; expected_backend_data=0;
        m_axi_rvalid=0; m_axi_bvalid=0; m_axi_rid=0; m_axi_bid=0; m_axi_rresp=0; m_axi_bresp=0; m_axi_rlast=1;
        tick(); cold_reset=0; reset_cycle=-1;
    endtask
    task automatic write_reg(input logic [31:0] addr, data, input logic [1:0] resp,
        input int skew=0, input logic [3:0] mask=15, input int bstall=0);
        int wait_count;
        s_axi_awaddr=addr; s_axi_wdata=data; s_axi_wstrb=mask;
        if(skew<0) begin s_axi_wvalid=1; tick(); s_axi_wvalid=0; idle_ticks(-skew); s_axi_awvalid=1; tick(); s_axi_awvalid=0; end
        else begin s_axi_awvalid=1; tick(); s_axi_awvalid=0; idle_ticks(skew); s_axi_wvalid=1; tick(); s_axi_wvalid=0; end
        wait_count=0;
        while(!s_axi_bvalid && wait_count<100) begin tick(); wait_count++; end
        must(s_axi_bvalid && s_axi_bresp==resp,"写响应或超时");
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
        logic [31:0] addr, expected;
        int prior, saved, count;
        initialize(1);
        // 完整普通map与非法方向、完整32位别名、所有byte strobe。
        for(int offset=0;offset<=16'h74;offset+=4) begin
            addr=32'h43c00000+32'(offset); expected=0;
            case(offset)
                0: expected=32'h53324250; 4: expected=32'h100; 12: expected=32'h400;
                28: expected=519168; 32: expected=32'h100000; 36: expected=5903100;
                48: expected=32'h10000000; 52: expected=32'h02000000;
                56: expected=32'h01000000; 60: expected=32'h01adadb8;
                64: expected=32'h01a46100; 68: expected=5070;
                72: expected=32'h01ad5e80; 76: expected=20280;
                default: expected=0;
            endcase
            read_reg(addr,expected,offset==8 ? 2'b11 : 2'b00); directed++;
        end
        foreach_mask: for(int mask=0;mask<15;mask++) begin
            write_reg(32'h43c00014,32'hfeedface,2,0,4'(mask)); read_reg(32'h43c00014,0); directed++;
        end
        for(int offset=0;offset<=16'h74;offset+=4) begin
            if(offset!=8 && !(offset>=20 && offset<=44) && offset!=92 && offset!=96) begin
                write_reg(32'h43c00000+32'(offset),0,3); directed++;
            end
        end
        read_reg(32'h00000000,0,3); read_reg(32'h43c10000,0,3); read_reg(32'h43c00078,0,3);
        read_reg(32'h43c00001,0,3); read_reg(32'h43c00140,0,3);
        write_reg(32'h43c10008,1,3); write_reg(32'h43c00009,1,3);
        write_reg(32'h43c00100,1,3); directed+=8;
        for(int offset=0;offset<=16'h3c;offset+=4) begin
            expected=offset==4 ? 0 : offset==8 ? 0 : 32'ha0000000 | 32'(offset);
            read_reg(32'h43c00100+32'(offset),expected,0,5); directed++;
        end
        for(int encoding=3;encoding<16;encoding++) begin
            if(encoding!=4 && encoding!=8) begin write_reg(32'h43c00008,32'(encoding),2); directed++; end
        end
        write_reg(32'h43c00008,32'h80000000,2); read_reg(32'h43c00064,5);
        write_reg(32'h43c00008,0,0); read_reg(32'h43c00064,5); directed++;
        for(int i=0;i<128;i++) begin
            rng=rng ^ (rng<<13); rng=rng ^ (rng>>17); rng=rng ^ (rng<<5);
            write_reg(32'h43c00014,rng,0,int'(rng%7)-3,15,int'((rng>>8)%4));
            read_reg(32'h43c00014,rng,0,int'((rng>>16)%4)); random_count++;
        end
        // 同沿普通写提交与AR从next-state读取新配置。
        s_axi_awaddr=32'h43c00014; s_axi_wdata=32'h11112222; s_axi_wstrb=15;
        s_axi_awvalid=1; s_axi_wvalid=1; tick(); s_axi_awvalid=0; s_axi_wvalid=0;
        s_axi_araddr=32'h43c00014; s_axi_arvalid=1; tick(); s_axi_arvalid=0;
        must(s_axi_bvalid && s_axi_rdata==32'h11112222,"同沿读新配置");
        s_axi_bready=1; s_axi_rready=1; tick(); s_axi_bready=0; s_axi_rready=0; directed++;
        // 接受错误START仍有epoch/frame；地址、长度、timeout错误优先。
        for(int which=0;which<3;which++) begin
            initialize(1); write_reg(32'h43c00014,32'h1234,0);
            if(which==0) write_reg(32'h43c00018,4,0);
            if(which<=1) write_reg(32'h43c0001c,8,0);
            write_reg(32'h43c00008,1,0); read_state(5);
            read_reg(32'h43c00010,which==0 ? 2 : which==1 ? 3 : 1);
            read_reg(32'h43c00050,1); read_reg(32'h43c00058,32'h1234);
            write_reg(32'h43c00008,1,2); read_reg(32'h43c00064,2);
            write_reg(32'h43c0005c,2,0); write_reg(32'h43c00008,4,2); read_reg(32'h43c00064,4);
            acknowledge(); write_reg(32'h43c00008,4,2); read_reg(32'h43c00064,3); directed++;
        end
        // START真实握手、busy写配置拒绝、done可见性及ACK的真实等待。
        initialize(1); configure(); start_run();
        write_reg(32'h43c00014,88,2); write_reg(32'h43c00008,1,2);
        visibility_confirmed=0; mock_status=2; idle_ticks(8); read_state(2);
        visibility_confirmed=1; idle_ticks(4); read_state(4);
        write_reg(32'h43c0005c,1,0); write_reg(32'h43c00060,0,0);
        while(phase!=3) tick();
        s_axi_awaddr=32'h43c00008; s_axi_wdata=4; s_axi_awvalid=1; s_axi_wvalid=1; tick();
        s_axi_awvalid=0; s_axi_wvalid=0; tick();
        must(!s_axi_bvalid,"ACK等待内核握手不提前B");
        s_axi_araddr=32'h43c0000c; s_axi_arvalid=1; tick(); s_axi_arvalid=0;
        must(s_axi_rdata[2:0]==4,"ACK等待期间旧安全终态"); s_axi_rready=1; tick(); s_axi_rready=0;
        while(!s_axi_bvalid) tick(); s_axi_bready=1; tick(); s_axi_bready=0;
        read_state(0); directed++;
        // 核心首次error先pending，下一ERROR采样；后续AXI只补风险不抢码。
        initialize(1); configure(); start_run(); while(phase!=0) tick();
        mock_status=4; mock_error=5; tick(); must(cancel,"观察error门禁");
        s_axi_araddr=32'h43c00010; s_axi_arvalid=1;
        mock_fault=1; mock_fault_code=9; mock_resp=2; mock_address_valid=1; tick();
        mock_fault=0; s_axi_arvalid=0; must(s_axi_rdata==5,"CORE pending后响应错不覆盖");
        s_axi_rready=1; tick(); s_axi_rready=0; await_safe(); read_reg(32'h43c00010,5); directed++;
        for(int code=0;code<9;code++) begin
            initialize(1); configure(); start_run(); mock_status=4; mock_error=32'(code);
            await_safe(); read_reg(32'h43c00010,code>=1 && code<=7 ? 32'(code) : 6); directed++;
        end
        // 在E沿之后产生sticky，覆盖四种E相位；观察沿先发布pending/code0。
        for(int injection_phase=0;injection_phase<4;injection_phase++) begin
            initialize(1); configure(); start_run(); while(phase!=injection_phase) tick();
            tick(); saved=cycles; prior=reset_count; mock_status=4; mock_error=7;
            while(phase!=0 && phase!=3) tick();
            s_axi_araddr=32'h43c00010; s_axi_arvalid=1; tick(); s_axi_arvalid=0;
            must(s_axi_rvalid && s_axi_rdata==0 && reset_count==prior,"首次STATUS观察仅pending不提前reset或code");
            must(cycles-saved <= (injection_phase==0 ? 3 : injection_phase==1 ? 2 : 1),"STATUS观察三周期上界");
            s_axi_rready=1; tick(); s_axi_rready=0;
            await_safe(); read_reg(32'h43c00010,7); phase_coverage[injection_phase]++; directed++;
        end
        // 同沿ABORT、成功/CORE与AXI响应/协议固定优先。
        for(int kind=0;kind<4;kind++) begin
            initialize(1); configure(); start_run(); while(phase!=3) tick();
            s_axi_awaddr=32'h43c00008; s_axi_wdata=2; s_axi_awvalid=1; s_axi_wvalid=1; tick();
            s_axi_awvalid=0; s_axi_wvalid=0; mock_status=kind==0 ? 2 : 4; mock_error=5;
            if(kind>=2) begin mock_fault=1; mock_fault_code=kind==2 ? 10 : 11; mock_resp=3; mock_protocol=kind==3; mock_write=1; mock_address_valid=1; end
            tick(); mock_fault=0; mock_status=0; must(s_axi_bvalid,"ABORT接受B");
            s_axi_bready=1; tick(); s_axi_bready=0;
            if(kind==3) begin idle_ticks(20); read_state(6); write_reg(32'h43c00008,4,2); end
            else await_safe();
            read_reg(32'h43c00010,kind<2 ? 8 : kind==2 ? 10 : 11); directed++;
        end
        // 低ready不能假STOP；ARMING超限，恢复诊断后恢复；ARMING取消不发start。
        initialize(1); configure(); ready_enabled=0; prior=start_count;
        write_reg(32'h43c00008,1,0); idle_ticks(45); read_state(3); must(start_count==prior,"异常ready不发start");
        read_reg(32'h43c00010,6); ready_enabled=1; await_safe(); directed++;
        initialize(1); configure(); prior=start_count; write_reg(32'h43c00008,1,0);
        write_reg(32'h43c00008,2,0); await_safe(); must(start_count==prior,"ARMING ABORT取消CSR序列"); directed++;
        // 请求撤销门禁等待真实归因，无法归因时INTERNAL；可见性低保持所有权。
        for(int explained=0;explained<2;explained++) begin
            initialize(1); configure(); start_run(); mock_withdrawn=1; tick(); mock_withdrawn=0;
            must(cancel,"公开mem撤销后持续门禁");
            if(explained!=0) begin mock_status=4; mock_error=5; end
            visibility_confirmed=0; idle_ticks(20); read_state(3);
            visibility_confirmed=1; await_safe(); read_reg(32'h43c00010,explained!=0 ? 5 : 6); directed++;
        end
        // idle收到未请求响应必须永久协议隔离；cold才能恢复。
        initialize(0); m_axi_rvalid=1; m_axi_rresp=1; tick(); m_axi_rvalid=0;
        idle_ticks(20); read_state(6); read_reg(32'h43c00010,11); read_reg(32'h43c00074,17);
        write_reg(32'h43c00008,1,2); write_reg(32'h43c00008,4,2); directed++;
        // 白盒仅用于不可实际等待2^64次的耗尽corner，不改变硬件初始化ABI。
        initialize(1); configure(); force dut.q.epoch=64'hffffffffffffffff;
        write_reg(32'h43c00008,1,2); read_reg(32'h43c00064,6); read_state(0);
        release dut.q.epoch; initialize(1); read_reg(32'h43c00050,0); directed++;
        // 集成四种AW/W独立停顿：ABORT后VALID不撤回，缺失通道最终合法闭合。
        for(int accepts=0;accepts<4;accepts++) begin
            initialize(0); configure(1000,8); start_run(); launch_memory(1);
            m_axi_awready=accepts[0]; m_axi_wready=accepts[1]; tick();
            m_axi_awready=0; m_axi_wready=0;
            write_reg(32'h43c00008,2,0); idle_ticks(20); read_state(6);
            must(m_axi_awvalid==!accepts[0] && m_axi_wvalid==!accepts[1],"取消仍保留AW/W声明");
            m_axi_awready=1; m_axi_wready=1; tick(); m_axi_awready=0; m_axi_wready=0;
            m_axi_bvalid=1; tick(); m_axi_bvalid=0; await_safe();
            read_reg(32'h43c00010,8); read_reg(32'h43c00074,8); acknowledge(); integration_count++;
        end
        // AXI3合法早B先于AW，timeout撤销读、错误B先到均不能丢AW。
        for(int err=0;err<2;err++) begin
            initialize(0); configure(1000,8); start_run(); launch_memory(1);
            m_axi_wready=1; tick(); m_axi_wready=0;
            m_axi_bvalid=1; m_axi_bresp=err!=0 ? 2 : 0; tick(); m_axi_bvalid=0;
            must(adapter_progress[9] && !adapter_progress[7] && m_axi_awvalid,"早B后继续保留AW");
            if(err==0) write_reg(32'h43c00008,2,0);
            idle_ticks(20); read_state(6); m_axi_awready=1; tick(); m_axi_awready=0; await_safe();
            read_reg(32'h43c00010,err!=0 ? 9 : 8); read_reg(32'h43c00074,err!=0 ? 14 : 8); integration_count++;
        end
        initialize(0); configure(40,8); start_run(); launch_memory(0,1);
        m_axi_arready=1; tick(); m_axi_arready=0; idle_ticks(55); read_state(6);
        must(!m_axi_arvalid && cancel,"timeout撤销后不发剩余子读");
        m_axi_rdata=64'h76543210; m_axi_rvalid=1; tick(); m_axi_rvalid=0; await_safe();
        read_reg(32'h43c00010,5); read_reg(32'h43c00074,8); integration_count++;
        // 正常真实runtime完成；公共STATUS读取到done后才发布HEAD。
        initialize(0); configure(); start_run(); operator_result_valid=1; tick(); operator_result_valid=0;
        idle_ticks(8); read_state(4); acknowledge(); integration_count++;
        // 实际最后start槽与非法响应同沿：内核握手后外层直接隔离，永不声明AXI。
        initialize(0); configure(); prior=start_count; saved=reset_count;
        write_reg(32'h43c00008,1,0);
        while(!(core_csr_valid && core_csr_write && core_csr_addr==0 && core_csr_wdata==1)) tick();
        m_axi_rvalid=1; m_axi_rresp=1; tick(); m_axi_rvalid=0;
        must(start_count==prior+1 && !run_enable && cancel,"start与HP故障同沿不得进入有效RUN");
        repeat(16) begin tick(); must(!m_axi_arvalid && !m_axi_awvalid && !m_axi_wvalid,"故障start不能声明物理请求"); end
        must(reset_count==saved+1,"故障start仍真实soft_reset"); read_state(6); read_reg(32'h43c00010,11); integration_count++;
        // guard错误实际先交给runtime，随后观察其公共error并保存原码。
        initialize(0); configure(); start_run(); prior=logical_responses;
        backend_req_write=1; backend_req_addr=32'h00100000; backend_req_rstrb=0; backend_req_wstrb=15;
        expected_backend_error=2; expected_backend_data=0;
        backend_req_valid=1; tick(); backend_req_valid=0; await_safe();
        must(logical_responses==prior+1 && !m_axi_arvalid && !m_axi_awvalid && !m_axi_wvalid,"guard拒绝必须真实交付且无AXI");
        read_reg(32'h43c00010,2); integration_count++;
        // 逻辑地址0有真实关联；HP响应错误与GP0读同沿从next-state读到首错。
        initialize(0); configure(); start_run(); launch_memory(0); m_axi_arready=1; tick(); m_axi_arready=0;
        m_axi_rvalid=1; m_axi_rresp=2; s_axi_araddr=32'h43c00010; s_axi_arvalid=1;
        tick(); m_axi_rvalid=0; s_axi_arvalid=0;
        must(s_axi_rdata==9 && !mem_ready,"HP错误同沿快照及禁止交付");
        s_axi_rready=1; tick(); s_axi_rready=0; await_safe();
        read_reg(32'h43c0006c,0); read_reg(32'h43c00070,32'h10000000); read_reg(32'h43c00074,2); integration_count++;
        // 正常OKAY响应已到达，ABORT提交沿仍不能把待交付响应送回core。
        initialize(0); configure(); start_run(); launch_memory(0); m_axi_arready=1; tick(); m_axi_arready=0;
        prior=logical_responses; s_axi_awaddr=32'h43c00008; s_axi_wdata=2; s_axi_wstrb=15;
        s_axi_awvalid=1; s_axi_wvalid=1; m_axi_rvalid=1; m_axi_rdata=64'h76543210;
        tick(); s_axi_awvalid=0; s_axi_wvalid=0; m_axi_rvalid=0;
        tick(); must(s_axi_bvalid && logical_responses==prior,"ABORT commit沿取消已到OKAY逻辑响应");
        s_axi_bready=1; tick(); s_axi_bready=0; await_safe(); read_reg(32'h43c00010,8); integration_count++;
        // 本沿HP接受/响应与AR同沿，公开progress采样实际next账本。
        initialize(0); configure(); start_run(); launch_memory(1);
        m_axi_awready=1; s_axi_araddr=32'h43c00068; s_axi_arvalid=1;
        tick(); m_axi_awready=0; s_axi_arvalid=0; must(s_axi_rdata==32'hb8,"本沿AW接受progress");
        s_axi_rready=1; tick(); s_axi_rready=0;
        m_axi_wready=1; s_axi_arvalid=1; tick(); m_axi_wready=0; s_axi_arvalid=0;
        must(s_axi_rdata==32'hf8,"本沿W接受progress"); s_axi_rready=1; tick(); s_axi_rready=0;
        m_axi_bvalid=1; s_axi_arvalid=1; tick(); m_axi_bvalid=0; s_axi_arvalid=0;
        must(s_axi_rdata==32'h100,"本沿合法B结束只剩逻辑response");
        s_axi_rready=1; tick(); s_axi_rready=0;
        read_reg(32'h43c00068,0); operator_result_valid=1; tick(); operator_result_valid=0;
        idle_ticks(8); read_state(4); acknowledge(); integration_count++;
        // ACK pending发生晚到协议错误，B必须结束且恢复槽不能被ACK占死。
        initialize(0); configure(); start_run(); operator_result_valid=1; tick(); operator_result_valid=0;
        idle_ticks(8); write_reg(32'h43c0005c,1,0); write_reg(32'h43c00060,0,0);
        while(phase!=3) tick(); s_axi_awaddr=32'h43c00008; s_axi_wdata=4; s_axi_awvalid=1; s_axi_wvalid=1;
        tick(); s_axi_awvalid=0; s_axi_wvalid=0; tick(); must(!s_axi_bvalid,"实际ACK等待");
        saved=reset_count; m_axi_bvalid=1; tick(); m_axi_bvalid=0;
        must(s_axi_bvalid && s_axi_bresp==2,"晚到协议故障取消未commit ACK并完成B");
        s_axi_bready=1; tick(); s_axi_bready=0; idle_ticks(16);
        must(reset_count==saved+1,"取消ACK后恢复softreset不饿死"); read_state(6); read_reg(32'h43c00010,11); integration_count++;
        // debug预留不被同沿START抢占，phase2最多四周期且Rstall不占监视。
        initialize(1); configure(); while(phase!=3) tick();
        s_axi_araddr=32'h43c00110; s_axi_arvalid=1; s_axi_awaddr=32'h43c00008;
        s_axi_wdata=1; s_axi_awvalid=1; s_axi_wvalid=1; saved=cycles; prior=debug_count;
        tick(); s_axi_arvalid=0; s_axi_awvalid=0; s_axi_wvalid=0;
        while(!s_axi_rvalid && cycles-saved<5) tick();
        must(s_axi_rvalid && debug_count==prior+1,"debug预约四周期公平");
        count=status_count; idle_ticks(12); must(status_count>=count+6,"debug R背压不阻塞监视");
        s_axi_rready=1; s_axi_bready=1; tick(); s_axi_rready=0; s_axi_bready=0;
        while(!run_enable) tick(); directed++;
        must(error_count>0 && ack_count>0 && reset_count>0,"控制及监视路径覆盖");
        for(int p=0;p<4;p++) must(phase_coverage[p]==1,"四相位错误覆盖");
        $display("PASS CONTROL_CSR directed=%0d random=%0d integration=%0d cycles=%0d status=%0d error=%0d debug=%0d starts=%0d resets=%0d acks=%0d",directed,random_count,integration_count,cycles,status_count,error_count,debug_count,start_count,reset_count,ack_count);
        $display("COVERAGE phases=%0d,%0d,%0d,%0d logical_responses=%0d seed=0x2b111010",phase_coverage[0],phase_coverage[1],phase_coverage[2],phase_coverage[3],logical_responses);
        $finish;
    end
endmodule
