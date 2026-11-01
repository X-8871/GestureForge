// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_conv_tile_boundary.h for the primary calling header

#include "Vtb_s2a_conv_tile_boundary__pch.h"

VlCoroutine Vtb_s2a_conv_tile_boundary___024root___eval_initial__TOP__Vtiming__0(Vtb_s2a_conv_tile_boundary___024root* vlSelf);
VlCoroutine Vtb_s2a_conv_tile_boundary___024root___eval_initial__TOP__Vtiming__1(Vtb_s2a_conv_tile_boundary___024root* vlSelf);

void Vtb_s2a_conv_tile_boundary___024root___eval_initial(Vtb_s2a_conv_tile_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___eval_initial\n"); );
    Vtb_s2a_conv_tile_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_s2a_conv_tile_boundary___024root___eval_initial__TOP__Vtiming__0(vlSelf);
    Vtb_s2a_conv_tile_boundary___024root___eval_initial__TOP__Vtiming__1(vlSelf);
}

void Vtb_s2a_conv_tile_boundary___024root____VbeforeTrig_h64692e26__0(Vtb_s2a_conv_tile_boundary___024root* vlSelf, const char* __VeventDescription);
extern const VlWide<10>/*319:0*/ Vtb_s2a_conv_tile_boundary__ConstPool__CONST_hb4617e49_0;
extern const VlUnpacked<IData/*31:0*/, 5> Vtb_s2a_conv_tile_boundary__ConstPool__TABLE_hc6a14c36_0;

