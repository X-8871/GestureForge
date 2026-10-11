// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_combined.h for the primary calling header

#include "Vtb_combined__pch.h"

VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__0(Vtb_combined___024root* vlSelf);
VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__1(Vtb_combined___024root* vlSelf);
VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__2(Vtb_combined___024root* vlSelf);
VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__3(Vtb_combined___024root* vlSelf);
VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__4(Vtb_combined___024root* vlSelf);

void Vtb_combined___024root___eval_initial(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_initial\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_combined___024root___eval_initial__TOP__Vtiming__0(vlSelf);
    Vtb_combined___024root___eval_initial__TOP__Vtiming__1(vlSelf);
    Vtb_combined___024root___eval_initial__TOP__Vtiming__2(vlSelf);
    Vtb_combined___024root___eval_initial__TOP__Vtiming__3(vlSelf);
    Vtb_combined___024root___eval_initial__TOP__Vtiming__4(vlSelf);
}

void Vtb_combined___024root____VbeforeTrig_hf7093994__0(Vtb_combined___024root* vlSelf, const char* __VeventDescription);

VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__0(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_initial__TOP__Vtiming__0\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    while ((1U & (~ ((IData)(vlSelfRef.tb_combined__DOT__feature_done) 
                     & (IData)(vlSelfRef.tb_combined__DOT__boundary_done))))) {
        Vtb_combined___024root____VbeforeTrig_hf7093994__0(vlSelf, 
                                                           "@( (tb_combined.feature_done & tb_combined.boundary_done))");
        co_await vlSelfRef.__VtrigSched_hf7093994__0.trigger(1U, 
                                                             nullptr, 
                                                             "@( (tb_combined.feature_done & tb_combined.boundary_done))", 
                                                             "tb_combined.sv", 
                                                             7);
    }
    VL_WRITEF_NX("PASS BOTH_DONE feature=1 boundary=1\n",0);
    VL_FINISH_MT("tb_combined.sv", 7, "");
    co_return;
}

VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__1(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_initial__TOP__Vtiming__1\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    co_await vlSelfRef.__VdlySched.delay(0x0000000077359400ULL, 
                                         nullptr, "tb_combined.sv", 
                                         8);
    VL_WRITEF_NX("[%0t] %%Fatal: tb_combined.sv:8: Assertion failed in %m: \344\270\244\344\270\252\345\233\236\345\275\222\346\234\252\345\256\214\346\225\264\347\273\223\346\235\237\n",3, 'M',vlSymsp->name(),"tb_combined", 'T',-9
                 , '#',64,VL_TIME_UNITED_Q(1000));
    VL_STOP_MT("tb_combined.sv", 8, "", false);
    co_return;
}

VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__2__0(Vtb_combined___024root* vlSelf);
VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__2__1(Vtb_combined___024root* vlSelf);
VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__2__2(Vtb_combined___024root* vlSelf);
VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__2__4(Vtb_combined___024root* vlSelf);
VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__2__6(Vtb_combined___024root* vlSelf);
VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__2__7(Vtb_combined___024root* vlSelf);
VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__2__8(Vtb_combined___024root* vlSelf);
VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__2__9(Vtb_combined___024root* vlSelf);
VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__2__10(Vtb_combined___024root* vlSelf);

VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__2(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_initial__TOP__Vtiming__2\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    co_await Vtb_combined___024root___eval_initial__TOP__Vtiming__2__0(vlSelf);
    co_await Vtb_combined___024root___eval_initial__TOP__Vtiming__2__1(vlSelf);
    co_await Vtb_combined___024root___eval_initial__TOP__Vtiming__2__2(vlSelf);
    {
        // Inlined CFunc: _eval_initial__TOP__Vtiming__2__3
        VL_FCLOSE_I(vlSelfRef.tb_combined__DOT__boundary_test__DOT__fd); vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk1__DOT__action = 0U;
    }
    co_await Vtb_combined___024root___eval_initial__TOP__Vtiming__2__4(vlSelf);
    {
        // Inlined CFunc: _eval_initial__TOP__Vtiming__2__5
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__code = 0U;
    }
    co_await Vtb_combined___024root___eval_initial__TOP__Vtiming__2__6(vlSelf);
    co_await Vtb_combined___024root___eval_initial__TOP__Vtiming__2__7(vlSelf);
    co_await Vtb_combined___024root___eval_initial__TOP__Vtiming__2__8(vlSelf);
    co_await Vtb_combined___024root___eval_initial__TOP__Vtiming__2__9(vlSelf);
    co_await Vtb_combined___024root___eval_initial__TOP__Vtiming__2__10(vlSelf);
    {
        // Inlined CFunc: _eval_initial__TOP__Vtiming__2__11
        if (VL_UNLIKELY(((1U & ((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_valid)) 
                                | (1U != (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_error_code))))))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_boundary.sv:123: Assertion failed in %m: raw80\346\213\222\347\273\235\350\257\255\344\271\211\344\270\215\345\220\214\n",3, 'M',vlSymsp->name(),"tb_combined.boundary_test", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("tb_boundary.sv", 123, "", false);
        }
        VL_WRITEF_NX("PASS CONV_VALIDATION vectors=%0d cycles=%0d abort_mask=%x reset_mask=%x response_cases=24 raw80=1\n",4
                     , '~',32,vlSelfRef.tb_combined__DOT__boundary_test__DOT__cases
                     , '~',32,vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles
                     , '~',32,vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort_mask
                     , '~',32,vlSelfRef.tb_combined__DOT__boundary_test__DOT__reset_mask);
        vlSelfRef.tb_combined__DOT__boundary_done = 1U;
    }
    co_return;
}

void Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(Vtb_combined___024root* vlSelf, const char* __VeventDescription);
void Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(Vtb_combined___024root* vlSelf, const char* __VeventDescription);

VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__2__0(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_initial__TOP__Vtiming__2__0\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset = 1U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_valid = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_ready = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending = 0U;
    Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                       "@(posedge tb_combined.boundary_test.clk)");
    co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_combined.boundary_test.clk)", 
                                                         "tb_boundary.sv", 
                                                         71);
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "tb_boundary.sv", 
                                         71);
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
    Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                       "@(negedge tb_combined.boundary_test.clk)");
    co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_combined.boundary_test.clk)", 
                                                         "tb_boundary.sv", 
                                                         71);
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "tb_boundary.sv", 
                                         71);
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset = 0U;
    Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                       "@(posedge tb_combined.boundary_test.clk)");
    co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_combined.boundary_test.clk)", 
                                                         "tb_boundary.sv", 
                                                         71);
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "tb_boundary.sv", 
                                         71);
    co_return;
}

VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__2__1(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_initial__TOP__Vtiming__2__1\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
    Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                       "@(negedge tb_combined.boundary_test.clk)");
    co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_combined.boundary_test.clk)", 
                                                         "tb_boundary.sv", 
                                                         71);
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "tb_boundary.sv", 
                                         71);
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__fd 
        = VL_FOPEN_NN("validation_vectors.txt"s, "r"s);
    ;
    if (VL_UNLIKELY(((0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__fd)))) {
        VL_WRITEF_NX("[%0t] %%Fatal: tb_boundary.sv:87: Assertion failed in %m: \345\220\221\351\207\217\346\226\207\344\273\266\347\274\272\345\244\261\n",3, 'M',vlSymsp->name(),"tb_combined.boundary_test", 'T',-9
                     , '#',64,VL_TIME_UNITED_Q(1000));
        VL_STOP_MT("tb_boundary.sv", 87, "", false);
    }
    co_return;
}

VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__2__2(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_initial__TOP__Vtiming__2__2\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    {
        while (true) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT____VlemExpr_0 
                = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__fd ? feof(VL_CVT_I_FP(vlSelfRef.tb_combined__DOT__boundary_test__DOT__fd)) : true);
            if (!((! vlSelfRef.tb_combined__DOT__boundary_test__DOT____VlemExpr_0))) break;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__scanned 
                = VL_FSCANF_INX(vlSelfRef.tb_combined__DOT__boundary_test__DOT__fd,"%h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h\n",32
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__layer_index)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_layer_index)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_base_address)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_length_bytes)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_batch_count)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_channels)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_height)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_width)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_base_address)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_length_bytes)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_batch_count)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_channels)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_height)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_width)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__kernel_height)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__kernel_width)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__stride_y)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__stride_x)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_left)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_right)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_top)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_bottom)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__groups)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__padding_value_int8)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_package_base_address)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_package_length_bytes)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__quantized_weight_offset)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__quantized_weight_bytes)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_batch)
                                , '#',2,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__activation_mode)
                                , '#',1,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__buffer_owner_pl)
                                , '#',32,&(vlSelfRef.tb_combined__DOT__boundary_test__DOT__expected_error)) ;
            if ((0x00000020U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__scanned)) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT____VlemExpr_1 
                    = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__fd ? feof(VL_CVT_I_FP(vlSelfRef.tb_combined__DOT__boundary_test__DOT__fd)) : true);
                if (VL_UNLIKELY(((! vlSelfRef.tb_combined__DOT__boundary_test__DOT____VlemExpr_1)))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_boundary.sv:90: Assertion failed in %m: \345\220\221\351\207\217\350\257\273\345\217\226\345\244\261\350\264\245\n",3, 'M',vlSymsp->name(),"tb_combined.boundary_test", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("tb_boundary.sv", 90, "", false);
                }
                goto __Vlabel0;
            }
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_valid = 1U;
            Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                               "@(posedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(posedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
            Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                               "@(negedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_valid = 0U;
            Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                               "@(posedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(posedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
            Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                               "@(negedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            if ((0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__expected_error)) {
                if (VL_UNLIKELY((vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_valid))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_boundary.sv:92: Assertion failed in %m: \345\220\210\346\263\225\345\261\202\346\240\241\351\252\214\350\242\253\346\213\222\347\273\235 case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.boundary_test", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '~',32,vlSelfRef.tb_combined__DOT__boundary_test__DOT__cases);
                    VL_STOP_MT("tb_boundary.sv", 92, "", false);
                }
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort = 1U;
                Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                                   "@(posedge tb_combined.boundary_test.clk)");
                co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                                     nullptr, 
                                                                     "@(posedge tb_combined.boundary_test.clk)", 
                                                                     "tb_boundary.sv", 
                                                                     71);
                co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                     nullptr, 
                                                     "tb_boundary.sv", 
                                                     71);
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
                    = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
                Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                                   "@(negedge tb_combined.boundary_test.clk)");
                co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                                     nullptr, 
                                                                     "@(negedge tb_combined.boundary_test.clk)", 
                                                                     "tb_boundary.sv", 
                                                                     71);
                co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                     nullptr, 
                                                     "tb_boundary.sv", 
                                                     71);
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort = 0U;
            } else {
                if (VL_UNLIKELY(((1U & ((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_valid)) 
                                        | ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_error_code) 
                                           != vlSelfRef.tb_combined__DOT__boundary_test__DOT__expected_error)))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_boundary.sv:93: Assertion failed in %m: \347\213\254\347\253\213\346\240\241\351\252\214\351\273\204\351\207\221\344\270\215\345\220\214 case=%0d want=%0d got=%0d\n",6, 'M',vlSymsp->name(),"tb_combined.boundary_test", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '~',32,vlSelfRef.tb_combined__DOT__boundary_test__DOT__cases
                                 , '~',32,vlSelfRef.tb_combined__DOT__boundary_test__DOT__expected_error
                                 , '#',3,(IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_error_code));
                    VL_STOP_MT("tb_boundary.sv", 93, "", false);
                }
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_ready = 1U;
                Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                                   "@(posedge tb_combined.boundary_test.clk)");
                co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                                     nullptr, 
                                                                     "@(posedge tb_combined.boundary_test.clk)", 
                                                                     "tb_boundary.sv", 
                                                                     71);
                co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                     nullptr, 
                                                     "tb_boundary.sv", 
                                                     71);
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
                    = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
                Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                                   "@(negedge tb_combined.boundary_test.clk)");
                co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                                     nullptr, 
                                                                     "@(negedge tb_combined.boundary_test.clk)", 
                                                                     "tb_boundary.sv", 
                                                                     71);
                co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                     nullptr, 
                                                     "tb_boundary.sv", 
                                                     71);
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_ready = 0U;
            }
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__cases 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cases);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_valid = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_ready = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending = 0U;
            Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                               "@(posedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(posedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
            Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                               "@(negedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset = 0U;
            Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                               "@(posedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(posedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
            Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                               "@(negedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
        }
        __Vlabel0: ;
    }
    co_return;
}

VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__2__4(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_initial__TOP__Vtiming__2__4\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __Vtask_tb_combined__DOT__boundary_test__DOT__service__17__accepted;
    __Vtask_tb_combined__DOT__boundary_test__DOT__service__17__accepted = 0;
    CData/*0:0*/ __Vtask_tb_combined__DOT__boundary_test__DOT__service__17__responded;
    __Vtask_tb_combined__DOT__boundary_test__DOT__service__17__responded = 0;
    CData/*0:0*/ __Vtask_tb_combined__DOT__boundary_test__DOT__service__19__accepted;
    __Vtask_tb_combined__DOT__boundary_test__DOT__service__19__accepted = 0;
    CData/*0:0*/ __Vtask_tb_combined__DOT__boundary_test__DOT__service__19__responded;
    __Vtask_tb_combined__DOT__boundary_test__DOT__service__19__responded = 0;
    // Body
    while (VL_GTS_III(32, 2U, vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk1__DOT__action)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk1__DOT__unnamedblk2__DOT__state_id = 0U;
        while (VL_GTS_III(32, 0x00000014U, vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk1__DOT__unnamedblk2__DOT__state_id)) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_valid = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_ready = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending = 0U;
            Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                               "@(posedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(posedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
            Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                               "@(negedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset = 0U;
            Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                               "@(posedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(posedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
            Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                               "@(negedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__layer_index = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_layer_index = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_base_address = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_length_bytes = 0x00000030U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_batch_count = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_channels = 3U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_height = 4U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_width = 4U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_base_address = 0x01000000U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_length_bytes = 0x00000080U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_batch_count = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_channels = 0x00000020U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_height = 2U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_width = 2U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__kernel_height = 3U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__kernel_width = 3U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__stride_y = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__stride_x = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_left = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_right = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_top = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_bottom = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__groups = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__padding_value_int8 = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_package_base_address = 0x00100000U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_package_length_bytes = 0x005a12fcU;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__quantized_weight_offset = 0x0000013cU;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__quantized_weight_bytes = 0x00000360U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_batch = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__activation_mode = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__buffer_owner_pl = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__error_code = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__error_request = 0U;
            if ((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk1__DOT__unnamedblk2__DOT__state_id)) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_valid = 1U;
                Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                                   "@(posedge tb_combined.boundary_test.clk)");
                co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                                     nullptr, 
                                                                     "@(posedge tb_combined.boundary_test.clk)", 
                                                                     "tb_boundary.sv", 
                                                                     71);
                co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                     nullptr, 
                                                     "tb_boundary.sv", 
                                                     71);
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
                    = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
                Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                                   "@(negedge tb_combined.boundary_test.clk)");
                co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                                     nullptr, 
                                                                     "@(negedge tb_combined.boundary_test.clk)", 
                                                                     "tb_boundary.sv", 
                                                                     71);
                co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                     nullptr, 
                                                     "tb_boundary.sv", 
                                                     71);
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_valid = 0U;
            }
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__timeout_count = 0U;
            while ((((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state) 
                     != vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk1__DOT__unnamedblk2__DOT__state_id) 
                    & VL_GTS_III(32, 0x00004e20U, vlSelfRef.tb_combined__DOT__boundary_test__DOT__timeout_count))) {
                __Vtask_tb_combined__DOT__boundary_test__DOT__service__17__accepted = 0;
                __Vtask_tb_combined__DOT__boundary_test__DOT__service__17__responded = 0;
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready 
                    = (0U != VL_MODDIVS_III(32, vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles, (IData)(5U)));
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid 
                    = ((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending) 
                       & (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count));
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                    = ((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__raw_invalid)
                        ? 0x80808080U : 0U);
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_error 
                    = ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests 
                        == vlSelfRef.tb_combined__DOT__boundary_test__DOT__error_request)
                        ? (7U & VL_EXTENDS_II(32,3, 
                                              (7U & vlSelfRef.tb_combined__DOT__boundary_test__DOT__error_code)))
                        : 0U);
                co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                     nullptr, 
                                                     "tb_boundary.sv", 
                                                     80);
                __Vtask_tb_combined__DOT__boundary_test__DOT__service__17__accepted 
                    = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_valid) 
                       & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready));
                __Vtask_tb_combined__DOT__boundary_test__DOT__service__17__responded 
                    = vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid;
                Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                                   "@(posedge tb_combined.boundary_test.clk)");
                co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                                     nullptr, 
                                                                     "@(posedge tb_combined.boundary_test.clk)", 
                                                                     "tb_boundary.sv", 
                                                                     71);
                co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                     nullptr, 
                                                     "tb_boundary.sv", 
                                                     71);
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
                    = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
                Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                                   "@(negedge tb_combined.boundary_test.clk)");
                co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                                     nullptr, 
                                                                     "@(negedge tb_combined.boundary_test.clk)", 
                                                                     "tb_boundary.sv", 
                                                                     71);
                co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                     nullptr, 
                                                     "tb_boundary.sv", 
                                                     71);
                if (__Vtask_tb_combined__DOT__boundary_test__DOT__service__17__responded) {
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending = 0U;
                } else if (((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending) 
                            & VL_LTS_III(32, 0U, vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count))) {
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count 
                        = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count 
                           - (IData)(1U));
                }
                if (__Vtask_tb_combined__DOT__boundary_test__DOT__service__17__accepted) {
                    if (VL_UNLIKELY(((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending)))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_boundary.sv:83: Assertion failed in %m: \351\207\215\345\244\215\350\257\267\346\261\202\n",3, 'M',vlSymsp->name(),"tb_combined.boundary_test.service", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000));
                        VL_STOP_MT("tb_boundary.sv", 83, "", false);
                    }
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests 
                        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests);
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending = 1U;
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count 
                        = VL_MODDIVS_III(32, vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles, (IData)(4U));
                }
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__timeout_count 
                    = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__timeout_count);
            }
            if (VL_UNLIKELY(((0x00004e20U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__timeout_count)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_boundary.sv:101: Assertion failed in %m: \347\212\266\346\200\201\344\270\215\345\217\257\350\276\276state=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.boundary_test.unnamedblk1.unnamedblk2", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk1__DOT__unnamedblk2__DOT__state_id);
                VL_STOP_MT("tb_boundary.sv", 101, "", false);
            }
            if ((0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk1__DOT__action)) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort = 1U;
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort_mask 
                    = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort_mask 
                       | VL_SHIFTL_III(32,32,32, (IData)(1U), vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk1__DOT__unnamedblk2__DOT__state_id));
            } else {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset = 1U;
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__reset_mask 
                    = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__reset_mask 
                       | VL_SHIFTL_III(32,32,32, (IData)(1U), vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk1__DOT__unnamedblk2__DOT__state_id));
            }
            __Vtask_tb_combined__DOT__boundary_test__DOT__service__19__accepted = 0;
            __Vtask_tb_combined__DOT__boundary_test__DOT__service__19__responded = 0;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready 
                = (0U != VL_MODDIVS_III(32, vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles, (IData)(5U)));
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid 
                = ((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending) 
                   & (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count));
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                = ((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__raw_invalid)
                    ? 0x80808080U : 0U);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_error 
                = ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests 
                    == vlSelfRef.tb_combined__DOT__boundary_test__DOT__error_request)
                    ? (7U & VL_EXTENDS_II(32,3, (7U 
                                                 & vlSelfRef.tb_combined__DOT__boundary_test__DOT__error_code)))
                    : 0U);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 80);
            __Vtask_tb_combined__DOT__boundary_test__DOT__service__19__accepted 
                = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_valid) 
                   & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready));
            __Vtask_tb_combined__DOT__boundary_test__DOT__service__19__responded 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid;
            Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                               "@(posedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(posedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
            Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                               "@(negedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            if (__Vtask_tb_combined__DOT__boundary_test__DOT__service__19__responded) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending = 0U;
            } else if (((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending) 
                        & VL_LTS_III(32, 0U, vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count))) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count 
                    = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count 
                       - (IData)(1U));
            }
            if (__Vtask_tb_combined__DOT__boundary_test__DOT__service__19__accepted) {
                if (VL_UNLIKELY(((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending)))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_boundary.sv:83: Assertion failed in %m: \351\207\215\345\244\215\350\257\267\346\261\202\n",3, 'M',vlSymsp->name(),"tb_combined.boundary_test.service", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("tb_boundary.sv", 83, "", false);
                }
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests 
                    = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests);
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending = 1U;
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count 
                    = VL_MODDIVS_III(32, vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles, (IData)(4U));
            }
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid = 0U;
            Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                               "@(posedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(posedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
            Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                               "@(negedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            if (VL_UNLIKELY(((1U & (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__busy) 
                                     | (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_valid)) 
                                    | (~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_ready))))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_boundary.sv:104: Assertion failed in %m: \345\244\215\344\275\215abort\346\234\252\345\233\236IDLE\n",3, 'M',vlSymsp->name(),"tb_combined.boundary_test.unnamedblk1.unnamedblk2", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("tb_boundary.sv", 104, "", false);
            }
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk1__DOT__unnamedblk2__DOT__state_id 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk1__DOT__unnamedblk2__DOT__state_id);
        }
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk1__DOT__action 
            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk1__DOT__action);
    }
    co_return;
}

VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__2__6(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_initial__TOP__Vtiming__2__6\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__unnamedblk4__DOT__unnamedblk1_1__DOT____Vrepeat0;
    tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__unnamedblk4__DOT__unnamedblk1_1__DOT____Vrepeat0 = 0;
    CData/*0:0*/ __Vtask_tb_combined__DOT__boundary_test__DOT__service__28__accepted;
    __Vtask_tb_combined__DOT__boundary_test__DOT__service__28__accepted = 0;
    CData/*0:0*/ __Vtask_tb_combined__DOT__boundary_test__DOT__service__28__responded;
    __Vtask_tb_combined__DOT__boundary_test__DOT__service__28__responded = 0;
    CData/*0:0*/ __Vtask_tb_combined__DOT__boundary_test__DOT__service__30__accepted;
    __Vtask_tb_combined__DOT__boundary_test__DOT__service__30__accepted = 0;
    CData/*0:0*/ __Vtask_tb_combined__DOT__boundary_test__DOT__service__30__responded;
    __Vtask_tb_combined__DOT__boundary_test__DOT__service__30__responded = 0;
    CData/*0:0*/ __Vtask_tb_combined__DOT__boundary_test__DOT__service__32__accepted;
    __Vtask_tb_combined__DOT__boundary_test__DOT__service__32__accepted = 0;
    CData/*0:0*/ __Vtask_tb_combined__DOT__boundary_test__DOT__service__32__responded;
    __Vtask_tb_combined__DOT__boundary_test__DOT__service__32__responded = 0;
    // Body
    while (VL_GTS_III(32, 8U, vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__code)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__unnamedblk4__DOT__request_target = 1U;
        while (VL_GTES_III(32, 3U, vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__unnamedblk4__DOT__request_target)) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_valid = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_ready = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending = 0U;
            Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                               "@(posedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(posedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
            Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                               "@(negedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset = 0U;
            Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                               "@(posedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(posedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
            Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                               "@(negedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__layer_index = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_layer_index = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_base_address = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_length_bytes = 0x00000030U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_batch_count = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_channels = 3U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_height = 4U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_width = 4U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_base_address = 0x01000000U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_length_bytes = 0x00000080U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_batch_count = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_channels = 0x00000020U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_height = 2U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_width = 2U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__kernel_height = 3U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__kernel_width = 3U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__stride_y = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__stride_x = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_left = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_right = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_top = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_bottom = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__groups = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__padding_value_int8 = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_package_base_address = 0x00100000U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_package_length_bytes = 0x005a12fcU;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__quantized_weight_offset = 0x0000013cU;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__quantized_weight_bytes = 0x00000360U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_batch = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__activation_mode = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__buffer_owner_pl = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__error_code 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__code;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__error_request 
                = ((1U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__unnamedblk4__DOT__request_target)
                    ? 1U : ((2U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__unnamedblk4__DOT__request_target)
                             ? 0x00000031U : 0x00000109U));
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_valid = 1U;
            Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                               "@(posedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(posedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
            Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                               "@(negedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_valid = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__timeout_count = 0U;
            while (((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_valid)) 
                    & VL_GTS_III(32, 0x00004e20U, vlSelfRef.tb_combined__DOT__boundary_test__DOT__timeout_count))) {
                if (VL_LTS_III(32, 2U, vlSelfRef.tb_combined__DOT__boundary_test__DOT__timeout_count)) {
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__buffer_owner_pl = 0U;
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_batch_count = 0xffffffffU;
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_batch_count = 0U;
                }
                __Vtask_tb_combined__DOT__boundary_test__DOT__service__28__accepted = 0;
                __Vtask_tb_combined__DOT__boundary_test__DOT__service__28__responded = 0;
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready 
                    = (0U != VL_MODDIVS_III(32, vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles, (IData)(5U)));
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid 
                    = ((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending) 
                       & (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count));
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                    = ((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__raw_invalid)
                        ? 0x80808080U : 0U);
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_error 
                    = ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests 
                        == vlSelfRef.tb_combined__DOT__boundary_test__DOT__error_request)
                        ? (7U & VL_EXTENDS_II(32,3, 
                                              (7U & vlSelfRef.tb_combined__DOT__boundary_test__DOT__error_code)))
                        : 0U);
                co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                     nullptr, 
                                                     "tb_boundary.sv", 
                                                     80);
                __Vtask_tb_combined__DOT__boundary_test__DOT__service__28__accepted 
                    = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_valid) 
                       & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready));
                __Vtask_tb_combined__DOT__boundary_test__DOT__service__28__responded 
                    = vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid;
                Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                                   "@(posedge tb_combined.boundary_test.clk)");
                co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                                     nullptr, 
                                                                     "@(posedge tb_combined.boundary_test.clk)", 
                                                                     "tb_boundary.sv", 
                                                                     71);
                co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                     nullptr, 
                                                     "tb_boundary.sv", 
                                                     71);
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
                    = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
                Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                                   "@(negedge tb_combined.boundary_test.clk)");
                co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                                     nullptr, 
                                                                     "@(negedge tb_combined.boundary_test.clk)", 
                                                                     "tb_boundary.sv", 
                                                                     71);
                co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                     nullptr, 
                                                     "tb_boundary.sv", 
                                                     71);
                if (__Vtask_tb_combined__DOT__boundary_test__DOT__service__28__responded) {
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending = 0U;
                } else if (((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending) 
                            & VL_LTS_III(32, 0U, vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count))) {
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count 
                        = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count 
                           - (IData)(1U));
                }
                if (__Vtask_tb_combined__DOT__boundary_test__DOT__service__28__accepted) {
                    if (VL_UNLIKELY(((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending)))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_boundary.sv:83: Assertion failed in %m: \351\207\215\345\244\215\350\257\267\346\261\202\n",3, 'M',vlSymsp->name(),"tb_combined.boundary_test.service", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000));
                        VL_STOP_MT("tb_boundary.sv", 83, "", false);
                    }
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests 
                        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests);
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending = 1U;
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count 
                        = VL_MODDIVS_III(32, vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles, (IData)(4U));
                }
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__timeout_count 
                    = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__timeout_count);
            }
            if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_valid)))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_boundary.sv:115: Assertion failed in %m: \345\223\215\345\272\224\351\224\231\350\257\257\346\210\226\346\210\220\345\212\237\350\266\205\346\227\266code=%0d target=%0d\n",5, 'M',vlSymsp->name(),"tb_combined.boundary_test.unnamedblk3.unnamedblk4", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__code
                             , '~',32,vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__unnamedblk4__DOT__request_target);
                VL_STOP_MT("tb_boundary.sv", 115, "", false);
            }
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__expected_error 
                = ((0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__code)
                    ? 0U : ((1U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__code)
                             ? 1U : ((2U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__code)
                                      ? 2U : 6U)));
            if (VL_UNLIKELY((((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_error_code) 
                              != vlSelfRef.tb_combined__DOT__boundary_test__DOT__expected_error)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_boundary.sv:117: Assertion failed in %m: \345\223\215\345\272\224\346\230\240\345\260\204\344\270\215\345\220\214code=%0d target=%0d got=%0d\n",6, 'M',vlSymsp->name(),"tb_combined.boundary_test.unnamedblk3.unnamedblk4", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__code
                             , '~',32,vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__unnamedblk4__DOT__request_target
                             , '#',3,(IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_error_code));
                VL_STOP_MT("tb_boundary.sv", 117, "", false);
            }
            tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__unnamedblk4__DOT__unnamedblk1_1__DOT____Vrepeat0 = 7U;
            while (VL_LTS_III(32, 0U, tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__unnamedblk4__DOT__unnamedblk1_1__DOT____Vrepeat0)) {
                __Vtask_tb_combined__DOT__boundary_test__DOT__service__30__accepted = 0;
                __Vtask_tb_combined__DOT__boundary_test__DOT__service__30__responded = 0;
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready 
                    = (0U != VL_MODDIVS_III(32, vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles, (IData)(5U)));
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid 
                    = ((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending) 
                       & (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count));
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                    = ((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__raw_invalid)
                        ? 0x80808080U : 0U);
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_error 
                    = ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests 
                        == vlSelfRef.tb_combined__DOT__boundary_test__DOT__error_request)
                        ? (7U & VL_EXTENDS_II(32,3, 
                                              (7U & vlSelfRef.tb_combined__DOT__boundary_test__DOT__error_code)))
                        : 0U);
                co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                     nullptr, 
                                                     "tb_boundary.sv", 
                                                     80);
                __Vtask_tb_combined__DOT__boundary_test__DOT__service__30__accepted 
                    = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_valid) 
                       & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready));
                __Vtask_tb_combined__DOT__boundary_test__DOT__service__30__responded 
                    = vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid;
                Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                                   "@(posedge tb_combined.boundary_test.clk)");
                co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                                     nullptr, 
                                                                     "@(posedge tb_combined.boundary_test.clk)", 
                                                                     "tb_boundary.sv", 
                                                                     71);
                co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                     nullptr, 
                                                     "tb_boundary.sv", 
                                                     71);
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
                    = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
                Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                                   "@(negedge tb_combined.boundary_test.clk)");
                co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                                     nullptr, 
                                                                     "@(negedge tb_combined.boundary_test.clk)", 
                                                                     "tb_boundary.sv", 
                                                                     71);
                co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                     nullptr, 
                                                     "tb_boundary.sv", 
                                                     71);
                if (__Vtask_tb_combined__DOT__boundary_test__DOT__service__30__responded) {
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending = 0U;
                } else if (((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending) 
                            & VL_LTS_III(32, 0U, vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count))) {
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count 
                        = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count 
                           - (IData)(1U));
                }
                if (__Vtask_tb_combined__DOT__boundary_test__DOT__service__30__accepted) {
                    if (VL_UNLIKELY(((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending)))) {
                        VL_WRITEF_NX("[%0t] %%Fatal: tb_boundary.sv:83: Assertion failed in %m: \351\207\215\345\244\215\350\257\267\346\261\202\n",3, 'M',vlSymsp->name(),"tb_combined.boundary_test.service", 'T',-9
                                     , '#',64,VL_TIME_UNITED_Q(1000));
                        VL_STOP_MT("tb_boundary.sv", 83, "", false);
                    }
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests 
                        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests);
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending = 1U;
                    vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count 
                        = VL_MODDIVS_III(32, vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles, (IData)(4U));
                }
                tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__unnamedblk4__DOT__unnamedblk1_1__DOT____Vrepeat0 
                    = (tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__unnamedblk4__DOT__unnamedblk1_1__DOT____Vrepeat0 
                       - (IData)(1U));
            }
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_ready = 1U;
            __Vtask_tb_combined__DOT__boundary_test__DOT__service__32__accepted = 0;
            __Vtask_tb_combined__DOT__boundary_test__DOT__service__32__responded = 0;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready 
                = (0U != VL_MODDIVS_III(32, vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles, (IData)(5U)));
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid 
                = ((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending) 
                   & (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count));
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
                = ((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__raw_invalid)
                    ? 0x80808080U : 0U);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_error 
                = ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests 
                    == vlSelfRef.tb_combined__DOT__boundary_test__DOT__error_request)
                    ? (7U & VL_EXTENDS_II(32,3, (7U 
                                                 & vlSelfRef.tb_combined__DOT__boundary_test__DOT__error_code)))
                    : 0U);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 80);
            __Vtask_tb_combined__DOT__boundary_test__DOT__service__32__accepted 
                = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_valid) 
                   & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready));
            __Vtask_tb_combined__DOT__boundary_test__DOT__service__32__responded 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid;
            Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                               "@(posedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(posedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
            Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                               "@(negedge tb_combined.boundary_test.clk)");
            co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                                 nullptr, 
                                                                 "@(negedge tb_combined.boundary_test.clk)", 
                                                                 "tb_boundary.sv", 
                                                                 71);
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_boundary.sv", 
                                                 71);
            if (__Vtask_tb_combined__DOT__boundary_test__DOT__service__32__responded) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending = 0U;
            } else if (((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending) 
                        & VL_LTS_III(32, 0U, vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count))) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count 
                    = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count 
                       - (IData)(1U));
            }
            if (__Vtask_tb_combined__DOT__boundary_test__DOT__service__32__accepted) {
                if (VL_UNLIKELY(((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending)))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_boundary.sv:83: Assertion failed in %m: \351\207\215\345\244\215\350\257\267\346\261\202\n",3, 'M',vlSymsp->name(),"tb_combined.boundary_test.service", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000));
                    VL_STOP_MT("tb_boundary.sv", 83, "", false);
                }
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests 
                    = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests);
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending = 1U;
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count 
                    = VL_MODDIVS_III(32, vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles, (IData)(4U));
            }
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_ready = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__unnamedblk4__DOT__request_target 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__unnamedblk4__DOT__request_target);
        }
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__code 
            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__unnamedblk3__DOT__code);
    }
    co_return;
}

VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__2__7(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_initial__TOP__Vtiming__2__7\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset = 1U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_valid = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_ready = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending = 0U;
    Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                       "@(posedge tb_combined.boundary_test.clk)");
    co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_combined.boundary_test.clk)", 
                                                         "tb_boundary.sv", 
                                                         71);
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "tb_boundary.sv", 
                                         71);
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
    Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                       "@(negedge tb_combined.boundary_test.clk)");
    co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_combined.boundary_test.clk)", 
                                                         "tb_boundary.sv", 
                                                         71);
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "tb_boundary.sv", 
                                         71);
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset = 0U;
    Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                       "@(posedge tb_combined.boundary_test.clk)");
    co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_combined.boundary_test.clk)", 
                                                         "tb_boundary.sv", 
                                                         71);
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "tb_boundary.sv", 
                                         71);
    co_return;
}

VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__2__8(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_initial__TOP__Vtiming__2__8\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
    Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                       "@(negedge tb_combined.boundary_test.clk)");
    co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_combined.boundary_test.clk)", 
                                                         "tb_boundary.sv", 
                                                         71);
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "tb_boundary.sv", 
                                         71);
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__layer_index = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_layer_index = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_base_address = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_length_bytes = 0x00000030U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_batch_count = 1U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_channels = 3U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_height = 4U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__input_width = 4U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_base_address = 0x01000000U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_length_bytes = 0x00000080U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_batch_count = 1U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_channels = 0x00000020U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_height = 2U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_width = 2U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__kernel_height = 3U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__kernel_width = 3U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__stride_y = 1U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__stride_x = 1U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_left = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_right = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_top = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__pad_bottom = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__groups = 1U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__padding_value_int8 = 0U;
    co_return;
}

VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__2__9(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_initial__TOP__Vtiming__2__9\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_package_base_address = 0x00100000U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__weight_package_length_bytes = 0x005a12fcU;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__quantized_weight_offset = 0x0000013cU;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__quantized_weight_bytes = 0x00000360U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__output_batch = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__activation_mode = 1U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__buffer_owner_pl = 1U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__error_code = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__error_request = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__raw_invalid = 1U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_valid = 1U;
    Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                       "@(posedge tb_combined.boundary_test.clk)");
    co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(posedge tb_combined.boundary_test.clk)", 
                                                         "tb_boundary.sv", 
                                                         71);
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "tb_boundary.sv", 
                                         71);
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
    Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                       "@(negedge tb_combined.boundary_test.clk)");
    co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                         nullptr, 
                                                         "@(negedge tb_combined.boundary_test.clk)", 
                                                         "tb_boundary.sv", 
                                                         71);
    co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                         nullptr, "tb_boundary.sv", 
                                         71);
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_valid = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__timeout_count = 0U;
    co_return;
}

VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__2__10(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_initial__TOP__Vtiming__2__10\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __Vtask_tb_combined__DOT__boundary_test__DOT__service__40__accepted;
    __Vtask_tb_combined__DOT__boundary_test__DOT__service__40__accepted = 0;
    CData/*0:0*/ __Vtask_tb_combined__DOT__boundary_test__DOT__service__40__responded;
    __Vtask_tb_combined__DOT__boundary_test__DOT__service__40__responded = 0;
    // Body
    while (((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__result_valid)) 
            & VL_GTS_III(32, 0x00004e20U, vlSelfRef.tb_combined__DOT__boundary_test__DOT__timeout_count))) {
        __Vtask_tb_combined__DOT__boundary_test__DOT__service__40__accepted = 0;
        __Vtask_tb_combined__DOT__boundary_test__DOT__service__40__responded = 0;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready 
            = (0U != VL_MODDIVS_III(32, vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles, (IData)(5U)));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid 
            = ((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending) 
               & (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_rdata 
            = ((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__raw_invalid)
                ? 0x80808080U : 0U);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_error 
            = ((vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests 
                == vlSelfRef.tb_combined__DOT__boundary_test__DOT__error_request)
                ? (7U & VL_EXTENDS_II(32,3, (7U & vlSelfRef.tb_combined__DOT__boundary_test__DOT__error_code)))
                : 0U);
        co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                             nullptr, 
                                             "tb_boundary.sv", 
                                             80);
        __Vtask_tb_combined__DOT__boundary_test__DOT__service__40__accepted 
            = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_valid) 
               & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_ready));
        __Vtask_tb_combined__DOT__boundary_test__DOT__service__40__responded 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid;
        Vtb_combined___024root____VbeforeTrig_h2fc87fd9__0(vlSelf, 
                                                           "@(posedge tb_combined.boundary_test.clk)");
        co_await vlSelfRef.__VtrigSched_h2fc87fd9__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(posedge tb_combined.boundary_test.clk)", 
                                                             "tb_boundary.sv", 
                                                             71);
        co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                             nullptr, 
                                             "tb_boundary.sv", 
                                             71);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles 
            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles);
        Vtb_combined___024root____VbeforeTrig_h2fc87fa8__0(vlSelf, 
                                                           "@(negedge tb_combined.boundary_test.clk)");
        co_await vlSelfRef.__VtrigSched_h2fc87fa8__0.trigger(0U, 
                                                             nullptr, 
                                                             "@(negedge tb_combined.boundary_test.clk)", 
                                                             "tb_boundary.sv", 
                                                             71);
        co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                             nullptr, 
                                             "tb_boundary.sv", 
                                             71);
        if (__Vtask_tb_combined__DOT__boundary_test__DOT__service__40__responded) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending = 0U;
        } else if (((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending) 
                    & VL_LTS_III(32, 0U, vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count 
                = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count 
                   - (IData)(1U));
        }
        if (__Vtask_tb_combined__DOT__boundary_test__DOT__service__40__accepted) {
            if (VL_UNLIKELY(((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_boundary.sv:83: Assertion failed in %m: \351\207\215\345\244\215\350\257\267\346\261\202\n",3, 'M',vlSymsp->name(),"tb_combined.boundary_test.service", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000));
                VL_STOP_MT("tb_boundary.sv", 83, "", false);
            }
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__requests);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__pending = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__delay_count 
                = VL_MODDIVS_III(32, vlSelfRef.tb_combined__DOT__boundary_test__DOT__cycles, (IData)(4U));
        }
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__timeout_count 
            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__timeout_count);
    }
    co_return;
}

VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__3__1(Vtb_combined___024root* vlSelf);

VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__3(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_initial__TOP__Vtiming__3\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    {
        // Inlined CFunc: _eval_initial__TOP__Vtiming__3__0
        IData/*31:0*/ __Vinline_0__eval_initial__TOP__Vtiming__3__0_tb_combined__DOT__feature_test__DOT____VlemExpr_0;
        __Vinline_0__eval_initial__TOP__Vtiming__3__0_tb_combined__DOT__feature_test__DOT____VlemExpr_0 
            = VL_VALUEPLUSARGS_INN(64, "VECTOR_PATH=%s"s, 
                                   vlSelfRef.tb_combined__DOT__feature_test__DOT__vector_path);
        if (VL_UNLIKELY(((! __Vinline_0__eval_initial__TOP__Vtiming__3__0_tb_combined__DOT__feature_test__DOT____VlemExpr_0)))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:40: Assertion failed in %m: \347\262\276\347\241\256\345\220\221\351\207\217\350\267\257\345\276\204\347\274\272\345\244\261\n",3, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("tb_feature.sv", 40, "", false);
        }
        vlSelfRef.tb_combined__DOT__feature_test__DOT__fd 
            = VL_FOPEN_NN(vlSelfRef.tb_combined__DOT__feature_test__DOT__vector_path
                          , "r"s);
        ;
        if (VL_UNLIKELY(((0U == vlSelfRef.tb_combined__DOT__feature_test__DOT__fd)))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:41: Assertion failed in %m: \345\220\221\351\207\217\347\274\272\345\244\261\n",3, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("tb_feature.sv", 41, "", false);
        }
    }
    co_await Vtb_combined___024root___eval_initial__TOP__Vtiming__3__1(vlSelf);
    {
        // Inlined CFunc: _eval_initial__TOP__Vtiming__3__2
        VL_FCLOSE_I(vlSelfRef.tb_combined__DOT__feature_test__DOT__fd); VL_WRITEF_NX("PASS S10_CONV_FEATURE_ADDRESS vectors=%0d end=%0d padding=%0d range=%0d request=%0d\n",5
                                                                                , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count
                                                                                , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__branch_count[0U]
                                                                                , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__branch_count[1U]
                                                                                , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__branch_count[2U]
                                                                                , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__branch_count[3U]);
        vlSelfRef.tb_combined__DOT__feature_done = 1U;
    }
    co_return;
}

extern const VlWide<8>/*255:0*/ Vtb_combined__ConstPool__CONST_hcad9ca82_0;
extern const VlUnpacked<CData/*4:0*/, 4> Vtb_combined__ConstPool__TABLE_hbad1f8b1_0;

VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__3__1(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_initial__TOP__Vtiming__3__1\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __Vfunc_tb_combined__DOT__feature_test__DOT__action__42__index;
    __Vfunc_tb_combined__DOT__feature_test__DOT__action__42__index = 0;
    IData/*31:0*/ __Vfunc_tb_combined__DOT__feature_test__DOT__action__42__count;
    __Vfunc_tb_combined__DOT__feature_test__DOT__action__42__count = 0;
    CData/*0:0*/ __Vfunc_tb_combined__DOT__feature_test__DOT__action__42__bounds;
    __Vfunc_tb_combined__DOT__feature_test__DOT__action__42__bounds = 0;
    CData/*0:0*/ __Vfunc_tb_combined__DOT__feature_test__DOT__action__42__bad;
    __Vfunc_tb_combined__DOT__feature_test__DOT__action__42__bad = 0;
    IData/*31:0*/ __Vfunc_tb_combined__DOT__feature_test__DOT__action__43__index;
    __Vfunc_tb_combined__DOT__feature_test__DOT__action__43__index = 0;
    IData/*31:0*/ __Vfunc_tb_combined__DOT__feature_test__DOT__action__43__count;
    __Vfunc_tb_combined__DOT__feature_test__DOT__action__43__count = 0;
    CData/*0:0*/ __Vfunc_tb_combined__DOT__feature_test__DOT__action__43__bounds;
    __Vfunc_tb_combined__DOT__feature_test__DOT__action__43__bounds = 0;
    CData/*0:0*/ __Vfunc_tb_combined__DOT__feature_test__DOT__action__43__bad;
    __Vfunc_tb_combined__DOT__feature_test__DOT__action__43__bad = 0;
    IData/*31:0*/ __Vtemp_1;
    IData/*31:0*/ __Vtemp_2;
    // Body
    while (true) {
        vlSelfRef.tb_combined__DOT__feature_test__DOT____VlemExpr_1 
            = (vlSelfRef.tb_combined__DOT__feature_test__DOT__fd ? feof(VL_CVT_I_FP(vlSelfRef.tb_combined__DOT__feature_test__DOT__fd)) : true);
        if (!((! vlSelfRef.tb_combined__DOT__feature_test__DOT____VlemExpr_1))) break;
        vlSelfRef.tb_combined__DOT__feature_test__DOT__scanned 
            = VL_FSCANF_INX(vlSelfRef.tb_combined__DOT__feature_test__DOT__fd,"%h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h\n",31
                            , '#',32,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_feature_scan_channel)
                            , '#',32,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_input_height_latched)
                            , '#',32,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_input_width_latched)
                            , '#',32,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_tile_start_y)
                            , '#',32,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_stride_y_latched)
                            , '#',32,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_feature_scan_y)
                            , '#',32,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_pad_top_latched)
                            , '#',32,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_tile_start_x)
                            , '#',32,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_stride_x_latched)
                            , '#',32,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_feature_scan_x)
                            , '#',32,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_pad_left_latched)
                            , '#',32,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_input_base_latched)
                            , '#',32,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_patch_height)
                            , '#',32,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_patch_width)
                            , '#',32,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_feature_scan_index)
                            , '#',32,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_patch_byte_count)
                            , '#',2,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_state)
                            , '#',1,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_valid)
                            , '#',3,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_rsp_error)
                            , '#',64,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_plane)
                            , '#',64,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_y)
                            , '#',64,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_x)
                            , '#',1,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_bounds)
                            , '#',64,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_offset)
                            , '#',64,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_address)
                            , '#',1,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_range)
                            , '#',2,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_action)
                            , '#',1,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_advance)
                            , '#',32,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_aligned)
                            , '#',4,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_strobe)
                            , '#',64,&(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_row)) ;
        if ((0x0000001fU == vlSelfRef.tb_combined__DOT__feature_test__DOT__scanned)) {
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_channel 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_feature_scan_channel;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__input_height_latched 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_input_height_latched;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__input_width_latched 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_input_width_latched;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_y 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_tile_start_y;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__stride_y_latched 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_stride_y_latched;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_y 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_feature_scan_y;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__pad_top_latched 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_pad_top_latched;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__tile_start_x 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_tile_start_x;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__stride_x_latched 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_stride_x_latched;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_x 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_feature_scan_x;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__pad_left_latched 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_pad_left_latched;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__input_base_latched 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_input_base_latched;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_height 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_patch_height;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_width 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_patch_width;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_feature_scan_index;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_byte_count 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_patch_byte_count;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_channel 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_feature_scan_channel;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__input_height_latched 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_input_height_latched;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__input_width_latched 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_input_width_latched;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_y 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_tile_start_y;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__stride_y_latched 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_stride_y_latched;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_y 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_feature_scan_y;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__pad_top_latched 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_pad_top_latched;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__tile_start_x 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_tile_start_x;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__stride_x_latched 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_stride_x_latched;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_x 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_feature_scan_x;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__pad_left_latched 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_pad_left_latched;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__input_base_latched 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_input_base_latched;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_height 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_patch_height;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_width 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_patch_width;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_feature_scan_index;
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_byte_count 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__v_patch_byte_count;
            __Vtemp_1 = VL_MATCHMASKED_I(32, (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_state), Vtb_combined__ConstPool__CONST_hcad9ca82_0);
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__state 
                = Vtb_combined__ConstPool__TABLE_hbad1f8b1_0
                [__Vtemp_1];
            __Vtemp_2 = VL_MATCHMASKED_I(32, (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_state), Vtb_combined__ConstPool__CONST_hcad9ca82_0);
            vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__state 
                = Vtb_combined__ConstPool__TABLE_hbad1f8b1_0
                [__Vtemp_2];
            co_await vlSelfRef.__VdlySched.delay(0x00000000000003e8ULL, 
                                                 nullptr, 
                                                 "tb_feature.sv", 
                                                 79);
            if (VL_UNLIKELY(((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_plane_bytes 
                              != vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_plane)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:80: Assertion failed in %m: \347\273\204\345\220\210\345\255\227\346\256\265u_old.patch_plane_bytes case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                VL_STOP_MT("tb_feature.sv", 80, "", false);
            }
            if (VL_UNLIKELY(((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_input_y 
                              != vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_y)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:81: Assertion failed in %m: \347\273\204\345\220\210\345\255\227\346\256\265u_old.feature_input_y case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                VL_STOP_MT("tb_feature.sv", 81, "", false);
            }
            if (VL_UNLIKELY(((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_input_x 
                              != vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_x)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:82: Assertion failed in %m: \347\273\204\345\220\210\345\255\227\346\256\265u_old.feature_input_x case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                VL_STOP_MT("tb_feature.sv", 82, "", false);
            }
            if (VL_UNLIKELY((((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_in_bounds) 
                              != (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_bounds))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:83: Assertion failed in %m: \347\273\204\345\220\210\345\255\227\346\256\265u_old.feature_scan_in_bounds case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                VL_STOP_MT("tb_feature.sv", 83, "", false);
            }
            if (VL_UNLIKELY(((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_source_offset 
                              != vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_offset)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:84: Assertion failed in %m: \347\273\204\345\220\210\345\255\227\346\256\265u_old.feature_source_offset case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                VL_STOP_MT("tb_feature.sv", 84, "", false);
            }
            if (VL_UNLIKELY(((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_source_address_wide 
                              != vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_address)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:85: Assertion failed in %m: \347\273\204\345\220\210\345\255\227\346\256\265u_old.feature_source_address_wide case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                VL_STOP_MT("tb_feature.sv", 85, "", false);
            }
            if (VL_UNLIKELY((((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_advance) 
                              != (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_advance))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:86: Assertion failed in %m: \347\273\204\345\220\210\345\255\227\346\256\265u_old.feature_scan_advance case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                VL_STOP_MT("tb_feature.sv", 86, "", false);
            }
            if (VL_UNLIKELY((((0x00000000ffffffffULL 
                               < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_source_address_wide) 
                              != (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_range))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:87: Assertion failed in %m: \345\216\237\350\214\203\345\233\264\345\210\244\346\215\256 case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                VL_STOP_MT("tb_feature.sv", 87, "", false);
            }
            __Vfunc_tb_combined__DOT__feature_test__DOT__action__42__bad 
                = (0x00000000ffffffffULL < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_source_address_wide);
            __Vfunc_tb_combined__DOT__feature_test__DOT__action__42__bounds 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_in_bounds;
            __Vfunc_tb_combined__DOT__feature_test__DOT__action__42__count 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__patch_byte_count;
            __Vfunc_tb_combined__DOT__feature_test__DOT__action__42__index 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_scan_index;
            vlSelfRef.tb_combined__DOT__feature_test__DOT____VlemCall_2__action = 0;
            vlSelfRef.tb_combined__DOT__feature_test__DOT____VlemCall_2__action 
                = ((__Vfunc_tb_combined__DOT__feature_test__DOT__action__42__index 
                    >= __Vfunc_tb_combined__DOT__feature_test__DOT__action__42__count)
                    ? 0U : ((IData)(__Vfunc_tb_combined__DOT__feature_test__DOT__action__42__bounds)
                             ? ((IData)(__Vfunc_tb_combined__DOT__feature_test__DOT__action__42__bad)
                                 ? 2U : 3U) : 1U));
            if (VL_UNLIKELY((((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT____VlemCall_2__action) 
                              != (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_action))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:88: Assertion failed in %m: \346\266\210\350\264\271\351\241\272\345\272\217 case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                VL_STOP_MT("tb_feature.sv", 88, "", false);
            }
            if (((3U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_action)) 
                 & (1U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_state)))) {
                if (VL_UNLIKELY((((((IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_source_address_wide 
                                             >> 2U)) 
                                    << 2U) != vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_aligned) 
                                  | ((0x0000000fU & 
                                      ((IData)(1U) 
                                       << (3U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_old__DOT__feature_source_address_wide)))) 
                                     != (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_strobe)))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:89: Assertion failed in %m: \350\257\267\346\261\202\345\257\271\351\275\220/strobe case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                    VL_STOP_MT("tb_feature.sv", 89, "", false);
                }
            }
            if (VL_UNLIKELY(((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_plane_bytes 
                              != vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_plane)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:90: Assertion failed in %m: \347\273\204\345\220\210\345\255\227\346\256\265u_dut.patch_plane_bytes case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                VL_STOP_MT("tb_feature.sv", 90, "", false);
            }
            if (VL_UNLIKELY(((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_input_y 
                              != vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_y)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:91: Assertion failed in %m: \347\273\204\345\220\210\345\255\227\346\256\265u_dut.feature_input_y case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                VL_STOP_MT("tb_feature.sv", 91, "", false);
            }
            if (VL_UNLIKELY(((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_input_x 
                              != vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_x)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:92: Assertion failed in %m: \347\273\204\345\220\210\345\255\227\346\256\265u_dut.feature_input_x case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                VL_STOP_MT("tb_feature.sv", 92, "", false);
            }
            if (VL_UNLIKELY((((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_in_bounds) 
                              != (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_bounds))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:93: Assertion failed in %m: \347\273\204\345\220\210\345\255\227\346\256\265u_dut.feature_scan_in_bounds case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                VL_STOP_MT("tb_feature.sv", 93, "", false);
            }
            if (VL_UNLIKELY(((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_source_offset 
                              != vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_offset)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:94: Assertion failed in %m: \347\273\204\345\220\210\345\255\227\346\256\265u_dut.feature_source_offset case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                VL_STOP_MT("tb_feature.sv", 94, "", false);
            }
            if (VL_UNLIKELY(((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_source_address_wide 
                              != vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_address)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:95: Assertion failed in %m: \347\273\204\345\220\210\345\255\227\346\256\265u_dut.feature_source_address_wide case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                VL_STOP_MT("tb_feature.sv", 95, "", false);
            }
            if (VL_UNLIKELY((((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_advance) 
                              != (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_advance))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:96: Assertion failed in %m: \347\273\204\345\220\210\345\255\227\346\256\265u_dut.feature_scan_advance case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                VL_STOP_MT("tb_feature.sv", 96, "", false);
            }
            if (VL_UNLIKELY((((0x00000000ffffffffULL 
                               < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_source_address_wide) 
                              != (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_range))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:97: Assertion failed in %m: \345\216\237\350\214\203\345\233\264\345\210\244\346\215\256 case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                VL_STOP_MT("tb_feature.sv", 97, "", false);
            }
            __Vfunc_tb_combined__DOT__feature_test__DOT__action__43__bad 
                = (0x00000000ffffffffULL < vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_source_address_wide);
            __Vfunc_tb_combined__DOT__feature_test__DOT__action__43__bounds 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_in_bounds;
            __Vfunc_tb_combined__DOT__feature_test__DOT__action__43__count 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__patch_byte_count;
            __Vfunc_tb_combined__DOT__feature_test__DOT__action__43__index 
                = vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_scan_index;
            vlSelfRef.tb_combined__DOT__feature_test__DOT____VlemCall_3__action = 0;
            vlSelfRef.tb_combined__DOT__feature_test__DOT____VlemCall_3__action 
                = ((__Vfunc_tb_combined__DOT__feature_test__DOT__action__43__index 
                    >= __Vfunc_tb_combined__DOT__feature_test__DOT__action__43__count)
                    ? 0U : ((IData)(__Vfunc_tb_combined__DOT__feature_test__DOT__action__43__bounds)
                             ? ((IData)(__Vfunc_tb_combined__DOT__feature_test__DOT__action__43__bad)
                                 ? 2U : 3U) : 1U));
            if (VL_UNLIKELY((((IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT____VlemCall_3__action) 
                              != (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_action))))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:98: Assertion failed in %m: \346\266\210\350\264\271\351\241\272\345\272\217 case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                VL_STOP_MT("tb_feature.sv", 98, "", false);
            }
            if (((3U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_action)) 
                 & (1U == (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__v_state)))) {
                if (VL_UNLIKELY((((((IData)((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_source_address_wide 
                                             >> 2U)) 
                                    << 2U) != vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_aligned) 
                                  | ((0x0000000fU & 
                                      ((IData)(1U) 
                                       << (3U & (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_source_address_wide)))) 
                                     != (IData)(vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_strobe)))))) {
                    VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:99: Assertion failed in %m: \350\257\267\346\261\202\345\257\271\351\275\220/strobe case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                 , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                    VL_STOP_MT("tb_feature.sv", 99, "", false);
                }
            }
            if (VL_UNLIKELY(((vlSelfRef.tb_combined__DOT__feature_test__DOT__u_dut__DOT__feature_row_offset 
                              != vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_row)))) {
                VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:100: Assertion failed in %m: \346\266\210\350\264\271\350\241\214\347\262\276\347\241\25664/\346\234\252bounds\351\273\230\350\256\2440 case=%0d\n",4, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                             , '#',64,VL_TIME_UNITED_Q(1000)
                             , '~',32,vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
                VL_STOP_MT("tb_feature.sv", 100, "", false);
            }
            vlSelfRef.tb_combined__DOT__feature_test__DOT__branch_count[vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_action] 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__branch_count
                   [vlSelfRef.tb_combined__DOT__feature_test__DOT__gold_action]);
            vlSelfRef.tb_combined__DOT__feature_test__DOT__count 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__feature_test__DOT__count);
        } else if (VL_UNLIKELY(((0xffffffffU != vlSelfRef.tb_combined__DOT__feature_test__DOT__scanned)))) {
            VL_WRITEF_NX("[%0t] %%Fatal: tb_feature.sv:102: Assertion failed in %m: \345\220\221\351\207\217\345\255\227\346\256\265\344\270\215\350\266\263\n",3, 'M',vlSymsp->name(),"tb_combined.feature_test", 'T',-9
                         , '#',64,VL_TIME_UNITED_Q(1000));
            VL_STOP_MT("tb_feature.sv", 102, "", false);
        }
    }
    co_return;
}

VlCoroutine Vtb_combined___024root___eval_initial__TOP__Vtiming__4(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___eval_initial__TOP__Vtiming__4\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    while (VL_LIKELY(!vlSymsp->_vm_contextp__->gotFinish())) {
        co_await vlSelfRef.__VdlySched.delay(0x0000000000001388ULL, 
                                             nullptr, 
                                             "tb_boundary.sv", 
                                             70);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__clk 
            = (1U & (~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__clk)));
    }
    co_return;
}

bool Vtb_combined___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___trigger_anySet__act\n"); );
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

void Vtb_combined___024root___act_comb__TOP__0(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__0\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_valid = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_write = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_write = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_valid = 0U;
    if ((1U & ((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset)) 
               & (~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort))))) {
        if (((4U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_valid = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_write = 0U;
        } else if ((0x10U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_valid = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_write = 1U;
        }
        if (((4U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_write = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_valid = 1U;
        } else if ((0x10U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_write = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_valid = 1U;
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__1(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__1\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_start_ready 
        = ((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset)) 
           & ((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort)) 
              & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__start_ready 
        = ((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset)) 
           & ((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort)) 
              & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_wstrb = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_rstrb = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_rstrb = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_wstrb = 0U;
    if ((1U & ((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset)) 
               & (~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort))))) {
        if ((1U & (~ ((4U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)) 
                      || (8U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)))))) {
            if ((0x10U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_wstrb 
                    = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_strobe_latched;
            }
        }
        if (((4U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_req_rstrb 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__request_strobe_latched;
        }
        if (((4U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_rstrb 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched;
        }
        if ((1U & (~ ((4U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)) 
                      || (8U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)))))) {
            if ((0x10U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_req_wstrb 
                    = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__request_strobe_latched;
            }
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__2(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__2\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
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
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__candidate_backend_cancel 
        = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__hard_reset) 
           | (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__abort));
    __Vtemp_1[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_batch_count_latched;
    __Vtemp_1[1U] = 0U;
    __Vtemp_1[2U] = 0U;
    __Vtemp_1[3U] = 0U;
    __Vtemp_2[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_channels_latched;
    __Vtemp_2[1U] = 0U;
    __Vtemp_2[2U] = 0U;
    __Vtemp_2[3U] = 0U;
    VL_MUL_W(4, __Vtemp_3, __Vtemp_1, __Vtemp_2);
    __Vtemp_4[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_height_latched;
    __Vtemp_4[1U] = 0U;
    __Vtemp_4[2U] = 0U;
    __Vtemp_4[3U] = 0U;
    VL_MUL_W(4, __Vtemp_5, __Vtemp_3, __Vtemp_4);
    __Vtemp_6[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_width_latched;
    __Vtemp_6[1U] = 0U;
    __Vtemp_6[2U] = 0U;
    __Vtemp_6[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_elements_wide, __Vtemp_5, __Vtemp_6);
    __Vtemp_7[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_batch_count_latched;
    __Vtemp_7[1U] = 0U;
    __Vtemp_7[2U] = 0U;
    __Vtemp_7[3U] = 0U;
    __Vtemp_8[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched;
    __Vtemp_8[1U] = 0U;
    __Vtemp_8[2U] = 0U;
    __Vtemp_8[3U] = 0U;
    VL_MUL_W(4, __Vtemp_9, __Vtemp_7, __Vtemp_8);
    __Vtemp_10[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched;
    __Vtemp_10[1U] = 0U;
    __Vtemp_10[2U] = 0U;
    __Vtemp_10[3U] = 0U;
    VL_MUL_W(4, __Vtemp_11, __Vtemp_9, __Vtemp_10);
    __Vtemp_12[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched;
    __Vtemp_12[1U] = 0U;
    __Vtemp_12[2U] = 0U;
    __Vtemp_12[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_elements_wide, __Vtemp_11, __Vtemp_12);
    __Vtemp_13[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched;
    __Vtemp_13[1U] = 0U;
    __Vtemp_13[2U] = 0U;
    __Vtemp_13[3U] = 0U;
    __Vtemp_14[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_channels_latched;
    __Vtemp_14[1U] = 0U;
    __Vtemp_14[2U] = 0U;
    __Vtemp_14[3U] = 0U;
    VL_MUL_W(4, __Vtemp_15, __Vtemp_13, __Vtemp_14);
    __Vtemp_16[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched;
    __Vtemp_16[1U] = 0U;
    __Vtemp_16[2U] = 0U;
    __Vtemp_16[3U] = 0U;
    VL_MUL_W(4, __Vtemp_17, __Vtemp_15, __Vtemp_16);
    __Vtemp_18[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched;
    __Vtemp_18[1U] = 0U;
    __Vtemp_18[2U] = 0U;
    __Vtemp_18[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__expected_weight_bytes_wide, __Vtemp_17, __Vtemp_18);
    __Vtemp_19[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_channels_latched;
    __Vtemp_19[1U] = 0U;
    __Vtemp_19[2U] = 0U;
    __Vtemp_19[3U] = 0U;
    __Vtemp_20[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched;
    __Vtemp_20[1U] = 0U;
    __Vtemp_20[2U] = 0U;
    __Vtemp_20[3U] = 0U;
    VL_MUL_W(4, __Vtemp_21, __Vtemp_19, __Vtemp_20);
    __Vtemp_22[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched;
    __Vtemp_22[1U] = 0U;
    __Vtemp_22[2U] = 0U;
    __Vtemp_22[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_wide, __Vtemp_21, __Vtemp_22);
    __Vtemp_23[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_base_latched;
    __Vtemp_23[1U] = 0U;
    __Vtemp_23[2U] = 0U;
    __Vtemp_23[3U] = 0U;
    __Vtemp_24[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_length_latched;
    __Vtemp_24[1U] = 0U;
    __Vtemp_24[2U] = 0U;
    __Vtemp_24[3U] = 0U;
    VL_ADD_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_end_wide, __Vtemp_23, __Vtemp_24);
    __Vtemp_25[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_base_latched;
    __Vtemp_25[1U] = 0U;
    __Vtemp_25[2U] = 0U;
    __Vtemp_25[3U] = 0U;
    __Vtemp_26[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_length_latched;
    __Vtemp_26[1U] = 0U;
    __Vtemp_26[2U] = 0U;
    __Vtemp_26[3U] = 0U;
    VL_ADD_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_end_wide, __Vtemp_25, __Vtemp_26);
    __Vtemp_27[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_package_base_latched;
    __Vtemp_27[1U] = 0U;
    __Vtemp_27[2U] = 0U;
    __Vtemp_27[3U] = 0U;
    __Vtemp_28[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_package_length_latched;
    __Vtemp_28[1U] = 0U;
    __Vtemp_28[2U] = 0U;
    __Vtemp_28[3U] = 0U;
    VL_ADD_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_package_end_wide, __Vtemp_27, __Vtemp_28);
    __Vtemp_29[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__quantized_weight_offset_latched;
    __Vtemp_29[1U] = 0U;
    __Vtemp_29[2U] = 0U;
    __Vtemp_29[3U] = 0U;
    __Vtemp_30[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__quantized_weight_bytes_latched;
    __Vtemp_30[1U] = 0U;
    __Vtemp_30[2U] = 0U;
    __Vtemp_30[3U] = 0U;
    VL_ADD_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__quantized_weight_end_wide, __Vtemp_29, __Vtemp_30);
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_numerator 
        = (((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_height_latched)) 
            + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_top_latched))) 
           + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_bottom_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_numerator 
        = (((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_width_latched)) 
            + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_left_latched))) 
           + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_right_latched)));
}

void Vtb_combined___024root___act_comb__TOP__3(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__3\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    VlWide<4>/*127:0*/ tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_height_wide;
    VL_ZERO_W(128, tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_height_wide);
    VlWide<4>/*127:0*/ tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_width_wide;
    VL_ZERO_W(128, tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_width_wide);
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
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_shape_span 
        = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_numerator 
           - (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_shape_span 
        = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_numerator 
           - (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_shape_product 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched)) 
           * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_shape_product 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched)) 
           * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_span_plus_stride 
        = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_shape_span 
           + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_span_plus_stride 
        = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_shape_span 
           + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched)));
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_height_wide[0U] = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_height_wide[1U] = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_height_wide[2U] = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_height_wide[3U] = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_width_wide[0U] = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_width_wide[1U] = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_width_wide[2U] = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_width_wide[3U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_bytes_wide[0U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_bytes_wide[1U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_bytes_wide[2U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_bytes_wide[3U] = 0U;
    if (((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched) 
         & (0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched))) {
        __Vtemp_1[0U] = (((8U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched)
                           ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched
                           : 8U) - (IData)(1U));
        __Vtemp_1[1U] = 0U;
        __Vtemp_1[2U] = 0U;
        __Vtemp_1[3U] = 0U;
        __Vtemp_2[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched;
        __Vtemp_2[1U] = 0U;
        __Vtemp_2[2U] = 0U;
        __Vtemp_2[3U] = 0U;
        VL_MUL_W(4, __Vtemp_3, __Vtemp_1, __Vtemp_2);
        __Vtemp_4[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched;
        __Vtemp_4[1U] = 0U;
        __Vtemp_4[2U] = 0U;
        __Vtemp_4[3U] = 0U;
        VL_ADD_W(4, tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_height_wide, __Vtemp_3, __Vtemp_4);
        __Vtemp_5[0U] = (((8U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched)
                           ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched
                           : 8U) - (IData)(1U));
        __Vtemp_5[1U] = 0U;
        __Vtemp_5[2U] = 0U;
        __Vtemp_5[3U] = 0U;
        __Vtemp_6[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched;
        __Vtemp_6[1U] = 0U;
        __Vtemp_6[2U] = 0U;
        __Vtemp_6[3U] = 0U;
        VL_MUL_W(4, __Vtemp_7, __Vtemp_5, __Vtemp_6);
        __Vtemp_8[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched;
        __Vtemp_8[1U] = 0U;
        __Vtemp_8[2U] = 0U;
        __Vtemp_8[3U] = 0U;
        VL_ADD_W(4, tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_width_wide, __Vtemp_7, __Vtemp_8);
        VL_MUL_W(4, __Vtemp_9, tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_height_wide, tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_width_wide);
        __Vtemp_10[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_channels_latched;
        __Vtemp_10[1U] = 0U;
        __Vtemp_10[2U] = 0U;
        __Vtemp_10[3U] = 0U;
        VL_MUL_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_bytes_wide, __Vtemp_9, __Vtemp_10);
    }
    __Vtemp_11[0U] = ((8U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched)
                       ? vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched
                       : 8U);
    __Vtemp_11[1U] = 0U;
    __Vtemp_11[2U] = 0U;
    __Vtemp_11[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_weight_group_bytes_wide, __Vtemp_11, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_wide);
}

void Vtb_combined___024root___act_comb__TOP__4(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__4\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
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
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__validation_ok = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__validation_error = 1U;
    __Vtemp_2[0U] = 0x00001200U;
    __Vtemp_2[1U] = 0U;
    __Vtemp_2[2U] = 0U;
    __Vtemp_2[3U] = 0U;
    if ((1U & ((((((((((((((((((((((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__buffer_owner_pl)) 
                                   | (1U < (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__activation_mode_latched))) 
                                  | (1U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_batch_count_latched)) 
                                 | (1U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_batch_count_latched)) 
                                | (0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_batch_latched)) 
                               | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_channels_latched)) 
                              | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_height_latched)) 
                             | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_width_latched)) 
                            | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched)) 
                           | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_latched)) 
                          | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_latched)) 
                         | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched)) 
                        | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched)) 
                       | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched)) 
                      | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched)) 
                     | (1U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__groups_latched)) 
                    | (0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__padding_latched)) 
                   | (0U == (((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_wide[0U] 
                               | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_wide[1U]) 
                              | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_wide[2U]) 
                             | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_wide[3U]))) 
                  | VL_LT_W(4, __Vtemp_2, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_wide)) 
                 | (0x00000026U <= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched)) 
                | ((0x00000026U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched) 
                   & (0U != ((0x25U >= (0x0000003fU 
                                        & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched))
                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OP
                             [(0x0000003fU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched)]
                              : 0U)))) | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched 
                                          != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_layer_index_latched)))) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__validation_error 
            = (((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched 
                 != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_layer_index_latched) 
                | (0x00000026U <= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched))
                ? 2U : 1U);
    } else {
        __Vtemp_3[0U] = 0xffffffffU;
        __Vtemp_3[1U] = 0U;
        __Vtemp_3[2U] = 0U;
        __Vtemp_3[3U] = 0U;
        __Vtemp_4[0U] = 0xffffffffU;
        __Vtemp_4[1U] = 0U;
        __Vtemp_4[2U] = 0U;
        __Vtemp_4[3U] = 0U;
        __Vtemp_5[0U] = 0xffffffffU;
        __Vtemp_5[1U] = 0U;
        __Vtemp_5[2U] = 0U;
        __Vtemp_5[3U] = 0U;
        if ((((((VL_LT_W(4, __Vtemp_3, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_elements_wide) 
                 | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_length_latched 
                    != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_elements_wide[0U])) 
                | VL_LT_W(4, __Vtemp_4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_elements_wide)) 
               | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_length_latched 
                  != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_elements_wide[0U])) 
              | VL_LT_W(4, __Vtemp_5, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__expected_weight_bytes_wide)) 
             | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__quantized_weight_bytes_latched 
                != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__expected_weight_bytes_wide[0U]))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__validation_error = 3U;
        } else {
            __Vtemp_6[0U] = 0U;
            __Vtemp_6[1U] = 1U;
            __Vtemp_6[2U] = 0U;
            __Vtemp_6[3U] = 0U;
            __Vtemp_7[0U] = 0U;
            __Vtemp_7[1U] = 1U;
            __Vtemp_7[2U] = 0U;
            __Vtemp_7[3U] = 0U;
            __Vtemp_8[0U] = 0U;
            __Vtemp_8[1U] = 1U;
            __Vtemp_8[2U] = 0U;
            __Vtemp_8[3U] = 0U;
            __Vtemp_9[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_package_length_latched;
            __Vtemp_9[1U] = 0U;
            __Vtemp_9[2U] = 0U;
            __Vtemp_9[3U] = 0U;
            __Vtemp_10[0U] = 0x00000c5cU;
            __Vtemp_10[1U] = 0U;
            __Vtemp_10[2U] = 0U;
            __Vtemp_10[3U] = 0U;
            __Vtemp_11[0U] = ((0x25U >= (0x0000003fU 
                                         & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched))
                               ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                              [(0x0000003fU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched)]
                               : 0U);
            __Vtemp_11[1U] = 0U;
            __Vtemp_11[2U] = 0U;
            __Vtemp_11[3U] = 0U;
            __Vtemp_12[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched;
            __Vtemp_12[1U] = 0U;
            __Vtemp_12[2U] = 0U;
            __Vtemp_12[3U] = 0U;
            VL_ADD_W(4, __Vtemp_13, __Vtemp_11, __Vtemp_12);
            __Vtemp_14[0U] = 0x0000c800U;
            __Vtemp_14[1U] = 0U;
            __Vtemp_14[2U] = 0U;
            __Vtemp_14[3U] = 0U;
            __Vtemp_15[0U] = 0x00009000U;
            __Vtemp_15[1U] = 0U;
            __Vtemp_15[2U] = 0U;
            __Vtemp_15[3U] = 0U;
            if (((((((((VL_LT_W(4, __Vtemp_6, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_end_wide) 
                        | VL_LT_W(4, __Vtemp_7, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_end_wide)) 
                       | VL_LT_W(4, __Vtemp_8, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_package_end_wide)) 
                      | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_package_length_latched)) 
                     | VL_GT_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__quantized_weight_end_wide, __Vtemp_9)) 
                    | (((0x25U >= (0x0000003fU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                        [(0x0000003fU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__layer_index_latched)]
                         : 0U) != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_channels_latched)) 
                   | VL_LT_W(4, __Vtemp_10, __Vtemp_13)) 
                  | VL_LT_W(4, __Vtemp_14, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_tile_patch_bytes_wide)) 
                 | VL_LT_W(4, __Vtemp_15, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__full_weight_group_bytes_wide))) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__validation_error = 2U;
            } else if (((((((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_numerator 
                             < (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched))) 
                            | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_numerator 
                               < (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched)))) 
                           | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_shape_product 
                              <= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_shape_span)) 
                          | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_shape_product 
                             > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_height_span_plus_stride)) 
                         | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_shape_product 
                            <= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_shape_span)) 
                        | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_shape_product 
                           > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__output_width_span_plus_stride))) {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__validation_error = 1U;
            } else {
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__validation_ok = 1U;
                vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__validation_error = 0U;
            }
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__5(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__5\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    QData/*63:0*/ tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_input_y;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_input_y = 0;
    QData/*63:0*/ tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_input_x;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_input_x = 0;
    QData/*63:0*/ tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_source_offset;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_source_offset = 0;
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_plane_bytes 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_height)) 
           * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_width)));
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_input_y = 0ULL;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_input_x = 0ULL;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_in_bounds = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_advance = 0U;
    tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_source_offset = 0ULL;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_source_address_wide = 0ULL;
    if (((0ULL != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_plane_bytes) 
         & (0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_width))) {
        tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_input_y 
            = ((((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y)) 
                 * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched))) 
                + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_y))) 
               - (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_top_latched)));
        tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_input_x 
            = ((((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x)) 
                 * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched))) 
                + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_x))) 
               - (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_left_latched)));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_input_y) 
                 & VL_LTS_IQQ(64, tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_input_y, (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_input_x)) 
               & VL_LTS_IQQ(64, tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_input_x, (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_width_latched))));
        if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_in_bounds) {
            tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_source_offset 
                = (((((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_channel)) 
                      * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_height_latched))) 
                     + tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_input_y) 
                    * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_width_latched))) 
                   + tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_input_x);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_source_address_wide 
                = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_base_latched)) 
                   + tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_source_offset);
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__6(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__6\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_area 
        = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched 
           * vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched);
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_next_input_channel 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_input_channel;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_next_kernel_y 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_y;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_next_reduction_index 
        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_reduction_index);
    if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_x) 
         >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_width_latched)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_next_kernel_x = 0U;
        if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_y) 
             >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__kernel_height_latched)) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_next_kernel_y = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_next_input_channel 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_input_channel);
        } else {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_next_kernel_y 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_y);
        }
    } else {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_next_kernel_x 
            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_x);
    }
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_point_y 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_y;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_point_x 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_x;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_input_channel 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_input_channel;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_kernel_y 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_y;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_kernel_x 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_x;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_reduction_index 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_reduction_index;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_input_y = 0ULL;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_input_x = 0ULL;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_tap_in_bounds = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_feature_index_wide = 0ULL;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_feature_index = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_enable = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_bad_argument = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_overflow = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[0U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[0U] = 0U;
}

