// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_s2a_conv_tile_unit.h for the primary calling header

#include "Vtb_s2a_conv_tile_unit__pch.h"

void Vtb_s2a_conv_tile_unit___024root___timing_ready(Vtb_s2a_conv_tile_unit___024root* vlSelf);

VL_ATTR_COLD void Vtb_s2a_conv_tile_unit___024root___eval_static(Vtb_s2a_conv_tile_unit___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___eval_static\n"); );
    Vtb_s2a_conv_tile_unit__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    {
        // Inlined CFunc: _eval_static__TOP
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__clk = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__hard_reset = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__abort = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__start_valid = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__layer_id = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__query_count = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__lane_checks = 0U;
    }
    vlSelfRef.__Vtrigprevexpr___TOP__tb_s2a_conv_tile_unit__DOT__clk__0 = 0U;
    Vtb_s2a_conv_tile_unit___024root___timing_ready(vlSelf);
    do {
        vlSelfRef.__VactTriggeredAcc[vlSelfRef.__Vi] 
            = vlSelfRef.__VactTriggered[vlSelfRef.__Vi];
        vlSelfRef.__Vi = ((IData)(1U) + vlSelfRef.__Vi);
    } while ((0U >= vlSelfRef.__Vi));
}

VL_ATTR_COLD void Vtb_s2a_conv_tile_unit___024root___eval_final(Vtb_s2a_conv_tile_unit___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___eval_final\n"); );
    Vtb_s2a_conv_tile_unit__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_conv_tile_unit___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG
VL_ATTR_COLD bool Vtb_s2a_conv_tile_unit___024root___eval_phase__stl(Vtb_s2a_conv_tile_unit___024root* vlSelf);

VL_ATTR_COLD void Vtb_s2a_conv_tile_unit___024root___eval_settle(Vtb_s2a_conv_tile_unit___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___eval_settle\n"); );
    Vtb_s2a_conv_tile_unit__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VstlIterCount;
    // Body
    __VstlIterCount = 0U;
    vlSelfRef.__VstlFirstIteration = 1U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VstlIterCount)))) {
#ifdef VL_DEBUG
            Vtb_s2a_conv_tile_unit___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
#endif
            VL_FATAL_MT("source\\tb_s2a_conv_tile_unit.sv", 3, "", "DIDNOTCONVERGE: Settle region did not converge after '--converge-limit' of 10000 tries");
        }
        __VstlIterCount = ((IData)(1U) + __VstlIterCount);
        vlSelfRef.__VstlPhaseResult = Vtb_s2a_conv_tile_unit___024root___eval_phase__stl(vlSelf);
        vlSelfRef.__VstlFirstIteration = 0U;
    } while (vlSelfRef.__VstlPhaseResult);
}

