`timescale 1ns/1ps
// 物理接口候选0.1.1：仅由公共CSR读握手观察计算状态，冷初始化才清epoch。
module s2b_control_csr (
    input logic clk, cold_reset,
    input logic [31:0] s_axi_awaddr,
    input logic s_axi_awvalid,
    output logic s_axi_awready,
    input logic [31:0] s_axi_wdata,
    input logic [3:0] s_axi_wstrb,
    input logic s_axi_wvalid,
    output logic s_axi_wready,
    output logic [1:0] s_axi_bresp,
    output logic s_axi_bvalid,
    input logic s_axi_bready,
    input logic [31:0] s_axi_araddr,
    input logic s_axi_arvalid,
    output logic s_axi_arready,
    output logic [31:0] s_axi_rdata,
    output logic [1:0] s_axi_rresp,
    output logic s_axi_rvalid,
    input logic s_axi_rready,
    output logic core_csr_valid, core_csr_write,
    output logic [7:0] core_csr_addr,
    output logic [31:0] core_csr_wdata,
    input logic core_csr_ready,
    input logic [31:0] core_csr_rdata,
    input logic core_mem_valid,
    input logic ledger_empty,
    input logic [63:0] ledger_epoch,
    input logic [9:0] axi_progress_next,
    input logic ledger_empty_next,
    input logic req_withdrawn, protocol_isolated,
    input logic fault_event_valid,
    input logic [7:0] fault_event_code,
    input logic [31:0] fault_event_address, fault_event_physical_address,
    input logic [1:0] fault_event_resp,
    input logic fault_event_write, fault_event_protocol, fault_event_address_valid,
    // 完整集成必须显式证明可见性；未绑定或低电平绝不发布物理安全终态。
    input logic visibility_confirmed,
    output logic run_enable, cancel, clear_safe,
    output logic [63:0] run_epoch
);
    localparam logic [2:0] IDLE_PS=0, ARMING=1, RUN=2, RECOVERING=3,
        DONE_SAFE=4, ERROR_SAFE=5, FAULT_ISOLATED=6;
    localparam logic [1:0] OKAY=0, SLVERR=2, DECERR=3;
    typedef struct packed {
        logic [2:0] state;
        logic [1:0] phase;
        logic [63:0] epoch, ack_epoch;
        logic [31:0] frame, active_frame, input_addr, input_bytes,
            weight_addr, weight_bytes, core_timeout, drain_timeout;
        logic [31:0] error_code, last_reject, fault_logical, fault_physical;
        logic [4:0] fault_detail;
        logic first_selected, first_pending, isolated, owner, head;
        logic [3:0] status_shadow;
        logic arming_idle;
        logic [2:0] config_step;
        logic [5:0] arming_cycles;
        logic diagnostic_status, diagnostic_error, reset_sent, stop_confirmed;
        logic [1:0] reset_age;
        logic [31:0] drain_cycles;
        logic withdrawn_seen;
        logic [2:0] withdrawn_cycles;
        logic aw_held, w_held, bvalid, ack_pending;
        logic [31:0] awaddr, wdata;
        logic [3:0] wstrb;
        logic [1:0] bresp;
        logic rvalid, debug_pending;
        logic [7:0] debug_addr;
        logic [31:0] rdata;
        logic [1:0] rresp;
    } state_t;
    state_t q, d;
    logic write_commit, address_write_ok, abort_commit;
    logic status_sample, error_sample, observed_error;
    logic control_pending, debug_address, read_address_ok;
    logic ack_commit, start_transfer, reset_transfer;
    logic epoch_ledger_ok;
    logic [31:0] read_value, status_value;
    logic [31:0] selected_code;
    logic select_fault, select_core, start_accepted;

    function automatic logic in_window(input logic [31:0] address);
        return (address >= 32'h43c00000) && (address < 32'h43c10000) && (address[1:0] == 0);
    endfunction
    function automatic logic writable(input logic [31:0] address);
        return in_window(address) && ((address[15:0] == 16'h008) ||
            ((address[15:0] >= 16'h014) && (address[15:0] <= 16'h02c)) ||
            (address[15:0] == 16'h05c) || (address[15:0] == 16'h060));
    endfunction
    function automatic logic readable(input logic [31:0] address);
        return in_window(address) &&
            (((address[15:0] <= 16'h074) && (address[15:0] != 16'h008)) ||
             ((address[15:0] >= 16'h100) && (address[15:0] <= 16'h13c)));
    endfunction
    function automatic logic safe_terminal(input logic [2:0] state);
        return (state == DONE_SAFE) || (state == ERROR_SAFE);
    endfunction
    function automatic logic [31:0] rejection(input logic [2:0] state);
        if (safe_terminal(state)) return 32'd2;
        else if ((state == IDLE_PS) || (state == FAULT_ISOLATED)) return 32'd3;
        else return 32'd1;
    endfunction

    assign s_axi_awready = !cold_reset && !q.aw_held && !q.bvalid && !q.ack_pending;
    assign s_axi_wready = !cold_reset && !q.w_held && !q.bvalid && !q.ack_pending;
    assign s_axi_bvalid = q.bvalid;
    assign s_axi_bresp = q.bresp;
    assign s_axi_rvalid = q.rvalid;
    assign s_axi_rdata = q.rdata;
    assign s_axi_rresp = q.rresp;
    assign debug_address = in_window(s_axi_araddr) &&
        (s_axi_araddr[15:0] >= 16'h100) && (s_axi_araddr[15:0] <= 16'h13c);
    assign read_address_ok = readable(s_axi_araddr);
    assign control_pending = (q.state == ARMING) ||
        ((q.state == RECOVERING || q.state == FAULT_ISOLATED) && !q.reset_sent) ||
        q.ack_pending;
    assign s_axi_arready = !cold_reset && !q.rvalid && !q.debug_pending &&
        (!debug_address || !control_pending);
    assign write_commit = q.aw_held && q.w_held && !q.bvalid && !q.ack_pending;
    assign address_write_ok = writable(q.awaddr);
    assign abort_commit = write_commit && address_write_ok && (q.wstrb == 4'hf) &&
        (q.awaddr[15:0] == 16'h008) && (q.wdata == 2) &&
        ((q.state == ARMING) || (q.state == RUN));
    assign status_sample = core_csr_valid && core_csr_ready && !core_csr_write &&
        ((q.phase == 0) || (q.phase == 3));
    assign error_sample = core_csr_valid && core_csr_ready && !core_csr_write && (q.phase == 1);
    assign observed_error = status_sample && core_csr_rdata[2] &&
        ((q.state == ARMING) || (q.state == RUN));
    // 此组合门禁不依赖恢复状态的next-state，避免与adapter的账本闭合形成环。
    assign cancel = (q.state == RECOVERING) || (q.state == FAULT_ISOLATED) ||
        q.first_pending || ((q.state == RUN) && q.withdrawn_seen) || abort_commit || observed_error ||
        fault_event_valid || protocol_isolated;
    assign run_enable = (q.state == RUN) && !cancel;
    assign run_epoch = q.epoch;
    assign epoch_ledger_ok = ledger_empty || (ledger_epoch == q.epoch);

    // 四相位每周期前进。已接受debug预留phase2，后来的控制不能抢占。
    always_comb begin
        core_csr_valid = !cold_reset;
        core_csr_write = 0;
        core_csr_addr = 8'h04;
        core_csr_wdata = 0;
        case (q.phase)
            0, 3: core_csr_addr = 8'h04;
            1: core_csr_addr = 8'h08;
            2: begin
                core_csr_valid = !cold_reset && q.debug_pending;
                core_csr_addr = q.debug_addr;
                if (!q.debug_pending) begin
                    if (q.ack_pending && safe_terminal(q.state)) begin
                        core_csr_valid = !cold_reset;
                        core_csr_write = 1;
                        core_csr_addr = 8'h3c;
                        core_csr_wdata = (q.state == DONE_SAFE) ? 1 : 2;
                    end else if ((q.state == RECOVERING || q.state == FAULT_ISOLATED) &&
                        q.diagnostic_status && q.diagnostic_error && !q.reset_sent) begin
                        core_csr_valid = !cold_reset;
                        core_csr_write = 1;
                        core_csr_addr = 0;
                        core_csr_wdata = 2;
                    end else if ((q.state == ARMING) && q.arming_idle &&
                        !abort_commit) begin
                        core_csr_valid = !cold_reset;
                        core_csr_write = 1;
                        case (q.config_step)
                            0: begin core_csr_addr=8'h0c; core_csr_wdata=q.active_frame; end
                            1: begin core_csr_addr=8'h10; core_csr_wdata=q.input_addr; end
                            2: begin core_csr_addr=8'h14; core_csr_wdata=q.input_bytes; end
                            3: begin core_csr_addr=8'h18; core_csr_wdata=q.weight_addr; end
                            4: begin core_csr_addr=8'h1c; core_csr_wdata=q.weight_bytes; end
                            5: begin core_csr_addr=8'h28; core_csr_wdata=q.core_timeout; end
                            6: begin core_csr_addr=0; core_csr_wdata=1; end
                            default: core_csr_valid=0;
                        endcase
                    end
                end
            end
            default: core_csr_valid = 0;
        endcase
    end
    assign start_transfer = core_csr_valid && core_csr_ready && core_csr_write &&
        (core_csr_addr == 0) && (core_csr_wdata == 1);
    assign reset_transfer = core_csr_valid && core_csr_ready && core_csr_write &&
        (core_csr_addr == 0) && (core_csr_wdata == 2);
    assign ack_commit = q.ack_pending && core_csr_valid && core_csr_ready &&
        core_csr_write && (core_csr_addr == 8'h3c) && !fault_event_valid && !protocol_isolated;
    // 已清内核终态的ACK在外层写提交沿执行；否则必须等待真实内核ACK握手。
    assign clear_safe = !cold_reset && (ack_commit ||
        (write_commit && address_write_ok && q.wstrb == 4'hf && q.awaddr[15:0] == 16'h008 &&
         q.wdata == 4 && safe_terminal(q.state) && q.ack_epoch == q.epoch &&
         (q.status_shadow[2:1] == 0) && ledger_empty && !q.isolated && !protocol_isolated &&
         !fault_event_valid && visibility_confirmed));

    always_comb begin
        d = q;
        d.phase = q.phase + 2'd1;
        select_fault = 0;
        select_core = 0;
        selected_code = 0;
        start_accepted = 0;
        read_value = 0;
        status_value = 0;
        if (q.bvalid && s_axi_bready) d.bvalid = 0;
        if (q.rvalid && s_axi_rready) d.rvalid = 0;
        if (s_axi_awvalid && s_axi_awready) begin d.aw_held=1; d.awaddr=s_axi_awaddr; end
        if (s_axi_wvalid && s_axi_wready) begin d.w_held=1; d.wdata=s_axi_wdata; d.wstrb=s_axi_wstrb; end
        if (status_sample) begin
            d.status_shadow = core_csr_rdata[3:0];
            if (q.state == ARMING && core_csr_rdata[3:0] == 0) d.arming_idle = 1;
            if (q.state == RECOVERING || q.state == FAULT_ISOLATED) d.diagnostic_status = 1;
        end
        if (error_sample) begin
            if ((q.state == RECOVERING || q.state == FAULT_ISOLATED) && q.diagnostic_status)
                d.diagnostic_error = 1;
            if (q.first_pending && q.diagnostic_status) begin
                d.error_code = (core_csr_rdata >= 1 && core_csr_rdata <= 7) ? core_csr_rdata : 6;
                d.first_pending = 0;
            end
        end
        if (q.debug_pending && q.phase == 2 && core_csr_valid && core_csr_ready) begin
            d.debug_pending=0; d.rvalid=1; d.rresp=OKAY; d.rdata=core_csr_rdata;
        end
        if (q.state == ARMING) begin
            if (q.arming_cycles < 40) d.arming_cycles=q.arming_cycles+6'd1;
            if (q.phase == 2 && core_csr_valid && core_csr_ready && core_csr_write) begin
                if (start_transfer) d.state=RUN;
                else d.config_step=q.config_step+3'd1;
            end
        end
        if (q.reset_sent && q.reset_age < 3) d.reset_age=q.reset_age+2'd1;
        if (reset_transfer) begin d.reset_sent=1; d.reset_age=0; end
        if (q.reset_sent && d.reset_age >= 2 && status_sample &&
            core_csr_rdata[3:0] == 0 && !core_mem_valid) d.stop_confirmed=1;
        if (q.state == RUN && req_withdrawn) d.withdrawn_seen=1;
        if (q.withdrawn_seen && q.withdrawn_cycles < 7) d.withdrawn_cycles=q.withdrawn_cycles+3'd1;

        // 写副作用只发生一次；锁存的AW/W在生成B或ACK提交前不重复执行。
        if (write_commit) begin
            d.aw_held=0; d.w_held=0; d.bvalid=1; d.bresp=OKAY;
            if (!address_write_ok) d.bresp=DECERR;
            else if (q.wstrb != 4'hf) d.bresp=SLVERR;
            else if (q.awaddr[15:0] == 16'h008) begin
                if (q.wdata != 0 && q.wdata != 1 && q.wdata != 2 && q.wdata != 4) begin
                    d.bresp=SLVERR; d.last_reject=5;
                end else if (q.wdata == 1) begin
                    if (q.state != IDLE_PS || fault_event_valid || protocol_isolated || q.isolated) begin
                        d.bresp=SLVERR; d.last_reject=rejection(q.state);
                    end else if (&q.epoch) begin
                        d.bresp=SLVERR; d.last_reject=6;
                    end else begin
                        start_accepted=1;
                        d.epoch=q.epoch+64'd1; d.active_frame=q.frame; d.last_reject=0;
                        d.error_code=0; d.first_selected=0; d.first_pending=0;
                        d.fault_logical=0; d.fault_physical=0; d.fault_detail=0;
                        d.head=0; d.arming_idle=0; d.config_step=0; d.arming_cycles=0;
                        d.diagnostic_status=0; d.diagnostic_error=0; d.reset_sent=0;
                        d.reset_age=0; d.stop_confirmed=0; d.drain_cycles=0;
                        d.withdrawn_seen=0; d.withdrawn_cycles=0;
                        if (q.input_addr != 0 || q.weight_addr != 32'h00100000) d.error_code=2;
                        else if (q.input_bytes != 519168 || q.weight_bytes != 5903100) d.error_code=3;
                        else if (q.core_timeout == 0 || q.drain_timeout == 0) d.error_code=1;
                        if (d.error_code != 0) begin
                            d.state=ERROR_SAFE; d.owner=0; d.first_selected=1; d.stop_confirmed=1;
                        end else begin d.state=ARMING; d.owner=1; end
                    end
                end else if (q.wdata == 2) begin
                    if (!abort_commit) begin d.bresp=SLVERR; d.last_reject=rejection(q.state); end
                    else d.last_reject=0;
                end else if (q.wdata == 4) begin
                    if (!safe_terminal(q.state) || !ledger_empty || q.isolated || protocol_isolated ||
                        fault_event_valid || !visibility_confirmed) begin
                        d.bresp=SLVERR; d.last_reject=3;
                    end else if (q.ack_epoch != q.epoch) begin d.bresp=SLVERR; d.last_reject=4; end
                    else begin
                        d.last_reject=0;
                        if (q.status_shadow[2:1] != 0) begin d.ack_pending=1; d.bvalid=0; end
                    end
                end
            end else if (q.awaddr[15:0] == 16'h05c || q.awaddr[15:0] == 16'h060) begin
                if (!safe_terminal(q.state) || q.isolated) begin d.bresp=SLVERR; d.last_reject=3; end
                else if (q.awaddr[15:0] == 16'h05c) d.ack_epoch[31:0]=q.wdata;
                else d.ack_epoch[63:32]=q.wdata;
            end else if (q.state != IDLE_PS || q.isolated) begin
                d.bresp=SLVERR; d.last_reject=rejection(q.state);
            end else begin
                case (q.awaddr[15:0])
                    16'h014: d.frame=q.wdata;
                    16'h018: d.input_addr=q.wdata;
                    16'h01c: d.input_bytes=q.wdata;
                    16'h020: d.weight_addr=q.wdata;
                    16'h024: d.weight_bytes=q.wdata;
                    16'h028: d.core_timeout=q.wdata;
                    16'h02c: d.drain_timeout=q.wdata;
                    default: begin end
                endcase
            end
        end
        if (clear_safe) begin
            d.state=IDLE_PS; d.head=0; d.first_selected=0; d.first_pending=0;
            d.error_code=0; d.fault_logical=0; d.fault_physical=0; d.fault_detail=0;
            d.withdrawn_seen=0; d.withdrawn_cycles=0; d.ack_pending=0;
            if (ack_commit) begin d.bvalid=1; d.bresp=OKAY; end
        end

        // 首错在同沿先协议、响应、ABORT、真实内核error；后续事件只能补隔离标志。
        if (fault_event_valid || protocol_isolated || !epoch_ledger_ok) begin
            select_fault=1;
            selected_code=fault_event_valid ? {24'd0,fault_event_code} : 11;
        end else if (abort_commit) begin select_fault=1; selected_code=8; end
        else if (observed_error) begin select_fault=1; select_core=1; end
        else if ((q.state == ARMING && q.arming_cycles >= 39 && !start_transfer) ||
                 (q.state == RUN && q.withdrawn_seen && q.withdrawn_cycles >= 5)) begin
            select_fault=1; selected_code=6;
        end
        if (select_fault && (!q.first_selected || start_accepted)) begin
            d.first_selected=1; d.first_pending=select_core; d.error_code=selected_code;
            d.fault_logical=0; d.fault_physical=0;
            if (fault_event_valid) begin
                if (fault_event_address_valid) begin
                    d.fault_logical=fault_event_address; d.fault_physical=fault_event_physical_address;
                end
                d.fault_detail[2:0]={fault_event_write,fault_event_resp};
            end
        end
        if (fault_event_valid && fault_event_protocol || protocol_isolated || !epoch_ledger_ok) begin
            d.isolated=1; d.fault_detail[4]=1;
        end
        if (select_fault && (q.state != RECOVERING && q.state != FAULT_ISOLATED)) begin
            d.state=RECOVERING; d.owner=1; d.head=0; d.drain_cycles=0;
            d.diagnostic_status=status_sample; d.diagnostic_error=0;
            d.reset_sent=0; d.reset_age=0; d.stop_confirmed=0;
        end
        if (select_fault && q.ack_pending) begin
            // ACK未提交期间出现故障，必须释放控制槽，让诊断和复位继续前进。
            d.ack_pending=0; d.bvalid=1; d.bresp=SLVERR; d.last_reject=3;
        end
        if (q.state == RECOVERING || q.state == FAULT_ISOLATED) begin
            if (q.drain_cycles != 32'hffffffff) d.drain_cycles=q.drain_cycles+32'd1;
            if (!ledger_empty && q.drain_timeout != 0 && d.drain_cycles >= q.drain_timeout) begin
                d.state=FAULT_ISOLATED; d.fault_detail[3]=1;
                if (!d.first_selected) begin d.first_selected=1; d.error_code=12; end
            end
            if (d.stop_confirmed && ledger_empty && !core_mem_valid && visibility_confirmed &&
                !d.first_pending && d.first_selected && !d.isolated && !protocol_isolated && !fault_event_valid) begin
                d.state=ERROR_SAFE; d.owner=0; d.head=0;
            end
        end
        if (d.isolated) begin d.state=FAULT_ISOLATED; d.owner=1; d.head=0; end
        if (q.state == RUN && !select_fault && !d.first_pending && !d.withdrawn_seen &&
            status_sample && core_csr_rdata[3:0] == 4'b0010 && !core_mem_valid &&
            ledger_empty && visibility_confirmed && !d.isolated) begin
            d.state=DONE_SAFE; d.owner=0; d.head=1;
        end

        // 普通读取最后使用聚合后的快照；既有R背压时只保留此前样本。
        status_value[2:0]=d.state;
        status_value[8]=d.owner; status_value[9]=d.head;
        status_value[10]=(d.state == IDLE_PS || safe_terminal(d.state)) && !d.isolated;
        status_value[11]=safe_terminal(d.state);
        status_value[12]=!ledger_empty_next; status_value[13]=d.first_pending;
        case (s_axi_araddr[15:0])
            16'h000: read_value=32'h53324250;
            16'h004: read_value=32'h00000100;
            16'h00c: read_value=status_value;
            16'h010: read_value=d.error_code;
            16'h014: read_value=d.frame;
            16'h018: read_value=d.input_addr;
            16'h01c: read_value=d.input_bytes;
            16'h020: read_value=d.weight_addr;
            16'h024: read_value=d.weight_bytes;
            16'h028: read_value=d.core_timeout;
            16'h02c: read_value=d.drain_timeout;
            16'h030: read_value=32'h10000000;
            16'h034: read_value=32'h02000000;
            16'h038: read_value=32'h01000000;
            16'h03c: read_value=32'h01adadb8;
            16'h040: read_value=32'h01a46100;
            16'h044: read_value=5070;
            16'h048: read_value=32'h01ad5e80;
            16'h04c: read_value=20280;
            16'h050: read_value=d.epoch[31:0];
            16'h054: read_value=d.epoch[63:32];
            16'h058: read_value=d.active_frame;
            16'h05c: read_value=d.ack_epoch[31:0];
            16'h060: read_value=d.ack_epoch[63:32];
            16'h064: read_value=d.last_reject;
            16'h068: read_value={22'd0,axi_progress_next};
            16'h06c: read_value=d.fault_logical;
            16'h070: read_value=d.fault_physical;
            16'h074: read_value={27'd0,d.fault_detail};
            default: read_value=0;
        endcase
        if (s_axi_arvalid && s_axi_arready) begin
            if (debug_address) begin d.debug_pending=1; d.debug_addr=s_axi_araddr[7:0]; end
            else begin
                d.rvalid=1; d.rdata=read_address_ok ? read_value : 0;
                d.rresp=read_address_ok ? OKAY : DECERR;
            end
        end
    end

    always_ff @(posedge clk) begin
        if (cold_reset) begin
            q <= '0;
            q.input_bytes <= 519168;
            q.weight_addr <= 32'h00100000;
            q.weight_bytes <= 5903100;
        end else q <= d;
    end
endmodule
