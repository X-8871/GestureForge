// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_conv_tile_memory.h for the primary calling header

#include "Vtb_s2a_conv_tile_memory__pch.h"

void Vtb_s2a_conv_tile_memory___024root___timing_ready(Vtb_s2a_conv_tile_memory___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___timing_ready\n"); );
    Vtb_s2a_conv_tile_memory__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VtrigSched_hb8586161__0.ready("@(negedge tb_s2a_conv_tile_memory.clk)");
    }
}

void Vtb_s2a_conv_tile_memory___024root___timing_resume(Vtb_s2a_conv_tile_memory___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___timing_resume\n"); );
    Vtb_s2a_conv_tile_memory__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VtrigSched_hb8586161__0.moveToResumeQueue(
                                                          "@(negedge tb_s2a_conv_tile_memory.clk)");
    vlSelfRef.__VtrigSched_hb8586161__0.resume("@(negedge tb_s2a_conv_tile_memory.clk)");
    if ((4ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VdlySched.resume();
    }
}

void Vtb_s2a_conv_tile_memory___024root___trigger_orInto__act_vec_vec(VlUnpacked<QData/*63:0*/, 1> &out, const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___trigger_orInto__act_vec_vec\n"); );
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
VL_ATTR_COLD void Vtb_s2a_conv_tile_memory___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG
bool Vtb_s2a_conv_tile_memory___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in);
void Vtb_s2a_conv_tile_memory___024root___act_comb__TOP__0(Vtb_s2a_conv_tile_memory___024root* vlSelf);

bool Vtb_s2a_conv_tile_memory___024root___eval_phase__act(Vtb_s2a_conv_tile_memory___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___eval_phase__act\n"); );
    Vtb_s2a_conv_tile_memory__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VactExecute;
    // Body
    {
        // Inlined CFunc: _eval_triggers_vec__act
        vlSelfRef.__VactTriggered[0U] = (QData)((IData)(
                                                        ((vlSelfRef.__VdlySched.awaitingCurrentTime() 
                                                          << 2U) 
                                                         | ((((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__clk) 
                                                              & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_conv_tile_memory__DOT__clk__0))) 
                                                             << 1U) 
                                                            | ((~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__clk)) 
                                                               & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_conv_tile_memory__DOT__clk__0))))));
        vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_conv_tile_memory__DOT__clk__0 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__clk;
    }
    Vtb_s2a_conv_tile_memory___024root___timing_ready(vlSelf);
    Vtb_s2a_conv_tile_memory___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VactTriggered, vlSelfRef.__VactTriggeredAcc);
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vtb_s2a_conv_tile_memory___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
    }
#endif
    Vtb_s2a_conv_tile_memory___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VnbaTriggered, vlSelfRef.__VactTriggered);
    __VactExecute = Vtb_s2a_conv_tile_memory___024root___trigger_anySet__act(vlSelfRef.__VactTriggered);
    if (__VactExecute) {
        vlSelfRef.__VactTriggeredAcc.fill(0ULL);
        Vtb_s2a_conv_tile_memory___024root___timing_resume(vlSelf);
        {
            // Inlined CFunc: _eval_act
            if ((5ULL & vlSelfRef.__VactTriggered[0U])) {
                Vtb_s2a_conv_tile_memory___024root___act_comb__TOP__0(vlSelf);
            }
        }
    }
    return (__VactExecute);
}

bool Vtb_s2a_conv_tile_memory___024root___eval_phase__inact(Vtb_s2a_conv_tile_memory___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___eval_phase__inact\n"); );
    Vtb_s2a_conv_tile_memory__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VinactExecute;
    // Body
    __VinactExecute = vlSelfRef.__VdlySched.awaitingZeroDelay();
    if (__VinactExecute) {
        VL_FATAL_MT("source\\tb_s2a_conv_tile_memory.sv", 3, "", "ZERODLY: Design Verilated with '--no-sched-zero-delay', but #0 delay executed at runtime");
    }
    return (__VinactExecute);
}

void Vtb_s2a_conv_tile_memory___024root___trigger_clear__act(VlUnpacked<QData/*63:0*/, 1> &out) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___trigger_clear__act\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        out[n] = 0ULL;
        n = ((IData)(1U) + n);
    } while ((1U > n));
}

void Vtb_s2a_conv_tile_memory___024root___nba_sequent__TOP__0(Vtb_s2a_conv_tile_memory___024root* vlSelf);
void Vtb_s2a_conv_tile_memory___024root___nba_sequent__TOP__1(Vtb_s2a_conv_tile_memory___024root* vlSelf);
void Vtb_s2a_conv_tile_memory___024root___nba_comb__TOP__0(Vtb_s2a_conv_tile_memory___024root* vlSelf);

