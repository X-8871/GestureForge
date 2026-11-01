// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_conv_tile_memory.h for the primary calling header

#include "Vtb_s2a_conv_tile_memory__pch.h"

VlCoroutine Vtb_s2a_conv_tile_memory___024root___eval_initial__TOP__Vtiming__0(Vtb_s2a_conv_tile_memory___024root* vlSelf);
VlCoroutine Vtb_s2a_conv_tile_memory___024root___eval_initial__TOP__Vtiming__1(Vtb_s2a_conv_tile_memory___024root* vlSelf);

void Vtb_s2a_conv_tile_memory___024root___eval_initial(Vtb_s2a_conv_tile_memory___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___eval_initial\n"); );
    Vtb_s2a_conv_tile_memory__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_s2a_conv_tile_memory___024root___eval_initial__TOP__Vtiming__0(vlSelf);
    Vtb_s2a_conv_tile_memory___024root___eval_initial__TOP__Vtiming__1(vlSelf);
}

void Vtb_s2a_conv_tile_memory___024root____VbeforeTrig_hb8586161__0(Vtb_s2a_conv_tile_memory___024root* vlSelf, const char* __VeventDescription);

VlCoroutine Vtb_s2a_conv_tile_memory___024root___eval_initial__TOP__Vtiming__0(Vtb_s2a_conv_tile_memory___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___eval_initial__TOP__Vtiming__0\n"); );
    Vtb_s2a_conv_tile_memory__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT____VlemExpr_0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__fd;
    tb_s2a_conv_tile_memory__DOT__fd = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__unnamedblk1_1__DOT____Vrepeat0;
    tb_s2a_conv_tile_memory__DOT__unnamedblk1_1__DOT____Vrepeat0 = 0;
    IData/*31:0*/ __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value;
    __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v;
    __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
    // Body
    tb_s2a_conv_tile_memory__DOT____VlemExpr_0 = VL_VALUEPLUSARGS_INI(32, "CASES=%d"s, 
                                                                      vlSelfRef.tb_s2a_conv_tile_memory__DOT__required_cases);
    if (VL_UNLIKELY((((! tb_s2a_conv_tile_memory__DOT____VlemExpr_0) 
                      || VL_GTES_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__required_cases))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:134: Assertion failed in %m: \345\277\205\351\241\273\347\273\231\345\256\232cases\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 134, "", false);
    }
    tb_s2a_conv_tile_memory__DOT__fd = VL_FOPEN_NN("cases.bin"s
                                                   , "rb"s);
    ;
    if (VL_UNLIKELY(((0U == tb_s2a_conv_tile_memory__DOT__fd)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:135: Assertion failed in %m: fixture\347\274\272\345\244\261\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 135, "", false);
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__hard_reset = 1U;
    tb_s2a_conv_tile_memory__DOT__unnamedblk1_1__DOT____Vrepeat0 = 2U;
    while (VL_LTS_III(32, 0U, tb_s2a_conv_tile_memory__DOT__unnamedblk1_1__DOT____Vrepeat0)) {
        Vtb_s2a_conv_tile_memory___024root____VbeforeTrig_hb8586161__0(vlSelf, 
                                                                       "@(negedge tb_s2a_conv_tile_memory.clk)");
        co_await vlSelfRef.__VtrigSched_hb8586161__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(negedge tb_s2a_conv_tile_memory.clk)", 
                                                             "source\\tb_s2a_conv_tile_memory.sv", 
                                                             136);
        tb_s2a_conv_tile_memory__DOT__unnamedblk1_1__DOT____Vrepeat0 
            = (tb_s2a_conv_tile_memory__DOT__unnamedblk1_1__DOT____Vrepeat0 
               - (IData)(1U));
    }
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "source\\tb_s2a_conv_tile_memory.sv", 
                                         136);
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__hard_reset = 0U;
    {
        while (true) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT____VlemExpr_1 
                = (tb_s2a_conv_tile_memory__DOT__fd ? feof(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : true);
            if (!((! vlSelfRef.tb_s2a_conv_tile_memory__DOT____VlemExpr_1))) break;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__b 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            if (VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__b)) {
                goto __Vlabel0;
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[0U] 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__b;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 1U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__b 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[0U] 
                = (vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[0U] 
                   | (0x0000ff00U & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__b 
                                     << 8U)));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 2U;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:139: Assertion failed in %m: \346\210\252\346\226\255header\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 139, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__b 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[0U] 
                = (vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[0U] 
                   | (0x00ff0000U & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__b 
                                     << 0x00000010U)));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 3U;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:139: Assertion failed in %m: \346\210\252\346\226\255header\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 139, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__b 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:139: Assertion failed in %m: \346\210\252\346\226\255header\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 139, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[0U] 
                = (vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[0U] 
                   | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__b 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 4U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 1U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[1U] 
                = __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 2U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[2U] 
                = __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 3U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[3U] 
                = __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 4U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[4U] 
                = __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 5U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[5U] 
                = __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 6U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[6U] 
                = __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 7U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[7U] 
                = __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 8U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[8U] 
                = __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 9U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[9U] 
                = __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 0x0000000aU;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[10U] 
                = __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 0x0000000bU;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[11U] 
                = __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 0x0000000cU;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:71: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 71, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[12U] 
                = __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 0x0000000dU;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[0U];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__ordinal 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[1U];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__ty 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[2U];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__tx 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[3U];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__group_base 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[4U];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__th 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[5U];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__tw 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[6U];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__ph 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[7U];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__pw 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[8U];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__ci 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[9U];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__k 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[10U];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__lanes 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[11U];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__outputs 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[12U];
            if (VL_UNLIKELY((((((VL_LTES_III(32, 0x00000026U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id) 
                                 | VL_LTS_III(32, 0x0000c800U, 
                                              VL_MULS_III(32, 
                                                          VL_MULS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__ci, vlSelfRef.tb_s2a_conv_tile_memory__DOT__ph), vlSelfRef.tb_s2a_conv_tile_memory__DOT__pw))) 
                                | VL_LTS_III(32, 0x00009000U, 
                                             VL_MULS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__lanes, vlSelfRef.tb_s2a_conv_tile_memory__DOT__k))) 
                               | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__outputs 
                                  != VL_MULS_III(32, 
                                                 VL_MULS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__lanes, vlSelfRef.tb_s2a_conv_tile_memory__DOT__th), vlSelfRef.tb_s2a_conv_tile_memory__DOT__tw))) 
                              | VL_LTS_III(32, 0x00000200U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__outputs))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:143: Assertion failed in %m: fixture\345\260\272\345\257\270\351\235\236\346\263\225\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 143, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 0U;
            while (VL_LTS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__i, 
                              VL_MULS_III(32, VL_MULS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__ci, vlSelfRef.tb_s2a_conv_tile_memory__DOT__ph), vlSelfRef.tb_s2a_conv_tile_memory__DOT__pw))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__b 
                    = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
                if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__b)))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:144: Assertion failed in %m: \346\210\252\346\226\255patch\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 144, "", false);
                }
                if (VL_LIKELY(((0xc7ffU >= (0x0000ffffU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__i))))) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__patch[(0x0000ffffU 
                                                                   & vlSelfRef.tb_s2a_conv_tile_memory__DOT__i)] 
                        = (0x000000ffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__b);
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__i 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__i);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 0U;
            while (VL_LTS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__i, 
                              VL_MULS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__lanes, vlSelfRef.tb_s2a_conv_tile_memory__DOT__k))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__b 
                    = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
                if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__b)))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:145: Assertion failed in %m: \346\210\252\346\226\255weight\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 145, "", false);
                }
                if (VL_LIKELY(((0x8fffU >= (0x0000ffffU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__i))))) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__weights[(0x0000ffffU 
                                                                     & vlSelfRef.tb_s2a_conv_tile_memory__DOT__i)] 
                        = (0x000000ffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__b);
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__i 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__i);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 0U;
            while (VL_LTS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__i, vlSelfRef.tb_s2a_conv_tile_memory__DOT__outputs)) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__b 
                    = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
                if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__b)))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:146: Assertion failed in %m: \346\210\252\346\226\255golden\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 146, "", false);
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__golden[(0x000001ffU 
                                                                & vlSelfRef.tb_s2a_conv_tile_memory__DOT__i)] 
                    = (0x000000ffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__b);
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__seen[(0x000001ffU 
                                                              & vlSelfRef.tb_s2a_conv_tile_memory__DOT__i)] = 0U;
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__i 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__i);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__seen_count = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__actual_features = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__actual_weights = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__expected_reads = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__counts[0U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__stalls[0U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 1U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__counts[1U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__stalls[1U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 2U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__counts[2U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__stalls[2U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 3U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__py = 0U;
            while (VL_LTS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__py, vlSelfRef.tb_s2a_conv_tile_memory__DOT__ph)) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__px = 0U;
                while (VL_LTS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__px, vlSelfRef.tb_s2a_conv_tile_memory__DOT__pw)) {
                    if (((((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__ty 
                              * ((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_H
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                                  : 0U)) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__py) 
                            >= ((0x25U >= (0x0000003fU 
                                           & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                 ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_TOP
                                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                                 : 0U)) & ((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__ty 
                                              * ((0x25U 
                                                  >= 
                                                  (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_H
                                                 [(0x0000003fU 
                                                   & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                                                  : 0U)) 
                                             + vlSelfRef.tb_s2a_conv_tile_memory__DOT__py) 
                                            - ((0x25U 
                                                >= 
                                                (0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_TOP
                                               [(0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                                                : 0U)) 
                                           < vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_H
                                           [((0x25U 
                                              >= (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                              ? (0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)
                                              : 0U)][0U])) 
                          & (((vlSelfRef.tb_s2a_conv_tile_memory__DOT__tx 
                               * ((0x25U >= (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_W
                                  [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                                   : 0U)) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__px) 
                             >= ((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_LEFT
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                                  : 0U))) & ((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__tx 
                                                * (
                                                   (0x25U 
                                                    >= 
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_W
                                                   [
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                                                    : 0U)) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__px) 
                                              - ((0x25U 
                                                  >= 
                                                  (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_LEFT
                                                 [(0x0000003fU 
                                                   & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                                                  : 0U)) 
                                             < vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_W
                                             [((0x25U 
                                                >= 
                                                (0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                                ? (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)
                                                : 0U)][0U]))) {
                        vlSelfRef.tb_s2a_conv_tile_memory__DOT__expected_reads 
                            = (vlSelfRef.tb_s2a_conv_tile_memory__DOT__expected_reads 
                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__ci);
                    }
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__px 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__px);
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__py 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__py);
            }
            Vtb_s2a_conv_tile_memory___024root____VbeforeTrig_hb8586161__0(vlSelf, 
                                                                           "@(negedge tb_s2a_conv_tile_memory.clk)");
            co_await vlSelfRef.__VtrigSched_hb8586161__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_s2a_conv_tile_memory.clk)", 
                                                                 "source\\tb_s2a_conv_tile_memory.sv", 
                                                                 151);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "source\\tb_s2a_conv_tile_memory.sv", 
                                                 151);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__start_valid = 1U;
            Vtb_s2a_conv_tile_memory___024root____VbeforeTrig_hb8586161__0(vlSelf, 
                                                                           "@(negedge tb_s2a_conv_tile_memory.clk)");
            co_await vlSelfRef.__VtrigSched_hb8586161__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_s2a_conv_tile_memory.clk)", 
                                                                 "source\\tb_s2a_conv_tile_memory.sv", 
                                                                 152);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "source\\tb_s2a_conv_tile_memory.sv", 
                                                 152);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__start_valid = 0U;
            Vtb_s2a_conv_tile_memory___024root____VbeforeTrig_hb8586161__0(vlSelf, 
                                                                           "@(negedge tb_s2a_conv_tile_memory.clk)");
            co_await vlSelfRef.__VtrigSched_hb8586161__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_s2a_conv_tile_memory.clk)", 
                                                                 "source\\tb_s2a_conv_tile_memory.sv", 
                                                                 153);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "source\\tb_s2a_conv_tile_memory.sv", 
                                                 153);
            if (VL_UNLIKELY(((2U != (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:154: Assertion failed in %m: \347\234\237\345\256\236descriptor\350\242\253\346\213\222\347\273\235\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 154, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__ty;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__tx;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__cycles = 0U;
            while ((6U != (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                Vtb_s2a_conv_tile_memory___024root____VbeforeTrig_hb8586161__0(vlSelf, 
                                                                               "@(negedge tb_s2a_conv_tile_memory.clk)");
                co_await vlSelfRef.__VtrigSched_hb8586161__0.trigger(0U, 
                                                                     nullptr, 
                                                                     "@(negedge tb_s2a_conv_tile_memory.clk)", 
                                                                     "source\\tb_s2a_conv_tile_memory.sv", 
                                                                     158);
                co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                     nullptr, 
                                                     "source\\tb_s2a_conv_tile_memory.sv", 
                                                     158);
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__cycles 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__cycles);
                if (VL_UNLIKELY((((0x12U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
                                  | VL_LTS_III(32, 0x000f4240U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__cycles))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:159: Assertion failed in %m: patch\345\212\240\350\275\275\345\244\261\350\264\245/\350\266\205\346\227\266\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 159, "", false);
                }
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__group_base;
            while ((0x11U != (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                Vtb_s2a_conv_tile_memory___024root____VbeforeTrig_hb8586161__0(vlSelf, 
                                                                               "@(negedge tb_s2a_conv_tile_memory.clk)");
                co_await vlSelfRef.__VtrigSched_hb8586161__0.trigger(0U, 
                                                                     nullptr, 
                                                                     "@(negedge tb_s2a_conv_tile_memory.clk)", 
                                                                     "source\\tb_s2a_conv_tile_memory.sv", 
                                                                     163);
                co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                     nullptr, 
                                                     "source\\tb_s2a_conv_tile_memory.sv", 
                                                     163);
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__cycles 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__cycles);
                if (VL_UNLIKELY((((0x12U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
                                  | VL_LTS_III(32, 0x001e8480U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__cycles))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:164: Assertion failed in %m: tile\346\211\247\350\241\214\345\244\261\350\264\245/\350\266\205\346\227\266 error=%0d\n",4, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '#',3,(IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 164, "", false);
                }
            }
            if (VL_UNLIKELY(((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__seen_count 
                                != vlSelfRef.tb_s2a_conv_tile_memory__DOT__outputs) 
                               | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__actual_features 
                                  != vlSelfRef.tb_s2a_conv_tile_memory__DOT__expected_reads)) 
                              | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__actual_weights 
                                 != VL_MULS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__lanes, vlSelfRef.tb_s2a_conv_tile_memory__DOT__k)))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:167: Assertion failed in %m: \344\274\240\350\276\223\350\256\241\346\225\260\344\270\215\345\256\214\346\225\264 got=%0d/%0d/%0d expected=%0d/%0d/%0d\n",9, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__seen_count
                             , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__actual_features
                             , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__actual_weights
                             , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__outputs
                             , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__expected_reads
                             , '~',32,VL_MULS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__lanes, vlSelfRef.tb_s2a_conv_tile_memory__DOT__k));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 167, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 0U;
            while (VL_LTS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__i, vlSelfRef.tb_s2a_conv_tile_memory__DOT__outputs)) {
                if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__seen
                                                  [
                                                  (0x000001ffU 
                                                   & vlSelfRef.tb_s2a_conv_tile_memory__DOT__i)])))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:168: Assertion failed in %m: \347\274\272\350\276\223\345\207\272\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 168, "", false);
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__i 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__i);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__abort = 1U;
            Vtb_s2a_conv_tile_memory___024root____VbeforeTrig_hb8586161__0(vlSelf, 
                                                                           "@(negedge tb_s2a_conv_tile_memory.clk)");
            co_await vlSelfRef.__VtrigSched_hb8586161__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_s2a_conv_tile_memory.clk)", 
                                                                 "source\\tb_s2a_conv_tile_memory.sv", 
                                                                 169);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "source\\tb_s2a_conv_tile_memory.sv", 
                                                 169);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__abort = 0U;
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "source\\tb_s2a_conv_tile_memory.sv", 
                                                 169);
            if (VL_UNLIKELY(((1U & (~ ((~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__cancel)) 
                                       & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)))))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:170: Assertion failed in %m: \345\217\226\346\266\210\346\234\252\346\201\242\345\244\215\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 170, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__case_count 
                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__case_count);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__total_outputs 
                = (vlSelfRef.tb_s2a_conv_tile_memory__DOT__total_outputs 
                   + vlSelfRef.tb_s2a_conv_tile_memory__DOT__outputs);
            VL_WRITEF_NX("CHECKPOINT TILE_MEMORY layer=%0d case=%0d cycles=%0d feature=%0d weight=%0d output=%0d stalls=%0d/%0d/%0d\n",9
                         , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id
                         , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__ordinal
                         , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__cycles
                         , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__actual_features
                         , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__actual_weights
                         , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__outputs
                         , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__stalls[0U]
                         , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__stalls[1U]
                         , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__stalls[2U]);
        }
        __Vlabel0: ;
    }
    if (VL_UNLIKELY(((vlSelfRef.tb_s2a_conv_tile_memory__DOT__case_count 
                      != vlSelfRef.tb_s2a_conv_tile_memory__DOT__required_cases)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:174: Assertion failed in %m: \347\224\250\344\276\213\346\225\260\344\270\215\345\256\214\346\225\264\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 174, "", false);
    }
    VL_WRITEF_NX("PASS TILE_MEMORY cases=%0d outputs=%0d\n",2
                 , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__case_count
                 , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__total_outputs);
    VL_FINISH_MT("source\\tb_s2a_conv_tile_memory.sv", 175, "");
    co_return;
}

VlCoroutine Vtb_s2a_conv_tile_memory___024root___eval_initial__TOP__Vtiming__1(Vtb_s2a_conv_tile_memory___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___eval_initial__TOP__Vtiming__1\n"); );
    Vtb_s2a_conv_tile_memory__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    while (VL_LIKELY(!vlSymsp->_vm_contextp__->gotFinish())) {
        co_await vlSelfRef.__VdlySched.delay(0x0000000000001388ULL, 
                                             nullptr, 
                                             "source\\tb_s2a_conv_tile_memory.sv", 
                                             20);
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__clk 
            = (1U & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__clk)));
    }
    co_return;
}

bool Vtb_s2a_conv_tile_memory___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___trigger_anySet__act\n"); );
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

void Vtb_s2a_conv_tile_memory___024root___act_comb__TOP__0(Vtb_s2a_conv_tile_memory___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___act_comb__TOP__0\n"); );
    Vtb_s2a_conv_tile_memory__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_plane_bytes;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_plane_bytes = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_rem;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_rem = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_offset;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_offset = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_area;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_area = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_y = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_x;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_x = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_y = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_x;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_x = 0;
    CData/*0:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index_wide;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index_wide = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index = 0;
    VlWide<3>/*95:0*/ __Vtemp_1;
    VlWide<3>/*95:0*/ __Vtemp_2;
    VlWide<3>/*95:0*/ __Vtemp_3;
    VlWide<3>/*95:0*/ __Vtemp_4;
    VlWide<3>/*95:0*/ __Vtemp_5;
    VlWide<3>/*95:0*/ __Vtemp_6;
    VlWide<3>/*95:0*/ __Vtemp_7;
    VlWide<3>/*95:0*/ __Vtemp_8;
    VlWide<3>/*95:0*/ __Vtemp_9;
    VlWide<3>/*95:0*/ __Vtemp_10;
    VlWide<3>/*95:0*/ __Vtemp_11;
    VlWide<3>/*95:0*/ __Vtemp_12;
    VlWide<3>/*95:0*/ __Vtemp_13;
    VlWide<3>/*95:0*/ __Vtemp_14;
    VlWide<3>/*95:0*/ __Vtemp_16;
    VlWide<3>/*95:0*/ __Vtemp_17;
    VlWide<3>/*95:0*/ __Vtemp_19;
    VlWide<3>/*95:0*/ __Vtemp_20;
    VlWide<3>/*95:0*/ __Vtemp_21;
    VlWide<3>/*95:0*/ __Vtemp_22;
    VlWide<3>/*95:0*/ __Vtemp_23;
    VlWide<3>/*95:0*/ __Vtemp_24;
    VlWide<3>/*95:0*/ __Vtemp_25;
    VlWide<3>/*95:0*/ __Vtemp_26;
    VlWide<3>/*95:0*/ __Vtemp_27;
    VlWide<3>/*95:0*/ __Vtemp_28;
    VlWide<3>/*95:0*/ __Vtemp_29;
    VlWide<3>/*95:0*/ __Vtemp_30;
    VlWide<3>/*95:0*/ __Vtemp_31;
    VlWide<3>/*95:0*/ __Vtemp_32;
    VlWide<3>/*95:0*/ __Vtemp_34;
    VlWide<3>/*95:0*/ __Vtemp_35;
    VlWide<3>/*95:0*/ __Vtemp_37;
    VlWide<3>/*95:0*/ __Vtemp_38;
    VlWide<3>/*95:0*/ __Vtemp_39;
    VlWide<3>/*95:0*/ __Vtemp_40;
    VlWide<3>/*95:0*/ __Vtemp_41;
    VlWide<3>/*95:0*/ __Vtemp_42;
    VlWide<3>/*95:0*/ __Vtemp_43;
    VlWide<3>/*95:0*/ __Vtemp_44;
    VlWide<3>/*95:0*/ __Vtemp_45;
    VlWide<3>/*95:0*/ __Vtemp_46;
    VlWide<3>/*95:0*/ __Vtemp_47;
    VlWide<3>/*95:0*/ __Vtemp_48;
    VlWide<3>/*95:0*/ __Vtemp_49;
    VlWide<3>/*95:0*/ __Vtemp_50;
    VlWide<3>/*95:0*/ __Vtemp_52;
    VlWide<3>/*95:0*/ __Vtemp_53;
    VlWide<3>/*95:0*/ __Vtemp_55;
    VlWide<3>/*95:0*/ __Vtemp_56;
    VlWide<3>/*95:0*/ __Vtemp_57;
    VlWide<3>/*95:0*/ __Vtemp_58;
    VlWide<3>/*95:0*/ __Vtemp_59;
    VlWide<3>/*95:0*/ __Vtemp_60;
    VlWide<3>/*95:0*/ __Vtemp_61;
    VlWide<3>/*95:0*/ __Vtemp_62;
    VlWide<3>/*95:0*/ __Vtemp_63;
    VlWide<3>/*95:0*/ __Vtemp_64;
    VlWide<3>/*95:0*/ __Vtemp_65;
    VlWide<3>/*95:0*/ __Vtemp_66;
    VlWide<3>/*95:0*/ __Vtemp_67;
    VlWide<3>/*95:0*/ __Vtemp_68;
    VlWide<3>/*95:0*/ __Vtemp_70;
    VlWide<3>/*95:0*/ __Vtemp_71;
    VlWide<3>/*95:0*/ __Vtemp_73;
    VlWide<3>/*95:0*/ __Vtemp_74;
    VlWide<3>/*95:0*/ __Vtemp_75;
    VlWide<3>/*95:0*/ __Vtemp_76;
    VlWide<3>/*95:0*/ __Vtemp_77;
    VlWide<3>/*95:0*/ __Vtemp_78;
    VlWide<3>/*95:0*/ __Vtemp_79;
    VlWide<3>/*95:0*/ __Vtemp_80;
    VlWide<3>/*95:0*/ __Vtemp_81;
    VlWide<3>/*95:0*/ __Vtemp_82;
    VlWide<3>/*95:0*/ __Vtemp_83;
    VlWide<3>/*95:0*/ __Vtemp_84;
    VlWide<3>/*95:0*/ __Vtemp_85;
    VlWide<3>/*95:0*/ __Vtemp_86;
    VlWide<3>/*95:0*/ __Vtemp_88;
    VlWide<3>/*95:0*/ __Vtemp_89;
    VlWide<3>/*95:0*/ __Vtemp_91;
    VlWide<3>/*95:0*/ __Vtemp_92;
    VlWide<3>/*95:0*/ __Vtemp_93;
    VlWide<3>/*95:0*/ __Vtemp_94;
    VlWide<3>/*95:0*/ __Vtemp_95;
    VlWide<3>/*95:0*/ __Vtemp_96;
    VlWide<3>/*95:0*/ __Vtemp_97;
    VlWide<3>/*95:0*/ __Vtemp_98;
    VlWide<3>/*95:0*/ __Vtemp_99;
    VlWide<3>/*95:0*/ __Vtemp_100;
    VlWide<3>/*95:0*/ __Vtemp_101;
    VlWide<3>/*95:0*/ __Vtemp_102;
    VlWide<3>/*95:0*/ __Vtemp_103;
    VlWide<3>/*95:0*/ __Vtemp_104;
    VlWide<3>/*95:0*/ __Vtemp_106;
    VlWide<3>/*95:0*/ __Vtemp_107;
    VlWide<3>/*95:0*/ __Vtemp_109;
    VlWide<3>/*95:0*/ __Vtemp_110;
    VlWide<3>/*95:0*/ __Vtemp_111;
    VlWide<3>/*95:0*/ __Vtemp_112;
    VlWide<3>/*95:0*/ __Vtemp_113;
    VlWide<3>/*95:0*/ __Vtemp_114;
    VlWide<3>/*95:0*/ __Vtemp_115;
    VlWide<3>/*95:0*/ __Vtemp_116;
    VlWide<3>/*95:0*/ __Vtemp_117;
    VlWide<3>/*95:0*/ __Vtemp_118;
    VlWide<3>/*95:0*/ __Vtemp_119;
    VlWide<3>/*95:0*/ __Vtemp_120;
    VlWide<3>/*95:0*/ __Vtemp_121;
    VlWide<3>/*95:0*/ __Vtemp_122;
    VlWide<3>/*95:0*/ __Vtemp_124;
    VlWide<3>/*95:0*/ __Vtemp_125;
    VlWide<3>/*95:0*/ __Vtemp_127;
    VlWide<3>/*95:0*/ __Vtemp_128;
    VlWide<3>/*95:0*/ __Vtemp_129;
    VlWide<3>/*95:0*/ __Vtemp_130;
    VlWide<3>/*95:0*/ __Vtemp_131;
    VlWide<3>/*95:0*/ __Vtemp_132;
    VlWide<3>/*95:0*/ __Vtemp_133;
    VlWide<3>/*95:0*/ __Vtemp_134;
    VlWide<3>/*95:0*/ __Vtemp_135;
    VlWide<3>/*95:0*/ __Vtemp_136;
    VlWide<3>/*95:0*/ __Vtemp_137;
    VlWide<3>/*95:0*/ __Vtemp_138;
    VlWide<3>/*95:0*/ __Vtemp_139;
    VlWide<3>/*95:0*/ __Vtemp_140;
    VlWide<3>/*95:0*/ __Vtemp_142;
    VlWide<3>/*95:0*/ __Vtemp_143;
    // Body
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_valid = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_rstrb = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_wstrb = 0U;
    if ((1U & ((~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__hard_reset)) 
               & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__abort))))) {
        if (((4U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_valid = 1U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_rstrb 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched;
        } else if ((0x0fU == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_valid = 1U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write = 1U;
        }
        if ((1U & (~ ((4U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
                      || (8U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)))))) {
            if ((0x0fU == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_wstrb 
                    = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched;
            }
        }
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__cancel 
        = ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__hard_reset) 
           | (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__abort));
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_source_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_base_latched)) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_offset_latched)) 
              + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index)) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index)))))));
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_byte_offset_wide 
        = ((QData)((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x 
                            + (VL_MODDIV_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width) 
                               & (- (IData)((0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width))))))) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched)) 
              * ((QData)((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y 
                                  + (VL_DIV_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width) 
                                     & (- (IData)((0U 
                                                   != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width))))))) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index)))))));
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[0U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[0U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[0U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[0U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[0U] = 0U;
    if ((0x00000026U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U] 
            = (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                 ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                 : 0U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base);
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])) {
            if ((0U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U]))) {
                    __Vtemp_1[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_1[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_1[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_2[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_2[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_2[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_3[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_3[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_3[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_4[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_4[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_4[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_5[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_5[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_5[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_6[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_6[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_6[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_7[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_7[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_7[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_8[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_8[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_8[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_9[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_9[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_9[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_10[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_10[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_10[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                } else {
                    __Vtemp_1[1U] = 0U;
                    __Vtemp_1[2U] = 0U;
                    __Vtemp_2[0U] = 0U;
                    __Vtemp_2[1U] = 0U;
                    __Vtemp_3[1U] = 0U;
                    __Vtemp_3[2U] = 0U;
                    __Vtemp_4[0U] = 0U;
                    __Vtemp_4[1U] = 0U;
                    __Vtemp_5[1U] = 0U;
                    __Vtemp_6[0U] = 0U;
                    __Vtemp_7[1U] = 0U;
                    __Vtemp_7[2U] = 0U;
                    __Vtemp_8[0U] = 0U;
                    __Vtemp_8[1U] = 0U;
                    __Vtemp_9[1U] = 0U;
                    __Vtemp_10[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_1[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_1[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_2[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_2[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_3[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_3[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_4[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_4[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_5[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_6[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_7[2U] << 0x00000010U) 
                             | (__Vtemp_7[1U] >> 0x00000010U)) 
                            != ((__Vtemp_8[1U] << 0x00000018U) 
                                | (__Vtemp_8[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_9[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_10[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[0U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U]))) {
                    __Vtemp_11[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_11[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_11[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_12[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_12[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_12[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                } else {
                    __Vtemp_11[0U] = 0U;
                    __Vtemp_11[1U] = 0U;
                    __Vtemp_12[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[0U] 
                    = ((__Vtemp_11[1U] << 0x00000018U) 
                       | (__Vtemp_11[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[0U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[0U]));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[0U] 
                    = (0x000000ffU & __Vtemp_12[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U]))) {
                    __Vtemp_13[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_13[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_13[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_14[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_14[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_14[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                } else {
                    __Vtemp_13[1U] = 0U;
                    __Vtemp_13[2U] = 0U;
                    __Vtemp_14[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[0U] 
                    = ((__Vtemp_13[2U] << 0x00000010U) 
                       | (__Vtemp_13[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[0U] 
                    = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[0U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[0U] 
                    = (0x000000ffU & (__Vtemp_14[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[0U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[0U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[0U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[0U])) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[0U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[0U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[0U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[0U] 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[0U]), vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[0U]);
            __Vtemp_16[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[0U]);
            __Vtemp_16[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[0U] 
                                      >> 0x00000020U));
            __Vtemp_16[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_17, __Vtemp_16);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[0U] 
                = ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[0U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_17[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_17[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[0U]);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[0U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[0U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[0U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[0U]))));
        } else if ((0U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U] 
            = ((IData)(1U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])) {
            if ((1U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U]))) {
                    __Vtemp_19[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_19[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_19[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_20[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_20[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_20[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_21[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_21[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_21[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_22[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_22[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_22[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_23[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_23[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_23[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_24[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_24[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_24[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_25[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_25[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_25[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_26[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_26[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_26[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_27[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_27[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_27[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_28[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_28[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_28[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                } else {
                    __Vtemp_19[1U] = 0U;
                    __Vtemp_19[2U] = 0U;
                    __Vtemp_20[0U] = 0U;
                    __Vtemp_20[1U] = 0U;
                    __Vtemp_21[1U] = 0U;
                    __Vtemp_21[2U] = 0U;
                    __Vtemp_22[0U] = 0U;
                    __Vtemp_22[1U] = 0U;
                    __Vtemp_23[1U] = 0U;
                    __Vtemp_24[0U] = 0U;
                    __Vtemp_25[1U] = 0U;
                    __Vtemp_25[2U] = 0U;
                    __Vtemp_26[0U] = 0U;
                    __Vtemp_26[1U] = 0U;
                    __Vtemp_27[1U] = 0U;
                    __Vtemp_28[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_19[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_19[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_20[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_20[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_21[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_21[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_22[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_22[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_23[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_24[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_25[2U] << 0x00000010U) 
                             | (__Vtemp_25[1U] >> 0x00000010U)) 
                            != ((__Vtemp_26[1U] << 0x00000018U) 
                                | (__Vtemp_26[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_27[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_28[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[1U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U]))) {
                    __Vtemp_29[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_29[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_29[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_30[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_30[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_30[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                } else {
                    __Vtemp_29[0U] = 0U;
                    __Vtemp_29[1U] = 0U;
                    __Vtemp_30[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[1U] 
                    = ((__Vtemp_29[1U] << 0x00000018U) 
                       | (__Vtemp_29[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[1U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[1U]));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[1U] 
                    = (0x000000ffU & __Vtemp_30[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U]))) {
                    __Vtemp_31[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_31[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_31[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_32[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_32[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_32[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                } else {
                    __Vtemp_31[1U] = 0U;
                    __Vtemp_31[2U] = 0U;
                    __Vtemp_32[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[1U] 
                    = ((__Vtemp_31[2U] << 0x00000010U) 
                       | (__Vtemp_31[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[1U] 
                    = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[1U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[1U] 
                    = (0x000000ffU & (__Vtemp_32[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[1U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[1U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[1U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[1U])) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[1U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[1U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[1U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[1U] 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[1U]), vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[1U]);
            __Vtemp_34[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[1U]);
            __Vtemp_34[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[1U] 
                                      >> 0x00000020U));
            __Vtemp_34[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_35, __Vtemp_34);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[1U] 
                = ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[1U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_35[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_35[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[1U]);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[1U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[1U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[1U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[1U]))));
        } else if ((1U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U] 
            = ((IData)(2U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])) {
            if ((2U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U]))) {
                    __Vtemp_37[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_37[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_37[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_38[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_38[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_38[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_39[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_39[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_39[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_40[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_40[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_40[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_41[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_41[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_41[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_42[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_42[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_42[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_43[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_43[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_43[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_44[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_44[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_44[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_45[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_45[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_45[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_46[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_46[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_46[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                } else {
                    __Vtemp_37[1U] = 0U;
                    __Vtemp_37[2U] = 0U;
                    __Vtemp_38[0U] = 0U;
                    __Vtemp_38[1U] = 0U;
                    __Vtemp_39[1U] = 0U;
                    __Vtemp_39[2U] = 0U;
                    __Vtemp_40[0U] = 0U;
                    __Vtemp_40[1U] = 0U;
                    __Vtemp_41[1U] = 0U;
                    __Vtemp_42[0U] = 0U;
                    __Vtemp_43[1U] = 0U;
                    __Vtemp_43[2U] = 0U;
                    __Vtemp_44[0U] = 0U;
                    __Vtemp_44[1U] = 0U;
                    __Vtemp_45[1U] = 0U;
                    __Vtemp_46[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_37[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_37[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_38[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_38[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_39[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_39[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_40[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_40[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_41[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_42[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_43[2U] << 0x00000010U) 
                             | (__Vtemp_43[1U] >> 0x00000010U)) 
                            != ((__Vtemp_44[1U] << 0x00000018U) 
                                | (__Vtemp_44[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_45[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_46[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[2U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U]))) {
                    __Vtemp_47[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_47[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_47[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_48[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_48[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_48[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                } else {
                    __Vtemp_47[0U] = 0U;
                    __Vtemp_47[1U] = 0U;
                    __Vtemp_48[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[2U] 
                    = ((__Vtemp_47[1U] << 0x00000018U) 
                       | (__Vtemp_47[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[2U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[2U]));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[2U] 
                    = (0x000000ffU & __Vtemp_48[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U]))) {
                    __Vtemp_49[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_49[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_49[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_50[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_50[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_50[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                } else {
                    __Vtemp_49[1U] = 0U;
                    __Vtemp_49[2U] = 0U;
                    __Vtemp_50[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[2U] 
                    = ((__Vtemp_49[2U] << 0x00000010U) 
                       | (__Vtemp_49[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[2U] 
                    = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[2U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[2U] 
                    = (0x000000ffU & (__Vtemp_50[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[2U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[2U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[2U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[2U])) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[2U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[2U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[2U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[2U] 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[2U]), vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[2U]);
            __Vtemp_52[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[2U]);
            __Vtemp_52[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[2U] 
                                      >> 0x00000020U));
            __Vtemp_52[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_53, __Vtemp_52);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[2U] 
                = ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[2U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_53[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_53[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[2U]);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[2U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[2U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[2U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[2U]))));
        } else if ((2U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U] 
            = ((IData)(3U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])) {
            if ((3U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U]))) {
                    __Vtemp_55[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_55[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_55[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_56[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_56[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_56[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_57[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_57[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_57[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_58[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_58[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_58[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_59[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_59[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_59[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_60[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_60[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_60[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_61[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_61[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_61[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_62[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_62[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_62[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_63[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_63[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_63[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_64[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_64[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_64[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                } else {
                    __Vtemp_55[1U] = 0U;
                    __Vtemp_55[2U] = 0U;
                    __Vtemp_56[0U] = 0U;
                    __Vtemp_56[1U] = 0U;
                    __Vtemp_57[1U] = 0U;
                    __Vtemp_57[2U] = 0U;
                    __Vtemp_58[0U] = 0U;
                    __Vtemp_58[1U] = 0U;
                    __Vtemp_59[1U] = 0U;
                    __Vtemp_60[0U] = 0U;
                    __Vtemp_61[1U] = 0U;
                    __Vtemp_61[2U] = 0U;
                    __Vtemp_62[0U] = 0U;
                    __Vtemp_62[1U] = 0U;
                    __Vtemp_63[1U] = 0U;
                    __Vtemp_64[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_55[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_55[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_56[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_56[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_57[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_57[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_58[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_58[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_59[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_60[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_61[2U] << 0x00000010U) 
                             | (__Vtemp_61[1U] >> 0x00000010U)) 
                            != ((__Vtemp_62[1U] << 0x00000018U) 
                                | (__Vtemp_62[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_63[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_64[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[3U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U]))) {
                    __Vtemp_65[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_65[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_65[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_66[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_66[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_66[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                } else {
                    __Vtemp_65[0U] = 0U;
                    __Vtemp_65[1U] = 0U;
                    __Vtemp_66[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[3U] 
                    = ((__Vtemp_65[1U] << 0x00000018U) 
                       | (__Vtemp_65[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[3U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[3U]));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[3U] 
                    = (0x000000ffU & __Vtemp_66[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U]))) {
                    __Vtemp_67[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_67[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_67[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_68[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_68[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_68[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                } else {
                    __Vtemp_67[1U] = 0U;
                    __Vtemp_67[2U] = 0U;
                    __Vtemp_68[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[3U] 
                    = ((__Vtemp_67[2U] << 0x00000010U) 
                       | (__Vtemp_67[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[3U] 
                    = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[3U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[3U] 
                    = (0x000000ffU & (__Vtemp_68[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[3U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[3U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[3U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[3U])) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[3U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[3U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[3U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[3U] 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[3U]), vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[3U]);
            __Vtemp_70[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[3U]);
            __Vtemp_70[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[3U] 
                                      >> 0x00000020U));
            __Vtemp_70[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_71, __Vtemp_70);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[3U] 
                = ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[3U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_71[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_71[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[3U]);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[3U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[3U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[3U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[3U]))));
        } else if ((3U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U] 
            = ((IData)(4U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])) {
            if ((4U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U]))) {
                    __Vtemp_73[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_73[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_73[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_74[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_74[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_74[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_75[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_75[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_75[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_76[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_76[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_76[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_77[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_77[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_77[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_78[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_78[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_78[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_79[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_79[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_79[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_80[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_80[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_80[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_81[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_81[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_81[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_82[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_82[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_82[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                } else {
                    __Vtemp_73[1U] = 0U;
                    __Vtemp_73[2U] = 0U;
                    __Vtemp_74[0U] = 0U;
                    __Vtemp_74[1U] = 0U;
                    __Vtemp_75[1U] = 0U;
                    __Vtemp_75[2U] = 0U;
                    __Vtemp_76[0U] = 0U;
                    __Vtemp_76[1U] = 0U;
                    __Vtemp_77[1U] = 0U;
                    __Vtemp_78[0U] = 0U;
                    __Vtemp_79[1U] = 0U;
                    __Vtemp_79[2U] = 0U;
                    __Vtemp_80[0U] = 0U;
                    __Vtemp_80[1U] = 0U;
                    __Vtemp_81[1U] = 0U;
                    __Vtemp_82[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_73[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_73[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_74[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_74[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_75[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_75[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_76[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_76[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_77[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_78[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_79[2U] << 0x00000010U) 
                             | (__Vtemp_79[1U] >> 0x00000010U)) 
                            != ((__Vtemp_80[1U] << 0x00000018U) 
                                | (__Vtemp_80[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_81[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_82[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[4U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U]))) {
                    __Vtemp_83[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_83[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_83[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_84[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_84[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_84[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                } else {
                    __Vtemp_83[0U] = 0U;
                    __Vtemp_83[1U] = 0U;
                    __Vtemp_84[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[4U] 
                    = ((__Vtemp_83[1U] << 0x00000018U) 
                       | (__Vtemp_83[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[4U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[4U]));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[4U] 
                    = (0x000000ffU & __Vtemp_84[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U]))) {
                    __Vtemp_85[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_85[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_85[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_86[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_86[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_86[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                } else {
                    __Vtemp_85[1U] = 0U;
                    __Vtemp_85[2U] = 0U;
                    __Vtemp_86[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[4U] 
                    = ((__Vtemp_85[2U] << 0x00000010U) 
                       | (__Vtemp_85[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[4U] 
                    = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[4U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[4U] 
                    = (0x000000ffU & (__Vtemp_86[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[4U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[4U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[4U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[4U])) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[4U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[4U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[4U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[4U] 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[4U]), vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[4U]);
            __Vtemp_88[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[4U]);
            __Vtemp_88[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[4U] 
                                      >> 0x00000020U));
            __Vtemp_88[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_89, __Vtemp_88);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[4U] 
                = ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[4U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_89[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_89[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[4U]);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[4U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[4U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[4U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[4U]))));
        } else if ((4U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U] 
            = ((IData)(5U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])) {
            if ((5U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U]))) {
                    __Vtemp_91[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_91[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_91[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_92[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_92[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_92[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_93[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_93[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_93[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_94[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_94[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_94[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_95[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_95[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_95[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_96[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_96[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_96[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_97[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_97[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_97[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_98[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_98[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_98[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_99[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_99[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_99[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_100[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_100[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_100[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                } else {
                    __Vtemp_91[1U] = 0U;
                    __Vtemp_91[2U] = 0U;
                    __Vtemp_92[0U] = 0U;
                    __Vtemp_92[1U] = 0U;
                    __Vtemp_93[1U] = 0U;
                    __Vtemp_93[2U] = 0U;
                    __Vtemp_94[0U] = 0U;
                    __Vtemp_94[1U] = 0U;
                    __Vtemp_95[1U] = 0U;
                    __Vtemp_96[0U] = 0U;
                    __Vtemp_97[1U] = 0U;
                    __Vtemp_97[2U] = 0U;
                    __Vtemp_98[0U] = 0U;
                    __Vtemp_98[1U] = 0U;
                    __Vtemp_99[1U] = 0U;
                    __Vtemp_100[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_91[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_91[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_92[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_92[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_93[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_93[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_94[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_94[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_95[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_96[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_97[2U] << 0x00000010U) 
                             | (__Vtemp_97[1U] >> 0x00000010U)) 
                            != ((__Vtemp_98[1U] << 0x00000018U) 
                                | (__Vtemp_98[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_99[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_100[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[5U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U]))) {
                    __Vtemp_101[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_101[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_101[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_102[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_102[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_102[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                } else {
                    __Vtemp_101[0U] = 0U;
                    __Vtemp_101[1U] = 0U;
                    __Vtemp_102[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[5U] 
                    = ((__Vtemp_101[1U] << 0x00000018U) 
                       | (__Vtemp_101[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[5U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[5U]));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[5U] 
                    = (0x000000ffU & __Vtemp_102[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U]))) {
                    __Vtemp_103[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_103[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_103[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_104[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_104[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_104[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                } else {
                    __Vtemp_103[1U] = 0U;
                    __Vtemp_103[2U] = 0U;
                    __Vtemp_104[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[5U] 
                    = ((__Vtemp_103[2U] << 0x00000010U) 
                       | (__Vtemp_103[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[5U] 
                    = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[5U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[5U] 
                    = (0x000000ffU & (__Vtemp_104[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[5U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[5U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[5U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[5U])) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[5U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[5U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[5U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[5U] 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[5U]), vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[5U]);
            __Vtemp_106[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[5U]);
            __Vtemp_106[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[5U] 
                                       >> 0x00000020U));
            __Vtemp_106[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_107, __Vtemp_106);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[5U] 
                = ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[5U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_107[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_107[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[5U]);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[5U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[5U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[5U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[5U]))));
        } else if ((5U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U] 
            = ((IData)(6U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])) {
            if ((6U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U]))) {
                    __Vtemp_109[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_109[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_109[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_110[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_110[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_110[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_111[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_111[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_111[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_112[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_112[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_112[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_113[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_113[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_113[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_114[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_114[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_114[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_115[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_115[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_115[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_116[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_116[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_116[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_117[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_117[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_117[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_118[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_118[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_118[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                } else {
                    __Vtemp_109[1U] = 0U;
                    __Vtemp_109[2U] = 0U;
                    __Vtemp_110[0U] = 0U;
                    __Vtemp_110[1U] = 0U;
                    __Vtemp_111[1U] = 0U;
                    __Vtemp_111[2U] = 0U;
                    __Vtemp_112[0U] = 0U;
                    __Vtemp_112[1U] = 0U;
                    __Vtemp_113[1U] = 0U;
                    __Vtemp_114[0U] = 0U;
                    __Vtemp_115[1U] = 0U;
                    __Vtemp_115[2U] = 0U;
                    __Vtemp_116[0U] = 0U;
                    __Vtemp_116[1U] = 0U;
                    __Vtemp_117[1U] = 0U;
                    __Vtemp_118[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_109[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_109[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_110[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_110[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_111[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_111[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_112[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_112[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_113[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_114[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_115[2U] << 0x00000010U) 
                             | (__Vtemp_115[1U] >> 0x00000010U)) 
                            != ((__Vtemp_116[1U] << 0x00000018U) 
                                | (__Vtemp_116[0U] 
                                   >> 8U))) | ((0x000000ffU 
                                                & (__Vtemp_117[1U] 
                                                   >> 8U)) 
                                               != (0x000000ffU 
                                                   & __Vtemp_118[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[6U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U]))) {
                    __Vtemp_119[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_119[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_119[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_120[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_120[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_120[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                } else {
                    __Vtemp_119[0U] = 0U;
                    __Vtemp_119[1U] = 0U;
                    __Vtemp_120[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[6U] 
                    = ((__Vtemp_119[1U] << 0x00000018U) 
                       | (__Vtemp_119[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[6U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[6U]));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[6U] 
                    = (0x000000ffU & __Vtemp_120[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U]))) {
                    __Vtemp_121[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_121[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_121[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_122[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_122[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_122[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                } else {
                    __Vtemp_121[1U] = 0U;
                    __Vtemp_121[2U] = 0U;
                    __Vtemp_122[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[6U] 
                    = ((__Vtemp_121[2U] << 0x00000010U) 
                       | (__Vtemp_121[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[6U] 
                    = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[6U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[6U] 
                    = (0x000000ffU & (__Vtemp_122[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[6U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[6U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[6U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[6U])) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[6U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[6U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[6U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[6U] 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[6U]), vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[6U]);
            __Vtemp_124[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[6U]);
            __Vtemp_124[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[6U] 
                                       >> 0x00000020U));
            __Vtemp_124[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_125, __Vtemp_124);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[6U] 
                = ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[6U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_125[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_125[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[6U]);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[6U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[6U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[6U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[6U]))));
        } else if ((6U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U] 
            = ((IData)(7U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])) {
            if ((7U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U]))) {
                    __Vtemp_127[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_127[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_127[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_128[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_128[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_128[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_129[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_129[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_129[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_130[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_130[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_130[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_131[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_131[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_131[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_132[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_132[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_132[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_133[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_133[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_133[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_134[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_134[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_134[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_135[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_135[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_135[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_136[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_136[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_136[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                } else {
                    __Vtemp_127[1U] = 0U;
                    __Vtemp_127[2U] = 0U;
                    __Vtemp_128[0U] = 0U;
                    __Vtemp_128[1U] = 0U;
                    __Vtemp_129[1U] = 0U;
                    __Vtemp_129[2U] = 0U;
                    __Vtemp_130[0U] = 0U;
                    __Vtemp_130[1U] = 0U;
                    __Vtemp_131[1U] = 0U;
                    __Vtemp_132[0U] = 0U;
                    __Vtemp_133[1U] = 0U;
                    __Vtemp_133[2U] = 0U;
                    __Vtemp_134[0U] = 0U;
                    __Vtemp_134[1U] = 0U;
                    __Vtemp_135[1U] = 0U;
                    __Vtemp_136[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_127[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_127[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_128[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_128[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_129[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_129[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_130[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_130[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_131[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_132[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_133[2U] << 0x00000010U) 
                             | (__Vtemp_133[1U] >> 0x00000010U)) 
                            != ((__Vtemp_134[1U] << 0x00000018U) 
                                | (__Vtemp_134[0U] 
                                   >> 8U))) | ((0x000000ffU 
                                                & (__Vtemp_135[1U] 
                                                   >> 8U)) 
                                               != (0x000000ffU 
                                                   & __Vtemp_136[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[7U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U]))) {
                    __Vtemp_137[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_137[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_137[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_138[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_138[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_138[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                } else {
                    __Vtemp_137[0U] = 0U;
                    __Vtemp_137[1U] = 0U;
                    __Vtemp_138[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[7U] 
                    = ((__Vtemp_137[1U] << 0x00000018U) 
                       | (__Vtemp_137[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[7U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[7U]));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[7U] 
                    = (0x000000ffU & __Vtemp_138[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U]))) {
                    __Vtemp_139[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_139[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_139[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_140[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_140[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_140[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                } else {
                    __Vtemp_139[1U] = 0U;
                    __Vtemp_139[2U] = 0U;
                    __Vtemp_140[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[7U] 
                    = ((__Vtemp_139[2U] << 0x00000010U) 
                       | (__Vtemp_139[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[7U] 
                    = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[7U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[7U] 
                    = (0x000000ffU & (__Vtemp_140[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[7U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[7U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[7U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[7U])) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[7U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[7U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[7U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[7U] 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[7U]), vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[7U]);
            __Vtemp_142[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[7U]);
            __Vtemp_142[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[7U] 
                                       >> 0x00000020U));
            __Vtemp_142[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_143, __Vtemp_142);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[7U] 
                = ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[7U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_143[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_143[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[7U]);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[7U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[7U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[7U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[7U]))));
        } else if ((7U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
    } else {
        if ((0U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[1U] = 0U;
        if ((1U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[2U] = 0U;
        if ((2U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[3U] = 0U;
        if ((3U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[4U] = 0U;
        if ((4U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[5U] = 0U;
        if ((5U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[6U] = 0U;
        if ((6U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[7U] = 0U;
        if ((7U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
    }
    tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_plane_bytes 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_height)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width)));
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_rem = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y = 0ULL;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_in_bounds = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_offset = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_address_wide = 0ULL;
    if (((0ULL != tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_plane_bytes) 
         & (0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width))) {
        tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel 
            = (IData)(VL_DIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index)), tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_plane_bytes));
        tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_rem 
            = (IData)(VL_MODDIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index)), tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_plane_bytes));
        tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y 
            = VL_DIV_III(32, tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_rem, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width);
        tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x 
            = VL_MODDIV_III(32, tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_rem, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width);
        tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched))) 
                + (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_top_latched)));
        tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched))) 
                + (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_width_latched))));
        if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_in_bounds) {
            tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_offset 
                = (((((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_height_latched))) 
                     + tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_width_latched))) 
                   + tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_address_wide 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_base_latched)) 
                   + tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_offset);
        }
    }
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_area 
        = (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched 
           * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched);
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_y = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_x = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_y = 0ULL;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_x = 0ULL;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index_wide = 0ULL;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[0U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[1U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[2U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[3U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[3U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[3U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[3U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[4U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[4U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[4U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[4U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[5U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[5U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[5U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[5U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[6U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[6U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[6U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[6U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[7U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[7U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[7U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[7U] = 0ULL;
    if (((0U != tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_area) 
         & (0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width))) {
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel 
            = VL_DIV_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index, tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_area);
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y 
            = VL_DIV_III(32, VL_MODDIV_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index, tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_area), vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched);
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x 
            = VL_MODDIV_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched);
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_y 
            = VL_DIV_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width);
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_x 
            = VL_MODDIV_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width);
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_y 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched))) 
                 + ((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_y)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched)))) 
                + (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_top_latched)));
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_x 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched))) 
                 + ((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_x)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched)))) 
                + (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_left_latched)));
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_y, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_x, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_width_latched))));
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index_wide 
            = (((((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel)) 
                  * tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_plane_bytes) 
                 + ((((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_y)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched))) 
                     + (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y))) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width)))) 
                + ((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_x)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched)))) 
               + (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x)));
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index 
            = (IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index_wide);
        if ((0U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[0U] 
                = ((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[0U] 
                = ((0x8fffU >= (0x0000ffffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index)]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[0U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[0U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[0U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[0U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[0U])));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[0U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[0U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[0U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[0U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[0U])))));
            if (((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[0U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[0U])))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[0U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[0U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[0U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[0U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[0U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[0U] = 0ULL;
        }
        if ((1U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[1U] 
                = ((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[1U] 
                = ((0x8fffU >= (0x0000ffffU & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched 
                                    + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[1U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[1U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[1U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[1U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[1U])));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[1U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[1U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[1U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[1U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[1U])))));
            if (((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[1U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[1U])))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[1U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[1U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[1U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[1U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[1U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[1U] = 0ULL;
        }
        if ((2U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[2U] 
                = ((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[2U] 
                = ((0x8fffU >= (0x0000ffffU & ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched 
                                                << 1U) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched 
                                     << 1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[2U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[2U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[2U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[2U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[2U])));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[2U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[2U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[2U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[2U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[2U])))));
            if (((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[2U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[2U])))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[2U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[2U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[2U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[2U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[2U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[2U] = 0ULL;
        }
        if ((3U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[3U] 
                = ((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[3U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(3U) 
                                                * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & (((IData)(3U) * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[3U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[3U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[3U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[3U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[3U])));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[3U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[3U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[3U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[3U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[3U])))));
            if (((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[3U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[3U])))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[3U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[3U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[3U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[3U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[3U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[3U] = 0ULL;
        }
        if ((4U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[4U] 
                = ((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[4U] 
                = ((0x8fffU >= (0x0000ffffU & ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched 
                                                << 2U) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched 
                                     << 2U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[4U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[4U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[4U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[4U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[4U])));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[4U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[4U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[4U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[4U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[4U])))));
            if (((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[4U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[4U])))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[4U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[4U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[4U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[4U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[4U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[4U] = 0ULL;
        }
        if ((5U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[5U] 
                = ((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[5U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(5U) 
                                                * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & (((IData)(5U) * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[5U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[5U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[5U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[5U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[5U])));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[5U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[5U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[5U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[5U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[5U])))));
            if (((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[5U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[5U])))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[5U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[5U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[5U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[5U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[5U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[5U] = 0ULL;
        }
        if ((6U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[6U] 
                = ((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[6U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(6U) 
                                                * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & (((IData)(6U) * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[6U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[6U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[6U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[6U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[6U])));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[6U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[6U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[6U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[6U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[6U])))));
            if (((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[6U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[6U])))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[6U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[6U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[6U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[6U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[6U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[6U] = 0ULL;
        }
        if ((7U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[7U] 
                = ((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[7U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(7U) 
                                                * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & (((IData)(7U) * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[7U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[7U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[7U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[7U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[7U])));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[7U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[7U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[7U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[7U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[7U])))));
            if (((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[7U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[7U])))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[7U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[7U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[7U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[7U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[7U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[7U] = 0ULL;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__cancel)) 
           & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)));
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_base_latched)) 
           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_byte_offset_wide);
}

void Vtb_s2a_conv_tile_memory___024root___nba_sequent__TOP__0(Vtb_s2a_conv_tile_memory___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___nba_sequent__TOP__0\n"); );
    Vtb_s2a_conv_tile_memory__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__input_elements_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_memory__DOT__dut__DOT__input_elements_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__expected_weight_bytes_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_memory__DOT__dut__DOT__expected_weight_bytes_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__input_end_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_memory__DOT__dut__DOT__input_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__output_end_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_memory__DOT__dut__DOT__output_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_end_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_end_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_end_wide);
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_numerator;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_numerator = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_numerator;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_numerator = 0;
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_height_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_height_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_width_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_width_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_bytes_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_bytes_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__full_weight_group_bytes_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_weight_group_bytes_wide);
    CData/*4:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base = 0;
    IData/*31:0*/ __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base;
    __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y = 0;
    IData/*31:0*/ __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y;
    __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x = 0;
    IData/*31:0*/ __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x;
    __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_height;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_height = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_byte_count;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_byte_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_point_count;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_point_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v1;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v1 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v1;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v1;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v1 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v2;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v2 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v2;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v2 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v2;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v2 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v3;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v3 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v3;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v3 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v3;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v3 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v4;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v4 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v4;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v4 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v4;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v4 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v5;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v5 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v5;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v5 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v5;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v5 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v6;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v6 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v6;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v6 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v6;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v6 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v7;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v7 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v7;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v7 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v7;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v7 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v0;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v0;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v0 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v1;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v1;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v1 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v2;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v2 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v2;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v2 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v3;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v3 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v3;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v3 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v4;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v4 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v4;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v4 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v5;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v5 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v5;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v5 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v6;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v6 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v6;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v6 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v7;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v7 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v7;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v7 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v8;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v8 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v8;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v8 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v9;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v9 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v9;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v9 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v10;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v10 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v11;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v11 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v12;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v12 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v13;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v13 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v14;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v14 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v15;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v15 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v16;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v16 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v16;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v16 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v17;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v17 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v17;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v17 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v18;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v18 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v19;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v19 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v20;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v20 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v21;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v21 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v22;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v22 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v23;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v23 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group__v0;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group__v0 = 0;
    SData/*15:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group__v0;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group__v0;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group__v0 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v0;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v0 = 0;
    SData/*15:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v0;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v0;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v0 = 0;
    SData/*15:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v1;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v1;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v1 = 0;
    VlWide<4>/*127:0*/ __Vtemp_2;
    VlWide<4>/*127:0*/ __Vtemp_3;
    VlWide<4>/*127:0*/ __Vtemp_4;
    VlWide<4>/*127:0*/ __Vtemp_5;
    VlWide<4>/*127:0*/ __Vtemp_6;
    VlWide<4>/*127:0*/ __Vtemp_7;
    VlWide<4>/*127:0*/ __Vtemp_8;
    VlWide<4>/*127:0*/ __Vtemp_9;
    VlWide<4>/*127:0*/ __Vtemp_10;
    VlWide<4>/*127:0*/ __Vtemp_11;
    VlWide<4>/*127:0*/ __Vtemp_12;
    VlWide<4>/*127:0*/ __Vtemp_13;
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
    VlWide<4>/*127:0*/ __Vtemp_55;
    VlWide<4>/*127:0*/ __Vtemp_56;
    VlWide<4>/*127:0*/ __Vtemp_57;
    VlWide<4>/*127:0*/ __Vtemp_58;
    // Body
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_height 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_height;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_byte_count 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_byte_count;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_point_count 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_point_count;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v1 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v2 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v3 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v4 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v5 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v6 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v7 = 0U;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group__v0 = 0U;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v1 = 0U;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v1 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v2 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v3 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v4 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v5 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v6 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v7 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v8 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v9 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v16 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v17 = 0U;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched;
    if (((((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_valid) 
           & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_ready)) 
          & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__hard_reset))) 
         & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__abort)))) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__selected_lane = 0xffffffffU;
        if ((2U >= (3U & vlSelfRef.tb_s2a_conv_tile_memory__DOT__cls))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__counts[(3U 
                                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__cls)] 
                = ((IData)(1U) + ((2U >= (3U & vlSelfRef.tb_s2a_conv_tile_memory__DOT__cls))
                                   ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__counts
                                  [(3U & vlSelfRef.tb_s2a_conv_tile_memory__DOT__cls)]
                                   : 0U));
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__wait_remaining = 0xffffffffU;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__pending_response = 1U;
        if ((1U == ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write)
                     ? (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_wstrb)
                     : (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_rstrb)))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__selected_lane = 0U;
        }
        if ((2U == ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write)
                     ? (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_wstrb)
                     : (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_rstrb)))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__selected_lane = 1U;
        }
        if ((4U == ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write)
                     ? (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_wstrb)
                     : (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_rstrb)))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__selected_lane = 2U;
        }
        if ((8U == ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write)
                     ? (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_wstrb)
                     : (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_rstrb)))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__selected_lane = 3U;
        }
        if (VL_UNLIKELY(((((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__selected_lane) 
                            | (0U != (3U & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_address_latched))) 
                           | ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write) 
                              & (0U != (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_rstrb)))) 
                          | ((~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write)) 
                             & (0U != (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_wstrb))))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:102: Assertion failed in %m: \351\235\236\346\263\225word/strobe\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 102, "", false);
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__address 
            = (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_address_latched 
               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__selected_lane);
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_data = 0U;
        if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__idx 
                = (vlSelfRef.tb_s2a_conv_tile_memory__DOT__address 
                   - ((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                       ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                      [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                       : 0U));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__oc 
                = VL_DIV_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__idx, 
                             (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_H
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                                : 0U) * ((0x25U >= 
                                          (0x0000003fU 
                                           & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                          ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
                                         [(0x0000003fU 
                                           & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                                          : 0U)));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__seen_count 
                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__seen_count);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__y 
                = VL_MODDIV_III(32, VL_DIV_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__idx, 
                                               ((0x25U 
                                                 >= 
                                                 (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                                 ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
                                                [(0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                                                 : 0U)), 
                                ((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_H
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                                  : 0U));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__x 
                = VL_MODDIV_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__idx, 
                                ((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                                  : 0U));
            if (VL_UNLIKELY(((((((VL_LTS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__oc, vlSelfRef.tb_s2a_conv_tile_memory__DOT__group_base) 
                                  | VL_GTES_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__oc, 
                                                (vlSelfRef.tb_s2a_conv_tile_memory__DOT__group_base 
                                                 + vlSelfRef.tb_s2a_conv_tile_memory__DOT__lanes))) 
                                 | VL_LTS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__y, vlSelfRef.tb_s2a_conv_tile_memory__DOT__ty)) 
                                | VL_GTES_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__y, 
                                              (vlSelfRef.tb_s2a_conv_tile_memory__DOT__ty 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__th))) 
                               | VL_LTS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__x, vlSelfRef.tb_s2a_conv_tile_memory__DOT__tx)) 
                              | VL_GTES_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__x, 
                                            (vlSelfRef.tb_s2a_conv_tile_memory__DOT__tx 
                                             + vlSelfRef.tb_s2a_conv_tile_memory__DOT__tw)))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:109: Assertion failed in %m: \350\276\223\345\207\272\345\234\260\345\235\200\344\270\215\345\234\250\346\211\200\351\200\211tile/group\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 109, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__idx 
                = (((VL_MULS_III(32, VL_MULS_III(32, 
                                                 (vlSelfRef.tb_s2a_conv_tile_memory__DOT__oc 
                                                  - vlSelfRef.tb_s2a_conv_tile_memory__DOT__group_base), vlSelfRef.tb_s2a_conv_tile_memory__DOT__th), vlSelfRef.tb_s2a_conv_tile_memory__DOT__tw) 
                     + VL_MULS_III(32, (vlSelfRef.tb_s2a_conv_tile_memory__DOT__y 
                                        - vlSelfRef.tb_s2a_conv_tile_memory__DOT__ty), vlSelfRef.tb_s2a_conv_tile_memory__DOT__tw)) 
                    + vlSelfRef.tb_s2a_conv_tile_memory__DOT__x) 
                   - vlSelfRef.tb_s2a_conv_tile_memory__DOT__tx);
            if (VL_UNLIKELY(((vlSelfRef.tb_s2a_conv_tile_memory__DOT__seen
                              [(0x000001ffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__idx)] 
                              | ((0x000000ffU & VL_SHIFTR_III(32,32,32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_wdata_latched, 
                                                              VL_MULS_III(32, (IData)(8U), vlSelfRef.tb_s2a_conv_tile_memory__DOT__selected_lane))) 
                                 != vlSelfRef.tb_s2a_conv_tile_memory__DOT__golden
                                 [(0x000001ffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__idx)]))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:112: Assertion failed in %m: \350\276\223\345\207\272\344\270\215\347\254\246/\351\207\215\345\244\215 layer=%0d case=%0d idx=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id
                             , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__ordinal
                             , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__idx);
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 112, "", false);
            }
            if (VL_UNLIKELY(((0U != (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_wdata_latched 
                                     & (~ VL_SHIFTL_III(32,32,32, (IData)(0x000000ffU), 
                                                        VL_MULS_III(32, (IData)(8U), vlSelfRef.tb_s2a_conv_tile_memory__DOT__selected_lane)))))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:113: Assertion failed in %m: \346\234\252\351\200\211write lane\351\235\236\351\233\266\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 113, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__seen[(0x000001ffU 
                                                          & vlSelfRef.tb_s2a_conv_tile_memory__DOT__idx)] = 1U;
        } else if (((vlSelfRef.tb_s2a_conv_tile_memory__DOT__address 
                     >= vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_ADDRESS
                     [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                        ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)
                        : 0U)][0U]) & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__address 
                                       < (vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_ADDRESS
                                          [((0x25U 
                                             >= (0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                             ? (0x0000003fU 
                                                & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)
                                             : 0U)][0U] 
                                          + vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_LENGTH_BYTES
                                          [((0x25U 
                                             >= (0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                             ? (0x0000003fU 
                                                & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)
                                             : 0U)][0U])))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__idx 
                = (vlSelfRef.tb_s2a_conv_tile_memory__DOT__address 
                   - vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_ADDRESS
                   [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                      ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)
                      : 0U)][0U]);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__actual_features 
                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__actual_features);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__ic 
                = VL_DIV_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__idx, 
                             (vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_H
                              [((0x25U >= (0x0000003fU 
                                           & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                 ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)
                                 : 0U)][0U] * vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_W
                              [((0x25U >= (0x0000003fU 
                                           & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                 ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)
                                 : 0U)][0U]));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__y 
                = VL_MODDIV_III(32, VL_DIV_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__idx, vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_W
                                               [((0x25U 
                                                  >= 
                                                  (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                                  ? 
                                                 (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)
                                                  : 0U)][0U]), vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_H
                                [((0x25U >= (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                   ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)
                                   : 0U)][0U]);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__x 
                = VL_MODDIV_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__idx, vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_W
                                [((0x25U >= (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                   ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)
                                   : 0U)][0U]);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__py 
                = ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__y 
                    - (vlSelfRef.tb_s2a_conv_tile_memory__DOT__ty 
                       * ((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                           ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_H
                          [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                           : 0U))) + ((0x25U >= (0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                       ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_TOP
                                      [(0x0000003fU 
                                        & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                                       : 0U));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__px 
                = ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__x 
                    - (vlSelfRef.tb_s2a_conv_tile_memory__DOT__tx 
                       * ((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                           ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_W
                          [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                           : 0U))) + ((0x25U >= (0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                       ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_LEFT
                                      [(0x0000003fU 
                                        & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                                       : 0U));
            if (VL_UNLIKELY((((((VL_GTES_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__ic, vlSelfRef.tb_s2a_conv_tile_memory__DOT__ci) 
                                 | VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__py)) 
                                | VL_GTES_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__py, vlSelfRef.tb_s2a_conv_tile_memory__DOT__ph)) 
                               | VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__px)) 
                              | VL_GTES_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__px, vlSelfRef.tb_s2a_conv_tile_memory__DOT__pw))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:121: Assertion failed in %m: feature\345\234\260\345\235\200\350\266\205patch\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 121, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_data 
                = VL_SHIFTL_III(32,32,32, ((0xc7ffU 
                                            >= (0x0000ffffU 
                                                & ((VL_MULS_III(32, 
                                                                VL_MULS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__ic, vlSelfRef.tb_s2a_conv_tile_memory__DOT__ph), vlSelfRef.tb_s2a_conv_tile_memory__DOT__pw) 
                                                    + 
                                                    VL_MULS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__py, vlSelfRef.tb_s2a_conv_tile_memory__DOT__pw)) 
                                                   + vlSelfRef.tb_s2a_conv_tile_memory__DOT__px)))
                                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__patch
                                           [(0x0000ffffU 
                                             & ((VL_MULS_III(32, 
                                                             VL_MULS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__ic, vlSelfRef.tb_s2a_conv_tile_memory__DOT__ph), vlSelfRef.tb_s2a_conv_tile_memory__DOT__pw) 
                                                 + 
                                                 VL_MULS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__py, vlSelfRef.tb_s2a_conv_tile_memory__DOT__pw)) 
                                                + vlSelfRef.tb_s2a_conv_tile_memory__DOT__px))]
                                            : 0U), 
                                VL_MULS_III(32, (IData)(8U), vlSelfRef.tb_s2a_conv_tile_memory__DOT__selected_lane));
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__idx 
                = (((vlSelfRef.tb_s2a_conv_tile_memory__DOT__address 
                     - ((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_PACKAGE_BASE
                        [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                         : 0U)) - ((0x25U >= (0x0000003fU 
                                              & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_WEIGHT_OFFSET
                                   [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                                    : 0U)) - (vlSelfRef.tb_s2a_conv_tile_memory__DOT__group_base 
                                              * vlSelfRef.tb_s2a_conv_tile_memory__DOT__k));
            if (VL_UNLIKELY(((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__idx) 
                              | VL_GTES_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__idx, 
                                            VL_MULS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__lanes, vlSelfRef.tb_s2a_conv_tile_memory__DOT__k)))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:126: Assertion failed in %m: GF8\345\234\260\345\235\200\350\266\212\347\273\204\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 126, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__actual_weights 
                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__actual_weights);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_data 
                = VL_SHIFTL_III(32,32,32, ((0x8fffU 
                                            >= (0x0000ffffU 
                                                & vlSelfRef.tb_s2a_conv_tile_memory__DOT__idx))
                                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__weights
                                           [(0x0000ffffU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__idx)]
                                            : 0U), 
                                VL_MULS_III(32, (IData)(8U), vlSelfRef.tb_s2a_conv_tile_memory__DOT__selected_lane));
        }
    }
    if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__hard_reset) {
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_layer_index_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_base_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_length_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_batch_count_latched = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_height_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_width_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_base_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_length_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_batch_count_latched = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_left_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_right_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_top_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_bottom_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__groups_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__padding_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_base_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_length_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_offset_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_bytes_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_batch_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base = 0U;
        __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y = 0U;
        __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x = 0U;
        __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_height = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_height = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_byte_count = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_point_count = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_address_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_wdata_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 0U;
    } else if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__abort) {
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_wdata_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 0U;
    } else if ((0x00000010U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
        if ((8U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 6U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x12U;
        } else if ((4U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 6U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x12U;
        } else if ((2U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
            if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 6U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x12U;
            }
        } else if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
            if ((((IData)(8U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base) 
                 < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched)) {
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base 
                    = ((IData)(8U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base);
                __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base = 0xffffffffU;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 6U;
            } else if (((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x 
                         + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width) 
                        < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched)) {
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x 
                    = ((IData)(8U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x);
                __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x = 0xffffffffU;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base = 0U;
                __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base = 0xffffffffU;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 2U;
            } else if (((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y 
                         + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_height) 
                        < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched)) {
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y 
                    = ((IData)(8U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y);
                __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y = 0xffffffffU;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base = 0U;
                __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base = 0xffffffffU;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x = 0U;
                __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x = 0xffffffffU;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 2U;
            } else {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 0U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x12U;
            }
        } else if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_valid) {
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index 
                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index);
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x0eU;
        }
    } else if ((8U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
        if ((4U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
            if ((2U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                    if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_valid) 
                         & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_ready))) {
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x10U;
                    }
                } else if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index 
                            >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x11U;
                } else if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index 
                            >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_point_count)) {
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index);
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index = 0U;
                } else {
                    __Vtemp_2[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_byte_offset_wide);
                    __Vtemp_2[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_byte_offset_wide 
                                             >> 0x00000020U));
                    __Vtemp_2[2U] = 0U;
                    __Vtemp_2[3U] = 0U;
                    if (((0x00000000ffffffffULL < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_address_wide) 
                         | VL_GTE_W(4, __Vtemp_2, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_elements_wide))) {
                        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 2U;
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x12U;
                    } else {
                        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_address_latched 
                            = ((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_address_wide 
                                        >> 2U)) << 2U);
                        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched 
                            = (0x0000000fU & ((IData)(1U) 
                                              << (3U 
                                                  & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_address_wide))));
                        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_wdata_latched 
                            = VL_SHIFTL_III(32,32,32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block
                                            [(0x000001ffU 
                                              & ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index 
                                                  << 6U) 
                                                 + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index))], 
                                            (0x00000018U 
                                             & ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_address_wide) 
                                                << 3U)));
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x0fU;
                    }
                }
            } else if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                if ((0U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0 
                        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[0U];
                    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0 
                        = (0x000001ffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index);
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0 = 1U;
                }
                if ((1U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v1 
                        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[1U];
                    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v1 
                        = (0x000001ffU & ((IData)(0x0040U) 
                                          + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index));
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v1 = 1U;
                }
                if ((2U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v2 
                        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[2U];
                    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v2 
                        = (0x000001ffU & ((IData)(0x0080U) 
                                          + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index));
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v2 = 1U;
                }
                if ((3U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v3 
                        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[3U];
                    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v3 
                        = (0x000001ffU & ((IData)(0x00c0U) 
                                          + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index));
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v3 = 1U;
                }
                if ((4U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v4 
                        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[4U];
                    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v4 
                        = (0x000001ffU & ((IData)(0x0100U) 
                                          + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index));
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v4 = 1U;
                }
                if ((5U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v5 
                        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[5U];
                    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v5 
                        = (0x000001ffU & ((IData)(0x0140U) 
                                          + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index));
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v5 = 1U;
                }
                if ((6U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v6 
                        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[6U];
                    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v6 
                        = (0x000001ffU & ((IData)(0x0180U) 
                                          + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index));
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v6 = 1U;
                }
                if ((7U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v7 
                        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[7U];
                    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v7 
                        = (0x000001ffU & ((IData)(0x01c0U) 
                                          + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index));
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v7 = 1U;
                }
                if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index) 
                     >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_point_count)) {
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index = 0U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index = 0U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x0eU;
                } else {
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index);
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index = 0U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x0bU;
                }
            } else if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 1U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x12U;
            } else if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 7U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x12U;
            } else {
                if ((0U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v0 
                        = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[0U]);
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v0 = 1U;
                }
                if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index) 
                     >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched)) {
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x0dU;
                } else {
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index);
                }
                if ((1U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v1 
                        = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[1U]);
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v1 = 1U;
                }
                if ((2U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v2 
                        = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[2U]);
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v2 = 1U;
                }
                if ((3U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v3 
                        = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[3U]);
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v3 = 1U;
                }
                if ((4U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v4 
                        = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[4U]);
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v4 = 1U;
                }
                if ((5U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v5 
                        = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[5U]);
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v5 = 1U;
                }
                if ((6U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v6 
                        = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[6U]);
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v6 = 1U;
                }
                if ((7U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v7 
                        = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[7U]);
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v7 = 1U;
                }
            }
        } else if ((2U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
            if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 1U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x12U;
                } else {
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v8 
                        = ((0U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? ((0x0c5bU >= (0x00000fffU 
                                            & (((0x25U 
                                                 >= 
                                                 (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                 ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                [(0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                 : 0U) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base)))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                               [(0x00000fffU & (((0x25U 
                                                  >= 
                                                  (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                 [(0x0000003fU 
                                                   & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                  : 0U) 
                                                + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base))]
                                : 0U) : 0U);
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v8 = 1U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index = 0U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x0cU;
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v9 
                        = ((1U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? ((0x0c5bU >= (0x00000fffU 
                                            & ((IData)(1U) 
                                               + ((
                                                   (0x25U 
                                                    >= 
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                   [
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                    : 0U) 
                                                  + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base))))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                               [(0x00000fffU & ((IData)(1U) 
                                                + (
                                                   ((0x25U 
                                                     >= 
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                     ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                    [
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                     : 0U) 
                                                   + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base)))]
                                : 0U) : 0U);
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v9 = 1U;
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v10 
                        = ((2U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? ((0x0c5bU >= (0x00000fffU 
                                            & ((IData)(2U) 
                                               + ((
                                                   (0x25U 
                                                    >= 
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                   [
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                    : 0U) 
                                                  + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base))))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                               [(0x00000fffU & ((IData)(2U) 
                                                + (
                                                   ((0x25U 
                                                     >= 
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                     ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                    [
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                     : 0U) 
                                                   + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base)))]
                                : 0U) : 0U);
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v11 
                        = ((3U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? ((0x0c5bU >= (0x00000fffU 
                                            & ((IData)(3U) 
                                               + ((
                                                   (0x25U 
                                                    >= 
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                   [
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                    : 0U) 
                                                  + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base))))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                               [(0x00000fffU & ((IData)(3U) 
                                                + (
                                                   ((0x25U 
                                                     >= 
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                     ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                    [
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                     : 0U) 
                                                   + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base)))]
                                : 0U) : 0U);
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v12 
                        = ((4U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? ((0x0c5bU >= (0x00000fffU 
                                            & ((IData)(4U) 
                                               + ((
                                                   (0x25U 
                                                    >= 
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                   [
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                    : 0U) 
                                                  + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base))))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                               [(0x00000fffU & ((IData)(4U) 
                                                + (
                                                   ((0x25U 
                                                     >= 
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                     ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                    [
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                     : 0U) 
                                                   + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base)))]
                                : 0U) : 0U);
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v13 
                        = ((5U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? ((0x0c5bU >= (0x00000fffU 
                                            & ((IData)(5U) 
                                               + ((
                                                   (0x25U 
                                                    >= 
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                   [
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                    : 0U) 
                                                  + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base))))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                               [(0x00000fffU & ((IData)(5U) 
                                                + (
                                                   ((0x25U 
                                                     >= 
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                     ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                    [
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                     : 0U) 
                                                   + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base)))]
                                : 0U) : 0U);
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v14 
                        = ((6U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? ((0x0c5bU >= (0x00000fffU 
                                            & ((IData)(6U) 
                                               + ((
                                                   (0x25U 
                                                    >= 
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                   [
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                    : 0U) 
                                                  + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base))))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                               [(0x00000fffU & ((IData)(6U) 
                                                + (
                                                   ((0x25U 
                                                     >= 
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                     ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                    [
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                     : 0U) 
                                                   + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base)))]
                                : 0U) : 0U);
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v15 
                        = ((7U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? ((0x0c5bU >= (0x00000fffU 
                                            & ((IData)(7U) 
                                               + ((
                                                   (0x25U 
                                                    >= 
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                   [
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                    : 0U) 
                                                  + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base))))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                               [(0x00000fffU & ((IData)(7U) 
                                                + (
                                                   ((0x25U 
                                                     >= 
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                     ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                    [
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                     : 0U) 
                                                   + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base)))]
                                : 0U) : 0U);
                }
            } else if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 1U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x12U;
            } else {
                __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v16 
                    = ((0U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                        ? ((0x0c5bU >= (0x00000fffU 
                                        & (((0x25U 
                                             >= (0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                             ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                            [(0x0000003fU 
                                              & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                             : 0U) 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base)))
                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                           [(0x00000fffU & (((0x25U 
                                              >= (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                             [(0x0000003fU 
                                               & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                              : 0U) 
                                            + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base))]
                            : 0U) : 0U);
                __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v16 = 1U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index = 0U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index = 0U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x0cU;
                __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v17 
                    = ((1U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                        ? ((0x0c5bU >= (0x00000fffU 
                                        & ((IData)(1U) 
                                           + (((0x25U 
                                                >= 
                                                (0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                               [(0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                : 0U) 
                                              + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base))))
                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                           [(0x00000fffU & ((IData)(1U) 
                                            + (((0x25U 
                                                 >= 
                                                 (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                 ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                [(0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                 : 0U) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base)))]
                            : 0U) : 0U);
                __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v17 = 1U;
                __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v18 
                    = ((2U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                        ? ((0x0c5bU >= (0x00000fffU 
                                        & ((IData)(2U) 
                                           + (((0x25U 
                                                >= 
                                                (0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                               [(0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                : 0U) 
                                              + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base))))
                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                           [(0x00000fffU & ((IData)(2U) 
                                            + (((0x25U 
                                                 >= 
                                                 (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                 ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                [(0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                 : 0U) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base)))]
                            : 0U) : 0U);
                __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v19 
                    = ((3U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                        ? ((0x0c5bU >= (0x00000fffU 
                                        & ((IData)(3U) 
                                           + (((0x25U 
                                                >= 
                                                (0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                               [(0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                : 0U) 
                                              + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base))))
                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                           [(0x00000fffU & ((IData)(3U) 
                                            + (((0x25U 
                                                 >= 
                                                 (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                 ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                [(0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                 : 0U) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base)))]
                            : 0U) : 0U);
                __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v20 
                    = ((4U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                        ? ((0x0c5bU >= (0x00000fffU 
                                        & ((IData)(4U) 
                                           + (((0x25U 
                                                >= 
                                                (0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                               [(0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                : 0U) 
                                              + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base))))
                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                           [(0x00000fffU & ((IData)(4U) 
                                            + (((0x25U 
                                                 >= 
                                                 (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                 ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                [(0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                 : 0U) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base)))]
                            : 0U) : 0U);
                __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v21 
                    = ((5U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                        ? ((0x0c5bU >= (0x00000fffU 
                                        & ((IData)(5U) 
                                           + (((0x25U 
                                                >= 
                                                (0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                               [(0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                : 0U) 
                                              + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base))))
                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                           [(0x00000fffU & ((IData)(5U) 
                                            + (((0x25U 
                                                 >= 
                                                 (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                 ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                [(0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                 : 0U) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base)))]
                            : 0U) : 0U);
                __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v22 
                    = ((6U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                        ? ((0x0c5bU >= (0x00000fffU 
                                        & ((IData)(6U) 
                                           + (((0x25U 
                                                >= 
                                                (0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                               [(0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                : 0U) 
                                              + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base))))
                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                           [(0x00000fffU & ((IData)(6U) 
                                            + (((0x25U 
                                                 >= 
                                                 (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                 ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                [(0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                 : 0U) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base)))]
                            : 0U) : 0U);
                __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v23 
                    = ((7U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                        ? ((0x0c5bU >= (0x00000fffU 
                                        & ((IData)(7U) 
                                           + (((0x25U 
                                                >= 
                                                (0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                               [(0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                : 0U) 
                                              + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base))))
                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                           [(0x00000fffU & ((IData)(7U) 
                                            + (((0x25U 
                                                 >= 
                                                 (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                                 ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                                [(0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                                 : 0U) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base)))]
                            : 0U) : 0U);
            }
        } else if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
            if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_valid) {
                if ((0x8fffU >= (0x0000ffffU & ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index 
                                                 * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched) 
                                                + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index)))) {
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group__v0 
                        = (0x000000ffU & VL_SHIFTR_III(8,32,32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_data, 
                                                       ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_byte_lane) 
                                                        << 3U)));
                    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group__v0 
                        = (0x0000ffffU & ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index 
                                           * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched) 
                                          + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index));
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group__v0 = 1U;
                }
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 7U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index);
            }
        } else if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_valid) 
                    & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_ready))) {
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 9U;
        }
    } else if ((4U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
        if ((2U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
            if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index 
                     >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x0aU;
                } else if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index 
                            >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched)) {
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index);
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index = 0U;
                } else if ((0x00000000ffffffffULL < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_source_address_wide)) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 2U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x12U;
                } else {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_address_latched 
                        = ((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_source_address_wide 
                                    >> 2U)) << 2U);
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched 
                        = (0x0000000fU & ((IData)(1U) 
                                          << (3U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_source_address_wide))));
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_wdata_latched = 0U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 8U;
                }
            } else if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base 
                        >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched)) {
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x11U;
            } else {
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count 
                    = ((8U <= (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched 
                               - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base))
                        ? 8U : (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched 
                                - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base));
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index = 0U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index = 0U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 7U;
            }
        } else if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
            if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_valid) {
                if ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index))) {
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v0 
                        = (0x000000ffU & VL_SHIFTR_III(8,32,32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_data, 
                                                       ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_byte_lane) 
                                                        << 3U)));
                    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v0 
                        = (0x0000ffffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index);
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v0 = 1U;
                }
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 3U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index);
            }
        } else if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_valid) 
                    & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_ready))) {
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 5U;
        }
    } else if ((2U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
        if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
            if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index 
                 >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_byte_count)) {
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base = 0U;
                __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base = 0xffffffffU;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 6U;
            } else if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_in_bounds) {
                if ((0x00000000ffffffffULL < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_address_wide)) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 2U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x12U;
                } else {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_address_latched 
                        = ((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_address_wide 
                                    >> 2U)) << 2U);
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched 
                        = (0x0000000fU & ((IData)(1U) 
                                          << (3U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_address_wide))));
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_wdata_latched = 0U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 4U;
                }
            } else {
                if ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index))) {
                    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v1 
                        = (0x0000ffffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index);
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v1 = 1U;
                }
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index);
            }
        } else {
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_height 
                = ((8U <= (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched 
                           - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y))
                    ? 8U : (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched 
                            - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y));
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 3U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width 
                = ((8U <= (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched 
                           - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x))
                    ? 8U : (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched 
                            - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_height 
                = (((((8U <= (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched 
                              - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y))
                       ? 8U : (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched 
                               - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y)) 
                     - (IData)(1U)) * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched) 
                   + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width 
                = (((((8U <= (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched 
                              - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x))
                       ? 8U : (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched 
                               - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x)) 
                     - (IData)(1U)) * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched) 
                   + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched);
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_byte_count 
                = (((((((8U <= (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched 
                                - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y))
                         ? 8U : (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched 
                                 - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y)) 
                       - (IData)(1U)) * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched) 
                     + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched) 
                    * (((((8U <= (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched 
                                  - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x))
                           ? 8U : (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched 
                                   - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x)) 
                         - (IData)(1U)) * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched) 
                       + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched)) 
                   * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched);
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_point_count 
                = (((8U <= (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched 
                            - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y))
                     ? 8U : (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched 
                             - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y)) 
                   * ((8U <= (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched 
                              - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x))
                       ? 8U : (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched 
                               - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x)));
        }
    } else if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
        if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_ok) {
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_wide[0U];
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 2U;
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_error;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x12U;
        }
    } else if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__start_valid) 
                & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__start_ready))) {
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_layer_index_latched 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_base_latched 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_ADDRESS
            [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
               ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)
               : 0U)][0U];
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_length_latched 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_LENGTH_BYTES
            [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
               ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)
               : 0U)][0U];
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_batch_count_latched 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_N
            [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
               ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)
               : 0U)][0U];
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_C
            [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
               ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)
               : 0U)][0U];
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_height_latched 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_H
            [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
               ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)
               : 0U)][0U];
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_width_latched 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_W
            [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
               ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)
               : 0U)][0U];
        if ((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_base_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_length_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_LENGTH_BYTES
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_batch_count_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_N
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)];
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_C
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)];
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_H
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)];
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)];
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_H
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)];
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_W
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)];
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_H
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)];
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_W
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_left_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_LEFT
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_right_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_RIGHT
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_top_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_TOP
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_bottom_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_BOTTOM
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_base_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_PACKAGE_BASE
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_length_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_PACKAGE_LENGTH
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_offset_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_WEIGHT_OFFSET
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_bytes_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_WEIGHT_BYTES
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)];
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_base_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_length_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_batch_count_latched = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_left_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_right_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_top_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_bottom_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_base_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_length_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_offset_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_bytes_latched = 0U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__groups_latched = 1U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__padding_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_batch_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched 
            = ((2U == ((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ACTIVATION
                       [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)]
                        : 0U)) ? 1U : 0U);
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base = 0U;
        __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y = 0U;
        __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x = 0U;
        __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 1U;
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_height 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_height;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_byte_count 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_byte_count;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_point_count 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_point_count;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index;
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v1) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v1] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v1;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v2) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v2] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v2;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v3) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v3] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v3;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v4) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v4] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v4;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v5) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v5] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v5;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v6) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v6] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v6;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v7) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v7] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v7;
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base 
        = ((__Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base 
            & __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base) 
           | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base 
              & (~ __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base)));
    __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index;
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group__v0) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group__v0] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group__v0;
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched;
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v0) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v0] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v1) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v1] = 0U;
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x 
        = ((__Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x 
            & __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x) 
           | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x 
              & (~ __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x)));
    __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y 
        = ((__Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y 
            & __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y) 
           | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y 
              & (~ __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y)));
    __VdlyMask__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count;
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v0) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[0U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v1) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[1U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v1;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v2) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[2U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v2;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v3) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[3U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v3;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v4) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[4U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v4;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v5) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[5U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v5;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v6) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[6U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v6;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v7) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[7U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v7;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v8) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[0U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v8;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v9) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[1U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v9;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[2U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v10;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[3U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v11;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[4U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v12;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[5U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v13;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[6U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v14;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[7U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v15;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v16) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[0U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v16;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v17) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[1U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v17;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[2U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v18;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[3U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v19;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[4U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v20;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[5U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v21;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[6U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v22;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[7U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v23;
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_byte_lane 
        = (3U & (0x00030210U >> ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched) 
                                 << 1U)));
    __Vtemp_3[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_batch_count_latched;
    __Vtemp_3[1U] = 0U;
    __Vtemp_3[2U] = 0U;
    __Vtemp_3[3U] = 0U;
    __Vtemp_4[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched;
    __Vtemp_4[1U] = 0U;
    __Vtemp_4[2U] = 0U;
    __Vtemp_4[3U] = 0U;
    VL_MUL_W(4, __Vtemp_5, __Vtemp_3, __Vtemp_4);
    __Vtemp_6[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_height_latched;
    __Vtemp_6[1U] = 0U;
    __Vtemp_6[2U] = 0U;
    __Vtemp_6[3U] = 0U;
    VL_MUL_W(4, __Vtemp_7, __Vtemp_5, __Vtemp_6);
    __Vtemp_8[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_width_latched;
    __Vtemp_8[1U] = 0U;
    __Vtemp_8[2U] = 0U;
    __Vtemp_8[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__input_elements_wide, __Vtemp_7, __Vtemp_8);
    __Vtemp_9[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_batch_count_latched;
    __Vtemp_9[1U] = 0U;
    __Vtemp_9[2U] = 0U;
    __Vtemp_9[3U] = 0U;
    __Vtemp_10[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched;
    __Vtemp_10[1U] = 0U;
    __Vtemp_10[2U] = 0U;
    __Vtemp_10[3U] = 0U;
    VL_MUL_W(4, __Vtemp_11, __Vtemp_9, __Vtemp_10);
    __Vtemp_12[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched;
    __Vtemp_12[1U] = 0U;
    __Vtemp_12[2U] = 0U;
    __Vtemp_12[3U] = 0U;
    VL_MUL_W(4, __Vtemp_13, __Vtemp_11, __Vtemp_12);
    __Vtemp_14[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched;
    __Vtemp_14[1U] = 0U;
    __Vtemp_14[2U] = 0U;
    __Vtemp_14[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_elements_wide, __Vtemp_13, __Vtemp_14);
    __Vtemp_15[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched;
    __Vtemp_15[1U] = 0U;
    __Vtemp_15[2U] = 0U;
    __Vtemp_15[3U] = 0U;
    __Vtemp_16[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched;
    __Vtemp_16[1U] = 0U;
    __Vtemp_16[2U] = 0U;
    __Vtemp_16[3U] = 0U;
    VL_MUL_W(4, __Vtemp_17, __Vtemp_15, __Vtemp_16);
    __Vtemp_18[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched;
    __Vtemp_18[1U] = 0U;
    __Vtemp_18[2U] = 0U;
    __Vtemp_18[3U] = 0U;
    VL_MUL_W(4, __Vtemp_19, __Vtemp_17, __Vtemp_18);
    __Vtemp_20[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched;
    __Vtemp_20[1U] = 0U;
    __Vtemp_20[2U] = 0U;
    __Vtemp_20[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__expected_weight_bytes_wide, __Vtemp_19, __Vtemp_20);
    __Vtemp_21[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched;
    __Vtemp_21[1U] = 0U;
    __Vtemp_21[2U] = 0U;
    __Vtemp_21[3U] = 0U;
    __Vtemp_22[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched;
    __Vtemp_22[1U] = 0U;
    __Vtemp_22[2U] = 0U;
    __Vtemp_22[3U] = 0U;
    VL_MUL_W(4, __Vtemp_23, __Vtemp_21, __Vtemp_22);
    __Vtemp_24[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched;
    __Vtemp_24[1U] = 0U;
    __Vtemp_24[2U] = 0U;
    __Vtemp_24[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_wide, __Vtemp_23, __Vtemp_24);
    __Vtemp_25[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_base_latched;
    __Vtemp_25[1U] = 0U;
    __Vtemp_25[2U] = 0U;
    __Vtemp_25[3U] = 0U;
    __Vtemp_26[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_length_latched;
    __Vtemp_26[1U] = 0U;
    __Vtemp_26[2U] = 0U;
    __Vtemp_26[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__input_end_wide, __Vtemp_25, __Vtemp_26);
    __Vtemp_27[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_base_latched;
    __Vtemp_27[1U] = 0U;
    __Vtemp_27[2U] = 0U;
    __Vtemp_27[3U] = 0U;
    __Vtemp_28[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_length_latched;
    __Vtemp_28[1U] = 0U;
    __Vtemp_28[2U] = 0U;
    __Vtemp_28[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__output_end_wide, __Vtemp_27, __Vtemp_28);
    __Vtemp_29[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_base_latched;
    __Vtemp_29[1U] = 0U;
    __Vtemp_29[2U] = 0U;
    __Vtemp_29[3U] = 0U;
    __Vtemp_30[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_length_latched;
    __Vtemp_30[1U] = 0U;
    __Vtemp_30[2U] = 0U;
    __Vtemp_30[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_end_wide, __Vtemp_29, __Vtemp_30);
    __Vtemp_31[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_offset_latched;
    __Vtemp_31[1U] = 0U;
    __Vtemp_31[2U] = 0U;
    __Vtemp_31[3U] = 0U;
    __Vtemp_32[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_bytes_latched;
    __Vtemp_32[1U] = 0U;
    __Vtemp_32[2U] = 0U;
    __Vtemp_32[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_end_wide, __Vtemp_31, __Vtemp_32);
    tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_height_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_top_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_bottom_latched)));
    tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_width_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_left_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_right_latched)));
    tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_height_wide[0U] = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_height_wide[1U] = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_height_wide[2U] = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_height_wide[3U] = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_width_wide[0U] = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_width_wide[1U] = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_width_wide[2U] = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_width_wide[3U] = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_bytes_wide[0U] = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_bytes_wide[1U] = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_bytes_wide[2U] = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_bytes_wide[3U] = 0U;
    if (((0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched) 
         & (0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched))) {
        __Vtemp_33[0U] = (((8U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched
                            : 8U) - (IData)(1U));
        __Vtemp_33[1U] = 0U;
        __Vtemp_33[2U] = 0U;
        __Vtemp_33[3U] = 0U;
        __Vtemp_34[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched;
        __Vtemp_34[1U] = 0U;
        __Vtemp_34[2U] = 0U;
        __Vtemp_34[3U] = 0U;
        VL_MUL_W(4, __Vtemp_35, __Vtemp_33, __Vtemp_34);
        __Vtemp_36[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched;
        __Vtemp_36[1U] = 0U;
        __Vtemp_36[2U] = 0U;
        __Vtemp_36[3U] = 0U;
        VL_ADD_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_height_wide, __Vtemp_35, __Vtemp_36);
        __Vtemp_37[0U] = (((8U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched
                            : 8U) - (IData)(1U));
        __Vtemp_37[1U] = 0U;
        __Vtemp_37[2U] = 0U;
        __Vtemp_37[3U] = 0U;
        __Vtemp_38[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched;
        __Vtemp_38[1U] = 0U;
        __Vtemp_38[2U] = 0U;
        __Vtemp_38[3U] = 0U;
        VL_MUL_W(4, __Vtemp_39, __Vtemp_37, __Vtemp_38);
        __Vtemp_40[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched;
        __Vtemp_40[1U] = 0U;
        __Vtemp_40[2U] = 0U;
        __Vtemp_40[3U] = 0U;
        VL_ADD_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_width_wide, __Vtemp_39, __Vtemp_40);
        VL_MUL_W(4, __Vtemp_41, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_height_wide, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_width_wide);
        __Vtemp_42[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched;
        __Vtemp_42[1U] = 0U;
        __Vtemp_42[2U] = 0U;
        __Vtemp_42[3U] = 0U;
        VL_MUL_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_bytes_wide, __Vtemp_41, __Vtemp_42);
    }
    __Vtemp_43[0U] = ((8U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched)
                       ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched
                       : 8U);
    __Vtemp_43[1U] = 0U;
    __Vtemp_43[2U] = 0U;
    __Vtemp_43[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_weight_group_bytes_wide, __Vtemp_43, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_wide);
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_ok = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_error = 1U;
    __Vtemp_45[0U] = 0x00001fffU;
    __Vtemp_45[1U] = 0U;
    __Vtemp_45[2U] = 0U;
    __Vtemp_45[3U] = 0U;
    if ((((((((((((((((((((((1U < (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched)) 
                            | (1U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_batch_count_latched)) 
                           | (1U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_batch_count_latched)) 
                          | (0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_batch_latched)) 
                         | (0U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched)) 
                        | (0U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_height_latched)) 
                       | (0U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_width_latched)) 
                      | (0U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched)) 
                     | (0U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched)) 
                    | (0U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched)) 
                   | (0U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched)) 
                  | (0U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched)) 
                 | (0U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched)) 
                | (0U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched)) 
               | (1U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__groups_latched)) 
              | (0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__padding_latched)) 
             | (0U == (((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_wide[0U] 
                         | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_wide[1U]) 
                        | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_wide[2U]) 
                       | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_wide[3U]))) 
            | VL_LT_W(4, __Vtemp_45, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_wide)) 
           | (0x00000026U <= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)) 
          | ((0x00000026U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched) 
             & (0U != ((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OP
                       [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                        : 0U)))) | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched 
                                    != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_layer_index_latched))) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_error 
            = (((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched 
                 != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_layer_index_latched) 
                | (0x00000026U <= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                ? 2U : 1U);
    } else {
        __Vtemp_46[0U] = 0xffffffffU;
        __Vtemp_46[1U] = 0U;
        __Vtemp_46[2U] = 0U;
        __Vtemp_46[3U] = 0U;
        __Vtemp_47[0U] = 0xffffffffU;
        __Vtemp_47[1U] = 0U;
        __Vtemp_47[2U] = 0U;
        __Vtemp_47[3U] = 0U;
        __Vtemp_48[0U] = 0xffffffffU;
        __Vtemp_48[1U] = 0U;
        __Vtemp_48[2U] = 0U;
        __Vtemp_48[3U] = 0U;
        if ((((((VL_LT_W(4, __Vtemp_46, tb_s2a_conv_tile_memory__DOT__dut__DOT__input_elements_wide) 
                 | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_length_latched 
                    != tb_s2a_conv_tile_memory__DOT__dut__DOT__input_elements_wide[0U])) 
                | VL_LT_W(4, __Vtemp_47, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_elements_wide)) 
               | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_length_latched 
                  != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_elements_wide[0U])) 
              | VL_LT_W(4, __Vtemp_48, tb_s2a_conv_tile_memory__DOT__dut__DOT__expected_weight_bytes_wide)) 
             | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_bytes_latched 
                != tb_s2a_conv_tile_memory__DOT__dut__DOT__expected_weight_bytes_wide[0U]))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_error = 3U;
        } else {
            __Vtemp_49[0U] = 0U;
            __Vtemp_49[1U] = 1U;
            __Vtemp_49[2U] = 0U;
            __Vtemp_49[3U] = 0U;
            __Vtemp_50[0U] = 0U;
            __Vtemp_50[1U] = 1U;
            __Vtemp_50[2U] = 0U;
            __Vtemp_50[3U] = 0U;
            __Vtemp_51[0U] = 0U;
            __Vtemp_51[1U] = 1U;
            __Vtemp_51[2U] = 0U;
            __Vtemp_51[3U] = 0U;
            __Vtemp_52[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_length_latched;
            __Vtemp_52[1U] = 0U;
            __Vtemp_52[2U] = 0U;
            __Vtemp_52[3U] = 0U;
            __Vtemp_53[0U] = 0x00000c5cU;
            __Vtemp_53[1U] = 0U;
            __Vtemp_53[2U] = 0U;
            __Vtemp_53[3U] = 0U;
            __Vtemp_54[0U] = ((0x25U >= (0x0000003fU 
                                         & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                               ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                              [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                               : 0U);
            __Vtemp_54[1U] = 0U;
            __Vtemp_54[2U] = 0U;
            __Vtemp_54[3U] = 0U;
            __Vtemp_55[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched;
            __Vtemp_55[1U] = 0U;
            __Vtemp_55[2U] = 0U;
            __Vtemp_55[3U] = 0U;
            VL_ADD_W(4, __Vtemp_56, __Vtemp_54, __Vtemp_55);
            __Vtemp_57[0U] = 0x0000c800U;
            __Vtemp_57[1U] = 0U;
            __Vtemp_57[2U] = 0U;
            __Vtemp_57[3U] = 0U;
            __Vtemp_58[0U] = 0x00009000U;
            __Vtemp_58[1U] = 0U;
            __Vtemp_58[2U] = 0U;
            __Vtemp_58[3U] = 0U;
            if (((((((((VL_LT_W(4, __Vtemp_49, tb_s2a_conv_tile_memory__DOT__dut__DOT__input_end_wide) 
                        | VL_LT_W(4, __Vtemp_50, tb_s2a_conv_tile_memory__DOT__dut__DOT__output_end_wide)) 
                       | VL_LT_W(4, __Vtemp_51, tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_end_wide)) 
                      | (0U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_length_latched)) 
                     | VL_GT_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_end_wide, __Vtemp_52)) 
                    | (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                        [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                         : 0U) != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched)) 
                   | VL_LT_W(4, __Vtemp_53, __Vtemp_56)) 
                  | VL_LT_W(4, __Vtemp_57, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_bytes_wide)) 
                 | VL_LT_W(4, __Vtemp_58, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_weight_group_bytes_wide))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_error = 2U;
            } else if (((((tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_numerator 
                           < (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched))) 
                          | (tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_numerator 
                             < (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched)))) 
                         | ((1ULL + VL_DIV_QQQ(64, 
                                               (tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_numerator 
                                                - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched))), (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched)))) 
                            != (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched)))) 
                        | ((1ULL + VL_DIV_QQQ(64, (tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_numerator 
                                                   - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched))), (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched)))) 
                           != (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched))))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_error = 1U;
            } else {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_ok = 1U;
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_error = 0U;
            }
        }
    }
}

extern const VlWide<10>/*319:0*/ Vtb_s2a_conv_tile_memory__ConstPool__CONST_hb4617e49_0;
extern const VlUnpacked<IData/*31:0*/, 5> Vtb_s2a_conv_tile_memory__ConstPool__TABLE_hc6a14c36_0;

void Vtb_s2a_conv_tile_memory___024root___nba_sequent__TOP__1(Vtb_s2a_conv_tile_memory___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___nba_sequent__TOP__1\n"); );
    Vtb_s2a_conv_tile_memory__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__0__Vfuncout;
    __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__0__Vfuncout = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__0__n;
    __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__0__n = 0;
    IData/*31:0*/ __Vtemp_1;
    // Body
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_valid = 0U;
    if ((((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__hard_reset) 
          | (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__abort)) 
         | (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__cancel))) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_ready = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__pending_response = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__wait_remaining = 0xffffffffU;
    } else if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__pending_response) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_valid = 1U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__pending_response = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_ready = 0U;
    } else if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_valid) {
        if (VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__wait_remaining)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__cls 
                = ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write)
                    ? 2U : (((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_address_latched 
                              >= vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_ADDRESS
                              [((0x25U >= (0x0000003fU 
                                           & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                 ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)
                                 : 0U)][0U]) & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_address_latched 
                                                < (vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_ADDRESS
                                                   [
                                                   ((0x25U 
                                                     >= 
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                                     ? 
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)
                                                     : 0U)][0U] 
                                                   + vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_LENGTH_BYTES
                                                   [
                                                   ((0x25U 
                                                     >= 
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id))
                                                     ? 
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id)
                                                     : 0U)][0U])))
                             ? 0U : 1U));
            __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__0__n 
                = ((2U >= (3U & vlSelfRef.tb_s2a_conv_tile_memory__DOT__cls))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__counts
                   [(3U & vlSelfRef.tb_s2a_conv_tile_memory__DOT__cls)]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__held_addr 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_address_latched;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__held_wdata 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_wdata_latched;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__held_rstrb 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_rstrb;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__held_wstrb 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_wstrb;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__held_write 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write;
            __Vtemp_1 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__0__n, (IData)(5U)), Vtb_s2a_conv_tile_memory__ConstPool__CONST_hb4617e49_0);
            __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__0__Vfuncout 
                = Vtb_s2a_conv_tile_memory__ConstPool__TABLE_hc6a14c36_0
                [__Vtemp_1];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__wait_remaining 
                = __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__0__Vfuncout;
        } else if (VL_UNLIKELY(((((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_address_latched 
                                     != vlSelfRef.tb_s2a_conv_tile_memory__DOT__held_addr) 
                                    | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_wdata_latched 
                                       != vlSelfRef.tb_s2a_conv_tile_memory__DOT__held_wdata)) 
                                   | ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_rstrb) 
                                      != (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__held_rstrb))) 
                                  | ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_wstrb) 
                                     != (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__held_wstrb))) 
                                 | ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write) 
                                    != (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__held_write)))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:91: Assertion failed in %m: stall\350\257\267\346\261\202\345\255\227\346\256\265\346\224\271\345\217\230\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 91, "", false);
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_ready 
            = (0U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__wait_remaining);
        if (VL_LTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__wait_remaining)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__wait_remaining 
                = (vlSelfRef.tb_s2a_conv_tile_memory__DOT__wait_remaining 
                   - (IData)(1U));
            if ((2U >= (3U & vlSelfRef.tb_s2a_conv_tile_memory__DOT__cls))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__stalls[(3U 
                                                                & vlSelfRef.tb_s2a_conv_tile_memory__DOT__cls)] 
                    = ((IData)(1U) + ((2U >= (3U & vlSelfRef.tb_s2a_conv_tile_memory__DOT__cls))
                                       ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__stalls
                                      [(3U & vlSelfRef.tb_s2a_conv_tile_memory__DOT__cls)]
                                       : 0U));
            }
        }
    } else {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_ready = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__wait_remaining = 0xffffffffU;
    }
}

void Vtb_s2a_conv_tile_memory___024root___nba_comb__TOP__0(Vtb_s2a_conv_tile_memory___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___nba_comb__TOP__0\n"); );
    Vtb_s2a_conv_tile_memory__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_plane_bytes;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_plane_bytes = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_rem;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_rem = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_offset;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_offset = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_area;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_area = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_y = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_x;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_x = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_y = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_x;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_x = 0;
    CData/*0:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index_wide;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index_wide = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index = 0;
    VlWide<3>/*95:0*/ __Vtemp_1;
    VlWide<3>/*95:0*/ __Vtemp_2;
    VlWide<3>/*95:0*/ __Vtemp_3;
    VlWide<3>/*95:0*/ __Vtemp_4;
    VlWide<3>/*95:0*/ __Vtemp_5;
    VlWide<3>/*95:0*/ __Vtemp_6;
    VlWide<3>/*95:0*/ __Vtemp_7;
    VlWide<3>/*95:0*/ __Vtemp_8;
    VlWide<3>/*95:0*/ __Vtemp_9;
    VlWide<3>/*95:0*/ __Vtemp_10;
    VlWide<3>/*95:0*/ __Vtemp_11;
    VlWide<3>/*95:0*/ __Vtemp_12;
    VlWide<3>/*95:0*/ __Vtemp_13;
    VlWide<3>/*95:0*/ __Vtemp_14;
    VlWide<3>/*95:0*/ __Vtemp_16;
    VlWide<3>/*95:0*/ __Vtemp_17;
    VlWide<3>/*95:0*/ __Vtemp_19;
    VlWide<3>/*95:0*/ __Vtemp_20;
    VlWide<3>/*95:0*/ __Vtemp_21;
    VlWide<3>/*95:0*/ __Vtemp_22;
    VlWide<3>/*95:0*/ __Vtemp_23;
    VlWide<3>/*95:0*/ __Vtemp_24;
    VlWide<3>/*95:0*/ __Vtemp_25;
    VlWide<3>/*95:0*/ __Vtemp_26;
    VlWide<3>/*95:0*/ __Vtemp_27;
    VlWide<3>/*95:0*/ __Vtemp_28;
    VlWide<3>/*95:0*/ __Vtemp_29;
    VlWide<3>/*95:0*/ __Vtemp_30;
    VlWide<3>/*95:0*/ __Vtemp_31;
    VlWide<3>/*95:0*/ __Vtemp_32;
    VlWide<3>/*95:0*/ __Vtemp_34;
    VlWide<3>/*95:0*/ __Vtemp_35;
    VlWide<3>/*95:0*/ __Vtemp_37;
    VlWide<3>/*95:0*/ __Vtemp_38;
    VlWide<3>/*95:0*/ __Vtemp_39;
    VlWide<3>/*95:0*/ __Vtemp_40;
    VlWide<3>/*95:0*/ __Vtemp_41;
    VlWide<3>/*95:0*/ __Vtemp_42;
    VlWide<3>/*95:0*/ __Vtemp_43;
    VlWide<3>/*95:0*/ __Vtemp_44;
    VlWide<3>/*95:0*/ __Vtemp_45;
    VlWide<3>/*95:0*/ __Vtemp_46;
    VlWide<3>/*95:0*/ __Vtemp_47;
    VlWide<3>/*95:0*/ __Vtemp_48;
    VlWide<3>/*95:0*/ __Vtemp_49;
    VlWide<3>/*95:0*/ __Vtemp_50;
    VlWide<3>/*95:0*/ __Vtemp_52;
    VlWide<3>/*95:0*/ __Vtemp_53;
    VlWide<3>/*95:0*/ __Vtemp_55;
    VlWide<3>/*95:0*/ __Vtemp_56;
    VlWide<3>/*95:0*/ __Vtemp_57;
    VlWide<3>/*95:0*/ __Vtemp_58;
    VlWide<3>/*95:0*/ __Vtemp_59;
    VlWide<3>/*95:0*/ __Vtemp_60;
    VlWide<3>/*95:0*/ __Vtemp_61;
    VlWide<3>/*95:0*/ __Vtemp_62;
    VlWide<3>/*95:0*/ __Vtemp_63;
    VlWide<3>/*95:0*/ __Vtemp_64;
    VlWide<3>/*95:0*/ __Vtemp_65;
    VlWide<3>/*95:0*/ __Vtemp_66;
    VlWide<3>/*95:0*/ __Vtemp_67;
    VlWide<3>/*95:0*/ __Vtemp_68;
    VlWide<3>/*95:0*/ __Vtemp_70;
    VlWide<3>/*95:0*/ __Vtemp_71;
    VlWide<3>/*95:0*/ __Vtemp_73;
    VlWide<3>/*95:0*/ __Vtemp_74;
    VlWide<3>/*95:0*/ __Vtemp_75;
    VlWide<3>/*95:0*/ __Vtemp_76;
    VlWide<3>/*95:0*/ __Vtemp_77;
    VlWide<3>/*95:0*/ __Vtemp_78;
    VlWide<3>/*95:0*/ __Vtemp_79;
    VlWide<3>/*95:0*/ __Vtemp_80;
    VlWide<3>/*95:0*/ __Vtemp_81;
    VlWide<3>/*95:0*/ __Vtemp_82;
    VlWide<3>/*95:0*/ __Vtemp_83;
    VlWide<3>/*95:0*/ __Vtemp_84;
    VlWide<3>/*95:0*/ __Vtemp_85;
    VlWide<3>/*95:0*/ __Vtemp_86;
    VlWide<3>/*95:0*/ __Vtemp_88;
    VlWide<3>/*95:0*/ __Vtemp_89;
    VlWide<3>/*95:0*/ __Vtemp_91;
    VlWide<3>/*95:0*/ __Vtemp_92;
    VlWide<3>/*95:0*/ __Vtemp_93;
    VlWide<3>/*95:0*/ __Vtemp_94;
    VlWide<3>/*95:0*/ __Vtemp_95;
    VlWide<3>/*95:0*/ __Vtemp_96;
    VlWide<3>/*95:0*/ __Vtemp_97;
    VlWide<3>/*95:0*/ __Vtemp_98;
    VlWide<3>/*95:0*/ __Vtemp_99;
    VlWide<3>/*95:0*/ __Vtemp_100;
    VlWide<3>/*95:0*/ __Vtemp_101;
    VlWide<3>/*95:0*/ __Vtemp_102;
    VlWide<3>/*95:0*/ __Vtemp_103;
    VlWide<3>/*95:0*/ __Vtemp_104;
    VlWide<3>/*95:0*/ __Vtemp_106;
    VlWide<3>/*95:0*/ __Vtemp_107;
    VlWide<3>/*95:0*/ __Vtemp_109;
    VlWide<3>/*95:0*/ __Vtemp_110;
    VlWide<3>/*95:0*/ __Vtemp_111;
    VlWide<3>/*95:0*/ __Vtemp_112;
    VlWide<3>/*95:0*/ __Vtemp_113;
    VlWide<3>/*95:0*/ __Vtemp_114;
    VlWide<3>/*95:0*/ __Vtemp_115;
    VlWide<3>/*95:0*/ __Vtemp_116;
    VlWide<3>/*95:0*/ __Vtemp_117;
    VlWide<3>/*95:0*/ __Vtemp_118;
    VlWide<3>/*95:0*/ __Vtemp_119;
    VlWide<3>/*95:0*/ __Vtemp_120;
    VlWide<3>/*95:0*/ __Vtemp_121;
    VlWide<3>/*95:0*/ __Vtemp_122;
    VlWide<3>/*95:0*/ __Vtemp_124;
    VlWide<3>/*95:0*/ __Vtemp_125;
    VlWide<3>/*95:0*/ __Vtemp_127;
    VlWide<3>/*95:0*/ __Vtemp_128;
    VlWide<3>/*95:0*/ __Vtemp_129;
    VlWide<3>/*95:0*/ __Vtemp_130;
    VlWide<3>/*95:0*/ __Vtemp_131;
    VlWide<3>/*95:0*/ __Vtemp_132;
    VlWide<3>/*95:0*/ __Vtemp_133;
    VlWide<3>/*95:0*/ __Vtemp_134;
    VlWide<3>/*95:0*/ __Vtemp_135;
    VlWide<3>/*95:0*/ __Vtemp_136;
    VlWide<3>/*95:0*/ __Vtemp_137;
    VlWide<3>/*95:0*/ __Vtemp_138;
    VlWide<3>/*95:0*/ __Vtemp_139;
    VlWide<3>/*95:0*/ __Vtemp_140;
    VlWide<3>/*95:0*/ __Vtemp_142;
    VlWide<3>/*95:0*/ __Vtemp_143;
    // Body
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_source_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_base_latched)) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_offset_latched)) 
              + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index)) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index)))))));
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_byte_offset_wide 
        = ((QData)((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x 
                            + (VL_MODDIV_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width) 
                               & (- (IData)((0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width))))))) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched)) 
              * ((QData)((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y 
                                  + (VL_DIV_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width) 
                                     & (- (IData)((0U 
                                                   != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width))))))) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index)))))));
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[0U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[0U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[0U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[0U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[0U] = 0U;
    if ((0x00000026U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U] 
            = (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                 ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                 : 0U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base);
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])) {
            if ((0U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U]))) {
                    __Vtemp_1[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_1[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_1[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_2[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_2[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_2[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_3[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_3[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_3[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_4[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_4[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_4[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_5[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_5[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_5[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_6[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_6[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_6[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_7[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_7[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_7[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_8[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_8[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_8[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_9[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_9[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_9[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_10[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_10[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_10[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                } else {
                    __Vtemp_1[1U] = 0U;
                    __Vtemp_1[2U] = 0U;
                    __Vtemp_2[0U] = 0U;
                    __Vtemp_2[1U] = 0U;
                    __Vtemp_3[1U] = 0U;
                    __Vtemp_3[2U] = 0U;
                    __Vtemp_4[0U] = 0U;
                    __Vtemp_4[1U] = 0U;
                    __Vtemp_5[1U] = 0U;
                    __Vtemp_6[0U] = 0U;
                    __Vtemp_7[1U] = 0U;
                    __Vtemp_7[2U] = 0U;
                    __Vtemp_8[0U] = 0U;
                    __Vtemp_8[1U] = 0U;
                    __Vtemp_9[1U] = 0U;
                    __Vtemp_10[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_1[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_1[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_2[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_2[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_3[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_3[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_4[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_4[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_5[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_6[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_7[2U] << 0x00000010U) 
                             | (__Vtemp_7[1U] >> 0x00000010U)) 
                            != ((__Vtemp_8[1U] << 0x00000018U) 
                                | (__Vtemp_8[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_9[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_10[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[0U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U]))) {
                    __Vtemp_11[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_11[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_11[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_12[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_12[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_12[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                } else {
                    __Vtemp_11[0U] = 0U;
                    __Vtemp_11[1U] = 0U;
                    __Vtemp_12[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[0U] 
                    = ((__Vtemp_11[1U] << 0x00000018U) 
                       | (__Vtemp_11[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[0U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[0U]));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[0U] 
                    = (0x000000ffU & __Vtemp_12[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U]))) {
                    __Vtemp_13[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_13[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_13[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_14[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_14[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_14[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                } else {
                    __Vtemp_13[1U] = 0U;
                    __Vtemp_13[2U] = 0U;
                    __Vtemp_14[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[0U] 
                    = ((__Vtemp_13[2U] << 0x00000010U) 
                       | (__Vtemp_13[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[0U] 
                    = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[0U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[0U] 
                    = (0x000000ffU & (__Vtemp_14[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[0U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[0U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[0U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[0U])) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[0U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[0U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[0U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[0U] 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[0U]), vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[0U]);
            __Vtemp_16[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[0U]);
            __Vtemp_16[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[0U] 
                                      >> 0x00000020U));
            __Vtemp_16[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_17, __Vtemp_16);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[0U] 
                = ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[0U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_17[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_17[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[0U]);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[0U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[0U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[0U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[0U]))));
        } else if ((0U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U] 
            = ((IData)(1U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])) {
            if ((1U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U]))) {
                    __Vtemp_19[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_19[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_19[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_20[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_20[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_20[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_21[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_21[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_21[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_22[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_22[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_22[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_23[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_23[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_23[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_24[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_24[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_24[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_25[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_25[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_25[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_26[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_26[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_26[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_27[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_27[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_27[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_28[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_28[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_28[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                } else {
                    __Vtemp_19[1U] = 0U;
                    __Vtemp_19[2U] = 0U;
                    __Vtemp_20[0U] = 0U;
                    __Vtemp_20[1U] = 0U;
                    __Vtemp_21[1U] = 0U;
                    __Vtemp_21[2U] = 0U;
                    __Vtemp_22[0U] = 0U;
                    __Vtemp_22[1U] = 0U;
                    __Vtemp_23[1U] = 0U;
                    __Vtemp_24[0U] = 0U;
                    __Vtemp_25[1U] = 0U;
                    __Vtemp_25[2U] = 0U;
                    __Vtemp_26[0U] = 0U;
                    __Vtemp_26[1U] = 0U;
                    __Vtemp_27[1U] = 0U;
                    __Vtemp_28[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_19[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_19[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_20[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_20[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_21[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_21[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_22[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_22[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_23[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_24[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_25[2U] << 0x00000010U) 
                             | (__Vtemp_25[1U] >> 0x00000010U)) 
                            != ((__Vtemp_26[1U] << 0x00000018U) 
                                | (__Vtemp_26[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_27[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_28[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[1U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U]))) {
                    __Vtemp_29[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_29[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_29[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_30[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_30[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_30[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                } else {
                    __Vtemp_29[0U] = 0U;
                    __Vtemp_29[1U] = 0U;
                    __Vtemp_30[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[1U] 
                    = ((__Vtemp_29[1U] << 0x00000018U) 
                       | (__Vtemp_29[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[1U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[1U]));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[1U] 
                    = (0x000000ffU & __Vtemp_30[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U]))) {
                    __Vtemp_31[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_31[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_31[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_32[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_32[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_32[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                } else {
                    __Vtemp_31[1U] = 0U;
                    __Vtemp_31[2U] = 0U;
                    __Vtemp_32[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[1U] 
                    = ((__Vtemp_31[2U] << 0x00000010U) 
                       | (__Vtemp_31[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[1U] 
                    = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[1U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[1U] 
                    = (0x000000ffU & (__Vtemp_32[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[1U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[1U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[1U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[1U])) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[1U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[1U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[1U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[1U] 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[1U]), vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[1U]);
            __Vtemp_34[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[1U]);
            __Vtemp_34[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[1U] 
                                      >> 0x00000020U));
            __Vtemp_34[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_35, __Vtemp_34);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[1U] 
                = ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[1U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_35[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_35[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[1U]);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[1U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[1U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[1U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[1U]))));
        } else if ((1U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U] 
            = ((IData)(2U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])) {
            if ((2U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U]))) {
                    __Vtemp_37[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_37[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_37[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_38[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_38[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_38[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_39[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_39[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_39[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_40[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_40[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_40[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_41[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_41[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_41[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_42[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_42[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_42[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_43[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_43[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_43[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_44[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_44[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_44[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_45[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_45[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_45[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_46[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_46[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_46[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                } else {
                    __Vtemp_37[1U] = 0U;
                    __Vtemp_37[2U] = 0U;
                    __Vtemp_38[0U] = 0U;
                    __Vtemp_38[1U] = 0U;
                    __Vtemp_39[1U] = 0U;
                    __Vtemp_39[2U] = 0U;
                    __Vtemp_40[0U] = 0U;
                    __Vtemp_40[1U] = 0U;
                    __Vtemp_41[1U] = 0U;
                    __Vtemp_42[0U] = 0U;
                    __Vtemp_43[1U] = 0U;
                    __Vtemp_43[2U] = 0U;
                    __Vtemp_44[0U] = 0U;
                    __Vtemp_44[1U] = 0U;
                    __Vtemp_45[1U] = 0U;
                    __Vtemp_46[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_37[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_37[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_38[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_38[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_39[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_39[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_40[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_40[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_41[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_42[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_43[2U] << 0x00000010U) 
                             | (__Vtemp_43[1U] >> 0x00000010U)) 
                            != ((__Vtemp_44[1U] << 0x00000018U) 
                                | (__Vtemp_44[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_45[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_46[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[2U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U]))) {
                    __Vtemp_47[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_47[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_47[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_48[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_48[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_48[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                } else {
                    __Vtemp_47[0U] = 0U;
                    __Vtemp_47[1U] = 0U;
                    __Vtemp_48[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[2U] 
                    = ((__Vtemp_47[1U] << 0x00000018U) 
                       | (__Vtemp_47[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[2U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[2U]));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[2U] 
                    = (0x000000ffU & __Vtemp_48[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U]))) {
                    __Vtemp_49[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_49[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_49[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_50[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_50[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_50[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                } else {
                    __Vtemp_49[1U] = 0U;
                    __Vtemp_49[2U] = 0U;
                    __Vtemp_50[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[2U] 
                    = ((__Vtemp_49[2U] << 0x00000010U) 
                       | (__Vtemp_49[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[2U] 
                    = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[2U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[2U] 
                    = (0x000000ffU & (__Vtemp_50[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[2U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[2U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[2U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[2U])) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[2U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[2U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[2U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[2U] 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[2U]), vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[2U]);
            __Vtemp_52[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[2U]);
            __Vtemp_52[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[2U] 
                                      >> 0x00000020U));
            __Vtemp_52[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_53, __Vtemp_52);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[2U] 
                = ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[2U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_53[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_53[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[2U]);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[2U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[2U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[2U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[2U]))));
        } else if ((2U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U] 
            = ((IData)(3U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])) {
            if ((3U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U]))) {
                    __Vtemp_55[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_55[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_55[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_56[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_56[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_56[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_57[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_57[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_57[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_58[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_58[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_58[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_59[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_59[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_59[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_60[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_60[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_60[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_61[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_61[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_61[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_62[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_62[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_62[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_63[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_63[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_63[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_64[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_64[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_64[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                } else {
                    __Vtemp_55[1U] = 0U;
                    __Vtemp_55[2U] = 0U;
                    __Vtemp_56[0U] = 0U;
                    __Vtemp_56[1U] = 0U;
                    __Vtemp_57[1U] = 0U;
                    __Vtemp_57[2U] = 0U;
                    __Vtemp_58[0U] = 0U;
                    __Vtemp_58[1U] = 0U;
                    __Vtemp_59[1U] = 0U;
                    __Vtemp_60[0U] = 0U;
                    __Vtemp_61[1U] = 0U;
                    __Vtemp_61[2U] = 0U;
                    __Vtemp_62[0U] = 0U;
                    __Vtemp_62[1U] = 0U;
                    __Vtemp_63[1U] = 0U;
                    __Vtemp_64[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_55[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_55[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_56[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_56[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_57[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_57[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_58[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_58[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_59[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_60[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_61[2U] << 0x00000010U) 
                             | (__Vtemp_61[1U] >> 0x00000010U)) 
                            != ((__Vtemp_62[1U] << 0x00000018U) 
                                | (__Vtemp_62[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_63[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_64[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[3U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U]))) {
                    __Vtemp_65[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_65[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_65[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_66[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_66[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_66[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                } else {
                    __Vtemp_65[0U] = 0U;
                    __Vtemp_65[1U] = 0U;
                    __Vtemp_66[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[3U] 
                    = ((__Vtemp_65[1U] << 0x00000018U) 
                       | (__Vtemp_65[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[3U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[3U]));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[3U] 
                    = (0x000000ffU & __Vtemp_66[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U]))) {
                    __Vtemp_67[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_67[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_67[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_68[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_68[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_68[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                } else {
                    __Vtemp_67[1U] = 0U;
                    __Vtemp_67[2U] = 0U;
                    __Vtemp_68[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[3U] 
                    = ((__Vtemp_67[2U] << 0x00000010U) 
                       | (__Vtemp_67[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[3U] 
                    = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[3U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[3U] 
                    = (0x000000ffU & (__Vtemp_68[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[3U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[3U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[3U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[3U])) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[3U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[3U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[3U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[3U] 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[3U]), vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[3U]);
            __Vtemp_70[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[3U]);
            __Vtemp_70[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[3U] 
                                      >> 0x00000020U));
            __Vtemp_70[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_71, __Vtemp_70);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[3U] 
                = ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[3U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_71[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_71[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[3U]);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[3U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[3U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[3U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[3U]))));
        } else if ((3U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U] 
            = ((IData)(4U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])) {
            if ((4U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U]))) {
                    __Vtemp_73[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_73[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_73[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_74[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_74[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_74[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_75[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_75[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_75[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_76[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_76[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_76[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_77[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_77[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_77[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_78[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_78[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_78[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_79[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_79[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_79[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_80[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_80[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_80[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_81[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_81[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_81[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_82[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_82[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_82[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                } else {
                    __Vtemp_73[1U] = 0U;
                    __Vtemp_73[2U] = 0U;
                    __Vtemp_74[0U] = 0U;
                    __Vtemp_74[1U] = 0U;
                    __Vtemp_75[1U] = 0U;
                    __Vtemp_75[2U] = 0U;
                    __Vtemp_76[0U] = 0U;
                    __Vtemp_76[1U] = 0U;
                    __Vtemp_77[1U] = 0U;
                    __Vtemp_78[0U] = 0U;
                    __Vtemp_79[1U] = 0U;
                    __Vtemp_79[2U] = 0U;
                    __Vtemp_80[0U] = 0U;
                    __Vtemp_80[1U] = 0U;
                    __Vtemp_81[1U] = 0U;
                    __Vtemp_82[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_73[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_73[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_74[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_74[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_75[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_75[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_76[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_76[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_77[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_78[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_79[2U] << 0x00000010U) 
                             | (__Vtemp_79[1U] >> 0x00000010U)) 
                            != ((__Vtemp_80[1U] << 0x00000018U) 
                                | (__Vtemp_80[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_81[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_82[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[4U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U]))) {
                    __Vtemp_83[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_83[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_83[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_84[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_84[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_84[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                } else {
                    __Vtemp_83[0U] = 0U;
                    __Vtemp_83[1U] = 0U;
                    __Vtemp_84[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[4U] 
                    = ((__Vtemp_83[1U] << 0x00000018U) 
                       | (__Vtemp_83[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[4U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[4U]));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[4U] 
                    = (0x000000ffU & __Vtemp_84[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U]))) {
                    __Vtemp_85[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_85[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_85[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_86[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_86[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_86[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                } else {
                    __Vtemp_85[1U] = 0U;
                    __Vtemp_85[2U] = 0U;
                    __Vtemp_86[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[4U] 
                    = ((__Vtemp_85[2U] << 0x00000010U) 
                       | (__Vtemp_85[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[4U] 
                    = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[4U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[4U] 
                    = (0x000000ffU & (__Vtemp_86[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[4U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[4U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[4U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[4U])) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[4U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[4U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[4U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[4U] 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[4U]), vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[4U]);
            __Vtemp_88[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[4U]);
            __Vtemp_88[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[4U] 
                                      >> 0x00000020U));
            __Vtemp_88[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_89, __Vtemp_88);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[4U] 
                = ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[4U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_89[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_89[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[4U]);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[4U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[4U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[4U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[4U]))));
        } else if ((4U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U] 
            = ((IData)(5U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])) {
            if ((5U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U]))) {
                    __Vtemp_91[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_91[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_91[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_92[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_92[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_92[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_93[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_93[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_93[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_94[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_94[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_94[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_95[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_95[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_95[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_96[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_96[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_96[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_97[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_97[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_97[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_98[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_98[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_98[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_99[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_99[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_99[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_100[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_100[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_100[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                } else {
                    __Vtemp_91[1U] = 0U;
                    __Vtemp_91[2U] = 0U;
                    __Vtemp_92[0U] = 0U;
                    __Vtemp_92[1U] = 0U;
                    __Vtemp_93[1U] = 0U;
                    __Vtemp_93[2U] = 0U;
                    __Vtemp_94[0U] = 0U;
                    __Vtemp_94[1U] = 0U;
                    __Vtemp_95[1U] = 0U;
                    __Vtemp_96[0U] = 0U;
                    __Vtemp_97[1U] = 0U;
                    __Vtemp_97[2U] = 0U;
                    __Vtemp_98[0U] = 0U;
                    __Vtemp_98[1U] = 0U;
                    __Vtemp_99[1U] = 0U;
                    __Vtemp_100[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_91[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_91[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_92[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_92[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_93[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_93[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_94[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_94[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_95[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_96[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_97[2U] << 0x00000010U) 
                             | (__Vtemp_97[1U] >> 0x00000010U)) 
                            != ((__Vtemp_98[1U] << 0x00000018U) 
                                | (__Vtemp_98[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_99[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_100[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[5U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U]))) {
                    __Vtemp_101[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_101[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_101[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_102[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_102[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_102[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                } else {
                    __Vtemp_101[0U] = 0U;
                    __Vtemp_101[1U] = 0U;
                    __Vtemp_102[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[5U] 
                    = ((__Vtemp_101[1U] << 0x00000018U) 
                       | (__Vtemp_101[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[5U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[5U]));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[5U] 
                    = (0x000000ffU & __Vtemp_102[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U]))) {
                    __Vtemp_103[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_103[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_103[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_104[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_104[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_104[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                } else {
                    __Vtemp_103[1U] = 0U;
                    __Vtemp_103[2U] = 0U;
                    __Vtemp_104[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[5U] 
                    = ((__Vtemp_103[2U] << 0x00000010U) 
                       | (__Vtemp_103[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[5U] 
                    = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[5U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[5U] 
                    = (0x000000ffU & (__Vtemp_104[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[5U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[5U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[5U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[5U])) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[5U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[5U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[5U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[5U] 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[5U]), vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[5U]);
            __Vtemp_106[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[5U]);
            __Vtemp_106[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[5U] 
                                       >> 0x00000020U));
            __Vtemp_106[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_107, __Vtemp_106);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[5U] 
                = ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[5U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_107[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_107[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[5U]);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[5U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[5U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[5U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[5U]))));
        } else if ((5U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U] 
            = ((IData)(6U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])) {
            if ((6U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U]))) {
                    __Vtemp_109[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_109[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_109[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_110[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_110[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_110[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_111[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_111[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_111[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_112[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_112[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_112[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_113[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_113[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_113[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_114[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_114[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_114[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_115[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_115[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_115[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_116[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_116[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_116[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_117[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_117[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_117[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_118[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_118[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_118[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                } else {
                    __Vtemp_109[1U] = 0U;
                    __Vtemp_109[2U] = 0U;
                    __Vtemp_110[0U] = 0U;
                    __Vtemp_110[1U] = 0U;
                    __Vtemp_111[1U] = 0U;
                    __Vtemp_111[2U] = 0U;
                    __Vtemp_112[0U] = 0U;
                    __Vtemp_112[1U] = 0U;
                    __Vtemp_113[1U] = 0U;
                    __Vtemp_114[0U] = 0U;
                    __Vtemp_115[1U] = 0U;
                    __Vtemp_115[2U] = 0U;
                    __Vtemp_116[0U] = 0U;
                    __Vtemp_116[1U] = 0U;
                    __Vtemp_117[1U] = 0U;
                    __Vtemp_118[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_109[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_109[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_110[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_110[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_111[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_111[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_112[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_112[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_113[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_114[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_115[2U] << 0x00000010U) 
                             | (__Vtemp_115[1U] >> 0x00000010U)) 
                            != ((__Vtemp_116[1U] << 0x00000018U) 
                                | (__Vtemp_116[0U] 
                                   >> 8U))) | ((0x000000ffU 
                                                & (__Vtemp_117[1U] 
                                                   >> 8U)) 
                                               != (0x000000ffU 
                                                   & __Vtemp_118[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[6U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U]))) {
                    __Vtemp_119[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_119[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_119[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_120[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_120[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_120[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                } else {
                    __Vtemp_119[0U] = 0U;
                    __Vtemp_119[1U] = 0U;
                    __Vtemp_120[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[6U] 
                    = ((__Vtemp_119[1U] << 0x00000018U) 
                       | (__Vtemp_119[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[6U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[6U]));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[6U] 
                    = (0x000000ffU & __Vtemp_120[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U]))) {
                    __Vtemp_121[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_121[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_121[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_122[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_122[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_122[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                } else {
                    __Vtemp_121[1U] = 0U;
                    __Vtemp_121[2U] = 0U;
                    __Vtemp_122[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[6U] 
                    = ((__Vtemp_121[2U] << 0x00000010U) 
                       | (__Vtemp_121[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[6U] 
                    = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[6U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[6U] 
                    = (0x000000ffU & (__Vtemp_122[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[6U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[6U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[6U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[6U])) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[6U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[6U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[6U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[6U] 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[6U]), vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[6U]);
            __Vtemp_124[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[6U]);
            __Vtemp_124[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[6U] 
                                       >> 0x00000020U));
            __Vtemp_124[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_125, __Vtemp_124);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[6U] 
                = ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[6U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_125[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_125[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[6U]);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[6U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[6U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[6U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[6U]))));
        } else if ((6U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U] 
            = ((IData)(7U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])) {
            if ((7U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U]))) {
                    __Vtemp_127[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_127[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_127[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_128[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_128[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_128[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_129[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_129[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_129[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_130[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_130[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_130[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_131[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_131[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_131[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_132[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_132[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_132[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_133[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_133[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_133[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_134[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_134[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_134[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_135[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_135[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_135[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_136[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_136[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_136[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                } else {
                    __Vtemp_127[1U] = 0U;
                    __Vtemp_127[2U] = 0U;
                    __Vtemp_128[0U] = 0U;
                    __Vtemp_128[1U] = 0U;
                    __Vtemp_129[1U] = 0U;
                    __Vtemp_129[2U] = 0U;
                    __Vtemp_130[0U] = 0U;
                    __Vtemp_130[1U] = 0U;
                    __Vtemp_131[1U] = 0U;
                    __Vtemp_132[0U] = 0U;
                    __Vtemp_133[1U] = 0U;
                    __Vtemp_133[2U] = 0U;
                    __Vtemp_134[0U] = 0U;
                    __Vtemp_134[1U] = 0U;
                    __Vtemp_135[1U] = 0U;
                    __Vtemp_136[0U] = 0U;
                }
                if (((((((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                            : 0U))) 
                           | (0U == ((__Vtemp_127[2U] 
                                      << 0x00000010U) 
                                     | (__Vtemp_127[1U] 
                                        >> 0x00000010U)))) 
                          | (0U == ((__Vtemp_128[1U] 
                                     << 0x00000018U) 
                                    | (__Vtemp_128[0U] 
                                       >> 8U)))) | 
                         (0x3fffffffU < ((__Vtemp_129[2U] 
                                          << 0x00000010U) 
                                         | (__Vtemp_129[1U] 
                                            >> 0x00000010U)))) 
                        | (0x3fffffffU < ((__Vtemp_130[1U] 
                                           << 0x00000018U) 
                                          | (__Vtemp_130[0U] 
                                             >> 8U)))) 
                       | (0x2fU < (0x000000ffU & (__Vtemp_131[1U] 
                                                  >> 8U)))) 
                      | (0x2fU < (0x000000ffU & __Vtemp_132[0U]))) 
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_133[2U] << 0x00000010U) 
                             | (__Vtemp_133[1U] >> 0x00000010U)) 
                            != ((__Vtemp_134[1U] << 0x00000018U) 
                                | (__Vtemp_134[0U] 
                                   >> 8U))) | ((0x000000ffU 
                                                & (__Vtemp_135[1U] 
                                                   >> 8U)) 
                                               != (0x000000ffU 
                                                   & __Vtemp_136[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[7U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U]))) {
                    __Vtemp_137[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_137[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_137[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_138[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_138[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_138[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                } else {
                    __Vtemp_137[0U] = 0U;
                    __Vtemp_137[1U] = 0U;
                    __Vtemp_138[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[7U] 
                    = ((__Vtemp_137[1U] << 0x00000018U) 
                       | (__Vtemp_137[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[7U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[7U]));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[7U] 
                    = (0x000000ffU & __Vtemp_138[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U]))) {
                    __Vtemp_139[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_139[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_139[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_140[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_140[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_140[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                } else {
                    __Vtemp_139[1U] = 0U;
                    __Vtemp_139[2U] = 0U;
                    __Vtemp_140[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[7U] 
                    = ((__Vtemp_139[2U] << 0x00000010U) 
                       | (__Vtemp_139[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[7U] 
                    = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[7U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[7U] 
                    = (0x000000ffU & (__Vtemp_140[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[7U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[7U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[7U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[7U])) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[7U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[7U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[7U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[7U] 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[7U]), vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[7U]);
            __Vtemp_142[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[7U]);
            __Vtemp_142[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[7U] 
                                       >> 0x00000020U));
            __Vtemp_142[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_143, __Vtemp_142);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[7U] 
                = ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[7U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_143[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_143[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[7U]);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[7U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[7U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[7U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[7U]))));
        } else if ((7U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
    } else {
        if ((0U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[1U] = 0U;
        if ((1U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[2U] = 0U;
        if ((2U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[3U] = 0U;
        if ((3U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[4U] = 0U;
        if ((4U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[5U] = 0U;
        if ((5U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[6U] = 0U;
        if ((6U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_index_for_lane[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value[7U] = 0U;
        if ((7U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_group_invalid = 1U;
        }
    }
    tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_plane_bytes 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_height)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width)));
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_rem = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y = 0ULL;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_in_bounds = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_offset = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_address_wide = 0ULL;
    if (((0ULL != tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_plane_bytes) 
         & (0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width))) {
        tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel 
            = (IData)(VL_DIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index)), tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_plane_bytes));
        tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_rem 
            = (IData)(VL_MODDIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index)), tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_plane_bytes));
        tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y 
            = VL_DIV_III(32, tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_rem, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width);
        tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x 
            = VL_MODDIV_III(32, tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_rem, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width);
        tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched))) 
                + (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_top_latched)));
        tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched))) 
                + (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_width_latched))));
        if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_in_bounds) {
            tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_offset 
                = (((((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_height_latched))) 
                     + tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_width_latched))) 
                   + tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_address_wide 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_base_latched)) 
                   + tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_offset);
        }
    }
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_area 
        = (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched 
           * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched);
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_y = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_x = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_y = 0ULL;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_x = 0ULL;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index_wide = 0ULL;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[0U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[1U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[2U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[3U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[3U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[3U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[3U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[4U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[4U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[4U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[4U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[5U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[5U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[5U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[5U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[6U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[6U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[6U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[6U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[7U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[7U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[7U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[7U] = 0ULL;
    if (((0U != tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_area) 
         & (0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width))) {
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel 
            = VL_DIV_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index, tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_area);
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y 
            = VL_DIV_III(32, VL_MODDIV_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index, tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_area), vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched);
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x 
            = VL_MODDIV_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched);
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_y 
            = VL_DIV_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width);
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_x 
            = VL_MODDIV_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width);
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_y 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched))) 
                 + ((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_y)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched)))) 
                + (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_top_latched)));
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_x 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched))) 
                 + ((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_x)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched)))) 
                + (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_left_latched)));
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_y, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_x, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_width_latched))));
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index_wide 
            = (((((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel)) 
                  * tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_plane_bytes) 
                 + ((((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_y)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched))) 
                     + (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y))) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width)))) 
                + ((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_x)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched)))) 
               + (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x)));
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index 
            = (IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index_wide);
        if ((0U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[0U] 
                = ((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[0U] 
                = ((0x8fffU >= (0x0000ffffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index)]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[0U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[0U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[0U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[0U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[0U])));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[0U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[0U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[0U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[0U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[0U])))));
            if (((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[0U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[0U])))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[0U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[0U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[0U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[0U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[0U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[0U] = 0ULL;
        }
        if ((1U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[1U] 
                = ((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[1U] 
                = ((0x8fffU >= (0x0000ffffU & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched 
                                    + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[1U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[1U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[1U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[1U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[1U])));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[1U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[1U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[1U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[1U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[1U])))));
            if (((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[1U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[1U])))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[1U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[1U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[1U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[1U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[1U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[1U] = 0ULL;
        }
        if ((2U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[2U] 
                = ((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[2U] 
                = ((0x8fffU >= (0x0000ffffU & ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched 
                                                << 1U) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched 
                                     << 1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[2U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[2U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[2U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[2U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[2U])));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[2U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[2U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[2U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[2U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[2U])))));
            if (((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[2U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[2U])))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[2U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[2U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[2U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[2U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[2U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[2U] = 0ULL;
        }
        if ((3U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[3U] 
                = ((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[3U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(3U) 
                                                * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & (((IData)(3U) * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[3U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[3U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[3U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[3U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[3U])));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[3U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[3U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[3U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[3U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[3U])))));
            if (((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[3U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[3U])))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[3U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[3U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[3U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[3U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[3U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[3U] = 0ULL;
        }
        if ((4U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[4U] 
                = ((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[4U] 
                = ((0x8fffU >= (0x0000ffffU & ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched 
                                                << 2U) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched 
                                     << 2U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[4U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[4U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[4U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[4U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[4U])));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[4U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[4U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[4U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[4U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[4U])))));
            if (((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[4U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[4U])))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[4U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[4U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[4U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[4U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[4U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[4U] = 0ULL;
        }
        if ((5U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[5U] 
                = ((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[5U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(5U) 
                                                * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & (((IData)(5U) * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[5U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[5U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[5U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[5U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[5U])));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[5U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[5U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[5U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[5U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[5U])))));
            if (((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[5U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[5U])))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[5U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[5U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[5U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[5U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[5U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[5U] = 0ULL;
        }
        if ((6U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[6U] 
                = ((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[6U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(6U) 
                                                * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & (((IData)(6U) * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[6U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[6U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[6U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[6U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[6U])));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[6U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[6U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[6U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[6U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[6U])))));
            if (((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[6U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[6U])))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[6U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[6U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[6U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[6U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[6U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[6U] = 0ULL;
        }
        if ((7U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[7U] 
                = ((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[7U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(7U) 
                                                * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & (((IData)(7U) * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[7U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[7U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[7U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[7U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[7U])));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[7U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[7U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[7U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[7U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[7U])))));
            if (((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[7U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[7U])))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[7U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[7U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[7U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[7U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[7U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[7U] = 0ULL;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_rstrb = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_wstrb = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_valid = 0U;
    if ((1U & ((~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__hard_reset)) 
               & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__abort))))) {
        if (((4U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_rstrb 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_valid = 1U;
        } else if ((0x0fU == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write = 1U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_valid = 1U;
        }
        if ((1U & (~ ((4U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
                      || (8U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)))))) {
            if ((0x0fU == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_wstrb 
                    = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched;
            }
        }
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_base_latched)) 
           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_byte_offset_wide);
}