VL_ATTR_COLD bool Vtb_s2a_conv_tile_unit___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_conv_tile_unit___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___dump_triggers__stl\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_s2a_conv_tile_unit___024root___trigger_anySet__stl(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: Internal 'stl' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD bool Vtb_s2a_conv_tile_unit___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___trigger_anySet__stl\n"); );
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

VL_ATTR_COLD void Vtb_s2a_conv_tile_unit___024root___stl_sequent__TOP__0(Vtb_s2a_conv_tile_unit___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___stl_sequent__TOP__0\n"); );
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
    VlWide<4>/*127:0*/ __Vtemp_145;
    VlWide<4>/*127:0*/ __Vtemp_146;
    VlWide<4>/*127:0*/ __Vtemp_147;
    VlWide<4>/*127:0*/ __Vtemp_148;
    VlWide<4>/*127:0*/ __Vtemp_149;
    VlWide<4>/*127:0*/ __Vtemp_150;
    VlWide<4>/*127:0*/ __Vtemp_151;
    VlWide<4>/*127:0*/ __Vtemp_152;
    VlWide<4>/*127:0*/ __Vtemp_153;
    VlWide<4>/*127:0*/ __Vtemp_154;
    VlWide<4>/*127:0*/ __Vtemp_155;
    VlWide<4>/*127:0*/ __Vtemp_156;
    VlWide<4>/*127:0*/ __Vtemp_157;
    VlWide<4>/*127:0*/ __Vtemp_158;
    VlWide<4>/*127:0*/ __Vtemp_159;
    VlWide<4>/*127:0*/ __Vtemp_160;
    VlWide<4>/*127:0*/ __Vtemp_161;
    VlWide<4>/*127:0*/ __Vtemp_162;
    VlWide<4>/*127:0*/ __Vtemp_163;
    VlWide<4>/*127:0*/ __Vtemp_164;
    VlWide<4>/*127:0*/ __Vtemp_165;
    VlWide<4>/*127:0*/ __Vtemp_166;
    VlWide<4>/*127:0*/ __Vtemp_167;
    VlWide<4>/*127:0*/ __Vtemp_168;
    VlWide<4>/*127:0*/ __Vtemp_169;
    VlWide<4>/*127:0*/ __Vtemp_170;
    VlWide<4>/*127:0*/ __Vtemp_171;
    VlWide<4>/*127:0*/ __Vtemp_172;
    VlWide<4>/*127:0*/ __Vtemp_173;
    VlWide<4>/*127:0*/ __Vtemp_174;
    VlWide<4>/*127:0*/ __Vtemp_175;
    VlWide<4>/*127:0*/ __Vtemp_176;
    VlWide<4>/*127:0*/ __Vtemp_177;
    VlWide<4>/*127:0*/ __Vtemp_178;
    VlWide<4>/*127:0*/ __Vtemp_179;
    VlWide<4>/*127:0*/ __Vtemp_180;
    VlWide<4>/*127:0*/ __Vtemp_181;
    VlWide<4>/*127:0*/ __Vtemp_182;
    VlWide<4>/*127:0*/ __Vtemp_183;
    VlWide<4>/*127:0*/ __Vtemp_184;
    VlWide<4>/*127:0*/ __Vtemp_185;
    VlWide<4>/*127:0*/ __Vtemp_187;
    VlWide<4>/*127:0*/ __Vtemp_188;
    VlWide<4>/*127:0*/ __Vtemp_189;
    VlWide<4>/*127:0*/ __Vtemp_190;
    VlWide<4>/*127:0*/ __Vtemp_191;
    VlWide<4>/*127:0*/ __Vtemp_192;
    VlWide<4>/*127:0*/ __Vtemp_193;
    VlWide<4>/*127:0*/ __Vtemp_194;
    VlWide<4>/*127:0*/ __Vtemp_195;
    VlWide<4>/*127:0*/ __Vtemp_196;
    VlWide<4>/*127:0*/ __Vtemp_197;
    VlWide<4>/*127:0*/ __Vtemp_198;
    VlWide<4>/*127:0*/ __Vtemp_199;
    VlWide<4>/*127:0*/ __Vtemp_200;
    // Body
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_1 = (0x12U 
                                                == (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state));
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__start_ready 
        = ((~ ((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__hard_reset) 
               | (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__abort))) 
           & (0U == (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__state)));
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
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[0U] = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[0U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[0U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[0U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[0U] = 0ULL;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[0U] = 0U;
    if ((0x00000026U > vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)) {
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U] 
            = (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                 ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                 : 0U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base);
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])) {
            if ((0U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U]))) {
                    __Vtemp_1[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_1[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_1[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_2[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_2[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_2[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_3[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_3[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_3[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_4[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_4[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_4[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_5[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_5[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_5[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_6[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_6[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_6[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_7[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_7[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_7[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_8[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_8[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_8[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_9[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_9[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_9[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_10[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_10[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_10[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
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
                if (((((((((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
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
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_7[2U] << 0x00000010U) 
                             | (__Vtemp_7[1U] >> 0x00000010U)) 
                            != ((__Vtemp_8[1U] << 0x00000018U) 
                                | (__Vtemp_8[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_9[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_10[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[0U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U]))) {
                    __Vtemp_11[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_11[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_11[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_12[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_12[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_12[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                } else {
                    __Vtemp_11[0U] = 0U;
                    __Vtemp_11[1U] = 0U;
                    __Vtemp_12[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[0U] 
                    = ((__Vtemp_11[1U] << 0x00000018U) 
                       | (__Vtemp_11[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[0U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[0U]));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[0U] 
                    = (0x000000ffU & __Vtemp_12[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U]))) {
                    __Vtemp_13[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_13[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_13[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                    __Vtemp_14[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][0U];
                    __Vtemp_14[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][1U];
                    __Vtemp_14[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[0U])][2U];
                } else {
                    __Vtemp_13[1U] = 0U;
                    __Vtemp_13[2U] = 0U;
                    __Vtemp_14[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[0U] 
                    = ((__Vtemp_13[2U] << 0x00000010U) 
                       | (__Vtemp_13[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[0U] 
                    = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[0U];
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[0U] 
                    = (0x000000ffU & (__Vtemp_14[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[0U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[0U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[0U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[0U])) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[0U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[0U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[0U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[0U] 
                                           + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[0U]), vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[0U]);
            __Vtemp_16[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[0U]);
            __Vtemp_16[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[0U] 
                                      >> 0x00000020U));
            __Vtemp_16[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_17, __Vtemp_16);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[0U] 
                = ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[0U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_17[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_17[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[0U]);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[0U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[0U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[0U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[0U]))));
        } else if ((0U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U] 
            = ((IData)(1U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])) {
            if ((1U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U]))) {
                    __Vtemp_19[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_19[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_19[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_20[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_20[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_20[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_21[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_21[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_21[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_22[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_22[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_22[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_23[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_23[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_23[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_24[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_24[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_24[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_25[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_25[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_25[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_26[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_26[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_26[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_27[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_27[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_27[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_28[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_28[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_28[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
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
                if (((((((((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
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
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_25[2U] << 0x00000010U) 
                             | (__Vtemp_25[1U] >> 0x00000010U)) 
                            != ((__Vtemp_26[1U] << 0x00000018U) 
                                | (__Vtemp_26[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_27[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_28[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[1U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U]))) {
                    __Vtemp_29[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_29[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_29[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_30[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_30[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_30[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                } else {
                    __Vtemp_29[0U] = 0U;
                    __Vtemp_29[1U] = 0U;
                    __Vtemp_30[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[1U] 
                    = ((__Vtemp_29[1U] << 0x00000018U) 
                       | (__Vtemp_29[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[1U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[1U]));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[1U] 
                    = (0x000000ffU & __Vtemp_30[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U]))) {
                    __Vtemp_31[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_31[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_31[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                    __Vtemp_32[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][0U];
                    __Vtemp_32[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][1U];
                    __Vtemp_32[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U])][2U];
                } else {
                    __Vtemp_31[1U] = 0U;
                    __Vtemp_31[2U] = 0U;
                    __Vtemp_32[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[1U] 
                    = ((__Vtemp_31[2U] << 0x00000010U) 
                       | (__Vtemp_31[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[1U] 
                    = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[1U];
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[1U] 
                    = (0x000000ffU & (__Vtemp_32[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[1U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[1U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[1U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[1U])) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[1U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[1U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[1U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[1U] 
                                           + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[1U]), vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[1U]);
            __Vtemp_34[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[1U]);
            __Vtemp_34[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[1U] 
                                      >> 0x00000020U));
            __Vtemp_34[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_35, __Vtemp_34);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[1U] 
                = ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[1U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_35[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_35[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[1U]);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[1U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[1U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[1U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[1U]))));
        } else if ((1U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U] 
            = ((IData)(2U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])) {
            if ((2U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U]))) {
                    __Vtemp_37[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_37[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_37[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_38[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_38[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_38[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_39[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_39[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_39[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_40[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_40[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_40[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_41[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_41[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_41[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_42[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_42[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_42[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_43[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_43[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_43[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_44[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_44[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_44[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_45[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_45[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_45[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_46[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_46[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_46[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
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
                if (((((((((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
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
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_43[2U] << 0x00000010U) 
                             | (__Vtemp_43[1U] >> 0x00000010U)) 
                            != ((__Vtemp_44[1U] << 0x00000018U) 
                                | (__Vtemp_44[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_45[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_46[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[2U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U]))) {
                    __Vtemp_47[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_47[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_47[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_48[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_48[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_48[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                } else {
                    __Vtemp_47[0U] = 0U;
                    __Vtemp_47[1U] = 0U;
                    __Vtemp_48[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[2U] 
                    = ((__Vtemp_47[1U] << 0x00000018U) 
                       | (__Vtemp_47[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[2U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[2U]));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[2U] 
                    = (0x000000ffU & __Vtemp_48[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U]))) {
                    __Vtemp_49[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_49[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_49[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                    __Vtemp_50[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][0U];
                    __Vtemp_50[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][1U];
                    __Vtemp_50[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U])][2U];
                } else {
                    __Vtemp_49[1U] = 0U;
                    __Vtemp_49[2U] = 0U;
                    __Vtemp_50[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[2U] 
                    = ((__Vtemp_49[2U] << 0x00000010U) 
                       | (__Vtemp_49[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[2U] 
                    = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[2U];
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[2U] 
                    = (0x000000ffU & (__Vtemp_50[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[2U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[2U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[2U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[2U])) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[2U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[2U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[2U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[2U] 
                                           + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[2U]), vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[2U]);
            __Vtemp_52[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[2U]);
            __Vtemp_52[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[2U] 
                                      >> 0x00000020U));
            __Vtemp_52[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_53, __Vtemp_52);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[2U] 
                = ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[2U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_53[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_53[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[2U]);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[2U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[2U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[2U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[2U]))));
        } else if ((2U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U] 
            = ((IData)(3U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])) {
            if ((3U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U]))) {
                    __Vtemp_55[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_55[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_55[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_56[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_56[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_56[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_57[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_57[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_57[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_58[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_58[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_58[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_59[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_59[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_59[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_60[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_60[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_60[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_61[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_61[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_61[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_62[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_62[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_62[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_63[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_63[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_63[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_64[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_64[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_64[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
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
                if (((((((((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
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
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_61[2U] << 0x00000010U) 
                             | (__Vtemp_61[1U] >> 0x00000010U)) 
                            != ((__Vtemp_62[1U] << 0x00000018U) 
                                | (__Vtemp_62[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_63[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_64[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[3U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U]))) {
                    __Vtemp_65[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_65[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_65[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_66[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_66[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_66[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                } else {
                    __Vtemp_65[0U] = 0U;
                    __Vtemp_65[1U] = 0U;
                    __Vtemp_66[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[3U] 
                    = ((__Vtemp_65[1U] << 0x00000018U) 
                       | (__Vtemp_65[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[3U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[3U]));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[3U] 
                    = (0x000000ffU & __Vtemp_66[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U]))) {
                    __Vtemp_67[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_67[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_67[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                    __Vtemp_68[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][0U];
                    __Vtemp_68[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][1U];
                    __Vtemp_68[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U])][2U];
                } else {
                    __Vtemp_67[1U] = 0U;
                    __Vtemp_67[2U] = 0U;
                    __Vtemp_68[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[3U] 
                    = ((__Vtemp_67[2U] << 0x00000010U) 
                       | (__Vtemp_67[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[3U] 
                    = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[3U];
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[3U] 
                    = (0x000000ffU & (__Vtemp_68[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[3U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[3U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[3U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[3U])) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[3U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[3U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[3U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[3U] 
                                           + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[3U]), vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[3U]);
            __Vtemp_70[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[3U]);
            __Vtemp_70[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[3U] 
                                      >> 0x00000020U));
            __Vtemp_70[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_71, __Vtemp_70);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[3U] 
                = ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[3U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_71[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_71[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[3U]);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[3U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[3U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[3U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[3U]))));
        } else if ((3U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U] 
            = ((IData)(4U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])) {
            if ((4U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U]))) {
                    __Vtemp_73[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_73[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_73[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_74[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_74[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_74[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_75[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_75[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_75[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_76[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_76[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_76[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_77[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_77[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_77[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_78[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_78[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_78[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_79[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_79[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_79[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_80[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_80[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_80[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_81[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_81[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_81[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_82[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_82[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_82[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
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
                if (((((((((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
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
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_79[2U] << 0x00000010U) 
                             | (__Vtemp_79[1U] >> 0x00000010U)) 
                            != ((__Vtemp_80[1U] << 0x00000018U) 
                                | (__Vtemp_80[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_81[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_82[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[4U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U]))) {
                    __Vtemp_83[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_83[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_83[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_84[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_84[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_84[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                } else {
                    __Vtemp_83[0U] = 0U;
                    __Vtemp_83[1U] = 0U;
                    __Vtemp_84[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[4U] 
                    = ((__Vtemp_83[1U] << 0x00000018U) 
                       | (__Vtemp_83[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[4U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[4U]));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[4U] 
                    = (0x000000ffU & __Vtemp_84[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U]))) {
                    __Vtemp_85[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_85[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_85[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                    __Vtemp_86[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][0U];
                    __Vtemp_86[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][1U];
                    __Vtemp_86[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U])][2U];
                } else {
                    __Vtemp_85[1U] = 0U;
                    __Vtemp_85[2U] = 0U;
                    __Vtemp_86[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[4U] 
                    = ((__Vtemp_85[2U] << 0x00000010U) 
                       | (__Vtemp_85[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[4U] 
                    = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[4U];
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[4U] 
                    = (0x000000ffU & (__Vtemp_86[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[4U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[4U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[4U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[4U])) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[4U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[4U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[4U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[4U] 
                                           + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[4U]), vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[4U]);
            __Vtemp_88[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[4U]);
            __Vtemp_88[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[4U] 
                                      >> 0x00000020U));
            __Vtemp_88[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_89, __Vtemp_88);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[4U] 
                = ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[4U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_89[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_89[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[4U]);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[4U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[4U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[4U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[4U]))));
        } else if ((4U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U] 
            = ((IData)(5U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])) {
            if ((5U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U]))) {
                    __Vtemp_91[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_91[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_91[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_92[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_92[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_92[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_93[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_93[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_93[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_94[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_94[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_94[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_95[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_95[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_95[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_96[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_96[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_96[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_97[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_97[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_97[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_98[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_98[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_98[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_99[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_99[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_99[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_100[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_100[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_100[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
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
                if (((((((((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
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
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_97[2U] << 0x00000010U) 
                             | (__Vtemp_97[1U] >> 0x00000010U)) 
                            != ((__Vtemp_98[1U] << 0x00000018U) 
                                | (__Vtemp_98[0U] >> 8U))) 
                           | ((0x000000ffU & (__Vtemp_99[1U] 
                                              >> 8U)) 
                              != (0x000000ffU & __Vtemp_100[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[5U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U]))) {
                    __Vtemp_101[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_101[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_101[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_102[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_102[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_102[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                } else {
                    __Vtemp_101[0U] = 0U;
                    __Vtemp_101[1U] = 0U;
                    __Vtemp_102[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[5U] 
                    = ((__Vtemp_101[1U] << 0x00000018U) 
                       | (__Vtemp_101[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[5U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[5U]));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[5U] 
                    = (0x000000ffU & __Vtemp_102[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U]))) {
                    __Vtemp_103[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_103[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_103[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                    __Vtemp_104[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][0U];
                    __Vtemp_104[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][1U];
                    __Vtemp_104[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U])][2U];
                } else {
                    __Vtemp_103[1U] = 0U;
                    __Vtemp_103[2U] = 0U;
                    __Vtemp_104[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[5U] 
                    = ((__Vtemp_103[2U] << 0x00000010U) 
                       | (__Vtemp_103[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[5U] 
                    = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[5U];
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[5U] 
                    = (0x000000ffU & (__Vtemp_104[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[5U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[5U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[5U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[5U])) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[5U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[5U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[5U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[5U] 
                                           + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[5U]), vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[5U]);
            __Vtemp_106[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[5U]);
            __Vtemp_106[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[5U] 
                                       >> 0x00000020U));
            __Vtemp_106[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_107, __Vtemp_106);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[5U] 
                = ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[5U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_107[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_107[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[5U]);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[5U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[5U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[5U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[5U]))));
        } else if ((5U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U] 
            = ((IData)(6U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])) {
            if ((6U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U]))) {
                    __Vtemp_109[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_109[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_109[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_110[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_110[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_110[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_111[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_111[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_111[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_112[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_112[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_112[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_113[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_113[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_113[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_114[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_114[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_114[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_115[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_115[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_115[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_116[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_116[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_116[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_117[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_117[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_117[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_118[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_118[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_118[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
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
                if (((((((((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
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
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_115[2U] << 0x00000010U) 
                             | (__Vtemp_115[1U] >> 0x00000010U)) 
                            != ((__Vtemp_116[1U] << 0x00000018U) 
                                | (__Vtemp_116[0U] 
                                   >> 8U))) | ((0x000000ffU 
                                                & (__Vtemp_117[1U] 
                                                   >> 8U)) 
                                               != (0x000000ffU 
                                                   & __Vtemp_118[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[6U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U]))) {
                    __Vtemp_119[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_119[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_119[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_120[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_120[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_120[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                } else {
                    __Vtemp_119[0U] = 0U;
                    __Vtemp_119[1U] = 0U;
                    __Vtemp_120[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[6U] 
                    = ((__Vtemp_119[1U] << 0x00000018U) 
                       | (__Vtemp_119[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[6U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[6U]));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[6U] 
                    = (0x000000ffU & __Vtemp_120[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U]))) {
                    __Vtemp_121[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_121[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_121[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                    __Vtemp_122[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][0U];
                    __Vtemp_122[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][1U];
                    __Vtemp_122[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U])][2U];
                } else {
                    __Vtemp_121[1U] = 0U;
                    __Vtemp_121[2U] = 0U;
                    __Vtemp_122[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[6U] 
                    = ((__Vtemp_121[2U] << 0x00000010U) 
                       | (__Vtemp_121[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[6U] 
                    = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[6U];
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[6U] 
                    = (0x000000ffU & (__Vtemp_122[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[6U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[6U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[6U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[6U])) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[6U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[6U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[6U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[6U] 
                                           + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[6U]), vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[6U]);
            __Vtemp_124[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[6U]);
            __Vtemp_124[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[6U] 
                                       >> 0x00000020U));
            __Vtemp_124[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_125, __Vtemp_124);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[6U] 
                = ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[6U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_125[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_125[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[6U]);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[6U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[6U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[6U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[6U]))));
        } else if ((6U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U] 
            = ((IData)(7U) + (((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                                : 0U) + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base));
        if ((0x00000c5cU > vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])) {
            if ((7U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U]))) {
                    __Vtemp_127[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_127[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_127[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_128[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_128[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_128[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_129[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_129[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_129[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_130[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_130[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_130[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_131[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_131[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_131[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_132[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_132[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_132[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_133[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_133[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_133[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_134[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_134[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_134[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_135[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_135[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_135[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_136[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_136[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_136[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
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
                if (((((((((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U] 
                            >= (((0x25U >= (0x0000003fU 
                                            & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                  ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                                 [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                                  : 0U) + ((0x25U >= 
                                            (0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                            ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                                           [(0x0000003fU 
                                             & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
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
                     | ((0U == (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__activation_mode_latched)) 
                        & ((((__Vtemp_133[2U] << 0x00000010U) 
                             | (__Vtemp_133[1U] >> 0x00000010U)) 
                            != ((__Vtemp_134[1U] << 0x00000018U) 
                                | (__Vtemp_134[0U] 
                                   >> 8U))) | ((0x000000ffU 
                                                & (__Vtemp_135[1U] 
                                                   >> 8U)) 
                                               != (0x000000ffU 
                                                   & __Vtemp_136[0U])))))) {
                    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
                }
            }
            if ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[7U] 
                 >> 0x1fU)) {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U]))) {
                    __Vtemp_137[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_137[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_137[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_138[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_138[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_138[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                } else {
                    __Vtemp_137[0U] = 0U;
                    __Vtemp_137[1U] = 0U;
                    __Vtemp_138[0U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[7U] 
                    = ((__Vtemp_137[1U] << 0x00000018U) 
                       | (__Vtemp_137[0U] >> 8U));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[7U] 
                    = ((IData)(1U) + (~ vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[7U]));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[7U] 
                    = (0x000000ffU & __Vtemp_138[0U]);
            } else {
                if ((0x0c5bU >= (0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U]))) {
                    __Vtemp_139[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_139[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_139[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                    __Vtemp_140[0U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][0U];
                    __Vtemp_140[1U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][1U];
                    __Vtemp_140[2U] = vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_ROM
                        [(0x00000fffU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U])][2U];
                } else {
                    __Vtemp_139[1U] = 0U;
                    __Vtemp_139[2U] = 0U;
                    __Vtemp_140[1U] = 0U;
                }
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[7U] 
                    = ((__Vtemp_139[2U] << 0x00000010U) 
                       | (__Vtemp_139[1U] >> 0x00000010U));
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[7U] 
                    = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[7U];
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[7U] 
                    = (0x000000ffU & (__Vtemp_140[1U] 
                                      >> 8U));
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[7U] 
                = ((QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[7U])) 
                   * (QData)((IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[7U])));
            if ((0U != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[7U])) {
                vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[7U] 
                    = VL_SHIFTL_QQI(64,64,32, 1ULL, 
                                    (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[7U] 
                                     - (IData)(1U)));
            }
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[7U] 
                = VL_SHIFTR_QQI(64,64,32, (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[7U] 
                                           + vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[7U]), vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[7U]);
            __Vtemp_142[0U] = (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[7U]);
            __Vtemp_142[1U] = (IData)((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[7U] 
                                       >> 0x00000020U));
            __Vtemp_142[2U] = 0U;
            VL_NEGATE_W(3, __Vtemp_143, __Vtemp_142);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[7U] 
                = ((vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[7U] 
                    >> 0x1fU) ? (((QData)((IData)(__Vtemp_143[1U])) 
                                  << 0x00000020U) | (QData)((IData)(__Vtemp_143[0U])))
                    : vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[7U]);
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[7U] 
                = (VL_LTS_IQQ(64, 0x000000000000007fULL, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[7U])
                    ? 0x0000007fU : (VL_GTS_IQQ(64, 0xffffffffffffff81ULL, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[7U])
                                      ? 0x00000081U
                                      : (0x000000ffU 
                                         & (IData)(vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[7U]))));
        } else if ((7U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
        }
    } else {
        if ((0U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[1U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[1U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[1U] = 0U;
        if ((1U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[2U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[2U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[2U] = 0U;
        if ((2U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[3U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[3U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[3U] = 0U;
        if ((3U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[4U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[4U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[4U] = 0U;
        if ((4U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[5U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[5U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[5U] = 0U;
        if ((5U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[6U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[6U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[6U] = 0U;
        if ((6U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
        }
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[7U] = 0U;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[7U] = 0ULL;
        vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[7U] = 0U;
        if ((7U < vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count)) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = 1U;
        }
    }
    __Vtemp_145[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_batch_count_latched;
    __Vtemp_145[1U] = 0U;
    __Vtemp_145[2U] = 0U;
    __Vtemp_145[3U] = 0U;
    __Vtemp_146[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_channels_latched;
    __Vtemp_146[1U] = 0U;
    __Vtemp_146[2U] = 0U;
    __Vtemp_146[3U] = 0U;
    VL_MUL_W(4, __Vtemp_147, __Vtemp_145, __Vtemp_146);
    __Vtemp_148[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_height_latched;
    __Vtemp_148[1U] = 0U;
    __Vtemp_148[2U] = 0U;
    __Vtemp_148[3U] = 0U;
    VL_MUL_W(4, __Vtemp_149, __Vtemp_147, __Vtemp_148);
    __Vtemp_150[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_width_latched;
    __Vtemp_150[1U] = 0U;
    __Vtemp_150[2U] = 0U;
    __Vtemp_150[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__input_elements_wide, __Vtemp_149, __Vtemp_150);
    __Vtemp_151[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_batch_count_latched;
    __Vtemp_151[1U] = 0U;
    __Vtemp_151[2U] = 0U;
    __Vtemp_151[3U] = 0U;
    __Vtemp_152[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched;
    __Vtemp_152[1U] = 0U;
    __Vtemp_152[2U] = 0U;
    __Vtemp_152[3U] = 0U;
    VL_MUL_W(4, __Vtemp_153, __Vtemp_151, __Vtemp_152);
    __Vtemp_154[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched;
    __Vtemp_154[1U] = 0U;
    __Vtemp_154[2U] = 0U;
    __Vtemp_154[3U] = 0U;
    VL_MUL_W(4, __Vtemp_155, __Vtemp_153, __Vtemp_154);
    __Vtemp_156[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched;
    __Vtemp_156[1U] = 0U;
    __Vtemp_156[2U] = 0U;
    __Vtemp_156[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_elements_wide, __Vtemp_155, __Vtemp_156);
    __Vtemp_157[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched;
    __Vtemp_157[1U] = 0U;
    __Vtemp_157[2U] = 0U;
    __Vtemp_157[3U] = 0U;
    __Vtemp_158[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_channels_latched;
    __Vtemp_158[1U] = 0U;
    __Vtemp_158[2U] = 0U;
    __Vtemp_158[3U] = 0U;
    VL_MUL_W(4, __Vtemp_159, __Vtemp_157, __Vtemp_158);
    __Vtemp_160[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched;
    __Vtemp_160[1U] = 0U;
    __Vtemp_160[2U] = 0U;
    __Vtemp_160[3U] = 0U;
    VL_MUL_W(4, __Vtemp_161, __Vtemp_159, __Vtemp_160);
    __Vtemp_162[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched;
    __Vtemp_162[1U] = 0U;
    __Vtemp_162[2U] = 0U;
    __Vtemp_162[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__expected_weight_bytes_wide, __Vtemp_161, __Vtemp_162);
    __Vtemp_163[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_channels_latched;
    __Vtemp_163[1U] = 0U;
    __Vtemp_163[2U] = 0U;
    __Vtemp_163[3U] = 0U;
    __Vtemp_164[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched;
    __Vtemp_164[1U] = 0U;
    __Vtemp_164[2U] = 0U;
    __Vtemp_164[3U] = 0U;
    VL_MUL_W(4, __Vtemp_165, __Vtemp_163, __Vtemp_164);
    __Vtemp_166[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched;
    __Vtemp_166[1U] = 0U;
    __Vtemp_166[2U] = 0U;
    __Vtemp_166[3U] = 0U;
    VL_MUL_W(4, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_wide, __Vtemp_165, __Vtemp_166);
    __Vtemp_167[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_base_latched;
    __Vtemp_167[1U] = 0U;
    __Vtemp_167[2U] = 0U;
    __Vtemp_167[3U] = 0U;
    __Vtemp_168[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_length_latched;
    __Vtemp_168[1U] = 0U;
    __Vtemp_168[2U] = 0U;
    __Vtemp_168[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__input_end_wide, __Vtemp_167, __Vtemp_168);
    __Vtemp_169[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_base_latched;
    __Vtemp_169[1U] = 0U;
    __Vtemp_169[2U] = 0U;
    __Vtemp_169[3U] = 0U;
    __Vtemp_170[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_length_latched;
    __Vtemp_170[1U] = 0U;
    __Vtemp_170[2U] = 0U;
    __Vtemp_170[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__output_end_wide, __Vtemp_169, __Vtemp_170);
    __Vtemp_171[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_base_latched;
    __Vtemp_171[1U] = 0U;
    __Vtemp_171[2U] = 0U;
    __Vtemp_171[3U] = 0U;
    __Vtemp_172[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_length_latched;
    __Vtemp_172[1U] = 0U;
    __Vtemp_172[2U] = 0U;
    __Vtemp_172[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_end_wide, __Vtemp_171, __Vtemp_172);
    __Vtemp_173[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_offset_latched;
    __Vtemp_173[1U] = 0U;
    __Vtemp_173[2U] = 0U;
    __Vtemp_173[3U] = 0U;
    __Vtemp_174[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_bytes_latched;
    __Vtemp_174[1U] = 0U;
    __Vtemp_174[2U] = 0U;
    __Vtemp_174[3U] = 0U;
    VL_ADD_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_end_wide, __Vtemp_173, __Vtemp_174);
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
        __Vtemp_175[0U] = (((8U > vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched)
                             ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched
                             : 8U) - (IData)(1U));
        __Vtemp_175[1U] = 0U;
        __Vtemp_175[2U] = 0U;
        __Vtemp_175[3U] = 0U;
        __Vtemp_176[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched;
        __Vtemp_176[1U] = 0U;
        __Vtemp_176[2U] = 0U;
        __Vtemp_176[3U] = 0U;
        VL_MUL_W(4, __Vtemp_177, __Vtemp_175, __Vtemp_176);
        __Vtemp_178[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched;
        __Vtemp_178[1U] = 0U;
        __Vtemp_178[2U] = 0U;
        __Vtemp_178[3U] = 0U;
        VL_ADD_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_height_wide, __Vtemp_177, __Vtemp_178);
        __Vtemp_179[0U] = (((8U > vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched)
                             ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched
                             : 8U) - (IData)(1U));
        __Vtemp_179[1U] = 0U;
        __Vtemp_179[2U] = 0U;
        __Vtemp_179[3U] = 0U;
        __Vtemp_180[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched;
        __Vtemp_180[1U] = 0U;
        __Vtemp_180[2U] = 0U;
        __Vtemp_180[3U] = 0U;
        VL_MUL_W(4, __Vtemp_181, __Vtemp_179, __Vtemp_180);
        __Vtemp_182[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched;
        __Vtemp_182[1U] = 0U;
        __Vtemp_182[2U] = 0U;
        __Vtemp_182[3U] = 0U;
        VL_ADD_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_width_wide, __Vtemp_181, __Vtemp_182);
        VL_MUL_W(4, __Vtemp_183, tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_height_wide, tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_width_wide);
        __Vtemp_184[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_channels_latched;
        __Vtemp_184[1U] = 0U;
        __Vtemp_184[2U] = 0U;
        __Vtemp_184[3U] = 0U;
        VL_MUL_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_bytes_wide, __Vtemp_183, __Vtemp_184);
    }
    __Vtemp_185[0U] = ((8U > vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched)
                        ? vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched
                        : 8U);
    __Vtemp_185[1U] = 0U;
    __Vtemp_185[2U] = 0U;
    __Vtemp_185[3U] = 0U;
    VL_MUL_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__full_weight_group_bytes_wide, __Vtemp_185, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_wide);
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__validation_ok = 0U;
    vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__validation_error = 1U;
    __Vtemp_187[0U] = 0x00001fffU;
    __Vtemp_187[1U] = 0U;
    __Vtemp_187[2U] = 0U;
    __Vtemp_187[3U] = 0U;
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
            | VL_LT_W(4, __Vtemp_187, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_wide)) 
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
        __Vtemp_188[0U] = 0xffffffffU;
        __Vtemp_188[1U] = 0U;
        __Vtemp_188[2U] = 0U;
        __Vtemp_188[3U] = 0U;
        __Vtemp_189[0U] = 0xffffffffU;
        __Vtemp_189[1U] = 0U;
        __Vtemp_189[2U] = 0U;
        __Vtemp_189[3U] = 0U;
        __Vtemp_190[0U] = 0xffffffffU;
        __Vtemp_190[1U] = 0U;
        __Vtemp_190[2U] = 0U;
        __Vtemp_190[3U] = 0U;
        if ((((((VL_LT_W(4, __Vtemp_188, tb_s2a_conv_tile_unit__DOT__dut__DOT__input_elements_wide) 
                 | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__input_length_latched 
                    != tb_s2a_conv_tile_unit__DOT__dut__DOT__input_elements_wide[0U])) 
                | VL_LT_W(4, __Vtemp_189, vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_elements_wide)) 
               | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_length_latched 
                  != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_elements_wide[0U])) 
              | VL_LT_W(4, __Vtemp_190, tb_s2a_conv_tile_unit__DOT__dut__DOT__expected_weight_bytes_wide)) 
             | (vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_bytes_latched 
                != tb_s2a_conv_tile_unit__DOT__dut__DOT__expected_weight_bytes_wide[0U]))) {
            vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__validation_error = 3U;
        } else {
            __Vtemp_191[0U] = 0U;
            __Vtemp_191[1U] = 1U;
            __Vtemp_191[2U] = 0U;
            __Vtemp_191[3U] = 0U;
            __Vtemp_192[0U] = 0U;
            __Vtemp_192[1U] = 1U;
            __Vtemp_192[2U] = 0U;
            __Vtemp_192[3U] = 0U;
            __Vtemp_193[0U] = 0U;
            __Vtemp_193[1U] = 1U;
            __Vtemp_193[2U] = 0U;
            __Vtemp_193[3U] = 0U;
            __Vtemp_194[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_length_latched;
            __Vtemp_194[1U] = 0U;
            __Vtemp_194[2U] = 0U;
            __Vtemp_194[3U] = 0U;
            __Vtemp_195[0U] = 0x00000c5cU;
            __Vtemp_195[1U] = 0U;
            __Vtemp_195[2U] = 0U;
            __Vtemp_195[3U] = 0U;
            __Vtemp_196[0U] = ((0x25U >= (0x0000003fU 
                                          & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                                ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_BASE
                               [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                                : 0U);
            __Vtemp_196[1U] = 0U;
            __Vtemp_196[2U] = 0U;
            __Vtemp_196[3U] = 0U;
            __Vtemp_197[0U] = vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched;
            __Vtemp_197[1U] = 0U;
            __Vtemp_197[2U] = 0U;
            __Vtemp_197[3U] = 0U;
            VL_ADD_W(4, __Vtemp_198, __Vtemp_196, __Vtemp_197);
            __Vtemp_199[0U] = 0x0000c800U;
            __Vtemp_199[1U] = 0U;
            __Vtemp_199[2U] = 0U;
            __Vtemp_199[3U] = 0U;
            __Vtemp_200[0U] = 0x00009000U;
            __Vtemp_200[1U] = 0U;
            __Vtemp_200[2U] = 0U;
            __Vtemp_200[3U] = 0U;
            if (((((((((VL_LT_W(4, __Vtemp_191, tb_s2a_conv_tile_unit__DOT__dut__DOT__input_end_wide) 
                        | VL_LT_W(4, __Vtemp_192, tb_s2a_conv_tile_unit__DOT__dut__DOT__output_end_wide)) 
                       | VL_LT_W(4, __Vtemp_193, tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_end_wide)) 
                      | (0U == vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_length_latched)) 
                     | VL_GT_W(4, tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_end_wide, __Vtemp_194)) 
                    | (((0x25U >= (0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched))
                         ? vlSymsp->TOP__s2a_network_descriptor_pkg.S2A_T23_MQ_CHANNEL_COUNT
                        [(0x0000003fU & vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched)]
                         : 0U) != vlSelfRef.tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched)) 
                   | VL_LT_W(4, __Vtemp_195, __Vtemp_198)) 
                  | VL_LT_W(4, __Vtemp_199, tb_s2a_conv_tile_unit__DOT__dut__DOT__full_tile_patch_bytes_wide)) 
                 | VL_LT_W(4, __Vtemp_200, tb_s2a_conv_tile_unit__DOT__dut__DOT__full_weight_group_bytes_wide))) {
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

VL_ATTR_COLD bool Vtb_s2a_conv_tile_unit___024root___eval_phase__stl(Vtb_s2a_conv_tile_unit___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___eval_phase__stl\n"); );
    Vtb_s2a_conv_tile_unit__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
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
        Vtb_s2a_conv_tile_unit___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
    }
#endif
    __VstlExecute = Vtb_s2a_conv_tile_unit___024root___trigger_anySet__stl(vlSelfRef.__VstlTriggered);
    if (__VstlExecute) {
        {
            // Inlined CFunc: _eval_stl
            if ((1ULL & vlSelfRef.__VstlTriggered[0U])) {
                Vtb_s2a_conv_tile_unit___024root___stl_sequent__TOP__0(vlSelf);
            }
        }
    }
    return (__VstlExecute);
}

bool Vtb_s2a_conv_tile_unit___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_s2a_conv_tile_unit___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___dump_triggers__act\n"); );
    // Body
    if ((1U & (~ (IData)(Vtb_s2a_conv_tile_unit___024root___trigger_anySet__act(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: @(posedge tb_s2a_conv_tile_unit.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 1U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 1 is active: @(negedge tb_s2a_conv_tile_unit.clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 2U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 2 is active: @([true] __VdlySched.awaitingCurrentTime())\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vtb_s2a_conv_tile_unit___024root___ctor_var_reset(Vtb_s2a_conv_tile_unit___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_s2a_conv_tile_unit___024root___ctor_var_reset\n"); );
    Vtb_s2a_conv_tile_unit__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->tb_s2a_conv_tile_unit__DOT__start_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7270139876765001690ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__ordinal = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9814545982188419087ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__channel = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2960219645789217641ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 806950988343912678ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11505523562874898778ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__k = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6563153018503771581ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__lanes = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15108783703786934621ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__i = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12838156404525276983ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__l = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6545638273115082392ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__ic = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17781939959513464100ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__ky = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17150531529981283536ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__kx = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1146840251478791975ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__idx = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6494530608968089169ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__group_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18375561878524741146ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__ty = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10429483091281335960ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__tx = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3847285222278942109ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__th = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16873479940203343520ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__tw = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6525390653503851378ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__ph = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17957117524217560740ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__pw = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15357550017771277778ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__point = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7259510973581481473ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__expected_acc[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5661317531812051157ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__expected_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11079773045694266699ull);
    }
    vlSelf->tb_s2a_conv_tile_unit__DOT__cycles = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9724828168978408339ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__hdr[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1334154891146402895ull);
    }
    vlSelf->tb_s2a_conv_tile_unit__DOT__word_work = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8157458089089785956ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__byte_work = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5808936584493876195ull);
    for (int __Vi0 = 0; __Vi0 < 8192; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__activations[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 7460243084011935637ull);
    }
    for (int __Vi0 = 0; __Vi0 < 36864; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__weights[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 6612284392783961771ull);
    }
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__state = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 7278335879885024734ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6053461604613959528ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_layer_index_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16799760618505647708ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__input_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15907685744953004160ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__input_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10300246200032813853ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__input_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6501474890043056595ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__input_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2530650001119451396ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__input_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14190797396672266953ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__input_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3686421729141890977ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__output_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7729250055741317303ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__output_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13793875085927988048ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__output_batch_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4556462620304130079ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__output_channels_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7093566026826903675ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__output_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15197702759564024959ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__output_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5979310948884802447ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_height_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4589323373344125264ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__kernel_width_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1439564684143924699ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_y_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3257684696031217015ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__stride_x_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15661577985375693181ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_left_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5366246101711846102ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_right_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16079490274022073670ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_top_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11460645167834393555ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__pad_bottom_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1812699002148931465ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__groups_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9437610369076298838ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__padding_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15780989328915768477ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_base_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 46857970222603708ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_package_length_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12592412998639514438ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_offset_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3885573032404766953ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__quantized_weight_bytes_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17746866183924029034ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__output_batch_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10525287247079477754ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__activation_mode_latched = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 11135536593497370856ull);
    for (int __Vi0 = 0; __Vi0 < 51200; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_patch[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 17262911002388565596ull);
    }
    for (int __Vi0 = 0; __Vi0 < 36864; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_group[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 18391589068656087711ull);
    }
    for (int __Vi0 = 0; __Vi0 < 512; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__output_block[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 11987789242297097066ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__lane_accumulator[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3311462530813245378ull);
    }
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_latched = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5426330244529916296ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__output_group_base = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8447896516234987491ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_y = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 170827882069342814ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_start_x = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11394151781712203592ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5541942185379228782ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4600088805898460311ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_height = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18310872179505225461ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_width = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1114689569878724213ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__patch_byte_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2165779218699829585ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__tile_point_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 612191877277091277ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__group_lane_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6987436882878876203ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10942252444173374813ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13436736439832788433ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15877736900435636047ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4802151133079232151ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_reduction_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9116087577717407020ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__output_lane_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1678837064834168892ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__output_point_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7039623309215961245ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__result_error_latched = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 10540445430674811322ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__output_elements_wide, __VscopeHash, 2372750106725444234ull);
    VL_SCOPED_RAND_RESET_W(128, vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__reduction_count_wide, __VscopeHash, 6310272234177441415ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__validation_ok = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1478286218810090033ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__validation_error = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 15227027682707391562ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_group_invalid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8229616578683985695ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_scan_in_bounds = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11098426567205637289ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__feature_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 11216173780976802477ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__weight_source_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 1625889409176464443ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_feature_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 15991621693877960621ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_weight_byte[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 1301323603423856928ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_product[__Vi0] = VL_SCOPED_RAND_RESET_I(16, __VscopeHash, 11156722270755613575ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_sum[__Vi0] = VL_SCOPED_RAND_RESET_Q(33, __VscopeHash, 15325325051205707498ull);
    }
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_bad_argument = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11976764886518496143ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__compute_overflow = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7656497242978962891ull);
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__mq_index_for_lane[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11677671966703440272ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_multiplier[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10000899422989007087ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_q_shift[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11975195758715732657ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_magnitude[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7958408129411582072ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_product[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 9182828890943247244ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounding_add[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 11572374392834564495ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_rounded_magnitude[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 848143242410685845ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__requant_signed_value[__Vi0] = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 626817802295643606ull);
    }
    for (int __Vi0 = 0; __Vi0 < 8; ++__Vi0) {
        vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__requantized_value[__Vi0] = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 16346690079989152228ull);
    }
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__output_byte_offset_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 5812325143939820582ull);
    vlSelf->tb_s2a_conv_tile_unit__DOT__dut__DOT__output_address_wide = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 4903497424272897776ull);
    vlSelf->__VdfgRegularize_h6e95ff9d_0_1 = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VstlTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggeredAcc[__Vi0] = 0;
    }
    vlSelf->__Vtrigprevexpr___TOP__tb_s2a_conv_tile_unit__DOT__clk__0 = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VnbaTriggered[__Vi0] = 0;
    }
    vlSelf->__Vi = 0;
}
