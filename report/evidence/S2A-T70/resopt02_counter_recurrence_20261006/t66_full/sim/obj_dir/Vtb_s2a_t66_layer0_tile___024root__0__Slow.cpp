// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_t66_layer0_tile.h for the primary calling header

#include "Vtb_s2a_t66_layer0_tile__pch.h"

void Vtb_s2a_t66_layer0_tile___024root___timing_ready(Vtb_s2a_t66_layer0_tile___024root* vlSelf);

VL_ATTR_COLD void Vtb_s2a_t66_layer0_tile___024root___eval_static(Vtb_s2a_t66_layer0_tile___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___eval_static\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    {
        // Inlined CFunc: _eval_static__TOP
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__clk = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__hard_reset = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__buffer_owner_pl = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__start_valid = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__result_ready = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point0_golden_seen = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point1_golden_seen = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point0_requant_seen = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__first_tile_point1_bias_checked = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__memory_pending = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_data = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_error = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_delay_remaining = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__request_count = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_count = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__output_write_count = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__input_read_count = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_read_count = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__stall_cycle_count = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_stall_cycle_count = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__held_request = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__stall_remaining = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__cycle_count = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__next_cycle_progress = 0x000186a0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__result_count = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__next_progress = 0x00030d40U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__pending_transfer_class = 0xffffffffU;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__active_request_stall_observed = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__active_response_stall_observed = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__feature_capture_checked = 0U;
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__weight_capture_checked = 0U;
        const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__t66_read_capture_monitor__DOT__selected_lane = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10737394431514779556ull);
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__t66_read_capture_monitor__DOT__destination_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18439610872733172488ull);
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__t66_read_capture_monitor__DOT__selected_byte = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 10221492769302941218ull);
    }
    vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_t66_layer0_tile__DOT__clk__0 = 0U;
    Vtb_s2a_t66_layer0_tile___024root___timing_ready(vlSelf);
    do {
        vlSelfRef.__VactTriggeredAcc[vlSelfRef.__Vi] 
            = vlSelfRef.__VactTriggered[vlSelfRef.__Vi];
        vlSelfRef.__Vi = ((IData)(1U) + vlSelfRef.__Vi);
    } while ((0U >= vlSelfRef.__Vi));
}

VL_ATTR_COLD void Vtb_s2a_t66_layer0_tile___024root___eval_final(Vtb_s2a_t66_layer0_tile___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___eval_final\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_t66_layer0_tile___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG
VL_ATTR_COLD bool Vtb_s2a_t66_layer0_tile___024root___eval_phase__stl(Vtb_s2a_t66_layer0_tile___024root* vlSelf);

VL_ATTR_COLD void Vtb_s2a_t66_layer0_tile___024root___eval_settle(Vtb_s2a_t66_layer0_tile___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___eval_settle\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VstlIterCount;
    // Body
    __VstlIterCount = 0U;
    vlSelfRef.__VstlFirstIteration = 1U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VstlIterCount)))) {
#ifdef VL_DEBUG
            Vtb_s2a_t66_layer0_tile___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
#endif
            VL_FATAL_MT("D:\\FPGA_Competition\\report\\evidence\\S2A-T70\\resopt02_counter_recurrence_20261006\\t66_full\\source\\tb_s2a_t66_layer0_tile.sv", 3, "", "DIDNOTCONVERGE: Settle region did not converge after '--converge-limit' of 10000 tries");
        }
        __VstlIterCount = ((IData)(1U) + __VstlIterCount);
        vlSelfRef.__VstlPhaseResult = Vtb_s2a_t66_layer0_tile___024root___eval_phase__stl(vlSelf);
        vlSelfRef.__VstlFirstIteration = 0U;
    } while (vlSelfRef.__VstlPhaseResult);
}