VlCoroutine Vtb_s2a_conv_tile_boundary___024root___eval_initial__TOP__Vtiming__0(Vtb_s2a_conv_tile_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___eval_initial__TOP__Vtiming__0\n"); );
    Vtb_s2a_conv_tile_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT____VlemCall_9__total_stalls;
    CData/*0:0*/ tb_s2a_conv_tile_boundary__DOT____VlemLogOr_7;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT____VlemExpr_5;
    CData/*0:0*/ tb_s2a_conv_tile_boundary__DOT____VlemLogOr_4;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT____VlemExpr_2;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__fd;
    tb_s2a_conv_tile_boundary__DOT__fd = 0;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__loaded;
    tb_s2a_conv_tile_boundary__DOT__loaded = 0;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__i;
    tb_s2a_conv_tile_boundary__DOT__i = 0;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__expected_error;
    tb_s2a_conv_tile_boundary__DOT__expected_error = 0;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__requests_before;
    tb_s2a_conv_tile_boundary__DOT__requests_before = 0;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__unnamedblk1_1__DOT____Vrepeat0;
    tb_s2a_conv_tile_boundary__DOT__unnamedblk1_1__DOT____Vrepeat0 = 0;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__unnamedblk1_2__DOT____Vrepeat1;
    tb_s2a_conv_tile_boundary__DOT__unnamedblk1_2__DOT____Vrepeat1 = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__n;
    __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__n = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2____VlefCall_0__stalls;
    __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2____VlefCall_0__stalls = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__j;
    __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__j = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__3__Vfuncout;
    __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__3__Vfuncout = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__3__n;
    __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__3__n = 0;
    IData/*31:0*/ __Vtemp_1;
    IData/*31:0*/ __Vtemp_2;
    IData/*31:0*/ __Vtemp_3;
    // Body
    tb_s2a_conv_tile_boundary__DOT____VlemExpr_2 = VL_VALUEPLUSARGS_INI(32, "LAYER=%d"s, 
                                                                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id);
    tb_s2a_conv_tile_boundary__DOT____VlemLogOr_4 = 
        (! tb_s2a_conv_tile_boundary__DOT____VlemExpr_2);
    if ((1U & (~ (IData)(tb_s2a_conv_tile_boundary__DOT____VlemLogOr_4)))) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT____VlemExpr_3 
            = VL_VALUEPLUSARGS_INI(32, "MODE=%d"s, 
                                   vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode);
        tb_s2a_conv_tile_boundary__DOT____VlemLogOr_4 
            = (! vlSelfRef.tb_s2a_conv_tile_boundary__DOT____VlemExpr_3);
    }
    if (VL_UNLIKELY((tb_s2a_conv_tile_boundary__DOT____VlemLogOr_4))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:125: Assertion failed in %m: \345\217\202\346\225\260\347\274\272\345\244\261\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 125, "", false);
    }
    if (VL_UNLIKELY((((0x0000001dU != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id) 
                      & (0x00000024U != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:126: Assertion failed in %m: \344\270\215\346\230\257\347\234\237\345\256\236head\345\261\202\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 126, "", false);
    }
    tb_s2a_conv_tile_boundary__DOT____VlemExpr_5 = VL_VALUEPLUSARGS_INN(64, "WEIGHT=%s"s, 
                                                                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__weight_file);
    tb_s2a_conv_tile_boundary__DOT____VlemLogOr_7 = 
        (! tb_s2a_conv_tile_boundary__DOT____VlemExpr_5);
    if ((1U & (~ (IData)(tb_s2a_conv_tile_boundary__DOT____VlemLogOr_7)))) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT____VlemExpr_6 
            = VL_VALUEPLUSARGS_INN(64, "GOLDEN=%s"s, 
                                   vlSelfRef.tb_s2a_conv_tile_boundary__DOT__golden_file);
        tb_s2a_conv_tile_boundary__DOT____VlemLogOr_7 
            = (! vlSelfRef.tb_s2a_conv_tile_boundary__DOT____VlemExpr_6);
    }
    if ((1U & (~ (IData)(tb_s2a_conv_tile_boundary__DOT____VlemLogOr_7)))) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT____VlemExpr_8 
            = VL_VALUEPLUSARGS_INN(64, "FEATURE=%s"s, 
                                   vlSelfRef.tb_s2a_conv_tile_boundary__DOT__feature_file);
        tb_s2a_conv_tile_boundary__DOT____VlemLogOr_7 
            = (! vlSelfRef.tb_s2a_conv_tile_boundary__DOT____VlemExpr_8);
    }
    if (VL_UNLIKELY((tb_s2a_conv_tile_boundary__DOT____VlemLogOr_7))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:127: Assertion failed in %m: \345\244\271\345\205\267\345\217\202\346\225\260\347\274\272\345\244\261\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 127, "", false);
    }
    tb_s2a_conv_tile_boundary__DOT__fd = VL_FOPEN_NN(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__weight_file
                                                     , "rb"s);
    ;
    if (VL_UNLIKELY(((1U & (~ (0U != tb_s2a_conv_tile_boundary__DOT__fd)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:128: Assertion failed in %m: \346\235\203\351\207\215\346\226\207\344\273\266\347\274\272\345\244\261\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 128, "", false);
    }
    tb_s2a_conv_tile_boundary__DOT__loaded = VL_FREAD_I(8
                                                        , 0
                                                        , 15360
                                                        , &(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__weights)
                                                        , tb_s2a_conv_tile_boundary__DOT__fd
                                                        , 0
                                                        , 15360);
    VL_FCLOSE_I(tb_s2a_conv_tile_boundary__DOT__fd); if (VL_UNLIKELY((
                                                                      (tb_s2a_conv_tile_boundary__DOT__loaded 
                                                                       != 
                                                                       ((0x25U 
                                                                         >= 
                                                                         (0x0000003fU 
                                                                          & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                                                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_WEIGHT_BYTES
                                                                        [
                                                                        (0x0000003fU 
                                                                         & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                                                                         : 0U))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:129: Assertion failed in %m: \346\235\203\351\207\215\351\225\277\345\272\246\351\224\231\350\257\257\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 129, "", false);
    }
    tb_s2a_conv_tile_boundary__DOT__fd = VL_FOPEN_NN(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__golden_file
                                                     , "rb"s);
    ;
    if (VL_UNLIKELY(((1U & (~ (0U != tb_s2a_conv_tile_boundary__DOT__fd)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:130: Assertion failed in %m: \351\273\204\351\207\221\346\226\207\344\273\266\347\274\272\345\244\261\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 130, "", false);
    }
    tb_s2a_conv_tile_boundary__DOT__loaded = VL_FREAD_I(8
                                                        , 0
                                                        , 20280
                                                        , &(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__expected)
                                                        , tb_s2a_conv_tile_boundary__DOT__fd
                                                        , 0
                                                        , 20280);
    VL_FCLOSE_I(tb_s2a_conv_tile_boundary__DOT__fd); if (VL_UNLIKELY((
                                                                      (tb_s2a_conv_tile_boundary__DOT__loaded 
                                                                       != 
                                                                       ((0x25U 
                                                                         >= 
                                                                         (0x0000003fU 
                                                                          & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                                                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_LENGTH_BYTES
                                                                        [
                                                                        (0x0000003fU 
                                                                         & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                                                                         : 0U))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:131: Assertion failed in %m: \351\273\204\351\207\221\351\225\277\345\272\246\351\224\231\350\257\257\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 131, "", false);
    }
    tb_s2a_conv_tile_boundary__DOT__fd = VL_FOPEN_NN(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__feature_file
                                                     , "rb"s);
    ;
    if (VL_UNLIKELY(((1U & (~ (0U != tb_s2a_conv_tile_boundary__DOT__fd)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:132: Assertion failed in %m: \347\211\271\345\276\201\346\226\207\344\273\266\347\274\272\345\244\261\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 132, "", false);
    }
    tb_s2a_conv_tile_boundary__DOT__loaded = VL_FREAD_I(8
                                                        , 0
                                                        , 173056
                                                        , &(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__features)
                                                        , tb_s2a_conv_tile_boundary__DOT__fd
                                                        , 0
                                                        , 173056);
    VL_FCLOSE_I(tb_s2a_conv_tile_boundary__DOT__fd); if (VL_UNLIKELY((
                                                                      (tb_s2a_conv_tile_boundary__DOT__loaded 
                                                                       != vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_LENGTH_BYTES
                                                                       [
                                                                       ((0x25U 
                                                                         >= 
                                                                         (0x0000003fU 
                                                                          & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                                                         ? 
                                                                        (0x0000003fU 
                                                                         & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)
                                                                         : 0U)][0U])))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:133: Assertion failed in %m: \347\211\271\345\276\201\351\225\277\345\272\246\351\224\231\350\257\257\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 133, "", false);
    }
    tb_s2a_conv_tile_boundary__DOT__i = 0U;
    while (VL_GTS_III(32, 0x00004f38U, tb_s2a_conv_tile_boundary__DOT__i)) {
        if (VL_LIKELY(((0x4f37U >= (0x00007fffU & tb_s2a_conv_tile_boundary__DOT__i))))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__seen[(0x00007fffU 
                                                            & tb_s2a_conv_tile_boundary__DOT__i)] = 0U;
        }
        tb_s2a_conv_tile_boundary__DOT__i = ((IData)(1U) 
                                             + tb_s2a_conv_tile_boundary__DOT__i);
    }
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__class_count[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__class_stalls[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__class_count[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__class_stalls[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__class_count[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__class_stalls[2U] = 0U;
    tb_s2a_conv_tile_boundary__DOT__i = 3U;
    tb_s2a_conv_tile_boundary__DOT__unnamedblk1_1__DOT____Vrepeat0 = 2U;
    while (VL_LTS_III(32, 0U, tb_s2a_conv_tile_boundary__DOT__unnamedblk1_1__DOT____Vrepeat0)) {
        Vtb_s2a_conv_tile_boundary___024root____VbeforeTrig_h64692e26__0(vlSelf, 
                                                                         "@(negedge tb_s2a_conv_tile_boundary.clk)");
        co_await vlSelfRef.__VtrigSched_h64692e26__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(negedge tb_s2a_conv_tile_boundary.clk)", 
                                                             "source\\tb_s2a_conv_tile_boundary.sv", 
                                                             136);
        tb_s2a_conv_tile_boundary__DOT__unnamedblk1_1__DOT____Vrepeat0 
            = (tb_s2a_conv_tile_boundary__DOT__unnamedblk1_1__DOT____Vrepeat0 
               - (IData)(1U));
    }
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__hard_reset = 0U;
    Vtb_s2a_conv_tile_boundary___024root____VbeforeTrig_h64692e26__0(vlSelf, 
                                                                     "@(negedge tb_s2a_conv_tile_boundary.clk)");
    co_await vlSelfRef.__VtrigSched_h64692e26__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_conv_tile_boundary.clk)", 
                                                         "source\\tb_s2a_conv_tile_boundary.sv", 
                                                         137);
    if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__start_ready)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:137: Assertion failed in %m: start\346\234\252ready\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 137, "", false);
    }
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__start_valid = 1U;
    Vtb_s2a_conv_tile_boundary___024root____VbeforeTrig_h64692e26__0(vlSelf, 
                                                                     "@(negedge tb_s2a_conv_tile_boundary.clk)");
    co_await vlSelfRef.__VtrigSched_h64692e26__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_conv_tile_boundary.clk)", 
                                                         "source\\tb_s2a_conv_tile_boundary.sv", 
                                                         138);
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__start_valid = 0U;
    while ((0x13U != (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
        Vtb_s2a_conv_tile_boundary___024root____VbeforeTrig_h64692e26__0(vlSelf, 
                                                                         "@(negedge tb_s2a_conv_tile_boundary.clk)");
        co_await vlSelfRef.__VtrigSched_h64692e26__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(negedge tb_s2a_conv_tile_boundary.clk)", 
                                                             "source\\tb_s2a_conv_tile_boundary.sv", 
                                                             139);
    }
    tb_s2a_conv_tile_boundary__DOT__expected_error = 0U;
    if ((((((1U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode) 
            | (2U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode)) 
           | (0x0000000bU == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode)) 
          | (0x0000000cU == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode)) 
         | (0x0000000dU == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode))) {
        tb_s2a_conv_tile_boundary__DOT__expected_error = 1U;
    }
    if ((3U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode)) {
        tb_s2a_conv_tile_boundary__DOT__expected_error = 7U;
    }
    if ((0x0000000eU == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode)) {
        tb_s2a_conv_tile_boundary__DOT__expected_error = 3U;
    }
    if ((0x0000000fU == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode)) {
        tb_s2a_conv_tile_boundary__DOT__expected_error = 2U;
    }
    if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__result_error_latched) 
                      != tb_s2a_conv_tile_boundary__DOT__expected_error)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:145: Assertion failed in %m: \351\224\231\350\257\257\347\240\201 mode=%0d actual=%0d expected=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode
                     , '#',3,(IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__result_error_latched)
                     , '~',32,tb_s2a_conv_tile_boundary__DOT__expected_error);
        VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 145, "", false);
    }
    if (VL_UNLIKELY(((VL_LTES_III(32, 0x0000000bU, vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode) 
                      & (0U != (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__reads 
                                + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__writes)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:146: Assertion failed in %m: \351\235\236\346\263\225descriptor\346\234\211memory\345\211\257\344\275\234\347\224\250\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 146, "", false);
    }
    if (VL_UNLIKELY((((3U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode) 
                      & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__injected)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:147: Assertion failed in %m: overflow\346\234\252\346\263\250\345\205\245\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 147, "", false);
    }
    if (((0U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode) 
         | (4U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode))) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__expected_feature 
            = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_LENGTH_BYTES
            [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
               ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)
               : 0U)][0U];
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__expected_weight 
            = (((((IData)(7U) + ((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_H
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                                  : 0U)) >> 3U) * (
                                                   ((IData)(7U) 
                                                    + 
                                                    ((0x25U 
                                                      >= 
                                                      (0x0000003fU 
                                                       & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                                      ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
                                                     [
                                                     (0x0000003fU 
                                                      & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                                                      : 0U)) 
                                                   >> 3U)) 
               * ((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_WEIGHT_BYTES
                  [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                   : 0U));
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__expected_output 
            = ((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_LENGTH_BYTES
               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                : 0U);
        if (VL_UNLIKELY(((((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__feature_reads 
                            != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__expected_feature) 
                           | (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__weight_reads 
                              != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__expected_weight)) 
                          | (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__writes 
                             != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__expected_output))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:152: Assertion failed in %m: cache\345\244\215\347\224\250\350\256\241\346\225\260\351\224\231\350\257\257\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 152, "", false);
        }
        tb_s2a_conv_tile_boundary__DOT__i = 0U;
        while (VL_LTS_III(32, tb_s2a_conv_tile_boundary__DOT__i, vlSelfRef.tb_s2a_conv_tile_boundary__DOT__expected_output)) {
            if (VL_UNLIKELY(((1U & (~ ((0x4f37U >= 
                                        (0x00007fffU 
                                         & tb_s2a_conv_tile_boundary__DOT__i)) 
                                       && vlSelfRef.tb_s2a_conv_tile_boundary__DOT__seen
                                       [(0x00007fffU 
                                         & tb_s2a_conv_tile_boundary__DOT__i)])))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:153: Assertion failed in %m: \350\276\223\345\207\272\347\274\272\345\244\261\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 153, "", false);
            }
            tb_s2a_conv_tile_boundary__DOT__i = ((IData)(1U) 
                                                 + tb_s2a_conv_tile_boundary__DOT__i);
        }
    } else if (VL_UNLIKELY(((0U != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__writes)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:154: Assertion failed in %m: \345\274\202\345\270\270\346\227\266\345\267\262\346\234\211\350\276\223\345\207\272\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 154, "", false);
    }
    tb_s2a_conv_tile_boundary__DOT__i = 0U;
    __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__n 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__class_count[0U];
    tb_s2a_conv_tile_boundary__DOT____VlemCall_9__total_stalls = 0;
    __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__j = 0;
    tb_s2a_conv_tile_boundary__DOT____VlemCall_9__total_stalls 
        = VL_MULS_III(32, (IData)(0x0000000dU), VL_DIVS_III(32, __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__n, (IData)(5U)));
    __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__j = 0U;
    while (VL_LTS_III(32, __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__j, 
                      VL_MODDIVS_III(32, __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__n, (IData)(5U)))) {
        __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__3__n 
            = __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__j;
        __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__3__Vfuncout = 0;
        __Vtemp_1 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__3__n, (IData)(5U)), Vtb_s2a_conv_tile_boundary__ConstPool__CONST_hb4617e49_0);
        __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__3__Vfuncout 
            = Vtb_s2a_conv_tile_boundary__ConstPool__TABLE_hc6a14c36_0
            [__Vtemp_1];
        __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2____VlefCall_0__stalls 
            = __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__3__Vfuncout;
        tb_s2a_conv_tile_boundary__DOT____VlemCall_9__total_stalls 
            = (tb_s2a_conv_tile_boundary__DOT____VlemCall_9__total_stalls 
               + __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2____VlefCall_0__stalls);
        __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__j 
            = ((IData)(1U) + __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__j);
    }
    if (VL_UNLIKELY(((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__class_stalls[0U] 
                      != tb_s2a_conv_tile_boundary__DOT____VlemCall_9__total_stalls)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:155: Assertion failed in %m: stall\350\256\241\346\225\260\351\224\231\350\257\257\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 155, "", false);
    }
    tb_s2a_conv_tile_boundary__DOT__i = 1U;
    __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__n 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__class_count[1U];
    tb_s2a_conv_tile_boundary__DOT____VlemCall_9__total_stalls = 0;
    __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__j = 0;
    tb_s2a_conv_tile_boundary__DOT____VlemCall_9__total_stalls 
        = VL_MULS_III(32, (IData)(0x0000000dU), VL_DIVS_III(32, __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__n, (IData)(5U)));
    __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__j = 0U;
    while (VL_LTS_III(32, __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__j, 
                      VL_MODDIVS_III(32, __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__n, (IData)(5U)))) {
        __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__3__n 
            = __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__j;
        __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__3__Vfuncout = 0;
        __Vtemp_2 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__3__n, (IData)(5U)), Vtb_s2a_conv_tile_boundary__ConstPool__CONST_hb4617e49_0);
        __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__3__Vfuncout 
            = Vtb_s2a_conv_tile_boundary__ConstPool__TABLE_hc6a14c36_0
            [__Vtemp_2];
        __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2____VlefCall_0__stalls 
            = __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__3__Vfuncout;
        tb_s2a_conv_tile_boundary__DOT____VlemCall_9__total_stalls 
            = (tb_s2a_conv_tile_boundary__DOT____VlemCall_9__total_stalls 
               + __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2____VlefCall_0__stalls);
        __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__j 
            = ((IData)(1U) + __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__j);
    }
    if (VL_UNLIKELY(((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__class_stalls[1U] 
                      != tb_s2a_conv_tile_boundary__DOT____VlemCall_9__total_stalls)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:155: Assertion failed in %m: stall\350\256\241\346\225\260\351\224\231\350\257\257\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 155, "", false);
    }
    tb_s2a_conv_tile_boundary__DOT__i = 2U;
    __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__n 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__class_count[2U];
    tb_s2a_conv_tile_boundary__DOT____VlemCall_9__total_stalls = 0;
    __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__j = 0;
    tb_s2a_conv_tile_boundary__DOT____VlemCall_9__total_stalls 
        = VL_MULS_III(32, (IData)(0x0000000dU), VL_DIVS_III(32, __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__n, (IData)(5U)));
    __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__j = 0U;
    while (VL_LTS_III(32, __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__j, 
                      VL_MODDIVS_III(32, __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__n, (IData)(5U)))) {
        __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__3__n 
            = __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__j;
        __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__3__Vfuncout = 0;
        __Vtemp_3 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__3__n, (IData)(5U)), Vtb_s2a_conv_tile_boundary__ConstPool__CONST_hb4617e49_0);
        __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__3__Vfuncout 
            = Vtb_s2a_conv_tile_boundary__ConstPool__TABLE_hc6a14c36_0
            [__Vtemp_3];
        __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2____VlefCall_0__stalls 
            = __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__3__Vfuncout;
        tb_s2a_conv_tile_boundary__DOT____VlemCall_9__total_stalls 
            = (tb_s2a_conv_tile_boundary__DOT____VlemCall_9__total_stalls 
               + __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2____VlefCall_0__stalls);
        __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__j 
            = ((IData)(1U) + __Vfunc_tb_s2a_conv_tile_boundary__DOT__total_stalls__2__j);
    }
    if (VL_UNLIKELY(((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__class_stalls[2U] 
                      != tb_s2a_conv_tile_boundary__DOT____VlemCall_9__total_stalls)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:155: Assertion failed in %m: stall\350\256\241\346\225\260\351\224\231\350\257\257\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 155, "", false);
    }
    tb_s2a_conv_tile_boundary__DOT__i = 3U;
    tb_s2a_conv_tile_boundary__DOT__requests_before 
        = (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__reads 
           + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__writes);
    tb_s2a_conv_tile_boundary__DOT__unnamedblk1_2__DOT____Vrepeat1 = 5U;
    while (VL_LTS_III(32, 0U, tb_s2a_conv_tile_boundary__DOT__unnamedblk1_2__DOT____Vrepeat1)) {
        Vtb_s2a_conv_tile_boundary___024root____VbeforeTrig_h64692e26__0(vlSelf, 
                                                                         "@(negedge tb_s2a_conv_tile_boundary.clk)");
        co_await vlSelfRef.__VtrigSched_h64692e26__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(negedge tb_s2a_conv_tile_boundary.clk)", 
                                                             "source\\tb_s2a_conv_tile_boundary.sv", 
                                                             157);
        tb_s2a_conv_tile_boundary__DOT__unnamedblk1_2__DOT____Vrepeat1 
            = (tb_s2a_conv_tile_boundary__DOT__unnamedblk1_2__DOT____Vrepeat1 
               - (IData)(1U));
    }
    if (VL_UNLIKELY(((((0x13U != (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)) 
                       | ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__result_error_latched) 
                          != tb_s2a_conv_tile_boundary__DOT__expected_error)) 
                      | ((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__reads 
                          + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__writes) 
                         != tb_s2a_conv_tile_boundary__DOT__requests_before))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:158: Assertion failed in %m: result\350\203\214\345\216\213\346\234\237\351\227\264\345\217\221\347\224\237\345\211\257\344\275\234\347\224\250\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 158, "", false);
    }
    VL_WRITEF_NX("PASS TILE_BOUNDARY layer=%0d mode=%0d feature=%0d weight=%0d writes=%0d error=%0d cycles=%0d\n",7
                 , '~',32,vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id
                 , '~',32,vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode
                 , '~',32,vlSelfRef.tb_s2a_conv_tile_boundary__DOT__feature_reads
                 , '~',32,vlSelfRef.tb_s2a_conv_tile_boundary__DOT__weight_reads
                 , '~',32,vlSelfRef.tb_s2a_conv_tile_boundary__DOT__writes
                 , '#',3,(IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__result_error_latched)
                 , '~',32,vlSelfRef.tb_s2a_conv_tile_boundary__DOT__cycles);
    VL_FINISH_MT("source\\tb_s2a_conv_tile_boundary.sv", 160, "");
    co_return;
}

VlCoroutine Vtb_s2a_conv_tile_boundary___024root___eval_initial__TOP__Vtiming__1(Vtb_s2a_conv_tile_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___eval_initial__TOP__Vtiming__1\n"); );
    Vtb_s2a_conv_tile_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    while (VL_LIKELY(!vlSymsp->_vm_contextp__->gotFinish())) {
        co_await vlSelfRef.__VdlySched.delay(0x0000000000001388ULL, 
                                             nullptr, 
                                             "source\\tb_s2a_conv_tile_boundary.sv", 
                                             23);
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__clk 
            = (1U & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__clk)));
    }
    co_return;
}

bool Vtb_s2a_conv_tile_boundary___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___trigger_anySet__act\n"); );
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

void Vtb_s2a_conv_tile_boundary___024root___nba_sequent__TOP__0(Vtb_s2a_conv_tile_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___nba_sequent__TOP__0\n"); );
    Vtb_s2a_conv_tile_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_elements_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_elements_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__expected_weight_bytes_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_boundary__DOT__dut__DOT__expected_weight_bytes_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_end_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_end_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_end_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_end_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_end_wide);
    QData/*63:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_numerator;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_numerator = 0;
    QData/*63:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_numerator;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_numerator = 0;
    QData/*63:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_shape_span;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_shape_span = 0;
    QData/*63:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_shape_span;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_shape_span = 0;
    QData/*63:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_shape_product;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_shape_product = 0;
    QData/*63:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_shape_product;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_shape_product = 0;
    QData/*63:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_span_plus_stride;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_span_plus_stride = 0;
    QData/*63:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_span_plus_stride;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_span_plus_stride = 0;
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_height_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_height_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_width_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_width_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_bytes_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_bytes_wide);
    VlWide<4>/*127:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_weight_group_bytes_wide;
    VL_ZERO_W(128, tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_weight_group_bytes_wide);
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_index;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_index = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__1__n;
    __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__1__n = 0;
    CData/*0:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__rsp_valid;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__rsp_valid = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__rsp_data;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__rsp_data = 0;
    CData/*4:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_channels_latched;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_channels_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_latched;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_height;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_height = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_width;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_width = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_height;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_height = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_width;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_width = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_byte_count;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_byte_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_point_count;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_point_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_index;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_channel;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_channel = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_y;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_x;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_index;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_y;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_x;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_reduction_index;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_reduction_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_input_channel;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_input_channel = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_y;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_x;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_lane_index;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_lane_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_index;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_y;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_x;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_lane;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_lane = 0;
    IData/*31:0*/ __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_lane_index;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_lane_index = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v0;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v0 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_block__v0;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_block__v0 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_block__v0;
    __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_block__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_block__v0;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_block__v0 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v0;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v0;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v0 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v1;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v1;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v1 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v2;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v2 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v2;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v2 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v3;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v3 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v3;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v3 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v4;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v4 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v4;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v4 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v5;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v5 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v5;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v5 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v6;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v6 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v6;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v6 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v7;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v7 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v7;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v7 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v8;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v8 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v8;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v8 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v9;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v9 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v9;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v9 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v10;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v10 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v11;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v11 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v12;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v12 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v13;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v13 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v14;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v14 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v15;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v15 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v16;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v16 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v16;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v16 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v17;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v17 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v17;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v17 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v18;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v18 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v19;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v19 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v20;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v20 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v21;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v21 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v22;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v22 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v23;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v23 = 0;
    VlWide<3>/*79:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v8;
    VL_ZERO_W(80, __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v8);
    CData/*2:0*/ __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v8;
    __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v8 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v8;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v8 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias__v8;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias__v8 = 0;
    CData/*2:0*/ __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias__v8;
    __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias__v8 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v0;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v0 = 0;
    SData/*15:0*/ __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v0;
    __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v0;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v0 = 0;
    SData/*15:0*/ __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v1;
    __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v1;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v1 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v0;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v0 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v1;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v1;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v1 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v2;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v2 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v3;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v3 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v3;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v3 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v4;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v4 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v5;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v5 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v5;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v5 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v6;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v6 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v7;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v7 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v7;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v7 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v8;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v8 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v9;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v9 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v9;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v9 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v10;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v10 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v11;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v11 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v11;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v11 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v12;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v12 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v13;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v13 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v13;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v13 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    SData/*12:0*/ __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0;
    __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v14;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v14 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v15;
    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v15 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v15;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v15 = 0;
    IData/*31:0*/ __Vtemp_2;
    VlWide<4>/*127:0*/ __Vtemp_4;
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
    VlWide<4>/*127:0*/ __Vtemp_51;
    VlWide<4>/*127:0*/ __Vtemp_52;
    VlWide<4>/*127:0*/ __Vtemp_53;
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
    VlWide<4>/*127:0*/ __Vtemp_66;
    VlWide<4>/*127:0*/ __Vtemp_67;
    VlWide<4>/*127:0*/ __Vtemp_68;
    // Body
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v2 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v3 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v4 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v5 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v6 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v7 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v8 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v9 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v10 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v11 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v12 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v13 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v14 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v15 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v1 = 0U;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_height 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_height;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_point_count 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_point_count;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_index 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_index;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_index 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_index;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_block__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v1 = 0U;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_lane_index 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_lane_index;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_y 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_y;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_x 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_x;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_lane 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_lane;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_lane_index 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_lane_index;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v8 = 0U;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_channels_latched 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_channels_latched;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_width 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_width;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_height 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_height;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_width 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_width;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_byte_count 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_byte_count;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_index 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_index;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_channel 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_channel;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_y 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_y;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_x 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_x;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_y 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_y;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_x 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_x;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_reduction_index 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_reduction_index;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_input_channel 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_input_channel;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_y 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_y;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_x 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_x;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_latched 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_latched;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v1 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v2 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v3 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v4 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v5 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v6 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v7 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v8 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v9 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v16 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v17 = 0U;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 0U;
    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 0U;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__rsp_data 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_data;
    __Vdly__tb_s2a_conv_tile_boundary__DOT__rsp_valid 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_valid;
    if ((1U & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__hard_reset)))) {
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mapped_response_error))) 
              & (1U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mapped_response_error))) 
              & (2U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mapped_response_error))) 
              & (3U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mapped_response_error))) 
              & (4U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mapped_response_error))) 
              & (5U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mapped_response_error))) 
              & (6U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mapped_response_error))) 
              & (7U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        if ((((((9U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)) 
                & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_valid)) 
               & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mapped_response_error))) 
              & (0U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index)) 
             & (0x00001200U > vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index))) {
            if ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index))) {
                __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 
                    = (0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_data 
                                      >> (0x00000018U 
                                          & ((0x00030210U 
                                              >> ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_strobe_latched) 
                                                  << 1U)) 
                                             << 3U))));
                __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 
                    = (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index);
                __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0 = 1U;
            }
        }
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__cycles 
            = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__cycles);
        if (VL_UNLIKELY((VL_LTS_III(32, 0x00989680U, vlSelfRef.tb_s2a_conv_tile_boundary__DOT__cycles)))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:66: Assertion failed in %m: \345\221\250\346\234\237 watchdog\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 66, "", false);
        }
        __Vdly__tb_s2a_conv_tile_boundary__DOT__rsp_valid = 0U;
        if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__waiting) 
                          & ((((((~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_valid)) 
                                 | (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_address_latched 
                                    != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__held_addr)) 
                                | (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_wdata_latched 
                                   != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__held_data)) 
                               | ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_write) 
                                  != (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__held_write))) 
                              | ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rstrb) 
                                 != (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__held_rs))) 
                             | ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__wstrb) 
                                != (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__held_ws))))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:69: Assertion failed in %m: \345\201\234\351\241\277\350\257\267\346\261\202\344\270\215\347\250\263\345\256\232\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 69, "", false);
        }
        if ((((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_valid) 
              & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_ready))) 
             & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_valid)))) {
            if ((2U >= (3U & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__transfer_class))) {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__class_stalls[(3U 
                                                                        & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__transfer_class)] 
                    = ((IData)(1U) + ((2U >= (3U & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__transfer_class))
                                       ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__class_stalls
                                      [(3U & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__transfer_class)]
                                       : 0U));
            }
            if (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__waiting) {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__wait_count 
                    = (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__wait_count 
                       - (IData)(1U));
            } else {
                __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__1__n 
                    = ((2U >= (3U & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__transfer_class))
                        ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__class_count
                       [(3U & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__transfer_class)]
                        : 0U);
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__waiting = 1U;
                __Vtemp_2 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__1__n, (IData)(5U)), Vtb_s2a_conv_tile_boundary__ConstPool__CONST_hb4617e49_0);
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT____VlemCall_1__stalls 
                    = Vtb_s2a_conv_tile_boundary__ConstPool__TABLE_hc6a14c36_0
                    [__Vtemp_2];
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__held_addr 
                    = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_address_latched;
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__held_data 
                    = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_wdata_latched;
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__held_write 
                    = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_write;
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__held_rs 
                    = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rstrb;
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__held_ws 
                    = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__wstrb;
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__wait_count 
                    = (vlSelfRef.tb_s2a_conv_tile_boundary__DOT____VlemCall_1__stalls 
                       - (IData)(1U));
            }
        }
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_valid) 
             & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_ready))) {
            if ((2U >= (3U & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__transfer_class))) {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__class_count[(3U 
                                                                       & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__transfer_class)] 
                    = ((IData)(1U) + ((2U >= (3U & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__transfer_class))
                                       ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__class_count
                                      [(3U & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__transfer_class)]
                                       : 0U));
            }
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__waiting = 0U;
            if (VL_UNLIKELY(((0U != (3U & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_address_latched))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:80: Assertion failed in %m: \345\234\260\345\235\200\346\234\252word\345\257\271\351\275\220\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 80, "", false);
            }
            if ((1U == ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_write)
                         ? (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__wstrb)
                         : (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rstrb)))) {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__selected_lane = 0U;
            } else if ((2U == ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_write)
                                ? (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__wstrb)
                                : (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rstrb)))) {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__selected_lane = 1U;
            } else if ((4U == ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_write)
                                ? (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__wstrb)
                                : (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rstrb)))) {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__selected_lane = 2U;
            } else if (VL_LIKELY(((8U == ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_write)
                                           ? (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__wstrb)
                                           : (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rstrb)))))) {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__selected_lane = 3U;
            } else {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:83: Assertion failed in %m: \351\235\236one-hot strobe\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 83, "", false);
            }
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_error = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__rsp_valid = 1U;
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__byte_address 
                = (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_address_latched 
                   + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__selected_lane);
            __Vdly__tb_s2a_conv_tile_boundary__DOT__rsp_data = 0U;
            if (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_write) {
                if (VL_UNLIKELY(((((0U != (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rstrb)) 
                                   | (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__byte_address 
                                      < ((0x25U >= 
                                          (0x0000003fU 
                                           & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                          ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                                         [(0x0000003fU 
                                           & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                                          : 0U))) | 
                                  (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__byte_address 
                                   >= (((0x25U >= (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                                        [(0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                                         : 0U) + ((0x25U 
                                                   >= 
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                                   ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_LENGTH_BYTES
                                                  [
                                                  (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                                                   : 0U))))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:89: Assertion failed in %m: \350\276\223\345\207\272\350\257\267\346\261\202\350\266\212\347\225\214\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 89, "", false);
                }
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__writes 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__writes);
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__index_work 
                    = (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__byte_address 
                       - ((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                           ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                          [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                           : 0U));
                if (VL_UNLIKELY((((((0U != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode) 
                                    & (4U != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode)) 
                                   | ((0x4f37U >= (0x00007fffU 
                                                   & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__index_work)) 
                                      && vlSelfRef.tb_s2a_conv_tile_boundary__DOT__seen
                                      [(0x00007fffU 
                                        & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__index_work)])) 
                                  | ((0x000000ffU & 
                                      VL_SHIFTR_III(32,32,32, vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_wdata_latched, 
                                                    VL_MULS_III(32, (IData)(8U), vlSelfRef.tb_s2a_conv_tile_boundary__DOT__selected_lane))) 
                                     != ((0x4f37U >= 
                                          (0x00007fffU 
                                           & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__index_work))
                                          ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__expected
                                         [(0x00007fffU 
                                           & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__index_work)]
                                          : 0U)))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:92: Assertion failed in %m: \350\276\223\345\207\272\351\207\215\345\244\215/\345\274\202\345\270\270/\346\225\260\345\200\274\344\270\215\347\254\246 index=%0d\n",4, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '~',32,vlSelfRef.tb_s2a_conv_tile_boundary__DOT__index_work);
                    VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 92, "", false);
                }
                if ((0x4f37U >= (0x00007fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__index_work))) {
                    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__seen[(0x00007fffU 
                                                                    & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__index_work)] = 1U;
                }
            } else {
                if (VL_UNLIKELY((((0U != (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__wstrb)) 
                                  | (0U != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_wdata_latched))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:95: Assertion failed in %m: \350\257\273\350\257\267\346\261\202\346\220\272\345\270\246\345\206\231\345\255\227\346\256\265\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 95, "", false);
                }
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__reads 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__reads);
                if ((1U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__transfer_class)) {
                    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__index_work 
                        = ((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__byte_address 
                            - ((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_PACKAGE_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                                : 0U)) - ((0x25U >= 
                                           (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                           ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_WEIGHT_OFFSET
                                          [(0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                                           : 0U));
                    if (VL_UNLIKELY(((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_conv_tile_boundary__DOT__index_work) 
                                      | (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__index_work 
                                         >= ((0x25U 
                                              >= (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_WEIGHT_BYTES
                                             [(0x0000003fU 
                                               & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                                              : 0U)))))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:99: Assertion failed in %m: \346\235\203\351\207\215\350\266\212\347\225\214\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000));
                        VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 99, "", false);
                    }
                    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__weight_reads 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__weight_reads);
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__rsp_data 
                        = VL_SHIFTL_III(32,32,32, (
                                                   (2U 
                                                    == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode)
                                                    ? 0x80U
                                                    : 
                                                   ((0x3bffU 
                                                     >= 
                                                     (0x00003fffU 
                                                      & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__index_work))
                                                     ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__weights
                                                    [
                                                    (0x00003fffU 
                                                     & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__index_work)]
                                                     : 0U)), 
                                        VL_MULS_III(32, (IData)(8U), vlSelfRef.tb_s2a_conv_tile_boundary__DOT__selected_lane));
                } else {
                    if (VL_UNLIKELY((((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__byte_address 
                                       < vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_ADDRESS
                                       [((0x25U >= 
                                          (0x0000003fU 
                                           & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                          ? (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)
                                          : 0U)][0U]) 
                                      | (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__byte_address 
                                         >= (vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_ADDRESS
                                             [((0x25U 
                                                >= 
                                                (0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                                ? (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)
                                                : 0U)][0U] 
                                             + vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_LENGTH_BYTES
                                             [((0x25U 
                                                >= 
                                                (0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                                ? (0x0000003fU 
                                                   & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)
                                                : 0U)][0U])))))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_conv_tile_boundary.sv:103: Assertion failed in %m: \347\211\271\345\276\201\350\266\212\347\225\214\n",3, 'M',vlSymsp->name(),"tb_s2a_conv_tile_boundary", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000));
                        VL_STOP_MT("source\\tb_s2a_conv_tile_boundary.sv", 103, "", false);
                    }
                    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__feature_reads 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__feature_reads);
                    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__index_work 
                        = (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__byte_address 
                           - vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_ADDRESS
                           [((0x25U >= (0x0000003fU 
                                        & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                              ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)
                              : 0U)][0U]);
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__rsp_data 
                        = VL_SHIFTL_III(32,32,32, (
                                                   (1U 
                                                    == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode)
                                                    ? 0x80U
                                                    : 
                                                   ((0x0002a3ffU 
                                                     >= 
                                                     (0x0003ffffU 
                                                      & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__index_work))
                                                     ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__features
                                                    [
                                                    (0x0003ffffU 
                                                     & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__index_work)]
                                                     : 0U)), 
                                        VL_MULS_III(32, (IData)(8U), vlSelfRef.tb_s2a_conv_tile_boundary__DOT__selected_lane));
                }
            }
        }
    }
    if (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__hard_reset) {
        __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v2 = 1U;
        __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v4 = 1U;
        __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v6 = 1U;
        __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v8 = 1U;
        __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v10 = 1U;
        __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v12 = 1U;
        __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v14 = 1U;
        __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v0 = 1U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_in_bounds = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_data = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_layer_index_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_base_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_length_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_batch_count_latched = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_channels_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_height_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_width_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_base_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_length_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_batch_count_latched = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_left_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_right_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_top_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_bottom_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__groups_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__padding_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_base_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_length_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_offset_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_bytes_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_batch_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__activation_mode_latched = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_latched = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_height = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_width = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_height = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_width = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_byte_count = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_point_count = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_index = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_channel = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_y = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_x = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_index = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_y = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_x = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_reduction_index = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_input_channel = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_y = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_x = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_lane_index = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_index = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_y = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_x = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_lane = 0U;
        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_lane_index = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_address_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_strobe_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_wdata_latched = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__result_error_latched = 0U;
        __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v0 = 1U;
    } else {
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_enable) 
             & (1U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v3 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v3 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_enable) 
             & (2U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v5 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v5 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_enable) 
             & (3U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v7 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v7 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_enable) 
             & (4U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v9 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v9 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_enable) 
             & (5U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v11 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v11 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_enable) 
             & (6U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v13 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v13 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_enable) 
             & (7U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v15 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v15 = 1U;
        }
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_enable) 
             & (0U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count))) {
            __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v1 
                = ((0x11ffU >= (0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_reduction_index))
                    ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory
                   [(0x00001fffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_reduction_index)]
                    : 0U);
            __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v1 = 1U;
        }
        if (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_enable) {
            if (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_tap_in_bounds) {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_in_bounds = 1U;
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_data 
                    = ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_feature_index))
                        ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch
                       [(0x0000ffffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_feature_index)]
                        : 0U);
            } else {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_in_bounds = 0U;
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_data = 0U;
            }
        }
        if (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_advance) {
            if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_x) 
                 >= vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_width)) {
                if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_y) 
                     >= vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_height)) {
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_channel 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_channel);
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_y = 0U;
                } else {
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_y 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_y);
                }
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_x = 0U;
            } else {
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_x 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_x);
            }
        }
        if ((0x00000010U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
            if ((8U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__result_error_latched = 6U;
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x13U;
            } else if ((4U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__result_error_latched = 6U;
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x13U;
            } else if ((2U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
                if ((1U & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)))) {
                    if ((((IData)(8U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base) 
                         < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched)) {
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base 
                            = ((IData)(8U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base);
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 6U;
                    } else if (((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x 
                                 + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_width) 
                                < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched)) {
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x 
                            = ((IData)(8U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x);
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base = 0U;
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 2U;
                    } else if (((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y 
                                 + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_height) 
                                < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched)) {
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y 
                            = ((IData)(8U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y);
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base = 0U;
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x = 0U;
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 2U;
                    } else {
                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__result_error_latched = 0U;
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x13U;
                    }
                }
            } else if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
                if (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_valid) {
                    if ((0U != (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mapped_response_error))) {
                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__result_error_latched 
                            = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mapped_response_error;
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x13U;
                    } else {
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_index);
                        if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_x) 
                             >= vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_width)) {
                            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_y 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_y);
                            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_x = 0U;
                        } else {
                            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_x 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_x);
                        }
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x0fU;
                    }
                }
            } else if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_valid) 
                        & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_ready))) {
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x11U;
            }
        } else if ((8U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
            if ((4U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
                if ((2U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
                    if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
                        if ((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_lane_index 
                             >= vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
                            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x12U;
                        } else if ((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_index 
                                    >= vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_point_count)) {
                            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_lane_index 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_lane_index);
                            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_index = 0U;
                            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_y = 0U;
                            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_x = 0U;
                        } else {
                            __Vtemp_4[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_byte_offset_wide);
                            __Vtemp_4[1U] = (IData)(
                                                    (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_byte_offset_wide 
                                                     >> 0x00000020U));
                            __Vtemp_4[2U] = 0U;
                            __Vtemp_4[3U] = 0U;
                            if (((0x00000000ffffffffULL 
                                  < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_address_wide) 
                                 | VL_GTE_W(4, __Vtemp_4, vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_elements_wide))) {
                                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__result_error_latched = 2U;
                                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x13U;
                            } else {
                                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_address_latched 
                                    = ((IData)((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_address_wide 
                                                >> 2U)) 
                                       << 2U);
                                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_strobe_latched 
                                    = (0x0000000fU 
                                       & ((IData)(1U) 
                                          << (3U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_address_wide))));
                                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_wdata_latched 
                                    = VL_SHIFTL_III(32,32,32, vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_block
                                                    [
                                                    (0x000001ffU 
                                                     & ((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_lane_index 
                                                         << 6U) 
                                                        + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_index))], 
                                                    (0x00000018U 
                                                     & ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_address_wide) 
                                                        << 3U)));
                                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x10U;
                            }
                        }
                    } else {
                        if ((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_lane_index 
                             < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_block__v0 
                                = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__requantized_value;
                            __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_block__v0 
                                = (0x000001ffU & ((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_lane_index 
                                                   << 6U) 
                                                  + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_index));
                            __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_block__v0 = 1U;
                        }
                        if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_lane_index) 
                             >= vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
                            if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_index) 
                                 >= vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_point_count)) {
                                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_lane_index = 0U;
                                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_index = 0U;
                                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_y = 0U;
                                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_x = 0U;
                                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x0fU;
                            } else {
                                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_index 
                                    = ((IData)(1U) 
                                       + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_index);
                                if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_x) 
                                     >= vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_width)) {
                                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_y 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_y);
                                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_x = 0U;
                                } else {
                                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_x 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_x);
                                }
                                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_reduction_index = 0U;
                                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x0cU;
                            }
                        } else {
                            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_lane_index 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_lane_index);
                        }
                    }
                } else if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
                    if (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_bad_argument) {
                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__result_error_latched = 1U;
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x13U;
                    } else if (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_overflow) {
                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__result_error_latched = 7U;
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x13U;
                    } else {
                        if ((0U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v0 
                                = (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[0U]);
                            __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v0 = 1U;
                        }
                        if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_reduction_index) 
                             >= vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_latched)) {
                            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_lane_index = 0U;
                            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x0eU;
                        } else {
                            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_reduction_index 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_reduction_index);
                            if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_x) 
                                 >= vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched)) {
                                if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_y) 
                                     >= vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched)) {
                                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_input_channel 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_input_channel);
                                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_y = 0U;
                                } else {
                                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_y 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_y);
                                }
                                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_x = 0U;
                            } else {
                                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_x 
                                    = ((IData)(1U) 
                                       + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_x);
                            }
                        }
                        if ((1U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v1 
                                = (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[1U]);
                            __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v1 = 1U;
                        }
                        if ((2U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v2 
                                = (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[2U]);
                            __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v2 = 1U;
                        }
                        if ((3U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v3 
                                = (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[3U]);
                            __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v3 = 1U;
                        }
                        if ((4U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v4 
                                = (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[4U]);
                            __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v4 = 1U;
                        }
                        if ((5U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v5 
                                = (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[5U]);
                            __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v5 = 1U;
                        }
                        if ((6U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v6 
                                = (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[6U]);
                            __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v6 = 1U;
                        }
                        if ((7U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v7 
                                = (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[7U]);
                            __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v7 = 1U;
                        }
                    }
                } else {
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_input_channel = 0U;
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_y = 0U;
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_x = 0U;
                    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v8 
                        = ((0U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[0U]
                            : 0U);
                    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v8 = 1U;
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_reduction_index = 0U;
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x0dU;
                    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v9 
                        = ((1U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[1U]
                            : 0U);
                    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v9 = 1U;
                    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v10 
                        = ((2U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[2U]
                            : 0U);
                    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v11 
                        = ((3U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[3U]
                            : 0U);
                    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v12 
                        = ((4U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[4U]
                            : 0U);
                    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v13 
                        = ((5U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[5U]
                            : 0U);
                    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v14 
                        = ((6U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[6U]
                            : 0U);
                    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v15 
                        = ((7U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[7U]
                            : 0U);
                }
            } else if ((2U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_input_channel = 0U;
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_y = 0U;
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_x = 0U;
                    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v16 
                        = ((0U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[0U]
                            : 0U);
                    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v16 = 1U;
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_index = 0U;
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_reduction_index = 0U;
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x0dU;
                    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v17 
                        = ((1U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[1U]
                            : 0U);
                    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v17 = 1U;
                    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v18 
                        = ((2U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[2U]
                            : 0U);
                    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v19 
                        = ((3U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[3U]
                            : 0U);
                    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v20 
                        = ((4U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[4U]
                            : 0U);
                    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v21 
                        = ((5U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[5U]
                            : 0U);
                    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v22 
                        = ((6U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[6U]
                            : 0U);
                    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v23 
                        = ((7U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[7U]
                            : 0U);
                } else if (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_invalid) {
                    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__result_error_latched = 1U;
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x13U;
                } else {
                    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v8[0U] 
                        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[0U];
                    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v8[1U] 
                        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[1U];
                    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v8[2U] 
                        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[2U];
                    __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v8 
                        = (7U & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_lane);
                    __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v8 = 1U;
                    __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias__v8 
                        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_bias;
                    __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias__v8 
                        = (7U & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_lane);
                    if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_lane) 
                         >= vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x0bU;
                    } else {
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_lane 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_lane);
                    }
                }
            } else if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
                if (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_valid) {
                    if ((0U != (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mapped_response_error))) {
                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__result_error_latched 
                            = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mapped_response_error;
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x13U;
                    } else {
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index);
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 7U;
                    }
                }
            } else if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_valid) 
                        & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_ready))) {
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 9U;
            }
        } else if ((4U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
            if ((2U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
                    if ((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index 
                         >= vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_lane = 0U;
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x0aU;
                    } else if ((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index 
                                >= vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_latched)) {
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index);
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index = 0U;
                    } else if ((0x00000000ffffffffULL 
                                < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_source_address_wide)) {
                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__result_error_latched = 2U;
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x13U;
                    } else {
                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_address_latched 
                            = ((IData)((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_source_address_wide 
                                        >> 2U)) << 2U);
                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_strobe_latched 
                            = (0x0000000fU & ((IData)(1U) 
                                              << (3U 
                                                  & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_source_address_wide))));
                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_wdata_latched = 0U;
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 8U;
                    }
                } else if ((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base 
                            >= vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched)) {
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x12U;
                } else {
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count 
                        = ((8U <= (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched 
                                   - vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base))
                            ? 8U : (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched 
                                    - vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base));
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_y = 0U;
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_x = 0U;
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index = 0U;
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index = 0U;
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_lane = 0U;
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 7U;
                }
            } else if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
                if (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_valid) {
                    if ((0U != (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mapped_response_error))) {
                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__result_error_latched 
                            = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mapped_response_error;
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x13U;
                    } else {
                        if ((0xc7ffU >= (0x0000ffffU 
                                         & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_index))) {
                            __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v0 
                                = (0x000000ffU & VL_SHIFTR_III(8,32,32, vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_data, 
                                                               ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_byte_lane) 
                                                                << 3U)));
                            __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v0 
                                = (0x0000ffffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_index);
                            __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v0 = 1U;
                        }
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 3U;
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_index);
                    }
                }
            } else if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_valid) 
                        & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_ready))) {
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 5U;
            }
        } else if ((2U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
            if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
                if ((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_index 
                     >= vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_byte_count)) {
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base = 0U;
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 6U;
                } else if (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_in_bounds) {
                    if ((0x00000000ffffffffULL < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_source_address_wide)) {
                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__result_error_latched = 2U;
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x13U;
                    } else {
                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_address_latched 
                            = ((IData)((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_source_address_wide 
                                        >> 2U)) << 2U);
                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_strobe_latched 
                            = (0x0000000fU & ((IData)(1U) 
                                              << (3U 
                                                  & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_source_address_wide))));
                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_wdata_latched = 0U;
                        __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 4U;
                    }
                } else {
                    if ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_index))) {
                        __VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v1 
                            = (0x0000ffffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_index);
                        __VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v1 = 1U;
                    }
                    __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_index 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_index);
                }
            } else {
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_height 
                    = ((8U <= (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched 
                               - vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y))
                        ? 8U : (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched 
                                - vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y));
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_channel = 0U;
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_y = 0U;
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_x = 0U;
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_y = 0U;
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_x = 0U;
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_index = 0U;
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 3U;
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_width 
                    = ((8U <= (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched 
                               - vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x))
                        ? 8U : (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched 
                                - vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x));
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_height 
                    = (((((8U <= (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched 
                                  - vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y))
                           ? 8U : (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched 
                                   - vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y)) 
                         - (IData)(1U)) * vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched) 
                       + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched);
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_width 
                    = (((((8U <= (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched 
                                  - vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x))
                           ? 8U : (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched 
                                   - vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x)) 
                         - (IData)(1U)) * vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched) 
                       + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched);
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_byte_count 
                    = (((((((8U <= (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched 
                                    - vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y))
                             ? 8U : (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched 
                                     - vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y)) 
                           - (IData)(1U)) * vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched) 
                         + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched) 
                        * (((((8U <= (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched 
                                      - vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x))
                               ? 8U : (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched 
                                       - vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x)) 
                             - (IData)(1U)) * vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched) 
                           + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched)) 
                       * vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_channels_latched);
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_point_count 
                    = (((8U <= (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched 
                                - vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y))
                         ? 8U : (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched 
                                 - vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y)) 
                       * ((8U <= (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched 
                                  - vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x))
                           ? 8U : (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched 
                                   - vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x)));
            }
        } else if ((1U & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
            if (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__validation_ok) {
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_latched 
                    = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_wide[0U];
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 2U;
            } else {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__result_error_latched 
                    = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__validation_error;
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 0x13U;
            }
        } else if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__start_valid) 
                    & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__start_ready))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched 
                = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id;
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_layer_index_latched 
                = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id;
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_base_latched 
                = ((0x0000000fU == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode)
                    ? 0xfffffff0U : vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_ADDRESS
                   [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                      ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)
                      : 0U)][0U]);
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_length_latched 
                = ((0x0000000eU == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode)
                    ? (vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_LENGTH_BYTES
                       [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                          ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)
                          : 0U)][0U] - (IData)(1U))
                    : vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_LENGTH_BYTES
                   [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                      ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)
                      : 0U)][0U]);
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_batch_count_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_N
                [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                   ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)
                   : 0U)][0U];
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_channels_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_C
                [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                   ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)
                   : 0U)][0U];
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_height_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_H
                [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                   ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)
                   : 0U)][0U];
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_width_latched 
                = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_INPUT_W
                [((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                   ? (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)
                   : 0U)][0U];
            if ((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))) {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_base_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_ADDRESS
                    [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)];
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_batch_count_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_N
                    [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)];
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_C
                    [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)];
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
                    [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)];
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_H
                    [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)];
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_KERNEL_W
                    [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)];
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_H
                    [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)];
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_STRIDE_W
                    [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)];
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_left_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_LEFT
                    [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)];
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_right_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_RIGHT
                    [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)];
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_top_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_TOP
                    [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)];
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_bottom_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_PADDING_BOTTOM
                    [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)];
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_base_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_PACKAGE_BASE
                    [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)];
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_length_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_PACKAGE_LENGTH
                    [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)];
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_offset_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_WEIGHT_OFFSET
                    [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)];
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_bytes_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_WEIGHT_BYTES
                    [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)];
            } else {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_base_latched = 0U;
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_batch_count_latched = 0U;
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched = 0U;
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched = 0U;
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched = 0U;
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched = 0U;
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched = 0U;
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched = 0U;
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_left_latched = 0U;
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_right_latched = 0U;
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_top_latched = 0U;
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_bottom_latched = 0U;
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_base_latched = 0U;
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_length_latched = 0U;
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_offset_latched = 0U;
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_bytes_latched = 0U;
            }
            if ((0x0000000dU == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode)) {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_length_latched 
                    = (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_LENGTH_BYTES
                        [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                         : 0U) + (((0x25U >= (0x0000003fU 
                                              & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_C
                                   [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                                    : 0U) * ((0x25U 
                                              >= (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_W
                                             [(0x0000003fU 
                                               & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                                              : 0U)));
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched 
                    = ((IData)(1U) + ((0x25U >= (0x0000003fU 
                                                 & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                       ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_H
                                      [(0x0000003fU 
                                        & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                                       : 0U));
            } else if ((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))) {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_length_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_LENGTH_BYTES
                    [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)];
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OUTPUT_H
                    [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)];
            } else {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_length_latched = 0U;
                __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched = 0U;
            }
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__groups_latched 
                = ((0x0000000cU == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode)
                    ? 2U : 1U);
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__padding_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_batch_latched = 0U;
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__activation_mode_latched 
                = (2U & (- (IData)((0x0000000bU == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode))));
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_latched = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_index = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_channel = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_y = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_x = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_index = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_y = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_x = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_reduction_index = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_input_channel = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_y = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_x = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_lane_index = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_index = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_y = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_x = 0U;
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__result_error_latched = 0U;
            __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = 1U;
        }
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v0) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[0U] = 0U;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v1) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[0U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v1;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v2) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[1U] = 0U;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v3) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[1U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v3;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v4) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[2U] = 0U;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v5) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[2U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v5;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v6) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[3U] = 0U;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v7) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[3U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v7;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v8) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[4U] = 0U;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v9) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[4U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v9;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v10) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[5U] = 0U;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v11) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[5U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v11;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v12) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[6U] = 0U;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v13) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[6U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v13;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v14) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[7U] = 0U;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v15) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[7U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte__v15;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory[__VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory__v0;
    }
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_height 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_height;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_point_count 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_point_count;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_index 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_index;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_index 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_index;
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_block__v0) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_block[__VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_block__v0] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_block__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v0) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch[__VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v0] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v1) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch[__VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch__v1] = 0U;
    }
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_data 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__rsp_data;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_lane_index 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_lane_index;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_y 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_y;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_x 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_x;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_lane 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_lane;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_lane_index 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_lane_index;
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v0) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[0U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[0U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[0U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[1U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[1U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[1U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[2U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[2U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[2U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[3U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[3U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[3U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[4U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[4U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[4U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[5U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[5U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[5U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[6U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[6U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[6U][2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[7U][0U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[7U][1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[7U][2U] = 0U;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v8) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[__VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias__v8] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias__v8;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[__VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v8][0U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v8[0U];
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[__VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v8][1U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v8[1U];
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[__VdlyDim0__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v8][2U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter__v8[2U];
    }
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_channels_latched 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_channels_latched;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_width 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_width;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_height 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_height;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_width 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_width;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_byte_count 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_byte_count;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_index 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_index;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_channel 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_channel;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_y 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_y;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_x 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_x;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_y 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_y;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_x 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_x;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_input_channel 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_input_channel;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_y 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_y;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_x 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_x;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_reduction_index 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_reduction_index;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_latched 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_latched;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_valid 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__rsp_valid;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count;
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v0) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[0U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v0;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v1) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[1U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v1;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v2) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[2U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v2;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v3) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[3U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v3;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v4) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[4U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v4;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v5) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[5U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v5;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v6) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[6U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v6;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v7) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[7U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v7;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v8) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[0U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v8;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v9) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[1U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v9;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[2U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v10;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[3U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v11;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[4U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v12;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[5U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v13;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[6U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v14;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[7U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v15;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v16) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[0U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v16;
    }
    if (__VdlySet__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v17) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[1U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v17;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[2U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v18;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[3U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v19;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[4U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v20;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[5U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v21;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[6U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v22;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[7U] 
            = __VdlyVal__tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator__v23;
    }
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__state;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched 
        = __Vdly__tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_byte_lane 
        = (3U & (0x00030210U >> ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_strobe_latched) 
                                 << 1U)));
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_source_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_base_latched)) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_offset_latched)) 
              + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index)) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index)))))));
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_byte_offset_wide 
        = ((QData)((IData)((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_x 
                            + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x))) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched)) 
              * ((QData)((IData)((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_y 
                                  + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y))) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_lane_index)))))));
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_index = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_bias = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_invalid = 0U;
    if (((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_lane 
          < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count) 
         & (0x00000026U > vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched))) {
        tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_index 
            = ((((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched))
                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched)]
                  : 0U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base) 
               + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_lane);
        if ((0x00000c5cU > tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_index)) {
            if ((0x0c5bU >= (0x00000fffU & tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_index))) {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[0U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_index)][0U];
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_index)][1U];
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[2U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_index)][2U];
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_bias 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                    [(0x00000fffU & tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_index)];
            } else {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[0U] = 0U;
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[1U] = 0U;
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[2U] = 0U;
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_bias = 0U;
            }
            if (((((((((tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_index 
                        >= (((0x25U >= (0x0000003fU 
                                        & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched))
                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                             [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched)]
                              : 0U) + ((0x25U >= (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched))
                                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                       [(0x0000003fU 
                                         & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched)]
                                        : 0U))) | (0U 
                                                   == 
                                                   ((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[2U] 
                                                     << 0x00000010U) 
                                                    | (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                                       >> 0x00000010U)))) 
                      | (0U == ((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                 << 0x00000018U) | 
                                (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[0U] 
                                 >> 8U)))) | (0x3fffffffU 
                                              < ((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[2U] 
                                                  << 0x00000010U) 
                                                 | (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                                    >> 0x00000010U)))) 
                    | (0x3fffffffU < ((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                       << 0x00000018U) 
                                      | (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[0U] 
                                         >> 8U)))) 
                   | (0x2fU < (0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                              >> 8U)))) 
                  | (0x2fU < (0x000000ffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[0U]))) 
                 | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__activation_mode_latched)) 
                    & ((((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[2U] 
                          << 0x00000010U) | (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                             >> 0x00000010U)) 
                        != ((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                             << 0x00000018U) | (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[0U] 
                                                >> 8U))) 
                       | ((0x000000ffU & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[1U] 
                                          >> 8U)) != 
                          (0x000000ffU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter[0U])))))) {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_invalid = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_invalid = 1U;
        }
    } else if ((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_lane 
                < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_invalid = 1U;
    }
    __Vtemp_13[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_batch_count_latched;
    __Vtemp_13[1U] = 0U;
    __Vtemp_13[2U] = 0U;
    __Vtemp_13[3U] = 0U;
    __Vtemp_14[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_channels_latched;
    __Vtemp_14[1U] = 0U;
    __Vtemp_14[2U] = 0U;
    __Vtemp_14[3U] = 0U;
    VL_MUL_W(4, __Vtemp_15, __Vtemp_13, __Vtemp_14);
    __Vtemp_16[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_height_latched;
    __Vtemp_16[1U] = 0U;
    __Vtemp_16[2U] = 0U;
    __Vtemp_16[3U] = 0U;
    VL_MUL_W(4, __Vtemp_17, __Vtemp_15, __Vtemp_16);
    __Vtemp_18[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_width_latched;
    __Vtemp_18[1U] = 0U;
    __Vtemp_18[2U] = 0U;
    __Vtemp_18[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_elements_wide, __Vtemp_17, __Vtemp_18);
    __Vtemp_19[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_batch_count_latched;
    __Vtemp_19[1U] = 0U;
    __Vtemp_19[2U] = 0U;
    __Vtemp_19[3U] = 0U;
    __Vtemp_20[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched;
    __Vtemp_20[1U] = 0U;
    __Vtemp_20[2U] = 0U;
    __Vtemp_20[3U] = 0U;
    VL_MUL_W(4, __Vtemp_21, __Vtemp_19, __Vtemp_20);
    __Vtemp_22[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched;
    __Vtemp_22[1U] = 0U;
    __Vtemp_22[2U] = 0U;
    __Vtemp_22[3U] = 0U;
    VL_MUL_W(4, __Vtemp_23, __Vtemp_21, __Vtemp_22);
    __Vtemp_24[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched;
    __Vtemp_24[1U] = 0U;
    __Vtemp_24[2U] = 0U;
    __Vtemp_24[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_elements_wide, __Vtemp_23, __Vtemp_24);
    __Vtemp_25[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched;
    __Vtemp_25[1U] = 0U;
    __Vtemp_25[2U] = 0U;
    __Vtemp_25[3U] = 0U;
    __Vtemp_26[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_channels_latched;
    __Vtemp_26[1U] = 0U;
    __Vtemp_26[2U] = 0U;
    __Vtemp_26[3U] = 0U;
    VL_MUL_W(4, __Vtemp_27, __Vtemp_25, __Vtemp_26);
    __Vtemp_28[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched;
    __Vtemp_28[1U] = 0U;
    __Vtemp_28[2U] = 0U;
    __Vtemp_28[3U] = 0U;
    VL_MUL_W(4, __Vtemp_29, __Vtemp_27, __Vtemp_28);
    __Vtemp_30[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched;
    __Vtemp_30[1U] = 0U;
    __Vtemp_30[2U] = 0U;
    __Vtemp_30[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__expected_weight_bytes_wide, __Vtemp_29, __Vtemp_30);
    __Vtemp_31[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_channels_latched;
    __Vtemp_31[1U] = 0U;
    __Vtemp_31[2U] = 0U;
    __Vtemp_31[3U] = 0U;
    __Vtemp_32[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched;
    __Vtemp_32[1U] = 0U;
    __Vtemp_32[2U] = 0U;
    __Vtemp_32[3U] = 0U;
    VL_MUL_W(4, __Vtemp_33, __Vtemp_31, __Vtemp_32);
    __Vtemp_34[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched;
    __Vtemp_34[1U] = 0U;
    __Vtemp_34[2U] = 0U;
    __Vtemp_34[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_wide, __Vtemp_33, __Vtemp_34);
    __Vtemp_35[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_base_latched;
    __Vtemp_35[1U] = 0U;
    __Vtemp_35[2U] = 0U;
    __Vtemp_35[3U] = 0U;
    __Vtemp_36[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_length_latched;
    __Vtemp_36[1U] = 0U;
    __Vtemp_36[2U] = 0U;
    __Vtemp_36[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_end_wide, __Vtemp_35, __Vtemp_36);
    __Vtemp_37[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_base_latched;
    __Vtemp_37[1U] = 0U;
    __Vtemp_37[2U] = 0U;
    __Vtemp_37[3U] = 0U;
    __Vtemp_38[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_length_latched;
    __Vtemp_38[1U] = 0U;
    __Vtemp_38[2U] = 0U;
    __Vtemp_38[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_end_wide, __Vtemp_37, __Vtemp_38);
    __Vtemp_39[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_base_latched;
    __Vtemp_39[1U] = 0U;
    __Vtemp_39[2U] = 0U;
    __Vtemp_39[3U] = 0U;
    __Vtemp_40[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_length_latched;
    __Vtemp_40[1U] = 0U;
    __Vtemp_40[2U] = 0U;
    __Vtemp_40[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_end_wide, __Vtemp_39, __Vtemp_40);
    __Vtemp_41[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_offset_latched;
    __Vtemp_41[1U] = 0U;
    __Vtemp_41[2U] = 0U;
    __Vtemp_41[3U] = 0U;
    __Vtemp_42[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_bytes_latched;
    __Vtemp_42[1U] = 0U;
    __Vtemp_42[2U] = 0U;
    __Vtemp_42[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_end_wide, __Vtemp_41, __Vtemp_42);
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_height_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_top_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_bottom_latched)));
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_width_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_left_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_right_latched)));
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_shape_span 
        = (tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_numerator 
           - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched)));
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_shape_span 
        = (tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_numerator 
           - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched)));
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_shape_product 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched)));
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_shape_product 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched)));
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_span_plus_stride 
        = (tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_shape_span 
           + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched)));
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_span_plus_stride 
        = (tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_shape_span 
           + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched)));
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_height_wide[0U] = 0U;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_height_wide[1U] = 0U;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_height_wide[2U] = 0U;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_height_wide[3U] = 0U;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_width_wide[0U] = 0U;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_width_wide[1U] = 0U;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_width_wide[2U] = 0U;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_width_wide[3U] = 0U;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_bytes_wide[0U] = 0U;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_bytes_wide[1U] = 0U;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_bytes_wide[2U] = 0U;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_bytes_wide[3U] = 0U;
    if (((0U != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched) 
         & (0U != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched))) {
        __Vtemp_43[0U] = (((8U > vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched)
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched
                            : 8U) - (IData)(1U));
        __Vtemp_43[1U] = 0U;
        __Vtemp_43[2U] = 0U;
        __Vtemp_43[3U] = 0U;
        __Vtemp_44[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched;
        __Vtemp_44[1U] = 0U;
        __Vtemp_44[2U] = 0U;
        __Vtemp_44[3U] = 0U;
        VL_MUL_W(4, __Vtemp_45, __Vtemp_43, __Vtemp_44);
        __Vtemp_46[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched;
        __Vtemp_46[1U] = 0U;
        __Vtemp_46[2U] = 0U;
        __Vtemp_46[3U] = 0U;
        VL_ADD_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_height_wide, __Vtemp_45, __Vtemp_46);
        __Vtemp_47[0U] = (((8U > vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched)
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched
                            : 8U) - (IData)(1U));
        __Vtemp_47[1U] = 0U;
        __Vtemp_47[2U] = 0U;
        __Vtemp_47[3U] = 0U;
        __Vtemp_48[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched;
        __Vtemp_48[1U] = 0U;
        __Vtemp_48[2U] = 0U;
        __Vtemp_48[3U] = 0U;
        VL_MUL_W(4, __Vtemp_49, __Vtemp_47, __Vtemp_48);
        __Vtemp_50[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched;
        __Vtemp_50[1U] = 0U;
        __Vtemp_50[2U] = 0U;
        __Vtemp_50[3U] = 0U;
        VL_ADD_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_width_wide, __Vtemp_49, __Vtemp_50);
        VL_MUL_W(4, __Vtemp_51, tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_height_wide, tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_width_wide);
        __Vtemp_52[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_channels_latched;
        __Vtemp_52[1U] = 0U;
        __Vtemp_52[2U] = 0U;
        __Vtemp_52[3U] = 0U;
        VL_MUL_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_bytes_wide, __Vtemp_51, __Vtemp_52);
    }
    __Vtemp_53[0U] = ((8U > vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched)
                       ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched
                       : 8U);
    __Vtemp_53[1U] = 0U;
    __Vtemp_53[2U] = 0U;
    __Vtemp_53[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_weight_group_bytes_wide, __Vtemp_53, vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_wide);
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__validation_ok = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__validation_error = 1U;
    __Vtemp_55[0U] = 0x00001200U;
    __Vtemp_55[1U] = 0U;
    __Vtemp_55[2U] = 0U;
    __Vtemp_55[3U] = 0U;
    if ((((((((((((((((((((((1U < (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__activation_mode_latched)) 
                            | (1U != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_batch_count_latched)) 
                           | (1U != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_batch_count_latched)) 
                          | (0U != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_batch_latched)) 
                         | (0U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_channels_latched)) 
                        | (0U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_height_latched)) 
                       | (0U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_width_latched)) 
                      | (0U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched)) 
                     | (0U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched)) 
                    | (0U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched)) 
                   | (0U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched)) 
                  | (0U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched)) 
                 | (0U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched)) 
                | (0U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched)) 
               | (1U != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__groups_latched)) 
              | (0U != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__padding_latched)) 
             | (0U == (((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_wide[0U] 
                         | vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_wide[1U]) 
                        | vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_wide[2U]) 
                       | vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_wide[3U]))) 
            | VL_LT_W(4, __Vtemp_55, vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_wide)) 
           | (0x00000026U <= vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched)) 
          | ((0x00000026U > vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched) 
             & (0U != ((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched))
                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OP
                       [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched)]
                        : 0U)))) | (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched 
                                    != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_layer_index_latched))) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__validation_error 
            = (((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched 
                 != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_layer_index_latched) 
                | (0x00000026U <= vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched))
                ? 2U : 1U);
    } else {
        __Vtemp_56[0U] = 0xffffffffU;
        __Vtemp_56[1U] = 0U;
        __Vtemp_56[2U] = 0U;
        __Vtemp_56[3U] = 0U;
        __Vtemp_57[0U] = 0xffffffffU;
        __Vtemp_57[1U] = 0U;
        __Vtemp_57[2U] = 0U;
        __Vtemp_57[3U] = 0U;
        __Vtemp_58[0U] = 0xffffffffU;
        __Vtemp_58[1U] = 0U;
        __Vtemp_58[2U] = 0U;
        __Vtemp_58[3U] = 0U;
        if ((((((VL_LT_W(4, __Vtemp_56, tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_elements_wide) 
                 | (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_length_latched 
                    != tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_elements_wide[0U])) 
                | VL_LT_W(4, __Vtemp_57, vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_elements_wide)) 
               | (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_length_latched 
                  != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_elements_wide[0U])) 
              | VL_LT_W(4, __Vtemp_58, tb_s2a_conv_tile_boundary__DOT__dut__DOT__expected_weight_bytes_wide)) 
             | (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_bytes_latched 
                != tb_s2a_conv_tile_boundary__DOT__dut__DOT__expected_weight_bytes_wide[0U]))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__validation_error = 3U;
        } else {
            __Vtemp_59[0U] = 0U;
            __Vtemp_59[1U] = 1U;
            __Vtemp_59[2U] = 0U;
            __Vtemp_59[3U] = 0U;
            __Vtemp_60[0U] = 0U;
            __Vtemp_60[1U] = 1U;
            __Vtemp_60[2U] = 0U;
            __Vtemp_60[3U] = 0U;
            __Vtemp_61[0U] = 0U;
            __Vtemp_61[1U] = 1U;
            __Vtemp_61[2U] = 0U;
            __Vtemp_61[3U] = 0U;
            __Vtemp_62[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_length_latched;
            __Vtemp_62[1U] = 0U;
            __Vtemp_62[2U] = 0U;
            __Vtemp_62[3U] = 0U;
            __Vtemp_63[0U] = 0x00000c5cU;
            __Vtemp_63[1U] = 0U;
            __Vtemp_63[2U] = 0U;
            __Vtemp_63[3U] = 0U;
            __Vtemp_64[0U] = ((0x25U >= (0x0000003fU 
                                         & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched))
                               ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                              [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched)]
                               : 0U);
            __Vtemp_64[1U] = 0U;
            __Vtemp_64[2U] = 0U;
            __Vtemp_64[3U] = 0U;
            __Vtemp_65[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched;
            __Vtemp_65[1U] = 0U;
            __Vtemp_65[2U] = 0U;
            __Vtemp_65[3U] = 0U;
            VL_ADD_W(4, __Vtemp_66, __Vtemp_64, __Vtemp_65);
            __Vtemp_67[0U] = 0x0000c800U;
            __Vtemp_67[1U] = 0U;
            __Vtemp_67[2U] = 0U;
            __Vtemp_67[3U] = 0U;
            __Vtemp_68[0U] = 0x00009000U;
            __Vtemp_68[1U] = 0U;
            __Vtemp_68[2U] = 0U;
            __Vtemp_68[3U] = 0U;
            if (((((((((VL_LT_W(4, __Vtemp_59, tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_end_wide) 
                        | VL_LT_W(4, __Vtemp_60, tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_end_wide)) 
                       | VL_LT_W(4, __Vtemp_61, tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_end_wide)) 
                      | (0U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_length_latched)) 
                     | VL_GT_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_end_wide, __Vtemp_62)) 
                    | (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                        [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched)]
                         : 0U) != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched)) 
                   | VL_LT_W(4, __Vtemp_63, __Vtemp_66)) 
                  | VL_LT_W(4, __Vtemp_67, tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_bytes_wide)) 
                 | VL_LT_W(4, __Vtemp_68, tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_weight_group_bytes_wide))) {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__validation_error = 2U;
            } else if (((((((tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_numerator 
                             < (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched))) 
                            | (tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_numerator 
                               < (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched)))) 
                           | (tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_shape_product 
                              <= tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_shape_span)) 
                          | (tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_shape_product 
                             > tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_span_plus_stride)) 
                         | (tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_shape_product 
                            <= tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_shape_span)) 
                        | (tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_shape_product 
                           > tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_span_plus_stride))) {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__validation_error = 1U;
            } else {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__validation_ok = 1U;
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__validation_error = 0U;
            }
        }
    }
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_base_latched)) 
           + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_byte_offset_wide);
}

