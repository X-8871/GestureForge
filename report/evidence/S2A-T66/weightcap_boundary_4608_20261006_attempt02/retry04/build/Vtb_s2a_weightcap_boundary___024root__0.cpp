// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_weightcap_boundary.h for the primary calling header

#include "Vtb_s2a_weightcap_boundary__pch.h"

VlCoroutine Vtb_s2a_weightcap_boundary___024root___eval_initial__TOP__Vtiming__0(Vtb_s2a_weightcap_boundary___024root* vlSelf);
VlCoroutine Vtb_s2a_weightcap_boundary___024root___eval_initial__TOP__Vtiming__1(Vtb_s2a_weightcap_boundary___024root* vlSelf);

void Vtb_s2a_weightcap_boundary___024root___eval_initial(Vtb_s2a_weightcap_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_weightcap_boundary___024root___eval_initial\n"); );
    Vtb_s2a_weightcap_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_s2a_weightcap_boundary___024root___eval_initial__TOP__Vtiming__0(vlSelf);
    Vtb_s2a_weightcap_boundary___024root___eval_initial__TOP__Vtiming__1(vlSelf);
}

void Vtb_s2a_weightcap_boundary___024root____VbeforeTrig_h7384c754__0(Vtb_s2a_weightcap_boundary___024root* vlSelf, const char* __VeventDescription);
void Vtb_s2a_weightcap_boundary___024root____VbeforeTrig_h2a9b4c34__0(Vtb_s2a_weightcap_boundary___024root* vlSelf, const char* __VeventDescription);