void Vtb_combined___024root___act_comb__TOP__7(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__7\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[0U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[0U] = 0ULL;
    if ((0U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[0U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[0U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[0U];
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[0U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[0U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[0U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[0U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[0U])));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[0U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[0U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[0U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[0U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[0U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[0U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[0U])))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[0U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[0U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__8(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__8\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[1U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[1U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[1U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[1U] = 0ULL;
    if ((1U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[1U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[1U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[1U];
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[1U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[1U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[1U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[1U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[1U])));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[1U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[1U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[1U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[1U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[1U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[1U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[1U])))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[1U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[1U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__9(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__9\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[2U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[2U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[2U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[2U] = 0ULL;
    if ((2U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[2U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[2U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[2U];
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[2U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[2U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[2U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[2U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[2U])));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[2U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[2U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[2U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[2U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[2U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[2U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[2U])))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[2U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[2U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__10(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__10\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[3U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[3U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[3U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[3U] = 0ULL;
    if ((3U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[3U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[3U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[3U];
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[3U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[3U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[3U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[3U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[3U])));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[3U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[3U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[3U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[3U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[3U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[3U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[3U])))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[3U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[3U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__11(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__11\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[4U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[4U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[4U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[4U] = 0ULL;
    if ((4U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[4U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[4U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[4U];
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[4U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[4U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[4U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[4U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[4U])));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[4U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[4U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[4U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[4U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[4U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[4U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[4U])))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[4U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[4U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__12(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__12\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[5U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[5U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[5U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[5U] = 0ULL;
    if ((5U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[5U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[5U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[5U];
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[5U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[5U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[5U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[5U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[5U])));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[5U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[5U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[5U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[5U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[5U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[5U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[5U])))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[5U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[5U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__13(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__13\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[6U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[6U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[6U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[6U] = 0ULL;
    if ((6U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[6U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[6U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[6U];
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[6U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[6U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[6U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[6U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[6U])));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[6U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[6U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[6U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[6U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[6U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[6U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[6U])))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[6U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[6U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__14(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__14\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[7U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[7U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[7U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[7U] = 0ULL;
    if ((7U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[7U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[7U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__weight_read_byte[7U];
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[7U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[7U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[7U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[7U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[7U])));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[7U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[7U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__lane_accumulator[7U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[7U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_product[7U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_feature_byte[7U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_weight_byte[7U])))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[7U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_sum[7U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__15(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__15\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (((0x0bU == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)) 
         | (0x0cU == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)))) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_point_y 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_y;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_point_x 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_x;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_input_channel = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_kernel_y = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_kernel_x = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_reduction_index = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_enable = 1U;
    } else if ((0x0dU == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state))) {
        if ((((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_reduction_index) 
               < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__reduction_count_latched) 
              & (~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_bad_argument))) 
             & (~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_overflow)))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_point_y 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_y;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_point_x 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_point_scan_x;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_input_channel 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_next_input_channel;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_kernel_y 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_next_kernel_y;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_kernel_x 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_next_kernel_x;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_reduction_index 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_next_reduction_index;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_enable = 1U;
        }
    }
    if (((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_kernel_area) 
         & (0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_width))) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_input_y 
            = (((((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_y)) 
                  * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched))) 
                 + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_point_y)) 
                    * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched)))) 
                + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_kernel_y))) 
               - (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_top_latched)));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_input_x 
            = (((((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__tile_start_x)) 
                  * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched))) 
                 + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_point_x)) 
                    * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched)))) 
                + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_kernel_x))) 
               - (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__pad_left_latched)));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_tap_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_input_y) 
                 & VL_LTS_IQQ(64, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_input_y, (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_input_x)) 
               & VL_LTS_IQQ(64, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_input_x, (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__input_width_latched))));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_feature_index_wide 
            = (((((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_input_channel)) 
                  * vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_plane_bytes) 
                 + ((((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_point_y)) 
                      * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_y_latched))) 
                     + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_kernel_y))) 
                    * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_width)))) 
                + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_point_x)) 
                   * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__stride_x_latched)))) 
               + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_kernel_x)));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_feature_index 
            = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__compute_read_feature_index_wide);
    }
}

void Vtb_combined___024root___act_comb__TOP__16(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__16\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    QData/*63:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_input_y;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_input_y = 0;
    QData/*63:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_input_x;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_input_x = 0;
    QData/*63:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_geometry_plane;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_geometry_plane = 0;
    QData/*63:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_channel_plane_offset;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_channel_plane_offset = 0;
    QData/*63:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_row_offset;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_row_offset = 0;
    QData/*63:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_source_offset;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_source_offset = 0;
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mapped_response_error = 6U;
    if ((0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_error))) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mapped_response_error = 0U;
    } else if ((((1U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_error)) 
                 | (2U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_error))) 
                | (6U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_error)))) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mapped_response_error 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_error;
    }
    if ((((3U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)) 
          & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_index 
             < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__patch_byte_count)) 
         & (~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_in_bounds)))) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_advance = 1U;
    } else if ((((5U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__state)) 
                 & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid)) 
                & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__mapped_response_error)))) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_dut__DOT__feature_scan_advance = 1U;
    }
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_plane_bytes 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_height)) 
           * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_width)));
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_input_y = 0ULL;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_input_x = 0ULL;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_in_bounds = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_advance = 0U;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_geometry_plane = 0ULL;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_channel_plane_offset = 0ULL;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_row_offset = 0ULL;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_source_offset = 0ULL;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_source_address_wide = 0ULL;
    if (((0ULL != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_plane_bytes) 
         & (0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_width))) {
        tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_input_y 
            = ((((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y)) 
                 * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_y_latched))) 
                + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_y))) 
               - (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__pad_top_latched)));
        tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_input_x 
            = ((((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x)) 
                 * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_x_latched))) 
                + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_x))) 
               - (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__pad_left_latched)));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_input_y) 
                 & VL_LTS_IQQ(64, tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_input_y, (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_input_x)) 
               & VL_LTS_IQQ(64, tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_input_x, (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_width_latched))));
        if (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_in_bounds) {
            tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_geometry_plane 
                = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_height_latched)) 
                   * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_width_latched)));
            tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_channel_plane_offset 
                = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_channel)) 
                   * tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_geometry_plane);
            tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_row_offset 
                = ((QData)((IData)(tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_input_y)) 
                   * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_width_latched)));
            tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_source_offset 
                = ((tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_channel_plane_offset 
                    + tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_row_offset) 
                   + tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_input_x);
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_source_address_wide 
                = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_base_latched)) 
                   + tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_source_offset);
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__17(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__17\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_area 
        = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_height_latched 
           * vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_width_latched);
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_next_input_channel 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_input_channel;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_next_kernel_y 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_y;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_next_reduction_index 
        = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_reduction_index);
    if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_x) 
         >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_width_latched)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_next_kernel_x = 0U;
        if ((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_y) 
             >= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_height_latched)) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_next_kernel_y = 0U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_next_input_channel 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_input_channel);
        } else {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_next_kernel_y 
                = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_y);
        }
    } else {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_next_kernel_x 
            = ((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_x);
    }
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_point_y 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_y;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_point_x 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_x;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_input_channel 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_input_channel;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_kernel_y 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_y;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_kernel_x 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_x;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_reduction_index 
        = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_reduction_index;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_input_y = 0ULL;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_input_x = 0ULL;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_tap_in_bounds = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_feature_index_wide = 0ULL;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_feature_index = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_enable = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_bad_argument = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_overflow = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[0U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[0U] = 0U;
}

void Vtb_combined___024root___act_comb__TOP__18(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__18\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[0U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[0U] = 0ULL;
    if ((0U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[0U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[0U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[0U];
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[0U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[0U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[0U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[0U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[0U])));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[0U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[0U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[0U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[0U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[0U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[0U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[0U])))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[0U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[0U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__19(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__19\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[1U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[1U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[1U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[1U] = 0ULL;
    if ((1U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[1U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[1U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[1U];
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[1U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[1U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[1U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[1U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[1U])));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[1U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[1U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[1U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[1U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[1U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[1U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[1U])))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[1U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[1U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__20(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__20\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[2U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[2U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[2U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[2U] = 0ULL;
    if ((2U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[2U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[2U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[2U];
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[2U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[2U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[2U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[2U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[2U])));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[2U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[2U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[2U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[2U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[2U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[2U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[2U])))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[2U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[2U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__21(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__21\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[3U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[3U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[3U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[3U] = 0ULL;
    if ((3U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[3U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[3U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[3U];
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[3U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[3U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[3U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[3U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[3U])));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[3U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[3U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[3U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[3U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[3U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[3U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[3U])))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[3U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[3U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__22(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__22\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[4U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[4U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[4U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[4U] = 0ULL;
    if ((4U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[4U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[4U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[4U];
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[4U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[4U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[4U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[4U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[4U])));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[4U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[4U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[4U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[4U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[4U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[4U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[4U])))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[4U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[4U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__23(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__23\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[5U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[5U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[5U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[5U] = 0ULL;
    if ((5U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[5U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[5U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[5U];
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[5U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[5U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[5U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[5U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[5U])));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[5U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[5U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[5U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[5U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[5U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[5U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[5U])))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[5U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[5U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__24(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__24\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[6U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[6U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[6U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[6U] = 0ULL;
    if ((6U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[6U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[6U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[6U];
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[6U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[6U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[6U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[6U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[6U])));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[6U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[6U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[6U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[6U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[6U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[6U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[6U])))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[6U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[6U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__25(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__25\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[7U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[7U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[7U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[7U] = 0ULL;
    if ((7U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__group_lane_count)) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[7U] 
            = ((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[7U] 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_read_byte[7U];
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[7U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[7U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[7U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[7U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[7U])));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[7U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[7U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__lane_accumulator[7U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[7U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_product[7U])))));
        if (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_feature_byte[7U]) 
                | (0x80U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_weight_byte[7U])))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[7U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_sum[7U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_overflow = 1U;
        }
    }
}

void Vtb_combined___024root___act_comb__TOP__26(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__26\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (((0x0bU == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)) 
         | (0x0cU == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)))) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_point_y 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_y;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_point_x 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_x;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_input_channel = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_kernel_y = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_kernel_x = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_reduction_index = 0U;
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_enable = 1U;
    } else if ((0x0dU == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state))) {
        if ((((((IData)(1U) + vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_reduction_index) 
               < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_latched) 
              & (~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_bad_argument))) 
             & (~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_overflow)))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_point_y 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_y;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_point_x 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_point_scan_x;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_input_channel 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_next_input_channel;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_kernel_y 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_next_kernel_y;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_kernel_x 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_next_kernel_x;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_reduction_index 
                = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_next_reduction_index;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_enable = 1U;
        }
    }
    if (((0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_kernel_area) 
         & (0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_width))) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_input_y 
            = (((((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_y)) 
                  * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_y_latched))) 
                 + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_point_y)) 
                    * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_y_latched)))) 
                + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_kernel_y))) 
               - (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__pad_top_latched)));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_input_x 
            = (((((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__tile_start_x)) 
                  * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_x_latched))) 
                 + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_point_x)) 
                    * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_x_latched)))) 
                + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_kernel_x))) 
               - (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__pad_left_latched)));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_tap_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_input_y) 
                 & VL_LTS_IQQ(64, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_input_y, (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_input_x)) 
               & VL_LTS_IQQ(64, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_input_x, (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_width_latched))));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_feature_index_wide 
            = (((((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_input_channel)) 
                  * vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_plane_bytes) 
                 + ((((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_point_y)) 
                      * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_y_latched))) 
                     + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_kernel_y))) 
                    * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_width)))) 
                + ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_point_x)) 
                   * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_x_latched)))) 
               + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_kernel_x)));
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_feature_index 
            = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__compute_read_feature_index_wide);
    }
}

void Vtb_combined___024root___act_comb__TOP__27(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__27\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mapped_response_error = 6U;
    if ((0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_error))) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mapped_response_error = 0U;
    } else if ((((1U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_error)) 
                 | (2U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_error))) 
                | (6U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_error)))) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mapped_response_error 
            = vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_error;
    }
    if ((((3U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)) 
          & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_index 
             < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__patch_byte_count)) 
         & (~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_in_bounds)))) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_advance = 1U;
    } else if ((((5U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__state)) 
                 & (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__backend_rsp_valid)) 
                & (0U == (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__mapped_response_error)))) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__feature_scan_advance = 1U;
    }
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_element_plane 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_channels_latched)) 
           * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_height_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_element_plane 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_channels_latched)) 
           * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_element_product 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_element_plane)) 
           * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_width_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_element_product 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_element_plane)) 
           * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_elements_wide[0U] 
        = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_element_product);
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_elements_wide[1U] 
        = (IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_element_product 
                   >> 0x00000020U));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_elements_wide[2U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_elements_wide[3U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_elements_wide[0U] 
        = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_element_product);
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_elements_wide[1U] 
        = (IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_element_product 
                   >> 0x00000020U));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_elements_wide[2U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_elements_wide[3U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_plane_narrow 
        = (0x03ffffffU & ((0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_channels_latched) 
                          * (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_height_latched)));
}

void Vtb_combined___024root___act_comb__TOP__28(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__28\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*25:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_narrow;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_narrow = 0;
    VlWide<4>/*127:0*/ __Vtemp_1;
    VlWide<4>/*127:0*/ __Vtemp_2;
    VlWide<4>/*127:0*/ __Vtemp_3;
    VlWide<4>/*127:0*/ __Vtemp_4;
    VlWide<4>/*127:0*/ __Vtemp_5;
    VlWide<4>/*127:0*/ __Vtemp_6;
    VlWide<4>/*127:0*/ __Vtemp_7;
    VlWide<4>/*127:0*/ __Vtemp_8;
    // Body
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_narrow 
        = (0x03ffffffU & ((0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_plane_narrow) 
                          * (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_width_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_bad 
        = (((((0x00001200U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_channels_latched) 
              | (0x00001200U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_height_latched)) 
             | (0x00001200U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_width_latched)) 
            | (0x00001200U < vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_plane_narrow)) 
           | (0x00001200U < tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_narrow));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_wide[0U] 
        = tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_narrow;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_wide[1U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_wide[2U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_wide[3U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__expected_weight_bytes_narrow 
        = (0x00001fffffffffffULL & ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_channels_latched)) 
                                    * (QData)((IData)(
                                                      (0x00001fffU 
                                                       & tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_narrow)))));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__expected_weight_bytes_wide[0U] 
        = (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__expected_weight_bytes_narrow);
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__expected_weight_bytes_wide[1U] 
        = (IData)((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__expected_weight_bytes_narrow 
                   >> 0x00000020U));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__expected_weight_bytes_wide[2U] = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__expected_weight_bytes_wide[3U] = 0U;
    __Vtemp_1[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_base_latched;
    __Vtemp_1[1U] = 0U;
    __Vtemp_1[2U] = 0U;
    __Vtemp_1[3U] = 0U;
    __Vtemp_2[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_length_latched;
    __Vtemp_2[1U] = 0U;
    __Vtemp_2[2U] = 0U;
    __Vtemp_2[3U] = 0U;
    VL_ADD_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_end_wide, __Vtemp_1, __Vtemp_2);
    __Vtemp_3[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_base_latched;
    __Vtemp_3[1U] = 0U;
    __Vtemp_3[2U] = 0U;
    __Vtemp_3[3U] = 0U;
    __Vtemp_4[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_length_latched;
    __Vtemp_4[1U] = 0U;
    __Vtemp_4[2U] = 0U;
    __Vtemp_4[3U] = 0U;
    VL_ADD_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_end_wide, __Vtemp_3, __Vtemp_4);
    __Vtemp_5[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_package_base_latched;
    __Vtemp_5[1U] = 0U;
    __Vtemp_5[2U] = 0U;
    __Vtemp_5[3U] = 0U;
    __Vtemp_6[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_package_length_latched;
    __Vtemp_6[1U] = 0U;
    __Vtemp_6[2U] = 0U;
    __Vtemp_6[3U] = 0U;
    VL_ADD_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_package_end_wide, __Vtemp_5, __Vtemp_6);
    __Vtemp_7[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__quantized_weight_offset_latched;
    __Vtemp_7[1U] = 0U;
    __Vtemp_7[2U] = 0U;
    __Vtemp_7[3U] = 0U;
    __Vtemp_8[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__quantized_weight_bytes_latched;
    __Vtemp_8[1U] = 0U;
    __Vtemp_8[2U] = 0U;
    __Vtemp_8[3U] = 0U;
    VL_ADD_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__quantized_weight_end_wide, __Vtemp_7, __Vtemp_8);
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_numerator 
        = (((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_height_latched)) 
            + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__pad_top_latched))) 
           + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__pad_bottom_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_numerator 
        = (((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_width_latched)) 
            + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__pad_left_latched))) 
           + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__pad_right_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_shape_span 
        = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_numerator 
           - (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_height_latched)));
}

void Vtb_combined___024root___act_comb__TOP__29(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__29\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*2:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_delta_y;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_delta_y = 0;
    // Body
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_shape_span 
        = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_numerator 
           - (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_width_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_shape_product 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched)) 
           * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_y_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_shape_product 
        = ((QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched)) 
           * (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_x_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_span_plus_stride 
        = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_shape_span 
           + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_y_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_span_plus_stride 
        = (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_shape_span 
           + (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_x_latched)));
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_delta_y 
        = ((0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched)
            ? 0U : ((8U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched)
                     ? (7U & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched 
                              - (IData)(1U))) : 7U));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_delta_x 
        = ((0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched)
            ? 0U : ((8U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched)
                     ? (7U & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched 
                              - (IData)(1U))) : 7U));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_height_narrow 
        = (0x0007ffffU & (((IData)(tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_delta_y) 
                           * (0x0000ffffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_y_latched)) 
                          + (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_height_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_width_narrow 
        = (0x0007ffffU & (((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_delta_x) 
                           * (0x0000ffffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_x_latched)) 
                          + (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_width_latched)));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_height_bad 
        = ((((0U != (IData)(tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_delta_y)) 
             & (0U != (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_y_latched 
                       >> 0x10U))) | (0U != (7U & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_height_narrow 
                                                   >> 0x10U)))) 
           | (0xc800U < (0x0000ffffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_height_narrow)));
}

void Vtb_combined___024root___act_comb__TOP__30(Vtb_combined___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_combined___024root___act_comb__TOP__30\n"); );
    Vtb_combined__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_plane_narrow;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_plane_narrow = 0;
    IData/*28:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_bytes_narrow;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_bytes_narrow = 0;
    CData/*0:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_width_bad;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_width_bad = 0;
    CData/*0:0*/ tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_bad;
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_bad = 0;
    VlWide<4>/*127:0*/ __Vtemp_1;
    VlWide<4>/*127:0*/ __Vtemp_2;
    VlWide<4>/*127:0*/ __Vtemp_3;
    VlWide<4>/*127:0*/ __Vtemp_4;
    VlWide<4>/*127:0*/ __Vtemp_5;
    VlWide<4>/*127:0*/ __Vtemp_6;
    VlWide<4>/*127:0*/ __Vtemp_7;
    VlWide<4>/*127:0*/ __Vtemp_8;
    // Body
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_width_bad 
        = ((((0U != (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_delta_x)) 
             & (0U != (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_x_latched 
                       >> 0x10U))) | (0U != (7U & (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_width_narrow 
                                                   >> 0x10U)))) 
           | (0xc800U < (0x0000ffffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_width_narrow)));
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_plane_narrow 
        = ((0x0000ffffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_height_narrow) 
           * (0x0000ffffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_width_narrow));
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_bytes_narrow 
        = (0x1fffffffU & ((0x0000ffffU & tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_plane_narrow) 
                          * (0x00001fffU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_channels_latched)));
    tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_bad 
        = ((((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_height_bad) 
             | (IData)(tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_width_bad)) 
            | (0U != (tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_plane_narrow 
                      >> 0x10U))) | (0x0000c800U < tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_bytes_narrow));
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__validation_ok = 0U;
    vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__validation_error = 1U;
    if ((1U & (((((((((((((((((((((~ (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__buffer_owner_pl)) 
                                  | (1U < (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__activation_mode_latched))) 
                                 | (1U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_batch_count_latched)) 
                                | (1U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_batch_count_latched)) 
                               | (0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_batch_latched)) 
                              | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_channels_latched)) 
                             | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_height_latched)) 
                            | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_width_latched)) 
                           | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_channels_latched)) 
                          | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_latched)) 
                         | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_latched)) 
                        | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_height_latched)) 
                       | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_width_latched)) 
                      | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_y_latched)) 
                     | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__stride_x_latched)) 
                    | (1U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__groups_latched)) 
                   | (0U != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__padding_latched)) 
                  | (IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__reduction_count_bad)) 
                 | (0x00000026U <= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched)) 
                | ((0x00000026U > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched) 
                   & (0U != ((0x25U >= (0x0000003fU 
                                        & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched))
                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OP
                             [(0x0000003fU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched)]
                              : 0U)))) | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched 
                                          != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_layer_index_latched)))) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__validation_error 
            = (((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched 
                 != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_layer_index_latched) 
                | (0x00000026U <= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched))
                ? 2U : 1U);
    } else if ((IData)(((((((0ULL != (0xffffffff00000000ULL 
                                      & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_element_plane)) 
                            | (0ULL != (0xffffffff00000000ULL 
                                        & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_element_product))) 
                           | (0ULL != (0xffffffff00000000ULL 
                                       & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_element_plane))) 
                          | (0ULL != (0xffffffff00000000ULL 
                                      & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_element_product))) 
                         | (0ULL != (0x00001fff00000000ULL 
                                     & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__expected_weight_bytes_narrow))) 
                        | (((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_length_latched 
                             != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_elements_wide[0U]) 
                            | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_length_latched 
                               != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_elements_wide[0U])) 
                           | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__quantized_weight_bytes_latched 
                              != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__expected_weight_bytes_wide[0U]))))) {
        vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__validation_error = 3U;
    } else {
        __Vtemp_1[0U] = 0U;
        __Vtemp_1[1U] = 1U;
        __Vtemp_1[2U] = 0U;
        __Vtemp_1[3U] = 0U;
        __Vtemp_2[0U] = 0U;
        __Vtemp_2[1U] = 1U;
        __Vtemp_2[2U] = 0U;
        __Vtemp_2[3U] = 0U;
        __Vtemp_3[0U] = 0U;
        __Vtemp_3[1U] = 1U;
        __Vtemp_3[2U] = 0U;
        __Vtemp_3[3U] = 0U;
        __Vtemp_4[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_package_length_latched;
        __Vtemp_4[1U] = 0U;
        __Vtemp_4[2U] = 0U;
        __Vtemp_4[3U] = 0U;
        __Vtemp_5[0U] = 0x00000c5cU;
        __Vtemp_5[1U] = 0U;
        __Vtemp_5[2U] = 0U;
        __Vtemp_5[3U] = 0U;
        __Vtemp_6[0U] = ((0x25U >= (0x0000003fU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched))
                          ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                         [(0x0000003fU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched)]
                          : 0U);
        __Vtemp_6[1U] = 0U;
        __Vtemp_6[2U] = 0U;
        __Vtemp_6[3U] = 0U;
        __Vtemp_7[0U] = vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_channels_latched;
        __Vtemp_7[1U] = 0U;
        __Vtemp_7[2U] = 0U;
        __Vtemp_7[3U] = 0U;
        VL_ADD_W(4, __Vtemp_8, __Vtemp_6, __Vtemp_7);
        if ((((((((VL_LT_W(4, __Vtemp_1, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__input_end_wide) 
                   | VL_LT_W(4, __Vtemp_2, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_end_wide)) 
                  | VL_LT_W(4, __Vtemp_3, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_package_end_wide)) 
                 | (0U == vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__weight_package_length_latched)) 
                | VL_GT_W(4, vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__quantized_weight_end_wide, __Vtemp_4)) 
               | (((0x25U >= (0x0000003fU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched))
                    ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                   [(0x0000003fU & vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__layer_index_latched)]
                    : 0U) != vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_channels_latched)) 
              | VL_LT_W(4, __Vtemp_5, __Vtemp_8)) | (IData)(tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__full_tile_patch_bad))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__validation_error = 2U;
        } else if (((((((vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_numerator 
                         < (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_height_latched))) 
                        | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_numerator 
                           < (QData)((IData)(vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__kernel_width_latched)))) 
                       | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_shape_product 
                          <= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_shape_span)) 
                      | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_shape_product 
                         > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_height_span_plus_stride)) 
                     | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_shape_product 
                        <= vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_shape_span)) 
                    | (vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_shape_product 
                       > vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__output_width_span_plus_stride))) {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__validation_error = 1U;
        } else {
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__validation_ok = 1U;
            vlSelfRef.tb_combined__DOT__boundary_test__DOT__u_candidate__DOT__validation_error = 0U;
        }
    }
}
