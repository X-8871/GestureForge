// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_conv_tile_memory.h for the primary calling header

#include "Vtb_s2a_conv_tile_memory__pch.h"

void Vtb_s2a_conv_tile_memory___024root___timing_ready(Vtb_s2a_conv_tile_memory___024root* vlSelf);

VL_ATTR_COLD void Vtb_s2a_conv_tile_memory___024root___eval_static(Vtb_s2a_conv_tile_memory___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___eval_static\n"); );
    Vtb_s2a_conv_tile_memory__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    {
        // Inlined CFunc: _eval_static__TOP
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__clk = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__hard_reset = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__abort = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__start_valid = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__req_ready = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_valid = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__rsp_data = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__layer_id = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__wait_remaining = 0xffffffffU;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__seen_count = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__total_outputs = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__case_count = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__required_cases = 0U;
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__pending_response = 0U;
    }
    vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_conv_tile_memory__DOT__clk__0 = 0U;
    Vtb_s2a_conv_tile_memory___024root___timing_ready(vlSelf);
    do {
        vlSelfRef.__VactTriggeredAcc[vlSelfRef.__Vi] 
            = vlSelfRef.__VactTriggered[vlSelfRef.__Vi];
        vlSelfRef.__Vi = ((IData)(1U) + vlSelfRef.__Vi);
    } while ((0U >= vlSelfRef.__Vi));
}

VL_ATTR_COLD void Vtb_s2a_conv_tile_memory___024root___eval_final(Vtb_s2a_conv_tile_memory___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___eval_final\n"); );
    Vtb_s2a_conv_tile_memory__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_conv_tile_memory___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG
VL_ATTR_COLD bool Vtb_s2a_conv_tile_memory___024root___eval_phase__stl(Vtb_s2a_conv_tile_memory___024root* vlSelf);

VL_ATTR_COLD void Vtb_s2a_conv_tile_memory___024root___eval_settle(Vtb_s2a_conv_tile_memory___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___eval_settle\n"); );
    Vtb_s2a_conv_tile_memory__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VstlIterCount;
    // Body
    __VstlIterCount = 0U;
    vlSelfRef.__VstlFirstIteration = 1U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VstlIterCount)))) {
#ifdef VL_DEBUG
            Vtb_s2a_conv_tile_memory___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
#endif
            VL_FATAL_MT("source\\tb_s2a_conv_tile_memory.sv", 3, "", "DIDNOTCONVERGE: Settle region did not converge after '--converge-limit' of 10000 tries");
        }
        __VstlIterCount = ((IData)(1U) + __VstlIterCount);
        vlSelfRef.__VstlPhaseResult = Vtb_s2a_conv_tile_memory___024root___eval_phase__stl(vlSelf);
        vlSelfRef.__VstlFirstIteration = 0U;
    } while (vlSelfRef.__VstlPhaseResult);
}