void Vtb_s2a_conv_tile_boundary___024root___nba_comb__TOP__0(Vtb_s2a_conv_tile_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___nba_comb__TOP__0\n"); );
    Vtb_s2a_conv_tile_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT____VlemCall_0__stalls;
    QData/*63:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_plane_bytes;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_plane_bytes = 0;
    QData/*63:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_input_y;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_input_y = 0;
    QData/*63:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_input_x;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_input_x = 0;
    QData/*63:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_source_offset;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_source_offset = 0;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_area;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_area = 0;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_next_input_channel;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_next_input_channel = 0;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_next_kernel_y;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_next_kernel_y = 0;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_next_reduction_index;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_next_reduction_index = 0;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_point_y;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_point_y = 0;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_point_x;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_point_x = 0;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_input_channel;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_input_channel = 0;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_kernel_y;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_kernel_y = 0;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_kernel_x;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_kernel_x = 0;
    QData/*63:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_input_y;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_input_y = 0;
    QData/*63:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_input_x;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_input_x = 0;
    QData/*63:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_feature_index_wide;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_feature_index_wide = 0;
    VlWide<3>/*79:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_parameter;
    VL_ZERO_W(80, tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_parameter);
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_accumulator;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_accumulator = 0;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_multiplier;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_multiplier = 0;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_q_shift;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_q_shift = 0;
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_magnitude;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_magnitude = 0;
    QData/*63:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_product;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_product = 0;
    QData/*63:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_rounding_add;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_rounding_add = 0;
    QData/*63:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_rounded_magnitude;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_rounded_magnitude = 0;
    QData/*63:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_signed_value;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_signed_value = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__0__n;
    __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__0__n = 0;
    VlWide<3>/*95:0*/ __Vtemp_2;
    VlWide<3>/*95:0*/ __Vtemp_3;
    IData/*31:0*/ __Vtemp_5;
    // Body
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__hard_reset)) 
           & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)));
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rstrb = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__wstrb = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_write = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_valid = 0U;
    if ((1U & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__hard_reset)))) {
        if (((4U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rstrb 
                = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_strobe_latched;
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_write = 0U;
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_valid = 1U;
        } else if ((0x10U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_write = 1U;
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_valid = 1U;
        }
        if ((1U & (~ ((4U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)) 
                      || (8U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)))))) {
            if ((0x10U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__wstrb 
                    = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_strobe_latched;
            }
        }
    }
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_parameter[0U] = 0U;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_parameter[1U] = 0U;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_parameter[2U] = 0U;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_accumulator = 0U;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_multiplier = 0U;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_q_shift = 0U;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_magnitude = 0U;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_product = 0ULL;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_rounding_add = 0ULL;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_rounded_magnitude = 0ULL;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_signed_value = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__requantized_value = 0U;
    if (((8U > vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_lane_index) 
         & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_lane_index 
            < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count))) {
        tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_parameter[0U] 
            = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_lane_index)][0U];
        tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_parameter[1U] 
            = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_lane_index)][1U];
        tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_parameter[2U] 
            = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_lane_index)][2U];
        tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_accumulator 
            = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator
            [(7U & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_lane_index)];
        if ((tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_accumulator 
             >> 0x1fU)) {
            tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_multiplier 
                = ((tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_parameter[1U] 
                    << 0x00000018U) | (tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_parameter[0U] 
                                       >> 8U));
            tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_magnitude 
                = ((IData)(1U) + (~ tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_accumulator));
            tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_q_shift 
                = (0x000000ffU & tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_parameter[0U]);
        } else {
            tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_multiplier 
                = ((tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_parameter[2U] 
                    << 0x00000010U) | (tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_parameter[1U] 
                                       >> 0x00000010U));
            tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_magnitude 
                = tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_accumulator;
            tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_q_shift 
                = (0x000000ffU & (tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_parameter[1U] 
                                  >> 8U));
        }
        tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_product 
            = ((QData)((IData)(tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_magnitude)) 
               * (QData)((IData)(tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_multiplier)));
        if ((0U != tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_q_shift)) {
            tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_rounding_add 
                = VL_SHIFTL_QQI(64,64,32, 1ULL, (tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_q_shift 
                                                 - (IData)(1U)));
        }
        tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_rounded_magnitude 
            = VL_SHIFTR_QQI(64,64,32, (tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_product 
                                       + tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_rounding_add), tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_q_shift);
        __Vtemp_2[0U] = (IData)(tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_rounded_magnitude);
        __Vtemp_2[1U] = (IData)((tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_rounded_magnitude 
                                 >> 0x00000020U));
        __Vtemp_2[2U] = 0U;
        VL_NEGATE_W(3, __Vtemp_3, __Vtemp_2);
        tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_signed_value 
            = ((tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_accumulator 
                >> 0x1fU) ? (((QData)((IData)(__Vtemp_3[1U])) 
                              << 0x00000020U) | (QData)((IData)(__Vtemp_3[0U])))
                : tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_rounded_magnitude);
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__requantized_value 
            = (VL_LTS_IQQ(64, 0x000000000000007fULL, tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_signed_value)
                ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_signed_value)
                                  ? 0x00000081U : (0x000000ffU 
                                                   & (IData)(tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_signed_value))));
    }
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_plane_bytes 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_height)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_width)));
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_input_y = 0ULL;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_input_x = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_in_bounds = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_advance = 0U;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_source_offset = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_source_address_wide = 0ULL;
    if (((0ULL != tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_plane_bytes) 
         & (0U != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_width))) {
        tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_input_y 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_top_latched)));
        tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_input_x 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_input_y, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_input_x, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_width_latched))));
        if (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_in_bounds) {
            tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_source_offset 
                = (((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_channel)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_height_latched))) 
                     + tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_input_y) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_width_latched))) 
                   + tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_input_x);
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_source_address_wide 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_base_latched)) 
                   + tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_source_offset);
        }
    }
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_area 
        = (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched 
           * vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched);
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_next_input_channel 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_input_channel;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_next_kernel_y 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_y;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_next_reduction_index 
        = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_reduction_index);
    if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_x) 
         >= vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched)) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_next_kernel_x = 0U;
        if ((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_y) 
             >= vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched)) {
            tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_next_kernel_y = 0U;
            tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_next_input_channel 
                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_input_channel);
        } else {
            tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_next_kernel_y 
                = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_y);
        }
    } else {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_next_kernel_x 
            = ((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_x);
    }
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_point_y 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_y;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_point_x 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_x;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_input_channel 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_input_channel;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_kernel_y 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_y;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_kernel_x 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_x;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_reduction_index 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_reduction_index;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_input_y = 0ULL;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_input_x = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_tap_in_bounds = 0U;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_feature_index_wide = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_feature_index = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_enable = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_bad_argument = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_overflow = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[0U] = 0ULL;
    if ((0U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[0U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[0U] 
            = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[0U];
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[0U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[0U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[0U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[0U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[0U])));
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[0U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[0U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[0U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[0U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[0U])))));
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[0U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[0U])))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[0U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[0U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[1U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[1U] = 0ULL;
    if ((1U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[1U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[1U] 
            = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[1U];
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[1U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[1U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[1U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[1U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[1U])));
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[1U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[1U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[1U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[1U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[1U])))));
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[1U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[1U])))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[1U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[1U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[2U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[2U] = 0ULL;
    if ((2U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[2U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[2U] 
            = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[2U];
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[2U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[2U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[2U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[2U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[2U])));
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[2U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[2U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[2U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[2U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[2U])))));
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[2U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[2U])))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[2U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[2U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[3U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[3U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[3U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[3U] = 0ULL;
    if ((3U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[3U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[3U] 
            = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[3U];
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[3U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[3U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[3U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[3U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[3U])));
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[3U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[3U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[3U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[3U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[3U])))));
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[3U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[3U])))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[3U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[3U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[4U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[4U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[4U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[4U] = 0ULL;
    if ((4U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[4U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[4U] 
            = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[4U];
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[4U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[4U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[4U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[4U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[4U])));
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[4U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[4U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[4U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[4U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[4U])))));
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[4U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[4U])))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[4U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[4U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[5U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[5U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[5U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[5U] = 0ULL;
    if ((5U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[5U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[5U] 
            = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[5U];
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[5U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[5U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[5U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[5U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[5U])));
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[5U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[5U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[5U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[5U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[5U])))));
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[5U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[5U])))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[5U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[5U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[6U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[6U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[6U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[6U] = 0ULL;
    if ((6U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[6U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[6U] 
            = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[6U];
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[6U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[6U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[6U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[6U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[6U])));
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[6U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[6U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[6U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[6U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[6U])))));
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[6U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[6U])))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[6U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[6U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[7U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[7U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[7U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[7U] = 0ULL;
    if ((7U < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[7U] 
            = ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[7U] 
            = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[7U];
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[7U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[7U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[7U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[7U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[7U])));
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[7U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[7U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[7U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[7U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[7U])))));
        if (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[7U]) 
                | (0x80U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[7U])))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[7U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[7U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_overflow = 1U;
        }
    }
    if (((0x0bU == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)) 
         | (0x0cU == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)))) {
        tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_point_y 
            = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_y;
        tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_point_x 
            = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_x;
        tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_input_channel = 0U;
        tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_kernel_y = 0U;
        tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_kernel_x = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_reduction_index = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_enable = 1U;
    } else if ((0x0dU == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
        if ((((((IData)(1U) + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_reduction_index) 
               < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_latched) 
              & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_bad_argument))) 
             & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_overflow)))) {
            tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_point_y 
                = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_y;
            tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_point_x 
                = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_x;
            tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_input_channel 
                = tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_next_input_channel;
            tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_kernel_y 
                = tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_next_kernel_y;
            tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_kernel_x 
                = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_next_kernel_x;
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_reduction_index 
                = tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_next_reduction_index;
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_enable = 1U;
        }
    }
    if (((0U != tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_area) 
         & (0U != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_width))) {
        tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_input_y 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched))) 
                 + ((QData)((IData)(tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_point_y)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched)))) 
                + (QData)((IData)(tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_kernel_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_top_latched)));
        tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_input_x 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched))) 
                 + ((QData)((IData)(tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_point_x)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched)))) 
                + (QData)((IData)(tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_kernel_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_tap_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_input_y, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_input_x, (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_width_latched))));
        tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_feature_index_wide 
            = (((((QData)((IData)(tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_input_channel)) 
                  * tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_plane_bytes) 
                 + ((((QData)((IData)(tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_point_y)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched))) 
                     + (QData)((IData)(tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_kernel_y))) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_width)))) 
                + ((QData)((IData)(tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_point_x)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched)))) 
               + (QData)((IData)(tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_kernel_x)));
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_feature_index 
            = (IData)(tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_feature_index_wide);
    }
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mapped_response_error = 6U;
    if ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_error))) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mapped_response_error = 0U;
    } else if ((((1U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_error)) 
                 | (2U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_error))) 
                | (6U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_error)))) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mapped_response_error 
            = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_error;
    }
    if ((((3U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)) 
          & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_index 
             < vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_byte_count)) 
         & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_in_bounds)))) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_advance = 1U;
    } else if ((((5U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)) 
                 & (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_valid)) 
                & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__mapped_response_error)))) {
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_advance = 1U;
    }
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__transfer_class 
        = ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_write)
            ? 2U : (((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_address_latched 
                      >= ((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                           ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_PACKAGE_BASE
                          [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                           : 0U)) & (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_address_latched 
                                     < (((0x25U >= 
                                          (0x0000003fU 
                                           & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                          ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_PACKAGE_BASE
                                         [(0x0000003fU 
                                           & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                                          : 0U) + (
                                                   (0x25U 
                                                    >= 
                                                    (0x0000003fU 
                                                     & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_PACKAGE_LENGTH
                                                   [
                                                   (0x0000003fU 
                                                    & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                                                    : 0U))))
                     ? 1U : 0U));
    __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__0__n 
        = ((2U >= (3U & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__transfer_class))
            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__class_count
           [(3U & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__transfer_class)]
            : 0U);
    __Vtemp_5 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__0__n, (IData)(5U)), Vtb_s2a_conv_tile_boundary__ConstPool__CONST_hb4617e49_0);
    tb_s2a_conv_tile_boundary__DOT____VlemCall_0__stalls 
        = Vtb_s2a_conv_tile_boundary__ConstPool__TABLE_hc6a14c36_0
        [__Vtemp_5];
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_ready 
        = ((((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_valid) 
             & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__hard_reset))) 
            & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_valid))) 
           & (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__waiting) 
               & (0U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__wait_count)) 
              | ((~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__waiting)) 
                 & (0U == tb_s2a_conv_tile_boundary__DOT____VlemCall_0__stalls))));
}

