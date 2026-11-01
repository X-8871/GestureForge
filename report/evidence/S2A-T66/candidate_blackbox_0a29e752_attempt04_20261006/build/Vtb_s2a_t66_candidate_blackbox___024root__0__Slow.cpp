// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_t66_candidate_blackbox.h for the primary calling header

#include "Vtb_s2a_t66_candidate_blackbox__pch.h"

void Vtb_s2a_t66_candidate_blackbox___024root___timing_ready(Vtb_s2a_t66_candidate_blackbox___024root* vlSelf);

VL_ATTR_COLD void Vtb_s2a_t66_candidate_blackbox___024root___eval_static(Vtb_s2a_t66_candidate_blackbox___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_candidate_blackbox___024root___eval_static\n"); );
    Vtb_s2a_t66_candidate_blackbox__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    {
        // Inlined CFunc: _eval_static__TOP
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__clk = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__hard_reset = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__buffer_owner_pl = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__start_valid = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__result_ready = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__first_tile_point0_golden_seen = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__first_tile_point1_golden_seen = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__memory_pending = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__response_data = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__response_error = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__response_delay_remaining = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__request_count = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__response_count = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__output_write_count = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__input_read_count = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__weight_read_count = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__stall_cycle_count = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__response_stall_cycle_count = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__held_request = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__stall_remaining = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__cycle_count = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__next_cycle_progress = 0x000186a0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__result_count = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__next_progress = 0x00030d40U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__pending_transfer_class = 0xffffffffU;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__active_request_stall_observed = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__active_response_stall_observed = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__fixture_input_path = ""s;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__fixture_weight_path = ""s;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__fixture_expected_path = ""s;
    }
    vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_t66_candidate_blackbox__DOT__clk__0 = 0U;
    Vtb_s2a_t66_candidate_blackbox___024root___timing_ready(vlSelf);
    do {
        vlSelfRef.__VactTriggeredAcc[vlSelfRef.__Vi] 
            = vlSelfRef.__VactTriggered[vlSelfRef.__Vi];
        vlSelfRef.__Vi = ((IData)(1U) + vlSelfRef.__Vi);
    } while ((0U >= vlSelfRef.__Vi));
}

VL_ATTR_COLD void Vtb_s2a_t66_candidate_blackbox___024root___eval_final(Vtb_s2a_t66_candidate_blackbox___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_candidate_blackbox___024root___eval_final\n"); );
    Vtb_s2a_t66_candidate_blackbox__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_t66_candidate_blackbox___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG
VL_ATTR_COLD bool Vtb_s2a_t66_candidate_blackbox___024root___eval_phase__stl(Vtb_s2a_t66_candidate_blackbox___024root* vlSelf);

VL_ATTR_COLD void Vtb_s2a_t66_candidate_blackbox___024root___eval_settle(Vtb_s2a_t66_candidate_blackbox___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_candidate_blackbox___024root___eval_settle\n"); );
    Vtb_s2a_t66_candidate_blackbox__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VstlIterCount;
    // Body
    __VstlIterCount = 0U;
    vlSelfRef.__VstlFirstIteration = 1U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VstlIterCount)))) {
#ifdef VL_DEBUG
            Vtb_s2a_t66_candidate_blackbox___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
#endif
            VL_FATAL_MT("D:\\FPGA_Competition\\sim\\tb_s2a_t66_candidate_blackbox.sv", 3, "", "DIDNOTCONVERGE: Settle region did not converge after '--converge-limit' of 10000 tries");
        }
        __VstlIterCount = ((IData)(1U) + __VstlIterCount);
        vlSelfRef.__VstlPhaseResult = Vtb_s2a_t66_candidate_blackbox___024root___eval_phase__stl(vlSelf);
        vlSelfRef.__VstlFirstIteration = 0U;
    } while (vlSelfRef.__VstlPhaseResult);
}

