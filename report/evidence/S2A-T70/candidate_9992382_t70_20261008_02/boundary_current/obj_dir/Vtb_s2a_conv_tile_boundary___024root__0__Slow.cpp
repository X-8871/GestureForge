// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_conv_tile_boundary.h for the primary calling header

#include "Vtb_s2a_conv_tile_boundary__pch.h"

void Vtb_s2a_conv_tile_boundary___024root___timing_ready(Vtb_s2a_conv_tile_boundary___024root* vlSelf);

VL_ATTR_COLD void Vtb_s2a_conv_tile_boundary___024root___eval_static(Vtb_s2a_conv_tile_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___eval_static\n"); );
    Vtb_s2a_conv_tile_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    {
        // Inlined CFunc: _eval_static__TOP
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__clk = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__hard_reset = 1U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__start_valid = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_valid = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_data = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_error = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__layer_id = 0x0000001dU;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__mode = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__cycles = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__reads = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__feature_reads = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__weight_reads = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__writes = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__wait_count = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__waiting = 0U;
        vlSelfRef.tb_s2a_conv_tile_boundary__DOT__injected = 0U;
    }
    vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_conv_tile_boundary__DOT__clk__0 = 0U;
    Vtb_s2a_conv_tile_boundary___024root___timing_ready(vlSelf);
    do {
        vlSelfRef.__VactTriggeredAcc[vlSelfRef.__Vi] 
            = vlSelfRef.__VactTriggered[vlSelfRef.__Vi];
        vlSelfRef.__Vi = ((IData)(1U) + vlSelfRef.__Vi);
    } while ((0U >= vlSelfRef.__Vi));
}

VL_ATTR_COLD void Vtb_s2a_conv_tile_boundary___024root___eval_final(Vtb_s2a_conv_tile_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___eval_final\n"); );
    Vtb_s2a_conv_tile_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_conv_tile_boundary___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG
VL_ATTR_COLD bool Vtb_s2a_conv_tile_boundary___024root___eval_phase__stl(Vtb_s2a_conv_tile_boundary___024root* vlSelf);

VL_ATTR_COLD void Vtb_s2a_conv_tile_boundary___024root___eval_settle(Vtb_s2a_conv_tile_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___eval_settle\n"); );
    Vtb_s2a_conv_tile_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VstlIterCount;
    // Body
    __VstlIterCount = 0U;
    vlSelfRef.__VstlFirstIteration = 1U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VstlIterCount)))) {
#ifdef VL_DEBUG
            Vtb_s2a_conv_tile_boundary___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
#endif
            VL_FATAL_MT("source\\tb_s2a_conv_tile_boundary.sv", 3, "", "DIDNOTCONVERGE: Settle region did not converge after '--converge-limit' of 10000 tries");
        }
        __VstlIterCount = ((IData)(1U) + __VstlIterCount);
        vlSelfRef.__VstlPhaseResult = Vtb_s2a_conv_tile_boundary___024root___eval_phase__stl(vlSelf);
        vlSelfRef.__VstlFirstIteration = 0U;
    } while (vlSelfRef.__VstlPhaseResult);
}