void Vtb_s2a_conv_tile_boundary___024root___timing_ready(Vtb_s2a_conv_tile_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___timing_ready\n"); );
    Vtb_s2a_conv_tile_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((2ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VtrigSched_h64692e26__0.ready("@(negedge tb_s2a_conv_tile_boundary.clk)");
    }
}

void Vtb_s2a_conv_tile_boundary___024root___timing_resume(Vtb_s2a_conv_tile_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___timing_resume\n"); );
    Vtb_s2a_conv_tile_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VtrigSched_h64692e26__0.moveToResumeQueue(
                                                          "@(negedge tb_s2a_conv_tile_boundary.clk)");
    vlSelfRef.__VtrigSched_h64692e26__0.resume("@(negedge tb_s2a_conv_tile_boundary.clk)");
    if ((4ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VdlySched.resume();
    }
}

void Vtb_s2a_conv_tile_boundary___024root___trigger_orInto__act_vec_vec(VlUnpacked<QData/*63:0*/, 1> &out, const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___trigger_orInto__act_vec_vec\n"); );
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
VL_ATTR_COLD void Vtb_s2a_conv_tile_boundary___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG

bool Vtb_s2a_conv_tile_boundary___024root___eval_phase__act(Vtb_s2a_conv_tile_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___eval_phase__act\n"); );
    Vtb_s2a_conv_tile_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VactExecute;
    // Body
    {
        // Inlined CFunc: _eval_triggers_vec__act
        vlSelfRef.__VactTriggered[0U] = (QData)((IData)(
                                                        ((vlSelfRef.__VdlySched.awaitingCurrentTime() 
                                                          << 2U) 
                                                         | ((((~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__clk)) 
                                                              & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_conv_tile_boundary__DOT__clk__0)) 
                                                             << 1U) 
                                                            | ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__clk) 
                                                               & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_conv_tile_boundary__DOT__clk__0)))))));
        vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_conv_tile_boundary__DOT__clk__0 
            = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__clk;
    }
    Vtb_s2a_conv_tile_boundary___024root___timing_ready(vlSelf);
    Vtb_s2a_conv_tile_boundary___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VactTriggered, vlSelfRef.__VactTriggeredAcc);
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vtb_s2a_conv_tile_boundary___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
    }