VL_ATTR_COLD bool Vtb_s2a_t66_layer0_tile___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_t66_layer0_tile___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___dump_triggers__stl\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_s2a_t66_layer0_tile___024root___trigger_anySet__stl(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: Internal 'stl' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD bool Vtb_s2a_t66_layer0_tile___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___trigger_anySet__stl\n"); );
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

VL_ATTR_COLD void Vtb_s2a_t66_layer0_tile___024root___stl_sequent__TOP__0(Vtb_s2a_t66_layer0_tile___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___stl_sequent__TOP__0\n"); );
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
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__Vfuncout;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__Vfuncout = 0;
    CData/*0:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__is_write;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__is_write = 0;
    IData/*31:0*/ __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__word_address;
    __Vfunc_tb_s2a_t66_layer0_tile__DOT__classify_transfer__0__word_address = 0;
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
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_cancel 
        = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__hard_reset;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_byte_lane 
        = (3U & (0x00030210U >> ((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_strobe_latched) 
                                 << 1U)));
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__start_ready 
        = ((~ (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__hard_reset)) 
           & (0U == (IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state)));
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_rstrb = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_wstrb = 0U;
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
        __Vtemp_2[0U] = (IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_rounded_magnitude);
        __Vtemp_2[1U] = (IData)((tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_rounded_magnitude 
                                 >> 0x00000020U));
        __Vtemp_2[2U] = 0U;
        VL_NEGATE_W(3, __Vtemp_3, __Vtemp_2);
        tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_signed_value 
            = ((tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_accumulator 
                >> 0x1fU) ? (((QData)((IData)(__Vtemp_3[1U])) 
                              << 0x00000020U) | (QData)((IData)(__Vtemp_3[0U])))
                : tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_rounded_magnitude);
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requantized_value 
            = (VL_LTS_IQQ(64, 0x000000000000007fULL, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_signed_value)
                ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_signed_value)
                                  ? 0x00000081U : (0x000000ffU 
                                                   & (IData)(tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_signed_value))));
    }
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
    __Vtemp_5[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_batch_count_latched;
    __Vtemp_5[1U] = 0U;
    __Vtemp_5[2U] = 0U;
    __Vtemp_5[3U] = 0U;
    __Vtemp_6[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_channels_latched;
    __Vtemp_6[1U] = 0U;
    __Vtemp_6[2U] = 0U;
    __Vtemp_6[3U] = 0U;
    VL_MUL_W(4, __Vtemp_7, __Vtemp_5, __Vtemp_6);
    __Vtemp_8[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_height_latched;
    __Vtemp_8[1U] = 0U;
    __Vtemp_8[2U] = 0U;
    __Vtemp_8[3U] = 0U;
    VL_MUL_W(4, __Vtemp_9, __Vtemp_7, __Vtemp_8);
    __Vtemp_10[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_width_latched;
    __Vtemp_10[1U] = 0U;
    __Vtemp_10[2U] = 0U;
    __Vtemp_10[3U] = 0U;
    VL_MUL_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_elements_wide, __Vtemp_9, __Vtemp_10);
    __Vtemp_11[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_batch_count_latched;
    __Vtemp_11[1U] = 0U;
    __Vtemp_11[2U] = 0U;
    __Vtemp_11[3U] = 0U;
    __Vtemp_12[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched;
    __Vtemp_12[1U] = 0U;
    __Vtemp_12[2U] = 0U;
    __Vtemp_12[3U] = 0U;
    VL_MUL_W(4, __Vtemp_13, __Vtemp_11, __Vtemp_12);
    __Vtemp_14[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched;
    __Vtemp_14[1U] = 0U;
    __Vtemp_14[2U] = 0U;
    __Vtemp_14[3U] = 0U;
    VL_MUL_W(4, __Vtemp_15, __Vtemp_13, __Vtemp_14);
    __Vtemp_16[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched;
    __Vtemp_16[1U] = 0U;
    __Vtemp_16[2U] = 0U;
    __Vtemp_16[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_elements_wide, __Vtemp_15, __Vtemp_16);
    __Vtemp_17[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched;
    __Vtemp_17[1U] = 0U;
    __Vtemp_17[2U] = 0U;
    __Vtemp_17[3U] = 0U;
    __Vtemp_18[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_channels_latched;
    __Vtemp_18[1U] = 0U;
    __Vtemp_18[2U] = 0U;
    __Vtemp_18[3U] = 0U;
    VL_MUL_W(4, __Vtemp_19, __Vtemp_17, __Vtemp_18);
    __Vtemp_20[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched;
    __Vtemp_20[1U] = 0U;
    __Vtemp_20[2U] = 0U;
    __Vtemp_20[3U] = 0U;
    VL_MUL_W(4, __Vtemp_21, __Vtemp_19, __Vtemp_20);
    __Vtemp_22[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched;
    __Vtemp_22[1U] = 0U;
    __Vtemp_22[2U] = 0U;
    __Vtemp_22[3U] = 0U;
    VL_MUL_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__expected_weight_bytes_wide, __Vtemp_21, __Vtemp_22);
    __Vtemp_23[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_channels_latched;
    __Vtemp_23[1U] = 0U;
    __Vtemp_23[2U] = 0U;
    __Vtemp_23[3U] = 0U;
    __Vtemp_24[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched;
    __Vtemp_24[1U] = 0U;
    __Vtemp_24[2U] = 0U;
    __Vtemp_24[3U] = 0U;
    VL_MUL_W(4, __Vtemp_25, __Vtemp_23, __Vtemp_24);
    __Vtemp_26[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched;
    __Vtemp_26[1U] = 0U;
    __Vtemp_26[2U] = 0U;
    __Vtemp_26[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_wide, __Vtemp_25, __Vtemp_26);
    __Vtemp_27[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_base_latched;
    __Vtemp_27[1U] = 0U;
    __Vtemp_27[2U] = 0U;
    __Vtemp_27[3U] = 0U;
    __Vtemp_28[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_length_latched;
    __Vtemp_28[1U] = 0U;
    __Vtemp_28[2U] = 0U;
    __Vtemp_28[3U] = 0U;
    VL_ADD_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_end_wide, __Vtemp_27, __Vtemp_28);
    __Vtemp_29[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_base_latched;
    __Vtemp_29[1U] = 0U;
    __Vtemp_29[2U] = 0U;
    __Vtemp_29[3U] = 0U;
    __Vtemp_30[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_length_latched;
    __Vtemp_30[1U] = 0U;
    __Vtemp_30[2U] = 0U;
    __Vtemp_30[3U] = 0U;
    VL_ADD_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_end_wide, __Vtemp_29, __Vtemp_30);
    __Vtemp_31[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_base_latched;
    __Vtemp_31[1U] = 0U;
    __Vtemp_31[2U] = 0U;
    __Vtemp_31[3U] = 0U;
    __Vtemp_32[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_length_latched;
    __Vtemp_32[1U] = 0U;
    __Vtemp_32[2U] = 0U;
    __Vtemp_32[3U] = 0U;
    VL_ADD_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_end_wide, __Vtemp_31, __Vtemp_32);
    __Vtemp_33[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__quantized_weight_offset_latched;
    __Vtemp_33[1U] = 0U;
    __Vtemp_33[2U] = 0U;
    __Vtemp_33[3U] = 0U;
    __Vtemp_34[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__quantized_weight_bytes_latched;
    __Vtemp_34[1U] = 0U;
    __Vtemp_34[2U] = 0U;
    __Vtemp_34[3U] = 0U;
    VL_ADD_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__quantized_weight_end_wide, __Vtemp_33, __Vtemp_34);
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
        __Vtemp_35[0U] = (((8U > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched)
                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched
                            : 8U) - (IData)(1U));
        __Vtemp_35[1U] = 0U;
        __Vtemp_35[2U] = 0U;
        __Vtemp_35[3U] = 0U;
        __Vtemp_36[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_y_latched;
        __Vtemp_36[1U] = 0U;
        __Vtemp_36[2U] = 0U;
        __Vtemp_36[3U] = 0U;
        VL_MUL_W(4, __Vtemp_37, __Vtemp_35, __Vtemp_36);
        __Vtemp_38[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched;
        __Vtemp_38[1U] = 0U;
        __Vtemp_38[2U] = 0U;
        __Vtemp_38[3U] = 0U;
        VL_ADD_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_height_wide, __Vtemp_37, __Vtemp_38);
        __Vtemp_39[0U] = (((8U > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched)
                            ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched
                            : 8U) - (IData)(1U));
        __Vtemp_39[1U] = 0U;
        __Vtemp_39[2U] = 0U;
        __Vtemp_39[3U] = 0U;
        __Vtemp_40[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_x_latched;
        __Vtemp_40[1U] = 0U;
        __Vtemp_40[2U] = 0U;
        __Vtemp_40[3U] = 0U;
        VL_MUL_W(4, __Vtemp_41, __Vtemp_39, __Vtemp_40);
        __Vtemp_42[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched;
        __Vtemp_42[1U] = 0U;
        __Vtemp_42[2U] = 0U;
        __Vtemp_42[3U] = 0U;
        VL_ADD_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_width_wide, __Vtemp_41, __Vtemp_42);
        VL_MUL_W(4, __Vtemp_43, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_height_wide, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_width_wide);
        __Vtemp_44[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_channels_latched;
        __Vtemp_44[1U] = 0U;
        __Vtemp_44[2U] = 0U;
        __Vtemp_44[3U] = 0U;
        VL_MUL_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_bytes_wide, __Vtemp_43, __Vtemp_44);
    }
    __Vtemp_45[0U] = ((8U > vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched)
                       ? vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched
                       : 8U);
    __Vtemp_45[1U] = 0U;
    __Vtemp_45[2U] = 0U;
    __Vtemp_45[3U] = 0U;
    VL_MUL_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_weight_group_bytes_wide, __Vtemp_45, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_wide);
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__validation_ok = 0U;
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__validation_error = 1U;
    __Vtemp_47[0U] = 0x00001fffU;
    __Vtemp_47[1U] = 0U;
    __Vtemp_47[2U] = 0U;
    __Vtemp_47[3U] = 0U;
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
                  | VL_LT_W(4, __Vtemp_47, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_wide)) 
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
        if ((((((VL_LT_W(4, __Vtemp_48, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_elements_wide) 
                 | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_length_latched 
                    != tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_elements_wide[0U])) 
                | VL_LT_W(4, __Vtemp_49, vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_elements_wide)) 
               | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_length_latched 
                  != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_elements_wide[0U])) 
              | VL_LT_W(4, __Vtemp_50, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__expected_weight_bytes_wide)) 
             | (vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__quantized_weight_bytes_latched 
                != tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__expected_weight_bytes_wide[0U]))) {
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__validation_error = 3U;
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
            __Vtemp_54[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_length_latched;
            __Vtemp_54[1U] = 0U;
            __Vtemp_54[2U] = 0U;
            __Vtemp_54[3U] = 0U;
            __Vtemp_55[0U] = 0x00000c5cU;
            __Vtemp_55[1U] = 0U;
            __Vtemp_55[2U] = 0U;
            __Vtemp_55[3U] = 0U;
            __Vtemp_56[0U] = ((0x25U >= (0x0000003fU 
                                         & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched))
                               ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                              [(0x0000003fU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched)]
                               : 0U);
            __Vtemp_56[1U] = 0U;
            __Vtemp_56[2U] = 0U;
            __Vtemp_56[3U] = 0U;
            __Vtemp_57[0U] = vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched;
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
            if (((((((((VL_LT_W(4, __Vtemp_51, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_end_wide) 
                        | VL_LT_W(4, __Vtemp_52, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_end_wide)) 
                       | VL_LT_W(4, __Vtemp_53, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_end_wide)) 
                      | (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_length_latched)) 
                     | VL_GT_W(4, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__quantized_weight_end_wide, __Vtemp_54)) 
                    | (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                        [(0x0000003fU & vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched)]
                         : 0U) != vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched)) 
                   | VL_LT_W(4, __Vtemp_55, __Vtemp_58)) 
                  | VL_LT_W(4, __Vtemp_59, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_tile_patch_bytes_wide)) 
                 | VL_LT_W(4, __Vtemp_60, tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__full_weight_group_bytes_wide))) {
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
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_rsp_valid 
        = ((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__memory_pending) 
           & (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT__response_delay_remaining));
    vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_address_wide 
        = ((QData)((IData)(vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_base_latched)) 
           + vlSelfRef.tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_byte_offset_wide);
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
            __Vtemp_61 = VL_MATCHMASKED_I(32, VL_MODDIVS_III(32, vlSelfRef.__Vfunc_tb_s2a_t66_layer0_tile__DOT__request_stall_cycles__1__index, (IData)(5U)), Vtb_s2a_t66_layer0_tile__ConstPool__CONST_hb4617e49_0);
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_0__request_stall_cycles 
                = Vtb_s2a_t66_layer0_tile__ConstPool__TABLE_hc6a14c36_0
                [__Vtemp_61];
            vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_ready 
                = (0U == vlSelfRef.tb_s2a_t66_layer0_tile__DOT____VlemCall_0__request_stall_cycles);
        }
    } else {
        vlSelfRef.tb_s2a_t66_layer0_tile__DOT__backend_req_ready = 0U;
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
}

VL_ATTR_COLD bool Vtb_s2a_t66_layer0_tile___024root___eval_phase__stl(Vtb_s2a_t66_layer0_tile___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___eval_phase__stl\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
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
        Vtb_s2a_t66_layer0_tile___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
    }
#endif
    __VstlExecute = Vtb_s2a_t66_layer0_tile___024root___trigger_anySet__stl(vlSelfRef.__VstlTriggered);
    if (__VstlExecute) {
        {
            // Inlined CFunc: _eval_stl
            if ((1ULL & vlSelfRef.__VstlTriggered[0U])) {
                Vtb_s2a_t66_layer0_tile___024root___stl_sequent__TOP__0(vlSelf);
            }
        }
    }
    return (__VstlExecute);
}

bool Vtb_s2a_t66_layer0_tile___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_t66_layer0_tile___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___dump_triggers__act\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_s2a_t66_layer0_tile___024root___trigger_anySet__act(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: @(negedge tb_s2a_t66_layer0_tile.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 1U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 1 is active: @(posedge tb_s2a_t66_layer0_tile.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 2U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 2 is active: @([true] __VdlySched.awaitingCurrentTime())\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vtb_s2a_t66_layer0_tile___024root___ctor_var_reset(Vtb_s2a_t66_layer0_tile___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_t66_layer0_tile___024root___ctor_var_reset\n"); );
    Vtb_s2a_t66_layer0_tile__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2551681917237304763ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__backend_cancel = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14758118918664601268ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__backend_req_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8343794617111864670ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__backend_req_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14795205934684040878ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__backend_req_write = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8130049706645647161ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__backend_req_rstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 18213168522275402588ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__backend_req_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 12309063777790698341ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__backend_rsp_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8471669679318853442ull);
    for (int __Vi0 = 0; __Vi0 < 519168; ++__Vi0) {
        vlSelf->tb_s2a_t66_layer0_tile__DOT__input_bytes[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 10212392420955302871ull);
    }
    for (int __Vi0 = 0; __Vi0 < 864; ++__Vi0) {
        vlSelf->tb_s2a_t66_layer0_tile__DOT__weight_bytes[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 12164668864471302857ull);
    }
    for (int __Vi0 = 0; __Vi0 < 1384448; ++__Vi0) {
        vlSelf->tb_s2a_t66_layer0_tile__DOT__expected_bytes[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 1533668918785378379ull);
    }
    for (int __Vi0 = 0; __Vi0 < 1384448; ++__Vi0) {
        vlSelf->tb_s2a_t66_layer0_tile__DOT__output_seen[__Vi0] = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2185933084142235173ull);
    }
    for (int __Vi0 = 0; __Vi0 < 864; ++__Vi0) {
        vlSelf->tb_s2a_t66_layer0_tile__DOT__weight_seen[__Vi0] = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5169409070513381539ull);
    }
    for (int __Vi0 = 0; __Vi0 < 3; ++__Vi0) {
        vlSelf->tb_s2a_t66_layer0_tile__DOT__class_request_count[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11453502235737885007ull);
    }
    for (int __Vi0 = 0; __Vi0 < 3; ++__Vi0) {
        vlSelf->tb_s2a_t66_layer0_tile__DOT__class_response_count[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15451076680842844999ull);
    }
    for (int __Vi0 = 0; __Vi0 < 3; ++__Vi0) {
        vlSelf->tb_s2a_t66_layer0_tile__DOT__class_request_stall_count[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15558839315427421836ull);
    }
    for (int __Vi0 = 0; __Vi0 < 3; ++__Vi0) {
        vlSelf->tb_s2a_t66_layer0_tile__DOT__class_response_stall_count[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11006812021321676454ull);
    }
    vlSelf->tb_s2a_t66_layer0_tile__DOT__held_write = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6407755251247899646ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__held_address = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 301625125397771361ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__held_wdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6646762416676210983ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__held_rstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 6263753320442915536ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__held_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 1115808879110314108ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__address_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10621464029201242763ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__weight_byte_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7805017190826653186ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__reset_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7995247746983789926ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__selected_read_lane_work = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 630695786169615740ull);
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->tb_s2a_t66_layer0_tile__DOT__feature_lane_request_count[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4792452960176144978ull);
    }
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->tb_s2a_t66_layer0_tile__DOT__weight_lane_request_count[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6787171836200360436ull);
    }
    vlSelf->tb_s2a_t66_layer0_tile__DOT__read_word_work = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8812405497876640070ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__read_error_work = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 10236729285369363405ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__selected_byte_address_work = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 198296254424811725ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__observed_byte_work = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 16639069465582451589ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__state = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 675287496433533454ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5135116980600521490ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1383163148280234762ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2514046123800892029ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9801495962244514766ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7910930795567098546ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 274937176670370579ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3660890463920363440ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__input_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13150771066685897361ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15968622581368423086ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 452016138616330335ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13465736161479298444ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15706187851731403557ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11667022408445007540ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14716080643094467681ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10684658858537951605ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__kernel_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1704417592919178034ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_y_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2354810111183416898ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__stride_x_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14710078896233184238ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__pad_left_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12797329978069897039ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__pad_right_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12034403441663504992ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__pad_top_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16960044849570762657ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__pad_bottom_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12981907010231487996ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__groups_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11160069496703647740ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__padding_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13305567788429175868ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5622716609136278486ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_package_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10914882195751490402ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__quantized_weight_offset_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11116259596777632771ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__quantized_weight_bytes_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13235004116826001271ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_batch_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7334069674263562810ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__activation_mode_latched = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 10114749835575227672ull);
    for (int __Vi0 = 0; __Vi0 < 51200; ++__Vi0) {
        vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_patch[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 6629357849159509962ull);
    }
    for (int __Vi0 = 0; __Vi0 < 36864; ++__Vi0) {
        vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_group[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 15398111441609700577ull);
    }
    for (int __Vi0 = 0; __Vi0 < 512; ++__Vi0) {
        vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_block[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 17585176965241249108ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_accumulator[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6474574996291091336ull);
    }
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16957757348730775187ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_group_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2920743693144627162ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3592893346579249048ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_start_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9284146968282386936ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12172214716261796179ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6343618919880642532ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11226031394573335999ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2514903603636271766ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__patch_byte_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13201068263339098709ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__tile_point_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3711157226341505455ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__group_lane_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1421689689853268372ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 686809836453979089ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3304025197675030930ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2824680031767289761ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9265584222119097485ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3022155685261528669ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15934344992640909283ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9527301896168711714ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_address_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6431032904370981046ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_strobe_latched = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 8209876200992522510ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_wdata_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 756263876206969323ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 15989042585563730295ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_elements_wide, __VscopeHash, 11051263759666248094ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__reduction_count_wide, __VscopeHash, 14164853432253065089ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__validation_ok = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3899255133646258961ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__validation_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 7013717732655618494ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14473022457089823061ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10673408476863571328ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12507165524668420204ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_advance = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 18296775102923938667ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_scan_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 23782037448172284ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__feature_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 6163286527540678509ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__weight_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 10924975824086493649ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_input_channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13956165977453386531ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7227388945052228569ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_kernel_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2597630088784020486ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_feature_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 499655190155148913ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_weight_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 2009440081383177474ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_product[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 12773521600314016035ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_sum[__Vi0] = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 1499425036293481586ull);
    }
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_bad_argument = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13596315371564974055ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__compute_overflow = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16643786613880861619ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_lane = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17371856021083927749ull);
    VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_parameter, __VscopeHash, 14217790202985906834ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_bias = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4068261818487874481ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mq_prefetch_invalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4231455299413321359ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        VL_SCOPED_RAND_RESET_W(80, vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_mq_parameter[__Vi0], __VscopeHash, 6186503834775142922ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__lane_bias[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7890209875977763832ull);
    }
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requant_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9641485000527507761ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__requantized_value = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 5926230654872925582ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6611938284240935008ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_point_scan_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10023996843596642511ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_byte_offset_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 13965891225025015377ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__output_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 5291337858725858024ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__mapped_response_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 11182368533465470088ull);
    vlSelf->tb_s2a_t66_layer0_tile__DOT__u_dut__DOT__request_byte_lane = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 13527744504666834420ull);
    vlSelf->__Vfunc_tb_s2a_t66_layer0_tile__DOT__request_stall_cycles__1__index = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VstlTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggeredAcc[__Vi0] = 0;
    }
    vlSelf->__Vtrigprevexpr___TOP__tb_s2a_t66_layer0_tile__DOT__clk__0 = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VnbaTriggered[__Vi0] = 0;
    }
    vlSelf->__Vi = 0;
}