VL_ATTR_COLD bool Vtb_s2a_t66_candidate_blackbox___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_t66_candidate_blackbox___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_candidate_blackbox___024root___dump_triggers__stl\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_s2a_t66_candidate_blackbox___024root___trigger_anySet__stl(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: Internal 'stl' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD bool Vtb_s2a_t66_candidate_blackbox___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_candidate_blackbox___024root___trigger_anySet__stl\n"); );
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

extern const VlWide<10>/*319:0*/ Vtb_s2a_t66_candidate_blackbox__ConstPool__CONST_hb4617e49_0;
extern const VlUnpacked<IData/*31:0*/, 5> Vtb_s2a_t66_candidate_blackbox__ConstPool__TABLE_hc6a14c36_0;

VL_ATTR_COLD void Vtb_s2a_t66_candidate_blackbox___024root___stl_sequent__TOP__0(Vtb_s2a_t66_candidate_blackbox___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_candidate_blackbox___024root___stl_sequent__TOP__0\n"); );
    Vtb_s2a_t66_candidate_blackbox__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ tb_s2a_t66_candidate_blackbox__DOT__request_transfer_class_comb;
    tb_s2a_t66_candidate_blackbox__DOT__request_transfer_class_comb = 0;
    VlWide<4>/*127:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_elements_wide;
    VL_ZERO_W(128, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_elements_wide);
    VlWide<4>/*127:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__expected_weight_bytes_wide;
    VL_ZERO_W(128, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__expected_weight_bytes_wide);
    VlWide<4>/*127:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_end_wide;
    VL_ZERO_W(128, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_end_wide;
    VL_ZERO_W(128, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_package_end_wide;
    VL_ZERO_W(128, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_package_end_wide);
    VlWide<4>/*127:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__quantized_weight_end_wide;
    VL_ZERO_W(128, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__quantized_weight_end_wide);
    QData/*63:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_numerator;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_numerator = 0;
    QData/*63:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_numerator;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_numerator = 0;
    QData/*63:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_shape_span;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_shape_span = 0;
    QData/*63:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_shape_span;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_shape_span = 0;
    QData/*63:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_shape_product;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_shape_product = 0;
    QData/*63:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_shape_product;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_shape_product = 0;
    QData/*63:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_span_plus_stride;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_span_plus_stride = 0;
    QData/*63:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_span_plus_stride;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_span_plus_stride = 0;
    VlWide<4>/*127:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_height_wide;
    VL_ZERO_W(128, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_height_wide);
    VlWide<4>/*127:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_width_wide;
    VL_ZERO_W(128, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_width_wide);
    VlWide<4>/*127:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_bytes_wide;
    VL_ZERO_W(128, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_bytes_wide);
    VlWide<4>/*127:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_weight_group_bytes_wide;
    VL_ZERO_W(128, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_weight_group_bytes_wide);
    QData/*63:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__patch_plane_bytes;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__patch_plane_bytes = 0;
    QData/*63:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_input_y;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_input_y = 0;
    QData/*63:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_input_x;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_input_x = 0;
    QData/*63:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_source_offset;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_source_offset = 0;
    IData/*31:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_kernel_area;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_kernel_area = 0;
    IData/*31:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_next_input_channel;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_next_input_channel = 0;
    IData/*31:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_next_kernel_y;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_next_kernel_y = 0;
    IData/*31:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_next_reduction_index;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_next_reduction_index = 0;
    IData/*31:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_point_y;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_point_y = 0;
    IData/*31:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_point_x;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_point_x = 0;
    IData/*31:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_input_channel;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_input_channel = 0;
    IData/*31:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_kernel_y;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_kernel_y = 0;
    IData/*31:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_kernel_x;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_kernel_x = 0;
    QData/*63:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_input_y;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_input_y = 0;
    QData/*63:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_input_x;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_input_x = 0;
    QData/*63:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_feature_index_wide;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_feature_index_wide = 0;
    IData/*31:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_index;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_index = 0;
    VlWide<3>/*79:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_parameter;
    VL_ZERO_W(80, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_parameter);
    IData/*31:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_accumulator;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_accumulator = 0;
    IData/*31:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_multiplier;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_multiplier = 0;
    IData/*31:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_q_shift;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_q_shift = 0;
    IData/*31:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_magnitude;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_magnitude = 0;
    QData/*63:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_product;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_product = 0;
    QData/*63:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_rounding_add;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_rounding_add = 0;
    QData/*63:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_rounded_magnitude;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_rounded_magnitude = 0;
    QData/*63:0*/ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_signed_value;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_signed_value = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_candidate_blackbox__DOT__classify_transfer__0__Vfuncout;
    __Vfunc_tb_s2a_t66_candidate_blackbox__DOT__classify_transfer__0__Vfuncout = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_t66_candidate_blackbox__DOT__classify_transfer__0__is_write;
    __Vfunc_tb_s2a_t66_candidate_blackbox__DOT__classify_transfer__0__is_write = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_candidate_blackbox__DOT__classify_transfer__0__word_address;
    __Vfunc_tb_s2a_t66_candidate_blackbox__DOT__classify_transfer__0__word_address = 0;
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
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__backend_cancel 
        = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__hard_reset;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__request_byte_lane 
        = (3U & (0x00030210U >> ((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__request_strobe_latched) 
                                 << 1U)));
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__hard_reset)) 
           & (0U == (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__state)));
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__backend_req_rstrb = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__backend_req_wstrb = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_source_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_package_base_latched)) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__quantized_weight_offset_latched)) 
              + ((QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_reduction_index)) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__reduction_count_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_lane_index)))))));
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_byte_offset_wide 
        = ((QData)((IData)((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_point_scan_x 
                            + vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__tile_start_x))) 
           + ((QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_latched)) 
              * ((QData)((IData)((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_point_scan_y 
                                  + vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__tile_start_y))) 
                 + ((QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_latched)) 
                    * (QData)((IData)((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_group_base 
                                       + vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_lane_index)))))));
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_index = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[0U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[1U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[2U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_bias = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_invalid = 0U;
    if (((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_lane 
          < vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__group_lane_count) 
         & (0x00000026U > vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__layer_index_latched))) {
        tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_index 
            = ((((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__layer_index_latched))
                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                 [(0x0000003fU & vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__layer_index_latched)]
                  : 0U) + vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_group_base) 
               + vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_lane);
        if ((0x00000c5cU > tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_index)) {
            if ((0x0c5bU >= (0x00000fffU & tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_index))) {
                vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[0U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_index)][0U];
                vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_index)][1U];
                vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[2U] 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                    [(0x00000fffU & tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_index)][2U];
                vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_bias 
                    = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_CONV_BIAS_ACCUMULATOR_INT32
                    [(0x00000fffU & tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_index)];
            } else {
                vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[0U] = 0U;
                vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[1U] = 0U;
                vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[2U] = 0U;
                vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_bias = 0U;
            }
            if (((((((((tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_index 
                        >= (((0x25U >= (0x0000003fU 
                                        & vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__layer_index_latched))
                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                             [(0x0000003fU & vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__layer_index_latched)]
                              : 0U) + ((0x25U >= (0x0000003fU 
                                                  & vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__layer_index_latched))
                                        ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                       [(0x0000003fU 
                                         & vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__layer_index_latched)]
                                        : 0U))) | (0U 
                                                   == 
                                                   ((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[2U] 
                                                     << 0x00000010U) 
                                                    | (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                                       >> 0x00000010U)))) 
                      | (0U == ((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                 << 0x00000018U) | 
                                (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[0U] 
                                 >> 8U)))) | (0x3fffffffU 
                                              < ((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[2U] 
                                                  << 0x00000010U) 
                                                 | (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                                    >> 0x00000010U)))) 
                    | (0x3fffffffU < ((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                       << 0x00000018U) 
                                      | (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[0U] 
                                         >> 8U)))) 
                   | (0x2fU < (0x000000ffU & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                              >> 8U)))) 
                  | (0x2fU < (0x000000ffU & vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[0U]))) 
                 | ((0U == (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__activation_mode_latched)) 
                    & ((((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[2U] 
                          << 0x00000010U) | (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                             >> 0x00000010U)) 
                        != ((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                             << 0x00000018U) | (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[0U] 
                                                >> 8U))) 
                       | ((0x000000ffU & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[1U] 
                                          >> 8U)) != 
                          (0x000000ffU & vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter[0U])))))) {
                vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_invalid = 1U;
            }
        } else {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_invalid = 1U;
        }
    } else if ((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_lane 
                < vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_invalid = 1U;
    }
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_parameter[0U] = 0U;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_parameter[1U] = 0U;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_parameter[2U] = 0U;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_accumulator = 0U;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_multiplier = 0U;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_q_shift = 0U;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_magnitude = 0U;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_product = 0ULL;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_rounding_add = 0ULL;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_rounded_magnitude = 0ULL;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_signed_value = 0ULL;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requantized_value = 0U;
    if (((8U > vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_lane_index) 
         & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_lane_index 
            < vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__group_lane_count))) {
        tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_parameter[0U] 
            = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_lane_index)][0U];
        tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_parameter[1U] 
            = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_lane_index)][1U];
        tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_parameter[2U] 
            = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_mq_parameter
            [(7U & vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_lane_index)][2U];
        tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_accumulator 
            = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_accumulator
            [(7U & vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_lane_index)];
        if ((tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_accumulator 
             >> 0x1fU)) {
            tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_multiplier 
                = ((tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_parameter[1U] 
                    << 0x00000018U) | (tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_parameter[0U] 
                                       >> 8U));
            tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_magnitude 
                = ((IData)(1U) + (~ tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_accumulator));
            tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_q_shift 
                = (0x000000ffU & tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_parameter[0U]);
        } else {
            tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_multiplier 
                = ((tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_parameter[2U] 
                    << 0x00000010U) | (tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_parameter[1U] 
                                       >> 0x00000010U));
            tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_magnitude 
                = tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_accumulator;
            tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_q_shift 
                = (0x000000ffU & (tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_parameter[1U] 
                                  >> 8U));
        }
        tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_product 
            = ((QData)((IData)(tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_magnitude)) 
               * (QData)((IData)(tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_multiplier)));
        if ((0U != tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_q_shift)) {
            tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_rounding_add 
                = VL_SHIFTL_QQI(64,64,32, 1ULL, (tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_q_shift 
                                                 - (IData)(1U)));
        }
        tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_rounded_magnitude 
            = VL_SHIFTR_QQI(64,64,32, (tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_product 
                                       + tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_rounding_add), tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_q_shift);
        __Vtemp_2[0U] = (IData)(tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_rounded_magnitude);
        __Vtemp_2[1U] = (IData)((tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_rounded_magnitude 
                                 >> 0x00000020U));
        __Vtemp_2[2U] = 0U;
        VL_NEGATE_W(3, __Vtemp_3, __Vtemp_2);
        tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_signed_value 
            = ((tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_accumulator 
                >> 0x1fU) ? (((QData)((IData)(__Vtemp_3[1U])) 
                              << 0x00000020U) | (QData)((IData)(__Vtemp_3[0U])))
                : tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_rounded_magnitude);
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requantized_value 
            = (VL_LTS_IQQ(64, 0x000000000000007fULL, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_signed_value)
                ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_signed_value)
                                  ? 0x00000081U : (0x000000ffU 
                                                   & (IData)(tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_signed_value))));
    }
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__backend_req_write = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__backend_req_valid = 0U;
    if ((1U & (~ (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__hard_reset)))) {
        if (((4U == (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__state)) 
             || (8U == (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__state)))) {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__backend_req_rstrb 
                = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__request_strobe_latched;
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__backend_req_write = 0U;
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__backend_req_valid = 1U;
        } else if ((0x10U == (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__state))) {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__backend_req_write = 1U;
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__backend_req_valid = 1U;
        }
        if ((1U & (~ ((4U == (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__state)) 
                      || (8U == (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__state)))))) {
            if ((0x10U == (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__state))) {
                vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__backend_req_wstrb 
                    = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__request_strobe_latched;
            }
        }
    }
    __Vtemp_5[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_batch_count_latched;
    __Vtemp_5[1U] = 0U;
    __Vtemp_5[2U] = 0U;
    __Vtemp_5[3U] = 0U;
    __Vtemp_6[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_channels_latched;
    __Vtemp_6[1U] = 0U;
    __Vtemp_6[2U] = 0U;
    __Vtemp_6[3U] = 0U;
    VL_MUL_W(4, __Vtemp_7, __Vtemp_5, __Vtemp_6);
    __Vtemp_8[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_height_latched;
    __Vtemp_8[1U] = 0U;
    __Vtemp_8[2U] = 0U;
    __Vtemp_8[3U] = 0U;
    VL_MUL_W(4, __Vtemp_9, __Vtemp_7, __Vtemp_8);
    __Vtemp_10[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_width_latched;
    __Vtemp_10[1U] = 0U;
    __Vtemp_10[2U] = 0U;
    __Vtemp_10[3U] = 0U;
    VL_MUL_W(4, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_elements_wide, __Vtemp_9, __Vtemp_10);
    __Vtemp_11[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_batch_count_latched;
    __Vtemp_11[1U] = 0U;
    __Vtemp_11[2U] = 0U;
    __Vtemp_11[3U] = 0U;
    __Vtemp_12[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_channels_latched;
    __Vtemp_12[1U] = 0U;
    __Vtemp_12[2U] = 0U;
    __Vtemp_12[3U] = 0U;
    VL_MUL_W(4, __Vtemp_13, __Vtemp_11, __Vtemp_12);
    __Vtemp_14[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_latched;
    __Vtemp_14[1U] = 0U;
    __Vtemp_14[2U] = 0U;
    __Vtemp_14[3U] = 0U;
    VL_MUL_W(4, __Vtemp_15, __Vtemp_13, __Vtemp_14);
    __Vtemp_16[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_latched;
    __Vtemp_16[1U] = 0U;
    __Vtemp_16[2U] = 0U;
    __Vtemp_16[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_elements_wide, __Vtemp_15, __Vtemp_16);
    __Vtemp_17[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_channels_latched;
    __Vtemp_17[1U] = 0U;
    __Vtemp_17[2U] = 0U;
    __Vtemp_17[3U] = 0U;
    __Vtemp_18[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_channels_latched;
    __Vtemp_18[1U] = 0U;
    __Vtemp_18[2U] = 0U;
    __Vtemp_18[3U] = 0U;
    VL_MUL_W(4, __Vtemp_19, __Vtemp_17, __Vtemp_18);
    __Vtemp_20[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__kernel_height_latched;
    __Vtemp_20[1U] = 0U;
    __Vtemp_20[2U] = 0U;
    __Vtemp_20[3U] = 0U;
    VL_MUL_W(4, __Vtemp_21, __Vtemp_19, __Vtemp_20);
    __Vtemp_22[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__kernel_width_latched;
    __Vtemp_22[1U] = 0U;
    __Vtemp_22[2U] = 0U;
    __Vtemp_22[3U] = 0U;
    VL_MUL_W(4, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__expected_weight_bytes_wide, __Vtemp_21, __Vtemp_22);
    __Vtemp_23[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_channels_latched;
    __Vtemp_23[1U] = 0U;
    __Vtemp_23[2U] = 0U;
    __Vtemp_23[3U] = 0U;
    __Vtemp_24[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__kernel_height_latched;
    __Vtemp_24[1U] = 0U;
    __Vtemp_24[2U] = 0U;
    __Vtemp_24[3U] = 0U;
    VL_MUL_W(4, __Vtemp_25, __Vtemp_23, __Vtemp_24);
    __Vtemp_26[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__kernel_width_latched;
    __Vtemp_26[1U] = 0U;
    __Vtemp_26[2U] = 0U;
    __Vtemp_26[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__reduction_count_wide, __Vtemp_25, __Vtemp_26);
    __Vtemp_27[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_base_latched;
    __Vtemp_27[1U] = 0U;
    __Vtemp_27[2U] = 0U;
    __Vtemp_27[3U] = 0U;
    __Vtemp_28[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_length_latched;
    __Vtemp_28[1U] = 0U;
    __Vtemp_28[2U] = 0U;
    __Vtemp_28[3U] = 0U;
    VL_ADD_W(4, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_end_wide, __Vtemp_27, __Vtemp_28);
    __Vtemp_29[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_base_latched;
    __Vtemp_29[1U] = 0U;
    __Vtemp_29[2U] = 0U;
    __Vtemp_29[3U] = 0U;
    __Vtemp_30[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_length_latched;
    __Vtemp_30[1U] = 0U;
    __Vtemp_30[2U] = 0U;
    __Vtemp_30[3U] = 0U;
    VL_ADD_W(4, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_end_wide, __Vtemp_29, __Vtemp_30);
    __Vtemp_31[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_package_base_latched;
    __Vtemp_31[1U] = 0U;
    __Vtemp_31[2U] = 0U;
    __Vtemp_31[3U] = 0U;
    __Vtemp_32[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_package_length_latched;
    __Vtemp_32[1U] = 0U;
    __Vtemp_32[2U] = 0U;
    __Vtemp_32[3U] = 0U;
    VL_ADD_W(4, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_package_end_wide, __Vtemp_31, __Vtemp_32);
    __Vtemp_33[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__quantized_weight_offset_latched;
    __Vtemp_33[1U] = 0U;
    __Vtemp_33[2U] = 0U;
    __Vtemp_33[3U] = 0U;
    __Vtemp_34[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__quantized_weight_bytes_latched;
    __Vtemp_34[1U] = 0U;
    __Vtemp_34[2U] = 0U;
    __Vtemp_34[3U] = 0U;
    VL_ADD_W(4, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__quantized_weight_end_wide, __Vtemp_33, __Vtemp_34);
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_height_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__pad_top_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__pad_bottom_latched)));
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_numerator 
        = (((QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_width_latched)) 
            + (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__pad_left_latched))) 
           + (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__pad_right_latched)));
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_shape_span 
        = (tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_numerator 
           - (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__kernel_height_latched)));
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_shape_span 
        = (tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_numerator 
           - (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__kernel_width_latched)));
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_shape_product 
        = ((QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_latched)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__stride_y_latched)));
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_shape_product 
        = ((QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_latched)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__stride_x_latched)));
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_span_plus_stride 
        = (tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_shape_span 
           + (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__stride_y_latched)));
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_span_plus_stride 
        = (tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_shape_span 
           + (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__stride_x_latched)));
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_height_wide[0U] = 0U;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_height_wide[1U] = 0U;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_height_wide[2U] = 0U;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_height_wide[3U] = 0U;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_width_wide[0U] = 0U;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_width_wide[1U] = 0U;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_width_wide[2U] = 0U;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_width_wide[3U] = 0U;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_bytes_wide[0U] = 0U;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_bytes_wide[1U] = 0U;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_bytes_wide[2U] = 0U;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_bytes_wide[3U] = 0U;
    if (((0U != vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_latched) 
         & (0U != vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_latched))) {
        __Vtemp_35[0U] = (((8U > vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_latched)
                            ? vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_latched
                            : 8U) - (IData)(1U));
        __Vtemp_35[1U] = 0U;
        __Vtemp_35[2U] = 0U;
        __Vtemp_35[3U] = 0U;
        __Vtemp_36[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__stride_y_latched;
        __Vtemp_36[1U] = 0U;
        __Vtemp_36[2U] = 0U;
        __Vtemp_36[3U] = 0U;
        VL_MUL_W(4, __Vtemp_37, __Vtemp_35, __Vtemp_36);
        __Vtemp_38[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__kernel_height_latched;
        __Vtemp_38[1U] = 0U;
        __Vtemp_38[2U] = 0U;
        __Vtemp_38[3U] = 0U;
        VL_ADD_W(4, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_height_wide, __Vtemp_37, __Vtemp_38);
        __Vtemp_39[0U] = (((8U > vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_latched)
                            ? vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_latched
                            : 8U) - (IData)(1U));
        __Vtemp_39[1U] = 0U;
        __Vtemp_39[2U] = 0U;
        __Vtemp_39[3U] = 0U;
        __Vtemp_40[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__stride_x_latched;
        __Vtemp_40[1U] = 0U;
        __Vtemp_40[2U] = 0U;
        __Vtemp_40[3U] = 0U;
        VL_MUL_W(4, __Vtemp_41, __Vtemp_39, __Vtemp_40);
        __Vtemp_42[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__kernel_width_latched;
        __Vtemp_42[1U] = 0U;
        __Vtemp_42[2U] = 0U;
        __Vtemp_42[3U] = 0U;
        VL_ADD_W(4, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_width_wide, __Vtemp_41, __Vtemp_42);
        VL_MUL_W(4, __Vtemp_43, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_height_wide, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_width_wide);
        __Vtemp_44[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_channels_latched;
        __Vtemp_44[1U] = 0U;
        __Vtemp_44[2U] = 0U;
        __Vtemp_44[3U] = 0U;
        VL_MUL_W(4, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_bytes_wide, __Vtemp_43, __Vtemp_44);
    }
    __Vtemp_45[0U] = ((8U > vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_channels_latched)
                       ? vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_channels_latched
                       : 8U);
    __Vtemp_45[1U] = 0U;
    __Vtemp_45[2U] = 0U;
    __Vtemp_45[3U] = 0U;
    VL_MUL_W(4, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_weight_group_bytes_wide, __Vtemp_45, vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__reduction_count_wide);
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__validation_ok = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__validation_error = 1U;
    __Vtemp_47[0U] = 0x00001fffU;
    __Vtemp_47[1U] = 0U;
    __Vtemp_47[2U] = 0U;
    __Vtemp_47[3U] = 0U;
    if ((1U & ((((((((((((((((((((((~ (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__buffer_owner_pl)) 
                                   | (1U < (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__activation_mode_latched))) 
                                  | (1U != vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_batch_count_latched)) 
                                 | (1U != vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_batch_count_latched)) 
                                | (0U != vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_batch_latched)) 
                               | (0U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_channels_latched)) 
                              | (0U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_height_latched)) 
                             | (0U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_width_latched)) 
                            | (0U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_channels_latched)) 
                           | (0U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_latched)) 
                          | (0U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_latched)) 
                         | (0U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__kernel_height_latched)) 
                        | (0U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__kernel_width_latched)) 
                       | (0U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__stride_y_latched)) 
                      | (0U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__stride_x_latched)) 
                     | (1U != vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__groups_latched)) 
                    | (0U != vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__padding_latched)) 
                   | (0U == (((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__reduction_count_wide[0U] 
                               | vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__reduction_count_wide[1U]) 
                              | vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__reduction_count_wide[2U]) 
                             | vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__reduction_count_wide[3U]))) 
                  | VL_LT_W(4, __Vtemp_47, vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__reduction_count_wide)) 
                 | (0x00000026U <= vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__layer_index_latched)) 
                | ((0x00000026U > vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__layer_index_latched) 
                   & (0U != ((0x25U >= (0x0000003fU 
                                        & vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__layer_index_latched))
                              ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_OP
                             [(0x0000003fU & vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__layer_index_latched)]
                              : 0U)))) | (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__layer_index_latched 
                                          != vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_layer_index_latched)))) {
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__validation_error 
            = (((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__layer_index_latched 
                 != vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_layer_index_latched) 
                | (0x00000026U <= vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__layer_index_latched))
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
        if ((((((VL_LT_W(4, __Vtemp_48, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_elements_wide) 
                 | (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_length_latched 
                    != tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_elements_wide[0U])) 
                | VL_LT_W(4, __Vtemp_49, vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_elements_wide)) 
               | (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_length_latched 
                  != vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_elements_wide[0U])) 
              | VL_LT_W(4, __Vtemp_50, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__expected_weight_bytes_wide)) 
             | (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__quantized_weight_bytes_latched 
                != tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__expected_weight_bytes_wide[0U]))) {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__validation_error = 3U;
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
            __Vtemp_54[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_package_length_latched;
            __Vtemp_54[1U] = 0U;
            __Vtemp_54[2U] = 0U;
            __Vtemp_54[3U] = 0U;
            __Vtemp_55[0U] = 0x00000c5cU;
            __Vtemp_55[1U] = 0U;
            __Vtemp_55[2U] = 0U;
            __Vtemp_55[3U] = 0U;
            __Vtemp_56[0U] = ((0x25U >= (0x0000003fU 
                                         & vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__layer_index_latched))
                               ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                              [(0x0000003fU & vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__layer_index_latched)]
                               : 0U);
            __Vtemp_56[1U] = 0U;
            __Vtemp_56[2U] = 0U;
            __Vtemp_56[3U] = 0U;
            __Vtemp_57[0U] = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_channels_latched;
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
            if (((((((((VL_LT_W(4, __Vtemp_51, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_end_wide) 
                        | VL_LT_W(4, __Vtemp_52, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_end_wide)) 
                       | VL_LT_W(4, __Vtemp_53, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_package_end_wide)) 
                      | (0U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_package_length_latched)) 
                     | VL_GT_W(4, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__quantized_weight_end_wide, __Vtemp_54)) 
                    | (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__layer_index_latched))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                        [(0x0000003fU & vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__layer_index_latched)]
                         : 0U) != vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_channels_latched)) 
                   | VL_LT_W(4, __Vtemp_55, __Vtemp_58)) 
                  | VL_LT_W(4, __Vtemp_59, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_tile_patch_bytes_wide)) 
                 | VL_LT_W(4, __Vtemp_60, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__full_weight_group_bytes_wide))) {
                vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__validation_error = 2U;
            } else if (((((((tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_numerator 
                             < (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__kernel_height_latched))) 
                            | (tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_numerator 
                               < (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__kernel_width_latched)))) 
                           | (tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_shape_product 
                              <= tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_shape_span)) 
                          | (tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_shape_product 
                             > tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_span_plus_stride)) 
                         | (tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_shape_product 
                            <= tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_shape_span)) 
                        | (tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_shape_product 
                           > tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_span_plus_stride))) {
                vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__validation_error = 1U;
            } else {
                vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__validation_ok = 1U;
                vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__validation_error = 0U;
            }
        }
    }
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__backend_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__memory_pending) 
           & (0U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__response_delay_remaining));
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_base_latched)) 
           + vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_byte_offset_wide);
    __Vfunc_tb_s2a_t66_candidate_blackbox__DOT__classify_transfer__0__word_address 
        = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__request_address_latched;
    __Vfunc_tb_s2a_t66_candidate_blackbox__DOT__classify_transfer__0__is_write 
        = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__backend_req_write;
    __Vfunc_tb_s2a_t66_candidate_blackbox__DOT__classify_transfer__0__Vfuncout 
        = ((IData)(__Vfunc_tb_s2a_t66_candidate_blackbox__DOT__classify_transfer__0__is_write)
            ? (((0x01000000U <= __Vfunc_tb_s2a_t66_candidate_blackbox__DOT__classify_transfer__0__word_address) 
                & (0x01152000U > __Vfunc_tb_s2a_t66_candidate_blackbox__DOT__classify_transfer__0__word_address))
                ? 2U : 0xffffffffU) : ((0x0007ec00U 
                                        > __Vfunc_tb_s2a_t66_candidate_blackbox__DOT__classify_transfer__0__word_address)
                                        ? 0U : (((0x0010013cU 
                                                  <= __Vfunc_tb_s2a_t66_candidate_blackbox__DOT__classify_transfer__0__word_address) 
                                                 & (0x0010049cU 
                                                    > __Vfunc_tb_s2a_t66_candidate_blackbox__DOT__classify_transfer__0__word_address))
                                                 ? 1U
                                                 : 0xffffffffU)));
    tb_s2a_t66_candidate_blackbox__DOT__request_transfer_class_comb 
        = __Vfunc_tb_s2a_t66_candidate_blackbox__DOT__classify_transfer__0__Vfuncout;
    if (((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__hard_reset) 
         | (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__memory_pending))) {
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__backend_req_ready = 0U;
    } else if ((0U != vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__held_request)) {
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__backend_req_ready 
            = (0U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__stall_remaining);
    } else if (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__backend_req_valid) {
        if (VL_GTS_III(32, 0U, tb_s2a_t66_candidate_blackbox__DOT__request_transfer_class_comb)) {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__backend_req_ready = 1U;
        } else {
            vlSelfRef.__Vfunc_tb_s2a_t66_candidate_blackbox__DOT__request_stall_cycles__1__index 
                = ((2U >= (3U & tb_s2a_t66_candidate_blackbox__DOT__request_transfer_class_comb))
                    ? vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__class_request_count
                   [(3U & tb_s2a_t66_candidate_blackbox__DOT__request_transfer_class_comb)]
                    : 0U);
            __Vtemp_61 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, vlSelfRef.__Vfunc_tb_s2a_t66_candidate_blackbox__DOT__request_stall_cycles__1__index, (IData)(5U)), Vtb_s2a_t66_candidate_blackbox__ConstPool__CONST_hb4617e49_0);
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT____VlemCall_0__request_stall_cycles 
                = Vtb_s2a_t66_candidate_blackbox__ConstPool__TABLE_hc6a14c36_0
                [__Vtemp_61];
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__backend_req_ready 
                = (0U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT____VlemCall_0__request_stall_cycles);
        }
    } else {
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__backend_req_ready = 0U;
    }
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__patch_plane_bytes 
        = ((QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__patch_height)) 
           * (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__patch_width)));
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_input_y = 0ULL;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_input_x = 0ULL;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_scan_in_bounds = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_scan_advance = 0U;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_source_offset = 0ULL;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_source_address_wide = 0ULL;
    if (((0ULL != tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__patch_plane_bytes) 
         & (0U != vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__patch_width))) {
        tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_input_y 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__tile_start_y)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__stride_y_latched))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_scan_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__pad_top_latched)));
        tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_input_x 
            = ((((QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__tile_start_x)) 
                 * (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__stride_x_latched))) 
                + (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_scan_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_scan_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_input_y, (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_input_x, (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_width_latched))));
        if (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_scan_in_bounds) {
            tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_source_offset 
                = (((((QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_scan_channel)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_height_latched))) 
                     + tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_input_y) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_width_latched))) 
                   + tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_input_x);
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_source_address_wide 
                = ((QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_base_latched)) 
                   + tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_source_offset);
        }
    }
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_kernel_area 
        = (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__kernel_height_latched 
           * vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__kernel_width_latched);
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_next_input_channel 
        = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_input_channel;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_next_kernel_y 
        = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_kernel_y;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_next_reduction_index 
        = ((IData)(1U) + vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_reduction_index);
    if ((((IData)(1U) + vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_kernel_x) 
         >= vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__kernel_width_latched)) {
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_next_kernel_x = 0U;
        if ((((IData)(1U) + vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_kernel_y) 
             >= vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__kernel_height_latched)) {
            tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_next_kernel_y = 0U;
            tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_next_input_channel 
                = ((IData)(1U) + vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_input_channel);
        } else {
            tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_next_kernel_y 
                = ((IData)(1U) + vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_kernel_y);
        }
    } else {
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_next_kernel_x 
            = ((IData)(1U) + vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_kernel_x);
    }
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_point_y 
        = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_point_scan_y;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_point_x 
        = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_point_scan_x;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_input_channel 
        = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_input_channel;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_kernel_y 
        = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_kernel_y;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_kernel_x 
        = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_kernel_x;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_reduction_index 
        = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_reduction_index;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_input_y = 0ULL;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_input_x = 0ULL;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_tap_in_bounds = 0U;
    tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_feature_index_wide = 0ULL;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_feature_index = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_enable = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_bad_argument = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_overflow = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[0U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[0U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[0U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[0U] = 0ULL;
    if ((0U < vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[0U] 
            = ((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[0U] 
            = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_read_byte[0U];
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[0U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[0U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[0U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[0U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[0U])));
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[0U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_accumulator[0U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_accumulator[0U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[0U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[0U])))));
        if (((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[0U]) 
                | (0x80U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[0U])))) {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[0U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[0U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[1U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[1U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[1U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[1U] = 0ULL;
    if ((1U < vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[1U] 
            = ((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[1U] 
            = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_read_byte[1U];
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[1U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[1U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[1U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[1U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[1U])));
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[1U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_accumulator[1U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_accumulator[1U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[1U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[1U])))));
        if (((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[1U]) 
                | (0x80U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[1U])))) {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[1U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[1U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[2U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[2U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[2U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[2U] = 0ULL;
    if ((2U < vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[2U] 
            = ((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[2U] 
            = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_read_byte[2U];
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[2U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[2U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[2U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[2U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[2U])));
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[2U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_accumulator[2U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_accumulator[2U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[2U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[2U])))));
        if (((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[2U]) 
                | (0x80U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[2U])))) {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[2U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[2U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[3U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[3U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[3U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[3U] = 0ULL;
    if ((3U < vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[3U] 
            = ((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[3U] 
            = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_read_byte[3U];
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[3U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[3U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[3U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[3U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[3U])));
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[3U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_accumulator[3U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_accumulator[3U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[3U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[3U])))));
        if (((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[3U]) 
                | (0x80U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[3U])))) {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[3U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[3U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[4U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[4U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[4U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[4U] = 0ULL;
    if ((4U < vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[4U] 
            = ((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[4U] 
            = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_read_byte[4U];
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[4U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[4U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[4U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[4U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[4U])));
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[4U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_accumulator[4U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_accumulator[4U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[4U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[4U])))));
        if (((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[4U]) 
                | (0x80U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[4U])))) {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[4U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[4U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[5U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[5U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[5U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[5U] = 0ULL;
    if ((5U < vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[5U] 
            = ((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[5U] 
            = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_read_byte[5U];
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[5U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[5U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[5U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[5U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[5U])));
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[5U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_accumulator[5U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_accumulator[5U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[5U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[5U])))));
        if (((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[5U]) 
                | (0x80U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[5U])))) {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[5U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[5U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[6U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[6U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[6U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[6U] = 0ULL;
    if ((6U < vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[6U] 
            = ((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[6U] 
            = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_read_byte[6U];
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[6U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[6U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[6U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[6U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[6U])));
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[6U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_accumulator[6U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_accumulator[6U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[6U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[6U])))));
        if (((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[6U]) 
                | (0x80U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[6U])))) {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[6U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[6U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[7U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[7U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[7U] = 0U;
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[7U] = 0ULL;
    if ((7U < vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__group_lane_count)) {
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[7U] 
            = ((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_in_bounds)
                ? (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_data)
                : 0U);
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[7U] 
            = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_read_byte[7U];
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[7U] 
            = (0x0000ffffU & VL_MULS_III(16, ((0x0000ff00U 
                                               & ((- (IData)(
                                                             (1U 
                                                              & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[7U] 
                                                                 >> 7U)))) 
                                                  << 8U)) 
                                              | vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[7U]), 
                                         ((0x0000ff00U 
                                           & ((- (IData)(
                                                         (1U 
                                                          & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[7U] 
                                                             >> 7U)))) 
                                              << 8U)) 
                                          | vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[7U])));
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[7U] 
            = (0x00000001ffffffffULL & ((((QData)((IData)(
                                                          (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_accumulator[7U] 
                                                           >> 0x1fU))) 
                                          << 0x00000020U) 
                                         | (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_accumulator[7U]))) 
                                        + (((QData)((IData)(
                                                            (0x0001ffffU 
                                                             & (- (IData)(
                                                                          (1U 
                                                                           & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[7U] 
                                                                              >> 0x0fU))))))) 
                                            << 0x00000010U) 
                                           | (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[7U])))));
        if (((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_in_bounds) 
             & ((0x80U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[7U]) 
                | (0x80U == vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[7U])))) {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_bad_argument = 1U;
        }
        if (((1U & (IData)((vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[7U] 
                            >> 0x20U))) != (1U & (IData)(
                                                         (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[7U] 
                                                          >> 0x1fU))))) {
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_overflow = 1U;
        }
    }
    if (((0x0bU == (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__state)) 
         | (0x0cU == (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__state)))) {
        tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_point_y 
            = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_point_scan_y;
        tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_point_x 
            = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_point_scan_x;
        tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_input_channel = 0U;
        tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_kernel_y = 0U;
        tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_kernel_x = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_reduction_index = 0U;
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_enable = 1U;
    } else if ((0x0dU == (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__state))) {
        if ((((((IData)(1U) + vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_reduction_index) 
               < vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__reduction_count_latched) 
              & (~ (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_bad_argument))) 
             & (~ (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_overflow)))) {
            tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_point_y 
                = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_point_scan_y;
            tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_point_x 
                = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_point_scan_x;
            tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_input_channel 
                = tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_next_input_channel;
            tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_kernel_y 
                = tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_next_kernel_y;
            tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_kernel_x 
                = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_next_kernel_x;
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_reduction_index 
                = tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_next_reduction_index;
            vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_enable = 1U;
        }
    }
    if (((0U != tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_kernel_area) 
         & (0U != vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__tile_width))) {
        tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_input_y 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__tile_start_y)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__stride_y_latched))) 
                 + ((QData)((IData)(tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_point_y)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__stride_y_latched)))) 
                + (QData)((IData)(tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_kernel_y))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__pad_top_latched)));
        tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_input_x 
            = (((((QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__tile_start_x)) 
                  * (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__stride_x_latched))) 
                 + ((QData)((IData)(tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_point_x)) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__stride_x_latched)))) 
                + (QData)((IData)(tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_kernel_x))) 
               - (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__pad_left_latched)));
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_tap_in_bounds 
            = (((VL_LTES_IQQ(64, 0ULL, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_input_y) 
                 & VL_LTS_IQQ(64, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_input_y, (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_height_latched)))) 
                & VL_LTES_IQQ(64, 0ULL, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_input_x)) 
               & VL_LTS_IQQ(64, tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_input_x, (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_width_latched))));
        tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_feature_index_wide 
            = (((((QData)((IData)(tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_input_channel)) 
                  * tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__patch_plane_bytes) 
                 + ((((QData)((IData)(tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_point_y)) 
                      * (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__stride_y_latched))) 
                     + (QData)((IData)(tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_kernel_y))) 
                    * (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__patch_width)))) 
                + ((QData)((IData)(tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_point_x)) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__stride_x_latched)))) 
               + (QData)((IData)(tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_kernel_x)));
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_feature_index 
            = (IData)(tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_feature_index_wide);
    }
    vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mapped_response_error = 6U;
    if ((0U == (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__response_error))) {
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mapped_response_error = 0U;
    } else if ((((1U == (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__response_error)) 
                 | (2U == (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__response_error))) 
                | (6U == (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__response_error)))) {
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mapped_response_error 
            = vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__response_error;
    }
    if ((((3U == (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__state)) 
          & (vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_scan_index 
             < vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__patch_byte_count)) 
         & (~ (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_scan_in_bounds)))) {
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_scan_advance = 1U;
    } else if ((((5U == (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__state)) 
                 & (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__backend_rsp_valid)) 
                & (0U == (IData)(vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mapped_response_error)))) {
        vlSelfRef.tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_scan_advance = 1U;
    }
}

VL_ATTR_COLD bool Vtb_s2a_t66_candidate_blackbox___024root___eval_phase__stl(Vtb_s2a_t66_candidate_blackbox___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_candidate_blackbox___024root___eval_phase__stl\n"); );
    Vtb_s2a_t66_candidate_blackbox__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
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
        Vtb_s2a_t66_candidate_blackbox___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
    }
#endif
    __VstlExecute = Vtb_s2a_t66_candidate_blackbox___024root___trigger_anySet__stl(vlSelfRef.__VstlTriggered);
    if (__VstlExecute) {
        {
            // Inlined CFunc: _eval_stl
            if ((1ULL & vlSelfRef.__VstlTriggered[0U])) {
                Vtb_s2a_t66_candidate_blackbox___024root___stl_sequent__TOP__0(vlSelf);
            }
        }
    }
    return (__VstlExecute);
}

bool Vtb_s2a_t66_candidate_blackbox___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_t66_candidate_blackbox___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_candidate_blackbox___024root___dump_triggers__act\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_s2a_t66_candidate_blackbox___024root___trigger_anySet__act(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: @(posedge tb_s2a_t66_candidate_blackbox.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 1U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 1 is active: @(negedge tb_s2a_t66_candidate_blackbox.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 2U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 2 is active: @([true] __VdlySched.awaitingCurrentTime())\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vtb_s2a_t66_candidate_blackbox___024root___ctor_var_reset(Vtb_s2a_t66_candidate_blackbox___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_candidate_blackbox___024root___ctor_var_reset\n"); );
    Vtb_s2a_t66_candidate_blackbox__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15218586518033246752ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__backend_cancel = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16223699044312493974ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__backend_req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3187478224414261224ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__backend_req_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11362832920979304479ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__backend_req_write = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10288603262214263105ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__backend_req_rstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 16191931355716852692ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__backend_req_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 9201311504869797900ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__backend_rsp_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 18281002057743453279ull);
    for (int __Vi0 = 0; __Vi0 < 519168; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__input_bytes[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 7422276062649555716ull);
    }
    for (int __Vi0 = 0; __Vi0 < 864; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__weight_bytes[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 379734154742308945ull);
    }
    for (int __Vi0 = 0; __Vi0 < 1384448; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__expected_bytes[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 3910211429037078386ull);
    }
    for (int __Vi0 = 0; __Vi0 < 1384448; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__output_seen[__Vi0] = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1432852888632134509ull);
    }
    for (int __Vi0 = 0; __Vi0 < 864; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__weight_seen[__Vi0] = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15602766668636224853ull);
    }
    for (int __Vi0 = 0; __Vi0 < 3; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__class_request_count[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11115363634254740159ull);
    }
    for (int __Vi0 = 0; __Vi0 < 3; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__class_response_count[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2544344835019706797ull);
    }
    for (int __Vi0 = 0; __Vi0 < 3; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__class_request_stall_count[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3740605493481027146ull);
    }
    for (int __Vi0 = 0; __Vi0 < 3; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__class_response_stall_count[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8227702158108881235ull);
    }
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__held_write = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3149647884422225106ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__held_address = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8086851774902646580ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__held_wdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10259163095302417244ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__held_rstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 2682013332091163305ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__held_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 4249548560115630195ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__address_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 270362900056683004ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__weight_byte_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13095180588247911672ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__reset_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12032422123449014347ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__selected_read_lane_work = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12508823690673506073ull);
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__feature_lane_request_count[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17201262457960500299ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__weight_lane_request_count[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1000140453961270690ull);
    }
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__read_word_work = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9737744920297897457ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__read_error_work = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 1668985492665676366ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__selected_byte_address_work = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9971396450082452652ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__observed_byte_work = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 16234637342283793952ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__state = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 16786776470731751403ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6135275879147007406ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 65324089909667890ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12560510083673816141ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15249092142337962829ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11236508171375605874ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3947824672587837858ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17205421792389664979ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__input_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2095058774052788602ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14094587356700441962ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 396700756119743667ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14018278943669765782ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5893780104089561152ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9201256557384735872ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12315745835818211751ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__kernel_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11328503160825677312ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__kernel_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11000135118088023382ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__stride_y_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12768634414989834616ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__stride_x_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8201120401367300853ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__pad_left_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2872112235226025030ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__pad_right_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1306735219491918587ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__pad_top_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8194688659129743482ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__pad_bottom_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8509391464177437901ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__groups_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9773849469732160593ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__padding_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11592229148400778989ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_package_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3742102432429403640ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_package_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7151771625937204619ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__quantized_weight_offset_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8338835749376063466ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__quantized_weight_bytes_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4348184395561772967ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_batch_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16367133188022522876ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__activation_mode_latched = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 16428873933084117336ull);
    for (int __Vi0 = 0; __Vi0 < 51200; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_patch[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 12504947820626254262ull);
    }
    for (int __Vi0 = 0; __Vi0 < 512; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_block[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 2861617930159167219ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_accumulator[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13362747806565463569ull);
    }
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_data = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 17733371329478329409ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_read_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10318476865324647207ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_read_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 10089912656604338348ull);
    }
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__reduction_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17868062019224820816ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_group_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8014206244143088517ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__tile_start_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6412891012933144211ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__tile_start_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11829288707581507919ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__tile_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9012090408295055632ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__tile_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8967840321439819695ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__patch_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5944271378009534516ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__patch_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14999619016755105944ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__patch_byte_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3402887579485504985ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__tile_point_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6461306046640235065ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__group_lane_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6817826947232495239ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_scan_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3809639302858056618ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12636141095689491925ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18133417793095496791ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11015996805420007036ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_point_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12348187385051832881ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_point_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5860989928257968430ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8326284964008685619ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6629285192025718118ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14157533588807097736ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__request_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9768807124474124114ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__request_strobe_latched = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 14625800050466258638ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__request_wdata_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4118966817092529616ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 2240671551133674643ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_elements_wide, __VscopeHash, 65558201074750349ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__reduction_count_wide, __VscopeHash, 12526973237769489716ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__validation_ok = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1608324001612965362ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__validation_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 17652882771208476619ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_scan_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17712150143395416650ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17699225308568662938ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16884270992876242036ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_scan_advance = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8880344001356858911ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_scan_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10277298666542860045ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__feature_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 6856941024656555786ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__weight_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 2181596680224978047ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_input_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8156002894129634902ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_kernel_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8658885405663538506ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8920168625491170322ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_next_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17041173318715689328ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1230985454041883490ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_tap_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17006775322644388489ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_feature_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12784413902116892522ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_read_enable = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13323729659531162776ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_feature_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 12663196330600871238ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_weight_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 13147063550236192457ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_product[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 8881736293339831414ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_sum[__Vi0] = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 8317348120362203034ull);
    }
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_bad_argument = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1347301407986472960ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__compute_overflow = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3849803256451114531ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_lane = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15017156711640640315ull);
    VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_parameter, __VscopeHash, 1150609618290495538ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_bias = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12660410762347247349ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mq_prefetch_invalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15717196933200256292ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_mq_parameter[__Vi0], __VscopeHash, 9560797011372230139ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__lane_bias[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9462703897812091359ull);
    }
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requant_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6260649434106915147ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__requantized_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 9891361088191327163ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_point_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10855585401223601498ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_point_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9874679167136516774ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_byte_offset_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 10849548320083424435ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__output_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 7126339225860920754ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 4360498892643022526ull);
    vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__request_byte_lane = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 14521603431762998457ull);
    for (int __Vi0 = 0; __Vi0 < 8192; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__0__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 6328749593522577330ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8192; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__1__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 14089906276341049895ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8192; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__2__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 13043463453606456715ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8192; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__3__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 8534680533524229834ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8192; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__4__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 4801404165758847426ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8192; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__5__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 6281044569309885768ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8192; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__6__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 5969958511597104874ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8192; ++__Vi0) {
        vlSelf->tb_s2a_t66_candidate_blackbox__DOT__u_dut__DOT__gen_weight_lane_bank__BRA__7__KET____DOT__lane_weight_memory[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 1176685887417223906ull);
    }
    vlSelf->__Vfunc_tb_s2a_t66_candidate_blackbox__DOT__request_stall_cycles__1__index = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VstlTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggeredAcc[__Vi0] = 0;
    }
    vlSelf->__Vtrigprevexpr___TOP__tb_s2a_t66_candidate_blackbox__DOT__clk__0 = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VnbaTriggered[__Vi0] = 0;
    }
    vlSelf->__Vi = 0;
}