VL_ATTR_COLD bool Vtb_s2a_conv_tile_memory___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_conv_tile_memory___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___dump_triggers__stl\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_s2a_conv_tile_memory___024root___trigger_anySet__stl(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: Internal 'stl' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD bool Vtb_s2a_conv_tile_memory___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___trigger_anySet__stl\n"); );
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

VL_ATTR_COLD void Vtb_s2a_conv_tile_memory___024root___stl_sequent__TOP__0(Vtb_s2a_conv_tile_memory___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___stl_sequent__TOP__0\n"); );
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
    // Body
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_byte_lane 
        = (3U & (0x00030210U >> ((IData)(vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched) 
                                 << 1U)));
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
        __Vtemp_2[0U] = (IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude);
        __Vtemp_2[1U] = (IData)((tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude 
                                 >> 0x00000020U));
        __Vtemp_2[2U] = 0U;
        VL_NEGATE_W(3, __Vtemp_3, __Vtemp_2);
        tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value 
            = ((tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_accumulator 
                >> 0x1fU) ? (((QData)((IData)(__Vtemp_3[1U])) 
                              << 0x00000020U) | (QData)((IData)(__Vtemp_3[0U])))
                : tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_rounded_magnitude);
        vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value 
            = (VL_LTS_IQQ(64, 0x000000000000007fULL, tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value)
                ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value)
                                  ? 0x00000081U : (0x000000ffU 
                                                   & (IData)(tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_signed_value))));
    }
    __Vtemp_5[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_batch_count_latched;
    __Vtemp_5[1U] = 0U;
    __Vtemp_5[2U] = 0U;
    __Vtemp_5[3U] = 0U;
    __Vtemp_6[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched;
    __Vtemp_6[1U] = 0U;
    __Vtemp_6[2U] = 0U;
    __Vtemp_6[3U] = 0U;
    VL_MUL_W(4, __Vtemp_7, __Vtemp_5, __Vtemp_6);
    __Vtemp_8[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_height_latched;
    __Vtemp_8[1U] = 0U;
    __Vtemp_8[2U] = 0U;
    __Vtemp_8[3U] = 0U;
    VL_MUL_W(4, __Vtemp_9, __Vtemp_7, __Vtemp_8);
    __Vtemp_10[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_width_latched;
    __Vtemp_10[1U] = 0U;
    __Vtemp_10[2U] = 0U;
    __Vtemp_10[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__input_elements_wide, __Vtemp_9, __Vtemp_10);
    __Vtemp_11[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_batch_count_latched;
    __Vtemp_11[1U] = 0U;
    __Vtemp_11[2U] = 0U;
    __Vtemp_11[3U] = 0U;
    __Vtemp_12[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched;
    __Vtemp_12[1U] = 0U;
    __Vtemp_12[2U] = 0U;
    __Vtemp_12[3U] = 0U;
    VL_MUL_W(4, __Vtemp_13, __Vtemp_11, __Vtemp_12);
    __Vtemp_14[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched;
    __Vtemp_14[1U] = 0U;
    __Vtemp_14[2U] = 0U;
    __Vtemp_14[3U] = 0U;
    VL_MUL_W(4, __Vtemp_15, __Vtemp_13, __Vtemp_14);
    __Vtemp_16[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched;
    __Vtemp_16[1U] = 0U;
    __Vtemp_16[2U] = 0U;
    __Vtemp_16[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_elements_wide, __Vtemp_15, __Vtemp_16);
    __Vtemp_17[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched;
    __Vtemp_17[1U] = 0U;
    __Vtemp_17[2U] = 0U;
    __Vtemp_17[3U] = 0U;
    __Vtemp_18[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched;
    __Vtemp_18[1U] = 0U;
    __Vtemp_18[2U] = 0U;
    __Vtemp_18[3U] = 0U;
    VL_MUL_W(4, __Vtemp_19, __Vtemp_17, __Vtemp_18);
    __Vtemp_20[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched;
    __Vtemp_20[1U] = 0U;
    __Vtemp_20[2U] = 0U;
    __Vtemp_20[3U] = 0U;
    VL_MUL_W(4, __Vtemp_21, __Vtemp_19, __Vtemp_20);
    __Vtemp_22[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched;
    __Vtemp_22[1U] = 0U;
    __Vtemp_22[2U] = 0U;
    __Vtemp_22[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__expected_weight_bytes_wide, __Vtemp_21, __Vtemp_22);
    __Vtemp_23[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched;
    __Vtemp_23[1U] = 0U;
    __Vtemp_23[2U] = 0U;
    __Vtemp_23[3U] = 0U;
    __Vtemp_24[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched;
    __Vtemp_24[1U] = 0U;
    __Vtemp_24[2U] = 0U;
    __Vtemp_24[3U] = 0U;
    VL_MUL_W(4, __Vtemp_25, __Vtemp_23, __Vtemp_24);
    __Vtemp_26[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched;
    __Vtemp_26[1U] = 0U;
    __Vtemp_26[2U] = 0U;
    __Vtemp_26[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_wide, __Vtemp_25, __Vtemp_26);
    __Vtemp_27[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_base_latched;
    __Vtemp_27[1U] = 0U;
    __Vtemp_27[2U] = 0U;
    __Vtemp_27[3U] = 0U;
    __Vtemp_28[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_length_latched;
    __Vtemp_28[1U] = 0U;
    __Vtemp_28[2U] = 0U;
    __Vtemp_28[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__input_end_wide, __Vtemp_27, __Vtemp_28);
    __Vtemp_29[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_base_latched;
    __Vtemp_29[1U] = 0U;
    __Vtemp_29[2U] = 0U;
    __Vtemp_29[3U] = 0U;
    __Vtemp_30[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_length_latched;
    __Vtemp_30[1U] = 0U;
    __Vtemp_30[2U] = 0U;
    __Vtemp_30[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__output_end_wide, __Vtemp_29, __Vtemp_30);
    __Vtemp_31[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_base_latched;
    __Vtemp_31[1U] = 0U;
    __Vtemp_31[2U] = 0U;
    __Vtemp_31[3U] = 0U;
    __Vtemp_32[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_length_latched;
    __Vtemp_32[1U] = 0U;
    __Vtemp_32[2U] = 0U;
    __Vtemp_32[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_end_wide, __Vtemp_31, __Vtemp_32);
    __Vtemp_33[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_offset_latched;
    __Vtemp_33[1U] = 0U;
    __Vtemp_33[2U] = 0U;
    __Vtemp_33[3U] = 0U;
    __Vtemp_34[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_bytes_latched;
    __Vtemp_34[1U] = 0U;
    __Vtemp_34[2U] = 0U;
    __Vtemp_34[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_end_wide, __Vtemp_33, __Vtemp_34);
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
        __Vtemp_35[0U] = (((8U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched
                            : 8U) - (IData)(1U));
        __Vtemp_35[1U] = 0U;
        __Vtemp_35[2U] = 0U;
        __Vtemp_35[3U] = 0U;
        __Vtemp_36[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched;
        __Vtemp_36[1U] = 0U;
        __Vtemp_36[2U] = 0U;
        __Vtemp_36[3U] = 0U;
        VL_MUL_W(4, __Vtemp_37, __Vtemp_35, __Vtemp_36);
        __Vtemp_38[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched;
        __Vtemp_38[1U] = 0U;
        __Vtemp_38[2U] = 0U;
        __Vtemp_38[3U] = 0U;
        VL_ADD_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_height_wide, __Vtemp_37, __Vtemp_38);
        __Vtemp_39[0U] = (((8U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched)
                            ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched
                            : 8U) - (IData)(1U));
        __Vtemp_39[1U] = 0U;
        __Vtemp_39[2U] = 0U;
        __Vtemp_39[3U] = 0U;
        __Vtemp_40[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched;
        __Vtemp_40[1U] = 0U;
        __Vtemp_40[2U] = 0U;
        __Vtemp_40[3U] = 0U;
        VL_MUL_W(4, __Vtemp_41, __Vtemp_39, __Vtemp_40);
        __Vtemp_42[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched;
        __Vtemp_42[1U] = 0U;
        __Vtemp_42[2U] = 0U;
        __Vtemp_42[3U] = 0U;
        VL_ADD_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_width_wide, __Vtemp_41, __Vtemp_42);
        VL_MUL_W(4, __Vtemp_43, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_height_wide, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_width_wide);
        __Vtemp_44[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched;
        __Vtemp_44[1U] = 0U;
        __Vtemp_44[2U] = 0U;
        __Vtemp_44[3U] = 0U;
        VL_MUL_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_bytes_wide, __Vtemp_43, __Vtemp_44);
    }
    __Vtemp_45[0U] = ((8U > vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched)
                       ? vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched
                       : 8U);
    __Vtemp_45[1U] = 0U;
    __Vtemp_45[2U] = 0U;
    __Vtemp_45[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_weight_group_bytes_wide, __Vtemp_45, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_wide);
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_ok = 0U;
    vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_error = 1U;
    __Vtemp_47[0U] = 0x00001200U;
    __Vtemp_47[1U] = 0U;
    __Vtemp_47[2U] = 0U;
    __Vtemp_47[3U] = 0U;
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
            | VL_LT_W(4, __Vtemp_47, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_wide)) 
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
        if ((((((VL_LT_W(4, __Vtemp_48, tb_s2a_conv_tile_memory__DOT__dut__DOT__input_elements_wide) 
                 | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__input_length_latched 
                    != tb_s2a_conv_tile_memory__DOT__dut__DOT__input_elements_wide[0U])) 
                | VL_LT_W(4, __Vtemp_49, vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_elements_wide)) 
               | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_length_latched 
                  != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_elements_wide[0U])) 
              | VL_LT_W(4, __Vtemp_50, tb_s2a_conv_tile_memory__DOT__dut__DOT__expected_weight_bytes_wide)) 
             | (vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_bytes_latched 
                != tb_s2a_conv_tile_memory__DOT__dut__DOT__expected_weight_bytes_wide[0U]))) {
            vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_error = 3U;
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
            __Vtemp_54[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_length_latched;
            __Vtemp_54[1U] = 0U;
            __Vtemp_54[2U] = 0U;
            __Vtemp_54[3U] = 0U;
            __Vtemp_55[0U] = 0x00000c5cU;
            __Vtemp_55[1U] = 0U;
            __Vtemp_55[2U] = 0U;
            __Vtemp_55[3U] = 0U;
            __Vtemp_56[0U] = ((0x25U >= (0x0000003fU 
                                         & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                               ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                              [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                               : 0U);
            __Vtemp_56[1U] = 0U;
            __Vtemp_56[2U] = 0U;
            __Vtemp_56[3U] = 0U;
            __Vtemp_57[0U] = vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched;
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
            if (((((((((VL_LT_W(4, __Vtemp_51, tb_s2a_conv_tile_memory__DOT__dut__DOT__input_end_wide) 
                        | VL_LT_W(4, __Vtemp_52, tb_s2a_conv_tile_memory__DOT__dut__DOT__output_end_wide)) 
                       | VL_LT_W(4, __Vtemp_53, tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_end_wide)) 
                      | (0U == vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_length_latched)) 
                     | VL_GT_W(4, tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_end_wide, __Vtemp_54)) 
                    | (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                        [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched)]
                         : 0U) != vlSelfRef.tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched)) 
                   | VL_LT_W(4, __Vtemp_55, __Vtemp_58)) 
                  | VL_LT_W(4, __Vtemp_59, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_tile_patch_bytes_wide)) 
                 | VL_LT_W(4, __Vtemp_60, tb_s2a_conv_tile_memory__DOT__dut__DOT__full_weight_group_bytes_wide))) {
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

VL_ATTR_COLD bool Vtb_s2a_conv_tile_memory___024root___eval_phase__stl(Vtb_s2a_conv_tile_memory___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___eval_phase__stl\n"); );
    Vtb_s2a_conv_tile_memory__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
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
        Vtb_s2a_conv_tile_memory___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
    }
#endif
    __VstlExecute = Vtb_s2a_conv_tile_memory___024root___trigger_anySet__stl(vlSelfRef.__VstlTriggered);
    if (__VstlExecute) {
        {
            // Inlined CFunc: _eval_stl
            if ((1ULL & vlSelfRef.__VstlTriggered[0U])) {
                Vtb_s2a_conv_tile_memory___024root___stl_sequent__TOP__0(vlSelf);
            }
        }
    }
    return (__VstlExecute);
}

bool Vtb_s2a_conv_tile_memory___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_conv_tile_memory___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___dump_triggers__act\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_s2a_conv_tile_memory___024root___trigger_anySet__act(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: @(negedge tb_s2a_conv_tile_memory.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 1U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 1 is active: @(posedge tb_s2a_conv_tile_memory.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 2U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 2 is active: @([true] __VdlySched.awaitingCurrentTime())\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vtb_s2a_conv_tile_memory___024root___ctor_var_reset(Vtb_s2a_conv_tile_memory___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_memory___024root___ctor_var_reset\n"); );
    Vtb_s2a_conv_tile_memory__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->tb_s2a_conv_tile_memory__DOT__start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3337608661814280789ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__cancel = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10199868176215307414ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12422527997959687878ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__req_write = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16778972524870254096ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__req_rstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 1944650707207200870ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__req_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 4731399449475903548ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__ordinal = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7671962617884153553ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__ty = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12718882619352214424ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__tx = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2850574592221527430ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__group_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4661681711664167505ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__th = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15052015581984659873ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__tw = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3414442306137588352ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__ph = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4510840959883560480ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__pw = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14106251863018503148ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__ci = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13695547046031024368ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__k = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17470601506102226549ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__lanes = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6754364999893684209ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__outputs = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3038568225065162632ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__i = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17958892410341833851ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__b = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8054966535149329272ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__idx = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10531645745408859064ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__oc = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9842479061777454498ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10616466485643862827ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11382241151802735776ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__ic = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12046221643677862777ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__py = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8321345500999720004ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__px = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2682367493102173873ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__address = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16290490514859179938ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__selected_lane = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14433738598049928508ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__cls = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18269444256781515273ull);
    for (int __Vi0 = 0; __Vi0 < 3; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__counts[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11157991260914386887ull);
    }
    for (int __Vi0 = 0; __Vi0 < 3; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__stalls[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1922179497502265423ull);
    }
    vlSelf->tb_s2a_conv_tile_memory__DOT__cycles = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15500777366067329194ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__expected_reads = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18357004906556664300ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__actual_features = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10475858641956459565ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__actual_weights = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5216126849235045495ull);
    for (int __Vi0 = 0; __Vi0 < 51200; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__patch[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 17815558822075593751ull);
    }
    for (int __Vi0 = 0; __Vi0 < 36864; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__weights[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 16524541534094225155ull);
    }
    for (int __Vi0 = 0; __Vi0 < 512; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__golden[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 12721215822606680555ull);
    }
    for (int __Vi0 = 0; __Vi0 < 512; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__seen[__Vi0] = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5824036675807816243ull);
    }
    for (int __Vi0 = 0; __Vi0 < 13; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__hdr[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12111783965346622630ull);
    }
    vlSelf->tb_s2a_conv_tile_memory__DOT__held_addr = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12427751254200710070ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__held_wdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7343360177715236137ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__held_rstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 1510488981176975568ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__held_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 1848881119891779248ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__held_write = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11838748270794491825ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__state = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 9103431857756114691ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10181607477968687914ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15573119715231123267ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__input_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6359499826198027752ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__input_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13310930853365036370ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__input_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13080042838279889618ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__input_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17994043972832542400ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__input_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17659109981155812115ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__input_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 42245989507220339ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__output_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17179621301402224273ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__output_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3287066494930690931ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__output_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8719678029440426832ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__output_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10886813719743217514ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__output_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17110345183252017520ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__output_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5859225700830605866ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15581651654858902007ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__kernel_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15193474120083075085ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_y_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17256680016026953274ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__stride_x_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5678607504499161917ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_left_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10945507282545067153ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_right_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12569762642499946780ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_top_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 706499896236850943ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__pad_bottom_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10835665362847777322ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__groups_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16803832716160838392ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__padding_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11096976137536391971ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10355629401987132374ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_package_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12895021924286213392ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_offset_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10629227126796803565ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__quantized_weight_bytes_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10978236345083492308ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__output_batch_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1467289202757350416ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__activation_mode_latched = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 16135452168298161454ull);
    for (int __Vi0 = 0; __Vi0 < 51200; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_patch[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 4793134313421618786ull);
    }
    for (int __Vi0 = 0; __Vi0 < 512; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__output_block[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 3547310153539270270ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_accumulator[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1352967858453585678ull);
    }
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_data = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 8129582325716433973ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_read_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5677241462383332248ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_read_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 805427491237595425ull);
    }
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10036925198214949740ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__output_group_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5829872406222933245ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7615700532461122092ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_start_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11339174099858386084ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17269215018015973192ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18062371448019409379ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7565984385393925692ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6938102281654178188ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__patch_byte_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15568715960019196767ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__tile_point_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3360334511210757962ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__group_lane_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15781426830885619410ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5348782949803292983ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4850313537446341238ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 779656337937816262ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1224449586848534168ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1951566550749555281ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_point_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9178781782235602474ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4318787827733556998ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__output_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7684472925108626922ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8663761282619471440ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__request_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1687463319548654781ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__request_strobe_latched = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 8492733065799985512ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__request_wdata_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16722298328234360808ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 15271448574605393251ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__output_elements_wide, __VscopeHash, 10894639785116615533ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__reduction_count_wide, __VscopeHash, 14331404207544972964ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_ok = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7364845744591886507ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__validation_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 16725690172469755719ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11354781456865826326ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5424604669682108691ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6926736530745079890ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_advance = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14626514363238106013ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_scan_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3480010654651785784ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__feature_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 1287731276012063314ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__weight_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 3901531365820832837ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_input_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4908002542805020364ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9839018979645813327ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15726003253653573610ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_next_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14735527184927329177ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8144163445065426524ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_tap_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6045195101625788376ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_feature_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4438529304019418438ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_read_enable = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2604804477384012199ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_feature_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 17499601183411524958ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_weight_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 14367025598731551013ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_product[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 18441359044026721883ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_sum[__Vi0] = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 252535735756025933ull);
    }
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_bad_argument = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9926123043337479658ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__compute_overflow = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10157336440491360315ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_lane = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16798409139766035552ull);
    VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_parameter, __VscopeHash, 11098345842774888432ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_bias = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2046876078880490236ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__mq_prefetch_invalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12108402329722413986ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_mq_parameter[__Vi0], __VscopeHash, 1196628285948453962ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__lane_bias[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6894988141796675856ull);
    }
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__requant_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17198208190360796440ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__requantized_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 3340071885487781707ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14400505976973668085ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__output_point_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16856484538312181418ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__output_byte_offset_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 6374984301680841823ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__output_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 14944424559283673761ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 13380273209938156329ull);
    vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__request_byte_lane = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 17321095087279278308ull);
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 9220880430275608685ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 13482868969198568211ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 5891632139222395077ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 1007056077510769466ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 11990455755314634164ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 776845328996909680ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 9279422561664787783ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4608; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_memory__DOT__dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 12989852212094661879ull);
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
    vlSelf->__Vtrigprevexpr___TOP__tb_s2a_conv_tile_memory__DOT__clk__0 = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VnbaTriggered[__Vi0] = 0;
    }
    vlSelf->__Vi = 0;
}