bool Vtb_s2a_conv_tile_memory___024root___eval_phase__nba(Vtb_s2a_conv_tile_memory___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___eval_phase__nba\n"); );
    Vtb_s2a_conv_tile_memory__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = Vtb_s2a_conv_tile_memory___024root___trigger_anySet__act(vlSelfRef.__VnbaTriggered);
    if (__VnbaExecute) {
        {
            // Inlined CFunc: _eval_nba
            if ((2ULL & vlSelfRef.__VnbaTriggered[0U])) {
                Vtb_s2a_conv_tile_memory___024root___nba_sequent__TOP__0(vlSelf);
            }
            if ((1ULL & vlSelfRef.__VnbaTriggered[0U])) {
                Vtb_s2a_conv_tile_memory___024root___nba_sequent__TOP__1(vlSelf);
            }
            if ((7ULL & vlSelfRef.__VnbaTriggered[0U])) {
                Vtb_s2a_conv_tile_memory___024root___nba_comb__TOP__0(vlSelf);
            }
            if ((5ULL & vlSelfRef.__VnbaTriggered[0U])) {
                {
                    // Inlined CFunc: _nba_comb__TOP__1
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__cancel 
                        = ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__hard_reset) 
                           | (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__abort));
                }
            }
            if ((7ULL & vlSelfRef.__VnbaTriggered[0U])) {
                {
                    // Inlined CFunc: _nba_comb__TOP__2
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__start_ready 
                        = ((~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__cancel)) 
                           & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)));
                }
            }
        }
        Vtb_s2a_conv_tile_memory___024root___trigger_clear__act(vlSelfRef.__VnbaTriggered);
    }
    return (__VnbaExecute);
}

void Vtb_s2a_conv_tile_memory___024root___eval(Vtb_s2a_conv_tile_memory___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___eval\n"); );
    Vtb_s2a_conv_tile_memory__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VnbaIterCount;
    // Body
    __VnbaIterCount = 0U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VnbaIterCount)))) {
#ifdef VL_DEBUG
            Vtb_s2a_conv_tile_memory___024root___dump_triggers__act(vlSelfRef.__VnbaTriggered, "nba"s);
#endif
            VL_FATAL_MT("source\\tb_s2a_conv_tile_memory.sv", 3, "", "DIDNOTCONVERGE: NBA region did not converge after '--converge-limit' of 10000 tries");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        vlSelfRef.__VinactIterCount = 0U;
        do {
            if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VinactIterCount)))) {
                VL_FATAL_MT("source\\tb_s2a_conv_tile_memory.sv", 3, "", "DIDNOTCONVERGE: Inactive region did not converge after '--converge-limit' of 10000 tries");
            }
            vlSelfRef.__VinactIterCount = ((IData)(1U) 
                                           + vlSelfRef.__VinactIterCount);
            vlSelfRef.__VactIterCount = 0U;
            do {
                if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                    Vtb_s2a_conv_tile_memory___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
#endif
                    VL_FATAL_MT("source\\tb_s2a_conv_tile_memory.sv", 3, "", "DIDNOTCONVERGE: Active region did not converge after '--converge-limit' of 10000 tries");
                }
                vlSelfRef.__VactIterCount = ((IData)(1U) 
                                             + vlSelfRef.__VactIterCount);
                vlSelfRef.__VactPhaseResult = Vtb_s2a_conv_tile_memory___024root___eval_phase__act(vlSelf);
            } while (vlSelfRef.__VactPhaseResult);
            vlSelfRef.__VinactPhaseResult = Vtb_s2a_conv_tile_memory___024root___eval_phase__inact(vlSelf);
        } while (vlSelfRef.__VinactPhaseResult);
        vlSelfRef.__VnbaPhaseResult = Vtb_s2a_conv_tile_memory___024root___eval_phase__nba(vlSelf);
    } while (vlSelfRef.__VnbaPhaseResult);
}

void Vtb_s2a_conv_tile_memory___024root____VbeforeTrig_hb8586161__0(Vtb_s2a_conv_tile_memory___024root* vlSelf, const char* __VeventDescription) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root____VbeforeTrig_hb8586161__0\n"); );
    Vtb_s2a_conv_tile_memory__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlUnpacked<QData/*63:0*/, 1> __VTmp;
    // Body
    __VTmp[0U] = (QData)((IData)(((~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__clk)) 
                                  & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_conv_tile_memory__DOT__clk__0))));
    vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_conv_tile_memory__DOT__clk__0 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__clk;
    if ((1ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_hb8586161__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_hb8586161__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_hb8586161__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_hb8586161__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_hb8586161__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_hb8586161__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_hb8586161__0.ready(__VeventDescription);
    }
    vlSelfRef.__VactTriggeredAcc[0U] = (vlSelfRef.__VactTriggeredAcc[0U] 
                                        | __VTmp[0U]);
}

#ifdef VL_DEBUG
void Vtb_s2a_conv_tile_memory___024root___eval_debug_assertions(Vtb_s2a_conv_tile_memory___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___eval_debug_assertions\n"); );
    Vtb_s2a_conv_tile_memory__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}
#endif  // VL_DEBUG
