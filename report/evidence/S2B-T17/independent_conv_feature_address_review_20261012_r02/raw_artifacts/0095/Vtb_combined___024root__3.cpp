// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_combined.h for the primary calling header

#include "Vtb_combined__pch.h"

void Vtb_combined___024root___nba_comb__TOP__54(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___nba_comb__TOP__54\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_wstrb = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_cancel 
        = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) 
           | (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_ready 
        = ((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset)) 
           & ((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort)) 
              & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_start_ready 
        = ((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset)) 
           & ((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort)) 
              & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_valid = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_valid = 0U;
    if ((1U & ((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset)) 
               & (~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort))))) {
        if ((1U & (~ ((4U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)) 
                      || (8U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)))))) {
            if ((0x10U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_wstrb 
                    = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_strobe_latched;
            }
        }
        if (((4U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_valid = 1U;
        } else if ((0x10U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_valid = 1U;
        }
        if (((4U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_valid = 1U;
        } else if ((0x10U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_valid = 1U;
        }
    }
}

void Vtb_combined___024root___nba_sequent__TOP__0(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__1(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__2(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__3(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__4(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__5(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__6(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__7(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__8(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__9(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__10(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__11(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__12(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__13(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__14(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__15(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__16(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__17(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__18(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__19(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__20(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__21(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__22(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__23(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__24(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__25(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__26(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__27(Vtb_combined___024root* vlSelf);

void Vtb_combined___024root___eval_nba__0(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_nba__0\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((4ULL & vlSelfRef.__VnbaTriggered[0U])) {
        Vtb_combined___024root___nba_sequent__TOP__0(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__1(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__2(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__3(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__4(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__5(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__6(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__7(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__8(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__9(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__10(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__11(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__12(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__13(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__14(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__15(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__16(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__17(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__18(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__19(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__20(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__21(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__22(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__23(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__24(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__25(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__26(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__27(vlSelf);
    }
}

void Vtb_combined___024root___nba_sequent__TOP__28(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__29(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__30(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__31(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__32(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__34(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__35(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__36(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__37(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__38(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__39(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__40(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__41(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__42(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__43(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__44(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__45(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__46(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__47(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__48(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__49(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__50(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__51(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__52(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__53(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__54(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__55(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__56(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__57(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__58(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__59(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__60(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__61(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__62(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__63(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__64(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__65(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__66(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_sequent__TOP__67(Vtb_combined___024root* vlSelf);

void Vtb_combined___024root___eval_nba__1(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_nba__1\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((2ULL & vlSelfRef.__VnbaTriggered[0U])) {
        Vtb_combined___024root___nba_sequent__TOP__28(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__29(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__30(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__31(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__32(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__34(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__35(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__36(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__37(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__38(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__39(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__40(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__41(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__42(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__43(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__44(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__45(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__46(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__47(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__48(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__49(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__50(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__51(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__52(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__53(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__54(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__55(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__56(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__57(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__58(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__59(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__60(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__61(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__62(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__63(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__64(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__65(vlSelf);
        Vtb_combined___024root___nba_sequent__TOP__66(vlSelf);
    }
    if ((1ULL & vlSelfRef.__VnbaTriggered[0U])) {
        Vtb_combined___024root___nba_sequent__TOP__67(vlSelf);
    }
}

void Vtb_combined___024root___nba_comb__TOP__0(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__1(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__2(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__3(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__4(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__5(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__6(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__7(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__8(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__9(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__10(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_comb__TOP__11(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_comb__TOP__12(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__12(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__13(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__14(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__15(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__16(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__17(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__18(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__19(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__20(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_sequent__TOP__21(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_comb__TOP__23(Vtb_combined___024root* vlSelf);

void Vtb_combined___024root___eval_nba__2(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_nba__2\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((0x0000000000000014ULL & vlSelfRef.__VnbaTriggered[0U])) {
        Vtb_combined___024root___nba_comb__TOP__0(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__1(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__2(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__3(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__4(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__5(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__6(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__7(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__8(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__9(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__10(vlSelf);
        Vtb_combined___024root___nba_comb__TOP__11(vlSelf);
        Vtb_combined___024root___nba_comb__TOP__12(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__12(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__13(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__14(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__15(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__16(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__17(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__18(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__19(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__20(vlSelf);
        Vtb_combined___024root___act_sequent__TOP__21(vlSelf);
        Vtb_combined___024root___nba_comb__TOP__23(vlSelf);
    }
}

void Vtb_combined___024root___timing_ready(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___timing_ready\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((8ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VtrigSched_hf7093994__0.ready("@( (tb_combined.feature_done & tb_combined.boundary_done))");
    }
    if ((2ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready("@(posedge tb_combined.boundary_test.clk)");
    }
    if ((1ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready("@(negedge tb_combined.boundary_test.clk)");
    }
}

void Vtb_combined___024root___timing_resume(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___timing_resume\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VtrigSched_hf7093994__0.moveToResumeQueue(
                                                          "@( (tb_combined.feature_done & tb_combined.boundary_done))");
    vlSelfRef.__VtrigSched_h2fc87fd9__0.moveToResumeQueue(
                                                          "@(posedge tb_combined.boundary_test.clk)");
    vlSelfRef.__VtrigSched_h2fc87fa8__0.moveToResumeQueue(
                                                          "@(negedge tb_combined.boundary_test.clk)");
    vlSelfRef.__VtrigSched_hf7093994__0.resume("@( (tb_combined.feature_done & tb_combined.boundary_done))");
    vlSelfRef.__VtrigSched_h2fc87fd9__0.resume("@(posedge tb_combined.boundary_test.clk)");
    vlSelfRef.__VtrigSched_h2fc87fa8__0.resume("@(negedge tb_combined.boundary_test.clk)");
    if ((0x0000000000000010ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VdlySched.resume();
    }
}

void Vtb_combined___024root___trigger_orInto__act_vec_vec(VlUnpacked<QData/*63:0*/, 1> &out, const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___trigger_orInto__act_vec_vec\n"); );
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
VL_ATTR_COLD void Vtb_combined___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG
bool Vtb_combined___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in);
void Vtb_combined___024root___eval_act(Vtb_combined___024root* vlSelf);

bool Vtb_combined___024root___eval_phase__act(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_phase__act\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VactExecute;
    // Body
    {
        // Inlined CFunc: _eval_triggers_vec__act
        {
            // Inlined CFunc: _eval_triggers_vec__act__0
            vlSelfRef.__Vtrigprevexpr_h6f3df181__0 
                = ((IData)(vlSelfRef.tb_combined__DOT__feature_done) 
                   & (IData)(vlSelfRef.tb_combined__DOT__boundary_done));
        }
        {
            // Inlined CFunc: _eval_triggers_vec__act__1
            vlSelfRef.__VactTriggered[0U] = (QData)((IData)(
                                                            ((vlSelfRef.__VdlySched.awaitingCurrentTime() 
                                                              << 4U) 
                                                             | (((((IData)(vlSelfRef.__Vtrigprevexpr_h6f3df181__0) 
                                                                   != (IData)(vlSelfRef.__Vtrigprevexpr_h6f3df181__1)) 
                                                                  << 3U) 
                                                                 | (((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__clk) 
                                                                     & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_combined__DOT__feature_test__DOT__clk__0))) 
                                                                    << 2U)) 
                                                                | ((((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__clk) 
                                                                     & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_combined__DOT__boundary_test__DOT__clk__0))) 
                                                                    << 1U) 
                                                                   | ((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__clk)) 
                                                                      & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_combined__DOT__boundary_test__DOT__clk__0)))))));
        }
        {
            // Inlined CFunc: _eval_triggers_vec__act__2
            vlSelfRef.__Vtrigprevexpr___TOP__tb_combined__DOT__boundary_test__DOT__clk__0 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__clk;
            vlSelfRef.__Vtrigprevexpr___TOP__tb_combined__DOT__feature_test__DOT__clk__0 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__clk;
            vlSelfRef.__Vtrigprevexpr_h6f3df181__1 
                = vlSelfRef.__Vtrigprevexpr_h6f3df181__0;
        }
    }
    Vtb_combined___024root___timing_ready(vlSelf);
    Vtb_combined___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VactTriggered, vlSelfRef.__VactTriggeredAcc);
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vtb_combined___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
    }
#endif
    Vtb_combined___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VnbaTriggered, vlSelfRef.__VactTriggered);
    __VactExecute = Vtb_combined___024root___trigger_anySet__act(vlSelfRef.__VactTriggered);
    if (__VactExecute) {
        vlSelfRef.__VactTriggeredAcc.fill(0ULL);
        Vtb_combined___024root___timing_resume(vlSelf);
        Vtb_combined___024root___eval_act(vlSelf);
    }
    return (__VactExecute);
}

bool Vtb_combined___024root___eval_phase__inact(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_phase__inact\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VinactExecute;
    // Body
    __VinactExecute = vlSelfRef.__VdlySched.awaitingZeroDelay();
    if (__VinactExecute) {
        VL_FATAL_MT("tb_combined.sv", 3, "", "ZERODLY: Design Verilated with '--no-sched-zero-delay', but #0 delay executed at runtime");
    }
    return (__VinactExecute);
}

void Vtb_combined___024root___trigger_clear__act(VlUnpacked<QData/*63:0*/, 1> &out) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___trigger_clear__act\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        out[n] = 0ULL;
        n = ((IData)(1U) + n);
    } while ((1U > n));
}

void Vtb_combined___024root___nba_comb__TOP__24(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_comb__TOP__25(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__4(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__5(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__6(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__7(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__8(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__9(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__10(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__11(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__12(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__13(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__14(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__15(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__16(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__17(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__18(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__19(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__20(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__21(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__22(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__23(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__24(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__25(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__26(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__27(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__28(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__29(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___act_comb__TOP__30(Vtb_combined___024root* vlSelf);
void Vtb_combined___024root___nba_comb__TOP__53(Vtb_combined___024root* vlSelf);

bool Vtb_combined___024root___eval_phase__nba(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_phase__nba\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = Vtb_combined___024root___trigger_anySet__act(vlSelfRef.__VnbaTriggered);
    if (__VnbaExecute) {
        {
            // Inlined CFunc: _eval_nba
            Vtb_combined___024root___eval_nba__0(vlSelf);
            Vtb_combined___024root___eval_nba__1(vlSelf);
            Vtb_combined___024root___eval_nba__2(vlSelf);
            {
                // Inlined CFunc: _eval_nba__3
                if ((0x0000000000000013ULL & vlSelfRef.__VnbaTriggered[0U])) {
                    Vtb_combined___024root___nba_comb__TOP__24(vlSelf);
                    Vtb_combined___024root___nba_comb__TOP__25(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__4(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__5(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__6(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__7(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__8(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__9(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__10(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__11(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__12(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__13(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__14(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__15(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__16(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__17(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__18(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__19(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__20(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__21(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__22(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__23(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__24(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__25(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__26(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__27(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__28(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__29(vlSelf);
                    Vtb_combined___024root___act_comb__TOP__30(vlSelf);
                    Vtb_combined___024root___nba_comb__TOP__53(vlSelf);
                    Vtb_combined___024root___nba_comb__TOP__54(vlSelf);
                    {
                        // Inlined CFunc: _act_comb__TOP__31
                        vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_cancel 
                            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_cancel;
                    }
                }
            }
        }
        Vtb_combined___024root___trigger_clear__act(vlSelfRef.__VnbaTriggered);
    }
    return (__VnbaExecute);
}

void Vtb_combined___024root___eval(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VnbaIterCount;
    // Body
    __VnbaIterCount = 0U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VnbaIterCount)))) {
#ifdef VL_DEBUG
            Vtb_combined___024root___dump_triggers__act(vlSelfRef.__VnbaTriggered, "nba"s);
#endif
            VL_FATAL_MT("tb_combined.sv", 3, "", "DIDNOTCONVERGE: NBA region did not converge after '--converge-limit' of 10000 tries");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        vlSelfRef.__VinactIterCount = 0U;
        do {
            if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VinactIterCount)))) {
                VL_FATAL_MT("tb_combined.sv", 3, "", "DIDNOTCONVERGE: Inactive region did not converge after '--converge-limit' of 10000 tries");
            }
            vlSelfRef.__VinactIterCount = ((IData)(1U) 
                                           + vlSelfRef.__VinactIterCount);
            vlSelfRef.__VactIterCount = 0U;
            do {
                if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                    Vtb_combined___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
#endif
                    VL_FATAL_MT("tb_combined.sv", 3, "", "DIDNOTCONVERGE: Active region did not converge after '--converge-limit' of 10000 tries");
                }
                vlSelfRef.__VactIterCount = ((IData)(1U) 
                                             + vlSelfRef.__VactIterCount);
                vlSelfRef.__VactPhaseResult = Vtb_combined___024root___eval_phase__act(vlSelf);
            } while (vlSelfRef.__VactPhaseResult);
            vlSelfRef.__VinactPhaseResult = Vtb_combined___024root___eval_phase__inact(vlSelf);
        } while (vlSelfRef.__VinactPhaseResult);
        vlSelfRef.__VnbaPhaseResult = Vtb_combined___024root___eval_phase__nba(vlSelf);
    } while (vlSelfRef.__VnbaPhaseResult);
}

void Vtb_combined___024root____VbeforeTrig_hf7093994__0(Vtb_combined___024root* vlSelf, const char* __VeventDescription) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root____VbeforeTrig_hf7093994__0\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlUnpacked<QData/*63:0*/, 1> __VTmp;
    // Body
    vlSelfRef.__Vtrigprevexpr_h6f3df181__0 = ((IData)(vlSelfRef.tb_combined__DOT__feature_done) 
                                              & (IData)(vlSelfRef.tb_combined__DOT__boundary_done));
    __VTmp[0U] = (QData)((IData)((((IData)(vlSelfRef.__Vtrigprevexpr_h6f3df181__0) 
                                   != (IData)(vlSelfRef.__Vtrigprevexpr_h6f3df181__1)) 
                                  << 3U)));
    vlSelfRef.__Vtrigprevexpr_h6f3df181__1 = vlSelfRef.__Vtrigprevexpr_h6f3df181__0;
    if ((8ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_hf7093994__0.ready(__VeventDescription);
    }
    vlSelfRef.__VactTriggeredAcc[0U] = (vlSelfRef.__VactTriggeredAcc[0U] 
                                        | __VTmp[0U]);
}

void Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(Vtb_combined___024root* vlSelf, const char* __VeventDescription) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlUnpacked<QData/*63:0*/, 1> __VTmp;
    // Body
    __VTmp[0U] = (QData)((IData)(((((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__clk) 
                                    & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_combined__DOT__boundary_test__DOT__clk__0))) 
                                   << 1U) | ((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__clk)) 
                                             & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_combined__DOT__boundary_test__DOT__clk__0)))));
    vlSelfRef.__Vtrigprevexpr___TOP__tb_combined__DOT__boundary_test__DOT__clk__0 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__clk;
    if ((1ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
    }
    if ((2ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
    }
    vlSelfRef.__VactTriggeredAcc[0U] = (vlSelfRef.__VactTriggeredAcc[0U] 
                                        | __VTmp[0U]);
}

void Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(Vtb_combined___024root* vlSelf, const char* __VeventDescription) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlUnpacked<QData/*63:0*/, 1> __VTmp;
    // Body
    __VTmp[0U] = (QData)((IData)(((((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__clk) 
                                    & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_combined__DOT__boundary_test__DOT__clk__0))) 
                                   << 1U) | ((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__clk)) 
                                             & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_combined__DOT__boundary_test__DOT__clk__0)))));
    vlSelfRef.__Vtrigprevexpr___TOP__tb_combined__DOT__boundary_test__DOT__clk__0 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__clk;
    if ((1ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fa8__0.ready(__VeventDescription);
    }
    if ((2ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2fc87fd9__0.ready(__VeventDescription);
    }
    vlSelfRef.__VactTriggeredAcc[0U] = (vlSelfRef.__VactTriggeredAcc[0U] 
                                        | __VTmp[0U]);
}

#ifdef VL_DEBUG
void Vtb_combined___024root___eval_debug_assertions(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_debug_assertions\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}
#endif  // VL_DEBUG
