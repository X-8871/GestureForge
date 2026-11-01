// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_t66_layer0_tile.h for the primary calling header

#include "Vtb_s2a_t66_layer0_tile__pch.h"

VlCoroutine Vtb_s2a_t66_layer0_tile___024root___eval_initial__TOP__Vtiming__0(Vtb_s2a_t66_layer0_tile___024root* vlSelf);
VlCoroutine Vtb_s2a_t66_layer0_tile___024root___eval_initial__TOP__Vtiming__1(Vtb_s2a_t66_layer0_tile___024root* vlSelf);
VlCoroutine Vtb_s2a_t66_layer0_tile___024root___eval_initial__TOP__Vtiming__2(Vtb_s2a_t66_layer0_tile___024root* vlSelf);

void Vtb_s2a_t66_layer0_tile___024root___eval_initial(Vtb_s2a_t66_layer0_tile___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___eval_initial\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_s2a_t66_layer0_tile___024root___eval_initial__TOP__Vtiming__0(vlSelf);
    Vtb_s2a_t66_layer0_tile___024root___eval_initial__TOP__Vtiming__1(vlSelf);
    Vtb_s2a_t66_layer0_tile___024root___eval_initial__TOP__Vtiming__2(vlSelf);
}

void Vtb_s2a_t66_layer0_tile___024root____VbeforeTrig_h2a50a19a__0(Vtb_s2a_t66_layer0_tile___024root* vlSelf, const char* __VeventDescription);
void Vtb_s2a_t66_layer0_tile___024root____VbeforeTrig_h2a50a1db__0(Vtb_s2a_t66_layer0_tile___024root* vlSelf, const char* __VeventDescription);
extern const VlWide<8>/*255:0*/ Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hc1b71656_0;
extern const VlUnpacked<IData/*31:0*/, 4> Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_h40b9650c_0;

