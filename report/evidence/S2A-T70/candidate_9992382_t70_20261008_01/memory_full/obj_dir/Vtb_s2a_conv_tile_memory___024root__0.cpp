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
extern const VlWide<10>/*319:0*/ Vtb_s2a_conv_tile_memory__ConstPool__CONST_hb4617e49_0;
extern const VlUnpacked<IData/*31:0*/, 5> Vtb_s2a_conv_tile_memory__ConstPool__TABLE_hc6a14c36_0;

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
    IData/*31:0*/ __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__n;
    __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__n = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3____VlefCall_0__pattern;
    __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3____VlefCall_0__pattern = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__r;
    __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__r = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__v;
    __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__v = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__4__Vfuncout;
    __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__4__Vfuncout = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__4__n;
    __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__4__n = 0;
    IData/*31:0*/ __Vtemp_4;
    IData/*31:0*/ __Vtemp_5;
    IData/*31:0*/ __Vtemp_6;
    // Body
    tb_s2a_conv_tile_memory__DOT____VlemExpr_0 = VL_VALUEPLUSARGS_INI(32, "CASES=%d"s, 
                                                                      vlSelfRef.tb_s2a_conv_tile_memory__DOT__required_cases);
    if (VL_UNLIKELY((((! tb_s2a_conv_tile_memory__DOT____VlemExpr_0) 
                      || VL_GTES_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__required_cases))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:143: Assertion failed in %m: \345\277\205\351\241\273\347\273\231\345\256\232cases\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 143, "", false);
    }
    tb_s2a_conv_tile_memory__DOT__fd = VL_FOPEN_NN("cases.bin"s
                                                   , "rb"s);
    ;
    if (VL_UNLIKELY(((0U == tb_s2a_conv_tile_memory__DOT__fd)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:144: Assertion failed in %m: fixture\347\274\272\345\244\261\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 144, "", false);
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
                                                             145);
        tb_s2a_conv_tile_memory__DOT__unnamedblk1_1__DOT____Vrepeat0 
            = (tb_s2a_conv_tile_memory__DOT__unnamedblk1_1__DOT____Vrepeat0 
               - (IData)(1U));
    }
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "source\\tb_s2a_conv_tile_memory.sv", 
                                         145);
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
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:148: Assertion failed in %m: \346\210\252\346\226\255header\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 148, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__b 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[0U] 
                = (vlSelfRef.tb_s2a_conv_tile_memory__DOT__hdr[0U] 
                   | (0x00ff0000U & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__b 
                                     << 0x00000010U)));
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 3U;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:148: Assertion failed in %m: \346\210\252\346\226\255header\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 148, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__b 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:148: Assertion failed in %m: \346\210\252\346\226\255header\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 148, "", false);
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
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
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
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
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
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
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
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
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
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
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
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
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
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
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
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
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
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
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
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
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
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
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
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v = 0;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value = 0U;
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                = (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
            }
            __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v 
                = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_memory__DOT__read_word__1__v)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:80: Assertion failed in %m: \346\210\252\346\226\255fixture\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory.read_word", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 80, "", false);
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
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:152: Assertion failed in %m: fixture\345\260\272\345\257\270\351\235\236\346\263\225\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 152, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 0U;
            while (VL_LTS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__i, 
                              VL_MULS_III(32, VL_MULS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__ci, vlSelfRef.tb_s2a_conv_tile_memory__DOT__ph), vlSelfRef.tb_s2a_conv_tile_memory__DOT__pw))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__b 
                    = (tb_s2a_conv_tile_memory__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_memory__DOT__fd)) : -1);
                if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__b)))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:153: Assertion failed in %m: \346\210\252\346\226\255patch\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 153, "", false);
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
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:154: Assertion failed in %m: \346\210\252\346\226\255weight\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 154, "", false);
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
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:155: Assertion failed in %m: \346\210\252\346\226\255golden\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 155, "", false);
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
                                                                 160);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "source\\tb_s2a_conv_tile_memory.sv", 
                                                 160);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__start_valid = 1U;
            Vtb_s2a_conv_tile_memory___024root____VbeforeTrig_hb8586161__0(vlSelf, 
                                                                           "@(negedge tb_s2a_conv_tile_memory.clk)");
            co_await vlSelfRef.__VtrigSched_hb8586161__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_s2a_conv_tile_memory.clk)", 
                                                                 "source\\tb_s2a_conv_tile_memory.sv", 
                                                                 161);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "source\\tb_s2a_conv_tile_memory.sv", 
                                                 161);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__start_valid = 0U;
            Vtb_s2a_conv_tile_memory___024root____VbeforeTrig_hb8586161__0(vlSelf, 
                                                                           "@(negedge tb_s2a_conv_tile_memory.clk)");
            co_await vlSelfRef.__VtrigSched_hb8586161__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_s2a_conv_tile_memory.clk)", 
                                                                 "source\\tb_s2a_conv_tile_memory.sv", 
                                                                 162);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "source\\tb_s2a_conv_tile_memory.sv", 
                                                 162);
            if (VL_UNLIKELY(((2U != (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:163: Assertion failed in %m: \347\234\237\345\256\236descriptor\350\242\253\346\213\222\347\273\235\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 163, "", false);
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
                                                                     167);
                co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                     nullptr, 
                                                     "source\\tb_s2a_conv_tile_memory.sv", 
                                                     167);
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__cycles 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__cycles);
                if (VL_UNLIKELY((((0x13U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
                                  | VL_LTS_III(32, 0x000f4240U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__cycles))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:168: Assertion failed in %m: patch\345\212\240\350\275\275\345\244\261\350\264\245/\350\266\205\346\227\266\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 168, "", false);
                }
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__group_base;
            while ((0x12U != (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                Vtb_s2a_conv_tile_memory___024root____VbeforeTrig_hb8586161__0(vlSelf, 
                                                                               "@(negedge tb_s2a_conv_tile_memory.clk)");
                co_await vlSelfRef.__VtrigSched_hb8586161__0.trigger(0U, 
                                                                     nullptr, 
                                                                     "@(negedge tb_s2a_conv_tile_memory.clk)", 
                                                                     "source\\tb_s2a_conv_tile_memory.sv", 
                                                                     172);
                co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                     nullptr, 
                                                     "source\\tb_s2a_conv_tile_memory.sv", 
                                                     172);
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__cycles 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__cycles);
                if (VL_UNLIKELY((((0x13U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
                                  | VL_LTS_III(32, 0x001e8480U, vlSelfRef.tb_s2a_conv_tile_memory__DOT__cycles))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:173: Assertion failed in %m: tile\346\211\247\350\241\214\345\244\261\350\264\245/\350\266\205\346\227\266 error=%0d\n",4, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '#',3,(IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 173, "", false);
                }
            }
            if (VL_UNLIKELY(((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__seen_count 
                                != vlSelfRef.tb_s2a_conv_tile_memory__DOT__outputs) 
                               | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__actual_features 
                                  != vlSelfRef.tb_s2a_conv_tile_memory__DOT__expected_reads)) 
                              | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__actual_weights 
                                 != VL_MULS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__lanes, vlSelfRef.tb_s2a_conv_tile_memory__DOT__k)))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:176: Assertion failed in %m: \344\274\240\350\276\223\350\256\241\346\225\260\344\270\215\345\256\214\346\225\264 got=%0d/%0d/%0d expected=%0d/%0d/%0d\n",9, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__seen_count
                             , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__actual_features
                             , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__actual_weights
                             , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__outputs
                             , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__expected_reads
                             , '~',32,VL_MULS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__lanes, vlSelfRef.tb_s2a_conv_tile_memory__DOT__k));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 176, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 0U;
            __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__n 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__counts[0U];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT____VlemCall_2__stall_total = 0;
            __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__r = 0;
            __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__v = 0;
            __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__v 
                = VL_MULS_III(32, (IData)(0x0000000dU), 
                              VL_DIVS_III(32, __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__n, (IData)(5U)));
            __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__r = 0U;
            while (VL_LTS_III(32, __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__r, 
                              VL_MODDIVS_III(32, __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__n, (IData)(5U)))) {
                __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__4__n 
                    = __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__r;
                __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__4__Vfuncout = 0;
                __Vtemp_4 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__4__n, (IData)(5U)), Vtb_s2a_conv_tile_memory__ConstPool__CONST_hb4617e49_0);
                __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__4__Vfuncout 
                    = Vtb_s2a_conv_tile_memory__ConstPool__TABLE_hc6a14c36_0
                    [__Vtemp_4];
                __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3____VlefCall_0__pattern 
                    = __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__4__Vfuncout;
                __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__v 
                    = (__Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__v 
                       + __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3____VlefCall_0__pattern);
                __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__r 
                    = ((IData)(1U) + __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__r);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT____VlemCall_2__stall_total 
                = __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__v;
            if (VL_UNLIKELY(((vlSelfRef.tb_s2a_conv_tile_memory__DOT__stalls[0U] 
                              != vlSelfRef.tb_s2a_conv_tile_memory__DOT____VlemCall_2__stall_total)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:177: Assertion failed in %m: \345\233\272\345\256\232stall\346\200\273\346\225\260\344\270\215\347\254\246\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 177, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 1U;
            __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__n 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__counts[1U];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT____VlemCall_2__stall_total = 0;
            __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__r = 0;
            __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__v = 0;
            __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__v 
                = VL_MULS_III(32, (IData)(0x0000000dU), 
                              VL_DIVS_III(32, __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__n, (IData)(5U)));
            __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__r = 0U;
            while (VL_LTS_III(32, __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__r, 
                              VL_MODDIVS_III(32, __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__n, (IData)(5U)))) {
                __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__4__n 
                    = __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__r;
                __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__4__Vfuncout = 0;
                __Vtemp_5 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__4__n, (IData)(5U)), Vtb_s2a_conv_tile_memory__ConstPool__CONST_hb4617e49_0);
                __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__4__Vfuncout 
                    = Vtb_s2a_conv_tile_memory__ConstPool__TABLE_hc6a14c36_0
                    [__Vtemp_5];
                __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3____VlefCall_0__pattern 
                    = __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__4__Vfuncout;
                __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__v 
                    = (__Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__v 
                       + __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3____VlefCall_0__pattern);
                __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__r 
                    = ((IData)(1U) + __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__r);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT____VlemCall_2__stall_total 
                = __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__v;
            if (VL_UNLIKELY(((vlSelfRef.tb_s2a_conv_tile_memory__DOT__stalls[1U] 
                              != vlSelfRef.tb_s2a_conv_tile_memory__DOT____VlemCall_2__stall_total)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:177: Assertion failed in %m: \345\233\272\345\256\232stall\346\200\273\346\225\260\344\270\215\347\254\246\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 177, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 2U;
            __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__n 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__counts[2U];
            vlSelfRef.tb_s2a_conv_tile_memory__DOT____VlemCall_2__stall_total = 0;
            __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__r = 0;
            __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__v = 0;
            __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__v 
                = VL_MULS_III(32, (IData)(0x0000000dU), 
                              VL_DIVS_III(32, __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__n, (IData)(5U)));
            __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__r = 0U;
            while (VL_LTS_III(32, __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__r, 
                              VL_MODDIVS_III(32, __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__n, (IData)(5U)))) {
                __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__4__n 
                    = __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__r;
                __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__4__Vfuncout = 0;
                __Vtemp_6 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__4__n, (IData)(5U)), Vtb_s2a_conv_tile_memory__ConstPool__CONST_hb4617e49_0);
                __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__4__Vfuncout 
                    = Vtb_s2a_conv_tile_memory__ConstPool__TABLE_hc6a14c36_0
                    [__Vtemp_6];
                __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3____VlefCall_0__pattern 
                    = __Vfunc_tb_s2a_conv_tile_memory__DOT__pattern__4__Vfuncout;
                __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__v 
                    = (__Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__v 
                       + __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3____VlefCall_0__pattern);
                __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__r 
                    = ((IData)(1U) + __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__r);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT____VlemCall_2__stall_total 
                = __Vfunc_tb_s2a_conv_tile_memory__DOT__stall_total__3__v;
            if (VL_UNLIKELY(((vlSelfRef.tb_s2a_conv_tile_memory__DOT__stalls[2U] 
                              != vlSelfRef.tb_s2a_conv_tile_memory__DOT____VlemCall_2__stall_total)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:177: Assertion failed in %m: \345\233\272\345\256\232stall\346\200\273\346\225\260\344\270\215\347\254\246\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 177, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 3U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__i = 0U;
            while (VL_LTS_III(32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__i, vlSelfRef.tb_s2a_conv_tile_memory__DOT__outputs)) {
                if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__seen
                                                  [
                                                  (0x000001ffU 
                                                   & vlSelfRef.tb_s2a_conv_tile_memory__DOT__i)])))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:178: Assertion failed in %m: \347\274\272\350\276\223\345\207\272\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 178, "", false);
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
                                                                 179);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "source\\tb_s2a_conv_tile_memory.sv", 
                                                 179);
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__abort = 0U;
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "source\\tb_s2a_conv_tile_memory.sv", 
                                                 179);
            if (VL_UNLIKELY(((1U & (~ ((~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__cancel)) 
                                       & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)))))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:180: Assertion failed in %m: \345\217\226\346\266\210\346\234\252\346\201\242\345\244\215\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 180, "", false);
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
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:184: Assertion failed in %m: \347\224\250\344\276\213\346\225\260\344\270\215\345\256\214\346\225\264\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 184, "", false);
    }
    VL_WRITEF_NX("PASS TILE_MEMORY cases=%0d outputs=%0d\n",2
                 , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__case_count
                 , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__total_outputs);
    VL_FINISH_MT("source\\tb_s2a_conv_tile_memory.sv", 185, "");
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
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_offset;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_offset = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_area;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_area = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_input_channel;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_input_channel = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_kernel_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_kernel_y = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_reduction_index;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_reduction_index = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_y = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_x;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_x = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_channel;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_channel = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_y = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_x;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_x = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_y = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_x;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_x = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_feature_index_wide;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_feature_index_wide = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index = 0;
    // Body
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_valid = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_rstrb = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_wstrb = 0U;
    if ((1U & ((~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__hard_reset)) 
               & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__abort))))) {
        if (((4U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_valid = 1U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_rstrb 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched;
        } else if ((0x10U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write = 1U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_valid = 1U;
        }
        if ((1U & (~ ((4U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
                      || (8U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)))))) {
            if ((0x10U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
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
        = ((QData)((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_x 
                            + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x))) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched)) 
              * ((QData)((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_y 
                                  + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y))) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index)))))));
    tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_bias = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_invalid = 0U;
    if (((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane 
          < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count) 
         & (0x00000026U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))) {
        tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index 
            = ((((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                  : 0U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base) 
               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane);
        if ((0x00000c5cU > tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index)) {
            if ((0x0c5bU >= (0x00000fffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[0U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index)][0U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index)][1U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[2U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index)][2U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_bias 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                    [(0x00000fffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index)];
            } else {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[0U] = 0U;
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] = 0U;
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[2U] = 0U;
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_bias = 0U;
            }
            if (((((((((tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index 
                        >= (((0x25U >= (0x0000003fU 
                                        & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                             [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                              : 0U) + ((0x25U >= (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                       [(0x0000003fU 
                                         & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                        : 0U))) | (0U 
                                                   == 
                                                   ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[2U] 
                                                     << 0x00000010U) 
                                                    | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                                       >> 0x00000010U)))) 
                      | (0U == ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                 << 0x00000018U) | 
                                (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[0U] 
                                 >> 8U)))) | (0x3fffffffU 
                                              < ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[2U] 
                                                  << 0x00000010U) 
                                                 | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                                    >> 0x00000010U)))) 
                    | (0x3fffffffU < ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                       << 0x00000018U) 
                                      | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[0U] 
                                         >> 8U)))) 
                   | (0x2fU < (0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                              >> 8U)))) 
                  | (0x2fU < (0x000000ffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[0U]))) 
                 | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched)) 
                    & ((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[2U] 
                          << 0x00000010U) | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                             >> 0x00000010U)) 
                        != ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                             << 0x00000018U) | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[0U] 
                                                >> 8U))) 
                       | ((0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                          >> 8U)) != 
                          (0x000000ffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[0U])))))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_invalid = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_invalid = 1U;
        }
    } else if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane 
                < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_invalid = 1U;
    }
    tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_plane_bytes 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_height)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width)));
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y = 0ULL;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_in_bounds = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_advance = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_offset = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_address_wide = 0ULL;
    if (((0ULL != tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_plane_bytes) 
         & (0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width))) {
        tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_top_latched)));
        tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_width_latched))));
        if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_in_bounds) {
            tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_offset 
                = (((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel)) 
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
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_input_channel 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_kernel_y 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_reduction_index 
        = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index);
    if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x) 
         >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_kernel_x = 0U;
        if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y) 
             >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched)) {
            tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_kernel_y = 0U;
            tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_input_channel 
                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel);
        } else {
            tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_kernel_y 
                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y);
        }
    } else {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_kernel_x 
            = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x);
    }
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_y 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_x 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_channel 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_y 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_x 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_y = 0ULL;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_x = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_tap_in_bounds = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_feature_index_wide = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_feature_index = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_enable = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[0U] = 0ULL;
    if ((0U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[0U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[0U] 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[0U];
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
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[0U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[0U])))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[0U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[0U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[1U] = 0ULL;
    if ((1U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[1U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[1U] 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[1U];
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
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[1U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[1U])))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[1U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[1U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[2U] = 0ULL;
    if ((2U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[2U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[2U] 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[2U];
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
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[2U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[2U])))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[2U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[2U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[3U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[3U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[3U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[3U] = 0ULL;
    if ((3U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[3U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[3U] 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[3U];
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
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[3U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[3U])))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[3U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[3U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[4U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[4U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[4U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[4U] = 0ULL;
    if ((4U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[4U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[4U] 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[4U];
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
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[4U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[4U])))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[4U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[4U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[5U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[5U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[5U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[5U] = 0ULL;
    if ((5U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[5U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[5U] 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[5U];
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
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[5U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[5U])))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[5U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[5U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[6U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[6U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[6U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[6U] = 0ULL;
    if ((6U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[6U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[6U] 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[6U];
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
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[6U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[6U])))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[6U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[6U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[7U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[7U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[7U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[7U] = 0ULL;
    if ((7U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[7U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[7U] 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[7U];
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
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[7U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[7U])))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[7U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[7U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    if (((0x0bU == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
         | (0x0cU == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)))) {
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_y 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_y;
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_x 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x;
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_channel = 0U;
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_y = 0U;
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_x = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_enable = 1U;
    } else if ((0x0dU == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
        if ((((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index) 
               < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched) 
              & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument))) 
             & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow)))) {
            tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_y 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_y;
            tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_x 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x;
            tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_channel 
                = tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_input_channel;
            tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_y 
                = tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_kernel_y;
            tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_x 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_kernel_x;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index 
                = tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_reduction_index;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_enable = 1U;
        }
    }
    if (((0U != tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_area) 
         & (0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width))) {
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_y 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched))) 
                 + ((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_y)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched)))) 
                + (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_top_latched)));
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_x 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched))) 
                 + ((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_x)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched)))) 
                + (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_tap_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_y, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_x, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_width_latched))));
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_feature_index_wide 
            = (((((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_channel)) 
                  * tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_plane_bytes) 
                 + ((((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_y)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched))) 
                     + (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_y))) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width)))) 
                + ((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_x)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched)))) 
               + (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_x)));
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_feature_index 
            = (IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_feature_index_wide);
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mapped_response_error = 0U;
    if ((((3U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
          & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index 
             < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_byte_count)) 
         & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_in_bounds)))) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_advance = 1U;
    } else if ((((5U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
                 & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_valid)) 
                & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mapped_response_error)))) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_advance = 1U;
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
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_shape_span;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_shape_span = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_shape_span;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_shape_span = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_shape_product;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_shape_product = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_shape_product;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_shape_product = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_span_plus_stride;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_span_plus_stride = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_span_plus_stride;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_span_plus_stride = 0;
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_height_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_height_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_width_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_width_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_bytes_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_bytes_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__full_weight_group_bytes_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_weight_group_bytes_wide);
    VlWide<3>/*79:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_parameter;
    VL_ZERO_W(80, tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_parameter);
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_accumulator;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_accumulator = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value = 0;
    CData/*4:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0;
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
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_height;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_height = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_byte_count;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_byte_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_point_count;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_point_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_y;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_y;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_x;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v0;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v8;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v8 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0 = 0;
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
    VlWide<3>/*79:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v16;
    VL_ZERO_W(80, __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v16);
    CData/*2:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v16;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v16 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v16;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v16 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias__v16;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias__v16 = 0;
    CData/*2:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias__v16;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias__v16 = 0;
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
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v0;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v0 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v1;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v1;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v1 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v2;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v2 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v3;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v3 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v3;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v3 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v4;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v4 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v5;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v5 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v5;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v5 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v6;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v6 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v7;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v7 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v7;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v7 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v8;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v8 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v9;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v9 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v9;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v9 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v10;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v10 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v11;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v11 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v11;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v11 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v12;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v12 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v13;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v13 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v13;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v13 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v14;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v14 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v15;
    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v15 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v15;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v15 = 0;
    VlWide<4>/*127:0*/ __Vtemp_2;
    VlWide<3>/*95:0*/ __Vtemp_20;
    VlWide<3>/*95:0*/ __Vtemp_21;
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
    VlWide<4>/*127:0*/ __Vtemp_55;
    VlWide<4>/*127:0*/ __Vtemp_56;
    VlWide<4>/*127:0*/ __Vtemp_57;
    VlWide<4>/*127:0*/ __Vtemp_58;
    VlWide<4>/*127:0*/ __Vtemp_59;
    VlWide<4>/*127:0*/ __Vtemp_60;
    VlWide<4>/*127:0*/ __Vtemp_61;
    VlWide<4>/*127:0*/ __Vtemp_62;
    VlWide<4>/*127:0*/ __Vtemp_63;
    VlWide<4>/*127:0*/ __Vtemp_65;
    VlWide<4>/*127:0*/ __Vtemp_66;
    VlWide<4>/*127:0*/ __Vtemp_67;
    VlWide<4>/*127:0*/ __Vtemp_68;
    VlWide<4>/*127:0*/ __Vtemp_69;
    VlWide<4>/*127:0*/ __Vtemp_70;
    VlWide<4>/*127:0*/ __Vtemp_71;
    VlWide<4>/*127:0*/ __Vtemp_72;
    VlWide<4>/*127:0*/ __Vtemp_73;
    VlWide<4>/*127:0*/ __Vtemp_74;
    VlWide<4>/*127:0*/ __Vtemp_75;
    VlWide<4>/*127:0*/ __Vtemp_76;
    VlWide<4>/*127:0*/ __Vtemp_77;
    VlWide<4>/*127:0*/ __Vtemp_78;
    // Body
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v1 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v2 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v3 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v4 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v5 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v6 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v7 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v8 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v9 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v10 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v11 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v12 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v13 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v14 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v15 = 0U;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_height 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_height;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_point_count 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_point_count;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v1 = 0U;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_y 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_y;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_x 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_x;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v8 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v16 = 0U;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_height 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_height;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_byte_count 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_byte_count;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_y 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_y;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched;
    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state;
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
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0U;
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
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:111: Assertion failed in %m: \351\235\236\346\263\225word/strobe\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 111, "", false);
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
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:118: Assertion failed in %m: \350\276\223\345\207\272\345\234\260\345\235\200\344\270\215\345\234\250\346\211\200\351\200\211tile/group\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 118, "", false);
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
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:121: Assertion failed in %m: \350\276\223\345\207\272\344\270\215\347\254\246/\351\207\215\345\244\215 layer=%0d case=%0d idx=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id
                             , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__ordinal
                             , '~',32,vlSelfRef.tb_s2a_conv_tile_memory__DOT__idx);
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 121, "", false);
            }
            if (VL_UNLIKELY(((0U != (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_wdata_latched 
                                     & (~ VL_SHIFTL_III(32,32,32, (IData)(0x000000ffU), 
                                                        VL_MULS_III(32, (IData)(8U), vlSelfRef.tb_s2a_conv_tile_memory__DOT__selected_lane)))))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:122: Assertion failed in %m: \346\234\252\351\200\211write lane\351\235\236\351\233\266\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 122, "", false);
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
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:130: Assertion failed in %m: feature\345\234\260\345\235\200\350\266\205patch\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 130, "", false);
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
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:135: Assertion failed in %m: GF8\345\234\260\345\235\200\350\266\212\347\273\204\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 135, "", false);
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
    if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__hard_reset) 
         | (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__abort))) {
        __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v0 = 1U;
        __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v2 = 1U;
        __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v4 = 1U;
        __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v6 = 1U;
        __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v8 = 1U;
        __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v10 = 1U;
        __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v12 = 1U;
        __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v14 = 1U;
    } else {
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_enable) 
             & (0U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v1 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v1 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_enable) 
             & (1U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v3 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v3 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_enable) 
             & (2U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v5 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v5 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_enable) 
             & (3U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v7 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v7 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_enable) 
             & (4U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v9 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v9 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_enable) 
             & (5U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v11 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v11 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_enable) 
             & (6U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v13 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v13 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_enable) 
             & (7U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v15 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v15 = 1U;
        }
    }
    if ((1U & (~ ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__hard_reset) 
                  | (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__abort))))) {
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mapped_response_error))) 
              & (0U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mapped_response_error))) 
              & (1U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mapped_response_error))) 
              & (2U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mapped_response_error))) 
              & (3U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mapped_response_error))) 
              & (4U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mapped_response_error))) 
              & (5U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mapped_response_error))) 
              & (6U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mapped_response_error))) 
              & (7U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
    }
    if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__hard_reset) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched = 0U;
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
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_height = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_byte_count = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_point_count = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_y = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_y = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_x = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_address_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_wdata_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 0U;
        __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v0 = 1U;
    } else if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__abort) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_y = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_y = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_x = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane = 0U;
        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_wdata_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 0U;
        __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v8 = 1U;
    } else {
        if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_enable) {
            if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_tap_in_bounds) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds = 1U;
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data 
                    = ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_feature_index)]
                        : 0U);
            } else {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds = 0U;
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data = 0U;
            }
        }
        if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_advance) {
            if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x) 
                 >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width)) {
                if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y) 
                     >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_height)) {
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel);
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y = 0U;
                } else {
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y);
                }
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x = 0U;
            } else {
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x);
            }
        }
        if ((0x00000010U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
            if ((8U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 6U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x13U;
            } else if ((4U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 6U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x13U;
            } else if ((2U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                if ((1U & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)))) {
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
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x13U;
                    }
                }
            } else if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_valid) {
                    if ((0U != (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mapped_response_error))) {
                        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched 
                            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mapped_response_error;
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x13U;
                    } else {
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index);
                        if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_x) 
                             >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width)) {
                            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_y 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_y);
                            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_x = 0U;
                        } else {
                            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_x 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_x);
                        }
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x0fU;
                    }
                }
            } else if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_valid) 
                        & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_ready))) {
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x11U;
            }
        } else if ((8U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
            if ((4U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                if ((2U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                    if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                        if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index 
                             >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x12U;
                        } else if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index 
                                    >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_point_count)) {
                            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index);
                            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index = 0U;
                            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_y = 0U;
                            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_x = 0U;
                        } else {
                            __Vtemp_2[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_byte_offset_wide);
                            __Vtemp_2[1U] = (IData)(
                                                    (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_byte_offset_wide 
                                                     >> 0x00000020U));
                            __Vtemp_2[2U] = 0U;
                            __Vtemp_2[3U] = 0U;
                            if (((0x00000000ffffffffULL 
                                  < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_address_wide) 
                                 | VL_GTE_W(4, __Vtemp_2, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_elements_wide))) {
                                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 2U;
                                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x13U;
                            } else {
                                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_address_latched 
                                    = ((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_address_wide 
                                                >> 2U)) 
                                       << 2U);
                                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched 
                                    = (0x0000000fU 
                                       & ((IData)(1U) 
                                          << (3U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_address_wide))));
                                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_wdata_latched 
                                    = VL_SHIFTL_III(32,32,32, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block
                                                    [
                                                    (0x000001ffU 
                                                     & ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index 
                                                         << 6U) 
                                                        + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index))], 
                                                    (0x00000018U 
                                                     & ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_address_wide) 
                                                        << 3U)));
                                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x10U;
                            }
                        }
                    } else {
                        if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index 
                             < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0 
                                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value;
                            __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0 
                                = (0x000001ffU & ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index 
                                                   << 6U) 
                                                  + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index));
                            __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0 = 1U;
                        }
                        if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index) 
                             >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                            if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index) 
                                 >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_point_count)) {
                                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index = 0U;
                                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index = 0U;
                                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_y = 0U;
                                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_x = 0U;
                                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x0fU;
                            } else {
                                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index 
                                    = ((IData)(1U) 
                                       + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index);
                                if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x) 
                                     >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width)) {
                                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_y 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_y);
                                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x = 0U;
                                } else {
                                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x);
                                }
                                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index = 0U;
                                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x0cU;
                            }
                        } else {
                            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index);
                        }
                    }
                } else if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                    if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument) {
                        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 1U;
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x13U;
                    } else if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow) {
                        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 7U;
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x13U;
                    } else {
                        if ((0U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v0 
                                = (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[0U]);
                            __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v0 = 1U;
                        }
                        if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index) 
                             >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched)) {
                            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index = 0U;
                            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x0eU;
                        } else {
                            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index);
                            if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x) 
                                 >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched)) {
                                if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y) 
                                     >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched)) {
                                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel);
                                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y = 0U;
                                } else {
                                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y);
                                }
                                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x = 0U;
                            } else {
                                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x 
                                    = ((IData)(1U) 
                                       + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x);
                            }
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
                } else {
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel = 0U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y = 0U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x = 0U;
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v8 
                        = ((0U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[0U]
                            : 0U);
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v8 = 1U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index = 0U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x0dU;
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v9 
                        = ((1U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[1U]
                            : 0U);
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v9 = 1U;
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v10 
                        = ((2U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[2U]
                            : 0U);
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v11 
                        = ((3U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[3U]
                            : 0U);
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v12 
                        = ((4U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[4U]
                            : 0U);
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v13 
                        = ((5U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[5U]
                            : 0U);
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v14 
                        = ((6U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[6U]
                            : 0U);
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v15 
                        = ((7U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[7U]
                            : 0U);
                }
            } else if ((2U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel = 0U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y = 0U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x = 0U;
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v16 
                        = ((0U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[0U]
                            : 0U);
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v16 = 1U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index = 0U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index = 0U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x0dU;
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v17 
                        = ((1U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[1U]
                            : 0U);
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v17 = 1U;
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v18 
                        = ((2U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[2U]
                            : 0U);
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v19 
                        = ((3U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[3U]
                            : 0U);
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v20 
                        = ((4U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[4U]
                            : 0U);
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v21 
                        = ((5U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[5U]
                            : 0U);
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v22 
                        = ((6U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[6U]
                            : 0U);
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator__v23 
                        = ((7U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[7U]
                            : 0U);
                } else if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_invalid) {
                    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 1U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x13U;
                } else {
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v16[0U] 
                        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[0U];
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v16[1U] 
                        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U];
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v16[2U] 
                        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[2U];
                    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v16 
                        = (7U & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane);
                    __VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v16 = 1U;
                    __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias__v16 
                        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_bias;
                    __VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias__v16 
                        = (7U & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane);
                    if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane) 
                         >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x0bU;
                    } else {
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane);
                    }
                }
            } else if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_valid) {
                    if ((0U != (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mapped_response_error))) {
                        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched 
                            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mapped_response_error;
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x13U;
                    } else {
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index);
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 7U;
                    }
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
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane = 0U;
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x0aU;
                    } else if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index 
                                >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched)) {
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index);
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index = 0U;
                    } else if ((0x00000000ffffffffULL 
                                < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_source_address_wide)) {
                        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 2U;
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x13U;
                    } else {
                        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_address_latched 
                            = ((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_source_address_wide 
                                        >> 2U)) << 2U);
                        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched 
                            = (0x0000000fU & ((IData)(1U) 
                                              << (3U 
                                                  & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_source_address_wide))));
                        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_wdata_latched = 0U;
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 8U;
                    }
                } else if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base 
                            >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched)) {
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x12U;
                } else {
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count 
                        = ((8U <= (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched 
                                   - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base))
                            ? 8U : (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched 
                                    - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base));
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_y = 0U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x = 0U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index = 0U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index = 0U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane = 0U;
                    __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 7U;
                }
            } else if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_valid) {
                    if ((0U != (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mapped_response_error))) {
                        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched 
                            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mapped_response_error;
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x13U;
                    } else {
                        if ((0xc7ffU >= (0x0000ffffU 
                                         & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index))) {
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
                        __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x13U;
                    } else {
                        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_address_latched 
                            = ((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_address_wide 
                                        >> 2U)) << 2U);
                        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched 
                            = (0x0000000fU & ((IData)(1U) 
                                              << (3U 
                                                  & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_address_wide))));
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
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel = 0U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y = 0U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x = 0U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_y = 0U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x = 0U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index = 0U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 3U;
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width 
                    = ((8U <= (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched 
                               - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x))
                        ? 8U : (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched 
                                - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x));
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_height 
                    = (((((8U <= (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched 
                                  - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y))
                           ? 8U : (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched 
                                   - vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y)) 
                         - (IData)(1U)) * vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched) 
                       + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched);
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width 
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
                __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 0x13U;
            }
        } else if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__start_valid) 
                    & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__start_ready))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched 
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
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_y = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_y = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_x = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = 0U;
            __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state = 1U;
        }
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v0) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[0U] = 0U;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v1) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[0U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v1;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v2) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[1U] = 0U;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v3) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[1U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v3;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v4) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[2U] = 0U;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v5) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[2U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v5;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v6) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[3U] = 0U;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v7) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[3U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v7;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v8) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[4U] = 0U;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v9) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[4U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v9;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v10) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[5U] = 0U;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v11) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[5U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v11;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v12) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[6U] = 0U;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v13) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[6U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v13;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v14) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[7U] = 0U;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v15) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[7U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte__v15;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0;
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_height 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_height;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_point_count 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_point_count;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index;
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v0) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v0] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v1) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch__v1] = 0U;
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_y 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_y;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_x 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_x;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index;
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v0) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[0U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[0U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[0U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[1U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[1U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[1U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[2U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[2U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[2U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[3U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[3U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[3U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[4U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[4U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[4U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[5U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[5U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[5U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[6U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[6U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[6U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[7U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[7U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[7U][2U] = 0U;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v8) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[0U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[0U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[0U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[1U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[1U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[1U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[2U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[2U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[2U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[3U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[3U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[3U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[4U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[4U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[4U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[5U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[5U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[5U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[6U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[6U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[6U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[7U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[7U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[7U][2U] = 0U;
    }
    if (__VdlySet__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v16) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias__v16] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias__v16;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v16][0U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v16[0U];
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v16][1U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v16[1U];
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[__VdlyDim0__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v16][2U] 
            = __VdlyVal__tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter__v16[2U];
    }
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
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_height 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_height;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_byte_count 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_byte_count;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_y 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_y;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched;
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
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state 
        = __Vdly__tb_s2a_conv_tile_memory__DOT__dut__DOT__state;
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
    tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_parameter[0U] = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_parameter[1U] = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_parameter[2U] = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_accumulator = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product = 0ULL;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add = 0ULL;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude = 0ULL;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value = 0U;
    if (((8U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index) 
         & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index 
            < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count))) {
        tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_parameter[0U] 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index)][0U];
        tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_parameter[1U] 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index)][1U];
        tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_parameter[2U] 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index)][2U];
        tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_accumulator 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator
            [(7U & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index)];
        if ((tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_accumulator 
             >> 0x1fU)) {
            tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier 
                = ((tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_parameter[1U] 
                    << 0x00000018U) | (tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_parameter[0U] 
                                       >> 8U));
            tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude 
                = ((IData)(1U) + (~ tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_accumulator));
            tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift 
                = (0x000000ffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_parameter[0U]);
        } else {
            tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier 
                = ((tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_parameter[2U] 
                    << 0x00000010U) | (tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_parameter[1U] 
                                       >> 0x00000010U));
            tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude 
                = tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_accumulator;
            tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift 
                = (0x000000ffU & (tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_parameter[1U] 
                                  >> 8U));
        }
        tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product 
            = ((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_magnitude)) 
               * (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_multiplier)));
        if ((0U != tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift)) {
            tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add 
                = VL_SHIFTL_QQI(64,64,32, 1ULL, (tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift 
                                                 - (IData)(1U)));
        }
        tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude 
            = VL_SHIFTR_QQI(64,64,32, (tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_product 
                                       + tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounding_add), tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_q_shift);
        __Vtemp_20[0U] = (IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude);
        __Vtemp_20[1U] = (IData)((tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude 
                                  >> 0x00000020U));
        __Vtemp_20[2U] = 0U;
        VL_NEGATE_W(3, __Vtemp_21, __Vtemp_20);
        tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value 
            = ((tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_accumulator 
                >> 0x1fU) ? (((QData)((IData)(__Vtemp_21[1U])) 
                              << 0x00000020U) | (QData)((IData)(__Vtemp_21[0U])))
                : tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude);
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value 
            = (VL_LTS_IQQ(64, 0x000000000000007fULL, tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value)
                ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value)
                                  ? 0x00000081U : (0x000000ffU 
                                                   & (IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value))));
    }
    __Vtemp_23[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_batch_count_latched;
    __Vtemp_23[1U] = 0U;
    __Vtemp_23[2U] = 0U;
    __Vtemp_23[3U] = 0U;
    __Vtemp_24[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched;
    __Vtemp_24[1U] = 0U;
    __Vtemp_24[2U] = 0U;
    __Vtemp_24[3U] = 0U;
    VL_MUL_W(4, __Vtemp_25, __Vtemp_23, __Vtemp_24);
    __Vtemp_26[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_height_latched;
    __Vtemp_26[1U] = 0U;
    __Vtemp_26[2U] = 0U;
    __Vtemp_26[3U] = 0U;
    VL_MUL_W(4, __Vtemp_27, __Vtemp_25, __Vtemp_26);
    __Vtemp_28[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_width_latched;
    __Vtemp_28[1U] = 0U;
    __Vtemp_28[2U] = 0U;
    __Vtemp_28[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__input_elements_wide, __Vtemp_27, __Vtemp_28);
    __Vtemp_29[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_batch_count_latched;
    __Vtemp_29[1U] = 0U;
    __Vtemp_29[2U] = 0U;
    __Vtemp_29[3U] = 0U;
    __Vtemp_30[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched;
    __Vtemp_30[1U] = 0U;
    __Vtemp_30[2U] = 0U;
    __Vtemp_30[3U] = 0U;
    VL_MUL_W(4, __Vtemp_31, __Vtemp_29, __Vtemp_30);
    __Vtemp_32[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched;
    __Vtemp_32[1U] = 0U;
    __Vtemp_32[2U] = 0U;
    __Vtemp_32[3U] = 0U;
    VL_MUL_W(4, __Vtemp_33, __Vtemp_31, __Vtemp_32);
    __Vtemp_34[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched;
    __Vtemp_34[1U] = 0U;
    __Vtemp_34[2U] = 0U;
    __Vtemp_34[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_elements_wide, __Vtemp_33, __Vtemp_34);
    __Vtemp_35[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched;
    __Vtemp_35[1U] = 0U;
    __Vtemp_35[2U] = 0U;
    __Vtemp_35[3U] = 0U;
    __Vtemp_36[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched;
    __Vtemp_36[1U] = 0U;
    __Vtemp_36[2U] = 0U;
    __Vtemp_36[3U] = 0U;
    VL_MUL_W(4, __Vtemp_37, __Vtemp_35, __Vtemp_36);
    __Vtemp_38[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched;
    __Vtemp_38[1U] = 0U;
    __Vtemp_38[2U] = 0U;
    __Vtemp_38[3U] = 0U;
    VL_MUL_W(4, __Vtemp_39, __Vtemp_37, __Vtemp_38);
    __Vtemp_40[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched;
    __Vtemp_40[1U] = 0U;
    __Vtemp_40[2U] = 0U;
    __Vtemp_40[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__expected_weight_bytes_wide, __Vtemp_39, __Vtemp_40);
    __Vtemp_41[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched;
    __Vtemp_41[1U] = 0U;
    __Vtemp_41[2U] = 0U;
    __Vtemp_41[3U] = 0U;
    __Vtemp_42[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched;
    __Vtemp_42[1U] = 0U;
    __Vtemp_42[2U] = 0U;
    __Vtemp_42[3U] = 0U;
    VL_MUL_W(4, __Vtemp_43, __Vtemp_41, __Vtemp_42);
    __Vtemp_44[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched;
    __Vtemp_44[1U] = 0U;
    __Vtemp_44[2U] = 0U;
    __Vtemp_44[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_wide, __Vtemp_43, __Vtemp_44);
    __Vtemp_45[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_base_latched;
    __Vtemp_45[1U] = 0U;
    __Vtemp_45[2U] = 0U;
    __Vtemp_45[3U] = 0U;
    __Vtemp_46[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_length_latched;
    __Vtemp_46[1U] = 0U;
    __Vtemp_46[2U] = 0U;
    __Vtemp_46[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__input_end_wide, __Vtemp_45, __Vtemp_46);
    __Vtemp_47[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_base_latched;
    __Vtemp_47[1U] = 0U;
    __Vtemp_47[2U] = 0U;
    __Vtemp_47[3U] = 0U;
    __Vtemp_48[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_length_latched;
    __Vtemp_48[1U] = 0U;
    __Vtemp_48[2U] = 0U;
    __Vtemp_48[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__output_end_wide, __Vtemp_47, __Vtemp_48);
    __Vtemp_49[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_base_latched;
    __Vtemp_49[1U] = 0U;
    __Vtemp_49[2U] = 0U;
    __Vtemp_49[3U] = 0U;
    __Vtemp_50[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_length_latched;
    __Vtemp_50[1U] = 0U;
    __Vtemp_50[2U] = 0U;
    __Vtemp_50[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_end_wide, __Vtemp_49, __Vtemp_50);
    __Vtemp_51[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_offset_latched;
    __Vtemp_51[1U] = 0U;
    __Vtemp_51[2U] = 0U;
    __Vtemp_51[3U] = 0U;
    __Vtemp_52[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_bytes_latched;
    __Vtemp_52[1U] = 0U;
    __Vtemp_52[2U] = 0U;
    __Vtemp_52[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_end_wide, __Vtemp_51, __Vtemp_52);
    tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_height_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_top_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_bottom_latched)));
    tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_width_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_left_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_right_latched)));
    tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_shape_span 
        = (tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_numerator 
           - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched)));
    tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_shape_span 
        = (tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_numerator 
           - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched)));
    tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_shape_product 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched)));
    tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_shape_product 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched)));
    tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_span_plus_stride 
        = (tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_shape_span 
           + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched)));
    tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_span_plus_stride 
        = (tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_shape_span 
           + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched)));
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
        __Vtemp_53[0U] = (((8U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched
                            : 8U) - (IData)(1U));
        __Vtemp_53[1U] = 0U;
        __Vtemp_53[2U] = 0U;
        __Vtemp_53[3U] = 0U;
        __Vtemp_54[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched;
        __Vtemp_54[1U] = 0U;
        __Vtemp_54[2U] = 0U;
        __Vtemp_54[3U] = 0U;
        VL_MUL_W(4, __Vtemp_55, __Vtemp_53, __Vtemp_54);
        __Vtemp_56[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched;
        __Vtemp_56[1U] = 0U;
        __Vtemp_56[2U] = 0U;
        __Vtemp_56[3U] = 0U;
        VL_ADD_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_height_wide, __Vtemp_55, __Vtemp_56);
        __Vtemp_57[0U] = (((8U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched
                            : 8U) - (IData)(1U));
        __Vtemp_57[1U] = 0U;
        __Vtemp_57[2U] = 0U;
        __Vtemp_57[3U] = 0U;
        __Vtemp_58[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched;
        __Vtemp_58[1U] = 0U;
        __Vtemp_58[2U] = 0U;
        __Vtemp_58[3U] = 0U;
        VL_MUL_W(4, __Vtemp_59, __Vtemp_57, __Vtemp_58);
        __Vtemp_60[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched;
        __Vtemp_60[1U] = 0U;
        __Vtemp_60[2U] = 0U;
        __Vtemp_60[3U] = 0U;
        VL_ADD_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_width_wide, __Vtemp_59, __Vtemp_60);
        VL_MUL_W(4, __Vtemp_61, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_height_wide, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_width_wide);
        __Vtemp_62[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched;
        __Vtemp_62[1U] = 0U;
        __Vtemp_62[2U] = 0U;
        __Vtemp_62[3U] = 0U;
        VL_MUL_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_bytes_wide, __Vtemp_61, __Vtemp_62);
    }
    __Vtemp_63[0U] = ((8U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched)
                       ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched
                       : 8U);
    __Vtemp_63[1U] = 0U;
    __Vtemp_63[2U] = 0U;
    __Vtemp_63[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_weight_group_bytes_wide, __Vtemp_63, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_wide);
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_ok = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_error = 1U;
    __Vtemp_65[0U] = 0x00001200U;
    __Vtemp_65[1U] = 0U;
    __Vtemp_65[2U] = 0U;
    __Vtemp_65[3U] = 0U;
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
            | VL_LT_W(4, __Vtemp_65, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_wide)) 
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
        __Vtemp_66[0U] = 0xffffffffU;
        __Vtemp_66[1U] = 0U;
        __Vtemp_66[2U] = 0U;
        __Vtemp_66[3U] = 0U;
        __Vtemp_67[0U] = 0xffffffffU;
        __Vtemp_67[1U] = 0U;
        __Vtemp_67[2U] = 0U;
        __Vtemp_67[3U] = 0U;
        __Vtemp_68[0U] = 0xffffffffU;
        __Vtemp_68[1U] = 0U;
        __Vtemp_68[2U] = 0U;
        __Vtemp_68[3U] = 0U;
        if ((((((VL_LT_W(4, __Vtemp_66, tb_s2a_conv_tile_memory__DOT__dut__DOT__input_elements_wide) 
                 | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_length_latched 
                    != tb_s2a_conv_tile_memory__DOT__dut__DOT__input_elements_wide[0U])) 
                | VL_LT_W(4, __Vtemp_67, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_elements_wide)) 
               | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_length_latched 
                  != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_elements_wide[0U])) 
              | VL_LT_W(4, __Vtemp_68, tb_s2a_conv_tile_memory__DOT__dut__DOT__expected_weight_bytes_wide)) 
             | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_bytes_latched 
                != tb_s2a_conv_tile_memory__DOT__dut__DOT__expected_weight_bytes_wide[0U]))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_error = 3U;
        } else {
            __Vtemp_69[0U] = 0U;
            __Vtemp_69[1U] = 1U;
            __Vtemp_69[2U] = 0U;
            __Vtemp_69[3U] = 0U;
            __Vtemp_70[0U] = 0U;
            __Vtemp_70[1U] = 1U;
            __Vtemp_70[2U] = 0U;
            __Vtemp_70[3U] = 0U;
            __Vtemp_71[0U] = 0U;
            __Vtemp_71[1U] = 1U;
            __Vtemp_71[2U] = 0U;
            __Vtemp_71[3U] = 0U;
            __Vtemp_72[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_length_latched;
            __Vtemp_72[1U] = 0U;
            __Vtemp_72[2U] = 0U;
            __Vtemp_72[3U] = 0U;
            __Vtemp_73[0U] = 0x00000c5cU;
            __Vtemp_73[1U] = 0U;
            __Vtemp_73[2U] = 0U;
            __Vtemp_73[3U] = 0U;
            __Vtemp_74[0U] = ((0x25U >= (0x0000003fU 
                                         & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                               ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                              [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                               : 0U);
            __Vtemp_74[1U] = 0U;
            __Vtemp_74[2U] = 0U;
            __Vtemp_74[3U] = 0U;
            __Vtemp_75[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched;
            __Vtemp_75[1U] = 0U;
            __Vtemp_75[2U] = 0U;
            __Vtemp_75[3U] = 0U;
            VL_ADD_W(4, __Vtemp_76, __Vtemp_74, __Vtemp_75);
            __Vtemp_77[0U] = 0x0000c800U;
            __Vtemp_77[1U] = 0U;
            __Vtemp_77[2U] = 0U;
            __Vtemp_77[3U] = 0U;
            __Vtemp_78[0U] = 0x00009000U;
            __Vtemp_78[1U] = 0U;
            __Vtemp_78[2U] = 0U;
            __Vtemp_78[3U] = 0U;
            if (((((((((VL_LT_W(4, __Vtemp_69, tb_s2a_conv_tile_memory__DOT__dut__DOT__input_end_wide) 
                        | VL_LT_W(4, __Vtemp_70, tb_s2a_conv_tile_memory__DOT__dut__DOT__output_end_wide)) 
                       | VL_LT_W(4, __Vtemp_71, tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_end_wide)) 
                      | (0U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_length_latched)) 
                     | VL_GT_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_end_wide, __Vtemp_72)) 
                    | (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                        [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                         : 0U) != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched)) 
                   | VL_LT_W(4, __Vtemp_73, __Vtemp_76)) 
                  | VL_LT_W(4, __Vtemp_77, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_bytes_wide)) 
                 | VL_LT_W(4, __Vtemp_78, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_weight_group_bytes_wide))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_error = 2U;
            } else if (((((((tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_numerator 
                             < (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched))) 
                            | (tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_numerator 
                               < (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched)))) 
                           | (tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_shape_product 
                              <= tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_shape_span)) 
                          | (tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_shape_product 
                             > tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_span_plus_stride)) 
                         | (tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_shape_product 
                            <= tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_shape_span)) 
                        | (tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_shape_product 
                           > tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_span_plus_stride))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_error = 1U;
            } else {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_ok = 1U;
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_error = 0U;
            }
        }
    }
}

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
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_memory.sv:100: Assertion failed in %m: stall\350\257\267\346\261\202\345\255\227\346\256\265\346\224\271\345\217\230\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_memory", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("source\\tb_s2a_conv_tile_memory.sv", 100, "", false);
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
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_offset;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_offset = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_area;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_area = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_input_channel;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_input_channel = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_kernel_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_kernel_y = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_reduction_index;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_reduction_index = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_y = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_x;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_x = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_channel;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_channel = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_y = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_x;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_x = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_y = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_x;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_x = 0;
    QData/*63:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_feature_index_wide;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_feature_index_wide = 0;
    IData/*31:0*/ tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index = 0;
    // Body
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_source_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_base_latched)) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_offset_latched)) 
              + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index)) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index)))))));
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_byte_offset_wide 
        = ((QData)((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_x 
                            + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x))) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched)) 
              * ((QData)((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_y 
                                  + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y))) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index)))))));
    tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_bias = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_invalid = 0U;
    if (((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane 
          < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count) 
         & (0x00000026U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))) {
        tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index 
            = ((((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                  : 0U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base) 
               + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane);
        if ((0x00000c5cU > tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index)) {
            if ((0x0c5bU >= (0x00000fffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[0U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index)][0U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index)][1U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[2U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index)][2U];
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_bias 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                    [(0x00000fffU & tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index)];
            } else {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[0U] = 0U;
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] = 0U;
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[2U] = 0U;
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_bias = 0U;
            }
            if (((((((((tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_index 
                        >= (((0x25U >= (0x0000003fU 
                                        & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                             [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                              : 0U) + ((0x25U >= (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                       [(0x0000003fU 
                                         & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                                        : 0U))) | (0U 
                                                   == 
                                                   ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[2U] 
                                                     << 0x00000010U) 
                                                    | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                                       >> 0x00000010U)))) 
                      | (0U == ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                 << 0x00000018U) | 
                                (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[0U] 
                                 >> 8U)))) | (0x3fffffffU 
                                              < ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[2U] 
                                                  << 0x00000010U) 
                                                 | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                                    >> 0x00000010U)))) 
                    | (0x3fffffffU < ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                       << 0x00000018U) 
                                      | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[0U] 
                                         >> 8U)))) 
                   | (0x2fU < (0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                              >> 8U)))) 
                  | (0x2fU < (0x000000ffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[0U]))) 
                 | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched)) 
                    & ((((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[2U] 
                          << 0x00000010U) | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                             >> 0x00000010U)) 
                        != ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                             << 0x00000018U) | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[0U] 
                                                >> 8U))) 
                       | ((0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                          >> 8U)) != 
                          (0x000000ffU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter[0U])))))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_invalid = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_invalid = 1U;
        }
    } else if ((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane 
                < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_invalid = 1U;
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_rstrb = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_wstrb = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_plane_bytes 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_height)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width)));
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y = 0ULL;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_in_bounds = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_advance = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_offset = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_address_wide = 0ULL;
    if (((0ULL != tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_plane_bytes) 
         & (0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width))) {
        tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_top_latched)));
        tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_y, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_input_x, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_width_latched))));
        if (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_in_bounds) {
            tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_offset 
                = (((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel)) 
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
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_input_channel 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_kernel_y 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_reduction_index 
        = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index);
    if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x) 
         >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_kernel_x = 0U;
        if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y) 
             >= vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched)) {
            tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_kernel_y = 0U;
            tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_input_channel 
                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel);
        } else {
            tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_kernel_y 
                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y);
        }
    } else {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_kernel_x 
            = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x);
    }
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_y 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_x 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_channel 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_y 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_x 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index 
        = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_y = 0ULL;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_x = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_tap_in_bounds = 0U;
    tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_feature_index_wide = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_feature_index = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_enable = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[0U] = 0ULL;
    if ((0U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[0U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[0U] 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[0U];
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
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[0U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[0U])))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[0U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[0U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[1U] = 0ULL;
    if ((1U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[1U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[1U] 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[1U];
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
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[1U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[1U])))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[1U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[1U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[2U] = 0ULL;
    if ((2U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[2U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[2U] 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[2U];
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
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[2U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[2U])))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[2U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[2U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[3U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[3U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[3U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[3U] = 0ULL;
    if ((3U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[3U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[3U] 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[3U];
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
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[3U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[3U])))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[3U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[3U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[4U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[4U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[4U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[4U] = 0ULL;
    if ((4U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[4U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[4U] 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[4U];
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
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[4U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[4U])))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[4U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[4U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[5U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[5U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[5U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[5U] = 0ULL;
    if ((5U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[5U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[5U] 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[5U];
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
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[5U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[5U])))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[5U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[5U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[6U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[6U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[6U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[6U] = 0ULL;
    if ((6U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[6U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[6U] 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[6U];
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
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[6U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[6U])))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[6U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[6U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[7U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[7U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[7U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[7U] = 0ULL;
    if ((7U < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[7U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[7U] 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[7U];
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
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[7U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[7U])))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[7U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[7U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    if (((0x0bU == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
         | (0x0cU == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)))) {
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_y 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_y;
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_x 
            = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x;
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_channel = 0U;
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_y = 0U;
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_x = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_enable = 1U;
    } else if ((0x0dU == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
        if ((((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index) 
               < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched) 
              & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument))) 
             & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow)))) {
            tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_y 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_y;
            tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_x 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x;
            tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_channel 
                = tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_input_channel;
            tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_y 
                = tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_kernel_y;
            tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_x 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_kernel_x;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index 
                = tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_reduction_index;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_enable = 1U;
        }
    }
    if (((0U != tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_area) 
         & (0U != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width))) {
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_y 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched))) 
                 + ((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_y)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched)))) 
                + (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_top_latched)));
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_x 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched))) 
                 + ((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_x)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched)))) 
                + (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_tap_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_y, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_x, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_width_latched))));
        tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_feature_index_wide 
            = (((((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_input_channel)) 
                  * tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_plane_bytes) 
                 + ((((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_y)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched))) 
                     + (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_y))) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width)))) 
                + ((QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_point_x)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched)))) 
               + (QData)((IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_kernel_x)));
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_feature_index 
            = (IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_feature_index_wide);
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mapped_response_error = 0U;
    if ((((3U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
          & (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index 
             < vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_byte_count)) 
         & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_in_bounds)))) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_advance = 1U;
    } else if ((((5U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
                 & (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_valid)) 
                & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__mapped_response_error)))) {
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_advance = 1U;
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_valid = 0U;
    if ((1U & ((~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__hard_reset)) 
               & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__abort))))) {
        if (((4U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write = 0U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_rstrb 
                = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_valid = 1U;
        } else if ((0x10U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_write = 1U;
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_valid = 1U;
        }
        if ((1U & (~ ((4U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)) 
                      || (8U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state)))))) {
            if ((0x10U == (IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__state))) {
                vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_wstrb 
                    = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched;
            }
        }
    }
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_base_latched)) 
           + vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_byte_offset_wide);
}

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