#endif
    Vtb_s2a_conv_tile_boundary___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VnbaTriggered, vlSelfRef.__VactTriggered);
    __VactExecute = Vtb_s2a_conv_tile_boundary___024root___trigger_anySet__act(vlSelfRef.__VactTriggered);
    if (__VactExecute) {
        vlSelfRef.__VactTriggeredAcc.fill(0ULL);
        Vtb_s2a_conv_tile_boundary___024root___timing_resume(vlSelf);
        {
            // Inlined CFunc: _eval_act
            if ((2ULL & vlSelfRef.__VactTriggered[0U])) {
                {
                    // Inlined CFunc: _act_sequent__TOP__0
                    IData/*31:0*/ __Vinline_0__eval_act___Vinline_0__act_sequent__TOP__0_tb_s2a_conv_tile_boundary__DOT____VlemCall_0__stalls;
                    IData/*31:0*/ __Vinline_0__eval_act___Vinline_0__act_sequent__TOP__0___Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__0__n;
                    __Vinline_0__eval_act___Vinline_0__act_sequent__TOP__0___Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__0__n = 0;
                    IData/*31:0*/ __Vinline_0__eval_act___Vinline_0__act_sequent__TOP__0___Vtemp_1;
                    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__start_ready 
                        = ((~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__hard_reset)) 
                           & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)));
                    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rstrb = 0U;
                    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__wstrb = 0U;
                    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_write = 0U;
                    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_valid = 0U;
                    if ((1U & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__hard_reset)))) {
                        if (((4U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)) 
                             || (8U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)))) {
                            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rstrb 
                                = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_strobe_latched;
                            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_write = 0U;
                            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_valid = 1U;
                        } else if ((0x10U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
                            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_write = 1U;
                            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_valid = 1U;
                        }
                        if ((1U & (~ ((4U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)) 
                                      || (8U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)))))) {
                            if ((0x10U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) {
                                vlSelfRef.tb_s2a_conv_tile_boundary__DOT__wstrb 
                                    = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_strobe_latched;
                            }
                        }
                    }
                    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__transfer_class 
                        = ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_write)
                            ? 2U : (((vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_address_latched 
                                      >= ((0x25U >= 
                                           (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                           ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_PACKAGE_BASE
                                          [(0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                                           : 0U)) & 
                                     (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_address_latched 
                                      < (((0x25U >= 
                                           (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                           ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_PACKAGE_BASE
                                          [(0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                                           : 0U) + 
                                         ((0x25U >= 
                                           (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id))
                                           ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_GF8_PACKAGE_LENGTH
                                          [(0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id)]
                                           : 0U))))
                                     ? 1U : 0U));
                    __Vinline_0__eval_act___Vinline_0__act_sequent__TOP__0___Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__0__n 
                        = ((2U >= (3U & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__transfer_class))
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__class_count
                           [(3U & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__transfer_class)]
                            : 0U);
                    __Vinline_0__eval_act___Vinline_0__act_sequent__TOP__0___Vtemp_1 
                        = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, __Vinline_0__eval_act___Vinline_0__act_sequent__TOP__0___Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__0__n, (IData)(5U)), Vtb_s2a_conv_tile_boundary__ConstPool__CONST_hb4617e49_0);
                    __Vinline_0__eval_act___Vinline_0__act_sequent__TOP__0_tb_s2a_conv_tile_boundary__DOT____VlemCall_0__stalls 
                        = Vtb_s2a_conv_tile_boundary__ConstPool__TABLE_hc6a14c36_0
                        [__Vinline_0__eval_act___Vinline_0__act_sequent__TOP__0___Vtemp_1];
                    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_ready 
                        = ((((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_valid) 
                             & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__hard_reset))) 
                            & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_valid))) 
                           & (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__waiting) 
                               & (0U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__wait_count)) 
                              | ((~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__waiting)) 
                                 & (0U == __Vinline_0__eval_act___Vinline_0__act_sequent__TOP__0_tb_s2a_conv_tile_boundary__DOT____VlemCall_0__stalls))));
                }
            }
        }
    }
    return (__VactExecute);
}

