    task automatic independent_cases();
        int deliveries, saved_ar;
        // 手算常量总线：低word=44332211，高word=88776655，不用生产参考函数。
        for (int high_word=0; high_word<2; high_word++) begin
            initialize(); start_request(0,32'h01000000+32'(4*high_word),15); declare_request(); accept_ar();
            m_axi_rdata=64'h8877665544332211; m_axi_rvalid=1; step(); m_axi_rvalid=0; #1;
            finish_logical(high_word!=0 ? 32'h88776655 : 32'h44332211,0);
        end
        // 稀疏高word只读取两个物理byte；其余lane必须为零。
        initialize(); start_request(0,32'h01000004,5); declare_request();
        must(m_axi_araddr==32'h11000004 && m_axi_arsize==0,"独立首byte地址"); accept_ar();
        m_axi_rdata=64'h8877665544332211; m_axi_rvalid=1; step(); m_axi_rvalid=0; step();
        must(m_axi_araddr==32'h11000006 && m_axi_arsize==0 && !mem_ready,"独立第二byte地址"); accept_ar();
        m_axi_rdata=64'h8877665544332211; m_axi_rvalid=1; step(); m_axi_rvalid=0; #1;
        finish_logical(32'h00770055,0);
        // 写高word和早到错误B与AW同沿；真实已声明AW/W仍必须入账。
        initialize(); start_request(1,32'h01000004,10); declare_request();
        must(m_axi_wstrb==8'ha0 && m_axi_wdata==64'hd4c3b2a100000000,"独立高word写手算");
        m_axi_wready=1; step(); m_axi_wready=0;
        m_axi_awready=1; m_axi_bvalid=1; m_axi_bresp=3; cancel=1; #1;
        must(fault_event_valid && fault_event_code==10 && !mem_ready,"取消同沿DECERR分类");
        step(); m_axi_awready=0; m_axi_bvalid=0; m_axi_bresp=0; cancel=0; mem_valid=0;
        must(ledger_empty && recovery_required && !protocol_isolated && first_fault_code==10,"同沿AW错误B未闭账");
        clear_diagnostic(1);
        // 合法SLVERR与无写事务的B同沿，协议11必须优先，合法R仍可闭账。
        initialize(); start_request(0,32'h01000000,15); declare_request(); accept_ar();
        m_axi_rvalid=1; m_axi_rresp=2; m_axi_bvalid=1; m_axi_bresp=3; #1;
        must(fault_event_code==11 && !mem_ready,"协议错未优先普通读错"); step();
        m_axi_rvalid=0; m_axi_bvalid=0; m_axi_rresp=0; m_axi_bresp=0; mem_valid=0;
        must(ledger_empty && first_fault_code==11 && protocol_isolated,"优先错隔离或合法R入账错误");
        clear_diagnostic(0);
        // 逻辑payload变化与合法SLVERR同沿，INTERNAL6保存且R物理消费。
        initialize(); start_request(0,32'h01000000,15); declare_request(); accept_ar();
        mem_wdata^=1; m_axi_rvalid=1; m_axi_rresp=2; #1;
        must(fault_event_code==6 && !mem_ready,"逻辑异常分类"); step(); m_axi_rvalid=0; m_axi_rresp=0; mem_valid=0;
        must(ledger_empty && first_fault_code==6 && protocol_isolated,"逻辑异常下合法R没有入账");
        clear_diagnostic(0);
        // 未接受AR的早R与AR接受同沿不凭早R闭账，后续合法R闭账仍保持隔离。
        initialize(); start_request(0,32'h01000000,15); declare_request();
        m_axi_arready=1; m_axi_rvalid=1; #1; must(fault_event_code==11,"同沿AR早R分类"); step();
        m_axi_arready=0; m_axi_rvalid=0; mem_valid=0;
        must(!ledger_empty && !m_axi_arvalid && protocol_isolated,"早R错误丢失AR账本");
        return_r(0,0,1); must(ledger_empty && protocol_isolated && !mem_ready,"合法晚R消除隔离");
        clear_diagnostic(0);
        // 未完成W的B与W接受同沿不闭账；之后合法B在AW stall期间保存。
        initialize(); start_request(1,32'h01000000,15); declare_request();
        m_axi_wready=1; m_axi_bvalid=1; #1; must(fault_event_code==11,"同沿W早B分类"); step();
        m_axi_wready=0; m_axi_bvalid=0; mem_valid=0;
        must(!ledger_empty && m_axi_awvalid && protocol_isolated,"早B丢失写账本");
        return_b(0,0); must(!ledger_empty && m_axi_awvalid,"合法晚B忘记AW");
        m_axi_awready=1; step(); m_axi_awready=0;
        must(ledger_empty && protocol_isolated && !mem_ready,"AW闭账消除隔离"); clear_diagnostic(0);
        // 准入错误槽与无请求AXI响应竞争，协议11抑制1/2交付。
        for (int error_kind=0; error_kind<2; error_kind++) begin
            initialize(); mem_valid=1; mem_write=1; mem_rstrb=0;
            mem_addr=error_kind==0 ? 32'h01000000 : 32'h00100000; mem_wstrb=error_kind==0 ? 0 : 15;
            step(); deliveries=logical_count; must(mem_ready,"独立guard槽未生成");
            m_axi_bvalid=1; #1; must(fault_event_code==11 && !mem_ready,"guard错误槽没有同沿封门"); step();
            m_axi_bvalid=0; mem_valid=0;
            must(logical_count==deliveries && ledger_empty && protocol_isolated && first_fault_code==11,"guard槽竞争错误交付");
            clear_diagnostic(0);
        end
        // byte之间收到无请求B并关闭RUN，不启动新的子读且不交付旧数据。
        initialize(); start_request(0,32'h01000000,3); declare_request(); accept_ar(); return_r(0,0,1);
        saved_ar=ar_count; m_axi_bvalid=1; run_enable=0; step(); m_axi_bvalid=0; mem_valid=0;
        must(ledger_empty && ar_count==saved_ar && !m_axi_arvalid && protocol_isolated && !mem_ready,"byte间协议异常发起新声明");
        clear_diagnostic(0);
        $display("PASS INDEPENDENT_HP0_CASES cases=11 hand_words=3 crossing_histories=8");
    endtask