VlCoroutine Vtb_s2a_weightcap_boundary___024root___eval_initial__TOP__Vtiming__0(Vtb_s2a_weightcap_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_weightcap_boundary___024root___eval_initial__TOP__Vtiming__0\n"); );
    Vtb_s2a_weightcap_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__unnamedblk1_1__DOT____Vrepeat0;
    tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__unnamedblk1_1__DOT____Vrepeat0 = 0;
    IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__unnamedblk1_2__DOT____Vrepeat1;
    tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__unnamedblk1_2__DOT____Vrepeat1 = 0;
    IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__unnamedblk1_3__DOT____Vrepeat2;
    tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__unnamedblk1_3__DOT____Vrepeat2 = 0;
    // Body
    tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__unnamedblk1_1__DOT____Vrepeat0 = 3U;
    while (VL_LTS_III(32, 0U, tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__unnamedblk1_1__DOT____Vrepeat0)) {
        Vtb_s2a_weightcap_boundary___024root____VbeforeTrig_h7384c754__0(vlSelf, 
                                                                         "@(negedge tb_s2a_weightcap_boundary.clk)");
        co_await vlSelfRef.__VtrigSched_h7384c754__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(negedge tb_s2a_weightcap_boundary.clk)", 
                                                             "D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 
                                                             193);
        tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__unnamedblk1_1__DOT____Vrepeat0 
            = (tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__unnamedblk1_1__DOT____Vrepeat0 
               - (IData)(1U));
    }
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__hard_reset = 0U;
    while ((1U & (~ (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__start_ready)))) {
        Vtb_s2a_weightcap_boundary___024root____VbeforeTrig_h2a9b4c34__0(vlSelf, 
                                                                         "@( tb_s2a_weightcap_boundary.start_ready)");
        co_await vlSelfRef.__VtrigSched_h2a9b4c34__0.trigger(1U, 
                                                             nullptr, 
                                                             "@( tb_s2a_weightcap_boundary.start_ready)", 
                                                             "D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 
                                                             195);
    }
    Vtb_s2a_weightcap_boundary___024root____VbeforeTrig_h7384c754__0(vlSelf, 
                                                                     "@(negedge tb_s2a_weightcap_boundary.clk)");
    co_await vlSelfRef.__VtrigSched_h7384c754__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_weightcap_boundary.clk)", 
                                                         "D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 
                                                         196);
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__start_valid = 1U;
    Vtb_s2a_weightcap_boundary___024root____VbeforeTrig_h7384c754__0(vlSelf, 
                                                                     "@(negedge tb_s2a_weightcap_boundary.clk)");
    co_await vlSelfRef.__VtrigSched_h7384c754__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_weightcap_boundary.clk)", 
                                                         "D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 
                                                         198);
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__start_valid = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__wait_cycles = 0U;
    while ((0x13U != (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
        Vtb_s2a_weightcap_boundary___024root____VbeforeTrig_h7384c754__0(vlSelf, 
                                                                         "@(negedge tb_s2a_weightcap_boundary.clk)");
        co_await vlSelfRef.__VtrigSched_h7384c754__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(negedge tb_s2a_weightcap_boundary.clk)", 
                                                             "D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 
                                                             203);
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__wait_cycles 
            = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__wait_cycles);
        if (VL_UNLIKELY((VL_LTS_III(32, 0x001e8480U, vlSelfRef.tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__wait_cycles)))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_weightcap_boundary.sv:206: Assertion failed in %m: K=4608 accepted-run timed out; requests=%0d\n",4, 'M',vlSymsp->name(),"tb_s2a_weightcap_boundary.run_boundary_cases", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000)
                         , '~',32,vlSelfRef.tb_s2a_weightcap_boundary__DOT__request_count);
            VL_STOP_MT("D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 206, "", false);
        }
    }
    if (VL_UNLIKELY(((0U != (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_weightcap_boundary.sv:210: Assertion failed in %m: K=4608 must be accepted, result_error_code=%0d\n",4, 'M',vlSymsp->name(),"tb_s2a_weightcap_boundary.run_boundary_cases", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',3,(IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched));
        VL_STOP_MT("D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 210, "", false);
    }
    if (VL_UNLIKELY(((((0x00001200U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__feature_read_count) 
                       | (0x00048000U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__weight_read_count)) 
                      | (0x00000200U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__output_write_count))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_weightcap_boundary.sv:214: Assertion failed in %m: K=4608 transfer coverage mismatch feature=%0d weight=%0d output=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_weightcap_boundary.run_boundary_cases", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,vlSelfRef.tb_s2a_weightcap_boundary__DOT__feature_read_count
                     , '~',32,vlSelfRef.tb_s2a_weightcap_boundary__DOT__weight_read_count
                     , '~',32,vlSelfRef.tb_s2a_weightcap_boundary__DOT__output_write_count);
        VL_STOP_MT("D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 214, "", false);
    }
    if (VL_UNLIKELY(((1U & ((((0U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__max_lane_last_index_fetch_count) 
                              | (~ (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__saw_final_package_weight_byte))) 
                             | (0x00000040U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__final_tap_count)) 
                            | (0xffU != (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__final_tap_lane_mask))))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_weightcap_boundary.sv:219: Assertion failed in %m: K=4608 last-index coverage missing fetch=%0d final_byte=%0d tap=%0d lane_mask=%02h\n",7, 'M',vlSymsp->name(),"tb_s2a_weightcap_boundary.run_boundary_cases", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,vlSelfRef.tb_s2a_weightcap_boundary__DOT__max_lane_last_index_fetch_count
                     , '#',1,(IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__saw_final_package_weight_byte)
                     , '~',32,vlSelfRef.tb_s2a_weightcap_boundary__DOT__final_tap_count
                     , '#',8,(IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__final_tap_lane_mask));
        VL_STOP_MT("D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 219, "", false);
    }
    VL_WRITEF_NX("K4608_PASS input_reads=%0d weight_reads=%0d output_writes=%0d lane7_index4607_fetches=%0d final_tap_cycles=%0d package_last_byte=%0d\n",6
                 , '~',32,vlSelfRef.tb_s2a_weightcap_boundary__DOT__feature_read_count
                 , '~',32,vlSelfRef.tb_s2a_weightcap_boundary__DOT__weight_read_count
                 , '~',32,vlSelfRef.tb_s2a_weightcap_boundary__DOT__output_write_count
                 , '~',32,vlSelfRef.tb_s2a_weightcap_boundary__DOT__max_lane_last_index_fetch_count
                 , '~',32,vlSelfRef.tb_s2a_weightcap_boundary__DOT__final_tap_count
                 , '#',1,(IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__saw_final_package_weight_byte));
    tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__unnamedblk1_2__DOT____Vrepeat1 = 2U;
    while (VL_LTS_III(32, 0U, tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__unnamedblk1_2__DOT____Vrepeat1)) {
        Vtb_s2a_weightcap_boundary___024root____VbeforeTrig_h7384c754__0(vlSelf, 
                                                                         "@(negedge tb_s2a_weightcap_boundary.clk)");
        co_await vlSelfRef.__VtrigSched_h7384c754__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(negedge tb_s2a_weightcap_boundary.clk)", 
                                                             "D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 
                                                             227);
        tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__unnamedblk1_2__DOT____Vrepeat1 
            = (tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__unnamedblk1_2__DOT____Vrepeat1 
               - (IData)(1U));
    }
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__hard_reset = 1U;
    tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__unnamedblk1_3__DOT____Vrepeat2 = 2U;
    while (VL_LTS_III(32, 0U, tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__unnamedblk1_3__DOT____Vrepeat2)) {
        Vtb_s2a_weightcap_boundary___024root____VbeforeTrig_h7384c754__0(vlSelf, 
                                                                         "@(negedge tb_s2a_weightcap_boundary.clk)");
        co_await vlSelfRef.__VtrigSched_h7384c754__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(negedge tb_s2a_weightcap_boundary.clk)", 
                                                             "D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 
                                                             229);
        tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__unnamedblk1_3__DOT____Vrepeat2 
            = (tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__unnamedblk1_3__DOT____Vrepeat2 
               - (IData)(1U));
    }
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__input_length_bytes = 0x00001201U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__input_channels = 0x00001201U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__input_height = 1U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__input_width = 1U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__kernel_height = 1U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__kernel_width = 1U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__output_length_bytes = 0x00000200U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__quantized_weight_bytes = 0x00240200U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__hard_reset = 0U;
    while ((1U & (~ (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__start_ready)))) {
        Vtb_s2a_weightcap_boundary___024root____VbeforeTrig_h2a9b4c34__0(vlSelf, 
                                                                         "@( tb_s2a_weightcap_boundary.start_ready)");
        co_await vlSelfRef.__VtrigSched_h2a9b4c34__0.trigger(1U, 
                                                             nullptr, 
                                                             "@( tb_s2a_weightcap_boundary.start_ready)", 
                                                             "D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 
                                                             239);
    }
    Vtb_s2a_weightcap_boundary___024root____VbeforeTrig_h7384c754__0(vlSelf, 
                                                                     "@(negedge tb_s2a_weightcap_boundary.clk)");
    co_await vlSelfRef.__VtrigSched_h7384c754__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_weightcap_boundary.clk)", 
                                                         "D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 
                                                         240);
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__bad_k_request_baseline 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__request_count;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__start_valid = 1U;
    Vtb_s2a_weightcap_boundary___024root____VbeforeTrig_h7384c754__0(vlSelf, 
                                                                     "@(negedge tb_s2a_weightcap_boundary.clk)");
    co_await vlSelfRef.__VtrigSched_h7384c754__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_weightcap_boundary.clk)", 
                                                         "D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 
                                                         243);
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__start_valid = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__wait_cycles = 0U;
    while ((0x13U != (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
        Vtb_s2a_weightcap_boundary___024root____VbeforeTrig_h7384c754__0(vlSelf, 
                                                                         "@(negedge tb_s2a_weightcap_boundary.clk)");
        co_await vlSelfRef.__VtrigSched_h7384c754__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(negedge tb_s2a_weightcap_boundary.clk)", 
                                                             "D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 
                                                             248);
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__wait_cycles 
            = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__wait_cycles);
        if (VL_UNLIKELY((VL_LTS_III(32, 0x00000014U, vlSelfRef.tb_s2a_weightcap_boundary__DOT__run_boundary_cases__DOT__wait_cycles)))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_weightcap_boundary.sv:251: Assertion failed in %m: K=4609 reject-run timed out; requests=%0d\n",4, 'M',vlSymsp->name(),"tb_s2a_weightcap_boundary.run_boundary_cases", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000)
                         , '~',32,(vlSelfRef.tb_s2a_weightcap_boundary__DOT__request_count 
                                   - vlSelfRef.tb_s2a_weightcap_boundary__DOT__bad_k_request_baseline));
            VL_STOP_MT("D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 251, "", false);
        }
    }
    if (VL_UNLIKELY((((1U != (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched)) 
                      | (vlSelfRef.tb_s2a_weightcap_boundary__DOT__request_count 
                         != vlSelfRef.tb_s2a_weightcap_boundary__DOT__bad_k_request_baseline))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_weightcap_boundary.sv:255: Assertion failed in %m: K=4609 must BAD_ARGUMENT before any memory access: error=%0d requests=%0d\n",5, 'M',vlSymsp->name(),"tb_s2a_weightcap_boundary.run_boundary_cases", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',3,(IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched)
                     , '~',32,(vlSelfRef.tb_s2a_weightcap_boundary__DOT__request_count 
                               - vlSelfRef.tb_s2a_weightcap_boundary__DOT__bad_k_request_baseline));
        VL_STOP_MT("D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 255, "", false);
    }
    VL_WRITEF_NX("K4609_REJECT_PASS result_error_code=%0d prevalidation_memory_requests=%0d\nPASS: exact K boundary 4608 reaches and reads/writes lane RAM index 4607; K=4609 is rejected before memory access\n",2
                 , '#',3,vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched
                 , '~',32,(vlSelfRef.tb_s2a_weightcap_boundary__DOT__request_count 
                           - vlSelfRef.tb_s2a_weightcap_boundary__DOT__bad_k_request_baseline));
    VL_FINISH_MT("D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 261, "");
    co_return;
}

VlCoroutine Vtb_s2a_weightcap_boundary___024root___eval_initial__TOP__Vtiming__1(Vtb_s2a_weightcap_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_weightcap_boundary___024root___eval_initial__TOP__Vtiming__1\n"); );
    Vtb_s2a_weightcap_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    while (VL_LIKELY(!vlSymsp->_vm_contextp__->gotFinish())) {
        co_await vlSelfRef.__VdlySched.delay(0x0000000000001388ULL, 
                                             nullptr, 
                                             "D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 
                                             76);
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__clk 
            = (1U & (~ (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__clk)));
    }
    co_return;
}

bool Vtb_s2a_weightcap_boundary___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_weightcap_boundary___024root___trigger_anySet__act\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        if (in[n]) {
            return (1U);
        }
        n = ((IData)(1U) + n);
    } while ((1U > n));
    return (0U);
}

extern const VlWide<16>/*511:0*/ Vtb_s2a_weightcap_boundary__ConstPool__CONST_h24ab78b6_0;

void Vtb_s2a_weightcap_boundary___024root___nba_sequent__TOP__0(Vtb_s2a_weightcap_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_weightcap_boundary___024root___nba_sequent__TOP__0\n"); );
    Vtb_s2a_weightcap_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlUnpacked<CData/*7:0*/, 512> tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_block;
    for (int __Vi0 = 0; __Vi0 < 512; ++__Vi0) {
        tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_block[__Vi0] = 0;
    }
    VlWide<4>/*127:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_elements_wide;
    VL_ZERO_W(128, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_elements_wide);
    VlWide<4>/*127:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__expected_weight_bytes_wide;
    VL_ZERO_W(128, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__expected_weight_bytes_wide);
    VlWide<4>/*127:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_end_wide;
    VL_ZERO_W(128, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_end_wide;
    VL_ZERO_W(128, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_package_end_wide;
    VL_ZERO_W(128, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_package_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__quantized_weight_end_wide;
    VL_ZERO_W(128, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__quantized_weight_end_wide);
    QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_numerator;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_numerator = 0;
    QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_numerator;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_numerator = 0;
    QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_shape_span;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_shape_span = 0;
    QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_shape_span;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_shape_span = 0;
    QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_shape_product;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_shape_product = 0;
    QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_shape_product;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_shape_product = 0;
    QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_span_plus_stride;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_span_plus_stride = 0;
    QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_span_plus_stride;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_span_plus_stride = 0;
    VlWide<4>/*127:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_height_wide;
    VL_ZERO_W(128, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_height_wide);
    VlWide<4>/*127:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_width_wide;
    VL_ZERO_W(128, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_width_wide);
    VlWide<4>/*127:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_bytes_wide;
    VL_ZERO_W(128, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_bytes_wide);
    VlWide<4>/*127:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_weight_group_bytes_wide;
    VL_ZERO_W(128, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_weight_group_bytes_wide);
    QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_plane_bytes;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_plane_bytes = 0;
    QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_input_y;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_input_y = 0;
    QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_input_x;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_input_x = 0;
    QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_source_offset;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_source_offset = 0;
    IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_area;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_area = 0;
    IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_next_input_channel;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_next_input_channel = 0;
    IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_next_kernel_y;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_next_kernel_y = 0;
    IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_next_reduction_index;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_next_reduction_index = 0;
    IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_point_y;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_point_y = 0;
    IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_point_x;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_point_x = 0;
    IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_input_channel;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_input_channel = 0;
    IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_kernel_y;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_kernel_y = 0;
    IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_kernel_x;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_kernel_x = 0;
    QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_input_y;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_input_y = 0;
    QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_input_x;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_input_x = 0;
    QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_feature_index_wide;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_feature_index_wide = 0;
    IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_index;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_index = 0;
    VlWide<3>/*79:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_parameter;
    VL_ZERO_W(80, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_parameter);
    IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_accumulator;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_accumulator = 0;
    IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_multiplier;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_multiplier = 0;
    IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_q_shift;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_q_shift = 0;
    IData/*31:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_magnitude;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_magnitude = 0;
    QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_product;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_product = 0;
    QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_rounding_add;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_rounding_add = 0;
    QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_rounded_magnitude;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_rounded_magnitude = 0;
    QData/*63:0*/ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_signed_value;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_signed_value = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_weightcap_boundary__DOT__strobe_lane__0__Vfuncout;
    __Vfunc_tb_s2a_weightcap_boundary__DOT__strobe_lane__0__Vfuncout = 0;
    CData/*3:0*/ __Vfunc_tb_s2a_weightcap_boundary__DOT__strobe_lane__0__strobe;
    __Vfunc_tb_s2a_weightcap_boundary__DOT__strobe_lane__0__strobe = 0;
    CData/*0:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__memory_pending;
    __Vdly__tb_s2a_weightcap_boundary__DOT__memory_pending = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__response_data;
    __Vdly__tb_s2a_weightcap_boundary__DOT__response_data = 0;
    CData/*4:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_channels_latched;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_channels_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_channels_latched;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_channels_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_height_latched;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_height_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_width_latched;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_width_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_y_latched;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_y_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_x_latched;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_x_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_latched;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_height;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_height = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_width;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_width = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_height;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_height = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_width;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_width = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_byte_count;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_byte_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_point_count;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_point_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_index;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_channel;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_channel = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_y;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_x;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_index;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_y;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_x;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_reduction_index;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_reduction_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_input_channel;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_input_channel = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_y;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_x;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_lane_index;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_lane_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_index;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_y;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_x;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_lane;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_lane = 0;
    IData/*31:0*/ __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_lane_index;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_lane_index = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v0;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v0 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_block__v0;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_block__v0 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_block__v0;
    __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_block__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_block__v0;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_block__v0 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v0;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v0;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v0 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v1;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v1;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v1 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v2;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v2 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v2;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v2 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v3;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v3 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v3;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v3 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v4;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v4 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v4;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v4 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v5;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v5 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v5;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v5 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v6;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v6 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v6;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v6 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v7;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v7 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v7;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v7 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v8;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v8 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v8;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v8 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v9;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v9 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v9;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v9 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v10;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v10 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v11;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v11 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v12;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v12 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v13;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v13 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v14;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v14 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v15;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v15 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v16;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v16 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v16;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v16 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v17;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v17 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v17;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v17 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v18;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v18 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v19;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v19 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v20;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v20 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v21;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v21 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v22;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v22 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v23;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v23 = 0;
    VlWide<3>/*79:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v8;
    VL_ZERO_W(80, __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v8);
    CData/*2:0*/ __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v8;
    __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v8 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v8;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v8 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias__v8;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias__v8 = 0;
    CData/*2:0*/ __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias__v8;
    __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias__v8 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v0;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v0 = 0;
    SData/*15:0*/ __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v0;
    __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v0;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v0 = 0;
    SData/*15:0*/ __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v1;
    __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v1;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v1 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v0;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v0 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v1;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v1;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v1 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v2;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v2 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v3;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v3 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v3;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v3 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v4;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v4 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v5;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v5 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v5;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v5 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v6;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v6 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v7;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v7 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v7;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v7 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v8;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v8 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v9;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v9 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v9;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v9 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v10;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v10 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v11;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v11 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v11;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v11 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v12;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v12 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v13;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v13 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v13;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v13 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v14;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v14 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v15;
    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v15 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v15;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v15 = 0;
    VlWide<4>/*127:0*/ __Vtemp_1;
    VlWide<3>/*95:0*/ __Vtemp_11;
    VlWide<3>/*95:0*/ __Vtemp_12;
    VlWide<4>/*127:0*/ __Vtemp_14;
    VlWide<4>/*127:0*/ __Vtemp_15;
    VlWide<4>/*127:0*/ __Vtemp_16;
    VlWide<4>/*127:0*/ __Vtemp_17;
    VlWide<4>/*127:0*/ __Vtemp_18;
    VlWide<4>/*127:0*/ __Vtemp_19;
    VlWide<4>/*127:0*/ __Vtemp_20;
    VlWide<4>/*127:0*/ __Vtemp_21;
    VlWide<4>/*127:0*/ __Vtemp_22;
    VlWide<4>/*127:0*/ __Vtemp_23;
    VlWide<4>/*127:0*/ __Vtemp_24;
    VlWide<4>/*127:0*/ __Vtemp_25;
    VlWide<4>/*127:0*/ __Vtemp_26;
    VlWide<4>/*127:0*/ __Vtemp_27;
    VlWide<4>/*127:0*/ __Vtemp_28;
    VlWide<4>/*127:0*/ __Vtemp_29;
    VlWide<4>/*127:0*/ __Vtemp_30;
    VlWide<4>/*127:0*/ __Vtemp_31;
    VlWide<4>/*127:0*/ __Vtemp_32;
    VlWide<4>/*127:0*/ __Vtemp_33;
    VlWide<4>/*127:0*/ __Vtemp_34;
    VlWide<4>/*127:0*/ __Vtemp_35;
    VlWide<4>/*127:0*/ __Vtemp_36;
    VlWide<4>/*127:0*/ __Vtemp_37;
    VlWide<4>/*127:0*/ __Vtemp_38;
    VlWide<4>/*127:0*/ __Vtemp_39;
    VlWide<4>/*127:0*/ __Vtemp_40;
    VlWide<4>/*127:0*/ __Vtemp_41;
    VlWide<4>/*127:0*/ __Vtemp_42;
    VlWide<4>/*127:0*/ __Vtemp_43;
    VlWide<4>/*127:0*/ __Vtemp_44;
    VlWide<4>/*127:0*/ __Vtemp_45;
    VlWide<4>/*127:0*/ __Vtemp_46;
    VlWide<4>/*127:0*/ __Vtemp_47;
    VlWide<4>/*127:0*/ __Vtemp_48;
    VlWide<4>/*127:0*/ __Vtemp_49;
    VlWide<4>/*127:0*/ __Vtemp_50;
    VlWide<4>/*127:0*/ __Vtemp_51;
    VlWide<4>/*127:0*/ __Vtemp_52;
    VlWide<4>/*127:0*/ __Vtemp_53;
    VlWide<4>/*127:0*/ __Vtemp_54;
    VlWide<4>/*127:0*/ __Vtemp_56;
    VlWide<4>/*127:0*/ __Vtemp_57;
    VlWide<4>/*127:0*/ __Vtemp_58;
    VlWide<4>/*127:0*/ __Vtemp_59;
    VlWide<4>/*127:0*/ __Vtemp_60;
    VlWide<4>/*127:0*/ __Vtemp_61;
    VlWide<4>/*127:0*/ __Vtemp_62;
    VlWide<4>/*127:0*/ __Vtemp_63;
    VlWide<4>/*127:0*/ __Vtemp_64;
    VlWide<4>/*127:0*/ __Vtemp_65;
    VlWide<4>/*127:0*/ __Vtemp_66;
    VlWide<4>/*127:0*/ __Vtemp_67;
    VlWide<4>/*127:0*/ __Vtemp_68;
    VlWide<4>/*127:0*/ __Vtemp_69;
    // Body
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v0 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v1 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v2 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v3 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v4 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v5 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v6 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v7 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v8 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v9 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v10 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v11 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v12 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v13 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v14 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v15 = 0U;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_height 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_height;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_point_count 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_point_count;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_index 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_index;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_index 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_index;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_block__v0 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v0 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v1 = 0U;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_lane_index 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_lane_index;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_y 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_y;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_x 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_x;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_lane 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_lane;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_lane_index 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_lane_index;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v0 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v8 = 0U;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_channels_latched 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_channels_latched;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_channels_latched 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_channels_latched;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_width 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_width;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_height 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_height;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_width 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_width;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_byte_count 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_byte_count;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_index 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_index;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_channel 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_channel;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_y 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_y;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_x 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_x;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_y 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_y;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_x 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_x;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_reduction_index 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_reduction_index;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_input_channel 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_input_channel;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_y 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_y;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_x 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_x;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_latched 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_latched;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v0 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v1 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v2 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v3 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v4 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v5 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v6 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v7 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v8 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v9 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v16 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v17 = 0U;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_height_latched 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_height_latched;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_width_latched 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_width_latched;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_y_latched 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_y_latched;
    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_x_latched 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_x_latched;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0U;
    __Vdly__tb_s2a_weightcap_boundary__DOT__response_data 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__response_data;
    __Vdly__tb_s2a_weightcap_boundary__DOT__memory_pending 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__memory_pending;
    if ((1U & (~ (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__hard_reset)))) {
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__memory_pending)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mapped_response_error))) 
              & (0U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__response_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__memory_pending)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mapped_response_error))) 
              & (1U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__response_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__memory_pending)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mapped_response_error))) 
              & (2U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__response_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__memory_pending)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mapped_response_error))) 
              & (3U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__response_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__memory_pending)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mapped_response_error))) 
              & (4U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__response_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__memory_pending)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mapped_response_error))) 
              & (5U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__response_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__memory_pending)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mapped_response_error))) 
              & (6U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__response_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__memory_pending)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mapped_response_error))) 
              & (7U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__response_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
    }
    if (vlSelfRef.tb_s2a_weightcap_boundary__DOT__hard_reset) {
        __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v0 = 1U;
        __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v2 = 1U;
        __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v4 = 1U;
        __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v6 = 1U;
        __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v8 = 1U;
        __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v10 = 1U;
        __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v12 = 1U;
        __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v14 = 1U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_in_bounds = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_data = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__memory_pending = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_layer_index_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_base_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_length_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_batch_count_latched = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_channels_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_height_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_width_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_base_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_length_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_batch_count_latched = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_channels_latched = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_height_latched = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_width_latched = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_y_latched = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_x_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__pad_left_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__pad_right_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__pad_top_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__pad_bottom_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__groups_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__padding_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_package_base_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_package_length_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__quantized_weight_offset_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__quantized_weight_bytes_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_batch_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__activation_mode_latched = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_latched = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_height = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_width = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_height = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_width = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_byte_count = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_point_count = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_index = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_channel = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_y = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_x = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_index = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_y = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_x = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_reduction_index = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_input_channel = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_y = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_x = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_lane_index = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_index = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_y = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_x = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_lane = 0U;
        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_lane_index = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_address_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_strobe_latched = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched = 0U;
        __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v0 = 1U;
    } else {
        if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_enable) 
             & (0U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v1 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v1 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_enable) 
             & (1U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v3 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v3 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_enable) 
             & (2U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v5 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v5 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_enable) 
             & (3U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v7 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v7 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_enable) 
             & (4U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v9 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v9 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_enable) 
             & (5U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v11 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v11 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_enable) 
             & (6U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v13 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v13 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_enable) 
             & (7U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v15 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v15 = 1U;
        }
        if (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_enable) {
            if (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_tap_in_bounds) {
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_in_bounds = 1U;
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_data 
                    = ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_feature_index))
                        ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch
                       [(0x0000ffffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_feature_index)]
                        : 0U);
            } else {
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_in_bounds = 0U;
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_data = 0U;
            }
        }
        if (vlSelfRef.tb_s2a_weightcap_boundary__DOT__memory_pending) {
            __Vdly__tb_s2a_weightcap_boundary__DOT__memory_pending = 0U;
        }
        if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_valid) 
             & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_ready))) {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__request_count 
                = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__request_count);
            __Vfunc_tb_s2a_weightcap_boundary__DOT__strobe_lane__0__strobe 
                = ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_write)
                    ? (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_wstrb)
                    : (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_rstrb));
            __Vfunc_tb_s2a_weightcap_boundary__DOT__strobe_lane__0__Vfuncout 
                = Vtb_s2a_weightcap_boundary__ConstPool__CONST_h24ab78b6_0
                [(0x07ffffffU & (IData)(__Vfunc_tb_s2a_weightcap_boundary__DOT__strobe_lane__0__strobe))];
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__selected_lane 
                = __Vfunc_tb_s2a_weightcap_boundary__DOT__strobe_lane__0__Vfuncout;
            __Vdly__tb_s2a_weightcap_boundary__DOT__response_data = 0x01010101U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__memory_pending = 1U;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_weightcap_boundary__DOT__selected_lane)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_weightcap_boundary.sv:124: Assertion failed in %m: \351\235\236\346\263\225\346\210\226\351\235\236 one-hot memory strobe: write=%0d rstrb=%b wstrb=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_weightcap_boundary", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '#',1,(IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_write)
                             , '#',4,vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_rstrb
                             , '#',4,(IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_wstrb));
                VL_STOP_MT("D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 124, "", false);
            }
            if (vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_write) {
                if (VL_UNLIKELY(((((0x01000000U > vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_address_latched) 
                                   | (((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_address_latched)) 
                                       + (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__selected_lane))) 
                                      >= (0x0000000001000000ULL 
                                          + (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__output_length_bytes))))) 
                                  | (0U != (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_rstrb)))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_weightcap_boundary.sv:132: Assertion failed in %m: \350\276\223\345\207\272\345\206\231\345\234\260\345\235\200\346\210\226 strobe \350\266\212\347\225\214: addr=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_weightcap_boundary", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '#',32,vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_address_latched);
                    VL_STOP_MT("D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 132, "", false);
                }
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__output_write_count 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__output_write_count);
            } else if ((((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_address_latched)) 
                         + (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__selected_lane))) 
                        < (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__input_length_bytes)))) {
                if (VL_UNLIKELY(((0U != (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_wstrb))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_weightcap_boundary.sv:137: Assertion failed in %m: \350\276\223\345\205\245\350\257\273\350\257\267\346\261\202\345\220\214\346\227\266\345\270\246\345\206\231 strobe\n",3, 'M',vlSymsp->name(),"tb_s2a_weightcap_boundary", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 137, "", false);
                }
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__feature_read_count 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__feature_read_count);
            } else if (VL_LIKELY((((0x000000000023925cULL 
                                    <= ((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_address_latched)) 
                                        + (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__selected_lane)))) 
                                   & (0x000000000047925cULL 
                                      > ((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_address_latched)) 
                                         + (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__selected_lane)))))))) {
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__unnamedblk1__DOT__weight_offset 
                    = (((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_address_latched)) 
                        + (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__selected_lane))) 
                       - 0x000000000023925cULL);
                if (VL_UNLIKELY(((0U != (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_wstrb))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_weightcap_boundary.sv:146: Assertion failed in %m: \346\235\203\351\207\215\350\257\273\350\257\267\346\261\202\345\220\214\346\227\266\345\270\246\345\206\231 strobe\n",3, 'M',vlSymsp->name(),"tb_s2a_weightcap_boundary.unnamedblk1", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 146, "", false);
                }
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__weight_read_count 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__weight_read_count);
                if (((7U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index) 
                     & (0x000011ffU == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index))) {
                    vlSelfRef.tb_s2a_weightcap_boundary__DOT__max_lane_last_index_fetch_count 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__max_lane_last_index_fetch_count);
                }
                if ((0x000000000023ffffULL == vlSelfRef.tb_s2a_weightcap_boundary__DOT__unnamedblk1__DOT__weight_offset)) {
                    vlSelfRef.tb_s2a_weightcap_boundary__DOT__saw_final_package_weight_byte = 1U;
                }
            } else {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_weightcap_boundary.sv:157: Assertion failed in %m: memory \350\257\267\346\261\202\344\270\215\345\261\236\344\272\216\350\276\223\345\205\245\343\200\201\346\235\203\351\207\215\346\210\226\350\276\223\345\207\272: write=%0d addr=%08h\n",5, 'M',vlSymsp->name(),"tb_s2a_weightcap_boundary", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '#',1,(IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_write)
                             , '#',32,vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_address_latched);
                VL_STOP_MT("D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 157, "", false);
            }
        }
        if (((0x0dU == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)) 
             & (0x000011ffU == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_reduction_index))) {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__final_tap_count 
                = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__final_tap_count);
            if (VL_UNLIKELY((((((((((1U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory[4607U]) 
                                    | (1U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory[4607U])) 
                                   | (1U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory[4607U])) 
                                  | (1U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory[4607U])) 
                                 | (1U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory[4607U])) 
                                | (1U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory[4607U])) 
                               | (1U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory[4607U])) 
                              | (1U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory[4607U]))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_weightcap_boundary.sv:174: Assertion failed in %m: K=4608 \346\235\203\351\207\215\346\234\253\351\241\271 index=4607 \346\234\252\346\210\220\345\212\237\345\206\231\345\205\245\345\205\250\351\203\250 8 \344\270\252 lane RAM\n",3, 'M',vlSymsp->name(),"tb_s2a_weightcap_boundary", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 174, "", false);
            }
            if (VL_UNLIKELY((((((((((1U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[0U]) 
                                    | (1U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[1U])) 
                                   | (1U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[2U])) 
                                  | (1U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[3U])) 
                                 | (1U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[4U])) 
                                | (1U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[5U])) 
                               | (1U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[6U])) 
                              | (1U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[7U]))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_weightcap_boundary.sv:184: Assertion failed in %m: K=4608 \346\235\203\351\207\215\346\234\253\351\241\271 index=4607 \346\234\252\350\242\253\345\205\250\351\203\250 8 \344\270\252 lane \347\232\204 MAC \350\257\273\345\217\226\n",3, 'M',vlSymsp->name(),"tb_s2a_weightcap_boundary", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 184, "", false);
            }
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__final_tap_lane_mask = 0xffU;
        }
        if (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_advance) {
            if ((((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_x) 
                 >= vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_width)) {
                if ((((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_y) 
                     >= vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_height)) {
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_channel 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_channel);
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_y = 0U;
                } else {
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_y 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_y);
                }
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_x = 0U;
            } else {
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_x 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_x);
            }
        }
        if ((0x00000010U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
            if ((8U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched = 6U;
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x13U;
            } else if ((4U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched = 6U;
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x13U;
            } else if ((2U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
                if ((1U & (~ (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)))) {
                    if ((((IData)(8U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base) 
                         < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_channels_latched)) {
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base 
                            = ((IData)(8U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base);
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 6U;
                    } else if (((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x 
                                 + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_width) 
                                < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched)) {
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x 
                            = ((IData)(8U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x);
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base = 0U;
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 2U;
                    } else if (((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y 
                                 + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_height) 
                                < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched)) {
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y 
                            = ((IData)(8U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y);
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base = 0U;
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x = 0U;
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 2U;
                    } else {
                        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched = 0U;
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x13U;
                    }
                }
            } else if ((1U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
                if (vlSelfRef.tb_s2a_weightcap_boundary__DOT__memory_pending) {
                    if ((0U != (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mapped_response_error))) {
                        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched 
                            = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mapped_response_error;
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x13U;
                    } else {
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_index);
                        if ((((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_x) 
                             >= vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_width)) {
                            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_y 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_y);
                            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_x = 0U;
                        } else {
                            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_x 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_x);
                        }
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x0fU;
                    }
                }
            } else if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_valid) 
                        & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_ready))) {
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x11U;
            }
        } else if ((8U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
            if ((4U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
                if ((2U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
                    if ((1U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
                        if ((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_lane_index 
                             >= vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
                            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x12U;
                        } else if ((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_index 
                                    >= vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_point_count)) {
                            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_lane_index 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_lane_index);
                            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_index = 0U;
                            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_y = 0U;
                            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_x = 0U;
                        } else {
                            __Vtemp_1[0U] = (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_byte_offset_wide);
                            __Vtemp_1[1U] = (IData)(
                                                    (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_byte_offset_wide 
                                                     >> 0x00000020U));
                            __Vtemp_1[2U] = 0U;
                            __Vtemp_1[3U] = 0U;
                            if (((0x00000000ffffffffULL 
                                  < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_address_wide) 
                                 | VL_GTE_W(4, __Vtemp_1, vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_elements_wide))) {
                                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched = 2U;
                                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x13U;
                            } else {
                                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_address_latched 
                                    = ((IData)((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_address_wide 
                                                >> 2U)) 
                                       << 2U);
                                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_strobe_latched 
                                    = (0x0000000fU 
                                       & ((IData)(1U) 
                                          << (3U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_address_wide))));
                                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x10U;
                            }
                        }
                    } else {
                        if ((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_lane_index 
                             < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_block__v0 
                                = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requantized_value;
                            __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_block__v0 
                                = (0x000001ffU & ((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_lane_index 
                                                   << 6U) 
                                                  + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_index));
                            __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_block__v0 = 1U;
                        }
                        if ((((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_lane_index) 
                             >= vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
                            if ((((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_index) 
                                 >= vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_point_count)) {
                                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_lane_index = 0U;
                                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_index = 0U;
                                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_y = 0U;
                                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_x = 0U;
                                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x0fU;
                            } else {
                                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_index 
                                    = ((IData)(1U) 
                                       + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_index);
                                if ((((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_x) 
                                     >= vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_width)) {
                                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_y 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_y);
                                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_x = 0U;
                                } else {
                                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_x 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_x);
                                }
                                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_reduction_index = 0U;
                                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x0cU;
                            }
                        } else {
                            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_lane_index 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_lane_index);
                        }
                    }
                } else if ((1U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
                    if (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_bad_argument) {
                        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched = 1U;
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x13U;
                    } else if (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_overflow) {
                        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched = 7U;
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x13U;
                    } else {
                        if ((0U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v0 
                                = (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[0U]);
                            __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v0 = 1U;
                        }
                        if ((((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_reduction_index) 
                             >= vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_latched)) {
                            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_lane_index = 0U;
                            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x0eU;
                        } else {
                            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_reduction_index 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_reduction_index);
                            if ((((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_x) 
                                 >= vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_width_latched)) {
                                if ((((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_y) 
                                     >= vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_height_latched)) {
                                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_input_channel 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_input_channel);
                                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_y = 0U;
                                } else {
                                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_y 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_y);
                                }
                                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_x = 0U;
                            } else {
                                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_x 
                                    = ((IData)(1U) 
                                       + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_x);
                            }
                        }
                        if ((1U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v1 
                                = (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[1U]);
                            __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v1 = 1U;
                        }
                        if ((2U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v2 
                                = (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[2U]);
                            __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v2 = 1U;
                        }
                        if ((3U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v3 
                                = (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[3U]);
                            __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v3 = 1U;
                        }
                        if ((4U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v4 
                                = (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[4U]);
                            __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v4 = 1U;
                        }
                        if ((5U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v5 
                                = (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[5U]);
                            __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v5 = 1U;
                        }
                        if ((6U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v6 
                                = (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[6U]);
                            __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v6 = 1U;
                        }
                        if ((7U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v7 
                                = (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[7U]);
                            __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v7 = 1U;
                        }
                    }
                } else {
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_input_channel = 0U;
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_y = 0U;
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_x = 0U;
                    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v8 
                        = ((0U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[0U]
                            : 0U);
                    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v8 = 1U;
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_reduction_index = 0U;
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x0dU;
                    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v9 
                        = ((1U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[1U]
                            : 0U);
                    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v9 = 1U;
                    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v10 
                        = ((2U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[2U]
                            : 0U);
                    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v11 
                        = ((3U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[3U]
                            : 0U);
                    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v12 
                        = ((4U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[4U]
                            : 0U);
                    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v13 
                        = ((5U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[5U]
                            : 0U);
                    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v14 
                        = ((6U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[6U]
                            : 0U);
                    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v15 
                        = ((7U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[7U]
                            : 0U);
                }
            } else if ((2U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_input_channel = 0U;
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_y = 0U;
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_x = 0U;
                    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v16 
                        = ((0U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[0U]
                            : 0U);
                    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v16 = 1U;
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_index = 0U;
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_reduction_index = 0U;
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x0dU;
                    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v17 
                        = ((1U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[1U]
                            : 0U);
                    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v17 = 1U;
                    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v18 
                        = ((2U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[2U]
                            : 0U);
                    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v19 
                        = ((3U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[3U]
                            : 0U);
                    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v20 
                        = ((4U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[4U]
                            : 0U);
                    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v21 
                        = ((5U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[5U]
                            : 0U);
                    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v22 
                        = ((6U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[6U]
                            : 0U);
                    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v23 
                        = ((7U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[7U]
                            : 0U);
                } else if (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_invalid) {
                    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched = 1U;
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x13U;
                } else {
                    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v8[0U] 
                        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[0U];
                    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v8[1U] 
                        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[1U];
                    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v8[2U] 
                        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[2U];
                    __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v8 
                        = (7U & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_lane);
                    __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v8 = 1U;
                    __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias__v8 
                        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_bias;
                    __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias__v8 
                        = (7U & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_lane);
                    if ((((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_lane) 
                         >= vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x0bU;
                    } else {
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_lane 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_lane);
                    }
                }
            } else if ((1U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
                if (vlSelfRef.tb_s2a_weightcap_boundary__DOT__memory_pending) {
                    if ((0U != (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mapped_response_error))) {
                        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched 
                            = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mapped_response_error;
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x13U;
                    } else {
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index);
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 7U;
                    }
                }
            } else if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_valid) 
                        & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_ready))) {
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 9U;
            }
        } else if ((4U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
            if ((2U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
                    if ((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index 
                         >= vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_lane = 0U;
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x0aU;
                    } else if ((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index 
                                >= vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_latched)) {
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index);
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index = 0U;
                    } else if ((0x00000000ffffffffULL 
                                < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_source_address_wide)) {
                        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched = 2U;
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x13U;
                    } else {
                        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_address_latched 
                            = ((IData)((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_source_address_wide 
                                        >> 2U)) << 2U);
                        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_strobe_latched 
                            = (0x0000000fU & ((IData)(1U) 
                                              << (3U 
                                                  & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_source_address_wide))));
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 8U;
                    }
                } else if ((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base 
                            >= vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_channels_latched)) {
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x12U;
                } else {
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count 
                        = ((8U <= (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_channels_latched 
                                   - vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base))
                            ? 8U : (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_channels_latched 
                                    - vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base));
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_y = 0U;
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_x = 0U;
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index = 0U;
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index = 0U;
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_lane = 0U;
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 7U;
                }
            } else if ((1U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
                if (vlSelfRef.tb_s2a_weightcap_boundary__DOT__memory_pending) {
                    if ((0U != (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mapped_response_error))) {
                        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched 
                            = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mapped_response_error;
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x13U;
                    } else {
                        if ((0xc7ffU >= (0x0000ffffU 
                                         & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_index))) {
                            __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v0 
                                = (0x000000ffU & VL_SHIFTR_III(8,32,32, vlSelfRef.tb_s2a_weightcap_boundary__DOT__response_data, 
                                                               ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_byte_lane) 
                                                                << 3U)));
                            __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v0 
                                = (0x0000ffffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_index);
                            __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v0 = 1U;
                        }
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 3U;
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_index);
                    }
                }
            } else if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_valid) 
                        & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_ready))) {
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 5U;
            }
        } else if ((2U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
            if ((1U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
                if ((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_index 
                     >= vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_byte_count)) {
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base = 0U;
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 6U;
                } else if (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_in_bounds) {
                    if ((0x00000000ffffffffULL < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_source_address_wide)) {
                        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched = 2U;
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x13U;
                    } else {
                        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_address_latched 
                            = ((IData)((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_source_address_wide 
                                        >> 2U)) << 2U);
                        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_strobe_latched 
                            = (0x0000000fU & ((IData)(1U) 
                                              << (3U 
                                                  & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_source_address_wide))));
                        __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 4U;
                    }
                } else {
                    if ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_index))) {
                        __VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v1 
                            = (0x0000ffffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_index);
                        __VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v1 = 1U;
                    }
                    __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_index 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_index);
                }
            } else {
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_height 
                    = ((8U <= (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched 
                               - vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y))
                        ? 8U : (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched 
                                - vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y));
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_channel = 0U;
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_y = 0U;
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_x = 0U;
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_y = 0U;
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_x = 0U;
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_index = 0U;
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 3U;
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_width 
                    = ((8U <= (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched 
                               - vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x))
                        ? 8U : (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched 
                                - vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x));
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_height 
                    = (((((8U <= (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched 
                                  - vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y))
                           ? 8U : (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched 
                                   - vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y)) 
                         - (IData)(1U)) * vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_y_latched) 
                       + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_height_latched);
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_width 
                    = (((((8U <= (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched 
                                  - vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x))
                           ? 8U : (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched 
                                   - vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x)) 
                         - (IData)(1U)) * vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_x_latched) 
                       + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_width_latched);
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_byte_count 
                    = (((((((8U <= (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched 
                                    - vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y))
                             ? 8U : (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched 
                                     - vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y)) 
                           - (IData)(1U)) * vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_y_latched) 
                         + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_height_latched) 
                        * (((((8U <= (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched 
                                      - vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x))
                               ? 8U : (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched 
                                       - vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x)) 
                             - (IData)(1U)) * vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_x_latched) 
                           + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_width_latched)) 
                       * vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_channels_latched);
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_point_count 
                    = (((8U <= (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched 
                                - vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y))
                         ? 8U : (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched 
                                 - vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y)) 
                       * ((8U <= (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched 
                                  - vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x))
                           ? 8U : (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched 
                                   - vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x)));
            }
        } else if ((1U & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
            if (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__validation_ok) {
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_latched 
                    = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_wide[0U];
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 2U;
            } else {
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched 
                    = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__validation_error;
                __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 0x13U;
            }
        } else if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__start_valid) 
                    & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__start_ready))) {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched = 0x0000001aU;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_layer_index_latched = 0x0000001aU;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_base_latched = 0U;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_length_latched 
                = vlSelfRef.tb_s2a_weightcap_boundary__DOT__input_length_bytes;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_batch_count_latched = 1U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_channels_latched 
                = vlSelfRef.tb_s2a_weightcap_boundary__DOT__input_channels;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_height_latched 
                = vlSelfRef.tb_s2a_weightcap_boundary__DOT__input_height;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_width_latched 
                = vlSelfRef.tb_s2a_weightcap_boundary__DOT__input_width;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_base_latched = 0x01000000U;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_length_latched 
                = vlSelfRef.tb_s2a_weightcap_boundary__DOT__output_length_bytes;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_batch_count_latched = 1U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_channels_latched = 0x00000200U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched = 1U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched = 1U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_height_latched 
                = vlSelfRef.tb_s2a_weightcap_boundary__DOT__kernel_height;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_width_latched 
                = vlSelfRef.tb_s2a_weightcap_boundary__DOT__kernel_width;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_y_latched = 1U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_x_latched = 1U;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__pad_left_latched = 0U;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__pad_right_latched = 0U;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__pad_top_latched = 0U;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__pad_bottom_latched = 0U;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__groups_latched = 1U;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__padding_latched = 0U;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_package_base_latched = 0x00100000U;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_package_length_latched = 0x005a12fcU;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__quantized_weight_offset_latched = 0x0013925cU;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__quantized_weight_bytes_latched 
                = vlSelfRef.tb_s2a_weightcap_boundary__DOT__quantized_weight_bytes;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_batch_latched = 0U;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__activation_mode_latched = 1U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_latched = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_index = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_channel = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_y = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_x = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_index = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_y = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_x = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_reduction_index = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_input_channel = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_y = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_x = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_lane_index = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_index = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_y = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_x = 0U;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__result_error_latched = 0U;
            __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state = 1U;
        }
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v0) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[0U] = 0U;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v1) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[0U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v1;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v2) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[1U] = 0U;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v3) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[1U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v3;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v4) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[2U] = 0U;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v5) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[2U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v5;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v6) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[3U] = 0U;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v7) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[3U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v7;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v8) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[4U] = 0U;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v9) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[4U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v9;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v10) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[5U] = 0U;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v11) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[5U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v11;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v12) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[6U] = 0U;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v13) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[6U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v13;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v14) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[7U] = 0U;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v15) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[7U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte__v15;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0;
    }
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_height 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_height;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_point_count 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_point_count;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_index 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_index;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_index 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_index;
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_block__v0) {
        tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_block[__VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_block__v0] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_block__v0;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v0) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch[__VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v0] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v0;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v1) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch[__VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_patch__v1] = 0U;
    }
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__response_data 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__response_data;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_lane_index 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_lane_index;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_y 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_y;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_x 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_x;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_lane 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_lane;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_lane_index 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_lane_index;
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v0) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[0U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[1U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[2U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[3U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[4U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[5U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[6U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[7U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[0U][0U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[0U][1U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[0U][2U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[1U][0U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[1U][1U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[1U][2U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[2U][0U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[2U][1U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[2U][2U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[3U][0U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[3U][1U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[3U][2U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[4U][0U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[4U][1U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[4U][2U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[5U][0U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[5U][1U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[5U][2U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[6U][0U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[6U][1U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[6U][2U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[7U][0U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[7U][1U] = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[7U][2U] = 0U;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v8) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias[__VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias__v8] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_bias__v8;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[__VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v8][0U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v8[0U];
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[__VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v8][1U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v8[1U];
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter[__VdlyDim0__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v8][2U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter__v8[2U];
    }
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_channels_latched 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_channels_latched;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_channels_latched 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_channels_latched;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_width 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_width;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_height 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_height;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_width 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_width;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_byte_count 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_byte_count;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_index 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_index;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_channel 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_channel;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_y 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_y;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_x 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_x;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_y 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_y;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_x 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_x;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_input_channel 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_input_channel;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_y 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_y;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_x 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_x;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_reduction_index 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_reduction_index;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_latched 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_latched;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__memory_pending 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__memory_pending;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count;
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v0) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[0U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v0;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v1) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[1U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v1;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v2) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[2U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v2;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v3) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[3U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v3;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v4) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[4U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v4;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v5) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[5U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v5;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v6) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[6U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v6;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v7) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[7U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v7;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v8) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[0U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v8;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v9) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[1U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v9;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[2U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v10;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[3U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v11;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[4U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v12;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[5U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v13;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[6U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v14;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[7U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v15;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v16) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[0U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v16;
    }
    if (__VdlySet__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v17) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[1U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v17;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[2U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v18;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[3U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v19;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[4U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v20;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[5U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v21;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[6U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v22;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[7U] 
            = __VdlyVal__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator__v23;
    }
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_height_latched 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_height_latched;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_width_latched 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_width_latched;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_y_latched 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_y_latched;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_x_latched 
        = __Vdly__tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_x_latched;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_byte_lane 
        = (3U & (0x00030210U >> ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_strobe_latched) 
                                 << 1U)));
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_source_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_package_base_latched)) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__quantized_weight_offset_latched)) 
              + ((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_reduction_index)) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_lane_index)))))));
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_byte_offset_wide 
        = ((QData)((IData)((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_x 
                            + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x))) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched)) 
              * ((QData)((IData)((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_point_scan_y 
                                  + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y))) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_lane_index)))))));
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_index = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[0U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[1U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[2U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_bias = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_invalid = 0U;
    if (((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_lane 
          < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count) 
         & (0x00000026U > vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched))) {
        tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_index 
            = ((((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched))
                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                 [(0x0000003fU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched)]
                  : 0U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_group_base) 
               + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_lane);
        if ((0x00000c5cU > tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_index)) {
            if ((0x0c5bU >= (0x00000fffU & tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_index))) {
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[0U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_index)][0U];
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_index)][1U];
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[2U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_index)][2U];
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_bias 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                    [(0x00000fffU & tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_index)];
            } else {
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[0U] = 0U;
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[1U] = 0U;
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[2U] = 0U;
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_bias = 0U;
            }
            if (((((((((tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_index 
                        >= (((0x25U >= (0x0000003fU 
                                        & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched))
                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                             [(0x0000003fU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched)]
                              : 0U) + ((0x25U >= (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched))
                                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                       [(0x0000003fU 
                                         & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched)]
                                        : 0U))) | (0U 
                                                   == 
                                                   ((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[2U] 
                                                     << 0x00000010U) 
                                                    | (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                                       >> 0x00000010U)))) 
                      | (0U == ((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                 << 0x00000018U) | 
                                (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[0U] 
                                 >> 8U)))) | (0x3fffffffU 
                                              < ((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[2U] 
                                                  << 0x00000010U) 
                                                 | (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                                    >> 0x00000010U)))) 
                    | (0x3fffffffU < ((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                       << 0x00000018U) 
                                      | (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[0U] 
                                         >> 8U)))) 
                   | (0x2fU < (0x000000ffU & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                              >> 8U)))) 
                  | (0x2fU < (0x000000ffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[0U]))) 
                 | ((0U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__activation_mode_latched)) 
                    & ((((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[2U] 
                          << 0x00000010U) | (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                             >> 0x00000010U)) 
                        != ((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                             << 0x00000018U) | (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[0U] 
                                                >> 8U))) 
                       | ((0x000000ffU & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                          >> 8U)) != 
                          (0x000000ffU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_parameter[0U])))))) {
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_invalid = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_invalid = 1U;
        }
    } else if ((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_lane 
                < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mq_prefetch_invalid = 1U;
    }
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_parameter[0U] = 0U;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_parameter[1U] = 0U;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_parameter[2U] = 0U;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_accumulator = 0U;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_multiplier = 0U;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_q_shift = 0U;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_magnitude = 0U;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_product = 0ULL;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_rounding_add = 0ULL;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_rounded_magnitude = 0ULL;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_signed_value = 0ULL;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requantized_value = 0U;
    if (((8U > vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_lane_index) 
         & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_lane_index 
            < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count))) {
        tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_parameter[0U] 
            = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_lane_index)][0U];
        tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_parameter[1U] 
            = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_lane_index)][1U];
        tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_parameter[2U] 
            = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_lane_index)][2U];
        tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_accumulator 
            = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator
            [(7U & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_lane_index)];
        if ((tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_accumulator 
             >> 0x1fU)) {
            tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_multiplier 
                = ((tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_parameter[1U] 
                    << 0x00000018U) | (tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_parameter[0U] 
                                       >> 8U));
            tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_magnitude 
                = ((IData)(1U) + (~ tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_accumulator));
            tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_q_shift 
                = (0x000000ffU & tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_parameter[0U]);
        } else {
            tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_multiplier 
                = ((tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_parameter[2U] 
                    << 0x00000010U) | (tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_parameter[1U] 
                                       >> 0x00000010U));
            tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_magnitude 
                = tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_accumulator;
            tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_q_shift 
                = (0x000000ffU & (tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_parameter[1U] 
                                  >> 8U));
        }
        tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_product 
            = ((QData)((IData)(tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_magnitude)) 
               * (QData)((IData)(tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_multiplier)));
        if ((0U != tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_q_shift)) {
            tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_rounding_add 
                = VL_SHIFTL_QQI(64,64,32, 1ULL, (tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_q_shift 
                                                 - (IData)(1U)));
        }
        tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_rounded_magnitude 
            = VL_SHIFTR_QQI(64,64,32, (tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_product 
                                       + tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_rounding_add), tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_q_shift);
        __Vtemp_11[0U] = (IData)(tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_rounded_magnitude);
        __Vtemp_11[1U] = (IData)((tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_rounded_magnitude 
                                  >> 0x00000020U));
        __Vtemp_11[2U] = 0U;
        VL_NEGATE_W(3, __Vtemp_12, __Vtemp_11);
        tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_signed_value 
            = ((tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_accumulator 
                >> 0x1fU) ? (((QData)((IData)(__Vtemp_12[1U])) 
                              << 0x00000020U) | (QData)((IData)(__Vtemp_12[0U])))
                : tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_rounded_magnitude);
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requantized_value 
            = (VL_LTS_IQQ(64, 0x000000000000007fULL, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_signed_value)
                ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_signed_value)
                                  ? 0x00000081U : (0x000000ffU 
                                                   & (IData)(tb_s2a_weightcap_boundary__DOT__u_dut__DOT__requant_signed_value))));
    }
    __Vtemp_14[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_batch_count_latched;
    __Vtemp_14[1U] = 0U;
    __Vtemp_14[2U] = 0U;
    __Vtemp_14[3U] = 0U;
    __Vtemp_15[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_channels_latched;
    __Vtemp_15[1U] = 0U;
    __Vtemp_15[2U] = 0U;
    __Vtemp_15[3U] = 0U;
    VL_MUL_W(4, __Vtemp_16, __Vtemp_14, __Vtemp_15);
    __Vtemp_17[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_height_latched;
    __Vtemp_17[1U] = 0U;
    __Vtemp_17[2U] = 0U;
    __Vtemp_17[3U] = 0U;
    VL_MUL_W(4, __Vtemp_18, __Vtemp_16, __Vtemp_17);
    __Vtemp_19[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_width_latched;
    __Vtemp_19[1U] = 0U;
    __Vtemp_19[2U] = 0U;
    __Vtemp_19[3U] = 0U;
    VL_MUL_W(4, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_elements_wide, __Vtemp_18, __Vtemp_19);
    __Vtemp_20[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_batch_count_latched;
    __Vtemp_20[1U] = 0U;
    __Vtemp_20[2U] = 0U;
    __Vtemp_20[3U] = 0U;
    __Vtemp_21[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_channels_latched;
    __Vtemp_21[1U] = 0U;
    __Vtemp_21[2U] = 0U;
    __Vtemp_21[3U] = 0U;
    VL_MUL_W(4, __Vtemp_22, __Vtemp_20, __Vtemp_21);
    __Vtemp_23[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched;
    __Vtemp_23[1U] = 0U;
    __Vtemp_23[2U] = 0U;
    __Vtemp_23[3U] = 0U;
    VL_MUL_W(4, __Vtemp_24, __Vtemp_22, __Vtemp_23);
    __Vtemp_25[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched;
    __Vtemp_25[1U] = 0U;
    __Vtemp_25[2U] = 0U;
    __Vtemp_25[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_elements_wide, __Vtemp_24, __Vtemp_25);
    __Vtemp_26[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_channels_latched;
    __Vtemp_26[1U] = 0U;
    __Vtemp_26[2U] = 0U;
    __Vtemp_26[3U] = 0U;
    __Vtemp_27[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_channels_latched;
    __Vtemp_27[1U] = 0U;
    __Vtemp_27[2U] = 0U;
    __Vtemp_27[3U] = 0U;
    VL_MUL_W(4, __Vtemp_28, __Vtemp_26, __Vtemp_27);
    __Vtemp_29[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_height_latched;
    __Vtemp_29[1U] = 0U;
    __Vtemp_29[2U] = 0U;
    __Vtemp_29[3U] = 0U;
    VL_MUL_W(4, __Vtemp_30, __Vtemp_28, __Vtemp_29);
    __Vtemp_31[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_width_latched;
    __Vtemp_31[1U] = 0U;
    __Vtemp_31[2U] = 0U;
    __Vtemp_31[3U] = 0U;
    VL_MUL_W(4, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__expected_weight_bytes_wide, __Vtemp_30, __Vtemp_31);
    __Vtemp_32[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_channels_latched;
    __Vtemp_32[1U] = 0U;
    __Vtemp_32[2U] = 0U;
    __Vtemp_32[3U] = 0U;
    __Vtemp_33[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_height_latched;
    __Vtemp_33[1U] = 0U;
    __Vtemp_33[2U] = 0U;
    __Vtemp_33[3U] = 0U;
    VL_MUL_W(4, __Vtemp_34, __Vtemp_32, __Vtemp_33);
    __Vtemp_35[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_width_latched;
    __Vtemp_35[1U] = 0U;
    __Vtemp_35[2U] = 0U;
    __Vtemp_35[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_wide, __Vtemp_34, __Vtemp_35);
    __Vtemp_36[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_base_latched;
    __Vtemp_36[1U] = 0U;
    __Vtemp_36[2U] = 0U;
    __Vtemp_36[3U] = 0U;
    __Vtemp_37[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_length_latched;
    __Vtemp_37[1U] = 0U;
    __Vtemp_37[2U] = 0U;
    __Vtemp_37[3U] = 0U;
    VL_ADD_W(4, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_end_wide, __Vtemp_36, __Vtemp_37);
    __Vtemp_38[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_base_latched;
    __Vtemp_38[1U] = 0U;
    __Vtemp_38[2U] = 0U;
    __Vtemp_38[3U] = 0U;
    __Vtemp_39[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_length_latched;
    __Vtemp_39[1U] = 0U;
    __Vtemp_39[2U] = 0U;
    __Vtemp_39[3U] = 0U;
    VL_ADD_W(4, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_end_wide, __Vtemp_38, __Vtemp_39);
    __Vtemp_40[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_package_base_latched;
    __Vtemp_40[1U] = 0U;
    __Vtemp_40[2U] = 0U;
    __Vtemp_40[3U] = 0U;
    __Vtemp_41[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_package_length_latched;
    __Vtemp_41[1U] = 0U;
    __Vtemp_41[2U] = 0U;
    __Vtemp_41[3U] = 0U;
    VL_ADD_W(4, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_package_end_wide, __Vtemp_40, __Vtemp_41);
    __Vtemp_42[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__quantized_weight_offset_latched;
    __Vtemp_42[1U] = 0U;
    __Vtemp_42[2U] = 0U;
    __Vtemp_42[3U] = 0U;
    __Vtemp_43[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__quantized_weight_bytes_latched;
    __Vtemp_43[1U] = 0U;
    __Vtemp_43[2U] = 0U;
    __Vtemp_43[3U] = 0U;
    VL_ADD_W(4, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__quantized_weight_end_wide, __Vtemp_42, __Vtemp_43);
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_height_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__pad_top_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__pad_bottom_latched)));
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_width_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__pad_left_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__pad_right_latched)));
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_shape_span 
        = (tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_numerator 
           - (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_height_latched)));
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_shape_span 
        = (tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_numerator 
           - (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_width_latched)));
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_shape_product 
        = ((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_y_latched)));
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_shape_product 
        = ((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_x_latched)));
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_span_plus_stride 
        = (tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_shape_span 
           + (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_y_latched)));
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_span_plus_stride 
        = (tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_shape_span 
           + (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_x_latched)));
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_height_wide[0U] = 0U;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_height_wide[1U] = 0U;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_height_wide[2U] = 0U;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_height_wide[3U] = 0U;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_width_wide[0U] = 0U;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_width_wide[1U] = 0U;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_width_wide[2U] = 0U;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_width_wide[3U] = 0U;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_bytes_wide[0U] = 0U;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_bytes_wide[1U] = 0U;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_bytes_wide[2U] = 0U;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_bytes_wide[3U] = 0U;
    if (((0U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched) 
         & (0U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched))) {
        __Vtemp_44[0U] = (((8U > vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched)
                            ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched
                            : 8U) - (IData)(1U));
        __Vtemp_44[1U] = 0U;
        __Vtemp_44[2U] = 0U;
        __Vtemp_44[3U] = 0U;
        __Vtemp_45[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_y_latched;
        __Vtemp_45[1U] = 0U;
        __Vtemp_45[2U] = 0U;
        __Vtemp_45[3U] = 0U;
        VL_MUL_W(4, __Vtemp_46, __Vtemp_44, __Vtemp_45);
        __Vtemp_47[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_height_latched;
        __Vtemp_47[1U] = 0U;
        __Vtemp_47[2U] = 0U;
        __Vtemp_47[3U] = 0U;
        VL_ADD_W(4, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_height_wide, __Vtemp_46, __Vtemp_47);
        __Vtemp_48[0U] = (((8U > vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched)
                            ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched
                            : 8U) - (IData)(1U));
        __Vtemp_48[1U] = 0U;
        __Vtemp_48[2U] = 0U;
        __Vtemp_48[3U] = 0U;
        __Vtemp_49[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_x_latched;
        __Vtemp_49[1U] = 0U;
        __Vtemp_49[2U] = 0U;
        __Vtemp_49[3U] = 0U;
        VL_MUL_W(4, __Vtemp_50, __Vtemp_48, __Vtemp_49);
        __Vtemp_51[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_width_latched;
        __Vtemp_51[1U] = 0U;
        __Vtemp_51[2U] = 0U;
        __Vtemp_51[3U] = 0U;
        VL_ADD_W(4, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_width_wide, __Vtemp_50, __Vtemp_51);
        VL_MUL_W(4, __Vtemp_52, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_height_wide, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_width_wide);
        __Vtemp_53[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_channels_latched;
        __Vtemp_53[1U] = 0U;
        __Vtemp_53[2U] = 0U;
        __Vtemp_53[3U] = 0U;
        VL_MUL_W(4, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_bytes_wide, __Vtemp_52, __Vtemp_53);
    }
    __Vtemp_54[0U] = ((8U > vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_channels_latched)
                       ? vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_channels_latched
                       : 8U);
    __Vtemp_54[1U] = 0U;
    __Vtemp_54[2U] = 0U;
    __Vtemp_54[3U] = 0U;
    VL_MUL_W(4, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_weight_group_bytes_wide, __Vtemp_54, vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_wide);
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__validation_ok = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__validation_error = 1U;
    __Vtemp_56[0U] = 0x00001200U;
    __Vtemp_56[1U] = 0U;
    __Vtemp_56[2U] = 0U;
    __Vtemp_56[3U] = 0U;
    if ((((((((((((((((((((((1U < (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__activation_mode_latched)) 
                            | (1U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_batch_count_latched)) 
                           | (1U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_batch_count_latched)) 
                          | (0U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_batch_latched)) 
                         | (0U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_channels_latched)) 
                        | (0U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_height_latched)) 
                       | (0U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_width_latched)) 
                      | (0U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_channels_latched)) 
                     | (0U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_latched)) 
                    | (0U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_latched)) 
                   | (0U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_height_latched)) 
                  | (0U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_width_latched)) 
                 | (0U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_y_latched)) 
                | (0U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_x_latched)) 
               | (1U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__groups_latched)) 
              | (0U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__padding_latched)) 
             | (0U == (((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_wide[0U] 
                         | vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_wide[1U]) 
                        | vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_wide[2U]) 
                       | vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_wide[3U]))) 
            | VL_LT_W(4, __Vtemp_56, vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_wide)) 
           | (0x00000026U <= vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched)) 
          | ((0x00000026U > vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched) 
             & (0U != ((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched))
                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OP
                       [(0x0000003fU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched)]
                        : 0U)))) | (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched 
                                    != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_layer_index_latched))) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__validation_error 
            = (((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched 
                 != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_layer_index_latched) 
                | (0x00000026U <= vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched))
                ? 2U : 1U);
    } else {
        __Vtemp_57[0U] = 0xffffffffU;
        __Vtemp_57[1U] = 0U;
        __Vtemp_57[2U] = 0U;
        __Vtemp_57[3U] = 0U;
        __Vtemp_58[0U] = 0xffffffffU;
        __Vtemp_58[1U] = 0U;
        __Vtemp_58[2U] = 0U;
        __Vtemp_58[3U] = 0U;
        __Vtemp_59[0U] = 0xffffffffU;
        __Vtemp_59[1U] = 0U;
        __Vtemp_59[2U] = 0U;
        __Vtemp_59[3U] = 0U;
        if ((((((VL_LT_W(4, __Vtemp_57, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_elements_wide) 
                 | (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_length_latched 
                    != tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_elements_wide[0U])) 
                | VL_LT_W(4, __Vtemp_58, vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_elements_wide)) 
               | (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_length_latched 
                  != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_elements_wide[0U])) 
              | VL_LT_W(4, __Vtemp_59, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__expected_weight_bytes_wide)) 
             | (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__quantized_weight_bytes_latched 
                != tb_s2a_weightcap_boundary__DOT__u_dut__DOT__expected_weight_bytes_wide[0U]))) {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__validation_error = 3U;
        } else {
            __Vtemp_60[0U] = 0U;
            __Vtemp_60[1U] = 1U;
            __Vtemp_60[2U] = 0U;
            __Vtemp_60[3U] = 0U;
            __Vtemp_61[0U] = 0U;
            __Vtemp_61[1U] = 1U;
            __Vtemp_61[2U] = 0U;
            __Vtemp_61[3U] = 0U;
            __Vtemp_62[0U] = 0U;
            __Vtemp_62[1U] = 1U;
            __Vtemp_62[2U] = 0U;
            __Vtemp_62[3U] = 0U;
            __Vtemp_63[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_package_length_latched;
            __Vtemp_63[1U] = 0U;
            __Vtemp_63[2U] = 0U;
            __Vtemp_63[3U] = 0U;
            __Vtemp_64[0U] = 0x00000c5cU;
            __Vtemp_64[1U] = 0U;
            __Vtemp_64[2U] = 0U;
            __Vtemp_64[3U] = 0U;
            __Vtemp_65[0U] = ((0x25U >= (0x0000003fU 
                                         & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched))
                               ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                              [(0x0000003fU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched)]
                               : 0U);
            __Vtemp_65[1U] = 0U;
            __Vtemp_65[2U] = 0U;
            __Vtemp_65[3U] = 0U;
            __Vtemp_66[0U] = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_channels_latched;
            __Vtemp_66[1U] = 0U;
            __Vtemp_66[2U] = 0U;
            __Vtemp_66[3U] = 0U;
            VL_ADD_W(4, __Vtemp_67, __Vtemp_65, __Vtemp_66);
            __Vtemp_68[0U] = 0x0000c800U;
            __Vtemp_68[1U] = 0U;
            __Vtemp_68[2U] = 0U;
            __Vtemp_68[3U] = 0U;
            __Vtemp_69[0U] = 0x00009000U;
            __Vtemp_69[1U] = 0U;
            __Vtemp_69[2U] = 0U;
            __Vtemp_69[3U] = 0U;
            if (((((((((VL_LT_W(4, __Vtemp_60, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_end_wide) 
                        | VL_LT_W(4, __Vtemp_61, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_end_wide)) 
                       | VL_LT_W(4, __Vtemp_62, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_package_end_wide)) 
                      | (0U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_package_length_latched)) 
                     | VL_GT_W(4, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__quantized_weight_end_wide, __Vtemp_63)) 
                    | (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                        [(0x0000003fU & vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__layer_index_latched)]
                         : 0U) != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_channels_latched)) 
                   | VL_LT_W(4, __Vtemp_64, __Vtemp_67)) 
                  | VL_LT_W(4, __Vtemp_68, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_tile_patch_bytes_wide)) 
                 | VL_LT_W(4, __Vtemp_69, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__full_weight_group_bytes_wide))) {
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__validation_error = 2U;
            } else if (((((((tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_numerator 
                             < (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_height_latched))) 
                            | (tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_numerator 
                               < (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_width_latched)))) 
                           | (tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_shape_product 
                              <= tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_shape_span)) 
                          | (tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_shape_product 
                             > tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_height_span_plus_stride)) 
                         | (tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_shape_product 
                            <= tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_shape_span)) 
                        | (tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_shape_product 
                           > tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_width_span_plus_stride))) {
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__validation_error = 1U;
            } else {
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__validation_ok = 1U;
                vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__validation_error = 0U;
            }
        }
    }
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_plane_bytes 
        = ((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_height)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_width)));
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_input_y = 0ULL;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_input_x = 0ULL;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_in_bounds = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_advance = 0U;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_source_offset = 0ULL;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_source_address_wide = 0ULL;
    if (((0ULL != tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_plane_bytes) 
         & (0U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_width))) {
        tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_input_y 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_y_latched))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__pad_top_latched)));
        tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_input_x 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_x_latched))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_input_y, (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_input_x, (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_width_latched))));
        if (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_in_bounds) {
            tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_source_offset 
                = (((((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_channel)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_height_latched))) 
                     + tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_input_y) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_width_latched))) 
                   + tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_input_x);
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_source_address_wide 
                = ((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_base_latched)) 
                   + tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_source_offset);
        }
    }
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_area 
        = (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_height_latched 
           * vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_width_latched);
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_next_input_channel 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_input_channel;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_next_kernel_y 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_y;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_next_reduction_index 
        = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_reduction_index);
    if ((((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_x) 
         >= vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_width_latched)) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_next_kernel_x = 0U;
        if ((((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_y) 
             >= vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__kernel_height_latched)) {
            tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_next_kernel_y = 0U;
            tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_next_input_channel 
                = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_input_channel);
        } else {
            tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_next_kernel_y 
                = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_y);
        }
    } else {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_next_kernel_x 
            = ((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_x);
    }
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_point_y 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_y;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_point_x 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_x;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_input_channel 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_input_channel;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_kernel_y 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_y;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_kernel_x 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_x;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_reduction_index 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_reduction_index;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_input_y = 0ULL;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_input_x = 0ULL;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_tap_in_bounds = 0U;
    tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_feature_index_wide = 0ULL;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_feature_index = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_enable = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_bad_argument = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_overflow = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[0U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[0U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[0U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[0U] = 0ULL;
    if ((0U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[0U] 
            = ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[0U] 
            = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[0U];
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[0U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[0U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[0U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[0U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[0U])));
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[0U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[0U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[0U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[0U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[0U])))));
        if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[0U]) 
                | (0x80U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[0U])))) {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[0U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[0U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[1U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[1U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[1U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[1U] = 0ULL;
    if ((1U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[1U] 
            = ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[1U] 
            = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[1U];
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[1U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[1U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[1U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[1U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[1U])));
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[1U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[1U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[1U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[1U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[1U])))));
        if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[1U]) 
                | (0x80U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[1U])))) {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[1U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[1U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[2U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[2U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[2U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[2U] = 0ULL;
    if ((2U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[2U] 
            = ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[2U] 
            = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[2U];
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[2U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[2U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[2U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[2U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[2U])));
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[2U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[2U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[2U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[2U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[2U])))));
        if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[2U]) 
                | (0x80U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[2U])))) {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[2U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[2U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[3U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[3U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[3U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[3U] = 0ULL;
    if ((3U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[3U] 
            = ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[3U] 
            = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[3U];
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[3U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[3U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[3U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[3U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[3U])));
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[3U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[3U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[3U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[3U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[3U])))));
        if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[3U]) 
                | (0x80U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[3U])))) {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[3U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[3U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[4U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[4U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[4U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[4U] = 0ULL;
    if ((4U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[4U] 
            = ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[4U] 
            = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[4U];
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[4U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[4U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[4U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[4U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[4U])));
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[4U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[4U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[4U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[4U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[4U])))));
        if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[4U]) 
                | (0x80U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[4U])))) {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[4U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[4U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[5U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[5U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[5U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[5U] = 0ULL;
    if ((5U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[5U] 
            = ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[5U] 
            = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[5U];
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[5U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[5U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[5U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[5U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[5U])));
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[5U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[5U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[5U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[5U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[5U])))));
        if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[5U]) 
                | (0x80U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[5U])))) {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[5U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[5U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[6U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[6U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[6U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[6U] = 0ULL;
    if ((6U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[6U] 
            = ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[6U] 
            = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[6U];
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[6U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[6U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[6U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[6U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[6U])));
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[6U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[6U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[6U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[6U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[6U])))));
        if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[6U]) 
                | (0x80U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[6U])))) {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[6U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[6U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[7U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[7U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[7U] = 0U;
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[7U] = 0ULL;
    if ((7U < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[7U] 
            = ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[7U] 
            = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__weight_read_byte[7U];
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[7U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[7U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[7U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[7U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[7U])));
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[7U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[7U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__lane_accumulator[7U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[7U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_product[7U])))));
        if (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_feature_byte[7U]) 
                | (0x80U == vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_weight_byte[7U])))) {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[7U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_sum[7U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
    if (((0x0bU == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)) 
         | (0x0cU == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)))) {
        tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_point_y 
            = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_y;
        tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_point_x 
            = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_x;
        tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_input_channel = 0U;
        tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_kernel_y = 0U;
        tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_kernel_x = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_reduction_index = 0U;
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_enable = 1U;
    } else if ((0x0dU == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
        if ((((((IData)(1U) + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_reduction_index) 
               < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__reduction_count_latched) 
              & (~ (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_bad_argument))) 
             & (~ (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_overflow)))) {
            tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_point_y 
                = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_y;
            tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_point_x 
                = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_point_scan_x;
            tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_input_channel 
                = tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_next_input_channel;
            tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_kernel_y 
                = tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_next_kernel_y;
            tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_kernel_x 
                = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_next_kernel_x;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_reduction_index 
                = tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_next_reduction_index;
            vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_enable = 1U;
        }
    }
    if (((0U != tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_kernel_area) 
         & (0U != vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_width))) {
        tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_input_y 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_y)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_y_latched))) 
                 + ((QData)((IData)(tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_point_y)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_y_latched)))) 
                + (QData)((IData)(tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_kernel_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__pad_top_latched)));
        tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_input_x 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__tile_start_x)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_x_latched))) 
                 + ((QData)((IData)(tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_point_x)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_x_latched)))) 
                + (QData)((IData)(tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_kernel_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_tap_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_input_y, (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_input_x, (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__input_width_latched))));
        tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_feature_index_wide 
            = (((((QData)((IData)(tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_input_channel)) 
                  * tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_plane_bytes) 
                 + ((((QData)((IData)(tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_point_y)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_y_latched))) 
                     + (QData)((IData)(tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_kernel_y))) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_width)))) 
                + ((QData)((IData)(tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_point_x)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__stride_x_latched)))) 
               + (QData)((IData)(tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_kernel_x)));
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_feature_index 
            = (IData)(tb_s2a_weightcap_boundary__DOT__u_dut__DOT__compute_read_feature_index_wide);
    }
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mapped_response_error = 0U;
    if ((((3U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)) 
          & (vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_index 
             < vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__patch_byte_count)) 
         & (~ (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_in_bounds)))) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_advance = 1U;
    } else if ((((5U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)) 
                 & (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__memory_pending)) 
                & (0U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__mapped_response_error)))) {
        vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__feature_scan_advance = 1U;
    }
    vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_base_latched)) 
           + vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__output_byte_offset_wide);
}

void Vtb_s2a_weightcap_boundary___024root___timing_ready(Vtb_s2a_weightcap_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_weightcap_boundary___024root___timing_ready\n"); );
    Vtb_s2a_weightcap_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((2ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VtrigSched_h7384c754__0.ready("@(negedge tb_s2a_weightcap_boundary.clk)");
    }
    if ((4ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VtrigSched_h2a9b4c34__0.ready("@( tb_s2a_weightcap_boundary.start_ready)");
    }
}

void Vtb_s2a_weightcap_boundary___024root___timing_resume(Vtb_s2a_weightcap_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_weightcap_boundary___024root___timing_resume\n"); );
    Vtb_s2a_weightcap_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VtrigSched_h7384c754__0.moveToResumeQueue(
                                                          "@(negedge tb_s2a_weightcap_boundary.clk)");
    vlSelfRef.__VtrigSched_h2a9b4c34__0.moveToResumeQueue(
                                                          "@( tb_s2a_weightcap_boundary.start_ready)");
    vlSelfRef.__VtrigSched_h7384c754__0.resume("@(negedge tb_s2a_weightcap_boundary.clk)");
    vlSelfRef.__VtrigSched_h2a9b4c34__0.resume("@( tb_s2a_weightcap_boundary.start_ready)");
    if ((8ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VdlySched.resume();
    }
}

void Vtb_s2a_weightcap_boundary___024root___trigger_orInto__act_vec_vec(VlUnpacked<QData/*63:0*/, 1> &out, const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_weightcap_boundary___024root___trigger_orInto__act_vec_vec\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        out[n] = (out[n] | in[n]);
        n = ((IData)(1U) + n);
    } while ((0U >= n));
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_weightcap_boundary___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG

bool Vtb_s2a_weightcap_boundary___024root___eval_phase__act(Vtb_s2a_weightcap_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_weightcap_boundary___024root___eval_phase__act\n"); );
    Vtb_s2a_weightcap_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VactExecute;
    // Body
    {
        // Inlined CFunc: _eval_triggers_vec__act
        vlSelfRef.__VactTriggered[0U] = (QData)((IData)(
                                                        (((vlSelfRef.__VdlySched.awaitingCurrentTime() 
                                                           << 3U) 
                                                          | (((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__start_ready) 
                                                              != (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_weightcap_boundary__DOT__start_ready__0)) 
                                                             << 2U)) 
                                                         | ((((~ (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__clk)) 
                                                              & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_weightcap_boundary__DOT__clk__0)) 
                                                             << 1U) 
                                                            | ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__clk) 
                                                               & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_weightcap_boundary__DOT__clk__0)))))));
        vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_weightcap_boundary__DOT__clk__0 
            = vlSelfRef.tb_s2a_weightcap_boundary__DOT__clk;
        vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_weightcap_boundary__DOT__start_ready__0 
            = vlSelfRef.tb_s2a_weightcap_boundary__DOT__start_ready;
    }
    Vtb_s2a_weightcap_boundary___024root___timing_ready(vlSelf);
    Vtb_s2a_weightcap_boundary___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VactTriggered, vlSelfRef.__VactTriggeredAcc);
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vtb_s2a_weightcap_boundary___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
    }
#endif
    Vtb_s2a_weightcap_boundary___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VnbaTriggered, vlSelfRef.__VactTriggered);
    __VactExecute = Vtb_s2a_weightcap_boundary___024root___trigger_anySet__act(vlSelfRef.__VactTriggered);
    if (__VactExecute) {
        vlSelfRef.__VactTriggeredAcc.fill(0ULL);
        Vtb_s2a_weightcap_boundary___024root___timing_resume(vlSelf);
        {
            // Inlined CFunc: _eval_act
            if ((6ULL & vlSelfRef.__VactTriggered[0U])) {
                {
                    // Inlined CFunc: _act_comb__TOP__0
                    vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_write = 0U;
                    vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_valid = 0U;
                    vlSelfRef.tb_s2a_weightcap_boundary__DOT__start_ready 
                        = ((~ (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__hard_reset)) 
                           & (0U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)));
                    vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_ready 
                        = (1U & (~ ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__hard_reset) 
                                    | (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__memory_pending))));
                    vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_rstrb = 0U;
                    vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_wstrb = 0U;
                    if ((1U & (~ (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__hard_reset)))) {
                        if (((4U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)) 
                             || (8U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)))) {
                            vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_write = 0U;
                            vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_valid = 1U;
                            vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_rstrb 
                                = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_strobe_latched;
                        } else if ((0x10U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
                            vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_write = 1U;
                            vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_valid = 1U;
                        }
                        if ((1U & (~ ((4U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)) 
                                      || (8U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)))))) {
                            if ((0x10U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
                                vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_wstrb 
                                    = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_strobe_latched;
                            }
                        }
                    }
                }
            }
        }
    }
    return (__VactExecute);
}

bool Vtb_s2a_weightcap_boundary___024root___eval_phase__inact(Vtb_s2a_weightcap_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_weightcap_boundary___024root___eval_phase__inact\n"); );
    Vtb_s2a_weightcap_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VinactExecute;
    // Body
    __VinactExecute = vlSelfRef.__VdlySched.awaitingZeroDelay();
    if (__VinactExecute) {
        VL_FATAL_MT("D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 1, "", "ZERODLY: Design Verilated with '--no-sched-zero-delay', but #0 delay executed at runtime");
    }
    return (__VinactExecute);
}

void Vtb_s2a_weightcap_boundary___024root___trigger_clear__act(VlUnpacked<QData/*63:0*/, 1> &out) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_weightcap_boundary___024root___trigger_clear__act\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        out[n] = 0ULL;
        n = ((IData)(1U) + n);
    } while ((1U > n));
}

bool Vtb_s2a_weightcap_boundary___024root___eval_phase__nba(Vtb_s2a_weightcap_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_weightcap_boundary___024root___eval_phase__nba\n"); );
    Vtb_s2a_weightcap_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = Vtb_s2a_weightcap_boundary___024root___trigger_anySet__act(vlSelfRef.__VnbaTriggered);
    if (__VnbaExecute) {
        {
            // Inlined CFunc: _eval_nba
            if ((1ULL & vlSelfRef.__VnbaTriggered[0U])) {
                Vtb_s2a_weightcap_boundary___024root___nba_sequent__TOP__0(vlSelf);
            }
            if ((7ULL & vlSelfRef.__VnbaTriggered[0U])) {
                {
                    // Inlined CFunc: _nba_comb__TOP__0
                    vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_ready 
                        = (1U & (~ ((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__hard_reset) 
                                    | (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__memory_pending))));
                    vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_write = 0U;
                    vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_valid = 0U;
                    vlSelfRef.tb_s2a_weightcap_boundary__DOT__start_ready 
                        = ((~ (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__hard_reset)) 
                           & (0U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)));
                    vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_rstrb = 0U;
                    vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_wstrb = 0U;
                    if ((1U & (~ (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__hard_reset)))) {
                        if (((4U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)) 
                             || (8U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)))) {
                            vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_write = 0U;
                            vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_valid = 1U;
                            vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_rstrb 
                                = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_strobe_latched;
                        } else if ((0x10U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
                            vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_write = 1U;
                            vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_valid = 1U;
                        }
                        if ((1U & (~ ((4U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)) 
                                      || (8U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state)))))) {
                            if ((0x10U == (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__state))) {
                                vlSelfRef.tb_s2a_weightcap_boundary__DOT__backend_req_wstrb 
                                    = vlSelfRef.tb_s2a_weightcap_boundary__DOT__u_dut__DOT__request_strobe_latched;
                            }
                        }
                    }
                }
            }
        }
        Vtb_s2a_weightcap_boundary___024root___trigger_clear__act(vlSelfRef.__VnbaTriggered);
    }
    return (__VnbaExecute);
}

void Vtb_s2a_weightcap_boundary___024root___eval(Vtb_s2a_weightcap_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_weightcap_boundary___024root___eval\n"); );
    Vtb_s2a_weightcap_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VnbaIterCount;
    // Body
    __VnbaIterCount = 0U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VnbaIterCount)))) {
#ifdef VL_DEBUG
            Vtb_s2a_weightcap_boundary___024root___dump_triggers__act(vlSelfRef.__VnbaTriggered, "nba"s);
#endif
            VL_FATAL_MT("D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 1, "", "DIDNOTCONVERGE: NBA region did not converge after '--converge-limit' of 10000 tries");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        vlSelfRef.__VinactIterCount = 0U;
        do {
            if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VinactIterCount)))) {
                VL_FATAL_MT("D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 1, "", "DIDNOTCONVERGE: Inactive region did not converge after '--converge-limit' of 10000 tries");
            }
            vlSelfRef.__VinactIterCount = ((IData)(1U) 
                                           + vlSelfRef.__VinactIterCount);
            vlSelfRef.__VactIterCount = 0U;
            do {
                if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                    Vtb_s2a_weightcap_boundary___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
#endif
                    VL_FATAL_MT("D:/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry04\\tb_s2a_weightcap_boundary.sv", 1, "", "DIDNOTCONVERGE: Active region did not converge after '--converge-limit' of 10000 tries");
                }
                vlSelfRef.__VactIterCount = ((IData)(1U) 
                                             + vlSelfRef.__VactIterCount);
                vlSelfRef.__VactPhaseResult = Vtb_s2a_weightcap_boundary___024root___eval_phase__act(vlSelf);
            } while (vlSelfRef.__VactPhaseResult);
            vlSelfRef.__VinactPhaseResult = Vtb_s2a_weightcap_boundary___024root___eval_phase__inact(vlSelf);
        } while (vlSelfRef.__VinactPhaseResult);
        vlSelfRef.__VnbaPhaseResult = Vtb_s2a_weightcap_boundary___024root___eval_phase__nba(vlSelf);
    } while (vlSelfRef.__VnbaPhaseResult);
}