VlCoroutine Vtb_s2a_t66_layer0_tile___024root___eval_initial__TOP__Vtiming__0(Vtb_s2a_t66_layer0_tile___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___eval_initial__TOP__Vtiming__0\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ tb_s2a_t66_layer0_tile__DOT____VlemCall_7__expected_stall_total;
    IData/*31:0*/ tb_s2a_t66_layer0_tile__DOT____VlemCall_6__expected_stall_total;
    IData/*31:0*/ tb_s2a_t66_layer0_tile__DOT__file_id;
    tb_s2a_t66_layer0_tile__DOT__file_id = 0;
    IData/*31:0*/ tb_s2a_t66_layer0_tile__DOT__file_read_count;
    tb_s2a_t66_layer0_tile__DOT__file_read_count = 0;
    IData/*31:0*/ tb_s2a_t66_layer0_tile__DOT__load_index;
    tb_s2a_t66_layer0_tile__DOT__load_index = 0;
    IData/*31:0*/ tb_s2a_t66_layer0_tile__DOT__missing_count;
    tb_s2a_t66_layer0_tile__DOT__missing_count = 0;
    IData/*31:0*/ tb_s2a_t66_layer0_tile__DOT__unnamedblk1_1__DOT____Vrepeat0;
    tb_s2a_t66_layer0_tile__DOT__unnamedblk1_1__DOT____Vrepeat0 = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__transfer_count;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__transfer_count = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__remainder;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__remainder = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__partial_stalls;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__partial_stalls = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__transfer_count;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__transfer_count = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__remainder;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__remainder = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__partial_stalls;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__partial_stalls = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__transfer_count;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__transfer_count = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__remainder;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__remainder = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__partial_stalls;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__partial_stalls = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__transfer_count;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__transfer_count = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__remainder;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__remainder = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__partial_stalls;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__partial_stalls = 0;
    IData/*31:0*/ __Vtemp_1;
    IData/*31:0*/ __Vtemp_2;
    IData/*31:0*/ __Vtemp_3;
    IData/*31:0*/ __Vtemp_4;
    IData/*31:0*/ __Vtemp_5;
    IData/*31:0*/ __Vtemp_6;
    IData/*31:0*/ __Vtemp_7;
    IData/*31:0*/ __Vtemp_8;
    IData/*31:0*/ __Vtemp_9;
    IData/*31:0*/ __Vtemp_10;
    IData/*31:0*/ __Vtemp_11;
    IData/*31:0*/ __Vtemp_12;
    // Body
    tb_s2a_t66_layer0_tile__DOT__load_index = 0U;
    while (VL_GTS_III(32, 0x0007ec00U, tb_s2a_t66_layer0_tile__DOT__load_index)) {
        if (VL_LIKELY(((0x0007ebffU >= (0x0007ffffU 
                                        & tb_s2a_t66_layer0_tile__DOT__load_index))))) {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__input_bytes[(0x0007ffffU 
                                                                & tb_s2a_t66_layer0_tile__DOT__load_index)] = 0U;
        }
        tb_s2a_t66_layer0_tile__DOT__load_index = ((IData)(1U) 
                                                   + tb_s2a_t66_layer0_tile__DOT__load_index);
    }
    tb_s2a_t66_layer0_tile__DOT__load_index = 0U;
    while (VL_GTS_III(32, 0x00000360U, tb_s2a_t66_layer0_tile__DOT__load_index)) {
        if (VL_LIKELY(((0x035fU >= (0x000003ffU & tb_s2a_t66_layer0_tile__DOT__load_index))))) {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_bytes[(0x000003ffU 
                                                                 & tb_s2a_t66_layer0_tile__DOT__load_index)] = 0U;
        }
        tb_s2a_t66_layer0_tile__DOT__load_index = ((IData)(1U) 
                                                   + tb_s2a_t66_layer0_tile__DOT__load_index);
    }
    tb_s2a_t66_layer0_tile__DOT__load_index = 0U;
    while (VL_GTS_III(32, 0x00152000U, tb_s2a_t66_layer0_tile__DOT__load_index)) {
        if (VL_LIKELY(((0x00151fffU >= (0x001fffffU 
                                        & tb_s2a_t66_layer0_tile__DOT__load_index))))) {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__expected_bytes[(0x001fffffU 
                                                                   & tb_s2a_t66_layer0_tile__DOT__load_index)] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_seen[(0x001fffffU 
                                                                & tb_s2a_t66_layer0_tile__DOT__load_index)] = 0U;
        }
        tb_s2a_t66_layer0_tile__DOT__load_index = ((IData)(1U) 
                                                   + tb_s2a_t66_layer0_tile__DOT__load_index);
    }
    tb_s2a_t66_layer0_tile__DOT__file_id = VL_FOPEN_NN("../fixture/sample0_input_chw_int8.bin"s
                                                       , "rb"s);
    ;
    if (VL_UNLIKELY(((0U == tb_s2a_t66_layer0_tile__DOT__file_id)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:576: Assertion failed in %m: \346\227\240\346\263\225\346\211\223\345\274\200 sample0 \350\276\223\345\205\245\345\244\271\345\205\267\357\274\232../fixture/sample0_input_chw_int8.bin\n",3, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 576, "", false);
    }
    tb_s2a_t66_layer0_tile__DOT__file_read_count = VL_FREAD_I(8
                                                              , 0
                                                              , 519168
                                                              , &(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__input_bytes)
                                                              , tb_s2a_t66_layer0_tile__DOT__file_id
                                                              , 0
                                                              , 519168);
    VL_FCLOSE_I(tb_s2a_t66_layer0_tile__DOT__file_id); if (VL_UNLIKELY((
                                                                        (0x0007ec00U 
                                                                         != tb_s2a_t66_layer0_tile__DOT__file_read_count)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:580: Assertion failed in %m: sample0 \350\276\223\345\205\245\345\244\271\345\205\267\351\225\277\345\272\246\351\224\231\350\257\257\357\274\232expected=519168 actual=%0d\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,tb_s2a_t66_layer0_tile__DOT__file_read_count);
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 580, "", false);
    }
    tb_s2a_t66_layer0_tile__DOT__file_id = VL_FOPEN_NN("../fixture/sample0_layer0_gf8_weights.bin"s
                                                       , "rb"s);
    ;
    if (VL_UNLIKELY(((0U == tb_s2a_t66_layer0_tile__DOT__file_id)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:583: Assertion failed in %m: \346\227\240\346\263\225\346\211\223\345\274\200 layer0 \346\235\203\351\207\215\345\244\271\345\205\267\357\274\232../fixture/sample0_layer0_gf8_weights.bin\n",3, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 583, "", false);
    }
    tb_s2a_t66_layer0_tile__DOT__file_read_count = VL_FREAD_I(8
                                                              , 0
                                                              , 864
                                                              , &(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_bytes)
                                                              , tb_s2a_t66_layer0_tile__DOT__file_id
                                                              , 0
                                                              , 864);
    VL_FCLOSE_I(tb_s2a_t66_layer0_tile__DOT__file_id); if (VL_UNLIKELY((
                                                                        (0x00000360U 
                                                                         != tb_s2a_t66_layer0_tile__DOT__file_read_count)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:587: Assertion failed in %m: layer0 \346\235\203\351\207\215\345\244\271\345\205\267\351\225\277\345\272\246\351\224\231\350\257\257\357\274\232expected=864 actual=%0d\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,tb_s2a_t66_layer0_tile__DOT__file_read_count);
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 587, "", false);
    }
    tb_s2a_t66_layer0_tile__DOT__file_id = VL_FOPEN_NN("../fixture/sample0_layer0_expected_nchw_int8.bin"s
                                                       , "rb"s);
    ;
    if (VL_UNLIKELY(((0U == tb_s2a_t66_layer0_tile__DOT__file_id)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:590: Assertion failed in %m: \346\227\240\346\263\225\346\211\223\345\274\200 T25 layer0 \351\273\204\351\207\221\345\244\271\345\205\267\357\274\232../fixture/sample0_layer0_expected_nchw_int8.bin\n",3, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 590, "", false);
    }
    tb_s2a_t66_layer0_tile__DOT__file_read_count = VL_FREAD_I(8
                                                              , 0
                                                              , 1384448
                                                              , &(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__expected_bytes)
                                                              , tb_s2a_t66_layer0_tile__DOT__file_id
                                                              , 0
                                                              , 1384448);
    VL_FCLOSE_I(tb_s2a_t66_layer0_tile__DOT__file_id); if (VL_UNLIKELY((
                                                                        (0x00152000U 
                                                                         != tb_s2a_t66_layer0_tile__DOT__file_read_count)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:594: Assertion failed in %m: T25 layer0 \351\273\204\351\207\221\345\244\271\345\205\267\351\225\277\345\272\246\351\224\231\350\257\257\357\274\232expected=1384448 actual=%0d\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,tb_s2a_t66_layer0_tile__DOT__file_read_count);
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 594, "", false);
    }
    tb_s2a_t66_layer0_tile__DOT__load_index = 0U;
    while (VL_GTS_III(32, 0x0007ec00U, tb_s2a_t66_layer0_tile__DOT__load_index)) {
        tb_s2a_t66_layer0_tile__DOT__load_index = ((IData)(1U) 
                                                   + tb_s2a_t66_layer0_tile__DOT__load_index);
    }
    tb_s2a_t66_layer0_tile__DOT__load_index = 0U;
    while (VL_GTS_III(32, 0x00000360U, tb_s2a_t66_layer0_tile__DOT__load_index)) {
        tb_s2a_t66_layer0_tile__DOT__load_index = ((IData)(1U) 
                                                   + tb_s2a_t66_layer0_tile__DOT__load_index);
    }
    tb_s2a_t66_layer0_tile__DOT__load_index = 0U;
    while (VL_GTS_III(32, 0x00152000U, tb_s2a_t66_layer0_tile__DOT__load_index)) {
        tb_s2a_t66_layer0_tile__DOT__load_index = ((IData)(1U) 
                                                   + tb_s2a_t66_layer0_tile__DOT__load_index);
    }
    VL_WRITEF_NX("T66_FIXTURES input=519168 weight=864 expected=1384448 shape=[1,32,208,208] layout=NCHW\nT66_MEMORY byte-strobes=one-hot aligned=32-bit outstanding=1 stall-pattern=[0,1,2,7,3]\nT66_PLAN estimated_cycles<=26003000 watchdog_cycles=75000000 lanes=8 waveforms=disabled\n",0);
    Vtb_s2a_t66_layer0_tile___024root____VbeforeTrig_h2a50a19a__0(vlSelf, 
                                                                  "@(negedge tb_s2a_t66_layer0_tile.clk)");
    co_await vlSelfRef.__VtrigSched_h2a50a19a__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_t66_layer0_tile.clk)", 
                                                         "D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 
                                                         612);
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__hard_reset = 1U;
    tb_s2a_t66_layer0_tile__DOT__unnamedblk1_1__DOT____Vrepeat0 = 2U;
    while (VL_LTS_III(32, 0U, tb_s2a_t66_layer0_tile__DOT__unnamedblk1_1__DOT____Vrepeat0)) {
        Vtb_s2a_t66_layer0_tile___024root____VbeforeTrig_h2a50a1db__0(vlSelf, 
                                                                      "@(posedge tb_s2a_t66_layer0_tile.clk)");
        co_await vlSelfRef.__VtrigSched_h2a50a1db__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(posedge tb_s2a_t66_layer0_tile.clk)", 
                                                             "D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 
                                                             614);
        tb_s2a_t66_layer0_tile__DOT__unnamedblk1_1__DOT____Vrepeat0 
            = (tb_s2a_t66_layer0_tile__DOT__unnamedblk1_1__DOT____Vrepeat0 
               - (IData)(1U));
    }
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 
                                         615);
    Vtb_s2a_t66_layer0_tile___024root____VbeforeTrig_h2a50a19a__0(vlSelf, 
                                                                  "@(negedge tb_s2a_t66_layer0_tile.clk)");
    co_await vlSelfRef.__VtrigSched_h2a50a19a__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_t66_layer0_tile.clk)", 
                                                         "D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 
                                                         616);
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__hard_reset = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__buffer_owner_pl = 1U;
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 
                                         619);
    if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__start_ready)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:621: Assertion failed in %m: T66 layer start \346\234\252 ready\357\274\232start_ready=%b\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',1,(IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__start_ready));
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 621, "", false);
    }
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__start_valid = 1U;
    Vtb_s2a_t66_layer0_tile___024root____VbeforeTrig_h2a50a1db__0(vlSelf, 
                                                                  "@(posedge tb_s2a_t66_layer0_tile.clk)");
    co_await vlSelfRef.__VtrigSched_h2a50a1db__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_t66_layer0_tile.clk)", 
                                                         "D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 
                                                         623);
    if (VL_UNLIKELY(((1U & ((~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__start_valid)) 
                            | (~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__start_ready))))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:625: Assertion failed in %m: T66 layer start \346\217\241\346\211\213\346\234\252\345\217\221\347\224\237\357\274\232start_valid=%b start_ready=%b\n",5, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',1,(IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__start_valid)
                     , '#',1,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__start_ready);
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 625, "", false);
    }
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 
                                         626);
    Vtb_s2a_t66_layer0_tile___024root____VbeforeTrig_h2a50a19a__0(vlSelf, 
                                                                  "@(negedge tb_s2a_t66_layer0_tile.clk)");
    co_await vlSelfRef.__VtrigSched_h2a50a19a__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_t66_layer0_tile.clk)", 
                                                         "D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 
                                                         627);
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__start_valid = 0U;
    tb_s2a_t66_layer0_tile__DOT__load_index = 0U;
    {
        while (VL_GTS_III(32, 0x047868c0U, tb_s2a_t66_layer0_tile__DOT__load_index)) {
            Vtb_s2a_t66_layer0_tile___024root____VbeforeTrig_h2a50a1db__0(vlSelf, 
                                                                          "@(posedge tb_s2a_t66_layer0_tile.clk)");
            co_await vlSelfRef.__VtrigSched_h2a50a1db__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(posedge tb_s2a_t66_layer0_tile.clk)", 
                                                                 "D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 
                                                                 631);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 
                                                 632);
            if ((0x13U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
                if (VL_UNLIKELY(((0U != (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:635: Assertion failed in %m: T66 layer engine \350\277\224\345\233\236\351\224\231\350\257\257\357\274\232code=%0d cycles=%0d\n",5, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '#',3,(IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched)
                                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__cycle_count);
                    VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 635, "", false);
                }
                goto __Vlabel0;
            }
            tb_s2a_t66_layer0_tile__DOT__load_index 
                = ((IData)(1U) + tb_s2a_t66_layer0_tile__DOT__load_index);
        }
        __Vlabel0: ;
    }
    if (VL_UNLIKELY(((0x13U != (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:640: Assertion failed in %m: T66 \345\205\250\345\261\202\344\273\277\347\234\237 watchdog \350\266\205\346\227\266\357\274\232limit=75000000 cycles=%0d writes=%0d requests=%0d\n",6, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__cycle_count
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__request_count);
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 640, "", false);
    }
    Vtb_s2a_t66_layer0_tile___024root____VbeforeTrig_h2a50a19a__0(vlSelf, 
                                                                  "@(negedge tb_s2a_t66_layer0_tile.clk)");
    co_await vlSelfRef.__VtrigSched_h2a50a19a__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_s2a_t66_layer0_tile.clk)", 
                                                         "D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 
                                                         642);
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__result_ready = 1U;
    Vtb_s2a_t66_layer0_tile___024root____VbeforeTrig_h2a50a1db__0(vlSelf, 
                                                                  "@(posedge tb_s2a_t66_layer0_tile.clk)");
    co_await vlSelfRef.__VtrigSched_h2a50a1db__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_s2a_t66_layer0_tile.clk)", 
                                                         "D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 
                                                         644);
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 
                                         645);
    if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__memory_pending) 
                      | (0U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_request))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:647: Assertion failed in %m: T66 result \346\227\266\344\273\215\346\234\211\346\234\252\345\256\214\346\210\220 memory request/response\n",3, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 647, "", false);
    }
    if (VL_UNLIKELY(((((((0x00152000U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count) 
                         | (1U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__result_count)) 
                        | (0U != (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) 
                       | (0x13U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) 
                      | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__request_count 
                         != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_count))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:650: Assertion failed in %m: T66 \344\274\240\350\276\223\350\256\241\346\225\260\344\270\215\345\256\214\346\225\264\357\274\232writes=%0d result=%0d req=%0d rsp=%0d\n",7, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__result_count
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__request_count
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_count);
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 650, "", false);
    }
    tb_s2a_t66_layer0_tile__DOT__missing_count = 0U;
    tb_s2a_t66_layer0_tile__DOT__load_index = 0U;
    while (VL_GTS_III(32, 0x00152000U, tb_s2a_t66_layer0_tile__DOT__load_index)) {
        if ((1U & (~ ((0x00151fffU >= (0x001fffffU 
                                       & tb_s2a_t66_layer0_tile__DOT__load_index)) 
                      && vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_seen
                      [(0x001fffffU & tb_s2a_t66_layer0_tile__DOT__load_index)])))) {
            tb_s2a_t66_layer0_tile__DOT__missing_count 
                = ((IData)(1U) + tb_s2a_t66_layer0_tile__DOT__missing_count);
            if (VL_UNLIKELY((VL_GTES_III(32, 8U, tb_s2a_t66_layer0_tile__DOT__missing_count)))) {
                VL_WRITEF_NX("T66_MISSING_OUTPUT index=%0d expected=%02h\n",2
                             , '~',32,tb_s2a_t66_layer0_tile__DOT__load_index
                             , '#',8,((0x00151fffU 
                                       >= (0x001fffffU 
                                           & tb_s2a_t66_layer0_tile__DOT__load_index))
                                       ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__expected_bytes
                                      [(0x001fffffU 
                                        & tb_s2a_t66_layer0_tile__DOT__load_index)]
                                       : 0U));
            }
        }
        tb_s2a_t66_layer0_tile__DOT__load_index = ((IData)(1U) 
                                                   + tb_s2a_t66_layer0_tile__DOT__load_index);
    }
    if (VL_UNLIKELY(((0U != tb_s2a_t66_layer0_tile__DOT__missing_count)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:661: Assertion failed in %m: T66 \346\234\211\346\234\252\345\206\231\350\276\223\345\207\272\345\255\227\350\212\202\357\274\232count=%0d\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,tb_s2a_t66_layer0_tile__DOT__missing_count);
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 661, "", false);
    }
    if (VL_UNLIKELY(((1U & ((((~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point0_requant_seen)) 
                              | (~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point1_bias_checked))) 
                             | (~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point0_golden_seen))) 
                            | (~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point1_golden_seen))))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:664: Assertion failed in %m: T66 \345\220\214 tile/\345\220\214 OC group \350\277\236\347\273\255\344\270\244\347\202\271 bias \346\210\226 T25 golden \346\240\270\351\252\214\344\270\215\345\256\214\346\225\264\357\274\232requant0=%b bias1=%b golden0=%b golden1=%b\n",7, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',1,(IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point0_requant_seen)
                     , '#',1,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point1_bias_checked
                     , '#',1,(IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point0_golden_seen)
                     , '#',1,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point1_golden_seen);
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 664, "", false);
    }
    if (VL_UNLIKELY((((((0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__input_read_count) 
                        | (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_read_count)) 
                       | (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__stall_cycle_count)) 
                      | (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_stall_cycle_count))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:669: Assertion failed in %m: T66 memory/stall \350\246\206\347\233\226\344\270\215\350\266\263\357\274\232input=%0d weight=%0d request_stalls=%0d response_stalls=%0d\n",7, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__input_read_count
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_read_count
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__stall_cycle_count
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_stall_cycle_count);
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 669, "", false);
    }
    if (VL_UNLIKELY((((((((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[0U] 
                           != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__input_read_count) 
                          | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[1U] 
                             != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_read_count)) 
                         | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[2U] 
                            != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count)) 
                        | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count[0U] 
                           != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[0U])) 
                       | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count[1U] 
                          != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[1U])) 
                      | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count[2U] 
                         != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[2U]))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:677: Assertion failed in %m: T66 transfer class \350\256\241\346\225\260\344\270\215\344\270\200\350\207\264\357\274\232feature=%0d/%0d weight=%0d/%0d output=%0d/%0d\n",9, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[0U]
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__input_read_count
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[1U]
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_read_count
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[2U]
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count);
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 677, "", false);
    }
    tb_s2a_t66_layer0_tile__DOT__load_index = 0U;
    while (VL_GTS_III(32, 0x00000360U, tb_s2a_t66_layer0_tile__DOT__load_index)) {
        if (VL_UNLIKELY(((1U & (~ ((0x035fU >= (0x000003ffU 
                                                & tb_s2a_t66_layer0_tile__DOT__load_index)) 
                                   && vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_seen
                                   [(0x000003ffU & tb_s2a_t66_layer0_tile__DOT__load_index)])))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:683: Assertion failed in %m: T66 layer0 \346\235\203\351\207\215\345\234\260\345\235\200\346\234\252\350\246\206\347\233\226\357\274\232index=%0d\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000)
                         , '~',32,tb_s2a_t66_layer0_tile__DOT__load_index);
            VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 683, "", false);
        }
        tb_s2a_t66_layer0_tile__DOT__load_index = ((IData)(1U) 
                                                   + tb_s2a_t66_layer0_tile__DOT__load_index);
    }
    tb_s2a_t66_layer0_tile__DOT__load_index = 0U;
    if (VL_UNLIKELY((((0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count[0U]) 
                      | (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count[0U]))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:688: Assertion failed in %m: T66 feature/weight read lane \350\246\206\347\233\226\344\270\215\345\256\214\346\225\264\357\274\232lane=0 feature=%0d weight=%0d\n",5, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count[0U]
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count[0U]);
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 688, "", false);
    }
    VL_WRITEF_NX("T66_READ_LANE_PASS lane=0 feature_requests=%0d weight_requests=%0d\n",2
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count[0U]
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count[0U]);
    tb_s2a_t66_layer0_tile__DOT__load_index = 1U;
    if (VL_UNLIKELY((((0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count[1U]) 
                      | (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count[1U]))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:688: Assertion failed in %m: T66 feature/weight read lane \350\246\206\347\233\226\344\270\215\345\256\214\346\225\264\357\274\232lane=1 feature=%0d weight=%0d\n",5, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count[1U]
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count[1U]);
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 688, "", false);
    }
    VL_WRITEF_NX("T66_READ_LANE_PASS lane=1 feature_requests=%0d weight_requests=%0d\n",2
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count[1U]
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count[1U]);
    tb_s2a_t66_layer0_tile__DOT__load_index = 2U;
    if (VL_UNLIKELY((((0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count[2U]) 
                      | (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count[2U]))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:688: Assertion failed in %m: T66 feature/weight read lane \350\246\206\347\233\226\344\270\215\345\256\214\346\225\264\357\274\232lane=2 feature=%0d weight=%0d\n",5, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count[2U]
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count[2U]);
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 688, "", false);
    }
    VL_WRITEF_NX("T66_READ_LANE_PASS lane=2 feature_requests=%0d weight_requests=%0d\n",2
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count[2U]
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count[2U]);
    tb_s2a_t66_layer0_tile__DOT__load_index = 3U;
    if (VL_UNLIKELY((((0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count[3U]) 
                      | (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count[3U]))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:688: Assertion failed in %m: T66 feature/weight read lane \350\246\206\347\233\226\344\270\215\345\256\214\346\225\264\357\274\232lane=3 feature=%0d weight=%0d\n",5, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count[3U]
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count[3U]);
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 688, "", false);
    }
    VL_WRITEF_NX("T66_READ_LANE_PASS lane=3 feature_requests=%0d weight_requests=%0d\n",2
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count[3U]
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count[3U]);
    tb_s2a_t66_layer0_tile__DOT__load_index = 4U;
    if (VL_UNLIKELY((((0x0fU != (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_capture_checked)) 
                      | (0x0fU != (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_capture_checked)))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:697: Assertion failed in %m: T66 feature/weight \347\274\223\345\255\230\345\273\266\350\277\237\351\207\207\346\240\267\346\234\252\350\246\206\347\233\226\345\205\250\351\203\250 8 \344\270\252 byte lane\357\274\232feature=%b weight=%b\n",5, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',4,(IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_capture_checked)
                     , '#',4,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_capture_checked);
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 697, "", false);
    }
    VL_WRITEF_NX("T66_READ_CAPTURE_PASS samples=8 feature_lanes=1111 weight_lanes=1111\n",0);
    tb_s2a_t66_layer0_tile__DOT__load_index = 0U;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__transfer_count 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[0U];
    tb_s2a_t66_layer0_tile__DOT____VlemCall_6__expected_stall_total = 0;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__remainder = 0;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__partial_stalls = 0;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__remainder 
        = VL_MODDIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__transfer_count, (IData)(5U));
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__partial_stalls = 0U;
    tb_s2a_t66_layer0_tile__DOT____VlemCall_6__expected_stall_total 
        = VL_MULS_III(32, (IData)(0x0000000dU), VL_DIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__transfer_count, (IData)(5U)));
    __Vtemp_1 = VL_MATCHMASKED_I(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__remainder, Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hc1b71656_0);
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__partial_stalls 
        = Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_h40b9650c_0
        [__Vtemp_1];
    tb_s2a_t66_layer0_tile__DOT____VlemCall_6__expected_stall_total 
        = (tb_s2a_t66_layer0_tile__DOT____VlemCall_6__expected_stall_total 
           + __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__partial_stalls);
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__transfer_count 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count[0U];
    tb_s2a_t66_layer0_tile__DOT____VlemCall_7__expected_stall_total = 0;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__remainder = 0;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__partial_stalls = 0;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__remainder 
        = VL_MODDIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__transfer_count, (IData)(5U));
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__partial_stalls = 0U;
    tb_s2a_t66_layer0_tile__DOT____VlemCall_7__expected_stall_total 
        = VL_MULS_III(32, (IData)(0x0000000dU), VL_DIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__transfer_count, (IData)(5U)));
    __Vtemp_2 = VL_MATCHMASKED_I(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__remainder, Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hc1b71656_0);
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__partial_stalls 
        = Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_h40b9650c_0
        [__Vtemp_2];
    tb_s2a_t66_layer0_tile__DOT____VlemCall_7__expected_stall_total 
        = (tb_s2a_t66_layer0_tile__DOT____VlemCall_7__expected_stall_total 
           + __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__partial_stalls);
    if (VL_UNLIKELY((((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_stall_count[0U] 
                       != tb_s2a_t66_layer0_tile__DOT____VlemCall_6__expected_stall_total) 
                      | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_stall_count[0U] 
                         != tb_s2a_t66_layer0_tile__DOT____VlemCall_7__expected_stall_total))))) {
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__transfer_count 
            = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[0U];
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_8__expected_stall_total = 0;
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__remainder = 0;
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__partial_stalls = 0;
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__remainder 
            = VL_MODDIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__transfer_count, (IData)(5U));
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__partial_stalls = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_8__expected_stall_total 
            = VL_MULS_III(32, (IData)(0x0000000dU), 
                          VL_DIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__transfer_count, (IData)(5U)));
        __Vtemp_3 = VL_MATCHMASKED_I(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__remainder, Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hc1b71656_0);
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__partial_stalls 
            = Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_h40b9650c_0
            [__Vtemp_3];
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_8__expected_stall_total 
            = (vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_8__expected_stall_total 
               + __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__partial_stalls);
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__transfer_count 
            = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count[0U];
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_9__expected_stall_total = 0;
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__remainder = 0;
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__partial_stalls = 0;
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__remainder 
            = VL_MODDIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__transfer_count, (IData)(5U));
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__partial_stalls = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_9__expected_stall_total 
            = VL_MULS_III(32, (IData)(0x0000000dU), 
                          VL_DIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__transfer_count, (IData)(5U)));
        __Vtemp_4 = VL_MATCHMASKED_I(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__remainder, Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hc1b71656_0);
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__partial_stalls 
            = Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_h40b9650c_0
            [__Vtemp_4];
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_9__expected_stall_total 
            = (vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_9__expected_stall_total 
               + __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__partial_stalls);
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:705: Assertion failed in %m: T66 transfer class stall \346\200\273\346\225\260\344\270\215\347\254\246\357\274\232class=0 request=%0d/%0d response=%0d/%0d\n",7, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_stall_count[0U]
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_8__expected_stall_total
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_stall_count[0U]
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_9__expected_stall_total);
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 705, "", false);
    }
    VL_WRITEF_NX("T66_CLASS_STALL class=0 requests=%0d request_stalls=%0d responses=%0d response_stalls=%0d pattern=[0,1,2,7,3]\n",4
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[0U]
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_stall_count[0U]
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count[0U]
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_stall_count[0U]);
    tb_s2a_t66_layer0_tile__DOT__load_index = 1U;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__transfer_count 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[1U];
    tb_s2a_t66_layer0_tile__DOT____VlemCall_6__expected_stall_total = 0;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__remainder = 0;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__partial_stalls = 0;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__remainder 
        = VL_MODDIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__transfer_count, (IData)(5U));
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__partial_stalls = 0U;
    tb_s2a_t66_layer0_tile__DOT____VlemCall_6__expected_stall_total 
        = VL_MULS_III(32, (IData)(0x0000000dU), VL_DIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__transfer_count, (IData)(5U)));
    __Vtemp_5 = VL_MATCHMASKED_I(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__remainder, Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hc1b71656_0);
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__partial_stalls 
        = Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_h40b9650c_0
        [__Vtemp_5];
    tb_s2a_t66_layer0_tile__DOT____VlemCall_6__expected_stall_total 
        = (tb_s2a_t66_layer0_tile__DOT____VlemCall_6__expected_stall_total 
           + __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__partial_stalls);
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__transfer_count 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count[1U];
    tb_s2a_t66_layer0_tile__DOT____VlemCall_7__expected_stall_total = 0;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__remainder = 0;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__partial_stalls = 0;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__remainder 
        = VL_MODDIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__transfer_count, (IData)(5U));
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__partial_stalls = 0U;
    tb_s2a_t66_layer0_tile__DOT____VlemCall_7__expected_stall_total 
        = VL_MULS_III(32, (IData)(0x0000000dU), VL_DIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__transfer_count, (IData)(5U)));
    __Vtemp_6 = VL_MATCHMASKED_I(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__remainder, Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hc1b71656_0);
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__partial_stalls 
        = Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_h40b9650c_0
        [__Vtemp_6];
    tb_s2a_t66_layer0_tile__DOT____VlemCall_7__expected_stall_total 
        = (tb_s2a_t66_layer0_tile__DOT____VlemCall_7__expected_stall_total 
           + __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__partial_stalls);
    if (VL_UNLIKELY((((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_stall_count[1U] 
                       != tb_s2a_t66_layer0_tile__DOT____VlemCall_6__expected_stall_total) 
                      | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_stall_count[1U] 
                         != tb_s2a_t66_layer0_tile__DOT____VlemCall_7__expected_stall_total))))) {
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__transfer_count 
            = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[1U];
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_8__expected_stall_total = 0;
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__remainder = 0;
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__partial_stalls = 0;
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__remainder 
            = VL_MODDIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__transfer_count, (IData)(5U));
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__partial_stalls = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_8__expected_stall_total 
            = VL_MULS_III(32, (IData)(0x0000000dU), 
                          VL_DIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__transfer_count, (IData)(5U)));
        __Vtemp_7 = VL_MATCHMASKED_I(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__remainder, Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hc1b71656_0);
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__partial_stalls 
            = Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_h40b9650c_0
            [__Vtemp_7];
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_8__expected_stall_total 
            = (vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_8__expected_stall_total 
               + __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__partial_stalls);
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__transfer_count 
            = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count[1U];
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_9__expected_stall_total = 0;
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__remainder = 0;
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__partial_stalls = 0;
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__remainder 
            = VL_MODDIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__transfer_count, (IData)(5U));
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__partial_stalls = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_9__expected_stall_total 
            = VL_MULS_III(32, (IData)(0x0000000dU), 
                          VL_DIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__transfer_count, (IData)(5U)));
        __Vtemp_8 = VL_MATCHMASKED_I(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__remainder, Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hc1b71656_0);
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__partial_stalls 
            = Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_h40b9650c_0
            [__Vtemp_8];
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_9__expected_stall_total 
            = (vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_9__expected_stall_total 
               + __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__partial_stalls);
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:705: Assertion failed in %m: T66 transfer class stall \346\200\273\346\225\260\344\270\215\347\254\246\357\274\232class=1 request=%0d/%0d response=%0d/%0d\n",7, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_stall_count[1U]
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_8__expected_stall_total
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_stall_count[1U]
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_9__expected_stall_total);
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 705, "", false);
    }
    VL_WRITEF_NX("T66_CLASS_STALL class=1 requests=%0d request_stalls=%0d responses=%0d response_stalls=%0d pattern=[0,1,2,7,3]\n",4
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[1U]
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_stall_count[1U]
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count[1U]
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_stall_count[1U]);
    tb_s2a_t66_layer0_tile__DOT__load_index = 2U;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__transfer_count 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[2U];
    tb_s2a_t66_layer0_tile__DOT____VlemCall_6__expected_stall_total = 0;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__remainder = 0;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__partial_stalls = 0;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__remainder 
        = VL_MODDIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__transfer_count, (IData)(5U));
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__partial_stalls = 0U;
    tb_s2a_t66_layer0_tile__DOT____VlemCall_6__expected_stall_total 
        = VL_MULS_III(32, (IData)(0x0000000dU), VL_DIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__transfer_count, (IData)(5U)));
    __Vtemp_9 = VL_MATCHMASKED_I(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__remainder, Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hc1b71656_0);
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__partial_stalls 
        = Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_h40b9650c_0
        [__Vtemp_9];
    tb_s2a_t66_layer0_tile__DOT____VlemCall_6__expected_stall_total 
        = (tb_s2a_t66_layer0_tile__DOT____VlemCall_6__expected_stall_total 
           + __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__12__partial_stalls);
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__transfer_count 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count[2U];
    tb_s2a_t66_layer0_tile__DOT____VlemCall_7__expected_stall_total = 0;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__remainder = 0;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__partial_stalls = 0;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__remainder 
        = VL_MODDIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__transfer_count, (IData)(5U));
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__partial_stalls = 0U;
    tb_s2a_t66_layer0_tile__DOT____VlemCall_7__expected_stall_total 
        = VL_MULS_III(32, (IData)(0x0000000dU), VL_DIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__transfer_count, (IData)(5U)));
    __Vtemp_10 = VL_MATCHMASKED_I(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__remainder, Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hc1b71656_0);
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__partial_stalls 
        = Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_h40b9650c_0
        [__Vtemp_10];
    tb_s2a_t66_layer0_tile__DOT____VlemCall_7__expected_stall_total 
        = (tb_s2a_t66_layer0_tile__DOT____VlemCall_7__expected_stall_total 
           + __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__13__partial_stalls);
    if (VL_UNLIKELY((((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_stall_count[2U] 
                       != tb_s2a_t66_layer0_tile__DOT____VlemCall_6__expected_stall_total) 
                      | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_stall_count[2U] 
                         != tb_s2a_t66_layer0_tile__DOT____VlemCall_7__expected_stall_total))))) {
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__transfer_count 
            = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[2U];
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_8__expected_stall_total = 0;
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__remainder = 0;
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__partial_stalls = 0;
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__remainder 
            = VL_MODDIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__transfer_count, (IData)(5U));
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__partial_stalls = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_8__expected_stall_total 
            = VL_MULS_III(32, (IData)(0x0000000dU), 
                          VL_DIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__transfer_count, (IData)(5U)));
        __Vtemp_11 = VL_MATCHMASKED_I(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__remainder, Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hc1b71656_0);
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__partial_stalls 
            = Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_h40b9650c_0
            [__Vtemp_11];
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_8__expected_stall_total 
            = (vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_8__expected_stall_total 
               + __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__14__partial_stalls);
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__transfer_count 
            = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count[2U];
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_9__expected_stall_total = 0;
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__remainder = 0;
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__partial_stalls = 0;
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__remainder 
            = VL_MODDIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__transfer_count, (IData)(5U));
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__partial_stalls = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_9__expected_stall_total 
            = VL_MULS_III(32, (IData)(0x0000000dU), 
                          VL_DIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__transfer_count, (IData)(5U)));
        __Vtemp_12 = VL_MATCHMASKED_I(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__remainder, Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hc1b71656_0);
        __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__partial_stalls 
            = Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_h40b9650c_0
            [__Vtemp_12];
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_9__expected_stall_total 
            = (vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_9__expected_stall_total 
               + __Vfunc_tb_s2a_t66_layer0_tile__DOT__expected_stall_total__15__partial_stalls);
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:705: Assertion failed in %m: T66 transfer class stall \346\200\273\346\225\260\344\270\215\347\254\246\357\274\232class=2 request=%0d/%0d response=%0d/%0d\n",7, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_stall_count[2U]
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_8__expected_stall_total
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_stall_count[2U]
                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_9__expected_stall_total);
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 705, "", false);
    }
    VL_WRITEF_NX("T66_CLASS_STALL class=2 requests=%0d request_stalls=%0d responses=%0d response_stalls=%0d pattern=[0,1,2,7,3]\n",4
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[2U]
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_stall_count[2U]
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count[2U]
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_stall_count[2U]);
    tb_s2a_t66_layer0_tile__DOT__load_index = 3U;
    if (VL_UNLIKELY((((0U != (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched)) 
                      | (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_cancel))))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:715: Assertion failed in %m: T66 \347\273\223\346\235\237\347\212\266\346\200\201\351\224\231\350\257\257\357\274\232error=%0d cancel=%b\n",5, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000)
                     , '#',3,(IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched)
                     , '#',1,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_cancel);
        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 715, "", false);
    }
    VL_WRITEF_NX("PASS: T66 sample0 layer0 full tensor matched T25; bytes=1384448 mismatches=0 input_reads=%0d weight_reads=%0d output_writes=%0d requests=%0d responses=%0d request_stalls=%0d response_stalls=%0d cycles=%0d\n",8
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__input_read_count
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_read_count
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__request_count
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_count
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__stall_cycle_count
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_stall_cycle_count
                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__cycle_count);
    VL_FINISH_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 719, "");
    co_return;
}

VlCoroutine Vtb_s2a_t66_layer0_tile___024root___eval_initial__TOP__Vtiming__1(Vtb_s2a_t66_layer0_tile___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___eval_initial__TOP__Vtiming__1\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    while (VL_LIKELY(!vlSymsp->_vm_contextp__->gotFinish())) {
        co_await vlSelfRef.__VdlySched.delay(0x0000000000001388ULL, 
                                             nullptr, 
                                             "D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 
                                             183);
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__clk 
            = (1U & (~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__clk)));
    }
    co_return;
}