bool Vtb_s2a_conv_tile_boundary___024root___eval_phase__inact(Vtb_s2a_conv_tile_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___eval_phase__inact\n"); );
    Vtb_s2a_conv_tile_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VinactExecute;
    // Body
    __VinactExecute = vlSelfRef.__VdlySched.awaitingZeroDelay();
    if (__VinactExecute) {
        VL_FATAL_MT("source\\tb_s2a_conv_tile_boundary.sv", 3, "", "ZERODLY: Design Verilated with '--no-sched-zero-delay', but #0 delay executed at runtime");
    }
    return (__VinactExecute);
}

void Vtb_s2a_conv_tile_boundary___024root___trigger_clear__act(VlUnpacked<QData/*63:0*/, 1> &out) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___trigger_clear__act\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        out[n] = 0ULL;
        n = ((IData)(1U) + n);
    } while ((1U > n));
}

bool Vtb_s2a_conv_tile_boundary___024root___eval_phase__nba(Vtb_s2a_conv_tile_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___eval_phase__nba\n"); );
    Vtb_s2a_conv_tile_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = Vtb_s2a_conv_tile_boundary___024root___trigger_anySet__act(vlSelfRef.__VnbaTriggered);
    if (__VnbaExecute) {
        {
            // Inlined CFunc: _eval_nba
            if ((1ULL & vlSelfRef.__VnbaTriggered[0U])) {
                Vtb_s2a_conv_tile_boundary___024root___nba_sequent__TOP__0(vlSelf);
            }
            if ((2ULL & vlSelfRef.__VnbaTriggered[0U])) {
                {
                    // Inlined CFunc: _nba_sequent__TOP__1
                    if (((((3U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode) 
                           & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__injected))) 
                          & (0x0dU == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state))) 
                         & (0U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_reduction_index))) {
                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[0U] = 0x7fffffffU;
                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch[0U] = 1U;
                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory[0U] = 1U;
                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[0U] = 1U;
                        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__injected = 1U;
                    }
                }
            }
            if ((3ULL & vlSelfRef.__VnbaTriggered[0U])) {
                Vtb_s2a_conv_tile_boundary___024root___nba_comb__TOP__0(vlSelf);
            }
        }
        Vtb_s2a_conv_tile_boundary___024root___trigger_clear__act(vlSelfRef.__VnbaTriggered);
    }
    return (__VnbaExecute);
}