VL_ATTR_COLD bool Vtb_s2a_conv_tile_boundary___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_conv_tile_boundary___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___dump_triggers__stl\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_s2a_conv_tile_boundary___024root___trigger_anySet__stl(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: Internal 'stl' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD bool Vtb_s2a_conv_tile_boundary___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___trigger_anySet__stl\n"); );
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

extern const VlWide<10>/*319:0*/ Vtb_s2a_conv_tile_boundary__ConstPool__CONST_hb4617e49_0;
extern const VlUnpacked<IData/*31:0*/, 5> Vtb_s2a_conv_tile_boundary__ConstPool__TABLE_hc6a14c36_0;

VL_ATTR_COLD void Vtb_s2a_conv_tile_boundary___024root___stl_sequent__TOP__0(Vtb_s2a_conv_tile_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___stl_sequent__TOP__0\n"); );
    Vtb_s2a_conv_tile_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT____VlemCall_0__stalls;
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
    IData/*31:0*/ tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_index;
    tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_index = 0;
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
    VlWide<4>/*127:0*/ __Vtemp_44;
    VlWide<4>/*127:0*/ __Vtemp_45;
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
    IData/*31:0*/ __Vtemp_61;
    // Body
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_byte_lane 
        = (3U & (0x00030210U >> ((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_strobe_latched) 
                                 << 1U)));
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__hard_reset)) 
           & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__state)));
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rstrb = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__wstrb = 0U;
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
    __Vtemp_5[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_batch_count_latched;
    __Vtemp_5[1U] = 0U;
    __Vtemp_5[2U] = 0U;
    __Vtemp_5[3U] = 0U;
    __Vtemp_6[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_channels_latched;
    __Vtemp_6[1U] = 0U;
    __Vtemp_6[2U] = 0U;
    __Vtemp_6[3U] = 0U;
    VL_MUL_W(4, __Vtemp_7, __Vtemp_5, __Vtemp_6);
    __Vtemp_8[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_height_latched;
    __Vtemp_8[1U] = 0U;
    __Vtemp_8[2U] = 0U;
    __Vtemp_8[3U] = 0U;
    VL_MUL_W(4, __Vtemp_9, __Vtemp_7, __Vtemp_8);
    __Vtemp_10[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_width_latched;
    __Vtemp_10[1U] = 0U;
    __Vtemp_10[2U] = 0U;
    __Vtemp_10[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_elements_wide, __Vtemp_9, __Vtemp_10);
    __Vtemp_11[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_batch_count_latched;
    __Vtemp_11[1U] = 0U;
    __Vtemp_11[2U] = 0U;
    __Vtemp_11[3U] = 0U;
    __Vtemp_12[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched;
    __Vtemp_12[1U] = 0U;
    __Vtemp_12[2U] = 0U;
    __Vtemp_12[3U] = 0U;
    VL_MUL_W(4, __Vtemp_13, __Vtemp_11, __Vtemp_12);
    __Vtemp_14[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched;
    __Vtemp_14[1U] = 0U;
    __Vtemp_14[2U] = 0U;
    __Vtemp_14[3U] = 0U;
    VL_MUL_W(4, __Vtemp_15, __Vtemp_13, __Vtemp_14);
    __Vtemp_16[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched;
    __Vtemp_16[1U] = 0U;
    __Vtemp_16[2U] = 0U;
    __Vtemp_16[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_elements_wide, __Vtemp_15, __Vtemp_16);
    __Vtemp_17[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched;
    __Vtemp_17[1U] = 0U;
    __Vtemp_17[2U] = 0U;
    __Vtemp_17[3U] = 0U;
    __Vtemp_18[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_channels_latched;
    __Vtemp_18[1U] = 0U;
    __Vtemp_18[2U] = 0U;
    __Vtemp_18[3U] = 0U;
    VL_MUL_W(4, __Vtemp_19, __Vtemp_17, __Vtemp_18);
    __Vtemp_20[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched;
    __Vtemp_20[1U] = 0U;
    __Vtemp_20[2U] = 0U;
    __Vtemp_20[3U] = 0U;
    VL_MUL_W(4, __Vtemp_21, __Vtemp_19, __Vtemp_20);
    __Vtemp_22[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched;
    __Vtemp_22[1U] = 0U;
    __Vtemp_22[2U] = 0U;
    __Vtemp_22[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__expected_weight_bytes_wide, __Vtemp_21, __Vtemp_22);
    __Vtemp_23[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_channels_latched;
    __Vtemp_23[1U] = 0U;
    __Vtemp_23[2U] = 0U;
    __Vtemp_23[3U] = 0U;
    __Vtemp_24[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched;
    __Vtemp_24[1U] = 0U;
    __Vtemp_24[2U] = 0U;
    __Vtemp_24[3U] = 0U;
    VL_MUL_W(4, __Vtemp_25, __Vtemp_23, __Vtemp_24);
    __Vtemp_26[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched;
    __Vtemp_26[1U] = 0U;
    __Vtemp_26[2U] = 0U;
    __Vtemp_26[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_wide, __Vtemp_25, __Vtemp_26);
    __Vtemp_27[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_base_latched;
    __Vtemp_27[1U] = 0U;
    __Vtemp_27[2U] = 0U;
    __Vtemp_27[3U] = 0U;
    __Vtemp_28[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_length_latched;
    __Vtemp_28[1U] = 0U;
    __Vtemp_28[2U] = 0U;
    __Vtemp_28[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_end_wide, __Vtemp_27, __Vtemp_28);
    __Vtemp_29[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_base_latched;
    __Vtemp_29[1U] = 0U;
    __Vtemp_29[2U] = 0U;
    __Vtemp_29[3U] = 0U;
    __Vtemp_30[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_length_latched;
    __Vtemp_30[1U] = 0U;
    __Vtemp_30[2U] = 0U;
    __Vtemp_30[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_end_wide, __Vtemp_29, __Vtemp_30);
    __Vtemp_31[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_base_latched;
    __Vtemp_31[1U] = 0U;
    __Vtemp_31[2U] = 0U;
    __Vtemp_31[3U] = 0U;
    __Vtemp_32[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_length_latched;
    __Vtemp_32[1U] = 0U;
    __Vtemp_32[2U] = 0U;
    __Vtemp_32[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_end_wide, __Vtemp_31, __Vtemp_32);
    __Vtemp_33[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_offset_latched;
    __Vtemp_33[1U] = 0U;
    __Vtemp_33[2U] = 0U;
    __Vtemp_33[3U] = 0U;
    __Vtemp_34[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_bytes_latched;
    __Vtemp_34[1U] = 0U;
    __Vtemp_34[2U] = 0U;
    __Vtemp_34[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_end_wide, __Vtemp_33, __Vtemp_34);
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
        __Vtemp_35[0U] = (((8U > vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched)
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched
                            : 8U) - (IData)(1U));
        __Vtemp_35[1U] = 0U;
        __Vtemp_35[2U] = 0U;
        __Vtemp_35[3U] = 0U;
        __Vtemp_36[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched;
        __Vtemp_36[1U] = 0U;
        __Vtemp_36[2U] = 0U;
        __Vtemp_36[3U] = 0U;
        VL_MUL_W(4, __Vtemp_37, __Vtemp_35, __Vtemp_36);
        __Vtemp_38[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched;
        __Vtemp_38[1U] = 0U;
        __Vtemp_38[2U] = 0U;
        __Vtemp_38[3U] = 0U;
        VL_ADD_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_height_wide, __Vtemp_37, __Vtemp_38);
        __Vtemp_39[0U] = (((8U > vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched)
                            ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched
                            : 8U) - (IData)(1U));
        __Vtemp_39[1U] = 0U;
        __Vtemp_39[2U] = 0U;
        __Vtemp_39[3U] = 0U;
        __Vtemp_40[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched;
        __Vtemp_40[1U] = 0U;
        __Vtemp_40[2U] = 0U;
        __Vtemp_40[3U] = 0U;
        VL_MUL_W(4, __Vtemp_41, __Vtemp_39, __Vtemp_40);
        __Vtemp_42[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched;
        __Vtemp_42[1U] = 0U;
        __Vtemp_42[2U] = 0U;
        __Vtemp_42[3U] = 0U;
        VL_ADD_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_width_wide, __Vtemp_41, __Vtemp_42);
        VL_MUL_W(4, __Vtemp_43, tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_height_wide, tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_width_wide);
        __Vtemp_44[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_channels_latched;
        __Vtemp_44[1U] = 0U;
        __Vtemp_44[2U] = 0U;
        __Vtemp_44[3U] = 0U;
        VL_MUL_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_bytes_wide, __Vtemp_43, __Vtemp_44);
    }
    __Vtemp_45[0U] = ((8U > vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched)
                       ? vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched
                       : 8U);
    __Vtemp_45[1U] = 0U;
    __Vtemp_45[2U] = 0U;
    __Vtemp_45[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_weight_group_bytes_wide, __Vtemp_45, vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_wide);
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__validation_ok = 0U;
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__validation_error = 1U;
    __Vtemp_47[0U] = 0x00001200U;
    __Vtemp_47[1U] = 0U;
    __Vtemp_47[2U] = 0U;
    __Vtemp_47[3U] = 0U;
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
            | VL_LT_W(4, __Vtemp_47, vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_wide)) 
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
        __Vtemp_48[0U] = 0xffffffffU;
        __Vtemp_48[1U] = 0U;
        __Vtemp_48[2U] = 0U;
        __Vtemp_48[3U] = 0U;
        __Vtemp_49[0U] = 0xffffffffU;
        __Vtemp_49[1U] = 0U;
        __Vtemp_49[2U] = 0U;
        __Vtemp_49[3U] = 0U;
        __Vtemp_50[0U] = 0xffffffffU;
        __Vtemp_50[1U] = 0U;
        __Vtemp_50[2U] = 0U;
        __Vtemp_50[3U] = 0U;
        if ((((((VL_LT_W(4, __Vtemp_48, tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_elements_wide) 
                 | (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_length_latched 
                    != tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_elements_wide[0U])) 
                | VL_LT_W(4, __Vtemp_49, vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_elements_wide)) 
               | (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_length_latched 
                  != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_elements_wide[0U])) 
              | VL_LT_W(4, __Vtemp_50, tb_s2a_conv_tile_boundary__DOT__dut__DOT__expected_weight_bytes_wide)) 
             | (vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_bytes_latched 
                != tb_s2a_conv_tile_boundary__DOT__dut__DOT__expected_weight_bytes_wide[0U]))) {
            vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__validation_error = 3U;
        } else {
            __Vtemp_51[0U] = 0U;
            __Vtemp_51[1U] = 1U;
            __Vtemp_51[2U] = 0U;
            __Vtemp_51[3U] = 0U;
            __Vtemp_52[0U] = 0U;
            __Vtemp_52[1U] = 1U;
            __Vtemp_52[2U] = 0U;
            __Vtemp_52[3U] = 0U;
            __Vtemp_53[0U] = 0U;
            __Vtemp_53[1U] = 1U;
            __Vtemp_53[2U] = 0U;
            __Vtemp_53[3U] = 0U;
            __Vtemp_54[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_length_latched;
            __Vtemp_54[1U] = 0U;
            __Vtemp_54[2U] = 0U;
            __Vtemp_54[3U] = 0U;
            __Vtemp_55[0U] = 0x00000c5cU;
            __Vtemp_55[1U] = 0U;
            __Vtemp_55[2U] = 0U;
            __Vtemp_55[3U] = 0U;
            __Vtemp_56[0U] = ((0x25U >= (0x0000003fU 
                                         & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched))
                               ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                              [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched)]
                               : 0U);
            __Vtemp_56[1U] = 0U;
            __Vtemp_56[2U] = 0U;
            __Vtemp_56[3U] = 0U;
            __Vtemp_57[0U] = vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched;
            __Vtemp_57[1U] = 0U;
            __Vtemp_57[2U] = 0U;
            __Vtemp_57[3U] = 0U;
            VL_ADD_W(4, __Vtemp_58, __Vtemp_56, __Vtemp_57);
            __Vtemp_59[0U] = 0x0000c800U;
            __Vtemp_59[1U] = 0U;
            __Vtemp_59[2U] = 0U;
            __Vtemp_59[3U] = 0U;
            __Vtemp_60[0U] = 0x00009000U;
            __Vtemp_60[1U] = 0U;
            __Vtemp_60[2U] = 0U;
            __Vtemp_60[3U] = 0U;
            if (((((((((VL_LT_W(4, __Vtemp_51, tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_end_wide) 
                        | VL_LT_W(4, __Vtemp_52, tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_end_wide)) 
                       | VL_LT_W(4, __Vtemp_53, tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_end_wide)) 
                      | (0U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_length_latched)) 
                     | VL_GT_W(4, tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_end_wide, __Vtemp_54)) 
                    | (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                        [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched)]
                         : 0U) != vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched)) 
                   | VL_LT_W(4, __Vtemp_55, __Vtemp_58)) 
                  | VL_LT_W(4, __Vtemp_59, tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_tile_patch_bytes_wide)) 
                 | VL_LT_W(4, __Vtemp_60, tb_s2a_conv_tile_boundary__DOT__dut__DOT__full_weight_group_bytes_wide))) {
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
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_base_latched)) 
           + vlSelfRef.tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_byte_offset_wide);
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
    __Vtemp_61 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, __Vfunc_tb_s2a_conv_tile_boundary__DOT__stalls__0__n, (IData)(5U)), Vtb_s2a_conv_tile_boundary__ConstPool__CONST_hb4617e49_0);
    tb_s2a_conv_tile_boundary__DOT____VlemCall_0__stalls 
        = Vtb_s2a_conv_tile_boundary__ConstPool__TABLE_hc6a14c36_0
        [__Vtemp_61];
    vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_ready 
        = ((((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__req_valid) 
             & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__hard_reset))) 
            & (~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__rsp_valid))) 
           & (((IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__waiting) 
               & (0U == vlSelfRef.tb_s2a_conv_tile_boundary__DOT__wait_count)) 
              | ((~ (IData)(vlSelfRef.tb_s2a_conv_tile_boundary__DOT__waiting)) 
                 & (0U == tb_s2a_conv_tile_boundary__DOT____VlemCall_0__stalls))));
}

VL_ATTR_COLD bool Vtb_s2a_conv_tile_boundary___024root___eval_phase__stl(Vtb_s2a_conv_tile_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___eval_phase__stl\n"); );
    Vtb_s2a_conv_tile_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VstlExecute;
    // Body
    {
        // Inlined CFunc: _eval_triggers_vec__stl
        vlSelfRef.__VstlTriggered[0U] = ((0xfffffffffffffffeULL 
                                          & vlSelfRef.__VstlTriggered[0U]) 
                                         | (IData)((IData)(vlSelfRef.__VstlFirstIteration)));
    }
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vtb_s2a_conv_tile_boundary___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
    }
#endif
    __VstlExecute = Vtb_s2a_conv_tile_boundary___024root___trigger_anySet__stl(vlSelfRef.__VstlTriggered);
    if (__VstlExecute) {
        {
            // Inlined CFunc: _eval_stl
            if ((1ULL & vlSelfRef.__VstlTriggered[0U])) {
                Vtb_s2a_conv_tile_boundary___024root___stl_sequent__TOP__0(vlSelf);
            }
        }
    }
    return (__VstlExecute);
}

bool Vtb_s2a_conv_tile_boundary___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_conv_tile_boundary___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___dump_triggers__act\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_s2a_conv_tile_boundary___024root___trigger_anySet__act(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: @(posedge tb_s2a_conv_tile_boundary.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 1U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 1 is active: @(negedge tb_s2a_conv_tile_boundary.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 2U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 2 is active: @([true] __VdlySched.awaitingCurrentTime())\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vtb_s2a_conv_tile_boundary___024root___ctor_var_reset(Vtb_s2a_conv_tile_boundary___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_boundary___024root___ctor_var_reset\n"); );
    Vtb_s2a_conv_tile_boundary__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5173145512783234247ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10620268297303272077ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__req_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15636999730146324949ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__req_write = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13887920290030821581ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__rstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 14308013860989053292ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 12111674120414963467ull);
    for (int __Vi0 = 0; __Vi0 < 3; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__class_count[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6827586420561359288ull);
    }
    for (int __Vi0 = 0; __Vi0 < 3; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__class_stalls[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14810389240220370654ull);
    }
    vlSelf->tb_s2a_conv_tile_boundary__DOT__selected_lane = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3915529779466684166ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__byte_address = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8431775278917813820ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__index_work = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3645651582344946940ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__transfer_class = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2470770237367187352ull);
    for (int __Vi0 = 0; __Vi0 < 15360; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__weights[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 4050694342266801878ull);
    }
    for (int __Vi0 = 0; __Vi0 < 20280; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__expected[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 11568499700974441365ull);
    }
    for (int __Vi0 = 0; __Vi0 < 173056; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__features[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 14234032700425919688ull);
    }
    for (int __Vi0 = 0; __Vi0 < 20280; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__seen[__Vi0] = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 446822986878348153ull);
    }
    vlSelf->tb_s2a_conv_tile_boundary__DOT__held_addr = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14825476501004677672ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__held_data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 859803266273237356ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__held_write = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7547167217123612195ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__held_rs = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 9080848823469430337ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__held_ws = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 5006839925001305125ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__expected_feature = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12649608102210908203ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__expected_weight = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13803466275781023971ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__expected_output = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16264400918648938481ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__state = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 5025955802157292506ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8104617878852661121ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1252887104947043150ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10628958722271078146ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17022630098196776503ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 54848848934922632ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5796655853902702579ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8868507472543176454ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__input_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 134446875692773693ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17575215701134048228ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7212930296398839980ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1588000866352549655ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11191801489100421558ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13282517323244754218ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13453501884292335572ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15552683350268126916ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__kernel_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11448079383418753252ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_y_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4893482684842428087ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__stride_x_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6553710090279239211ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_left_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14593113741135140705ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_right_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12461153865123601333ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_top_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13698694223149426995ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__pad_bottom_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17945685173303237574ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__groups_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12015005737970866891ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__padding_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15319363927475273399ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12867138395588081384ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_package_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14623978267731818872ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_offset_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15356592648289078496ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__quantized_weight_bytes_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14530634919730847513ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_batch_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18264706817068951033ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__activation_mode_latched = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 12993683167717008999ull);
    for (int __Vi0 = 0; __Vi0 < 51200; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_patch[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 6513346795733096174ull);
    }
    for (int __Vi0 = 0; __Vi0 < 512; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_block[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 92435886108528178ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_accumulator[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14098063857506566475ull);
    }
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_data = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 8621268540705967611ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_read_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16062708518965454433ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_read_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 14583036516623373641ull);
    }
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3327442806590096800ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_group_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12424609931043601008ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7106728430246549752ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_start_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5723634349016845505ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17230721273133423348ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4276500680941584850ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18048259005147839ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14398994471625948886ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__patch_byte_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5618812774209255386ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__tile_point_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4421405158495509446ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__group_lane_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 250575481809693737ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8715696177871772503ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12358096890965754005ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17081907006617230262ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1837897321371103160ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9976068249395938816ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_point_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3510441613663832060ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11198496229895726142ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5440832760926739787ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9383097107903187702ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1694732875327684291ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_strobe_latched = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 18334829747954047441ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_wdata_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5708247047846257456ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 16299330125252132015ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_elements_wide, __VscopeHash, 11684677557721444098ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__reduction_count_wide, __VscopeHash, 1628554490969641246ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__validation_ok = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10044021248345878073ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__validation_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 16050124103718336047ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14094740753176613770ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14185999484051442438ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12432009516720445920ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_advance = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4773083852623765535ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_scan_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2779067968115548265ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__feature_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 8065166136998475980ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__weight_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 16700230996531128821ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_input_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13946992855115531032ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11686428991372837348ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17239243187695213073ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_next_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 556029919025264980ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1119502457167822453ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_tap_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 376750444808787156ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_feature_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4081761168167515061ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_read_enable = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4646642534282237440ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_feature_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 482278229118246572ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_weight_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 11419923726800445655ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_product[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 2427016165206569320ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_sum[__Vi0] = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 149146834806041992ull);
    }
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_bad_argument = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10126873768680325032ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__compute_overflow = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3182078254973092443ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_lane = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3537947960629143119ull);
    VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_parameter, __VscopeHash, 7382162145376768591ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_bias = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2601683430603850433ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__mq_prefetch_invalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4327587450370452170ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_mq_parameter[__Vi0], __VscopeHash, 8859503730298811471ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__lane_bias[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10428580069964264080ull);
    }
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__requant_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12791873952046395939ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__requantized_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 3718117446454462197ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12588847702825134199ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_point_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13096568542795724154ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_byte_offset_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 5455559904194119699ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__output_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 334874316560633083ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 663657265755063612ull);
    vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__request_byte_lane = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 18189414711132429038ull);
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 3669708295568510036ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 5033760333490382173ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 10440044249723701917ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 12932247470468432266ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 1255704310549931905ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 11089047528029122819ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 14044246669445732459ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_boundary__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 13991711878233577676ull);
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VstlTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggeredAcc[__Vi0] = 0;
    }
    vlSelf->__Vtrigprevexpr___TOP__tb_s2a_conv_tile_boundary__DOT__clk__0 = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VnbaTriggered[__Vi0] = 0;
    }
    vlSelf->__Vi = 0;
}