VlCoroutine Vtb_s2a_t66_layer0_tile___024root___eval_initial__TOP__Vtiming__2(Vtb_s2a_t66_layer0_tile___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___eval_initial__TOP__Vtiming__2\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__transfer_class;
    __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__transfer_class = 0;
    IData/*31:0*/ __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__destination_index;
    __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__destination_index = 0;
    CData/*7:0*/ __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__expected_byte;
    __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__expected_byte = 0;
    IData/*31:0*/ __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__transfer_class;
    __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__transfer_class = 0;
    IData/*31:0*/ __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__destination_index;
    __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__destination_index = 0;
    CData/*7:0*/ __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__expected_byte;
    __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__expected_byte = 0;
    // Body
    while (VL_LIKELY(!vlSymsp->_vm_contextp__->gotFinish())) {
        Vtb_s2a_t66_layer0_tile___024root____VbeforeTrig_h2a50a1db__0(vlSelf, 
                                                                      "@(posedge tb_s2a_t66_layer0_tile.clk)");
        co_await vlSelfRef.__VtrigSched_h2a50a1db__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(posedge tb_s2a_t66_layer0_tile.clk)", 
                                                             "D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 
                                                             297);
        if (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__hard_reset) {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_capture_checked = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_capture_checked = 0U;
        } else if ((((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__memory_pending) 
                     & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_rsp_valid)) 
                    & (0U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_error)))) {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__t66_read_capture_monitor__DOT__selected_lane 
                = (3U & (0x00030210U >> ((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_strobe_latched) 
                                         << 1U)));
            if ((0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__pending_transfer_class)) {
                if ((1U & (~ ((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_capture_checked) 
                              >> (3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__t66_read_capture_monitor__DOT__selected_lane))))) {
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__t66_read_capture_monitor__DOT__selected_byte 
                        = (0x000000ffU & VL_SHIFTR_III(8,32,32, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_data, 
                                                       VL_MULS_III(32, (IData)(8U), vlSelfRef.tb_s2a_t66_layer0_tile__DOT__t66_read_capture_monitor__DOT__selected_lane)));
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__t66_read_capture_monitor__DOT__destination_index 
                        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index;
                    __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__expected_byte 
                        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__t66_read_capture_monitor__DOT__selected_byte;
                    __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__destination_index 
                        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__t66_read_capture_monitor__DOT__destination_index;
                    __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__transfer_class = 0U;
                    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                         nullptr, 
                                                         "D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 
                                                         239);
                    if ((0U == __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__transfer_class)) {
                        if (VL_UNLIKELY(((((0xc7ffU 
                                            >= (0x0000ffffU 
                                                & __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__destination_index))
                                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch
                                           [(0x0000ffffU 
                                             & __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__destination_index)]
                                            : 0U) != (IData)(__Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__expected_byte))))) {
                            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:242: Assertion failed in %m: T66 feature byte lane \346\217\220\345\217\226\351\224\231\350\257\257\357\274\232index=%0d actual=%02h expected=%02h\n",6, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile.check_read_byte_capture", 'T',-9
                                         , '#',64,VL_TIME_UNITED_Q(1000)
                                         , '~',32,__Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__destination_index
                                         , '~',8,((0xc7ffU 
                                                   >= 
                                                   (0x0000ffffU 
                                                    & __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__destination_index))
                                                   ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch
                                                  [
                                                  (0x0000ffffU 
                                                   & __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__destination_index)]
                                                   : 0U)
                                         , '~',8,(IData)(__Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__expected_byte));
                            VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 242, "", false);
                        }
                    } else if ((1U == __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__transfer_class)) {
                        if (VL_UNLIKELY(((((0x8fffU 
                                            >= (0x0000ffffU 
                                                & __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__destination_index))
                                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group
                                           [(0x0000ffffU 
                                             & __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__destination_index)]
                                            : 0U) != (IData)(__Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__expected_byte))))) {
                            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:246: Assertion failed in %m: T66 weight byte lane \346\217\220\345\217\226\351\224\231\350\257\257\357\274\232index=%0d actual=%02h expected=%02h\n",6, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile.check_read_byte_capture", 'T',-9
                                         , '#',64,VL_TIME_UNITED_Q(1000)
                                         , '~',32,__Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__destination_index
                                         , '~',8,((0x8fffU 
                                                   >= 
                                                   (0x0000ffffU 
                                                    & __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__destination_index))
                                                   ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group
                                                  [
                                                  (0x0000ffffU 
                                                   & __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__destination_index)]
                                                   : 0U)
                                         , '~',8,(IData)(__Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__2__expected_byte));
                            VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 246, "", false);
                        }
                    }
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_capture_checked 
                        = ((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_capture_checked) 
                           | (0x0fU & ((IData)(1U) 
                                       << (3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__t66_read_capture_monitor__DOT__selected_lane))));
                }
            } else if ((1U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__pending_transfer_class)) {
                if ((1U & (~ ((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_capture_checked) 
                              >> (3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__t66_read_capture_monitor__DOT__selected_lane))))) {
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__t66_read_capture_monitor__DOT__selected_byte 
                        = (0x000000ffU & VL_SHIFTR_III(8,32,32, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_data, 
                                                       VL_MULS_III(32, (IData)(8U), vlSelfRef.tb_s2a_t66_layer0_tile__DOT__t66_read_capture_monitor__DOT__selected_lane)));
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__t66_read_capture_monitor__DOT__destination_index 
                        = ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_lane_index 
                            * vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched) 
                           + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_reduction_index);
                    __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__expected_byte 
                        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__t66_read_capture_monitor__DOT__selected_byte;
                    __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__destination_index 
                        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__t66_read_capture_monitor__DOT__destination_index;
                    __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__transfer_class = 1U;
                    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                         nullptr, 
                                                         "D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 
                                                         239);
                    if ((0U == __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__transfer_class)) {
                        if (VL_UNLIKELY(((((0xc7ffU 
                                            >= (0x0000ffffU 
                                                & __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__destination_index))
                                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch
                                           [(0x0000ffffU 
                                             & __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__destination_index)]
                                            : 0U) != (IData)(__Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__expected_byte))))) {
                            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:242: Assertion failed in %m: T66 feature byte lane \346\217\220\345\217\226\351\224\231\350\257\257\357\274\232index=%0d actual=%02h expected=%02h\n",6, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile.check_read_byte_capture", 'T',-9
                                         , '#',64,VL_TIME_UNITED_Q(1000)
                                         , '~',32,__Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__destination_index
                                         , '~',8,((0xc7ffU 
                                                   >= 
                                                   (0x0000ffffU 
                                                    & __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__destination_index))
                                                   ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch
                                                  [
                                                  (0x0000ffffU 
                                                   & __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__destination_index)]
                                                   : 0U)
                                         , '~',8,(IData)(__Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__expected_byte));
                            VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 242, "", false);
                        }
                    } else if ((1U == __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__transfer_class)) {
                        if (VL_UNLIKELY(((((0x8fffU 
                                            >= (0x0000ffffU 
                                                & __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__destination_index))
                                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group
                                           [(0x0000ffffU 
                                             & __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__destination_index)]
                                            : 0U) != (IData)(__Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__expected_byte))))) {
                            VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:246: Assertion failed in %m: T66 weight byte lane \346\217\220\345\217\226\351\224\231\350\257\257\357\274\232index=%0d actual=%02h expected=%02h\n",6, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile.check_read_byte_capture", 'T',-9
                                         , '#',64,VL_TIME_UNITED_Q(1000)
                                         , '~',32,__Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__destination_index
                                         , '~',8,((0x8fffU 
                                                   >= 
                                                   (0x0000ffffU 
                                                    & __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__destination_index))
                                                   ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group
                                                  [
                                                  (0x0000ffffU 
                                                   & __Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__destination_index)]
                                                   : 0U)
                                         , '~',8,(IData)(__Vtask_tb_s2a_t66_layer0_tile__DOT__check_read_byte_capture__3__expected_byte));
                            VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 246, "", false);
                        }
                    }
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_capture_checked 
                        = ((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_capture_checked) 
                           | (0x0fU & ((IData)(1U) 
                                       << (3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__t66_read_capture_monitor__DOT__selected_lane))));
                }
            }
        }
    }
    co_return;
}

bool Vtb_s2a_t66_layer0_tile___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___trigger_anySet__act\n"); );
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

extern const VlWide<10>/*319:0*/ Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hb4617e49_0;
extern const VlUnpacked<IData/*31:0*/, 5> Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_hc6a14c36_0;

void Vtb_s2a_t66_layer0_tile___024root___act_comb__TOP__0(Vtb_s2a_t66_layer0_tile___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___act_comb__TOP__0\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ tb_s2a_t66_layer0_tile__DOT__request_transfer_class_comb;
    tb_s2a_t66_layer0_tile__DOT__request_transfer_class_comb = 0;
    VlWide<4>/*127:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_elements_wide;
    VL_ZERO_W(128, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_elements_wide);
    VlWide<4>/*127:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__expected_weight_bytes_wide;
    VL_ZERO_W(128, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__expected_weight_bytes_wide);
    VlWide<4>/*127:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_end_wide;
    VL_ZERO_W(128, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_end_wide;
    VL_ZERO_W(128, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_end_wide;
    VL_ZERO_W(128, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__quantized_weight_end_wide;
    VL_ZERO_W(128, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__quantized_weight_end_wide);
    QData/*63:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_numerator;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_numerator = 0;
    QData/*63:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_numerator;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_numerator = 0;
    QData/*63:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_shape_span;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_shape_span = 0;
    QData/*63:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_shape_span;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_shape_span = 0;
    QData/*63:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_shape_product;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_shape_product = 0;
    QData/*63:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_shape_product;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_shape_product = 0;
    QData/*63:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_span_plus_stride;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_span_plus_stride = 0;
    QData/*63:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_span_plus_stride;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_span_plus_stride = 0;
    VlWide<4>/*127:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_height_wide;
    VL_ZERO_W(128, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_height_wide);
    VlWide<4>/*127:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_width_wide;
    VL_ZERO_W(128, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_width_wide);
    VlWide<4>/*127:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_bytes_wide;
    VL_ZERO_W(128, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_bytes_wide);
    VlWide<4>/*127:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_weight_group_bytes_wide;
    VL_ZERO_W(128, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_weight_group_bytes_wide);
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__Vfuncout;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__Vfuncout = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__is_write;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__is_write = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__word_address;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__word_address = 0;
    VlWide<4>/*127:0*/ __Vtemp_1;
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
    IData/*31:0*/ __Vtemp_57;
    // Body
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_cancel 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__hard_reset;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__hard_reset)) 
           & (0U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state)));
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_rstrb = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_wstrb = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_write = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_valid = 0U;
    if ((1U & (~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__hard_reset)))) {
        if (((4U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state)))) {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_rstrb 
                = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_strobe_latched;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_write = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_valid = 1U;
        } else if ((0x10U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_write = 1U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_valid = 1U;
        }
        if ((1U & (~ ((4U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state)) 
                      || (8U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state)))))) {
            if ((0x10U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_wstrb 
                    = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_strobe_latched;
            }
        }
    }
    __Vtemp_1[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_batch_count_latched;
    __Vtemp_1[1U] = 0U;
    __Vtemp_1[2U] = 0U;
    __Vtemp_1[3U] = 0U;
    __Vtemp_2[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_channels_latched;
    __Vtemp_2[1U] = 0U;
    __Vtemp_2[2U] = 0U;
    __Vtemp_2[3U] = 0U;
    VL_MUL_W(4, __Vtemp_3, __Vtemp_1, __Vtemp_2);
    __Vtemp_4[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_height_latched;
    __Vtemp_4[1U] = 0U;
    __Vtemp_4[2U] = 0U;
    __Vtemp_4[3U] = 0U;
    VL_MUL_W(4, __Vtemp_5, __Vtemp_3, __Vtemp_4);
    __Vtemp_6[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_width_latched;
    __Vtemp_6[1U] = 0U;
    __Vtemp_6[2U] = 0U;
    __Vtemp_6[3U] = 0U;
    VL_MUL_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_elements_wide, __Vtemp_5, __Vtemp_6);
    __Vtemp_7[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_batch_count_latched;
    __Vtemp_7[1U] = 0U;
    __Vtemp_7[2U] = 0U;
    __Vtemp_7[3U] = 0U;
    __Vtemp_8[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched;
    __Vtemp_8[1U] = 0U;
    __Vtemp_8[2U] = 0U;
    __Vtemp_8[3U] = 0U;
    VL_MUL_W(4, __Vtemp_9, __Vtemp_7, __Vtemp_8);
    __Vtemp_10[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched;
    __Vtemp_10[1U] = 0U;
    __Vtemp_10[2U] = 0U;
    __Vtemp_10[3U] = 0U;
    VL_MUL_W(4, __Vtemp_11, __Vtemp_9, __Vtemp_10);
    __Vtemp_12[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched;
    __Vtemp_12[1U] = 0U;
    __Vtemp_12[2U] = 0U;
    __Vtemp_12[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_elements_wide, __Vtemp_11, __Vtemp_12);
    __Vtemp_13[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched;
    __Vtemp_13[1U] = 0U;
    __Vtemp_13[2U] = 0U;
    __Vtemp_13[3U] = 0U;
    __Vtemp_14[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_channels_latched;
    __Vtemp_14[1U] = 0U;
    __Vtemp_14[2U] = 0U;
    __Vtemp_14[3U] = 0U;
    VL_MUL_W(4, __Vtemp_15, __Vtemp_13, __Vtemp_14);
    __Vtemp_16[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched;
    __Vtemp_16[1U] = 0U;
    __Vtemp_16[2U] = 0U;
    __Vtemp_16[3U] = 0U;
    VL_MUL_W(4, __Vtemp_17, __Vtemp_15, __Vtemp_16);
    __Vtemp_18[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched;
    __Vtemp_18[1U] = 0U;
    __Vtemp_18[2U] = 0U;
    __Vtemp_18[3U] = 0U;
    VL_MUL_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__expected_weight_bytes_wide, __Vtemp_17, __Vtemp_18);
    __Vtemp_19[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_channels_latched;
    __Vtemp_19[1U] = 0U;
    __Vtemp_19[2U] = 0U;
    __Vtemp_19[3U] = 0U;
    __Vtemp_20[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched;
    __Vtemp_20[1U] = 0U;
    __Vtemp_20[2U] = 0U;
    __Vtemp_20[3U] = 0U;
    VL_MUL_W(4, __Vtemp_21, __Vtemp_19, __Vtemp_20);
    __Vtemp_22[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched;
    __Vtemp_22[1U] = 0U;
    __Vtemp_22[2U] = 0U;
    __Vtemp_22[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_wide, __Vtemp_21, __Vtemp_22);
    __Vtemp_23[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_base_latched;
    __Vtemp_23[1U] = 0U;
    __Vtemp_23[2U] = 0U;
    __Vtemp_23[3U] = 0U;
    __Vtemp_24[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_length_latched;
    __Vtemp_24[1U] = 0U;
    __Vtemp_24[2U] = 0U;
    __Vtemp_24[3U] = 0U;
    VL_ADD_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_end_wide, __Vtemp_23, __Vtemp_24);
    __Vtemp_25[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_base_latched;
    __Vtemp_25[1U] = 0U;
    __Vtemp_25[2U] = 0U;
    __Vtemp_25[3U] = 0U;
    __Vtemp_26[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_length_latched;
    __Vtemp_26[1U] = 0U;
    __Vtemp_26[2U] = 0U;
    __Vtemp_26[3U] = 0U;
    VL_ADD_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_end_wide, __Vtemp_25, __Vtemp_26);
    __Vtemp_27[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_base_latched;
    __Vtemp_27[1U] = 0U;
    __Vtemp_27[2U] = 0U;
    __Vtemp_27[3U] = 0U;
    __Vtemp_28[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_length_latched;
    __Vtemp_28[1U] = 0U;
    __Vtemp_28[2U] = 0U;
    __Vtemp_28[3U] = 0U;
    VL_ADD_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_end_wide, __Vtemp_27, __Vtemp_28);
    __Vtemp_29[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__quantized_weight_offset_latched;
    __Vtemp_29[1U] = 0U;
    __Vtemp_29[2U] = 0U;
    __Vtemp_29[3U] = 0U;
    __Vtemp_30[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__quantized_weight_bytes_latched;
    __Vtemp_30[1U] = 0U;
    __Vtemp_30[2U] = 0U;
    __Vtemp_30[3U] = 0U;
    VL_ADD_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__quantized_weight_end_wide, __Vtemp_29, __Vtemp_30);
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_height_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__pad_top_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__pad_bottom_latched)));
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_width_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__pad_left_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__pad_right_latched)));
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_shape_span 
        = (tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_numerator 
           - (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched)));
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_shape_span 
        = (tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_numerator 
           - (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched)));
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_shape_product 
        = ((QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_y_latched)));
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_shape_product 
        = ((QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_x_latched)));
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_span_plus_stride 
        = (tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_shape_span 
           + (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_y_latched)));
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_span_plus_stride 
        = (tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_shape_span 
           + (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_x_latched)));
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_height_wide[0U] = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_height_wide[1U] = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_height_wide[2U] = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_height_wide[3U] = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_width_wide[0U] = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_width_wide[1U] = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_width_wide[2U] = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_width_wide[3U] = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_bytes_wide[0U] = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_bytes_wide[1U] = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_bytes_wide[2U] = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_bytes_wide[3U] = 0U;
    if (((0U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched) 
         & (0U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched))) {
        __Vtemp_31[0U] = (((8U > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched)
                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched
                            : 8U) - (IData)(1U));
        __Vtemp_31[1U] = 0U;
        __Vtemp_31[2U] = 0U;
        __Vtemp_31[3U] = 0U;
        __Vtemp_32[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_y_latched;
        __Vtemp_32[1U] = 0U;
        __Vtemp_32[2U] = 0U;
        __Vtemp_32[3U] = 0U;
        VL_MUL_W(4, __Vtemp_33, __Vtemp_31, __Vtemp_32);
        __Vtemp_34[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched;
        __Vtemp_34[1U] = 0U;
        __Vtemp_34[2U] = 0U;
        __Vtemp_34[3U] = 0U;
        VL_ADD_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_height_wide, __Vtemp_33, __Vtemp_34);
        __Vtemp_35[0U] = (((8U > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched)
                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched
                            : 8U) - (IData)(1U));
        __Vtemp_35[1U] = 0U;
        __Vtemp_35[2U] = 0U;
        __Vtemp_35[3U] = 0U;
        __Vtemp_36[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_x_latched;
        __Vtemp_36[1U] = 0U;
        __Vtemp_36[2U] = 0U;
        __Vtemp_36[3U] = 0U;
        VL_MUL_W(4, __Vtemp_37, __Vtemp_35, __Vtemp_36);
        __Vtemp_38[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched;
        __Vtemp_38[1U] = 0U;
        __Vtemp_38[2U] = 0U;
        __Vtemp_38[3U] = 0U;
        VL_ADD_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_width_wide, __Vtemp_37, __Vtemp_38);
        VL_MUL_W(4, __Vtemp_39, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_height_wide, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_width_wide);
        __Vtemp_40[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_channels_latched;
        __Vtemp_40[1U] = 0U;
        __Vtemp_40[2U] = 0U;
        __Vtemp_40[3U] = 0U;
        VL_MUL_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_bytes_wide, __Vtemp_39, __Vtemp_40);
    }
    __Vtemp_41[0U] = ((8U > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched)
                       ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched
                       : 8U);
    __Vtemp_41[1U] = 0U;
    __Vtemp_41[2U] = 0U;
    __Vtemp_41[3U] = 0U;
    VL_MUL_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_weight_group_bytes_wide, __Vtemp_41, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_wide);
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__validation_ok = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__validation_error = 1U;
    __Vtemp_43[0U] = 0x00001fffU;
    __Vtemp_43[1U] = 0U;
    __Vtemp_43[2U] = 0U;
    __Vtemp_43[3U] = 0U;
    if ((1U & ((((((((((((((((((((((~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__buffer_owner_pl)) 
                                   | (1U < (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__activation_mode_latched))) 
                                  | (1U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_batch_count_latched)) 
                                 | (1U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_batch_count_latched)) 
                                | (0U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_batch_latched)) 
                               | (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_channels_latched)) 
                              | (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_height_latched)) 
                             | (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_width_latched)) 
                            | (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched)) 
                           | (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched)) 
                          | (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched)) 
                         | (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched)) 
                        | (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched)) 
                       | (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_y_latched)) 
                      | (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_x_latched)) 
                     | (1U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__groups_latched)) 
                    | (0U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__padding_latched)) 
                   | (0U == (((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_wide[0U] 
                               | vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_wide[1U]) 
                              | vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_wide[2U]) 
                             | vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_wide[3U]))) 
                  | VL_LT_W(4, __Vtemp_43, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_wide)) 
                 | (0x00000026U <= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched)) 
                | ((0x00000026U > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched) 
                   & (0U != ((0x25U >= (0x0000003fU 
                                        & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched))
                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OP
                             [(0x0000003fU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched)]
                              : 0U)))) | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched 
                                          != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_layer_index_latched)))) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__validation_error 
            = (((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched 
                 != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_layer_index_latched) 
                | (0x00000026U <= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched))
                ? 2U : 1U);
    } else {
        __Vtemp_44[0U] = 0xffffffffU;
        __Vtemp_44[1U] = 0U;
        __Vtemp_44[2U] = 0U;
        __Vtemp_44[3U] = 0U;
        __Vtemp_45[0U] = 0xffffffffU;
        __Vtemp_45[1U] = 0U;
        __Vtemp_45[2U] = 0U;
        __Vtemp_45[3U] = 0U;
        __Vtemp_46[0U] = 0xffffffffU;
        __Vtemp_46[1U] = 0U;
        __Vtemp_46[2U] = 0U;
        __Vtemp_46[3U] = 0U;
        if ((((((VL_LT_W(4, __Vtemp_44, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_elements_wide) 
                 | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_length_latched 
                    != tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_elements_wide[0U])) 
                | VL_LT_W(4, __Vtemp_45, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_elements_wide)) 
               | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_length_latched 
                  != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_elements_wide[0U])) 
              | VL_LT_W(4, __Vtemp_46, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__expected_weight_bytes_wide)) 
             | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__quantized_weight_bytes_latched 
                != tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__expected_weight_bytes_wide[0U]))) {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__validation_error = 3U;
        } else {
            __Vtemp_47[0U] = 0U;
            __Vtemp_47[1U] = 1U;
            __Vtemp_47[2U] = 0U;
            __Vtemp_47[3U] = 0U;
            __Vtemp_48[0U] = 0U;
            __Vtemp_48[1U] = 1U;
            __Vtemp_48[2U] = 0U;
            __Vtemp_48[3U] = 0U;
            __Vtemp_49[0U] = 0U;
            __Vtemp_49[1U] = 1U;
            __Vtemp_49[2U] = 0U;
            __Vtemp_49[3U] = 0U;
            __Vtemp_50[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_length_latched;
            __Vtemp_50[1U] = 0U;
            __Vtemp_50[2U] = 0U;
            __Vtemp_50[3U] = 0U;
            __Vtemp_51[0U] = 0x00000c5cU;
            __Vtemp_51[1U] = 0U;
            __Vtemp_51[2U] = 0U;
            __Vtemp_51[3U] = 0U;
            __Vtemp_52[0U] = ((0x25U >= (0x0000003fU 
                                         & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched))
                               ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                              [(0x0000003fU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched)]
                               : 0U);
            __Vtemp_52[1U] = 0U;
            __Vtemp_52[2U] = 0U;
            __Vtemp_52[3U] = 0U;
            __Vtemp_53[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched;
            __Vtemp_53[1U] = 0U;
            __Vtemp_53[2U] = 0U;
            __Vtemp_53[3U] = 0U;
            VL_ADD_W(4, __Vtemp_54, __Vtemp_52, __Vtemp_53);
            __Vtemp_55[0U] = 0x0000c800U;
            __Vtemp_55[1U] = 0U;
            __Vtemp_55[2U] = 0U;
            __Vtemp_55[3U] = 0U;
            __Vtemp_56[0U] = 0x00009000U;
            __Vtemp_56[1U] = 0U;
            __Vtemp_56[2U] = 0U;
            __Vtemp_56[3U] = 0U;
            if (((((((((VL_LT_W(4, __Vtemp_47, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_end_wide) 
                        | VL_LT_W(4, __Vtemp_48, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_end_wide)) 
                       | VL_LT_W(4, __Vtemp_49, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_end_wide)) 
                      | (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_length_latched)) 
                     | VL_GT_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__quantized_weight_end_wide, __Vtemp_50)) 
                    | (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                        [(0x0000003fU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched)]
                         : 0U) != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched)) 
                   | VL_LT_W(4, __Vtemp_51, __Vtemp_54)) 
                  | VL_LT_W(4, __Vtemp_55, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_bytes_wide)) 
                 | VL_LT_W(4, __Vtemp_56, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_weight_group_bytes_wide))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__validation_error = 2U;
            } else if (((((((tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_numerator 
                             < (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched))) 
                            | (tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_numerator 
                               < (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched)))) 
                           | (tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_shape_product 
                              <= tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_shape_span)) 
                          | (tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_shape_product 
                             > tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_span_plus_stride)) 
                         | (tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_shape_product 
                            <= tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_shape_span)) 
                        | (tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_shape_product 
                           > tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_span_plus_stride))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__validation_error = 1U;
            } else {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__validation_ok = 1U;
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__validation_error = 0U;
            }
        }
    }
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__word_address 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__is_write 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_write;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__Vfuncout 
        = ((IData)(__Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__is_write)
            ? (((0x01000000U <= __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__word_address) 
                & (0x01152000U > __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__word_address))
                ? 2U : 0xffffffffU) : ((0x0007ec00U 
                                        > __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__word_address)
                                        ? 0U : (((0x0010013cU 
                                                  <= __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__word_address) 
                                                 & (0x0010049cU 
                                                    > __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__word_address))
                                                 ? 1U
                                                 : 0xffffffffU)));
    tb_s2a_t66_layer0_tile__DOT__request_transfer_class_comb 
        = __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__Vfuncout;
    if (((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__hard_reset) 
         | (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__memory_pending))) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_ready = 0U;
    } else if ((0U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_request)) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_ready 
            = (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__stall_remaining);
    } else if (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_valid) {
        if (VL_GTS_III(32, 0U, tb_s2a_t66_layer0_tile__DOT__request_transfer_class_comb)) {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_ready = 1U;
        } else {
            vlSelfRef.__Vfunc_tb_s2a_t66_layer0_tile__DOT__request_stall_cycles__1__index 
                = ((2U >= (3U & tb_s2a_t66_layer0_tile__DOT__request_transfer_class_comb))
                    ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count
                   [(3U & tb_s2a_t66_layer0_tile__DOT__request_transfer_class_comb)]
                    : 0U);
            __Vtemp_57 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, vlSelfRef.__Vfunc_tb_s2a_t66_layer0_tile__DOT__request_stall_cycles__1__index, (IData)(5U)), Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hb4617e49_0);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_0__request_stall_cycles 
                = Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_hc6a14c36_0
                [__Vtemp_57];
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_ready 
                = (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_0__request_stall_cycles);
        }
    } else {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_ready = 0U;
    }
}

