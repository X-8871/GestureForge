// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_conv_tile_unit.h for the primary calling header

#include "Vtb_s2a_conv_tile_unit__pch.h"

VlCoroutine Vtb_s2a_conv_tile_unit___024root___eval_initial__TOP__Vtiming__0(Vtb_s2a_conv_tile_unit___024root* vlSelf);
VlCoroutine Vtb_s2a_conv_tile_unit___024root___eval_initial__TOP__Vtiming__1(Vtb_s2a_conv_tile_unit___024root* vlSelf);

void Vtb_s2a_conv_tile_unit___024root___eval_initial(Vtb_s2a_conv_tile_unit___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___eval_initial\n"); );
    Vtb_s2a_conv_tile_unit__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_s2a_conv_tile_unit___024root___eval_initial__TOP__Vtiming__0(vlSelf);
    Vtb_s2a_conv_tile_unit___024root___eval_initial__TOP__Vtiming__1(vlSelf);
}

void Vtb_s2a_conv_tile_unit___024root____VbeforeTrig_h5ceb9ffd__0(Vtb_s2a_conv_tile_unit___024root* vlSelf, const char* __VeventDescription);

VlCoroutine Vtb_s2a_conv_tile_unit___024root___eval_initial__TOP__Vtiming__0(Vtb_s2a_conv_tile_unit___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___eval_initial__TOP__Vtiming__0\n"); );
    Vtb_s2a_conv_tile_unit__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__fd;
    tb_s2a_conv_tile_unit__DOT__fd = 0;
    IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__query_runner__DOT__unnamedblk1_1__DOT____Vrepeat0;
    tb_s2a_conv_tile_unit__DOT__query_runner__DOT__unnamedblk1_1__DOT____Vrepeat0 = 0;
    IData/*31:0*/ __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value;
    __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b;
    __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b = 0;
    IData/*31:0*/ __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__value;
    __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__value = 0;
    IData/*31:0*/ __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__b;
    __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__b = 0;
    // Body
    VL_WRITEF_NX("PROBE before open\n",0);
    VL_FFLUSH_MT();tb_s2a_conv_tile_unit__DOT__fd = VL_FOPEN_NN("queries.bin"s
                                                                , "rb"s);
    ;
    VL_WRITEF_NX("PROBE opened fd=%0d\n",1, '~',32,tb_s2a_conv_tile_unit__DOT__fd);
    VL_FFLUSH_MT();if (VL_UNLIKELY(((0U == tb_s2a_conv_tile_unit__DOT__fd)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:78: Assertion failed in %m: queries.bin \347\274\272\345\244\261\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.query_runner", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 78, "", false);
    }
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__hard_reset = 1U;
    tb_s2a_conv_tile_unit__DOT__query_runner__DOT__unnamedblk1_1__DOT____Vrepeat0 = 2U;
    while (VL_LTS_III(32, 0U, tb_s2a_conv_tile_unit__DOT__query_runner__DOT__unnamedblk1_1__DOT____Vrepeat0)) {
        Vtb_s2a_conv_tile_unit___024root____VbeforeTrig_h5ceb9ffd__0(vlSelf, 
                                                                     "@(negedge tb_s2a_conv_tile_unit.clk)");
        co_await vlSelfRef.__VtrigSched_h5ceb9ffd__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(negedge tb_s2a_conv_tile_unit.clk)", 
                                                             "source\\tb_s2a_conv_tile_unit.sv", 
                                                             80);
        tb_s2a_conv_tile_unit__DOT__query_runner__DOT__unnamedblk1_1__DOT____Vrepeat0 
            = (tb_s2a_conv_tile_unit__DOT__query_runner__DOT__unnamedblk1_1__DOT____Vrepeat0 
               - (IData)(1U));
    }
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__hard_reset = 0U;
    VL_WRITEF_NX("PROBE reset complete\n",0);
    VL_FFLUSH_MT();{
        while (true) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT____VlemExpr_0 
                = (tb_s2a_conv_tile_unit__DOT__fd ? feof(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : true);
            if (!((! vlSelfRef.tb_s2a_conv_tile_unit__DOT____VlemExpr_0))) break;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            if (VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work)) {
                goto __Vlabel0;
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[0U] 
                = vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__i = 1U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[0U] 
                = (vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[0U] 
                   | (0x0000ff00U & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work 
                                     << 8U)));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__i = 2U;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:90: Assertion failed in %m: \346\210\252\346\226\255 layer header\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.query_runner", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 90, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[0U] 
                = (vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[0U] 
                   | (0x00ff0000U & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work 
                                     << 0x00000010U)));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__i = 3U;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:90: Assertion failed in %m: \346\210\252\346\226\255 layer header\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.query_runner", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 90, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:90: Assertion failed in %m: \346\210\252\346\226\255 layer header\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.query_runner", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 90, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[0U] 
                = (vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[0U] 
                   | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__i = 4U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__i = 1U;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value = 0;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b = 0;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value = 0U;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[1U] 
                = __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__i = 2U;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value = 0;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b = 0;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value = 0U;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[2U] 
                = __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__i = 3U;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value = 0;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b = 0;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value = 0U;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[3U] 
                = __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__i = 4U;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value = 0;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b = 0;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value = 0U;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[4U] 
                = __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__i = 5U;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value = 0;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b = 0;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value = 0U;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[5U] 
                = __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__i = 6U;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value = 0;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b = 0;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value = 0U;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[6U] 
                = __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__i = 7U;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value = 0;
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b = 0;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value = 0U;
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (0x000000ffU & __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                                     << 8U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                                     << 0x00000010U)));
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
            }
            __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value 
                   | (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__b 
                      << 0x00000018U));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[7U] 
                = __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__0__value;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__i = 8U;
            VL_WRITEF_NX("PROBE header layer=%0d ordinal=%0d k=%0d lanes=%0d\n",4
                         , '#',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[0U]
                         , '#',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[1U]
                         , '#',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[6U]
                         , '#',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[7U]);
            VL_FFLUSH_MT();vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id 
                = vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[0U];
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__ordinal 
                = vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[1U];
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__channel 
                = vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[3U];
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__y 
                = vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[4U];
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__x 
                = vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[5U];
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__k 
                = vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[6U];
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__lanes 
                = vlSelfRef.tb_s2a_conv_tile_unit__DOT__hdr[7U];
            if (VL_UNLIKELY((((((VL_LTES_III(32, 0x00000026U, vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id) 
                                 | VL_GTES_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_unit__DOT__k)) 
                                | VL_LTS_III(32, 0x00001fffU, vlSelfRef.tb_s2a_conv_tile_unit__DOT__k)) 
                               | VL_GTS_III(32, 1U, vlSelfRef.tb_s2a_conv_tile_unit__DOT__lanes)) 
                              | VL_LTS_III(32, 8U, vlSelfRef.tb_s2a_conv_tile_unit__DOT__lanes))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:98: Assertion failed in %m: \351\235\236\346\263\225\346\237\245\350\257\242\350\256\260\345\275\225\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.query_runner", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 98, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__i = 0U;
            while (VL_LTS_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__i, vlSelfRef.tb_s2a_conv_tile_unit__DOT__k)) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work 
                    = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
                if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work)))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:101: Assertion failed in %m: \346\210\252\346\226\255 activation\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.query_runner", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 101, "", false);
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__activations[(0x00001fffU 
                                                                   & vlSelfRef.tb_s2a_conv_tile_unit__DOT__i)] 
                    = (0x000000ffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work);
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__i 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__i);
            }
            if (VL_UNLIKELY((VL_LTS_III(32, 0x00009000U, 
                                        VL_MULS_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__lanes, vlSelfRef.tb_s2a_conv_tile_unit__DOT__k))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:104: Assertion failed in %m: weight_group \345\256\271\351\207\217\350\266\205\351\231\220\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.query_runner", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 104, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__i = 0U;
            while (VL_LTS_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__i, 
                              VL_MULS_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__lanes, vlSelfRef.tb_s2a_conv_tile_unit__DOT__k))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work 
                    = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
                if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work)))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:107: Assertion failed in %m: \346\210\252\346\226\255 weight\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.query_runner", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 107, "", false);
                }
                if (VL_LIKELY(((0x8fffU >= (0x0000ffffU 
                                            & vlSelfRef.tb_s2a_conv_tile_unit__DOT__i))))) {
                    vlSelfRef.tb_s2a_conv_tile_unit__DOT__weights[(0x0000ffffU 
                                                                   & vlSelfRef.tb_s2a_conv_tile_unit__DOT__i)] 
                        = (0x000000ffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work);
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__i 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__i);
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__l = 0U;
            while (VL_LTS_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__l, vlSelfRef.tb_s2a_conv_tile_unit__DOT__lanes)) {
                __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__value = 0;
                __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__b = 0;
                __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__value = 0U;
                __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__b 
                    = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
                __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__value 
                    = (0x000000ffU & __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__b);
                if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__b)))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
                }
                __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__b 
                    = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
                __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__value 
                    = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__value 
                       | (0x0000ff00U & (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__b 
                                         << 8U)));
                if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__b)))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
                }
                __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__b 
                    = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
                __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__value 
                    = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__value 
                       | (0x00ff0000U & (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__b 
                                         << 0x00000010U)));
                if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__b)))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
                }
                __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__b 
                    = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
                if (VL_UNLIKELY((VL_GTS_III(32, 0U, __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__b)))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:68: Assertion failed in %m: \346\210\252\346\226\255 header \346\210\226 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.read_u32", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 68, "", false);
                }
                __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__value 
                    = (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__value 
                       | (__Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__b 
                          << 0x00000018U));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__word_work 
                    = __Vtask_tb_s2a_conv_tile_unit__DOT__read_u32__1__value;
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__expected_acc[(7U 
                                                                    & vlSelfRef.tb_s2a_conv_tile_unit__DOT__l)] 
                    = vlSelfRef.tb_s2a_conv_tile_unit__DOT__word_work;
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work 
                    = (tb_s2a_conv_tile_unit__DOT__fd ? fgetc(VL_CVT_I_FP(tb_s2a_conv_tile_unit__DOT__fd)) : -1);
                if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work)))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:114: Assertion failed in %m: \346\210\252\346\226\255\350\276\223\345\207\272 oracle\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.query_runner", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 114, "", false);
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__expected_byte[(7U 
                                                                     & vlSelfRef.tb_s2a_conv_tile_unit__DOT__l)] 
                    = vlSelfRef.tb_s2a_conv_tile_unit__DOT__byte_work;
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__l 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__l);
            }
            VL_WRITEF_NX("PROBE payload read\n",0);
            VL_FFLUSH_MT();vlSelfRef.tb_s2a_conv_tile_unit__DOT__group_base 
                = VL_MULS_III(32, (IData)(8U), VL_DIVS_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__channel, (IData)(8U)));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__ty 
                = VL_MULS_III(32, (IData)(8U), VL_DIVS_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__y, (IData)(8U)));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__tx 
                = VL_MULS_III(32, (IData)(8U), VL_DIVS_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__x, (IData)(8U)));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__th 
                = ((8U > (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_H
                           [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                            : 0U) - vlSelfRef.tb_s2a_conv_tile_unit__DOT__ty))
                    ? (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_H
                        [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                         : 0U) - vlSelfRef.tb_s2a_conv_tile_unit__DOT__ty)
                    : 8U);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__tw 
                = ((8U > (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
                           [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                            : 0U) - vlSelfRef.tb_s2a_conv_tile_unit__DOT__tx))
                    ? (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
                        [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                         : 0U) - vlSelfRef.tb_s2a_conv_tile_unit__DOT__tx)
                    : 8U);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__ph 
                = (((vlSelfRef.tb_s2a_conv_tile_unit__DOT__th 
                     - (IData)(1U)) * ((0x25U >= (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_H
                                       [(0x0000003fU 
                                         & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                                        : 0U)) + ((0x25U 
                                                   >= 
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_H
                                                  [
                                                  (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                                                   : 0U));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__pw 
                = (((vlSelfRef.tb_s2a_conv_tile_unit__DOT__tw 
                     - (IData)(1U)) * ((0x25U >= (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_W
                                       [(0x0000003fU 
                                         & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                                        : 0U)) + ((0x25U 
                                                   >= 
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_W
                                                  [
                                                  (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                                                   : 0U));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__point 
                = ((VL_MULS_III(32, (vlSelfRef.tb_s2a_conv_tile_unit__DOT__y 
                                     - vlSelfRef.tb_s2a_conv_tile_unit__DOT__ty), vlSelfRef.tb_s2a_conv_tile_unit__DOT__tw) 
                    + vlSelfRef.tb_s2a_conv_tile_unit__DOT__x) 
                   - vlSelfRef.tb_s2a_conv_tile_unit__DOT__tx);
            if (VL_UNLIKELY(((vlSelfRef.tb_s2a_conv_tile_unit__DOT__lanes 
                              != ((8U > (((0x25U >= 
                                           (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                                           ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_C
                                          [(0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                                           : 0U) - vlSelfRef.tb_s2a_conv_tile_unit__DOT__group_base))
                                   ? (((0x25U >= (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_C
                                       [(0x0000003fU 
                                         & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                                        : 0U) - vlSelfRef.tb_s2a_conv_tile_unit__DOT__group_base)
                                   : 8U))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:125: Assertion failed in %m: \345\260\276\347\273\204 lane \346\225\260\351\224\231\350\257\257\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.query_runner", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 125, "", false);
            }
            if (VL_UNLIKELY(((vlSelfRef.tb_s2a_conv_tile_unit__DOT__k 
                              != ((vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_C
                                   [((0x25U >= (0x0000003fU 
                                                & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                                      ? (0x0000003fU 
                                         & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)
                                      : 0U)][0U] * 
                                   ((0x25U >= (0x0000003fU 
                                               & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                                     ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_H
                                    [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                                     : 0U)) * ((0x25U 
                                                >= 
                                                (0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_W
                                               [(0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                                                : 0U)))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:127: Assertion failed in %m: \345\256\236\351\231\205\346\250\241\345\236\213 K \344\270\215\344\270\200\350\207\264\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.query_runner", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 127, "", false);
            }
            Vtb_s2a_conv_tile_unit___024root____VbeforeTrig_h5ceb9ffd__0(vlSelf, 
                                                                         "@(negedge tb_s2a_conv_tile_unit.clk)");
            co_await vlSelfRef.__VtrigSched_h5ceb9ffd__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_s2a_conv_tile_unit.clk)", 
                                                                 "source\\tb_s2a_conv_tile_unit.sv", 
                                                                 128);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__start_valid = 1U;
            Vtb_s2a_conv_tile_unit___024root____VbeforeTrig_h5ceb9ffd__0(vlSelf, 
                                                                         "@(negedge tb_s2a_conv_tile_unit.clk)");
            co_await vlSelfRef.__VtrigSched_h5ceb9ffd__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_s2a_conv_tile_unit.clk)", 
                                                                 "source\\tb_s2a_conv_tile_unit.sv", 
                                                                 129);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__start_valid = 0U;
            VL_WRITEF_NX("PROBE query started layer=%0d ordinal=%0d\n",2
                         , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id
                         , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__ordinal);
            VL_FFLUSH_MT();Vtb_s2a_conv_tile_unit___024root____VbeforeTrig_h5ceb9ffd__0(vlSelf, 
                                                                                "@(negedge tb_s2a_conv_tile_unit.clk)");
            co_await vlSelfRef.__VtrigSched_h5ceb9ffd__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_s2a_conv_tile_unit.clk)", 
                                                                 "source\\tb_s2a_conv_tile_unit.sv", 
                                                                 132);
            if (VL_UNLIKELY(((2U != (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:133: Assertion failed in %m: \347\234\237\345\256\236 descriptor \346\234\252\351\200\232\350\277\207\351\252\214\350\257\201 state=%0d layer=%0d error=%0d validation=%0d\n",7, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.query_runner", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '#',5,(IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state)
                             , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id
                             , '#',3,(IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__result_error_latched)
                             , '#',3,vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__validation_error);
                VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 133, "", false);
            }
            VL_WRITEF_NX("PROBE descriptor passed\n",0);
            VL_FFLUSH_MT();vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y 
                = vlSelfRef.tb_s2a_conv_tile_unit__DOT__ty;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x 
                = vlSelfRef.tb_s2a_conv_tile_unit__DOT__tx;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_height 
                = vlSelfRef.tb_s2a_conv_tile_unit__DOT__th;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width 
                = vlSelfRef.tb_s2a_conv_tile_unit__DOT__tw;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_height 
                = vlSelfRef.tb_s2a_conv_tile_unit__DOT__ph;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width 
                = vlSelfRef.tb_s2a_conv_tile_unit__DOT__pw;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_byte_count 
                = ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__ph 
                    * vlSelfRef.tb_s2a_conv_tile_unit__DOT__pw) 
                   * vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_C
                   [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                      ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)
                      : 0U)][0U]);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_point_count 
                = VL_MULS_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__th, vlSelfRef.tb_s2a_conv_tile_unit__DOT__tw);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base 
                = vlSelfRef.tb_s2a_conv_tile_unit__DOT__group_base;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count 
                = vlSelfRef.tb_s2a_conv_tile_unit__DOT__lanes;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__i = 0U;
            while (VL_LTS_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__i, vlSelfRef.tb_s2a_conv_tile_unit__DOT__k)) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__ic 
                    = VL_DIV_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__i, 
                                 (((0x25U >= (0x0000003fU 
                                              & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_H
                                   [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                                    : 0U) * ((0x25U 
                                              >= (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_W
                                             [(0x0000003fU 
                                               & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                                              : 0U)));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__ky 
                    = VL_DIV_III(32, VL_MODDIV_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__i, 
                                                   (((0x25U 
                                                      >= 
                                                      (0x0000003fU 
                                                       & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                                                      ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_H
                                                     [
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                                                      : 0U) 
                                                    * 
                                                    ((0x25U 
                                                      >= 
                                                      (0x0000003fU 
                                                       & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                                                      ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_W
                                                     [
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                                                      : 0U))), 
                                 ((0x25U >= (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_W
                                  [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                                   : 0U));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__kx 
                    = VL_MODDIV_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__i, 
                                    ((0x25U >= (0x0000003fU 
                                                & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                                      ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_W
                                     [(0x0000003fU 
                                       & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                                      : 0U));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__idx 
                    = (((((vlSelfRef.tb_s2a_conv_tile_unit__DOT__ic 
                           * vlSelfRef.tb_s2a_conv_tile_unit__DOT__ph) 
                          * vlSelfRef.tb_s2a_conv_tile_unit__DOT__pw) 
                         + ((((vlSelfRef.tb_s2a_conv_tile_unit__DOT__y 
                               - vlSelfRef.tb_s2a_conv_tile_unit__DOT__ty) 
                              * ((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_H
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                                  : 0U)) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__ky) 
                            * vlSelfRef.tb_s2a_conv_tile_unit__DOT__pw)) 
                        + ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__x 
                            - vlSelfRef.tb_s2a_conv_tile_unit__DOT__tx) 
                           * ((0x25U >= (0x0000003fU 
                                         & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                               ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_W
                              [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                               : 0U))) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__kx);
                if (VL_UNLIKELY((VL_LTES_III(32, 0x0000c800U, vlSelfRef.tb_s2a_conv_tile_unit__DOT__idx)))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:147: Assertion failed in %m: patch \347\264\242\345\274\225\350\266\205\351\231\220\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.query_runner", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 147, "", false);
                }
                if (VL_LIKELY(((0xc7ffU >= (0x0000ffffU 
                                            & vlSelfRef.tb_s2a_conv_tile_unit__DOT__idx))))) {
                    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch[(0x0000ffffU 
                                                                                & vlSelfRef.tb_s2a_conv_tile_unit__DOT__idx)] 
                        = vlSelfRef.tb_s2a_conv_tile_unit__DOT__activations
                        [(0x00001fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__i)];
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__i 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__i);
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__i = 0U;
            while (VL_LTS_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__i, 
                              VL_MULS_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__lanes, vlSelfRef.tb_s2a_conv_tile_unit__DOT__k))) {
                if (VL_LIKELY(((0x8fffU >= (0x0000ffffU 
                                            & vlSelfRef.tb_s2a_conv_tile_unit__DOT__i))))) {
                    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_group[(0x0000ffffU 
                                                                                & vlSelfRef.tb_s2a_conv_tile_unit__DOT__i)] 
                        = ((0x8fffU >= (0x0000ffffU 
                                        & vlSelfRef.tb_s2a_conv_tile_unit__DOT__i))
                            ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__weights
                           [(0x0000ffffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__i)]
                            : 0U);
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__i 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__i);
            }
            VL_WRITEF_NX("PROBE weights loaded lanes=%0d k=%0d\n",2
                         , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__lanes
                         , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__k);
            VL_FFLUSH_MT();VL_WRITEF_NX("PROBE before prefetch\n",0);
            VL_FFLUSH_MT();vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x0aU;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__cycles = 0U;
            while ((0x0dU != (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))) {
                if (VL_UNLIKELY((((0x13U == (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state)) 
                                  | VL_GTS_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__cycles, 
                                               ((IData)(2U) 
                                                + vlSelfRef.tb_s2a_conv_tile_unit__DOT__lanes)))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:157: Assertion failed in %m: \345\217\202\346\225\260\351\242\204\345\217\226\345\274\202\345\270\270 layer=%0d ordinal=%0d error=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.query_runner", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id
                                 , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__ordinal
                                 , '#',3,(IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__result_error_latched));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 157, "", false);
                }
                Vtb_s2a_conv_tile_unit___024root____VbeforeTrig_h5ceb9ffd__0(vlSelf, 
                                                                             "@(negedge tb_s2a_conv_tile_unit.clk)");
                co_await vlSelfRef.__VtrigSched_h5ceb9ffd__0.trigger(0U, 
                                                                     nullptr, 
                                                                     "@(negedge tb_s2a_conv_tile_unit.clk)", 
                                                                     "source\\tb_s2a_conv_tile_unit.sv", 
                                                                     158);
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__cycles 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__cycles);
            }
            VL_WRITEF_NX("PROBE prefetch complete cycles=%0d\n",1
                         , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__cycles);
            VL_FFLUSH_MT();vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index 
                = vlSelfRef.tb_s2a_conv_tile_unit__DOT__point;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__cycles = 0U;
            while ((0x0eU != (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))) {
                if (VL_UNLIKELY((((0x13U == (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state)) 
                                  | VL_GTS_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__cycles, 
                                               ((IData)(4U) 
                                                + vlSelfRef.tb_s2a_conv_tile_unit__DOT__k)))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:164: Assertion failed in %m: \350\256\241\347\256\227\345\274\202\345\270\270 layer=%0d ordinal=%0d error=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.query_runner", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id
                                 , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__ordinal
                                 , '#',3,(IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__result_error_latched));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 164, "", false);
                }
                Vtb_s2a_conv_tile_unit___024root____VbeforeTrig_h5ceb9ffd__0(vlSelf, 
                                                                             "@(negedge tb_s2a_conv_tile_unit.clk)");
                co_await vlSelfRef.__VtrigSched_h5ceb9ffd__0.trigger(0U, 
                                                                     nullptr, 
                                                                     "@(negedge tb_s2a_conv_tile_unit.clk)", 
                                                                     "source\\tb_s2a_conv_tile_unit.sv", 
                                                                     165);
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__cycles 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__cycles);
            }
            VL_WRITEF_NX("PROBE compute complete cycles=%0d\n",1
                         , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__cycles);
            VL_FFLUSH_MT();vlSelfRef.tb_s2a_conv_tile_unit__DOT__l = 0U;
            while (VL_LTS_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__l, vlSelfRef.tb_s2a_conv_tile_unit__DOT__lanes)) {
                if (VL_UNLIKELY(((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator
                                  [(7U & vlSelfRef.tb_s2a_conv_tile_unit__DOT__l)] 
                                  != vlSelfRef.tb_s2a_conv_tile_unit__DOT__expected_acc
                                  [(7U & vlSelfRef.tb_s2a_conv_tile_unit__DOT__l)])))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:170: Assertion failed in %m: \347\264\257\345\212\240\344\270\215\347\254\246 layer=%0d ordinal=%0d lane=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.query_runner", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id
                                 , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__ordinal
                                 , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__l);
                    VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 170, "", false);
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__l 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__l);
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__cycles = 0U;
            while ((0x0eU == (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))) {
                if (VL_UNLIKELY((VL_GTS_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__cycles, 
                                            ((IData)(1U) 
                                             + vlSelfRef.tb_s2a_conv_tile_unit__DOT__lanes))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:174: Assertion failed in %m: \351\200\220 lane requant \350\266\205\346\227\266 layer=%0d ordinal=%0d\n",5, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.query_runner", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id
                                 , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__ordinal);
                    VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 174, "", false);
                }
                Vtb_s2a_conv_tile_unit___024root____VbeforeTrig_h5ceb9ffd__0(vlSelf, 
                                                                             "@(negedge tb_s2a_conv_tile_unit.clk)");
                co_await vlSelfRef.__VtrigSched_h5ceb9ffd__0.trigger(0U, 
                                                                     nullptr, 
                                                                     "@(negedge tb_s2a_conv_tile_unit.clk)", 
                                                                     "source\\tb_s2a_conv_tile_unit.sv", 
                                                                     175);
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__cycles 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__cycles);
            }
            VL_WRITEF_NX("PROBE requant complete cycles=%0d\n",1
                         , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__cycles);
            VL_FFLUSH_MT();vlSelfRef.tb_s2a_conv_tile_unit__DOT__l = 0U;
            while (VL_LTS_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__l, vlSelfRef.tb_s2a_conv_tile_unit__DOT__lanes)) {
                if (VL_UNLIKELY((((0x000000ffU & VL_EXTENDS_II(32,8, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_block
                                                               [
                                                               (0x000001ffU 
                                                                & (VL_MULS_III(32, (IData)(0x00000040U), vlSelfRef.tb_s2a_conv_tile_unit__DOT__l) 
                                                                   + vlSelfRef.tb_s2a_conv_tile_unit__DOT__point))])) 
                                  != vlSelfRef.tb_s2a_conv_tile_unit__DOT__expected_byte
                                  [(7U & vlSelfRef.tb_s2a_conv_tile_unit__DOT__l)])))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:180: Assertion failed in %m: INT8 \344\270\215\347\254\246 layer=%0d ordinal=%0d lane=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.query_runner", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id
                                 , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__ordinal
                                 , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__l);
                    VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 180, "", false);
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__lane_checks 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__lane_checks);
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__l 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__l);
            }
            VL_WRITEF_NX("PASS TILE_FIRST_QUERY layer=%0d ordinal=%0d lanes=%0d\n",3
                         , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id
                         , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__ordinal
                         , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__lanes);
            VL_FFLUSH_MT();VL_FINISH_MT("source\\tb_s2a_conv_tile_unit.sv", 184, "");
            goto __Vlabel0;
        }
        __Vlabel0: ;
    }
    VL_FCLOSE_I(tb_s2a_conv_tile_unit__DOT__fd); VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_unit.sv:197: Assertion failed in %m: \345\215\225\346\235\241 query \350\256\241\346\225\260\344\270\215\347\254\246\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_unit.query_runner", 'T',-9
                                                              , '#',64,VL_TIME_UNITED_Q(1000));
    VL_STOP_MT("source\\tb_s2a_conv_tile_unit.sv", 197, "", false);
    VL_WRITEF_NX("PASS TILE_ONE_QUERY queries=0 lane_checks=%0d\n",1
                 , '~',32,vlSelfRef.tb_s2a_conv_tile_unit__DOT__lane_checks);
    VL_FFLUSH_MT();VL_FINISH_MT("source\\tb_s2a_conv_tile_unit.sv", 199, "");
    co_return;
}

VlCoroutine Vtb_s2a_conv_tile_unit___024root___eval_initial__TOP__Vtiming__1(Vtb_s2a_conv_tile_unit___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___eval_initial__TOP__Vtiming__1\n"); );
    Vtb_s2a_conv_tile_unit__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    while (VL_LIKELY(!vlSymsp->_vm_contextp__->gotFinish())) {
        co_await vlSelfRef.__VdlySched.delay(0x0000000000001388ULL, 
                                             nullptr, 
                                             "source\\tb_s2a_conv_tile_unit.sv", 
                                             21);
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__clk = 
            (1U & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__clk)));
    }
    co_return;
}

bool Vtb_s2a_conv_tile_unit___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___trigger_anySet__act\n"); );
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

void Vtb_s2a_conv_tile_unit___024root___act_sequent__TOP__0(Vtb_s2a_conv_tile_unit___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___act_sequent__TOP__0\n"); );
    Vtb_s2a_conv_tile_unit__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    QData/*63:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_plane_bytes;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_plane_bytes = 0;
    IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_channel;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_channel = 0;
    IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_rem;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_rem = 0;
    IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_y;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_y = 0;
    IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_x;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_x = 0;
    QData/*63:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_input_y;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_input_y = 0;
    QData/*63:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_input_x;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_input_x = 0;
    QData/*63:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_source_offset;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_source_offset = 0;
    IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_kernel_area;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_kernel_area = 0;
    IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_input_channel;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_input_channel = 0;
    IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_kernel_y;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_kernel_y = 0;
    IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_kernel_x;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_kernel_x = 0;
    IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_y;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_y = 0;
    IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_x;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_x = 0;
    QData/*63:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_input_y;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_input_y = 0;
    QData/*63:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_input_x;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_input_x = 0;
    CData/*0:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_tap_in_bounds;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_tap_in_bounds = 0;
    QData/*63:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index_wide;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index_wide = 0;
    IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index = 0;
    IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_index;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_index = 0;
    VlWide<3>/*79:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_parameter;
    VL_ZERO_W(80, tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_parameter);
    IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_accumulator;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_accumulator = 0;
    IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier = 0;
    IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift = 0;
    IData/*31:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude = 0;
    QData/*63:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product = 0;
    QData/*63:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add = 0;
    QData/*63:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude = 0;
    QData/*63:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value = 0;
    VlWide<3>/*95:0*/ __Vtemp_2;
    VlWide<3>/*95:0*/ __Vtemp_3;
    // Body
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_source_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_base_latched)) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_offset_latched)) 
              + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_reduction_index)) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_lane_index)))))));
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_byte_offset_wide 
        = ((QData)((IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x 
                            + (VL_MODDIV_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_point_index, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width) 
                               & (- (IData)((0U != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width))))))) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched)) 
              * ((QData)((IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y 
                                  + (VL_DIV_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_point_index, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width) 
                                     & (- (IData)((0U 
                                                   != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width))))))) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_lane_index)))))));
    tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_index = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_bias = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_invalid = 0U;
    if (((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane 
          < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count) 
         & (0x00000026U > vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))) {
        tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_index 
            = ((((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                  : 0U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base) 
               + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane);
        if ((0x00000c5cU > tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_index)) {
            if ((0x0c5bU >= (0x00000fffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_index))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[0U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_index)][0U];
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_index)][1U];
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[2U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_index)][2U];
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_bias 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                    [(0x00000fffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_index)];
            } else {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[0U] = 0U;
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[1U] = 0U;
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[2U] = 0U;
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_bias = 0U;
            }
            if (((((((((tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_index 
                        >= (((0x25U >= (0x0000003fU 
                                        & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                             [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                              : 0U) + ((0x25U >= (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                       [(0x0000003fU 
                                         & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                                        : 0U))) | (0U 
                                                   == 
                                                   ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[2U] 
                                                     << 0x00000010U) 
                                                    | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                                       >> 0x00000010U)))) 
                      | (0U == ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                 << 0x00000018U) | 
                                (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[0U] 
                                 >> 8U)))) | (0x3fffffffU 
                                              < ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[2U] 
                                                  << 0x00000010U) 
                                                 | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                                    >> 0x00000010U)))) 
                    | (0x3fffffffU < ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                       << 0x00000018U) 
                                      | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[0U] 
                                         >> 8U)))) 
                   | (0x2fU < (0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                              >> 8U)))) 
                  | (0x2fU < (0x000000ffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[0U]))) 
                 | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__activation_mode_latched)) 
                    & ((((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[2U] 
                          << 0x00000010U) | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                             >> 0x00000010U)) 
                        != ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                             << 0x00000018U) | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[0U] 
                                                >> 8U))) 
                       | ((0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                          >> 8U)) != 
                          (0x000000ffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[0U])))))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_invalid = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_invalid = 1U;
        }
    } else if ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane 
                < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_invalid = 1U;
    }
    tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_parameter[0U] = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_parameter[1U] = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_parameter[2U] = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_accumulator = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product = 0ULL;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add = 0ULL;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude = 0ULL;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value = 0U;
    if (((8U > vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_lane_index) 
         & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_lane_index 
            < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count))) {
        tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_parameter[0U] 
            = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_lane_index)][0U];
        tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_parameter[1U] 
            = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_lane_index)][1U];
        tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_parameter[2U] 
            = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_lane_index)][2U];
        tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_accumulator 
            = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator
            [(7U & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_lane_index)];
        if ((tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_accumulator 
             >> 0x1fU)) {
            tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier 
                = ((tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_parameter[1U] 
                    << 0x00000018U) | (tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_parameter[0U] 
                                       >> 8U));
            tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude 
                = ((IData)(1U) + (~ tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_accumulator));
            tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift 
                = (0x000000ffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_parameter[0U]);
        } else {
            tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier 
                = ((tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_parameter[2U] 
                    << 0x00000010U) | (tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_parameter[1U] 
                                       >> 0x00000010U));
            tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude 
                = tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_accumulator;
            tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift 
                = (0x000000ffU & (tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_parameter[1U] 
                                  >> 8U));
        }
        tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product 
            = ((QData)((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude)) 
               * (QData)((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier)));
        if ((0U != tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift)) {
            tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add 
                = VL_SHIFTL_QQI(64,64,32, 1ULL, (tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift 
                                                 - (IData)(1U)));
        }
        tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude 
            = VL_SHIFTR_QQI(64,64,32, (tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product 
                                       + tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add), tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift);
        __Vtemp_2[0U] = (IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude);
        __Vtemp_2[1U] = (IData)((tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude 
                                 >> 0x00000020U));
        __Vtemp_2[2U] = 0U;
        VL_NEGATE_W(3, __Vtemp_3, __Vtemp_2);
        tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value 
            = ((tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_accumulator 
                >> 0x1fU) ? (((QData)((IData)(__Vtemp_3[1U])) 
                              << 0x00000020U) | (QData)((IData)(__Vtemp_3[0U])))
                : tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude);
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value 
            = (VL_LTS_IQQ(64, 0x000000000000007fULL, tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value)
                ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value)
                                  ? 0x00000081U : (0x000000ffU 
                                                   & (IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value))));
    }
    tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_plane_bytes 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_height)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width)));
    tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_channel = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_rem = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_y = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_x = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_input_y = 0ULL;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_input_x = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_in_bounds = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_source_offset = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_source_address_wide = 0ULL;
    if (((0ULL != tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_plane_bytes) 
         & (0U != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width))) {
        tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_channel 
            = (IData)(VL_DIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_index)), tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_plane_bytes));
        tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_rem 
            = (IData)(VL_MODDIV_QQQ(64, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_index)), tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_plane_bytes));
        tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_y 
            = VL_DIV_III(32, tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_rem, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width);
        tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_x 
            = VL_MODDIV_III(32, tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_rem, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width);
        tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_input_y 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched))) 
                + (QData)((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_top_latched)));
        tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_input_x 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched))) 
                + (QData)((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_input_y, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_input_x, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_width_latched))));
        if (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_in_bounds) {
            tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_source_offset 
                = (((((QData)((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_channel)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_height_latched))) 
                     + tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_input_y) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_width_latched))) 
                   + tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_input_x);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_source_address_wide 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_base_latched)) 
                   + tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_source_offset);
        }
    }
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_kernel_area 
        = (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched 
           * vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched);
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_input_channel = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_kernel_y = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_kernel_x = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_y = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_x = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_input_y = 0ULL;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_input_x = 0ULL;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_tap_in_bounds = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index_wide = 0ULL;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_bad_argument = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_overflow = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[0U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[1U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[2U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[3U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[3U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[3U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[3U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[4U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[4U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[4U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[4U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[5U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[5U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[5U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[5U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[6U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[6U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[6U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[6U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[7U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[7U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[7U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[7U] = 0ULL;
    if (((0U != tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_kernel_area) 
         & (0U != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width))) {
        tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_input_channel 
            = VL_DIV_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index, tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_kernel_area);
        tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_kernel_y 
            = VL_DIV_III(32, VL_MODDIV_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index, tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_kernel_area), vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched);
        tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_kernel_x 
            = VL_MODDIV_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched);
        tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_y 
            = VL_DIV_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width);
        tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_x 
            = VL_MODDIV_III(32, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width);
        tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_input_y 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched))) 
                 + ((QData)((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_y)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched)))) 
                + (QData)((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_kernel_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_top_latched)));
        tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_input_x 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched))) 
                 + ((QData)((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_x)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched)))) 
                + (QData)((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_kernel_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_left_latched)));
        tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_tap_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_input_y, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_input_x, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_width_latched))));
        tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index_wide 
            = (((((QData)((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_input_channel)) 
                  * tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_plane_bytes) 
                 + ((((QData)((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_y)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched))) 
                     + (QData)((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_kernel_y))) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width)))) 
                + ((QData)((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_x)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched)))) 
               + (QData)((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_kernel_x)));
        tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index 
            = (IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index_wide);
        if ((0U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[0U] 
                = ((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[0U] 
                = ((0x8fffU >= (0x0000ffffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index))
                    ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index)]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[0U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[0U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[0U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[0U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[0U])));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[0U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[0U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[0U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[0U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[0U])))));
            if (((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[0U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[0U])))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[0U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[0U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[0U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[0U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[0U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[0U] = 0ULL;
        }
        if ((1U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[1U] 
                = ((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[1U] 
                = ((0x8fffU >= (0x0000ffffU & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched 
                                               + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched 
                                    + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[1U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[1U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[1U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[1U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[1U])));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[1U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[1U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[1U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[1U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[1U])))));
            if (((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[1U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[1U])))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[1U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[1U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[1U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[1U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[1U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[1U] = 0ULL;
        }
        if ((2U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[2U] 
                = ((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[2U] 
                = ((0x8fffU >= (0x0000ffffU & ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched 
                                                << 1U) 
                                               + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched 
                                     << 1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[2U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[2U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[2U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[2U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[2U])));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[2U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[2U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[2U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[2U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[2U])))));
            if (((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[2U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[2U])))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[2U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[2U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[2U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[2U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[2U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[2U] = 0ULL;
        }
        if ((3U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[3U] 
                = ((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[3U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(3U) 
                                                * vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & (((IData)(3U) * vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[3U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[3U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[3U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[3U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[3U])));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[3U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[3U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[3U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[3U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[3U])))));
            if (((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[3U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[3U])))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[3U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[3U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[3U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[3U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[3U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[3U] = 0ULL;
        }
        if ((4U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[4U] 
                = ((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[4U] 
                = ((0x8fffU >= (0x0000ffffU & ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched 
                                                << 2U) 
                                               + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched 
                                     << 2U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[4U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[4U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[4U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[4U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[4U])));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[4U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[4U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[4U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[4U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[4U])))));
            if (((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[4U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[4U])))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[4U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[4U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[4U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[4U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[4U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[4U] = 0ULL;
        }
        if ((5U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[5U] 
                = ((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[5U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(5U) 
                                                * vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & (((IData)(5U) * vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[5U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[5U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[5U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[5U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[5U])));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[5U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[5U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[5U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[5U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[5U])))));
            if (((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[5U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[5U])))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[5U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[5U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[5U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[5U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[5U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[5U] = 0ULL;
        }
        if ((6U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[6U] 
                = ((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[6U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(6U) 
                                                * vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & (((IData)(6U) * vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[6U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[6U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[6U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[6U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[6U])));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[6U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[6U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[6U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[6U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[6U])))));
            if (((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[6U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[6U])))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[6U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[6U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[6U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[6U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[6U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[6U] = 0ULL;
        }
        if ((7U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[7U] 
                = ((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[7U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(7U) 
                                                * vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_group
                   [(0x0000ffffU & (((IData)(7U) * vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[7U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[7U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[7U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[7U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[7U])));
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[7U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[7U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[7U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[7U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[7U])))));
            if (((IData)(tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[7U]) 
                    | (0x80U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[7U])))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[7U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[7U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[7U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[7U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[7U] = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[7U] = 0ULL;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_base_latched)) 
           + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_byte_offset_wide);
}

void Vtb_s2a_conv_tile_unit___024root___nba_sequent__TOP__0(Vtb_s2a_conv_tile_unit___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___nba_sequent__TOP__0\n"); );
    Vtb_s2a_conv_tile_unit__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__input_elements_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_unit__DOT__dut__DOT__input_elements_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__expected_weight_bytes_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_unit__DOT__dut__DOT__expected_weight_bytes_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__input_end_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_unit__DOT__dut__DOT__input_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__output_end_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_unit__DOT__dut__DOT__output_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_end_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_end_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_end_wide);
    QData/*63:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_numerator;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_numerator = 0;
    QData/*63:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_numerator;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_numerator = 0;
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_height_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_height_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_width_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_width_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_bytes_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_bytes_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_unit__DOT__dut__DOT__full_weight_group_bytes_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_unit__DOT__dut__DOT__full_weight_group_bytes_wide);
    CData/*4:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0;
    CData/*4:0*/ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state;
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__input_channels_latched;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__input_channels_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base = 0;
    IData/*31:0*/ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base;
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y = 0;
    IData/*31:0*/ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y;
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x = 0;
    IData/*31:0*/ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x;
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_height;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_height = 0;
    IData/*31:0*/ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_height;
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_height = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width = 0;
    IData/*31:0*/ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width;
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_height;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_height = 0;
    IData/*31:0*/ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_height;
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_height = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width = 0;
    IData/*31:0*/ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width;
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_byte_count;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_byte_count = 0;
    IData/*31:0*/ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_byte_count;
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_byte_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_point_count;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_point_count = 0;
    IData/*31:0*/ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_point_count;
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_point_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count = 0;
    IData/*31:0*/ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count;
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_index;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_lane_index;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_lane_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_reduction_index;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_reduction_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index = 0;
    IData/*31:0*/ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index;
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_lane_index;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_lane_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_point_index;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_point_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane = 0;
    IData/*31:0*/ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane;
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_lane_index;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_lane_index = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v0;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v0 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_block__v0;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_block__v0 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_block__v0;
    __VdlyDim0__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_block__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_block__v0;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_block__v0 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v0;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v0;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v0 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v1;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v1;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v1 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v2;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v2 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v2;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v2 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v3;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v3 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v3;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v3 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v4;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v4 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v4;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v4 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v5;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v5 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v5;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v5 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v6;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v6 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v6;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v6 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v7;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v7 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v7;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v7 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v8;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v8 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v8;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v8 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v9;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v9 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v9;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v9 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v10;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v10 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v11;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v11 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v12;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v12 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v13;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v13 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v14;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v14 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v15;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v15 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v16;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v16 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v16;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v16 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v17;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v17 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v17;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v17 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v18;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v18 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v19;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v19 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v20;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v20 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v21;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v21 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v22;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v22 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v23;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v23 = 0;
    VlWide<3>/*79:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v8;
    VL_ZERO_W(80, __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v8);
    CData/*2:0*/ __VdlyDim0__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v8;
    __VdlyDim0__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v8 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v8;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v8 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias__v8;
    __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias__v8 = 0;
    CData/*2:0*/ __VdlyDim0__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias__v8;
    __VdlyDim0__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias__v8 = 0;
    SData/*15:0*/ __VdlyDim0__tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch__v0;
    __VdlyDim0__tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch__v0;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch__v0 = 0;
    VlWide<4>/*127:0*/ __Vtemp_1;
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
    VlWide<4>/*127:0*/ __Vtemp_44;
    VlWide<4>/*127:0*/ __Vtemp_45;
    VlWide<4>/*127:0*/ __Vtemp_46;
    VlWide<4>/*127:0*/ __Vtemp_47;
    VlWide<4>/*127:0*/ __Vtemp_48;
    VlWide<4>/*127:0*/ __Vtemp_49;
    VlWide<4>/*127:0*/ __Vtemp_50;
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
    VlWide<4>/*127:0*/ __Vtemp_64;
    VlWide<4>/*127:0*/ __Vtemp_65;
    // Body
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_block__v0 = 0U;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_lane_index 
        = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_lane_index;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_reduction_index 
        = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_reduction_index;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_lane_index 
        = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_lane_index;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_point_index 
        = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_point_index;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_lane_index 
        = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_lane_index;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v8 = 0U;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__input_channels_latched 
        = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_channels_latched;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched 
        = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_index 
        = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_index;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index 
        = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch__v0 = 0U;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched 
        = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched 
        = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched 
        = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v1 = 0U;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v2 = 0U;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v3 = 0U;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v4 = 0U;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v5 = 0U;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v6 = 0U;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v7 = 0U;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v8 = 0U;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v9 = 0U;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v16 = 0U;
    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v17 = 0U;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched 
        = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched 
        = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched 
        = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched;
    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched 
        = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched;
    if (vlSelfRef.tb_s2a_conv_tile_unit__DOT__hard_reset) {
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0U;
        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_layer_index_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_base_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_length_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_batch_count_latched = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__input_channels_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_height_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_width_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_base_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_length_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_batch_count_latched = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_left_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_right_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_top_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_bottom_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__groups_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__padding_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_base_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_length_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_offset_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_bytes_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_batch_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__activation_mode_latched = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base = 0U;
        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y = 0U;
        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x = 0U;
        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_height = 0U;
        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_height = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width = 0U;
        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_height = 0U;
        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_height = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width = 0U;
        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_byte_count = 0U;
        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_byte_count = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_point_count = 0U;
        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_point_count = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count = 0U;
        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_index = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_lane_index = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_reduction_index = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index = 0U;
        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_lane_index = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_point_index = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane = 0U;
        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_lane_index = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__result_error_latched = 0U;
        __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v0 = 1U;
    } else if ((0x00000010U & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))) {
        if ((8U & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__result_error_latched = 6U;
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x13U;
            __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
        } else if ((4U & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__result_error_latched = 6U;
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x13U;
            __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
        } else if ((2U & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))) {
            if ((1U & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state)))) {
                if ((((IData)(8U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base) 
                     < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched)) {
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base 
                        = ((IData)(8U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base);
                    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base = 0xffffffffU;
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 6U;
                } else if (((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x 
                             + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width) 
                            < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched)) {
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x 
                        = ((IData)(8U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x);
                    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x = 0xffffffffU;
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base = 0U;
                    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base = 0xffffffffU;
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 2U;
                } else if (((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y 
                             + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_height) 
                            < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched)) {
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y 
                        = ((IData)(8U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y);
                    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y = 0xffffffffU;
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base = 0U;
                    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base = 0xffffffffU;
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x = 0U;
                    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x = 0xffffffffU;
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 2U;
                } else {
                    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__result_error_latched = 0U;
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x13U;
                }
                __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
            }
        }
    } else if ((8U & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))) {
        if ((4U & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))) {
            if ((2U & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))) {
                    if ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_lane_index 
                         >= vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x12U;
                        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
                    } else if ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_point_index 
                                >= vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_point_count)) {
                        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_lane_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_lane_index);
                        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_point_index = 0U;
                    } else {
                        __Vtemp_1[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_byte_offset_wide);
                        __Vtemp_1[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_byte_offset_wide 
                                                 >> 0x00000020U));
                        __Vtemp_1[2U] = 0U;
                        __Vtemp_1[3U] = 0U;
                        if (((0x00000000ffffffffULL 
                              < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_address_wide) 
                             | VL_GTE_W(4, __Vtemp_1, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_elements_wide))) {
                            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__result_error_latched = 2U;
                            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x13U;
                        } else {
                            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x10U;
                        }
                        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
                    }
                } else {
                    if ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_lane_index 
                         < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_block__v0 
                            = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value;
                        __VdlyDim0__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_block__v0 
                            = (0x000001ffU & ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_lane_index 
                                               << 6U) 
                                              + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index));
                        __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_block__v0 = 1U;
                    }
                    if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_lane_index) 
                         >= vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                        if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index) 
                             >= vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_point_count)) {
                            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_lane_index = 0U;
                            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_point_index = 0U;
                            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x0fU;
                        } else {
                            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index);
                            __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index = 0xffffffffU;
                            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index = 0U;
                            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x0cU;
                        }
                        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
                    } else {
                        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_lane_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_lane_index);
                    }
                }
            } else if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))) {
                if (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_bad_argument) {
                    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__result_error_latched = 1U;
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x13U;
                    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
                } else if (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_overflow) {
                    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__result_error_latched = 7U;
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x13U;
                    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
                } else {
                    if ((0U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v0 
                            = (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[0U]);
                        __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v0 = 1U;
                    }
                    if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index) 
                         >= vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched)) {
                        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_lane_index = 0U;
                        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x0eU;
                        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
                    } else {
                        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index);
                    }
                    if ((1U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v1 
                            = (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[1U]);
                        __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v1 = 1U;
                    }
                    if ((2U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v2 
                            = (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[2U]);
                        __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v2 = 1U;
                    }
                    if ((3U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v3 
                            = (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[3U]);
                        __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v3 = 1U;
                    }
                    if ((4U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v4 
                            = (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[4U]);
                        __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v4 = 1U;
                    }
                    if ((5U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v5 
                            = (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[5U]);
                        __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v5 = 1U;
                    }
                    if ((6U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v6 
                            = (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[6U]);
                        __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v6 = 1U;
                    }
                    if ((7U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                        __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v7 
                            = (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[7U]);
                        __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v7 = 1U;
                    }
                }
            } else {
                __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v8 
                    = ((0U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[0U]
                        : 0U);
                __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v8 = 1U;
                __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index = 0U;
                __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x0dU;
                __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
                __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v9 
                    = ((1U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[1U]
                        : 0U);
                __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v9 = 1U;
                __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v10 
                    = ((2U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[2U]
                        : 0U);
                __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v11 
                    = ((3U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[3U]
                        : 0U);
                __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v12 
                    = ((4U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[4U]
                        : 0U);
                __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v13 
                    = ((5U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[5U]
                        : 0U);
                __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v14 
                    = ((6U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[6U]
                        : 0U);
                __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v15 
                    = ((7U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[7U]
                        : 0U);
            }
        } else if ((2U & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))) {
            if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))) {
                __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v16 
                    = ((0U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[0U]
                        : 0U);
                __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v16 = 1U;
                __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index = 0U;
                __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index = 0xffffffffU;
                __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index = 0U;
                __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x0dU;
                __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
                __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v17 
                    = ((1U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[1U]
                        : 0U);
                __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v17 = 1U;
                __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v18 
                    = ((2U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[2U]
                        : 0U);
                __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v19 
                    = ((3U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[3U]
                        : 0U);
                __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v20 
                    = ((4U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[4U]
                        : 0U);
                __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v21 
                    = ((5U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[5U]
                        : 0U);
                __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v22 
                    = ((6U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[6U]
                        : 0U);
                __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v23 
                    = ((7U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[7U]
                        : 0U);
            } else if (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_invalid) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__result_error_latched = 1U;
                __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x13U;
                __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
            } else {
                __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v8[0U] 
                    = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[0U];
                __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v8[1U] 
                    = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[1U];
                __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v8[2U] 
                    = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_parameter[2U];
                __VdlyDim0__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v8 
                    = (7U & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane);
                __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v8 = 1U;
                __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias__v8 
                    = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_bias;
                __VdlyDim0__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias__v8 
                    = (7U & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane);
                if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane) 
                     >= vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x0bU;
                    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
                } else {
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane);
                    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane = 0xffffffffU;
                }
            }
        }
    } else if ((4U & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))) {
        if ((2U & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))) {
            if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))) {
                if ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_lane_index 
                     >= vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane = 0U;
                    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane = 0xffffffffU;
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x0aU;
                    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
                } else if ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_reduction_index 
                            >= vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched)) {
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_lane_index 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_lane_index);
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_reduction_index = 0U;
                } else {
                    if ((0x00000000ffffffffULL < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_source_address_wide)) {
                        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__result_error_latched = 2U;
                        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x13U;
                    } else {
                        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 8U;
                    }
                    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
                }
            } else {
                if ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base 
                     >= vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched)) {
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x12U;
                } else {
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count 
                        = ((8U <= (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched 
                                   - vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base))
                            ? 8U : (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched 
                                    - vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base));
                    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count = 0xffffffffU;
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_lane_index = 0U;
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_reduction_index = 0U;
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane = 0U;
                    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane = 0xffffffffU;
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 7U;
                }
                __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
            }
        }
    } else if ((2U & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))) {
        if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))) {
            if ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_index 
                 >= vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_byte_count)) {
                __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base = 0U;
                __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base = 0xffffffffU;
                __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 6U;
                __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
            } else if (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_in_bounds) {
                if ((0x00000000ffffffffULL < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_source_address_wide)) {
                    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__result_error_latched = 2U;
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x13U;
                } else {
                    __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 4U;
                }
                __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
            } else {
                if ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_index))) {
                    __VdlyDim0__tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch__v0 
                        = (0x0000ffffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_index);
                    __VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch__v0 = 1U;
                }
                __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_index 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_index);
            }
        } else {
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_height 
                = ((8U <= (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched 
                           - vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y))
                    ? 8U : (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched 
                            - vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y));
            __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_height = 0xffffffffU;
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_index = 0U;
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 3U;
            __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width 
                = ((8U <= (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched 
                           - vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x))
                    ? 8U : (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched 
                            - vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x));
            __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width = 0xffffffffU;
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_height 
                = (((((8U <= (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched 
                              - vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y))
                       ? 8U : (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched 
                               - vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y)) 
                     - (IData)(1U)) * vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched) 
                   + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched);
            __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_height = 0xffffffffU;
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width 
                = (((((8U <= (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched 
                              - vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x))
                       ? 8U : (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched 
                               - vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x)) 
                     - (IData)(1U)) * vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched) 
                   + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched);
            __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width = 0xffffffffU;
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_byte_count 
                = (((((((8U <= (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched 
                                - vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y))
                         ? 8U : (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched 
                                 - vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y)) 
                       - (IData)(1U)) * vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched) 
                     + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched) 
                    * (((((8U <= (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched 
                                  - vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x))
                           ? 8U : (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched 
                                   - vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x)) 
                         - (IData)(1U)) * vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched) 
                       + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched)) 
                   * vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_channels_latched);
            __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_byte_count = 0xffffffffU;
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_point_count 
                = (((8U <= (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched 
                            - vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y))
                     ? 8U : (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched 
                             - vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y)) 
                   * ((8U <= (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched 
                              - vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x))
                       ? 8U : (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched 
                               - vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x)));
            __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_point_count = 0xffffffffU;
        }
    } else if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))) {
        if (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__validation_ok) {
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched 
                = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_wide[0U];
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 2U;
        } else {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__result_error_latched 
                = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__validation_error;
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x13U;
        }
        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
    } else if (((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__start_valid) 
                & ((~ (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__hard_reset)) 
                   & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state))))) {
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched 
            = vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_layer_index_latched 
            = vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_base_latched 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_ADDRESS
            [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
               ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)
               : 0U)][0U];
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_length_latched 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_LENGTH_BYTES
            [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
               ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)
               : 0U)][0U];
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_batch_count_latched 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_N
            [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
               ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)
               : 0U)][0U];
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__input_channels_latched 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_C
            [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
               ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)
               : 0U)][0U];
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_height_latched 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_H
            [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
               ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)
               : 0U)][0U];
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_width_latched 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_W
            [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
               ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)
               : 0U)][0U];
        if ((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_base_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)];
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_length_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_LENGTH_BYTES
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)];
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_batch_count_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_N
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)];
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_C
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)];
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_H
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)];
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)];
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_H
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)];
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_W
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)];
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_H
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)];
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_W
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)];
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_left_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_LEFT
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)];
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_right_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_RIGHT
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)];
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_top_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_TOP
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)];
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_bottom_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_BOTTOM
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)];
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_base_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_PACKAGE_BASE
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)];
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_length_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_PACKAGE_LENGTH
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)];
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_offset_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_WEIGHT_OFFSET
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)];
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_bytes_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_WEIGHT_BYTES
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)];
        } else {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_base_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_length_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_batch_count_latched = 0U;
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched = 0U;
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched = 0U;
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched = 0U;
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched = 0U;
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched = 0U;
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched = 0U;
            __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_left_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_right_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_top_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_bottom_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_base_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_length_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_offset_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_bytes_latched = 0U;
        }
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__groups_latched = 1U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__padding_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_batch_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__activation_mode_latched 
            = ((2U == ((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id))
                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_ACTIVATION
                       [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id)]
                        : 0U)) ? 1U : 0U);
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base = 0U;
        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y = 0U;
        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x = 0U;
        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_index = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_lane_index = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_reduction_index = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index = 0U;
        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index = 0xffffffffU;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_lane_index = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_point_index = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__result_error_latched = 0U;
        __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 1U;
        __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0x1fU;
    }
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state 
        = (((IData)(__Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__state) 
            & (IData)(__VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state)) 
           | ((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state) 
              & (~ (IData)(__VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state))));
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__state = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_height 
        = ((__Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_height 
            & __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_height) 
           | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_height 
              & (~ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_height)));
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_height = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_point_count 
        = ((__Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_point_count 
            & __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_point_count) 
           | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_point_count 
              & (~ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_point_count)));
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_point_count = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_byte_count 
        = ((__Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_byte_count 
            & __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_byte_count) 
           | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_byte_count 
              & (~ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_byte_count)));
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_byte_count = 0U;
    if (__VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_block__v0) {
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_block[__VdlyDim0__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_block__v0] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_block__v0;
    }
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_lane_index 
        = __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_lane_index;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_reduction_index 
        = __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_reduction_index;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_lane_index 
        = __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_lane_index;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_point_index 
        = __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_point_index;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane 
        = ((__Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane 
            & __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane) 
           | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane 
              & (~ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane)));
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_prefetch_lane = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_lane_index 
        = __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_lane_index;
    if (__VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v0) {
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[0U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[0U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[0U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[1U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[1U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[1U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[2U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[2U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[2U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[3U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[3U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[3U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[4U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[4U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[4U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[5U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[5U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[5U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[6U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[6U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[6U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[7U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[7U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[7U][2U] = 0U;
    }
    if (__VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v8) {
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias[__VdlyDim0__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias__v8] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_bias__v8;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[__VdlyDim0__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v8][0U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v8[0U];
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[__VdlyDim0__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v8][1U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v8[1U];
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter[__VdlyDim0__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v8][2U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_mq_parameter__v8[2U];
    }
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base 
        = ((__Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base 
            & __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base) 
           | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base 
              & (~ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base)));
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_channels_latched 
        = __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__input_channels_latched;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched 
        = __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_index 
        = __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_index;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index 
        = __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_height 
        = ((__Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_height 
            & __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_height) 
           | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_height 
              & (~ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_height)));
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_height = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width 
        = ((__Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width 
            & __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width) 
           | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width 
              & (~ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width)));
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index 
        = ((__Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index 
            & __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index) 
           | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index 
              & (~ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index)));
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index = 0U;
    if (__VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch__v0) {
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch[__VdlyDim0__tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch__v0] = 0U;
    }
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched 
        = __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched 
        = __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched 
        = __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x 
        = ((__Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x 
            & __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x) 
           | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x 
              & (~ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x)));
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width 
        = ((__Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width 
            & __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width) 
           | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width 
              & (~ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width)));
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y 
        = ((__Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y 
            & __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y) 
           | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y 
              & (~ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y)));
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count 
        = ((__Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count 
            & __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count) 
           | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count 
              & (~ __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)));
    __VdlyMask__tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count = 0U;
    if (__VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v0) {
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[0U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v1) {
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[1U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v1;
    }
    if (__VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v2) {
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[2U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v2;
    }
    if (__VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v3) {
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[3U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v3;
    }
    if (__VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v4) {
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[4U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v4;
    }
    if (__VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v5) {
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[5U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v5;
    }
    if (__VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v6) {
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[6U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v6;
    }
    if (__VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v7) {
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[7U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v7;
    }
    if (__VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v8) {
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[0U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v8;
    }
    if (__VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v9) {
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[1U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v9;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[2U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v10;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[3U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v11;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[4U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v12;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[5U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v13;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[6U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v14;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[7U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v15;
    }
    if (__VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v16) {
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[0U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v16;
    }
    if (__VdlySet__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v17) {
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[1U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v17;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[2U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v18;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[3U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v19;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[4U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v20;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[5U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v21;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[6U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v22;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[7U] 
            = __VdlyVal__tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator__v23;
    }
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched 
        = __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched 
        = __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched 
        = __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched 
        = __Vdly__tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched;
    __Vtemp_10[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_batch_count_latched;
    __Vtemp_10[1U] = 0U;
    __Vtemp_10[2U] = 0U;
    __Vtemp_10[3U] = 0U;
    __Vtemp_11[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_channels_latched;
    __Vtemp_11[1U] = 0U;
    __Vtemp_11[2U] = 0U;
    __Vtemp_11[3U] = 0U;
    VL_MUL_W(4, __Vtemp_12, __Vtemp_10, __Vtemp_11);
    __Vtemp_13[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_height_latched;
    __Vtemp_13[1U] = 0U;
    __Vtemp_13[2U] = 0U;
    __Vtemp_13[3U] = 0U;
    VL_MUL_W(4, __Vtemp_14, __Vtemp_12, __Vtemp_13);
    __Vtemp_15[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_width_latched;
    __Vtemp_15[1U] = 0U;
    __Vtemp_15[2U] = 0U;
    __Vtemp_15[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__input_elements_wide, __Vtemp_14, __Vtemp_15);
    __Vtemp_16[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_batch_count_latched;
    __Vtemp_16[1U] = 0U;
    __Vtemp_16[2U] = 0U;
    __Vtemp_16[3U] = 0U;
    __Vtemp_17[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched;
    __Vtemp_17[1U] = 0U;
    __Vtemp_17[2U] = 0U;
    __Vtemp_17[3U] = 0U;
    VL_MUL_W(4, __Vtemp_18, __Vtemp_16, __Vtemp_17);
    __Vtemp_19[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched;
    __Vtemp_19[1U] = 0U;
    __Vtemp_19[2U] = 0U;
    __Vtemp_19[3U] = 0U;
    VL_MUL_W(4, __Vtemp_20, __Vtemp_18, __Vtemp_19);
    __Vtemp_21[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched;
    __Vtemp_21[1U] = 0U;
    __Vtemp_21[2U] = 0U;
    __Vtemp_21[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_elements_wide, __Vtemp_20, __Vtemp_21);
    __Vtemp_22[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched;
    __Vtemp_22[1U] = 0U;
    __Vtemp_22[2U] = 0U;
    __Vtemp_22[3U] = 0U;
    __Vtemp_23[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_channels_latched;
    __Vtemp_23[1U] = 0U;
    __Vtemp_23[2U] = 0U;
    __Vtemp_23[3U] = 0U;
    VL_MUL_W(4, __Vtemp_24, __Vtemp_22, __Vtemp_23);
    __Vtemp_25[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched;
    __Vtemp_25[1U] = 0U;
    __Vtemp_25[2U] = 0U;
    __Vtemp_25[3U] = 0U;
    VL_MUL_W(4, __Vtemp_26, __Vtemp_24, __Vtemp_25);
    __Vtemp_27[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched;
    __Vtemp_27[1U] = 0U;
    __Vtemp_27[2U] = 0U;
    __Vtemp_27[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__expected_weight_bytes_wide, __Vtemp_26, __Vtemp_27);
    __Vtemp_28[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_channels_latched;
    __Vtemp_28[1U] = 0U;
    __Vtemp_28[2U] = 0U;
    __Vtemp_28[3U] = 0U;
    __Vtemp_29[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched;
    __Vtemp_29[1U] = 0U;
    __Vtemp_29[2U] = 0U;
    __Vtemp_29[3U] = 0U;
    VL_MUL_W(4, __Vtemp_30, __Vtemp_28, __Vtemp_29);
    __Vtemp_31[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched;
    __Vtemp_31[1U] = 0U;
    __Vtemp_31[2U] = 0U;
    __Vtemp_31[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_wide, __Vtemp_30, __Vtemp_31);
    __Vtemp_32[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_base_latched;
    __Vtemp_32[1U] = 0U;
    __Vtemp_32[2U] = 0U;
    __Vtemp_32[3U] = 0U;
    __Vtemp_33[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_length_latched;
    __Vtemp_33[1U] = 0U;
    __Vtemp_33[2U] = 0U;
    __Vtemp_33[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__input_end_wide, __Vtemp_32, __Vtemp_33);
    __Vtemp_34[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_base_latched;
    __Vtemp_34[1U] = 0U;
    __Vtemp_34[2U] = 0U;
    __Vtemp_34[3U] = 0U;
    __Vtemp_35[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_length_latched;
    __Vtemp_35[1U] = 0U;
    __Vtemp_35[2U] = 0U;
    __Vtemp_35[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__output_end_wide, __Vtemp_34, __Vtemp_35);
    __Vtemp_36[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_base_latched;
    __Vtemp_36[1U] = 0U;
    __Vtemp_36[2U] = 0U;
    __Vtemp_36[3U] = 0U;
    __Vtemp_37[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_length_latched;
    __Vtemp_37[1U] = 0U;
    __Vtemp_37[2U] = 0U;
    __Vtemp_37[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_end_wide, __Vtemp_36, __Vtemp_37);
    __Vtemp_38[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_offset_latched;
    __Vtemp_38[1U] = 0U;
    __Vtemp_38[2U] = 0U;
    __Vtemp_38[3U] = 0U;
    __Vtemp_39[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_bytes_latched;
    __Vtemp_39[1U] = 0U;
    __Vtemp_39[2U] = 0U;
    __Vtemp_39[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_end_wide, __Vtemp_38, __Vtemp_39);
    tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_height_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_top_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_bottom_latched)));
    tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_width_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_left_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_right_latched)));
    tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_height_wide[0U] = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_height_wide[1U] = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_height_wide[2U] = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_height_wide[3U] = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_width_wide[0U] = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_width_wide[1U] = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_width_wide[2U] = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_width_wide[3U] = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_bytes_wide[0U] = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_bytes_wide[1U] = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_bytes_wide[2U] = 0U;
    tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_bytes_wide[3U] = 0U;
    if (((0U != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched) 
         & (0U != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched))) {
        __Vtemp_40[0U] = (((8U > vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched)
                            ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched
                            : 8U) - (IData)(1U));
        __Vtemp_40[1U] = 0U;
        __Vtemp_40[2U] = 0U;
        __Vtemp_40[3U] = 0U;
        __Vtemp_41[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched;
        __Vtemp_41[1U] = 0U;
        __Vtemp_41[2U] = 0U;
        __Vtemp_41[3U] = 0U;
        VL_MUL_W(4, __Vtemp_42, __Vtemp_40, __Vtemp_41);
        __Vtemp_43[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched;
        __Vtemp_43[1U] = 0U;
        __Vtemp_43[2U] = 0U;
        __Vtemp_43[3U] = 0U;
        VL_ADD_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_height_wide, __Vtemp_42, __Vtemp_43);
        __Vtemp_44[0U] = (((8U > vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched)
                            ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched
                            : 8U) - (IData)(1U));
        __Vtemp_44[1U] = 0U;
        __Vtemp_44[2U] = 0U;
        __Vtemp_44[3U] = 0U;
        __Vtemp_45[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched;
        __Vtemp_45[1U] = 0U;
        __Vtemp_45[2U] = 0U;
        __Vtemp_45[3U] = 0U;
        VL_MUL_W(4, __Vtemp_46, __Vtemp_44, __Vtemp_45);
        __Vtemp_47[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched;
        __Vtemp_47[1U] = 0U;
        __Vtemp_47[2U] = 0U;
        __Vtemp_47[3U] = 0U;
        VL_ADD_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_width_wide, __Vtemp_46, __Vtemp_47);
        VL_MUL_W(4, __Vtemp_48, tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_height_wide, tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_width_wide);
        __Vtemp_49[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_channels_latched;
        __Vtemp_49[1U] = 0U;
        __Vtemp_49[2U] = 0U;
        __Vtemp_49[3U] = 0U;
        VL_MUL_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_bytes_wide, __Vtemp_48, __Vtemp_49);
    }
    __Vtemp_50[0U] = ((8U > vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched)
                       ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched
                       : 8U);
    __Vtemp_50[1U] = 0U;
    __Vtemp_50[2U] = 0U;
    __Vtemp_50[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__full_weight_group_bytes_wide, __Vtemp_50, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_wide);
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__validation_ok = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__validation_error = 1U;
    __Vtemp_52[0U] = 0x00001fffU;
    __Vtemp_52[1U] = 0U;
    __Vtemp_52[2U] = 0U;
    __Vtemp_52[3U] = 0U;
    if ((((((((((((((((((((((1U < (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__activation_mode_latched)) 
                            | (1U != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_batch_count_latched)) 
                           | (1U != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_batch_count_latched)) 
                          | (0U != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_batch_latched)) 
                         | (0U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_channels_latched)) 
                        | (0U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_height_latched)) 
                       | (0U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_width_latched)) 
                      | (0U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched)) 
                     | (0U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched)) 
                    | (0U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched)) 
                   | (0U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched)) 
                  | (0U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched)) 
                 | (0U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched)) 
                | (0U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched)) 
               | (1U != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__groups_latched)) 
              | (0U != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__padding_latched)) 
             | (0U == (((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_wide[0U] 
                         | vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_wide[1U]) 
                        | vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_wide[2U]) 
                       | vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_wide[3U]))) 
            | VL_LT_W(4, __Vtemp_52, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_wide)) 
           | (0x00000026U <= vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)) 
          | ((0x00000026U > vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched) 
             & (0U != ((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OP
                       [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                        : 0U)))) | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched 
                                    != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_layer_index_latched))) {
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__validation_error 
            = (((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched 
                 != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_layer_index_latched) 
                | (0x00000026U <= vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                ? 2U : 1U);
    } else {
        __Vtemp_53[0U] = 0xffffffffU;
        __Vtemp_53[1U] = 0U;
        __Vtemp_53[2U] = 0U;
        __Vtemp_53[3U] = 0U;
        __Vtemp_54[0U] = 0xffffffffU;
        __Vtemp_54[1U] = 0U;
        __Vtemp_54[2U] = 0U;
        __Vtemp_54[3U] = 0U;
        __Vtemp_55[0U] = 0xffffffffU;
        __Vtemp_55[1U] = 0U;
        __Vtemp_55[2U] = 0U;
        __Vtemp_55[3U] = 0U;
        if ((((((VL_LT_W(4, __Vtemp_53, tb_s2a_conv_tile_unit__DOT__dut__DOT__input_elements_wide) 
                 | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_length_latched 
                    != tb_s2a_conv_tile_unit__DOT__dut__DOT__input_elements_wide[0U])) 
                | VL_LT_W(4, __Vtemp_54, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_elements_wide)) 
               | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_length_latched 
                  != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_elements_wide[0U])) 
              | VL_LT_W(4, __Vtemp_55, tb_s2a_conv_tile_unit__DOT__dut__DOT__expected_weight_bytes_wide)) 
             | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_bytes_latched 
                != tb_s2a_conv_tile_unit__DOT__dut__DOT__expected_weight_bytes_wide[0U]))) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__validation_error = 3U;
        } else {
            __Vtemp_56[0U] = 0U;
            __Vtemp_56[1U] = 1U;
            __Vtemp_56[2U] = 0U;
            __Vtemp_56[3U] = 0U;
            __Vtemp_57[0U] = 0U;
            __Vtemp_57[1U] = 1U;
            __Vtemp_57[2U] = 0U;
            __Vtemp_57[3U] = 0U;
            __Vtemp_58[0U] = 0U;
            __Vtemp_58[1U] = 1U;
            __Vtemp_58[2U] = 0U;
            __Vtemp_58[3U] = 0U;
            __Vtemp_59[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_length_latched;
            __Vtemp_59[1U] = 0U;
            __Vtemp_59[2U] = 0U;
            __Vtemp_59[3U] = 0U;
            __Vtemp_60[0U] = 0x00000c5cU;
            __Vtemp_60[1U] = 0U;
            __Vtemp_60[2U] = 0U;
            __Vtemp_60[3U] = 0U;
            __Vtemp_61[0U] = ((0x25U >= (0x0000003fU 
                                         & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                               ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                              [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                               : 0U);
            __Vtemp_61[1U] = 0U;
            __Vtemp_61[2U] = 0U;
            __Vtemp_61[3U] = 0U;
            __Vtemp_62[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched;
            __Vtemp_62[1U] = 0U;
            __Vtemp_62[2U] = 0U;
            __Vtemp_62[3U] = 0U;
            VL_ADD_W(4, __Vtemp_63, __Vtemp_61, __Vtemp_62);
            __Vtemp_64[0U] = 0x0000c800U;
            __Vtemp_64[1U] = 0U;
            __Vtemp_64[2U] = 0U;
            __Vtemp_64[3U] = 0U;
            __Vtemp_65[0U] = 0x00009000U;
            __Vtemp_65[1U] = 0U;
            __Vtemp_65[2U] = 0U;
            __Vtemp_65[3U] = 0U;
            if (((((((((VL_LT_W(4, __Vtemp_56, tb_s2a_conv_tile_unit__DOT__dut__DOT__input_end_wide) 
                        | VL_LT_W(4, __Vtemp_57, tb_s2a_conv_tile_unit__DOT__dut__DOT__output_end_wide)) 
                       | VL_LT_W(4, __Vtemp_58, tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_end_wide)) 
                      | (0U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_length_latched)) 
                     | VL_GT_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_end_wide, __Vtemp_59)) 
                    | (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                        [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                         : 0U) != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched)) 
                   | VL_LT_W(4, __Vtemp_60, __Vtemp_63)) 
                  | VL_LT_W(4, __Vtemp_64, tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_bytes_wide)) 
                 | VL_LT_W(4, __Vtemp_65, tb_s2a_conv_tile_unit__DOT__dut__DOT__full_weight_group_bytes_wide))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__validation_error = 2U;
            } else if (((((tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_numerator 
                           < (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched))) 
                          | (tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_numerator 
                             < (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched)))) 
                         | ((1ULL + VL_DIV_QQQ(64, 
                                               (tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_numerator 
                                                - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched))), (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched)))) 
                            != (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched)))) 
                        | ((1ULL + VL_DIV_QQQ(64, (tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_numerator 
                                                   - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched))), (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched)))) 
                           != (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched))))) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__validation_error = 1U;
            } else {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__validation_ok = 1U;
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__validation_error = 0U;
            }
        }
    }
}

void Vtb_s2a_conv_tile_unit___024root___timing_ready(Vtb_s2a_conv_tile_unit___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___timing_ready\n"); );
    Vtb_s2a_conv_tile_unit__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((2ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VtrigSched_h5ceb9ffd__0.ready("@(negedge tb_s2a_conv_tile_unit.clk)");
    }
}

void Vtb_s2a_conv_tile_unit___024root___timing_resume(Vtb_s2a_conv_tile_unit___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___timing_resume\n"); );
    Vtb_s2a_conv_tile_unit__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VtrigSched_h5ceb9ffd__0.moveToResumeQueue(
                                                          "@(negedge tb_s2a_conv_tile_unit.clk)");
    vlSelfRef.__VtrigSched_h5ceb9ffd__0.resume("@(negedge tb_s2a_conv_tile_unit.clk)");
    vlSelfRef.__VdynSched.resume();
    if ((4ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VdlySched.resume();
    }
}

void Vtb_s2a_conv_tile_unit___024root___trigger_orInto__act_vec_vec(VlUnpacked<QData/*63:0*/, 1> &out, const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___trigger_orInto__act_vec_vec\n"); );
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
VL_ATTR_COLD void Vtb_s2a_conv_tile_unit___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG

bool Vtb_s2a_conv_tile_unit___024root___eval_phase__act(Vtb_s2a_conv_tile_unit___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___eval_phase__act\n"); );
    Vtb_s2a_conv_tile_unit__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VactExecute;
    // Body
    {
        // Inlined CFunc: _eval_triggers_vec__act
        vlSelfRef.__VactTriggered[0U] = VL_EXTEND_QI(64,4, 
                                                     (((vlSelfRef.__VdynSched.evaluate() 
                                                        << 3U) 
                                                       | (vlSelfRef.__VdlySched.awaitingCurrentTime() 
                                                          << 2U)) 
                                                      | ((((~ (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__clk)) 
                                                           & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_conv_tile_unit__DOT__clk__0)) 
                                                          << 1U) 
                                                         | ((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__clk) 
                                                            & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_conv_tile_unit__DOT__clk__0))))));
        vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_conv_tile_unit__DOT__clk__0 
            = vlSelfRef.tb_s2a_conv_tile_unit__DOT__clk;
        vlSelfRef.__VdynSched.doPostUpdates();
    }
    Vtb_s2a_conv_tile_unit___024root___timing_ready(vlSelf);
    Vtb_s2a_conv_tile_unit___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VactTriggered, vlSelfRef.__VactTriggeredAcc);
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vtb_s2a_conv_tile_unit___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
    }
#endif
    Vtb_s2a_conv_tile_unit___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VnbaTriggered, vlSelfRef.__VactTriggered);
    __VactExecute = Vtb_s2a_conv_tile_unit___024root___trigger_anySet__act(vlSelfRef.__VactTriggered);
    if (__VactExecute) {
        vlSelfRef.__VactTriggeredAcc.fill(0ULL);
        Vtb_s2a_conv_tile_unit___024root___timing_resume(vlSelf);
        {
            // Inlined CFunc: _eval_act
            if ((2ULL & vlSelfRef.__VactTriggered[0U])) {
                Vtb_s2a_conv_tile_unit___024root___act_sequent__TOP__0(vlSelf);
            }
        }
    }
    return (__VactExecute);
}

bool Vtb_s2a_conv_tile_unit___024root___eval_phase__inact(Vtb_s2a_conv_tile_unit___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___eval_phase__inact\n"); );
    Vtb_s2a_conv_tile_unit__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VinactExecute;
    // Body
    __VinactExecute = vlSelfRef.__VdlySched.awaitingZeroDelay();
    if (__VinactExecute) {
        VL_FATAL_MT("source\\tb_s2a_conv_tile_unit.sv", 3, "", "ZERODLY: Design Verilated with '--no-sched-zero-delay', but #0 delay executed at runtime");
    }
    return (__VinactExecute);
}

void Vtb_s2a_conv_tile_unit___024root___trigger_clear__act(VlUnpacked<QData/*63:0*/, 1> &out) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___trigger_clear__act\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        out[n] = 0ULL;
        n = ((IData)(1U) + n);
    } while ((1U > n));
}

bool Vtb_s2a_conv_tile_unit___024root___eval_phase__nba(Vtb_s2a_conv_tile_unit___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___eval_phase__nba\n"); );
    Vtb_s2a_conv_tile_unit__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = Vtb_s2a_conv_tile_unit___024root___trigger_anySet__act(vlSelfRef.__VnbaTriggered);
    if (__VnbaExecute) {
        {
            // Inlined CFunc: _eval_nba
            if ((1ULL & vlSelfRef.__VnbaTriggered[0U])) {
                Vtb_s2a_conv_tile_unit___024root___nba_sequent__TOP__0(vlSelf);
            }
            if ((3ULL & vlSelfRef.__VnbaTriggered[0U])) {
                Vtb_s2a_conv_tile_unit___024root___act_sequent__TOP__0(vlSelf);
            }
        }
        Vtb_s2a_conv_tile_unit___024root___trigger_clear__act(vlSelfRef.__VnbaTriggered);
    }
    return (__VnbaExecute);
}

void Vtb_s2a_conv_tile_unit___024root___eval(Vtb_s2a_conv_tile_unit___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___eval\n"); );
    Vtb_s2a_conv_tile_unit__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VnbaIterCount;
    // Body
    __VnbaIterCount = 0U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VnbaIterCount)))) {
#ifdef VL_DEBUG
            Vtb_s2a_conv_tile_unit___024root___dump_triggers__act(vlSelfRef.__VnbaTriggered, "nba"s);
#endif
            VL_FATAL_MT("source\\tb_s2a_conv_tile_unit.sv", 3, "", "DIDNOTCONVERGE: NBA region did not converge after '--converge-limit' of 10000 tries");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        vlSelfRef.__VinactIterCount = 0U;
        do {
            if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VinactIterCount)))) {
                VL_FATAL_MT("source\\tb_s2a_conv_tile_unit.sv", 3, "", "DIDNOTCONVERGE: Inactive region did not converge after '--converge-limit' of 10000 tries");
            }
            vlSelfRef.__VinactIterCount = ((IData)(1U) 
                                           + vlSelfRef.__VinactIterCount);
            vlSelfRef.__VactIterCount = 0U;
            do {
                if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                    Vtb_s2a_conv_tile_unit___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
#endif
                    VL_FATAL_MT("source\\tb_s2a_conv_tile_unit.sv", 3, "", "DIDNOTCONVERGE: Active region did not converge after '--converge-limit' of 10000 tries");
                }
                vlSelfRef.__VactIterCount = ((IData)(1U) 
                                             + vlSelfRef.__VactIterCount);
                vlSelfRef.__VactPhaseResult = Vtb_s2a_conv_tile_unit___024root___eval_phase__act(vlSelf);
            } while (vlSelfRef.__VactPhaseResult);
            vlSelfRef.__VinactPhaseResult = Vtb_s2a_conv_tile_unit___024root___eval_phase__inact(vlSelf);
        } while (vlSelfRef.__VinactPhaseResult);
        vlSelfRef.__VnbaPhaseResult = Vtb_s2a_conv_tile_unit___024root___eval_phase__nba(vlSelf);
    } while (vlSelfRef.__VnbaPhaseResult);
}

void Vtb_s2a_conv_tile_unit___024root____VbeforeTrig_h5ceb9ffd__0(Vtb_s2a_conv_tile_unit___024root* vlSelf, const char* __VeventDescription) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root____VbeforeTrig_h5ceb9ffd__0\n"); );
    Vtb_s2a_conv_tile_unit__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlUnpacked<QData/*63:0*/, 1> __VTmp;
    // Body
    __VTmp[0U] = (QData)((IData)((((~ (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__clk)) 
                                   & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_conv_tile_unit__DOT__clk__0)) 
                                  << 1U)));
    vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_conv_tile_unit__DOT__clk__0 
        = vlSelfRef.tb_s2a_conv_tile_unit__DOT__clk;
    if ((2ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_h5ceb9ffd__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h5ceb9ffd__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h5ceb9ffd__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h5ceb9ffd__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h5ceb9ffd__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h5ceb9ffd__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h5ceb9ffd__0.ready(__VeventDescription);
    }
    vlSelfRef.__VactTriggeredAcc[0U] = (vlSelfRef.__VactTriggeredAcc[0U] 
                                        | __VTmp[0U]);
}

#ifdef VL_DEBUG
void Vtb_s2a_conv_tile_unit___024root___eval_debug_assertions(Vtb_s2a_conv_tile_unit___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___eval_debug_assertions\n"); );
    Vtb_s2a_conv_tile_unit__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}
#endif  // VL_DEBUG