void Vtb_s2a_weightcap_boundary___024root____VbeforeTrig_h7384c754__0(Vtb_s2a_weightcap_boundary___024root* vlSelf, const char* __VeventDescription) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_weightcap_boundary___024root____VbeforeTrig_h7384c754__0\n"); );
    Vtb_s2a_weightcap_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlUnpacked<QData/*63:0*/, 1> __VTmp;
    // Body
    __VTmp[0U] = (QData)((IData)((((~ (IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__clk)) 
                                   & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_weightcap_boundary__DOT__clk__0)) 
                                  << 1U)));
    vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_weightcap_boundary__DOT__clk__0 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__clk;
    if ((2ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_h7384c754__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h7384c754__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h7384c754__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h7384c754__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h7384c754__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h7384c754__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h7384c754__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h7384c754__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h7384c754__0.ready(__VeventDescription);
    }
    vlSelfRef.__VactTriggeredAcc[0U] = (vlSelfRef.__VactTriggeredAcc[0U] 
                                        | __VTmp[0U]);
}

void Vtb_s2a_weightcap_boundary___024root____VbeforeTrig_h2a9b4c34__0(Vtb_s2a_weightcap_boundary___024root* vlSelf, const char* __VeventDescription) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_weightcap_boundary___024root____VbeforeTrig_h2a9b4c34__0\n"); );
    Vtb_s2a_weightcap_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlUnpacked<QData/*63:0*/, 1> __VTmp;
    // Body
    __VTmp[0U] = (QData)((IData)((((IData)(vlSelfRef.tb_s2a_weightcap_boundary__DOT__start_ready) 
                                   != (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_weightcap_boundary__DOT__start_ready__0)) 
                                  << 2U)));
    vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_weightcap_boundary__DOT__start_ready__0 
        = vlSelfRef.tb_s2a_weightcap_boundary__DOT__start_ready;
    if ((4ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_h2a9b4c34__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2a9b4c34__0.ready(__VeventDescription);
    }
    vlSelfRef.__VactTriggeredAcc[0U] = (vlSelfRef.__VactTriggeredAcc[0U] 
                                        | __VTmp[0U]);
}

#ifdef VL_DEBUG
void Vtb_s2a_weightcap_boundary___024root___eval_debug_assertions(Vtb_s2a_weightcap_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_weightcap_boundary___024root___eval_debug_assertions\n"); );
    Vtb_s2a_weightcap_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}
#endif  // VL_DEBUG