extern const VlWide<16>/*511:0*/ Vtb_s2a_t66_layer0_tile__ConstPool__CONST_h24ab78b6_0;

void Vtb_s2a_t66_layer0_tile___024root___nba_sequent__TOP__0(Vtb_s2a_t66_layer0_tile___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___nba_sequent__TOP__0\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ tb_s2a_t66_layer0_tile__DOT__transfer_class_work;
    tb_s2a_t66_layer0_tile__DOT__transfer_class_work = 0;
    QData/*63:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_plane_bytes;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_plane_bytes = 0;
    QData/*63:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_input_y;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_input_y = 0;
    QData/*63:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_input_x;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_input_x = 0;
    QData/*63:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_source_offset;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_source_offset = 0;
    IData/*31:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_area;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_area = 0;
    IData/*31:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_y;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_y = 0;
    IData/*31:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_x;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_x = 0;
    QData/*63:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_y;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_y = 0;
    QData/*63:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_x;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_x = 0;
    CData/*0:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_tap_in_bounds;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_tap_in_bounds = 0;
    QData/*63:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index_wide;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index_wide = 0;
    IData/*31:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index = 0;
    IData/*31:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_index;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_index = 0;
    VlWide<3>/*79:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_parameter;
    VL_ZERO_W(80, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_parameter);
    IData/*31:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_accumulator;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_accumulator = 0;
    IData/*31:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_multiplier;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_multiplier = 0;
    IData/*31:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_q_shift;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_q_shift = 0;
    IData/*31:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_magnitude;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_magnitude = 0;
    QData/*63:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_product;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_product = 0;
    QData/*63:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_rounding_add;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_rounding_add = 0;
    QData/*63:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_rounded_magnitude;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_rounded_magnitude = 0;
    QData/*63:0*/ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_signed_value;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_signed_value = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__4__Vfuncout;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__4__Vfuncout = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__4__is_write;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__4__is_write = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__4__word_address;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__4__word_address = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__request_stall_cycles__5__index;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__request_stall_cycles__5__index = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__request_stall_cycles__6__index;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__request_stall_cycles__6__index = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__request_stall_cycles__7__index;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__request_stall_cycles__7__index = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__response_stall_cycles__8__Vfuncout;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__response_stall_cycles__8__Vfuncout = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__response_stall_cycles__8__index;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__response_stall_cycles__8__index = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__strobe_lane_index__9__Vfuncout;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__strobe_lane_index__9__Vfuncout = 0;
    CData/*3:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__strobe_lane_index__9__strobe;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__strobe_lane_index__9__strobe = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__response_stall_cycles__10__index;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__response_stall_cycles__10__index = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__response_stall_cycles__11__index;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__response_stall_cycles__11__index = 0;
    CData/*0:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__memory_pending;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__memory_pending = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__response_data;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__response_data = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__response_delay_remaining;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__response_delay_remaining = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__request_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__request_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__response_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__response_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__pending_transfer_class;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__pending_transfer_class = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__active_request_stall_observed;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__active_request_stall_observed = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__active_response_stall_observed;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__active_response_stall_observed = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__output_write_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__output_write_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__input_read_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__input_read_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__weight_read_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__weight_read_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__stall_cycle_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__stall_cycle_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__response_stall_cycle_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__response_stall_cycle_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__held_request;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__held_request = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__stall_remaining;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__stall_remaining = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__cycle_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__cycle_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__next_cycle_progress;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__next_cycle_progress = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__result_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__result_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__next_progress;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__next_progress = 0;
    CData/*0:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__held_write;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__held_write = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__held_address;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__held_address = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__held_wdata;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__held_wdata = 0;
    CData/*3:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__held_rstrb;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__held_rstrb = 0;
    CData/*3:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__held_wstrb;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__held_wstrb = 0;
    CData/*4:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_channels_latched;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_channels_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_y_latched;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_y_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_x_latched;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_x_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_height;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_height = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_width;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_width = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_height;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_height = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_width;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_width = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_byte_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_byte_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_point_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_point_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_channel;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_channel = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_y;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_x;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_lane_index;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_lane_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_reduction_index;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_reduction_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_index;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_channel;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_channel = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_y;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_x;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_lane_index;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_lane_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_index;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_index = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_y;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_y = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_x;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_x = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_lane;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_lane = 0;
    IData/*31:0*/ __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_lane_index;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_lane_index = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_request_count__v0;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_request_count__v0 = 0;
    SData/*9:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_seen__v0;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_seen__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_request_count__v1;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_request_count__v1 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__class_request_stall_count__v3;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__class_request_stall_count__v3 = 0;
    CData/*1:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__class_request_stall_count__v3;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__class_request_stall_count__v3 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_request_stall_count__v3;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_request_stall_count__v3 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__class_request_count__v3;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__class_request_count__v3 = 0;
    CData/*1:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__class_request_count__v3;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__class_request_count__v3 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_request_count__v3;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_request_count__v3 = 0;
    IData/*20:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__output_seen__v0;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__output_seen__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__output_seen__v0;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__output_seen__v0 = 0;
    IData/*20:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__output_seen__v1;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__output_seen__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__output_seen__v1;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__output_seen__v1 = 0;
    IData/*20:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__output_seen__v2;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__output_seen__v2 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__output_seen__v2;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__output_seen__v2 = 0;
    IData/*20:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__output_seen__v3;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__output_seen__v3 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__output_seen__v3;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__output_seen__v3 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count__v4;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count__v4 = 0;
    CData/*1:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count__v4;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count__v4 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count__v4;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count__v4 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count__v4;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count__v4 = 0;
    CData/*1:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count__v4;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count__v4 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count__v4;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count__v4 = 0;
    SData/*9:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_seen__v1;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_seen__v1 = 0;
    SData/*9:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_seen__v2;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_seen__v2 = 0;
    SData/*9:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_seen__v3;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_seen__v3 = 0;
    SData/*9:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_seen__v4;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_seen__v4 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__class_response_count__v3;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__class_response_count__v3 = 0;
    CData/*1:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__class_response_count__v3;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__class_response_count__v3 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_response_count__v3;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_response_count__v3 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__class_response_stall_count__v3;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__class_response_stall_count__v3 = 0;
    CData/*1:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__class_response_stall_count__v3;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__class_response_stall_count__v3 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_response_stall_count__v3;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_response_stall_count__v3 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v0;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v0 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_block__v0;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_block__v0 = 0;
    SData/*8:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_block__v0;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_block__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_block__v0;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_block__v0 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v0;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v0;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v0 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v1;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v1;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v1 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v2;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v2 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v2;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v2 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v3;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v3 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v3;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v3 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v4;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v4 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v4;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v4 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v5;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v5 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v5;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v5 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v6;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v6 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v6;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v6 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v7;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v7 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v7;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v7 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v8;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v8 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v8;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v8 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v9;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v9 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v9;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v9 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v10;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v10 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v11;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v11 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v12;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v12 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v13;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v13 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v14;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v14 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v15;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v15 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v16;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v16 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v16;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v16 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v17;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v17 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v17;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v17 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v18;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v18 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v19;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v19 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v20;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v20 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v21;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v21 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v22;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v22 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v23;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v23 = 0;
    VlWide<3>/*79:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v8;
    VL_ZERO_W(80, __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v8);
    CData/*2:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v8;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v8 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v8;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v8 = 0;
    IData/*31:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias__v8;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias__v8 = 0;
    CData/*2:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias__v8;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias__v8 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group__v0;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group__v0 = 0;
    SData/*15:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group__v0;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group__v0;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group__v0 = 0;
    CData/*7:0*/ __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v0;
    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v0 = 0;
    SData/*15:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v0;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v0 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v0;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v0 = 0;
    SData/*15:0*/ __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v1;
    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v1 = 0;
    CData/*0:0*/ __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v1;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v1 = 0;
    IData/*31:0*/ __Vtemp_1;
    IData/*31:0*/ __Vtemp_2;
    IData/*31:0*/ __Vtemp_3;
    IData/*31:0*/ __Vtemp_4;
    IData/*31:0*/ __Vtemp_5;
    IData/*31:0*/ __Vtemp_6;
    VlWide<4>/*127:0*/ __Vtemp_7;
    VlWide<3>/*95:0*/ __Vtemp_17;
    VlWide<3>/*95:0*/ __Vtemp_18;
    // Body
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_height 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_height;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_point_count 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_point_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_index 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_index;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_block__v0 = 0U;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_lane_index 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_lane_index;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_reduction_index 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_reduction_index;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_lane_index 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_lane_index;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_y 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_y;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_x 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_x;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_lane 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_lane;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_lane_index 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_lane_index;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v0 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v8 = 0U;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_width 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_width;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_height 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_height;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_width 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_width;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_byte_count 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_byte_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_channel 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_channel;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_y 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_y;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_x 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_x;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_index 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_index;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_channel 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_channel;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_y 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_y;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_x 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_x;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_channels_latched 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_channels_latched;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group__v0 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v0 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v1 = 0U;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v0 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v1 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v2 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v3 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v4 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v5 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v6 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v7 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v8 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v9 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v16 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v17 = 0U;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_y_latched 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_y_latched;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_x_latched 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_x_latched;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__response_data 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_data;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__request_count 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__request_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__response_count 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__pending_transfer_class 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__pending_transfer_class;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__active_request_stall_observed 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__active_request_stall_observed;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__active_response_stall_observed 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__active_response_stall_observed;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__output_write_count 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__input_read_count 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__input_read_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__weight_read_count 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_read_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__stall_cycle_count 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__stall_cycle_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__response_stall_cycle_count 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_stall_cycle_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__cycle_count 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__cycle_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__next_cycle_progress 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__next_cycle_progress;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__result_count 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__result_count;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__next_progress 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__next_progress;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__held_write 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_write;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__held_address 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_address;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__held_wdata 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_wdata;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__held_rstrb 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_rstrb;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__held_wstrb 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_wstrb;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_response_count__v3 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_request_stall_count__v3 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_response_stall_count__v3 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count__v4 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count__v4 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__output_seen__v0 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__output_seen__v1 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__output_seen__v2 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__output_seen__v3 = 0U;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__held_request 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_request;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__stall_remaining 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__stall_remaining;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_request_count__v3 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_request_count__v0 = 0U;
    __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_request_count__v1 = 0U;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__response_delay_remaining 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_delay_remaining;
    __Vdly__tb_s2a_t66_layer0_tile__DOT__memory_pending 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__memory_pending;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__4__word_address 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__4__is_write 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_write;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__4__Vfuncout 
        = ((IData)(__Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__4__is_write)
            ? (((0x01000000U <= __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__4__word_address) 
                & (0x01152000U > __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__4__word_address))
                ? 2U : 0xffffffffU) : ((0x0007ec00U 
                                        > __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__4__word_address)
                                        ? 0U : (((0x0010013cU 
                                                  <= __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__4__word_address) 
                                                 & (0x0010049cU 
                                                    > __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__4__word_address))
                                                 ? 1U
                                                 : 0xffffffffU)));
    tb_s2a_t66_layer0_tile__DOT__transfer_class_work 
        = __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__4__Vfuncout;
    if (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__hard_reset) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__reset_index = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__memory_pending = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__response_data = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_error = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__response_delay_remaining = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__request_count = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__response_count = 0U;
        __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_request_count__v0 = 1U;
        while (VL_GTS_III(32, 0x00000360U, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__reset_index)) {
            if (VL_LIKELY(((0x035fU >= (0x000003ffU 
                                        & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__reset_index))))) {
                __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_seen__v0 
                    = (0x000003ffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__reset_index);
                vlSelfRef.__VdlyCommitQueuetb_s2a_t66_layer0_tile__DOT__weight_seen.enqueue(0U, (IData)(__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_seen__v0));
            }
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__reset_index 
                = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__reset_index);
        }
        __Vdly__tb_s2a_t66_layer0_tile__DOT__pending_transfer_class = 0xffffffffU;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__active_request_stall_observed = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__active_response_stall_observed = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__output_write_count = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point0_golden_seen = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point1_golden_seen = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__input_read_count = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__weight_read_count = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__stall_cycle_count = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__response_stall_cycle_count = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__held_request = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__stall_remaining = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__cycle_count = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__next_cycle_progress = 0x000186a0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__result_count = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__next_progress = 0x00030d40U;
        __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_request_count__v1 = 1U;
    } else {
        if (((0x13U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state)) 
             & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__result_ready))) {
            __Vdly__tb_s2a_t66_layer0_tile__DOT__result_count 
                = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__result_count);
        }
        __Vdly__tb_s2a_t66_layer0_tile__DOT__cycle_count 
            = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__cycle_count);
        if (VL_UNLIKELY((VL_GTES_III(32, ((IData)(1U) 
                                          + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__cycle_count), vlSelfRef.tb_s2a_t66_layer0_tile__DOT__next_cycle_progress)))) {
            __Vdly__tb_s2a_t66_layer0_tile__DOT__next_cycle_progress 
                = ((IData)(0x000186a0U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__next_cycle_progress);
            VL_WRITEF_NX("T66_CYCLE_PROGRESS cycles=%0d requests=%0d writes=%0d\n",3
                         , '~',32,((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__cycle_count)
                         , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__request_count
                         , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count);
        }
        if ((0U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_request)) {
            if (VL_UNLIKELY(((1U & ((((((~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_valid)) 
                                        | ((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_write) 
                                           != (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_write))) 
                                       | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched 
                                          != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_address)) 
                                      | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_wdata_latched 
                                         != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_wdata)) 
                                     | ((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_rstrb) 
                                        != (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_rstrb))) 
                                    | ((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_wstrb) 
                                       != (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_wstrb))))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:377: Assertion failed in %m: T66 backpressure \346\234\237\351\227\264 request \345\255\227\346\256\265\345\217\230\345\214\226\357\274\232cycle=%0d\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__cycle_count);
                VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 377, "", false);
            }
        }
        if (((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_valid) 
             & (~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_ready)))) {
            __Vdly__tb_s2a_t66_layer0_tile__DOT__stall_cycle_count 
                = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__stall_cycle_count);
            __Vdly__tb_s2a_t66_layer0_tile__DOT__active_request_stall_observed 
                = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__active_request_stall_observed);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, tb_s2a_t66_layer0_tile__DOT__transfer_class_work)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:383: Assertion failed in %m: T66 backpressure \350\257\267\346\261\202\344\270\215\345\261\236\344\272\216\345\267\262\346\230\240\345\260\204\345\257\271\350\261\241\357\274\232addr=%08h write=%b\n",5, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '#',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched
                             , '#',1,(IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_write));
                VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 383, "", false);
            }
            if ((2U >= (3U & tb_s2a_t66_layer0_tile__DOT__transfer_class_work))) {
                __VdlyVal__tb_s2a_t66_layer0_tile__DOT__class_request_stall_count__v3 
                    = ((IData)(1U) + ((2U >= (3U & tb_s2a_t66_layer0_tile__DOT__transfer_class_work))
                                       ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_stall_count
                                      [(3U & tb_s2a_t66_layer0_tile__DOT__transfer_class_work)]
                                       : 0U));
                __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__class_request_stall_count__v3 
                    = (3U & tb_s2a_t66_layer0_tile__DOT__transfer_class_work);
                __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_request_stall_count__v3 = 1U;
            }
            if ((0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_request)) {
                __Vfunc_tb_s2a_t66_layer0_tile__DOT__request_stall_cycles__5__index 
                    = ((2U >= (3U & tb_s2a_t66_layer0_tile__DOT__transfer_class_work))
                        ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count
                       [(3U & tb_s2a_t66_layer0_tile__DOT__transfer_class_work)]
                        : 0U);
                __Vtemp_1 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__request_stall_cycles__5__index, (IData)(5U)), Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hb4617e49_0);
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_1__request_stall_cycles 
                    = Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_hc6a14c36_0
                    [__Vtemp_1];
                __Vdly__tb_s2a_t66_layer0_tile__DOT__held_request = 1U;
                __Vdly__tb_s2a_t66_layer0_tile__DOT__held_write 
                    = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_write;
                __Vdly__tb_s2a_t66_layer0_tile__DOT__held_address 
                    = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched;
                __Vdly__tb_s2a_t66_layer0_tile__DOT__held_wdata 
                    = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_wdata_latched;
                __Vdly__tb_s2a_t66_layer0_tile__DOT__held_rstrb 
                    = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_rstrb;
                __Vdly__tb_s2a_t66_layer0_tile__DOT__held_wstrb 
                    = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_wstrb;
                __Vdly__tb_s2a_t66_layer0_tile__DOT__stall_remaining 
                    = (vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_1__request_stall_cycles 
                       - (IData)(1U));
            } else if (VL_LTS_III(32, 0U, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__stall_remaining)) {
                __Vdly__tb_s2a_t66_layer0_tile__DOT__stall_remaining 
                    = (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__stall_remaining 
                       - (IData)(1U));
            }
        }
        if (((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_valid) 
             & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_ready))) {
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, tb_s2a_t66_layer0_tile__DOT__transfer_class_work)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:405: Assertion failed in %m: T66 \350\257\267\346\261\202\344\270\215\345\261\236\344\272\216\345\267\262\346\230\240\345\260\204\345\257\271\350\261\241\357\274\232addr=%08h write=%b\n",5, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '#',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched
                             , '#',1,(IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_write));
                VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 405, "", false);
            }
            if (VL_UNLIKELY((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__memory_pending))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:408: Assertion failed in %m: T66 memory model \345\217\221\347\216\260\347\254\254\344\272\214\344\270\252 outstanding \350\257\267\346\261\202\n",3, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 408, "", false);
            }
            __Vdly__tb_s2a_t66_layer0_tile__DOT__stall_remaining = 0U;
            if (VL_UNLIKELY((((0U != (3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched)) 
                              | ((0U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_rstrb)) 
                                 & (0U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_wstrb))))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:412: Assertion failed in %m: T66 \350\257\267\346\261\202\346\234\252\345\257\271\351\275\220\346\210\226 byte strobe \344\270\272\347\251\272\357\274\232addr=%08h rstrb=%b wstrb=%b\n",6, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '#',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched
                             , '#',4,(IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_rstrb)
                             , '#',4,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_wstrb);
                VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 412, "", false);
            }
            if (VL_UNLIKELY((((0U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_request) 
                              & ((((((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_write) 
                                     != (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_write)) 
                                    | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched 
                                       != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_address)) 
                                   | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_wdata_latched 
                                      != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_wdata)) 
                                  | ((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_rstrb) 
                                     != (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_rstrb))) 
                                 | ((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_wstrb) 
                                    != (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_wstrb))))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:421: Assertion failed in %m: T66 \346\216\245\345\217\227\346\227\266 request \345\255\227\346\256\265\344\270\216 stalled request \344\270\215\344\270\200\350\207\264\n",3, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 421, "", false);
            }
            if ((2U >= (3U & tb_s2a_t66_layer0_tile__DOT__transfer_class_work))) {
                __Vfunc_tb_s2a_t66_layer0_tile__DOT__request_stall_cycles__6__index 
                    = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count
                    [(3U & tb_s2a_t66_layer0_tile__DOT__transfer_class_work)];
                __VdlyVal__tb_s2a_t66_layer0_tile__DOT__class_request_count__v3 
                    = ((IData)(1U) + ((2U >= (3U & tb_s2a_t66_layer0_tile__DOT__transfer_class_work))
                                       ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count
                                      [(3U & tb_s2a_t66_layer0_tile__DOT__transfer_class_work)]
                                       : 0U));
                __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__class_request_count__v3 
                    = (3U & tb_s2a_t66_layer0_tile__DOT__transfer_class_work);
                __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_request_count__v3 = 1U;
                __Vfunc_tb_s2a_t66_layer0_tile__DOT__response_stall_cycles__8__index 
                    = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count
                    [(3U & tb_s2a_t66_layer0_tile__DOT__transfer_class_work)];
            } else {
                __Vfunc_tb_s2a_t66_layer0_tile__DOT__request_stall_cycles__6__index = 0U;
                __Vfunc_tb_s2a_t66_layer0_tile__DOT__response_stall_cycles__8__index = 0U;
            }
            __Vdly__tb_s2a_t66_layer0_tile__DOT__memory_pending = 1U;
            __Vtemp_2 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__request_stall_cycles__6__index, (IData)(5U)), Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hb4617e49_0);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_2__request_stall_cycles 
                = Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_hc6a14c36_0
                [__Vtemp_2];
            __Vdly__tb_s2a_t66_layer0_tile__DOT__held_request = 0U;
            if (VL_UNLIKELY(((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__active_request_stall_observed 
                              != vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_2__request_stall_cycles)))) {
                __Vfunc_tb_s2a_t66_layer0_tile__DOT__request_stall_cycles__7__index 
                    = ((2U >= (3U & tb_s2a_t66_layer0_tile__DOT__transfer_class_work))
                        ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count
                       [(3U & tb_s2a_t66_layer0_tile__DOT__transfer_class_work)]
                        : 0U);
                __Vtemp_3 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__request_stall_cycles__7__index, (IData)(5U)), Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hb4617e49_0);
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_3__request_stall_cycles 
                    = Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_hc6a14c36_0
                    [__Vtemp_3];
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:427: Assertion failed in %m: T66 request stall \345\272\217\345\210\227\351\224\231\350\257\257\357\274\232class=%0d index=%0d expected=%0d actual=%0d\n",7, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,tb_s2a_t66_layer0_tile__DOT__transfer_class_work
                             , '~',32,((2U >= (3U & tb_s2a_t66_layer0_tile__DOT__transfer_class_work))
                                        ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count
                                       [(3U & tb_s2a_t66_layer0_tile__DOT__transfer_class_work)]
                                        : 0U), '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_3__request_stall_cycles
                             , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__active_request_stall_observed);
                VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 427, "", false);
            }
            __Vdly__tb_s2a_t66_layer0_tile__DOT__request_count 
                = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__request_count);
            __Vdly__tb_s2a_t66_layer0_tile__DOT__active_request_stall_observed = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__pending_transfer_class 
                = tb_s2a_t66_layer0_tile__DOT__transfer_class_work;
            __Vtemp_4 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__response_stall_cycles__8__index, (IData)(5U)), Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hb4617e49_0);
            __Vfunc_tb_s2a_t66_layer0_tile__DOT__response_stall_cycles__8__Vfuncout 
                = Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_hc6a14c36_0
                [__Vtemp_4];
            __Vdly__tb_s2a_t66_layer0_tile__DOT__response_delay_remaining 
                = __Vfunc_tb_s2a_t66_layer0_tile__DOT__response_stall_cycles__8__Vfuncout;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__response_data = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_error = 0U;
            if (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_write) {
                if (VL_UNLIKELY(((((0U != (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_rstrb)) 
                                   | (0U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_wstrb))) 
                                  | (1U != VL_COUNTONES_I((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_wstrb))))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:447: Assertion failed in %m: T66 \345\206\231\350\257\267\346\261\202\346\226\271\345\220\221\346\210\226 strobe \351\224\231\350\257\257\357\274\232r=%b w=%b\n",5, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '#',4,(IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_rstrb)
                                 , '#',4,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_wstrb);
                    VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 447, "", false);
                }
                if ((1U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_wstrb))) {
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work 
                        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched;
                    if (VL_UNLIKELY((((0x01000000U 
                                       > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work) 
                                      | (0x01152000U 
                                         <= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work))))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:455: Assertion failed in %m: T66 \345\206\231\350\257\267\346\261\202\350\266\212\347\225\214\357\274\232address=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '#',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work);
                        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 455, "", false);
                    }
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index 
                        = (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work 
                           - (IData)(0x01000000U));
                    if (VL_UNLIKELY((((0x00151fffU 
                                       >= (0x001fffffU 
                                           & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index)) 
                                      && vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_seen
                                      [(0x001fffffU 
                                        & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index)])))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:459: Assertion failed in %m: T66 \351\207\215\345\244\215\345\206\231\350\276\223\345\207\272\345\255\227\350\212\202\357\274\232index=%0d address=%08h\n",5, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index
                                     , '#',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work);
                        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 459, "", false);
                    }
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__observed_byte_work 
                        = (0x000000ffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_wdata_latched);
                    if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__observed_byte_work) 
                                      != ((0x00151fffU 
                                           >= (0x001fffffU 
                                               & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index))
                                           ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__expected_bytes
                                          [(0x001fffffU 
                                            & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index)]
                                           : 0U))))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:464: Assertion failed in %m: T66 \350\276\223\345\207\272 mismatch\357\274\232index=%0d NCHW-channel-plane-byte=%0d address=%08h actual=%02h expected=%02h\n",8, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index
                                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index
                                     , '#',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work
                                     , '#',8,(IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__observed_byte_work)
                                     , '#',8,((0x00151fffU 
                                               >= (0x001fffffU 
                                                   & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index))
                                               ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__expected_bytes
                                              [(0x001fffffU 
                                                & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index)]
                                               : 0U));
                        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 464, "", false);
                    }
                    if ((0x01000000U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work)) {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point0_golden_seen = 1U;
                    }
                    if ((0x01000001U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work)) {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point1_golden_seen = 1U;
                    }
                    if ((0x00151fffU >= (0x001fffffU 
                                         & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index))) {
                        __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__output_seen__v0 
                            = (0x001fffffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index);
                        __VdlySet__tb_s2a_t66_layer0_tile__DOT__output_seen__v0 = 1U;
                    }
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__output_write_count 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count);
                    if (VL_UNLIKELY((VL_GTES_III(32, 
                                                 ((IData)(1U) 
                                                  + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count), vlSelfRef.tb_s2a_t66_layer0_tile__DOT__next_progress)))) {
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__next_progress 
                            = ((IData)(0x00030d40U) 
                               + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__next_progress);
                        VL_WRITEF_NX("T66_PROGRESS writes=%0d/1384448 cycles=%0d requests=%0d\n",3
                                     , '~',32,((IData)(1U) 
                                               + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count)
                                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__cycle_count
                                     , '~',32,((IData)(1U) 
                                               + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__request_count));
                    }
                }
                if ((2U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_wstrb))) {
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched);
                    if (VL_UNLIKELY((((0x01000000U 
                                       > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work) 
                                      | (0x01152000U 
                                         <= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work))))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:455: Assertion failed in %m: T66 \345\206\231\350\257\267\346\261\202\350\266\212\347\225\214\357\274\232address=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '#',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work);
                        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 455, "", false);
                    }
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index 
                        = (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work 
                           - (IData)(0x01000000U));
                    if (VL_UNLIKELY((((0x00151fffU 
                                       >= (0x001fffffU 
                                           & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index)) 
                                      && vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_seen
                                      [(0x001fffffU 
                                        & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index)])))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:459: Assertion failed in %m: T66 \351\207\215\345\244\215\345\206\231\350\276\223\345\207\272\345\255\227\350\212\202\357\274\232index=%0d address=%08h\n",5, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index
                                     , '#',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work);
                        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 459, "", false);
                    }
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__observed_byte_work 
                        = (0x000000ffU & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_wdata_latched 
                                          >> 8U));
                    if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__observed_byte_work) 
                                      != ((0x00151fffU 
                                           >= (0x001fffffU 
                                               & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index))
                                           ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__expected_bytes
                                          [(0x001fffffU 
                                            & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index)]
                                           : 0U))))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:464: Assertion failed in %m: T66 \350\276\223\345\207\272 mismatch\357\274\232index=%0d NCHW-channel-plane-byte=%0d address=%08h actual=%02h expected=%02h\n",8, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index
                                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index
                                     , '#',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work
                                     , '#',8,(IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__observed_byte_work)
                                     , '#',8,((0x00151fffU 
                                               >= (0x001fffffU 
                                                   & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index))
                                               ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__expected_bytes
                                              [(0x001fffffU 
                                                & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index)]
                                               : 0U));
                        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 464, "", false);
                    }
                    if ((0x01000000U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work)) {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point0_golden_seen = 1U;
                    }
                    if ((0x01000001U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work)) {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point1_golden_seen = 1U;
                    }
                    if ((0x00151fffU >= (0x001fffffU 
                                         & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index))) {
                        __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__output_seen__v1 
                            = (0x001fffffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index);
                        __VdlySet__tb_s2a_t66_layer0_tile__DOT__output_seen__v1 = 1U;
                    }
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__output_write_count 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count);
                    if (VL_UNLIKELY((VL_GTES_III(32, 
                                                 ((IData)(1U) 
                                                  + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count), vlSelfRef.tb_s2a_t66_layer0_tile__DOT__next_progress)))) {
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__next_progress 
                            = ((IData)(0x00030d40U) 
                               + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__next_progress);
                        VL_WRITEF_NX("T66_PROGRESS writes=%0d/1384448 cycles=%0d requests=%0d\n",3
                                     , '~',32,((IData)(1U) 
                                               + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count)
                                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__cycle_count
                                     , '~',32,((IData)(1U) 
                                               + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__request_count));
                    }
                }
                if ((4U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_wstrb))) {
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work 
                        = ((IData)(2U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched);
                    if (VL_UNLIKELY((((0x01000000U 
                                       > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work) 
                                      | (0x01152000U 
                                         <= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work))))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:455: Assertion failed in %m: T66 \345\206\231\350\257\267\346\261\202\350\266\212\347\225\214\357\274\232address=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '#',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work);
                        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 455, "", false);
                    }
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index 
                        = (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work 
                           - (IData)(0x01000000U));
                    if (VL_UNLIKELY((((0x00151fffU 
                                       >= (0x001fffffU 
                                           & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index)) 
                                      && vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_seen
                                      [(0x001fffffU 
                                        & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index)])))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:459: Assertion failed in %m: T66 \351\207\215\345\244\215\345\206\231\350\276\223\345\207\272\345\255\227\350\212\202\357\274\232index=%0d address=%08h\n",5, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index
                                     , '#',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work);
                        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 459, "", false);
                    }
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__observed_byte_work 
                        = (0x000000ffU & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_wdata_latched 
                                          >> 0x10U));
                    if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__observed_byte_work) 
                                      != ((0x00151fffU 
                                           >= (0x001fffffU 
                                               & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index))
                                           ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__expected_bytes
                                          [(0x001fffffU 
                                            & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index)]
                                           : 0U))))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:464: Assertion failed in %m: T66 \350\276\223\345\207\272 mismatch\357\274\232index=%0d NCHW-channel-plane-byte=%0d address=%08h actual=%02h expected=%02h\n",8, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index
                                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index
                                     , '#',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work
                                     , '#',8,(IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__observed_byte_work)
                                     , '#',8,((0x00151fffU 
                                               >= (0x001fffffU 
                                                   & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index))
                                               ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__expected_bytes
                                              [(0x001fffffU 
                                                & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index)]
                                               : 0U));
                        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 464, "", false);
                    }
                    if ((0x01000000U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work)) {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point0_golden_seen = 1U;
                    }
                    if ((0x01000001U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work)) {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point1_golden_seen = 1U;
                    }
                    if ((0x00151fffU >= (0x001fffffU 
                                         & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index))) {
                        __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__output_seen__v2 
                            = (0x001fffffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index);
                        __VdlySet__tb_s2a_t66_layer0_tile__DOT__output_seen__v2 = 1U;
                    }
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__output_write_count 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count);
                    if (VL_UNLIKELY((VL_GTES_III(32, 
                                                 ((IData)(1U) 
                                                  + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count), vlSelfRef.tb_s2a_t66_layer0_tile__DOT__next_progress)))) {
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__next_progress 
                            = ((IData)(0x00030d40U) 
                               + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__next_progress);
                        VL_WRITEF_NX("T66_PROGRESS writes=%0d/1384448 cycles=%0d requests=%0d\n",3
                                     , '~',32,((IData)(1U) 
                                               + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count)
                                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__cycle_count
                                     , '~',32,((IData)(1U) 
                                               + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__request_count));
                    }
                }
                if ((8U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_wstrb))) {
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work 
                        = ((IData)(3U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched);
                    if (VL_UNLIKELY((((0x01000000U 
                                       > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work) 
                                      | (0x01152000U 
                                         <= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work))))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:455: Assertion failed in %m: T66 \345\206\231\350\257\267\346\261\202\350\266\212\347\225\214\357\274\232address=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '#',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work);
                        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 455, "", false);
                    }
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index 
                        = (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work 
                           - (IData)(0x01000000U));
                    if (VL_UNLIKELY((((0x00151fffU 
                                       >= (0x001fffffU 
                                           & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index)) 
                                      && vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_seen
                                      [(0x001fffffU 
                                        & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index)])))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:459: Assertion failed in %m: T66 \351\207\215\345\244\215\345\206\231\350\276\223\345\207\272\345\255\227\350\212\202\357\274\232index=%0d address=%08h\n",5, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index
                                     , '#',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work);
                        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 459, "", false);
                    }
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__observed_byte_work 
                        = (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_wdata_latched 
                           >> 0x18U);
                    if (VL_UNLIKELY((((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__observed_byte_work) 
                                      != ((0x00151fffU 
                                           >= (0x001fffffU 
                                               & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index))
                                           ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__expected_bytes
                                          [(0x001fffffU 
                                            & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index)]
                                           : 0U))))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:464: Assertion failed in %m: T66 \350\276\223\345\207\272 mismatch\357\274\232index=%0d NCHW-channel-plane-byte=%0d address=%08h actual=%02h expected=%02h\n",8, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index
                                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index
                                     , '#',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work
                                     , '#',8,(IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__observed_byte_work)
                                     , '#',8,((0x00151fffU 
                                               >= (0x001fffffU 
                                                   & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index))
                                               ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__expected_bytes
                                              [(0x001fffffU 
                                                & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index)]
                                               : 0U));
                        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 464, "", false);
                    }
                    if ((0x01000000U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work)) {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point0_golden_seen = 1U;
                    }
                    if ((0x01000001U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work)) {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point1_golden_seen = 1U;
                    }
                    if ((0x00151fffU >= (0x001fffffU 
                                         & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index))) {
                        __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__output_seen__v3 
                            = (0x001fffffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__address_index);
                        __VdlySet__tb_s2a_t66_layer0_tile__DOT__output_seen__v3 = 1U;
                    }
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__output_write_count 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count);
                    if (VL_UNLIKELY((VL_GTES_III(32, 
                                                 ((IData)(1U) 
                                                  + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count), vlSelfRef.tb_s2a_t66_layer0_tile__DOT__next_progress)))) {
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__next_progress 
                            = ((IData)(0x00030d40U) 
                               + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__next_progress);
                        VL_WRITEF_NX("T66_PROGRESS writes=%0d/1384448 cycles=%0d requests=%0d\n",3
                                     , '~',32,((IData)(1U) 
                                               + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count)
                                     , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__cycle_count
                                     , '~',32,((IData)(1U) 
                                               + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__request_count));
                    }
                }
            } else {
                if (VL_UNLIKELY(((((0U != (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_wstrb)) 
                                   | (0U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_rstrb))) 
                                  | (1U != VL_COUNTONES_I((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_rstrb))))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:485: Assertion failed in %m: T66 \350\257\273\350\257\267\346\261\202\346\226\271\345\220\221\346\210\226 strobe \351\224\231\350\257\257\357\274\232r=%b w=%b\n",5, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '#',4,(IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_rstrb)
                                 , '#',4,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_wstrb);
                    VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 485, "", false);
                }
                __Vfunc_tb_s2a_t66_layer0_tile__DOT__strobe_lane_index__9__strobe 
                    = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_rstrb;
                __Vfunc_tb_s2a_t66_layer0_tile__DOT__strobe_lane_index__9__Vfuncout 
                    = Vtb_s2a_t66_layer0_tile__ConstPool__CONST_h24ab78b6_0
                    [(0x07ffffffU & (IData)(__Vfunc_tb_s2a_t66_layer0_tile__DOT__strobe_lane_index__9__strobe))];
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_read_lane_work 
                    = __Vfunc_tb_s2a_t66_layer0_tile__DOT__strobe_lane_index__9__Vfuncout;
                if (VL_UNLIKELY(((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_read_lane_work) 
                                  | ((3U & (0x00030210U 
                                            >> ((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_strobe_latched) 
                                                << 1U))) 
                                     != (3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_read_lane_work)))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:491: Assertion failed in %m: T66 read request lane decode \351\224\231\350\257\257\357\274\232class=%0d strobe=%b lane=%0d decoded=%0d\n",7, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '~',32,tb_s2a_t66_layer0_tile__DOT__transfer_class_work
                                 , '#',4,(IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_rstrb)
                                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_read_lane_work
                                 , '#',2,(3U & (0x00030210U 
                                                >> 
                                                ((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_strobe_latched) 
                                                 << 1U))));
                    VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 491, "", false);
                }
                if ((0U == tb_s2a_t66_layer0_tile__DOT__transfer_class_work)) {
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count__v4 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count
                           [(3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_read_lane_work)]);
                    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count__v4 
                        = (3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_read_lane_work);
                    __VdlySet__tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count__v4 = 1U;
                } else if ((1U == tb_s2a_t66_layer0_tile__DOT__transfer_class_work)) {
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count__v4 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count
                           [(3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_read_lane_work)]);
                    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count__v4 
                        = (3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_read_lane_work);
                    __VdlySet__tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count__v4 = 1U;
                }
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_word_work = 0U;
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_error_work = 0U;
                if ((1U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_rstrb))) {
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work 
                        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched;
                    if ((0x0007ec00U > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work)) {
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__input_read_count 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__input_read_count);
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_word_work 
                            = ((0xffffff00U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_word_work) 
                               | ((0x0007ebffU >= (0x0007ffffU 
                                                   & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work))
                                   ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__input_bytes
                                  [(0x0007ffffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work)]
                                   : 0U));
                    } else if (VL_LIKELY((((0x0010013cU 
                                            <= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work) 
                                           & (0x0010049cU 
                                              > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work))))) {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_byte_index 
                            = ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work 
                                - (IData)(0x00100000U)) 
                               - (IData)(0x0000013cU));
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__weight_read_count 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_read_count);
                        if ((0x035fU >= (0x000003ffU 
                                         & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_byte_index))) {
                            __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_seen__v1 
                                = (0x000003ffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_byte_index);
                            vlSelfRef.__VdlyCommitQueuetb_s2a_t66_layer0_tile__DOT__weight_seen.enqueue(1U, (IData)(__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_seen__v1));
                        }
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_word_work 
                            = ((0xffffff00U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_word_work) 
                               | ((0x035fU >= (0x000003ffU 
                                               & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_byte_index))
                                   ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_bytes
                                  [(0x000003ffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_byte_index)]
                                   : 0U));
                    } else {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_error_work = 2U;
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:522: Assertion failed in %m: T66 \350\257\273\350\257\267\346\261\202\350\266\212\347\225\214\357\274\232address=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '#',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work);
                        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 522, "", false);
                    }
                }
                if ((2U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_rstrb))) {
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched);
                    if ((0x0007ec00U > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work)) {
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__input_read_count 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__input_read_count);
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_word_work 
                            = ((0xffff00ffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_word_work) 
                               | (((0x0007ebffU >= 
                                    (0x0007ffffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work))
                                    ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__input_bytes
                                   [(0x0007ffffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work)]
                                    : 0U) << 8U));
                    } else if (VL_LIKELY((((0x0010013cU 
                                            <= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work) 
                                           & (0x0010049cU 
                                              > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work))))) {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_byte_index 
                            = ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work 
                                - (IData)(0x00100000U)) 
                               - (IData)(0x0000013cU));
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__weight_read_count 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_read_count);
                        if ((0x035fU >= (0x000003ffU 
                                         & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_byte_index))) {
                            __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_seen__v2 
                                = (0x000003ffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_byte_index);
                            vlSelfRef.__VdlyCommitQueuetb_s2a_t66_layer0_tile__DOT__weight_seen.enqueue(1U, (IData)(__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_seen__v2));
                        }
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_word_work 
                            = ((0xffff00ffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_word_work) 
                               | (((0x035fU >= (0x000003ffU 
                                                & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_byte_index))
                                    ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_bytes
                                   [(0x000003ffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_byte_index)]
                                    : 0U) << 8U));
                    } else {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_error_work = 2U;
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:522: Assertion failed in %m: T66 \350\257\273\350\257\267\346\261\202\350\266\212\347\225\214\357\274\232address=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '#',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work);
                        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 522, "", false);
                    }
                }
                if ((4U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_rstrb))) {
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work 
                        = ((IData)(2U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched);
                    if ((0x0007ec00U > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work)) {
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__input_read_count 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__input_read_count);
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_word_work 
                            = ((0xff00ffffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_word_work) 
                               | (((0x0007ebffU >= 
                                    (0x0007ffffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work))
                                    ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__input_bytes
                                   [(0x0007ffffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work)]
                                    : 0U) << 0x00000010U));
                    } else if (VL_LIKELY((((0x0010013cU 
                                            <= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work) 
                                           & (0x0010049cU 
                                              > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work))))) {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_byte_index 
                            = ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work 
                                - (IData)(0x00100000U)) 
                               - (IData)(0x0000013cU));
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__weight_read_count 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_read_count);
                        if ((0x035fU >= (0x000003ffU 
                                         & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_byte_index))) {
                            __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_seen__v3 
                                = (0x000003ffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_byte_index);
                            vlSelfRef.__VdlyCommitQueuetb_s2a_t66_layer0_tile__DOT__weight_seen.enqueue(1U, (IData)(__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_seen__v3));
                        }
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_word_work 
                            = ((0xff00ffffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_word_work) 
                               | (((0x035fU >= (0x000003ffU 
                                                & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_byte_index))
                                    ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_bytes
                                   [(0x000003ffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_byte_index)]
                                    : 0U) << 0x00000010U));
                    } else {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_error_work = 2U;
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:522: Assertion failed in %m: T66 \350\257\273\350\257\267\346\261\202\350\266\212\347\225\214\357\274\232address=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '#',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work);
                        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 522, "", false);
                    }
                }
                if ((8U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_rstrb))) {
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work 
                        = ((IData)(3U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched);
                    if ((0x0007ec00U > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work)) {
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__input_read_count 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__input_read_count);
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_word_work 
                            = ((0x00ffffffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_word_work) 
                               | (((0x0007ebffU >= 
                                    (0x0007ffffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work))
                                    ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__input_bytes
                                   [(0x0007ffffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work)]
                                    : 0U) << 0x00000018U));
                    } else if (VL_LIKELY((((0x0010013cU 
                                            <= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work) 
                                           & (0x0010049cU 
                                              > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work))))) {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_byte_index 
                            = ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work 
                                - (IData)(0x00100000U)) 
                               - (IData)(0x0000013cU));
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__weight_read_count 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_read_count);
                        if ((0x035fU >= (0x000003ffU 
                                         & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_byte_index))) {
                            __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_seen__v4 
                                = (0x000003ffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_byte_index);
                            vlSelfRef.__VdlyCommitQueuetb_s2a_t66_layer0_tile__DOT__weight_seen.enqueue(1U, (IData)(__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_seen__v4));
                        }
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_word_work 
                            = ((0x00ffffffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_word_work) 
                               | (((0x035fU >= (0x000003ffU 
                                                & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_byte_index))
                                    ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_bytes
                                   [(0x000003ffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_byte_index)]
                                    : 0U) << 0x00000018U));
                    } else {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_error_work = 2U;
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:522: Assertion failed in %m: T66 \350\257\273\350\257\267\346\261\202\350\266\212\347\225\214\357\274\232address=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000)
                                     , '#',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work);
                        VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 522, "", false);
                    }
                }
                __Vdly__tb_s2a_t66_layer0_tile__DOT__response_data 
                    = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_word_work;
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_error 
                    = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__read_error_work;
            }
        } else if ((((0U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_request) 
                     & (~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_ready))) 
                    & VL_LTS_III(32, 0U, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__stall_remaining))) {
            __Vdly__tb_s2a_t66_layer0_tile__DOT__stall_remaining 
                = (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__stall_remaining 
                   - (IData)(1U));
        }
        if (((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__memory_pending) 
             & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_rsp_valid))) {
            __Vdly__tb_s2a_t66_layer0_tile__DOT__response_count 
                = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_count);
            if (VL_UNLIKELY((VL_GTS_III(32, 0U, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__pending_transfer_class)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:535: Assertion failed in %m: T66 \345\223\215\345\272\224\347\274\272\345\260\221\346\234\211\346\225\210\347\232\204 transfer class\n",3, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 535, "", false);
            }
            if ((2U >= (3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__pending_transfer_class))) {
                __Vfunc_tb_s2a_t66_layer0_tile__DOT__response_stall_cycles__10__index 
                    = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count
                    [(3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__pending_transfer_class)];
                __VdlyVal__tb_s2a_t66_layer0_tile__DOT__class_response_count__v3 
                    = ((IData)(1U) + ((2U >= (3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__pending_transfer_class))
                                       ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count
                                      [(3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__pending_transfer_class)]
                                       : 0U));
                __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__class_response_count__v3 
                    = (3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__pending_transfer_class);
                __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_response_count__v3 = 1U;
            } else {
                __Vfunc_tb_s2a_t66_layer0_tile__DOT__response_stall_cycles__10__index = 0U;
            }
            __Vdly__tb_s2a_t66_layer0_tile__DOT__memory_pending = 0U;
            __Vtemp_5 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__response_stall_cycles__10__index, (IData)(5U)), Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hb4617e49_0);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_4__response_stall_cycles 
                = Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_hc6a14c36_0
                [__Vtemp_5];
            if (VL_UNLIKELY(((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__active_response_stall_observed 
                              != vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_4__response_stall_cycles)))) {
                __Vfunc_tb_s2a_t66_layer0_tile__DOT__response_stall_cycles__11__index 
                    = ((2U >= (3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__pending_transfer_class))
                        ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count
                       [(3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__pending_transfer_class)]
                        : 0U);
                __Vtemp_6 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, __Vfunc_tb_s2a_t66_layer0_tile__DOT__response_stall_cycles__11__index, (IData)(5U)), Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hb4617e49_0);
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_5__response_stall_cycles 
                    = Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_hc6a14c36_0
                    [__Vtemp_6];
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:538: Assertion failed in %m: T66 response stall \345\272\217\345\210\227\351\224\231\350\257\257\357\274\232class=%0d index=%0d expected=%0d actual=%0d\n",7, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__pending_transfer_class
                             , '~',32,((2U >= (3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__pending_transfer_class))
                                        ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count
                                       [(3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__pending_transfer_class)]
                                        : 0U), '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_5__response_stall_cycles
                             , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__active_response_stall_observed);
                VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 538, "", false);
            }
            __Vdly__tb_s2a_t66_layer0_tile__DOT__active_response_stall_observed = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__pending_transfer_class = 0xffffffffU;
        } else if (((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__memory_pending) 
                    & VL_LTS_III(32, 0U, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_delay_remaining))) {
            __Vdly__tb_s2a_t66_layer0_tile__DOT__response_delay_remaining 
                = (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_delay_remaining 
                   - (IData)(1U));
            __Vdly__tb_s2a_t66_layer0_tile__DOT__response_stall_cycle_count 
                = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_stall_cycle_count);
            if ((2U >= (3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__pending_transfer_class))) {
                __VdlyVal__tb_s2a_t66_layer0_tile__DOT__class_response_stall_count__v3 
                    = ((IData)(1U) + ((2U >= (3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__pending_transfer_class))
                                       ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_stall_count
                                      [(3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__pending_transfer_class)]
                                       : 0U));
                __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__class_response_stall_count__v3 
                    = (3U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__pending_transfer_class);
                __VdlySet__tb_s2a_t66_layer0_tile__DOT__class_response_stall_count__v3 = 1U;
            }
            __Vdly__tb_s2a_t66_layer0_tile__DOT__active_response_stall_observed 
                = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__active_response_stall_observed);
        }
    }
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__request_count 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__request_count;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_count 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__response_count;
    vlSelfRef.__VdlyCommitQueuetb_s2a_t66_layer0_tile__DOT__weight_seen.commit(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_seen);
    if (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__hard_reset) {
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_layer_index_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_base_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_length_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_batch_count_latched = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_channels_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_height_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_width_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_base_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_length_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_batch_count_latched = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_y_latched = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_x_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__pad_left_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__pad_right_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__pad_top_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__pad_bottom_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__groups_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__padding_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_base_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_length_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__quantized_weight_offset_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__quantized_weight_bytes_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_batch_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__activation_mode_latched = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_height = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_width = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_height = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_width = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_byte_count = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_point_count = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_channel = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_y = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_x = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_lane_index = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_reduction_index = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_index = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_channel = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_y = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_x = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_lane_index = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_index = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_y = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_x = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_lane = 0U;
        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_lane_index = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_strobe_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_wdata_latched = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched = 0U;
        __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v0 = 1U;
    } else {
        if (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_advance) {
            if ((((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_x) 
                 >= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_width)) {
                if ((((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_y) 
                     >= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_height)) {
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_channel 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_channel);
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_y = 0U;
                } else {
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_y 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_y);
                }
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_x = 0U;
            } else {
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_x 
                    = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_x);
            }
        }
        if ((0x00000010U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
            if ((8U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched = 6U;
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x13U;
            } else if ((4U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched = 6U;
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x13U;
            } else if ((2U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
                    if (((0x13U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state)) 
                         & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__result_ready))) {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched = 0U;
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0U;
                    }
                } else if ((((IData)(8U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base) 
                            < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched)) {
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base 
                        = ((IData)(8U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base);
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 6U;
                } else if (((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x 
                             + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_width) 
                            < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched)) {
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x 
                        = ((IData)(8U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x);
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base = 0U;
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 2U;
                } else if (((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y 
                             + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_height) 
                            < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched)) {
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y 
                        = ((IData)(8U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y);
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base = 0U;
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x = 0U;
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 2U;
                } else {
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched = 0U;
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x13U;
                }
            } else if ((1U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
                if (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_rsp_valid) {
                    if ((0U != (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mapped_response_error))) {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched 
                            = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mapped_response_error;
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x13U;
                    } else {
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_index);
                        if ((((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_x) 
                             >= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_width)) {
                            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_y 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_y);
                            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_x = 0U;
                        } else {
                            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_x 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_x);
                        }
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x0fU;
                    }
                }
            } else if (((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_valid) 
                        & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_ready))) {
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x11U;
            }
        } else if ((8U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
            if ((4U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
                if ((2U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
                    if ((1U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
                        if ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_lane_index 
                             >= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x12U;
                        } else if ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_index 
                                    >= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_point_count)) {
                            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_lane_index 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_lane_index);
                            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_index = 0U;
                            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_y = 0U;
                            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_x = 0U;
                        } else {
                            __Vtemp_7[0U] = (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_byte_offset_wide);
                            __Vtemp_7[1U] = (IData)(
                                                    (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_byte_offset_wide 
                                                     >> 0x00000020U));
                            __Vtemp_7[2U] = 0U;
                            __Vtemp_7[3U] = 0U;
                            if (((0x00000000ffffffffULL 
                                  < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_address_wide) 
                                 | VL_GTE_W(4, __Vtemp_7, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_elements_wide))) {
                                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched = 2U;
                                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x13U;
                            } else {
                                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched 
                                    = ((IData)((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_address_wide 
                                                >> 2U)) 
                                       << 2U);
                                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_strobe_latched 
                                    = (0x0000000fU 
                                       & ((IData)(1U) 
                                          << (3U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_address_wide))));
                                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_wdata_latched 
                                    = VL_SHIFTL_III(32,32,32, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_block
                                                    [
                                                    (0x000001ffU 
                                                     & ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_lane_index 
                                                         << 6U) 
                                                        + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_index))], 
                                                    (0x00000018U 
                                                     & ((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_address_wide) 
                                                        << 3U)));
                                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x10U;
                            }
                        }
                    } else {
                        if ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_lane_index 
                             < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_block__v0 
                                = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requantized_value;
                            __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_block__v0 
                                = (0x000001ffU & ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_lane_index 
                                                   << 6U) 
                                                  + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_index));
                            __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_block__v0 = 1U;
                        }
                        if ((((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_lane_index) 
                             >= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                            if ((((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_index) 
                                 >= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_point_count)) {
                                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_lane_index = 0U;
                                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_index = 0U;
                                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_y = 0U;
                                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_x = 0U;
                                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x0fU;
                            } else {
                                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_index 
                                    = ((IData)(1U) 
                                       + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_index);
                                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index = 0U;
                                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x0cU;
                            }
                        } else {
                            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_lane_index 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_lane_index);
                        }
                    }
                } else if ((1U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
                    if (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_bad_argument) {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched = 1U;
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x13U;
                    } else if (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_overflow) {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched = 7U;
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x13U;
                    } else {
                        if ((0U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v0 
                                = (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[0U]);
                            __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v0 = 1U;
                        }
                        if ((((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index) 
                             >= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched)) {
                            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_lane_index = 0U;
                            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x0eU;
                        } else {
                            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index 
                                = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index);
                            if ((((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_x) 
                                 >= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched)) {
                                if ((((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_y) 
                                     >= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched)) {
                                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_channel 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_channel);
                                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_y = 0U;
                                } else {
                                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_y 
                                        = ((IData)(1U) 
                                           + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_y);
                                }
                                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_x = 0U;
                            } else {
                                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_x 
                                    = ((IData)(1U) 
                                       + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_x);
                            }
                        }
                        if ((1U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v1 
                                = (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[1U]);
                            __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v1 = 1U;
                        }
                        if ((2U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v2 
                                = (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[2U]);
                            __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v2 = 1U;
                        }
                        if ((3U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v3 
                                = (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[3U]);
                            __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v3 = 1U;
                        }
                        if ((4U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v4 
                                = (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[4U]);
                            __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v4 = 1U;
                        }
                        if ((5U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v5 
                                = (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[5U]);
                            __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v5 = 1U;
                        }
                        if ((6U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v6 
                                = (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[6U]);
                            __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v6 = 1U;
                        }
                        if ((7U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                            __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v7 
                                = (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[7U]);
                            __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v7 = 1U;
                        }
                    }
                } else {
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_channel = 0U;
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_y = 0U;
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_x = 0U;
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v8 
                        = ((0U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[0U]
                            : 0U);
                    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v8 = 1U;
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index = 0U;
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x0dU;
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v9 
                        = ((1U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[1U]
                            : 0U);
                    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v9 = 1U;
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v10 
                        = ((2U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[2U]
                            : 0U);
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v11 
                        = ((3U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[3U]
                            : 0U);
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v12 
                        = ((4U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[4U]
                            : 0U);
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v13 
                        = ((5U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[5U]
                            : 0U);
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v14 
                        = ((6U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[6U]
                            : 0U);
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v15 
                        = ((7U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[7U]
                            : 0U);
                }
            } else if ((2U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_channel = 0U;
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_y = 0U;
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_x = 0U;
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v16 
                        = ((0U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[0U]
                            : 0U);
                    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v16 = 1U;
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_index = 0U;
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index = 0U;
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x0dU;
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v17 
                        = ((1U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[1U]
                            : 0U);
                    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v17 = 1U;
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v18 
                        = ((2U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[2U]
                            : 0U);
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v19 
                        = ((3U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[3U]
                            : 0U);
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v20 
                        = ((4U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[4U]
                            : 0U);
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v21 
                        = ((5U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[5U]
                            : 0U);
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v22 
                        = ((6U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[6U]
                            : 0U);
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v23 
                        = ((7U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)
                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[7U]
                            : 0U);
                } else if (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_invalid) {
                    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched = 1U;
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x13U;
                } else {
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v8[0U] 
                        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[0U];
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v8[1U] 
                        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[1U];
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v8[2U] 
                        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[2U];
                    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v8 
                        = (7U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_lane);
                    __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v8 = 1U;
                    __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias__v8 
                        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_bias;
                    __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias__v8 
                        = (7U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_lane);
                    if ((((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_lane) 
                         >= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x0bU;
                    } else {
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_lane 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_lane);
                    }
                }
            } else if ((1U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
                if (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_rsp_valid) {
                    if ((0U != (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mapped_response_error))) {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched 
                            = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mapped_response_error;
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x13U;
                    } else {
                        if ((0x8fffU >= (0x0000ffffU 
                                         & ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_lane_index 
                                             * vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched) 
                                            + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_reduction_index)))) {
                            __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group__v0 
                                = (0x000000ffU & VL_SHIFTR_III(8,32,32, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_data, 
                                                               ((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_byte_lane) 
                                                                << 3U)));
                            __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group__v0 
                                = (0x0000ffffU & ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_lane_index 
                                                   * vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched) 
                                                  + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_reduction_index));
                            __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group__v0 = 1U;
                        }
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 7U;
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_reduction_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_reduction_index);
                    }
                }
            } else if (((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_valid) 
                        & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_ready))) {
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 9U;
            }
        } else if ((4U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
            if ((2U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
                if ((1U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
                    if ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_lane_index 
                         >= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_lane = 0U;
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x0aU;
                    } else if ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_reduction_index 
                                >= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched)) {
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_lane_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_lane_index);
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_reduction_index = 0U;
                    } else if ((0x00000000ffffffffULL 
                                < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_source_address_wide)) {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched = 2U;
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x13U;
                    } else {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched 
                            = ((IData)((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_source_address_wide 
                                        >> 2U)) << 2U);
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_strobe_latched 
                            = (0x0000000fU & ((IData)(1U) 
                                              << (3U 
                                                  & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_source_address_wide))));
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_wdata_latched = 0U;
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 8U;
                    }
                } else if ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base 
                            >= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched)) {
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x12U;
                } else {
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count 
                        = ((8U <= (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched 
                                   - vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base))
                            ? 8U : (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched 
                                    - vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base));
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_lane_index = 0U;
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_reduction_index = 0U;
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_lane = 0U;
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 7U;
                }
            } else if ((1U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
                if (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_rsp_valid) {
                    if ((0U != (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mapped_response_error))) {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched 
                            = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mapped_response_error;
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x13U;
                    } else {
                        if ((0xc7ffU >= (0x0000ffffU 
                                         & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index))) {
                            __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v0 
                                = (0x000000ffU & VL_SHIFTR_III(8,32,32, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_data, 
                                                               ((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_byte_lane) 
                                                                << 3U)));
                            __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v0 
                                = (0x0000ffffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index);
                            __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v0 = 1U;
                        }
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 3U;
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index 
                            = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index);
                    }
                }
            } else if (((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_valid) 
                        & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_ready))) {
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 5U;
            }
        } else if ((2U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
            if ((1U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
                if ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index 
                     >= vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_byte_count)) {
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base = 0U;
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 6U;
                } else if (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_in_bounds) {
                    if ((0x00000000ffffffffULL < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_source_address_wide)) {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched = 2U;
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x13U;
                    } else {
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched 
                            = ((IData)((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_source_address_wide 
                                        >> 2U)) << 2U);
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_strobe_latched 
                            = (0x0000000fU & ((IData)(1U) 
                                              << (3U 
                                                  & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_source_address_wide))));
                        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_wdata_latched = 0U;
                        __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 4U;
                    }
                } else {
                    if ((0xc7ffU >= (0x0000ffffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index))) {
                        __VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v1 
                            = (0x0000ffffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index);
                        __VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v1 = 1U;
                    }
                    __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index 
                        = ((IData)(1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index);
                }
            } else {
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_height 
                    = ((8U <= (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched 
                               - vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y))
                        ? 8U : (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched 
                                - vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y));
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_channel = 0U;
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_y = 0U;
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_x = 0U;
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index = 0U;
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 3U;
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_width 
                    = ((8U <= (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched 
                               - vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x))
                        ? 8U : (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched 
                                - vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x));
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_height 
                    = (((((8U <= (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched 
                                  - vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y))
                           ? 8U : (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched 
                                   - vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y)) 
                         - (IData)(1U)) * vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_y_latched) 
                       + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched);
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_width 
                    = (((((8U <= (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched 
                                  - vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x))
                           ? 8U : (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched 
                                   - vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x)) 
                         - (IData)(1U)) * vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_x_latched) 
                       + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched);
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_byte_count 
                    = (((((((8U <= (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched 
                                    - vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y))
                             ? 8U : (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched 
                                     - vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y)) 
                           - (IData)(1U)) * vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_y_latched) 
                         + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched) 
                        * (((((8U <= (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched 
                                      - vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x))
                               ? 8U : (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched 
                                       - vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x)) 
                             - (IData)(1U)) * vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_x_latched) 
                           + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched)) 
                       * vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_channels_latched);
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_point_count 
                    = (((8U <= (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched 
                                - vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y))
                         ? 8U : (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched 
                                 - vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y)) 
                       * ((8U <= (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched 
                                  - vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x))
                           ? 8U : (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched 
                                   - vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x)));
            }
        } else if ((1U & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) {
            if (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__validation_ok) {
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched 
                    = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_wide[0U];
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 2U;
            } else {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched 
                    = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__validation_error;
                __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 0x13U;
            }
        } else if (((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__start_valid) 
                    & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__start_ready))) {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_layer_index_latched = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_base_latched = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_length_latched = 0x0007ec00U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_batch_count_latched = 1U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_channels_latched = 3U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_height_latched = 0x000001a0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_width_latched = 0x000001a0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_base_latched = 0x01000000U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_length_latched = 0x00152000U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_batch_count_latched = 1U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched = 0x00000020U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched = 0x000000d0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched = 0x000000d0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched = 3U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched = 3U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_y_latched = 2U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_x_latched = 2U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__pad_left_latched = 1U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__pad_right_latched = 1U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__pad_top_latched = 1U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__pad_bottom_latched = 1U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__groups_latched = 1U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__padding_latched = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_base_latched = 0x00100000U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_length_latched = 0x005a12fcU;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__quantized_weight_offset_latched = 0x0000013cU;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__quantized_weight_bytes_latched = 0x00000360U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_batch_latched = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__activation_mode_latched = 1U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_channel = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_y = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_x = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_lane_index = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_reduction_index = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_index = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_channel = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_y = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_x = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_lane_index = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_index = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_y = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_x = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched = 0U;
            __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = 1U;
        }
    }
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__pending_transfer_class 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__pending_transfer_class;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__active_request_stall_observed 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__active_request_stall_observed;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__active_response_stall_observed 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__active_response_stall_observed;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__output_write_count;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__input_read_count 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__input_read_count;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_read_count 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__weight_read_count;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__stall_cycle_count 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__stall_cycle_count;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_stall_cycle_count 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__response_stall_cycle_count;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__cycle_count 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__cycle_count;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__next_cycle_progress 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__next_cycle_progress;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__result_count 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__result_count;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__next_progress 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__next_progress;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_write 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__held_write;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_address 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__held_address;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_wdata 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__held_wdata;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_rstrb 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__held_rstrb;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_wstrb 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__held_wstrb;
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__output_seen__v0) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_seen[__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__output_seen__v0] = 1U;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__output_seen__v1) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_seen[__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__output_seen__v1] = 1U;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__output_seen__v2) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_seen[__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__output_seen__v2] = 1U;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__output_seen__v3) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_seen[__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__output_seen__v3] = 1U;
    }
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_request 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__held_request;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__stall_remaining 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__stall_remaining;
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__class_request_count__v0) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count[0U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_stall_count[0U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_stall_count[0U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count[0U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count[0U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[0U] = 0U;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__class_request_count__v1) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count[1U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count[2U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_stall_count[1U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_stall_count[2U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_stall_count[1U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_stall_count[2U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count[1U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count[2U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count[3U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count[1U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count[2U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count[3U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[1U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[2U] = 0U;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__class_response_count__v3) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_count[__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__class_response_count__v3] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__class_response_count__v3;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__class_request_stall_count__v3) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_stall_count[__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__class_request_stall_count__v3] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__class_request_stall_count__v3;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__class_response_stall_count__v3) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_response_stall_count[__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__class_response_stall_count__v3] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__class_response_stall_count__v3;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count__v4) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count[__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count__v4] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count__v4;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count__v4) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count[__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count__v4] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count__v4;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__class_request_count__v3) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__class_request_count[__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__class_request_count__v3] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__class_request_count__v3;
    }
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_delay_remaining 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__response_delay_remaining;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__memory_pending 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__memory_pending;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_data 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__response_data;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_height 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_height;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_point_count 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_point_count;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_index 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_index;
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_block__v0) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_block[__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_block__v0] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_block__v0;
    }
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_lane_index 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_lane_index;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_reduction_index 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_reduction_index;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_lane_index 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_lane_index;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_y 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_y;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_x 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_x;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_lane 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_lane;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_lane_index 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_lane_index;
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v0) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[0U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[1U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[2U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[3U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[4U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[5U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[6U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[7U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[0U][0U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[0U][1U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[0U][2U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[1U][0U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[1U][1U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[1U][2U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[2U][0U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[2U][1U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[2U][2U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[3U][0U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[3U][1U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[3U][2U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[4U][0U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[4U][1U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[4U][2U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[5U][0U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[5U][1U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[5U][2U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[6U][0U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[6U][1U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[6U][2U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[7U][0U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[7U][1U] = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[7U][2U] = 0U;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v8) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias__v8] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias__v8;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v8][0U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v8[0U];
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v8][1U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v8[1U];
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v8][2U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter__v8[2U];
    }
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_width 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_width;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_height 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_height;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_width 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_width;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_byte_count 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_byte_count;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_channel 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_channel;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_y 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_y;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_x 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_x;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_channel 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_channel;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_y 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_y;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_x 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_x;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_index 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_index;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__memory_pending) 
           & (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_delay_remaining));
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_channels_latched 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_channels_latched;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched;
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group__v0) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group[__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group__v0] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group__v0;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v0) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch[__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v0] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v0;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v1) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch[__VdlyDim0__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch__v1] = 0U;
    }
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count;
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v0) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[0U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v0;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v1) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[1U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v1;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v2) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[2U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v2;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v3) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[3U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v3;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v4) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[4U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v4;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v5) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[5U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v5;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v6) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[6U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v6;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v7) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[7U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v7;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v8) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[0U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v8;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v9) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[1U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v9;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[2U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v10;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[3U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v11;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[4U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v12;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[5U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v13;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[6U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v14;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[7U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v15;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v16) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[0U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v16;
    }
    if (__VdlySet__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v17) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[1U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v17;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[2U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v18;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[3U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v19;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[4U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v20;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[5U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v21;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[6U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v22;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[7U] 
            = __VdlyVal__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator__v23;
    }
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_y_latched 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_y_latched;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_x_latched 
        = __Vdly__tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_x_latched;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_byte_lane 
        = (3U & (0x00030210U >> ((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_strobe_latched) 
                                 << 1U)));
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_source_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_base_latched)) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__quantized_weight_offset_latched)) 
              + ((QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_reduction_index)) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_lane_index)))))));
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_byte_offset_wide 
        = ((QData)((IData)((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x 
                            + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_x))) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched)) 
              * ((QData)((IData)((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y 
                                  + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_y))) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_lane_index)))))));
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_index = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[0U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[1U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[2U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_bias = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_invalid = 0U;
    if (((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_lane 
          < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count) 
         & (0x00000026U > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched))) {
        tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_index 
            = ((((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched))
                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                 [(0x0000003fU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched)]
                  : 0U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base) 
               + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_lane);
        if ((0x00000c5cU > tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_index)) {
            if ((0x0c5bU >= (0x00000fffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_index))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[0U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_index)][0U];
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_index)][1U];
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[2U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_index)][2U];
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_bias 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                    [(0x00000fffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_index)];
            } else {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[0U] = 0U;
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[1U] = 0U;
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[2U] = 0U;
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_bias = 0U;
            }
            if (((((((((tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_index 
                        >= (((0x25U >= (0x0000003fU 
                                        & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched))
                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                             [(0x0000003fU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched)]
                              : 0U) + ((0x25U >= (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched))
                                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                       [(0x0000003fU 
                                         & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched)]
                                        : 0U))) | (0U 
                                                   == 
                                                   ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[2U] 
                                                     << 0x00000010U) 
                                                    | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                                       >> 0x00000010U)))) 
                      | (0U == ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                 << 0x00000018U) | 
                                (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[0U] 
                                 >> 8U)))) | (0x3fffffffU 
                                              < ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[2U] 
                                                  << 0x00000010U) 
                                                 | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                                    >> 0x00000010U)))) 
                    | (0x3fffffffU < ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                       << 0x00000018U) 
                                      | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[0U] 
                                         >> 8U)))) 
                   | (0x2fU < (0x000000ffU & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                              >> 8U)))) 
                  | (0x2fU < (0x000000ffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[0U]))) 
                 | ((0U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__activation_mode_latched)) 
                    & ((((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[2U] 
                          << 0x00000010U) | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                             >> 0x00000010U)) 
                        != ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                             << 0x00000018U) | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[0U] 
                                                >> 8U))) 
                       | ((0x000000ffU & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                          >> 8U)) != 
                          (0x000000ffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter[0U])))))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_invalid = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_invalid = 1U;
        }
    } else if ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_lane 
                < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_invalid = 1U;
    }
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_parameter[0U] = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_parameter[1U] = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_parameter[2U] = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_accumulator = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_multiplier = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_q_shift = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_magnitude = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_product = 0ULL;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_rounding_add = 0ULL;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_rounded_magnitude = 0ULL;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_signed_value = 0ULL;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requantized_value = 0U;
    if (((8U > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_lane_index) 
         & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_lane_index 
            < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count))) {
        tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_parameter[0U] 
            = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_lane_index)][0U];
        tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_parameter[1U] 
            = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_lane_index)][1U];
        tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_parameter[2U] 
            = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_lane_index)][2U];
        tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_accumulator 
            = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator
            [(7U & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_lane_index)];
        if ((tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_accumulator 
             >> 0x1fU)) {
            tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_multiplier 
                = ((tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_parameter[1U] 
                    << 0x00000018U) | (tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_parameter[0U] 
                                       >> 8U));
            tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_magnitude 
                = ((IData)(1U) + (~ tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_accumulator));
            tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_q_shift 
                = (0x000000ffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_parameter[0U]);
        } else {
            tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_multiplier 
                = ((tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_parameter[2U] 
                    << 0x00000010U) | (tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_parameter[1U] 
                                       >> 0x00000010U));
            tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_magnitude 
                = tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_accumulator;
            tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_q_shift 
                = (0x000000ffU & (tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_parameter[1U] 
                                  >> 8U));
        }
        tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_product 
            = ((QData)((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_magnitude)) 
               * (QData)((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_multiplier)));
        if ((0U != tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_q_shift)) {
            tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_rounding_add 
                = VL_SHIFTL_QQI(64,64,32, 1ULL, (tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_q_shift 
                                                 - (IData)(1U)));
        }
        tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_rounded_magnitude 
            = VL_SHIFTR_QQI(64,64,32, (tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_product 
                                       + tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_rounding_add), tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_q_shift);
        __Vtemp_17[0U] = (IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_rounded_magnitude);
        __Vtemp_17[1U] = (IData)((tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_rounded_magnitude 
                                  >> 0x00000020U));
        __Vtemp_17[2U] = 0U;
        VL_NEGATE_W(3, __Vtemp_18, __Vtemp_17);
        tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_signed_value 
            = ((tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_accumulator 
                >> 0x1fU) ? (((QData)((IData)(__Vtemp_18[1U])) 
                              << 0x00000020U) | (QData)((IData)(__Vtemp_18[0U])))
                : tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_rounded_magnitude);
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requantized_value 
            = (VL_LTS_IQQ(64, 0x000000000000007fULL, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_signed_value)
                ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_signed_value)
                                  ? 0x00000081U : (0x000000ffU 
                                                   & (IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_signed_value))));
    }
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_plane_bytes 
        = ((QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_height)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_width)));
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_input_y = 0ULL;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_input_x = 0ULL;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_in_bounds = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_advance = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_source_offset = 0ULL;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_source_address_wide = 0ULL;
    if (((0ULL != tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_plane_bytes) 
         & (0U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_width))) {
        tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_input_y 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_y_latched))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__pad_top_latched)));
        tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_input_x 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_x_latched))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_input_y, (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_input_x, (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_width_latched))));
        if (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_in_bounds) {
            tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_source_offset 
                = (((((QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_channel)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_height_latched))) 
                     + tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_input_y) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_width_latched))) 
                   + tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_input_x);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_source_address_wide 
                = ((QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_base_latched)) 
                   + tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_source_offset);
        }
    }
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_area 
        = (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched 
           * vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched);
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_y = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_x = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_y = 0ULL;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_x = 0ULL;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_tap_in_bounds = 0U;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index_wide = 0ULL;
    tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_bad_argument = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_overflow = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[0U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[0U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[0U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[0U] = 0ULL;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[1U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[1U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[1U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[1U] = 0ULL;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[2U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[2U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[2U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[2U] = 0ULL;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[3U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[3U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[3U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[3U] = 0ULL;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[4U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[4U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[4U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[4U] = 0ULL;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[5U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[5U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[5U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[5U] = 0ULL;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[6U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[6U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[6U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[6U] = 0ULL;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[7U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[7U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[7U] = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[7U] = 0ULL;
    if (((0U != tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_area) 
         & (0U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_width))) {
        tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_y 
            = VL_DIV_III(32, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_index, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_width);
        tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_x 
            = VL_MODDIV_III(32, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_index, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_width);
        tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_y 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_y_latched))) 
                 + ((QData)((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_y)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_y_latched)))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__pad_top_latched)));
        tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_x 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_x_latched))) 
                 + ((QData)((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_x)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_x_latched)))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__pad_left_latched)));
        tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_tap_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_y, (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_x, (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_width_latched))));
        tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index_wide 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_channel)) 
                  * tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_plane_bytes) 
                 + ((((QData)((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_y)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_y_latched))) 
                     + (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_y))) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_width)))) 
                + ((QData)((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_x)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_x_latched)))) 
               + (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_x)));
        tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index 
            = (IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index_wide);
        if ((0U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[0U] 
                = ((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[0U] 
                = ((0x8fffU >= (0x0000ffffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index))
                    ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group
                   [(0x0000ffffU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index)]
                    : 0U);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[0U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[0U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[0U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[0U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[0U])));
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[0U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[0U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[0U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[0U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[0U])))));
            if (((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[0U]) 
                    | (0x80U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[0U])))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[0U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[0U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[0U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[0U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[0U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[0U] = 0ULL;
        }
        if ((1U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[1U] 
                = ((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[1U] 
                = ((0x8fffU >= (0x0000ffffU & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched 
                                               + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group
                   [(0x0000ffffU & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched 
                                    + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[1U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[1U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[1U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[1U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[1U])));
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[1U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[1U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[1U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[1U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[1U])))));
            if (((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[1U]) 
                    | (0x80U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[1U])))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[1U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[1U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[1U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[1U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[1U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[1U] = 0ULL;
        }
        if ((2U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[2U] 
                = ((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[2U] 
                = ((0x8fffU >= (0x0000ffffU & ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched 
                                                << 1U) 
                                               + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group
                   [(0x0000ffffU & ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched 
                                     << 1U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[2U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[2U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[2U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[2U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[2U])));
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[2U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[2U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[2U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[2U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[2U])))));
            if (((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[2U]) 
                    | (0x80U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[2U])))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[2U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[2U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[2U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[2U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[2U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[2U] = 0ULL;
        }
        if ((3U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[3U] 
                = ((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[3U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(3U) 
                                                * vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group
                   [(0x0000ffffU & (((IData)(3U) * vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[3U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[3U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[3U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[3U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[3U])));
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[3U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[3U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[3U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[3U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[3U])))));
            if (((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[3U]) 
                    | (0x80U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[3U])))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[3U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[3U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[3U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[3U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[3U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[3U] = 0ULL;
        }
        if ((4U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[4U] 
                = ((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[4U] 
                = ((0x8fffU >= (0x0000ffffU & ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched 
                                                << 2U) 
                                               + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group
                   [(0x0000ffffU & ((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched 
                                     << 2U) + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[4U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[4U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[4U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[4U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[4U])));
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[4U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[4U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[4U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[4U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[4U])))));
            if (((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[4U]) 
                    | (0x80U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[4U])))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[4U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[4U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[4U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[4U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[4U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[4U] = 0ULL;
        }
        if ((5U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[5U] 
                = ((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[5U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(5U) 
                                                * vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group
                   [(0x0000ffffU & (((IData)(5U) * vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[5U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[5U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[5U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[5U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[5U])));
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[5U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[5U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[5U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[5U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[5U])))));
            if (((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[5U]) 
                    | (0x80U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[5U])))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[5U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[5U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[5U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[5U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[5U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[5U] = 0ULL;
        }
        if ((6U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[6U] 
                = ((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[6U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(6U) 
                                                * vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group
                   [(0x0000ffffU & (((IData)(6U) * vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[6U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[6U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[6U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[6U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[6U])));
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[6U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[6U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[6U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[6U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[6U])))));
            if (((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[6U]) 
                    | (0x80U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[6U])))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[6U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[6U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[6U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[6U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[6U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[6U] = 0ULL;
        }
        if ((7U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[7U] 
                = ((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_tap_in_bounds)
                    ? ((0xc7ffU >= (0x0000ffffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index))
                        ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch
                       [(0x0000ffffU & tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_index)]
                        : 0U) : 0U);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[7U] 
                = ((0x8fffU >= (0x0000ffffU & (((IData)(7U) 
                                                * vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched) 
                                               + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index)))
                    ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group
                   [(0x0000ffffU & (((IData)(7U) * vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched) 
                                    + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index))]
                    : 0U);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[7U] 
                = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                                   & ((- (IData)(
                                                                 (1U 
                                                                  & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[7U] 
                                                                     >> 7U)))) 
                                                      << 8U)) 
                                                  | vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[7U]), 
                                             ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[7U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[7U])));
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[7U] 
                = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                              (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[7U] 
                                                               >> 0x1fU))) 
                                              << 0x00000020U) 
                                             | (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[7U]))) 
                                            + (((QData)((IData)(
                                                                (0x0001ffffU 
                                                                 & (- (IData)(
                                                                              (1U 
                                                                               & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[7U] 
                                                                                >> 0x0fU))))))) 
                                                << 0x00000010U) 
                                               | (QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[7U])))));
            if (((IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_tap_in_bounds) 
                 & ((0x80U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[7U]) 
                    | (0x80U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[7U])))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_bad_argument = 1U;
            }
            if (((1U & (IData)((vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[7U] 
                                >> 0x20U))) != (1U 
                                                & (IData)(
                                                          (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[7U] 
                                                           >> 0x1fU))))) {
                vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_overflow = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[7U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[7U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[7U] = 0U;
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[7U] = 0ULL;
        }
    }
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mapped_response_error = 6U;
    if ((0U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_error))) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mapped_response_error = 0U;
    } else if ((((1U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_error)) 
                 | (2U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_error))) 
                | (6U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_error)))) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mapped_response_error 
            = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_error;
    }
    if ((((3U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state)) 
          & (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index 
             < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_byte_count)) 
         & (~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_in_bounds)))) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_advance = 1U;
    } else if ((((5U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state)) 
                 & (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_rsp_valid)) 
                & (0U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mapped_response_error)))) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_advance = 1U;
    }
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_base_latched)) 
           + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_byte_offset_wide);
}

void Vtb_s2a_t66_layer0_tile___024root___nba_sequent__TOP__1(Vtb_s2a_t66_layer0_tile___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___nba_sequent__TOP__1\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__hard_reset) {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point0_requant_seen = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point1_bias_checked = 0U;
    } else if ((((0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y) 
                 & (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x)) 
                & (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base))) {
        if (((0x0eU == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state)) 
             & (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_index))) {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point0_requant_seen = 1U;
        }
        if (VL_UNLIKELY((((((~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point1_bias_checked)) 
                            & (0x0dU == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state))) 
                           & (1U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_index)) 
                          & (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index))))) {
            if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point0_requant_seen)))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:269: Assertion failed in %m: T66 \350\277\236\347\273\255\347\251\272\351\227\264\347\202\271\346\243\200\346\237\245\346\234\252\350\247\202\345\257\237\345\210\260 point0 requant\n",3, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 269, "", false);
            }
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point1_bias_checked = 1U;
            if ((0U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                if (VL_UNLIKELY(((0xffffaa77U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[0U])))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:278: Assertion failed in %m: T66 point1 bias \350\265\267\347\202\271\351\224\231\350\257\257\357\274\232lane=0 actual=%08h expected=ffffaa77\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[0U]);
                    VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 278, "", false);
                }
            } else if (VL_UNLIKELY(((0U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[0U])))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:285: Assertion failed in %m: T66 point1 \346\227\240\346\225\210 lane \346\234\252\346\270\205\351\233\266\357\274\232lane=0 actual=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[0U]);
                VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 285, "", false);
            }
            if ((1U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                if (VL_UNLIKELY(((0x00000c59U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[1U])))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:278: Assertion failed in %m: T66 point1 bias \350\265\267\347\202\271\351\224\231\350\257\257\357\274\232lane=1 actual=%08h expected=00000c59\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[1U]);
                    VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 278, "", false);
                }
            } else if (VL_UNLIKELY(((0U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[1U])))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:285: Assertion failed in %m: T66 point1 \346\227\240\346\225\210 lane \346\234\252\346\270\205\351\233\266\357\274\232lane=1 actual=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[1U]);
                VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 285, "", false);
            }
            if ((2U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                if (VL_UNLIKELY(((0xfffffc63U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[2U])))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:278: Assertion failed in %m: T66 point1 bias \350\265\267\347\202\271\351\224\231\350\257\257\357\274\232lane=2 actual=%08h expected=fffffc63\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[2U]);
                    VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 278, "", false);
                }
            } else if (VL_UNLIKELY(((0U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[2U])))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:285: Assertion failed in %m: T66 point1 \346\227\240\346\225\210 lane \346\234\252\346\270\205\351\233\266\357\274\232lane=2 actual=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[2U]);
                VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 285, "", false);
            }
            if ((3U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                if (VL_UNLIKELY(((0x00000062U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[3U])))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:278: Assertion failed in %m: T66 point1 bias \350\265\267\347\202\271\351\224\231\350\257\257\357\274\232lane=3 actual=%08h expected=00000062\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[3U]);
                    VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 278, "", false);
                }
            } else if (VL_UNLIKELY(((0U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[3U])))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:285: Assertion failed in %m: T66 point1 \346\227\240\346\225\210 lane \346\234\252\346\270\205\351\233\266\357\274\232lane=3 actual=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[3U]);
                VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 285, "", false);
            }
            if ((4U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                if (VL_UNLIKELY(((0xfffff883U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[4U])))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:278: Assertion failed in %m: T66 point1 bias \350\265\267\347\202\271\351\224\231\350\257\257\357\274\232lane=4 actual=%08h expected=fffff883\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[4U]);
                    VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 278, "", false);
                }
            } else if (VL_UNLIKELY(((0U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[4U])))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:285: Assertion failed in %m: T66 point1 \346\227\240\346\225\210 lane \346\234\252\346\270\205\351\233\266\357\274\232lane=4 actual=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[4U]);
                VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 285, "", false);
            }
            if ((5U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                if (VL_UNLIKELY(((0x00001351U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[5U])))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:278: Assertion failed in %m: T66 point1 bias \350\265\267\347\202\271\351\224\231\350\257\257\357\274\232lane=5 actual=%08h expected=00001351\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[5U]);
                    VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 278, "", false);
                }
            } else if (VL_UNLIKELY(((0U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[5U])))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:285: Assertion failed in %m: T66 point1 \346\227\240\346\225\210 lane \346\234\252\346\270\205\351\233\266\357\274\232lane=5 actual=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[5U]);
                VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 285, "", false);
            }
            if ((6U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                if (VL_UNLIKELY(((0x00000e93U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[6U])))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:278: Assertion failed in %m: T66 point1 bias \350\265\267\347\202\271\351\224\231\350\257\257\357\274\232lane=6 actual=%08h expected=00000e93\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[6U]);
                    VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 278, "", false);
                }
            } else if (VL_UNLIKELY(((0U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[6U])))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:285: Assertion failed in %m: T66 point1 \346\227\240\346\225\210 lane \346\234\252\346\270\205\351\233\266\357\274\232lane=6 actual=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[6U]);
                VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 285, "", false);
            }
            if ((7U < vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count)) {
                if (VL_UNLIKELY(((0x0000167aU != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[7U])))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:278: Assertion failed in %m: T66 point1 bias \350\265\267\347\202\271\351\224\231\350\257\257\357\274\232lane=7 actual=%08h expected=0000167a\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[7U]);
                    VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 278, "", false);
                }
            } else if (VL_UNLIKELY(((0U != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[7U])))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_s2a_t66_layer0_tile.sv:285: Assertion failed in %m: T66 point1 \346\227\240\346\225\210 lane \346\234\252\346\270\205\351\233\266\357\274\232lane=7 actual=%08h\n",4, 'M',vlSymsp->name(),"tb_s2a_t66_layer0_tile", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[7U]);
                VL_STOP_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 285, "", false);
            }
            VL_WRITEF_NX("T66_POINT_BIAS_RESET_PASS tile=(0,0) oc_group=0 points=0->1 lanes=%0d\n",1
                         , '#',32,vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count);
        }
    }
}

void Vtb_s2a_t66_layer0_tile___024root___timing_ready(Vtb_s2a_t66_layer0_tile___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___timing_ready\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VtrigSched_h2a50a19a__0.ready("@(negedge tb_s2a_t66_layer0_tile.clk)");
    }
    if ((2ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VtrigSched_h2a50a1db__0.ready("@(posedge tb_s2a_t66_layer0_tile.clk)");
    }
}

void Vtb_s2a_t66_layer0_tile___024root___timing_resume(Vtb_s2a_t66_layer0_tile___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___timing_resume\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VtrigSched_h2a50a19a__0.moveToResumeQueue(
                                                          "@(negedge tb_s2a_t66_layer0_tile.clk)");
    vlSelfRef.__VtrigSched_h2a50a1db__0.moveToResumeQueue(
                                                          "@(posedge tb_s2a_t66_layer0_tile.clk)");
    vlSelfRef.__VtrigSched_h2a50a19a__0.resume("@(negedge tb_s2a_t66_layer0_tile.clk)");
    vlSelfRef.__VtrigSched_h2a50a1db__0.resume("@(posedge tb_s2a_t66_layer0_tile.clk)");
    if ((4ULL & vlSelfRef.__VactTriggered[0U])) {
        vlSelfRef.__VdlySched.resume();
    }
}

void Vtb_s2a_t66_layer0_tile___024root___trigger_orInto__act_vec_vec(VlUnpacked<QData/*63:0*/, 1> &out, const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___trigger_orInto__act_vec_vec\n"); );
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
VL_ATTR_COLD void Vtb_s2a_t66_layer0_tile___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG

bool Vtb_s2a_t66_layer0_tile___024root___eval_phase__act(Vtb_s2a_t66_layer0_tile___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___eval_phase__act\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VactExecute;
    // Body
    {
        // Inlined CFunc: _eval_triggers_vec__act
        vlSelfRef.__VactTriggered[0U] = (QData)((IData)(
                                                        ((vlSelfRef.__VdlySched.awaitingCurrentTime() 
                                                          << 2U) 
                                                         | ((((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__clk) 
                                                              & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_t66_layer0_tile__DOT__clk__0))) 
                                                             << 1U) 
                                                            | ((~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__clk)) 
                                                               & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_t66_layer0_tile__DOT__clk__0))))));
        vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_t66_layer0_tile__DOT__clk__0 
            = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__clk;
    }
    Vtb_s2a_t66_layer0_tile___024root___timing_ready(vlSelf);
    Vtb_s2a_t66_layer0_tile___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VactTriggered, vlSelfRef.__VactTriggeredAcc);
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vtb_s2a_t66_layer0_tile___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
    }
#endif
    Vtb_s2a_t66_layer0_tile___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VnbaTriggered, vlSelfRef.__VactTriggered);
    __VactExecute = Vtb_s2a_t66_layer0_tile___024root___trigger_anySet__act(vlSelfRef.__VactTriggered);
    if (__VactExecute) {
        vlSelfRef.__VactTriggeredAcc.fill(0ULL);
        Vtb_s2a_t66_layer0_tile___024root___timing_resume(vlSelf);
        {
            // Inlined CFunc: _eval_act
            if ((7ULL & vlSelfRef.__VactTriggered[0U])) {
                Vtb_s2a_t66_layer0_tile___024root___act_comb__TOP__0(vlSelf);
            }
        }
    }
    return (__VactExecute);
}

bool Vtb_s2a_t66_layer0_tile___024root___eval_phase__inact(Vtb_s2a_t66_layer0_tile___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___eval_phase__inact\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VinactExecute;
    // Body
    __VinactExecute = vlSelfRef.__VdlySched.awaitingZeroDelay();
    if (__VinactExecute) {
        VL_FATAL_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 3, "", "ZERODLY: Design Verilated with '--no-sched-zero-delay', but #0 delay executed at runtime");
    }
    return (__VinactExecute);
}

void Vtb_s2a_t66_layer0_tile___024root___trigger_clear__act(VlUnpacked<QData/*63:0*/, 1> &out) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___trigger_clear__act\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        out[n] = 0ULL;
        n = ((IData)(1U) + n);
    } while ((1U > n));
}

bool Vtb_s2a_t66_layer0_tile___024root___eval_phase__nba(Vtb_s2a_t66_layer0_tile___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___eval_phase__nba\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = Vtb_s2a_t66_layer0_tile___024root___trigger_anySet__act(vlSelfRef.__VnbaTriggered);
    if (__VnbaExecute) {
        {
            // Inlined CFunc: _eval_nba
            if ((2ULL & vlSelfRef.__VnbaTriggered[0U])) {
                Vtb_s2a_t66_layer0_tile___024root___nba_sequent__TOP__0(vlSelf);
            }
            if ((7ULL & vlSelfRef.__VnbaTriggered[0U])) {
                Vtb_s2a_t66_layer0_tile___024root___act_comb__TOP__0(vlSelf);
            }
            if ((1ULL & vlSelfRef.__VnbaTriggered[0U])) {
                Vtb_s2a_t66_layer0_tile___024root___nba_sequent__TOP__1(vlSelf);
            }
        }
        Vtb_s2a_t66_layer0_tile___024root___trigger_clear__act(vlSelfRef.__VnbaTriggered);
    }
    return (__VnbaExecute);
}

void Vtb_s2a_t66_layer0_tile___024root___eval(Vtb_s2a_t66_layer0_tile___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___eval\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VnbaIterCount;
    // Body
    __VnbaIterCount = 0U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VnbaIterCount)))) {
#ifdef VL_DEBUG
            Vtb_s2a_t66_layer0_tile___024root___dump_triggers__act(vlSelfRef.__VnbaTriggered, "nba"s);
#endif
            VL_FATAL_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 3, "", "DIDNOTCONVERGE: NBA region did not converge after '--converge-limit' of 10000 tries");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        vlSelfRef.__VinactIterCount = 0U;
        do {
            if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VinactIterCount)))) {
                VL_FATAL_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 3, "", "DIDNOTCONVERGE: Inactive region did not converge after '--converge-limit' of 10000 tries");
            }
            vlSelfRef.__VinactIterCount = ((IData)(1U) 
                                           + vlSelfRef.__VinactIterCount);
            vlSelfRef.__VactIterCount = 0U;
            do {
                if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                    Vtb_s2a_t66_layer0_tile___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
#endif
                    VL_FATAL_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 3, "", "DIDNOTCONVERGE: Active region did not converge after '--converge-limit' of 10000 tries");
                }
                vlSelfRef.__VactIterCount = ((IData)(1U) 
                                             + vlSelfRef.__VactIterCount);
                vlSelfRef.__VactPhaseResult = Vtb_s2a_t66_layer0_tile___024root___eval_phase__act(vlSelf);
            } while (vlSelfRef.__VactPhaseResult);
            vlSelfRef.__VinactPhaseResult = Vtb_s2a_t66_layer0_tile___024root___eval_phase__inact(vlSelf);
        } while (vlSelfRef.__VinactPhaseResult);
        vlSelfRef.__VnbaPhaseResult = Vtb_s2a_t66_layer0_tile___024root___eval_phase__nba(vlSelf);
    } while (vlSelfRef.__VnbaPhaseResult);
}

void Vtb_s2a_t66_layer0_tile___024root____VbeforeTrig_h2a50a19a__0(Vtb_s2a_t66_layer0_tile___024root* vlSelf, const char* __VeventDescription) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root____VbeforeTrig_h2a50a19a__0\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlUnpacked<QData/*63:0*/, 1> __VTmp;
    // Body
    __VTmp[0U] = (QData)((IData)(((((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__clk) 
                                    & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_t66_layer0_tile__DOT__clk__0))) 
                                   << 1U) | ((~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__clk)) 
                                             & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_t66_layer0_tile__DOT__clk__0)))));
    vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_t66_layer0_tile__DOT__clk__0 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__clk;
    if ((1ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_h2a50a19a__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2a50a19a__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2a50a19a__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2a50a19a__0.ready(__VeventDescription);
    }
    if ((2ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_h2a50a1db__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2a50a1db__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2a50a1db__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2a50a1db__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2a50a1db__0.ready(__VeventDescription);
    }
    vlSelfRef.__VactTriggeredAcc[0U] = (vlSelfRef.__VactTriggeredAcc[0U] 
                                        | __VTmp[0U]);
}

void Vtb_s2a_t66_layer0_tile___024root____VbeforeTrig_h2a50a1db__0(Vtb_s2a_t66_layer0_tile___024root* vlSelf, const char* __VeventDescription) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root____VbeforeTrig_h2a50a1db__0\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlUnpacked<QData/*63:0*/, 1> __VTmp;
    // Body
    __VTmp[0U] = (QData)((IData)(((((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__clk) 
                                    & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_t66_layer0_tile__DOT__clk__0))) 
                                   << 1U) | ((~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__clk)) 
                                             & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_t66_layer0_tile__DOT__clk__0)))));
    vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_t66_layer0_tile__DOT__clk__0 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__clk;
    if ((1ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_h2a50a19a__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2a50a19a__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2a50a19a__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2a50a19a__0.ready(__VeventDescription);
    }
    if ((2ULL & __VTmp[0U])) {
        vlSelfRef.__VtrigSched_h2a50a1db__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2a50a1db__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2a50a1db__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2a50a1db__0.ready(__VeventDescription);
        vlSelfRef.__VtrigSched_h2a50a1db__0.ready(__VeventDescription);
    }
    vlSelfRef.__VactTriggeredAcc[0U] = (vlSelfRef.__VactTriggeredAcc[0U] 
                                        | __VTmp[0U]);
}

#ifdef VL_DEBUG
void Vtb_s2a_t66_layer0_tile___024root___eval_debug_assertions(Vtb_s2a_t66_layer0_tile___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___eval_debug_assertions\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}
#endif  // VL_DEBUG