void Vtb_s2a_conv_tile_boundary___024root___eval(Vtb_s2a_conv_tile_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___eval\n"); );
    Vtb_s2a_conv_tile_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VnbaIterCount;
    // Body
    __VnbaIterCount = 0U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VnbaIterCount)))) {
#ifdef VL_DEBUG
            Vtb_s2a_conv_tile_boundary___024root___dump_triggers__act(vlSelfRef.__VnbaTriggered, "nba"s);
#endif
            VL_FATAL_MT("source\\tb_s2a_conv_tile_boundary.sv", 3, "", "DIDNOTCONVERGE: NBA region did not converge after '--converge-limit' of 10000 tries");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        vlSelfRef.__VinactIterCount = 0U;
        do {
            if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VinactIterCount)))) {
                VL_FATAL_MT("source\\tb_s2a_conv_tile_boundary.sv", 3, "", "DIDNOTCONVERGE: Inactive region did not converge after '--converge-limit' of 10000 tries");
            }
            vlSelfRef.__VinactIterCount = ((IData)(1U) 
                                           + vlSelfRef.__VinactIterCount);
            vlSelfRef.__VactIterCount = 0U;
            do {
                if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                    Vtb_s2a_conv_tile_boundary___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
#endif
                    VL_FATAL_MT("source\\tb_s2a_conv_tile_boundary.sv", 3, "", "DIDNOTCONVERGE: Active region did not converge after '--converge-limit' of 10000 tries");
                }
                vlSelfRef.__VactIterCount = ((IData)(1U) 
                                             + vlSelfRef.__VactIterCount);
                vlSelfRef.__VactPhaseResult = Vtb_s2a_conv_tile_boundary___024root___eval_phase__act(vlSelf);
            } while (vlSelfRef.__VactPhaseResult);
            vlSelfRef.__VinactPhaseResult = Vtb_s2a_conv_tile_boundary___024root___eval_phase__inact(vlSelf);
        } while (vlSelfRef.__VinactPhaseResult);
        vlSelfRef.__VnbaPhaseResult = Vtb_s2a_conv_tile_boundary___024root___eval_phase__nba(vlSelf);
    } while (vlSelfRef.__VnbaPhaseResult);
}

void Vtb_s2a_conv_tile_boundary___024root____VbeforeTrig_h64692e26__0(Vtb_s2a_conv_tile_boundary___024root* vlSelf, const char* __VeventDescription) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root____VbeforeTrig_h64692e26__0\n"); );
    Vtb_s2a_conv_tile_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlUnpacked<QData/*63:0*/, 1> __VTmp;
    // Body
    __VTmp[0U] = (QData)((IData)((((~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__clk)) 
                                   & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_conv_tile_boundary__DOT__clk__0)) 
                                  << 1U)));
    vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_conv_tile_boundary__DOT__clk__0 
        = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__clk;
    if ((2ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_h64692e26__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h64692e26__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h64692e26__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h64692e26__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h64692e26__0.ready(__VeventDescription);
    }
    vlSelfRef.__VactTriggeredAcc[0U] = (vlSelfRef.__VactTriggeredAcc[0U] 
                                        | __VTmp[0U]);
}

#ifdef VL_DEBUG
void Vtb_s2a_conv_tile_boundary___024root___eval_debug_assertions(Vtb_s2a_conv_tile_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___eval_debug_assertions\n"); );
    Vtb_s2a_conv_tile_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}
#endif  // VL_DEBUG
